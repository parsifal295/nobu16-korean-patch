#!/usr/bin/env python3
"""Build the source-free PK overlay bound to the complete literal candidate."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
FULL_AUDIT_PATH = (
    WORKSTREAM / "build_pk_msggame_full_candidate_runtime_vm_audit_v1.py"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_msggame_full_candidate_runtime_vm_verified.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_msggame_full_candidate_runtime_vm_promotion.v1.json"
)

PROMOTION_SCHEMA = (
    "nobu16.kr.pk-msggame-full-candidate-runtime-vm-promotion.v1"
)
OVERLAY_ROW_SCHEMA = (
    "nobu16.kr.pk-msggame-full-candidate-runtime-vm-verification-overlay-row.v1"
)
METHOD = "reversed_vm_full_candidate_static_analysis"


class FullCandidatePromotionError(ValueError):
    """Raised when a full-candidate overlay proof drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FullCandidatePromotionError(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


FULL_AUDIT = load_module("pk_full_candidate_overlay_audit", FULL_AUDIT_PATH)
BASE_AUDIT = FULL_AUDIT.BASE_AUDIT
ENGINE = FULL_AUDIT.ENGINE


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def canonical_sha256(value: Any) -> str:
    return FULL_AUDIT.canonical_sha256(value)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n"


def canonical_jsonl(rows: Sequence[Mapping[str, Any]]) -> str:
    return "".join(
        json.dumps(
            row,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
        for row in rows
    )


def expected_overlay_row(
    coordinate: str,
    *,
    report: Mapping[str, Any],
    report_file_sha256: str,
    inputs: Any,
    source_rows: Mapping[str, dict[str, Any]],
) -> dict[str, Any]:
    require(coordinate in source_rows, f"exact source row is absent: {coordinate}")
    source = source_rows[coordinate]
    adjudication = report["row_adjudications"].get(coordinate)
    require(
        isinstance(adjudication, dict)
        and adjudication.get("status") == "promotion_eligible"
        and adjudication.get("taints") == []
        and adjudication.get("reason_codes") == []
        and adjudication.get("layout_change_pending") is False,
        f"blocked full-candidate row cannot be promoted: {coordinate}",
    )
    bound = BASE_AUDIT.validate_row_binding(
        source,
        prefill_report=inputs.prefill_report,
        base_promoted_rows=inputs.base_promoted_rows,
        base_coverage=inputs.base_coverage,
        base_source_records=inputs.base_source_records,
        base_candidate_records=inputs.base_candidate_records,
        pk_source_records=inputs.pk_source_records,
        pk_current_records=inputs.pk_current_records,
        pk_candidate_records=inputs.pk_candidate_records,
    )
    pair_key = adjudication["pair_key"]
    pair_guard = report["pair_proof_guards"].get(pair_key)
    require(
        isinstance(pair_guard, dict)
        and pair_guard.get("taints") == []
        and pair_guard.get("reason_codes") == [],
        f"full-candidate pair proof is tainted: {coordinate}",
    )
    row_guard = canonical_sha256(
        FULL_AUDIT.row_guard_payload(
            bound=bound,
            adjudication=adjudication,
            pair_guard=pair_guard,
            inputs=inputs,
        )
    )
    require(
        row_guard == adjudication.get("row_verification_guard_sha256"),
        f"full-candidate row guard drifted: {coordinate}",
    )
    prefill_evidence = source.get("base_exact_reuse_prefill")
    require(
        isinstance(prefill_evidence, dict),
        f"prefill evidence is absent: {coordinate}",
    )
    pk_record = bound["pk_record"]
    return {
        "schema": OVERLAY_ROW_SCHEMA,
        "resource": "pk_msggame",
        "coordinate": coordinate,
        "status": "verified",
        "method": METHOD,
        "scope_transition": {
            "from": "runtime_fragment_pending",
            "to": "retranslated",
        },
        "translation_utf16le_sha256": bound[
            "translation_utf16le_sha256"
        ],
        "source_decision_binding": {
            "decision_sha256": canonical_sha256(source),
            "prefill_evidence_sha256": canonical_sha256(prefill_evidence),
            "mapping_universe_sha256": prefill_evidence[
                "mapping_universe_sha256"
            ],
        },
        "full_candidate_binding": {
            "coverage_report_file_sha256": report_file_sha256,
            "coverage_report_payload_sha256": report["guards"][
                "report_payload_sha256"
            ],
            "pk_full_candidate_packed_sha256": report["candidate_scope"][
                "literal_candidate_packed_sha256"
            ],
            "replacement_manifest_sha256": report["guards"][
                "replacement_manifest_sha256"
            ],
            "source_decision_segment_universe_sha256": report["guards"][
                "source_decision_segment_universe_sha256"
            ],
            "pk_candidate_root_record_sha256": sha256_bytes(
                inputs.pk_candidate_records[pk_record].data
            ),
        },
        "audit_binding": {
            "row_verification_guard_sha256": row_guard,
            "pair_key": pair_key,
            "pair_proof_sha256": pair_guard["proof_sha256"],
            "pair_proof_guard_sha256": canonical_sha256(pair_guard),
        },
        "base_donor_binding": {
            "coordinate": bound["base_coordinate"],
            "base_vm_row_guard_sha256": bound["base_vm_row_guard"],
            "base_coverage_report_sha256": inputs.base_coverage_sha256,
            "base_candidate_packed_sha256": inputs.artifact_hashes[
                "base_candidate_packed_sha256"
            ],
        },
        "per_row_game_playback_required": False,
    }


def build_overlay_rows(
    *,
    report: Mapping[str, Any],
    report_file_sha256: str,
    inputs: Any,
) -> list[dict[str, Any]]:
    source_rows = {
        str(row["coordinate"]): row
        for row in inputs.rows
    }
    eligible = [
        coordinate
        for coordinate, adjudication in report["row_adjudications"].items()
        if adjudication["status"] == "promotion_eligible"
    ]
    eligible.sort(key=BASE_AUDIT.parse_literal_coordinate)
    require(
        len(eligible) == FULL_AUDIT.EXPECTED_ELIGIBLE_ROWS,
        "full-candidate eligible universe drifted",
    )
    return [
        expected_overlay_row(
            coordinate,
            report=report,
            report_file_sha256=report_file_sha256,
            inputs=inputs,
            source_rows=source_rows,
        )
        for coordinate in eligible
    ]


def validate_overlay_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    report: Mapping[str, Any],
    report_file_sha256: str,
    inputs: Any,
) -> None:
    expected = build_overlay_rows(
        report=report,
        report_file_sha256=report_file_sha256,
        inputs=inputs,
    )
    require(
        list(rows) == expected,
        "full-candidate verification overlay drifted",
    )


def read_overlay(path: Path) -> list[dict[str, Any]]:
    require(path.is_file(), f"private overlay is absent: {path}")
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def build_outputs() -> tuple[
    str,
    str,
    dict[str, Any],
    dict[str, Any],
]:
    coverage_content, coverage, inputs, metadata = FULL_AUDIT.build_outputs()
    report_file_sha256 = sha256_bytes(coverage_content.encode("utf-8"))
    require(
        FULL_AUDIT.DEFAULT_OUTPUT.is_file()
        and FULL_AUDIT.DEFAULT_OUTPUT.read_text(encoding="utf-8")
        == coverage_content,
        "tracked full-candidate coverage report drifted",
    )
    rows = build_overlay_rows(
        report=coverage,
        report_file_sha256=report_file_sha256,
        inputs=inputs,
    )
    validate_overlay_rows(
        rows,
        report=coverage,
        report_file_sha256=report_file_sha256,
        inputs=inputs,
    )
    private_content = canonical_jsonl(rows)
    private_sha256 = sha256_bytes(private_content.encode("utf-8"))
    report = {
        "schema": PROMOTION_SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "input": {
            "runtime_pending_exact_reuse_rows": coverage["scope"][
                "runtime_pending_rows"
            ],
            "promotion_eligible_rows": coverage["scope"][
                "promotion_eligible_rows"
            ],
            "blocked_rows_excluded": coverage["scope"]["blocked_rows"],
            "full_candidate_packed_sha256": coverage["candidate_scope"][
                "literal_candidate_packed_sha256"
            ],
        },
        "result": {
            "private_overlay_rows": len(rows),
            "private_overlay_sha256": private_sha256,
            "eligible_coordinate_universe_sha256": coverage["guards"][
                "eligible_coordinate_universe_sha256"
            ],
            "translation_body_copied": False,
        },
        "evidence": {
            "coverage_report": (
                "workstreams/pk_msggame_runtime_vm_audit_v1/public/"
                "pk_msggame_full_candidate_runtime_vm_coverage.v1.json"
            ),
            "coverage_report_file_sha256": report_file_sha256,
            "coverage_report_payload_sha256": coverage["guards"][
                "report_payload_sha256"
            ],
            "row_guard_universe_sha256": coverage["guards"][
                "row_verification_guards_sha256"
            ],
            "pair_guard_universe_sha256": coverage["guards"][
                "pair_proof_guards_sha256"
            ],
            "replacement_manifest_sha256": metadata[
                "replacement_manifest_sha256"
            ],
            "all_rows_recomputed_from_full_candidate": True,
        },
        "exclusion_policy": {
            "blocked_rows_included": 0,
            "layout_taint_rows_included": 0,
            "full_completeness_required":
            FULL_AUDIT.EXPECTED_ELIGIBLE_ROWS,
        },
        "integration_boundary": {
            "overlay_is_not_a_full_dialogue_decision_file": True,
            "shared_engine_integration_required": True,
            "full_candidate_bound": True,
        },
        "distribution_policy": {
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "private_overlay_contains_commercial_source_text": False,
            "private_overlay_contains_translated_dialogue_text": False,
            "private_overlay_stays_below_tmp": True,
        },
        "steam_write_performed": False,
    }
    context = {
        "coverage": coverage,
        "coverage_file_sha256": report_file_sha256,
        "inputs": inputs,
        "metadata": metadata,
    }
    return private_content, canonical_json(report), report, context


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
    private_root = DIALOGUE_TMP.resolve(strict=False)
    resolved_private = args.private_output.resolve(strict=False)
    require(
        resolved_private != private_root
        and private_root in resolved_private.parents,
        f"private output must remain below {private_root}",
    )
    first = build_outputs()
    second = build_outputs()
    require(first[0] == second[0], "two-run private overlay drifted")
    require(first[1] == second[1], "two-run promotion report drifted")
    private_content, public_content, report, context = first
    if args.write:
        ENGINE.atomic_write(args.private_output, private_content)
        ENGINE.atomic_write(args.public_output, public_content)
    if args.check:
        require(
            args.private_output.is_file()
            and args.private_output.read_text(encoding="utf-8")
            == private_content,
            "private full-candidate overlay drifted",
        )
        require(
            args.public_output.is_file()
            and args.public_output.read_text(encoding="utf-8")
            == public_content,
            "tracked full-candidate promotion report drifted",
        )
    validate_overlay_rows(
        read_overlay(args.private_output),
        report=context["coverage"],
        report_file_sha256=context["coverage_file_sha256"],
        inputs=context["inputs"],
    )
    print(
        "PASS "
        f"promoted={report['result']['private_overlay_rows']} "
        f"blocked_included={report['exclusion_policy']['blocked_rows_included']} "
        "steam_write=false"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        OSError,
        ValueError,
        FullCandidatePromotionError,
        FULL_AUDIT.FullCandidateAuditError,
        ENGINE.RetranslationError,
        BASE_AUDIT.AuditError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
