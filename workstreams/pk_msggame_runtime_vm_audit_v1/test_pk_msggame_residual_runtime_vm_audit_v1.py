#!/usr/bin/env python3
"""Regression and tamper tests for the conservative residual VM layer."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
OVERLAY_PATH = (
    WORKSTREAM
    / "build_pk_msggame_residual_runtime_verified_overlay_v1.py"
)
REFLOW_REPORT_PATH = (
    WORKSTREAM
    / "public"
    / "pk_msggame_residual_a_relative_reflow.v1.json"
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


OVERLAY = load_module("pk_residual_runtime_vm_test_overlay", OVERLAY_PATH)
AUDIT = OVERLAY.AUDIT


class PkResidualRuntimeVmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (
            cls.private_content,
            _public_content,
            cls.promotion,
            cls.context,
        ) = OVERLAY.build_outputs()
        cls.rows = [
            json.loads(line)
            for line in cls.private_content.splitlines()
            if line
        ]

    def test_scope_candidate_and_layout_contract(self) -> None:
        coverage = self.context["coverage"]
        self.assertEqual(coverage["scope"]["residual_rows"], 10_913)
        self.assertEqual(
            coverage["scope"]["tier_rows"],
            {"A": 7_295, "B": 1_375, "C": 907, "D": 1_336},
        )
        self.assertEqual(
            coverage["scope"]["tier_a_final_exact_safe_rows"],
            6_735,
        )
        self.assertEqual(
            coverage["scope"]["recomputed_tier_bc_safe_rows"],
            1_785,
        )
        self.assertEqual(
            coverage["scope"]["recomputed_tier_bc_safe_records"],
            1_351,
        )
        self.assertEqual(
            coverage["scope"]["unified_safe_rows"],
            8_520,
        )
        self.assertEqual(
            coverage["scope"]["unified_safe_records"],
            5_199,
        )
        self.assertEqual(
            coverage["scope"]["promotion_eligible_rows"],
            2_945,
        )
        self.assertEqual(
            coverage["scope"]["promotion_eligible_records"],
            1_949,
        )
        self.assertFalse(
            coverage["layout_contract"][
                "absolute_msggame_widget_width_assumed"
            ]
        )
        self.assertFalse(
            coverage["layout_contract"]["pk_msgev_912px_rule_applied"]
        )
        self.assertEqual(len(self.rows), 2_945)
        transition_counts: dict[str, int] = {}
        for row in self.rows:
            transition = row["layout_transition"]
            self.assertEqual(transition["to"], "runtime_verified")
            source_status = transition["from"]
            transition_counts[source_status] = (
                transition_counts.get(source_status, 0) + 1
            )
        self.assertEqual(
            transition_counts,
            {
                "runtime_pending": 2_290,
                "unchanged_from_current": 655,
            },
        )
        self.assertFalse(self.promotion["steam_write_performed"])

    def test_reflowed_residual_row_uses_effective_translation_binding(
        self,
    ) -> None:
        reflow_report = json.loads(
            REFLOW_REPORT_PATH.read_text(encoding="utf-8")
        )
        overlays = {row["coordinate"]: row for row in self.rows}
        shared = sorted(
            set(overlays) & set(reflow_report["row_adjudications"])
        )
        self.assertEqual(len(shared), 23)
        for coordinate in shared:
            overlay_row = overlays[coordinate]
            coverage_row = self.context["coverage"][
                "row_adjudications"
            ][coordinate]
            self.assertEqual(
                overlay_row["translation_utf16le_sha256"],
                coverage_row["translation_utf16le_sha256"],
            )
            self.assertEqual(
                overlay_row["translation_utf16le_sha256"],
                reflow_report["row_adjudications"][coordinate][
                    "after_translation_utf16le_sha256"
                ],
            )
            self.assertEqual(
                overlay_row["source_decision_binding"]["decision_sha256"],
                coverage_row["source_decision_sha256"],
            )

    def test_overlay_and_report_tampering_are_rejected(self) -> None:
        tampered_rows = copy.deepcopy(self.rows)
        tampered_rows[0]["audit_binding"][
            "record_proof_sha256"
        ] = "0" * 64
        with self.assertRaises(OVERLAY.ResidualPromotionError):
            OVERLAY.validate_overlay_rows(
                tampered_rows,
                report=self.context["coverage"],
                report_file_sha256=self.context[
                    "coverage_file_sha256"
                ],
                inputs=self.context["inputs"],
            )

        tampered_report = copy.deepcopy(self.context["coverage"])
        tampered_report["layout_contract"][
            "pk_msgev_912px_rule_applied"
        ] = True
        with self.assertRaises(AUDIT.ResidualAuditError):
            AUDIT.validate_report(
                tampered_report,
                inputs=self.context["inputs"],
                full_metadata={},
            )


if __name__ == "__main__":
    unittest.main()
