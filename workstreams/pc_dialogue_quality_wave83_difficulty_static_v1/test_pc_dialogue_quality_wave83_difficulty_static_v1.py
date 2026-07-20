from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_dialogue_quality_wave83_difficulty_static_v1.py"
SPEC = importlib.util.spec_from_file_location("wave83_dialogue_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot import Wave 83 dialogue builder")
wave83 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave83
SPEC.loader.exec_module(wave83)


class Wave83DialogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave83.prepare_candidate()
        cls.before = wave83.load_predecessors()[1]
        cls.after = {resource: wave83.W27.records_by_coordinate(packed) for resource, packed in cls.bundle.packed.items()}

    def test_exact_four_record_scope(self) -> None:
        self.assertEqual(self.bundle.audit["changed_record_count"], 4)
        self.assertEqual(self.bundle.manifest["changed_record_count"], 4)
        self.assertEqual(
            {(row["resource"], row["coordinate"]) for row in self.bundle.audit["records"]},
            {
                (wave83.BASE_RESOURCE, "15:220"),
                (wave83.BASE_RESOURCE, "15:270"),
                (wave83.PK_RESOURCE, "15:223"),
                (wave83.PK_RESOURCE, "15:273"),
            },
        )

    def test_w82_is_the_strict_pk_predecessor(self) -> None:
        self.assertEqual(wave83.INPUT_PROFILES[wave83.PK_RESOURCE]["kind"], "wave82_private_candidate")
        self.assertEqual(wave83.sha256_path(wave83.W82_PK_PATH), wave83.INPUT_PROFILES[wave83.PK_RESOURCE]["sha256"])
        evidence = wave83.validate_w82_evidence()
        self.assertEqual(set(evidence), {"audit.v1.json", "build_manifest.v1.json"})
        self.assertEqual(self.bundle.audit["predecessors"][wave83.PK_RESOURCE]["sha256"], wave83.INPUT_PROFILES[wave83.PK_RESOURCE]["sha256"])

    def test_pc_only_source_contract(self) -> None:
        self.assertEqual(set(wave83.PC_SOURCES), {"BASE_JP", "PK_JP", "EN", "SC", "TC"})
        for path, _hash in wave83.PC_SOURCES.values():
            self.assertNotIn("switch", str(path).casefold())
        policy = self.bundle.audit["source_policy"]
        self.assertTrue(policy["pc_jp_en_sc_tc_only"])
        self.assertFalse(policy["switch_korean_read"])
        self.assertFalse(policy["steam_game_resource_written"])

    def test_only_declared_records_change(self) -> None:
        for resource, before in self.before.items():
            after = self.after[resource]
            expected = {change.coordinate for change in wave83.CHANGES if change.resource == resource}
            changed = {coordinate for coordinate in before if before[coordinate].data != after[coordinate].data}
            self.assertEqual(changed, expected, resource)
            self.assertEqual(set(before), set(after), resource)
            for coordinate, record in before.items():
                if coordinate not in expected:
                    self.assertEqual(record.data, after[coordinate].data, (resource, coordinate))

    def test_layout_marker_and_static_0143_contracts(self) -> None:
        advance, _font = wave83.W27.load_font_advance()
        for change in wave83.CHANGES:
            before = self.before[change.resource][change.coordinate]
            after = self.after[change.resource][change.coordinate]
            self.assertEqual(wave83.W27.sha256_bytes(before.data), change.current_record_sha256)
            self.assertEqual(wave83.W27.sha256_bytes(after.data), change.target_record_sha256)
            self.assertEqual(wave83.W27.literal_texts(after), change.target_literals)
            self.assertEqual(wave83.W27.marker_topology(after), wave83.W27.marker_topology(before))
            self.assertEqual(tuple(span.hex().upper() for span in wave83.W27.opaque_spans(before)), change.input_opaque_spans_hex)
            self.assertEqual(wave83.W27.complete_0143_commands(wave83.W27.opaque_spans(before)), change.static_0143_commands)
            self.assertNotIn("014301000000", change.static_0143_commands)
            self.assertEqual(wave83.opaque_02xx_prefixes(before), ())
            self.assertEqual(wave83.W27.opaque_spans(after), wave83.W27.stripped_opaque_spans(before))
            self.assertEqual(wave83.W27.complete_0143_commands(wave83.W27.opaque_spans(after)), ())
            self.assertEqual(wave83.opaque_02xx_prefixes(after), ())
            self.assertTrue(after.data.endswith(wave83.W27.RECORD_TERMINATOR))
            layout = wave83.W27.line_layout(change.target_literals, advance)
            self.assertEqual(tuple(layout["line_widths_px"]), change.target_line_widths_px)
            self.assertLessEqual(layout["line_count"], wave83.MAX_LINES)
            self.assertLessEqual(layout["max_width_px"], wave83.MAX_LINE_PX)
            self.assertEqual(layout["wide_fallback_codepoints"], [])

    def test_pinned_targets_and_private_guard(self) -> None:
        for resource, packed in self.bundle.packed.items():
            profile = wave83.TARGET_PROFILES[resource]
            self.assertEqual(len(packed), profile["size"])
            self.assertEqual(wave83.sha256_bytes(packed), profile["sha256"])
            self.assertEqual(len(self.bundle.raw[resource]), profile["raw_size"])
            self.assertEqual(wave83.sha256_bytes(self.bundle.raw[resource]), profile["raw_sha256"])
        with self.assertRaises(wave83.Wave83Error):
            wave83.require_private(wave83.REPO, "repository root")


if __name__ == "__main__":
    unittest.main(verbosity=2)
