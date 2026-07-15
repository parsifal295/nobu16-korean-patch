from __future__ import annotations

import json
from pathlib import Path
import re
import sys
import tempfile
import unittest


WORKSTREAM_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = WORKSTREAM_ROOT.parents[1]
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_msgdata_pk_structural_review_b13 as batch  # noqa: E402


class MsgdataPkStructuralReviewB13Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay_path = WORKSTREAM_ROOT / "public" / batch.OVERLAY_NAME
        cls.evidence_path = WORKSTREAM_ROOT / "evidence" / batch.EVIDENCE_NAME
        cls.review_path = WORKSTREAM_ROOT / "review" / batch.REVIEW_NAME
        cls.validation_path = WORKSTREAM_ROOT / batch.VALIDATION_NAME
        cls.overlay = json.loads(cls.overlay_path.read_text(encoding="utf-8"))
        cls.validation = json.loads(cls.validation_path.read_text(encoding="utf-8"))
        cls.packed_sc, cls.tables = batch.previous.previous.previous.previous.previous.previous.load_tables(batch.GAME_ROOT)
        cls.targets = batch.previous.previous.previous.previous.previous.previous.previous.load_target_catalog(
            REPO_ROOT / batch.TARGET_CATALOG_RELATIVE
        )["ids"]
        cls.selected, cls.reasons, cls.predecessors, cls.owner_blobs = batch.validate_scope(
            cls.tables, cls.targets, REPO_ROOT
        )

    def test_six_explicit_predecessors_own_3000_unique_ids(self) -> None:
        self.assertEqual(set(batch.OWNER_PATHS), set(self.owner_blobs))
        ids = []
        for path in batch.OWNER_PATHS:
            overlay = json.loads(self.owner_blobs[path].decode("utf-8"))
            current = [entry["id"] for entry in overlay["entries"]]
            self.assertEqual(500, len(current), path)
            ids.extend(current)
        self.assertEqual(3000, len(set(ids)))
        self.assertTrue(set(ids).issubset(self.predecessors))
        self.assertEqual(batch.EXPECTED_B12_OVERLAY_SHA256, batch.sha256(self.owner_blobs[batch.previous.SELF_OVERLAY_PATH]))

    def test_b12_is_the_direct_predecessor(self) -> None:
        blob, ids = batch.load_b12_owner(REPO_ROOT)
        self.assertEqual(batch.EXPECTED_B12_OVERLAY_SHA256, batch.sha256(blob))
        self.assertEqual(500, len(ids))
        self.assertEqual(batch.previous.EXPECTED_REVIEW_IDS_SHA256, batch.hash_json(ids))
        self.assertTrue(set(ids).issubset(self.predecessors))

    def test_scope_is_seventh_500_and_leaves_610(self) -> None:
        self.assertEqual((27494, 28042), (self.selected[0], self.selected[-1]))
        self.assertEqual(500, len(self.selected))
        self.assertEqual(batch.EXPECTED_REVIEW_IDS_SHA256, batch.hash_json(self.selected))
        self.assertEqual(24424, len(self.predecessors))
        self.assertFalse(set(self.selected) & self.predecessors)
        self.assertEqual(1110, len(self.targets - self.predecessors))
        self.assertEqual(610, len(self.targets - self.predecessors - set(self.selected)))

    def test_all_rows_are_restricted_ascii_lookup_keys(self) -> None:
        sc = self.tables["SC"].texts
        self.assertEqual({batch.REASON}, {self.reasons[entry_id] for entry_id in self.selected})
        for entry_id in self.selected:
            value = sc[entry_id]
            self.assertTrue(re.fullmatch(r"[A-Za-z0-9_%+_.-]+", value.strip()), entry_id)
            self.assertEqual(0, sum(batch.script_counts(value).values()), entry_id)
            self.assertNotIn("\x00", value, entry_id)

    def test_overlay_is_reviewed_unique_nonoverlapping_and_byte_preserved(self) -> None:
        resource, _stock, entries = batch.common.validate_overlay_shape(self.overlay)
        ids = [entry["id"] for entry in entries]
        self.assertEqual(batch.RESOURCE, resource)
        self.assertEqual(self.selected, ids)
        self.assertEqual(500, len(set(ids)))
        self.assertEqual({"reviewed"}, {entry["status"] for entry in entries})
        self.assertFalse(set(ids) & self.predecessors)
        for entry in entries:
            source = self.tables["SC"].texts[entry["id"]]
            self.assertEqual(source.encode("utf-16le"), entry["ko"].encode("utf-16le"))
            self.assertEqual(batch.common.text_hash(source), entry["source_sc_utf16le_sha256"])

    def test_four_language_selected_rowsets_are_pinned(self) -> None:
        actual = {
            language: batch.hash_json([
                {"id": entry_id, "utf16le_sha256": batch.common.text_hash(table.texts[entry_id])}
                for entry_id in self.selected
            ])
            for language, table in self.tables.items()
        }
        self.assertEqual(batch.OFFICIAL_ROWSET_SHA256, actual)

    def test_historical_self_and_future_registration_are_byte_stable(self) -> None:
        source_progress = json.loads((REPO_ROOT / batch.PROGRESS_RELATIVE).read_text(encoding="utf-8"))
        prefix = list(batch.previous.previous.previous.previous.previous.previous.EXPECTED_PREDECESSOR_PATHS)
        self_path = batch.SELF_OVERLAY_PATH
        successor = "workstreams/msgdata_pk_structural_review_b14/public/msgdata_ko_pk_structural_review_b14_500.v1.json"
        checked = {relative: (WORKSTREAM_ROOT / relative).read_bytes() for relative in (
            f"public/{batch.OVERLAY_NAME}", f"evidence/{batch.EVIDENCE_NAME}",
            f"review/{batch.REVIEW_NAME}", batch.VALIDATION_NAME,
        )}
        tails = (
            list(batch.OWNER_PATHS[:-1]), list(batch.OWNER_PATHS),
            list(batch.OWNER_PATHS) + [self_path], list(batch.OWNER_PATHS) + [self_path, successor],
        )
        with tempfile.TemporaryDirectory(prefix="nobu16-msgdata-b13-history-", dir=REPO_ROOT / "tmp") as directory:
            fake_repo = Path(directory)
            for path, blob in self.owner_blobs.items():
                target = fake_repo / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(blob)
            self_target = fake_repo / self_path
            self_target.parent.mkdir(parents=True, exist_ok=True)
            self_target.write_bytes(self.overlay_path.read_bytes())
            successor_target = fake_repo / successor
            successor_target.parent.mkdir(parents=True, exist_ok=True)
            successor_target.write_bytes(b"registered-successor-placeholder")
            for index, tail in enumerate(tails):
                progress = json.loads(json.dumps(source_progress))
                row = next(item for item in progress["resources"] if item["path"] == batch.RESOURCE)
                row["overlay_globs"] = prefix + tail
                progress_path = fake_repo / f"progress-{index}.json"
                progress_path.write_bytes(batch.encode_json(progress))
                rebuilt = batch.make_files(
                    batch.GAME_ROOT, fake_repo, REPO_ROOT / batch.TARGET_CATALOG_RELATIVE, progress_path
                )
                self.assertEqual(checked, rebuilt)

    def test_public_artifacts_are_source_free_and_safe(self) -> None:
        for path in (self.overlay_path, self.evidence_path, self.review_path, self.validation_path):
            text = path.read_text(encoding="utf-8")
            self.assertEqual(0, sum(batch.script_counts(text).values()), path.name)
            self.assertNotIn("\x00", text, path.name)
        self.assertTrue(self.validation["passed"])
        self.assertEqual(0, self.validation["scope"]["blocked_count"])
        self.assertTrue(self.validation["reproducibility"]["self_and_successor_registration_stable"])
        self.assertTrue(all(value is False for value in self.validation["safety"].values()))

    def test_target_reconstruction_is_deterministic(self) -> None:
        first = batch.engine.upstream.reconstruct_sc_target(self.packed_sc, self.tables["SC"], self.overlay["entries"])
        second = batch.engine.upstream.reconstruct_sc_target(self.packed_sc, self.tables["SC"], self.overlay["entries"])
        self.assertEqual(first, second)
        self.assertEqual(self.validation["target_reconstruction"]["packed_sha256"], first["packed_sha256"])
        self.assertFalse(first["complete_target_included"])

    def test_reproducible_build_matches_checked_in_artifacts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="nobu16-msgdata-b13-build-", dir=REPO_ROOT / "tmp") as directory:
            result = batch.build_reproducibly(
                batch.GAME_ROOT, REPO_ROOT, REPO_ROOT / batch.TARGET_CATALOG_RELATIVE,
                REPO_ROOT / batch.PROGRESS_RELATIVE, Path(directory),
            )
            self.assertEqual((500, 500, 0, 610), (
                result["reviewed_count"], result["preserve_count"], result["blocked_count"], result["remaining_count"]
            ))
            for relative, blob in result["files"].items():
                self.assertEqual((WORKSTREAM_ROOT / relative).read_bytes(), blob)


if __name__ == "__main__":
    unittest.main()
