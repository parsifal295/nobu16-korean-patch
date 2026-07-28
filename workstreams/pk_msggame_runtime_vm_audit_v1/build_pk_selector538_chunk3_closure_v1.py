#!/usr/bin/env python3
"""Build the independent selector-538 chunk-3 runtime closure layer.

The frozen BF7B post-selector-1066 checkpoint is the predecessor. Dialogue
bodies and exact overrides remain private below ``tmp``; only source-free
coverage and promotion reports are tracked. Shared integration code and Steam
remain read only.
"""

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
DIALOGUE_WORKSTREAM = (
    REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
)
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
BASE_CLOSURE_PATH = WORKSTREAM / "build_pk_selector538_chunk1_closure_v1.py"
REVIEW_BUILDER_PATH = WORKSTREAM / "build_pk_selector538_chunk3_review_v1.py"
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_bound_terminal_2546_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    DIALOGUE_WORKSTREAM
    / "runtime_vm_integration."
    "post_bound_terminal_2546_checkpoint.source_free.v1.json"
)
PRIVATE_HANDOFF_PATH = (
    DIALOGUE_TMP / "family538_chunk3_analysis.private.v1.json"
)
REVIEW_PUBLIC_PATH = (
    WORKSTREAM
    / "public"
    / "pk_selector538_chunk3_review_proposal.v1.json"
)

DEFAULT_AUDIT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector538_chunk3_closure_coverage.v1.json"
)
DEFAULT_PROMOTION_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector538_chunk3_closure_promotion.v1.json"
)
DEFAULT_DECISION_OUTPUT = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector538_chunk3_closure_decisions.private.v1.jsonl"
)
DEFAULT_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_selector538_chunk3_closure_evidence.private.v1.jsonl"
)

AUDIT_SCHEMA = "nobu16.kr.pk-selector538-chunk3-closure-coverage.v1"
PROMOTION_SCHEMA = "nobu16.kr.pk-selector538-chunk3-closure-promotion.v1"
EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector538-chunk3-closure-evidence-row.v1"
)
OVERRIDE_SCHEMA = "nobu16.kr.pk-selector538-chunk3-exact-override.v1"
METHOD = "reversed_vm_pk_selector538_chunk3_independent_closure"
UPDATE_ACTION_FIELD = "selector538_chunk3_update_action"
EXACT_OVERRIDE_FIELD = "selector538_chunk3_exact_override_evidence"
SELECTOR = 538
TERMINALS = tuple(range(1916, 1923))

EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "838D162126925ECF706577688D35570853CDA68226AF3C8FFB7FE14C3943D072"
)
EXPECTED_HANDOFF_SHA256 = (
    "255BA2FC945ED52288C4829DAB27AC73726DCE0AEB5874279E92957362DCF41C"
)
EXPECTED_REVIEW_PUBLIC_SHA256 = (
    "5B04A1C7230DB3A99367F4959A0213C1E351E45B84E4076EED0ED1CC5A2B093C"
)
EXPECTED_PREDECESSOR_ROWS = 52_803
EXPECTED_PREDECESSOR_PENDING = 8_213
EXPECTED_PENDING_AFTER = 8_124
EXPECTED_BASELINE_CANDIDATE_SHA256 = (
    "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E"
)
EXPECTED_CANDIDATE_SHA256 = (
    "0A9EB099C94499D9BD24FE4162785BE6FB844A5E38412114EAB13E503C33AF08"
)
EXPECTED_REWRITE_ROWS = 37
EXPECTED_KEEP_ROWS = 1
EXPECTED_REJECTED_SITES = 32
EXPECTED_ACCEPTED_SITES = 38
EXPECTED_ACCEPTED_ASSEMBLIES = 266
EXPECTED_PROMOTION_ROWS = 89
EXPECTED_PROMOTION_ROOTS = 28
EXPECTED_REJECTED_PENDING_ROWS = 53
EXPECTED_REJECTED_ROOTS = 32
EXPECTED_REJECTED_PENDING_ROOTS = 24
EXPECTED_RENEWAL_ROWS = 420
EXPECTED_RENEWAL_ROOTS = 204
EXPECTED_DECISION_ROWS = 509
EXPECTED_CANDIDATE_AFFECTED_ROOTS = 340
EXPECTED_SOURCE_AFFECTED_ROOTS = 405
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 70,
    "translation_override_and_runtime_promotion": 19,
    "translation_override_and_verification_renewal": 18,
    "verification_renewal": 402,
}

