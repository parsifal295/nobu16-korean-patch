#!/usr/bin/env python3
"""Advance source-free progress with the 1,254-row local-static delta."""

from __future__ import annotations

import argparse
import copy
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Iterable, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
REPO = next(
    parent
    for parent in SCRIPT.parents
    if (parent / "workstreams" / "pc_dialogue_full_retranslation_v0150").is_dir()
)
TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
DIALOGUE = REPO / "workstreams" / "pc_dialogue_full_retranslation_v0150"
PK_AUDIT = REPO / "workstreams" / "pk_msggame_runtime_vm_audit_v1"

PREDECESSOR_PROGRESS = (
    DIALOGUE
    / "progress.post_selector292_wave7_root_sharded_consolidated.source_free.v1.json"
)
CHECKPOINT_BUILDER = (
    DIALOGUE / "build_runtime_vm_post_wave7_local_static_checkpoint_v1.py"
)
CHECKPOINT_PRIVATE = (
    TMP / "runtime_vm_integrated.post_wave7_local_static_checkpoint.private.v1.jsonl"
)
CHECKPOINT_PUBLIC = (
    DIALOGUE
    / "runtime_vm_integration.post_wave7_local_static_checkpoint.source_free.v1.json"
)
STATIC_BUILDER = (
    PK_AUDIT / "build_pk_msggame_post_wave7_local_static_closure_v1.py"
)
STATIC_DECISIONS = (
    TMP
    / "decisions"
    / "runtime_verification_overlays"
    / "pk_msggame_post_wave7_local_static_runtime_verified_decisions.private.v1.jsonl"
)
STATIC_EVIDENCE = (
    TMP / "pk_msggame_post_wave7_local_static_runtime_verified_evidence.private.v1.json"
)
STATIC_PUBLIC = (
    PK_AUDIT
    / "public"
    / "pk_msggame_post_wave7_local_static_runtime_verified.source_free.v1.json"
)
DECISIONS_DIR = TMP / "decisions"
REVIEW_QUEUE = TMP / "review_queue.private.v1.jsonl"
DEFAULT_OUTPUT = (
    DIALOGUE / "progress.post_wave7_local_static.source_free.v1.json"
)
ALIAS_OUTPUT = DIALOGUE / "progress.source_free.v1.json"

EXPECTED_INPUT_SHA256 = {
    "predecessor_progress": "53423D5B16ED9EE60619989F09A71CDD7194B70CDB698AA9DDE606AE2145EF0B",
    "checkpoint_builder": "835B7920C7B3EF44ED9B770A402E21C230B8687F3EA8A95758C644B8BA436C9A",
    "checkpoint_private": "502C274DB571359D6C028381F1E77CE70A0AA191CAEC39FD41499044537964ED",
    "checkpoint_public": "CB33295B6416CC3F76041D502C0DA868773CCED8AC6337B60F3D45A30EFBDD84",
    "static_builder": "372146CEDED272C1D4B00EA9B647EDA54973087103BACDA279225F9CB32B0ABC",
    "static_decisions": "1F026C793D9B8E0A8D5139B5B1B1EFFC7B23899244AE6C38F7C37911E7D423FE",
    "static_evidence": "CFC6ADCCE55D3374AF69D4B3D6002DE6E013E6BFD0E9685915E2F7457713C7A2",
    "static_public": "82B3A5E1C2B8E7558E1992BA65D0B001EC6778B60C9BC12EB2A5483F887E60F4",
}
EXPECTED_OUTPUT_SHA256: str | None = (
    "F74957421DB48A2474D18E59D1B71C8422321FBA29AC14A3415E02E38836F94E"
)

EXPECTED_ROWS = 52_803
EXPECTED_PROMOTIONS = 1_254
EXPECTED_PENDING_BEFORE = 5_901
EXPECTED_PENDING_AFTER = 4_647
EXPECTED_ELIGIBLE_BEFORE = 46_902
EXPECTED_ELIGIBLE_AFTER = 48_156
EXPECTED_PROMOTED_BEFORE = 30_433
EXPECTED_PROMOTED_AFTER = 31_687
EXPECTED_PK_PROMOTIONS_AFTER = 16_036
EXPECTED_RETRANSLATED_BEFORE = 46_557
EXPECTED_RETRANSLATED_AFTER = 47_811
EXPECTED_CONFIRMED_NON_DISPLAY = 345
EXPECTED_CANDIDATE_SHA256 = (
    "DAB40F2AA8095E67550B69213A53CC777B96B17071FFF5B860CFAEE1A868D7E0"
)
EXPECTED_COORDINATE_SHA256 = (
    "7AD1E0AE524392364726462241867FBFA16A937826B016EA3C719AAB7DA3F7C5"
)


