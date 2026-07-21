from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_pc_dialogue_b17_spacing_grammar_v0140.py")
SPEC = importlib.util.spec_from_file_location("b17_spacing_grammar_test_target", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class B17SpacingGrammarTests(unittest.TestCase):
    def test_scope_and_safety_proofs(self) -> None:
        public, private, validation, _candidates = MODULE.build_model()
        self.assertEqual(24, validation["literal_count"])
        self.assertEqual(17, validation["record_count"])
        self.assertTrue(validation["proofs"]["opaque_bytecode_preserved"])
        self.assertFalse(validation["proofs"]["steam_game_resource_written"])
        self.assertEqual(24, len(private["rows"]))
        rows = {(row["resource"], row["record_id"], row["literal_id"]): row for row in private["rows"]}
        self.assertEqual("우리 ", rows[("MSG_PK/JP/msggame.bin", 115, 0)]["after"])
        self.assertEqual("를 사수하라!", rows[("MSG_PK/JP/msggame.bin", 981, 3)]["after"])
        self.assertEqual(2, len(public["resources"]))

    def test_public_artifact_is_source_free(self) -> None:
        public, _private, _validation, _candidates = MODULE.build_model()
        payload = MODULE.canonical_json(public, source_free=True)
        self.assertTrue(payload.isascii())
        self.assertNotIn(b"\xed\x95\x98", payload)


if __name__ == "__main__":
    unittest.main()
