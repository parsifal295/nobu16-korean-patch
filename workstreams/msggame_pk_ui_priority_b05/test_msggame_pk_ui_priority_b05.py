#!/usr/bin/env python3
"""Validation tests for the 300-entry PK msggame UI-priority B05 batch."""

from __future__ import annotations

import argparse
import collections
import json
import tempfile
import unittest
from pathlib import Path

import build_msggame_pk_ui_priority_b05 as build_b05
import candidate_selection
from ui_translations_block8_13 import TRANSLATIONS_BLOCK8_13
from ui_translations_block15 import TRANSLATIONS_BLOCK15


class MsggamePkUiPriorityB05Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.coordinates, cls.context = candidate_selection.select_coordinates()
        cls.builder = cls.context["builder"]
        cls.translations = {**TRANSLATIONS_BLOCK8_13, **TRANSLATIONS_BLOCK15}
        cls.overlay_path = build_b05.WORKSTREAM_ROOT / "public" / build_b05.OVERLAY_NAME
        cls.overlay = json.loads(cls.overlay_path.read_text(encoding="utf-8"))

    def test_exact_coordinate_contract_and_b04_reservation(self) -> None:
        selected = set(self.coordinates)
        self.assertEqual(300, len(selected))
        self.assertEqual(selected, set(self.translations))
        self.assertEqual(
            candidate_selection.B05_COORDINATES_SHA256,
            self.builder.canonical_hash([list(value) for value in sorted(selected)]),
        )
        self.assertTrue(selected <= self.context["targets"])
        self.assertTrue(selected.isdisjoint(self.context["registered"]))
        self.assertTrue(selected.isdisjoint(self.context["reserved_b04"]))
        self.assertEqual(
            candidate_selection.B04_OVERLAY_SHA256,
            self.builder.sha256(candidate_selection.B04_OVERLAY.read_bytes()),
        )

    def test_structure_script_width_and_duplicate_consistency(self) -> None:
        by_source: dict[str, list[str]] = collections.defaultdict(list)
        for coordinate, replacement in self.translations.items():
            source = self.context["sources"]["SC"]["literals"][coordinate].text
            self.assertEqual([], self.builder.common.invariant_mismatches(source, replacement), coordinate)
            self.assertEqual(
                {"cjk_unified_count": 0, "kana_count": 0},
                self.builder.script_counts(replacement),
                coordinate,
            )
            self.assertIsNotNone(self.builder.HANGUL_RE.search(replacement), coordinate)
            official_widths = []
            for label in ("SC", "JP", "EN", "TC"):
                official_widths += self.builder.line_widths(
                    self.context["sources"][label]["literals"][coordinate].text
                )
            self.assertLessEqual(
                max(self.builder.line_widths(replacement)),
                max(official_widths) + 12,
                coordinate,
            )
            by_source[source].append(replacement)
        self.assertTrue(all(len(set(values)) == 1 for values in by_source.values()))

    def test_public_overlay_is_source_free_and_exact(self) -> None:
        entries = self.overlay["entries"]
        self.assertEqual(300, self.overlay["entry_count"])
        self.assertEqual(300, len(entries))
        actual = {
            (entry["block_id"], entry["record_id"], entry["literal_id"]): entry["ko"]
            for entry in entries
        }
        self.assertEqual(self.translations, actual)
        self.assertEqual(
            {"cjk_unified_count": 0, "kana_count": 0},
            self.builder.script_counts(self.overlay_path.read_text(encoding="utf-8")),
        )

    def test_offline_and_full_candidate_proofs(self) -> None:
        validation = json.loads(
            (build_b05.WORKSTREAM_ROOT / build_b05.VALIDATION_NAME).read_text(encoding="utf-8")
        )
        self.assertTrue(validation["passed"])
        self.assertEqual(300, validation["counts"]["translated"])
        self.assertTrue(validation["offline_binary_validation"]["literal_coordinates_preserved"])
        self.assertTrue(validation["full_candidate_validation"]["literal_coordinates_preserved"])
        self.assertTrue(validation["full_candidate_validation"]["non_overlay_literals_preserved"])
        self.assertTrue(validation["coordinate_sets"]["selected_reserved_b04_disjoint"])

    def test_build_is_deterministic_and_progress_is_read_only(self) -> None:
        progress = self.builder.DEFAULT_PROGRESS
        progress_before = self.builder.sha256(progress.read_bytes())
        expected = {
            "public/" + build_b05.OVERLAY_NAME: self.builder.sha256(self.overlay_path.read_bytes()),
            "evidence/" + build_b05.EVIDENCE_NAME: self.builder.sha256(
                (build_b05.WORKSTREAM_ROOT / "evidence" / build_b05.EVIDENCE_NAME).read_bytes()
            ),
            "review/" + build_b05.REVIEW_NAME: self.builder.sha256(
                (build_b05.WORKSTREAM_ROOT / "review" / build_b05.REVIEW_NAME).read_bytes()
            ),
            build_b05.VALIDATION_NAME: self.builder.sha256(
                (build_b05.WORKSTREAM_ROOT / build_b05.VALIDATION_NAME).read_bytes()
            ),
        }
        with tempfile.TemporaryDirectory(prefix="nobu16-b05-test-") as temp_root:
            args = argparse.Namespace(
                pk_sc=self.builder.DEFAULT_PK_SC,
                pk_jp=self.builder.DEFAULT_PK_JP,
                pk_en=self.builder.DEFAULT_PK_EN,
                pk_tc=self.builder.DEFAULT_PK_TC,
                progress=progress,
                target_catalog=self.builder.DEFAULT_TARGET,
                out_root=Path(temp_root),
            )
            build_b05.build(args)
            actual = {
                relative: self.builder.sha256((Path(temp_root) / relative).read_bytes())
                for relative in expected
            }
        self.assertEqual(expected, actual)
        self.assertEqual(progress_before, self.builder.sha256(progress.read_bytes()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
