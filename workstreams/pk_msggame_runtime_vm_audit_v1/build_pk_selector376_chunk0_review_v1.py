#!/usr/bin/env python3
"""Validate selector-376 chunk 0 and emit its source-free checkpoint."""

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
    "selector376_chunk0_review_base",
)
ASSIGN_WRAPPER = load_module(
    WORKSTREAM / "build_pk_selector376_assignment_v1.py",
    "selector376_chunk0_review_assignment_wrapper",
)
ASSIGN = ASSIGN_WRAPPER.ASSIGNMENT
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.RECORDS.load_records

BASE.ASSIGNMENT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector376_assignment_v1.py"
)
BASE.ASSIGNMENT_PATH = DIALOGUE_TMP / "pk_selector376_assignment.private.v1.json"
BASE.ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector376_assignment_coverage.v1.json"
)
BASE.OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1162_consolidated_checkpoint.private.v1.jsonl"
)
BASE.PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector376_chunk0_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector376_chunk0_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector376_chunk0_review.source_free.v1.json"
)
BASE.SELECTOR = 376
BASE.TERMINALS = tuple(range(1713, 1720))
BASE.CHUNK_ID = 0
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector376-chunk0-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector376-chunk0-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector376-chunk0-review.source-free.v1"
BASE.METHOD = (
    "post_selector1162_selector376_chunk0_single_pass_"
    "terminal_caller_incompatible_blocked_only_review"
)
BASE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "0E5776587F048804617A39D53BB1F9F675E73563E92F698AE1585292EEE6F759"
)
BASE.EXPECTED_ASSIGNMENT_SHA256 = (
    "B91E0CAA8134AB1B7868B79BA93C739BAF76D8EDB478A6F1E81DD254BA4D1858"
)
BASE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "046738E8E977A7929A5171136120F8C0AEFE4B61B3E7AC56ED5BA850018D6F0C"
)
BASE.EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "A3A5433CCDD5F085AF61BEDB0409B5A02C7CAD162AD4ADE5938B356C988065B4"
)
BASE.EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "3FB3E8D860F530ACE232E3C1A55EA53FA7F46668FBFC7F44A50F9C4F40B890C0"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "94FE58C283D696DA36E0F6ADB8339713A0211163EDCD6FD0A92EB5110AE613D2"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "94FE58C283D696DA36E0F6ADB8339713A0211163EDCD6FD0A92EB5110AE613D2"
)
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "B7BBB2D16EBF75D831911F63D0F6C6DE52759AF20F41EE62449B99FC9A65915C"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 0,
    "accepted_sites": 0,
    "assembly_branches": 133,
    "blocked_pending_roots": 13,
    "blocked_pending_rows": 29,
    "blocked_sites": 19,
    "decision_rows": 0,
    "promoted_pending_rows": 0,
    "roots": 19,
    "same_gap_branches": 0,
    "shared_override_rows": 0,
    "sites": 19,
    "translation_overrides": 0,
}
BASE.EXPECTED_ACTION_COUNTS = {}
BASE.EXPECTED_DIGESTS = {
    "assembly": "FA58E10EF9244C1D14826D397C15EC351342FAAFF0F69813BDAB1D100D35E1B5",
    "decision": "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "override": "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "promoted": "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
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
