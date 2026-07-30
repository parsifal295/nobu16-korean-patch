#!/usr/bin/env python3
"""Prepare the source-free progress delta for post-selector292 wave 2."""

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
    / "build_progress_post_selector292_wave1_consolidated_delta_v1.py"
)
CHECKPOINT_BUILDER_PATH = (
    WORKSTREAM
    / "build_runtime_vm_post_selector292_wave2_consolidated_checkpoint_v1.py"
)
CHECKPOINT_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector292_wave2_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration."
    "post_selector292_wave2_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_dialogue_wave_post_selector292_wave2_consolidated_closure_"
    "decisions.private.v1.jsonl"
)
DEFAULT_PREDECESSOR_PROGRESS = (
    WORKSTREAM
    / "progress.post_selector292_wave1_consolidated.source_free.v1.json"
)
DEFAULT_PROGRESS_OUTPUT = WORKSTREAM / "progress.source_free.v1.json"
IMMUTABLE_PROGRESS_OUTPUT = (
    WORKSTREAM
    / "progress.post_selector292_wave2_consolidated.source_free.v1.json"
)

EXPECTED_BASE_BUILDER_SHA256 = (
    "03BB2894B0DBBA9DD387087BA0C292F183CD7CBBF7F4DE07C49E6D86E50BD1FE"
)
EXPECTED_PREDECESSOR_PROGRESS_SHA256 = (
    "D77906D6319E1F037E7F3C54892DDDCE3A5268B6EBACD07A960509D01D41D528"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "3A49375034F28AE3AB088D7A22DDCEE6252CA4C45F67B3B57F32FC449DF2BEFF"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "71930E0261038636E8B20D0E03C577A98B4E09E160C10429E68D88B2F88A4331"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "C47390C28DE697CAD3F57A72A079F4D8CEA897F6E343CFCE704851BCC3507060"
)

# Frozen after the wave-2 checkpoint becomes immutable.
EXPECTED_CLOSURE_DECISIONS_SHA256: str | None = (
    "8126679196ACC7E85A1C3B9C760884650BD01BF7219C30CDFF2E005732460E49"
)
EXPECTED_FINAL_CANDIDATE_SHA256: str | None = (
    "DF91852936FFBCF0F7C9A17D4D05166A66E041F7A837E50BE600923DB8A2CA9A"
)
EXPECTED_CHECKPOINT_BUILDER_SHA256: str | None = (
    "32812D569C2F5CDF431871AB8FD0E1610776ADE8846E04A3203432AF86414F6D"
)
EXPECTED_CHECKPOINT_PRIVATE_SHA256: str | None = (
    "477C57FE380B20F45F5D952ED3954DE3D1F267CA2E0EA4BC5FA6E96B36877843"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256: str | None = (
    "24EC33757EB877A0025F23908305D002306359DAC277D36ED85EC45EF076E21A"
)
EXPECTED_PROGRESS_OUTPUT_SHA256: str | None = (
    "BB153A023FDCAAE6F178DB0DCAA73096D9E6EBE5DED67BBA63ACB2F3BEE3BA3C"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS: int | None = 62
EXPECTED_PROMOTIONS: int | None = 62
EXPECTED_RENEWALS: int | None = 0
EXPECTED_OVERRIDES: int | None = 50
EXPECTED_PREDECESSOR_PENDING = 6_084
EXPECTED_FINAL_PENDING: int | None = 6_022
EXPECTED_PREDECESSOR_ELIGIBLE = 46_719
EXPECTED_FINAL_ELIGIBLE: int | None = 46_781
EXPECTED_PREDECESSOR_PROMOTED_TOTAL = 30_250
EXPECTED_FINAL_PROMOTED_TOTAL: int | None = 30_312
EXPECTED_PREDECESSOR_PK_PROMOTIONS = 14_599
EXPECTED_FINAL_PK_PROMOTIONS: int | None = 14_661
EXPECTED_PREDECESSOR_RETRANSLATED = 46_374
EXPECTED_FINAL_RETRANSLATED: int | None = 46_436
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_TARGETED_AFFECTED_ROWS: int | None = 62
EXPECTED_UNAFFECTED_ROWS: int | None = 52_741
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


PREVIOUS = load_module(BASE_BUILDER_PATH, "post292_wave1_progress_base")
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
            "post-selector292 wave2 progress input pins unresolved: "
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
    alias_report["dialogue_wave_post_selector292_consolidated"] = alias_report[
        "dialogue_wave_post_selector292_wave2_consolidated"
    ]
    baseline_integration = baseline["runtime_vm_integration"]
    old_wave_layer = copy.deepcopy(
        baseline_integration["dialogue_wave_post_selector292_consolidated"]
    )
    old_wave_included = baseline_integration[
        "dialogue_wave_post_selector292_consolidated_layer_included"
    ]
    old_wave_delta = copy.deepcopy(
        baseline_integration[
            "dialogue_wave_post_selector292_targeted_progress_delta"
        ]
    )
    old_wave_exact = {
        key: copy.deepcopy(value)
        for key, value in baseline_integration["final_exact_layers"].items()
        if key.startswith("dialogue_wave_post_selector292_")
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
        integration["dialogue_wave_post_selector292_consolidated"]
    )
    new_delta = copy.deepcopy(
        integration[
            "dialogue_wave_post_selector292_targeted_progress_delta"
        ]
    )
    exact = integration["final_exact_layers"]
    new_exact = {
        key.replace(
            "dialogue_wave_post_selector292_",
            "dialogue_wave_post_selector292_wave2_",
            1,
        ): copy.deepcopy(value)
        for key, value in exact.items()
        if key.startswith("dialogue_wave_post_selector292_")
    }
    for key in list(exact):
        if key.startswith("dialogue_wave_post_selector292_"):
            del exact[key]
    exact.update(old_wave_exact)
    exact.update(new_exact)
    exact["final_pk_candidate_sha256"] = EXPECTED_FINAL_CANDIDATE_SHA256
    integration[
        "dialogue_wave_post_selector292_consolidated_layer_included"
    ] = old_wave_included
    integration[
        "dialogue_wave_post_selector292_consolidated"
    ] = old_wave_layer
    integration[
        "dialogue_wave_post_selector292_targeted_progress_delta"
    ] = old_wave_delta
    integration[
        "dialogue_wave_post_selector292_wave2_consolidated_layer_included"
    ] = True
    integration[
        "dialogue_wave_post_selector292_wave2_consolidated"
    ] = new_layer
    integration[
        "dialogue_wave_post_selector292_wave2_targeted_progress_delta"
    ] = new_delta
    return progress


def main(argv: Sequence[str] | None = None) -> int:
    arguments = tuple(sys.argv[1:] if argv is None else argv)
    require_checkpoint_pins()
    if "--check" in arguments and EXPECTED_PROGRESS_OUTPUT_SHA256 is None:
        raise RuntimeError(
            "post-selector292 wave2 progress output hash unresolved"
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
            "post-selector292 wave2 progress outputs drifted",
        )
    return result


if __name__ == "__main__":
    raise SystemExit(main())
