#!/usr/bin/env python3
"""Re-audit exact-reuse PK rows against the complete final literal candidate.

The earlier PK audit deliberately used the Base-exact prefill candidate.  A
later residual translation can change a sibling literal in the same record,
so this audit rebuilds all 29,038 PK decisions first and binds every row and
transitive pair proof to that complete candidate.  It writes only a
source-free report and never writes Steam.
"""

from __future__ import annotations

import argparse
import copy
import dataclasses
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_WORKSTREAM = (
    REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
)
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
DECISIONS_DIR = DIALOGUE_TMP / "decisions"
ENGINE_PATH = (
    DIALOGUE_WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
)
BASE_AUDIT_PATH = WORKSTREAM / "build_pk_msggame_runtime_vm_audit_v1.py"
BASE_PREFILL_COVERAGE_PATH = (
    WORKSTREAM / "public" / "pk_msggame_runtime_vm_coverage.v1.json"
)
DEFAULT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_msggame_full_candidate_runtime_vm_coverage.v1.json"
)

SCHEMA = "nobu16.kr.pk-msggame-full-candidate-runtime-vm-coverage.v1"
EXPECTED_SOURCE_SEGMENTS = 408
EXPECTED_PK_ROWS = 29_038
EXPECTED_STRING_REPLACEMENTS = 28_956
EXPECTED_EXACT_ROWS = 9_770
EXPECTED_ELIGIBLE_ROWS = 7_453
EXPECTED_BLOCKED_ROWS = 2_317
EXPECTED_KEPT_ELIGIBLE_ROWS = 4_663
EXPECTED_NEW_ELIGIBLE_ROWS = 2_790
EXPECTED_NEW_BLOCKED_ROWS = 54
EXPECTED_FULL_CANDIDATE_SHA256 = (
    "5480D65CE6BF15A35549FE6013DC7F03787A5713E06BDD3E2C50418F31B1CA22"
)
EXPECTED_ELIGIBLE_COORDINATE_SHA256 = (
    "0D9D424C2EEBBD652EFF807BEF604164C9691011839C724658F5808BD4A64147"
)
EXPECTED_BLOCKED_COORDINATE_SHA256 = (
    "AD52864FFA21C9B1158E5C1EABCB2D6D9D8B16796BF6F84695D53B721337ADA4"
)
EXPECTED_NEW_ELIGIBLE_COORDINATE_SHA256 = (
    "8019ED8335DF4CC02896770ED512C759DC9A927A5B10D998AD1A00F641D84DBE"
)
EXPECTED_NEW_BLOCKED_COORDINATE_SHA256 = (
    "22F8BAC68A5C05130BE1A6EABE6268AF5E056A245FFF0590BCB0F45950A5F6D5"
)
EXPECTED_PK_SOURCE_CANDIDATE_TAINT_ROWS = 13
EXPECTED_PK_SOURCE_CANDIDATE_TAINT_COORDINATE_SHA256 = (
    "3811287253C5634BA0A9B3A6FDE6FEF97429F0727271F7EFB1A5C0F87494AC1A"
)


