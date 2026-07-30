#!/usr/bin/env python3
"""Prepare the source-free progress delta for root-sharded wave 7."""

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
TRACKED_DIALOGUE = REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"

BASE_BUILDER_PATH = (
    TRACKED_DIALOGUE
    / "build_progress_post_selector292_wave6_consolidated_delta_v1.py"
)
CHECKPOINT_BUILDER_PATH = (
    TRACKED_DIALOGUE
    / "build_runtime_vm_post_selector292_wave7_root_sharded_"
    "consolidated_checkpoint_v1.py"
)
CHECKPOINT_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector292_wave7_root_sharded_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC_PATH = (
    TRACKED_DIALOGUE
    / "runtime_vm_integration."
    "post_selector292_wave7_root_sharded_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_dialogue_wave_post_selector292_wave7_root_sharded_consolidated_closure_"
    "decisions.private.v1.jsonl"
)
DEFAULT_PREDECESSOR_PROGRESS = (
    TRACKED_DIALOGUE
    / "progress.post_selector292_wave6_consolidated.source_free.v1.json"
)
DEFAULT_PROGRESS_OUTPUT = (
    TRACKED_DIALOGUE / "progress.source_free.v1.json"
)
IMMUTABLE_PROGRESS_OUTPUT = (
    TRACKED_DIALOGUE
    / "progress.post_selector292_wave7_root_sharded_consolidated.source_free.v1.json"
)

EXPECTED_BASE_BUILDER_SHA256 = (
    "CB288CF5C509B9FBC252A3FACCA5080080E197EF5547F2C4B38F0BF3D1B4D4B2"
)
EXPECTED_PREDECESSOR_PROGRESS_SHA256 = (
    "58A10BDE56CAC75D6B57CC6E2BACFD7BE49B506D2350E6402E7FCA16CE6A44F4"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "7016A0AB5EFD5B0FD223818F860B5757A914188A8EE58C2AD3BE6D14BC393F61"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "987E9644DD5DC235C74E52858546C9196BA15203871A7FE9DDEBF121697435F3"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "DC8F4F47EA9DDD81BA6DD788ECE55FD303FA5C228925E6E947E4E7F5C1007804"
)

