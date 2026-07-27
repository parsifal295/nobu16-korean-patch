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
        self.assertEqual(report["promotions"]["promoted_total"], 28_144)
        self.assertEqual(report["result"]["runtime_review_pending"], 8_190)
        self.assertEqual(report["result"]["fully_candidate_eligible"], 44_613)
        self.assertEqual(
            report["result"]["private_integrated_decision_sha256"],
            "5A789D888F3BB353F37BC74779D2C91F5BCB5542CD17842C9371F49AB53C1ABF",
        )
        self.assertEqual(
            report["promotions"]["pk_msggame"]["promotion_count"],
            12_493,
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
            8_213,
        )
        self.assertEqual(
            progress["runtime_vm_integration"][
                "private_integrated_decision_sha256"
            ],
            (
                "BF7B89E425502144C0A1992872895A774"
                "C56BADCA1FE8DD34ED6778CF3A627C5"
            ),
        )
        self.assertNotEqual(
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
        self.assertTrue(
            report["promotions"]["pk_msggame"][
                "bound_terminal_caller_layer_included"
            ]
        )
        caller = report["promotions"]["pk_msggame"][
            "bound_terminal_caller"
        ]
        self.assertEqual(caller["translation_override_count"], 261)
        self.assertEqual(caller["ledger_backed_override_count"], 257)
        self.assertEqual(caller["literal_only_override_count"], 4)
        self.assertEqual(caller["verification_renewal_count"], 120)
        self.assertEqual(caller["promotion_count"], 41)
        self.assertEqual(caller["updated_row_count"], 313)
        self.assertEqual(
            caller["overlap_final_evidence_sha256"],
            "BD82EF31C36A7E32FA6E0A3D59A27A54E0528369CD661D9603E42B49109FB998",
        )
        self.assertEqual(
            caller["combined_verified_renewal_evidence_manifest_sha256"],
            "0EC7E69CAB57E15F646D98005D023160AAA97A8A4A3E0D7DDB09F6E2AD4D7F67",
        )
        self.assertEqual(
            caller["pk_candidate_packed_sha256"],
            "498A9A19FA33B57789C6FBF3732DA61967FEDE8055F034F68E43E628C16ED74F",
        )
        self.assertTrue(
            progress["runtime_vm_integration"][
                "bound_terminal_caller_layer_included"
            ]
        )
        self.assertEqual(
            progress["runtime_vm_integration"][
                "bound_terminal_caller_override_count"
            ],
            257,
        )
        self.assertTrue(
            report["promotions"]["pk_msggame"][
                "bound_terminal_2546_full_caller_layer_included"
            ]
        )
        terminal_2546 = report["promotions"]["pk_msggame"][
            "bound_terminal_2546_full_caller"
        ]
        self.assertEqual(terminal_2546["translation_override_count"], 216)
        self.assertEqual(terminal_2546["verification_renewal_count"], 292)
        self.assertEqual(terminal_2546["promotion_count"], 364)
        self.assertEqual(terminal_2546["updated_row_count"], 656)
        self.assertEqual(terminal_2546["rejected_pending_count"], 74)
        self.assertEqual(
            terminal_2546["action_counts"],
            {
                "runtime_promotion": 279,
                "translation_override_and_runtime_promotion": 85,
                "translation_override_and_verification_renewal": 131,
                "verification_renewal": 161,
            },
        )
        self.assertEqual(
            terminal_2546["predecessor_integrated_private_sha256"],
            "54B4255C29F256B84E1CA4EE8A9B5D21FE254100A2A71CA28657F7EF6EB34E45",
        )
        self.assertEqual(
            terminal_2546["pk_candidate_packed_sha256"],
            "D5F704C82DD9CBDFB92CD6502B90B11D95C883DEA7EFCC1BD50A05A4758B9C0E",
        )
        self.assertEqual(
            report["promotions"]["pk_msggame"][
                "rebuilt_post_bound_terminal_caller_integrated_private_sha256"
            ],
            "54B4255C29F256B84E1CA4EE8A9B5D21FE254100A2A71CA28657F7EF6EB34E45",
        )
        self.assertTrue(
            report["validation"][
                "post_bound_terminal_caller_predecessor_checkpoint_rebuilt_and_matched"
            ]
        )
        self.assertTrue(
            report["validation"][
                "caller_overlap_actions_preserved_and_superseded"
            ]
        )
        self.assertTrue(
            report["promotions"]["pk_msggame"][
                "bound_terminal_2546_simple_caller_layer_included"
            ]
        )
        simple = report["promotions"]["pk_msggame"][
            "bound_terminal_2546_simple_caller"
        ]
        self.assertEqual(simple["translation_override_count"], 17)
        self.assertEqual(simple["verification_renewal_count"], 5)
        self.assertEqual(simple["promotion_count"], 23)
        self.assertEqual(simple["updated_row_count"], 28)
        self.assertEqual(
            simple["action_counts"],
            {
                "runtime_promotion": 9,
                "translation_override_and_runtime_promotion": 14,
                "translation_override_and_verification_renewal": 3,
                "verification_renewal": 2,
            },
        )
        self.assertEqual(
            simple["predecessor_integrated_private_sha256"],
            "BF7B89E425502144C0A1992872895A774C56BADCA1FE8DD34ED6778CF3A627C5",
        )
        self.assertEqual(
            simple["pk_candidate_packed_sha256"],
            "C59CA74634E8A1FB0BBBFA3FE3A324AFC0ED06FDF7D707444116D5862A6C2C75",
        )
        self.assertEqual(simple["superseded_verified_evidence_count"], 5)
        self.assertTrue(
            report["validation"][
                "post_bound_terminal_2546_full_caller_predecessor_"
                "checkpoint_rebuilt_and_matched"
            ]
        )
        self.assertTrue(
            report["validation"][
                "historical_actions_preserved_and_exactly_superseded"
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
            self.assertEqual(source["runtime_review"], "verified")
            self.assertEqual(
                source["bound_terminal_2546_full_caller_update_action"],
                "runtime_promotion",
            )
            self.assertEqual(
                source["runtime_vm_verification"]["method"],
                "reversed_vm_pk_bound_terminal_2546_full_caller_closure",
            )
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
            {"0:1917:0", "0:1922:0", "8:1241:0"},
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
        # Later thought, caller, and selector-1066 closure layers supersede
        # this evidence while retaining its historical action metadata.
        self.assertEqual(len(renewed), 386)
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
        self.assertEqual(len(targets), 72)
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
                "translation_override_and_verification_renewal": 49,
            },
        )
        overrides = [
            row
            for row in targets
            if row["thought_predicate_family_update_action"]
            != "runtime_promotion"
        ]
        self.assertEqual(len(overrides), 71)
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

    def test_bound_terminal_caller_actions_and_promotions_are_exact(
        self,
    ) -> None:
        targets = [
            row
            for row in self.rows
            if row.get("bound_terminal_caller_update_action") is not None
        ]
        self.assertEqual(len(targets), 313)
        actions = {
            action: sum(
                row["bound_terminal_caller_update_action"] == action
                for row in targets
            )
            for action in {
                "translation_override_pending",
                "translation_override_and_verification_renewal",
                "verification_renewal",
                "translation_override_and_runtime_promotion",
                "runtime_promotion",
            }
        }
        self.assertEqual(
            actions,
            {
                "translation_override_pending": 152,
                "translation_override_and_verification_renewal": 74,
                "verification_renewal": 46,
                "translation_override_and_runtime_promotion": 31,
                "runtime_promotion": 10,
            },
        )
        promoted = [
            row
            for row in targets
            if row["bound_terminal_caller_update_action"]
            in {
                "translation_override_and_runtime_promotion",
                "runtime_promotion",
            }
        ]
        self.assertEqual(len(promoted), 41)
        source = promoted[0]
        self.validate_rows([source])
        tampered = copy.deepcopy(source)
        tampered["runtime_vm_verification"][
            "actual_promotion_binding"
        ]["manual_full_assembly_verified"] = False
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([tampered])

    def test_bound_terminal_caller_pending_evidence_is_bound(self) -> None:
        source = next(
            row
            for row in self.rows
            if row.get("bound_terminal_caller_update_action")
            == "translation_override_pending"
        )
        self.assertEqual(source["runtime_review"], "pending")
        self.validate_rows([source])
        tampered = copy.deepcopy(source)
        tampered["bound_terminal_caller_runtime_evidence"][
            "translation_utf16le_sha256"
        ] = "0" * 64
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([tampered])

    def test_caller_preserves_superseded_bound_renewal_actions(self) -> None:
        expected = {
            "6:3863:0",
            "6:3863:2",
            "6:3863:3",
            "6:3941:0",
            "6:3941:1",
            "6:3941:2",
            "15:277:1",
            "15:278:1",
            "15:703:0",
            "15:703:1",
            "15:703:2",
        }
        superseded = [
            row
            for row in self.rows
            if row["resource"] == "pk_msggame"
            and row["coordinate"] in expected
        ]
        self.assertEqual({row["coordinate"] for row in superseded}, expected)
        for source in superseded:
            self.assertEqual(
                source["terminal_family_update_action"],
                "verification_renewal",
            )
            expected_method = (
                "reversed_vm_pk_bound_terminal_2546_full_caller_closure"
                if source["coordinate"]
                in {
                    "6:3863:0",
                    "6:3863:2",
                    "6:3863:3",
                    "15:277:1",
                    "15:278:1",
                }
                else (
                    "reversed_vm_pk_bound_terminal_caller_"
                    "full_closure_analysis"
                )
            )
            self.assertEqual(
                source["runtime_vm_verification"]["method"],
                expected_method,
            )
            self.validate_rows([source])

    def test_caller_overlap_preserves_thought_and_rebinds_combined_proof(
        self,
    ) -> None:
        source = next(
            row
            for row in self.rows
            if row["resource"] == "pk_msggame"
            and row["coordinate"] == "15:1068:0"
        )
        self.assertEqual(source["translation"], "을 수복하겠다")
        self.assertEqual(
            source["thought_predicate_family_update_action"],
            "translation_override_and_verification_renewal",
        )
        self.assertEqual(
            source["bound_terminal_caller_update_action"],
            "verification_renewal",
        )
        evidence = source["runtime_vm_verification"]
        self.assertEqual(
            evidence["method"],
            "reversed_vm_pk_bound_terminal_caller_full_closure_analysis",
        )
        binding = evidence["combined_final_binding"]
        self.assertEqual(
            binding["pk_candidate_packed_sha256"],
            "498A9A19FA33B57789C6FBF3732DA61967FEDE8055F034F68E43E628C16ED74F",
        )
        self.assertEqual(
            binding["candidate_record_raw_sha256"],
            "564F81EBB9353750EAFAB190D1A5E3F1050783E0B4D5D526DD7A60DC2F8AC109",
        )
        self.assertTrue(binding["thought_translation_preserved"])
        self.validate_rows([source])
        for field in (
            "pk_candidate_packed_sha256",
            "candidate_record_raw_sha256",
            "root_delta_proof_sha256",
        ):
            tampered = copy.deepcopy(source)
            tampered["runtime_vm_verification"][
                "combined_final_binding"
            ][field] = "0" * 64
            with self.assertRaises(ENGINE.RetranslationError):
                self.validate_rows([tampered])

    def test_bound_terminal_2546_full_caller_actions_are_exact(self) -> None:
        field = "bound_terminal_2546_full_caller_update_action"
        targets = [row for row in self.rows if row.get(field) is not None]
        self.assertEqual(len(targets), 656)
        actions = {
            action: sum(row[field] == action for row in targets)
            for action in {
                "runtime_promotion",
                "translation_override_and_runtime_promotion",
                "translation_override_and_verification_renewal",
                "verification_renewal",
            }
        }
        self.assertEqual(
            actions,
            {
                "runtime_promotion": 279,
                "translation_override_and_runtime_promotion": 85,
                "translation_override_and_verification_renewal": 131,
                "verification_renewal": 161,
            },
        )
        promoted = [
            row
            for row in targets
            if row[field]
            in {
                "runtime_promotion",
                "translation_override_and_runtime_promotion",
            }
        ]
        renewed = [
            row
            for row in targets
            if row[field]
            in {
                "verification_renewal",
                "translation_override_and_verification_renewal",
            }
        ]
        overridden = [
            row
            for row in targets
            if str(row[field]).startswith("translation_override")
        ]
        self.assertEqual(len(promoted), 364)
        self.assertEqual(len(renewed), 292)
        self.assertEqual(len(overridden), 216)
        self.assertTrue(
            all(row["runtime_review"] == "verified" for row in targets)
        )
        simple_superseded = {
            "15:313:0",
            "15:313:1",
            "15:2095:1",
            "15:2095:2",
            "15:2326:0",
        }
        self.assertTrue(
            all(
                row["runtime_vm_verification"]["method"]
                == "reversed_vm_pk_bound_terminal_2546_full_caller_closure"
                and row["runtime_vm_verification"]["action"] == row[field]
                and row["runtime_vm_verification"]["predecessor_binding"][
                    "checkpoint_sha256"
                ]
                == (
                    "54B4255C29F256B84E1CA4EE8A9B5D21"
                    "FE254100A2A71CA28657F7EF6EB34E45"
                )
                and row["runtime_vm_verification"]["closure_binding"][
                    "candidate_sha256"
                ]
                == (
                    "D5F704C82DD9CBDFB92CD6502B90B11"
                    "D95C883DEA7EFCC1BD50A05A4758B9C0E"
                )
                for row in targets
                if row["coordinate"] not in simple_superseded
            )
        )
        source = promoted[0]
        self.validate_rows([source])

        bad_predecessor = copy.deepcopy(source)
        bad_predecessor["runtime_vm_verification"][
            "predecessor_binding"
        ]["row_sha256"] = "0" * 64
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([bad_predecessor])

        bad_action = copy.deepcopy(source)
        bad_action[field] = "verification_renewal"
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([bad_action])

    def test_bound_terminal_2546_supersedes_exact_caller_overlaps(
        self,
    ) -> None:
        expected = {"15:277:1", "15:278:1"}
        overlaps = [
            row
            for row in self.rows
            if row["resource"] == "pk_msggame"
            and row["coordinate"] in expected
        ]
        self.assertEqual(
            {row["coordinate"] for row in overlaps},
            expected,
        )
        for source in overlaps:
            self.assertEqual(
                source["terminal_family_update_action"],
                "verification_renewal",
            )
            self.assertEqual(
                source["bound_terminal_caller_update_action"],
                "translation_override_and_verification_renewal",
            )
            self.assertEqual(
                source["bound_terminal_2546_full_caller_update_action"],
                "translation_override_and_verification_renewal",
            )
            evidence = source["runtime_vm_verification"]
            self.assertEqual(
                evidence["method"],
                "reversed_vm_pk_bound_terminal_2546_full_caller_closure",
            )
            self.assertTrue(
                evidence["preexisting_verified_evidence_renewed"]
            )
            self.validate_rows([source])

            caller_tamper = copy.deepcopy(source)
            caller_tamper["bound_terminal_caller_update_action"] = (
                "verification_renewal"
            )
            with self.assertRaises(ENGINE.RetranslationError):
                self.validate_rows([caller_tamper])

            terminal_tamper = copy.deepcopy(source)
            terminal_tamper["terminal_family_update_action"] = (
                "runtime_promotion"
            )
            with self.assertRaises(ENGINE.RetranslationError):
                self.validate_rows([terminal_tamper])

    def test_bound_terminal_2546_simple_caller_is_exactly_integrated(
        self,
    ) -> None:
        field = "bound_terminal_2546_simple_caller_update_action"
        targets = [row for row in self.rows if row.get(field) is not None]
        self.assertEqual(len(targets), 28)
        self.assertEqual(
            {
                action: sum(row[field] == action for row in targets)
                for action in {
                    "runtime_promotion",
                    "translation_override_and_runtime_promotion",
                    "translation_override_and_verification_renewal",
                    "verification_renewal",
                }
            },
            {
                "runtime_promotion": 9,
                "translation_override_and_runtime_promotion": 14,
                "translation_override_and_verification_renewal": 3,
                "verification_renewal": 2,
            },
        )
        self.assertEqual(
            sum(
                "bound_terminal_2546_simple_caller_"
                "exact_override_evidence" in row
                for row in targets
            ),
            17,
        )
        self.assertTrue(
            all(
                row["runtime_vm_verification"]["method"]
                == (
                    "reversed_vm_pk_bound_terminal_2546_"
                    "simple_caller_retranslation_closure"
                )
                and row["runtime_vm_verification"]["action"] == row[field]
                and row["runtime_vm_verification"]["predecessor_binding"][
                    "checkpoint_sha256"
                ]
                == (
                    "BF7B89E425502144C0A1992872895A774"
                    "C56BADCA1FE8DD34ED6778CF3A627C5"
                )
                and row["runtime_vm_verification"]["closure_binding"][
                    "candidate_sha256"
                ]
                == (
                    "C59CA74634E8A1FB0BBBFA3FE3A324AF"
                    "C0ED06FDF7D707444116D5862A6C2C75"
                )
                for row in targets
            )
        )
        expected_superseded = {
            "15:313:0",
            "15:313:1",
            "15:2095:1",
            "15:2095:2",
            "15:2326:0",
        }
        superseded = {
            row["coordinate"]
            for row in targets
            if row.get("bound_terminal_2546_full_caller_update_action")
            == "verification_renewal"
            and row["runtime_vm_verification"][
                "preexisting_verified_evidence_renewed"
            ]
            is True
        }
        self.assertEqual(superseded, expected_superseded)
        renewal = next(
            row
            for row in targets
            if row["coordinate"] == "15:313:0"
        )
        self.assertEqual(
            renewal["terminal_family_update_action"],
            "verification_renewal",
        )
        self.validate_rows([renewal])

        historical_tamper = copy.deepcopy(renewal)
        historical_tamper[
            "bound_terminal_2546_full_caller_update_action"
        ] = "runtime_promotion"
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([historical_tamper])

        proof_tamper = copy.deepcopy(renewal)
        proof_tamper["runtime_vm_verification"]["proof"][
            "raw_g1n_nonexpanding_for_all_7_register_assemblies"
        ] = False
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([proof_tamper])

        promotion = next(
            row
            for row in targets
            if row[field] == "runtime_promotion"
        )
        self.validate_rows([promotion])
        action_tamper = copy.deepcopy(promotion)
        action_tamper[field] = "verification_renewal"
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([action_tamper])


if __name__ == "__main__":
    unittest.main()
