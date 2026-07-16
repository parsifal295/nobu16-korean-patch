from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("switch_v2_image_delta_audit", WORKSTREAM / "build_switch_v2_image_delta_audit_v1.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class SwitchV2ImageDeltaAuditTests(unittest.TestCase):
    def test_expected_release_delta_contract(self) -> None:
        self.assertEqual(MODULE.EXPECTED_DELTAS["v20_to_v21"], (8,))
        self.assertEqual(MODULE.EXPECTED_DELTAS["v21_to_v22"], (5, 8, 12, 13, 16, 24))
        self.assertEqual(MODULE.EXPECTED_DELTAS["v22_to_v23"], (6, 7))
        self.assertEqual(MODULE.EXPECTED_DELTAS["v23_to_v24"], (6, 7))

    def test_target_set_includes_wheel_and_all_v22_image_bundles(self) -> None:
        self.assertEqual(set(MODULE.TARGETS), {5, 8, 12, 13, 16, 24})
        self.assertEqual(MODULE.TARGETS[8]["priority"], "P0")
        self.assertEqual(MODULE.TARGETS[8]["status"], "confirmed")
        self.assertEqual(MODULE.V21_TO_V22_CHANGED_TEXTURES[5], (1,))
        self.assertEqual(MODULE.V21_TO_V22_CHANGED_TEXTURES[13], tuple(range(48, 57)))

    def test_button_atlas_is_next_after_wheel(self) -> None:
        self.assertEqual(MODULE.TARGETS[5]["priority"], "P1")
        self.assertIn("system/navigation", MODULE.TARGETS[5]["family"])
        self.assertEqual(MODULE.TARGETS[12]["family"], "battle military-assessment overlay")
        self.assertEqual(MODULE.TARGETS[13]["family"], "battle-start banner family")
        self.assertEqual(MODULE.TARGETS[16]["family"], "tutorial flow diagram")
        self.assertEqual(MODULE.TARGETS[24]["priority"], "P2")

    def test_audit_is_source_free_and_self_validating(self) -> None:
        audit = json.loads((WORKSTREAM / "audit.v1.json").read_text(encoding="utf-8"))
        MODULE.verify_audit(audit)
        guarantees = audit["source_free_guarantees"]
        self.assertTrue(guarantees["metadata_only"])
        self.assertFalse(guarantees["committed_switch_payload_bytes"])

    def test_no_preview_output_may_escape_tmp(self) -> None:
        self.assertTrue(MODULE.is_within(MODULE.DEFAULT_PREVIEW_ROOT, MODULE.TMP_ROOT))
        self.assertFalse(MODULE.is_within(WORKSTREAM, MODULE.TMP_ROOT))


if __name__ == "__main__":
    unittest.main()
