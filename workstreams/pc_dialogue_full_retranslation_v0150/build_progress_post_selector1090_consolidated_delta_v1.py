#!/usr/bin/env python3
"""Advance source-free progress with the targeted selector-1090 delta."""

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
    WORKSTREAM / "build_progress_post_selector178_consolidated_delta_v1.py"
)
CHECKPOINT_BUILDER_PATH = (
    WORKSTREAM / "build_runtime_vm_post_selector1090_consolidated_checkpoint_v1.py"
)
CHECKPOINT_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector1090_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector1090_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector1090_consolidated_closure_decisions.private.v1.jsonl"
)
DEFAULT_PREDECESSOR_PROGRESS = (
    WORKSTREAM / "progress.post_selector178_consolidated.source_free.v1.json"
)
DEFAULT_PROGRESS_OUTPUT = WORKSTREAM / "progress.source_free.v1.json"
IMMUTABLE_PROGRESS_OUTPUT = (
    WORKSTREAM / "progress.post_selector1090_consolidated.source_free.v1.json"
)

EXPECTED_BASE_BUILDER_SHA256 = (
    "A5227C1FDD43D36DCD67029ECF0A70149A84BD15DF8441099DD5BCBBB107205E"
)
EXPECTED_PREDECESSOR_PROGRESS_SHA256 = (
    "344807711381CE8E98EDBA6A9EAC6BE3049D64194FC18F84AF413E68B84515B4"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "A11DC8F5F0BAA9532DCB7737AFAFC8732506AC2F4E4B6479B44056CF9958015D"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "8850CDFFDEF13076DF8402F68AA4F72528C9ACEE8145F4A65B4FAF64C7A27742"
)
EXPECTED_CLOSURE_DECISIONS_SHA256 = (
    "059A2A0FCC04036A4FECDC00D8C9437623E4CC1B9B1DDC63867C882D3147DD50"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "396A8DF109A0693C439F990049477F5DE6E10720854D73057F3DFA1702002CCF"
)
EXPECTED_CHECKPOINT_BUILDER_SHA256 = (
    "B952BB83C720465B75F6AF125B062C68F736826DEB5B4B1E2FCF5B77B8749277"
)
EXPECTED_CHECKPOINT_PRIVATE_SHA256 = (
    "CDF7539F8E6A6F0D024A7357854A0AFE45E91F3CBD144822E1DEF8730A9A373F"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256 = (
    "C01950D1B342D45FF8C6FBEB3D7EFD0B5087592D0585EC1A60A668FE0C0B0D93"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 89
EXPECTED_PROMOTIONS = 64
EXPECTED_RENEWALS = 25
EXPECTED_OVERRIDES = 33
EXPECTED_FINAL_PENDING = 6_368
EXPECTED_FINAL_ELIGIBLE = 46_435
EXPECTED_FINAL_PROMOTED_TOTAL = 29_966
EXPECTED_FINAL_PK_PROMOTIONS = 14_315
EXPECTED_FINAL_RETRANSLATED = 46_090
EXPECTED_CONFIRMED_NON_DISPLAY = 345

EXPECTED_PROGRESS_OUTPUT_SHA256: str | None = (
    "DD634BFCF1707E5276CAF91AEB43AF14B8C96C10879391F42A52E731ACDF5562"
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PREVIOUS = load_module(BASE_BUILDER_PATH, "selector1090_progress_base")
BASE = PREVIOUS.BASE


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
        and totals.get("runtime_review_pending") == 6_432
        and totals.get("fully_candidate_eligible") == 46_371
        and scope.get("retranslated") == 46_026
        and scope.get("confirmed_non_display") == 345
        and scope.get("runtime_fragment_pending") == 6_432
        and integration.get("sha256") == EXPECTED_PREDECESSOR_PUBLIC_SHA256
        and integration.get("private_integrated_decision_sha256")
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256
        and integration.get("promoted_total") == 29_902
        and integration.get("runtime_review_pending_after") == 6_432
        and integration.get("selector178_consolidated_layer_included") is True
        and sum(int(row["runtime_review_pending"]) for row in segments) == 6_432
        and sum(int(row["runtime_review_verified"]) for row in segments)
        == 29_902
        and sum(int(row["decision_count"]) for row in segments) == EXPECTED_ROWS
        and sum(int(row["runtime_review_pending"]) for row in batches) == 6_432
        and sum(int(row["fully_candidate_eligible"]) for row in batches)
        == 46_371
        and sum(int(row["decision_count"]) for row in batches) == EXPECTED_ROWS,
        "post-selector178 progress predecessor drifted",
    )


def build_progress_delta(
    baseline: Mapping[str, Any],
    checkpoint_report: Mapping[str, Any],
    promotions: set[str],
    target_segments: Mapping[str, str],
    target_batches: Mapping[str, str],
) -> dict[str, Any]:
    alias_report = copy.deepcopy(checkpoint_report)
    alias_report["selector178_consolidated"] = alias_report[
        "selector1090_consolidated"
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
    new_layer = copy.deepcopy(integration["selector178_consolidated"])
    new_delta = copy.deepcopy(integration["selector178_targeted_progress_delta"])
    exact = integration["final_exact_layers"]
    new_exact = {
        key.replace("selector178_", "selector1090_", 1): copy.deepcopy(value)
        for key, value in exact.items()
        if key.startswith("selector178_")
    }
    for key in list(integration):
        if key.startswith("selector"):
            del integration[key]
    integration.update(preserved)
    integration["selector1090_consolidated_layer_included"] = True
    integration["selector1090_consolidated"] = new_layer
    integration["selector1090_targeted_progress_delta"] = new_delta
    exact.clear()
    exact.update(preserved_exact)
    exact.update(new_exact)
    exact["final_pk_candidate_sha256"] = EXPECTED_FINAL_CANDIDATE_SHA256
    return progress


def main(argv: Sequence[str] | None = None) -> int:
    BASE.require(
        BASE.sha256_file(BASE_BUILDER_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "selector178 progress delta base drifted",
    )
    BASE.require(
        BASE.sha256_file(DEFAULT_PREDECESSOR_PROGRESS)
        == EXPECTED_PREDECESSOR_PROGRESS_SHA256,
        "post-selector178 progress snapshot drifted",
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
            "post-selector1090 progress alias drifted",
        )
    return result


if __name__ == "__main__":
    raise SystemExit(main())
