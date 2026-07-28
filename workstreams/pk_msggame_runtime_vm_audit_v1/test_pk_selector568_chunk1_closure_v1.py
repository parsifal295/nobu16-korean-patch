#!/usr/bin/env python3
"""Tests for the independent selector-568 chunk-1 closure layer."""

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
BUILDER_PATH = SCRIPT.parent / "build_pk_selector568_chunk1_closure_v1.py"


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
    "pk_selector568_chunk1_closure_test_builder_v1",
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


class Selector568Chunk1ClosureTests(unittest.TestCase):
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

    def test_all_inputs_and_outputs_are_frozen(self) -> None:
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
        for path, (expected_hash, content) in expected_outputs.items():
            with self.subTest(path=path):
                self.assertEqual(BUILDER.sha256_file(path), expected_hash)
                self.assertEqual(path.read_text(encoding="utf-8"), content)

    def test_promotion_renewal_and_rejection_partitions_are_exact(self) -> None:
        analysis = self.bundle["analysis"]
        self.assertEqual(len(analysis["promotion_coordinates"]), 100)
        self.assertEqual(
            len(analysis["planned_live_promotion_coordinates"]),
            97,
        )
        self.assertEqual(len(analysis["already_promoted_coordinates"]), 3)
        self.assertEqual(len(analysis["renewal_coordinates"]), 261)
        self.assertEqual(len(analysis["update_coordinates"]), 361)
        self.assertEqual(
            len(analysis["rejected_pending_coordinates"]),
            31,
        )
        self.assertEqual(
            BUILDER.coordinate_digest(analysis["promotion_coordinates"]),
            BUILDER.EXPECTED_PROMOTION_COORDINATE_SHA256,
        )
        self.assertEqual(
            BUILDER.coordinate_digest(
                analysis["planned_live_promotion_coordinates"]
            ),
            BUILDER.EXPECTED_PLANNED_LIVE_PROMOTION_COORDINATE_SHA256,
        )
        self.assertEqual(
            BUILDER.coordinate_digest(analysis["renewal_coordinates"]),
            BUILDER.EXPECTED_RENEWAL_COORDINATE_SHA256,
        )
        self.assertEqual(
            BUILDER.coordinate_digest(analysis["update_coordinates"]),
            BUILDER.EXPECTED_DECISION_COORDINATE_SHA256,
        )

    def test_actions_and_exact_overrides_are_frozen(self) -> None:
        actions = Counter(
            str(row["action"]) for row in self.bundle["evidence_rows"]
        )
        theoretical = Counter(
            str(row["bf7b_action"]) for row in self.bundle["evidence_rows"]
        )
        self.assertEqual(dict(actions), BUILDER.EXPECTED_ACTION_COUNTS)
        self.assertEqual(
            dict(theoretical),
            BUILDER.EXPECTED_BF7B_ACTION_COUNTS,
        )
        overrides = [
            row
            for row in self.bundle["updated_rows"]
            if BUILDER.EXACT_OVERRIDE_FIELD in row
        ]
        self.assertEqual(len(overrides), 46)
        self.assertTrue(
            all(
                row[BUILDER.EXACT_OVERRIDE_FIELD][
                    "automatic_space_inserted"
                ]
                is False
                for row in overrides
            )
        )

    def test_selector538_family_supersession_is_exact(self) -> None:
        analysis = self.bundle["analysis"]
        superseded = analysis["selector538_supersession_coordinates"]
        renewal = (
            analysis["selector538_renewal_supersession_coordinates"]
        )
        self.assertEqual(len(superseded), 22)
        self.assertEqual(len(renewal), 19)
        self.assertEqual(
            BUILDER.coordinate_digest(superseded),
            BUILDER.EXPECTED_SELECTOR538_SUPERSESSION_COORDINATE_SHA256,
        )
        self.assertEqual(
            BUILDER.coordinate_digest(renewal),
            BUILDER
            .EXPECTED_SELECTOR538_RENEWAL_SUPERSESSION_COORDINATE_SHA256,
        )
        updated = {
            str(row["coordinate"]): row
            for row in self.bundle["updated_rows"]
        }
        for coordinate in superseded:
            self.assertIn(
                "superseded_evidence_binding",
                updated[coordinate]["runtime_vm_verification"],
            )

    def test_temporary_family_alias_does_not_leak_into_rows(self) -> None:
        actual = self.bundle["analysis"]["actual_predecessor_rows"]
        for row in self.bundle["updated_rows"]:
            coordinate = str(row["coordinate"])
            predecessor = actual[("pk_msggame", coordinate)]
            self.assertEqual(
                row.get("selector538_chunk0_update_action"),
                predecessor.get("selector538_chunk0_update_action"),
            )

    def test_actual_projection_reproduces_candidate_and_pending_count(self) -> None:
        analysis = self.bundle["analysis"]
        merged = {
            key: copy.deepcopy(dict(row))
            for key, row in analysis["actual_predecessor_rows"].items()
        }
        for row in self.bundle["updated_rows"]:
            merged[("pk_msggame", str(row["coordinate"]))] = row
        self.assertEqual(
            sum(
                row.get("runtime_review") == "pending"
                for row in merged.values()
            ),
            7_799,
        )
        replacements = {
            BUILDER.parse_coordinate(coordinate): str(row["translation"])
            for (resource, coordinate), row in merged.items()
            if resource == "pk_msggame"
            and isinstance(row.get("translation"), str)
        }
        candidate = BUILDER.BASE_AUDIT.rebuild_packed_with_literals(
            BUILDER.BASE_AUDIT.DEFAULT_PK_CURRENT.read_bytes(),
            replacements,
        )
        self.assertEqual(
            BUILDER.sha256_bytes(candidate),
            BUILDER.EXPECTED_ACTUAL_CANDIDATE_SHA256,
        )

    def test_public_reports_are_source_free_and_chunk_one_bound(self) -> None:
        for content in (self.audit_content, self.promotion_content):
            self.assertIsNone(
                re.search(
                    r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
                    r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af"
                    r"\uf900-\ufaff]",
                    content,
                )
            )
            self.assertNotIn('"translation"', content)
            self.assertNotIn('"exact_maps"', content)
        self.assertEqual(self.audit["scope"]["chunk_id"], 1)
        self.assertEqual(
            self.audit["integration_policy"][
                "actual_integration_predecessor"
            ],
            "post_selector538_family_integrated_ledger",
        )
        self.assertTrue(
            self.audit["proof"]["rejected_chunk1_pending_rows_unchanged"]
        )
        self.assertEqual(
            self.bundle["steam_before"],
            self.bundle["steam_after"],
        )

    def test_output_paths_are_isolated(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(BUILDER.ClosureError):
                BUILDER.validate_output_paths(
                    default_args(
                        audit_output=Path(temporary) / "coverage.json"
                    )
                )


if __name__ == "__main__":
    unittest.main()
