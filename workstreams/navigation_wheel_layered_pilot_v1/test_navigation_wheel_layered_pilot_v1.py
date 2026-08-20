from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MODULE = ROOT / "build_navigation_wheel_layered_pilot_v1.py"
SPEC = importlib.util.spec_from_file_location("navigation_wheel_layered_pilot_v1", MODULE)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class LayeredPilotContractTests(unittest.TestCase):
    def test_scope_and_generation_policy(self) -> None:
        self.assertEqual(builder.SCHEMA, "nobu16.kr.navigation-wheel-layered-pilot.v1")
        self.assertEqual(builder.GENERATION_POLICY, "forbidden-and-not-used")
        self.assertEqual(builder.ROUTE_ID, "base_low")
        self.assertEqual(builder.PILOT_GROUP, 8)
        self.assertEqual(builder.PILOT_JP, "入城")
        self.assertEqual(builder.PILOT_KO, "입성")
        self.assertEqual(builder.CELL_SIZE, (100, 95))
        self.assertEqual(builder.STATE_COUNT, 6)

    def test_selected_b_rendering_contract(self) -> None:
        self.assertEqual(builder.TARGET_INK_HEIGHT, 21)
        self.assertEqual(builder.INK_BOTTOM, 85)
        self.assertEqual(builder.SAFE_INK_WIDTH, 88)
        self.assertEqual(builder.STROKE_RADIUS, 1.4)
        self.assertEqual(builder.OUTER_RADIUS, 3.0)
        self.assertEqual(builder.FONT_SHA256, "60D6A471E9A14F4BA563612D2577B9B6CCB2D1C599A69191B3F9F82EF80A19D1")
        self.assertEqual([item.state for item in builder.STATE_PALETTES], list(range(1, 7)))
        self.assertEqual(builder.STATE_PALETTES[1].fill, builder.STATE_PALETTES[4].fill)
        self.assertEqual(builder.STATE_PALETTES[3].fill, builder.STATE_PALETTES[5].fill)

    def test_official_locale_pin_table_covers_all_routes(self) -> None:
        data = json.loads((ROOT / "official_locale_inputs_v1.json").read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], "nobu16.kr.navigation-wheel-official-locale-inputs.v1")
        rows = data["files"]
        self.assertEqual(len(rows), 12)
        self.assertEqual({row["locale"] for row in rows}, {"SC", "TC", "EN"})
        self.assertEqual({row["route"] for row in rows}, {"base_low", "base_high", "pk_low", "pk_high"})
        self.assertEqual(len({(row["locale"], row["route"]) for row in rows}), 12)
        for row in rows:
            self.assertGreater(row["size"], 0)
            self.assertEqual(len(row["sha256"]), 64)
            int(row["sha256"], 16)


if __name__ == "__main__":
    unittest.main()
