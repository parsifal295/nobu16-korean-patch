import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "verify_release_v0_7_1", HERE / "verify_release_v0_7_1.py"
)
assert SPEC and SPEC.loader
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class ReleaseV071Tests(unittest.TestCase):
    def test_manifest_is_stable_exact_12_jp_release(self):
        manifest = VERIFY.load_manifest()
        self.assertEqual(manifest["release"]["tag"], "v0.7.1")
        self.assertTrue(manifest["release"]["stable"])
        self.assertFalse(manifest["release"]["prerelease"])
        self.assertEqual(manifest["runtime"]["language_route"], "JP")
        self.assertEqual({row["path"] for row in manifest["entries"]}, VERIFY.EXPECTED_PATHS)

    def test_surname_candidate_and_four_fonts_are_pinned(self):
        manifest = VERIFY.load_manifest()
        by_path = {row["path"]: row for row in manifest["entries"]}
        self.assertEqual(
            by_path["MSG_PK/JP/msgdata.bin"]["sha256"],
            VERIFY.SURNAME_MSGDATA_HASH,
        )
        self.assertEqual(manifest["scope"]["officer_surnames_recovered"], 980)
        self.assertEqual(manifest["scope"]["font_container_count"], 4)
        self.assertTrue(VERIFY.FONT_PATHS <= set(by_path))

    def test_manifest_contains_hashes_not_game_bytes(self):
        manifest = VERIFY.load_manifest()
        self.assertFalse(manifest["scope"]["commercial_binary_bytes_included"])
        for row in manifest["entries"]:
            self.assertRegex(row["sha256"], r"^[0-9A-F]{64}$")
            self.assertNotIn("data", row)
            self.assertNotIn("text", row)


if __name__ == "__main__":
    unittest.main()
