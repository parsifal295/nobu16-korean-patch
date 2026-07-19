#!/usr/bin/env python3
"""Regression tests for the private direct-PC PK event reflow batch D."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
MODULE_PATH = SCRIPT.with_name("build_pc_event_reflow_static_batch_d_candidate_v1.py")


def load_module():
    spec = importlib.util.spec_from_file_location("pc_event_reflow_static_batch_d", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load batch D builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class BatchDTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.m = load_module()

    def test_declared_scope_and_hold(self) -> None:
        self.m.validate_declarations()
        self.assertEqual(len(self.m.CHANGES), 24)
        self.assertEqual([change.entry_id for change in self.m.CHANGES], sorted(change.entry_id for change in self.m.CHANGES))
        self.assertEqual([hold.entry_id for hold in self.m.HOLDS], [4999])
        self.assertNotIn(4999, [change.entry_id for change in self.m.CHANGES])

    def test_prepare_preserves_visible_text_and_controls(self) -> None:
        bundle = self.m.prepare_candidate()
        source = self.m.read_table(self.m.W45_KO_EVENT, self.m.W45_PROFILE, "test W45")
        _header, raw = self.m.decompress_wrapper(bundle.packed)
        output = self.m.parse_message_table(raw)
        changed = [index for index, pair in enumerate(zip(source.table.texts, output.texts)) if pair[0] != pair[1]]
        self.assertEqual(changed, [change.entry_id for change in self.m.CHANGES])
        for change in self.m.CHANGES:
            before = source.table.texts[change.entry_id]
            after = output.texts[change.entry_id]
            self.assertTrue(self.m.layout_equivalent(before, after))
            self.assertEqual(self.m.control_signature(before), self.m.control_signature(after))
            self.assertEqual(self.m.LINEBREAK_RE.findall(before), [])
            self.assertEqual(self.m.LINEBREAK_RE.findall(after), ["\n"])
        self.assertEqual(output.texts[4999], source.table.texts[4999])
        profile = self.m.file_profile(bundle.packed, raw, output)
        self.assertEqual(profile, self.m.EXPECTED_OUTPUT_PROFILE)

    def test_build_verify_and_diff_private_only(self) -> None:
        bundle = self.m.prepare_candidate()
        self.m.write_candidate(bundle)
        self.m.verify_private()
        self.m.diff_check()


if __name__ == "__main__":
    unittest.main(verbosity=2)
