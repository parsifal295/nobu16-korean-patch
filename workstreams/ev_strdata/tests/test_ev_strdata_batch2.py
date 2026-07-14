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
import build_ev_strdata_batch2 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": (
        "2F2A31E5F1871D48B9E93CECB9C6D04CF6C9B65C96CA6B5C407072DD2E5941E1"
    ),
    f"evidence/{batch.EVIDENCE_NAME}": (
        "237BE36ACBA9DFF542D1BACC420F53742FE9A9DE7D0FE4062201C435F7C0561C"
    ),
    f"review/{batch.REVIEW_NAME}": (
        "98909C907274E5CD2604A26E50B70997E9184184EED7D4005B32F1F40605584A"
    ),
    batch.VALIDATION_NAME: (
        "F5734E59CB8BA5CBC6B50EE121BE69E6596EA2AE15EBC04FE35431D7F2C3B9A2"
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


class EvStrDataBatch2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = load(f"public/{batch.OVERLAY_NAME}")
        cls.evidence = load(f"evidence/{batch.EVIDENCE_NAME}")
        cls.review = load(f"review/{batch.REVIEW_NAME}")
        cls.validation = load(batch.VALIDATION_NAME)

    def test_scope_is_exactly_next_200_display_entries(self) -> None:
        entries = self.overlay["entries"]
        self.assertIsInstance(entries, list)
        ids = [int(entry["id"]) for entry in entries]
        self.assertEqual(list(range(150, 350)), ids)
        self.assertEqual(200, self.overlay["entry_count"])
        self.assertEqual(350, self.evidence["scope"]["next_start_id"])
        self.assertEqual(350, self.validation["scope"]["next_start_id"])

    def test_overlay_is_source_free_common_message_contract(self) -> None:
        original_allowlist = common.ALLOWED_RESOURCES
        common.ALLOWED_RESOURCES = original_allowlist | shared.SUPPORTED_RESOURCES
        try:
            resource, stock, entries = common.validate_overlay_shape(self.overlay)
        finally:
            common.ALLOWED_RESOURCES = original_allowlist
        self.assertEqual(shared.RESOURCE, resource)
        self.assertEqual(shared.STRING_COUNT, stock["string_count"])
        self.assertEqual(200, len(entries))
        self.assertFalse(
            self.overlay["distribution_policy"]["contains_commercial_source_text"]
        )

    def test_alignment_and_translation_reuse_are_exact(self) -> None:
        alignment = self.validation["source_alignment"]
        self.assertEqual(["SC", "JP", "TC"], alignment["languages"])
        self.assertFalse(alignment["english_reference_available"])
        self.assertTrue(alignment["traditional_chinese_used_as_third_reference"])
        self.assertEqual(600, alignment["selected_reference_hash_count"])
        self.assertEqual(200, self.validation["translation_reuse"]["exact_sc_hash_matches"])
        self.assertEqual(0, self.validation["translation_reuse"]["mismatches"])
        self.assertEqual(200, self.evidence["entry_count"])
        for entry in self.evidence["entries"]:
            with self.subTest(entry_id=entry["id"]):
                self.assertEqual({"SC", "JP", "TC"}, set(entry["references"]))
                self.assertTrue(entry["translation_reuse_exact_sc_hash_match"])

    def test_public_files_are_pinned_and_source_free(self) -> None:
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
        self.assertEqual(200, self.validation["replacement_invariants"]["checked"])
        self.assertEqual(0, self.validation["replacement_invariants"]["failures"])
        self.assertEqual(
            ["isolated_a", "isolated_b", "final"],
            self.validation["reproducibility"]["required_runs"],
        )
        self.assertEqual(200, self.validation["offline_binary_build"]["operations"])
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
            "existing_v01_artifacts_modified",
        ):
            with self.subTest(key=key):
                self.assertFalse(safety[key])

    def test_review_index_matches_overlay(self) -> None:
        overlay_ids = [entry["id"] for entry in self.overlay["entries"]]
        review_ids = [entry["id"] for entry in self.review["entries"]]
        self.assertEqual(overlay_ids, review_ids)
        self.assertEqual(200, self.review["entry_count"])
        self.assertTrue(all(entry["human_review_required"] for entry in self.review["entries"]))
        self.assertTrue(all(not entry["runtime_reviewed"] for entry in self.review["entries"]))

    @unittest.skipUnless(STOCK_AVAILABLE, "installed SC/JP/TC stock resources are unavailable")
    def test_stock_replay_is_deterministic_and_install_is_unchanged(self) -> None:
        source_paths = [
            GAME_ROOT / "MSG" / language / "ev_strdata.bin"
            for language in shared.LANGUAGES
        ]
        before = {path: digest(path) for path in source_paths}
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr2-test-") as temporary:
            result = batch.build_reproducibly(GAME_ROOT, Path(temporary))
            self.assertEqual(200, result["entry_count"])
            self.assertEqual(350, result["next_start_id"])
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
