#!/usr/bin/env python3
"""Focused regressions for the selector-730 chunk-0 checkpoint."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
BUILDER_PATH = WORKSTREAM / "build_pk_selector730_chunk0_review_v1.py"


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "selector730_chunk0_review_under_test", BUILDER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


B = load_builder()


class Selector730Chunk0ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = B.build_report()
        cls.evidence = B.load_json(B.PRIVATE_EVIDENCE_PATH)

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
            (
                payload["accepted"],
                payload["blocked"],
                payload["overrides"],
                payload["shared_cartesian_recomputed"],
            ),
            (0, 12, 0, 0),
        )
        self.assertFalse(payload["steam_write_performed"])

    def test_exact_blocked_partition(self) -> None:
        result = self.report["result"]
        self.assertEqual(
            (
                result["assigned_sites"],
                result["assigned_roots"],
                result["accepted_pending_roots"],
                result["accepted_pending_rows"],
                result["blocked_pending_roots"],
                result["blocked_pending_rows"],
                result["decision_rows"],
                result["promotion_rows"],
                result["translation_overrides"],
                result["rewrite_attempt_roots"],
            ),
            (21, 21, 0, 0, 8, 12, 0, 0, 0, 8),
        )
        self.assertEqual(B.PRIVATE_DECISIONS_PATH.read_bytes(), b"")

    def test_shared_cartesian_manifest_is_reused_not_recomputed(self) -> None:
        result = self.report["result"]
        self.assertEqual(
            (
                result["shared_cartesian_roots"],
                result["shared_cartesian_branches_reused"],
                result["pending_cartesian_roots"],
                result["pending_cartesian_branches_reused"],
            ),
            (19, 931, 8, 392),
        )
        self.assertEqual(
            self.report["proof"]["cartesian_branches_recomputed"], 0
        )
        references = self.evidence["chunk_cartesian_references"]
        self.assertEqual(len(references), 19)
        self.assertTrue(all(row["branch_count"] == 49 for row in references))
        self.assertEqual(
            self.report["guards"]["shared_cartesian_manifest_sha256"],
            B.EXPECTED_SHA256["shared_private"],
        )

    def test_fresh_semantics_and_single_attempt_blocks(self) -> None:
        rows = self.evidence["pending_semantic_reviews"]
        roots = self.evidence["root_reviews"]
        self.assertEqual((len(rows), len(roots)), (12, 8))
        self.assertTrue(all(
            row["fresh_semantic_review"] == "approved"
            and row["historical_factuality_review"] == "approved"
            and row["speaker_tone_review"] == "approved"
            and row["jp_source_authoritative"]
            and not row["prior_or_owned_evidence_used_for_semantics"]
            and row["rewrite_attempt_count"] == 1
            and row["translation_override_count"] == 0
            for row in rows
        ))
        self.assertTrue(all(
            row["caller_rewrite_attempt_count"] == 1
            and row["disposition"] == "blocked_atomic_root"
            and row["shared_manifest_reused"]
            and len(row["ordered_controls"]) == 2
            for row in roots
        ))

    def test_terminal_template_owned_and_exclusion_guards(self) -> None:
        result = self.report["result"]
        self.assertEqual(
            (
                result["terminal_pending_rows"],
                result["terminal_decision_rows"],
                result["template_root_count"],
                result["template_pending_rows"],
                result["owned_overlap_root_count"],
                result["owned_overlap_relation_count"],
                result["owned_overlap_pending_rows"],
                result["prior_assembly_root_count"],
                result["prior_assembly_pending_rows"],
                result["source_only_site_count"],
                result["source_only_action_count"],
                result["non_display_action_count"],
            ),
            (7, 0, 2, 2, 3, 3, 6, 6, 10, 5, 0, 0),
        )
        self.assertTrue(all(
            row["runtime_review"] == "pending"
            and not row["decision_authorized"]
            and not any(row["context_nonempty"].values())
            for row in self.evidence["terminal_manifest"]
        ))
        for key in (
            "automatic_promotion_count_zero",
            "controls_tags_and_linebreaks_preserved",
            "same_gap_roots_blocked_atomically",
            "shared_cartesian_manifest_reused",
            "source_only_action_count_zero",
            "terminal_rows_pending_read_only",
        ):
            self.assertTrue(self.report["proof"][key])

    def test_private_tamper_and_public_privacy_contracts(self) -> None:
        original = B.PRIVATE_EVIDENCE_PATH
        raw = original.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            tampered = Path(directory) / "tampered.json"
            tampered.write_bytes(raw[:-1] + b" \n")
            B.PRIVATE_EVIDENCE_PATH = tampered
            try:
                with self.assertRaises(B.ReviewError):
                    B.build_report()
            finally:
                B.PRIVATE_EVIDENCE_PATH = original
        self.assertEqual(
            B.sha256_file(B.DEFAULT_PUBLIC_OUTPUT),
            B.EXPECTED_PUBLIC_SHA256,
        )
        self.assertEqual(
            B.DEFAULT_PUBLIC_OUTPUT.read_bytes(),
            B.serialized(self.report),
        )
        cjk = re.compile(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]"
        )
        coordinate = re.compile(r"\b\d+:\d+(?::\d+){0,2}\b")
        payload = B.DEFAULT_PUBLIC_OUTPUT.read_text(encoding="ascii")
        self.assertIsNone(cjk.search(payload))
        self.assertIsNone(coordinate.search(payload))
        for path in (BUILDER_PATH, SCRIPT):
            self.assertIsNone(cjk.search(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
