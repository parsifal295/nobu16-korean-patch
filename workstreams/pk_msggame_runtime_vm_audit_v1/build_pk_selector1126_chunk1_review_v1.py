#!/usr/bin/env python3
"""Validate selector-1126 chunk 1 and emit its source-free checkpoint."""

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
    "selector1126_chunk1_review_base",
)
ASSIGN = load_module(
    WORKSTREAM / "build_pk_selector1126_assignment_v1.py",
    "selector1126_chunk1_review_assignment",
)

BASE.ASSIGNMENT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector1126_assignment_v1.py"
)
BASE.ASSIGNMENT_PATH = (
    DIALOGUE_TMP / "pk_selector1126_assignment.private.v1.json"
)
BASE.ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector1126_assignment_coverage.v1.json"
)
BASE.OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector748_consolidated_checkpoint.private.v1.jsonl"
)
BASE.PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector1126_chunk1_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector1126_chunk1_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector1126_chunk1_review.source_free.v1.json"
)
BASE.SELECTOR = 1126
BASE.TERMINALS = tuple(range(2616, 2623))
BASE.CHUNK_ID = 1
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector1126-chunk1-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector1126-chunk1-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector1126-chunk1-review.source-free.v1"
BASE.METHOD = (
    "post_selector748_selector1126_chunk1_fresh_semantic_seven_branch_"
    "same_gap_owned_dependency_and_current_relative_review"
)
BASE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "9EFDF4FD9CD8330A97AC59E44B4364F9EE965549FEC24F65C5AA79295EDA6ACE"
)
BASE.EXPECTED_ASSIGNMENT_SHA256 = (
    "6E5CC3EB27553DC7ECA4AF5095D3F7AB5FAEDBBC5D260A33D635F8E8F407BEE2"
)
BASE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "83B6F9CA80DF3400ABEAC5DF6BE8E2335FF97A8F407FAE0854A14BCD70C7BFA3"
)
BASE.EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "05D9C79515E8B161CD469FFEC5C340F54BE9BB94BFBA8F725B8DFC025DE49E76"
)
BASE.EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "EE1AD1847FE6D1EF02F907169BF08562699AEA500074011BEEB0C060EBEA590C"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "B4CE98AE51099EAF185D21999C3979D3902130A632EC31D6E865D0202E2BDF62"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "903B515128E94FE263430FAF7EECC51759A0DD132211F3C3047E5DAA6D16D9A6"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "5731304B4EBC046F51BB907615DC03A4835AAB37E7FA8EDC5763B474A27458FE"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 18,
    "accepted_sites": 25,
    "assembly_branches": 266,
    "blocked_pending_roots": 8,
    "blocked_pending_rows": 19,
    "blocked_sites": 13,
    "decision_rows": 49,
    "promoted_pending_rows": 36,
    "roots": 38,
    "same_gap_branches": 21,
    "shared_override_rows": 0,
    "sites": 38,
    "translation_overrides": 40,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 9,
    "translation_override_and_runtime_promotion": 27,
    "translation_override_and_verification_renewal": 13,
}
BASE.EXPECTED_DIGESTS = {
    "assembly": "BF6FC87BBA63C514415ADFE3E2E849629A37992FE092B4BC2CEEF9399C7CB64A",
    "decision": "E374CD0A3560CFBD34D66F9ACC99B4CE9D1316D6EAC527E3CC6F20C1296B8944",
    "override": "CF02CA9329B775986F10617127173670BE4ADAAD2E3887FE2F71C5A948B2BB3E",
    "promoted": "7FD4EA46B5E6438AB50F8364FB1C2D025DE9D4A00270A035163E448601E87FC6",
}
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
BASE.ASSIGN = ASSIGN
BASE.ENGINE = ASSIGN.ENGINE
BASE.RANKING = ASSIGN.RANKING
BASE._EDGE_CACHE.clear()
BASE._TERMINAL_CACHE.clear()

EXPECTED_PUBLIC_FILE_SHA256 = (
    "9523656C069465E2CFCBBAB349C62B3012FEC7F54416D33D0384C07196FD1479"
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
