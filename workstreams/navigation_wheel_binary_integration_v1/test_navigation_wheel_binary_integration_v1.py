from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MODULE = ROOT / "build_navigation_wheel_binary_integration_v1.py"
SPEC = importlib.util.spec_from_file_location("navigation_wheel_binary_integration_v1", MODULE)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class NavigationWheelBinaryIntegrationTests(unittest.TestCase):
    def test_scope_and_static_pin(self) -> None:
        self.assertEqual(builder.SCHEMA, "nobu16.kr.navigation-wheel-binary-integration.v1")
        self.assertEqual(builder.GENERATION_POLICY, "forbidden-and-not-used")
        self.assertEqual(builder.ROUTE_ORDER, ("base_low", "base_high", "pk_low", "pk_high"))
        self.assertEqual(
            builder.STATIC_MANIFEST_SHA256,
            "12B024C4FAB0D22AF3BB17E59E18543BFBE446C89D5CFB856458C98BBF78D2A4",
        )

    def test_pixel_to_bc3_block_mask(self) -> None:
        pixels = builder.np.zeros((8, 12), dtype=bool)
        pixels[0, 0] = True
        pixels[3, 7] = True
        pixels[7, 11] = True
        blocks = builder.block_mask_from_pixels(pixels)
        self.assertEqual(blocks.shape, (2, 3))
        self.assertEqual(builder.blocks_from_mask(blocks), {(0, 0), (1, 0), (2, 1)})
        expanded = builder.expanded_block_pixels(blocks)
        self.assertEqual(expanded.shape, pixels.shape)
        self.assertTrue(bool(builder.np.all(expanded[pixels])))

    def test_catalog_target_contract_covers_four_current_v094_archives(self) -> None:
        routes = {str(route["id"]): route for route in builder.catalog.ROUTES}
        self.assertEqual(tuple(routes), builder.ROUTE_ORDER)
        self.assertEqual(
            [routes[route]["relative_path"] for route in builder.ROUTE_ORDER],
            [
                "RES_JP/res_lang.bin",
                "RES_JP_PK_PORT/res_lang_pk_port1.bin",
                "RES_JP_PK/res_lang_pk.bin",
                "RES_JP_PK_PORT/res_lang_pk_port2.bin",
            ],
        )
        self.assertEqual(
            routes["base_high"]["target"]["sha256"],
            "26D56822815383CCC5CA74EA289AE2E7BEC5756A141C3A5BDCA78379A6F3D11F",
        )
        self.assertEqual(
            routes["pk_high"]["target"]["sha256"],
            "D8B26D0D514AD886ECAE746B0C2C0245E8DD74E85932260EAB88F2856ECDB330",
        )


if __name__ == "__main__":
    unittest.main()
