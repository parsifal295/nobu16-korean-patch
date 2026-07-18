#!/usr/bin/env python3
"""Fail-closed tests for the private PC-only Wave 23 dialogue candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_dialogue_quality_wave23_static_inflection_v1.py"
SPEC = importlib.util.spec_from_file_location("wave23_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import wiring guard
    raise RuntimeError("cannot import Wave 23 builder")
wave23 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave23
SPEC.loader.exec_module(wave23)


class Wave23StaticInflectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.output, cls.audit = wave23.prepare_candidate()
        cls.before = {resource: (wave23.PREDECESSOR_ROOT / resource).read_bytes() for resource in wave23.CHANGED_PATHS}
        cls.before_records = {resource: wave23.records_by_coordinate(data) for resource, data in cls.before.items()}
        cls.output_records = {resource: wave23.records_by_coordinate(data) for resource, data in cls.output.items()}

    def test_family_inventory_and_coordinates_are_exact(self) -> None:
        self.assertEqual(len(wave23.FAMILIES), 20)
        self.assertEqual(self.audit["changed_record_count"], 40)
        self.assertEqual(sum(family.retain_literal_text for family in wave23.FAMILIES), 2)
        self.assertEqual(
            {(family.base_coordinate, family.pk_coordinate) for family in wave23.FAMILIES},
            {(family.base_coordinate, family.pk_coordinate) for family in wave23.FAMILIES},
        )
        self.assertEqual(
            [(family.base_coordinate, family.pk_coordinate) for family in wave23.FAMILIES],
            [
                ((8, 1045), (8, 1057)), ((8, 1052), (8, 1064)), ((8, 1060), (8, 1072)), ((8, 1067), (8, 1079)), ((8, 1068), (8, 1080)), ((8, 1183), (8, 1199)),
                ((13, 107), (13, 107)), ((13, 121), (13, 121)), ((15, 248), (15, 251)), ((15, 253), (15, 256)), ((15, 261), (15, 264)), ((15, 1506), (15, 1521)),
                ((15, 1588), (15, 1618)), ((15, 1626), (15, 1656)), ((15, 1822), (15, 1852)), ((15, 1823), (15, 1853)), ((15, 1860), (15, 1890)), ((15, 1862), (15, 1892)),
                ((15, 2194), (15, 2224)), ((15, 2195), (15, 2225)),
            ],
        )

    def test_complete_eleven_file_profile_is_pinned(self) -> None:
        wave23.assert_profile(wave23.PREDECESSOR_ROOT, wave23.INPUT_SHA256, wave23.INPUT_SIZES, "test predecessor")
        target_hashes = {**wave23.INPUT_SHA256, **{resource: wave23.sha256_bytes(data) for resource, data in self.output.items()}}
        target_sizes = {**wave23.INPUT_SIZES, **{resource: len(data) for resource, data in self.output.items()}}
        self.assertEqual(target_hashes, wave23.TARGET_SHA256)
        self.assertEqual(target_sizes, wave23.TARGET_SIZES)

    def test_pc_jp_en_sc_tc_anchors_are_fail_closed(self) -> None:
        references, hashes = wave23.load_references()
        wave23.validate_family_anchors(references)
        self.assertEqual(hashes, {language: expected_hash for language, (_path, expected_hash) in wave23.PC_REFERENCE_PATHS.items()})

    def test_exact_changed_set_marker_topology_and_0143_removal(self) -> None:
        for resource in wave23.CHANGED_PATHS:
            expected_coordinates = {
                family.base_coordinate if resource == wave23.BASE_MSGGAME else family.pk_coordinate
                for family in wave23.FAMILIES
            }
            changed = {
                coordinate
                for coordinate in self.before_records[resource]
                if self.before_records[resource][coordinate].data != self.output_records[resource][coordinate].data
            }
            self.assertEqual(changed, expected_coordinates)
        for family in wave23.FAMILIES:
            for resource, coordinate in ((wave23.BASE_MSGGAME, family.base_coordinate), (wave23.PK_MSGGAME, family.pk_coordinate)):
                source = self.before_records[resource][coordinate]
                target = self.output_records[resource][coordinate]
                self.assertEqual(wave23.literal_texts(target), family.target_literals)
                self.assertEqual(wave23.opaque_spans(target), wave23.stripped_opaque_spans(source))
                self.assertEqual(wave23.marker_topology(target), wave23.marker_topology(source))
                self.assertEqual(wave23.morphology_commands(target), ())
                self.assertTrue(target.data.endswith(wave23.RECORD_TERMINATOR))
                self.assertEqual(wave23.sha256_bytes(target.data), family.target.sha256)
                self.assertEqual(len(target.data), family.target.size)

    def test_manual_breaks_and_strict_font_measurement(self) -> None:
        for family in wave23.FAMILIES:
            source = self.before_records[wave23.BASE_MSGGAME][family.base_coordinate]
            self.assertEqual("".join(wave23.literal_texts(source)).count("\n"), "".join(family.target_literals).count("\n"))
            widths = wave23.font_line_widths_px(family.target_literals)
            self.assertEqual(widths, family.target_font_widths_px)
            self.assertLessEqual(max(widths), wave23.DIALOGUE_MAX_LINE_PX)

    def test_retain_pairs_keep_literal_payload_byte_identical(self) -> None:
        retains = [family for family in wave23.FAMILIES if family.retain_literal_text]
        self.assertEqual([family.name for family in retains], ["retain_vanguard", "retain_useful_trait"])
        for family in retains:
            for resource, coordinate in ((wave23.BASE_MSGGAME, family.base_coordinate), (wave23.PK_MSGGAME, family.pk_coordinate)):
                source_payloads = tuple(value.encode("utf-16-le") for value in wave23.literal_texts(self.before_records[resource][coordinate]))
                target_payloads = tuple(value.encode("utf-16-le") for value in wave23.literal_texts(self.output_records[resource][coordinate]))
                self.assertEqual(target_payloads, source_payloads)

    def test_quality_corrections_and_real_font_widths(self) -> None:
        expected = {
            "rumor_illusion": ("유언비어와 환술로 적을 현혹하오.\n장치 준비에 얼마간의 자금이 필요하오나\n더 많은 적을 끌어들일 수 있을 것이오.", (768, 912, 888)),
            "incitement_edict": ("선동에는 약간의 자금이 필요하오.\n교서로 호소한다면\n선동은 틀림없이 성공할 것이오.", (768, 408, 720)),
            "appoint_lord": ("아무래도 비어 있는 군이 있다던데…\n마침 여유가 있는 자가 있으니\n영주로 다스리게 하는 것은 어떻겠소?", (816, 672, 840)),
            "diplomatic_strategy": ("현재 특별히 주의할 세력은 없습니다.\n주변 세력의 전력에 유의하며\n외교·공략 전략을 세워 나가야 합니다.", (840, 648, 888)),
            "strength_wait": ("무모한 진군은 목숨을 잃기 쉽소.\n국력을 높이며 타국끼리 싸워\n피폐해질 때를 기다리는 것도 한 수겠소.", (744, 648, 912)),
        }
        for family in wave23.FAMILIES:
            if family.name in expected:
                text, widths = expected[family.name]
                self.assertEqual("".join(family.target_literals), text)
                self.assertEqual(wave23.font_line_widths_px(family.target_literals), widths)

    def test_private_and_platform_guards(self) -> None:
        with self.assertRaises(wave23.Wave23Error):
            wave23.require_predecessor_root(wave23.REPO)
        with self.assertRaises(wave23.Wave23Error):
            wave23.require_tmp(wave23.REPO / "outside-wave23", "test output")
        self.assertFalse(self.audit["source_policy"]["switch_korean_read"])
        self.assertEqual(self.audit["source_policy"]["steam_apply_capability"], "absent")
        self.assertEqual(self.audit["source_policy"]["git_operation"], "absent")


if __name__ == "__main__":
    unittest.main()
