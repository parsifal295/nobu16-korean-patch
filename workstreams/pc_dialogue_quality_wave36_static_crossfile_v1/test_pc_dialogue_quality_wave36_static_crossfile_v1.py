from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_dialogue_quality_wave36_static_crossfile_v1.py"
SPEC = importlib.util.spec_from_file_location("wave36_dialogue_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot import Wave 36 dialogue builder")
wave36 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave36
SPEC.loader.exec_module(wave36)


class Wave36DialogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave36.prepare_candidate()
        cls.before = {resource: wave36.W27.records_by_coordinate(path.read_bytes()) for resource, path in wave36.RESOURCE_PATHS.items()}
        cls.after = {resource: wave36.W27.records_by_coordinate(packed) for resource, packed in cls.bundle.packed.items()}

    def test_exact_static_scope(self) -> None:
        self.assertEqual(len(wave36.CHANGES), 3)
        self.assertEqual(self.bundle.audit["changed_record_count"], 3)
        self.assertEqual(self.bundle.manifest["changed_record_count"], 3)

    def test_pc_only_source_contract(self) -> None:
        self.assertEqual(set(wave36.PC_SOURCES), {"BASE_JP", "BASE_SC", "BASE_TC", "PK_JP", "PK_EN", "PK_SC", "PK_TC"})
        for path, _hash in wave36.PC_SOURCES.values():
            self.assertNotIn("switch", str(path).casefold())
        policy = self.bundle.audit["source_policy"]
        self.assertTrue(policy["pc_only_sources"])
        self.assertFalse(policy["switch_korean_read"])

    def test_only_declared_records_change(self) -> None:
        for resource in wave36.RESOURCE_PATHS:
            with self.subTest(resource=resource):
                changed = {coordinate for coordinate in self.before[resource] if self.before[resource][coordinate].data != self.after[resource][coordinate].data}
                expected = {change.coordinate for change in wave36.CHANGES if change.resource == resource}
                self.assertEqual(changed, expected)
                self.assertEqual(set(self.before[resource]), set(self.after[resource]))

    def test_record_structure_and_layout(self) -> None:
        advance, _font = wave36.W27.load_font_advance()
        for change in wave36.CHANGES:
            with self.subTest(change=change.name):
                before = self.before[change.resource][change.coordinate]
                after = self.after[change.resource][change.coordinate]
                self.assertEqual(wave36.W27.sha256_bytes(before.data), change.current_record_sha256)
                self.assertEqual(wave36.W27.sha256_bytes(after.data), change.target_record_sha256)
                self.assertEqual(len(after.data), change.target_record_size)
                self.assertEqual(wave36.W27.literal_texts(after), change.target_literals)
                self.assertEqual(wave36.W27.opaque_spans(after), wave36.W27.stripped_opaque_spans(before))
                layout = wave36.W27.line_layout(change.target_literals, advance)
                self.assertEqual(tuple(layout["line_widths_px"]), change.target_line_widths_px)
                self.assertLessEqual(layout["line_count"], wave36.MAX_LINES)
                self.assertLessEqual(layout["max_width_px"], wave36.MAX_LINE_PX)
                self.assertEqual(layout["wide_fallback_codepoints"], [])

    def test_pinned_target_profiles_and_private_guards(self) -> None:
        for resource, packed in self.bundle.packed.items():
            with self.subTest(resource=resource):
                target = wave36.TARGET_PROFILES[resource]
                self.assertEqual(len(packed), target["size"])
                self.assertEqual(wave36.sha256_bytes(packed), target["sha256"])
                self.assertEqual(len(self.bundle.raw[resource]), target["raw_size"])
                self.assertEqual(wave36.sha256_bytes(self.bundle.raw[resource]), target["raw_sha256"])
        with self.assertRaises(wave36.Wave36Error):
            wave36.require_private(wave36.REPO, "repository root")


if __name__ == "__main__":
    unittest.main(verbosity=2)
