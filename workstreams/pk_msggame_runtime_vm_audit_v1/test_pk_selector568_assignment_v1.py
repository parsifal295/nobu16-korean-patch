#!/usr/bin/env python3
"""Tests for the deterministic selector-568 assignment."""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.parent / "build_pk_selector568_assignment_v1.py"


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
    "pk_selector568_assignment_test_builder_v1",
)


def default_args(**updates):
    values = {
        "private_output": BUILDER.DEFAULT_PRIVATE_OUTPUT,
        "public_output": BUILDER.DEFAULT_PUBLIC_OUTPUT,
        "check": True,
    }
    values.update(updates)
    return argparse.Namespace(**values)


class Selector568AssignmentTests(unittest.TestCase):
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
            BUILDER.PREDECESSOR_PRIVATE_PATH:
                BUILDER.EXPECTED_PREDECESSOR_PRIVATE_SHA256,
            BUILDER.PREDECESSOR_PUBLIC_PATH:
                BUILDER.EXPECTED_PREDECESSOR_PUBLIC_SHA256,
            BUILDER.CURRENT_A19_LEDGER_PATH:
                BUILDER.EXPECTED_CURRENT_A19_LEDGER_SHA256,
            Path(BUILDER.BASE_AUDIT.DEFAULT_PK_PRISTINE):
                BUILDER.EXPECTED_PK_PRISTINE_SHA256,
            Path(BUILDER.BASE_AUDIT.DEFAULT_PK_CURRENT):
                BUILDER.EXPECTED_PK_CURRENT_SHA256,
        }
        expected_inputs.update(
            zip(
                BUILDER.SELECTOR538_DECISION_PATHS,
                BUILDER.EXPECTED_SELECTOR538_DECISION_SHA256,
            )
        )
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
        for path, (digest, content) in expected_outputs.items():
            with self.subTest(path=path):
                self.assertEqual(BUILDER.sha256_file(path), digest)
                self.assertEqual(path.read_text(encoding="utf-8"), content)

    def test_terminal_call_graph_and_ceilings_are_exact(self) -> None:
        graph = self.report["graph"]
        self.assertEqual(graph["candidate_call_site_count"], 222)
        self.assertEqual(graph["candidate_call_root_count"], 215)
        self.assertEqual(graph["source_call_site_count"], 231)
        self.assertEqual(graph["source_call_root_count"], 224)
        self.assertEqual(graph["source_only_site_count"], 9)
        self.assertEqual(graph["candidate_only_site_count"], 0)
        self.assertEqual(
            graph["direct_pending_ceiling"]["pending_row_count"],
            348,
        )
        self.assertEqual(
            graph["direct_pending_ceiling"]["pending_root_count"],
            147,
        )
        self.assertEqual(
            graph["structural_pending_ceiling"]["pending_row_count"],
            352,
        )
        self.assertEqual(
            graph["structural_pending_ceiling"]["pending_root_count"],
            150,
        )
        self.assertEqual(
            self.report["scope"]["terminal_coordinate_sha256"],
            BUILDER.EXPECTED_TERMINAL_COORDINATE_SHA256,
        )

    def test_a19_and_selector538_overlap_partitions_are_exact(self) -> None:
        overlap = self.report["graph"]["a19_and_selector538_overlap"]
        self.assertEqual(overlap["already_promoted_count"], 5)
        self.assertEqual(overlap["current_live_pending_count"], 343)
        self.assertEqual(
            overlap["planned_selector538_overlap_count"],
            17,
        )
        self.assertEqual(
            overlap["live_after_selector538_plan_count"],
            331,
        )
        self.assertEqual(
            overlap["selector538_full_planned_promotion_count"],
            277,
        )
        self.assertEqual(
            [
                (
                    row["current_live_pending_count"],
                    row["planned_selector538_overlap_count"],
                    row["live_after_selector538_plan_count"],
                )
                for row in overlap["chunk_live_counts"]
            ],
            list(BUILDER.EXPECTED_CHUNK_LIVE_COUNTS),
        )
        private = self.manifest["graph_evidence"]
        self.assertEqual(
            len(private["already_promoted_coordinates"]),
            5,
        )
        self.assertEqual(
            len(private["current_live_pending_coordinates"]),
            343,
        )
        self.assertEqual(
            len(private["selector538_planned_overlap_coordinates"]),
            17,
        )
        self.assertEqual(
            len(private["live_after_selector538_plan_coordinates"]),
            331,
        )

    def test_chunks_and_chunk0_priority_are_deterministic(self) -> None:
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
                    chunk["workload_weight"],
                )
                for chunk in chunks
            ),
            BUILDER.EXPECTED_CHUNK_COUNTS,
        )
        assigned = [
            site
            for chunk in chunks
            for site in chunk["sites"]
        ]
        self.assertEqual(len(assigned), 222)
        self.assertEqual(len(set(assigned)), 222)
        priority = self.manifest["graph_evidence"][
            "chunk0_live_pending_priority"
        ]
        self.assertEqual(len(priority), 75)
        self.assertEqual(
            priority,
            sorted(
                priority,
                key=lambda row: (
                    -row["live_after_selector538_plan_count"],
                    -row["current_live_pending_count"],
                    row["first_ordinal"],
                    row["root"],
                ),
            ),
        )
        self.assertEqual(
            BUILDER.canonical_sha256(priority),
            self.report["graph"]["a19_and_selector538_overlap"][
                "chunk0_priority_sha256"
            ],
        )

    def test_public_report_is_source_free_and_steam_unchanged(self) -> None:
        self.assertIsNone(
            re.search(
                r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
                r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
                self.public_content,
            )
        )
        self.assertIsNone(
            re.search(r"\b\d+:\d+(?::\d+){0,2}\b", self.public_content)
        )
        self.assertNotIn('"translation"', self.public_content)
        self.assertFalse(self.report["steam_write_performed"])
        self.assertEqual(
            BUILDER.sha256_file(
                Path(BUILDER.BASE_AUDIT.DEFAULT_PK_CURRENT)
            ),
            BUILDER.EXPECTED_PK_CURRENT_SHA256,
        )

    def test_path_guards_reject_escape_and_steam(self) -> None:
        BUILDER.validate_paths(default_args())
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(
                BUILDER.AssignmentError,
                "below tmp",
            ):
                BUILDER.validate_paths(
                    default_args(
                        private_output=Path(temporary) / "assignment.json"
                    )
                )
            with self.assertRaisesRegex(
                BUILDER.AssignmentError,
                "fixed tracked path",
            ):
                BUILDER.validate_paths(
                    default_args(
                        public_output=Path(temporary) / "report.json"
                    )
                )
        with self.assertRaisesRegex(
            BUILDER.AssignmentError,
            "Steam data",
        ):
            BUILDER.validate_paths(
                default_args(
                    private_output=Path(
                        BUILDER.BASE_AUDIT.DEFAULT_PK_CURRENT
                    )
                )
            )


if __name__ == "__main__":
    unittest.main()
