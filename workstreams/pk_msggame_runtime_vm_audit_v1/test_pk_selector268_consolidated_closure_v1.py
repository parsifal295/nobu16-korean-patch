#!/usr/bin/env python3
"""Targeted checks for the frozen selector-268 consolidated closure."""

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
    "build_pk_selector268_consolidated_closure_v1.py"
)
spec = importlib.util.spec_from_file_location(
    "selector268_closure_tested", BUILDER_PATH
)
assert spec is not None and spec.loader is not None
BUILDER = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BUILDER
spec.loader.exec_module(BUILDER)


class Selector268ClosureTest(unittest.TestCase):
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

    def test_exact_single_coordinate_union(self) -> None:
        result = self.promotion["result"]
        self.assertEqual(result["action_counts"], BUILDER.EXPECTED_ACTION_COUNTS)
        self.assertEqual(
            (
                result["decision_rows"],
                result["overrides"],
                result["pending_before"],
                result["pending_after"],
                result["promotions"],
                result["renewals"],
                result["source_only_actions"],
            ),
            (14, 4, 6246, 6232, 14, 0, 0),
        )
        self.assertEqual(
            Counter(
                row["selector268_consolidated_update_action"]
                for row in self.decisions
            ),
            Counter(BUILDER.EXPECTED_ACTION_COUNTS),
        )
        self.assertEqual(len({row["coordinate"] for row in self.decisions}), 14)

    def test_scope_lineage_and_block_proofs(self) -> None:
        result = self.coverage["result"]
        proof = self.coverage["proof"]
        self.assertEqual(
            (
                result["reviewed_sites"],
                result["source_call_sites"],
                result["source_only_sites"],
                result["predecessor_overlaps"],
                result["predecessor_supersessions"],
            ),
            (26, 27, 1, 0, 0),
        )
        for name in (
            "all_26_candidate_sites_reviewed",
            "source_only_1_absent_from_current_and_candidate",
            "source_only_action_count_zero",
            "same_gap_atom_blocked_as_one_unit",
            "pending_assembly_evidence_did_not_auto_promote",
            "seven_terminal_records_unchanged",
            "terminal_register_multiplicity_preserved",
            "terminal_records_absent_from_decisions",
            "completed_selector_overlaps_freshly_reviewed",
            "all_owner_permutations_identical",
            "reverse_overlay_exact",
        ):
            self.assertTrue(proof[name], name)

    def test_terminal_and_same_gap_roots_absent(self) -> None:
        assignment = json.loads(
            BUILDER.ASSIGNMENT_PRIVATE_PATH.read_text(encoding="utf-8")
        )
        forbidden = {
            f"0:{record_id}" for record_id in range(1587, 1594)
        } | set(assignment["same_gap_control_atom"]["roots"])
        decision_roots = {
            ":".join(row["coordinate"].split(":")[:2])
            for row in self.decisions
        }
        self.assertFalse(forbidden & decision_roots)
        BUILDER.validate_wrapper_invariants(self.outputs)

    def test_candidate_reverse_and_outputs_are_frozen(self) -> None:
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
            tuple(row["result"]["decision_rows"] for row in chunks), (10, 4)
        )
        self.assertEqual(
            tuple(row["result"]["sites"] for row in chunks), (13, 13)
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

    def test_determinism_and_chunk_tamper_rejection(self) -> None:
        self.assertEqual(BUILDER.build_outputs(), self.outputs)
        original = BUILDER.EXPECTED_INPUT_SHA256["chunk1_decisions"]
        try:
            BUILDER.EXPECTED_INPUT_SHA256["chunk1_decisions"] = "0" * 64
            with self.assertRaises(BUILDER.BASE.ClosureError):
                BUILDER.build_outputs()
        finally:
            BUILDER.EXPECTED_INPUT_SHA256["chunk1_decisions"] = original


if __name__ == "__main__":
    unittest.main()
