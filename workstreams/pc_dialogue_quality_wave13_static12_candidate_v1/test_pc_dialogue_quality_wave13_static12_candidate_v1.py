#!/usr/bin/env python3
"""Regression contracts for the private Wave 13 static dialogue candidate."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_dialogue_quality_wave13_static12_candidate_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("pc_dialogue_quality_wave13", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load Wave 13 builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


WAVE13 = load_builder()


class Wave13Static12Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle_a = WAVE13.prepare_candidate()
        cls.bundle_b = WAVE13.prepare_candidate()
        cls.before = WAVE13.records_by_coordinate(
            WAVE13.validate_current_steam_input(WAVE13.CURRENT_STEAM_PK_MSGGAME)
        )
        cls.after = WAVE13.records_by_coordinate(cls.bundle_a.packed_msggame)

    def test_current_steam_input_and_candidate_hashes_are_fixed(self) -> None:
        self.assertEqual(WAVE13.RESOURCE, "MSG_PK/JP/msggame.bin")
        self.assertEqual(WAVE13.INPUT_SHA256, self.bundle_a.input_sha256)
        self.assertEqual(WAVE13.TARGET_SHA256, self.bundle_a.output_sha256)
        self.assertEqual(len(self.bundle_a.packed_msggame), WAVE13.TARGET_SIZE)
        self.assertEqual(len(WAVE13.CHANGES), 12)
        self.assertEqual(
            [change.coordinate for change in WAVE13.CHANGES],
            [
                (6, 4341), (6, 4342), (6, 4343), (6, 4344), (6, 4345), (6, 4346),
                (6, 4352), (6, 4354), (6, 4355), (6, 4359), (6, 4366), (6, 4367),
            ],
        )

    def test_exact_preimages_targets_and_static_controls(self) -> None:
        for change in WAVE13.CHANGES:
            with self.subTest(coordinate=change.coordinate):
                before = self.before[change.coordinate]
                after = self.after[change.coordinate]
                self.assertEqual(WAVE13.sha256_bytes(before.data), change.input_record_sha256)
                self.assertEqual(WAVE13.sha256_bytes(after.data), change.target_record_sha256)
                self.assertEqual(len(before.data), change.input_record_size)
                self.assertEqual(len(after.data), change.target_record_size)
                self.assertEqual(WAVE13.literal_texts(before), change.current_literals)
                self.assertEqual(WAVE13.literal_texts(after), change.target_literals)
                self.assertEqual(
                    tuple(value.hex().upper() for value in WAVE13.opaque_spans(before)),
                    WAVE13.expected_input_opaque(change),
                )
                self.assertEqual(
                    tuple(value.hex().upper() for value in WAVE13.opaque_spans(after)),
                    WAVE13.expected_output_opaque(change),
                )
                self.assertEqual(WAVE13.marker_topology(before), WAVE13.marker_topology(after))
                self.assertTrue(after.data.endswith(WAVE13.RECORD_TERMINATOR))
                self.assertNotIn(bytes((1, 67)), after.data)
                self.assertEqual("".join(change.current_literals).count("\n"), 1)
                self.assertEqual("".join(change.target_literals).count("\n"), 1)

    def test_only_the_twelve_records_changed_and_raw_roundtrips(self) -> None:
        changed = {
            coordinate
            for coordinate in self.before
            if self.before[coordinate].data != self.after[coordinate].data
        }
        expected = {change.coordinate for change in WAVE13.CHANGES}
        self.assertEqual(changed, expected)
        self.assertEqual(self.before.keys(), self.after.keys())
        for coordinate, before in self.before.items():
            if coordinate not in expected:
                self.assertEqual(before.data, self.after[coordinate].data)
        WAVE13.validate_raw_roundtrip(self.bundle_a.packed_msggame)

    def test_waves_10_to_12_are_explicitly_disjoint(self) -> None:
        ours = {change.coordinate for change in WAVE13.CHANGES}
        prior = WAVE13.prior_wave_coordinates()
        self.assertEqual(set(prior), {"wave10", "wave11", "wave12"})
        for label, coordinates in prior.items():
            with self.subTest(wave=label):
                self.assertFalse(ours & coordinates)
        evidence = WAVE13.validate_prior_wave_disjointness()
        self.assertEqual(set(evidence), {"wave10", "wave11", "wave12"})

    def test_candidate_is_deterministic_private_and_has_no_apply_operation(self) -> None:
        self.assertEqual(self.bundle_a.packed_msggame, self.bundle_b.packed_msggame)
        self.assertEqual(
            json.dumps(self.bundle_a.audit, ensure_ascii=False, sort_keys=True),
            json.dumps(self.bundle_b.audit, ensure_ascii=False, sort_keys=True),
        )
        self.assertFalse(self.bundle_a.audit["source_policy"]["switch_korean_used"])
        self.assertEqual(self.bundle_a.audit["source_policy"]["steam_write_capability"], "absent")
        manifest = WAVE13.build_manifest(self.bundle_a, "A" * 64)
        self.assertEqual(manifest["steam_write_capability"], "absent")
        self.assertIsNone(manifest["steam_apply_command"])
        self.assertIsNone(manifest["git_operation"])
        with self.assertRaises(WAVE13.Wave13Error):
            WAVE13.require_private_output(WAVE13.CURRENT_STEAM_PK_MSGGAME, "must reject Steam")


if __name__ == "__main__":
    unittest.main(verbosity=2)
