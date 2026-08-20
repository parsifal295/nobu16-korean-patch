from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("build_ordinary_button_approve_all_layered_v1.py")
SPEC = importlib.util.spec_from_file_location("ordinary_button_approve_all_layered_v1", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class OrdinaryButtonApproveAllLayeredTests(unittest.TestCase):
    def test_label_contract_has_no_space(self) -> None:
        self.assertEqual(MODULE.LABEL, "전체승인")
        self.assertNotIn(" ", MODULE.LABEL)
        self.assertEqual(MODULE.VARIANT, "approve_all_compact")
        self.assertEqual(MODULE.ASPECT_SCALE_X, 0.80)
        self.assertEqual(MODULE.TRACKING_GRADE, "standard")
        self.assertEqual(MODULE.TRACKING_EM, MODULE.pilot.TRACKING_EM)

    def test_native_route_contracts(self) -> None:
        low, high = MODULE.ROUTES
        self.assertEqual(
            (low.relative_path, low.outer_entry, low.resource_id, low.texture_index, low.dimensions),
            ("RES_JP_PK/res_lang_exp_pk.bin", 4, 870, 1, (2048, 512)),
        )
        self.assertEqual(
            (high.relative_path, high.outer_entry, high.resource_id, high.texture_index, high.dimensions),
            ("RES_JP_PK_PORT/res_lang_pk_port2.bin", 2, 870, 1, (4096, 1024)),
        )
        self.assertEqual(low.cell_size, (192, 88))
        self.assertEqual(high.cell_size, (368, 160))

    def test_low_cells_are_detected_native_cells_not_halved_high_cells(self) -> None:
        low, high = MODULE.ROUTES
        low_rects = low.primary_rects["JP"]
        halved_high = tuple(tuple(value // 2 for value in rect) for rect in high.primary_rects["JP"])
        self.assertNotEqual(low_rects, halved_high)
        self.assertEqual(low_rects, MODULE.LOW_JP_RECTS)
        self.assertEqual({(r[2] - r[0], r[3] - r[1]) for r in low_rects}, {(192, 88)})

    def test_six_states_and_compact_donors_are_block_aligned(self) -> None:
        for route in MODULE.ROUTES:
            for table in (route.primary_rects, route.compact_rects):
                self.assertEqual(set(table), set(MODULE.LOCALES))
                for rects in table.values():
                    self.assertEqual(len(rects), 6)
                    for left, top, right, bottom in rects:
                        self.assertEqual((right - left, bottom - top), route.cell_size)
                        self.assertEqual((left % 4, top % 4, right % 4, bottom % 4), (0, 0, 0, 0))
                        self.assertGreaterEqual(left, 0)
                        self.assertGreaterEqual(top, 0)
                        self.assertLessEqual(right, route.dimensions[0])
                        self.assertLessEqual(bottom, route.dimensions[1])

    def test_compact_condensed_native_render_contract(self) -> None:
        low, high = MODULE.ROUTES
        self.assertEqual((low.target_height, low.oversample), (26, 8))
        self.assertEqual((high.target_height, high.oversample), (52, 4))
        self.assertEqual((low.center, high.center), ((117.0, 41.0), (227.0, 76.0)))
        self.assertEqual((low.interior_text_lane, high.interior_text_lane), ((74, 178), (140, 338)))
        self.assertEqual((low.icon_protect_kernel, high.icon_protect_kernel), (7, 13))
        self.assertEqual(MODULE.GAP_ALPHA_THRESHOLD, 8)
        self.assertEqual(MODULE.GAP_TOLERANCE_NATIVE_PX, 0.75)
        self.assertEqual(MODULE.ASPECT_CANDIDATES, (0.84, 0.82, 0.80))
        self.assertEqual(MODULE.STATE_ROLES, ("white", "cyan", "blue", "disabled", "cyan_alt", "disabled_alt"))

    def test_all_inputs_are_hash_pinned(self) -> None:
        for route in MODULE.ROUTES:
            self.assertEqual(set(route.source_pins), set(MODULE.LOCALES))
            for pin in (route.target_pin, *route.source_pins.values()):
                self.assertGreater(pin["size"], 0)
                self.assertRegex(pin["sha256"], r"^[0-9A-F]{64}$")


if __name__ == "__main__":
    unittest.main()
