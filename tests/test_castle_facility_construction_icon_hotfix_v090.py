from __future__ import annotations

import importlib.util
import struct
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))


def load_builder():
    path = TOOLS / "build_castle_facility_construction_icon_hotfix_v090.py"
    spec = importlib.util.spec_from_file_location("construction_icon_v090", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load_builder()


class CastleFacilityConstructionIconHotfixV090Tests(unittest.TestCase):
    def test_targets_only_the_verified_label_child_and_vertical_sentinel(self) -> None:
        self.assertEqual(builder.LABEL_WIDTH_WIDGET_OFFSET, 0x140)
        self.assertEqual(builder.CONSTRUCTION_ICON_WIDGET_OFFSET, 0x268)
        self.assertEqual(builder.ACTIVE_VERTICAL_X_BITS, 0x41F00000)
        self.assertEqual(builder.ACTIVE_VERTICAL_Y_BITS, 0x42B80000)
        self.assertEqual(builder.HORIZONTAL_Y_BITS, 0x433D0000)

    def test_helper_uses_live_width_and_never_hardcodes_inactive_x(self) -> None:
        injected = builder.build_injected_code(0x1447BF600)
        self.assertLessEqual(len(injected), builder.APPEND_SIZE)
        self.assertIn(bytes.fromhex("48 8B 81 40 01 00 00"), injected)
        self.assertIn(bytes.fromhex("F3 0F 10 48 10"), injected)
        self.assertIn(bytes.fromhex("48 8B 91 68 02 00 00"), injected)
        self.assertIn(bytes.fromhex("81 7A 08 00 00 F0 41"), injected)
        self.assertIn(bytes.fromhex("81 7A 0C 00 00 B8 42"), injected)
        self.assertIn(bytes.fromhex("F3 0F 58 C1"), injected)
        self.assertIn(bytes.fromhex("C7 42 0C 00 00 3D 43"), injected)
        self.assertNotIn(struct.pack("<I", 0x439C0000), injected)  # 312.0f
        self.assertTrue(injected.endswith(bytes.fromhex("48 83 C4 58 C3")))

    def test_patch_chains_before_the_existing_wrapper_restores_rsp(self) -> None:
        self.assertEqual(builder.AUX_HELPER_EPILOGUE_VA, 0x1447BF3DD)
        self.assertEqual(
            builder.AUX_HELPER_EPILOGUE_BEFORE,
            bytes.fromhex("48 83 C4 58 C3"),
        )
        target = 0x1447BF600
        chain = b"\xE9" + builder.rel32(builder.AUX_HELPER_EPILOGUE_VA + 5, target)
        self.assertEqual(
            builder.AUX_HELPER_EPILOGUE_VA
            + 5
            + struct.unpack_from("<i", chain, 1)[0],
            target,
        )

    def test_source_hashes_are_pinned(self) -> None:
        self.assertRegex(builder.EXPECTED_HORIZONTAL_SHA256, r"^[0-9A-F]{64}$")
        self.assertRegex(builder.EXPECTED_XINPUT_HORIZONTAL_SHA256, r"^[0-9A-F]{64}$")


if __name__ == "__main__":
    unittest.main()
