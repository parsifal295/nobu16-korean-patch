from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_dialogue_quality_wave38_dynamic_ui_v1.py"
SPEC = importlib.util.spec_from_file_location("wave38_dynamic_ui_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot import Wave 38 dynamic UI builder")
wave38 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave38
SPEC.loader.exec_module(wave38)


class Wave38DynamicUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave38.prepare_candidate()
        cls.before = {resource: wave38.W27.records_by_coordinate(path.read_bytes()) for resource, path in wave38.RESOURCE_PATHS.items()}
        cls.after = {resource: wave38.W27.records_by_coordinate(packed) for resource, packed in cls.bundle.packed.items()}

    def test_exact_runtime_shell_scope(self) -> None:
        self.assertEqual(len(wave38.CHANGES), 21)
        self.assertEqual(self.bundle.audit["changed_record_count"], 21)
        self.assertEqual(sum(change.resource == wave38.BASE_RESOURCE for change in wave38.CHANGES), 11)
        self.assertEqual(sum(change.resource == wave38.PK_RESOURCE for change in wave38.CHANGES), 10)

    def test_pc_only_source_contract(self) -> None:
        policy = self.bundle.audit["source_policy"]
        self.assertTrue(policy["pc_jp_en_sc_tc_only"])
        self.assertFalse(policy["switch_korean_read"])
        for path, _hash in wave38.W37.PC_SOURCES.values():
            self.assertNotIn("switch", str(path).casefold())

    def test_only_declared_records_change(self) -> None:
        for resource in wave38.RESOURCE_PATHS:
            with self.subTest(resource=resource):
                changed = {coordinate for coordinate in self.before[resource] if self.before[resource][coordinate].data != self.after[resource][coordinate].data}
                expected = {change.coordinate for change in wave38.CHANGES if change.resource == resource}
                self.assertEqual(changed, expected)
                self.assertEqual(set(self.before[resource]), set(self.after[resource]))

    def test_runtime_structure_and_shell_width_nonregression(self) -> None:
        advance, _font = wave38.W27.load_font_advance()
        for change in wave38.CHANGES:
            with self.subTest(change=change.name):
                before = self.before[change.resource][change.coordinate]
                after = self.after[change.resource][change.coordinate]
                self.assertEqual(wave38.W27.sha256_bytes(before.data), change.current_record_sha256)
                self.assertEqual(wave38.W27.sha256_bytes(after.data), change.target_record_sha256)
                self.assertEqual(len(after.data), change.target_record_size)
                self.assertEqual(wave38.W27.literal_texts(after), change.target_literals)
                self.assertEqual(wave38.W27.opaque_spans(after), wave38.W27.opaque_spans(before))
                self.assertEqual(wave38.W27.marker_topology(after), wave38.W27.marker_topology(before))
                self.assertFalse(wave38.W27.complete_0143_commands(wave38.W27.opaque_spans(before)))
                self.assertIn(change.runtime_opcode_hex.lower(), "".join(span.hex() for span in wave38.W27.opaque_spans(before)))
                current_layout = wave38.W27.line_layout(wave38.W27.literal_texts(before), advance)
                target_layout = wave38.W27.line_layout(change.target_literals, advance)
                self.assertEqual(tuple(target_layout["line_widths_px"]), change.target_line_widths_px)
                self.assertLessEqual(target_layout["line_count"], wave38.MAX_LINES)
                self.assertLessEqual(target_layout["max_width_px"], current_layout["max_width_px"])
                self.assertEqual(target_layout["wide_fallback_codepoints"], [])

    def test_pinned_target_profiles_and_private_guard(self) -> None:
        for resource, packed in self.bundle.packed.items():
            with self.subTest(resource=resource):
                target = wave38.TARGET_PROFILES[resource]
                self.assertEqual(len(packed), target["size"])
                self.assertEqual(wave38.sha256_bytes(packed), target["sha256"])
                self.assertEqual(len(self.bundle.raw[resource]), target["raw_size"])
                self.assertEqual(wave38.sha256_bytes(self.bundle.raw[resource]), target["raw_sha256"])
        with self.assertRaises(wave38.Wave38Error):
            wave38.require_private(wave38.REPO, "repository root")


if __name__ == "__main__":
    unittest.main(verbosity=2)
