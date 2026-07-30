#!/usr/bin/env python3
"""Validate selector 538 chunk 3 and build its source-free proposal report."""

from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
BASE_REVIEW_PATH = WORKSTREAM / "build_pk_selector538_chunk1_review_v1.py"
ASSIGNMENT_PATH = DIALOGUE_TMP / "family538_assignment.private.v1.json"
PRIVATE_HANDOFF_PATH = (
    DIALOGUE_TMP / "family538_chunk3_analysis.private.v1.json"
)
CHUNK0_PRIVATE_HANDOFF_PATH = (
    DIALOGUE_TMP / "family538_chunk0_analysis.private.v1.json"
)
CHUNK1_PRIVATE_HANDOFF_PATH = (
    DIALOGUE_TMP / "family538_chunk1_analysis.private.v1.json"
)
DEFAULT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector538_chunk3_review_proposal.v1.json"
)

PRIVATE_SCHEMA = "nobu16.kr.pk-selector538-chunk3-analysis.private.v1"
PUBLIC_SCHEMA = "nobu16.kr.pk-selector538-chunk3-review-proposal.v1"
METHOD = "reversed_vm_pk_selector538_chunk3_full_caller_review"
SELECTOR = 538
TERMINALS = tuple(range(1916, 1923))
ORDINAL_START = 207
ORDINAL_END = 276
EXPECTED_SITE_COUNT = 70
EXPECTED_ROOT_COUNT = 69
EXPECTED_ASSEMBLY_COUNT = 490
EXPECTED_ACCEPTED = 38
EXPECTED_REWRITE = 37
EXPECTED_KEEP = 1
EXPECTED_REJECT = 32
EXPECTED_ACCEPTED_ROOTS = 37
EXPECTED_REJECTED_ROOTS = 32
EXPECTED_ACCEPTED_ASSEMBLIES = 266
EXPECTED_REJECTED_ASSEMBLIES = 224
EXPECTED_POTENTIAL_PROMOTION_COUNT = 89
EXPECTED_BLOCKED_PENDING_COUNT = 53
EXPECTED_PROMOTION_ROOTS = 28
EXPECTED_REJECTED_PENDING_ROOTS = 24
EXPECTED_RENEWAL_ROWS = 420
EXPECTED_RENEWAL_ROOTS = 204
EXPECTED_DECISION_ROWS = 509
EXPECTED_PREDECESSOR_ROWS = 52_803
EXPECTED_PREDECESSOR_PENDING = 8_213
EXPECTED_PENDING_AFTER = 8_124
EXPECTED_CANDIDATE_AFFECTED_ROOTS = 340
EXPECTED_SOURCE_AFFECTED_ROOTS = 405
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 70,
    "translation_override_and_runtime_promotion": 19,
    "translation_override_and_verification_renewal": 18,
    "verification_renewal": 402,
}

EXPECTED_ASSIGNMENT_SHA256 = (
    "57FBEE8EEC3551DAD8A7F1BB77CD7B2E2CF08109CB3A912452BE8244BB0FAACF"
)
EXPECTED_BASELINE_CANDIDATE_SHA256 = (
    "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E"
)
EXPECTED_LEDGER_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_CHUNK_SITE_SHA256 = (
    "A38F29C9C0C872A3768A614D7F4EC981E43C7BA683FF25FD41544FA49E8438DA"
)
EXPECTED_CHUNK_ROOT_SHA256 = (
    "4F3DBB3FCFD2E6F64ED51313E74056E59A60EC6A2F302E263692C8A8A0C93754"
)
EXPECTED_PENDING_COORDINATE_SHA256 = (
    "6E4B581AEF159CCC79DF7EBDE9874169AD287B3F591C6F5138DB625AFA858130"
)
EXPECTED_PENDING_ROW_UPPER_BOUND = 142
EXPECTED_CHUNK0_PRIVATE_HANDOFF_SHA256 = (
    "9A8CE09CCA100FCA9C5F9C148EDA38C043D8737218F2B4A11F3CDF2B7A7A92BF"
)
EXPECTED_CHUNK1_PRIVATE_HANDOFF_SHA256 = (
    "E598C36F210BF91D02C09C6FE0BABD995212A542CACCAD60AA89CE6F91AE3E8F"
)

