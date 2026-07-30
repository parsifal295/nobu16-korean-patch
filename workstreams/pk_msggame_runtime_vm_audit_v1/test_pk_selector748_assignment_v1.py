#!/usr/bin/env python3
"""Tests for the immutable PK selector-748 assignment."""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.parent / "build_pk_selector748_assignment_v1.py"
spec = importlib.util.spec_from_file_location(
    "pk_selector748_assignment_test", BUILDER_PATH
)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot import {BUILDER_PATH}")
BUILDER = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = BUILDER
spec.loader.exec_module(BUILDER)


class Selector748AssignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.private_content, cls.public_content, cls.private, cls.public = (
            BUILDER.build_outputs()
        )

    def test_exact_coverage_and_source_only_partition(self) -> None:
        coverage = self.public["coverage"]
        self.assertEqual(
            (
                coverage["candidate_call_site_count"],
                coverage["candidate_call_root_count"],
                coverage["source_call_site_count"],
                coverage["source_only_repair_site_count"],
                coverage["direct_pending_call_site_count"],
                coverage["potential_current_pending_rows"],
            ),
            (102, 100, 114, 12, 62, 162),
        )
        candidate = set(self.private["scope"]["candidate_call_sites"])
        source_only = set(self.private["scope"]["source_only_repair_sites"])
        self.assertFalse(candidate & source_only)
        self.assertTrue(
            self.public["assignment"][
                "source_only_calls_separate_from_candidate_chunks"
            ]
        )

    def test_root_disjoint_weighted_chunks(self) -> None:
        chunks = self.private["chunks"]
        self.assertEqual(
            [row["workload_weight"] for row in chunks], [814, 815, 826]
        )
        self.assertEqual(
            [row["pending_row_upper_bound"] for row in chunks], [68, 47, 47]
        )
        for left in range(3):
            for right in range(left + 1, 3):
                self.assertFalse(
                    set(chunks[left]["roots"]) & set(chunks[right]["roots"])
                )
        self.assertEqual(
            set().union(*(set(row["sites"]) for row in chunks)),
            set(self.private["scope"]["candidate_call_sites"]),
        )

    def test_template_atoms_are_intact(self) -> None:
        self.assertEqual(self.private["identical_template_atoms"], [])
        self.assertFalse(
            self.public["assignment"]["identical_template_atoms_split"]
        )

    def test_public_is_source_free(self) -> None:
        self.assertIsNone(re.search(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
            self.public_content,
        ))
        self.assertIsNone(
            re.search(r"\b\d+:\d+(?::\d+){0,2}\b", self.public_content)
        )
        self.assertNotIn('"translation"', self.public_content)
        self.assertFalse(self.public["steam_write_performed"])

    def test_outputs_are_frozen(self) -> None:
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.DEFAULT_PRIVATE_OUTPUT),
            BUILDER.EXPECTED_PRIVATE_FILE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.DEFAULT_PUBLIC_OUTPUT),
            BUILDER.EXPECTED_PUBLIC_FILE_SHA256,
        )


if __name__ == "__main__":
    unittest.main()
