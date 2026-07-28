#!/usr/bin/env python3
"""Freeze selector-760 chunk 0 as a blocked-only residual checkpoint."""

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
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


CORE = load_module(
    WORKSTREAM / "build_pk_selector550_chunk1_review_v1.py",
    "selector760_chunk0_review_core",
)
ASSIGN_WRAPPER = load_module(
    WORKSTREAM / "build_pk_selector760_assignment_v1.py",
    "selector760_chunk0_review_assignment",
)
ASSIGN = ASSIGN_WRAPPER.ASSIGNMENT
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.RECORDS.load_records

ASSIGNMENT_PATH = DIALOGUE_TMP / "pk_selector760_assignment.private.v1.json"
PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector760_chunk0_review_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector760_chunk0_review_evidence.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector760_chunk0_review.source_free.v1.json"
)

METHOD = (
    "post_selector1090_selector760_chunk0_single_pass_"
    "terminal_caller_and_same_gap_blocked_residual_review"
)
PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector760-chunk0-review-decision.private.v1"
)
PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector760-chunk0-review-evidence.private.v1"
)
PUBLIC_SCHEMA = "nobu16.kr.pk-selector760-chunk0-review.source-free.v1"
EXPECTED_COUNTS = {
    "accepted_pending_roots": 0,
    "accepted_sites": 0,
    "assembly_branches": 112,
    "blocked_pending_roots": 10,
    "blocked_pending_rows": 31,
    "blocked_sites": 16,
    "decision_rows": 0,
    "promoted_pending_rows": 0,
    "roots": 16,
    "same_gap_branches": 49,
    "shared_override_rows": 0,
    "sites": 16,
    "translation_overrides": 0,
}
EXPECTED_ACTION_COUNTS: dict[str, int] = {}
EMPTY_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "FBE5625F1480AB8FD5C65E349F961F6336A1EA9A4F7C2C74E9579F092B2ACE5B"
)
EXPECTED_ASSIGNMENT_SHA256 = (
    "2D14D2E186E8E4A23B0BC1591B669E76B701071CDFB1A8ACBF93FA15B018C6AB"
)
EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "7DBCAF6DF39C482E6958390A944BF3941576B69F469361129FD46715E89648F5"
)
EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "CDF7539F8E6A6F0D024A7357854A0AFE45E91F3CBD144822E1DEF8730A9A373F"
)
EXPECTED_CANDIDATE_SHA256 = (
    "396A8DF109A0693C439F990049477F5DE6E10720854D73057F3DFA1702002CCF"
)
EXPECTED_LIVE_STEAM_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_TERMINAL_CANDIDATE_SHA256 = (
    "D5B58452C039DA92C6EFD272626BCB73044F9666C0E417EAD4945615CB1FFFD8"
)
EXPECTED_TERMINAL_SOURCE_SHA256 = (
    "400ACD7B78641E3E2D711DBAB61F2131F98DCD836A871FC2D344FB9CFF063307"
)
EXPECTED_PRIVATE_DECISIONS_SHA256 = EMPTY_SHA256
EXPECTED_PRIVATE_EVIDENCE_SHA256: str | None = (
    "0C8F07C1421E03A04441C7E65BB03BF40AEEE50D1E78254725D59558980EF43B"
)
EXPECTED_ASSEMBLY_SHA256: str | None = (
    "5ABD7B6B7FF9494A09DE6F66F758103CE04806F2F3ED5DA03DBC1E4841036D7E"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "F1D9F23621BF784FDF6EBC19EAC14BE88910FA18252F7D7150E2252E2812C90A"
)


