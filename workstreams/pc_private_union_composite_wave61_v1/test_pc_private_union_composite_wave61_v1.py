from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_private_union_composite_wave61_v1.py"
SPEC = importlib.util.spec_from_file_location("pc_private_union_wave61_test", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import guard
    raise RuntimeError("cannot import W61 builder")
wave61 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave61
SPEC.loader.exec_module(wave61)


class PrivateUnionCompositeWave61Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave61.prepare(require_output_profiles=True)
        cls.w60_bundle = wave61.w60.prepare(require_output_profiles=True)

    def test_direct_audit_scope_is_exact_and_holds_are_excluded(self) -> None:
        self.assertEqual(len(wave61.B06_TARGETS), 27)
        self.assertEqual(len(wave61.B09_TARGETS), 54)
        self.assertEqual(len(wave61.TARGETS), 81)
        self.assertNotIn(
            (6, 2257, 0),
            {target.coordinate for target in wave61.B06_TARGETS if target.resource == wave61.PK},
        )
        b09_coordinates = {(target.resource, target.coordinate) for target in wave61.B09_TARGETS}
        self.assertNotIn((wave61.BASE, (9, 1253, 0)), b09_coordinates)
        self.assertNotIn((wave61.PK, (9, 1327, 0)), b09_coordinates)
        self.assertNotIn((wave61.BASE, (9, 1061, 0)), b09_coordinates)
        self.assertNotIn((wave61.PK, (9, 3867, 1)), b09_coordinates)

    def test_classification_counts_profiles_and_total_scope_are_pinned(self) -> None:
        counts = {
            resource: {
                audit: {name: len(values[name]) for name in ("fresh", "already", "override")}
                for audit, values in self.bundle.classifications[resource].items()
            }
            for resource in wave61.MSGGAME_RESOURCES
        }
        self.assertEqual(counts, wave61.EXPECTED_CLASS_COUNTS)
        self.assertEqual(self.bundle.profiles, wave61.EXPECTED_FINAL_PROFILES)
        self.assertEqual(self.bundle.final_record_counts, wave61.EXPECTED_FINAL_RECORD_COUNTS)
        self.assertEqual(sum(self.bundle.final_record_counts.values()), 496)
        self.assertEqual(
            {resource: len(self.bundle.effective[resource]) for resource in wave61.MSGGAME_RESOURCES},
            {wave61.BASE: 19, wave61.PK: 35},
        )

    def test_overlay_changes_only_approved_w60_literals(self) -> None:
        for resource in wave61.MSGGAME_RESOURCES:
            with self.subTest(resource=resource):
                before = wave61.parse_w60(resource, self.w60_bundle.outputs[resource])
                after = wave61.parse_w60(resource, self.bundle.outputs[resource])
                wave61.w59.assert_same_literal_topology_and_skeleton(
                    f"W60-to-W61 {resource}", before, after
                )
                before_records = wave61.w59.archive_records(before)
                after_records = wave61.w59.archive_records(after)
                before_texts = wave61.w59.literal_texts(before)
                after_texts = wave61.w59.literal_texts(after)
                expected_literals = set(self.bundle.effective[resource])
                expected_records = {(block, record) for block, record, _literal in expected_literals}
                self.assertEqual(
                    {key for key in before_records if before_records[key].data != after_records[key].data},
                    expected_records,
                )
                self.assertEqual(
                    {key for key in before_texts if before_texts[key] != after_texts[key]},
                    expected_literals,
                )
                for coordinate, target in self.bundle.effective[resource].items():
                    self.assertEqual(after_texts[coordinate], target)

    def test_w60_event_and_data_components_are_preserved(self) -> None:
        self.assertEqual(self.bundle.outputs[wave61.MSGDATA], self.w60_bundle.outputs[wave61.MSGDATA])
        self.assertEqual(self.bundle.outputs[wave61.MSGEV], self.w60_bundle.outputs[wave61.MSGEV])

    def test_private_candidate_policy(self) -> None:
        self.assertEqual(wave61.require_private(wave61.CANDIDATE_ROOT).parent, wave61.TMP_ROOT)
        policy = self.bundle.audit["source_policy"]
        self.assertFalse(policy["switch_read"])
        self.assertFalse(policy["steam_game_resource_written"])
        self.assertEqual(policy["steam_apply_or_transaction_capability"], "absent")
        self.assertFalse(self.bundle.manifest["steam_game_resource_written"])
        self.assertFalse(self.bundle.manifest["git_operation_performed"])
        self.assertFalse(self.bundle.manifest["release_published"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
