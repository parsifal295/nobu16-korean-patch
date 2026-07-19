from __future__ import annotations

import hashlib
import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))


def load_builder():
    path = TOOLS / "build_map_label_hotfix_v0130.py"
    spec = importlib.util.spec_from_file_location("map_label_hotfix_v0130", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load_builder()


class MapLabelHotfixV0130Tests(unittest.TestCase):
    def test_landmark_patch_sites_are_exact_and_unique(self) -> None:
        sites = builder.LANDMARK_HORIZONTAL_SITES
        self.assertEqual(len(sites), 11)
        self.assertEqual(len({va for va, _before, _purpose in sites}), 11)
        self.assertTrue(all(len(before) == 5 for _va, before, _purpose in sites))
        self.assertTrue(all(purpose for _va, _before, purpose in sites))

    def test_ground_landmark_owner_stages_are_covered(self) -> None:
        addresses = {va for va, _before, _purpose in builder.LANDMARK_HORIZONTAL_SITES}
        self.assertEqual(
            addresses,
            {
                0x140F42BFB,
                0x140F42C2A,
                0x140F42DC7,
                0x140F42DFD,
                0x140F42E3D,
                0x140F42E52,
                0x140F42F13,
                0x140F42F38,
                0x140F42F5D,
                0x140F42F82,
                0x140F61B10,
            },
        )

    def test_horizontal_result_is_local_constant_true(self) -> None:
        self.assertEqual(builder.HORIZONTAL_RESULT, bytes.fromhex("B8 01 00 00 00"))

    def test_source_and_output_hashes_are_pinned(self) -> None:
        for value in (
            builder.EXPECTED_V0121_SHA256,
            builder.EXPECTED_CANDIDATE_SHA256,
        ):
            self.assertRegex(value, r"^[0-9A-F]{64}$")

    def test_changed_run_detection_is_minimal(self) -> None:
        before = bytes.fromhex("00 01 02 03 04 05")
        after = bytes.fromhex("00 FF EE 03 DD 05")
        self.assertEqual(builder.changed_runs(before, after), [(1, 3), (4, 5)])

    def test_builder_script_hash_is_stable_shape(self) -> None:
        digest = hashlib.sha256(
            (TOOLS / "build_map_label_hotfix_v0130.py").read_bytes()
        ).hexdigest()
        self.assertRegex(digest, r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
