#!/usr/bin/env python3
"""Regression checks for direct-PC dialogue-quality wave four."""

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
BUILD = WORKSTREAM / "build_pc_dialogue_quality_wave4_v1.py"

spec = importlib.util.spec_from_file_location("wave4_quality", BUILD)
assert spec and spec.loader
wave4 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = wave4
spec.loader.exec_module(wave4)


class Wave4QualityTests(unittest.TestCase):
    def test_target_is_pinned_and_quality_plans_are_unique(self) -> None:
        self.assertTrue(wave4.target_is_pinned())
        for relative in wave4.CHANGED_PATHS:
            wave4.validate_plan_set(wave4.plans_for(relative), relative)

    def test_candidate_preserves_runtime_bytes_and_unplanned_records(self) -> None:
        steam = wave4.DEFAULT_STEAM_ROOT
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
            outcome = json.loads(completed.stdout)
            self.assertEqual(outcome["output_sha256"], wave4.TARGET_SHA256)
            self.assertEqual(json.loads(manifest.read_text(encoding="utf-8"))["output_sha256"], wave4.TARGET_SHA256)
            source_base = (steam / "MSG/JP/msggame.bin").read_bytes()
            source_pk = (steam / "MSG_PK/JP/msggame.bin").read_bytes()
            before = wave4.records_by_coordinate(source_pk)
            after = wave4.records_by_coordinate((candidate / "MSG_PK/JP/msggame.bin").read_bytes())
            plans = {item.coordinate: item for item in wave4.PK_PLANS}
            wave3_base = wave4.WAVE3.rebuild_static_resource(
                source_base,
                wave4.WAVE3.BASE_PLANS,
                "MSG/JP/msggame.bin",
            )
            wave3_before = wave4.WAVE3.rebuild_static_resource(
                source_pk,
                wave4.WAVE3.PK_PLANS,
                "MSG_PK/JP/msggame.bin",
            )
            candidate_base = wave4.records_by_coordinate((candidate / "MSG/JP/msggame.bin").read_bytes())
            wave3_base_records = wave4.records_by_coordinate(wave3_base)
            wave3_records = wave4.records_by_coordinate(wave3_before)
            self.assertEqual(set(candidate_base), set(wave3_base_records))
            for coordinate, record in wave3_base_records.items():
                self.assertEqual(candidate_base[coordinate].data, record.data, f"base {coordinate}")
            for coordinate, item in plans.items():
                self.assertEqual(wave4.opaque_bytes(after[coordinate]), wave4.opaque_bytes(wave3_records[coordinate]))
                for entry in item.changes:
                    literals = {literal.literal_id: literal.text for literal in wave4.parse_record_literals(after[coordinate])}
                    self.assertEqual(literals[entry.literal_id], entry.replacement)
            self.assertEqual(set(before), set(after))
            for coordinate, record in wave3_records.items():
                if coordinate not in plans:
                    self.assertEqual(after[coordinate].data, record.data, f"PK {coordinate}")


if __name__ == "__main__":
    unittest.main()
