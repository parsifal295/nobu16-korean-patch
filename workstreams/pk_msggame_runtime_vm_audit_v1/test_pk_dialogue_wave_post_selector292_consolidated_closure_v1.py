#!/usr/bin/env python3
"""Regression checks for the frozen post-selector292 dialogue-wave closure."""

from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name(
    "build_pk_dialogue_wave_post_selector292_consolidated_closure_v1.py"
)
SPEC = importlib.util.spec_from_file_location(
    "post_selector292_dialogue_wave_closure_tested",
    BUILDER_PATH,
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {BUILDER_PATH}")
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class PostSelector292DialogueWaveClosureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.outputs = BUILDER.build_outputs()
        cls.coverage = json.loads(
            cls.outputs[BUILDER.PUBLIC_COVERAGE_OUTPUT].decode("utf-8")
        )
        cls.promotion = json.loads(
            cls.outputs[BUILDER.PUBLIC_PROMOTION_OUTPUT].decode("utf-8")
        )
        cls.evidence = json.loads(
            cls.outputs[BUILDER.PRIVATE_EVIDENCE_OUTPUT].decode("utf-8")
        )
        cls.decisions = [
            json.loads(line)
            for line in cls.outputs[BUILDER.PRIVATE_DECISIONS_OUTPUT]
            .decode("utf-8")
            .splitlines()
            if line
        ]

    def test_frozen_counts_and_actions(self) -> None:
        result = self.promotion["result"]
        self.assertEqual(BUILDER.SELECTORS, (286, 190, 736))
        self.assertEqual(
            (
                BUILDER.EXPECTED_DECISION_ROWS,
                BUILDER.EXPECTED_DECISION_ROOTS,
                BUILDER.EXPECTED_PROMOTIONS,
                BUILDER.EXPECTED_RENEWALS,
                BUILDER.EXPECTED_OVERRIDES,
                BUILDER.EXPECTED_PENDING_BEFORE,
                BUILDER.EXPECTED_PENDING_AFTER,
            ),
            (46, 15, 46, 0, 29, 6_130, 6_084),
        )
        self.assertEqual(
            BUILDER.EXPECTED_ACTION_COUNTS,
            {
                "runtime_promotion": 17,
                "translation_override_and_runtime_promotion": 29,
            },
        )
        self.assertEqual(result["action_counts"], BUILDER.EXPECTED_ACTION_COUNTS)
        self.assertEqual(result["decision_rows"], BUILDER.EXPECTED_DECISION_ROWS)
        self.assertEqual(result["promotions"], BUILDER.EXPECTED_PROMOTIONS)
        self.assertEqual(result["renewals"], BUILDER.EXPECTED_RENEWALS)
        self.assertEqual(result["overrides"], BUILDER.EXPECTED_OVERRIDES)
        self.assertEqual(result["source_only_actions"], 0)
        self.assertEqual(
            Counter(
                row["post_selector292_wave1_update_action"]
                for row in self.decisions
            ),
            Counter(BUILDER.EXPECTED_ACTION_COUNTS),
        )

    def test_all_input_and_output_pins_are_frozen(self) -> None:
        self.assertTrue(BUILDER.EXPECTED_SCAFFOLD_SHA256)
        self.assertTrue(BUILDER.EXPECTED_OFFICIAL_CANDIDATE_SHA256)
        self.assertTrue(BUILDER.EXPECTED_OFFICIAL_PUBLIC_CHECKPOINT_SHA256)
        self.assertTrue(BUILDER.EXPECTED_INPUT_SHA256)
        self.assertTrue(BUILDER.EXPECTED_OUTPUT_SHA256)
        self.assertTrue(all(
            isinstance(value, str) and re.fullmatch(r"[0-9A-F]{64}", value)
            for value in BUILDER.EXPECTED_INPUT_SHA256.values()
        ))
        self.assertTrue(all(
            isinstance(value, str) and re.fullmatch(r"[0-9A-F]{64}", value)
            for value in BUILDER.EXPECTED_OUTPUT_SHA256.values()
        ))

    def test_output_paths_and_bytes_are_exact(self) -> None:
        expected = {
            BUILDER.PRIVATE_DECISIONS_OUTPUT: "private_decisions",
            BUILDER.PRIVATE_EVIDENCE_OUTPUT: "private_evidence",
            BUILDER.PUBLIC_COVERAGE_OUTPUT: "public_coverage",
            BUILDER.PUBLIC_PROMOTION_OUTPUT: "public_promotion",
        }
        self.assertEqual(set(self.outputs), set(expected))
        self.assertEqual(
            BUILDER.PRIVATE_DECISIONS_OUTPUT.parent,
            BUILDER.SEMANTIC_TMP,
        )
        self.assertEqual(
            BUILDER.PRIVATE_EVIDENCE_OUTPUT.parent,
            BUILDER.DIALOGUE_TMP,
        )
        self.assertTrue(all(
            path.parent == BUILDER.PUBLIC_DIR
            for path in (
                BUILDER.PUBLIC_COVERAGE_OUTPUT,
                BUILDER.PUBLIC_PROMOTION_OUTPUT,
            )
        ))
        for path, label in expected.items():
            self.assertTrue(path.is_file(), path)
            self.assertEqual(path.read_bytes(), self.outputs[path])
            self.assertEqual(
                BUILDER.BASE.sha256_bytes(self.outputs[path]),
                BUILDER.EXPECTED_OUTPUT_SHA256[label],
            )
        self.assertNotIn(
            BUILDER.PUBLIC_DIR / "runtime_vm_integration.source_free.v1.json",
            self.outputs,
        )

    def test_public_outputs_are_source_free(self) -> None:
        combined = (
            self.outputs[BUILDER.PUBLIC_COVERAGE_OUTPUT]
            + self.outputs[BUILDER.PUBLIC_PROMOTION_OUTPUT]
        ).decode("utf-8")
        self.assertIsNone(re.search(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]",
            combined,
        ))
        self.assertIsNone(
            re.search(r"\b\d+:\d+(?::\d+){0,2}\b", combined)
        )
        self.assertNotIn('"translation":', combined)
        self.assertNotIn('"reviewed_translation":', combined)
        BUILDER.BASE.assert_source_free(self.coverage)
        BUILDER.BASE.assert_source_free(self.promotion)

    def test_no_steam_write_or_full_rebuild(self) -> None:
        self.assertFalse(self.coverage["steam_write_performed"])
        self.assertFalse(self.promotion["steam_write_performed"])
        self.assertFalse(
            self.coverage["proof"]["full_dialogue_rebuild_performed"]
        )
        self.assertFalse(
            self.coverage["privacy"]["shared_integration_mutated"]
        )
        self.assertTrue(
            self.coverage["proof"]["terminal_21_records_read_only"]
        )
        self.assertEqual(self.coverage["result"]["source_only_actions"], 0)
        self.assertEqual(
            self.evidence["source_only_runtime_delta_proof"]["actions"],
            0,
        )

    def test_builder_check_subprocess_passes(self) -> None:
        environment = os.environ.copy()
        environment["PYTHONUTF8"] = "1"
        result = subprocess.run(
            [sys.executable, str(BUILDER_PATH), "--check"],
            cwd=BUILDER.REPO,
            env=environment,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        summary = json.loads(result.stdout.strip().splitlines()[-1])
        self.assertEqual(summary["status"], "PASS")
        self.assertFalse(summary["steam_write_performed"])
        self.assertEqual(summary["decision_rows"], 46)
        self.assertEqual(summary["promotions"], 46)


if __name__ == "__main__":
    unittest.main()
