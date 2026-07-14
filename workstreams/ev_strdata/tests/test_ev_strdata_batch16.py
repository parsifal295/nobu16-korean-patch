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
import build_ev_strdata_batch16 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": (
        "BB693C67252DAB581582D0F842C6DCE5468663131892A2FF62EB17F750F96C12"
    ),
    f"evidence/{batch.EVIDENCE_NAME}": (
        "2B7BFC4D520C1B232479F04755D945C13E024694D18EFED88373BD108786E256"
    ),
    f"review/{batch.REVIEW_NAME}": (
        "E4405EF646BA45C3A213F59418A2C3CD9D7CBBC8547852250944CE2E807078FA"
    ),
    batch.VALIDATION_NAME: (
        "CDC5D70C137DDF4FAC4C7E3EA26270AA583B8BF145E67DA15A4DEEF2AEB6DCE6"
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


class EvStrDataBatch16Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = load(f"public/{batch.OVERLAY_NAME}")
        cls.evidence = load(f"evidence/{batch.EVIDENCE_NAME}")
        cls.review = load(f"review/{batch.REVIEW_NAME}")
        cls.validation = load(batch.VALIDATION_NAME)

    def test_overlay_contains_exact_174_labels_and_narration_entries(self) -> None:
        ids = [int(entry["id"]) for entry in self.overlay["entries"]]
        expected = list(range(3007, 3105)) + [3117] + list(range(3202, 3277))
        self.assertEqual(expected, ids)
        self.assertEqual(174, self.overlay["entry_count"])
        self.assertEqual(99, len(batch.LABEL_TRANSLATIONS))
        self.assertEqual(75, len(batch.NARRATION_TRANSLATIONS))
        by_id = {int(entry["id"]): entry["ko"] for entry in self.overlay["entries"]}
        self.assertEqual("호조 쓰나시게", by_id[3007])
        self.assertEqual("다치바나 긴치요", by_id[3014])
        self.assertEqual("오사카성", by_id[3048])
        self.assertEqual("야마다 교토쿠", by_id[3117])
        self.assertIn("삼각 동맹", by_id[3208])
        self.assertIn("미카타가하라", by_id[3270])

    def test_inspected_scope_is_an_exact_translated_or_deferred_partition(self) -> None:
        translated = set(batch.TRANSLATIONS)
        deferred = set().union(*batch.DEFERRED_GROUP_IDS.values())
        self.assertFalse(translated & deferred)
        self.assertEqual(set(range(3007, 3277)), translated | deferred)
        self.assertEqual(96, len(deferred))
        self.assertEqual(batch.DEFERRED_IDS_SHA256, shared.hash_json(sorted(deferred)))
        self.assertEqual(3277, self.evidence["scope"]["next_display_id"])

    def test_deferred_groups_and_v015_overlap_check_are_pinned(self) -> None:
        groups = {
            entry["classification"]: entry
            for entry in self.evidence["deferred_internal_groups"]
        }
        self.assertEqual(
            {"dummy_placeholder", "actor_reference", "empty_slot"},
            set(groups),
        )
        self.assertEqual(94, groups["dummy_placeholder"]["count"])
        self.assertEqual(1, groups["actor_reference"]["count"])
        self.assertEqual(1, groups["empty_slot"]["count"])
        self.assertTrue(
            all(
                group["excluded_from_overlay_and_translation_progress"]
                for group in groups.values()
            )
        )
        overlap = self.evidence["previous_deferred_overlap"]
        self.assertEqual(43, overlap["previous_deferred_entry_count"])
        self.assertEqual(batch.PREVIOUS_DEFERRED_IDS_SHA256, overlap["previous_deferred_ids_sha256"])
        self.assertEqual(0, overlap["overlap_entry_count"])
        self.assertEqual(batch.EMPTY_IDS_SHA256, overlap["overlap_ids_sha256"])
        self.assertFalse(overlap["overlap_detected"])
        self.assertEqual(overlap, self.review["previous_deferred_overlap"])

    def test_functional_classification_counts_are_pinned(self) -> None:
        expected = {
            "generic_speaker_label": 1,
            "historical_event_narration": 75,
            "named_character_label": 97,
            "place_label": 1,
        }
        self.assertEqual(expected, self.evidence["scope"]["functional_class_counts"])
        actual = {name: 0 for name in batch.CLASS_COUNTS}
        for entry in self.evidence["entries"]:
            actual[entry["classification"]] += 1
        self.assertEqual(batch.CLASS_COUNTS, actual)

    def test_repeated_source_labels_use_identical_korean(self) -> None:
        policy = self.validation["repeated_source_policy"]
        self.assertTrue(policy["same_source_same_translation_required"])
        self.assertEqual(166, policy["translated_unique_source_hash_count"])
        self.assertEqual(8, policy["translated_repeated_source_group_count"])
        self.assertEqual(
            [list(group) for group in batch.REPEATED_SOURCE_ID_GROUPS],
            policy["repeated_source_id_groups"],
        )
        self.assertEqual(0, policy["failures"])
        for group in batch.REPEATED_SOURCE_ID_GROUPS:
            self.assertEqual(1, len({batch.TRANSLATIONS[entry_id] for entry_id in group}))

    def test_review_flags_rare_readings_and_all_narration_layouts(self) -> None:
        by_id = {int(entry["id"]): entry for entry in self.review["entries"]}
        rare = {
            entry_id
            for entry_id, entry in by_id.items()
            if "rare_person_or_alias_reading" in entry["uncertainty_flags"]
        }
        narration = {
            entry_id
            for entry_id, entry in by_id.items()
            if "historical_narration_runtime_layout" in entry["uncertainty_flags"]
        }
        self.assertEqual(set(batch.UNCERTAIN_READING_IDS), rare)
        self.assertEqual(set(batch.NARRATION_TRANSLATIONS), narration)
        self.assertEqual(6, self.review["uncertain_reading_count"])
        self.assertTrue(all(entry["human_review_required"] for entry in by_id.values()))
        self.assertTrue(all(not entry["runtime_reviewed"] for entry in by_id.values()))

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

    def test_alignment_and_translation_hash_sets_are_pinned(self) -> None:
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
        self.assertEqual(
            batch.TRANSLATION_MAP_SHA256,
            self.validation["translation"]["translation_map_sha256"],
        )

    def test_public_v016_files_are_pinned_and_source_free(self) -> None:
        for relative, expected_hash in EXPECTED_HASHES.items():
            path = WORKSTREAM_ROOT / relative
            with self.subTest(relative=relative):
                self.assertEqual(expected_hash, digest(path))
                self.assertEqual(
                    {"han_or_kana_count": 0, "embedded_nul_count": 0},
                    shared.source_free_counts(path.read_bytes()),
                )

    def test_validation_records_determinism_invariants_and_file_only_safety(self) -> None:
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
        self.assertEqual(
            batch.ALL_REFERENCE_HASHES_SHA256,
            shared.hash_json(all_reference_hashes),
        )
        for language in shared.LANGUAGES:
            self.assertEqual(
                batch.NEXT_DISPLAY_REFERENCE_HASHES[language],
                common.text_hash(loaded[language]["table"].texts[3277]),
            )
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr16-test-") as temporary:
            result = batch.build_reproducibly(GAME_ROOT, Path(temporary))
            self.assertEqual(174, result["entry_count"])
            self.assertEqual(99, result["label_count"])
            self.assertEqual(75, result["narration_count"])
            self.assertEqual(270, result["inspected_count"])
            self.assertEqual(96, result["deferred_count"])
            self.assertEqual(3277, result["next_display_id"])
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
