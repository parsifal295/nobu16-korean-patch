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
        self.assertEqual(len(wave4.BASE_PLANS), len(wave4.BASE_RUNTIME_SUFFIX_IDS))
        self.assertEqual(len(wave4.PK_RUNTIME_SUFFIX_PLANS), 12)
        self.assertEqual(len(wave4.PK_REAUDITED_RUNTIME_PLANS), 39)
        self.assertEqual(len(wave4.PK_REAUDITED_DIALOGUE_PLANS), 21)
        self.assertEqual(len(wave4.PK_REAUDITED_PLANS), 60)
        runtime_coordinates = {(6, record_id) for record_id in range(2089, 2101)}
        self.assertTrue(runtime_coordinates.issubset({item.coordinate for item in wave4.PK_PLANS}))
        reaudited_coordinates = {item.coordinate for item in wave4.PK_REAUDITED_PLANS}
        active_deferred_coordinates = {
            item.coordinate for item in wave4.PK_PLANS
        } & wave4.DEFERRED_UNALIGNED_0FB9_COORDINATES
        self.assertTrue(
            wave4.DEFERRED_UNALIGNED_0FB9_COORDINATES.issubset(reaudited_coordinates)
        )
        self.assertEqual(active_deferred_coordinates, wave4.DEFERRED_UNALIGNED_0FB9_COORDINATES)
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
            after = wave4.records_by_coordinate((candidate / "MSG_PK/JP/msggame.bin").read_bytes())

            def assert_transform(
                before_records: dict[tuple[int, int], wave4.MsgGameRecord],
                after_records: dict[tuple[int, int], wave4.MsgGameRecord],
                plan_items: tuple[wave4.QualityPlan, ...],
                label: str,
            ) -> None:
                plans = {item.coordinate: item for item in plan_items}
                self.assertEqual(set(before_records), set(after_records), label)
                for coordinate, record in before_records.items():
                    actual = after_records[coordinate]
                    item = plans.get(coordinate)
                    if item is None:
                        self.assertEqual(actual.data, record.data, f"{label} {coordinate}")
                        continue
                    self.assertEqual(
                        wave4.opaque_bytes(actual),
                        wave4.expected_opaque_after_removals(record, item),
                        f"{label} opaque {coordinate}",
                    )
                    for entry in item.changes:
                        literals = {
                            literal.literal_id: literal.text
                            for literal in wave4.parse_record_literals(actual)
                        }
                        self.assertEqual(
                            literals[entry.literal_id], entry.replacement, f"{label} literal {coordinate}"
                        )

            assert_transform(wave3_base_records, candidate_base, wave4.BASE_PLANS, "base")
            assert_transform(wave3_records, after, wave4.PK_PLANS, "PK")


if __name__ == "__main__":
    unittest.main()
