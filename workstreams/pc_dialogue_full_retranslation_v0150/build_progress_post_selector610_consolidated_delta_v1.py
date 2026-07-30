#!/usr/bin/env python3
"""Advance source-free progress with the targeted selector-610 delta.

The expensive dialogue preparation and 52,803-row integration rebuild are not
repeated.  Exact promotion coordinates are located in the already frozen
decision segments and review queue only to update their source-free segment
and queue-batch counters.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / WORKSTREAM.name
CHECKPOINT_BUILDER_PATH = (
    WORKSTREAM
    / "build_runtime_vm_post_selector610_consolidated_checkpoint_v1.py"
)
CHECKPOINT_PRIVATE_PATH = (
    DIALOGUE_TMP
    / "runtime_vm_integrated."
    "post_selector610_consolidated_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC_PATH = (
    WORKSTREAM
    / "runtime_vm_integration."
    "post_selector610_consolidated_checkpoint.source_free.v1.json"
)
CLOSURE_DECISIONS_PATH = (
    DIALOGUE_TMP
    / "semantic_overrides"
    / "pk_selector610_consolidated_closure_decisions.private.v1.jsonl"
)
DECISIONS_DIR = DIALOGUE_TMP / "decisions"
REVIEW_QUEUE_PATH = DIALOGUE_TMP / "review_queue.private.v1.jsonl"

DEFAULT_PREDECESSOR_PROGRESS = (
    WORKSTREAM
    / "progress."
    "post_selector568_1096_1174_consolidated.source_free.v1.json"
)
DEFAULT_PROGRESS_OUTPUT = WORKSTREAM / "progress.source_free.v1.json"

EXPECTED_PREDECESSOR_PROGRESS_SHA256 = (
    "C569482EFC544942F989C3323BC534A393923FE7BCB279B56A6E6B5975EC980D"
)
EXPECTED_PREDECESSOR_PRIVATE_SHA256 = (
    "FC157A9907686D0EA6DC6C61C7785E81AC7F750100F2E1CDDE02DBF4F09F2DCA"
)
EXPECTED_PREDECESSOR_PUBLIC_SHA256 = (
    "1FCF033F1F75FC43473152CFB7115D170657519952C19D563C36C3F9BAB4CBD1"
)
EXPECTED_CLOSURE_DECISIONS_SHA256 = (
    "CFEF7B6B8410397DED1FA10AF9C5AAF94D0C1B9C0D0CF1B593527A3A06D15357"
)
EXPECTED_FINAL_CANDIDATE_SHA256 = (
    "F80EA5958757F097885279BAB53A8456758BB99B1CE47E214FE0F54AB7152807"
)

EXPECTED_CHECKPOINT_BUILDER_SHA256 = (
    "95BEB55BCA35AC165FA869C22BB8F243E0C07B479C57BD6F688EAEFD9611C150"
)
EXPECTED_CHECKPOINT_PRIVATE_SHA256 = (
    "0218C3D198C9930C8920ED8DAEB2DDD85987878035AC59DD5ECC8179D38DE12B"
)
EXPECTED_CHECKPOINT_PUBLIC_SHA256 = (
    "42BB33CD2F7553EE3E251DDD78933F85D181F140AA133C5843F6DBDF379B53D3"
)
EXPECTED_PROGRESS_OUTPUT_SHA256: str | None = (
    "03E827757D1D85282043A29B4B112A768D0B3E545245750A61273C1B8CDB83F4"
)

EXPECTED_ROWS = 52_803
EXPECTED_PROMOTIONS = 167
EXPECTED_RENEWALS = 147
EXPECTED_OVERRIDES = 193
EXPECTED_DECISIONS = 314
EXPECTED_FINAL_PENDING = 7_101
EXPECTED_FINAL_ELIGIBLE = 45_702
EXPECTED_FINAL_PROMOTED_TOTAL = 29_233
EXPECTED_FINAL_PK_PROMOTIONS = 13_582
EXPECTED_FINAL_RETRANSLATED = 45_357
EXPECTED_CONFIRMED_NON_DISPLAY = 345


class ProgressDeltaError(ValueError):
    """Raised when the selector-610 source-free progress delta drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProgressDeltaError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    require(path.is_file(), f"required file is absent: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def is_placeholder(value: str | None) -> bool:
    return value is None or value.startswith("__PENDING_")


def validate_output_paths(
    predecessor_progress: Path,
    progress_output: Path,
) -> None:
    require(
        predecessor_progress.resolve(strict=False)
        == DEFAULT_PREDECESSOR_PROGRESS.resolve(strict=False),
        "progress predecessor must use its immutable source-free path",
    )
    require(
        progress_output.resolve(strict=False)
        == DEFAULT_PROGRESS_OUTPUT.resolve(strict=False),
        "progress output must use the canonical source-free path",
    )
    require(
        predecessor_progress.resolve(strict=False)
        != progress_output.resolve(strict=False),
        "progress predecessor and current output must be distinct",
    )


def validate_frozen_inputs() -> Any:
    placeholders = [
        name
        for name, value in (
            (
                "checkpoint_builder",
                EXPECTED_CHECKPOINT_BUILDER_SHA256,
            ),
            (
                "checkpoint_private",
                EXPECTED_CHECKPOINT_PRIVATE_SHA256,
            ),
            (
                "checkpoint_public",
                EXPECTED_CHECKPOINT_PUBLIC_SHA256,
            ),
        )
        if is_placeholder(value)
    ]
    require(
        not placeholders,
        "selector-610 checkpoint pins are not frozen: "
        + ", ".join(placeholders),
    )
    expected = {
        CHECKPOINT_BUILDER_PATH: EXPECTED_CHECKPOINT_BUILDER_SHA256,
        CHECKPOINT_PRIVATE_PATH: EXPECTED_CHECKPOINT_PRIVATE_SHA256,
        CHECKPOINT_PUBLIC_PATH: EXPECTED_CHECKPOINT_PUBLIC_SHA256,
        CLOSURE_DECISIONS_PATH: EXPECTED_CLOSURE_DECISIONS_SHA256,
    }
    for path, digest in expected.items():
        require(sha256_file(path) == digest, f"frozen input drifted: {path}")
    checkpoint = load_module(
        "selector610_delta_checkpoint_for_progress",
        CHECKPOINT_BUILDER_PATH,
    )
    require(
        checkpoint.EXPECTED_PRIVATE_OUTPUT_SHA256
        == EXPECTED_CHECKPOINT_PRIVATE_SHA256
        and checkpoint.EXPECTED_PUBLIC_OUTPUT_SHA256
        == EXPECTED_CHECKPOINT_PUBLIC_SHA256,
        "checkpoint builder output pins drifted",
    )
    return checkpoint


def load_baseline_progress(
    predecessor_progress: Path,
    progress_output: Path,
    *,
    write: bool,
) -> tuple[bytes, dict[str, Any]]:
    if predecessor_progress.is_file():
        content = predecessor_progress.read_bytes()
    else:
        require(
            write
            and progress_output.is_file()
            and sha256_file(progress_output)
            == EXPECTED_PREDECESSOR_PROGRESS_SHA256,
            "immutable progress predecessor is absent",
        )
        content = progress_output.read_bytes()
    require(
        sha256_bytes(content) == EXPECTED_PREDECESSOR_PROGRESS_SHA256,
        "post-selector568/1096/1174 progress predecessor drifted",
    )
    progress = json.loads(content.decode("ascii"))
    require(isinstance(progress, dict), "progress predecessor must be an object")
    validate_baseline_progress(progress)
    return content, progress


def validate_baseline_progress(progress: Mapping[str, Any]) -> None:
    totals = progress.get("totals", {})
    integration = progress.get("runtime_vm_integration", {})
    scope = totals.get("scope_classification_counts", {})
    segments = progress.get("segments", [])
    batches = progress.get("queue_batch_coverage", [])
    require(
        progress.get("mechanical_candidate_universe") == EXPECTED_ROWS
        and totals.get("semantic_review_approved") == EXPECTED_ROWS
        and totals.get("runtime_review_pending") == 7_268
        and totals.get("fully_candidate_eligible") == 45_535
        and scope.get("retranslated") == 45_190
        and scope.get("confirmed_non_display")
        == EXPECTED_CONFIRMED_NON_DISPLAY
        and scope.get("runtime_fragment_pending") == 7_268
        and integration.get("sha256")
        == EXPECTED_PREDECESSOR_PUBLIC_SHA256
        and integration.get("private_integrated_decision_sha256")
        == EXPECTED_PREDECESSOR_PRIVATE_SHA256
        and integration.get("promoted_total") == 29_066
        and integration.get("runtime_review_pending_after") == 7_268
        and isinstance(segments, list)
        and isinstance(batches, list)
        and sum(int(row["runtime_review_pending"]) for row in segments)
        == 7_268
        and sum(int(row["runtime_review_verified"]) for row in segments)
        == 29_066
        and sum(int(row["decision_count"]) for row in segments)
        == EXPECTED_ROWS
        and sum(int(row["runtime_review_pending"]) for row in batches)
        == 7_268
        and sum(int(row["fully_candidate_eligible"]) for row in batches)
        == 45_535
        and sum(int(row["decision_count"]) for row in batches)
        == EXPECTED_ROWS,
        "progress predecessor counts/lineage drifted",
    )


def load_promotions(checkpoint: Any) -> set[str]:
    decisions = checkpoint.load_closure_decisions()
    promotions = {
        coordinate
        for coordinate, row in decisions.items()
        if "runtime_promotion" in row[checkpoint.UPDATE_ACTION_FIELD]
    }
    require(
        len(decisions) == EXPECTED_DECISIONS
        and len(promotions) == EXPECTED_PROMOTIONS,
        "selector-610 progress decision universe drifted",
    )
    return promotions


def segment_id(path: Path) -> str:
    suffix = ".private.v1.jsonl"
    require(path.name.endswith(suffix), f"unexpected segment path: {path}")
    return path.name[: -len(suffix)]


def locate_target_segments(promotions: set[str]) -> dict[str, str]:
    located: dict[str, str] = {}
    for path in sorted(DECISIONS_DIR.glob("*.private.v1.jsonl")):
        current_segment = segment_id(path)
        with path.open("r", encoding="utf-8") as stream:
            for line in stream:
                if not line:
                    continue
                row = json.loads(line)
                if row.get("resource") != "pk_msggame":
                    continue
                coordinate = str(row.get("coordinate"))
                if coordinate not in promotions:
                    continue
                require(
                    coordinate not in located,
                    f"promotion appears in multiple segments: {coordinate}",
                )
                located[coordinate] = current_segment
    require(
        set(located) == promotions,
        "not every selector-610 promotion maps to a decision segment",
    )
    return located


def locate_target_batches(promotions: set[str]) -> dict[str, str]:
    located: dict[str, str] = {}
    with REVIEW_QUEUE_PATH.open("r", encoding="utf-8") as stream:
        for line in stream:
            if not line:
                continue
            row = json.loads(line)
            if row.get("resource") != "pk_msggame":
                continue
            batch_id = str(row.get("batch_id"))
            for target in row.get("target_literals", []):
                coordinate = str(target.get("coordinate"))
                if coordinate not in promotions:
                    continue
                require(
                    coordinate not in located,
                    f"promotion appears in multiple queue batches: {coordinate}",
                )
                located[coordinate] = batch_id
    require(
        set(located) == promotions,
        "not every selector-610 promotion maps to a review queue batch",
    )
    return located


def update_counter_row(row: dict[str, Any], promotion_count: int) -> None:
    scope = row["scope_classification_counts"]
    require(
        int(row["runtime_review_pending"]) >= promotion_count
        and int(scope["runtime_fragment_pending"]) >= promotion_count,
        "targeted progress counter would underflow",
    )
    row["runtime_review_pending"] -= promotion_count
    if "runtime_review_verified" in row:
        row["runtime_review_verified"] += promotion_count
    if "fully_candidate_eligible" in row:
        row["fully_candidate_eligible"] += promotion_count
    scope["runtime_fragment_pending"] -= promotion_count
    scope["retranslated"] += promotion_count


def build_progress_delta(
    baseline: Mapping[str, Any],
    checkpoint_report: Mapping[str, Any],
    promotions: set[str],
    target_segments: Mapping[str, str],
    target_batches: Mapping[str, str],
) -> dict[str, Any]:
    progress = copy.deepcopy(baseline)
    segment_counts = Counter(target_segments.values())
    batch_counts = Counter(target_batches.values())
    segments = {
        str(row["segment_id"]): row for row in progress["segments"]
    }
    batches = {
        str(row["batch_id"]): row
        for row in progress["queue_batch_coverage"]
    }
    require(
        set(segment_counts) <= set(segments)
        and set(batch_counts) <= set(batches),
        "targeted progress segment/batch is absent",
    )
    for target, count in segment_counts.items():
        update_counter_row(segments[target], count)
    for target, count in batch_counts.items():
        update_counter_row(batches[target], count)

    totals = progress["totals"]
    total_scope = totals["scope_classification_counts"]
    totals["runtime_review_pending"] = EXPECTED_FINAL_PENDING
    totals["fully_candidate_eligible"] = EXPECTED_FINAL_ELIGIBLE
    total_scope["runtime_fragment_pending"] = EXPECTED_FINAL_PENDING
    total_scope["retranslated"] = EXPECTED_FINAL_RETRANSLATED

    checkpoint_layer = checkpoint_report["selector610_consolidated"]
    checkpoint_result = checkpoint_report["result"]
    integration = progress["runtime_vm_integration"]
    integration.update(
        {
            "schema": checkpoint_report["schema"],
            "path": str(
                CHECKPOINT_PUBLIC_PATH.relative_to(REPO)
            ).replace("\\", "/"),
            "sha256": EXPECTED_CHECKPOINT_PUBLIC_SHA256,
            "private_integrated_decision_sha256":
                EXPECTED_CHECKPOINT_PRIVATE_SHA256,
            "promoted_total": EXPECTED_FINAL_PROMOTED_TOTAL,
            "runtime_review_pending_after": EXPECTED_FINAL_PENDING,
            "selector610_consolidated_layer_included": True,
            "selector610_consolidated": checkpoint_layer,
        }
    )
    exact_layers = integration["final_exact_layers"]
    exact_layers["final_pk_candidate_sha256"] = (
        EXPECTED_FINAL_CANDIDATE_SHA256
    )
    exact_layers.update(
        {
            "selector610_consolidated_decision_rows":
                EXPECTED_DECISIONS,
            "selector610_consolidated_promotion_count":
                EXPECTED_PROMOTIONS,
            "selector610_consolidated_renewal_count":
                EXPECTED_RENEWALS,
            "selector610_consolidated_override_count":
                EXPECTED_OVERRIDES,
            "selector610_consolidated_decision_sha256":
                checkpoint_layer["decision_coordinate_sha256"],
            "selector610_consolidated_final_candidate_sha256":
                EXPECTED_FINAL_CANDIDATE_SHA256,
        }
    )
    require(
        checkpoint_result["runtime_review_pending"]
        == EXPECTED_FINAL_PENDING
        and checkpoint_result["fully_candidate_eligible"]
        == EXPECTED_FINAL_ELIGIBLE
        and checkpoint_result["promoted_total"]
        == EXPECTED_FINAL_PROMOTED_TOTAL
        and checkpoint_result["pk_msggame_promotion_count"]
        == EXPECTED_FINAL_PK_PROMOTIONS,
        "checkpoint result and progress delta disagree",
    )
    validate_final_progress(
        progress,
        changed_segment_count=len(segment_counts),
        changed_batch_count=len(batch_counts),
    )
    progress["runtime_vm_integration"][
        "selector610_targeted_progress_delta"
    ] = {
        "promotion_count": EXPECTED_PROMOTIONS,
        "changed_segment_count": len(segment_counts),
        "changed_batch_count": len(batch_counts),
        "full_dialogue_rebuild_performed": False,
        "steam_write_performed": False,
    }
    return progress


def validate_final_progress(
    progress: Mapping[str, Any],
    *,
    changed_segment_count: int,
    changed_batch_count: int,
) -> None:
    totals = progress["totals"]
    scope = totals["scope_classification_counts"]
    segments = progress["segments"]
    batches = progress["queue_batch_coverage"]
    require(
        changed_segment_count > 0
        and changed_batch_count > 0
        and totals["semantic_review_approved"] == EXPECTED_ROWS
        and totals["runtime_review_pending"] == EXPECTED_FINAL_PENDING
        and totals["fully_candidate_eligible"] == EXPECTED_FINAL_ELIGIBLE
        and scope["confirmed_non_display"]
        == EXPECTED_CONFIRMED_NON_DISPLAY
        and scope["retranslated"] == EXPECTED_FINAL_RETRANSLATED
        and scope["runtime_fragment_pending"] == EXPECTED_FINAL_PENDING
        and sum(int(row["runtime_review_pending"]) for row in segments)
        == EXPECTED_FINAL_PENDING
        and sum(int(row["runtime_review_verified"]) for row in segments)
        == EXPECTED_FINAL_PROMOTED_TOTAL
        and sum(int(row["runtime_review_pending"]) for row in batches)
        == EXPECTED_FINAL_PENDING
        and sum(int(row["fully_candidate_eligible"]) for row in batches)
        == EXPECTED_FINAL_ELIGIBLE,
        "final selector-610 progress counts drifted",
    )


def serialized_progress(progress: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(progress, ensure_ascii=True, indent=2) + "\n"
    ).encode("ascii")


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="wb",
        prefix=path.name + ".",
        suffix=".tmp",
        dir=path.parent,
        delete=False,
    ) as stream:
        temporary = Path(stream.name)
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--predecessor-progress",
        type=Path,
        default=DEFAULT_PREDECESSOR_PROGRESS,
    )
    parser.add_argument(
        "--progress-output",
        type=Path,
        default=DEFAULT_PROGRESS_OUTPUT,
    )
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--bootstrap-output-pins",
        action="store_true",
        help="permit the first deterministic write before progress hash is pinned",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    require(args.write or args.check, "choose --write, --check, or both")
    validate_output_paths(args.predecessor_progress, args.progress_output)
    checkpoint = validate_frozen_inputs()
    predecessor_content, baseline = load_baseline_progress(
        args.predecessor_progress,
        args.progress_output,
        write=args.write,
    )
    checkpoint_report = json.loads(
        CHECKPOINT_PUBLIC_PATH.read_text(encoding="ascii")
    )
    promotions = load_promotions(checkpoint)
    target_segments = locate_target_segments(promotions)
    target_batches = locate_target_batches(promotions)
    progress = build_progress_delta(
        baseline,
        checkpoint_report,
        promotions,
        target_segments,
        target_batches,
    )
    content = serialized_progress(progress)
    output_sha256 = sha256_bytes(content)
    require(
        EXPECTED_PROGRESS_OUTPUT_SHA256 is not None
        or args.bootstrap_output_pins,
        "progress output hash is not pinned; use --bootstrap-output-pins once",
    )
    require(
        not args.check or EXPECTED_PROGRESS_OUTPUT_SHA256 is not None,
        "--check requires a frozen progress output hash",
    )
    if EXPECTED_PROGRESS_OUTPUT_SHA256 is not None:
        require(
            output_sha256 == EXPECTED_PROGRESS_OUTPUT_SHA256,
            "selector-610 progress output digest drifted",
        )
    if args.write:
        if not args.predecessor_progress.is_file():
            atomic_write(args.predecessor_progress, predecessor_content)
        atomic_write(args.progress_output, content)
    if args.check:
        require(
            sha256_file(args.predecessor_progress)
            == EXPECTED_PREDECESSOR_PROGRESS_SHA256,
            "written immutable progress predecessor drifted",
        )
        require(
            sha256_file(args.progress_output)
            == EXPECTED_PROGRESS_OUTPUT_SHA256,
            "written selector-610 progress output drifted",
        )
    print(
        "PASS "
        f"progress_sha256={output_sha256} "
        f"promoted={EXPECTED_PROMOTIONS} "
        f"pending={EXPECTED_FINAL_PENDING} "
        "full_dialogue_rebuild=false steam_write=false"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProgressDeltaError as error:
        raise SystemExit(f"ERROR: {error}") from error
