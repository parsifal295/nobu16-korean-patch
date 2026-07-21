from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_pc_event_w102_context_reflow_wave1_v0140.py")
SPEC = importlib.util.spec_from_file_location("w102_context_reflow_test_target", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class W102ContextReflowTests(unittest.TestCase):
    def test_scope_and_layout_contract(self) -> None:
        public, private, validation, _candidate = MODULE.build_model()
        self.assertEqual(20, validation["entry_count"])
        self.assertTrue(validation["proofs"]["four_line_912px_layout_passed"])
        self.assertFalse(validation["proofs"]["steam_game_resource_written"])
        self.assertEqual(20, len(private["rows"]))
        by_id = {row["entry_id"]: row for row in private["rows"]}
        self.assertEqual(4, by_id[5785]["line_count"])
        dynamic_line = by_id[5785]["lines"][0]
        self.assertEqual("오다 노부나가가 마쓰다이라 모토야스의 군과 함께", dynamic_line["display_string"])
        self.assertEqual(
            [{
                "token": "[b1871]",
                "display_string": "마쓰다이라 모토야스",
                "reserved_raw_g1n_width_px": 456,
                "reserved_effective_width_px": 285,
            }],
            dynamic_line["runtime_name_reservations"],
        )
        self.assertTrue(all(not line["is_over_912px"] for row in private["rows"] for line in row["lines"]))
        self.assertEqual(20, len(public["resource"]["operations"]))

    def test_public_artifact_is_source_free(self) -> None:
        public, _private, _validation, _candidate = MODULE.build_model()
        payload = MODULE.canonical_json(public, source_free=True)
        self.assertTrue(payload.isascii())
        self.assertNotIn(b"\xec\x95\x84", payload)


if __name__ == "__main__":
    unittest.main()
