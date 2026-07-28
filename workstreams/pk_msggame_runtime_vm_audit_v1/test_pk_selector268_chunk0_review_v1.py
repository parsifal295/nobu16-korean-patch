#!/usr/bin/env python3
"""Focused regressions for the selector-268 chunk-0 checkpoint."""

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
BUILDER_PATH = WORKSTREAM / "build_pk_selector268_chunk0_review_v1.py"


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "selector268_chunk0_review_under_test", BUILDER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


B = load_builder()


class Selector268Chunk0ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = B.build_report()
        cls.evidence = json.loads(
            B.BASE.PRIVATE_EVIDENCE_PATH.read_text(encoding="utf-8")
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
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["accepted_pending"], 10)
        self.assertEqual(payload["blocked_pending"], 6)
        self.assertFalse(payload["steam_write_performed"])

    def test_exact_fresh_partition(self) -> None:
        result = self.report["result"]
        self.assertEqual(
            (
                result["sites"],
                result["roots"],
                result["assembly_branches"],
                result["accepted_sites"],
                result["blocked_sites"],
                result["promoted_pending_rows"],
                result["blocked_pending_rows"],
                result["translation_overrides"],
                result["verification_renewals"],
            ),
            (13, 12, 91, 6, 7, 10, 6, 4, 0),
        )
        self.assertFalse(
            self.evidence["prior_evidence"][
                "stale_aggregate_counts_reused"
            ]
        )
        self.assertEqual(len(self.evidence["rewrite_attempt_roots"]), 5)

    def test_pending_semantics_are_fresh(self) -> None:
        rows = self.evidence["pending_semantic_rows"]
        self.assertEqual(len(rows), 16)
        self.assertTrue(
            all(
                row["fresh_semantic_review"] == "approved"
                and row["historical_factuality_review"] == "approved"
                and row["speaker_tone_review"] == "approved"
                and row["rewrite_attempt_count"] == 1
                and not row[
                    "prior_assembly_evidence_used_for_semantics"
                ]
                and set(row["context_utf8_sha256"])
                    == {"jp", "en", "sc", "tc"}
                for row in rows
            )
        )

    def test_actions_owned_overlap_and_candidate_are_exact(self) -> None:
        rows = B.load_decisions()
        self.assertEqual(
            Counter(row["action"] for row in rows),
            Counter(B.EXPECTED_ACTION_COUNTS),
        )
        self.assertTrue(all("auto" not in row["action"] for row in rows))
        self.assertEqual(
            B.coordinate_digest(row["coordinate"] for row in rows),
            B.EXPECTED_DIGESTS["decision"],
        )
        self.assertEqual(
            self.report["guards"]["reviewed_candidate_sha256"],
            B.BASE.EXPECTED_REVIEWED_CANDIDATE_SHA256,
        )

    def test_question_terminal_prior_and_layout_guards(self) -> None:
        B.validate_selector268_guards()
        proof = self.report["proof"]
        self.assertTrue(proof["all_selected_question_ordinals_reviewed"])
        self.assertTrue(proof["question_boundary_punctuation_exact"])
        self.assertTrue(
            proof[
                "accepted_assemblies_current_relative_raw_g1n_nonexpanding"
            ]
        )
        self.assertTrue(
            proof["pending_assembly_evidence_did_not_auto_promote"]
        )
        self.assertTrue(proof["completed_selector_overlap_freshly_reviewed"])
        self.assertTrue(proof["terminal_rows_read_only"])
        self.assertTrue(proof["source_only_action_count_zero"])
        self.assertTrue(proof["non_display_candidate_action_count_zero"])

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

    def test_public_artifact_is_frozen_and_source_free(self) -> None:
        self.assertEqual(
            B.sha256_file(B.DEFAULT_PUBLIC_OUTPUT),
            B.EXPECTED_PUBLIC_FILE_SHA256,
        )
        self.assertEqual(
            B.DEFAULT_PUBLIC_OUTPUT.read_bytes(),
            B.serialized(self.report),
        )
        cjk = re.compile(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]"
        )
        self.assertIsNone(
            cjk.search(B.DEFAULT_PUBLIC_OUTPUT.read_text(encoding="utf-8"))
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
