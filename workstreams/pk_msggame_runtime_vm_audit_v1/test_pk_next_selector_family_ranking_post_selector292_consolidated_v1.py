#!/usr/bin/env python3
"""Exact checks for the frozen post-selector292 PK ranking."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).with_name(
    "build_pk_next_selector_family_ranking_post_selector292_consolidated_v1.py"
)
SPEC = importlib.util.spec_from_file_location("post292_ranking_test", PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {PATH}")
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class PostSelector292RankingTests(unittest.TestCase):
    def test_known_closure_state_and_owned_exclusion(self) -> None:
        self.assertEqual(BUILDER.EXPECTED_PK_PENDING_ROWS, 6_130)
        self.assertEqual(BUILDER.COMPARABLE_ACTUAL_PROMOTIONS[292], 21)
        self.assertEqual(BUILDER.COMPARABLE_PENDING_UPPER_BOUNDS[292], 33)
        self.assertIn(292, BUILDER.OWNED_SELECTORS)

    def test_checkpoint_and_ranking_pins_are_frozen(self) -> None:
        self.assertFalse(BUILDER.bootstrap_missing())
        self.assertEqual(
            BUILDER.EXPECTED_CHECKPOINT_BUILDER_SHA256,
            "CCF550E94624B4A8C0E8A343DAC700568F1FA91798948C25E63E96F3B18EF50E",
        )
        self.assertEqual(
            BUILDER.EXPECTED_LEDGER_SHA256,
            "90644EA8E6F2EF99CA2020993930E551536F00E9BF4DFD244ED46640123E8725",
        )
        self.assertEqual(
            BUILDER.EXPECTED_CHECKPOINT_PUBLIC_SHA256,
            "E76C849DFB6589B7C48B830D227C368ACA98B80F18FBBC2DD8CF146D455F9652",
        )
        self.assertEqual(
            BUILDER.EXPECTED_PK_CANDIDATE_SHA256,
            "723589D4CC42165F93FF60F0711E96DAB6E84737C75954FA36819F780CD57A2C",
        )

    def test_unfrozen_output_pin_refuses_write(self) -> None:
        private_before = BUILDER.DEFAULT_PRIVATE_OUTPUT.read_bytes()
        public_before = BUILDER.DEFAULT_PUBLIC_OUTPUT.read_bytes()
        original = BUILDER.EXPECTED_PUBLIC_FILE_SHA256
        try:
            BUILDER.EXPECTED_PUBLIC_FILE_SHA256 = None
            with self.assertRaisesRegex(
                BUILDER.RankingError,
                "post-selector292 ranking bootstrap is not frozen",
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

    def test_exact_ranking_contract_comes_from_post292_ledger(self) -> None:
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
                public["exclusions"][
                    "already_owned_reachable_call_targets"
                ],
                public["exclusions"][
                    "non_seven_way_reachable_call_targets"
                ],
            ),
            (6_130, 4_026, 148, 93, 623, 32, 23),
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
            ("0:286", 32, 13, 12, 57, 69, 12, 0),
        )
        self.assertEqual(
            public["recommendation"]["selector_coordinate"],
            public["ranking"][0]["selector_coordinate"],
        )
        self.assertEqual(
            (
                public["recommendation"]["estimated_actual_promotion_rows"],
                tuple(
                    public["recommendation"][
                        "estimated_actual_promotion_range"
                    ]
                ),
            ),
            (20, (0, 31)),
        )
        self.assertEqual(
            tuple(private["recommendation"]["terminal_coordinates"]),
            (
                "0:1608", "0:1609", "0:1610", "0:1611",
                "0:1612", "0:1613", "0:1614",
            ),
        )
        ranked = {row["selector_coordinate"] for row in public["ranking"]}
        self.assertTrue(
            {f"0:{selector}" for selector in BUILDER.OWNED_SELECTORS}.isdisjoint(
                ranked
            )
        )
        self.assertFalse(public["privacy"]["shared_integration_mutated"])
        self.assertFalse(public["privacy"]["steam_write_performed"])

    def test_top_six_ranking_metrics_are_exact(self) -> None:
        _private, public = BUILDER.build_outputs(
            ledger_path=BUILDER.DEFAULT_LEDGER,
            checkpoint_public_path=BUILDER.CHECKPOINT_PUBLIC,
        )
        metrics = [
            (
                row["selector_coordinate"],
                row["current_pending_rows"],
                row["reachable_pending_root_count"],
                row["direct_pending_call_site_count"],
                row["candidate_call_site_count"],
                row["source_call_site_count"],
                row["source_only_call_site_count"],
            )
            for row in public["ranking"][:6]
        ]
        self.assertEqual(
            metrics,
            [
                ("0:286", 32, 13, 12, 57, 69, 12),
                ("0:190", 31, 11, 11, 22, 25, 3),
                ("0:1048", 31, 13, 13, 21, 22, 1),
                ("0:736", 30, 11, 11, 17, 17, 0),
                ("0:82", 28, 17, 17, 58, 66, 8),
                ("0:214", 25, 9, 9, 21, 21, 0),
            ],
        )

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
