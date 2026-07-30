from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "RELEASE_NOTES_v0.13.0_KO.md"


class ReleaseNotesV0130Tests(unittest.TestCase):
    def test_notes_cover_translation_issues_and_installer_upgrade(self) -> None:
        notes = NOTES.read_text(encoding="utf-8")
        for text in (
            "## v0.13.0 — 번역 품질 개선·고해상도 지도 라벨·명소 가로쓰기",
            "이벤트 대사 **26건**",
            "인물 대사 **51건**",
            "총 **77건**",
            "Issue #68",
            "4096×2048",
            "4096×4096",
            "Issue #70",
            "아쓰타 신궁",
            "800×450",
            "완전히 종료하고 새",
            "v0.12.0 사용자는 v0.13.0 ZIP을 게임 폴더에 덮어쓴 뒤 반드시 새",
            "`APPLY_STATIC_EXE_PATCHES.bat`를 다시 실행해야 합니다",
            "파일만 덮어쓰면\n  EXE에는 `005`가 적용되지 않습니다",
            "v0.12.0에서 배포한 `004` 정의와 페이로드는 변경하지 않습니다",
            "001~004`가 이미 적용된 EXE는 `005`만 자동 적용",
            "BE983A61C81008289E2483D552122C0BE3299B5F8DD4A557FA14DA2663AC7BD6",
            "A62410EB857001306EE699FD85CE429AC9A8966619F742FA4AB07BB413308255",
            "380,395,760 bytes",
        ):
            self.assertIn(text, notes)
        self.assertIn("v0.13.0 ZIP SHA-256:", notes)
        self.assertNotIn("현재 릴리즈 후보 문서", notes)


if __name__ == "__main__":
    unittest.main()
