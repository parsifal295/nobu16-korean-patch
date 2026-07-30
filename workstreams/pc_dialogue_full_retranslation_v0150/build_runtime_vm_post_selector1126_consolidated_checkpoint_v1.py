#!/usr/bin/env python3
"""Apply selector-1126 as a 185-coordinate targeted immutable ledger delta."""

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
    WORKSTREAM / "build_runtime_vm_post_selector748_consolidated_checkpoint_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector748_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector748_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    PK_AUDIT / "build_pk_selector1126_consolidated_closure_v1.py"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector1126_consolidated_closure_decisions.private.v1.jsonl"
)
CLOSURE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector1126_consolidated_closure_evidence.private.v1.json"
)
CLOSURE_COVERAGE_PATH = (
    PK_AUDIT / "public" / "pk_selector1126_consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    PK_AUDIT / "public" / "pk_selector1126_consolidated_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1126_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector1126_consolidated_checkpoint.source_free.v1.json"
)

EXPECTED_BASE_BUILDER_SHA256 = (
    "AA118738B65D91F902DED7C32C1C4F87CF9CB1B75ADA96D9FADB80724407BB97"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "05D9C79515E8B161CD469FFEC5C340F54BE9BB94BFBA8F725B8DFC025DE49E76"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "882781E1F51D963610A492589C19B6FAE09B33BA533D1369C26E9864AA48BAA7"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "903B515128E94FE263430FAF7EECC51759A0DD132211F3C3047E5DAA6D16D9A6"
)
EXPECTED_CLOSURE_BUILDER_SHA256 = (
    "AE769DBA9F0BBC1A6E04A663E6DBDE98ADC5DA45CA5CA1A4199DE1B0C3CBCC77"
)
EXPECTED_CLOSURE_DECISIONS_SHA256 = (
    "E7FE1D70A6DF175C25D3D4D42359983E26075F1962B8F0EB6BD52DC82376EB15"
)
EXPECTED_CLOSURE_EVIDENCE_SHA256 = (
    "88F6E0E0115D026359545301B5FD0B65F7D5D34AA2A07B79B2AF24E9956F2CDF"
)
EXPECTED_CLOSURE_COVERAGE_SHA256 = (
    "830B0F2EE480EA11AD6FAACE5A18522B56E314A8A673CEC766FA63E6A67A1F81"
)
EXPECTED_CLOSURE_PROMOTION_SHA256 = (
    "407906D270337DAFD38DB94A2192B171AA04F0ACE8D9EFEF5425AAEF0C4909F0"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 185
EXPECTED_UNAFFECTED_ROWS = 52_618
EXPECTED_OWNER_ROWS = 185
EXPECTED_PROMOTIONS = 118
EXPECTED_RENEWALS = 67
EXPECTED_OVERRIDES = 140
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 45,
    "translation_override_and_runtime_promotion": 73,
    "translation_override_and_verification_renewal": 67,
}
EXPECTED_OWNER_CHUNK_COUNTS = {0: 65, 1: 49, 2: 71}
EXPECTED_PREDECESSOR_PENDING = 6_879
EXPECTED_FINAL_PENDING = 6_761
EXPECTED_PREDECESSOR_ELIGIBLE = 45_924
EXPECTED_FINAL_ELIGIBLE = 46_042
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 13_804
EXPECTED_FINAL_PK_PROMOTIONS = 13_922
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 29_455
EXPECTED_FINAL_PROMOTED_TOTAL = 29_573
EXPECTED_REVIEWED_SITES = 114
EXPECTED_SOURCE_ONLY_SITES = 14
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "0BBBC43125AC65FD7F7EF9A78BA3AB6ACC0D91283F729AA721C0608607578208"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "AC668CFB8B8220593DA743BFD7547060C0503D118D5A08CDF4085977E8C86C04"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "B3ECFED0C1DE975316A6B9F400AA3ECEAABB3B19AFE846FB96B95855CA3C7588"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "760418C7AFCD2CC5B12A542D5DC35B2A4C528E4CDA329C7C804284A0C4F9957C"
)
EXPECTED_REVIEWED_SITE_SHA256 = (
    "4142609E7659D9E077D2648303DE0DC6D0C6717F4A0E22288263614B712D66BA"
)
EXPECTED_SOURCE_ONLY_SITE_SHA256 = (
    "8F97365A616918DA6E91CF4EB45A8DE4830305555832F7ED645517370DEFAAD8"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "B25D15DB919FC4E3CF3A68E7C10938F581C233F04DA111F1C8D0ECA0A3F86D62"
)
UPDATE_ACTION_FIELD = "selector1126_consolidated_update_action"

