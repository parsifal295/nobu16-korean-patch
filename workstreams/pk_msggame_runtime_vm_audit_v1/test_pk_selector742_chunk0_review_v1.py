#!/usr/bin/env python3
"""Focused regressions for the selector-742 chunk-0 residual checkpoint."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
BUILDER_PATH = WORKSTREAM / "build_pk_selector742_chunk0_review_v1.py"


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "selector742_chunk0_review_under_test", BUILDER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


B = load_builder()


class Selector742Chunk0ReviewTests(unittest.TestCase):
    def test_builder_check_and_blocked_only_scope(self) -> None:
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
        self.assertEqual(payload["accepted_pending"], 0)
        self.assertEqual(payload["blocked_pending"], 25)
        self.assertFalse(payload["steam_write_performed"])

    def test_empty_decisions_and_frozen_private_evidence(self) -> None:
        self.assertEqual(B.PRIVATE_DECISIONS_PATH.read_bytes(), b"")
        self.assertEqual(B.sha256_file(B.PRIVATE_DECISIONS_PATH), B.EMPTY_SHA256)
        self.assertEqual(
            B.sha256_file(B.PRIVATE_EVIDENCE_PATH),
            B.EXPECTED_PRIVATE_EVIDENCE_SHA256,
        )
        report = B.build_report()
        self.assertEqual(report["result"]["sites"], 30)
        self.assertEqual(report["result"]["blocked_sites"], 30)
        self.assertEqual(report["result"]["decision_rows"], 0)
        self.assertEqual(report["result"]["promoted_pending_rows"], 0)

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
