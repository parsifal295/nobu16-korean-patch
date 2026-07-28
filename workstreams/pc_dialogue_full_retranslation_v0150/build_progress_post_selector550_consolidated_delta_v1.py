#!/usr/bin/env python3
"""Advance source-free progress with the targeted selector-550 delta."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / WORKSTREAM.name

GENERIC_BUILDER_PATH = (
    WORKSTREAM / "build_progress_post_selector610_consolidated_delta_v1.py"
)
CHECKPOINT_BUILDER_PATH = (
    WORKSTREAM / "build_runtime_vm_post_selector550_consolidated_checkpoint_v1.py"
)
CHECKPOINT_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector550_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector550_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector550_consolidated_closure_decisions.private.v1.jsonl"
)
DEFAULT_PREDECESSOR_PROGRESS = (
    WORKSTREAM / "progress.post_selector610_consolidated.source_free.v1.json"
)
DEFAULT_PROGRESS_OUTPUT = WORKSTREAM / "progress.source_free.v1.json"

EXPECTED_GENERIC_BUILDER_SHA256 = (
    "C2DEBB0A5EEE13D3A5B3DF44CE65F5AAFEF65B093489895E6763EE5102D44704"
)
EXPECTED_PREDECESSOR_PROGRESS_SHA256 = (
    "03E827757D1D85282043A29B4B112A768D0B3E545245750A61273C1B8CDB83F4"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "0218C3D198C9930C8920ED8DAEB2DDD85987878035AC59DD5ECC8179D38DE12B"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "42BB33CD2F7553EE3E251DDD78933F85D181F140AA133C5843F6DBDF379B53D3"
)
EXPECTED_CLOSURE_DECISIONS_SHA256 = (
    "EAA8AB5A7B71532AC5E95C0C772C990AD05A9B9DFA0D2CCFDB3A813469F0F600"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "15C3BF1B4CC2E29020E5A8A6F40669555B54EEE57B04C3F7F77DF3AC680CFB93"
)
EXPECTED_CHECKPOINT_BUILDER_SHA256 = (
    "A5EB1AD4E2F5CF35E824C1F4131E2B99D10E6E3FFE6AAF50487FD50011AF8C4C"
)
EXPECTED_CHECKPOINT_PRIVATE_SHA256 = (
    "F2CB7279F71D33CFA9D73BD4A6DA8E7E90692047F8ECF1D521FD70512D71846E"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256 = (
    "2120F85E7450E58667C784D0ED2035589E1E6674563B94A938545A51B9C573CC"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 224
EXPECTED_PROMOTIONS = 121
EXPECTED_RENEWALS = 103
EXPECTED_OVERRIDES = 131
EXPECTED_FINAL_PENDING = 6_980
EXPECTED_FINAL_ELIGIBLE = 45_823
EXPECTED_FINAL_PROMOTED_TOTAL = 29_354
EXPECTED_FINAL_PK_PROMOTIONS = 13_703
EXPECTED_FINAL_RETRANSLATED = 45_478
EXPECTED_CONFIRMED_NON_DISPLAY = 345

# Frozen after deterministic bootstrap.
EXPECTED_PROGRESS_OUTPUT_SHA256: str | None = (
    "A119995801D6A39ADFD35009DBBA152F3C50548F143ABDF2F2EFDEE314913EC7"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_module(GENERIC_BUILDER_PATH, "selector550_progress_delta_base")
ORIGINAL_BUILD_PROGRESS_DELTA = BASE.build_progress_delta


def configure_base() -> None:
    BASE.CHECKPOINT_BUILDER_PATH = CHECKPOINT_BUILDER_PATH
    BASE.CHECKPOINT_PRIVATE_PATH = CHECKPOINT_PRIVATE_PATH
    BASE.CHECKPOINT_PUBLIC_PATH = CHECKPOINT_PUBLIC_PATH
    BASE.CLOSURE_DECISIONS_PATH = CLOSURE_DECISIONS_PATH
    BASE.DEFAULT_PREDECESSOR_PROGRESS = DEFAULT_PREDECESSOR_PROGRESS
    BASE.DEFAULT_PROGRESS_OUTPUT = DEFAULT_PROGRESS_OUTPUT
    BASE.EXPECTED_PREDECESSOR_PROGRESS_SHA256 = (
        EXPECTED_PREDECESSOR_PROGRESS_SHA256
    )
    BASE.EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
        EXPECTED_PREDECESSOR_PRIVATE_SHA256
    )
    BASE.EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
        EXPECTED_PREDECESSOR_PUBLIC_SHA256
    )
    BASE.EXPECTED_CLOSURE_DECISIONS_SHA256 = (
        EXPECTED_CLOSURE_DECISIONS_SHA256
    )
    BASE.EXPECTED_FINAL_CANDIDATE_SHA256 = EXPECTED_FINAL_CANDIDATE_SHA256
    BASE.EXPECTED_CHECKPOINT_BUILDER_SHA256 = (
        EXPECTED_CHECKPOINT_BUILDER_SHA256
    )
    BASE.EXPECTED_CHECKPOINT_PRIVATE_SHA256 = (
        EXPECTED_CHECKPOINT_PRIVATE_SHA256
    )
    BASE.EXPECTED_CHECKPOINT_PUBLIC_SHA256 = (
        EXPECTED_CHECKPOINT_PUBLIC_SHA256
    )
    BASE.EXPECTED_PROGRESS_OUTPUT_SHA256 = EXPECTED_PROGRESS_OUTPUT_SHA256
    BASE.EXPECTED_ROWS = EXPECTED_ROWS
    BASE.EXPECTED_DECISIONS = EXPECTED_DECISIONS
    BASE.EXPECTED_PROMOTIONS = EXPECTED_PROMOTIONS
    BASE.EXPECTED_RENEWALS = EXPECTED_RENEWALS
    BASE.EXPECTED_OVERRIDES = EXPECTED_OVERRIDES
    BASE.EXPECTED_FINAL_PENDING = EXPECTED_FINAL_PENDING
    BASE.EXPECTED_FINAL_ELIGIBLE = EXPECTED_FINAL_ELIGIBLE
    BASE.EXPECTED_FINAL_PROMOTED_TOTAL = EXPECTED_FINAL_PROMOTED_TOTAL
    BASE.EXPECTED_FINAL_PK_PROMOTIONS = EXPECTED_FINAL_PK_PROMOTIONS
    BASE.EXPECTED_FINAL_RETRANSLATED = EXPECTED_FINAL_RETRANSLATED
    BASE.EXPECTED_CONFIRMED_NON_DISPLAY = EXPECTED_CONFIRMED_NON_DISPLAY


def validate_baseline_progress(progress: Mapping[str, Any]) -> None:
    totals = progress["totals"]
    scope = totals["scope_classification_counts"]
    integration = progress["runtime_vm_integration"]
    segments = progress["segments"]
    batches = progress["queue_batch_coverage"]
    BASE.require(
        progress.get("mechanical_candidate_universe") == EXPECTED_ROWS
        and totals.get("semantic_review_approved") == EXPECTED_ROWS
        and totals.get("runtime_review_pending") == 7_101
        and totals.get("fully_candidate_eligible") == 45_702
        and scope.get("retranslated") == 45_357
        and scope.get("confirmed_non_display") == EXPECTED_CONFIRMED_NON_DISPLAY
        and scope.get("runtime_fragment_pending") == 7_101
        and integration.get("sha256") == EXPECTED_PREDECESSOR_PUBLIC_SHA256
        and integration.get("private_integrated_decision_sha256")
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256
        and integration.get("promoted_total") == 29_233
        and integration.get("runtime_review_pending_after") == 7_101
        and integration.get("selector610_consolidated_layer_included") is True
        and sum(int(row["runtime_review_pending"]) for row in segments) == 7_101
        and sum(int(row["runtime_review_verified"]) for row in segments) == 29_233
        and sum(int(row["decision_count"]) for row in segments) == EXPECTED_ROWS
        and sum(int(row["runtime_review_pending"]) for row in batches) == 7_101
        and sum(int(row["fully_candidate_eligible"]) for row in batches) == 45_702
        and sum(int(row["decision_count"]) for row in batches) == EXPECTED_ROWS,
        "post-selector610 progress predecessor drifted",
    )


def build_progress_delta(
    baseline: Mapping[str, Any],
    checkpoint_report: Mapping[str, Any],
    promotions: set[str],
    target_segments: Mapping[str, str],
    target_batches: Mapping[str, str],
) -> dict[str, Any]:
    alias_report = copy.deepcopy(checkpoint_report)
    alias_report["selector610_consolidated"] = alias_report[
        "selector550_consolidated"
    ]
    baseline_integration = baseline["runtime_vm_integration"]
    old_layer = copy.deepcopy(baseline_integration["selector610_consolidated"])
    old_included = baseline_integration["selector610_consolidated_layer_included"]
    old_delta = copy.deepcopy(
        baseline_integration["selector610_targeted_progress_delta"]
    )
    old_exact = {
        key: copy.deepcopy(value)
        for key, value in baseline_integration["final_exact_layers"].items()
        if key.startswith("selector610_")
    }
    progress = ORIGINAL_BUILD_PROGRESS_DELTA(
        baseline,
        alias_report,
        promotions,
        target_segments,
        target_batches,
    )
    integration = progress["runtime_vm_integration"]
    new_layer = integration["selector610_consolidated"]
    new_delta = integration.pop("selector610_targeted_progress_delta")
    exact = integration["final_exact_layers"]
    new_exact = {
        key.replace("selector610_", "selector550_", 1): value
        for key, value in exact.items()
        if key.startswith("selector610_")
    }
    for key in list(exact):
        if key.startswith("selector610_"):
            del exact[key]
    exact.update(old_exact)
    exact.update(new_exact)
    integration["selector610_consolidated_layer_included"] = old_included
    integration["selector610_consolidated"] = old_layer
    integration["selector610_targeted_progress_delta"] = old_delta
    integration["selector550_consolidated_layer_included"] = True
    integration["selector550_consolidated"] = new_layer
    integration["selector550_targeted_progress_delta"] = new_delta
    return progress


def main(argv: Sequence[str] | None = None) -> int:
    BASE.require(
        BASE.sha256_file(GENERIC_BUILDER_PATH) == EXPECTED_GENERIC_BUILDER_SHA256,
        "generic progress delta builder drifted",
    )
    configure_base()
    BASE.validate_baseline_progress = validate_baseline_progress
    BASE.build_progress_delta = build_progress_delta
    return BASE.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
