#!/usr/bin/env python3
"""Promote pending PK roots with an exact verified Base/PK closure donor.

A target is eligible only when a previously verified Base or PK record has
the same source literals, final Korean literals, and local non-operand VM
structure; the donor/target call-and-jump closure is taint-free; and the
target PK source/current/final closure independently passes control,
grammar, and relative line-envelope gates.  Promotion is atomic per target
root.  The private overlay contains hashes and predicates only and stays
below ``tmp``.  Steam is read only.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_WORKSTREAM = (
    REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
)
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
OVERLAY_DIR = DIALOGUE_TMP / "decisions" / "runtime_verification_overlays"
PK_ONLY_BUILDER_PATH = (
    WORKSTREAM / "build_pk_msggame_exact_blocked_pk_only_closure_v1.py"
)
CHECKPOINT_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_pk_only_checkpoint.private.v1.jsonl"
)
CHECKPOINT_REPORT_PATH = (
    DIALOGUE_WORKSTREAM
    / "runtime_vm_integration.post_pk_only_checkpoint.source_free.v1.json"
)
CHECKPOINT_BUILDER_PATH = (
    DIALOGUE_WORKSTREAM
    / "build_runtime_vm_post_pk_only_checkpoint_v1.py"
)
PK_ONLY_AUDIT_PATH = (
    WORKSTREAM
    / "public"
    / "pk_msggame_exact_blocked_pk_only_closure_coverage.v1.json"
)
GHIDRA_CONTRACT_PATH = WORKSTREAM / "ghidra_pk_vm_contract.v1.json"
DEFAULT_AUDIT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_msggame_pending_cross_resource_exact_closure_coverage.v1.json"
)
DEFAULT_PROMOTION_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_msggame_pending_cross_resource_exact_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    OVERLAY_DIR
    / "pk_msggame_pending_cross_resource_exact_closure_verified.private.v1.jsonl"
)
LIVE_STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

AUDIT_SCHEMA = (
    "nobu16.kr.pk-msggame-pending-cross-resource-exact-closure-coverage.v1"
)
PROMOTION_SCHEMA = (
    "nobu16.kr.pk-msggame-pending-cross-resource-exact-closure-promotion.v1"
)
OVERLAY_ROW_SCHEMA = (
    "nobu16.kr.pk-msggame-pending-cross-resource-exact-closure-overlay-row.v1"
)
METHOD = "reversed_vm_cross_resource_exact_closure_analysis"

EXPECTED_CHECKPOINT_PRIVATE_SHA256 = (
    "2E1B649D0BF6AD0852A750A7C00FAEBCCCB86C7EC5CF076FFE08E5463785B4DE"
)
EXPECTED_CHECKPOINT_REPORT_SHA256 = (
    "2BE09EF37952A246B1A6ED8C139EC55DCCE5557C6D7EAD4A457762936AEBFA01"
)
EXPECTED_CHECKPOINT_BUILDER_SHA256 = (
    "8212C9339446544755A7337DAE8F58041E3C22B8968B7635620413980F6E5E99"
)
EXPECTED_PK_ONLY_AUDIT_SHA256 = (
    "47F72E6A77DFF0B8F2BDA60373298B5D05E3440D510A9A272CB036D1F4DC5248"
)
EXPECTED_GHIDRA_CONTRACT_SHA256 = (
    "21DAF83330F278484BFB2462188804947A6C457F4B072DA80D7ADFBD3D13F461"
)
EXPECTED_PENDING_ROWS = 8_752
EXPECTED_PENDING_ROOTS = 5_237
EXPECTED_LOCAL_MATCH_ROWS = 3_841
EXPECTED_LOCAL_MATCH_ROOTS = 2_990
EXPECTED_TARGET_GUARD_FAILED_ROWS = 1_289
EXPECTED_TARGET_GUARD_FAILED_ROOTS = 1_095
EXPECTED_ELIGIBLE_ROWS = 2_552
EXPECTED_ELIGIBLE_ROOTS = 1_895
EXPECTED_ELIGIBLE_COORDINATE_SHA256 = (
    "45ED0A53FCE6345E83000F2790B5A52F48C124FC019CA86CC09CB9D7BCA5178B"
)
EXPECTED_ELIGIBLE_RECORD_SHA256 = (
    "4D88405A8FFD87856D0ED453406DA5127F4BBDB820B5E9FA4EF28DD9E52E319D"
)
EXPECTED_ANALYSIS_MANIFEST_SHA256 = (
    "8806BA38A2991CE7E8BC34BCD7965400E87C629B76A051B068D0544AAFBFBBFE"
)
EXPECTED_DONOR_EXCLUSIVE = {
    "base_only": {"rows": 696, "roots": 412},
    "pk_only": {"rows": 509, "roots": 406},
    "base_and_pk": {"rows": 1_347, "roots": 1_077},
}


class CrossResourceClosureError(ValueError):
    """Raised when the exact donor or target PK proof drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CrossResourceClosureError(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PK_ONLY = load_module(
    "pk_pending_cross_resource_exact_closure_pk_only",
    PK_ONLY_BUILDER_PATH,
)
BASE_AUDIT = PK_ONLY.BASE_AUDIT
FULL_AUDIT = PK_ONLY.FULL_AUDIT
ENGINE = PK_ONLY.ENGINE


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def canonical_sha256(value: Any) -> str:
    return PK_ONLY.canonical_sha256(value)


def canonical_json(value: Any) -> str:
    return PK_ONLY.canonical_json(value)


def canonical_jsonl(rows: Iterable[Mapping[str, Any]]) -> str:
    return "".join(
        json.dumps(
            dict(row),
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
        for row in rows
    )


def read_json(path: Path) -> dict[str, Any]:
    return PK_ONLY.read_json(path)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return PK_ONLY.read_jsonl(path)


def coordinate_sort_key(value: str) -> tuple[int, int, int]:
    return BASE_AUDIT.parse_literal_coordinate(value)


def record_sort_key(value: tuple[int, int]) -> tuple[int, int]:
    return value


def coordinate_digest(values: Iterable[str]) -> str:
    coordinates = sorted(set(values), key=coordinate_sort_key)
    return sha256_bytes(
        "".join(f"{coordinate}\n" for coordinate in coordinates).encode("ascii")
    )


def record_digest(values: Iterable[tuple[int, int]]) -> str:
    records = sorted(set(values), key=record_sort_key)
    return sha256_bytes(
        "".join(f"{block}:{record}\n" for block, record in records).encode(
            "ascii"
        )
    )


def record_key(value: tuple[int, int]) -> str:
    return f"{value[0]}:{value[1]}"


def seal_report(report: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(report)
    guards = dict(result.get("guards", {}))
    guards.pop("report_payload_sha256", None)
    result["guards"] = guards
    guards["report_payload_sha256"] = canonical_sha256(result)
    result["guards"] = guards
    return result


def validate_seal(report: Mapping[str, Any]) -> None:
    expected = report.get("guards", {}).get("report_payload_sha256")
    require(isinstance(expected, str), "report payload seal is absent")
    copy_value = dict(report)
    guards = dict(copy_value["guards"])
    guards.pop("report_payload_sha256", None)
    copy_value["guards"] = guards
    require(canonical_sha256(copy_value) == expected, "report payload seal drifted")


def live_steam_hash() -> str | None:
    if not LIVE_STEAM_PK.is_file():
        return None
    return sha256_bytes(LIVE_STEAM_PK.read_bytes())


def verify_ghidra_contract() -> dict[str, Any]:
    contract_sha256 = sha256_bytes(GHIDRA_CONTRACT_PATH.read_bytes())
    require(
        contract_sha256 == EXPECTED_GHIDRA_CONTRACT_SHA256,
        f"Ghidra VM contract drifted: {contract_sha256}",
    )
    contract = read_json(GHIDRA_CONTRACT_PATH)
    BASE_AUDIT.verify_contract(contract)
    opcode = contract.get("opcode_contract", {})
    require(
        opcode.get("0143", {}).get("semantics")
        == "push_return_address_then_call_record"
        and opcode.get("014A", {}).get("semantics") == "jump_to_record"
        and opcode.get("02", {}).get("automatic_space_inserted") is False
        and opcode.get("02", {}).get("automatic_punctuation_inserted") is False,
        "Ghidra sequential append/call contract drifted",
    )
    return {
        "file_sha256": contract_sha256,
        "schema": contract["schema"],
        "program_sha256": contract["program"]["unpacked_exe_sha256"],
        "execute_record_vm": contract["functions"]["execute_record_vm"],
        "dispatch_opcode": contract["functions"]["dispatch_opcode"],
    }


def load_checkpoint() -> tuple[
    dict[tuple[str, str], dict[str, Any]],
    dict[str, Any],
]:
    private_sha256 = sha256_bytes(CHECKPOINT_PRIVATE_PATH.read_bytes())
    report_sha256 = sha256_bytes(CHECKPOINT_REPORT_PATH.read_bytes())
    builder_sha256 = sha256_bytes(CHECKPOINT_BUILDER_PATH.read_bytes())
    require(
        private_sha256 == EXPECTED_CHECKPOINT_PRIVATE_SHA256,
        f"post-PK-only private checkpoint drifted: {private_sha256}",
    )
    require(
        report_sha256 == EXPECTED_CHECKPOINT_REPORT_SHA256,
        f"post-PK-only report checkpoint drifted: {report_sha256}",
    )
    if EXPECTED_CHECKPOINT_BUILDER_SHA256:
        require(
            builder_sha256 == EXPECTED_CHECKPOINT_BUILDER_SHA256,
            f"post-PK-only checkpoint builder drifted: {builder_sha256}",
        )
    report = read_json(CHECKPOINT_REPORT_PATH)
    require(
        report.get("schema")
        == "nobu16.kr.pc-dialogue-runtime-vm-integration.v1"
        and report.get("status") == "PASS"
        and report.get("result", {}).get(
            "private_integrated_decision_sha256"
        )
        == private_sha256
        and report.get("result", {}).get("runtime_review_pending")
        == EXPECTED_PENDING_ROWS
        and report.get("promotions", {}).get("pk_msggame", {}).get(
            "promotion_count"
        )
        == 11_931
        and report.get("promotions", {}).get("pk_msggame", {}).get(
            "pk_only_layer_included"
        )
        is True
        and report.get("steam_write_performed") is False,
        "post-PK-only checkpoint contract drifted",
    )
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    for row in read_jsonl(CHECKPOINT_PRIVATE_PATH):
        resource = str(row.get("resource"))
        coordinate = str(row.get("coordinate"))
        key = (resource, coordinate)
        require(
            resource in {"base_msggame", "pk_msggame"} and key not in rows,
            f"invalid or duplicate checkpoint row: {key}",
        )
        rows[key] = row
    require(len(rows) == 52_803, f"checkpoint row universe drifted: {len(rows)}")
    pending = [
        coordinate
        for (resource, coordinate), row in rows.items()
        if resource == "pk_msggame" and row.get("runtime_review") == "pending"
    ]
    pending_roots = {
        BASE_AUDIT.parse_literal_coordinate(coordinate)[:2]
        for coordinate in pending
    }
    require(
        len(pending) == EXPECTED_PENDING_ROWS
        and len(pending_roots) == EXPECTED_PENDING_ROOTS,
        "checkpoint pending universe drifted",
    )
    return rows, {
        "private_sha256": private_sha256,
        "report_file_sha256": report_sha256,
        "report_payload_sha256": canonical_sha256(report),
        "builder_sha256": builder_sha256,
        "pending_rows": len(pending),
        "pending_roots": len(pending_roots),
    }


def local_signature(
    root: tuple[int, int],
    *,
    source_records: Mapping[tuple[int, int], Any],
    candidate_records: Mapping[tuple[int, int], Any],
) -> str:
    source = source_records.get(root)
    candidate = candidate_records.get(root)
    require(
        source is not None and candidate is not None,
        f"signature record is absent: {root}",
    )
    components = [
        BASE_AUDIT.structural_component(component)
        for component in BASE_AUDIT.decode_record(candidate)
    ]
    return canonical_sha256(
        {
            "components": components,
            "source_literals": [
                literal.text
                for literal in BASE_AUDIT.parse_record_literals(source)
            ],
            "candidate_literals": [
                literal.text
                for literal in BASE_AUDIT.parse_record_literals(candidate)
            ],
        }
    )


def donor_witnesses(
    checkpoint_rows: Mapping[tuple[str, str], Mapping[str, Any]],
) -> dict[
    str,
    dict[tuple[int, int], dict[str, dict[str, Any]]],
]:
    result: dict[
        str,
        dict[tuple[int, int], dict[str, dict[str, Any]]],
    ] = {"base_msggame": {}, "pk_msggame": {}}
    for (resource, coordinate), row in checkpoint_rows.items():
        if row.get("runtime_review") != "verified":
            continue
        verification = row.get("runtime_vm_verification")
        require(
            isinstance(verification, dict)
            and isinstance(verification.get("method"), str),
            f"verified donor has no VM evidence: {resource}:{coordinate}",
        )
        root = BASE_AUDIT.parse_literal_coordinate(coordinate)[:2]
        method = str(verification["method"])
        by_method = result[resource].setdefault(root, {})
        previous = by_method.get(method)
        witness = {
            "coordinate": coordinate,
            "integrated_row_sha256": canonical_sha256(row),
            "runtime_vm_verification_sha256": canonical_sha256(verification),
        }
        if previous is None or coordinate_sort_key(coordinate) < coordinate_sort_key(
            str(previous["coordinate"])
        ):
            by_method[method] = witness
    return result


def target_guard_passes(guard: Mapping[str, Any]) -> bool:
    return (
        guard.get("failure_codes") == []
        and guard.get("source_current_control_equal") is True
        and guard.get("source_final_control_equal") is True
        and guard.get("current_final_control_equal") is True
        and guard.get("final_line_envelope_not_above_current") is True
        and guard.get("hard_grammar_risk_absent") is True
    )


def proof_universe(
    *,
    context: Mapping[str, Any],
    checkpoint_rows: Mapping[tuple[str, str], Mapping[str, Any]],
) -> dict[str, Any]:
    inputs = context["inputs"]
    witnesses = donor_witnesses(checkpoint_rows)
    signature_index: defaultdict[
        str,
        dict[str, list[tuple[int, int]]],
    ] = defaultdict(lambda: {"base_msggame": [], "pk_msggame": []})
    for resource, by_root in witnesses.items():
        source_records = (
            inputs.base_source_records
            if resource == "base_msggame"
            else inputs.pk_source_records
        )
        candidate_records = (
            inputs.base_candidate_records
            if resource == "base_msggame"
            else inputs.pk_candidate_records
        )
        for root in sorted(by_root):
            signature_index[
                local_signature(
                    root,
                    source_records=source_records,
                    candidate_records=candidate_records,
                )
            ][resource].append(root)

    pending_by_root: defaultdict[tuple[int, int], list[str]] = defaultdict(list)
    for (resource, coordinate), row in checkpoint_rows.items():
        if resource == "pk_msggame" and row.get("runtime_review") == "pending":
            pending_by_root[
                BASE_AUDIT.parse_literal_coordinate(coordinate)[:2]
            ].append(coordinate)
    for coordinates in pending_by_root.values():
        coordinates.sort(key=coordinate_sort_key)

    local_matches: list[dict[str, Any]] = []
    target_guard_failures: list[dict[str, Any]] = []
    eligible: list[dict[str, Any]] = []
    pair_cache: dict[
        tuple[str, tuple[int, int], tuple[int, int]],
        Any,
    ] = {}
    for target_root in sorted(pending_by_root):
        signature = local_signature(
            target_root,
            source_records=inputs.pk_source_records,
            candidate_records=inputs.pk_candidate_records,
        )
        bucket = signature_index.get(signature)
        if not bucket:
            continue
        donors: list[dict[str, Any]] = []
        for resource in ("base_msggame", "pk_msggame"):
            donor_roots = bucket[resource]
            for method in sorted(
                {
                    method
                    for donor_root in donor_roots
                    for method in witnesses[resource][donor_root]
                }
            ):
                representative: dict[str, Any] | None = None
                for donor_root in donor_roots:
                    cache_key = (resource, donor_root, target_root)
                    pair = pair_cache.get(cache_key)
                    if pair is None:
                        donor_source_records = (
                            inputs.base_source_records
                            if resource == "base_msggame"
                            else inputs.pk_source_records
                        )
                        donor_candidate_records = (
                            inputs.base_candidate_records
                            if resource == "base_msggame"
                            else inputs.pk_candidate_records
                        )
                        pair = BASE_AUDIT.compare_record_pair(
                            donor_root,
                            target_root,
                            base_source_records=donor_source_records,
                            base_candidate_records=donor_candidate_records,
                            pk_source_records=inputs.pk_source_records,
                            pk_candidate_records=inputs.pk_candidate_records,
                        )
                        pair_cache[cache_key] = pair
                    if pair.taints or method not in witnesses[resource][donor_root]:
                        continue
                    witness = witnesses[resource][donor_root][method]
                    representative = {
                        "resource": resource,
                        "method": method,
                        "record": list(donor_root),
                        "pair_proof_sha256": pair.proof_sha256,
                        "visited_pair_count": len(pair.visited_pairs),
                        "0143_occurrences": pair.call_occurrences,
                        "014a_occurrences": pair.jump_occurrences,
                        "donor_witness_coordinate": witness["coordinate"],
                        "donor_integrated_row_sha256": witness[
                            "integrated_row_sha256"
                        ],
                        "donor_runtime_vm_verification_sha256": witness[
                            "runtime_vm_verification_sha256"
                        ],
                    }
                    break
                if representative is not None:
                    donors.append(representative)
        if not donors:
            continue
        members = pending_by_root[target_root]
        guard = PK_ONLY.closure_guard(
            target_root,
            inputs=inputs,
            decisions_by_record=context["decisions_by_record"],
        )
        analysis_entry = {
            "root": list(target_root),
            "member_coordinates": members,
            "donors": donors,
            "pk_closure_proof_sha256": guard["proof_sha256"],
        }
        local_matches.append(analysis_entry)
        if not target_guard_passes(guard):
            target_guard_failures.append(
                {
                    **analysis_entry,
                    "failure_codes": guard["failure_codes"],
                    "grammar_risk_keys": guard["grammar_risk_keys"],
                }
            )
            continue
        eligible.append(
            {
                **analysis_entry,
                "root_member_pending_coordinate_sha256": coordinate_digest(
                    members
                ),
                "pk_target_guard": {
                    "source_current_control_equal": True,
                    "source_final_control_equal": True,
                    "current_final_control_equal": True,
                    "final_line_envelope_not_above_current": True,
                    "hard_grammar_risk_absent": True,
                    "failure_codes": [],
                },
            }
        )

    local_rows = sum(len(entry["member_coordinates"]) for entry in local_matches)
    failed_rows = sum(
        len(entry["member_coordinates"]) for entry in target_guard_failures
    )
    eligible_rows = [
        coordinate
        for entry in eligible
        for coordinate in entry["member_coordinates"]
    ]
    eligible_roots = {
        tuple(entry["root"])
        for entry in eligible
    }
    require(
        len(local_matches) == EXPECTED_LOCAL_MATCH_ROOTS
        and local_rows == EXPECTED_LOCAL_MATCH_ROWS,
        "local exact-donor closure funnel drifted: "
        f"roots={len(local_matches)} rows={local_rows}",
    )
    require(
        len(target_guard_failures) == EXPECTED_TARGET_GUARD_FAILED_ROOTS
        and failed_rows == EXPECTED_TARGET_GUARD_FAILED_ROWS,
        "target PK guard failure funnel drifted: "
        f"roots={len(target_guard_failures)} rows={failed_rows}",
    )
    require(
        len(eligible) == EXPECTED_ELIGIBLE_ROOTS
        and len(eligible_rows) == EXPECTED_ELIGIBLE_ROWS
        and coordinate_digest(eligible_rows)
        == EXPECTED_ELIGIBLE_COORDINATE_SHA256
        and record_digest(eligible_roots) == EXPECTED_ELIGIBLE_RECORD_SHA256,
        "eligible cross-resource closure universe drifted",
    )

    # Reproduce the independent analysis manifest before adding stronger
    # donor witness bindings to the shipped proof.
    analysis_manifest = [
        {
            "root": entry["root"],
            "member_coordinates": entry["member_coordinates"],
            "donors": [
                {
                    "resource": donor["resource"],
                    "method": donor["method"],
                    "record": donor["record"],
                    "pair_proof_sha256": donor["pair_proof_sha256"],
                }
                for donor in entry["donors"]
            ],
            "pk_closure_proof_sha256": entry["pk_closure_proof_sha256"],
        }
        for entry in eligible
    ]
    require(
        canonical_sha256(analysis_manifest)
        == EXPECTED_ANALYSIS_MANIFEST_SHA256,
        "independent analysis manifest was not reproduced",
    )

    exclusive = {
        "base_only": {"rows": 0, "roots": 0},
        "pk_only": {"rows": 0, "roots": 0},
        "base_and_pk": {"rows": 0, "roots": 0},
    }
    for entry in eligible:
        resources = {donor["resource"] for donor in entry["donors"]}
        category = (
            "base_and_pk"
            if resources == {"base_msggame", "pk_msggame"}
            else "base_only"
            if resources == {"base_msggame"}
            else "pk_only"
        )
        exclusive[category]["roots"] += 1
        exclusive[category]["rows"] += len(entry["member_coordinates"])
    require(
        exclusive == EXPECTED_DONOR_EXCLUSIVE,
        f"exclusive donor distribution drifted: {exclusive}",
    )
    return {
        "eligible": eligible,
        "eligible_coordinates": sorted(
            eligible_rows,
            key=coordinate_sort_key,
        ),
        "local_match_rows": local_rows,
        "local_match_roots": len(local_matches),
        "target_guard_failed_rows": failed_rows,
        "target_guard_failed_roots": len(target_guard_failures),
        "analysis_manifest_sha256": canonical_sha256(analysis_manifest),
        "proof_manifest_sha256": canonical_sha256(eligible),
        "donor_exclusive": exclusive,
    }


def build_audit(
    *,
    context: Mapping[str, Any],
    checkpoint_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    checkpoint_metadata: Mapping[str, Any],
    ghidra_metadata: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    proof = proof_universe(
        context=context,
        checkpoint_rows=checkpoint_rows,
    )
    pk_only_audit_sha256 = sha256_bytes(PK_ONLY_AUDIT_PATH.read_bytes())
    require(
        pk_only_audit_sha256 == EXPECTED_PK_ONLY_AUDIT_SHA256,
        "PK-only audit binding drifted",
    )
    pk_only_audit = read_json(PK_ONLY_AUDIT_PATH)
    exact_manual = {
        coordinate
        for coordinate, adjudication in pk_only_audit[
            "row_adjudications"
        ].items()
        if adjudication["status"] == "manual_review_required"
    }
    require(
        not (set(proof["eligible_coordinates"]) & exact_manual),
        "cross-resource closure overlaps exact manual-review rows",
    )
    root_proofs = {
        record_key(tuple(entry["root"])): entry
        for entry in proof["eligible"]
    }
    report = {
        "schema": AUDIT_SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "scope": {
            "predecessor_pending_rows": EXPECTED_PENDING_ROWS,
            "predecessor_pending_roots": EXPECTED_PENDING_ROOTS,
            "local_exact_closure_match_rows": proof["local_match_rows"],
            "local_exact_closure_match_roots": proof["local_match_roots"],
            "target_pk_guard_failed_rows": proof[
                "target_guard_failed_rows"
            ],
            "target_pk_guard_failed_roots": proof[
                "target_guard_failed_roots"
            ],
            "promotion_eligible_rows": len(proof["eligible_coordinates"]),
            "promotion_eligible_roots": len(root_proofs),
            "manual_review_remaining_rows": (
                EXPECTED_PENDING_ROWS - len(proof["eligible_coordinates"])
            ),
            "per_row_game_playback_required": 0,
        },
        "proof_policy": {
            "donor_must_be_predecessor_runtime_verified": True,
            "donor_and_target_local_source_literal_tuple_equal": True,
            "donor_and_target_local_final_literal_tuple_equal": True,
            "donor_and_target_local_nonoperand_vm_sequence_equal": True,
            "actual_0143_014a_closure_pair_must_be_taint_free": True,
            "target_source_current_final_control_closure_equal": True,
            "target_final_line_envelope_not_above_current": True,
            "target_hard_grammar_risk_absent": True,
            "target_root_pending_members_promoted_atomically": True,
            "base_runtime_state_inherited": False,
            "absolute_msggame_width_gate_used": False,
            "pk_msgev_912px_rule_used": False,
        },
        "donor_exclusive": proof["donor_exclusive"],
        "guards": {
            "checkpoint_private_sha256": checkpoint_metadata[
                "private_sha256"
            ],
            "checkpoint_report_file_sha256": checkpoint_metadata[
                "report_file_sha256"
            ],
            "checkpoint_report_payload_sha256": checkpoint_metadata[
                "report_payload_sha256"
            ],
            "checkpoint_builder_sha256": checkpoint_metadata[
                "builder_sha256"
            ],
            "pk_only_audit_file_sha256": pk_only_audit_sha256,
            "full_candidate_packed_sha256": context["full_report"][
                "candidate_scope"
            ]["literal_candidate_packed_sha256"],
            "source_decision_segment_universe_sha256": context[
                "source_metadata"
            ]["source_decision_segment_universe_sha256"],
            "ghidra_contract_file_sha256": ghidra_metadata["file_sha256"],
            "eligible_coordinate_universe_sha256": coordinate_digest(
                proof["eligible_coordinates"]
            ),
            "eligible_record_universe_sha256": record_digest(
                tuple(tuple(entry["root"]) for entry in proof["eligible"])
            ),
            "independent_analysis_manifest_sha256": proof[
                "analysis_manifest_sha256"
            ],
            "proof_manifest_sha256": proof["proof_manifest_sha256"],
            "root_proof_universe_sha256": canonical_sha256(root_proofs),
        },
        "ghidra_vm_contract": ghidra_metadata,
        "root_proofs": root_proofs,
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_translated_dialogue_text": False,
            "contains_complete_game_resource": False,
            "contains_only_coordinates_hashes_counts_and_predicates": True,
        },
        "promotion": {
            "runtime_promotion_performed": False,
            "steam_write_performed": False,
        },
    }
    return seal_report(report), proof


def validate_audit(report: Mapping[str, Any]) -> None:
    validate_seal(report)
    require(
        report.get("schema") == AUDIT_SCHEMA
        and report.get("status") == "PASS"
        and report.get("scope", {}).get("promotion_eligible_rows")
        == EXPECTED_ELIGIBLE_ROWS
        and report.get("scope", {}).get("promotion_eligible_roots")
        == EXPECTED_ELIGIBLE_ROOTS
        and report.get("guards", {}).get(
            "eligible_coordinate_universe_sha256"
        )
        == EXPECTED_ELIGIBLE_COORDINATE_SHA256
        and report.get("guards", {}).get("eligible_record_universe_sha256")
        == EXPECTED_ELIGIBLE_RECORD_SHA256,
        "cross-resource closure audit counts or guards drifted",
    )
    require(
        report.get("promotion", {}).get("runtime_promotion_performed") is False
        and report.get("promotion", {}).get("steam_write_performed") is False,
        "audit attempted a promotion or Steam write",
    )


def overlay_row(
    coordinate: str,
    *,
    entry: Mapping[str, Any],
    checkpoint_row: Mapping[str, Any],
    audit: Mapping[str, Any],
    audit_file_sha256: str,
    inputs: Any,
) -> dict[str, Any]:
    block_id, record_id, literal_id = (
        BASE_AUDIT.parse_literal_coordinate(coordinate)
    )
    literals = BASE_AUDIT.parse_record_literals(
        inputs.pk_candidate_records[(block_id, record_id)]
    )
    require(literal_id < len(literals), f"candidate literal is absent: {coordinate}")
    translation_sha256 = sha256_bytes(
        literals[literal_id].text.encode("utf-16-le")
    )
    require(
        checkpoint_row.get("runtime_review") == "pending"
        and checkpoint_row.get("scope_classification")
        == "runtime_fragment_pending"
        and checkpoint_row.get("semantic_review") == "approved"
        and sha256_bytes(
            str(checkpoint_row["translation"]).encode("utf-16-le")
        )
        == translation_sha256,
        f"checkpoint target row drifted: {coordinate}",
    )
    row_guard = {
        "coordinate": coordinate,
        "root": entry["root"],
        "root_member_pending_coordinate_sha256": entry[
            "root_member_pending_coordinate_sha256"
        ],
        "translation_utf16le_sha256": translation_sha256,
        "checkpoint_row_sha256": canonical_sha256(checkpoint_row),
        "pk_closure_proof_sha256": entry["pk_closure_proof_sha256"],
        "donor_proof_sha256": canonical_sha256(entry["donors"]),
        "audit_file_sha256": audit_file_sha256,
        "audit_payload_sha256": audit["guards"]["report_payload_sha256"],
    }
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
        "translation_utf16le_sha256": translation_sha256,
        "layout_review_binding": {
            "status": checkpoint_row["layout_review"],
        },
        "layout_transition": {
            "from": checkpoint_row["layout_review"],
            "to": "runtime_verified",
        },
        "predecessor_integrated_binding": {
            "row_sha256": canonical_sha256(checkpoint_row),
            "private_integrated_decision_sha256": audit["guards"][
                "checkpoint_private_sha256"
            ],
            "source_free_report_file_sha256": audit["guards"][
                "checkpoint_report_file_sha256"
            ],
            "integrated_builder_sha256": audit["guards"][
                "checkpoint_builder_sha256"
            ],
        },
        "cross_resource_closure_binding": {
            "root": entry["root"],
            "root_member_pending_coordinate_sha256": entry[
                "root_member_pending_coordinate_sha256"
            ],
            "donors": entry["donors"],
            "pk_closure_proof_sha256": entry["pk_closure_proof_sha256"],
            "pk_target_guard": entry["pk_target_guard"],
            "audit_report_file_sha256": audit_file_sha256,
            "audit_report_payload_sha256": audit["guards"][
                "report_payload_sha256"
            ],
            "row_verification_guard_sha256": canonical_sha256(row_guard),
        },
        "base_runtime_proof_inherited": False,
        "per_row_game_playback_required": False,
    }


def build_overlay_rows(
    *,
    proof: Mapping[str, Any],
    checkpoint_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    audit: Mapping[str, Any],
    audit_file_sha256: str,
    inputs: Any,
) -> list[dict[str, Any]]:
    entry_by_coordinate = {
        coordinate: entry
        for entry in proof["eligible"]
        for coordinate in entry["member_coordinates"]
    }
    require(
        len(entry_by_coordinate) == EXPECTED_ELIGIBLE_ROWS
        and coordinate_digest(entry_by_coordinate)
        == EXPECTED_ELIGIBLE_COORDINATE_SHA256,
        "overlay eligible coordinate universe drifted",
    )
    return [
        overlay_row(
            coordinate,
            entry=entry_by_coordinate[coordinate],
            checkpoint_row=checkpoint_rows[("pk_msggame", coordinate)],
            audit=audit,
            audit_file_sha256=audit_file_sha256,
            inputs=inputs,
        )
        for coordinate in sorted(entry_by_coordinate, key=coordinate_sort_key)
    ]


def build_promotion_report(
    *,
    audit: Mapping[str, Any],
    audit_file_sha256: str,
    private_content: str,
) -> dict[str, Any]:
    report = {
        "schema": PROMOTION_SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "input": {
            "predecessor_pending_rows": EXPECTED_PENDING_ROWS,
            "promotion_eligible_rows": EXPECTED_ELIGIBLE_ROWS,
            "promotion_eligible_roots": EXPECTED_ELIGIBLE_ROOTS,
            "full_candidate_packed_sha256": audit["guards"][
                "full_candidate_packed_sha256"
            ],
        },
        "result": {
            "private_overlay_rows": EXPECTED_ELIGIBLE_ROWS,
            "private_overlay_sha256": sha256_bytes(
                private_content.encode("utf-8")
            ),
            "eligible_coordinate_universe_sha256": audit["guards"][
                "eligible_coordinate_universe_sha256"
            ],
            "eligible_record_universe_sha256": audit["guards"][
                "eligible_record_universe_sha256"
            ],
            "remaining_rows": EXPECTED_PENDING_ROWS - EXPECTED_ELIGIBLE_ROWS,
            "translation_body_copied": False,
        },
        "evidence": {
            "audit_report_file_sha256": audit_file_sha256,
            "audit_report_payload_sha256": audit["guards"][
                "report_payload_sha256"
            ],
            "proof_manifest_sha256": audit["guards"][
                "proof_manifest_sha256"
            ],
            "checkpoint_private_sha256": audit["guards"][
                "checkpoint_private_sha256"
            ],
            "ghidra_contract_file_sha256": audit["guards"][
                "ghidra_contract_file_sha256"
            ],
        },
        "exclusion_policy": {
            "target_pk_guard_failed_rows_included": 0,
            "exact_manual_review_rows_included": 0,
            "normalized_or_partial_match_rows_included": 0,
            "unsafe_rows_included": 0,
            "base_runtime_proof_inherited": False,
        },
        "distribution_policy": {
            "tracked_reports_contain_commercial_source_text": False,
            "tracked_reports_contain_translated_dialogue_text": False,
            "private_overlay_contains_commercial_source_text": False,
            "private_overlay_contains_translated_dialogue_text": False,
            "private_overlay_stays_below_tmp": True,
        },
        "steam_write_performed": False,
        "guards": {},
    }
    return seal_report(report)


def build_outputs() -> tuple[
    str,
    str,
    str,
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    steam_before = live_steam_hash()
    ghidra_metadata = verify_ghidra_contract()
    context = PK_ONLY.input_context()
    checkpoint_rows, checkpoint_metadata = load_checkpoint()
    audit, proof = build_audit(
        context=context,
        checkpoint_rows=checkpoint_rows,
        checkpoint_metadata=checkpoint_metadata,
        ghidra_metadata=ghidra_metadata,
    )
    validate_audit(audit)
    audit_content = canonical_json(audit)
    audit_file_sha256 = sha256_bytes(audit_content.encode("utf-8"))
    overlay_rows = build_overlay_rows(
        proof=proof,
        checkpoint_rows=checkpoint_rows,
        audit=audit,
        audit_file_sha256=audit_file_sha256,
        inputs=context["inputs"],
    )
    private_content = canonical_jsonl(overlay_rows)
    promotion = build_promotion_report(
        audit=audit,
        audit_file_sha256=audit_file_sha256,
        private_content=private_content,
    )
    promotion_content = canonical_json(promotion)
    steam_after = live_steam_hash()
    require(
        steam_after == steam_before,
        "Steam PK msggame changed during cross-resource closure build",
    )
    return (
        audit_content,
        private_content,
        promotion_content,
        audit,
        promotion,
        {
            "context": context,
            "checkpoint_rows": checkpoint_rows,
            "checkpoint_metadata": checkpoint_metadata,
            "proof": proof,
            "audit_file_sha256": audit_file_sha256,
            "steam_hash_before": steam_before,
            "steam_hash_after": steam_after,
        },
    )


def require_private_output_scope(path: Path) -> None:
    root = DIALOGUE_TMP.resolve(strict=False)
    resolved = path.resolve(strict=False)
    require(
        resolved != root and root in resolved.parents,
        f"private output must stay below {root}: {resolved}",
    )


def require_public_output_scope(path: Path) -> None:
    root = WORKSTREAM.resolve(strict=False)
    resolved = path.resolve(strict=False)
    require(
        resolved != root and root in resolved.parents,
        f"public output must stay below {root}: {resolved}",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--audit-output",
        type=Path,
        default=DEFAULT_AUDIT_OUTPUT,
    )
    parser.add_argument(
        "--private-output",
        type=Path,
        default=DEFAULT_PRIVATE_OUTPUT,
    )
    parser.add_argument(
        "--promotion-output",
        type=Path,
        default=DEFAULT_PROMOTION_OUTPUT,
    )
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    require(args.write or args.check, "choose --write, --check, or both")
    require_private_output_scope(args.private_output)
    require_public_output_scope(args.audit_output)
    require_public_output_scope(args.promotion_output)
    first = build_outputs()
    second = build_outputs()
    require(first[0] == second[0], "two-run audit drifted")
    require(first[1] == second[1], "two-run overlay drifted")
    require(first[2] == second[2], "two-run promotion drifted")
    (
        audit_content,
        private_content,
        promotion_content,
        audit,
        _promotion,
        _context,
    ) = first
    if args.write:
        ENGINE.atomic_write(args.audit_output, audit_content)
        ENGINE.atomic_write(args.private_output, private_content)
        ENGINE.atomic_write(args.promotion_output, promotion_content)
    if args.check:
        require(
            args.audit_output.is_file()
            and args.audit_output.read_text(encoding="utf-8") == audit_content,
            "tracked cross-resource audit drifted",
        )
        require(
            args.private_output.is_file()
            and args.private_output.read_text(encoding="utf-8") == private_content,
            "private cross-resource overlay drifted",
        )
        require(
            args.promotion_output.is_file()
            and args.promotion_output.read_text(encoding="utf-8")
            == promotion_content,
            "tracked cross-resource promotion drifted",
        )
    validate_audit(audit)
    print(
        "PASS "
        f"promoted={audit['scope']['promotion_eligible_rows']} "
        f"roots={audit['scope']['promotion_eligible_roots']} "
        f"remaining={audit['scope']['manual_review_remaining_rows']} "
        "steam_write=false"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        OSError,
        ValueError,
        CrossResourceClosureError,
        PK_ONLY.PkOnlyClosureError,
        FULL_AUDIT.FullCandidateAuditError,
        BASE_AUDIT.AuditError,
        ENGINE.RetranslationError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
