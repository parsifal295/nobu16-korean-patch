from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "release_payload" / "v0.14.0"
PREVIOUS_PAYLOAD = ROOT / "release_payload" / "v0.13.1"
STATIC_ROOT = PAYLOAD / "OfficerEditorStaticFix"
PREVIOUS_STATIC_ROOT = PREVIOUS_PAYLOAD / "OfficerEditorStaticFix"
PATCH_ROOT = STATIC_ROOT / "Patches"
REGISTRY = STATIC_ROOT / "000-PatchRegistry.psd1"
PATCH_007 = PATCH_ROOT / "007-EventMessageTypography.psd1"


class StaticEventMessageTypographyInstallerV0140Tests(unittest.TestCase):
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

    def test_published_v0131_installer_files_are_unchanged(self) -> None:
        relative_paths = [
            Path("../APPLY_STATIC_EXE_PATCHES.bat"),
            Path("../APPLY_STATIC_OFFICER_EDITOR_FIX.bat"),
            Path("../RESTORE_ORIGINAL_NOBU16PK_EXE.bat"),
            Path("Invoke-Nobu16StaticPatches.ps1"),
            Path("Invoke-StaticOfficerEditorFix.ps1"),
            Path("THIRD_PARTY_NOTICES.txt"),
            Path("Steamless/Steamless.CLI.exe"),
            Path("Steamless/Steamless.CLI.exe.config"),
            Path("Steamless/Plugins/Steamless.API.dll"),
            Path("Steamless/Plugins/Steamless.Unpacker.Variant31.x64.dll"),
            *(Path("Patches") / name for name in (
                "001-OfficerEditorNameValidation.psd1",
                "002-FictionalPrincessNameValidation.psd1",
                "003-TopHeaderLayout.psd1",
                "004-HorizontalMapLabelsDynamicWidth.psd1",
                "005-DualResolutionAndHorizontalLandmarks.psd1",
                "006-HorizontalMapStatusIcons.psd1",
            )),
            Path("Patches/Payloads/004-HorizontalMapLabelsDynamicWidth.append.gz"),
            Path("Patches/Payloads/005-DualResolutionAndHorizontalLandmarks.append.gz"),
        ]
        for relative in relative_paths:
            self.assertEqual(
                (STATIC_ROOT / relative).read_bytes(),
                (PREVIOUS_STATIC_ROOT / relative).read_bytes(),
                str(relative),
            )

    def test_patch_007_is_the_reviewed_same_size_byte_patch(self) -> None:
        source = PATCH_007.read_text(encoding="ascii")
        self.assertIn("Kind = 'BytePatch'", source)
        self.assertIn("Compact event message typography", source)
        self.assertEqual(source.count("Before = '"), 2)
        self.assertEqual(source.count("After = '"), 2)
        offsets = [int(value, 16) for value in re.findall(r"Offset = 0x([0-9A-F]+)", source)]
        self.assertEqual(offsets, [0x0089957A, 0x008995BC])
        self.assertIn("Before = 'BF000A0000'; After = 'BF00080000'", source)
        self.assertIn("Before = 'B924000000'; After = 'B91E000000'", source)
        self.assertEqual(len(PATCH_007.read_bytes()), 378)
        self.assertEqual(
            hashlib.sha256(PATCH_007.read_bytes()).hexdigest().upper(),
            "B9370AA005202CB2E3D2FA22B5F33265517D8354851B434B4A3844EC50796F78",
        )

    def test_payload_has_no_game_executable_or_new_append_payload(self) -> None:
        self.assertFalse(any(PAYLOAD.rglob("NOBU16PK.exe")))
        payload_names = tuple(
            path.name for path in sorted((PATCH_ROOT / "Payloads").glob("*.gz"))
        )
        self.assertEqual(
            payload_names,
            (
                "004-HorizontalMapLabelsDynamicWidth.append.gz",
                "005-DualResolutionAndHorizontalLandmarks.append.gz",
            ),
        )

    def test_installer_and_project_readmes_document_patch_007(self) -> None:
        installer_readme = (PAYLOAD / "STATIC_OFFICER_EDITOR_FIX_README_KO.txt").read_text(
            encoding="utf-8"
        )
        project_readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for source in (installer_readme, project_readme):
            for text in (
                "007",
                "글자 크기",
                "36에서 30",
                "줄간격",
                "10에서 8",
                "v0.13.1",
                "APPLY_STATIC_EXE_PATCHES.bat",
                "F424964405CFCD1AC454B3801DA4795A183A8271DD16EA8A6A7B97A2547232BF",
            ):
                self.assertIn(text, source)

        attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
        self.assertIn("/release_payload/v0.14.0/*.bat text eol=lf", attributes)
        self.assertIn(
            "/release_payload/v0.14.0/OfficerEditorStaticFix/Steamless/Steamless.CLI.exe.config binary",
            attributes,
        )


if __name__ == "__main__":
    unittest.main()
