#!/usr/bin/env python3
"""Validate selector-1096 chunk-2 and build its source-free review report."""

from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
BASE_BUILDER = WORKSTREAM / "build_pk_selector1096_chunk0_review_v1.py"
ASSIGNMENT_PATH = DIALOGUE_TMP / "family1096_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector1096_assignment_coverage.v1.json"
)
PRIVATE_HANDOFF_PATH = (
    DIALOGUE_TMP / "family1096_chunk2_analysis.private.v1.json"
)
DEFAULT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector1096_chunk2_review_proposal.v1.json"
)

PRIVATE_SCHEMA = "nobu16.kr.pk-selector1096-chunk2-analysis.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector1096-chunk2-review-proposal.v1"
METHOD = "reversed_vm_pk_selector1096_chunk2_full_caller_review"
SELECTOR = 1096
TERMINALS = tuple(range(2581, 2588))
ORDINAL_START = 115
ORDINAL_END = 171
EXPECTED_SITE_COUNT = 57
EXPECTED_ROOT_COUNT = 57
EXPECTED_ASSEMBLY_COUNT = 399
EXPECTED_ACCEPTED = 49
EXPECTED_REWRITE = 47
EXPECTED_KEEP = 2
EXPECTED_REJECT = 8
EXPECTED_ACCEPTED_ROOTS = 49
EXPECTED_REJECTED_ROOTS = 8
EXPECTED_ACCEPTED_ASSEMBLIES = 343
EXPECTED_REJECTED_ASSEMBLIES = 56
EXPECTED_POTENTIAL_PROMOTION_COUNT = 67
EXPECTED_BLOCKED_PENDING_COUNT = 12
EXPECTED_ACCEPTED_CURRENT_LIVE = 67
EXPECTED_ACCEPTED_LIVE_AFTER_SELECTOR538_PLAN = 62

EXPECTED_ASSIGNMENT_SHA256 = (
    "6A76DFA45A4706B4D7524ACEDBA46DFFDC15CD592E3D6A5740A1AB46C2EE5925"
)
EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "0B5A862BD98474B0A8A64423FEFD714EE5013D233E759C45BA4365AAC76F859D"
)
EXPECTED_BASELINE_CANDIDATE_SHA256 = (
    "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E"
)
EXPECTED_LEDGER_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_CHUNK_SITE_SHA256 = (
    "E0C09101FD8157E18FC5EB13B233F8C71355B4370841F6AB35003621F643C28C"
)
EXPECTED_CHUNK_ROOT_SHA256 = (
    "40EA499BCDCEBE59D4032A90E7399B3E2B6B5831ABD2803B286DE9375E09AD7D"
)
EXPECTED_PENDING_COORDINATE_SHA256 = (
    "E327CC020F0258E375FBDDAD274DEF0636EE0B5BD1A2A0E3E12C9B79EA569FD9"
)
EXPECTED_PENDING_ROW_UPPER_BOUND = 79
EXPECTED_CHUNK0_PRIORITY_SHA256 = EXPECTED_PENDING_COORDINATE_SHA256

