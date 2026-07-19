from __future__ import annotations

import importlib.util
import sys
import unittest
from collections import Counter
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_dialogue_runtime_repair_wave46_v1.py"
SPEC = importlib.util.spec_from_file_location("wave46_runtime_repair_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot import Wave 46 runtime dialogue builder")
wave46 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave46
SPEC.loader.exec_module(wave46)


class Wave46RuntimeDialogueRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave46.prepare_candidate()
        cls.before = {
            resource: wave46.W27.records_by_coordinate(path.read_bytes())
            for resource, path in wave46.RESOURCE_PATHS.items()
        }
        cls.after = {
            resource: wave46.W27.records_by_coordinate(packed)
            for resource, packed in cls.bundle.packed.items()
        }

    def test_exact_three_family_six_record_scope(self) -> None:
        self.assertEqual(len(wave46.CHANGES), 6)
        self.assertEqual(
            {change.family for change in wave46.CHANGES},
            {"difficulty_with_caution", "difficulty_short", "castle_administration_runtime_slot"},
        )
        self.assertEqual(sum(change.resource == wave46.BASE_RESOURCE for change in wave46.CHANGES), 3)
        self.assertEqual(sum(change.resource == wave46.PK_RESOURCE for change in wave46.CHANGES), 3)

    def test_current_baseline_is_the_pinned_static_safe_profile(self) -> None:
        self.assertEqual(
            wave46.INPUT_PROFILES[wave46.BASE_RESOURCE]["sha256"],
            "F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB",
        )
        self.assertEqual(
            wave46.INPUT_PROFILES[wave46.PK_RESOURCE]["sha256"],
            "0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092",
        )

    def test_only_the_declared_records_change(self) -> None:
        for resource, before in self.before.items():
            with self.subTest(resource=resource):
                after = self.after[resource]
                self.assertEqual(set(before), set(after))
                changed = {coordinate for coordinate in before if before[coordinate].data != after[coordinate].data}
                expected = {change.coordinate for change in wave46.CHANGES if change.resource == resource}
                self.assertEqual(changed, expected)

    def test_literal_marker_lf_and_font_contracts(self) -> None:
        advance, _font = wave46.W27.load_font_advance()
        for change in wave46.CHANGES:
            with self.subTest(change=(change.resource, change.coordinate)):
                before = self.before[change.resource][change.coordinate]
                after = self.after[change.resource][change.coordinate]
                self.assertEqual(wave46.W27.literal_texts(after), change.target_literals)
                self.assertEqual(len(wave46.W27.literal_texts(after)), len(wave46.W27.literal_texts(before)))
                self.assertEqual(wave46.W27.marker_topology(after), wave46.W27.marker_topology(before))
                self.assertEqual("".join(wave46.W27.literal_texts(after)).count("\n"), "".join(wave46.W27.literal_texts(before)).count("\n"))
                layout = wave46.W27.line_layout(change.target_literals, advance)
                self.assertEqual(tuple(layout["line_widths_px"]), change.target_line_widths_px)
                self.assertLessEqual(layout["line_count"], wave46.MAX_LINES)
                self.assertLessEqual(layout["max_width_px"], wave46.MAX_LINE_PX)
                self.assertEqual(layout["wide_fallback_codepoints"], [])

    def test_exact_opaque_contracts_and_runtime_slot(self) -> None:
        for change in wave46.CHANGES:
            with self.subTest(change=(change.resource, change.coordinate)):
                before = self.before[change.resource][change.coordinate]
                after = self.after[change.resource][change.coordinate]
                self.assertEqual(wave46.span_hexes(before), change.input_opaque_spans_hex)
                self.assertEqual(wave46.span_hexes(after), change.target_opaque_spans_hex)
                self.assertEqual(wave46.opcodes_02xx(after), wave46.opcodes_02xx(before))
                removed_values = Counter(entry.value for entry in change.removed_0143)
                before_values = Counter(value for _offset, value in wave46.commands_0143(before))
                after_values = Counter(value for _offset, value in wave46.commands_0143(after))
                self.assertEqual(after_values, before_values - removed_values)
                for runtime_hex in change.preserved_runtime_opaque_hex:
                    runtime = bytes.fromhex(runtime_hex)
                    self.assertEqual(sum(span.count(runtime) for _offset, span in wave46.opaque_spans_with_offsets(before)), 1)
                    self.assertEqual(sum(span.count(runtime) for _offset, span in wave46.opaque_spans_with_offsets(after)), 1)
                self.assertTrue(after.data.endswith(wave46.W27.RECORD_TERMINATOR))

    def test_pinned_target_profiles_and_records(self) -> None:
        for resource, packed in self.bundle.packed.items():
            with self.subTest(resource=resource):
                profile = wave46.TARGET_PROFILES[resource]
                self.assertEqual(len(packed), profile["size"])
                self.assertEqual(wave46.sha256_bytes(packed), profile["sha256"])
                self.assertEqual(len(self.bundle.raw[resource]), profile["raw_size"])
                self.assertEqual(wave46.sha256_bytes(self.bundle.raw[resource]), profile["raw_sha256"])
        for change in wave46.CHANGES:
            with self.subTest(change=(change.resource, change.coordinate)):
                after = self.after[change.resource][change.coordinate]
                self.assertEqual(wave46.sha256_bytes(after.data), change.target_record_sha256)
                self.assertEqual(len(after.data), change.target_record_size)

    def test_private_output_guard_rejects_the_repository_root(self) -> None:
        with self.assertRaises(wave46.RuntimeRepairError):
            wave46.require_private(wave46.REPO, "repository")


if __name__ == "__main__":
    unittest.main(verbosity=2)
