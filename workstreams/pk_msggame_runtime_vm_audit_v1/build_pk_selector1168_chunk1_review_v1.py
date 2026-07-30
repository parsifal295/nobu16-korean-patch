#!/usr/bin/env python3
"""Validate selector-1168 chunk 1 and emit its source-free checkpoint."""

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
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


CORE = load_module(
    WORKSTREAM / "build_pk_selector550_chunk1_review_v1.py",
    "selector1168_chunk1_review_core",
)
ASSIGN_WRAPPER = load_module(
    WORKSTREAM / "build_pk_selector1168_assignment_v1.py",
    "selector1168_chunk1_review_assignment",
)
ASSIGN = ASSIGN_WRAPPER.ASSIGNMENT
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.RECORDS.load_records

ASSIGNMENT_PATH = DIALOGUE_TMP / "pk_selector1168_assignment.private.v1.json"
PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector1168_chunk1_review_decisions.private.v1.jsonl"
)
PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector1168_chunk1_review_evidence.private.v1.json"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector1168_chunk1_review.source_free.v1.json"
)

METHOD = (
    "post_selector364_selector1168_chunk1_single_rewrite_"
    "caller_complete_form_current_relative_review"
)
PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector1168-chunk1-review-decision.private.v1"
)
PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector1168-chunk1-review-evidence.private.v1"
)
PUBLIC_SCHEMA = "nobu16.kr.pk-selector1168-chunk1-review.source-free.v1"
EXPECTED_COUNTS = {
    "accepted_pending_roots": 1,
    "accepted_sites": 1,
    "assembly_branches": 189,
    "blocked_pending_roots": 5,
    "blocked_pending_rows": 17,
    "blocked_sites": 26,
    "decision_rows": 4,
    "owned_overlap_roots": 4,
    "promoted_pending_rows": 4,
    "roots": 26,
    "same_gap_branches": 0,
    "shared_override_rows": 0,
    "sites": 27,
    "translation_overrides": 1,
    "verification_renewal_rows": 0,
}
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 3,
    "translation_override_and_runtime_promotion": 1,
}
EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "48D0F8AB64F8F5FA9A2953A6B277519C724A838EF41CB83DB49D3FC8512B25F5"
)
EXPECTED_ASSIGNMENT_SHA256 = (
    "F2256EDB63FAD8148C6C8C1CDA8CF8E51C2BB47E2218812C34D921C3A8A8546B"
)
EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "33FF21CFE153B280B0F365573529B5BBA77B77BFB149623584C9B75237A13A2F"
)
EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "B776FEF076BC8A466D02F7A8C3624A2BC1EF52012306715A7FF083CF1F53FBD5"
)
EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "C19E154059B94BE562ABEC3E174D7455DA657FDEB60DB9B569F4F7013797CF25"
)
EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "6503637FC758A09AB11A1A8BF98BE7F0E160E6363A12CDEECCE44F827965CF0D"
)
EXPECTED_CANDIDATE_SHA256 = (
    "6F3880DF9105F47402378E89E9C1ADE9599C052CAEC6EE3D7CC795333C04C7DE"
)
EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "92983A525D33E1B29BCE776F733E122E95A851BBBAFC98FB9D27A716F42FA3FE"
)
EXPECTED_LIVE_STEAM_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_TERMINAL_CANDIDATE_SHA256 = (
    "D088784B7ECB87F1EA17E6F982FA968FFEFCC07B79DE6ECC548FC00242868DA6"
)
EXPECTED_TERMINAL_CURRENT_SHA256 = (
    "D0C572F2E364E97D2C6095B6F1DA12FFC5C58D0D0254C814648AD2D093FE50CF"
)
EXPECTED_TERMINAL_SOURCE_SHA256 = (
    "DFAD8074D657712C1C709F847A83183A4179DA5C4B5F222676DA7A37E0F1586C"
)
EXPECTED_DIGESTS = {
    "assembly":
        "9A5D88995E6166C8504D6E98B94F305A095FFE7D700D9DFD626DF5DDA70ADAF9",
    "decision":
        "36ED8F5454E1FE449AE01CD99245EDBDF874C6254D4094B597DF27A9ED8168A0",
    "override":
        "C8C2FECC1052393275543CE28D615D0F02218E07523267C549554B0A98983488",
    "promoted":
        "36ED8F5454E1FE449AE01CD99245EDBDF874C6254D4094B597DF27A9ED8168A0",
}
EXPECTED_PUBLIC_FILE_SHA256 = (
    "5DA0977A9D46AE08273047A4185032D6EE60A0792C0BD38B56946AD49877F8B8"
)

_CORE_BUILD_REPORT = CORE.build_report


