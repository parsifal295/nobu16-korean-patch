#!/usr/bin/env python3
"""Validate selector-178 chunk 1 and emit its source-free checkpoint."""

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
    "selector178_chunk1_review_base",
)
ASSIGN = load_module(
    WORKSTREAM / "build_pk_selector178_assignment_v1.py",
    "selector178_chunk1_review_assignment",
)

BASE.ASSIGNMENT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector178_assignment_v1.py"
)
BASE.ASSIGNMENT_PATH = (
    DIALOGUE_TMP / "pk_selector178_assignment.private.v1.json"
)
BASE.ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector178_assignment_coverage.v1.json"
)
BASE.OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1198_consolidated_checkpoint.private.v1.jsonl"
)
BASE.PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector178_chunk1_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector178_chunk1_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector178_chunk1_review.source_free.v1.json"
)
BASE.SELECTOR = 178
BASE.TERMINALS = tuple(range(1482, 1489))
BASE.CHUNK_ID = 1
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector178-chunk1-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector178-chunk1-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector178-chunk1-review.source-free.v1"
BASE.METHOD = (
    "post_selector1198_selector178_chunk1_grouped_existential_boundary_"
    "same_gap_owned_dependency_and_current_relative_review"
)
BASE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "83B8B3FAD9E37A891F2E896504DD2555FE840C4AA8CB2A099217A122E07B771A"
)
BASE.EXPECTED_ASSIGNMENT_SHA256 = (
    "C1DE0528BF795DEF68C914A32F9583C2CD084F55491C181329BAE39AE631FACC"
)
BASE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "230A9679566C5D8BD7821F0A4D148CC00A820A16EDFD22C7C5EF2567695C92A8"
)
BASE.EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "A3B6AE01A30C4EC6EFCE171345EFEB81F7FDB9EDFDCAECD90AA4A78AB3296F4F"
)
BASE.EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "F32D97D3BB21B5E092811A6E145BC5E133B592108CE35C1C1E0559DD262D3ED6"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "8E79424B276B3112D92EE4397069FF870525E917443D02C415A6CE86FFE2DEC2"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "74E30E798B82129565518FA04F35DC73220974CFC6E1E7E61BCEC2D8008671DA"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "B197E800335461333198ECE26F5FB2D90AD2FDC5289492C9C374ACC8D7BB4D96"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 10,
    "accepted_sites": 33,
    "assembly_branches": 532,
    "blocked_pending_roots": 18,
    "blocked_pending_rows": 28,
    "blocked_sites": 43,
    "decision_rows": 48,
    "promoted_pending_rows": 24,
    "roots": 75,
    "same_gap_branches": 21,
    "shared_override_rows": 0,
    "sites": 76,
    "translation_overrides": 31,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 17,
    "translation_override_and_runtime_promotion": 7,
    "translation_override_and_verification_renewal": 24,
}
BASE.EXPECTED_DIGESTS = {
    "assembly": "877253E88D0B8EF5172EA0DE599FAB7687F9C34725D5E2EAFADC210AC783A47D",
    "decision": "A734BA98D4839C46D70796AF100243785C9CD3347FE393B552F3572E11AA0EAB",
    "override": "4321D21F16DE58019AE1BA5D56BCF262A0E2FD6AF96CE78E9FBF2959955D0E5E",
    "promoted": "C48D5F4751B9E54D5033554D34F2BBAC6C76C2835AB04975B4882C22A5E64D97",
}
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "0ACA9CA2E78B24E5E1CDE78A6625CA9FF7821BF330DF0A3A17529214FEDAF650"
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
