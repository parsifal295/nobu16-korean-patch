from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_private_union_composite_wave64_v1.py"
SPEC = importlib.util.spec_from_file_location("pc_private_union_wave64_test", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import guard
    raise RuntimeError("cannot import W64 builder")
wave64 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave64
SPEC.loader.exec_module(wave64)


class PrivateUnionCompositeWave64Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave64.prepare(require_output_profiles=False)
        cls.w63_bundle = wave64.w63.prepare(require_output_profiles=True)

    def test_scope_and_title_hold_are_exact(self) -> None:
        self.assertEqual(len(wave64.REFLOW_TARGETS), 57)
        self.assertEqual(tuple(target.entry_id for target in wave64.REFLOW_TARGETS), wave64.EXPECTED_TARGET_IDS)
        self.assertIn(6523, wave64.EXPECTED_TARGET_IDS)
        self.assertNotIn(11000, wave64.EXPECTED_TARGET_IDS)
        self.assertEqual(
            {name: len(values) for name, values in self.bundle.event_classifications.items()},
            wave64.EXPECTED_EVENT_CLASSES,
        )
        self.assertEqual(len(self.bundle.event_rows), 57)

    def test_every_row_is_one_static_space_to_lf_reflow(self) -> None:
        _header, _raw, before = wave64.w60.parse_table("W63 event", self.w63_bundle.outputs[wave64.MSGEV])
        _header, _raw, after = wave64.w60.parse_table("W64 event", self.bundle.outputs[wave64.MSGEV])
        font = wave64.layout.load_font()
        by_id = {row["entry_id"]: row for row in self.bundle.event_rows}
        for target in wave64.REFLOW_TARGETS:
            with self.subTest(entry_id=target.entry_id):
                source = before.texts[target.entry_id]
                result = after.texts[target.entry_id]
                row = by_id[target.entry_id]
                self.assertEqual(wave64.manual_lf_count(source), 0)
                self.assertEqual(wave64.manual_lf_count(result), 1)
                self.assertTrue(wave64.layout.layout_equivalent(source, result))
                self.assertEqual(
                    wave64.static_signature(source, target.entry_id, "test source"),
                    wave64.static_signature(result, target.entry_id, "test target"),
                )
                self.assertEqual(wave64.layout.line_widths(source, font), (target.source_width_px,))
                self.assertEqual(wave64.layout.line_widths(result, font), target.target_line_widths_px)
                self.assertLessEqual(max(target.target_line_widths_px), wave64.layout.PK_MAX_LINE_PX)
                self.assertEqual(row["target_ko"], result)
                self.assertEqual(row["source_line_widths_px"], [target.source_width_px])
                self.assertEqual(row["target_line_widths_px"], list(target.target_line_widths_px))

    def test_w63_to_w64_changes_only_approved_event_rows(self) -> None:
        _header, _raw, before = wave64.w60.parse_table("W63 event", self.w63_bundle.outputs[wave64.MSGEV])
        _header, _raw, after = wave64.w60.parse_table("W64 event", self.bundle.outputs[wave64.MSGEV])
        changed = {index for index, value in enumerate(before.texts) if value != after.texts[index]}
        self.assertEqual(changed, set(wave64.EXPECTED_TARGET_IDS))
        self.assertEqual(changed, set(self.bundle.event_effective))

    def test_non_event_w63_components_are_byte_identical(self) -> None:
        for resource in (wave64.BASE, wave64.PK, wave64.MSGDATA):
            with self.subTest(resource=resource):
                self.assertEqual(self.bundle.outputs[resource], self.w63_bundle.outputs[resource])

    def test_w45_event_history_is_retained(self) -> None:
        w45 = wave64.w62.load_w45_backups()
        _header, _raw, before = wave64.w60.parse_table("W45 event", w45[wave64.MSGEV])
        _header, _raw, w63 = wave64.w60.parse_table("W63 event", self.w63_bundle.outputs[wave64.MSGEV])
        _header, _raw, w64 = wave64.w60.parse_table("W64 event", self.bundle.outputs[wave64.MSGEV])
        w63_changed = {index for index, value in enumerate(before.texts) if value != w63.texts[index]}
        w64_changed = {index for index, value in enumerate(before.texts) if value != w64.texts[index]}
        self.assertTrue(w63_changed.isdisjoint(wave64.EXPECTED_TARGET_IDS))
        self.assertEqual(w64_changed, w63_changed | set(wave64.EXPECTED_TARGET_IDS))

    def test_record_counts_and_candidate_policy(self) -> None:
        self.assertEqual(self.bundle.final_record_counts, wave64.EXPECTED_FINAL_RECORD_COUNTS)
        self.assertEqual(sum(self.bundle.final_record_counts.values()), wave64.EXPECTED_FINAL_TOTAL_RECORDS)
        policy = self.bundle.audit["source_policy"]
        self.assertFalse(policy["switch_read"])
        self.assertFalse(policy["steam_game_resource_written"])
        self.assertEqual(policy["steam_apply_or_transaction_capability"], "absent")
        self.assertFalse(self.bundle.manifest["steam_game_resource_written"])
        self.assertFalse(self.bundle.manifest["git_operation_performed"])
        self.assertFalse(self.bundle.manifest["release_published"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
