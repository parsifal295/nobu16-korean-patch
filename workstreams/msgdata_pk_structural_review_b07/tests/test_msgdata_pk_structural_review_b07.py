from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


WORKSTREAM_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = WORKSTREAM_ROOT.parents[1]
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_msgdata_pk_structural_review_b07 as batch  # noqa: E402


class MsgdataPkStructuralReviewB07Tests(unittest.TestCase):
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
        cls.packed_sc, cls.tables = batch.load_tables(batch.GAME_ROOT)
        cls.targets = batch.previous.load_target_catalog(
            REPO_ROOT / batch.TARGET_CATALOG_RELATIVE
        )["ids"]
        (
            cls.selected,
            cls.reason_by_id,
            cls.selected_groups,
            cls.predecessor_claims,
        ) = batch.validate_scope(cls.tables, cls.targets)

    def test_scope_is_exact_first_500_of_the_structural_gap(self) -> None:
        self.assertEqual(500, len(self.selected))
        self.assertEqual((6651, 19198), (self.selected[0], self.selected[-1]))
        self.assertEqual(
            batch.EXPECTED_REVIEW_IDS_SHA256, batch.hash_json(self.selected)
        )
        self.assertFalse(set(self.selected) & self.predecessor_claims)
        self.assertEqual(4110, len(self.targets - self.predecessor_claims))
        self.assertEqual(3610, len(self.targets - self.predecessor_claims - set(self.selected)))

    def test_reason_partition_is_complete_and_pinned(self) -> None:
        expected_counts = {
            "placeholder_dummy_not_a_translatable_display_message": 439,
            "romanized_or_phonetic_lookup_key": 58,
            "format_or_control_only_token": 3,
        }
        self.assertEqual(expected_counts, {key: len(value) for key, value in self.selected_groups.items()})
        self.assertTrue(set(self.selected).issubset(self.reason_by_id))
        self.assertEqual(4110, len(self.reason_by_id))
        self.assertEqual(500, sum(expected_counts.values()))

    def test_overlay_is_reviewed_unique_and_non_overlapping(self) -> None:
        resource, _stock, entries = batch.common.validate_overlay_shape(self.overlay)
        ids = [entry["id"] for entry in entries]
        self.assertEqual(batch.RESOURCE, resource)
        self.assertEqual(self.selected, ids)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual({"reviewed"}, {entry["status"] for entry in entries})
        self.assertFalse(set(ids) & self.predecessor_claims)

    def test_every_value_is_exact_sc_utf16le_byte_preservation(self) -> None:
        sc = self.tables["SC"].texts
        for entry in self.overlay["entries"]:
            source = sc[entry["id"]]
            with self.subTest(entry_id=entry["id"]):
                self.assertEqual(source.encode("utf-16le"), entry["ko"].encode("utf-16le"))
                self.assertEqual(batch.common.text_hash(source), entry["source_sc_utf16le_sha256"])
                self.assertEqual(0, sum(batch.previous.script_counts(entry["ko"]).values()))
                self.assertNotIn("\x00", entry["ko"])

    def test_structural_shapes_exclude_semantic_narrative(self) -> None:
        sc = self.tables["SC"].texts
        for entry_id in self.selected:
            value = sc[entry_id]
            reason = self.reason_by_id[entry_id]
            with self.subTest(entry_id=entry_id, reason=reason):
                if reason == "placeholder_dummy_not_a_translatable_display_message":
                    self.assertEqual("dummy", value.strip().lower())
                elif reason == "romanized_or_phonetic_lookup_key":
                    self.assertRegex(value.strip(), r"^[a-z0-9_]+$")
                else:
                    self.assertFalse(batch.engine.has_semantic_alphanumeric(value))

    def test_official_four_language_rowsets_are_pinned(self) -> None:
        actual = {
            language: batch.hash_json([
                {"id": entry_id, "utf16le_sha256": batch.common.text_hash(table.texts[entry_id])}
                for entry_id in self.selected
            ])
            for language, table in self.tables.items()
        }
        self.assertEqual(batch.OFFICIAL_ROWSET_SHA256, actual)

    def test_progress_audit_accepts_absent_or_exact_self_registration(self) -> None:
        overlay_blob = self.overlay_path.read_bytes()
        baseline = batch.audit_progress(
            REPO_ROOT / batch.PROGRESS_RELATIVE,
            REPO_ROOT,
            overlay_blob,
            self.targets,
            self.predecessor_claims,
            set(self.selected),
        )
        progress = json.loads((REPO_ROOT / batch.PROGRESS_RELATIVE).read_text(encoding="utf-8"))
        row = next(item for item in progress["resources"] if item["path"] == batch.RESOURCE)
        if batch.SELF_OVERLAY_PATH not in row["overlay_globs"]:
            row["overlay_globs"].append(batch.SELF_OVERLAY_PATH)
        with tempfile.TemporaryDirectory(prefix="nobu16-msgdata-b07-progress-", dir=REPO_ROOT / "tmp") as directory:
            progress_path = Path(directory) / "progress.json"
            progress_path.write_bytes(batch.encode_json(progress))
            registered = batch.audit_progress(
                progress_path,
                REPO_ROOT,
                overlay_blob,
                self.targets,
                self.predecessor_claims,
                set(self.selected),
            )
        self.assertIn(baseline["self_registration_count"], (0, 1))
        self.assertEqual(1, registered["self_registration_count"])
        baseline.pop("self_registration_count")
        registered.pop("self_registration_count")
        self.assertEqual(baseline, registered)

    def test_public_artifacts_are_source_free_and_validation_is_safe(self) -> None:
        for path in (self.overlay_path, self.evidence_path, self.review_path, self.validation_path):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertEqual(0, sum(batch.previous.script_counts(text).values()))
                self.assertNotIn("\x00", text)
        self.assertTrue(self.validation["passed"])
        self.assertEqual(0, self.validation["scope"]["blocked_count"])
        self.assertEqual(0, self.validation["scope"]["narrative_mixed_count"])
        self.assertTrue(all(value is False for value in self.validation["safety"].values()))

    def test_in_memory_target_reconstruction_is_deterministic(self) -> None:
        entries = self.overlay["entries"]
        first = batch.engine.upstream.reconstruct_sc_target(self.packed_sc, self.tables["SC"], entries)
        second = batch.engine.upstream.reconstruct_sc_target(self.packed_sc, self.tables["SC"], entries)
        self.assertEqual(first, second)
        self.assertEqual(self.validation["target_reconstruction"]["packed_sha256"], first["packed_sha256"])
        self.assertFalse(first["complete_target_included"])

    def test_reproducible_build_matches_all_checked_in_artifacts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="nobu16-msgdata-b07-build-", dir=REPO_ROOT / "tmp") as directory:
            result = batch.build_reproducibly(
                batch.GAME_ROOT,
                batch.REPO_ROOT,
                batch.REPO_ROOT / batch.TARGET_CATALOG_RELATIVE,
                batch.REPO_ROOT / batch.PROGRESS_RELATIVE,
                Path(directory),
            )
            self.assertEqual(500, result["reviewed_count"])
            self.assertEqual(500, result["preserve_count"])
            self.assertEqual(0, result["blocked_count"])
            self.assertEqual(3610, result["remaining_count"])
            for relative, blob in result["files"].items():
                self.assertEqual((WORKSTREAM_ROOT / relative).read_bytes(), blob)


if __name__ == "__main__":
    unittest.main()
