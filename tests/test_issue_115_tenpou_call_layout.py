from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "workstreams" / "rust_patcher_v1" / "rust" / "tools"
PATCHER = TOOLS / "Set-TenpouCallPersonWidths.ps1"
GENERATOR = TOOLS / "New-V0910ResourceSpec.ps1"
AUDIT = ROOT / "workstreams" / "issue_115_tenpou_call_layout_v1" / "README_KO.md"


class Issue115TenpouCallLayoutTests(unittest.TestCase):
    def test_width_patcher_has_two_hash_pinned_contracts(self) -> None:
        if not PATCHER.is_file():
            self.skipTest("private product width patcher is not published")
        text = PATCHER.read_text(encoding="utf-8")
        self.assertIn("PARAM_PK/Person_Tenpou_Call_LeftInfo.bin", text)
        self.assertIn("PARAM_PK/Person_Tenpou_Call_RightInfo.bin", text)
        self.assertIn("D3C20281580CB596237DFD2B58D9DF8C2F38983D48F450A0D027F7671E71F995", text)
        self.assertIn("587D1939536ED4AB648B068FC42C4E26E9791F233727C04939E5CD385E691A7B", text)
        self.assertIn("if ($groupTotals[$group] -gt 800)", text)
        self.assertEqual(2, len(re.findall(r"TargetSha256 = '[0-9A-F]{64}'", text)))

    def test_generator_tracks_and_applies_both_param_files(self) -> None:
        if not GENERATOR.is_file():
            self.skipTest("private product resource generator is not published")
        text = GENERATOR.read_text(encoding="utf-8")
        self.assertIn("$tenpouCallFiles", text)
        self.assertIn("'PARAM_PK/Person_Tenpou_Call_LeftInfo.bin'", text)
        self.assertIn("'PARAM_PK/Person_Tenpou_Call_RightInfo.bin'", text)
        self.assertIn("'Set-TenpouCallPersonWidths.ps1'", text)

    def test_audit_records_every_profile_and_800px_limit(self) -> None:
        text = AUDIT.read_text(encoding="utf-8")
        self.assertIn("사용 가능 총폭은 모든 프로필에서 800px", text)
        for group in ("0120", "0038", "0122", "1210", "0482", "2248", "0712", "2098", "1138"):
            self.assertIn(f"`{group}`", text)
        self.assertIn("| `0712` | 188 | 584 | 216 | 300 | 696 |", text)
        self.assertIn("| `0482` | 216 | 612 | 188 | 300 | 696 |", text)


if __name__ == "__main__":
    unittest.main()
