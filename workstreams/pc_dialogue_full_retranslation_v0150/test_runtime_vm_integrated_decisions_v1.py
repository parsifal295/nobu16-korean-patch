#!/usr/bin/env python3
"""Regression tests for the v0.15.0 runtime VM integration boundary."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT_ROOT = REPO / "tmp" / WORKSTREAM.name
INTEGRATED = OUTPUT_ROOT / "runtime_vm_integrated.private.v1.jsonl"
REPORT = WORKSTREAM / "runtime_vm_integration.source_free.v1.json"
PROGRESS = WORKSTREAM / "progress.source_free.v1.json"
SHADOW_STEAM_ROOT = (
    OUTPUT_ROOT / "development_steam_root_pre_base_runtime_apply_13a404f"
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_module("runtime_vm_integration_test_engine", ENGINE_PATH)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


class RuntimeVmIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.prepared = ENGINE.prepare_artifacts(
            SHADOW_STEAM_ROOT,
            ENGINE.DEFAULT_BASE_PRISTINE,
            (
                SHADOW_STEAM_ROOT
                / "KR_PATCH_BACKUP"
                / "file_only_transaction"
                / "steam-jp-1.1.7-v0.6.0"
                / "originals"
                / "MSG_PK"
                / "JP"
                / "msggame.bin"
            ),
        )
        cls.rows = read_jsonl(INTEGRATED)

    def validate_rows(self, rows: list[dict[str, Any]]) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "decisions.private.v1.jsonl"
            path.write_text(ENGINE.jsonl(rows), encoding="utf-8", newline="\n")
            ENGINE.validate_decisions(
                self.prepared,
                path,
                require_complete=False,
            )

    def test_integrated_universe_and_source_free_counts(self) -> None:
        self.assertEqual(len(self.rows), 52_803)
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        progress = json.loads(PROGRESS.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["promotions"]["promoted_total"], 27_716)
        self.assertEqual(report["result"]["runtime_review_pending"], 8_618)
        self.assertEqual(
            report["result"]["private_integrated_decision_sha256"],
            "9245DED68D1A8DFA51B0587E5E2B1B7165BF610CB4618460654D4032B04E1F10",
        )
        self.assertEqual(
            report["promotions"]["pk_msggame"]["promotion_count"],
            12_065,
        )
        self.assertEqual(
            report["promotions"]["pk_msggame"]["residual"][
                "promotion_count"
            ],
            2_945,
        )
        self.assertEqual(
            report["promotions"]["pk_msggame"]["pk_only_exact_blocked"][
                "promotion_count"
            ],
            1_536,
        )
        self.assertTrue(
            report["promotions"]["pk_msggame"]["full_candidate_bound"]
        )
        self.assertTrue(
            report["promotions"]["pk_msggame"]["pk_only_layer_included"]
        )
        self.assertTrue(
            report["promotions"]["pk_msggame"][
                "pk_only_predecessor_checkpoint_match"
            ]
        )
        self.assertEqual(
            report["promotions"]["pk_msggame"][
                "cross_resource_exact_closure"
            ]["promotion_count"],
            50,
        )
        self.assertTrue(
            report["promotions"]["pk_msggame"][
                "cross_resource_layer_included"
            ]
        )
        self.assertTrue(
            report["promotions"]["pk_msggame"][
                "cross_resource_predecessor_checkpoint_match"
            ]
        )
        self.assertTrue(
            report["promotions"]["pk_msggame"][
                "dynamic_honorific_spacing_layer_included"
            ]
        )
        self.assertEqual(
            report["promotions"]["pk_msggame"][
                "dynamic_honorific_spacing"
            ]["promotion_count"],
            57,
        )
        self.assertEqual(
            report["promotions"]["pk_msggame"][
                "dynamic_honorific_spacing"
            ]["translation_override_count"],
            4,
        )
        self.assertTrue(
            report["validation"][
                "pk_only_predecessor_checkpoint_rebuilt_and_matched"
            ]
        )
        self.assertTrue(
            report["validation"][
                "cross_resource_predecessor_checkpoint_rebuilt_and_matched"
            ]
        )
        self.assertEqual(
            report["promotions"]["relative_reflow_override"][
                "override_count"
            ],
            26,
        )
        self.assertFalse(report["steam_write_performed"])
        self.assertEqual(
            progress["totals"]["runtime_review_pending"],
            8_618,
        )
        self.assertEqual(
            progress["runtime_vm_integration"][
                "private_integrated_decision_sha256"
            ],
            report["result"]["private_integrated_decision_sha256"],
        )
        self.assertTrue(
            report["promotions"]["pk_msggame"][
                "bound_terminal_family_layer_included"
            ]
        )
        terminal = report["promotions"]["pk_msggame"][
            "bound_terminal_family"
        ]
        self.assertEqual(terminal["translation_override_count"], 14)
        self.assertEqual(terminal["verification_renewal_count"], 685)
        self.assertEqual(terminal["promotion_count"], 4)
        self.assertEqual(terminal["pending_override_count"], 6)
        self.assertEqual(
            terminal["pk_candidate_packed_sha256"],
            "902CD3A1372BC19ABCA846C6A9F43195085C0782994ECFCE8A8353B2F9E0A628",
        )
        self.assertTrue(
            progress["runtime_vm_integration"][
                "bound_terminal_family_layer_included"
            ]
        )
        self.assertEqual(
            progress["runtime_vm_integration"][
                "bound_terminal_family_override_count"
            ],
            14,
        )
        self.assertTrue(
            report["promotions"]["pk_msggame"][
                "thought_predicate_family_layer_included"
            ]
        )
        thought = report["promotions"]["pk_msggame"][
            "thought_predicate_family"
        ]
        self.assertEqual(
            report["promotions"]["pk_msggame"][
                "rebuilt_post_bound_integrated_private_sha256"
            ],
            "F6BAA43C22404365E49D40C6B306C850C3B123681CD0A42D5A63EDB73D8018FB",
        )
        self.assertEqual(thought["translation_override_count"], 75)
        self.assertEqual(thought["verification_renewal_count"], 53)
        self.assertEqual(thought["promotion_count"], 23)
        self.assertEqual(thought["updated_row_count"], 76)
        self.assertTrue(
            progress["runtime_vm_integration"][
                "thought_predicate_family_layer_included"
            ]
        )
        self.assertEqual(
            progress["runtime_vm_integration"][
                "thought_predicate_family_override_count"
            ],
            75,
        )
        self.assertTrue(
            report["validation"][
                "post_bound_predecessor_checkpoint_rebuilt_and_matched"
            ]
        )

    def test_pk_verified_row_is_bound_to_exact_overlay(self) -> None:
        source = next(
            row
            for row in self.rows
            if row["resource"] == "pk_msggame"
            and row["runtime_review"] == "verified"
            and row["runtime_vm_verification"]["method"]
            == "reversed_vm_full_candidate_static_analysis"
        )
        self.validate_rows([source])

        missing = copy.deepcopy(source)
        missing.pop("runtime_vm_verification")
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([missing])

        tampered = copy.deepcopy(source)
        tampered["runtime_vm_verification"][
            "translation_utf16le_sha256"
        ] = "0" * 64
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([tampered])

    def test_pk_residual_row_binds_runtime_and_layout_transitions(self) -> None:
        source = next(
            row
            for row in self.rows
            if row["resource"] == "pk_msggame"
            and row["runtime_review"] == "verified"
            and row["runtime_vm_verification"]["method"]
            == "reversed_vm_residual_full_closure_nonexpansion_analysis"
        )
        self.assertEqual(source["layout_review"], "runtime_verified")
        self.validate_rows([source])

        bad_layout = copy.deepcopy(source)
        bad_layout["layout_review"] = "runtime_pending"
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([bad_layout])

        bad_evidence = copy.deepcopy(source)
        bad_evidence["runtime_vm_verification"]["layout_transition"][
            "to"
        ] = "runtime_pending"
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([bad_evidence])

    def test_pk_only_exact_blocked_row_preserves_layout_binding(self) -> None:
        source = next(
            row
            for row in self.rows
            if row["resource"] == "pk_msggame"
            and row["runtime_review"] == "verified"
            and row["runtime_vm_verification"]["method"]
            == "reversed_vm_pk_only_exact_blocked_closure_nonexpansion_analysis"
        )
        self.assertEqual(source["layout_review"], "unchanged_from_current")
        self.assertEqual(
            source["runtime_vm_verification"]["layout_review_binding"],
            {"status": "unchanged_from_current"},
        )
        self.validate_rows([source])

        bad_layout = copy.deepcopy(source)
        bad_layout["layout_review"] = "runtime_verified"
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([bad_layout])

        bad_binding = copy.deepcopy(source)
        bad_binding["runtime_vm_verification"]["layout_review_binding"][
            "status"
        ] = "runtime_verified"
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([bad_binding])

    def test_cross_resource_exact_closure_row_preserves_layout_binding(
        self,
    ) -> None:
        source = next(
            row
            for row in self.rows
            if row["resource"] == "pk_msggame"
            and row["runtime_review"] == "verified"
            and row["runtime_vm_verification"]["method"]
            == "reversed_vm_cross_resource_exact_closure_analysis"
        )
        self.assertEqual(source["layout_review"], "runtime_verified")
        self.assertEqual(
            source["runtime_vm_verification"]["layout_transition"],
            {
                "from": source["runtime_vm_verification"][
                    "layout_review_binding"
                ]["status"],
                "to": "runtime_verified",
            },
        )
        self.validate_rows([source])

        bad_binding = copy.deepcopy(source)
        bad_binding["runtime_vm_verification"]["layout_review_binding"][
            "status"
        ] = "runtime_verified"
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([bad_binding])

        bad_width_proof = copy.deepcopy(source)
        bad_width_proof["runtime_vm_verification"][
            "cross_resource_closure_binding"
        ]["relative_layout_guard"]["reason_codes"] = [
            "relative_line_width_expansion"
        ]
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([bad_width_proof])

    def test_dynamic_honorific_override_is_exact_and_bound(self) -> None:
        targets = [
            row
            for row in self.rows
            if row.get("runtime_boundary_leading_space_inserted") is True
        ]
        self.assertEqual(len(targets), 4)
        self.assertEqual(
            {
                (row["resource"], row["coordinate"])
                for row in targets
            },
            ENGINE.RUNTIME_BOUNDARY_LEADING_SPACE_COORDINATES,
        )
        for source in targets:
            self.assertEqual(source["translation"], " 공")
            self.assertEqual(
                source["runtime_vm_verification"]["action"],
                "translation_override",
            )
            self.validate_rows([source])

            missing_flag = copy.deepcopy(source)
            missing_flag.pop("runtime_boundary_leading_space_inserted")
            with self.assertRaises(ENGINE.RetranslationError):
                self.validate_rows([missing_flag])

            doubled_space = copy.deepcopy(source)
            doubled_space["translation"] = "  공"
            doubled_space["runtime_vm_verification"][
                "translation_utf16le_sha256"
            ] = ENGINE.sha256_text("  공")
            with self.assertRaises(ENGINE.RetranslationError):
                self.validate_rows([doubled_space])

    def test_dynamic_honorific_promotion_requires_width_proof(self) -> None:
        source = next(
            row
            for row in self.rows
            if row["resource"] == "pk_msggame"
            and row.get("runtime_vm_verification", {}).get("method")
            == "reversed_vm_dynamic_honorific_spacing_closure_analysis"
            and row["runtime_vm_verification"]["action"]
            == "runtime_promotion"
        )
        self.assertEqual(source["layout_review"], "runtime_verified")
        self.validate_rows([source])

        bad_width = copy.deepcopy(source)
        bad_width["runtime_vm_verification"]["pk_promoted_root_binding"][
            "relative_full_closure_line_envelope_nonexpanding"
        ] = False
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([bad_width])

    def test_bound_terminal_exact_overrides_and_pending_rejections(
        self,
    ) -> None:
        targets = [
            row
            for row in self.rows
            if row.get("terminal_family_exact_override_evidence")
            is not None
        ]
        self.assertEqual(len(targets), 14)
        self.assertEqual(
            {row["coordinate"] for row in targets},
            {
                *(f"0:{record_id}:0" for record_id in range(1916, 1923)),
                *(f"0:{record_id}:0" for record_id in range(2546, 2553)),
            },
        )
        pending = [
            row
            for row in targets
            if row["terminal_family_update_action"]
            == "translation_override_pending"
        ]
        self.assertEqual(
            {row["coordinate"] for row in pending},
            {
                "0:2546:0",
                "0:2547:0",
                "0:2548:0",
                "0:2549:0",
                "0:2550:0",
                "0:2552:0",
            },
        )
        for source in targets:
            exact = source["terminal_family_exact_override_evidence"]
            self.assertTrue(exact["bound_ending_only"])
            self.assertTrue(exact["lexical_predicate_removed"])
            self.assertTrue(exact["caller_predicate_stem_required"])
            self.validate_rows([source])
        for source in pending:
            self.assertEqual(source["runtime_review"], "pending")
            self.assertNotIn("runtime_vm_verification", source)
            self.assertEqual(
                source["terminal_family_runtime_evidence"]["status"],
                "pending",
            )
            tampered = copy.deepcopy(source)
            tampered["terminal_family_runtime_evidence"]["status"] = (
                "verified"
            )
            with self.assertRaises(ENGINE.RetranslationError):
                self.validate_rows([tampered])

    def test_bound_terminal_promotions_require_exact_closure_proof(
        self,
    ) -> None:
        promotions = [
            row
            for row in self.rows
            if row.get("runtime_vm_verification", {}).get("method")
            == (
                "reversed_vm_pk_bound_terminal_family_exact_"
                "closure_analysis"
            )
            and row["runtime_vm_verification"]["action"]
            in {
                "runtime_promotion",
                "translation_override_and_runtime_promotion",
            }
        ]
        self.assertEqual(
            {row["coordinate"] for row in promotions},
            {"0:1917:0", "0:1922:0", "0:2551:0", "8:1241:0"},
        )
        for source in promotions:
            self.validate_rows([source])
            binding = source["runtime_vm_verification"][
                "actual_promotion_binding"
            ]
            self.assertTrue(binding["manual_full_assembly_verified"])
            self.assertTrue(binding["hard_grammar_risk_absent"])
            self.assertTrue(
                binding[
                    "relative_full_closure_line_envelope_nonexpanding"
                ]
            )
        tampered = copy.deepcopy(promotions[0])
        tampered["runtime_vm_verification"][
            "actual_promotion_binding"
        ]["manual_full_assembly_verified"] = False
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([tampered])

    def test_bound_terminal_verified_evidence_renewal_is_bound(self) -> None:
        renewed = [
            row
            for row in self.rows
            if row.get("runtime_vm_verification", {}).get("method")
            == (
                "reversed_vm_pk_bound_terminal_family_exact_"
                "closure_analysis"
            )
            and row["runtime_vm_verification"]["action"]
            in {"verification_renewal", "translation_override"}
        ]
        # Five earlier bound renewals are superseded by exact
        # thought-predicate renewal evidence in the final layer.
        self.assertEqual(len(renewed), 680)
        source = renewed[0]
        self.assertTrue(
            source["runtime_vm_verification"][
                "preexisting_verified_evidence_renewed"
            ]
        )
        self.validate_rows([source])

        tampered = copy.deepcopy(source)
        tampered["runtime_vm_verification"][
            "translation_utf16le_sha256"
        ] = "0" * 64
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([tampered])

    def test_thought_predicate_actions_and_overrides_are_exact(self) -> None:
        targets = [
            row
            for row in self.rows
            if row.get("runtime_vm_verification", {}).get("method")
            == (
                "reversed_vm_pk_thought_predicate_family_exact_"
                "closure_analysis"
            )
        ]
        self.assertEqual(len(targets), 76)
        actions = {
            action: sum(
                row["thought_predicate_family_update_action"] == action
                for row in targets
            )
            for action in {
                "runtime_promotion",
                "translation_override_and_runtime_promotion",
                "translation_override_and_verification_renewal",
            }
        }
        self.assertEqual(
            actions,
            {
                "runtime_promotion": 1,
                "translation_override_and_runtime_promotion": 22,
                "translation_override_and_verification_renewal": 53,
            },
        )
        overrides = [
            row
            for row in targets
            if row["thought_predicate_family_update_action"]
            != "runtime_promotion"
        ]
        self.assertEqual(len(overrides), 75)
        for source in targets:
            evidence = source["runtime_vm_verification"]
            self.assertTrue(evidence["full_incoming_closure_verified"])
            self.assertTrue(evidence["grammar_complete_for_all_registers"])
            self.assertTrue(
                evidence["actual_current_relative_nonexpanding"]
            )
            self.validate_rows([source])

    def test_thought_predicate_evidence_and_action_are_bound(self) -> None:
        source = next(
            row
            for row in self.rows
            if row.get("runtime_vm_verification", {}).get("method")
            == (
                "reversed_vm_pk_thought_predicate_family_exact_"
                "closure_analysis"
            )
            and row["thought_predicate_family_update_action"]
            == "translation_override_and_runtime_promotion"
        )
        tampered_hash = copy.deepcopy(source)
        tampered_hash["runtime_vm_verification"][
            "updated_translation_utf16le_sha256"
        ] = "0" * 64
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([tampered_hash])

        tampered_proof = copy.deepcopy(source)
        tampered_proof["runtime_vm_verification"][
            "grammar_complete_for_all_registers"
        ] = False
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([tampered_proof])

        missing_action = copy.deepcopy(source)
        missing_action.pop("thought_predicate_family_update_action")
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([missing_action])

    def test_thought_predicate_supersedes_exact_bound_renewals(self) -> None:
        superseded = [
            row
            for row in self.rows
            if row.get("thought_predicate_family_update_action")
            == "translation_override_and_verification_renewal"
            and row.get("terminal_family_update_action")
            == "verification_renewal"
        ]
        self.assertEqual(
            {row["coordinate"] for row in superseded},
            {
                "6:3551:1",
                "6:4398:0",
                "6:4437:0",
                "15:1430:1",
                "15:1698:1",
            },
        )
        for source in superseded:
            self.validate_rows([source])
        tampered = copy.deepcopy(superseded[0])
        tampered["terminal_family_update_action"] = "runtime_promotion"
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([tampered])


if __name__ == "__main__":
    unittest.main()
