#!/usr/bin/env python3
"""Targeted tests for frozen selector-550 chunk-0 review."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.parent / "build_pk_selector550_chunk0_review_v1.py"
spec = importlib.util.spec_from_file_location("selector550_chunk0_test", BUILDER_PATH)
assert spec is not None and spec.loader is not None
builder = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = builder
spec.loader.exec_module(builder)


class Selector550Chunk0ReviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.public = builder.build_public()
        cls.evidence = json.loads(builder.EVIDENCE.read_text(encoding="utf-8"))
        cls.decisions = [
            json.loads(line)
            for line in builder.DECISIONS.read_text(encoding="utf-8").splitlines()
            if line
        ]

    def test_partition(self) -> None:
        self.assertEqual(self.public["result"], builder.COUNTS)
        self.assertEqual(builder.COUNTS["accepted_sites"], 44)
        self.assertEqual(builder.COUNTS["blocked_sites"], 10)
        self.assertEqual(builder.COUNTS["promoted_pending_rows"], 46)
        self.assertEqual(builder.COUNTS["blocked_pending_rows"], 14)

    def test_all_seven_voice_branches_are_accounted_for(self) -> None:
        self.assertEqual(len(self.evidence["assembly_manifest"]), 54 * 7)
        self.assertTrue(
            all(len(row["assemblies"]) == 7 for row in self.evidence["site_reviews"])
        )

    def test_accepted_branches_pass_layout_and_grammar(self) -> None:
        accepted = [
            row for row in self.evidence["site_reviews"]
            if not row["decision"].startswith("blocked_")
        ]
        self.assertEqual(len(accepted), 44)
        self.assertTrue(
            all(
                branch["line_count_match"]
                and branch["current_relative_raw_g1n_nonexpanding"]
                and branch["grammar_and_spacing_proven"]
                for row in accepted
                for branch in row["assemblies"]
            )
        )

    def test_blocked_pending_rows_never_enter_decisions(self) -> None:
        blocked = set(self.evidence["blocked"]["pending_coordinates"])
        decided = {row["coordinate"] for row in self.decisions}
        self.assertEqual(len(blocked), 14)
        self.assertTrue(blocked.isdisjoint(decided))

    def test_actions_and_approvals(self) -> None:
        self.assertEqual(
            self.public["guards"]["action_counts"],
            builder.ACTIONS,
        )
        self.assertTrue(
            all(
                row["fresh_semantic_review"] == "approved"
                and row["historical_factuality_review"] == "approved"
                and row["speaker_tone_review"] == "approved"
                and row["runtime_review"] == "verified"
                for row in self.decisions
            )
        )

    def test_public_payload_is_source_free(self) -> None:
        text = json.dumps(self.public, ensure_ascii=False, sort_keys=True)
        self.assertIsNone(
            re.search(
                r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
                r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
                text,
            )
        )
        self.assertIsNone(re.search(r"\b\d+:\d+(?::\d+){0,2}\b", text))

    def test_live_steam_unchanged(self) -> None:
        self.assertEqual(builder.sha256_file(builder.STEAM), builder.EXPECTED["steam"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
