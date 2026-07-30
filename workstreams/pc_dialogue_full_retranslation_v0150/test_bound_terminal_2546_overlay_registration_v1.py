#!/usr/bin/env python3
"""Targeted tests for the PK bound-terminal 2546 evidence registration."""

from __future__ import annotations

import collections
import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
ENGINE_PATH = SCRIPT.parent / "build_pc_dialogue_full_retranslation_v0150.py"
SPEC = importlib.util.spec_from_file_location(
    "pc_dialogue_full_retranslation_2546_engine_under_test",
    ENGINE_PATH,
)
assert SPEC is not None and SPEC.loader is not None
ENGINE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ENGINE
SPEC.loader.exec_module(ENGINE)

DECISION_DELTA_PATH = (
    ENGINE.DEFAULT_OUTPUT_ROOT
    / "semantic_overrides"
    / (
        "pk_bound_terminal_2546_full_caller_closure_"
        "integrated_decisions.private.v1.jsonl"
    )
)


class BoundTerminal2546OverlayRegistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay_rows = ENGINE.load_pk_runtime_vm_overlays()
        cls.predecessor_rows = (
            ENGINE.load_bound_terminal_2546_predecessor_rows()
        )
        cls.decision_rows = [
            json.loads(line)
            for line in DECISION_DELTA_PATH.read_text(
                encoding="utf-8"
            ).splitlines()
            if line
        ]
        cls.new_overlay_rows = {
            coordinate: row
            for (schema, coordinate), row in cls.overlay_rows.items()
            if schema
            == ENGINE.PK_BOUND_TERMINAL_2546_RUNTIME_VM_EVIDENCE_ROW_SCHEMA
        }

    def test_frozen_paths_schema_method_action_and_public_seals(self) -> None:
        promotion, audit = (
            ENGINE.load_bound_terminal_2546_public_contract()
        )
        self.assertEqual(len(self.new_overlay_rows), 656)
        self.assertEqual(
            collections.Counter(
                row["action"] for row in self.new_overlay_rows.values()
            ),
            collections.Counter(
                {
                    action: count
                    for action, count in (
                        ENGINE
                        .PK_BOUND_TERMINAL_2546_EXPECTED_ACTION_COUNTS
                        .items()
                    )
                    if count
                }
            ),
        )
        self.assertEqual(
            promotion["method"],
            ENGINE.PK_BOUND_TERMINAL_2546_RUNTIME_VM_VERIFICATION_METHOD,
        )
        self.assertEqual(
            audit["guards"]["candidate_sha256"],
            ENGINE.PK_BOUND_TERMINAL_2546_CANDIDATE_SHA256,
        )
        self.assertFalse(promotion["steam_write_performed"])
        self.assertFalse(audit["steam_write_performed"])

    def test_all_rows_bind_exact_predecessor_and_decision_transition(
        self,
    ) -> None:
        for row in self.decision_rows:
            coordinate = row["coordinate"]
            predecessor = self.predecessor_rows[
                ("pk_msggame", coordinate)
            ]
            ENGINE.validate_bound_terminal_2546_decision_row(
                row,
                predecessor=predecessor,
                label=coordinate,
            )
            ENGINE.validate_pk_runtime_vm_verification(
                evidence=row["runtime_vm_verification"],
                overlay_rows=self.overlay_rows,
                coordinate_value=coordinate,
                translation=row["translation"],
                layout_review=row["layout_review"],
                resource=row["resource"],
                scope_classification=row["scope_classification"],
                label=coordinate,
            )

    def test_full_engine_accepts_the_656_row_delta_only(self) -> None:
        prepared = ENGINE.prepare_artifacts(
            ENGINE.DEFAULT_STEAM_ROOT,
            ENGINE.DEFAULT_BASE_PRISTINE,
            ENGINE.DEFAULT_PK_PRISTINE,
        )
        replacements = ENGINE.validate_decisions(
            prepared,
            DECISION_DELTA_PATH,
            require_complete=False,
        )
        self.assertEqual(len(replacements), 656)

    def test_closure_predecessor_and_action_tampering_is_rejected(self) -> None:
        audit = ENGINE.load_bound_terminal_2546_public_contract()[1]
        coordinate = "0:2546:0"
        original = self.new_overlay_rows[coordinate]
        predecessor_rows = self.predecessor_rows
        cases = []

        closure_tamper = copy.deepcopy(original)
        closure_tamper["closure_binding"]["candidate_sha256"] = "0" * 64
        cases.append(closure_tamper)

        predecessor_tamper = copy.deepcopy(original)
        predecessor_tamper["predecessor_binding"]["row_sha256"] = "0" * 64
        cases.append(predecessor_tamper)

        pending_action = copy.deepcopy(original)
        pending_action["action"] = "translation_override_pending"
        pending_action["status"] = "pending"
        cases.append(pending_action)

        for row in cases:
            with self.subTest(action=row["action"]):
                with self.assertRaises(ENGINE.RetranslationError):
                    ENGINE.validate_bound_terminal_2546_overlay_row(
                        row,
                        predecessor_rows=predecessor_rows,
                        audit=audit,
                    )

    def test_verified_caller_supersession_is_exactly_two_coordinates(
        self,
    ) -> None:
        actual = set()
        for coordinate, row in self.new_overlay_rows.items():
            predecessor = self.predecessor_rows[
                ("pk_msggame", coordinate)
            ]
            previous = predecessor.get("runtime_vm_verification")
            if (
                isinstance(previous, dict)
                and previous.get("method")
                == (
                    ENGINE
                    .PK_BOUND_TERMINAL_CALLER_RUNTIME_VM_VERIFICATION_METHOD
                )
                and (
                    "pk_msggame",
                    coordinate,
                )
                in (
                    ENGINE
                    .BOUND_TERMINAL_2546_SUPERSEDED_CALLER_VERIFIED_COORDINATES
                )
            ):
                actual.add(("pk_msggame", coordinate))
                self.assertEqual(
                    predecessor["bound_terminal_caller_update_action"],
                    "translation_override_and_verification_renewal",
                )
                self.assertEqual(
                    row["predecessor_binding"]["row_sha256"],
                    ENGINE.canonical_sha256(predecessor),
                )
        self.assertEqual(
            actual,
            ENGINE.BOUND_TERMINAL_2546_SUPERSEDED_CALLER_VERIFIED_COORDINATES,
        )

        special_coordinate = "15:277:1"
        tampered_decision = copy.deepcopy(
            next(
                row
                for row in self.decision_rows
                if row["coordinate"] == special_coordinate
            )
        )
        tampered_decision.pop("bound_terminal_caller_update_action")
        with self.assertRaisesRegex(
            ENGINE.RetranslationError,
            "preserve",
        ):
            ENGINE.validate_bound_terminal_2546_decision_row(
                tampered_decision,
                predecessor=self.predecessor_rows[
                    ("pk_msggame", special_coordinate)
                ],
                label=special_coordinate,
            )

    def test_public_seal_tamper_is_rejected(self) -> None:
        promotion = ENGINE.load_bound_terminal_2546_public_contract()[0]
        tampered = copy.deepcopy(promotion)
        tampered["result"]["runtime_promotion_rows"] += 1
        with self.assertRaisesRegex(
            ENGINE.RetranslationError,
            "payload seal",
        ):
            ENGINE.validate_source_free_report_seal(
                tampered,
                "tampered promotion",
            )


if __name__ == "__main__":
    unittest.main()
