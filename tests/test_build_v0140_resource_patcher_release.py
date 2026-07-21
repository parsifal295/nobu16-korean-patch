from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


release = load_module(
    "v0140_resource_patcher_release_test", "tools/build_v0140_resource_patcher_release.py"
)


class V0140ResourcePatcherReleaseTests(unittest.TestCase):
    def test_payload_member_set_is_exact(self) -> None:
        members = release.read_support_payload(release.DEFAULT_PAYLOAD_ROOT)
        self.assertEqual(set(members), set(release.SUPPORT_MEMBERS))
        self.assertEqual(len(members), 23)
        self.assertIn("APPLY_KOREAN_PATCH.bat", members)
        self.assertIn("RESTORE_KOREAN_PATCH.bat", members)
        self.assertIn("Invoke-Nobu16KoreanPatch.ps1", members)
        self.assertIn("PATCHER_README_KO.txt", members)
        self.assertNotIn("APPLY_KOREAN_RESOURCE_PATCH.bat", members)
        self.assertNotIn("APPLY_STATIC_EXE_PATCHES.bat", members)

    def test_archive_rejects_game_resources_and_game_executable(self) -> None:
        for bad_member in ("MSG/JP/msggame.bin", "RES_JP/res_lang.bin", "NOBU16PK.exe"):
            with self.subTest(bad_member=bad_member):
                with self.assertRaises(RuntimeError):
                    release.reject_game_content({bad_member: b"not distributable"})
        release.reject_game_content({"patches/binary/RES_JP__res_lang.bin.bsdiff": b"delta"})

    def test_manifest_declares_pristine_direct_distribution(self) -> None:
        ledger = {
            "source_profile": {
                "kind": "steam-jp-1.1.7-pristine",
                "resource_count": len(release.PATCHER.RESOURCE_PATHS),
            },
            "operation_counts": dict(release.PATCHER.EXPECTED_OPERATION_COUNTS),
            "payload_policy": {
                "contains_complete_game_resources": False,
                "contains_game_executable": False,
                "process_memory_access": False,
                "requires_installed_pristine_resources": True,
                "pristine_full_resources_stored": False,
                "opaque_target_records_may_include_context": True,
                "binary_delta_format": release.PATCHER.BINARY_PATCH_FORMAT,
                "binary_delta_resource_count": len(release.PATCHER.BINARY_RESOURCE_PATHS),
            },
        }
        manifest = release.manifest_for({"readme.txt": b"fixture"}, ledger)
        self.assertEqual(manifest["distribution"]["complete_game_resource_count"], 0)
        self.assertEqual(manifest["distribution"]["game_executable_count"], 0)
        self.assertEqual(
            manifest["distribution"]["kind"],
            "pristine-steam-jp-1.1.7-to-v0.14.0-direct-unified-patcher",
        )
        self.assertEqual(manifest["resource_patcher"]["full_preflight_resource_count"], 15)
        self.assertEqual(manifest["resource_patcher"]["binary_delta_resource_count"], 5)
        self.assertTrue(manifest["static_installer"]["integrated_into_unified_patcher"])
        self.assertEqual(
            manifest["unified_patcher"]["apply_order"], ["static_exe", "resources"]
        )
        self.assertEqual(
            manifest["unified_patcher"]["restore_order"], ["resources", "static_exe"]
        )


if __name__ == "__main__":
    unittest.main()
