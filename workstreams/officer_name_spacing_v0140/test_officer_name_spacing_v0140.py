from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_officer_name_spacing_v0140.py")
SPEC = importlib.util.spec_from_file_location("officer_name_spacing_test_target", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class OfficerNameSpacingTests(unittest.TestCase):
    def test_full_name_evidence_derives_the_pinned_scope(self) -> None:
        public, private, validation, _candidates = MODULE.build_model()
        self.assertEqual(5, validation["candidate_count"])
        self.assertEqual(MODULE.EXPECTED_IDS_SHA256, validation["candidate_ids_sha256"])
        self.assertFalse(validation["proofs"]["steam_game_resource_written"])
        self.assertEqual(5, len(private["rows"]))
        by_id = {row["display_id"]: row for row in private["rows"]}
        self.assertEqual("하시바", by_id[941]["current_display"])
        self.assertEqual("하시바 ", by_id[941]["replacement"])
        self.assertGreaterEqual(len(by_id[941]["evidence"]), 4)
        self.assertEqual([939, 940, 941, 942, 943], sorted(by_id))
        self.assertEqual(5, len(public["resources"]["MSG_PK/JP/msgdata.bin"]["operations"]))
        self.assertTrue(validation["proofs"]["shared_or_ambiguous_component_evidence_excluded"])

    def test_public_artifact_contains_no_game_text(self) -> None:
        public, _private, _validation, _candidates = MODULE.build_model()
        payload = MODULE.canonical_json(public, source_free=True)
        self.assertTrue(payload.isascii())
        self.assertNotIn(b"\xed\x95\x98", payload)
        self.assertTrue(public["source_free"])
        self.assertFalse(public["scope"]["steam_game_resource_written"])


if __name__ == "__main__":
    unittest.main()
