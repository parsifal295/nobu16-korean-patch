#!/usr/bin/env python3
"""Focused tests for the immutable post-selector178 PK ranking."""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).with_name(
    "build_pk_next_selector_family_ranking_post_selector178_consolidated_v1.py"
)
SPEC = importlib.util.spec_from_file_location("post178_ranking_test", PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {PATH}")
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class PostSelector178RankingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.private, cls.public = BUILDER.build_outputs(
            ledger_path=BUILDER.DEFAULT_LEDGER,
            checkpoint_public_path=BUILDER.CHECKPOINT_PUBLIC,
        )
        BUILDER.assert_source_free(cls.public)

    def test_exact_universe_and_recommendation(self) -> None:
        self.assertEqual(
            (
                self.public["scope"]["official_pending_rows"],
                self.public["scope"]["official_pending_root_count"],
                self.public["scope"]["eligible_fixed_seven_way_family_count"],
                self.public["scope"][
                    "eligible_family_current_pending_union_rows"
                ],
            ),
            (6432, 4158, 116, 1181),
        )
        top = self.public["ranking"][0]
        self.assertEqual(
            (
                top["selector_coordinate"],
                top["current_pending_rows"],
                top["reachable_pending_root_count"],
                top["candidate_call_site_count"],
                top["source_call_site_count"],
                top["source_only_call_site_count"],
            ),
            ("0:1090", 80, 41, 96, 104, 8),
        )
        self.assertEqual(
            self.private["classification_counts"],
            {
                "already_owned_selector_or_dispatch_closure": 13,
                "eligible_fixed_seven_way_selector": 116,
                "non_seven_way_call_target": 26,
            },
        )

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
