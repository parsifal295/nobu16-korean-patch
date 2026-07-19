from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_dialogue_quality_wave35_static_command_v1.py"
SPEC = importlib.util.spec_from_file_location("wave35_dialogue_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot import Wave 35 dialogue builder")
wave35 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave35
SPEC.loader.exec_module(wave35)


class Wave35DialogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave35.prepare_candidate()
        cls.before = wave35.W27.records_by_coordinate(wave35.RESOURCE_PATH.read_bytes())
        cls.after = wave35.W27.records_by_coordinate(cls.bundle.packed)

    def test_exact_static_scope(self) -> None:
        self.assertEqual(self.bundle.audit["changed_record_count"], 1)
        self.assertEqual(self.bundle.manifest["changed_record_count"], 1)

    def test_pc_only_source_contract(self) -> None:
        self.assertEqual(set(wave35.PC_SOURCES), {"PK_JP", "EN", "SC", "TC"})
        for path, _hash in wave35.PC_SOURCES.values():
            self.assertNotIn("switch", str(path).casefold())
        policy = self.bundle.audit["source_policy"]
        self.assertTrue(policy["pc_jp_en_sc_tc_only"])
        self.assertFalse(policy["switch_korean_read"])

    def test_only_declared_record_changes(self) -> None:
        changed = {coordinate for coordinate in self.before if self.before[coordinate].data != self.after[coordinate].data}
        self.assertEqual(changed, {wave35.CHANGE.coordinate})
        self.assertEqual(set(self.before), set(self.after))

    def test_record_structure_and_layout(self) -> None:
        advance, _font = wave35.W27.load_font_advance()
        before = self.before[wave35.CHANGE.coordinate]
        after = self.after[wave35.CHANGE.coordinate]
        self.assertEqual(wave35.W27.sha256_bytes(before.data), wave35.CHANGE.current_record_sha256)
        self.assertEqual(wave35.W27.sha256_bytes(after.data), wave35.CHANGE.target_record_sha256)
        self.assertEqual(len(after.data), wave35.CHANGE.target_record_size)
        self.assertEqual(wave35.W27.literal_texts(after), wave35.CHANGE.target_literals)
        self.assertEqual(wave35.W27.opaque_spans(after), wave35.W27.stripped_opaque_spans(before))
        layout = wave35.W27.line_layout(wave35.CHANGE.target_literals, advance)
        self.assertEqual(tuple(layout["line_widths_px"]), wave35.CHANGE.target_line_widths_px)
        self.assertLessEqual(layout["line_count"], wave35.MAX_LINES)
        self.assertLessEqual(layout["max_width_px"], wave35.MAX_LINE_PX)
        self.assertEqual(layout["wide_fallback_codepoints"], [])

    def test_pinned_target_profile_and_private_guards(self) -> None:
        self.assertEqual(len(self.bundle.packed), wave35.TARGET_SIZE)
        self.assertEqual(wave35.sha256_bytes(self.bundle.packed), wave35.TARGET_SHA256)
        self.assertEqual(len(self.bundle.raw), wave35.TARGET_RAW_SIZE)
        self.assertEqual(wave35.sha256_bytes(self.bundle.raw), wave35.TARGET_RAW_SHA256)
        with self.assertRaises(wave35.Wave35Error):
            wave35.require_private(wave35.REPO, "repository root")


if __name__ == "__main__":
    unittest.main(verbosity=2)
