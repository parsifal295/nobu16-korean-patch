"""Regression gates for the three-row Switch biography cleanup."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
WORKSTREAM_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = WORKSTREAM_ROOT.parents[1]
GAME_ROOT = REPO_ROOT.parent
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_switch_msgbre_v13_cjk_cleanup as builder  # noqa: E402


class SwitchMsgbreV13CleanupTests(unittest.TestCase):
    def args_for(self, out_root: Path, **overrides: Path) -> argparse.Namespace:
        values: dict[str, Path] = {
            "switch_zip": REPO_ROOT / builder.SWITCH_ARCHIVE_RELATIVE,
            "base_jp_strdata": GAME_ROOT / "MSG" / "JP" / "strdata.bin",
            "stock_pk_jp": GAME_ROOT / "MSG_PK" / "JP" / "msgbre.bin",
            "stock_pk_sc": builder.strict.LOCAL_STOCK_SC_BACKUP,
            "progress": REPO_ROOT / "data" / "public" / "translation_progress.v0.1.json",
            "out_root": out_root,
        }
        values.update(overrides)
        return argparse.Namespace(**values)

    def temporary_output(self) -> tempfile.TemporaryDirectory[str]:
        return tempfile.TemporaryDirectory(
            prefix="test-switch-msgbre-cleanup-", dir=REPO_ROOT / "tmp"
        )

    def test_reproducible_build_has_exactly_the_three_pinned_rows(self) -> None:
        with self.temporary_output() as directory:
            root = Path(directory)
            result = builder.build_reproducibly(self.args_for(root))
            overlay = json.loads(
                (root / "public" / builder.OVERLAY_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual(result["entry_count"], 3)
            self.assertEqual(
                [entry["id"] for entry in overlay["entries"]], builder.SELECTED_IDS
            )
            self.assertEqual(
                [builder.common.text_hash(entry["ko"]) for entry in overlay["entries"]],
                [
                    builder.CLEANUP_PINS[entry_id]["cleaned_ko_utf16le_sha256"]
                    for entry_id in builder.SELECTED_IDS
                ],
            )
            self.assertTrue(result["target"]["parse_rebuild_round_trip"])
            self.assertTrue(result["target"]["wrapper_round_trip"])
            checked_paths = {
                "overlay": WORKSTREAM_ROOT / "public" / builder.OVERLAY_NAME,
                "alignment_evidence": WORKSTREAM_ROOT / "evidence" / builder.EVIDENCE_NAME,
                "review_index": WORKSTREAM_ROOT / "review" / builder.REVIEW_NAME,
                "generation_validation": WORKSTREAM_ROOT / builder.VALIDATION_NAME,
            }
            for name, path in checked_paths.items():
                self.assertEqual(path.read_bytes(), result["files"][name], name)

    def test_rows_are_disjoint_and_inside_the_stock_visible_target(self) -> None:
        with self.temporary_output() as directory:
            root = Path(directory)
            builder.build_once(self.args_for(root), root)
            claimed, snapshot = builder.load_existing_claims(self.args_for(root).progress)
            evidence = json.loads(
                (root / "evidence" / builder.EVIDENCE_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual(snapshot["unique_claimed_count"], 2203)
            self.assertEqual(
                snapshot["claimed_ids_sha256"],
                builder.EXPECTED_PRIOR_CLAIMED_IDS_SHA256,
            )
            self.assertTrue(snapshot["successors_excluded_from_prior_claims"])
            self.assertTrue(all(row["source_free"] for row in snapshot["successor_overlays"]))
            self.assertFalse(claimed.intersection(builder.SELECTED_IDS))
            self.assertTrue(
                all(
                    entry["selected_within_stock_visible_target"]
                    for entry in evidence["entries"]
                )
            )

    def test_public_artifacts_are_source_script_free_and_preserve_invariants(self) -> None:
        with self.temporary_output() as directory:
            root = Path(directory)
            builder.build_once(self.args_for(root), root)
            for path in (
                root / "public" / builder.OVERLAY_NAME,
                root / "evidence" / builder.EVIDENCE_NAME,
                root / "review" / builder.REVIEW_NAME,
                root / builder.VALIDATION_NAME,
            ):
                self.assertEqual(
                    builder.script_counts(path.read_text(encoding="utf-8")),
                    {"cjk_unified_count": 0, "kana_count": 0},
                    path.name,
                )
            evidence = json.loads(
                (root / "evidence" / builder.EVIDENCE_NAME).read_text(encoding="utf-8")
            )
            self.assertTrue(
                all(
                    entry["all_pk_sc_message_invariants_preserved"]
                    for entry in evidence["entries"]
                )
            )

    def test_inputs_are_unchanged(self) -> None:
        with self.temporary_output() as directory:
            args = self.args_for(Path(directory))
            before = builder.input_snapshot(args)
            builder.build_once(args, Path(directory))
            self.assertEqual(builder.input_snapshot(args), before)

    def test_non_release_archive_is_rejected(self) -> None:
        with self.temporary_output() as directory:
            root = Path(directory)
            bad = root / "not-the-release.zip"
            bad.write_bytes(b"not a Switch patch archive")
            with self.assertRaises(builder.MsgbreCleanupError):
                builder.build_once(
                    self.args_for(root / "out", switch_zip=bad), root / "out"
                )


if __name__ == "__main__":
    unittest.main()
