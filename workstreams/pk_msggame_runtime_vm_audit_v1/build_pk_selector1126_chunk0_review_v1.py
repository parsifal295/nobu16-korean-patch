#!/usr/bin/env python3
"""Validate selector-1126 chunk 0 and emit its source-free checkpoint."""

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
    "selector1126_chunk0_review_base",
)
ASSIGN = load_module(
    WORKSTREAM / "build_pk_selector1126_assignment_v1.py",
    "selector1126_chunk0_review_assignment",
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
    / "pk_selector1126_chunk0_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector1126_chunk0_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector1126_chunk0_review.source_free.v1.json"
)
BASE.SELECTOR = 1126
BASE.TERMINALS = tuple(range(2616, 2623))
BASE.CHUNK_ID = 0
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector1126-chunk0-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector1126-chunk0-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector1126-chunk0-review.source-free.v1"
BASE.METHOD = (
    "post_selector748_selector1126_chunk0_fresh_semantic_seven_branch_"
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
    "75DE26F6C85557CAD3E261E0ACB494F65CCCCB1F986EC4D5531DA946F2FE1B6D"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "9A3B80F100666B7DA115059E3D1D508220825E48966B6AFAD7D9C455A91DBCA8"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "903B515128E94FE263430FAF7EECC51759A0DD132211F3C3047E5DAA6D16D9A6"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "AEBD15E0CFB551619932DC416812859A25F84D70526060F382055BE8E411C877"
)
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "A231BA9BD105695A9F3413A65BEAA3CE3D1615504BB930D84282B90BEA2D4540"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 20,
    "accepted_sites": 35,
    "assembly_branches": 266,
    "blocked_pending_roots": 2,
    "blocked_pending_rows": 4,
    "blocked_sites": 3,
    "decision_rows": 65,
    "promoted_pending_rows": 40,
    "roots": 38,
    "same_gap_branches": 14,
    "shared_override_rows": 0,
    "sites": 38,
    "translation_overrides": 44,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 21,
    "translation_override_and_runtime_promotion": 19,
    "translation_override_and_verification_renewal": 25,
}
BASE.EXPECTED_DIGESTS = {
    "assembly": "537ABADF1822E29D6670B7CFBFBE9BB4EFDE19D48025656610CD0EFC49888401",
    "decision": "FF89803FF29BBA880E5A90CA11D3CA48E649BD27398C9A014A81967CC7945900",
    "override": "E7AC77C5128F1654D22B53D1871F2E1942A5322A1B07A75E5FF48CDEEB7A9A92",
    "promoted": "6D1C956645788003A6E38DF89B3B5D2304FA1AF024DBC528013FC44742F75B09",
}
BASE.ASSIGN = ASSIGN
BASE.ENGINE = ASSIGN.ENGINE
BASE.RANKING = ASSIGN.RANKING
BASE._EDGE_CACHE.clear()
BASE._TERMINAL_CACHE.clear()


if __name__ == "__main__":
    raise SystemExit(BASE.main())
