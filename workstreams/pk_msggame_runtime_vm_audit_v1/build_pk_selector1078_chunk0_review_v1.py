#!/usr/bin/env python3
"""Validate selector-1078 chunk 0 and emit its source-free checkpoint."""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PREDECESSOR = load_module(
    WORKSTREAM / "build_pk_selector268_chunk0_review_v1.py",
    "selector1078_chunk0_review_predecessor",
)
BASE = PREDECESSOR.BASE
CORE_BUILD_REPORT = PREDECESSOR._build_report
ASSIGN_WRAPPER = load_module(
    WORKSTREAM / "build_pk_selector1078_assignment_v1.py",
    "selector1078_chunk0_review_assignment",
)
ASSIGN = ASSIGN_WRAPPER.ASSIGNMENT
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.RECORDS.load_records

BASE.ASSIGNMENT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector1078_assignment_v1.py"
)
BASE.ASSIGNMENT_PATH = (
    DIALOGUE_TMP / "pk_selector1078_assignment.private.v1.json"
)
BASE.ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector1078_assignment_coverage.v1.json"
)
BASE.OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector268_consolidated_checkpoint.private.v1.jsonl"
)
BASE.PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector1078_chunk0_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector1078_chunk0_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector1078_chunk0_review.source_free.v1.json"
)
PRIVATE_PLAN_PATH = (
    DIALOGUE_TMP / "pk_selector1078_chunk0_review_plan.private.v1.json"
)
PRIVATE_GENERATOR_PATH = (
    DIALOGUE_TMP / "build_pk_selector1078_chunk0_private_review_v1.py"
)
BASE.SELECTOR = 1078
BASE.TERMINALS = tuple(range(2560, 2567))
BASE.CHUNK_ID = 0
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector1078-chunk0-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector1078-chunk0-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector1078-chunk0-review.source-free.v1"
BASE.METHOD = (
    "post_selector268_selector1078_chunk0_exact_one_rewrite_attempt_"
    "atomic_neighbor_multilingual_historical_register_review"
)
BASE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "3D8332E789CD35560E78A68B153F25E20E500FF681E6DB38515240204DBE8551"
)
BASE.EXPECTED_ASSIGNMENT_SHA256 = (
    "6637FE722BF183489E8BE32473A67C5B40FDD2BB25DB080D6C5B429111A90F4D"
)
BASE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "0B01BDE88CE6CF091E07720FB5C83772F2C7EA7E9139C85EEFF7788F92864EA3"
)
BASE.EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "0936BD050D1BB529848AD861B951D178A3521C086BC41027C4ED4A5B4FBC79C3"
)
BASE.EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "E29B1FE509F18C48189B5D532EEA7F47D711FF8FF8298283D46AA1CDA9D57D02"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "56362E38B394EAB7739DC6497BEE5711A9600DAB30BB02A062C5820E4C9DD0CA"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "92B86808931C1FD34320BC5A9BFD05B7AD704FA9392534FF8DE8F6293F413DAD"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "7E213AA71B08BAC327AAE93366904FEB96F1ED15B8B0A01DB576A603452CB536"
)
BASE.EXPECTED_LIVE_STEAM_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "9976EE272E2F83FF93CAFE341AD3CBE5865D41918777288DF012F1D1BD5F98AE"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 3,
    "accepted_sites": 3,
    "assembly_branches": 147,
    "atomic_neighbor_assembly_branches": 168,
    "blocked_pending_roots": 7,
    "blocked_pending_rows": 18,
    "blocked_sites": 18,
    "decision_rows": 7,
    "non_display_candidate_sites": 0,
    "prior_assembly_pending_roots": 7,
    "prior_assembly_pending_rows": 12,
    "promoted_pending_rows": 7,
    "rewrite_attempt_roots": 10,
    "roots": 21,
    "same_gap_branches": 35,
    "shared_override_rows": 0,
    "sites": 21,
    "translation_overrides": 2,
    "verification_renewals": 0,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 5,
    "translation_override_and_runtime_promotion": 2,
}
BASE.EXPECTED_DIGESTS = {
    "assembly":
        "12A90AD3B7488058140B6E1EA3B2FE1DD6FBA6DD31C25DD7E763F0884E21C0E9",
    "decision":
        "665CB5CF0983E2B4E24F9D2295CF8DDEEE078FAB2AA0B416E3E7836C5F9FE17B",
    "override":
        "090D4C4E0E571B850C51626E065CFE1460D924B507D1D8F93E9B876A1EF1A2FA",
    "promoted":
        "665CB5CF0983E2B4E24F9D2295CF8DDEEE078FAB2AA0B416E3E7836C5F9FE17B",
}
BASE.ASSIGN = ASSIGN
BASE.ENGINE = ASSIGN.ENGINE
BASE.RANKING = ASSIGN.RANKING
BASE._EDGE_CACHE.clear()
BASE._TERMINAL_CACHE.clear()

