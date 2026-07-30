#!/usr/bin/env python3
"""Prepare the source-free progress delta for post-selector292 wave 4."""

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
    WORKSTREAM
    / "build_progress_post_selector292_wave3_consolidated_delta_v1.py"
)
CHECKPOINT_BUILDER_PATH = (
    WORKSTREAM
    / "build_runtime_vm_post_selector292_wave4_consolidated_checkpoint_v1.py"
)
CHECKPOINT_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector292_wave4_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration."
    "post_selector292_wave4_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_dialogue_wave_post_selector292_wave4_consolidated_closure_"
    "decisions.private.v1.jsonl"
)
DEFAULT_PREDECESSOR_PROGRESS = (
    WORKSTREAM
    / "progress.post_selector292_wave3_consolidated.source_free.v1.json"
)
DEFAULT_PROGRESS_OUTPUT = WORKSTREAM / "progress.source_free.v1.json"
IMMUTABLE_PROGRESS_OUTPUT = (
    WORKSTREAM
    / "progress.post_selector292_wave4_consolidated.source_free.v1.json"
)

EXPECTED_BASE_BUILDER_SHA256 = (
    "6CB967B57CBC2C1A3189FBA9A4F0442BA9DE45660C139D63F59EB8E8F8884C7D"
)
EXPECTED_PREDECESSOR_PROGRESS_SHA256 = (
    "7BE116E17F8400C88EEA54304EE9B2BCEFE932C6D7643BA1CD44C675FD798333"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "3AEE8906C75A77C5808A28D3BAD62509BA2A32FF69C80AA68FAEA3C99CA72FDE"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "6B8E2A8701A0FE248909DE9FB0C6F9F448B4C37F98CBA47370A9F04259D30359"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "4B2A09C787802B073109DE00B280FFC7FAB69FCF91C8D800EADCA3F072BE3C20"
)

