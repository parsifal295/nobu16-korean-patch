from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_private_union_composite_wave65_v1.py"
SPEC = importlib.util.spec_from_file_location("pc_private_union_wave65_test", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import guard
    raise RuntimeError("cannot import W65 builder")
wave65 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave65
SPEC.loader.exec_module(wave65)


class PrivateUnionCompositeWave65Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave65.prepare(require_output_profiles=False)
        cls.w64_bundle = wave65.w64.prepare(require_output_profiles=True)

    def test_scope_is_exact_and_direct_pc_jp_backed(self) -> None:
        self.assertEqual(len(wave65.TITLE_TARGETS), 4)
        self.assertEqual(
            tuple(target.coordinate for target in wave65.TITLE_TARGETS),
            wave65.EXPECTED_TARGET_COORDINATES,
        )
        self.assertEqual(
            {name: len(values) for name, values in self.bundle.title_classifications.items()},
            wave65.EXPECTED_TITLE_CLASSES,
        )
        self.assertEqual(len(self.bundle.title_rows), 4)
        self.assertEqual({row["direct_pc_jp"] for row in self.bundle.title_rows}, {"内府"})

    def test_every_replacement_preserves_controls_and_width(self) -> None:
        before = wave65.parse_msggame(self.w64_bundle.outputs[wave65.PK], "W64 PK")
        after = wave65.parse_msggame(self.bundle.outputs[wave65.PK], "W65 PK")
        font = wave65.w64.layout.load_font()
        rows = {row["coordinate"]: row for row in self.bundle.title_rows}
        for target in wave65.TITLE_TARGETS:
            with self.subTest(coordinate=target.coordinate):
                source = wave65.literal_at(before, target.coordinate, "W64 PK")
                result = wave65.literal_at(after, target.coordinate, "W65 PK")
                self.assertEqual(source, target.current_ko)
                self.assertEqual(result, target.target_ko)
                self.assertEqual(wave65.w61.literal_signature(source), wave65.w61.literal_signature(result))
                self.assertEqual(wave65.w64.layout.line_widths(source, font), target.expected_widths_px)
                self.assertEqual(wave65.w64.layout.line_widths(result, font), target.expected_widths_px)
                self.assertEqual(rows[target.coordinate_text]["target_ko"], result)

    def test_w64_to_w65_changes_only_approved_pk_literals(self) -> None:
        before = wave65.parse_msggame(self.w64_bundle.outputs[wave65.PK], "W64 PK")
        after = wave65.parse_msggame(self.bundle.outputs[wave65.PK], "W65 PK")
        before_literals = wave65.w63.w59.literal_texts(before)
        after_literals = wave65.w63.w59.literal_texts(after)
        changed = {coordinate for coordinate in before_literals if before_literals[coordinate] != after_literals[coordinate]}
        self.assertEqual(changed, set(wave65.EXPECTED_TARGET_COORDINATES))
        self.assertEqual(changed, set(self.bundle.title_effective))
        for resource in (wave65.BASE, wave65.MSGDATA, wave65.MSGEV):
            with self.subTest(resource=resource):
                self.assertEqual(self.bundle.outputs[resource], self.w64_bundle.outputs[resource])

    def test_w45_history_and_final_counts_are_retained(self) -> None:
        w45 = wave65.w62.load_w45_backups()
        before = wave65.parse_msggame(w45[wave65.PK], "W45 PK")
        w64 = wave65.parse_msggame(self.w64_bundle.outputs[wave65.PK], "W64 PK")
        w65 = wave65.parse_msggame(self.bundle.outputs[wave65.PK], "W65 PK")
        before_literals = wave65.w63.w59.literal_texts(before)
        w64_literals = wave65.w63.w59.literal_texts(w64)
        w65_literals = wave65.w63.w59.literal_texts(w65)
        w64_changed = {coordinate for coordinate in before_literals if before_literals[coordinate] != w64_literals[coordinate]}
        w65_changed = {coordinate for coordinate in before_literals if before_literals[coordinate] != w65_literals[coordinate]}
        self.assertTrue(w64_changed.isdisjoint(wave65.EXPECTED_TARGET_COORDINATES))
        self.assertEqual(w65_changed, w64_changed | set(wave65.EXPECTED_TARGET_COORDINATES))
        self.assertEqual(self.bundle.final_record_counts, wave65.EXPECTED_FINAL_RECORD_COUNTS)
        self.assertEqual(sum(self.bundle.final_record_counts.values()), wave65.EXPECTED_FINAL_TOTAL_RECORDS)

    def test_candidate_policy_and_pinned_output_profile(self) -> None:
        policy = self.bundle.audit["source_policy"]
        self.assertFalse(policy["switch_read"])
        self.assertFalse(policy["steam_game_resource_written"])
        self.assertEqual(policy["steam_apply_or_transaction_capability"], "absent")
        self.assertFalse(self.bundle.manifest["steam_game_resource_written"])
        self.assertFalse(self.bundle.manifest["git_operation_performed"])
        self.assertFalse(self.bundle.manifest["release_published"])
        pinned = wave65.prepare(require_output_profiles=True)
        self.assertEqual(pinned.outputs, self.bundle.outputs)


if __name__ == "__main__":
    unittest.main(verbosity=2)
