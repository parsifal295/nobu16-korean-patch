#!/usr/bin/env python3
"""Validate selector-142 chunk 2 and emit its source-free checkpoint."""

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
    "selector142_chunk2_review_base",
)
ASSIGN = load_module(
    WORKSTREAM / "build_pk_selector142_assignment_v1.py",
    "selector142_chunk2_review_assignment",
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
    / "pk_selector142_chunk2_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector142_chunk2_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector142_chunk2_review.source_free.v1.json"
)
BASE.SELECTOR = 142
BASE.TERMINALS = tuple(range(1440, 1447))
BASE.CHUNK_ID = 2
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector142-chunk2-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector142-chunk2-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector142-chunk2-review.source-free.v1"
BASE.METHOD = (
    "post_selector1126_selector142_chunk2_fresh_semantic_seven_branch_"
    "same_gap_owned_dependency_and_current_relative_review"
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
    "6F0F575A206F2A2B3E1244E0451556000058B3580A7FF70345EE46F24920FD40"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "75C32D13199A16F0A887D8D52A37ADE7D6DA989A9A6F508C94943205B0171415"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "B25D15DB919FC4E3CF3A68E7C10938F581C233F04DA111F1C8D0ECA0A3F86D62"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "CDE3CA58494DCB02EF2E199D5074F3344846C1C5736D8DBCC6EBC24C1E89BA76"
)
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "8B3F493D7BD169B5BF0176F829A92AE03BFEEC4ABD788C3FBF37F9832DE754C2"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 26,
    "accepted_sites": 39,
    "assembly_branches": 273,
    "blocked_pending_roots": 0,
    "blocked_pending_rows": 0,
    "blocked_sites": 0,
    "decision_rows": 63,
    "promoted_pending_rows": 54,
    "roots": 39,
    "same_gap_branches": 0,
    "shared_override_rows": 0,
    "sites": 39,
    "translation_overrides": 31,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 32,
    "translation_override_and_runtime_promotion": 22,
    "translation_override_and_verification_renewal": 9,
}
BASE.EXPECTED_DIGESTS = {
    "assembly": "88FBA0B87D279D94CC4D3F0BE2E423A9B8C627DD95F0679437C9FB50A2939E85",
    "decision": "83BC31D4FC10682122DE9E47C331A32163A719AACEA033C8A345A9DFC2157F92",
    "override": "E7C8C883B9795786E483C0424A3F07EA96FEF0A8B7FF7035B88D257B3348460D",
    "promoted": "70D7B815EABF50557D01F66EDF12D5380D58C17094E770FECB9E2C99CA7A5772",
}
BASE.ASSIGN = ASSIGN
BASE.ASSIGN.load_records = ASSIGN.BASE.load_records
BASE.ENGINE = ASSIGN.ENGINE
BASE.RANKING = ASSIGN.RANKING
BASE._EDGE_CACHE.clear()
BASE._TERMINAL_CACHE.clear()


if __name__ == "__main__":
    raise SystemExit(BASE.main())
