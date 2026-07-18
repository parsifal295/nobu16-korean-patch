#!/usr/bin/env python3
"""Regression contracts for the private PC-only Wave 26 candidate."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_dialogue_quality_wave26_static_inflection_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("pc_dialogue_quality_wave26", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


WAVE26 = load_builder()


EXPECTED_PAIRS = (
    ((15, 2204), (15, 2234)), ((15, 2205), (15, 2235)),
    ((15, 2206), (15, 2236)), ((15, 2207), (15, 2237)),
    ((15, 2209), (15, 2239)), ((15, 2211), (15, 2241)),
    ((15, 2213), (15, 2243)), ((15, 2214), (15, 2244)),
    ((15, 2215), (15, 2245)), ((15, 2216), (15, 2246)),
    ((15, 2217), (15, 2247)), ((15, 2218), (15, 2248)),
    ((15, 2222), (15, 2252)), ((15, 2223), (15, 2253)),
    ((15, 2225), (15, 2255)), ((15, 2238), (15, 2268)),
    ((15, 2240), (15, 2270)), ((15, 2241), (15, 2271)),
    ((15, 2246), (15, 2276)), ((15, 2247), (15, 2277)),
)


class Wave26StaticInflectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        WAVE26.require_predecessor_root(WAVE26.PREDECESSOR_ROOT)
        WAVE26.validate_wave25_evidence(WAVE26.PREDECESSOR_ROOT)
        cls.before = {
            resource: WAVE26.records_by_coordinate((WAVE26.PREDECESSOR_ROOT / resource).read_bytes())
            for resource in WAVE26.CHANGED_PATHS
        }
        cls.output_a, cls.audit_a = WAVE26.prepare_candidate()
        cls.output_b, cls.audit_b = WAVE26.prepare_candidate()
        cls.after = {resource: WAVE26.records_by_coordinate(data) for resource, data in cls.output_a.items()}
        cls.advance, cls.font = WAVE26.load_font_advance()

    def test_exact_wave25_eleven_file_preimage_and_evidence(self) -> None:
        hashes, sizes = WAVE26.profile(WAVE26.PREDECESSOR_ROOT)
        self.assertEqual(hashes, WAVE26.INPUT_SHA256)
        self.assertEqual(sizes, WAVE26.INPUT_SIZES)
        self.assertEqual(tuple(WAVE26.INPUT_SHA256), WAVE26.PROFILE_PATHS)
        for item in WAVE26.WAVE25_EVIDENCE.values():
            path = Path(item["path"])
            self.assertEqual(path.stat().st_size, item["size"])
            self.assertEqual(WAVE26.sha256_path(path), item["sha256"])
        self.assertEqual(WAVE26.INPUT_SHA256[WAVE26.PK_MSGGAME], "70FB0AB6EB2B07795CB37DEEB8941635184DC3C48246A6F45C25B59CD75559BC")

    def test_exact_twenty_base_to_pk_pairs_and_target_literals(self) -> None:
        self.assertEqual(
            tuple((family.base_coordinate, family.pk_coordinate) for family in WAVE26.FAMILIES),
            EXPECTED_PAIRS,
        )
        self.assertEqual(len(WAVE26.FAMILIES), 20)
        self.assertEqual(len(WAVE26.TARGET_RECORD_PINS), 20)
        for family in WAVE26.FAMILIES:
            target_hash, target_size, target_widths = WAVE26.TARGET_RECORD_PINS[family.name]
            for resource, coordinate in ((WAVE26.BASE_MSGGAME, family.base_coordinate), (WAVE26.PK_MSGGAME, family.pk_coordinate)):
                with self.subTest(family=family.name, resource=resource):
                    before = self.before[resource][coordinate]
                    after = self.after[resource][coordinate]
                    self.assertNotEqual(before.data, after.data)
                    self.assertEqual(WAVE26.sha256_bytes(after.data), target_hash)
                    self.assertEqual(len(after.data), target_size)
                    self.assertEqual(WAVE26.literal_texts(after), family.target_literals)
                    self.assertEqual(WAVE26.opaque_spans(after), WAVE26.stripped_opaque_spans(before))
                    self.assertEqual(WAVE26.marker_topology(after), WAVE26.marker_topology(before))
                    self.assertTrue(before.data.endswith(WAVE26.RECORD_TERMINATOR))
                    self.assertTrue(after.data.endswith(WAVE26.RECORD_TERMINATOR))
                    self.assertTrue(WAVE26.complete_0143_commands(WAVE26.opaque_spans(before)))
                    self.assertEqual(WAVE26.complete_0143_commands(WAVE26.opaque_spans(after)), ())
                    self.assertEqual(
                        "".join(WAVE26.literal_texts(before)).count("\n"),
                        "".join(WAVE26.literal_texts(after)).count("\n"),
                    )
                    layout = WAVE26.line_layout(WAVE26.literal_texts(after), type(self).advance)
                    self.assertEqual(tuple(layout["line_widths_px"]), target_widths)
                    self.assertLessEqual(layout["max_width_px"], WAVE26.DIALOGUE_MAX_LINE_PX)
                    self.assertEqual(layout["wide_fallback_codepoints"], [])

    def test_only_the_forty_specified_records_change(self) -> None:
        expected = WAVE26.expected_coordinate_sets()
        for resource in WAVE26.CHANGED_PATHS:
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
        hashes = {**WAVE26.INPUT_SHA256, **{resource: WAVE26.sha256_bytes(data) for resource, data in self.output_a.items()}}
        sizes = {**WAVE26.INPUT_SIZES, **{resource: len(data) for resource, data in self.output_a.items()}}
        self.assertEqual(hashes, WAVE26.TARGET_SHA256)
        self.assertEqual(sizes, WAVE26.TARGET_SIZES)
        self.assertEqual(WAVE26.TARGET_SHA256[WAVE26.BASE_MSGGAME], "031BD5C425FA0259624524E78DB99D4F54B16A43D96A43FE850C2A51500D779A")
        self.assertEqual(WAVE26.TARGET_SHA256[WAVE26.PK_MSGGAME], "828559146ACE4F456E9E764A69C5E36B88B34F969E108B9E3177614083E9C760")
        for resource, packed in self.output_a.items():
            WAVE26.validate_raw_roundtrip(packed, f"test Wave 26 {resource}")

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
        with self.assertRaises(WAVE26.Wave26Error):
            WAVE26.require_tmp(WAVE26.DEFAULT_STEAM_ROOT, "Steam path")


if __name__ == "__main__":
    unittest.main(verbosity=2)
