#!/usr/bin/env python3
"""Advance source-free progress with the targeted selector-1162 delta."""

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
    WORKSTREAM / "build_progress_post_selector322_consolidated_delta_v1.py"
)
CHECKPOINT_BUILDER_PATH = (
    WORKSTREAM / "build_runtime_vm_post_selector1162_consolidated_checkpoint_v1.py"
)
CHECKPOINT_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1162_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector1162_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector1162_consolidated_closure_decisions.private.v1.jsonl"
)
DEFAULT_PREDECESSOR_PROGRESS = (
    WORKSTREAM / "progress.post_selector322_consolidated.source_free.v1.json"
)
DEFAULT_PROGRESS_OUTPUT = WORKSTREAM / "progress.source_free.v1.json"
IMMUTABLE_PROGRESS_OUTPUT = (
    WORKSTREAM / "progress.post_selector1162_consolidated.source_free.v1.json"
)

EXPECTED_BASE_BUILDER_SHA256 = (
    "8265A734139091151F0B6CA0E246669C9E7B89DF974A814BF6400BD32E396FE9"
)
EXPECTED_PREDECESSOR_PROGRESS_SHA256 = (
    "AEBCAE97B9794EC527C698E93B1D2F659F55CAFE1E0760B0F2FE1AD9C320070F"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "9A7E135544FA2F2A02A0D2B4941159CB92A3E4A495AF72B6CB335DE371351343"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "3C245CE82733F50F08E61B05A165B1038C4D5BBA5D3DAD38D46933B392101642"
)
EXPECTED_CLOSURE_DECISIONS_SHA256 = (
    "61E3E983D040461169FC989BB9F54BA67E4031CCF0CF49A411B0FB41CFC8BD37"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "94FE58C283D696DA36E0F6ADB8339713A0211163EDCD6FD0A92EB5110AE613D2"
)
EXPECTED_CHECKPOINT_BUILDER_SHA256 = (
    "8D3BD60AA4F593057BF76FBD033E17C238843C1A499CA8A8DBA232AA876E6678"
)
EXPECTED_CHECKPOINT_PRIVATE_SHA256 = (
    "A3A5433CCDD5F085AF61BEDB0409B5A02C7CAD162AD4ADE5938B356C988065B4"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256 = (
    "E063AF9F3681DA84315A4596F43EE6ED8F5FC368D4D712A96DD2B1BFEA1031D7"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 3
EXPECTED_PROMOTIONS = 3
EXPECTED_RENEWALS = 0
EXPECTED_OVERRIDES = 1
EXPECTED_FINAL_PENDING = 6_307
EXPECTED_FINAL_ELIGIBLE = 46_496
EXPECTED_FINAL_PROMOTED_TOTAL = 30_027
EXPECTED_FINAL_PK_PROMOTIONS = 14_376
EXPECTED_FINAL_RETRANSLATED = 46_151
EXPECTED_CONFIRMED_NON_DISPLAY = 345

EXPECTED_PROGRESS_OUTPUT_SHA256: str | None = (
    "98316D642D898EDED9A5E00D912A3F4CBA0A05821BE27E3FA23486C74E11610B"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PREVIOUS = load_module(BASE_BUILDER_PATH, "selector1162_progress_base")
BASE = PREVIOUS.BASE
ORIGINAL_BASE_LOAD_MODULE = BASE.load_module


def load_checkpoint_compat(name: str, path: Path) -> Any:
    module = ORIGINAL_BASE_LOAD_MODULE(name, path)
    if path.resolve() == CHECKPOINT_BUILDER_PATH.resolve():
        module.configure_base()
        module.load_closure_decisions = module.BASE.load_closure_decisions
    return module


def configure_base() -> None:
    PREVIOUS.configure_base()
    for name, value in {
        "CHECKPOINT_BUILDER_PATH": CHECKPOINT_BUILDER_PATH,
        "CHECKPOINT_PRIVATE_PATH": CHECKPOINT_PRIVATE_PATH,
        "CHECKPOINT_PUBLIC_PATH": CHECKPOINT_PUBLIC_PATH,
        "CLOSURE_DECISIONS_PATH": CLOSURE_DECISIONS_PATH,
        "DEFAULT_PREDECESSOR_PROGRESS": DEFAULT_PREDECESSOR_PROGRESS,
        "DEFAULT_PROGRESS_OUTPUT": DEFAULT_PROGRESS_OUTPUT,
        "EXPECTED_PREDECESSOR_PROGRESS_SHA256":
            EXPECTED_PREDECESSOR_PROGRESS_SHA256,
        "EXPECTED_PREDECESSOR_PRIVATE_SHA256":
            EXPECTED_PREDECESSOR_PRIVATE_SHA256,
        "EXPECTED_PREDECESSOR_PUBLIC_SHA256":
            EXPECTED_PREDECESSOR_PUBLIC_SHA256,
        "EXPECTED_CLOSURE_DECISIONS_SHA256":
            EXPECTED_CLOSURE_DECISIONS_SHA256,
        "EXPECTED_FINAL_CANDIDATE_SHA256": EXPECTED_FINAL_CANDIDATE_SHA256,
        "EXPECTED_CHECKPOINT_BUILDER_SHA256":
            EXPECTED_CHECKPOINT_BUILDER_SHA256,
        "EXPECTED_CHECKPOINT_PRIVATE_SHA256":
            EXPECTED_CHECKPOINT_PRIVATE_SHA256,
        "EXPECTED_CHECKPOINT_PUBLIC_SHA256":
            EXPECTED_CHECKPOINT_PUBLIC_SHA256,
        "EXPECTED_ROWS": EXPECTED_ROWS,
        "EXPECTED_DECISIONS": EXPECTED_DECISIONS,
        "EXPECTED_PROMOTIONS": EXPECTED_PROMOTIONS,
        "EXPECTED_RENEWALS": EXPECTED_RENEWALS,
        "EXPECTED_OVERRIDES": EXPECTED_OVERRIDES,
        "EXPECTED_FINAL_PENDING": EXPECTED_FINAL_PENDING,
        "EXPECTED_FINAL_ELIGIBLE": EXPECTED_FINAL_ELIGIBLE,
        "EXPECTED_FINAL_PROMOTED_TOTAL": EXPECTED_FINAL_PROMOTED_TOTAL,
        "EXPECTED_FINAL_PK_PROMOTIONS": EXPECTED_FINAL_PK_PROMOTIONS,
        "EXPECTED_FINAL_RETRANSLATED": EXPECTED_FINAL_RETRANSLATED,
        "EXPECTED_CONFIRMED_NON_DISPLAY": EXPECTED_CONFIRMED_NON_DISPLAY,
        "EXPECTED_PROGRESS_OUTPUT_SHA256": EXPECTED_PROGRESS_OUTPUT_SHA256,
    }.items():
        setattr(BASE, name, value)


def validate_baseline_progress(progress: Mapping[str, Any]) -> None:
    totals = progress["totals"]
    scope = totals["scope_classification_counts"]
    integration = progress["runtime_vm_integration"]
    segments = progress["segments"]
    batches = progress["queue_batch_coverage"]
    BASE.require(
        progress.get("mechanical_candidate_universe") == EXPECTED_ROWS
        and totals.get("semantic_review_approved") == EXPECTED_ROWS
        and totals.get("runtime_review_pending") == 6_310
        and totals.get("fully_candidate_eligible") == 46_493
        and scope.get("retranslated") == 46_148
        and scope.get("confirmed_non_display") == 345
        and scope.get("runtime_fragment_pending") == 6_310
        and integration.get("sha256") == EXPECTED_PREDECESSOR_PUBLIC_SHA256
        and integration.get("private_integrated_decision_sha256")
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256
        and integration.get("promoted_total") == 30_024
        and integration.get("runtime_review_pending_after") == 6_310
        and integration.get("selector322_consolidated_layer_included") is True
        and sum(int(row["runtime_review_pending"]) for row in segments) == 6_310
        and sum(int(row["runtime_review_verified"]) for row in segments)
        == 30_024
        and sum(int(row["decision_count"]) for row in segments) == EXPECTED_ROWS
        and sum(int(row["runtime_review_pending"]) for row in batches) == 6_310
        and sum(int(row["fully_candidate_eligible"]) for row in batches)
        == 46_493
        and sum(int(row["decision_count"]) for row in batches) == EXPECTED_ROWS,
        "post-selector322 progress predecessor drifted",
    )


def build_progress_delta(
    baseline: Mapping[str, Any],
    checkpoint_report: Mapping[str, Any],
    promotions: set[str],
    target_segments: Mapping[str, str],
    target_batches: Mapping[str, str],
) -> dict[str, Any]:
    alias_report = copy.deepcopy(checkpoint_report)
    alias_report["selector322_consolidated"] = alias_report[
        "selector1162_consolidated"
    ]
    baseline_integration = baseline["runtime_vm_integration"]
    preserved = {
        key: copy.deepcopy(value)
        for key, value in baseline_integration.items()
        if key.startswith("selector")
    }
    preserved_exact = copy.deepcopy(baseline_integration["final_exact_layers"])
    progress = PREVIOUS.build_progress_delta(
        baseline,
        alias_report,
        promotions,
        target_segments,
        target_batches,
    )
    integration = progress["runtime_vm_integration"]
    new_layer = copy.deepcopy(integration["selector322_consolidated"])
    new_delta = copy.deepcopy(integration["selector322_targeted_progress_delta"])
    exact = integration["final_exact_layers"]
    new_exact = {
        key.replace("selector322_", "selector1162_", 1): copy.deepcopy(value)
        for key, value in exact.items()
        if key.startswith("selector322_")
    }
    for key in list(integration):
        if key.startswith("selector"):
            del integration[key]
    integration.update(preserved)
    integration["selector1162_consolidated_layer_included"] = True
    integration["selector1162_consolidated"] = new_layer
    integration["selector1162_targeted_progress_delta"] = new_delta
    exact.clear()
    exact.update(preserved_exact)
    exact.update(new_exact)
    exact["final_pk_candidate_sha256"] = EXPECTED_FINAL_CANDIDATE_SHA256
    return progress


def main(argv: Sequence[str] | None = None) -> int:
    BASE.require(
        BASE.sha256_file(BASE_BUILDER_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "selector322 progress delta base drifted",
    )
    BASE.require(
        BASE.sha256_file(DEFAULT_PREDECESSOR_PROGRESS)
        == EXPECTED_PREDECESSOR_PROGRESS_SHA256,
        "post-selector322 progress snapshot drifted",
    )
    configure_base()
    BASE.validate_baseline_progress = validate_baseline_progress
    BASE.build_progress_delta = build_progress_delta
    BASE.load_module = load_checkpoint_compat
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
            "post-selector1162 progress alias drifted",
        )
    return result


if __name__ == "__main__":
    raise SystemExit(main())
