#!/usr/bin/env python3
"""Validate selector-268 chunk 1 and emit its source-free checkpoint."""

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
    "selector268_chunk1_review_core",
)
ASSIGNMENT = load_module(
    WORKSTREAM / "build_pk_selector268_assignment_v1.py",
    "selector268_chunk1_review_assignment",
)
ASSIGN = ASSIGNMENT.ASSIGNMENT
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.RECORDS.load_records

ASSIGNMENT_PATH = DIALOGUE_TMP / "pk_selector268_assignment.private.v1.json"
PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector268_chunk1_review_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector268_chunk1_review_evidence.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector268_chunk1_review.source_free.v1.json"
)
METHOD = (
    "post_selector226_selector268_chunk1_single_pass_fresh_exact_"
    "question_register_and_same_gap_atom_review"
)
PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector268-chunk1-review-decision.private.v1"
)
PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector268-chunk1-review-evidence.private.v1"
)
PUBLIC_SCHEMA = "nobu16.kr.pk-selector268-chunk1-review.source-free.v1"
EXPECTED_COUNTS = {
    "accepted_pending_roots": 2,
    "accepted_sites": 3,
    "assembly_branches": 91,
    "blocked_pending_roots": 8,
    "blocked_pending_rows": 24,
    "blocked_sites": 10,
    "completed_selector_overlap_relations": 6,
    "decision_rows": 4,
    "non_display_actions": 0,
    "owned_overlap_blocked_rows": 15,
    "owned_overlap_roots": 4,
    "prior_assembly_evidence_pending_rows": 25,
    "prior_assembly_evidence_roots": 10,
    "promoted_pending_rows": 4,
    "question_boundary_blocked_rows": 8,
    "rewrite_attempt_roots": 0,
    "roots": 13,
    "same_gap_atoms": 1,
    "same_gap_blocked_rows": 1,
    "same_gap_branches": 7,
    "sites": 13,
    "source_only_actions": 0,
    "translation_overrides": 0,
    "verification_renewal_rows": 0,
}
EXPECTED_ACTION_COUNTS = {"runtime_promotion": 4}
EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "8D0B1F1156ABD01697502DEA809B15C483F3D9EC1AA3D16AF6509423A72FC1E1"
)
EXPECTED_ASSIGNMENT_SHA256 = (
    "91ED0510E5783DDA7B6894CA8A5144FB4D2FA9300A71BD2EC1B2F4699022C315"
)
EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "5F0C6B1935B7EC8568DC7C52EFB67D90BEF96398A8977DFEA70B23B3FA71053B"
)
EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "33B635E1409B290202A98719A9CD58F356551BB54703B7F287FC45250134623D"
)
EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "5971BC8E14E713173EBCFFFD214BD0F6CE4A77BCD5613CB23BCC8A0D4961E23C"
)
EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "E1C76FF7F38290F0BF517CA64590D946AB3F6EA0BE7D381F370B92B883F2C3AD"
)
EXPECTED_CANDIDATE_SHA256 = (
    "FEE99844339C291F6950BEB2193AB5FDD8D25B6F6117AD52F81DCBF7F0CC9B66"
)
EXPECTED_REVIEWED_CANDIDATE_SHA256 = EXPECTED_CANDIDATE_SHA256
EXPECTED_LIVE_STEAM_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_TERMINAL_CANDIDATE_SHA256 = (
    "4B8A084ECCE354B2B0201FD5A7490CE5FEE18E0A7EBDD40C3908CB2E6EED04D1"
)
EXPECTED_TERMINAL_CURRENT_SHA256 = (
    "5A9B895D4F1D91B2BA58C6607ED672C28F256DD3D2C1A114E2097D041A9B2F6D"
)
EXPECTED_TERMINAL_SOURCE_SHA256 = (
    "3151D392EC13DFEA77F2972C31CEBD28D120C117C484E43C386DCB71FCB3160F"
)
EXPECTED_SAME_GAP_ATOM_SHA256 = (
    "52952A615E18681849833DF5F349FF96EF69349732DCB49EBC265D0B7D676A7A"
)
EXPECTED_DIGESTS = {
    "assembly": "5DCB40DA281E2387CDC4BA5F9F15B4A42BEEE81C8A6AAD9868843EEDE36FBFEC",
    "decision": "8CAB0AFFCAB8E6A06761E656984742DD39CD9C74443CBF0CB8B5AEFAA4A4F808",
    "override": "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "promoted": "8CAB0AFFCAB8E6A06761E656984742DD39CD9C74443CBF0CB8B5AEFAA4A4F808",
}
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "67812DFAEDBDA6400A729583CC05D30A8BBD238117088A5142E110DA7779978E"
)


