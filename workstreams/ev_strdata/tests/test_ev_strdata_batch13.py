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
import build_ev_strdata_batch13 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": (
        "D397316FFFD3BB41BAAD4A92ED182637F75157E895EE8B5239E560A677FC1167"
    ),
    f"evidence/{batch.EVIDENCE_NAME}": (
        "B55180324866E6433FDB49B9CDA5F55194E7BBBFB71FA0D6550241C44D34F991"
    ),
    f"review/{batch.REVIEW_NAME}": (
        "FD6223855513ABB9B62DC3D1B3D7450939401D195D960AE3336D530669DCB223"
    ),
    batch.VALIDATION_NAME: (
        "5E27892414EC3FD0DE581F05BC3AEDD44323FA6296058A6E628EE32D23D76897"
    ),
}
EXPECTED_TRANSLATIONS = {
    2400: "모베쓰중 두령",
    2401: "아카이시중 두령",
    2402: "도와다중 두령",
    2403: "시치노헤중 두령",
    2404: "다야마중 두령",
    2405: "구지중 두령",
    2406: "히에누키중 두령",
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


class EvStrDataBatch13Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = load(f"public/{batch.OVERLAY_NAME}")
        cls.evidence = load(f"evidence/{batch.EVIDENCE_NAME}")
        cls.review = load(f"review/{batch.REVIEW_NAME}")
        cls.validation = load(batch.VALIDATION_NAME)

    def test_overlay_has_only_seven_real_display_translations(self) -> None:
        ids = [int(entry["id"]) for entry in self.overlay["entries"]]
        self.assertEqual(list(range(2400, 2407)), ids)
        self.assertEqual(7, self.overlay["entry_count"])
        self.assertEqual(
            EXPECTED_TRANSLATIONS,
            {int(entry["id"]): entry["ko"] for entry in self.overlay["entries"]},
        )
        self.assertTrue(all(entry_id >= 2400 for entry_id in ids))

    def test_inspected_scope_and_deferred_placeholder_range_are_explicit(self) -> None:
        scope = self.evidence["scope"]
        self.assertEqual(2207, scope["start_id"])
        self.assertEqual(2406, scope["end_id"])
        self.assertEqual(2407, scope["next_start_id"])
        self.assertEqual(200, scope["inspected_entry_count"])
        self.assertEqual(7, scope["translated_display_entry_count"])
        self.assertEqual(193, scope["deferred_code_placeholder_count"])

        deferred = self.evidence["deferred_ranges"]
        self.assertEqual(1, len(deferred))
        self.assertEqual(2207, deferred[0]["start_id"])
        self.assertEqual(2399, deferred[0]["end_id"])
        self.assertEqual(193, deferred[0]["count"])
        self.assertEqual("deferred", deferred[0]["status"])
        self.assertEqual("code_placeholder", deferred[0]["classification"])
        self.assertTrue(deferred[0]["excluded_from_overlay_and_translation_progress"])
        self.assertEqual(deferred, self.review["deferred_ranges"])

    def test_overlay_is_source_free_common_message_contract(self) -> None:
        original_allowlist = common.ALLOWED_RESOURCES
        common.ALLOWED_RESOURCES = original_allowlist | shared.SUPPORTED_RESOURCES
        try:
            resource, stock, entries = common.validate_overlay_shape(self.overlay)
        finally:
            common.ALLOWED_RESOURCES = original_allowlist
        self.assertEqual(shared.RESOURCE, resource)
        self.assertEqual(shared.STRING_COUNT, stock["string_count"])
        self.assertEqual(7, len(entries))
        self.assertFalse(
            self.overlay["distribution_policy"]["contains_commercial_source_text"]
        )

    def test_extended_2207_through_3200_structure_profile_is_complete(self) -> None:
        analysis = self.evidence["extended_structure_analysis"]
        self.assertEqual(2207, analysis["start_id"])
        self.assertEqual(3200, analysis["end_id"])
        self.assertEqual(994, analysis["entry_count"])
        self.assertEqual(
            {
                "code_placeholder": 488,
                "other_display_candidate": 328,
                "regional_group_leader_label": 178,
            },
            analysis["class_counts"],
        )
        runs = analysis["runs"]
        self.assertEqual(15, len(runs))
        self.assertEqual(2207, runs[0]["start_id"])
        self.assertEqual(3200, runs[-1]["end_id"])
        self.assertEqual(994, sum(int(run["count"]) for run in runs))
        for language in shared.LANGUAGES:
            summary = analysis["language_structure_summary"][language]
            self.assertEqual(994, summary["entry_count"])
            self.assertEqual(994, summary["nonempty_count"])

    def test_alignment_review_and_repeated_source_policy_are_pinned(self) -> None:
        alignment = self.validation["source_alignment"]
        self.assertEqual(["SC", "JP", "TC"], alignment["languages"])
        self.assertFalse(alignment["english_reference_available"])
        self.assertTrue(alignment["traditional_chinese_used_as_third_reference"])
        self.assertEqual(600, alignment["inspected_reference_hash_count"])
        self.assertEqual(21, alignment["translated_reference_hash_count"])
        self.assertEqual(7, alignment["translated_ids_nonempty_in_all_references"])

        policy = self.validation["repeated_source_policy"]
        self.assertTrue(policy["same_source_same_translation_required"])
        self.assertEqual(7, policy["translated_unique_source_hash_count"])
        self.assertEqual(0, policy["translated_repeated_source_group_count"])
        self.assertEqual(1, policy["deferred_unique_source_hash_count"])
        self.assertEqual(193, policy["deferred_repeated_entry_count"])
        self.assertEqual(0, policy["failures"])

    def test_public_v013_files_are_pinned_and_source_free(self) -> None:
        for relative, expected_hash in EXPECTED_HASHES.items():
            path = WORKSTREAM_ROOT / relative
            with self.subTest(relative=relative):
                self.assertEqual(expected_hash, digest(path))
                self.assertEqual(
                    {"han_or_kana_count": 0, "embedded_nul_count": 0},
                    shared.source_free_counts(path.read_bytes()),
                )

    def test_review_index_separates_translated_and_deferred(self) -> None:
        overlay_ids = [entry["id"] for entry in self.overlay["entries"]]
        review_ids = [entry["id"] for entry in self.review["entries"]]
        self.assertEqual(overlay_ids, review_ids)
        self.assertEqual(200, self.review["inspected_entry_count"])
        self.assertEqual(7, self.review["translated_entry_count"])
        self.assertEqual(193, self.review["deferred_entry_count"])
        self.assertTrue(all(entry["status"] == "translated" for entry in self.review["entries"]))
        self.assertTrue(all(entry["human_review_required"] for entry in self.review["entries"]))
        self.assertTrue(all(not entry["runtime_reviewed"] for entry in self.review["entries"]))

    def test_validation_records_invariants_determinism_and_file_only_safety(self) -> None:
        self.assertTrue(self.validation["passed"])
        self.assertEqual(7, self.validation["replacement_invariants"]["checked"])
        self.assertEqual(0, self.validation["replacement_invariants"]["failures"])
        self.assertEqual(
            ["isolated_a", "isolated_b", "final"],
            self.validation["reproducibility"]["required_runs"],
        )
        self.assertEqual(7, self.validation["offline_binary_build"]["operations"])
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
        overlay_by_id = {int(entry["id"]): entry for entry in self.overlay["entries"]}
        for entry_id in range(2207, 2400):
            for language in shared.LANGUAGES:
                self.assertEqual(
                    batch.DEFERRED_REFERENCE_HASHES[language],
                    common.text_hash(loaded[language]["table"].texts[entry_id]),
                )
        for entry_id in range(2400, 2407):
            with self.subTest(stock_entry_id=entry_id):
                self.assertEqual(
                    batch.TRANSLATIONS[entry_id]["source_sc_utf16le_sha256"],
                    common.text_hash(loaded["SC"]["table"].texts[entry_id]),
                )
                self.assertEqual(
                    batch.TRANSLATIONS[entry_id]["ko"],
                    overlay_by_id[entry_id]["ko"],
                )
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr13-test-") as temporary:
            result = batch.build_reproducibly(GAME_ROOT, Path(temporary))
            self.assertEqual(200, result["inspected_count"])
            self.assertEqual(7, result["entry_count"])
            self.assertEqual(193, result["deferred_count"])
            self.assertEqual(2407, result["next_start_id"])
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
