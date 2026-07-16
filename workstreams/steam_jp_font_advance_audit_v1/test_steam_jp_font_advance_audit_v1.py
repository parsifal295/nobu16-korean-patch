#!/usr/bin/env python3
"""Unit tests for source-free Switch v2.3 font metric audit logic."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "steam_jp_font_advance_audit_v1_under_test",
    ROOT / "build_steam_jp_font_advance_audit_v1.py",
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def record(width: int, cell: int, pointer: int) -> bytes:
    return bytes((width, cell, 0, cell, width, (-width // 2) & 0xFF, 0, cell)) + pointer.to_bytes(4, "little")


class SwitchMetricAuditTests(unittest.TestCase):
    def test_triplet_delta_accepts_width_advance_stride_only(self) -> None:
        mapping = [0] * MODULE.MAP_ENTRIES
        mapping[0xAC00] = 1
        before = MODULE.G1NTable(0, 48, tuple(mapping), (record(48, 48, 0), record(48, 48, 1152)))
        after = MODULE.G1NTable(0, 48, tuple(mapping), (record(48, 48, 0), record(40, 48, 1152)))
        result = MODULE.delta_table(before, after, "synthetic")
        self.assertTrue(result["only_width_advance_row_stride_triplet_changed"])
        self.assertTrue(result["changed_triplet_internal_contract_valid"])
        self.assertFalse(result["pointer_bytes_changed"])
        self.assertEqual(result["changed_hangul_codepoint_count"], 1)

    def test_triplet_delta_rejects_pointer_change(self) -> None:
        mapping = [0] * MODULE.MAP_ENTRIES
        mapping[0xAC00] = 1
        before = MODULE.G1NTable(0, 48, tuple(mapping), (record(48, 48, 0), record(48, 48, 1152)))
        after = MODULE.G1NTable(0, 48, tuple(mapping), (record(48, 48, 0), record(40, 48, 960)))
        result = MODULE.delta_table(before, after, "synthetic")
        self.assertFalse(result["only_width_advance_row_stride_triplet_changed"])
        self.assertTrue(result["pointer_bytes_changed"])

    def test_compact_range_summary_keeps_exact_contract_out_of_large_dump(self) -> None:
        values = list(range(0xAC00, 0xAC80, 2))
        summary = MODULE.compact_range_summary(values)
        self.assertIn("range_count", summary)
        self.assertNotIn("ranges", summary)
        self.assertIn("head", summary)
        self.assertIn("tail", summary)


if __name__ == "__main__":
    unittest.main()
