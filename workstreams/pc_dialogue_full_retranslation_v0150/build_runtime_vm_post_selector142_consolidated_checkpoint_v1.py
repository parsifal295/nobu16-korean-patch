#!/usr/bin/env python3
"""Apply selector-142 as a 162-coordinate targeted immutable ledger delta."""

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
    WORKSTREAM / "build_runtime_vm_post_selector1126_consolidated_checkpoint_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1126_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector1126_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    PK_AUDIT / "build_pk_selector142_consolidated_closure_v1.py"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector142_consolidated_closure_decisions.private.v1.jsonl"
)
CLOSURE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector142_consolidated_closure_evidence.private.v1.json"
)
CLOSURE_COVERAGE_PATH = (
    PK_AUDIT / "public" / "pk_selector142_consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    PK_AUDIT / "public" / "pk_selector142_consolidated_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector142_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector142_consolidated_checkpoint.source_free.v1.json"
)

EXPECTED_BASE_BUILDER_SHA256 = (
    "BB481F5E4653E771279CDC5D4DF23769BDCE28D5B2D85D8BA8B8224B78428325"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "3198DC9F7A06809636D0C43F5740A65B5D4C50E7226D53AA7C52B7D893EFA06E"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "BD38D0EE71B59ADFEB8146760B91E82A7E09604E17B770760F13C94CB32704A5"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "B25D15DB919FC4E3CF3A68E7C10938F581C233F04DA111F1C8D0ECA0A3F86D62"
)
EXPECTED_CLOSURE_BUILDER_SHA256 = (
    "F9AE146781E6BD408BB3404A5923A149C0ABD48B1077B94B631AA376BB2BC3C7"
)
EXPECTED_CLOSURE_DECISIONS_SHA256 = (
    "E0AD32905438B6E1228F512105B1AE33570B51307FFA5550A1A2E82D8B5D6692"
)
EXPECTED_CLOSURE_EVIDENCE_SHA256 = (
    "9822F9E413F8F74DD5AA08D7F7626B69143295F22EAF6BAFA569BF0C7FC48FAF"
)
EXPECTED_CLOSURE_COVERAGE_SHA256 = (
    "C2E6289A849D7D2ADE417DF818F0CE373017C6F4FB5E398C7F17956933F1FA7A"
)
EXPECTED_CLOSURE_PROMOTION_SHA256 = (
    "35D1E186215717B75C781B8A04FF70F3D26714ED3605ED5E0C1BF6BB48F0DE26"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 162
EXPECTED_UNAFFECTED_ROWS = 52_641
EXPECTED_OWNER_ROWS = 162
EXPECTED_PROMOTIONS = 116
EXPECTED_RENEWALS = 46
EXPECTED_OVERRIDES = 101
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 61,
    "translation_override_and_runtime_promotion": 55,
    "translation_override_and_verification_renewal": 46,
}
EXPECTED_OWNER_CHUNK_COUNTS = {0: 46, 1: 53, 2: 63}
EXPECTED_PREDECESSOR_PENDING = 6_761
EXPECTED_FINAL_PENDING = 6_645
EXPECTED_PREDECESSOR_ELIGIBLE = 46_042
EXPECTED_FINAL_ELIGIBLE = 46_158
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 13_922
EXPECTED_FINAL_PK_PROMOTIONS = 14_038
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 29_573
EXPECTED_FINAL_PROMOTED_TOTAL = 29_689
EXPECTED_REVIEWED_SITES = 109
EXPECTED_SOURCE_ONLY_SITES = 6
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "719F9CA4F9801104F5255824916307084EDF1FB20D16B1373EB801B3783A759E"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "18E0612009B06E1C9E7DB613C2A118C647C0073FF43F9C75E9C0EEC6F83D69D9"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "28366F53ED7F7C6019DBF228458D0CF14D6D6910EB5E91877427BE57ED91C826"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "8ED2707A3B3EE4F46788D7CB4DD6C614CD0FC8C68C333EEB67720E9B2264F065"
)
EXPECTED_REVIEWED_SITE_SHA256 = (
    "4E040FA596394C5378375876510E3A296F66719CB57370AF9AF0445B9F8CD070"
)
EXPECTED_SOURCE_ONLY_SITE_SHA256 = (
    "C4F5553FF0AE65E2880C01A09914A138F36F15A887E783EDC9192B6FCB08E40B"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "6E3E5CD8A0FF7CC07C69BD9ABDCB2380FFD507D21F528E2A446D57329359F6A8"
)
UPDATE_ACTION_FIELD = "selector142_consolidated_update_action"

