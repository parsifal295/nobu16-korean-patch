#!/usr/bin/env python3
"""Contract tests for the post-post292-wave1 PK ranking scaffold."""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).with_name(
    "build_pk_next_selector_family_ranking_post_post292_wave1_v1.py"
)
SPEC = importlib.util.spec_from_file_location(
    "post_post292_wave1_ranking_test", PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {PATH}")
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class PostPost292Wave1RankingTests(unittest.TestCase):
    def test_exact_progress_transition_and_owned_selectors(self) -> None:
        self.assertEqual(
            BUILDER.EXPECTED_PROGRESS_TRANSITION,
            {
                "pending_before": 6_130,
                "pending_after": 6_084,
                "eligible_before": 46_673,
                "eligible_after": 46_719,
                "pk_promotions_before": 14_553,
                "pk_promotions_after": 14_599,
                "promoted_total_before": 30_204,
                "promoted_total_after": 30_250,
                "retranslated_before": 46_328,
                "retranslated_after": 46_374,
                "wave_promotions": 46,
            },
        )
        self.assertEqual(BUILDER.EXPECTED_PK_PENDING_ROWS, 6_084)
        self.assertTrue(
            set(BUILDER.WAVE_SELECTORS).issubset(BUILDER.OWNED_SELECTORS)
        )

    def test_exact_handoff_and_output_basenames(self) -> None:
        self.assertEqual(
            BUILDER.CHECKPOINT_BUILDER_PATH.name,
            "build_runtime_vm_"
            "post_selector292_wave1_consolidated_checkpoint_v1.py",
        )
        self.assertEqual(
            BUILDER.DEFAULT_LEDGER.name,
            "runtime_vm_integrated."
            "post_selector292_wave1_consolidated_checkpoint.private.v1.jsonl",
        )
        self.assertEqual(
            BUILDER.CHECKPOINT_PUBLIC.name,
            "runtime_vm_integration."
            "post_selector292_wave1_consolidated_checkpoint.source_free.v1.json",
        )
        self.assertEqual(
            BUILDER.PROGRESS_BUILDER_PATH.name,
            "build_progress_"
            "post_selector292_wave1_consolidated_delta_v1.py",
        )
        self.assertEqual(
            BUILDER.PROGRESS_PUBLIC_PATH.name,
            "progress.post_selector292_wave1_consolidated.source_free.v1.json",
        )
        self.assertEqual(
            BUILDER.DEFAULT_PRIVATE_OUTPUT.name,
            "pk_next_selector_family_ranking."
            "post_post292_wave1.private.v1.json",
        )
        self.assertEqual(
            BUILDER.DEFAULT_PUBLIC_OUTPUT.name,
            "pk_next_selector_family_ranking."
            "post_post292_wave1.source_free.v1.json",
        )

    def test_frozen_pins_have_fixed_shape(self) -> None:
        digest = re.compile(r"^[0-9A-F]{64}$")
        self.assertEqual(
            set(BUILDER.EXPECTED_INPUT_SHA256),
            set(BUILDER.input_paths()),
        )
        for value in BUILDER.EXPECTED_INPUT_SHA256.values():
            self.assertIsNotNone(value)
            self.assertTrue(digest.fullmatch(value))
        self.assertFalse(BUILDER.unresolved_pins())
        for name in (
            "EXPECTED_PK_CANDIDATE_SHA256",
            "EXPECTED_PK_PENDING_ROOT_SHA256",
            "EXPECTED_ELIGIBLE_UNION_SHA256",
            "EXPECTED_TOP_SIX_OVERLAP_SHA256",
            "EXPECTED_PRIVATE_FILE_SHA256",
            "EXPECTED_PUBLIC_FILE_SHA256",
        ):
            self.assertTrue(digest.fullmatch(getattr(BUILDER, name)), name)
        self.assertEqual(BUILDER.EXPECTED_RECOMMENDED_SELECTOR, "0:1048")

    def test_pairwise_overlap_dimensions_are_exact(self) -> None:
        left = {
            "candidate_call_sites": ["1:1:1:0", "1:2:1:0"],
            "current_pending_coordinates": ["1:1:0", "1:2:0"],
            "reachable_pending_roots": ["1:1", "1:2"],
            "source_call_sites": [
                "1:1:1:0", "1:2:1:0", "1:3:1:0"
            ],
            "jump_closure": {
                "terminal_coordinates": ["0:10", "0:11"]
            },
        }
        right = {
            "candidate_call_sites": ["1:2:1:0", "2:1:1:0"],
            "current_pending_coordinates": ["1:2:0", "2:1:0"],
            "reachable_pending_roots": ["1:2", "2:1"],
            "source_call_sites": [
                "1:2:1:0", "1:3:1:0", "2:1:1:0"
            ],
            "jump_closure": {
                "terminal_coordinates": ["0:11", "0:12"]
            },
        }
        overlaps = BUILDER.overlap_values(left, right)
        self.assertEqual(
            {name: len(values) for name, values in overlaps.items()},
            {
                "candidate_call_sites": 1,
                "pending_coordinates": 1,
                "reachable_pending_roots": 1,
                "source_only_call_sites": 1,
                "terminal_coordinates": 1,
            },
        )

    def test_pin_loss_fails_before_writing(self) -> None:
        original = BUILDER.EXPECTED_PUBLIC_FILE_SHA256
        BUILDER.EXPECTED_PUBLIC_FILE_SHA256 = None
        try:
            with self.assertRaisesRegex(
                BUILDER.PostWaveRankingError,
                "ranking pins unresolved",
            ):
                BUILDER.build_outputs()
        finally:
            BUILDER.EXPECTED_PUBLIC_FILE_SHA256 = original

    def test_frozen_build_when_handoffs_have_landed(self) -> None:
        if BUILDER.unresolved_pins():
            self.skipTest("ranking scaffold awaits wave closure/progress pins")
        private, public, _observed = BUILDER.build_outputs()
        BUILDER.assert_source_free(public)
        self.assertEqual(
            private["top_six_pairwise_overlap"]["pair_count"], 15
        )
        self.assertEqual(
            public["top_six_pairwise_overlap"]["pair_count"], 15
        )
        ranked = {row["selector_coordinate"] for row in public["ranking"]}
        self.assertTrue(
            {
                f"0:{selector}" for selector in BUILDER.OWNED_SELECTORS
            }.isdisjoint(ranked)
        )
        self.assertFalse(public["privacy"]["shared_integration_mutated"])
        self.assertFalse(public["privacy"]["steam_write_performed"])


if __name__ == "__main__":
    unittest.main()
