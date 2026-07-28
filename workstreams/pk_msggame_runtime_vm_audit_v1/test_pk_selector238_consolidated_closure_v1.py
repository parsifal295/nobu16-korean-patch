#!/usr/bin/env python3
"""Targeted checks for the frozen selector-238 consolidated closure."""

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
    "build_pk_selector238_consolidated_closure_v1.py"
)
SPEC = importlib.util.spec_from_file_location(
    "selector238_closure_tested", BUILDER_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {BUILDER_PATH}")
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class Selector238ClosureTest(unittest.TestCase):
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

    def test_exact_pending_only_union(self) -> None:
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
            (27, 22, 6_178, 6_151, 27, 0, 0),
        )
        self.assertEqual(
            Counter(
                row["selector238_consolidated_update_action"]
                for row in self.decisions
            ),
            Counter(BUILDER.EXPECTED_ACTION_COUNTS),
        )
        self.assertEqual(
            len({row["coordinate"] for row in self.decisions}), 27
        )
        self.assertEqual(
            len({
                ":".join(row["coordinate"].split(":")[:2])
                for row in self.decisions
            }),
            9,
        )

    def test_scope_lineage_and_runtime_branch_proofs(self) -> None:
        result = self.coverage["result"]
        proof = self.coverage["proof"]
        self.assertEqual(
            (
                result["reviewed_sites"],
                result["source_call_sites"],
                result["source_only_sites"],
                result["predecessor_overlaps"],
                result["predecessor_supersessions"],
                result["decision_roots"],
                result["changed_roots"],
            ),
            (27, 28, 1, 0, 0, 9, 9),
        )
        self.assertEqual(
            proof["direct_ordinary_terminal_branches_reviewed"], 105
        )
        for name in (
            "all_27_candidate_sites_reviewed",
            "source_only_1_absent_from_current_and_candidate",
            "source_only_action_count_zero",
            "same_gap_and_multi_control_atoms_absent",
            "terminal_rows_pending_and_read_only",
            "terminal_records_absent_from_decisions",
            "confirmed_non_display_rows_untouched",
            "all_owner_permutations_identical",
            "reverse_overlay_exact",
        ):
            self.assertTrue(proof[name], name)

    def test_terminal_and_nonpending_rows_are_protected(self) -> None:
        assignment = json.loads(
            BUILDER.ASSIGNMENT_PRIVATE_PATH.read_text(encoding="utf-8")
        )
        terminal_roots = {
            f"0:{record_id}" for record_id in range(1552, 1559)
        }
        decision_roots = {
            ":".join(row["coordinate"].split(":")[:2])
            for row in self.decisions
        }
        self.assertFalse(terminal_roots & decision_roots)
        self.assertEqual(assignment["same_gap_root_atoms"], [])
        self.assertTrue(all(
            row["resource"] == "pk_msggame"
            and row["layout_review"]
                == "current_relative_raw_g1n_nonexpanding"
            and row["runtime_review"] == "verified"
            for row in self.decisions
        ))
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

    def test_chunk_inputs_and_branch_metrics_are_exact(self) -> None:
        chunks = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in BUILDER.CHUNK_PUBLIC
        ]
        self.assertEqual(
            tuple(row["result"]["decision_rows"] for row in chunks), (11, 16)
        )
        self.assertEqual(
            (
                chunks[0]["result"]["sites"],
                chunks[1]["result"]["assigned_sites"],
            ),
            (14, 13),
        )
        self.assertEqual(
            tuple(
                row["result"]["blocked_pending_rows"] for row in chunks
            ),
            (3, 6),
        )
        self.assertEqual(
            sum(
                row["result"]["selector238_accepted_branches"]
                + row["result"]["selector238_blocked_pending_branches"]
                for row in chunks
            ),
            105,
        )
        self.assertEqual(
            tuple(
                row["result"]["selector238_total_branches"]
                for row in chunks
            ),
            (98, 91),
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

    def test_determinism_and_input_tamper_rejection(self) -> None:
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
