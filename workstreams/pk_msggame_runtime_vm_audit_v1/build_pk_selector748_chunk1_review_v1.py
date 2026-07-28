#!/usr/bin/env python3
"""Validate selector-748 chunk 1 and emit its source-free checkpoint."""

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
    "selector748_chunk1_review_base",
)
ASSIGN = load_module(
    WORKSTREAM / "build_pk_selector748_assignment_v1.py",
    "selector748_chunk1_review_assignment",
)

BASE.ASSIGNMENT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector748_assignment_v1.py"
)
BASE.ASSIGNMENT_PATH = (
    DIALOGUE_TMP / "pk_selector748_assignment.private.v1.json"
)
BASE.ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector748_assignment_coverage.v1.json"
)
BASE.OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector550_consolidated_checkpoint.private.v1.jsonl"
)
BASE.PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector748_chunk1_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector748_chunk1_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector748_chunk1_review.source_free.v1.json"
)
BASE.SELECTOR = 748
BASE.TERMINALS = tuple(range(2161, 2168))
BASE.CHUNK_ID = 1
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector748-chunk1-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector748-chunk1-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector748-chunk1-review.source-free.v1"
BASE.METHOD = (
    "post_selector550_selector748_chunk1_fresh_semantic_seven_branch_"
    "same_gap_owned_dependency_and_current_relative_review"
)
BASE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "E39ED4738833FB56680E81E5B06A68F04472BABE7279D92CB608A40DB7D17CF5"
)
BASE.EXPECTED_ASSIGNMENT_SHA256 = (
    "CE5FBC60D33426695E86FBC8E76205E99917956EE55DBF10375B8933CE91B17E"
)
BASE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "68615492AC049EF3B87D5840ACDB67A8E05D6E8F2EED63CBC89905A8DF5515B2"
)
BASE.EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "F2CB7279F71D33CFA9D73BD4A6DA8E7E90692047F8ECF1D521FD70512D71846E"
)
BASE.EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "383D540C26F63C07E495446932D884CB9A3094CF160BB7428A1AB8680BA55A36"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "DB86BB97C491AB0AFDBE58E99A29B19EFBE1342DDDF23E6A310539F3092B63DF"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "15C3BF1B4CC2E29020E5A8A6F40669555B54EEE57B04C3F7F77DF3AC680CFB93"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "A1FA037FCB59C62550E2E98A1AA96C52AF81E5B880FFC29FD3E116F678D26CCE"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 8,
    "accepted_sites": 22,
    "assembly_branches": 238,
    "blocked_pending_roots": 8,
    "blocked_pending_rows": 29,
    "blocked_sites": 12,
    "decision_rows": 36,
    "promoted_pending_rows": 18,
    "roots": 33,
    "same_gap_branches": 63,
    "sites": 34,
    "translation_overrides": 30,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 6,
    "translation_override_and_runtime_promotion": 12,
    "translation_override_and_verification_renewal": 18,
}
BASE.EXPECTED_DIGESTS = {
    "assembly": "7AB3070C30DE208A627B34FC4B1F2E85A46BB96C415CF35508EBFC3E623B4399",
    "decision": "56587BE305567B449074F00DED64E925235C161DB8F0E7AB3B1FA194FC54F896",
    "override": "5E363B60D2F86CE61F2652F8EEE895D6267AF167671F80148E8FDA1DAC0B56D3",
    "promoted": "2C00E0D774ADB123D5B1A2EFCC51272F3E04B86FF013651A4DE0C6C1A11A103C",
}
BASE.ASSIGN = ASSIGN
BASE.ENGINE = ASSIGN.ENGINE
BASE.RANKING = ASSIGN.RANKING
BASE._EDGE_CACHE.clear()
BASE._TERMINAL_CACHE.clear()

EXPECTED_PUBLIC_FILE_SHA256 = (
    "B13A18A0115B5B89405BA358967D8100F16FCA66BEACB437C52A5C5F4B6014E3"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = BASE.build_report()
    content = BASE.serialized(report)
    output_sha256 = BASE.sha256_bytes(content)
    if EXPECTED_PUBLIC_FILE_SHA256:
        BASE.require(
            output_sha256 == EXPECTED_PUBLIC_FILE_SHA256,
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
        "reviewed_candidate_sha256": BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256,
        "status": "PASS",
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
