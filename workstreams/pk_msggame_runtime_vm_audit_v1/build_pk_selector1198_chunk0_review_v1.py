#!/usr/bin/env python3
"""Validate selector-1198 chunk 0 and emit its source-free checkpoint."""

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
    "selector1198_chunk0_review_base",
)
ASSIGN = load_module(
    WORKSTREAM / "build_pk_selector1198_assignment_v1.py",
    "selector1198_chunk0_review_assignment",
)
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.RECORDS.load_records

BASE.ASSIGNMENT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector1198_assignment_v1.py"
)
BASE.ASSIGNMENT_PATH = (
    DIALOGUE_TMP / "pk_selector1198_assignment.private.v1.json"
)
BASE.ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector1198_assignment_coverage.v1.json"
)
BASE.OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector628_consolidated_checkpoint.private.v1.jsonl"
)
BASE.PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector1198_chunk0_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector1198_chunk0_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector1198_chunk0_review.source_free.v1.json"
)
BASE.SELECTOR = 1198
BASE.TERMINALS = tuple(range(2672, 2679))
BASE.CHUNK_ID = 0
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector1198-chunk0-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector1198-chunk0-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector1198-chunk0-review.source-free.v1"
BASE.METHOD = (
    "post_selector628_selector1198_chunk0_grouped_benefactive_boundary_"
    "same_gap_owned_dependency_and_current_relative_review"
)
BASE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "698AAEB85B9036ABBD4171E41E533EC9A2EDDCF511D9755BF0DD1BF7E60CB0EB"
)
BASE.EXPECTED_ASSIGNMENT_SHA256 = (
    "5EE8DB27C71CFA014DBD4EEF454E69A02FF10B0D1EFD82F14E91CEF487CC090A"
)
BASE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "A20F3757EC0EDC48BC68CD60A844F38E42873D244A2B858DEF3B93679F901A3A"
)
BASE.EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "64F57157C47A72E42CBDBDA59C84AA142519CAAF7D4391983CEFD34362640147"
)
BASE.EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "B12CB46EE9175B2EF889F471B063B5C1235FE02FFE17132F6F756671CBB34E83"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "84A845EC897B23E09BFB5C55052D8D53D618A36459E304C7C40826177A387862"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "28267B6928CBDBF3E98FBB8E13A4733947A4EAC6A2BF04812A848C1091F9B186"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "33F8D888F1ADB835716DCDB8B9E0FAF71D6FF2C7983B9E8076DAA2109DF0F3E3"
)
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "793ACC7D31442340BFFDAD8BC6C2D1A3B184C619AC6B0FFA85739289A35F8E36"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 3,
    "accepted_sites": 9,
    "assembly_branches": 161,
    "blocked_pending_roots": 9,
    "blocked_pending_rows": 32,
    "blocked_sites": 14,
    "decision_rows": 8,
    "promoted_pending_rows": 8,
    "roots": 23,
    "same_gap_branches": 77,
    "shared_override_rows": 0,
    "sites": 23,
    "translation_overrides": 1,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 7,
    "translation_override_and_runtime_promotion": 1,
}
BASE.EXPECTED_DIGESTS = {
    "assembly": "4925C2B6E2AC2BC43BB47682DF152D8620234ADD7DB1FE80A73EAE2D44462C74",
    "decision": "F1C2394E2ED56DB2BE07DC0B8D563B4F851D4A80CA524046B4106181323BE7BE",
    "override": "5B9EEDB9BA140C363A1ED37120B1E4AA84AF8EA57463A5110E211895FFDF62F9",
    "promoted": "F1C2394E2ED56DB2BE07DC0B8D563B4F851D4A80CA524046B4106181323BE7BE",
}
BASE.ASSIGN = ASSIGN
BASE.ENGINE = ASSIGN.ENGINE
BASE.RANKING = ASSIGN.RANKING
BASE._EDGE_CACHE.clear()
BASE._TERMINAL_CACHE.clear()

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