# Frozen after the wave-4 checkpoint becomes immutable.
EXPECTED_CLOSURE_DECISIONS_SHA256: str | None = (
    "BF56EAC530AB4D6AD5D510663575E18FDEE76F73751CFF755196D073E0D1EAC3"
)
EXPECTED_FINAL_CANDIDATE_SHA256: str | None = (
    "6D60AEEDBD22843B9AEC1DC4B1DDC3509106D6C8FC8F74FE79E4C1E3CE037836"
)
EXPECTED_CHECKPOINT_BUILDER_SHA256: str | None = (
    "C6BEB85B9E7CFB8B5BE395EFC9837631A806D40572151924ADBB06F62AA072F5"
)
EXPECTED_CHECKPOINT_PRIVATE_SHA256: str | None = (
    "BDE252E097BB1D7531F2269E0C4C105972EAEC484961E7EEEA44C0D1414C1DAE"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256: str | None = (
    "FA294DE6C6B4D26F5BE6BF352D7631AB210224D6C1B95962871275011C07CAEB"
)
EXPECTED_PROGRESS_OUTPUT_SHA256: str | None = (
    "7E032B6CFF3AF1D6F1B299CD2A9683E8DC880778702820D1F4308A26EBB9E20D"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS: int | None = 29
EXPECTED_PROMOTIONS: int | None = 29
EXPECTED_RENEWALS: int | None = 0
EXPECTED_OVERRIDES: int | None = 27
EXPECTED_PREDECESSOR_PENDING = 5_999
EXPECTED_FINAL_PENDING: int | None = 5_970
EXPECTED_PREDECESSOR_ELIGIBLE = 46_804
EXPECTED_FINAL_ELIGIBLE: int | None = 46_833
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 30_335
EXPECTED_FINAL_PROMOTED_TOTAL: int | None = 30_364
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 14_684
EXPECTED_FINAL_PK_PROMOTIONS: int | None = 14_713
EXPECTED_PREDECESSOR_RETRANSLATED = 46_459
EXPECTED_FINAL_RETRANSLATED: int | None = 46_488
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_TARGETED_AFFECTED_ROWS: int | None = 29
EXPECTED_UNAFFECTED_ROWS: int | None = 52_774
EXPECTED_FULL_DIALOGUE_REBUILD = False

CHECKPOINT_PIN_NAMES = (
    "EXPECTED_CLOSURE_DECISIONS_SHA256",
    "EXPECTED_FINAL_CANDIDATE_SHA256",
    "EXPECTED_CHECKPOINT_BUILDER_SHA256",
    "EXPECTED_CHECKPOINT_PRIVATE_SHA256",
    "EXPECTED_CHECKPOINT_PUBLIC_SHA256",
    "EXPECTED_DECISIONS",
    "EXPECTED_PROMOTIONS",
    "EXPECTED_RENEWALS",
    "EXPECTED_OVERRIDES",
    "EXPECTED_FINAL_PENDING",
    "EXPECTED_FINAL_ELIGIBLE",
    "EXPECTED_FINAL_PROMOTED_TOTAL",
    "EXPECTED_FINAL_PK_PROMOTIONS",
    "EXPECTED_FINAL_RETRANSLATED",
    "EXPECTED_TARGETED_AFFECTED_ROWS",
    "EXPECTED_UNAFFECTED_ROWS",
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PREVIOUS = load_module(BASE_BUILDER_PATH, "post292_wave3_progress_base")
BASE = PREVIOUS.BASE
ORIGINAL_BASE_LOAD_MODULE = PREVIOUS.ORIGINAL_BASE_LOAD_MODULE


def unresolved_checkpoint_pins() -> tuple[str, ...]:
    return tuple(
        name for name in CHECKPOINT_PIN_NAMES if globals()[name] is None
    )


def pins_resolved() -> bool:
    return (
        not unresolved_checkpoint_pins()
        and EXPECTED_PROGRESS_OUTPUT_SHA256 is not None
    )


def require_checkpoint_pins() -> None:
    missing = unresolved_checkpoint_pins()
    if missing:
        raise RuntimeError(
            "post-selector292 wave4 progress input pins unresolved: "
            + ", ".join(missing)
        )


def load_checkpoint_compat(name: str, path: Path) -> Any:
    module = ORIGINAL_BASE_LOAD_MODULE(name, path)
    if path.resolve() == CHECKPOINT_BUILDER_PATH.resolve():
        if hasattr(module, "configure_base"):
            module.configure_base()
        else:
            module.configure_predecessor()
        module.load_closure_decisions = module.BASE.load_closure_decisions
    return module


def configure_base() -> None:
    require_checkpoint_pins()
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
        "EXPECTED_TARGETED_AFFECTED_ROWS":
            EXPECTED_TARGETED_AFFECTED_ROWS,
        "EXPECTED_UNAFFECTED_ROWS": EXPECTED_UNAFFECTED_ROWS,
        "EXPECTED_FULL_DIALOGUE_REBUILD": EXPECTED_FULL_DIALOGUE_REBUILD,
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
        and totals.get("runtime_review_pending")
        == EXPECTED_PREDECESSOR_PENDING
        and totals.get("fully_candidate_eligible")
        == EXPECTED_PREDECESSOR_ELIGIBLE
        and scope.get("retranslated") == EXPECTED_PREDECESSOR_RETRANSLATED
        and scope.get("confirmed_non_display")
        == EXPECTED_CONFIRMED_NON_DISPLAY
        and scope.get("runtime_fragment_pending")
        == EXPECTED_PREDECESSOR_PENDING
        and integration.get("sha256") == EXPECTED_PREDECESSOR_PUBLIC_SHA256
        and integration.get("private_integrated_decision_sha256")
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256
        and integration.get("promoted_total")
        == EXPECTED_PREDECESSOR_PROMOTED_TOTAL
        and integration.get("runtime_review_pending_after")
        == EXPECTED_PREDECESSOR_PENDING
        and integration.get("selector292_consolidated_layer_included")
        is True
        and integration["final_exact_layers"].get(
            "final_pk_candidate_sha256"
        ) == EXPECTED_PREDECESSOR_CANDIDATE_SHA256
        and sum(int(row["runtime_review_pending"]) for row in segments)
        == EXPECTED_PREDECESSOR_PENDING
        and sum(int(row["runtime_review_verified"]) for row in segments)
        == EXPECTED_PREDECESSOR_PROMOTED_TOTAL
        and sum(int(row["decision_count"]) for row in segments)
        == EXPECTED_ROWS
        and sum(int(row["runtime_review_pending"]) for row in batches)
        == EXPECTED_PREDECESSOR_PENDING
        and sum(int(row["fully_candidate_eligible"]) for row in batches)
        == EXPECTED_PREDECESSOR_ELIGIBLE
        and sum(int(row["decision_count"]) for row in batches)
        == EXPECTED_ROWS,
        "post-selector292 progress predecessor drifted",
    )


def build_progress_delta(
    baseline: Mapping[str, Any],
    checkpoint_report: Mapping[str, Any],
    promotions: set[str],
    target_segments: Mapping[str, str],
    target_batches: Mapping[str, str],
) -> dict[str, Any]:
    alias_report = copy.deepcopy(checkpoint_report)
    alias_report[
        "dialogue_wave_post_selector292_wave3_consolidated"
    ] = alias_report[
        "dialogue_wave_post_selector292_wave4_consolidated"
    ]
    baseline_integration = baseline["runtime_vm_integration"]
    old_wave_layer = copy.deepcopy(
        baseline_integration[
            "dialogue_wave_post_selector292_wave3_consolidated"
        ]
    )
    old_wave_included = baseline_integration[
        "dialogue_wave_post_selector292_wave3_consolidated_layer_included"
    ]
    old_wave_delta = copy.deepcopy(
        baseline_integration[
            "dialogue_wave_post_selector292_wave3_targeted_progress_delta"
        ]
    )
    old_wave_exact = {
        key: copy.deepcopy(value)
        for key, value in baseline_integration["final_exact_layers"].items()
        if key.startswith("dialogue_wave_post_selector292_wave3_")
    }
    progress = PREVIOUS.build_progress_delta(
        baseline,
        alias_report,
        promotions,
        target_segments,
        target_batches,
    )
    integration = progress["runtime_vm_integration"]
    new_layer = copy.deepcopy(
        integration["dialogue_wave_post_selector292_wave3_consolidated"]
    )
    new_delta = copy.deepcopy(
        integration[
            "dialogue_wave_post_selector292_wave3_targeted_progress_delta"
        ]
    )
    exact = integration["final_exact_layers"]
    new_exact = {
        key.replace(
            "dialogue_wave_post_selector292_wave3_",
            "dialogue_wave_post_selector292_wave4_",
            1,
        ): copy.deepcopy(value)
        for key, value in exact.items()
        if key.startswith("dialogue_wave_post_selector292_wave3_")
    }
    for key in list(exact):
        if key.startswith("dialogue_wave_post_selector292_wave3_"):
            del exact[key]
    exact.update(old_wave_exact)
    exact.update(new_exact)
    exact["final_pk_candidate_sha256"] = EXPECTED_FINAL_CANDIDATE_SHA256
    integration[
        "dialogue_wave_post_selector292_wave3_consolidated_layer_included"
    ] = old_wave_included
    integration[
        "dialogue_wave_post_selector292_wave3_consolidated"
    ] = old_wave_layer
    integration[
        "dialogue_wave_post_selector292_wave3_targeted_progress_delta"
    ] = old_wave_delta
    integration[
        "dialogue_wave_post_selector292_wave4_consolidated_layer_included"
    ] = True
    integration[
        "dialogue_wave_post_selector292_wave4_consolidated"
    ] = new_layer
    integration[
        "dialogue_wave_post_selector292_wave4_targeted_progress_delta"
    ] = new_delta
    return progress


def main(argv: Sequence[str] | None = None) -> int:
    arguments = tuple(sys.argv[1:] if argv is None else argv)
    require_checkpoint_pins()
    if "--check" in arguments and EXPECTED_PROGRESS_OUTPUT_SHA256 is None:
        raise RuntimeError(
            "post-selector292 wave4 progress output hash unresolved"
        )
    BASE.require(
        BASE.sha256_file(BASE_BUILDER_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "post-selector292 progress delta base drifted",
    )
    BASE.require(
        BASE.sha256_file(DEFAULT_PREDECESSOR_PROGRESS)
        == EXPECTED_PREDECESSOR_PROGRESS_SHA256,
        "post-selector292 progress snapshot drifted",
    )
    configure_base()
    BASE.validate_baseline_progress = validate_baseline_progress
    BASE.build_progress_delta = build_progress_delta
    BASE.load_module = load_checkpoint_compat
    result = BASE.main(argv)
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
            "post-selector292 wave4 progress outputs drifted",
        )
    return result


if __name__ == "__main__":
    raise SystemExit(main())
