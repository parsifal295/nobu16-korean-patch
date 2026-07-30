#!/usr/bin/env python3
"""Build the independent selector-1096 chunk-2 runtime closure layer."""

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
BASE_CLOSURE_PATH = WORKSTREAM / "build_pk_selector1096_chunk1_closure_v1.py"
REVIEW_BUILDER_PATH = WORKSTREAM / "build_pk_selector1096_chunk2_review_v1.py"
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
    DIALOGUE_TMP / "family1096_chunk2_analysis.private.v1.json"
)
REVIEW_PUBLIC_PATH = (
    WORKSTREAM
    / "public"
    / "pk_selector1096_chunk2_review_proposal.v1.json"
)
DEFAULT_AUDIT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector1096_chunk2_closure_coverage.v1.json"
)
DEFAULT_PROMOTION_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector1096_chunk2_closure_promotion.v1.json"
)
DEFAULT_DECISION_OUTPUT = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector1096_chunk2_closure_decisions.private.v1.jsonl"
)
DEFAULT_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_selector1096_chunk2_closure_evidence.private.v1.jsonl"
)

AUDIT_SCHEMA = "nobu16.kr.pk-selector1096-chunk2-closure-coverage.v1"
PROMOTION_SCHEMA = "nobu16.kr.pk-selector1096-chunk2-closure-promotion.v1"
EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector1096-chunk2-closure-evidence-row.v1"
)
OVERRIDE_SCHEMA = "nobu16.kr.pk-selector1096-chunk2-exact-override.v1"
METHOD = "reversed_vm_pk_selector1096_chunk2_independent_closure"
UPDATE_ACTION_FIELD = "selector1096_chunk2_update_action"
EXACT_OVERRIDE_FIELD = "selector1096_chunk2_exact_override_evidence"
SUPERSESSION_FIELD = (
    "selector1096_chunk2_selector538_evidence_supersession"
)
SELECTOR = 1096
TERMINALS = tuple(range(2581, 2588))

EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "838D162126925ECF706577688D35570853CDA68226AF3C8FFB7FE14C3943D072"
)
EXPECTED_HANDOFF_SHA256 = (
    "B07587B8B357F5C49445A9DE725840DD9FA7A05B5D3F0C2278597D3215790303"
)
EXPECTED_REVIEW_PUBLIC_SHA256 = (
    "55BF8BCA0AD81CF9F45E1E010DACB74356B73E31C1CA7E55EE4158F8263C8D6A"
)
EXPECTED_PREDECESSOR_ROWS = 52_803
EXPECTED_PREDECESSOR_PENDING = 8_213
EXPECTED_PENDING_AFTER = 8_146
EXPECTED_BASELINE_CANDIDATE_SHA256 = (
    "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E"
)
EXPECTED_CANDIDATE_SHA256 = (
    "F0F9DCCECA33105E6235A20E3F812094DC120465ECCC75CB094FB3F2E8F3F6F7"
)
EXPECTED_REWRITE_ROWS = 47
EXPECTED_KEEP_ROWS = 2
EXPECTED_REJECTED_SITES = 8
EXPECTED_ACCEPTED_SITES = 49
EXPECTED_ACCEPTED_ASSEMBLIES = 343
EXPECTED_PROMOTION_ROWS = 67
EXPECTED_PROMOTION_ROOTS = 33
EXPECTED_REJECTED_PENDING_ROWS = 12
EXPECTED_REJECTED_ROOTS = 8
EXPECTED_REJECTED_PENDING_ROOTS = 6
EXPECTED_RENEWAL_ROWS = 203
EXPECTED_RENEWAL_ROOTS = 98
EXPECTED_DECISION_ROWS = 270
EXPECTED_CANDIDATE_AFFECTED_ROOTS = 239
EXPECTED_SOURCE_AFFECTED_ROOTS = 258
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 45,
    "translation_override_and_runtime_promotion": 22,
    "translation_override_and_verification_renewal": 25,
    "verification_renewal": 178,
}

