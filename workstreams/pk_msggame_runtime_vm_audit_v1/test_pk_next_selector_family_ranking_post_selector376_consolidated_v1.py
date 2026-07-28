#!/usr/bin/env python3
"""Focused tests for the immutable post-selector376 PK ranking."""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).with_name(
    "build_pk_next_selector_family_ranking_post_selector376_consolidated_v1.py"
)
SPEC = importlib.util.spec_from_file_location("post376_ranking_test", PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {PATH}")
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class PostSelector376RankingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.private, cls.public = BUILDER.build_outputs(
            ledger_path=BUILDER.DEFAULT_LEDGER,
            checkpoint_public_path=BUILDER.CHECKPOINT_PUBLIC,
        )
        BUILDER.assert_source_free(cls.public)

    def test_exact_universe_recommendation_and_zero_closure_guard(self) -> None:
        self.assertEqual(
            (
                self.public["scope"]["official_pending_rows"],
                self.public["scope"]["official_pending_root_count"],
                self.public["scope"]["reachable_0143_call_target_count"],
                self.public["scope"]["eligible_fixed_seven_way_family_count"],
                self.public["scope"][
                    "eligible_family_current_pending_union_rows"
                ],
            ),
            (6307, 4105, 150, 105, 927),
        )
        top = self.public["ranking"][0]
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
            ("0:364", 48, 21, 21, 38, 42, 4, 0),
        )
        self.assertEqual(
            self.private["classification_counts"],
            {
                "already_owned_selector_or_dispatch_closure": 22,
                "eligible_fixed_seven_way_selector": 105,
                "non_seven_way_call_target": 23,
            },
        )
        ranked = {
            row["selector_coordinate"] for row in self.public["ranking"]
        }
        for selector in BUILDER.OWNED_SELECTORS:
            self.assertIn(
                selector,
                self.public["exclusions"]["already_owned_selectors"],
            )
            self.assertNotIn(f"0:{selector}", ranked)
        self.assertNotIn("0:508", ranked)
        self.assertNotIn("0:376", ranked)

    def test_frozen_source_free_outputs(self) -> None:
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.DEFAULT_PRIVATE_OUTPUT),
            BUILDER.EXPECTED_PRIVATE_FILE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.DEFAULT_PUBLIC_OUTPUT),
            BUILDER.EXPECTED_PUBLIC_FILE_SHA256,
        )
        content = BUILDER.serialized_json(self.public).decode("ascii")
        self.assertIsNone(
            re.search(
                r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff"
                r"\uac00-\ud7a3]",
                content,
            )
        )
        self.assertFalse(self.public["privacy"]["steam_write_performed"])


if __name__ == "__main__":
    unittest.main()