EXPECTED_PLAN_SHA256 = (
    "342C244B63E5DE1108AF8862E6C63120D378994D770EC4489A628581D8492A7D"
)
EXPECTED_GENERATOR_SHA256 = (
    "AC68B2E018270AD10B22900C2F152AA48E7E4D36D941107B1C12FE9C78AF0FC8"
)
EXPECTED_CANDIDATE_TERMINAL_SHA256 = (
    "51C604DD377D15C87B104D243917530C2F1FBB2956C4770AC77451C9ED249219"
)
EXPECTED_SOURCE_TERMINAL_SHA256 = (
    "2CFD3803511E2C4BCDDDFC25768645ED2E90CB8CACB750FC27F82742E9CA3793"
)
EXPECTED_EMPTY_TERMINAL_SHA256 = (
    "B0F66ADC83641586656866813FD9DD0B8EBB63796075661BA45D1AA8089E1D44"
)
EXPECTED_ATOMIC_NEIGHBOR_SHA256 = (
    "CE487EB0FDCD9135FEC64A725C64A4E523DDFF96EFA858D15F938647DF9E916C"
)


def terminal_values(records):
    return [
        BASE.first_literal(records, (0, record_id))
        for record_id in BASE.TERMINALS
    ]


def terminal_digest(records) -> str:
    return BASE.sha256_bytes(
        "\0".join(terminal_values(records)).encode("utf-8")
    )


