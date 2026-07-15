from __future__ import annotations

import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path


TEST_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = TEST_PATH.parents[1]
REPO_ROOT = TEST_PATH.parents[3]
sys.path[:0] = [str(WORKSTREAM_ROOT), str(REPO_ROOT / "tools")]

import build_msggame_pk_ui_priority_b04 as builder  # noqa: E402
import build_full_pk_message_candidate as integration  # noqa: E402


class MsgGamePkUiPriorityB04Tests(unittest.TestCase):
    def arguments(self, out_root: Path) -> argparse.Namespace:
        return argparse.Namespace(
            pk_sc=builder.DEFAULT_PK_SC,
            pk_jp=builder.DEFAULT_PK_JP,
            pk_en=builder.DEFAULT_PK_EN,
            pk_tc=builder.DEFAULT_PK_TC,
            progress=builder.DEFAULT_PROGRESS,
            target_catalog=builder.DEFAULT_TARGET,
            out_root=out_root,
        )

    def test_scope_and_disjointness(self) -> None:
        self.assertEqual(len(builder.TRANSLATIONS), 250)
        self.assertEqual(
            {coordinate[0] for coordinate in builder.TRANSLATIONS},
            {6, 7, 8, 9, 12, 13, 14, 15, 17},
        )
        self.assertFalse(set(builder.TRANSLATIONS) & set(builder.EXCLUSIONS))
        registered, _b01 = builder.existing_coordinates(builder.DEFAULT_PROGRESS)
        self.assertFalse(set(builder.TRANSLATIONS) & registered)

    def test_rebuild_is_deterministic_and_matches_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            result_a = builder.build(self.arguments(Path(first)))
            result_b = builder.build(self.arguments(Path(second)))
            self.assertEqual(result_a, result_b)
            for folder, name in (
                ("public", builder.OVERLAY_NAME),
                ("evidence", builder.EVIDENCE_NAME),
                ("review", builder.REVIEW_NAME),
                ("", builder.VALIDATION_NAME),
            ):
                generated = Path(first) / folder / name if folder else Path(first) / name
                committed = WORKSTREAM_ROOT / folder / name if folder else WORKSTREAM_ROOT / name
                self.assertEqual(generated.read_bytes(), committed.read_bytes(), name)

    def test_overlay_passes_full_candidate_parser(self) -> None:
        payload = json.loads(
            (WORKSTREAM_ROOT / "public" / builder.OVERLAY_NAME).read_text(encoding="utf-8")
        )
        parsed = integration.parse_msggame_overlay(payload, "b04")
        self.assertEqual(len(parsed["entries"]), 250)
        self.assertEqual(
            set(payload),
            {
                "schema", "overlay_id", "resource", "base_language", "entry_count",
                "distribution_policy", "stock_sc", "defaults", "entries",
                "translation_provenance", "selection_policy",
            },
        )

    def test_public_artifacts_are_source_free(self) -> None:
        for path in (
            WORKSTREAM_ROOT / "public" / builder.OVERLAY_NAME,
            WORKSTREAM_ROOT / "evidence" / builder.EVIDENCE_NAME,
            WORKSTREAM_ROOT / "review" / builder.REVIEW_NAME,
            WORKSTREAM_ROOT / builder.VALIDATION_NAME,
        ):
            self.assertEqual(
                builder.script_counts(path.read_text(encoding="utf-8")),
                {"cjk_unified_count": 0, "kana_count": 0},
            )


if __name__ == "__main__":
    unittest.main()
