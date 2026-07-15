from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


WORKSTREAM_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = WORKSTREAM_ROOT.parents[1]
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_msgev_pk_structural_completion_b07 as batch  # noqa: E402


class MsgevPkStructuralCompletionB07Tests(unittest.TestCase):
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
        cls.sources = batch.base.load_sources(
            batch.GAME_ROOT,
            batch.REPO_ROOT,
            batch.REPO_ROOT / batch.strict.SWITCH_ARCHIVE_RELATIVE,
        )

    def test_partition_covers_all_241_remaining_target_rows(self) -> None:
        reasons = batch.validate_partition(self.sources)
        self.assertEqual(241, len(batch.EXPECTED_IDS))
        self.assertEqual(batch.EXPECTED_IDS, sorted(reasons))
        self.assertEqual(219, len(batch.PRESERVE_IDS))
        self.assertEqual(22, len(batch.DYNAMIC_IDS))
        self.assertFalse(set(batch.PRESERVE_IDS) & set(batch.DYNAMIC_IDS))
        self.assertEqual(
            batch.EXPECTED_IDS,
            sorted(batch.PRESERVE_IDS + batch.DYNAMIC_IDS),
        )

    def test_overlay_is_reviewed_source_free_and_pinned(self) -> None:
        resource, _stock, entries = batch.common.validate_overlay_shape(self.overlay)
        self.assertEqual(batch.RESOURCE, resource)
        self.assertEqual("reviewed", self.overlay["defaults"]["status"])
        self.assertEqual(batch.EXPECTED_IDS, [entry["id"] for entry in entries])
        self.assertEqual({"reviewed"}, {entry["status"] for entry in entries})
        self.assertEqual(
            batch.EXPECTED_OVERLAY_SHA256,
            batch.sha256(self.overlay_path.read_bytes()),
        )
        self.assertEqual(
            {"han_or_kana_count": 0, "embedded_nul_count": 0},
            batch.strict.source_free_counts(self.overlay_path.read_bytes()),
        )

    def test_219_structural_values_are_exact_byte_preservations(self) -> None:
        sc = self.sources["SC"]["table"].texts
        entries = {entry["id"]: entry["ko"] for entry in self.overlay["entries"]}
        for entry_id in batch.PRESERVE_IDS:
            with self.subTest(entry_id=entry_id):
                self.assertEqual(sc[entry_id], entries[entry_id])
                self.assertFalse(batch.strict.upstream.contains_cjk_or_kana(entries[entry_id]))

    def test_22_dynamic_narratives_are_korean_and_preserve_runtime_contract(self) -> None:
        sc = self.sources["SC"]["table"].texts
        entries = {entry["id"]: entry["ko"] for entry in self.overlay["entries"]}
        for entry_id in batch.DYNAMIC_IDS:
            replacement = entries[entry_id]
            with self.subTest(entry_id=entry_id):
                self.assertEqual(batch.DYNAMIC_TRANSLATIONS[entry_id], replacement)
                self.assertNotEqual(sc[entry_id], replacement)
                self.assertFalse(batch.strict.upstream.contains_cjk_or_kana(replacement))
                self.assertEqual([], batch.common.invariant_mismatches(sc[entry_id], replacement))
                self.assertEqual(
                    batch.base.BRACKET_TOKEN_RE.findall(sc[entry_id]),
                    batch.base.BRACKET_TOKEN_RE.findall(replacement),
                )

    def test_every_source_hash_matches_the_pinned_sc_table(self) -> None:
        sc = self.sources["SC"]["table"].texts
        for entry in self.overlay["entries"]:
            self.assertEqual(
                batch.common.text_hash(sc[entry["id"]]),
                entry["source_sc_utf16le_sha256"],
            )

    def test_reason_catalog_has_nine_complete_classes(self) -> None:
        summary = self.evidence["reason_summary"]
        self.assertEqual(9, len(summary))
        self.assertEqual(241, sum(row["count"] for row in summary.values()))
        self.assertEqual(20, summary["runtime_custom_bracket_substitution"]["count"])
        self.assertEqual(2, summary["dynamic_substitution_token_manual_runtime_risk"]["count"])

    def test_progress_audit_closes_the_exact_target_catalog(self) -> None:
        audit = self.evidence["progress_audit"]
        self.assertEqual(12_665, audit["predecessor_target_count"])
        self.assertEqual(241, audit["pre_completion_gap_count"])
        self.assertEqual(12_906, audit["post_completion_target_count"])
        self.assertEqual(0, audit["post_completion_gap_count"])

    def test_absent_and_exact_self_registration_are_both_accepted(self) -> None:
        target = batch.previous.batch01.load_target_catalog(
            REPO_ROOT / batch.TARGET_CATALOG_RELATIVE, REPO_ROOT
        )
        overlay_blob = self.overlay_path.read_bytes()
        baseline = batch.audit_progress(
            REPO_ROOT / batch.PROGRESS_RELATIVE,
            REPO_ROOT,
            target["ids"],
            overlay_blob,
        )
        progress = json.loads(
            (REPO_ROOT / batch.PROGRESS_RELATIVE).read_text(encoding="utf-8")
        )
        row = next(item for item in progress["resources"] if item["path"] == batch.RESOURCE)
        if batch.SELF_OVERLAY_PATH not in row["overlay_globs"]:
            row["overlay_globs"].append(batch.SELF_OVERLAY_PATH)
        with tempfile.TemporaryDirectory(
            prefix="nobu16-msgev-b07-self-", dir=REPO_ROOT / "tmp"
        ) as directory:
            progress_path = Path(directory) / "progress.json"
            progress_path.write_bytes(batch.encode_json(progress))
            registered = batch.audit_progress(
                progress_path, REPO_ROOT, target["ids"], overlay_blob
            )
        self.assertEqual(0, baseline["self_registration_count"])
        self.assertEqual(1, registered["self_registration_count"])
        baseline.pop("self_registration_count")
        registered.pop("self_registration_count")
        self.assertEqual(baseline, registered)

    def test_public_evidence_review_and_validation_contain_no_source_script(self) -> None:
        expected = {"han_or_kana_count": 0, "embedded_nul_count": 0}
        for path in (
            self.evidence_path,
            self.review_path,
            self.validation_path,
        ):
            with self.subTest(path=path.name):
                self.assertEqual(expected, batch.strict.source_free_counts(path.read_bytes()))

    def test_validation_reports_zero_blocked_and_no_unsafe_mechanisms(self) -> None:
        self.assertTrue(self.validation["passed"])
        self.assertEqual(0, self.validation["scope"]["blocked_count"])
        self.assertEqual(0, self.review["blocked_count"])
        self.assertEqual(0, self.validation["replacement_invariants"]["failures"])
        self.assertTrue(all(value is False for value in self.validation["safety"].values()))

    def test_in_memory_target_is_deterministic_and_not_published(self) -> None:
        entries = self.overlay["entries"]
        first = batch.base.reconstruct_target(self.sources, entries)
        second = batch.base.reconstruct_target(self.sources, entries)
        self.assertEqual(first, second)
        self.assertEqual(
            self.validation["target_reconstruction"]["packed_sha256"],
            first["packed_sha256"],
        )
        self.assertFalse(first["complete_target_included"])

    def test_reproducible_build_matches_checked_in_artifacts(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="nobu16-msgev-b07-build-", dir=REPO_ROOT / "tmp"
        ) as directory:
            result = batch.build_reproducibly(
                batch.GAME_ROOT,
                batch.REPO_ROOT,
                batch.REPO_ROOT / batch.strict.SWITCH_ARCHIVE_RELATIVE,
                batch.REPO_ROOT / batch.TARGET_CATALOG_RELATIVE,
                batch.REPO_ROOT / batch.PROGRESS_RELATIVE,
                Path(directory),
            )
            self.assertEqual(241, result["reviewed_count"])
            self.assertEqual(219, result["preserve_count"])
            self.assertEqual(22, result["dynamic_count"])
            self.assertEqual(0, result["blocked_count"])
            for relative, blob in result["files"].items():
                self.assertEqual((WORKSTREAM_ROOT / relative).read_bytes(), blob)


if __name__ == "__main__":
    unittest.main()
