#!/usr/bin/env python3
"""Tests for the private W69 canonical PK event-title candidate builder."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
MODULE_PATH = SCRIPT.with_name("build_pc_event_title_canonical_wave69_v1.py")


def load_builder() -> object:
    spec = importlib.util.spec_from_file_location("wave69_test_builder", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Wave69Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()

    def test_title_scope_and_duplicate_pairs_are_pinned(self) -> None:
        targets = self.builder.TARGETS
        self.assertEqual(len(targets), 10)
        self.assertEqual(len({target.entry_id for target in targets}), 10)
        self.assertEqual(self.builder.EXPECTED_CLASS_COUNTS, {"fresh": 10, "already": 0, "override": 0})
        target_by_id = {target.entry_id: target for target in targets}
        for left, right in ((14002, 14010), (14003, 14017), (14004, 14013)):
            self.assertEqual(target_by_id[left].direct_pc_jp, target_by_id[right].direct_pc_jp)
            self.assertEqual(target_by_id[left].target_ko, target_by_id[right].target_ko)
        for target in targets:
            self.assertEqual(target.current_ko.count("\n"), 0)
            self.assertEqual(target.target_ko.count("\n"), 0)
            self.assertLessEqual(target.target_width_px, 912)

    def test_prepare_matches_pinned_w68_overlay_contract(self) -> None:
        bundle = self.builder.prepare(require_output_profiles=True)
        self.assertEqual(len(bundle.effective), 10)
        self.assertEqual({name: len(values) for name, values in bundle.classifications.items()}, {"fresh": 10, "already": 0, "override": 0})
        self.assertEqual(bundle.final_record_counts, self.builder.expected_final_record_counts())
        self.assertEqual(sum(bundle.final_record_counts.values()), self.builder.EXPECTED_TOTAL_RECORDS)
        self.assertEqual({resource: self.builder.profile_dict(value) for resource, value in bundle.profiles.items()}, self.builder.expected_final_profile_dicts())


if __name__ == "__main__":
    unittest.main()
