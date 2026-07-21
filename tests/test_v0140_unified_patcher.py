from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "release_payload" / "v0.14.0"
ATTRIBUTES = ROOT / ".gitattributes"


class V0140UnifiedPatcherTests(unittest.TestCase):
    def test_only_the_unified_launchers_are_public(self) -> None:
        apply = (PAYLOAD / "APPLY_KOREAN_PATCH.bat").read_text(encoding="utf-8")
        restore = (PAYLOAD / "RESTORE_KOREAN_PATCH.bat").read_text(encoding="utf-8")
        self.assertIn("Invoke-Nobu16KoreanPatch.ps1", apply)
        self.assertIn("-Apply", apply)
        self.assertIn("chcp 65001 >nul", apply)
        self.assertNotIn("Korean patch completed.", apply)
        self.assertNotIn("Korean patch failed.", apply)
        self.assertIn("Invoke-Nobu16KoreanPatch.ps1", restore)
        self.assertIn("-Restore", restore)
        for retired in (
            "APPLY_KOREAN_RESOURCE_PATCH.bat",
            "RESTORE_KOREAN_RESOURCE_PATCH.bat",
            "APPLY_STATIC_EXE_PATCHES.bat",
            "RESTORE_ORIGINAL_NOBU16PK_EXE.bat",
        ):
            self.assertFalse((PAYLOAD / retired).exists(), retired)

    def test_unified_batch_files_are_checked_out_as_crlf(self) -> None:
        attributes = ATTRIBUTES.read_text(encoding="utf-8")
        self.assertIn("/release_payload/v0.14.0/*.bat text eol=crlf", attributes)

    def test_package_readme_requires_steam_integrity_verification(self) -> None:
        readme = (PAYLOAD / "PATCHER_README_KO.txt").read_text(encoding="utf-8")
        self.assertIn("Steam JP 1.1.7 순정 파일에서만 설치할 수 있습니다", readme)
        self.assertIn("게임 파일 무결성 확인", readme)
        self.assertIn("APPLY_KOREAN_PATCH.bat", readme)
        self.assertIn("패치 완료! Steam에서 게임을 시작하세요.", readme)

    def test_coordinator_preflights_and_verifies_both_engines(self) -> None:
        coordinator = PAYLOAD / "Invoke-Nobu16KoreanPatch.ps1"
        self.assertTrue(coordinator.read_bytes().startswith(b"\xef\xbb\xbf"))
        source = coordinator.read_text(encoding="utf-8-sig")
        self.assertIn("('--' + $Mode.ToLowerInvariant())", source)
        self.assertIn("Invoke-StaticPatcher $resolvedGameRoot 'Status'", source)
        self.assertIn("Invoke-StaticPatcher $resolvedGameRoot 'Apply'", source)
        self.assertIn("Invoke-ResourcePatcher $resolvedGameRoot 'Apply'", source)
        self.assertIn("Invoke-ResourcePatcher $resolvedGameRoot 'Restore'", source)
        self.assertIn("compensating_static_restore", source)
        self.assertIn("compensating_resource_apply", source)
        self.assertIn("$TargetExeSha256", source)
        self.assertIn("$arguments += '--no-banner'", source)
        self.assertLess(
            source.index("Write-TransactionState $resolvedGameRoot 'applied'"),
            source.rindex("Show-CompletionBanner"),
        )
        self.assertLess(
            source.rindex("Show-CompletionBanner"),
            source.index("패치 완료! Steam에서 게임을 시작하세요."),
        )
        self.assertEqual(source.count("패치 완료! Steam에서 게임을 시작하세요."), 1)
        self.assertNotIn("Korean patch completed.", source)


if __name__ == "__main__":
    unittest.main()
