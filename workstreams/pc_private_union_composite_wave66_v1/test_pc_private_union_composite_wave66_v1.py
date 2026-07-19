from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_private_union_composite_wave66_v1.py"
SPEC = importlib.util.spec_from_file_location("pc_private_union_wave66_test", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import guard
    raise RuntimeError("cannot import W66 builder")
wave66 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave66
SPEC.loader.exec_module(wave66)


class PrivateUnionCompositeWave66Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave66.prepare(require_output_profiles=False)
        cls.w65_bundle = wave66.w65.prepare(require_output_profiles=True)

    def test_scope_is_exact_and_pc_only(self) -> None:
        self.assertEqual(len(wave66.DIALOGUE_TARGETS), 46)
        self.assertEqual(len(wave66.EVENT_TARGETS), 15)
        self.assertEqual(
            {resource: tuple(target.coordinate for target in wave66.DIALOGUE_TARGETS if target.resource == resource)
             for resource in (wave66.BASE, wave66.PK)},
            wave66.EXPECTED_DIALOGUE_TARGETS,
        )
        self.assertEqual(tuple(target.entry_id for target in wave66.EVENT_TARGETS), wave66.EXPECTED_EVENT_IDS)
        self.assertEqual(
            {name: len(values) for name, values in self.bundle.event_classifications.items()},
            wave66.EXPECTED_EVENT_CLASSES,
        )
        policy = self.bundle.audit["source_policy"]
        self.assertFalse(policy["switch_read"])
        self.assertFalse(policy["steam_game_resource_written"])

    def test_dialogue_scope_controls_and_reflow_are_pinned(self) -> None:
        font = wave66.w64.layout.load_font()
        for resource in (wave66.BASE, wave66.PK):
            before = wave66.parse_msggame(self.w65_bundle.outputs[resource], f"W65 {resource}")
            after = wave66.parse_msggame(self.bundle.outputs[resource], f"W66 {resource}")
            before_literals = wave66.w63.w59.literal_texts(before)
            after_literals = wave66.w63.w59.literal_texts(after)
            changed = {coordinate for coordinate in before_literals if before_literals[coordinate] != after_literals[coordinate]}
            self.assertEqual(changed, set(wave66.EXPECTED_DIALOGUE_TARGETS[resource]))
            for target in (target for target in wave66.DIALOGUE_TARGETS if target.resource == resource):
                with self.subTest(resource=resource, coordinate=target.coordinate):
                    self.assertEqual(before_literals[target.coordinate], target.current_ko)
                    self.assertEqual(after_literals[target.coordinate], target.target_ko)
                    self.assertEqual(
                        wave66.literal_controls(before_literals[target.coordinate]),
                        wave66.literal_controls(after_literals[target.coordinate]),
                    )
                    if not target.allow_lf_change:
                        self.assertEqual(
                            before_literals[target.coordinate].count("\n"),
                            after_literals[target.coordinate].count("\n"),
                        )
                    if target.target_line_widths_px is not None:
                        widths = wave66.w64.layout.line_widths(after_literals[target.coordinate], font)
                        self.assertEqual(widths, target.target_line_widths_px)
                        self.assertLessEqual(max(widths), wave66.w64.layout.PK_MAX_LINE_PX)

    def test_event_scope_tags_and_widths_are_pinned(self) -> None:
        _header, _raw, before = wave66.w60.parse_table("W65 event", self.w65_bundle.outputs[wave66.MSGEV])
        _header, _raw, after = wave66.w60.parse_table("W66 event", self.bundle.outputs[wave66.MSGEV])
        font = wave66.w64.layout.load_font()
        changed = {index for index, value in enumerate(before.texts) if value != after.texts[index]}
        self.assertEqual(changed, set(wave66.EXPECTED_EVENT_IDS))
        for target in wave66.EVENT_TARGETS:
            with self.subTest(entry_id=target.entry_id):
                self.assertEqual(before.texts[target.entry_id], target.current_ko)
                self.assertEqual(after.texts[target.entry_id], target.target_ko)
                self.assertEqual(
                    wave66.static_event_signature(before.texts[target.entry_id], target.entry_id, "test source"),
                    wave66.static_event_signature(after.texts[target.entry_id], target.entry_id, "test target"),
                )
                self.assertEqual(wave66.w64.layout.line_widths(after.texts[target.entry_id], font), target.target_line_widths_px)
                self.assertLessEqual(max(target.target_line_widths_px), wave66.w64.layout.PK_MAX_LINE_PX)

    def test_w65_history_and_other_resource_are_retained(self) -> None:
        self.assertEqual(self.bundle.outputs[wave66.MSGDATA], self.w65_bundle.outputs[wave66.MSGDATA])
        w45 = wave66.w62.load_w45_backups()
        for resource in (wave66.BASE, wave66.PK):
            before = wave66.parse_msggame(w45[resource], f"W45 {resource}")
            w65 = wave66.parse_msggame(self.w65_bundle.outputs[resource], f"W65 {resource}")
            w66 = wave66.parse_msggame(self.bundle.outputs[resource], f"W66 {resource}")
            before_literals = wave66.w63.w59.literal_texts(before)
            w65_literals = wave66.w63.w59.literal_texts(w65)
            w66_literals = wave66.w63.w59.literal_texts(w66)
            w65_changed = {coordinate for coordinate in before_literals if before_literals[coordinate] != w65_literals[coordinate]}
            w66_changed = {coordinate for coordinate in before_literals if before_literals[coordinate] != w66_literals[coordinate]}
            targets = set(wave66.EXPECTED_DIALOGUE_TARGETS[resource])
            expected_history_revisions = set(
                wave66.EXPECTED_BASE_HISTORY_REVISIONS
                if resource == wave66.BASE
                else wave66.EXPECTED_PK_HISTORY_REVISIONS
            )
            self.assertEqual(w65_changed & targets, expected_history_revisions)
            self.assertEqual(w66_changed, w65_changed | targets)
            self.assertEqual(set(wave66.EXPECTED_HISTORY_REVISION_TEXTS[resource]), expected_history_revisions)
            for coordinate, (w45_text, w65_text, w66_text) in wave66.EXPECTED_HISTORY_REVISION_TEXTS[resource].items():
                with self.subTest(resource=resource, coordinate=coordinate):
                    self.assertEqual(before_literals[coordinate], w45_text)
                    self.assertEqual(w65_literals[coordinate], w65_text)
                    self.assertEqual(w66_literals[coordinate], w66_text)

    def test_candidate_policy_and_pinned_output_profile(self) -> None:
        self.assertFalse(self.bundle.manifest["steam_game_resource_written"])
        self.assertFalse(self.bundle.manifest["git_operation_performed"])
        self.assertFalse(self.bundle.manifest["release_published"])
        pinned = wave66.prepare(require_output_profiles=True)
        self.assertEqual(pinned.outputs, self.bundle.outputs)


if __name__ == "__main__":
    unittest.main(verbosity=2)
