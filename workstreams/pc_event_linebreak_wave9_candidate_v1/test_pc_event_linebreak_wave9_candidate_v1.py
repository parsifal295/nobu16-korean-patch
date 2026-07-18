#!/usr/bin/env python3
"""Regression checks for the private Wave9 PC event candidate builder."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("pc_event_linebreak_wave9", HERE / "build_pc_event_linebreak_wave9_candidate_v1.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load Wave9 candidate builder")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_candidate_coordinate_contract() -> None:
    groups = MODULE.candidate_groups()
    assert [row.identifier for row in groups["base"]] == [
        4558,
        4657,
        4769,
        4781,
        5155,
        5403,
        5492,
        6233,
        6365,
        6401,
        6668,
        7475,
        9580,
        9585,
        16397,
    ]
    assert [row.identifier for row in groups["pk"]] == [3945, 4289, 6499, 6662, 9585]
    assert sum(len(rows) for rows in groups.values()) == 20


def test_reflow_only_skeleton_contract() -> None:
    groups = MODULE.candidate_groups()
    reflow = [row for rows in groups.values() for row in rows if row.change_kind == "hard_break_reflow_only"]
    assert {(row.resource_key, row.identifier) for row in reflow} == {
        ("base", 6668),
        ("base", 16397),
        ("pk", 3945),
        ("pk", 6499),
    }


def test_live_pc_validation_is_candidate_only() -> None:
    result = MODULE.validate()
    assert result["status"] == "ok"
    assert result["base_candidate_count"] == 15
    assert result["pk_candidate_count"] == 5
    assert result["total_candidate_count"] == 20
    assert result["steam_game_resource_written"] is False
    assert result["write_scope"] == "none"


if __name__ == "__main__":
    test_candidate_coordinate_contract()
    test_reflow_only_skeleton_contract()
    test_live_pc_validation_is_candidate_only()
    print("Wave9 candidate regression checks: OK")
