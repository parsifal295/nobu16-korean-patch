#!/usr/bin/env python3
"""Validate selector-568 chunk-1 and build its source-free review report."""

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
BASE_BUILDER = WORKSTREAM / "build_pk_selector568_chunk0_review_v1.py"
ASSIGNMENT_BUILDER = WORKSTREAM / "build_pk_selector568_assignment_v1.py"
ASSIGNMENT_PATH = DIALOGUE_TMP / "family568_assignment.private.v1.json"
ASSIGNMENT_PUBLIC_PATH = (
    WORKSTREAM / "public" / "pk_selector568_assignment_coverage.v1.json"
)
PRIVATE_HANDOFF_PATH = (
    DIALOGUE_TMP / "family568_chunk1_analysis.private.v1.json"
)
DEFAULT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector568_chunk1_review_proposal.v1.json"
)

PRIVATE_SCHEMA = "nobu16.kr.pk-selector568-chunk1-analysis.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector568-chunk1-review-proposal.v1"
METHOD = "reversed_vm_pk_selector568_chunk1_full_caller_review"
SELECTOR = 568
TERMINALS = tuple(range(1951, 1958))
ORDINAL_START = 77
ORDINAL_END = 143
EXPECTED_SITE_COUNT = 67
EXPECTED_ROOT_COUNT = 62
EXPECTED_ASSEMBLY_COUNT = 469
EXPECTED_ACCEPTED = 47
EXPECTED_REWRITE = 46
EXPECTED_KEEP = 1
EXPECTED_REJECT = 20
EXPECTED_ACCEPTED_ROOTS = 46
EXPECTED_REJECTED_ROOTS = 16
EXPECTED_ACCEPTED_ASSEMBLIES = 329
EXPECTED_REJECTED_ASSEMBLIES = 140
EXPECTED_POTENTIAL_PROMOTION_COUNT = 100
EXPECTED_BLOCKED_PENDING_COUNT = 31

EXPECTED_ASSIGNMENT_SHA256 = (
    "B55F2C43D8B4149DDE1739D35FF322E5A6A30C3D58E77AC2500D45200A4AAB98"
)
EXPECTED_ASSIGNMENT_PUBLIC_SHA256 = (
    "BF889606D3C2748B5923CDD9FC46936ED5DE6DED9993FC1B29D5F00785FB6D91"
)
EXPECTED_BASELINE_CANDIDATE_SHA256 = (
    "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E"
)
EXPECTED_LEDGER_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_CHUNK_SITE_SHA256 = (
    "F260A4E506F015936797B1512CB09F22E4B2D703C9BDEE03BFF0D714407F127A"
)
EXPECTED_CHUNK_ROOT_SHA256 = (
    "EA4D55625F5455387B6BF5C8C4792800764C70EDBE282973B147141BF7BB9725"
)
EXPECTED_PENDING_COORDINATE_SHA256 = (
    "97619CA890206A2A71AA77F51DDB60D30900EDF02C3FD5CA2D4D506AADA981D4"
)
EXPECTED_PENDING_ROW_UPPER_BOUND = 131

