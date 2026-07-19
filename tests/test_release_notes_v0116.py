from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "RELEASE_NOTES_v0.11.6_KO.md"


class ReleaseNotesV0116Tests(unittest.TestCase):
    def test_notes_state_the_exact_text_scope_and_npc_examples(self) -> None:
        notes = NOTES.read_text(encoding="utf-8")
        self.assertIn(
            "## v0.11.6 — NPC 표기·인물 대사·이벤트 줄바꿈·상단 헤더 누적 보정",
            notes,
        )
        self.assertIn("**6개**", notes)
        self.assertIn("**276개**", notes)
        self.assertIn("인물 대사 **205개**", notes)
        self.assertIn("조합 조각 **46개**", notes)
        self.assertIn("줄바꿈 **25개**", notes)
        for before, after in (
            ("덴령", "전령"),
            ("상사람", "상인"),
            ("선교모로", "선교사"),
            ("소성씨", "시동"),
            ("가인", "가신"),
        ):
            self.assertIn(f"`{before}` → `{after}`", notes)
        self.assertIn("우에무라 라이렌", notes)
        self.assertIn("쿠시마 마사노부", notes)
        self.assertIn("상단 헤더", notes)
        self.assertIn("12개", notes)
        self.assertIn("총 21개 지점", notes)
        self.assertIn("Pending 항목만 적용", notes)
        self.assertIn("설치·지원 파일 15개, 총 30개", notes)
        self.assertIn("APPLY_STATIC_EXE_PATCHES.bat", notes)
        self.assertIn("스위치판 한글은", notes)
        self.assertIn("6B3C2A8DF5B419EF78F2C87C3C3840D1E276E7D51B1C00BE2B61B6BABD8DE9F3", notes)


if __name__ == "__main__":
    unittest.main()
