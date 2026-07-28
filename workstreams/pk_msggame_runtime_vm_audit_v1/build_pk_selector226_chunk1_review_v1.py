#!/usr/bin/env python3
"""Validate selector-226 chunk 1 and emit its source-free checkpoint."""

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
    "selector226_chunk1_review_core",
)
ASSIGN_WRAPPER = load_module(
    WORKSTREAM / "build_pk_selector226_assignment_v1.py",
    "selector226_chunk1_review_assignment",
)
ASSIGN = ASSIGN_WRAPPER.ASSIGNMENT
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.RECORDS.load_records

ASSIGNMENT_PATH = DIALOGUE_TMP / "pk_selector226_assignment.private.v1.json"
PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector226_chunk1_review_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector226_chunk1_review_evidence.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector226_chunk1_review.source_free.v1.json"
)
METHOD = (
    "post_selector1168_selector226_chunk1_single_pass_"
    "fresh_pending_semantic_and_register_assembly_review"
)
PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector226-chunk1-review-decision.private.v1"
)
PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector226-chunk1-review-evidence.private.v1"
)
PUBLIC_SCHEMA = "nobu16.kr.pk-selector226-chunk1-review.source-free.v1"
EXPECTED_COUNTS = {
    "accepted_pending_roots": 13,
    "accepted_sites": 28,
    "assembly_branches": 245,
    "blocked_pending_roots": 5,
    "blocked_pending_rows": 9,
    "blocked_sites": 7,
    "completed_selector_overlap_relations": 5,
    "decision_rows": 17,
    "owned_overlap_roots": 5,
    "prior_caller_evidence_roots": 18,
    "promoted_pending_rows": 17,
    "roots": 35,
    "same_gap_branches": 0,
    "shared_override_rows": 0,
    "sites": 35,
    "template_roots": 5,
    "translation_overrides": 3,
    "verification_renewal_rows": 0,
}
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 14,
    "translation_override_and_runtime_promotion": 3,
}
EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "B8957E12245FDAA02CDAB3690E4DE4FE4601D2B92F8185D5734DBAB909C87D7F"
)
EXPECTED_ASSIGNMENT_SHA256 = (
    "223EBD7D1C0C0D6E78DCD97D0189C1E5099DBB917DD2498CC659BEDEBFAEE050"
)
EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "BFD1F9D8A813C2ADA7D8C065B4F7C1963F8704A7538C306C9EF6DE203F414215"
)
EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "56FBAF8FB54CCFA7EAF10355F66FE6A730374804F48FB4CD9F8F15A99AEE9A91"
)
EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "0EB986AA79D4E1C8195440877754B434C338A4E3FED3A7BB365B5905F93FE533"
)
EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "49D8E1A3F47EDA254C3F923C304BDF67932BA9500B9CC058FF0084E3AF5E2979"
)
EXPECTED_CANDIDATE_SHA256 = (
    "EF84A8B8A18C1F2F1F72D3A650C01DC7B058F32A3536C130809C4FCB31C837C7"
)
EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "FEE99844339C291F6950BEB2193AB5FDD8D25B6F6117AD52F81DCBF7F0CC9B66"
)
EXPECTED_LIVE_STEAM_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_TERMINAL_CANDIDATE_SHA256 = (
    "E84F2CF9B57C34F9C40F357BFC0469E2A7FAB5C49E33DC1734447F6C9F069E62"
)
EXPECTED_TERMINAL_CURRENT_SHA256 = (
    "0FBD6CD0D4C3C5CB6C3CF17B62D061ADDAF0A6117FC4B6A6C70353B50A6A0419"
)
EXPECTED_TERMINAL_SOURCE_SHA256 = (
    "DB8801176872E89F4109D2AECA4A0B60A51E76CB0A3EAF5FE6EA6E04966E3511"
)
EXPECTED_DIGESTS = {
    "assembly":
        "EBD3A259FF78EFFC0278E4B4C2D1F105CBA1B5388DEFCB07A9AD8A027B86C595",
    "decision":
        "B48AB8A9783760193110FFDBAE58460949ADF7AA4CB9FFA26C3C6EA9AB42405A",
    "override":
        "2E959DE55A7C303B2DC2D149EE232C963A42EFC3A17F52DB368FC59C8F438679",
    "promoted":
        "B48AB8A9783760193110FFDBAE58460949ADF7AA4CB9FFA26C3C6EA9AB42405A",
}
EXPECTED_PUBLIC_FILE_SHA256 = (
    "66B9A2D4B2BD4ACAEE18AB82855F6A9F4C352568985749889AFC85AEAC75CC62"
)
_CORE_BUILD_REPORT = CORE.build_report


