#!/usr/bin/env python3
"""Advance source-free progress with the targeted selector-514 delta."""

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
    WORKSTREAM / "build_progress_post_selector142_consolidated_delta_v1.py"
)
CHECKPOINT_BUILDER_PATH = (
    WORKSTREAM / "build_runtime_vm_post_selector514_consolidated_checkpoint_v1.py"
)
CHECKPOINT_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector514_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector514_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector514_consolidated_closure_decisions.private.v1.jsonl"
)
PREDECESSOR_SOURCE_PATH = WORKSTREAM / "progress.source_free.v1.json"
DEFAULT_PREDECESSOR_PROGRESS = (
    WORKSTREAM / "progress.post_selector142_consolidated.source_free.v1.json"
)
DEFAULT_PROGRESS_OUTPUT = WORKSTREAM / "progress.source_free.v1.json"
IMMUTABLE_PROGRESS_OUTPUT = (
    WORKSTREAM / "progress.post_selector514_consolidated.source_free.v1.json"
)

EXPECTED_BASE_BUILDER_SHA256 = (
    "C3C23943CA28F0905C592ACEF81DF2A4AC632FB26E5F59629D9B5AD1836BF91D"
)
EXPECTED_PREDECESSOR_PROGRESS_SHA256 = (
    "EC0FEE21DE4431A4F6B19FA15CEF3A9257EAFA0CEFCCC720E5E93CAB04B83D81"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "5D3673BC67F8FB55B258BB236CBC6ACD3E76F2E001300994ED7AFD742601C0DB"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "FB3119A8080949EDC0BA740E893C4C4B387FF8BC6564E6E4C1B19A3DC8D9A919"
)
EXPECTED_CLOSURE_DECISIONS_SHA256 = (
    "9934DEDCE404E2F27EE6680BF43E2B4E8E7870FE6F728E96D09DF566529F1444"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "623C6EE2BDC25B13680C353C97847C3AC646C4B2B222A51F0F242B7A1CC2E093"
)
EXPECTED_CHECKPOINT_BUILDER_SHA256 = (
    "6E71DF57BD30B9C9372535438C25AB10A8A805FF54BCB476DBDBBB3CB34B3682"
)
EXPECTED_CHECKPOINT_PRIVATE_SHA256 = (
    "FCAB3A5CACEEAE4C610BD284D8C0631E65DA14562DB7B78A66655554EED07A79"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256 = (
    "49BB13AF414DA7A751F7B9CA9830386A3832FF99411B4FC39DC96F94FE649100"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 108
EXPECTED_PROMOTIONS = 98
EXPECTED_RENEWALS = 10
EXPECTED_OVERRIDES = 29
EXPECTED_FINAL_PENDING = 6_547
EXPECTED_FINAL_ELIGIBLE = 46_256
EXPECTED_FINAL_PROMOTED_TOTAL = 29_787
EXPECTED_FINAL_PK_PROMOTIONS = 14_136
EXPECTED_FINAL_RETRANSLATED = 45_911
EXPECTED_CONFIRMED_NON_DISPLAY = 345

# Frozen after deterministic bootstrap.
EXPECTED_PROGRESS_OUTPUT_SHA256: str | None = (
    "C40A71C8CA87B8B13600C05115D9831220151AA5847B580ED7A0A064F9CD9B4D"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


OUTER = load_module(BASE_BUILDER_PATH, "selector514_progress_base")
INNER = OUTER.INNER
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
    setattr(OUTER, _name, globals()[_name])
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
        and totals.get("runtime_review_pending") == 6_645
        and totals.get("fully_candidate_eligible") == 46_158
        and scope.get("retranslated") == 45_813
        and scope.get("confirmed_non_display") == EXPECTED_CONFIRMED_NON_DISPLAY
        and scope.get("runtime_fragment_pending") == 6_645
        and integration.get("sha256") == EXPECTED_PREDECESSOR_PUBLIC_SHA256
        and integration.get("private_integrated_decision_sha256")
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256
        and integration.get("promoted_total") == 29_689
        and integration.get("runtime_review_pending_after") == 6_645
        and integration.get("selector142_consolidated_layer_included") is True
        and sum(int(row["runtime_review_pending"]) for row in segments) == 6_645
        and sum(int(row["runtime_review_verified"]) for row in segments)
        == 29_689
        and sum(int(row["decision_count"]) for row in segments) == EXPECTED_ROWS
        and sum(int(row["runtime_review_pending"]) for row in batches) == 6_645
        and sum(int(row["fully_candidate_eligible"]) for row in batches)
        == 46_158
        and sum(int(row["decision_count"]) for row in batches) == EXPECTED_ROWS,
        "post-selector142 progress predecessor drifted",
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
        "selector514_consolidated"
    ]
    baseline_integration = baseline["runtime_vm_integration"]
    preserved = {
        key: copy.deepcopy(value)
        for key, value in baseline_integration.items()
        if key.startswith(("selector550_", "selector748_", "selector142_"))
    }
    preserved_exact = {
        key: copy.deepcopy(value)
        for key, value in baseline_integration["final_exact_layers"].items()
        if key.startswith(("selector550_", "selector748_", "selector142_"))
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
        key.replace("selector550_", "selector514_", 1): value
        for key, value in exact.items()
        if key.startswith("selector550_")
    }
    for key in list(exact):
        if key.startswith(
            ("selector550_", "selector748_", "selector142_")
        ):
            del exact[key]
    exact.update(preserved_exact)
    exact.update(new_exact)
    integration.update(preserved)
    integration["selector514_consolidated_layer_included"] = True
    integration["selector514_consolidated"] = new_layer
    integration["selector514_targeted_progress_delta"] = new_delta
    return progress


def main(argv: Sequence[str] | None = None) -> int:
    BASE.require(
        BASE.sha256_file(BASE_BUILDER_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "selector142 progress delta base drifted",
    )
    BASE.require(
        BASE.sha256_file(DEFAULT_PREDECESSOR_PROGRESS)
        == EXPECTED_PREDECESSOR_PROGRESS_SHA256,
        "post-selector142 progress snapshot drifted",
    )
    configure_base()
    BASE.validate_baseline_progress = validate_baseline_progress
    BASE.build_progress_delta = build_progress_delta
    result = BASE.main(argv)
    arguments = tuple(sys.argv[1:] if argv is None else argv)
    if "--write" in arguments:
        BASE.atomic_write(
            IMMUTABLE_PROGRESS_OUTPUT,
            DEFAULT_PROGRESS_OUTPUT.read_bytes(),
        )
    if EXPECTED_PROGRESS_OUTPUT_SHA256 is not None:
        BASE.require(
            BASE.sha256_file(DEFAULT_PROGRESS_OUTPUT)
            == EXPECTED_PROGRESS_OUTPUT_SHA256
            and BASE.sha256_file(IMMUTABLE_PROGRESS_OUTPUT)
            == EXPECTED_PROGRESS_OUTPUT_SHA256,
            "post-selector514 progress alias drifted",
        )
    return result


if __name__ == "__main__":
    raise SystemExit(main())
