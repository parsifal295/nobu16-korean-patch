#!/usr/bin/env python3
"""Validate selector-1090 chunk 0 and emit its source-free checkpoint."""

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
    "selector1090_chunk0_review_base",
)
ASSIGN_WRAPPER = load_module(
    WORKSTREAM / "build_pk_selector1090_assignment_v1.py",
    "selector1090_chunk0_review_assignment_wrapper",
)
ASSIGN = ASSIGN_WRAPPER.ASSIGNMENT
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.RECORDS.load_records

BASE.ASSIGNMENT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector1090_assignment_v1.py"
)
BASE.ASSIGNMENT_PATH = (
    DIALOGUE_TMP / "pk_selector1090_assignment.private.v1.json"
)
BASE.ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector1090_assignment_coverage.v1.json"
)
BASE.OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector178_consolidated_checkpoint.private.v1.jsonl"
)
BASE.PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector1090_chunk0_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector1090_chunk0_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector1090_chunk0_review.source_free.v1.json"
)
BASE.SELECTOR = 1090
BASE.TERMINALS = tuple(range(2574, 2581))
BASE.CHUNK_ID = 0
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector1090-chunk0-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector1090-chunk0-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector1090-chunk0-review.source-free.v1"
BASE.METHOD = (
    "post_selector178_selector1090_chunk0_grouped_ha_i_stem_"
    "same_gap_and_current_relative_review"
)
BASE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "3E1D9AC82DB1BF6CA842AD47C2C5227A6F63BC80DCEA6C8553B1267DB1F15061"
)
BASE.EXPECTED_ASSIGNMENT_SHA256 = (
    "B256F67F1A584D8895BA7BDCCA764338A9F9A08B12C78F00579703035AC090FA"
)
BASE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "917E3C6087EE4593EEEA0529A2FE88E6D68FE16A69CBC61A0476113EE719EE9B"
)
BASE.EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "A11DC8F5F0BAA9532DCB7737AFAFC8732506AC2F4E4B6479B44056CF9958015D"
)
BASE.EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "86180B30A40AF71F3C4D417DEED2D4184167003A45C215BFA262722F478D0789"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "4664A9C4B009C6DF3EE52AE8B9D6881CB795B3E46987ED669306EFC006D1D7D3"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "D89D47866F7FA9D34F68814219A00840921C130E062EA5DE80F95063B9E96E7F"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "77964F922B0DDC4E66CEFD7AD5113E0997FE25390B16645AAF498CC898D496E6"
)
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "C390C034B0C115E60440616B8DABC289F65CB28D7F32410F4C774A34E7949833"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 15,
    "accepted_sites": 36,
    "assembly_branches": 329,
    "blocked_pending_roots": 4,
    "blocked_pending_rows": 8,
    "blocked_sites": 11,
    "decision_rows": 49,
    "promoted_pending_rows": 33,
    "roots": 45,
    "same_gap_branches": 14,
    "shared_override_rows": 0,
    "sites": 47,
    "translation_overrides": 20,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 29,
    "translation_override_and_runtime_promotion": 4,
    "translation_override_and_verification_renewal": 16,
}
BASE.EXPECTED_DIGESTS = {
    "assembly": "CACDF22EC282C650AFF81A9A909E3FE6D183505548A2E963A1F5447732F027F7",
    "decision": "D635AC209634B34B5065E14EF09E22015ECCE5FDC5EF5A782BD653D7D35B3BA3",
    "override": "35CB7E12F00D41D3B9DE9957EFE1209731A206550A64C0CF7B9CFA2371679698",
    "promoted": "BD8C463525172F2BBB15FAD8D3EA9B94D480C627BB2AC398E33A7947817C4709",
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
