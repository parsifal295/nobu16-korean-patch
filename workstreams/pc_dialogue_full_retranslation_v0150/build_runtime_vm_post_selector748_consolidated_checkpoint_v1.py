#!/usr/bin/env python3
"""Apply selector-748 as a 147-coordinate targeted immutable ledger delta."""

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
    WORKSTREAM / "build_runtime_vm_post_selector550_consolidated_checkpoint_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector550_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector550_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    PK_AUDIT / "build_pk_selector748_consolidated_closure_v1.py"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector748_consolidated_closure_decisions.private.v1.jsonl"
)
CLOSURE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector748_consolidated_closure_evidence.private.v1.json"
)
CLOSURE_COVERAGE_PATH = (
    PK_AUDIT / "public" / "pk_selector748_consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    PK_AUDIT / "public" / "pk_selector748_consolidated_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector748_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector748_consolidated_checkpoint.source_free.v1.json"
)

EXPECTED_BASE_BUILDER_SHA256 = (
    "A5EB1AD4E2F5CF35E824C1F4131E2B99D10E6E3FFE6AAF50487FD50011AF8C4C"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "F2CB7279F71D33CFA9D73BD4A6DA8E7E90692047F8ECF1D521FD70512D71846E"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "2120F85E7450E58667C784D0ED2035589E1E6674563B94A938545A51B9C573CC"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "15C3BF1B4CC2E29020E5A8A6F40669555B54EEE57B04C3F7F77DF3AC680CFB93"
)
EXPECTED_CLOSURE_BUILDER_SHA256 = (
    "FCFFA6BC40D3B39E1FFE6B07ADF407CA3B45F712BE44E865DA51CD8D7C0A7EE9"
)
EXPECTED_CLOSURE_DECISIONS_SHA256 = (
    "35D4A9DF18F3BFC14866B5EEE52606D5BCF41282D0E400AD2B11284FD3C407AE"
)
EXPECTED_CLOSURE_EVIDENCE_SHA256 = (
    "B810947BAC53C9E989535CE95926AD61B3F3D85265B11699F288BC5D6E87D496"
)
EXPECTED_CLOSURE_COVERAGE_SHA256 = (
    "6FAD3A50788E7E4FFF2A25171C9461EA77BA5706B9E40E3C09E8F4BAFB95C78E"
)
EXPECTED_CLOSURE_PROMOTION_SHA256 = (
    "F253708E1DC1D171D57EA8C6D55A0CEC2E0366E8A614364A2C6F23C493607487"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 147
EXPECTED_UNAFFECTED_ROWS = 52_656
EXPECTED_OWNER_ROWS = 154
EXPECTED_PROMOTIONS = 101
EXPECTED_RENEWALS = 46
EXPECTED_OVERRIDES = 99
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 48,
    "translation_override_and_runtime_promotion": 53,
    "translation_override_and_verification_renewal": 46,
}
EXPECTED_OWNER_CHUNK_COUNTS = {0: 72, 1: 36, 2: 39}
EXPECTED_PREDECESSOR_PENDING = 6_980
EXPECTED_FINAL_PENDING = 6_879
EXPECTED_PREDECESSOR_ELIGIBLE = 45_823
EXPECTED_FINAL_ELIGIBLE = 45_924
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 13_703
EXPECTED_FINAL_PK_PROMOTIONS = 13_804
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 29_354
EXPECTED_FINAL_PROMOTED_TOTAL = 29_455
EXPECTED_REVIEWED_SITES = 102
EXPECTED_SOURCE_ONLY_SITES = 12
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "21BED7CD926A5D699ECBE4F240D9CB41085C1A888E021504557730F4B74830E4"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "CABC471277C98FD744C34251EA5E5FF073D6764B3F20422A6E79AA10E994D4AA"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "61042C5B2B468EB02DF3A6859D33F5E43B0D43377A24E34131A374556F065294"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "B1E7473FA32CA6992E04E80ACAD3F4DC33D2A8761A7A454F897F159256E2A5F6"
)
EXPECTED_REVIEWED_SITE_SHA256 = (
    "D69B1CEAF19B324B5B3D6C29AF16F9890A705BA1E4D9CE8DDD758A4CD9FDFF54"
)
EXPECTED_SOURCE_ONLY_SITE_SHA256 = (
    "C4E05AF2C8076ED3386680145364D99CF22E76D624047B5A587ED20EB343CF40"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "903B515128E94FE263430FAF7EECC51759A0DD132211F3C3047E5DAA6D16D9A6"
)
UPDATE_ACTION_FIELD = "selector748_consolidated_update_action"