# Frozen after the private handoff and public report are reproduced.
EXPECTED_PRIVATE_HANDOFF_SHA256 = (
    "255BA2FC945ED52288C4829DAB27AC73726DCE0AEB5874279E92957362DCF41C"
)
EXPECTED_PROPOSAL_CANDIDATE_SHA256 = (
    "0A9EB099C94499D9BD24FE4162785BE6FB844A5E38412114EAB13E503C33AF08"
)
EXPECTED_REWRITE_COORDINATE_SHA256 = (
    "DC2572C167E55C34184899AA08E4D039F472C678F53283E810064E955D50EEB1"
)
EXPECTED_KEEP_COORDINATE_SHA256 = (
    "E6EA4B3FF0AEECC03490959B8E83B425B822A7AD48105740D84C8DD546AE5567"
)
EXPECTED_REJECT_COORDINATE_SHA256 = (
    "93A3539BD109B85C6ED03A9DA6634EF4072A52E480A1778EB8A0901D6C4969D7"
)
EXPECTED_ACCEPTED_SITE_SHA256 = (
    "839A75F3A94E3A481A48ABA88E25ABBEC472C6427FDA61FB9F2C854CA08D0ACE"
)
EXPECTED_REJECTED_SITE_SHA256 = (
    "DA6DCBFB69F1C34F722EA69ED44CAF6824F3944DA4F09F71466EAAA435866E95"
)
EXPECTED_ASSEMBLY_SHA256 = (
    "69B6899B1FD809D4846AD984E5A608349B87C8AEECBBFAD1D755A3E64FDF9B0C"
)
EXPECTED_ACCEPTED_ROOT_SHA256 = (
    "86AB6997E1606D756AC42C6A8F60D3B47A1DB4D9CA7D5B09BBC367A6E5948F80"
)
EXPECTED_REJECTED_ROOT_SHA256 = (
    "547145021BC455AEE7C609B74CA07507180D90D70E805ECE213049D43E202987"
)
EXPECTED_POTENTIAL_PROMOTION_COORDINATE_SHA256 = (
    "B0DE2E9A377CEB542135F330B1AC2B7358F272E66EA0E326F7674EA87646CFDD"
)
EXPECTED_BLOCKED_PENDING_COORDINATE_SHA256 = (
    "DD8D177F94A131E76A689AEA85276AB81FF2675E77FABC4378EBBD089E453159"
)
EXPECTED_CHUNK0_OVERLAP_SHA256 = (
    "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
)
EXPECTED_ACCEPTED_ASSEMBLY_SHA256 = (
    "26205B4450FD2D2E40667CFDE045B007CF616D0350BA0912B34A0260DFDA9C78"
)
EXPECTED_PROMOTION_ROOT_SHA256 = (
    "74BE1E6D7438026DE1AD60D7740E988EEA0FBFCBEE8C8D3C23BC39DF10E474B0"
)
EXPECTED_REJECTED_PENDING_ROOT_SHA256 = (
    "6D03F01846473C6DE75CB569B207261F8C6AD797684F0E030BC20DC466E624E3"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "36058C249C73F5B42C0DC7426FA68879F4BDC515F40F9C50B6CFEC07C7FD4D59"
)
EXPECTED_RENEWAL_ROOT_SHA256 = (
    "65AB478BEE4C7F7102084ACDD7D1268C33F5FE93DDA278F69DEB7D59C502AE92"
)
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "DDD94F031325CFE8BF6D752CA34F1E9F6F13B4F50B8D47ABBC184FAA4B0192B9"
)
EXPECTED_ACTION_SHA256 = (
    "708186E688453A7F337E1491239E1CDE6EAE81EFDD18725D90817B96DDE42355"
)
EXPECTED_PUBLIC_FILE_SHA256 = (
    "5B04A1C7230DB3A99367F4959A0213C1E351E45B84E4076EED0ED1CC5A2B093C"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(BASE_REVIEW_PATH, "pk_selector538_chunk3_review_base_v1")
_BASE_BUILD_REPORT = BASE.build_report


def patch_base_contract() -> None:
    replacements = {
        "ASSIGNMENT_PATH": ASSIGNMENT_PATH,
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
        "EXPECTED_PROMOTION_ROOTS",
        "EXPECTED_REJECTED_PENDING_ROOTS",
        "EXPECTED_RENEWAL_ROWS",
        "EXPECTED_RENEWAL_ROOTS",
        "EXPECTED_DECISION_ROWS",
        "EXPECTED_PREDECESSOR_ROWS",
        "EXPECTED_PREDECESSOR_PENDING",
        "EXPECTED_PENDING_AFTER",
        "EXPECTED_CANDIDATE_AFFECTED_ROOTS",
        "EXPECTED_SOURCE_AFFECTED_ROOTS",
        "EXPECTED_ACTION_COUNTS",
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
        "EXPECTED_CHUNK0_OVERLAP_SHA256",
        "EXPECTED_ACCEPTED_ASSEMBLY_SHA256",
        "EXPECTED_PROMOTION_ROOT_SHA256",
        "EXPECTED_REJECTED_PENDING_ROOT_SHA256",
        "EXPECTED_RENEWAL_COORDINATE_SHA256",
        "EXPECTED_RENEWAL_ROOT_SHA256",
        "EXPECTED_DECISION_COORDINATE_SHA256",
        "EXPECTED_ACTION_SHA256",
        "EXPECTED_PUBLIC_FILE_SHA256",
    ):
        replacements[name] = globals()[name]
    for name, value in replacements.items():
        setattr(BASE, name, value)


def load_assignment() -> tuple[dict[str, Any], dict[str, Any]]:
    BASE.require(
        BASE.sha256_file(ASSIGNMENT_PATH) == EXPECTED_ASSIGNMENT_SHA256,
        "selector 538 assignment hash drifted",
    )
    assignment = BASE.load_json_exact(ASSIGNMENT_PATH)
    BASE.require(
        assignment.get("schema") == BASE.ASSIGN.SCHEMA,
        "selector 538 assignment schema drifted",
    )
    chunk = assignment["chunks"][3]
    BASE.require(
        chunk.get("chunk_id") == 3
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
        "selector 538 chunk-3 assignment drifted",
    )
    return assignment, chunk


def validate_chunk1_overlap(
    reviewed_map: Mapping[str, str],
    recorded: Mapping[str, Any],
) -> dict[str, Any]:
    BASE.require(
        BASE.sha256_file(CHUNK1_PRIVATE_HANDOFF_PATH)
        == EXPECTED_CHUNK1_PRIVATE_HANDOFF_SHA256,
        "chunk-1 private handoff drifted",
    )
    chunk1 = BASE.load_json_exact(CHUNK1_PRIVATE_HANDOFF_PATH)
    chunk1_reviewed = chunk1.get("exact_maps", {}).get("reviewed")
    BASE.require(isinstance(chunk1_reviewed, dict), "chunk-1 map absent")
    overlap = sorted(
        set(reviewed_map) & set(chunk1_reviewed),
        key=BASE.parse_coordinate,
    )
    identical = all(
        reviewed_map[coordinate] == chunk1_reviewed[coordinate]
        for coordinate in overlap
    )
    manifest = [
        [
            coordinate,
            BASE.sha256_bytes(str(reviewed_map[coordinate]).encode("utf-8")),
        ]
        for coordinate in overlap
    ]
    digest = BASE.canonical_sha256(manifest)
    BASE.require(
        identical
        and recorded.get("coordinate_count") == len(overlap)
        and recorded.get("all_overlapping_values_identical") is True
        and recorded.get("canonical_sha256") == digest,
        "chunk-1 exact-map overlap contract drifted",
    )
    return {
        "all_overlapping_values_identical": identical,
        "canonical_sha256": digest,
        "coordinate_count": len(overlap),
    }


def build_report() -> tuple[dict[str, Any], dict[str, str]]:
    report, _frozen = _BASE_BUILD_REPORT()
    handoff = BASE.load_json_exact(PRIVATE_HANDOFF_PATH)
    chunk1_overlap = validate_chunk1_overlap(
        handoff["exact_maps"]["reviewed"],
        handoff.get("chunk1_exact_map_overlap", {}),
    )
    result = copy.deepcopy(report)
    result["proof"]["all_70_sites_classified"] = result["proof"].pop(
        "all_71_sites_classified"
    )
    result["proof"]["chunk1_exact_map_overlap"] = chunk1_overlap
    result["scope"]["chunk_id"] = 3
    guards = result.pop("guards")
    result["guards"] = {
        "private_handoff_sha256": guards["private_handoff_sha256"],
        "report_payload_sha256": BASE.canonical_sha256(result),
        "steam_archive_sha256_before":
            guards["steam_archive_sha256_before"],
        "steam_archive_sha256_after": guards["steam_archive_sha256_after"],
    }
    frozen = {
        "accepted_assembly_sha256": result["proof"][
            "accepted_assembly_canonical_sha256"
        ],
        "accepted_root_sha256": result["result"]["accepted_root_sha256"],
        "accepted_site_sha256": result["result"]["accepted_site_sha256"],
        "action_sha256": result["proof"][
            "runtime_action_manifest_canonical_sha256"
        ],
        "assembly_sha256": result["proof"]["assembly_canonical_sha256"],
        "blocked_pending_coordinate_sha256": result["result"][
            "blocked_pending_coordinate_sha256"
        ],
        "chunk0_overlap_sha256": result["proof"][
            "chunk0_exact_map_overlap"
        ]["canonical_sha256"],
        "decision_coordinate_sha256": result["result"][
            "decision_delta_coordinate_sha256"
        ],
        "keep_coordinate_sha256": result["result"][
            "keep_coordinate_sha256"
        ],
        "private_handoff_sha256": guards["private_handoff_sha256"],
        "proposal_candidate_sha256": result["result"][
            "proposal_candidate_sha256"
        ],
        "potential_promotion_coordinate_sha256": result["result"][
            "potential_promotion_coordinate_sha256"
        ],
        "promotion_root_sha256": result["result"][
            "runtime_promotion_root_sha256"
        ],
        "reject_coordinate_sha256": result["result"][
            "reject_coordinate_sha256"
        ],
        "rejected_pending_root_sha256": result["result"][
            "rejected_pending_root_sha256"
        ],
        "rejected_root_sha256": result["result"]["rejected_root_sha256"],
        "rejected_site_sha256": result["result"]["rejected_site_sha256"],
        "renewal_coordinate_sha256": result["result"][
            "verification_renewal_coordinate_sha256"
        ],
        "renewal_root_sha256": result["result"][
            "verification_renewal_root_sha256"
        ],
        "rewrite_coordinate_sha256": result["result"][
            "rewrite_coordinate_sha256"
        ],
    }
    return result, frozen


patch_base_contract()
BASE.load_assignment = load_assignment
BASE.build_report = build_report

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
load_world = BASE.load_world
validate_private_handoff = BASE.validate_private_handoff
build_runtime_classification = BASE.build_runtime_classification
validate_frozen = BASE.validate_frozen
serialized_report = BASE.serialized_report
parse_args = BASE.parse_args
ASSIGN = BASE.ASSIGN
CALLER = BASE.CALLER
BASE_AUDIT = BASE.BASE_AUDIT
ENGINE = BASE.CALLER.ENGINE


def main(argv: Sequence[str] | None = None) -> int:
    return BASE.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
