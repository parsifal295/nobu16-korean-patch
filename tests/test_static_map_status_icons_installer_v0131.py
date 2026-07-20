from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "release_payload" / "v0.13.1"
PREVIOUS_PAYLOAD = ROOT / "release_payload" / "v0.13.0"
STATIC_ROOT = PAYLOAD / "OfficerEditorStaticFix"
PREVIOUS_STATIC_ROOT = PREVIOUS_PAYLOAD / "OfficerEditorStaticFix"
PATCH_ROOT = STATIC_ROOT / "Patches"
REGISTRY = STATIC_ROOT / "000-PatchRegistry.psd1"
PATCH_006 = PATCH_ROOT / "006-HorizontalMapStatusIcons.psd1"


class StaticMapStatusIconsInstallerV0131Tests(unittest.TestCase):
    def test_registry_owns_six_ordered_patch_definitions(self) -> None:
        expected = (
            "001-OfficerEditorNameValidation.psd1",
            "002-FictionalPrincessNameValidation.psd1",
            "003-TopHeaderLayout.psd1",
            "004-HorizontalMapLabelsDynamicWidth.psd1",
            "005-DualResolutionAndHorizontalLandmarks.psd1",
            "006-HorizontalMapStatusIcons.psd1",
        )
        self.assertEqual(tuple(path.name for path in sorted(PATCH_ROOT.glob("*.psd1"))), expected)
        registry = REGISTRY.read_text(encoding="ascii")
        self.assertIn("nobu16.static-exe-patch-registry.v3", registry)
        self.assertIn("Release = 'v0.13.1'", registry)
        self.assertIn(
            "AllAppliedSha256 = "
            "'811F6B31C09AD87F2D73F1349FB17AA4C9ABEA76F2415083C78E932D0B1D5A31'",
            registry,
        )
        for name in expected:
            self.assertIn(f"Patches/{name}", registry)

    def test_published_001_through_005_are_unchanged(self) -> None:
        relative_paths = [
            *(Path("Patches") / f"{index:03d}-{name}" for index, name in (
                (1, "OfficerEditorNameValidation.psd1"),
                (2, "FictionalPrincessNameValidation.psd1"),
                (3, "TopHeaderLayout.psd1"),
                (4, "HorizontalMapLabelsDynamicWidth.psd1"),
                (5, "DualResolutionAndHorizontalLandmarks.psd1"),
            )),
            Path("Patches/Payloads/004-HorizontalMapLabelsDynamicWidth.append.gz"),
            Path("Patches/Payloads/005-DualResolutionAndHorizontalLandmarks.append.gz"),
        ]
        for relative in relative_paths:
            self.assertEqual(
                (STATIC_ROOT / relative).read_bytes(),
                (PREVIOUS_STATIC_ROOT / relative).read_bytes(),
                str(relative),
            )

    def test_master_accepts_every_registered_prefix_state(self) -> None:
        source = (STATIC_ROOT / "Invoke-Nobu16StaticPatches.ps1").read_text(
            encoding="ascii"
        )
        for token in (
            "AcceptedAfter = @()",
            "$acceptedAfter += ,(Copy-Bytes $currentAfter)",
            "$changedByLaterPatch",
            "$matchesAcceptedAfter",
            "$site.Offset + $site.Before.Length) -gt $Data.Length",
            "FinalAfter",
            "LaterSites",
        ):
            self.assertIn(token, source)

    def test_patch_006_is_the_reviewed_same_size_byte_patch(self) -> None:
        source = PATCH_006.read_text(encoding="ascii")
        self.assertIn("Kind = 'BytePatch'", source)
        self.assertIn("dynamic alignment", source)
        self.assertIn("dynamic map status X/Y and paired supply-root alignment wrapper", source)
        self.assertEqual(source.count("Before = '"), 4)
        self.assertEqual(source.count("After = '"), 4)
        offsets = [int(value, 16) for value in re.findall(r"Offset = 0x([0-9A-F]+)", source)]
        self.assertEqual(offsets, [0x000003C0, 0x000003DC, 0x00F97B64, 0x03FEB460])
        self.assertEqual(len(PATCH_006.read_bytes()), 1_910)
        self.assertEqual(
            hashlib.sha256(PATCH_006.read_bytes()).hexdigest().upper(),
            "AE96F16467396A31F9891F877BC827C2D62CCEB2F77EE934F469BDD4FDC668C3",
        )

    def test_payload_has_no_game_executable_or_new_append_payload(self) -> None:
        self.assertFalse(any(PAYLOAD.rglob("NOBU16PK.exe")))
        payload_names = tuple(
            path.name for path in sorted((PATCH_ROOT / "Payloads").glob("*.gz"))
        )
        self.assertEqual(
            payload_names,
            (
                "004-HorizontalMapLabelsDynamicWidth.append.gz",
                "005-DualResolutionAndHorizontalLandmarks.append.gz",
            ),
        )

    def test_installer_readme_documents_006_upgrade_and_qa(self) -> None:
        readme = (PAYLOAD / "STATIC_OFFICER_EDITOR_FIX_README_KO.txt").read_text(
            encoding="utf-8"
        )
        for text in (
            "006: 지도 성 이름 뒤 상태·보급 아이콘 동적 정렬",
            "v0.13.0 사용자는 v0.13.1 파일을 게임 폴더에 덮어쓴 뒤 반드시",
            "새 APPLY_STATIC_EXE_PATCHES.bat를 다시 실행해야 합니다",
            "파일만 덮어쓰면\n  EXE의 006은 적용되지 않습니다",
            "v0.13.0에서 001~005가 적용된 EXE: 006만 자동 적용",
            "원본 Steam JP 1.1.7 EXE: 001~006을 순서대로 적용",
            "1920x1080",
            "완전 종료·재실행",
            "811F6B31C09AD87F2D73F1349FB17AA4C9ABEA76F2415083C78E932D0B1D5A31",
        ):
            self.assertIn(text, readme)

    def test_project_readme_documents_issue_72_and_installer_rerun(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for text in (
            "## v0.13.1 — 지도 성 이름 뒤 상태·보급 아이콘 동적 정렬",
            "Issue #72",
            "전투 준비·방위 거점·공략 목표 아이콘",
            "군량 표시",
            "v0.13.0 사용자는 v0.13.1 파일을 게임 폴더에 덮어쓴 뒤 반드시 새",
            "APPLY_STATIC_EXE_PATCHES.bat",
            "EXE의 `006`은 적용되지 않습니다",
            "1920×1080",
            "완전히 종료한 뒤 새 프로세스로 재실행",
            "811F6B31C09AD87F2D73F1349FB17AA4C9ABEA76F2415083C78E932D0B1D5A31",
        ):
            self.assertIn(text, readme)


if __name__ == "__main__":
    unittest.main()
