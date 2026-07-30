#!/usr/bin/env python3
"""Targeted checks for the frozen selector-376 consolidated closure."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name(
    "build_pk_selector376_consolidated_closure_v1.py"
)
spec = importlib.util.spec_from_file_location(
    "selector376_closure_tested", BUILDER_PATH
)
assert spec is not None and spec.loader is not None
BUILDER = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BUILDER
spec.loader.exec_module(BUILDER)


class Selector376ClosureTest(unittest.TestCase):
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
        self.assertEqual(result["decision_rows"], BUILDER.EXPECTED_DECISION_ROWS)
        self.assertEqual(result["overrides"], BUILDER.EXPECTED_OVERRIDES)
        self.assertEqual(result["pending_before"], 6307)
        self.assertEqual(result["pending_after"], BUILDER.EXPECTED_PENDING_AFTER)
        self.assertEqual(result["promotions"], BUILDER.EXPECTED_PROMOTIONS)
        self.assertEqual(result["renewals"], BUILDER.EXPECTED_RENEWALS)
        self.assertEqual(result["source_only_actions"], 0)
        self.assertEqual(
            Counter(
                row["selector376_consolidated_update_action"]
                for row in self.decisions
            ),
            Counter(BUILDER.EXPECTED_ACTION_COUNTS),
        )

    def test_site_lineage_overlap_and_terminal_proofs(self) -> None:
        result = self.coverage["result"]
        proof = self.coverage["proof"]
        self.assertEqual(result["reviewed_sites"], 41)
        self.assertEqual(result["source_call_sites"], 48)
        self.assertEqual(result["source_only_sites"], 7)
        self.assertEqual(result["source_only_actions"], 0)
        self.assertEqual(
            result["predecessor_overlaps"],
            BUILDER.EXPECTED_PREDECESSOR_OVERLAPS,
        )
        self.assertEqual(
            result["predecessor_supersessions"],
            BUILDER.EXPECTED_PREDECESSOR_SUPERSESSIONS,
        )
        self.assertTrue(proof["all_41_candidate_sites_reviewed"])
        self.assertTrue(proof["source_only_7_absent_from_current_and_candidate"])
        self.assertTrue(proof["confirmed_non_display_rows_untouched"])
        self.assertTrue(proof["seven_terminal_records_unchanged"])
        self.assertTrue(proof["owned_overlap_rows_require_fresh_exact_review"])
        self.assertTrue(proof["all_owner_permutations_identical"])
        self.assertTrue(proof["reverse_overlay_exact"])

    def test_owned_assignment_overlap_is_explicit_and_never_automatic(self) -> None:
        assignment = json.loads(
            BUILDER.ASSIGNMENT_PRIVATE_PATH.read_text(encoding="utf-8")
        )
        chunks = assignment["chunks"]
        self.assertEqual(
            [row["owned_overlap_root_count"] for row in chunks], [3, 2]
        )
        self.assertEqual(
            [row["pending_row_upper_bound"] for row in chunks], [29, 23]
        )
        self.assertEqual(sum(row["site_count"] for row in chunks), 41)
        self.assertFalse(set(chunks[0]["roots"]) & set(chunks[1]["roots"]))
        assignment_public = json.loads(
            BUILDER.ASSIGNMENT_PUBLIC_PATH.read_text(encoding="ascii")
        )
        self.assertEqual(
            (
                assignment_public["coverage"]["owned_overlap_root_count"],
                assignment_public["coverage"]["owned_overlap_pending_rows"],
            ),
            (5, 11),
        )
        chunk_decisions = [
            json.loads(line)
            for path in BUILDER.CHUNK_DECISIONS
            for line in path.read_text(encoding="utf-8").splitlines()
            if line
        ]
        for row in chunk_decisions:
            self.assertEqual(row["fresh_semantic_review"], "approved")
            self.assertEqual(row["runtime_review"], "verified")
            self.assertEqual(
                row["predecessor_candidate_sha256"],
                BUILDER.EXPECTED_OFFICIAL_CANDIDATE_SHA256,
            )
            self.assertNotIn("auto", row["action"].lower())

    def test_terminal_roots_are_absent_from_decisions(self) -> None:
        terminal_roots = {(0, record_id) for record_id in range(1713, 1720)}
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

    def test_chunk_empty_and_blocked_contracts(self) -> None:
        chunks = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in BUILDER.CHUNK_PUBLIC
        ]
        self.assertEqual(
            tuple(row["result"]["decision_rows"] for row in chunks),
            BUILDER.EXPECTED_CHUNK_ROWS,
        )
        self.assertEqual(
            tuple(row["result"]["sites"] for row in chunks),
            BUILDER.EXPECTED_CHUNK_SITES,
        )
        self.assertTrue(
            all(
                row["result"]["blocked_pending_rows"] >= 0
                and row["proof"]["blocked_unresolved_sites_not_promoted"]
                and row["proof"]["all_assigned_sites_reviewed"]
                for row in chunks
            )
        )
        for index, row in enumerate(chunks):
            decision_bytes = BUILDER.CHUNK_DECISIONS[index].read_bytes()
            if row["result"]["decision_rows"] == 0:
                self.assertEqual(decision_bytes, b"")
                self.assertGreater(row["result"]["blocked_pending_rows"], 0)
            else:
                self.assertEqual(
                    len([line for line in decision_bytes.splitlines() if line]),
                    row["result"]["decision_rows"],
                )
        with tempfile.TemporaryDirectory() as directory:
            empty = Path(directory) / "empty.jsonl"
            empty.write_bytes(b"")
            self.assertEqual(BUILDER.BASE.load_jsonl(empty), [])

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
