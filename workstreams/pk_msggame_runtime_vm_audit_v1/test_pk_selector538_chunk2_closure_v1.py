#!/usr/bin/env python3
"""Tests for the independent selector-538 chunk-2 closure layer."""

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
BUILDER_PATH = SCRIPT.parent / "build_pk_selector538_chunk2_closure_v1.py"


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
    "pk_selector538_chunk2_closure_test_builder_v1",
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


class Selector538Chunk2ClosureTests(unittest.TestCase):
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

    def test_all_frozen_inputs_and_outputs_match_disk(self) -> None:
        expected_inputs = {
            BUILDER.PREDECESSOR_PRIVATE_PATH:
                BUILDER.EXPECTED_PREDECESSOR_PRIVATE_SHA256,
            BUILDER.PREDECESSOR_PUBLIC_PATH:
                BUILDER.EXPECTED_PREDECESSOR_PUBLIC_SHA256,
            BUILDER.PRIVATE_HANDOFF_PATH:
                BUILDER.EXPECTED_HANDOFF_SHA256,
            BUILDER.REVIEW_PUBLIC_PATH:
                BUILDER.EXPECTED_REVIEW_PUBLIC_SHA256,
        }
        for path, expected in expected_inputs.items():
            with self.subTest(path=path):
                self.assertEqual(BUILDER.sha256_file(path), expected)

        expected_outputs = {
            BUILDER.DEFAULT_AUDIT_OUTPUT: (
                BUILDER.EXPECTED_AUDIT_FILE_SHA256,
                self.audit_content,
            ),
            BUILDER.DEFAULT_PROMOTION_OUTPUT: (
                BUILDER.EXPECTED_PROMOTION_FILE_SHA256,
                self.promotion_content,
            ),
            BUILDER.DEFAULT_DECISION_OUTPUT: (
                BUILDER.EXPECTED_DECISION_FILE_SHA256,
                self.decision_content,
            ),
            BUILDER.DEFAULT_EVIDENCE_OUTPUT: (
                BUILDER.EXPECTED_EVIDENCE_FILE_SHA256,
                self.evidence_content,
            ),
        }
        for path, (digest, content) in expected_outputs.items():
            with self.subTest(path=path):
                self.assertEqual(BUILDER.sha256_file(path), digest)
                self.assertEqual(path.read_text(encoding="utf-8"), content)

    def test_reverse_ancestor_partitions_are_exact(self) -> None:
        analysis = self.bundle["analysis"]
        expected_renewal_roots = set(analysis["verified_by_root"]) & (
            analysis["candidate_affected"] | analysis["source_affected"]
        )
        self.assertEqual(analysis["renewal_roots"], expected_renewal_roots)
        self.assertEqual(len(analysis["renewal_roots"]), 204)
        self.assertEqual(len(analysis["renewal_coordinates"]), 420)
        self.assertEqual(
            BUILDER.coordinate_digest(analysis["renewal_coordinates"]),
            BUILDER.EXPECTED_RENEWAL_COORDINATE_SHA256,
        )
        self.assertEqual(len(analysis["promotion_roots"]), 25)
        self.assertEqual(len(analysis["promotion_coordinates"]), 44)
        self.assertEqual(len(analysis["rejected_roots"]), 38)
        self.assertEqual(len(analysis["rejected_pending_roots"]), 32)
        self.assertEqual(
            len(analysis["rejected_pending_coordinates"]),
            57,
        )
        self.assertFalse(
            analysis["promotion_coordinates"]
            & analysis["rejected_pending_coordinates"]
        )
        self.assertEqual(len(analysis["held_unreviewed_roots"]), 183)
        self.assertEqual(
            len(analysis["held_unreviewed_coordinates"]),
            443,
        )

    def test_all_231_accepted_assemblies_and_candidate_are_bound(self) -> None:
        analysis = self.bundle["analysis"]
        self.assertEqual(
            len(analysis["accepted_assembly_manifest"]),
            231,
        )
        self.assertEqual(
            BUILDER.canonical_sha256(
                analysis["accepted_assembly_manifest"]
            ),
            BUILDER.EXPECTED_ACCEPTED_ASSEMBLY_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_bytes(analysis["baseline_blob"]),
            BUILDER.EXPECTED_BASELINE_CANDIDATE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_bytes(analysis["candidate_blob"]),
            BUILDER.EXPECTED_CANDIDATE_SHA256,
        )
        proof = self.audit["proof"]
        self.assertTrue(proof["all_accepted_register_branches_proven"])
        self.assertTrue(proof["all_accepted_width_branches_nonexpanding"])
        self.assertTrue(proof["all_changed_record_control_gaps_preserved"])
        self.assertTrue(proof["all_exact_overrides_applied"])
        self.assertTrue(proof["all_keep_rows_preserved"])

    def test_actions_promote_44_and_renew_all_420_rows(self) -> None:
        actions = Counter(
            str(row["action"]) for row in self.bundle["evidence_rows"]
        )
        self.assertEqual(dict(actions), BUILDER.EXPECTED_ACTION_COUNTS)
        self.assertEqual(
            dict(actions),
            {
                "runtime_promotion": 36,
                "translation_override_and_runtime_promotion": 8,
                "translation_override_and_verification_renewal": 22,
                "verification_renewal": 398,
            },
        )
        self.assertEqual(len(self.bundle["updated_rows"]), 464)
        self.assertEqual(len(self.bundle["evidence_rows"]), 464)
        self.assertEqual(
            self.bundle["promotion"]["result"]["pending_rows_after"],
            8169,
        )
        self.assertEqual(
            self.bundle["promotion"]["result"][
                "verification_renewal_rows"
            ],
            420,
        )
        self.assertTrue(
            all(
                not BUILDER.contains_body_key(row)
                for row in self.bundle["evidence_rows"]
            )
        )
        override_rows = [
            row for row in self.bundle["updated_rows"]
            if BUILDER.EXACT_OVERRIDE_FIELD in row
        ]
        self.assertEqual(len(override_rows), 30)
        self.assertTrue(
            all(
                "selector538_chunk0_exact_override_evidence" not in row
                and "selector538_chunk1_exact_override_evidence" not in row
                for row in self.bundle["updated_rows"]
            )
        )

    def test_public_reports_are_source_free_and_steam_is_unchanged(
        self,
    ) -> None:
        combined = self.audit_content + self.promotion_content
        self.assertIsNone(
            re.search(
                r"[\u1100-\u11ff\u3130-\u318f\u3400-\u4dbf"
                r"\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
                combined,
            )
        )
        self.assertIsNone(re.search(r"\b\d+:\d+(?::\d+)?\b", combined))
        self.assertNotIn('"translation"', combined)
        self.assertNotIn('"exact_maps"', combined)
        self.assertFalse(self.audit["steam_write_performed"])
        self.assertFalse(
            self.bundle["promotion"]["steam_write_performed"]
        )
        self.assertEqual(
            self.bundle["steam_before"],
            self.bundle["steam_after"],
        )

    def test_output_path_guards_reject_escape_and_steam(self) -> None:
        BUILDER.validate_output_paths(default_args())
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(
                BUILDER.ClosureError,
                "private output",
            ):
                BUILDER.validate_output_paths(
                    default_args(
                        decision_output=Path(temporary) / "private.jsonl"
                    )
                )
            with self.assertRaisesRegex(
                BUILDER.ClosureError,
                "public reports",
            ):
                BUILDER.validate_output_paths(
                    default_args(
                        audit_output=Path(temporary) / "public.json"
                    )
                )
        with self.assertRaisesRegex(BUILDER.ClosureError, "live Steam"):
            BUILDER.validate_output_paths(
                default_args(decision_output=BUILDER.LIVE_STEAM_PK)
            )


if __name__ == "__main__":
    unittest.main()