class ProgressError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProgressError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def atomic_write(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=True, indent=2) + "\n").encode("ascii")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"not an object: {path}")
    return value


def parse_coordinate(value: str) -> tuple[int, int, int]:
    parts = tuple(map(int, value.split(":")))
    require(len(parts) == 3, f"invalid coordinate: {value}")
    return parts


def coordinate_digest(values: Iterable[str]) -> str:
    payload = "".join(
        f"{value}\n" for value in sorted(set(values), key=parse_coordinate)
    ).encode("ascii")
    return sha256_bytes(payload)


def load_promotions() -> set[str]:
    promotions: set[str] = set()
    for line in STATIC_DECISIONS.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        row = json.loads(line)
        coordinate = str(row["coordinate"])
        require(
            row.get("resource") == "pk_msggame"
            and row.get("action") == "runtime_promotion"
            and coordinate not in promotions,
            f"invalid promotion: {coordinate}",
        )
        promotions.add(coordinate)
    require(
        len(promotions) == EXPECTED_PROMOTIONS
        and coordinate_digest(promotions) == EXPECTED_COORDINATE_SHA256,
        "promotion universe drift",
    )
    return promotions


def segment_id(path: Path) -> str:
    suffix = ".private.v1.jsonl"
    require(path.name.endswith(suffix), f"invalid segment path: {path}")
    return path.name[: -len(suffix)]


def locate_target_segments(promotions: set[str]) -> dict[str, str]:
    located: dict[str, str] = {}
    for path in sorted(DECISIONS_DIR.glob("*.private.v1.jsonl")):
        current_segment = segment_id(path)
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line:
                    continue
                row = json.loads(line)
                if row.get("resource") != "pk_msggame":
                    continue
                coordinate = str(row.get("coordinate"))
                if coordinate not in promotions:
                    continue
                require(coordinate not in located, f"duplicate segment: {coordinate}")
                located[coordinate] = current_segment
    require(set(located) == promotions, "not every promotion maps to a segment")
    return located


def locate_target_batches(promotions: set[str]) -> dict[str, str]:
    located: dict[str, str] = {}
    with REVIEW_QUEUE.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line:
                continue
            row = json.loads(line)
            if row.get("resource") != "pk_msggame":
                continue
            batch_id = str(row["batch_id"])
            for target in row.get("target_literals", []):
                coordinate = str(target.get("coordinate"))
                if coordinate not in promotions:
                    continue
                require(coordinate not in located, f"duplicate batch: {coordinate}")
                located[coordinate] = batch_id
    require(set(located) == promotions, "not every promotion maps to a batch")
    return located


def update_counter_row(row: dict[str, Any], count: int) -> None:
    scope = row["scope_classification_counts"]
    require(
        int(row["runtime_review_pending"]) >= count
        and int(scope["runtime_fragment_pending"]) >= count,
        "progress counter underflow",
    )
    row["runtime_review_pending"] -= count
    if "runtime_review_verified" in row:
        row["runtime_review_verified"] += count
    if "fully_candidate_eligible" in row:
        row["fully_candidate_eligible"] += count
    scope["runtime_fragment_pending"] -= count
    scope["retranslated"] += count


