from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "RELEASE_NOTES_v0.15.1_KO.md"


class ReleaseNotesV0151Tests(unittest.TestCase):
    def test_hotfix_notes_pin_correct_port3_and_artifact(self) -> None:
        notes = NOTES.read_text(encoding="utf-8")
        for text in (
            "# NOBU16 PK 한글 패치 v0.15.1 릴리즈 노트",
            "Resource stage Preflight failed",
            "BE1361E17341D433931EB5740B228EF1842BF6DF2F01D4F582CE790A9A57A154",
            "BA739C28A8EE1A47C8085339F98FDCF4F317302316F93C3F74E413DB2AFEADC9",
            "DLC가 하나도 없어도",
            "writes_performed: false",
            "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.15.1.zip",
            "134,592,418",
            "976ED03927DB5D0315AAFF43DF5C5B4962446B1C95434BB36DBDA39B5FFFB759",
        ):
            self.assertIn(text, notes)


if __name__ == "__main__":
    unittest.main()