EXPECTED_PRIVATE_HANDOFF_SHA256: str | None = (
    "B07587B8B357F5C49445A9DE725840DD9FA7A05B5D3F0C2278597D3215790303"
)
EXPECTED_PROPOSAL_CANDIDATE_SHA256: str | None = (
    "F0F9DCCECA33105E6235A20E3F812094DC120465ECCC75CB094FB3F2E8F3F6F7"
)
EXPECTED_REWRITE_COORDINATE_SHA256: str | None = (
    "3800FC160FDED5EABD5EB037A5D8A5452B842994DAF0B4179298EBFF342E212E"
)
EXPECTED_KEEP_COORDINATE_SHA256: str | None = (
    "4658799A719A2C65C04F44613D9D77FAE117C1CB7C556F0B71E8D729ADEB74D7"
)
EXPECTED_REJECT_COORDINATE_SHA256: str | None = (
    "8B3C768BD8E6A76E472E788EB57FF9E3531831E718239C8F797BC80CDBD3B929"
)
EXPECTED_ACCEPTED_SITE_SHA256: str | None = (
    "FA118B222DF42FFEEF72951A16097A4A98714FE096AB6D6BE23090A814231B7A"
)
EXPECTED_REJECTED_SITE_SHA256: str | None = (
    "908A64BE776E9ADB4E641400C3B368343F3D2EFE991FFAA3F8DEA1D6E02EC6AD"
)
EXPECTED_ASSEMBLY_SHA256: str | None = (
    "B5ED09A07E9240D04832931FA3E61AB11450D4D47D9ACFE55BD5A6DDC23A3FB6"
)
EXPECTED_ACCEPTED_ROOT_SHA256: str | None = (
    "31B3CA059158B715787576F2D7B1F1D65A6ABDCAC54873F44BE47CC573296A80"
)
EXPECTED_REJECTED_ROOT_SHA256: str | None = (
    "713DD8CA4CB291DAF00A50051D3B32C980FA83B31C5B4A56AC16608C8AAFFC75"
)
EXPECTED_POTENTIAL_PROMOTION_COORDINATE_SHA256: str | None = (
    "798836E8F1B8FCF2826BAC76314C483930D36D2E36300D1161A8F04A24C94F72"
)
EXPECTED_BLOCKED_PENDING_COORDINATE_SHA256: str | None = (
    "634B39179A2DCE9749C00AEED238987CCA7EC89BD28A5EB695AB472158DE3E82"
)
EXPECTED_ACCEPTED_CURRENT_LIVE_SHA256: str | None = (
    "798836E8F1B8FCF2826BAC76314C483930D36D2E36300D1161A8F04A24C94F72"
)
EXPECTED_ACCEPTED_LIVE_AFTER_SELECTOR538_PLAN_SHA256: str | None = (
    "DAB4DD150A55F58B3229B7ECFE0F091901C7BC5A9F7CCDB5DE78A2866A2A85B0"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "55BF8BCA0AD81CF9F45E1E010DACB74356B73E31C1CA7E55EE4158F8263C8D6A"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(BASE_BUILDER, "pk_selector1096_chunk2_review_base_v1")
CORE = BASE.BASE
_BASE_BUILD_REPORT = BASE.build_report


def patch_contract() -> None:
    replacements = {
        "ASSIGNMENT_PATH": ASSIGNMENT_PATH,
        "ASSIGNMENT_PUBLIC_PATH": ASSIGNMENT_PUBLIC_PATH,
        "PRIVATE_HANDOFF_PATH": PRIVATE_HANDOFF_PATH,
        "DEFAULT_OUTPUT": DEFAULT_OUTPUT,
        "PRIVATE_SCHEMA": PRIVATE_SCHEMA,
        "PUBLIC_SCHEMA": PUBLIC_SCHEMA,
        "METHOD": METHOD,
        "SELECTOR": SELECTOR,
        "TERMINALS": TERMINALS,
    }
    for name in (
        "ORDINAL_START",
        "ORDINAL_END",
        "EXPECTED_SITE_COUNT",
        "EXPECTED_ASSEMBLY_COUNT",
        "EXPECTED_ACCEPTED",
        "EXPECTED_REWRITE",
        "EXPECTED_KEEP",
        "EXPECTED_REJECT",
        "EXPECTED_ACCEPTED_ASSEMBLIES",
        "EXPECTED_REJECTED_ASSEMBLIES",
        "EXPECTED_ASSIGNMENT_SHA256",
        "EXPECTED_BASELINE_CANDIDATE_SHA256",
        "EXPECTED_LEDGER_SHA256",
        "EXPECTED_CHUNK_SITE_SHA256",
        "EXPECTED_CHUNK_ROOT_SHA256",
        "EXPECTED_PENDING_COORDINATE_SHA256",
        "EXPECTED_PENDING_ROW_UPPER_BOUND",
        "EXPECTED_PRIVATE_HANDOFF_SHA256",
        "EXPECTED_PROPOSAL_CANDIDATE_SHA256",
        "EXPECTED_REWRITE_COORDINATE_SHA256",
        "EXPECTED_KEEP_COORDINATE_SHA256",
        "EXPECTED_REJECT_COORDINATE_SHA256",
        "EXPECTED_ACCEPTED_SITE_SHA256",
        "EXPECTED_REJECTED_SITE_SHA256",
        "EXPECTED_ASSEMBLY_SHA256",
        "EXPECTED_ACCEPTED_ROOT_SHA256",
        "EXPECTED_REJECTED_ROOT_SHA256",
        "EXPECTED_POTENTIAL_PROMOTION_COORDINATE_SHA256",
        "EXPECTED_BLOCKED_PENDING_COORDINATE_SHA256",
        "EXPECTED_PUBLIC_FILE_SHA256",
    ):
        replacements[name] = globals()[name]
    for module in (BASE, CORE):
        for name, value in replacements.items():
            setattr(module, name, value)
    for name in (
        "EXPECTED_ASSIGNMENT_PUBLIC_SHA256",
        "EXPECTED_ROOT_COUNT",
        "EXPECTED_ACCEPTED_ROOTS",
        "EXPECTED_REJECTED_ROOTS",
        "EXPECTED_POTENTIAL_PROMOTION_COUNT",
        "EXPECTED_BLOCKED_PENDING_COUNT",
        "EXPECTED_ACCEPTED_CURRENT_LIVE",
        "EXPECTED_ACCEPTED_LIVE_AFTER_SELECTOR538_PLAN",
        "EXPECTED_ACCEPTED_CURRENT_LIVE_SHA256",
        "EXPECTED_ACCEPTED_LIVE_AFTER_SELECTOR538_PLAN_SHA256",
        "EXPECTED_CHUNK0_PRIORITY_SHA256",
    ):
        setattr(BASE, name, globals()[name])


patch_contract()

ReviewError = BASE.ReviewError
require = BASE.require
sha256_bytes = BASE.sha256_bytes
sha256_file = BASE.sha256_file
canonical_bytes = BASE.canonical_bytes
canonical_sha256 = BASE.canonical_sha256
coordinate_digest = BASE.coordinate_digest
site_digest = BASE.site_digest
root_digest = BASE.root_digest
parse_coordinate = BASE.parse_coordinate
site_root = BASE.site_root
line_metrics = BASE.line_metrics
current_relative_nonexpanding = BASE.current_relative_nonexpanding
outer_whitespace_signature = BASE.outer_whitespace_signature
record_gap_sha256 = BASE.record_gap_sha256
adjacent_literals = BASE.adjacent_literals
terminal_literals = BASE.terminal_literals
load_json_exact = BASE.load_json_exact
ASSIGN = BASE.ASSIGN
CALLER = BASE.CALLER
BASE_AUDIT = BASE.BASE_AUDIT
ENGINE = BASE.ENGINE
semantic_register = BASE.semantic_register
assert_source_free = BASE.assert_source_free
validate_private_handoff = BASE.validate_private_handoff


def load_assignment() -> tuple[dict[str, Any], dict[str, Any]]:
    require(
        sha256_file(ASSIGNMENT_PATH) == EXPECTED_ASSIGNMENT_SHA256,
        "selector 1096 assignment hash drifted",
    )
    assignment = load_json_exact(ASSIGNMENT_PATH)
    require(
        assignment.get("schema") == ASSIGN.PRIVATE_SCHEMA,
        "selector 1096 assignment schema drifted",
    )
    chunk = assignment["chunks"][2]
    require(
        chunk.get("chunk_id") == 2
        and chunk.get("ordinal_start") == ORDINAL_START
        and chunk.get("ordinal_end") == ORDINAL_END
        and chunk.get("site_count") == EXPECTED_SITE_COUNT
        and chunk.get("root_count") == EXPECTED_ROOT_COUNT
        and chunk.get("site_sha256") == EXPECTED_CHUNK_SITE_SHA256
        and chunk.get("root_sha256") == EXPECTED_CHUNK_ROOT_SHA256
        and chunk.get("pending_coordinate_sha256")
        == EXPECTED_PENDING_COORDINATE_SHA256
        and chunk.get("pending_row_upper_bound")
        == EXPECTED_PENDING_ROW_UPPER_BOUND,
        "selector 1096 chunk-2 assignment drifted",
    )
    return assignment, chunk


def build_report() -> tuple[dict[str, Any], dict[str, str]]:
    report, frozen = _BASE_BUILD_REPORT()
    result = copy.deepcopy(report)
    result["proof"]["all_57_sites_classified"] = result["proof"].pop(
        "all_56_sites_classified"
    )
    result["proof"]["chunk2_pending_coordinate_sha256"] = (
        result["proof"].pop("chunk0_live_pending_priority_sha256")
    )
    result["scope"]["chunk_id"] = 2
    guards = result.pop("guards")
    guards["report_payload_sha256"] = canonical_sha256(result)
    result["guards"] = guards
    assert_source_free(result)
    return result, frozen


BASE.load_assignment = load_assignment
CORE.load_assignment = load_assignment
BASE.build_report = build_report

load_world = BASE.load_world
serialized_report = BASE.serialized_report
validate_frozen = BASE.validate_frozen
parse_args = BASE.parse_args


def main(argv: Sequence[str] | None = None) -> int:
    return BASE.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
