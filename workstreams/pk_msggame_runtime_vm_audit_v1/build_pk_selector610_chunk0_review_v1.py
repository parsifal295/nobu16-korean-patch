#!/usr/bin/env python3
"""Validate the frozen, source-free selector-610 chunk-0 review."""

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
ASSIGNMENT_PATH = DIALOGUE_TMP / "pk_selector610_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector610_assignment_coverage.v1.json"
)
PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector610_chunk0_review_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector610_chunk0_review_evidence.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector610_chunk0_review.source_free.v1.json"
)
LIVE_STEAM_PATH = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

METHOD = (
    "fc157a_selector610_chunk0_full_seven_branch_review_with_"
    "same_gap_chain_blocks_and_owned_dependency_renewal"
)
PUBLIC_SCHEMA = "nobu16.kr.pk-selector610-chunk0-review.source-free.v1"
PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector610-chunk0-review-decision.private.v1"
)
PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector610-chunk0-review-evidence.private.v1"
)
EXPECTED_ASSIGNMENT_SHA256 = (
    "50A4234CC7207FFF4BCC3049532EC78502E1E8F14565CF1FBFC5399A88D4D036"
)
EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "FD98F9289C6F1D429BF03B53252E9C1846262A29419E97ECDCE26695D91E9C2F"
)
EXPECTED_OFFICIAL_CANDIDATE_SHA256 = (
    "07E65E6338D32C1FD13F17408F82A4133E55541C722874632948C7B36C909805"
)
EXPECTED_LIVE_STEAM_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_DECISION_FILE_SHA256 = (
    "EF6679D24898A4EB87FEBDF2AFBF2AC47FB6EBEC2253D9C52091C22751F3012C"
)
EXPECTED_EVIDENCE_FILE_SHA256 = (
    "35947BFF399DC9B1263B8D10EE54C1D71F9A034D0AE62F4796608D0BFE6D2785"
)
EXPECTED_PUBLIC_FILE_SHA256 = (
    "F8826430F6B48D985A93021E44F655430A0F1CF830B0BF0B38CE910F5249BAD2"
)
EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "E2D029B99A6318DD8F13CBC01777661CAA4054F5AD786D320DD0603622C5C584"
)
EXPECTED_ASSEMBLY_SHA256 = (
    "CBB0ED678433489A6AE6B7B37A0836D9CCAB82B5DCC45CDBCC29A9CA477E4D39"
)
EXPECTED_DEPENDENCY_ASSEMBLY_SHA256 = (
    "4AE8C2AA0DE30752076CDC06BA1E5AAA0DEC3B1CF7486FE36D9F8218BEFC2774"
)
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "3ACAFE0DEC089AF7DA236D4BCBE6B166DB7AEE3FAFEA4768EFF0AE6039E71AF5"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "3AAC8562FCE4A54446990EED976537C16DEF4FC190D0186751121DEBA87066D7"
)
EXPECTED_PROMOTED_COORDINATE_SHA256 = (
    "8A75D66B2C3B9DEA57B4DE23479ECA4AAF0C37025A8A62E1723FB8FB1B395B15"
)
EXPECTED_COUNTS = {
    "accepted_pending_roots": 25,
    "accepted_sites": 60,
    "assembly_branches": 539,
    "blocked_pending_roots": 11,
    "blocked_pending_rows": 25,
    "blocked_sites": 17,
    "decision_rows": 104,
    "dependency_assemblies": 28,
    "dependency_renewal_rows": 3,
    "owned_overlap_roots": 4,
    "promoted_pending_rows": 66,
    "roots": 77,
    "sites": 77,
    "translation_overrides": 61,
}
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 42,
    "translation_override_and_runtime_promotion": 24,
    "translation_override_and_verification_renewal": 37,
    "verification_renewal": 1,
}


class ReviewError(ValueError):
    """Raised when the frozen review evidence drifts."""


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


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"object expected: {path}")
    return value


def load_decisions() -> tuple[list[dict[str, Any]], bytes]:
    content = PRIVATE_DECISIONS_PATH.read_bytes()
    require(
        sha256_bytes(content) == EXPECTED_DECISION_FILE_SHA256,
        "private decision hash drifted",
    )
    rows = [
        json.loads(line.decode("utf-8"))
        for line in content.splitlines()
        if line
    ]
    require(len(rows) == EXPECTED_COUNTS["decision_rows"], "decision count drifted")
    require(
        len({row["coordinate"] for row in rows}) == len(rows),
        "duplicate decision coordinate",
    )
    require(
        all(
            row.get("schema") == PRIVATE_DECISION_SCHEMA
            and row.get("runtime_review") == "verified"
            and row.get("fresh_semantic_review") == "approved"
            and row.get("historical_factuality_review") == "approved"
            and row.get("speaker_tone_review") == "approved"
            and row.get("layout_review")
            == "current_relative_raw_g1n_nonexpanding"
            for row in rows
        ),
        "decision approval drifted",
    )
    require(
        Counter(row["action"] for row in rows) == Counter(EXPECTED_ACTION_COUNTS),
        "decision action counts drifted",
    )
    return rows, content


