from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_private_union_composite_wave63_v1.py"
SPEC = importlib.util.spec_from_file_location("pc_private_union_wave63_test", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import guard
    raise RuntimeError("cannot import W63 builder")
wave63 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave63
SPEC.loader.exec_module(wave63)


class PrivateUnionCompositeWave63Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave63.prepare(require_output_profiles=False)
        cls.w62_bundle = wave63.w62.prepare(require_output_profiles=True)

    def test_target_scope_and_classifications_are_exact(self) -> None:
        self.assertEqual(len(wave63.DIALOGUE_TARGETS), 10)
        self.assertEqual(len(wave63.EVENT_TARGETS), 4)
        self.assertEqual(
            {
                resource: sum(target.resource == resource for target in wave63.DIALOGUE_TARGETS)
                for resource in (wave63.BASE, wave63.PK)
            },
            {wave63.BASE: 1, wave63.PK: 9},
        )
        self.assertEqual(
            {name: len(values) for name, values in self.bundle.dialogue_classifications.items()},
            wave63.EXPECTED_DIALOGUE_CLASSES,
        )
        self.assertEqual(
            {name: len(values) for name, values in self.bundle.event_classifications.items()},
            wave63.EXPECTED_EVENT_CLASSES,
        )

    def test_overlay_changes_only_approved_w62_dialogue_literals(self) -> None:
        expected_records = {
            wave63.BASE: {(9, 3622)},
            wave63.PK: {(6, value) for value in (1230, 1231, 1232, 1234, 1235, 1236, 1237, 1238)}
            | {(9, 3867)},
        }
        for resource in (wave63.BASE, wave63.PK):
            with self.subTest(resource=resource):
                before = wave63.parse_msggame(self.w62_bundle.outputs[resource], f"W62 {resource}")
                after = wave63.parse_msggame(self.bundle.outputs[resource], f"W63 {resource}")
                wave63.w59.assert_same_literal_topology_and_skeleton(f"W62-to-W63 {resource}", before, after)
                before_records = wave63.w59.archive_records(before)
                after_records = wave63.w59.archive_records(after)
                before_texts = wave63.w59.literal_texts(before)
                after_texts = wave63.w59.literal_texts(after)
                expected_literals = {
                    coordinate[1:]
                    for coordinate in self.bundle.dialogue_effective
                    if coordinate[0] == resource
                }
                self.assertEqual(
                    {key for key in before_texts if before_texts[key] != after_texts[key]},
                    expected_literals,
                )
                self.assertEqual(
                    {key for key in before_records if before_records[key].data != after_records[key].data},
                    expected_records[resource],
                )

    def test_event_scope_tag_structure_and_widths_are_pinned(self) -> None:
        _header, _raw, before = wave63.w60.parse_table("W62 event", self.w62_bundle.outputs[wave63.MSGEV])
        _header, _raw, after = wave63.w60.parse_table("W63 event", self.bundle.outputs[wave63.MSGEV])
        self.assertEqual(
            {index for index, value in enumerate(before.texts) if value != after.texts[index]},
            set(self.bundle.event_effective),
        )
        self.assertEqual(
            self.bundle.event_line_widths,
            {target.entry_id: target.expected_line_widths for target in wave63.EVENT_TARGETS},
        )

    def test_other_w62_components_are_byte_identical(self) -> None:
        for resource in (wave63.MSGDATA,):
            with self.subTest(resource=resource):
                self.assertEqual(self.bundle.outputs[resource], self.w62_bundle.outputs[resource])

    def test_record_counts_and_candidate_policy(self) -> None:
        self.assertEqual(self.bundle.final_record_counts, wave63.EXPECTED_FINAL_RECORD_COUNTS)
        self.assertEqual(sum(self.bundle.final_record_counts.values()), wave63.EXPECTED_FINAL_TOTAL_RECORDS)
        policy = self.bundle.audit["source_policy"]
        self.assertFalse(policy["switch_read"])
        self.assertFalse(policy["steam_game_resource_written"])
        self.assertEqual(policy["steam_apply_or_transaction_capability"], "absent")
        self.assertFalse(self.bundle.manifest["steam_game_resource_written"])
        self.assertFalse(self.bundle.manifest["git_operation_performed"])
        self.assertFalse(self.bundle.manifest["release_published"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
