#!/usr/bin/env python3
"""Regression contracts for the private Wave 15 plus Wave 16 bundle."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_text_quality_wave15_bundle_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("pc_text_quality_wave15_bundle", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BUNDLE = load_builder()


class Wave15BundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = BUNDLE.prepare_bundle()
        cls.wave16_profile, cls.wave16_evidence = BUNDLE.load_wave16_source()
        cls.wave15_msgev, cls.wave15_evidence = BUNDLE.load_wave15_source()

    def test_profile_is_exactly_the_eleven_file_jp_text_audit_set(self) -> None:
        self.assertEqual(self.bundle.audit["profile"], "JP_TEXT_AUDIT")
        self.assertEqual(tuple(self.bundle.profile), BUNDLE.PROFILE_PATHS)
        self.assertEqual(len(self.bundle.profile), 11)
        self.assertEqual(
            tuple(self.bundle.manifest["profile_paths"]),
            BUNDLE.PROFILE_PATHS,
        )
        self.assertEqual(
            tuple(BUNDLE.FINAL_SHA256),
            BUNDLE.PROFILE_PATHS,
        )
        self.assertEqual(
            tuple(BUNDLE.FINAL_SIZES),
            BUNDLE.PROFILE_PATHS,
        )

    def test_source_candidates_and_their_evidence_are_pinned(self) -> None:
        sources = self.bundle.audit["source_candidates"]
        self.assertEqual(sources["wave16"], self.wave16_evidence)
        self.assertEqual(sources["wave15"], self.wave15_evidence)
        self.assertEqual(BUNDLE.profile_hashes(self.wave16_profile), BUNDLE.WAVE16_SHA256)
        self.assertEqual(BUNDLE.sha256_bytes(self.wave15_msgev), BUNDLE.WAVE15_MSGEV_SHA256)
        self.assertEqual(len(self.wave15_msgev), BUNDLE.WAVE15_MSGEV_SIZE)
        self.assertEqual(
            sources["wave16"]["audit"]["sha256"],
            BUNDLE.WAVE16_AUDIT_SHA256,
        )
        self.assertEqual(
            sources["wave15"]["manifest"]["sha256"],
            BUNDLE.WAVE15_MANIFEST_SHA256,
        )

    def test_final_profile_has_exactly_the_three_required_file_diffs(self) -> None:
        final_hashes = BUNDLE.profile_hashes(self.bundle.profile)
        self.assertEqual(final_hashes, BUNDLE.FINAL_SHA256)
        self.assertEqual(
            BUNDLE.changed_paths(BUNDLE.WAVE14_SHA256, final_hashes),
            BUNDLE.FINAL_CHANGED_PATHS,
        )
        self.assertEqual(
            BUNDLE.changed_paths(BUNDLE.WAVE14_SHA256, BUNDLE.WAVE16_SHA256),
            (BUNDLE.BASE_MSGGAME, BUNDLE.PK_MSGGAME),
        )
        self.assertEqual(
            BUNDLE.changed_paths(BUNDLE.WAVE16_SHA256, final_hashes),
            (BUNDLE.PK_MSGEV,),
        )
        final_diff = self.bundle.audit["final_diff"]
        self.assertEqual(final_diff["changed_paths"], list(BUNDLE.FINAL_CHANGED_PATHS))
        self.assertEqual(len(final_diff["unchanged_paths"]), 8)

    def test_merge_retains_wave16_bytes_except_for_wave15_msgev(self) -> None:
        for relative in BUNDLE.PROFILE_PATHS:
            with self.subTest(relative=relative):
                if relative == BUNDLE.PK_MSGEV:
                    self.assertEqual(self.bundle.profile[relative], self.wave15_msgev)
                else:
                    self.assertEqual(self.bundle.profile[relative], self.wave16_profile[relative])
        self.assertEqual(
            self.bundle.profile[BUNDLE.BASE_MSGGAME],
            self.wave16_profile[BUNDLE.BASE_MSGGAME],
        )
        self.assertEqual(
            self.bundle.profile[BUNDLE.PK_MSGGAME],
            self.wave16_profile[BUNDLE.PK_MSGGAME],
        )

    def test_event_name_text_diff_remains_exactly_the_three_wave15_ids(self) -> None:
        event_diff = self.bundle.audit["final_diff"]["event_name_text_diff"]
        self.assertEqual(event_diff["changed_ids"], list(BUNDLE.WAVE15_EVENT_NAME_IDS))
        rows = {row["id"]: row for row in event_diff["rows"]}
        self.assertEqual(set(rows), set(BUNDLE.WAVE15_EVENT_NAME_IDS))
        for entry_id in BUNDLE.WAVE15_EVENT_NAME_IDS:
            with self.subTest(entry_id=entry_id):
                self.assertEqual(
                    rows[entry_id]["current_utf16le_sha256"],
                    BUNDLE.WAVE15_CURRENT_TEXT_SHA256[entry_id],
                )
                self.assertEqual(
                    rows[entry_id]["target_utf16le_sha256"],
                    BUNDLE.WAVE15_TARGET_TEXT_SHA256[entry_id],
                )

    def test_source_and_output_policy_excludes_switch_steam_git_and_release(self) -> None:
        policy = self.bundle.audit["source_policy"]
        self.assertTrue(policy["wave15_candidate_read"])
        self.assertTrue(policy["wave16_candidate_read"])
        self.assertFalse(policy["switch_korean_read"])
        self.assertFalse(policy["steam_game_resource_written"])
        self.assertEqual(policy["steam_apply_capability"], "absent")
        self.assertEqual(policy["git_operation"], "absent")
        self.assertEqual(policy["release_operation"], "absent")
        self.assertEqual(self.bundle.manifest["steam_apply"], "absent")
        self.assertEqual(self.bundle.manifest["git_operation"], "absent")
        self.assertEqual(self.bundle.manifest["release_operation"], "absent")

    def test_bundle_is_deterministic_and_output_guard_rejects_steam(self) -> None:
        again = BUNDLE.prepare_bundle()
        self.assertEqual(again.profile, self.bundle.profile)
        self.assertEqual(again.audit, self.bundle.audit)
        self.assertEqual(again.manifest, self.bundle.manifest)
        valid = BUNDLE.require_tmp(BUNDLE.TMP_ROOT / "unit-test-candidate", "unit test")
        self.assertEqual(valid, (BUNDLE.TMP_ROOT / "unit-test-candidate").resolve())
        with self.assertRaises(BUNDLE.BundleError):
            BUNDLE.require_tmp(Path(r"F:\SteamLibrary\steamapps\common\NOBU16"), "Steam")


if __name__ == "__main__":
    unittest.main(verbosity=2)
