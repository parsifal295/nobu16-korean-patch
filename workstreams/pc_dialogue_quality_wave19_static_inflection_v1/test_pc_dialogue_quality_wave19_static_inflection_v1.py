#!/usr/bin/env python3
"""Regression contracts for the private Wave 19 static-dialogue candidate."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_dialogue_quality_wave19_static_inflection_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("pc_dialogue_quality_wave19", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


WAVE19 = load_builder()


class Wave19StaticInflectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.input_root = WAVE19.PREDECESSOR_CANDIDATE_ROOT
        cls.input_profile = WAVE19.profile_hashes(cls.input_root)
        if cls.input_profile != WAVE19.INPUT_SHA256:
            raise RuntimeError("Wave 17 candidate is not the exact pinned Wave 19 predecessor")
        cls.output_a, cls.audit_a = WAVE19.prepare_candidate(cls.input_root)
        cls.output_b, cls.audit_b = WAVE19.prepare_candidate(cls.input_root)
        cls.before = {
            resource: WAVE19.records_by_coordinate((cls.input_root / resource).read_bytes())
            for resource in WAVE19.CHANGED_PATHS
        }
        cls.after = {
            resource: WAVE19.records_by_coordinate(packed)
            for resource, packed in cls.output_a.items()
        }

    def test_wave17_successor_is_the_only_pinned_input(self) -> None:
        self.assertEqual(tuple(WAVE19.INPUT_SHA256), WAVE19.PROFILE_PATHS)
        self.assertEqual(tuple(WAVE19.TARGET_SHA256), WAVE19.PROFILE_PATHS)
        self.assertEqual(self.input_profile, WAVE19.INPUT_SHA256)
        self.assertEqual(
            WAVE19.INPUT_SHA256[WAVE19.BASE_MSGGAME],
            "C1B39C7344F8A095E179942A26FB4EBDECEAABC2D6A8966A0DB134B7EBE600AC",
        )
        self.assertEqual(
            WAVE19.INPUT_SHA256[WAVE19.PK_MSGGAME],
            "9EB0FD80E7A6D50BC2A6073FDBF213E7BDB685D81DFCD9191C9C86E415D7EFCC",
        )
        self.assertEqual(WAVE19.require_predecessor_root(self.input_root), self.input_root.resolve())
        for resource in WAVE19.CHANGED_PATHS:
            with self.subTest(resource=resource):
                self.assertEqual(
                    len(self.output_a[resource]), WAVE19.TARGET_PACKED_SIZES[resource]
                )
                self.assertEqual(
                    WAVE19.sha256_bytes(self.output_a[resource]),
                    WAVE19.TARGET_SHA256[resource],
                )

    def test_exact_twelve_targets_preserve_their_opaque_layouts(self) -> None:
        self.assertEqual(len(WAVE19.CHANGES), 12)
        self.assertEqual(
            [(change.resource, change.coordinate) for change in WAVE19.CHANGES],
            [
                (WAVE19.BASE_MSGGAME, (6, 4224)),
                (WAVE19.PK_MSGGAME, (6, 4254)),
                (WAVE19.BASE_MSGGAME, (6, 4446)),
                (WAVE19.PK_MSGGAME, (6, 4505)),
                (WAVE19.BASE_MSGGAME, (8, 1043)),
                (WAVE19.PK_MSGGAME, (8, 1055)),
                (WAVE19.BASE_MSGGAME, (15, 1523)),
                (WAVE19.PK_MSGGAME, (15, 1538)),
                (WAVE19.BASE_MSGGAME, (15, 2202)),
                (WAVE19.PK_MSGGAME, (15, 2232)),
                (WAVE19.PK_MSGGAME, (2, 503)),
                (WAVE19.PK_MSGGAME, (2, 533)),
            ],
        )
        for change in WAVE19.CHANGES:
            with self.subTest(change=f"{change.resource}:{change.coordinate_text}"):
                before = self.before[change.resource][change.coordinate]
                after = self.after[change.resource][change.coordinate]
                self.assertEqual(WAVE19.sha256_bytes(before.data), change.current.sha256)
                self.assertEqual(len(before.data), change.current.size)
                self.assertEqual(
                    tuple(value.hex().upper() for value in WAVE19.opaque_spans(before)),
                    change.current.opaque_spans_hex,
                )
                self.assertEqual(
                    WAVE19.morphology_commands(before),
                    change.current.morphology_commands_hex,
                )
                self.assertEqual(
                    WAVE19.stripped_opaque_spans(before),
                    WAVE19.output_opaque_spans(change.target_literals),
                )
                self.assertEqual(WAVE19.sha256_bytes(after.data), change.target_record_sha256)
                self.assertEqual(len(after.data), change.target_record_size)
                self.assertEqual(WAVE19.literal_texts(after), change.target_literals)
                self.assertEqual(WAVE19.morphology_commands(after), ())
                self.assertEqual(
                    WAVE19.opaque_spans(after),
                    WAVE19.output_opaque_spans(change.target_literals),
                )
                self.assertTrue(after.data.endswith(WAVE19.RECORD_TERMINATOR))
                self.assertEqual(WAVE19.marker_topology(after), WAVE19.marker_topology(before))
                self.assertEqual(
                    "".join(WAVE19.literal_texts(before)).count("\n"),
                    "".join(change.target_literals).count("\n"),
                )
                self.assertLessEqual("".join(change.target_literals).count("\n") + 1, 3)
                self.assertEqual(
                    WAVE19.line_upper_bound_px(change.target_literals),
                    change.target_line_upper_bounds_px,
                )
                self.assertTrue(
                    all(width <= WAVE19.DIALOGUE_MAX_LINE_PX for width in change.target_line_upper_bounds_px)
                )
                if change.target_font_widths_px is not None:
                    self.assertEqual(
                        WAVE19.font_line_widths_px(change.target_literals),
                        change.target_font_widths_px,
                    )

    def test_village_pair_removes_all_three_morphology_commands(self) -> None:
        village = [change for change in WAVE19.CHANGES if change.family == "village_reconstruction"]
        self.assertEqual(len(village), 2)
        for change in village:
            with self.subTest(change=change.coordinate_text):
                before = self.before[change.resource][change.coordinate]
                after = self.after[change.resource][change.coordinate]
                self.assertEqual(len(WAVE19.morphology_commands(before)), 3)
                self.assertEqual(WAVE19.morphology_commands(after), ())
                self.assertEqual(len(WAVE19.literal_texts(after)), 2)
                self.assertEqual(
                    WAVE19.literal_texts(after),
                    (
                        WAVE19._u(
                            r"\uc2f8\uc6c0\uc73c\ub85c \ud669\ud3d0\ud574\uc9c4 \ub9c8\uc744\uc758\n"
                            r"\ubd80\ud765\uc744 \uc9c0\uc6d0\ud588\uc2b5\ub2c8\ub2e4."
                        ),
                        WAVE19._u(
                            r"\n\ubc31\uc131\ub4e4\ub3c4 \ubb34\ucc99 \uac10\uc0ac\ud558\uace0 \uc788\uc2b5\ub2c8\ub2e4."
                        ),
                    ),
                )
                self.assertEqual(
                    WAVE19.opaque_spans(after),
                    (b"", b"", WAVE19.RECORD_TERMINATOR),
                )

    def test_pk_wave17_counterparts_are_literal_only_and_opaque_stable(self) -> None:
        counterparts = [
            change
            for change in WAVE19.CHANGES
            if change.edit_kind == "literal_only_counterpart"
        ]
        self.assertEqual([(change.coordinate, change.resource) for change in counterparts], [
            ((2, 503), WAVE19.PK_MSGGAME),
            ((2, 533), WAVE19.PK_MSGGAME),
        ])
        expected_literals = {
            (2, 503): (
                WAVE19._u(
                    r"\ud718\ud558\uac00 \ub420 \uc7a5\uc218\ub4e4\uc5d0\uac8c\n"
                    r"\ud65c\uc57d\uc758 \uc7a5\uc744 \ub9c8\uc74c\uaecf "
                ),
                WAVE19._u(r"\uc8fc\uaca0\ub2e4!"),
            ),
            (2, 533): (
                WAVE19._u(r"\ud3ec\uc704\ubcd1\ub4e4\uc774 \ub9c8\uc74c\ub300\ub85c \ud558\uac8c \ub450\uc9c0 "),
                WAVE19._u(r"\uc54a\uaca0\ub2e4.\n\uc774\ucabd\uc5d0\uc11c\ub3c4 "),
                WAVE19._u(r"\ubc18\uaca9\ud558\uaca0\ub2e4!"),
            ),
        }
        for change in counterparts:
            with self.subTest(change=change.coordinate_text):
                before = self.before[change.resource][change.coordinate]
                after = self.after[change.resource][change.coordinate]
                self.assertEqual(WAVE19.morphology_commands(before), ())
                self.assertEqual(WAVE19.morphology_commands(after), ())
                self.assertEqual(WAVE19.opaque_spans(after), WAVE19.opaque_spans(before))
                self.assertEqual(WAVE19.literal_texts(after), expected_literals[change.coordinate])
                self.assertEqual(
                    WAVE19.font_line_widths_px(change.target_literals),
                    change.target_font_widths_px,
                )

    def test_only_twelve_records_change_and_archives_round_trip(self) -> None:
        expected_by_resource = {resource: set() for resource in WAVE19.CHANGED_PATHS}
        for change in WAVE19.CHANGES:
            expected_by_resource[change.resource].add(change.coordinate)
        for resource in WAVE19.CHANGED_PATHS:
            with self.subTest(resource=resource):
                self.assertEqual(self.before[resource].keys(), self.after[resource].keys())
                changed = {
                    coordinate
                    for coordinate in self.before[resource]
                    if self.before[resource][coordinate].data != self.after[resource][coordinate].data
                }
                self.assertEqual(changed, expected_by_resource[resource])
                for coordinate, record in self.before[resource].items():
                    if coordinate not in expected_by_resource[resource]:
                        self.assertEqual(record.data, self.after[resource][coordinate].data)
                WAVE19.validate_raw_roundtrip(self.output_a[resource], f"test candidate {resource}")

    def test_pc_jp_en_sc_tc_anchors_are_exact_and_audited(self) -> None:
        jp, contexts = WAVE19.load_references()
        WAVE19.validate_family_anchors(jp, contexts)
        self.assertEqual(set(contexts), {"EN", "SC", "TC"})
        self.assertEqual(len(self.audit_a["families"]), 7)
        for family, report in zip(WAVE19.FAMILIES, self.audit_a["families"], strict=True):
            with self.subTest(family=family.name):
                self.assertEqual(report["name"], family.name)
                self.assertEqual(
                    WAVE19.literal_texts(jp[WAVE19.BASE_MSGGAME][family.base_coordinate]),
                    WAVE19.literal_texts(jp[WAVE19.PK_MSGGAME][family.pk_coordinate]),
                )
                self.assertTrue(report["pc_base_jp"]["literals"])
                self.assertTrue(report["pc_pk_jp"]["literals"])
                for language in ("EN", "SC", "TC"):
                    self.assertTrue(report["pc_pk_contexts"][language]["literals"])
                    self.assertEqual(
                        report["pc_pk_contexts"][language]["record_sha256"],
                        family.sources[language].sha256,
                    )

    def test_candidate_is_deterministic_and_cannot_target_steam(self) -> None:
        self.assertEqual(self.output_a, self.output_b)
        self.assertEqual(
            json.dumps(self.audit_a, ensure_ascii=False, sort_keys=True),
            json.dumps(self.audit_b, ensure_ascii=False, sort_keys=True),
        )
        policy = self.audit_a["source_policy"]
        self.assertTrue(policy["wave17_11_file_profile_required"])
        self.assertTrue(policy["pristine_pc_japanese_read"])
        self.assertTrue(policy["pc_pk_en_sc_tc_context_read"])
        self.assertTrue(policy["active_pc_jp_font_read"])
        self.assertFalse(policy["switch_korean_read"])
        self.assertFalse(policy["steam_game_resource_written"])
        self.assertEqual(policy["steam_apply_capability"], "absent")
        self.assertEqual(policy["git_operation"], "absent")
        self.assertEqual(policy["release_operation"], "absent")
        with self.assertRaises(WAVE19.Wave19Error):
            WAVE19.require_tmp(WAVE19.DEFAULT_STEAM_ROOT, "Steam must be rejected")
        with self.assertRaises(WAVE19.Wave19Error):
            WAVE19.require_predecessor_root(WAVE19.DEFAULT_STEAM_ROOT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
