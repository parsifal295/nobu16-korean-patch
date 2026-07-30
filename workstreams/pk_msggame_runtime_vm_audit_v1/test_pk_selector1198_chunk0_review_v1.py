#!/usr/bin/env python3
"""Focused regressions for the selector-1198 chunk-0 checkpoint."""

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
WORKSTREAM = SCRIPT.parent
BUILDER_PATH = WORKSTREAM / "build_pk_selector1198_chunk0_review_v1.py"


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "selector1198_chunk0_review_under_test", BUILDER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


B = load_builder()


class Selector1198Chunk0ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = B.build_report()

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
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["accepted_pending"], 8)
        self.assertEqual(payload["blocked_pending"], 32)
        self.assertFalse(payload["steam_write_performed"])

    def test_public_file_is_frozen(self) -> None:
        self.assertEqual(
            B.sha256_file(B.DEFAULT_PUBLIC_OUTPUT),
            B.EXPECTED_PUBLIC_FILE_SHA256,
        )
        self.assertEqual(
            B.DEFAULT_PUBLIC_OUTPUT.read_bytes(),
            B.serialized(self.report),
        )

    def test_exact_scope_and_partition(self) -> None:
        result = self.report["result"]
        self.assertEqual(result["sites"], 23)
        self.assertEqual(result["roots"], 23)
        self.assertEqual(result["promoted_pending_rows"], 8)
        self.assertEqual(result["blocked_pending_rows"], 32)
        self.assertEqual(result["translation_overrides"], 1)

    def test_runtime_and_same_gap_proofs_are_complete(self) -> None:
        result = self.report["result"]
        proof = self.report["proof"]
        self.assertEqual(result["assembly_branches"], 23 * 7)
        self.assertEqual(result["same_gap_branches"], 11 * 7)
        self.assertTrue(
            proof[
                "accepted_assemblies_current_relative_raw_g1n_nonexpanding"
            ]
        )
        self.assertTrue(proof["same_gap_selectors_reviewed"])
        self.assertFalse(proof["automatic_space_or_grammar_repair_by_vm"])

    def test_private_decision_actions_are_exact(self) -> None:
        rows = B.load_decisions()
        self.assertEqual(len(rows), 8)
        self.assertEqual(
            Counter(row["action"] for row in rows),
            Counter(B.EXPECTED_ACTION_COUNTS),
        )
        self.assertEqual(
            B.coordinate_digest(str(row["coordinate"]) for row in rows),
            B.EXPECTED_DIGESTS["decision"],
        )

    def test_encoding_controls_and_reverse_overlay_pass(self) -> None:
        proof = self.report["proof"]
        self.assertTrue(proof["all_changed_record_control_gaps_preserved"])
        self.assertTrue(proof["all_literal_linebreak_counts_preserved"])
        self.assertTrue(proof["reverse_overlay_recovers_official_candidate"])

    def test_private_decision_tamper_is_rejected(self) -> None:
        original_path = B.BASE.PRIVATE_DECISIONS_PATH
        raw = original_path.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            tampered = Path(directory) / "tampered.jsonl"
            tampered.write_bytes(raw[:-1] + b" \n")
            B.BASE.PRIVATE_DECISIONS_PATH = tampered
            try:
                with self.assertRaises(B.ReviewError):
                    B.build_report()
            finally:
                B.BASE.PRIVATE_DECISIONS_PATH = original_path

    def test_tracked_artifacts_are_source_free(self) -> None:
        cjk = re.compile(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]"
        )
        coordinate = re.compile(r'["\']\d+:\d+(?::\d+){0,2}["\']')
        for path in (BUILDER_PATH, SCRIPT, B.DEFAULT_PUBLIC_OUTPUT):
            content = path.read_text(encoding="utf-8")
            self.assertIsNone(cjk.search(content), path)
            self.assertIsNone(coordinate.search(content), path)
        self.assertFalse(
            self.report["distribution_policy"][
                "tracked_report_contains_translated_dialogue_text"
            ]
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
