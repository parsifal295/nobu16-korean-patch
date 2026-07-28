#!/usr/bin/env python3
"""Targeted checks for the frozen selector-292 consolidated closure."""

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
    "build_pk_selector292_consolidated_closure_v1.py"
)
SPEC = importlib.util.spec_from_file_location(
    "selector292_closure_tested", BUILDER_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {BUILDER_PATH}")
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class Selector292ClosureTest(unittest.TestCase):
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

    def test_exact_review_union(self) -> None:
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
            (22, 8, 6_151, 6_130, 21, 1, 0),
        )
        self.assertEqual(
            Counter(
                row["selector292_consolidated_update_action"]
                for row in self.decisions
            ),
            Counter(BUILDER.EXPECTED_ACTION_COUNTS),
        )
        self.assertEqual(
            len({row["coordinate"] for row in self.decisions}), 22
        )
        self.assertEqual(
            len({
                ":".join(row["coordinate"].split(":")[:2])
                for row in self.decisions
            }),
            6,
        )

    def test_scope_lineage_and_reused_layout_proofs(self) -> None:
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
            (26, 31, 5, 0, 0, 6, 5),
        )
        for name in (
            "all_26_candidate_sites_reviewed",
            "confirmed_non_display_rows_untouched",
            "hard_block_5_pending_rows_received_no_decisions",
            "layout_manifest_reused_without_full_recompute",
            "same_gap_392_cartesian_branches_reused",
            "source_only_5_absent_from_current_and_candidate",
            "source_only_action_count_zero",
            "terminal_records_absent_from_decisions",
            "terminal_rows_6_verified_1_pending_all_read_only",
            "all_owner_permutations_identical",
            "reverse_overlay_exact",
        ):
            self.assertTrue(proof[name], name)

    def test_hard_blocks_terminals_and_labels_are_protected(self) -> None:
        assignment = json.loads(
            BUILDER.ASSIGNMENT_PRIVATE_PATH.read_text(encoding="utf-8")
        )
        decision_coordinates = {
            row["coordinate"] for row in self.decisions
        }
        decision_roots = {
            ":".join(coordinate.split(":")[:2])
            for coordinate in decision_coordinates
        }
        hard_block_coordinates = set(
            assignment["review_partition"]["hard_block_pending_coordinates"]
        )
        hard_block_roots = set(
            assignment["review_partition"]["hard_block_roots"]
        )
        terminals = assignment["shared_terminal_ownership"][
            "terminal_manifest"
        ]
        terminal_coordinates = {row["coordinate"] for row in terminals}
        terminal_roots = {
            ":".join(coordinate.split(":")[:2])
            for coordinate in terminal_coordinates
        }
        self.assertEqual(len(hard_block_coordinates), 5)
        self.assertFalse(hard_block_coordinates & decision_coordinates)
        self.assertFalse(hard_block_roots & decision_roots)
        self.assertFalse(terminal_coordinates & decision_coordinates)
        self.assertFalse(terminal_roots & decision_roots)
        self.assertEqual(
            Counter(row["runtime_review"] for row in terminals),
            Counter({"verified": 6, "pending": 1}),
        )
        self.assertTrue(all(
            row["read_only"] is True
            and row["automatic_status_promotion_authorized"] is False
            for row in terminals
        ))
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

    def test_chunk_inputs_and_review_metrics_are_exact(self) -> None:
        chunks = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in BUILDER.CHUNK_PUBLIC
        ]
        self.assertEqual(
            tuple(row["result"]["decision_rows"] for row in chunks), (12, 10)
        )
        self.assertEqual(
            (
                chunks[0]["result"]["promoted_pending_rows"],
                chunks[1]["result"]["promoted_pending_rows"],
            ),
            (11, 10),
        )
        self.assertEqual(
            tuple(
                row["result"]["blocked_pending_rows"] for row in chunks
            ),
            (2, 10),
        )
        self.assertEqual(
            (
                chunks[0]["result"]["ordinary_attempt_branches"],
                chunks[0]["result"]["ordinary_verified_branches"],
                chunks[1]["result"]["affected_ordinary_branches_computed"],
                chunks[1]["result"]["affected_ordinary_pass_branches"],
                chunks[1]["result"]["hard_block_reused_branches"],
            ),
            (28, 21, 35, 33, 7),
        )
        self.assertEqual(
            (
                chunks[0]["result"]["full_layout_recomputed_branches"],
                chunks[1]["proof"]["full_layout_manifest_recomputed"],
            ),
            (0, False),
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
