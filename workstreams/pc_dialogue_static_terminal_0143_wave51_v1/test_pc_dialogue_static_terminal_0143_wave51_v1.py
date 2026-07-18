"""Regression tests for the private Wave 51 terminal-static candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
BUILDER = SCRIPT.with_name("build_pc_dialogue_static_terminal_0143_wave51_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("wave51_under_test", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Wave 51 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W51 = load_builder()


class Wave51StaticTerminalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = W51.prepare_candidate()

    def test_exact_scope_and_target_profiles(self):
        self.assertEqual(len(W51.CHANGES), 40)
        self.assertEqual(len(W51.EXPECTED_SCOPE[W51.BASE_RESOURCE]), 4)
        self.assertEqual(len(W51.EXPECTED_SCOPE[W51.PK_RESOURCE]), 36)
        for resource, profile in W51.TARGET_PROFILES.items():
            self.assertEqual(len(self.bundle.packed[resource]), profile["size"])
            self.assertEqual(W51.sha256_bytes(self.bundle.packed[resource]), profile["sha256"])
            self.assertEqual(len(self.bundle.raw[resource]), profile["raw_size"])
            self.assertEqual(W51.sha256_bytes(self.bundle.raw[resource]), profile["raw_sha256"])

    def test_overlap_guards_are_executable_and_empty(self):
        report = W51.validate_external_nonoverlap()
        self.assertEqual(report["w46_overlap"], 0)
        self.assertEqual(report["w48_overlap"], 0)

    def test_every_target_preserves_korean_literals_and_removes_only_static_command(self):
        _packed, current = W51.load_current()
        for change in W51.CHANGES:
            before = current[change.resource][change.coordinate]
            target_data = W51.rebuild_record(change, before)
            after = W51.W27.MsgGameRecord(before.block_id, before.record_id, before.relative_offset, target_data)
            self.assertEqual(W51.literal_texts(after), change.current_literals)
            self.assertEqual(W51.marker_topology(after), W51.marker_topology(before))
            self.assertEqual(W51.commands_0143(after), ())
            self.assertEqual(W51.opcodes_02xx(after), ())
            self.assertNotIn(W51.RUNTIME_SLOT, after.data)
            self.assertTrue(after.data.endswith(W51.RECORD_TERMINATOR))

    def test_pk_two_literal_marker_topology(self):
        _packed, current = W51.load_current()
        actual = set()
        for coordinate in W51.MULTI_LITERAL_PK_COORDINATES:
            change = W51.CHANGE_BY_KEY[(W51.PK_RESOURCE, coordinate)]
            before = current[W51.PK_RESOURCE][coordinate]
            after = W51.W27.MsgGameRecord(
                before.block_id,
                before.record_id,
                before.relative_offset,
                W51.rebuild_record(change, before),
            )
            W51.validate_pk_two_literal_topology(change, before, after)
            self.assertEqual(len(W51.literal_texts(before)), 2)
            self.assertEqual(len(W51.literal_texts(after)), 2)
            self.assertEqual(W51.marker_topology(before), W51.marker_topology(after))
            self.assertEqual(W51.span_hexes(before)[:2], W51.span_hexes(after)[:2])
            actual.add(coordinate)
        self.assertEqual(actual, set(W51.MULTI_LITERAL_PK_COORDINATES))

    def test_private_guard_rejects_steam_path(self):
        with self.assertRaises(W51.StaticTerminal0143Error):
            W51.require_private(W51.STEAM_ROOT / W51.BASE_RESOURCE, "Steam path")


if __name__ == "__main__":
    unittest.main()
