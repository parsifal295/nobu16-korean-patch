from __future__ import annotations

import importlib.util
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "release_payload" / "v0.11.6"
MASTER = PAYLOAD / "OfficerEditorStaticFix" / "Invoke-Nobu16StaticPatches.ps1"
WRAPPER = PAYLOAD / "OfficerEditorStaticFix" / "Invoke-StaticOfficerEditorFix.ps1"
PATCH_ROOT = PAYLOAD / "OfficerEditorStaticFix" / "Patches"
PATCH_REGISTRY = PAYLOAD / "OfficerEditorStaticFix" / "000-PatchRegistry.psd1"
README = PAYLOAD / "STATIC_OFFICER_EDITOR_FIX_README_KO.txt"
PATCH_FILES = (
    "001-OfficerEditorNameValidation.psd1",
    "002-FictionalPrincessNameValidation.psd1",
    "003-TopHeaderLayout.psd1",
)


def load_release_module():
    path = ROOT / "tools" / "build_steam_jp_v0116_release.py"
    spec = importlib.util.spec_from_file_location("static_release_v0116", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


release = load_release_module()
upstream = release.load_configured_upstream("static_release_v0116_helpers")


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
        self.assertEqual(contract["registered_patch_count"], 3)
        self.assertEqual(
            contract["installer_architecture"], "data-driven-master-registry"
        )
        self.assertTrue(contract["supports_per_patch_state_detection"])
        self.assertTrue(contract["supports_registered_patch_combinations"])
        self.assertEqual(contract["partial_patch_policy"], "fail-closed")
        self.assertEqual(
            contract["patch_registry_manifest"],
            "OfficerEditorStaticFix/000-PatchRegistry.psd1",
        )
        self.assertFalse(contract["resource_archives_modified"])
        self.assertEqual(contract["validated_resolution"], "2048x1152")
        self.assertTrue(contract["validated_after_full_process_restart"])
        self.assertEqual(
            contract["output_sha256"],
            "FD7F07A29DBD76E4AB18B1D1EE85D6B1677E0A4827A79E3732075D4CACBA8BB6",
        )

    def test_three_data_files_own_all_twenty_one_nonoverlapping_sites(self) -> None:
        self.assertEqual(
            tuple(path.name for path in sorted(PATCH_ROOT.glob("*.psd1"))),
            PATCH_FILES,
        )
        expected_offsets = (
            (0x00BAF630, 0x00BAF640, 0x00BAF656, 0x00BAF667, 0x00BAF6C8),
            (0x00EB3BBF, 0x00EB3BE0, 0x00EB3C4F, 0x00EB3C78),
            (
                0x01CA7B08,
                0x01CA7C68,
                0x01CA7C70,
                0x01CA7C80,
                0x01CA7C90,
                0x01CA7CA0,
                0x01CA7CA8,
                0x01CA7CB0,
                0x01CA7CC0,
                0x01CA7CC8,
                0x01CA7D00,
                0x01CA7D10,
            ),
        )
        all_offsets: list[int] = []
        for name, expected in zip(PATCH_FILES, expected_offsets, strict=True):
            source = (PATCH_ROOT / name).read_text(encoding="ascii")
            offsets = tuple(
                int(value, 16)
                for value in re.findall(r"Offset\s*=\s*(0x[0-9A-Fa-f]+)", source)
            )
            self.assertEqual(offsets, expected)
            self.assertEqual(source.count("Before = '"), len(expected))
            self.assertEqual(source.count("After = '"), len(expected))
            all_offsets.extend(offsets)
        self.assertEqual(len(all_offsets), 21)
        self.assertEqual(len(set(all_offsets)), 21)

    def test_master_discovers_registry_and_applies_only_pending_items(self) -> None:
        source = MASTER.read_text(encoding="ascii")
        self.assertIn("000-PatchRegistry.psd1", source)
        self.assertIn("Get-ChildItem -LiteralPath $patchRoot -Filter '*.psd1'", source)
        self.assertIn("Import-PowerShellDataFile", source)
        self.assertIn("Sort-Object Name", source)
        self.assertIn("function Get-PatchState", source)
        self.assertIn("return 'Applied'", source)
        self.assertIn("return 'Pending'", source)
        self.assertIn("is partially applied; refusing an unsafe repair", source)
        self.assertIn("if ($state -eq 'Applied')", source)
        self.assertIn("$pending += $patch", source)
        self.assertIn("foreach ($patch in $pending)", source)
        self.assertIn("function Assert-NormalizedBase", source)
        self.assertIn("EXE differs outside registered patch sites", source)
        self.assertIn("Patch definition set differs from 000-PatchRegistry.psd1", source)
        self.assertIn("Registered all-applied output hash mismatch", source)
        self.assertIn("Set-PeChecksum", source)
        self.assertIn("[System.IO.File]::Replace", source)

    def test_legacy_wrapper_and_both_apply_bats_delegate_to_master(self) -> None:
        wrapper = WRAPPER.read_text(encoding="ascii")
        self.assertIn("Invoke-Nobu16StaticPatches.ps1", wrapper)
        self.assertIn("@PSBoundParameters", wrapper)
        for name in (
            "APPLY_STATIC_EXE_PATCHES.bat",
            "APPLY_STATIC_OFFICER_EDITOR_FIX.bat",
            "RESTORE_ORIGINAL_NOBU16PK_EXE.bat",
        ):
            source = (PAYLOAD / name).read_text(encoding="ascii")
            self.assertIn("Invoke-Nobu16StaticPatches.ps1", source)

    def test_installer_never_uses_runtime_process_memory_apis(self) -> None:
        source = (MASTER.read_text(encoding="ascii") + WRAPPER.read_text(encoding="ascii")).casefold()
        for forbidden in (
            "openprocess",
            "writeprocessmemory",
            "virtualprotectex",
            "readprocessmemory",
            "debugactiveprocess",
            "suspendthread",
        ):
            self.assertNotIn(forbidden, source)

    def test_payload_is_hash_pinned_and_documents_registry_and_real_qa(self) -> None:
        self.assertEqual(len(release.SUPPORT_TARGETS), 15)
        for relative, (size, digest) in release.SUPPORT_TARGETS.items():
            path = release.DEFAULT_PAYLOAD_ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(path.stat().st_size, size, relative)
            self.assertEqual(upstream.sha256_file(path), digest, relative)
        readme = README.read_text(encoding="utf-8")
        self.assertIn("패치 레지스트리 기반 마스터", readme)
        self.assertIn("001: 무장 에디트", readme)
        self.assertIn("002: 가공 히메", readme)
        self.assertIn("003: 한국어 상단 헤더", readme)
        self.assertIn("Applied 또는 Pending", readme)
        self.assertIn("2048x1152", readme)
        self.assertIn("완전 종료 후 재실행", readme)
        self.assertIn(release.STATIC_EXE_PATCH["output_sha256"], readme)
        registry = PATCH_REGISTRY.read_text(encoding="ascii")
        self.assertIn("nobu16.static-exe-patch-registry.v1", registry)
        self.assertIn(release.STATIC_EXE_PATCH["output_sha256"], registry)
        for name in PATCH_FILES:
            self.assertIn(f"Patches/{name}", registry)


if __name__ == "__main__":
    unittest.main()
