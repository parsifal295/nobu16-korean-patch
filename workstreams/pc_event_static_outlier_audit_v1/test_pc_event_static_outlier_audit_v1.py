#!/usr/bin/env python3
"""Regression tests for the PK static-width outlier UI-path audit."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BUILDER = WORKSTREAM / "build_pc_event_static_outlier_audit_v1.py"
REPORT = WORKSTREAM / "public" / "pc_event_static_outlier_audit.v1.json"


class StaticOutlierAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run([sys.executable, str(BUILDER), "build"], cwd=REPO, check=True)
        subprocess.run([sys.executable, str(BUILDER), "verify"], cwd=REPO, check=True)
        cls.document = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_scope_and_non_mutating_status(self) -> None:
        self.assertTrue(self.document["candidate_only"])
        self.assertEqual(self.document["mutation_scope"], "read_only_audit_public_json_only")
        self.assertEqual(self.document["scope"]["target_ids"], [17862, 17863, 17864])
        self.assertEqual(self.document["conclusion"]["approved_manual_line_break_count"], 0)
        self.assertEqual(self.document["conclusion"]["status"], "renderer_path_hold")

    def test_static007_measurements_are_complete(self) -> None:
        expected = {
            17862: (1896, 1185, 33, 13),
            17863: (1464, 915, 27, 7),
            17864: (1512, 945, 28, 7),
        }
        self.assertEqual(len(self.document["entries"]), 3)
        for entry in self.document["entries"]:
            line = entry["static_patch_007_measurement"]["lines"][0]
            actual = (
                line["raw_g1n_width_px"],
                line["effective_width_px"],
                line["full_width_character_count"],
                line["half_width_character_count"],
            )
            self.assertEqual(actual, expected[entry["entry_id"]])
            self.assertEqual(entry["static_patch_007_measurement"]["line_count"], 1)
            self.assertTrue(entry["static_patch_007_measurement"]["over_912px"])
            self.assertEqual(entry["decision"], "retain_one_line_no_candidate_mutation")
            self.assertFalse(entry["widget_judgement"]["is_static_patch_007_dialogue_box_proven"])
            self.assertEqual(entry["direct_pc_witnesses"]["line_break_character_count"], {"jp": 0, "en": 0, "sc": 0, "tc": 0})

    def test_neighbor_and_base_evidence_remain_pinned(self) -> None:
        neighbors = {entry["entry_id"]: entry["display_string"] for entry in self.document["ui_neighbor_evidence"]}
        self.assertEqual(neighbors[17817], "아니다")
        self.assertEqual(neighbors[17879], "※추가로 다음 조건을 만족하는 경우, 결과에 변동이 생깁니다※")
        for entry in self.document["entries"]:
            self.assertTrue(entry["base_duplicate_evidence"]["same_as_pk_direct_jp"])
            self.assertTrue(entry["no_shortening_or_source_lf_import"])


if __name__ == "__main__":
    unittest.main()
