#!/usr/bin/env python3
"""Targeted tests for the selector568/1096/1174 consolidated layer."""

from __future__ import annotations

import copy
import importlib.util
import json
import re
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
OUTPUT_ROOT = REPO / "tmp" / WORKSTREAM.name
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
INTEGRATION_PATH = (
    WORKSTREAM / "build_runtime_vm_integrated_decisions_v1.py"
)
SHADOW_STEAM_ROOT = (
    OUTPUT_ROOT / "development_steam_root_pre_base_runtime_apply_13a404f"
)
PK_PRISTINE = (
    SHADOW_STEAM_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / "MSG_PK"
    / "JP"
    / "msggame.bin"
)
CJK_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af]")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_module("selector568_1096_1174_test_engine", ENGINE_PATH)
INTEGRATION = load_module(
    "selector568_1096_1174_test_integration",
    INTEGRATION_PATH,
)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


class Selector56810961174ConsolidatedIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.layer = INTEGRATION.load_selector568_1096_1174_consolidated()
        cls.bundle = cls.layer.build_outputs()
        cls.layer.validate_frozen(cls.bundle)
        cls.source_rows = read_jsonl(cls.layer.DEFAULT_DECISION_OUTPUT)
        cls.predecessors = (
            ENGINE.load_selector568_1096_1174_consolidated_predecessor_rows()
        )
        cls.prepared = ENGINE.prepare_artifacts(
            SHADOW_STEAM_ROOT,
            ENGINE.DEFAULT_BASE_PRISTINE,
            PK_PRISTINE,
        )

    def validate_rows(self, rows: list[dict[str, Any]]) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "decisions.private.v1.jsonl"
            path.write_text(
                ENGINE.jsonl(rows),
                encoding="utf-8",
                newline="\n",
            )
            ENGINE.validate_decisions(
                self.prepared,
                path,
                require_complete=False,
            )

    def test_frozen_layer_counts_and_digests(self) -> None:
        audit = self.bundle["audit"]
        promotion = self.bundle["promotion"]
        self.assertEqual(audit["result"]["decision_rows"], 1_173)
        self.assertEqual(audit["result"]["actual_promotion_rows"], 628)
        self.assertEqual(audit["result"]["verification_renewal_rows"], 545)
        self.assertEqual(audit["result"]["semantic_override_rows"], 440)
        self.assertEqual(audit["result"]["pending_rows_after"], 7_268)
        self.assertEqual(
            audit["result"]["final_candidate_sha256"],
            "07E65E6338D32C1FD13F17408F82A4133E55541C722874632948C7B36C909805",
        )
        self.assertEqual(
            promotion["evidence"]["decision_private_sha256"],
            "3260FCF12561EE116228907E1619FDB368DBDF9D0BA8565C03CD014440669B38",
        )
        self.assertEqual(
            promotion["evidence"]["evidence_private_sha256"],
            "3AA3CB05106CA921F22B96D26B8FA74A4F7C7D15A4D3AE122738F92E10A34C25",
        )

    def test_exact_decision_layer_passes_normal_validator(self) -> None:
        self.assertEqual(len(self.source_rows), 1_173)
        self.validate_rows(self.source_rows)
        field = (
            ENGINE.PK_SELECTOR568_1096_1174_CONSOLIDATED_UPDATE_ACTION_FIELD
        )
        self.assertEqual(
            Counter(str(row[field]) for row in self.source_rows),
            Counter(
                {
                    "runtime_promotion": 413,
                    "translation_override_and_runtime_promotion": 215,
                    "translation_override_and_verification_renewal": 225,
                    "verification_renewal": 320,
                }
            ),
        )

    def test_current81b4_transition_is_exact(self) -> None:
        promotions = []
        renewals = []
        for row in self.source_rows:
            key = ("pk_msggame", str(row["coordinate"]))
            predecessor = self.predecessors[key]
            evidence = row["runtime_vm_verification"]
            promoted = (
                predecessor["runtime_review"] == "pending"
                and row["runtime_review"] == "verified"
            )
            self.assertEqual(
                evidence["current81b4_rebase"]["actual_runtime_promotion"],
                promoted,
            )
            self.assertEqual(
                evidence["predecessor_binding"]["row_sha256"],
                ENGINE.canonical_ascii_sha256(predecessor),
            )
            if promoted:
                promotions.append(str(row["coordinate"]))
                self.assertEqual(row["scope_classification"], "retranslated")
                self.assertEqual(row["layout_review"], "runtime_verified")
            else:
                renewals.append(str(row["coordinate"]))
        self.assertEqual(len(promotions), 628)
        self.assertEqual(len(renewals), 545)
        self.assertEqual(
            self.layer.coordinate_digest(promotions),
            "68C1F1020153F158E416DDD8500563F3701AE14497791F06806B7F61B27C0FAF",
        )
        self.assertEqual(
            self.layer.coordinate_digest(renewals),
            "56BFC0325D9EF5C975FC0836374F1BA3B705FB4ED7BEEA75FC91850E43A88E62",
        )

    def test_validator_rejects_tampered_binding(self) -> None:
        field = (
            ENGINE.PK_SELECTOR568_1096_1174_CONSOLIDATED_UPDATE_ACTION_FIELD
        )
        samples = [
            next(row for row in self.source_rows if row[field] == action)
            for action in sorted(
                ENGINE.PK_SELECTOR568_1096_1174_CONSOLIDATED_RECOGNIZED_ACTIONS
            )
        ]
        self.validate_rows(samples)
        tampered = copy.deepcopy(samples[0])
        tampered["runtime_vm_verification"]["predecessor_binding"][
            "row_sha256"
        ] = "0" * 64
        with self.assertRaises(ENGINE.RetranslationError):
            self.validate_rows([tampered])

    def test_public_layer_reports_are_source_free(self) -> None:
        for path in (
            self.layer.DEFAULT_AUDIT_OUTPUT,
            self.layer.DEFAULT_PROMOTION_OUTPUT,
        ):
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(CJK_RE.search(text))
            self.assertNotIn('"translation"', text)
            self.assertNotIn('"source_text"', text)

    def test_cli_is_opt_in_and_requires_immutable_outputs(self) -> None:
        parser = INTEGRATION.build_parser()
        self.assertFalse(
            parser.parse_args(
                ["--check"]
            ).include_selector568_1096_1174_consolidated
        )
        parsed = parser.parse_args(
            [
                "--check",
                "--include-selector568-1096-1174-consolidated",
            ]
        )
        self.assertTrue(parsed.include_selector568_1096_1174_consolidated)
        self.assertEqual(
            INTEGRATION.SELECTOR568_1096_1174_CONSOLIDATED_PRIVATE_OUTPUT,
            OUTPUT_ROOT
            / (
                "runtime_vm_integrated.post_selector568_1096_1174_"
                "consolidated_checkpoint.private.v1.jsonl"
            ),
        )
        self.assertEqual(
            INTEGRATION.SELECTOR568_1096_1174_CONSOLIDATED_PUBLIC_OUTPUT,
            WORKSTREAM
            / (
                "runtime_vm_integration.post_selector568_1096_1174_"
                "consolidated_checkpoint.source_free.v1.json"
            ),
        )
        with self.assertRaises(INTEGRATION.IntegrationError):
            INTEGRATION.main(
                [
                    "--check",
                    "--include-selector568-1096-1174-consolidated",
                ]
            )

    def test_written_checkpoint_is_exact_when_present(self) -> None:
        private_path = (
            INTEGRATION.SELECTOR568_1096_1174_CONSOLIDATED_PRIVATE_OUTPUT
        )
        public_path = (
            INTEGRATION.SELECTOR568_1096_1174_CONSOLIDATED_PUBLIC_OUTPUT
        )
        if not private_path.is_file() or not public_path.is_file():
            return
        rows = read_jsonl(private_path)
        report = json.loads(public_path.read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 52_803)
        self.assertEqual(report["promotions"]["promoted_total"], 29_066)
        self.assertEqual(
            report["promotions"]["pk_msggame"]["promotion_count"],
            13_415,
        )
        self.assertEqual(report["result"]["runtime_review_pending"], 7_268)
        self.assertEqual(report["result"]["fully_candidate_eligible"], 45_535)
        layer = report["promotions"]["pk_msggame"][
            "selector568_1096_1174_consolidated"
        ]
        self.assertEqual(layer["updated_row_count"], 1_173)
        self.assertEqual(layer["promotion_count"], 628)
        self.assertTrue(
            report["validation"][
                "selector568_1096_1174_consolidated_layer_included"
            ]
        )


if __name__ == "__main__":
    unittest.main()
