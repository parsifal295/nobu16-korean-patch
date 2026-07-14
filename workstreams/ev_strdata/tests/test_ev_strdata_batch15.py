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
import build_ev_strdata_batch15 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": (
        "CE37F5F9F12FC8C61CD6B047AA8B51ABDBF8D2AB6F41989548D970FCD5D3AD9D"
    ),
    f"evidence/{batch.EVIDENCE_NAME}": (
        "FEC0B1C91A452B71F424DF8AB0FCED9DDEE39C25EBF8D5E6598A3A1341F0B116"
    ),
    f"review/{batch.REVIEW_NAME}": (
        "E878A61318DC55070CE7D5B7057DE654A8BE455498FF55BC5860890C18812439"
    ),
    batch.VALIDATION_NAME: (
        "A754B9980A20BE1D03D6E29159FECD6A3906CAFCE744B157726A2BDDC7EFDBA5"
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


class EvStrDataBatch15Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = load(f"public/{batch.OVERLAY_NAME}")
        cls.evidence = load(f"evidence/{batch.EVIDENCE_NAME}")
        cls.review = load(f"review/{batch.REVIEW_NAME}")
        cls.validation = load(batch.VALIDATION_NAME)

    def test_overlay_contains_exact_184_reviewed_display_labels(self) -> None:
        ids = [int(entry["id"]) for entry in self.overlay["entries"]]
        expected = sorted(batch.TRANSLATIONS)
        self.assertEqual(expected, ids)
        self.assertEqual(184, len(ids))
        self.assertEqual(list(range(2780, 2953)), ids[:173])
        self.assertEqual(2780, ids[0])
        self.assertEqual(2971, ids[-1])
        by_id = {int(entry["id"]): entry["ko"] for entry in self.overlay["entries"]}
        self.assertEqual("쓰다 소규", by_id[2780])
        self.assertEqual("마쓰다이라 다케치요", by_id[2805])
        self.assertEqual("아소 고레노리", by_id[2825])
        self.assertEqual("안도 모리나리", by_id[2963])
        self.assertEqual("다카하시대 잡병", by_id[2971])

    def test_inspected_partition_defers_exact_43_internal_entries(self) -> None:
        translated = set(batch.TRANSLATIONS)
        deferred = set().union(*batch.DEFERRED_GROUP_IDS.values())
        self.assertFalse(translated & deferred)
        self.assertEqual(set(range(2780, 3007)), translated | deferred)
        self.assertEqual(43, len(deferred))
        groups = {
            entry["classification"]: entry
            for entry in self.evidence["deferred_internal_groups"]
        }
        self.assertEqual(
            {"actor_reference", "dummy_placeholder", "internal_role_key"},
            set(groups),
        )
        self.assertEqual(34, groups["actor_reference"]["count"])
        self.assertEqual(2, groups["dummy_placeholder"]["count"])
        self.assertEqual(7, groups["internal_role_key"]["count"])
        self.assertTrue(
            all(
                group["excluded_from_overlay_and_translation_progress"]
                for group in groups.values()
            )
        )
        self.assertEqual(
            self.evidence["deferred_internal_groups"],
            self.review["deferred_internal_groups"],
        )

    def test_functional_classification_counts_are_pinned(self) -> None:
        self.assertEqual(
            {"generic_speaker_label": 63, "named_character_label": 121},
            self.evidence["scope"]["functional_class_counts"],
        )
        actual = {name: 0 for name in batch.CLASS_COUNTS}
        for entry in self.evidence["entries"]:
            actual[entry["classification"]] += 1
        self.assertEqual(batch.CLASS_COUNTS, actual)
        self.assertEqual(3007, self.evidence["scope"]["next_display_id"])

    def test_repeated_source_labels_use_identical_korean(self) -> None:
        policy = self.validation["repeated_source_policy"]
        self.assertTrue(policy["same_source_same_translation_required"])
        self.assertEqual(181, policy["translated_unique_source_hash_count"])
        self.assertEqual(3, policy["translated_repeated_source_group_count"])
        self.assertEqual(
            [list(group) for group in batch.REPEATED_SOURCE_ID_GROUPS],
            policy["repeated_source_id_groups"],
        )
        self.assertEqual(0, policy["failures"])
        for group in batch.REPEATED_SOURCE_ID_GROUPS:
            self.assertEqual(1, len({batch.TRANSLATIONS[entry_id] for entry_id in group}))

    def test_review_flags_only_eight_uncertain_person_readings(self) -> None:
        by_id = {int(entry["id"]): entry for entry in self.review["entries"]}
        flagged = {
            entry_id
            for entry_id, entry in by_id.items()
            if "rare_person_reading" in entry["uncertainty_flags"]
        }
        self.assertEqual(set(batch.UNCERTAIN_READING_IDS), flagged)
        self.assertEqual(8, self.review["uncertain_reading_count"])
        self.assertEqual(184, self.review["entry_count"])
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
        self.assertEqual(184, len(entries))
        self.assertFalse(
            self.overlay["distribution_policy"]["contains_commercial_source_text"]
        )

    def test_alignment_and_translation_hash_sets_are_pinned(self) -> None:
        alignment = self.validation["source_alignment"]
        self.assertEqual(["SC", "JP", "TC"], alignment["languages"])
        self.assertFalse(alignment["english_reference_available"])
        self.assertTrue(alignment["traditional_chinese_used_as_third_reference"])
        self.assertEqual(552, alignment["translated_reference_hash_count"])
        self.assertEqual(184, alignment["translated_ids_nonempty_in_all_references"])
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

    def test_public_v015_files_are_pinned_and_source_free(self) -> None:
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
        self.assertEqual(184, self.validation["replacement_invariants"]["checked"])
        self.assertEqual(0, self.validation["replacement_invariants"]["failures"])
        self.assertEqual(
            ["isolated_a", "isolated_b", "final"],
            self.validation["reproducibility"]["required_runs"],
        )
        self.assertEqual(184, self.validation["offline_binary_build"]["operations"])
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
                common.text_hash(loaded[language]["table"].texts[3007]),
            )
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr15-test-") as temporary:
            result = batch.build_reproducibly(GAME_ROOT, Path(temporary))
            self.assertEqual(184, result["entry_count"])
            self.assertEqual(227, result["inspected_count"])
            self.assertEqual(43, result["deferred_count"])
            self.assertEqual(3007, result["next_display_id"])
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
