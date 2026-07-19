from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_private_union_composite_wave62_v1.py"
SPEC = importlib.util.spec_from_file_location("pc_private_union_wave62_test", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import guard
    raise RuntimeError("cannot import W62 builder")
wave62 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave62
SPEC.loader.exec_module(wave62)


class PrivateUnionCompositeWave62Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave62.prepare(require_output_profiles=False)
        cls.w61_bundle = wave62.load_w61_candidate()

    def test_target_scope_is_four_literal_only_records(self) -> None:
        self.assertEqual(len(wave62.TARGETS), 4)
        self.assertEqual(
            {target.coordinate for target in wave62.TARGETS},
            {(16, 3, 0), (16, 14, 0), (16, 19, 0), (16, 22, 0)},
        )
        self.assertEqual(
            {name: len(values) for name, values in self.bundle.classifications.items()},
            wave62.EXPECTED_CLASSIFICATIONS,
        )

    def test_overlay_changes_only_the_four_approved_base_literals(self) -> None:
        before = wave62.parse_base(self.w61_bundle[wave62.BASE], "W61 Base")
        after = wave62.parse_base(self.bundle.outputs[wave62.BASE], "W62 Base")
        wave62.w59.assert_same_literal_topology_and_skeleton("W61-to-W62 Base", before, after)
        before_records = wave62.w59.archive_records(before)
        after_records = wave62.w59.archive_records(after)
        before_texts = wave62.w59.literal_texts(before)
        after_texts = wave62.w59.literal_texts(after)
        self.assertEqual(
            {key for key in before_texts if before_texts[key] != after_texts[key]},
            set(self.bundle.effective),
        )
        self.assertEqual(
            {key for key in before_records if before_records[key].data != after_records[key].data},
            {(16, 3), (16, 14), (16, 19), (16, 22)},
        )

    def test_w61_non_base_components_are_byte_identical(self) -> None:
        for resource in (wave62.PK, wave62.MSGDATA, wave62.MSGEV):
            with self.subTest(resource=resource):
                if resource == wave62.MSGEV:
                    self.assertNotEqual(self.bundle.outputs[resource], self.w61_bundle[resource])
                else:
                    self.assertEqual(self.bundle.outputs[resource], self.w61_bundle[resource])

    def test_event_overlay_changes_only_the_twenty_approved_ids(self) -> None:
        _header, _raw, before = wave62.w60.parse_table("W61 event", self.w61_bundle[wave62.MSGEV])
        _header, _raw, after = wave62.w60.parse_table("W62 event", self.bundle.outputs[wave62.MSGEV])
        self.assertEqual(
            {index for index, value in enumerate(before.texts) if value != after.texts[index]},
            set(self.bundle.event_effective),
        )
        self.assertEqual(len(self.bundle.event_effective), 20)
        self.assertEqual(
            {name: len(values) for name, values in self.bundle.event_classifications.items()},
            wave62.EXPECTED_EVENT_CLASSIFICATIONS,
        )

    def test_profile_and_policy_contract(self) -> None:
        self.assertEqual(self.bundle.final_record_counts, wave62.EXPECTED_FINAL_RECORD_COUNTS)
        self.assertEqual(sum(self.bundle.final_record_counts.values()), wave62.EXPECTED_FINAL_TOTAL_RECORDS)
        policy = self.bundle.audit["source_policy"]
        self.assertFalse(policy["switch_read"])
        self.assertFalse(policy["steam_game_resource_written"])
        self.assertEqual(policy["steam_apply_or_transaction_capability"], "absent")
        self.assertFalse(self.bundle.manifest["steam_game_resource_written"])
        self.assertFalse(self.bundle.manifest["git_operation_performed"])
        self.assertFalse(self.bundle.manifest["release_published"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
