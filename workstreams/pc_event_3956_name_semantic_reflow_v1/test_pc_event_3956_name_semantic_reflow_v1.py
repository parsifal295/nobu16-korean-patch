from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_event_3956_name_semantic_reflow_v1.py"
SPEC = importlib.util.spec_from_file_location("pc_event_3956_name_semantic_reflow_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot import PC event 3956 candidate builder")
wave = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave
SPEC.loader.exec_module(wave)


class Event3956NameSemanticReflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave.prepare_candidate()
        cls.before = wave.load_w45()
        header, raw = wave.decompress_wrapper(cls.bundle.packed)
        cls.after_header = header
        cls.after_raw = raw
        cls.after = wave.parse_message_table(raw)
        cls.width = wave.load_width_utility()

    def test_source_baseline_hashes_and_record_count_are_pinned(self) -> None:
        self.assertEqual(len(self.before.packed), wave.W45_INPUT_PROFILE.size)
        self.assertEqual(wave.sha256_bytes(self.before.packed), wave.W45_INPUT_PROFILE.sha256)
        self.assertEqual(len(self.before.raw), wave.W45_INPUT_PROFILE.raw_size)
        self.assertEqual(wave.sha256_bytes(self.before.raw), wave.W45_INPUT_PROFILE.raw_sha256)
        self.assertEqual(len(self.before.table.texts), wave.INPUT_RECORD_COUNT)
        self.assertEqual(wave.text_hash(self.before.table.texts[wave.EVENT_ID]), wave.CURRENT_UTF16LE_SHA256)

    def test_exact_one_record_scope_and_literal_target(self) -> None:
        changed = [
            entry_id
            for entry_id, (source, candidate) in enumerate(zip(self.before.table.texts, self.after.texts))
            if source != candidate
        ]
        self.assertEqual(changed, [3956])
        self.assertEqual(self.bundle.audit["changed_ids"], [3956])
        self.assertEqual(self.bundle.audit["changed_record_count"], 1)
        self.assertEqual(self.after.texts[3956], wave.TARGET)
        self.assertEqual(wave.text_hash(self.after.texts[3956]), wave.TARGET_UTF16LE_SHA256)

    def test_original_target_control_tag_runtime_signature_is_identical(self) -> None:
        before = self.before.table.texts[3956]
        after = self.after.texts[3956]
        self.assertEqual(
            wave.control_tag_runtime_signature(self.width, before),
            wave.control_tag_runtime_signature(self.width, after),
        )
        wave.assert_no_linebreak_inside_color_span(after)
        self.assertTrue(self.bundle.audit["records"][0]["control_tag_runtime_signature_identical"])
        self.assertFalse(self.bundle.audit["records"][0]["manual_lf_inside_color_tag_span"])

    def test_actual_pc_event_font_three_line_width_contract(self) -> None:
        advance, _font = self.width.load_event_font()
        widths = self.width.line_widths(self.after.texts[3956], advance)
        self.assertEqual(widths, (840, 912, 912))
        self.assertEqual(widths, wave.TARGET_LINE_WIDTHS_PX)
        self.assertEqual(len(widths), 3)
        self.assertLessEqual(max(widths), 912)

    def test_lz4_and_message_table_round_trip(self) -> None:
        self.assertEqual(wave.rebuild_message_table(self.after, self.after.texts), self.after_raw)
        self.assertEqual(wave.recompress_wrapper(self.after_raw, self.after_header), self.bundle.packed)
        self.assertEqual(len(self.bundle.packed), wave.TARGET_PROFILE.size)
        self.assertEqual(wave.sha256_bytes(self.bundle.packed), wave.TARGET_PROFILE.sha256)
        self.assertEqual(len(self.bundle.raw), wave.TARGET_PROFILE.raw_size)
        self.assertEqual(wave.sha256_bytes(self.bundle.raw), wave.TARGET_PROFILE.raw_sha256)

    def test_semantic_compaction_preserves_required_content(self) -> None:
        self.assertNotIn("단숨에", wave.TARGET)
        for token in wave.SEMANTIC_RETENTION_TOKENS:
            with self.subTest(token=token):
                self.assertIn(token, wave.TARGET)
        semantic = self.bundle.audit["records"][0]["semantic_compaction"]
        self.assertEqual(semantic["omitted_lexeme_only"], "단숨에")
        self.assertEqual(semantic["retained"], ["몰래", "자객", "암살", "급습", "일족 30여 명", "숙청"])

    def test_private_output_guard_and_manifest(self) -> None:
        self.assertEqual(
            self.bundle.manifest["audit_sha256"],
            wave.sha256_bytes(wave.canonical_json(self.bundle.audit)),
        )
        self.assertEqual(self.bundle.manifest["resource"]["changed_ids"], [3956])
        self.assertEqual(self.bundle.manifest["steam_game_resource_write"], "absent")
        with self.assertRaises(wave.Event3956CandidateError):
            wave.require_private(wave.REPO, "repository")


if __name__ == "__main__":
    unittest.main(verbosity=2)
