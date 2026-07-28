#!/usr/bin/env python3
"""Advance source-free progress with the targeted selector-748 delta."""

from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / WORKSTREAM.name

BASE_BUILDER_PATH = (
    WORKSTREAM / "build_progress_post_selector550_consolidated_delta_v1.py"
)
CHECKPOINT_BUILDER_PATH = (
    WORKSTREAM / "build_runtime_vm_post_selector748_consolidated_checkpoint_v1.py"
)
CHECKPOINT_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector748_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector748_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector748_consolidated_closure_decisions.private.v1.jsonl"
)
DEFAULT_PREDECESSOR_PROGRESS = (
    WORKSTREAM / "progress.post_selector550_consolidated.source_free.v1.json"
)
DEFAULT_PROGRESS_OUTPUT = WORKSTREAM / "progress.source_free.v1.json"

EXPECTED_BASE_BUILDER_SHA256 = (
    "6926CD3F376D37090206A753A5A1BF9917DDDB44C944035C1D17174AB89D43D8"
)
EXPECTED_PREDECESSOR_PROGRESS_SHA256 = (
    "A119995801D6A39ADFD35009DBBA152F3C50548F143ABDF2F2EFDEE314913EC7"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "F2CB7279F71D33CFA9D73BD4A6DA8E7E90692047F8ECF1D521FD70512D71846E"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "2120F85E7450E58667C784D0ED2035589E1E6674563B94A938545A51B9C573CC"
)
EXPECTED_CLOSURE_DECISIONS_SHA256 = (
    "35D4A9DF18F3BFC14866B5EEE52606D5BCF41282D0E400AD2B11284FD3C407AE"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "903B515128E94FE263430FAF7EECC51759A0DD132211F3C3047E5DAA6D16D9A6"
)
EXPECTED_CHECKPOINT_BUILDER_SHA256 = (
    "AA118738B65D91F902DED7C32C1C4F87CF9CB1B75ADA96D9FADB80724407BB97"
)
EXPECTED_CHECKPOINT_PRIVATE_SHA256 = (
    "05D9C79515E8B161CD469FFEC5C340F54BE9BB94BFBA8F725B8DFC025DE49E76"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256 = (
    "882781E1F51D963610A492589C19B6FAE09B33BA533D1369C26E9864AA48BAA7"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 147
EXPECTED_PROMOTIONS = 101
EXPECTED_RENEWALS = 46
EXPECTED_OVERRIDES = 99
EXPECTED_FINAL_PENDING = 6_879
EXPECTED_FINAL_ELIGIBLE = 45_924
EXPECTED_FINAL_PROMOTED_TOTAL = 29_455
EXPECTED_FINAL_PK_PROMOTIONS = 13_804
EXPECTED_FINAL_RETRANSLATED = 45_579
EXPECTED_CONFIRMED_NON_DISPLAY = 345

# Frozen after deterministic bootstrap.
EXPECTED_PROGRESS_OUTPUT_SHA256: str | None = (
    "C6378D2A78324BCE4E2AE3AD3FC1A2E9CEB512E32FA3F623B5E22D2A5E7D6F2C"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE_WRAPPER = load_module(BASE_BUILDER_PATH, "selector748_progress_base")
BASE = BASE_WRAPPER.BASE
ORIGINAL_CONFIGURE_BASE = BASE_WRAPPER.configure_base
ORIGINAL_BUILD_PROGRESS_DELTA = BASE_WRAPPER.build_progress_delta

BASE_WRAPPER.CHECKPOINT_BUILDER_PATH = CHECKPOINT_BUILDER_PATH
BASE_WRAPPER.CHECKPOINT_PRIVATE_PATH = CHECKPOINT_PRIVATE_PATH
BASE_WRAPPER.CHECKPOINT_PUBLIC_PATH = CHECKPOINT_PUBLIC_PATH
BASE_WRAPPER.CLOSURE_DECISIONS_PATH = CLOSURE_DECISIONS_PATH
BASE_WRAPPER.DEFAULT_PREDECESSOR_PROGRESS = DEFAULT_PREDECESSOR_PROGRESS
BASE_WRAPPER.DEFAULT_PROGRESS_OUTPUT = DEFAULT_PROGRESS_OUTPUT
BASE_WRAPPER.EXPECTED_PREDECESSOR_PROGRESS_SHA256 = (
    EXPECTED_PREDECESSOR_PROGRESS_SHA256
)
BASE_WRAPPER.EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    EXPECTED_PREDECESSOR_PRIVATE_SHA256
)
BASE_WRAPPER.EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    EXPECTED_PREDECESSOR_PUBLIC_SHA256
)
BASE_WRAPPER.EXPECTED_CLOSURE_DECISIONS_SHA256 = (
    EXPECTED_CLOSURE_DECISIONS_SHA256
)
BASE_WRAPPER.EXPECTED_FINAL_CANDIDATE_SHA256 = EXPECTED_FINAL_CANDIDATE_SHA256
BASE_WRAPPER.EXPECTED_CHECKPOINT_BUILDER_SHA256 = (
    EXPECTED_CHECKPOINT_BUILDER_SHA256
)
BASE_WRAPPER.EXPECTED_CHECKPOINT_PRIVATE_SHA256 = (
    EXPECTED_CHECKPOINT_PRIVATE_SHA256
)
BASE_WRAPPER.EXPECTED_CHECKPOINT_PUBLIC_SHA256 = (
    EXPECTED_CHECKPOINT_PUBLIC_SHA256
)
BASE_WRAPPER.EXPECTED_ROWS = EXPECTED_ROWS
BASE_WRAPPER.EXPECTED_DECISIONS = EXPECTED_DECISIONS
BASE_WRAPPER.EXPECTED_PROMOTIONS = EXPECTED_PROMOTIONS
BASE_WRAPPER.EXPECTED_RENEWALS = EXPECTED_RENEWALS
BASE_WRAPPER.EXPECTED_OVERRIDES = EXPECTED_OVERRIDES
BASE_WRAPPER.EXPECTED_FINAL_PENDING = EXPECTED_FINAL_PENDING
BASE_WRAPPER.EXPECTED_FINAL_ELIGIBLE = EXPECTED_FINAL_ELIGIBLE
BASE_WRAPPER.EXPECTED_FINAL_PROMOTED_TOTAL = EXPECTED_FINAL_PROMOTED_TOTAL
BASE_WRAPPER.EXPECTED_FINAL_PK_PROMOTIONS = EXPECTED_FINAL_PK_PROMOTIONS
BASE_WRAPPER.EXPECTED_FINAL_RETRANSLATED = EXPECTED_FINAL_RETRANSLATED
BASE_WRAPPER.EXPECTED_CONFIRMED_NON_DISPLAY = EXPECTED_CONFIRMED_NON_DISPLAY
BASE_WRAPPER.EXPECTED_PROGRESS_OUTPUT_SHA256 = EXPECTED_PROGRESS_OUTPUT_SHA256


def configure_base() -> None:
    ORIGINAL_CONFIGURE_BASE()
    BASE.EXPECTED_PROGRESS_OUTPUT_SHA256 = EXPECTED_PROGRESS_OUTPUT_SHA256


def validate_baseline_progress(progress: Mapping[str, Any]) -> None:
    totals = progress["totals"]
    scope = totals["scope_classification_counts"]
    integration = progress["runtime_vm_integration"]
    segments = progress["segments"]
    batches = progress["queue_batch_coverage"]
    BASE.require(
        progress.get("mechanical_candidate_universe") == EXPECTED_ROWS
        and totals.get("semantic_review_approved") == EXPECTED_ROWS
        and totals.get("runtime_review_pending") == 6_980
        and totals.get("fully_candidate_eligible") == 45_823
        and scope.get("retranslated") == 45_478
        and scope.get("confirmed_non_display") == EXPECTED_CONFIRMED_NON_DISPLAY
        and scope.get("runtime_fragment_pending") == 6_980
        and integration.get("sha256") == EXPECTED_PREDECESSOR_PUBLIC_SHA256
        and integration.get("private_integrated_decision_sha256")
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256
        and integration.get("promoted_total") == 29_354
        and integration.get("runtime_review_pending_after") == 6_980
        and integration.get("selector550_consolidated_layer_included") is True
        and sum(int(row["runtime_review_pending"]) for row in segments) == 6_980
        and sum(int(row["runtime_review_verified"]) for row in segments)
        == 29_354
        and sum(int(row["decision_count"]) for row in segments) == EXPECTED_ROWS
        and sum(int(row["runtime_review_pending"]) for row in batches) == 6_980
        and sum(int(row["fully_candidate_eligible"]) for row in batches)
        == 45_823
        and sum(int(row["decision_count"]) for row in batches) == EXPECTED_ROWS,
        "post-selector550 progress predecessor drifted",
    )


def build_progress_delta(
    baseline: Mapping[str, Any],
    checkpoint_report: Mapping[str, Any],
    promotions: set[str],
    target_segments: Mapping[str, str],
    target_batches: Mapping[str, str],
) -> dict[str, Any]:
    alias_report = copy.deepcopy(checkpoint_report)
    alias_report["selector550_consolidated"] = alias_report[
        "selector748_consolidated"
    ]
    baseline_integration = baseline["runtime_vm_integration"]
    old_layer = copy.deepcopy(baseline_integration["selector550_consolidated"])
    old_included = baseline_integration["selector550_consolidated_layer_included"]
    old_delta = copy.deepcopy(
        baseline_integration["selector550_targeted_progress_delta"]
    )
    old_exact = {
        key: copy.deepcopy(value)
        for key, value in baseline_integration["final_exact_layers"].items()
        if key.startswith("selector550_")
    }
    progress = ORIGINAL_BUILD_PROGRESS_DELTA(
        baseline,
        alias_report,
        promotions,
        target_segments,
        target_batches,
    )
    integration = progress["runtime_vm_integration"]
    new_layer = integration["selector550_consolidated"]
    new_delta = integration.pop("selector550_targeted_progress_delta")
    exact = integration["final_exact_layers"]
    new_exact = {
        key.replace("selector550_", "selector748_", 1): value
        for key, value in exact.items()
        if key.startswith("selector550_")
    }
    for key in list(exact):
        if key.startswith("selector550_"):
            del exact[key]
    exact.update(old_exact)
    exact.update(new_exact)
    integration["selector550_consolidated_layer_included"] = old_included
    integration["selector550_consolidated"] = old_layer
    integration["selector550_targeted_progress_delta"] = old_delta
    integration["selector748_consolidated_layer_included"] = True
    integration["selector748_consolidated"] = new_layer
    integration["selector748_targeted_progress_delta"] = new_delta
    return progress


def main(argv: Sequence[str] | None = None) -> int:
    BASE.require(
        BASE.sha256_file(BASE_BUILDER_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "selector550 progress delta base drifted",
    )
    configure_base()
    BASE.validate_baseline_progress = validate_baseline_progress
    BASE.build_progress_delta = build_progress_delta
    return BASE.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
