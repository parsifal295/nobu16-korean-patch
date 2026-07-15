from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


TEST_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = TEST_PATH.parents[1]
REPO_ROOT = TEST_PATH.parents[3]
GAME_ROOT = REPO_ROOT.parent
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(WORKSTREAM_ROOT))
sys.path.insert(0, str(TOOLS_ROOT))

import build_common_message_overlay as common  # noqa: E402
import build_ev_strdata_batch1 as shared  # noqa: E402
import build_ev_strdata_batch24 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": (
        "123C03144C29E307C65C95BD5D528FE53388511FE5FD587ADBE75401AEAF5D15"
    ),
    f"evidence/{batch.EVIDENCE_NAME}": (
        "D5919E30354DADA5D24B369B8D6841EC6BE05E2E0B976A6B7FD6BED3EE0E5549"
    ),
    f"review/{batch.REVIEW_NAME}": (
        "BBCA5B79688354570DE2215F50F25E426337FF7A6C3CEEAE5DBC2391EF0A2492"
    ),
    batch.VALIDATION_NAME: (
        "4100EBE167176A214056EA46E64D3CF6E6501213C28F64EC546683A755CAD972"
    ),
}
STOCK_AVAILABLE = all(
    (GAME_ROOT / "MSG" / language / "ev_strdata.bin").is_file()
    for language in shared.LANGUAGES
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load(relative: str) -> dict[str, object]:
    return json.loads(
        (WORKSTREAM_ROOT / relative).read_text(encoding="utf-8"),
        object_pairs_hook=common.strict_object,
    )


class EvStrDataBatch24Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = load(f"public/{batch.OVERLAY_NAME}")
        cls.evidence = load(f"evidence/{batch.EVIDENCE_NAME}")
        cls.review = load(f"review/{batch.REVIEW_NAME}")
        cls.validation = load(batch.VALIDATION_NAME)

    def test_overlay_contains_exact_194_historical_event_entries(self) -> None:
        ids = [int(entry["id"]) for entry in self.overlay["entries"]]
        self.assertEqual(list(range(4557, 4751)), ids)
        self.assertEqual(194, self.overlay["entry_count"])
        by_id = {int(entry["id"]): entry["ko"] for entry in self.overlay["entries"]}
        self.assertIn("\ub9c8\uc4f0\ub098\uac00 \ud788\uc0ac\ud788\ub370", by_id[4557])
        self.assertIn("\ud638\uc870 \uac00\ubb38", by_id[4570])
        self.assertIn("\uace0\uc18c\uc2a8 \uc0bc\uad6d\ub3d9\ub9f9", by_id[4592])
        self.assertIn("\uac00\uc2a4\uac00\uc57c\ub9c8\uc131", by_id[4610])
        self.assertIn("\uc18c\uace0 \uac00\uc988\ub9c8\uc0ac", by_id[4632])
        self.assertIn("\ub098\uac00\ub178 \ub098\ub9ac\ub9c8\uc0ac", by_id[4657])
        self.assertIn("\ub2e4\ucf00\ub2e4\uad70", by_id[4691])
        self.assertIn("\uc544\ub9c8\uce74\uc2a4 \uac00\uac8c\ubaa8\uce58", by_id[4720])

    def test_scope_has_no_non_display_exclusions(self) -> None:
        self.assertEqual(set(range(4557, 4751)), set(batch.TRANSLATIONS))
        self.assertEqual(frozenset(), batch.CURRENT_EXCLUDED_IDS)
        self.assertEqual(0, self.evidence["scope"]["deferred_internal_entry_count"])
        self.assertEqual(
            {
                "actor_reference": 0,
                "dummy_placeholder": 0,
                "empty_slot": 0,
                "internal_event_key": 0,
            },
            self.evidence["scope"]["excluded_candidate_counts"],
        )
        self.assertEqual(batch.DEFERRED_IDS_SHA256, shared.hash_json([]))
        self.assertEqual(4751, self.evidence["scope"]["next_display_id"])

    def test_all_prior_exclusion_sets_and_zero_overlap_are_pinned(self) -> None:
        overlap = self.evidence["previous_deferred_overlap"]
        self.assertEqual(
            [193, 199, 43, 96, 18, 0, 0, 0, 0, 0, 0],
            [item["deferred_entry_count"] for item in overlap["previous_batches"]],
        )
        self.assertEqual(549, overlap["previous_deferred_union_entry_count"])
        self.assertEqual(
            batch.PREVIOUS_DEFERRED_UNION_SHA256,
            overlap["previous_deferred_union_ids_sha256"],
        )
        self.assertEqual(0, overlap["current_deferred_entry_count"])
        self.assertEqual(0, overlap["overlap_entry_count"])
        self.assertEqual(batch.DEFERRED_IDS_SHA256, overlap["overlap_ids_sha256"])
        self.assertFalse(overlap["overlap_detected"])
        self.assertEqual(overlap, self.review["previous_deferred_overlap"])

    def test_event_classification_counts_are_pinned(self) -> None:
        self.assertEqual(batch.CLASS_COUNTS, self.evidence["scope"]["functional_class_counts"])
        actual = {name: 0 for name in batch.CLASS_COUNTS}
        for entry in self.evidence["entries"]:
            actual[entry["classification"]] += 1
        self.assertEqual(batch.CLASS_COUNTS, actual)

    def test_repeated_sc_sources_use_one_korean_translation(self) -> None:
        policy = self.validation["repeated_source_policy"]
        self.assertTrue(policy["same_source_same_translation_required"])
        self.assertEqual(190, policy["translated_unique_source_hash_count"])
        self.assertEqual(3, policy["translated_repeated_source_group_count"])
        self.assertEqual(
            [[4659, 4693], [4722, 4729], [4728, 4736, 4741]],
            policy["repeated_source_id_groups"],
        )
        self.assertEqual(0, policy["failures"])
        by_id = {int(entry["id"]): entry["ko"] for entry in self.overlay["entries"]}
        for group in policy["repeated_source_id_groups"]:
            self.assertEqual(1, len({by_id[int(entry_id)] for entry_id in group}))

    def test_related_msgev_reuse_and_sc_adjustments_are_recorded(self) -> None:
        related = self.evidence["related_msgev_review"]
        self.assertEqual(194, related["same_numeric_id_semantic_reviewed_entry_count"])
        self.assertTrue(related["terminology_cross_checked"])
        self.assertTrue(related["direct_translation_reuse"])
        self.assertEqual(194, related["source_free_reused_entry_count"])
        self.assertEqual(0, related["sc_structure_adjusted_entry_count"])
        self.assertEqual([], related["ev_strdata_sc_structure_differs_at_ids"])
        self.assertTrue(related["ev_strdata_sc_structure_is_authoritative"])
        self.assertEqual(related, self.review["related_msgev_review"])

    def test_review_marks_layout_and_selected_historical_terms(self) -> None:
        self.assertEqual(194, len(self.review["entries"]))
        self.assertEqual(18, self.review["terminology_review_count"])
        flagged = set()
        for entry in self.review["entries"]:
            self.assertTrue(entry["human_review_required"])
            self.assertFalse(entry["runtime_reviewed"])
            self.assertIn("event_text_runtime_layout", entry["uncertainty_flags"])
            if "historical_term_or_reading_review" in entry["uncertainty_flags"]:
                flagged.add(int(entry["id"]))
        self.assertEqual(set(batch.TERMINOLOGY_REVIEW_IDS), flagged)

    def test_overlay_is_source_free_common_message_contract(self) -> None:
        original_allowlist = common.ALLOWED_RESOURCES
        common.ALLOWED_RESOURCES = original_allowlist | shared.SUPPORTED_RESOURCES
        try:
            resource, stock, entries = common.validate_overlay_shape(self.overlay)
        finally:
            common.ALLOWED_RESOURCES = original_allowlist
        self.assertEqual(shared.RESOURCE, resource)
        self.assertEqual(shared.STRING_COUNT, stock["string_count"])
        self.assertEqual(194, len(entries))
        self.assertFalse(self.overlay["distribution_policy"]["contains_commercial_source_text"])

    def test_alignment_and_translation_hash_sets_are_pinned(self) -> None:
        alignment = self.validation["source_alignment"]
        self.assertEqual(["SC", "JP", "TC"], alignment["languages"])
        self.assertFalse(alignment["english_reference_available"])
        self.assertTrue(alignment["traditional_chinese_used_as_third_reference"])
        self.assertEqual(582, alignment["translated_reference_hash_count"])
        self.assertEqual(194, alignment["translated_ids_nonempty_in_all_references"])
        self.assertEqual(batch.SOURCE_SC_HASHES_SHA256, alignment["ordered_sc_source_hashes_sha256"])
        self.assertEqual(batch.ALL_REFERENCE_HASHES_SHA256, alignment["ordered_all_reference_hashes_sha256"])
        self.assertEqual(batch.TRANSLATION_MAP_SHA256, self.validation["translation"]["translation_map_sha256"])

    def test_v024_generated_files_are_pinned_and_source_free(self) -> None:
        for relative, expected_hash in EXPECTED_HASHES.items():
            path = WORKSTREAM_ROOT / relative
            with self.subTest(relative=relative):
                self.assertEqual(expected_hash, digest(path))
                self.assertEqual(
                    {"han_or_kana_count": 0, "embedded_nul_count": 0},
                    shared.source_free_counts(path.read_bytes()),
                )

    def test_exactly_seven_new_batch_files_are_source_free(self) -> None:
        paths = (
            WORKSTREAM_ROOT / "build_ev_strdata_batch24.py",
            WORKSTREAM_ROOT / "BATCH24_V0.24_README_KO.md",
            WORKSTREAM_ROOT / "public" / batch.OVERLAY_NAME,
            WORKSTREAM_ROOT / "evidence" / batch.EVIDENCE_NAME,
            WORKSTREAM_ROOT / "review" / batch.REVIEW_NAME,
            WORKSTREAM_ROOT / batch.VALIDATION_NAME,
            WORKSTREAM_ROOT / "tests" / "test_ev_strdata_batch24.py",
        )
        self.assertEqual(7, len(paths))
        for path in paths:
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())
                self.assertEqual(
                    {"han_or_kana_count": 0, "embedded_nul_count": 0},
                    shared.source_free_counts(path.read_bytes()),
                )

    def test_validation_records_determinism_invariants_and_file_only_safety(self) -> None:
        self.assertTrue(self.validation["passed"])
        self.assertEqual(194, self.validation["replacement_invariants"]["checked"])
        self.assertEqual(0, self.validation["replacement_invariants"]["failures"])
        self.assertEqual(
            ["isolated_a", "isolated_b", "final"],
            self.validation["reproducibility"]["required_runs"],
        )
        self.assertEqual(193, self.validation["offline_binary_build"]["operations"])
        self.assertEqual(194, self.validation["offline_binary_build"]["overlay_entries"])
        self.assertFalse(self.validation["offline_binary_build"]["installed_target_written"])
        self.assertEqual(
            ["SC", "JP", "TC"],
            self.validation["raw_format"]["raw_parse_rebuild_byte_exact_languages"],
        )
        for key, value in self.validation["safety"].items():
            with self.subTest(key=key):
                self.assertFalse(value)

    @unittest.skipUnless(STOCK_AVAILABLE, "installed SC/JP/TC stock resources are unavailable")
    def test_stock_replay_is_deterministic_and_install_is_unchanged(self) -> None:
        source_paths = [
            GAME_ROOT / "MSG" / language / "ev_strdata.bin"
            for language in shared.LANGUAGES
        ]
        before = {path: digest(path) for path in source_paths}
        loaded, _ = shared.load_sources(GAME_ROOT)
        ids = sorted(batch.TRANSLATIONS)
        source_sc_hashes = [
            common.text_hash(loaded["SC"]["table"].texts[entry_id])
            for entry_id in ids
        ]
        all_reference_hashes = [
            common.text_hash(loaded[language]["table"].texts[entry_id])
            for entry_id in ids
            for language in shared.LANGUAGES
        ]
        self.assertEqual(batch.SOURCE_SC_HASHES_SHA256, shared.hash_json(source_sc_hashes))
        self.assertEqual(batch.ALL_REFERENCE_HASHES_SHA256, shared.hash_json(all_reference_hashes))
        for language in shared.LANGUAGES:
            self.assertEqual(
                batch.NEXT_DISPLAY_REFERENCE_HASHES[language],
                common.text_hash(loaded[language]["table"].texts[4751]),
            )
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr24-test-") as temporary:
            result = batch.build_reproducibly(GAME_ROOT, Path(temporary))
            self.assertEqual(194, result["entry_count"])
            self.assertEqual(194, result["inspected_count"])
            self.assertEqual(0, result["deferred_count"])
            self.assertEqual(4751, result["next_display_id"])
            self.assertEqual(
                EXPECTED_HASHES,
                {
                    relative: hashlib.sha256(blob).hexdigest().upper()
                    for relative, blob in result["files"].items()
                },
            )
        after = {path: digest(path) for path in source_paths}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
