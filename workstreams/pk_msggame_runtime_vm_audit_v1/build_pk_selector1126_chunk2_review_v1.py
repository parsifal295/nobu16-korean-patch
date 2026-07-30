#!/usr/bin/env python3
"""Validate selector-1126 chunk 2 and emit its source-free checkpoint."""

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
    "selector1126_chunk2_review_base",
)
ASSIGN = load_module(
    WORKSTREAM / "build_pk_selector1126_assignment_v1.py",
    "selector1126_chunk2_review_assignment",
)

BASE.ASSIGNMENT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector1126_assignment_v1.py"
)
BASE.ASSIGNMENT_PATH = (
    DIALOGUE_TMP / "pk_selector1126_assignment.private.v1.json"
)
BASE.ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector1126_assignment_coverage.v1.json"
)
BASE.OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector748_consolidated_checkpoint.private.v1.jsonl"
)
BASE.PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector1126_chunk2_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector1126_chunk2_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector1126_chunk2_review.source_free.v1.json"
)
BASE.SELECTOR = 1126
BASE.TERMINALS = tuple(range(2616, 2623))
BASE.CHUNK_ID = 2
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector1126-chunk2-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector1126-chunk2-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector1126-chunk2-review.source-free.v1"
BASE.METHOD = (
    "post_selector748_selector1126_chunk2_fresh_semantic_seven_branch_"
    "same_gap_owned_dependency_and_current_relative_review"
)
BASE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "9EFDF4FD9CD8330A97AC59E44B4364F9EE965549FEC24F65C5AA79295EDA6ACE"
)
BASE.EXPECTED_ASSIGNMENT_SHA256 = (
    "6E5CC3EB27553DC7ECA4AF5095D3F7AB5FAEDBBC5D260A33D635F8E8F407BEE2"
)
BASE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "83B6F9CA80DF3400ABEAC5DF6BE8E2335FF97A8F407FAE0854A14BCD70C7BFA3"
)
BASE.EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "05D9C79515E8B161CD469FFEC5C340F54BE9BB94BFBA8F725B8DFC025DE49E76"
)
BASE.EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "63D1151625C2F6E050173FF9AC6F11545E1E6DB5D06BEE53FC5D0B3A17403A9F"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "8A99A6A6F73269848EF3E8A5AE20EBC31EB34EB802A3961D667877943BE64F10"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "903B515128E94FE263430FAF7EECC51759A0DD132211F3C3047E5DAA6D16D9A6"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "4C9B1B550904B64A5502141EA984A30F2BE48FD6D637F89709CC2086024EA989"
)
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "2378BE997B9FE2FBCA44DF21014BFD12FDDFE0E5FE73BB5154581E4E6DDC8CE3"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 20,
    "accepted_sites": 38,
    "assembly_branches": 266,
    "blocked_pending_roots": 0,
    "blocked_pending_rows": 0,
    "blocked_sites": 0,
    "decision_rows": 71,
    "promoted_pending_rows": 42,
    "roots": 38,
    "same_gap_branches": 0,
    "shared_override_rows": 0,
    "sites": 38,
    "translation_overrides": 56,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 15,
    "translation_override_and_runtime_promotion": 27,
    "translation_override_and_verification_renewal": 29,
}
BASE.EXPECTED_DIGESTS = {
    "assembly": "008D96EA06CB82EF48912CB490F9D0F184E4A91C87C7829986291044249747CD",
    "decision": "D02E6E3413B7A5105F7ADC4F207BF2A99F0981C1D29AD4B7E5FFD09B9AAA6AD9",
    "override": "923B7151578DFA39D3486CFFCF8B0B5B3310403DB648C4E4797197CFEBA89C4B",
    "promoted": "40BF11A45408E53C171960242AE79E9001E58E736849F25776419990EEBD3D8E",
}
BASE.ASSIGN = ASSIGN
BASE.ENGINE = ASSIGN.ENGINE
BASE.RANKING = ASSIGN.RANKING
BASE._EDGE_CACHE.clear()
BASE._TERMINAL_CACHE.clear()


if __name__ == "__main__":
    raise SystemExit(BASE.main())
