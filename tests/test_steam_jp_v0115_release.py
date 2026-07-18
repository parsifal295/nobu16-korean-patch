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


release = load_module("steam_jp_v0115_release", "tools/build_steam_jp_v0115_release.py")
previous_release = load_module(
    "steam_jp_v0114_release_for_v0115_test",
    "tools/build_steam_jp_v0114_release.py",
)
upstream = release.load_module("steam_jp_v0112_test_helpers", release.UPSTREAM_PATH)


class SteamJpV0115ReleaseTests(unittest.TestCase):
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

    def test_release_advances_only_the_static_installer_contract(self) -> None:
        self.assertEqual(release.VERSION, "v0.11.5")
        self.assertIn("v0.11.5", release.ZIP_NAME)
        self.assertIn("v0.11.5", release.MANIFEST_NAME)
        self.assertTrue(release.SCHEMA.endswith("v0.11.5"))
        self.assertEqual(release.GAME_TARGETS, previous_release.GAME_TARGETS)
        self.assertEqual(len(release.SUPPORT_TARGETS), 9)
        self.assertEqual(release.STATIC_EXE_PATCH["patch_site_count"], 9)
        self.assertEqual(release.STATIC_EXE_PATCH["officer_editor_patch_site_count"], 5)
        self.assertEqual(release.STATIC_EXE_PATCH["fictional_princess_patch_site_count"], 4)
        self.assertFalse(release.STATIC_EXE_PATCH["shared_character_validators_modified"])
        self.assertEqual(
            release.STATIC_EXE_PATCH["previous_output_sha256"],
            previous_release.load_upstream().STATIC_EXE_PATCH["output_sha256"],
        )

    def test_repository_support_payload_matches_exact_pins(self) -> None:
        upstream.validate_payload_directory(
            release.DEFAULT_PAYLOAD_ROOT, release.SUPPORT_TARGETS
        )
        for relative, (size, digest) in release.SUPPORT_TARGETS.items():
            path = release.DEFAULT_PAYLOAD_ROOT / relative
            self.assertEqual(path.stat().st_size, size, relative)
            self.assertEqual(upstream.sha256_file(path), digest, relative)

    def test_fixture_build_is_deterministic_and_uses_new_contract(self) -> None:
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
