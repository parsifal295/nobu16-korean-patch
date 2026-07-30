#!/usr/bin/env python3
"""Targeted tests for the selector-142 surgical progress delta."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BUILDER_PATH = (
    WORKSTREAM / "build_progress_post_selector142_consolidated_delta_v1.py"
)


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "selector142_progress_tested", BUILDER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


B = load_builder()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="ascii"))


def test_builder_check() -> None:
    result = subprocess.run(
        [sys.executable, str(BUILDER_PATH), "--check"],
        cwd=REPO,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0, result.stderr
    assert "promoted=116 pending=6645" in result.stdout
    assert "full_dialogue_rebuild=false steam_write=false" in result.stdout


def test_predecessor_snapshot_and_output_hashes() -> None:
    assert sha256_file(B.DEFAULT_PREDECESSOR_PROGRESS) == (
        B.EXPECTED_PREDECESSOR_PROGRESS_SHA256
    )
    assert sha256_file(B.DEFAULT_PROGRESS_OUTPUT) == (
        B.EXPECTED_PROGRESS_OUTPUT_SHA256
    )
    assert sha256_file(B.IMMUTABLE_PROGRESS_OUTPUT) == (
        B.EXPECTED_PROGRESS_OUTPUT_SHA256
    )


def test_progress_totals() -> None:
    progress = load_json(B.DEFAULT_PROGRESS_OUTPUT)
    totals = progress["totals"]
    scope = totals["scope_classification_counts"]
    assert totals["semantic_review_approved"] == 52_803
    assert totals["runtime_review_pending"] == 6_645
    assert totals["fully_candidate_eligible"] == 46_158
    assert scope["retranslated"] == 45_813
    assert scope["confirmed_non_display"] == 345
    assert scope["runtime_fragment_pending"] == 6_645


def test_segment_and_batch_delta_sums() -> None:
    before = load_json(B.DEFAULT_PREDECESSOR_PROGRESS)
    after = load_json(B.DEFAULT_PROGRESS_OUTPUT)
    before_segments = {row["segment_id"]: row for row in before["segments"]}
    after_segments = {row["segment_id"]: row for row in after["segments"]}
    before_batches = {
        row["batch_id"]: row for row in before["queue_batch_coverage"]
    }
    after_batches = {
        row["batch_id"]: row for row in after["queue_batch_coverage"]
    }
    segment_delta = sum(
        before_segments[key]["runtime_review_pending"]
        - after_segments[key]["runtime_review_pending"]
        for key in before_segments
    )
    batch_delta = sum(
        before_batches[key]["runtime_review_pending"]
        - after_batches[key]["runtime_review_pending"]
        for key in before_batches
    )
    assert segment_delta == batch_delta == 116


def test_prior_layers_preserved_and_selector142_added() -> None:
    before = load_json(B.DEFAULT_PREDECESSOR_PROGRESS)["runtime_vm_integration"]
    after = load_json(B.DEFAULT_PROGRESS_OUTPUT)["runtime_vm_integration"]
    for prefix in ("selector550_", "selector748_", "selector1126_"):
        for key, value in before.items():
            if key.startswith(prefix):
                assert after[key] == value
    assert after["selector142_consolidated_layer_included"] is True
    layer = after["selector142_consolidated"]
    assert layer["updated_coordinate_count"] == 162
    assert layer["promotion_count"] == 116
    assert layer["source_only_action_count"] == 0
    delta = after["selector142_targeted_progress_delta"]
    assert delta["promotion_count"] == 116
    assert delta["full_dialogue_rebuild_performed"] is False
    assert after["sha256"] == B.EXPECTED_CHECKPOINT_PUBLIC_SHA256
    assert after["private_integrated_decision_sha256"] == (
        B.EXPECTED_CHECKPOINT_PRIVATE_SHA256
    )
    assert after["promoted_total"] == 29_689


def test_source_free_and_no_coordinates() -> None:
    cjk = re.compile(
        r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
        r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]"
    )
    coordinate = re.compile(r"\b\d+:\d+(?::\d+){0,2}\b")
    for path in (BUILDER_PATH, SCRIPT):
        content = path.read_text(encoding="ascii")
        assert cjk.search(content) is None
        assert coordinate.search(content) is None
    for path in (B.DEFAULT_PREDECESSOR_PROGRESS, B.DEFAULT_PROGRESS_OUTPUT):
        content = path.read_text(encoding="ascii")
        assert cjk.search(content) is None
        assert '"translation"' not in content
        assert '"reviewed_translation"' not in content


def main() -> int:
    tests = [
        value
        for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"PASS {len(tests)}/{len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