def configure_core() -> None:
    CORE.ASSIGNMENT_BUILDER_PATH = (
        WORKSTREAM / "build_pk_selector268_assignment_v1.py"
    )
    CORE.ASSIGNMENT_PATH = ASSIGNMENT_PATH
    CORE.ASSIGNMENT_PUBLIC_PATH = (
        WORKSTREAM / "public" / "pk_selector268_assignment_coverage.v1.json"
    )
    CORE.OFFICIAL_LEDGER_PATH = (
        DIALOGUE_TMP
        / "runtime_vm_integrated.post_selector226_consolidated_checkpoint.private.v1.jsonl"
    )
    CORE.PRIVATE_DECISIONS_PATH = PRIVATE_DECISIONS_PATH
    CORE.PRIVATE_EVIDENCE_PATH = PRIVATE_EVIDENCE_PATH
    CORE.DEFAULT_PUBLIC_OUTPUT = DEFAULT_PUBLIC_OUTPUT
    CORE.SELECTOR = 268
    CORE.TERMINALS = tuple(range(1587, 1594))
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
    current_shape, current_sha = terminal_info(current)
    source_shape, source_sha = terminal_info(source)
    CORE.require(
        candidate_shape == [1, 2, 4]
        and current_shape == [1, 2, 4]
        and source_shape == [1, 2, 4]
        and candidate_sha == EXPECTED_TERMINAL_CANDIDATE_SHA256
        and current_sha == EXPECTED_TERMINAL_CURRENT_SHA256
        and source_sha == EXPECTED_TERMINAL_SOURCE_SHA256
        and all(
            CORE.first_literal(contexts[language], (0, terminal)) == ""
            for language in ("en", "sc", "tc")
            for terminal in CORE.TERMINALS
        ),
        "question-register terminal guard drifted",
    )
    evidence = json.loads(
        PRIVATE_EVIDENCE_PATH.read_text(encoding="utf-8")
    )
    proof = evidence["proof"]
    atom = evidence["same_gap_atom_manifest"]
    CORE.require(
        proof["all_selected_ordinals_reviewed"] is True
        and proof["maximum_rewrite_attempts_per_root"] == 1
        and proof["rewrite_attempt_roots"] == []
        and proof["owned_overlap_auto_promotion_count"] == 0
        and proof["prior_pending_evidence_automatic_promotion_count"] == 0
        and proof["same_gap_atom_accepted"] is False
        and proof["same_gap_atom_partial_pass_authorized"] is False
        and proof["source_only_action_count"] == 0
        and proof["non_display_candidate_action_count"] == 0
        and proof["shared_terminal_modified"] is False
        and len(atom) == 21
        and {int(row["selector"]) for row in atom} == {268, 700, 736}
        and not any(row["atom_accepted"] for row in atom)
        and CORE.canonical_sha256(atom) == EXPECTED_SAME_GAP_ATOM_SHA256,
        "single-pass or same-gap atom proof drifted",
    )
    decisions = CORE.load_decisions()
    terminal_roots = {(0, value) for value in CORE.TERMINALS}
    CORE.require(
        len(decisions) == 4
        and not {
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
        not non_display & {str(row["coordinate"]) for row in decisions},
        "confirmed non-display decision detected",
    )
    assignment_public = json.loads(
        CORE.ASSIGNMENT_PUBLIC_PATH.read_text(encoding="ascii")
    )
    CORE.require(
        assignment_public["coverage"]["source_only_action_count"] == 0
        and assignment_public["coverage"]["source_only_repair_site_count"] == 1
        and assignment_public["coverage"]["owned_overlap_pending_rows"] == 25
        and assignment_public["assignment"]["same_gap_atom_count"] == 1
        and assignment_public["assignment"]["same_gap_atom_split"] is False
        and assignment_public["assignment"][
            "same_gap_neighbor_relation_count"
        ] == 2
        and assignment_public["terminal_compatibility"][
            "automatic_status_promotion_authorized"
        ]
        is False,
        "assignment source-only, overlap, or atom guard drifted",
    )
    report["guards"].update({
        "assignment_public_sha256": EXPECTED_ASSIGNMENT_PUBLIC_SHA256,
        "official_ledger_sha256": EXPECTED_OFFICIAL_LEDGER_SHA256,
        "same_gap_atom_sha256": EXPECTED_SAME_GAP_ATOM_SHA256,
        "terminal_candidate_sha256": EXPECTED_TERMINAL_CANDIDATE_SHA256,
        "terminal_current_sha256": EXPECTED_TERMINAL_CURRENT_SHA256,
        "terminal_source_sha256": EXPECTED_TERMINAL_SOURCE_SHA256,
    })
    report["proof"].update({
        "all_selected_question_register_ordinals_reviewed": True,
        "owned_overlap_automatic_promotion_count": 0,
        "prior_pending_evidence_automatic_promotion_count": 0,
        "question_boundary_duplicate_or_omission_count": 0,
        "same_gap_atom_atomic_rejection": True,
        "same_gap_atom_partial_pass_authorized": False,
        "shared_terminal_modified": False,
        "source_only_action_count": 0,
        "terminal_multiplicity_sorted": [1, 2, 4],
        "translation_override_count": 0,
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
