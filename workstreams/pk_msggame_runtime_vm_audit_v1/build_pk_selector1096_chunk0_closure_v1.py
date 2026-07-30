#!/usr/bin/env python3
"""Build the independent selector-1096 chunk-0 runtime closure layer.

The frozen BF7B post-selector-1066 checkpoint is the predecessor. Dialogue
bodies and exact overrides remain private below ``tmp``; only source-free
coverage and promotion reports are tracked. The BF7B potential promotion set
is kept distinct from the current A19 / selector-538 live set so overlapping
evidence can be superseded without double-counting release progress.
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
REVIEW_BUILDER_PATH = WORKSTREAM / "build_pk_selector1096_chunk0_review_v1.py"
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
    DIALOGUE_TMP / "family1096_chunk0_analysis.private.v1.json"
)
REVIEW_PUBLIC_PATH = (
    WORKSTREAM
    / "public"
    / "pk_selector1096_chunk0_review_proposal.v1.json"
)

DEFAULT_AUDIT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector1096_chunk0_closure_coverage.v1.json"
)
DEFAULT_PROMOTION_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_selector1096_chunk0_closure_promotion.v1.json"
)
DEFAULT_DECISION_OUTPUT = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector1096_chunk0_closure_decisions.private.v1.jsonl"
)
DEFAULT_EVIDENCE_OUTPUT = (
    DIALOGUE_TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_selector1096_chunk0_closure_evidence.private.v1.jsonl"
)

AUDIT_SCHEMA = "nobu16.kr.pk-selector1096-chunk0-closure-coverage.v1"
PROMOTION_SCHEMA = "nobu16.kr.pk-selector1096-chunk0-closure-promotion.v1"
EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-selector1096-chunk0-closure-evidence-row.v1"
)
OVERRIDE_SCHEMA = "nobu16.kr.pk-selector1096-chunk0-exact-override.v1"
METHOD = "reversed_vm_pk_selector1096_chunk0_independent_closure"
UPDATE_ACTION_FIELD = "selector1096_chunk0_update_action"
EXACT_OVERRIDE_FIELD = "selector1096_chunk0_exact_override_evidence"
SUPERSESSION_FIELD = (
    "selector1096_chunk0_selector538_evidence_supersession"
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
    "F2731FD912F0BEF3CCB69CA8A0DD231DE6391AB1A47DE36027B44B49B3840240"
)
EXPECTED_REVIEW_PUBLIC_SHA256 = (
    "5214EEDAF9060F2BC2D075438226B47A2DEE92BFE30004256A24887D9994416B"
)
EXPECTED_PREDECESSOR_ROWS = 52_803
EXPECTED_PREDECESSOR_PENDING = 8_213
EXPECTED_PENDING_AFTER = 8_136
EXPECTED_BASELINE_CANDIDATE_SHA256 = (
    "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E"
)
EXPECTED_CANDIDATE_SHA256 = (
    "A63E1996DDB0DC46EB16F9AD82F1870FEB6215333D3E5CCCBACD33FB99EC7A74"
)
EXPECTED_REWRITE_ROWS = 34
EXPECTED_KEEP_ROWS = 0
EXPECTED_REJECTED_SITES = 22
EXPECTED_ACCEPTED_SITES = 34
EXPECTED_ACCEPTED_ASSEMBLIES = 238
EXPECTED_PROMOTION_ROWS = 77
EXPECTED_PROMOTION_ROOTS = 28
EXPECTED_REJECTED_PENDING_ROWS = 16
EXPECTED_REJECTED_ROOTS = 22
EXPECTED_REJECTED_PENDING_ROOTS = 7
EXPECTED_RENEWAL_ROWS = 203
EXPECTED_RENEWAL_ROOTS = 98
EXPECTED_DECISION_ROWS = 280
EXPECTED_CANDIDATE_AFFECTED_ROOTS = 239
EXPECTED_SOURCE_AFFECTED_ROOTS = 258
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 55,
    "translation_override_and_runtime_promotion": 22,
    "translation_override_and_verification_renewal": 12,
    "verification_renewal": 191,
}

EXPECTED_REWRITE_COORDINATE_SHA256 = (
    "56C2E28FEC4A6E0533FBC5A9CEA6CE5FEA5CAD168C1912ADBE59F217BE54C5C0"
)
EXPECTED_REWRITE_MAP_SHA256 = (
    "BEC346CBAF343CE512295815A5AD7FCE02297B45A17CD48F133F2878E9FE904E"
)
EXPECTED_ACCEPTED_SITE_SHA256 = (
    "CA45F8E499B54C5F5FE6284D502DA9249C5AB5803325FFEE1910A566DD41C1FC"
)
EXPECTED_REJECTED_SITE_SHA256 = (
    "DC14B986516F7E3BA0AFABAA5CA13800567D5F7C832D330886AB434273B3D1BE"
)
EXPECTED_ACCEPTED_ROOT_SHA256 = (
    "03A1496709BBA31AA0D37EEC373535DC2EF4F681352F51A5D5D3720BBADDA12A"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "BF344D246667752E5B4698E7EE64D723F2CFE13244CA514A24F390ADBDB7C97E"
)
EXPECTED_PROMOTION_ROOT_SHA256 = (
    "CF87B06DECB58991D3954560A702931C9BBB1FD648DACE0EE48707E085CD3532"
)
EXPECTED_REJECTED_COORDINATE_SHA256 = (
    "4CAFE770ED2C56C8F42CFBE90B0F7A2B8E21C6ED77B745EDDE1AB8F8DBBF6251"
)
EXPECTED_REJECTED_ROOT_SHA256 = (
    "5844A9398F904D3C36EEECDA82D6AFA9B0BD90610E4E4BE9184D5D2D50DCFAE2"
)
EXPECTED_REJECTED_PENDING_ROOT_SHA256 = (
    "6C6E39BF88F1D70D7CA8A51268059AABE1934043A3A5B34581A069895021178B"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "A61E32F775BD7589B665B9A13F5B7D9968905097F50CBBFAD4041B118E9261FB"
)
EXPECTED_RENEWAL_ROOT_SHA256 = (
    "AFDA486567AFE4883F249664CF3F9AC010B372A6BDD7E1B65A811BBC2DCDC285"
)
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "635F054B0A7BB103F1885288FB5B90FECF1A67D2AC67AA642CCB0DEB4F9F4629"
)
EXPECTED_CANDIDATE_AFFECTED_ROOT_SHA256 = (
    "FA82BC4416848852AC94D26AB3A6FCA1B01A9B18203C4D71B7C6682C4453E03E"
)
EXPECTED_SOURCE_AFFECTED_ROOT_SHA256 = (
    "EAD6CD856477156C41710533536934F2EC647BB50368B548E4A656694B478D34"
)
EXPECTED_ACCEPTED_ASSEMBLY_SHA256 = (
    "EF87AEF4AE940C7B18E6A23071C10943B98299745EBE35A6A510E10B5E9B0995"
)

EXPECTED_ALREADY_PROMOTED_ROWS = 5
EXPECTED_ALREADY_PROMOTED_COORDINATE_SHA256 = (
    "7C53C00911001CCC4C81EA047166B468BF1404255ABD4407F04EB763548537DE"
)
EXPECTED_CURRENT_A19_LIVE_ROWS = 72
EXPECTED_CURRENT_A19_LIVE_COORDINATE_SHA256 = (
    "53D099EF4BAC63E65EFE5C6E48ED8C700D2B05598D0867BC9E84CA3E6973BC32"
)
EXPECTED_SELECTOR538_PLANNED_OVERLAP_ROWS = 5
EXPECTED_SELECTOR538_PLANNED_OVERLAP_COORDINATE_SHA256 = (
    "7C53C00911001CCC4C81EA047166B468BF1404255ABD4407F04EB763548537DE"
)
EXPECTED_LIVE_AFTER_SELECTOR538_PLAN_ROWS = 72
EXPECTED_LIVE_AFTER_SELECTOR538_PLAN_COORDINATE_SHA256 = (
    "53D099EF4BAC63E65EFE5C6E48ED8C700D2B05598D0867BC9E84CA3E6973BC32"
)

# Frozen after independently reproducible outputs are generated.
EXPECTED_AUDIT_FILE_SHA256: str | None = (
    "1E2497E1C0127C9C31D2FFBA9541FCF46FEEAF7D85C8500A7A4C3CBB03A52177"
)
EXPECTED_PROMOTION_FILE_SHA256: str | None = (
    "067D09F16F170F9A34F6889846D60C754ED4AF5785D7667E3AA15073CB2131CE"
)
EXPECTED_DECISION_FILE_SHA256: str | None = (
    "C9120BF2F5151CD2913CB60FE20557745E39DC15D058493E60C3BD95FF963067"
)
EXPECTED_EVIDENCE_FILE_SHA256: str | None = (
    "CA3EA97054424CBD8A3FBA544283EC2947BFFCD2210CFFA4014B91874E46AF19"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(BASE_CLOSURE_PATH, "pk_selector1096_chunk0_closure_base_v1")
REVIEW = load_module(REVIEW_BUILDER_PATH, "pk_selector1096_chunk0_closure_review_v1")
CORE = BASE.BASE

_CORE_BUILD_ANALYSIS = BASE._BASE_BUILD_ANALYSIS
_CORE_BUILD_AUDIT = BASE._BASE_BUILD_AUDIT
_CORE_BUILD_UPDATED_ROWS = BASE._BASE_BUILD_UPDATED_ROWS
_CORE_BUILD_PROMOTION = CORE.build_promotion


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
        "private selector-1096 chunk-0 handoff drifted",
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
        and proof.get("assembly_branches_recorded") == 392
        and proof.get(
            "all_accepted_current_relative_raw_g1n_nonexpanding"
        )
        is True
        and proof.get("all_accepted_register_branches_proven") is True
        and public.get("steam_write_performed") is False,
        "source-free selector-1096 chunk-0 proposal drifted",
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
        len(potential) == EXPECTED_PROMOTION_ROWS
        and CORE.coordinate_digest(potential)
        == EXPECTED_PROMOTION_COORDINATE_SHA256
        and len(already) == EXPECTED_ALREADY_PROMOTED_ROWS
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
        and already == planned_overlap
        and current_live == live_after_plan
        and not already & current_live
        and already | current_live == potential,
        "selector-538 evidence supersession partition drifted",
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
        "already_promoted_equals_selector538_planned_overlap": True,
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
    result["proof"]["rejected_selector1096_chunk0_pending_rows_unchanged"] = (
        result["proof"].pop("rejected_chunk0_pending_rows_unchanged")
    )
    result["proof"]["selector538_evidence_supersession"] = (
        public_supersession_summary(analysis)
    )
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
            "already_promoted_in_current_a19":
                coordinate in partition["already_promoted"],
            "bf7b_potential_promotion": True,
            "current_a19_live_pending":
                coordinate in partition["current_a19_live"],
            "live_after_selector538_plan":
                coordinate in partition["live_after_selector538_plan"],
            "selector538_evidence_superseded":
                coordinate in partition["already_promoted"],
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