def validate_evidence(
    evidence: Mapping[str, Any], decisions: Sequence[Mapping[str, Any]]
) -> None:
    require(
        evidence.get("schema") == PRIVATE_EVIDENCE_SCHEMA
        and evidence.get("method") == METHOD
        and evidence.get("counts") == EXPECTED_COUNTS,
        "evidence header or counts drifted",
    )
    manifest = evidence["assembly_manifest"]
    reviews = evidence["site_reviews"]
    dependencies = evidence["dependency_assembly_manifest"]
    require(
        len(manifest) == EXPECTED_COUNTS["assembly_branches"]
        and canonical_sha256(manifest) == EXPECTED_ASSEMBLY_SHA256
        and len(reviews) == EXPECTED_COUNTS["sites"]
        and sum(len(row["assemblies"]) for row in reviews)
        == EXPECTED_COUNTS["assembly_branches"],
        "site assembly evidence drifted",
    )
    decision_counts = Counter(row["decision"] for row in reviews)
    require(
        decision_counts["blocked_same_gap_complete_ending_collision"]
        == EXPECTED_COUNTS["blocked_sites"]
        and decision_counts["rewrite"] + decision_counts["keep"]
        == EXPECTED_COUNTS["accepted_sites"],
        "site decision partition drifted",
    )
    for review in reviews:
        blocked = (
            review["decision"]
            == "blocked_same_gap_complete_ending_collision"
        )
        require(
            review["historical_factuality_reviewed"] is True
            and review["speaker_tone_reviewed"] is True
            and all(
                branch["line_count_match"] is True
                and (
                    branch["grammar_and_spacing_proven"] is False
                    if blocked
                    else branch["grammar_and_spacing_proven"] is True
                    and branch[
                        "current_relative_raw_g1n_nonexpanding"
                    ]
                    is True
                )
                for branch in review["assemblies"]
            ),
            "site branch proof drifted",
        )
    require(
        len(dependencies) == EXPECTED_COUNTS["dependency_assemblies"]
        and canonical_sha256(dependencies)
        == EXPECTED_DEPENDENCY_ASSEMBLY_SHA256
        and all(row[-1] is True for row in dependencies),
        "dependency assembly evidence drifted",
    )
    blocked = set(evidence["blocked"]["pending_coordinates"])
    decision_coordinates = {str(row["coordinate"]) for row in decisions}
    require(
        len(blocked) == EXPECTED_COUNTS["blocked_pending_rows"]
        and blocked.isdisjoint(decision_coordinates),
        "blocked coordinate partition drifted",
    )
    digests = evidence["digests"]
    require(
        digests["assembly_canonical_sha256"] == EXPECTED_ASSEMBLY_SHA256
        and digests["dependency_assembly_canonical_sha256"]
        == EXPECTED_DEPENDENCY_ASSEMBLY_SHA256
        and digests["decision_coordinate_sha256"]
        == EXPECTED_DECISION_COORDINATE_SHA256
        and digests["override_coordinate_sha256"]
        == EXPECTED_OVERRIDE_COORDINATE_SHA256
        and digests["promoted_coordinate_sha256"]
        == EXPECTED_PROMOTED_COORDINATE_SHA256
        and digests["reviewed_candidate_sha256"]
        == EXPECTED_REVIEWED_CANDIDATE_SHA256
        and digests["reverse_overlay_sha256"]
        == EXPECTED_OFFICIAL_CANDIDATE_SHA256,
        "evidence digest drifted",
    )


