#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

import build_recovery as builder
from nobu16_lz4 import decompress_wrapper, recompress_wrapper
from nobu16_msg_table import parse_message_table, rebuild_message_table


ROOT = Path(__file__).resolve().parent
PUBLIC_ENTRY_FIELDS = {"id", "source_jp_utf16le_sha256", "ko"}


class SteamJpMsguiWave07RecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit, cls.audit_blob = builder.load_audit()
        cls.foundation_ids, cls.foundation_blob = builder.load_foundation_ids()
        cls.decisions, cls.decisions_blob = builder.load_decisions()
        cls.values = builder.build_values()
        cls.overlay = cls.values["overlay"][0]
        cls.exclusions = cls.values["exclusions"][0]

    def test_withheld_partition_is_exact_and_disjoint(self) -> None:
        self.assertEqual(344, len(self.audit))
        self.assertEqual(344, len(self.decisions))
        self.assertEqual(set(self.audit), set(self.decisions))
        self.assertEqual(3_693, len(self.foundation_ids))
        self.assertTrue(self.foundation_ids.isdisjoint(self.decisions))
        self.assertEqual(
            builder.WITHHELD_COORDINATE_SHA256,
            builder.canonical_hash(sorted(self.decisions)),
        )

    def test_recovered_and_excluded_counts_are_exact(self) -> None:
        recovered = [row for row in self.decisions.values() if row["status"] == "recovered"]
        excluded = [row for row in self.decisions.values() if row["status"] == "excluded"]
        self.assertEqual(343, len(recovered))
        self.assertEqual(1, len(excluded))
        self.assertEqual(343, self.overlay["entry_count"])
        self.assertEqual(341, self.overlay["effective_change_count"])
        self.assertEqual(2, self.overlay["no_op_count"])
        self.assertEqual(1, self.overlay["excluded_entry_count"])

    def test_current_jp_hashes_and_invariants_are_exact(self) -> None:
        jp, _spec = builder.load_table(builder.DEFAULT_JP_STOCK, "JP")
        entries = {row["id"]: row for row in self.overlay["entries"]}
        self.assertEqual(343, len(entries))
        for entry_id, row in entries.items():
            source = jp[entry_id]
            self.assertEqual(builder.text_hash(source), row["source_jp_utf16le_sha256"])
            self.assertEqual([], builder.mismatch_keys(source, row["ko"]))
            self.assertEqual(PUBLIC_ENTRY_FIELDS, set(row))

    def test_only_nonsemantic_jp_slot_is_explicitly_excluded(self) -> None:
        jp, _spec = builder.load_table(builder.DEFAULT_JP_STOCK, "JP")
        self.assertEqual(1, len(self.exclusions["entries"]))
        row = self.exclusions["entries"][0]
        self.assertEqual(2657, row["id"])
        self.assertEqual("jp_slot_nonsemantic_whitespace_only", row["reason"])
        self.assertFalse(builder.has_semantic_text(jp[row["id"]]))
        self.assertEqual(builder.text_hash(jp[row["id"]]), row["source_jp_utf16le_sha256"])

    def test_outputs_are_source_free_and_byte_reproducible(self) -> None:
        targets = {
            "overlay": builder.PUBLIC_OVERLAY,
            "exclusions": builder.EXCLUSIONS,
            "review": builder.REVIEW,
            "validation": builder.VALIDATION,
        }
        builder.source_free(self.decisions_blob, "decisions")
        for name, path in targets.items():
            self.assertTrue(path.is_file(), path)
            blob = path.read_bytes()
            self.assertEqual(self.values[name][1], blob, path)
            builder.source_free(blob, name)
        self.assertEqual([], list(ROOT.rglob("*.bin")))

    def test_private_multilingual_context_pins_are_exact(self) -> None:
        context_paths = {
            "JP": builder.DEFAULT_JP_STOCK,
            "SC": builder.DEFAULT_CONTEXT_ROOT / "SC" / "msgui.bin",
            "EN": builder.DEFAULT_CONTEXT_ROOT / "EN" / "msgui.bin",
            "TC": builder.DEFAULT_CONTEXT_ROOT / "TC" / "msgui.bin",
        }
        for language, path in context_paths.items():
            texts, spec = builder.load_table(path, language)
            self.assertEqual(5_100, len(texts))
            self.assertEqual(builder.PRIVATE_SPECS[language], spec)

    def test_foundation_plus_supplement_rebuilds_in_memory(self) -> None:
        packed = builder.DEFAULT_JP_STOCK.read_bytes()
        _header, raw = decompress_wrapper(packed)
        table = parse_message_table(raw)
        foundation = json.loads(self.foundation_blob.decode("utf-8"))
        entries = foundation["entries"] + self.overlay["entries"]
        self.assertEqual(4_036, len(entries))
        self.assertEqual(4_036, len({row["id"] for row in entries}))

        texts = list(table.texts)
        selected: set[int] = set()
        for row in entries:
            entry_id = row["id"]
            source = table.texts[entry_id]
            self.assertEqual(builder.text_hash(source), row["source_jp_utf16le_sha256"])
            self.assertEqual([], builder.mismatch_keys(source, row["ko"]))
            texts[entry_id] = row["ko"]
            selected.add(entry_id)

        rebuilt_a = rebuild_message_table(table, texts)
        rebuilt_b = rebuild_message_table(table, texts)
        self.assertEqual(rebuilt_a, rebuilt_b)
        candidate_a = recompress_wrapper(rebuilt_a, packed)
        candidate_b = recompress_wrapper(rebuilt_b, packed)
        self.assertEqual(candidate_a, candidate_b)
        _candidate_header, check_raw = decompress_wrapper(candidate_a)
        self.assertEqual(rebuilt_a, check_raw)
        check = parse_message_table(check_raw)
        self.assertEqual(5_100, check.string_count)
        self.assertEqual(tuple(texts), check.texts)
        for entry_id, source in enumerate(table.texts):
            if entry_id not in selected:
                self.assertEqual(source, check.texts[entry_id])
        self.assertNotIn(2657, selected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
