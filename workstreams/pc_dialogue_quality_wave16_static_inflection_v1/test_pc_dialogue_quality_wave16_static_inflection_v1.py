#!/usr/bin/env python3
"""Regression contracts for the private Wave 16 static-inflection candidate."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_dialogue_quality_wave16_static_inflection_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("pc_dialogue_quality_wave16", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


WAVE16 = load_builder()


class Wave16StaticInflectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.live_profile = WAVE16.profile_hashes(WAVE16.DEFAULT_STEAM_ROOT)
        if cls.live_profile != WAVE16.INPUT_SHA256:
            raise RuntimeError("Steam profile is not the Wave 14 input pinned for Wave 16")
        cls.output_a, cls.audit_a = WAVE16.prepare_candidate(WAVE16.DEFAULT_STEAM_ROOT)
        cls.output_b, cls.audit_b = WAVE16.prepare_candidate(WAVE16.DEFAULT_STEAM_ROOT)
        cls.before = {
            resource: WAVE16.records_by_coordinate((WAVE16.DEFAULT_STEAM_ROOT / resource).read_bytes())
            for resource in WAVE16.CHANGED_PATHS
        }
        cls.after = {
            resource: WAVE16.records_by_coordinate(packed)
            for resource, packed in cls.output_a.items()
        }

    def test_wave14_profile_is_the_only_pinned_input(self) -> None:
        self.assertEqual(tuple(WAVE16.INPUT_SHA256), WAVE16.PROFILE_PATHS)
        self.assertEqual(tuple(WAVE16.TARGET_SHA256), WAVE16.PROFILE_PATHS)
        self.assertEqual(self.live_profile, WAVE16.INPUT_SHA256)
        self.assertEqual(
            WAVE16.INPUT_SHA256[WAVE16.BASE_MSGGAME],
            "4D147A4AD73466E882043D8A5E47F0D4DAF37473702A8CEABAEFFBF4E76F2EB8",
        )
        self.assertEqual(
            WAVE16.INPUT_SHA256[WAVE16.PK_MSGGAME],
            "BD789D1C5230159433BDB9F2FCBE4B0ABABF9D84FAD2FE1C16EED45B071CE860",
        )
        for resource in WAVE16.CHANGED_PATHS:
            with self.subTest(resource=resource):
                self.assertEqual(len(self.output_a[resource]), WAVE16.TARGET_PACKED_SIZES[resource])
                self.assertEqual(WAVE16.sha256_bytes(self.output_a[resource]), WAVE16.TARGET_SHA256[resource])

    def test_exact_six_targets_and_static_opaque_layouts(self) -> None:
        self.assertEqual(len(WAVE16.CHANGES), 6)
        self.assertEqual(
            [(change.resource, change.coordinate) for change in WAVE16.CHANGES],
            [
                (WAVE16.BASE_MSGGAME, (8, 398)),
                (WAVE16.BASE_MSGGAME, (8, 969)),
                (WAVE16.BASE_MSGGAME, (15, 2261)),
                (WAVE16.PK_MSGGAME, (8, 410)),
                (WAVE16.PK_MSGGAME, (8, 981)),
                (WAVE16.PK_MSGGAME, (15, 2292)),
            ],
        )
        for change in WAVE16.CHANGES:
            with self.subTest(change=f"{change.resource}:{change.coordinate_text}"):
                before = self.before[change.resource][change.coordinate]
                after = self.after[change.resource][change.coordinate]
                self.assertEqual(WAVE16.sha256_bytes(before.data), change.input_record_sha256)
                self.assertEqual(len(before.data), change.input_record_size)
                self.assertEqual(WAVE16.literal_texts(before), change.current_literals)
                self.assertEqual(
                    tuple(value.hex().upper() for value in WAVE16.opaque_spans(before)),
                    change.input_opaque_spans_hex,
                )
                self.assertEqual(WAVE16.morphology_commands(before), change.removed_commands_hex)
                self.assertEqual(WAVE16.stripped_opaque_spans(before), WAVE16.output_opaque_spans(change))
                self.assertEqual(WAVE16.sha256_bytes(after.data), change.target_record_sha256)
                self.assertEqual(len(after.data), change.target_record_size)
                self.assertEqual(WAVE16.literal_texts(after), change.target_literals)
                self.assertEqual(WAVE16.morphology_commands(after), ())
                self.assertEqual(WAVE16.opaque_spans(after), WAVE16.output_opaque_spans(change))
                self.assertTrue(after.data.endswith(WAVE16.RECORD_TERMINATOR))
                self.assertEqual(WAVE16.marker_topology(after), WAVE16.marker_topology(before))
                self.assertEqual("".join(change.current_literals).count("\n"), "".join(change.target_literals).count("\n"))
                self.assertLessEqual("".join(change.target_literals).count("\n") + 1, 3)

    def test_only_the_six_records_change_and_archives_round_trip(self) -> None:
        expected_by_resource = {resource: set() for resource in WAVE16.CHANGED_PATHS}
        for change in WAVE16.CHANGES:
            expected_by_resource[change.resource].add(change.coordinate)
        for resource in WAVE16.CHANGED_PATHS:
            with self.subTest(resource=resource):
                self.assertEqual(self.before[resource].keys(), self.after[resource].keys())
                changed = {
                    coordinate
                    for coordinate in self.before[resource]
                    if self.before[resource][coordinate].data != self.after[resource][coordinate].data
                }
                self.assertEqual(changed, expected_by_resource[resource])
                for coordinate, record in self.before[resource].items():
                    if coordinate not in expected_by_resource[resource]:
                        self.assertEqual(record.data, self.after[resource][coordinate].data)
                WAVE16.validate_raw_roundtrip(self.output_a[resource], f"test candidate {resource}")

    def test_pc_jp_and_pk_en_sc_tc_anchors_are_exact(self) -> None:
        jp, contexts = WAVE16.load_references(WAVE16.DEFAULT_STEAM_ROOT)
        WAVE16.validate_family_anchors(jp, contexts)
        self.assertEqual(set(contexts), {"EN", "SC", "TC"})
        for family in WAVE16.FAMILIES:
            with self.subTest(family=family.name):
                self.assertEqual(
                    WAVE16.literal_texts(jp[WAVE16.BASE_MSGGAME][family.base_coordinate]),
                    family.jp_literals,
                )
                self.assertEqual(
                    WAVE16.literal_texts(jp[WAVE16.PK_MSGGAME][family.pk_coordinate]),
                    family.jp_literals,
                )
                for language in ("EN", "SC", "TC"):
                    record = contexts[language][family.pk_coordinate]
                    self.assertEqual(WAVE16.literal_texts(record), family.pk_context_literals[language])
                    self.assertEqual(WAVE16.morphology_commands(record), family.pk_context_commands[language])

    def test_candidate_is_deterministic_and_cannot_target_steam(self) -> None:
        self.assertEqual(self.output_a, self.output_b)
        self.assertEqual(
            json.dumps(self.audit_a, ensure_ascii=False, sort_keys=True),
            json.dumps(self.audit_b, ensure_ascii=False, sort_keys=True),
        )
        policy = self.audit_a["source_policy"]
        self.assertTrue(policy["wave14_profile_required"])
        self.assertTrue(policy["pristine_pc_japanese_read"])
        self.assertTrue(policy["pc_pk_en_sc_tc_context_read"])
        self.assertFalse(policy["switch_korean_read"])
        self.assertFalse(policy["steam_game_resource_written"])
        self.assertEqual(policy["git_operation"], "absent")
        self.assertEqual(policy["release_operation"], "absent")
        with self.assertRaises(WAVE16.Wave16Error):
            WAVE16.require_tmp(WAVE16.DEFAULT_STEAM_ROOT, "Steam must be rejected")
        manifest = {
            "steam_write_capability": "absent",
            "git_operation": "absent",
            "release_operation": "absent",
        }
        self.assertEqual(manifest["steam_write_capability"], "absent")


if __name__ == "__main__":
    unittest.main(verbosity=2)
