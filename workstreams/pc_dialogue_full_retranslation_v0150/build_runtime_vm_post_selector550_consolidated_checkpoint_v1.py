#!/usr/bin/env python3
"""Apply selector-550 as a 224-coordinate targeted immutable ledger delta."""

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

GENERIC_BUILDER_PATH = (
    WORKSTREAM / "build_runtime_vm_post_selector610_consolidated_checkpoint_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector610_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector610_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    PK_AUDIT / "build_pk_selector550_consolidated_closure_v1.py"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector550_consolidated_closure_decisions.private.v1.jsonl"
)
CLOSURE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector550_consolidated_closure_evidence.private.v1.json"
)
CLOSURE_COVERAGE_PATH = (
    PK_AUDIT / "public" / "pk_selector550_consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    PK_AUDIT / "public" / "pk_selector550_consolidated_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector550_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector550_consolidated_checkpoint.source_free.v1.json"
)

EXPECTED_GENERIC_BUILDER_SHA256 = (
    "95BEB55BCA35AC165FA869C22BB8F243E0C07B479C57BD6F688EAEFD9611C150"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "0218C3D198C9930C8920ED8DAEB2DDD85987878035AC59DD5ECC8179D38DE12B"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "42BB33CD2F7553EE3E251DDD78933F85D181F140AA133C5843F6DBDF379B53D3"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "F80EA5958757F097885279BAB53A8456758BB99B1CE47E214FE0F54AB7152807"
)
EXPECTED_CLOSURE_BUILDER_SHA256 = (
    "F7F5FEF832B1C98AD288E3A72BD1A02744B5C14D305B3F901CE8484876C67C26"
)
EXPECTED_CLOSURE_DECISIONS_SHA256 = (
    "EAA8AB5A7B71532AC5E95C0C772C990AD05A9B9DFA0D2CCFDB3A813469F0F600"
)
EXPECTED_CLOSURE_EVIDENCE_SHA256 = (
    "A3FD969E350F80D2653E1142540ED6FC20B56683EAD1E06A82E237CBAF604B4C"
)
EXPECTED_CLOSURE_COVERAGE_SHA256 = (
    "42B456C6B3CA425B173366E092BDD5CD8FBDAD147DAB45EBBA6724464498B520"
)
EXPECTED_CLOSURE_PROMOTION_SHA256 = (
    "756397FC3F228DF36F8544E6914782BE3A7C4361F36C395134BEB675CB4F7B55"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 224
EXPECTED_UNAFFECTED_ROWS = 52_579
EXPECTED_PROMOTIONS = 121
EXPECTED_RENEWALS = 103
EXPECTED_OVERRIDES = 131
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 93,
    "translation_override_and_runtime_promotion": 28,
    "translation_override_and_verification_renewal": 103,
}
EXPECTED_OWNER_CHUNK_COUNTS = {0: 84, 1: 80, 2: 60}
EXPECTED_PREDECESSOR_PENDING = 7_101
EXPECTED_FINAL_PENDING = 6_980
EXPECTED_PREDECESSOR_ELIGIBLE = 45_702
EXPECTED_FINAL_ELIGIBLE = 45_823
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 13_582
EXPECTED_FINAL_PK_PROMOTIONS = 13_703
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 29_233
EXPECTED_FINAL_PROMOTED_TOTAL = 29_354
EXPECTED_REVIEWED_SITES = 169
EXPECTED_SOURCE_ONLY_SITES = 8
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "6F483AF06164F922C590F8FC7933E130AFE6CEF453A2D55901954975067DBF5E"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "F8C2CF55D1BA2BC4774BED272102DD34E513D324BEC98B2DBA2822EC61E4B644"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "1A3F07E583A179D622921643BA018A516F0FE1F6AEEEE7C85C0272E8D9DF504B"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "E9948002912296EFF51065967A19A70809FBCB00E352A49F4308796A23D2EF90"
)
EXPECTED_REVIEWED_SITE_SHA256 = (
    "C192D4C89E340FF974BB38DC57039AA28626976597B12DA976AC9D9BA0C49741"
)
EXPECTED_SOURCE_ONLY_SITE_SHA256 = (
    "D621F264506A41110B53B8D83022C4D73AE331EB2BFFF662ADBD81352A7E5308"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "15C3BF1B4CC2E29020E5A8A6F40669555B54EEE57B04C3F7F77DF3AC680CFB93"
)
UPDATE_ACTION_FIELD = "selector550_consolidated_update_action"

