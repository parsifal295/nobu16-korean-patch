from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MODULE = ROOT / "build_navigation_wheel_layered_rebuild_v1.py"
SPEC = importlib.util.spec_from_file_location("navigation_wheel_layered_rebuild_v1", MODULE)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class LayeredRebuildContractTests(unittest.TestCase):
    def test_scope_is_all_four_routes_and_ai_free(self) -> None:
        self.assertEqual(builder.SCHEMA, "nobu16.kr.navigation-wheel-layered-rebuild.v1")
        self.assertEqual(builder.GENERATION_POLICY, "forbidden-and-not-used")
        self.assertEqual(builder.ROUTE_ORDER, ("base_low", "base_high", "pk_low", "pk_high"))
        self.assertEqual(len(builder.TYPE_CONTRACTS), 8)

    def test_typography_contracts_keep_native_font_aspect(self) -> None:
        low = builder.TYPE_CONTRACTS[("base_low", "base_detail")]
        high = builder.TYPE_CONTRACTS[("base_high", "base_detail")]
        self.assertEqual(high.cell_size, (low.cell_size[0] * 2, low.cell_size[1] * 2))
        self.assertEqual(high.ink_height, low.ink_height * 2)
        self.assertEqual(high.ink_bottom, low.ink_bottom * 2)
        self.assertEqual(high.stroke_radius, low.stroke_radius * 2)
        self.assertEqual(high.outer_radius, low.outer_radius * 2)
        self.assertEqual((builder.LOW_OVERSAMPLE, builder.HIGH_OVERSAMPLE), (8, 4))
        self.assertEqual(low.cell_size[0] * builder.LOW_OVERSAMPLE, high.cell_size[0] * builder.HIGH_OVERSAMPLE)
        self.assertEqual(builder.FONT_SHA256, "60D6A471E9A14F4BA563612D2577B9B6CCB2D1C599A69191B3F9F82EF80A19D1")

    def test_group_and_state_contracts_total_900(self) -> None:
        counts = {family: len(builder.record_groups(family)) for family in builder.FAMILY_ORDER}
        self.assertEqual(counts, {"base_detail": 57, "base_main": 5, "pk_detail": 12, "pk_main": 1})
        self.assertEqual((57 + 5) * 6 * 2 + (12 + 1) * 6 * 2, 900)

    def test_nontext_direction_marker_contract(self) -> None:
        self.assertEqual(
            builder.NON_TEXT_MARKERS_LOW,
            {
                ("base_detail", 33): ("right", (72, 71, 86, 80)),
                ("base_detail", 34): ("right", (75, 69, 82, 82)),
                ("base_detail", 35): ("right", (73, 72, 85, 80)),
                ("base_detail", 36): ("left", (18, 69, 25, 83)),
                ("base_main", 1): ("right", (81, 77, 89, 90)),
                ("base_main", 2): ("left", (15, 77, 23, 90)),
                ("base_main", 3): ("left", (15, 77, 23, 90)),
                ("base_main", 4): ("right", (81, 77, 89, 90)),
            },
        )

    def test_marker_component_is_removed_from_text_and_protected(self) -> None:
        core = builder.np.zeros((95, 100), dtype=builder.np.uint8)
        core[74:78, 75:80] = 255
        core[73:82, 40:48] = 255
        text, marker, protected, report = builder.split_text_and_marker_core(core, "base_detail", 33, 1)
        self.assertEqual(builder.bbox(text), [40, 73, 48, 82])
        self.assertEqual(builder.bbox(marker), [75, 74, 80, 78])
        self.assertIsNotNone(report)
        assert report is not None
        self.assertEqual(report["side"], "right")
        self.assertFalse(bool(builder.np.any(text[marker > 0])))
        self.assertTrue(bool(builder.np.all(protected[marker > 0])))
        self.assertFalse(bool(builder.np.any(protected[:, :74])))


if __name__ == "__main__":
    unittest.main()
