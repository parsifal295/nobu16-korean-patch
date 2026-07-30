from __future__ import annotations

import hashlib
import importlib.util
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))
SCRIPT = TOOLS / "build_static_patch_006_v0131.py"
DEFINITION = (
    ROOT
    / "release_payload"
    / "v0.13.1"
    / "OfficerEditorStaticFix"
    / "Patches"
    / "006-HorizontalMapStatusIcons.psd1"
)


spec = importlib.util.spec_from_file_location("build_static_patch_006_v0131", SCRIPT)
assert spec and spec.loader
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class BuildStaticPatch006V0131Tests(unittest.TestCase):
    def test_builder_contract_is_pinned(self) -> None:
        self.assertEqual(builder.TARGET_SIZE, 67_024_384)
        self.assertEqual(
            builder.EXPECTED_V0130_SHA256,
            "FCA1D8CF58D44BDFAEFF338F5CF935AB9B2FA0F611EDC26CC8E9DF6E40B9D892",
        )
        self.assertEqual(
            builder.EXPECTED_V0131_SHA256,
            "3548AD5B71168296DD03851B1F9613CAD1C325AF2AB916A11CC140DC61FA0E43",
        )
        self.assertEqual(
            builder.EXPECTED_V0130_INSTALLED_SHA256,
            "BE983A61C81008289E2483D552122C0BE3299B5F8DD4A557FA14DA2663AC7BD6",
        )
        self.assertEqual(
            builder.EXPECTED_V0131_INSTALLED_SHA256,
            "3548AD5B71168296DD03851B1F9613CAD1C325AF2AB916A11CC140DC61FA0E43",
        )

    def test_generated_definition_is_exact_and_semantic(self) -> None:
        source = DEFINITION.read_text(encoding="ascii")
        self.assertIn("Id = '006'", source)
        self.assertIn("Kind = 'BytePatch'", source)
        self.assertIn("Dynamic horizontal map status alignment", source)
        self.assertIn("dynamic map status X/Y wrapper preserving troop-count root", source)
        self.assertEqual(source.count("Before = '"), 4)
        self.assertEqual(source.count("After = '"), 4)
        offsets = [int(value, 16) for value in re.findall(r"Offset = 0x([0-9A-F]+)", source)]
        self.assertEqual(len(offsets), len(set(offsets)))
        self.assertEqual(offsets, [0x000003C0, 0x000003DC, 0x00F97B64, 0x03FEB460])
        self.assertIn("Before = '" + "00" * 162 + "'", source)
        self.assertEqual(len(DEFINITION.read_bytes()), 1_294)
        digest = hashlib.sha256(DEFINITION.read_bytes()).hexdigest().upper()
        self.assertEqual(
            digest,
            "47B668CD1988C1393F051C4253FE2E895F42D4D1228C50174232F2EB96806625",
        )


if __name__ == "__main__":
    unittest.main()
