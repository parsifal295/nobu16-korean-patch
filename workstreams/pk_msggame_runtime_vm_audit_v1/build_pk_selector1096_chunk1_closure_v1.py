#!/usr/bin/env python3
"""Build the independent selector-1096 chunk-1 runtime closure layer."""

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
BASE_CLOSURE_PATH = WORKSTREAM / "build_pk_selector1096_chunk0_closure_v1.py"
REVIEW_BUILDER_PATH = WORKSTREAM / "build_pk_selector1096_chunk1_review_v1.py"
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
    DIALOGUE_TMP / "family1096_chunk1_analysis.private.v1.json"
)
REVIEW_PUBLIC_PATH = (
    WORKSTREAM
    / "public"
    / "pk_selector1096_chunk1_review_proposal.v1.json"
)

DEFAULT_AUDIT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector1096_chunk1_closure_coverage.v1.json"
)
DEFAULT_PROMOTION_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector1096_chunk1_closure_promotion.v1.json"
)
DEFAULT_DECISION_OUTPUT = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector1096_chunk1_closure_decisions.private.v1.jsonl"
)
DEFAULT_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_selector1096_chunk1_closure_evidence.private.v1.jsonl"
)

AUDIT_SCHEMA = "nobu16.kr.pk-selector1096-chunk1-closure-coverage.v1"
PROMOTION_SCHEMA = "nobu16.kr.pk-selector1096-chunk1-closure-promotion.v1"
EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector1096-chunk1-closure-evidence-row.v1"
)
OVERRIDE_SCHEMA = "nobu16.kr.pk-selector1096-chunk1-exact-override.v1"
METHOD = "reversed_vm_pk_selector1096_chunk1_independent_closure"
UPDATE_ACTION_FIELD = "selector1096_chunk1_update_action"
EXACT_OVERRIDE_FIELD = "selector1096_chunk1_exact_override_evidence"
SUPERSESSION_FIELD = (
    "selector1096_chunk1_selector538_evidence_supersession"
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
    "7B3BC7DA3AEBC2F49FBE20C4777D2307BC3D0C3C86E0EC30189174284D7C719D"
)
EXPECTED_REVIEW_PUBLIC_SHA256 = (
    "7421A90EB3A33D465D151B0EC0039A4CB303F81B5F001D2408D1FB07C2137AF8"
)
EXPECTED_PREDECESSOR_ROWS = 52_803
EXPECTED_PREDECESSOR_PENDING = 8_213
EXPECTED_PENDING_AFTER = 8_135
EXPECTED_BASELINE_CANDIDATE_SHA256 = (
    "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E"
)
EXPECTED_CANDIDATE_SHA256 = (
    "4EF2FF6ACA78559F6B5B0D07E32E9FAB674DC113C754E9EE03BD43683A1DDAA7"
)
EXPECTED_REWRITE_ROWS = 46
EXPECTED_KEEP_ROWS = 4
EXPECTED_REJECTED_SITES = 9
EXPECTED_ACCEPTED_SITES = 50
EXPECTED_ACCEPTED_ASSEMBLIES = 350
EXPECTED_PROMOTION_ROWS = 78
EXPECTED_PROMOTION_ROOTS = 36
EXPECTED_REJECTED_PENDING_ROWS = 13
EXPECTED_REJECTED_ROOTS = 8
EXPECTED_REJECTED_PENDING_ROOTS = 5
EXPECTED_RENEWAL_ROWS = 203
EXPECTED_RENEWAL_ROOTS = 98
EXPECTED_DECISION_ROWS = 281
EXPECTED_CANDIDATE_AFFECTED_ROOTS = 239
EXPECTED_SOURCE_AFFECTED_ROOTS = 258
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 58,
    "translation_override_and_runtime_promotion": 20,
    "translation_override_and_verification_renewal": 26,
    "verification_renewal": 177,
}

