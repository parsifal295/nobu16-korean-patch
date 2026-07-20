#!/usr/bin/env python3
"""Deterministic checks for the read-only manual-compact event inventory."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
BUILDER = SCRIPT.with_name("build_pc_event_manual_compact_korean_layout_inventory_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("manual_compact_inventory_builder", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_read_only_inventory_outputs_match_strict_inputs() -> None:
    builder = load_builder()
    inventory, batches, validation, report = builder.build_bundle()
    assert inventory["read_only"] is True
    assert inventory["event_candidate_created"] is False
    assert inventory["counts"]["row_count"] == 1553
    assert inventory["current_successor"]["event_profile"] == builder.EXPECTED_CURRENT_PROFILE
    assert inventory["batch01_predecessor"]["event_profile"] == builder.EXPECTED_BATCH01_PROFILE
    assert inventory["static007_3line_predecessor"]["event_profile"] == builder.EXPECTED_STATIC007_3LINE_PROFILE
    assert inventory["counts"]["current_differs_from_historical_compact_count"] == 205
    assert inventory["counts"]["legacy_static_preflight"]["recovery_category_counts"] == {
        "current_diff+oldfit": 201,
        "current_diff+reflow": 4,
        "current_same+oldfit": 1319,
        "current_same+reflow": 29,
    }
    assert inventory["counts"]["legacy_static_preflight"]["static_reflow_row_count"] == 33
    assert validation["row_count"] == 1553
    assert inventory["counts"]["contiguous_scene_batch_count"] == batches["contiguous_scene_batch_count"]
    assert all(
        row["required_human_action"]["semantic_retranslation_required"]
        and row["required_human_action"]["non_shortened_required"]
        and row["required_human_action"]["global_linebreak_strip_forbidden"]
        and row["required_human_action"]["automatic_decompaction_forbidden"]
        for row in inventory["rows"]
    )
    rows_by_id = {row["entry_id"]: row for row in inventory["rows"]}
    assert rows_by_id[5777]["manual_layout"]["manual_line_count"] == 3
    assert rows_by_id[5777]["current_differs_from_w97_historical_predecessor"] is True
    assert all(
        rows_by_id[entry_id]["candidate_protection"]["do_not_overwrite"]
        for entry_id in (3210, 3231, 3232, 3233, 3234, 3239, 3254, 3260, 3285, 5777)
    )
    assert all(
        rows_by_id[entry_id]["current_differs_from_historical_compact"]
        for entry_id in (3210, 3231, 3232, 3233, 3234, 3239, 3254, 3260)
    )
    assert "requested_raw_line_limit_px" not in inventory["layout_policy"]
    assert "안전한 후보 체인" in report
    assert builder.verify_outputs((inventory, batches, validation, report))["status"] == "PASS"
