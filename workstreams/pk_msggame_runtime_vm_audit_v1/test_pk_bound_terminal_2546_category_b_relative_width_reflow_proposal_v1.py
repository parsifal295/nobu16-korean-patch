#!/usr/bin/env python3
"""Tests for the source-free PK 2546 category-B reflow proposal."""

from __future__ import annotations

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
        "relative_width_reflow_proposal_v1.py"
    )
)
SPEC = importlib.util.spec_from_file_location(
    "pk_bound_terminal_2546_category_b_reflow_under_test",
    BUILDER_PATH,
)
assert SPEC is not None and SPEC.loader is not None
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class CategoryBRelativeWidthReflowProposalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.content, cls.report, cls.bundle = BUILDER.build_outputs()
        BUILDER.validate_outputs(
            content=cls.content,
            report=cls.report,
            bundle=cls.bundle,
        )

    def test_authority_chain_and_private_handoff_are_frozen(self) -> None:
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.CHECKPOINT_PRIVATE_PATH),
            BUILDER.EXPECTED_CHECKPOINT_PRIVATE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.CHECKPOINT_SOURCE_FREE_PATH),
            BUILDER.EXPECTED_CHECKPOINT_SOURCE_FREE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.PRIVATE_HANDOFF_PATH),
            BUILDER.EXPECTED_PRIVATE_HANDOFF_SHA256,
        )
        self.assertEqual(
            self.report["bindings"]["checkpoint_candidate_sha256"],
            BUILDER.EXPECTED_CHECKPOINT_CANDIDATE_SHA256,
        )
        self.assertEqual(
            self.report["bindings"]["residual_ledger_sha256"],
            BUILDER.EXPECTED_LEDGER_SHA256,
        )

    def test_exact_immediate_and_deferred_partition(self) -> None:
        immediate = self.report["proposal"]["immediate"]
        deferred = self.report["proposal"]["deferred"]
        self.assertEqual(immediate["root_count"], 4)
        self.assertEqual(immediate["pending_promotion_rows"], 12)
        self.assertEqual(immediate["translation_override_rows"], 7)
        self.assertEqual(immediate["translation_keep_rows"], 5)
        self.assertEqual(
            immediate["preexisting_verified_dependency_rewrite_rows"],
            0,
        )
        self.assertTrue(
            immediate["runtime_promotion_authorized_by_this_proposal"]
        )
        self.assertEqual(deferred["root_count"], 2)
        self.assertEqual(deferred["pending_rows"], 5)
        self.assertEqual(deferred["pending_translation_override_rows"], 4)
        self.assertEqual(deferred["pending_translation_keep_rows"], 1)
        self.assertEqual(
            deferred[
                "required_preexisting_verified_dependency_rewrite_rows"
            ],
            2,
        )
        self.assertFalse(
            deferred["runtime_promotion_authorized_by_this_proposal"]
        )

    def test_seven_register_width_proof_and_precise_rejection(self) -> None:
        immediate = self.bundle["immediate_manifest"]
        pending = self.bundle["pending_manifest"]
        pending_failures = self.bundle["pending_failures"]
        deferred_full = self.bundle["deferred_full_manifest"]
        self.assertEqual(len(immediate), 28)
        self.assertTrue(all(row["nonexpanding"] for row in immediate))
        self.assertEqual(len(pending), 14)
        self.assertEqual(len(pending_failures), 13)
        failure_counts = Counter(row["root"] for row in pending_failures)
        self.assertEqual(sorted(failure_counts.values()), [6, 7])
        pending_passes = [row for row in pending if row["nonexpanding"]]
        self.assertEqual(len(pending_passes), 1)
        self.assertEqual(pending_passes[0]["terminal_record_id"], 2551)
        self.assertEqual(len(deferred_full), 14)
        self.assertTrue(all(row["nonexpanding"] for row in deferred_full))
        self.assertEqual(
            BUILDER.canonical_sha256(pending_failures),
            BUILDER.EXPECTED_PENDING_ONLY_FAILURE_SHA256,
        )

    def test_candidate_control_and_review_manifests_are_pinned(self) -> None:
        candidates = self.bundle["candidates"]
        self.assertEqual(
            BUILDER.sha256_bytes(candidates["checkpoint_blob"]),
            BUILDER.EXPECTED_CHECKPOINT_CANDIDATE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_bytes(candidates["immediate_blob"]),
            BUILDER.EXPECTED_IMMEDIATE_CANDIDATE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_bytes(candidates["pending_only_blob"]),
            BUILDER.EXPECTED_PENDING_ONLY_CANDIDATE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_bytes(candidates["full_blob"]),
            BUILDER.EXPECTED_FULL_CANDIDATE_SHA256,
        )
        self.assertEqual(
            BUILDER.canonical_sha256(self.bundle["component_manifest"]),
            BUILDER.EXPECTED_COMPONENT_MANIFEST_SHA256,
        )
        review = self.report["review"]
        self.assertEqual(review["jp_semantic_authority_root_count"], 6)
        self.assertEqual(
            review["en_sc_tc_auxiliary_context_root_count"],
            6,
        )
        self.assertEqual(review["historical_term_review_root_count"], 6)
        self.assertEqual(
            review["character_voice_seven_register_review_root_count"],
            6,
        )

    def test_source_free_report_and_distribution_boundary(self) -> None:
        BUILDER.assert_source_free_report(self.report)
        parsed = json.loads(self.content)
        self.assertFalse(
            parsed["distribution_policy"][
                "tracked_report_contains_commercial_source_text"
            ]
        )
        self.assertFalse(
            parsed["distribution_policy"][
                "tracked_report_contains_translated_dialogue_text"
            ]
        )
        self.assertFalse(
            parsed["integration"]["shared_runtime_vm_integration_modified"]
        )
        self.assertFalse(parsed["steam_write_performed"])
        self.assertEqual(
            BUILDER.sha256_bytes(self.content.encode("utf-8")),
            BUILDER.EXPECTED_PUBLIC_OUTPUT_SHA256,
        )

    def test_source_free_guard_and_strict_loader_reject_tampering(self) -> None:
        rejected = (
            {"translation": "redacted"},
            {"nested": [{"exact_map": {}}]},
            {"safe": "\ud55c\uad6d\uc5b4"},
        )
        for value in rejected:
            with self.subTest(value=value):
                with self.assertRaises(BUILDER.ProposalError):
                    BUILDER.assert_source_free_report(value)

        with tempfile.TemporaryDirectory() as temporary:
            tampered = Path(temporary) / "tampered.json"
            tampered.write_bytes(
                BUILDER.PRIVATE_HANDOFF_PATH.read_bytes() + b" "
            )
            with self.assertRaisesRegex(
                BUILDER.ProposalError,
                "digest drifted",
            ):
                BUILDER.load_json(
                    tampered,
                    BUILDER.EXPECTED_PRIVATE_HANDOFF_SHA256,
                )

    def test_output_path_is_fixed_and_not_steam(self) -> None:
        BUILDER.validate_output_path(BUILDER.DEFAULT_PUBLIC_OUTPUT)
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(
                BUILDER.ProposalError,
                "fixed tracked",
            ):
                BUILDER.validate_output_path(
                    Path(temporary) / "report.json"
                )
        with self.assertRaises(BUILDER.ProposalError):
            BUILDER.validate_output_path(BUILDER.LIVE_STEAM_PK)


if __name__ == "__main__":
    unittest.main()
