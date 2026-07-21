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
SCRIPT = TOOLS / "build_static_patch_010_v0140.py"
DEFINITION = (
    ROOT
    / "release_payload"
    / "v0.14.0"
    / "OfficerEditorStaticFix"
    / "Patches"
    / "010-EventMessageAutoWrapLimit.psd1"
)


spec = importlib.util.spec_from_file_location("build_static_patch_010_v0140", SCRIPT)
assert spec and spec.loader
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class BuildStaticPatch010V0140Tests(unittest.TestCase):
    def test_builder_contract_is_pinned(self) -> None:
        self.assertEqual(builder.TARGET_SIZE, 67_024_384)
        self.assertEqual(builder.AUTO_WRAP_WIDTH_BEFORE, bytes.fromhex("27"))
        self.assertEqual(builder.AUTO_WRAP_WIDTH_AFTER, bytes.fromhex("3B"))
        self.assertEqual(
            builder.AUTO_WRAP_SITES,
            (
                (
                    "expand primary event auto-wrap limit from 40 to 60",
                    0x0085C9D4,
                    bytes.fromhex("458D4127488D5590498BCEE81FC11900"),
                ),
                (
                    "expand alternate event auto-wrap limit from 40 to 60",
                    0x0088F6F1,
                    bytes.fromhex("458D4127488D542440498BCEE801941600"),
                ),
            ),
        )
        self.assertEqual(
            builder.EXPECTED_PATCH009_SHA256,
            "4ED6C7DBF3F9DF55F574D285DF82653C9A48BC4212DBF8728DE225946A34D730",
        )
        self.assertEqual(
            builder.EXPECTED_PATCH010_SHA256,
            "C1E9123539506055C1ACB96A15A446C43952AED607DEA2C9646F690813FA53D5",
        )

    def test_generated_definition_is_exact_and_event_scoped(self) -> None:
        source = DEFINITION.read_text(encoding="ascii")
        self.assertIn("Id = '010'", source)
        self.assertIn("Kind = 'BytePatch'", source)
        self.assertIn("event message auto-wrap", source)
        self.assertEqual(source.count("Before = '"), 2)
        self.assertEqual(source.count("After = '"), 2)
        offsets = [int(value, 16) for value in re.findall(r"Offset = 0x([0-9A-F]+)", source)]
        self.assertEqual(offsets, [0x0085BDD4, 0x0088EAF1])
        self.assertIn("Before = '27'; After = '3B'", source)
        self.assertEqual(len(DEFINITION.read_bytes()), 364)
        self.assertEqual(
            hashlib.sha256(DEFINITION.read_bytes()).hexdigest().upper(),
            "D16D8CA248563EE9A595D0E7BD3D5E2544C1181193ADDCA49B881BCA3FAEEECC",
        )


if __name__ == "__main__":
    unittest.main()
