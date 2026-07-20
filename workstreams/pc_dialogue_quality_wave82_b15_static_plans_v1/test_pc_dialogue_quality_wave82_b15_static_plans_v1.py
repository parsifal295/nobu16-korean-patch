from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_dialogue_quality_wave82_b15_static_plans_v1.py"
SPEC = importlib.util.spec_from_file_location("wave82_dialogue_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot import Wave 82 dialogue builder")
wave82 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave82
SPEC.loader.exec_module(wave82)


class Wave82DialogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave82.prepare_candidate()
        cls.before = wave82.W27.records_by_coordinate(wave82.RESOURCE_PATH.read_bytes())
        cls.after = wave82.W27.records_by_coordinate(cls.bundle.packed)

    def test_exact_static_scope(self) -> None:
        self.assertEqual(self.bundle.audit["changed_record_count"], 2)
        self.assertEqual(self.bundle.manifest["changed_record_count"], 2)
        self.assertEqual({row["coordinate"] for row in self.bundle.audit["records"]}, {"15:259", "15:261"})

    def test_pc_only_source_contract(self) -> None:
        self.assertEqual(set(wave82.PC_SOURCES), {"PK_JP", "EN", "SC", "TC"})
        for path, _hash in wave82.PC_SOURCES.values():
            self.assertNotIn("switch", str(path).casefold())
        policy = self.bundle.audit["source_policy"]
        self.assertTrue(policy["pc_jp_en_sc_tc_only"])
        self.assertFalse(policy["switch_korean_read"])
        self.assertFalse(policy["steam_game_resource_written"])

    def test_only_declared_records_change(self) -> None:
        target_coordinates = {change.coordinate for change in wave82.CHANGES}
        changed = {coordinate for coordinate in self.before if self.before[coordinate].data != self.after[coordinate].data}
        self.assertEqual(changed, target_coordinates)
        self.assertEqual(set(self.before), set(self.after))
        for coordinate, record in self.before.items():
            if coordinate not in target_coordinates:
                self.assertEqual(record.data, self.after[coordinate].data, coordinate)

    def test_structure_and_static_0143_proof(self) -> None:
        advance, _font = wave82.W27.load_font_advance()
        for change in wave82.CHANGES:
            before = self.before[change.coordinate]
            after = self.after[change.coordinate]
            self.assertEqual(wave82.W27.sha256_bytes(before.data), change.current_record_sha256)
            self.assertEqual(len(before.data), change.current_record_size)
            self.assertEqual(wave82.W27.sha256_bytes(after.data), change.target_record_sha256)
            self.assertEqual(len(after.data), change.target_record_size)
            self.assertEqual(wave82.W27.literal_texts(after), change.target_literals)
            self.assertEqual(tuple(span.hex().upper() for span in wave82.W27.opaque_spans(before)), change.input_opaque_spans_hex)
            self.assertEqual(wave82.W27.complete_0143_commands(wave82.W27.opaque_spans(before)), change.static_0143_commands)
            self.assertNotIn("014301000000", change.static_0143_commands)
            self.assertEqual(wave82.W27.opaque_spans(after), wave82.W27.stripped_opaque_spans(before))
            self.assertEqual(tuple(span.hex().upper() for span in wave82.W27.opaque_spans(after)), ("", "", "", "050505"))
            self.assertEqual(wave82.W27.complete_0143_commands(wave82.W27.opaque_spans(after)), ())
            self.assertEqual(wave82.W27.marker_topology(after), wave82.W27.marker_topology(before))
            self.assertTrue(after.data.endswith(wave82.W27.RECORD_TERMINATOR))
            layout = wave82.W27.line_layout(change.target_literals, advance)
            self.assertEqual(tuple(layout["line_widths_px"]), change.target_line_widths_px)
            self.assertLessEqual(layout["line_count"], wave82.MAX_LINES)
            self.assertLessEqual(layout["max_width_px"], wave82.MAX_LINE_PX)
            self.assertEqual(layout["wide_fallback_codepoints"], [])

    def test_pinned_profile_and_private_guards(self) -> None:
        self.assertEqual(len(self.bundle.packed), wave82.TARGET_SIZE)
        self.assertEqual(wave82.sha256_bytes(self.bundle.packed), wave82.TARGET_SHA256)
        self.assertEqual(len(self.bundle.raw), wave82.TARGET_RAW_SIZE)
        self.assertEqual(wave82.sha256_bytes(self.bundle.raw), wave82.TARGET_RAW_SHA256)
        with self.assertRaises(wave82.Wave82Error):
            wave82.require_private(wave82.REPO, "repository root")


if __name__ == "__main__":
    unittest.main(verbosity=2)