def configure_core() -> None:
    CORE.ASSIGNMENT_BUILDER_PATH = (
        WORKSTREAM / "build_pk_selector760_assignment_v1.py"
    )
    CORE.ASSIGNMENT_PATH = ASSIGNMENT_PATH
    CORE.ASSIGNMENT_PUBLIC_PATH = (
        WORKSTREAM / "public" / "pk_selector760_assignment_coverage.v1.json"
    )
    CORE.OFFICIAL_LEDGER_PATH = (
        DIALOGUE_TMP
        / "runtime_vm_integrated.post_selector1090_consolidated_checkpoint.private.v1.jsonl"
    )
    CORE.PRIVATE_DECISIONS_PATH = PRIVATE_DECISIONS_PATH
    CORE.PRIVATE_EVIDENCE_PATH = PRIVATE_EVIDENCE_PATH
    CORE.DEFAULT_PUBLIC_OUTPUT = DEFAULT_PUBLIC_OUTPUT
    CORE.SELECTOR = 760
    CORE.TERMINALS = tuple(range(2175, 2182))
    CORE.CHUNK_ID = 0
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
    CORE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = EXPECTED_CANDIDATE_SHA256
    CORE.EXPECTED_LIVE_STEAM_SHA256 = EXPECTED_LIVE_STEAM_SHA256
    CORE.EXPECTED_PUBLIC_FILE_SHA256 = EXPECTED_PUBLIC_FILE_SHA256
    CORE.EXPECTED_COUNTS = EXPECTED_COUNTS
    CORE.EXPECTED_ACTION_COUNTS = EXPECTED_ACTION_COUNTS
    CORE.EXPECTED_DIGESTS = {
        "assembly": EXPECTED_ASSEMBLY_SHA256,
        "decision": EMPTY_SHA256,
        "override": EMPTY_SHA256,
        "promoted": EMPTY_SHA256,
    }
    CORE.ASSIGN = ASSIGN
    CORE.ENGINE = ASSIGN.ENGINE
    CORE.RANKING = ASSIGN.RANKING
    CORE._EDGE_CACHE.clear()
    CORE._TERMINAL_CACHE.clear()


def terminal_digest(records: Any) -> tuple[int, str]:
    values = [
        CORE.first_literal(records, (0, terminal))
        for terminal in range(2175, 2182)
    ]
    return len(set(values)), CORE.sha256_bytes("\n".join(values).encode("utf-8"))


