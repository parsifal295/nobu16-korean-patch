#!/usr/bin/env python3
"""Regression checks for the Wave 7 pinned PC dialogue repair candidate."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BUILD = WORKSTREAM / "build_pc_dialogue_goodwill_runtime_wave7_v1.py"

spec = importlib.util.spec_from_file_location("pc_dialogue_goodwill_runtime_wave7_test", BUILD)
assert spec and spec.loader
wave7 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = wave7
spec.loader.exec_module(wave7)


class Wave7QualityTests(unittest.TestCase):
    def test_contract_is_exactly_the_twelve_reviewed_records(self) -> None:
        audit, plans = wave7.validate_contracts(wave7.DEFAULT_STEAM_ROOT)
        self.assertEqual(
            {resource: tuple(plan.coordinate for plan, _row in values) for resource, values in plans.items()},
            wave7.EXPECTED_COORDINATES,
        )
        self.assertEqual(audit["input_profile_sha256"], wave7.INPUT_SHA256)
        self.assertEqual(audit["output_profile_sha256"], wave7.TARGET_SHA256)
        self.assertEqual(len(audit["records"]), 12)
        for resource, values in plans.items():
            for plan, row in values:
                self.assertEqual(plan.coordinate, wave7.parse_coordinate(row["coordinate"]))
                self.assertEqual(
                    bool(plan.remove_commands),
                    row["kind"].endswith("_runtime"),
                    (resource, plan.coordinate),
                )

    def test_build_is_pinned_and_changes_no_other_records_or_resources(self) -> None:
        steam = wave7.DEFAULT_STEAM_ROOT
        test_root = REPO / "tmp" / WORKSTREAM.name
        test_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="wave7_test_", dir=test_root) as directory:
            root = Path(directory)
            output = root / "candidate"
            manifest_path = root / "manifest.json"
            manifest = wave7.build_candidate(steam, output, manifest_path)
            self.assertEqual(manifest["output_sha256"], wave7.TARGET_SHA256)
            persisted = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(persisted["pinned_output_sha256"], wave7.TARGET_SHA256)
            self.assertEqual(len(persisted["records"]), 12)
            for resource, expected in wave7.EXPECTED_COORDINATES.items():
                before = wave7.WAVE4.records_by_coordinate((steam / resource).read_bytes())
                after = wave7.WAVE4.records_by_coordinate((output / resource).read_bytes())
                changed = {coordinate for coordinate in before if before[coordinate].data != after[coordinate].data}
                self.assertEqual(changed, set(expected), resource)
                for coordinate, old in before.items():
                    if coordinate not in changed:
                        self.assertEqual(after[coordinate].data, old.data, (resource, coordinate))
            for relative in wave7.PROFILE_PATHS:
                if relative not in wave7.CHANGED_PATHS:
                    self.assertEqual((output / relative).read_bytes(), (steam / relative).read_bytes(), relative)


if __name__ == "__main__":
    unittest.main()
