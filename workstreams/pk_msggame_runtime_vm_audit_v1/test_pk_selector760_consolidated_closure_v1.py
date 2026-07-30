#!/usr/bin/env python3
"""Targeted checks for the frozen selector-760 consolidated closure."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from collections import Counter
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name(
    "build_pk_selector760_consolidated_closure_v1.py"
)
spec = importlib.util.spec_from_file_location(
    "selector760_closure_tested", BUILDER_PATH
)
assert spec is not None and spec.loader is not None
BUILDER = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BUILDER
spec.loader.exec_module(BUILDER)


class Selector760ClosureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.outputs = BUILDER.build_outputs()
        cls.coverage = json.loads(
            cls.outputs[BUILDER.PUBLIC_COVERAGE_OUTPUT].decode("ascii")
        )
        cls.promotion = json.loads(
            cls.outputs[BUILDER.PUBLIC_PROMOTION_OUTPUT].decode("ascii")
        )
        cls.decisions = [
            json.loads(line)
            for line in cls.outputs[BUILDER.PRIVATE_DECISIONS_OUTPUT]
            .decode("utf-8")
            .splitlines()
            if line
        ]

    def test_exact_union_counts_and_predecessor_states(self) -> None:
        self.assertEqual(
            self.promotion["result"],
            {
                "action_counts": {
                    "runtime_promotion": 16,
                    "translation_override_and_runtime_promotion": 11,
                    "translation_override_and_verification_renewal": 3,
                },
                "decision_rows": 30,
                "overrides": 14,
                "pending_after": 6341,
                "pending_before": 6368,
                "promotions": 27,
                "renewals": 3,
                "source_only_actions": 0,
            },
        )
        self.assertEqual(
            Counter(
                row["selector760_consolidated_update_action"]
                for row in self.decisions
            ),
            Counter(self.promotion["result"]["action_counts"]),
        )

    def test_site_lineage_overlap_and_terminal_proofs(self) -> None:
        result = self.coverage["result"]
        proof = self.coverage["proof"]
        self.assertEqual(result["reviewed_sites"], 32)
        self.assertEqual(result["source_call_sites"], 35)
        self.assertEqual(result["source_only_sites"], 3)
        self.assertEqual(result["source_only_actions"], 0)
        self.assertEqual(
            result["predecessor_overlaps"],
            BUILDER.EXPECTED_PREDECESSOR_OVERLAPS,
        )
        self.assertEqual(
            result["predecessor_supersessions"],
            BUILDER.EXPECTED_PREDECESSOR_SUPERSESSIONS,
        )
        self.assertTrue(proof["all_32_candidate_sites_reviewed"])
        self.assertTrue(proof["source_only_3_absent_from_current_and_candidate"])
        self.assertTrue(proof["confirmed_non_display_rows_untouched"])
        self.assertTrue(proof["seven_terminal_records_unchanged"])
        self.assertTrue(proof["all_owner_permutations_identical"])
        self.assertTrue(proof["reverse_overlay_exact"])

    def test_assignment_owned_overlap_contract_is_frozen(self) -> None:
        assignment = json.loads(
            BUILDER.ASSIGNMENT_PRIVATE_PATH.read_text(encoding="utf-8")
        )
        chunks = assignment["chunks"]
        self.assertEqual(
            [row["owned_overlap_root_count"] for row in chunks], [5, 4]
        )
        self.assertEqual(
            [row["pending_row_upper_bound"] for row in chunks], [31, 36]
        )
        self.assertEqual(sum(row["site_count"] for row in chunks), 32)
        assignment_public = json.loads(
            BUILDER.ASSIGNMENT_PUBLIC_PATH.read_text(encoding="ascii")
        )
        self.assertEqual(
            (
                assignment_public["coverage"]["owned_overlap_root_count"],
                assignment_public["coverage"]["owned_overlap_pending_rows"],
            ),
            (9, 29),
        )

    def test_terminal_roots_are_absent_from_decisions(self) -> None:
        terminal_roots = {(0, record_id) for record_id in range(2175, 2182)}
        decision_roots = {
            tuple(map(int, row["coordinate"].split(":")[:2]))
            for row in self.decisions
        }
        self.assertFalse(terminal_roots & decision_roots)

    def test_frozen_candidate_reverse_proof_and_outputs(self) -> None:
        self.assertEqual(
            self.promotion["candidate"]["reviewed_sha256"],
            "03D128438A4A79F1C4C59D46996D93E8DBD10ECAF707E18E0A46A0B3AF29A2F5",
        )
        self.assertEqual(
            self.promotion["candidate"]["reverse_overlay_sha256"],
            "396A8DF109A0693C439F990049477F5DE6E10720854D73057F3DFA1702002CCF",
        )
        labels = {
            BUILDER.PRIVATE_DECISIONS_OUTPUT: "private_decisions",
            BUILDER.PRIVATE_EVIDENCE_OUTPUT: "private_evidence",
            BUILDER.PUBLIC_COVERAGE_OUTPUT: "public_coverage",
            BUILDER.PUBLIC_PROMOTION_OUTPUT: "public_promotion",
        }
        for path, label in labels.items():
            self.assertEqual(
                BUILDER.BASE.sha256_bytes(self.outputs[path]),
                BUILDER.EXPECTED_OUTPUT_SHA256[label],
            )
            self.assertEqual(path.read_bytes(), self.outputs[path])

    def test_chunk_assembly_contracts_are_both_frozen(self) -> None:
        chunks = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in BUILDER.CHUNK_PUBLIC
        ]
        self.assertEqual(
            [
                (
                    row["result"]["decision_rows"],
                    row["result"]["blocked_pending_rows"],
                )
                for row in chunks
            ],
            [(0, 31), (30, 9)],
        )
        self.assertEqual(
            sum(row["result"]["assembly_branches"] for row in chunks), 224
        )
        self.assertTrue(
            all(
                row["proof"][
                    "accepted_assemblies_current_relative_raw_g1n_nonexpanding"
                ]
                for row in chunks
            )
        )
        self.assertTrue(
            all(
                row["proof"]["all_changed_record_control_gaps_preserved"]
                for row in chunks
            )
        )

    def test_public_reports_are_source_free(self) -> None:
        combined = (
            self.outputs[BUILDER.PUBLIC_COVERAGE_OUTPUT]
            + self.outputs[BUILDER.PUBLIC_PROMOTION_OUTPUT]
        ).decode("utf-8")
        self.assertIsNone(
            re.search(
                r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
                r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af"
                r"\uf900-\ufaff]",
                combined,
            )
        )
        self.assertIsNone(re.search(r"\b\d+:\d+(?::\d+){0,2}\b", combined))
        self.assertNotIn('"translation"', combined)
        self.assertFalse(self.coverage["steam_write_performed"])
        self.assertFalse(self.promotion["steam_write_performed"])

    def test_two_runs_are_byte_identical(self) -> None:
        self.assertEqual(BUILDER.build_outputs(), self.outputs)


if __name__ == "__main__":
    unittest.main()
