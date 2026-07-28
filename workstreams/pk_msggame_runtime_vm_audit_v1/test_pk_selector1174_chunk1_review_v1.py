#!/usr/bin/env python3
"""Tests for the PK selector-1174 chunk-1 semantic review."""

from __future__ import annotations

import copy
import importlib.util
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.parent / "build_pk_selector1174_chunk1_review_v1.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = load_module(
    BUILDER_PATH,
    "pk_selector1174_chunk1_review_test_builder_v1",
)


class Selector1174Chunk1ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.assignment = BUILDER.load_json_exact(BUILDER.ASSIGNMENT_PATH)
        cls.chunk = cls.assignment["chunks"][BUILDER.CHUNK_ID]
        cls.private = BUILDER.load_json_exact(BUILDER.PRIVATE_REVIEW_PATH)
        cls.world = BUILDER.load_world()
        cls.validated = BUILDER.validate_private(
            cls.private,
            assignment=cls.assignment,
            chunk=cls.chunk,
            world=cls.world,
        )
        cls.report = BUILDER.build_report()
        cls.content = BUILDER.canonical_bytes(cls.report) + b"\n"

    def test_assignment_cross_predecessor_and_outputs_are_frozen(self) -> None:
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.ASSIGNMENT_PATH),
            BUILDER.EXPECTED_ASSIGNMENT_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.CROSS_DECISIONS_PATH),
            BUILDER.EXPECTED_CROSS_DECISIONS_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.PRIVATE_REVIEW_PATH),
            BUILDER.EXPECTED_PRIVATE_REVIEW_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_bytes(self.world["candidate_blob"]),
            BUILDER.EXPECTED_CROSS_CANDIDATE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_bytes(self.validated["proposal_blob"]),
            BUILDER.EXPECTED_PROPOSAL_CANDIDATE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_bytes(self.content),
            BUILDER.EXPECTED_PUBLIC_FILE_SHA256,
        )
        self.assertEqual(BUILDER.DEFAULT_OUTPUT.read_bytes(), self.content)
        self.assertEqual(
            self.private["inputs"]["corrected_cross_commit"],
            "d2a89f11e9c0bb75e03e9ccc19ce0ca548fa45e8",
        )

    def test_all_60_sites_and_420_runtime_branches_are_reviewed(self) -> None:
        self.assertEqual(
            self.private["counts"],
            {
                "accepted_pending_coordinates": 98,
                "accepted_roots": 41,
                "accepted_sites": 42,
                "assemblies": 420,
                "blocked_pending_coordinates": 37,
                "blocked_roots": 18,
                "cross_overlap_blocked": 10,
                "cross_overlap_renewals": 3,
                "disjoint_potential_promotions": 95,
                "keep": 7,
                "reject": 18,
                "rewrite": 35,
                "sites": 60,
            },
        )
        rows = self.private["site_reviews"]
        self.assertEqual(len(rows), 60)
        self.assertEqual(
            [row["ordinal"] for row in rows],
            list(range(55, 115)),
        )
        self.assertEqual(
            sum(len(row["assemblies"]) for row in rows),
            420,
        )
        for row in rows:
            self.assertEqual(len(row["assemblies"]), 7)
            authority = row["multilingual_authority"]
            self.assertTrue(authority["jp_is_semantic_authority"])
            self.assertTrue(authority["speaker_tone_reviewed"])
            self.assertTrue(authority["historical_terms_reviewed"])
            self.assertEqual(authority["review_passes"], 2)
            control = row["control_and_boundary_proof"]
            self.assertTrue(control["record_control_gaps_preserved"])
            self.assertTrue(control["literal_linebreak_count_preserved"])
            self.assertTrue(control["existing_leading_whitespace_preserved"])
            self.assertTrue(control["existing_trailing_whitespace_preserved"])

    def test_accepted_branches_pass_register_and_relative_width_guards(self) -> None:
        accepted = [
            row
            for row in self.private["site_reviews"]
            if row["decision"] != "reject"
        ]
        rejected = [
            row
            for row in self.private["site_reviews"]
            if row["decision"] == "reject"
        ]
        self.assertEqual(len(accepted), 42)
        self.assertEqual(len(rejected), 18)
        for row in accepted:
            self.assertTrue(row["all_seven_register_branches_proven"])
            self.assertTrue(row["all_seven_width_branches_nonexpanding"])
            for branch in row["assemblies"]:
                self.assertTrue(branch["register_and_grammar_proven"])
                self.assertTrue(
                    branch["current_relative_raw_g1n_nonexpanding"]
                )
                self.assertTrue(branch["line_count_match"])
                self.assertIn(
                    branch["register_semantic"],
                    {"plain_empty", "contextual_honorific_elided"},
                )
        for row in rejected:
            self.assertTrue(row["reject_reason"])
            self.assertFalse(row["all_seven_register_branches_proven"])

    def test_pending_and_cross_overlap_disposition_is_exact(self) -> None:
        result = self.report["result"]
        self.assertEqual(result["accepted_pending_coordinate_count"], 98)
        self.assertEqual(result["blocked_pending_coordinate_count"], 37)
        self.assertEqual(result["cross_verification_renewal_count"], 3)
        self.assertEqual(result["blocked_cross_overlap_count"], 10)
        self.assertEqual(result["disjoint_potential_promotion_count"], 95)
        self.assertEqual(result["translation_override_count"], 35)
        self.assertEqual(result["pending_translation_override_count"], 19)
        self.assertEqual(result["nonpending_translation_override_count"], 16)
        exact = self.private["exact_maps"]
        self.assertEqual(
            set(exact["cross_overlap_renewal_coordinates"])
            | set(exact["cross_overlap_blocked_coordinates"]),
            set(self.chunk["cross_family_overlap_coordinates"]),
        )
        self.assertTrue(
            set(exact["cross_overlap_renewal_coordinates"]).isdisjoint(
                exact["disjoint_potential_promotion_coordinates"]
            )
        )

    def test_translation_overrides_are_strict_utf16_and_reverse_cleanly(self) -> None:
        overrides = self.private["exact_maps"]["translation_overrides"]
        for translation in overrides.values():
            encoded = translation.encode("utf-16le", errors="strict")
            self.assertEqual(
                encoded.decode("utf-16le", errors="strict"),
                translation,
            )
        candidate_records = self.world["candidate_records"]
        reverse_map = {
            BUILDER.parse_coordinate(coordinate):
                BUILDER.ENGINE.parse_record_literals(
                    candidate_records[
                        BUILDER.parse_coordinate(coordinate)[:2]
                    ]
                )[BUILDER.parse_coordinate(coordinate)[2]].text
            for coordinate in overrides
        }
        reversed_blob = BUILDER.ENGINE.rebuild_packed_with_literals(
            self.validated["proposal_blob"],
            reverse_map,
        )
        self.assertEqual(reversed_blob, self.world["candidate_blob"])

    def test_tampered_private_review_is_rejected(self) -> None:
        tampered = copy.deepcopy(self.private)
        row = next(
            row
            for row in tampered["site_reviews"]
            if row["decision"] == "rewrite"
        )
        row["reviewed_left_translation"] += "X"
        with self.assertRaises(BUILDER.ReviewError):
            BUILDER.validate_private(
                tampered,
                assignment=self.assignment,
                chunk=self.chunk,
                world=self.world,
            )

    def test_two_builds_are_identical_and_live_steam_is_read_only(self) -> None:
        first = BUILDER.serialized_report()
        second = BUILDER.serialized_report()
        self.assertEqual(first, second)
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.LIVE_STEAM_PK),
            BUILDER.EXPECTED_STEAM_PK_SHA256,
        )
        self.assertFalse(self.report["steam_write_performed"])
        self.assertEqual(
            self.report["guards"]["steam_archive_sha256_before"],
            self.report["guards"]["steam_archive_sha256_after"],
        )

    def test_public_report_is_source_free_and_output_path_is_fixed(self) -> None:
        decoded = self.content.decode("ascii")
        self.assertIsNone(
            re.search(
                r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
                r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
                decoded,
            )
        )
        self.assertIsNone(
            re.search(r"\b\d+:\d+(?::\d+){0,2}\b", decoded)
        )
        self.assertNotIn('"translation"', decoded)
        self.assertNotIn('"exact_maps"', decoded)
        self.assertFalse(
            self.report["proof"]["msggame_event_912px_rule_applied"]
        )
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(
                BUILDER.ReviewError,
                "fixed tracked path",
            ):
                BUILDER.main(
                    ["--output", str(Path(temporary) / "report.json")]
                )


if __name__ == "__main__":
    unittest.main()
