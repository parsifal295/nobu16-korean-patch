#!/usr/bin/env python3
"""Prepare the source-free progress delta scaffold for selector 466."""

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
    WORKSTREAM / "build_progress_post_selector1078_consolidated_delta_v1.py"
)
CHECKPOINT_BUILDER_PATH = (
    WORKSTREAM / "build_runtime_vm_post_selector466_consolidated_checkpoint_v1.py"
)
CHECKPOINT_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated.post_selector466_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration.post_selector466_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector466_consolidated_closure_decisions.private.v1.jsonl"
)
DEFAULT_PREDECESSOR_PROGRESS = (
    WORKSTREAM / "progress.post_selector1078_consolidated.source_free.v1.json"
)
DEFAULT_PROGRESS_OUTPUT = WORKSTREAM / "progress.source_free.v1.json"
IMMUTABLE_PROGRESS_OUTPUT = (
    WORKSTREAM / "progress.post_selector466_consolidated.source_free.v1.json"
)

EXPECTED_BASE_BUILDER_SHA256 = (
    "13AC05CA2C9A09D319A8D0E7A1306255213EBEE912867932A61E92A13BEEFA41"
)
EXPECTED_PREDECESSOR_PROGRESS_SHA256 = (
    "F554DCDBE12A64A9D9958CAC48C29EE75593E6F9DD87D2F4999FEE4255F66ABA"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "71ADE7F33FC40A817E60F429DE0A0B329E05BF37BD1E03E1671A019783E800F6"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "395C8B600B1AED634FA199602CBBB9F2DCA5691D9E5850688E2107966A8A77E3"
)

# Frozen after the selector-466 closure and checkpoint became immutable.
EXPECTED_CLOSURE_DECISIONS_SHA256: str | None = (
    "9460D51503D9B204E0D6AEC2BD152439137A38C2961D9C4D9464F7B5ABCE87DF"
)
EXPECTED_FINAL_CANDIDATE_SHA256: str | None = (
    "E2283160520383E455C9C26112E80E5DB5EDB89161A9842FF3BD8F4C7FFCAD45"
)
EXPECTED_CHECKPOINT_BUILDER_SHA256: str | None = (
    "727BC2640FC993AB417960D7D29E96BC89C9A09803EB4038A2AB0F0285E319F3"
)
EXPECTED_CHECKPOINT_PRIVATE_SHA256: str | None = (
    "99450F568D8EDED40C7A7332F52DADA184EE6F11FB129CFDBCC758C7880DC197"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256: str | None = (
    "D3824B5CF7A8DE02626FF06CE40816086F7DFB8EF6A0A9E06686756A9B69EA5E"
)
EXPECTED_PROGRESS_OUTPUT_SHA256: str | None = (
    "930EC7EEC2ADD9A85A3DEC7BB7E57D7071E7993A62D40321CBDBDD1F42B12DE9"
)

EXPECTED_ROWS = 52_803
EXPECTED_DECISIONS = 24
EXPECTED_PROMOTIONS = 24
EXPECTED_RENEWALS = 0
EXPECTED_OVERRIDES = 13
EXPECTED_FINAL_PENDING = 6_191
EXPECTED_FINAL_ELIGIBLE = 46_612
EXPECTED_FINAL_PROMOTED_TOTAL = 30_143
EXPECTED_FINAL_PK_PROMOTIONS = 14_492
EXPECTED_FINAL_RETRANSLATED = 46_267
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_TARGETED_AFFECTED_ROWS = 24
EXPECTED_UNAFFECTED_ROWS = 52_779
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


PREVIOUS = load_module(BASE_BUILDER_PATH, "selector466_progress_base")
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
            "selector466 progress scaffold has unresolved checkpoint pins: "
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
        and totals.get("runtime_review_pending") == 6_215
        and totals.get("fully_candidate_eligible") == 46_588
        and scope.get("retranslated") == 46_243
        and scope.get("confirmed_non_display") == 345
        and scope.get("runtime_fragment_pending") == 6_215
        and integration.get("sha256") == EXPECTED_PREDECESSOR_PUBLIC_SHA256
        and integration.get("private_integrated_decision_sha256")
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256
        and integration.get("promoted_total") == 30_119
        and integration.get("runtime_review_pending_after") == 6_215
        and integration.get("selector1078_consolidated_layer_included")
        is True
        and sum(int(row["runtime_review_pending"]) for row in segments)
        == 6_215
        and sum(int(row["runtime_review_verified"]) for row in segments)
        == 30_119
        and sum(int(row["decision_count"]) for row in segments)
        == EXPECTED_ROWS
        and sum(int(row["runtime_review_pending"]) for row in batches)
        == 6_215
        and sum(int(row["fully_candidate_eligible"]) for row in batches)
        == 46_588
        and sum(int(row["decision_count"]) for row in batches)
        == EXPECTED_ROWS,
        "post-selector1078 progress predecessor drifted",
    )


