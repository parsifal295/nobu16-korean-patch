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
import build_ev_strdata_batch17 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": (
        "EC862E7D3809EC0D7E87F2048DB74053546F743C2018543240A569BF43EC9DC6"
    ),
    f"evidence/{batch.EVIDENCE_NAME}": (
        "D716BD868D072334CF4F3385263F0D6F49EF89D1499BB30EF17C0AB8F43B0468"
    ),
    f"review/{batch.REVIEW_NAME}": (
        "FAAC5AD969755D6B8E15272F4A755F0B3F8B052CED33A4B7DFD670AC8470444F"
    ),
    batch.VALIDATION_NAME: (
        "FC127E846FA54293D55A5E3A23811A0ACDB3F6A33BA8B2A8D19BAA01BE8289CD"
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


class EvStrDataBatch17Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = load(f"public/{batch.OVERLAY_NAME}")
        cls.evidence = load(f"evidence/{batch.EVIDENCE_NAME}")
        cls.review = load(f"review/{batch.REVIEW_NAME}")
        cls.validation = load(batch.VALIDATION_NAME)

    def test_overlay_contains_exact_190_event_and_ending_entries(self) -> None:
        ids = [int(entry["id"]) for entry in self.overlay["entries"]]
        expected = sorted(set(range(3277, 3485)) - batch.DEFERRED_INTERNAL_IDS)
        self.assertEqual(expected, ids)
        self.assertEqual(190, self.overlay["entry_count"])
        by_id = {int(entry["id"]): entry["ko"] for entry in self.overlay["entries"]}
        self.assertIn("프란치스코 하비에르", by_id[3281])
        self.assertIn("도호쿠", by_id[3312])
        self.assertIn("[bus]\\x1bCZ의 평화", repr(by_id[3392]))
        self.assertIn("미요시 나가요시", by_id[3448])
        self.assertIn("오다 노부카쓰", by_id[3461])
        self.assertIn("오와리", by_id[3484])

    def test_inspected_scope_is_exact_translated_or_internal_key_partition(self) -> None:
        translated = set(batch.TRANSLATIONS)
        deferred = set(batch.DEFERRED_INTERNAL_IDS)
        self.assertFalse(translated & deferred)
        self.assertEqual(set(range(3277, 3485)), translated | deferred)
        self.assertEqual(18, len(deferred))
        self.assertEqual(batch.DEFERRED_IDS_SHA256, shared.hash_json(sorted(deferred)))
        self.assertEqual(3485, self.evidence["scope"]["next_display_id"])

    def test_internal_keys_and_all_prior_exclusion_sets_are_pinned(self) -> None:
        groups = self.evidence["deferred_internal_groups"]
        self.assertEqual(1, len(groups))
        self.assertEqual("internal_event_key", groups[0]["classification"])
        self.assertEqual(18, groups[0]["count"])
        self.assertTrue(groups[0]["excluded_from_overlay_and_translation_progress"])
        overlap = self.evidence["previous_deferred_overlap"]
        self.assertEqual([193, 199, 43, 96], [item["deferred_entry_count"] for item in overlap["previous_batches"]])
        self.assertEqual(531, overlap["previous_deferred_union_entry_count"])
        self.assertEqual(batch.PREVIOUS_DEFERRED_UNION_SHA256, overlap["previous_deferred_union_ids_sha256"])
        self.assertEqual(0, overlap["overlap_entry_count"])
        self.assertEqual(batch.EMPTY_IDS_SHA256, overlap["overlap_ids_sha256"])
        self.assertFalse(overlap["overlap_detected"])
        self.assertEqual(overlap, self.review["previous_deferred_overlap"])

    def test_functional_classification_counts_are_pinned(self) -> None:
        self.assertEqual(batch.CLASS_COUNTS, self.evidence["scope"]["functional_class_counts"])
        actual = {name: 0 for name in batch.CLASS_COUNTS}
        for entry in self.evidence["entries"]:
            actual[entry["classification"]] += 1
        self.assertEqual(batch.CLASS_COUNTS, actual)

    def test_repeated_source_entries_use_identical_korean(self) -> None:
        policy = self.validation["repeated_source_policy"]
        self.assertTrue(policy["same_source_same_translation_required"])
        self.assertEqual(188, policy["translated_unique_source_hash_count"])
        self.assertEqual(2, policy["translated_repeated_source_group_count"])
        self.assertEqual(
            [list(group) for group in batch.REPEATED_SOURCE_ID_GROUPS],
            policy["repeated_source_id_groups"],
        )
        self.assertEqual(0, policy["failures"])
        for group in batch.REPEATED_SOURCE_ID_GROUPS:
            self.assertEqual(1, len({batch.TRANSLATIONS[entry_id] for entry_id in group}))

    def test_review_marks_every_entry_for_runtime_layout_review(self) -> None:
        self.assertEqual(190, len(self.review["entries"]))
        for entry in self.review["entries"]:
            self.assertTrue(entry["human_review_required"])
            self.assertFalse(entry["runtime_reviewed"])
            self.assertEqual(["event_text_runtime_layout"], entry["uncertainty_flags"])

    def test_overlay_is_source_free_common_message_contract(self) -> None:
        original_allowlist = common.ALLOWED_RESOURCES
        common.ALLOWED_RESOURCES = original_allowlist | shared.SUPPORTED_RESOURCES
        try:
            resource, stock, entries = common.validate_overlay_shape(self.overlay)
        finally:
            common.ALLOWED_RESOURCES = original_allowlist
        self.assertEqual(shared.RESOURCE, resource)
        self.assertEqual(shared.STRING_COUNT, stock["string_count"])
        self.assertEqual(190, len(entries))
        self.assertFalse(self.overlay["distribution_policy"]["contains_commercial_source_text"])

    def test_alignment_and_translation_hash_sets_are_pinned(self) -> None:
        alignment = self.validation["source_alignment"]
        self.assertEqual(["SC", "JP", "TC"], alignment["languages"])
        self.assertFalse(alignment["english_reference_available"])
        self.assertTrue(alignment["traditional_chinese_used_as_third_reference"])
        self.assertEqual(570, alignment["translated_reference_hash_count"])
        self.assertEqual(190, alignment["translated_ids_nonempty_in_all_references"])
        self.assertEqual(batch.SOURCE_SC_HASHES_SHA256, alignment["ordered_sc_source_hashes_sha256"])
        self.assertEqual(batch.ALL_REFERENCE_HASHES_SHA256, alignment["ordered_all_reference_hashes_sha256"])
        self.assertEqual(batch.TRANSLATION_MAP_SHA256, self.validation["translation"]["translation_map_sha256"])

    def test_v017_generated_files_are_pinned_and_source_free(self) -> None:
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
            WORKSTREAM_ROOT / "build_ev_strdata_batch17.py",
            WORKSTREAM_ROOT / "BATCH17_V0.17_README_KO.md",
            WORKSTREAM_ROOT / "public" / batch.OVERLAY_NAME,
            WORKSTREAM_ROOT / "evidence" / batch.EVIDENCE_NAME,
            WORKSTREAM_ROOT / "review" / batch.REVIEW_NAME,
            WORKSTREAM_ROOT / batch.VALIDATION_NAME,
            WORKSTREAM_ROOT / "tests" / "test_ev_strdata_batch17.py",
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
        self.assertEqual(190, self.validation["replacement_invariants"]["checked"])
        self.assertEqual(0, self.validation["replacement_invariants"]["failures"])
        self.assertEqual(
            ["isolated_a", "isolated_b", "final"],
            self.validation["reproducibility"]["required_runs"],
        )
        self.assertEqual(189, self.validation["offline_binary_build"]["operations"])
        self.assertEqual(190, self.validation["offline_binary_build"]["overlay_entries"])
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
                common.text_hash(loaded[language]["table"].texts[3485]),
            )
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr17-test-") as temporary:
            result = batch.build_reproducibly(GAME_ROOT, Path(temporary))
            self.assertEqual(190, result["entry_count"])
            self.assertEqual(208, result["inspected_count"])
            self.assertEqual(18, result["deferred_count"])
            self.assertEqual(3485, result["next_display_id"])
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
