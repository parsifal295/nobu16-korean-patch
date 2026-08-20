from __future__ import annotations

import csv
import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class NavigationWheelAtlasCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = json.loads((ROOT / "navigation_wheel_catalog_v1.json").read_text(encoding="utf-8"))
        cls.metrics = json.loads((ROOT / "wheel_geometry_metrics_v1.json").read_text(encoding="utf-8"))

    def test_catalog_schema_and_coverage(self) -> None:
        self.assertEqual(self.catalog["schema"], "nobu16.kr.navigation-wheel-atlas-catalog.v1")
        self.assertEqual(self.catalog["coverage"]["routes"], 4)
        self.assertEqual(self.catalog["coverage"]["placements"], 900)
        self.assertEqual(len(self.catalog["placements"]), 900)
        counts = Counter(row["route"] for row in self.catalog["placements"])
        self.assertEqual(counts, Counter({"base_low": 372, "base_high": 372, "pk_low": 78, "pk_high": 78}))
        families = Counter(row["family"] for row in self.catalog["placements"])
        self.assertEqual(
            families,
            Counter({"base_detail": 684, "base_main": 60, "pk_detail": 144, "pk_main": 12}),
        )

    def test_routes_are_the_four_verified_runtime_locations(self) -> None:
        expected = {
            "base_low": ("RES_JP/res_lang.bin", 8, 0, 474, 0, [2048, 2048], 372),
            "base_high": ("RES_JP_PK_PORT/res_lang_pk_port1.bin", 3, 0, 474, 0, [4096, 4096], 372),
            "pk_low": ("RES_JP_PK/res_lang_pk.bin", 1, 0, 81, 0, [1024, 1024], 78),
            "pk_high": ("RES_JP_PK_PORT/res_lang_pk_port2.bin", 3, 0, 81, 0, [2048, 2048], 78),
        }
        for route_id, values in expected.items():
            route = self.catalog["routes"][route_id]
            actual = (
                route["archive"], route["outer_entry"], route["nested_slot"], route["resource_id"],
                route["texture_index"], route["dimensions"], route["placement_count"],
            )
            self.assertEqual(actual, values)
            self.assertEqual(route["format_code"], "0x5B")

    def test_every_placement_key_and_bc3_rect_is_valid(self) -> None:
        keys = set()
        dimensions = {key: value["dimensions"] for key, value in self.catalog["routes"].items()}
        for row in self.catalog["placements"]:
            key = (row["route"], row["family"], row["group"], row["state"], row["metadata_record"])
            self.assertNotIn(key, keys)
            keys.add(key)
            self.assertIn(row["state"], range(1, 7))
            x0, y0, x1, y1 = row["atlas_clip_rect"]
            width, height = dimensions[row["route"]]
            self.assertTrue(0 <= x0 < x1 <= width)
            self.assertTrue(0 <= y0 < y1 <= height)
            self.assertEqual(row["bc3_block_rect"], [x0 // 4, y0 // 4, (x1 + 3) // 4, (y1 + 3) // 4])
        self.assertEqual(len(keys), 900)

    def test_metadata_record_coverage(self) -> None:
        by_route: dict[str, set[int]] = {}
        for row in self.catalog["placements"]:
            by_route.setdefault(row["route"], set()).add(row["metadata_record"])
        expected_base = set(range(18, 282)) | set(range(282, 390))
        expected_pk = set(range(0, 78))
        self.assertEqual(by_route["base_low"], expected_base)
        self.assertEqual(by_route["base_high"], expected_base)
        self.assertEqual(by_route["pk_low"], expected_pk)
        self.assertEqual(by_route["pk_high"], expected_pk)

    def test_structural_scale_contracts_pin_pk_non_2x_cells(self) -> None:
        contracts = self.catalog["structural_scale_contracts"]
        self.assertEqual(contracts["base_detail"]["logical_high_over_low"], [2.0, 2.0])
        self.assertEqual(contracts["base_main"]["logical_high_over_low"], [2.0, 2.0])
        self.assertEqual(contracts["pk_detail"]["logical_cell_low"], [104, 96])
        self.assertEqual(contracts["pk_detail"]["logical_cell_high"], [200, 184])
        self.assertEqual(contracts["pk_main"]["metadata_core_high"], [196, 180])
        self.assertEqual(contracts["pk_main"]["logical_cell_high"], [204, 188])

    def test_base_sizes_are_2x_but_atlas_positions_are_independently_packed(self) -> None:
        by_key = {
            (row["route"], row["family"], row["group"], row["state"]): row
            for row in self.catalog["placements"]
        }
        independently_packed = 0
        for low in (row for row in self.catalog["placements"] if row["route"] == "base_low"):
            high = by_key[("base_high", low["family"], low["group"], low["state"])]
            self.assertEqual(high["metadata_rect"][2:], [value * 2 for value in low["metadata_rect"][2:]])
            self.assertEqual(high["logical_size"], [value * 2 for value in low["logical_size"]])
            if high["metadata_rect"][:2] != [value * 2 for value in low["metadata_rect"][:2]]:
                independently_packed += 1
        self.assertEqual(independently_packed, 372)

    def test_metrics_pin_current_geometry_finding(self) -> None:
        self.assertEqual(self.metrics["schema"], "nobu16.kr.navigation-wheel-geometry-metrics.v1")
        self.assertEqual(len(self.metrics["rows"]), 900)
        self.assertEqual(len(self.metrics["resolution_scale_rows"]), 450)
        overall = self.metrics["summary"]["overall"]
        self.assertEqual(overall["full_sprite_outliers_5pct"], 858)
        self.assertEqual(overall["body_proxy_outliers_5pct"], 858)
        self.assertEqual(overall["body_proxy_target_over_source_width"]["median"], 0.890244)
        self.assertEqual(overall["label_proxy_target_over_source_width"]["median"], 0.811828)
        self.assertEqual(overall["target_over_source_width"]["median"], 0.890244)
        self.assertEqual(overall["target_over_source_height"]["median"], 0.928571)
        base_detail = self.metrics["summary"]["by_family"]["base_detail"]
        self.assertEqual(base_detail["full_sprite_outliers_5pct"], 684)
        self.assertEqual(base_detail["target_over_source_width"]["min"], 0.682927)
        scale = self.metrics["summary"]["resolution_scale"]["overall"]
        self.assertEqual(scale["source_scale_outliers_5pct"], 1)
        self.assertEqual(scale["target_scale_outliers_5pct"], 3)
        self.assertTrue(self.metrics["methodology"]["body_band_is_not_body_layer"])
        self.assertTrue(self.metrics["methodology"]["label_band_is_not_font_only"])

    def test_generated_csv_row_counts(self) -> None:
        expected = {
            "navigation_wheel_placements_v1.csv": 900,
            "wheel_geometry_metrics_v1.csv": 900,
            "wheel_resolution_scale_v1.csv": 450,
        }
        for name, count in expected.items():
            with (ROOT / name).open("r", encoding="utf-8-sig", newline="") as stream:
                self.assertEqual(sum(1 for _ in csv.DictReader(stream)), count, name)

    def test_human_readable_position_table_covers_all_groups(self) -> None:
        text = (ROOT / "NAVIGATION_WHEEL_POSITIONS_KO.md").read_text(encoding="utf-8")
        self.assertEqual(text.count("## base_low"), 1)
        self.assertEqual(text.count("## base_high"), 1)
        self.assertEqual(text.count("## pk_low"), 1)
        self.assertEqual(text.count("## pk_high"), 1)
        table_rows = [line for line in text.splitlines() if line.startswith("| `")]
        self.assertEqual(len(table_rows), 150)  # (57+5)*2 + (12+1)*2


if __name__ == "__main__":
    unittest.main()
