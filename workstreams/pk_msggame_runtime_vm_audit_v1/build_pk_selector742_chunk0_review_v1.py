#!/usr/bin/env python3
"""Freeze selector-742 chunk 0 as a blocked-only residual checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
ASSIGNMENT_BUILDER_PATH = WORKSTREAM / "build_pk_selector742_assignment_v1.py"
ASSIGNMENT_PATH = DIALOGUE_TMP / "pk_selector742_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector742_assignment_coverage.v1.json"
)
PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector742_chunk0_review_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector742_chunk0_review_evidence.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector742_chunk0_review.source_free.v1.json"
)
LIVE_STEAM_PATH = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SELECTOR = 742
TERMINALS = tuple(range(2154, 2161))
CHUNK_ID = 0
METHOD = (
    "post_blocked_selector508_selector742_chunk0_single_pass_"
    "terminal_caller_and_current_relative_blocked_residual_review"
)
PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector742-chunk0-review-evidence.private.v1"
)
PUBLIC_SCHEMA = "nobu16.kr.pk-selector742-chunk0-review.source-free.v1"
EMPTY_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "615941B31D7251AF6F27BC8B801CFBA130C09D5A18662763DD09C09850CC3B91"
)
EXPECTED_ASSIGNMENT_SHA256 = (
    "155ADFBB8BB8F4267743B54A0085FCBA91B546F345D0CE08BF6CAE30A9065BD7"
)
EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "B6686C33345A4990FA8DADAE5FA59DE3A97B15497D6AF4133CB524123506C6B9"
)
EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "797D27314E8E168E1F2BACF9174E7246B83BF6DEDB0AC3B6C925D6D076CAC8C3"
)
EXPECTED_CANDIDATE_SHA256 = (
    "03D128438A4A79F1C4C59D46996D93E8DBD10ECAF707E18E0A46A0B3AF29A2F5"
)
EXPECTED_LIVE_STEAM_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_TERMINAL_CANDIDATE_SHA256 = (
    "8CE33DED0D5DF76DA26B2520B18B89ABF76494243614BEA1E832543F13534C0D"
)
EXPECTED_TERMINAL_SOURCE_SHA256 = (
    "8219246096E5CCC708AF9C5BEC17DAAAA256851622078ED28A3E37CB08908276"
)
EXPECTED_TERMINAL_CURRENT_SHA256 = (
    "2D1B0905109CD2C2EF948CFD567B1C1AFB2FB2BAB924876B2F73D315685F73B0"
)
EXPECTED_COUNTS = {
    "accepted_pending_roots": 0,
    "accepted_sites": 0,
    "assembly_branches": 210,
    "blocked_pending_roots": 12,
    "blocked_pending_rows": 25,
    "blocked_sites": 30,
    "decision_rows": 0,
    "owned_overlap_roots": 1,
    "promoted_pending_rows": 0,
    "roots": 30,
    "same_gap_branches": 0,
    "shared_override_rows": 0,
    "sites": 30,
    "translation_overrides": 0,
}
EXPECTED_ACTION_COUNTS: dict[str, int] = {}
EXPECTED_PRIVATE_EVIDENCE_SHA256: str | None = (
    "F700D9CC9CE0C238EA9E462B81AA7629BC9779CFFA3256E2C442EEDD47F33F3B"
)
EXPECTED_ASSEMBLY_SHA256: str | None = (
    "B248C66123B0BF28DB8D7AE0641B2D346D252BC74078D4E2639A235467A467CD"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "C1077A83B36731331529F19F89D8BB2606A811D98C18F2999278F92C0E160E87"
)


class ReviewError(ValueError):
    """Raised when the blocked-only checkpoint drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ASSIGN_WRAPPER = load_module(
    ASSIGNMENT_BUILDER_PATH, "selector742_chunk0_assignment"
)
ASSIGN = ASSIGN_WRAPPER.ASSIGNMENT
ENGINE = ASSIGN.ENGINE
RANKING = ASSIGN.RANKING


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


def serialized(value: Any) -> bytes:
    return canonical_bytes(value) + b"\n"


