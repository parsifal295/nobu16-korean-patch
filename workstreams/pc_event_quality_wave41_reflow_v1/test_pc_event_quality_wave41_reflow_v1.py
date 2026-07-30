from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_event_quality_wave41_reflow_v1.py"
SPEC = importlib.util.spec_from_file_location("wave41_reflow_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot import Wave 41 builder")
wave41 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave41
SPEC.loader.exec_module(wave41)


class Wave41ReflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave41.prepare_candidate()
        cls.current, _sources = wave41.W40.load_tables()
        _header, raw = wave41.W31.decompress_wrapper(cls.bundle.packed)
        cls.after = wave41.W31.parse_message_table(raw)

    def test_exact_scope_and_qa_hold(self) -> None:
        self.assertEqual(len(wave41.CHANGES), 6)
        self.assertEqual(self.bundle.audit["changed_cell_count"], 6)
        self.assertEqual(self.bundle.audit["real_game_display_qa_required_ids"], [5558, 5832, 7083, 7579, 7801, 7845])

    def test_only_declared_cells_change(self) -> None:
        before = self.current["pk"].table.texts
        changed = [index for index, (left, right) in enumerate(zip(before, self.after.texts)) if left != right]
        self.assertEqual(changed, [change.entry_id for change in wave41.CHANGES])

    def test_whitespace_only_and_layout_bounds(self) -> None:
        advance, _font = wave41.W31.load_event_font()
        for change in wave41.CHANGES:
            with self.subTest(change=change.entry_id):
                before = self.current["pk"].table.texts[change.entry_id]
                after = self.after.texts[change.entry_id]
                self.assertEqual(wave41.W31.protected_nonlayout_signature(before), wave41.W31.protected_nonlayout_signature(after))
                self.assertEqual(wave41.WHITESPACE_RE.sub("", before), wave41.WHITESPACE_RE.sub("", after))
                widths = wave41.W31.line_widths(after, advance)
                self.assertEqual(widths, change.target_line_widths_px)
                self.assertLessEqual(len(widths), 3)
                self.assertLessEqual(max(widths), wave41.PK_MAX_LINE_PX)

    def test_profile_and_private_guard(self) -> None:
        self.assertEqual(len(self.bundle.packed), wave41.TARGET_PROFILE["size"])
        self.assertEqual(wave41.W31.sha256_bytes(self.bundle.packed), wave41.TARGET_PROFILE["sha256"])
        self.assertEqual(len(self.bundle.raw), wave41.TARGET_PROFILE["raw_size"])
        self.assertEqual(wave41.W31.sha256_bytes(self.bundle.raw), wave41.TARGET_PROFILE["raw_sha256"])
        with self.assertRaises(wave41.Wave41Error):
            wave41.require_private(wave41.REPO, "repo")


if __name__ == "__main__":
    unittest.main(verbosity=2)
