from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("revalidate_pc_msgev_layout_current_v1.py")
SPEC = importlib.util.spec_from_file_location("msgev_current_revalidator", SCRIPT)
assert SPEC and SPEC.loader
REVALIDATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = REVALIDATOR
SPEC.loader.exec_module(REVALIDATOR)


class CurrentLayoutRevalidationTests(unittest.TestCase):
    def test_review_coordinate_contract_is_frozen(self) -> None:
        ids = REVALIDATOR.reviewed_ids()
        self.assertEqual(len(ids), 4003)
        self.assertEqual(
            REVALIDATOR.canonical_hash(ids),
            REVALIDATOR.EXPECTED_COORDINATE_SHA256,
        )


if __name__ == "__main__":
    unittest.main()
