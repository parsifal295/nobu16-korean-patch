#!/usr/bin/env python3
"""Targeted checks for the frozen selector-730 consolidated closure."""

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
    "build_pk_selector730_consolidated_closure_v1.py"
)
SPEC = importlib.util.spec_from_file_location(
    "selector730_closure_tested", BUILDER_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {BUILDER_PATH}")
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class Selector730ClosureTest(unittest.TestCase):
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
            (3, 1, 6_181, 6_178, 3, 0, 0),
        )
        self.assertEqual(
            Counter(
                row["selector730_consolidated_update_action"]
                for row in self.decisions
            ),
            Counter(BUILDER.EXPECTED_ACTION_COUNTS),
        )
        self.assertEqual(len({row["coordinate"] for row in self.decisions}), 3)
        self.assertEqual(
            len({
                ":".join(row["coordinate"].split(":")[:2])
                for row in self.decisions
            }),
            1,
        )

    def test_scope_lineage_and_cartesian_block_proofs(self) -> None:
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
                result["shared_cartesian_roots"],
                result["shared_cartesian_branches"],
                result["blocked_same_gap_pending_roots"],
                result["blocked_same_gap_pending_rows"],
            ),
            (41, 46, 5, 0, 0, 1, 1, 37, 1_813, 17, 34),
        )
        for name in (
            "all_41_candidate_sites_reviewed",
            "source_only_5_absent_from_current_and_candidate",
            "source_only_action_count_zero",
            "same_gap_37_roots_atomic",
            "same_gap_17_pending_roots_blocked",
            "shared_cartesian_1813_branches_reused",
            "shared_cartesian_branches_recomputed_zero",
            "prior_owned_and_template_automatic_promotion_count_zero",
            "terminal_rows_pending_and_read_only",
            "terminal_records_absent_from_decisions",
            "confirmed_non_display_rows_untouched",
            "all_owner_permutations_identical",
            "reverse_overlay_exact",
        ):
            self.assertTrue(proof[name], name)

    def test_terminal_and_same_gap_roots_absent(self) -> None:
        assignment = json.loads(
            BUILDER.ASSIGNMENT_PRIVATE_PATH.read_text(encoding="utf-8")
        )
        forbidden = {
            f"0:{record_id}" for record_id in range(2140, 2147)
        } | {
            str(row["root"]) for row in assignment["same_gap_root_atoms"]
        }
        decision_roots = {
            ":".join(row["coordinate"].split(":")[:2])
            for row in self.decisions
        }
        self.assertFalse(forbidden & decision_roots)
        self.assertTrue(all(
            row["resource"] == "pk_msggame"
            and row["layout_review"]
                == "current_relative_raw_g1n_nonexpanding"
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

    def test_chunk_and_shared_manifest_inputs_are_exact(self) -> None:
        chunks = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in BUILDER.CHUNK_PUBLIC
        ]
        self.assertEqual(
            tuple(row["result"]["decision_rows"] for row in chunks), (0, 3)
        )
        self.assertEqual(
            (
                chunks[0]["result"]["assigned_sites"],
                chunks[1]["result"]["chunk_sites"],
            ),
            (21, 20),
        )
        self.assertEqual(
            (
                chunks[0]["result"]["shared_cartesian_branches_reused"],
                chunks[1]["result"]["same_gap_total_branches_reused"],
            ),
            (931, 882),
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
        for kind, path in (
            ("builder", BUILDER.SHARED_CARTESIAN_BUILDER_PATH),
            ("private", BUILDER.SHARED_CARTESIAN_PRIVATE_PATH),
            ("public", BUILDER.SHARED_CARTESIAN_PUBLIC_PATH),
        ):
            self.assertEqual(
                BUILDER.BASE.sha256_file(path),
                BUILDER.EXPECTED_SHARED_CARTESIAN_SHA256[kind],
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
