#!/usr/bin/env python3
"""Advance source-free progress with the targeted selector-322 delta."""

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
    WORKSTREAM / "build_progress_post_selector742_consolidated_delta_v1.py"
)
CHECKPOINT_BUILDER_PATH = (
    WORKSTREAM / "build_runtime_vm_post_selector322_consolidated_checkpoint_v1.py"
)
CHECKPOINT_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector322_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector322_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector322_consolidated_closure_decisions.private.v1.jsonl"
)
DEFAULT_PREDECESSOR_PROGRESS = (
    WORKSTREAM / "progress.post_selector742_consolidated.source_free.v1.json"
)
DEFAULT_PROGRESS_OUTPUT = WORKSTREAM / "progress.source_free.v1.json"
IMMUTABLE_PROGRESS_OUTPUT = (
    WORKSTREAM / "progress.post_selector322_consolidated.source_free.v1.json"
)

EXPECTED_BASE_BUILDER_SHA256 = (
    "BA77D490D1223054CB77DF675D5BA4998DE6819BAC2C15759193728CA7CFC0A1"
)
EXPECTED_PREDECESSOR_PROGRESS_SHA256 = (
    "2FBC69410CB1830F9280CF18AF02DA3FA6F4E03FAEAE76CF5DCB52945DC1B294"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "4AC2CD8969958AA254D0F70F7302E1BC3D273229DBB59A0512FEB27E1786D90B"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "D9A52A500BD6E60D3B35574E1890BFC128151A9328A5CAE8B1C4CFBEAB087E9B"
)
EXPECTED_CLOSURE_DECISIONS_SHA256 = (
    "F7992DD09D0955EC49B2CFD4419D1B53F29857E58510F4382C0514DEA83AF80B"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "D0739EBB2E00B9034071165D00CA0D5E08D5F30A6400C8FF38CDA2867BA0203E"
)
EXPECTED_CHECKPOINT_BUILDER_SHA256 = (
    "8FE37F41B9ECBCF7D5E5F3CCF6F1FAFF6A3C31E519081783A994C3E7E380D510"
)
EXPECTED_CHECKPOINT_PRIVATE_SHA256 = (
    "9A7E135544FA2F2A02A0D2B4941159CB92A3E4A495AF72B6CB335DE371351343"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256 = (
    "3C245CE82733F50F08E61B05A165B1038C4D5BBA5D3DAD38D46933B392101642"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 28
EXPECTED_PROMOTIONS = 25
EXPECTED_RENEWALS = 3
EXPECTED_OVERRIDES = 12
EXPECTED_FINAL_PENDING = 6_310
EXPECTED_FINAL_ELIGIBLE = 46_493
EXPECTED_FINAL_PROMOTED_TOTAL = 30_024
EXPECTED_FINAL_PK_PROMOTIONS = 14_373
EXPECTED_FINAL_RETRANSLATED = 46_148
EXPECTED_CONFIRMED_NON_DISPLAY = 345

EXPECTED_PROGRESS_OUTPUT_SHA256: str | None = (
    "AEBCAE97B9794EC527C698E93B1D2F659F55CAFE1E0760B0F2FE1AD9C320070F"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PREVIOUS = load_module(BASE_BUILDER_PATH, "selector322_progress_base")
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
        and totals.get("runtime_review_pending") == 6_335
        and totals.get("fully_candidate_eligible") == 46_468
        and scope.get("retranslated") == 46_123
        and scope.get("confirmed_non_display") == 345
        and scope.get("runtime_fragment_pending") == 6_335
        and integration.get("sha256") == EXPECTED_PREDECESSOR_PUBLIC_SHA256
        and integration.get("private_integrated_decision_sha256")
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256
        and integration.get("promoted_total") == 29_999
        and integration.get("runtime_review_pending_after") == 6_335
        and integration.get("selector742_consolidated_layer_included") is True
        and sum(int(row["runtime_review_pending"]) for row in segments) == 6_335
        and sum(int(row["runtime_review_verified"]) for row in segments)
        == 29_999
        and sum(int(row["decision_count"]) for row in segments) == EXPECTED_ROWS
        and sum(int(row["runtime_review_pending"]) for row in batches) == 6_335
        and sum(int(row["fully_candidate_eligible"]) for row in batches)
        == 46_468
        and sum(int(row["decision_count"]) for row in batches) == EXPECTED_ROWS,
        "post-selector742 progress predecessor drifted",
    )


def build_progress_delta(
    baseline: Mapping[str, Any],
    checkpoint_report: Mapping[str, Any],
    promotions: set[str],
    target_segments: Mapping[str, str],
    target_batches: Mapping[str, str],
) -> dict[str, Any]:
    alias_report = copy.deepcopy(checkpoint_report)
    alias_report["selector742_consolidated"] = alias_report[
        "selector322_consolidated"
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
    new_layer = copy.deepcopy(integration["selector742_consolidated"])
    new_delta = copy.deepcopy(integration["selector742_targeted_progress_delta"])
    exact = integration["final_exact_layers"]
    new_exact = {
        key.replace("selector742_", "selector322_", 1): copy.deepcopy(value)
        for key, value in exact.items()
        if key.startswith("selector742_")
    }
    for key in list(integration):
        if key.startswith("selector"):
            del integration[key]
    integration.update(preserved)
    integration["selector322_consolidated_layer_included"] = True
    integration["selector322_consolidated"] = new_layer
    integration["selector322_targeted_progress_delta"] = new_delta
    exact.clear()
    exact.update(preserved_exact)
    exact.update(new_exact)
    exact["final_pk_candidate_sha256"] = EXPECTED_FINAL_CANDIDATE_SHA256
    return progress


def main(argv: Sequence[str] | None = None) -> int:
    BASE.require(
        BASE.sha256_file(BASE_BUILDER_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "selector742 progress delta base drifted",
    )
    BASE.require(
        BASE.sha256_file(DEFAULT_PREDECESSOR_PROGRESS)
        == EXPECTED_PREDECESSOR_PROGRESS_SHA256,
        "post-selector742 progress snapshot drifted",
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
            "post-selector322 progress alias drifted",
        )
    return result


if __name__ == "__main__":
    raise SystemExit(main())
