#!/usr/bin/env python3
"""Detect completed-prefix/terminal-suffix defects at every msggame call.

This detector is intentionally independent from the release surface auditor.
It walks every decoded ``call`` component, renders the called record, and
checks only variants whose entire visible output is a known Korean terminal
ending.  A finding is emitted when the fixed literal immediately before the
call already ends in a completed Korean sentence ending.

Tracked/default output is source-free.  ``--include-text`` is available only
for a report written below the repository's ``tmp`` directory.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
AUDIT_PATH = WORKSTREAM / "audit_runtime_surface_v1.py"
SCHEMA = "nobu16.kr.pc-dialogue-terminal-boundary-detector.v1"


def load_surface_audit() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_runtime_surface_audit_for_terminal_boundary_v1",
        AUDIT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {AUDIT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


AUDIT = load_surface_audit()

# These component kinds do not emit visible text.  They may occur between a
# fixed literal and the call whose rendered suffix is appended to it.
NON_EMITTING_COMPONENTS = frozenset(
    {
        "arithmetic_operator",
        "comparison_operator",
        "logical_operator",
        "decimal_atom",
        "percent_decimal_atom",
        "control_tag",
        "block_token",
        "random_select",
        "padding_zero",
    }
)

# The called variant must be *entirely* one of these ending families.  This is
# deliberately narrower than "contains a sentence ending" so that ordinary
# called dialogue and quoted clauses are not classified as suffixes.
TERMINAL_SUFFIX_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "ha",
        re.compile(
            r"^(?:합니다|하다|한다|했다|했습니다|하겠다|하겠소|"
            r"하겠습니다|하겠사옵니다|하겠나이다|하옵니다|하오|"
            r"하라|하십시오|하옵소서|합니까|하옵니까)$"
        ),
    ),
    (
        "exist",
        re.compile(
            r"^(?:있습니다|있다|있소|있겠습니다|있겠사옵니다|"
            r"있겠나이다|있습니까)$"
        ),
    ),
    (
        "absent",
        re.compile(
            r"^(?:없습니다|없다|없소|없겠습니다|없겠사옵니다|"
            r"없겠나이다|없습니까)$"
        ),
    ),
    (
        "copula",
        re.compile(
            r"^(?:입니다|이다|이오|이옵니다|이겠소|이겠습니다|"
            r"이겠사옵니다|이겠나이다|이겠지요|이리라|이겠지|입니까)$"
        ),
    ),
    (
        "become",
        re.compile(
            r"^(?:됩니다|된다|되옵니다|되겠습니다|되겠사옵니다|"
            r"되겠나이다|됩니까)$"
        ),
    ),
    (
        "bare_terminal",
        re.compile(
            r"^(?:다|습니다|사옵니다|옵니다|겠습니다|겠사옵니다|"
            r"겠나이다|습니까|사옵니까|옵니까|겠습니까)$"
        ),
    ),
)

# Prefix classifiers are ordered from specific/high-confidence endings to the
# limited plain-declarative forms needed by the runtime resource.
COMPLETED_PREFIX_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "formal_declarative",
        re.compile(
            r"(?:합니다|했습니다|사옵니다|하옵니다|옵니다|습니다|"
            r"입니다|겠습니다|했사옵니다|했나이다)$"
        ),
    ),
    (
        "formal_interrogative",
        re.compile(
            r"(?:합니까|하옵니까|습니까|입니까|겠습니까|인가요|인가)$"
        ),
    ),
    (
        "polite_or_archaic",
        re.compile(
            r"(?:하오|있소|없소|겠소|이오|해요|하여요|세요|십시오|"
            r"지요|죠|네요|군요|하소서|하옵소서)$"
        ),
    ),
    (
        "imperative",
        re.compile(
            r"[가-힣]*(?:하라|해라|가라|오라|보라|주라|말라|"
            r"으라|어라|아라)$"
        ),
    ),
    (
        "plain_declarative",
        re.compile(
            r"(?:있다|없다|한다|했다|된다|됐다|겠다|이다|간다|"
            r"온다|본다|준다|난다|전한다|알린다|말한다)$"
        ),
    ),
)

BOUNDARY_PUNCTUATION = frozenset(
    " \t\r\n\u3000"
    ".,!?;:"
    "。．、，！？；："
    "\"'“”‘’「」『』《》〈〉【】〔〕（）()[]{}"
    "…⋯·・"
)


class TerminalBoundaryError(ValueError):
    """Raised when the detector input or output policy is invalid."""


@dataclass(frozen=True)
class TerminalBoundaryIssue:
    resource: str
    category: str
    block_id: int
    record_id: int
    literal_id: int
    component_index: int
    call_target: str
    prefix_family: str
    suffix_family: str
    prefix_sha256: str
    suffix_sha256: str
    combined_sha256: str
    prefix: str | None = None
    suffix: str | None = None
    combined: str | None = None


@dataclass(frozen=True)
class TerminalBoundaryResource:
    resource: str
    path: str
    sha256: str
    record_count: int
    decoded_record_count: int
    call_site_count: int
    terminal_suffix_variant_count: int
    issues: tuple[TerminalBoundaryIssue, ...]


def normalize_visible_boundary(value: str) -> str:
    """Remove VM controls and outer punctuation used around an ending."""

    visible = "".join(
        character
        for character in value
        if not unicodedata.category(character).startswith("C")
    )
    start = 0
    end = len(visible)
    while start < end and visible[start] in BOUNDARY_PUNCTUATION:
        start += 1
    while end > start and visible[end - 1] in BOUNDARY_PUNCTUATION:
        end -= 1
    return visible[start:end]


def classify_terminal_suffix(value: str) -> str | None:
    normalized = normalize_visible_boundary(value)
    for family, pattern in TERMINAL_SUFFIX_PATTERNS:
        if pattern.fullmatch(normalized):
            return family
    return None


def classify_completed_prefix(value: str) -> str | None:
    normalized = normalize_visible_boundary(value)
    for family, pattern in COMPLETED_PREFIX_PATTERNS:
        if pattern.search(normalized):
            return family
    return None


def unique_ordered(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def detect_resource(
    resource: str,
    path: Path,
    *,
    include_text: bool = False,
) -> TerminalBoundaryResource:
    records, blob_sha256 = AUDIT.records_from_path(path)
    renderer = AUDIT.TerminalRenderer(records)
    findings: list[TerminalBoundaryIssue] = []
    decoded_record_count = 0
    call_site_count = 0
    terminal_suffix_variant_count = 0

    for coordinate, record in records.items():
        literals = tuple(
            literal.text for literal in AUDIT.parse_record_literals(record)
        )
        components = AUDIT.tolerant_decode_record(record)
        decoded_record_count += 1
        previous_literal: tuple[int, str] | None = None

        for component_index, component in enumerate(components):
            kind = str(component["kind"])
            if kind == "literal_boundary":
                literal_id = int(component["slot"])
                previous_literal = (literal_id, literals[literal_id])
                continue

            if kind == "call":
                call_site_count += 1
                target_tuple = tuple(component["target"])
                target = (int(target_tuple[0]), int(target_tuple[1]))
                suffixes = unique_ordered(renderer.render(target))
                classified_suffixes = tuple(
                    (suffix, classify_terminal_suffix(suffix))
                    for suffix in suffixes
                )
                terminal_suffix_variant_count += sum(
                    suffix_family is not None
                    for _, suffix_family in classified_suffixes
                )

                if previous_literal is not None:
                    literal_id, prefix = previous_literal
                    prefix_family = classify_completed_prefix(prefix)
                    if prefix_family is not None:
                        for suffix, suffix_family in classified_suffixes:
                            if suffix_family is None:
                                continue
                            combined = prefix + suffix
                            findings.append(
                                TerminalBoundaryIssue(
                                    resource=resource,
                                    category=(
                                        "completed_prefix_terminal_suffix"
                                    ),
                                    block_id=coordinate[0],
                                    record_id=coordinate[1],
                                    literal_id=literal_id,
                                    component_index=component_index,
                                    call_target=f"{target[0]}:{target[1]}",
                                    prefix_family=prefix_family,
                                    suffix_family=suffix_family,
                                    prefix_sha256=AUDIT.utf16le_sha256(prefix),
                                    suffix_sha256=AUDIT.utf16le_sha256(suffix),
                                    combined_sha256=(
                                        AUDIT.utf16le_sha256(combined)
                                    ),
                                    prefix=prefix if include_text else None,
                                    suffix=suffix if include_text else None,
                                    combined=combined if include_text else None,
                                )
                            )
                # A call emits dynamic visible text, so a later call cannot be
                # assumed to touch the earlier fixed literal.
                previous_literal = None
                continue

            if kind in NON_EMITTING_COMPONENTS:
                continue

            # Selectors, output controls, jumps, and all other output-bearing
            # or flow-changing components break the fixed literal boundary.
            previous_literal = None

    deduplicated = {
        (
            issue.resource,
            issue.block_id,
            issue.record_id,
            issue.literal_id,
            issue.component_index,
            issue.call_target,
            issue.prefix_family,
            issue.suffix_family,
            issue.prefix_sha256,
            issue.suffix_sha256,
        ): issue
        for issue in findings
    }
    ordered = tuple(
        sorted(
            deduplicated.values(),
            key=lambda issue: (
                issue.block_id,
                issue.record_id,
                issue.literal_id,
                issue.component_index,
                issue.call_target,
                issue.suffix_sha256,
            ),
        )
    )
    return TerminalBoundaryResource(
        resource=resource,
        path=str(path.resolve()),
        sha256=blob_sha256,
        record_count=len(records),
        decoded_record_count=decoded_record_count,
        call_site_count=call_site_count,
        terminal_suffix_variant_count=terminal_suffix_variant_count,
        issues=ordered,
    )


def source_free_issue(issue: TerminalBoundaryIssue) -> dict[str, Any]:
    payload = asdict(issue)
    payload.pop("prefix", None)
    payload.pop("suffix", None)
    payload.pop("combined", None)
    return payload


def build_report(
    resources: Sequence[TerminalBoundaryResource],
    *,
    include_text: bool = False,
) -> dict[str, Any]:
    issues = [
        issue
        for resource in resources
        for issue in resource.issues
    ]
    prefix_counts = Counter(issue.prefix_family for issue in issues)
    suffix_counts = Counter(issue.suffix_family for issue in issues)
    return {
        "schema": SCHEMA,
        "status": "PASS" if not issues else "FAIL",
        "issue_count": len(issues),
        "prefix_family_counts": dict(sorted(prefix_counts.items())),
        "suffix_family_counts": dict(sorted(suffix_counts.items())),
        "resources": {
            resource.resource: {
                "path": resource.path,
                "sha256": resource.sha256,
                "record_count": resource.record_count,
                "decoded_record_count": resource.decoded_record_count,
                "call_site_count": resource.call_site_count,
                "terminal_suffix_variant_count": (
                    resource.terminal_suffix_variant_count
                ),
                "issue_count": len(resource.issues),
            }
            for resource in resources
        },
        "issues": [
            (
                asdict(issue)
                if include_text
                else source_free_issue(issue)
            )
            for issue in issues
        ],
        "detector_contract": {
            "all_decoded_call_sites_scanned": True,
            "immediate_fixed_literal_boundary_only": True,
            "called_variant_must_be_terminal_suffix_only": True,
            "tracked_output_is_source_free": not include_text,
            "ghidra_opcode_0143_call_contract_reused": True,
        },
    }


def canonical_json(value: Any) -> str:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def is_below(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def validate_private_output(
    *,
    include_text: bool,
    output: Path | None,
) -> None:
    if not include_text:
        return
    if output is None:
        raise TerminalBoundaryError(
            "--include-text requires --output below the repository tmp directory"
        )
    if not is_below(output, REPO / "tmp"):
        raise TerminalBoundaryError(
            "--include-text output must be below the repository tmp directory"
        )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=AUDIT.DEFAULT_BASE)
    parser.add_argument("--pk", type=Path, default=AUDIT.DEFAULT_PK)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--include-text",
        action="store_true",
        help="include bodies only in a report written below repository tmp",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="return exit code 1 when any terminal boundary defect is found",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    validate_private_output(
        include_text=args.include_text,
        output=args.output,
    )
    resources = (
        detect_resource(
            "base_msggame",
            args.base,
            include_text=args.include_text,
        ),
        detect_resource(
            "pk_msggame",
            args.pk,
            include_text=args.include_text,
        ),
    )
    payload = build_report(resources, include_text=args.include_text)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(canonical_json(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "schema": payload["schema"],
                "status": payload["status"],
                "issue_count": payload["issue_count"],
                "prefix_family_counts": payload["prefix_family_counts"],
                "suffix_family_counts": payload["suffix_family_counts"],
                "resources": {
                    name: {
                        "sha256": value["sha256"],
                        "record_count": value["record_count"],
                        "decoded_record_count": (
                            value["decoded_record_count"]
                        ),
                        "call_site_count": value["call_site_count"],
                        "terminal_suffix_variant_count": (
                            value["terminal_suffix_variant_count"]
                        ),
                        "issue_count": value["issue_count"],
                    }
                    for name, value in payload["resources"].items()
                },
                "output": (
                    str(args.output.resolve())
                    if args.output is not None
                    else None
                ),
            },
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    if args.strict and payload["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
