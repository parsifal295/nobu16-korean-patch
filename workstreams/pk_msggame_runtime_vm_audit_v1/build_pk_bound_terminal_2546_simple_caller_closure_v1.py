#!/usr/bin/env python3
"""Integrate the frozen PK 2546 simple-caller retranslation proposal.

The translation-bearing proposal, decision delta, and evidence remain below
``tmp``.  Only source-free coverage and promotion reports are tracked.  The
live Steam installation is read-only.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
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
PROPOSAL_BUILDER_PATH = (
    WORKSTREAM
    / "build_pk_bound_terminal_2546_simple_caller_retranslation_proposal_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP / "runtime_vm_integrated.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    DIALOGUE_WORKSTREAM / "runtime_vm_integration.source_free.v1.json"
)
PROPOSAL_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "family2546_simple_caller_retranslation_proposal.private.v1.json"
)
PROPOSAL_PUBLIC_PATH = (
    WORKSTREAM
    / "public"
    / "pk_bound_terminal_2546_simple_caller_retranslation_proposal.v1.json"
)
LEDGER_PATH = DIALOGUE_TMP / "family2546_full_ledger.private.v1.json"

DEFAULT_AUDIT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_bound_terminal_2546_simple_caller_closure_coverage.v1.json"
)
DEFAULT_PROMOTION_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_bound_terminal_2546_simple_caller_closure_promotion.v1.json"
)
DEFAULT_DECISION_OUTPUT = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / (
        "pk_bound_terminal_2546_simple_caller_closure_"
        "integrated_decisions.private.v1.jsonl"
    )
)
DEFAULT_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / (
        "pk_bound_terminal_2546_simple_caller_closure_"
        "evidence.private.v1.jsonl"
    )
)

AUDIT_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-2546-simple-caller-closure-coverage.v1"
)
PROMOTION_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-2546-simple-caller-closure-promotion.v1"
)
EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-2546-simple-caller-closure-evidence-row.v1"
)
OVERRIDE_SCHEMA = (
    "nobu16.kr.pk-bound-terminal-2546-simple-caller-exact-override.v1"
)
METHOD = (
    "reversed_vm_pk_bound_terminal_2546_"
    "simple_caller_retranslation_closure"
)
UPDATE_ACTION_FIELD = "bound_terminal_2546_simple_caller_update_action"
OVERRIDE_FIELD = (
    "bound_terminal_2546_simple_caller_exact_override_evidence"
)

EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "838D162126925ECF706577688D35570853CDA68226AF3C8FFB7FE14C3943D072"
)
EXPECTED_PROPOSAL_PRIVATE_SHA256 = (
    "EE9978A8D2B6E432618A0B5A70286C8B2E7EC6CC2AA6671AD77B02D002F50DBB"
)
EXPECTED_PROPOSAL_PUBLIC_SHA256 = (
    "712A4D767F2E8C6F8E82FCADF4AA2C827AA5AE7CF5948E328D455EDB77161A2E"
)
EXPECTED_LEDGER_SHA256 = (
    "90987EC88A5AA06DA1BAB681E84D59ECD1E8090EE1AFCD472A0A5D646C3399EE"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E"
)
EXPECTED_CANDIDATE_SHA256 = (
    "C59CA74634E8A1FB0BBBFA3FE3A324AFC0ED06FDF7D707444116D5862A6C2C75"
)
EXPECTED_ROWS = 52_803
EXPECTED_PENDING_BEFORE = 8_213
EXPECTED_PENDING_AFTER = 8_190
EXPECTED_OVERRIDE_ROWS = 17
EXPECTED_PROMOTION_ROWS = 23
EXPECTED_PROMOTION_ROOTS = 9
EXPECTED_RENEWAL_ROWS = 5
EXPECTED_RENEWAL_ROOTS = 3
EXPECTED_DECISION_ROWS = 28
EXPECTED_ASSEMBLIES = 63
EXPECTED_ROOT_SHA256 = (
    "DAF81B7CE6F04C328884A6344380AA51FE16DDDC42EBC41D0A9FAB3B0843F74D"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "0EA72CCAB19602D79E8F1D04690D7F3DD39E02BF47267CC91A73A780EEA1FBE9"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "33E1CB0D48FA401F556CE8C2824D5EE83877007B0B3271537CCFC5496923DA63"
)
EXPECTED_RENEWAL_ROOT_SHA256 = (
    "1547BCB77C532661058ACB64B496E448FB76F4598DA78ADE9A0FE666B5532F38"
)
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "196FC4887A53E1F01647B2A47D6BB650D5CA48B4962EA83A9639A39D4DAD65EF"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "8F75484BA98CEECCF591CBEF8FC0174587E497F8734EECFA3626A7E4A591A9FD"
)
EXPECTED_OVERRIDE_MAP_SHA256 = (
    "B12AD98F0AF23266F8AD057A1256F2558B810451EE96D4668FA06A1997408704"
)
EXPECTED_TERMINAL_COORDINATE_SHA256 = (
    "DD975EDD56BA114A8BB46274BF5B141E18A3A28C0153A769F586059E6C9F810A"
)
EXPECTED_ASSEMBLY_MANIFEST_SHA256 = (
    "801CA6616376313B8F2D49F58053C9131F061FE8DD270BE63C17A52FAE62E704"
)
EXPECTED_COMPONENT_MANIFEST_SHA256 = (
    "34DF9DD1AB7F311201B898C029E0F5B36F7F59CA189049078B3311C757CDF052"
)
EXPECTED_PROPOSAL_DECISION_MANIFEST_SHA256 = (
    "CE49C707616F79165C5B49A54A41E0FD4FE1456EBB949DD41F4053DDA6ECBFF8"
)
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 9,
    "translation_override_and_runtime_promotion": 14,
    "translation_override_and_verification_renewal": 3,
    "verification_renewal": 2,
}
EXPECTED_ACTION_COORDINATE_SHA256 = {
    "runtime_promotion":
    "59FC7D95C829E0BC68F4387DB60E364F544930C0E889FDAF0C23A2CE8E6CF8AE",
    "translation_override_and_runtime_promotion":
    "145F143D08B26C2845987E37195FF4FF9C31665E509C9F9A81FE3007E6A8EF62",
    "translation_override_and_verification_renewal":
    "0F7FE250ADBCDEB7A13737F4FD603A979433CB2B0D7C07A064A5F0C735E16952",
    "verification_renewal":
    "81F79F6A6BFB36FF5FAF27A58138AA41D42ABFD5D5738900992E1880B53A89FC",
}

# Frozen after the first deterministic write.
EXPECTED_AUDIT_FILE_SHA256: str | None = (
    "F68983910EFD2EAFBC869C5AC3D7C7E86C11812410ECCFDFD1CC2E6D75A2EE9E"
)
EXPECTED_PROMOTION_FILE_SHA256: str | None = (
    "54F73AE0CAAB57088D593812147BDBC92DE4C445AA5B5FFB49C0C658F8F70938"
)
EXPECTED_DECISION_FILE_SHA256: str | None = (
    "FB2EFFAC4D8FFD6C7A77D09A0D51F9C9252A878371381E9CA0D1F35F89ACF90B"
)
EXPECTED_EVIDENCE_FILE_SHA256: str | None = (
    "36F5EE8A90BE6EE0FE54EAEC6556B9AB60243A5440420650265524F8DA42F99A"
)


class ClosureError(ValueError):
    """Raised when a frozen simple-caller closure contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ClosureError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(
        spec is not None and spec.loader is not None,
        f"cannot import {path}",
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PROPOSAL = load_module(
    PROPOSAL_BUILDER_PATH,
    "pk_bound_terminal_2546_simple_caller_closure_proposal_helpers_v1",
)
FAMILY = PROPOSAL.FAMILY
BASE_AUDIT = PROPOSAL.BASE_AUDIT
ENGINE = PROPOSAL.ENGINE
HONORIFIC = PROPOSAL.HONORIFIC
LIVE_STEAM_BASE = FAMILY.LIVE_STEAM_BASE
LIVE_STEAM_PK = FAMILY.LIVE_STEAM_PK


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> str:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    )


