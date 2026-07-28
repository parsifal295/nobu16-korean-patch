#!/usr/bin/env python3
"""Validate selector-226 chunk 0 and emit its source-free checkpoint."""

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
    "selector226_chunk0_review_base",
)
ASSIGN_WRAPPER = load_module(
    WORKSTREAM / "build_pk_selector226_assignment_v1.py",
    "selector226_chunk0_review_assignment_wrapper",
)
ASSIGN = ASSIGN_WRAPPER.ASSIGNMENT
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.RECORDS.load_records

BASE.ASSIGNMENT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector226_assignment_v1.py"
)
BASE.ASSIGNMENT_PATH = DIALOGUE_TMP / "pk_selector226_assignment.private.v1.json"
BASE.ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector226_assignment_coverage.v1.json"
)
BASE.OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1168_consolidated_checkpoint.private.v1.jsonl"
)
BASE.PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector226_chunk0_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector226_chunk0_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector226_chunk0_review.source_free.v1.json"
)
THOUGHT_EVIDENCE_PATH = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_thought_predicate_family_exact_closure_evidence.private.v1.jsonl"
)
BASE.SELECTOR = 226
BASE.TERMINALS = tuple(range(1538, 1545))
BASE.CHUNK_ID = 0
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector226-chunk0-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector226-chunk0-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector226-chunk0-review.source-free.v1"
BASE.METHOD = (
    "post_selector1168_selector226_chunk0_exact_one_rewrite_attempt_"
    "prior_caller_assembly_revalidation"
)
BASE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "B8957E12245FDAA02CDAB3690E4DE4FE4601D2B92F8185D5734DBAB909C87D7F"
)
BASE.EXPECTED_ASSIGNMENT_SHA256 = (
    "223EBD7D1C0C0D6E78DCD97D0189C1E5099DBB917DD2498CC659BEDEBFAEE050"
)
BASE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "BFD1F9D8A813C2ADA7D8C065B4F7C1963F8704A7538C306C9EF6DE203F414215"
)
BASE.EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "56FBAF8FB54CCFA7EAF10355F66FE6A730374804F48FB4CD9F8F15A99AEE9A91"
)
BASE.EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "FC7FA52ED723BAE5D55DCDBCCE3B68BD4E1A71BEE3AB745830541E65E5F452DD"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "1B4F0568039DBF5659E7536B22268E7534A79C86D5357014E813C5D55B1E7EE8"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "EF84A8B8A18C1F2F1F72D3A650C01DC7B058F32A3536C130809C4FCB31C837C7"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = BASE.EXPECTED_CANDIDATE_SHA256
BASE.EXPECTED_LIVE_STEAM_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "A5F078515256725FB25637F59FD1E0672CFE81333A69D2D165EB70052C02E8AD"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 15,
    "accepted_sites": 32,
    "assembly_branches": 245,
    "blocked_pending_roots": 0,
    "blocked_pending_rows": 0,
    "blocked_sites": 3,
    "decision_rows": 20,
    "non_display_candidate_sites": 1,
    "prior_caller_evidence_roots": 34,
    "prior_pending_caller_evidence_roots": 15,
    "promoted_pending_rows": 20,
    "rewrite_attempt_roots": 35,
    "roots": 35,
    "same_gap_branches": 0,
    "shared_override_rows": 0,
    "sites": 35,
    "translation_overrides": 0,
}
BASE.EXPECTED_ACTION_COUNTS = {"runtime_promotion": 20}
BASE.EXPECTED_DIGESTS = {
    "assembly": "31FCCB7F883940F8C58CCBDE0095CC0CCA1D162B1BC1A9331BD12AE3BBF0E18F",
    "decision": "6BA4E37411D87CEA47806635AA7122ABAF7383E70E034B3E3C4FA7849A126D66",
    "override": "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "promoted": "6BA4E37411D87CEA47806635AA7122ABAF7383E70E034B3E3C4FA7849A126D66",
}
BASE.ASSIGN = ASSIGN
BASE.ENGINE = ASSIGN.ENGINE
BASE.RANKING = ASSIGN.RANKING
BASE._EDGE_CACHE.clear()
BASE._TERMINAL_CACHE.clear()

EXPECTED_THOUGHT_EVIDENCE_SHA256 = (
    "76722DBB632D9CBB78C5BE089C18BDA8AD66C79C8A302B79DBE7DA9C03F32399"
)
EXPECTED_CANDIDATE_TERMINAL_SHA256 = (
    "E84F2CF9B57C34F9C40F357BFC0469E2A7FAB5C49E33DC1734447F6C9F069E62"
)
EXPECTED_SOURCE_TERMINAL_SHA256 = (
    "DB8801176872E89F4109D2AECA4A0B60A51E76CB0A3EAF5FE6EA6E04966E3511"
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


def validate_selector226_guards() -> None:
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
        ),
        "selector226 terminal register family drifted",
    )
    BASE.require(
        sorted(Counter(terminal_values(candidate)).values()) == [1, 1, 2, 3]
        and not terminal_roots & decision_roots,
        "selector226 terminal multiplicity or read-only guard drifted",
    )
    owned = {
        relation["root"]: []
        for relation in assignment["completed_selector_overlap"]["relations"]
    }
    for relation in assignment["completed_selector_overlap"]["relations"]:
        owned[relation["root"]].append(relation["selector"])
    for row in decisions:
        root = ":".join(str(row["coordinate"]).split(":")[:2])
        expected = owned.get(root)
        BASE.require(
            row.get("overlap_owner") == expected
            and "auto" not in str(row["action"]).lower(),
            "selector226 owned overlap was not freshly reviewed",
        )
    template_atoms = [set(group) for group in assignment["identical_template_atoms"]]
    chunk_roots = set(chunk["roots"])
    BASE.require(
        all(
            not (atom & chunk_roots) or atom <= chunk_roots
            for atom in template_atoms
        ),
        "selector226 template atom split",
    )
    BASE.require(
        BASE.sha256_file(THOUGHT_EVIDENCE_PATH)
        == EXPECTED_THOUGHT_EVIDENCE_SHA256,
        "selector226 prior caller evidence drifted",
    )


_build_report = BASE.build_report


def build_report():
    validate_selector226_guards()
    report = _build_report()
    report["proof"].update({
        "connective_and_space_preserved": True,
        "non_display_candidate_action_count_zero": True,
        "pending_multilingual_semantics_fresh": True,
        "prior_thought_evidence_used_for_assembly_only": True,
        "source_only_action_count_zero": True,
        "template_atoms_atomic": True,
        "terminal_register_multiplicity_preserved": True,
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
