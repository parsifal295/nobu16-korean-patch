#!/usr/bin/env python3
"""Tests for the independent selector-568 chunk-0 closure layer."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import re
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.parent / "build_pk_selector568_chunk0_closure_v1.py"


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
    "pk_selector568_chunk0_closure_test_builder_v1",
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


class Selector568Chunk0ClosureTests(unittest.TestCase):
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
            BUILDER.ACTUAL_PREDECESSOR_PATH:
                BUILDER.EXPECTED_ACTUAL_PREDECESSOR_SHA256,
            BUILDER.PRIVATE_HANDOFF_PATH:
                BUILDER.EXPECTED_HANDOFF_SHA256,
            BUILDER.REVIEW_PUBLIC_PATH:
                BUILDER.EXPECTED_REVIEW_PUBLIC_SHA256,
            BUILDER.SELECTOR538_DECISION_PATH:
                BUILDER.EXPECTED_SELECTOR538_DECISION_SHA256,
            BUILDER.SELECTOR538_EVIDENCE_PATH:
                BUILDER.EXPECTED_SELECTOR538_EVIDENCE_SHA256,
            BUILDER.SELECTOR538_PROMOTION_PATH:
                BUILDER.EXPECTED_SELECTOR538_PROMOTION_SHA256,
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

    def test_bf7b_and_actual_promotion_partitions_are_distinct(self) -> None:
        analysis = self.bundle["analysis"]
        potential = analysis["promotion_coordinates"]
        planned_live = analysis["planned_live_promotion_coordinates"]
        already = analysis["already_promoted_coordinates"]
        self.assertEqual(len(potential), 92)
        self.assertEqual(len(planned_live), 87)
        self.assertEqual(len(already), 5)
        self.assertEqual(potential, planned_live | already)
        self.assertFalse(planned_live & already)
        self.assertEqual(
            BUILDER.coordinate_digest(potential),
            BUILDER.EXPECTED_PROMOTION_COORDINATE_SHA256,
        )
        self.assertEqual(
            BUILDER.coordinate_digest(planned_live),
            BUILDER.EXPECTED_PLANNED_LIVE_PROMOTION_COORDINATE_SHA256,
        )
        self.assertEqual(
            BUILDER.coordinate_digest(already),
            BUILDER.EXPECTED_ALREADY_PROMOTED_COORDINATE_SHA256,
        )
        self.assertEqual(len(analysis["renewal_coordinates"]), 261)
        self.assertEqual(len(analysis["renewal_roots"]), 142)
        self.assertEqual(len(analysis["rejected_pending_coordinates"]), 39)

    def test_actions_freeze_promotions_renewals_and_overrides(self) -> None:
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
        self.assertEqual(len(self.bundle["updated_rows"]), 353)
        self.assertEqual(len(self.bundle["evidence_rows"]), 353)
        override_rows = [
            row for row in self.bundle["updated_rows"]
            if BUILDER.EXACT_OVERRIDE_FIELD in row
        ]
        self.assertEqual(len(override_rows), 59)
        self.assertEqual(
            sum("runtime_promotion" in action for action in actions.elements()),
            87,
        )
        self.assertEqual(
            actions["translation_override_and_verification_renewal"]
            + actions["verification_renewal"],
            261,
        )

    def test_selector538_evidence_is_explicitly_superseded(self) -> None:
        analysis = self.bundle["analysis"]
        superseded = analysis["selector538_supersession_coordinates"]
        renewal_superseded = (
            analysis["selector538_renewal_supersession_coordinates"]
        )
        evidence_by_coordinate = {
            str(row["coordinate"]): row
            for row in self.bundle["evidence_rows"]
        }
        self.assertEqual(len(superseded), 24)
        self.assertEqual(len(renewal_superseded), 19)
        self.assertEqual(
            BUILDER.coordinate_digest(superseded),
            BUILDER.EXPECTED_SELECTOR538_SUPERSESSION_COORDINATE_SHA256,
        )
        for coordinate in superseded:
            binding = evidence_by_coordinate[coordinate][
                "superseded_evidence_binding"
            ]
            self.assertEqual(binding["selector"], 538)
            self.assertEqual(
                binding["evidence_file_sha256"],
                BUILDER.EXPECTED_SELECTOR538_EVIDENCE_SHA256,
            )
        already_actions = Counter(
            evidence_by_coordinate[coordinate]["action"]
            for coordinate in analysis["already_promoted_coordinates"]
        )
        self.assertEqual(
            already_actions,
            Counter(
                {
                    "evidence_supersession": 4,
                    "translation_override_and_evidence_supersession": 1,
                }
            ),
        )

    def test_actual_projection_promotes_only_87_pending_rows(self) -> None:
        analysis = self.bundle["analysis"]
        merged = {
            key: copy.deepcopy(dict(row))
            for key, row in analysis["actual_predecessor_rows"].items()
        }
        pending_before = sum(
            row.get("runtime_review") == "pending" for row in merged.values()
        )
        merged.update(
            {
                ("pk_msggame", str(row["coordinate"])): row
                for row in self.bundle["updated_rows"]
            }
        )
        pending_after = sum(
            row.get("runtime_review") == "pending" for row in merged.values()
        )
        self.assertEqual(pending_before, 8113)
        self.assertEqual(pending_after, 8026)
        self.assertTrue(
            all(
                merged[("pk_msggame", coordinate)]["runtime_review"]
                == "verified"
                for coordinate
                in analysis["planned_live_promotion_coordinates"]
            )
        )
        promotion = self.bundle["promotion"]["result"]
        self.assertEqual(
            promotion["bf7b_potential_runtime_promotion_rows"],
            92,
        )
        self.assertEqual(
            promotion["planned_live_runtime_promotion_rows"],
            87,
        )
        self.assertEqual(
            BUILDER.sha256_bytes(analysis["candidate_blob"]),
            BUILDER.EXPECTED_CANDIDATE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_bytes(analysis["actual_candidate_blob"]),
            BUILDER.EXPECTED_ACTUAL_CANDIDATE_SHA256,
        )

    def test_public_reports_and_output_paths_remain_safe(self) -> None:
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
        self.assertNotIn('"exact_maps"', combined)
        self.assertFalse(self.audit["steam_write_performed"])
        self.assertFalse(self.bundle["promotion"]["steam_write_performed"])
        self.assertEqual(
            self.bundle["steam_before"],
            self.bundle["steam_after"],
        )
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