EXPECTED_REWRITE_COORDINATE_SHA256 = (
    "3800FC160FDED5EABD5EB037A5D8A5452B842994DAF0B4179298EBFF342E212E"
)
EXPECTED_REWRITE_MAP_SHA256 = (
    "69A131148A20C696B8E507013AD69BE2DDF1CFE11E0006C3E239D15C3A2410C9"
)
EXPECTED_ACCEPTED_SITE_SHA256 = (
    "FA118B222DF42FFEEF72951A16097A4A98714FE096AB6D6BE23090A814231B7A"
)
EXPECTED_REJECTED_SITE_SHA256 = (
    "908A64BE776E9ADB4E641400C3B368343F3D2EFE991FFAA3F8DEA1D6E02EC6AD"
)
EXPECTED_ACCEPTED_ROOT_SHA256 = (
    "31B3CA059158B715787576F2D7B1F1D65A6ABDCAC54873F44BE47CC573296A80"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "798836E8F1B8FCF2826BAC76314C483930D36D2E36300D1161A8F04A24C94F72"
)
EXPECTED_PROMOTION_ROOT_SHA256 = (
    "786BDC702B040F449F43098C9600F27003407A005EA6B36A0944B52AD3CB9DE6"
)
EXPECTED_REJECTED_COORDINATE_SHA256 = (
    "634B39179A2DCE9749C00AEED238987CCA7EC89BD28A5EB695AB472158DE3E82"
)
EXPECTED_REJECTED_ROOT_SHA256 = (
    "713DD8CA4CB291DAF00A50051D3B32C980FA83B31C5B4A56AC16608C8AAFFC75"
)
EXPECTED_REJECTED_PENDING_ROOT_SHA256 = (
    "EDF6ACF61C1810989DA7ED7CAD6FC52714C959F442FA1DD7A038A8DCC216D57B"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "A61E32F775BD7589B665B9A13F5B7D9968905097F50CBBFAD4041B118E9261FB"
)
EXPECTED_RENEWAL_ROOT_SHA256 = (
    "AFDA486567AFE4883F249664CF3F9AC010B372A6BDD7E1B65A811BBC2DCDC285"
)
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "2C8837F0AE764558A1B9D0E87B83AB9E2A4C259100AC73EC9F8B63930D52AADD"
)
EXPECTED_CANDIDATE_AFFECTED_ROOT_SHA256 = (
    "FA82BC4416848852AC94D26AB3A6FCA1B01A9B18203C4D71B7C6682C4453E03E"
)
EXPECTED_SOURCE_AFFECTED_ROOT_SHA256 = (
    "EAD6CD856477156C41710533536934F2EC647BB50368B548E4A656694B478D34"
)
EXPECTED_ACCEPTED_ASSEMBLY_SHA256: str | None = (
    "9A712F1001D0618BC02B87109AC425084DE9EF3E86ECEEEE05FA191BCB9726F5"
)

EXPECTED_ALREADY_PROMOTED_ROWS = 0
EXPECTED_ALREADY_PROMOTED_COORDINATE_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_CURRENT_A19_LIVE_ROWS = 67
EXPECTED_CURRENT_A19_LIVE_COORDINATE_SHA256 = (
    "798836E8F1B8FCF2826BAC76314C483930D36D2E36300D1161A8F04A24C94F72"
)
EXPECTED_SELECTOR538_PLANNED_OVERLAP_ROWS = 5
EXPECTED_SELECTOR538_PLANNED_OVERLAP_COORDINATE_SHA256 = (
    "22CB2966734BFDBFB50BF239863727ACF174F06FCF214A420334A7E9A0D85CFE"
)
EXPECTED_LIVE_AFTER_SELECTOR538_PLAN_ROWS = 62
EXPECTED_LIVE_AFTER_SELECTOR538_PLAN_COORDINATE_SHA256 = (
    "DAB4DD150A55F58B3229B7ECFE0F091901C7BC5A9F7CCDB5DE78A2866A2A85B0"
)

