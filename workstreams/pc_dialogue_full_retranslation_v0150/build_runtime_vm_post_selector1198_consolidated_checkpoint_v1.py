#!/usr/bin/env python3
"""Apply selector-1198 as a targeted immutable ledger delta."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
PK_AUDIT = REPO / "workstreams" / "pk_msggame_runtime_vm_audit_v1"
DIALOGUE_TMP = REPO / "tmp" / WORKSTREAM.name

BASE_BUILDER_PATH = (
    WORKSTREAM / "build_runtime_vm_post_selector628_consolidated_checkpoint_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector628_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector628_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    PK_AUDIT / "build_pk_selector1198_consolidated_closure_v1.py"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector1198_consolidated_closure_decisions.private.v1.jsonl"
)
CLOSURE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector1198_consolidated_closure_evidence.private.v1.json"
)
CLOSURE_COVERAGE_PATH = (
    PK_AUDIT / "public" / "pk_selector1198_consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    PK_AUDIT / "public" / "pk_selector1198_consolidated_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1198_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector1198_consolidated_checkpoint.source_free.v1.json"
)

EXPECTED_BASE_BUILDER_SHA256 = (
    "86BA03A1939362C7183C37DF3103AAE0AFD7140A9CE573A1FBB3990329FA8B0C"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "64F57157C47A72E42CBDBDA59C84AA142519CAAF7D4391983CEFD34362640147"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "D75600A25C086D41190589DA21C8B389ACD9A9BAD561B920F9BB25F5FB9E5B88"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "28267B6928CBDBF3E98FBB8E13A4733947A4EAC6A2BF04812A848C1091F9B186"
)
EXPECTED_CLOSURE_BUILDER_SHA256 = (
    "D34D46DB89CC1ED30DE5F291CEBA9ED73216C2A1F8F035B67B154667EF098035"
)
EXPECTED_CLOSURE_DECISIONS_SHA256 = (
    "933552574FBFC2322CC17DD35ED106BF24326A006EB85F057E4136C720B6E1B4"
)
EXPECTED_CLOSURE_EVIDENCE_SHA256 = (
    "BCFA331FDED65EBCACBCC3906D9454A5FB7307DEE5015F2ABB910FF4EFF8D262"
)
EXPECTED_CLOSURE_COVERAGE_SHA256 = (
    "EDDE1CBEA959714C9F16B88CB23E442CC5529BE31CF3ED70F806D3361DDA7A01"
)
EXPECTED_CLOSURE_PROMOTION_SHA256 = (
    "3F90F0BB36FAAA06162FD805E0BC6DFEF20676F22D395579106964828212067E"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 27
EXPECTED_UNAFFECTED_ROWS = 52_776
EXPECTED_OWNER_ROWS = 27
EXPECTED_PROMOTIONS = 25
EXPECTED_RENEWALS = 2
EXPECTED_OVERRIDES = 6
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 21,
    "translation_override_and_runtime_promotion": 4,
    "translation_override_and_verification_renewal": 2,
}
EXPECTED_OWNER_CHUNK_COUNTS = {0: 8, 1: 19}
EXPECTED_PREDECESSOR_PENDING = 6_489
EXPECTED_FINAL_PENDING = 6_464
EXPECTED_PREDECESSOR_ELIGIBLE = 46_314
EXPECTED_FINAL_ELIGIBLE = 46_339
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 14_194
EXPECTED_FINAL_PK_PROMOTIONS = 14_219
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 29_845
EXPECTED_FINAL_PROMOTED_TOTAL = 29_870
EXPECTED_REVIEWED_SITES = 46
EXPECTED_SOURCE_ONLY_SITES = 0
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "FE9A7E842B974AC8669153DFAF33657EB79EAC55618C4D79F8ECFF9BB770B1BE"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "490D8B91BEABD960A6D9DDAB59CD982243779F011B6EF63FB227AFB171D8979C"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "F908D488BC94E36E6FD0BCC1FA3342744CFC61307404C8B124B9BFD9E1ACCE6B"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "62A0D9D5CC458EA5DA8653C87D6886C86C5C1ABE87FF113142B97705C3631E57"
)
EXPECTED_REVIEWED_SITE_SHA256 = (
    "5D1E5253A7B6CC4683BE71F4A17DDACAB1E6C57715E47859127FA327B888C811"
)
EXPECTED_SOURCE_ONLY_SITE_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "74E30E798B82129565518FA04F35DC73220974CFC6E1E7E61BCEC2D8008671DA"
)
UPDATE_ACTION_FIELD = "selector1198_consolidated_update_action"

EXPECTED_PRIVATE_OUTPUT_SHA256: str | None = (
    "A3B6AE01A30C4EC6EFCE171345EFEB81F7FDB9EDFDCAECD90AA4A78AB3296F4F"
)
EXPECTED_PUBLIC_OUTPUT_SHA256: str | None = (
    "DAD1BCD22AAE11BDD5D10669BC052240FDDAFD634AE5B6A32353BF11CE563B2C"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PREVIOUS = load_module(BASE_BUILDER_PATH, "selector1198_checkpoint_base")
BASE = PREVIOUS.BASE
ORIGINAL_PATCH_PREDECESSOR_ROW = PREVIOUS.ORIGINAL_PATCH_PREDECESSOR_ROW


def configure_base() -> None:
    PREVIOUS.configure_base()
    values = {
        "PREDECESSOR_PRIVATE_PATH": PREDECESSOR_PRIVATE_PATH,
        "PREDECESSOR_PUBLIC_PATH": PREDECESSOR_PUBLIC_PATH,
        "CLOSURE_BUILDER_PATH": CLOSURE_BUILDER_PATH,
        "CLOSURE_DECISIONS_PATH": CLOSURE_DECISIONS_PATH,
        "CLOSURE_EVIDENCE_PATH": CLOSURE_EVIDENCE_PATH,
        "CLOSURE_COVERAGE_PATH": CLOSURE_COVERAGE_PATH,
        "CLOSURE_PROMOTION_PATH": CLOSURE_PROMOTION_PATH,
        "DEFAULT_PRIVATE_OUTPUT": DEFAULT_PRIVATE_OUTPUT,
        "DEFAULT_PUBLIC_OUTPUT": DEFAULT_PUBLIC_OUTPUT,
        "EXPECTED_ROWS": EXPECTED_ROWS,
        "EXPECTED_DECISIONS": EXPECTED_DECISIONS,
        "EXPECTED_UNAFFECTED_ROWS": EXPECTED_UNAFFECTED_ROWS,
        "EXPECTED_PROMOTIONS": EXPECTED_PROMOTIONS,
        "EXPECTED_RENEWALS": EXPECTED_RENEWALS,
        "EXPECTED_OVERRIDES": EXPECTED_OVERRIDES,
        "EXPECTED_ACTION_COUNTS": EXPECTED_ACTION_COUNTS,
        "EXPECTED_OWNER_CHUNK_COUNTS": EXPECTED_OWNER_CHUNK_COUNTS,
        "EXPECTED_PREDECESSOR_PENDING": EXPECTED_PREDECESSOR_PENDING,
        "EXPECTED_FINAL_PENDING": EXPECTED_FINAL_PENDING,
        "EXPECTED_PREDECESSOR_ELIGIBLE": EXPECTED_PREDECESSOR_ELIGIBLE,
        "EXPECTED_FINAL_ELIGIBLE": EXPECTED_FINAL_ELIGIBLE,
        "EXPECTED_PREDECESSOR_PK_PROMOTIONS":
            EXPECTED_PREDECESSOR_PK_PROMOTIONS,
        "EXPECTED_FINAL_PK_PROMOTIONS": EXPECTED_FINAL_PK_PROMOTIONS,
        "EXPECTED_PREDECESSOR_PROMOTED_TOTAL":
            EXPECTED_PREDECESSOR_PROMOTED_TOTAL,
        "EXPECTED_FINAL_PROMOTED_TOTAL": EXPECTED_FINAL_PROMOTED_TOTAL,
        "EXPECTED_PREDECESSOR_PRIVATE_SHA256":
            EXPECTED_PREDECESSOR_PRIVATE_SHA256,
        "EXPECTED_PREDECESSOR_PUBLIC_SHA256":
            EXPECTED_PREDECESSOR_PUBLIC_SHA256,
        "EXPECTED_PREDECESSOR_CANDIDATE_SHA256":
            EXPECTED_PREDECESSOR_CANDIDATE_SHA256,
        "EXPECTED_CLOSURE_BUILDER_SHA256": EXPECTED_CLOSURE_BUILDER_SHA256,
        "EXPECTED_CLOSURE_DECISIONS_SHA256":
            EXPECTED_CLOSURE_DECISIONS_SHA256,
        "EXPECTED_CLOSURE_EVIDENCE_SHA256":
            EXPECTED_CLOSURE_EVIDENCE_SHA256,
        "EXPECTED_CLOSURE_COVERAGE_SHA256":
            EXPECTED_CLOSURE_COVERAGE_SHA256,
        "EXPECTED_CLOSURE_PROMOTION_SHA256":
            EXPECTED_CLOSURE_PROMOTION_SHA256,
        "EXPECTED_DECISION_COORDINATE_SHA256":
            EXPECTED_DECISION_COORDINATE_SHA256,
        "EXPECTED_PROMOTION_COORDINATE_SHA256":
            EXPECTED_PROMOTION_COORDINATE_SHA256,
        "EXPECTED_RENEWAL_COORDINATE_SHA256":
            EXPECTED_RENEWAL_COORDINATE_SHA256,
        "EXPECTED_OVERRIDE_COORDINATE_SHA256":
            EXPECTED_OVERRIDE_COORDINATE_SHA256,
        "EXPECTED_REVIEWED_SITE_SHA256": EXPECTED_REVIEWED_SITE_SHA256,
        "EXPECTED_SOURCE_ONLY_SITE_SHA256":
            EXPECTED_SOURCE_ONLY_SITE_SHA256,
        "EXPECTED_FINAL_CANDIDATE_SHA256": EXPECTED_FINAL_CANDIDATE_SHA256,
        "EXPECTED_PRIVATE_OUTPUT_SHA256": EXPECTED_PRIVATE_OUTPUT_SHA256,
        "EXPECTED_PUBLIC_OUTPUT_SHA256": EXPECTED_PUBLIC_OUTPUT_SHA256,
    }
    for name, value in values.items():
        setattr(BASE, name, value)
    BASE.SCHEMA = (
        "nobu16.kr.pc-dialogue-runtime-vm-selector1198-delta-checkpoint."
        "source-free.v1"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector1198-consolidated-closure-decision.private.v1"
    )
    BASE.METHOD = (
        "post_selector628_selector1198_single_coordinate_union_targeted_ledger_delta"
    )
    BASE.UPDATE_ACTION_FIELD = UPDATE_ACTION_FIELD
    BASE.EXACT_OVERRIDE_FIELD = "selector1198_consolidated_exact_override_evidence"


def validate_closure_reports(
    coverage: Mapping[str, Any],
    promotion: Mapping[str, Any],
) -> None:
    cr = coverage["result"]
    pr = promotion["result"]
    BASE.require(
        coverage.get("status") == promotion.get("status") == "PASS"
        and coverage.get("steam_write_performed") is False
        and promotion.get("steam_write_performed") is False
        and cr.get("decision_rows") == EXPECTED_DECISIONS
        and cr.get("reviewed_sites") == EXPECTED_REVIEWED_SITES
        and cr.get("source_only_sites") == EXPECTED_SOURCE_ONLY_SITES
        and cr.get("source_only_actions") == 0
        and cr.get("predecessor_overlaps") == 0
        and cr.get("predecessor_supersessions") == 0
        and pr.get("decision_rows") == EXPECTED_DECISIONS
        and pr.get("promotions") == EXPECTED_PROMOTIONS
        and pr.get("renewals") == EXPECTED_RENEWALS
        and pr.get("overrides") == EXPECTED_OVERRIDES
        and pr.get("action_counts") == EXPECTED_ACTION_COUNTS
        and pr.get("pending_before") == EXPECTED_PREDECESSOR_PENDING
        and pr.get("pending_after") == EXPECTED_FINAL_PENDING,
        "selector1198 closure report drifted",
    )
    guards = {
        "decision_coordinate_sha256": EXPECTED_DECISION_COORDINATE_SHA256,
        "promotion_coordinate_sha256": EXPECTED_PROMOTION_COORDINATE_SHA256,
        "renewal_coordinate_sha256": EXPECTED_RENEWAL_COORDINATE_SHA256,
        "override_coordinate_sha256": EXPECTED_OVERRIDE_COORDINATE_SHA256,
        "candidate_call_site_sha256": EXPECTED_REVIEWED_SITE_SHA256,
        "source_only_site_sha256": EXPECTED_SOURCE_ONLY_SITE_SHA256,
        "decision_file_sha256": EXPECTED_CLOSURE_DECISIONS_SHA256,
        "private_evidence_sha256": EXPECTED_CLOSURE_EVIDENCE_SHA256,
    }
    BASE.require(
        all(
            coverage["guards"].get(key) == value
            and promotion["guards"].get(key) == value
            for key, value in guards.items()
        ),
        "selector1198 closure guard drifted",
    )
    for report in (coverage, promotion):
        BASE.require(
            report["inputs"].get("official_ledger_sha256")
            == EXPECTED_PREDECESSOR_PRIVATE_SHA256
            and report["inputs"].get("official_public_checkpoint_sha256")
            == EXPECTED_PREDECESSOR_PUBLIC_SHA256
            and report["candidate"].get("official_predecessor_sha256")
            == EXPECTED_PREDECESSOR_CANDIDATE_SHA256
            and report["candidate"].get("reviewed_sha256")
            == EXPECTED_FINAL_CANDIDATE_SHA256
            and report["candidate"].get("reverse_overlay_sha256")
            == EXPECTED_PREDECESSOR_CANDIDATE_SHA256,
            "selector1198 closure lineage drifted",
        )


def patch_predecessor_row(
    predecessor: dict[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    changed = ORIGINAL_PATCH_PREDECESSOR_ROW(predecessor, decision)
    verification = changed["runtime_vm_verification"]
    verification["schema"] = (
        "nobu16.kr.pk-selector1198-consolidated-row-verification.v1"
    )
    verification["method"] = "reversed_vm_pk_selector1198_consolidated_closure"
    return changed


def build_public_report(
    private_sha256: str,
    stream_result: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema": BASE.SCHEMA,
        "method": BASE.METHOD,
        "release_target": "0.15.0",
        "inputs": {
            "predecessor_private_sha256": EXPECTED_PREDECESSOR_PRIVATE_SHA256,
            "predecessor_public_sha256": EXPECTED_PREDECESSOR_PUBLIC_SHA256,
            "predecessor_candidate_sha256": EXPECTED_PREDECESSOR_CANDIDATE_SHA256,
            "closure_builder_sha256": EXPECTED_CLOSURE_BUILDER_SHA256,
            "closure_decisions_sha256": EXPECTED_CLOSURE_DECISIONS_SHA256,
            "closure_evidence_sha256": EXPECTED_CLOSURE_EVIDENCE_SHA256,
            "closure_coverage_sha256": EXPECTED_CLOSURE_COVERAGE_SHA256,
            "closure_promotion_sha256": EXPECTED_CLOSURE_PROMOTION_SHA256,
        },
        "selector1198_consolidated": {
            "owner_decision_row_count": EXPECTED_OWNER_ROWS,
            "updated_coordinate_count": EXPECTED_DECISIONS,
            "promotion_count": EXPECTED_PROMOTIONS,
            "verification_renewal_count": EXPECTED_RENEWALS,
            "semantic_override_count": EXPECTED_OVERRIDES,
            "action_counts": EXPECTED_ACTION_COUNTS,
            "decision_coordinate_sha256": EXPECTED_DECISION_COORDINATE_SHA256,
            "promotion_coordinate_sha256": EXPECTED_PROMOTION_COORDINATE_SHA256,
            "renewal_coordinate_sha256": EXPECTED_RENEWAL_COORDINATE_SHA256,
            "override_coordinate_sha256": EXPECTED_OVERRIDE_COORDINATE_SHA256,
            "reviewed_site_count": EXPECTED_REVIEWED_SITES,
            "reviewed_site_sha256": EXPECTED_REVIEWED_SITE_SHA256,
            "source_only_repair_site_count": 0,
            "source_only_site_sha256": EXPECTED_SOURCE_ONLY_SITE_SHA256,
            "source_only_action_count": 0,
            "predecessor_overlap_count": 0,
            "predecessor_supersession_count": 0,
            "predecessor_candidate_sha256":
                EXPECTED_PREDECESSOR_CANDIDATE_SHA256,
            "final_candidate_sha256": EXPECTED_FINAL_CANDIDATE_SHA256,
            "reverse_overlay_sha256": EXPECTED_PREDECESSOR_CANDIDATE_SHA256,
            "single_coordinate_union_used": True,
            "owner_coordinate_sets_disjoint": True,
            "sequential_chunk_overlays_used": False,
            "steam_write_performed": False,
        },
        "result": {
            "semantic_review_approved": EXPECTED_ROWS,
            "runtime_review_pending": EXPECTED_FINAL_PENDING,
            "fully_candidate_eligible": EXPECTED_FINAL_ELIGIBLE,
            "promoted_total": EXPECTED_FINAL_PROMOTED_TOTAL,
            "pk_msggame_promotion_count": EXPECTED_FINAL_PK_PROMOTIONS,
            "private_integrated_decision_sha256": private_sha256,
            **stream_result,
        },
        "validation": {
            "full_integration_engine_invoked": False,
            "targeted_affected_rows_rechecked": EXPECTED_DECISIONS,
            "unaffected_rows_byte_copied": EXPECTED_UNAFFECTED_ROWS,
            "candidate_call_sites_rechecked": EXPECTED_REVIEWED_SITES,
            "source_only_sites_rechecked": 0,
            "event_dialogue_912px_rule_applied": False,
            "current_relative_raw_g1n_nonexpansion_used": True,
            "confirmed_non_display_rows_preserved": True,
            "steam_archives_read_only": True,
        },
        "distribution_policy": {
            "private_integrated_decision_stays_below_tmp": True,
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "tracked_report_contains_exact_coordinates": False,
        },
        "status": "PASS",
        "steam_write_performed": False,
    }


def load_closure_decisions() -> dict[str, dict[str, Any]]:
    configure_base()
    return BASE.load_closure_decisions()


def main(argv: Sequence[str] | None = None) -> int:
    BASE.require(
        BASE.sha256_file(BASE_BUILDER_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "selector628 targeted checkpoint base drifted",
    )
    configure_base()
    BASE.validate_closure_reports = validate_closure_reports
    BASE.patch_predecessor_row = patch_predecessor_row
    BASE.build_public_report = build_public_report
    return BASE.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