# Frozen after the wave-6 checkpoint became immutable.
EXPECTED_CLOSURE_DECISIONS_SHA256: str | None = (
    "554F0365B15976A7F0457D277AB7FFECFCCD86CBF0B6507E68D5737B072D7AE4"
)
EXPECTED_FINAL_CANDIDATE_SHA256: str | None = (
    "DAB40F2AA8095E67550B69213A53CC777B96B17071FFF5B860CFAEE1A868D7E0"
)
EXPECTED_CHECKPOINT_BUILDER_SHA256: str | None = (
    "825D7AA13B5750697CB7A0A548CBE5C90D2F2A5BD7762985F1F17B1FEB556DFF"
)
EXPECTED_CHECKPOINT_PRIVATE_SHA256: str | None = (
    "B1CF7F4523DE9411BA5172E7C9DEA946C7646085C83A1480C51807E2DD0C90E7"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256: str | None = (
    "96E03D3EA32FAB5E6701DB75060038A5E967F9617EB0E22E5C91352944626930"
)
EXPECTED_PROGRESS_OUTPUT_SHA256: str | None = (
    "53423D5B16ED9EE60619989F09A71CDD7194B70CDB698AA9DDE606AE2145EF0B"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS: int | None = 21
EXPECTED_PROMOTIONS: int | None = 21
EXPECTED_RENEWALS: int | None = 0
EXPECTED_OVERRIDES: int | None = 13
EXPECTED_PREDECESSOR_PENDING = 5_922
EXPECTED_FINAL_PENDING: int | None = 5_901
EXPECTED_PREDECESSOR_ELIGIBLE = 46_881
EXPECTED_FINAL_ELIGIBLE: int | None = 46_902
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 30_412
EXPECTED_FINAL_PROMOTED_TOTAL: int | None = 30_433
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 14_761
EXPECTED_FINAL_PK_PROMOTIONS: int | None = 14_782
EXPECTED_PREDECESSOR_RETRANSLATED = 46_536
EXPECTED_FINAL_RETRANSLATED: int | None = 46_557
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_TARGETED_AFFECTED_ROWS: int | None = 21
EXPECTED_UNAFFECTED_ROWS: int | None = 52_782
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


PREVIOUS = load_module(BASE_BUILDER_PATH, "post292_wave7_progress_base")
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
            "post-selector292 wave7 root-sharded progress input pins unresolved: "
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
        "dialogue_wave_post_selector292_wave6_consolidated"
    ] = alias_report[
        "dialogue_wave_post_selector292_wave7_root_sharded_consolidated"
    ]
    baseline_integration = baseline["runtime_vm_integration"]
    old_wave_layer = copy.deepcopy(
        baseline_integration[
            "dialogue_wave_post_selector292_wave6_consolidated"
        ]
    )
    old_wave_included = baseline_integration[
        "dialogue_wave_post_selector292_wave6_consolidated_layer_included"
    ]
    old_wave_delta = copy.deepcopy(
        baseline_integration[
            "dialogue_wave_post_selector292_wave6_targeted_progress_delta"
        ]
    )
    old_wave_exact = {
        key: copy.deepcopy(value)
        for key, value in baseline_integration["final_exact_layers"].items()
        if key.startswith("dialogue_wave_post_selector292_wave6_")
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
        integration["dialogue_wave_post_selector292_wave6_consolidated"]
    )
    new_delta = copy.deepcopy(
        integration[
            "dialogue_wave_post_selector292_wave6_targeted_progress_delta"
        ]
    )
    exact = integration["final_exact_layers"]
    new_exact = {
        key.replace(
            "dialogue_wave_post_selector292_wave6_",
            "dialogue_wave_post_selector292_wave7_root_sharded_",
            1,
        ): copy.deepcopy(value)
        for key, value in exact.items()
        if key.startswith("dialogue_wave_post_selector292_wave6_")
    }
    for key in list(exact):
        if key.startswith("dialogue_wave_post_selector292_wave6_"):
            del exact[key]
    exact.update(old_wave_exact)
    exact.update(new_exact)
    exact["final_pk_candidate_sha256"] = EXPECTED_FINAL_CANDIDATE_SHA256
    integration[
        "dialogue_wave_post_selector292_wave6_consolidated_layer_included"
    ] = old_wave_included
    integration[
        "dialogue_wave_post_selector292_wave6_consolidated"
    ] = old_wave_layer
    integration[
        "dialogue_wave_post_selector292_wave6_targeted_progress_delta"
    ] = old_wave_delta
    integration[
        "dialogue_wave_post_selector292_wave7_root_sharded_consolidated_layer_included"
    ] = True
    integration[
        "dialogue_wave_post_selector292_wave7_root_sharded_consolidated"
    ] = new_layer
    integration[
        "dialogue_wave_post_selector292_wave7_root_sharded_targeted_progress_delta"
    ] = new_delta
    return progress


def main(argv: Sequence[str] | None = None) -> int:
    arguments = tuple(sys.argv[1:] if argv is None else argv)
    require_checkpoint_pins()
    if "--check" in arguments and EXPECTED_PROGRESS_OUTPUT_SHA256 is None:
        raise RuntimeError(
            "post-selector292 wave7 root-sharded progress output hash unresolved"
        )
    BASE.require(
        BASE.sha256_file(BASE_BUILDER_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "post-selector292 wave7 progress delta base drifted",
    )
    BASE.require(
        BASE.sha256_file(DEFAULT_PREDECESSOR_PROGRESS)
        == EXPECTED_PREDECESSOR_PROGRESS_SHA256,
        "post-selector292 wave7 progress snapshot drifted",
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
            "post-selector292 wave7 root-sharded progress outputs drifted",
        )
    return result


if __name__ == "__main__":
    raise SystemExit(main())
