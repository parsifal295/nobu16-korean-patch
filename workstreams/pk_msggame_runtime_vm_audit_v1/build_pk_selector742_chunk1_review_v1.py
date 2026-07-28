#!/usr/bin/env python3
"""Validate selector-742 chunk 1 and emit its source-free checkpoint."""

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
    "selector742_chunk1_review_base",
)
ASSIGN = load_module(
    WORKSTREAM / "build_pk_selector742_assignment_v1.py",
    "selector742_chunk1_review_assignment",
)

BASE.ASSIGNMENT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector742_assignment_v1.py"
)
BASE.ASSIGNMENT_PATH = (
    DIALOGUE_TMP / "pk_selector742_assignment.private.v1.json"
)
BASE.ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector742_assignment_coverage.v1.json"
)
BASE.OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector760_consolidated_checkpoint.private.v1.jsonl"
)
BASE.PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector742_chunk1_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector742_chunk1_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector742_chunk1_review.source_free.v1.json"
)
BASE.SELECTOR = 742
BASE.TERMINALS = tuple(range(2154, 2161))
BASE.CHUNK_ID = 1
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector742-chunk1-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector742-chunk1-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector742-chunk1-review.source-free.v1"
BASE.METHOD = (
    "post_selector760_selector742_chunk1_compatible_absence_terminal_"
    "single_pass_recut_and_residual_block_review"
)
BASE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "615941B31D7251AF6F27BC8B801CFBA130C09D5A18662763DD09C09850CC3B91"
)
BASE.EXPECTED_ASSIGNMENT_SHA256 = (
    "155ADFBB8BB8F4267743B54A0085FCBA91B546F345D0CE08BF6CAE30A9065BD7"
)
BASE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "B6686C33345A4990FA8DADAE5FA59DE3A97B15497D6AF4133CB524123506C6B9"
)
BASE.EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "797D27314E8E168E1F2BACF9174E7246B83BF6DEDB0AC3B6C925D6D076CAC8C3"
)
BASE.EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "6544C936F5DFDF362EED2C5F8B7E3DF4F4A23CC0B97B8B96AB65612E2AE65901"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "101CEC8C42CDAB15688FD2592E363352A972A9DB6403888B0FAAC35A4A1837F8"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "03D128438A4A79F1C4C59D46996D93E8DBD10ECAF707E18E0A46A0B3AF29A2F5"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "BCA693F86DEE850F95996243CB5FFA3DBA56A4F58750800FFE8253F9FC2ACFBB"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 2,
    "accepted_sites": 2,
    "assembly_branches": 203,
    "blocked_pending_roots": 13,
    "blocked_pending_rows": 30,
    "blocked_sites": 27,
    "decision_rows": 6,
    "promoted_pending_rows": 6,
    "roots": 29,
    "same_gap_branches": 7,
    "sites": 29,
    "translation_overrides": 3,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 3,
    "translation_override_and_runtime_promotion": 3,
}
BASE.EXPECTED_DIGESTS = {
    "assembly": "4DA0801DC4CC79F7CEB9FC6C612897663C013CE434FE7BB33A6807188BF9BC51",
    "decision": "8E45988085322D3E7FC8F9E2403107F2F757AA2AD94C813A85A551C91306AAD7",
    "override": "B19E80EBD22FB9C21F544FC3A2C9F73CB168910AB1A5C17E59E395021AF7A633",
    "promoted": "8E45988085322D3E7FC8F9E2403107F2F757AA2AD94C813A85A551C91306AAD7",
}
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "26C62F210BFE7EC9D2A253E58AFF72269F6F392390B5B5CD34D616FE24D570B3"
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
