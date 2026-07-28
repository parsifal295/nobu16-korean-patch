#!/usr/bin/env python3
"""Validate selector-322 chunk 1 and emit its source-free checkpoint."""

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
    "selector322_chunk1_review_base",
)
ASSIGN = load_module(
    WORKSTREAM / "build_pk_selector322_assignment_v1.py",
    "selector322_chunk1_review_assignment",
)

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
    / "pk_selector322_chunk1_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector322_chunk1_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector322_chunk1_review.source_free.v1.json"
)
BASE.SELECTOR = 322
BASE.TERMINALS = tuple(range(1650, 1657))
BASE.CHUNK_ID = 1
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector322-chunk1-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector322-chunk1-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector322-chunk1-review.source-free.v1"
BASE.METHOD = (
    "post_selector742_selector322_chunk1_compatible_request_terminal_"
    "single_pass_recut_and_residual_block_review"
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
    "393BD642B4DD5FBC881461047A33F4510429854F2327E704FCB971B5895502A0"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "2FFA605B5FFAC27AE78FA8AB7CF49FAFDA3DAFF98182575845C949672851E8B3"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "BCA693F86DEE850F95996243CB5FFA3DBA56A4F58750800FFE8253F9FC2ACFBB"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "C161D166FB82E6A477102E5E518B74DB57AD3306A420D601B6CCA4EC50D0BA07"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 6,
    "accepted_sites": 6,
    "assembly_branches": 301,
    "blocked_pending_roots": 9,
    "blocked_pending_rows": 21,
    "blocked_sites": 37,
    "decision_rows": 11,
    "promoted_pending_rows": 10,
    "roots": 43,
    "same_gap_branches": 7,
    "sites": 43,
    "translation_overrides": 6,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 5,
    "translation_override_and_runtime_promotion": 5,
    "translation_override_and_verification_renewal": 1,
}
BASE.EXPECTED_DIGESTS = {
    "assembly": "0A1FEEEB57952DCDAC24BA07EC70DA8703C0FCD3CF9D46E4FD9A8AE17763A441",
    "decision": "C8C1A2D4EE59D1EE2DD35B62404A7D663FCC84C40FCD3B2999574AD16DA72FE7",
    "override": "5D1432333D0B14882D9F922F90A2E01A3CCE17E7CA5C10A4324530A15E130849",
    "promoted": "C9AC2F917FE4D08B26CB3A0905360174F44D96BA22E1AA9D925317E7E3E6BDF7",
}
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "D31D0529EDE28566CE2D8D435FA264516FA0D299B753D006CE71F2E8DF9C2269"
)
ASSIGN.LEGACY = ASSIGN.ASSIGNMENT.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.ASSIGNMENT.RECORDS.load_records
ASSIGN.root_digest = ASSIGN.ASSIGNMENT.root_digest
ASSIGN.site_digest = ASSIGN.ASSIGNMENT.site_digest
BASE.ASSIGN = ASSIGN
BASE.ENGINE = ASSIGN.ENGINE
BASE.RANKING = ASSIGN.RANKING
BASE._EDGE_CACHE.clear()
BASE._TERMINAL_CACHE.clear()


def selected_terminal_roots(records, source, selector):
    cache_key = (id(records), id(source), selector)
    if cache_key in BASE._TERMINAL_CACHE:
        return BASE._TERMINAL_CACHE[cache_key]
    if selector == BASE.SELECTOR:
        result = tuple((0, terminal) for terminal in BASE.TERMINALS)
    else:
        shape = BASE.RANKING.family_shape(
            BASE.graph_edges_cached(records),
            BASE.graph_edges_cached(source),
            (0, selector),
        )
        leaves = tuple(sorted(shape["candidate_leaves"]))
        BASE.require(len(leaves) >= 7, f"selector family is undersized: {selector}")
        result = leaves[:7]
    BASE._TERMINAL_CACHE[cache_key] = result
    return result


BASE.selected_terminal_roots = selected_terminal_roots


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--bootstrap-output-pin", action="store_true")
    args = parser.parse_args()
    report = BASE.build_report()
    content = BASE.serialized(report)
    output_sha256 = BASE.sha256_bytes(content)
    if BASE.EXPECTED_PUBLIC_FILE_SHA256 is not None:
        BASE.require(
            output_sha256 == BASE.EXPECTED_PUBLIC_FILE_SHA256,
            f"public output hash drifted: {output_sha256}",
        )
    elif not args.bootstrap_output_pin:
        raise BASE.ReviewError("public output hash is not pinned")
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