# Frozen after deterministic targeted bootstrap.
EXPECTED_PRIVATE_OUTPUT_SHA256: str | None = (
    "5D3673BC67F8FB55B258BB236CBC6ACD3E76F2E001300994ED7AFD742601C0DB"
)
EXPECTED_PUBLIC_OUTPUT_SHA256: str | None = (
    "FB3119A8080949EDC0BA740E893C4C4B387FF8BC6564E6E4C1B19A3DC8D9A919"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE_WRAPPER = load_module(BASE_BUILDER_PATH, "selector142_checkpoint_base")
BASE = BASE_WRAPPER.BASE
ORIGINAL_PATCH_PREDECESSOR_ROW = BASE_WRAPPER.ORIGINAL_PATCH_PREDECESSOR_ROW

for _name in (
    "PREDECESSOR_PRIVATE_PATH",
    "PREDECESSOR_PUBLIC_PATH",
    "CLOSURE_BUILDER_PATH",
    "CLOSURE_DECISIONS_PATH",
    "CLOSURE_EVIDENCE_PATH",
    "CLOSURE_COVERAGE_PATH",
    "CLOSURE_PROMOTION_PATH",
    "DEFAULT_PRIVATE_OUTPUT",
    "DEFAULT_PUBLIC_OUTPUT",
    "EXPECTED_PREDECESSOR_PRIVATE_SHA256",
    "EXPECTED_PREDECESSOR_PUBLIC_SHA256",
    "EXPECTED_PREDECESSOR_CANDIDATE_SHA256",
    "EXPECTED_CLOSURE_BUILDER_SHA256",
    "EXPECTED_CLOSURE_DECISIONS_SHA256",
    "EXPECTED_CLOSURE_EVIDENCE_SHA256",
    "EXPECTED_CLOSURE_COVERAGE_SHA256",
    "EXPECTED_CLOSURE_PROMOTION_SHA256",
    "EXPECTED_ROWS",
    "EXPECTED_DECISIONS",
    "EXPECTED_UNAFFECTED_ROWS",
    "EXPECTED_OWNER_ROWS",
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
    "EXPECTED_REVIEWED_SITES",
    "EXPECTED_SOURCE_ONLY_SITES",
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
    setattr(BASE_WRAPPER, _name, globals()[_name])


def configure_base() -> None:
    BASE_WRAPPER.configure_base()
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
        "nobu16.kr.pc-dialogue-runtime-vm-selector142-delta-checkpoint."
        "source-free.v1"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector142-consolidated-closure-decision.private.v1"
    )
    BASE.METHOD = (
        "post_selector1126_selector142_single_coordinate_union_targeted_ledger_delta"
    )
    BASE.UPDATE_ACTION_FIELD = UPDATE_ACTION_FIELD
    BASE.EXACT_OVERRIDE_FIELD = "selector142_consolidated_exact_override_evidence"
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
        "selector142 closure status drifted",
    )
    cr = coverage["result"]
    pr = promotion["result"]
    BASE.require(
        cr.get("coordinate_union_rows") == EXPECTED_DECISIONS
        and cr.get("owner_decision_rows") == EXPECTED_OWNER_ROWS
        and cr.get("reviewed_sites") == EXPECTED_REVIEWED_SITES
        and cr.get("source_only_sites") == EXPECTED_SOURCE_ONLY_SITES
        and cr.get("source_only_actions") == 0
        and cr.get("predecessor_overlaps") == 0
        and cr.get("predecessor_supersessions") == 0
        and pr.get("coordinate_union_rows") == EXPECTED_DECISIONS
        and pr.get("decision_rows") == EXPECTED_OWNER_ROWS
        and pr.get("promotions") == EXPECTED_PROMOTIONS
        and pr.get("effective_renewals") == EXPECTED_RENEWALS
        and pr.get("effective_overrides") == EXPECTED_OVERRIDES
        and pr.get("effective_action_counts") == EXPECTED_ACTION_COUNTS
        and pr.get("pending_before") == EXPECTED_PREDECESSOR_PENDING
        and pr.get("pending_after") == EXPECTED_FINAL_PENDING,
        "selector142 closure count drifted",
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
        "selector142 closure guard drifted",
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
            "selector142 closure lineage drifted",
        )


def patch_predecessor_row(
    predecessor: dict[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    changed = ORIGINAL_PATCH_PREDECESSOR_ROW(predecessor, decision)
    verification = changed["runtime_vm_verification"]
    verification["schema"] = (
        "nobu16.kr.pk-selector142-consolidated-row-verification.v1"
    )
    verification["method"] = "reversed_vm_pk_selector142_consolidated_closure"
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
        "selector142_consolidated": {
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
        "selector1126 targeted checkpoint base drifted",
    )
    configure_base()
    BASE.validate_closure_reports = validate_closure_reports
    BASE.patch_predecessor_row = patch_predecessor_row
    BASE.build_public_report = build_public_report
    return BASE.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
