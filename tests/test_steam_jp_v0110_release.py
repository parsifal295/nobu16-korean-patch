from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_MANIFEST = ROOT / "data" / "public" / "steam_jp_117_v0110_release.v1.json"


def load_module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


release = load_module(
    "steam_jp_v0110_release", "tools/build_steam_jp_v0110_release.py"
)
previous_release = load_module(
    "steam_jp_v0102_release_for_v0110_test",
    "tools/build_steam_jp_v0102_release.py",
)


class SteamJpV0110ReleaseTests(unittest.TestCase):
    def make_fixture(
        self, root: Path
    ) -> tuple[Path, Path, dict[str, tuple[int, str]], dict[str, tuple[int, str]]]:
        game_root = root / "game"
        payload_root = root / "payload"
        game_targets: dict[str, tuple[int, str]] = {}
        support_targets: dict[str, tuple[int, str]] = {}

        for relative in release.GAME_TARGETS:
            path = game_root / Path(relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = f"fixture game resource: {relative}\n".encode()
            path.write_bytes(payload)
            game_targets[relative] = (len(payload), release.sha256_bytes(payload))

        for relative in release.EXPECTED_SUPPORT_MEMBERS:
            path = payload_root / Path(relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = f"fixture static installer support: {relative}\n".encode()
            path.write_bytes(payload)
            support_targets[relative] = (len(payload), release.sha256_bytes(payload))

        return game_root, payload_root, game_targets, support_targets

    def test_version_and_release_names_are_v0110(self) -> None:
        self.assertEqual(release.VERSION, "v0.11.0")
        self.assertIn("v0.11.0", release.ZIP_NAME)
        self.assertIn("v0.11.0", release.MANIFEST_NAME)
        self.assertTrue(release.SCHEMA.endswith("v0.11.0"))

    def test_public_manifest_matches_the_release_builder_contract(self) -> None:
        manifest = json.loads(PUBLIC_MANIFEST.read_text(encoding="utf-8"))
        expected_members = {
            path: {"size": size, "sha256": sha256}
            for path, (size, sha256) in sorted(
                {**release.GAME_TARGETS, **release.SUPPORT_TARGETS}.items()
            )
        }
        self.assertEqual(manifest["schema"], release.SCHEMA)
        self.assertEqual(manifest["version"], release.VERSION)
        self.assertEqual(manifest["member_count"], 24)
        self.assertEqual(manifest["game_resource_count"], 15)
        self.assertEqual(manifest["support_file_count"], 9)
        self.assertEqual(manifest["members"], expected_members)
        self.assertEqual(manifest["static_exe_patch"], release.STATIC_EXE_PATCH)
        self.assertEqual(manifest["third_party"]["steamless"], release.STEAMLESS)
        self.assertEqual(
            manifest["release_zip"],
            {
                "name": release.ZIP_NAME,
                "size": 374_143_486,
                "sha256": "3D0382BCD199C19031442CE6C070E0627A455FD43937BADEFC70F797BC2FC5BB",
            },
        )
        self.assertTrue(manifest["qa"]["static_installer_workspace_roundtrip"])
        self.assertTrue(manifest["qa"]["officer_edit_saved"])

    def test_the_fifteen_game_resource_pins_are_unchanged_from_v0102(self) -> None:
        self.assertEqual(len(release.GAME_TARGETS), 15)
        self.assertEqual(release.GAME_TARGETS, previous_release.TARGETS)

    def test_static_support_allowlist_is_exact_and_excludes_the_game_executable(self) -> None:
        self.assertEqual(
            tuple(sorted(release.SUPPORT_TARGETS)),
            tuple(sorted(release.EXPECTED_SUPPORT_MEMBERS)),
        )
        self.assertEqual(len(release.EXPECTED_SUPPORT_MEMBERS), 9)
        self.assertEqual(
            {path for path in release.EXPECTED_SUPPORT_MEMBERS if path.endswith(".exe")},
            {"OfficerEditorStaticFix/Steamless/Steamless.CLI.exe"},
        )
        self.assertEqual(
            {path for path in release.EXPECTED_SUPPORT_MEMBERS if path.endswith(".dll")},
            {
                "OfficerEditorStaticFix/Steamless/Plugins/Steamless.API.dll",
                "OfficerEditorStaticFix/Steamless/Plugins/Steamless.Unpacker.Variant31.x64.dll",
            },
        )
        for relative in (*release.GAME_TARGETS, *release.SUPPORT_TARGETS):
            lowered = relative.casefold()
            self.assertNotEqual(Path(relative).name.casefold(), "nobu16pk.exe")
            self.assertNotIn("workstreams", Path(lowered).parts)
            self.assertNotIn("tmp", Path(lowered).parts)

    def test_all_release_pins_are_canonical(self) -> None:
        for relative, (size, sha256) in {
            **release.GAME_TARGETS,
            **release.SUPPORT_TARGETS,
        }.items():
            self.assertEqual(relative, Path(relative).as_posix())
            self.assertNotIn("..", Path(relative).parts)
            self.assertGreater(size, 0)
            self.assertEqual(len(sha256), 64)
            self.assertEqual(sha256, sha256.upper())
            int(sha256, 16)

    def test_repository_support_payload_matches_its_exact_pins(self) -> None:
        for relative, (expected_size, expected_hash) in release.SUPPORT_TARGETS.items():
            path = release.DEFAULT_PAYLOAD_ROOT / relative
            self.assertTrue(path.is_file(), relative)
            self.assertEqual(path.stat().st_size, expected_size, relative)
            self.assertEqual(release.sha256_file(path), expected_hash, relative)

    def test_fixture_build_is_deterministic_and_contains_only_allowlisted_members(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            game_root, payload_root, game_targets, support_targets = self.make_fixture(root)
            first_output = root / "first"
            second_output = root / "second"

            first_manifest = release.build(
                game_root,
                first_output,
                payload_root,
                game_targets=game_targets,
                support_targets=support_targets,
            )
            second_manifest = release.build(
                game_root,
                second_output,
                payload_root,
                game_targets=game_targets,
                support_targets=support_targets,
            )

            self.assertEqual(first_manifest["member_count"], 24)
            self.assertEqual(first_manifest["game_resource_count"], 15)
            self.assertEqual(first_manifest["support_file_count"], 9)
            self.assertEqual(
                first_manifest["release_zip"], second_manifest["release_zip"]
            )
            first_zip = first_output / release.ZIP_NAME
            second_zip = second_output / release.ZIP_NAME
            self.assertEqual(first_zip.read_bytes(), second_zip.read_bytes())
            with zipfile.ZipFile(first_zip) as archive:
                self.assertEqual(
                    archive.namelist(),
                    sorted((*release.GAME_TARGETS, *release.EXPECTED_SUPPORT_MEMBERS)),
                )
                self.assertNotIn("NOBU16PK.exe", archive.namelist())
                self.assertNotIn("Steamless.exe", archive.namelist())
            saved_manifest = json.loads(
                (first_output / release.MANIFEST_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual(saved_manifest, first_manifest)
            self.assertTrue(
                saved_manifest["checks"]["proprietary_game_executable_excluded"]
            )
            self.assertTrue(
                saved_manifest["checks"]["steamless_minimal_dependencies_exact"]
            )

    def test_modified_support_payload_fails_closed_and_removes_staging(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            game_root, payload_root, game_targets, support_targets = self.make_fixture(root)
            target = payload_root / "STATIC_OFFICER_EDITOR_FIX_README_KO.txt"
            target.write_text("tampered\n", encoding="utf-8")
            output = root / "failed"
            with self.assertRaisesRegex(release.ReleaseError, "release payload differs"):
                release.build(
                    game_root,
                    output,
                    payload_root,
                    game_targets=game_targets,
                    support_targets=support_targets,
                )
            self.assertFalse(output.exists())
            self.assertEqual(list(root.glob(".failed.staging-*")), [])

    def test_unexpected_payload_file_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            game_root, payload_root, game_targets, support_targets = self.make_fixture(root)
            (payload_root / "extra.txt").write_text("unexpected", encoding="utf-8")
            with self.assertRaisesRegex(release.ReleaseError, "member vector differs"):
                release.build(
                    game_root,
                    root / "failed",
                    payload_root,
                    game_targets=game_targets,
                    support_targets=support_targets,
                )

    def test_game_executable_and_unapproved_steamless_files_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _, payload_root, _, support_targets = self.make_fixture(root)
            game_exe = payload_root / "NOBU16PK.exe"
            game_exe.write_bytes(b"must not ship")
            with self.assertRaisesRegex(
                release.ReleaseError, "proprietary game executable"
            ):
                release.validate_payload_directory(payload_root, support_targets)
            game_exe.unlink()

            bad_steamless = payload_root / "OfficerEditorStaticFix" / "Steamless" / "Steamless.exe"
            bad_steamless.write_bytes(b"unapproved GUI")
            with self.assertRaisesRegex(release.ReleaseError, "unapproved Steamless"):
                release.validate_payload_directory(payload_root, support_targets)
            bad_steamless.unlink()

            bad_variant = (
                payload_root
                / "OfficerEditorStaticFix"
                / "Steamless"
                / "Plugins"
                / "Steamless.Unpacker.Variant31.x86.dll"
            )
            bad_variant.write_bytes(b"unapproved x86 plug-in")
            with self.assertRaisesRegex(release.ReleaseError, "unapproved Steamless"):
                release.validate_payload_directory(payload_root, support_targets)


if __name__ == "__main__":
    unittest.main()
