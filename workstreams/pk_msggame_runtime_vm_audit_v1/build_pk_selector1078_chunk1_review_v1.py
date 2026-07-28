#!/usr/bin/env python3
"""Validate selector-1078 chunk 1 and emit its source-free checkpoint."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


CORE = load_module(
    WORKSTREAM / "build_pk_selector550_chunk1_review_v1.py",
    "selector1078_chunk1_review_core",
)
ASSIGNMENT = load_module(
    WORKSTREAM / "build_pk_selector1078_assignment_v1.py",
    "selector1078_chunk1_review_assignment",
)
ASSIGN = ASSIGNMENT.ASSIGNMENT
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.RECORDS.load_records

ASSIGNMENT_PATH = DIALOGUE_TMP / "pk_selector1078_assignment.private.v1.json"
PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP / "semantic_overrides"
    / "pk_selector1078_chunk1_review_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector1078_chunk1_review_evidence.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector1078_chunk1_review.source_free.v1.json"
)
METHOD = (
    "post_selector268_selector1078_chunk1_single_pass_fresh_exact_"
    "bound_negative_register_review"
)
PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector1078-chunk1-review-decision.private.v1"
)
PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector1078-chunk1-review-evidence.private.v1"
)
PUBLIC_SCHEMA = "nobu16.kr.pk-selector1078-chunk1-review.source-free.v1"
EXPECTED_COUNTS = {
    "accepted_pending_roots": 4,
    "accepted_sites": 4,
    "assembly_branches": 154,
    "blocked_pending_roots": 6,
    "blocked_pending_rows": 8,
    "blocked_sites": 18,
    "decision_rows": 10,
    "jp_only_sites": 11,
    "multi_control_blocked_sites": 4,
    "non_display_actions": 0,
    "owned_overlap_roots": 0,
    "prior_assembly_evidence_pending_rows": 17,
    "prior_assembly_evidence_roots": 10,
    "promoted_pending_rows": 10,
    "rewrite_attempt_roots": 4,
    "roots": 22,
    "same_gap_branches": 28,
    "sites": 22,
    "source_only_actions": 0,
    "translation_overrides": 5,
    "verification_renewal_rows": 0,
}
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 5,
    "translation_override_and_runtime_promotion": 5,
}
EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "3D8332E789CD35560E78A68B153F25E20E500FF681E6DB38515240204DBE8551"
)
EXPECTED_ASSIGNMENT_SHA256 = (
    "6637FE722BF183489E8BE32473A67C5B40FDD2BB25DB080D6C5B429111A90F4D"
)
EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "0B01BDE88CE6CF091E07720FB5C83772F2C7EA7E9139C85EEFF7788F92864EA3"
)
EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "0936BD050D1BB529848AD861B951D178A3521C086BC41027C4ED4A5B4FBC79C3"
)
EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "3FA2BF9BE3D62F980CF6BB90558999C921D68BDC97E470103050BEE3703C3429"
)
EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "8D3C1A367AC82F23EBEAA05F4DEB973D3C5FD453437EBB3B3E1CB64CA732B99C"
)
EXPECTED_CANDIDATE_SHA256 = (
    "92B86808931C1FD34320BC5A9BFD05B7AD704FA9392534FF8DE8F6293F413DAD"
)
EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "1CDC655B3841BDA81984CB6E1A58D9095F8D8FB58AABB154684C9CABFC6E0859"
)
EXPECTED_LIVE_STEAM_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_TERMINAL_CANDIDATE_SHA256 = (
    "51C604DD377D15C87B104D243917530C2F1FBB2956C4770AC77451C9ED249219"
)
EXPECTED_TERMINAL_CURRENT_SHA256 = (
    "D530A0A4D56E02144371B1A8299A42438CC4372773D1D0A23B9688E18E560AA9"
)
EXPECTED_TERMINAL_SOURCE_SHA256 = (
    "2CFD3803511E2C4BCDDDFC25768645ED2E90CB8CACB750FC27F82742E9CA3793"
)
EXPECTED_DIGESTS = {
    "assembly": "7F23359F8106E94A382B1CDDE8212295CB7D99C09C84E3F8A3FC112FDE3268DB",
    "decision": "9C64CF7E424ABD9930D887DA6F4406DC3AA41C95DFA9CC9B56E171C1F8E61481",
    "override": "6327082388E32235078AB318F4B4D902AE9D3D96A80F5FA1B871CC4F0B10BB77",
    "promoted": "9C64CF7E424ABD9930D887DA6F4406DC3AA41C95DFA9CC9B56E171C1F8E61481",
}
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "8844E5A29E3FD00735CE26A2FE2EE226A4C732F765D524613391040DC2CDE45D"
)


def configure_core() -> None:
    CORE.ASSIGNMENT_BUILDER_PATH = (
        WORKSTREAM / "build_pk_selector1078_assignment_v1.py"
    )
    CORE.ASSIGNMENT_PATH = ASSIGNMENT_PATH
    CORE.ASSIGNMENT_PUBLIC_PATH = (
        WORKSTREAM / "public" / "pk_selector1078_assignment_coverage.v1.json"
    )
    CORE.OFFICIAL_LEDGER_PATH = (
        DIALOGUE_TMP
        / "runtime_vm_integrated.post_selector268_consolidated_checkpoint.private.v1.jsonl"
    )
    CORE.PRIVATE_DECISIONS_PATH = PRIVATE_DECISIONS_PATH
    CORE.PRIVATE_EVIDENCE_PATH = PRIVATE_EVIDENCE_PATH
    CORE.DEFAULT_PUBLIC_OUTPUT = DEFAULT_PUBLIC_OUTPUT
    CORE.SELECTOR = 1078
    CORE.TERMINALS = tuple(range(2560, 2567))
    CORE.CHUNK_ID = 1
    CORE.PRIVATE_DECISION_SCHEMA = PRIVATE_DECISION_SCHEMA
    CORE.PRIVATE_EVIDENCE_SCHEMA = PRIVATE_EVIDENCE_SCHEMA
    CORE.PUBLIC_SCHEMA = PUBLIC_SCHEMA
    CORE.METHOD = METHOD
    CORE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = EXPECTED_ASSIGNMENT_BUILDER_SHA256
    CORE.EXPECTED_ASSIGNMENT_SHA256 = EXPECTED_ASSIGNMENT_SHA256
    CORE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = EXPECTED_ASSIGNMENT_PUBLIC_SHA256
    CORE.EXPECTED_OFFICIAL_LEDGER_SHA256 = EXPECTED_OFFICIAL_LEDGER_SHA256
    CORE.EXPECTED_PRIVATE_DECISIONS_SHA256 = EXPECTED_PRIVATE_DECISIONS_SHA256
    CORE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = EXPECTED_PRIVATE_EVIDENCE_SHA256
    CORE.EXPECTED_CANDIDATE_SHA256 = EXPECTED_CANDIDATE_SHA256
    CORE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = EXPECTED_REVIEWED_CANDIDATE_SHA256
    CORE.EXPECTED_LIVE_STEAM_SHA256 = EXPECTED_LIVE_STEAM_SHA256
    CORE.EXPECTED_COUNTS = EXPECTED_COUNTS
    CORE.EXPECTED_ACTION_COUNTS = EXPECTED_ACTION_COUNTS
    CORE.EXPECTED_DIGESTS = EXPECTED_DIGESTS
    CORE.ASSIGN = ASSIGN
    CORE.ENGINE = ASSIGN.ENGINE
    CORE.RANKING = ASSIGN.RANKING
    CORE._EDGE_CACHE.clear()
    CORE._TERMINAL_CACHE.clear()


def terminal_info(records: Any) -> tuple[list[int], str]:
    values = [
        CORE.first_literal(records, (0, terminal))
        for terminal in CORE.TERMINALS
    ]
    return (
        sorted(Counter(values).values()),
        CORE.sha256_bytes("\0".join(values).encode("utf-8")),
    )


def build_report() -> dict[str, Any]:
    report = _CORE_BUILD_REPORT()
    candidate, current, source, contexts, _pending = ASSIGN.load_records()
    candidate_shape, candidate_sha = terminal_info(candidate)
    _current_shape, current_sha = terminal_info(current)
    _source_shape, source_sha = terminal_info(source)
    CORE.require(
        candidate_shape == [2, 2, 3]
        and candidate_sha == EXPECTED_TERMINAL_CANDIDATE_SHA256
        and current_sha == EXPECTED_TERMINAL_CURRENT_SHA256
        and source_sha == EXPECTED_TERMINAL_SOURCE_SHA256
        and all(
            CORE.first_literal(contexts[language], (0, terminal)) == ""
            for language in ("en", "sc", "tc")
            for terminal in CORE.TERMINALS
        ),
        "bound-negative register terminal guard drifted",
    )
    evidence = json.loads(PRIVATE_EVIDENCE_PATH.read_text(encoding="utf-8"))
    proof = evidence["proof"]
    CORE.require(
        proof["all_selected_ordinals_reviewed"] is True
        and proof["maximum_rewrite_attempts_per_root"] == 1
        and len(proof["rewrite_attempt_roots"]) == 4
        and proof["owned_overlap_auto_promotion_count"] == 0
        and proof["prior_pending_evidence_automatic_promotion_count"] == 0
        and proof["multi_control_partial_pass_authorized"] is False
        and proof["source_only_action_count"] == 0
        and proof["non_display_candidate_action_count"] == 0
        and proof["shared_terminal_modified"] is False,
        "single-pass or exclusion proof drifted",
    )
    decisions = CORE.load_decisions()
    terminal_roots = {(0, value) for value in CORE.TERMINALS}
    CORE.require(
        len(decisions) == 10
        and not {
            CORE.parse_coordinate(str(row["coordinate"]))[:2]
            for row in decisions
        } & terminal_roots,
        "shared terminal decision detected",
    )
    assignment_public = json.loads(
        CORE.ASSIGNMENT_PUBLIC_PATH.read_text(encoding="ascii")
    )
    CORE.require(
        assignment_public["coverage"]["source_only_action_count"] == 0
        and assignment_public["coverage"]["source_only_repair_site_count"] == 1
        and assignment_public["assignment"]["chunks"][1]["owned_overlap_root_count"] == 0
        and assignment_public["assignment"]["chunks"][1]["same_gap_atom_count"] == 0
        and assignment_public["terminal_compatibility"][
            "automatic_status_promotion_authorized"
        ] is False,
        "assignment exclusion guard drifted",
    )
    report["guards"].update({
        "assignment_public_sha256": EXPECTED_ASSIGNMENT_PUBLIC_SHA256,
        "official_ledger_sha256": EXPECTED_OFFICIAL_LEDGER_SHA256,
        "terminal_candidate_sha256": EXPECTED_TERMINAL_CANDIDATE_SHA256,
        "terminal_current_sha256": EXPECTED_TERMINAL_CURRENT_SHA256,
        "terminal_source_sha256": EXPECTED_TERMINAL_SOURCE_SHA256,
    })
    report["proof"].update({
        "all_selected_bound_negative_ordinals_reviewed": True,
        "context_terminals_authoritative": False,
        "multi_control_partial_pass_authorized": False,
        "owned_overlap_automatic_promotion_count": 0,
        "prior_pending_evidence_automatic_promotion_count": 0,
        "shared_terminal_modified": False,
        "source_only_action_count": 0,
        "terminal_register_counts": {
            "archaic": 2,
            "formal": 3,
            "plain": 2,
        },
        "translation_override_count": 5,
    })
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--bootstrap-public", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    content = CORE.serialized(report)
    output_sha256 = CORE.sha256_bytes(content)
    if not args.bootstrap_public:
        CORE.require(
            EXPECTED_PUBLIC_FILE_SHA256 is not None
            and output_sha256 == EXPECTED_PUBLIC_FILE_SHA256,
            f"public output hash drifted: {output_sha256}",
        )
    if args.check:
        CORE.require(
            DEFAULT_PUBLIC_OUTPUT.is_file()
            and DEFAULT_PUBLIC_OUTPUT.read_bytes() == content,
            "public artifact drifted",
        )
    else:
        DEFAULT_PUBLIC_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_PUBLIC_OUTPUT.write_bytes(content)
    print(json.dumps({
        "accepted_pending": EXPECTED_COUNTS["promoted_pending_rows"],
        "blocked_pending": EXPECTED_COUNTS["blocked_pending_rows"],
        "output_sha256": output_sha256,
        "reviewed_candidate_sha256": EXPECTED_REVIEWED_CANDIDATE_SHA256,
        "status": "PASS",
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True))
    return 0


configure_core()
_CORE_BUILD_REPORT = CORE.build_report
CORE.build_report = build_report
coordinate_digest = CORE.coordinate_digest
load_decisions = CORE.load_decisions
serialized = CORE.serialized
sha256_file = CORE.sha256_file
ReviewError = CORE.ReviewError


if __name__ == "__main__":
    raise SystemExit(main())