def build_public(
    *,
    evidence: Mapping[str, Any],
    decisions_content: bytes,
    evidence_content: bytes,
    steam_sha256: str,
) -> dict[str, Any]:
    public = {
        "distribution_policy": {
            "private_decisions_stay_below_tmp": True,
            "private_evidence_stays_below_tmp": True,
            "tracked_builder_contains_dialogue_bodies": False,
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_exact_coordinates": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_test_contains_dialogue_bodies": False,
            "tracked_validator_uses_frozen_private_hashes": True,
        },
        "guards": {
            "action_counts": dict(sorted(EXPECTED_ACTION_COUNTS.items())),
            "assembly_canonical_sha256": EXPECTED_ASSEMBLY_SHA256,
            "decision_coordinate_sha256":
            EXPECTED_DECISION_COORDINATE_SHA256,
            "decision_file_sha256": sha256_bytes(decisions_content),
            "dependency_assembly_canonical_sha256":
            EXPECTED_DEPENDENCY_ASSEMBLY_SHA256,
            "evidence_file_sha256": sha256_bytes(evidence_content),
            "official_candidate_sha256": EXPECTED_OFFICIAL_CANDIDATE_SHA256,
            "override_coordinate_sha256":
            EXPECTED_OVERRIDE_COORDINATE_SHA256,
            "promoted_coordinate_sha256":
            EXPECTED_PROMOTED_COORDINATE_SHA256,
            "reviewed_candidate_sha256":
            EXPECTED_REVIEWED_CANDIDATE_SHA256,
            "reverse_overlay_sha256": EXPECTED_OFFICIAL_CANDIDATE_SHA256,
            "steam_archive_sha256_after": steam_sha256,
            "steam_archive_sha256_before": steam_sha256,
        },
        "method": METHOD,
        "proof": {
            "accepted_assemblies_current_relative_raw_g1n_nonexpanding": True,
            "all_77_sites_reviewed": True,
            "all_changed_record_control_gaps_preserved": True,
            "all_literal_linebreak_counts_preserved": True,
            "automatic_space_or_grammar_repair_by_vm": False,
            "blocked_same_gap_complete_ending_collisions_not_promoted": True,
            "historical_factuality_reviewed": True,
            "owned_dependency_assemblies_verified": True,
            "reverse_overlay_recovers_official_candidate": True,
            "speaker_tone_reviewed": True,
        },
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "result": dict(EXPECTED_COUNTS),
        "schema": PUBLIC_SCHEMA,
        "scope": {"chunk_id": 0, "selector": 610, "terminal_count": 7},
        "status": "PASS",
        "steam_write_performed": False,
    }
    assert_source_free(public)
    return public


def assert_source_free(value: Any) -> None:
    serialized = json.dumps(value, ensure_ascii=False, sort_keys=True)
    require(
        re.search(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
            serialized,
        )
        is None,
        "public report contains source-bearing text",
    )
    require(
        re.search(r"\b\d+:\d+(?::\d+){0,2}\b", serialized) is None,
        "public report contains an exact coordinate",
    )


def build_outputs() -> dict[str, Any]:
    require(
        sha256_file(ASSIGNMENT_PATH) == EXPECTED_ASSIGNMENT_SHA256
        and sha256_file(ASSIGNMENT_PUBLIC_PATH)
        == EXPECTED_ASSIGNMENT_PUBLIC_SHA256,
        "assignment artifacts drifted",
    )
    decisions, decisions_content = load_decisions()
    evidence_content = PRIVATE_EVIDENCE_PATH.read_bytes()
    require(
        sha256_bytes(evidence_content) == EXPECTED_EVIDENCE_FILE_SHA256,
        "private evidence hash drifted",
    )
    evidence = json.loads(evidence_content.decode("utf-8"))
    validate_evidence(evidence, decisions)
    steam_sha256 = sha256_file(LIVE_STEAM_PATH)
    require(
        steam_sha256 == EXPECTED_LIVE_STEAM_SHA256,
        "live Steam archive drifted",
    )
    public = build_public(
        evidence=evidence,
        decisions_content=decisions_content,
        evidence_content=evidence_content,
        steam_sha256=steam_sha256,
    )
    public_content = canonical_bytes(public) + b"\n"
    require(
        sha256_bytes(public_content) == EXPECTED_PUBLIC_FILE_SHA256,
        "public report bytes drifted",
    )
    return {
        "decisions": decisions,
        "decisions_content": decisions_content,
        "evidence": evidence,
        "evidence_content": evidence_content,
        "public": public,
        "public_content": public_content,
    }


def validate_frozen(outputs: Mapping[str, Any]) -> None:
    require(
        DEFAULT_PUBLIC_OUTPUT.read_bytes() == outputs["public_content"],
        "tracked public report drifted",
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--public-output", type=Path, default=DEFAULT_PUBLIC_OUTPUT)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    require(
        args.public_output.resolve() == DEFAULT_PUBLIC_OUTPUT.resolve(),
        "public output must use its fixed path",
    )
    outputs = build_outputs()
    if args.check:
        validate_frozen(outputs)
    else:
        args.public_output.write_bytes(outputs["public_content"])
    print(
        "selector610 chunk0 review: PASS "
        f"sites={EXPECTED_COUNTS['sites']} "
        f"promoted={EXPECTED_COUNTS['promoted_pending_rows']} "
        f"blocked={EXPECTED_COUNTS['blocked_pending_rows']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
