from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_dialogue_quality_wave50_static_blocks9_12_v1.py"
SPEC = importlib.util.spec_from_file_location("wave50_static_blocks9_12_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot import Wave 50 builder")
wave50 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave50
SPEC.loader.exec_module(wave50)


class Wave50StaticBlocks9And12Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packed, cls.raw, cls.audit, cls.manifest = wave50.prepare_candidate()
        cls.before = {
            resource: wave50.records_by_coordinate(wave50.RESOURCE_SPECS[resource].current_path.read_bytes())
            for resource in wave50.RESOURCE_ORDER
        }
        cls.after = {
            resource: wave50.records_by_coordinate(cls.packed[resource])
            for resource in wave50.RESOURCE_ORDER
        }

    def test_exact_reviewed_scope(self) -> None:
        self.assertEqual(len(wave50.PK_BLOCK9_CHANGES), 35)
        self.assertEqual(len(wave50.BASE_MATCHING_BLOCK9_CHANGES), 19)
        self.assertEqual(len(wave50.BLOCK12_51_CHANGES), 2)
        self.assertEqual(len(wave50.CHANGES), 56)
        self.assertEqual(sum(change.resource == wave50.BASE_RESOURCE for change in wave50.CHANGES), 20)
        self.assertEqual(sum(change.resource == wave50.PK_RESOURCE for change in wave50.CHANGES), 36)
        pk_coordinates = {change.coordinate for change in wave50.PK_BLOCK9_CHANGES}
        self.assertFalse(set(wave50.EXCLUDED_STYLE_HOLDS) & pk_coordinates)
        self.assertFalse(set(wave50.EXCLUDED_STATIC_HOLDS) & pk_coordinates)
        self.assertEqual(
            next(change.target_literals for change in wave50.PK_BLOCK9_CHANGES if change.coordinate == (9, 2135)),
            ("함부로 덤비기만 한다고\n병법이 되는 건 아니지 않느냐",),
        )

    def test_only_declared_resource_qualified_records_change(self) -> None:
        for resource in wave50.RESOURCE_ORDER:
            with self.subTest(resource=resource):
                changed = {
                    coordinate
                    for coordinate, record in self.before[resource].items()
                    if record.data != self.after[resource][coordinate].data
                }
                expected = {change.coordinate for change in wave50.CHANGES if change.resource == resource}
                self.assertEqual(changed, expected)
                self.assertEqual(set(self.before[resource]), set(self.after[resource]))

    def test_static_opcode_marker_lf_and_font_contracts(self) -> None:
        advance, _font = wave50.W27.load_font_advance()
        for change in wave50.CHANGES:
            with self.subTest(resource=change.resource, coordinate=change.coordinate_text):
                before = self.before[change.resource][change.coordinate]
                after = self.after[change.resource][change.coordinate]
                pin = wave50.RECORD_PINS[change.identity]
                self.assertEqual(wave50.W27.literal_texts(after), change.target_literals)
                self.assertEqual(len(wave50.W27.literal_texts(after)), len(wave50.W27.literal_texts(before)))
                self.assertEqual(wave50.W27.marker_topology(after), wave50.W27.marker_topology(before))
                self.assertEqual(wave50.W27.opaque_spans(after), wave50.W27.opaque_spans(before))
                self.assertEqual(wave50.runtime_opcodes(before), ())
                self.assertFalse(wave50.W27.complete_0143_commands(wave50.W27.opaque_spans(before)))
                self.assertEqual("".join(wave50.W27.literal_texts(after)).count("\n"), "".join(wave50.W27.literal_texts(before)).count("\n"))
                layout = wave50.W27.line_layout(change.target_literals, advance)
                self.assertLessEqual(layout["line_count"], wave50.MAX_LINES)
                self.assertLessEqual(layout["max_width_px"], wave50.MAX_LINE_PX)
                self.assertEqual(layout["wide_fallback_codepoints"], [])
                self.assertEqual(tuple(layout["line_widths_px"]), pin.target_line_widths_px)

    def test_pc_japanese_source_and_target_record_pins(self) -> None:
        pc_jp = {
            resource: wave50.records_by_coordinate(wave50.RESOURCE_SPECS[resource].pc_jp_source.read_bytes())
            for resource in wave50.RESOURCE_ORDER
        }
        for change in wave50.CHANGES:
            with self.subTest(resource=change.resource, coordinate=change.coordinate_text):
                pin = wave50.RECORD_PINS[change.identity]
                self.assertEqual(wave50.sha256_bytes(self.before[change.resource][change.coordinate].data), pin.current_sha256)
                self.assertEqual(len(self.before[change.resource][change.coordinate].data), pin.current_size)
                self.assertEqual(wave50.sha256_bytes(pc_jp[change.resource][change.coordinate].data), pin.pc_jp_sha256)
                self.assertEqual(wave50.sha256_bytes(self.after[change.resource][change.coordinate].data), pin.target_sha256)
                self.assertEqual(len(self.after[change.resource][change.coordinate].data), pin.target_size)

    def test_verified_base_pairings_and_styled_block12_family(self) -> None:
        pc_jp = {
            resource: wave50.records_by_coordinate(wave50.RESOURCE_SPECS[resource].pc_jp_source.read_bytes())
            for resource in wave50.RESOURCE_ORDER
        }
        wave50.validate_exact_base_counterparts(self.before, pc_jp)
        self.assertEqual(set(wave50.BASE_TO_PK_EQUIVALENTS), {change.coordinate for change in wave50.BASE_MATCHING_BLOCK9_CHANGES})
        for resource in wave50.RESOURCE_ORDER:
            with self.subTest(resource=resource):
                record = self.after[resource][(12, 51)]
                self.assertEqual(wave50.W27.literal_texts(record), wave50.BLOCK12_51_TARGET)

    def test_packed_and_raw_output_profiles_are_pinned(self) -> None:
        for resource in wave50.RESOURCE_ORDER:
            with self.subTest(resource=resource):
                profile = wave50.TARGET_PROFILES[resource]
                self.assertEqual(len(self.packed[resource]), profile["size"])
                self.assertEqual(wave50.sha256_bytes(self.packed[resource]), profile["sha256"])
                self.assertEqual(len(self.raw[resource]), profile["raw_size"])
                self.assertEqual(wave50.sha256_bytes(self.raw[resource]), profile["raw_sha256"])
        self.assertEqual(self.audit["changed_record_count"], 56)
        self.assertEqual(self.audit["changed_record_count_by_resource"], {wave50.BASE_RESOURCE: 20, wave50.PK_RESOURCE: 36})
        self.assertEqual(self.manifest["steam_game_resource_write"], "absent")

    def test_private_output_guard_rejects_repository_root(self) -> None:
        with self.assertRaises(wave50.Wave50Error):
            wave50.require_private(wave50.REPO, "repository")


if __name__ == "__main__":
    unittest.main(verbosity=2)
