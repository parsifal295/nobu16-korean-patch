#!/usr/bin/env python3
"""Build the exact-nonnewline PK residual-A relative reflow candidate layer.

This builder changes newline positions only.  For every override, removing
``\n`` from the before and after strings produces the exact same string.
Protected tokens, outer whitespace, non-newline whitespace runs, literal
count, record gaps, decoded VM components, and the complete packed candidate
are cryptographically bound.

The only layout limit is the corresponding current-Korean per-line envelope.
No absolute ``msggame`` widget width is assumed, and the PK ``msgev`` 912px
rule is forbidden.  The dialogue-bearing override stays below ``tmp/`` and
this program has no Steam write path.
"""

from __future__ import annotations

import argparse
import copy
import dataclasses
import hashlib
import importlib.util
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
RESIDUAL_AUDIT_PATH = (
    WORKSTREAM / "build_pk_msggame_residual_runtime_vm_audit_v1.py"
)
EXACT_COVERAGE_PATH = (
    WORKSTREAM
    / "public"
    / (
        "pk_msggame_full_candidate_runtime_vm_coverage."
        "pre_reflow_checkpoint.v1.json"
    )
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "layout_overrides"
    / "pk_msggame_residual_a_relative_reflow.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_msggame_residual_a_relative_reflow.v1.json"
)

REPORT_SCHEMA = "nobu16.kr.pk-msggame-residual-a-relative-reflow.v1"
ROW_SCHEMA = (
    "nobu16.kr.pk-msggame-residual-a-relative-reflow-override-row.v1"
)
EXPECTED_PK_ROWS = 29_038
EXPECTED_RESIDUAL_ROWS = 10_913
EXPECTED_A_SAFE_ROWS = 6_737
EXPECTED_A_SAFE_RECORDS = 3_850
EXPECTED_EXACT_SAFE_ROOT_ROWS = 39
EXPECTED_EXACT_SAFE_ROOT_RECORDS = 26
EXPECTED_OVERRIDE_ROWS = 26
EXPECTED_OVERRIDE_RECORDS = 26
EXPECTED_EXACT_SAFE_ROOT_COORDINATE_SHA256 = (
    "7A648E51CFF4B8F1E9B8B730126257F35251DC160CD747F879865F06E5D72816"
)
EXPECTED_EXACT_SAFE_ROOT_RECORD_SHA256 = (
    "5E0C068765F1ABF7A05A50E2B665575FBA418AD099E22075F7E1F2073DB3CA0C"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "E0FC03945EA080A33BD7ACC71F8114279DB385D085F6A63A31974E77B9E0B0EE"
)
EXPECTED_PRE_REFLOW_COVERAGE_FILE_SHA256 = (
    "99FF832F2EB74DB205DE37B0079FA275471BF31A224F81E3FF422003A9B2D910"
)
EXPECTED_PRE_REFLOW_COVERAGE_PAYLOAD_SHA256 = (
    "899B84A721D7881D1A75EEE7BB2E8491B864DB2EC001640AC4B2760ADF74FE54"
)
EXPECTED_PRE_REFLOW_ELIGIBLE_ROWS = 7_453
EXPECTED_PRE_REFLOW_BLOCKED_ROWS = 2_317
EXPECTED_PRE_REFLOW_ELIGIBLE_COORDINATE_SHA256 = (
    "0D9D424C2EEBBD652EFF807BEF604164C9691011839C724658F5808BD4A64147"
)
EXPECTED_PRE_REFLOW_BLOCKED_COORDINATE_SHA256 = (
    "AD52864FFA21C9B1158E5C1EABCB2D6D9D8B16796BF6F84695D53B721337ADA4"
)
STALE_EXACT_PROBE_ROOT_ROWS = 31
STALE_EXACT_PROBE_ROOT_RECORDS = 19
STALE_EXACT_PROBE_COORDINATE_SHA256 = (
    "45724D81A65259DDCA3A80D0CABC8269EEBE7FFB4D17EB6EEFD0172913F2872B"
)
STALE_EXACT_PROBE_RECORD_SHA256 = (
    "0E3C6F1D983050309C317DA49D4CDE1CBC8985A65442EFEC38AB6E647B25242D"
)
LEGACY_NORMALIZED_SPACE_ROOT_ROWS = 23
LEGACY_NORMALIZED_SPACE_ROOT_RECORDS = 14
LEGACY_NORMALIZED_SPACE_COORDINATE_SHA256 = (
    "44C1926F55F2D9EC9E388F1FEC4C4DAE0A0B8204DAA8B485E6CD50AD96B3F872"
)
LEGACY_NORMALIZED_SPACE_RECORD_SHA256 = (
    "45108C8174983FA45B6D6A9A8E298AECC063AD7E0151D1FBB10BBC98830985DD"
)

# Filled after the deterministic candidate was first derived.  These values
# are intentionally independent so a translation, record, or archive drift
# cannot be hidden behind a single aggregate.
EXPECTED_REFLOWED_CANDIDATE_SHA256 = (
    "C18AED979C9F81B99E898FD18C7CD4F2415737223F6FF7D329A69983ECF5BB1F"
)
EXPECTED_REFLOW_REPLACEMENT_MANIFEST_SHA256 = (
    "1C809ACF49B5DEF55F54FC781513C8C190BC91A766C3EBF4D86138B3C5296368"
)
EXPECTED_CHANGED_RECORD_MANIFEST_SHA256 = (
    "1959D420D40D1192D7B1E1EEC37AAA446DB47B245B5A6D345836C728DDE1190F"
)

BREAK_PUNCTUATION = frozenset(
    ",.;:!?%…)]}〉》」』】、。，．！？：；"
)


