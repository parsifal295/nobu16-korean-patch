from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import sys
import tempfile
import unittest


WORKSTREAM_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = WORKSTREAM_ROOT.parents[1]
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_switch_msgev_v13_invariant_recovery as batch  # noqa: E402


class SwitchMsgevV13InvariantRecoveryTests(unittest.TestCase):
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
        cls.sources = batch.strict.load_sources(
            batch.GAME_ROOT,
            batch.REPO_ROOT,
            batch.REPO_ROOT / batch.strict.SWITCH_ARCHIVE_RELATIVE,
        )

    def test_overlay_contract_hash_and_exact_partition_are_pinned(self) -> None:
        resource, stock, entries = batch.common.validate_overlay_shape(self.overlay)
        self.assertEqual(batch.RESOURCE, resource)
        self.assertEqual(batch.EXPECTED_SELECTED_COUNT, len(entries))
        self.assertEqual(batch.strict.upstream.SOURCE_PINS["pk_sc_stock"]["packed_sha256"], stock["packed_sha256"])
        ids = [entry["id"] for entry in entries]
        self.assertEqual(sorted(ids), ids)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(batch.EXPECTED_SELECTED_IDS_SHA256, batch.hash_json(ids))
        self.assertEqual(batch.EXPECTED_OVERLAY_SHA256, batch.sha256(self.overlay_path.read_bytes()))

        excluded = [entry["id"] for entry in self.review["exclusions"]]
        self.assertEqual(list(batch.EXPECTED_EXCLUDED_IDS), excluded)
        self.assertEqual(batch.EXPECTED_EXCLUDED_IDS_SHA256, batch.hash_json(excluded))
        self.assertFalse(set(ids) & set(excluded))
        residual = self.evidence["residual_pool"]
        self.assertEqual(batch.EXPECTED_RESIDUAL_COUNT, residual["residual_count"])
        self.assertEqual(batch.EXPECTED_RESIDUAL_IDS_SHA256, residual["residual_ids_sha256"])

    def test_selected_rows_are_target_members_and_disjoint_from_all_prior_owners(self) -> None:
        progress = batch.validate_progress_catalog(
            REPO_ROOT / batch.PROGRESS_RELATIVE, REPO_ROOT
        )
        target = batch.load_target_catalog(REPO_ROOT)
        selected = {entry["id"] for entry in self.overlay["entries"]}
        self.assertFalse(selected & progress["ids"])
        self.assertTrue(selected <= target["ids"])
        self.assertEqual(len(selected), self.evidence["selection"]["selected_target_catalog_intersection_count"])
        self.assertEqual(0, self.evidence["selection"]["selected_outside_target_count"])
        progress_json = json.loads(
            (REPO_ROOT / batch.PROGRESS_RELATIVE).read_text(encoding="utf-8")
        )
        progress_row = next(
            row for row in progress_json["resources"] if row["path"] == batch.RESOURCE
        )
        self.assertIn(
            batch.STRICT_OVERLAY_LOGICAL_PATH, progress_row["overlay_globs"]
        )

    def test_every_repair_preserves_visible_stream_structure_and_sc_invariants(self) -> None:
        stock = self.sources["pk_sc_stock"]["table"]
        evidence_by_id = {entry["id"]: entry for entry in self.evidence["entries"]}
        for overlay_entry in self.overlay["entries"]:
            entry_id = overlay_entry["id"]
            source_sc = stock.texts[entry_id]
            repaired = overlay_entry["ko"]
            evidence = evidence_by_id[entry_id]
            with self.subTest(entry_id=entry_id):
                self.assertEqual(
                    overlay_entry["source_sc_utf16le_sha256"],
                    batch.common.text_hash(source_sc),
                )
                self.assertEqual([], batch.common.invariant_mismatches(source_sc, repaired))
                self.assertEqual(
                    batch.strict.upstream.BRACKET_TOKEN_RE.findall(source_sc),
                    batch.strict.upstream.BRACKET_TOKEN_RE.findall(repaired),
                )
                self.assertFalse(batch.strict.upstream.contains_cjk_or_kana(repaired))
                self.assertTrue(batch.strict.upstream.has_meaningful_hangul(repaired))
                self.assertTrue(evidence["visible_stream_preserved"])
                self.assertTrue(evidence["word_boundary_order_preserved"])
                self.assertTrue(evidence["pk_sc_invariants_preserved"])
                self.assertTrue(evidence["custom_bracket_tokens_preserved"])

    def test_operation_classes_and_overlaps_are_exact(self) -> None:
        entries = self.evidence["entries"]
        operation_counts: Counter[str] = Counter()
        combination_counts: Counter[str] = Counter()
        for entry in entries:
            operation_counts.update(entry["operations"])
            combination_counts[entry["operation_combination"]] += 1
        self.assertEqual(batch.EXPECTED_OPERATION_CLASS_COUNTS, dict(operation_counts))
        self.assertEqual(batch.EXPECTED_OPERATION_COMBINATIONS, dict(combination_counts))

        classes = self.evidence["selection"]["exclusion_classes"]
        self.assertEqual(11, classes["esc_token_count_mismatch"]["count"])
        self.assertEqual(batch.ESC_COUNT_EXCLUSION_IDS_SHA256, classes["esc_token_count_mismatch"]["ids_sha256"])
        self.assertEqual(3, classes["custom_bracket_sequence_mismatch"]["count"])
        self.assertEqual(batch.BRACKET_EXCLUSION_IDS_SHA256, classes["custom_bracket_sequence_mismatch"]["ids_sha256"])
        self.assertEqual(1, classes["class_intersection"]["count"])
        self.assertEqual(batch.EXCLUSION_CLASS_OVERLAP_IDS_SHA256, classes["class_intersection"]["ids_sha256"])
        self.assertEqual(13, classes["class_union"]["count"])
        self.assertEqual(batch.EXPECTED_EXCLUDED_IDS_SHA256, classes["class_union"]["ids_sha256"])

    def test_gate_class_union_and_raw_predicate_overlap_are_honest(self) -> None:
        residual = self.evidence["residual_pool"]
        precedence = residual["upstream_precedence_gate_classes"]
        self.assertEqual(
            {
                "source_script": 4,
                "sc_invariant_after_source_script_gate": 257,
                "class_overlap_count": 0,
                "class_union_count": 261,
            },
            precedence,
        )
        raw = residual["raw_predicates_on_full_residual"]
        self.assertEqual(
            {
                "source_script_count": 4,
                "sc_invariant_mismatch_count": 261,
                "intersection_count": 4,
                "union_count": 261,
            },
            raw,
        )

    def test_switch_v13_text_identity_and_exact_japanese_mapping_are_recorded(self) -> None:
        identity = self.evidence["switch_text_identity"]
        self.assertTrue(identity["v13_is_byte_identical_to_v11"])
        self.assertEqual(identity["v13_member_packed_sha256"], identity["v11_member_packed_sha256"])
        self.assertEqual(identity["v13_member_raw_sha256"], identity["v11_member_raw_sha256"])
        for entry in self.evidence["entries"]:
            with self.subTest(entry_id=entry["id"]):
                self.assertTrue(entry["exact_japanese_hash_and_in_memory_equality"])
                self.assertTrue(entry["unique_meaningful_switch_korean"])
                self.assertEqual(entry["pk_jp_utf16le_sha256"], entry["base_jp_utf16le_sha256"])
                self.assertGreater(entry["base_jp_coordinate_count"], 0)

    def test_all_public_artifacts_are_source_free_and_safety_is_explicit(self) -> None:
        expected = {"han_or_kana_count": 0, "embedded_nul_count": 0}
        for path in (
            self.overlay_path,
            self.evidence_path,
            self.review_path,
            self.validation_path,
        ):
            with self.subTest(path=path.name):
                self.assertEqual(expected, batch.source_free_counts(path.read_bytes()))
        safety = self.validation["safety"]
        for key, value in safety.items():
            with self.subTest(key=key):
                self.assertFalse(value)
        self.assertTrue(self.validation["passed"])
        self.assertEqual(0, self.validation["replacement_invariants"]["failures"])
        self.assertEqual(0, self.validation["replacement_invariants"]["sentence_fragment_rearrangement_count"])
        self.assertEqual(0, self.validation["replacement_invariants"]["placeholder_rearrangement_count"])

    def test_reproducible_build_matches_checked_in_artifacts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="nobu16-msgev-test-") as directory:
            result = batch.build_reproducibly(
                batch.GAME_ROOT,
                batch.REPO_ROOT,
                batch.REPO_ROOT / batch.strict.SWITCH_ARCHIVE_RELATIVE,
                batch.REPO_ROOT / batch.PROGRESS_RELATIVE,
                Path(directory),
            )
            self.assertEqual(batch.EXPECTED_SELECTED_COUNT, result["entry_count"])
            for relative, blob in result["files"].items():
                self.assertEqual((WORKSTREAM_ROOT / relative).read_bytes(), blob)

    def test_pre_and_post_exact_self_registration_builds_are_byte_identical(self) -> None:
        progress = json.loads(
            (REPO_ROOT / batch.PROGRESS_RELATIVE).read_text(encoding="utf-8")
        )
        row = next(item for item in progress["resources"] if item["path"] == batch.RESOURCE)
        row["overlay_globs"] = [
            item
            for item in row["overlay_globs"]
            if item != batch.SELF_OVERLAY_LOGICAL_PATH
        ]
        pre = json.loads(json.dumps(progress))
        post = json.loads(json.dumps(progress))
        post_row = next(item for item in post["resources"] if item["path"] == batch.RESOURCE)
        post_row["overlay_globs"].append(batch.SELF_OVERLAY_LOGICAL_PATH)

        with tempfile.TemporaryDirectory(prefix="nobu16-msgev-registration-") as directory:
            root = Path(directory)
            pre_path = root / "pre.json"
            post_path = root / "post.json"
            pre_path.write_bytes(batch.encode_json(pre))
            post_path.write_bytes(batch.encode_json(post))
            pre_result = batch.build_once(
                batch.GAME_ROOT,
                batch.REPO_ROOT,
                batch.REPO_ROOT / batch.strict.SWITCH_ARCHIVE_RELATIVE,
                pre_path,
                root / "pre",
            )
            post_result = batch.build_once(
                batch.GAME_ROOT,
                batch.REPO_ROOT,
                batch.REPO_ROOT / batch.strict.SWITCH_ARCHIVE_RELATIVE,
                post_path,
                root / "post",
            )
            self.assertEqual(pre_result["files"], post_result["files"])


if __name__ == "__main__":
    unittest.main()
