#!/usr/bin/env python3
"""Apply selector-178 as a targeted immutable ledger delta."""

from __future__ import annotations

import importlib.util
import json
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
    WORKSTREAM / "build_runtime_vm_post_selector1198_consolidated_checkpoint_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1198_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector1198_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    PK_AUDIT / "build_pk_selector178_consolidated_closure_v1.py"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector178_consolidated_closure_decisions.private.v1.jsonl"
)
CLOSURE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector178_consolidated_closure_evidence.private.v1.json"
)
CLOSURE_COVERAGE_PATH = (
    PK_AUDIT / "public" / "pk_selector178_consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    PK_AUDIT / "public" / "pk_selector178_consolidated_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector178_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector178_consolidated_checkpoint.source_free.v1.json"
)

EXPECTED_BASE_BUILDER_SHA256 = (
    "B7F5688FA0155B6743D82F9DDDBA8C523946A8B381E2EF8418FB0C56B167B5C6"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "A3B6AE01A30C4EC6EFCE171345EFEB81F7FDB9EDFDCAECD90AA4A78AB3296F4F"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "DAD1BCD22AAE11BDD5D10669BC052240FDDAFD634AE5B6A32353BF11CE563B2C"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "74E30E798B82129565518FA04F35DC73220974CFC6E1E7E61BCEC2D8008671DA"
)
EXPECTED_CLOSURE_BUILDER_SHA256 = (
    "50645CF73A385B4FF34EE6A961CFE9721BF90379E5B411C04131481E21D897B8"
)
EXPECTED_CLOSURE_DECISIONS_SHA256 = (
    "2F81E5E455F613A8B6550787FFB278282002B7BC487B60B29E05DCB09CB4C093"
)
EXPECTED_CLOSURE_EVIDENCE_SHA256 = (
    "E8C5E9E78CD585183E9D4C38A1C3A116494CCD25D2577B2D381920F7F386A407"
)
EXPECTED_CLOSURE_COVERAGE_SHA256 = (
    "3263178FBA9FAC322472CDC0599234AD27EF56B1EB78A4AA24DEA3B9D00462FF"
)
EXPECTED_CLOSURE_PROMOTION_SHA256 = (
    "4D3CE8E47126BCFC20B068DB4163319C2AECA37C95655BE52A03CEC1D7E7D147"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 70
EXPECTED_UNAFFECTED_ROWS = 52_733
EXPECTED_OWNER_ROWS = 70
EXPECTED_PROMOTIONS = 32
EXPECTED_RENEWALS = 38
EXPECTED_OVERRIDES = 47
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 23,
    "translation_override_and_runtime_promotion": 9,
    "translation_override_and_verification_renewal": 38,
}
EXPECTED_OWNER_CHUNK_COUNTS = {0: 22, 1: 48}
EXPECTED_PREDECESSOR_PENDING = 6_464
EXPECTED_FINAL_PENDING = 6_432
EXPECTED_PREDECESSOR_ELIGIBLE = 46_339
EXPECTED_FINAL_ELIGIBLE = 46_371
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 14_219
EXPECTED_FINAL_PK_PROMOTIONS = 14_251
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 29_870
EXPECTED_FINAL_PROMOTED_TOTAL = 29_902
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_REVIEWED_SITES = 153
EXPECTED_SOURCE_ONLY_SITES = 10
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "C3A8A1832CDA66D290005900E9609896ED59043F2507EAFE68E4E2566D7048E1"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "DA73EC0BD42C63F5F7EC5956EC76813014DF2A88E0DF7EF60C29FA89B904E032"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "97F00C5ED8CD8C5936E45911F24F777E20AD21F30B7C836A05F4593D21E8365B"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "E79D24DC9E99ECFF9ED88357223370038C17A6CB5EFF5D63503C6D05471A67F1"
)
EXPECTED_REVIEWED_SITE_SHA256 = (
    "20DEFAEEC547AC566E2B1D74E0C3CB47EF2B7477AB01E06A3DA5CA890ADCC0D7"
)
EXPECTED_SOURCE_ONLY_SITE_SHA256 = (
    "87DD78E9FC339A62810B94DE2FCCB39FEAE1A5C5E583454B7C6F11A5C5A08D05"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "D89D47866F7FA9D34F68814219A00840921C130E062EA5DE80F95063B9E96E7F"
)
UPDATE_ACTION_FIELD = "selector178_consolidated_update_action"

EXPECTED_PRIVATE_OUTPUT_SHA256: str | None = (
    "A11DC8F5F0BAA9532DCB7737AFAFC8732506AC2F4E4B6479B44056CF9958015D"
)
EXPECTED_PUBLIC_OUTPUT_SHA256: str | None = (
    "8850CDFFDEF13076DF8402F68AA4F72528C9ACEE8145F4A65B4FAF64C7A27742"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PREVIOUS = load_module(BASE_BUILDER_PATH, "selector178_checkpoint_base")
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
        "nobu16.kr.pc-dialogue-runtime-vm-selector178-delta-checkpoint."
        "source-free.v1"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector178-consolidated-closure-decision.private.v1"
    )
    BASE.METHOD = (
        "post_selector1198_selector178_single_coordinate_union_targeted_ledger_delta"
    )
    BASE.UPDATE_ACTION_FIELD = UPDATE_ACTION_FIELD
    BASE.EXACT_OVERRIDE_FIELD = "selector178_consolidated_exact_override_evidence"


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
        "selector178 closure report drifted",
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
        "selector178 closure guard drifted",
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
            "selector178 closure lineage drifted",
        )


def patch_predecessor_row(
    predecessor: dict[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    changed = ORIGINAL_PATCH_PREDECESSOR_ROW(predecessor, decision)
    verification = changed["runtime_vm_verification"]
    verification["schema"] = (
        "nobu16.kr.pk-selector178-consolidated-row-verification.v1"
    )
    verification["method"] = "reversed_vm_pk_selector178_consolidated_closure"
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
        "selector178_consolidated": {
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
            "confirmed_non_display": EXPECTED_CONFIRMED_NON_DISPLAY,
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


def validate_confirmed_non_display(
    decisions: Mapping[str, Mapping[str, Any]],
) -> None:
    count = 0
    touched = 0
    with PREDECESSOR_PRIVATE_PATH.open("r", encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            if row.get("scope_classification") == "confirmed_non_display":
                count += 1
                if (
                    row.get("resource") == "pk_msggame"
                    and str(row.get("coordinate")) in decisions
                ):
                    touched += 1
    BASE.require(
        count == EXPECTED_CONFIRMED_NON_DISPLAY and touched == 0,
        "confirmed-non-display predecessor invariant drifted",
    )


def main(argv: Sequence[str] | None = None) -> int:
    BASE.require(
        BASE.sha256_file(BASE_BUILDER_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "selector1198 targeted checkpoint base drifted",
    )
    configure_base()
    BASE.validate_closure_reports = validate_closure_reports
    BASE.patch_predecessor_row = patch_predecessor_row
    BASE.build_public_report = build_public_report
    validate_confirmed_non_display(BASE.load_closure_decisions())
    return BASE.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
