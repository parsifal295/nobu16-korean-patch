from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "release_payload" / "v0.15.0"
REGISTRY = PAYLOAD / "OfficerEditorStaticFix" / "000-PatchRegistry.psd1"
STATIC = PAYLOAD / "OfficerEditorStaticFix" / "Invoke-Nobu16StaticPatches.ps1"
COORDINATOR = PAYLOAD / "Invoke-Nobu16KoreanPatch.ps1"


class CastleNameLayoutProfileV0150Tests(unittest.TestCase):
    def test_registry_pins_vertical_and_horizontal_profiles(self) -> None:
        source = REGISTRY.read_text(encoding="ascii")
        self.assertIn("Release = 'v0.15.0'", source)
        self.assertRegex(
            source,
            re.compile(
                r"Vertical\s*=\s*@\{.*?PatchIds\s*=\s*@\("
                r"'001', '002', '003', '007', '009', '010'\).*?"
                r"3964E160B789982E1E197F77CBA3F592AFF0144F063E7AFCAC4DCEB4C6C99CB4",
                re.S,
            ),
        )
        self.assertRegex(
            source,
            re.compile(
                r"Horizontal\s*=\s*@\{.*?PatchIds\s*=\s*@\("
                r"'001', '002', '003', '004', '005', '006', '007', '008', '009', '010'\).*?"
                r"C1E9123539506055C1ACB96A15A446C43952AED607DEA2C9646F690813FA53D5",
                re.S,
            ),
        )

    def test_vertical_excludes_horizontal_map_and_icon_patches(self) -> None:
        registry = REGISTRY.read_text(encoding="ascii")
        vertical = registry.split("Vertical = @{", 1)[1].split("Horizontal = @{", 1)[0]
        for patch_id in ("004", "005", "006", "008"):
            self.assertNotIn(f"'{patch_id}'", vertical)
        static = STATIC.read_text(encoding="utf-8-sig")
        self.assertIn("Rebuild every requested profile from the protected original", static)
        self.assertIn("Get-UnpackedBytes $BackupPath $workRoot", static)
        self.assertIn("[ValidateSet('Vertical', 'Horizontal')]", static)

    def test_interactive_choice_and_readme_contract(self) -> None:
        source = COORDINATOR.read_text(encoding="utf-8-sig")
        self.assertIn("Read-Host '번호 입력 [1/2]'", source)
        self.assertIn("if ($choice -eq '1')", source)
        self.assertIn("return 'Vertical'", source)
        self.assertIn("if ($choice -eq '2')", source)
        self.assertIn("return 'Horizontal'", source)
        readme = (PAYLOAD / "PATCHER_README_KO.txt").read_text(encoding="utf-8")
        self.assertIn("1: 세로쓰기", readme)
        self.assertIn("004, 005, 006, 008", readme)
        self.assertIn("2: 가로쓰기", readme)


if __name__ == "__main__":
    unittest.main()
