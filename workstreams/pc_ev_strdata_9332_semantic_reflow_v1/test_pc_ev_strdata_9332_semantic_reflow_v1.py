#!/usr/bin/env python3
"""Focused invariant tests for the ID 9332 base-event reflow builder."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parent / "build_pc_ev_strdata_9332_semantic_reflow_v1.py"
SPEC = importlib.util.spec_from_file_location("ev9332_builder", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class Event9332ReflowTests(unittest.TestCase):
    def test_target_has_exactly_three_deliberate_lines(self) -> None:
        self.assertEqual(builder.TARGET_TEXT.count("\n"), 2)
        self.assertEqual(len(builder.TARGET_TEXT.split("\n")), 3)
        self.assertTrue(all(builder.visible_text(line).strip() for line in builder.TARGET_TEXT.split("\n")))

    def test_target_has_balanced_colour_controls(self) -> None:
        builder.validate_colors(builder.TARGET_TEXT)
        self.assertNotIn("?", builder.visible_text(builder.TARGET_TEXT))

    def test_target_preserves_no_runtime_or_printf_token(self) -> None:
        self.assertEqual(builder.protected_signature(builder.TARGET_TEXT), {"printf": [], "runtime": [], "controls": []})

    def test_target_hash_is_pinned(self) -> None:
        self.assertEqual(builder.text_hash(builder.TARGET_TEXT), builder.TARGET_TEXT_SHA256)


if __name__ == "__main__":
    unittest.main()
