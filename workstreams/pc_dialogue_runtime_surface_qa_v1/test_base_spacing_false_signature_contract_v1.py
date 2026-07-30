#!/usr/bin/env python3
"""Regressions for the source-free Base Kiwi false-signature contract."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "base_spacing_false_signature_contract_builder",
    HERE / "build_base_spacing_false_signature_contract_v1.py",
)
assert SPEC is not None and SPEC.loader is not None
BUILD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILD
SPEC.loader.exec_module(BUILD)
CONTRACT_PATH = (
    HERE / "base_spacing_false_signature_contract.source_free.v1.json"
)


class BaseSpacingFalseSignatureContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_contract_is_source_free_and_digest_pinned(self) -> None:
        self.assertEqual(self.contract["schema"], BUILD.SCHEMA)
        self.assertFalse(self.contract["private_text_included"])
        self.assertEqual(self.contract["entry_count"], 173)
        self.assertEqual(
            self.contract["entry_sha256"],
            "C31F816E6E47CD78B8404A2FBEBA9773D49677586C86ADE37D41DF9E9889B21F",
        )
        self.assertEqual(
            self.contract["category_summaries"],
            {
                "adverb_to_lexeme": {
                    "coordinate_count": 226,
                    "coordinate_sha256":
                        "C8123D72FEFC46F6153064315521E73E6C4E14D35D241BB9EBDC2D7A47CA83F4",
                    "finding_count": 701,
                    "signature_count": 31,
                },
                "etm_to_lexeme": {
                    "coordinate_count": 96,
                    "coordinate_sha256":
                        "D094E2121221425A97D41F8D58752F226CED101391D4442C83C789433C8BF4C7",
                    "finding_count": 224,
                    "signature_count": 29,
                },
                "nominal_to_bound_noun": {
                    "coordinate_count": 220,
                    "coordinate_sha256":
                        "D87E616E3AA1AB43FE02D4970BB60F67DD6D590B09B10FFD6A3EB9380C39717A",
                    "finding_count": 406,
                    "signature_count": 32,
                },
                "nominal_to_predicate": {
                    "coordinate_count": 343,
                    "coordinate_sha256":
                        "0C3BE9489CFA002EF5A702F60D0CA8B83D230F258E76D44BD7DDB185599BBB6F",
                    "finding_count": 462,
                    "signature_count": 59,
                },
                "particle_to_lexeme": {
                    "coordinate_count": 102,
                    "coordinate_sha256":
                        "61C417159DC8B646F321F809493721F982314929A12663F9CE1C51659F9E3BAF",
                    "finding_count": 153,
                    "signature_count": 22,
                },
            },
        )

    def test_private_review_rebuilds_exact_source_free_contract(self) -> None:
        rebuilt = BUILD.build(
            BUILD.DEFAULT_INPUT,
            BUILD.DEFAULT_POST_INPUT,
        )
        self.assertEqual(
            BUILD.canonical_json(rebuilt),
            BUILD.canonical_json(self.contract),
        )

    def test_current_high_confidence_findings_are_all_reviewed_false(
        self,
    ) -> None:
        allowed = {
            (
                row["category"],
                row["signature_sha256"],
                tuple(coordinate),
            )
            for row in self.contract["entries"]
            for coordinate in row["coordinates"]
        }
        report = json.loads(
            BUILD.DEFAULT_POST_INPUT.read_text(encoding="utf-8")
        )
        for row in report["issues"]:
            if row["category"] not in BUILD.EXPECTED_CONTRACT_COUNTS:
                continue
            key = (
                row["category"],
                BUILD.signature_digest(row),
                (int(row["block_id"]), int(row["record_id"])),
            )
            self.assertIn(key, allowed)

    def test_entry_digest_detects_tampering(self) -> None:
        rows = [dict(row) for row in self.contract["entries"]]
        rows[0]["coordinate_sha256"] = "0" * 64
        body = "\n".join(
            (
                f"{row['category']}:{row['signature_sha256']}:"
                f"{row['coordinate_count']}:{row['coordinate_sha256']}:"
                f"{row['finding_count']}"
            )
            for row in rows
        )
        self.assertNotEqual(
            BUILD.sha256_bytes(body.encode("ascii")),
            self.contract["entry_sha256"],
        )


if __name__ == "__main__":
    unittest.main()