EXPECTED_REWRITE_COORDINATE_SHA256 = (
    "FDC65FE67D353C1E20ADDF209743785C691EC9D8DE604A1AC69440D1A675C39B"
)
EXPECTED_REWRITE_MAP_SHA256 = (
    "47533F50E56A9CA0159FA011A549B1630DA9E0A104D0509D5CA7D2ED5D8F6E4D"
)
EXPECTED_ACCEPTED_SITE_SHA256 = (
    "0E7C9F63E06188FE48636A5EC44B3BAA6D980A6D3AB07DFF14903D9C23C1B313"
)
EXPECTED_REJECTED_SITE_SHA256 = (
    "90A3D51F9F1BEE4DB773C78E6B4BD96276973B911B4CD28D2940849FD0159DAE"
)
EXPECTED_ACCEPTED_ROOT_SHA256 = (
    "66C2B65A18E292F4C36910CB26D618835EBE16859986E57136046020545B870F"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "60F19B80260ABEF101EB0FD367B4DD75C7779AB3525D4DAD692D6425EBAB786E"
)
EXPECTED_PROMOTION_ROOT_SHA256 = (
    "ABAB8823E76CD1893DCD47F94B27E23712F42E7492B08B3A6327E784E86383C9"
)
EXPECTED_REJECTED_COORDINATE_SHA256 = (
    "194BD74F8E0029211054B3BA18D39F859B1F5D250CB64B977277804A55C72844"
)
EXPECTED_REJECTED_ROOT_SHA256 = (
    "002EFEFA2E8A6D292ECF193F8DB1B544041025984A1AB808B395F666B0AC6029"
)
EXPECTED_REJECTED_PENDING_ROOT_SHA256 = (
    "B20E20843D52BE4F80219712D09222E6F608371AD874893E645AF420EEF456A7"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "A61E32F775BD7589B665B9A13F5B7D9968905097F50CBBFAD4041B118E9261FB"
)
EXPECTED_RENEWAL_ROOT_SHA256 = (
    "AFDA486567AFE4883F249664CF3F9AC010B372A6BDD7E1B65A811BBC2DCDC285"
)
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "564CE27E20367454F7D0912B19E6ADAF8742E8AF676361A0D04682A6440D2FF2"
)
EXPECTED_CANDIDATE_AFFECTED_ROOT_SHA256 = (
    "FA82BC4416848852AC94D26AB3A6FCA1B01A9B18203C4D71B7C6682C4453E03E"
)
EXPECTED_SOURCE_AFFECTED_ROOT_SHA256 = (
    "EAD6CD856477156C41710533536934F2EC647BB50368B548E4A656694B478D34"
)
EXPECTED_ACCEPTED_ASSEMBLY_SHA256: str | None = (
    "674E53E70BF9421123371CCC4B410384F82DEA964AD81CE93109CB6D7C176153"
)

EXPECTED_ALREADY_PROMOTED_ROWS = 0
EXPECTED_ALREADY_PROMOTED_COORDINATE_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_CURRENT_A19_LIVE_ROWS = 78
EXPECTED_CURRENT_A19_LIVE_COORDINATE_SHA256 = (
    "60F19B80260ABEF101EB0FD367B4DD75C7779AB3525D4DAD692D6425EBAB786E"
)
EXPECTED_SELECTOR538_PLANNED_OVERLAP_ROWS = 6
EXPECTED_SELECTOR538_PLANNED_OVERLAP_COORDINATE_SHA256 = (
    "A2A4673E06F66E63811D0E23FFB382BB732C673C745BD7D43B65448DD0BE5C8E"
)
EXPECTED_LIVE_AFTER_SELECTOR538_PLAN_ROWS = 72
EXPECTED_LIVE_AFTER_SELECTOR538_PLAN_COORDINATE_SHA256 = (
    "F5E715D108BF66D16448B77A489B5792CFB7D4C99AB23B5C77223EAB2C8DAE73"
)

