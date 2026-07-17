from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "public" / "steam_jp_117_v0101_release.v1.json"
SPEC = importlib.util.spec_from_file_location(
    "steam_jp_v0101_release", ROOT / "tools" / "build_steam_jp_v0101_release.py"
)
assert SPEC and SPEC.loader
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


class SteamJpV0101ReleaseTests(unittest.TestCase):
    def test_public_manifest_matches_the_release_builder_contract(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema"], release.SCHEMA)
        self.assertEqual(manifest["version"], release.VERSION)
        self.assertEqual(manifest["member_count"], 14)
        self.assertEqual(manifest["release_zip"]["name"], release.ZIP_NAME)
        self.assertEqual(
            manifest["members"],
            {
                path: {"size": size, "sha256": sha256}
                for path, (size, sha256) in sorted(release.TARGETS.items())
            },
        )

    def test_release_paths_and_hashes_are_canonical(self) -> None:
        self.assertEqual(len(release.TARGETS), 14)
        for path, (size, sha256) in release.TARGETS.items():
            self.assertEqual(path, Path(path).as_posix())
            self.assertNotIn("..", Path(path).parts)
            self.assertGreater(size, 0)
            self.assertEqual(len(sha256), 64)
            self.assertEqual(sha256, sha256.upper())


if __name__ == "__main__":
    unittest.main()
