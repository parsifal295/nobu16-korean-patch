from __future__ import annotations

import bz2
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


patcher = load_module("v0140_resource_patcher_test", "tools/v0140_resource_patcher.py")


class V0140ResourcePatcherTests(unittest.TestCase):
    def test_attribution_banner_contract(self) -> None:
        banner = patcher.ATTRIBUTION_BANNER
        self.assertIn("|  _ \\ / ___|_ _| \\ | / ___|", banner)
        self.assertNotIn("_   _  ___  ____", banner)
        self.assertIn("제작: 디시인사이드 신장의야망 갤러리", banner)
        self.assertIn("parsifal", banner)
        self.assertIn("https://github.com/parsifal295/nobu16-korean-patch", banner)

    def test_top_level_resource_path_is_supported(self) -> None:
        self.assertEqual(
            patcher.ordinary_relative_path("RES_JP/res_lang.bin").as_posix(),
            "RES_JP/res_lang.bin",
        )
        for unsafe in ("../outside.bin", "C:/outside.bin", "MSG/../outside.bin", "one"):
            with self.subTest(unsafe=unsafe):
                with self.assertRaises(patcher.PatcherError):
                    patcher.ordinary_relative_path(unsafe)

    def test_replacement_schema_rejects_unknown_or_mismatched_content(self) -> None:
        operation = {
            "id": 7,
            "source_utf16le_sha256": patcher.text_hash("before"),
            "replacement": "after",
            "replacement_utf16le_sha256": patcher.text_hash("after"),
        }
        patcher.verify_text_operation(operation, "operation", coordinate_keys={"id"})

        with_unknown = dict(operation, unrelated_full_resource_base64="not allowed")
        with self.assertRaises(patcher.PatcherError):
            patcher.verify_text_operation(with_unknown, "operation", coordinate_keys={"id"})

        wrong_hash = dict(operation, replacement_utf16le_sha256=patcher.text_hash("wrong"))
        with self.assertRaises(patcher.PatcherError):
            patcher.verify_text_operation(wrong_hash, "operation", coordinate_keys={"id"})

    def test_resource_contract_is_fixed(self) -> None:
        self.assertEqual(set(patcher.RESOURCE_KINDS), set(patcher.RESOURCE_PATHS))
        self.assertEqual(set(patcher.EXPECTED_OPERATION_COUNTS), set(patcher.TEXT_RESOURCE_PATHS))
        self.assertEqual(sum(patcher.EXPECTED_OPERATION_COUNTS.values()), 120_309)
        self.assertEqual(len(patcher.RESOURCE_PATHS), 15)
        self.assertEqual(len(patcher.BINARY_RESOURCE_PATHS), 5)
        self.assertEqual(patcher.RETAINED_RESOURCES, {})

    def test_preflight_is_a_dedicated_nonwriting_action(self) -> None:
        parsed = patcher.build_parser().parse_args(["--preflight"])
        self.assertTrue(parsed.preflight)
        self.assertFalse(parsed.apply)
        self.assertFalse(parsed.restore)
        hidden = patcher.build_parser().parse_args(["--apply", "--no-banner"])
        self.assertTrue(hidden.no_banner)

    @staticmethod
    def bsdiff_integer(value: int) -> bytes:
        if value < 0:
            return ((-value) | (1 << 63)).to_bytes(8, "little")
        return value.to_bytes(8, "little")

    def test_bsdiff40_apply_is_exact_and_range_checked(self) -> None:
        source = b"ABC"
        control = b"".join(self.bsdiff_integer(value) for value in (3, 1, 0))
        diff = bytes((0, 0, 1))
        control_blob = bz2.compress(control)
        diff_blob = bz2.compress(diff)
        patch = b"".join(
            (
                b"BSDIFF40",
                self.bsdiff_integer(len(control_blob)),
                self.bsdiff_integer(len(diff_blob)),
                self.bsdiff_integer(4),
                control_blob,
                diff_blob,
                bz2.compress(b"!"),
            )
        )
        self.assertEqual(
            patcher.apply_bsdiff40(source, patch, relative="RES_JP/res_lang.bin"),
            b"ABD!",
        )
        broken = bytearray(patch)
        broken[24:32] = self.bsdiff_integer(5)
        with self.assertRaises(patcher.PatcherError):
            patcher.apply_bsdiff40(source, bytes(broken), relative="RES_JP/res_lang.bin")


if __name__ == "__main__":
    unittest.main()
