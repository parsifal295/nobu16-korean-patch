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

import build_translation_batch19 as batch19  # noqa: E402
import build_translation_batch20 as batch  # noqa: E402
from build_literal_overlay import apply_overlay_blob  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": "EB7FD44B58DCEE05827FB730986650CE6A2F527E63FE7365F2D75B63E9D11112",
    f"evidence/{batch.EVIDENCE_NAME}": "02F9CE0F3A2F06CDEADAE3EB52167CE062E6D18BEC87440D93A847708C0C1DA2",
    f"review/{batch.REVIEW_NAME}": "72AE63086945610661BB680ED3523594003BDA822564B104DA4CBCA98DD41741",
    batch.VALIDATION_NAME: "C138929952E9F48BCFD58E75228CAAED90EEB11EE5E9D8CBC3E4571E31D19A2C",
}
EXPECTED_TARGET_SHA256 = "254C6BAEC4A8CD3530090CA6677D9E1FA30048141AB9B6E548776F1A1A480BEF"
PRIOR_OVERLAYS = (
    "msggame_ko_system_messages_b01r0003_b02r0086_0197.v0.1.json",
    "msggame_ko_system_messages_b02r0198_0297.v0.2.json",
    "msggame_ko_system_messages_b02r0298_0565.v0.3.json",
    "msggame_ko_system_messages_b02r0566_0665.v0.4.json",
    "msggame_ko_system_messages_b02r0666_b04r0075.v0.5.json",
    "msggame_ko_system_messages_b04r0076_b06r0559.v0.6.json",
    "msggame_ko_system_messages_b06r0560_0947.v0.7.json",
    "msggame_ko_system_messages_b06r0948_1205.v0.8.json",
    "msggame_ko_system_messages_b06r1209_1384.v0.9.json",
    "msggame_ko_system_messages_b06r1385_1514.v0.10.json",
    "msggame_ko_system_messages_b06r1515_1677.v0.11.json",
    "msggame_ko_system_messages_b06r1677_1838.v0.12.json",
    "msggame_ko_system_messages_b06r1839_1991.v0.13.json",
    "msggame_ko_system_messages_b06r1993_2139.v0.14.json",
    "msggame_ko_system_messages_b06r2139_2436.v0.15.json",
    "msggame_ko_system_messages_b06r2436_2787.v0.16.json",
    "msggame_ko_system_messages_b06r2787_3050.v0.17.json",
    "msggame_ko_system_messages_b06r3050_3298.v0.18.json",
    "msggame_ko_system_messages_b06r3302_3477.v0.19.json",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path} root is not an object")
    return value


