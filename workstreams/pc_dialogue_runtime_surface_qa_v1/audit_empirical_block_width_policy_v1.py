#!/usr/bin/env python3
"""Independently validate the proposed msggame empirical width policy.

This does not apply the PK event-dialogue 912px rule.  Final safety is checked
against the predecessor's empirical maximum line width and maximum literal
line count in the same block.  The existing relative +24px audit is also run
between each materialized remediation stage so that a broad final diff cannot
hide an abrupt stage transition.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

import audit_candidate_relative_width_v1 as RELATIVE


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
SCHEMA = "nobu16.kr.msggame-empirical-block-width-policy-audit.v1"
DEFAULT_SOURCE = RELATIVE.DEFAULT_BASE_SOURCE
DEFAULT_PRE_CALL = (
    REPO
    / "tmp"
    / "pc_dialogue_runtime_surface_remediation_v1"
    / "base"
    / "pre_call_assembly"
    / "MSG"
    / "JP"
    / "msggame.bin"
)
DEFAULT_CALL = (
    REPO
    / "tmp"
    / "pc_dialogue_runtime_surface_remediation_v1"
    / "base"
    / "call_assembly_candidate"
    / "MSG"
    / "JP"
    / "msggame.bin"
)
DEFAULT_FINAL = RELATIVE.DEFAULT_BASE_CANDIDATE
DEFAULT_PK_SOURCE = RELATIVE.DEFAULT_PK_SOURCE
DEFAULT_PK_FINAL = RELATIVE.DEFAULT_PK_CANDIDATE


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def block_line_count_maxima(
    literals: Mapping[tuple[int, int, int], str],
) -> dict[int, int]:
    maxima: dict[int, int] = defaultdict(int)
    for (block_id, _record_id, _literal_id), text in literals.items():
        maxima[block_id] = max(maxima[block_id], len(text.split("\n")))
    return dict(maxima)


def empirical_final_audit(
    resource: str,
    source_path: Path,
    candidate_path: Path,
) -> dict[str, Any]:
    source_records, source_sha256 = RELATIVE.SURFACE.records_from_path(
        source_path
    )
    candidate_records, candidate_sha256 = (
        RELATIVE.SURFACE.records_from_path(candidate_path)
    )
    source_literals = RELATIVE.literal_map(source_records)
    candidate_literals = RELATIVE.literal_map(candidate_records)
    width_maxima = RELATIVE.block_maxima(source_literals)
    line_count_maxima = block_line_count_maxima(source_literals)
    issues: list[dict[str, Any]] = []
    changed_literal_count = 0
    for coordinate in sorted(set(source_literals) & set(candidate_literals)):
        before = source_literals[coordinate]
        after = candidate_literals[coordinate]
        if before == after:
            continue
        changed_literal_count += 1
        lines = after.split("\n")
        block_id, record_id, literal_id = coordinate
        if len(lines) > line_count_maxima[block_id]:
            issues.append(
                {
                    "category":
                        "candidate_line_count_exceeds_predecessor_block_max",
                    "block_id": block_id,
                    "record_id": record_id,
                    "literal_id": literal_id,
                    "candidate_line_count": len(lines),
                    "predecessor_block_max_line_count":
                        line_count_maxima[block_id],
                }
            )
        for line_index, line in enumerate(lines):
            width = RELATIVE.raw_g1n_width_px(line)
            if width <= width_maxima[block_id]:
                continue
            issues.append(
                {
                    "category":
                        "candidate_line_exceeds_predecessor_block_max",
                    "block_id": block_id,
                    "record_id": record_id,
                    "literal_id": literal_id,
                    "line_index": line_index,
                    "candidate_width_px": width,
                    "predecessor_block_max_width_px":
                        width_maxima[block_id],
                }
            )
    if set(source_literals) != set(candidate_literals):
        issues.insert(
            0,
            {
                "category": "literal_coordinate_set_changed",
                "source_count": len(source_literals),
                "candidate_count": len(candidate_literals),
            },
        )
    category_counts = Counter(issue["category"] for issue in issues)
    return {
        "resource": resource,
        "status": "PASS" if not issues else "FAIL",
        "source": {
            "path": str(source_path.resolve()),
            "sha256": source_sha256,
            "size": source_path.stat().st_size,
        },
        "candidate": {
            "path": str(candidate_path.resolve()),
            "sha256": candidate_sha256,
            "size": candidate_path.stat().st_size,
        },
        "changed_literal_count": changed_literal_count,
        "issue_count": len(issues),
        "issue_coordinate_count": len(
            {
                (
                    issue.get("block_id"),
                    issue.get("record_id"),
                    issue.get("literal_id"),
                )
                for issue in issues
                if "block_id" in issue
            }
        ),
        "category_counts": dict(sorted(category_counts.items())),
        "issues": issues,
    }


def build_final_report(
    base_source: Path,
    base_candidate: Path,
    pk_source: Path,
    pk_candidate: Path,
) -> dict[str, Any]:
    resources = {
        "MSG/JP/msggame.bin": empirical_final_audit(
            "base_msggame",
            base_source,
            base_candidate,
        ),
        "MSG_PK/JP/msggame.bin": empirical_final_audit(
            "pk_msggame",
            pk_source,
            pk_candidate,
        ),
    }
    issue_count = sum(
        int(resource["issue_count"]) for resource in resources.values()
    )
    return {
        "schema": SCHEMA,
        "status": "PASS" if issue_count == 0 else "FAIL",
        "release_target": "0.15.0",
        "issue_count": issue_count,
        "resources": resources,
        "contract": {
            "event_dialogue_912px_gate_applied": False,
            "final_global_plus_24px_gate_applied": False,
            "candidate_line_must_fit_predecessor_same_block_max": True,
            "candidate_line_count_must_fit_predecessor_same_block_max":
                True,
            "base_and_pk_required": True,
        },
        "literal_bodies_omitted": True,
        "steam_write_performed": False,
    }


def stage_summary(
    name: str,
    predecessor: Path,
    candidate: Path,
) -> dict[str, Any]:
    result = RELATIVE.audit_pair(
        "base_msggame",
        predecessor,
        candidate,
    )
    return {
        "stage": name,
        **result,
    }


def build_report(
    source: Path,
    pre_call: Path,
    call: Path,
    final: Path,
    pk_source: Path,
    pk_final: Path,
) -> dict[str, Any]:
    final_report = build_final_report(
        source,
        final,
        pk_source,
        pk_final,
    )
    stages = [
        stage_summary("surface_remediation", source, pre_call),
        stage_summary("call_assembly_remediation", pre_call, call),
        stage_summary("post_call_selector_spacing", call, final),
    ]
    stage_issue_count = sum(stage["issue_count"] for stage in stages)
    status = "PASS" if final_report["issue_count"] == 0 else "FAIL"
    return {
        "schema": SCHEMA,
        "status": status,
        "release_target": "0.15.0",
        "final_empirical_block_report": final_report,
        "final_empirical_block_audits": final_report["resources"],
        "final_issue_count": final_report["issue_count"],
        "stage_relative_audits": stages,
        "diagnostic_stage_issue_count": stage_issue_count,
        "authoritative_stage_status": {
            "surface_remediation": stages[0]["status"],
            "call_assembly_remediation":
                "REQUIRES_EXACT_SEMANTIC_CONTRACT",
            "post_call_selector_spacing": stages[2]["status"],
        },
        "contract": {
            "event_dialogue_912px_gate_applied": False,
            "final_global_plus_24px_gate_applied": False,
            "candidate_line_must_fit_predecessor_same_block_max": True,
            "candidate_line_count_must_fit_predecessor_same_block_max":
                True,
            "stage_relative_plus_24px_gate_applied": True,
            "priority_exact_exceptions_only": True,
            "relative_engine_sha256": sha256_path(
                Path(RELATIVE.__file__).resolve()
            ),
            "approved_relative_growth_exception_count": len(
                RELATIVE.APPROVED_LINE_GROWTH_EXCEPTIONS
            ),
        },
        "literal_bodies_omitted": True,
        "steam_write_performed": False,
    }


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--pre-call", type=Path, default=DEFAULT_PRE_CALL)
    parser.add_argument("--call", type=Path, default=DEFAULT_CALL)
    parser.add_argument("--final", type=Path, default=DEFAULT_FINAL)
    parser.add_argument("--pk-source", type=Path, default=DEFAULT_PK_SOURCE)
    parser.add_argument("--pk-final", type=Path, default=DEFAULT_PK_FINAL)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(
        args.source,
        args.pre_call,
        args.call,
        args.final,
        args.pk_source,
        args.pk_final,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        canonical_json(report),
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "final_issue_count":
                    report["final_issue_count"],
                "final_issue_coordinate_count":
                    sum(
                        int(resource["issue_coordinate_count"])
                        for resource
                        in report["final_empirical_block_audits"].values()
                    ),
                "diagnostic_stage_issue_count":
                    report["diagnostic_stage_issue_count"],
                "stage_category_counts": {
                    stage["stage"]: stage["category_counts"]
                    for stage in report["stage_relative_audits"]
                },
            },
            sort_keys=True,
        )
    )
    return int(args.strict and report["status"] != "PASS")


if __name__ == "__main__":
    raise SystemExit(main())
