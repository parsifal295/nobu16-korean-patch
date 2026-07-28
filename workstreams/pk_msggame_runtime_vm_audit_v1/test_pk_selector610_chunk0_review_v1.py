#!/usr/bin/env python3
"""Source-free tests for selector-610 chunk-0 review."""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from collections import Counter
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.parent / "build_pk_selector610_chunk0_review_v1.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = load_module(BUILDER_PATH, "pk_selector610_chunk0_test_builder")


class Selector610Chunk0ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.outputs = BUILDER.build_outputs()
        BUILDER.validate_frozen(cls.outputs)

    def test_counts_are_exact(self) -> None:
        self.assertEqual(
            self.outputs["evidence"]["counts"], BUILDER.EXPECTED_COUNTS
        )

    def test_action_partition_is_exact(self) -> None:
        self.assertEqual(
            Counter(row["action"] for row in self.outputs["decisions"]),
            Counter(BUILDER.EXPECTED_ACTION_COUNTS),
        )

    def test_all_sites_and_dependencies_are_recorded(self) -> None:
        evidence = self.outputs["evidence"]
        self.assertEqual(len(evidence["site_reviews"]), 77)
        self.assertEqual(len(evidence["assembly_manifest"]), 539)
        self.assertEqual(
            len(evidence["dependency_assembly_manifest"]), 28
        )

    def test_blocked_rows_are_not_promoted(self) -> None:
        blocked = set(
            self.outputs["evidence"]["blocked"]["pending_coordinates"]
        )
        decided = {
            row["coordinate"] for row in self.outputs["decisions"]
        }
        self.assertEqual(len(blocked), 25)
        self.assertTrue(blocked.isdisjoint(decided))

    def test_candidate_and_reverse_overlay_are_frozen(self) -> None:
        digests = self.outputs["evidence"]["digests"]
        self.assertEqual(
            digests["reviewed_candidate_sha256"],
            BUILDER.EXPECTED_REVIEWED_CANDIDATE_SHA256,
        )
        self.assertEqual(
            digests["reverse_overlay_sha256"],
            BUILDER.EXPECTED_OFFICIAL_CANDIDATE_SHA256,
        )

    def test_public_report_is_source_free(self) -> None:
        decoded = self.outputs["public_content"].decode("ascii")
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
        self.assertNotIn('"reviewed_translation"', decoded)
        self.assertFalse(self.outputs["public"]["steam_write_performed"])

    def test_two_builds_are_identical(self) -> None:
        second = BUILDER.build_outputs()
        self.assertEqual(
            second["public_content"], self.outputs["public_content"]
        )


if __name__ == "__main__":
    unittest.main()
