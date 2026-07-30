#!/usr/bin/env python3
"""Deterministic regression tests for the PK runtime-surface remediation."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "pk_runtime_surface_remediation",
    HERE / "pk_build_runtime_surface_remediation_v1.py",
)
assert SPEC is not None and SPEC.loader is not None
BUILD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILD
SPEC.loader.exec_module(BUILD)


class PkRuntimeSurfaceRemediationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (
            cls.candidate,
            cls.overlay,
            cls.surface_audit,
            cls.terminal_audit,
            cls.report,
        ) = BUILD.build()
        cls.records = BUILD.records_from_blob(cls.candidate)
        cls.literals = BUILD.literal_map(cls.candidate)

    def test_candidate_closes_both_independent_audits(self) -> None:
        self.assertEqual(self.report["status"], "PASS")
        self.assertEqual(self.report["candidate"]["surface_issue_count"], 0)
        self.assertEqual(
            self.report["terminal_boundary_detector"]["issue_count"],
            0,
        )
        self.assertEqual(
            self.report["call_carrier_rejection"][
                "candidate_detected_artifact_count"
            ],
            0,
        )
        self.assertEqual(
            self.report["selector_carrier_rejection"][
                "candidate_detected_artifact_count"
            ],
            0,
        )

    def test_build_is_byte_for_byte_deterministic(self) -> None:
        second = BUILD.build()
        self.assertEqual(second[0], self.candidate)
        self.assertEqual(second[1], self.overlay)
        self.assertEqual(second[2], self.surface_audit)
        self.assertEqual(second[3], self.terminal_audit)
        self.assertEqual(
            BUILD.canonical_json(second[4]),
            BUILD.canonical_json(self.report),
        )

    def test_priority_regressions_round_trip_exactly(self) -> None:
        expected = {
            (2, 148, 0): "에게 병환이 생겼습니다",
            (8, 1032, 1):
                "에게도 병환이 들다니…\n…당분간 제 힘을 발휘하지 ",
            (8, 1032, 3): "폐를 끼쳐 ",
            (15, 1545, 0): "을 공략할 계책이 있사옵니다",
            (15, 1545, 2):
                "으로 적병을 유인하면\n허술해진 성을 공략할 수 있을 것",
        }
        for coordinate, text in expected.items():
            self.assertEqual(self.literals[coordinate], text)
        self.assertEqual(
            self.report["overlay"]["priority_replacement_count"],
            len(expected),
        )

    def test_illness_dialogue_has_all_45_exact_runtime_assemblies(self) -> None:
        evidence = self.report["regressions"]["8:1032"]
        self.assertTrue(evidence["cartesian_product_verified"])
        self.assertEqual(evidence["assembled_variant_count"], 45)
        self.assertEqual(
            evidence["call_variant_counts"],
            {"0:1": 5, "0:748": 3, "0:1174": 1, "0:460": 3},
        )
        assembled = BUILD.QA.TerminalRenderer(self.records).render((8, 1032))
        self.assertEqual(len(assembled), 45)
        for value in assembled:
            self.assertIn("에게도 병환이 들다니", value)
            self.assertIn("발휘하지 않", value)
            self.assertIn("폐를 끼쳐 ", value)
            self.assertNotIn("이(가)", value)

    def test_lure_plan_uses_the_proved_empty_terminal(self) -> None:
        components = BUILD.QA.tolerant_decode_record(self.records[(15, 1545)])
        calls = [
            tuple(component["target"])
            for component in components
            if component["kind"] == "call"
        ]
        self.assertEqual(calls, [(0, 1247), (0, 610)])
        self.assertEqual(
            BUILD.QA.TerminalRenderer(self.records).render((0, 1247)),
            ("",),
        )

    def test_wrapped_diplomacy_posture_has_invariant_direction(self) -> None:
        self.assertEqual(self.literals[(15, 1133, 2)], "」 쪽")
        self.assertEqual(
            self.report["regressions"]["15:1133"]["final_relation"],
            "quoted_dynamic_diplomacy_posture_direction",
        )

    def test_user_reported_clan_requests_have_left_separator(self) -> None:
        expected_literals = {
            (6, 3768): (
                "훗날 ",
                "에 원군 등\n군사적 ",
                "협력을 약조하겠소?\n",
                "",
                "",
            ),
            (6, 4917): (
                "훗날 ",
                "에 중재 등\n군사 ",
                "협력을 약조하겠소?\n",
                "",
                "",
            ),
        }
        for coordinate, expected in expected_literals.items():
            record = self.records[coordinate]
            components = BUILD.QA.tolerant_decode_record(record)
            self.assertEqual(
                [
                    (component["kind"], component.get("slot"))
                    for component in components[:2]
                ],
                [("literal_boundary", 0), ("selector", 0)],
            )
            self.assertEqual(int(components[1]["group"]), 4)
            self.assertEqual(int(components[1]["property"]), 0x32)
            self.assertEqual(self.literals[coordinate + (0,)], expected[0])
            self.assertEqual(self.literals[coordinate + (1,)], expected[1])
            self.assertEqual(self.literals[coordinate + (2,)], expected[2])
            self.assertEqual(self.literals[coordinate + (3,)], expected[3])
            self.assertEqual(self.literals[coordinate + (4,)], expected[4])
            calls = [
                tuple(component["target"])
                for component in components
                if component["kind"] == "call"
            ]
            self.assertIn((0, 1247), calls)

    def test_exact_semantic_rewrite_universes_are_pinned(self) -> None:
        self.assertEqual(
            len(BUILD.SEMANTIC_MIXED_REGISTER_REWRITES),
            BUILD.EXPECTED_MIXED_REGISTER_REWRITE_COUNT,
        )
        self.assertEqual(
            len(BUILD.SELECTOR_PERSON_REWRITES),
            BUILD.EXPECTED_SELECTOR_PERSON_REWRITE_COUNT,
        )
        self.assertEqual(
            len(BUILD.SELECTOR_LOCATION_REWRITES),
            BUILD.EXPECTED_SELECTOR_LOCATION_REWRITE_COUNT,
        )
        self.assertEqual(len(BUILD.FOREIGN_MERCHANT_ORTHOGRAPHY_REWRITES), 4)
        self.assertEqual(
            len(BUILD.INDEPENDENT_QA_REWRITES),
            BUILD.EXPECTED_INDEPENDENT_QA_LITERAL_REWRITE_COUNT,
        )
        self.assertEqual(
            len({coordinate[:2] for coordinate in BUILD.INDEPENDENT_QA_REWRITES}),
            BUILD.EXPECTED_INDEPENDENT_QA_SAMPLE_COUNT,
        )
        review = self.report["independent_language_review"]
        self.assertEqual(review["status"], "PASS")
        self.assertEqual(
            review["reported_defect_record_count"],
            BUILD.EXPECTED_INDEPENDENT_QA_DEFECT_RECORD_COUNT,
        )
        self.assertEqual(len(review["candidate_record_sha256"]), 33)
        self.assertTrue(review["all_reported_records_changed"])

    def test_exhaustive_remainder_universe_and_ownership_are_pinned(
        self,
    ) -> None:
        exact = frozenset(BUILD.EXHAUSTIVE_REMAINDER_EXACT_REWRITES)
        spacing = BUILD.EXHAUSTIVE_REMAINDER_SPACING_COORDINATES
        universe = exact | spacing
        self.assertFalse(exact & spacing)
        self.assertFalse(exact & frozenset(BUILD.BOUNDARY_CLOSURE_REWRITES))
        self.assertEqual(
            len(universe),
            BUILD.EXPECTED_EXHAUSTIVE_REMAINDER_ACTUAL_COUNT,
        )
        self.assertEqual(
            BUILD.coordinate_digest(universe),
            BUILD.EXPECTED_EXHAUSTIVE_REMAINDER_ACTUAL_COORDINATE_SHA256,
        )
        self.assertEqual(len(exact), 27)
        self.assertEqual(len(spacing), 94)
        for coordinate in spacing:
            self.assertTrue(
                self.literals[coordinate][:1].isspace(),
                coordinate,
            )

    def test_exhaustive_semantic_reconstructions_round_trip_exactly(
        self,
    ) -> None:
        expected = {
            (6, 4906, 0):
                " 장수는 현재 평정중에 임명된 무장입니다.\n"
                "계속하시겠습니까?",
            (7, 701, 0): "을 빼앗았다!",
            (7, 767, 1): "을 빼앗았다!",
            (7, 2023, 0): ", 각오하라!\n",
            (7, 2031, 1): ", 각오하라!",
            (9, 3570, 1):
                " 장수를 따르고 있구먼\n다가가려면 조심해야겠어",
            (9, 3572, 1):
                " 장수를 해칠 속셈인 듯하니\n경계해야 하옵니다",
            (9, 3573, 1):
                " 장수를 노리는 것일까요\n경계해 두도록 하지요",
            (9, 3575, 1):
                " 장수가 공격을 준비하는 낌새가 있으니\n"
                "강탈해 버리는 것도 재미있겠군요",
            (9, 3576, 1):
                " 장수를 노리는 것일까요\n경계해 두도록 하지요",
            (9, 3578, 1):
                " 장수를 노리는 것일까요\n조심해야겠습니다",
            (9, 3579, 1):
                " 장수가 공격을 준비하는 기색이 있소\n"
                "경계가 필요할 듯하오",
            (9, 3580, 1):
                " 장수를 노리는 것일까요\n조심해야겠습니다",
            (9, 4120, 0): ": 파괴하라",
            (9, 4125, 0): " 부대를 협격해 격파하라",
            (15, 1104, 3):
                " 두 가문의\n당가에 대한 인상이 나빠진 듯……",
            (15, 2067, 1): "의 전과는\n무관하여 송구하오나\n",
            (15, 2151, 1): "의 전과는\n무관하여 송구하오나\n",
            (17, 948, 0):
                ", 드, 드디어 마주했군…\n자, 그 목을 내놓아라",
        }
        for coordinate, text in expected.items():
            self.assertEqual(self.literals[coordinate], text)

        renderer = BUILD.QA.TerminalRenderer(self.records)
        for coordinate in ((9, 3576), (9, 3580)):
            variants = renderer.render(coordinate)
            self.assertTrue(variants)
            self.assertTrue(
                all(" 장수를 노리는" in value for value in variants),
                coordinate,
            )
            self.assertTrue(
                all("\uE000노리는" not in value for value in variants),
                coordinate,
            )

    def test_generic_and_relative_layout_gates_pass(self) -> None:
        quality = self.report["quality_gates"]
        self.assertEqual(quality["new_generic_carrier_count"], 0)
        self.assertTrue(
            quality["legal_target_ui"]["coordinate_set_preserved"]
        )
        layout = quality["raw_g1n_relative_layout"]
        self.assertFalse(layout["msgev_912px_absolute_gate_applied"])
        self.assertEqual(layout["line_count_increase_count"], 0)
        self.assertEqual(layout["ordinary_over_24px_count"], 0)
        self.assertEqual(
            layout["ordinary_plus_24px_over_block_max_count"],
            0,
        )
        self.assertEqual(layout["ordinary_plus_48px_or_more_count"], 0)
        expected_layout_exception_count = len(
            BUILD.APPROVED_LAYOUT_EXCEPTIONS
        )
        self.assertEqual(
            layout["approved_exact_exception_count"],
            expected_layout_exception_count,
        )
        guardrails = self.report["independent_candidate_guardrails"]
        self.assertEqual(guardrails["structure"]["issue_count"], 0)
        self.assertEqual(
            guardrails["structure"]["allowed_mutation_count"],
            BUILD.control_retarget_mutation_count(),
        )
        self.assertEqual(guardrails["relative_width"]["issue_count"], 0)
        self.assertEqual(
            guardrails["relative_width"][
                "approved_growth_exception_count"
            ],
            sum(
                1
                for coordinate in (
                    BUILD.RELATIVE_WIDTH.APPROVED_LINE_GROWTH_EXCEPTIONS
                )
                if coordinate[0] == "pk_msggame"
            ),
        )


if __name__ == "__main__":
    unittest.main()
