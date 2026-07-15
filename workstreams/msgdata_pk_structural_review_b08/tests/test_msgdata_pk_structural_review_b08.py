from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


WORKSTREAM_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = WORKSTREAM_ROOT.parents[1]
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_msgdata_pk_structural_review_b08 as batch  # noqa: E402


class MsgdataPkStructuralReviewB08Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay_path = WORKSTREAM_ROOT / "public" / batch.OVERLAY_NAME
        cls.evidence_path = WORKSTREAM_ROOT / "evidence" / batch.EVIDENCE_NAME
        cls.review_path = WORKSTREAM_ROOT / "review" / batch.REVIEW_NAME
        cls.validation_path = WORKSTREAM_ROOT / batch.VALIDATION_NAME
        cls.overlay = json.loads(cls.overlay_path.read_text(encoding="utf-8"))
        cls.evidence = json.loads(cls.evidence_path.read_text(encoding="utf-8"))
        cls.review = json.loads(cls.review_path.read_text(encoding="utf-8"))
        cls.validation = json.loads(cls.validation_path.read_text(encoding="utf-8"))
        cls.packed_sc, cls.tables = batch.previous.load_tables(batch.GAME_ROOT)
        cls.targets = batch.previous.previous.load_target_catalog(
            REPO_ROOT / batch.TARGET_CATALOG_RELATIVE
        )["ids"]
        (
            cls.selected,
            cls.reason_by_id,
            cls.groups,
            cls.predecessor_claims,
            cls.b07_blob,
        ) = batch.validate_scope(cls.tables, cls.targets, REPO_ROOT)

    def test_b07_is_an_explicit_hash_pinned_predecessor(self) -> None:
        blob, ids = batch.load_b07_claims(REPO_ROOT)
        self.assertEqual(batch.EXPECTED_B07_OVERLAY_SHA256, batch.sha256(blob))
        self.assertEqual(500, len(ids))
        self.assertEqual(batch.previous.EXPECTED_REVIEW_IDS_SHA256, batch.hash_json(ids))
        self.assertTrue(set(ids).issubset(self.predecessor_claims))

    def test_scope_is_exact_next_500_and_leaves_3110(self) -> None:
        self.assertEqual(500, len(self.selected))
        self.assertEqual((19199, 19820), (self.selected[0], self.selected[-1]))
        self.assertEqual(batch.EXPECTED_REVIEW_IDS_SHA256, batch.hash_json(self.selected))
        self.assertEqual(21924, len(self.predecessor_claims))
        self.assertFalse(set(self.selected) & self.predecessor_claims)
        self.assertEqual(3610, len(self.targets - self.predecessor_claims))
        self.assertEqual(3110, len(self.targets - self.predecessor_claims - set(self.selected)))

    def test_reason_partition_is_complete_and_pinned(self) -> None:
        expected = {
            "placeholder_dummy_not_a_translatable_display_message": 487,
            "romanized_or_phonetic_lookup_key": 13,
        }
        self.assertEqual(expected, {key: len(value) for key, value in self.groups.items()})
        self.assertEqual(500, sum(expected.values()))
        for reason, ids in self.groups.items():
            self.assertEqual(batch.REASON_PINS[reason]["ids_sha256"], batch.hash_json(list(ids)))

    def test_overlay_is_reviewed_unique_and_non_overlapping(self) -> None:
        resource, _stock, entries = batch.common.validate_overlay_shape(self.overlay)
        ids = [entry["id"] for entry in entries]
        self.assertEqual(batch.RESOURCE, resource)
        self.assertEqual(self.selected, ids)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual({"reviewed"}, {entry["status"] for entry in entries})
        self.assertFalse(set(ids) & self.predecessor_claims)

    def test_all_values_are_exact_sc_utf16le_preservations(self) -> None:
        sc = self.tables["SC"].texts
        for entry in self.overlay["entries"]:
            source = sc[entry["id"]]
            with self.subTest(entry_id=entry["id"]):
                self.assertEqual(source.encode("utf-16le"), entry["ko"].encode("utf-16le"))
                self.assertEqual(batch.common.text_hash(source), entry["source_sc_utf16le_sha256"])
                self.assertEqual(0, sum(batch.previous.previous.script_counts(entry["ko"]).values()))
                self.assertNotIn("\x00", entry["ko"])

    def test_structural_shapes_exclude_mixed_narrative(self) -> None:
        sc = self.tables["SC"].texts
        for entry_id in self.selected:
            value = sc[entry_id]
            reason = self.reason_by_id[entry_id]
            with self.subTest(entry_id=entry_id, reason=reason):
                if reason == "placeholder_dummy_not_a_translatable_display_message":
                    self.assertEqual("dummy", value.strip().lower())
                else:
                    self.assertRegex(value.strip(), r"^[a-z0-9_]+$")

    def test_four_language_selected_rowsets_are_pinned(self) -> None:
        actual = {
            language: batch.hash_json([
                {"id": entry_id, "utf16le_sha256": batch.common.text_hash(table.texts[entry_id])}
                for entry_id in self.selected
            ])
            for language, table in self.tables.items()
        }
        self.assertEqual(batch.OFFICIAL_ROWSET_SHA256, actual)

    def test_progress_audit_accepts_absent_b07_only_or_b07_and_b08(self) -> None:
        source = json.loads((REPO_ROOT / batch.PROGRESS_RELATIVE).read_text(encoding="utf-8"))
        row = next(item for item in source["resources"] if item["path"] == batch.RESOURCE)
        prefix = list(batch.previous.EXPECTED_PREDECESSOR_PATHS)
        results = []
        with tempfile.TemporaryDirectory(prefix="nobu16-msgdata-b08-progress-", dir=REPO_ROOT / "tmp") as directory:
            for index, tail in enumerate(([], [batch.B07_OVERLAY_PATH], [batch.B07_OVERLAY_PATH, batch.SELF_OVERLAY_PATH])):
                progress = json.loads(json.dumps(source))
                target_row = next(item for item in progress["resources"] if item["path"] == batch.RESOURCE)
                target_row["overlay_globs"] = prefix + tail
                path = Path(directory) / f"progress-{index}.json"
                path.write_bytes(batch.encode_json(progress))
                results.append(batch.audit_progress(
                    path, REPO_ROOT, self.b07_blob, self.overlay_path.read_bytes(), self.targets,
                    self.predecessor_claims, set(self.selected),
                ))
        self.assertEqual([0, 1, 1], [row["b07_registration_count"] for row in results])
        self.assertEqual([0, 0, 1], [row["self_registration_count"] for row in results])
        for row in results:
            row.pop("b07_registration_count")
            row.pop("self_registration_count")
        self.assertEqual(results[0], results[1])
        self.assertEqual(results[1], results[2])

    def test_public_artifacts_and_validation_are_source_free_and_safe(self) -> None:
        for path in (self.overlay_path, self.evidence_path, self.review_path, self.validation_path):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertEqual(0, sum(batch.previous.previous.script_counts(text).values()))
                self.assertNotIn("\x00", text)
        self.assertTrue(self.validation["passed"])
        self.assertEqual(0, self.validation["scope"]["blocked_count"])
        self.assertEqual(0, self.validation["scope"]["narrative_mixed_count"])
        self.assertTrue(all(value is False for value in self.validation["safety"].values()))

    def test_reconstruction_and_artifact_build_are_deterministic(self) -> None:
        first = batch.engine.upstream.reconstruct_sc_target(self.packed_sc, self.tables["SC"], self.overlay["entries"])
        second = batch.engine.upstream.reconstruct_sc_target(self.packed_sc, self.tables["SC"], self.overlay["entries"])
        self.assertEqual(first, second)
        self.assertEqual(self.validation["target_reconstruction"]["packed_sha256"], first["packed_sha256"])
        with tempfile.TemporaryDirectory(prefix="nobu16-msgdata-b08-build-", dir=REPO_ROOT / "tmp") as directory:
            result = batch.build_reproducibly(
                batch.GAME_ROOT, REPO_ROOT, REPO_ROOT / batch.TARGET_CATALOG_RELATIVE,
                REPO_ROOT / batch.PROGRESS_RELATIVE, Path(directory),
            )
            self.assertEqual((500, 500, 0, 3110), (
                result["reviewed_count"], result["preserve_count"], result["blocked_count"], result["remaining_count"]
            ))
            for relative, blob in result["files"].items():
                self.assertEqual((WORKSTREAM_ROOT / relative).read_bytes(), blob)


if __name__ == "__main__":
    unittest.main()
