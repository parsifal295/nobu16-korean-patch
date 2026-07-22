from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "RELEASE_NOTES_v0.15.0_KO.md"


class ReleaseNotesV0150Tests(unittest.TestCase):
    def test_notes_cover_release_scope_installation_and_artifact(self) -> None:
        notes = NOTES.read_text(encoding="utf-8")
        for text in (
            "# NOBU16 PK 한글 패치 v0.15.0 릴리즈 노트",
            "DLC 리소스 **105개**",
            "없는 DLC는 오류 없이 건너뜁니다",
            "`BASE LOW`",
            "`PORT1 HIGH`",
            "`PORT3 HIGH`",
            "영양군 음식디미방체",
            "`1` 세로쓰기",
            "`2` 가로쓰기",
            "`004`, `005`, `006`,",
            "`008`은 적용하지 않습니다",
            "필수 리소스 16개",
            "이미지 아틀라스 6개",
            "실게임 이미지 QA는 수행하지 않았습니다",
            "50C1886C587EA0634506F32428D6EEF35EAECCA1FA6DF7CF117EA1B49F2F5CA0",
            "134,592,423",
        ):
            self.assertIn(text, notes)


if __name__ == "__main__":
    unittest.main()
