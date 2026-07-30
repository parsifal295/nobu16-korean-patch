#!/usr/bin/env python3
"""Validate selector-1090 chunk 1 and emit its source-free checkpoint."""

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
    "selector1090_chunk1_review_base",
)
ASSIGN = load_module(
    WORKSTREAM / "build_pk_selector1090_assignment_v1.py",
    "selector1090_chunk1_review_assignment",
)

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
    / "pk_selector1090_chunk1_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector1090_chunk1_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector1090_chunk1_review.source_free.v1.json"
)
BASE.SELECTOR = 1090
BASE.TERMINALS = tuple(range(2574, 2581))
BASE.CHUNK_ID = 1
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector1090-chunk1-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector1090-chunk1-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector1090-chunk1-review.source-free.v1"
BASE.METHOD = (
    "post_selector178_selector1090_chunk1_grouped_oda_stem_boundary_"
    "same_gap_owned_dependency_and_current_relative_review"
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
    "D567CBD70E2491D4FE4B90678F441C7C8168830199F9088AFCB85A75F7E42857"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "BA0B228198517C8B9207A699356E8E9C890E58EA76F41CDF28424BCA21129835"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "D89D47866F7FA9D34F68814219A00840921C130E062EA5DE80F95063B9E96E7F"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "F74B72F4D56B2A8B4D0EC34A92F077E5462E979834ECBBDEF39F86504856DA7B"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 15,
    "accepted_sites": 36,
    "assembly_branches": 343,
    "blocked_pending_roots": 7,
    "blocked_pending_rows": 8,
    "blocked_sites": 13,
    "decision_rows": 40,
    "promoted_pending_rows": 31,
    "roots": 47,
    "same_gap_branches": 21,
    "shared_override_rows": 0,
    "sites": 49,
    "translation_overrides": 13,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 27,
    "translation_override_and_runtime_promotion": 4,
    "translation_override_and_verification_renewal": 9,
}
BASE.EXPECTED_DIGESTS = {
    "assembly": "E6ABD19B0CA4B4242099DA4B3C011EE5CA9ABB6830ED16AC52A6EA354E953983",
    "decision": "DF5FA96AEE02FAA918DC409B65FD44EFED4751557FC503D005E96EEB4560DF5D",
    "override": "D70B9B50718096EB944157DC72180033DE60FB73EC57B9978F7239DFFA292B9E",
    "promoted": "2B1CAED9403BE735B487F582E03974A5123BDCF1FC77421F292665CC9EF84F7A",
}
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "29A3743CD7EAB0C3C4927A378615D6BB89103753608948E76E1766F3FD0E10B3"
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
