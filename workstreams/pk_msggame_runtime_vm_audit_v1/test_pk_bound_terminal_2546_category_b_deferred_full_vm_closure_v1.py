#!/usr/bin/env python3
"""Tests for the PK 2546 category-B deferred full-VM closure."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = (
    SCRIPT.parent
    / (
        "build_pk_bound_terminal_2546_category_b_"
        "deferred_full_vm_closure_v1.py"
    )
)
SPEC = importlib.util.spec_from_file_location(
    "pk_bound_terminal_2546_category_b_deferred_closure_under_test",
    BUILDER_PATH,
)
assert SPEC is not None and SPEC.loader is not None
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


def default_args(**updates: Path | bool) -> argparse.Namespace:
    values: dict[str, Path | bool] = {
        "audit_output": BUILDER.DEFAULT_AUDIT_OUTPUT,
        "promotion_output": BUILDER.DEFAULT_PROMOTION_OUTPUT,
        "decision_output": BUILDER.DEFAULT_DECISION_OUTPUT,
        "evidence_output": BUILDER.DEFAULT_EVIDENCE_OUTPUT,
        "write": False,
    }
    values.update(updates)
    return argparse.Namespace(**values)


class CategoryBDeferredFullVmClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (
            cls.decision_content,
            cls.evidence_content,
            cls.audit_content,
            cls.promotion_content,
            cls.audit,
            cls.bundle,
        ) = BUILDER.build_outputs()
        BUILDER.validate_outputs(
            decision_content=cls.decision_content,
            evidence_content=cls.evidence_content,
            audit_content=cls.audit_content,
            promotion_content=cls.promotion_content,
            audit=cls.audit,
            bundle=cls.bundle,
        )

    def test_exact_actions_and_status_transition(self) -> None:
        partition = self.bundle["partition"]
        self.assertEqual(len(partition["promotion"]), 5)
        self.assertEqual(len(partition["renewal"]), 2)
        self.assertEqual(len(partition["overrides"]), 6)
        self.assertEqual(len(partition["keep"]), 1)
        self.assertEqual(len(partition["decisions"]), 7)
        self.assertEqual(
            Counter(
                row["action"] for row in self.bundle["evidence_rows"]
            ),
            Counter(BUILDER.EXPECTED_ACTION_COUNTS),
        )
        self.assertEqual(
            sum(
                row["preexisting_verified_evidence_renewed"]
                for row in self.bundle["evidence_rows"]
            ),
            2,
        )
        self.assertEqual(
            sum(
                row.get("runtime_review") == "pending"
                for row in self.bundle["merged"].values()
            ),
            8_196,
        )

    def test_dependency_inclusive_candidate_and_assemblies(self) -> None:
        self.assertEqual(
            BUILDER.rebuild_merged_candidate(self.bundle["merged"]),
            BUILDER.EXPECTED_FULL_CANDIDATE_SHA256,
        )
        assemblies = self.bundle["partition"]["assemblies"]
        self.assertEqual(len(assemblies), 14)
        self.assertTrue(all(row["nonexpanding"] for row in assemblies))
        self.assertTrue(
            all(row["line_topology_equal"] for row in assemblies)
        )
        self.assertEqual(
            BUILDER.canonical_sha256(assemblies),
            BUILDER.EXPECTED_ASSEMBLY_MANIFEST_SHA256,
        )
        self.assertEqual(
            self.audit["proof"]["register_assembly_pass"],
            14,
        )
        self.assertEqual(
            self.audit["proof"]["register_assembly_fail"],
            0,
        )

    def test_source_candidate_full_graph_closure(self) -> None:
        graph = self.bundle["graph_proof"]
        self.assertEqual(graph["incoming_records"], 3)
        self.assertEqual(graph["outgoing_records"], 28)
        self.assertEqual(graph["selector_call_sites"], 2)
        self.assertEqual(graph["terminal_records"], 7)
        self.assertTrue(
            graph["source_intermediate_candidate_incoming_equal"]
        )
        self.assertTrue(
            graph["source_intermediate_candidate_outgoing_equal"]
        )
        self.assertEqual(
            graph["incoming_edge_manifest_sha256"],
            BUILDER.EXPECTED_INCOMING_EDGE_MANIFEST_SHA256,
        )
        self.assertEqual(
            graph["outgoing_edge_manifest_sha256"],
            BUILDER.EXPECTED_OUTGOING_EDGE_MANIFEST_SHA256,
        )

    def test_verified_predecessor_evidence_is_exact(self) -> None:
        self.assertEqual(len(self.bundle["renewal_manifest"]), 2)
        self.assertEqual(len(self.bundle["unchanged_manifest"]), 1)
        self.assertEqual(
            BUILDER.canonical_sha256(self.bundle["renewal_manifest"]),
            BUILDER.EXPECTED_PREDECESSOR_RENEWAL_EVIDENCE_SHA256,
        )
        self.assertEqual(
            BUILDER.canonical_sha256(self.bundle["unchanged_manifest"]),
            BUILDER.EXPECTED_UNCHANGED_PREVERIFIED_MANIFEST_SHA256,
        )
        self.assertTrue(
            self.audit["proof"][
                "source_candidate_reverse_ancestor_closure_equal"
            ]
        )
        self.assertEqual(
            self.audit["proof"][
                "verified_dependency_rows_rewritten_and_renewed"
            ],
            2,
        )

    def test_ghidra_vm_contract_recheck(self) -> None:
        observation = self.bundle["ghidra_observation"]
        self.assertTrue(observation["live_mcp_redecompile_completed"])
        self.assertTrue(
            observation["call_pushes_return_offset_and_current_block"]
        )
        self.assertTrue(
            observation["return_pops_block_then_instruction_offset"]
        )
        self.assertTrue(observation["dynamic_output_is_verbatim"])
        self.assertFalse(observation["automatic_spacing_or_punctuation"])
        self.assertEqual(
            observation["contract_subset_sha256"],
            BUILDER.EXPECTED_GHIDRA_CONTRACT_SUBSET_SHA256,
        )

    def test_frozen_outputs_and_source_free_public_reports(self) -> None:
        promotion = self.bundle["promotion"]
        BUILDER.assert_source_free_report(self.audit)
        BUILDER.assert_source_free_report(promotion)
        self.assertEqual(
            BUILDER.sha256_bytes(self.audit_content.encode("utf-8")),
            BUILDER.EXPECTED_AUDIT_OUTPUT_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_bytes(self.promotion_content.encode("utf-8")),
            BUILDER.EXPECTED_PROMOTION_OUTPUT_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_bytes(self.decision_content.encode("utf-8")),
            BUILDER.EXPECTED_DECISION_OUTPUT_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_bytes(self.evidence_content.encode("utf-8")),
            BUILDER.EXPECTED_EVIDENCE_OUTPUT_SHA256,
        )
        self.assertEqual(
            self.audit_content,
            BUILDER.DEFAULT_AUDIT_OUTPUT.read_text(encoding="ascii"),
        )
        self.assertEqual(
            self.promotion_content,
            BUILDER.DEFAULT_PROMOTION_OUTPUT.read_text(encoding="ascii"),
        )
        self.assertEqual(
            self.decision_content,
            BUILDER.DEFAULT_DECISION_OUTPUT.read_text(encoding="utf-8"),
        )
        self.assertEqual(
            self.evidence_content,
            BUILDER.DEFAULT_EVIDENCE_OUTPUT.read_text(encoding="utf-8"),
        )

    def test_source_free_guard_rejects_private_content(self) -> None:
        rejected = (
            {"translation": "redacted"},
            {"safe": "\ud55c\uad6d\uc5b4"},
            {"safe": "1:2:3"},
        )
        for value in rejected:
            with self.subTest(value=value):
                with self.assertRaises(BUILDER.ClosureError):
                    BUILDER.assert_source_free_report(value)

    def test_output_paths_and_no_steam_write(self) -> None:
        BUILDER.validate_output_paths(default_args())
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaises(BUILDER.ClosureError):
                BUILDER.validate_output_paths(
                    default_args(audit_output=root / "coverage.json")
                )
            with self.assertRaises(BUILDER.ClosureError):
                BUILDER.validate_output_paths(
                    default_args(decision_output=root / "decision.jsonl")
                )
        self.assertEqual(
            self.bundle["steam_before"],
            self.bundle["steam_after"],
        )
        self.assertFalse(self.audit["steam_write_performed"])
        self.assertFalse(
            self.bundle["promotion"]["steam_write_performed"]
        )

    def test_public_reports_parse_without_private_rows(self) -> None:
        audit = json.loads(self.audit_content)
        promotion = json.loads(self.promotion_content)
        self.assertEqual(audit["status"], "PASS")
        self.assertEqual(promotion["status"], "PASS")
        self.assertEqual(BUILDER.body_key_count(audit), 0)
        self.assertEqual(BUILDER.body_key_count(promotion), 0)
        self.assertTrue(
            audit["integration_boundary"]["dedicated_layer_only"]
        )
        self.assertFalse(
            audit["integration_boundary"][
                "shared_runtime_vm_integration_modified"
            ]
        )


if __name__ == "__main__":
    unittest.main()
