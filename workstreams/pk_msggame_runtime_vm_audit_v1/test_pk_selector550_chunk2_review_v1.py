#!/usr/bin/env python3
"""Focused regressions for the selector-550 chunk-2 checkpoint."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.parent / "build_pk_selector550_chunk2_review_v1.py"
spec = importlib.util.spec_from_file_location("selector550_chunk2_test", BUILDER_PATH)
assert spec is not None and spec.loader is not None
B = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = B
spec.loader.exec_module(B)


class Selector550Chunk2ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = B.build_report()

    def test_exact_partition(self) -> None:
        self.assertEqual(self.report["result"], B.COUNTS)
        self.assertEqual(B.COUNTS["promoted_pending_rows"], 29)
        self.assertEqual(B.COUNTS["blocked_pending_rows"], 20)
        self.assertEqual(B.COUNTS["accepted_sites"], 45)
        self.assertEqual(B.COUNTS["blocked_sites"], 14)

    def test_seven_branch_and_same_gap_coverage(self) -> None:
        self.assertEqual(B.COUNTS["assembly_branches"], 59 * 7)
        self.assertEqual(B.COUNTS["same_gap_branches"], 2 * 7)
        self.assertTrue(
            self.report["proof"][
                "accepted_assemblies_current_relative_raw_g1n_nonexpanding"
            ]
        )
        self.assertFalse(
            self.report["proof"]["automatic_space_or_grammar_repair_by_vm"]
        )

    def test_actions_are_exact(self) -> None:
        rows = [
            json.loads(line)
            for line in B.DECISIONS.read_text(encoding="utf-8").splitlines()
            if line
        ]
        self.assertEqual(Counter(row["action"] for row in rows), Counter(B.ACTIONS))
        self.assertEqual(
            B.coordinate_digest(row["coordinate"] for row in rows),
            B.EXPECTED["decision_coordinates"],
        )

    def test_builder_check_is_reproducible(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(BUILDER_PATH), "--check"],
            cwd=B.REPO,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_private_tamper_is_rejected(self) -> None:
        original = B.DECISIONS
        with tempfile.TemporaryDirectory() as directory:
            tampered = Path(directory) / "tampered.jsonl"
            tampered.write_bytes(original.read_bytes()[:-1] + b" \n")
            B.DECISIONS = tampered
            try:
                with self.assertRaises(B.ReviewError):
                    B.build_report()
            finally:
                B.DECISIONS = original

    def test_public_and_tracked_files_are_source_free(self) -> None:
        cjk = re.compile(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]"
        )
        coordinate = re.compile(r'["\']\d+:\d+(?::\d+){0,2}["\']')
        for path in (BUILDER_PATH, SCRIPT, B.PUBLIC_OUTPUT):
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(cjk.search(text), path)
            self.assertIsNone(coordinate.search(text), path)
        self.assertEqual(
            B.sha256_file(B.PUBLIC_OUTPUT),
            B.EXPECTED["public"],
        )

    def test_live_steam_unchanged(self) -> None:
        self.assertEqual(B.sha256_file(B.STEAM), B.EXPECTED["steam"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
