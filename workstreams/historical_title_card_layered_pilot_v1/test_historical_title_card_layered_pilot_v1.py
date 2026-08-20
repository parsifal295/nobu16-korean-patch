from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
MODULE_PATH = WORKSTREAM / "build_historical_title_card_layered_pilot_v1.py"
SPEC = importlib.util.spec_from_file_location("historical_title_card_layered_pilot_v1", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
pilot = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = pilot
SPEC.loader.exec_module(pilot)


class HistoricalTitleCardLayeredPilotTests(unittest.TestCase):
    def test_catalog_has_one_three_state_prototype(self) -> None:
        catalog = json.loads((WORKSTREAM / "catalog.prototype.v1.json").read_text(encoding="utf-8"))
        self.assertEqual(catalog["state_order"], list(pilot.STATE_NAMES))
        self.assertEqual(len(catalog["entries"]), 1)
        self.assertEqual(catalog["entries"][0]["slots"], [0, 1, 2])
        self.assertEqual(catalog["entries"][0]["ko"], "독안룡")

    def test_zoom_burst_expands_without_leaving_final_bbox(self) -> None:
        mask = pilot.np.zeros((64, 128), dtype=pilot.np.uint8)
        mask[24:40, 48:80] = 255
        burst = pilot.zoom_burst_mask(mask, [48, 24, 80, 40], [24, 12, 104, 52], 0.125)
        self.assertEqual(pilot.alpha_bbox(burst), [24, 12, 104, 52])
        self.assertFalse(pilot.np.any(burst[:12]))
        self.assertFalse(pilot.np.any(burst[52:]))
        self.assertFalse(pilot.np.any(burst[:, :24]))
        self.assertFalse(pilot.np.any(burst[:, 104:]))

    def test_text_mask_fits_requested_bbox(self) -> None:
        font = pilot.DEFAULT_FONT
        if not font.is_file():
            self.skipTest(f"pinned local font is unavailable: {font}")
        mask = pilot.render_text_mask("독안룡", font, (512, 128), [100, 12, 412, 116])
        box = pilot.alpha_bbox(mask)
        self.assertGreaterEqual(box[0], 100)
        self.assertGreaterEqual(box[1], 12)
        self.assertLessEqual(box[2], 412)
        self.assertLessEqual(box[3], 116)

    def test_generation_and_deployment_policy_is_closed(self) -> None:
        self.assertEqual(pilot.GENERATION_POLICY, "forbidden-and-not-used")


if __name__ == "__main__":
    unittest.main()
