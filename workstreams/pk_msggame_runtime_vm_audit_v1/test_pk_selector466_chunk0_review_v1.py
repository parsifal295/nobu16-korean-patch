#!/usr/bin/env python3
"""Focused regressions for the selector-466 chunk-0 checkpoint."""

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
BUILDER_PATH = WORKSTREAM / "build_pk_selector466_chunk0_review_v1.py"


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "selector466_chunk0_review_under_test", BUILDER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


B = load_builder()


class Selector466Chunk0ReviewTests(unittest.TestCase):
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
        self.assertEqual(
            (payload["accepted_pending"], payload["blocked_pending"]),
            (3, 13),
        )
        self.assertFalse(payload["steam_write_performed"])

    def test_exact_single_pass_partition(self) -> None:
        result = self.report["result"]
        self.assertEqual(
            (
                result["sites"],
                result["roots"],
                result["assembly_branches"],
                result["atomic_neighbor_assembly_branches"],
                result["accepted_pending_roots"],
                result["accepted_sites"],
                result["blocked_pending_roots"],
                result["blocked_sites"],
                result["promoted_pending_rows"],
                result["blocked_pending_rows"],
                result["translation_overrides"],
                result["verification_renewals"],
            ),
            (38, 38, 266, 91, 2, 2, 6, 36, 3, 13, 2, 0),
        )
        self.assertEqual(
            (
                result["prior_assembly_pending_roots"],
                result["prior_assembly_pending_rows"],
                result["rewrite_attempt_roots"],
                result["same_gap_branches"],
                result["atomic_non_seven_way_gap_count"],
                result["non_display_candidate_sites"],
                result["source_only_action_count"],
                result["terminal_decision_rows"],
            ),
            (7, 12, 8, 0, 3, 0, 0, 0),
        )

    def test_decisions_are_exact_and_never_automatic(self) -> None:
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

    def test_atomic_multilingual_historical_review_is_complete(self) -> None:
        rows = self.evidence["pending_semantic_rows"]
        self.assertEqual(len(rows), 16)
        self.assertTrue(all(
            row["fresh_semantic_review"] == "approved"
            and row["historical_factuality_review"] == "approved"
            and row["speaker_tone_review"] == "approved"
            and row["rewrite_attempt_count"] == 1
            and not row["prior_assembly_evidence_used_for_semantics"]
            and set(row["context_utf8_sha256"]) == {"jp", "en", "sc", "tc"}
            for row in rows
        ))
        neighbors = self.evidence["atomic_neighbor_assembly_manifest"]
        self.assertEqual(len(neighbors), 91)
        self.assertTrue(all(
            row["current_relative_raw_g1n_nonexpanding"]
            for row in neighbors
            if row["review_disposition"] == "approved_atomic_root"
        ))
        self.assertEqual(
            sorted({row["register"] for row in neighbors}),
            ["archaic", "formal", "plain"],
        )

    def test_terminal_template_owned_and_exclusion_proofs(self) -> None:
        B.validate_selector466_guards()
        proof = self.report["proof"]
        for key in (
            "all_atomic_neighbor_alternatives_reviewed",
            "completed_selector_overlap_freshly_blocked",
            "repeated_template_atom_single_disposition",
            "historical_register_exact_reviewed",
            "pending_assembly_evidence_did_not_auto_promote",
            "terminal_register_order_preserved",
            "terminal_context_languages_non_authoritative",
            "terminal_rows_verified_read_only",
            "source_only_action_count_zero",
            "non_display_candidate_action_count_zero",
        ):
            self.assertTrue(proof[key])

    def test_private_tamper_and_public_privacy_contracts(self) -> None:
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
