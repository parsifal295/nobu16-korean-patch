"""Regression gates for the strict Switch v1.1 PK biography importer."""

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

import build_switch_msgbre_v11 as builder  # noqa: E402


class SwitchMsgbreV11Tests(unittest.TestCase):
    def args_for(self, out_root: Path, **overrides: Path) -> argparse.Namespace:
        values: dict[str, Path] = {
            "switch_zip": REPO_ROOT / builder.SWITCH_ARCHIVE_RELATIVE,
            "base_jp_strdata": GAME_ROOT / "MSG" / "JP" / "strdata.bin",
            "stock_pk_jp": GAME_ROOT / "MSG_PK" / "JP" / "msgbre.bin",
            "stock_pk_sc": builder.LOCAL_STOCK_SC_BACKUP,
            "progress": REPO_ROOT / "data" / "public" / "translation_progress.v0.1.json",
            "out_root": out_root,
        }
        values.update(overrides)
        return argparse.Namespace(**values)

    def temporary_output(self) -> tempfile.TemporaryDirectory[str]:
        return tempfile.TemporaryDirectory(prefix="test-switch-msgbre-", dir=REPO_ROOT / "tmp")

    def test_strict_reproducible_build_has_the_pinned_increment(self) -> None:
        with self.temporary_output() as directory:
            result = builder.build_reproducibly(self.args_for(Path(directory)))
            self.assertEqual(result["entry_count"], builder.EXPECTED_SELECTED_COUNT)
            self.assertEqual(result["selected_ids_sha256"], builder.EXPECTED_SELECTED_IDS_SHA256)
            self.assertTrue(result["target"]["parse_rebuild_round_trip"])
            self.assertTrue(result["target"]["wrapper_round_trip"])
            overlay = json.loads((Path(directory) / "public" / builder.OVERLAY_NAME).read_text(encoding="utf-8"))
            self.assertEqual(overlay["entry_count"], 1367)
            self.assertEqual([entry["id"] for entry in overlay["entries"]], sorted(entry["id"] for entry in overlay["entries"]))
            self.assertEqual(overlay["entries"][0]["id"], 836)
            self.assertEqual(overlay["entries"][-1]["id"], 2206)
            checked_paths = {
                "overlay": WORKSTREAM_ROOT / "public" / builder.OVERLAY_NAME,
                "alignment_evidence": WORKSTREAM_ROOT / "evidence" / builder.EVIDENCE_NAME,
                "review_index": WORKSTREAM_ROOT / "review" / builder.REVIEW_NAME,
                "generation_validation": WORKSTREAM_ROOT / builder.VALIDATION_NAME,
            }
            for name, path in checked_paths.items():
                self.assertEqual(path.read_bytes(), result["files"][name], name)

    def test_output_is_disjoint_from_manual_biography_overlays(self) -> None:
        with self.temporary_output() as directory:
            result = builder.build_reproducibly(self.args_for(Path(directory)))
            claimed, snapshot = builder.load_existing_msgbre_claims(self.args_for(Path(directory)).progress)
            overlay = json.loads((Path(directory) / "public" / builder.OVERLAY_NAME).read_text(encoding="utf-8"))
            selected = {entry["id"] for entry in overlay["entries"]}
            self.assertEqual(snapshot["unique_claimed_count"], 836)
            self.assertTrue(snapshot["successors_excluded_from_prior_claims"])
            self.assertEqual(
                {item["path"] for item in builder.SUCCESSOR_OVERLAYS},
                {item["logical_path"] for item in snapshot["successor_overlays"]},
            )
            self.assertTrue(all(item["source_free"] for item in snapshot["successor_overlays"]))
            self.assertFalse(claimed.intersection(selected))
            self.assertEqual(len(selected), result["entry_count"])

    def test_generated_artifacts_are_source_script_free(self) -> None:
        with self.temporary_output() as directory:
            builder.build_reproducibly(self.args_for(Path(directory)))
            paths = [
                Path(directory) / "public" / builder.OVERLAY_NAME,
                Path(directory) / "evidence" / builder.EVIDENCE_NAME,
                Path(directory) / "review" / builder.REVIEW_NAME,
                Path(directory) / builder.VALIDATION_NAME,
            ]
            for path in paths:
                self.assertEqual(builder.script_counts(path.read_text(encoding="utf-8")), {"cjk_unified_count": 0, "kana_count": 0}, path.name)

    def test_inputs_are_unchanged_by_build(self) -> None:
        with self.temporary_output() as directory:
            args = self.args_for(Path(directory))
            before = builder.input_snapshot(args)
            post_registration = builder.build_reproducibly(args)
            self.assertEqual(builder.input_snapshot(args), before)
            progress = json.loads(args.progress.read_text(encoding="utf-8"))
            row = next(item for item in progress["resources"] if item["path"] == builder.RESOURCE)
            row["overlay_globs"] = [
                item for item in row["overlay_globs"] if item != builder.SELF_OVERLAY_PATH
            ]
            pre_progress = Path(directory) / "progress-before-self-registration.json"
            pre_progress.write_text(
                json.dumps(progress, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            pre_args = self.args_for(
                Path(directory) / "before-self-registration",
                progress=pre_progress,
            )
            pre_registration = builder.build_once(pre_args, pre_args.out_root)
            self.assertEqual(post_registration["files"], pre_registration["files"])

    def test_archive_pin_rejects_a_non_release_input(self) -> None:
        with self.temporary_output() as directory:
            bad = Path(directory) / "not-the-release.zip"
            bad.write_bytes(b"not a Switch patch archive")
            with self.assertRaises(builder.SwitchMsgbreImportError):
                builder.build_once(self.args_for(Path(directory) / "out", switch_zip=bad), Path(directory) / "out")


if __name__ == "__main__":
    unittest.main()
