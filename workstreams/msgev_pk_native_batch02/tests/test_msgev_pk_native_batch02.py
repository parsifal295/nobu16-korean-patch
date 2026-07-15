from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


WORKSTREAM_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = WORKSTREAM_ROOT.parents[1]
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_msgev_pk_native_batch02 as batch  # noqa: E402


class MsgevPkNativeBatch02Tests(unittest.TestCase):
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

    def test_selection_is_the_first_150_safe_lexical_gap_rows(self) -> None:
        target = batch.batch01.load_target_catalog(
            REPO_ROOT / batch.TARGET_CATALOG_RELATIVE, REPO_ROOT
        )
        progress = batch.audit_progress_registration(
            REPO_ROOT / batch.PROGRESS_RELATIVE, REPO_ROOT, target["ids"]
        )
        gaps = sorted(target["ids"] - progress["ids"])
        lexical = [
            entry_id
            for entry_id in gaps
            if entry_id not in batch.batch01.EXCLUDED_IDS
            and batch._has_letter_or_number(
                batch._remove_runtime_tokens(
                    self.sources["SC"]["table"].texts[entry_id]
                )
            )
        ]
        self.assertEqual(150, len(batch.SELECTED_IDS))
        self.assertEqual(batch.SELECTED_IDS, lexical[:150])
        self.assertEqual(
            batch.EXPECTED_SELECTED_IDS_SHA256,
            batch.hash_json(batch.SELECTED_IDS),
        )

    def test_candidate_selected_and_excluded_partitions_are_exact(self) -> None:
        self.assertFalse(set(batch.SELECTED_IDS) & set(batch.EXCLUDED_IDS))
        self.assertEqual(
            set(batch.CANDIDATE_IDS),
            set(batch.SELECTED_IDS) | set(batch.EXCLUDED_IDS),
        )
        self.assertEqual(284, len(batch.CANDIDATE_IDS))
        self.assertEqual(150, self.evidence["scope"]["translated_count"])
        self.assertEqual(134, self.evidence["scope"]["excluded_count"])
        self.assertEqual(9, self.evidence["scope"]["switch_semantic_reuse_count"])
        self.assertEqual(141, self.evidence["scope"]["pk_native_translation_count"])

    def test_overlay_shape_hash_target_membership_and_disjointness(self) -> None:
        resource, stock, entries = batch.common.validate_overlay_shape(self.overlay)
        self.assertEqual(batch.RESOURCE, resource)
        self.assertEqual(batch.SELECTED_IDS, [entry["id"] for entry in entries])
        self.assertEqual(
            batch.EXPECTED_OVERLAY_SHA256,
            batch.sha256(self.overlay_path.read_bytes()),
        )
        self.assertEqual(
            batch.base.SOURCE_PINS["SC"]["packed_sha256"], stock["packed_sha256"]
        )
        target = batch.batch01.load_target_catalog(
            REPO_ROOT / batch.TARGET_CATALOG_RELATIVE, REPO_ROOT
        )
        progress = batch.audit_progress_registration(
            REPO_ROOT / batch.PROGRESS_RELATIVE, REPO_ROOT, target["ids"]
        )
        selected = set(batch.SELECTED_IDS)
        self.assertTrue(selected <= target["ids"])
        self.assertFalse(selected & progress["ids"])
        self.assertEqual(0, progress["selected_predecessor_overlap_count"])
        self.assertEqual(0, progress["selected_outside_target_count"])

    def test_all_translations_preserve_the_exact_pk_sc_runtime_contract(self) -> None:
        sc = self.sources["SC"]["table"].texts
        evidence = {
            entry["id"]: entry
            for entry in self.evidence["entries"]
            if entry["status"] == "translated"
        }
        for entry in self.overlay["entries"]:
            entry_id = entry["id"]
            source = sc[entry_id]
            translation = entry["ko"]
            with self.subTest(entry_id=entry_id):
                self.assertEqual(
                    entry["source_sc_utf16le_sha256"], batch.common.text_hash(source)
                )
                self.assertEqual([], batch.common.invariant_mismatches(source, translation))
                self.assertEqual(
                    batch.base.BRACKET_TOKEN_RE.findall(source),
                    batch.base.BRACKET_TOKEN_RE.findall(translation),
                )
                self.assertFalse(batch.strict.upstream.contains_cjk_or_kana(translation))
                self.assertIsNotNone(batch.HANGUL_RE.search(translation))
                self.assertTrue(evidence[entry_id]["pk_sc_invariants_preserved"])
                self.assertTrue(evidence[entry_id]["custom_bracket_tokens_preserved"])

    def test_translation_provenance_partition_is_revalidated(self) -> None:
        evidence = {
            entry["id"]: entry
            for entry in self.evidence["entries"]
            if entry["status"] == "translated"
        }
        buckets = batch.strict.exact_jp_buckets(
            {
                "pk_jp": self.sources["JP"],
                "base_jp": self.sources["base_jp"],
                "switch_ko": self.sources["switch_ko"],
            }
        )
        for entry_id in batch.SWITCH_SEMANTIC_REUSE_IDS:
            with self.subTest(switch_semantic_reuse=entry_id):
                self.assertEqual(
                    "switch_same_index_semantic_reuse",
                    evidence[entry_id]["translation_kind"],
                )
                self.assertEqual(
                    batch.common.text_hash(
                        self.sources["base_jp"]["table"].texts[entry_id]
                    ),
                    evidence[entry_id]["switch_same_index_jp_utf16le_sha256"],
                )
                self.assertEqual(
                    batch.common.text_hash(
                        self.sources["switch_ko"]["table"].texts[entry_id]
                    ),
                    evidence[entry_id]["switch_same_index_ko_utf16le_sha256"],
                )
        for entry_id in batch.PK_NATIVE_IDS:
            with self.subTest(pk_native=entry_id):
                jp = self.sources["JP"]["table"].texts[entry_id]
                exact = [
                    row
                    for row in buckets.get(batch.common.text_hash(jp), [])
                    if row["jp"] == jp
                ]
                self.assertEqual([], exact)
                self.assertEqual(
                    "pk_native_event_translation",
                    evidence[entry_id]["translation_kind"],
                )

    def test_every_exclusion_is_structurally_revalidated_and_unclaimed(self) -> None:
        reasons = batch.exclusion_reason_by_id()
        evidence = {
            entry["id"]: entry
            for entry in self.evidence["entries"]
            if entry["status"] == "excluded"
        }
        self.assertEqual(batch.EXCLUDED_IDS, sorted(reasons))
        self.assertEqual(batch.EXCLUDED_IDS, sorted(evidence))
        for entry_id, reason in reasons.items():
            with self.subTest(entry_id=entry_id, reason=reason):
                batch.validate_exclusion_shape(entry_id, reason, self.sources)
                self.assertEqual(reason, evidence[entry_id]["exclusion_reason"])
                self.assertTrue(evidence[entry_id]["preserve_stock_value"])
                self.assertFalse(evidence[entry_id]["overlay_claim_created"])
                self.assertNotIn(entry_id, batch.SELECTED_IDS)

    def test_multilingual_source_hashes_are_complete_without_source_text(self) -> None:
        evidence = {entry["id"]: entry for entry in self.evidence["entries"]}
        for entry_id in batch.CANDIDATE_IDS:
            hashes = evidence[entry_id]["official_pk_utf16le_sha256"]
            self.assertEqual({"SC", "JP", "EN", "TC"}, set(hashes))
            for language in ("SC", "JP", "EN", "TC"):
                with self.subTest(entry_id=entry_id, language=language):
                    self.assertEqual(
                        batch.common.text_hash(
                            self.sources[language]["table"].texts[entry_id]
                        ),
                        hashes[language],
                    )

    def test_public_artifacts_are_source_free_and_safety_is_explicit(self) -> None:
        expected = {"han_or_kana_count": 0, "embedded_nul_count": 0}
        for path in (
            self.overlay_path,
            self.evidence_path,
            self.review_path,
            self.validation_path,
        ):
            with self.subTest(path=path.name):
                self.assertEqual(
                    expected, batch.strict.source_free_counts(path.read_bytes())
                )
        self.assertTrue(self.validation["passed"])
        self.assertEqual(0, self.validation["replacement_invariants"]["failures"])
        for key, value in self.validation["safety"].items():
            with self.subTest(safety=key):
                self.assertFalse(value)

    def test_reproducible_build_matches_checked_in_artifacts(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="nobu16-msgev-b02-test-", dir=REPO_ROOT / "tmp"
        ) as directory:
            result = batch.build_reproducibly(
                batch.GAME_ROOT,
                batch.REPO_ROOT,
                batch.REPO_ROOT / batch.strict.SWITCH_ARCHIVE_RELATIVE,
                batch.REPO_ROOT / batch.TARGET_CATALOG_RELATIVE,
                batch.REPO_ROOT / batch.PROGRESS_RELATIVE,
                Path(directory),
            )
            self.assertEqual(284, result["candidate_count"])
            self.assertEqual(150, result["entry_count"])
            self.assertEqual(134, result["excluded_count"])
            for relative, blob in result["files"].items():
                self.assertEqual((WORKSTREAM_ROOT / relative).read_bytes(), blob)

    def test_pre_and_post_exact_self_registration_builds_are_byte_identical(self) -> None:
        progress = json.loads(
            (REPO_ROOT / batch.PROGRESS_RELATIVE).read_text(encoding="utf-8")
        )
        row = next(item for item in progress["resources"] if item["path"] == batch.RESOURCE)
        row["overlay_globs"] = [
            item for item in row["overlay_globs"] if item != batch.SELF_OVERLAY_PATH
        ]
        pre = json.loads(json.dumps(progress))
        post = json.loads(json.dumps(progress))
        post_row = next(item for item in post["resources"] if item["path"] == batch.RESOURCE)
        post_row["overlay_globs"].append(batch.SELF_OVERLAY_PATH)

        with tempfile.TemporaryDirectory(
            prefix="nobu16-msgev-b02-registration-", dir=REPO_ROOT / "tmp"
        ) as directory:
            root = Path(directory)
            pre_path = root / "pre.json"
            post_path = root / "post.json"
            pre_path.write_bytes(batch.encode_json(pre))
            post_path.write_bytes(batch.encode_json(post))
            pre_result = batch.build_once(
                batch.GAME_ROOT,
                batch.REPO_ROOT,
                batch.REPO_ROOT / batch.strict.SWITCH_ARCHIVE_RELATIVE,
                batch.REPO_ROOT / batch.TARGET_CATALOG_RELATIVE,
                pre_path,
                root / "pre",
            )
            post_result = batch.build_once(
                batch.GAME_ROOT,
                batch.REPO_ROOT,
                batch.REPO_ROOT / batch.strict.SWITCH_ARCHIVE_RELATIVE,
                batch.REPO_ROOT / batch.TARGET_CATALOG_RELATIVE,
                post_path,
                root / "post",
            )
            self.assertEqual(pre_result["files"], post_result["files"])
            self.assertEqual(pre_result["target"], post_result["target"])

    def test_valid_successor_registration_does_not_change_predecessor_selection(self) -> None:
        target = batch.batch01.load_target_catalog(
            REPO_ROOT / batch.TARGET_CATALOG_RELATIVE, REPO_ROOT
        )
        baseline = batch.audit_progress_registration(
            REPO_ROOT / batch.PROGRESS_RELATIVE, REPO_ROOT, target["ids"]
        )
        progress = json.loads(
            (REPO_ROOT / batch.PROGRESS_RELATIVE).read_text(encoding="utf-8")
        )
        row = next(item for item in progress["resources"] if item["path"] == batch.RESOURCE)
        row["overlay_globs"] = [
            item for item in row["overlay_globs"] if item != batch.SELF_OVERLAY_PATH
        ]
        with tempfile.TemporaryDirectory(
            prefix="nobu16-msgev-b02-successor-", dir=REPO_ROOT / "tmp"
        ) as directory:
            root = Path(directory)
            successor_path = root / "successor.json"
            logical = successor_path.relative_to(REPO_ROOT).as_posix()
            successor = json.loads(json.dumps(self.overlay))
            successor["overlay_id"] = "msgev-pk-native-successor-test.v1"
            successor["entry_count"] = 1
            successor["entries"] = [
                {
                    "id": 9_938,
                    "source_sc_utf16le_sha256": batch.common.text_hash(
                        self.sources["SC"]["table"].texts[9_938]
                    ),
                    "ko": "후속 등록 검증",
                }
            ]
            successor_path.write_bytes(batch.encode_json(successor))
            row["overlay_globs"].append(logical)
            progress_path = root / "progress.json"
            progress_path.write_bytes(batch.encode_json(progress))
            observed = batch.audit_progress_registration(
                progress_path, REPO_ROOT, target["ids"]
            )
            self.assertEqual(baseline, observed)


if __name__ == "__main__":
    unittest.main()

