#!/usr/bin/env python3
"""Source-free tests for selector-748 chunk-2 review."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from collections import Counter
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.parent / "build_pk_selector748_chunk2_review_v1.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = load_module(BUILDER_PATH, "pk_selector748_chunk2_test_builder")


class Selector748Chunk2ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.public = BUILDER.build_public()
        cls.decisions = [
            json.loads(line)
            for line in BUILDER.DECISIONS.read_text(
                encoding="utf-8"
            ).splitlines()
            if line
        ]
        cls.evidence = json.loads(
            BUILDER.EVIDENCE.read_text(encoding="utf-8")
        )

    def test_counts_are_exact(self) -> None:
        self.assertEqual(self.public["result"], BUILDER.COUNTS)

    def test_action_partition_is_exact(self) -> None:
        self.assertEqual(
            Counter(row["action"] for row in self.decisions),
            Counter(BUILDER.ACTIONS),
        )

    def test_all_sites_and_branches_are_recorded(self) -> None:
        self.assertEqual(len(self.evidence["site_reviews"]), 34)
        self.assertEqual(len(self.evidence["assembly_manifest"]), 238)

    def test_blocked_rows_are_not_decided(self) -> None:
        blocked = set(self.evidence["blocked"]["pending_coordinates"])
        decided = {row["coordinate"] for row in self.decisions}
        self.assertEqual(len(blocked), 20)
        self.assertTrue(blocked.isdisjoint(decided))

    def test_shared_terminal_repairs_are_exact(self) -> None:
        shared = [
            row
            for row in self.decisions
            if row["overlap_owner"] == "selector748_shared_terminal"
        ]
        self.assertEqual(len(shared), 7)
        self.assertTrue(
            all(
                row["action"]
                == "translation_override_and_runtime_promotion"
                for row in shared
            )
        )

    def test_promotions_are_exact(self) -> None:
        promoted = [
            row
            for row in self.decisions
            if row["action"].endswith("runtime_promotion")
        ]
        self.assertEqual(len(promoted), 34)

    def test_candidate_and_reverse_overlay_are_frozen(self) -> None:
        digests = self.evidence["digests"]
        self.assertEqual(
            digests["reviewed_candidate_sha256"],
            BUILDER.EXPECTED["reviewed_candidate"],
        )
        self.assertEqual(
            digests["reverse_overlay_sha256"],
            BUILDER.EXPECTED["official_candidate"],
        )

    def test_public_report_is_source_free(self) -> None:
        decoded = (
            BUILDER.canonical_bytes(self.public) + b"\n"
        ).decode("utf-8")
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
        self.assertFalse(self.public["steam_write_performed"])

    def test_two_builds_are_identical(self) -> None:
        self.assertEqual(BUILDER.build_public(), self.public)


if __name__ == "__main__":
    unittest.main()