EXPECTED_REWRITE_COORDINATE_SHA256 = (
    "DC2572C167E55C34184899AA08E4D039F472C678F53283E810064E955D50EEB1"
)
EXPECTED_REWRITE_MAP_SHA256 = (
    "AC56D5E47956F9E1945FBB5EE0AE53BC3FF1A5FD8D7FB6D4DBCCBA0EB4363B15"
)
EXPECTED_ACCEPTED_SITE_SHA256 = (
    "839A75F3A94E3A481A48ABA88E25ABBEC472C6427FDA61FB9F2C854CA08D0ACE"
)
EXPECTED_REJECTED_SITE_SHA256 = (
    "DA6DCBFB69F1C34F722EA69ED44CAF6824F3944DA4F09F71466EAAA435866E95"
)
EXPECTED_ACCEPTED_ROOT_SHA256 = (
    "86AB6997E1606D756AC42C6A8F60D3B47A1DB4D9CA7D5B09BBC367A6E5948F80"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "B0DE2E9A377CEB542135F330B1AC2B7358F272E66EA0E326F7674EA87646CFDD"
)
EXPECTED_PROMOTION_ROOT_SHA256 = (
    "74BE1E6D7438026DE1AD60D7740E988EEA0FBFCBEE8C8D3C23BC39DF10E474B0"
)
EXPECTED_REJECTED_COORDINATE_SHA256 = (
    "DD8D177F94A131E76A689AEA85276AB81FF2675E77FABC4378EBBD089E453159"
)
EXPECTED_REJECTED_ROOT_SHA256 = (
    "547145021BC455AEE7C609B74CA07507180D90D70E805ECE213049D43E202987"
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
EXPECTED_CANDIDATE_AFFECTED_ROOT_SHA256 = (
    "8EF7B4ED0FF43FACAB1B4D393D0198CAE3E2C7057A9D29EF3F22E21DB176BC50"
)
EXPECTED_SOURCE_AFFECTED_ROOT_SHA256 = (
    "1958C5972B0E9F1F7606DDD39F41FDCD05CE7A80AC1A7B63E357E3EA51358A64"
)
EXPECTED_ACCEPTED_ASSEMBLY_SHA256 = (
    "26205B4450FD2D2E40667CFDE045B007CF616D0350BA0912B34A0260DFDA9C78"
)

# Frozen after independently reproducible outputs are generated.
EXPECTED_AUDIT_FILE_SHA256 = (
    "91D52FB7ED6CD13DA6E15AFB77494A9D907EC78FDBC6CB399FABB2285C10103F"
)
EXPECTED_PROMOTION_FILE_SHA256 = (
    "BE3832142A04A989CEEA7259340089AD8AC18280FEF91AFD7C492E59262AAA47"
)
EXPECTED_DECISION_FILE_SHA256 = (
    "21F647B8D680DDA3639A95F289AAD8E9B442C00F05378CB213EEC847AE8CFC8C"
)
EXPECTED_EVIDENCE_FILE_SHA256 = (
    "36C8E2C923AB8F94F2E2C2218EC3F09B382FB5A7856533C0378F3668BDC00BD8"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(BASE_CLOSURE_PATH, "pk_selector538_chunk3_closure_base_v1")
REVIEW = load_module(REVIEW_BUILDER_PATH, "pk_selector538_chunk3_closure_review_v1")
CORE = BASE.BASE

_CORE_BUILD_ANALYSIS = BASE._BASE_BUILD_ANALYSIS
_CORE_BUILD_AUDIT = BASE._BASE_BUILD_AUDIT
_CORE_BUILD_UPDATED_ROWS = BASE._BASE_BUILD_UPDATED_ROWS


def patch_core_contract() -> None:
    replacements = {
        "REVIEW": REVIEW,
        "CALLER": REVIEW.CALLER,
        "HONORIFIC": REVIEW.CALLER.HONORIFIC,
        "CROSS": REVIEW.CALLER.CROSS,
        "BASE_AUDIT": REVIEW.BASE_AUDIT,
        "ENGINE": REVIEW.CALLER.ENGINE,
        "LIVE_STEAM_BASE": Path(REVIEW.CALLER.LIVE_STEAM_BASE),
        "LIVE_STEAM_PK": Path(REVIEW.CALLER.LIVE_STEAM_PK),
        "PREDECESSOR_PRIVATE_PATH": PREDECESSOR_PRIVATE_PATH,
        "PREDECESSOR_PUBLIC_PATH": PREDECESSOR_PUBLIC_PATH,
        "PRIVATE_HANDOFF_PATH": PRIVATE_HANDOFF_PATH,
        "REVIEW_PUBLIC_PATH": REVIEW_PUBLIC_PATH,
        "DEFAULT_AUDIT_OUTPUT": DEFAULT_AUDIT_OUTPUT,
        "DEFAULT_PROMOTION_OUTPUT": DEFAULT_PROMOTION_OUTPUT,
        "DEFAULT_DECISION_OUTPUT": DEFAULT_DECISION_OUTPUT,
        "DEFAULT_EVIDENCE_OUTPUT": DEFAULT_EVIDENCE_OUTPUT,
        "AUDIT_SCHEMA": AUDIT_SCHEMA,
        "PROMOTION_SCHEMA": PROMOTION_SCHEMA,
        "EVIDENCE_SCHEMA": EVIDENCE_SCHEMA,
        "OVERRIDE_SCHEMA": OVERRIDE_SCHEMA,
        "METHOD": METHOD,
        "UPDATE_ACTION_FIELD": UPDATE_ACTION_FIELD,
        "SELECTOR": SELECTOR,
        "TERMINALS": TERMINALS,
    }
    for name in (
        "EXPECTED_PREDECESSOR_PRIVATE_SHA256",
        "EXPECTED_PREDECESSOR_PUBLIC_SHA256",
        "EXPECTED_HANDOFF_SHA256",
        "EXPECTED_REVIEW_PUBLIC_SHA256",
        "EXPECTED_PREDECESSOR_ROWS",
        "EXPECTED_PREDECESSOR_PENDING",
        "EXPECTED_PENDING_AFTER",
        "EXPECTED_BASELINE_CANDIDATE_SHA256",
        "EXPECTED_CANDIDATE_SHA256",
        "EXPECTED_REWRITE_ROWS",
        "EXPECTED_KEEP_ROWS",
        "EXPECTED_REJECTED_SITES",
        "EXPECTED_ACCEPTED_SITES",
        "EXPECTED_ACCEPTED_ASSEMBLIES",
        "EXPECTED_PROMOTION_ROWS",
        "EXPECTED_PROMOTION_ROOTS",
        "EXPECTED_REJECTED_PENDING_ROWS",
        "EXPECTED_REJECTED_ROOTS",
        "EXPECTED_REJECTED_PENDING_ROOTS",
        "EXPECTED_RENEWAL_ROWS",
        "EXPECTED_RENEWAL_ROOTS",
        "EXPECTED_DECISION_ROWS",
        "EXPECTED_CANDIDATE_AFFECTED_ROOTS",
        "EXPECTED_SOURCE_AFFECTED_ROOTS",
        "EXPECTED_ACTION_COUNTS",
        "EXPECTED_REWRITE_COORDINATE_SHA256",
        "EXPECTED_REWRITE_MAP_SHA256",
        "EXPECTED_ACCEPTED_SITE_SHA256",
        "EXPECTED_REJECTED_SITE_SHA256",
        "EXPECTED_ACCEPTED_ROOT_SHA256",
        "EXPECTED_PROMOTION_COORDINATE_SHA256",
        "EXPECTED_PROMOTION_ROOT_SHA256",
        "EXPECTED_REJECTED_COORDINATE_SHA256",
        "EXPECTED_REJECTED_ROOT_SHA256",
        "EXPECTED_REJECTED_PENDING_ROOT_SHA256",
        "EXPECTED_RENEWAL_COORDINATE_SHA256",
        "EXPECTED_RENEWAL_ROOT_SHA256",
        "EXPECTED_DECISION_COORDINATE_SHA256",
        "EXPECTED_CANDIDATE_AFFECTED_ROOT_SHA256",
        "EXPECTED_SOURCE_AFFECTED_ROOT_SHA256",
        "EXPECTED_ACCEPTED_ASSEMBLY_SHA256",
        "EXPECTED_AUDIT_FILE_SHA256",
        "EXPECTED_PROMOTION_FILE_SHA256",
        "EXPECTED_DECISION_FILE_SHA256",
        "EXPECTED_EVIDENCE_FILE_SHA256",
    ):
        replacements[name] = globals()[name]
    for name, value in replacements.items():
        setattr(CORE, name, value)


def load_review() -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    CORE.require(
        CORE.sha256_file(PRIVATE_HANDOFF_PATH) == EXPECTED_HANDOFF_SHA256,
        "private chunk-3 handoff drifted",
    )
    public = CORE.load_json_exact(
        REVIEW_PUBLIC_PATH,
        EXPECTED_REVIEW_PUBLIC_SHA256,
    )
    assignment, chunk = REVIEW.load_assignment()
    world = REVIEW.load_world()
    handoff = REVIEW.load_json_exact(PRIVATE_HANDOFF_PATH)
    validated = REVIEW.validate_private_handoff(
        handoff,
        assignment=assignment,
        chunk=chunk,
        world=world,
    )
    result = public.get("result", {})
    proof = public.get("proof", {})
    CORE.require(
        public.get("schema") == REVIEW.PUBLIC_SCHEMA
        and public.get("status") == "PASS"
        and result.get("accepted_site_count") == EXPECTED_ACCEPTED_SITES
        and result.get("rewrite_coordinate_count") == EXPECTED_REWRITE_ROWS
        and result.get("keep_coordinate_count") == EXPECTED_KEEP_ROWS
        and result.get("reject_coordinate_count") == EXPECTED_REJECTED_SITES
        and result.get("proposal_candidate_sha256")
        == EXPECTED_CANDIDATE_SHA256
        and result.get("runtime_promotion_coordinate_count")
        == EXPECTED_PROMOTION_ROWS
        and result.get("blocked_pending_coordinate_count")
        == EXPECTED_REJECTED_PENDING_ROWS
        and result.get("verification_renewal_coordinate_count")
        == EXPECTED_RENEWAL_ROWS
        and proof.get("accepted_assembly_branches")
        == EXPECTED_ACCEPTED_ASSEMBLIES
        and proof.get("assembly_branches_recorded") == 490
        and proof.get(
            "all_accepted_current_relative_raw_g1n_nonexpanding"
        )
        is True
        and proof.get("all_accepted_register_branches_proven") is True
        and public.get("steam_write_performed") is False,
        "source-free chunk-3 proposal drifted",
    )
    return handoff, public, world, validated


def build_analysis(
    *,
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    world: Mapping[str, Any],
    handoff: Mapping[str, Any],
    validated: Mapping[str, Any],
) -> dict[str, Any]:
    adapted = copy.deepcopy(dict(handoff))
    for row in adapted["site_reviews"]:
        row["baseline_candidate_right"] = row["reviewed_candidate_right"]
    return _CORE_BUILD_ANALYSIS(
        predecessor_rows=predecessor_rows,
        world=world,
        handoff=adapted,
        validated=validated,
    )


def build_audit(
    *,
    analysis: Mapping[str, Any],
    predecessor_report: Mapping[str, Any],
    review_public: Mapping[str, Any],
) -> dict[str, Any]:
    report = _CORE_BUILD_AUDIT(
        analysis=analysis,
        predecessor_report=predecessor_report,
        review_public=review_public,
    )
    result = copy.deepcopy(report)
    result["proof"]["rejected_chunk3_pending_rows_unchanged"] = (
        result["proof"].pop("rejected_chunk0_pending_rows_unchanged")
    )
    result["scope"]["chunk_id"] = 3
    return CORE.HONORIFIC.seal_report(result)


def build_updated_rows(
    *,
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    analysis: Mapping[str, Any],
    audit: Mapping[str, Any],
    audit_file_sha256: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    updated_rows, evidence_rows = _CORE_BUILD_UPDATED_ROWS(
        predecessor_rows=predecessor_rows,
        analysis=analysis,
        audit=audit,
        audit_file_sha256=audit_file_sha256,
    )
    for row in updated_rows:
        if "selector538_chunk0_exact_override_evidence" in row:
            row[EXACT_OVERRIDE_FIELD] = row.pop(
                "selector538_chunk0_exact_override_evidence"
            )
    return updated_rows, evidence_rows


patch_core_contract()
CORE.load_review = load_review
CORE.build_analysis = build_analysis
CORE.build_audit = build_audit
CORE.build_updated_rows = build_updated_rows

ClosureError = CORE.ClosureError
require = CORE.require
sha256_bytes = CORE.sha256_bytes
sha256_file = CORE.sha256_file
canonical_bytes = CORE.canonical_bytes
canonical_json = CORE.canonical_json
canonical_jsonl = CORE.canonical_jsonl
canonical_sha256 = CORE.canonical_sha256
parse_coordinate = CORE.parse_coordinate
coordinate_digest = CORE.coordinate_digest
root_digest = CORE.root_digest
site_digest = CORE.site_digest
row_sort_key = CORE.row_sort_key
load_json_exact = CORE.load_json_exact
load_predecessor = CORE.load_predecessor
grouped_coordinates = CORE.grouped_coordinates
build_candidate = CORE.build_candidate
coordinates_for_roots = CORE.coordinates_for_roots
build_promotion = CORE.build_promotion
assert_source_free_report = CORE.assert_source_free_report
contains_body_key = CORE.contains_body_key
build_outputs = CORE.build_outputs
validate_outputs = CORE.validate_outputs
validate_output_paths = CORE.validate_output_paths
parse_args = CORE.parse_args
HONORIFIC = CORE.HONORIFIC
BASE_AUDIT = CORE.BASE_AUDIT
ENGINE = CORE.ENGINE
CALLER = CORE.CALLER
LIVE_STEAM_BASE = CORE.LIVE_STEAM_BASE
LIVE_STEAM_PK = CORE.LIVE_STEAM_PK


def main(argv: Sequence[str] | None = None) -> int:
    return CORE.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
