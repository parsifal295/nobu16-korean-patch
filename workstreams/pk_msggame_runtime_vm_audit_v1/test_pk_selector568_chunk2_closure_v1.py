#!/usr/bin/env python3
"""Tests for the independent selector-568 chunk-2 closure layer."""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.parent / "build_pk_selector568_chunk2_closure_v1.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = load_module(
    BUILDER_PATH,
    "pk_selector568_chunk2_closure_test_builder_v1",
)


def default_args(**updates):
    values = {
        "audit_output": BUILDER.DEFAULT_AUDIT_OUTPUT,
        "promotion_output": BUILDER.DEFAULT_PROMOTION_OUTPUT,
        "decision_output": BUILDER.DEFAULT_DECISION_OUTPUT,
        "evidence_output": BUILDER.DEFAULT_EVIDENCE_OUTPUT,
        "check": True,
    }
    values.update(updates)
    return argparse.Namespace(**values)


class Selector568Chunk2ClosureTests(unittest.TestCase):
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
            require_frozen_hashes=True,
        )

    def test_frozen_inputs_and_outputs_match_disk(self) -> None:
        expected = {
            BUILDER.PREDECESSOR_PRIVATE_PATH:
                BUILDER.EXPECTED_PREDECESSOR_PRIVATE_SHA256,
            BUILDER.PREDECESSOR_PUBLIC_PATH:
                BUILDER.EXPECTED_PREDECESSOR_PUBLIC_SHA256,
            BUILDER.PRIVATE_HANDOFF_PATH:
                BUILDER.EXPECTED_HANDOFF_SHA256,
            BUILDER.REVIEW_PUBLIC_PATH:
                BUILDER.EXPECTED_REVIEW_PUBLIC_SHA256,
            BUILDER.DEFAULT_AUDIT_OUTPUT:
                BUILDER.EXPECTED_AUDIT_FILE_SHA256,
            BUILDER.DEFAULT_PROMOTION_OUTPUT:
                BUILDER.EXPECTED_PROMOTION_FILE_SHA256,
            BUILDER.DEFAULT_DECISION_OUTPUT:
                BUILDER.EXPECTED_DECISION_FILE_SHA256,
            BUILDER.DEFAULT_EVIDENCE_OUTPUT:
                BUILDER.EXPECTED_EVIDENCE_FILE_SHA256,
        }
        for path, digest in expected.items():
            with self.subTest(path=path):
                self.assertEqual(BUILDER.sha256_file(path), digest)

    def test_bf7b_theoretical_partition_is_exact(self) -> None:
        analysis = self.bundle["analysis"]
        self.assertEqual(len(analysis["promotion_coordinates"]), 50)
        self.assertEqual(
            len(analysis["planned_live_promotion_coordinates"]),
            50,
        )
        self.assertEqual(len(analysis["already_promoted_coordinates"]), 0)
        self.assertEqual(len(analysis["renewal_coordinates"]), 261)
        self.assertEqual(len(analysis["renewal_roots"]), 142)
        self.assertEqual(
            len(analysis["rejected_pending_coordinates"]),
            36,
        )
        self.assertEqual(
            BUILDER.coordinate_digest(analysis["promotion_coordinates"]),
            BUILDER.EXPECTED_PROMOTION_COORDINATE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_bytes(analysis["candidate_blob"]),
            BUILDER.EXPECTED_CANDIDATE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_bytes(analysis["actual_candidate_blob"]),
            BUILDER.EXPECTED_ACTUAL_CANDIDATE_SHA256,
        )

    def test_actions_and_overrides_are_frozen(self) -> None:
        actions = Counter(
            str(row["action"]) for row in self.bundle["evidence_rows"]
        )
        bf7b_actions = Counter(
            str(row["bf7b_action"]) for row in self.bundle["evidence_rows"]
        )
        self.assertEqual(dict(actions), BUILDER.EXPECTED_ACTION_COUNTS)
        self.assertEqual(
            dict(bf7b_actions),
            BUILDER.EXPECTED_BF7B_ACTION_COUNTS,
        )
        self.assertEqual(len(self.bundle["updated_rows"]), 311)
        self.assertEqual(len(self.bundle["evidence_rows"]), 311)
        self.assertEqual(
            sum(
                BUILDER.EXACT_OVERRIDE_FIELD in row
                for row in self.bundle["updated_rows"]
            ),
            51,
        )

    def test_standalone_does_not_claim_official_post_family_promotion(self) -> None:
        policy = self.audit["integration_policy"]
        proof = self.audit["proof"]
        self.assertEqual(
            policy["actual_integration_predecessor"],
            "immutable_bf7b_theoretical_checkpoint",
        )
        self.assertTrue(
            policy[
                "official_post_selector538_rebase_deferred_to_family_consolidation"
            ]
        )
        self.assertTrue(
            proof[
                "standalone_layer_is_theoretical_not_official_promotion_claim"
            ]
        )
        self.assertEqual(self.audit["scope"]["chunk_id"], 2)
        self.assertEqual(
            len(
                self.bundle["analysis"][
                    "selector538_supersession_coordinates"
                ]
            ),
            0,
        )

    def test_public_reports_are_source_free(self) -> None:
        combined = self.audit_content + self.promotion_content
        self.assertIsNone(
            re.search(
                r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
                r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
                combined,
            )
        )
        self.assertIsNone(re.search(r"\b\d+:\d+(?::\d+)?\b", combined))
        self.assertNotIn('"translation"', combined)
        self.assertFalse(self.audit["steam_write_performed"])
        self.assertEqual(
            self.bundle["steam_before"],
            self.bundle["steam_after"],
        )

    def test_output_paths_remain_isolated(self) -> None:
        BUILDER.validate_output_paths(default_args())
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(
                BUILDER.ClosureError,
                "private output",
            ):
                BUILDER.validate_output_paths(
                    default_args(
                        evidence_output=Path(temporary) / "evidence.jsonl"
                    )
                )
        with self.assertRaisesRegex(BUILDER.ClosureError, "live Steam"):
            BUILDER.validate_output_paths(
                default_args(decision_output=BUILDER.LIVE_STEAM_PK)
            )


if __name__ == "__main__":
    unittest.main()
