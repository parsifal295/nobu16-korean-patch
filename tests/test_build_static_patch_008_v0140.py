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
SCRIPT = TOOLS / "build_static_patch_008_v0140.py"
DEFINITION = (
    ROOT
    / "release_payload"
    / "v0.14.0"
    / "OfficerEditorStaticFix"
    / "Patches"
    / "008-HorizontalMapAuxiliaryIndicators.psd1"
)

spec = importlib.util.spec_from_file_location("build_static_patch_008_v0140", SCRIPT)
assert spec and spec.loader
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class BuildStaticPatch008V0140Tests(unittest.TestCase):
    def test_builder_contract_is_pinned(self) -> None:
        self.assertEqual(builder.TARGET_SIZE, 67_024_384)
        self.assertEqual(
            builder.EXPECTED_V0140_SHA256,
            "F424964405CFCD1AC454B3801DA4795A183A8271DD16EA8A6A7B97A2547232BF",
        )
        self.assertEqual(
            builder.EXPECTED_PATCH008_SHA256,
            "01C8769F09BD9A5459844FF5E335A71048C1F11CC7AF7738517EFEE61D4BF28D",
        )

    def test_generated_definition_is_exact_and_auxiliary_scoped(self) -> None:
        source = DEFINITION.read_text(encoding="ascii")
        self.assertIn("Id = '008'", source)
        self.assertIn("Kind = 'BytePatch'", source)
        self.assertIn("Dynamic map auxiliary indicator alignment", source)
        self.assertIn("battle-ready number", source)
        self.assertIn("no-castle-lord warning", source)
        self.assertEqual(source.count("Before = '"), 3)
        self.assertEqual(source.count("After = '"), 3)
        offsets = [int(value, 16) for value in re.findall(r"Offset = 0x([0-9A-F]+)", source)]
        self.assertEqual(offsets, [0x000003C0, 0x03FEB4FD, 0x03FEB510])
        self.assertIn("Before = '4883C458C3'; After = 'E90E000000'", source)
        self.assertEqual(len(DEFINITION.read_bytes()), 1_362)
        self.assertEqual(
            hashlib.sha256(DEFINITION.read_bytes()).hexdigest().upper(),
            "91DFFF797E00D62567494519E7772ED42A3A966B5D25E488C31BD1B0DD8F0D6F",
        )


if __name__ == "__main__":
    unittest.main()
