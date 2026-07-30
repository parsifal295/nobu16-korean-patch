#!/usr/bin/env python3
"""Validate selector-1198 chunk 1 and emit its source-free checkpoint."""

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
    "selector1198_chunk1_review_base",
)
ASSIGN = load_module(
    WORKSTREAM / "build_pk_selector1198_assignment_v1.py",
    "selector1198_chunk1_review_assignment",
)

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
    / "pk_selector1198_chunk1_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector1198_chunk1_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector1198_chunk1_review.source_free.v1.json"
)
BASE.SELECTOR = 1198
BASE.TERMINALS = tuple(range(2672, 2679))
BASE.CHUNK_ID = 1
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector1198-chunk1-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector1198-chunk1-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector1198-chunk1-review.source-free.v1"
BASE.METHOD = (
    "post_selector628_selector1198_chunk1_grouped_benefactive_boundary_"
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
    "4CD586C905B7D45A03E51B9AA7C99F0C62D9480CEE9DFB3757B2D6F13A014602"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "B2B7CC75AB60AC917900F716ACBBD9D58C07FE321ECCD13333180FCFC244A89B"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "28267B6928CBDBF3E98FBB8E13A4733947A4EAC6A2BF04812A848C1091F9B186"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "D64484DF3DC68D9F184E22910C79C2723E83CCF54D4D22B29763C2CB3D853409"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 6,
    "accepted_sites": 13,
    "assembly_branches": 161,
    "blocked_pending_roots": 7,
    "blocked_pending_rows": 26,
    "blocked_sites": 10,
    "decision_rows": 19,
    "promoted_pending_rows": 17,
    "roots": 23,
    "same_gap_branches": 63,
    "shared_override_rows": 0,
    "sites": 23,
    "translation_overrides": 5,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 14,
    "translation_override_and_runtime_promotion": 3,
    "translation_override_and_verification_renewal": 2,
}
BASE.EXPECTED_DIGESTS = {
    "assembly": "8474CB8EB38DA48F7027CF363ED84601AA443CA4639AB4AFCA58AEC0C7D100B0",
    "decision": "EE72DB6A4DF09AB3D0BD4E1C990C5D65AA4310BE04ADFF77E7F0EB3F9613BC1F",
    "override": "20389217C93A62EE76AFD839A6D4321C444B79FC4FEBB13E275A3A9F8513DFA0",
    "promoted": "3CAA71587BFBC57CA82228B06370FA03ED6949460FCE59761BF46C604B41282C",
}
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "EEC95385EFC742956B08630B0B82FCE8238D9FB90EB99052DA50BAE3F44FEC31"
)
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.RECORDS.load_records
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
