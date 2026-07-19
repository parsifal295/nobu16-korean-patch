from __future__ import annotations

import gzip
import hashlib
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "release_payload" / "v0.13.0"
PREVIOUS_PAYLOAD = ROOT / "release_payload" / "v0.12.0"
STATIC_ROOT = PAYLOAD / "OfficerEditorStaticFix"
MASTER = STATIC_ROOT / "Invoke-Nobu16StaticPatches.ps1"
PATCH_ROOT = STATIC_ROOT / "Patches"
REGISTRY = STATIC_ROOT / "000-PatchRegistry.psd1"
PATCH_004 = PATCH_ROOT / "004-HorizontalMapLabelsDynamicWidth.psd1"
PATCH_005 = PATCH_ROOT / "005-DualResolutionAndHorizontalLandmarks.psd1"
APPEND_005 = PATCH_ROOT / "Payloads" / "005-DualResolutionAndHorizontalLandmarks.append.gz"


class StaticMapLabelsInstallerV0130Tests(unittest.TestCase):
    def test_registry_owns_five_ordered_patch_definitions(self) -> None:
        expected = (
            "001-OfficerEditorNameValidation.psd1",
            "002-FictionalPrincessNameValidation.psd1",
            "003-TopHeaderLayout.psd1",
            "004-HorizontalMapLabelsDynamicWidth.psd1",
            "005-DualResolutionAndHorizontalLandmarks.psd1",
        )
        self.assertEqual(tuple(path.name for path in sorted(PATCH_ROOT.glob("*.psd1"))), expected)
        registry = REGISTRY.read_text(encoding="ascii")
        self.assertIn("nobu16.static-exe-patch-registry.v3", registry)
        self.assertIn("Release = 'v0.13.0'", registry)
        self.assertIn(
            "BE983A61C81008289E2483D552122C0BE3299B5F8DD4A557FA14DA2663AC7BD6",
            registry,
        )
        for name in expected:
            self.assertIn(f"Patches/{name}", registry)

    def test_patch_004_is_byte_identical_to_the_published_v0120_patch(self) -> None:
        previous_root = PREVIOUS_PAYLOAD / "OfficerEditorStaticFix" / "Patches"
        pairs = (
            (PATCH_004, previous_root / PATCH_004.name),
            (
                PATCH_ROOT / "Payloads" / "004-HorizontalMapLabelsDynamicWidth.append.gz",
                previous_root / "Payloads" / "004-HorizontalMapLabelsDynamicWidth.append.gz",
            ),
        )
        for current, previous in pairs:
            self.assertEqual(current.read_bytes(), previous.read_bytes(), current.name)
        self.assertEqual(
            hashlib.sha256(PATCH_004.read_bytes()).hexdigest().upper(),
            "D009D596ACC5E1B3A4FC7D74913B5D17F87FA199B38956FBAC456130DEDA754B",
        )

    def test_patch_005_combines_high_resolution_assets_and_landmark_sites(self) -> None:
        source = PATCH_005.read_text(encoding="ascii")
        self.assertIn("Kind = 'AppendOverlay'", source)
        self.assertIn("BaseSize = 38991872L", source)
        self.assertIn("TargetSize = 67024384L", source)
        self.assertIn("ExpandedSize = 28032512L", source)
        self.assertEqual(source.count("Before = '"), 48)
        self.assertEqual(source.count("After = '"), 48)
        offsets = {int(value, 16) for value in re.findall(r"Offset = 0x([0-9A-F]+)", source)}
        self.assertTrue(
            {
                0x00F41FFB,
                0x00F4202A,
                0x00F421C7,
                0x00F421FD,
                0x00F4223D,
                0x00F42252,
                0x00F42313,
                0x00F42338,
                0x00F4235D,
                0x00F42382,
                0x00F60F10,
            }.issubset(offsets)
        )

    def test_patch_005_append_payload_is_pinned_and_roundtrips(self) -> None:
        compressed = APPEND_005.read_bytes()
        expanded = gzip.decompress(compressed)
        self.assertEqual(len(compressed), 4_706_907)
        self.assertEqual(len(expanded), 28_032_512)
        self.assertEqual(
            hashlib.sha256(compressed).hexdigest().upper(),
            "F723A94E8A63409E0A5458D2790FEE7713EB805FA9E48488EF9281205E27BA1F",
        )
        self.assertEqual(
            hashlib.sha256(expanded).hexdigest().upper(),
            "F89447BA89038C594319649F2E881D2B3E826E32C034E6ED2395BD34788DD11D",
        )

    def test_master_supports_chained_structural_patches_and_idempotence(self) -> None:
        source = MASTER.read_text(encoding="ascii")
        for token in (
            "nobu16.static-exe-patch-registry.v3",
            "return 'Blocked'",
            "FinalAfter",
            "LaterSites",
            "$structuralSize",
            "$Patches.Count - 1",
            "$changedCount",
            "remains blocked after its registered dependencies",
            "All registered static patches are already applied.",
            "Registered all-applied output hash mismatch",
        ):
            self.assertIn(token, source)

    def test_payload_has_no_game_executable_or_runtime_memory_patcher(self) -> None:
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

    def test_installer_readme_documents_005_upgrade_paths(self) -> None:
        readme = (PAYLOAD / "STATIC_OFFICER_EDITOR_FIX_README_KO.txt").read_text(
            encoding="utf-8"
        )
        for text in (
            "004는 v0.12.0에서 배포한 정의와 해시를 그대로 유지",
            "005는 4K에서",
            "아쓰타 신궁",
            "v0.12.0 사용자는 v0.13.0 파일을 게임 폴더에 덮어쓴 뒤 반드시",
            "새 APPLY_STATIC_EXE_PATCHES.bat를 다시 실행해야 합니다",
            "파일만 덮어쓰면\n  EXE의 005는 적용되지 않습니다",
            "v0.12.0에서 001~004가 적용된 EXE: 005만 자동 적용",
            "원본 Steam JP 1.1.7 EXE: 001~005를 순서대로 적용",
            "800x450",
            "완전 종료·재실행",
            "BE983A61C81008289E2483D552122C0BE3299B5F8DD4A557FA14DA2663AC7BD6",
        ):
            self.assertIn(text, readme)


if __name__ == "__main__":
    unittest.main()
