from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "public" / "steam_jp_117_v0102_release.v1.json"
SPEC = importlib.util.spec_from_file_location(
    "steam_jp_v0102_release", ROOT / "tools" / "build_steam_jp_v0102_release.py"
)
assert SPEC and SPEC.loader
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


class SteamJpV0102ReleaseTests(unittest.TestCase):
    def test_public_manifest_matches_the_release_builder_contract(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema"], release.SCHEMA)
        self.assertEqual(manifest["version"], release.VERSION)
        self.assertEqual(manifest["member_count"], 15)
        self.assertEqual(manifest["release_zip"]["name"], release.ZIP_NAME)
        self.assertEqual(
            manifest["members"],
            {
                path: {"size": size, "sha256": sha256}
                for path, (size, sha256) in sorted(release.TARGETS.items())
            },
        )

    def test_release_includes_the_runtime_loaded_ordinary_resolution_atlas(self) -> None:
        path = "RES_JP/res_lang_exp.bin"
        self.assertIn(path, release.TARGETS)
        self.assertEqual(
            release.TARGETS[path],
            (
                13_796_051,
                "AC55622FC5C78ECA4ECFE37D1D890D5B26F6200ED7BAF1506B784541E158B7B7",
            ),
        )

    def test_release_paths_and_hashes_are_canonical(self) -> None:
        self.assertEqual(len(release.TARGETS), 15)
        for path, (size, sha256) in release.TARGETS.items():
            self.assertEqual(path, Path(path).as_posix())
            self.assertNotIn("..", Path(path).parts)
            self.assertGreater(size, 0)
            self.assertEqual(len(sha256), 64)
            self.assertEqual(sha256, sha256.upper())


if __name__ == "__main__":
    unittest.main()
