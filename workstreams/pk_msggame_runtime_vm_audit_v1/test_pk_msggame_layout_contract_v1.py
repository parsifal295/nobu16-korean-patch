from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
CONTRACT_PATH = SCRIPT.parent / "ghidra_pk_msggame_layout_contract.v1.json"


class PkMsggameLayoutContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.content = CONTRACT_PATH.read_text(encoding="utf-8")
        cls.contract = json.loads(cls.content)

    def test_program_route_and_multiple_consumers_are_pinned(self) -> None:
        self.assertEqual(
            self.contract["schema"],
            "nobu16.kr.pk-msggame-ghidra-layout-contract.v1",
        )
        self.assertEqual(
            self.contract["program"]["unpacked_exe_sha256"],
            "BC885875A5E4288E5A1A424D99974F6F215777C03569C7EA707FDE63BDBC2B39",
        )
        self.assertEqual(
            self.contract["message_evaluation"]["evaluator"],
            "0x1409F7490",
        )
        self.assertGreaterEqual(len(self.contract["consumer_routes"]), 4)
        self.assertFalse(
            self.contract["adjudication"]["msggame_uses_one_widget"]
        )

    def test_dynamic_wrap_gate_is_not_msgev_912px(self) -> None:
        wrap = self.contract["line_wrap_contract"]
        self.assertEqual(wrap["widget_text_update"], "0x140F14A60")
        self.assertEqual(wrap["normalized_wrap_entry"], "0x1409F92E0")
        self.assertEqual(wrap["wrap_engine"], "0x1409F8B00")
        self.assertEqual(
            wrap["normalized_gate_formula"],
            "floor(widget_width * 18 / font_size)",
        )
        self.assertEqual(wrap["normalized_measurement_size"], 18)
        self.assertEqual(wrap["fullwidth_advance_normalized_px"], 18)
        self.assertFalse(
            self.contract["adjudication"][
                "one_absolute_pixel_gate_applies_to_all_msggame_rows"
            ]
        )
        self.assertFalse(
            self.contract["adjudication"]["pk_msgev_912px_rule_applies"]
        )

    def test_storage_gates_and_distribution_are_source_free(self) -> None:
        storage = self.contract["dialogue_queue_storage"]
        self.assertEqual(storage["speaker_capacity_utf16"], 150)
        self.assertEqual(storage["body_capacity_utf16"], 280)
        self.assertIsNone(
            re.search(
                r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff"
                r"\uac00-\ud7af]",
                self.content,
            )
        )
        self.assertFalse(self.contract["steam_write_performed"])
        policy = self.contract["distribution_policy"]
        self.assertFalse(policy["contains_commercial_dialogue_text"])
        self.assertFalse(policy["contains_translated_dialogue_text"])
        self.assertFalse(policy["contains_decompiled_function_body"])


if __name__ == "__main__":
    unittest.main()
