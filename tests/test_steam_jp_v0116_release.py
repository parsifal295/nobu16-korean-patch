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


release = load_module("steam_jp_v0116_release", "tools/build_steam_jp_v0116_release.py")
previous_release = load_module(
    "steam_jp_v0115_release_for_v0116_test",
    "tools/build_steam_jp_v0115_release.py",
)
upstream = release.load_module("steam_jp_v0112_test_helpers", release.UPSTREAM_PATH)


class SteamJpV0116ReleaseTests(unittest.TestCase):
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

    def test_release_updates_six_text_resources_and_static_installer(self) -> None:
        self.assertEqual(release.VERSION, "v0.11.6")
        self.assertIn("v0.11.6", release.ZIP_NAME)
        self.assertIn("v0.11.6", release.MANIFEST_NAME)
        self.assertTrue(release.SCHEMA.endswith("v0.11.6"))
        self.assertEqual(len(release.GAME_TARGETS), 15)
        changed = {
            relative
            for relative, target in release.GAME_TARGETS.items()
            if target != previous_release.GAME_TARGETS[relative]
        }
        self.assertEqual(
            changed,
            {
                "MSG/JP/ev_strdata.bin",
                "MSG/JP/msggame.bin",
                "MSG/JP/strdata.bin",
                "MSG_PK/JP/msgdata.bin",
                "MSG_PK/JP/msgev.bin",
                "MSG_PK/JP/msggame.bin",
            },
        )
        changed_support = {
            relative
            for relative, target in release.SUPPORT_TARGETS.items()
            if target != previous_release.SUPPORT_TARGETS[relative]
        }
        self.assertEqual(
            changed_support,
            {
                "OfficerEditorStaticFix/Invoke-StaticOfficerEditorFix.ps1",
                "STATIC_OFFICER_EDITOR_FIX_README_KO.txt",
            },
        )

        contract = release.STATIC_EXE_PATCH
        self.assertEqual(contract["patch_site_count"], 21)
        self.assertEqual(contract["officer_editor_patch_site_count"], 5)
        self.assertEqual(contract["fictional_princess_patch_site_count"], 4)
        self.assertEqual(contract["header_layout_patch_site_count"], 12)
        self.assertTrue(contract["supports_officer_only_output_upgrade"])
        self.assertTrue(contract["supports_previous_output_upgrade"])
        self.assertEqual(
            contract["officer_only_output_sha256"],
            "2E098ECB5E4335DC264F865306B990B724EA7C242B1B9F87FFC5EE2E7191797C",
        )
        self.assertEqual(
            contract["previous_output_sha256"],
            "7CA2F1D59E02650C67F343F0776F6D05517C0486B65168E63A9AE4CBCAAFDBB2",
        )
        self.assertEqual(
            contract["output_sha256"],
            "FD7F07A29DBD76E4AB18B1D1EE85D6B1677E0A4827A79E3732075D4CACBA8BB6",
        )
        self.assertFalse(contract["resource_archives_modified"])
        self.assertEqual(contract["validated_resolution"], "2048x1152")
        self.assertTrue(contract["validated_after_full_process_restart"])

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
            second_manifest = release.build(
                game_root,
                second,
                payload_root,
                game_targets=game_targets,
                support_targets=support_targets,
            )
            self.assertEqual(first_manifest["release_zip"], second_manifest["release_zip"])
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


if __name__ == "__main__":
    unittest.main()
