#!/usr/bin/env python3
"""Regression contracts for the private Wave 20 composition bundle."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_text_quality_wave20_bundle_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("pc_text_quality_wave20_bundle", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BUNDLE = load_builder()


class Wave20BundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = BUNDLE.prepare_bundle()
        cls.wave21_profile, cls.wave21_evidence = BUNDLE.load_wave21_source()
        cls.wave18_msgev, cls.wave18_evidence = BUNDLE.load_wave18_source()

    def test_profile_is_exactly_the_eleven_file_jp_text_audit_set(self) -> None:
        self.assertEqual(self.bundle.audit["profile"], "JP_TEXT_AUDIT")
        self.assertEqual(tuple(self.bundle.profile), BUNDLE.PROFILE_PATHS)
        self.assertEqual(len(self.bundle.profile), 11)
        self.assertEqual(tuple(self.bundle.manifest["profile_paths"]), BUNDLE.PROFILE_PATHS)
        self.assertEqual(tuple(BUNDLE.WAVE21_SHA256), BUNDLE.PROFILE_PATHS)
        self.assertEqual(tuple(BUNDLE.FINAL_SHA256), BUNDLE.PROFILE_PATHS)
        self.assertEqual(tuple(BUNDLE.FINAL_SIZES), BUNDLE.PROFILE_PATHS)

    def test_wave21_and_wave18_sources_are_pinned_with_their_evidence(self) -> None:
        sources = self.bundle.audit["source_candidates"]
        self.assertEqual(sources["wave21"], self.wave21_evidence)
        self.assertEqual(sources["wave18"], self.wave18_evidence)
        self.assertEqual(BUNDLE.profile_hashes(self.wave21_profile), BUNDLE.WAVE21_SHA256)
        self.assertEqual(BUNDLE.sha256_bytes(self.wave18_msgev), BUNDLE.WAVE18_MSGEV_SHA256)
        self.assertEqual(len(self.wave18_msgev), BUNDLE.WAVE18_MSGEV_SIZE)
        self.assertEqual(sources["wave21"]["audit"]["sha256"], BUNDLE.WAVE21_AUDIT_SHA256)
        self.assertEqual(sources["wave18"]["manifest"]["sha256"], BUNDLE.WAVE18_MANIFEST_SHA256)

    def test_final_profile_diff_from_wave21_is_only_msgev(self) -> None:
        final_hashes = BUNDLE.profile_hashes(self.bundle.profile)
        self.assertEqual(final_hashes, BUNDLE.FINAL_SHA256)
        self.assertEqual(
            BUNDLE.changed_paths(BUNDLE.WAVE21_SHA256, final_hashes),
            BUNDLE.FINAL_CHANGED_FROM_WAVE21,
        )
        final_diff = self.bundle.audit["final_diff"]
        self.assertEqual(final_diff["changed_paths"], list(BUNDLE.FINAL_CHANGED_FROM_WAVE21))
        self.assertEqual(len(final_diff["retained_paths"]), 10)

    def test_merge_retains_all_wave21_bytes_except_wave18_msgev(self) -> None:
        for relative in BUNDLE.PROFILE_PATHS:
            with self.subTest(relative=relative):
                if relative == BUNDLE.PK_MSGEV:
                    self.assertEqual(self.bundle.profile[relative], self.wave18_msgev)
                else:
                    self.assertEqual(self.bundle.profile[relative], self.wave21_profile[relative])
        self.assertEqual(self.bundle.profile[BUNDLE.PK_MSGGAME], self.wave21_profile[BUNDLE.PK_MSGGAME])

    def test_issue61_paths_remain_exact_wave21_bytes(self) -> None:
        final_hashes = BUNDLE.profile_hashes(self.bundle.profile)
        self.assertEqual(
            self.bundle.audit["final_diff"]["issue61_retained_paths"],
            list(BUNDLE.ISSUE61_RETAINED_PATHS),
        )
        for relative in BUNDLE.ISSUE61_RETAINED_PATHS:
            with self.subTest(relative=relative):
                self.assertEqual(self.bundle.profile[relative], self.wave21_profile[relative])
                self.assertEqual(final_hashes[relative], BUNDLE.WAVE21_SHA256[relative])

    def test_event_static_text_diff_remains_the_eight_reviewed_ids(self) -> None:
        event_diff = self.bundle.audit["final_diff"]["event_static_text_diff"]
        self.assertEqual(event_diff["changed_ids"], list(BUNDLE.WAVE18_EVENT_IDS))
        rows = {row["id"]: row for row in event_diff["rows"]}
        self.assertEqual(set(rows), set(BUNDLE.WAVE18_EVENT_IDS))
        for entry_id in BUNDLE.WAVE18_EVENT_IDS:
            with self.subTest(entry_id=entry_id):
                current_hash, target_hash = BUNDLE.WAVE18_EVENT_TEXT_HASHES[entry_id]
                self.assertEqual(rows[entry_id]["current_utf16le_sha256"], current_hash)
                self.assertEqual(rows[entry_id]["target_utf16le_sha256"], target_hash)

    def test_policy_excludes_switch_steam_git_release_and_network(self) -> None:
        policy = self.bundle.audit["source_policy"]
        self.assertTrue(policy["wave21_candidate_read"])
        self.assertTrue(policy["wave18_candidate_read"])
        self.assertFalse(policy["switch_korean_read"])
        self.assertFalse(policy["steam_game_resource_written"])
        self.assertEqual(policy["steam_apply_capability"], "absent")
        self.assertEqual(policy["git_operation"], "absent")
        self.assertEqual(policy["release_operation"], "absent")
        self.assertEqual(policy["network_operation"], "absent")
        self.assertEqual(self.bundle.manifest["steam_apply"], "absent")
        self.assertEqual(self.bundle.manifest["git_operation"], "absent")
        self.assertEqual(self.bundle.manifest["release_operation"], "absent")

    def test_bundle_is_deterministic_and_output_guard_rejects_nonprivate_paths(self) -> None:
        again = BUNDLE.prepare_bundle()
        self.assertEqual(again.profile, self.bundle.profile)
        self.assertEqual(again.audit, self.bundle.audit)
        self.assertEqual(again.manifest, self.bundle.manifest)
        valid = BUNDLE.require_tmp_child(BUNDLE.TMP_ROOT / "unit-test-candidate", "unit test")
        self.assertEqual(valid, (BUNDLE.TMP_ROOT / "unit-test-candidate").resolve())
        with self.assertRaises(BUNDLE.BundleError):
            BUNDLE.require_tmp_child(BUNDLE.TMP_ROOT, "unit test root")
        with self.assertRaises(BUNDLE.BundleError):
            BUNDLE.require_tmp_child(Path(r"F:\SteamLibrary\steamapps\common\NOBU16"), "Steam")


if __name__ == "__main__":
    unittest.main(verbosity=2)
