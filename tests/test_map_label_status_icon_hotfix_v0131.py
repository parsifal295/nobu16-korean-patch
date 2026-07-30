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
    path = TOOLS / "build_map_label_status_icon_hotfix_v0131.py"
    spec = importlib.util.spec_from_file_location("map_label_status_icon_v0131", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load_builder()


class MapLabelStatusIconHotfixV0131Tests(unittest.TestCase):
    def test_single_hook_wraps_the_real_status_update(self) -> None:
        self.assertEqual(builder.STATUS_UPDATE_CALL_SITE, 0x140F98764)
        self.assertEqual(builder.STATUS_UPDATE_VA, 0x140FA52B0)
        self.assertEqual(
            builder.STATUS_UPDATE_CALL_BEFORE,
            bytes.fromhex("E8 47 CB 00 00"),
        )
        target = (
            builder.STATUS_UPDATE_CALL_SITE
            + 5
            + struct.unpack_from("<i", builder.STATUS_UPDATE_CALL_BEFORE, 1)[0]
        )
        self.assertEqual(target, builder.STATUS_UPDATE_VA)
        self.assertFalse(hasattr(builder, "PROJECTION_CALL_SITES"))
        self.assertFalse(hasattr(builder, "PROJECTION_VA"))

    def test_dynamic_width_source_is_exact_and_paired_pools_are_untouched(self) -> None:
        self.assertEqual(builder.LABEL_WIDTH_WIDGET_OFFSET, 0x140)
        self.assertEqual(builder.LABEL_STATUS_WIDGET_OFFSET, 0x248)
        self.assertEqual(builder.ACTIVE_STATUS_BASE_X_BITS, 0x41F00000)
        self.assertFalse(hasattr(builder, "MARKER_X_DELTA"))
        self.assertFalse(hasattr(builder, "LABEL_POOL_1_VA"))
        self.assertFalse(hasattr(builder, "SUPPLY_POOL_2_VA"))
        self.assertFalse(hasattr(builder, "LABEL_POOL_3_VA"))
        self.assertFalse(hasattr(builder, "SUPPLY_POOL_4_VA"))

    def test_wrapper_forwards_stack_args_and_updates_only_target_fields(self) -> None:
        code_va = 0x1447BF260
        injected, labels = builder.build_injected_code(code_va)
        self.assertEqual(len(injected), 162)
        self.assertEqual(labels["status_wrapper"], code_va)

        # Six-argument wrapper: aligned frame, saved RCX, incoming arg 5/6
        # copied to the outgoing Windows x64 stack argument slots.
        self.assertTrue(
            injected.startswith(
                bytes.fromhex(
                    "48 83 EC 58 48 89 4C 24 40 "
                    "8B 84 24 80 00 00 00 89 44 24 20 "
                    "8B 84 24 88 00 00 00 89 44 24 28"
                )
            )
        )
        call_offset = 31
        self.assertEqual(injected[call_offset], 0xE8)
        displacement = struct.unpack_from("<i", injected, call_offset + 1)[0]
        self.assertEqual(code_va + call_offset + 5 + displacement, builder.STATUS_UPDATE_VA)

        # Dynamic rendered width, the single status slot, and the active-base
        # guard must all be present.
        self.assertIn(bytes.fromhex("48 8B 81 40 01 00 00"), injected)
        self.assertIn(bytes.fromhex("F3 0F 10 48 10"), injected)
        self.assertIn(bytes.fromhex("48 8B 91 48 02 00 00"), injected)
        self.assertIn(bytes.fromhex("81 7A 08 00 00 F0 41"), injected)
        self.assertIn(bytes.fromhex("F3 0F 11 42 08"), injected)
        self.assertIn(bytes.fromhex("F3 0F 10 40 0C"), injected)
        self.assertIn(bytes.fromhex("F3 0F 10 50 14"), injected)
        self.assertIn(bytes.fromhex("F3 0F 5C 52 14"), injected)
        self.assertIn(bytes.fromhex("41 BA 00 00 00 3F"), injected)
        self.assertIn(bytes.fromhex("F3 0F 11 42 0C"), injected)

        # Regression guard: never scan the paired label pools or write the
        # root X of the troop-count group below the castle crest.
        self.assertNotIn(bytes.fromhex("49 81 C0 38 00 01 00"), injected)
        self.assertNotIn(bytes.fromhex("F3 0F 11 40 08"), injected)
        self.assertNotIn(bytes.fromhex("41 83 7A 08 02"), injected)
        self.assertNotIn(bytes.fromhex("49 39 52 10"), injected)

    def test_candidate_is_source_hash_gated(self) -> None:
        self.assertRegex(builder.EXPECTED_V0130_SHA256, r"^[0-9A-F]{64}$")
        if builder.EXPECTED_CANDIDATE_SHA256:
            self.assertRegex(builder.EXPECTED_CANDIDATE_SHA256, r"^[0-9A-F]{64}$")


if __name__ == "__main__":
    unittest.main()
