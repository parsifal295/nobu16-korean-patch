#!/usr/bin/env python3
"""Validate selector-562 chunk 1 and emit its source-free checkpoint."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Sequence

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"


def load(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


CORE = load(
    WORKSTREAM / "build_pk_selector550_chunk1_review_v1.py",
    "selector562_chunk1_review_core",
)
WRAPPER = load(
    WORKSTREAM / "build_pk_selector562_assignment_v1.py",
    "selector562_chunk1_review_assignment",
)
ASSIGN = WRAPPER.ASSIGNMENT
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.RECORDS.load_records

ASSIGNMENT_PATH = TMP / "pk_selector562_assignment.private.v1.json"
PRIVATE_DECISIONS_PATH = (
    TMP / "semantic_overrides"
    / "pk_selector562_chunk1_review_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_PATH = TMP / "pk_selector562_chunk1_review_evidence.private.v1.json"
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector562_chunk1_review.source_free.v1.json"
)
METHOD = (
    "post_selector466_selector562_chunk1_single_pass_exact_"
    "nominal_copula_review"
)
PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector562-chunk1-review-decision.private.v1"
)
PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector562-chunk1-review-evidence.private.v1"
)
PUBLIC_SCHEMA = "nobu16.kr.pk-selector562-chunk1-review.source-free.v1"
EXPECTED_COUNTS = {
    "accepted_pending_roots": 2,
    "accepted_sites": 3,
    "assembly_branches": 182,
    "blocked_pending_roots": 14,
    "blocked_pending_rows": 20,
    "blocked_sites": 23,
    "decision_rows": 5,
    "jp_only_sites": 13,
    "non_display_actions": 0,
    "owned_overlap_roots": 0,
    "prior_assembly_evidence_pending_rows": 23,
    "prior_assembly_evidence_roots": 16,
    "promoted_pending_rows": 5,
    "rewrite_attempt_roots": 5,
    "roots": 26,
    "same_gap_branches": 0,
    "sites": 26,
    "source_only_actions": 0,
    "translation_overrides": 3,
    "verification_renewal_rows": 0,
}
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 2,
    "translation_override_and_runtime_promotion": 3,
}
EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "FEBE7891BE6CA37EF8C2708F7E73F3F8647E2A1BCD55B85CD00F87FEF08F7395"
)
EXPECTED_ASSIGNMENT_SHA256 = (
    "9F0DF230231732B1345B80FC6F159F9D18DAD56F87D707971193658C895B1067"
)
EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "42AC1603E4F599BC36BF9B58BB766390388660050650101EC22DF41C043EED3A"
)
EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "99450F568D8EDED40C7A7332F52DADA184EE6F11FB129CFDBCC758C7880DC197"
)
EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "4DB881B2DEC037241F3092B292D485695D2B3842982F91E6DCED249D156CE240"
)
EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "C341085B60E72385F376819BD1F8D89651F4A5BAEC33AB5645CA4887631F60D9"
)
EXPECTED_CANDIDATE_SHA256 = (
    "E2283160520383E455C9C26112E80E5DB5EDB89161A9842FF3BD8F4C7FFCAD45"
)
EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "FFDC50EFE3858F8FEDD7F7F8E66271E80AA5CC43B948AB1684431531D950DAE3"
)
EXPECTED_LIVE_STEAM_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_TERMINAL_CANDIDATE_SHA256 = (
    "31F899387108821947571F9085D8A7FD9919BD52B8BA349DC831E138740343D6"
)
EXPECTED_TERMINAL_CURRENT_SHA256 = EXPECTED_TERMINAL_CANDIDATE_SHA256
EXPECTED_TERMINAL_SOURCE_SHA256 = (
    "DD32A4A1CB88CDA98B9B37CDC21CB43A7D2C5B00B7EE374A10A0F774FD26C073"
)
EXPECTED_CROSS_SELECTOR754_SHA256 = (
    "5DDA016D2859AF1B9FA198C9EAFC11D0A71C246D548FC8906CD81EEDF8E1FAA9"
)
EXPECTED_DIGESTS = {
    "assembly": "09BB2AAF5A9E95C60D0C6F414D120C08A7BAA3546B45838E32C7BCE70383789A",
    "decision": "585E1CCB0662679D546B8AC5B54F39E22A1F3B61A9BC99494616D6B954D4FD18",
    "override": "48A4C83A434B314F6295EB843E2B9D9AE9F7C0A92C862682212F8F78B7D2A7B2",
    "promoted": "585E1CCB0662679D546B8AC5B54F39E22A1F3B61A9BC99494616D6B954D4FD18",
}
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "BFACB9361C7C6765504B691FF4DA6DE12807D409A0E26E648FEBCBC9DC359985"
)


def configure() -> None:
    CORE.ASSIGNMENT_BUILDER_PATH = (
        WORKSTREAM / "build_pk_selector562_assignment_v1.py"
    )
    CORE.ASSIGNMENT_PATH = ASSIGNMENT_PATH
    CORE.ASSIGNMENT_PUBLIC_PATH = (
        WORKSTREAM / "public" / "pk_selector562_assignment_coverage.v1.json"
    )
    CORE.OFFICIAL_LEDGER_PATH = (
        TMP
        / "runtime_vm_integrated.post_selector466_consolidated_checkpoint.private.v1.jsonl"
    )
    CORE.PRIVATE_DECISIONS_PATH = PRIVATE_DECISIONS_PATH
    CORE.PRIVATE_EVIDENCE_PATH = PRIVATE_EVIDENCE_PATH
    CORE.DEFAULT_PUBLIC_OUTPUT = DEFAULT_PUBLIC_OUTPUT
    CORE.SELECTOR = 562
    CORE.TERMINALS = tuple(range(1944, 1951))
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


configure()
_CORE_BUILD_REPORT = CORE.build_report


def terminal_digest(records: Any) -> str:
    values = [
        CORE.first_literal(records, (0, terminal))
        for terminal in CORE.TERMINALS
    ]
    return CORE.sha256_bytes("\0".join(values).encode("utf-8"))


def build_report() -> dict[str, Any]:
    report = _CORE_BUILD_REPORT()
    candidate, current, source, contexts, _pending = ASSIGN.load_records()
    CORE.require(
        terminal_digest(candidate) == EXPECTED_TERMINAL_CANDIDATE_SHA256
        and terminal_digest(current) == EXPECTED_TERMINAL_CURRENT_SHA256
        and terminal_digest(source) == EXPECTED_TERMINAL_SOURCE_SHA256
        and all(
            CORE.first_literal(contexts[language], (0, terminal)) == ""
            for language in ("en", "sc", "tc")
            for terminal in CORE.TERMINALS
        ),
        "nominal copula terminal guard drifted",
    )
    evidence = json.loads(PRIVATE_EVIDENCE_PATH.read_text(encoding="utf-8"))
    proof = evidence["proof"]
    CORE.require(
        proof["maximum_rewrite_attempts_per_root"] == 1
        and len(proof["rewrite_attempt_roots"]) == 5
        and len(proof["rejected_rewrite_attempt_roots"]) == 3
        and proof["cross_selector754_branches_reviewed"] == 7
        and evidence["digests"]["cross_selector754_sha256"]
            == EXPECTED_CROSS_SELECTOR754_SHA256
        and proof["owned_overlap_auto_promotion_count"] == 0
        and proof["prior_pending_evidence_automatic_promotion_count"] == 0
        and proof["same_gap_branch_count"] == 0
        and proof["shared_terminal_modified"] is False
        and proof["verification_renewal_rows"] == 0,
        "single-pass proof drifted",
    )
    report["guards"].update({
        "cross_selector754_sha256": EXPECTED_CROSS_SELECTOR754_SHA256,
        "terminal_candidate_sha256": EXPECTED_TERMINAL_CANDIDATE_SHA256,
        "terminal_current_sha256": EXPECTED_TERMINAL_CURRENT_SHA256,
        "terminal_source_sha256": EXPECTED_TERMINAL_SOURCE_SHA256,
    })
    report["proof"].update({
        "all_seven_nominal_copula_ordinals_reviewed": True,
        "context_terminals_authoritative": False,
        "cross_selector754_branches_reviewed": 7,
        "maximum_rewrite_attempts_per_root": 1,
        "owned_overlap_automatic_promotion_count": 0,
        "prior_pending_evidence_automatic_promotion_count": 0,
        "same_gap_branch_count": 0,
        "shared_terminal_modified": False,
        "source_only_action_count": 0,
        "terminal_register_counts": {
            "archaic": 3, "formal": 2, "plain": 2,
        },
        "verification_renewal_rows": 0,
    })
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--bootstrap-public", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    content = CORE.serialized(report)
    digest = CORE.sha256_bytes(content)
    if not args.bootstrap_public:
        CORE.require(
            EXPECTED_PUBLIC_FILE_SHA256 is not None
            and digest == EXPECTED_PUBLIC_FILE_SHA256,
            f"public output hash drifted: {digest}",
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
        "accepted_pending": 5,
        "blocked_pending": 20,
        "output_sha256": digest,
        "reviewed_candidate_sha256": EXPECTED_REVIEWED_CANDIDATE_SHA256,
        "status": "PASS",
        "steam_write_performed": False,
    }, sort_keys=True))
    return 0


CORE.build_report = build_report
coordinate_digest = CORE.coordinate_digest
load_decisions = CORE.load_decisions
serialized = CORE.serialized
sha256_file = CORE.sha256_file
ReviewError = CORE.ReviewError

if __name__ == "__main__":
    raise SystemExit(main())