def validate_selector1078_guards() -> None:
    BASE.require(
        BASE.sha256_file(PRIVATE_PLAN_PATH) == EXPECTED_PLAN_SHA256
        and BASE.sha256_file(PRIVATE_GENERATOR_PATH)
            == EXPECTED_GENERATOR_SHA256,
        "private review inputs drifted",
    )
    candidate, _current, source, contexts, _pending = ASSIGN.load_records()
    decisions = BASE.load_decisions()
    assignment = json.loads(
        BASE.ASSIGNMENT_PATH.read_text(encoding="utf-8")
    )
    chunk = assignment["chunks"][BASE.CHUNK_ID]
    decision_coordinates = {
        str(row["coordinate"]) for row in decisions
    }
    decision_roots = {
        ":".join(coordinate.split(":")[:2])
        for coordinate in decision_coordinates
    }
    terminal_roots = {(0, record_id) for record_id in BASE.TERMINALS}
    BASE.require(
        terminal_digest(candidate) == EXPECTED_CANDIDATE_TERMINAL_SHA256
        and terminal_digest(source) == EXPECTED_SOURCE_TERMINAL_SHA256
        and all(
            terminal_digest(contexts[language])
                == EXPECTED_EMPTY_TERMINAL_SHA256
            for language in ("en", "sc", "tc")
        )
        and sorted(Counter(terminal_values(candidate)).values()) == [2, 2, 3]
        and sorted(Counter(terminal_values(source)).values()) == [1, 1, 2, 3]
        and not terminal_roots & {
            BASE.parse_coordinate(coordinate)[:2]
            for coordinate in decision_coordinates
        },
        "selector1078 terminal register/read-only drifted",
    )
    owned: dict[str, list[int]] = {}
    for relation in assignment["completed_selector_overlap"]["relations"]:
        owned.setdefault(str(relation["root"]), []).append(
            int(relation["selector"])
        )
    BASE.require(
        all(
            row.get("overlap_owner") == owned.get(
                ":".join(str(row["coordinate"]).split(":")[:2])
            )
            and "auto" not in str(row["action"]).lower()
            for row in decisions
        ),
        "owned overlap was not freshly reviewed",
    )
    same_gap_roots = set(assignment["same_gap_control_atom"]["roots"])
    template_coordinates = {
        coordinate
        for root in assignment["identical_template_atoms"][0]
        for coordinate in chunk["pending_coordinates"]
        if coordinate.startswith(root + ":")
    }
    BASE.require(
        not same_gap_roots & decision_roots
        and template_coordinates <= decision_coordinates,
        "atomic pending disposition drifted",
    )
    evidence = json.loads(
        BASE.PRIVATE_EVIDENCE_PATH.read_text(encoding="utf-8")
    )
    pending_rows = evidence["pending_semantic_rows"]
    neighbor_rows = evidence["atomic_neighbor_assembly_manifest"]
    BASE.require(
        len(pending_rows) == 25
        and len(evidence["rewrite_attempt_roots"]) == 10
        and all(
            row["fresh_semantic_review"] == "approved"
            and row["historical_factuality_review"] == "approved"
            and row["speaker_tone_review"] == "approved"
            and row["rewrite_attempt_count"] == 1
            and not row["prior_assembly_evidence_used_for_semantics"]
            and set(row["context_utf8_sha256"]) == {"jp", "en", "sc", "tc"}
            for row in pending_rows
        )
        and len(neighbor_rows) == 168
        and len({row["root"] for row in neighbor_rows}) == 10
        and all(
            row["current_relative_raw_g1n_nonexpanding"]
            for row in neighbor_rows
            if row["review_disposition"] == "approved_atomic_root"
        )
        and evidence["digests"][
            "atomic_neighbor_assembly_canonical_sha256"
        ] == EXPECTED_ATOMIC_NEIGHBOR_SHA256
        and evidence["prior_evidence"]["overlap_is_subset"]
        and not evidence["prior_evidence"][
            "automatic_status_promotion_authorized"
        ],
        "fresh atomic multilingual review drifted",
    )
    ledger = {
        str(row["coordinate"]): row
        for row in (
            json.loads(line)
            for line in BASE.OFFICIAL_LEDGER_PATH.read_text(
                encoding="utf-8"
            ).splitlines()
            if line
        )
        if row.get("resource") == "pk_msggame"
    }
    BASE.require(
        all(
            ledger[coordinate].get("runtime_assembly_evidence")
            and ledger[coordinate].get("runtime_review") == "pending"
            for coordinate in assignment["scope"]["terminal_coordinates"]
        ),
        "terminal prior evidence/read-only state drifted",
    )


def build_report():
    validate_selector1078_guards()
    report = CORE_BUILD_REPORT()
    report["proof"].update({
        "all_atomic_neighbor_alternatives_reviewed": True,
        "completed_selector_overlap_freshly_reviewed": True,
        "historical_register_exact_reviewed": True,
        "non_display_candidate_action_count_zero": True,
        "pending_assembly_evidence_did_not_auto_promote": True,
        "pending_multilingual_semantics_fresh": True,
        "repeated_template_atom_single_disposition": True,
        "same_gap_atom_blocked_as_unit": True,
        "source_only_action_count_zero": True,
        "terminal_context_languages_non_authoritative": True,
        "terminal_register_multiplicity_preserved": True,
        "terminal_rows_read_only": True,
    })
    return report


BASE.build_report = build_report
coordinate_digest = BASE.coordinate_digest
load_decisions = BASE.load_decisions
serialized = BASE.serialized
sha256_file = BASE.sha256_file
ReviewError = BASE.ReviewError
DEFAULT_PUBLIC_OUTPUT = BASE.DEFAULT_PUBLIC_OUTPUT
EXPECTED_ACTION_COUNTS = BASE.EXPECTED_ACTION_COUNTS
EXPECTED_DIGESTS = BASE.EXPECTED_DIGESTS
EXPECTED_PUBLIC_FILE_SHA256 = BASE.EXPECTED_PUBLIC_FILE_SHA256


if __name__ == "__main__":
    raise SystemExit(BASE.main())
