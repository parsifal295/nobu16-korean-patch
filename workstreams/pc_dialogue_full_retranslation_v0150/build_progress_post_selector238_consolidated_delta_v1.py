#!/usr/bin/env python3
"""Prepare the source-free progress delta scaffold for selector 238."""

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
    WORKSTREAM / "build_progress_post_selector730_consolidated_delta_v1.py"
)
CHECKPOINT_BUILDER_PATH = (
    WORKSTREAM / "build_runtime_vm_post_selector238_consolidated_checkpoint_v1.py"
)
CHECKPOINT_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector238_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector238_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector238_consolidated_closure_decisions.private.v1.jsonl"
)
DEFAULT_PREDECESSOR_PROGRESS = (
    WORKSTREAM / "progress.post_selector730_consolidated.source_free.v1.json"
)
DEFAULT_PROGRESS_OUTPUT = WORKSTREAM / "progress.source_free.v1.json"
IMMUTABLE_PROGRESS_OUTPUT = (
    WORKSTREAM / "progress.post_selector238_consolidated.source_free.v1.json"
)

EXPECTED_BASE_BUILDER_SHA256 = (
    "677893076103E3F55D481F6F83D84FDCFBDBDFC9C2DE954DF805821F6DD52A89"
)
EXPECTED_PREDECESSOR_PROGRESS_SHA256 = (
    "60C09B9BF8C632DE5824D854DC20704755A73FB30E2F5ABDD9187879B6DD3628"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "9F6BD587F6EC92CD00A2E2AF9FD9E07A8B6A71405272F0D79A515C3405617C5C"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "311DD27E8C260B7438EDF90FFB944EAEC25C3462C2C8E6BDA196BCF89DEDF362"
)
EXPECTED_PREDECESSOR_CANDIDATE_SHA256 = (
    "5D4CDF1CEB8C733B0E22C7AA6185D9FF6C5C4C500176E99A6AACB3D89F7E0140"
)

