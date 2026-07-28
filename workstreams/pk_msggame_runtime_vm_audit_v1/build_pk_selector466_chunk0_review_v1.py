#!/usr/bin/env python3
"""Validate selector-466 chunk 0 and emit its source-free checkpoint."""

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
    WORKSTREAM / "build_pk_selector1078_chunk0_review_v1.py",
    "selector466_chunk0_review_predecessor",
)
BASE = PREDECESSOR.BASE
CORE_BUILD_REPORT = PREDECESSOR.CORE_BUILD_REPORT
ASSIGN_WRAPPER = load_module(
    WORKSTREAM / "build_pk_selector466_assignment_v1.py",
    "selector466_chunk0_review_assignment",
)
ASSIGN = ASSIGN_WRAPPER.ASSIGNMENT
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.RECORDS.load_records

BASE.ASSIGNMENT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector466_assignment_v1.py"
)
BASE.ASSIGNMENT_PATH = (
    DIALOGUE_TMP / "pk_selector466_assignment.private.v1.json"
)
BASE.ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector466_assignment_coverage.v1.json"
)
BASE.OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1078_consolidated_checkpoint.private.v1.jsonl"
)
BASE.PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector466_chunk0_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector466_chunk0_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector466_chunk0_review.source_free.v1.json"
)
PRIVATE_PLAN_PATH = (
    DIALOGUE_TMP / "pk_selector466_chunk0_review_plan.private.v1.json"
)
PRIVATE_GENERATOR_PATH = (
    DIALOGUE_TMP / "build_pk_selector466_chunk0_private_review_v1.py"
)
BASE.SELECTOR = 466
BASE.TERMINALS = tuple(range(1839, 1846))
BASE.CHUNK_ID = 0
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector466-chunk0-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector466-chunk0-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector466-chunk0-review.source-free.v1"
BASE.METHOD = (
    "post_selector1078_selector466_chunk0_exact_one_rewrite_attempt_"
    "atomic_neighbor_multilingual_historical_register_review"
)
BASE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "729E1778540A1E5FB5BF48CACE9309B83CFE0A021FDA294049FEC91104387F71"
)
BASE.EXPECTED_ASSIGNMENT_SHA256 = (
    "8C7350F94A08894C5B88A4E6BD335DA96877EEE55902B4E9110186FE0E8C7507"
)
BASE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "457C7C0D368269F69C391E6A981CF6AA5D4FB905C99B327C2DAEE9C4F137BA5E"
)
BASE.EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "71ADE7F33FC40A817E60F429DE0A0B329E05BF37BD1E03E1671A019783E800F6"
)
BASE.EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "159087FAF3C33589CFCEA9447ECAA8074908F2AF2B5C962C67B85AC572CB5F86"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "33C957C6B6F4B64874A27859900B8DCCD6B6052969DB9CA48EB8AB985A4D93AC"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "1A931E023A5248626AE90094772657D91B4270D0F530B48ABC613FDA84BB508D"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "153F9CB70EBBF24B62168898F0FC237E50050FE713F75245D62763D878583165"
)
BASE.EXPECTED_LIVE_STEAM_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "D9F17A13C69FA8C5885D9BF048A98271ABA7B733D68C9F9AD3D6469198C418AE"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 2,
    "accepted_sites": 2,
    "assembly_branches": 266,
    "atomic_neighbor_assembly_branches": 91,
    "atomic_non_seven_way_gap_count": 3,
    "blocked_pending_roots": 6,
    "blocked_pending_rows": 13,
    "blocked_sites": 36,
    "decision_rows": 3,
    "non_display_candidate_sites": 0,
    "prior_assembly_pending_roots": 7,
    "prior_assembly_pending_rows": 12,
    "promoted_pending_rows": 3,
    "rewrite_attempt_roots": 8,
    "roots": 38,
    "same_gap_branches": 0,
    "shared_override_rows": 0,
    "sites": 38,
    "source_only_action_count": 0,
    "terminal_decision_rows": 0,
    "translation_overrides": 2,
    "verification_renewals": 0,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 1,
    "translation_override_and_runtime_promotion": 2,
}
BASE.EXPECTED_DIGESTS = {
    "assembly":
        "BC8BD05E92FEF68C407DD6B988A6F8D5C202184F634EC101446447D5AB947FD3",
    "decision":
        "26C22AA6496EC55CC60DF92F7214EE381E2D4558BA544F05A74C41BCA33D6318",
    "override":
        "1DF81C3F3183D9ECE5182F6698ED3530417EA936E7DC11A7D5093E90B4DFDC05",
    "promoted":
        "26C22AA6496EC55CC60DF92F7214EE381E2D4558BA544F05A74C41BCA33D6318",
}
BASE.ASSIGN = ASSIGN
BASE.ENGINE = ASSIGN.ENGINE
BASE.RANKING = ASSIGN.RANKING
BASE._EDGE_CACHE.clear()
BASE._TERMINAL_CACHE.clear()

