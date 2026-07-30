#!/usr/bin/env python3
"""Prepare the source-free progress delta for selector 268."""

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
    WORKSTREAM / "build_progress_post_selector226_consolidated_delta_v1.py"
)
CHECKPOINT_BUILDER_PATH = (
    WORKSTREAM / "build_runtime_vm_post_selector268_consolidated_checkpoint_v1.py"
)
CHECKPOINT_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector268_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector268_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector268_consolidated_closure_decisions.private.v1.jsonl"
)
DEFAULT_PREDECESSOR_PROGRESS = (
    WORKSTREAM / "progress.post_selector226_consolidated.source_free.v1.json"
)
DEFAULT_PROGRESS_OUTPUT = WORKSTREAM / "progress.source_free.v1.json"
IMMUTABLE_PROGRESS_OUTPUT = (
    WORKSTREAM / "progress.post_selector268_consolidated.source_free.v1.json"
)

EXPECTED_BASE_BUILDER_SHA256 = (
    "C123A7B86118DA899DFCD3F31CA9E4B91C6B58D947905F3AA82A6EE186913C27"
)
EXPECTED_PREDECESSOR_PROGRESS_SHA256 = (
    "75739D657C4642294184C49036FC18C0D00B0EB66FD5F2598E9E75CA3E37A377"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "33B635E1409B290202A98719A9CD58F356551BB54703B7F287FC45250134623D"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "8526C4C53B87ED529D6C9EC44FF00FC9B77703EB6D4369DB83F4B916BAE37337"
)

# Frozen after the selector-268 closure and checkpoint became immutable.
EXPECTED_CLOSURE_DECISIONS_SHA256: str | None = (
    "127BA2D9B9F443AA4DF5030643F476CBB943C971300020F249461A3745F6D93F"
)
EXPECTED_FINAL_CANDIDATE_SHA256: str | None = (
    "92B86808931C1FD34320BC5A9BFD05B7AD704FA9392534FF8DE8F6293F413DAD"
)
EXPECTED_CHECKPOINT_BUILDER_SHA256: str | None = (
    "6E4FEFF52329BA9A4A6AACB74910FC0DB05C0659F02277680102C4447BFA5B3A"
)
EXPECTED_CHECKPOINT_PRIVATE_SHA256: str | None = (
    "0936BD050D1BB529848AD861B951D178A3521C086BC41027C4ED4A5B4FBC79C3"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256: str | None = (
    "FD8A708ED92756AB2024861A1B97550F8229889282E7B58CDEFAEEDFC0C2ECE3"
)
EXPECTED_PROGRESS_OUTPUT_SHA256: str | None = (
    "788FBFDD48CAD296B34416FAAB63F89120C66DF6670F84BB2537CEE25E1273F3"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 14
EXPECTED_PROMOTIONS = 14
EXPECTED_RENEWALS = 0
EXPECTED_OVERRIDES = 4
EXPECTED_FINAL_PENDING = 6_232
EXPECTED_FINAL_ELIGIBLE = 46_571
EXPECTED_FINAL_PROMOTED_TOTAL = 30_102
EXPECTED_FINAL_PK_PROMOTIONS = 14_451
EXPECTED_FINAL_RETRANSLATED = 46_226
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_TARGETED_AFFECTED_ROWS = 14
EXPECTED_UNAFFECTED_ROWS = 52_789
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


PREVIOUS = load_module(BASE_BUILDER_PATH, "selector268_progress_base")
BASE = PREVIOUS.BASE
ORIGINAL_BASE_LOAD_MODULE = BASE.load_module


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
            "selector268 progress scaffold has unresolved checkpoint pins: "
            + ", ".join(missing)
        )


def load_checkpoint_compat(name: str, path: Path) -> Any:
    module = ORIGINAL_BASE_LOAD_MODULE(name, path)
    if path.resolve() == CHECKPOINT_BUILDER_PATH.resolve():
        module.configure_base()
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
        and totals.get("runtime_review_pending") == 6_246
        and totals.get("fully_candidate_eligible") == 46_557
        and scope.get("retranslated") == 46_212
        and scope.get("confirmed_non_display") == 345
        and scope.get("runtime_fragment_pending") == 6_246
        and integration.get("sha256") == EXPECTED_PREDECESSOR_PUBLIC_SHA256
        and integration.get("private_integrated_decision_sha256")
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256
        and integration.get("promoted_total") == 30_088
        and integration.get("runtime_review_pending_after") == 6_246
        and integration.get("selector226_consolidated_layer_included")
        is True
        and sum(int(row["runtime_review_pending"]) for row in segments)
        == 6_246
        and sum(int(row["runtime_review_verified"]) for row in segments)
        == 30_088
        and sum(int(row["decision_count"]) for row in segments)
        == EXPECTED_ROWS
        and sum(int(row["runtime_review_pending"]) for row in batches)
        == 6_246
        and sum(int(row["fully_candidate_eligible"]) for row in batches)
        == 46_557
        and sum(int(row["decision_count"]) for row in batches)
        == EXPECTED_ROWS,
        "post-selector226 progress predecessor drifted",
    )


def build_progress_delta(
    baseline: Mapping[str, Any],
    checkpoint_report: Mapping[str, Any],
    promotions: set[str],
    target_segments: Mapping[str, str],
    target_batches: Mapping[str, str],
) -> dict[str, Any]:
    alias_report = copy.deepcopy(checkpoint_report)
    alias_report["selector226_consolidated"] = alias_report[
        "selector268_consolidated"
    ]
    integration_before = baseline["runtime_vm_integration"]
    preserved = {
        key: copy.deepcopy(value)
        for key, value in integration_before.items()
        if key.startswith("selector")
    }
    preserved_exact = copy.deepcopy(integration_before["final_exact_layers"])
    progress = PREVIOUS.build_progress_delta(
        baseline,
        alias_report,
        promotions,
        target_segments,
        target_batches,
    )
    integration = progress["runtime_vm_integration"]
    new_layer = copy.deepcopy(integration["selector226_consolidated"])
    new_delta = copy.deepcopy(
        integration["selector226_targeted_progress_delta"]
    )
    exact = integration["final_exact_layers"]
    new_exact = {
        key.replace("selector226_", "selector268_", 1): copy.deepcopy(value)
        for key, value in exact.items()
        if key.startswith("selector226_")
    }
    for key in list(integration):
        if key.startswith("selector"):
            del integration[key]
    integration.update(preserved)
    integration["selector268_consolidated_layer_included"] = True
    integration["selector268_consolidated"] = new_layer
    integration["selector268_targeted_progress_delta"] = new_delta
    exact.clear()
    exact.update(preserved_exact)
    exact.update(new_exact)
    exact["final_pk_candidate_sha256"] = EXPECTED_FINAL_CANDIDATE_SHA256
    return progress


def main(argv: Sequence[str] | None = None) -> int:
    arguments = tuple(sys.argv[1:] if argv is None else argv)
    require_checkpoint_pins()
    if "--check" in arguments and EXPECTED_PROGRESS_OUTPUT_SHA256 is None:
        raise RuntimeError(
            "selector268 progress scaffold has unresolved output hash"
        )
    BASE.require(
        BASE.sha256_file(BASE_BUILDER_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "selector226 progress delta base drifted",
    )
    BASE.require(
        BASE.sha256_file(DEFAULT_PREDECESSOR_PROGRESS)
        == EXPECTED_PREDECESSOR_PROGRESS_SHA256,
        "post-selector226 progress snapshot drifted",
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
            "post-selector268 progress alias drifted",
        )
    return result


if __name__ == "__main__":
    raise SystemExit(main())
