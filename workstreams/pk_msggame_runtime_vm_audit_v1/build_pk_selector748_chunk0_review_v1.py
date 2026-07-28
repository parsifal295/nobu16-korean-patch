#!/usr/bin/env python3
"""Validate the frozen, source-free selector-748 chunk-0 review."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
ASSIGNMENT = DIALOGUE_TMP / "pk_selector748_assignment.private.v1.json"
ASSIGNMENT_PUBLIC = (
    WORKSTREAM / "public" / "pk_selector748_assignment_coverage.v1.json"
)
DECISIONS = (
    DIALOGUE_TMP / "semantic_overrides"
    / "pk_selector748_chunk0_review_decisions.private.v1.jsonl"
)
EVIDENCE = DIALOGUE_TMP / "pk_selector748_chunk0_review_evidence.private.v1.json"
PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector748_chunk0_review.source_free.v1.json"
)
STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin")

METHOD = (
    "f2cb_selector748_chunk0_full_seven_branch_review_with_"
    "shared_terminal_repair_and_same_gap_collision_blocks"
)
DECISION_SCHEMA = "nobu16.kr.pk-selector748-chunk0-review-decision.private.v1"
EVIDENCE_SCHEMA = "nobu16.kr.pk-selector748-chunk0-review-evidence.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector748-chunk0-review.source-free.v1"
EXPECTED = {
    "assignment": "CE5FBC60D33426695E86FBC8E76205E99917956EE55DBF10375B8933CE91B17E",
    "assignment_public": "68615492AC049EF3B87D5840ACDB67A8E05D6E8F2EED63CBC89905A8DF5515B2",
    "decision_file": "731378E3F4F8B3211814C7FCB7C43E3E8B0DF68CF37023A2A80245A0C73B7E93",
    "evidence_file": "D47573CA550B4DE6A86BE840B19DC2CEC93F12F8BEEDD4D0167D137563876DB7",
    "public_file": "E844D56FA280B747ACAF73AB35F9AE068682C5E5FD204C38C2078CEEC6D10993",
    "official_candidate": "15C3BF1B4CC2E29020E5A8A6F40669555B54EEE57B04C3F7F77DF3AC680CFB93",
    "reviewed_candidate": "69320B45F4054DC16E350EA046E0A448A5B251D4B29272ACCFC8014FF121EAF3",
    "assembly": "0F6C81FAF68F0692B136BDB0DDE14171C05B3EF8025031ADEC60E882FF62C38D",
    "decision_coordinates": "AB3F13BDC38E5A2A5AABC91D4DA0E138907FCC0E16F05E85837150F629F48396",
    "override_coordinates": "B96B71886EA6DF49ED12BE428F76BDFC2FC68950E833C485BBAF00BD822F537C",
    "promoted_coordinates": "F3112F0E8EF69EBEB77FFD90E9CA64EC9162111C416C788675565E08B7CE1BCE",
    "steam": "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766",
}
COUNTS = {
    "accepted_sites": 27,
    "assembly_branches": 238,
    "blocked_owned_overlap_roots": 2,
    "blocked_pending_rows": 19,
    "blocked_sites": 7,
    "decision_rows": 72,
    "promoted_pending_rows": 49,
    "roots": 33,
    "shared_terminal_overrides": 7,
    "sites": 34,
    "translation_overrides": 43,
}
ACTIONS = {
    "runtime_promotion": 29,
    "translation_override_and_runtime_promotion": 20,
    "translation_override_and_verification_renewal": 23,
}


class ReviewError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def build_public():
    require(
        sha256_file(ASSIGNMENT) == EXPECTED["assignment"]
        and sha256_file(ASSIGNMENT_PUBLIC) == EXPECTED["assignment_public"]
        and sha256_file(DECISIONS) == EXPECTED["decision_file"]
        and sha256_file(EVIDENCE) == EXPECTED["evidence_file"],
        "frozen review input drifted",
    )
    decisions = [
        json.loads(line)
        for line in DECISIONS.read_text(encoding="utf-8").splitlines()
        if line
    ]
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    require(
        len(decisions) == COUNTS["decision_rows"]
        and len({row["coordinate"] for row in decisions}) == len(decisions)
        and Counter(row["action"] for row in decisions) == Counter(ACTIONS),
        "decision rows drifted",
    )
    require(
        all(
            row["schema"] == DECISION_SCHEMA
            and row["runtime_review"] == "verified"
            and row["fresh_semantic_review"] == "approved"
            and row["historical_factuality_review"] == "approved"
            and row["speaker_tone_review"] == "approved"
            and row["layout_review"]
            == "current_relative_raw_g1n_nonexpanding"
            for row in decisions
        ),
        "decision approvals drifted",
    )
    require(
        sum(
            row["overlap_owner"] == "selector748_shared_terminal"
            for row in decisions
        ) == COUNTS["shared_terminal_overrides"],
        "shared terminal ownership drifted",
    )
    require(
        evidence["schema"] == EVIDENCE_SCHEMA
        and evidence["method"] == METHOD
        and evidence["counts"] == COUNTS
        and len(evidence["assembly_manifest"]) == COUNTS["assembly_branches"]
        and len(evidence["site_reviews"]) == COUNTS["sites"],
        "private evidence drifted",
    )
    require(
        all(
            review["historical_factuality_reviewed"] is True
            and review["speaker_tone_reviewed"] is True
            and all(
                branch["line_count_match"] is True
                and (
                    branch["grammar_and_spacing_proven"] is False
                    if review["decision"].startswith("blocked_")
                    else branch["grammar_and_spacing_proven"] is True
                    and branch[
                        "current_relative_raw_g1n_nonexpanding"
                    ] is True
                )
                for branch in review["assemblies"]
            )
            for review in evidence["site_reviews"]
        ),
        "branch proof drifted",
    )
    digests = evidence["digests"]
    require(
        digests["assembly_canonical_sha256"] == EXPECTED["assembly"]
        and digests["decision_coordinate_sha256"]
        == EXPECTED["decision_coordinates"]
        and digests["override_coordinate_sha256"]
        == EXPECTED["override_coordinates"]
        and digests["promoted_coordinate_sha256"]
        == EXPECTED["promoted_coordinates"]
        and digests["reviewed_candidate_sha256"]
        == EXPECTED["reviewed_candidate"]
        and digests["reverse_overlay_sha256"]
        == EXPECTED["official_candidate"],
        "evidence digest drifted",
    )
    require(sha256_file(STEAM) == EXPECTED["steam"], "Steam archive drifted")
    public = {
        "distribution_policy": {
            "private_decisions_stay_below_tmp": True,
            "private_evidence_stays_below_tmp": True,
            "tracked_builder_contains_dialogue_bodies": False,
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_exact_coordinates": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_test_contains_dialogue_bodies": False,
        },
        "guards": {
            "action_counts": ACTIONS,
            "assembly_canonical_sha256": EXPECTED["assembly"],
            "decision_coordinate_sha256": EXPECTED["decision_coordinates"],
            "decision_file_sha256": EXPECTED["decision_file"],
            "evidence_file_sha256": EXPECTED["evidence_file"],
            "official_candidate_sha256": EXPECTED["official_candidate"],
            "override_coordinate_sha256": EXPECTED["override_coordinates"],
            "promoted_coordinate_sha256": EXPECTED["promoted_coordinates"],
            "reviewed_candidate_sha256": EXPECTED["reviewed_candidate"],
            "reverse_overlay_sha256": EXPECTED["official_candidate"],
            "steam_archive_sha256_after": EXPECTED["steam"],
            "steam_archive_sha256_before": EXPECTED["steam"],
        },
        "method": METHOD,
        "proof": {
            "accepted_assemblies_current_relative_raw_g1n_nonexpanding": True,
            "all_34_sites_reviewed": True,
            "all_changed_record_control_gaps_preserved": True,
            "all_literal_linebreak_counts_preserved": True,
            "automatic_space_or_grammar_repair_by_vm": False,
            "blocked_same_gap_terminal_collisions_not_promoted": True,
            "historical_factuality_reviewed": True,
            "owned_overlap_roots_blocked_without_renewal": True,
            "shared_selector_terminals_repaired": True,
            "speaker_tone_reviewed": True,
        },
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "result": COUNTS,
        "schema": PUBLIC_SCHEMA,
        "scope": {"chunk_id": 0, "selector": 748, "terminal_count": 7},
        "status": "PASS",
        "steam_write_performed": False,
    }
    serialized = json.dumps(public, ensure_ascii=False, sort_keys=True)
    require(
        re.search(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
            serialized,
        ) is None
        and re.search(r"\b\d+:\d+(?::\d+){0,2}\b", serialized) is None,
        "public payload is not source-free",
    )
    return public


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    content = canonical_bytes(build_public()) + b"\n"
    require(
        sha256_bytes(content) == EXPECTED["public_file"],
        "public bytes drifted",
    )
    if args.check:
        require(
            PUBLIC_OUTPUT.read_bytes() == content,
            "tracked public report drifted",
        )
    else:
        PUBLIC_OUTPUT.write_bytes(content)
    print("selector748 chunk0 review: PASS sites=34 promoted=49 blocked=19")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
