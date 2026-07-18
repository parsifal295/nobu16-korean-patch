from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_event_quality_wave33_strict_static_v1.py"
SPEC = importlib.util.spec_from_file_location("wave33_event_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot import Wave 33 event builder")
wave33 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave33
SPEC.loader.exec_module(wave33)


class Wave33EventTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave33.prepare_candidate()

    def test_exact_pair_and_cell_scope(self) -> None:
        self.assertEqual(len(wave33.PAIRS), 13)
        self.assertEqual(len(wave33.CHANGES), 26)
        self.assertEqual(len({(change.resource, change.entry_id) for change in wave33.CHANGES}), 26)
        self.assertEqual(self.bundle.audit["changed_cell_count"], 26)

    def test_pc_only_sources_and_paired_japanese_anchors(self) -> None:
        for source_specs in wave33.SOURCES.values():
            for source in source_specs.values():
                self.assertNotIn("switch", str(source.path).casefold())
        for row in self.bundle.audit["records"]:
            anchor = row["source_anchor"]
            self.assertTrue(anchor["paired_jp_utf16le_sha256"])
            self.assertIn("JP", anchor["cell_utf16le_sha256"])
        policy = self.bundle.audit["source_policy"]
        self.assertTrue(policy["pc_jp_en_sc_tc_only"])
        self.assertFalse(policy["switch_korean_read"])

    def test_targets_preserve_controls_and_apply_supported_layout_checks(self) -> None:
        advance, _font = wave33.load_event_font()
        for change in wave33.CHANGES:
            with self.subTest(resource=change.resource, entry_id=change.entry_id):
                widths = wave33.line_widths(change.target, advance)
                self.assertEqual(widths, change.target_widths_px)
                self.assertLessEqual(len(widths), wave33.MAX_LINES)
                if change.resource == wave33.PK.key:
                    self.assertLessEqual(max(widths), wave33.PK_MAX_LINE_PX)
                self.assertEqual(tuple(wave33.protected_signature(change.target)["line_breaks"]), ("\n",) * (len(widths) - 1))

    def test_pinned_target_profile_and_private_guard(self) -> None:
        for key, spec in wave33.RESOURCES.items():
            with self.subTest(resource=key):
                self.assertEqual(wave33.sha256_bytes(self.bundle.packed[key]), spec.target_sha256)
                self.assertEqual(len(self.bundle.packed[key]), spec.target_size)
                self.assertEqual(wave33.sha256_bytes(self.bundle.raw[key]), spec.target_raw_sha256)
                self.assertEqual(len(self.bundle.raw[key]), spec.target_raw_size)
        self.assertEqual(self.bundle.manifest["changed_cell_count"], 26)
        self.assertEqual(self.bundle.audit["base_real_game_qa_required_ids"], [6772, 6941, 8776, 8803, 8947, 9292])
        self.assertEqual(self.bundle.audit["layout_validation"]["base"]["text_message_logical_size"], [448, 100])
        self.assertFalse(self.bundle.audit["layout_validation"]["base"]["renderer_width_bound_verified"])
        self.assertEqual(self.bundle.audit["layout_validation"]["pk"]["max_line_px"], 912)
        with self.assertRaises(wave33.Wave33Error):
            wave33.require_private(wave33.REPO, "repository root")


if __name__ == "__main__":
    unittest.main(verbosity=2)
