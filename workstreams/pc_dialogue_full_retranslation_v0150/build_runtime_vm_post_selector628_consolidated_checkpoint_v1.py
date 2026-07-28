#!/usr/bin/env python3
"""Apply selector-628 as a targeted immutable ledger delta."""

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
    WORKSTREAM / "build_runtime_vm_post_selector514_consolidated_checkpoint_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector514_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector514_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    PK_AUDIT / "build_pk_selector628_consolidated_closure_v1.py"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector628_consolidated_closure_decisions.private.v1.jsonl"
)
CLOSURE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector628_consolidated_closure_evidence.private.v1.json"
)
CLOSURE_COVERAGE_PATH = (
    PK_AUDIT / "public" / "pk_selector628_consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    PK_AUDIT / "public" / "pk_selector628_consolidated_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector628_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector628_consolidated_checkpoint.source_free.v1.json"
)

EXPECTED_BASE_BUILDER_SHA256 = (
    "6E71DF57BD30B9C9372535438C25AB10A8A805FF54BCB476DBDBBB3CB34B3682"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "FCAB3A5CACEEAE4C610BD284D8C0631E65DA14562DB7B78A66655554EED07A79"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "49BB13AF414DA7A751F7B9CA9830386A3832FF99411B4FC39DC96F94FE649100"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "623C6EE2BDC25B13680C353C97847C3AC646C4B2B222A51F0F242B7A1CC2E093"
)
EXPECTED_CLOSURE_BUILDER_SHA256 = (
    "FF00EDACCAB0A65281CE3A7F3182518E87ED3060D54E77F7089FC22B841D9523"
)
EXPECTED_CLOSURE_DECISIONS_SHA256 = (
    "009C9D4B7DCE6CE0E7F07D21F827FB4633DF3C01A3BA6D097AC19F04E0CBE2C4"
)
EXPECTED_CLOSURE_EVIDENCE_SHA256 = (
    "F99DC2F8AA28D3BF12FBB01F8B876B12F0E70598B6543E1E39E4B16F5D9AF175"
)
EXPECTED_CLOSURE_COVERAGE_SHA256 = (
    "19F20B71648A392E239930E36311C303C4F48DDA526329A96875CEC3EB0C5BAC"
)
EXPECTED_CLOSURE_PROMOTION_SHA256 = (
    "C989EF03AAEB433B3D1484B439593EE5C9BC6A61BED789C9977A87AB7FD7CEEB"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 100
EXPECTED_UNAFFECTED_ROWS = 52_703
EXPECTED_OWNER_ROWS = 100
EXPECTED_PROMOTIONS = 58
EXPECTED_RENEWALS = 42
EXPECTED_OVERRIDES = 60
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 40,
    "translation_override_and_runtime_promotion": 18,
    "translation_override_and_verification_renewal": 42,
}
EXPECTED_OWNER_CHUNK_COUNTS = {0: 30, 1: 70}
EXPECTED_PREDECESSOR_PENDING = 6_547
EXPECTED_FINAL_PENDING = 6_489
EXPECTED_PREDECESSOR_ELIGIBLE = 46_256
EXPECTED_FINAL_ELIGIBLE = 46_314
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 14_136
EXPECTED_FINAL_PK_PROMOTIONS = 14_194
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 29_787
EXPECTED_FINAL_PROMOTED_TOTAL = 29_845
EXPECTED_REVIEWED_SITES = 145
EXPECTED_SOURCE_ONLY_SITES = 21
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "E59F2DCE04734EED5732D6CFD475AF379589EAFB8FF6484B3BD0A387F62B6ACE"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "828A08D4E2E26B45BF598137C9DA16B88B240609AE33B5E180D49EE81DF1E62C"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "C0276E37E4AABAE781766BDB612218D0AF147F0DDC5FE196B3A25FF6C97723E0"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "1018F3E00D32CCA5A7A53D68BE2B669C0CE2CF03769D39358B2A07B433E48E6C"
)
EXPECTED_REVIEWED_SITE_SHA256 = (
    "8ACBBCAE255F2F4C1BAD8AC57D23E344EF533A93C6F0523FFE669907DD596D57"
)
EXPECTED_SOURCE_ONLY_SITE_SHA256 = (
    "23C63D343F24382696B596DD38C08FD78D4DB287F15714E520B4E60E5F09990C"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "28267B6928CBDBF3E98FBB8E13A4733947A4EAC6A2BF04812A848C1091F9B186"
)
UPDATE_ACTION_FIELD = "selector628_consolidated_update_action"

