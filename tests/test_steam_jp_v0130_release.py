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


release = load_module("steam_jp_v0130_release", "tools/build_steam_jp_v0130_release.py")
previous_release = load_module(
    "steam_jp_v0120_release_for_v0130_test",
    "tools/build_steam_jp_v0120_release.py",
)
upstream = release.load_configured_upstream("steam_jp_v0130_test_helpers")


class SteamJpV0130ReleaseTests(unittest.TestCase):
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
        self.assertEqual(release.VERSION, "v0.13.0")
        self.assertIn("v0.13.0", release.ZIP_NAME)
        self.assertIn("v0.13.0", release.MANIFEST_NAME)
        self.assertTrue(release.SCHEMA.endswith("v0.13.0"))

        changed_game = {
            relative
            for relative, target in release.GAME_TARGETS.items()
            if target != previous_release.GAME_TARGETS.get(relative)
        }
        self.assertEqual(
            changed_game,
            {
                "MSG/JP/ev_strdata.bin",
                "MSG/JP/msggame.bin",
                "MSG_PK/JP/msgev.bin",
                "MSG_PK/JP/msggame.bin",
            },
        )
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
                "OfficerEditorStaticFix/Patches/005-DualResolutionAndHorizontalLandmarks.psd1",
                "OfficerEditorStaticFix/Patches/Payloads/005-DualResolutionAndHorizontalLandmarks.append.gz",
            },
        )

        contract = release.STATIC_EXE_PATCH
        self.assertEqual(contract["registered_patch_count"], 5)
        self.assertEqual(contract["patch_site_count"], 197)
        self.assertEqual(contract["patch_005_site_count"], 48)
        self.assertEqual(contract["landmark_owner_patch_site_count"], 11)
        self.assertEqual(contract["patch_005_append_size"], 28_032_512)
        self.assertEqual(contract["output_size"], 67_024_384)
        self.assertTrue(contract["supports_chained_append_overlays"])
        self.assertTrue(contract["supports_previous_output_upgrade"])
        self.assertEqual(contract["installer_architecture"], "data-driven-master-registry-v3")
        self.assertEqual(
            contract["previous_output_sha256"],
            "A430615A2D6EAD81B0B50DB6D9055FB77BD3E6CC7EEEAE7F145D203960B5C98E",
        )
        self.assertEqual(
            contract["output_sha256"],
            "BE983A61C81008289E2483D552122C0BE3299B5F8DD4A557FA14DA2663AC7BD6",
        )
        self.assertTrue(contract["validated_after_full_process_restart"])
        self.assertFalse(contract["resource_archives_modified"])

        quality = release.TRANSLATION_QUALITY
        self.assertEqual(quality["event_count"], 26)
        self.assertEqual(quality["dialogue_count"], 51)
        self.assertEqual(quality["changed_resource_count"], 4)

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
                self.assertNotIn("NOBU16PK.exe", archive.namelist())
            saved = json.loads(
                (first / release.MANIFEST_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual(saved, first_manifest)
            self.assertEqual(saved["static_exe_patch"], release.STATIC_EXE_PATCH)
            self.assertEqual(saved["translation_quality"], release.TRANSLATION_QUALITY)


if __name__ == "__main__":
    unittest.main()
