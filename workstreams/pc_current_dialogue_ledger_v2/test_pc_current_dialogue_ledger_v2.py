#!/usr/bin/env python3
"""Regression tests for the current, source-free PC dialogue ledger v2."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
BUILDER = WORKSTREAM / "build_current_pc_dialogue_ledger_v2.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("pc_current_dialogue_ledger_v2_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import builder: {BUILDER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_builder()


class CurrentPcDialogueLedgerV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows, cls.retired_rows, cls.hold_rows, cls.stale_rows, cls.summary = MODULE.build(
            MODULE.DEFAULT_STEAM_ROOT
        )
        MODULE.validate_rows(cls.rows, cls.retired_rows, cls.hold_rows, cls.stale_rows, cls.summary)

    def test_current_profile_and_coordinate_counts_are_pinned(self) -> None:
        self.assertEqual(len(self.rows), 53_743)
        self.assertEqual(
            self.summary["current_literal_resource_coordinate_counts"],
            {"base_msggame": 24_241, "pk_msggame": 29_502},
        )
        self.assertEqual(len(self.retired_rows), 43)
        self.assertEqual(
            self.summary["current_profile"]["sha256"]["MSG/JP/msggame.bin"],
            "4D147A4AD73466E882043D8A5E47F0D4DAF37473702A8CEABAEFFBF4E76F2EB8",
        )
        self.assertEqual(
            self.summary["current_profile"]["sha256"]["MSG_PK/JP/msggame.bin"],
            "BD789D1C5230159433BDB9F2FCBE4B0ABABF9D84FAD2FE1C16EED45B071CE860",
        )

    def test_wave7_to_wave14_record_and_literal_projection_is_current(self) -> None:
        repair = self.summary["repair_record_validation"]
        self.assertTrue(repair["all_target_record_hashes_match_current"])
        self.assertEqual(repair["record_count"], 138)
        self.assertEqual(
            repair["changed_literal_counts"],
            {
                "wave7": 24,
                "wave8": 108,
                "wave9": 59,
                "wave10": 24,
                "wave11": 8,
                "wave12": 2,
                "wave13": 22,
                "wave14": 19,
            },
        )
        relation = self.summary["prior_hash_relation"]
        self.assertEqual(relation["current_hash_matches_prior_count"], 52_192)
        self.assertEqual(relation["current_hash_differs_prior_count"], 1_551)
        self.assertEqual(relation["verified_wave7_to_wave14_repair_literal_count"], 266)
        self.assertEqual(relation["legacy_profile_lineage_different_literal_count"], 1_285)

    def test_current_and_stale_hold_evidence_are_separate(self) -> None:
        holds = self.summary["current_explicit_hold_evidence"]
        self.assertEqual(holds["current_hold_literal_count"], 597)
        self.assertEqual(
            holds["current_hold_group_literal_counts"],
            {
                "wave5_runtime_or_policy": 421,
                "wave7_runtime_visual_qa": 16,
                "wave8_historical_real_game_qa": 108,
                "wave9_historical_real_game_qa": 60,
            },
        )
        self.assertEqual(holds["stale_legacy_hold_record_count"], 31)
        self.assertEqual(len(self.hold_rows), 597)
        self.assertEqual(len(self.stale_rows), 31)
        self.assertTrue(
            all(row["reason"] == "legacy_record_preimage_no_longer_matches_current" for row in self.stale_rows)
        )

    def test_payloads_are_deterministic_and_source_free(self) -> None:
        payloads = {
            "ledger": MODULE.canonical_jsonl(self.rows),
            "retired": MODULE.canonical_jsonl(self.retired_rows),
            "holds": MODULE.canonical_jsonl(self.hold_rows),
            "stale": MODULE.canonical_jsonl(self.stale_rows),
            "summary": MODULE.canonical_json(self.summary),
        }
        for name, payload in payloads.items():
            MODULE.assert_source_free_bytes(name, payload)
            self.assertTrue(payload.decode("ascii"))
        ledger_first = json.loads(payloads["ledger"].splitlines()[0])
        self.assertNotIn("current_literals", ledger_first)
        self.assertNotIn("target_literals", ledger_first)
        self.assertFalse(self.summary["semantic_completion"])
        self.assertFalse(self.summary["switch_korean_translation_used"])
        self.assertFalse(self.summary["steam_installation_written"])


if __name__ == "__main__":
    unittest.main()
