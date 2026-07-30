#!/usr/bin/env python3
"""Focused regressions for the selector-514 chunk-1 checkpoint."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
BUILDER_PATH = WORKSTREAM / "build_pk_selector514_chunk1_review_v1.py"


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "selector514_chunk1_review_under_test", BUILDER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


B = load_builder()


class Selector514Chunk1ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = B.build_report()

    def test_builder_check_is_reproducible(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(BUILDER_PATH), "--check"],
            cwd=B.BASE.REPO,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["accepted_pending"], 31)
        self.assertEqual(payload["blocked_pending"], 15)
        self.assertFalse(payload["steam_write_performed"])

    def test_exact_scope_and_partition(self) -> None:
        result = self.report["result"]
        self.assertEqual(result["sites"], 26)
        self.assertEqual(result["assembly_branches"], 26 * 7)
        self.assertEqual(result["promoted_pending_rows"], 31)
        self.assertEqual(result["blocked_pending_rows"], 15)
        self.assertEqual(result["dependency_override_rows"], 4)

    def test_runtime_dependency_and_layout_proofs(self) -> None:
        proof = self.report["proof"]
        self.assertTrue(
            proof[
                "accepted_assemblies_current_relative_raw_g1n_nonexpanding"
            ]
        )
        self.assertTrue(
            proof["shared_empty_terminal_dependency_owned_by_chunk_zero"]
        )
        self.assertTrue(proof["same_gap_selectors_reviewed"])
        self.assertFalse(proof["automatic_space_or_grammar_repair_by_vm"])

    def test_private_decision_actions_are_exact(self) -> None:
        rows = B.BASE.load_decisions()
        self.assertEqual(len(rows), 34)
        self.assertEqual(
            Counter(row["action"] for row in rows),
            Counter(B.BASE.EXPECTED_ACTION_COUNTS),
        )

    def test_encoding_controls_and_reverse_overlay_pass(self) -> None:
        proof = self.report["proof"]
        self.assertTrue(proof["all_changed_record_control_gaps_preserved"])
        self.assertTrue(proof["all_literal_linebreak_counts_preserved"])
        self.assertTrue(proof["reverse_overlay_recovers_official_candidate"])

    def test_tracked_artifacts_are_source_free(self) -> None:
        cjk = re.compile(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]"
        )
        coordinate = re.compile(r'["\']\d+:\d+(?::\d+){0,2}["\']')
        for path in (BUILDER_PATH, SCRIPT, B.BASE.DEFAULT_PUBLIC_OUTPUT):
            content = path.read_text(encoding="utf-8")
            self.assertIsNone(cjk.search(content), path)
            self.assertIsNone(coordinate.search(content), path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
