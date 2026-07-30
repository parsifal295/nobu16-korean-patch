#!/usr/bin/env python3
"""Validate selector-142 chunk 1 and emit its source-free checkpoint."""

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
    "selector142_chunk1_review_base",
)
ASSIGN = load_module(
    WORKSTREAM / "build_pk_selector142_assignment_v1.py",
    "selector142_chunk1_review_assignment",
)

BASE.ASSIGNMENT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector142_assignment_v1.py"
)
BASE.ASSIGNMENT_PATH = (
    DIALOGUE_TMP / "pk_selector142_assignment.private.v1.json"
)
BASE.ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector142_assignment_coverage.v1.json"
)
BASE.OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1126_consolidated_checkpoint.private.v1.jsonl"
)
BASE.PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector142_chunk1_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector142_chunk1_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector142_chunk1_review.source_free.v1.json"
)
BASE.SELECTOR = 142
BASE.TERMINALS = tuple(range(1440, 1447))
BASE.CHUNK_ID = 1
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector142-chunk1-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector142-chunk1-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector142-chunk1-review.source-free.v1"
BASE.METHOD = (
    "post_selector1126_selector142_chunk1_fresh_semantic_seven_branch_"
    "same_gap_owned_dependency_and_current_relative_review"
)
BASE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "AE1428FBF34BA042F1588E89DAA02623752D791BCD498687B9AD8595ED4BD7FF"
)
BASE.EXPECTED_ASSIGNMENT_SHA256 = (
    "3F22858009367851ADCFBC99E4620CCD4676043FD22755DBF48A50571B7E4C7E"
)
BASE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "D0EA381E8491BDD34E7E9D30BFCAA027CCBCA197468EB5AFF6F76B5F4D892438"
)
BASE.EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "3198DC9F7A06809636D0C43F5740A65B5D4C50E7226D53AA7C52B7D893EFA06E"
)
BASE.EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "6C9F52DB04C2FE46CF14D40CD1CED03E4638D2201664F232895990C713798B9D"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "3668346AF7B6070C1A25529ED0720B2349F0D18EEB8C535E3E26E2F8522307BF"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "B25D15DB919FC4E3CF3A68E7C10938F581C233F04DA111F1C8D0ECA0A3F86D62"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "E58467EFF3233478E74B7D4F5034D43DBA6FE609A5A04260B15F2EB0316603E0"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 13,
    "accepted_sites": 35,
    "assembly_branches": 252,
    "blocked_pending_roots": 1,
    "blocked_pending_rows": 2,
    "blocked_sites": 1,
    "decision_rows": 53,
    "promoted_pending_rows": 30,
    "roots": 36,
    "same_gap_branches": 0,
    "shared_override_rows": 0,
    "sites": 36,
    "translation_overrides": 43,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 10,
    "translation_override_and_runtime_promotion": 20,
    "translation_override_and_verification_renewal": 23,
}
BASE.EXPECTED_DIGESTS = {
    "assembly": "C897E254C7C087C02CA8E0473C541406F94465FDD99257D75EA27AD827419810",
    "decision": "055EAB61517D04A8C2E2DC081FC1C57B72FA05C93820875D6E08E2513E82DA4F",
    "override": "260E627905005C9AA816DE769FEAF5758C2C3357D74AF31CD066B6F519DA5524",
    "promoted": "188CFA705C971FC1805E7292700175E62C606F31CAF667612E35F2E4A419829C",
}
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.BASE.load_records
BASE.ASSIGN = ASSIGN
BASE.ENGINE = ASSIGN.ENGINE
BASE.RANKING = ASSIGN.RANKING
BASE._EDGE_CACHE.clear()
BASE._TERMINAL_CACHE.clear()

EXPECTED_PUBLIC_FILE_SHA256 = (
    "966B8005C2BE5D271C7AD8D710B0A47018378B8E1CFAF2B37034539FD9FAC161"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = BASE.build_report()
    content = BASE.serialized(report)
    output_sha256 = BASE.sha256_bytes(content)
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
