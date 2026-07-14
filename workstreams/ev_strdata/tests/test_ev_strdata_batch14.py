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
import build_ev_strdata_batch14 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": (
        "F2517512E5168AAAFA787D6CAC82F0C06DF08D6113227852700121E16E4E4FF6"
    ),
    f"evidence/{batch.EVIDENCE_NAME}": (
        "A6EC331A4C8D2CC3A37D1AC2F2520F44C038E5926993BCF95D200810937A3FD5"
    ),
    f"review/{batch.REVIEW_NAME}": (
        "4C9C0EEEE6B82C0CEB42540074217C994755F1897C0DA4828267C6DCC6C69DBC"
    ),
    batch.VALIDATION_NAME: (
        "0BF3CB981CC923A0B16AEEECB17153D983B54E336BF73E672F2D4D08277651C0"
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


class EvStrDataBatch14Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = load(f"public/{batch.OVERLAY_NAME}")
        cls.evidence = load(f"evidence/{batch.EVIDENCE_NAME}")
        cls.review = load(f"review/{batch.REVIEW_NAME}")
        cls.validation = load(batch.VALIDATION_NAME)

    def test_overlay_is_exact_contiguous_2407_through_2580_range(self) -> None:
        ids = [int(entry["id"]) for entry in self.overlay["entries"]]
        self.assertEqual(list(range(2407, 2581)), ids)
        self.assertEqual(174, self.overlay["entry_count"])
        by_id = {int(entry["id"]): entry["ko"] for entry in self.overlay["entries"]}
        self.assertEqual("와가중 두령", by_id[2407])
        self.assertEqual("후마 일당 두령", by_id[2449])
        self.assertEqual("가와치중 두령", by_id[2450])
        self.assertEqual("시와쿠 수군 두령", by_id[2544])
        self.assertEqual("무라카미 수군 두령", by_id[2548])
        self.assertEqual("네지메중 두령", by_id[2580])

    def test_input_mapping_is_pinned_with_only_one_reviewed_correction(self) -> None:
        mapping = self.evidence["input_mapping"]
        self.assertEqual(batch.INPUT_MAP_SHA256, mapping["sha256"])
        self.assertEqual(174, mapping["entry_count"])
        self.assertFalse(mapping["embedded_in_distribution"])
        self.assertEqual(1, mapping["obvious_typo_correction_count"])
        self.assertEqual({2450}, set(batch.INPUT_CORRECTION_IDS))
        self.assertEqual("가와치중 두령", batch.TRANSLATIONS[2450])

    def test_functional_label_section_is_complete(self) -> None:
        scope = self.evidence["scope"]
        self.assertEqual(2407, scope["start_id"])
        self.assertEqual(2580, scope["end_id"])
        self.assertEqual(174, scope["translated_display_entry_count"])
        self.assertEqual(2581, scope["sequential_next_id"])
        self.assertEqual(2780, scope["next_display_id"])
        self.assertEqual(
            {
                "fuma_party_leader_label": 1,
                "naval_group_leader_label": 2,
                "regional_group_leader_label": 171,
            },
            scope["functional_class_counts"],
        )
        actual = {name: 0 for name in batch.CLASS_COUNTS}
        for entry in self.evidence["entries"]:
            actual[entry["classification"]] += 1
        self.assertEqual(batch.CLASS_COUNTS, actual)

    def test_next_199_placeholder_ids_are_deferred_not_translated(self) -> None:
        deferred = self.evidence["next_deferred_ranges"]
        self.assertEqual(1, len(deferred))
        self.assertEqual(2581, deferred[0]["start_id"])
        self.assertEqual(2779, deferred[0]["end_id"])
        self.assertEqual(199, deferred[0]["count"])
        self.assertEqual("deferred", deferred[0]["status"])
        self.assertEqual("code_placeholder", deferred[0]["classification"])
        self.assertTrue(deferred[0]["excluded_from_overlay_and_translation_progress"])
        self.assertEqual(deferred, self.review["next_deferred_ranges"])
        self.assertTrue(
            all(int(entry["id"]) < 2581 for entry in self.overlay["entries"])
        )

    def test_overlay_is_source_free_common_message_contract(self) -> None:
        original_allowlist = common.ALLOWED_RESOURCES
        common.ALLOWED_RESOURCES = original_allowlist | shared.SUPPORTED_RESOURCES
        try:
            resource, stock, entries = common.validate_overlay_shape(self.overlay)
        finally:
            common.ALLOWED_RESOURCES = original_allowlist
        self.assertEqual(shared.RESOURCE, resource)
        self.assertEqual(shared.STRING_COUNT, stock["string_count"])
        self.assertEqual(174, len(entries))
        self.assertFalse(
            self.overlay["distribution_policy"]["contains_commercial_source_text"]
        )

    def test_alignment_hash_sets_and_repeated_source_policy_are_pinned(self) -> None:
        alignment = self.validation["source_alignment"]
        self.assertEqual(["SC", "JP", "TC"], alignment["languages"])
        self.assertFalse(alignment["english_reference_available"])
        self.assertTrue(alignment["traditional_chinese_used_as_third_reference"])
        self.assertEqual(522, alignment["translated_reference_hash_count"])
        self.assertEqual(174, alignment["translated_ids_nonempty_in_all_references"])
        self.assertEqual(
            batch.SOURCE_SC_HASHES_SHA256,
            alignment["ordered_sc_source_hashes_sha256"],
        )
        self.assertEqual(
            batch.ALL_REFERENCE_HASHES_SHA256,
            alignment["ordered_all_reference_hashes_sha256"],
        )
        policy = self.validation["repeated_source_policy"]
        self.assertTrue(policy["same_source_same_translation_required"])
        self.assertEqual(174, policy["translated_unique_source_hash_count"])
        self.assertEqual(0, policy["translated_repeated_source_group_count"])
        self.assertEqual(0, policy["failures"])

    def test_review_keeps_rare_reading_and_correction_flags(self) -> None:
        by_id = {int(entry["id"]): entry for entry in self.review["entries"]}
        flagged = {
            entry_id
            for entry_id, entry in by_id.items()
            if "rare_place_reading" in entry["uncertainty_flags"]
        }
        corrected = {
            entry_id
            for entry_id, entry in by_id.items()
            if "input_map_typo_corrected" in entry["uncertainty_flags"]
        }
        self.assertEqual(set(batch.UNCERTAIN_READING_IDS), flagged)
        self.assertEqual({2450}, corrected)
        self.assertEqual(20, self.review["uncertain_reading_count"])
        self.assertEqual(174, self.review["entry_count"])
        self.assertTrue(all(entry["human_review_required"] for entry in by_id.values()))
        self.assertTrue(all(not entry["runtime_reviewed"] for entry in by_id.values()))

    def test_public_v014_files_are_pinned_and_source_free(self) -> None:
        for relative, expected_hash in EXPECTED_HASHES.items():
            path = WORKSTREAM_ROOT / relative
            with self.subTest(relative=relative):
                self.assertEqual(expected_hash, digest(path))
                self.assertEqual(
                    {"han_or_kana_count": 0, "embedded_nul_count": 0},
                    shared.source_free_counts(path.read_bytes()),
                )

    def test_validation_records_invariants_determinism_and_file_only_safety(self) -> None:
        self.assertTrue(self.validation["passed"])
        self.assertEqual(174, self.validation["replacement_invariants"]["checked"])
        self.assertEqual(0, self.validation["replacement_invariants"]["failures"])
        self.assertEqual(
            ["isolated_a", "isolated_b", "final"],
            self.validation["reproducibility"]["required_runs"],
        )
        self.assertEqual(174, self.validation["offline_binary_build"]["operations"])
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
        source_sc_hashes = [
            common.text_hash(loaded["SC"]["table"].texts[entry_id])
            for entry_id in range(2407, 2581)
        ]
        all_reference_hashes = [
            common.text_hash(loaded[language]["table"].texts[entry_id])
            for entry_id in range(2407, 2581)
            for language in shared.LANGUAGES
        ]
        self.assertEqual(batch.SOURCE_SC_HASHES_SHA256, shared.hash_json(source_sc_hashes))
        self.assertEqual(
            batch.ALL_REFERENCE_HASHES_SHA256,
            shared.hash_json(all_reference_hashes),
        )
        for entry_id in range(2581, 2780):
            for language in shared.LANGUAGES:
                self.assertEqual(
                    batch.PLACEHOLDER_REFERENCE_HASHES[language],
                    common.text_hash(loaded[language]["table"].texts[entry_id]),
                )
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr14-test-") as temporary:
            result = batch.build_reproducibly(GAME_ROOT, Path(temporary))
            self.assertEqual(174, result["entry_count"])
            self.assertEqual(199, result["next_placeholder_count"])
            self.assertEqual(2780, result["next_display_id"])
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
