from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path


TEST_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = TEST_PATH.parents[1]
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_base_translation_batch1 as base_batch1  # noqa: E402
import build_base_translation_batch2 as batch  # noqa: E402
import build_translation_batch18 as pk_batch18  # noqa: E402
from build_literal_overlay import apply_overlay_blob  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": "TO_BE_FILLED",
    f"evidence/{batch.EVIDENCE_NAME}": "TO_BE_FILLED",
    f"review/{batch.REVIEW_NAME}": "TO_BE_FILLED",
    batch.VALIDATION_NAME: "TO_BE_FILLED",
}
EXPECTED_TARGET_SHA256 = "TO_BE_FILLED"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path} root is not an object")
    return value


class BaseMsggameTranslationBatch2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = load_json(WORKSTREAM_ROOT / "public" / batch.OVERLAY_NAME)
        cls.evidence = load_json(WORKSTREAM_ROOT / "evidence" / batch.EVIDENCE_NAME)
        cls.review = load_json(WORKSTREAM_ROOT / "review" / batch.REVIEW_NAME)
        cls.validation = load_json(WORKSTREAM_ROOT / batch.VALIDATION_NAME)

    def test_scope_is_exactly_the_next_150_visible_base_sc_literals(self) -> None:
        coordinates = batch.selected_coordinates()
        self.assertEqual(150, len(coordinates))
        self.assertEqual(79, len(batch.selected_record_keys()))
        self.assertEqual((2, 139, 0), coordinates[0])
        self.assertEqual((2, 217, 1), coordinates[-1])
        self.assertEqual((2, 218, 0), batch.NEXT_COORDINATE)
        self.assertEqual({}, batch.SKIPPED_CANDIDATES)

        source_paths = {
            language: batch.WORKSPACE_ROOT / batch.SOURCE_PATHS[language]
            for language in batch.LANGUAGES
        }
        if not all(path.is_file() for path in source_paths.values()):
            self.skipTest("commercial base resources are intentionally absent")
        loaded = batch.previous.load_sources(source_paths)
        selected = [
            (literal.block_id, literal.record_id, literal.literal_id)
            for literal in batch.previous.iter_literals(loaded["SC"]["parsed"].archive)
            if batch.previous.is_visible_translation_candidate(literal.text)
        ]
        self.assertEqual(coordinates, selected[150:300])
        self.assertEqual(batch.NEXT_COORDINATE, selected[300])

    def test_base_scope_is_separate_from_v01_and_pk_module_state(self) -> None:
        self.assertEqual("MSG/SC/msggame.bin", batch.RESOURCE)
        self.assertEqual(("SC", "JP", "TC"), batch.LANGUAGES)
        self.assertNotIn("EN", batch.SOURCE_PATHS)
        self.assertIn("base", batch.OVERLAY_NAME)
        self.assertEqual((0, 1194, 0), base_batch1.selected_coordinates()[0])
        self.assertEqual((2, 138, 1), base_batch1.selected_coordinates()[-1])
        self.assertEqual((2, 139, 0), base_batch1.NEXT_COORDINATE)
        self.assertEqual("MSG_PK/SC/msggame.bin", pk_batch18.RESOURCE)
        self.assertEqual(("SC", "JP", "EN", "TC"), pk_batch18.LANGUAGES)
        self.assertEqual((6, 3302, 0), pk_batch18.NEXT_COORDINATE)

    def test_published_artifacts_are_source_free_and_base_pinned(self) -> None:
        self.assertEqual(150, self.overlay["entry_count"])
        self.assertEqual("MSG/SC/msggame.bin", self.overlay["resource"])
        self.assertEqual("SC", self.overlay["base_language"])
        self.assertFalse(self.overlay["distribution_policy"]["contains_commercial_source_text"])
        self.assertEqual(
            batch.selected_coordinates(),
            [
                (entry["block_id"], entry["record_id"], entry["literal_id"])
                for entry in self.overlay["entries"]
            ],
        )
        self.assertEqual({"SC", "JP", "TC"}, set(self.evidence["source_files"]))
        self.assertEqual(["SC", "JP", "TC"], self.validation["source_alignment"]["languages"])
        self.assertEqual(79, self.evidence["record_count"])
        self.assertEqual(150, self.review["entry_count"])
        self.assertTrue(self.validation["passed"])
        self.assertEqual(0, self.validation["replacement_invariants"]["failures"])
        self.assertEqual(EXPECTED_TARGET_SHA256, self.validation["offline_binary_validation"]["target_packed_sha256"])
        self.assertFalse(self.validation["offline_binary_validation"]["installed_game_file_written"])
        self.assertTrue(all(value is False for value in self.validation["safety"].values()))
        for relative, expected_hash in EXPECTED_HASHES.items():
            path = WORKSTREAM_ROOT / relative
            self.assertEqual(expected_hash, digest(path))
            self.assertEqual(
                {"cjk_unified_count": 0, "kana_count": 0},
                batch.previous.script_counts(path.read_text(encoding="utf-8")),
            )

    def test_isolated_builds_are_byte_identical_and_leave_base_sources_unchanged(self) -> None:
        source_paths = {
            language: batch.WORKSPACE_ROOT / batch.SOURCE_PATHS[language]
            for language in batch.LANGUAGES
        }
        if not all(path.is_file() for path in source_paths.values()):
            self.skipTest("commercial base resources are intentionally absent")
        source_before = {language: digest(path) for language, path in source_paths.items()}
        with tempfile.TemporaryDirectory() as temporary:
            roots = [Path(temporary) / name for name in ("isolated_a", "isolated_b")]
            results = [
                batch.build(
                    Namespace(
                        stock_sc=source_paths["SC"],
                        stock_jp=source_paths["JP"],
                        stock_tc=source_paths["TC"],
                        out_root=root,
                    )
                )
                for root in roots
            ]
            self.assertEqual(EXPECTED_TARGET_SHA256, results[0]["target_packed_sha256"])
            self.assertEqual(results[0]["target_packed_sha256"], results[1]["target_packed_sha256"])
            for relative, expected_hash in EXPECTED_HASHES.items():
                self.assertEqual((roots[0] / relative).read_bytes(), (roots[1] / relative).read_bytes())
                self.assertEqual((roots[0] / relative).read_bytes(), (WORKSTREAM_ROOT / relative).read_bytes())
                self.assertEqual(expected_hash, digest(roots[0] / relative))
        self.assertEqual(source_before, {language: digest(path) for language, path in source_paths.items()})

    def test_final_overlay_rebuilds_with_shared_builder(self) -> None:
        source_path = batch.WORKSPACE_ROOT / batch.RESOURCE
        if not source_path.is_file():
            self.skipTest("commercial base SC resource is intentionally absent")
        before = digest(source_path)
        rebuilt, manifest = apply_overlay_blob(source_path.read_bytes(), self.overlay)
        self.assertEqual(150, manifest["entry_count"])
        self.assertEqual(EXPECTED_TARGET_SHA256, hashlib.sha256(rebuilt).hexdigest().upper())
        self.assertEqual({"OK"}, set(manifest["checks"].values()))
        self.assertEqual(before, digest(source_path))


if __name__ == "__main__":
    unittest.main()
