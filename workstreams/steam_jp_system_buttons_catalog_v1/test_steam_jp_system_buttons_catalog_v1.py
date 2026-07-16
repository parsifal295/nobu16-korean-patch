"""Contract tests for the source-free Steam JP system-button catalog."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
CATALOG_PATH = WORKSTREAM / "catalog.v1.json"


def load_catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def assert_rect(test: unittest.TestCase, rect: object, width: int, height: int) -> None:
    test.assertIsInstance(rect, list)
    test.assertEqual(len(rect), 4)
    left, top, right, bottom = rect
    test.assertTrue(all(isinstance(value, int) for value in rect))
    test.assertGreaterEqual(left, 0)
    test.assertGreaterEqual(top, 0)
    test.assertLess(left, right)
    test.assertLess(top, bottom)
    test.assertLessEqual(right, width)
    test.assertLessEqual(bottom, height)


def has_cjk_or_kana(value: str) -> bool:
    return any(
        "\u3040" <= char <= "\u30ff"
        or "\u3400" <= char <= "\u4dbf"
        or "\u4e00" <= char <= "\u9fff"
        or "\uf900" <= char <= "\ufaff"
        for char in value
    )


class SystemButtonsCatalogTests(unittest.TestCase):
    def test_scope_is_catalog_only(self) -> None:
        catalog = load_catalog()
        self.assertEqual(catalog["schema"], "nobu16.kr.steam-jp-system-buttons.catalog.v1")
        self.assertTrue(catalog["candidate_generation_blocked"])
        self.assertIn("후보", catalog["candidate_generation_blocked_reason"])
        self.assertFalse(catalog["scope"]["candidate_created"])
        self.assertTrue(catalog["scope"]["candidate_generation_blocked"])
        self.assertEqual(catalog["scope"]["candidate_generation_blocked_reason"], "top-level candidate block applies.")
        self.assertFalse(catalog["scope"]["game_files_written"])
        self.assertFalse(catalog["scope"]["git_or_release_action"])
        self.assertEqual(catalog["scope"]["outer_entry"], 5)
        self.assertEqual(catalog["scope"]["nested_slot"], 0)
        self.assertEqual(catalog["scope"]["texture"], 1)

    def test_source_free_guarantees_and_no_raw_artifacts(self) -> None:
        catalog = load_catalog()
        guarantees = catalog["source_free_guarantees"]
        for key in (
            "committed_switch_archive",
            "committed_switch_container_or_payload",
            "committed_decoded_image",
            "committed_pc_game_resource",
            "committed_original_language_string",
        ):
            self.assertFalse(guarantees[key], key)
        self.assertTrue(guarantees["private_visual_reference_only"])
        forbidden_suffixes = {".bin", ".zip", ".png", ".jpg", ".jpeg", ".dds", ".g1t", ".bc3", ".pyc"}
        found = [path.name for path in WORKSTREAM.rglob("*") if path.is_file() and path.suffix.lower() in forbidden_suffixes]
        self.assertEqual(found, [])

    def test_no_original_language_characters_are_committed(self) -> None:
        for path in WORKSTREAM.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".json", ".md", ".py"}:
                self.assertFalse(has_cjk_or_kana(path.read_text(encoding="utf-8")), path)

    def test_core_v1_labels_are_disjoint(self) -> None:
        catalog = load_catalog()
        core = set(catalog["core_v1_excluded_labels_ko"])
        labels = {row["label_ko"] for row in catalog["mappings"]}
        self.assertTrue(core.isdisjoint(labels))
        self.assertEqual(len(core), 8)
        self.assertEqual(len(labels), 12)

    def test_confirmed_coordinate_contract_and_duplicate_handling(self) -> None:
        catalog = load_catalog()
        confirmed = [row for row in catalog["mappings"] if row["confidence"] == "confirmed"]
        self.assertEqual(len(confirmed), 11)
        source_rects: set[tuple[int, int, int, int]] = set()
        target_rects: set[tuple[int, int, int, int]] = set()
        state_groups: set[str] = set()
        for row in confirmed:
            assert_rect(self, row["switch_source_cell_rect"], 2048, 2048)
            assert_rect(self, row["pc_jp_target_cell_rect"], 4096, 2048)
            self.assertEqual(row["priority"], "P1")
            self.assertIn(row["canonical_state"], {"white", "cyan", "blue"})
            self.assertEqual(row["pc_native_preservation"]["background"], "confirmed")
            self.assertTrue(row["evidence"].startswith("private v2.2 Korean"))
            source = tuple(row["switch_source_cell_rect"])
            target = tuple(row["pc_jp_target_cell_rect"])
            self.assertNotIn(source, source_rects)
            self.assertNotIn(target, target_rects)
            self.assertNotIn(row["state_group_id"], state_groups)
            source_rects.add(source)
            target_rects.add(target)
            state_groups.add(row["state_group_id"])

    def test_deferred_ornamented_start_is_not_candidate_ready(self) -> None:
        catalog = load_catalog()
        deferred = [row for row in catalog["mappings"] if row["confidence"] == "deferred"]
        self.assertEqual(len(deferred), 1)
        row = deferred[0]
        self.assertEqual(row["label_ko"], "개시")
        self.assertEqual(row["priority"], "P2")
        self.assertEqual(row["canonical_state"], "ornamented_white")
        self.assertEqual(row["pc_native_preservation"]["background"], "deferred")
        self.assertIn("실제 화면", row["deferred_reason"])
        assert_rect(self, row["switch_source_cell_rect"], 2048, 2048)
        assert_rect(self, row["pc_jp_target_cell_rect"], 4096, 2048)


if __name__ == "__main__":
    unittest.main()
