#!/usr/bin/env python3
"""Deterministic regression tests for the Base runtime-surface remediation."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "base_runtime_surface_remediation",
    HERE / "base_build_runtime_surface_remediation_v1.py",
)
assert SPEC is not None and SPEC.loader is not None
BUILD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILD
SPEC.loader.exec_module(BUILD)


class BaseRuntimeSurfaceRemediationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (
            cls.candidate,
            cls.overlay,
            cls.surface_audit,
            cls.terminal_audit,
            cls.layout_report,
            cls.report,
        ) = BUILD.build()
        cls.records = BUILD.records_from_blob(cls.candidate)
        cls.overlay_payload = json.loads(cls.overlay)

    def test_candidate_closes_all_surface_and_terminal_gates(self) -> None:
        self.assertEqual(self.report["status"], "PASS")
        candidate = self.report["candidate"]
        self.assertEqual(candidate["surface_issue_count"], 0)
        self.assertEqual(candidate["terminal_boundary_issue_count"], 0)
        self.assertEqual(
            candidate["call_semantic_carrier_artifact_issue_count"],
            0,
        )
        self.assertEqual(
            candidate["selector_semantic_carrier_artifact_issue_count"],
            0,
        )
        self.assertEqual(
            candidate["sha256"],
            "ADB73561AAA10A66364B3C09B2184BB29698186C808E0FE264C64B1DD2A5A4FE",
        )

    def test_reported_cartesian_sentences_are_finite_in_every_branch(
        self,
    ) -> None:
        renderer = BUILD.QA.TerminalRenderer(self.records)
        coordinates = (
            (15, 268),
            (15, 921),
            (15, 2145),
            (15, 2146),
            (15, 2150),
            (15, 2154),
        )
        forbidden = (
            "인가 하고",
            "쉽다입니다",
            "쉽다다",
            "쉽다이오",
            "질문하오?",
            "질문하다?",
            "들으시오?",
            "들으시다?",
            "보고하겠습니다?",
            "보고하겠다?",
            "보고하자?",
        )
        for coordinate in coordinates:
            rendered = renderer.render(coordinate)
            self.assertTrue(rendered, coordinate)
            for value in rendered:
                for fragment in forbidden:
                    self.assertNotIn(fragment, value, (coordinate, value))
        self.assertEqual(
            renderer.render((15, 268)),
            (
                "아마 잘될 것이겠지요",
                "아마 잘될 것이리라",
                "아마 잘될 것이겠지",
            ),
        )

    def test_incomplete_kato_terminal_has_no_body_callers(self) -> None:
        callers = []
        for coordinate, record in self.records.items():
            if coordinate[0] == 0:
                continue
            for component in BUILD.QA.tolerant_decode_record(record):
                if (
                    component["kind"] == "call"
                    and tuple(component["target"]) == (0, 286)
                ):
                    callers.append(coordinate)
        self.assertEqual(callers, [])

    def test_reported_direct_static_sentences_are_closed(self) -> None:
        renderer = BUILD.QA.TerminalRenderer(self.records)
        expected = {
            (6, 4150):
                "주변에 공략할 수 있는 성이 없어\n"
                "영지 발전에 힘쓰고 있습니다",
            (8, 1036):
                "마목장을 건설하여\n"
                "이로써 많은 준마가 자라나\n"
                "기병도 한층 정예해질 것입니다",
            (8, 1038):
                "절을 건설하여\n"
                "백성들이 마음을 기댈 곳이 되어\n"
                "승려들도 기쁨을 감추지 못하는 듯합니다",
            (8, 1040):
                "온천향을 건설하여\n"
                "아무래도 부상 치료에 효험이 있어\n"
                "병사들의 요양에도 도움이 될 것입니다",
            (8, 1041):
                "대농촌을 건설하여\n"
                "광활한 농지를 본 백성들도 의욕이 넘치니\n"
                "수확량은 물론 병사 수도 기대할 수 있습니다",
        }
        for coordinate, text in expected.items():
            self.assertEqual(renderer.render(coordinate), (text,))
        closure = self.report["candidate"][
            "direct_static_sentence_closure"
        ]
        self.assertEqual(closure["changed_record_count"], 48)
        self.assertEqual(closure["replacement_count"], 77)
        self.assertEqual(closure["pre_gate_issue_count"], 54)
        self.assertEqual(closure["post_gate_issue_count"], 0)

    def test_build_is_byte_for_byte_deterministic(self) -> None:
        second = BUILD.build()
        self.assertEqual(second[0], self.candidate)
        self.assertEqual(second[1], self.overlay)
        self.assertEqual(second[2], self.surface_audit)
        self.assertEqual(second[3], self.terminal_audit)
        self.assertEqual(second[4], self.layout_report)
        self.assertEqual(
            BUILD.canonical_json(second[5]),
            BUILD.canonical_json(self.report),
        )

    def test_bulk_relative_layout_has_no_general_exception(self) -> None:
        document = json.loads(self.layout_report)
        bulk = document["bulk_relative_layout"]
        self.assertEqual(bulk["status"], "PASS")
        self.assertEqual(bulk["line_count_change_count"], 0)
        self.assertEqual(bulk["line_count_expansion_count"], 0)
        self.assertEqual(bulk["over_24_raw_g1n_count"], 0)
        self.assertEqual(
            bulk["plus_24_over_predecessor_block_max_count"],
            0,
        )
        self.assertEqual(bulk["maximum_positive_delta_raw_g1n"], 24)
        spacing = document["selector_left_spacing_relative_layout"]
        self.assertEqual(spacing["status"], "PASS")
        self.assertEqual(spacing["changed_coordinate_count"], 2051)
        self.assertEqual(spacing["line_count_change_count"], 0)
        self.assertEqual(spacing["over_24_raw_g1n_count"], 0)
        self.assertEqual(
            spacing["plus_24_over_predecessor_block_max_count"],
            0,
        )
        self.assertEqual(spacing["maximum_positive_delta_raw_g1n"], 24)
        person_suffix = document[
            "person_suffix_spacing_relative_layout"
        ]
        self.assertEqual(person_suffix["status"], "PASS")
        self.assertEqual(person_suffix["changed_coordinate_count"], 346)
        self.assertEqual(person_suffix["line_count_change_count"], 0)
        self.assertEqual(person_suffix["over_24_raw_g1n_count"], 0)
        self.assertEqual(
            person_suffix[
                "plus_24_over_predecessor_block_max_count"
            ],
            0,
        )
        self.assertEqual(
            person_suffix["maximum_positive_delta_raw_g1n"],
            24,
        )
        approved = document["priority_approved_exceptions"]
        self.assertEqual(approved["approved_exception_count"], 2)
        self.assertFalse(approved["generalized_exception_policy"])
        self.assertEqual(
            {
                (
                    row["coordinate"],
                    row["line_index"],
                    row["before_width_raw_g1n"],
                    row["after_width_raw_g1n"],
                    row["delta_raw_g1n"],
                )
                for row in approved["rows"]
            },
            {
                ("2:142:0", 0, 432, 528, 96),
                ("8:1020:1", 0, 192, 528, 336),
            },
        )

    def test_no_new_generic_person_noun_is_automatic(self) -> None:
        audit = self.report["overlay"][
            "introduced_generic_noun_audit"
        ]
        self.assertEqual(
            audit["term_counts"],
            {"대상": 0, "인물": 0, "분": 0, "장수": 1},
        )
        self.assertEqual(audit["unapproved_count"], 0)
        self.assertEqual(
            [
                (row["term"], row["coordinate"])
                for row in audit["approved_role_nouns"]
            ],
            [("장수", "15:1642:1")],
        )
        semantic = self.report["overlay"][
            "introduced_semantic_boundary_audit"
        ]
        self.assertEqual(semantic["introduced_marker_count"], 0)

    def test_priority_coordinates_are_not_in_bulk_overlay(self) -> None:
        bulk_coordinates = {
            (
                int(row["block_id"]),
                int(row["record_id"]),
                int(row["literal_id"]),
            )
            for row in self.overlay_payload["entries"]
        }
        priority = BUILD.load_priority_replacements(
            BUILD.SOURCE_BASE.read_bytes()
        )
        self.assertTrue(set(priority).isdisjoint(bulk_coordinates))
        self.assertEqual(len(priority), 6)

    def test_sick_person_runtime_cartesian_product_is_exact(self) -> None:
        candidate = self.report["candidate"]
        self.assertEqual(
            candidate["base_8_1020_rendered_branch_count"],
            60,
        )
        self.assertTrue(
            candidate["honorific_call_assembly"][
                "all_nonempty_branches_exact_assembled"
            ]
        )

    def test_user_reported_runtime_dialogues_are_exact(self) -> None:
        renderer = (
            BUILD.CALL_REMEDIATION.CALL_QA.SyntheticSelectorRenderer(
                self.records
            )
        )
        sick_intro = (
            "콜록, 콜록…\n몸을 돌보지 않은 탓인 듯합니다…",
        )
        sick_report = (
            "으윽, 병에 걸린 모양입니다…\n"
            "반드시 회복하겠습니다. 그러므로, 잠시 시간을…",
        )
        personas = ("소승", "나", "저", "소인", "이 몸")
        negatives = ("않습니다", "않는다", "않사옵니다")
        apologies = (
            "죄송합니다",
            "미안하오",
            "면목이 없습니다",
            "송구하옵니다",
        )
        sick_variants = tuple(
            "하아… 설마, "
            f"{persona}에게도 병환이 들다니…\n"
            f"…당분간은 제 힘을 발휘하지 {negative}\n"
            f"폐를 끼쳐 {apology}…"
            for persona in personas
            for negative in negatives
            for apology in apologies
        )
        self.assertEqual(renderer.render((8, 1018)), sick_intro)
        self.assertEqual(renderer.render((8, 1019)), sick_report)
        self.assertEqual(renderer.render((8, 1020)), sick_variants)
        self.assertEqual(
            renderer.render((8, 107)),
            sick_intro + sick_report + sick_variants,
        )
        self.assertEqual(
            renderer.render((6, 3761)),
            (
                "훗날 도쿠가와 가문에게 원군이나 중재 등\n"
                "군사적 협력을 청하고자…\n"
                "약속하시겠습니까?",
            ),
        )

    def test_user_reported_clan_request_has_left_separator(self) -> None:
        record = self.records[(6, 3761)]
        literals = [
            value.text for value in BUILD.parse_record_literals(record)
        ]
        self.assertEqual(literals[0], "훗날 ")
        self.assertTrue(literals[1].startswith("에게 원군"))
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
        self.assertEqual(
            "훗날 " + "도쿠가와 가문" + literals[1],
            "훗날 도쿠가와 가문에게 원군이나 중재 등\n군사적 ",
        )

    def test_hot_spring_two_call_assembly_is_not_fragmented(self) -> None:
        rendered = BUILD.QA.TerminalRenderer(self.records).render((8, 1188))
        self.assertEqual(len(rendered), 12)
        self.assertEqual(
            self.report["candidate"]["base_8_1188_rendered_branch_count"],
            12,
        )
        for value in rendered:
            self.assertIn("온천향을 조성하려고 생각", value)
            self.assertIn(".계", value)
            self.assertTrue(value.endswith("만"))
            self.assertNotIn(".안", value)
            self.assertNotIn("안다", value)

    def test_foreign_trader_speech_is_natural_and_exact(self) -> None:
        expected_literals = {
            (6, 1149): [
                "먼저 남만 상관을 지어 주십시오\n"
                "이야기는 그다음입니다",
            ],
            (6, 1150): [
                "안녕하십니까\n"
                "철포는 얼마나 필요합니까",
            ],
            (6, 1153): [
                "구매해 주셔서 감사합니다\n철포 ",
                " 수령 바랍니다",
            ],
        }
        expected_rendered = {
            (6, 1149): (
                "먼저 남만 상관을 지어 주십시오\n"
                "이야기는 그다음입니다",
            ),
            (6, 1150): (
                "안녕하십니까\n철포는 얼마나 필요합니까",
            ),
            (6, 1153): (
                "구매해 주셔서 감사합니다\n철포  수령 바랍니다",
            ),
        }
        for coordinate, literals in expected_literals.items():
            self.assertEqual(
                [
                    value.text
                    for value in BUILD.parse_record_literals(
                        self.records[coordinate]
                    )
                ],
                literals,
            )
            rendered = BUILD.QA.TerminalRenderer(self.records).render(
                coordinate
            )
            self.assertEqual(rendered, expected_rendered[coordinate])
            self.assertNotIn("요오", "".join(rendered))
        self.assertEqual(
            self.report["input"]["live_source_category_counts"][
                "literal_orthography_artifact"
            ],
            4,
        )

    def test_person_selector_recasts_and_first_merit_lines_are_exact(
        self,
    ) -> None:
        method = (
            "person_selector_exact_context_reconstruction:"
            "dynamic_selector_followed_by_unreviewed_person_carrier"
        )
        self.assertEqual(
            self.report["overlay"]["method_counts"][method],
            264,
        )
        self.assertEqual(
            self.report["candidate"][
                "selector_semantic_carrier_artifact_issue_count"
            ],
            0,
        )
        expected = {
            (9, 2547): [
                "의 선봉 공적이다!\n따르라!　돌격하라!",
            ],
            (9, 2549): [
                "이 몸―",
                "의\n선봉 공적입니다!",
            ],
            (9, 2556): [
                "이 몸―",
                "의\n선봉 공적입니다",
            ],
            (9, 2557): [
                "이 몸―",
                "의\n선봉 공적이다!",
            ],
        }
        for coordinate, literals in expected.items():
            self.assertEqual(
                [
                    value.text
                    for value in BUILD.parse_record_literals(
                        self.records[coordinate]
                    )
                ],
                literals,
            )

    def test_selector_left_spacing_and_reported_diplomacy_are_exact(
        self,
    ) -> None:
        overlay = self.report["overlay"]
        self.assertEqual(
            overlay["selector_left_spacing_repair_count"],
            2051,
        )
        self.assertEqual(
            overlay["selector_left_spacing_repair_coordinate_sha256"],
            "020A5146BF8D83744F4233CDB475E30B7CDBD2F215F6C84BC999775FAA6DE66A",
        )
        self.assertEqual(
            overlay["selector_left_width_compaction_count"],
            100,
        )
        self.assertEqual(
            overlay["selector_left_width_compaction_coordinate_sha256"],
            "766E0052AA3FEE9FAF80AA1DE67DF71B1051C2A33099746A1A2AB21B365A92D1",
        )
        self.assertEqual(
            [
                literal.text
                for literal in BUILD.parse_record_literals(
                    self.records[(6, 3761)]
                )
            ][0],
            "훗날 ",
        )
        assembly = self.report["candidate"][
            "base_6_3761_reported_runtime_assembly"
        ]
        self.assertEqual(assembly["rendered_branch_count"], 3)
        self.assertEqual(
            assembly["rendered_branch_sha256"],
            "47DEC557FEF04F5D23ECF63D0920F5E42CA1D883EA89570E1FE2DD6DAF7300AF",
        )

    def test_person_name_suffix_spacing_is_exhaustive(self) -> None:
        spacing = self.report["candidate"]["person_suffix_spacing"]
        self.assertEqual(
            spacing["ghidra_person_like_selector_groups"],
            [1, 2, 5, 6],
        )
        self.assertEqual(spacing["direct_repair_count"], 230)
        self.assertEqual(
            spacing["direct_coordinate_sha256"],
            "0B2F53260ADD26C1566A237B88A4CDFF842B4994F496F7BF537AB5E13001A03C",
        )
        self.assertEqual(spacing["terminal_leaf_repair_count"], 5)
        self.assertEqual(
            spacing["terminal_leaf_coordinate_sha256"],
            "F5ACB241DFE20CBD25E338CC4F283E3DAF07531636FFCC2E3501AEEE5D61CD7C",
        )
        self.assertEqual(spacing["lexical_boundary_repair_count"], 1)
        self.assertEqual(
            spacing["lexical_boundary_coordinate_sha256"],
            "F5B58EA3D5BC5996711A9BA466F666A2DEBFD9324C92E27EDDE8614C82BC873C",
        )
        self.assertEqual(spacing["selector_lexeme_repair_count"], 64)
        self.assertEqual(
            spacing["selector_lexeme_coordinate_sha256"],
            "37AD892D30D402FEA6A99D7A914F4816E7C294BDF051AF79430F22CFDF8CC90A",
        )
        self.assertEqual(
            spacing["selector_remainder_actual_repair_count"],
            46,
        )
        self.assertEqual(
            spacing["selector_remainder_actual_coordinate_sha256"],
            "222C8B88335B90757E606B28A1B2BDF58F6742E6016622048189925D77E97A6D",
        )
        self.assertEqual(spacing["replacement_count"], 346)
        self.assertEqual(
            spacing["replacement_coordinate_sha256"],
            "42660243E2576C3F8650D47C05F11E8327D290047AA1431D4FB4E19538F2A28E",
        )
        self.assertEqual(
            spacing["suffix_counts"],
            {"공": 9, "님": 191, "놈": 35},
        )
        final_audit = spacing["final_audit"]
        self.assertEqual(final_audit["direct_boundary_issue_count"], 0)
        self.assertEqual(final_audit["lexical_boundary_issue_count"], 0)
        self.assertEqual(final_audit["selector_lexeme_issue_count"], 0)
        self.assertEqual(
            final_audit["selector_remainder_actual_issue_count"],
            0,
        )
        self.assertEqual(final_audit["rendered_issue_root_count"], 0)
        self.assertEqual(
            final_audit["rendered_selector_lexeme_issue_root_count"],
            0,
        )
        self.assertTrue(
            final_audit["all_person_name_suffix_boundaries_spaced"]
        )
        self.assertEqual(
            [
                literal.text
                for literal in BUILD.parse_record_literals(
                    self.records[(6, 2979)]
                )
            ][1],
            " 님",
        )
        self.assertTrue(
            [
                literal.text
                for literal in BUILD.parse_record_literals(
                    self.records[(15, 2263)]
                )
            ][1].startswith(" 아래에"),
        )
        for record_id in (2339, 2340, 2343, 2344, 2414):
            self.assertEqual(
                [
                    literal.text
                    for literal in BUILD.parse_record_literals(
                        self.records[(0, record_id)]
                    )
                ],
                [" 놈"],
            )

    def test_semantic_review_keeps_only_154_valid_rows(self) -> None:
        self.assertEqual(len(BUILD.load_blocks1_7_review()), 154)


if __name__ == "__main__":
    unittest.main()
