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
import build_ev_strdata_batch22 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": (
        "F8EFBF4F6253D531C8F8D94117AD185E58855800A32C0A08BF664DBBDAB021DA"
    ),
    f"evidence/{batch.EVIDENCE_NAME}": (
        "AE941BEFE00488DAFBDD20242026921552FFAE5AC7599FB35539A01BC8AF604E"
    ),
    f"review/{batch.REVIEW_NAME}": (
        "FCE1530A21DCF808278A615D21C7FF6A3F19D867177FF35602329157B682D72B"
    ),
    batch.VALIDATION_NAME: (
        "0B96FE5F42A7CCE80A12FF2A6DD37FFDAAC853E6A51D3039AAE04BAE455F8B2A"
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


class EvStrDataBatch22Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = load(f"public/{batch.OVERLAY_NAME}")
        cls.evidence = load(f"evidence/{batch.EVIDENCE_NAME}")
        cls.review = load(f"review/{batch.REVIEW_NAME}")
        cls.validation = load(batch.VALIDATION_NAME)

    def test_overlay_contains_exact_177_historical_event_entries(self) -> None:
        ids = [int(entry["id"]) for entry in self.overlay["entries"]]
        self.assertEqual(list(range(4210, 4387)), ids)
        self.assertEqual(177, self.overlay["entry_count"])
        by_id = {int(entry["id"]): entry["ko"] for entry in self.overlay["entries"]}
        self.assertIn("\ub2e4\uc774\uac90 \uc14b\uc0ac\uc774", by_id[4210])
        self.assertIn("\uae30\uc694\uc2a4\uc131", by_id[4231])
        self.assertIn("\ubbf8\ub178 \uc0ac\uc774\ud1a0 \uac00\ubb38", by_id[4236])
        self.assertIn("\uc57c\ucfe0\uc624 \uc18c\ucf04", by_id[4250])
        self.assertIn("\uac00\uc2a4\uac00\uc57c\ub9c8\uc131", by_id[4280])
        self.assertIn("\uc624\ub2e4 \uac04\uc8fc\ub85c \ub178\ubd80\uce74\uc4f0", by_id[4315])
        self.assertIn("\uc624\uc6b0\uce58 \uac00\ubb38", by_id[4358])
        self.assertIn("\ub3c4\uc2dc\uc774\uc5d0", by_id[4386])

    def test_scope_has_no_non_display_exclusions(self) -> None:
        self.assertEqual(set(range(4210, 4387)), set(batch.TRANSLATIONS))
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
        self.assertEqual(4387, self.evidence["scope"]["next_display_id"])

    def test_all_prior_exclusion_sets_and_zero_overlap_are_pinned(self) -> None:
        overlap = self.evidence["previous_deferred_overlap"]
        self.assertEqual(
            [193, 199, 43, 96, 18, 0, 0, 0, 0],
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

    def test_all_sc_sources_are_unique_in_this_batch(self) -> None:
        policy = self.validation["repeated_source_policy"]
        self.assertTrue(policy["same_source_same_translation_required"])
        self.assertEqual(177, policy["translated_unique_source_hash_count"])
        self.assertEqual(0, policy["translated_repeated_source_group_count"])
        self.assertEqual([], policy["repeated_source_id_groups"])
        self.assertEqual(0, policy["failures"])

    def test_related_msgev_reuse_and_sc_adjustments_are_recorded(self) -> None:
        related = self.evidence["related_msgev_review"]
        self.assertEqual(177, related["same_numeric_id_semantic_reviewed_entry_count"])
        self.assertTrue(related["terminology_cross_checked"])
        self.assertTrue(related["direct_translation_reuse"])
        self.assertEqual(177, related["source_free_reused_entry_count"])
        self.assertEqual(0, related["sc_structure_adjusted_entry_count"])
        self.assertEqual([], related["ev_strdata_sc_structure_differs_at_ids"])
        self.assertTrue(related["ev_strdata_sc_structure_is_authoritative"])
        self.assertEqual(related, self.review["related_msgev_review"])

    def test_review_marks_layout_and_selected_historical_terms(self) -> None:
        self.assertEqual(177, len(self.review["entries"]))
        self.assertEqual(14, self.review["terminology_review_count"])
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
        self.assertEqual(177, len(entries))
        self.assertFalse(self.overlay["distribution_policy"]["contains_commercial_source_text"])

    def test_alignment_and_translation_hash_sets_are_pinned(self) -> None:
        alignment = self.validation["source_alignment"]
        self.assertEqual(["SC", "JP", "TC"], alignment["languages"])
        self.assertFalse(alignment["english_reference_available"])
        self.assertTrue(alignment["traditional_chinese_used_as_third_reference"])
        self.assertEqual(531, alignment["translated_reference_hash_count"])
        self.assertEqual(177, alignment["translated_ids_nonempty_in_all_references"])
        self.assertEqual(batch.SOURCE_SC_HASHES_SHA256, alignment["ordered_sc_source_hashes_sha256"])
        self.assertEqual(batch.ALL_REFERENCE_HASHES_SHA256, alignment["ordered_all_reference_hashes_sha256"])
        self.assertEqual(batch.TRANSLATION_MAP_SHA256, self.validation["translation"]["translation_map_sha256"])

    def test_v022_generated_files_are_pinned_and_source_free(self) -> None:
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
            WORKSTREAM_ROOT / "build_ev_strdata_batch22.py",
            WORKSTREAM_ROOT / "BATCH22_V0.22_README_KO.md",
            WORKSTREAM_ROOT / "public" / batch.OVERLAY_NAME,
            WORKSTREAM_ROOT / "evidence" / batch.EVIDENCE_NAME,
            WORKSTREAM_ROOT / "review" / batch.REVIEW_NAME,
            WORKSTREAM_ROOT / batch.VALIDATION_NAME,
            WORKSTREAM_ROOT / "tests" / "test_ev_strdata_batch22.py",
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
        self.assertEqual(177, self.validation["replacement_invariants"]["checked"])
        self.assertEqual(0, self.validation["replacement_invariants"]["failures"])
        self.assertEqual(
            ["isolated_a", "isolated_b", "final"],
            self.validation["reproducibility"]["required_runs"],
        )
        self.assertEqual(176, self.validation["offline_binary_build"]["operations"])
        self.assertEqual(177, self.validation["offline_binary_build"]["overlay_entries"])
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
                common.text_hash(loaded[language]["table"].texts[4387]),
            )
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr22-test-") as temporary:
            result = batch.build_reproducibly(GAME_ROOT, Path(temporary))
            self.assertEqual(177, result["entry_count"])
            self.assertEqual(177, result["inspected_count"])
            self.assertEqual(0, result["deferred_count"])
            self.assertEqual(4387, result["next_display_id"])
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
