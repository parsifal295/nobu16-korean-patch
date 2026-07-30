#!/usr/bin/env python3
"""Apply selector-760 as a targeted immutable ledger delta."""

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

PREDECESSOR_BUILDER_PATH = (
    WORKSTREAM / "build_runtime_vm_post_selector1090_consolidated_checkpoint_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1090_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector1090_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    PK_AUDIT / "build_pk_selector760_consolidated_closure_v1.py"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector760_consolidated_closure_decisions.private.v1.jsonl"
)
CLOSURE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector760_consolidated_closure_evidence.private.v1.json"
)
CLOSURE_COVERAGE_PATH = (
    PK_AUDIT / "public" / "pk_selector760_consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    PK_AUDIT / "public" / "pk_selector760_consolidated_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector760_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector760_consolidated_checkpoint.source_free.v1.json"
)

EXPECTED_PREDECESSOR_BUILDER_SHA256 = (
    "B952BB83C720465B75F6AF125B062C68F736826DEB5B4B1E2FCF5B77B8749277"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "CDF7539F8E6A6F0D024A7357854A0AFE45E91F3CBD144822E1DEF8730A9A373F"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "C01950D1B342D45FF8C6FBEB3D7EFD0B5087592D0585EC1A60A668FE0C0B0D93"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "396A8DF109A0693C439F990049477F5DE6E10720854D73057F3DFA1702002CCF"
)
EXPECTED_CLOSURE_BUILDER_SHA256 = (
    "DAE91CA004EE830837AE4B672591095A92A8FDB88374C03E4825C18F532B5D68"
)
EXPECTED_CLOSURE_DECISIONS_SHA256 = (
    "959DD7C8607CBB4F5FCB1DF769914ABF03331A1F7C3CDB75EFD073303BB05FB3"
)
EXPECTED_CLOSURE_EVIDENCE_SHA256 = (
    "FD4A436CEDF6C51B61C3CBF42275C70FC56DD2C7D43F5A6C1CC563EB45B554AC"
)
EXPECTED_CLOSURE_COVERAGE_SHA256 = (
    "089ECED1B842375BB0B33FF5AAD08ED35EDD32B1DE142ECD9F3EB9AB277458F4"
)
EXPECTED_CLOSURE_PROMOTION_SHA256 = (
    "04A6157CBAB6D9546F74C0CEF1266076BF5F87048642F3833872BF240F3B68C8"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 30
EXPECTED_UNAFFECTED_ROWS = 52_773
EXPECTED_OWNER_ROWS = 30
EXPECTED_PROMOTIONS = 27
EXPECTED_RENEWALS = 3
EXPECTED_OVERRIDES = 14
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 16,
    "translation_override_and_runtime_promotion": 11,
    "translation_override_and_verification_renewal": 3,
}
EXPECTED_OWNER_CHUNK_COUNTS = {1: 30}
EXPECTED_PREDECESSOR_PENDING = 6_368
EXPECTED_FINAL_PENDING = 6_341
EXPECTED_PREDECESSOR_ELIGIBLE = 46_435
EXPECTED_FINAL_ELIGIBLE = 46_462
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 14_315
EXPECTED_FINAL_PK_PROMOTIONS = 14_342
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 29_966
EXPECTED_FINAL_PROMOTED_TOTAL = 29_993
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_REVIEWED_SITES = 32
EXPECTED_SOURCE_ONLY_SITES = 3
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "C14B5FC0FFFD08997BCAA1685B98015C8EB7207AE7290DB16059A3D27C1E3EDD"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "FBB11BF3A69947409A9E443A15F4E1773981565EAB42326E6AA58D0F3D23C020"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "24FAC46E2722AFD0994829AAF0B1C206DC88445DEC12AED4AF00DA11C52C4CE9"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "3247C83C4288BA33BF53007BEA758BDF6A9004268B678F389148B4B3BA7E1EC5"
)
EXPECTED_REVIEWED_SITE_SHA256 = (
    "1226CF6A1892998D892C15480708068D21ADA054D21BDA982DF0D0B51E05131D"
)
EXPECTED_SOURCE_ONLY_SITE_SHA256 = (
    "D6C6A092B570F9846E422D7063FEFD47342351DB248E6EDE52DE1BB8880188A5"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "03D128438A4A79F1C4C59D46996D93E8DBD10ECAF707E18E0A46A0B3AF29A2F5"
)
UPDATE_ACTION_FIELD = "selector760_consolidated_update_action"
EXPECTED_PRIVATE_OUTPUT_SHA256: str | None = (
    "797D27314E8E168E1F2BACF9174E7246B83BF6DEDB0AC3B6C925D6D076CAC8C3"
)
EXPECTED_PUBLIC_OUTPUT_SHA256: str | None = (
    "3B67EC38FCECCD9B9592A39C426EC14F64EF9354C608C176730460E2C37D8B6D"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PREVIOUS = load_module(PREDECESSOR_BUILDER_PATH, "selector760_checkpoint_base")
BASE = PREVIOUS.BASE
ORIGINAL_PATCH_PREDECESSOR_ROW = PREVIOUS.ORIGINAL_PATCH_PREDECESSOR_ROW


def configure_base() -> None:
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
        "EXPECTED_OWNER_ROWS": EXPECTED_OWNER_ROWS,
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
        "EXPECTED_CONFIRMED_NON_DISPLAY": EXPECTED_CONFIRMED_NON_DISPLAY,
        "EXPECTED_REVIEWED_SITES": EXPECTED_REVIEWED_SITES,
        "EXPECTED_SOURCE_ONLY_SITES": EXPECTED_SOURCE_ONLY_SITES,
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
        "UPDATE_ACTION_FIELD": UPDATE_ACTION_FIELD,
    }
    for name, value in values.items():
        setattr(PREVIOUS, name, value)
    PREVIOUS.configure_base()
    BASE.SCHEMA = (
        "nobu16.kr.pc-dialogue-runtime-vm-selector760-delta-checkpoint."
        "source-free.v1"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector760-consolidated-closure-decision.private.v1"
    )
    BASE.METHOD = (
        "post_selector1090_selector760_single_coordinate_union_targeted_ledger_delta"
    )
    BASE.UPDATE_ACTION_FIELD = UPDATE_ACTION_FIELD
    BASE.EXACT_OVERRIDE_FIELD = "selector760_consolidated_exact_override_evidence"


def patch_predecessor_row(
    predecessor: dict[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    changed = ORIGINAL_PATCH_PREDECESSOR_ROW(predecessor, decision)
    verification = changed["runtime_vm_verification"]
    verification["schema"] = (
        "nobu16.kr.pk-selector760-consolidated-row-verification.v1"
    )
    verification["method"] = "reversed_vm_pk_selector760_consolidated_closure"
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
        "selector760_consolidated": {
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
        BASE.sha256_file(PREDECESSOR_BUILDER_PATH)
        == EXPECTED_PREDECESSOR_BUILDER_SHA256,
        "selector1090 targeted checkpoint base drifted",
    )
    configure_base()
    BASE.validate_closure_reports = PREVIOUS.validate_closure_reports
    BASE.patch_predecessor_row = patch_predecessor_row
    BASE.build_public_report = build_public_report
    decisions = BASE.load_closure_decisions()
    validate_confirmed_non_display(decisions)
    return BASE.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