# Frozen after the selector-238 checkpoint became immutable.
EXPECTED_CLOSURE_DECISIONS_SHA256: str | None = (
    "6C06A0C6702109D17663270FB6946155D28B805F6D81A71CFC522A12F9B75B58"
)
EXPECTED_FINAL_CANDIDATE_SHA256: str | None = (
    "9E5C60A451DB7CCA7B046AFD8CFF199CB3665E003CB0C751120478F693D20C24"
)
EXPECTED_CHECKPOINT_BUILDER_SHA256: str | None = (
    "503A8500AFDB5A1041FA497A62634B3C30772DCE79628168C4208A898B45738B"
)
EXPECTED_CHECKPOINT_PRIVATE_SHA256: str | None = (
    "AC10F7E71CFAD259ABBC08139BE0DB848CF5309578045532A48991F40E0035AB"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256: str | None = (
    "0CAE7231474FBAE0BCE8E1E98D44225DCC5445EEEA435378E0D56BD1F83A5384"
)
EXPECTED_PROGRESS_OUTPUT_SHA256: str | None = (
    "3882DA0AE88D67A43EA2EF747E6B9ACF945CF07E6D98DC331FBB5871848C8720"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 27
EXPECTED_PROMOTIONS = 27
EXPECTED_RENEWALS = 0
EXPECTED_OVERRIDES = 22
EXPECTED_FINAL_PENDING = 6_151
EXPECTED_FINAL_ELIGIBLE = 46_652
EXPECTED_FINAL_PROMOTED_TOTAL = 30_183
EXPECTED_FINAL_PK_PROMOTIONS = 14_532
EXPECTED_FINAL_RETRANSLATED = 46_307
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_TARGETED_AFFECTED_ROWS = 27
EXPECTED_UNAFFECTED_ROWS = 52_776
EXPECTED_FULL_DIALOGUE_REBUILD = False

CHECKPOINT_PIN_NAMES = (
    "EXPECTED_CLOSURE_DECISIONS_SHA256",
    "EXPECTED_FINAL_CANDIDATE_SHA256",
    "EXPECTED_CHECKPOINT_BUILDER_SHA256",
    "EXPECTED_CHECKPOINT_PRIVATE_SHA256",
    "EXPECTED_CHECKPOINT_PUBLIC_SHA256",
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


PREVIOUS = load_module(BASE_BUILDER_PATH, "selector238_progress_base")
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
            "selector238 progress scaffold has unresolved checkpoint pins: "
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
        and totals.get("runtime_review_pending") == 6_178
        and totals.get("fully_candidate_eligible") == 46_625
        and scope.get("retranslated") == 46_280
        and scope.get("confirmed_non_display") == 345
        and scope.get("runtime_fragment_pending") == 6_178
        and integration.get("sha256") == EXPECTED_PREDECESSOR_PUBLIC_SHA256
        and integration.get("private_integrated_decision_sha256")
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256
        and integration.get("promoted_total") == 30_156
        and integration.get("runtime_review_pending_after") == 6_178
        and integration.get("selector730_consolidated_layer_included")
        is True
        and integration["final_exact_layers"].get(
            "final_pk_candidate_sha256"
        ) == EXPECTED_PREDECESSOR_CANDIDATE_SHA256
        and sum(int(row["runtime_review_pending"]) for row in segments)
        == 6_178
        and sum(int(row["runtime_review_verified"]) for row in segments)
        == 30_156
        and sum(int(row["decision_count"]) for row in segments)
        == EXPECTED_ROWS
        and sum(int(row["runtime_review_pending"]) for row in batches)
        == 6_178
        and sum(int(row["fully_candidate_eligible"]) for row in batches)
        == 46_625
        and sum(int(row["decision_count"]) for row in batches)
        == EXPECTED_ROWS,
        "post-selector730 progress predecessor drifted",
    )


def build_progress_delta(
    baseline: Mapping[str, Any],
    checkpoint_report: Mapping[str, Any],
    promotions: set[str],
    target_segments: Mapping[str, str],
    target_batches: Mapping[str, str],
) -> dict[str, Any]:
    alias_report = copy.deepcopy(checkpoint_report)
    alias_report["selector730_consolidated"] = alias_report[
        "selector238_consolidated"
    ]
    baseline_integration = baseline["runtime_vm_integration"]
    old_layer = copy.deepcopy(
        baseline_integration["selector730_consolidated"]
    )
    old_included = baseline_integration[
        "selector730_consolidated_layer_included"
    ]
    old_delta = copy.deepcopy(
        baseline_integration["selector730_targeted_progress_delta"]
    )
    old_exact = {
        key: copy.deepcopy(value)
        for key, value in baseline_integration["final_exact_layers"].items()
        if key.startswith("selector730_")
    }
    progress = PREVIOUS.build_progress_delta(
        baseline,
        alias_report,
        promotions,
        target_segments,
        target_batches,
    )
    integration = progress["runtime_vm_integration"]
    new_layer = copy.deepcopy(integration["selector730_consolidated"])
    new_delta = copy.deepcopy(
        integration["selector730_targeted_progress_delta"]
    )
    exact = integration["final_exact_layers"]
    new_exact = {
        key.replace("selector730_", "selector238_", 1):
            copy.deepcopy(value)
        for key, value in exact.items()
        if key.startswith("selector730_")
    }
    for key in list(exact):
        if key.startswith("selector730_"):
            del exact[key]
    exact.update(old_exact)
    exact.update(new_exact)
    exact["final_pk_candidate_sha256"] = EXPECTED_FINAL_CANDIDATE_SHA256
    integration["selector730_consolidated_layer_included"] = old_included
    integration["selector730_consolidated"] = old_layer
    integration["selector730_targeted_progress_delta"] = old_delta
    integration["selector238_consolidated_layer_included"] = True
    integration["selector238_consolidated"] = new_layer
    integration["selector238_targeted_progress_delta"] = new_delta
    return progress


def main(argv: Sequence[str] | None = None) -> int:
    arguments = tuple(sys.argv[1:] if argv is None else argv)
    require_checkpoint_pins()
    if "--check" in arguments and EXPECTED_PROGRESS_OUTPUT_SHA256 is None:
        raise RuntimeError(
            "selector238 progress scaffold has unresolved output hash"
        )
    BASE.require(
        BASE.sha256_file(BASE_BUILDER_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "selector730 progress delta base drifted",
    )
    BASE.require(
        BASE.sha256_file(DEFAULT_PREDECESSOR_PROGRESS)
        == EXPECTED_PREDECESSOR_PROGRESS_SHA256,
        "post-selector730 progress snapshot drifted",
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
            "post-selector238 progress alias drifted",
        )
    return result


if __name__ == "__main__":
    raise SystemExit(main())
