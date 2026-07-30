#!/usr/bin/env python3
"""Exact checks for the frozen post-selector1078 PK ranking."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).with_name(
    "build_pk_next_selector_family_ranking_post_selector1078_consolidated_v1.py"
)
SPEC = importlib.util.spec_from_file_location("post1078_ranking_test", PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {PATH}")
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class PostSelector1078RankingTests(unittest.TestCase):
    def test_known_closure_state_and_owned_exclusion(self) -> None:
        self.assertEqual(BUILDER.EXPECTED_PK_PENDING_ROWS, 6215)
        self.assertEqual(
            BUILDER.EXPECTED_PK_CANDIDATE_SHA256,
            "1A931E023A5248626AE90094772657D91B4270D0F530B48ABC613FDA84BB508D",
        )
        self.assertEqual(BUILDER.COMPARABLE_ACTUAL_PROMOTIONS[1078], 17)
        self.assertEqual(BUILDER.COMPARABLE_PENDING_UPPER_BOUNDS[1078], 43)
        self.assertIn(1078, BUILDER.OWNED_SELECTORS)

    def test_checkpoint_and_ranking_pins_are_frozen(self) -> None:
        self.assertFalse(BUILDER.bootstrap_missing())
        self.assertEqual(
            BUILDER.EXPECTED_CHECKPOINT_BUILDER_SHA256,
            "D3555F7C9CBE95B188C478D8D1AAEFD0F50EEB8C68A28F7D69819F77323D6D38",
        )
        self.assertEqual(
            BUILDER.EXPECTED_LEDGER_SHA256,
            "71ADE7F33FC40A817E60F429DE0A0B329E05BF37BD1E03E1671A019783E800F6",
        )
        self.assertEqual(
            BUILDER.EXPECTED_CHECKPOINT_PUBLIC_SHA256,
            "395C8B600B1AED634FA199602CBBB9F2DCA5691D9E5850688E2107966A8A77E3",
        )
        self.assertEqual(BUILDER.EXPECTED_RECOMMENDED_SELECTOR, "0:466")

    def test_unfrozen_bootstrap_refuses_materialization(self) -> None:
        private_existed = BUILDER.DEFAULT_PRIVATE_OUTPUT.exists()
        public_existed = BUILDER.DEFAULT_PUBLIC_OUTPUT.exists()
        original = BUILDER.EXPECTED_CHECKPOINT_BUILDER_SHA256
        try:
            BUILDER.EXPECTED_CHECKPOINT_BUILDER_SHA256 = None
            with self.assertRaisesRegex(
                BUILDER.RankingError,
                "post-selector1078 ranking bootstrap is not frozen",
            ):
                BUILDER.build_outputs(
                    ledger_path=BUILDER.DEFAULT_LEDGER,
                    checkpoint_public_path=BUILDER.CHECKPOINT_PUBLIC,
                )
        finally:
            BUILDER.EXPECTED_CHECKPOINT_BUILDER_SHA256 = original
        self.assertEqual(
            BUILDER.DEFAULT_PRIVATE_OUTPUT.exists(), private_existed
        )
        self.assertEqual(
            BUILDER.DEFAULT_PUBLIC_OUTPUT.exists(), public_existed
        )

    def test_exact_ranking_contract(self) -> None:
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
            (6215, 4058, 150, 100, 759),
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
            ("0:466", 41, 20, 20, 79, 94, 15, 0),
        )
        ranked = {row["selector_coordinate"] for row in public["ranking"]}
        self.assertTrue(
            {f"0:{selector}" for selector in BUILDER.OWNED_SELECTORS}.isdisjoint(
                ranked
            )
        )
        self.assertFalse(public["privacy"]["steam_write_performed"])
        self.assertEqual(
            tuple(private["recommendation"]["terminal_coordinates"]),
            BUILDER.EXPECTED_RECOMMENDED_TERMINALS,
        )

    def test_output_hashes_and_determinism(self) -> None:
        before = (
            BUILDER.sha256_file(BUILDER.DEFAULT_PRIVATE_OUTPUT),
            BUILDER.sha256_file(BUILDER.DEFAULT_PUBLIC_OUTPUT),
        )
        self.assertEqual(
            before,
            (
                BUILDER.EXPECTED_PRIVATE_FILE_SHA256,
                BUILDER.EXPECTED_PUBLIC_FILE_SHA256,
            ),
        )
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
