#!/usr/bin/env python3
"""Regression tests for the proposal-reference dialogue hotfix."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "build_pc_dialogue_proposal_reference_hotfix_v1.py"
SPEC = importlib.util.spec_from_file_location(
    "pc_dialogue_proposal_reference_hotfix_v1",
    MODULE_PATH,
)
assert SPEC is not None and SPEC.loader is not None
HOTFIX = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = HOTFIX
SPEC.loader.exec_module(HOTFIX)


class ProposalReferenceHotfixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not HOTFIX.DEFAULT_INPUT_ROOT.is_dir():
            raise unittest.SkipTest("the pinned resource input root is unavailable")
        cls.output, cls.report = HOTFIX.prepare_candidate(HOTFIX.DEFAULT_INPUT_ROOT)

    def test_exact_source_and_target_profiles_are_pinned(self) -> None:
        self.assertEqual("PASS", self.report["status"])
        for spec in HOTFIX.SPECS:
            detail = self.report["resources"][spec.relative_path]
            self.assertEqual(spec.input_size, detail["input_size"])
            self.assertEqual(spec.input_sha256, detail["input_sha256"])
            self.assertEqual(spec.target_size, detail["target_size"])
            if not spec.target_sha256.startswith("TO_FILL"):
                self.assertEqual(spec.target_sha256, detail["target_sha256"])

    def test_only_one_equal_length_record_changes_per_resource(self) -> None:
        for spec in HOTFIX.SPECS:
            source = (HOTFIX.DEFAULT_INPUT_ROOT / spec.relative_path).read_bytes()
            candidate = self.output[spec.relative_path]
            before = HOTFIX.record_map(source)
            after = HOTFIX.record_map(candidate)
            self.assertEqual(before.keys(), after.keys())
            changed = [key for key in before if before[key].data != after[key].data]
            self.assertEqual([spec.coordinate], changed)
            self.assertEqual(
                len(before[spec.coordinate].data),
                len(after[spec.coordinate].data),
            )

    def test_bad_suffix_calls_are_removed_but_first_style_call_remains(self) -> None:
        for spec in HOTFIX.SPECS:
            candidate = self.output[spec.relative_path]
            record = HOTFIX.record_map(candidate)[spec.coordinate]
            texts, gaps = HOTFIX.split_record(record)
            self.assertEqual(5, len(texts))
            self.assertEqual(1, record.data.count(b"\x01\x43"))
            self.assertEqual("050505", gaps[-1])
            self.assertNotIn("저것", "".join(texts))
            self.assertIn("필요할 때 ", "".join(texts))
            self.assertIn("참조해 보시오.", "".join(texts))

    def test_public_overlay_matches_the_exact_build(self) -> None:
        overlay = json.loads(HOTFIX.OVERLAY_PATH.read_text(encoding="utf-8"))
        self.assertEqual(HOTFIX.expected_overlay(self.report), overlay)
        self.assertFalse(
            overlay["distribution_policy"]["contains_commercial_source_text"]
        )
        self.assertFalse(
            overlay["distribution_policy"]["contains_complete_game_binary"]
        )
        self.assertFalse(overlay["distribution_policy"]["steam_write_supported"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
