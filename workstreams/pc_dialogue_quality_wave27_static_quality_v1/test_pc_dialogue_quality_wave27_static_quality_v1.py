#!/usr/bin/env python3
"""Regression contracts for the private PC-only Wave 27 candidate."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_dialogue_quality_wave27_static_quality_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("pc_dialogue_quality_wave27", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


WAVE27 = load_builder()


EXPECTED_PAIRS = (
    ((8, 1033), (8, 1045)), ((8, 1034), (8, 1046)),
    ((8, 1035), (8, 1047)), ((8, 1036), (8, 1048)),
    ((8, 1037), (8, 1049)), ((8, 1038), (8, 1050)),
    ((8, 1039), (8, 1051)), ((8, 1040), (8, 1052)),
    ((8, 1041), (8, 1053)), ((8, 1042), (8, 1054)),
    ((8, 1044), (8, 1056)), ((8, 1047), (8, 1059)),
    ((8, 1048), (8, 1060)), ((8, 1049), (8, 1061)),
    ((8, 1051), (8, 1063)), ((8, 1053), (8, 1065)),
    ((8, 1055), (8, 1067)), ((8, 1056), (8, 1068)),
    ((8, 1057), (8, 1069)), ((8, 1059), (8, 1071)),
)


class Wave27StaticQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        WAVE27.require_predecessor_root(WAVE27.PREDECESSOR_ROOT)
        WAVE27.validate_wave26_evidence(WAVE27.PREDECESSOR_ROOT)
        cls.before = {
            resource: WAVE27.records_by_coordinate((WAVE27.PREDECESSOR_ROOT / resource).read_bytes())
            for resource in WAVE27.CHANGED_PATHS
        }
        cls.output_a, cls.audit_a = WAVE27.prepare_candidate()
        cls.output_b, cls.audit_b = WAVE27.prepare_candidate()
        cls.after = {resource: WAVE27.records_by_coordinate(data) for resource, data in cls.output_a.items()}
        cls.advance, cls.font = WAVE27.load_font_advance()

    def test_exact_wave26_eleven_file_preimage_and_evidence(self) -> None:
        hashes, sizes = WAVE27.profile(WAVE27.PREDECESSOR_ROOT)
        self.assertEqual(hashes, WAVE27.INPUT_SHA256)
        self.assertEqual(sizes, WAVE27.INPUT_SIZES)
        self.assertEqual(tuple(WAVE27.INPUT_SHA256), WAVE27.PROFILE_PATHS)
        for item in WAVE27.WAVE26_EVIDENCE.values():
            path = Path(item["path"])
            self.assertEqual(path.stat().st_size, item["size"])
            self.assertEqual(WAVE27.sha256_path(path), item["sha256"])
        self.assertEqual(WAVE27.INPUT_SHA256[WAVE27.BASE_MSGGAME], "031BD5C425FA0259624524E78DB99D4F54B16A43D96A43FE850C2A51500D779A")
        self.assertEqual(WAVE27.INPUT_SHA256[WAVE27.PK_MSGGAME], "828559146ACE4F456E9E764A69C5E36B88B34F969E108B9E3177614083E9C760")

    def test_exact_twenty_base_to_pk_pairs_and_target_literals(self) -> None:
        self.assertEqual(
            tuple((family.base_coordinate, family.pk_coordinate) for family in WAVE27.FAMILIES),
            EXPECTED_PAIRS,
        )
        self.assertEqual(len(WAVE27.FAMILIES), 20)
        self.assertEqual(len(WAVE27.TARGET_RECORD_PINS), 20)
        for family in WAVE27.FAMILIES:
            target_hash, target_size, target_widths = WAVE27.TARGET_RECORD_PINS[family.name]
            for resource, coordinate in ((WAVE27.BASE_MSGGAME, family.base_coordinate), (WAVE27.PK_MSGGAME, family.pk_coordinate)):
                with self.subTest(family=family.name, resource=resource):
                    before = self.before[resource][coordinate]
                    after = self.after[resource][coordinate]
                    self.assertNotEqual(before.data, after.data)
                    self.assertEqual(WAVE27.sha256_bytes(after.data), target_hash)
                    self.assertEqual(len(after.data), target_size)
                    self.assertEqual(WAVE27.literal_texts(after), family.target_literals)
                    self.assertEqual(WAVE27.opaque_spans(after), WAVE27.stripped_opaque_spans(before))
                    self.assertEqual(WAVE27.marker_topology(after), WAVE27.marker_topology(before))
                    self.assertTrue(before.data.endswith(WAVE27.RECORD_TERMINATOR))
                    self.assertTrue(after.data.endswith(WAVE27.RECORD_TERMINATOR))
                    self.assertTrue(WAVE27.complete_0143_commands(WAVE27.opaque_spans(before)))
                    self.assertEqual(WAVE27.complete_0143_commands(WAVE27.opaque_spans(after)), ())
                    self.assertEqual(
                        "".join(WAVE27.literal_texts(before)).count("\n"),
                        "".join(WAVE27.literal_texts(after)).count("\n"),
                    )
                    layout = WAVE27.line_layout(WAVE27.literal_texts(after), type(self).advance)
                    self.assertEqual(tuple(layout["line_widths_px"]), target_widths)
                    self.assertLessEqual(layout["max_width_px"], WAVE27.DIALOGUE_MAX_LINE_PX)
                    self.assertEqual(layout["wide_fallback_codepoints"], [])

    def test_only_the_forty_specified_records_change(self) -> None:
        expected = WAVE27.expected_coordinate_sets()
        for resource in WAVE27.CHANGED_PATHS:
            with self.subTest(resource=resource):
                self.assertEqual(set(self.before[resource]), set(self.after[resource]))
                changed = {
                    coordinate for coordinate in self.before[resource]
                    if self.before[resource][coordinate].data != self.after[resource][coordinate].data
                }
                self.assertEqual(changed, expected[resource])
                self.assertEqual(len(changed), 20)
                for coordinate, record in self.before[resource].items():
                    if coordinate not in changed:
                        self.assertEqual(record.data, self.after[resource][coordinate].data)

    def test_packed_full_profile_and_roundtrip_are_pinned(self) -> None:
        hashes = {**WAVE27.INPUT_SHA256, **{resource: WAVE27.sha256_bytes(data) for resource, data in self.output_a.items()}}
        sizes = {**WAVE27.INPUT_SIZES, **{resource: len(data) for resource, data in self.output_a.items()}}
        self.assertEqual(hashes, WAVE27.TARGET_SHA256)
        self.assertEqual(sizes, WAVE27.TARGET_SIZES)
        self.assertEqual(WAVE27.TARGET_SHA256[WAVE27.BASE_MSGGAME], "4D6460F1B717FD8D424229ABD619DE4093C21929F6C42B061BAD62E163C5D3CB")
        self.assertEqual(WAVE27.TARGET_SHA256[WAVE27.PK_MSGGAME], "AD3F6DD64C0AD360C5A8C7A4747ABFCE9B2D72BFFDD3D44940781A68AC2DE8D1")
        for resource, packed in self.output_a.items():
            WAVE27.validate_raw_roundtrip(packed, f"test Wave 27 {resource}")

    def test_pc_only_jp_and_context_anchors(self) -> None:
        anchors = self.audit_a["pc_anchors"]
        self.assertEqual(set(anchors["reference_packed_sha256"]), {"BASE_JP", "PK_JP", "EN", "SC", "TC"})
        self.assertEqual(len(anchors["families"]), 20)
        for row in anchors["families"]:
            self.assertTrue(row["BASE_JP"]["record_sha256"])
            self.assertTrue(row["PK_JP"]["record_sha256"])
            self.assertEqual(set(row["contexts"]), {"EN", "SC", "TC"})
        policy = self.audit_a["source_policy"]
        self.assertTrue(policy["pc_base_pk_jp_and_en_sc_tc_anchors_read"])
        self.assertFalse(policy["switch_korean_read"])

    def test_deterministic_private_only_guards(self) -> None:
        self.assertEqual(self.output_a, self.output_b)
        self.assertEqual(
            json.dumps(self.audit_a, ensure_ascii=False, sort_keys=True),
            json.dumps(self.audit_b, ensure_ascii=False, sort_keys=True),
        )
        self.assertEqual(self.audit_a["changed_record_count"], 40)
        self.assertFalse(self.audit_a["source_policy"]["steam_game_resource_written"])
        self.assertEqual(self.audit_a["source_policy"]["git_operation"], "absent")
        self.assertEqual(self.audit_a["source_policy"]["release_operation"], "absent")
        with self.assertRaises(WAVE27.Wave27Error):
            WAVE27.require_tmp(WAVE27.DEFAULT_STEAM_ROOT, "Steam path")


if __name__ == "__main__":
    unittest.main(verbosity=2)
