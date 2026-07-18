from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_battle_dialogue_static_quality_wave47_v1.py"
SPEC = importlib.util.spec_from_file_location("wave47_battle_dialogue_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot import Wave 47 battle-dialogue builder")
wave47 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave47
SPEC.loader.exec_module(wave47)


class Wave47BattleDialogueStaticQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packed, cls.raw, cls.audit, cls.manifest = wave47.prepare_candidate()
        cls.before = wave47.records_by_coordinate(wave47.RESOURCE_PATH.read_bytes())
        cls.after = wave47.records_by_coordinate(cls.packed)

    def test_scope_is_safe_subset_of_reviewed_block_17_findings(self) -> None:
        self.assertEqual(len(wave47.CHANGES), 34)
        self.assertEqual(len(wave47.REVIEWED_CHANGES), 65)
        self.assertEqual(len(wave47.DISPLAY_QA_HOLDS), 31)
        self.assertEqual(
            {change.coordinate for change in wave47.CHANGES}
            | wave47.DISPLAY_QA_HOLDS,
            {change.coordinate for change in wave47.REVIEWED_CHANGES},
        )
        self.assertFalse({change.coordinate for change in wave47.CHANGES} & wave47.DISPLAY_QA_HOLDS)
        self.assertTrue(all(change.coordinate[0] == 17 for change in wave47.CHANGES))

    def test_only_declared_safe_records_change(self) -> None:
        self.assertEqual(set(self.before), set(self.after))
        changed = {coordinate for coordinate in self.before if self.before[coordinate].data != self.after[coordinate].data}
        self.assertEqual(changed, {change.coordinate for change in wave47.CHANGES})

    def test_static_marker_opaque_lf_and_font_contracts(self) -> None:
        advance, _font = wave47.W27.load_font_advance()
        for change in wave47.CHANGES:
            with self.subTest(coordinate=change.coordinate_text):
                before = self.before[change.coordinate]
                after = self.after[change.coordinate]
                self.assertEqual(wave47.W27.literal_texts(after), change.target_literals)
                self.assertEqual(len(wave47.W27.literal_texts(after)), len(wave47.W27.literal_texts(before)))
                self.assertEqual(wave47.W27.marker_topology(after), wave47.W27.marker_topology(before))
                self.assertEqual(wave47.W27.opaque_spans(after), wave47.W27.opaque_spans(before))
                self.assertEqual(wave47.runtime_opcodes(before), ())
                self.assertFalse(wave47.W27.complete_0143_commands(wave47.W27.opaque_spans(before)))
                self.assertEqual("".join(wave47.W27.literal_texts(after)).count("\n"), "".join(wave47.W27.literal_texts(before)).count("\n"))
                layout = wave47.W27.line_layout(change.target_literals, advance)
                self.assertLessEqual(layout["line_count"], wave47.MAX_LINES)
                self.assertLessEqual(layout["max_width_px"], wave47.MAX_LINE_PX)
                self.assertEqual(layout["wide_fallback_codepoints"], [])

    def test_pc_japanese_and_target_record_pins(self) -> None:
        pc_jp = wave47.records_by_coordinate(wave47.PC_JP_SOURCE.read_bytes())
        for change in wave47.CHANGES:
            with self.subTest(coordinate=change.coordinate_text):
                pin = wave47.RECORD_PINS[change.coordinate]
                self.assertEqual(wave47.sha256_bytes(self.before[change.coordinate].data), pin.current_sha256)
                self.assertEqual(len(self.before[change.coordinate].data), pin.current_size)
                self.assertEqual(wave47.sha256_bytes(pc_jp[change.coordinate].data), pin.pc_jp_sha256)
                self.assertEqual(wave47.sha256_bytes(self.after[change.coordinate].data), pin.target_sha256)
                self.assertEqual(len(self.after[change.coordinate].data), pin.target_size)

    def test_packed_and_raw_output_profiles_are_pinned(self) -> None:
        self.assertEqual(len(self.packed), wave47.TARGET_PROFILE["size"])
        self.assertEqual(wave47.sha256_bytes(self.packed), wave47.TARGET_PROFILE["sha256"])
        self.assertEqual(len(self.raw), wave47.TARGET_PROFILE["raw_size"])
        self.assertEqual(wave47.sha256_bytes(self.raw), wave47.TARGET_PROFILE["raw_sha256"])
        self.assertEqual(self.audit["changed_record_count"], 34)
        self.assertEqual(self.manifest["steam_game_resource_write"], "absent")

    def test_private_output_guard_rejects_repository_root(self) -> None:
        with self.assertRaises(wave47.Wave47Error):
            wave47.require_private(wave47.REPO, "repository")


if __name__ == "__main__":
    unittest.main(verbosity=2)
