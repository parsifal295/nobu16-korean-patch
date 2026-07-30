#!/usr/bin/env python3
"""Validate selector-466 chunk 1 and emit its source-free checkpoint."""

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
TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"


def load(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


CORE = load(WORKSTREAM / "build_pk_selector550_chunk1_review_v1.py", "s466_review_core")
WRAPPER = load(WORKSTREAM / "build_pk_selector466_assignment_v1.py", "s466_review_assignment")
ASSIGN = WRAPPER.ASSIGNMENT
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.RECORDS.load_records

ASSIGNMENT_PATH = TMP / "pk_selector466_assignment.private.v1.json"
PRIVATE_DECISIONS_PATH = TMP / "semantic_overrides" / "pk_selector466_chunk1_review_decisions.private.v1.jsonl"
PRIVATE_EVIDENCE_PATH = TMP / "pk_selector466_chunk1_review_evidence.private.v1.json"
DEFAULT_PUBLIC_OUTPUT = WORKSTREAM / "public" / "pk_selector466_chunk1_review.source_free.v1.json"
METHOD = "post_selector1078_selector466_chunk1_single_pass_exact_cartesian_review"
PRIVATE_DECISION_SCHEMA = "nobu16.kr.pk-selector466-chunk1-review-decision.private.v1"
PRIVATE_EVIDENCE_SCHEMA = "nobu16.kr.pk-selector466-chunk1-review-evidence.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector466-chunk1-review.source-free.v1"
EXPECTED_COUNTS = {
    "accepted_pending_roots": 10,
    "accepted_sites": 18,
    "assembly_branches": 287,
    "blocked_pending_roots": 2,
    "blocked_pending_rows": 4,
    "blocked_sites": 23,
    "decision_rows": 21,
    "jp_only_sites": 13,
    "multi_control_blocked_sites": 2,
    "non_display_actions": 0,
    "owned_overlap_relations": 3,
    "owned_overlap_roots": 2,
    "owned_relation_branches": 21,
    "prior_assembly_evidence_pending_rows": 23,
    "prior_assembly_evidence_roots": 11,
    "promoted_pending_rows": 21,
    "rewrite_attempt_roots": 9,
    "roots": 41,
    "same_gap_atoms": 2,
    "same_gap_branches": 14,
    "same_gap_cartesian_branches": 98,
    "same_gap_ordered_manifests": 2,
    "sites": 41,
    "source_only_actions": 0,
    "template_atoms": 3,
    "template_roots": 14,
    "translation_overrides": 11,
    "verification_renewal_rows": 0,
}
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 10,
    "translation_override_and_runtime_promotion": 11,
}
EXPECTED_ASSIGNMENT_BUILDER_SHA256 = "729E1778540A1E5FB5BF48CACE9309B83CFE0A021FDA294049FEC91104387F71"
EXPECTED_ASSIGNMENT_SHA256 = "8C7350F94A08894C5B88A4E6BD335DA96877EEE55902B4E9110186FE0E8C7507"
EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = "457C7C0D368269F69C391E6A981CF6AA5D4FB905C99B327C2DAEE9C4F137BA5E"
EXPECTED_OFFICIAL_LEDGER_SHA256 = "71ADE7F33FC40A817E60F429DE0A0B329E05BF37BD1E03E1671A019783E800F6"
EXPECTED_PRIVATE_DECISIONS_SHA256 = "DE6E32948B02FB7B19EB300C600B9732C9B3C27B4D30C9B00338F59C5FD61704"
EXPECTED_PRIVATE_EVIDENCE_SHA256 = "3E4F2CCD6E06769A76A4BBC17CAA61EF0CA70A2ACC20AFB3FDF69A0F4EEDC22B"
EXPECTED_CANDIDATE_SHA256 = "1A931E023A5248626AE90094772657D91B4270D0F530B48ABC613FDA84BB508D"
EXPECTED_REVIEWED_CANDIDATE_SHA256 = "3F71B4543F5FB7608A1D6D8E89941EEC184FCA0973166F84F6DA53309FAF833C"
EXPECTED_LIVE_STEAM_SHA256 = "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
EXPECTED_TERMINAL_CANDIDATE_SHA256 = "43B346EA667D710BDFC6A84D958602CCB68DB95CA78D204C1D8F2C43B7336483"
EXPECTED_TERMINAL_CURRENT_SHA256 = "EE25924A3F5EB5008D1EC7C3EE6506E11821B2969EF7E1AE76935E69CA64F9B3"
EXPECTED_TERMINAL_SOURCE_SHA256 = "47ABF41C98D2DF16C3C5A572EE31139D0C457B04C131D164FE69494332C4FBA3"
EXPECTED_DIGESTS = {
    "assembly": "C86C793536ACCBE685A6EC040AE7D9C07826044451EE3C04B10A5134DCECFE81",
    "decision": "3EFD049B4E438AF1160EFBBFC5D0DA646C58366A449244878491C5775E1D804A",
    "override": "0E84B705C4F401C2C9A10B1EA68514250E09CBE706E9EF36AA5BB3F888013B7C",
    "promoted": "3EFD049B4E438AF1160EFBBFC5D0DA646C58366A449244878491C5775E1D804A",
}
EXPECTED_CARTESIAN_SHA256 = "A6E6CEACB8DBB7FBA5587AAB1A5B82C312102EDDF9CFA7719348A4DFAF2A4BBC"
EXPECTED_PUBLIC_FILE_SHA256: str | None = "CA8571E73E15A9CFA4DECF83D3E8095EC9C0B5E56194D949604BF987237C1A5F"