# Frozen after the first deterministic targeted write.
EXPECTED_PRIVATE_OUTPUT_SHA256: str | None = (
    "F2CB7279F71D33CFA9D73BD4A6DA8E7E90692047F8ECF1D521FD70512D71846E"
)
EXPECTED_PUBLIC_OUTPUT_SHA256: str | None = (
    "2120F85E7450E58667C784D0ED2035589E1E6674563B94A938545A51B9C573CC"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(GENERIC_BUILDER_PATH, "selector550_targeted_checkpoint_base")
ORIGINAL_PATCH_PREDECESSOR_ROW = BASE.patch_predecessor_row


def configure_base() -> None:
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
        "nobu16.kr.pc-dialogue-runtime-vm-selector550-delta-checkpoint."
        "source-free.v1"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector550-consolidated-closure-decision.private.v1"
    )
    BASE.METHOD = (
        "post_selector610_selector550_single_coordinate_union_targeted_ledger_delta"
    )
    BASE.UPDATE_ACTION_FIELD = "selector550_consolidated_update_action"
    BASE.EXACT_OVERRIDE_FIELD = "selector550_consolidated_exact_override_evidence"
    BASE.EXPECTED_ROWS = EXPECTED_ROWS
    BASE.EXPECTED_UNAFFECTED_ROWS = EXPECTED_UNAFFECTED_ROWS
    BASE.EXPECTED_DECISIONS = EXPECTED_DECISIONS
    BASE.EXPECTED_PROMOTIONS = EXPECTED_PROMOTIONS
    BASE.EXPECTED_RENEWALS = EXPECTED_RENEWALS
    BASE.EXPECTED_OVERRIDES = EXPECTED_OVERRIDES
    BASE.EXPECTED_ACTION_COUNTS = EXPECTED_ACTION_COUNTS
    BASE.EXPECTED_OWNER_CHUNK_COUNTS = EXPECTED_OWNER_CHUNK_COUNTS
    BASE.EXPECTED_PREDECESSOR_PENDING = EXPECTED_PREDECESSOR_PENDING
    BASE.EXPECTED_FINAL_PENDING = EXPECTED_FINAL_PENDING
    BASE.EXPECTED_PREDECESSOR_ELIGIBLE = EXPECTED_PREDECESSOR_ELIGIBLE
    BASE.EXPECTED_FINAL_ELIGIBLE = EXPECTED_FINAL_ELIGIBLE
    BASE.EXPECTED_PREDECESSOR_PK_PROMOTIONS = (
        EXPECTED_PREDECESSOR_PK_PROMOTIONS
    )
    BASE.EXPECTED_FINAL_PK_PROMOTIONS = EXPECTED_FINAL_PK_PROMOTIONS
    BASE.EXPECTED_PREDECESSOR_PROMOTED_TOTAL = (
        EXPECTED_PREDECESSOR_PROMOTED_TOTAL
    )
    BASE.EXPECTED_FINAL_PROMOTED_TOTAL = EXPECTED_FINAL_PROMOTED_TOTAL
    BASE.EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
        EXPECTED_PREDECESSOR_PRIVATE_SHA256
    )
    BASE.EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
        EXPECTED_PREDECESSOR_PUBLIC_SHA256
    )
    BASE.EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
        EXPECTED_PREDECESSOR_CANDIDATE_SHA256
    )
    BASE.EXPECTED_CLOSURE_BUILDER_SHA256 = EXPECTED_CLOSURE_BUILDER_SHA256
    BASE.EXPECTED_CLOSURE_DECISIONS_SHA256 = (
        EXPECTED_CLOSURE_DECISIONS_SHA256
    )
    BASE.EXPECTED_CLOSURE_EVIDENCE_SHA256 = (
        EXPECTED_CLOSURE_EVIDENCE_SHA256
    )
    BASE.EXPECTED_CLOSURE_COVERAGE_SHA256 = (
        EXPECTED_CLOSURE_COVERAGE_SHA256
    )
    BASE.EXPECTED_CLOSURE_PROMOTION_SHA256 = (
        EXPECTED_CLOSURE_PROMOTION_SHA256
    )
    BASE.EXPECTED_DECISION_COORDINATE_SHA256 = (
        EXPECTED_DECISION_COORDINATE_SHA256
    )
    BASE.EXPECTED_PROMOTION_COORDINATE_SHA256 = (
        EXPECTED_PROMOTION_COORDINATE_SHA256
    )
    BASE.EXPECTED_RENEWAL_COORDINATE_SHA256 = (
        EXPECTED_RENEWAL_COORDINATE_SHA256
    )
    BASE.EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
        EXPECTED_OVERRIDE_COORDINATE_SHA256
    )
    BASE.EXPECTED_REVIEWED_SITE_SHA256 = EXPECTED_REVIEWED_SITE_SHA256
    BASE.EXPECTED_SOURCE_ONLY_SITE_SHA256 = EXPECTED_SOURCE_ONLY_SITE_SHA256
    BASE.EXPECTED_FINAL_CANDIDATE_SHA256 = EXPECTED_FINAL_CANDIDATE_SHA256
    BASE.EXPECTED_PRIVATE_OUTPUT_SHA256 = EXPECTED_PRIVATE_OUTPUT_SHA256
    BASE.EXPECTED_PUBLIC_OUTPUT_SHA256 = EXPECTED_PUBLIC_OUTPUT_SHA256


