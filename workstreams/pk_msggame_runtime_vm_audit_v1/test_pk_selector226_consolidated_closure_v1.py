#!/usr/bin/env python3
"""Targeted checks for the frozen selector-226 consolidated closure."""

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
    "build_pk_selector226_consolidated_closure_v1.py"
)
spec = importlib.util.spec_from_file_location(
    "selector226_closure_tested", BUILDER_PATH
)
assert spec is not None and spec.loader is not None
BUILDER = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BUILDER
spec.loader.exec_module(BUILDER)


class Selector226ClosureTest(unittest.TestCase):
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

    def test_exact_union_counts(self) -> None:
        result = self.promotion["result"]
        self.assertEqual(result["action_counts"], BUILDER.EXPECTED_ACTION_COUNTS)
        self.assertEqual(result["decision_rows"], 37)
        self.assertEqual(result["overrides"], 3)
        self.assertEqual(result["pending_before"], 6283)
        self.assertEqual(result["pending_after"], 6246)
        self.assertEqual(result["promotions"], 37)
        self.assertEqual(result["renewals"], 0)
        self.assertEqual(result["source_only_actions"], 0)
        self.assertEqual(
            Counter(
                row["selector226_consolidated_update_action"]
                for row in self.decisions
            ),
            Counter(BUILDER.EXPECTED_ACTION_COUNTS),
        )

    def test_scope_lineage_and_zero_action_proofs(self) -> None:
        result = self.coverage["result"]
        proof = self.coverage["proof"]
        self.assertEqual(result["reviewed_sites"], 70)
        self.assertEqual(result["source_call_sites"], 75)
        self.assertEqual(result["source_only_sites"], 5)
        self.assertEqual(result["predecessor_overlaps"], 0)
        self.assertEqual(result["predecessor_supersessions"], 0)
        for name in (
            "all_70_candidate_sites_reviewed",
            "source_only_5_absent_from_current_and_candidate",
            "source_only_action_count_zero",
            "non_display_candidate_action_count_zero",
            "confirmed_non_display_rows_untouched",
            "seven_terminal_records_unchanged",
            "terminal_register_multiplicity_preserved",
            "terminal_connective_and_space_preserved",
            "terminal_records_absent_from_decisions",
            "owned_overlap_rows_require_fresh_exact_review",
            "all_owner_permutations_identical",
            "reverse_overlay_exact",
        ):
            self.assertTrue(proof[name], name)

    def test_terminal_roots_are_absent_from_decisions(self) -> None:
        terminal_roots = {(0, record_id) for record_id in range(1538, 1545)}
        decision_roots = {
            tuple(map(int, row["coordinate"].split(":")[:2]))
            for row in self.decisions
        }
        self.assertFalse(terminal_roots & decision_roots)
        BUILDER.validate_wrapper_invariants(self.outputs)

    def test_frozen_candidate_reverse_and_outputs(self) -> None:
        self.assertEqual(
            self.promotion["candidate"]["reviewed_sha256"],
            BUILDER.EXPECTED_OUTPUT_SHA256["final_candidate"],
        )
        self.assertEqual(
            self.promotion["candidate"]["reverse_overlay_sha256"],
            BUILDER.EXPECTED_OFFICIAL_CANDIDATE_SHA256,
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

    def test_chunk_contract_and_exact_inputs(self) -> None:
        chunks = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in BUILDER.CHUNK_PUBLIC
        ]
        self.assertEqual(
            tuple(row["result"]["decision_rows"] for row in chunks), (20, 17)
        )
        self.assertEqual(
            tuple(row["result"]["sites"] for row in chunks), (35, 35)
        )
        for index in range(2):
            for kind, paths in (
                ("builder", BUILDER.CHUNK_BUILDERS),
                ("public", BUILDER.CHUNK_PUBLIC),
                ("decisions", BUILDER.CHUNK_DECISIONS),
                ("evidence", BUILDER.CHUNK_EVIDENCE),
            ):
                self.assertEqual(
                    BUILDER.BASE.sha256_file(paths[index]),
                    BUILDER.EXPECTED_INPUT_SHA256[f"chunk{index}_{kind}"],
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

    def test_chunk_decision_tamper_is_rejected(self) -> None:
        original = BUILDER.EXPECTED_INPUT_SHA256["chunk1_decisions"]
        try:
            BUILDER.EXPECTED_INPUT_SHA256["chunk1_decisions"] = "0" * 64
            with self.assertRaises(BUILDER.BASE.ClosureError):
                BUILDER.build_outputs()
        finally:
            BUILDER.EXPECTED_INPUT_SHA256["chunk1_decisions"] = original


if __name__ == "__main__":
    unittest.main()
