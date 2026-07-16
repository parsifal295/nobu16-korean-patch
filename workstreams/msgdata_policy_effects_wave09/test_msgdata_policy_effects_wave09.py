#!/usr/bin/env python3
"""Regression tests for the source-free Steam-JP policy-effect wave 09."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load_module():
    path = HERE / "build_msgdata_policy_effects_wave09.py"
    spec = importlib.util.spec_from_file_location("policy_effects_wave09_test_module", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MOD = load_module()


class PolicyEffectsWave09Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.stock_root = MOD.DEFAULT_STOCK_ROOT
        cls._default_baseline, _metrics = MOD.TACTICS.build_blob(cls.stock_root)

    def default_baseline(self) -> bytes:
        return self._default_baseline

    def parse(self, packed: bytes):
        _header, raw = MOD.COMMON.decompress_wrapper(packed)
        return MOD.COMMON.parse_message_table(raw)

    def test_verify_tracked_artifacts_and_deterministic_build(self) -> None:
        metrics = MOD.verify(self.stock_root)
        self.assertEqual(metrics["policy_effect_delta_count"], 44)
        self.assertTrue(metrics["deterministic_ab_equal"])
        self.assertTrue(metrics["all_target_policy_effect_values_no_latin"])

    def test_default_api_equals_direct_default_build(self) -> None:
        baseline = self.default_baseline()
        from_api, api_metrics = MOD.apply_to_baseline(self.stock_root, baseline)
        from_default, default_metrics = MOD.build_blob(self.stock_root)
        self.assertEqual(from_api, from_default)
        self.assertEqual(api_metrics["candidate"], default_metrics["candidate"])

    def test_screen_hotfix_non_target_change_composes_and_is_preserved(self) -> None:
        baseline = self.default_baseline()
        baseline_table = self.parse(baseline)
        non_target_id = 100
        self.assertNotIn(non_target_id, MOD.TARGET_IDS)
        screen_texts = list(baseline_table.texts)
        screen_texts[non_target_id] = "화면 핫픽스 유지"
        screen_raw = MOD.COMMON.rebuild_message_table(baseline_table, screen_texts)
        screen_baseline = MOD.COMMON.recompress_wrapper(screen_raw, baseline)

        candidate, metrics = MOD.build_after_screen_hotfix(self.stock_root, screen_baseline)
        candidate_table = self.parse(candidate)
        self.assertEqual(candidate_table.texts[non_target_id], "화면 핫픽스 유지")
        self.assertEqual(metrics["policy_effect_delta_count"], len(MOD.TARGET_IDS))
        for entry_id in MOD.TARGET_IDS:
            self.assertEqual(candidate_table.texts[entry_id], MOD.TARGET_KO[entry_id])

    def test_changed_target_baseline_fails_closed(self) -> None:
        baseline = self.default_baseline()
        baseline_table = self.parse(baseline)
        changed = list(baseline_table.texts)
        changed[MOD.TARGET_IDS[0]] = "이미 변경된 정책 효과"
        changed_raw = MOD.COMMON.rebuild_message_table(baseline_table, changed)
        changed_baseline = MOD.COMMON.recompress_wrapper(changed_raw, baseline)
        with self.assertRaises(MOD.PolicyEffectsWave09Error):
            MOD.build_after_screen_hotfix(self.stock_root, changed_baseline)

    def test_only_targets_change_from_default_baseline(self) -> None:
        baseline = self.default_baseline()
        candidate, _metrics = MOD.build_blob(self.stock_root)
        baseline_table = self.parse(baseline)
        candidate_table = self.parse(candidate)
        changed_ids = {
            entry_id
            for entry_id, (before, after) in enumerate(zip(baseline_table.texts, candidate_table.texts))
            if before != after
        }
        self.assertEqual(changed_ids, set(MOD.TARGET_IDS))


if __name__ == "__main__":
    unittest.main()
