#!/usr/bin/env python3
"""Focused regression tests for selector-610 chunk-2 review."""

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
BUILDER_PATH = WORKSTREAM / "build_pk_selector610_chunk2_review_v1.py"


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "selector610_chunk2_review_under_test", BUILDER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


B = load_builder()


class Selector610Chunk2ReviewTests(unittest.TestCase):
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
        self.assertEqual(payload["accepted_pending"], 48)
        self.assertEqual(payload["blocked_sites"], 27)
        self.assertFalse(payload["steam_write_performed"])

    def test_public_file_is_frozen(self) -> None:
        self.assertEqual(
            B.sha256_file(B.DEFAULT_PUBLIC_OUTPUT),
            B.EXPECTED_SHA256["public"],
        )
        self.assertEqual(
            B.DEFAULT_PUBLIC_OUTPUT.read_bytes(),
            B.serialized(self.report),
        )

    def test_scope_and_result_counts_are_exact(self) -> None:
        self.assertEqual(
            self.report["scope"],
            {
                "chunk_id": 2,
                "owned_overlap_roots": 24,
                "pending_rows": 48,
                "roots": 76,
                "selector": 610,
                "sites": 76,
            },
        )
        self.assertEqual(
            self.report["result"],
            B.EXPECTED_COUNTS,
        )
        self.assertEqual(
            self.report["result"]["accepted_pending_rows"], 48
        )
        self.assertEqual(
            self.report["result"]["blocked_pending_rows"], 0
        )

    def test_uniform_template_proof_is_complete(self) -> None:
        proof = self.report["proof"]
        self.assertTrue(proof["template_uniform_rule_indivisible"])
        self.assertTrue(proof["all_template_records_byte_identical"])
        self.assertTrue(
            proof["all_template_cross_product_branches_nonexpanding"]
        )
        self.assertTrue(proof["selector538_verified_companions_renewed"])
        self.assertFalse(proof["runtime_grammar_repair"])
        self.assertEqual(
            self.report["result"]["template_cross_product_branches"],
            7 * 7 * 7,
        )
        self.assertEqual(
            self.report["result"]["template_correlated_branches"], 7
        )

    def test_decision_actions_are_exact(self) -> None:
        rows = B.load_decisions()
        self.assertEqual(len(rows), 140)
        self.assertEqual(
            Counter(row["action"] for row in rows),
            Counter(B.EXPECTED_ACTION_COUNTS),
        )
        self.assertEqual(
            B.coordinate_digest(str(row["coordinate"]) for row in rows),
            B.EXPECTED_DIGESTS["decision_coordinate_sha256"],
        )

    def test_control_and_reverse_guards_pass(self) -> None:
        self.assertEqual(self.report["status"], "PASS")
        self.assertTrue(
            self.report["proof"][
                "same_gap_complete_ending_collisions_blocked"
            ]
        )
        self.assertFalse(self.report["steam_write_performed"])
        self.assertFalse(
            self.report["privacy"]["shared_integration_mutated"]
        )

    def test_private_decision_tamper_is_rejected(self) -> None:
        original = B.PRIVATE_DECISIONS_PATH
        raw = original.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            tampered = Path(directory) / "tampered.jsonl"
            tampered.write_bytes(raw[:-1] + b" \n")
            B.PRIVATE_DECISIONS_PATH = tampered
            try:
                with self.assertRaises(B.ReviewError):
                    B.build_report()
            finally:
                B.PRIVATE_DECISIONS_PATH = original

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
        self.assertFalse(
            self.report["privacy"]["contains_dialogue_bodies"]
        )
        self.assertFalse(
            self.report["privacy"]["contains_exact_coordinates"]
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