def configure_core() -> None:
    CORE.ASSIGNMENT_BUILDER_PATH = (
        WORKSTREAM / "build_pk_selector226_assignment_v1.py"
    )
    CORE.ASSIGNMENT_PATH = ASSIGNMENT_PATH
    CORE.ASSIGNMENT_PUBLIC_PATH = (
        WORKSTREAM / "public" / "pk_selector226_assignment_coverage.v1.json"
    )
    CORE.OFFICIAL_LEDGER_PATH = (
        DIALOGUE_TMP
        / "runtime_vm_integrated.post_selector1168_consolidated_checkpoint.private.v1.jsonl"
    )
    CORE.PRIVATE_DECISIONS_PATH = PRIVATE_DECISIONS_PATH
    CORE.PRIVATE_EVIDENCE_PATH = PRIVATE_EVIDENCE_PATH
    CORE.DEFAULT_PUBLIC_OUTPUT = DEFAULT_PUBLIC_OUTPUT
    CORE.SELECTOR = 226
    CORE.TERMINALS = tuple(range(1538, 1545))
    CORE.CHUNK_ID = 1
    CORE.PRIVATE_DECISION_SCHEMA = PRIVATE_DECISION_SCHEMA
    CORE.PRIVATE_EVIDENCE_SCHEMA = PRIVATE_EVIDENCE_SCHEMA
    CORE.PUBLIC_SCHEMA = PUBLIC_SCHEMA
    CORE.METHOD = METHOD
    CORE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
        EXPECTED_ASSIGNMENT_BUILDER_SHA256
    )
    CORE.EXPECTED_ASSIGNMENT_SHA256 = EXPECTED_ASSIGNMENT_SHA256
    CORE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
        EXPECTED_ASSIGNMENT_PUBLIC_SHA256
    )
    CORE.EXPECTED_OFFICIAL_LEDGER_SHA256 = EXPECTED_OFFICIAL_LEDGER_SHA256
    CORE.EXPECTED_PRIVATE_DECISIONS_SHA256 = (
        EXPECTED_PRIVATE_DECISIONS_SHA256
    )
    CORE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = EXPECTED_PRIVATE_EVIDENCE_SHA256
    CORE.EXPECTED_CANDIDATE_SHA256 = EXPECTED_CANDIDATE_SHA256
    CORE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
        EXPECTED_REVIEWED_CANDIDATE_SHA256
    )
    CORE.EXPECTED_LIVE_STEAM_SHA256 = EXPECTED_LIVE_STEAM_SHA256
    CORE.EXPECTED_PUBLIC_FILE_SHA256 = EXPECTED_PUBLIC_FILE_SHA256
    CORE.EXPECTED_COUNTS = EXPECTED_COUNTS
    CORE.EXPECTED_ACTION_COUNTS = EXPECTED_ACTION_COUNTS
    CORE.EXPECTED_DIGESTS = EXPECTED_DIGESTS
    CORE.ASSIGN = ASSIGN
    CORE.ENGINE = ASSIGN.ENGINE
    CORE.RANKING = ASSIGN.RANKING
    CORE._EDGE_CACHE.clear()
    CORE._TERMINAL_CACHE.clear()


def terminal_info(records: Any) -> tuple[list[int], str, bool]:
    values = [
        CORE.first_literal(records, (0, terminal))
        for terminal in CORE.TERMINALS
    ]
    return (
        sorted(Counter(values).values()),
        CORE.sha256_bytes("\0".join(values).encode("utf-8")),
        all(value.startswith(chr(44256) + " ") for value in values),
    )