class FullCandidateAuditError(ValueError):
    """Raised when a complete-candidate proof binding drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FullCandidateAuditError(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_module("pk_full_candidate_runtime_engine", ENGINE_PATH)
BASE_AUDIT = load_module("pk_full_candidate_base_audit", BASE_AUDIT_PATH)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def canonical_sha256(value: Any) -> str:
    return BASE_AUDIT.canonical_sha256(value)


def canonical_json(value: Any) -> str:
    return BASE_AUDIT.canonical_json(value)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
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


def coordinate_digest(coordinates: Sequence[str]) -> str:
    return canonical_sha256(
        sorted(coordinates, key=BASE_AUDIT.parse_literal_coordinate)
    )


def source_decisions() -> tuple[
    list[dict[str, Any]],
    dict[str, Any],
]:
    prepared = ENGINE.prepare_artifacts(
        BASE_AUDIT.SHADOW_STEAM_ROOT,
        BASE_AUDIT.DEFAULT_BASE_PRISTINE,
        BASE_AUDIT.DEFAULT_PK_PRISTINE,
    )
    paths = sorted(DECISIONS_DIR.glob("pk_msggame*.private.v1.jsonl"))
    require(
        len(paths) == EXPECTED_SOURCE_SEGMENTS,
        f"PK source decision segment count drifted: {len(paths)}",
    )
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    segment_guards: list[dict[str, Any]] = []
    for path in paths:
        ENGINE.validate_decisions(prepared, path, require_complete=False)
        values = load_jsonl(path)
        for row in values:
            coordinate = str(row.get("coordinate"))
            require(
                row.get("resource") == "pk_msggame"
                and coordinate not in seen,
                f"invalid or duplicate PK source decision: {coordinate}",
            )
            seen.add(coordinate)
            rows.append(row)
        segment_guards.append(
            {
                "name": path.name,
                "row_count": len(values),
                "sha256": sha256_bytes(path.read_bytes()),
            }
        )
    require(
        len(rows) == len(seen) == EXPECTED_PK_ROWS,
        f"PK decision universe drifted: {len(rows)}",
    )
    rows.sort(
        key=lambda row: BASE_AUDIT.parse_literal_coordinate(
            row["coordinate"]
        )
    )
    replacement_manifest = [
        {
            "coordinate": row["coordinate"],
            "translation_utf16le_sha256": ENGINE.sha256_text(
                row["translation"]
            ),
        }
        for row in rows
        if isinstance(row.get("translation"), str)
    ]
    require(
        len(replacement_manifest) == EXPECTED_STRING_REPLACEMENTS,
        "PK full-candidate replacement count drifted",
    )
    return rows, {
        "source_decision_segment_count": len(paths),
        "source_decision_segment_universe_sha256": canonical_sha256(
            segment_guards
        ),
        "replacement_count": len(replacement_manifest),
        "replacement_manifest_sha256": canonical_sha256(
            replacement_manifest
        ),
    }


def full_candidate_inputs() -> tuple[Any, dict[str, Any]]:
    rows, metadata = source_decisions()
    baseline = BASE_AUDIT.build_inputs()
    replacements = {
        BASE_AUDIT.parse_literal_coordinate(row["coordinate"]):
        row["translation"]
        for row in rows
        if isinstance(row.get("translation"), str)
    }
    current_blob = BASE_AUDIT.DEFAULT_PK_CURRENT.read_bytes()
    candidate_blob = BASE_AUDIT.rebuild_packed_with_literals(
        current_blob,
        replacements,
    )
    candidate_sha256 = sha256_bytes(candidate_blob)
    require(
        candidate_sha256 == EXPECTED_FULL_CANDIDATE_SHA256,
        f"PK full literal candidate hash drifted: {candidate_sha256}",
    )
    artifact_hashes = dict(baseline.artifact_hashes)
    artifact_hashes.update(
        {
            "pk_candidate_packed_sha256": candidate_sha256,
            "pk_full_candidate_packed_sha256": candidate_sha256,
            "pk_full_candidate_replacement_manifest_sha256": metadata[
                "replacement_manifest_sha256"
            ],
            "pk_full_candidate_source_segment_universe_sha256": metadata[
                "source_decision_segment_universe_sha256"
            ],
        }
    )
    inputs = dataclasses.replace(
        baseline,
        pk_candidate_records=BASE_AUDIT.records_from_blob(candidate_blob),
        artifact_hashes=artifact_hashes,
    )
    return inputs, metadata


def pk_component_signature(component: Mapping[str, Any]) -> dict[str, Any]:
    result = BASE_AUDIT.structural_component(component)
    if component["kind"] in {"call", "jump"}:
        result = {
            **result,
            "operand": component["operand"],
            "target": component["target"],
        }
    return result


def pk_source_candidate_closure_guard(
    root: tuple[int, int],
    *,
    inputs: Any,
) -> dict[str, Any]:
    queue: list[tuple[tuple[int, int], int]] = [(root, 0)]
    seen: set[tuple[int, int]] = set()
    proof_records: list[dict[str, Any]] = []
    proof_edges: list[dict[str, Any]] = []
    taints: set[str] = set()
    reasons: set[str] = set()
    call_count = 0
    jump_count = 0
    while queue:
        coordinate, depth = queue.pop()
        if coordinate in seen:
            continue
        seen.add(coordinate)
        source = inputs.pk_source_records.get(coordinate)
        candidate = inputs.pk_candidate_records.get(coordinate)
        if source is None or candidate is None:
            taints.add("pk_source_candidate_control_taint")
            reasons.add(
                "pk_source_candidate_closure_target_missing"
                if depth
                else "pk_source_candidate_target_missing"
            )
            continue
        try:
            source_components = BASE_AUDIT.decode_record(source)
            candidate_components = BASE_AUDIT.decode_record(candidate)
        except BASE_AUDIT.AuditError:
            taints.add("pk_source_candidate_control_taint")
            reasons.add(
                "pk_source_candidate_closure_decode_failure"
                if depth
                else "pk_source_candidate_decode_failure"
            )
            continue
        source_signatures = [
            pk_component_signature(component)
            for component in source_components
        ]
        candidate_signatures = [
            pk_component_signature(component)
            for component in candidate_components
        ]
        proof_records.append(
            {
                "coordinate": list(coordinate),
                "source_record_sha256": sha256_bytes(source.data),
                "candidate_record_sha256": sha256_bytes(candidate.data),
                "source_component_sha256": canonical_sha256(
                    source_signatures
                ),
                "candidate_component_sha256": canonical_sha256(
                    candidate_signatures
                ),
            }
        )
        if source_signatures != candidate_signatures:
            taints.add("pk_source_candidate_control_taint")
            reasons.add(
                "pk_source_candidate_closure_component_mismatch"
                if depth
                else "pk_source_candidate_component_mismatch"
            )
        for occurrence, component in enumerate(source_components):
            if component["kind"] not in {"call", "jump"}:
                continue
            target = tuple(component["target"])
            proof_edges.append(
                {
                    "source": list(coordinate),
                    "occurrence": occurrence,
                    "kind": component["kind"],
                    "operand": component["operand"],
                    "target": list(target),
                }
            )
            if component["kind"] == "call":
                call_count += 1
            else:
                jump_count += 1
            queue.append((target, depth + 1))
    proof = {
        "root": list(root),
        "records": sorted(
            proof_records,
            key=lambda value: value["coordinate"],
        ),
        "edges": sorted(
            proof_edges,
            key=lambda value: (
                value["source"],
                value["occurrence"],
                value["kind"],
            ),
        ),
        "taints": sorted(taints),
        "reason_codes": sorted(reasons),
    }
    return {
        "proof_sha256": canonical_sha256(proof),
        "taints": sorted(taints),
        "reason_codes": sorted(reasons),
        "visited_record_count": len(seen),
        "0143_occurrences": call_count,
        "014a_occurrences": jump_count,
    }


def pk_source_candidate_closure_guards(
    inputs: Any,
) -> dict[str, dict[str, Any]]:
    roots = {
        BASE_AUDIT.parse_literal_coordinate(row["coordinate"])[:2]
        for row in inputs.rows
    }
    return {
        f"{root[0]}:{root[1]}": pk_source_candidate_closure_guard(
            root,
            inputs=inputs,
        )
        for root in sorted(roots)
    }


def apply_pk_source_candidate_gate(
    report: dict[str, Any],
    *,
    inputs: Any,
) -> dict[str, dict[str, Any]]:
    closure_guards = pk_source_candidate_closure_guards(inputs)
    for coordinate, adjudication in report["row_adjudications"].items():
        block_id, record_id, _literal_id = (
            BASE_AUDIT.parse_literal_coordinate(coordinate)
        )
        guard = closure_guards[f"{block_id}:{record_id}"]
        adjudication[
            "pk_source_candidate_closure_proof_sha256"
        ] = guard["proof_sha256"]
        if guard["taints"]:
            adjudication["taints"] = sorted(
                set(adjudication["taints"]) | set(guard["taints"])
            )
            adjudication["reason_codes"] = sorted(
                set(adjudication["reason_codes"])
                | set(guard["reason_codes"])
            )
            adjudication["status"] = "blocked"
    eligible_count = sum(
        row["status"] == "promotion_eligible"
        for row in report["row_adjudications"].values()
    )
    report["scope"]["promotion_eligible_rows"] = eligible_count
    report["scope"]["blocked_rows"] = (
        len(report["row_adjudications"]) - eligible_count
    )
    taint_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    for adjudication in report["row_adjudications"].values():
        taint_counts.update(adjudication["taints"])
        reason_counts.update(adjudication["reason_codes"])
    report["blockers"]["taint_row_counts"] = dict(
        sorted(taint_counts.items())
    )
    report["blockers"]["reason_row_counts"] = dict(
        sorted(reason_counts.items())
    )
    tainted_coordinates = [
        coordinate
        for coordinate, adjudication in report["row_adjudications"].items()
        if "pk_source_candidate_control_taint"
        in adjudication["taints"]
    ]
    require(
        len(tainted_coordinates) == EXPECTED_PK_SOURCE_CANDIDATE_TAINT_ROWS
        and coordinate_digest(tainted_coordinates)
        == EXPECTED_PK_SOURCE_CANDIDATE_TAINT_COORDINATE_SHA256,
        "PK source-candidate control-taint universe drifted",
    )
    report["blockers"]["pk_source_candidate_control_taint_rows"] = len(
        tainted_coordinates
    )
    return closure_guards


def row_guard_payload(
    *,
    bound: Mapping[str, Any],
    adjudication: Mapping[str, Any],
    pair_guard: Mapping[str, Any],
    inputs: Any,
) -> dict[str, Any]:
    pk_record = bound["pk_record"]
    return {
        "coordinate": bound["coordinate"],
        "base_coordinate": bound["base_coordinate"],
        "translation_utf16le_sha256": bound[
            "translation_utf16le_sha256"
        ],
        "row_evidence_sha256": bound["row_evidence_sha256"],
        "base_vm_row_guard": bound["base_vm_row_guard"],
        "base_coverage_sha256": inputs.base_coverage_sha256,
        "base_candidate_packed_sha256": inputs.artifact_hashes[
            "base_candidate_packed_sha256"
        ],
        "pk_full_candidate_packed_sha256": inputs.artifact_hashes[
            "pk_full_candidate_packed_sha256"
        ],
        "pair_key": adjudication["pair_key"],
        "pair_proof_sha256": pair_guard["proof_sha256"],
        "pk_source_candidate_closure_proof_sha256": adjudication[
            "pk_source_candidate_closure_proof_sha256"
        ],
        "pk_source_root_record_sha256": sha256_bytes(
            inputs.pk_source_records[pk_record].data
        ),
        "pk_candidate_root_record_sha256": sha256_bytes(
            inputs.pk_candidate_records[pk_record].data
        ),
        "status": adjudication["status"],
        "taints": adjudication["taints"],
        "reason_codes": adjudication["reason_codes"],
        "layout_change_pending": adjudication[
            "layout_change_pending"
        ],
    }


def strengthened_row_guards(
    *,
    report: dict[str, Any],
    inputs: Any,
) -> dict[str, str]:
    row_guards: dict[str, str] = {}
    adjudications = report["row_adjudications"]
    pair_guards = report["pair_proof_guards"]
    for row in inputs.rows:
        bound = BASE_AUDIT.validate_row_binding(
            row,
            prefill_report=inputs.prefill_report,
            base_promoted_rows=inputs.base_promoted_rows,
            base_coverage=inputs.base_coverage,
            base_source_records=inputs.base_source_records,
            base_candidate_records=inputs.base_candidate_records,
            pk_source_records=inputs.pk_source_records,
            pk_current_records=inputs.pk_current_records,
            pk_candidate_records=inputs.pk_candidate_records,
        )
        coordinate = str(bound["coordinate"])
        adjudication = adjudications[coordinate]
        pair_guard = pair_guards[adjudication["pair_key"]]
        guard = canonical_sha256(
            row_guard_payload(
                bound=bound,
                adjudication=adjudication,
                pair_guard=pair_guard,
                inputs=inputs,
            )
        )
        adjudication["row_verification_guard_sha256"] = guard
        row_guards[coordinate] = guard
    return row_guards


def transition_summary(
    new_report: Mapping[str, Any],
) -> dict[str, Any]:
    old_report = json.loads(
        BASE_PREFILL_COVERAGE_PATH.read_text(encoding="utf-8")
    )
    BASE_AUDIT.validate_report(old_report)
    old_adjudications = old_report["row_adjudications"]
    new_adjudications = new_report["row_adjudications"]
    old_eligible = {
        coordinate
        for coordinate, row in old_adjudications.items()
        if row["status"] == "promotion_eligible"
    }
    new_eligible = {
        coordinate
        for coordinate, row in new_adjudications.items()
        if row["status"] == "promotion_eligible"
    }
    kept_eligible = old_eligible & new_eligible
    newly_eligible = new_eligible - old_eligible
    newly_blocked = old_eligible - new_eligible
    kept_blocked = set(new_adjudications) - new_eligible - newly_blocked
    require(
        len(kept_eligible) == EXPECTED_KEPT_ELIGIBLE_ROWS
        and len(newly_eligible) == EXPECTED_NEW_ELIGIBLE_ROWS
        and len(newly_blocked) == EXPECTED_NEW_BLOCKED_ROWS,
        "full-candidate status transition counts drifted",
    )
    require(
        coordinate_digest(sorted(newly_eligible))
        == EXPECTED_NEW_ELIGIBLE_COORDINATE_SHA256
        and coordinate_digest(sorted(newly_blocked))
        == EXPECTED_NEW_BLOCKED_COORDINATE_SHA256,
        "full-candidate transition coordinate universe drifted",
    )
    old_blocker_counts: Counter[str] = Counter()
    old_reason_counts: Counter[str] = Counter()
    for coordinate in newly_eligible:
        old_blocker_counts.update(old_adjudications[coordinate]["taints"])
        old_reason_counts.update(old_adjudications[coordinate]["reason_codes"])
    return {
        "kept_eligible_rows": len(kept_eligible),
        "newly_eligible_rows": len(newly_eligible),
        "newly_blocked_rows": len(newly_blocked),
        "kept_blocked_rows": len(kept_blocked),
        "kept_eligible_coordinate_sha256": coordinate_digest(
            sorted(kept_eligible)
        ),
        "newly_eligible_coordinate_sha256": coordinate_digest(
            sorted(newly_eligible)
        ),
        "newly_blocked_coordinate_sha256": coordinate_digest(
            sorted(newly_blocked)
        ),
        "kept_blocked_coordinate_sha256": coordinate_digest(
            sorted(kept_blocked)
        ),
        "newly_eligible_old_taint_counts": dict(
            sorted(old_blocker_counts.items())
        ),
        "newly_eligible_old_reason_counts": dict(
            sorted(old_reason_counts.items())
        ),
    }


def build_report(inputs: Any, metadata: Mapping[str, Any]) -> dict[str, Any]:
    report = BASE_AUDIT.build_report(inputs)
    BASE_AUDIT.validate_report(report)
    report = copy.deepcopy(report)
    report["schema"] = SCHEMA
    closure_guards = apply_pk_source_candidate_gate(
        report,
        inputs=inputs,
    )
    report["candidate_scope"] = {
        "binding": "complete final PK literal decision universe",
        "source_decision_rows": EXPECTED_PK_ROWS,
        "string_replacement_rows": EXPECTED_STRING_REPLACEMENTS,
        "source_decision_segment_count": metadata[
            "source_decision_segment_count"
        ],
        "control_gap_repairs_applied": False,
        "literal_candidate_packed_sha256": inputs.artifact_hashes[
            "pk_full_candidate_packed_sha256"
        ],
    }
    row_guards = strengthened_row_guards(report=report, inputs=inputs)
    eligible = [
        coordinate
        for coordinate, row in report["row_adjudications"].items()
        if row["status"] == "promotion_eligible"
    ]
    blocked = [
        coordinate
        for coordinate, row in report["row_adjudications"].items()
        if row["status"] == "blocked"
    ]
    require(
        len(eligible) == EXPECTED_ELIGIBLE_ROWS
        and len(blocked) == EXPECTED_BLOCKED_ROWS,
        "full-candidate adjudication counts drifted",
    )
    require(
        coordinate_digest(eligible) == EXPECTED_ELIGIBLE_COORDINATE_SHA256
        and coordinate_digest(blocked) == EXPECTED_BLOCKED_COORDINATE_SHA256,
        "full-candidate adjudication coordinate universe drifted",
    )
    report["full_candidate_transitions"] = transition_summary(report)
    report["pairing_method"][
        "candidate_binding"
    ] = "all 29,038 final PK decisions assembled before closure comparison"
    report["promotion"][
        "eligible_rows_can_be_promoted_only_by_a_separate_bound_decision_builder"
    ] = True
    report["guards"].update(
        {
            "row_verification_guards_sha256": canonical_sha256(row_guards),
            "pk_source_candidate_closure_guards_sha256": canonical_sha256(
                closure_guards
            ),
            "eligible_coordinate_universe_sha256":
            coordinate_digest(eligible),
            "blocked_coordinate_universe_sha256":
            coordinate_digest(blocked),
            "source_decision_segment_universe_sha256": metadata[
                "source_decision_segment_universe_sha256"
            ],
            "replacement_manifest_sha256": metadata[
                "replacement_manifest_sha256"
            ],
        }
    )
    report["pk_source_candidate_closure_guards"] = closure_guards
    report["distribution_policy"].update(
        {
            "contains_translated_dialogue_text": False,
            "contains_commercial_source_text": False,
        }
    )
    report["guards"].pop("report_payload_sha256", None)
    return BASE_AUDIT.seal_report(report)


def validate_report(
    report: Mapping[str, Any],
    *,
    inputs: Any,
    metadata: Mapping[str, Any],
) -> None:
    require(report.get("schema") == SCHEMA, "full-candidate schema drifted")
    require(report.get("status") == "PASS", "full-candidate audit is not PASS")
    unsealed = copy.deepcopy(dict(report))
    guards = unsealed.get("guards")
    require(isinstance(guards, dict), "full-candidate guards are absent")
    expected_payload = guards.pop("report_payload_sha256", None)
    require(
        expected_payload == canonical_sha256(unsealed),
        "full-candidate report payload hash drifted",
    )
    scope = report.get("scope")
    require(
        isinstance(scope, dict)
        and scope.get("runtime_pending_rows") == EXPECTED_EXACT_ROWS
        and scope.get("promotion_eligible_rows") == EXPECTED_ELIGIBLE_ROWS
        and scope.get("blocked_rows") == EXPECTED_BLOCKED_ROWS,
        "full-candidate scope counts drifted",
    )
    candidate_scope = report.get("candidate_scope")
    require(
        isinstance(candidate_scope, dict)
        and candidate_scope.get("source_decision_rows") == EXPECTED_PK_ROWS
        and candidate_scope.get("string_replacement_rows")
        == EXPECTED_STRING_REPLACEMENTS
        and candidate_scope.get("literal_candidate_packed_sha256")
        == EXPECTED_FULL_CANDIDATE_SHA256
        and candidate_scope.get("control_gap_repairs_applied") is False,
        "full-candidate binding drifted",
    )
    rebuilt = copy.deepcopy(dict(report))
    rebuilt["guards"].pop("report_payload_sha256", None)
    rebuilt_guards = strengthened_row_guards(
        report=rebuilt,
        inputs=inputs,
    )
    expected_closure_guards = pk_source_candidate_closure_guards(inputs)
    require(
        report["guards"]["row_verification_guards_sha256"]
        == canonical_sha256(rebuilt_guards)
        and report["pk_source_candidate_closure_guards"]
        == expected_closure_guards
        and report["guards"][
            "pk_source_candidate_closure_guards_sha256"
        ]
        == canonical_sha256(expected_closure_guards)
        and report["guards"]["source_decision_segment_universe_sha256"]
        == metadata["source_decision_segment_universe_sha256"]
        and report["guards"]["replacement_manifest_sha256"]
        == metadata["replacement_manifest_sha256"],
        "full-candidate row or input guard universe drifted",
    )
    require(
        transition_summary(report) == report["full_candidate_transitions"],
        "full-candidate transition summary drifted",
    )
    require(
        report.get("promotion", {}).get("runtime_promotion_performed") is False
        and report.get("promotion", {}).get("steam_write_performed") is False,
        "full-candidate audit attempted promotion or Steam write",
    )


def build_outputs() -> tuple[str, dict[str, Any], Any, dict[str, Any]]:
    inputs, metadata = full_candidate_inputs()
    report = build_report(inputs, metadata)
    validate_report(report, inputs=inputs, metadata=metadata)
    return canonical_json(report), report, inputs, metadata


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    require(args.write or args.check, "choose --write, --check, or both")
    first = build_outputs()
    second = build_outputs()
    require(first[0] == second[0], "two-run full-candidate report drifted")
    content, report, _inputs, _metadata = first
    if args.write:
        ENGINE.atomic_write(args.output, content)
    if args.check:
        require(
            args.output.is_file()
            and args.output.read_text(encoding="utf-8") == content,
            "tracked full-candidate report drifted",
        )
    print(
        "PASS "
        f"pending={report['scope']['runtime_pending_rows']} "
        f"eligible={report['scope']['promotion_eligible_rows']} "
        f"blocked={report['scope']['blocked_rows']} "
        "steam_write=false"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        OSError,
        ValueError,
        FullCandidateAuditError,
        ENGINE.RetranslationError,
        BASE_AUDIT.AuditError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
