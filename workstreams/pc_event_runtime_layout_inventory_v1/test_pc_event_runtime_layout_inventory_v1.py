from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_pc_event_runtime_layout_inventory_v1.py")
SPEC = importlib.util.spec_from_file_location("pc_event_runtime_layout_inventory_v1", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class RuntimeLedgerTest(unittest.TestCase):
    def test_runtime_ledger_is_full_and_read_only(self) -> None:
        ledger, validation, report = MODULE.build_bundle()

        self.assertIs(ledger["read_only"], True)
        self.assertIs(ledger["event_candidate_created"], False)
        self.assertIs(ledger["steam_game_resource_written"], False)
        self.assertEqual(validation["status"], "PASS")
        self.assertEqual(ledger["counts"]["runtime_row_count"], 1049)
        self.assertEqual(ledger["counts"]["numeric_name_token_row_count"], 859)
        self.assertEqual(ledger["counts"]["printf_runtime_token_row_count"], 190)
        self.assertEqual(
            ledger["counts"]["status_counts"],
            {"pass": 859, "unresolved_token_or_ui_hold": 190},
        )
        self.assertEqual(ledger["counts"]["width_or_line_overflow_candidate_count"], 0)
        self.assertIs(ledger["w100_to_w101_rebase"]["runtime_scope_identical"], True)
        self.assertEqual(ledger["w100_to_w101_rebase"]["runtime_changed_ids"], [3514, 3522, 3526])
        self.assertEqual(len(ledger["rows"]), 1049)
        self.assertTrue(all(row["manual_line_count"] <= 4 for row in ledger["rows"] if row["status"] == "pass"))
        self.assertTrue(
            all(
                all(line["effective_width_px"] <= 912 for line in row["lines"])
                for row in ledger["rows"]
                if row["status"] == "pass"
            )
        )
        self.assertIn("1,049행", report)

    def test_every_row_records_required_line_level_fields(self) -> None:
        ledger, _validation, _report = MODULE.build_bundle()
        required = {
            "display_string",
            "raw_g1n_width_px",
            "effective_width_px",
            "full_width_character_count",
            "half_width_character_count",
            "over_912px",
        }
        for row in ledger["rows"]:
            self.assertIn(row["status"], {"pass", "width_or_line_overflow_candidate", "unresolved_token_or_ui_hold"})
            self.assertEqual(row["manual_line_count"], len(row["lines"]))
            for line in row["lines"]:
                self.assertTrue(required.issubset(line))
                self.assertEqual(line["row_manual_line_count"], row["manual_line_count"])
                for reservation in line["runtime_name_reservations"]:
                    self.assertIs(reservation["runtime_proven"], False)
                    self.assertIs(reservation["prefix_semantics_assumed"], False)


if __name__ == "__main__":
    unittest.main()
