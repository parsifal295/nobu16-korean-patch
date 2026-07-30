#!/usr/bin/env python3
"""Bootstrap tests for the post-selector292 wave1 progress delta."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name(
    "build_progress_post_selector292_wave1_consolidated_delta_v1.py"
)
SPEC = importlib.util.spec_from_file_location(
    "post292_wave1_progress_tested", BUILDER_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(BUILDER_PATH)
B = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = B
SPEC.loader.exec_module(B)


def optional_bytes(path: Path) -> bytes | None:
    return path.read_bytes() if path.is_file() else None


class PostSelector292Wave1ProgressTests(unittest.TestCase):
    def test_frozen_predecessor_inputs(self) -> None:
        self.assertEqual(
            B.BASE.sha256_file(B.BASE_BUILDER_PATH),
            B.EXPECTED_BASE_BUILDER_SHA256,
        )
        self.assertEqual(
            B.BASE.sha256_file(B.DEFAULT_PREDECESSOR_PROGRESS),
            B.EXPECTED_PREDECESSOR_PROGRESS_SHA256,
        )
        self.assertEqual(B.EXPECTED_PREDECESSOR_PENDING, 6_130)
        self.assertEqual(B.EXPECTED_PREDECESSOR_ELIGIBLE, 46_673)
        self.assertEqual(B.EXPECTED_PREDECESSOR_PROMOTED_TOTAL, 30_204)
        self.assertEqual(B.EXPECTED_PREDECESSOR_PK_PROMOTIONS, 14_553)
        self.assertEqual(B.EXPECTED_PREDECESSOR_RETRANSLATED, 46_328)

    def test_wave_checkpoint_paths_are_reserved(self) -> None:
        self.assertEqual(
            B.CHECKPOINT_BUILDER_PATH.name,
            "build_runtime_vm_post_selector292_wave1_consolidated_"
            "checkpoint_v1.py",
        )
        self.assertEqual(
            B.CHECKPOINT_PRIVATE_PATH.name,
            "runtime_vm_integrated.post_selector292_wave1_consolidated_"
            "checkpoint.private.v1.jsonl",
        )
        self.assertEqual(
            B.CHECKPOINT_PUBLIC_PATH.name,
            "runtime_vm_integration.post_selector292_wave1_consolidated_"
            "checkpoint.source_free.v1.json",
        )
        self.assertEqual(
            B.CLOSURE_DECISIONS_PATH.name,
            "pk_dialogue_wave_post_selector292_consolidated_closure_"
            "decisions.private.v1.jsonl",
        )

    def test_frozen_progress_contract(self) -> None:
        self.assertTrue(B.pins_resolved())
        self.assertFalse(B.unresolved_checkpoint_pins())
        self.assertEqual(B.EXPECTED_DECISIONS, 46)
        self.assertEqual(B.EXPECTED_PROMOTIONS, 46)
        self.assertEqual(B.EXPECTED_RENEWALS, 0)
        self.assertEqual(B.EXPECTED_OVERRIDES, 29)
        self.assertEqual(B.EXPECTED_FINAL_PENDING, 6_084)
        self.assertEqual(B.EXPECTED_FINAL_ELIGIBLE, 46_719)
        self.assertEqual(B.EXPECTED_FINAL_PROMOTED_TOTAL, 30_250)
        self.assertEqual(B.EXPECTED_FINAL_PK_PROMOTIONS, 14_599)
        self.assertEqual(B.EXPECTED_FINAL_RETRANSLATED, 46_374)
        self.assertEqual(B.EXPECTED_TARGETED_AFFECTED_ROWS, 46)
        self.assertEqual(B.EXPECTED_UNAFFECTED_ROWS, 52_757)
        self.assertIsNotNone(B.EXPECTED_PROGRESS_OUTPUT_SHA256)

    def test_pin_loss_refuses_all_progress_writes(self) -> None:
        alias_before = optional_bytes(B.DEFAULT_PROGRESS_OUTPUT)
        immutable_before = optional_bytes(B.IMMUTABLE_PROGRESS_OUTPUT)
        original = B.EXPECTED_CHECKPOINT_PRIVATE_SHA256
        try:
            B.EXPECTED_CHECKPOINT_PRIVATE_SHA256 = None
            with self.assertRaisesRegex(
                RuntimeError,
                "post-selector292 wave1 progress input pins unresolved",
            ):
                B.main(["--write", "--bootstrap-output-pins"])
        finally:
            B.EXPECTED_CHECKPOINT_PRIVATE_SHA256 = original
        self.assertEqual(
            optional_bytes(B.DEFAULT_PROGRESS_OUTPUT),
            alias_before,
        )
        self.assertEqual(
            optional_bytes(B.IMMUTABLE_PROGRESS_OUTPUT),
            immutable_before,
        )

    def test_runtime_integration_alias_is_immutable(self) -> None:
        protected = B.WORKSTREAM / "runtime_vm_integration.source_free.v1.json"
        before = optional_bytes(protected)
        source = BUILDER_PATH.read_text(encoding="utf-8")
        self.assertNotIn(
            '"runtime_vm_integration.source_free.v1.json"',
            source,
        )
        self.assertEqual(B.main(["--check"]), 0)
        self.assertEqual(optional_bytes(protected), before)

    def test_predecessor_progress_contract(self) -> None:
        progress = json.loads(
            B.DEFAULT_PREDECESSOR_PROGRESS.read_text("ascii")
        )
        B.validate_baseline_progress(progress)
        integration = progress["runtime_vm_integration"]
        self.assertTrue(
            integration["selector292_consolidated_layer_included"]
        )

    def test_frozen_targeted_progress_delta(self) -> None:
        self.assertEqual(B.main(["--check"]), 0)
        progress = json.loads(B.IMMUTABLE_PROGRESS_OUTPUT.read_text("ascii"))
        totals = progress["totals"]
        scope = totals["scope_classification_counts"]
        integration = progress["runtime_vm_integration"]
        self.assertEqual(totals["runtime_review_pending"], 6_084)
        self.assertEqual(totals["fully_candidate_eligible"], 46_719)
        self.assertEqual(scope["retranslated"], 46_374)
        self.assertEqual(scope["confirmed_non_display"], 345)
        self.assertEqual(integration["promoted_total"], 30_250)
        self.assertTrue(
            integration["selector292_consolidated_layer_included"]
        )
        self.assertTrue(
            integration[
                "dialogue_wave_post_selector292_consolidated_layer_included"
            ]
        )
        delta = integration[
            "dialogue_wave_post_selector292_targeted_progress_delta"
        ]
        self.assertEqual(delta["promotion_count"], 46)
        self.assertFalse(delta["full_dialogue_rebuild_performed"])
        self.assertFalse(delta["steam_write_performed"])

    def test_outputs_are_named_progress_artifacts_only(self) -> None:
        self.assertEqual(
            B.DEFAULT_PROGRESS_OUTPUT.name,
            "progress.source_free.v1.json",
        )
        self.assertEqual(
            B.IMMUTABLE_PROGRESS_OUTPUT.name,
            "progress.post_selector292_wave1_consolidated.source_free.v1.json",
        )
        self.assertFalse(hasattr(B, "DEFAULT_STEAM_ROOT"))
        self.assertFalse(B.EXPECTED_FULL_DIALOGUE_REBUILD)

    def test_tracked_files_are_source_free(self) -> None:
        cjk = re.compile(
            r"[\u1100-\u11ff\u3040-\u30ff\u3130-\u318f"
            r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]"
        )
        for path in (BUILDER_PATH, SCRIPT):
            self.assertIsNone(cjk.search(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
