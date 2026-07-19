from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_private_union_composite_wave60_v1.py"
SPEC = importlib.util.spec_from_file_location("pc_private_union_wave60_test", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import guard
    raise RuntimeError("cannot import W60 builder")
wave60 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave60
SPEC.loader.exec_module(wave60)


class PrivateUnionCompositeWave60Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave60.prepare(require_output_profiles=True)
        cls.w59 = wave60.load_w59()
        cls.w45 = wave60.w59.load_w45_sources()

    def test_exact_component_classes_and_final_counts(self) -> None:
        self.assertEqual(
            {relative: len(values) for relative, values in self.bundle.b17_deltas.items()},
            {wave60.BASE: 4, wave60.PK: 40},
        )
        self.assertEqual(tuple(sorted(self.bundle.event_deltas)), wave60.BATCH_D_IDS)
        self.assertEqual(self.bundle.b17_classes, wave60.EXPECTED_B17_CLASSES)
        self.assertEqual(self.bundle.final_record_counts, wave60.EXPECTED_FINAL_RECORD_COUNTS)
        self.assertEqual(sum(self.bundle.final_record_counts.values()), 445)
        self.assertEqual(self.bundle.profiles, wave60.EXPECTED_FINAL_PROFILES)

    def test_b17_overlay_changes_only_effective_w59_literals(self) -> None:
        for relative in wave60.MSGGAME_RESOURCES:
            with self.subTest(resource=relative):
                before = wave60.w59.assert_archive_parse_roundtrip(
                    f"W59 {relative}", self.w59[relative]
                )
                after = wave60.w59.assert_archive_parse_roundtrip(
                    f"W60 {relative}", self.bundle.outputs[relative]
                )
                wave60.w59.assert_same_literal_topology_and_skeleton(
                    f"W59-to-W60 {relative}", before, after
                )
                before_records = wave60.w59.archive_records(before)
                after_records = wave60.w59.archive_records(after)
                before_texts = wave60.w59.literal_texts(before)
                after_texts = wave60.w59.literal_texts(after)
                expected_literals = set(self.bundle.b17_effective[relative])
                expected_records = {
                    (block_id, record_id)
                    for block_id, record_id, _literal_id in expected_literals
                }
                self.assertEqual(
                    {key for key in before_records if before_records[key].data != after_records[key].data},
                    expected_records,
                )
                self.assertEqual(
                    {key for key in before_texts if before_texts[key] != after_texts[key]},
                    expected_literals,
                )
                for coordinate, target in self.bundle.b17_effective[relative].items():
                    self.assertEqual(after_texts[coordinate], target)

    def test_event_overlay_changes_only_batch_d_entries(self) -> None:
        _header, _raw, before = wave60.parse_table("W59 event", self.w59[wave60.MSGEV])
        _header, _raw, after = wave60.parse_table("W60 event", self.bundle.outputs[wave60.MSGEV])
        self.assertEqual(
            {index for index, value in enumerate(before.texts) if value != after.texts[index]},
            set(wave60.BATCH_D_IDS),
        )
        self.assertEqual(after.texts[4999], before.texts[4999])
        for entry_id, target in self.bundle.event_deltas.items():
            self.assertEqual(after.texts[entry_id], target)
            self.assertEqual(before.texts[entry_id].count("\n"), 0)
            self.assertEqual(target.count("\n"), 1)

    def test_private_candidate_policy(self) -> None:
        self.assertEqual(wave60.candidate_root().parent, wave60.TMP_ROOT)
        policy = self.bundle.audit["source_policy"]
        self.assertFalse(policy["switch_read"])
        self.assertFalse(policy["steam_game_resource_written"])
        self.assertEqual(policy["steam_apply_or_transaction_capability"], "absent")
        self.assertFalse(self.bundle.manifest["steam_game_resource_written"])
        self.assertFalse(self.bundle.manifest["git_operation_performed"])
        self.assertFalse(self.bundle.manifest["release_published"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