def build_report() -> dict[str, Any]:
    report = _CORE_BUILD_REPORT()
    candidate, current, source, _contexts, _pending = ASSIGN.load_records()
    candidate_shape, candidate_sha, connective = terminal_info(candidate)
    current_shape, current_sha, _ = terminal_info(current)
    source_shape, source_sha, _ = terminal_info(source)
    CORE.require(
        candidate_shape == [1, 1, 2, 3]
        and current_shape == [1, 1, 1, 2, 2]
        and source_shape == [1, 1, 1, 2, 2]
        and connective
        and candidate_sha == EXPECTED_TERMINAL_CANDIDATE_SHA256
        and current_sha == EXPECTED_TERMINAL_CURRENT_SHA256
        and source_sha == EXPECTED_TERMINAL_SOURCE_SHA256,
        "terminal register guard drifted",
    )
    evidence = json.loads(
        PRIVATE_EVIDENCE_PATH.read_text(encoding="utf-8")
    )
    proof = evidence["proof"]
    CORE.require(
        proof["maximum_rewrite_attempts_per_root"] == 1
        and len(proof["rewrite_attempt_roots"]) == 3
        and proof["shared_terminal_modified"] is False
        and proof["source_only_action_count"] == 0
        and proof["non_display_candidate_action_count"] == 0
        and proof["owned_overlap_auto_promotion_count"] == 0
        and proof["prior_caller_evidence_usage"]
        == "assembly_and_terminal_only"
        and sorted(
            len(row["roots"])
            for row in proof["template_group_dispositions"]
        ) == [2, 3]
        and all(
            row["accepted"] is True
            for row in proof["template_group_dispositions"]
        ),
        "single-pass private proof drifted",
    )
    decisions = CORE.load_decisions()
    terminal_roots = {(0, value) for value in CORE.TERMINALS}
    CORE.require(
        not {
            CORE.parse_coordinate(str(row["coordinate"]))[:2]
            for row in decisions
        }
        & terminal_roots,
        "shared terminal decision detected",
    )
    official_rows = [
        json.loads(line)
        for line in CORE.OFFICIAL_LEDGER_PATH.read_text(
            encoding="utf-8"
        ).splitlines()
        if line
    ]
    non_display = {
        str(row["coordinate"])
        for row in official_rows
        if row.get("resource") == "pk_msggame"
        and row.get("scope_classification") == "confirmed_non_display"
    }
    CORE.require(
        not non_display
        & {str(row["coordinate"]) for row in decisions},
        "confirmed non-display decision detected",
    )
    assignment_public = json.loads(
        CORE.ASSIGNMENT_PUBLIC_PATH.read_text(encoding="ascii")
    )
    CORE.require(
        assignment_public["coverage"]["source_only_action_count"] == 0
        and assignment_public["coverage"]["source_only_repair_site_count"]
        == 5
        and assignment_public["terminal_compatibility"][
            "terminal_registers_frozen"
        ]
        is True,
        "assignment source-only or terminal guard drifted",
    )
    report["guards"].update({
        "assignment_public_sha256": EXPECTED_ASSIGNMENT_PUBLIC_SHA256,
        "official_ledger_sha256": EXPECTED_OFFICIAL_LEDGER_SHA256,
        "terminal_candidate_sha256": EXPECTED_TERMINAL_CANDIDATE_SHA256,
        "terminal_current_sha256": EXPECTED_TERMINAL_CURRENT_SHA256,
        "terminal_source_sha256": EXPECTED_TERMINAL_SOURCE_SHA256,
    })
    report["proof"].update({
        "connective_and_space_owned_by_terminal": True,
        "maximum_rewrite_attempts_per_root": 1,
        "non_display_candidate_action_count": 0,
        "owned_overlap_auto_promotion_count": 0,
        "prior_caller_evidence_used_for_assembly_and_terminal_only": True,
        "rewrite_attempt_roots": 3,
        "shared_terminal_modified": False,
        "source_only_action_count": 0,
        "template_groups_atomic": True,
        "terminal_register_multiplicities": [1, 1, 2, 3],
        "verification_renewal_rows_empty": True,
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
    if EXPECTED_PUBLIC_FILE_SHA256:
        CORE.require(
            output_sha256 == EXPECTED_PUBLIC_FILE_SHA256,
            "public output drifted",
        )
    if args.bootstrap_public or not args.check:
        DEFAULT_PUBLIC_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_PUBLIC_OUTPUT.write_bytes(content)
    else:
        CORE.require(
            DEFAULT_PUBLIC_OUTPUT.is_file()
            and DEFAULT_PUBLIC_OUTPUT.read_bytes() == content,
            "public artifact drifted",
        )
    print(json.dumps({
        "accepted_pending": EXPECTED_COUNTS["promoted_pending_rows"],
        "blocked_pending": EXPECTED_COUNTS["blocked_pending_rows"],
        "output_sha256": output_sha256,
        "reviewed_candidate_sha256": EXPECTED_REVIEWED_CANDIDATE_SHA256,
        "status": "PASS",
        "steam_write_performed": False,
    }, sort_keys=True))
    return 0


configure_core()
CORE.build_report = build_report
coordinate_digest = CORE.coordinate_digest
load_decisions = CORE.load_decisions
serialized = CORE.serialized
sha256_file = CORE.sha256_file
ReviewError = CORE.ReviewError


if __name__ == "__main__":
    raise SystemExit(main())