def validate_closure_reports(
    coverage: Mapping[str, Any],
    promotion: Mapping[str, Any],
) -> None:
    BASE.require(
        coverage.get("status") == promotion.get("status") == "PASS"
        and coverage.get("steam_write_performed") is False
        and promotion.get("steam_write_performed") is False,
        "selector550 closure status drifted",
    )
    cr = coverage["result"]
    pr = promotion["result"]
    BASE.require(
        cr.get("coordinate_union_rows") == EXPECTED_DECISIONS
        and cr.get("owner_decision_rows") == 225
        and cr.get("reviewed_sites") == EXPECTED_REVIEWED_SITES
        and cr.get("source_only_sites") == EXPECTED_SOURCE_ONLY_SITES
        and cr.get("source_only_actions") == 0
        and pr.get("coordinate_union_rows") == EXPECTED_DECISIONS
        and pr.get("decision_rows") == 225
        and pr.get("promotions") == EXPECTED_PROMOTIONS
        and pr.get("effective_renewals") == EXPECTED_RENEWALS
        and pr.get("effective_overrides") == EXPECTED_OVERRIDES
        and pr.get("effective_action_counts") == EXPECTED_ACTION_COUNTS
        and pr.get("pending_before") == EXPECTED_PREDECESSOR_PENDING
        and pr.get("pending_after") == EXPECTED_FINAL_PENDING,
        "selector550 closure count drifted",
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
        "selector550 closure guard drifted",
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
            "selector550 closure lineage drifted",
        )


def patch_predecessor_row(
    predecessor: dict[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    changed = ORIGINAL_PATCH_PREDECESSOR_ROW(predecessor, decision)
    verification = changed["runtime_vm_verification"]
    verification["schema"] = (
        "nobu16.kr.pk-selector550-consolidated-row-verification.v1"
    )
    verification["method"] = "reversed_vm_pk_selector550_consolidated_closure"
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
        "selector550_consolidated": {
            "owner_decision_row_count": 225,
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
            "predecessor_candidate_sha256":
                EXPECTED_PREDECESSOR_CANDIDATE_SHA256,
            "final_candidate_sha256": EXPECTED_FINAL_CANDIDATE_SHA256,
            "reverse_overlay_sha256": EXPECTED_PREDECESSOR_CANDIDATE_SHA256,
            "single_coordinate_union_used": True,
            "identical_terminal_owner_overlap_deduplicated": True,
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
    """Expose the frozen effective decision union to targeted progress tools."""
    configure_base()
    return BASE.load_closure_decisions()


def main(argv: Sequence[str] | None = None) -> int:
    BASE.require(
        BASE.sha256_file(GENERIC_BUILDER_PATH) == EXPECTED_GENERIC_BUILDER_SHA256,
        "generic targeted checkpoint builder drifted",
    )
    configure_base()
    BASE.validate_closure_reports = validate_closure_reports
    BASE.patch_predecessor_row = patch_predecessor_row
    BASE.build_public_report = build_public_report
    return BASE.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