def build_progress_delta(
    baseline: Mapping[str, Any],
    checkpoint_report: Mapping[str, Any],
    promotions: set[str],
    target_segments: Mapping[str, str],
    target_batches: Mapping[str, str],
) -> dict[str, Any]:
    alias_report = copy.deepcopy(checkpoint_report)
    alias_report["selector1078_consolidated"] = alias_report[
        "selector466_consolidated"
    ]
    baseline_integration = baseline["runtime_vm_integration"]
    old_layer = copy.deepcopy(
        baseline_integration["selector1078_consolidated"]
    )
    old_included = baseline_integration[
        "selector1078_consolidated_layer_included"
    ]
    old_delta = copy.deepcopy(
        baseline_integration["selector1078_targeted_progress_delta"]
    )
    old_exact = {
        key: copy.deepcopy(value)
        for key, value in baseline_integration["final_exact_layers"].items()
        if key.startswith("selector1078_")
    }
    progress = PREVIOUS.build_progress_delta(
        baseline,
        alias_report,
        promotions,
        target_segments,
        target_batches,
    )
    integration = progress["runtime_vm_integration"]
    new_layer = copy.deepcopy(integration["selector1078_consolidated"])
    new_delta = copy.deepcopy(
        integration["selector1078_targeted_progress_delta"]
    )
    exact = integration["final_exact_layers"]
    new_exact = {
        key.replace("selector1078_", "selector466_", 1):
            copy.deepcopy(value)
        for key, value in exact.items()
        if key.startswith("selector1078_")
    }
    for key in list(exact):
        if key.startswith("selector1078_"):
            del exact[key]
    exact.update(old_exact)
    exact.update(new_exact)
    exact["final_pk_candidate_sha256"] = EXPECTED_FINAL_CANDIDATE_SHA256
    integration["selector1078_consolidated_layer_included"] = old_included
    integration["selector1078_consolidated"] = old_layer
    integration["selector1078_targeted_progress_delta"] = old_delta
    integration["selector466_consolidated_layer_included"] = True
    integration["selector466_consolidated"] = new_layer
    integration["selector466_targeted_progress_delta"] = new_delta
    return progress


def main(argv: Sequence[str] | None = None) -> int:
    arguments = tuple(sys.argv[1:] if argv is None else argv)
    require_checkpoint_pins()
    if "--check" in arguments and EXPECTED_PROGRESS_OUTPUT_SHA256 is None:
        raise RuntimeError(
            "selector466 progress scaffold has unresolved output hash"
        )
    BASE.require(
        BASE.sha256_file(BASE_BUILDER_PATH) == EXPECTED_BASE_BUILDER_SHA256,
        "selector1078 progress delta base drifted",
    )
    BASE.require(
        BASE.sha256_file(DEFAULT_PREDECESSOR_PROGRESS)
        == EXPECTED_PREDECESSOR_PROGRESS_SHA256,
        "post-selector1078 progress snapshot drifted",
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
            "post-selector466 progress alias drifted",
        )
    return result


if __name__ == "__main__":
    raise SystemExit(main())
