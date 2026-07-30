#!/usr/bin/env python3
"""Targeted tests for the immutable selector-142 ledger checkpoint."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BUILDER_PATH = (
    WORKSTREAM / "build_runtime_vm_post_selector142_consolidated_checkpoint_v1.py"
)


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "selector142_checkpoint_tested", BUILDER_PATH
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
    assert "full_integration_rebuild=false steam_write=false" in result.stdout


def test_frozen_output_hashes() -> None:
    assert sha256_file(B.DEFAULT_PRIVATE_OUTPUT) == (
        B.EXPECTED_PRIVATE_OUTPUT_SHA256
    )
    assert sha256_file(B.DEFAULT_PUBLIC_OUTPUT) == (
        B.EXPECTED_PUBLIC_OUTPUT_SHA256
    )


def test_targeted_raw_copy_delta() -> None:
    predecessor = B.PREDECESSOR_PRIVATE_PATH.read_bytes().splitlines(
        keepends=True
    )
    current = B.DEFAULT_PRIVATE_OUTPUT.read_bytes().splitlines(keepends=True)
    assert len(predecessor) == len(current) == 52_803
    changed = [
        index
        for index, pair in enumerate(zip(predecessor, current))
        if pair[0] != pair[1]
    ]
    assert len(changed) == 162
    assert 52_803 - len(changed) == 52_641
    for index in changed:
        before = json.loads(predecessor[index].decode("utf-8"))
        after = json.loads(current[index].decode("utf-8"))
        assert before["resource"] == after["resource"] == "pk_msggame"
        assert before["coordinate"] == after["coordinate"]
        assert before["scope_classification"] != "confirmed_non_display"
        assert after["runtime_review"] == "verified"
        assert "selector142_consolidated_update_action" in after


def test_scope_partition_is_preserved() -> None:
    rows = [
        json.loads(line)
        for line in B.DEFAULT_PRIVATE_OUTPUT.read_text(
            encoding="utf-8"
        ).splitlines()
        if line
    ]
    assert Counter(row["runtime_review"] for row in rows) == {
        "verified": 29_689,
        "not_required": 16_469,
        "pending": 6_645,
    }
    assert Counter(row["scope_classification"] for row in rows) == {
        "retranslated": 45_813,
        "confirmed_non_display": 345,
        "runtime_fragment_pending": 6_645,
    }


def test_public_counts_and_lineage() -> None:
    report = load_json(B.DEFAULT_PUBLIC_OUTPUT)
    assert report["inputs"]["predecessor_private_sha256"] == (
        B.EXPECTED_PREDECESSOR_PRIVATE_SHA256
    )
    layer = report["selector142_consolidated"]
    assert layer["owner_decision_row_count"] == 162
    assert layer["updated_coordinate_count"] == 162
    assert layer["promotion_count"] == 116
    assert layer["source_only_action_count"] == 0
    assert report["result"]["runtime_review_pending"] == 6_645
    assert report["result"]["fully_candidate_eligible"] == 46_158
    assert report["result"]["promoted_total"] == 29_689
    assert report["result"]["pk_msggame_promotion_count"] == 14_038
    assert report["validation"]["full_integration_engine_invoked"] is False
    assert report["validation"]["confirmed_non_display_rows_preserved"]


def test_source_free_and_no_coordinates() -> None:
    cjk = re.compile(
        r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
        r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]"
    )
    coordinate = re.compile(r"\b\d+:\d+(?::\d+){0,2}\b")
    for path in (BUILDER_PATH, SCRIPT, B.DEFAULT_PUBLIC_OUTPUT):
        content = path.read_text(encoding="utf-8")
        assert cjk.search(content) is None
        assert coordinate.search(content) is None
    public = B.DEFAULT_PUBLIC_OUTPUT.read_text(encoding="ascii")
    assert '"translation"' not in public
    assert '"reviewed_translation"' not in public


def test_live_steam_unchanged() -> None:
    if B.BASE.LIVE_BASE_PATH.is_file():
        assert sha256_file(B.BASE.LIVE_BASE_PATH) == (
            B.BASE.EXPECTED_LIVE_BASE_SHA256
        )
    if B.BASE.LIVE_PK_PATH.is_file():
        assert sha256_file(B.BASE.LIVE_PK_PATH) == (
            B.BASE.EXPECTED_LIVE_PK_SHA256
        )
    assert load_json(B.DEFAULT_PUBLIC_OUTPUT)["steam_write_performed"] is False


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