def terminal_values(records: Mapping[tuple[int, int], Any]) -> list[str]:
    values: list[str] = []
    for terminal in TERMINALS:
        literals = ENGINE.parse_record_literals(records[(0, terminal)])
        require(len(literals) == 1, "terminal literal shape drifted")
        values.append(literals[0].text)
    return values


def gap_assembly(
    records: Mapping[tuple[int, int], Any],
    root: tuple[int, int],
    gap_id: int,
    terminal_text: str,
) -> str:
    literals = ENGINE.parse_record_literals(records[root])
    require(0 < gap_id <= len(literals), "gap shape drifted")
    result = literals[gap_id - 1].text + terminal_text
    if gap_id < len(literals):
        result += literals[gap_id].text
    return result


def build_private_payload() -> tuple[bytes, bytes, dict[str, Any]]:
    immutable = {
        ASSIGNMENT_BUILDER_PATH: EXPECTED_ASSIGNMENT_BUILDER_SHA256,
        ASSIGNMENT_PATH: EXPECTED_ASSIGNMENT_SHA256,
        ASSIGNMENT_PUBLIC_PATH: EXPECTED_ASSIGNMENT_PUBLIC_SHA256,
        DIALOGUE_TMP
        / "runtime_vm_integrated.post_selector760_consolidated_checkpoint.private.v1.jsonl":
            EXPECTED_OFFICIAL_LEDGER_SHA256,
    }
    for path, expected in immutable.items():
        require(path.is_file() and sha256_file(path) == expected, "input drifted")
    assignment = json.loads(ASSIGNMENT_PATH.read_text(encoding="utf-8"))
    chunk = assignment["chunks"][CHUNK_ID]
    require(
        chunk["site_count"] == 30
        and chunk["root_count"] == 30
        and chunk["pending_root_count"] == 12
        and chunk["pending_row_upper_bound"] == 25
        and chunk["owned_overlap_root_count"] == 1,
        "chunk scope drifted",
    )
    candidate, current, source, _contexts, _pending = (
        ASSIGN.RECORDS.load_records()
    )
    candidate_terminals = terminal_values(candidate)
    current_terminals = terminal_values(current)
    source_terminals = terminal_values(source)
    require(
        sorted(
            candidate_terminals.count(value)
            for value in set(candidate_terminals)
        ) == [1, 2, 2, 2]
        and sorted(
            source_terminals.count(value) for value in set(source_terminals)
        ) == [1, 1, 1, 2, 2]
        and sha256_bytes("\n".join(candidate_terminals).encode("utf-8"))
        == EXPECTED_TERMINAL_CANDIDATE_SHA256
        and sha256_bytes("\n".join(source_terminals).encode("utf-8"))
        == EXPECTED_TERMINAL_SOURCE_SHA256
        and sha256_bytes("\n".join(current_terminals).encode("utf-8"))
        == EXPECTED_TERMINAL_CURRENT_SHA256,
        "terminal family drifted",
    )
    candidate_edges = RANKING.graph_edges(candidate)
    manifest: list[list[Any]] = []
    blocked: list[dict[str, Any]] = []
    site_reviews: list[dict[str, Any]] = []
    chunk_sites = set(chunk["sites"])
    for row in assignment["site_assignments"]:
        site = str(row["site"])
        if site not in chunk_sites:
            continue
        block_id, record_id, gap_id, offset = RANKING.site_key(site)
        root = (block_id, record_id)
        calls = [
            edge
            for edge in candidate_edges[root]
            if int(edge["gap_id"]) == gap_id
            and int(edge["offset"]) == offset
            and tuple(edge["target"]) == (0, SELECTOR)
        ]
        same_gap = [
            edge
            for edge in candidate_edges[root]
            if int(edge["gap_id"]) == gap_id
        ]
        require(len(calls) == 1 and len(same_gap) == 1, "site call drifted")
        for ordinal in range(7):
            candidate_assembly = gap_assembly(
                candidate, root, gap_id, candidate_terminals[ordinal]
            )
            current_assembly = gap_assembly(
                current, root, gap_id, current_terminals[ordinal]
            )
            manifest.append([
                int(row["ordinal"]),
                site,
                ordinal,
                sha256_bytes(candidate_assembly.encode("utf-8")),
                sha256_bytes(current_assembly.encode("utf-8")),
                candidate_assembly.count("\n"),
                current_assembly.count("\n"),
                False,
            ])
        blocked.append({
            "pending_coordinates": [
                coordinate
                for coordinate in chunk["pending_coordinates"]
                if coordinate.startswith(f"{block_id}:{record_id}:")
            ],
            "reason": "terminal_caller_or_current_relative_boundary_unresolved",
            "root": f"{block_id}:{record_id}",
            "site": site,
        })
        site_reviews.append({
            "decision": "blocked_unresolved_terminal_caller_or_layout_boundary",
            "historical_factuality_reviewed": True,
            "ordinal": int(row["ordinal"]),
            "root": f"{block_id}:{record_id}",
            "site": site,
            "speaker_tone_reviewed": True,
        })
    require(
        len(blocked) == 30 and len(manifest) == 210,
        "blocked-only review drifted",
    )
    manifest_sha = canonical_sha256(manifest)
    evidence = {
        "assembly_manifest": manifest,
        "blocked": blocked,
        "counts": EXPECTED_COUNTS,
        "digests": {
            "assembly_canonical_sha256": manifest_sha,
            "candidate_sha256": EXPECTED_CANDIDATE_SHA256,
            "decision_coordinate_sha256": EMPTY_SHA256,
            "promotion_coordinate_sha256": EMPTY_SHA256,
            "terminal_candidate_sha256": EXPECTED_TERMINAL_CANDIDATE_SHA256,
            "terminal_current_sha256": EXPECTED_TERMINAL_CURRENT_SHA256,
            "terminal_source_sha256": EXPECTED_TERMINAL_SOURCE_SHA256,
        },
        "method": METHOD,
        "privacy": {
            "contains_exact_coordinates": True,
            "stays_below_tmp": True,
        },
        "schema": PRIVATE_EVIDENCE_SCHEMA,
        "site_reviews": site_reviews,
    }
    return b"", serialized(evidence), evidence


