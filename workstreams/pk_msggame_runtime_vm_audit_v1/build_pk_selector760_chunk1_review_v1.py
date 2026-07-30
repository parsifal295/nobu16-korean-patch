#!/usr/bin/env python3
"""Validate selector-760 chunk 1 and emit its source-free checkpoint."""

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
    "selector760_chunk1_review_base",
)
ASSIGN = load_module(
    WORKSTREAM / "build_pk_selector760_assignment_v1.py",
    "selector760_chunk1_review_assignment",
)

BASE.ASSIGNMENT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector760_assignment_v1.py"
)
BASE.ASSIGNMENT_PATH = (
    DIALOGUE_TMP / "pk_selector760_assignment.private.v1.json"
)
BASE.ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector760_assignment_coverage.v1.json"
)
BASE.OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1090_consolidated_checkpoint.private.v1.jsonl"
)
BASE.PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector760_chunk1_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector760_chunk1_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector760_chunk1_review.source_free.v1.json"
)
BASE.SELECTOR = 760
BASE.TERMINALS = tuple(range(2175, 2182))
BASE.CHUNK_ID = 1
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector760-chunk1-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector760-chunk1-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector760-chunk1-review.source-free.v1"
BASE.METHOD = (
    "post_selector1090_selector760_chunk1_single_control_rewrite_"
    "same_gap_residual_block_and_current_relative_review"
)
BASE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "FBE5625F1480AB8FD5C65E349F961F6336A1EA9A4F7C2C74E9579F092B2ACE5B"
)
BASE.EXPECTED_ASSIGNMENT_SHA256 = (
    "2D14D2E186E8E4A23B0BC1591B669E76B701071CDFB1A8ACBF93FA15B018C6AB"
)
BASE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "7DBCAF6DF39C482E6958390A944BF3941576B69F469361129FD46715E89648F5"
)
BASE.EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "CDF7539F8E6A6F0D024A7357854A0AFE45E91F3CBD144822E1DEF8730A9A373F"
)
BASE.EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "0C4A803CF5776E39953CC7983B4F91C0E728EF91C0E3C488FF7C9C62B376C51D"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "D5C8D20A7F79036C8836EB11762C9E77EBC21AC8B2C57CB7AD2327DEE772B667"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "396A8DF109A0693C439F990049477F5DE6E10720854D73057F3DFA1702002CCF"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "03D128438A4A79F1C4C59D46996D93E8DBD10ECAF707E18E0A46A0B3AF29A2F5"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 7,
    "accepted_sites": 9,
    "assembly_branches": 112,
    "blocked_pending_roots": 4,
    "blocked_pending_rows": 9,
    "blocked_sites": 7,
    "decision_rows": 30,
    "promoted_pending_rows": 27,
    "roots": 16,
    "same_gap_branches": 49,
    "sites": 16,
    "translation_overrides": 14,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 16,
    "translation_override_and_runtime_promotion": 11,
    "translation_override_and_verification_renewal": 3,
}
BASE.EXPECTED_DIGESTS = {
    "assembly": "4D90D683FF3A0E2036A04BAD5673BE922C3FCE7A686FE2B5A8DEDA75894D0F1C",
    "decision": "9B139103D60BBCD09810189A92A212E4B84FE5421ECF8B4F77E4B3495C19FB56",
    "override": "58BA39FCD74CD771C80CDADA8EA0BFFAC82EDB1542DD07AED09C59ED62BAFE4F",
    "promoted": "88D9D582B9DD4F45A154BD83C356DB0C91B1CCE852D12FE34ED252814DA64126",
}
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "59081F5586BC4F9B5DA57363071A40677AACF449100F15BF74833079ACCF67E4"
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
