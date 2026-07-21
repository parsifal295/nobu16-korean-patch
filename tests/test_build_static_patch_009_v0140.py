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
SCRIPT = TOOLS / "build_static_patch_009_v0140.py"
DEFINITION = (
    ROOT
    / "release_payload"
    / "v0.14.0"
    / "OfficerEditorStaticFix"
    / "Patches"
    / "009-EventMessageParentWidth.psd1"
)


spec = importlib.util.spec_from_file_location("build_static_patch_009_v0140", SCRIPT)
assert spec and spec.loader
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class BuildStaticPatch009V0140Tests(unittest.TestCase):
    def test_builder_contract_is_pinned(self) -> None:
        self.assertEqual(builder.TARGET_SIZE, 67_024_384)
        self.assertEqual(builder.PARENT_WIDTH_VA, 0x14151D388)
        self.assertEqual(builder.PARENT_WIDTH_BEFORE, bytes.fromhex("00805C44"))
        self.assertEqual(builder.PARENT_WIDTH_AFTER, bytes.fromhex("00007344"))
        self.assertEqual(
            builder.EXPECTED_PATCH008_SHA256,
            "01C8769F09BD9A5459844FF5E335A71048C1F11CC7AF7738517EFEE61D4BF28D",
        )
        self.assertEqual(
            builder.EXPECTED_PATCH009_SHA256,
            "4ED6C7DBF3F9DF55F574D285DF82653C9A48BC4212DBF8728DE225946A34D730",
        )

    def test_generated_definition_is_exact_and_event_scoped(self) -> None:
        source = DEFINITION.read_text(encoding="ascii")
        self.assertIn("Id = '009'", source)
        self.assertIn("Kind = 'BytePatch'", source)
        self.assertIn("Expand event message parent width", source)
        self.assertEqual(source.count("Before = '"), 1)
        self.assertEqual(source.count("After = '"), 1)
        offsets = [int(value, 16) for value in re.findall(r"Offset = 0x([0-9A-F]+)", source)]
        self.assertEqual(offsets, [0x0151BD88])
        self.assertIn("Before = '00805C44'; After = '00007344'", source)
        self.assertEqual(len(DEFINITION.read_bytes()), 245)
        self.assertEqual(
            hashlib.sha256(DEFINITION.read_bytes()).hexdigest().upper(),
            "CB70279E78F1B7C2B7F5ED633C5B966D34D8680EEB595BC7C00A8BE1FC57133E",
        )


if __name__ == "__main__":
    unittest.main()
