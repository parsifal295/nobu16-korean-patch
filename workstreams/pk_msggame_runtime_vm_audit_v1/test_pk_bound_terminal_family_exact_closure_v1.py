#!/usr/bin/env python3
"""Boundary tests for the PK bound-terminal family closure layer."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from argparse import Namespace
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
MODULE_PATH = (
    SCRIPT.parent / "build_pk_bound_terminal_family_exact_closure_v1.py"
)


def load_module() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pk_bound_terminal_family_exact_closure_test_subject",
        MODULE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class BoundTerminalFamilyExactClosureTests(unittest.TestCase):
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

    def test_frozen_checkpoint_and_full_candidate_hashes(self) -> None:
        guards = self.audit["guards"]
        self.assertEqual(
            guards["checkpoint_git_commit"],
            "bde654aaea2fae23da486232f44a5c3132a667de",
        )
        self.assertEqual(
            guards["checkpoint_private_sha256"],
            MODULE.EXPECTED_CHECKPOINT_PRIVATE_SHA256,
        )
        self.assertEqual(
            guards["pk_predecessor_candidate_packed_sha256"],
            MODULE.EXPECTED_PK_PREDECESSOR_CANDIDATE_SHA256,
        )
        self.assertEqual(
            guards["pk_candidate_packed_sha256"],
            MODULE.EXPECTED_PK_CANDIDATE_SHA256,
        )
        self.assertEqual(
            guards["target_delta_manifest_sha256"],
            MODULE.EXPECTED_TARGET_DELTA_MANIFEST_SHA256,
        )
        self.assertEqual(
            guards["root_delta_proof_manifest_sha256"],
            MODULE.EXPECTED_ROOT_DELTA_PROOF_MANIFEST_SHA256,
        )

    def test_exact_fourteen_bound_endings_and_seven_risk_repairs(
        self,
    ) -> None:
        rows = {
            str(row["coordinate"]): row
            for row in self.bundle["updated_rows"]
        }
        override_rows = {
            coordinate: rows[coordinate]
            for coordinate in MODULE.TRANSLATION_OVERRIDES
        }
        self.assertEqual(len(override_rows), 14)
        for coordinate, expected in MODULE.TRANSLATION_OVERRIDES.items():
            row = override_rows[coordinate]
            self.assertEqual(row["translation"], expected)
            evidence = row["terminal_family_exact_override_evidence"]
            self.assertTrue(evidence["bound_ending_only"])
            self.assertTrue(evidence["lexical_predicate_removed"])
            self.assertTrue(evidence["caller_predicate_stem_required"])
            self.assertFalse(evidence["automatic_space_inserted"])
        self.assertEqual(
            self.bundle["analysis"]["repaired_risks"],
            7,
        )

    def test_only_actual_four_pending_rows_are_promoted(self) -> None:
        promoted = [
            row
            for row in self.bundle["updated_rows"]
            if row["terminal_family_update_action"]
            in {
                "runtime_promotion",
                "translation_override_and_runtime_promotion",
            }
        ]
        coordinates = {str(row["coordinate"]) for row in promoted}
        self.assertEqual(
            coordinates,
            {"0:1917:0", "0:1922:0", "0:2551:0", "8:1241:0"},
        )
        for row in promoted:
            self.assertEqual(row["runtime_review"], "verified")
            self.assertEqual(row["scope_classification"], "retranslated")
            binding = row["runtime_vm_verification"][
                "actual_promotion_binding"
            ]
            self.assertTrue(binding["hard_grammar_risk_absent"])
            self.assertTrue(
                binding[
                    "relative_full_closure_line_envelope_nonexpanding"
                ]
            )
            self.assertTrue(binding["manual_full_assembly_verified"])
        self.assertEqual(
            self.audit["scope"]["post_layer_pending_rows"],
            MODULE.EXPECTED_PENDING_AFTER,
        )

    def test_unproved_terminal_overrides_remain_pending(self) -> None:
        rows = {
            str(row["coordinate"]): row
            for row in self.bundle["updated_rows"]
        }
        pending = {
            coordinate
            for coordinate in MODULE.TRANSLATION_OVERRIDES
            if rows[coordinate]["terminal_family_update_action"]
            == "translation_override_pending"
        }
        self.assertEqual(
            pending,
            {
                "0:2546:0",
                "0:2547:0",
                "0:2548:0",
                "0:2549:0",
                "0:2550:0",
                "0:2552:0",
            },
        )
        for coordinate in pending:
            row = rows[coordinate]
            self.assertEqual(row["runtime_review"], "pending")
            self.assertNotIn("runtime_vm_verification", row)
            self.assertEqual(
                row["terminal_family_runtime_evidence"]["status"],
                "pending",
            )

    def test_all_affected_existing_pk_evidence_is_renewed(self) -> None:
        predecessor = self.bundle["checkpoint_rows"]
        renewed = {
            str(row["coordinate"])
            for row in self.bundle["updated_rows"]
            if predecessor[
                ("pk_msggame", str(row["coordinate"]))
            ].get("runtime_review")
            == "verified"
        }
        expected = set(
            MODULE.member_coordinates(
                self.bundle["analysis"]["affected_verified_roots"],
                self.bundle["analysis"]["verified_by_root"],
            )
        )
        self.assertEqual(renewed, expected)
        self.assertEqual(
            len(renewed),
            MODULE.EXPECTED_VERIFIED_RENEWAL_ROWS,
        )
        for coordinate in renewed:
            row = next(
                item
                for item in self.bundle["updated_rows"]
                if str(item["coordinate"]) == coordinate
            )
            evidence = row["runtime_vm_verification"]
            self.assertTrue(
                evidence["preexisting_verified_evidence_renewed"]
            )
            self.assertEqual(evidence["status"], "verified")
        self.assertEqual(
            self.audit["scope"]["affected_existing_verified_base_rows"],
            0,
        )
        self.assertTrue(self.audit["adjudication"]["base_resource_changed"] is False)

    def test_action_counts_and_private_overlay_privacy(self) -> None:
        actions = Counter(
            str(row["action"]) for row in self.bundle["evidence_rows"]
        )
        self.assertEqual(
            actions,
            {
                "verification_renewal": 680,
                "translation_override": 5,
                "translation_override_and_runtime_promotion": 3,
                "translation_override_pending": 6,
                "runtime_promotion": 1,
            },
        )
        self.assertEqual(
            len(self.bundle["updated_rows"]),
            MODULE.EXPECTED_DECISION_DELTA_ROWS,
        )
        self.assertEqual(
            len(self.bundle["evidence_rows"]),
            MODULE.EXPECTED_EVIDENCE_ROWS,
        )
        for line in self.evidence_content.splitlines():
            row = json.loads(line)
            self.assertNotIn("translation", row)
            self.assertFalse(row["per_row_game_playback_required"])

    def test_public_reports_are_source_free_and_steam_read_only(self) -> None:
        public = self.audit_content + self.promotion_content
        self.assertIsNone(
            re.search(
                r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff"
                r"\uac00-\ud7af]",
                public,
            )
        )
        self.assertIsNone(
            re.search(
                r'"(?:translation|source|source_text|dialogue_text)"\s*:',
                public,
            )
        )
        self.assertFalse(self.audit["steam_write_performed"])
        self.assertFalse(
            self.bundle["promotion"]["steam_write_performed"]
        )


class BoundTerminalFamilyPathSafetyTests(unittest.TestCase):
    def test_default_private_public_paths_are_separated(self) -> None:
        MODULE.validate_output_paths(
            Namespace(
                decision_output=MODULE.DEFAULT_DECISION_OUTPUT,
                evidence_output=MODULE.DEFAULT_EVIDENCE_OUTPUT,
                audit_output=MODULE.DEFAULT_AUDIT_OUTPUT,
                promotion_output=MODULE.DEFAULT_PROMOTION_OUTPUT,
            )
        )

    def test_private_output_cannot_escape_tmp(self) -> None:
        with self.assertRaises(MODULE.TerminalFamilyError):
            MODULE.validate_output_paths(
                Namespace(
                    decision_output=MODULE.WORKSTREAM / "private.jsonl",
                    evidence_output=MODULE.DEFAULT_EVIDENCE_OUTPUT,
                    audit_output=MODULE.DEFAULT_AUDIT_OUTPUT,
                    promotion_output=MODULE.DEFAULT_PROMOTION_OUTPUT,
                )
            )

    def test_output_cannot_target_live_steam(self) -> None:
        with self.assertRaises(MODULE.TerminalFamilyError):
            MODULE.validate_output_paths(
                Namespace(
                    decision_output=MODULE.DEFAULT_DECISION_OUTPUT,
                    evidence_output=MODULE.DEFAULT_EVIDENCE_OUTPUT,
                    audit_output=MODULE.LIVE_STEAM_PK,
                    promotion_output=MODULE.DEFAULT_PROMOTION_OUTPUT,
                )
            )


if __name__ == "__main__":
    unittest.main()
