from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "release_payload"
    / "v0.11.6"
    / "OfficerEditorStaticFix"
    / "Invoke-StaticOfficerEditorFix.ps1"
)
README = ROOT / "release_payload" / "v0.11.6" / "STATIC_OFFICER_EDITOR_FIX_README_KO.txt"


def load_release_module():
    path = ROOT / "tools" / "build_steam_jp_v0116_release.py"
    spec = importlib.util.spec_from_file_location("static_release_v0116", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


release = load_release_module()
upstream = release.load_module("static_release_v0116_helpers", release.UPSTREAM_PATH)


class StaticHeaderLayoutInstallerV0116Tests(unittest.TestCase):
    def test_static_patch_contract_is_pinned(self) -> None:
        contract = release.STATIC_EXE_PATCH
        self.assertEqual(contract["delivery"], "one-time-local-installer")
        self.assertFalse(contract["per_session_component"])
        self.assertFalse(contract["process_memory_access"])
        self.assertEqual(contract["target"], "NOBU16PK.exe")
        self.assertEqual(contract["patch_site_count"], 21)
        self.assertEqual(contract["officer_editor_patch_site_count"], 5)
        self.assertEqual(contract["fictional_princess_patch_site_count"], 4)
        self.assertEqual(contract["header_layout_patch_site_count"], 12)
        self.assertEqual(
            contract["header_layout_reference"],
            "native-north-american-horizontal-geometry",
        )
        self.assertFalse(contract["resource_archives_modified"])
        self.assertEqual(contract["validated_resolution"], "2048x1152")
        self.assertTrue(contract["validated_after_full_process_restart"])
        self.assertEqual(
            contract["previous_output_sha256"],
            "7CA2F1D59E02650C67F343F0776F6D05517C0486B65168E63A9AE4CBCAAFDBB2",
        )
        self.assertEqual(
            contract["output_sha256"],
            "FD7F07A29DBD76E4AB18B1D1EE85D6B1677E0A4827A79E3732075D4CACBA8BB6",
        )

    def test_script_has_all_twelve_preimage_checked_header_sites(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8-sig")
        for offset in (
            "0x01CA7B08",
            "0x01CA7C68",
            "0x01CA7C70",
            "0x01CA7C80",
            "0x01CA7C90",
            "0x01CA7CA0",
            "0x01CA7CA8",
            "0x01CA7CB0",
            "0x01CA7CC0",
            "0x01CA7CC8",
            "0x01CA7D00",
            "0x01CA7D10",
        ):
            self.assertIn(offset, source)
        self.assertIn("$HeaderLayoutPatchSites", source)
        self.assertIn(
            "$PatchSites = @($OfficerEditorPatchSites) + @($PrincessPatchSites) + @($HeaderLayoutPatchSites)",
            source,
        )
        self.assertIn("Assert-Bytes $patched $site.Offset $site.Before", source)
        self.assertIn("Assert-Bytes $patched $site.Offset $site.After", source)
        self.assertIn("Set-PeChecksum", source)
        self.assertIn("[System.IO.File]::Replace", source)

    def test_both_prior_outputs_have_guarded_upgrade_paths(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8-sig")
        self.assertIn("$OfficerOnlyPatchedSha256", source)
        self.assertIn("$PreviousPatchedSha256", source)
        self.assertIn("$isOfficerOnlyPatch", source)
        self.assertIn("$isPreviousPatch", source)
        self.assertIn("foreach ($site in $OfficerEditorPatchSites)", source)
        self.assertIn("foreach ($site in $PrincessPatchSites)", source)
        self.assertIn("foreach ($site in $HeaderLayoutPatchSites)", source)

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

    def test_payload_is_bom_safe_hash_pinned_and_documents_real_qa(self) -> None:
        self.assertTrue(SCRIPT.read_bytes().startswith(b"\xef\xbb\xbf"))
        for relative, (size, digest) in release.SUPPORT_TARGETS.items():
            path = release.DEFAULT_PAYLOAD_ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(path.stat().st_size, size, relative)
            self.assertEqual(upstream.sha256_file(path), digest, relative)
        readme = README.read_text(encoding="utf-8-sig")
        self.assertIn("2048x1152", readme)
        self.assertIn("완전 종료 후 재실행", readme)
        self.assertIn(release.STATIC_EXE_PATCH["output_sha256"], readme)


if __name__ == "__main__":
    unittest.main()