# Frozen after deterministic bootstrap.
EXPECTED_PRIVATE_OUTPUT_SHA256: str | None = (
    "05D9C79515E8B161CD469FFEC5C340F54BE9BB94BFBA8F725B8DFC025DE49E76"
)
EXPECTED_PUBLIC_OUTPUT_SHA256: str | None = (
    "882781E1F51D963610A492589C19B6FAE09B33BA533D1369C26E9864AA48BAA7"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE_WRAPPER = load_module(BASE_BUILDER_PATH, "selector748_checkpoint_base")
BASE = BASE_WRAPPER.BASE
ORIGINAL_CONFIGURE_BASE = BASE_WRAPPER.configure_base
ORIGINAL_PATCH_PREDECESSOR_ROW = BASE_WRAPPER.ORIGINAL_PATCH_PREDECESSOR_ROW

BASE_WRAPPER.PREDECESSOR_PRIVATE_PATH = PREDECESSOR_PRIVATE_PATH
BASE_WRAPPER.PREDECESSOR_PUBLIC_PATH = PREDECESSOR_PUBLIC_PATH
BASE_WRAPPER.CLOSURE_BUILDER_PATH = CLOSURE_BUILDER_PATH
BASE_WRAPPER.CLOSURE_DECISIONS_PATH = CLOSURE_DECISIONS_PATH
BASE_WRAPPER.CLOSURE_EVIDENCE_PATH = CLOSURE_EVIDENCE_PATH
BASE_WRAPPER.CLOSURE_COVERAGE_PATH = CLOSURE_COVERAGE_PATH
BASE_WRAPPER.CLOSURE_PROMOTION_PATH = CLOSURE_PROMOTION_PATH
BASE_WRAPPER.DEFAULT_PRIVATE_OUTPUT = DEFAULT_PRIVATE_OUTPUT
BASE_WRAPPER.DEFAULT_PUBLIC_OUTPUT = DEFAULT_PUBLIC_OUTPUT
BASE_WRAPPER.EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    EXPECTED_PREDECESSOR_PRIVATE_SHA256
)
BASE_WRAPPER.EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    EXPECTED_PREDECESSOR_PUBLIC_SHA256
)
BASE_WRAPPER.EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    EXPECTED_PREDECESSOR_CANDIDATE_SHA256
)
BASE_WRAPPER.EXPECTED_CLOSURE_BUILDER_SHA256 = EXPECTED_CLOSURE_BUILDER_SHA256
BASE_WRAPPER.EXPECTED_CLOSURE_DECISIONS_SHA256 = (
    EXPECTED_CLOSURE_DECISIONS_SHA256
)
BASE_WRAPPER.EXPECTED_CLOSURE_EVIDENCE_SHA256 = (
    EXPECTED_CLOSURE_EVIDENCE_SHA256
)
BASE_WRAPPER.EXPECTED_CLOSURE_COVERAGE_SHA256 = (
    EXPECTED_CLOSURE_COVERAGE_SHA256
)
BASE_WRAPPER.EXPECTED_CLOSURE_PROMOTION_SHA256 = (
    EXPECTED_CLOSURE_PROMOTION_SHA256
)
BASE_WRAPPER.EXPECTED_ROWS = EXPECTED_ROWS
BASE_WRAPPER.EXPECTED_DECISIONS = EXPECTED_DECISIONS
BASE_WRAPPER.EXPECTED_UNAFFECTED_ROWS = EXPECTED_UNAFFECTED_ROWS
BASE_WRAPPER.EXPECTED_PROMOTIONS = EXPECTED_PROMOTIONS
BASE_WRAPPER.EXPECTED_RENEWALS = EXPECTED_RENEWALS
BASE_WRAPPER.EXPECTED_OVERRIDES = EXPECTED_OVERRIDES
BASE_WRAPPER.EXPECTED_ACTION_COUNTS = EXPECTED_ACTION_COUNTS
BASE_WRAPPER.EXPECTED_OWNER_CHUNK_COUNTS = EXPECTED_OWNER_CHUNK_COUNTS
BASE_WRAPPER.EXPECTED_PREDECESSOR_PENDING = EXPECTED_PREDECESSOR_PENDING
BASE_WRAPPER.EXPECTED_FINAL_PENDING = EXPECTED_FINAL_PENDING
BASE_WRAPPER.EXPECTED_PREDECESSOR_ELIGIBLE = EXPECTED_PREDECESSOR_ELIGIBLE
BASE_WRAPPER.EXPECTED_FINAL_ELIGIBLE = EXPECTED_FINAL_ELIGIBLE
BASE_WRAPPER.EXPECTED_PREDECESSOR_PK_PROMOTIONS = (
    EXPECTED_PREDECESSOR_PK_PROMOTIONS
)
BASE_WRAPPER.EXPECTED_FINAL_PK_PROMOTIONS = EXPECTED_FINAL_PK_PROMOTIONS
BASE_WRAPPER.EXPECTED_PREDECESSOR_PROMOTED_TOTAL = (
    EXPECTED_PREDECESSOR_PROMOTED_TOTAL
)
BASE_WRAPPER.EXPECTED_FINAL_PROMOTED_TOTAL = EXPECTED_FINAL_PROMOTED_TOTAL
BASE_WRAPPER.EXPECTED_REVIEWED_SITES = EXPECTED_REVIEWED_SITES
BASE_WRAPPER.EXPECTED_SOURCE_ONLY_SITES = EXPECTED_SOURCE_ONLY_SITES
BASE_WRAPPER.EXPECTED_DECISION_COORDINATE_SHA256 = (
    EXPECTED_DECISION_COORDINATE_SHA256
)
BASE_WRAPPER.EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    EXPECTED_PROMOTION_COORDINATE_SHA256
)
BASE_WRAPPER.EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    EXPECTED_RENEWAL_COORDINATE_SHA256
)
BASE_WRAPPER.EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    EXPECTED_OVERRIDE_COORDINATE_SHA256
)
BASE_WRAPPER.EXPECTED_REVIEWED_SITE_SHA256 = EXPECTED_REVIEWED_SITE_SHA256
BASE_WRAPPER.EXPECTED_SOURCE_ONLY_SITE_SHA256 = (
    EXPECTED_SOURCE_ONLY_SITE_SHA256
)
BASE_WRAPPER.EXPECTED_FINAL_CANDIDATE_SHA256 = EXPECTED_FINAL_CANDIDATE_SHA256
BASE_WRAPPER.EXPECTED_PRIVATE_OUTPUT_SHA256 = EXPECTED_PRIVATE_OUTPUT_SHA256
BASE_WRAPPER.EXPECTED_PUBLIC_OUTPUT_SHA256 = EXPECTED_PUBLIC_OUTPUT_SHA256


