"""Regression checks for the local-only Wave 8 dialogue candidate."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_pc_dialogue_quality_wave8_candidate_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("pc_dialogue_wave8_candidate_test", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load builder: {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Wave8CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load_builder()
        cls.steam_root = cls.builder.DEFAULT_STEAM_ROOT

    def test_regenerated_audit_is_pinned_and_pc_only(self):
        audit = self.builder.read_audit(self.steam_root)
        self.assertEqual(audit["scope"]["excluded_sources"], ["Switch Korean"])
        self.assertFalse(audit["scope"]["steam_game_resource_written"])
        self.assertEqual(audit["summary"]["msggame_record_count"], 48)
        self.assertEqual(audit["summary"]["pk_msgev_entry_count"], 5)
        self.assertEqual(audit["summary"]["total_changed_records_or_entries"], 53)

    def test_rebuilt_resources_match_the_full_pinned_profile(self):
        resources, audit = self.builder.construct_resources(self.steam_root)
        profile = dict(self.builder.INPUT_SHA256)
        profile.update({path: self.builder.sha256_bytes(value) for path, value in resources.items()})
        self.assertEqual(profile, self.builder.TARGET_SHA256)
        self.assertEqual(set(resources), set(self.builder.CHANGED_PATHS))
        self.assertEqual(audit["pk_msgev"]["output_packed_sha256"], profile[self.builder.EVENT_RESOURCE])

    def test_event_layout_and_static_dialogue_contracts_hold(self):
        audit = json.loads(self.builder.AUDIT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(len(audit["msggame_records"]), 48)
        for row in audit["msggame_records"]:
            self.assertEqual(row["output_opaque_hex"], "050505")
            self.assertEqual(row["manual_line_count"], row["literal_layout"]["after"]["line_count"])
            self.assertTrue(row["real_game_qa_required_before_release"])
        entries = audit["pk_msgev"]["records"]
        self.assertEqual(tuple(row["coordinate"] for row in entries), self.builder.EXPECTED_EVENT_IDS)
        for row in entries:
            layout = row["layout"]["after"]
            self.assertLessEqual(layout["line_count"], self.builder.MAX_EVENT_LINES)
            self.assertLessEqual(max(layout["reserved_line_width_px"]), self.builder.MAX_EVENT_LINE_PX)
            self.assertTrue(row["real_game_qa_required_before_release"])


if __name__ == "__main__":
    unittest.main()
