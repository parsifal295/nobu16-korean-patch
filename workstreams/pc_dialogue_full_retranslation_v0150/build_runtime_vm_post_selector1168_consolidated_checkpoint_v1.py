#!/usr/bin/env python3
"""Apply selector-1168 as a targeted immutable ledger delta."""

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
    WORKSTREAM / "build_runtime_vm_post_selector364_consolidated_checkpoint_v1.py"
)
PREDECESSOR_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector364_consolidated_checkpoint.private.v1.jsonl"
)
PREDECESSOR_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector364_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_BUILDER_PATH = (
    PK_AUDIT / "build_pk_selector1168_consolidated_closure_v1.py"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector1168_consolidated_closure_decisions.private.v1.jsonl"
)
CLOSURE_EVIDENCE_PATH = (
    DIALOGUE_TMP / "pk_selector1168_consolidated_closure_evidence.private.v1.json"
)
CLOSURE_COVERAGE_PATH = (
    PK_AUDIT / "public" / "pk_selector1168_consolidated_closure_coverage.v1.json"
)
CLOSURE_PROMOTION_PATH = (
    PK_AUDIT / "public" / "pk_selector1168_consolidated_closure_promotion.v1.json"
)
DEFAULT_PRIVATE_OUTPUT = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1168_consolidated_checkpoint.private.v1.jsonl"
)
DEFAULT_PUBLIC_OUTPUT = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector1168_consolidated_checkpoint.source_free.v1.json"
)

EXPECTED_PREDECESSOR_BUILDER_SHA256 = (
    "F558B83A63EF8BD3C5E21EF104A0ECDE63219B753415FC81EA7627FD22B81484"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "B776FEF076BC8A466D02F7A8C3624A2BC1EF52012306715A7FF083CF1F53FBD5"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "6FBC581903028C5DE82B53368310D730F47CF408F59685BAA6310F6E62663680"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "6F3880DF9105F47402378E89E9C1ADE9599C052CAEC6EE3D7CC795333C04C7DE"
)

