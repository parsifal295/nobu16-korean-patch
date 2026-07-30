#!/usr/bin/env python3
"""Focused tests for the immutable selector-1126 assignment."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


PATH = Path(__file__).with_name("build_pk_selector1126_assignment_v1.py")
SPEC = importlib.util.spec_from_file_location("selector1126_assignment_test", PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {PATH}")
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class Selector1126AssignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.private_content, cls.public_content, cls.private, cls.public = (
            BUILDER.build_outputs()
        )

    def test_exact_partition(self) -> None:
        self.assertEqual(
            [
                self.public["coverage"]["candidate_call_site_count"],
                self.public["coverage"]["source_only_repair_site_count"],
                self.public["coverage"]["potential_current_pending_rows"],
            ],
            [114, 14, 141],
        )
        self.assertEqual(
            [row["site_count"] for row in self.public["assignment"]["chunks"]],
            [38, 38, 38],
        )

    def test_roots_and_template_atoms_are_not_split(self) -> None:
        chunks = self.private["chunks"]
        for left in range(3):
            for right in range(left + 1, 3):
                self.assertFalse(
                    set(chunks[left]["roots"]) & set(chunks[right]["roots"])
                )
        self.assertEqual(
            sorted(len(group) for group in self.private["identical_template_atoms"]),
            [4, 4, 8, 8],
        )
        self.assertFalse(
            self.public["assignment"]["identical_template_atoms_split"]
        )

    def test_source_only_is_separate_and_public_is_source_free(self) -> None:
        candidate = set(self.private["scope"]["candidate_call_sites"])
        source_only = set(self.private["scope"]["source_only_repair_sites"])
        self.assertFalse(candidate & source_only)
        BUILDER.assert_source_free(self.public)
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
