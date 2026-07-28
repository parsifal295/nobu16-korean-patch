#!/usr/bin/env python3
"""Focused tests for the immutable two-chunk selector-1090 assignment."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).with_name("build_pk_selector1090_assignment_v1.py")
SPEC = importlib.util.spec_from_file_location("selector1090_assignment_test", PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {PATH}")
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class Selector1090AssignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.private_content, cls.public_content, cls.private, cls.public = (
            BUILDER.build_outputs()
        )

    def test_exact_two_way_partition(self) -> None:
        self.assertEqual(self.public["assignment"]["chunk_count"], 2)
        self.assertEqual(
            (
                self.public["coverage"]["candidate_call_site_count"],
                self.public["coverage"]["source_call_site_count"],
                self.public["coverage"]["source_only_repair_site_count"],
                self.public["coverage"]["potential_current_pending_rows"],
                self.public["coverage"]["owned_overlap_root_count"],
            ),
            (96, 104, 8, 80, 10),
        )
        self.assertEqual(
            tuple(
                (
                    chunk["site_count"],
                    chunk["root_count"],
                    chunk["pending_root_count"],
                    chunk["pending_row_upper_bound"],
                    chunk["owned_overlap_root_count"],
                    chunk["workload_weight"],
                )
                for chunk in self.public["assignment"]["chunks"]
            ),
            BUILDER.EXPECTED_CHUNK_METRICS,
        )
        chunks = self.private["chunks"]
        self.assertFalse(set(chunks[0]["roots"]) & set(chunks[1]["roots"]))
        self.assertFalse(
            self.public["assignment"]["identical_template_atoms_split"]
        )
        self.assertTrue(
            self.public["assignment"][
                "source_only_calls_separate_from_candidate_chunks"
            ]
        )

    def test_outputs_are_frozen_and_source_free(self) -> None:
        BUILDER.assert_source_free(self.public)
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.DEFAULT_PRIVATE_OUTPUT),
            BUILDER.EXPECTED_PRIVATE_FILE_SHA256,
        )
        self.assertEqual(
            BUILDER.sha256_file(BUILDER.DEFAULT_PUBLIC_OUTPUT),
            BUILDER.EXPECTED_PUBLIC_FILE_SHA256,
        )
        self.assertFalse(self.public["steam_write_performed"])


if __name__ == "__main__":
    unittest.main()
