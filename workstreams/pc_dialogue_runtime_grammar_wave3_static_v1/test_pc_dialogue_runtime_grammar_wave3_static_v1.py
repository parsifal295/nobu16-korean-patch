#!/usr/bin/env python3
"""Regression checks for the PC-only static third dialogue repair wave."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BUILD = WORKSTREAM / "build_pc_dialogue_runtime_grammar_wave3_static_v1.py"

spec = importlib.util.spec_from_file_location("wave3_static", BUILD)
assert spec and spec.loader
wave3 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = wave3
spec.loader.exec_module(wave3)


class Wave3StaticTests(unittest.TestCase):
    def test_pristine_pc_jp_layout_matches_current_pc_profile(self) -> None:
        self.assertTrue(wave3.DEFAULT_STEAM_ROOT.is_dir(), wave3.DEFAULT_STEAM_ROOT)
        self.assertEqual(
            wave3.assert_pristine_sources(),
            {relative: expected for relative, (_path, expected) in wave3.PRISTINE_SOURCES.items()},
        )
        wave3.assert_pristine_layout_matches_steam(wave3.DEFAULT_STEAM_ROOT)

    def test_target_is_pinned_and_plan_shape_is_static(self) -> None:
        self.assertTrue(wave3.target_is_pinned())
        for relative in wave3.CHANGED_PATHS:
            plans = wave3.plans_for(relative)
            wave3.validate_plan_set(plans, relative)
            self.assertTrue(plans)
            for item in plans:
                self.assertEqual(wave3.expected_record_data(item)[-3:], wave3.TERMINATOR)

    def test_candidate_preserves_all_unplanned_records(self) -> None:
        steam = wave3.DEFAULT_STEAM_ROOT
        self.assertTrue(steam.is_dir(), steam)
        with tempfile.TemporaryDirectory(dir=REPO / "tmp") as directory:
            root = Path(directory)
            candidate = root / "candidate"
            manifest = root / "manifest.json"
            environment = os.environ.copy()
            environment["PYTHONIOENCODING"] = "utf-8"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(BUILD),
                    "build",
                    "--steam-root",
                    str(steam),
                    "--output-root",
                    str(candidate),
                    "--manifest",
                    str(manifest),
                ],
                check=True,
                text=True,
                capture_output=True,
                encoding="utf-8",
                env=environment,
            )
            result = json.loads(completed.stdout)
            self.assertEqual(result["output_sha256"], wave3.TARGET_SHA256)
            self.assertEqual(json.loads(manifest.read_text(encoding="utf-8"))["output_sha256"], wave3.TARGET_SHA256)
            for relative in wave3.CHANGED_PATHS:
                before = wave3.records_by_coordinate((steam / relative).read_bytes())
                after = wave3.records_by_coordinate((candidate / relative).read_bytes())
                planned = {item.coordinate: item for item in wave3.plans_for(relative)}
                self.assertEqual(set(before), set(after))
                for coordinate, original in before.items():
                    if coordinate not in planned:
                        self.assertEqual(after[coordinate].data, original.data, f"{relative} {coordinate}")
                for coordinate, item in planned.items():
                    self.assertEqual(after[coordinate].data, wave3.expected_record_data(item))
                    self.assertNotIn(b"\x01\x43", after[coordinate].data)


if __name__ == "__main__":
    unittest.main()
