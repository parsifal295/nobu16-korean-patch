#!/usr/bin/env python3
"""Targeted checks for the zero-change selector-508 closure."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name(
    "build_pk_selector508_consolidated_closure_v1.py"
)
spec = importlib.util.spec_from_file_location(
    "selector508_closure_tested", BUILDER_PATH
)
assert spec is not None and spec.loader is not None
BUILDER = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BUILDER
spec.loader.exec_module(BUILDER)


class Selector508ClosureTest(unittest.TestCase):
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

    def test_exact_empty_union_and_identity_state(self) -> None:
        self.assertEqual(
            self.promotion["result"],
            {
                "action_counts": {},
                "decision_rows": 0,
                "overrides": 0,
                "pending_after": 6341,
                "pending_before": 6341,
                "promotions": 0,
                "renewals": 0,
                "source_only_actions": 0,
            },
        )
        self.assertEqual(self.decisions, [])
        self.assertEqual(
            self.outputs[BUILDER.PRIVATE_DECISIONS_OUTPUT], b""
        )

    def test_site_lineage_overlap_and_terminal_proofs(self) -> None:
        result = self.coverage["result"]
        proof = self.coverage["proof"]
        self.assertEqual(result["reviewed_sites"], 74)
        self.assertEqual(result["source_call_sites"], 81)
        self.assertEqual(result["source_only_sites"], 7)
        self.assertEqual(result["source_only_actions"], 0)
        self.assertEqual(result["predecessor_overlaps"], 0)
        self.assertEqual(result["predecessor_supersessions"], 0)
        self.assertTrue(proof["all_74_candidate_sites_reviewed"])
        self.assertTrue(proof["source_only_7_absent_from_current_and_candidate"])
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
            [row["owned_overlap_root_count"] for row in chunks], [1, 6]
        )
        self.assertEqual(
            [row["pending_row_upper_bound"] for row in chunks], [30, 31]
        )
        self.assertEqual(sum(row["site_count"] for row in chunks), 74)
        assignment_public = json.loads(
            BUILDER.ASSIGNMENT_PUBLIC_PATH.read_text(encoding="ascii")
        )
        self.assertEqual(
            (
                assignment_public["coverage"]["owned_overlap_root_count"],
                assignment_public["coverage"]["owned_overlap_pending_rows"],
            ),
            (7, 19),
        )

    def test_terminal_roots_are_absent_from_empty_union(self) -> None:
        terminal_roots = {(0, record_id) for record_id in range(1888, 1895)}
        decision_roots = {
            tuple(map(int, row["coordinate"].split(":")[:2]))
            for row in self.decisions
        }
        self.assertFalse(terminal_roots & decision_roots)

    def test_candidate_and_reverse_are_identity_and_outputs_frozen(self) -> None:
        expected = (
            "03D128438A4A79F1C4C59D46996D93E8DBD10ECAF707E18E0A46A0B3AF29A2F5"
        )
        self.assertEqual(
            self.promotion["candidate"]["reviewed_sha256"], expected
        )
        self.assertEqual(
            self.promotion["candidate"]["reverse_overlay_sha256"], expected
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

    def test_both_chunks_are_blocked_only_and_complete(self) -> None:
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
            [(0, 30), (0, 31)],
        )
        self.assertEqual(
            sum(row["result"]["assembly_branches"] for row in chunks), 518
        )
        self.assertTrue(
            all(
                row["proof"]["blocked_unresolved_sites_not_promoted"]
                and row["proof"]["all_assigned_sites_reviewed"]
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
