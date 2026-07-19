from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_dialogue_quality_wave32_static_remainder_v1.py"
SPEC = importlib.util.spec_from_file_location("wave32_dialogue_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot import Wave 32 dialogue builder")
wave32 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave32
SPEC.loader.exec_module(wave32)


class Wave32DialogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave32.prepare_candidate()
        cls.before = wave32.W27.records_by_coordinate(wave32.RESOURCE_PATH.read_bytes())
        cls.after = wave32.W27.records_by_coordinate(cls.bundle.packed)

    def test_exact_static_scope(self) -> None:
        self.assertEqual(len(wave32.CHANGES), 16)
        self.assertEqual(len({change.pk_coordinate for change in wave32.CHANGES}), 16)
        self.assertEqual(self.bundle.audit["changed_record_count"], 16)

    def test_pc_only_source_contract(self) -> None:
        self.assertEqual(set(wave32.PC_SOURCES), {"BASE_JP", "PK_JP", "EN", "SC", "TC"})
        for path, _hash in wave32.PC_SOURCES.values():
            self.assertNotIn("switch", str(path).casefold())
        policy = self.bundle.audit["source_policy"]
        self.assertTrue(policy["pc_jp_en_sc_tc_only"])
        self.assertFalse(policy["switch_korean_read"])

    def test_only_declared_records_change(self) -> None:
        changed = {coordinate for coordinate in self.before if self.before[coordinate].data != self.after[coordinate].data}
        self.assertEqual(changed, {change.pk_coordinate for change in wave32.CHANGES})
        self.assertEqual(set(self.before), set(self.after))

    def test_record_structure_and_layout(self) -> None:
        advance, _font = wave32.W27.load_font_advance()
        for change in wave32.CHANGES:
            with self.subTest(change=change.name):
                before = self.before[change.pk_coordinate]
                after = self.after[change.pk_coordinate]
                self.assertEqual(wave32.W27.sha256_bytes(before.data), change.current_record_sha256)
                self.assertEqual(wave32.W27.sha256_bytes(after.data), change.target_record_sha256)
                self.assertEqual(len(after.data), change.target_record_size)
                self.assertEqual(wave32.W27.literal_texts(after), change.target_literals)
                self.assertEqual(wave32.W27.opaque_spans(after), wave32.W27.stripped_opaque_spans(before))
                self.assertFalse(wave32.W27.complete_0143_commands(wave32.W27.opaque_spans(after)))
                layout = wave32.W27.line_layout(change.target_literals, advance)
                self.assertEqual(tuple(layout["line_widths_px"]), change.target_line_widths_px)
                self.assertLessEqual(layout["line_count"], wave32.MAX_LINES)
                self.assertLessEqual(layout["max_width_px"], wave32.MAX_LINE_PX)
                self.assertEqual(layout["wide_fallback_codepoints"], [])

    def test_pinned_target_profile_and_private_guards(self) -> None:
        self.assertEqual(len(self.bundle.packed), wave32.TARGET_SIZE)
        self.assertEqual(wave32.sha256_bytes(self.bundle.packed), wave32.TARGET_SHA256)
        self.assertEqual(len(self.bundle.raw), wave32.TARGET_RAW_SIZE)
        self.assertEqual(wave32.sha256_bytes(self.bundle.raw), wave32.TARGET_RAW_SHA256)
        self.assertEqual(self.bundle.manifest["changed_record_count"], 16)
        with self.assertRaises(wave32.Wave32Error):
            wave32.require_private(wave32.REPO, "repository root")


if __name__ == "__main__":
    unittest.main(verbosity=2)
