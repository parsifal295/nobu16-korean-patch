#!/usr/bin/env python3
"""Tests for the immutable selector-292 targeted ledger checkpoint."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BUILDER_PATH = (
    WORKSTREAM
    / "build_runtime_vm_post_selector292_consolidated_checkpoint_v1.py"
)


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "selector292_checkpoint_tested", BUILDER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


B = load_builder()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="ascii"))


class Selector292TargetedCheckpointTest(unittest.TestCase):
    def test_builder_check(self) -> None:
        result = subprocess.run(
            [sys.executable, str(BUILDER_PATH), "--check"],
            cwd=REPO,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("promoted=21 pending=6130", result.stdout)
        self.assertIn(
            "full_integration_rebuild=false steam_write=false",
            result.stdout,
        )

    def test_frozen_output_hashes(self) -> None:
        self.assertTrue(B.is_frozen())
        self.assertEqual(
            sha256_file(B.DEFAULT_PRIVATE_OUTPUT),
            B.EXPECTED_PRIVATE_OUTPUT_SHA256,
        )
        self.assertEqual(
            sha256_file(B.DEFAULT_PUBLIC_OUTPUT),
            B.EXPECTED_PUBLIC_OUTPUT_SHA256,
        )

    def test_targeted_raw_copy_delta(self) -> None:
        predecessor = B.PREDECESSOR_PRIVATE_PATH.read_bytes().splitlines(
            keepends=True
        )
        current = B.DEFAULT_PRIVATE_OUTPUT.read_bytes().splitlines(
            keepends=True
        )
        self.assertEqual(len(predecessor), B.EXPECTED_ROWS)
        self.assertEqual(len(current), B.EXPECTED_ROWS)
        changed = [
            index
            for index, pair in enumerate(zip(predecessor, current))
            if pair[0] != pair[1]
        ]
        self.assertEqual(len(changed), B.EXPECTED_DECISIONS)
        self.assertEqual(
            len(current) - len(changed), B.EXPECTED_UNAFFECTED_ROWS
        )
        for index in changed:
            before = json.loads(predecessor[index].decode("utf-8"))
            after = json.loads(current[index].decode("utf-8"))
            self.assertEqual(before["resource"], "pk_msggame")
            self.assertEqual(after["resource"], "pk_msggame")
            self.assertEqual(before["coordinate"], after["coordinate"])
            self.assertEqual(after["runtime_review"], "verified")
            self.assertIn(B.UPDATE_ACTION_FIELD, after)

    def test_closure_action_partition(self) -> None:
        rows = [
            json.loads(line)
            for line in B.CLOSURE_DECISIONS_PATH.read_text(
                encoding="utf-8"
            ).splitlines()
            if line
        ]
        self.assertEqual(len(rows), B.EXPECTED_DECISIONS)
        self.assertEqual(
            Counter(row[B.UPDATE_ACTION_FIELD] for row in rows),
            Counter(B.EXPECTED_ACTION_COUNTS),
        )
        self.assertEqual(
            Counter(int(row["owner_chunk"]) for row in rows),
            Counter(B.EXPECTED_OWNER_CHUNK_COUNTS),
        )

    def test_public_counts_and_lineage(self) -> None:
        report = load_json(B.DEFAULT_PUBLIC_OUTPUT)
        self.assertEqual(
            report["inputs"]["predecessor_private_sha256"],
            B.EXPECTED_PREDECESSOR_PRIVATE_SHA256,
        )
        layer = report["selector292_consolidated"]
        self.assertEqual(layer["owner_decision_row_count"], 22)
        self.assertEqual(layer["updated_coordinate_count"], 22)
        self.assertEqual(layer["promotion_count"], 21)
        self.assertEqual(layer["verification_renewal_count"], 1)
        self.assertEqual(layer["source_only_action_count"], 0)
        self.assertEqual(report["result"]["runtime_review_pending"], 6_130)
        self.assertEqual(report["result"]["fully_candidate_eligible"], 46_673)
        self.assertEqual(report["result"]["promoted_total"], 30_204)
        self.assertEqual(
            report["result"]["pk_msggame_promotion_count"], 14_553
        )
        self.assertFalse(
            report["validation"]["full_integration_engine_invoked"]
        )

    def test_source_free_and_no_coordinates(self) -> None:
        cjk = re.compile(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]"
        )
        coordinate = re.compile(r"\b\d+:\d+(?::\d+){0,2}\b")
        for path in (BUILDER_PATH, SCRIPT, B.DEFAULT_PUBLIC_OUTPUT):
            content = path.read_text(encoding="utf-8")
            self.assertIsNone(cjk.search(content))
            self.assertIsNone(coordinate.search(content))
        public = B.DEFAULT_PUBLIC_OUTPUT.read_text(encoding="ascii")
        self.assertNotIn('"translation"', public)
        self.assertNotIn('"reviewed_translation"', public)

    def test_live_steam_unchanged(self) -> None:
        if B.BASE.LIVE_BASE_PATH.is_file():
            self.assertEqual(
                sha256_file(B.BASE.LIVE_BASE_PATH),
                B.BASE.EXPECTED_LIVE_BASE_SHA256,
            )
        if B.BASE.LIVE_PK_PATH.is_file():
            self.assertEqual(
                sha256_file(B.BASE.LIVE_PK_PATH),
                B.BASE.EXPECTED_LIVE_PK_SHA256,
            )
        self.assertFalse(
            load_json(B.DEFAULT_PUBLIC_OUTPUT)["steam_write_performed"]
        )


if __name__ == "__main__":
    unittest.main()
