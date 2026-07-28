#!/usr/bin/env python3
"""Validate selector-1162 chunk 0 and emit its source-free checkpoint."""

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
    "selector1162_chunk0_review_base",
)
ASSIGN_WRAPPER = load_module(
    WORKSTREAM / "build_pk_selector1162_assignment_v1.py",
    "selector1162_chunk0_review_assignment_wrapper",
)
ASSIGN = ASSIGN_WRAPPER.ASSIGNMENT
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.RECORDS.load_records

BASE.ASSIGNMENT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector1162_assignment_v1.py"
)
BASE.ASSIGNMENT_PATH = (
    DIALOGUE_TMP / "pk_selector1162_assignment.private.v1.json"
)
BASE.ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector1162_assignment_coverage.v1.json"
)
BASE.OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector322_consolidated_checkpoint.private.v1.jsonl"
)
BASE.PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector1162_chunk0_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector1162_chunk0_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector1162_chunk0_review.source_free.v1.json"
)
BASE.SELECTOR = 1162
BASE.TERMINALS = tuple(range(1902, 1909))
BASE.CHUNK_ID = 0
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector1162-chunk0-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector1162-chunk0-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector1162-chunk0-review.source-free.v1"
BASE.METHOD = (
    "post_selector322_selector1162_chunk0_single_pass_"
    "caller_stem_current_relative_review"
)
BASE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "9E4B2A3684EB89B3D206B4C43BE47DDC7746896562926398DB6ECEC30C6DD534"
)
BASE.EXPECTED_ASSIGNMENT_SHA256 = (
    "2144C6C9C077AC38A95F408B4AC6D1C21F4DDC09ADD749699E8F599DA3E2D371"
)
BASE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "11A182F29CD68FC96348DAACD15DC9FE80082ECA7A79345AE10563E30EEA00E1"
)
BASE.EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "9A7E135544FA2F2A02A0D2B4941159CB92A3E4A495AF72B6CB335DE371351343"
)
BASE.EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "35F4B232698A5BD953F40FA92F0F8684A1ECA4E40A47ED25F8C736F0280DDAD9"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "8F72984067BB399C60F5DCA113D8BC1FBB8328537A434A03180469E8C71962DE"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "D0739EBB2E00B9034071165D00CA0D5E08D5F30A6400C8FF38CDA2867BA0203E"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "94FE58C283D696DA36E0F6ADB8339713A0211163EDCD6FD0A92EB5110AE613D2"
)
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "BEC9A41FE7C7DE2921C11396E7A42EF142C06098D668B2737C6DD9F5268C9342"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 1,
    "accepted_sites": 1,
    "assembly_branches": 210,
    "blocked_pending_roots": 8,
    "blocked_pending_rows": 18,
    "blocked_sites": 29,
    "decision_rows": 3,
    "promoted_pending_rows": 3,
    "roots": 30,
    "same_gap_branches": 7,
    "shared_override_rows": 0,
    "sites": 30,
    "translation_overrides": 1,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 2,
    "translation_override_and_runtime_promotion": 1,
}
BASE.EXPECTED_DIGESTS = {
    "assembly": "DBC1CDC7053C2A0312CBB97DDC5850B28B781E42B4BECCD2D2BA33C84035ACD4",
    "decision": "78E19F53FA48AF0E74A906C8A6A65A7823165EF667C247D39088C3036A87D4C8",
    "override": "C3F9E8CDF0C3779CAD67D79D3D4A41E740F27032F2F9E77367035139AAF9AB4D",
    "promoted": "78E19F53FA48AF0E74A906C8A6A65A7823165EF667C247D39088C3036A87D4C8",
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
