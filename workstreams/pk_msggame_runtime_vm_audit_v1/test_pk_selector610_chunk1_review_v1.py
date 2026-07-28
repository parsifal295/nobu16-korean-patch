#!/usr/bin/env python3
"""Focused regression tests for the selector-610 chunk-1 checkpoint."""

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
BUILDER_PATH = WORKSTREAM / "build_pk_selector610_chunk1_review_v1.py"


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "selector610_chunk1_review_under_test", BUILDER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


B = load_builder()


class Selector610Chunk1ReviewTests(unittest.TestCase):
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
        self.assertEqual(payload["accepted_pending"], 53)
        self.assertEqual(payload["dependency_branches"], 49)
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

    def test_exact_scope_and_promotion_counts(self) -> None:
        scope = self.report["scope"]
        promotion = self.report["promotion"]
        self.assertEqual(scope["site_count"], 77)
        self.assertEqual(scope["root_count"], 77)
        self.assertEqual(scope["pending_root_count"], 29)
        self.assertEqual(scope["pending_row_upper_bound"], 53)
        self.assertEqual(promotion["accepted_pending_coordinate_count"], 53)
        self.assertEqual(promotion["blocked_pending_coordinate_count"], 0)
        self.assertEqual(
            promotion["accepted_owned_overlap_pending_count"], 1
        )

    def test_all_runtime_branches_are_bound(self) -> None:
        proof = self.report["runtime_proof"]
        self.assertEqual(proof["assembly_branch_count"], 77 * 7)
        self.assertEqual(
            proof["dependency_cross_product_branch_count"], 7 * 7
        )
        self.assertTrue(
            proof["all_accepted_branches_current_relative_nonexpanding"]
        )
        self.assertFalse(proof["runtime_grammar_repair"])

    def test_private_decision_actions_are_exact(self) -> None:
        rows = B.load_decisions()
        self.assertEqual(len(rows), 70)
        self.assertEqual(
            Counter(row["action"] for row in rows),
            Counter(B.EXPECTED_DECISION_ACTION_COUNTS),
        )
        self.assertEqual(
            B.coordinate_digest(str(row["coordinate"]) for row in rows),
            B.EXPECTED_DECISION_COORDINATE_SHA256,
        )

    def test_encoding_controls_and_reverse_overlay_pass(self) -> None:
        proof = self.report["encoding_and_controls"]
        self.assertTrue(proof["all_changed_literals_strict_utf16le"])
        self.assertTrue(
            proof["all_changed_literal_linebreak_counts_preserved"]
        )
        self.assertTrue(proof["all_changed_record_control_gaps_preserved"])
        self.assertTrue(proof["reverse_overlay_exact"])

    def test_private_decision_tamper_is_rejected(self) -> None:
        original_path = B.PRIVATE_DECISIONS_PATH
        raw = original_path.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            tampered = Path(directory) / "tampered.jsonl"
            tampered.write_bytes(raw[:-1] + b" \n")
            B.PRIVATE_DECISIONS_PATH = tampered
            try:
                with self.assertRaises(B.ReviewError):
                    B.build_report()
            finally:
                B.PRIVATE_DECISIONS_PATH = original_path

    def test_tracked_artifacts_are_source_free(self) -> None:
        cjk = re.compile(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]"
        )
        coordinate = re.compile(r'["\']\d+:\d+(?::\d+){0,2}["\']')
        for path in (
            BUILDER_PATH,
            SCRIPT,
            B.DEFAULT_PUBLIC_OUTPUT,
        ):
            content = path.read_text(encoding="utf-8")
            self.assertIsNone(cjk.search(content), path)
            self.assertIsNone(coordinate.search(content), path)
        public = json.loads(
            B.DEFAULT_PUBLIC_OUTPUT.read_text(encoding="ascii")
        )
        self.assertFalse(public["privacy"]["contains_dialogue_bodies"])
        self.assertFalse(public["privacy"]["contains_exact_coordinates"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
