#!/usr/bin/env python3
"""Exact checks for the frozen post-selector226 PK ranking."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).with_name(
    "build_pk_next_selector_family_ranking_post_selector226_consolidated_v1.py"
)
SPEC = importlib.util.spec_from_file_location("post226_ranking_test", PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {PATH}")
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class PostSelector226RankingBootstrapTests(unittest.TestCase):
    def test_known_closure_state_and_owned_exclusion(self) -> None:
        self.assertEqual(BUILDER.EXPECTED_PK_PENDING_ROWS, 6246)
        self.assertEqual(
            BUILDER.EXPECTED_PK_CANDIDATE_SHA256,
            "FEE99844339C291F6950BEB2193AB5FDD8D25B6F6117AD52F81DCBF7F0CC9B66",
        )
        self.assertEqual(BUILDER.COMPARABLE_ACTUAL_PROMOTIONS[226], 37)
        self.assertEqual(BUILDER.COMPARABLE_PENDING_UPPER_BOUNDS[226], 46)
        self.assertIn(226, BUILDER.OWNED_SELECTORS)

    def test_checkpoint_and_ranking_pins_are_frozen(self) -> None:
        self.assertFalse(BUILDER.bootstrap_missing())
        self.assertEqual(
            BUILDER.EXPECTED_CHECKPOINT_BUILDER_SHA256,
            "59B68FA9A409E5963FED601CF2DCAF98B66E47A267941273CAC71126F22B0FCB",
        )
        self.assertEqual(
            BUILDER.EXPECTED_LEDGER_SHA256,
            "33B635E1409B290202A98719A9CD58F356551BB54703B7F287FC45250134623D",
        )
        self.assertEqual(
            BUILDER.EXPECTED_CHECKPOINT_PUBLIC_SHA256,
            "8526C4C53B87ED529D6C9EC44FF00FC9B77703EB6D4369DB83F4B916BAE37337",
        )
        self.assertEqual(BUILDER.EXPECTED_RECOMMENDED_SELECTOR, "0:268")

    def test_unfrozen_bootstrap_refuses_materialization(self) -> None:
        private_existed = BUILDER.DEFAULT_PRIVATE_OUTPUT.exists()
        public_existed = BUILDER.DEFAULT_PUBLIC_OUTPUT.exists()
        original = BUILDER.EXPECTED_CHECKPOINT_BUILDER_SHA256
        try:
            BUILDER.EXPECTED_CHECKPOINT_BUILDER_SHA256 = None
            with self.assertRaisesRegex(
                BUILDER.RankingError,
                "post-selector226 ranking bootstrap is not frozen",
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

    def test_exact_ranking_contract_after_pins_are_frozen(self) -> None:
        if BUILDER.bootstrap_missing():
            self.skipTest("post-selector226 ranking pins are not frozen")
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
                public["scope"][
                    "eligible_family_current_pending_union_rows"
                ],
            ),
            (
                6246,
                BUILDER.EXPECTED_PK_PENDING_ROOTS,
                BUILDER.EXPECTED_REACHABLE_CALL_TARGETS,
                BUILDER.EXPECTED_ELIGIBLE_FAMILIES,
                BUILDER.EXPECTED_ELIGIBLE_UNION_ROWS,
            ),
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
            (
                BUILDER.EXPECTED_RECOMMENDED_SELECTOR,
                BUILDER.EXPECTED_RECOMMENDED_PENDING_ROWS,
                BUILDER.EXPECTED_RECOMMENDED_PENDING_ROOTS,
                BUILDER.EXPECTED_RECOMMENDED_PENDING_SITES,
                BUILDER.EXPECTED_RECOMMENDED_CANDIDATE_SITES,
                BUILDER.EXPECTED_RECOMMENDED_SOURCE_SITES,
                BUILDER.EXPECTED_RECOMMENDED_SOURCE_ONLY_SITES,
                BUILDER.EXPECTED_RECOMMENDED_CANDIDATE_ONLY_SITES,
            ),
        )
        ranked = {row["selector_coordinate"] for row in public["ranking"]}
        self.assertTrue(
            {f"0:{selector}" for selector in BUILDER.OWNED_SELECTORS}.isdisjoint(
                ranked
            )
        )
        self.assertFalse(public["privacy"]["steam_write_performed"])
        self.assertIn("terminal_coordinates", private["recommendation"])


if __name__ == "__main__":
    unittest.main()
