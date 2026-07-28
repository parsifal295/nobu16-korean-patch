#!/usr/bin/env python3
"""Validate selector-1096 chunk-1 and build its source-free review report."""

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
    DIALOGUE_TMP / "family1096_chunk1_analysis.private.v1.json"
)
DEFAULT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector1096_chunk1_review_proposal.v1.json"
)

PRIVATE_SCHEMA = "nobu16.kr.pk-selector1096-chunk1-analysis.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector1096-chunk1-review-proposal.v1"
METHOD = "reversed_vm_pk_selector1096_chunk1_full_caller_review"
SELECTOR = 1096
TERMINALS = tuple(range(2581, 2588))
ORDINAL_START = 56
ORDINAL_END = 114
EXPECTED_SITE_COUNT = 59
EXPECTED_ROOT_COUNT = 58
EXPECTED_ASSEMBLY_COUNT = 413
EXPECTED_ACCEPTED = 50
EXPECTED_REWRITE = 46
EXPECTED_KEEP = 4
EXPECTED_REJECT = 9
EXPECTED_ACCEPTED_ROOTS = 50
EXPECTED_REJECTED_ROOTS = 8
EXPECTED_ACCEPTED_ASSEMBLIES = 350
EXPECTED_REJECTED_ASSEMBLIES = 63
EXPECTED_POTENTIAL_PROMOTION_COUNT = 78
EXPECTED_BLOCKED_PENDING_COUNT = 13
EXPECTED_ACCEPTED_CURRENT_LIVE = 78
EXPECTED_ACCEPTED_LIVE_AFTER_SELECTOR538_PLAN = 72

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
    "E4A0F3795A236DD83276E3304912A5C9E32751CDDB15C2F50B76C75A36B61FCA"
)
EXPECTED_CHUNK_ROOT_SHA256 = (
    "F3B4E40E649F62CB7C5E9019EC4EB418484C16BDBCFB9D60305DD8B5D8818FFA"
)
EXPECTED_PENDING_COORDINATE_SHA256 = (
    "6EC8C17EB01B6E1F9A94FEEC2A8DDC82D8C4CD5E2C6EDC8750A0BC7ACB2D1D2F"
)
EXPECTED_PENDING_ROW_UPPER_BOUND = 91
EXPECTED_CHUNK0_PRIORITY_SHA256 = EXPECTED_PENDING_COORDINATE_SHA256

EXPECTED_PRIVATE_HANDOFF_SHA256: str | None = (
    "7B3BC7DA3AEBC2F49FBE20C4777D2307BC3D0C3C86E0EC30189174284D7C719D"
)
EXPECTED_PROPOSAL_CANDIDATE_SHA256: str | None = (
    "4EF2FF6ACA78559F6B5B0D07E32E9FAB674DC113C754E9EE03BD43683A1DDAA7"
)
EXPECTED_REWRITE_COORDINATE_SHA256: str | None = (
    "FDC65FE67D353C1E20ADDF209743785C691EC9D8DE604A1AC69440D1A675C39B"
)
EXPECTED_KEEP_COORDINATE_SHA256: str | None = (
    "CA191EC4B55339DF6AF042B0EB55C3D81226FA509E1027F9C4CB8D8175DB13DD"
)
EXPECTED_REJECT_COORDINATE_SHA256: str | None = (
    "160B0ECF169900B350550F4C9B9CE80AD70B2C91F7DED377FE225DB8C0E33981"
)
EXPECTED_ACCEPTED_SITE_SHA256: str | None = (
    "0E7C9F63E06188FE48636A5EC44B3BAA6D980A6D3AB07DFF14903D9C23C1B313"
)
EXPECTED_REJECTED_SITE_SHA256: str | None = (
    "90A3D51F9F1BEE4DB773C78E6B4BD96276973B911B4CD28D2940849FD0159DAE"
)
EXPECTED_ASSEMBLY_SHA256: str | None = (
    "F6EBCE3C8221EA89FB50099F54C3B85E05ABA9882605C4A1902AEF4B0FC0296D"
)
EXPECTED_ACCEPTED_ROOT_SHA256: str | None = (
    "66C2B65A18E292F4C36910CB26D618835EBE16859986E57136046020545B870F"
)
EXPECTED_REJECTED_ROOT_SHA256: str | None = (
    "002EFEFA2E8A6D292ECF193F8DB1B544041025984A1AB808B395F666B0AC6029"
)
EXPECTED_POTENTIAL_PROMOTION_COORDINATE_SHA256: str | None = (
    "60F19B80260ABEF101EB0FD367B4DD75C7779AB3525D4DAD692D6425EBAB786E"
)
EXPECTED_BLOCKED_PENDING_COORDINATE_SHA256: str | None = (
    "194BD74F8E0029211054B3BA18D39F859B1F5D250CB64B977277804A55C72844"
)
EXPECTED_ACCEPTED_CURRENT_LIVE_SHA256: str | None = (
    "60F19B80260ABEF101EB0FD367B4DD75C7779AB3525D4DAD692D6425EBAB786E"
)
EXPECTED_ACCEPTED_LIVE_AFTER_SELECTOR538_PLAN_SHA256: str | None = (
    "F5E715D108BF66D16448B77A489B5792CFB7D4C99AB23B5C77223EAB2C8DAE73"
)
EXPECTED_PUBLIC_FILE_SHA256: str | None = (
    "7421A90EB3A33D465D151B0EC0039A4CB303F81B5F001D2408D1FB07C2137AF8"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(BASE_BUILDER, "pk_selector1096_chunk1_review_base_v1")
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
    chunk = assignment["chunks"][1]
    require(
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
        "selector 1096 chunk-1 assignment drifted",
    )
    return assignment, chunk


def build_report() -> tuple[dict[str, Any], dict[str, str]]:
    report, frozen = _BASE_BUILD_REPORT()
    result = copy.deepcopy(report)
    result["proof"]["all_59_sites_classified"] = result["proof"].pop(
        "all_56_sites_classified"
    )
    result["proof"]["chunk1_pending_coordinate_sha256"] = (
        result["proof"].pop("chunk0_live_pending_priority_sha256")
    )
    result["scope"]["chunk_id"] = 1
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
