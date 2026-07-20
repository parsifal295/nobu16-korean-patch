#!/usr/bin/env python3
"""Tests for the private W67 B17 static-boundary candidate builder."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
MODULE_PATH = SCRIPT.with_name("build_pc_b17_static_boundary_spacing_wave67_v1.py")


def load_builder() -> object:
    spec = importlib.util.spec_from_file_location("wave67_test_builder", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Wave67Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()

    def test_target_scope_is_static_b17_only(self) -> None:
        targets = self.builder.TARGETS
        self.assertEqual(len(targets), 20)
        self.assertEqual(len({target.coordinate for target in targets}), 20)
        self.assertEqual({target.coordinate[0] for target in targets}, {17})
        self.assertEqual(
            self.builder.EXPECTED_CLASS_COUNTS,
            {"fresh": 20, "already": 0, "override": 0},
        )
        for target in targets:
            self.assertEqual(target.current_ko.count("\n"), target.target_ko.count("\n"))
            self.assertNotIn("\x1b", target.current_ko)
            self.assertNotIn("\x1b", target.direct_pc_jp)
            self.assertLessEqual(max(target.target_record_line_widths_px), 912)

    def test_prepare_matches_pinned_w66_overlay_contract(self) -> None:
        bundle = self.builder.prepare(require_output_profiles=True)
        self.assertEqual(len(bundle.effective), 20)
        self.assertEqual(
            {name: len(values) for name, values in bundle.classifications.items()},
            {"fresh": 20, "already": 0, "override": 0},
        )
        self.assertEqual(bundle.final_record_counts, self.builder.EXPECTED_FINAL_RECORD_COUNTS)
        self.assertEqual(sum(bundle.final_record_counts.values()), self.builder.EXPECTED_FINAL_TOTAL_RECORDS)
        self.assertEqual(
            {resource: self.builder.profile_dict(value) for resource, value in bundle.profiles.items()},
            self.builder.EXPECTED_FINAL_PROFILE_DICTS,
        )


if __name__ == "__main__":
    unittest.main()
