#!/usr/bin/env python3
"""Boundary tests for the PK thought-predicate family closure layer."""

from __future__ import annotations

import copy
import importlib.util
import json
import re
import sys
import unittest
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
MODULE_PATH = (
    SCRIPT.parent
    / "build_pk_thought_predicate_family_exact_closure_v1.py"
)


def load_module() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pk_thought_predicate_family_exact_closure_test_subject",
        MODULE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class ThoughtPredicateFamilyExactClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (
            cls.decision_content,
            cls.evidence_content,
            cls.audit_content,
            cls.promotion_content,
            cls.audit,
            cls.bundle,
        ) = MODULE.build_outputs()
        MODULE.validate_outputs(
            decision_content=cls.decision_content,
            evidence_content=cls.evidence_content,
            audit_content=cls.audit_content,
            promotion_content=cls.promotion_content,
            audit=cls.audit,
            bundle=cls.bundle,
        )

    def test_7777aa7_predecessor_and_candidate_are_frozen(self) -> None:
        self.assertEqual(
            self.audit["predecessor"]["git_commit"],
            MODULE.PREDECESSOR_COMMIT,
        )
        self.assertEqual(
            self.audit["predecessor"]["pending_rows"],
            MODULE.EXPECTED_PREDECESSOR_PENDING,
        )
        self.assertEqual(
            self.audit["predecessor"]["merged_private_sha256"],
            MODULE.EXPECTED_PREDECESSOR_MERGED_SHA256,
        )
        self.assertEqual(
            self.audit["guards"][
                "pk_predecessor_candidate_packed_sha256"
            ],
            MODULE.EXPECTED_PK_PREDECESSOR_CANDIDATE_SHA256,
        )
        self.assertEqual(
            self.audit["guards"]["pk_candidate_packed_sha256"],
            MODULE.EXPECTED_PK_CANDIDATE_SHA256,
        )

    def test_exact_seventy_five_translation_overrides(self) -> None:
        analysis = self.bundle["analysis"]
        overrides = analysis["overrides"]
        self.assertEqual(len(overrides), MODULE.EXPECTED_TRANSLATION_OVERRIDES)
        self.assertEqual(
            set(overrides),
            (
                set(MODULE.SUFFIX_RULES)
                | set(MODULE.CURRENT_AUTHORITY_OVERRIDES)
                | set(MODULE.TERMINAL_OVERRIDES)
            ),
        )
        self.assertNotIn(MODULE.UNCHANGED_DISPLAY_CALLER, overrides)
        for coordinate, expected in MODULE.CURRENT_AUTHORITY_OVERRIDES.items():
            self.assertEqual(overrides[coordinate], expected)
        for coordinate, expected in MODULE.TERMINAL_OVERRIDES.items():
            self.assertEqual(overrides[coordinate], expected)
        for coordinate, (old_suffix, new_suffix) in (
            MODULE.SUFFIX_RULES.items()
        ):
            predecessor = analysis["override_basis"][coordinate]
            self.assertTrue(predecessor.endswith(old_suffix))
            self.assertEqual(
                overrides[coordinate],
                predecessor[: -len(old_suffix)] + new_suffix,
            )
        self.assertEqual(
            self.audit["guards"]["override_coordinate_sha256"],
            MODULE.EXPECTED_OVERRIDE_COORDINATE_SHA256,
        )
        self.assertEqual(
            self.audit["guards"]["override_manifest_sha256"],
            MODULE.EXPECTED_OVERRIDE_MANIFEST_SHA256,
        )

    def test_all_483_display_assemblies_are_grammar_and_width_safe(
        self,
    ) -> None:
        analysis = self.bundle["analysis"]
        self.assertEqual(
            len(analysis["callers"]),
            MODULE.EXPECTED_DISPLAY_CALLERS,
        )
        self.assertEqual(
            len(analysis["assembly_manifest"]),
            MODULE.EXPECTED_DISPLAY_ASSEMBLIES,
        )
        self.assertNotIn(MODULE.NON_DISPLAY_CALLER, analysis["callers"])
        self.assertIn(
            MODULE.UNCHANGED_DISPLAY_CALLER,
            analysis["callers"],
        )
        for entry in analysis["assembly_manifest"]:
            self.assertEqual(
                len(entry["current_line_widths_raw_g1n"]),
                len(entry["final_line_widths_raw_g1n"]),
            )
            self.assertTrue(
                all(
                    final <= current
                    for current, final in zip(
                        entry["current_line_widths_raw_g1n"],
                        entry["final_line_widths_raw_g1n"],
                    )
                )
            )
        self.assertEqual(
            analysis["assembly_manifest_sha256"],
            MODULE.EXPECTED_ASSEMBLY_MANIFEST_SHA256,
        )
        adjudication = self.audit["adjudication"]
        self.assertTrue(adjudication["all_483_assemblies_grammar_complete"])
        self.assertTrue(
            adjudication[
                "all_483_assemblies_actual_current_relative_nonexpanding"
            ]
        )
        self.assertFalse(adjudication["one_absolute_widget_gate_assumed"])
        self.assertFalse(adjudication["pk_msgev_912px_rule_applied"])

    def test_pending_promotions_and_verified_renewals_are_exact(self) -> None:
        rows = self.bundle["updated_rows"]
        actions = Counter(
            str(row["thought_predicate_family_update_action"])
            for row in rows
        )
        self.assertEqual(
            actions,
            {
                "translation_override_and_runtime_promotion": 22,
                "runtime_promotion": 1,
                "translation_override_and_verification_renewal": 53,
            },
        )
        promoted = [
            row for row in rows
            if row["thought_predicate_family_update_action"]
            in {
                "translation_override_and_runtime_promotion",
                "runtime_promotion",
            }
        ]
        renewed = [
            row for row in rows
            if row["thought_predicate_family_update_action"]
            == "translation_override_and_verification_renewal"
        ]
        self.assertEqual(
            len(promoted),
            MODULE.EXPECTED_PENDING_ELIGIBLE_ROWS,
        )
        self.assertEqual(
            len(renewed),
            MODULE.EXPECTED_VERIFIED_RENEWAL_ROWS,
        )
        self.assertTrue(
            all(row["runtime_review"] == "verified" for row in rows)
        )
        self.assertEqual(
            MODULE.coordinate_digest(
                str(row["coordinate"]) for row in promoted
            ),
            MODULE.EXPECTED_PENDING_COORDINATE_SHA256,
        )
        self.assertEqual(
            MODULE.coordinate_digest(
                str(row["coordinate"]) for row in renewed
            ),
            MODULE.EXPECTED_RENEWAL_COORDINATE_SHA256,
        )

    def test_delta_merges_to_pending_8618_and_rejected_zero(self) -> None:
        merged = {
            key: copy.deepcopy(dict(row))
            for key, row in self.bundle["analysis"][
                "predecessor_rows"
            ].items()
        }
        merged.update(
            {
                (str(row["resource"]), str(row["coordinate"])): row
                for row in self.bundle["updated_rows"]
            }
        )
        pending = [
            row for row in merged.values()
            if row.get("runtime_review") == "pending"
        ]
        self.assertEqual(len(pending), MODULE.EXPECTED_POST_LAYER_PENDING)
        self.assertEqual(
            self.audit["scope"]["rejected_rows"],
            MODULE.EXPECTED_REJECTED_ROWS,
        )
        self.assertEqual(
            self.bundle["promotion"]["result"]["pending_rows_after"],
            MODULE.EXPECTED_POST_LAYER_PENDING,
        )

    def test_private_evidence_has_no_translation_bodies(self) -> None:
        evidence_rows = self.bundle["evidence_rows"]
        self.assertEqual(
            len(evidence_rows),
            MODULE.EXPECTED_DISPLAY_CLOSURE_ROWS,
        )
        for evidence in evidence_rows:
            self.assertNotIn("translation", evidence)
            self.assertFalse(evidence["per_row_game_playback_required"])
            self.assertTrue(evidence["full_incoming_closure_verified"])
            self.assertTrue(evidence["grammar_complete_for_all_registers"])
            self.assertTrue(
                evidence["actual_current_relative_nonexpanding"]
            )
        self.assertNotRegex(self.evidence_content, r'"translation"\s*:')

    def test_tracked_reports_are_source_free_and_outputs_match_disk(
        self,
    ) -> None:
        self.assertNotRegex(
            self.audit_content + self.promotion_content,
            re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7a3]"),
        )
        self.assertNotIn('"translation":', self.audit_content)
        self.assertNotIn('"translation":', self.promotion_content)
        expected = {
            MODULE.DEFAULT_DECISION_OUTPUT: self.decision_content,
            MODULE.DEFAULT_EVIDENCE_OUTPUT: self.evidence_content,
            MODULE.DEFAULT_AUDIT_OUTPUT: self.audit_content,
            MODULE.DEFAULT_PROMOTION_OUTPUT: self.promotion_content,
        }
        for path, content in expected.items():
            self.assertTrue(path.is_file(), path)
            self.assertEqual(path.read_text(encoding="utf-8"), content)
        self.assertFalse(self.audit["steam_write_performed"])
        self.assertFalse(
            self.bundle["promotion"]["steam_write_performed"]
        )

    def test_output_hashes_are_frozen(self) -> None:
        self.assertEqual(
            MODULE.sha256_bytes(self.audit_content.encode("utf-8")),
            MODULE.EXPECTED_AUDIT_FILE_SHA256,
        )
        self.assertEqual(
            MODULE.sha256_bytes(self.promotion_content.encode("utf-8")),
            MODULE.EXPECTED_PROMOTION_FILE_SHA256,
        )
        self.assertEqual(
            MODULE.sha256_bytes(self.decision_content.encode("utf-8")),
            MODULE.EXPECTED_DECISION_FILE_SHA256,
        )
        self.assertEqual(
            MODULE.sha256_bytes(self.evidence_content.encode("utf-8")),
            MODULE.EXPECTED_EVIDENCE_FILE_SHA256,
        )


if __name__ == "__main__":
    unittest.main()
