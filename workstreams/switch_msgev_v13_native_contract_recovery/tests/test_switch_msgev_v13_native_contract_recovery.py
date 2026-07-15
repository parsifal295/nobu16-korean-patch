from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


WORKSTREAM_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = WORKSTREAM_ROOT.parents[1]
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_switch_msgev_v13_native_contract_recovery as batch  # noqa: E402


class SwitchMsgevV13NativeContractRecoveryTests(unittest.TestCase):
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
        cls.sources = batch.load_sources(
            batch.GAME_ROOT,
            batch.REPO_ROOT,
            batch.REPO_ROOT / batch.strict.SWITCH_ARCHIVE_RELATIVE,
        )

    def test_overlay_exact_set_shape_and_hash_are_pinned(self) -> None:
        resource, stock, entries = batch.common.validate_overlay_shape(self.overlay)
        self.assertEqual(batch.RESOURCE, resource)
        self.assertEqual(batch.EXPECTED_SELECTED_IDS_SHA256, batch.hash_json(batch.SELECTED_IDS))
        self.assertEqual(batch.SELECTED_IDS, [entry["id"] for entry in entries])
        self.assertEqual(len(batch.SELECTED_IDS), self.overlay["entry_count"])
        self.assertEqual(batch.SOURCE_PINS["SC"]["packed_sha256"], stock["packed_sha256"])
        self.assertEqual(batch.EXPECTED_OVERLAY_SHA256, batch.sha256(self.overlay_path.read_bytes()))

    def test_exact_predecessor_exclusion_partition_is_consumed(self) -> None:
        snapshot = batch.validate_predecessor_exclusions(REPO_ROOT)
        self.assertEqual(len(batch.SELECTED_IDS), snapshot["excluded_count"])
        self.assertEqual(batch.EXPECTED_SELECTED_IDS_SHA256, snapshot["excluded_ids_sha256"])
        self.assertTrue(snapshot["exact_partition_consumed"])
        self.assertTrue(self.evidence["scope"]["exact_predecessor_exclusion_partition"])

    def test_entries_are_exact_targets_and_disjoint_from_every_prior_overlay(self) -> None:
        target = batch.load_target_catalog(REPO_ROOT / batch.TARGET_CATALOG_RELATIVE)
        progress = batch.audit_progress_registration(
            REPO_ROOT / batch.PROGRESS_RELATIVE, REPO_ROOT, target["ids"]
        )
        selected = set(batch.SELECTED_IDS)
        self.assertTrue(selected <= target["ids"])
        self.assertFalse(selected & progress["ids"])
        self.assertEqual(0, progress["candidate_prior_overlap_count"])
        self.assertEqual(len(selected), progress["candidate_target_intersection_count"])
        self.assertEqual(0, progress["candidate_outside_target_count"])

    def test_every_native_translation_matches_the_pk_sc_runtime_contract(self) -> None:
        sc = self.sources["SC"]["table"].texts
        evidence_by_id = {entry["id"]: entry for entry in self.evidence["entries"]}
        for entry in self.overlay["entries"]:
            entry_id = entry["id"]
            translation = entry["ko"]
            source_sc = sc[entry_id]
            with self.subTest(entry_id=entry_id):
                self.assertEqual(entry["source_sc_utf16le_sha256"], batch.common.text_hash(source_sc))
                self.assertEqual([], batch.common.invariant_mismatches(source_sc, translation))
                self.assertEqual(
                    batch.BRACKET_TOKEN_RE.findall(source_sc),
                    batch.BRACKET_TOKEN_RE.findall(translation),
                )
                self.assertFalse(batch.strict.upstream.contains_cjk_or_kana(translation))
                self.assertIsNotNone(batch.HANGUL_RE.search(translation))
                self.assertTrue(evidence_by_id[entry_id]["native_reconstruction_completed"])
                self.assertFalse(evidence_by_id[entry_id]["switch_text_blindly_preserved"])
                self.assertTrue(evidence_by_id[entry_id]["pk_sc_invariants_preserved"])
                self.assertTrue(evidence_by_id[entry_id]["custom_bracket_tokens_preserved"])

    def test_switch_mapping_and_multilingual_hash_alignment_are_complete(self) -> None:
        evidence_by_id = {entry["id"]: entry for entry in self.evidence["entries"]}
        for entry_id in batch.SELECTED_IDS:
            switch_ko, coordinates, jp_hash = batch.switch_mapping_for_id(
                self.sources, entry_id
            )
            evidence = evidence_by_id[entry_id]
            with self.subTest(entry_id=entry_id):
                self.assertTrue(evidence["exact_switch_japanese_mapping"])
                self.assertTrue(evidence["unique_meaningful_switch_korean_draft"])
                self.assertEqual(
                    batch.common.text_hash(switch_ko),
                    evidence["switch_ko_before_utf16le_sha256"],
                )
                self.assertEqual(jp_hash, evidence["official_pk_utf16le_sha256"]["JP"])
                self.assertEqual(len(coordinates), evidence["base_jp_coordinate_count"])
                self.assertEqual(batch.hash_json(coordinates), evidence["base_jp_coordinate_ids_sha256"])
                for language in ("SC", "JP", "EN", "TC"):
                    self.assertEqual(
                        batch.common.text_hash(
                            self.sources[language]["table"].texts[entry_id]
                        ),
                        evidence["official_pk_utf16le_sha256"][language],
                    )

    def test_locale_rewrite_conflict_is_isolated_to_id_10888(self) -> None:
        conflicts = [
            entry["id"]
            for entry in self.evidence["entries"]
            if entry["jp_en_switch_semantic_conflict"]
        ]
        self.assertEqual([10_888], conflicts)
        special = next(entry for entry in self.evidence["entries"] if entry["id"] == 10_888)
        self.assertEqual("pk_sc_tc_locale_rewrite", special["semantic_basis"])
        self.assertEqual(
            "replace_incompatible_switch_dynamic_person_fragment",
            special["control_repair"],
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
                self.assertEqual(expected, batch.strict.source_free_counts(path.read_bytes()))
        self.assertTrue(self.validation["passed"])
        self.assertEqual(0, self.validation["replacement_invariants"]["failures"])
        self.assertEqual(0, self.validation["replacement_invariants"]["switch_text_blindly_preserved_count"])
        for key, value in self.validation["safety"].items():
            with self.subTest(safety=key):
                self.assertFalse(value)

    def test_reproducible_build_matches_checked_in_artifacts(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="nobu16-msgev-native-test-", dir=REPO_ROOT / "tmp"
        ) as directory:
            result = batch.build_reproducibly(
                batch.GAME_ROOT,
                batch.REPO_ROOT,
                batch.REPO_ROOT / batch.strict.SWITCH_ARCHIVE_RELATIVE,
                batch.REPO_ROOT / batch.TARGET_CATALOG_RELATIVE,
                batch.REPO_ROOT / batch.PROGRESS_RELATIVE,
                Path(directory),
            )
            self.assertEqual(len(batch.SELECTED_IDS), result["entry_count"])
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
            prefix="nobu16-msgev-native-registration-", dir=REPO_ROOT / "tmp"
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


if __name__ == "__main__":
    unittest.main()
