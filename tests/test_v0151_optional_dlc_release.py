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


patcher = load_module("v0151_optional_dlc_patcher_test", "tools/v0151_resource_patcher.py")
release = load_module(
    "v0151_optional_dlc_release_test", "tools/build_v0151_resource_patcher_release.py"
)


class V0151OptionalDlcReleaseTests(unittest.TestCase):
    def test_profile_has_sixteen_mandatory_and_105_optional_resources(self) -> None:
        self.assertEqual(len(patcher.RESOURCE_PATHS), 121)
        self.assertEqual(len(patcher.TEXT_RESOURCE_PATHS), 10)
        self.assertEqual(len(patcher.BINARY_RESOURCE_PATHS), 111)
        self.assertEqual(len(patcher.MANDATORY_RESOURCE_PATHS), 16)
        self.assertEqual(len(patcher.OPTIONAL_RESOURCE_PATHS), 105)
        self.assertTrue(
            all(path.startswith(("DLC/JP/", "DLC_PK/JP/")) for path in patcher.OPTIONAL_RESOURCE_PATHS)
        )

    def test_missing_dlc_and_later_installed_dlc_are_valid_apply_states(self) -> None:
        pristine = {
            path: ("missing_optional" if path in patcher.OPTIONAL_RESOURCE_PATHS else "predecessor")
            for path in patcher.RESOURCE_PATHS
        }
        self.assertEqual(
            set(patcher.pending_apply_paths(pristine)), set(patcher.MANDATORY_RESOURCE_PATHS)
        )
        installed = {
            path: ("missing_optional" if path in patcher.OPTIONAL_RESOURCE_PATHS else "target")
            for path in patcher.RESOURCE_PATHS
        }
        self.assertEqual(patcher.pending_apply_paths(installed), ())
        added_dlc = sorted(patcher.OPTIONAL_RESOURCE_PATHS)[0]
        installed[added_dlc] = "predecessor"
        self.assertEqual(patcher.pending_apply_paths(installed), (added_dlc,))

    def test_unknown_or_mixed_mandatory_resources_fail_closed(self) -> None:
        state = {path: "target" for path in patcher.RESOURCE_PATHS}
        state[patcher.MANDATORY_RESOURCE_PATHS[0]] = "unknown"
        with self.assertRaises(patcher.PatcherError):
            patcher.pending_apply_paths(state)
        state[patcher.MANDATORY_RESOURCE_PATHS[0]] = "predecessor"
        with self.assertRaises(patcher.PatcherError):
            patcher.pending_apply_paths(state)

    def test_release_manifest_declares_optional_dlc_policy(self) -> None:
        ledger = {
            "source_profile": {"kind": "steam-jp-1.1.7-pristine", "resource_count": 121},
            "operation_counts": dict(patcher.EXPECTED_OPERATION_COUNTS),
            "payload_policy": {
                "contains_complete_game_resources": False,
                "contains_game_executable": False,
                "process_memory_access": False,
                "requires_installed_pristine_resources": True,
                "pristine_full_resources_stored": False,
                "opaque_target_records_may_include_context": True,
                "binary_delta_format": patcher.BINARY_PATCH_FORMAT,
                "binary_delta_resource_count": 111,
            },
        }
        manifest = release.manifest_for({"fixture.txt": b"fixture"}, ledger)
        self.assertEqual(manifest["resource_patcher"]["optional_dlc_resource_count"], 105)
        self.assertIn("skip", manifest["unified_patcher"]["missing_dlc_policy"])
        self.assertEqual(
            manifest["distribution"]["kind"],
            "pristine-steam-jp-1.1.7-to-v0.15.1-direct-unified-patcher",
        )

    def test_payload_member_set_and_game_content_rejection(self) -> None:
        members = release.read_support_payload(release.DEFAULT_PAYLOAD_ROOT)
        self.assertIn(release.PROFILE_MEMBER, members)
        for bad in ("DLC/JP/evm_001.n16", "DLC_PK/JP/evm_001.n16"):
            with self.assertRaises(RuntimeError):
                release.reject_game_content({bad: b"game content"})


if __name__ == "__main__":
    unittest.main()