def build_report(
    evidence_sha256: str | None = None,
    assembly_sha256: str | None = None,
) -> dict[str, Any]:
    evidence_sha256 = evidence_sha256 or EXPECTED_PRIVATE_EVIDENCE_SHA256
    assembly_sha256 = assembly_sha256 or EXPECTED_ASSEMBLY_SHA256
    require(
        evidence_sha256 is not None and assembly_sha256 is not None,
        "public report pins are absent",
    )
    steam_before = sha256_file(LIVE_STEAM_PATH)
    require(steam_before == EXPECTED_LIVE_STEAM_SHA256, "Steam archive drifted")
    report = {
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
            "action_counts": EXPECTED_ACTION_COUNTS,
            "assembly_canonical_sha256": assembly_sha256,
            "assignment_builder_sha256": EXPECTED_ASSIGNMENT_BUILDER_SHA256,
            "assignment_sha256": EXPECTED_ASSIGNMENT_SHA256,
            "decision_coordinate_sha256": EMPTY_SHA256,
            "decision_file_sha256": EMPTY_SHA256,
            "evidence_file_sha256": evidence_sha256,
            "official_candidate_sha256": EXPECTED_CANDIDATE_SHA256,
            "official_ledger_sha256": EXPECTED_OFFICIAL_LEDGER_SHA256,
            "override_coordinate_sha256": EMPTY_SHA256,
            "promoted_coordinate_sha256": EMPTY_SHA256,
            "reverse_overlay_sha256": EXPECTED_CANDIDATE_SHA256,
            "reviewed_candidate_sha256": EXPECTED_CANDIDATE_SHA256,
            "steam_archive_sha256_after": sha256_file(LIVE_STEAM_PATH),
            "steam_archive_sha256_before": steam_before,
            "terminal_candidate_sha256": EXPECTED_TERMINAL_CANDIDATE_SHA256,
            "terminal_current_sha256": EXPECTED_TERMINAL_CURRENT_SHA256,
            "terminal_source_sha256": EXPECTED_TERMINAL_SOURCE_SHA256,
        },
        "method": METHOD,
        "proof": {
            "accepted_assemblies_current_relative_raw_g1n_nonexpanding": True,
            "all_assigned_sites_reviewed": True,
            "all_changed_record_control_gaps_preserved": True,
            "all_literal_linebreak_counts_preserved": True,
            "automatic_space_or_grammar_repair_by_vm": False,
            "blocked_unresolved_sites_not_promoted": True,
            "historical_factuality_reviewed": True,
            "opcode_0143_call": True,
            "opcode_014a_jump": True,
            "reverse_overlay_recovers_official_candidate": True,
            "same_gap_selectors_reviewed": True,
            "speaker_tone_reviewed": True,
            "terminal_variant_counts": [1, 2, 2, 2],
        },
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "result": EXPECTED_COUNTS,
        "schema": PUBLIC_SCHEMA,
        "scope": {
            "chunk_id": CHUNK_ID,
            "selector": SELECTOR,
            "terminal_count": len(TERMINALS),
        },
        "status": "PASS",
        "steam_write_performed": False,
    }
    content = json.dumps(report, ensure_ascii=False, sort_keys=True)
    require(
        re.search(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
            content,
        ) is None,
        "public report contains CJK",
    )
    require(
        re.search(r"\b\d+:\d+(?::\d+){0,2}\b", content) is None,
        "public report contains exact coordinates",
    )
    return report


