from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_text_quality_wave34_strict_bundle_v1.py"
SPEC = importlib.util.spec_from_file_location("wave34_bundle_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot import Wave 34 bundle builder")
wave34 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave34
SPEC.loader.exec_module(wave34)


class Wave34BundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave34.prepare_candidate()

    def test_exact_composed_scope(self) -> None:
        changed = self.bundle.audit["changed"]
        self.assertEqual(len(changed["MSG/JP/ev_strdata.bin"]), 17)
        self.assertEqual(len(changed["MSG_PK/JP/msgev.bin"]), 17)
        self.assertEqual(len(changed["MSG_PK/JP/msggame.bin"]), 16)
        self.assertEqual(self.bundle.audit["changed_event_cell_count"], 34)
        self.assertEqual(self.bundle.audit["changed_total_count"], 50)

    def test_all_profiles_are_pinned(self) -> None:
        for relative, spec in wave34.RESOURCE_SPECS.items():
            with self.subTest(resource=relative):
                self.assertEqual(len(self.bundle.files[relative]), spec["output_size"])
                self.assertEqual(wave34.sha256_bytes(self.bundle.files[relative]), spec["output_sha256"])

    def test_component_policy_and_base_qa_hold(self) -> None:
        policy = self.bundle.audit["source_policy"]
        self.assertTrue(policy["component_pc_jp_en_sc_tc_only"])
        self.assertFalse(policy["switch_korean_read"])
        self.assertEqual(self.bundle.audit["base_real_game_qa_required_ids"], [6772, 6941, 8776, 8803, 8947, 9292])
        self.assertTrue(all(value for value in self.bundle.audit["component_audit_sha256"].values()))

    def test_private_output_guard(self) -> None:
        with self.assertRaises(wave34.Wave34Error):
            wave34.require_private(wave34.REPO, "repository root")


if __name__ == "__main__":
    unittest.main(verbosity=2)
