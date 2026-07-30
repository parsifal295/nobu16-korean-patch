#!/usr/bin/env python3
"""Tests for the standalone opaque-selector spacing final gate."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


HERE = Path(__file__).resolve().parent
SPECIFICATION = importlib.util.spec_from_file_location(
    "opaque_selector_spacing_final_gate_test_subject",
    HERE / "gate_opaque_selector_spacing_final_v1.py",
)
assert (
    SPECIFICATION is not None
    and SPECIFICATION.loader is not None
)
GATE = importlib.util.module_from_spec(SPECIFICATION)
sys.modules[SPECIFICATION.name] = GATE
SPECIFICATION.loader.exec_module(GATE)
AUDIT = GATE.AUDIT


def resource(
    name: str,
    sha256: str,
    *,
    issues=(),
):
    return AUDIT.OpaqueSelectorResource(
        resource=name,
        path=f"{name}.bin",
        sha256=sha256,
        size=1,
        record_count=1,
        decoded_record_count=1,
        selector_component_count=1,
        lexical_selector_component_count=1,
        lexical_selector_record_count=1,
        person_selector_component_count=1,
        person_selector_record_count=1,
        symbolic_prefix_state_count=1,
        symbolic_selector_tail_state_count=1,
        issues=issues,
    )


class OpaqueSelectorSpacingFinalGateTests(unittest.TestCase):
    def test_zero_issues_is_the_only_pass(self) -> None:
        gate = GATE.build_gate(
            (
                resource("base_msggame", "A" * 64),
                resource("pk_msggame", "B" * 64),
            )
        )
        self.assertEqual(gate["status"], "PASS")
        self.assertEqual(gate["runtime_completion"], "PASS")
        self.assertTrue(gate["runtime_completion_allowed"])
        self.assertEqual(gate["issue_count"], 0)
        self.assertTrue(gate["source_or_translation_bodies_omitted"])
        self.assertRegex(
            gate["audit_contract"]["engine_sha256"],
            r"^[0-9A-F]{64}$",
        )

    def test_exact_issue_blocks_and_remains_source_free(self) -> None:
        issue = AUDIT.OpaqueSelectorSpacingIssue(
            resource="pk_msggame",
            block_id=1,
            record_id=2,
            selector_group=2,
            boundary_class="honorific_nim",
            opaque_tail_sha256="C" * 64,
            tail_complete=True,
        )
        gate = GATE.build_gate(
            (
                resource("base_msggame", "A" * 64),
                resource(
                    "pk_msggame",
                    "B" * 64,
                    issues=(issue,),
                ),
            )
        )
        self.assertEqual(gate["status"], "FAIL")
        self.assertEqual(gate["runtime_completion"], "FAIL")
        self.assertFalse(gate["runtime_completion_allowed"])
        self.assertEqual(gate["issue_count"], 1)
        self.assertNotIn("opaque_tail", gate["issues"][0])

    def test_main_returns_one_for_dirty_candidates(self) -> None:
        issue = AUDIT.OpaqueSelectorSpacingIssue(
            resource="base_msggame",
            block_id=1,
            record_id=2,
            selector_group=3,
            boundary_class="dependent_arae",
            opaque_tail_sha256="C" * 64,
            tail_complete=True,
        )
        dirty = resource(
            "base_msggame",
            "A" * 64,
            issues=(issue,),
        )
        clean = resource("pk_msggame", "B" * 64)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "gate.json"
            with mock.patch.object(
                AUDIT,
                "audit_resource",
                side_effect=(dirty, clean),
            ):
                result = GATE.main(
                    [
                        "--base",
                        "base.bin",
                        "--pk",
                        "pk.bin",
                        "--output",
                        str(output),
                    ]
                )
            self.assertEqual(result, 1)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "FAIL")
            self.assertNotIn("opaque_tail", payload["issues"][0])


if __name__ == "__main__":
    unittest.main()
