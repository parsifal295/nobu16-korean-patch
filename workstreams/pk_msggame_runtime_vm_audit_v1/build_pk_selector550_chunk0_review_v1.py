#!/usr/bin/env python3
"""Validate the frozen, source-free selector-550 chunk-0 review."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
ASSIGNMENT = DIALOGUE_TMP / "pk_selector550_assignment.private.v1.json"
ASSIGNMENT_PUBLIC = WORKSTREAM / "public" / "pk_selector550_assignment_coverage.v1.json"
DECISIONS = (
    DIALOGUE_TMP / "semantic_overrides"
    / "pk_selector550_chunk0_review_decisions.private.v1.jsonl"
)
EVIDENCE = DIALOGUE_TMP / "pk_selector550_chunk0_review_evidence.private.v1.json"
PUBLIC_OUTPUT = WORKSTREAM / "public" / "pk_selector550_chunk0_review.source_free.v1.json"
STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin")

METHOD = (
    "selector610_checkpoint_selector550_chunk0_full_seven_branch_"
    "review_with_same_gap_chain_and_dynamic_unit_blocks"
)
PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector550-chunk0-review-decision.private.v1"
)
PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector550-chunk0-review-evidence.private.v1"
)
PUBLIC_SCHEMA = "nobu16.kr.pk-selector550-chunk0-review.source-free.v1"
EXPECTED = {
    "assignment": "A692CAAEFAB77ED85DE5A07F775694ABFDDC1407E01AC158C2C1C4FC861EDFBF",
    "assignment_public": "A98C40EB3414E5F4DC21C264E091761A54C59F90771902A2B611EF13E90D13A8",
    "decision_file": "1CDA6791443B9097D71430ADDB1BD16875C7F9895887C598C8A911D528B79E6D",
    "evidence_file": "EB4A89FC716E2D896C4FD870281ECE7A8F035ECEB8D32CA9B64E55A4BCDC0DE7",
    "public_file": "80DB68BCE758BE1B7154E2CC9EB0ADC67BDE5BDD0602C18A642B21984CBFBD13",
    "official_candidate": "F80EA5958757F097885279BAB53A8456758BB99B1CE47E214FE0F54AB7152807",
    "reviewed_candidate": "38E3F8C73B709E99C46D4AC87E9E9EAF7641B4BFDE457968512A7126E926DB71",
    "assembly": "84EB4452C84D66D717FFABABA8F34B4F2FCEC2F1A9A2789E1ECC5D69BFED11AB",
    "decision_coordinates": "325604BDC3EDFF505C887D35119DDD2DC763310484A495F178A4A245EA981C14",
    "override_coordinates": "953A1CA33C2B9DB7944DF2C30EB41E89063F2A44CFA4E37EB86FFBD8F0E41784",
    "promoted_coordinates": "386BD48847D605632469E320AC0683AD7539F1B955F019ED27885E11E114FA30",
    "steam": "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766",
}
COUNTS = {
    "accepted_sites": 44,
    "assembly_branches": 378,
    "blocked_pending_rows": 14,
    "blocked_sites": 10,
    "decision_rows": 84,
    "promoted_pending_rows": 46,
    "roots": 53,
    "sites": 54,
    "translation_overrides": 43,
}
ACTIONS = {
    "runtime_promotion": 41,
    "translation_override_and_runtime_promotion": 5,
    "translation_override_and_verification_renewal": 38,
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


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def build_public() -> dict[str, Any]:
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
            row["schema"] == PRIVATE_DECISION_SCHEMA
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
        evidence["schema"] == PRIVATE_EVIDENCE_SCHEMA
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
            and review["template_atoms_preserved"] is True
            and all(
                branch["line_count_match"] is True
                and (
                    branch["grammar_and_spacing_proven"] is False
                    if review["decision"].startswith("blocked_")
                    else branch["grammar_and_spacing_proven"] is True
                    and branch["current_relative_raw_g1n_nonexpanding"] is True
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
        and digests["reverse_overlay_sha256"] == EXPECTED["official_candidate"],
        "evidence digest drifted",
    )
    require(sha256_file(STEAM) == EXPECTED["steam"], "live Steam archive drifted")
    public = {
        "distribution_policy": {
            "private_decisions_stay_below_tmp": True,
            "private_evidence_stays_below_tmp": True,
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_exact_coordinates": False,
            "tracked_report_contains_translated_dialogue_text": False,
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
            "all_54_sites_reviewed": True,
            "all_changed_record_control_gaps_preserved": True,
            "all_literal_linebreak_counts_preserved": True,
            "automatic_space_or_grammar_repair_by_vm": False,
            "blocked_unproven_runtime_atoms_not_promoted": True,
            "historical_factuality_reviewed": True,
            "same_gap_selector_chain_reviewed": True,
            "speaker_tone_reviewed": True,
            "template_atoms_preserved": True,
        },
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "result": COUNTS,
        "schema": PUBLIC_SCHEMA,
        "scope": {"chunk_id": 0, "selector": 550, "terminal_count": 7},
        "status": "PASS",
        "steam_write_performed": False,
    }
    serialized = json.dumps(public, ensure_ascii=False, sort_keys=True)
    require(
        re.search(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
            serialized,
        )
        is None
        and re.search(r"\b\d+:\d+(?::\d+){0,2}\b", serialized) is None,
        "public payload is not source-free",
    )
    return public


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    content = canonical_bytes(build_public()) + b"\n"
    require(sha256_bytes(content) == EXPECTED["public_file"], "public bytes drifted")
    if args.check:
        require(PUBLIC_OUTPUT.read_bytes() == content, "tracked report drifted")
    else:
        PUBLIC_OUTPUT.write_bytes(content)
    print("selector550 chunk0 review: PASS sites=54 promoted=46 blocked=14")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
