#!/usr/bin/env python3
"""Exact checks for the frozen post-selector238 PK ranking."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).with_name(
    "build_pk_next_selector_family_ranking_post_selector238_consolidated_v1.py"
)
SPEC = importlib.util.spec_from_file_location("post238_ranking_test", PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {PATH}")
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class PostSelector238RankingTests(unittest.TestCase):
    def test_known_closure_state_and_owned_exclusion(self) -> None:
        self.assertEqual(BUILDER.EXPECTED_PK_PENDING_ROWS, 6_151)
        self.assertEqual(BUILDER.COMPARABLE_ACTUAL_PROMOTIONS[238], 27)
        self.assertEqual(BUILDER.COMPARABLE_PENDING_UPPER_BOUNDS[238], 36)
        self.assertIn(238, BUILDER.OWNED_SELECTORS)

    def test_checkpoint_and_ranking_pins_are_frozen(self) -> None:
        self.assertFalse(BUILDER.bootstrap_missing())
        self.assertEqual(
            BUILDER.EXPECTED_CHECKPOINT_BUILDER_SHA256,
            "503A8500AFDB5A1041FA497A62634B3C30772DCE79628168C4208A898B45738B",
        )
        self.assertEqual(
            BUILDER.EXPECTED_LEDGER_SHA256,
            "AC10F7E71CFAD259ABBC08139BE0DB848CF5309578045532A48991F40E0035AB",
        )
        self.assertEqual(
            BUILDER.EXPECTED_CHECKPOINT_PUBLIC_SHA256,
            "0CAE7231474FBAE0BCE8E1E98D44225DCC5445EEEA435378E0D56BD1F83A5384",
        )
        self.assertEqual(
            BUILDER.EXPECTED_PK_CANDIDATE_SHA256,
            "9E5C60A451DB7CCA7B046AFD8CFF199CB3665E003CB0C751120478F693D20C24",
        )

    def test_unfrozen_output_pin_refuses_write(self) -> None:
        private_before = BUILDER.DEFAULT_PRIVATE_OUTPUT.read_bytes()
        public_before = BUILDER.DEFAULT_PUBLIC_OUTPUT.read_bytes()
        original = BUILDER.EXPECTED_PUBLIC_FILE_SHA256
        try:
            BUILDER.EXPECTED_PUBLIC_FILE_SHA256 = None
            with self.assertRaisesRegex(
                BUILDER.RankingError,
                "post-selector238 ranking bootstrap is not frozen",
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

    def test_exact_ranking_contract_comes_from_post238_ledger(self) -> None:
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
            (6_151, 4_032, 149, 95, 646, 31, 23),
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
            ("0:292", 33, 11, 11, 26, 31, 5, 0),
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
            (21, (0, 32)),
        )
        self.assertEqual(
            tuple(private["recommendation"]["terminal_coordinates"]),
            (
                "0:1615", "0:1616", "0:1617", "0:1618",
                "0:1619", "0:1620", "0:1621",
            ),
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
