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
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_msggame_pk_ui_priority_b02 as builder  # noqa: E402

EXCLUSIONS = builder.EXCLUSIONS
TRANSLATIONS = builder.TRANSLATIONS


class MsgGamePkUiPriorityB02Tests(unittest.TestCase):
    def arguments(self, out_root: Path) -> argparse.Namespace:
        return argparse.Namespace(
            pk_sc=builder.DEFAULT_PK_SC,
            pk_jp=builder.DEFAULT_PK_JP,
            pk_en=builder.DEFAULT_PK_EN,
            progress=builder.DEFAULT_PROGRESS,
            target_catalog=builder.DEFAULT_TARGET,
            out_root=out_root,
        )

    def test_scope_and_mandatory_false_positive(self) -> None:
        self.assertEqual(len(TRANSLATIONS), 53)
        self.assertTrue(all(coordinate[0] not in {13, 14} for coordinate in TRANSLATIONS))
        self.assertEqual(EXCLUSIONS[(7, 2076, 0)], "dynamic_narrative_false_positive")
        self.assertFalse(set(TRANSLATIONS) & set(EXCLUSIONS))

    def test_b01_and_registered_overlays_are_disjoint(self) -> None:
        registered, b01 = builder.existing_coordinates(builder.DEFAULT_PROGRESS)
        self.assertFalse(set(TRANSLATIONS) & registered)
        self.assertFalse(set(TRANSLATIONS) & b01)

    def test_rebuild_matches_committed_artifacts(self) -> None:
        source_paths = (builder.DEFAULT_PK_SC, builder.DEFAULT_PK_JP, builder.DEFAULT_PK_EN)
        before = {path: builder.sha256(path.read_bytes()) for path in source_paths}
        with tempfile.TemporaryDirectory() as directory:
            out_root = Path(directory)
            result = builder.build(self.arguments(out_root))
            self.assertEqual(result["entry_count"], 53)
            expected = (
                ("public", builder.OVERLAY_NAME),
                ("evidence", builder.EVIDENCE_NAME),
                ("review", builder.REVIEW_NAME),
                ("", builder.VALIDATION_NAME),
            )
            for folder, name in expected:
                generated = out_root / folder / name if folder else out_root / name
                committed = WORKSTREAM_ROOT / folder / name if folder else WORKSTREAM_ROOT / name
                self.assertEqual(generated.read_bytes(), committed.read_bytes(), name)
        after = {path: builder.sha256(path.read_bytes()) for path in source_paths}
        self.assertEqual(before, after)

    def test_public_artifacts_are_source_free(self) -> None:
        paths = (
            WORKSTREAM_ROOT / "public" / builder.OVERLAY_NAME,
            WORKSTREAM_ROOT / "evidence" / builder.EVIDENCE_NAME,
            WORKSTREAM_ROOT / "review" / builder.REVIEW_NAME,
            WORKSTREAM_ROOT / builder.VALIDATION_NAME,
        )
        for path in paths:
            self.assertEqual(
                builder.script_counts(path.read_text(encoding="utf-8")),
                {"cjk_unified_count": 0, "kana_count": 0},
                path.name,
            )

    def test_validation_contracts(self) -> None:
        path = WORKSTREAM_ROOT / builder.VALIDATION_NAME
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(payload["passed"])
        self.assertEqual(payload["counts"]["translated"], 53)
        self.assertTrue(payload["coordinate_sets"]["selected_b01_disjoint"])
        self.assertTrue(payload["proofs"]["placeholder_control_code_newline_preserved"])
        self.assertTrue(payload["proofs"]["display_width_budget_preserved"])
        self.assertTrue(payload["proofs"]["mandatory_dynamic_narrative_false_positive_excluded"])
        self.assertFalse(payload["offline_binary_validation"]["installed_game_file_written"])


if __name__ == "__main__":
    unittest.main()