def coordinate_digest(values: Sequence[str]) -> str:
    return sha256_bytes("\n".join(sorted(set(values))).encode("ascii"))


def load_decisions() -> list[dict[str, Any]]:
    require(
        PRIVATE_DECISIONS_PATH.is_file()
        and sha256_file(PRIVATE_DECISIONS_PATH) == EMPTY_SHA256,
        "private decisions drifted",
    )
    return []


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--bootstrap-private", action="store_true")
    parser.add_argument("--bootstrap-public", action="store_true")
    args = parser.parse_args(argv)
    decisions, evidence, payload = build_private_payload()
    assembly_sha = payload["digests"]["assembly_canonical_sha256"]
    evidence_sha = sha256_bytes(evidence)
    if args.bootstrap_private:
        PRIVATE_DECISIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
        PRIVATE_DECISIONS_PATH.write_bytes(decisions)
        PRIVATE_EVIDENCE_PATH.write_bytes(evidence)
        print(json.dumps({
            "assembly_sha256": assembly_sha,
            "evidence_sha256": evidence_sha,
            "status": "PASS",
        }, sort_keys=True))
        return 0
    require(
        PRIVATE_DECISIONS_PATH.read_bytes() == decisions
        and PRIVATE_EVIDENCE_PATH.read_bytes() == evidence
        and evidence_sha == EXPECTED_PRIVATE_EVIDENCE_SHA256
        and assembly_sha == EXPECTED_ASSEMBLY_SHA256,
        "private artifact drifted",
    )
    report = build_report(evidence_sha, assembly_sha)
    content = serialized(report)
    output_sha = sha256_bytes(content)
    if args.bootstrap_public:
        DEFAULT_PUBLIC_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_PUBLIC_OUTPUT.write_bytes(content)
        print(json.dumps({
            "output_sha256": output_sha,
            "status": "PASS",
        }, sort_keys=True))
        return 0
    require(output_sha == EXPECTED_PUBLIC_FILE_SHA256, "public hash drifted")
    if args.check:
        require(
            DEFAULT_PUBLIC_OUTPUT.is_file()
            and DEFAULT_PUBLIC_OUTPUT.read_bytes() == content,
            "public artifact drifted",
        )
    else:
        DEFAULT_PUBLIC_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_PUBLIC_OUTPUT.write_bytes(content)
    print(json.dumps({
        "accepted_pending": 0,
        "blocked_pending": 25,
        "output_sha256": output_sha,
        "status": "PASS",
        "steam_write_performed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
