#!/usr/bin/env python3
"""Validate selector-514 chunk 1 and emit its source-free checkpoint."""

from __future__ import annotations

import argparse
import importlib.util
import json
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
    "selector514_chunk1_review_base",
)
ASSIGN = load_module(
    WORKSTREAM / "build_pk_selector514_assignment_v1.py",
    "selector514_chunk1_review_assignment",
)

BASE.ASSIGNMENT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector514_assignment_v1.py"
)
BASE.ASSIGNMENT_PATH = (
    DIALOGUE_TMP / "pk_selector514_assignment.private.v1.json"
)
BASE.ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector514_assignment_coverage.v1.json"
)
BASE.OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector142_consolidated_checkpoint.private.v1.jsonl"
)
BASE.PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector514_chunk1_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector514_chunk1_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector514_chunk1_review.source_free.v1.json"
)
BASE.SELECTOR = 514
BASE.TERMINALS = tuple(range(1895, 1902))
BASE.CHUNK_ID = 1
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector514-chunk1-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector514-chunk1-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector514-chunk1-review.source-free.v1"
BASE.METHOD = (
    "post_selector142_selector514_chunk1_empty_emphasis_terminal_"
    "dependency_same_gap_owned_dependency_and_current_relative_review"
)
BASE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "88236661B06478F554DA70706265602722DC4A38254767AF2C9F8CAF6D718A73"
)
BASE.EXPECTED_ASSIGNMENT_SHA256 = (
    "22D71A0373FF9B325ABE06C356BBA3A239DB56E9EECB10BFACFAA10C85B1E8DA"
)
BASE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "EA962FAAC51391DD773E4519693B41377DA5359491451F0631FB297A6A29EAA2"
)
BASE.EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "5D3673BC67F8FB55B258BB236CBC6ACD3E76F2E001300994ED7AFD742601C0DB"
)
BASE.EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "254E6F3F4E587D2F2401E77EBD1B2C3D8B10057FC866B8739B7AED7EAACC6D44"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "160D857EC71B859E448D5FF7537C575DFC5A0A7C2712514142DDE2B8FC66BD28"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "6E3E5CD8A0FF7CC07C69BD9ABDCB2380FFD507D21F528E2A446D57329359F6A8"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "61228A7E1EE0D2BF6C853D4BD33B4DD72E835E5F0D31123D9F79085258A157F0"
)
DEPENDENCY_REVIEWED_CANDIDATE_SHA256 = (
    "7603BADC7202678B16D2357FF84AF87146667D7FBCB6604AE2C85A4FC24A4BF9"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 10,
    "accepted_sites": 19,
    "assembly_branches": 182,
    "blocked_pending_roots": 5,
    "blocked_pending_rows": 15,
    "blocked_sites": 7,
    "decision_rows": 34,
    "dependency_override_rows": 4,
    "promoted_pending_rows": 31,
    "roots": 26,
    "same_gap_branches": 147,
    "shared_override_rows": 0,
    "sites": 26,
    "translation_overrides": 10,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 24,
    "translation_override_and_runtime_promotion": 7,
    "translation_override_and_verification_renewal": 3,
}
BASE.EXPECTED_DIGESTS = {
    "assembly": "9CA541E98EA828C316B7B59F5C1FE83CA6899183C9EE9C08D33FB8CFA69EE6EB",
    "decision": "0F939564CC98C83CEB3333B71EE01BEC41123C7A760870A339150A27C8195E9C",
    "override": "83E4CBC4C250E2468C23247363A87F22C7419BA47D7E38B818726577ABD7C240",
    "promoted": "3CB3A16BA0A0DE450D532276D1AB46FAF045BF6DE2E21E1EB14639F96A8F3BD6",
}
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "D506896AA1CD2F6F9F4EFB490DEE76D0A228B7535281442F5C6DF902A09E9A75"
)
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.RECORDS.load_records
BASE.ASSIGN = ASSIGN
BASE.ENGINE = ASSIGN.ENGINE
BASE.RANKING = ASSIGN.RANKING
BASE._EDGE_CACHE.clear()
BASE._TERMINAL_CACHE.clear()

_current_records = None
_load_records = ASSIGN.load_records


def load_records():
    global _current_records
    result = _load_records()
    _current_records = result[1]
    return result


ASSIGN.load_records = load_records


def gap_assembly(*, records, source, root, gap_id, ordinal):
    literals = BASE.ENGINE.parse_record_literals(records[root])
    BASE.require(0 < gap_id <= len(literals), "invalid gap")
    edges = [
        edge
        for edge in BASE.graph_edges_cached(records)[root]
        if int(edge["gap_id"]) == gap_id
    ]
    result = literals[gap_id - 1].text
    for edge in sorted(edges, key=lambda row: int(row["offset"])):
        selector = int(edge["target"][1])
        terminals = BASE.selected_terminal_roots(
            records, source, selector
        )
        if selector == BASE.SELECTOR and records is not _current_records:
            result += ""
        else:
            result += BASE.first_literal(records, terminals[ordinal])
    if gap_id < len(literals):
        result += literals[gap_id].text
    return result


BASE.gap_assembly = gap_assembly
_build_report = BASE.build_report


def build_report():
    report = _build_report()
    report["guards"]["dependency_reviewed_candidate_sha256"] = (
        DEPENDENCY_REVIEWED_CANDIDATE_SHA256
    )
    report["proof"]["shared_empty_terminal_dependency_owned_by_chunk_zero"] = (
        True
    )
    return report


BASE.build_report = build_report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    content = BASE.serialized(report)
    output_sha256 = BASE.sha256_bytes(content)
    BASE.require(
        output_sha256 == BASE.EXPECTED_PUBLIC_FILE_SHA256,
        f"public output hash drifted: {output_sha256}",
    )
    if args.check:
        BASE.require(
            BASE.DEFAULT_PUBLIC_OUTPUT.is_file()
            and BASE.DEFAULT_PUBLIC_OUTPUT.read_bytes() == content,
            "public artifact drifted",
        )
    else:
        BASE.DEFAULT_PUBLIC_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        BASE.DEFAULT_PUBLIC_OUTPUT.write_bytes(content)
    print(json.dumps({
        "accepted_pending": BASE.EXPECTED_COUNTS["promoted_pending_rows"],
        "blocked_pending": BASE.EXPECTED_COUNTS["blocked_pending_rows"],
        "output_sha256": output_sha256,
        "reviewed_candidate_sha256":
            BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256,
        "status": "PASS",
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
