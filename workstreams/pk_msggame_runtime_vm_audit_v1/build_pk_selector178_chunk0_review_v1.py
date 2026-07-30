#!/usr/bin/env python3
"""Validate selector-178 chunk 0 and emit its source-free checkpoint."""

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
    "selector178_chunk0_review_base",
)
ASSIGN_WRAPPER = load_module(
    WORKSTREAM / "build_pk_selector178_assignment_v1.py",
    "selector178_chunk0_review_assignment_wrapper",
)
ASSIGN = ASSIGN_WRAPPER.ASSIGNMENT
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.RECORDS.load_records

BASE.ASSIGNMENT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector178_assignment_v1.py"
)
BASE.ASSIGNMENT_PATH = (
    DIALOGUE_TMP / "pk_selector178_assignment.private.v1.json"
)
BASE.ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector178_assignment_coverage.v1.json"
)
BASE.OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1198_consolidated_checkpoint.private.v1.jsonl"
)
BASE.PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector178_chunk0_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector178_chunk0_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector178_chunk0_review.source_free.v1.json"
)
BASE.SELECTOR = 178
BASE.TERMINALS = tuple(range(1482, 1489))
BASE.CHUNK_ID = 0
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector178-chunk0-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector178-chunk0-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector178-chunk0-review.source-free.v1"
BASE.METHOD = (
    "post_selector1198_selector178_chunk0_grouped_progressive_"
    "caller_stem_same_gap_and_current_relative_review"
)
BASE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "83B8B3FAD9E37A891F2E896504DD2555FE840C4AA8CB2A099217A122E07B771A"
)
BASE.EXPECTED_ASSIGNMENT_SHA256 = (
    "C1DE0528BF795DEF68C914A32F9583C2CD084F55491C181329BAE39AE631FACC"
)
BASE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "230A9679566C5D8BD7821F0A4D148CC00A820A16EDFD22C7C5EF2567695C92A8"
)
BASE.EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "A3B6AE01A30C4EC6EFCE171345EFEB81F7FDB9EDFDCAECD90AA4A78AB3296F4F"
)
BASE.EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "FE6FF50CC1E975480C20AA5D5D5AF86D50EF312C090118D3A311EE3D784CF48E"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "6FC94BAAF6ADCC929F3342612095C14161F04A4AB5183B0AB0DC3775417B2BA2"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "74E30E798B82129565518FA04F35DC73220974CFC6E1E7E61BCEC2D8008671DA"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "ABE93504BE413246926A6EFDFBE931CD7805B09B5154348C0170695A4F0C7CBB"
)
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "6408617D0DFAEC1A652DE8655A6A3AE0CB1CF49B828DF775CC4D21093CECD365"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 6,
    "accepted_sites": 18,
    "assembly_branches": 539,
    "blocked_pending_roots": 13,
    "blocked_pending_rows": 21,
    "blocked_sites": 59,
    "decision_rows": 22,
    "promoted_pending_rows": 8,
    "roots": 75,
    "same_gap_branches": 84,
    "shared_override_rows": 0,
    "sites": 77,
    "translation_overrides": 16,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 6,
    "translation_override_and_runtime_promotion": 2,
    "translation_override_and_verification_renewal": 14,
}
BASE.EXPECTED_DIGESTS = {
    "assembly": "5963C698AF0ED1CE67A5C8782EF0AA503BCD845D0E8B860DF97416E7EB24E787",
    "decision": "70C21EB8AF172E748C8C4255EA80666AA903E6AFD09E7F47AADA9C647CE85C03",
    "override": "28A302EBA64F76B0C78857A24516CB60A14BC4016B978D19B1BF4D1ED0689BD3",
    "promoted": "7C12B2FFB64B779C345BC1EF2730978A6316DD975DA72406420F06CAD7C89F19",
}
BASE.ASSIGN = ASSIGN
BASE.ENGINE = ASSIGN.ENGINE
BASE.RANKING = ASSIGN.RANKING
BASE._EDGE_CACHE.clear()
BASE._TERMINAL_CACHE.clear()

build_report = BASE.build_report
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