# Frozen after the first write/check cycle.
EXPECTED_AUDIT_FILE_SHA256: str | None = (
    "5DAD2ACFA8F1FD95D91A2F44BB4C3776AA83063B0DDC717472F65E49D635F97E"
)
EXPECTED_PROMOTION_FILE_SHA256: str | None = (
    "004916E84686EBB232DFCA19CB88CC50CF58A0427A6BC07718460C0D35EF825B"
)
EXPECTED_DECISION_FILE_SHA256: str | None = (
    "C1EE13CA111299841F426A9D463EBFC3EDA7CD590B0588BCD27DA063FD121E09"
)
EXPECTED_EVIDENCE_FILE_SHA256: str | None = (
    "EA258B813447A81EF1F4ADC790048C6C5D8EC96F235265960BEB3EC7EF3CE0BC"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(BASE_CLOSURE_PATH, "pk_selector1096_chunk2_closure_base_v1")
REVIEW = load_module(REVIEW_BUILDER_PATH, "pk_selector1096_chunk2_closure_review_v1")
CORE = BASE.CORE
_CORE_BUILD_ANALYSIS = BASE._CORE_BUILD_ANALYSIS
_CORE_BUILD_AUDIT = BASE._CORE_BUILD_AUDIT
_CORE_BUILD_UPDATED_ROWS = BASE._CORE_BUILD_UPDATED_ROWS
_CORE_BUILD_PROMOTION = BASE._CORE_BUILD_PROMOTION


def patch_contract() -> None:
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
        "EXACT_OVERRIDE_FIELD": EXACT_OVERRIDE_FIELD,
        "SUPERSESSION_FIELD": SUPERSESSION_FIELD,
        "SELECTOR": SELECTOR,
        "TERMINALS": TERMINALS,
    }
    names = (
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
        "EXPECTED_ALREADY_PROMOTED_ROWS",
        "EXPECTED_ALREADY_PROMOTED_COORDINATE_SHA256",
        "EXPECTED_CURRENT_A19_LIVE_ROWS",
        "EXPECTED_CURRENT_A19_LIVE_COORDINATE_SHA256",
        "EXPECTED_SELECTOR538_PLANNED_OVERLAP_ROWS",
        "EXPECTED_SELECTOR538_PLANNED_OVERLAP_COORDINATE_SHA256",
        "EXPECTED_LIVE_AFTER_SELECTOR538_PLAN_ROWS",
        "EXPECTED_LIVE_AFTER_SELECTOR538_PLAN_COORDINATE_SHA256",
        "EXPECTED_AUDIT_FILE_SHA256",
        "EXPECTED_PROMOTION_FILE_SHA256",
        "EXPECTED_DECISION_FILE_SHA256",
        "EXPECTED_EVIDENCE_FILE_SHA256",
    )
    for name in names:
        replacements[name] = globals()[name]
    for module in (BASE, CORE):
        for name, value in replacements.items():
            setattr(module, name, value)


def load_review() -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    CORE.require(
        CORE.sha256_file(PRIVATE_HANDOFF_PATH) == EXPECTED_HANDOFF_SHA256,
        "private selector-1096 chunk-2 handoff drifted",
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
        and result.get("potential_promotion_coordinate_count")
        == EXPECTED_PROMOTION_ROWS
        and result.get("blocked_pending_coordinate_count")
        == EXPECTED_REJECTED_PENDING_ROWS
        and result.get("accepted_current_a19_live_pending_count")
        == EXPECTED_CURRENT_A19_LIVE_ROWS
        and result.get("accepted_live_after_selector538_plan_count")
        == EXPECTED_LIVE_AFTER_SELECTOR538_PLAN_ROWS
        and proof.get("accepted_assembly_branches")
        == EXPECTED_ACCEPTED_ASSEMBLIES
        and proof.get("assembly_branches_recorded") == 399
        and proof.get(
            "all_accepted_current_relative_raw_g1n_nonexpanding"
        )
        is True
        and proof.get("all_accepted_register_branches_proven") is True
        and public.get("steam_write_performed") is False,
        "source-free selector-1096 chunk-2 proposal drifted",
    )
    return handoff, public, world, validated


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
    result["proof"]["rejected_selector1096_chunk2_pending_rows_unchanged"] = (
        result["proof"].pop("rejected_chunk0_pending_rows_unchanged")
    )
    result["proof"]["selector538_evidence_supersession"] = (
        BASE.public_supersession_summary(analysis)
    )
    result["scope"]["chunk_id"] = 2
    return CORE.HONORIFIC.seal_report(result)


patch_contract()
BASE.REVIEW = REVIEW
BASE.load_review = load_review
BASE.build_audit = build_audit
CORE.load_review = load_review
CORE.build_analysis = BASE.build_analysis
CORE.build_audit = build_audit
CORE.build_updated_rows = BASE.build_updated_rows
CORE.build_promotion = BASE.build_promotion

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
assert_source_free_report = CORE.assert_source_free_report
contains_body_key = CORE.contains_body_key
supersession_partition = BASE.supersession_partition
public_supersession_summary = BASE.public_supersession_summary
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
