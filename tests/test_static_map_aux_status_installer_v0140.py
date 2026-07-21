from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "release_payload" / "v0.14.0"
STATIC_ROOT = PAYLOAD / "OfficerEditorStaticFix"
PATCH_ROOT = STATIC_ROOT / "Patches"
REGISTRY = STATIC_ROOT / "000-PatchRegistry.psd1"
PATCH_008 = PATCH_ROOT / "008-HorizontalMapAuxiliaryIndicators.psd1"


class StaticMapAuxStatusInstallerV0140Tests(unittest.TestCase):
    def test_registry_owns_ten_ordered_patch_definitions(self) -> None:
        expected = (
            "001-OfficerEditorNameValidation.psd1",
            "002-FictionalPrincessNameValidation.psd1",
            "003-TopHeaderLayout.psd1",
            "004-HorizontalMapLabelsDynamicWidth.psd1",
            "005-DualResolutionAndHorizontalLandmarks.psd1",
            "006-HorizontalMapStatusIcons.psd1",
            "007-EventMessageTypography.psd1",
            "008-HorizontalMapAuxiliaryIndicators.psd1",
            "009-EventMessageParentWidth.psd1",
            "010-EventMessageAutoWrapLimit.psd1",
        )
        self.assertEqual(tuple(path.name for path in sorted(PATCH_ROOT.glob("*.psd1"))), expected)
        registry = REGISTRY.read_text(encoding="ascii")
        self.assertIn("nobu16.static-exe-patch-registry.v3", registry)
        self.assertIn("Release = 'v0.14.0'", registry)
        self.assertIn(
            "AllAppliedSha256 = "
            "'C1E9123539506055C1ACB96A15A446C43952AED607DEA2C9646F690813FA53D5'",
            registry,
        )
        for name in expected:
            self.assertIn(f"Patches/{name}", registry)

    def test_published_patch_006_and_patch_007_definitions_are_unchanged(self) -> None:
        pinned = {
            "006-HorizontalMapStatusIcons.psd1": (
                1_294,
                "47B668CD1988C1393F051C4253FE2E895F42D4D1228C50174232F2EB96806625",
            ),
            "007-EventMessageTypography.psd1": (
                378,
                "B9370AA005202CB2E3D2FA22B5F33265517D8354851B434B4A3844EC50796F78",
            ),
        }
        for name, (size, expected_hash) in pinned.items():
            data = (PATCH_ROOT / name).read_bytes()
            self.assertEqual(len(data), size)
            self.assertEqual(hashlib.sha256(data).hexdigest().upper(), expected_hash)

    def test_patch_008_is_the_reviewed_same_size_byte_patch(self) -> None:
        source = PATCH_008.read_text(encoding="ascii")
        self.assertIn("Kind = 'BytePatch'", source)
        self.assertIn("Dynamic map auxiliary indicator alignment", source)
        self.assertEqual(source.count("Before = '"), 3)
        self.assertEqual(source.count("After = '"), 3)
        offsets = [int(value, 16) for value in re.findall(r"Offset = 0x([0-9A-F]+)", source)]
        self.assertEqual(offsets, [0x000003C0, 0x03FEB4FD, 0x03FEB510])

    def test_payload_has_no_game_executable_or_new_append_payload(self) -> None:
        self.assertFalse(any(PAYLOAD.rglob("NOBU16PK.exe")))
        payload_names = tuple(path.name for path in sorted((PATCH_ROOT / "Payloads").glob("*.gz")))
        self.assertEqual(
            payload_names,
            (
                "004-HorizontalMapLabelsDynamicWidth.append.gz",
                "005-DualResolutionAndHorizontalLandmarks.append.gz",
            ),
        )

    def test_docs_explain_patch_008_and_unified_entrypoint(self) -> None:
        source = (ROOT / "README.md").read_text(encoding="utf-8")
        for text in (
            "008",
            "20px",
            "임전 숫자",
            "성주 미임명",
            "APPLY_KOREAN_PATCH.bat",
            "01C8769F09BD9A5459844FF5E335A71048C1F11CC7AF7738517EFEE61D4BF28D",
        ):
            self.assertIn(text, source)


if __name__ == "__main__":
    unittest.main()
