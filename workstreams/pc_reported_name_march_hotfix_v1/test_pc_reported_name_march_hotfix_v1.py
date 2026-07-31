#!/usr/bin/env python3
"""Regression tests for the v0.90.1 surname and march report hotfix."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "build_pc_reported_name_march_hotfix_v1.py"
SPEC = importlib.util.spec_from_file_location(
    "pc_reported_name_march_hotfix_v1",
    MODULE_PATH,
)
assert SPEC is not None and SPEC.loader is not None
HOTFIX = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = HOTFIX
SPEC.loader.exec_module(HOTFIX)


class ReportedNameMarchHotfixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not HOTFIX.DEFAULT_INPUT_ROOT.is_dir():
            raise unittest.SkipTest("the pinned v0.90.1 input root is unavailable")
        cls.before_profile = HOTFIX.profile(HOTFIX.DEFAULT_INPUT_ROOT)
        cls.output, cls.report = HOTFIX.prepare_candidate(
            HOTFIX.DEFAULT_INPUT_ROOT
        )

    def test_source_free_overlay_is_exact(self) -> None:
        overlay = json.loads(
            HOTFIX.OVERLAY_PATH.read_text(encoding="utf-8")
        )
        self.assertEqual(HOTFIX.expected_overlay(), overlay)
        self.assertFalse(
            overlay["distribution_policy"]["contains_commercial_source_text"]
        )
        self.assertFalse(
            overlay["distribution_policy"]["contains_complete_game_binary"]
        )
        self.assertFalse(
            overlay["distribution_policy"]["steam_write_supported"]
        )

    def test_only_surname_slot_757_changes_in_two_tables(self) -> None:
        self.assertEqual("PASS", self.report["status"])
        self.assertEqual(
            [HOTFIX.BASE_STRDATA, HOTFIX.PK_MSGDATA],
            self.report["changed_resources"],
        )
        self.assertEqual("초 ", self.report["surname"]["after"])
        self.assertTrue(
            self.report["surname"]["trailing_composition_space_preserved"]
        )
        self.assertTrue(
            self.report["surname"]["non_target_slot_bytes_identical"]
        )
        self.assertNotEqual("부족", self.report["surname"]["after"])

        source_base = (
            HOTFIX.DEFAULT_INPUT_ROOT / HOTFIX.BASE_STRDATA
        ).read_bytes()
        source_pk = (
            HOTFIX.DEFAULT_INPUT_ROOT / HOTFIX.PK_MSGDATA
        ).read_bytes()
        HOTFIX.verify_component_delta(
            source_base,
            self.output[HOTFIX.BASE_STRDATA],
            source_pk,
            self.output[HOTFIX.PK_MSGDATA],
        )

    def test_march_notification_is_correct_and_byte_identical(self) -> None:
        march = self.report["march_regression"]
        self.assertEqual("6:4137", march["coordinate"])
        self.assertEqual(HOTFIX.MARCH_FORMAL_RENDER, march["formal_render"])
        self.assertNotIn("성행", march["formal_render"])
        self.assertNotIn("진군대입니다", march["formal_render"])
        self.assertTrue(march["source_resource_byte_identical"])
        self.assertEqual(
            (
                HOTFIX.DEFAULT_INPUT_ROOT / HOTFIX.BASE_MSGGAME
            ).read_bytes(),
            self.output[HOTFIX.BASE_MSGGAME],
        )

    def test_exact_input_and_target_profiles_are_pinned(self) -> None:
        self.assertEqual(
            (HOTFIX.INPUT_SHA256, HOTFIX.INPUT_SIZES),
            self.before_profile,
        )
        actual_hashes = {
            relative: HOTFIX.sha256_bytes(self.output[relative])
            for relative in HOTFIX.PROFILE_PATHS
        }
        actual_sizes = {
            relative: len(self.output[relative])
            for relative in HOTFIX.PROFILE_PATHS
        }
        self.assertEqual(HOTFIX.TARGET_SHA256, actual_hashes)
        self.assertEqual(HOTFIX.TARGET_SIZES, actual_sizes)
        self.assertEqual(
            self.before_profile,
            HOTFIX.profile(HOTFIX.DEFAULT_INPUT_ROOT),
        )

    def test_private_candidate_build_and_verify_is_deterministic(self) -> None:
        HOTFIX.TMP_ROOT.mkdir(parents=True, exist_ok=True)
        scratch = Path(
            tempfile.mkdtemp(
                prefix=".reported-hotfix-test-",
                dir=HOTFIX.TMP_ROOT,
            )
        )
        output_root = scratch / "candidate"
        manifest_path = scratch / "manifest.v1.json"
        try:
            report = HOTFIX.build_candidate(
                HOTFIX.DEFAULT_INPUT_ROOT,
                output_root,
                manifest_path,
            )
            self.assertEqual(self.report, report)
            self.assertEqual(
                self.report,
                HOTFIX.verify_private_candidate(
                    HOTFIX.DEFAULT_INPUT_ROOT,
                    output_root,
                ),
            )
            self.assertEqual(
                self.report,
                json.loads(manifest_path.read_text(encoding="utf-8")),
            )
            self.assertEqual(
                set(HOTFIX.PROFILE_PATHS),
                HOTFIX.output_files(output_root),
            )
        finally:
            shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
