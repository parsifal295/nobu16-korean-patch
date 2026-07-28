#!/usr/bin/env python3
"""Apply selector-742 as a targeted immutable ledger delta."""

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
    WORKSTREAM / "build_runtime_vm_post_selector760_consolidated_checkpoint_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector760_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector760_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    PK_AUDIT / "build_pk_selector742_consolidated_closure_v1.py"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector742_consolidated_closure_decisions.private.v1.jsonl"
)
CLOSURE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector742_consolidated_closure_evidence.private.v1.json"
)
CLOSURE_COVERAGE_PATH = (
    PK_AUDIT / "public" / "pk_selector742_consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    PK_AUDIT / "public" / "pk_selector742_consolidated_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector742_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector742_consolidated_checkpoint.source_free.v1.json"
)

EXPECTED_PREDECESSOR_BUILDER_SHA256 = (
    "43E662FE0D595BE6AAF77DCD75DE295C6E721BCFCE7F71466DB52014F0DD4E66"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "797D27314E8E168E1F2BACF9174E7246B83BF6DEDB0AC3B6C925D6D076CAC8C3"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "3B67EC38FCECCD9B9592A39C426EC14F64EF9354C608C176730460E2C37D8B6D"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "03D128438A4A79F1C4C59D46996D93E8DBD10ECAF707E18E0A46A0B3AF29A2F5"
)
EXPECTED_CLOSURE_BUILDER_SHA256 = (
    "F992EA2097355E25C4A6ADA68A8E49D99F3AB4CE85C36E753D654186E74205A0"
)
EXPECTED_CLOSURE_DECISIONS_SHA256 = (
    "F0EBDA5FC1154F9568CD802D1AA65BAD4FED0A082A41CC8E20959C3A9C263881"
)
EXPECTED_CLOSURE_EVIDENCE_SHA256 = (
    "9351D0782BC5CB2D0E473FC860B8081D9ADBC48BEDA3E82771D8AB5CBBFC500F"
)
EXPECTED_CLOSURE_COVERAGE_SHA256 = (
    "BA906DBF87D4CD07505DDCA10211D5644AA965919BB7E0B34927A88FCBFDC79C"
)
EXPECTED_CLOSURE_PROMOTION_SHA256 = (
    "078A00B34D17ACAB0C7B50D0215982769641A82E6D400E8BA4B47C9D8FD38323"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 6
EXPECTED_UNAFFECTED_ROWS = 52_797
EXPECTED_OWNER_ROWS = 6
EXPECTED_PROMOTIONS = 6
EXPECTED_RENEWALS = 0
EXPECTED_OVERRIDES = 3
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 3,
    "translation_override_and_runtime_promotion": 3,
}
EXPECTED_OWNER_CHUNK_COUNTS = {1: 6}
EXPECTED_PREDECESSOR_PENDING = 6_341
EXPECTED_FINAL_PENDING = 6_335
EXPECTED_PREDECESSOR_ELIGIBLE = 46_462
EXPECTED_FINAL_ELIGIBLE = 46_468
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 14_342
EXPECTED_FINAL_PK_PROMOTIONS = 14_348
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 29_993
EXPECTED_FINAL_PROMOTED_TOTAL = 29_999
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_REVIEWED_SITES = 59
EXPECTED_SOURCE_ONLY_SITES = 21
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "A6B026FA44E087F4166F09660CA8B997A282A783FDD18FE9702D8D6A1E88FE67"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = EXPECTED_DECISION_COORDINATE_SHA256
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "65B241E90B7268B91760D8907C50BD6BFDEFCECF0C811289703AD46AE5BCCA5B"
)
EXPECTED_REVIEWED_SITE_SHA256 = (
    "0E2C823877679AFA9F30F45C201B700B2B1D46ED1341164933943D59156E3371"
)
EXPECTED_SOURCE_ONLY_SITE_SHA256 = (
    "2395475C05879CC553B6D7D87001B3494E3A850CCDBD2AC2E7896475CAE59DDA"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "BCA693F86DEE850F95996243CB5FFA3DBA56A4F58750800FFE8253F9FC2ACFBB"
)
UPDATE_ACTION_FIELD = "selector742_consolidated_update_action"
EXPECTED_PRIVATE_OUTPUT_SHA256: str | None = (
    "4AC2CD8969958AA254D0F70F7302E1BC3D273229DBB59A0512FEB27E1786D90B"
)
EXPECTED_PUBLIC_OUTPUT_SHA256: str | None = (
    "D9A52A500BD6E60D3B35574E1890BFC128151A9328A5CAE8B1C4CFBEAB087E9B"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PREDECESSOR = load_module(PREDECESSOR_BUILDER_PATH, "selector742_checkpoint_base")
UPSTREAM = PREDECESSOR.PREVIOUS
BASE = PREDECESSOR.BASE
ORIGINAL_PATCH_PREDECESSOR_ROW = (
    PREDECESSOR.ORIGINAL_PATCH_PREDECESSOR_ROW
)


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
        setattr(PREDECESSOR, name, value)
    PREDECESSOR.configure_base()
    BASE.SCHEMA = (
        "nobu16.kr.pc-dialogue-runtime-vm-selector742-delta-checkpoint."
        "source-free.v1"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector742-consolidated-closure-decision.private.v1"
    )
    BASE.METHOD = (
        "post_selector760_selector742_single_coordinate_union_targeted_ledger_delta"
    )
    BASE.UPDATE_ACTION_FIELD = UPDATE_ACTION_FIELD
    BASE.EXACT_OVERRIDE_FIELD = "selector742_consolidated_exact_override_evidence"


def patch_predecessor_row(
    predecessor: dict[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    changed = ORIGINAL_PATCH_PREDECESSOR_ROW(predecessor, decision)
    verification = changed["runtime_vm_verification"]
    verification["schema"] = (
        "nobu16.kr.pk-selector742-consolidated-row-verification.v1"
    )
    verification["method"] = "reversed_vm_pk_selector742_consolidated_closure"
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
        "selector742_consolidated": {
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
        "selector760 targeted checkpoint base drifted",
    )
    configure_base()
    BASE.validate_closure_reports = UPSTREAM.validate_closure_reports
    BASE.patch_predecessor_row = patch_predecessor_row
    BASE.build_public_report = build_public_report
    decisions = BASE.load_closure_decisions()
    validate_confirmed_non_display(decisions)
    return BASE.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
