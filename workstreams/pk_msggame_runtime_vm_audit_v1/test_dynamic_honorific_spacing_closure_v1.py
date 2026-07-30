from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from argparse import Namespace
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
MODULE_PATH = SCRIPT.parent / "build_dynamic_honorific_spacing_closure_v1.py"


def load_module() -> Any:
    spec = importlib.util.spec_from_file_location(
        "dynamic_honorific_spacing_closure_test_subject",
        MODULE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


class DynamicHonorificSpacingClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.outputs = MODULE.build_outputs()
        (
            cls.decision_content,
            cls.base_overlay_content,
            cls.pk_overlay_content,
            cls.audit_content,
            cls.base_report_content,
            cls.pk_report_content,
            cls.audit,
            cls.bundle,
        ) = cls.outputs
        MODULE.validate_outputs(
            decision_content=cls.decision_content,
            base_overlay_content=cls.base_overlay_content,
            pk_overlay_content=cls.pk_overlay_content,
            audit_content=cls.audit_content,
            base_report_content=cls.base_report_content,
            pk_report_content=cls.pk_report_content,
            audit=cls.audit,
            bundle=cls.bundle,
        )

    def test_expected_funnel_and_candidate_hashes(self) -> None:
        scope = self.audit["scope"]
        guards = self.audit["guards"]
        self.assertEqual(scope["translation_override_rows"], 4)
        self.assertEqual(
            scope["pk_promotion_eligible_rows"],
            MODULE.EXPECTED_ELIGIBLE_ROWS,
        )
        self.assertEqual(
            scope["pk_promotion_eligible_roots"],
            MODULE.EXPECTED_ELIGIBLE_ROOTS,
        )
        self.assertEqual(
            scope["post_layer_pending_rows"],
            MODULE.EXPECTED_PENDING_AFTER,
        )
        self.assertEqual(
            guards["base_candidate_packed_sha256"],
            MODULE.EXPECTED_BASE_CANDIDATE_SHA256,
        )
        self.assertEqual(
            guards["pk_candidate_packed_sha256"],
            MODULE.EXPECTED_PK_CANDIDATE_SHA256,
        )
        self.assertEqual(
            guards["eligible_coordinate_sha256"],
            MODULE.EXPECTED_ELIGIBLE_COORDINATE_SHA256,
        )
        self.assertEqual(
            guards["eligible_root_sha256"],
            MODULE.EXPECTED_ELIGIBLE_ROOT_SHA256,
        )

    def test_resource_namespaced_action_classification(self) -> None:
        rows = {
            (str(row["resource"]), str(row["coordinate"])): row
            for row in self.bundle["updated_rows"]
        }
        base = rows[("base_msggame", "6:822:0")]
        pk = rows[("pk_msggame", "6:822:0")]
        self.assertEqual(
            base["runtime_vm_verification"]["action"],
            "verification_renewal",
        )
        self.assertEqual(
            pk["runtime_vm_verification"]["action"],
            "runtime_promotion",
        )
        self.assertNotIn(
            "pk_promoted_root_binding",
            base["runtime_vm_verification"],
        )
        self.assertIn(
            "pk_promoted_root_binding",
            pk["runtime_vm_verification"],
        )

    def test_exact_four_literal_owned_space_overrides(self) -> None:
        rows = {
            (str(row["resource"]), str(row["coordinate"])): row
            for row in self.bundle["updated_rows"]
        }
        flagged = {
            key
            for key, row in rows.items()
            if row.get("runtime_boundary_leading_space_inserted") is True
        }
        self.assertEqual(flagged, set(MODULE.TRANSLATION_OVERRIDES))
        for key in flagged:
            row = rows[key]
            self.assertEqual(row["translation"], " 공")
            self.assertEqual(
                row["runtime_vm_verification"]["action"],
                "translation_override",
            )
            self.assertTrue(
                row["honorific_spacing_evidence"][
                    "boundary_space_literal_owned"
                ]
            )

    def test_action_counts_and_overlay_privacy(self) -> None:
        actions = Counter(
            row["runtime_vm_verification"]["action"]
            for row in self.bundle["updated_rows"]
        )
        self.assertEqual(
            actions,
            {
                "translation_override": 4,
                "verification_renewal": 466,
                "runtime_promotion": 57,
            },
        )
        for content in (
            self.base_overlay_content,
            self.pk_overlay_content,
        ):
            for line in content.splitlines():
                row = json.loads(line)
                self.assertNotIn("translation", row)
                self.assertFalse(row["per_row_game_playback_required"])

    def test_public_outputs_are_source_free_and_steam_read_only(self) -> None:
        public = (
            self.audit_content
            + self.base_report_content
            + self.pk_report_content
        )
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
        self.assertFalse(self.audit["steam_write_performed"])
        self.assertFalse(self.bundle["base_report"]["steam_write_performed"])
        self.assertFalse(self.bundle["pk_report"]["steam_write_performed"])


class DynamicHonorificSpacingPathSafetyTests(unittest.TestCase):
    def test_cli_output_paths_cannot_target_steam(self) -> None:
        args = Namespace(
            decision_output=MODULE.DEFAULT_DECISION_OUTPUT,
            base_overlay_output=MODULE.DEFAULT_BASE_OVERLAY_OUTPUT,
            pk_overlay_output=MODULE.DEFAULT_PK_OVERLAY_OUTPUT,
            audit_output=MODULE.LIVE_STEAM_PK,
            base_report_output=MODULE.DEFAULT_BASE_REPORT_OUTPUT,
            pk_report_output=MODULE.DEFAULT_PK_REPORT_OUTPUT,
        )
        with self.assertRaises(MODULE.HonorificSpacingError):
            MODULE.validate_output_paths(args)


if __name__ == "__main__":
    unittest.main()
