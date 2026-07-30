#!/usr/bin/env python3
"""Validate selector-322 chunk 0 and emit its source-free checkpoint."""

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
    "selector322_chunk0_review_base",
)
ASSIGN_WRAPPER = load_module(
    WORKSTREAM / "build_pk_selector322_assignment_v1.py",
    "selector322_chunk0_review_assignment_wrapper",
)
ASSIGN = ASSIGN_WRAPPER.ASSIGNMENT
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.RECORDS.load_records

BASE.ASSIGNMENT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector322_assignment_v1.py"
)
BASE.ASSIGNMENT_PATH = (
    DIALOGUE_TMP / "pk_selector322_assignment.private.v1.json"
)
BASE.ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector322_assignment_coverage.v1.json"
)
BASE.OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector742_consolidated_checkpoint.private.v1.jsonl"
)
BASE.PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector322_chunk0_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector322_chunk0_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector322_chunk0_review.source_free.v1.json"
)
BASE.SELECTOR = 322
BASE.TERMINALS = tuple(range(1650, 1657))
BASE.CHUNK_ID = 0
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector322-chunk0-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector322-chunk0-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector322-chunk0-review.source-free.v1"
BASE.METHOD = (
    "post_selector742_selector322_chunk0_single_pass_"
    "caller_stem_current_relative_review"
)
BASE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "6DD14D61DFF734FA574CB174E97F89BD24AB69412CDD8B5FE5931E1BFEC7BB86"
)
BASE.EXPECTED_ASSIGNMENT_SHA256 = (
    "0FE780C5A37609CF062AA210212A1CB745D6938E5DA28BA9725AFD3C8DF2D97F"
)
BASE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "6A6034DC2A4485F254931AA81DEF408FBBEC805C58175B6A1FADB724EA02F364"
)
BASE.EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "4AC2CD8969958AA254D0F70F7302E1BC3D273229DBB59A0512FEB27E1786D90B"
)
BASE.EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "13AF9393F5DFC0935FA3A9FD8A495ED422DF2A5763A1A2B4509CA99BC44C6721"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "F6AAE4BA45FE2C5EA7ED674A0D7BBB27DB5205831F5742DB2AB938451DD5BF62"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "BCA693F86DEE850F95996243CB5FFA3DBA56A4F58750800FFE8253F9FC2ACFBB"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "2A28A4051E7B32D1E3495D598A7EC845E98BB7B741BA281DD9AB5201DD1607AC"
)
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "2E4DE94F1A1F228E6EFDF52982EBE25CCCA52E6CAD769724BE9469A4FA538B7A"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 7,
    "accepted_sites": 7,
    "assembly_branches": 294,
    "blocked_pending_roots": 7,
    "blocked_pending_rows": 11,
    "blocked_sites": 35,
    "decision_rows": 17,
    "promoted_pending_rows": 15,
    "roots": 42,
    "same_gap_branches": 7,
    "shared_override_rows": 0,
    "sites": 42,
    "translation_overrides": 6,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 11,
    "translation_override_and_runtime_promotion": 4,
    "translation_override_and_verification_renewal": 2,
}
BASE.EXPECTED_DIGESTS = {
    "assembly": "95004C3423DF8C44EF6F866B2A6CDCA4F7286B9759B0DDBC99E6C31E48353BBE",
    "decision": "694ADAD2DD982406FDEDA63C4470B708120BFCC98898FB2E9B75B8578832B25C",
    "override": "1954FDEAED3DE1F68A053ADEAA6C97F926F2A479F3DD1366860B4EC239586F68",
    "promoted": "72CDB4A7EBE22FA35C328AC278DFE9EB801334E9038280E171804A5268A651DA",
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
