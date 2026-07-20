from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "RELEASE_NOTES_v0.13.1_KO.md"


class ReleaseNotesV0131Tests(unittest.TestCase):
    def test_notes_cover_issue_72_installer_upgrade_and_artifact(self) -> None:
        notes = NOTES.read_text(encoding="utf-8")
        for text in (
            "## v0.13.1 — 지도 성 이름 뒤 상태 아이콘 동적 정렬",
            "Issue #72",
            "전투 준비",
            "방위 거점",
            "공략 목표",
            "병사수",
            "라벨 Y + (라벨 높이 - 아이콘 높이) / 2",
            "v0.13.0 사용자는 v0.13.1 ZIP을 게임 폴더에 덮어쓴 뒤 반드시 새",
            "`APPLY_STATIC_EXE_PATCHES.bat`를 다시 실행해야 합니다",
            "파일만 덮어쓰면\n  EXE에는 `006`이 적용되지 않습니다",
            "001~005`가 적용된 EXE는 `006`만 자동 적용",
            "001~004`가 적용된 EXE는 `005`와 `006`만 순서대로 적용",
            "1920×1080",
            "완전히 종료하고 새 프로세스로 재실행",
            "3548AD5B71168296DD03851B1F9613CAD1C325AF2AB916A11CC140DC61FA0E43",
            "7A670A03ACAB2CED43D8F27392CD1F31DB92CD16CB6B0EF04909B8E519A57FDF",
            "380,397,094",
            "총 35개 멤버",
            "`NOBU16PK.exe`는 포함하지 않습니다",
        ):
            self.assertIn(text, notes)
        self.assertNotIn("TO_BE_PINNED", notes)


if __name__ == "__main__":
    unittest.main()
