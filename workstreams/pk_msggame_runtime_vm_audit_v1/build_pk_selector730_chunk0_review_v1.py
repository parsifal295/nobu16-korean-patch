#!/usr/bin/env python3
"""Validate selector-730 chunk 0 and emit its source-free checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
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
PRIVATE_GENERATOR_PATH = (
    TMP / "build_pk_selector730_chunk0_private_review_v1.py"
)
PRIVATE_DECISIONS_PATH = (
    TMP / "semantic_overrides"
    / "pk_selector730_chunk0_review_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_PATH = (
    TMP / "pk_selector730_chunk0_review_evidence.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    PUBLIC / "pk_selector730_chunk0_review.source_free.v1.json"
)

SCHEMA = "nobu16.kr.pk-selector730-chunk0-review.source-free.v1"
METHOD = (
    "post_selector562_selector730_chunk0_shared_cartesian_reference_"
    "single_caller_rewrite_feasibility_review"
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
    "private_generator":
        "25120C16BC3A93C32D338AE5B40D3E27021DF32F8ACE6732E55006882AC97A98",
    "private_decisions":
        "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
    "private_evidence":
        "E9E0D6F66B630C89DF5741809D4452AE3D6A41DC95FA8F66ED7D4715EE5999BF",
    "candidate":
        "B7CBFA388BDD50F60CD5EEF88A63B62D357475925A0A3AA6D7DCA1A191607815",
}
EXPECTED_PUBLIC_SHA256: str | None = (
    "FBBE5314BF89B94EC41F1BA102C1DA02DCA4E7AD000D5996F55FA5C0A6F0673C"
)
EXPECTED_COUNTS = {
    "accepted_pending_roots": 0,
    "accepted_pending_rows": 0,
    "assigned_roots": 21,
    "assigned_sites": 21,
    "blocked_pending_roots": 8,
    "blocked_pending_rows": 12,
    "control_or_tag_change_count": 0,
    "decision_rows": 0,
    "linebreak_change_count": 0,
    "non_display_action_count": 0,
    "owned_overlap_pending_rows": 6,
    "owned_overlap_relation_count": 3,
    "owned_overlap_root_count": 3,
    "pending_cartesian_branches_reused": 392,
    "pending_cartesian_roots": 8,
    "prior_assembly_pending_rows": 10,
    "prior_assembly_root_count": 6,
    "promotion_rows": 0,
    "rewrite_attempt_roots": 8,
    "shared_cartesian_branches_reused": 931,
    "shared_cartesian_roots": 19,
    "source_only_action_count": 0,
    "source_only_site_count": 5,
    "template_pending_rows": 2,
    "template_root_count": 2,
    "terminal_decision_rows": 0,
    "terminal_pending_rows": 7,
    "translation_overrides": 0,
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
        require(
            coordinate.search(value) is None,
            f"exact coordinate leaked at {path}",
        )


def validate_inputs() -> tuple[
    dict[str, Any], dict[str, Any], dict[str, Any]
]:
    immutable = {
        ASSIGNMENT_BUILDER_PATH: EXPECTED_SHA256["assignment_builder"],
        ASSIGNMENT_PATH: EXPECTED_SHA256["assignment_private"],
        ASSIGNMENT_PUBLIC_PATH: EXPECTED_SHA256["assignment_public"],
        SHARED_BUILDER_PATH: EXPECTED_SHA256["shared_builder"],
        SHARED_PRIVATE_PATH: EXPECTED_SHA256["shared_private"],
        SHARED_PUBLIC_PATH: EXPECTED_SHA256["shared_public"],
        PRIVATE_GENERATOR_PATH: EXPECTED_SHA256["private_generator"],
        PRIVATE_DECISIONS_PATH: EXPECTED_SHA256["private_decisions"],
        PRIVATE_EVIDENCE_PATH: EXPECTED_SHA256["private_evidence"],
    }
    for path, expected in immutable.items():
        require(
            path.is_file() and sha256_file(path) == expected,
            f"immutable input drifted: {path}",
        )
    require(
        PRIVATE_DECISIONS_PATH.read_bytes() == b"",
        "blocked review unexpectedly has decisions",
    )
    assignment = load_json(ASSIGNMENT_PATH)
    shared = load_json(SHARED_PRIVATE_PATH)
    evidence = load_json(PRIVATE_EVIDENCE_PATH)
    return assignment, shared, evidence


def validate_assignment(
    assignment: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> None:
    chunk = assignment["chunks"][0]
    require(
        (
            chunk["site_count"],
            chunk["root_count"],
            chunk["pending_root_count"],
            chunk["pending_row_upper_bound"],
            chunk["owned_overlap_root_count"],
            chunk["completed_selector_overlap_relation_count"],
            chunk["prior_assembly_evidence_root_count"],
            chunk["prior_assembly_evidence_pending_row_count"],
            chunk["template_root_count"],
            chunk["same_gap_atom_count"],
            chunk["same_gap_cartesian_branch_count"],
            chunk["workload_weight"],
        ) == (21, 21, 8, 12, 3, 3, 6, 10, 2, 19, 931, 503),
        "chunk0 assignment metrics drifted",
    )
    require(
        sorted(map(len, assignment["identical_template_atoms"])) == [2]
        and assignment["source_only_repair"]["action_count"] == 0
        and len(assignment["source_only_repair"]["sites"]) == 5
        and not assignment["prior_pending_evidence"][
            "automatic_status_promotion_authorized"
        ]
        and not assignment["shared_terminal_ownership"][
            "automatic_status_promotion_authorized"
        ],
        "assignment protection guard drifted",
    )
    observed_coordinates = {
        str(row["coordinate"])
        for row in evidence["pending_semantic_reviews"]
    }
    require(
        observed_coordinates == set(chunk["pending_coordinates"]),
        "pending semantic coverage drifted",
    )


def validate_shared_manifest(
    assignment: Mapping[str, Any],
    shared: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> None:
    chunk_roots = set(assignment["chunks"][0]["roots"])
    pending_roots = {
        ":".join(coordinate.split(":")[:2])
        for coordinate in assignment["chunks"][0]["pending_coordinates"]
    }
    chunk_rows = [
        row for row in shared["cartesian_roots"]
        if row["root"] in chunk_roots
    ]
    pending_rows = [
        row for row in chunk_rows if row["root"] in pending_roots
    ]
    require(
        len(shared["cartesian_roots"]) == 37
        and sum(
            int(row["branch_count"]) for row in shared["cartesian_roots"]
        ) == 1_813
        and len(chunk_rows) == 19
        and sum(int(row["branch_count"]) for row in chunk_rows) == 931
        and len(pending_rows) == 8
        and sum(int(row["branch_count"]) for row in pending_rows) == 392,
        "shared Cartesian partition drifted",
    )
    references = evidence["chunk_cartesian_references"]
    require(
        len(references) == 19
        and all(int(row["branch_count"]) == 49 for row in references)
        and evidence["proof"]["cartesian_branches_recomputed"] == 0
        and evidence["proof"]["shared_manifest_reused"],
        "shared Cartesian evidence was recomputed or incomplete",
    )
    require(
        evidence["digests"]["shared_cartesian_manifest_sha256"]
        == EXPECTED_SHA256["shared_private"]
        and evidence["shared_manifest_guards"] == shared["guards"],
        "shared Cartesian guard drifted",
    )


def validate_semantics_and_protections(
    evidence: Mapping[str, Any],
) -> None:
    require(
        evidence["schema"]
        == "nobu16.kr.pk-selector730-chunk0-review-evidence.private.v1"
        and evidence["method"] == METHOD
        and evidence["counts"] == EXPECTED_COUNTS,
        "private evidence header/count drifted",
    )
    pending_rows = evidence["pending_semantic_reviews"]
    root_rows = evidence["root_reviews"]
    require(
        len(pending_rows) == 12
        and len(root_rows) == 8
        and all(
            row["fresh_semantic_review"] == "approved"
            and row["historical_factuality_review"] == "approved"
            and row["speaker_tone_review"] == "approved"
            and row["jp_source_authoritative"]
            and not row["prior_or_owned_evidence_used_for_semantics"]
            and row["rewrite_attempt_count"] == 1
            and row["translation_override_count"] == 0
            and row["disposition"]
                == "blocked_same_gap_read_only_terminal_collision"
            and set(row["context_record_utf8_sha256"])
                == {"en", "sc", "tc"}
            for row in pending_rows
        )
        and all(
            row["branch_count"] == 49
            and row["caller_rewrite_attempt_count"] == 1
            and row["disposition"] == "blocked_atomic_root"
            and row["shared_manifest_reused"]
            and len(row["ordered_controls"]) == 2
            for row in root_rows
        ),
        "fresh semantic/root disposition drifted",
    )
    terminal_rows = evidence["terminal_manifest"]
    require(
        len(terminal_rows) == 7
        and all(
            row["runtime_review"] == "pending"
            and not row["decision_authorized"]
            and not any(row["context_nonempty"].values())
            for row in terminal_rows
        ),
        "shared terminal read-only contract drifted",
    )
    proof = evidence["proof"]
    require(
        proof == {
            "all_pending_rows_freshly_reviewed": True,
            "cartesian_branches_recomputed": 0,
            "controls_tags_and_linebreaks_preserved": True,
            "owned_or_prior_evidence_automatic_promotion_count": 0,
            "same_gap_partial_pass_authorized": False,
            "shared_manifest_reused": True,
            "template_atom_single_disposition": True,
            "terminal_context_languages_authoritative": False,
            "terminal_rows_read_only": True,
        }
        and evidence["exclusions"] == {
            "non_display_action_count": 0,
            "source_only_action_count": 0,
            "steam_write_performed": False,
        },
        "protection/exclusion proof drifted",
    )


def build_report() -> dict[str, Any]:
    assignment, shared, evidence = validate_inputs()
    validate_assignment(assignment, evidence)
    validate_shared_manifest(assignment, shared, evidence)
    validate_semantics_and_protections(evidence)
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
            "assignment_private_sha256": EXPECTED_SHA256[
                "assignment_private"
            ],
            "candidate_sha256": EXPECTED_SHA256["candidate"],
            "decisions_sha256": EXPECTED_SHA256["private_decisions"],
            "evidence_sha256": EXPECTED_SHA256["private_evidence"],
            "shared_cartesian_manifest_sha256": EXPECTED_SHA256[
                "shared_private"
            ],
        },
        "method": METHOD,
        "proof": {
            "all_pending_rows_freshly_reviewed": True,
            "automatic_promotion_count_zero": True,
            "cartesian_branches_recomputed": 0,
            "controls_tags_and_linebreaks_preserved": True,
            "current_relative_raw_g1n_gate_applied": True,
            "historical_factuality_reviewed": True,
            "same_gap_roots_blocked_atomically": True,
            "shared_cartesian_manifest_reused": True,
            "source_only_action_count_zero": True,
            "speaker_tone_reviewed": True,
            "terminal_rows_pending_read_only": True,
        },
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "result": EXPECTED_COUNTS,
        "schema": SCHEMA,
        "scope": {
            "chunk_id": 0,
            "selector": 730,
            "workload_weight": 503,
        },
        "status": "PASS",
        "steam_write_performed": False,
    }
    assert_source_free(report)
    return report


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_PUBLIC_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    require(
        args.output.resolve() == DEFAULT_PUBLIC_OUTPUT.resolve(),
        "public output path is fixed",
    )
    content = serialized(build_report())
    output_sha256 = sha256_bytes(content)
    if EXPECTED_PUBLIC_SHA256 is not None:
        require(
            output_sha256 == EXPECTED_PUBLIC_SHA256,
            f"public output hash drifted: {output_sha256}",
        )
    if args.check:
        require(
            args.output.is_file() and args.output.read_bytes() == content,
            "public artifact drifted",
        )
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(content)
    print(json.dumps({
        "accepted": 0,
        "blocked": 12,
        "output_sha256": output_sha256,
        "overrides": 0,
        "shared_cartesian_recomputed": 0,
        "status": "PASS",
        "steam_write_performed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
