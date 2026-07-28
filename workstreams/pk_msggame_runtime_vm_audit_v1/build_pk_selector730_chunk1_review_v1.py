#!/usr/bin/env python3
"""Validate selector-730 chunk 1 and emit its source-free checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
PUBLIC = WORKSTREAM / "public"

ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector730_assignment_v1.py"
ASSIGNMENT_PATH = TMP / "pk_selector730_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = PUBLIC / "pk_selector730_assignment_coverage.v1.json"
SHARED_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector730_shared_cartesian_manifest_v1.py"
)
SHARED_PRIVATE_PATH = (
    TMP / "pk_selector730_shared_cartesian_assembly_manifest.private.v1.json"
)
SHARED_PUBLIC_PATH = (
    PUBLIC / "pk_selector730_shared_cartesian_assembly_coverage.v1.json"
)
PRIVATE_DECISIONS_PATH = (
    TMP / "semantic_overrides"
    / "pk_selector730_chunk1_review_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_PATH = (
    TMP / "pk_selector730_chunk1_review_evidence.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    PUBLIC / "pk_selector730_chunk1_review.source_free.v1.json"
)

SCHEMA = "nobu16.kr.pk-selector730-chunk1-review.source-free.v1"
METHOD = (
    "post_selector562_selector730_chunk1_single_pass_semantic_review_"
    "with_frozen_cartesian_reuse"
)
EXPECTED_SHA256 = {
    "assignment_builder":
        "94E9846279014E431832E232509B1C495BEE3D9EFEF01B8D8EBAB687D0968AA8",
    "assignment_private":
        "D9554CC8E6BED91EB9141CFC11F142E389868565AFC7B82B230FC9F931DB4781",
    "assignment_public":
        "07EA6FE891F17C7E4CF22C6C42625D1E224FF606524A2683ED0CA58C767CD454",
    "shared_builder":
        "0F0FF85083A76AF97AF6DA6ECFD5991A1681CBC28FA46C4E847C01D38DB39C32",
    "shared_private":
        "BB00FFACC84CE778AFCEFB5E531B23BDA8BB03CFEE06E42DC885BC164314C173",
    "shared_public":
        "F9F2F82231DD417F397EE05B23C4AFF7FB60056865ABF22B87B99CCFD58A4DE1",
    "private_decisions":
        "9569A9658FE235C60327A01F957EA79B4A3151AA1346242B7DCFEF5C4A780702",
    "private_evidence":
        "6F3A8F0D96B70D101416796C23E9BF42EEFE5552C03E242C23022950247A4BFD",
    "candidate":
        "B7CBFA388BDD50F60CD5EEF88A63B62D357475925A0A3AA6D7DCA1A191607815",
}
EXPECTED_PUBLIC_SHA256: str | None = (
    "F13FF98456662B6AAE56D0B7022E4C089191D1FBEF8B97060EF2B50E65993D38"
)


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
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def serialized(value: Any) -> bytes:
    return canonical_bytes(value) + b"\n"


def load_json(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    require(not raw.startswith(b"\xef\xbb\xbf"), f"BOM rejected: {path}")
    value = json.loads(raw.decode("utf-8", errors="strict"))
    require(isinstance(value, dict), f"object expected: {path}")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_bytes().splitlines():
        if line:
            value = json.loads(line.decode("utf-8", errors="strict"))
            require(isinstance(value, dict), "JSONL row must be an object")
            rows.append(value)
    return rows


def assert_source_free(value: Any, path: str = "$") -> None:
    cjk = re.compile(
        r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
        r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]"
    )
    coordinate = re.compile(r"\b\d+:\d+(?::\d+){0,2}\b")
    if isinstance(value, dict):
        for key, item in value.items():
            assert_source_free(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            assert_source_free(item, f"{path}[{index}]")
    elif isinstance(value, str):
        require(cjk.search(value) is None, f"CJK leaked at {path}")
        require(coordinate.search(value) is None, f"coordinate leaked at {path}")


def validate_inputs() -> tuple[
    dict[str, Any], dict[str, Any], dict[str, Any], list[dict[str, Any]]
]:
    immutable = {
        ASSIGNMENT_BUILDER_PATH: EXPECTED_SHA256["assignment_builder"],
        ASSIGNMENT_PATH: EXPECTED_SHA256["assignment_private"],
        ASSIGNMENT_PUBLIC_PATH: EXPECTED_SHA256["assignment_public"],
        SHARED_BUILDER_PATH: EXPECTED_SHA256["shared_builder"],
        SHARED_PRIVATE_PATH: EXPECTED_SHA256["shared_private"],
        SHARED_PUBLIC_PATH: EXPECTED_SHA256["shared_public"],
        PRIVATE_DECISIONS_PATH: EXPECTED_SHA256["private_decisions"],
        PRIVATE_EVIDENCE_PATH: EXPECTED_SHA256["private_evidence"],
    }
    for path, expected in immutable.items():
        require(
            path.is_file() and sha256_file(path) == expected,
            f"immutable input drifted: {path}",
        )
    return (
        load_json(ASSIGNMENT_PATH),
        load_json(SHARED_PRIVATE_PATH),
        load_json(PRIVATE_EVIDENCE_PATH),
        load_jsonl(PRIVATE_DECISIONS_PATH),
    )


def validate_assignment(
    assignment: Mapping[str, Any],
    shared: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> None:
    chunk = assignment["chunks"][1]
    require(
        (
            chunk["site_count"],
            chunk["root_count"],
            chunk["pending_root_count"],
            chunk["pending_row_upper_bound"],
            chunk["owned_overlap_root_count"],
            chunk["prior_assembly_evidence_root_count"],
            chunk["prior_assembly_evidence_pending_row_count"],
            chunk["template_root_count"],
            chunk["same_gap_atom_count"],
            chunk["same_gap_cartesian_branch_count"],
            chunk["workload_weight"],
        ) == (20, 20, 10, 25, 7, 9, 22, 0, 18, 882, 504),
        "chunk1 assignment metrics drifted",
    )
    require(
        not assignment["prior_pending_evidence"][
            "automatic_status_promotion_authorized"
        ]
        and not assignment["shared_terminal_ownership"][
            "automatic_status_promotion_authorized"
        ]
        and assignment["source_only_repair"]["action_count"] == 0
        and len(assignment["source_only_repair"]["sites"]) == 5
        and len(shared["cartesian_roots"]) == 37
        and sum(
            int(row["branch_count"])
            for row in shared["cartesian_roots"]
        ) == 1813
        and shared["proof"]["semantic_decision_rows"] == 0
        and shared["assignment_partition"]["status"] == "validated",
        "assignment/shared protection guard drifted",
    )
    require(
        set(evidence["accepted_pending_coordinates"])
        | set(evidence["blocked_pending_coordinates"])
        == set(chunk["pending_coordinates"]),
        "pending semantic coverage drifted",
    )


def validate_decisions(
    decisions: Sequence[Mapping[str, Any]],
    evidence: Mapping[str, Any],
) -> None:
    require(
        len(decisions) == 3
        and {str(row["coordinate"]) for row in decisions}
        == set(evidence["accepted_pending_coordinates"])
        and Counter(str(row["action"]) for row in decisions)
        == Counter({
            "runtime_promotion": 2,
            "translation_override_and_runtime_promotion": 1,
        }),
        "decision union drifted",
    )
    for row in decisions:
        body = str(row["reviewed_translation"])
        require(
            row.get("fresh_semantic_review") == "approved"
            and row.get("historical_factuality_review") == "approved"
            and row.get("speaker_tone_review") == "approved"
            and row.get("runtime_review") == "verified"
            and row.get("resource") == "pk_msggame"
            and row.get("layout_review")
            == "current_relative_raw_g1n_nonexpanding"
            and row.get("root_rewrite_attempt_count") == 1
            and sha256_bytes(body.encode("utf-16le"))
            == row.get("reviewed_utf16le_sha256"),
            "decision semantic/layout contract drifted",
        )


def validate_evidence(evidence: Mapping[str, Any]) -> None:
    counts = evidence["counts"]
    require(
        (
            counts["accepted_pending_roots"],
            counts["accepted_pending_rows"],
            counts["blocked_pending_roots"],
            counts["blocked_pending_rows"],
            counts["decision_rows"],
            counts["translation_overrides"],
            counts["same_gap_pending_branches_reused"],
            counts["same_gap_total_branches_reused"],
            counts["source_only_actions"],
            counts["terminal_read_only_rows"],
        ) == (1, 3, 9, 22, 3, 1, 441, 882, 0, 7),
        "review counts drifted",
    )
    proof = evidence["proof"]
    require(
        proof["cartesian_evidence_reused"]
        and proof["cartesian_branches_recomputed"] == 0
        and proof["fresh_semantic_review_limited_to_pending_rows"]
        and proof["maximum_rewrite_attempts_per_root"] == 1
        and proof["same_gap_root_atomicity_preserved"]
        and proof["terminal_records_read_only"]
        and not proof["shared_terminal_modified"]
        and proof["source_only_action_count"] == 0
        and proof["non_display_action_count"] == 0
        and proof["reverse_overlay_recovers_official_candidate"],
        "review proof drifted",
    )


def build_output() -> bytes:
    assignment, shared, evidence, decisions = validate_inputs()
    validate_assignment(assignment, shared, evidence)
    validate_decisions(decisions, evidence)
    validate_evidence(evidence)
    counts = dict(evidence["counts"])
    report = {
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
            "assignment_private_sha256": EXPECTED_SHA256["assignment_private"],
            "candidate_sha256": EXPECTED_SHA256["candidate"],
            "decision_coordinate_sha256":
                evidence["digests"]["decision_coordinate_sha256"],
            "decisions_sha256": EXPECTED_SHA256["private_decisions"],
            "evidence_sha256": EXPECTED_SHA256["private_evidence"],
            "reviewed_candidate_sha256":
                evidence["digests"]["reviewed_candidate_sha256"],
            "shared_cartesian_manifest_sha256":
                EXPECTED_SHA256["shared_private"],
        },
        "method": METHOD,
        "proof": {
            "all_pending_rows_freshly_reviewed": True,
            "automatic_promotion_count_zero": True,
            "cartesian_branches_recomputed": 0,
            "controls_tags_and_linebreaks_preserved": True,
            "current_relative_raw_g1n_gate_applied": True,
            "historical_factuality_reviewed": True,
            "maximum_rewrite_attempts_per_root": 1,
            "same_gap_roots_blocked_atomically": True,
            "shared_cartesian_manifest_reused": True,
            "source_only_action_count_zero": True,
            "speaker_tone_reviewed": True,
            "terminal_rows_pending_read_only": True,
        },
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "result": counts,
        "schema": SCHEMA,
        "scope": {
            "chunk_id": 1,
            "selector": 730,
            "workload_weight": 504,
        },
        "status": "PASS",
        "steam_write_performed": False,
    }
    assert_source_free(report)
    content = serialized(report)
    if EXPECTED_PUBLIC_SHA256 is not None:
        require(
            sha256_bytes(content) == EXPECTED_PUBLIC_SHA256,
            "public output drifted",
        )
    return content


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    content = build_output()
    if args.write:
        DEFAULT_PUBLIC_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_PUBLIC_OUTPUT.write_bytes(content)
    else:
        require(
            DEFAULT_PUBLIC_OUTPUT.is_file()
            and DEFAULT_PUBLIC_OUTPUT.read_bytes() == content,
            "public output not frozen",
        )
    print(json.dumps({
        "accepted_pending": 3,
        "blocked_pending": 22,
        "output_sha256": sha256_bytes(content),
        "status": "PASS",
        "steam_write_performed": False,
    }, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
