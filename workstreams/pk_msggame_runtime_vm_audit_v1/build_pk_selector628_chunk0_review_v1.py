#!/usr/bin/env python3
"""Validate selector-628 chunk 0 and emit its source-free checkpoint."""

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
    "selector628_chunk0_review_base",
)
ASSIGN = load_module(
    WORKSTREAM / "build_pk_selector628_assignment_v1.py",
    "selector628_chunk0_review_assignment",
)
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.RECORDS.load_records

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
    / "pk_selector628_chunk0_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector628_chunk0_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector628_chunk0_review.source_free.v1.json"
)
BASE.SELECTOR = 628
BASE.TERMINALS = tuple(range(2021, 2028))
BASE.CHUNK_ID = 0
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector628-chunk0-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector628-chunk0-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector628-chunk0-review.source-free.v1"
BASE.METHOD = (
    "post_selector514_selector628_chunk0_fast_grouped_boundary_"
    "same_gap_and_current_relative_review"
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
    "47A984E2BE18C7B8C84F9E4ADA888C5EA6AB6C6809F33517F99BE86D7F7DDB44"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "C08808F2E9E576D9990BEC349707B64EFAF0A06436C808C57B207D9A5742AC97"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "623C6EE2BDC25B13680C353C97847C3AC646C4B2B222A51F0F242B7A1CC2E093"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "E33405B526764E4A346A766F9E4075531FFA7789906A01F27558071F5E5FA75A"
)
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "6B217383997591962EEC8B166302809E18DB674E3CCC344C68CB9B5B0CD2B11C"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 8,
    "accepted_sites": 36,
    "assembly_branches": 511,
    "blocked_pending_roots": 11,
    "blocked_pending_rows": 21,
    "blocked_sites": 37,
    "decision_rows": 30,
    "promoted_pending_rows": 29,
    "roots": 73,
    "same_gap_branches": 21,
    "shared_override_rows": 0,
    "sites": 73,
    "translation_overrides": 9,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 21,
    "translation_override_and_runtime_promotion": 8,
    "translation_override_and_verification_renewal": 1,
}
BASE.EXPECTED_DIGESTS = {
    "assembly": "2E7227A61FC378BC25C783A215E697B68234E4FCB4ACFA947155461FBA0AC94D",
    "decision": "5099669106F73CE7C392A98453E1293BE27E3C6B10858ADA47133B9330D30564",
    "override": "A5B52357A6FDA82100E0EA420CA570B2AB32A80022E0FF2F6C58B8206C2474F4",
    "promoted": "E6D8217A159E253F7B30409D1034051C7B1000214AEBF20D08297B6EAF0CCD30",
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
