from __future__ import annotations

import importlib.util
import json
import tempfile
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
    "steam_jp_v0114_release", "tools/build_steam_jp_v0114_release.py"
)
previous_release = load_module(
    "steam_jp_v0113_release_for_v0114_test",
    "tools/build_steam_jp_v0113_release.py",
)


class SteamJpV0114ReleaseTests(unittest.TestCase):
    def test_release_identity_and_profile_delta_are_explicit(self) -> None:
        self.assertEqual(release.VERSION, "v0.11.4")
        self.assertIn("v0.11.4", release.ZIP_NAME)
        self.assertIn("v0.11.4", release.MANIFEST_NAME)
        self.assertTrue(release.SCHEMA.endswith("v0.11.4"))
        self.assertEqual(set(release.GAME_TARGETS), set(previous_release.GAME_TARGETS))

        changed = {
            path
            for path in release.GAME_TARGETS
            if release.GAME_TARGETS[path] != previous_release.GAME_TARGETS[path]
        }
        self.assertEqual(
            changed,
            {
                "MSG/JP/msggame.bin",
                "MSG/JP/strdata.bin",
                "MSG_PK/JP/msgdata.bin",
                "MSG_PK/JP/msgev.bin",
                "MSG_PK/JP/msggame.bin",
            },
        )
        self.assertEqual(
            release.GAME_TARGETS["MSG/JP/strdata.bin"][1],
            "6E7DD096A999299C43A9A23D9E99F75C81D6A9C8116488EC541A43423871B933",
        )
        self.assertEqual(
            release.GAME_TARGETS["MSG_PK/JP/msgdata.bin"][1],
            "73CF194E4EF81C20692A245DAC75C3B2A9FCF1A997B7F6755D89DBB59149F2ED",
        )

    def test_fixture_build_keeps_the_24_member_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            game_root = root / "game"
            fixture_targets: dict[str, tuple[int, str]] = {}
            upstream = release.load_upstream()
            for relative in release.GAME_TARGETS:
                path = game_root / Path(relative)
                path.parent.mkdir(parents=True, exist_ok=True)
                payload = f"fixture game resource: {relative}\n".encode()
                path.write_bytes(payload)
                fixture_targets[relative] = (
                    len(payload),
                    upstream.sha256_bytes(payload),
                )

            original_targets = release.GAME_TARGETS
            release.GAME_TARGETS = fixture_targets
            try:
                manifest = release.build(game_root, root / "output")
            finally:
                release.GAME_TARGETS = original_targets

            self.assertEqual(manifest["member_count"], 24)
            self.assertEqual(manifest["game_resource_count"], 15)
            self.assertEqual(manifest["support_file_count"], 9)
            self.assertTrue(all(manifest["checks"].values()))
            saved = json.loads(
                (root / "output" / release.MANIFEST_NAME).read_text(encoding="utf-8")
            )
            self.assertEqual(saved, manifest)


if __name__ == "__main__":
    unittest.main()