class MsggameTranslationBatch20Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = load_json(WORKSTREAM_ROOT / "public" / batch.OVERLAY_NAME)
        cls.evidence = load_json(WORKSTREAM_ROOT / "evidence" / batch.EVIDENCE_NAME)
        cls.review = load_json(WORKSTREAM_ROOT / "review" / batch.REVIEW_NAME)
        cls.validation = load_json(WORKSTREAM_ROOT / batch.VALIDATION_NAME)

    def test_scope_is_exactly_the_next_150_visible_sc_literals(self) -> None:
        coordinates = batch.selected_coordinates()
        self.assertEqual(150, len(coordinates))
        self.assertEqual(85, len(batch.selected_record_keys()))
        self.assertEqual((6, 3478, 0), coordinates[0])
        self.assertEqual((6, 3697, 1), coordinates[-1])
        self.assertEqual((6, 3698, 0), batch.NEXT_COORDINATE)
        self.assertEqual({}, batch.SKIPPED_CANDIDATES)

        source_paths = {
            language: batch.WORKSPACE_ROOT / batch.SOURCE_PATHS[language]
            for language in batch.LANGUAGES
        }
        if not all(path.is_file() for path in source_paths.values()):
            self.skipTest("commercial stock resources are intentionally absent")
        loaded = batch.previous.load_sources(source_paths)
        records = batch.previous._record_map(loaded["SC"]["parsed"].archive)
        selected: list[tuple[int, int, int]] = []
        following: tuple[int, int, int] | None = None
        for (block_id, record_id), record in sorted(records.items()):
            if (block_id, record_id) < (6, 3478):
                continue
            for literal in batch.previous.parse_record_literals(record):
                if not batch.previous.is_visible_translation_candidate(literal.text):
                    continue
                coordinate = (block_id, record_id, literal.literal_id)
                if len(selected) == 150:
                    following = coordinate
                    break
                selected.append(coordinate)
            if following is not None:
                break
        self.assertEqual(coordinates, selected)
        self.assertEqual(batch.NEXT_COORDINATE, following)

    def test_private_engine_preserves_v19_empty_slot_behavior_without_using_it_here(self) -> None:
        self.assertEqual((6, 3302, 0), batch19.selected_coordinates()[0])
        self.assertEqual((6, 3477, 0), batch19.selected_coordinates()[-1])
        self.assertEqual((6, 3478, 0), batch19.NEXT_COORDINATE)
        self.assertFalse(batch19.previous.is_visible_translation_candidate(""))
        self.assertTrue(batch19._engine.previous.is_visible_translation_candidate(""))
        self.assertFalse(batch.previous.is_visible_translation_candidate(""))
        self.assertIsNot(batch._engine, batch19._engine)
        self.assertTrue(all(value is not None for values in batch.TRANSLATIONS.values() for value in values))

    def test_published_artifacts_are_source_free_and_pinned(self) -> None:
        self.assertEqual(150, self.overlay["entry_count"])
        self.assertEqual("MSG_PK/SC/msggame.bin", self.overlay["resource"])
        self.assertEqual("SC", self.overlay["base_language"])
        self.assertFalse(self.overlay["distribution_policy"]["contains_commercial_source_text"])
        coordinates = [
            (entry["block_id"], entry["record_id"], entry["literal_id"])
            for entry in self.overlay["entries"]
        ]
        self.assertEqual(batch.selected_coordinates(), coordinates)
        for entry in self.overlay["entries"]:
            self.assertRegex(entry["source_sc_utf16le_sha256"], r"^[0-9A-F]{64}$")
            self.assertTrue(entry["ko"])
            self.assertNotIn("\x00", entry["ko"])
        self.assertEqual(85, self.evidence["record_count"])
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

    def test_scope_does_not_overlap_prior_pk_overlays(self) -> None:
        prior: set[tuple[int, int, int]] = set()
        for name in PRIOR_OVERLAYS:
            overlay = load_json(WORKSTREAM_ROOT / "public" / name)
            self.assertEqual("MSG_PK/SC/msggame.bin", overlay["resource"])
            prior.update(
                (entry["block_id"], entry["record_id"], entry["literal_id"])
                for entry in overlay["entries"]
            )
        self.assertTrue(set(batch.selected_coordinates()).isdisjoint(prior))

    def test_isolated_builds_are_byte_identical_and_leave_sources_unchanged(self) -> None:
        source_paths = {
            language: batch.WORKSPACE_ROOT / batch.SOURCE_PATHS[language]
            for language in batch.LANGUAGES
        }
        if not all(path.is_file() for path in source_paths.values()):
            self.skipTest("commercial stock resources are intentionally absent")
        source_before = {language: digest(path) for language, path in source_paths.items()}
        with tempfile.TemporaryDirectory() as temporary:
            roots = [Path(temporary) / name for name in ("isolated_a", "isolated_b")]
            results = [
                batch.build(
                    Namespace(
                        stock_sc=source_paths["SC"],
                        stock_jp=source_paths["JP"],
                        stock_en=source_paths["EN"],
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
            self.skipTest("commercial stock SC resource is intentionally absent")
        before = digest(source_path)
        rebuilt, manifest = apply_overlay_blob(source_path.read_bytes(), self.overlay)
        self.assertEqual(150, manifest["entry_count"])
        self.assertEqual(EXPECTED_TARGET_SHA256, hashlib.sha256(rebuilt).hexdigest().upper())
        self.assertEqual({"OK"}, set(manifest["checks"].values()))
        self.assertEqual(before, digest(source_path))


if __name__ == "__main__":
    unittest.main()
