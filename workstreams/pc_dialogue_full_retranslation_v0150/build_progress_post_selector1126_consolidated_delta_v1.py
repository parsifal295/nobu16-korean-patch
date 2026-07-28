#!/usr/bin/env python3
"""Advance source-free progress with the targeted selector-1126 delta."""

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
    WORKSTREAM / "build_progress_post_selector748_consolidated_delta_v1.py"
)
CHECKPOINT_BUILDER_PATH = (
    WORKSTREAM / "build_runtime_vm_post_selector1126_consolidated_checkpoint_v1.py"
)
CHECKPOINT_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1126_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector1126_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector1126_consolidated_closure_decisions.private.v1.jsonl"
)
DEFAULT_PREDECESSOR_PROGRESS = WORKSTREAM / "progress.source_free.v1.json"
DEFAULT_PROGRESS_OUTPUT = (
    WORKSTREAM / "progress.post_selector1126_consolidated.source_free.v1.json"
)

EXPECTED_BASE_BUILDER_SHA256 = (
    "B5C63849A9F2A26CE7B6FA3BE2057A5F397267F6480F6FE9E1F9932DE3438BD1"
)
EXPECTED_PREDECESSOR_PROGRESS_SHA256 = (
    "C6378D2A78324BCE4E2AE3AD3FC1A2E9CEB512E32FA3F623B5E22D2A5E7D6F2C"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "05D9C79515E8B161CD469FFEC5C340F54BE9BB94BFBA8F725B8DFC025DE49E76"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "882781E1F51D963610A492589C19B6FAE09B33BA533D1369C26E9864AA48BAA7"
)
EXPECTED_CLOSURE_DECISIONS_SHA256 = (
    "E7FE1D70A6DF175C25D3D4D42359983E26075F1962B8F0EB6BD52DC82376EB15"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "B25D15DB919FC4E3CF3A68E7C10938F581C233F04DA111F1C8D0ECA0A3F86D62"
)
EXPECTED_CHECKPOINT_BUILDER_SHA256 = (
    "BB481F5E4653E771279CDC5D4DF23769BDCE28D5B2D85D8BA8B8224B78428325"
)
EXPECTED_CHECKPOINT_PRIVATE_SHA256 = (
    "3198DC9F7A06809636D0C43F5740A65B5D4C50E7226D53AA7C52B7D893EFA06E"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256 = (
    "BD38D0EE71B59ADFEB8146760B91E82A7E09604E17B770760F13C94CB32704A5"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 185
EXPECTED_PROMOTIONS = 118
EXPECTED_RENEWALS = 67
EXPECTED_OVERRIDES = 140
EXPECTED_FINAL_PENDING = 6_761
EXPECTED_FINAL_ELIGIBLE = 46_042
EXPECTED_FINAL_PROMOTED_TOTAL = 29_573
EXPECTED_FINAL_PK_PROMOTIONS = 13_922
EXPECTED_FINAL_RETRANSLATED = 45_697
EXPECTED_CONFIRMED_NON_DISPLAY = 345

# Frozen after deterministic bootstrap.
EXPECTED_PROGRESS_OUTPUT_SHA256: str | None = (
    "657F474E3D4BCF487A51162D0738D620ED49FB27B58BA2A1B77771F98E4D69EB"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


OUTER = load_module(BASE_BUILDER_PATH, "selector1126_progress_base")
INNER = OUTER.BASE_WRAPPER
BASE = OUTER.BASE
ORIGINAL_CONFIGURE_BASE = OUTER.ORIGINAL_CONFIGURE_BASE
ORIGINAL_BUILD_PROGRESS_DELTA = OUTER.ORIGINAL_BUILD_PROGRESS_DELTA

for _name in (
    "CHECKPOINT_BUILDER_PATH",
    "CHECKPOINT_PRIVATE_PATH",
    "CHECKPOINT_PUBLIC_PATH",
    "CLOSURE_DECISIONS_PATH",
    "DEFAULT_PREDECESSOR_PROGRESS",
    "DEFAULT_PROGRESS_OUTPUT",
    "EXPECTED_PREDECESSOR_PROGRESS_SHA256",
    "EXPECTED_PREDECESSOR_PRIVATE_SHA256",
    "EXPECTED_PREDECESSOR_PUBLIC_SHA256",
    "EXPECTED_CLOSURE_DECISIONS_SHA256",
    "EXPECTED_FINAL_CANDIDATE_SHA256",
    "EXPECTED_CHECKPOINT_BUILDER_SHA256",
    "EXPECTED_CHECKPOINT_PRIVATE_SHA256",
    "EXPECTED_CHECKPOINT_PUBLIC_SHA256",
    "EXPECTED_ROWS",
    "EXPECTED_DECISIONS",
    "EXPECTED_PROMOTIONS",
    "EXPECTED_RENEWALS",
    "EXPECTED_OVERRIDES",
    "EXPECTED_FINAL_PENDING",
    "EXPECTED_FINAL_ELIGIBLE",
    "EXPECTED_FINAL_PROMOTED_TOTAL",
    "EXPECTED_FINAL_PK_PROMOTIONS",
    "EXPECTED_FINAL_RETRANSLATED",
    "EXPECTED_CONFIRMED_NON_DISPLAY",
    "EXPECTED_PROGRESS_OUTPUT_SHA256",
):
    setattr(INNER, _name, globals()[_name])


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
        and totals.get("runtime_review_pending") == 6_879
        and totals.get("fully_candidate_eligible") == 45_924
        and scope.get("retranslated") == 45_579
        and scope.get("confirmed_non_display") == EXPECTED_CONFIRMED_NON_DISPLAY
        and scope.get("runtime_fragment_pending") == 6_879
        and integration.get("sha256") == EXPECTED_PREDECESSOR_PUBLIC_SHA256
        and integration.get("private_integrated_decision_sha256")
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256
        and integration.get("promoted_total") == 29_455
        and integration.get("runtime_review_pending_after") == 6_879
        and integration.get("selector748_consolidated_layer_included") is True
        and sum(int(row["runtime_review_pending"]) for row in segments) == 6_879
        and sum(int(row["runtime_review_verified"]) for row in segments)
        == 29_455
        and sum(int(row["decision_count"]) for row in segments) == EXPECTED_ROWS
        and sum(int(row["runtime_review_pending"]) for row in batches) == 6_879
        and sum(int(row["fully_candidate_eligible"]) for row in batches)
        == 45_924
        and sum(int(row["decision_count"]) for row in batches) == EXPECTED_ROWS,
        "post-selector748 progress predecessor drifted",
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
        "selector1126_consolidated"
    ]
    baseline_integration = baseline["runtime_vm_integration"]
    preserved = {
        key: copy.deepcopy(value)
        for key, value in baseline_integration.items()
        if key.startswith("selector550_") or key.startswith("selector748_")
    }
    preserved_exact = {
        key: copy.deepcopy(value)
        for key, value in baseline_integration["final_exact_layers"].items()
        if key.startswith("selector550_") or key.startswith("selector748_")
    }
    progress = ORIGINAL_BUILD_PROGRESS_DELTA(
        baseline,
        alias_report,
        promotions,
        target_segments,
        target_batches,
    )
    integration = progress["runtime_vm_integration"]
    new_layer = integration.pop("selector550_consolidated")
    new_delta = integration.pop("selector550_targeted_progress_delta")
    exact = integration["final_exact_layers"]
    new_exact = {
        key.replace("selector550_", "selector1126_", 1): value
        for key, value in exact.items()
        if key.startswith("selector550_")
    }
    for key in list(exact):
        if key.startswith("selector550_") or key.startswith("selector748_"):
            del exact[key]
    exact.update(preserved_exact)
    exact.update(new_exact)
    integration.update(preserved)
    integration["selector1126_consolidated_layer_included"] = True
    integration["selector1126_consolidated"] = new_layer
    integration["selector1126_targeted_progress_delta"] = new_delta
    return progress


def main(argv: Sequence[str] | None = None) -> int:
    BASE.require(
        BASE.sha256_file(BASE_BUILDER_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "selector748 progress delta base drifted",
    )
    configure_base()
    BASE.validate_baseline_progress = validate_baseline_progress
    BASE.build_progress_delta = build_progress_delta
    return BASE.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