def configure() -> None:
    CORE.ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector466_assignment_v1.py"
    CORE.ASSIGNMENT_PATH = ASSIGNMENT_PATH
    CORE.ASSIGNMENT_PUBLIC_PATH = WORKSTREAM / "public" / "pk_selector466_assignment_coverage.v1.json"
    CORE.OFFICIAL_LEDGER_PATH = TMP / "runtime_vm_integrated.post_selector1078_consolidated_checkpoint.private.v1.jsonl"
    CORE.PRIVATE_DECISIONS_PATH = PRIVATE_DECISIONS_PATH
    CORE.PRIVATE_EVIDENCE_PATH = PRIVATE_EVIDENCE_PATH
    CORE.DEFAULT_PUBLIC_OUTPUT = DEFAULT_PUBLIC_OUTPUT
    CORE.SELECTOR = 466
    CORE.TERMINALS = tuple(range(1839, 1846))
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
    values = [CORE.first_literal(records, (0, value)) for value in CORE.TERMINALS]
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
        "terminal guard drifted",
    )
    evidence = json.loads(PRIVATE_EVIDENCE_PATH.read_text(encoding="utf-8"))
    proof = evidence["proof"]
    CORE.require(
        proof["maximum_rewrite_attempts_per_root"] == 1
        and len(proof["rewrite_attempt_roots"]) == 9
        and proof["same_gap_cartesian_manifest"]
        and len(proof["same_gap_cartesian_manifest"]) == 98
        and evidence["digests"]["same_gap_cartesian_sha256"] == EXPECTED_CARTESIAN_SHA256
        and proof["multi_control_partial_pass_authorized"] is False
        and proof["template_atom_partial_pass_authorized"] is False
        and proof["owned_overlap_auto_promotion_count"] == 0
        and proof["prior_pending_evidence_automatic_promotion_count"] == 0
        and proof["shared_terminal_modified"] is False,
        "atomic proof drifted",
    )
    report["guards"].update({
        "same_gap_cartesian_sha256": EXPECTED_CARTESIAN_SHA256,
        "terminal_candidate_sha256": EXPECTED_TERMINAL_CANDIDATE_SHA256,
        "terminal_current_sha256": EXPECTED_TERMINAL_CURRENT_SHA256,
        "terminal_source_sha256": EXPECTED_TERMINAL_SOURCE_SHA256,
    })
    report["proof"].update({
        "all_same_gap_cartesian_branches_reviewed": True,
        "context_terminals_authoritative": False,
        "maximum_rewrite_attempts_per_root": 1,
        "owned_overlap_automatic_promotion_count": 0,
        "prior_pending_evidence_automatic_promotion_count": 0,
        "same_gap_partial_pass_authorized": False,
        "shared_terminal_modified": False,
        "source_only_action_count": 0,
        "template_atom_partial_pass_authorized": False,
        "terminal_register_counts": {"archaic": 3, "formal": 2, "plain": 2},
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
        CORE.require(EXPECTED_PUBLIC_FILE_SHA256 is not None
                     and digest == EXPECTED_PUBLIC_FILE_SHA256,
                     f"public output hash drifted: {digest}")
    if args.check:
        CORE.require(DEFAULT_PUBLIC_OUTPUT.is_file()
                     and DEFAULT_PUBLIC_OUTPUT.read_bytes() == content,
                     "public artifact drifted")
    else:
        DEFAULT_PUBLIC_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_PUBLIC_OUTPUT.write_bytes(content)
    print(json.dumps({
        "accepted_pending": 21, "blocked_pending": 4,
        "output_sha256": digest,
        "reviewed_candidate_sha256": EXPECTED_REVIEWED_CANDIDATE_SHA256,
        "status": "PASS", "steam_write_performed": False,
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
