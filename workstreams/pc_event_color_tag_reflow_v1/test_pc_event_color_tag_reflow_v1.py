from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_event_color_tag_reflow_v1.py"
SPEC = importlib.util.spec_from_file_location("pc_event_color_tag_reflow_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot import PC event color-tag reflow builder")
wave = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave
SPEC.loader.exec_module(wave)


EXPECTED_IDS = [3237, 3477, 3832, 3896, 3919, 4011, 4020]
EXPECTED_WIDTHS = {
    3237: (672, 888, 600),
    3477: (600, 816, 168),
    3832: (432, 456, 504),
    3896: (720, 480, 768),
    3919: (696, 480, 912),
    4011: (504, 432, 768),
    4020: (408, 720, 912),
}


class ColorTagReflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave.prepare_candidate()
        cls.before = wave.load_table(
            wave.STEAM_PK_EVENT,
            wave.W45_INPUT_PROFILE,
            wave.INPUT_RECORD_COUNT,
            "W45 Steam PC PK event input",
            require_packed_round_trip=True,
        )
        _header, raw = wave.decompress_wrapper(cls.bundle.packed)
        cls.after = wave.parse_message_table(raw)

    def test_exact_scope_and_holds(self) -> None:
        self.assertEqual([change.entry_id for change in wave.CHANGES], EXPECTED_IDS)
        self.assertEqual(len(wave.CHANGES), 7)
        self.assertEqual(wave.HARD_HOLD_IDS, (3202, 3900, 3934, 4140, 8723, 9359, 10045))
        self.assertEqual(wave.SEMANTIC_HOLD_IDS, (8510,))
        self.assertTrue(set(EXPECTED_IDS).isdisjoint(wave.HARD_HOLD_IDS))
        self.assertTrue(set(EXPECTED_IDS).isdisjoint(wave.SEMANTIC_HOLD_IDS))
        self.assertEqual(self.bundle.audit["changed_ids"], EXPECTED_IDS)
        self.assertEqual(self.bundle.audit["hard_holds"], list(wave.HARD_HOLD_IDS))
        self.assertEqual(self.bundle.audit["semantic_holds"], [8510])

    def test_w49_static_candidate_overlap_is_rejected(self) -> None:
        w49_ids = wave.load_w49_static_ids()
        self.assertTrue(set(EXPECTED_IDS).isdisjoint(w49_ids))
        self.assertEqual(self.bundle.audit["w49_static_overlap_guard"]["overlap"], [])
        self.assertEqual(
            self.bundle.audit["w49_static_overlap_guard"]["declared_ids_sha256"],
            wave.W49_STATIC_IDS_SHA256,
        )

    def test_only_declared_records_change(self) -> None:
        changed = [
            index
            for index, (before, after) in enumerate(zip(self.before.table.texts, self.after.texts))
            if before != after
        ]
        self.assertEqual(changed, EXPECTED_IDS)
        for held_id in (*wave.HARD_HOLD_IDS, *wave.SEMANTIC_HOLD_IDS):
            with self.subTest(held_id=held_id):
                self.assertEqual(self.before.table.texts[held_id], self.after.texts[held_id])

    def test_controls_outer_whitespace_and_non_whitespace_are_immutable(self) -> None:
        width = wave.load_width_utility()
        for change in wave.CHANGES:
            with self.subTest(entry_id=change.entry_id):
                before = self.before.table.texts[change.entry_id]
                after = self.after.texts[change.entry_id]
                self.assertEqual(wave.text_hash(before), change.current_utf16le_sha256)
                self.assertEqual(wave.text_hash(after), change.target_utf16le_sha256)
                self.assertEqual(
                    width.protected_nonlayout_signature(before),
                    width.protected_nonlayout_signature(after),
                )
                self.assertEqual(
                    wave.layout_whitespace_stripped(before),
                    wave.layout_whitespace_stripped(after),
                )
                self.assertNotIn("\r", before)
                self.assertNotIn("\r", after)

    def test_actual_font_three_line_912px_contract(self) -> None:
        width = wave.load_width_utility()
        advance, font = width.load_event_font()
        self.assertEqual(dict(font), wave.FONT_EVIDENCE)
        for change in wave.CHANGES:
            with self.subTest(entry_id=change.entry_id):
                widths = width.line_widths(self.after.texts[change.entry_id], advance)
                self.assertEqual(widths, EXPECTED_WIDTHS[change.entry_id])
                self.assertEqual(widths, change.target_line_widths_px)
                self.assertEqual(len(widths), 3)
                self.assertLessEqual(max(widths), wave.PK_MAX_LINE_PX)

    def test_pc_jp_recheck_and_context_evidence_are_bound(self) -> None:
        records = {record["id"]: record for record in self.bundle.audit["records"]}
        self.assertEqual(set(records), set(EXPECTED_IDS))
        source_evidence = self.bundle.audit["pc_source_evidence"]
        self.assertEqual(source_evidence["JP"]["sha256"], wave.PC_SOURCE_SPECS["JP"].profile.sha256)
        self.assertEqual(source_evidence["JP"]["role"], "reading_and_natural_clause_boundary_review")
        for language in ("EN", "SC", "TC"):
            self.assertEqual(source_evidence[language]["role"], "context_evidence_only")
        for change in wave.CHANGES:
            with self.subTest(entry_id=change.entry_id):
                record = records[change.entry_id]
                self.assertEqual(record["pc_source_utf16le_sha256"], dict(change.pc_source_utf16le_sha256))
                self.assertEqual(record["pc_jp_anchors"], list(change.pc_jp_anchors))
                self.assertTrue(record["target_reading_and_clause_boundary_rechecked_with_pc_jp"])

    def test_packed_raw_target_and_private_guard(self) -> None:
        self.assertEqual(len(self.bundle.packed), wave.TARGET_PROFILE.size)
        self.assertEqual(wave.sha256_bytes(self.bundle.packed), wave.TARGET_PROFILE.sha256)
        self.assertEqual(len(self.bundle.raw), wave.TARGET_PROFILE.raw_size)
        self.assertEqual(wave.sha256_bytes(self.bundle.raw), wave.TARGET_PROFILE.raw_sha256)
        self.assertEqual(
            self.bundle.manifest["audit_sha256"],
            wave.sha256_bytes(wave.canonical_json(self.bundle.audit)),
        )
        self.assertEqual(self.bundle.audit["reflow_policy"]["blind_or_algorithmic_reflow"], "forbidden")
        with self.assertRaises(wave.ColorTagReflowError):
            wave.require_private(wave.REPO, "repository")


if __name__ == "__main__":
    unittest.main(verbosity=2)
