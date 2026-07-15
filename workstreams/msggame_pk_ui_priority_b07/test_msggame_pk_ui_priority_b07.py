#!/usr/bin/env python3
"""Validation tests for the 300-entry PK msggame UI-priority B07 batch."""

from __future__ import annotations

import argparse
import collections
import json
import sys
import tempfile
import unittest
from pathlib import Path

WORKSTREAM_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_msggame_pk_ui_priority_b07 as build_b07
import candidate_selection
from translations_block6 import TRANSLATIONS_BLOCK6
from translations_block8_landmarks import TRANSLATIONS_BLOCK8_LANDMARKS
from translations_block8_reports_a import TRANSLATIONS_BLOCK8_REPORTS_A
from translations_block8_reports_b import TRANSLATIONS_BLOCK8_REPORTS_B
from translations_help import TRANSLATIONS_HELP


class MsggamePkUiPriorityB07Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.coordinates, cls.context = candidate_selection.select_coordinates()
        cls.builder = cls.context["builder"]
        cls.translations = {
            **TRANSLATIONS_BLOCK6,
            **TRANSLATIONS_BLOCK8_REPORTS_A,
            **TRANSLATIONS_BLOCK8_REPORTS_B,
            **TRANSLATIONS_BLOCK8_LANDMARKS,
            **TRANSLATIONS_HELP,
        }
        cls.overlay_path = build_b07.WORKSTREAM_ROOT / "public" / build_b07.OVERLAY_NAME
        cls.overlay = json.loads(cls.overlay_path.read_text(encoding="utf-8"))

    def test_exact_coordinate_contract_and_immutable_history(self) -> None:
        selected = set(self.coordinates)
        self.assertEqual(300, len(selected))
        self.assertEqual(selected, set(self.translations))
        self.assertEqual(
            candidate_selection.B07_COORDINATES_SHA256,
            self.builder.canonical_hash([list(value) for value in sorted(selected)]),
        )
        self.assertEqual({6: 28, 8: 227, 13: 28, 14: 17}, self.context["selected_counts"])
        self.assertTrue({16, 17}.isdisjoint({value[0] for value in selected}))
        self.assertTrue(selected <= self.context["targets"])
        self.assertTrue(selected.isdisjoint(self.context["history"]["prefix_coordinates"]))
        self.assertTrue(selected.isdisjoint(self.context["history"]["future_coordinates"]))
        self.assertEqual(
            candidate_selection.PREFIX_ENTRY_COUNT,
            len(self.context["history"]["prefix_coordinates"]),
        )
        self.assertEqual(
            candidate_selection.PREFIX_COORDINATES_SHA256,
            self.builder.canonical_hash(
                [list(value) for value in sorted(self.context["history"]["prefix_coordinates"])]
            ),
        )

    def test_structure_script_width_and_duplicate_consistency(self) -> None:
        by_source: dict[str, list[str]] = collections.defaultdict(list)
        part_lengths = [
            len(TRANSLATIONS_BLOCK6),
            len(TRANSLATIONS_BLOCK8_REPORTS_A),
            len(TRANSLATIONS_BLOCK8_REPORTS_B),
            len(TRANSLATIONS_BLOCK8_LANDMARKS),
            len(TRANSLATIONS_HELP),
        ]
        self.assertEqual([28, 71, 79, 77, 45], part_lengths)
        self.assertEqual(300, sum(part_lengths))
        for coordinate, replacement in self.translations.items():
            source = self.context["sources"]["SC"]["literals"][coordinate].text
            self.assertEqual(
                [], self.builder.common.invariant_mismatches(source, replacement), coordinate
            )
            self.assertEqual(
                {"cjk_unified_count": 0, "kana_count": 0},
                self.builder.script_counts(replacement),
                coordinate,
            )
            self.assertIsNotNone(self.builder.HANGUL_RE.search(replacement), coordinate)
            official_widths: list[int] = []
            for label in ("SC", "JP", "EN", "TC"):
                literal = self.context["sources"][label]["literals"].get(coordinate)
                if literal is not None:
                    official_widths += self.builder.line_widths(literal.text)
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
        self.assertEqual(
            155,
            self.overlay["translation_provenance"]["switch_context"][
                "unique_jp_hash_semantic_context_count"
            ],
        )
        actual = {
            (entry["block_id"], entry["record_id"], entry["literal_id"]): entry["ko"]
            for entry in entries
        }
        self.assertEqual(self.translations, actual)
        self.assertEqual(
            candidate_selection.SELF_OVERLAY_SHA256,
            self.builder.sha256(self.overlay_path.read_bytes()),
        )
        self.assertEqual(
            {"cjk_unified_count": 0, "kana_count": 0},
            self.builder.script_counts(self.overlay_path.read_text(encoding="utf-8")),
        )

    def test_offline_and_full_candidate_proofs(self) -> None:
        validation = json.loads(
            (build_b07.WORKSTREAM_ROOT / build_b07.VALIDATION_NAME).read_text(encoding="utf-8")
        )
        self.assertTrue(validation["passed"])
        self.assertEqual(300, validation["counts"]["translated"])
        self.assertTrue(validation["offline_binary_validation"]["literal_coordinates_preserved"])
        self.assertTrue(validation["full_candidate_validation"]["literal_coordinates_preserved"])
        self.assertTrue(validation["full_candidate_validation"]["non_overlay_literals_preserved"])
        self.assertEqual(11_722, validation["full_candidate_validation"]["full_overlay_entry_count"])
        self.assertEqual(
            11_422,
            validation["full_candidate_validation"]["registered_predecessor_entry_count"],
        )
        self.assertEqual(
            "D5365A49945582D1F82BF5137CA898EC9EBE270B5F8B90513497E6ADC68E9AD9",
            validation["full_candidate_validation"]["target_packed_sha256"],
        )
        self.assertTrue(validation["proofs"]["self_registration_does_not_feed_selection"])
        self.assertTrue(validation["proofs"]["future_registration_does_not_feed_selection"])
        self.assertTrue(validation["proofs"]["narrative_blocks_16_and_17_excluded"])

    def _expected_artifact_hashes(self) -> dict[str, str]:
        return {
            "public/" + build_b07.OVERLAY_NAME: self.builder.sha256(self.overlay_path.read_bytes()),
            "evidence/" + build_b07.EVIDENCE_NAME: self.builder.sha256(
                (build_b07.WORKSTREAM_ROOT / "evidence" / build_b07.EVIDENCE_NAME).read_bytes()
            ),
            "review/" + build_b07.REVIEW_NAME: self.builder.sha256(
                (build_b07.WORKSTREAM_ROOT / "review" / build_b07.REVIEW_NAME).read_bytes()
            ),
            build_b07.VALIDATION_NAME: self.builder.sha256(
                (build_b07.WORKSTREAM_ROOT / build_b07.VALIDATION_NAME).read_bytes()
            ),
        }

    def _build_to(self, out_root: Path, progress: Path) -> dict[str, str]:
        args = argparse.Namespace(
            pk_sc=self.builder.DEFAULT_PK_SC,
            pk_jp=self.builder.DEFAULT_PK_JP,
            pk_en=self.builder.DEFAULT_PK_EN,
            pk_tc=self.builder.DEFAULT_PK_TC,
            progress=progress,
            target_catalog=self.builder.DEFAULT_TARGET,
            out_root=out_root,
        )
        build_b07.build(args)
        return {
            relative: self.builder.sha256((out_root / relative).read_bytes())
            for relative in self._expected_artifact_hashes()
        }

    def test_build_is_deterministic_and_progress_is_read_only(self) -> None:
        progress = self.builder.DEFAULT_PROGRESS
        progress_before = self.builder.sha256(progress.read_bytes())
        with tempfile.TemporaryDirectory(prefix="nobu16-b07-test-") as temp_root:
            actual = self._build_to(Path(temp_root), progress)
        self.assertEqual(self._expected_artifact_hashes(), actual)
        self.assertEqual(progress_before, self.builder.sha256(progress.read_bytes()))

    def test_self_and_future_registration_filter(self) -> None:
        progress_payload = json.loads(self.builder.DEFAULT_PROGRESS.read_text(encoding="utf-8"))
        progress_item = next(item for item in progress_payload["resources"] if item["path"] == build_b07.RESOURCE)
        patterns = progress_item["overlay_globs"]
        if candidate_selection.SELF_RELATIVE not in patterns:
            patterns.append(candidate_selection.SELF_RELATIVE)

        unavailable = (
            self.context["history"]["prefix_coordinates"]
            | self.context["history"]["future_coordinates"]
            | set(self.coordinates)
        )
        future_coordinate = min(self.context["targets"] - unavailable)
        future_source = self.context["sources"]["SC"]["literals"][future_coordinate].text
        handle = tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".json", prefix=".b07-future-", dir=WORKSTREAM_ROOT, delete=False
        )
        future_path = Path(handle.name)
        handle.close()
        future_relative = future_path.relative_to(candidate_selection.REPO_ROOT).as_posix()
        future_overlay = {
            "schema": "nobu16.kr.literal-overlay.v0.1",
            "overlay_id": "msggame_pk_ui_priority_b07_future_filter_fixture.v1",
            "resource": build_b07.RESOURCE,
            "base_language": "SC",
            "defaults": {"status": "translated"},
            "entry_count": 1,
            "distribution_policy": {
                "contains_commercial_source_text": False,
                "contains_complete_game_resource": False,
            },
            "entries": [
                {
                    "block_id": future_coordinate[0],
                    "record_id": future_coordinate[1],
                    "literal_id": future_coordinate[2],
                    "source_sc_utf16le_sha256": self.builder.text_hash(future_source),
                    "ko": "미래 배치 검증",
                }
            ],
        }
        try:
            build_b07._write_json(future_path, future_overlay)
            patterns.append(future_relative)
            with tempfile.TemporaryDirectory(prefix="nobu16-b07-filter-") as temp_root:
                progress_path = Path(temp_root) / "progress.json"
                build_b07._write_json(progress_path, progress_payload)
                filtered, filtered_context = candidate_selection.select_coordinates(
                    progress_path=progress_path
                )
                self.assertEqual(self.coordinates, filtered)
                self.assertEqual(1, filtered_context["history"]["self_registration_count"])
                self.assertIn(future_relative, filtered_context["history"]["future_paths"])
                actual = self._build_to(Path(temp_root) / "out", progress_path)
                self.assertEqual(self._expected_artifact_hashes(), actual)

            # A successor cannot claim a B07 coordinate even when B07 itself
            # is absent from the synthetic progress state.
            marker = patterns.index(candidate_selection.B06_RELATIVE)
            progress_item["overlay_globs"] = patterns[: marker + 1] + [future_relative]
            claimed = self.coordinates[0]
            future_overlay["entries"][0].update(
                {
                    "block_id": claimed[0],
                    "record_id": claimed[1],
                    "literal_id": claimed[2],
                    "source_sc_utf16le_sha256": self.builder.text_hash(
                        self.context["sources"]["SC"]["literals"][claimed].text
                    ),
                }
            )
            build_b07._write_json(future_path, future_overlay)
            with tempfile.TemporaryDirectory(prefix="nobu16-b07-overlap-") as temp_root:
                progress_path = Path(temp_root) / "progress.json"
                build_b07._write_json(progress_path, progress_payload)
                with self.assertRaisesRegex(RuntimeError, "future overlay overlaps"):
                    candidate_selection.select_coordinates(progress_path=progress_path)
        finally:
            future_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