class RelativeReflowError(ValueError):
    """Raised when the isolated reflow proof or artifact drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RelativeReflowError(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


AUDIT = load_module("pk_residual_a_relative_reflow_audit", RESIDUAL_AUDIT_PATH)
FULL_AUDIT = AUDIT.FULL_AUDIT
BASE_AUDIT = AUDIT.BASE_AUDIT
ENGINE = AUDIT.ENGINE


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    )


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n"


def canonical_jsonl(rows: Sequence[Mapping[str, Any]]) -> str:
    return "".join(
        json.dumps(
            row,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
        for row in rows
    )


def parse_coordinate(value: str) -> tuple[int, int, int]:
    return BASE_AUDIT.parse_literal_coordinate(value)


def coordinate_digest(coordinates: Sequence[str]) -> str:
    payload = "".join(
        f"{coordinate}\n"
        for coordinate in sorted(set(coordinates), key=parse_coordinate)
    )
    return sha256_bytes(payload.encode("ascii"))


def record_digest(records: Sequence[tuple[int, int]]) -> str:
    payload = "".join(
        f"{block_id}:{record_id}\n"
        for block_id, record_id in sorted(set(records))
    )
    return sha256_bytes(payload.encode("ascii"))


def read_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"required JSON is absent: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    require(path.is_file(), f"required JSONL is absent: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line:
            continue
        value = json.loads(line)
        require(
            isinstance(value, dict),
            f"{path}:{line_number} is not an object",
        )
        rows.append(value)
    return rows


def character_width(character: str) -> int:
    if unicodedata.category(character) == "Cc":
        return 0
    return (
        48
        if unicodedata.east_asian_width(character) in {"W", "F", "A"}
        else 24
    )


def line_widths(value: str) -> tuple[int, ...]:
    return tuple(
        sum(character_width(character) for character in line)
        for line in value.split("\n")
    )


def nonnewline_text(value: str) -> str:
    return value.replace("\n", "")


def nonnewline_whitespace_signature(value: str) -> list[dict[str, Any]]:
    flattened = nonnewline_text(value)
    return [
        {
            "start": match.start(),
            "end": match.end(),
            "sha256": ENGINE.sha256_text(match.group(0)),
        }
        for match in re.finditer(r"\s+", flattened)
    ]


def protected_span_ranges(value: str) -> tuple[tuple[int, int], ...]:
    spans: list[tuple[int, int]] = []
    for pattern in (
        ENGINE.ESC_TAG_RE,
        ENGINE.PRINTF_RE,
        ENGINE.BRACKET_TOKEN_RE,
    ):
        spans.extend(
            (match.start(), match.end())
            for match in pattern.finditer(value)
        )
    return tuple(sorted(spans))


def exact_nonnewline_reflow(
    candidate: str,
    current_line_widths: Sequence[int],
) -> str | None:
    """Return the first canonical exact-nonnewline reflow, if one exists."""
    capacities = tuple(int(value) for value in current_line_widths)
    flattened = nonnewline_text(candidate)
    if (
        not flattened
        or candidate.count("\n") + 1 != len(capacities)
        or len(capacities) <= 1
        or candidate.startswith("\n")
        or candidate.endswith("\n")
    ):
        return None

    original_breaks: list[int] = []
    flat_cursor = 0
    for character in candidate:
        if character == "\n":
            original_breaks.append(flat_cursor)
        else:
            flat_cursor += 1
    if len(original_breaks) != len(capacities) - 1:
        return None

    spans = protected_span_ranges(flattened)

    def inside_protected(position: int) -> bool:
        return any(start < position < end for start, end in spans)

    allowed_breaks = {
        position
        for position in range(1, len(flattened))
        if not inside_protected(position)
        and (
            flattened[position - 1].isspace()
            or flattened[position].isspace()
            or flattened[position - 1] in BREAK_PUNCTUATION
            or flattened[position] in BREAK_PUNCTUATION
        )
    }
    allowed_breaks.update(
        position
        for position in original_breaks
        if 0 < position < len(flattened)
        and not inside_protected(position)
    )

    prefix_widths = [0]
    for character in flattened:
        prefix_widths.append(
            prefix_widths[-1] + character_width(character)
        )
    ordered_allowed = tuple(sorted(allowed_breaks))

    @lru_cache(maxsize=None)
    def solve(
        line_index: int,
        start: int,
    ) -> tuple[int, ...] | None:
        if line_index == len(capacities) - 1:
            width = prefix_widths[-1] - prefix_widths[start]
            if width > capacities[line_index]:
                return None
            return ()
        for end in ordered_allowed:
            if end <= start:
                continue
            width = prefix_widths[end] - prefix_widths[start]
            if width > capacities[line_index]:
                break
            tail = solve(line_index + 1, end)
            if tail is None:
                continue
            return (end,) + tail
        return None

    solved = solve(0, 0)
    if solved is None:
        return None
    selected = frozenset(solved)
    output: list[str] = []
    for index, character in enumerate(flattened):
        if index in selected:
            output.append("\n")
        output.append(character)
    reflowed = "".join(output)

    require(
        nonnewline_text(reflowed) == flattened,
        "exact nonnewline stream changed during reflow",
    )
    require(
        reflowed.count("\n") == candidate.count("\n"),
        "literal newline count changed during reflow",
    )
    require(
        ENGINE.protected_signature(reflowed)
        == ENGINE.protected_signature(candidate),
        "protected token or outer-whitespace signature changed",
    )
    require(
        nonnewline_whitespace_signature(reflowed)
        == nonnewline_whitespace_signature(candidate),
        "nonnewline whitespace runs changed",
    )
    require(
        all(
            after <= current
            for after, current in zip(
                line_widths(reflowed),
                capacities,
            )
        ),
        "reflow still exceeds the current-Korean relative line envelope",
    )
    return reflowed


def load_effective_rows(
    *,
    full_metadata: Mapping[str, Any],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, Any],
]:
    paths = sorted(
        FULL_AUDIT.DECISIONS_DIR.glob("pk_msggame*.private.v1.jsonl")
    )
    require(
        len(paths) == FULL_AUDIT.EXPECTED_SOURCE_SEGMENTS,
        "PK source decision segment count drifted",
    )
    original_rows: list[dict[str, Any]] = []
    segment_guards: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in paths:
        values = FULL_AUDIT.load_jsonl(path)
        for row in values:
            coordinate = str(row.get("coordinate"))
            require(
                row.get("resource") == "pk_msggame"
                and coordinate not in seen,
                f"invalid or duplicate PK decision: {coordinate}",
            )
            seen.add(coordinate)
            original_rows.append(row)
        segment_guards.append(
            {
                "name": path.name,
                "row_count": len(values),
                "sha256": sha256_bytes(path.read_bytes()),
            }
        )
    require(
        len(original_rows) == len(seen) == EXPECTED_PK_ROWS,
        "PK decision row universe drifted",
    )
    original_rows.sort(
        key=lambda row: parse_coordinate(str(row["coordinate"]))
    )
    source_segment_universe = canonical_sha256(segment_guards)
    require(
        source_segment_universe
        == full_metadata["source_decision_segment_universe_sha256"],
        "source segment universe changed after full-candidate validation",
    )

    effective_rows = [copy.deepcopy(row) for row in original_rows]
    (
        semantic_private,
        semantic_public,
        semantic_report,
        semantic_row,
    ) = FULL_AUDIT.SEMANTIC_OVERRIDE.build_outputs()
    FULL_AUDIT.SEMANTIC_OVERRIDE.validate_outputs(
        semantic_private,
        semantic_public,
        semantic_report,
        semantic_row,
    )
    semantic_coordinate = str(semantic_row["coordinate"])
    matches = [
        index
        for index, row in enumerate(effective_rows)
        if str(row["coordinate"]) == semantic_coordinate
    ]
    require(len(matches) == 1, "semantic override coordinate drifted")
    effective_rows[matches[0]] = semantic_row

    replacement_manifest = [
        {
            "coordinate": str(row["coordinate"]),
            "translation_utf16le_sha256":
            ENGINE.sha256_text(str(row["translation"])),
        }
        for row in effective_rows
        if isinstance(row.get("translation"), str)
    ]
    require(
        canonical_sha256(replacement_manifest)
        == full_metadata["replacement_manifest_sha256"],
        "effective full-candidate replacement manifest drifted",
    )
    return original_rows, effective_rows, {
        "source_decision_segment_universe_sha256":
        source_segment_universe,
        "effective_replacement_manifest_sha256":
        canonical_sha256(replacement_manifest),
    }


def closure_state(
    root: tuple[int, int],
    *,
    profiles: Mapping[tuple[int, int], Mapping[str, Any]],
    edges: Mapping[tuple[int, int], Sequence[tuple[int, int]]],
    tiers: Mapping[tuple[int, int], str],
    a_safe_records: set[tuple[int, int]],
    exact_statuses: Mapping[tuple[int, int], Sequence[str]],
) -> dict[str, Any]:
    queue = [root]
    seen: set[tuple[int, int]] = set()
    width_records: set[tuple[int, int]] = set()
    unsafe_records: set[tuple[int, int]] = set()
    blocked_exact_records: set[tuple[int, int]] = set()
    other_reasons: set[str] = set()
    while queue:
        record = queue.pop()
        if record in seen:
            continue
        seen.add(record)
        profile = profiles.get(record)
        if profile is None:
            other_reasons.add("record_profile_missing")
            continue
        for reason in profile["reason_codes"]:
            if reason == "relative_line_width_expansion":
                width_records.add(record)
            else:
                other_reasons.add(str(reason))
        if record in tiers and record not in a_safe_records:
            unsafe_records.add(record)
        if "blocked" in exact_statuses.get(record, ()):
            blocked_exact_records.add(record)
        queue.extend(edges.get(record, ()))
    return {
        "visited_records": seen,
        "width_records": width_records,
        "unsafe_records": unsafe_records,
        "blocked_exact_records": blocked_exact_records,
        "other_reasons": other_reasons,
    }


def record_reflow_plan(
    record: tuple[int, int],
    *,
    inputs: Any,
) -> dict[int, str] | None:
    current_literals = ENGINE.parse_record_literals(
        inputs.pk_current_records[record]
    )
    candidate_literals = ENGINE.parse_record_literals(
        inputs.pk_candidate_records[record]
    )
    if len(current_literals) != len(candidate_literals):
        return None
    plan: dict[int, str] = {}
    for literal_id, (current, candidate) in enumerate(
        zip(current_literals, candidate_literals)
    ):
        capacities = line_widths(current.text)
        before_widths = line_widths(candidate.text)
        if len(capacities) != len(before_widths):
            return None
        if not any(
            before > current_width
            for before, current_width in zip(before_widths, capacities)
        ):
            continue
        reflowed = exact_nonnewline_reflow(candidate.text, capacities)
        if reflowed is None:
            return None
        plan[literal_id] = reflowed
    return plan


def validate_pre_reflow_exact_report(
    report: Mapping[str, Any],
    *,
    inputs: Any,
    full_metadata: Mapping[str, Any],
) -> None:
    require(
        sha256_bytes(EXACT_COVERAGE_PATH.read_bytes())
        == EXPECTED_PRE_REFLOW_COVERAGE_FILE_SHA256,
        "immutable pre-reflow exact coverage file drifted",
    )
    unsealed = copy.deepcopy(dict(report))
    guards = unsealed.get("guards")
    require(isinstance(guards, dict), "pre-reflow coverage guards are absent")
    payload_sha256 = guards.pop("report_payload_sha256", None)
    adjudications = report.get("row_adjudications")
    require(
        isinstance(adjudications, dict),
        "pre-reflow exact adjudications are absent",
    )
    eligible = [
        coordinate
        for coordinate, row in adjudications.items()
        if row.get("status") == "promotion_eligible"
    ]
    blocked = [
        coordinate
        for coordinate, row in adjudications.items()
        if row.get("status") == "blocked"
    ]
    require(
        report.get("schema")
        == "nobu16.kr.pk-msggame-full-candidate-runtime-vm-coverage.v1"
        and report.get("status") == "PASS"
        and payload_sha256 == EXPECTED_PRE_REFLOW_COVERAGE_PAYLOAD_SHA256
        and payload_sha256 == canonical_sha256(unsealed)
        and report.get("candidate_scope", {}).get(
            "literal_candidate_packed_sha256"
        )
        == inputs.artifact_hashes["pk_full_candidate_packed_sha256"]
        and report.get("candidate_scope", {}).get("source_decision_rows")
        == EXPECTED_PK_ROWS
        and report.get("candidate_scope", {}).get("string_replacement_rows")
        == FULL_AUDIT.EXPECTED_STRING_REPLACEMENTS
        and report.get("candidate_scope", {}).get(
            "source_decision_segment_count"
        )
        == FULL_AUDIT.EXPECTED_SOURCE_SEGMENTS
        and report.get("guards", {}).get("replacement_manifest_sha256")
        == full_metadata["replacement_manifest_sha256"]
        and report.get("guards", {}).get(
            "source_decision_segment_universe_sha256"
        )
        == full_metadata["source_decision_segment_universe_sha256"]
        and report.get("promotion", {}).get("runtime_promotion_performed")
        is False
        and report.get("promotion", {}).get("steam_write_performed") is False,
        "pre-reflow exact coverage binding drifted",
    )
    require(
        len(eligible) == EXPECTED_PRE_REFLOW_ELIGIBLE_ROWS
        and len(blocked) == EXPECTED_PRE_REFLOW_BLOCKED_ROWS
        and len(eligible) + len(blocked) == FULL_AUDIT.EXPECTED_EXACT_ROWS
        and FULL_AUDIT.coordinate_digest(eligible)
        == EXPECTED_PRE_REFLOW_ELIGIBLE_COORDINATE_SHA256
        and FULL_AUDIT.coordinate_digest(blocked)
        == EXPECTED_PRE_REFLOW_BLOCKED_COORDINATE_SHA256,
        "pre-reflow exact coverage universe drifted",
    )


def build_scope(
    *,
    inputs: Any,
    original_rows: Sequence[Mapping[str, Any]],
    full_metadata: Mapping[str, Any],
) -> dict[str, Any]:
    exact_report = read_json(EXACT_COVERAGE_PATH)
    validate_pre_reflow_exact_report(
        exact_report,
        inputs=inputs,
        full_metadata=full_metadata,
    )
    exact_coordinates = set(exact_report["row_adjudications"])
    residual_rows = [
        row
        for row in original_rows
        if row.get("runtime_review") == "pending"
        and str(row["coordinate"]) not in exact_coordinates
    ]
    tiers, residual_by_record = AUDIT.classify_records(residual_rows)
    require(
        len(residual_rows) == EXPECTED_RESIDUAL_ROWS,
        "residual row universe drifted",
    )
    exact_statuses: defaultdict[
        tuple[int, int], list[str]
    ] = defaultdict(list)
    for coordinate, adjudication in exact_report[
        "row_adjudications"
    ].items():
        exact_statuses[parse_coordinate(coordinate)[:2]].append(
            str(adjudication["status"])
        )
    a_safe_records = {
        record
        for record, tier in tiers.items()
        if tier == "A" and "blocked" not in exact_statuses[record]
    }
    a_safe_coordinates = [
        str(row["coordinate"])
        for record in sorted(a_safe_records)
        for row in residual_by_record[record]
    ]
    require(
        len(a_safe_records) == EXPECTED_A_SAFE_RECORDS
        and len(a_safe_coordinates) == EXPECTED_A_SAFE_ROWS,
        "final-exact-safe Tier-A universe drifted",
    )

    profiles, edges = AUDIT.build_record_profiles(inputs=inputs)
    states = {
        record: closure_state(
            record,
            profiles=profiles,
            edges=edges,
            tiers=tiers,
            a_safe_records=a_safe_records,
            exact_statuses=exact_statuses,
        )
        for record in sorted(a_safe_records)
    }
    width_only_roots = {
        record
        for record, state in states.items()
        if state["width_records"]
        and not state["unsafe_records"]
        and not state["blocked_exact_records"]
        and not state["other_reasons"]
    }
    referenced_width_records = {
        record
        for root in width_only_roots
        for record in states[root]["width_records"]
    }
    plans: dict[tuple[int, int], dict[int, str]] = {}
    for record in sorted(referenced_width_records):
        plan = record_reflow_plan(record, inputs=inputs)
        if plan is not None:
            plans[record] = plan

    exact_safe_roots = {
        root
        for root in width_only_roots
        if states[root]["width_records"].issubset(plans)
    }
    root_coordinates = [
        str(row["coordinate"])
        for record in sorted(exact_safe_roots)
        for row in residual_by_record[record]
    ]
    require(
        len(exact_safe_roots) == EXPECTED_EXACT_SAFE_ROOT_RECORDS
        and len(root_coordinates) == EXPECTED_EXACT_SAFE_ROOT_ROWS
        and coordinate_digest(root_coordinates)
        == EXPECTED_EXACT_SAFE_ROOT_COORDINATE_SHA256
        and record_digest(list(exact_safe_roots))
        == EXPECTED_EXACT_SAFE_ROOT_RECORD_SHA256,
        (
            "exact-nonnewline safe root universe drifted: "
            f"records={len(exact_safe_roots)} "
            f"rows={len(root_coordinates)} "
            f"width_only_roots={len(width_only_roots)} "
            f"planned_width_records={len(plans)} "
            f"coordinate_sha256={coordinate_digest(root_coordinates)} "
            f"record_sha256={record_digest(list(exact_safe_roots))}"
        ),
    )
    touched_records = {
        record
        for root in exact_safe_roots
        for record in states[root]["width_records"]
    }
    override_coordinates = [
        f"{record[0]}:{record[1]}:{literal_id}"
        for record in sorted(touched_records)
        for literal_id in sorted(plans[record])
    ]
    require(
        len(touched_records) == EXPECTED_OVERRIDE_RECORDS
        and len(override_coordinates) == EXPECTED_OVERRIDE_ROWS
        and coordinate_digest(override_coordinates)
        == EXPECTED_OVERRIDE_COORDINATE_SHA256,
        (
            "exact-nonnewline override universe drifted: "
            f"records={len(touched_records)} "
            f"rows={len(override_coordinates)} "
            f"coordinate_sha256={coordinate_digest(override_coordinates)}"
        ),
    )
    return {
        "exact_report": exact_report,
        "tiers": tiers,
        "residual_by_record": residual_by_record,
        "a_safe_records": a_safe_records,
        "profiles_before": profiles,
        "edges_before": edges,
        "states_before": states,
        "width_only_roots": width_only_roots,
        "exact_safe_roots": exact_safe_roots,
        "root_coordinates": root_coordinates,
        "touched_records": touched_records,
        "override_coordinates": override_coordinates,
        "plans": plans,
    }


def gap_sha256(record: Any) -> str:
    return canonical_sha256(
        [
            sha256_bytes(gap)
            for gap in ENGINE.record_gap_bytes(record)
        ]
    )


def component_sha256(record: Any) -> str:
    return canonical_sha256(
        [
            FULL_AUDIT.pk_component_signature(component)
            for component in BASE_AUDIT.decode_record(record)
        ]
    )


def build_candidate(
    *,
    inputs: Any,
    effective_rows: Sequence[Mapping[str, Any]],
    scope: Mapping[str, Any],
) -> dict[str, Any]:
    effective_by_coordinate = {
        str(row["coordinate"]): row for row in effective_rows
    }
    replacements = {
        parse_coordinate(str(row["coordinate"])): str(row["translation"])
        for row in effective_rows
        if isinstance(row.get("translation"), str)
    }
    current_blob = BASE_AUDIT.DEFAULT_PK_CURRENT.read_bytes()
    before_blob = BASE_AUDIT.rebuild_packed_with_literals(
        current_blob,
        replacements,
    )
    before_sha256 = sha256_bytes(before_blob)
    require(
        before_sha256
        == inputs.artifact_hashes["pk_full_candidate_packed_sha256"],
        "reconstructed full candidate drifted",
    )
    before_records = BASE_AUDIT.records_from_blob(before_blob)

    override_manifest: list[dict[str, Any]] = []
    for coordinate in sorted(
        scope["override_coordinates"],
        key=parse_coordinate,
    ):
        block_id, record_id, literal_id = parse_coordinate(coordinate)
        reflowed = scope["plans"][(block_id, record_id)][literal_id]
        before = effective_by_coordinate[coordinate]
        require(
            str(before["translation"])
            == ENGINE.parse_record_literals(
                before_records[(block_id, record_id)]
            )[literal_id].text,
            f"effective decision/candidate drifted: {coordinate}",
        )
        replacements[(block_id, record_id, literal_id)] = reflowed
        override_manifest.append(
            {
                "coordinate": coordinate,
                "before_translation_utf16le_sha256":
                ENGINE.sha256_text(str(before["translation"])),
                "after_translation_utf16le_sha256":
                ENGINE.sha256_text(reflowed),
                "nonnewline_utf16le_sha256":
                ENGINE.sha256_text(nonnewline_text(reflowed)),
            }
        )
    override_manifest_sha256 = canonical_sha256(override_manifest)
    after_blob = BASE_AUDIT.rebuild_packed_with_literals(
        current_blob,
        replacements,
    )
    after_sha256 = sha256_bytes(after_blob)
    after_records = BASE_AUDIT.records_from_blob(after_blob)
    require(
        set(before_records) == set(after_records),
        "record coordinate universe changed",
    )

    changed_records: set[tuple[int, int]] = set()
    record_manifest: list[dict[str, Any]] = []
    for record in sorted(before_records):
        before_record = before_records[record]
        after_record = after_records[record]
        if before_record.data == after_record.data:
            continue
        changed_records.add(record)
        require(
            record in scope["touched_records"],
            f"non-target record changed: {record}",
        )
        before_literals = ENGINE.parse_record_literals(before_record)
        after_literals = ENGINE.parse_record_literals(after_record)
        require(
            len(before_literals) == len(after_literals),
            f"literal count changed: {record}",
        )
        require(
            ENGINE.record_gap_bytes(before_record)
            == ENGINE.record_gap_bytes(after_record),
            f"record gap bytes changed: {record}",
        )
        require(
            [
                FULL_AUDIT.pk_component_signature(component)
                for component in BASE_AUDIT.decode_record(before_record)
            ]
            == [
                FULL_AUDIT.pk_component_signature(component)
                for component in BASE_AUDIT.decode_record(after_record)
            ],
            f"decoded VM structure changed: {record}",
        )
        planned_literals = scope["plans"][record]
        for literal_id, (before_literal, after_literal) in enumerate(
            zip(before_literals, after_literals)
        ):
            if literal_id in planned_literals:
                require(
                    after_literal.text == planned_literals[literal_id],
                    f"planned literal was not applied: {record}:{literal_id}",
                )
                require(
                    nonnewline_text(before_literal.text)
                    == nonnewline_text(after_literal.text),
                    f"nonnewline stream changed: {record}:{literal_id}",
                )
            else:
                require(
                    before_literal.text == after_literal.text,
                    f"untargeted literal changed: {record}:{literal_id}",
                )
        record_manifest.append(
            {
                "record": list(record),
                "before_record_sha256": sha256_bytes(before_record.data),
                "after_record_sha256": sha256_bytes(after_record.data),
                "gap_sha256": gap_sha256(after_record),
                "component_sha256": component_sha256(after_record),
            }
        )
    require(
        changed_records == scope["touched_records"],
        "changed record universe is incomplete",
    )
    record_manifest_sha256 = canonical_sha256(record_manifest)
    require(
        (
            after_sha256 == EXPECTED_REFLOWED_CANDIDATE_SHA256
            and override_manifest_sha256
            == EXPECTED_REFLOW_REPLACEMENT_MANIFEST_SHA256
            and record_manifest_sha256
            == EXPECTED_CHANGED_RECORD_MANIFEST_SHA256
        ),
        (
            "reflow candidate guards drifted: "
            f"packed={after_sha256} "
            f"override={override_manifest_sha256} "
            f"records={record_manifest_sha256}"
        ),
    )

    artifact_hashes = dict(inputs.artifact_hashes)
    artifact_hashes["pk_candidate_packed_sha256"] = after_sha256
    artifact_hashes["pk_reflow_candidate_packed_sha256"] = after_sha256
    after_inputs = dataclasses.replace(
        inputs,
        pk_candidate_records=after_records,
        artifact_hashes=artifact_hashes,
    )
    return {
        "before_blob_sha256": before_sha256,
        "after_blob_sha256": after_sha256,
        "before_records": before_records,
        "after_records": after_records,
        "after_inputs": after_inputs,
        "override_manifest": override_manifest,
        "override_manifest_sha256": override_manifest_sha256,
        "record_manifest": record_manifest,
        "record_manifest_sha256": record_manifest_sha256,
        "effective_by_coordinate": effective_by_coordinate,
    }


def verify_after_closures(
    *,
    scope: Mapping[str, Any],
    candidate: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    after_inputs = candidate["after_inputs"]
    profiles_after, edges_after = AUDIT.build_record_profiles(
        inputs=after_inputs
    )
    require(
        edges_after == scope["edges_before"],
        "call/jump edge universe changed after reflow",
    )
    exact_statuses: defaultdict[
        tuple[int, int], list[str]
    ] = defaultdict(list)
    for coordinate, adjudication in scope["exact_report"][
        "row_adjudications"
    ].items():
        exact_statuses[parse_coordinate(coordinate)[:2]].append(
            str(adjudication["status"])
        )

    proofs: dict[str, dict[str, Any]] = {}
    for root in sorted(scope["exact_safe_roots"]):
        state = closure_state(
            root,
            profiles=profiles_after,
            edges=edges_after,
            tiers=scope["tiers"],
            a_safe_records=scope["a_safe_records"],
            exact_statuses=exact_statuses,
        )
        require(
            not state["width_records"]
            and not state["unsafe_records"]
            and not state["blocked_exact_records"]
            and not state["other_reasons"],
            f"reflowed root is still blocked: {root}",
        )
        control_guard = FULL_AUDIT.pk_source_candidate_closure_guard(
            root,
            inputs=after_inputs,
        )
        require(
            not control_guard["taints"],
            f"reflowed root has a VM control taint: {root}",
        )
        proof_payload = {
            "root": list(root),
            "visited_records": [
                {
                    "record": list(record),
                    "profile_sha256": canonical_sha256(
                        profiles_after[record]
                    ),
                }
                for record in sorted(state["visited_records"])
            ],
            "source_candidate_closure_proof_sha256":
            control_guard["proof_sha256"],
            "status": "exact_nonnewline_reflow_safe",
        }
        proofs[f"{root[0]}:{root[1]}"] = {
            "status": "exact_nonnewline_reflow_safe",
            "visited_record_count": len(state["visited_records"]),
            "proof_sha256": canonical_sha256(proof_payload),
            "source_candidate_closure_proof_sha256":
            control_guard["proof_sha256"],
        }
    return proofs


def expected_override_rows(
    *,
    inputs: Any,
    full_metadata: Mapping[str, Any],
    source_metadata: Mapping[str, Any],
    scope: Mapping[str, Any],
    candidate: Mapping[str, Any],
    root_proofs: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    roots_by_changed_record: defaultdict[
        tuple[int, int], list[tuple[int, int]]
    ] = defaultdict(list)
    for root in sorted(scope["exact_safe_roots"]):
        for record in scope["states_before"][root]["width_records"]:
            roots_by_changed_record[record].append(root)

    rows: list[dict[str, Any]] = []
    for coordinate in sorted(
        scope["override_coordinates"],
        key=parse_coordinate,
    ):
        block_id, record_id, literal_id = parse_coordinate(coordinate)
        record = (block_id, record_id)
        source_row = candidate["effective_by_coordinate"][coordinate]
        before_record = candidate["before_records"][record]
        after_record = candidate["after_records"][record]
        current_record = inputs.pk_current_records[record]
        before_text = ENGINE.parse_record_literals(before_record)[
            literal_id
        ].text
        after_text = ENGINE.parse_record_literals(after_record)[
            literal_id
        ].text
        current_text = ENGINE.parse_record_literals(current_record)[
            literal_id
        ].text
        current_widths = line_widths(current_text)
        before_widths = line_widths(before_text)
        after_widths = line_widths(after_text)
        roots = roots_by_changed_record[record]
        root_keys = [f"{root[0]}:{root[1]}" for root in roots]
        require(
            nonnewline_text(before_text) == nonnewline_text(after_text)
            and before_text.count("\n") == after_text.count("\n")
            and ENGINE.protected_signature(before_text)
            == ENGINE.protected_signature(after_text)
            and nonnewline_whitespace_signature(before_text)
            == nonnewline_whitespace_signature(after_text)
            and all(
                after <= current
                for after, current in zip(
                    after_widths,
                    current_widths,
                )
            ),
            f"override invariant failed: {coordinate}",
        )
        rows.append(
            {
                "schema": ROW_SCHEMA,
                "resource": "pk_msggame",
                "coordinate": coordinate,
                "record": [block_id, record_id],
                "literal_id": literal_id,
                "translation": after_text,
                "source_decision_binding": {
                    "decision_canonical_sha256":
                    canonical_sha256(source_row),
                    "before_translation_utf16le_sha256":
                    ENGINE.sha256_text(before_text),
                    "source_decision_segment_universe_sha256":
                    source_metadata[
                        "source_decision_segment_universe_sha256"
                    ],
                },
                "exact_nonnewline_contract": {
                    "nonnewline_utf16le_sha256":
                    ENGINE.sha256_text(nonnewline_text(before_text)),
                    "newline_count": before_text.count("\n"),
                    "protected_signature_sha256": canonical_sha256(
                        ENGINE.protected_signature(before_text)
                    ),
                    "nonnewline_whitespace_signature_sha256":
                    canonical_sha256(
                        nonnewline_whitespace_signature(before_text)
                    ),
                    "before_line_widths": list(before_widths),
                    "after_line_widths": list(after_widths),
                    "current_ko_line_envelope": list(current_widths),
                    "all_after_lines_nonexpanding": True,
                    "absolute_msggame_widget_width_assumed": False,
                    "pk_msgev_912px_rule_applied": False,
                },
                "record_binding": {
                    "current_record_sha256":
                    sha256_bytes(current_record.data),
                    "before_candidate_record_sha256":
                    sha256_bytes(before_record.data),
                    "after_candidate_record_sha256":
                    sha256_bytes(after_record.data),
                    "gap_sha256": gap_sha256(after_record),
                    "component_sha256": component_sha256(after_record),
                },
                "candidate_binding": {
                    "before_full_candidate_packed_sha256":
                    candidate["before_blob_sha256"],
                    "after_reflow_candidate_packed_sha256":
                    candidate["after_blob_sha256"],
                    "before_replacement_manifest_sha256":
                    full_metadata["replacement_manifest_sha256"],
                    "reflow_override_manifest_sha256":
                    candidate["override_manifest_sha256"],
                    "changed_record_manifest_sha256":
                    candidate["record_manifest_sha256"],
                },
                "root_binding": {
                    "root_records": [list(root) for root in roots],
                    "root_record_universe_sha256": record_digest(roots),
                    "root_proof_universe_sha256": canonical_sha256(
                        {
                            key: root_proofs[key]
                            for key in root_keys
                        }
                    ),
                },
                "runtime_review_transition_performed": False,
                "layout_review_transition_performed": False,
                "steam_write_performed": False,
            }
        )
    return rows


def validate_override_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    expected: Sequence[Mapping[str, Any]],
    candidate: Mapping[str, Any],
) -> None:
    require(
        list(rows) == list(expected),
        "private exact-nonnewline reflow override drifted",
    )
    coordinates: list[str] = []
    for row in rows:
        require(row.get("schema") == ROW_SCHEMA, "override schema drifted")
        coordinate = str(row.get("coordinate"))
        block_id, record_id, literal_id = parse_coordinate(coordinate)
        after_text = str(row.get("translation"))
        before_text = ENGINE.parse_record_literals(
            candidate["before_records"][(block_id, record_id)]
        )[literal_id].text
        require(
            nonnewline_text(after_text) == nonnewline_text(before_text)
            and after_text.count("\n") == before_text.count("\n")
            and ENGINE.protected_signature(after_text)
            == ENGINE.protected_signature(before_text)
            and nonnewline_whitespace_signature(after_text)
            == nonnewline_whitespace_signature(before_text),
            f"private override invariant drifted: {coordinate}",
        )
        coordinates.append(coordinate)
    require(
        len(coordinates) == EXPECTED_OVERRIDE_ROWS
        and coordinate_digest(coordinates)
        == EXPECTED_OVERRIDE_COORDINATE_SHA256,
        "private override coordinate universe drifted",
    )


def public_report(
    *,
    private_content: str,
    rows: Sequence[Mapping[str, Any]],
    inputs: Any,
    full_metadata: Mapping[str, Any],
    source_metadata: Mapping[str, Any],
    scope: Mapping[str, Any],
    candidate: Mapping[str, Any],
    root_proofs: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    row_adjudications = {
        str(row["coordinate"]): {
            "status": "exact_nonnewline_reflow_safe",
            "record": row["record"],
            "before_translation_utf16le_sha256":
            row["source_decision_binding"][
                "before_translation_utf16le_sha256"
            ],
            "after_translation_utf16le_sha256":
            ENGINE.sha256_text(str(row["translation"])),
            "nonnewline_utf16le_sha256":
            row["exact_nonnewline_contract"][
                "nonnewline_utf16le_sha256"
            ],
            "before_candidate_record_sha256":
            row["record_binding"]["before_candidate_record_sha256"],
            "after_candidate_record_sha256":
            row["record_binding"]["after_candidate_record_sha256"],
            "root_record_universe_sha256":
            row["root_binding"]["root_record_universe_sha256"],
        }
        for row in rows
    }
    report = {
        "schema": REPORT_SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "scope": {
            "pk_rows": EXPECTED_PK_ROWS,
            "residual_rows": EXPECTED_RESIDUAL_ROWS,
            "tier_a_final_exact_safe_rows": EXPECTED_A_SAFE_ROWS,
            "tier_a_final_exact_safe_records": EXPECTED_A_SAFE_RECORDS,
            "width_only_roots_considered":
            len(scope["width_only_roots"]),
            "exact_nonnewline_safe_root_rows":
            EXPECTED_EXACT_SAFE_ROOT_ROWS,
            "exact_nonnewline_safe_root_records":
            EXPECTED_EXACT_SAFE_ROOT_RECORDS,
            "private_override_rows": len(rows),
            "private_override_records": len(
                {tuple(row["record"]) for row in rows}
            ),
        },
        "prior_probe_mismatch": {
            "legacy_normalized_space_root_rows":
            LEGACY_NORMALIZED_SPACE_ROOT_ROWS,
            "legacy_normalized_space_root_records":
            LEGACY_NORMALIZED_SPACE_ROOT_RECORDS,
            "legacy_normalized_space_coordinate_sha256":
            LEGACY_NORMALIZED_SPACE_COORDINATE_SHA256,
            "legacy_normalized_space_record_sha256":
            LEGACY_NORMALIZED_SPACE_RECORD_SHA256,
            "legacy_invariant":
            "newline normalized to one ordinary space before comparison",
            "authoritative_invariant":
            "newline removed before byte-exact comparison",
            "legacy_count_is_not_used_for_this_layer": True,
            "stale_exact_probe_root_rows":
            STALE_EXACT_PROBE_ROOT_ROWS,
            "stale_exact_probe_root_records":
            STALE_EXACT_PROBE_ROOT_RECORDS,
            "stale_exact_probe_coordinate_sha256":
            STALE_EXACT_PROBE_COORDINATE_SHA256,
            "stale_exact_probe_record_sha256":
            STALE_EXACT_PROBE_RECORD_SHA256,
            "stale_exact_probe_is_not_used_for_this_layer": True,
            "authoritative_direct_builder_recomputation_root_rows":
            EXPECTED_EXACT_SAFE_ROOT_ROWS,
            "authoritative_direct_builder_recomputation_root_records":
            EXPECTED_EXACT_SAFE_ROOT_RECORDS,
        },
        "reflow_contract": {
            "nonnewline_utf16le_byte_exact": True,
            "character_order_preserved": True,
            "protected_tokens_preserved": True,
            "outer_whitespace_preserved": True,
            "nonnewline_whitespace_runs_preserved": True,
            "literal_newline_count_preserved": True,
            "literal_boundary_count_preserved": True,
            "record_gap_bytes_preserved": True,
            "decoded_vm_components_preserved": True,
            "breaks_never_inserted_inside_protected_tokens": True,
            "new_breaks_restricted_to_whitespace_or_punctuation_boundaries":
            True,
            "cross_literal_reflow_used": False,
        },
        "layout_contract": {
            "comparison":
            "reflowed line <= corresponding current KO line envelope",
            "relative_full_width_units": 48,
            "relative_half_width_units": 24,
            "absolute_msggame_widget_width_assumed": False,
            "pk_msgev_912px_rule_applied": False,
        },
        "candidate_binding": {
            "before_full_candidate_packed_sha256":
            candidate["before_blob_sha256"],
            "after_reflow_candidate_packed_sha256":
            candidate["after_blob_sha256"],
            "source_decision_segment_universe_sha256":
            source_metadata[
                "source_decision_segment_universe_sha256"
            ],
            "before_replacement_manifest_sha256":
            full_metadata["replacement_manifest_sha256"],
            "reflow_override_manifest_sha256":
            candidate["override_manifest_sha256"],
            "changed_record_manifest_sha256":
            candidate["record_manifest_sha256"],
            "pk_pristine_packed_sha256":
            inputs.artifact_hashes["pk_pristine_packed_sha256"],
            "pk_current_packed_sha256":
            inputs.artifact_hashes["pk_current_packed_sha256"],
            "exact_coverage_file_sha256":
            sha256_bytes(EXACT_COVERAGE_PATH.read_bytes()),
            "exact_coverage_payload_sha256":
            scope["exact_report"]["guards"]["report_payload_sha256"],
        },
        "result": {
            "private_override_file_sha256":
            sha256_bytes(private_content.encode("utf-8")),
            "translation_body_stays_private": True,
            "runtime_review_transition_performed": False,
            "layout_review_transition_performed": False,
            "steam_write_performed": False,
        },
        "guards": {
            "exact_safe_root_coordinate_sha256":
            EXPECTED_EXACT_SAFE_ROOT_COORDINATE_SHA256,
            "exact_safe_root_record_sha256":
            EXPECTED_EXACT_SAFE_ROOT_RECORD_SHA256,
            "override_coordinate_sha256":
            EXPECTED_OVERRIDE_COORDINATE_SHA256,
            "root_proof_universe_sha256":
            canonical_sha256(root_proofs),
            "row_adjudication_universe_sha256":
            canonical_sha256(row_adjudications),
        },
        "root_proofs": dict(root_proofs),
        "row_adjudications": row_adjudications,
        "distribution_policy": {
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "private_override_contains_commercial_source_text": False,
            "private_override_contains_translated_dialogue_text": True,
            "private_override_stays_below_tmp": True,
        },
        "steam_write_performed": False,
    }
    unsealed = copy.deepcopy(report)
    report["guards"]["report_payload_sha256"] = canonical_sha256(unsealed)
    return report


def validate_report(
    report: Mapping[str, Any],
    *,
    expected: Mapping[str, Any],
) -> None:
    require(
        dict(report) == dict(expected),
        "source-free exact-nonnewline reflow report drifted",
    )
    require(
        report.get("schema") == REPORT_SCHEMA
        and report.get("status") == "PASS"
        and report.get("steam_write_performed") is False,
        "source-free report metadata drifted",
    )
    unsealed = copy.deepcopy(dict(report))
    guards = unsealed.get("guards")
    require(isinstance(guards, dict), "report guards are absent")
    payload_sha256 = guards.pop("report_payload_sha256", None)
    require(
        payload_sha256 == canonical_sha256(unsealed),
        "source-free report payload hash drifted",
    )
    serialized = canonical_json(report)
    require(
        not re.search(r"[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7a3]", serialized),
        "tracked report contains dialogue-script characters",
    )


def build_outputs() -> tuple[
    str,
    str,
    dict[str, Any],
    dict[str, Any],
]:
    inputs, full_metadata = FULL_AUDIT.full_candidate_inputs(
        apply_reflow=False
    )
    original_rows, effective_rows, source_metadata = load_effective_rows(
        full_metadata=full_metadata
    )
    scope = build_scope(
        inputs=inputs,
        original_rows=original_rows,
        full_metadata=full_metadata,
    )
    candidate = build_candidate(
        inputs=inputs,
        effective_rows=effective_rows,
        scope=scope,
    )
    root_proofs = verify_after_closures(
        scope=scope,
        candidate=candidate,
    )
    rows = expected_override_rows(
        inputs=inputs,
        full_metadata=full_metadata,
        source_metadata=source_metadata,
        scope=scope,
        candidate=candidate,
        root_proofs=root_proofs,
    )
    validate_override_rows(
        rows,
        expected=rows,
        candidate=candidate,
    )
    private_content = canonical_jsonl(rows)
    report = public_report(
        private_content=private_content,
        rows=rows,
        inputs=inputs,
        full_metadata=full_metadata,
        source_metadata=source_metadata,
        scope=scope,
        candidate=candidate,
        root_proofs=root_proofs,
    )
    validate_report(report, expected=report)
    public_content = canonical_json(report)
    return private_content, public_content, report, {
        "inputs": inputs,
        "full_metadata": full_metadata,
        "source_metadata": source_metadata,
        "scope": scope,
        "candidate": candidate,
        "root_proofs": root_proofs,
        "rows": rows,
        "report": report,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--private-output",
        type=Path,
        default=DEFAULT_PRIVATE_OUTPUT,
    )
    parser.add_argument(
        "--public-output",
        type=Path,
        default=DEFAULT_PUBLIC_OUTPUT,
    )
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    require(args.write or args.check, "choose --write, --check, or both")

    first = build_outputs()
    second = build_outputs()
    require(
        first[0] == second[0] and first[1] == second[1],
        "two-run exact-nonnewline reflow output drifted",
    )
    private_content, public_content, report, context = first
    if args.write:
        ENGINE.atomic_write(args.private_output, private_content)
        ENGINE.atomic_write(args.public_output, public_content)
    if args.check:
        require(
            args.private_output.is_file()
            and args.private_output.read_text(encoding="utf-8")
            == private_content,
            "private exact-nonnewline reflow override drifted",
        )
        require(
            args.public_output.is_file()
            and args.public_output.read_text(encoding="utf-8")
            == public_content,
            "tracked exact-nonnewline reflow report drifted",
        )
        validate_override_rows(
            read_jsonl(args.private_output),
            expected=context["rows"],
            candidate=context["candidate"],
        )
        validate_report(
            read_json(args.public_output),
            expected=context["report"],
        )
    print(
        "PASS "
        f"root_rows={report['scope']['exact_nonnewline_safe_root_rows']} "
        f"root_records={report['scope']['exact_nonnewline_safe_root_records']} "
        f"overrides={report['scope']['private_override_rows']} "
        f"candidate={report['candidate_binding']['after_reflow_candidate_packed_sha256']} "
        "steam_write=false"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        OSError,
        ValueError,
        RelativeReflowError,
        AUDIT.ResidualAuditError,
        FULL_AUDIT.FullCandidateAuditError,
        BASE_AUDIT.AuditError,
        ENGINE.RetranslationError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
