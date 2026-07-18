#!/usr/bin/env python3
"""Regression checks for the Wave 6 pinned static cleanup candidate."""

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
BUILD = WORKSTREAM / "build_pc_dialogue_quality_wave6_v1.py"

spec = importlib.util.spec_from_file_location("pc_dialogue_quality_wave6_test", BUILD)
assert spec and spec.loader
wave6 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = wave6
spec.loader.exec_module(wave6)


class Wave6QualityTests(unittest.TestCase):
    def test_contract_is_exactly_the_three_reviewed_records(self) -> None:
        audit, plans = wave6.validate_contracts(wave6.DEFAULT_STEAM_ROOT)
        self.assertEqual(tuple(plan.coordinate for plan in plans), wave6.EXPECTED_COORDINATES)
        self.assertEqual(audit["output"]["steam_file_sha256"], wave6.TARGET_SHA256[wave6.RESOURCE])
        self.assertEqual(
            [row["output_record_sha256"] for row in audit["records"]],
            [
                "3263E7CF589D849F175D6774EFC1F4304FE4E0E273DAF0E9D0F05CF280B122F8",
                "6A84B08790B5386855C59EA65804FAFFEE2F077BD1F2DF823C0535119AF35F18",
                "76709A636FE41CA1779F7B92F051369CA4DA9C349C4E0A3AD25AF45201BBFD4A",
            ],
        )

    def test_build_is_pinned_and_changes_no_other_records_or_resources(self) -> None:
        steam = wave6.DEFAULT_STEAM_ROOT
        test_root = REPO / "tmp" / WORKSTREAM.name
        test_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="wave6_test_", dir=test_root) as directory:
            root = Path(directory)
            output = root / "candidate"
            manifest_path = root / "manifest.json"
            manifest = wave6.build_candidate(steam, output, manifest_path)
            self.assertEqual(manifest["output_sha256"], wave6.TARGET_SHA256)
            self.assertEqual(json.loads(manifest_path.read_text(encoding="utf-8"))["pinned_output_sha256"], wave6.TARGET_SHA256)
            before = wave6.WAVE4.records_by_coordinate((steam / wave6.RESOURCE).read_bytes())
            after = wave6.WAVE4.records_by_coordinate((output / wave6.RESOURCE).read_bytes())
            changed = {coordinate for coordinate in before if before[coordinate].data != after[coordinate].data}
            self.assertEqual(changed, set(wave6.EXPECTED_COORDINATES))
            for coordinate, old in before.items():
                if coordinate not in changed:
                    self.assertEqual(after[coordinate].data, old.data, coordinate)
            for relative in wave6.PROFILE_PATHS:
                if relative != wave6.RESOURCE:
                    self.assertEqual((output / relative).read_bytes(), (steam / relative).read_bytes(), relative)


if __name__ == "__main__":
    unittest.main()