def build_private_payload() -> tuple[bytes, bytes, dict[str, Any]]:
    configure_core()
    assignment = json.loads(ASSIGNMENT_PATH.read_text(encoding="utf-8"))
    chunk = assignment["chunks"][0]
    candidate, current, source, contexts, _pending = ASSIGN.load_records()
    candidate_shape, candidate_terminal_sha = terminal_digest(candidate)
    source_shape, source_terminal_sha = terminal_digest(source)
    CORE.require(
        candidate_shape == 1
        and source_shape == 2
        and candidate_terminal_sha == EXPECTED_TERMINAL_CANDIDATE_SHA256
        and source_terminal_sha == EXPECTED_TERMINAL_SOURCE_SHA256,
        "terminal family drifted",
    )
    graph = CORE.graph_edges_cached(candidate)
    site_reviews: list[dict[str, Any]] = []
    assembly_manifest: list[list[Any]] = []
    same_gap_branches = 0
    blocked: list[dict[str, Any]] = []
    for assignment_row in assignment["site_assignments"]:
        site = str(assignment_row["site"])
        if site not in set(chunk["sites"]):
            continue
        block_id, record_id, gap_id, _offset = CORE.RANKING.site_key(site)
        root = (block_id, record_id)
        targets = [
            f"{int(edge['target'][0])}:{int(edge['target'][1])}"
            for edge in graph[root]
            if int(edge["gap_id"]) == gap_id
        ]
        assemblies: list[dict[str, Any]] = []
        for ordinal in range(7):
            reviewed_assembly = CORE.gap_assembly(
                records=candidate,
                source=source,
                root=root,
                gap_id=gap_id,
                ordinal=ordinal,
            )
            current_assembly = CORE.gap_assembly(
                records=current,
                source=source,
                root=root,
                gap_id=gap_id,
                ordinal=ordinal,
            )
            reviewed_lines = CORE.BASE.line_metrics(reviewed_assembly)
            current_lines = CORE.BASE.line_metrics(current_assembly)
            width_pass = CORE.BASE.current_relative_nonexpanding(
                reviewed_lines, current_lines
            )
            same_gap_branches += int(len(targets) > 1)
            assemblies.append({
                "current_assembly": current_assembly,
                "current_lines": current_lines,
                "current_relative_raw_g1n_nonexpanding": width_pass,
                "grammar_and_spacing_proven": False,
                "line_count_match": len(reviewed_lines) == len(current_lines),
                "ordinal": ordinal,
                "reviewed_assembly": reviewed_assembly,
                "reviewed_lines": reviewed_lines,
                "same_gap_targets": targets,
            })
            assembly_manifest.append([
                int(assignment_row["ordinal"]),
                site,
                ordinal,
                CORE.sha256_bytes(reviewed_assembly.encode("utf-8")),
                CORE.sha256_bytes(current_assembly.encode("utf-8")),
                len(reviewed_lines) == len(current_lines),
                width_pass,
                False,
            ])
        multilingual = {}
        for language, records in {
            "en": contexts["en"],
            "jp": source,
            "sc": contexts["sc"],
            "tc": contexts["tc"],
        }.items():
            available = root in records
            joined = ""
            if available:
                joined = "\n".join(
                    literal.text
                    for literal in CORE.ENGINE.parse_record_literals(records[root])
                )
            multilingual[language] = {
                "available": available,
                "joined_utf8_sha256": CORE.sha256_bytes(joined.encode("utf-8")),
            }
        site_reviews.append({
            "assemblies": assemblies,
            "decision": "blocked_unresolved_terminal_caller_or_same_gap_boundary",
            "historical_factuality_reviewed": True,
            "multilingual_context": multilingual,
            "ordinal": int(assignment_row["ordinal"]),
            "root": f"{block_id}:{record_id}",
            "site": site,
            "speaker_tone_reviewed": True,
        })
        blocked.append({
            "pending_coordinates": [
                coordinate
                for coordinate in chunk["pending_coordinates"]
                if coordinate.startswith(f"{block_id}:{record_id}:")
            ],
            "reason": "terminal_caller_or_same_gap_boundary_unresolved",
            "root": f"{block_id}:{record_id}",
            "site": site,
        })
    assembly_sha = CORE.canonical_sha256(assembly_manifest)
    CORE.require(
        len(site_reviews) == 16
        and len(assembly_manifest) == 112
        and same_gap_branches == 49,
        "blocked-only scope drifted",
    )
    evidence = {
        "assembly_manifest": assembly_manifest,
        "blocked": blocked,
        "counts": EXPECTED_COUNTS,
        "digests": {
            "assembly_canonical_sha256": assembly_sha,
            "decision_coordinate_sha256": EMPTY_SHA256,
            "override_coordinate_sha256": EMPTY_SHA256,
            "promoted_coordinate_sha256": EMPTY_SHA256,
            "reviewed_candidate_sha256": EXPECTED_CANDIDATE_SHA256,
            "reverse_overlay_sha256": EXPECTED_CANDIDATE_SHA256,
        },
        "inputs": {
            "assignment_sha256": EXPECTED_ASSIGNMENT_SHA256,
            "candidate_sha256": EXPECTED_CANDIDATE_SHA256,
            "official_ledger_sha256": EXPECTED_OFFICIAL_LEDGER_SHA256,
        },
        "method": METHOD,
        "privacy": {
            "contains_commercial_source_text": True,
            "stays_below_tmp": True,
        },
        "schema": PRIVATE_EVIDENCE_SCHEMA,
        "site_reviews": site_reviews,
    }
    return b"", CORE.serialized(evidence), evidence


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--bootstrap-private", action="store_true")
    parser.add_argument("--bootstrap-public", action="store_true")
    args = parser.parse_args(argv)
    decisions, evidence, payload = build_private_payload()
    if args.bootstrap_private:
        PRIVATE_DECISIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
        PRIVATE_DECISIONS_PATH.write_bytes(decisions)
        PRIVATE_EVIDENCE_PATH.write_bytes(evidence)
        print(json.dumps({
            "assembly_sha256":
                payload["digests"]["assembly_canonical_sha256"],
            "evidence_sha256": CORE.sha256_bytes(evidence),
            "status": "PASS",
        }, sort_keys=True))
        return 0
    CORE.require(
        PRIVATE_DECISIONS_PATH.read_bytes() == decisions
        and PRIVATE_EVIDENCE_PATH.read_bytes() == evidence,
        "private artifact drifted",
    )
    configure_core()
    if args.bootstrap_public:
        report = CORE.build_report()
        content = CORE.serialized(report)
        DEFAULT_PUBLIC_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_PUBLIC_OUTPUT.write_bytes(content)
        print(json.dumps({
            "output_sha256": CORE.sha256_bytes(content),
            "status": "PASS",
        }, sort_keys=True))
        return 0
    return CORE.main(["--check"] if args.check else [])


configure_core()
build_report = CORE.build_report
coordinate_digest = CORE.coordinate_digest
load_decisions = CORE.load_decisions
serialized = CORE.serialized
sha256_file = CORE.sha256_file
ReviewError = CORE.ReviewError


if __name__ == "__main__":
    raise SystemExit(main())
