from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
MODULE_PATH = (
    SCRIPT.parent
    / "build_pk_msggame_pending_cross_resource_exact_closure_v1.py"
)


def load_module() -> object:
    spec = importlib.util.spec_from_file_location(
        "pk_pending_cross_resource_exact_closure_test_subject",
        MODULE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class PendingCrossResourceExactClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.outputs = MODULE.build_outputs()
        (
            cls.audit_content,
            cls.private_content,
            cls.promotion_content,
            cls.audit,
            cls.promotion,
            cls.context,
        ) = cls.outputs

    def test_expected_funnel_and_universes(self) -> None:
        scope = self.audit["scope"]
        self.assertEqual(
            scope["local_exact_closure_match_rows"],
            MODULE.EXPECTED_LOCAL_MATCH_ROWS,
        )
        self.assertEqual(
            scope["target_pk_guard_failed_rows"],
            MODULE.EXPECTED_TARGET_GUARD_FAILED_ROWS,
        )
        self.assertEqual(
            scope["promotion_eligible_rows"],
            MODULE.EXPECTED_ELIGIBLE_ROWS,
        )
        self.assertEqual(
            scope["promotion_eligible_roots"],
            MODULE.EXPECTED_ELIGIBLE_ROOTS,
        )
        self.assertEqual(
            self.audit["guards"]["eligible_coordinate_universe_sha256"],
            MODULE.EXPECTED_ELIGIBLE_COORDINATE_SHA256,
        )
        self.assertEqual(
            self.audit["guards"]["eligible_record_universe_sha256"],
            MODULE.EXPECTED_ELIGIBLE_RECORD_SHA256,
        )
        self.assertEqual(
            self.audit["guards"]["independent_analysis_manifest_sha256"],
            MODULE.EXPECTED_ANALYSIS_MANIFEST_SHA256,
        )

    def test_overlay_is_atomic_and_hash_only(self) -> None:
        rows = [
            json.loads(line)
            for line in self.private_content.splitlines()
            if line
        ]
        self.assertEqual(len(rows), MODULE.EXPECTED_ELIGIBLE_ROWS)
        self.assertEqual(
            [row["coordinate"] for row in rows],
            sorted(
                (row["coordinate"] for row in rows),
                key=MODULE.coordinate_sort_key,
            ),
        )
        for row in rows:
            self.assertEqual(row["schema"], MODULE.OVERLAY_ROW_SCHEMA)
            self.assertEqual(row["method"], MODULE.METHOD)
            self.assertEqual(row["status"], "verified")
            self.assertFalse(row["base_runtime_proof_inherited"])
            self.assertFalse(row["per_row_game_playback_required"])
            self.assertEqual(
                row["layout_transition"],
                {
                    "from": row["layout_review_binding"]["status"],
                    "to": "runtime_verified",
                },
            )
            binding = row["cross_resource_closure_binding"]
            self.assertTrue(binding["donors"])
            self.assertEqual(binding["pk_target_guard"]["failure_codes"], [])

    def test_public_outputs_are_source_free_and_steam_read_only(self) -> None:
        public = self.audit_content + self.promotion_content
        self.assertIsNone(
            re.search(
                r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff"
                r"\uac00-\ud7af]",
                public,
            )
        )
        self.assertIsNone(
            re.search(
                r'"(?:translation|source|source_text|dialogue_text)"\s*:',
                public,
            )
        )
        self.assertFalse(self.audit["promotion"]["steam_write_performed"])
        self.assertFalse(self.promotion["steam_write_performed"])
        self.assertEqual(
            self.context["steam_hash_before"],
            self.context["steam_hash_after"],
        )
        policy = self.audit["proof_policy"]
        self.assertFalse(policy["absolute_msggame_width_gate_used"])
        self.assertFalse(policy["pk_msgev_912px_rule_used"])

    def test_private_artifact_is_ignored_below_tmp(self) -> None:
        private_path = MODULE.DEFAULT_PRIVATE_OUTPUT
        self.assertTrue(private_path.is_file())
        self.assertIn(
            MODULE.DIALOGUE_TMP.resolve(strict=False),
            private_path.resolve(strict=False).parents,
        )


if __name__ == "__main__":
    unittest.main()