def gap_assembly(
    *,
    records: Any,
    source: Any,
    root: tuple[int, int],
    gap_id: int,
    ordinal: int,
) -> str:
    literals = CORE.ENGINE.parse_record_literals(records[root])
    CORE.require(0 <= gap_id <= len(literals), f"invalid gap {root}:{gap_id}")
    edges = [
        edge
        for edge in CORE.graph_edges_cached(records)[root]
        if int(edge["gap_id"]) == gap_id
    ]
    result = literals[gap_id - 1].text if gap_id else ""
    for edge in sorted(edges, key=lambda row: int(row["offset"])):
        selector = int(edge["target"][1])
        terminals = CORE.selected_terminal_roots(records, source, selector)
        result += CORE.first_literal(records, terminals[ordinal])
    if gap_id < len(literals):
        result += literals[gap_id].text
    return result


def configure_core() -> None:
    CORE.ASSIGNMENT_BUILDER_PATH = (
        WORKSTREAM / "build_pk_selector1168_assignment_v1.py"
    )
    CORE.ASSIGNMENT_PATH = ASSIGNMENT_PATH
    CORE.ASSIGNMENT_PUBLIC_PATH = (
        WORKSTREAM / "public" / "pk_selector1168_assignment_coverage.v1.json"
    )
    CORE.OFFICIAL_LEDGER_PATH = (
        DIALOGUE_TMP
        / "runtime_vm_integrated.post_selector364_consolidated_checkpoint.private.v1.jsonl"
    )
    CORE.PRIVATE_DECISIONS_PATH = PRIVATE_DECISIONS_PATH
    CORE.PRIVATE_EVIDENCE_PATH = PRIVATE_EVIDENCE_PATH
    CORE.DEFAULT_PUBLIC_OUTPUT = DEFAULT_PUBLIC_OUTPUT
    CORE.SELECTOR = 1168
    CORE.TERMINALS = tuple(range(2637, 2644))
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
    CORE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
        EXPECTED_PRIVATE_EVIDENCE_SHA256
    )
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
    CORE.gap_assembly = gap_assembly
    CORE._EDGE_CACHE.clear()
    CORE._TERMINAL_CACHE.clear()


def terminal_digest(records: Any) -> tuple[list[int], str]:
    values = [
        CORE.first_literal(records, (0, terminal))
        for terminal in range(2637, 2644)
    ]
    return (
        sorted(Counter(values).values()),
        CORE.sha256_bytes("\n".join(values).encode("utf-8")),
    )


def build_report() -> dict[str, Any]:
    report = _CORE_BUILD_REPORT()
    candidate, current, source, _contexts, _pending = ASSIGN.load_records()
    candidate_shape, candidate_sha = terminal_digest(candidate)
    current_shape, current_sha = terminal_digest(current)
    source_shape, source_sha = terminal_digest(source)
    CORE.require(
        candidate_shape == [7]
        and current_shape == [2, 5]
        and source_shape == [2, 5]
        and candidate_sha == EXPECTED_TERMINAL_CANDIDATE_SHA256
        and current_sha == EXPECTED_TERMINAL_CURRENT_SHA256
        and source_sha == EXPECTED_TERMINAL_SOURCE_SHA256,
        "shared terminal guard drifted",
    )
    evidence = json.loads(
        PRIVATE_EVIDENCE_PATH.read_text(encoding="utf-8")
    )
    CORE.require(
        evidence["proof"] == {
            "rewrite_attempt_count": 1,
            "shared_terminal_modified": False,
            "source_only_action_count": 0,
        },
        "single-pass proof drifted",
    )
    assignment_public = json.loads(
        CORE.ASSIGNMENT_PUBLIC_PATH.read_text(encoding="ascii")
    )
    CORE.require(
        assignment_public["coverage"]["source_only_action_count"] == 0,
        "source-only action guard drifted",
    )
    report["guards"].update({
        "assignment_public_sha256": EXPECTED_ASSIGNMENT_PUBLIC_SHA256,
        "official_ledger_sha256": EXPECTED_OFFICIAL_LEDGER_SHA256,
        "terminal_candidate_sha256": EXPECTED_TERMINAL_CANDIDATE_SHA256,
        "terminal_current_sha256": EXPECTED_TERMINAL_CURRENT_SHA256,
        "terminal_source_sha256": EXPECTED_TERMINAL_SOURCE_SHA256,
    })
    report["proof"].update({
        "caller_complete_form_reviewed": True,
        "rewrite_attempt_count": 1,
        "shared_terminal_modified": False,
        "source_only_action_count": 0,
        "terminal_candidate_all_empty": True,
        "terminal_variant_multiplicities": {
            "candidate": [7],
            "current": [2, 5],
            "source": [2, 5],
        },
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
            f"public output hash drifted: {output_sha256}",
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
