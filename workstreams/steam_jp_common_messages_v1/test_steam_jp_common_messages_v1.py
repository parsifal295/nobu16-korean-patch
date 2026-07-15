#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "build_steam_jp_common_messages_v1.py"
SPEC = importlib.util.spec_from_file_location("steam_jp_common_messages_v1", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


EXPECTED = {
    "msgev.bin": (13_794, 73, 2, 71),
    "msgdata.bin": (23_369, 72, 48, 24),
    "msgbre.bin": (2_216, 0, 0, 0),
    "msgire.bin": (122, 0, 0, 0),
    "msgstf.bin": (6, 1, 0, 1),
}
JP_SCRIPT_RE = re.compile(r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def assert_no_publisher_text(test: unittest.TestCase, value: object, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            test.assertNotIn(key, {"source_jp", "source_text", "official_jp", "jp_text"})
            if key == "ko":
                test.assertIsInstance(child, str)
                continue
            assert_no_publisher_text(test, child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_no_publisher_text(test, child, f"{path}[{index}]")
    elif isinstance(value, str):
        test.assertIsNone(JP_SCRIPT_RE.search(value), f"publisher-script text at {path}")


class SteamJpCommonMessagesV1Test(unittest.TestCase):
    def test_public_overlays_are_jp_native_and_exact(self) -> None:
        total_applied = 0
        total_nonmapped = 0
        total_collapsed = 0
        total_unresolved = 0
        for name, (expected_applied, expected_nonmapped, expected_collapsed, expected_unresolved) in EXPECTED.items():
            value = json.loads(module.OVERLAY_PATHS[name].read_text(encoding="utf-8"))
            entries = module.validate_overlay(value, name)
            self.assertEqual(len(entries), expected_applied)
            self.assertEqual(
                value["provenance"]["legacy_nonmapped_coordinate_count"],
                expected_nonmapped,
            )
            self.assertEqual(
                value["provenance"]["collapsed_duplicate_coverage_count"],
                expected_collapsed,
            )
            self.assertEqual(value["provenance"]["unresolved_count"], expected_unresolved)
            self.assertEqual(value["resource"], f"MSG_PK/JP/{name}")
            self.assertFalse(value["provenance"]["sc_binary_used"])
            self.assertFalse(value["provenance"]["sc_coordinate_used"])
            assert_no_publisher_text(self, value)
            total_applied += expected_applied
            total_nonmapped += expected_nonmapped
            total_collapsed += expected_collapsed
            total_unresolved += expected_unresolved
        self.assertEqual(total_applied, 39_507)
        self.assertEqual(total_nonmapped, 146)
        self.assertEqual(total_collapsed, 50)
        self.assertEqual(total_unresolved, 96)

    def test_review_and_validation_are_source_free_and_exact(self) -> None:
        review = json.loads(module.REVIEW_PATH.read_text(encoding="utf-8"))
        validation = json.loads(module.VALIDATION_PATH.read_text(encoding="utf-8"))
        self.assertEqual(review["aggregate_legacy_nonmapped_coordinate_count"], 146)
        self.assertEqual(review["aggregate_collapsed_duplicate_coverage_count"], 50)
        self.assertEqual(review["aggregate_unresolved_count"], 96)
        self.assertEqual(validation["status"], "PASS")
        self.assertEqual(validation["aggregate"]["applied_count"], 39_507)
        self.assertEqual(validation["aggregate"]["legacy_nonmapped_coordinate_count"], 146)
        self.assertEqual(validation["aggregate"]["collapsed_duplicate_coverage_count"], 50)
        self.assertEqual(validation["aggregate"]["unresolved_count"], 96)
        self.assertTrue(validation["all_candidate_ab_equal"])
        self.assertFalse(validation["sc_binary_used"])
        self.assertFalse(validation["sc_coordinate_used"])
        assert_no_publisher_text(self, review)
        assert_no_publisher_text(self, validation)
        for artifact in validation["artifacts"]:
            path = module.REPO_ROOT / artifact["path"]
            self.assertEqual(path.stat().st_size, artifact["size"])
            self.assertEqual(sha256(path), artifact["sha256"])

    def test_tracked_workstream_contains_no_complete_resource(self) -> None:
        self.assertEqual(list(HERE.rglob("*.bin")), [])
        payload = "\n".join(
            path.read_text(encoding="utf-8", errors="strict")
            for path in HERE.rglob("*.json")
        )
        self.assertNotIn("/SC/", payload)
        self.assertNotIn('"source_sc', payload)
        self.assertNotIn('"stock_sc', payload)

    def test_live_steam_rebuild_is_deterministic_and_non_mutating(self) -> None:
        root = module.DEFAULT_STEAM_ROOT
        if not all((root / "MSG_PK" / "JP" / name).is_file() for name in module.FILES):
            self.skipTest("pinned Steam JP installation is unavailable")
        paths = {name: root / "MSG_PK" / "JP" / name for name in module.FILES}
        before = {name: (path.stat().st_size, sha256(path)) for name, path in paths.items()}
        result = module.verify_public(root)
        after = {name: (path.stat().st_size, sha256(path)) for name, path in paths.items()}
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["applied_count"], 39_507)
        self.assertEqual(result["legacy_nonmapped_coordinate_count"], 146)
        self.assertEqual(result["collapsed_duplicate_coverage_count"], 50)
        self.assertEqual(result["unresolved_count"], 96)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
