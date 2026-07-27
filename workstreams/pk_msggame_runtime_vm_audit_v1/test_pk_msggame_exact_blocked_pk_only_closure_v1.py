#!/usr/bin/env python3
"""Regression and tamper tests for the independent exact-blocked PK layer."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
BUILDER_PATH = (
    WORKSTREAM / "build_pk_msggame_exact_blocked_pk_only_closure_v1.py"
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = load_module(
    "pk_exact_blocked_pk_only_closure_test_builder",
    BUILDER_PATH,
)


class PkExactBlockedPkOnlyClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (
            cls.audit_content,
            cls.private_content,
            cls.promotion_content,
            cls.audit,
            cls.promotion,
            cls.context,
        ) = BUILDER.build_outputs()
        cls.rows = [
            json.loads(line)
            for line in cls.private_content.splitlines()
            if line
        ]

    def test_exact_split_and_upstream_bindings(self) -> None:
        scope = self.audit["scope"]
        self.assertEqual(scope["full_candidate_blocked_rows"], 2_317)
        self.assertEqual(scope["full_candidate_blocked_records"], 1_616)
        self.assertEqual(scope["pk_only_promotion_eligible_rows"], 1_533)
        self.assertEqual(
            scope["pk_only_promotion_eligible_records"],
            1_126,
        )
        self.assertEqual(scope["manual_review_remaining_rows"], 784)
        self.assertEqual(scope["manual_review_remaining_records"], 490)
        self.assertEqual(
            self.audit["guards"]["eligible_coordinate_universe_sha256"],
            BUILDER.EXPECTED_SAFE_COORDINATE_SHA256,
        )
        self.assertEqual(
            self.audit["guards"]["remaining_coordinate_universe_sha256"],
            BUILDER.EXPECTED_REMAINING_COORDINATE_SHA256,
        )
        self.assertEqual(
            self.audit["guards"]["integrated_private_sha256"],
            BUILDER.EXPECTED_INTEGRATED_PRIVATE_SHA256,
        )
        self.assertEqual(
            self.audit["guards"]["full_coverage_file_sha256"],
            BUILDER.EXPECTED_FULL_COVERAGE_FILE_SHA256,
        )
        self.assertEqual(
            self.audit["guards"]["semantic_override_public_sha256"],
            BUILDER.EXPECTED_SEMANTIC_OVERRIDE_PUBLIC_SHA256,
        )

    def test_overlay_is_complete_source_free_and_pk_only(self) -> None:
        self.assertEqual(len(self.rows), 1_533)
        self.assertEqual(
            len({row["coordinate"] for row in self.rows}),
            1_533,
        )
        self.assertTrue(all(row["status"] == "verified" for row in self.rows))
        self.assertTrue(
            all(row["method"] == BUILDER.METHOD for row in self.rows)
        )
        self.assertTrue(
            all(
                row["base_runtime_proof_inherited"] is False
                for row in self.rows
            )
        )
        self.assertTrue(
            all("translation" not in row for row in self.rows)
        )
        self.assertTrue(
            all(ord(character) < 128 for character in self.private_content)
        )
        self.assertTrue(
            all(ord(character) < 128 for character in self.audit_content)
        )
        self.assertTrue(
            all(ord(character) < 128 for character in self.promotion_content)
        )
        BUILDER.validate_overlay_rows(
            self.rows,
            audit=self.audit,
            audit_file_sha256=self.context["audit_file_sha256"],
        )

    def test_control_grammar_and_layout_risks_are_excluded(self) -> None:
        adjudications = self.audit["row_adjudications"]
        for row in self.rows:
            adjudication = adjudications[row["coordinate"]]
            self.assertEqual(adjudication["failure_codes"], [])
            self.assertEqual(
                adjudication["proof_predicates"],
                {
                    "source_current_control_equal": True,
                    "source_final_control_equal": True,
                    "current_final_control_equal": True,
                    "final_line_envelope_not_above_current": True,
                    "explicit_layout_change_pending_absent": True,
                    "hard_grammar_risk_absent": True,
                    "base_runtime_proof_inherited": False,
                },
            )
        failures = self.audit["pk_only_failures"]
        self.assertEqual(
            failures["mandatory_source_final_control_exclusion_rows"],
            13,
        )
        self.assertEqual(
            failures["mandatory_source_final_control_exclusion_records"],
            7,
        )
        self.assertEqual(
            failures["combination_row_counts"]["PASS"],
            1_533,
        )
        self.assertEqual(
            failures["combination_row_counts"]["grammar_risk"],
            768,
        )

    def test_overlay_tampering_is_rejected(self) -> None:
        missing = copy.deepcopy(self.rows[:-1])
        with self.assertRaises(BUILDER.PkOnlyClosureError):
            BUILDER.validate_overlay_rows(
                missing,
                audit=self.audit,
                audit_file_sha256=self.context["audit_file_sha256"],
            )

        predicate_tamper = copy.deepcopy(self.rows)
        predicate_tamper[0]["pk_only_closure_binding"][
            "proof_predicates"
        ]["hard_grammar_risk_absent"] = False
        with self.assertRaises(BUILDER.PkOnlyClosureError):
            BUILDER.validate_overlay_rows(
                predicate_tamper,
                audit=self.audit,
                audit_file_sha256=self.context["audit_file_sha256"],
            )

        integrated_tamper = copy.deepcopy(self.rows)
        integrated_tamper[0]["predecessor_integrated_binding"][
            "private_integrated_decision_sha256"
        ] = "0" * 64
        with self.assertRaises(BUILDER.PkOnlyClosureError):
            BUILDER.validate_overlay_rows(
                integrated_tamper,
                audit=self.audit,
                audit_file_sha256=self.context["audit_file_sha256"],
            )

        closure_tamper = copy.deepcopy(self.rows)
        closure_tamper[0]["pk_only_closure_binding"][
            "closure_proof_sha256"
        ] = "0" * 64
        with self.assertRaises(BUILDER.PkOnlyClosureError):
            BUILDER.validate_overlay_rows(
                closure_tamper,
                audit=self.audit,
                audit_file_sha256=self.context["audit_file_sha256"],
            )

    def test_report_tampering_and_steam_guard(self) -> None:
        tampered = copy.deepcopy(self.audit)
        tampered["scope"]["manual_review_remaining_rows"] -= 1
        with self.assertRaises(BUILDER.PkOnlyClosureError):
            BUILDER.validate_audit(tampered, context=self.context)
        self.assertFalse(self.promotion["steam_write_performed"])
        self.assertEqual(
            self.context["steam_hash_before"],
            self.context["steam_hash_after"],
        )
        self.assertEqual(
            BUILDER.live_steam_hash(),
            self.context["steam_hash_before"],
        )


if __name__ == "__main__":
    unittest.main()
