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
SCRIPT = TOOLS / "build_static_patch_007_v0140.py"
DEFINITION = (
    ROOT
    / "release_payload"
    / "v0.14.0"
    / "OfficerEditorStaticFix"
    / "Patches"
    / "007-EventMessageTypography.psd1"
)


spec = importlib.util.spec_from_file_location("build_static_patch_007_v0140", SCRIPT)
assert spec and spec.loader
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class BuildStaticPatch007V0140Tests(unittest.TestCase):
    def test_builder_contract_is_pinned(self) -> None:
        self.assertEqual(builder.TARGET_SIZE, 67_024_384)
        self.assertEqual(builder.LINE_SPACING_VA, 0x14089A17A)
        self.assertEqual(builder.FONT_SIZE_VA, 0x14089A1BC)
        self.assertEqual(
            builder.EXPECTED_V0131_SHA256,
            "3548AD5B71168296DD03851B1F9613CAD1C325AF2AB916A11CC140DC61FA0E43",
        )
        self.assertEqual(
            builder.EXPECTED_V0140_SHA256,
            "F424964405CFCD1AC454B3801DA4795A183A8271DD16EA8A6A7B97A2547232BF",
        )

    def test_generated_definition_is_exact_and_event_scoped(self) -> None:
        source = DEFINITION.read_text(encoding="ascii")
        self.assertIn("Id = '007'", source)
        self.assertIn("Kind = 'BytePatch'", source)
        self.assertIn("Compact event message typography", source)
        self.assertIn("line spacing from 10 to 8", source)
        self.assertIn("font size from 36 to 30", source)
        self.assertEqual(source.count("Before = '"), 2)
        self.assertEqual(source.count("After = '"), 2)
        offsets = [int(value, 16) for value in re.findall(r"Offset = 0x([0-9A-F]+)", source)]
        self.assertEqual(offsets, [0x0089957A, 0x008995BC])
        self.assertIn("Before = 'BF000A0000'; After = 'BF00080000'", source)
        self.assertIn("Before = 'B924000000'; After = 'B91E000000'", source)
        self.assertEqual(len(DEFINITION.read_bytes()), 378)
        self.assertEqual(
            hashlib.sha256(DEFINITION.read_bytes()).hexdigest().upper(),
            "B9370AA005202CB2E3D2FA22B5F33265517D8354851B434B4A3844EC50796F78",
        )


if __name__ == "__main__":
    unittest.main()
