#!/usr/bin/env python3
"""Regressions for the opaque person-selector spacing audit."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


HERE = Path(__file__).resolve().parent
SPECIFICATION = importlib.util.spec_from_file_location(
    "opaque_person_selector_spacing_test_subject",
    HERE / "audit_opaque_person_selector_spacing_v1.py",
)
assert (
    SPECIFICATION is not None
    and SPECIFICATION.loader is not None
)
AUDIT = importlib.util.module_from_spec(SPECIFICATION)
sys.modules[SPECIFICATION.name] = AUDIT
SPECIFICATION.loader.exec_module(AUDIT)


class OpaquePersonSelectorSpacingTests(unittest.TestCase):
    def boundary_for(
        self,
        group: int,
        suffix: str,
    ):
        summary = AUDIT.compose(
            AUDIT.selector_summary(group),
            AUDIT.text_summary(suffix),
        )
        self.assertEqual(len(summary.selector_tails), 1)
        return AUDIT.tail_boundary(next(iter(summary.selector_tails)))

    def test_exact_no_space_nouns_are_detected_for_person_groups(self) -> None:
        expected = {
            "\uacf5\uc758": "honorific_gong",
            "\ub2d8\uaed8\uc11c": "honorific_nim",
            "\ub188\ub4e4": "hostile_nom",
        }
        for group in AUDIT.PERSON_LIKE_SELECTOR_GROUPS:
            for suffix, boundary_class in expected.items():
                self.assertEqual(
                    self.boundary_for(group, suffix),
                    (group, boundary_class),
                )

    def test_no_space_dependent_noun_is_detected_for_lexical_groups(
        self,
    ) -> None:
        for group in AUDIT.LEXICAL_SELECTOR_GROUPS:
            self.assertEqual(
                self.boundary_for(group, "\uc544\ub798\uc5d0"),
                (group, "dependent_arae"),
            )

    def test_space_prevents_the_boundary(self) -> None:
        for suffix in (
            " \uacf5",
            " \ub2d8",
            " \ub188",
            " \uc544\ub798",
        ):
            self.assertIsNone(self.boundary_for(2, suffix))

    def test_attached_families_and_particles_are_not_targeted(self) -> None:
        allowed = (
            "\uc81c2\ub144",
            "2\ubc88\uc9f8",
            "\uc774",
            "\uac00",
            "\uc740",
            "\ub294",
            "\uc744",
            "\ub97c",
            "\uacfc",
            "\uc640",
            "\uac00\ubb38",
            "\uc131",
            "\uad70",
            "\uacf5\uaca9",
            "\uacf5\ub7b5",
            "\uacf5\uc791",
        )
        for suffix in allowed:
            self.assertIsNone(self.boundary_for(2, suffix), suffix)

    def test_non_lexical_selector_never_creates_a_selector_tail(
        self,
    ) -> None:
        for group in (0, 14):
            summary = AUDIT.compose(
                AUDIT.selector_summary(group),
                AUDIT.text_summary("\ub2d8\uaed8\uc11c"),
            )
            self.assertFalse(summary.selector_tails)

    def test_non_person_lexical_selector_ignores_honorifics(self) -> None:
        for group in (3, 4, 7, 10, 13):
            for suffix in ("\uacf5\uc758", "\ub2d8\uaed8", "\ub188\ub4e4"):
                self.assertIsNone(self.boundary_for(group, suffix))

    def test_reviewed_lexical_prefixes_use_exact_group_policy(self) -> None:
        self.assertEqual(
            self.boundary_for(3, "\uacf5\uaca9\uc774"),
            (3, "action_gonggyeok"),
        )
        self.assertIsNone(self.boundary_for(2, "\uacf5\uaca9\uc774"))
        self.assertEqual(
            self.boundary_for(4, "\ub530\uc704\ub294"),
            (4, "dependent_ttawi"),
        )
        self.assertEqual(
            self.boundary_for(1, "\ub178\ub9ac\ub294 \uac83"),
            (1, "carrier_norineun"),
        )
        self.assertIsNone(self.boundary_for(1, "\ud589 \uc9c4\uad70"))
        self.assertIsNone(self.boundary_for(1, "\uc9c1\uc744 \ubc30\ub839"))

    def test_symbolic_composition_crosses_call_like_boundaries(self) -> None:
        person_caller = AUDIT.selector_summary(2)
        empty_branch = AUDIT.text_summary("")
        suffix_branch = AUDIT.text_summary("\ub2d8\uc740")
        called_language = AUDIT.union_summaries(
            (empty_branch, suffix_branch)
        )
        rendered = AUDIT.compose(person_caller, called_language)
        verdicts = {
            AUDIT.tail_boundary(tail)
            for tail in rendered.selector_tails
        }
        self.assertIn((2, "honorific_nim"), verdicts)
        self.assertIn(None, verdicts)

    def test_truncated_tail_is_not_treated_as_end_of_output(self) -> None:
        incomplete = AUDIT.Fragment(
            AUDIT.SELECTOR_MARKERS[2] + "\ub2d8",
            False,
        )
        complete = AUDIT.Fragment(
            AUDIT.SELECTOR_MARKERS[2] + "\ub2d8",
            True,
        )
        self.assertIsNone(AUDIT.tail_boundary(incomplete))
        self.assertEqual(
            AUDIT.tail_boundary(complete),
            (2, "honorific_nim"),
        )

    def test_ghidra_and_repository_policy_evidence_is_live(self) -> None:
        evidence = AUDIT.load_evidence_contract()
        self.assertTrue(evidence["copy_verbatim"])
        self.assertFalse(evidence["automatic_space_inserted"])
        self.assertTrue(evidence["honorific_suffix_policy_validated"])
        self.assertTrue(evidence["tono_spacing_policy_validated"])
        self.assertTrue(evidence["person_like_selector_policy_validated"])
        self.assertTrue(evidence["lexical_selector_policy_validated"])
        for key in (
            "ghidra_selector_contract_sha256",
            "base_honorific_policy_sha256",
            "pk_honorific_policy_sha256",
            "base_person_selector_policy_sha256",
            "pk_person_selector_policy_sha256",
            "runtime_lexical_selector_policy_sha256",
        ):
            self.assertRegex(evidence[key], r"^[0-9A-F]{64}$")

    def test_strict_mode_fails_and_report_stays_source_free(self) -> None:
        issue = AUDIT.OpaqueSelectorSpacingIssue(
            resource="base_msggame",
            block_id=1,
            record_id=2,
            selector_group=2,
            boundary_class="honorific_nim",
            opaque_tail_sha256="A" * 64,
            tail_complete=True,
        )
        dirty = AUDIT.OpaqueSelectorResource(
            resource="base_msggame",
            path="base.bin",
            sha256="B" * 64,
            size=1,
            record_count=1,
            decoded_record_count=1,
            selector_component_count=1,
            lexical_selector_component_count=1,
            lexical_selector_record_count=1,
            person_selector_component_count=1,
            person_selector_record_count=1,
            symbolic_prefix_state_count=1,
            symbolic_selector_tail_state_count=1,
            issues=(issue,),
        )
        clean = AUDIT.OpaqueSelectorResource(
            resource="pk_msggame",
            path="pk.bin",
            sha256="C" * 64,
            size=1,
            record_count=1,
            decoded_record_count=1,
            selector_component_count=0,
            lexical_selector_component_count=0,
            lexical_selector_record_count=0,
            person_selector_component_count=0,
            person_selector_record_count=0,
            symbolic_prefix_state_count=1,
            symbolic_selector_tail_state_count=0,
            issues=(),
        )
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "report.json"
            with mock.patch.object(
                AUDIT,
                "audit_resource",
                side_effect=(dirty, clean),
            ):
                result = AUDIT.main(
                    [
                        "--base",
                        "base.bin",
                        "--pk",
                        "pk.bin",
                        "--output",
                        str(output),
                        "--strict",
                    ]
                )
            self.assertEqual(result, 1)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(report["issue_count"], 1)
            self.assertNotIn("opaque_tail", report["issues"][0])
            serialized = json.dumps(report, ensure_ascii=True)
            self.assertFalse(any(ord(character) > 127 for character in serialized))


if __name__ == "__main__":
    unittest.main()
