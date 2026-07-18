from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "build_pc_event_current_rebase_ledger_v1.py"
SPEC = importlib.util.spec_from_file_location("pc_event_current_rebase_ledger", SCRIPT)
assert SPEC and SPEC.loader
LEDGER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = LEDGER
SPEC.loader.exec_module(LEDGER)


class CurrentEventRebaseLedgerTests(unittest.TestCase):
    def test_validation_contract_has_expected_current_state(self) -> None:
        contract = LEDGER.read_contract()
        self.assertEqual(contract["schema"], LEDGER.SCHEMA)
        self.assertEqual(contract["profiles"]["base"]["resource"], LEDGER.BASE_RESOURCE)
        self.assertEqual(contract["profiles"]["pk"]["resource"], LEDGER.PK_RESOURCE)
        self.assertEqual(contract["profiles"]["font"]["resource"], LEDGER.FONT_RESOURCE)
        self.assertEqual(contract["current_pk_selection"]["new_runtime_ids"], [10837, 10840, 10905])

    def test_current_steam_verification_is_noop(self) -> None:
        report = LEDGER.verify()
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["candidate"]["effective_change_count"], 0)
        self.assertEqual(report["candidate"]["packed"], report["profiles"]["pk"]["packed"])
        self.assertEqual(report["candidate"]["raw"], report["profiles"]["pk"]["raw"])
        self.assertFalse(report["safety"]["steam_files_written"])
        self.assertFalse(report["safety"]["old_v2_target_overlay_reinjected"])

    def test_layout_and_reconciliation_contracts_are_complete(self) -> None:
        report = LEDGER.build_noop()
        self.assertEqual(report["selection"]["bounded_review_rows"], 4002)
        self.assertEqual(report["selection"]["unbounded_printf_preserved_id"], 16402)
        self.assertEqual(report["layout"]["max_lines"], 3)
        self.assertEqual(report["layout"]["max_reserved_width_px"], 912)
        self.assertEqual(report["stale_v2_reconciliation"]["nonexact_target_count"], 74)
        self.assertEqual(report["stale_v2_reconciliation"]["exact_current_target_noop_count"], 3700)
        self.assertEqual(report["stale_v2_reconciliation"]["historic_v1_reused_nonreview_count"], 11)
        self.assertEqual(report["stale_v2_reconciliation"]["current_bounded_max_lines"], 3)
        self.assertEqual(report["stale_v2_reconciliation"]["current_bounded_max_reserved_width_px"], 912)

    def test_builder_has_no_file_write_surface(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        for forbidden in ("write_bytes(", "write_text(", "os.replace(", "shutil.", "recompress_wrapper("):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
