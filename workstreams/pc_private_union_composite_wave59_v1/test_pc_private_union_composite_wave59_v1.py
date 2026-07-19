from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_private_union_composite_wave59_v1.py"
SPEC = importlib.util.spec_from_file_location("pc_private_union_composite_wave59_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import guard
    raise RuntimeError("cannot import W59 builder")
wave59 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave59
SPEC.loader.exec_module(wave59)


class PrivateUnionCompositeWave59Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave59.prepare(require_output_profiles=True)
        cls.result = wave59.build_private_candidate()

    def test_component_pins_and_literal_delta_scope(self) -> None:
        self.assertEqual(
            {
                name: {relative: len(delta) for relative, delta in by_resource.items()}
                for name, by_resource in self.bundle.component_deltas.items()
            },
            {
                "b14_static_v1": {
                    wave59.BASE: 3,
                    wave59.PK: 7,
                },
                "b15_static_v2": {
                    wave59.BASE: 6,
                    wave59.PK: 4,
                },
                "b15_highrisk_static_v1": {
                    wave59.BASE: 1,
                    wave59.PK: 1,
                },
            },
        )
        self.assertEqual(
            {relative: len(delta) for relative, delta in self.bundle.merged.items()},
            {wave59.BASE: 10, wave59.PK: 12},
        )
        self.assertEqual(self.bundle.audit["component_literal_conflicts"], [])
        self.assertEqual(self.bundle.audit["component_literal_conflict_count"], 0)

    def test_only_approved_w58_literals_change_and_opaque_skeletons_survive(self) -> None:
        self.assertEqual(
            {relative: len(values) for relative, values in self.bundle.effective_overlays.items()},
            {wave59.BASE: 7, wave59.PK: 11},
        )
        self.assertEqual(
            {
                relative: set(classification["override"])
                for relative, classification in self.bundle.classifications.items()
            },
            {
                wave59.BASE: {(14, 32, 3), (14, 117, 3)},
                wave59.PK: {(14, 48, 3)},
            },
        )
        self.assertEqual(
            {
                relative: set(classification["already"])
                for relative, classification in self.bundle.classifications.items()
            },
            {
                wave59.BASE: {(14, 113, 1), (15, 1875, 1), (15, 1890, 1)},
                wave59.PK: {(14, 51, 1)},
            },
        )
        self.assertEqual(
            self.bundle.audit["w58_to_w59"],
            {
                wave59.BASE: {"record_count": 7, "literal_count": 7},
                wave59.PK: {"record_count": 11, "literal_count": 11},
            },
        )

    def test_final_profiles_and_private_candidate_scope(self) -> None:
        self.assertEqual(self.bundle.output_profiles, wave59.EXPECTED_FINAL_PROFILES)
        self.assertEqual(
            self.bundle.audit["final_record_counts"], wave59.EXPECTED_FINAL_RECORD_COUNTS
        )
        self.assertEqual(self.bundle.audit["final_total_records"], 396)
        self.assertEqual(
            self.bundle.outputs[wave59.MSGDATA],
            (wave59.W58_ROOT / wave59.MSGDATA).read_bytes(),
        )
        self.assertEqual(
            self.bundle.outputs[wave59.MSGEV],
            (wave59.W58_ROOT / wave59.MSGEV).read_bytes(),
        )
        self.assertEqual(self.result["candidate_only"], True)
        self.assertFalse(self.result["steam_game_resource_written"])
        self.assertFalse(self.result["git_operation_performed"])
        self.assertFalse(self.result["release_published"])
        self.assertEqual(
            self.result["candidate_root"],
            "tmp/pc_private_union_composite_wave59_v1/candidate",
        )

    def test_audit_declares_no_apply_capability(self) -> None:
        policy = self.bundle.audit["source_policy"]
        self.assertEqual(policy["platform"], "Steam PC direct W45 only")
        self.assertFalse(policy["switch_read"])
        self.assertFalse(policy["steam_game_resource_written"])
        self.assertEqual(policy["steam_apply_or_transaction_capability"], "absent")
        self.assertEqual(policy["git_operation_capability"], "absent")
        self.assertEqual(policy["release_capability"], "absent")


if __name__ == "__main__":
    unittest.main(verbosity=2)
