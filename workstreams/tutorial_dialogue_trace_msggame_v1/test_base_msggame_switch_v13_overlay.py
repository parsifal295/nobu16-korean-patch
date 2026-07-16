#!/usr/bin/env python3
"""Regression tests for the base shared-tutorial Switch-v1.3 transfer."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BUILDER_PATH = ROOT / "build_base_msggame_switch_v13_overlay.py"
SPEC = importlib.util.spec_from_file_location("base_msggame_switch_v13_tested", BUILDER_PATH)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class BaseMsgGameSwitchV13OverlayTests(unittest.TestCase):
    def test_pinned_inputs_have_exact_coordinate_alignment_and_tutorial_anchor(self) -> None:
        if not builder.DEFAULT_GAME_ROOT.is_dir() or not builder.DEFAULT_SWITCH_ZIP.is_file():
            self.skipTest("private Steam 1.1.7 or pinned Switch v1.3 input is unavailable")
        base = builder.load_base(builder.DEFAULT_GAME_ROOT)
        switch = builder.load_switch(builder.DEFAULT_SWITCH_ZIP)
        self.assertEqual(
            {"packed_size": len(base["packed"]), "packed_sha256": builder.sha256(base["packed"]), "raw_size": len(base["raw"]), "raw_sha256": builder.sha256(base["raw"])},
            {
                "packed_size": builder.BASE_PIN["packed_size"],
                "packed_sha256": builder.BASE_PIN["packed_sha256"],
                "raw_size": builder.BASE_PIN["raw_size"],
                "raw_sha256": builder.BASE_PIN["raw_sha256"],
            },
        )
        self.assertEqual(
            {"packed_size": len(switch["packed"]), "packed_sha256": builder.sha256(switch["packed"]), "raw_size": len(switch["raw"]), "raw_sha256": builder.sha256(switch["raw"])},
            {
                "packed_size": builder.SWITCH_TEXT_PIN["packed_size"],
                "packed_sha256": builder.SWITCH_TEXT_PIN["packed_sha256"],
                "raw_size": builder.SWITCH_TEXT_PIN["raw_size"],
                "raw_sha256": builder.SWITCH_TEXT_PIN["raw_sha256"],
            },
        )
        self.assertEqual(set(base["literals"]), set(switch["literals"]))
        self.assertEqual(len(base["literals"]), 24_262)
        eligible = builder.eligible_coordinates(base, switch)
        self.assertEqual(len(eligible), builder.EXPECTED_ELIGIBLE_COUNT)
        self.assertEqual(builder.coordinate_hash(eligible), builder.EXPECTED_COORDINATE_SHA256)
        self.assertIn(builder.TUTORIAL_ANCHOR, eligible)
        self.assertEqual(
            builder.text_hash(base["literals"][builder.TUTORIAL_ANCHOR].text),
            builder.TUTORIAL_ANCHOR_SOURCE_HASH,
        )
        self.assertEqual(
            builder.text_hash(switch["literals"][builder.TUTORIAL_ANCHOR].text),
            builder.TUTORIAL_ANCHOR_KO_HASH,
        )

    def test_public_overlay_is_source_free_and_has_the_full_coordinate_contract(self) -> None:
        overlay, blob = builder.strict_json(builder.OVERLAY_PATH)
        self.assertEqual(overlay["schema"], builder.SCHEMA)
        self.assertEqual(overlay["resource"], builder.RESOURCE)
        self.assertEqual(overlay["base_language"], "JP")
        self.assertEqual(overlay["entry_count"], builder.EXPECTED_ELIGIBLE_COUNT)
        self.assertEqual(overlay["entry_coordinate_sha256"], builder.EXPECTED_COORDINATE_SHA256)
        self.assertEqual(overlay["entry_contract_sha256"], builder.EXPECTED_ENTRY_CONTRACT_SHA256)
        self.assertEqual(
            overlay["distribution_policy"],
            {
                "contains_commercial_source_text": False,
                "contains_complete_game_resource": False,
            },
        )
        self.assertEqual(overlay["stock_jp"], builder.BASE_PIN)
        self.assertEqual(len(overlay["entries"]), builder.EXPECTED_ELIGIBLE_COUNT)
        self.assertEqual(blob, builder.pretty_bytes(overlay))

        # The public recipe may include Korean translations, but it must not
        # embed JP source prose from the commercial resource.
        serialized = json.dumps(overlay, ensure_ascii=False)
        self.assertIsNone(builder.CJK_RE.search(serialized))
        self.assertIsNone(builder.KANA_RE.search(serialized))

    def test_candidate_is_deterministic_and_changes_only_selected_literals(self) -> None:
        if not builder.DEFAULT_GAME_ROOT.is_dir() or not builder.DEFAULT_SWITCH_ZIP.is_file():
            self.skipTest("private Steam 1.1.7 or pinned Switch v1.3 input is unavailable")
        first, metrics = builder.build_blob()
        second, second_metrics = builder.build_blob()
        self.assertEqual(first, second)
        self.assertEqual(metrics, second_metrics)
        self.assertEqual(metrics["entry_count"], builder.EXPECTED_ELIGIBLE_COUNT)
        self.assertEqual(metrics["candidate"], builder.EXPECTED_CANDIDATE)
        self.assertTrue(metrics["non_selected_literals_preserved"])
        self.assertTrue(metrics["wrapper_prefix_preserved"])
        self.assertFalse(metrics["sc_binary_used"])

        base = builder.load_base(builder.DEFAULT_GAME_ROOT)
        parsed = builder.msggame.parse_packed_msggame(first)
        candidate_literals = builder.literal_map(parsed.archive)
        anchor = candidate_literals[builder.TUTORIAL_ANCHOR].text
        self.assertEqual(builder.text_hash(anchor), builder.TUTORIAL_ANCHOR_KO_HASH)
        self.assertEqual(anchor.count("\n"), 2)
        self.assertIsNone(builder.CJK_RE.search(anchor))
        self.assertIsNone(builder.KANA_RE.search(anchor))
        self.assertNotEqual(
            builder.text_hash(base["literals"][builder.TUTORIAL_ANCHOR].text),
            builder.text_hash(anchor),
        )

        validation, validation_blob = builder.strict_json(builder.VALIDATION_PATH)
        self.assertEqual(validation, builder.validation_model(metrics))
        self.assertEqual(validation_blob, builder.pretty_bytes(validation))

    def test_workstream_contains_no_game_binary(self) -> None:
        forbidden = {".bin", ".g1n", ".ttf", ".otf", ".zip", ".pixels"}
        offenders = [
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("*")
            if path.is_file() and path.suffix.lower() in forbidden
        ]
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
