from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "RELEASE_NOTES_v0.11.5_KO.md"


class ReleaseNotesV0115Tests(unittest.TestCase):
    def test_notes_cover_issue_62_installation_and_release_asset(self) -> None:
        notes = NOTES.read_text(encoding="utf-8")
        self.assertIn("## v0.11.5 — 가공 히메 한글 작명 허용", notes)
        self.assertIn("Issue #62", notes)
        self.assertIn("네 호출부", notes)
        self.assertIn("공용 문자 검증기를 바꾸지 않고", notes)
        self.assertIn("공란 검사", notes)
        self.assertIn("성+이름 합산 길이 제한", notes)
        self.assertIn(
            "2E098ECB5E4335DC264F865306B990B724EA7C242B1B9F87FFC5EE2E7191797C",
            notes,
        )
        self.assertIn(
            "7CA2F1D59E02650C67F343F0776F6D05517C0486B65168E63A9AE4CBCAAFDBB2",
            notes,
        )
        self.assertIn("APPLY_STATIC_OFFICER_EDITOR_FIX.bat", notes)
        self.assertIn(
            "5B9CF5E245808DB532B60C27C847254F3A22987FF57A75467ED34C8C5942127D",
            notes,
        )


if __name__ == "__main__":
    unittest.main()