EXPECTED_PRIVATE_OUTPUT_SHA256: str | None = (
    "64F57157C47A72E42CBDBDA59C84AA142519CAAF7D4391983CEFD34362640147"
)
EXPECTED_PUBLIC_OUTPUT_SHA256: str | None = (
    "D75600A25C086D41190589DA21C8B389ACD9A9BAD561B920F9BB25F5FB9E5B88"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PREVIOUS = load_module(BASE_BUILDER_PATH, "selector628_checkpoint_base")
BASE = PREVIOUS.BASE
ORIGINAL_PATCH_PREDECESSOR_ROW = PREVIOUS.ORIGINAL_PATCH_PREDECESSOR_ROW


def configure_base() -> None:
    PREVIOUS.configure_base()
    for name, value in {
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
    }.items():
        setattr(BASE, name, value)
    BASE.SCHEMA = (
        "nobu16.kr.pc-dialogue-runtime-vm-selector628-delta-checkpoint."
        "source-free.v1"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector628-consolidated-closure-decision.private.v1"
    )
    BASE.METHOD = (
        "post_selector514_selector628_single_coordinate_union_targeted_ledger_delta"
    )
    BASE.UPDATE_ACTION_FIELD = UPDATE_ACTION_FIELD
    BASE.EXACT_OVERRIDE_FIELD = "selector628_consolidated_exact_override_evidence"


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
        and cr.get("predecessor_overlaps") == 1
        and cr.get("predecessor_supersessions") == 1
        and pr.get("decision_rows") == EXPECTED_DECISIONS
        and pr.get("promotions") == EXPECTED_PROMOTIONS
        and pr.get("renewals") == EXPECTED_RENEWALS
        and pr.get("overrides") == EXPECTED_OVERRIDES
        and pr.get("action_counts") == EXPECTED_ACTION_COUNTS
        and pr.get("pending_before") == EXPECTED_PREDECESSOR_PENDING
        and pr.get("pending_after") == EXPECTED_FINAL_PENDING,
        "selector628 closure report drifted",
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
        "selector628 closure guard drifted",
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
            "selector628 closure lineage drifted",
        )


def patch_predecessor_row(
    predecessor: dict[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    changed = ORIGINAL_PATCH_PREDECESSOR_ROW(predecessor, decision)
    verification = changed["runtime_vm_verification"]
    verification["schema"] = (
        "nobu16.kr.pk-selector628-consolidated-row-verification.v1"
    )
    verification["method"] = "reversed_vm_pk_selector628_consolidated_closure"
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
        "selector628_consolidated": {
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
            "source_only_repair_site_count": EXPECTED_SOURCE_ONLY_SITES,
            "source_only_site_sha256": EXPECTED_SOURCE_ONLY_SITE_SHA256,
            "source_only_action_count": 0,
            "predecessor_overlap_count": 1,
            "predecessor_supersession_count": 1,
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
            "source_only_sites_rechecked": EXPECTED_SOURCE_ONLY_SITES,
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
        "selector514 targeted checkpoint base drifted",
    )
    configure_base()
    BASE.validate_closure_reports = validate_closure_reports
    BASE.patch_predecessor_row = patch_predecessor_row
    BASE.build_public_report = build_public_report
    return BASE.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
