#!/usr/bin/env python3
"""Private-candidate tests for Wave 51 blocks 13–14 static corrections."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER = SCRIPT.with_name("build_pc_dialogue_quality_wave51_static_blocks13_14_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("wave51_under_test", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Wave 51 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Wave51PrivateCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()
        cls.steam_before = {
            resource: cls.builder.sha256_path(spec.current_path)
            for resource, spec in cls.builder.RESOURCE_SPECS.items()
        }
        cls.derived_pins = cls.builder.derive_pins()
        cls.bundle = cls.builder.prepare_candidate()

    @classmethod
    def tearDownClass(cls) -> None:
        for resource, spec in cls.builder.RESOURCE_SPECS.items():
            if cls.builder.sha256_path(spec.current_path) != cls.steam_before[resource]:
                raise AssertionError(f"Steam resource changed during test: {resource}")

    def test_pinned_profiles_and_record_evidence(self) -> None:
        self.assertEqual(self.derived_pins["target_profiles"], self.builder.TARGET_PROFILES)
        self.assertEqual(self.derived_pins["record_evidence_count"], 54)
        self.assertEqual(self.derived_pins["record_evidence_sha256"], self.builder.RECORD_EVIDENCE_SHA256)
        self.assertEqual(self.bundle.audit["record_evidence_sha256"], self.builder.RECORD_EVIDENCE_SHA256)
        self.assertEqual(self.bundle.audit["changed_record_count"], 54)
        self.assertEqual(
            self.bundle.audit["changed_record_count_by_resource"],
            {self.builder.BASE_RESOURCE: 19, self.builder.PK_RESOURCE: 35},
        )

    def test_static_record_contracts_and_scope(self) -> None:
        records = self.bundle.audit["records"]
        self.assertEqual(len(records), 54)
        for row in records:
            current = row["current_record"]
            source = row["pc_jp_record"]
            target = row["target_record"]
            self.assertTrue(current["terminator"])
            self.assertTrue(source["terminator"])
            self.assertTrue(target["terminator"])
            self.assertEqual(current["runtime_02xx_opcodes"], [])
            self.assertEqual(source["runtime_02xx_opcodes"], [])
            self.assertEqual(target["runtime_02xx_opcodes"], [])
            self.assertEqual(current["complete_0143_commands"], [])
            self.assertEqual(source["complete_0143_commands"], [])
            self.assertEqual(target["complete_0143_commands"], [])
            self.assertEqual(current["marker_topology_hex"], source["marker_topology_hex"])
            self.assertEqual(current["marker_topology_hex"], target["marker_topology_hex"])
            self.assertEqual(current["opaque_spans_hex"], source["opaque_spans_hex"])
            self.assertEqual(current["opaque_spans_hex"], target["opaque_spans_hex"])
            self.assertEqual(current["manual_lf_count"], target["manual_lf_count"])
            self.assertLessEqual(target["max_line_px"], current["max_line_px"])
            self.assertEqual(target["wide_fallback_codepoints"], [])
            self.assertNotEqual(current["sha256"], target["sha256"])

        expected = {
            resource: {change.coordinate for change in self.builder.CHANGES if change.resource == resource}
            for resource in self.builder.RESOURCE_ORDER
        }
        for resource in self.builder.RESOURCE_ORDER:
            current = self.builder.W27.records_by_coordinate(self.builder.RESOURCE_SPECS[resource].current_path.read_bytes())
            candidate = self.builder.W27.records_by_coordinate(self.bundle.packed[resource])
            changed = {coordinate for coordinate, record in current.items() if record.data != candidate[coordinate].data}
            self.assertEqual(changed, expected[resource], resource)

        # Representative holds must remain byte-identical in the candidate.
        held = {
            self.builder.BASE_RESOURCE: ((13, 213),),
            self.builder.PK_RESOURCE: ((13, 185), (14, 97), (14, 98), (14, 156), (14, 157)),
        }
        for resource, coordinates in held.items():
            current = self.builder.W27.records_by_coordinate(self.builder.RESOURCE_SPECS[resource].current_path.read_bytes())
            candidate = self.builder.W27.records_by_coordinate(self.bundle.packed[resource])
            for coordinate in coordinates:
                self.assertEqual(current[coordinate].data, candidate[coordinate].data, f"held {resource}:{coordinate}")

    def test_private_build_and_verify(self) -> None:
        output = self.builder.write_candidate(self.bundle)
        self.assertTrue(output.is_dir())
        self.assertTrue(output.resolve().is_relative_to(self.builder.TMP_ROOT.resolve()))
        result = self.builder.verify_private()
        self.assertEqual(result["changed_record_count"], 54)
        self.assertFalse(result["steam_game_resource_written"])


if __name__ == "__main__":
    unittest.main()