EXPECTED_PLAN_SHA256 = (
    "674AF05086FF399A9E554CEAEF26ED80327CFF868EACEF42F28B879DCB59DD7F"
)
EXPECTED_GENERATOR_SHA256 = (
    "9DFB85351A537B702A3CED70C3149B03F120C9C7A01F3627C4C08BD51B3B5E7A"
)
EXPECTED_CANDIDATE_TERMINAL_SHA256 = (
    "43B346EA667D710BDFC6A84D958602CCB68DB95CA78D204C1D8F2C43B7336483"
)
EXPECTED_SOURCE_TERMINAL_SHA256 = (
    "47ABF41C98D2DF16C3C5A572EE31139D0C457B04C131D164FE69494332C4FBA3"
)
EXPECTED_EMPTY_TERMINAL_SHA256 = (
    "B0F66ADC83641586656866813FD9DD0B8EBB63796075661BA45D1AA8089E1D44"
)
EXPECTED_ATOMIC_NEIGHBOR_SHA256 = (
    "4BAE24F9EACCB93F9C2490F08B3B9682E7AC1F5DAC31A7D389F69422A7711CCF"
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


def validate_selector466_guards() -> None:
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
        and not terminal_roots & {
            BASE.parse_coordinate(coordinate)[:2]
            for coordinate in decision_coordinates
        },
        "selector466 terminal register/read-only drifted",
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
        )
        and not {
            root for root in owned
            if root in {
                ":".join(coordinate.split(":")[:2])
                for coordinate in decision_coordinates
            }
        },
        "owned overlap was promoted or not freshly blocked",
    )
    evidence = json.loads(
        BASE.PRIVATE_EVIDENCE_PATH.read_text(encoding="utf-8")
    )
    pending_rows = evidence["pending_semantic_rows"]
    neighbor_rows = evidence["atomic_neighbor_assembly_manifest"]
    BASE.require(
        len(pending_rows) == 16
        and len(evidence["rewrite_attempt_roots"]) == 8
        and all(
            row["fresh_semantic_review"] == "approved"
            and row["historical_factuality_review"] == "approved"
            and row["speaker_tone_review"] == "approved"
            and row["rewrite_attempt_count"] == 1
            and not row["prior_assembly_evidence_used_for_semantics"]
            and set(row["context_utf8_sha256"]) == {"jp", "en", "sc", "tc"}
            for row in pending_rows
        )
        and len(neighbor_rows) == 91
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
        ]
        and evidence["terminal_register_review"]["ordered_registers"]
            == [
                "formal", "plain", "archaic", "archaic",
                "formal", "archaic", "plain"
            ]
        and not evidence["terminal_register_review"][
            "context_terminals_authoritative"
        ]
        and evidence["exclusions"]["source_only_action_count"] == 0
        and evidence["exclusions"]["candidate_non_display_action_count"] == 0,
        "fresh atomic multilingual review drifted",
    )
    template_roots = {
        root for atom in assignment["identical_template_atoms"] for root in atom
    }
    site_dispositions = {
        str(row["root"]): str(row["decision"])
        for row in evidence["site_reviews"]
    }
    BASE.require(
        all(
            not (set(atom) & set(chunk["roots"]))
            or set(atom) <= set(chunk["roots"])
            for atom in assignment["identical_template_atoms"]
        )
        and len({
            site_dispositions[root]
            for root in template_roots & set(chunk["roots"])
        }) == 1,
        "repeated-template atom disposition drifted",
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
            and ledger[coordinate].get("runtime_review") == "verified"
            for coordinate in assignment["scope"]["terminal_coordinates"]
        ),
        "terminal verified/read-only state drifted",
    )


def build_report():
    validate_selector466_guards()
    report = CORE_BUILD_REPORT()
    report["proof"].update({
        "all_atomic_neighbor_alternatives_reviewed": True,
        "completed_selector_overlap_freshly_blocked": True,
        "historical_register_exact_reviewed": True,
        "non_display_candidate_action_count_zero": True,
        "pending_assembly_evidence_did_not_auto_promote": True,
        "pending_multilingual_semantics_fresh": True,
        "repeated_template_atom_single_disposition": True,
        "same_gap_candidate_site_count_zero": True,
        "source_only_action_count_zero": True,
        "terminal_context_languages_non_authoritative": True,
        "terminal_register_order_preserved": True,
        "terminal_rows_verified_read_only": True,
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
