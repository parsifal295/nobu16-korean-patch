#!/usr/bin/env python3
"""Build the bound verification overlay for conservative PK residual rows."""

from __future__ import annotations

import argparse
import copy
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
AUDIT_PATH = (
    WORKSTREAM / "build_pk_msggame_residual_runtime_vm_audit_v1.py"
)
COVERAGE_PATH = (
    WORKSTREAM
    / "public"
    / "pk_msggame_residual_runtime_vm_coverage.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_msggame_residual_runtime_vm_verified.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_msggame_residual_runtime_vm_promotion.v1.json"
)

PROMOTION_SCHEMA = (
    "nobu16.kr.pk-msggame-residual-runtime-vm-promotion.v1"
)
OVERLAY_ROW_SCHEMA = (
    "nobu16.kr.pk-msggame-residual-runtime-vm-verification-overlay-row.v1"
)
METHOD = "reversed_vm_residual_full_closure_nonexpansion_analysis"
EXPECTED_ROWS = 1_889


class ResidualPromotionError(ValueError):
    """Raised when the residual overlay proof drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ResidualPromotionError(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


AUDIT = load_module("pk_residual_overlay_audit", AUDIT_PATH)
FULL_AUDIT = AUDIT.FULL_AUDIT
ENGINE = AUDIT.ENGINE


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def canonical_sha256(value: Any) -> str:
    return AUDIT.canonical_sha256(value)


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


def read_overlay(path: Path) -> list[dict[str, Any]]:
    require(path.is_file(), f"private residual overlay is absent: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line:
            continue
        row = json.loads(line)
        require(
            isinstance(row, dict),
            f"{path}:{line_number} is not an object",
        )
        rows.append(row)
    return rows


def expected_overlay_row(
    coordinate: str,
    *,
    report: Mapping[str, Any],
    report_file_sha256: str,
    inputs: Any,
    source_rows: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    source = source_rows.get(coordinate)
    adjudication = report["row_adjudications"].get(coordinate)
    require(
        isinstance(source, dict)
        and source.get("runtime_review") == "pending"
        and source.get("scope_classification")
        == "runtime_fragment_pending"
        and source.get("layout_review") == "runtime_pending",
        f"residual source row is not promotable: {coordinate}",
    )
    require(
        isinstance(adjudication, dict)
        and adjudication.get("status") == "promotion_eligible"
        and adjudication.get("tier") == "A"
        and adjudication.get("layout_adjudication")
        == "relative_full_closure_line_envelope_nonexpanding",
        f"residual adjudication is not eligible: {coordinate}",
    )
    require(
        adjudication["source_decision_sha256"]
        == canonical_sha256(source)
        and adjudication["translation_utf16le_sha256"]
        == ENGINE.sha256_text(source["translation"]),
        f"residual source binding drifted: {coordinate}",
    )
    record = tuple(adjudication["record"])
    record_key = f"{record[0]}:{record[1]}"
    record_proof = report["record_proofs"].get(record_key)
    require(
        isinstance(record_proof, dict)
        and record_proof.get("status") == "promotion_eligible"
        and record_proof.get("reason_codes") == []
        and record_proof.get("proof_sha256")
        == adjudication["record_proof_sha256"],
        f"residual record proof drifted: {coordinate}",
    )
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
        "layout_transition": {
            "from": "runtime_pending",
            "to": "runtime_verified",
        },
        "translation_utf16le_sha256": adjudication[
            "translation_utf16le_sha256"
        ],
        "source_decision_binding": {
            "decision_sha256": adjudication[
                "source_decision_sha256"
            ],
        },
        "full_candidate_binding": {
            "coverage_report_file_sha256": report_file_sha256,
            "coverage_report_payload_sha256": report["guards"][
                "report_payload_sha256"
            ],
            "pk_full_candidate_packed_sha256": report[
                "candidate_binding"
            ]["pk_full_candidate_packed_sha256"],
            "replacement_manifest_sha256": report[
                "candidate_binding"
            ]["replacement_manifest_sha256"],
            "semantic_override_private_sha256": report[
                "candidate_binding"
            ]["semantic_override_private_sha256"],
            "pk_candidate_root_record_sha256": sha256_bytes(
                inputs.pk_candidate_records[record].data
            ),
        },
        "audit_binding": {
            "row_verification_guard_sha256": adjudication[
                "row_verification_guard_sha256"
            ],
            "record_proof_sha256": record_proof["proof_sha256"],
            "source_candidate_closure_proof_sha256": record_proof[
                "source_candidate_closure_proof_sha256"
            ],
            "eligible_coordinate_universe_sha256": report["guards"][
                "eligible_coordinate_sha256"
            ],
            "eligible_record_universe_sha256": report["guards"][
                "eligible_record_sha256"
            ],
        },
        "per_row_game_playback_required": False,
        "representative_game_smoke_required_before_release": True,
    }


def build_overlay_rows(
    *,
    report: Mapping[str, Any],
    report_file_sha256: str,
    inputs: Any,
) -> list[dict[str, Any]]:
    source_values, _source_metadata = FULL_AUDIT.source_decisions()
    source_rows = {
        str(row["coordinate"]): row for row in source_values
    }
    coordinates = sorted(
        report["row_adjudications"],
        key=AUDIT.parse_coordinate,
    )
    require(
        len(coordinates) == EXPECTED_ROWS,
        "residual promotion row count drifted",
    )
    return [
        expected_overlay_row(
            coordinate,
            report=report,
            report_file_sha256=report_file_sha256,
            inputs=inputs,
            source_rows=source_rows,
        )
        for coordinate in coordinates
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
        "residual verification overlay drifted",
    )
    require(
        len({str(row["coordinate"]) for row in rows})
        == len(rows)
        == EXPECTED_ROWS,
        "residual verification overlay coordinate universe drifted",
    )


def build_outputs() -> tuple[
    str,
    str,
    dict[str, Any],
    dict[str, Any],
]:
    coverage_content, coverage, inputs, full_metadata = (
        AUDIT.build_outputs()
    )
    require(
        COVERAGE_PATH.is_file()
        and COVERAGE_PATH.read_text(encoding="utf-8")
        == coverage_content,
        "tracked residual coverage drifted",
    )
    coverage_file_sha256 = sha256_bytes(COVERAGE_PATH.read_bytes())
    rows = build_overlay_rows(
        report=coverage,
        report_file_sha256=coverage_file_sha256,
        inputs=inputs,
    )
    validate_overlay_rows(
        rows,
        report=coverage,
        report_file_sha256=coverage_file_sha256,
        inputs=inputs,
    )
    private_content = canonical_jsonl(rows)
    private_sha256 = sha256_bytes(private_content.encode("utf-8"))
    report = {
        "schema": PROMOTION_SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "resource": "pk_msggame",
        "method": METHOD,
        "input": {
            "coverage_report_file_sha256": coverage_file_sha256,
            "coverage_report_payload_sha256": coverage["guards"][
                "report_payload_sha256"
            ],
            "pk_full_candidate_packed_sha256": coverage[
                "candidate_binding"
            ]["pk_full_candidate_packed_sha256"],
            "source_decision_segment_universe_sha256": full_metadata[
                "source_decision_segment_universe_sha256"
            ],
        },
        "result": {
            "private_overlay_rows": len(rows),
            "private_overlay_sha256": private_sha256,
            "eligible_coordinate_sha256": coverage["guards"][
                "eligible_coordinate_sha256"
            ],
            "eligible_record_sha256": coverage["guards"][
                "eligible_record_sha256"
            ],
            "layout_review_transition": "runtime_pending_to_runtime_verified",
        },
        "validation": {
            "coverage_rebuilt_and_rechecked": True,
            "full_candidate_binding_rechecked": True,
            "complete_closure_nonexpansion_rechecked": True,
            "runtime_and_layout_transition_bound": True,
            "two_run_deterministic": True,
        },
        "distribution_policy": {
            "private_overlay_contains_commercial_source_text": False,
            "private_overlay_contains_translated_dialogue_text": False,
            "private_overlay_stays_below_tmp": True,
        },
        "steam_write_performed": False,
    }
    unsealed = copy.deepcopy(report)
    report["report_payload_sha256"] = canonical_sha256(unsealed)
    return private_content, canonical_json(report), report, {
        "coverage": coverage,
        "coverage_file_sha256": coverage_file_sha256,
        "inputs": inputs,
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
    require(first[:3] == second[:3], "two-run residual overlay drifted")
    private_content, public_content, report, context = first
    if args.write:
        ENGINE.atomic_write(args.private_output, private_content)
        ENGINE.atomic_write(args.public_output, public_content)
    if args.check:
        require(
            args.private_output.is_file()
            and args.private_output.read_text(encoding="utf-8")
            == private_content,
            "private residual overlay drifted",
        )
        require(
            args.public_output.is_file()
            and args.public_output.read_text(encoding="utf-8")
            == public_content,
            "tracked residual promotion report drifted",
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
        "layout=runtime_verified "
        f"steam_write={str(report['steam_write_performed']).lower()}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        OSError,
        ValueError,
        ResidualPromotionError,
        AUDIT.ResidualAuditError,
        ENGINE.RetranslationError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
