#!/usr/bin/env python3
"""Validate selector-268 chunk 0 and emit its source-free checkpoint."""

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


BASE = load_module(
    WORKSTREAM / "build_pk_selector550_chunk1_review_v1.py",
    "selector268_chunk0_review_base",
)
ASSIGN_WRAPPER = load_module(
    WORKSTREAM / "build_pk_selector268_assignment_v1.py",
    "selector268_chunk0_review_assignment_wrapper",
)
ASSIGN = ASSIGN_WRAPPER.ASSIGNMENT
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.RECORDS.load_records

BASE.ASSIGNMENT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector268_assignment_v1.py"
)
BASE.ASSIGNMENT_PATH = (
    DIALOGUE_TMP / "pk_selector268_assignment.private.v1.json"
)
BASE.ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector268_assignment_coverage.v1.json"
)
BASE.OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector226_consolidated_checkpoint.private.v1.jsonl"
)
BASE.PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector268_chunk0_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector268_chunk0_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector268_chunk0_review.source_free.v1.json"
)
PRIVATE_PLAN_PATH = (
    DIALOGUE_TMP / "pk_selector268_chunk0_review_plan.private.v1.json"
)
PRIVATE_GENERATOR_PATH = (
    DIALOGUE_TMP / "build_pk_selector268_chunk0_private_review_v1.py"
)
BASE.SELECTOR = 268
BASE.TERMINALS = tuple(range(1587, 1594))
BASE.CHUNK_ID = 0
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector268-chunk0-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector268-chunk0-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector268-chunk0-review.source-free.v1"
BASE.METHOD = (
    "post_selector226_selector268_chunk0_exact_one_rewrite_attempt_"
    "question_boundary_owned_overlap_and_pending_assembly_review"
)
BASE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "8D0B1F1156ABD01697502DEA809B15C483F3D9EC1AA3D16AF6509423A72FC1E1"
)
BASE.EXPECTED_ASSIGNMENT_SHA256 = (
    "91ED0510E5783DDA7B6894CA8A5144FB4D2FA9300A71BD2EC1B2F4699022C315"
)
BASE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "5F0C6B1935B7EC8568DC7C52EFB67D90BEF96398A8977DFEA70B23B3FA71053B"
)
BASE.EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "33B635E1409B290202A98719A9CD58F356551BB54703B7F287FC45250134623D"
)
BASE.EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "5941B268BEE074B6C8B168F09CB2F78C26EE769C29E6B6C10F1739BC57BA5FD3"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "AF95272CED53A341445A8060F309F3AF96FC39BCB11EA96F8EC774BBF5ACD107"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "FEE99844339C291F6950BEB2193AB5FDD8D25B6F6117AD52F81DCBF7F0CC9B66"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "92B86808931C1FD34320BC5A9BFD05B7AD704FA9392534FF8DE8F6293F413DAD"
)
BASE.EXPECTED_LIVE_STEAM_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "16E4EBED73904001F5FD160FD41BF6EE3D23629B0F000C4C6D549D0721FAB7CB"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 3,
    "accepted_sites": 6,
    "assembly_branches": 91,
    "blocked_pending_roots": 2,
    "blocked_pending_rows": 6,
    "blocked_sites": 7,
    "decision_rows": 10,
    "non_display_candidate_sites": 0,
    "prior_assembly_pending_roots": 5,
    "prior_assembly_pending_rows": 16,
    "promoted_pending_rows": 10,
    "rewrite_attempt_roots": 5,
    "roots": 12,
    "same_gap_branches": 0,
    "shared_override_rows": 0,
    "sites": 13,
    "translation_overrides": 4,
    "verification_renewals": 0,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 6,
    "translation_override_and_runtime_promotion": 4,
}
BASE.EXPECTED_DIGESTS = {
    "assembly":
        "BB64889355C07D69FB4A243513ADD807AC4F0BF943FBA0BAB2C62266679251A0",
    "decision":
        "5519C7D828B1AE3AC21D66543B0809121160B7D5D960E5D1D48257F0C20C2697",
    "override":
        "338B7C9B9EBAED69221FA581352FC6293C489697C31C4AA70B8144C705F7D2C4",
    "promoted":
        "5519C7D828B1AE3AC21D66543B0809121160B7D5D960E5D1D48257F0C20C2697",
}
BASE.ASSIGN = ASSIGN
BASE.ENGINE = ASSIGN.ENGINE
BASE.RANKING = ASSIGN.RANKING
BASE._EDGE_CACHE.clear()
BASE._TERMINAL_CACHE.clear()

