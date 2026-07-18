from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_npc_name_quality_wave50_v1.py"
SPEC = importlib.util.spec_from_file_location("wave50_npc_name_quality_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot import Wave 50 builder")
wave50 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave50
SPEC.loader.exec_module(wave50)


EXPECTED_IDS = {
    "msgdata": [405, 17197, 17235, 17352],
    "msgev": [291, 292, 293, 2412, 2421, 2450, 2477, 2521, 2529, 2544, 2567, 3960],
}


class Wave50NpcNameQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave50.prepare_candidate()
        cls.before = {key: wave50.load_table(spec.current) for key, spec in wave50.RESOURCES.items()}
        cls.after = {}
        for key, payload in cls.bundle.packed.items():
            _header, raw = wave50.decompress_wrapper(payload)
            cls.after[key] = wave50.parse_message_table(raw)

    def test_exact_16_record_scope_and_w49_guard(self) -> None:
        self.assertEqual(len(wave50.CHANGES), 16)
        self.assertEqual(
            {key: list(ids) for key, ids in self.bundle.actual_changed_ids.items()},
            EXPECTED_IDS,
        )
        self.assertEqual(self.bundle.audit["changed_record_count"], 16)
        self.assertEqual(self.bundle.audit["actual_changed_ids"], EXPECTED_IDS)
        self.assertTrue(set(EXPECTED_IDS["msgev"]).isdisjoint(wave50.W49_OVERLAP_GUARD_IDS))
        self.assertTrue(self.bundle.audit["w49_overlap_guard_passed"])

    def test_only_declared_records_change(self) -> None:
        for key in wave50.RESOURCES:
            with self.subTest(resource=key):
                changed = [
                    entry_id
                    for entry_id, (before, after) in enumerate(zip(self.before[key].table.texts, self.after[key].texts))
                    if before != after
                ]
                self.assertEqual(changed, EXPECTED_IDS[key])

    def test_3956_is_an_explicit_byte_identical_width_hold(self) -> None:
        self.assertEqual(self.bundle.audit["held_record_count"], 1)
        hold = self.bundle.audit["explicit_holds"][0]
        self.assertEqual((hold["resource"], hold["id"]), ("msgev", 3956))
        self.assertTrue(hold["candidate_utf16le_byte_identical"])
        before = self.before["msgev"].table.texts[3956].encode("utf-16le")
        after = self.after["msgev"].texts[3956].encode("utf-16le")
        self.assertEqual(before, after)
        self.assertLessEqual(max(hold["preimage_line_widths_px"]), wave50.PK_MAX_LINE_PX)
        self.assertGreater(max(hold["name_only_target_line_widths_px"]), wave50.PK_MAX_LINE_PX)

    def test_preimage_jp_en_anchor_and_hash_bindings(self) -> None:
        japanese = {key: wave50.load_table(spec.japanese) for key, spec in wave50.RESOURCES.items()}
        english = {key: wave50.load_table(spec.english) for key, spec in wave50.RESOURCES.items()}
        for record in self.bundle.audit["records"]:
            with self.subTest(resource=record["resource"], entry_id=record["id"]):
                key = record["resource"]
                entry_id = record["id"]
                self.assertEqual(self.before[key].table.texts[entry_id], record["preimage"])
                self.assertEqual(self.after[key].texts[entry_id], record["target"])
                self.assertEqual(wave50.text_hash(record["preimage"]), record["preimage_utf16le_sha256"])
                self.assertEqual(wave50.text_hash(record["target"]), record["target_utf16le_sha256"])
                jp_text = japanese[key].table.texts[entry_id]
                en_text = english[key].table.texts[entry_id]
                self.assertEqual(wave50.text_hash(jp_text), record["jp_utf16le_sha256"])
                self.assertEqual(wave50.text_hash(en_text), record["en_utf16le_sha256"])
                for anchor, anchor_hash in zip(record["jp_anchors"], record["jp_anchor_utf16le_sha256"]):
                    self.assertIn(anchor, jp_text)
                    self.assertEqual(wave50.text_hash(anchor), anchor_hash)
                for anchor, anchor_hash in zip(record["en_anchors"], record["en_anchor_utf16le_sha256"]):
                    self.assertIn(anchor, en_text)
                    self.assertEqual(wave50.text_hash(anchor), anchor_hash)

    def test_tokens_tags_manual_lf_line_counts_and_912px_width(self) -> None:
        advance, _font = wave50.load_event_font_advance()
        for record in self.bundle.audit["records"]:
            with self.subTest(resource=record["resource"], entry_id=record["id"]):
                self.assertEqual(
                    wave50.protected_signature(record["preimage"]),
                    wave50.protected_signature(record["target"]),
                )
                self.assertEqual(record["protected_signature"], wave50.protected_signature(record["target"]))
                widths = wave50.line_widths(record["target"], advance)
                self.assertEqual(list(widths), record["target_line_widths_px"])
                self.assertEqual(len(widths), record["target_line_count"])
                self.assertGreaterEqual(len(widths), 1)
                self.assertLessEqual(len(widths), wave50.MAX_LINES)
                self.assertLessEqual(max(widths), wave50.PK_MAX_LINE_PX)

    def test_packed_raw_profiles_manifest_and_binding(self) -> None:
        for key, spec in wave50.RESOURCES.items():
            with self.subTest(resource=key):
                wave50.require_profile(self.bundle.packed[key], self.bundle.raw[key], spec.target, "test candidate")
        binding = [wave50.record_binding(record) for record in self.bundle.audit["records"]]
        self.assertEqual(wave50.sha256_bytes(wave50.canonical_json(binding)), wave50.RECORD_BINDING_SHA256)
        self.assertEqual(self.bundle.audit["record_binding_sha256"], wave50.RECORD_BINDING_SHA256)
        self.assertEqual(
            self.bundle.manifest["audit_sha256"],
            wave50.sha256_bytes(wave50.canonical_json(self.bundle.audit)),
        )

    def test_private_output_guard(self) -> None:
        with self.assertRaises(wave50.Wave50Error):
            wave50.require_private(wave50.REPO, "repository")


if __name__ == "__main__":
    unittest.main(verbosity=2)