# Frozen after the private handoff and public proposal are reproduced.
EXPECTED_CHUNK1_PRIORITY_SHA256: str | None = (
    "6A9EC7D2B643B92D0DB57275AE940E3E055AB676BABD3F27452A44D109E589F0"
)
EXPECTED_PRIVATE_HANDOFF_SHA256: str | None = (
    "6EE3B78E55A6A1DC92736EF8392844091D9A3A584D92F610B3911B7C8E33026E"
)
EXPECTED_PROPOSAL_CANDIDATE_SHA256: str | None = (
    "5376D233785CCFAFF79E4869DF213342151F3BCB34AC8586D723ECDD2887F535"
)
EXPECTED_REWRITE_COORDINATE_SHA256: str | None = (
    "F4F9BA5BD4F3D7859996C08298D074F4BC70115C36C0FCB9A625E52847D6AF38"
)
EXPECTED_KEEP_COORDINATE_SHA256: str | None = (
    "700DBCE3DE048C2942F2213DFB3399636A1E304ED4457B184B79FA26A542C07C"
)
EXPECTED_REJECT_COORDINATE_SHA256: str | None = (
    "BD3CB45409018D171D158B966F506EF53602F183D946B1878C1DCFAD994629B0"
)
EXPECTED_ACCEPTED_SITE_SHA256: str | None = (
    "38C563105477D24BDAF643FF7ED91511DE9AE60D655FC6FBBE61819E3C849A05"
)
EXPECTED_REJECTED_SITE_SHA256: str | None = (
    "F8D5DB0866B29A6C838BA6755AB7A6FA40E933C1041568DA53AC73313E7EFF9D"
)
EXPECTED_ASSEMBLY_SHA256: str | None = (
    "56A36CCFA91782F189CEED2255B416CF4BC2A3CCDF76D9D1AD7B50F3C23CDB61"
)
EXPECTED_ACCEPTED_ROOT_SHA256: str | None = (
    "3DC257746F0C17F0D6C166E5A96B7BF8DCB34B20569479A69CB5F46C17285445"
)
EXPECTED_REJECTED_ROOT_SHA256: str | None = (
    "FB5AD29FB9F2B07C9AB7B54BEB0861F44B12EE1BFEC1FB4829608E0E30F1B00B"
)
EXPECTED_POTENTIAL_PROMOTION_COORDINATE_SHA256: str | None = (
    "3206E515A635A0F2423C85B9F22F9449C34DE7AFB3573486234F325115797889"
)
EXPECTED_BLOCKED_PENDING_COORDINATE_SHA256: str | None = (
    "F4733437116797C88A0D9A903AB07705461AC85B8409A7782EE1258B65ADBD0E"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "E161B61CBE28D788CC5E0A457F0D5E2D6AFC8CBDE8283C4B96FAF47A7819B7B4"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_module(BASE_BUILDER, "pk_selector568_chunk1_review_engine_v1")
ASSIGN = load_module(
    ASSIGNMENT_BUILDER,
    "pk_selector568_chunk1_review_assignment_v1",
)
ASSIGN.adjacent_literals = ASSIGN.BASE.adjacent_literals
BASE = ENGINE.BASE
_BASE_BUILD_REPORT = ENGINE.build_report


def patch_contract() -> None:
    replacements = {
        "ASSIGN": ASSIGN,
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
        "EXPECTED_ROOT_COUNT",
        "EXPECTED_ASSEMBLY_COUNT",
        "EXPECTED_ACCEPTED",
        "EXPECTED_REWRITE",
        "EXPECTED_KEEP",
        "EXPECTED_REJECT",
        "EXPECTED_ACCEPTED_ROOTS",
        "EXPECTED_REJECTED_ROOTS",
        "EXPECTED_ACCEPTED_ASSEMBLIES",
        "EXPECTED_REJECTED_ASSEMBLIES",
        "EXPECTED_POTENTIAL_PROMOTION_COUNT",
        "EXPECTED_BLOCKED_PENDING_COUNT",
        "EXPECTED_ASSIGNMENT_SHA256",
        "EXPECTED_ASSIGNMENT_PUBLIC_SHA256",
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
    for module in (ENGINE, BASE):
        for name, value in replacements.items():
            setattr(module, name, value)


def load_assignment() -> tuple[dict[str, Any], dict[str, Any]]:
    ENGINE.require(
        ENGINE.sha256_file(ASSIGNMENT_PATH) == EXPECTED_ASSIGNMENT_SHA256,
        "selector 568 assignment hash drifted",
    )
    assignment = ENGINE.load_json_exact(ASSIGNMENT_PATH)
    ENGINE.require(
        assignment.get("schema") == ASSIGN.PRIVATE_SCHEMA,
        "selector 568 assignment schema drifted",
    )
    chunk = assignment["chunks"][1]
    ENGINE.require(
        chunk.get("chunk_id") == 1
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
        "selector 568 chunk-1 assignment drifted",
    )
    return assignment, chunk


def build_report() -> tuple[dict[str, Any], dict[str, str]]:
    report, frozen = _BASE_BUILD_REPORT()
    result = copy.deepcopy(report)
    proof = result["proof"]
    proof["all_67_sites_classified"] = proof.pop(
        "all_77_sites_classified"
    )
    proof["chunk1_live_pending_priority_sha256"] = (
        EXPECTED_CHUNK1_PRIORITY_SHA256
    )
    proof.pop("chunk0_live_pending_priority_sha256")
    result["scope"]["chunk_id"] = 1
    guards = dict(result.pop("guards"))
    guards["report_payload_sha256"] = ENGINE.canonical_sha256(result)
    result["guards"] = guards
    ENGINE.assert_source_free(result)
    return result, frozen


patch_contract()
ENGINE.load_assignment = load_assignment
BASE.load_assignment = load_assignment
ENGINE.build_report = build_report
BASE.build_report = build_report

ReviewError = ENGINE.ReviewError
require = ENGINE.require
sha256_bytes = ENGINE.sha256_bytes
sha256_file = ENGINE.sha256_file
canonical_bytes = ENGINE.canonical_bytes
canonical_sha256 = ENGINE.canonical_sha256
coordinate_digest = ENGINE.coordinate_digest
site_digest = ENGINE.site_digest
root_digest = ENGINE.root_digest
parse_coordinate = ENGINE.parse_coordinate
site_root = ENGINE.site_root
line_metrics = ENGINE.line_metrics
current_relative_nonexpanding = ENGINE.current_relative_nonexpanding
outer_whitespace_signature = ENGINE.outer_whitespace_signature
record_gap_sha256 = ENGINE.record_gap_sha256
adjacent_literals = ENGINE.adjacent_literals
terminal_literals = ENGINE.terminal_literals
load_json_exact = ENGINE.load_json_exact
load_world = ENGINE.load_world
validate_private_handoff = ENGINE.validate_private_handoff
semantic_register = ENGINE.semantic_register
assert_source_free = ENGINE.assert_source_free
serialized_report = ENGINE.serialized_report
validate_frozen = ENGINE.validate_frozen
parse_args = ENGINE.parse_args
CALLER = ENGINE.CALLER
BASE_AUDIT = ENGINE.BASE_AUDIT


def main(argv: Sequence[str] | None = None) -> int:
    return ENGINE.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
