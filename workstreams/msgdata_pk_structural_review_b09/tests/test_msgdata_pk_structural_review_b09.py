from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


WORKSTREAM_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = WORKSTREAM_ROOT.parents[1]
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_msgdata_pk_structural_review_b09 as batch  # noqa: E402


class MsgdataPkStructuralReviewB09Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay_path = WORKSTREAM_ROOT / "public" / batch.OVERLAY_NAME
        cls.evidence_path = WORKSTREAM_ROOT / "evidence" / batch.EVIDENCE_NAME
        cls.review_path = WORKSTREAM_ROOT / "review" / batch.REVIEW_NAME
        cls.validation_path = WORKSTREAM_ROOT / batch.VALIDATION_NAME
        cls.overlay = json.loads(cls.overlay_path.read_text(encoding="utf-8"))
        cls.validation = json.loads(cls.validation_path.read_text(encoding="utf-8"))
        cls.packed_sc, cls.tables = batch.previous.previous.load_tables(batch.GAME_ROOT)
        cls.targets = batch.previous.previous.previous.load_target_catalog(
            REPO_ROOT / batch.TARGET_CATALOG_RELATIVE
        )["ids"]
        cls.selected, cls.reasons, cls.predecessors, cls.owner_blobs = batch.validate_scope(
            cls.tables, cls.targets, REPO_ROOT
        )

    def test_b07_and_b08_are_explicit_hash_pinned_owners(self) -> None:
        expected = {
            batch.B07_OVERLAY_PATH: (batch.EXPECTED_B07_OVERLAY_SHA256, batch.previous.previous.EXPECTED_REVIEW_IDS_SHA256),
            batch.B08_OVERLAY_PATH: (batch.EXPECTED_B08_OVERLAY_SHA256, batch.previous.EXPECTED_REVIEW_IDS_SHA256),
        }
        all_ids = []
        for path, (blob_hash, ids_hash) in expected.items():
            overlay = json.loads(self.owner_blobs[path].decode("utf-8"))
            ids = [entry["id"] for entry in overlay["entries"]]
            with self.subTest(path=path):
                self.assertEqual(blob_hash, batch.sha256(self.owner_blobs[path]))
                self.assertEqual(500, len(ids))
                self.assertEqual(ids_hash, batch.hash_json(ids))
            all_ids.extend(ids)
        self.assertEqual(1000, len(set(all_ids)))
        self.assertTrue(set(all_ids).issubset(self.predecessors))

    def test_scope_is_third_500_and_leaves_2610(self) -> None:
        self.assertEqual(500, len(self.selected))
        self.assertEqual((19821, 20378), (self.selected[0], self.selected[-1]))
        self.assertEqual(batch.EXPECTED_REVIEW_IDS_SHA256, batch.hash_json(self.selected))
        self.assertEqual(22424, len(self.predecessors))
        self.assertFalse(set(self.selected) & self.predecessors)
        self.assertEqual(3110, len(self.targets - self.predecessors))
        self.assertEqual(2610, len(self.targets - self.predecessors - set(self.selected)))

    def test_all_500_rows_are_dummy_structural_placeholders(self) -> None:
        sc = self.tables["SC"].texts
        self.assertEqual({batch.REASON}, {self.reasons[entry_id] for entry_id in self.selected})
        for entry_id in self.selected:
            with self.subTest(entry_id=entry_id):
                self.assertEqual("dummy", sc[entry_id].strip().lower())
                self.assertEqual(0, sum(batch.previous.previous.previous.script_counts(sc[entry_id]).values()))

    def test_overlay_is_unique_reviewed_and_non_overlapping(self) -> None:
        resource, _stock, entries = batch.common.validate_overlay_shape(self.overlay)
        ids = [entry["id"] for entry in entries]
        self.assertEqual(batch.RESOURCE, resource)
        self.assertEqual(self.selected, ids)
        self.assertEqual(500, len(set(ids)))
        self.assertEqual({"reviewed"}, {entry["status"] for entry in entries})
        self.assertFalse(set(ids) & self.predecessors)

    def test_values_are_exact_sc_utf16le_byte_preservations(self) -> None:
        sc = self.tables["SC"].texts
        for entry in self.overlay["entries"]:
            source = sc[entry["id"]]
            with self.subTest(entry_id=entry["id"]):
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

    def test_progress_audit_accepts_all_ordered_registration_stages(self) -> None:
        source = json.loads((REPO_ROOT / batch.PROGRESS_RELATIVE).read_text(encoding="utf-8"))
        prefix = list(batch.previous.previous.EXPECTED_PREDECESSOR_PATHS)
        tails = (
            [], [batch.B07_OVERLAY_PATH], [batch.B07_OVERLAY_PATH, batch.B08_OVERLAY_PATH],
            [batch.B07_OVERLAY_PATH, batch.B08_OVERLAY_PATH, batch.SELF_OVERLAY_PATH],
        )
        results = []
        with tempfile.TemporaryDirectory(prefix="nobu16-msgdata-b09-progress-", dir=REPO_ROOT / "tmp") as directory:
            for index, tail in enumerate(tails):
                progress = json.loads(json.dumps(source))
                row = next(item for item in progress["resources"] if item["path"] == batch.RESOURCE)
                row["overlay_globs"] = prefix + tail
                path = Path(directory) / f"progress-{index}.json"
                path.write_bytes(batch.encode_json(progress))
                results.append(batch.audit_progress(
                    path, REPO_ROOT, self.owner_blobs, self.overlay_path.read_bytes(), self.targets,
                    self.predecessors, set(self.selected),
                ))
        self.assertEqual([0, 1, 1, 1], [row["b07_registration_count"] for row in results])
        self.assertEqual([0, 0, 1, 1], [row["b08_registration_count"] for row in results])
        self.assertEqual([0, 0, 0, 1], [row["self_registration_count"] for row in results])

    def test_public_artifacts_are_source_free_and_validation_is_safe(self) -> None:
        for path in (self.overlay_path, self.evidence_path, self.review_path, self.validation_path):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertEqual(0, sum(batch.previous.previous.previous.script_counts(text).values()))
                self.assertNotIn("\x00", text)
        self.assertTrue(self.validation["passed"])
        self.assertEqual(0, self.validation["scope"]["blocked_count"])
        self.assertEqual(0, self.validation["scope"]["narrative_mixed_count"])
        self.assertTrue(all(value is False for value in self.validation["safety"].values()))

    def test_in_memory_target_reconstruction_is_deterministic(self) -> None:
        first = batch.engine.upstream.reconstruct_sc_target(self.packed_sc, self.tables["SC"], self.overlay["entries"])
        second = batch.engine.upstream.reconstruct_sc_target(self.packed_sc, self.tables["SC"], self.overlay["entries"])
        self.assertEqual(first, second)
        self.assertEqual(self.validation["target_reconstruction"]["packed_sha256"], first["packed_sha256"])
        self.assertFalse(first["complete_target_included"])

    def test_reproducible_build_matches_checked_in_artifacts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="nobu16-msgdata-b09-build-", dir=REPO_ROOT / "tmp") as directory:
            result = batch.build_reproducibly(
                batch.GAME_ROOT, REPO_ROOT, REPO_ROOT / batch.TARGET_CATALOG_RELATIVE,
                REPO_ROOT / batch.PROGRESS_RELATIVE, Path(directory),
            )
            self.assertEqual((500, 500, 0, 2610), (
                result["reviewed_count"], result["preserve_count"], result["blocked_count"], result["remaining_count"]
            ))
            for relative, blob in result["files"].items():
                self.assertEqual((WORKSTREAM_ROOT / relative).read_bytes(), blob)


if __name__ == "__main__":
    unittest.main()
