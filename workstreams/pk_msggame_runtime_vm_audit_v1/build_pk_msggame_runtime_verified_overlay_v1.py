#!/usr/bin/env python3
"""Build a source-free private overlay for PK runtime-verified reuse rows.

The overlay does not duplicate dialogue text and is deliberately kept outside
the normal ``pk_msggame_*.private.v1.jsonl`` decision directory glob.  It
binds the original prefill row to the tracked PK VM coverage, the synchronized
pair proof, and the Base donor VM row guard.  It never writes Steam.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_msggame_exact_reuse_runtime_vm_verified.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_msggame_runtime_vm_promotion.v1.json"
)
COVERAGE_PATH = (
    WORKSTREAM / "public" / "pk_msggame_runtime_vm_coverage.v1.json"
)
AUDIT_PATH = WORKSTREAM / "build_pk_msggame_runtime_vm_audit_v1.py"
LIVE_STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

PROMOTION_SCHEMA = "nobu16.kr.pk-msggame-runtime-vm-promotion.v1"
OVERLAY_ROW_SCHEMA = (
    "nobu16.kr.pk-msggame-exact-reuse-runtime-vm-verification-overlay-row.v1"
)
EXPECTED_ELIGIBLE_ROWS = 4_717


class PromotionError(ValueError):
    """Raised when an eligible-row or evidence binding drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PromotionError(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


AUDIT = load_module("pk_runtime_vm_verified_overlay_audit", AUDIT_PATH)


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


def canonical_jsonl(rows: list[dict[str, Any]]) -> str:
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


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as stream:
        temporary = Path(stream.name)
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def require_private_output_scope(path: Path) -> None:
    root = DIALOGUE_TMP.resolve(strict=False)
    resolved = path.resolve(strict=False)
    require(
        resolved != root and root in resolved.parents,
        f"private output must stay below {root}: {resolved}",
    )


def live_steam_hash() -> str | None:
    return (
        sha256_bytes(LIVE_STEAM_PK.read_bytes())
        if LIVE_STEAM_PK.is_file()
        else None
    )


def verified_audit() -> tuple[Any, dict[str, Any], str]:
    inputs = AUDIT.build_inputs()
    rebuilt = AUDIT.build_report(inputs)
    AUDIT.validate_report(rebuilt)
    require(COVERAGE_PATH.is_file(), f"tracked PK VM coverage is absent: {COVERAGE_PATH}")
    tracked_content = COVERAGE_PATH.read_text(encoding="utf-8")
    require(
        tracked_content == AUDIT.canonical_json(rebuilt),
        "tracked PK VM coverage report drifted",
    )
    return inputs, rebuilt, sha256_bytes(tracked_content.encode("utf-8"))


def pending_prefill_rows(inputs: Any) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in inputs.rows:
        coordinate = row.get("coordinate")
        AUDIT.parse_literal_coordinate(coordinate)
        require(
            isinstance(coordinate, str) and coordinate not in result,
            f"duplicate pending prefill coordinate: {coordinate}",
        )
        result[coordinate] = row
    require(
        len(result) == AUDIT.EXPECTED_PENDING_ROWS,
        "pending prefill universe drifted",
    )
    return result


def eligible_coordinates(report: Mapping[str, Any]) -> tuple[str, ...]:
    adjudications = report.get("row_adjudications")
    require(isinstance(adjudications, dict), "audit row adjudications are absent")
    values = tuple(
        sorted(
            (
                coordinate
                for coordinate, adjudication in adjudications.items()
                if adjudication.get("status") == "promotion_eligible"
            ),
            key=AUDIT.parse_literal_coordinate,
        )
    )
    require(
        len(values)
        == report.get("scope", {}).get("promotion_eligible_rows")
        == EXPECTED_ELIGIBLE_ROWS,
        "promotion-eligible coordinate universe drifted",
    )
    return values


def recompute_audit_row_guard(
    *,
    bound: Mapping[str, Any],
    adjudication: Mapping[str, Any],
    inputs: Any,
) -> str:
    pk_record = bound["pk_record"]
    payload = {
        "coordinate": bound["coordinate"],
        "base_coordinate": bound["base_coordinate"],
        "translation_utf16le_sha256": bound["translation_utf16le_sha256"],
        "row_evidence_sha256": bound["row_evidence_sha256"],
        "base_vm_row_guard": bound["base_vm_row_guard"],
        "base_coverage_sha256": inputs.base_coverage_sha256,
        "pair_proof_sha256": adjudication["pair_proof_sha256"],
        "pk_candidate_record_sha256": AUDIT.sha256_bytes(
            inputs.pk_candidate_records[pk_record].data
        ),
        "status": adjudication["status"],
        "taints": adjudication["taints"],
        "reason_codes": adjudication["reason_codes"],
        "layout_change_pending": adjudication["layout_change_pending"],
    }
    return AUDIT.canonical_sha256(payload)


def expected_overlay_row(
    coordinate: str,
    *,
    inputs: Any,
    report: Mapping[str, Any],
    report_file_sha256: str,
    prefill_rows: Mapping[str, dict[str, Any]],
) -> dict[str, Any]:
    require(coordinate in prefill_rows, f"eligible prefill row is absent: {coordinate}")
    source = prefill_rows[coordinate]
    adjudications = report["row_adjudications"]
    require(coordinate in adjudications, f"audit row is absent: {coordinate}")
    adjudication = adjudications[coordinate]
    require(
        adjudication.get("status") == "promotion_eligible"
        and adjudication.get("taints") == []
        and adjudication.get("reason_codes") == []
        and adjudication.get("layout_change_pending") is False
        and adjudication.get("base_vm_row_guard_present") is True,
        f"blocked or tainted row cannot be promoted: {coordinate}",
    )
    bound = AUDIT.validate_row_binding(
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
    require(
        bound["base_vm_row_guard"] is not None,
        f"eligible row has no Base donor VM guard: {coordinate}",
    )
    expected_pair_key = AUDIT.pair_key(
        bound["base_record"],
        bound["pk_record"],
    )
    require(
        adjudication.get("pair_key") == expected_pair_key,
        f"audit root pair binding drifted: {coordinate}",
    )
    pair_guards = report["pair_proof_guards"]
    require(expected_pair_key in pair_guards, f"pair proof is absent: {coordinate}")
    pair_guard = pair_guards[expected_pair_key]
    require(
        pair_guard.get("taints") == []
        and pair_guard.get("reason_codes") == [],
        f"tainted pair cannot be promoted: {coordinate}",
    )
    require(
        adjudication.get("pair_proof_sha256")
        == pair_guard.get("proof_sha256"),
        f"pair proof hash drifted: {coordinate}",
    )
    recomputed_row_guard = recompute_audit_row_guard(
        bound=bound,
        adjudication=adjudication,
        inputs=inputs,
    )
    require(
        recomputed_row_guard
        == adjudication.get("row_verification_guard_sha256"),
        f"audit row verification guard drifted: {coordinate}",
    )

    prefill_evidence = source.get("base_exact_reuse_prefill")
    require(
        isinstance(prefill_evidence, dict),
        f"prefill evidence is absent: {coordinate}",
    )
    translation = source.get("translation")
    require(isinstance(translation, str), f"prefill translation is absent: {coordinate}")
    translation_hash = sha256_bytes(translation.encode("utf-16-le"))
    require(
        translation_hash == prefill_evidence.get("translation_utf16le_sha256"),
        f"prefill translation hash drifted: {coordinate}",
    )
    base_coordinate = prefill_evidence.get("base_coordinate")
    require(
        base_coordinate == bound["base_coordinate"],
        f"Base donor coordinate drifted: {coordinate}",
    )

    return {
        "schema": OVERLAY_ROW_SCHEMA,
        "resource": "pk_msggame",
        "coordinate": coordinate,
        "status": "verified",
        "method": "reversed_vm_static_analysis",
        "scope_transition": {
            "from": "runtime_fragment_pending",
            "to": "retranslated",
        },
        "translation_utf16le_sha256": translation_hash,
        "prefill_binding": {
            "decision_sha256": canonical_sha256(source),
            "evidence_sha256": canonical_sha256(prefill_evidence),
            "mapping_universe_sha256": prefill_evidence[
                "mapping_universe_sha256"
            ],
            "pk_candidate_packed_sha256": inputs.artifact_hashes[
                "pk_candidate_packed_sha256"
            ],
        },
        "audit_binding": {
            "coverage_report_file_sha256": report_file_sha256,
            "coverage_report_payload_sha256": report["guards"][
                "report_payload_sha256"
            ],
            "row_adjudication_sha256": canonical_sha256(adjudication),
            "row_verification_guard_sha256": recomputed_row_guard,
            "pair_key": expected_pair_key,
            "pair_proof_sha256": pair_guard["proof_sha256"],
            "pair_proof_guard_sha256": canonical_sha256(pair_guard),
        },
        "base_donor_binding": {
            "coordinate": base_coordinate,
            "base_vm_row_guard_sha256": bound["base_vm_row_guard"],
            "base_coverage_report_sha256": inputs.base_coverage_sha256,
        },
        "per_row_game_playback_required": False,
    }


def build_overlay_rows(
    *,
    inputs: Any,
    report: Mapping[str, Any],
    report_file_sha256: str,
) -> list[dict[str, Any]]:
    AUDIT.validate_report(report)
    prefill_rows = pending_prefill_rows(inputs)
    rows = [
        expected_overlay_row(
            coordinate,
            inputs=inputs,
            report=report,
            report_file_sha256=report_file_sha256,
            prefill_rows=prefill_rows,
        )
        for coordinate in eligible_coordinates(report)
    ]
    require(len(rows) == EXPECTED_ELIGIBLE_ROWS, "overlay row count drifted")
    return rows


def validate_overlay_rows(
    rows: list[dict[str, Any]],
    *,
    inputs: Any,
    report: Mapping[str, Any],
    report_file_sha256: str,
) -> None:
    prefill_rows = pending_prefill_rows(inputs)
    expected_coordinates = eligible_coordinates(report)
    actual_coordinates: list[str] = []
    seen: set[str] = set()
    for row in rows:
        coordinate = row.get("coordinate")
        AUDIT.parse_literal_coordinate(coordinate)
        require(
            isinstance(coordinate, str) and coordinate not in seen,
            f"duplicate overlay coordinate: {coordinate}",
        )
        seen.add(coordinate)
        actual_coordinates.append(coordinate)
        expected = expected_overlay_row(
            coordinate,
            inputs=inputs,
            report=report,
            report_file_sha256=report_file_sha256,
            prefill_rows=prefill_rows,
        )
        require(row == expected, f"overlay evidence drifted: {coordinate}")
    require(
        tuple(actual_coordinates) == expected_coordinates,
        "overlay completeness or ordering drifted",
    )
    require(len(rows) == EXPECTED_ELIGIBLE_ROWS, "overlay completeness drifted")


def read_overlay(path: Path) -> list[dict[str, Any]]:
    require(path.is_file(), f"private verification overlay is absent: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line:
            continue
        value = json.loads(line)
        require(isinstance(value, dict), f"{path}:{line_number} is not an object")
        rows.append(value)
    return rows


def build_outputs() -> tuple[str, str, dict[str, Any], Any, dict[str, Any]]:
    steam_before = live_steam_hash()
    inputs, coverage, coverage_file_sha256 = verified_audit()
    rows = build_overlay_rows(
        inputs=inputs,
        report=coverage,
        report_file_sha256=coverage_file_sha256,
    )
    validate_overlay_rows(
        rows,
        inputs=inputs,
        report=coverage,
        report_file_sha256=coverage_file_sha256,
    )
    private_content = canonical_jsonl(rows)
    private_sha256 = sha256_bytes(private_content.encode("utf-8"))
    coordinate_digest = sha256_bytes(
        "\n".join(row["coordinate"] for row in rows).encode("ascii")
    )
    steam_after = live_steam_hash()
    require(steam_after == steam_before, "Steam PK msggame changed during overlay build")
    report = {
        "schema": PROMOTION_SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "input": {
            "runtime_pending_prefill_rows": coverage["scope"][
                "runtime_pending_rows"
            ],
            "promotion_eligible_rows": coverage["scope"][
                "promotion_eligible_rows"
            ],
            "blocked_rows_excluded": coverage["scope"]["blocked_rows"],
        },
        "result": {
            "private_overlay_rows": len(rows),
            "private_overlay_sha256": private_sha256,
            "eligible_coordinate_universe_sha256": coordinate_digest,
            "translation_body_copied": False,
        },
        "evidence": {
            "coverage_report": (
                "workstreams/pk_msggame_runtime_vm_audit_v1/public/"
                "pk_msggame_runtime_vm_coverage.v1.json"
            ),
            "coverage_report_file_sha256": coverage_file_sha256,
            "coverage_report_payload_sha256": coverage["guards"][
                "report_payload_sha256"
            ],
            "coverage_row_guard_universe_sha256": coverage["guards"][
                "row_verification_guards_sha256"
            ],
            "coverage_pair_guard_universe_sha256": coverage["guards"][
                "pair_proof_guards_sha256"
            ],
            "base_coverage_report_sha256": inputs.base_coverage_sha256,
            "original_prefill_row_and_evidence_hashes_rechecked": True,
            "translation_utf16le_hashes_rechecked": True,
            "base_donor_vm_guards_rechecked": True,
        },
        "exclusion_policy": {
            "blocked_rows_included": 0,
            "novel_taint_rows_included": 0,
            "layout_taint_rows_included": 0,
            "donor_taint_rows_included": 0,
            "closure_taint_rows_included": 0,
            "sibling_taint_rows_included": 0,
            "full_completeness_required": EXPECTED_ELIGIBLE_ROWS,
        },
        "integration_boundary": {
            "overlay_is_not_a_full_dialogue_decision_file": True,
            "shared_engine_modified": False,
            "central_progress_modified": False,
            "prefill_builder_modified": False,
            "separate_integration_required": True,
        },
        "distribution_policy": {
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "private_overlay_contains_commercial_source_text": False,
            "private_overlay_contains_translated_dialogue_text": False,
            "private_overlay_stays_below_tmp": True,
        },
        "steam_read_guard": {
            "path": str(LIVE_STEAM_PK),
            "before_sha256": steam_before,
            "after_sha256": steam_after,
            "unchanged": steam_before == steam_after,
        },
        "steam_write_performed": False,
    }
    context = {
        "inputs": inputs,
        "coverage": coverage,
        "coverage_file_sha256": coverage_file_sha256,
        "rows": rows,
    }
    return private_content, canonical_json(report), report, inputs, context


def main() -> int:
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
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    require_private_output_scope(args.private_output)

    first = build_outputs()
    second = build_outputs()
    require(first[0] == second[0], "private overlay two-run reproduction drifted")
    require(first[1] == second[1], "public promotion two-run reproduction drifted")
    private_content, public_content, report, _inputs, context = first
    if args.check:
        require(
            args.private_output.is_file(),
            f"private verification overlay is absent: {args.private_output}",
        )
        require(
            args.private_output.read_text(encoding="utf-8") == private_content,
            "private verification overlay drifted",
        )
        require(
            args.public_output.is_file(),
            f"public promotion report is absent: {args.public_output}",
        )
        require(
            args.public_output.read_text(encoding="utf-8") == public_content,
            "public promotion report drifted",
        )
    else:
        atomic_write(args.private_output, private_content)
        atomic_write(args.public_output, public_content)

    output_rows = read_overlay(args.private_output)
    validate_overlay_rows(
        output_rows,
        inputs=context["inputs"],
        report=context["coverage"],
        report_file_sha256=context["coverage_file_sha256"],
    )
    print(
        f"PASS promoted={report['result']['private_overlay_rows']} "
        f"blocked_included={report['exclusion_policy']['blocked_rows_included']} "
        "steam_write=false"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, PromotionError, AUDIT.AuditError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
