#!/usr/bin/env python3
"""Tests for the immutable post-selector1126 PK family ranking."""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = (
    SCRIPT.parent
    / "build_pk_next_selector_family_ranking_post_selector1126_consolidated_v1.py"
)


def load_builder() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pk_next_selector_post_1126_test_builder_v1",
        BUILDER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = load_builder()


class PostSelector1126RankingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.private, cls.public = BUILDER.build_outputs(
            ledger_path=BUILDER.DEFAULT_LEDGER,
            checkpoint_public_path=BUILDER.CHECKPOINT_PUBLIC,
        )
        BUILDER.assert_source_free(cls.public)

    def test_frozen_input_lineage_and_candidate(self) -> None:
        self.assertEqual(
            self.public["inputs"]["official_integrated_ledger_sha256"],
            BUILDER.EXPECTED_LEDGER_SHA256,
        )
        self.assertEqual(
            self.public["inputs"]["official_public_checkpoint_sha256"],
            BUILDER.EXPECTED_CHECKPOINT_PUBLIC_SHA256,
        )
        self.assertEqual(
            self.public["inputs"]["pk_rebuilt_candidate_sha256"],
            BUILDER.EXPECTED_PK_CANDIDATE_SHA256,
        )

    def test_pending_universe_and_classification_are_exact(self) -> None:
        self.assertEqual(self.public["scope"]["official_pending_rows"], 6761)
        self.assertEqual(
            self.public["scope"]["official_pending_root_count"], 4288
        )
        self.assertEqual(
            self.private["classification_counts"],
            {
                "already_owned_selector_or_dispatch_closure": 9,
                "eligible_fixed_seven_way_selector": 122,
                "non_seven_way_call_target": 26,
            },
        )

    def test_selector142_is_current_structural_recommendation(self) -> None:
        top = self.public["ranking"][0]
        self.assertEqual(top["selector_coordinate"], "0:142")
        self.assertEqual(top["current_pending_rows"], 118)
        self.assertEqual(top["reachable_pending_root_count"], 56)
        self.assertEqual(top["direct_pending_call_site_count"], 56)
        self.assertEqual(top["candidate_call_site_count"], 109)
        self.assertEqual(top["source_call_site_count"], 115)
        self.assertEqual(top["source_only_call_site_count"], 6)
        self.assertEqual(top["candidate_only_call_site_count"], 0)
        self.assertTrue(
            top["dispatch_contract"]["source_candidate_identical"]
        )
        self.assertEqual(top["dispatch_contract"]["terminal_count"], 7)

    def test_owned_selector1126_is_excluded_and_estimate_refreshed(self) -> None:
        self.assertEqual(
            self.public["exclusions"]["already_owned_selectors"],
            [538, 568, 1096, 1174, 610, 550, 748, 1126],
        )
        self.assertNotIn(
            "0:1126",
            {
                row["selector_coordinate"]
                for row in self.public["ranking"]
            },
        )
        basis = self.public["recommendation"]["estimate_basis"]
        self.assertEqual(
            basis["completed_family_actual_promotions"]["1126"], 118
        )
        self.assertEqual(
            self.public["recommendation"]["estimated_actual_promotion_rows"],
            91,
        )
        self.assertEqual(
            self.public["recommendation"]["estimated_actual_promotion_range"],
            [74, 104],
        )

    def test_outputs_are_frozen_source_free_and_alias_independent(self) -> None:
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.DEFAULT_PRIVATE_OUTPUT),
            BUILDER.EXPECTED_PRIVATE_FILE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.DEFAULT_PUBLIC_OUTPUT),
            BUILDER.EXPECTED_PUBLIC_FILE_SHA256,
        )
        self.assertNotIn("progress.", str(BUILDER.DEFAULT_LEDGER))
        public_content = BUILDER.serialized_json(self.public).decode("utf-8")
        self.assertIsNone(
            re.search(
                r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
                r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
                public_content,
            )
        )
        self.assertNotIn('"translation"', public_content)
        self.assertFalse(self.public["privacy"]["steam_write_performed"])


if __name__ == "__main__":
    unittest.main()
