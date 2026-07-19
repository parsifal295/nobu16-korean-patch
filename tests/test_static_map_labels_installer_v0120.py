from __future__ import annotations

import gzip
import hashlib
import importlib.util
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "release_payload" / "v0.12.0"
STATIC_ROOT = PAYLOAD / "OfficerEditorStaticFix"
MASTER = STATIC_ROOT / "Invoke-Nobu16StaticPatches.ps1"
PATCH_ROOT = STATIC_ROOT / "Patches"
PATCH_REGISTRY = STATIC_ROOT / "000-PatchRegistry.psd1"
PATCH_004 = PATCH_ROOT / "004-HorizontalMapLabelsDynamicWidth.psd1"
APPEND_PAYLOAD = (
    PATCH_ROOT
    / "Payloads"
    / "004-HorizontalMapLabelsDynamicWidth.append.gz"
)


def load_release_module():
    path = ROOT / "tools" / "build_steam_jp_v0120_release.py"
    spec = importlib.util.spec_from_file_location("static_release_v0120", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


release = load_release_module()


class StaticMapLabelsInstallerV0120Tests(unittest.TestCase):
    def test_registry_owns_four_ordered_patch_definitions(self) -> None:
        expected = (
            "001-OfficerEditorNameValidation.psd1",
            "002-FictionalPrincessNameValidation.psd1",
            "003-TopHeaderLayout.psd1",
            "004-HorizontalMapLabelsDynamicWidth.psd1",
        )
        self.assertEqual(
            tuple(path.name for path in sorted(PATCH_ROOT.glob("*.psd1"))),
            expected,
        )
        registry = PATCH_REGISTRY.read_text(encoding="ascii")
        self.assertIn("nobu16.static-exe-patch-registry.v2", registry)
        self.assertIn("Release = 'v0.12.0'", registry)
        self.assertIn(release.STATIC_EXE_PATCH["output_sha256"], registry)
        for name in expected:
            self.assertIn(f"Patches/{name}", registry)

    def test_structural_patch_is_exact_and_has_no_character_ceiling(self) -> None:
        source = PATCH_004.read_text(encoding="ascii")
        self.assertIn("Kind = 'AppendOverlay'", source)
        self.assertIn("BaseSize = 31747848L", source)
        self.assertIn("TargetSize = 38991872L", source)
        self.assertIn("ExpandedSize = 7244024L", source)
        self.assertEqual(source.count("Before = '"), 128)
        self.assertEqual(source.count("After = '"), 128)
        before = re.findall(r"Before = '([0-9A-F]+)'", source)
        after = re.findall(r"After = '([0-9A-F]+)'", source)
        self.assertEqual(len(before), len(after))
        self.assertTrue(all(len(old) == len(new) for old, new in zip(before, after, strict=True)))

        # Call-specific UTF-16 width path: preserve RAX, resolve font size, and
        # call the local NUL-terminated half/full-width loop.
        self.assertIn("Offset = 0x00F61A3A; Before = '44'; After = '48'", source)
        self.assertIn("After = 'D88BCFE8EC29A6FF'", source)
        self.assertIn("After = 'D0488BCBE8387A6B0190909090909090'", source)
        for forbidden_ceiling in ("three-character", "five-character", "nine-character"):
            self.assertNotIn(forbidden_ceiling, source.casefold())

    def test_append_payload_is_pinned_and_roundtrips(self) -> None:
        compressed = APPEND_PAYLOAD.read_bytes()
        expanded = gzip.decompress(compressed)
        self.assertEqual(len(compressed), 1_580_771)
        self.assertEqual(len(expanded), 7_244_024)
        self.assertEqual(
            hashlib.sha256(compressed).hexdigest().upper(),
            "BFA9F42C9021208349021A6A26193ADE0C83DE6B797CBDA7E15E59D463630A95",
        )
        self.assertEqual(
            hashlib.sha256(expanded).hexdigest().upper(),
            "5C28CF48729EBC132FEEF74E4E373084125D2B1F3E44A36C58BEA05F44DC360D",
        )
        self.assertIn(bytes.fromhex("4189D031C00FB7116685D27418"), expanded)

    def test_master_detects_pending_applied_and_structural_payload_states(self) -> None:
        source = MASTER.read_text(encoding="ascii")
        for token in (
            "Get-ExpandedPayload",
            "System.IO.Compression.GZipStream",
            "Kind -eq 'AppendOverlay'",
            "ExpandedSha256",
            "return 'Applied'",
            "return 'Pending'",
            "partially applied; refusing an unsafe repair",
            "unknown appended payload",
            "Sort-Object TargetSize -Descending",
            "Registered all-applied output hash mismatch",
            "[System.IO.File]::Replace",
        ):
            self.assertIn(token, source)

    def test_payload_contains_no_game_executable_or_runtime_memory_patcher(self) -> None:
        self.assertFalse(any(PAYLOAD.rglob("NOBU16PK.exe")))
        source = MASTER.read_text(encoding="ascii").casefold()
        for forbidden in (
            "openprocess",
            "writeprocessmemory",
            "virtualprotectex",
            "readprocessmemory",
            "debugactiveprocess",
            "suspendthread",
        ):
            self.assertNotIn(forbidden, source)

    def test_readme_records_real_restart_qa_and_dynamic_width(self) -> None:
        readme = (PAYLOAD / "STATIC_OFFICER_EDITOR_FIX_README_KO.txt").read_text(
            encoding="utf-8"
        )
        for text in (
            "지도 성·지명 가로쓰기",
            "실제 UTF-16 문자열을 NUL까지",
            "공백과 '성' 접미사",
            "1920x1080",
            "완전히 종료하고 새 프로세스로 재실행",
            "3자·5자·6자·7자",
            "최장 9자",
            release.STATIC_EXE_PATCH["output_sha256"],
        ):
            self.assertIn(text, readme)


if __name__ == "__main__":
    unittest.main()
