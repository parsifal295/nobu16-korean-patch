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

import build_msgdata_pk_structural_review_b10 as batch  # noqa: E402


class MsgdataPkStructuralReviewB10Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay_path = WORKSTREAM_ROOT / "public" / batch.OVERLAY_NAME
        cls.evidence_path = WORKSTREAM_ROOT / "evidence" / batch.EVIDENCE_NAME
        cls.review_path = WORKSTREAM_ROOT / "review" / batch.REVIEW_NAME
        cls.validation_path = WORKSTREAM_ROOT / batch.VALIDATION_NAME
        cls.overlay = json.loads(cls.overlay_path.read_text(encoding="utf-8"))
        cls.validation = json.loads(cls.validation_path.read_text(encoding="utf-8"))
        cls.packed_sc, cls.tables = batch.previous.previous.previous.load_tables(batch.GAME_ROOT)
        cls.targets = batch.previous.previous.previous.previous.load_target_catalog(
            REPO_ROOT / batch.TARGET_CATALOG_RELATIVE
        )["ids"]
        cls.selected, cls.reasons, cls.groups, cls.predecessors, cls.owner_blobs = batch.validate_scope(
            cls.tables, cls.targets, REPO_ROOT
        )

    def test_three_explicit_predecessor_overlays_own_1500_unique_ids(self) -> None:
        expected_hashes = {
            batch.B07_OVERLAY_PATH: batch.EXPECTED_B07_OVERLAY_SHA256,
            batch.B08_OVERLAY_PATH: batch.EXPECTED_B08_OVERLAY_SHA256,
            batch.B09_OVERLAY_PATH: batch.EXPECTED_B09_OVERLAY_SHA256,
        }
        ids = []
        for path, expected_hash in expected_hashes.items():
            overlay = json.loads(self.owner_blobs[path].decode("utf-8"))
            current = [entry["id"] for entry in overlay["entries"]]
            with self.subTest(path=path):
                self.assertEqual(expected_hash, batch.sha256(self.owner_blobs[path]))
                self.assertEqual(500, len(current))
            ids.extend(current)
        self.assertEqual(1500, len(set(ids)))
        self.assertTrue(set(ids).issubset(self.predecessors))

    def test_scope_is_fourth_500_and_leaves_2110(self) -> None:
        self.assertEqual(500, len(self.selected))
        self.assertEqual((20379, 24743), (self.selected[0], self.selected[-1]))
        self.assertEqual(batch.EXPECTED_REVIEW_IDS_SHA256, batch.hash_json(self.selected))
        self.assertEqual(22924, len(self.predecessors))
        self.assertFalse(set(self.selected) & self.predecessors)
        self.assertEqual(2610, len(self.targets - self.predecessors))
        self.assertEqual(2110, len(self.targets - self.predecessors - set(self.selected)))

    def test_reason_partition_is_complete_and_pinned(self) -> None:
        expected = {reason: pin["count"] for reason, pin in batch.REASON_PINS.items()}
        self.assertEqual(expected, {reason: len(ids) for reason, ids in self.groups.items()})
        self.assertEqual(500, sum(expected.values()))
        for reason, ids in self.groups.items():
            self.assertEqual(batch.REASON_PINS[reason]["ids_sha256"], batch.hash_json(list(ids)))

    def test_structural_shapes_exclude_narrative_or_source_script(self) -> None:
        sc = self.tables["SC"].texts
        script_counts = batch.previous.previous.previous.previous.script_counts
        for entry_id in self.selected:
            value = sc[entry_id]
            reason = self.reasons[entry_id]
            with self.subTest(entry_id=entry_id, reason=reason):
                self.assertEqual(0, sum(script_counts(value).values()))
                self.assertNotIn("\x00", value)
                if reason == "placeholder_dummy_not_a_translatable_display_message":
                    self.assertEqual("dummy", value.strip().lower())
                elif reason == "romanized_or_phonetic_lookup_key":
                    self.assertTrue(re.fullmatch(r"[A-Za-z0-9_%+_.-]+", value.strip()))
                else:
                    self.assertFalse(batch.engine.has_semantic_alphanumeric(value))

    def test_overlay_is_unique_reviewed_and_byte_preserved(self) -> None:
        resource, _stock, entries = batch.common.validate_overlay_shape(self.overlay)
        ids = [entry["id"] for entry in entries]
        self.assertEqual(batch.RESOURCE, resource)
        self.assertEqual(self.selected, ids)
        self.assertEqual(500, len(set(ids)))
        self.assertEqual({"reviewed"}, {entry["status"] for entry in entries})
        self.assertFalse(set(ids) & self.predecessors)
        sc = self.tables["SC"].texts
        for entry in entries:
            source = sc[entry["id"]]
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

    def test_progress_audit_accepts_five_ordered_registration_stages(self) -> None:
        source = json.loads((REPO_ROOT / batch.PROGRESS_RELATIVE).read_text(encoding="utf-8"))
        prefix = list(batch.previous.previous.previous.EXPECTED_PREDECESSOR_PATHS)
        chain = [batch.B07_OVERLAY_PATH, batch.B08_OVERLAY_PATH, batch.B09_OVERLAY_PATH, batch.SELF_OVERLAY_PATH]
        results = []
        with tempfile.TemporaryDirectory(prefix="nobu16-msgdata-b10-progress-", dir=REPO_ROOT / "tmp") as directory:
            for index in range(5):
                progress = json.loads(json.dumps(source))
                row = next(item for item in progress["resources"] if item["path"] == batch.RESOURCE)
                row["overlay_globs"] = prefix + chain[:index]
                path = Path(directory) / f"progress-{index}.json"
                path.write_bytes(batch.encode_json(progress))
                results.append(batch.audit_progress(
                    path, REPO_ROOT, self.owner_blobs, self.overlay_path.read_bytes(), self.targets,
                    self.predecessors, set(self.selected),
                ))
        self.assertEqual([0, 1, 1, 1, 1], [row["b07_registration_count"] for row in results])
        self.assertEqual([0, 0, 1, 1, 1], [row["b08_registration_count"] for row in results])
        self.assertEqual([0, 0, 0, 1, 1], [row["b09_registration_count"] for row in results])
        self.assertEqual([0, 0, 0, 0, 1], [row["self_registration_count"] for row in results])

    def test_public_artifacts_are_source_free_and_validation_is_safe(self) -> None:
        script_counts = batch.previous.previous.previous.previous.script_counts
        for path in (self.overlay_path, self.evidence_path, self.review_path, self.validation_path):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertEqual(0, sum(script_counts(text).values()))
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
        with tempfile.TemporaryDirectory(prefix="nobu16-msgdata-b10-build-", dir=REPO_ROOT / "tmp") as directory:
            result = batch.build_reproducibly(
                batch.GAME_ROOT, REPO_ROOT, REPO_ROOT / batch.TARGET_CATALOG_RELATIVE,
                REPO_ROOT / batch.PROGRESS_RELATIVE, Path(directory),
            )
            self.assertEqual((500, 500, 0, 2110), (
                result["reviewed_count"], result["preserve_count"], result["blocked_count"], result["remaining_count"]
            ))
            for relative, blob in result["files"].items():
                self.assertEqual((WORKSTREAM_ROOT / relative).read_bytes(), blob)


if __name__ == "__main__":
    unittest.main()