EXPECTED_AUDIT_FILE_SHA256: str | None = (
    "D82432709E05D4D7102180416D7A9FEEA26ADF2AC95567753F915923144DF10D"
)
EXPECTED_PROMOTION_FILE_SHA256: str | None = (
    "CCFC0251AF9044E9F4B63C3E2237463FDE1430527C14A780F760D7FF93F61275"
)
EXPECTED_DECISION_FILE_SHA256: str | None = (
    "03716EFC6954E9FE4AB21E1461F988BBBA6B127FCA7FE62E4DD34586A810456C"
)
EXPECTED_EVIDENCE_FILE_SHA256: str | None = (
    "ABA8D291C02531E551EAE109ED0AB989F254E18E22FD3E6590D53566A958E668"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(BASE_CLOSURE_PATH, "pk_selector1096_chunk1_closure_base_v1")
REVIEW = load_module(REVIEW_BUILDER_PATH, "pk_selector1096_chunk1_closure_review_v1")
CORE = BASE.CORE

_CORE_BUILD_ANALYSIS = BASE._CORE_BUILD_ANALYSIS
_CORE_BUILD_AUDIT = BASE._CORE_BUILD_AUDIT
_CORE_BUILD_UPDATED_ROWS = BASE._CORE_BUILD_UPDATED_ROWS
_CORE_BUILD_PROMOTION = BASE._CORE_BUILD_PROMOTION


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
        "private selector-1096 chunk-1 handoff drifted",
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
        and proof.get("assembly_branches_recorded") == 413
        and proof.get(
            "all_accepted_current_relative_raw_g1n_nonexpanding"
        )
        is True
        and proof.get("all_accepted_register_branches_proven") is True
        and public.get("steam_write_performed") is False,
        "source-free selector-1096 chunk-1 proposal drifted",
    )
    return handoff, public, world, validated


def build_analysis(
    *,
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    world: Mapping[str, Any],
    handoff: Mapping[str, Any],
    validated: Mapping[str, Any],
) -> dict[str, Any]:
    return _CORE_BUILD_ANALYSIS(
        predecessor_rows=predecessor_rows,
        world=world,
        handoff=handoff,
        validated=validated,
    )


def supersession_partition(
    analysis: Mapping[str, Any],
) -> dict[str, set[str]]:
    assignment, _chunk = REVIEW.load_assignment()
    graph = assignment["graph_evidence"]
    potential = set(analysis["promotion_coordinates"])
    already = potential & set(graph["already_promoted_coordinates"])
    current_live = potential & set(graph["current_live_pending_coordinates"])
    planned_overlap = potential & set(
        graph["selector538_planned_overlap_coordinates"]
    )
    live_after_plan = potential & set(
        graph["live_after_selector538_plan_coordinates"]
    )
    CORE.require(
        len(already) == EXPECTED_ALREADY_PROMOTED_ROWS
        and CORE.coordinate_digest(already)
        == EXPECTED_ALREADY_PROMOTED_COORDINATE_SHA256
        and len(current_live) == EXPECTED_CURRENT_A19_LIVE_ROWS
        and CORE.coordinate_digest(current_live)
        == EXPECTED_CURRENT_A19_LIVE_COORDINATE_SHA256
        and len(planned_overlap)
        == EXPECTED_SELECTOR538_PLANNED_OVERLAP_ROWS
        and CORE.coordinate_digest(planned_overlap)
        == EXPECTED_SELECTOR538_PLANNED_OVERLAP_COORDINATE_SHA256
        and len(live_after_plan)
        == EXPECTED_LIVE_AFTER_SELECTOR538_PLAN_ROWS
        and CORE.coordinate_digest(live_after_plan)
        == EXPECTED_LIVE_AFTER_SELECTOR538_PLAN_COORDINATE_SHA256
        and not already
        and current_live == potential
        and not planned_overlap & live_after_plan
        and planned_overlap | live_after_plan == potential,
        "selector-1096 chunk-1 selector538 supersession partition drifted",
    )
    return {
        "already_promoted": already,
        "current_a19_live": current_live,
        "live_after_selector538_plan": live_after_plan,
        "potential": potential,
        "selector538_planned_overlap": planned_overlap,
    }


