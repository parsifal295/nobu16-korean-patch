from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("render_prep", ROOT / "build_steam_jp_pk_menu_labels_render_prep_v1.py")
assert SPEC and SPEC.loader
prep = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prep)


class RenderPrepTests(unittest.TestCase):
    def test_plan_is_source_free_and_hard_disabled(self) -> None:
        plan = prep.validate_plan(prep.DEFAULT_PLAN)
        self.assertEqual(plan["slot_count"], 43)
        self.assertEqual(plan["wording_review_required_slots"], [1, 2, 19])
        self.assertFalse(plan["scope"]["candidate_generation_enabled"])
        self.assertEqual(plan["scope"]["excluded_outer_entries"], [3, 24])
        self.assertTrue(prep.DEFAULT_PLAN.read_bytes().isascii())
        self.assertTrue(all("proposed_ko" not in entry for entry in plan["slots"]))
        self.assertTrue(all(prep.valid_sha256(entry["proposed_ko_utf16le_sha256"]) for entry in plan["slots"]))

    def test_all_slots_are_blocked_pending_runtime_evidence(self) -> None:
        plan = prep.validate_plan(prep.DEFAULT_PLAN)
        self.assertTrue(all(not entry["candidate_eligible"] for entry in plan["slots"]))
        self.assertTrue(all(entry["runtime_trace_status"] == "missing" for entry in plan["slots"]))
        self.assertTrue(all(entry["text_rectangle_qa_status"] == "missing" for entry in plan["slots"]))

    def test_tmp_gate_rejects_game_install(self) -> None:
        with self.assertRaises(prep.RenderPrepError):
            prep.require_tmp(Path(r"F:\SteamLibrary\steamapps\common\NOBU16"))


if __name__ == "__main__":
    unittest.main()
