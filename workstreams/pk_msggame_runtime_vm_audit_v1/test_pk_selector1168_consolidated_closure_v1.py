#!/usr/bin/env python3
"""Targeted checks for the frozen selector-1168 consolidated closure."""

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
    "build_pk_selector1168_consolidated_closure_v1.py"
)
spec = importlib.util.spec_from_file_location(
    "selector1168_closure_tested", BUILDER_PATH
)
assert spec is not None and spec.loader is not None
BUILDER = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BUILDER
spec.loader.exec_module(BUILDER)


class Selector1168ClosureTest(unittest.TestCase):
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
        result = self.promotion["result"]
        self.assertEqual(result["action_counts"], BUILDER.EXPECTED_ACTION_COUNTS)
        self.assertEqual(result["decision_rows"], 19)
        self.assertEqual(result["overrides"], 5)
        self.assertEqual(result["pending_before"], 6302)
        self.assertEqual(result["pending_after"], 6283)
        self.assertEqual(result["promotions"], 19)
        self.assertEqual(result["renewals"], 0)
        self.assertEqual(result["source_only_actions"], 0)
        self.assertEqual(
            Counter(
                row["selector1168_consolidated_update_action"]
                for row in self.decisions
            ),
            Counter(BUILDER.EXPECTED_ACTION_COUNTS),
        )

    def test_site_lineage_and_terminal_proofs(self) -> None:
        result = self.coverage["result"]
        proof = self.coverage["proof"]
        self.assertEqual(result["reviewed_sites"], 53)
        self.assertEqual(result["source_call_sites"], 58)
        self.assertEqual(result["source_only_sites"], 5)
        self.assertEqual(result["source_only_actions"], 0)
        self.assertEqual(result["predecessor_overlaps"], 0)
        self.assertEqual(result["predecessor_supersessions"], 0)
        for name in (
            "all_53_candidate_sites_reviewed",
            "source_only_5_absent_from_current_and_candidate",
            "confirmed_non_display_rows_untouched",
            "seven_terminal_records_unchanged",
            "honorific_prefix_terminals_all_empty_in_candidate",
            "honorific_prefix_terminals_absent_from_decisions",
            "owned_overlap_rows_require_fresh_exact_review",
            "all_owner_permutations_identical",
            "reverse_overlay_exact",
        ):
            self.assertTrue(proof[name], name)

    def test_assignment_overlap_is_explicit_and_never_automatic(self) -> None:
        assignment = json.loads(
            BUILDER.ASSIGNMENT_PRIVATE_PATH.read_text(encoding="utf-8")
        )
        self.assertEqual(
            [row["owned_overlap_root_count"] for row in assignment["chunks"]],
            [3, 4],
        )
        self.assertFalse(
            set(assignment["chunks"][0]["roots"])
            & set(assignment["chunks"][1]["roots"])
        )
        for path in BUILDER.CHUNK_DECISIONS:
            for line in path.read_text(encoding="utf-8").splitlines():
                row = json.loads(line)
                self.assertEqual(row["fresh_semantic_review"], "approved")
                self.assertEqual(row["runtime_review"], "verified")
                self.assertEqual(
                    row["predecessor_candidate_sha256"],
                    BUILDER.EXPECTED_OFFICIAL_CANDIDATE_SHA256,
                )
                self.assertNotIn("auto", row["action"].lower())

    def test_terminal_roots_are_absent_from_decisions(self) -> None:
        terminal_roots = {(0, record_id) for record_id in range(2637, 2644)}
        decision_roots = {
            tuple(map(int, row["coordinate"].split(":")[:2]))
            for row in self.decisions
        }
        self.assertFalse(terminal_roots & decision_roots)

    def test_frozen_candidate_reverse_proof_and_outputs(self) -> None:
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

    def test_chunk_contract_and_exact_input_hashes(self) -> None:
        chunks = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in BUILDER.CHUNK_PUBLIC
        ]
        self.assertEqual(
            tuple(row["result"]["decision_rows"] for row in chunks), (15, 4)
        )
        self.assertEqual(
            tuple(row["result"]["sites"] for row in chunks), (26, 27)
        )
        for index, path in enumerate(BUILDER.CHUNK_DECISIONS):
            self.assertEqual(
                len([line for line in path.read_bytes().splitlines() if line]),
                BUILDER.EXPECTED_CHUNK_ROWS[index],
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

    def test_determinism_and_tamper_rejection(self) -> None:
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
