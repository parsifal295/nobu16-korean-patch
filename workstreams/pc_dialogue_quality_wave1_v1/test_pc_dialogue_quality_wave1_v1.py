from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_pc_dialogue_quality_wave1_v1.py")
SPEC = importlib.util.spec_from_file_location("wave1_builder", SCRIPT)
assert SPEC and SPEC.loader
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class DialogueQualityWave1Tests(unittest.TestCase):
    def test_declared_profile_is_exact(self) -> None:
        self.assertEqual(set(BUILDER.PROFILE_TARGETS), set(BUILDER.BASELINE_SHA256))
        self.assertEqual(set(BUILDER.PROFILE_TARGETS), set(BUILDER.TARGET_SHA256))
        self.assertEqual(BUILDER.expected_changed_paths(), {
            "MSG/JP/ev_strdata.bin",
            "MSG/JP/msggame.bin",
            "MSG/JP/strdata.bin",
            "MSG_PK/JP/msgbre.bin",
            "MSG_PK/JP/msgdata.bin",
            "MSG_PK/JP/msgev.bin",
            "MSG_PK/JP/msggame.bin",
            "MSG_PK/JP/msgire.bin",
        })

    def test_literal_coordinates_are_unique(self) -> None:
        keys = [(fix.relative, fix.block_id, fix.record_id, fix.literal_id) for fix in BUILDER.LITERAL_FIXES]
        self.assertEqual(len(keys), len(set(keys)))

    def test_source_and_target_are_not_equal(self) -> None:
        for fix in (*BUILDER.COMMON_FIXES, *BUILDER.STRDATA_FIXES, *BUILDER.LITERAL_FIXES):
            self.assertNotEqual(fix.before, fix.after)


if __name__ == "__main__":
    unittest.main()
