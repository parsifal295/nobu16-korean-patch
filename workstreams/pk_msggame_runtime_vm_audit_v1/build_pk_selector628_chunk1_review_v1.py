#!/usr/bin/env python3
"""Validate selector-628 chunk 1 and emit its source-free checkpoint."""

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
    "selector628_chunk1_review_base",
)
ASSIGN = load_module(
    WORKSTREAM / "build_pk_selector628_assignment_v1.py",
    "selector628_chunk1_review_assignment",
)

BASE.ASSIGNMENT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector628_assignment_v1.py"
)
BASE.ASSIGNMENT_PATH = (
    DIALOGUE_TMP / "pk_selector628_assignment.private.v1.json"
)
BASE.ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector628_assignment_coverage.v1.json"
)
BASE.OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector514_consolidated_checkpoint.private.v1.jsonl"
)
BASE.PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector628_chunk1_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector628_chunk1_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector628_chunk1_review.source_free.v1.json"
)
BASE.SELECTOR = 628
BASE.TERMINALS = tuple(range(2021, 2028))
BASE.CHUNK_ID = 1
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector628-chunk1-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector628-chunk1-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector628-chunk1-review.source-free.v1"
BASE.METHOD = (
    "post_selector514_selector628_chunk1_grouped_past_tense_boundary_"
    "same_gap_owned_dependency_and_current_relative_review"
)
BASE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "4781B9533C51ED3B5A7147AE79C2E314539DECF4DAE4E2A71262340D6A4DACDE"
)
BASE.EXPECTED_ASSIGNMENT_SHA256 = (
    "14578A2713C45C4E3088E7B9547ED48CFA4BC0B2CCF8795EE522EF614691F87B"
)
BASE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "82CE0CA3BBC6579125AF1D0C20BFBF6A508B1F51594B53EC23103842CCF3B476"
)
BASE.EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "FCAB3A5CACEEAE4C610BD284D8C0631E65DA14562DB7B78A66655554EED07A79"
)
BASE.EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "139F319F7A964105ECDCB2A78E37DDE87BA6DBD13D341323B736BD204867B8F9"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "C97908A6EC4CF60A8E1501943A1A8CC05F67A028B37C3584D1E098CF1844B565"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "623C6EE2BDC25B13680C353C97847C3AC646C4B2B222A51F0F242B7A1CC2E093"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "D7CC49F07D643C393DA2B6C3415ED93120FC31A12A7CB6701ECEBABDAC67E9A5"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 11,
    "accepted_sites": 44,
    "assembly_branches": 504,
    "blocked_pending_roots": 4,
    "blocked_pending_rows": 11,
    "blocked_sites": 28,
    "decision_rows": 70,
    "promoted_pending_rows": 29,
    "roots": 72,
    "same_gap_branches": 42,
    "shared_override_rows": 0,
    "sites": 72,
    "translation_overrides": 51,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 19,
    "translation_override_and_runtime_promotion": 10,
    "translation_override_and_verification_renewal": 41,
}
BASE.EXPECTED_DIGESTS = {
    "assembly": "6C7CF5A38B1517B1EFCA41CDFEEEB5643DA4374E55132E4CCE8E833E31E591E4",
    "decision": "865E25D3F035E951244171E39A152C8C330EAF50D22B95A3E0BCC1555D3A1A99",
    "override": "11744A6E6210C1FA409AE18AADA6BD5E717CEE9B50274AD08BC97CADDA33E562",
    "promoted": "E83744A7A1C641774B780BEC88D7174C2CA987D30718BD996CCD7A7688BEE4A8",
}
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "4343397CC9BD15BFAD0283BEB9353DE322ABE54984893FA517261C70DF4211C2"
)
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.RECORDS.load_records
BASE.ASSIGN = ASSIGN
BASE.ENGINE = ASSIGN.ENGINE
BASE.RANKING = ASSIGN.RANKING
BASE._EDGE_CACHE.clear()
BASE._TERMINAL_CACHE.clear()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = BASE.build_report()
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
