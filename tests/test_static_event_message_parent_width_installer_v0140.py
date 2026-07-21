from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "release_payload" / "v0.14.0"
STATIC_ROOT = PAYLOAD / "OfficerEditorStaticFix"
REGISTRY = STATIC_ROOT / "000-PatchRegistry.psd1"
PATCH_009 = STATIC_ROOT / "Patches" / "009-EventMessageParentWidth.psd1"


class StaticEventMessageParentWidthInstallerV0140Tests(unittest.TestCase):
    def test_patch_009_is_a_single_same_size_event_width_patch(self) -> None:
        source = PATCH_009.read_text(encoding="ascii")
        self.assertIn("Id = '009'", source)
        self.assertIn("Kind = 'BytePatch'", source)
        self.assertIn("event message parent width", source)
        self.assertEqual(source.count("Before = '"), 1)
        self.assertEqual(source.count("After = '"), 1)
        self.assertIn("Offset = 0x0151BD88", source)
        self.assertIn("Before = '00805C44'; After = '00007344'", source)

    def test_registry_chains_patch_009_after_patch_008(self) -> None:
        source = REGISTRY.read_text(encoding="ascii")
        self.assertIn("Patches/008-HorizontalMapAuxiliaryIndicators.psd1", source)
        self.assertIn("Patches/009-EventMessageParentWidth.psd1", source)
        self.assertLess(
            source.index("Patches/008-HorizontalMapAuxiliaryIndicators.psd1"),
            source.index("Patches/009-EventMessageParentWidth.psd1"),
        )
        self.assertIn(
            "AllAppliedSha256 = "
            "'C1E9123539506055C1ACB96A15A446C43952AED607DEA2C9646F690813FA53D5'",
            source,
        )

    def test_payload_does_not_ship_a_game_executable(self) -> None:
        self.assertFalse(any(PAYLOAD.rglob("NOBU16PK.exe")))


if __name__ == "__main__":
    unittest.main()
