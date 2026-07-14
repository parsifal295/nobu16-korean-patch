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
import build_ev_strdata_batch12 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": (
        "1A74A2F99E281BE6A5E04B6E8BDF0976D041AFE3776DC5265F2852BB2C075822"
    ),
    f"evidence/{batch.EVIDENCE_NAME}": (
        "DA50C9D3228BDBDB8D932F50A2ED5CAABF66DE01A894586A7A4994E54CEE2CF7"
    ),
    f"review/{batch.REVIEW_NAME}": (
        "0B36EDD21FC0982F0D5A392838D4ABCAC3D414850C11427419B338C6202C2EB8"
    ),
    batch.VALIDATION_NAME: (
        "BC66C829BBE668ECEFEA6FDDB6B976069E0B14462B02B15CAA3D2A5DD47B2A29"
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


class EvStrDataBatch12Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = load(f"public/{batch.OVERLAY_NAME}")
        cls.evidence = load(f"evidence/{batch.EVIDENCE_NAME}")
        cls.review = load(f"review/{batch.REVIEW_NAME}")
        cls.validation = load(batch.VALIDATION_NAME)

    def test_scope_is_exactly_final_seed_ids_2150_through_2206(self) -> None:
        ids = [int(entry["id"]) for entry in self.overlay["entries"]]
        self.assertEqual(list(range(2150, 2207)), ids)
        self.assertEqual(57, self.overlay["entry_count"])
        self.assertEqual(2207, self.evidence["scope"]["next_start_id"])
        self.assertEqual(2207, self.validation["scope"]["next_start_id"])

        seed = shared.load_json(REPO_ROOT / shared.SEED_RELATIVE)
        seed_ids = [int(entry["id"]) for entry in seed["entries"]]
        self.assertEqual(list(range(2207)), seed_ids)

    def test_overlay_is_source_free_common_message_contract(self) -> None:
        original_allowlist = common.ALLOWED_RESOURCES
        common.ALLOWED_RESOURCES = original_allowlist | shared.SUPPORTED_RESOURCES
        try:
            resource, stock, entries = common.validate_overlay_shape(self.overlay)
        finally:
            common.ALLOWED_RESOURCES = original_allowlist
        self.assertEqual(shared.RESOURCE, resource)
        self.assertEqual(shared.STRING_COUNT, stock["string_count"])
        self.assertEqual(57, len(entries))
        self.assertFalse(
            self.overlay["distribution_policy"]["contains_commercial_source_text"]
        )

    def test_alignment_and_translation_provenance_are_complete(self) -> None:
        alignment = self.validation["source_alignment"]
        self.assertEqual(["SC", "JP", "TC"], alignment["languages"])
        self.assertFalse(alignment["english_reference_available"])
        self.assertTrue(alignment["traditional_chinese_used_as_third_reference"])
        self.assertEqual(171, alignment["selected_reference_hash_count"])
        self.assertEqual(57, alignment["selected_ids_nonempty_in_all_references"])

        reuse = self.validation["translation_reuse"]
        self.assertEqual(57, reuse["exact_sc_hash_matches"])
        self.assertEqual(0, reuse["mismatches"])
        manual = self.validation["manual_translation"]
        self.assertEqual(0, manual["count"])
        self.assertEqual(0, manual["sc_hash_pins_checked"])
        self.assertEqual(0, manual["sc_jp_tc_alignment_reviewed"])
        self.assertFalse(manual["source_text_embedded"])

        self.assertEqual({}, batch.MANUAL_TRANSLATIONS)
        self.assertTrue(
            all(
                entry["translation_reuse_exact_sc_hash_match"]
                for entry in self.evidence["entries"]
            )
        )
        for entry in self.evidence["entries"]:
            with self.subTest(entry_id=entry["id"]):
                self.assertEqual({"SC", "JP", "TC"}, set(entry["references"]))

    def test_public_v012_files_are_pinned_and_source_free(self) -> None:
        for relative, expected_hash in EXPECTED_HASHES.items():
            path = WORKSTREAM_ROOT / relative
            with self.subTest(relative=relative):
                self.assertEqual(expected_hash, digest(path))
                self.assertEqual(
                    {"han_or_kana_count": 0, "embedded_nul_count": 0},
                    shared.source_free_counts(path.read_bytes()),
                )

    def test_validation_records_invariants_determinism_and_safety(self) -> None:
        self.assertTrue(self.validation["passed"])
        self.assertEqual(57, self.validation["replacement_invariants"]["checked"])
        self.assertEqual(0, self.validation["replacement_invariants"]["failures"])
        self.assertEqual(
            ["isolated_a", "isolated_b", "final"],
            self.validation["reproducibility"]["required_runs"],
        )
        self.assertEqual(57, self.validation["offline_binary_build"]["operations"])
        self.assertEqual(
            ["SC", "JP", "TC"],
            self.validation["raw_format"]["raw_parse_rebuild_byte_exact_languages"],
        )
        safety = self.validation["safety"]
        for key in (
            "installed_game_files_modified",
            "font_files_modified",
            "installer_modified",
            "root_readme_or_progress_modified",
            "official_source_text_exposed_in_public_artifacts",
            "process_memory_access",
            "executable_modified",
            "registry_modified",
            "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v010_v011_artifacts_modified",
        ):
            with self.subTest(key=key):
                self.assertFalse(safety[key])

    def test_review_index_matches_overlay(self) -> None:
        overlay_ids = [entry["id"] for entry in self.overlay["entries"]]
        review_ids = [entry["id"] for entry in self.review["entries"]]
        self.assertEqual(overlay_ids, review_ids)
        self.assertEqual(57, self.review["entry_count"])
        self.assertTrue(all(entry["human_review_required"] for entry in self.review["entries"]))
        self.assertTrue(all(not entry["runtime_reviewed"] for entry in self.review["entries"]))
        self.assertTrue(
            all(
                entry["translation_origin"]
                == "existing_officer_name_overlay_exact_sc_hash_match"
                for entry in self.review["entries"]
            )
        )

    @unittest.skipUnless(STOCK_AVAILABLE, "installed SC/JP/TC stock resources are unavailable")
    def test_stock_replay_is_deterministic_and_install_is_unchanged(self) -> None:
        source_paths = [
            GAME_ROOT / "MSG" / language / "ev_strdata.bin"
            for language in shared.LANGUAGES
        ]
        before = {path: digest(path) for path in source_paths}
        loaded, _ = shared.load_sources(GAME_ROOT)
        seed = shared.load_json(REPO_ROOT / shared.SEED_RELATIVE)
        seed_by_id = {int(entry["id"]): entry for entry in seed["entries"]}
        overlay_by_id = {int(entry["id"]): entry for entry in self.overlay["entries"]}
        for entry_id in range(batch.SCOPE_START, batch.NEXT_START_ID):
            with self.subTest(stock_entry_id=entry_id):
                self.assertTrue(
                    all(
                        loaded[language]["table"].texts[entry_id].strip()
                        for language in shared.LANGUAGES
                    )
                )
                source_hash = common.text_hash(loaded["SC"]["table"].texts[entry_id])
                self.assertEqual(
                    source_hash,
                    overlay_by_id[entry_id]["source_sc_utf16le_sha256"],
                )
                self.assertEqual(
                    source_hash,
                    seed_by_id[entry_id]["source_sc_utf16le_sha256"],
                )
                self.assertEqual(
                    seed_by_id[entry_id]["ko"],
                    overlay_by_id[entry_id]["ko"],
                )
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr12-test-") as temporary:
            result = batch.build_reproducibly(GAME_ROOT, Path(temporary))
            self.assertEqual(57, result["entry_count"])
            self.assertEqual(2207, result["next_start_id"])
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
