#!/usr/bin/env python3
"""Tests for the PK 2546 category-B immediate closure layer."""

from __future__ import annotations

import argparse
import copy
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
    / "build_pk_bound_terminal_2546_category_b_immediate_closure_v1.py"
)
SPEC = importlib.util.spec_from_file_location(
    "pk_bound_terminal_2546_category_b_immediate_closure_under_test",
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
        "check": True,
    }
    values.update(updates)
    return argparse.Namespace(**values)


class CategoryBImmediateClosureTests(unittest.TestCase):
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

    def test_immutable_predecessor_and_proposal_bindings(self) -> None:
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.PREDECESSOR_PRIVATE_PATH),
            BUILDER.EXPECTED_PREDECESSOR_PRIVATE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.PREDECESSOR_PUBLIC_PATH),
            BUILDER.EXPECTED_PREDECESSOR_PUBLIC_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.PROPOSAL_PRIVATE_PATH),
            BUILDER.EXPECTED_PROPOSAL_PRIVATE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.PROPOSAL_PUBLIC_PATH),
            BUILDER.EXPECTED_PROPOSAL_PUBLIC_SHA256,
        )
        self.assertEqual(
            self.audit["guards"]["candidate_sha256"],
            BUILDER.EXPECTED_CANDIDATE_SHA256,
        )

    def test_exact_promotion_partition_and_actions(self) -> None:
        partition = self.bundle["partition"]
        self.assertEqual(len(partition["promotion"]), 12)
        self.assertEqual(len(partition["roots"]), 4)
        self.assertEqual(len(partition["overrides"]), 7)
        self.assertEqual(len(partition["keep"]), 5)
        self.assertEqual(
            Counter(
                row["action"] for row in self.bundle["evidence_rows"]
            ),
            Counter(BUILDER.EXPECTED_ACTION_COUNTS),
        )
        self.assertEqual(
            self.audit["scope"]["verification_renewal_rows"],
            0,
        )

    def test_twenty_eight_assemblies_and_record_guards(self) -> None:
        proposal_bundle = self.bundle["proposal_bundle"]
        manifest = proposal_bundle["immediate_manifest"]
        self.assertEqual(len(manifest), 28)
        self.assertTrue(all(row["nonexpanding"] for row in manifest))
        self.assertEqual(
            BUILDER.canonical_sha256(manifest),
            BUILDER.EXPECTED_ASSEMBLY_MANIFEST_SHA256,
        )
        self.assertEqual(
            BUILDER.canonical_sha256(
                self.bundle["partition"]["component_manifest"]
            ),
            BUILDER.EXPECTED_COMPONENT_MANIFEST_SHA256,
        )
        proof = self.audit["proof"]
        self.assertTrue(
            proof[
                "all_7_register_assemblies_current_relative_raw_g1n_"
                "nonexpanding"
            ]
        )
        self.assertTrue(proof["control_components_preserved"])
        self.assertTrue(proof["record_gap_bytes_preserved"])
        self.assertTrue(proof["protected_token_signatures_preserved"])

    def test_deferred_rows_and_dependencies_remain_exact_blockers(self) -> None:
        partition = self.bundle["partition"]
        self.assertEqual(len(partition["deferred_roots"]), 2)
        self.assertEqual(len(partition["deferred_pending"]), 5)
        self.assertEqual(len(partition["deferred_dependencies"]), 2)
        self.assertEqual(len(self.bundle["blocker_manifest"]), 7)
        self.assertEqual(
            BUILDER.canonical_sha256(self.bundle["blocker_manifest"]),
            BUILDER.EXPECTED_DEFERRED_BLOCKER_MANIFEST_SHA256,
        )
        self.assertEqual(
            len(self.bundle["proposal_bundle"]["pending_failures"]),
            13,
        )
        self.assertFalse(
            self.audit["deferred_blockers"][
                "runtime_promotion_authorized"
            ]
        )
        updated = {
            str(row["coordinate"]) for row in self.bundle["updated_rows"]
        }
        self.assertFalse(
            updated
            & (
                partition["deferred_pending"]
                | partition["deferred_dependencies"]
            )
        )

    def test_merged_candidate_pending_count_and_private_rows(self) -> None:
        merged = {
            key: copy.deepcopy(dict(row))
            for key, row in self.bundle["predecessor_rows"].items()
        }
        merged.update(
            {
                ("pk_msggame", str(row["coordinate"])): row
                for row in self.bundle["updated_rows"]
            }
        )
        self.assertEqual(
            sum(
                row.get("runtime_review") == "pending"
                for row in merged.values()
            ),
            8_201,
        )
        self.assertEqual(
            BUILDER.rebuild_merged_candidate(merged),
            BUILDER.EXPECTED_CANDIDATE_SHA256,
        )
        self.assertEqual(len(self.bundle["updated_rows"]), 12)
        self.assertEqual(len(self.bundle["evidence_rows"]), 12)
        self.assertEqual(
            BUILDER.body_key_count(self.bundle["evidence_rows"]),
            0,
        )

    def test_source_free_reports_and_frozen_outputs(self) -> None:
        promotion = self.bundle["promotion"]
        BUILDER.assert_source_free_report(self.audit)
        BUILDER.assert_source_free_report(promotion)
        self.assertEqual(
            BUILDER.sha256_bytes(self.audit_content.encode("utf-8")),
            BUILDER.EXPECTED_AUDIT_FILE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_bytes(self.promotion_content.encode("utf-8")),
            BUILDER.EXPECTED_PROMOTION_FILE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_bytes(self.decision_content.encode("utf-8")),
            BUILDER.EXPECTED_DECISION_FILE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_bytes(self.evidence_content.encode("utf-8")),
            BUILDER.EXPECTED_EVIDENCE_FILE_SHA256,
        )
        self.assertFalse(self.audit["steam_write_performed"])
        self.assertFalse(promotion["steam_write_performed"])
        self.assertEqual(
            self.bundle["steam_before"],
            self.bundle["steam_after"],
        )

    def test_source_free_guard_rejects_bodies_text_and_coordinates(self) -> None:
        rejected = (
            {"translation": "redacted"},
            {"safe": "\ud55c\uad6d\uc5b4"},
            {"safe": "1:2:3"},
        )
        for value in rejected:
            with self.subTest(value=value):
                with self.assertRaises(BUILDER.ClosureError):
                    BUILDER.assert_source_free_report(value)

    def test_output_path_guards(self) -> None:
        BUILDER.validate_output_paths(default_args())
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(
                BUILDER.ClosureError,
                "private output",
            ):
                BUILDER.validate_output_paths(
                    default_args(decision_output=root / "decision.jsonl")
                )
            with self.assertRaisesRegex(
                BUILDER.ClosureError,
                "fixed tracked",
            ):
                BUILDER.validate_output_paths(
                    default_args(audit_output=root / "coverage.json")
                )
        with self.assertRaisesRegex(BUILDER.ClosureError, "live Steam"):
            BUILDER.validate_output_paths(
                default_args(decision_output=BUILDER.LIVE_STEAM_PK)
            )

    def test_public_reports_parse_and_contain_no_private_rows(self) -> None:
        audit = json.loads(self.audit_content)
        promotion = json.loads(self.promotion_content)
        self.assertEqual(audit["status"], "PASS")
        self.assertEqual(promotion["status"], "PASS")
        self.assertEqual(BUILDER.body_key_count(audit), 0)
        self.assertEqual(BUILDER.body_key_count(promotion), 0)
        self.assertFalse(
            audit["distribution_policy"][
                "tracked_report_contains_translated_dialogue_text"
            ]
        )
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
