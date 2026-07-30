#!/usr/bin/env python3
"""Focused regressions for the selector-1078 chunk-1 checkpoint."""

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
BUILDER_PATH = WORKSTREAM / "build_pk_selector1078_chunk1_review_v1.py"


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "selector1078_chunk1_review_under_test", BUILDER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


B = load_builder()


class Selector1078Chunk1ReviewTests(unittest.TestCase):
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
        self.assertEqual(payload["accepted_pending"], 10)
        self.assertEqual(payload["blocked_pending"], 8)
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
        self.assertEqual(result["sites"], 22)
        self.assertEqual(result["roots"], 22)
        self.assertEqual(result["accepted_sites"], 4)
        self.assertEqual(result["blocked_sites"], 18)
        self.assertEqual(result["promoted_pending_rows"], 10)
        self.assertEqual(result["blocked_pending_rows"], 8)
        self.assertEqual(result["translation_overrides"], 5)
        self.assertEqual(result["rewrite_attempt_roots"], 4)

    def test_terminal_family_is_read_only(self) -> None:
        proof = self.report["proof"]
        self.assertEqual(
            proof["terminal_register_counts"],
            {"archaic": 2, "formal": 3, "plain": 2},
        )
        self.assertFalse(proof["context_terminals_authoritative"])
        self.assertFalse(proof["shared_terminal_modified"])
        terminal_roots = {(0, value) for value in B.CORE.TERMINALS}
        self.assertFalse({
            B.CORE.parse_coordinate(str(row["coordinate"]))[:2]
            for row in B.load_decisions()
        } & terminal_roots)

    def test_exclusion_guards_are_exact(self) -> None:
        proof = self.report["proof"]
        result = self.report["result"]
        self.assertFalse(proof["multi_control_partial_pass_authorized"])
        self.assertEqual(result["multi_control_blocked_sites"], 4)
        self.assertEqual(result["same_gap_branches"], 28)
        self.assertEqual(proof["source_only_action_count"], 0)
        self.assertEqual(proof["owned_overlap_automatic_promotion_count"], 0)
        self.assertEqual(
            proof["prior_pending_evidence_automatic_promotion_count"], 0
        )

    def test_runtime_and_reverse_proofs_are_complete(self) -> None:
        result = self.report["result"]
        proof = self.report["proof"]
        guards = self.report["guards"]
        self.assertEqual(result["assembly_branches"], 22 * 7)
        self.assertTrue(
            proof["accepted_assemblies_current_relative_raw_g1n_nonexpanding"]
        )
        self.assertTrue(proof["reverse_overlay_recovers_official_candidate"])
        self.assertNotEqual(
            guards["reviewed_candidate_sha256"],
            guards["official_candidate_sha256"],
        )
        self.assertEqual(
            guards["steam_archive_sha256_before"],
            guards["steam_archive_sha256_after"],
        )

    def test_private_decision_actions_are_exact(self) -> None:
        rows = B.load_decisions()
        self.assertEqual(len(rows), 10)
        self.assertEqual(
            Counter(row["action"] for row in rows),
            Counter(B.EXPECTED_ACTION_COUNTS),
        )
        self.assertEqual(
            B.coordinate_digest(str(row["coordinate"]) for row in rows),
            B.EXPECTED_DIGESTS["decision"],
        )

    def test_private_artifact_tamper_is_rejected(self) -> None:
        original = B.CORE.PRIVATE_DECISIONS_PATH
        raw = original.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            tampered = Path(directory) / "tampered.jsonl"
            tampered.write_bytes(raw[:-1] + b" \n")
            B.CORE.PRIVATE_DECISIONS_PATH = tampered
            try:
                with self.assertRaises(B.ReviewError):
                    B.build_report()
            finally:
                B.CORE.PRIVATE_DECISIONS_PATH = original

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
