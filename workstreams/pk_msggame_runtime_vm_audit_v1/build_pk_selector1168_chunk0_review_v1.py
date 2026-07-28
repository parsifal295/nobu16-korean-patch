#!/usr/bin/env python3
"""Validate selector-1168 chunk 0 and emit its source-free checkpoint."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(
    WORKSTREAM / "build_pk_selector550_chunk1_review_v1.py",
    "selector1168_chunk0_review_base",
)
ASSIGN_WRAPPER = load_module(
    WORKSTREAM / "build_pk_selector1168_assignment_v1.py",
    "selector1168_chunk0_review_assignment_wrapper",
)
ASSIGN = ASSIGN_WRAPPER.ASSIGNMENT
ASSIGN.LEGACY = ASSIGN.HELPER.LEGACY
ASSIGN.load_records = ASSIGN.RECORDS.load_records

BASE.ASSIGNMENT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector1168_assignment_v1.py"
)
BASE.ASSIGNMENT_PATH = DIALOGUE_TMP / "pk_selector1168_assignment.private.v1.json"
BASE.ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector1168_assignment_coverage.v1.json"
)
BASE.OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector364_consolidated_checkpoint.private.v1.jsonl"
)
BASE.PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector1168_chunk0_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector1168_chunk0_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector1168_chunk0_review.source_free.v1.json"
)
BASE.SELECTOR = 1168
BASE.TERMINALS = tuple(range(2637, 2644))
BASE.CHUNK_ID = 0
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector1168-chunk0-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector1168-chunk0-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector1168-chunk0-review.source-free.v1"
BASE.METHOD = (
    "post_selector364_selector1168_chunk0_single_rewrite_attempt_"
    "empty_terminal_complete_caller_current_relative_review"
)
BASE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "48D0F8AB64F8F5FA9A2953A6B277519C724A838EF41CB83DB49D3FC8512B25F5"
)
BASE.EXPECTED_ASSIGNMENT_SHA256 = (
    "F2256EDB63FAD8148C6C8C1CDA8CF8E51C2BB47E2218812C34D921C3A8A8546B"
)
BASE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "33FF21CFE153B280B0F365573529B5BBA77B77BFB149623584C9B75237A13A2F"
)
BASE.EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "B776FEF076BC8A466D02F7A8C3624A2BC1EF52012306715A7FF083CF1F53FBD5"
)
BASE.EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "585C20C50BB22B709D03C7F6766E34C69B66E989ED7FADF28300B9BA810C5CCC"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "19C318217E21CD7B7B1F64C01E3FA464BA8A0CF410085DC338E7C813B66B68DD"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "6F3880DF9105F47402378E89E9C1ADE9599C052CAEC6EE3D7CC795333C04C7DE"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "E4BB332843D61F4B3EB6D1E061706AA3E5730413670E837386F2DC5CEFBEA1D6"
)
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "775A5AB4238F45ECDC0DBA5467E4EEA21EFE698C0A2E9BFF621EDA9DFD5BFF64"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 4,
    "accepted_sites": 4,
    "assembly_branches": 182,
    "blocked_pending_roots": 3,
    "blocked_pending_rows": 12,
    "blocked_sites": 22,
    "decision_rows": 15,
    "promoted_pending_rows": 15,
    "roots": 26,
    "same_gap_branches": 0,
    "shared_override_rows": 0,
    "sites": 26,
    "translation_overrides": 4,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 11,
    "translation_override_and_runtime_promotion": 4,
}
BASE.EXPECTED_DIGESTS = {
    "assembly": "F39CC48B606886A1BB9F2DEAA63087936197DF74734525508146DDA23E69E574",
    "decision": "B4EACE861BDF95FC92902A25709839E0F7B5972E17B589B0923792FD2ADB1BAB",
    "override": "424BEB025390CBFA69DEF7FC38202CD933D0137A6A3F35BF2D9186A1AE072C07",
    "promoted": "B4EACE861BDF95FC92902A25709839E0F7B5972E17B589B0923792FD2ADB1BAB",
}
BASE.ASSIGN = ASSIGN
BASE.ENGINE = ASSIGN.ENGINE
BASE.RANKING = ASSIGN.RANKING
BASE._EDGE_CACHE.clear()
BASE._TERMINAL_CACHE.clear()

EXPECTED_EMPTY_TERMINAL_SHA256 = (
    "B0F66ADC83641586656866813FD9DD0B8EBB63796075661BA45D1AA8089E1D44"
)
EXPECTED_SOURCE_TERMINAL_SHA256 = (
    "5D3D3A6C696F698638360E90EA204BE98C7B986199D29BB06AB10850039D10E9"
)

_selected_terminal_roots = BASE.selected_terminal_roots


def selected_terminal_roots(records, source, selector):
    try:
        return _selected_terminal_roots(records, source, selector)
    except BASE.ReviewError:
        shape = BASE.RANKING.family_shape(
            BASE.graph_edges_cached(records),
            BASE.graph_edges_cached(source),
            (0, selector),
        )
        leaves = tuple(sorted(shape["candidate_leaves"]))
        BASE.require(leaves, f"selector {selector} has no terminal")
        return tuple(leaves[0] for _ in range(7))


BASE.selected_terminal_roots = selected_terminal_roots
_gap_assembly = BASE.gap_assembly


def gap_assembly(*, records, source, root, gap_id, ordinal):
    if gap_id != 0:
        return _gap_assembly(
            records=records,
            source=source,
            root=root,
            gap_id=gap_id,
            ordinal=ordinal,
        )
    literals = BASE.ENGINE.parse_record_literals(records[root])
    result = ""
    edges = [
        edge
        for edge in BASE.graph_edges_cached(records)[root]
        if int(edge["gap_id"]) == 0
    ]
    for edge in sorted(edges, key=lambda row: int(row["offset"])):
        selector = int(edge["target"][1])
        terminals = selected_terminal_roots(records, source, selector)
        result += BASE.first_literal(records, terminals[ordinal])
    if literals:
        result += literals[0].text
    return result


BASE.gap_assembly = gap_assembly
_build_report = BASE.build_report


def terminal_digest(records) -> str:
    values = [
        BASE.first_literal(records, (0, record_id))
        for record_id in BASE.TERMINALS
    ]
    return BASE.sha256_bytes("\0".join(values).encode("utf-8"))


def validate_empty_honorific_prefix_family() -> None:
    candidate, _current, source, contexts, _pending = ASSIGN.load_records()
    BASE.require(
        terminal_digest(candidate) == EXPECTED_EMPTY_TERMINAL_SHA256,
        "candidate terminal family is not empty",
    )
    BASE.require(
        terminal_digest(source) == EXPECTED_SOURCE_TERMINAL_SHA256,
        "source terminal family drifted",
    )
    for language in ("en", "sc", "tc"):
        BASE.require(
            terminal_digest(contexts[language])
            == EXPECTED_EMPTY_TERMINAL_SHA256,
            f"{language} terminal family is not empty",
        )
    terminal_roots = {(0, record_id) for record_id in BASE.TERMINALS}
    BASE.require(
        not any(
            BASE.parse_coordinate(str(row["coordinate"]))[:2]
            in terminal_roots
            for row in BASE.load_decisions()
        ),
        "shared terminal mutation is forbidden",
    )


def build_report():
    validate_empty_honorific_prefix_family()
    return _build_report()


BASE.build_report = build_report
coordinate_digest = BASE.coordinate_digest
load_decisions = BASE.load_decisions
serialized = BASE.serialized
sha256_file = BASE.sha256_file
ReviewError = BASE.ReviewError
DEFAULT_PUBLIC_OUTPUT = BASE.DEFAULT_PUBLIC_OUTPUT
EXPECTED_ACTION_COUNTS = BASE.EXPECTED_ACTION_COUNTS
EXPECTED_DIGESTS = BASE.EXPECTED_DIGESTS
EXPECTED_PUBLIC_FILE_SHA256 = BASE.EXPECTED_PUBLIC_FILE_SHA256


if __name__ == "__main__":
    raise SystemExit(BASE.main())
