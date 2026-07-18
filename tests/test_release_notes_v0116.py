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
        self.assertIn("스위치판 한글은", notes)
        self.assertIn("9BF487C431164B24CBEE5B97E3A8BB03FB77C20B6D7DD8BF9BAEC19A96BB85B1", notes)


if __name__ == "__main__":
    unittest.main()
