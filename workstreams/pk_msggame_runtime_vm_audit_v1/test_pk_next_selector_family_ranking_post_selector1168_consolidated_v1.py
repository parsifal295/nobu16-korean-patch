#!/usr/bin/env python3
"""Bootstrap checks for the post-selector1168 PK ranking."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).with_name(
    "build_pk_next_selector_family_ranking_post_selector1168_consolidated_v1.py"
)
SPEC = importlib.util.spec_from_file_location("post1168_ranking_test", PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {PATH}")
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class PostSelector1168RankingBootstrapTests(unittest.TestCase):
    def test_known_closure_state_and_owned_exclusion(self) -> None:
        self.assertEqual(BUILDER.EXPECTED_PK_PENDING_ROWS, 6283)
        self.assertEqual(
            BUILDER.EXPECTED_PK_CANDIDATE_SHA256,
            "EF84A8B8A18C1F2F1F72D3A650C01DC7B058F32A3536C130809C4FCB31C837C7",
        )
        self.assertEqual(BUILDER.COMPARABLE_ACTUAL_PROMOTIONS[1168], 19)
        self.assertEqual(BUILDER.COMPARABLE_PENDING_UPPER_BOUNDS[1168], 48)
        self.assertIn(1168, BUILDER.OWNED_SELECTORS)

    def test_unfrozen_bootstrap_refuses_materialization(self) -> None:
        original_ledger = BUILDER.EXPECTED_LEDGER_SHA256
        original_selector = BUILDER.EXPECTED_RECOMMENDED_SELECTOR
        try:
            BUILDER.EXPECTED_LEDGER_SHA256 = None
            BUILDER.EXPECTED_RECOMMENDED_SELECTOR = None
            missing = BUILDER.bootstrap_missing()
            self.assertIn("EXPECTED_LEDGER_SHA256", missing)
            self.assertIn("EXPECTED_RECOMMENDED_SELECTOR", missing)
            with self.assertRaises(BUILDER.RankingError):
                BUILDER.build_outputs(
                    ledger_path=BUILDER.DEFAULT_LEDGER,
                    checkpoint_public_path=BUILDER.CHECKPOINT_PUBLIC,
                )
        finally:
            BUILDER.EXPECTED_LEDGER_SHA256 = original_ledger
            BUILDER.EXPECTED_RECOMMENDED_SELECTOR = original_selector

    def test_exact_ranking_contract_after_pins_are_frozen(self) -> None:
        if BUILDER.bootstrap_missing():
            self.skipTest("post-selector1168 ranking pins are not frozen")
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
                6283,
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
            {"0:508", "0:376", "0:364", "0:1168"}.isdisjoint(ranked)
        )
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.DEFAULT_PRIVATE_OUTPUT),
            BUILDER.EXPECTED_PRIVATE_FILE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.DEFAULT_PUBLIC_OUTPUT),
            BUILDER.EXPECTED_PUBLIC_FILE_SHA256,
        )
        self.assertFalse(public["privacy"]["steam_write_performed"])
        self.assertIn("terminal_coordinates", private["recommendation"])


if __name__ == "__main__":
    unittest.main()
