#!/usr/bin/env python3
"""Deterministic regressions for the final Base call-assembly pass."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "base_call_assembly_remediation_test_subject",
    HERE / "base_call_assembly_remediation_v1.py",
)
assert SPEC is not None and SPEC.loader is not None
BUILD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILD
SPEC.loader.exec_module(BUILD)


class BaseCallAssemblyRemediationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = BUILD.DEFAULT_SOURCE.read_bytes()
        cls.candidate, cls.report = BUILD.build(cls.source)
        cls.records = BUILD.records_from_blob(cls.candidate)
        cls.renderer = BUILD.CALL_QA.SyntheticSelectorRenderer(cls.records)

    def test_candidate_is_deterministic_and_closes_audit(self) -> None:
        self.assertEqual(self.report["status"], "PASS")
        self.assertEqual(self.report["source_issue_count"], 3000)
        self.assertEqual(self.report["final_issue_count"], 0)
        self.assertEqual(self.report["literal_replacement_count"], 2588)
        self.assertEqual(self.report["retarget_count"], 1672)
        self.assertEqual(
            self.report["candidate_sha256"],
            "B49E084309CA0845AAA29C6794ECA2C55DF2BAB122CF3CD5409604499AA6617B",
        )
        second, second_report = BUILD.build(self.source)
        self.assertEqual(second, self.candidate)
        self.assertEqual(
            BUILD.canonical_json(second_report),
            BUILD.canonical_json(self.report),
        )

    def test_reported_clan_treaty_notifications_are_exact(self) -> None:
        self.assertEqual(
            self.renderer.render((6, 3957)),
            (
                "도쿠가와 가문이 제안한 \uE000개월 친선 협정을 수락",
            ),
        )
        self.assertEqual(
            self.renderer.render((6, 3958)),
            (
                "도쿠가와 가문이 제안한 친선 협정을 거부",
            ),
        )

    def test_ai_hostility_help_never_breaks_inside_a_word(self) -> None:
        self.assertEqual(
            self.renderer.render((4, 26)),
            (
                "【AI 호전도】\n"
                "타 세력의 호전도를 설정합니다\n"
                "높을수록 적국을 침공하기\n"
                "쉬워집니다",
            ),
        )
        self.assertNotIn("쉬워집\n니다", self.renderer.render((4, 26))[0])

    def test_reported_disease_cartesian_product_has_no_broken_carrier(
        self,
    ) -> None:
        variants = self.renderer.render((8, 1020))
        self.assertEqual(len(variants), 60)
        for value in variants:
            self.assertIn("에게도 병환이 들다니", value)
            self.assertIn("제 힘을 발휘하지 ", value)
            self.assertNotIn("(이)가", value)
            self.assertNotIn("발휘않", value)
        combined = self.renderer.render((8, 107))
        self.assertEqual(len(combined), 62)
        self.assertEqual(combined[2:], variants)

    def test_only_reviewed_archaic_morph_pairs_remain(self) -> None:
        expected = {
            (6, 3432): "올해도 쉬지 않고 정진하겠사와요",
            (7, 1096): "여기서는 원군을 청하옵시다",
        }
        for coordinate, value in expected.items():
            self.assertTrue(
                any(
                    value in rendered
                    for rendered in self.renderer.render(coordinate)
                )
            )
            self.assertEqual(
                BUILD.CALL_QA.reviewed_morph_pair_collisions(
                    "base_msggame",
                    coordinate,
                    value,
                ),
                (),
            )

    def test_reviewed_sentence_level_repairs_are_exact(self) -> None:
        self.assertEqual(
            self.renderer.render((1, 18)),
            (
                "감사합니다. 부모의 원수를 찾아 떠돌고 있습니다.",
            ),
        )
        for value in self.renderer.render((8, 278)):
            self.assertRegex(value, r"올해는 흉작이 들었")
            self.assertIn("고려해야 ", value)
            self.assertNotIn("고려해야 하안", value)
        for value in self.renderer.render((15, 267)):
            self.assertIn("잠시 기다려", value)
            self.assertIn("맡길 수 없", value)
            self.assertIn("출진이 시급합니다", value)
        self.assertEqual(
            self.renderer.render((15, 1410)),
            (
                "\uE000님을 찾아냈습니다\n"
                "우리 가문에 사관하고 싶다는 뜻이오. 어떠하오?",
            ),
        )

    def test_opaque_dynamic_name_boundaries_are_exact(self) -> None:
        for value in self.renderer.render((6, 90)):
            self.assertNotIn("하고\uE000", value)
            self.assertNotIn("\uE000님", value)
            self.assertNotIn("\uE000공", value)
        for coordinate in ((6, 134), (6, 3471), (6, 3529)):
            for value in self.renderer.render(coordinate):
                if "과연" in value:
                    self.assertIn("과연 \uE000", value)
                    self.assertNotIn("과연\uE000", value)
        for value in self.renderer.render((6, 3402)):
            self.assertTrue(value.startswith("안심하고 주시오, "))
            self.assertNotIn("\uE000공", value)
            self.assertNotIn("\uE000놈", value)
        self.assertEqual(
            {
                value.splitlines()[0]
                for value in self.renderer.render((7, 218))
            },
            {"\uE000의 활약으로"},
        )
        for value in self.renderer.render((7, 218)):
            self.assertIn("\n적장을 포박", value)
            self.assertNotIn("(이)가", value)
            self.assertNotIn("우리\uE000", value)
            self.assertNotIn("저희\uE000", value)


if __name__ == "__main__":
    unittest.main()