def assert_source_free(value: Any, path: str = "$") -> None:
    forbidden = {
        "translation",
        "translations",
        "dialogue",
        "dialogue_body",
        "source_text",
        "current_text",
        "candidate_text",
        "japanese",
        "korean",
    }
    cjk = re.compile(
        r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7a3]"
    )
    if isinstance(value, dict):
        for key, child in value.items():
            require(str(key) not in forbidden, f"source-bearing key: {path}.{key}")
            assert_source_free(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_source_free(child, f"{path}[{index}]")
    elif isinstance(value, str):
        require(cjk.search(value) is None, f"CJK leaked: {path}")


def validate_baseline(progress: Mapping[str, Any]) -> None:
    totals = progress["totals"]
    scope = totals["scope_classification_counts"]
    integration = progress["runtime_vm_integration"]
    require(
        progress["mechanical_candidate_universe"] == EXPECTED_ROWS
        and totals["semantic_review_approved"] == EXPECTED_ROWS
        and totals["runtime_review_pending"] == EXPECTED_PENDING_BEFORE
        and totals["fully_candidate_eligible"] == EXPECTED_ELIGIBLE_BEFORE
        and scope["retranslated"] == EXPECTED_RETRANSLATED_BEFORE
        and scope["runtime_fragment_pending"] == EXPECTED_PENDING_BEFORE
        and scope["confirmed_non_display"] == EXPECTED_CONFIRMED_NON_DISPLAY
        and integration["promoted_total"] == EXPECTED_PROMOTED_BEFORE
        and integration["runtime_review_pending_after"] == EXPECTED_PENDING_BEFORE
        and integration["private_integrated_decision_sha256"]
        == "B1CF7F4523DE9411BA5172E7C9DEA946C7646085C83A1480C51807E2DD0C90E7"
        and integration["sha256"]
        == "96E03D3EA32FAB5E6701DB75060038A5E967F9617EB0E22E5C91352944626930"
        and integration["final_exact_layers"]["final_pk_candidate_sha256"]
        == EXPECTED_CANDIDATE_SHA256,
        "baseline progress drift",
    )


def validate_final(
    progress: Mapping[str, Any],
    changed_segment_count: int,
    changed_batch_count: int,
) -> None:
    totals = progress["totals"]
    scope = totals["scope_classification_counts"]
    segments = progress["segments"]
    batches = progress["queue_batch_coverage"]
    integration = progress["runtime_vm_integration"]
    require(
        changed_segment_count > 0
        and changed_batch_count > 0
        and totals["semantic_review_approved"] == EXPECTED_ROWS
        and totals["runtime_review_pending"] == EXPECTED_PENDING_AFTER
        and totals["fully_candidate_eligible"] == EXPECTED_ELIGIBLE_AFTER
        and scope["retranslated"] == EXPECTED_RETRANSLATED_AFTER
        and scope["runtime_fragment_pending"] == EXPECTED_PENDING_AFTER
        and scope["confirmed_non_display"] == EXPECTED_CONFIRMED_NON_DISPLAY
        and sum(int(row["runtime_review_pending"]) for row in segments)
        == EXPECTED_PENDING_AFTER
        and sum(int(row["runtime_review_verified"]) for row in segments)
        == EXPECTED_PROMOTED_AFTER
        and sum(int(row["runtime_review_pending"]) for row in batches)
        == EXPECTED_PENDING_AFTER
        and sum(int(row["fully_candidate_eligible"]) for row in batches)
        == EXPECTED_ELIGIBLE_AFTER
        and integration["promoted_total"] == EXPECTED_PROMOTED_AFTER
        and integration["runtime_review_pending_after"] == EXPECTED_PENDING_AFTER,
        "final progress drift",
    )


def build_output() -> tuple[bytes, dict[str, Any]]:
    inputs = {
        "predecessor_progress": sha256_file(PREDECESSOR_PROGRESS),
        "checkpoint_builder": sha256_file(CHECKPOINT_BUILDER),
        "checkpoint_private": sha256_file(CHECKPOINT_PRIVATE),
        "checkpoint_public": sha256_file(CHECKPOINT_PUBLIC),
        "static_builder": sha256_file(STATIC_BUILDER),
        "static_decisions": sha256_file(STATIC_DECISIONS),
        "static_evidence": sha256_file(STATIC_EVIDENCE),
        "static_public": sha256_file(STATIC_PUBLIC),
    }
    require(inputs == EXPECTED_INPUT_SHA256, f"input drift: {inputs}")
    baseline = load_json(PREDECESSOR_PROGRESS)
    checkpoint = load_json(CHECKPOINT_PUBLIC)
    validate_baseline(baseline)
    promotions = load_promotions()
    target_segments = locate_target_segments(promotions)
    target_batches = locate_target_batches(promotions)

    progress = copy.deepcopy(baseline)
    segment_counts = Counter(target_segments.values())
    batch_counts = Counter(target_batches.values())
    segments = {str(row["segment_id"]): row for row in progress["segments"]}
    batches = {
        str(row["batch_id"]): row for row in progress["queue_batch_coverage"]
    }
    require(
        set(segment_counts) <= set(segments)
        and set(batch_counts) <= set(batches),
        "target segment/batch absent",
    )
    for target, count in segment_counts.items():
        update_counter_row(segments[target], count)
    for target, count in batch_counts.items():
        update_counter_row(batches[target], count)

    totals = progress["totals"]
    totals["runtime_review_pending"] = EXPECTED_PENDING_AFTER
    totals["fully_candidate_eligible"] = EXPECTED_ELIGIBLE_AFTER
    totals["scope_classification_counts"][
        "runtime_fragment_pending"
    ] = EXPECTED_PENDING_AFTER
    totals["scope_classification_counts"][
        "retranslated"
    ] = EXPECTED_RETRANSLATED_AFTER

    integration = progress["runtime_vm_integration"]
    integration.update(
        {
            "schema": checkpoint["schema"],
            "path": str(CHECKPOINT_PUBLIC.relative_to(REPO)).replace("\\", "/"),
            "sha256": EXPECTED_INPUT_SHA256["checkpoint_public"],
            "private_integrated_decision_sha256":
                EXPECTED_INPUT_SHA256["checkpoint_private"],
            "promoted_total": EXPECTED_PROMOTED_AFTER,
            "runtime_review_pending_after": EXPECTED_PENDING_AFTER,
            "post_wave7_local_static_layer_included": True,
            "post_wave7_local_static": copy.deepcopy(checkpoint["targeted_delta"]),
            "post_wave7_local_static_targeted_progress_delta": {
                "promotion_count": EXPECTED_PROMOTIONS,
                "semantic_override_count": 0,
                "changed_segment_count": len(segment_counts),
                "changed_batch_count": len(batch_counts),
                "candidate_byte_changes": 0,
                "full_dialogue_rebuild_performed": False,
                "steam_write_performed": False,
            },
        }
    )
    exact = integration["final_exact_layers"]
    exact["final_pk_candidate_sha256"] = EXPECTED_CANDIDATE_SHA256
    exact.update(
        {
            "post_wave7_local_static_decision_rows": EXPECTED_PROMOTIONS,
            "post_wave7_local_static_promotion_count": EXPECTED_PROMOTIONS,
            "post_wave7_local_static_override_count": 0,
            "post_wave7_local_static_decision_sha256":
                EXPECTED_COORDINATE_SHA256,
            "post_wave7_local_static_final_candidate_sha256":
                EXPECTED_CANDIDATE_SHA256,
            "post_wave7_local_static_checkpoint_private_sha256":
                EXPECTED_INPUT_SHA256["checkpoint_private"],
            "post_wave7_local_static_checkpoint_public_sha256":
                EXPECTED_INPUT_SHA256["checkpoint_public"],
            "post_wave7_local_static_pk_msggame_promotion_count":
                EXPECTED_PK_PROMOTIONS_AFTER,
        }
    )
    validate_final(progress, len(segment_counts), len(batch_counts))
    assert_source_free(progress)
    return json_bytes(progress), {
        "status": "PASS",
        "promotions": EXPECTED_PROMOTIONS,
        "pending": EXPECTED_PENDING_AFTER,
        "eligible": EXPECTED_ELIGIBLE_AFTER,
        "changed_segments": len(segment_counts),
        "changed_batches": len(batch_counts),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--bootstrap", action="store_true")
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    payload, report = build_output()
    digest = sha256_bytes(payload)
    if not args.bootstrap:
        require(EXPECTED_OUTPUT_SHA256 is not None, "unfrozen progress output")
        require(digest == EXPECTED_OUTPUT_SHA256, "progress output drift")
    if args.bootstrap or args.write:
        atomic_write(args.output, payload)
        if args.output.resolve() == DEFAULT_OUTPUT.resolve():
            atomic_write(ALIAS_OUTPUT, payload)
    else:
        require(args.output.read_bytes() == payload, "progress file drift")
        if args.output.resolve() == DEFAULT_OUTPUT.resolve():
            require(ALIAS_OUTPUT.read_bytes() == payload, "progress alias drift")
    print(json.dumps({**report, "progress_sha256": digest}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