def canonical_jsonl(rows: Iterable[Mapping[str, Any]]) -> str:
    return "".join(canonical_json(row) for row in rows)


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )


def parse_coordinate(value: str) -> tuple[int, int, int]:
    return FAMILY.parse_coordinate(value)


def coordinate_digest(values: Iterable[str]) -> str:
    return FAMILY.coordinate_digest(values)


def record_digest(values: Iterable[tuple[int, int]]) -> str:
    return FAMILY.record_digest(values)


def row_sort_key(row: Mapping[str, Any]) -> tuple[int, int, int, int]:
    return FAMILY.row_sort_key(row)


def load_predecessor() -> tuple[
    dict[tuple[str, str], dict[str, Any]],
    dict[str, Any],
]:
    require(
        sha256_file(PREDECESSOR_PRIVATE_PATH)
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256,
        "BF7B predecessor checkpoint hash drifted",
    )
    require(
        sha256_file(PREDECESSOR_PUBLIC_PATH)
        == EXPECTED_PREDECESSOR_PUBLIC_SHA256,
        "838D predecessor report hash drifted",
    )
    report = json.loads(PREDECESSOR_PUBLIC_PATH.read_text(encoding="utf-8"))
    result = report.get("result", {})
    require(
        report.get("schema")
        == "nobu16.kr.pc-dialogue-runtime-vm-integration.v1"
        and report.get("status") == "PASS"
        and report.get("steam_write_performed") is False
        and result.get("semantic_review_approved") == EXPECTED_ROWS
        and result.get("runtime_review_pending") == EXPECTED_PENDING_BEFORE
        and result.get("private_integrated_decision_sha256")
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256,
        "838D predecessor report contract drifted",
    )
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    raw = PREDECESSOR_PRIVATE_PATH.read_bytes()
    require(
        not raw.startswith(b"\xef\xbb\xbf"),
        "BF7B predecessor checkpoint has a BOM",
    )
    for line_number, line in enumerate(
        raw.decode("utf-8", errors="strict").splitlines(),
        start=1,
    ):
        require(line, f"BF7B predecessor line {line_number} is empty")
        row = json.loads(line)
        key = (str(row["resource"]), str(row["coordinate"]))
        require(key not in rows, f"duplicate predecessor row: {key}")
        rows[key] = row
    require(
        len(rows) == EXPECTED_ROWS
        and sum(
            row.get("runtime_review") == "pending"
            for row in rows.values()
        )
        == EXPECTED_PENDING_BEFORE,
        "BF7B predecessor universe drifted",
    )
    return rows, report


