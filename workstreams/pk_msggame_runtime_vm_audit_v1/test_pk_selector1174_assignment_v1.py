#!/usr/bin/env python3
"""Tests for the deterministic PK selector-1174 review assignment."""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.parent / "build_pk_selector1174_assignment_v1.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = load_module(
    BUILDER_PATH, "pk_selector1174_assignment_test_builder_v1"
)


def default_args(**updates):
    values = {
        "private_output": BUILDER.DEFAULT_PRIVATE_OUTPUT,
        "public_output": BUILDER.DEFAULT_PUBLIC_OUTPUT,
        "check": True,
    }
    values.update(updates)
    return argparse.Namespace(**values)


class Selector1174AssignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (
            cls.private_content,
            cls.public_content,
            cls.manifest,
            cls.report,
        ) = BUILDER.build_outputs()
        BUILDER.validate_outputs(
            cls.private_content,
            cls.public_content,
            require_frozen_hashes=True,
        )

    def test_frozen_inputs_and_outputs_match(self) -> None:
        expected_inputs = {
            BUILDER.OFFICIAL_LEDGER_PATH:
                BUILDER.EXPECTED_OFFICIAL_LEDGER_SHA256,
            BUILDER.RANKING_BUILDER_PATH:
                BUILDER.EXPECTED_RANKING_BUILDER_SHA256,
            BUILDER.RANKING_PRIVATE_PATH:
                BUILDER.EXPECTED_RANKING_PRIVATE_SHA256,
            BUILDER.RANKING_PUBLIC_PATH:
                BUILDER.EXPECTED_RANKING_PUBLIC_SHA256,
            BUILDER.CROSS_BUILDER_PATH:
                BUILDER.EXPECTED_CROSS_BUILDER_SHA256,
            BUILDER.CROSS_DECISIONS_PATH:
                BUILDER.EXPECTED_CROSS_DECISIONS_SHA256,
            BUILDER.CROSS_COVERAGE_PATH:
                BUILDER.EXPECTED_CROSS_COVERAGE_SHA256,
            BUILDER.CROSS_PROMOTION_PATH:
                BUILDER.EXPECTED_CROSS_PROMOTION_REPORT_SHA256,
        }
        for path, expected in expected_inputs.items():
            with self.subTest(path=path):
                self.assertEqual(BUILDER.sha256_file(path), expected)
        expected_outputs = {
            BUILDER.DEFAULT_PRIVATE_OUTPUT: (
                BUILDER.EXPECTED_PRIVATE_FILE_SHA256,
                self.private_content,
            ),
            BUILDER.DEFAULT_PUBLIC_OUTPUT: (
                BUILDER.EXPECTED_PUBLIC_FILE_SHA256,
                self.public_content,
            ),
        }
        for path, (expected, content) in expected_outputs.items():
            with self.subTest(path=path):
                self.assertEqual(BUILDER.sha256_file(path), expected)
                self.assertEqual(path.read_text(encoding="utf-8"), content)

    def test_ranking_handoff_and_dispatch_contract_are_exact(self) -> None:
        coverage = self.report["coverage"]
        dispatch = self.report["dispatch_contract"]
        self.assertEqual(coverage["candidate_call_site_count"], 115)
        self.assertEqual(coverage["candidate_call_root_count"], 113)
        self.assertEqual(coverage["source_call_site_count"], 121)
        self.assertEqual(coverage["source_call_root_count"], 119)
        self.assertEqual(coverage["source_only_call_site_count"], 6)
        self.assertEqual(coverage["candidate_only_call_site_count"], 0)
        self.assertEqual(coverage["direct_pending_call_site_count"], 82)
        self.assertEqual(coverage["direct_pending_root_count"], 80)
        self.assertEqual(coverage["reachable_pending_root_count"], 80)
        self.assertTrue(dispatch["source_candidate_identical"])
        self.assertEqual(dispatch["node_count"], 13)
        self.assertEqual(dispatch["edge_count"], 13)
        self.assertEqual(dispatch["terminal_count"], 7)
        self.assertEqual(
            dispatch["edge_sha256"],
            BUILDER.EXPECTED_DISPATCH_EDGE_SHA256,
        )

    def test_cross_family_overlap_and_disjoint_partition_are_exact(self) -> None:
        coverage = self.report["coverage"]
        self.assertEqual(coverage["potential_current_pending_rows"], 242)
        self.assertEqual(coverage["cross_family_overlap_rows"], 18)
        self.assertEqual(coverage["disjoint_current_pending_rows"], 224)
        self.assertEqual(
            coverage["cross_family_overlap_sha256"],
            BUILDER.EXPECTED_OVERLAP_SHA256,
        )
        self.assertEqual(
            coverage["disjoint_current_pending_sha256"],
            BUILDER.EXPECTED_DISJOINT_SHA256,
        )
        scope = self.manifest["scope"]
        potential = set(scope["potential_current_pending_coordinates"])
        overlap = set(scope["cross_family_overlap_coordinates"])
        disjoint = set(scope["disjoint_current_pending_coordinates"])
        self.assertEqual(potential, overlap | disjoint)
        self.assertFalse(overlap & disjoint)

    def test_balanced_chunks_are_root_disjoint_and_feature_complete(self) -> None:
        chunks = self.manifest["chunks"]
        self.assertEqual(
            tuple(chunk["ordinal_end"] + 1 for chunk in chunks),
            BUILDER.EXPECTED_CUTS,
        )
        self.assertEqual(
            tuple(
                (
                    chunk["site_count"],
                    chunk["root_count"],
                    chunk["pending_row_upper_bound"],
                    chunk["cross_family_overlap_row_count"],
                    chunk["workload_weight"],
                )
                for chunk in chunks
            ),
            BUILDER.EXPECTED_CHUNK_COUNTS,
        )
        self.assertFalse(set(chunks[0]["roots"]) & set(chunks[1]["roots"]))
        self.assertEqual(
            sum(chunk["site_count"] for chunk in chunks),
            BUILDER.EXPECTED_SITE_COUNT,
        )
        self.assertEqual(
            sum(chunk["pending_row_upper_bound"] for chunk in chunks),
            BUILDER.EXPECTED_POTENTIAL_ROWS,
        )
        self.assertEqual(
            sum(chunk["cross_family_overlap_row_count"] for chunk in chunks),
            BUILDER.EXPECTED_OVERLAP_ROWS,
        )
        self.assertEqual(
            BUILDER.canonical_sha256(self.manifest["site_assignments"]),
            BUILDER.EXPECTED_SITE_ROW_SHA256,
        )
        required_flags = {
            "grammar_right_boundary",
            "layout_relative_expansion",
            "multi_control_gap",
            "protected_outer_space",
        }
        required_languages = {"en", "jp", "sc", "tc"}
        for row in self.manifest["site_assignments"]:
            self.assertEqual(set(row["flags"]), required_flags)
            self.assertEqual(
                set(row["language_available"]), required_languages
            )
        self.assertEqual(
            [chunk["flag_counts"]["multi_control_gap"] for chunk in chunks],
            [0, 0],
        )
        self.assertEqual(
            [
                chunk["language_available_counts"]
                for chunk in chunks
            ],
            [
                {"en": 13, "jp": 55, "sc": 17, "tc": 17},
                {"en": 32, "jp": 60, "sc": 30, "tc": 33},
            ],
        )

    def test_public_report_is_source_free_and_shadow_steam_unchanged(
        self,
    ) -> None:
        self.assertIsNone(
            re.search(
                r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
                r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
                self.public_content,
            )
        )
        self.assertIsNone(
            re.search(
                r"\b\d+:\d+(?::\d+){0,2}\b", self.public_content
            )
        )
        self.assertNotIn('"translation"', self.public_content)
        self.assertFalse(self.report["steam_write_performed"])
        shadow_pk = (
            BUILDER.RANKING.DEFAULT_STEAM_ROOT
            / "MSG_PK"
            / "JP"
            / "msggame.bin"
        )
        self.assertEqual(
            BUILDER.sha256_file(shadow_pk),
            BUILDER.EXPECTED_PK_CURRENT_SHA256,
        )

    def test_path_guards_reject_escape_and_steam(self) -> None:
        BUILDER.validate_paths(default_args())
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(
                BUILDER.AssignmentError, "below tmp"
            ):
                BUILDER.validate_paths(
                    default_args(
                        private_output=Path(temporary) / "assignment.json"
                    )
                )
            with self.assertRaisesRegex(
                BUILDER.AssignmentError, "fixed tracked path"
            ):
                BUILDER.validate_paths(
                    default_args(
                        public_output=Path(temporary) / "report.json"
                    )
                )
        with self.assertRaisesRegex(
            BUILDER.AssignmentError, "Steam data"
        ):
            BUILDER.validate_paths(
                default_args(
                    private_output=(
                        BUILDER.RANKING.DEFAULT_STEAM_ROOT
                        / "MSG_PK"
                        / "JP"
                        / "msggame.bin"
                    )
                )
            )


if __name__ == "__main__":
    unittest.main()
