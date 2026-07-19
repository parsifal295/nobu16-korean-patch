from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "RELEASE_NOTES_v0.12.0_KO.md"


class ReleaseNotesV0120Tests(unittest.TestCase):
    def test_notes_document_dynamic_map_labels_and_installer_upgrade(self) -> None:
        notes = NOTES.read_text(encoding="utf-8")
        for text in (
            "지도 성·지명 가로쓰기",
            "실제 UTF-16 문자열 길이",
            "공백과 `성` 접미사",
            "최대 글자 수 제한을 두지 않습니다",
            "`001~003`이 이미 적용된 EXE에서는 `004`만 자동 적용",
            "재실행 시 모든 항목을 `Applied`로 판정",
            "1920x1080",
            "완전히 종료하고 새 프로세스로 재실행",
            "최장 표시 문자열 9자",
            "A430615A2D6EAD81B0B50DB6D9055FB77BD3E6CC7EEEAE7F145D203960B5C98E",
            "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.12.0.zip",
            "375,721,788 bytes",
            "624B507EB239F82A2BD9CD5856B8FA0048CDFE3BE285FFF549A5E6C05E2766A4",
        ):
            self.assertIn(text, notes)


if __name__ == "__main__":
    unittest.main()
