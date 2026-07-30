#!/usr/bin/env python3
"""Build the independent selector-538 chunk-1 runtime closure layer.

The frozen post-selector-1066 checkpoint is the predecessor. Dialogue bodies
and exact overrides remain private below ``tmp``; only source-free coverage
and promotion reports are tracked. Shared integration code and Steam remain
read only.
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
BASE_CLOSURE_PATH = WORKSTREAM / "build_pk_selector538_chunk0_closure_v1.py"
REVIEW_BUILDER_PATH = WORKSTREAM / "build_pk_selector538_chunk1_review_v1.py"
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
    DIALOGUE_TMP / "family538_chunk1_analysis.private.v1.json"
)
REVIEW_PUBLIC_PATH = (
    WORKSTREAM
    / "public"
    / "pk_selector538_chunk1_review_proposal.v1.json"
)

DEFAULT_AUDIT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector538_chunk1_closure_coverage.v1.json"
)
DEFAULT_PROMOTION_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector538_chunk1_closure_promotion.v1.json"
)
DEFAULT_DECISION_OUTPUT = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector538_chunk1_closure_decisions.private.v1.jsonl"
)
DEFAULT_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_selector538_chunk1_closure_evidence.private.v1.jsonl"
)

AUDIT_SCHEMA = "nobu16.kr.pk-selector538-chunk1-closure-coverage.v1"
PROMOTION_SCHEMA = "nobu16.kr.pk-selector538-chunk1-closure-promotion.v1"
EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector538-chunk1-closure-evidence-row.v1"
)
OVERRIDE_SCHEMA = "nobu16.kr.pk-selector538-chunk1-exact-override.v1"
METHOD = "reversed_vm_pk_selector538_chunk1_independent_closure"
UPDATE_ACTION_FIELD = "selector538_chunk1_update_action"
EXACT_OVERRIDE_FIELD = "selector538_chunk1_exact_override_evidence"
SELECTOR = 538
TERMINALS = tuple(range(1916, 1923))

EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "838D162126925ECF706577688D35570853CDA68226AF3C8FFB7FE14C3943D072"
)
EXPECTED_HANDOFF_SHA256 = (
    "E598C36F210BF91D02C09C6FE0BABD995212A542CACCAD60AA89CE6F91AE3E8F"
)
EXPECTED_REVIEW_PUBLIC_SHA256 = (
    "772622A0A474F5FC3388B49F78FEE2ADDCD297785A5C97CE4EB4285FAAD96502"
)
EXPECTED_PREDECESSOR_ROWS = 52_803
EXPECTED_PREDECESSOR_PENDING = 8_213
EXPECTED_PENDING_AFTER = 8_134
EXPECTED_BASELINE_CANDIDATE_SHA256 = (
    "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E"
)
EXPECTED_CANDIDATE_SHA256 = (
    "A8CDBB1CBD15E53BF77606C4E05425B861D28B80C6E8C327A219AE76FEFA6427"
)
EXPECTED_REWRITE_ROWS = 42
EXPECTED_KEEP_ROWS = 3
EXPECTED_REJECTED_SITES = 26
EXPECTED_ACCEPTED_SITES = 45
EXPECTED_ACCEPTED_ASSEMBLIES = 315
EXPECTED_PROMOTION_ROWS = 79
EXPECTED_PROMOTION_ROOTS = 34
EXPECTED_REJECTED_PENDING_ROWS = 15
EXPECTED_REJECTED_ROOTS = 26
EXPECTED_REJECTED_PENDING_ROOTS = 7
EXPECTED_RENEWAL_ROWS = 420
EXPECTED_RENEWAL_ROOTS = 204
EXPECTED_DECISION_ROWS = 499
EXPECTED_CANDIDATE_AFFECTED_ROOTS = 340
EXPECTED_SOURCE_AFFECTED_ROOTS = 405
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 66,
    "translation_override_and_runtime_promotion": 13,
    "translation_override_and_verification_renewal": 29,
    "verification_renewal": 391,
}

EXPECTED_REWRITE_COORDINATE_SHA256 = (
    "BA3630B6AA76665ACD2018BADD5439C3C14D3D0F01D8A5241FB5DB220F885780"
)
EXPECTED_REWRITE_MAP_SHA256 = (
    "93F33083089071A083151B85A1CBD5EDA762211CF1C6C1D6F5B392E67235CF3C"
)
EXPECTED_ACCEPTED_SITE_SHA256 = (
    "3869A52B0B9426C54E406AB5A763353046B9B27C3261E415CF8CD958331A82A7"
)
EXPECTED_REJECTED_SITE_SHA256 = (
    "7A9D19FCF78D0CB81D47F09948BCDFDD3E12F47429F25DC4A971E00E65DE4355"
)
EXPECTED_ACCEPTED_ROOT_SHA256 = (
    "57DCA1F009604A61CD579FF8239D93A6AB4F58CAA211D8CE3AED811249C61924"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "3BCA0D28A86BBACA0732614473B45B5C72A9669BB080DF772188E6478287DEF8"
)
EXPECTED_PROMOTION_ROOT_SHA256 = (
    "09F4132381ADB06DBC8F11CD13B439CCAA573A235F1659B3508BB524139DF536"
)
EXPECTED_REJECTED_COORDINATE_SHA256 = (
    "588A99104D245BDC13639A9E9BAFD85E55405DE79C59F8E89D90D9D02DD641DE"
)
EXPECTED_REJECTED_ROOT_SHA256 = (
    "DCBD4146BCDDA3946A11DB16203768A0A812F3715CF59FDDD82E5F5F2C29D185"
)
EXPECTED_REJECTED_PENDING_ROOT_SHA256 = (
    "8AA5842A0C24C70AEA5C92C3A49E66B7B8B6ADD959EB3DC2469107383B858D80"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "36058C249C73F5B42C0DC7426FA68879F4BDC515F40F9C50B6CFEC07C7FD4D59"
)
EXPECTED_RENEWAL_ROOT_SHA256 = (
    "65AB478BEE4C7F7102084ACDD7D1268C33F5FE93DDA278F69DEB7D59C502AE92"
)
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "876D5F6B96D0C50D245F7E176E0AE038BBB4BC0D4D4A9EB29F48B76AD89DF829"
)
EXPECTED_CANDIDATE_AFFECTED_ROOT_SHA256 = (
    "8EF7B4ED0FF43FACAB1B4D393D0198CAE3E2C7057A9D29EF3F22E21DB176BC50"
)
EXPECTED_SOURCE_AFFECTED_ROOT_SHA256 = (
    "1958C5972B0E9F1F7606DDD39F41FDCD05CE7A80AC1A7B63E357E3EA51358A64"
)

# Frozen after independently reproducible outputs are generated.
EXPECTED_ACCEPTED_ASSEMBLY_SHA256: str | None = (
    "2F0F7F81B3AEC6CEBB139B2EC2EBB32B610A60732C24CCCC81B7237639CA5977"
)
EXPECTED_AUDIT_FILE_SHA256: str | None = (
    "CA0ADCF4ADDA5AF0AEEC28DDEDE3ECED87121BD391B428102FB6CAFFD5A73717"
)
EXPECTED_PROMOTION_FILE_SHA256: str | None = (
    "EC3BCB3E9246B8B3C837CFC1929F76E278B99B8483450CA57EEE0175CFA388E0"
)
EXPECTED_DECISION_FILE_SHA256: str | None = (
    "1FFA7BF45AA7DE0E53EFE3ED59BDED1E824A39F3E2CC4FD0E8CFFAC6D28A4D70"
)
EXPECTED_EVIDENCE_FILE_SHA256: str | None = (
    "D20256F303BE835F079883C856E1D3C1A8949C5E775ABB61CBFD421FEC9F9647"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(BASE_CLOSURE_PATH, "pk_selector538_chunk1_closure_base_v1")
REVIEW = load_module(REVIEW_BUILDER_PATH, "pk_selector538_chunk1_closure_review_v1")

_BASE_BUILD_ANALYSIS = BASE.build_analysis
_BASE_BUILD_AUDIT = BASE.build_audit
_BASE_BUILD_UPDATED_ROWS = BASE.build_updated_rows


def patch_base_contract() -> None:
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
        setattr(BASE, name, value)


def load_review() -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    BASE.require(
        BASE.sha256_file(PRIVATE_HANDOFF_PATH) == EXPECTED_HANDOFF_SHA256,
        "private chunk-1 handoff drifted",
    )
    public = BASE.load_json_exact(
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
    BASE.require(
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
        and proof.get("assembly_branches_recorded") == 497
        and proof.get(
            "all_accepted_current_relative_raw_g1n_nonexpanding"
        )
        is True
        and proof.get("all_accepted_register_branches_proven") is True
        and public.get("steam_write_performed") is False,
        "source-free chunk-1 proposal drifted",
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
    return _BASE_BUILD_ANALYSIS(
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
    report = _BASE_BUILD_AUDIT(
        analysis=analysis,
        predecessor_report=predecessor_report,
        review_public=review_public,
    )
    result = copy.deepcopy(report)
    result["proof"]["rejected_chunk1_pending_rows_unchanged"] = (
        result["proof"].pop("rejected_chunk0_pending_rows_unchanged")
    )
    result["scope"]["chunk_id"] = 1
    return BASE.HONORIFIC.seal_report(result)


def build_updated_rows(
    *,
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    analysis: Mapping[str, Any],
    audit: Mapping[str, Any],
    audit_file_sha256: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    updated_rows, evidence_rows = _BASE_BUILD_UPDATED_ROWS(
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


patch_base_contract()
BASE.load_review = load_review
BASE.build_analysis = build_analysis
BASE.build_audit = build_audit
BASE.build_updated_rows = build_updated_rows

ClosureError = BASE.ClosureError
require = BASE.require
sha256_bytes = BASE.sha256_bytes
sha256_file = BASE.sha256_file
canonical_bytes = BASE.canonical_bytes
canonical_json = BASE.canonical_json
canonical_jsonl = BASE.canonical_jsonl
canonical_sha256 = BASE.canonical_sha256
parse_coordinate = BASE.parse_coordinate
coordinate_digest = BASE.coordinate_digest
root_digest = BASE.root_digest
site_digest = BASE.site_digest
row_sort_key = BASE.row_sort_key
load_json_exact = BASE.load_json_exact
load_predecessor = BASE.load_predecessor
grouped_coordinates = BASE.grouped_coordinates
build_candidate = BASE.build_candidate
coordinates_for_roots = BASE.coordinates_for_roots
build_promotion = BASE.build_promotion
assert_source_free_report = BASE.assert_source_free_report
contains_body_key = BASE.contains_body_key
build_outputs = BASE.build_outputs
validate_outputs = BASE.validate_outputs
validate_output_paths = BASE.validate_output_paths
parse_args = BASE.parse_args
HONORIFIC = BASE.HONORIFIC
BASE_AUDIT = BASE.BASE_AUDIT
ENGINE = BASE.ENGINE
CALLER = BASE.CALLER
LIVE_STEAM_BASE = BASE.LIVE_STEAM_BASE
LIVE_STEAM_PK = BASE.LIVE_STEAM_PK


def main(argv: Sequence[str] | None = None) -> int:
    return BASE.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
