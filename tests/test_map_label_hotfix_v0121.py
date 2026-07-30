from __future__ import annotations

import hashlib
import importlib.util
import struct
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))


def load_builder():
    path = TOOLS / "build_map_label_hotfix_v0121.py"
    spec = importlib.util.spec_from_file_location("map_label_hotfix_v0121", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load_builder()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


class MapLabelHotfixV0121Tests(unittest.TestCase):
    def test_resolution_contracts_are_exact(self) -> None:
        self.assertEqual(builder.GROUP_KEY, 0x17ED)
        self.assertEqual(builder.LOW_SOURCE_OUTER_SIZE, 0x8D9A6)
        self.assertEqual(builder.HIGH_SOURCE_OUTER_SIZE, 0x1B842C)
        self.assertEqual(builder.LOW_SOURCE_RAW_G1T_SIZE, 0x300054)
        self.assertEqual(builder.HIGH_SOURCE_RAW_G1T_SIZE, 0xC00054)
        self.assertEqual(len(builder.TARGET_IDS), 24)
        self.assertEqual(len(set(builder.TARGET_IDS)), 24)

    def test_rectangle_wrapper_uses_loader_owned_resolution_flag(self) -> None:
        wrapper = builder.build_rect_wrapper(
            builder.CODE_SECTION_VA,
            builder.IMAGE_BASE + 0x2D03610,
            builder.IMAGE_BASE + 0x2D03600,
        )
        self.assertEqual(len(wrapper), 85)
        self.assertEqual(sha256(wrapper), builder.EXPECTED_RECT_WRAPPER_SHA256)
        self.assertIn(bytes.fromhex("803D"), wrapper)
        self.assertIn(bytes.fromhex("4883C00C"), wrapper)
        self.assertNotIn(bytes.fromhex("4883C018"), wrapper)

    def test_outer_provider_dispatches_only_known_17ed_sizes(self) -> None:
        provider = builder.build_outer_provider(
            builder.CODE_SECTION_VA + builder.OUTER_PROVIDER_OFFSET,
            builder.LOW_OUTER_VA,
            builder.LOW_OUTER_SIZE,
            builder.IMAGE_BASE + 0x2D038B0,
            0x2BB949,
            builder.IMAGE_BASE + 0x2D03600,
        )
        self.assertEqual(len(provider), 119)
        self.assertEqual(sha256(provider), builder.EXPECTED_OUTER_PROVIDER_SHA256)
        self.assertIn(struct.pack("<I", builder.HIGH_SOURCE_OUTER_SIZE), provider)
        self.assertIn(struct.pack("<I", builder.LOW_SOURCE_OUTER_SIZE), provider)
        self.assertIn(bytes.fromhex("C605"), provider)

    def test_nested_provider_dispatches_only_known_17ed_sizes(self) -> None:
        provider = builder.build_nested_provider(
            builder.CODE_SECTION_VA + builder.NESTED_PROVIDER_OFFSET,
            builder.LOW_RAW_G1T_VA,
            builder.LOW_RAW_G1T_SIZE,
            builder.IMAGE_BASE + 0x2FBF200,
            0x1800054,
            builder.IMAGE_BASE + 0x2D03600,
        )
        self.assertEqual(len(provider), 145)
        self.assertEqual(sha256(provider), builder.EXPECTED_NESTED_PROVIDER_SHA256)
        self.assertIn(struct.pack("<I", builder.HIGH_SOURCE_RAW_G1T_SIZE), provider)
        self.assertIn(struct.pack("<I", builder.LOW_SOURCE_RAW_G1T_SIZE), provider)

    def test_source_and_output_hashes_are_pinned(self) -> None:
        for value in (
            builder.EXPECTED_V0120_SHA256,
            builder.EXPECTED_JP_PORT2_SHA256,
            builder.EXPECTED_EN_PORT2_SHA256,
            builder.EXPECTED_HIGH_OUTER_SHA256,
            builder.EXPECTED_HIGH_RAW_G1T_SHA256,
            builder.EXPECTED_CANDIDATE_SHA256,
        ):
            self.assertRegex(value, r"^[0-9A-F]{64}$")

    def test_hook_padding_is_nop_not_zero(self) -> None:
        source = (TOOLS / "build_map_label_hotfix_v0121.py").read_text(
            encoding="utf-8"
        )
        self.assertIn('b"\\x90" * 7', source)
        self.assertNotIn('b"\\x00" * 7', source)


if __name__ == "__main__":
    unittest.main()