# Frozen after deterministic targeted bootstrap.
EXPECTED_PRIVATE_OUTPUT_SHA256: str | None = (
    "3198DC9F7A06809636D0C43F5740A65B5D4C50E7226D53AA7C52B7D893EFA06E"
)
EXPECTED_PUBLIC_OUTPUT_SHA256: str | None = (
    "BD38D0EE71B59ADFEB8146760B91E82A7E09604E17B770760F13C94CB32704A5"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE_WRAPPER = load_module(BASE_BUILDER_PATH, "selector1126_checkpoint_base")
BASE = BASE_WRAPPER.BASE
ORIGINAL_CONFIGURE_BASE = BASE_WRAPPER.configure_base
ORIGINAL_PATCH_PREDECESSOR_ROW = BASE_WRAPPER.ORIGINAL_PATCH_PREDECESSOR_ROW


def configure_base() -> None:
    ORIGINAL_CONFIGURE_BASE()
    BASE.PREDECESSOR_PRIVATE_PATH = PREDECESSOR_PRIVATE_PATH
    BASE.PREDECESSOR_PUBLIC_PATH = PREDECESSOR_PUBLIC_PATH
    BASE.CLOSURE_BUILDER_PATH = CLOSURE_BUILDER_PATH
    BASE.CLOSURE_DECISIONS_PATH = CLOSURE_DECISIONS_PATH
    BASE.CLOSURE_EVIDENCE_PATH = CLOSURE_EVIDENCE_PATH
    BASE.CLOSURE_COVERAGE_PATH = CLOSURE_COVERAGE_PATH
    BASE.CLOSURE_PROMOTION_PATH = CLOSURE_PROMOTION_PATH
    BASE.DEFAULT_PRIVATE_OUTPUT = DEFAULT_PRIVATE_OUTPUT
    BASE.DEFAULT_PUBLIC_OUTPUT = DEFAULT_PUBLIC_OUTPUT
    BASE.SCHEMA = (
        "nobu16.kr.pc-dialogue-runtime-vm-selector1126-delta-checkpoint."
        "source-free.v1"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector1126-consolidated-closure-decision.private.v1"
    )
    BASE.METHOD = (
        "post_selector748_selector1126_single_coordinate_union_targeted_ledger_delta"
    )
    BASE.UPDATE_ACTION_FIELD = UPDATE_ACTION_FIELD
    BASE.EXACT_OVERRIDE_FIELD = "selector1126_consolidated_exact_override_evidence"
    for name in (
        "EXPECTED_ROWS",
        "EXPECTED_DECISIONS",
        "EXPECTED_UNAFFECTED_ROWS",
        "EXPECTED_PROMOTIONS",
        "EXPECTED_RENEWALS",
        "EXPECTED_OVERRIDES",
        "EXPECTED_ACTION_COUNTS",
        "EXPECTED_OWNER_CHUNK_COUNTS",
        "EXPECTED_PREDECESSOR_PENDING",
        "EXPECTED_FINAL_PENDING",
        "EXPECTED_PREDECESSOR_ELIGIBLE",
        "EXPECTED_FINAL_ELIGIBLE",
        "EXPECTED_PREDECESSOR_PK_PROMOTIONS",
        "EXPECTED_FINAL_PK_PROMOTIONS",
        "EXPECTED_PREDECESSOR_PROMOTED_TOTAL",
        "EXPECTED_FINAL_PROMOTED_TOTAL",
        "EXPECTED_PREDECESSOR_PRIVATE_SHA256",
        "EXPECTED_PREDECESSOR_PUBLIC_SHA256",
        "EXPECTED_PREDECESSOR_CANDIDATE_SHA256",
        "EXPECTED_CLOSURE_BUILDER_SHA256",
        "EXPECTED_CLOSURE_DECISIONS_SHA256",
        "EXPECTED_CLOSURE_EVIDENCE_SHA256",
        "EXPECTED_CLOSURE_COVERAGE_SHA256",
        "EXPECTED_CLOSURE_PROMOTION_SHA256",
        "EXPECTED_DECISION_COORDINATE_SHA256",
        "EXPECTED_PROMOTION_COORDINATE_SHA256",
        "EXPECTED_RENEWAL_COORDINATE_SHA256",
        "EXPECTED_OVERRIDE_COORDINATE_SHA256",
        "EXPECTED_REVIEWED_SITE_SHA256",
        "EXPECTED_SOURCE_ONLY_SITE_SHA256",
        "EXPECTED_FINAL_CANDIDATE_SHA256",
        "EXPECTED_PRIVATE_OUTPUT_SHA256",
        "EXPECTED_PUBLIC_OUTPUT_SHA256",
    ):
        setattr(BASE, name, globals()[name])


def validate_closure_reports(
    coverage: Mapping[str, Any],
    promotion: Mapping[str, Any],
) -> None:
    BASE.require(
        coverage.get("status") == promotion.get("status") == "PASS"
        and coverage.get("steam_write_performed") is False
        and promotion.get("steam_write_performed") is False,
        "selector1126 closure status drifted",
    )
    cr = coverage["result"]
    pr = promotion["result"]
    BASE.require(
        cr.get("coordinate_union_rows") == EXPECTED_DECISIONS
        and cr.get("owner_decision_rows") == EXPECTED_OWNER_ROWS
        and cr.get("reviewed_sites") == EXPECTED_REVIEWED_SITES
        and cr.get("source_only_sites") == EXPECTED_SOURCE_ONLY_SITES
        and cr.get("source_only_actions") == 0
        and cr.get("predecessor_overlaps") == 1
        and cr.get("predecessor_supersessions") == 1
        and pr.get("coordinate_union_rows") == EXPECTED_DECISIONS
        and pr.get("decision_rows") == EXPECTED_OWNER_ROWS
        and pr.get("promotions") == EXPECTED_PROMOTIONS
        and pr.get("effective_renewals") == EXPECTED_RENEWALS
        and pr.get("effective_overrides") == EXPECTED_OVERRIDES
        and pr.get("effective_action_counts") == EXPECTED_ACTION_COUNTS
        and pr.get("pending_before") == EXPECTED_PREDECESSOR_PENDING
        and pr.get("pending_after") == EXPECTED_FINAL_PENDING,
        "selector1126 closure count drifted",
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
        "selector1126 closure guard drifted",
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
            "selector1126 closure lineage drifted",
        )


def patch_predecessor_row(
    predecessor: dict[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    changed = ORIGINAL_PATCH_PREDECESSOR_ROW(predecessor, decision)
    verification = changed["runtime_vm_verification"]
    verification["schema"] = (
        "nobu16.kr.pk-selector1126-consolidated-row-verification.v1"
    )
    verification["method"] = "reversed_vm_pk_selector1126_consolidated_closure"
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
        "selector1126_consolidated": {
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
        "selector748 targeted checkpoint base drifted",
    )
    configure_base()
    BASE.validate_closure_reports = validate_closure_reports
    BASE.patch_predecessor_row = patch_predecessor_row
    BASE.build_public_report = build_public_report
    return BASE.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
