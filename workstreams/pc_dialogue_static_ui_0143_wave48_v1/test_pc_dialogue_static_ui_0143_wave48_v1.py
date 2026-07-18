from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_dialogue_static_ui_0143_wave48_v1.py"
SPEC = importlib.util.spec_from_file_location("wave48_static_ui_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot import Wave 48 static-UI builder")
wave48 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave48
SPEC.loader.exec_module(wave48)


class Wave48StaticUi0143Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source_hashes_before = {
            resource: wave48.sha256_path(path) for resource, path in wave48.RESOURCE_PATHS.items()
        }
        cls.bundle = wave48.prepare_candidate()
        cls.source_hashes_after = {
            resource: wave48.sha256_path(path) for resource, path in wave48.RESOURCE_PATHS.items()
        }
        cls.before = {
            resource: wave48.W27.records_by_coordinate(path.read_bytes())
            for resource, path in wave48.RESOURCE_PATHS.items()
        }
        cls.after = {
            resource: wave48.W27.records_by_coordinate(packed)
            for resource, packed in cls.bundle.packed.items()
        }
        cls.references, cls.reference_report = wave48.validate_reference_anchors()

    def test_exact_sixteen_family_thirty_two_record_scope(self) -> None:
        self.assertEqual(len(wave48.FAMILIES), 16)
        self.assertEqual(len(wave48.CHANGES), 32)
        self.assertEqual(sum(change.resource == wave48.BASE_RESOURCE for change in wave48.CHANGES), 16)
        self.assertEqual(sum(change.resource == wave48.PK_RESOURCE for change in wave48.CHANGES), 16)
        self.assertEqual(len({(change.resource, change.coordinate) for change in wave48.CHANGES}), 32)

    def test_w45_input_profile_and_source_files_are_unchanged(self) -> None:
        self.assertEqual(
            wave48.INPUT_PROFILES[wave48.BASE_RESOURCE]["sha256"],
            "F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB",
        )
        self.assertEqual(
            wave48.INPUT_PROFILES[wave48.PK_RESOURCE]["sha256"],
            "0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092",
        )
        self.assertEqual(self.source_hashes_before, self.source_hashes_after)
        self.assertEqual(
            self.source_hashes_after,
            {resource: profile["sha256"] for resource, profile in wave48.INPUT_PROFILES.items()},
        )

    def test_pc_jp_en_sc_tc_semantic_anchor_contract(self) -> None:
        self.assertEqual(set(self.reference_report["profiles"]), {"BASE_JP", "PK_JP", "EN", "SC", "TC"})
        self.assertEqual(len(self.reference_report["families"]), 16)
        for family in wave48.FAMILIES:
            with self.subTest(family=family.name):
                self.assertEqual(
                    wave48.W27.literal_texts(self.references["BASE_JP"][family.base_coordinate]),
                    (family.jp_literal,),
                )
                self.assertEqual(
                    wave48.W27.literal_texts(self.references["PK_JP"][family.pk_coordinate]),
                    (family.jp_literal,),
                )
                for language, expected in family.reference_literals:
                    self.assertEqual(
                        wave48.W27.literal_texts(self.references[language][family.pk_coordinate]),
                        (expected,),
                    )

    def test_only_declared_records_change(self) -> None:
        for resource, before in self.before.items():
            with self.subTest(resource=resource):
                after = self.after[resource]
                self.assertEqual(set(before), set(after))
                changed = {coordinate for coordinate in before if before[coordinate].data != after[coordinate].data}
                expected = {change.coordinate for change in wave48.CHANGES if change.resource == resource}
                self.assertEqual(changed, expected)

    def test_exact_static_0143_removal_and_no_dynamic_tokens(self) -> None:
        for change in wave48.CHANGES:
            with self.subTest(change=(change.resource, change.coordinate)):
                before = self.before[change.resource][change.coordinate]
                after = self.after[change.resource][change.coordinate]
                expected = ((change.pin.removed_0143.offset, change.pin.removed_0143.value),)
                self.assertEqual(wave48.commands_0143(before), expected)
                self.assertEqual(wave48.commands_0143(after), ())
                self.assertEqual(wave48.opcodes_02xx(before), ())
                self.assertEqual(wave48.opcodes_02xx(after), ())
                self.assertNotIn(wave48.RUNTIME_SLOT, before.data)
                self.assertNotIn(wave48.RUNTIME_SLOT, after.data)
                self.assertEqual(wave48.span_hexes(before), change.input_opaque_spans_hex)
                self.assertEqual(wave48.span_hexes(after), change.target_opaque_spans_hex)
                self.assertTrue(before.data.endswith(wave48.W27.RECORD_TERMINATOR))
                self.assertTrue(after.data.endswith(wave48.W27.RECORD_TERMINATOR))

    def test_literal_marker_two_line_width_and_record_pins(self) -> None:
        advance, _font = wave48.W27.load_font_advance()
        for change in wave48.CHANGES:
            with self.subTest(change=(change.resource, change.coordinate)):
                before = self.before[change.resource][change.coordinate]
                after = self.after[change.resource][change.coordinate]
                self.assertEqual(wave48.W27.literal_texts(before), change.current_literals)
                self.assertEqual(wave48.W27.literal_texts(after), change.target_literals)
                self.assertEqual(wave48.W27.marker_topology(after), wave48.W27.marker_topology(before))
                layout = wave48.W27.line_layout(change.target_literals, advance)
                self.assertEqual(layout["line_count"], 2)
                self.assertLessEqual(layout["line_count"], wave48.MAX_LINES)
                self.assertLessEqual(layout["max_width_px"], wave48.MAX_LINE_PX)
                self.assertEqual(layout["wide_fallback_codepoints"], [])
                self.assertEqual(tuple(layout["line_widths_px"]), change.pin.target_line_widths_px)
                self.assertEqual(wave48.sha256_bytes(after.data), change.pin.target_sha256)
                self.assertEqual(len(after.data), change.pin.target_size)

    def test_packed_and_raw_target_profiles(self) -> None:
        for resource, packed in self.bundle.packed.items():
            with self.subTest(resource=resource):
                profile = wave48.TARGET_PROFILES[resource]
                self.assertEqual(len(packed), profile["size"])
                self.assertEqual(wave48.sha256_bytes(packed), profile["sha256"])
                self.assertEqual(len(self.bundle.raw[resource]), profile["raw_size"])
                self.assertEqual(wave48.sha256_bytes(self.bundle.raw[resource]), profile["raw_sha256"])

    def test_private_output_only_contract(self) -> None:
        with self.assertRaises(wave48.StaticUi0143Error):
            wave48.require_private(wave48.REPO, "repository")
        result = wave48.verify_private()
        self.assertEqual(result["changed_record_count"], 32)
        self.assertFalse(result["steam_game_resource_written"])
        manifest = self.bundle.manifest
        self.assertTrue(manifest["candidate_only"])
        self.assertEqual(manifest["steam_game_resource_write"], "absent")
        self.assertEqual(manifest["git_operation"], "not_implemented")
        self.assertEqual(manifest["network"], "not_implemented")
        self.assertEqual(manifest["release"], "not_implemented")


if __name__ == "__main__":
    unittest.main(verbosity=2)
