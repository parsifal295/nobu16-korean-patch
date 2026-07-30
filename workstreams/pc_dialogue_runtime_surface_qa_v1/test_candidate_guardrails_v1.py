#!/usr/bin/env python3
"""Unit tests for structural and relative-width candidate guardrails."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent


def load_module(name: str, filename: str) -> Any:
    path = WORKSTREAM / filename
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


STRUCTURE = load_module(
    "pc_dialogue_candidate_structure_audit_v1",
    "audit_candidate_structure_v1.py",
)
WIDTH = load_module(
    "pc_dialogue_candidate_relative_width_audit_v1",
    "audit_candidate_relative_width_v1.py",
)
FINAL_GATE = load_module(
    "pc_dialogue_final_candidate_gate_v1",
    "gate_final_candidate_v1.py",
)


class CandidateGuardrailTests(unittest.TestCase):
    def test_semantic_boundary_marker_contract(self) -> None:
        self.assertEqual(
            STRUCTURE.semantic_boundary_marker(
                "\ub3c4 \uc6b0\ub9ac\ub97c \ub530\ub974\uaca0\uc2b5\ub2c8\ub2e4"
            ),
            "additive_do",
        )
        self.assertEqual(
            STRUCTURE.semantic_boundary_marker(
                " \ubc0f \ud608\uc5f0\uad00\uacc4\uac00 \uc5c6\uc5b4"
            ),
            "conjunction_mit",
        )
        self.assertEqual(
            STRUCTURE.semantic_boundary_marker(
                "\u300d\ub3c4 \uacc4\uc18d\ud558\uae30 \uc5b4\ub835\uc2b5\ub2c8\ub2e4"
            ),
            "additive_do",
        )
        self.assertIsNone(
            STRUCTURE.semantic_boundary_marker(
                "\uc758 \uc81c\uc548\uc744 \ubc1b\uc558\uc2b5\ub2c8\ub2e4"
            )
        )
        self.assertIsNone(
            STRUCTURE.semantic_boundary_marker(
                "\ub3c4\uc6c0\uc744 \ubc1b\uc744 \uc218 \uc788\uaca0\uc2b5\ub2c8\uae4c?"
            )
        )

    def test_relative_width_uses_48_and_24_cells(self) -> None:
        self.assertEqual(WIDTH.raw_g1n_width_px("가문 A"), 48 * 2 + 24 * 2)
        self.assertEqual(WIDTH.raw_g1n_width_px("ABC 12"), 24 * 6)

    def test_pk_priority_width_exception_is_exact_hash_bound(self) -> None:
        text = "에게 병환이 생겼습니다"
        self.assertTrue(
            WIDTH.approved_growth_exception(
                "pk_msggame",
                (2, 148, 0),
                0,
                432,
                528,
                text,
            )
        )
        self.assertFalse(
            WIDTH.approved_growth_exception(
                "pk_msggame",
                (2, 148, 0),
                0,
                432,
                528,
                text + ".",
            )
        )
        self.assertFalse(
            WIDTH.approved_growth_exception(
                "pk_msggame",
                (2, 148, 0),
                0,
                432,
                552,
                text,
            )
        )

    def test_base_priority_width_exception_is_exact_hash_bound(self) -> None:
        text = "에게도 병환이 들다니…\n…당분간은 힘을 발휘"
        self.assertTrue(
            WIDTH.approved_growth_exception(
                "base_msggame",
                (8, 1020, 1),
                0,
                192,
                528,
                text,
            )
        )
        self.assertFalse(
            WIDTH.approved_growth_exception(
                "base_msggame",
                (8, 1020, 1),
                1,
                192,
                528,
                text,
            )
        )

    def test_only_reviewed_pk_call_retargets_are_allowed(self) -> None:
        self.assertTrue(
            STRUCTURE.allowed_component_change(
                "pk_msggame",
                (6, 3541),
                3,
                STRUCTURE.CALL_376,
                STRUCTURE.CALL_520,
            )
        )
        self.assertTrue(
            STRUCTURE.allowed_component_change(
                "pk_msggame",
                (15, 1545),
                2,
                STRUCTURE.CALL_376,
                STRUCTURE.CALL_1247,
            )
        )
        self.assertTrue(
            STRUCTURE.allowed_component_change(
                "pk_msggame",
                (6, 3768),
                7,
                STRUCTURE.CALL_748,
                STRUCTURE.CALL_1247,
            )
        )
        self.assertTrue(
            STRUCTURE.allowed_component_change(
                "pk_msggame",
                (6, 4917),
                7,
                STRUCTURE.CALL_748,
                STRUCTURE.CALL_1247,
            )
        )
        self.assertFalse(
            STRUCTURE.allowed_component_change(
                "base_msggame",
                (6, 3541),
                3,
                STRUCTURE.CALL_376,
                STRUCTURE.CALL_520,
            )
        )
        self.assertFalse(
            STRUCTURE.allowed_component_change(
                "pk_msggame",
                (6, 3542),
                3,
                STRUCTURE.CALL_376,
                STRUCTURE.CALL_520,
            )
        )

    def test_ghidra_contract_binds_verbatim_runtime_assembly(self) -> None:
        document = FINAL_GATE.load_selector_domain_contract()
        adjudication = document["adjudication"]
        self.assertTrue(adjudication["automatic_space_insertion_is_absent"])
        self.assertTrue(
            adjudication[
                "literal_and_selector_utf16_units_are_copied_verbatim"
            ]
        )
        self.assertTrue(adjudication["opcode_0143_calls_another_record"])
        live_session = document["live_session"]
        self.assertEqual(live_session["transport"], "GhidraMCP HTTP bridge")
        self.assertTrue(live_session["forced_decompile_refreshed"])
        assembler = document["fresh_decompile_checks"][
            "runtime_assembler_0x140A013B0"
        ]
        self.assertTrue(
            assembler["opcode_0x02_copies_resolved_utf16_units"]
        )
        self.assertFalse(
            assembler["injected_separator_or_particle_branch_observed"]
        )


if __name__ == "__main__":
    unittest.main()