def public_supersession_summary(
    analysis: Mapping[str, Any],
) -> dict[str, Any]:
    supersession_partition(analysis)
    return {
        "already_promoted_rows": EXPECTED_ALREADY_PROMOTED_ROWS,
        "already_promoted_sha256":
            EXPECTED_ALREADY_PROMOTED_COORDINATE_SHA256,
        "bf7b_potential_promotion_rows": EXPECTED_PROMOTION_ROWS,
        "bf7b_potential_promotion_sha256":
            EXPECTED_PROMOTION_COORDINATE_SHA256,
        "current_a19_live_pending_rows": EXPECTED_CURRENT_A19_LIVE_ROWS,
        "current_a19_live_pending_sha256":
            EXPECTED_CURRENT_A19_LIVE_COORDINATE_SHA256,
        "live_after_selector538_plan_rows":
            EXPECTED_LIVE_AFTER_SELECTOR538_PLAN_ROWS,
        "live_after_selector538_plan_sha256":
            EXPECTED_LIVE_AFTER_SELECTOR538_PLAN_COORDINATE_SHA256,
        "partition_complete": True,
        "selector538_planned_overlap_rows":
            EXPECTED_SELECTOR538_PLANNED_OVERLAP_ROWS,
        "selector538_planned_overlap_sha256":
            EXPECTED_SELECTOR538_PLANNED_OVERLAP_COORDINATE_SHA256,
    }


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
    result["proof"]["rejected_selector1096_chunk1_pending_rows_unchanged"] = (
        result["proof"].pop("rejected_chunk0_pending_rows_unchanged")
    )
    result["proof"]["selector538_evidence_supersession"] = (
        public_supersession_summary(analysis)
    )
    result["scope"]["chunk_id"] = 1
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
    partition = supersession_partition(analysis)
    updated_by_coordinate = {
        str(row["coordinate"]): row for row in updated_rows
    }
    evidence_by_coordinate = {
        str(row["coordinate"]): row for row in evidence_rows
    }
    for row in updated_rows:
        if "selector538_chunk0_exact_override_evidence" in row:
            row[EXACT_OVERRIDE_FIELD] = row.pop(
                "selector538_chunk0_exact_override_evidence"
            )
    for coordinate in partition["potential"]:
        metadata = {
            "already_promoted_in_current_a19": False,
            "bf7b_potential_promotion": True,
            "current_a19_live_pending": True,
            "live_after_selector538_plan":
                coordinate in partition["live_after_selector538_plan"],
            "selector538_evidence_superseded":
                coordinate in partition["selector538_planned_overlap"],
            "selector538_planned_overlap":
                coordinate in partition["selector538_planned_overlap"],
        }
        updated_by_coordinate[coordinate][SUPERSESSION_FIELD] = metadata
        evidence_by_coordinate[coordinate][SUPERSESSION_FIELD] = metadata
    return updated_rows, evidence_rows


def build_promotion(
    *,
    audit: Mapping[str, Any],
    audit_file_sha256: str,
    decision_content: str,
    evidence_content: str,
    evidence_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    report = _CORE_BUILD_PROMOTION(
        audit=audit,
        audit_file_sha256=audit_file_sha256,
        decision_content=decision_content,
        evidence_content=evidence_content,
        evidence_rows=evidence_rows,
    )
    result = copy.deepcopy(report)
    result["evidence"]["selector538_evidence_supersession"] = (
        audit["proof"]["selector538_evidence_supersession"]
    )
    return CORE.HONORIFIC.seal_report(result)


patch_core_contract()
CORE.load_review = load_review
CORE.build_analysis = build_analysis
CORE.build_audit = build_audit
CORE.build_updated_rows = build_updated_rows
CORE.build_promotion = build_promotion

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
