from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


release = load_module("steam_jp_v0131_release", "tools/build_steam_jp_v0131_release.py")
previous_release = load_module(
    "steam_jp_v0130_release_for_v0131_test",
    "tools/build_steam_jp_v0130_release.py",
)
upstream = release.load_configured_upstream("steam_jp_v0131_test_helpers")


class SteamJpV0131ReleaseTests(unittest.TestCase):
    def make_fixture(
        self, root: Path
    ) -> tuple[Path, Path, dict[str, tuple[int, str]], dict[str, tuple[int, str]]]:
        game_root = root / "game"
        payload_root = root / "payload"
        game_targets: dict[str, tuple[int, str]] = {}
        support_targets: dict[str, tuple[int, str]] = {}
        for relative in release.GAME_TARGETS:
            path = game_root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = f"fixture game resource: {relative}\n".encode()
            path.write_bytes(payload)
            game_targets[relative] = (len(payload), upstream.sha256_bytes(payload))
        for relative in release.SUPPORT_TARGETS:
            path = payload_root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = f"fixture support resource: {relative}\n".encode()
            path.write_bytes(payload)
            support_targets[relative] = (len(payload), upstream.sha256_bytes(payload))
        return game_root, payload_root, game_targets, support_targets

    def test_release_scope_and_static_patch_contract(self) -> None:
        self.assertEqual(release.VERSION, "v0.13.1")
        self.assertIn("v0.13.1", release.ZIP_NAME)
        self.assertIn("v0.13.1", release.MANIFEST_NAME)
        self.assertTrue(release.SCHEMA.endswith("v0.13.1"))
        self.assertEqual(release.GAME_TARGETS, previous_release.GAME_TARGETS)

        changed_support = {
            relative
            for relative, target in release.SUPPORT_TARGETS.items()
            if target != previous_release.SUPPORT_TARGETS.get(relative)
        }
        self.assertEqual(
            changed_support,
            {
                "STATIC_OFFICER_EDITOR_FIX_README_KO.txt",
                "OfficerEditorStaticFix/Invoke-Nobu16StaticPatches.ps1",
                "OfficerEditorStaticFix/000-PatchRegistry.psd1",
                "OfficerEditorStaticFix/Patches/006-HorizontalMapStatusIcons.psd1",
            },
        )

        contract = release.STATIC_EXE_PATCH
        self.assertEqual(contract["registered_patch_count"], 6)
        self.assertEqual(contract["patch_site_count"], 201)
        self.assertEqual(contract["patch_006_site_count"], 4)
        self.assertEqual(contract["patch_006_injected_code_size"], 162)
        self.assertEqual(contract["patch_006_changed_byte_count"], 150)
        self.assertEqual(contract["output_size"], 67_024_384)
        self.assertEqual(
            contract["previous_output_sha256"],
            "BE983A61C81008289E2483D552122C0BE3299B5F8DD4A557FA14DA2663AC7BD6",
        )
        self.assertEqual(
            contract["output_sha256"],
            "3548AD5B71168296DD03851B1F9613CAD1C325AF2AB916A11CC140DC61FA0E43",
        )
        self.assertTrue(contract["supports_all_registered_prefix_states"])
        self.assertTrue(contract["validated_after_full_process_restart"])
        self.assertFalse(contract["resource_archives_modified"])

        alignment = release.ISSUE_72_ALIGNMENT
        self.assertEqual(alignment["issue"], 72)
        self.assertIsNone(alignment["fixed_offset"])
        self.assertTrue(alignment["troop_count_group_preserved"])
        self.assertNotIn("supply_marker_included", alignment)
        self.assertEqual(alignment["validated_resolution"], "1920x1080")
        self.assertTrue(alignment["validated_after_full_process_restart"])

    def test_repository_support_payload_matches_exact_pins(self) -> None:
        upstream.validate_payload_directory(
            release.DEFAULT_PAYLOAD_ROOT, release.SUPPORT_TARGETS
        )
        for relative, (size, digest) in release.SUPPORT_TARGETS.items():
            path = release.DEFAULT_PAYLOAD_ROOT / relative
            self.assertEqual(path.stat().st_size, size, relative)
            self.assertEqual(upstream.sha256_file(path), digest, relative)

    def test_fixture_build_is_deterministic_and_excludes_game_exe(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            game_root, payload_root, game_targets, support_targets = self.make_fixture(root)
            first = root / "first"
            second = root / "second"
            first_manifest = release.build(
                game_root,
                first,
                payload_root,
                game_targets=game_targets,
                support_targets=support_targets,
            )
            release.build(
                game_root,
                second,
                payload_root,
                game_targets=game_targets,
                support_targets=support_targets,
            )
            self.assertEqual(
                (first / release.ZIP_NAME).read_bytes(),
                (second / release.ZIP_NAME).read_bytes(),
            )
            with zipfile.ZipFile(first / release.ZIP_NAME) as archive:
                self.assertEqual(len(archive.namelist()), 35)
                self.assertNotIn("NOBU16PK.exe", archive.namelist())
            saved = json.loads(
                (first / release.MANIFEST_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual(saved, first_manifest)
            self.assertEqual(saved["static_exe_patch"], release.STATIC_EXE_PATCH)
            self.assertEqual(saved["issue_72_alignment"], release.ISSUE_72_ALIGNMENT)


if __name__ == "__main__":
    unittest.main()
