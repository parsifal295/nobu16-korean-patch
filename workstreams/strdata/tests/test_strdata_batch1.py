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
import build_structure_inventory as inventory  # noqa: E402
import build_translation_batch1 as batch  # noqa: E402
from strdata_format import rebuild_raw_strdata  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": "9B1C3F1B2C3C1BFC44974C6C2E1573DA6C48433B9E945EEF6EC5BE2C54B85F24",
    f"evidence/{batch.EVIDENCE_NAME}": "1ADE91F00FEA86B9D7CB5C7FBAA7711AA31D0DD3CEC79E1EEB4C5A08665017F2",
    f"review/{batch.REVIEW_NAME}": "26D97B83196A941767EAE06992D6608F9E5A9B5F50AFE27443C786E0D201004F",
    batch.VALIDATION_NAME: "114158A02D52868F50FB90258E849AB0E9587A1591CB9513D4FA0EC15619E7F4",
}
EXPECTED_INVENTORY_SHA256 = "E3D9B6B6C92ABC6E115A23FDF8E9DA9073DA433C49341966491285B4A9F3E2AC"
EXPECTED_SLOT_COUNTS = [25069, 4100, 3000, 122, 20]
EXPECTED_NONEMPTY_COUNTS = {
    "SC": [21115, 3240, 2207, 122, 6],
    "JP": [22289, 3261, 2221, 122, 6],
    "TC": [21002, 3240, 2207, 122, 6],
}
STOCK_AVAILABLE = all(
    (GAME_ROOT / "MSG" / language / "strdata.bin").is_file()
    for language in inventory.LANGUAGES
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load(relative: str) -> dict[str, object]:
    return json.loads(
        (WORKSTREAM_ROOT / relative).read_text(encoding="utf-8"),
        object_pairs_hook=common.strict_object,
    )


class StrdataBatch1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inventory = load("public/structure_inventory.v0.1.json")
        cls.overlay = load(f"public/{batch.OVERLAY_NAME}")
        cls.evidence = load(f"evidence/{batch.EVIDENCE_NAME}")
        cls.review = load(f"review/{batch.REVIEW_NAME}")
        cls.validation = load(batch.VALIDATION_NAME)

    def test_structure_inventory_contract_and_source_free(self) -> None:
        self.assertEqual("nobu16.kr.strdata-structure-inventory.v1", self.inventory["schema"])
        self.assertEqual(batch.RESOURCE, self.inventory["resource"])
        self.assertEqual(EXPECTED_SLOT_COUNTS, self.inventory["expected_slot_counts"])
        self.assertEqual(["SC", "JP", "TC"], self.inventory["languages"])
        self.assertEqual(["SC", "JP", "TC"], self.inventory["raw_parse_rebuild_byte_exact_languages"])
        self.assertFalse(self.inventory["contains_commercial_source_text"])
        self.assertEqual(
            {"han_or_kana_count": 0, "embedded_nul_count": 0},
            inventory.source_free_counts(
                (WORKSTREAM_ROOT / "public/structure_inventory.v0.1.json").read_bytes()
            ),
        )
        for language, expected_counts in EXPECTED_NONEMPTY_COUNTS.items():
            with self.subTest(language=language):
                self.assertEqual(
                    expected_counts,
                    self.inventory["source_files"][language]["block_display_nonempty_counts"],
                )

    @unittest.skipUnless(STOCK_AVAILABLE, "installed SC/JP/TC stock resources are unavailable")
    def test_structure_inventory_regenerates_byte_identically(self) -> None:
        with tempfile.TemporaryDirectory(prefix="nobu16-strdata-inventory-test-") as temporary:
            result = inventory.build(GAME_ROOT, Path(temporary))
        self.assertEqual(EXPECTED_INVENTORY_SHA256, result["artifact"]["sha256"])
        self.assertEqual(
            {"han_or_kana_count": 0, "embedded_nul_count": 0},
            result["source_free_scan"],
        )

    @unittest.skipUnless(STOCK_AVAILABLE, "installed SC/JP/TC stock resources are unavailable")
    def test_parser_rebuilds_every_stock_language_byte_exactly(self) -> None:
        loaded, before = inventory.load_sources(GAME_ROOT)
        for language in inventory.LANGUAGES:
            with self.subTest(language=language):
                archive = loaded[language]["archive"]
                self.assertEqual(EXPECTED_SLOT_COUNTS, [block.slot_count for block in archive.blocks])
                self.assertEqual(
                    EXPECTED_NONEMPTY_COUNTS[language],
                    list(loaded[language]["nonempty_counts"]),
                )
                self.assertEqual(loaded[language]["raw"], rebuild_raw_strdata(archive))
        after = {
            relative: digest(GAME_ROOT / Path(relative))
            for relative in before
        }
        self.assertEqual(before, after)

    def test_batch_scope_overlay_and_alignment_are_coordinate_based(self) -> None:
        batch.validate_overlay_shape(self.overlay)
        coordinates = [
            (int(entry["block_id"]), int(entry["slot_id"]))
            for entry in self.overlay["entries"]
        ]
        self.assertEqual(batch.selected_coordinates(), coordinates)
        self.assertEqual(batch.TRANSLATED_COUNT, self.overlay["entry_count"])
        self.assertEqual([0, 0], self.validation["scope"]["first_coordinate"])
        self.assertEqual([0, 99], self.validation["scope"]["last_coordinate"])
        self.assertEqual([0, 100], self.validation["scope"]["next_coordinate"])
        self.assertEqual(100, self.evidence["entry_count"])
        self.assertEqual(["SC", "JP", "TC"], self.validation["source_alignment"]["languages"])
        self.assertEqual(300, self.validation["source_alignment"]["translated_reference_hash_count"])
        self.assertFalse(self.overlay["distribution_policy"]["contains_commercial_source_text"])
        self.assertFalse(self.evidence["contains_commercial_source_text"])

    def test_cross_resource_translation_memory_is_not_automatic_reuse(self) -> None:
        review = self.validation["cross_resource_translation_memory_review"]
        self.assertTrue(review["policy"]["matching_source_hash_is_translation_memory_only"])
        self.assertFalse(review["policy"]["automatic_reuse_permitted"])
        self.assertTrue(review["policy"]["independent_strdata_coordinate_context_reviewed"])
        summary = review["summary"]
        self.assertEqual(100, summary["strdata_coordinate_count"])
        self.assertEqual(90, summary["coordinates_with_matching_source_hash_candidate"])
        self.assertEqual(10, summary["coordinates_without_matching_source_hash_candidate"])
        self.assertEqual(0, summary["automatic_reuse_count"])
        self.assertEqual(2, summary["ambiguous_reference_candidate_coordinate_count"])
        self.assertEqual(
            review,
            self.evidence["cross_resource_translation_memory_review"],
        )

    def test_review_and_validation_record_pending_runtime_review_and_safety(self) -> None:
        self.assertEqual(100, self.review["entry_count"])
        self.assertTrue(all(entry["human_review_required"] for entry in self.review["entries"]))
        self.assertTrue(all(not entry["runtime_reviewed"] for entry in self.review["entries"]))
        self.assertTrue(self.validation["passed"])
        self.assertEqual(100, self.validation["replacement_invariants"]["checked"])
        self.assertEqual(0, self.validation["replacement_invariants"]["failures"])
        self.assertTrue(self.validation["raw_binary_validation"]["coordinate_set_preserved"])
        self.assertTrue(self.validation["raw_binary_validation"]["unselected_texts_preserved"])
        for key, value in self.validation["safety"].items():
            with self.subTest(key=key):
                self.assertFalse(value)

    def test_public_artifacts_are_pinned_and_source_free(self) -> None:
        paths = {
            "public/structure_inventory.v0.1.json": EXPECTED_INVENTORY_SHA256,
            **EXPECTED_HASHES,
        }
        for relative, expected_hash in paths.items():
            with self.subTest(relative=relative):
                path = WORKSTREAM_ROOT / relative
                self.assertEqual(expected_hash, digest(path))
                self.assertEqual(
                    {"han_or_kana_count": 0, "embedded_nul_count": 0},
                    inventory.source_free_counts(path.read_bytes()),
                )

    @unittest.skipUnless(STOCK_AVAILABLE, "installed SC/JP/TC stock resources are unavailable")
    def test_reproducible_replay_preserves_installed_sources(self) -> None:
        source_paths = [
            GAME_ROOT / "MSG" / language / "strdata.bin"
            for language in inventory.LANGUAGES
        ]
        before = {path: digest(path) for path in source_paths}
        with tempfile.TemporaryDirectory(prefix="nobu16-strdata-b01-test-") as temporary:
            result = batch.build_reproducibly(GAME_ROOT, Path(temporary))
        self.assertEqual(100, result["entry_count"])
        self.assertEqual((0, 100), result["next_coordinate"])
        self.assertEqual(
            EXPECTED_HASHES,
            {
                artifact["path"]: artifact["sha256"]
                for artifact in result["artifacts"].values()
            },
        )
        after = {path: digest(path) for path in source_paths}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
