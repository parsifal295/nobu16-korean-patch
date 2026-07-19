from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_event_quality_wave31_static_v1.py"
SPEC = importlib.util.spec_from_file_location("wave31_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot import Wave 31 builder")
wave31 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave31
SPEC.loader.exec_module(wave31)


class Wave31EventQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave31.prepare_candidate()

    def test_exact_four_paired_cell_scope(self) -> None:
        self.assertEqual(len(wave31.CHANGES), 8)
        self.assertEqual([change.entry_id for change in wave31.CHANGE_BY_RESOURCE["base"]], [3898, 4507, 5528, 6379])
        self.assertEqual([change.entry_id for change in wave31.CHANGE_BY_RESOURCE["pk"]], [3898, 4507, 5528, 6379])
        self.assertEqual(self.bundle.audit["changed_cell_count"], 8)

    def test_pc_only_sources_and_target_hashes_are_pinned(self) -> None:
        for change in wave31.CHANGES:
            self.assertEqual(
                set(change.source_utf16le_sha256),
                set(wave31.SOURCES[change.resource]),
            )
            self.assertEqual(wave31.text_hash(change.target), change.target_utf16le_sha256)
        for language_specs in wave31.SOURCES.values():
            for source in language_specs.values():
                self.assertNotIn("switch", str(source.path).casefold())

    def test_candidate_profile_and_only_declared_cells_change(self) -> None:
        for key, spec in wave31.RESOURCES.items():
            self.assertEqual(wave31.sha256_bytes(self.bundle.packed[key]), spec.target_sha256)
            self.assertEqual(len(self.bundle.packed[key]), spec.target_size)
            self.assertEqual(wave31.sha256_bytes(self.bundle.raw[key]), spec.target_raw_sha256)
            self.assertEqual(len(self.bundle.raw[key]), spec.target_raw_size)
            _header, decoded = wave31.decompress_wrapper(self.bundle.packed[key])
            table = wave31.parse_message_table(decoded)
            self.assertEqual(wave31.rebuild_message_table(table, table.texts), decoded)

    def test_every_target_preserves_controls_and_fits_three_lines(self) -> None:
        advance, _font = wave31.load_event_font()
        for change in wave31.CHANGES:
            with self.subTest(resource=change.resource, entry_id=change.entry_id):
                widths = wave31.line_widths(change.target, advance)
                self.assertEqual(widths, change.target_widths_px)
                self.assertLessEqual(len(widths), wave31.MAX_LINES)
                if change.resource == wave31.PK.key:
                    self.assertLessEqual(max(widths), wave31.PK_MAX_LINE_PX)
                self.assertEqual(wave31.protected_signature(change.target)["line_breaks"], ["\n", "\n"])

    def test_base_width_contract_is_not_assumed_from_pk(self) -> None:
        layout = self.bundle.audit["layout_validation"]
        self.assertEqual(layout["base"]["text_message_logical_size"], [448, 100])
        self.assertFalse(layout["base"]["renderer_width_bound_verified"])
        self.assertEqual(layout["pk"]["max_line_px"], 912)

    def test_private_output_guard_rejects_repository_root(self) -> None:
        with self.assertRaises(wave31.Wave31Error):
            wave31.require_private(wave31.REPO, "test")


if __name__ == "__main__":
    unittest.main(verbosity=2)
