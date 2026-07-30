#!/usr/bin/env python3
"""Tests for the PK 2546 simple-caller closure builder."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = (
    SCRIPT.parent
    / "build_pk_bound_terminal_2546_simple_caller_closure_v1.py"
)
SPEC = importlib.util.spec_from_file_location(
    "pk_bound_terminal_2546_simple_caller_closure_under_test",
    BUILDER_PATH,
)
assert SPEC is not None and SPEC.loader is not None
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


def default_args(**updates: Path | bool) -> argparse.Namespace:
    values = {
        "audit_output": BUILDER.DEFAULT_AUDIT_OUTPUT,
        "promotion_output": BUILDER.DEFAULT_PROMOTION_OUTPUT,
        "decision_output": BUILDER.DEFAULT_DECISION_OUTPUT,
        "evidence_output": BUILDER.DEFAULT_EVIDENCE_OUTPUT,
        "write": False,
        "check": True,
    }
    values.update(updates)
    return argparse.Namespace(**values)


class BoundTerminal2546SimpleCallerClosureTests(unittest.TestCase):
    def test_predecessor_is_exactly_frozen(self) -> None:
        rows, report = BUILDER.load_predecessor()
        self.assertEqual(len(rows), BUILDER.EXPECTED_ROWS)
        self.assertEqual(
            sum(
                row.get("runtime_review") == "pending"
                for row in rows.values()
            ),
            BUILDER.EXPECTED_PENDING_BEFORE,
        )
        self.assertEqual(
            report["result"]["private_integrated_decision_sha256"],
            BUILDER.EXPECTED_PREDECESSOR_PRIVATE_SHA256,
        )

    def test_proposal_rebuild_rechecks_all_63_assemblies(self) -> None:
        private, public = BUILDER.load_and_rebuild_proposal()
        self.assertEqual(
            private["counts"]["register_assemblies"],
            BUILDER.EXPECTED_ASSEMBLIES,
        )
        self.assertTrue(
            private["proof"][
                "all_7_register_assemblies_current_relative_"
                "raw_g1n_nonexpanding"
            ]
        )
        self.assertTrue(
            public["proof"]["control_topology_preserved_for_all_roots"]
        )

    def test_partition_is_exact_and_action_counts_are_actual(self) -> None:
        private, _public = BUILDER.load_and_rebuild_proposal()
        partition = BUILDER.build_partition(private)
        self.assertEqual(len(partition["promotion"]), 23)
        self.assertEqual(len(partition["renewal"]), 5)
        self.assertEqual(len(partition["overrides"]), 17)
        self.assertEqual(
            {
                action: len(coordinates)
                for action, coordinates in partition["actions"].items()
            },
            BUILDER.EXPECTED_ACTION_COUNTS,
        )

    def test_source_free_guard_rejects_text_coordinates_and_bodies(self) -> None:
        rejected_values = [
            {"translation": "redacted"},
            {"safe": "\ud55c\uad6d\uc5b4"},
            {"safe": "15:313:0"},
        ]
        for value in rejected_values:
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
                    default_args(decision_output=root / "private.jsonl")
                )
            with self.assertRaisesRegex(
                BUILDER.ClosureError,
                "fixed tracked",
            ):
                BUILDER.validate_output_paths(
                    default_args(audit_output=root / "public.json")
                )
        with self.assertRaisesRegex(BUILDER.ClosureError, "live Steam"):
            BUILDER.validate_output_paths(
                default_args(decision_output=BUILDER.LIVE_STEAM_PK)
            )

    def test_full_build_reproduces_frozen_closure(self) -> None:
        (
            decision_content,
            evidence_content,
            audit_content,
            promotion_content,
            audit,
            bundle,
        ) = BUILDER.build_outputs()
        BUILDER.validate_outputs(
            decision_content=decision_content,
            evidence_content=evidence_content,
            audit_content=audit_content,
            promotion_content=promotion_content,
            audit=audit,
            bundle=bundle,
        )
        self.assertEqual(len(bundle["updated_rows"]), 28)
        self.assertEqual(len(bundle["evidence_rows"]), 28)
        self.assertEqual(audit["scope"]["post_layer_pending_rows"], 8_190)
        self.assertEqual(
            audit["proof"]["register_assemblies_recomputed"],
            63,
        )
        self.assertFalse(audit["steam_write_performed"])
        self.assertEqual(bundle["steam_before"], bundle["steam_after"])
        self.assertEqual(
            BUILDER.body_key_count(json.loads(audit_content)),
            0,
        )
        self.assertEqual(BUILDER.body_key_count(bundle["evidence_rows"]), 0)


if __name__ == "__main__":
    unittest.main()
