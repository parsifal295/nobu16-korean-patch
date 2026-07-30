#!/usr/bin/env python3
"""Regression tests for the guarded PK 6:3421 semantic override."""

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
    WORKSTREAM / "build_pk_semantic_flattening_override_3421_v1.py"
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = load_module("pk_semantic_flattening_override_test", BUILDER_PATH)


class PkSemanticFlatteningOverrideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (
            cls.private_content,
            cls.public_content,
            cls.report,
            cls.row,
        ) = BUILDER.build_outputs()

    def test_no_call_adjudication_and_relative_layout(self) -> None:
        self.assertEqual(self.row["coordinate"], "6:3421:0")
        self.assertEqual(self.row["runtime_review"], "not_required")
        self.assertEqual(
            self.report["adjudication"]["repair_status"],
            "repair_not_required",
        )
        self.assertTrue(
            self.report["adjudication"][
                "repair_candidate_application_forbidden"
            ]
        )
        self.assertTrue(
            self.report["layout_evidence"][
                "relative_line_envelope_nonexpanding"
            ]
        )
        self.assertFalse(
            self.report["layout_evidence"][
                "absolute_msggame_widget_width_assumed"
            ]
        )
        self.assertFalse(self.report["steam_write_performed"])

    def test_report_and_serialization_tampering_are_rejected(self) -> None:
        tampered_report = copy.deepcopy(self.report)
        tampered_report["adjudication"][
            "repair_candidate_application_forbidden"
        ] = False
        with self.assertRaises(BUILDER.SemanticOverrideError):
            BUILDER.validate_outputs(
                self.private_content,
                BUILDER.canonical_json(tampered_report),
                tampered_report,
                self.row,
            )

        tampered_row = copy.deepcopy(self.row)
        tampered_row["semantic_flattening_verification"][
            "translation_utf16le_sha256"
        ] = "0" * 64
        with self.assertRaises(BUILDER.SemanticOverrideError):
            BUILDER.validate_outputs(
                BUILDER.canonical_jsonl([tampered_row]),
                self.public_content,
                self.report,
                tampered_row,
            )


if __name__ == "__main__":
    unittest.main()
