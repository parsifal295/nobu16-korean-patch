#!/usr/bin/env python3
"""Tests for the PK 2546 full caller closure builder."""

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
    SCRIPT.parent / "build_pk_bound_terminal_2546_full_caller_closure_v1.py"
)
SPEC = importlib.util.spec_from_file_location(
    "pk_bound_terminal_2546_full_caller_closure_under_test",
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
        "check": True,
    }
    values.update(updates)
    return argparse.Namespace(**values)


class BoundTerminal2546FullCallerClosureTests(unittest.TestCase):
    def test_private_handoffs_are_strict_hash_bound_and_private(self) -> None:
        first, second = BUILDER.load_handoffs()
        expected_privacy = {
            "classification": "private",
            "public": False,
            "shared": False,
            "tracked": False,
        }
        self.assertEqual(first["privacy"], expected_privacy)
        self.assertEqual(second["privacy"], expected_privacy)
        self.assertEqual(first["scope"]["selector_coordinate"], "0:1066:0")
        self.assertEqual(second["scope"]["selector_coordinate"], "0:1066:0")
        self.assertEqual(
            tuple(first["scope"]["terminal_coordinates"]),
            BUILDER.EXPECTED_TERMINALS,
        )
        self.assertEqual(
            tuple(second["scope"]["terminal_coordinates"]),
            BUILDER.EXPECTED_TERMINALS,
        )

    def test_strict_loader_rejects_hash_tamper_and_invalid_utf8(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original = BUILDER.HANDOFF_000_151_PATH.read_bytes()
            tampered = root / "tampered.json"
            tampered.write_bytes(original + b" ")
            with self.assertRaisesRegex(
                BUILDER.ClosureError,
                "hash drifted",
            ):
                BUILDER.load_utf8_json_exact(
                    tampered,
                    BUILDER.EXPECTED_HANDOFF_000_151_SHA256,
                    "family2546_ord000_151_analysis.private.v1",
                )

            invalid = root / "invalid.json"
            invalid.write_bytes(b'{"schema":"' + b"\xff" + b'"}')
            with self.assertRaisesRegex(
                BUILDER.ClosureError,
                "not strict UTF-8",
            ):
                BUILDER.load_utf8_json_exact(
                    invalid,
                    BUILDER.sha256_file(invalid),
                    "irrelevant",
                )

    def test_predecessor_checkpoint_is_exactly_frozen(self) -> None:
        rows, report = BUILDER.load_predecessor()
        self.assertEqual(len(rows), BUILDER.EXPECTED_PREDECESSOR_ROWS)
        pending = sum(
            row.get("runtime_review") == "pending"
            for row in rows.values()
        )
        self.assertEqual(pending, BUILDER.EXPECTED_PREDECESSOR_PENDING)
        self.assertEqual(
            report["result"]["private_integrated_decision_sha256"],
            BUILDER.EXPECTED_PREDECESSOR_PRIVATE_SHA256,
        )

    def test_independent_residual_ledger_is_exactly_bound(self) -> None:
        ledger = BUILDER.load_residual_ledger()
        self.assertTrue(all(ledger["assertions"].values()))
        self.assertEqual(ledger["counts"]["promotion_rows"], 364)
        self.assertEqual(ledger["counts"]["verified_renewal_rows"], 292)
        self.assertEqual(
            ledger["digests"]["decision_evidence_delta_coordinate_sha256"],
            BUILDER.EXPECTED_DECISION_COORDINATE_SHA256,
        )
        self.assertFalse(ledger["privacy"]["contains_translation_bodies"])

    def test_source_free_guard_rejects_bodies_maps_and_text(self) -> None:
        rejected_values = [
            {"translation": "redacted"},
            {"exact_final_override_map": {}},
            {"nested": [{"accepted_sites": []}]},
            {"safe": "\ud55c\uad6d\uc5b4"},
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
        self.assertEqual(len(bundle["updated_rows"]), 656)
        self.assertEqual(len(bundle["evidence_rows"]), 656)
        self.assertEqual(audit["scope"]["post_layer_pending_rows"], 8_213)
        self.assertEqual(audit["proof"]["unknown_selector_sites"], 0)
        self.assertEqual(
            audit["guards"]["independent_residual_ledger_sha256"],
            BUILDER.EXPECTED_RESIDUAL_LEDGER_SHA256,
        )
        self.assertFalse(audit["steam_write_performed"])
        self.assertEqual(bundle["steam_before"], bundle["steam_after"])
        self.assertFalse(
            json.loads(audit_content)["distribution_policy"][
                "tracked_report_contains_translation_map_keys"
            ]
        )


if __name__ == "__main__":
    unittest.main()
