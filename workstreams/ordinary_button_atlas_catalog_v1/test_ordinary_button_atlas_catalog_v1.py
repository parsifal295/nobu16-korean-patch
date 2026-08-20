from __future__ import annotations

import csv
import json
import unittest
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class OrdinaryButtonAtlasCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads((ROOT / "ordinary_button_catalog_v1.json").read_text(encoding="utf-8"))
        cls.rows = cls.catalog["placements"]

    def test_schema_and_complete_coverage(self) -> None:
        self.assertEqual(self.catalog["schema"], "nobu16.kr.ordinary-button-atlas-catalog.v1")
        self.assertEqual(
            self.catalog["coverage"],
            {
                "physical_archives": 4,
                "texture_routes": 5,
                "logical_groups": 22,
                "standard_groups": 20,
                "standard_states_each": 6,
                "battle_start_groups": 1,
                "battle_start_states": 7,
                "approve_all_groups": 1,
                "approve_all_routes": 2,
                "approve_all_states_each": 6,
                "approve_all_placements": 12,
                "placements": 266,
            },
        )
        self.assertEqual(len(self.rows), 266)

    def test_five_verified_runtime_routes(self) -> None:
        expected = {
            "common_low": ("RES_JP/res_lang.bin", 5, 0, 3856, 1, "0x5B", [4096, 2048], 127),
            "pk_low_approve_all": ("RES_JP_PK/res_lang_exp_pk.bin", 4, 0, 870, 1, "0x5F", [2048, 512], 6),
            "common_high_standard": ("RES_JP_PK_PORT/res_lang_pk_port1.bin", 2, 0, 3860, 1, "0x5B", [4096, 4096], 120),
            "common_high_battle": ("RES_JP_PK_PORT/res_lang_pk_port1.bin", 2, 0, 3860, 2, "0x5B", [4096, 2048], 7),
            "pk_high_approve_all": ("RES_JP_PK_PORT/res_lang_pk_port2.bin", 2, 0, 870, 1, "0x5F", [4096, 1024], 6),
        }
        for route_id, values in expected.items():
            route = self.catalog["routes"][route_id]
            actual = (
                route["archive"], route["outer_entry"], route["nested_slot"], route["resource_id"],
                route["texture_index"], route["format_code"], route["dimensions"], route["placement_count"],
            )
            self.assertEqual(actual, values)

    def test_route_and_family_counts(self) -> None:
        self.assertEqual(
            Counter(row["route"] for row in self.rows),
            Counter({"common_low": 127, "pk_low_approve_all": 6, "common_high_standard": 120, "common_high_battle": 7, "pk_high_approve_all": 6}),
        )
        self.assertEqual(Counter(row["family"] for row in self.rows), Counter({"standard": 240, "battle_start": 14, "approve_all": 12}))

    def test_all_twenty_standard_labels_have_six_states_per_resolution(self) -> None:
        labels = [item["name"] for item in self.catalog["labels"][:20]]
        self.assertEqual(len(labels), 20)
        by_key: dict[tuple[str, str], list[int]] = defaultdict(list)
        for row in self.rows:
            if row["family"] == "standard":
                by_key[(row["route"], row["name"])].append(row["state"])
        self.assertEqual(len(by_key), 40)
        for route in ("common_low", "common_high_standard"):
            for name in labels:
                self.assertEqual(sorted(by_key[(route, name)]), list(range(1, 7)))

    def test_native_geometry_contracts_are_not_forced_to_two_x(self) -> None:
        for row in self.rows:
            if row["family"] != "standard":
                continue
            if row["route"] == "common_low":
                self.assertEqual(row["artwork_size"], [180, 79])
                self.assertEqual(row["processing_size"], [192, 88])
            elif row["route"] == "common_high_standard":
                self.assertEqual(row["artwork_size"], [360, 158])
                self.assertEqual(row["processing_size"], [376, 168])
        battle_high = [row for row in self.rows if row["route"] == "common_high_battle"]
        self.assertEqual(battle_high[0]["processing_size"], [508, 154])
        self.assertEqual({tuple(row["processing_size"]) for row in battle_high[1:]}, {(493, 146)})

    def test_rectangles_and_block_contracts_are_valid(self) -> None:
        dimensions = {key: value["dimensions"] for key, value in self.catalog["routes"].items()}
        keys = set()
        for row in self.rows:
            key = (row["route"], row["family"], row["group"], row["state"])
            self.assertNotIn(key, keys)
            keys.add(key)
            width, height = dimensions[row["route"]]
            x0, y0, x1, y1 = row["atlas_clip_rect"]
            self.assertTrue(0 <= x0 < x1 <= width)
            self.assertTrue(0 <= y0 < y1 <= height)
            expected_blocks = [x0 // 4, y0 // 4, (x1 + 3) // 4, (y1 + 3) // 4]
            self.assertEqual(row["bc_block_rect"], expected_blocks)
            self.assertEqual(row["bc_pixel_rect"], [value * 4 for value in expected_blocks])
        self.assertEqual(len(keys), 266)

    def test_only_low_battle_processing_canvases_cross_atlas_boundary(self) -> None:
        clipped = [row for row in self.rows if row["boundary_clipped"]]
        self.assertEqual(len(clipped), 7)
        self.assertTrue(all(row["route"] == "common_low" and row["family"] == "battle_start" for row in clipped))

    def test_approve_all_bc7_cells_are_block_aligned(self) -> None:
        rows = [row for row in self.rows if row["family"] == "approve_all"]
        self.assertEqual(len(rows), 12)
        for route, size in (("pk_low_approve_all", [192, 88]), ("pk_high_approve_all", [368, 160])):
            route_rows = [row for row in rows if row["route"] == route]
            self.assertEqual(
                [row["state_variant"] for row in route_rows],
                ["white", "cyan", "blue", "disabled", "cyan_alt", "disabled_alt"],
            )
            for row in route_rows:
                self.assertEqual(row["ko"], "전체승인")
                self.assertEqual(row["processing_size"], size)
                self.assertTrue(all(value % 4 == 0 for value in row["processing_rect"]))
                self.assertEqual(row["processing_rect"], row["bc_pixel_rect"])

    def test_generated_tables_cover_every_placement_and_group(self) -> None:
        with (ROOT / "ordinary_button_placements_v1.csv").open("r", encoding="utf-8-sig", newline="") as stream:
            self.assertEqual(sum(1 for _ in csv.DictReader(stream)), 266)
        text = (ROOT / "ORDINARY_BUTTON_POSITIONS_KO.md").read_text(encoding="utf-8")
        table_rows = [line for line in text.splitlines() if line.startswith("| `")]
        self.assertEqual(len(table_rows), 44)
        for route_id in self.catalog["route_order"]:
            self.assertEqual(text.count(f"## {route_id}"), 1)


if __name__ == "__main__":
    unittest.main()