def load_and_rebuild_proposal() -> tuple[
    dict[str, Any],
    dict[str, Any],
]:
    require(
        sha256_file(PROPOSAL_PRIVATE_PATH)
        == EXPECTED_PROPOSAL_PRIVATE_SHA256,
        "EE99 private proposal hash drifted",
    )
    require(
        sha256_file(PROPOSAL_PUBLIC_PATH)
        == EXPECTED_PROPOSAL_PUBLIC_SHA256,
        "712A public proposal hash drifted",
    )
    require(
        sha256_file(LEDGER_PATH) == EXPECTED_LEDGER_SHA256,
        "90987 residual ledger hash drifted",
    )
    (
        private_content,
        public_content,
        private_payload,
        public_payload,
    ) = PROPOSAL.build_outputs()
    require(
        private_content
        == PROPOSAL_PRIVATE_PATH.read_text(encoding="utf-8")
        and public_content
        == PROPOSAL_PUBLIC_PATH.read_text(encoding="ascii"),
        "proposal files differ from the deterministic 63-assembly rebuild",
    )
    scope = private_payload.get("scope", {})
    proof = private_payload.get("proof", {})
    public_proof = public_payload.get("proof", {})
    require(
        private_payload.get("schema") == PROPOSAL.PRIVATE_SCHEMA
        and public_payload.get("schema") == PROPOSAL.PUBLIC_SCHEMA
        and private_payload.get("status") == "PASS"
        and public_payload.get("status") == "PASS"
        and private_payload.get("steam_write_performed") is False
        and public_payload.get("steam_write_performed") is False
        and scope.get("pending_coordinate_count")
        == EXPECTED_PROMOTION_ROWS
        and scope.get("verified_coordinate_count")
        == EXPECTED_RENEWAL_ROWS
        and len(private_payload.get("exact_translation_map", {}))
        == EXPECTED_OVERRIDE_ROWS
        and private_payload.get("counts", {}).get("register_assemblies")
        == EXPECTED_ASSEMBLIES
        and public_proof.get("register_assemblies")
        == EXPECTED_ASSEMBLIES
        and proof.get(
            "all_7_register_assemblies_current_relative_raw_g1n_nonexpanding"
        )
        is True
        and proof.get("all_7_register_assemblies_grammar_pass") is True
        and proof.get("control_topology_preserved_for_all_roots") is True
        and proof.get("protected_tokens_preserved_for_all_coordinates") is True
        and proof.get("minimum_width_delta_px") == -216
        and proof.get("maximum_width_delta_px") == 0
        and proof.get("assembly_manifest_sha256")
        == EXPECTED_ASSEMBLY_MANIFEST_SHA256
        and proof.get("component_manifest_sha256")
        == EXPECTED_COMPONENT_MANIFEST_SHA256
        and proof.get("decision_manifest_sha256")
        == EXPECTED_PROPOSAL_DECISION_MANIFEST_SHA256,
        "deterministic proposal proof contract drifted",
    )
    return private_payload, public_payload


