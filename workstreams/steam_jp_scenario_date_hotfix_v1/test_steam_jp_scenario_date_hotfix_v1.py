#!/usr/bin/env python3
"""Regression tests for the Steam-JP scenario calendar-month hotfix."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BUILDER_PATH = ROOT / "build_steam_jp_scenario_date_hotfix_v1.py"
SPEC = importlib.util.spec_from_file_location("scenario_date_hotfix_tested", BUILDER_PATH)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class ScenarioDateHotfixTests(unittest.TestCase):
    def test_contract_is_one_source_free_jp_only_delta(self) -> None:
        overlay, blob = builder.strict_json(builder.OVERLAY_PATH)
        self.assertEqual(overlay["schema"], builder.SCHEMA)
        self.assertEqual(overlay["resource"], builder.RESOURCE)
        self.assertEqual(overlay["base_language"], "JP")
        self.assertEqual(overlay["entry_count"], 1)
        self.assertEqual(overlay["distribution_policy"], {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        })
        self.assertEqual(overlay["stock_jp"], builder.MSGUI.stock_spec())
        self.assertEqual(len(overlay["entries"]), 1)
        entry = overlay["entries"][0]
        self.assertEqual(entry["id"], 1_051)
        self.assertEqual(entry["source_jp_utf16le_sha256"], builder.SOURCE_JP_HASH)
        self.assertEqual(entry["ko"], "%d월")
        self.assertEqual(blob, builder.pretty_bytes(overlay))
        self.assertFalse(any("SC" in value for value in json.dumps(overlay, ensure_ascii=False).split()))

    def test_build_changes_only_calendar_month_and_preserves_duration(self) -> None:
        if not builder.DEFAULT_STOCK_ROOT.is_dir():
            self.skipTest("private Steam 1.1.7 pristine JP backup is unavailable")
        first, metrics = builder.build_blob(builder.DEFAULT_STOCK_ROOT)
        second, second_metrics = builder.build_blob(builder.DEFAULT_STOCK_ROOT)
        self.assertEqual(first, second)
        self.assertEqual(metrics, second_metrics)
        self.assertEqual(metrics["entry_count"], 1)
        self.assertTrue(metrics["duration_month_preserved"])
        self.assertEqual(metrics["scenario_date_composition"], "1559년 3월")
        validation, validation_blob = builder.strict_json(builder.VALIDATION_PATH)
        self.assertEqual(validation, builder.validation_model(metrics))
        self.assertEqual(validation_blob, builder.pretty_bytes(validation))

        baseline, _baseline_metadata = builder.baseline_blob(builder.DEFAULT_STOCK_ROOT)
        _wrapper, baseline_raw = builder.V2.BASE.decompress_wrapper(baseline)
        baseline_table = builder.MSGUI.parse_message_table(baseline_raw)
        _candidate_wrapper, candidate_raw = builder.V2.BASE.decompress_wrapper(first)
        candidate_table = builder.MSGUI.parse_message_table(candidate_raw)
        changed = [
            entry_id
            for entry_id, (before, after) in enumerate(zip(baseline_table.texts, candidate_table.texts))
            if before != after
        ]
        self.assertEqual(changed, [builder.ENTRY_ID])
        self.assertEqual(candidate_table.texts[builder.YEAR_ENTRY_ID], "%d년")
        self.assertEqual(candidate_table.texts[builder.ENTRY_ID], "%d월")
        self.assertEqual(candidate_table.texts[builder.DURATION_ENTRY_ID], "%d개월")

    def test_public_workstream_contains_no_game_binary(self) -> None:
        forbidden = {".bin", ".g1n", ".ttf", ".otf", ".zip", ".pixels"}
        offenders = [
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("*")
            if path.is_file() and path.suffix.lower() in forbidden
        ]
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
