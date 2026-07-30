from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "release_payload"
    / "v0.11.5"
    / "OfficerEditorStaticFix"
    / "Invoke-StaticOfficerEditorFix.ps1"
)


def load_release_module():
    path = ROOT / "tools" / "build_steam_jp_v0115_release.py"
    spec = importlib.util.spec_from_file_location("static_release_v0115", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


release = load_release_module()
upstream = release.load_module("static_release_v0115_helpers", release.UPSTREAM_PATH)


class StaticNameValidationInstallerV0115Tests(unittest.TestCase):
    def test_static_patch_contract_is_pinned(self) -> None:
        contract = release.STATIC_EXE_PATCH
        self.assertEqual(contract["delivery"], "one-time-local-installer")
        self.assertFalse(contract["per_session_component"])
        self.assertFalse(contract["process_memory_access"])
        self.assertEqual(contract["target"], "NOBU16PK.exe")
        self.assertEqual(contract["patch_site_count"], 9)
        self.assertEqual(contract["officer_editor_patch_site_count"], 5)
        self.assertEqual(contract["fictional_princess_patch_site_count"], 4)
        self.assertFalse(contract["shared_character_validators_modified"])
        self.assertTrue(contract["supports_previous_output_upgrade"])
        self.assertEqual(
            contract["previous_output_sha256"],
            "2E098ECB5E4335DC264F865306B990B724EA7C242B1B9F87FFC5EE2E7191797C",
        )
        self.assertEqual(
            contract["output_sha256"],
            "7CA2F1D59E02650C67F343F0776F6D05517C0486B65168E63A9AE4CBCAAFDBB2",
        )

    def test_script_has_all_nine_preimage_checked_patch_sites(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8-sig")
        for offset in (
            "0x00BAF630",
            "0x00BAF640",
            "0x00BAF656",
            "0x00BAF667",
            "0x00BAF6C8",
            "0x00EB3BBF",
            "0x00EB3BE0",
            "0x00EB3C4F",
            "0x00EB3C78",
        ):
            self.assertIn(offset, source)
        for princess_preimage in (
            "0xE8,0x4C,0x6E,0xCE,0xFF",
            "0xE8,0xCB,0x6E,0xCE,0xFF",
            "0xE8,0xBC,0x6D,0xCE,0xFF",
            "0xE8,0x33,0x6E,0xCE,0xFF",
        ):
            self.assertIn(princess_preimage, source)
        self.assertEqual(source.count("0xB8,0x01,0x00,0x00,0x00"), 4)
        self.assertIn("Assert-Bytes $patched $site.Offset $site.Before", source)
        self.assertIn("Assert-Bytes $patched $site.Offset $site.After", source)
        self.assertIn("Set-PeChecksum", source)
        self.assertIn("[System.IO.File]::Replace", source)

    def test_previous_patch_has_a_guarded_upgrade_path(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8-sig")
        self.assertIn("$PreviousPatchedSha256", source)
        self.assertIn("$isPreviousPatch", source)
        self.assertIn("foreach ($site in $OfficerEditorPatchSites)", source)
        self.assertIn("foreach ($site in $PrincessPatchSites)", source)
        self.assertIn("기존 무장 에디트 패치에서 업그레이드", source)

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

    def test_script_has_utf8_bom_and_payload_is_hash_pinned(self) -> None:
        self.assertTrue(SCRIPT.read_bytes().startswith(b"\xef\xbb\xbf"))
        for relative, (size, digest) in release.SUPPORT_TARGETS.items():
            path = release.DEFAULT_PAYLOAD_ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(path.stat().st_size, size, relative)
            self.assertEqual(upstream.sha256_file(path), digest)


if __name__ == "__main__":
    unittest.main()
