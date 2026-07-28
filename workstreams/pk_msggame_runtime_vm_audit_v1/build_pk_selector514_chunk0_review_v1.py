#!/usr/bin/env python3
"""Validate selector-514 chunk 0 and emit its source-free checkpoint."""

from __future__ import annotations

import importlib.util
import json
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
    "selector514_chunk0_review_base",
)
ASSIGN = load_module(
    WORKSTREAM / "build_pk_selector514_assignment_v1.py",
    "selector514_chunk0_review_assignment",
)

BASE.ASSIGNMENT_BUILDER_PATH = (
    WORKSTREAM / "build_pk_selector514_assignment_v1.py"
)
BASE.ASSIGNMENT_PATH = (
    DIALOGUE_TMP / "pk_selector514_assignment.private.v1.json"
)
BASE.ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector514_assignment_coverage.v1.json"
)
BASE.OFFICIAL_LEDGER_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector142_consolidated_checkpoint.private.v1.jsonl"
)
BASE.PRIVATE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector514_chunk0_review_decisions.private.v1.jsonl"
)
BASE.PRIVATE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector514_chunk0_review_evidence.private.v1.json"
)
BASE.DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM / "public" / "pk_selector514_chunk0_review.source_free.v1.json"
)
BASE.SELECTOR = 514
BASE.TERMINALS = tuple(range(1895, 1902))
BASE.CHUNK_ID = 0
BASE.PRIVATE_DECISION_SCHEMA = (
    "nobu16.kr.pk-selector514-chunk0-review-decision.private.v1"
)
BASE.PRIVATE_EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector514-chunk0-review-evidence.private.v1"
)
BASE.PUBLIC_SCHEMA = "nobu16.kr.pk-selector514-chunk0-review.source-free.v1"
BASE.METHOD = (
    "post_selector142_selector514_chunk0_fast_grouped_boundary_"
    "same_gap_and_current_relative_review"
)
BASE.EXPECTED_ASSIGNMENT_BUILDER_SHA256 = (
    "88236661B06478F554DA70706265602722DC4A38254767AF2C9F8CAF6D718A73"
)
BASE.EXPECTED_ASSIGNMENT_SHA256 = (
    "22D71A0373FF9B325ABE06C356BBA3A239DB56E9EECB10BFACFAA10C85B1E8DA"
)
BASE.EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "EA962FAAC51391DD773E4519693B41377DA5359491451F0631FB297A6A29EAA2"
)
BASE.EXPECTED_OFFICIAL_LEDGER_SHA256 = (
    "5D3673BC67F8FB55B258BB236CBC6ACD3E76F2E001300994ED7AFD742601C0DB"
)
BASE.EXPECTED_PRIVATE_DECISIONS_SHA256 = (
    "82E46843418DEE444DE2CDE80A1A26F736F270C3293FFF222E1C45CBC652C431"
)
BASE.EXPECTED_PRIVATE_EVIDENCE_SHA256 = (
    "EB7B9297D9047051547C110AE7F3AD67A1598D2F49760BB69CB467B567E7ED48"
)
BASE.EXPECTED_CANDIDATE_SHA256 = (
    "6E3E5CD8A0FF7CC07C69BD9ABDCB2380FFD507D21F528E2A446D57329359F6A8"
)
BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256 = (
    "B8D3FDF78A36877DAA2757827DFE5AC061DF9E1A00B19E3CE1FEF7D7E729984F"
)
BASE.EXPECTED_LIVE_STEAM_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
BASE.EXPECTED_PUBLIC_FILE_SHA256 = (
    "F2313F745BE5A50A82780C092258BBB8995A4531088C41B07037C35C467E7861"
)
BASE.EXPECTED_COUNTS = {
    "accepted_pending_roots": 21,
    "accepted_sites": 29,
    "assembly_branches": 210,
    "blocked_pending_roots": 0,
    "blocked_pending_rows": 0,
    "blocked_sites": 1,
    "decision_rows": 74,
    "promoted_pending_rows": 67,
    "roots": 30,
    "same_gap_branches": 126,
    "shared_override_rows": 4,
    "sites": 30,
    "translation_overrides": 19,
}
BASE.EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 55,
    "translation_override_and_runtime_promotion": 12,
    "translation_override_and_verification_renewal": 7,
}
BASE.EXPECTED_DIGESTS = {
    "assembly": "7719DF32EEA5BD1E94092C5C5FFB6665363F89F3460FEBC5D0A81D36BCEC8ED3",
    "decision": "DBB99EC33FB8E01290DC4D5E7CBE82C794EC10D4B190218F955C2B7F15DCEC4B",
    "override": "D9F3AE99D32C519DD087A0A7CDA303FDDEB09B384EB8CCFB5204A21AC4C866C8",
    "promoted": "C87F2804E14355449F93B68273518EFBECCC0F06D35039644310B4C2919E8C20",
}
BASE.ASSIGN = ASSIGN
BASE.ASSIGN.load_records = ASSIGN.RECORDS.load_records
BASE.ENGINE = ASSIGN.ENGINE
BASE.RANKING = ASSIGN.RANKING
BASE._EDGE_CACHE.clear()
BASE._TERMINAL_CACHE.clear()

_base_build_report = BASE.build_report


def build_report_with_shared_terminal_scope():
    report = _base_build_report()
    evidence = json.loads(
        BASE.PRIVATE_EVIDENCE_PATH.read_text(encoding="utf-8")
    )
    terminal = evidence["shared_terminal_scope"]
    BASE.require(
        terminal["candidate_branch_count"] == 392
        and terminal["candidate_changed_branch_count"] == 224
        and terminal["candidate_site_count"] == 56
        and terminal["manifest_canonical_sha256"]
        == "11CFCF80E5D438F6036E3C288A23BDF7F42D9A9142416011361AF6CD208289ED"
        and terminal["source_only_call_absent_from_candidate_graph"] is True
        and terminal["source_only_site_count"] == 30
        and len(terminal["terminal_coordinates"]) == 4
        and BASE.coordinate_digest(terminal["terminal_coordinates"])
        == "1FF80B31ECF451A52441461D31459DBAC4C9F2834764FA08E257BB0A642DF28D",
        "shared terminal scope drifted",
    )
    terminal_rows = {
        str(row["coordinate"]): row
        for row in BASE.load_decisions()
        if str(row.get("overlap_owner") or "") == "selector514_chunk0"
    }
    BASE.require(
        set(terminal_rows) == set(terminal["terminal_coordinates"])
        and all(
            row["action"]
            == "translation_override_and_verification_renewal"
            and row["reviewed_translation"] == ""
            for row in terminal_rows.values()
        ),
        "shared terminal predecessor disposition drifted",
    )
    report["guards"]["shared_terminal_manifest_sha256"] = terminal[
        "manifest_canonical_sha256"
    ]
    report["proof"][
        "shared_terminal_all_candidate_sites_nonexpanding"
    ] = True
    report["proof"]["source_only_calls_absent_from_candidate_graph"] = True
    report["result"]["shared_terminal_candidate_branches"] = 392
    report["result"]["shared_terminal_candidate_sites"] = 56
    report["result"]["shared_terminal_changed_branches"] = 224
    report["result"]["shared_terminal_source_only_sites"] = 30
    return report


BASE.build_report = build_report_with_shared_terminal_scope


if __name__ == "__main__":
    raise SystemExit(BASE.main())
