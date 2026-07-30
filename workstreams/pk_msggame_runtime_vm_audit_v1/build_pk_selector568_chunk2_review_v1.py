#!/usr/bin/env python3
"""Validate selector-568 chunk-2 and build its source-free review report."""

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
    DIALOGUE_TMP / "family568_chunk2_analysis.private.v1.json"
)
DEFAULT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector568_chunk2_review_proposal.v1.json"
)

PRIVATE_SCHEMA = "nobu16.kr.pk-selector568-chunk2-analysis.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector568-chunk2-review-proposal.v1"
METHOD = "reversed_vm_pk_selector568_chunk2_full_caller_review"
SELECTOR = 568
TERMINALS = tuple(range(1951, 1958))
ORDINAL_START = 144
ORDINAL_END = 221
EXPECTED_SITE_COUNT = 78
EXPECTED_ROOT_COUNT = 78
EXPECTED_ASSEMBLY_COUNT = 546

# Frozen after the independent semantic review is reproduced.
EXPECTED_ACCEPTED = 60
EXPECTED_REWRITE = 51
EXPECTED_KEEP = 9
EXPECTED_REJECT = 18
EXPECTED_ACCEPTED_ROOTS = 60
EXPECTED_REJECTED_ROOTS = 18
EXPECTED_ACCEPTED_ASSEMBLIES = 420
EXPECTED_REJECTED_ASSEMBLIES = 126
EXPECTED_POTENTIAL_PROMOTION_COUNT = 50
EXPECTED_BLOCKED_PENDING_COUNT = 36

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
    "0183D55E113211862F571DD82E7E9CC14C9A040F7B9FF31200A87BCAF0FC6D3A"
)
EXPECTED_CHUNK_ROOT_SHA256 = (
    "D11F46FAE98BB3C5B095DD49E932F114C876BBC7DF9499FE3A2A5D3E4CF35D72"
)
EXPECTED_PENDING_COORDINATE_SHA256 = (
    "CE9FE7BD38EC1C48320F4215A641548F861A8D953D2BA3B923BCF7C096995231"
)
EXPECTED_PENDING_ROW_UPPER_BOUND = 86

EXPECTED_CHUNK2_PRIORITY_SHA256: str | None = (
    "5B874A52B9F625882B2978C98007E6C335F46455753A4D817DE6837DC0745A2E"
)
EXPECTED_PRIVATE_HANDOFF_SHA256: str | None = (
    "C2235C1BBF2E12D1A9E8466BBB77A0AC3BD1FE87B8EE9238F32D27F24AA3AB37"
)
EXPECTED_PROPOSAL_CANDIDATE_SHA256: str | None = (
    "D6F95943EA08B02533D8541EF28B3E0F584E79E0CBA2A49D30B5B84D2D48B409"
)
EXPECTED_REWRITE_COORDINATE_SHA256: str | None = (
    "A2234AB61FD1A5B236CF46FC94B8A68A2EEE1DF88A2EC981DD9B9CD23920DEF3"
)
EXPECTED_KEEP_COORDINATE_SHA256: str | None = (
    "54C053369C4D1D860B3ADB79B7B51B176AB934DA43477EBCDE7A38DF93983358"
)
EXPECTED_REJECT_COORDINATE_SHA256: str | None = (
    "863F40ACBE46CE33110E5D8FDDB49128C33F22F1A95452FFE4801038D9BF6BEB"
)
EXPECTED_ACCEPTED_SITE_SHA256: str | None = (
    "5194E3E6361BBC9791F18F9B98DC37366EA6933F92689AF4F748210BBE6978B7"
)
EXPECTED_REJECTED_SITE_SHA256: str | None = (
    "9D4D52DAE0DCBC38C923836249BEF3528A86D4E8E740D17B2594FEFE9713E1F3"
)
EXPECTED_ASSEMBLY_SHA256: str | None = (
    "902F2BB58BDFFAACEBF69972BE66D81FED92A1D3410CBA1D10C339CC221F2717"
)
EXPECTED_ACCEPTED_ROOT_SHA256: str | None = (
    "F5389A12EF6C98B456C38BEA56E710220E2EA81DE1F3B37B112ABA20F4A6615A"
)
EXPECTED_REJECTED_ROOT_SHA256: str | None = (
    "CAD70606F1AF2324BEFBCDA21C8581A7AEC60F73C5E21C3A863ACC8F9AE8E871"
)
EXPECTED_POTENTIAL_PROMOTION_COORDINATE_SHA256: str | None = (
    "998CAF454BA7AE62242E465391B90ED53810A830D0E1257191F2533AD5067B65"
)
EXPECTED_BLOCKED_PENDING_COORDINATE_SHA256: str | None = (
    "5353221004B1902876E0E27CF18C0541D1B24DB9001B8450350EF6B40C7284BD"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "EE379364FF07A9080E3CFCBB0D6804BB3213EDFF7213C14D37F4A6C46236DE1B"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_module(BASE_BUILDER, "pk_selector568_chunk2_review_engine_v1")
ASSIGN = load_module(
    ASSIGNMENT_BUILDER,
    "pk_selector568_chunk2_review_assignment_v1",
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
    chunk = assignment["chunks"][2]
    ENGINE.require(
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
        "selector 568 chunk-2 assignment drifted",
    )
    return assignment, chunk


def build_report() -> tuple[dict[str, Any], dict[str, str]]:
    report, frozen = _BASE_BUILD_REPORT()
    result = copy.deepcopy(report)
    proof = result["proof"]
    proof["all_78_sites_classified"] = proof.pop(
        "all_77_sites_classified"
    )
    proof["chunk2_live_pending_priority_sha256"] = (
        EXPECTED_CHUNK2_PRIORITY_SHA256
    )
    proof.pop("chunk0_live_pending_priority_sha256")
    result["scope"]["chunk_id"] = 2
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
