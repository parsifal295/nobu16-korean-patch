#!/usr/bin/env python3
"""Targeted tests for the single-union selector-610 closure."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name(
    "build_pk_selector610_consolidated_closure_v1.py"
)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = load_module(BUILDER_PATH, "selector610_consolidated_test_builder")


class Selector610ConsolidatedClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.outputs = BUILDER.build_outputs()
        cls.decisions = [
            json.loads(line)
            for line in cls.outputs[
                BUILDER.PRIVATE_DECISIONS_OUTPUT
            ].decode("utf-8").splitlines()
            if line
        ]
        cls.evidence = json.loads(
            cls.outputs[BUILDER.PRIVATE_EVIDENCE_OUTPUT].decode("utf-8")
        )
        cls.coverage = json.loads(
            cls.outputs[BUILDER.PUBLIC_COVERAGE_OUTPUT].decode("utf-8")
        )
        cls.promotion = json.loads(
            cls.outputs[BUILDER.PUBLIC_PROMOTION_OUTPUT].decode("utf-8")
        )
        cls.official = {
            (row["resource"], row["coordinate"]): row
            for row in BUILDER.load_jsonl(BUILDER.OFFICIAL_LEDGER_PATH)
        }

    def test_exact_union_counts_and_actions(self) -> None:
        result = self.promotion["result"]
        self.assertEqual(len(self.decisions), 314)
        self.assertEqual(result["promotions"], 167)
        self.assertEqual(result["renewals"], 147)
        self.assertEqual(result["overrides"], 193)
        self.assertEqual(result["action_counts"], BUILDER.EXPECTED_ACTION_COUNTS)
        self.assertEqual(result["pending_before"], 7_268)
        self.assertEqual(result["pending_after"], 7_101)

    def test_chunk_coordinate_and_root_sets_are_disjoint(self) -> None:
        coordinate_sets = []
        root_sets = []
        for path in BUILDER.CHUNK_DECISIONS:
            rows = BUILDER.load_jsonl(path)
            coordinates = {row["coordinate"] for row in rows}
            coordinate_sets.append(coordinates)
            root_sets.append(
                {BUILDER.coordinate_root(value) for value in coordinates}
            )
        for left in range(3):
            for right in range(left + 1, 3):
                self.assertFalse(coordinate_sets[left] & coordinate_sets[right])
                self.assertFalse(root_sets[left] & root_sets[right])

    def test_predecessor_supersession_is_explicit(self) -> None:
        exact = self.evidence["exact_maps"]
        self.assertEqual(len(exact["predecessor_overlaps"]), 4)
        self.assertEqual(len(exact["predecessor_supersessions"]), 3)
        self.assertTrue(
            set(exact["predecessor_supersessions"])
            <= set(exact["predecessor_overlaps"])
        )
        self.assertTrue(
            self.evidence["proof"]["predecessor_supersessions_explicit"]
        )

    def test_candidate_and_reverse_overlay_are_frozen(self) -> None:
        candidate = self.promotion["candidate"]
        self.assertEqual(
            candidate["reviewed_sha256"],
            BUILDER.EXPECTED_OUTPUT_SHA256["final_candidate"],
        )
        self.assertEqual(
            candidate["reverse_overlay_sha256"],
            BUILDER.EXPECTED_OFFICIAL_CANDIDATE_SHA256,
        )
        self.assertTrue(self.evidence["proof"]["record_control_gaps_preserved"])
        self.assertTrue(self.evidence["proof"]["reverse_overlay_exact"])

    def test_site_register_and_source_only_disposition(self) -> None:
        result = self.coverage["result"]
        self.assertEqual(result["reviewed_sites"], 230)
        self.assertEqual(
            result["candidate_call_site_sha256"],
            BUILDER.EXPECTED_CANDIDATE_SITE_SHA256,
        )
        self.assertEqual(result["source_only_sites"], 13)
        self.assertEqual(result["source_only_actions"], 0)
        self.assertEqual(
            result["source_only_site_sha256"],
            BUILDER.EXPECTED_SOURCE_ONLY_SHA256,
        )
        rows = self.evidence["exact_maps"]["source_only_sites"]
        self.assertEqual(len(rows), 13)
        self.assertTrue(all(row["action"] == "none" for row in rows))
        self.assertTrue(
            all(
                row["source_call_present"]
                and row["current_call_absent"]
                and row["candidate_call_absent"]
                for row in rows
            )
        )

    def test_private_rows_have_the_canonical_delta_contract(self) -> None:
        expected_keys = {
            BUILDER.UPDATE_ACTION_FIELD,
            "coordinate",
            "fresh_semantic_review",
            "historical_factuality_review",
            "jp_source_utf16le_sha256",
            "layout_review",
            "method",
            "official_predecessor_utf16le_sha256",
            "owner_chunk",
            "resource",
            "runtime_review",
            "schema",
            "speaker_tone_review",
            "translation",
            "translation_utf16le_sha256",
        }
        self.assertTrue(all(set(row) == expected_keys for row in self.decisions))
        self.assertTrue(
            all(
                row["schema"] == BUILDER.PRIVATE_DECISION_SCHEMA
                and row["resource"] == "pk_msggame"
                and row[BUILDER.UPDATE_ACTION_FIELD]
                in BUILDER.RECOGNIZED_ACTIONS
                for row in self.decisions
            )
        )

    def test_actions_match_fc157a_state_and_body(self) -> None:
        for row in self.decisions:
            predecessor = self.official[("pk_msggame", row["coordinate"])]
            promoted = predecessor["runtime_review"] == "pending"
            changed = row["translation"] != predecessor["translation"]
            if promoted:
                expected = (
                    "translation_override_and_runtime_promotion"
                    if changed else "runtime_promotion"
                )
            else:
                self.assertEqual(predecessor["runtime_review"], "verified")
                expected = (
                    "translation_override_and_verification_renewal"
                    if changed else "verification_renewal"
                )
            self.assertEqual(row[BUILDER.UPDATE_ACTION_FIELD], expected)

    def test_public_artifacts_are_source_free(self) -> None:
        for report in (self.coverage, self.promotion):
            content = json.dumps(report, ensure_ascii=False, sort_keys=True)
            self.assertIsNone(
                re.search(
                    r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
                    r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af"
                    r"\uf900-\ufaff]",
                    content,
                )
            )
            self.assertIsNone(
                re.search(r"\b\d+:\d+(?::\d+){0,2}\b", content)
            )
            self.assertFalse(report["steam_write_performed"])
            self.assertFalse(report["privacy"]["shared_integration_mutated"])

    def test_all_outputs_match_the_frozen_files(self) -> None:
        for path, content in self.outputs.items():
            self.assertTrue(path.is_file())
            self.assertEqual(path.read_bytes(), content)

    def test_source_free_guard_rejects_coordinates(self) -> None:
        with self.assertRaises(BUILDER.ClosureError):
            BUILDER.assert_source_free(
                {"coordinate": ":".join(("1", "1", "1"))}
            )


if __name__ == "__main__":
    unittest.main()