def configure_base() -> None:
    ORIGINAL_CONFIGURE_BASE()
    BASE.SCHEMA = (
        "nobu16.kr.pc-dialogue-runtime-vm-selector748-delta-checkpoint."
        "source-free.v1"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector748-consolidated-closure-decision.private.v1"
    )
    BASE.METHOD = (
        "post_selector550_selector748_single_coordinate_union_targeted_ledger_delta"
    )
    BASE.UPDATE_ACTION_FIELD = UPDATE_ACTION_FIELD
    BASE.EXACT_OVERRIDE_FIELD = "selector748_consolidated_exact_override_evidence"


def validate_closure_reports(
    coverage: Mapping[str, Any],
    promotion: Mapping[str, Any],
) -> None:
    BASE.require(
        coverage.get("status") == promotion.get("status") == "PASS"
        and coverage.get("steam_write_performed") is False
        and promotion.get("steam_write_performed") is False,
        "selector748 closure status drifted",
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
        "selector748 closure count drifted",
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
        "selector748 closure guard drifted",
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
            "selector748 closure lineage drifted",
        )


def patch_predecessor_row(
    predecessor: dict[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    changed = ORIGINAL_PATCH_PREDECESSOR_ROW(predecessor, decision)
    verification = changed["runtime_vm_verification"]
    verification["schema"] = (
        "nobu16.kr.pk-selector748-consolidated-row-verification.v1"
    )
    verification["method"] = "reversed_vm_pk_selector748_consolidated_closure"
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
        "selector748_consolidated": {
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
    configure_base()
    return BASE.load_closure_decisions()


def main(argv: Sequence[str] | None = None) -> int:
    BASE.require(
        BASE.sha256_file(BASE_BUILDER_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "selector550 targeted checkpoint base drifted",
    )
    configure_base()
    BASE.validate_closure_reports = validate_closure_reports
    BASE.patch_predecessor_row = patch_predecessor_row
    BASE.build_public_report = build_public_report
    return BASE.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
