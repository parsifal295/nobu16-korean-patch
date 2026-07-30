#!/usr/bin/env python3
"""Validate selector-142 chunk 0 and emit its source-free checkpoint."""

from __future__ import annotations

import importlib.util
import sys
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
    "selector142_chunk0_review_base",
)
ASSIGN = load_module(
    WORKSTREAM / "build_pk_selector142_assignment_v1.py",
    "selector142_chunk0_review_assignment",
)

BASE.ASSIGNMENT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector142_assignment_v1.py"
)
BASE.ASSIGNMENT_PATH = (
    DIALOGUE_TMP / "pk_selector142_assignment.private.v1.json"
)
BASE.ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector142_assignment_coverage.v1.json"
)
BASE.OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1126_consolidated_checkpoint.private.v1.jsonl"
)
BASE.PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector142_chunk0_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector142_chunk0_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector142_chunk0_review.source_free.v1.json"
)
BASE.SELECTOR = 142
BASE.TERMINALS = tuple(range(1440, 1447))
BASE.CHUNK_ID = 0
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector142-chunk0-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector142-chunk0-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector142-chunk0-review.source-free.v1"
BASE.METHOD = (
    "post_selector1126_selector142_chunk0_fresh_semantic_seven_branch_"
    "same_gap_and_current_relative_review"
)
BASE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "AE1428FBF34BA042F1588E89DAA02623752D791BCD498687B9AD8595ED4BD7FF"
)
BASE.EXPECTED_ASSIGNMENT_SHA256 = (
    "3F22858009367851ADCFBC99E4620CCD4676043FD22755DBF48A50571B7E4C7E"
)
BASE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "D0EA381E8491BDD34E7E9D30BFCAA027CCBCA197468EB5AFF6F76B5F4D892438"
)
BASE.EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "3198DC9F7A06809636D0C43F5740A65B5D4C50E7226D53AA7C52B7D893EFA06E"
)
BASE.EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "8CB612B1F881A15E46F5450DE4AC0BAFB1A067531886BF5E80EC7726B6033F92"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "66DC85B09C88F3C42A659A13AEBB06DF60EAB724675F1DD1376CC73ADFFB78A9"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "B25D15DB919FC4E3CF3A68E7C10938F581C233F04DA111F1C8D0ECA0A3F86D62"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "23D24C0BCE7E4D6A65EBE920446D5C80E9C99A3AB2307D104FDB3E6E432E5491"
)
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "BEBE9154674989ABFA86926A91FAF911DC8EAB5D2646A0C3348046F6D6A23AB5"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 16,
    "accepted_sites": 34,
    "assembly_branches": 238,
    "blocked_pending_roots": 0,
    "blocked_pending_rows": 0,
    "blocked_sites": 0,
    "decision_rows": 46,
    "promoted_pending_rows": 32,
    "roots": 34,
    "same_gap_branches": 0,
    "shared_override_rows": 0,
    "sites": 34,
    "translation_overrides": 27,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 19,
    "translation_override_and_runtime_promotion": 13,
    "translation_override_and_verification_renewal": 14,
}
BASE.EXPECTED_DIGESTS = {
    "assembly": "BA6DE01AB55C7D96EA70D5FAAE518470880017066E7339620334AFA92707EC1A",
    "decision": "41093EAC8D0793CD2463A5EB65825D38E633A5139ED58FB8CAB3326CA2C5C79E",
    "override": "39E4D2E0A85990DC2E171E31A7743989C97267A7B94E3FC53AD4E456D258CCD6",
    "promoted": "0F3037F847F4311AEE9FFBE5C3880587124D2144292431DC63280F28C7C58908",
}
BASE.ASSIGN = ASSIGN
BASE.ASSIGN.load_records = ASSIGN.BASE.load_records
BASE.ENGINE = ASSIGN.ENGINE
BASE.RANKING = ASSIGN.RANKING
BASE._EDGE_CACHE.clear()
BASE._TERMINAL_CACHE.clear()


if __name__ == "__main__":
    raise SystemExit(BASE.main())
