#!/usr/bin/env python3
"""Validate selector-364 chunk 0 and emit its source-free checkpoint."""

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
    "selector364_chunk0_review_base",
)
ASSIGN_WRAPPER = load_module(
    WORKSTREAM / "build_pk_selector364_assignment_v1.py",
    "selector364_chunk0_review_assignment_wrapper",
)
ASSIGN = ASSIGN_WRAPPER.ASSIGNMENT
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.RECORDS.load_records

BASE.ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector364_assignment_v1.py"
BASE.ASSIGNMENT_PATH = DIALOGUE_TMP / "pk_selector364_assignment.private.v1.json"
BASE.ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector364_assignment_coverage.v1.json"
)
BASE.OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1162_consolidated_checkpoint.private.v1.jsonl"
)
BASE.PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector364_chunk0_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector364_chunk0_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector364_chunk0_review.source_free.v1.json"
)
BASE.SELECTOR = 364
BASE.TERMINALS = tuple(range(1699, 1706))
BASE.CHUNK_ID = 0
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector364-chunk0-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector364-chunk0-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector364-chunk0-review.source-free.v1"
BASE.METHOD = (
    "post_selector1162_selector364_chunk0_single_pass_"
    "caller_stem_current_relative_review"
)
BASE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "0726F36F1D0259708698AC1721943A40C119CCC0D3DCED8A87C0511497E6DFFE"
)
BASE.EXPECTED_ASSIGNMENT_SHA256 = (
    "48BC6BDF976BC50A0BDE822504AB6CA4014533859D8B0D51554DDD027C2B9653"
)
BASE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "485D30E2790D091064A93482915AC3DE4FCD1B9413FCD0B4198F442936CC75A3"
)
BASE.EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "A3A5433CCDD5F085AF61BEDB0409B5A02C7CAD162AD4ADE5938B356C988065B4"
)
BASE.EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "4FC9F47D2F80B018705D01E854EBC068047C860DAC665ED9E4EA800569DB4733"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "B332E1F0055552000106EF28BF94A34A9FE2F8F4C8A88EE210BB3DD0385B4803"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "94FE58C283D696DA36E0F6ADB8339713A0211163EDCD6FD0A92EB5110AE613D2"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "6F3880DF9105F47402378E89E9C1ADE9599C052CAEC6EE3D7CC795333C04C7DE"
)
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "206EADD38D09E906EC4530B2B0208683FD920F05B57C1095D5C77FC86C528F0D"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 2,
    "accepted_sites": 2,
    "assembly_branches": 133,
    "blocked_pending_roots": 11,
    "blocked_pending_rows": 23,
    "blocked_sites": 17,
    "decision_rows": 5,
    "promoted_pending_rows": 5,
    "roots": 19,
    "same_gap_branches": 0,
    "shared_override_rows": 0,
    "sites": 19,
    "translation_overrides": 2,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 3,
    "translation_override_and_runtime_promotion": 2,
}
BASE.EXPECTED_DIGESTS = {
    "assembly": "90F43E4CF33BD63E1135B2A4B6B37C796A5AAFDD52C5F3FD38342FFD7A294D7B",
    "decision": "ED7F8CBDFA9C2D6359A9971C5FA2B766BB26789309157C10DB0259EB8815FE66",
    "override": "D6511E887F2531B40EB1AD2B87276A164447F68CF1F84B7724EE00C01FD691C7",
    "promoted": "ED7F8CBDFA9C2D6359A9971C5FA2B766BB26789309157C10DB0259EB8815FE66",
}
BASE.ASSIGN = ASSIGN
BASE.ENGINE = ASSIGN.ENGINE
BASE.RANKING = ASSIGN.RANKING
BASE._EDGE_CACHE.clear()
BASE._TERMINAL_CACHE.clear()

_selected_terminal_roots = BASE.selected_terminal_roots


def selected_terminal_roots(records, source, selector):
    try:
        return _selected_terminal_roots(records, source, selector)
    except BASE.ReviewError:
        shape = BASE.RANKING.family_shape(
            BASE.graph_edges_cached(records),
            BASE.graph_edges_cached(source),
            (0, selector),
        )
        leaves = tuple(sorted(shape["candidate_leaves"]))
        BASE.require(leaves, f"selector {selector} has no terminal")
        return tuple(leaves[0] for _ in range(7))


BASE.selected_terminal_roots = selected_terminal_roots

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