def build_partition(
    proposal: Mapping[str, Any],
) -> dict[str, Any]:
    scope = proposal["scope"]
    promotion = set(map(str, scope["pending_coordinates"]))
    renewal = set(map(str, scope["verified_coordinates"]))
    overrides = {
        str(coordinate): str(text)
        for coordinate, text in proposal["exact_translation_map"].items()
    }
    decisions = promotion | renewal
    roots = {parse_coordinate(coordinate)[:2] for coordinate in promotion}
    renewal_roots = {
        parse_coordinate(coordinate)[:2] for coordinate in renewal
    }
    compact_map = json.dumps(
        overrides,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    require(
        len(promotion) == EXPECTED_PROMOTION_ROWS
        and coordinate_digest(promotion)
        == EXPECTED_PROMOTION_COORDINATE_SHA256
        and len(roots) == EXPECTED_PROMOTION_ROOTS
        and record_digest(roots) == EXPECTED_ROOT_SHA256
        and len(renewal) == EXPECTED_RENEWAL_ROWS
        and coordinate_digest(renewal) == EXPECTED_RENEWAL_COORDINATE_SHA256
        and len(renewal_roots) == EXPECTED_RENEWAL_ROOTS
        and record_digest(renewal_roots)
        == EXPECTED_RENEWAL_ROOT_SHA256
        and len(decisions) == EXPECTED_DECISION_ROWS
        and coordinate_digest(decisions)
        == EXPECTED_DECISION_COORDINATE_SHA256
        and len(overrides) == EXPECTED_OVERRIDE_ROWS
        and coordinate_digest(overrides)
        == EXPECTED_OVERRIDE_COORDINATE_SHA256
        and sha256_bytes(compact_map) == EXPECTED_OVERRIDE_MAP_SHA256,
        "simple-caller closure partition drifted",
    )
    actions = {
        "runtime_promotion": promotion - set(overrides),
        "translation_override_and_runtime_promotion":
        promotion & set(overrides),
        "verification_renewal": renewal - set(overrides),
        "translation_override_and_verification_renewal":
        renewal & set(overrides),
    }
    require(
        {name: len(values) for name, values in actions.items()}
        == EXPECTED_ACTION_COUNTS
        and all(
            coordinate_digest(values)
            == EXPECTED_ACTION_COORDINATE_SHA256[name]
            for name, values in actions.items()
        ),
        "simple-caller action partition drifted",
    )
    return {
        "promotion": promotion,
        "renewal": renewal,
        "decisions": decisions,
        "roots": roots,
        "renewal_roots": renewal_roots,
        "overrides": overrides,
        "actions": actions,
    }


def action_for(
    coordinate: str,
    *,
    promotion: set[str],
    overrides: Mapping[str, str],
) -> str:
    if coordinate in promotion:
        return (
            "translation_override_and_runtime_promotion"
            if coordinate in overrides
            else "runtime_promotion"
        )
    return (
        "translation_override_and_verification_renewal"
        if coordinate in overrides
        else "verification_renewal"
    )


def build_audit(
    predecessor_report: Mapping[str, Any],
    proposal_public: Mapping[str, Any],
    partition: Mapping[str, Any],
) -> dict[str, Any]:
    proof = proposal_public["proof"]
    report = {
        "schema": AUDIT_SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "method": METHOD,
        "scope": {
            "selector": 1066,
            "terminal_records": 7,
            "predecessor_rows": EXPECTED_ROWS,
            "predecessor_pending_rows": EXPECTED_PENDING_BEFORE,
            "reviewed_rows": EXPECTED_DECISION_ROWS,
            "exact_override_rows": EXPECTED_OVERRIDE_ROWS,
            "runtime_promotion_rows": EXPECTED_PROMOTION_ROWS,
            "runtime_promotion_roots": EXPECTED_PROMOTION_ROOTS,
            "verification_renewal_rows": EXPECTED_RENEWAL_ROWS,
            "verification_renewal_roots": EXPECTED_RENEWAL_ROOTS,
            "post_layer_pending_rows": EXPECTED_PENDING_AFTER,
        },
        "action_counts": dict(sorted(EXPECTED_ACTION_COUNTS.items())),
        "proof": {
            "register_assemblies_recomputed": EXPECTED_ASSEMBLIES,
            "all_7_register_assemblies_grammar_pass":
            proof["all_7_register_assemblies_grammar_pass"],
            "all_7_register_assemblies_current_relative_raw_g1n_"
            "nonexpanding":
            proof[
                "all_7_register_assemblies_current_relative_"
                "raw_g1n_nonexpanding"
            ],
            "minimum_width_delta_px": proof["minimum_width_delta_px"],
            "maximum_width_delta_px": proof["maximum_width_delta_px"],
            "control_topology_preserved_for_all_roots":
            proof["control_topology_preserved_for_all_roots"],
            "protected_tokens_preserved_for_all_coordinates":
            proof["protected_tokens_preserved_for_all_coordinates"],
            "preexisting_verified_evidence_renewed": True,
            "per_row_game_playback_required": False,
        },
        "guards": {
            "predecessor_private_sha256":
            EXPECTED_PREDECESSOR_PRIVATE_SHA256,
            "predecessor_public_sha256": EXPECTED_PREDECESSOR_PUBLIC_SHA256,
            "predecessor_result_canonical_sha256": canonical_sha256(
                predecessor_report["result"]
            ),
            "proposal_private_sha256": EXPECTED_PROPOSAL_PRIVATE_SHA256,
            "proposal_public_sha256": EXPECTED_PROPOSAL_PUBLIC_SHA256,
            "residual_ledger_sha256": EXPECTED_LEDGER_SHA256,
            "predecessor_candidate_sha256":
            EXPECTED_PREDECESSOR_CANDIDATE_SHA256,
            "candidate_sha256": EXPECTED_CANDIDATE_SHA256,
            "root_sha256": record_digest(partition["roots"]),
            "promotion_coordinate_sha256":
            coordinate_digest(partition["promotion"]),
            "renewal_coordinate_sha256":
            coordinate_digest(partition["renewal"]),
            "renewal_root_sha256":
            record_digest(partition["renewal_roots"]),
            "decision_coordinate_sha256":
            coordinate_digest(partition["decisions"]),
            "override_coordinate_sha256":
            coordinate_digest(partition["overrides"]),
            "override_map_canonical_sha256":
            EXPECTED_OVERRIDE_MAP_SHA256,
            "terminal_coordinate_sha256":
            EXPECTED_TERMINAL_COORDINATE_SHA256,
            "assembly_manifest_sha256":
            EXPECTED_ASSEMBLY_MANIFEST_SHA256,
            "component_manifest_sha256":
            EXPECTED_COMPONENT_MANIFEST_SHA256,
            "proposal_decision_manifest_sha256":
            EXPECTED_PROPOSAL_DECISION_MANIFEST_SHA256,
            "action_coordinate_sha256": dict(
                sorted(EXPECTED_ACTION_COORDINATE_SHA256.items())
            ),
        },
        "distribution_policy": {
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_report_contains_exact_coordinates": False,
            "tracked_report_contains_translation_map_keys": False,
            "private_proposal_stays_below_tmp": True,
            "private_decision_bodies_stay_below_tmp": True,
            "private_evidence_contains_dialogue_bodies": False,
        },
        "steam_write_performed": False,
    }
    return HONORIFIC.seal_report(report)


def build_updated_rows(
    *,
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    proposal: Mapping[str, Any],
    partition: Mapping[str, Any],
    audit: Mapping[str, Any],
    audit_file_sha256: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    decision_manifest = {
        str(row["coordinate"]): row
        for row in proposal["manifests"]["decisions"]
    }
    promotion = partition["promotion"]
    renewal = partition["renewal"]
    overrides = partition["overrides"]
    updated_rows: list[dict[str, Any]] = []
    evidence_rows: list[dict[str, Any]] = []
    for coordinate in sorted(partition["decisions"], key=parse_coordinate):
        predecessor = predecessor_rows[("pk_msggame", coordinate)]
        updated = copy.deepcopy(dict(predecessor))
        is_promotion = coordinate in promotion
        is_override = coordinate in overrides
        manifest = decision_manifest[coordinate]
        require(
            manifest.get("status")
            == ("pending" if is_promotion else "verified")
            and manifest.get("decision")
            == ("rewrite" if is_override else "keep"),
            f"proposal decision binding drifted: {coordinate}",
        )
        if is_override:
            updated["translation"] = overrides[coordinate]
            FAMILY.CALLER.PREDECESSOR.repair_hard_risks(updated)
            require(
                ENGINE.sha256_text(str(updated["translation"]))
                == manifest["proposal_translation_utf16le_sha256"],
                f"override translation hash drifted: {coordinate}",
            )
            updated[OVERRIDE_FIELD] = {
                "schema": OVERRIDE_SCHEMA,
                "private_proposal_sha256":
                EXPECTED_PROPOSAL_PRIVATE_SHA256,
                "proposal_public_sha256":
                EXPECTED_PROPOSAL_PUBLIC_SHA256,
                "exact_override_coordinate_sha256":
                EXPECTED_OVERRIDE_COORDINATE_SHA256,
                "exact_override_map_sha256":
                EXPECTED_OVERRIDE_MAP_SHA256,
                "translation_utf16le_sha256":
                ENGINE.sha256_text(str(updated["translation"])),
                "control_topology_preserved": True,
                "protected_tokens_preserved": True,
                "all_7_register_assemblies_recomputed": True,
            }
        if is_promotion:
            require(
                predecessor.get("runtime_review") == "pending",
                f"promotion predecessor status drifted: {coordinate}",
            )
            updated["runtime_review"] = "verified"
            updated["scope_classification"] = "retranslated"
            updated["layout_review"] = "runtime_verified"
        else:
            require(
                coordinate in renewal
                and predecessor.get("runtime_review") == "verified",
                f"renewal predecessor status drifted: {coordinate}",
            )
        action = action_for(
            coordinate,
            promotion=promotion,
            overrides=overrides,
        )
        evidence = {
            "schema": EVIDENCE_SCHEMA,
            "resource": "pk_msggame",
            "coordinate": coordinate,
            "status": "verified",
            "method": METHOD,
            "action": action,
            "translation_utf16le_sha256":
            ENGINE.sha256_text(str(updated["translation"])),
            "predecessor_binding": {
                "row_sha256": canonical_sha256(predecessor),
                "checkpoint_sha256":
                EXPECTED_PREDECESSOR_PRIVATE_SHA256,
            },
            "closure_binding": {
                "selector": 1066,
                "terminal_coordinate_sha256":
                EXPECTED_TERMINAL_COORDINATE_SHA256,
                "candidate_sha256": EXPECTED_CANDIDATE_SHA256,
                "decision_coordinate_sha256":
                EXPECTED_DECISION_COORDINATE_SHA256,
                "audit_report_file_sha256": audit_file_sha256,
                "audit_report_payload_sha256":
                audit["guards"]["report_payload_sha256"],
                "proposal_private_sha256":
                EXPECTED_PROPOSAL_PRIVATE_SHA256,
                "proposal_public_sha256":
                EXPECTED_PROPOSAL_PUBLIC_SHA256,
                "residual_ledger_sha256": EXPECTED_LEDGER_SHA256,
                "assembly_manifest_sha256":
                EXPECTED_ASSEMBLY_MANIFEST_SHA256,
                "component_manifest_sha256":
                EXPECTED_COMPONENT_MANIFEST_SHA256,
                "proposal_decision_manifest_sha256":
                EXPECTED_PROPOSAL_DECISION_MANIFEST_SHA256,
            },
            "proof": {
                "grammar_pass_for_all_7_register_assemblies": True,
                "raw_g1n_nonexpanding_for_all_7_register_assemblies": True,
                "control_topology_preserved": True,
                "protected_tokens_preserved": True,
            },
            "preexisting_verified_evidence_renewed": not is_promotion,
            "per_row_game_playback_required": False,
        }
        updated[UPDATE_ACTION_FIELD] = action
        updated["runtime_vm_verification"] = evidence
        updated_rows.append(updated)
        evidence_rows.append(evidence)
    updated_rows.sort(key=row_sort_key)
    evidence_rows.sort(key=lambda row: parse_coordinate(str(row["coordinate"])))
    require(
        Counter(row["action"] for row in evidence_rows)
        == Counter(EXPECTED_ACTION_COUNTS),
        "private output action counts drifted",
    )
    return updated_rows, evidence_rows


def build_promotion(
    *,
    audit: Mapping[str, Any],
    audit_file_sha256: str,
    decision_content: str,
    evidence_content: str,
) -> dict[str, Any]:
    report = {
        "schema": PROMOTION_SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "method": METHOD,
        "result": {
            "runtime_promotion_rows": EXPECTED_PROMOTION_ROWS,
            "runtime_promotion_roots": EXPECTED_PROMOTION_ROOTS,
            "verification_renewal_rows": EXPECTED_RENEWAL_ROWS,
            "verification_renewal_roots": EXPECTED_RENEWAL_ROOTS,
            "pending_rows_before": EXPECTED_PENDING_BEFORE,
            "pending_rows_after": EXPECTED_PENDING_AFTER,
            "exact_override_rows": EXPECTED_OVERRIDE_ROWS,
            "decision_delta_rows": EXPECTED_DECISION_ROWS,
            "private_evidence_rows": EXPECTED_DECISION_ROWS,
            "private_decision_delta_sha256": sha256_bytes(
                decision_content.encode("utf-8")
            ),
            "private_evidence_sha256": sha256_bytes(
                evidence_content.encode("utf-8")
            ),
        },
        "action_counts": dict(sorted(EXPECTED_ACTION_COUNTS.items())),
        "evidence": {
            "audit_report_file_sha256": audit_file_sha256,
            "audit_report_payload_sha256":
            audit["guards"]["report_payload_sha256"],
            "predecessor_checkpoint_sha256":
            EXPECTED_PREDECESSOR_PRIVATE_SHA256,
            "proposal_private_sha256": EXPECTED_PROPOSAL_PRIVATE_SHA256,
            "proposal_public_sha256": EXPECTED_PROPOSAL_PUBLIC_SHA256,
            "candidate_sha256": EXPECTED_CANDIDATE_SHA256,
            "decision_coordinate_sha256":
            EXPECTED_DECISION_COORDINATE_SHA256,
            "assembly_manifest_sha256":
            EXPECTED_ASSEMBLY_MANIFEST_SHA256,
        },
        "distribution_policy": {
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_report_contains_exact_coordinates": False,
            "tracked_report_contains_translation_map_keys": False,
            "private_decision_bodies_stay_below_tmp": True,
            "private_evidence_contains_dialogue_bodies": False,
        },
        "steam_write_performed": False,
    }
    return HONORIFIC.seal_report(report)


SOURCE_TEXT_RE = re.compile(
    r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7a3]"
)
EXACT_COORDINATE_RE = re.compile(r"\b\d+:\d+(?::\d+)?\b")
SENSITIVE_BODY_KEYS = {
    "translation",
    "source_text",
    "current_text",
    "candidate_text",
    "assembly",
    "exact_translation_map",
    "exact_maps",
    "records",
    "site_lists",
    "accepted_sites",
    "rejected_sites",
}


def body_key_count(value: Any) -> int:
    if isinstance(value, Mapping):
        return sum(
            int(key in SENSITIVE_BODY_KEYS) + body_key_count(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return sum(body_key_count(child) for child in value)
    return 0


def assert_source_free_report(value: Any) -> None:
    require(body_key_count(value) == 0, "tracked report contains a body key")
    if isinstance(value, Mapping):
        for child in value.values():
            assert_source_free_report(child)
    elif isinstance(value, list):
        for child in value:
            assert_source_free_report(child)
    elif isinstance(value, str):
        require(
            SOURCE_TEXT_RE.search(value) is None,
            "tracked report contains Hangul/CJK text",
        )
        require(
            EXACT_COORDINATE_RE.search(value) is None,
            "tracked report contains an exact coordinate",
        )


def rebuild_merged_candidate(
    merged: Mapping[tuple[str, str], Mapping[str, Any]],
) -> str:
    replacements = {
        parse_coordinate(coordinate): str(row["translation"])
        for (resource, coordinate), row in merged.items()
        if resource == "pk_msggame"
        and isinstance(row.get("translation"), str)
    }
    blob = BASE_AUDIT.rebuild_packed_with_literals(
        BASE_AUDIT.DEFAULT_PK_CURRENT.read_bytes(),
        replacements,
    )
    return sha256_bytes(blob)


def build_outputs() -> tuple[
    str,
    str,
    str,
    str,
    dict[str, Any],
    dict[str, Any],
]:
    steam_before = {
        "base": HONORIFIC.live_hash(LIVE_STEAM_BASE),
        "pk": HONORIFIC.live_hash(LIVE_STEAM_PK),
    }
    predecessor_rows, predecessor_report = load_predecessor()
    proposal, proposal_public = load_and_rebuild_proposal()
    partition = build_partition(proposal)
    audit = build_audit(
        predecessor_report,
        proposal_public,
        partition,
    )
    HONORIFIC.validate_seal(audit)
    audit_content = canonical_json(audit)
    audit_file_sha256 = sha256_bytes(audit_content.encode("utf-8"))
    updated_rows, evidence_rows = build_updated_rows(
        predecessor_rows=predecessor_rows,
        proposal=proposal,
        partition=partition,
        audit=audit,
        audit_file_sha256=audit_file_sha256,
    )
    decision_content = canonical_jsonl(updated_rows)
    evidence_content = canonical_jsonl(evidence_rows)
    promotion = build_promotion(
        audit=audit,
        audit_file_sha256=audit_file_sha256,
        decision_content=decision_content,
        evidence_content=evidence_content,
    )
    HONORIFIC.validate_seal(promotion)
    promotion_content = canonical_json(promotion)
    steam_after = {
        "base": HONORIFIC.live_hash(LIVE_STEAM_BASE),
        "pk": HONORIFIC.live_hash(LIVE_STEAM_PK),
    }
    require(
        steam_before == steam_after,
        "live Steam msggame changed during closure build",
    )
    return (
        decision_content,
        evidence_content,
        audit_content,
        promotion_content,
        audit,
        {
            "predecessor_rows": predecessor_rows,
            "proposal": proposal,
            "partition": partition,
            "updated_rows": updated_rows,
            "evidence_rows": evidence_rows,
            "promotion": promotion,
            "steam_before": steam_before,
            "steam_after": steam_after,
        },
    )


def validate_outputs(
    *,
    decision_content: str,
    evidence_content: str,
    audit_content: str,
    promotion_content: str,
    audit: Mapping[str, Any],
    bundle: Mapping[str, Any],
    require_frozen_hashes: bool = True,
) -> None:
    promotion = bundle["promotion"]
    require(
        decision_content == canonical_jsonl(bundle["updated_rows"])
        and evidence_content == canonical_jsonl(bundle["evidence_rows"])
        and audit_content == canonical_json(audit)
        and promotion_content == canonical_json(promotion),
        "serialized output drifted",
    )
    frozen = (
        EXPECTED_AUDIT_FILE_SHA256,
        EXPECTED_PROMOTION_FILE_SHA256,
        EXPECTED_DECISION_FILE_SHA256,
        EXPECTED_EVIDENCE_FILE_SHA256,
    )
    actual = (
        sha256_bytes(audit_content.encode("utf-8")),
        sha256_bytes(promotion_content.encode("utf-8")),
        sha256_bytes(decision_content.encode("utf-8")),
        sha256_bytes(evidence_content.encode("utf-8")),
    )
    if require_frozen_hashes:
        require(all(frozen), "output hashes have not been frozen")
        require(actual == frozen, f"frozen output file hash drifted: {actual}")
    HONORIFIC.validate_seal(audit)
    HONORIFIC.validate_seal(promotion)
    assert_source_free_report(audit)
    assert_source_free_report(promotion)
    require(
        body_key_count(bundle["evidence_rows"]) == 0,
        "private evidence contains a dialogue body/map key",
    )
    updated_by_key = {
        ("pk_msggame", str(row["coordinate"])): row
        for row in bundle["updated_rows"]
    }
    require(
        len(updated_by_key) == EXPECTED_DECISION_ROWS
        and len(bundle["evidence_rows"]) == EXPECTED_DECISION_ROWS,
        "private output row count drifted",
    )
    merged = {
        key: copy.deepcopy(dict(row))
        for key, row in bundle["predecessor_rows"].items()
    }
    merged.update(updated_by_key)
    pending_after = sum(
        row.get("runtime_review") == "pending" for row in merged.values()
    )
    actions = Counter(
        str(row[UPDATE_ACTION_FIELD]) for row in bundle["updated_rows"]
    )
    require(
        pending_after == EXPECTED_PENDING_AFTER
        and dict(actions) == EXPECTED_ACTION_COUNTS
        and rebuild_merged_candidate(merged) == EXPECTED_CANDIDATE_SHA256
        and audit["scope"]["post_layer_pending_rows"]
        == EXPECTED_PENDING_AFTER
        and promotion["result"]["pending_rows_after"]
        == EXPECTED_PENDING_AFTER
        and audit.get("steam_write_performed") is False
        and promotion.get("steam_write_performed") is False
        and bundle["steam_before"] == bundle["steam_after"],
        "final simple-caller closure result drifted",
    )
    for coordinate, text in bundle["partition"]["overrides"].items():
        require(
            merged[("pk_msggame", coordinate)].get("translation") == text,
            f"merged private override drifted: {coordinate}",
        )


def validate_output_paths(args: argparse.Namespace) -> None:
    private_root = DIALOGUE_TMP.resolve(strict=False)
    steam_paths = {
        LIVE_STEAM_BASE.resolve(strict=False),
        LIVE_STEAM_PK.resolve(strict=False),
    }
    for path in (args.decision_output, args.evidence_output):
        resolved = path.resolve(strict=False)
        require(
            resolved not in steam_paths,
            "private output may not target live Steam",
        )
        require(
            private_root in resolved.parents,
            f"private output must remain below {private_root}",
        )
    require(
        args.audit_output.resolve(strict=False)
        == DEFAULT_AUDIT_OUTPUT.resolve(strict=False)
        and args.promotion_output.resolve(strict=False)
        == DEFAULT_PROMOTION_OUTPUT.resolve(strict=False),
        "public reports must use their fixed tracked source-free paths",
    )
    paths = {
        args.audit_output.resolve(strict=False),
        args.promotion_output.resolve(strict=False),
        args.decision_output.resolve(strict=False),
        args.evidence_output.resolve(strict=False),
    }
    require(len(paths) == 4, "closure output paths must be distinct")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-output", type=Path, default=DEFAULT_AUDIT_OUTPUT)
    parser.add_argument(
        "--promotion-output",
        type=Path,
        default=DEFAULT_PROMOTION_OUTPUT,
    )
    parser.add_argument(
        "--decision-output",
        type=Path,
        default=DEFAULT_DECISION_OUTPUT,
    )
    parser.add_argument(
        "--evidence-output",
        type=Path,
        default=DEFAULT_EVIDENCE_OUTPUT,
    )
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    require(args.write or args.check, "choose --write and/or --check")
    validate_output_paths(args)
    (
        decision_content,
        evidence_content,
        audit_content,
        promotion_content,
        audit,
        bundle,
    ) = build_outputs()
    validate_outputs(
        decision_content=decision_content,
        evidence_content=evidence_content,
        audit_content=audit_content,
        promotion_content=promotion_content,
        audit=audit,
        bundle=bundle,
        require_frozen_hashes=True,
    )
    outputs = {
        args.audit_output: audit_content,
        args.promotion_output: promotion_content,
        args.decision_output: decision_content,
        args.evidence_output: evidence_content,
    }
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
    if args.check:
        for path, expected_content in outputs.items():
            require(path.is_file(), f"output missing: {path}")
            require(
                path.read_text(encoding="utf-8") == expected_content,
                f"output drifted: {path}",
            )
    print(
        "PASS "
        f"overrides={EXPECTED_OVERRIDE_ROWS} "
        f"renewed={EXPECTED_RENEWAL_ROWS} "
        f"promoted={EXPECTED_PROMOTION_ROWS} "
        f"pending={EXPECTED_PENDING_AFTER} "
        f"assemblies={EXPECTED_ASSEMBLIES} "
        "steam_write=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
