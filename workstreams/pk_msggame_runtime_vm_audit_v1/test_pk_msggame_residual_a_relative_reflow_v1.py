#!/usr/bin/env python3
"""Regression and tamper tests for the exact-nonnewline PK reflow layer."""

from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
BUILDER_PATH = (
    WORKSTREAM / "build_pk_msggame_residual_a_relative_reflow_v1.py"
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = load_module(
    "pk_residual_a_relative_reflow_test_builder",
    BUILDER_PATH,
)


class PkResidualARelativeReflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (
            cls.private_content,
            cls.public_content,
            cls.report,
            cls.context,
        ) = BUILDER.build_outputs()
        cls.rows = cls.context["rows"]

    def test_exact_scope_and_relative_only_contract(self) -> None:
        scope = self.report["scope"]
        self.assertEqual(scope["exact_nonnewline_safe_root_rows"], 39)
        self.assertEqual(scope["exact_nonnewline_safe_root_records"], 26)
        self.assertEqual(scope["private_override_rows"], 26)
        self.assertEqual(scope["private_override_records"], 26)
        self.assertEqual(
            self.report["guards"]["exact_safe_root_coordinate_sha256"],
            BUILDER.EXPECTED_EXACT_SAFE_ROOT_COORDINATE_SHA256,
        )
        self.assertEqual(
            self.report["guards"]["override_coordinate_sha256"],
            BUILDER.EXPECTED_OVERRIDE_COORDINATE_SHA256,
        )
        layout = self.report["layout_contract"]
        self.assertFalse(layout["absolute_msggame_widget_width_assumed"])
        self.assertFalse(layout["pk_msgev_912px_rule_applied"])
        self.assertFalse(self.report["steam_write_performed"])

    def test_every_override_preserves_strong_invariants(self) -> None:
        candidate = self.context["candidate"]
        for row in self.rows:
            block_id, record_id, literal_id = BUILDER.parse_coordinate(
                row["coordinate"]
            )
            before_record = candidate["before_records"][
                (block_id, record_id)
            ]
            after_record = candidate["after_records"][(block_id, record_id)]
            before = BUILDER.ENGINE.parse_record_literals(before_record)[
                literal_id
            ].text
            after = row["translation"]
            self.assertEqual(
                BUILDER.nonnewline_text(before),
                BUILDER.nonnewline_text(after),
            )
            self.assertEqual(before.count("\n"), after.count("\n"))
            self.assertEqual(
                BUILDER.ENGINE.protected_signature(before),
                BUILDER.ENGINE.protected_signature(after),
            )
            self.assertEqual(
                BUILDER.nonnewline_whitespace_signature(before),
                BUILDER.nonnewline_whitespace_signature(after),
            )
            self.assertEqual(
                BUILDER.ENGINE.record_gap_bytes(before_record),
                BUILDER.ENGINE.record_gap_bytes(after_record),
            )
            self.assertEqual(
                BUILDER.component_sha256(before_record),
                BUILDER.component_sha256(after_record),
            )
            contract = row["exact_nonnewline_contract"]
            self.assertTrue(contract["all_after_lines_nonexpanding"])
            self.assertTrue(
                all(
                    after_width <= current_width
                    for after_width, current_width in zip(
                        contract["after_line_widths"],
                        contract["current_ko_line_envelope"],
                    )
                )
            )

    def test_private_override_tampering_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.rows)
        tampered[0]["translation"] += "X"
        with self.assertRaises(BUILDER.RelativeReflowError):
            BUILDER.validate_override_rows(
                tampered,
                expected=self.rows,
                candidate=self.context["candidate"],
            )

        newline_tampered = copy.deepcopy(self.rows)
        translation = newline_tampered[0]["translation"]
        newline_index = translation.index("\n")
        newline_tampered[0]["translation"] = (
            "\n" + translation[:newline_index] + translation[newline_index + 1 :]
        )
        with self.assertRaises(BUILDER.RelativeReflowError):
            BUILDER.validate_override_rows(
                newline_tampered,
                expected=self.rows,
                candidate=self.context["candidate"],
            )

    def test_resealed_public_report_tampering_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.report)
        tampered["layout_contract"]["pk_msgev_912px_rule_applied"] = True
        unsealed = copy.deepcopy(tampered)
        unsealed["guards"].pop("report_payload_sha256", None)
        tampered["guards"]["report_payload_sha256"] = (
            BUILDER.canonical_sha256(unsealed)
        )
        with self.assertRaises(BUILDER.RelativeReflowError):
            BUILDER.validate_report(
                tampered,
                expected=self.report,
            )

    def test_candidate_and_record_manifests_are_pinned(self) -> None:
        binding = self.report["candidate_binding"]
        self.assertEqual(
            binding["after_reflow_candidate_packed_sha256"],
            BUILDER.EXPECTED_REFLOWED_CANDIDATE_SHA256,
        )
        self.assertEqual(
            binding["reflow_override_manifest_sha256"],
            BUILDER.EXPECTED_REFLOW_REPLACEMENT_MANIFEST_SHA256,
        )
        self.assertEqual(
            binding["changed_record_manifest_sha256"],
            BUILDER.EXPECTED_CHANGED_RECORD_MANIFEST_SHA256,
        )
        self.assertTrue(
            self.report["prior_probe_mismatch"][
                "legacy_count_is_not_used_for_this_layer"
            ]
        )
        self.assertTrue(
            self.report["prior_probe_mismatch"][
                "stale_exact_probe_is_not_used_for_this_layer"
            ]
        )


if __name__ == "__main__":
    unittest.main()
