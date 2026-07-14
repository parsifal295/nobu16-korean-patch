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
import build_ev_strdata_batch1 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": (
        "5E4AE2EE962B9E723816A42132E1F31E71161E0336D7AD7BE9E6DACD8CA6482F"
    ),
    f"evidence/{batch.EVIDENCE_NAME}": (
        "17DDAE2ECEF889BA7B039C6A0028AA29E0BAF9BFCFEB1773CAA2ED8EE52D8A5C"
    ),
    f"review/{batch.REVIEW_NAME}": (
        "2456994679BB3F8B0875544EB93BA1A2D6E7C084D84EACBB8271CE62D4FF5AA2"
    ),
    batch.VALIDATION_NAME: (
        "01FAE717C0C1293DD36D474ED3CC045291FEE3C3681CB0C2F04FE62F4B8D99D3"
    ),
}
STOCK_AVAILABLE = all(
    (GAME_ROOT / "MSG" / language / "ev_strdata.bin").is_file()
    for language in batch.LANGUAGES
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load(relative: str) -> dict[str, object]:
    return json.loads(
        (WORKSTREAM_ROOT / relative).read_text(encoding="utf-8"),
        object_pairs_hook=common.strict_object,
    )


class EvStrDataBatch1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = load(f"public/{batch.OVERLAY_NAME}")
        cls.evidence = load(f"evidence/{batch.EVIDENCE_NAME}")
        cls.review = load(f"review/{batch.REVIEW_NAME}")
        cls.validation = load(batch.VALIDATION_NAME)

    def test_scope_is_exactly_first_150_display_entries(self) -> None:
        entries = self.overlay["entries"]
        self.assertIsInstance(entries, list)
        ids = [int(entry["id"]) for entry in entries]
        self.assertEqual(list(range(150)), ids)
        self.assertEqual(150, self.overlay["entry_count"])
        self.assertEqual(150, self.evidence["scope"]["next_start_id"])
        self.assertEqual(150, self.validation["scope"]["next_start_id"])

    def test_overlay_is_common_message_source_free_contract(self) -> None:
        original_allowlist = common.ALLOWED_RESOURCES
        common.ALLOWED_RESOURCES = original_allowlist | batch.SUPPORTED_RESOURCES
        try:
            resource, stock, entries = common.validate_overlay_shape(self.overlay)
        finally:
            common.ALLOWED_RESOURCES = original_allowlist
        self.assertEqual(batch.RESOURCE, resource)
        self.assertEqual(batch.STRING_COUNT, stock["string_count"])
        self.assertEqual(150, len(entries))
        self.assertFalse(
            self.overlay["distribution_policy"]["contains_commercial_source_text"]
        )

    def test_alignment_uses_sc_jp_tc_and_hashes_only(self) -> None:
        self.assertEqual(["SC", "JP", "TC"], self.validation["source_alignment"]["languages"])
        self.assertFalse(
            self.validation["source_alignment"]["english_reference_available"]
        )
        self.assertTrue(
            self.validation["source_alignment"][
                "traditional_chinese_used_as_third_reference"
            ]
        )
        self.assertEqual(150, self.evidence["entry_count"])
        self.assertEqual(450, self.validation["source_alignment"]["selected_reference_hash_count"])
        for entry in self.evidence["entries"]:
            with self.subTest(entry_id=entry["id"]):
                self.assertEqual({"SC", "JP", "TC"}, set(entry["references"]))
                self.assertTrue(entry["translation_reuse_exact_sc_hash_match"])
        self.assertFalse(self.evidence["contains_commercial_source_text"])

    def test_public_files_are_pinned_and_source_free(self) -> None:
        for relative, expected_hash in EXPECTED_HASHES.items():
            path = WORKSTREAM_ROOT / relative
            with self.subTest(relative=relative):
                self.assertEqual(expected_hash, digest(path))
                self.assertEqual(
                    {"han_or_kana_count": 0, "embedded_nul_count": 0},
                    batch.source_free_counts(path.read_bytes()),
                )

    def test_validation_records_all_required_invariants_and_safety(self) -> None:
        self.assertTrue(self.validation["passed"])
        self.assertEqual(150, self.validation["replacement_invariants"]["checked"])
        self.assertEqual(0, self.validation["replacement_invariants"]["failures"])
        self.assertEqual(
            ["isolated_a", "isolated_b", "final"],
            self.validation["reproducibility"]["required_runs"],
        )
        self.assertEqual(
            ["SC", "JP", "TC"],
            self.validation["raw_format"]["raw_parse_rebuild_byte_exact_languages"],
        )
        self.assertEqual(150, self.validation["offline_binary_build"]["operations"])
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
        ):
            with self.subTest(key=key):
                self.assertFalse(safety[key])

    def test_review_index_matches_overlay_ids(self) -> None:
        overlay_ids = [entry["id"] for entry in self.overlay["entries"]]
        review_ids = [entry["id"] for entry in self.review["entries"]]
        self.assertEqual(overlay_ids, review_ids)
        self.assertEqual(150, self.review["entry_count"])
        self.assertTrue(all(entry["human_review_required"] for entry in self.review["entries"]))
        self.assertTrue(all(not entry["runtime_reviewed"] for entry in self.review["entries"]))

    @unittest.skipUnless(STOCK_AVAILABLE, "installed SC/JP/TC stock resources are unavailable")
    def test_stock_replay_is_deterministic_and_install_is_unchanged(self) -> None:
        source_paths = [
            GAME_ROOT / "MSG" / language / "ev_strdata.bin"
            for language in batch.LANGUAGES
        ]
        before = {path: digest(path) for path in source_paths}
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr-test-") as temporary:
            result = batch.build_reproducibly(GAME_ROOT, Path(temporary))
            self.assertEqual(150, result["entry_count"])
            self.assertEqual(150, result["next_start_id"])
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