# Frozen from the selector-1168 closure.
EXPECTED_CLOSURE_BUILDER_SHA256 = (
    "22B574A57E38BD068689D1FEDF39CEB9FE18C11A66A5360AC25774F741BF6D90"
)
EXPECTED_CLOSURE_DECISIONS_SHA256 = (
    "37402EE773B331D48C957C8C2AA3EED55FA582726BC98EA5F9BECBF87AD153AE"
)
EXPECTED_CLOSURE_EVIDENCE_SHA256 = (
    "D16D23F204D82F926CB0E6304928BD8F852FE2F6AB8B8437F80130A1889C2CEF"
)
EXPECTED_CLOSURE_COVERAGE_SHA256 = (
    "F929792EEA4C3B1B7F4F65C5F498C01437DA24A7812AC2B41B29B13806D53E38"
)
EXPECTED_CLOSURE_PROMOTION_SHA256 = (
    "D6BEC8BFCD19B0E75FFD0BDC491980528EF6FDBF92C7CD061D19093E1A782F2F"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "EF84A8B8A18C1F2F1F72D3A650C01DC7B058F32A3536C130809C4FCB31C837C7"
)
EXPECTED_DECISION_COORDINATE_SHA256 = (
    "9EAE219F77866334A2B88A574EA5928735DE735CED27046DD9114B232ABE6C0B"
)
EXPECTED_PROMOTION_COORDINATE_SHA256 = (
    "9EAE219F77866334A2B88A574EA5928735DE735CED27046DD9114B232ABE6C0B"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "6B1B9A5804093507073303CF67C69FC3ECA09F1F828EF199002615B6D6B0977A"
)
EXPECTED_PRIVATE_OUTPUT_SHA256 = (
    "56FBAF8FB54CCFA7EAF10355F66FE6A730374804F48FB4CD9F8F15A99AEE9A91"
)
EXPECTED_PUBLIC_OUTPUT_SHA256 = (
    "9A04C999B850A1024BBB9AE57F509CA1C879A5DC4D59BF717873FD17E609545F"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 19
EXPECTED_UNAFFECTED_ROWS = 52_784
EXPECTED_OWNER_ROWS = 19
EXPECTED_PROMOTIONS = 19
EXPECTED_RENEWALS = 0
EXPECTED_OVERRIDES = 5
EXPECTED_ACTION_COUNTS = {
    "runtime_promotion": 14,
    "translation_override_and_runtime_promotion": 5,
}
EXPECTED_OWNER_CHUNK_COUNTS = {0: 15, 1: 4}
EXPECTED_PREDECESSOR_PENDING = 6_302
EXPECTED_FINAL_PENDING = 6_283
EXPECTED_PREDECESSOR_ELIGIBLE = 46_501
EXPECTED_FINAL_ELIGIBLE = 46_520
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 14_381
EXPECTED_FINAL_PK_PROMOTIONS = 14_400
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 30_032
EXPECTED_FINAL_PROMOTED_TOTAL = 30_051
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_REVIEWED_SITES = 53
EXPECTED_SOURCE_ONLY_SITES = 5
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EXPECTED_REVIEWED_SITE_SHA256 = (
    "5B250420F71B3E9A0BEBB3476A7BAF45BA7B99D913F783148D753D5A2676EF3B"
)
EXPECTED_SOURCE_ONLY_SITE_SHA256 = (
    "D4362787134108F376BAF902DD0FE5ED45FA36DA10ACEA74CBE2D8941620868D"
)
UPDATE_ACTION_FIELD = "selector1168_consolidated_update_action"


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PREDECESSOR = load_module(
    PREDECESSOR_BUILDER_PATH, "selector1168_checkpoint_base"
)
UPSTREAM = PREDECESSOR.UPSTREAM
BASE = PREDECESSOR.BASE
ORIGINAL_PATCH_PREDECESSOR_ROW = PREDECESSOR.ORIGINAL_PATCH_PREDECESSOR_ROW


def unresolved_pins() -> list[str]:
    names = (
        "EXPECTED_CLOSURE_BUILDER_SHA256",
        "EXPECTED_CLOSURE_DECISIONS_SHA256",
        "EXPECTED_CLOSURE_EVIDENCE_SHA256",
        "EXPECTED_CLOSURE_COVERAGE_SHA256",
        "EXPECTED_CLOSURE_PROMOTION_SHA256",
        "EXPECTED_FINAL_CANDIDATE_SHA256",
        "EXPECTED_DECISION_COORDINATE_SHA256",
        "EXPECTED_PROMOTION_COORDINATE_SHA256",
        "EXPECTED_OVERRIDE_COORDINATE_SHA256",
        "EXPECTED_PRIVATE_OUTPUT_SHA256",
        "EXPECTED_PUBLIC_OUTPUT_SHA256",
    )
    return [name for name in names if globals()[name] is None]


def is_frozen() -> bool:
    return not unresolved_pins()


def configure_base() -> None:
    names = (
        "PREDECESSOR_PRIVATE_PATH",
        "PREDECESSOR_PUBLIC_PATH",
        "CLOSURE_BUILDER_PATH",
        "CLOSURE_DECISIONS_PATH",
        "CLOSURE_EVIDENCE_PATH",
        "CLOSURE_COVERAGE_PATH",
        "CLOSURE_PROMOTION_PATH",
        "DEFAULT_PRIVATE_OUTPUT",
        "DEFAULT_PUBLIC_OUTPUT",
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
        "EXPECTED_CONFIRMED_NON_DISPLAY",
        "EXPECTED_REVIEWED_SITES",
        "EXPECTED_SOURCE_ONLY_SITES",
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
        "UPDATE_ACTION_FIELD",
    )
    for name in names:
        setattr(PREDECESSOR, name, globals()[name])
    PREDECESSOR.configure_base()
    BASE.SCHEMA = (
        "nobu16.kr.pc-dialogue-runtime-vm-selector1168-delta-checkpoint."
        "source-free.v1"
    )
    BASE.PRIVATE_DECISION_SCHEMA = (
        "nobu16.kr.pk-selector1168-consolidated-closure-decision.private.v1"
    )
    BASE.METHOD = (
        "post_selector364_selector1168_single_coordinate_union_"
        "targeted_ledger_delta"
    )
    BASE.UPDATE_ACTION_FIELD = UPDATE_ACTION_FIELD
    BASE.EXACT_OVERRIDE_FIELD = (
        "selector1168_consolidated_exact_override_evidence"
    )


def patch_predecessor_row(
    predecessor: dict[str, Any],
    decision: Mapping[str, Any],
) -> dict[str, Any]:
    changed = ORIGINAL_PATCH_PREDECESSOR_ROW(predecessor, decision)
    verification = changed["runtime_vm_verification"]
    verification["schema"] = (
        "nobu16.kr.pk-selector1168-consolidated-row-verification.v1"
    )
    verification["method"] = "reversed_vm_pk_selector1168_consolidated_closure"
    return changed


def build_public_report(
    private_sha256: str,
    stream_result: Mapping[str, Any],
) -> dict[str, Any]:
    report = PREDECESSOR.build_public_report(private_sha256, stream_result)
    report["selector1168_consolidated"] = report.pop(
        "selector364_consolidated"
    )
    return report


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
    blocking_pins = [
        name
        for name in unresolved_pins()
        if name
        not in {
            "EXPECTED_PRIVATE_OUTPUT_SHA256",
            "EXPECTED_PUBLIC_OUTPUT_SHA256",
        }
    ]
    BASE.require(
        not blocking_pins,
        "selector1168 targeted checkpoint input pins unresolved: "
        + ",".join(blocking_pins),
    )
    BASE.require(
        BASE.sha256_file(PREDECESSOR_BUILDER_PATH)
        == EXPECTED_PREDECESSOR_BUILDER_SHA256,
        "selector364 targeted checkpoint base drifted",
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
