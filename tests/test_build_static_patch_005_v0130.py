from __future__ import annotations

import gzip
import hashlib
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "build_static_patch_005_v0130.py"
DEFINITION = (
    ROOT
    / "release_payload"
    / "v0.13.0"
    / "OfficerEditorStaticFix"
    / "Patches"
    / "005-DualResolutionAndHorizontalLandmarks.psd1"
)
PAYLOAD = DEFINITION.parent / "Payloads" / "005-DualResolutionAndHorizontalLandmarks.append.gz"


spec = importlib.util.spec_from_file_location("build_static_patch_005_v0130", SCRIPT)
assert spec and spec.loader
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class BuildStaticPatch005V0130Tests(unittest.TestCase):
    def test_builder_contract_is_pinned(self) -> None:
        self.assertEqual(builder.BASE_SIZE, 38_991_872)
        self.assertEqual(builder.TARGET_SIZE, 67_024_384)
        self.assertEqual(
            builder.EXPECTED_V0120_SHA256,
            "5D5B1F0B9CDE3A651DFA84E19FD5C7F2C6DF06D6D25C3674C049F7F049D26BF7",
        )
        self.assertEqual(
            builder.EXPECTED_V0130_SHA256,
            "FCA1D8CF58D44BDFAEFF338F5CF935AB9B2FA0F611EDC26CC8E9DF6E40B9D892",
        )

    def test_changed_run_detection_is_minimal(self) -> None:
        before = bytes.fromhex("00 01 02 03 04 05")
        after = bytes.fromhex("00 FF EE 03 DD 05")
        self.assertEqual(builder.changed_runs(before, after), [(1, 3), (4, 5)])

    def test_generated_definition_and_payload_are_exact(self) -> None:
        definition = DEFINITION.read_bytes()
        compressed = PAYLOAD.read_bytes()
        expanded = gzip.decompress(compressed)
        self.assertEqual(len(definition), 7_335)
        self.assertEqual(
            hashlib.sha256(definition).hexdigest().upper(),
            "31B31DDD996A403C8FEA1AA710FB709F352DA91AEEE35E050C98C2BF4BBE5E64",
        )
        self.assertEqual(len(compressed), 4_706_907)
        self.assertEqual(len(expanded), builder.TARGET_SIZE - builder.BASE_SIZE)
        self.assertEqual(
            hashlib.sha256(compressed).hexdigest().upper(),
            "F723A94E8A63409E0A5458D2790FEE7713EB805FA9E48488EF9281205E27BA1F",
        )


if __name__ == "__main__":
    unittest.main()
