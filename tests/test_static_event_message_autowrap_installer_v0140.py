from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "release_payload" / "v0.14.0"
STATIC_ROOT = PAYLOAD / "OfficerEditorStaticFix"
REGISTRY = STATIC_ROOT / "000-PatchRegistry.psd1"
PATCH_010 = STATIC_ROOT / "Patches" / "010-EventMessageAutoWrapLimit.psd1"


class StaticEventMessageAutowrapInstallerV0140Tests(unittest.TestCase):
    def test_patch_010_has_two_same_size_event_formatter_sites(self) -> None:
        source = PATCH_010.read_text(encoding="ascii")
        self.assertIn("Id = '010'", source)
        self.assertIn("Kind = 'BytePatch'", source)
        self.assertIn("event message auto-wrap", source)
        self.assertEqual(source.count("Before = '"), 2)
        self.assertEqual(source.count("After = '"), 2)
        self.assertIn("Offset = 0x0085BDD4", source)
        self.assertIn("Offset = 0x0088EAF1", source)
        self.assertIn("Before = '27'; After = '3B'", source)

    def test_registry_chains_patch_010_after_parent_width(self) -> None:
        source = REGISTRY.read_text(encoding="ascii")
        self.assertIn("Patches/009-EventMessageParentWidth.psd1", source)
        self.assertIn("Patches/010-EventMessageAutoWrapLimit.psd1", source)
        self.assertLess(
            source.index("Patches/009-EventMessageParentWidth.psd1"),
            source.index("Patches/010-EventMessageAutoWrapLimit.psd1"),
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
