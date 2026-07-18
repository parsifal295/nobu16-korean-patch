#!/usr/bin/env python3
"""Regression contracts for the PC-only Wave 14 static-inflection candidate."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_dialogue_quality_wave14_static_inflection_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("pc_dialogue_quality_wave14", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


WAVE14 = load_builder()


class Wave14StaticInflectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.live_profile = WAVE14.profile_hashes(WAVE14.DEFAULT_STEAM_ROOT)
        if cls.live_profile == WAVE14.INPUT_SHA256:
            cls.mode = "predecessor"
            cls.output_a, cls.audit_a = WAVE14.prepare_candidate(WAVE14.DEFAULT_STEAM_ROOT)
            cls.output_b, cls.audit_b = WAVE14.prepare_candidate(WAVE14.DEFAULT_STEAM_ROOT)
        elif cls.live_profile == WAVE14.TARGET_SHA256:
            cls.mode = "target"
            WAVE14.verify_installed(WAVE14.DEFAULT_STEAM_ROOT)
            cls.output_a = {
                resource: (WAVE14.DEFAULT_STEAM_ROOT / resource).read_bytes()
                for resource in WAVE14.CHANGED_PATHS
            }
            cls.output_b = dict(cls.output_a)
            cls.audit_a = None
            cls.audit_b = None
        else:
            raise RuntimeError("Steam profile is neither the pinned Wave 14 predecessor nor target")

    def test_current_and_target_profiles_are_completely_pinned(self) -> None:
        self.assertEqual(tuple(WAVE14.INPUT_SHA256), WAVE14.PROFILE_PATHS)
        self.assertEqual(tuple(WAVE14.TARGET_SHA256), WAVE14.PROFILE_PATHS)
        self.assertEqual(set(WAVE14.CHANGED_PATHS), set(self.output_a))
        self.assertIn(self.mode, {"predecessor", "target"})
        if self.mode == "predecessor":
            self.assertEqual(self.audit_a["input_sha256"], WAVE14.INPUT_SHA256)
            self.assertEqual(self.audit_a["target_sha256"], WAVE14.TARGET_SHA256)
        else:
            self.assertEqual(self.live_profile, WAVE14.TARGET_SHA256)
        for change in WAVE14.CHANGES:
            with self.subTest(change=change.coordinate_text):
                self.assertTrue(change.target_record_sha256)
                self.assertGreater(change.target_record_size, 0)

    def test_only_the_eleven_pinned_records_change(self) -> None:
        if self.mode != "predecessor":
            self.skipTest("installed Steam is already the target; predecessor comparison is intentionally unavailable")
        expected_by_resource: dict[str, set[tuple[int, int]]] = {
            resource: set() for resource in WAVE14.CHANGED_PATHS
        }
        for change in WAVE14.CHANGES:
            expected_by_resource[change.resource].add(change.coordinate)
        for resource in WAVE14.CHANGED_PATHS:
            with self.subTest(resource=resource):
                before = WAVE14.records_by_coordinate((WAVE14.DEFAULT_STEAM_ROOT / resource).read_bytes())
                after = WAVE14.records_by_coordinate(self.output_a[resource])
                self.assertEqual(before.keys(), after.keys())
                changed = {coordinate for coordinate in before if before[coordinate].data != after[coordinate].data}
                self.assertEqual(changed, expected_by_resource[resource])

    def test_each_target_is_static_and_byte_pinned(self) -> None:
        by_resource = {
            resource: WAVE14.records_by_coordinate(packed)
            for resource, packed in self.output_a.items()
        }
        for change in WAVE14.CHANGES:
            with self.subTest(change=change.coordinate_text):
                record = by_resource[change.resource][change.coordinate]
                self.assertEqual(WAVE14.sha256_bytes(record.data), change.target_record_sha256)
                self.assertEqual(len(record.data), change.target_record_size)
                self.assertEqual(WAVE14.literal_texts(record), change.target_literals)
                self.assertEqual(WAVE14.morphology_commands(record), ())
                self.assertEqual(
                    WAVE14.opaque_spans(record),
                    tuple(b"" for _ in change.target_literals) + (WAVE14.RECORD_TERMINATOR,),
                )
                self.assertEqual(
                    "".join(change.current_literals).count("\n"),
                    "".join(change.target_literals).count("\n"),
                )
                self.assertLessEqual("".join(change.target_literals).count("\n") + 1, 3)

    def test_build_is_deterministic_and_pc_only(self) -> None:
        self.assertEqual(self.output_a, self.output_b)
        if self.mode == "target":
            WAVE14.verify_installed(WAVE14.DEFAULT_STEAM_ROOT)
            return
        self.assertEqual(
            json.dumps(self.audit_a, ensure_ascii=False, sort_keys=True),
            json.dumps(self.audit_b, ensure_ascii=False, sort_keys=True),
        )
        policy = self.audit_a["source_policy"]
        self.assertTrue(policy["pristine_pc_japanese_read"])
        self.assertTrue(policy["pc_en_sc_tc_context_read"])
        self.assertFalse(policy["switch_korean_read"])
        self.assertFalse(policy["steam_game_resource_written"])

    def test_safety_scope_keeps_dynamic_or_contextual_families_out(self) -> None:
        actual = {(change.resource, change.coordinate) for change in WAVE14.CHANGES}
        excluded = {
            (WAVE14.BASE_MSGGAME, (6, 2169)),
            (WAVE14.PK_MSGGAME, (6, 2175)),
            (WAVE14.BASE_MSGGAME, (6, 3506)),
            (WAVE14.PK_MSGGAME, (6, 3513)),
            (WAVE14.PK_MSGGAME, (9, 1828)),
        }
        self.assertFalse(actual & excluded)
        self.assertEqual(len(WAVE14.CHANGES), 11)


if __name__ == "__main__":
    unittest.main(verbosity=2)
