from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))
SCRIPT = TOOLS / "build_map_label_aux_status_hotfix_v0140.py"

spec = importlib.util.spec_from_file_location("map_label_aux_status_v0140", SCRIPT)
assert spec and spec.loader
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class MapLabelAuxStatusHotfixV0140Tests(unittest.TestCase):
    def test_source_and_existing_patch_006_contract_are_pinned(self) -> None:
        self.assertEqual(builder.TARGET_SIZE, 67_024_384)
        self.assertEqual(builder.EXPECTED_SECTION_VIRTUAL_SIZE, 35_275_522)
        self.assertEqual(builder.EXISTING_006_WRAPPER_VA, 0x1447BF260)
        self.assertEqual(builder.EXISTING_006_EPILOGUE_VA, 0x1447BF2FD)
        self.assertEqual(
            builder.EXISTING_006_EPILOGUE_BEFORE,
            bytes.fromhex("48 83 C4 58 C3"),
        )
        self.assertEqual(
            builder.EXPECTED_V0140_SHA256,
            "F424964405CFCD1AC454B3801DA4795A183A8271DD16EA8A6A7B97A2547232BF",
        )
        self.assertEqual(
            builder.EXPECTED_CANDIDATE_SHA256,
            "01C8769F09BD9A5459844FF5E335A71048C1F11CC7AF7738517EFEE61D4BF28D",
        )

    def test_helper_uses_reviewed_warning_geometry(self) -> None:
        code_va = 0x1447BF310
        injected, labels = builder.build_injected_code(code_va)
        self.assertEqual(len(injected), 210)
        self.assertEqual(labels["aux_alignment"], code_va)
        self.assertTrue(injected.startswith(bytes.fromhex("48 8B 4C 24 40 48 85 C9")))
        self.assertTrue(injected.endswith(bytes.fromhex("48 83 C4 58 C3")))

        self.assertEqual(builder.NO_CASTLE_LORD_WARNING_WIDGET_OFFSET, 0x270)
        self.assertEqual(builder.NO_CASTLE_LORD_WARNING_NATIVE_X_BITS, 0x41E00000)
        self.assertEqual(builder.NO_CASTLE_LORD_WARNING_IMAGE_HEIGHT_OFFSET, 0xA0)
        self.assertIn(bytes.fromhex("48 8B 91 70 02 00 00"), injected)
        self.assertIn(bytes.fromhex("81 7A 08 00 00 E0 41"), injected)
        self.assertIn(bytes.fromhex("F3 0F 10 40 08"), injected)
        self.assertIn(bytes.fromhex("F3 0F 58 40 10"), injected)
        self.assertIn(bytes.fromhex("F3 0F 5C 92 A0 00 00 00"), injected)
        self.assertNotIn(bytes.fromhex("F3 0F 5C 52 14"), injected)

    def test_helper_uses_confirmed_battle_ready_number_geometry(self) -> None:
        injected, _labels = builder.build_injected_code(0x1447BF310)
        self.assertEqual(builder.BATTLE_READY_NUMBER_WIDGET_OFFSET, 0x260)
        self.assertEqual(builder.PRIMARY_STATUS_WIDGET_OFFSET, 0x248)
        self.assertEqual(builder.BATTLE_READY_NUMBER_NATIVE_X_BITS, 0x42480000)
        self.assertEqual(builder.BATTLE_READY_NUMBER_STATUS_X_OFFSET_BITS, 0x41A00000)
        self.assertIn(bytes.fromhex("48 8B 91 60 02 00 00"), injected)
        self.assertIn(bytes.fromhex("81 7A 08 00 00 48 42"), injected)
        self.assertIn(bytes.fromhex("4C 8B 81 48 02 00 00"), injected)
        self.assertIn(bytes.fromhex("41 BA 00 00 A0 41"), injected)
        self.assertIn(bytes.fromhex("66 41 0F 6E CA F3 0F 58 C1"), injected)
        self.assertNotIn(bytes.fromhex("F3 41 0F 58 40 10"), injected)
        self.assertIn(bytes.fromhex("F3 41 0F 58 40 14"), injected)
        self.assertIn(bytes.fromhex("F3 0F 5C 42 14"), injected)

        # The helper never accesses the independent castle-crest/troop-count
        # root children used by the regression fixed in v0.13.1.
        self.assertNotIn(bytes.fromhex("48 8B 81 80 02 00 00"), injected)
        self.assertNotIn(bytes.fromhex("48 8B 81 88 02 00 00"), injected)


if __name__ == "__main__":
    unittest.main()
