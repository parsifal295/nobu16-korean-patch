#!/usr/bin/env python3
"""Regression checks for the Wave 102 Takeda/Hikotsuru private candidate."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_pc_event_takeda_hikotsuru_quality_wave102_v1.py")
SPEC = importlib.util.spec_from_file_location("pc_event_takeda_hikotsuru_wave102_tested", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TakedaHikotsuruWave102Tests(unittest.TestCase):
    def test_authored_scope(self) -> None:
        self.assertEqual(MODULE.APPLIED_IDS, tuple(sorted(MODULE.APPLIED_IDS)))
        self.assertEqual(len(MODULE.APPLIED_IDS), 20)
        self.assertEqual(MODULE.RUNTIME_RESERVATION_IDS, (3548,))

    def test_in_memory_candidate(self) -> None:
        event, audit, manifest, public_audit, validation = MODULE.build_bundle(require_output_profile=True)
        self.assertTrue(event)
        self.assertEqual(audit["schema"], "nobu16.kr.pc-event-takeda-hikotsuru-quality-wave102.v1.audit")
        self.assertEqual(audit["coverage"]["applied_row_ids"], list(MODULE.APPLIED_IDS))
        self.assertEqual(audit["coverage"]["outside_w101_changed_row_ids"], [])
        self.assertEqual(audit["coverage"]["runtime_reservation_ids"], [3548])
        self.assertTrue(audit["coverage"]["all_rows_static_patch_007_pass"])
        self.assertTrue(audit["coverage"]["all_rows_four_or_fewer_lines"])
        self.assertTrue(audit["coverage"]["all_rows_sentence_shortened_or_deleted_false"])
        self.assertEqual(manifest["applied_row_ids"], list(MODULE.APPLIED_IDS))
        self.assertEqual(public_audit["coverage"], audit["coverage"])
        self.assertEqual(validation["status"], "PASS")
        self.assertFalse(audit["policy"]["steam_game_resource_written"])
        self.assertFalse(audit["policy"]["git_operation_performed"])
        by_id = {row["entry_id"]: row for row in audit["rows"]}
        self.assertIn("내조의 공으로 뒷받침", by_id[3550]["proposed_ko"])
        self.assertIn("첫눈에 반했다고", by_id[3551]["proposed_ko"])
        self.assertIn("재치를 발휘해", by_id[3563]["proposed_ko"])
        self.assertIn("전국시대에는", by_id[3564]["proposed_ko"])
        runtime = by_id[3548]["layout"]["lines"][1]["runtime_reservations"]
        self.assertEqual(len(runtime), 1)
        self.assertFalse(runtime[0]["runtime_proven"])
        for row in audit["rows"]:
            self.assertFalse(row["korean_sentence_shortened_or_deleted"])
            self.assertFalse(row["japanese_source_line_breaks_reused"])
            self.assertLessEqual(row["layout"]["line_count"], 4)
            for line in row["layout"]["lines"]:
                self.assertLessEqual(line["effective_width_px"], 912)
                self.assertFalse(line["exceeds_912px"])

    def test_private_candidate_and_public_audit(self) -> None:
        result = MODULE.verify_private_candidate()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["applied_row_ids"], list(MODULE.APPLIED_IDS))
        self.assertEqual(result["outside_w101_changed_row_ids"], [])
        public_audit = json.loads(MODULE.PUBLIC_AUDIT.read_text(encoding="utf-8"))
        self.assertEqual(public_audit["coverage"]["applied_row_count"], 20)
        self.assertEqual(public_audit["coverage"]["runtime_reservation_ids"], [3548])


if __name__ == "__main__":
    unittest.main(verbosity=2)