EXPECTED_PLAN_SHA256 = (
    "FD5715141ECD356613B84C159A4502C1D9BA0C02162FC91A60A9EFC17267ABA0"
)
EXPECTED_GENERATOR_SHA256 = (
    "911E4E7AA15FA82BB4E55A2BD97A3619CBD7892A3D2899C2FF302EE302D76757"
)
EXPECTED_CANDIDATE_TERMINAL_SHA256 = (
    "4B8A084ECCE354B2B0201FD5A7490CE5FEE18E0A7EBDD40C3908CB2E6EED04D1"
)
EXPECTED_SOURCE_TERMINAL_SHA256 = (
    "3151D392EC13DFEA77F2972C31CEBD28D120C117C484E43C386DCB71FCB3160F"
)
EXPECTED_EMPTY_TERMINAL_SHA256 = (
    "B0F66ADC83641586656866813FD9DD0B8EBB63796075661BA45D1AA8089E1D44"
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


def validate_selector268_guards() -> None:
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
    terminal_roots = {(0, record_id) for record_id in BASE.TERMINALS}
    decision_roots = {
        BASE.parse_coordinate(str(row["coordinate"]))[:2]
        for row in decisions
    }
    BASE.require(
        terminal_digest(candidate) == EXPECTED_CANDIDATE_TERMINAL_SHA256
        and terminal_digest(source) == EXPECTED_SOURCE_TERMINAL_SHA256
        and all(
            terminal_digest(contexts[language])
                == EXPECTED_EMPTY_TERMINAL_SHA256
            for language in ("en", "sc", "tc")
        )
        and sorted(Counter(terminal_values(candidate)).values()) == [1, 2, 4]
        and not terminal_roots & decision_roots,
        "selector268 terminal register/read-only drifted",
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
            for coordinate in chunk["pending_coordinates"]
        )
        and all(
            ledger[coordinate].get("runtime_assembly_evidence")
            and ledger[coordinate].get("runtime_review") == "pending"
            for coordinate in assignment["scope"]["terminal_coordinates"]
        ),
        "pending prior assembly evidence drifted",
    )

    owned: dict[str, list[int]] = {}
    for relation in assignment["completed_selector_overlap"]["relations"]:
        owned.setdefault(str(relation["root"]), []).append(
            int(relation["selector"])
        )
    for row in decisions:
        root = ":".join(str(row["coordinate"]).split(":")[:2])
        BASE.require(
            row.get("overlap_owner") == owned.get(root)
            and "auto" not in str(row["action"]).lower(),
            "completed-selector overlap was not freshly reviewed",
        )

    evidence = json.loads(
        BASE.PRIVATE_EVIDENCE_PATH.read_text(encoding="utf-8")
    )
    BASE.require(
        len(evidence["pending_semantic_rows"]) == 16
        and len(evidence["rewrite_attempt_roots"]) == 5
        and not evidence["prior_evidence"][
            "automatic_status_promotion_authorized"
        ]
        and not evidence["prior_evidence"][
            "pending_assembly_evidence_reused_for_semantics"
        ],
        "fresh pending semantic review drifted",
    )
    terminals = terminal_values(candidate)
    for review in evidence["site_reviews"]:
        if not str(review["decision"]).startswith("accepted_"):
            continue
        for ordinal, branch in enumerate(review["assemblies"]):
            assembly = str(branch["reviewed_assembly"])
            terminal = terminals[ordinal]
            boundary = assembly.split(terminal, 1)[1].split("\n", 1)[0]
            BASE.require(
                assembly.count(terminal) == 1 and "?" in boundary,
                "accepted question boundary drifted",
            )


_build_report = BASE.build_report


def build_report():
    validate_selector268_guards()
    report = _build_report()
    report["proof"].update({
        "all_selected_question_ordinals_reviewed": True,
        "completed_selector_overlap_freshly_reviewed": True,
        "non_display_candidate_action_count_zero": True,
        "pending_assembly_evidence_did_not_auto_promote": True,
        "pending_multilingual_semantics_fresh": True,
        "question_boundary_punctuation_exact": True,
        "source_only_action_count_zero": True,
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
