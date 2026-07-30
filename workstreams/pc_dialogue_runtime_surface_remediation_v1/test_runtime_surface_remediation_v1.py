#!/usr/bin/env python3
"""Regression checks for the first user-reported runtime defects."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "runtime_surface_remediation",
    HERE / "build_runtime_surface_candidate_v1.py",
)
assert SPEC is not None and SPEC.loader is not None
BUILD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILD
SPEC.loader.exec_module(BUILD)


class RuntimeSurfaceRemediationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = BUILD.overlay_entries([BUILD.DEFAULT_PRIORITY_OVERLAY])

    def replacement(self, resource, coordinate):
        return self.entries[resource][coordinate]["ko"]

    def test_illness_notification_is_batchim_independent(self):
        expected = "에게 병환이 생겼습니다"
        self.assertEqual(
            self.replacement("base_msggame", (2, 142, 0)),
            expected,
        )
        self.assertEqual(
            self.replacement("pk_msggame", (2, 148, 0)),
            expected,
        )

    def test_base_diplomacy_log_has_both_spaces(self):
        first = self.replacement("base_msggame", (6, 3957, 0))
        second = self.replacement("base_msggame", (6, 3957, 1))
        self.assertTrue(first.startswith("이 "))
        self.assertTrue(first.endswith(" "))
        self.assertTrue(second.startswith("개월"))
        self.assertNotIn("(가)", first)
        assembled = "아사노 가문" + first + "13" + second
        self.assertEqual(
            assembled,
            "아사노 가문이 제안한 13개월 친선 협정을 수락",
        )

    def test_pk_lure_plan_uses_batchim_independent_direction(self):
        target = self.replacement("pk_msggame", (15, 1545, 2))
        self.assertTrue(target.startswith("으로 "))
        self.assertNotIn("을(를)", target)

    def test_user_reported_illness_assembly(self):
        suffix = self.replacement("pk_msggame", (2, 148, 0))
        self.assertEqual(
            "가타기리 가쓰모토" + suffix,
            "가타기리 가쓰모토에게 병환이 생겼습니다",
        )

    def test_user_reported_base_illness_dialogue_all_variants(self):
        body = self.replacement("base_msggame", (8, 1020, 1))
        apology = self.replacement("base_msggame", (8, 1020, 3))
        for pronoun in ("소승", "나", "저", "소인", "이 몸"):
            for ending in (
                "하지 않습니다",
                "하지 않는다",
                "하지 않사옵니다",
            ):
                assembled = pronoun + body + ending
                self.assertIn("에게도 병환이 들다니", assembled)
                self.assertNotIn("이(가)", assembled)
                self.assertNotIn("못하지 않", assembled)
                self.assertIn("힘을 발휘하지 ", assembled)
        for ending in (
            "죄송합니다",
            "미안하오",
            "면목이 없습니다",
            "송구하옵니다",
        ):
            self.assertEqual(apology + ending, "폐를 끼쳐 " + ending)

    def test_user_reported_pk_illness_dialogue_all_variants(self):
        body = self.replacement("pk_msggame", (8, 1032, 1))
        apology = self.replacement("pk_msggame", (8, 1032, 3))
        for pronoun in ("소승", "나", "저", "소인", "이 몸"):
            for ending in ("않습니다", "않는다", "않사옵니다"):
                assembled = pronoun + body + ending
                self.assertIn("에게도 병환이 들다니", assembled)
                self.assertNotIn("이(가)", assembled)
                self.assertIn("힘을 발휘하지 않", assembled)
                self.assertNotIn("발휘않", assembled)
        for ending in ("죄송합니다", "미안하오", "송구하옵니다"):
            self.assertEqual(apology + ending, "폐를 끼쳐 " + ending)

    def test_priority_overlay_rebuilds_without_source_drift(self):
        entries = self.entries
        for resource, relative in BUILD.RESOURCE_PATHS.items():
            path = BUILD.DEFAULT_INPUT_ROOT / relative
            rebuilt, metadata = BUILD.rebuild_resource(
                path,
                entries[resource],
            )
            self.assertGreater(len(rebuilt), 0)
            self.assertNotEqual(
                metadata["source_sha256"],
                metadata["candidate_sha256"],
            )


if __name__ == "__main__":
    unittest.main()
