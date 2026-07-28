#!/usr/bin/env python3
"""Deterministic tests for the next PK selector-family ranking."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
BUILDER_PATH = WORKSTREAM / "build_pk_next_selector_family_ranking_v1.py"


def load_builder() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pk_next_selector_family_ranking_test_builder_v1",
        BUILDER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = load_builder()


class NextSelectorFamilyRankingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.private, cls.public = BUILDER.build_outputs()

    def test_official_inputs_and_scope_are_frozen(self) -> None:
        self.assertEqual(
            self.public["inputs"]["official_integrated_ledger_sha256"],
            BUILDER.EXPECTED_LEDGER_SHA256,
        )
        self.assertEqual(
            self.public["inputs"]["pk_rebuilt_candidate_sha256"],
            BUILDER.EXPECTED_PK_CANDIDATE_SHA256,
        )
        self.assertEqual(
            self.public["scope"]["official_pending_rows"],
            BUILDER.EXPECTED_PK_PENDING_ROWS,
        )
        self.assertEqual(
            self.public["scope"]["reachable_0143_call_target_count"],
            BUILDER.EXPECTED_REACHABLE_CALL_TARGETS,
        )

    def test_owned_and_non_seven_way_targets_are_excluded(self) -> None:
        exclusions = self.public["exclusions"]
        self.assertEqual(
            exclusions["already_owned_selectors"],
            list(BUILDER.OWNED_SELECTORS),
        )
        self.assertEqual(
            exclusions["already_owned_reachable_call_targets"],
            BUILDER.EXPECTED_OWNED_CALL_TARGETS,
        )
        self.assertEqual(
            exclusions["non_seven_way_reachable_call_targets"],
            BUILDER.EXPECTED_NON_SEVEN_WAY_TARGETS,
        )
        selectors = {
            row["selector_coordinate"] for row in self.public["ranking"]
        }
        self.assertTrue(
            selectors.isdisjoint(
                {f"0:{selector}" for selector in BUILDER.OWNED_SELECTORS}
            )
        )

    def test_every_ranked_family_has_fixed_seven_way_shape(self) -> None:
        self.assertEqual(
            len(self.public["ranking"]),
            BUILDER.EXPECTED_ELIGIBLE_FAMILIES,
        )
        for row in self.public["ranking"]:
            contract = row["dispatch_contract"]
            self.assertTrue(contract["source_candidate_identical"])
            self.assertEqual(contract["node_count"], 13)
            self.assertEqual(contract["edge_count"], 13)
            self.assertEqual(contract["terminal_count"], 7)

    def test_ranking_is_deterministic_and_descending(self) -> None:
        keys = [
            (
                -row["disjoint_current_pending_rows"],
                -row["potential_current_pending_rows"],
                BUILDER.parse_root(row["selector_coordinate"]),
            )
            for row in self.public["ranking"]
        ]
        self.assertEqual(keys, sorted(keys))
        self.assertEqual(
            self.public["guards"]["eligible_ranking_canonical_sha256"],
            BUILDER.canonical_sha256(self.public["ranking"]),
        )

    def test_selector1174_is_the_next_highest_yield_family(self) -> None:
        recommendation = self.public["recommendation"]
        self.assertEqual(
            recommendation["selector_coordinate"],
            BUILDER.EXPECTED_RECOMMENDED_SELECTOR,
        )
        self.assertEqual(
            recommendation["exact_current_pending_upper_bound"],
            BUILDER.EXPECTED_RECOMMENDED_POTENTIAL,
        )
        self.assertEqual(
            recommendation[
                "exact_overlap_with_selector568_promotions"
            ],
            BUILDER.EXPECTED_RECOMMENDED_OVERLAP_568,
        )
        self.assertEqual(
            recommendation[
                "exact_overlap_with_selector1096_promotions"
            ],
            BUILDER.EXPECTED_RECOMMENDED_OVERLAP_1096,
        )
        self.assertEqual(
            recommendation[
                "exact_disjoint_current_pending_upper_bound"
            ],
            BUILDER.EXPECTED_RECOMMENDED_DISJOINT,
        )
        self.assertEqual(
            recommendation["estimated_actual_promotion_rows"],
            BUILDER.EXPECTED_POINT_ESTIMATE,
        )
        self.assertEqual(
            tuple(recommendation["estimated_actual_promotion_range"]),
            BUILDER.EXPECTED_ESTIMATE_RANGE,
        )

    def test_private_detail_contains_no_translation_field(self) -> None:
        def walk(value: Any) -> None:
            if isinstance(value, dict):
                self.assertNotIn("translation", value)
                self.assertNotIn("translations", value)
                for child in value.values():
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)

        walk(self.private)
        self.assertFalse(
            self.private["privacy"]["contains_dialogue_bodies"]
        )
        self.assertFalse(
            self.private["privacy"]["steam_write_performed"]
        )

    def test_public_report_is_source_free(self) -> None:
        BUILDER.assert_source_free(self.public)
        content = BUILDER.serialized_json(self.public).decode("ascii")
        self.assertIsNone(
            re.search(
                r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff"
                r"\uac00-\ud7a3]",
                content,
            )
        )
        self.assertNotIn('"translation"', content)

    def test_written_artifacts_match_rebuild(self) -> None:
        self.assertEqual(
            BUILDER.DEFAULT_PRIVATE_OUTPUT.read_bytes(),
            BUILDER.serialized_json(self.private),
        )
        self.assertEqual(
            BUILDER.DEFAULT_PUBLIC_OUTPUT.read_bytes(),
            BUILDER.serialized_json(self.public),
        )
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.DEFAULT_PRIVATE_OUTPUT),
            BUILDER.EXPECTED_PRIVATE_FILE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.DEFAULT_PUBLIC_OUTPUT),
            BUILDER.EXPECTED_PUBLIC_FILE_SHA256,
        )

    def test_public_file_parses_to_rebuilt_payload(self) -> None:
        parsed = json.loads(
            BUILDER.DEFAULT_PUBLIC_OUTPUT.read_text(encoding="ascii")
        )
        self.assertEqual(parsed, self.public)


if __name__ == "__main__":
    unittest.main()
