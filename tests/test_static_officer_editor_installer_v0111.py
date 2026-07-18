from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "release_payload"
    / "v0.11.1"
    / "OfficerEditorStaticFix"
    / "Invoke-StaticOfficerEditorFix.ps1"
)


def load_release_module():
    path = ROOT / "tools" / "build_steam_jp_v0111_release.py"
    spec = importlib.util.spec_from_file_location("static_release", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


release = load_release_module()


class StaticOfficerEditorInstallerV0111Tests(unittest.TestCase):
    def test_static_patch_contract_is_pinned(self) -> None:
        contract = release.STATIC_EXE_PATCH
        self.assertEqual(contract["delivery"], "one-time-local-installer")
        self.assertFalse(contract["per_session_component"])
        self.assertFalse(contract["process_memory_access"])
        self.assertEqual(contract["target"], "NOBU16PK.exe")
        self.assertEqual(contract["patch_site_count"], 5)
        self.assertEqual(contract["input_size"], 31_978_264)
        self.assertEqual(contract["unpacked_size"], 31_747_848)
        self.assertEqual(contract["output_size"], 31_747_848)
        self.assertEqual(
            contract["input_sha256"],
            "29BC1ED66D27B9AEF5EB6CE3D126BA2BDBF86099E12B09615FE9F988F41E2246",
        )
        self.assertEqual(
            contract["unpacked_sha256"],
            "BC885875A5E4288E5A1A424D99974F6F215777C03569C7EA707FDE63BDBC2B39",
        )
        self.assertEqual(
            contract["output_sha256"],
            "2E098ECB5E4335DC264F865306B990B724EA7C242B1B9F87FFC5EE2E7191797C",
        )

    def test_script_has_all_five_preimage_checked_patch_sites(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8-sig")
        self.assertIn("0x00BAF630", source)
        self.assertIn("0x00BAF640", source)
        self.assertIn("0x00BAF656", source)
        self.assertIn("0x00BAF667", source)
        self.assertIn("0x00BAF6C8", source)
        self.assertIn("0x0F,0x84,0xB4,0x01,0x00,0x00", source)
        self.assertIn("0x7E,0x0C", source)
        self.assertIn("0xEB,0x0C", source)
        self.assertIn("Assert-Bytes $patched $site.Offset $site.Before", source)
        self.assertIn("Set-PeChecksum", source)
        self.assertIn("[System.IO.File]::Replace", source)

    def test_installer_never_uses_runtime_process_memory_apis(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8-sig").casefold()
        for forbidden in (
            "openprocess",
            "writeprocessmemory",
            "virtualprotectex",
            "readprocessmemory",
            "debugactiveprocess",
            "suspendthread",
        ):
            self.assertNotIn(forbidden, source)
        self.assertFalse((ROOT / "tools" / "OfficerEditorMemoryPatch.cs").exists())
        self.assertFalse((ROOT / "tools" / "build_officer_editor_memory_patch.ps1").exists())

    def test_both_launchers_target_the_static_installer(self) -> None:
        apply = (ROOT / "release_payload" / "v0.11.1" / "APPLY_STATIC_OFFICER_EDITOR_FIX.bat").read_text(
            encoding="utf-8"
        )
        restore = (ROOT / "release_payload" / "v0.11.1" / "RESTORE_ORIGINAL_NOBU16PK_EXE.bat").read_text(
            encoding="utf-8"
        )
        self.assertIn("Invoke-StaticOfficerEditorFix.ps1", apply)
        self.assertNotIn("-Restore", apply)
        self.assertIn("Invoke-StaticOfficerEditorFix.ps1", restore)
        self.assertIn("-Restore", restore)
        self.assertIn('-GameRoot "%~dp0."', apply)
        self.assertIn('-GameRoot "%~dp0."', restore)
        self.assertNotIn('-GameRoot "%~dp0"', apply)
        self.assertNotIn('-GameRoot "%~dp0"', restore)

    def test_powershell_script_has_utf8_bom_and_readable_korean_errors(self) -> None:
        raw = SCRIPT.read_bytes()
        self.assertTrue(raw.startswith(b"\xef\xbb\xbf"))
        source = raw.decode("utf-8-sig")
        self.assertIn("실패", source)
        self.assertIn("파일이 없습니다", source)

    def test_minimal_steamless_dependency_set_is_pinned(self) -> None:
        self.assertEqual(release.STEAMLESS["version"], "v3.1.0.5")
        self.assertEqual(release.STEAMLESS["minimal_member_count"], 4)
        self.assertEqual(
            {
                path
                for path in release.SUPPORT_TARGETS
                if "/Steamless/" in path or path.endswith("Steamless.CLI.exe")
            },
            {
                "OfficerEditorStaticFix/Steamless/Steamless.CLI.exe",
                "OfficerEditorStaticFix/Steamless/Steamless.CLI.exe.config",
                "OfficerEditorStaticFix/Steamless/Plugins/Steamless.API.dll",
                "OfficerEditorStaticFix/Steamless/Plugins/Steamless.Unpacker.Variant31.x64.dll",
            },
        )


if __name__ == "__main__":
    unittest.main()
