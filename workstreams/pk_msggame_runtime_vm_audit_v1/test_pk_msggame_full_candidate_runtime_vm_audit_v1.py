#!/usr/bin/env python3
"""Tamper and completeness tests for the full-candidate PK VM audit."""

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
    / "build_pk_msggame_full_candidate_runtime_verified_overlay_v1.py"
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


OVERLAY = load_module("pk_full_candidate_runtime_vm_test_overlay", OVERLAY_PATH)
FULL_AUDIT = OVERLAY.FULL_AUDIT


class PkFullCandidateRuntimeVmTests(unittest.TestCase):
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

    def test_full_candidate_scope_and_transitions(self) -> None:
        coverage = self.context["coverage"]
        self.assertEqual(coverage["scope"]["runtime_pending_rows"], 9_770)
        self.assertEqual(coverage["scope"]["promotion_eligible_rows"], 7_450)
        self.assertEqual(coverage["scope"]["blocked_rows"], 2_320)
        self.assertEqual(
            coverage["candidate_scope"]["literal_candidate_packed_sha256"],
            FULL_AUDIT.EXPECTED_FULL_CANDIDATE_SHA256,
        )
        transitions = coverage["full_candidate_transitions"]
        self.assertEqual(transitions["kept_eligible_rows"], 4_660)
        self.assertEqual(transitions["newly_eligible_rows"], 2_790)
        self.assertEqual(transitions["newly_blocked_rows"], 57)
        self.assertEqual(
            coverage["candidate_scope"][
                "relative_reflow_exact_rows_superseded"
            ],
            3,
        )
        self.assertEqual(
            coverage["blockers"][
                "pk_source_candidate_control_taint_rows"
            ],
            13,
        )
        self.assertEqual(len(self.rows), 7_450)
        self.assertFalse(self.promotion["steam_write_performed"])

    def test_overlay_and_report_tampering_are_rejected(self) -> None:
        tampered_rows = copy.deepcopy(self.rows)
        tampered_rows[0]["full_candidate_binding"][
            "pk_full_candidate_packed_sha256"
        ] = "0" * 64
        with self.assertRaises(OVERLAY.FullCandidatePromotionError):
            OVERLAY.validate_overlay_rows(
                tampered_rows,
                report=self.context["coverage"],
                report_file_sha256=self.context["coverage_file_sha256"],
                inputs=self.context["inputs"],
            )

        tampered_report = copy.deepcopy(self.context["coverage"])
        tampered_report["candidate_scope"][
            "literal_candidate_packed_sha256"
        ] = "0" * 64
        with self.assertRaises(FULL_AUDIT.FullCandidateAuditError):
            FULL_AUDIT.validate_report(
                tampered_report,
                inputs=self.context["inputs"],
                metadata=self.context["metadata"],
            )


if __name__ == "__main__":
    unittest.main()
