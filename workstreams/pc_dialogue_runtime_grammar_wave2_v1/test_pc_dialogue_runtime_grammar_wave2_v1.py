from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_pc_dialogue_runtime_grammar_wave2_v1.py")
SPEC = importlib.util.spec_from_file_location("runtime_grammar_wave2", SCRIPT)
assert SPEC and SPEC.loader
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class RuntimeGrammarWave2Tests(unittest.TestCase):
    def test_plan_contract_is_exact(self) -> None:
        self.assertEqual(BUILDER.plan_coordinates(), set(BUILDER.CONTRACTS))
        self.assertEqual(len(BUILDER.LITERAL_PLANS), 23)
        self.assertEqual(len(BUILDER.STATIC_PLANS), 10)

    def test_profile_and_scope_are_exact(self) -> None:
        self.assertEqual(set(BUILDER.PROFILE_TARGETS), set(BUILDER.BASELINE_SHA256))
        self.assertEqual(set(BUILDER.PROFILE_TARGETS), set(BUILDER.TARGET_SHA256))
        self.assertEqual(BUILDER.CHANGED_PATHS, {"MSG/JP/msggame.bin", "MSG_PK/JP/msggame.bin"})

    def test_each_contract_has_unique_pinned_commands(self) -> None:
        for item in BUILDER.CONTRACTS.values():
            for commands in (item.base_commands, item.pk_commands):
                self.assertEqual(len(commands), len(set(commands)))
                self.assertTrue(commands)
                self.assertTrue(all(value[:2] == b"\x01\x43" and len(value) == 6 for _, value in commands))


if __name__ == "__main__":
    unittest.main()
