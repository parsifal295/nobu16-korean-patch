#!/usr/bin/env python3
"""Exact checks for the frozen post-selector730 PK ranking."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).with_name(
    "build_pk_next_selector_family_ranking_post_selector730_consolidated_v1.py"
)
SPEC = importlib.util.spec_from_file_location("post730_ranking_test", PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {PATH}")
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class PostSelector730RankingTests(unittest.TestCase):
    def test_known_closure_state_and_owned_exclusion(self) -> None:
        self.assertEqual(BUILDER.EXPECTED_PK_PENDING_ROWS, 6_178)
        self.assertEqual(BUILDER.COMPARABLE_ACTUAL_PROMOTIONS[730], 3)
        self.assertEqual(BUILDER.COMPARABLE_PENDING_UPPER_BOUNDS[730], 37)
        self.assertIn(730, BUILDER.OWNED_SELECTORS)

    def test_checkpoint_and_ranking_pins_are_frozen(self) -> None:
        self.assertFalse(BUILDER.bootstrap_missing())
        self.assertEqual(
            BUILDER.EXPECTED_CHECKPOINT_BUILDER_SHA256,
            "D65C1E87DC82D32D0E8765EDC5829926E4D0E838BAA4CAE76623B277E925B4FA",
        )
        self.assertEqual(
            BUILDER.EXPECTED_LEDGER_SHA256,
            "9F6BD587F6EC92CD00A2E2AF9FD9E07A8B6A71405272F0D79A515C3405617C5C",
        )
        self.assertEqual(
            BUILDER.EXPECTED_CHECKPOINT_PUBLIC_SHA256,
            "311DD27E8C260B7438EDF90FFB944EAEC25C3462C2C8E6BDA196BCF89DEDF362",
        )
        self.assertEqual(
            BUILDER.EXPECTED_PK_CANDIDATE_SHA256,
            "5D4CDF1CEB8C733B0E22C7AA6185D9FF6C5C4C500176E99A6AACB3D89F7E0140",
        )

    def test_unfrozen_output_pin_refuses_write(self) -> None:
        private_before = (
            BUILDER.DEFAULT_PRIVATE_OUTPUT.read_bytes()
            if BUILDER.DEFAULT_PRIVATE_OUTPUT.is_file()
            else None
        )
        public_before = (
            BUILDER.DEFAULT_PUBLIC_OUTPUT.read_bytes()
            if BUILDER.DEFAULT_PUBLIC_OUTPUT.is_file()
            else None
        )
        original = BUILDER.EXPECTED_PUBLIC_FILE_SHA256
        try:
            BUILDER.EXPECTED_PUBLIC_FILE_SHA256 = None
            with self.assertRaisesRegex(
                BUILDER.RankingError,
                "post-selector730 ranking bootstrap is not frozen",
            ):
                BUILDER.main([])
        finally:
            BUILDER.EXPECTED_PUBLIC_FILE_SHA256 = original
        self.assertEqual(
            BUILDER.DEFAULT_PRIVATE_OUTPUT.read_bytes(),
            private_before,
        )
        self.assertEqual(
            BUILDER.DEFAULT_PUBLIC_OUTPUT.read_bytes(),
            public_before,
        )

    def test_frozen_predecessor_and_checkpoint_builders(self) -> None:
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.PREDECESSOR_BUILDER),
            BUILDER.EXPECTED_PREDECESSOR_BUILDER_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.CHECKPOINT_BUILDER_PATH),
            BUILDER.EXPECTED_CHECKPOINT_BUILDER_SHA256,
        )

    def test_exact_ranking_contract_comes_from_post730_ledger(self) -> None:
        private, public = BUILDER.build_outputs(
            ledger_path=BUILDER.DEFAULT_LEDGER,
            checkpoint_public_path=BUILDER.CHECKPOINT_PUBLIC,
        )
        BUILDER.assert_source_free(public)
        top = public["ranking"][0]
        self.assertEqual(
            (
                public["scope"]["official_pending_rows"],
                public["scope"]["official_pending_root_count"],
                public["scope"]["reachable_0143_call_target_count"],
                public["scope"]["eligible_fixed_seven_way_family_count"],
                public["scope"]["eligible_family_current_pending_union_rows"],
            ),
            (6_178, 4_041, 150, 97, 677),
        )
        self.assertEqual(
            (
                top["selector_coordinate"],
                top["current_pending_rows"],
                top["reachable_pending_root_count"],
                top["direct_pending_call_site_count"],
                top["candidate_call_site_count"],
                top["source_call_site_count"],
                top["source_only_call_site_count"],
                top["candidate_only_call_site_count"],
            ),
            ("0:238", 36, 15, 15, 27, 28, 1, 0),
        )
        self.assertEqual(
            public["recommendation"]["selector_coordinate"],
            public["ranking"][0]["selector_coordinate"],
        )
        self.assertEqual(
            tuple(private["recommendation"]["terminal_coordinates"]),
            ("0:1552", "0:1553", "0:1554", "0:1555",
             "0:1556", "0:1557", "0:1558"),
        )
        ranked = {row["selector_coordinate"] for row in public["ranking"]}
        self.assertTrue(
            {f"0:{selector}" for selector in BUILDER.OWNED_SELECTORS}.isdisjoint(
                ranked
            )
        )
        self.assertFalse(public["privacy"]["steam_write_performed"])

    def test_output_hashes_check_and_determinism(self) -> None:
        self.assertEqual(
            (
                BUILDER.sha256_file(BUILDER.DEFAULT_PRIVATE_OUTPUT),
                BUILDER.sha256_file(BUILDER.DEFAULT_PUBLIC_OUTPUT),
            ),
            (
                BUILDER.EXPECTED_PRIVATE_FILE_SHA256,
                BUILDER.EXPECTED_PUBLIC_FILE_SHA256,
            ),
        )
        self.assertEqual(BUILDER.main(["--check"]), 0)
        first = BUILDER.build_outputs(
            ledger_path=BUILDER.DEFAULT_LEDGER,
            checkpoint_public_path=BUILDER.CHECKPOINT_PUBLIC,
        )
        second = BUILDER.build_outputs(
            ledger_path=BUILDER.DEFAULT_LEDGER,
            checkpoint_public_path=BUILDER.CHECKPOINT_PUBLIC,
        )
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
