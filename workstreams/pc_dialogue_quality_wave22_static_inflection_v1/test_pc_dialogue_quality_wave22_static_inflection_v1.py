#!/usr/bin/env python3
"""Regression contracts for the private Wave 22 static-dialogue candidate."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_dialogue_quality_wave22_static_inflection_v1.py")
EXTRACTOR_PATH = SCRIPT.with_name("derive_wave22_specs.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("pc_dialogue_quality_wave22", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


WAVE22 = load_builder()


class Wave22StaticInflectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.predecessor_hashes = WAVE22.profile_hashes(WAVE22.PREDECESSOR_ROOT)
        cls.predecessor_sizes = WAVE22.profile_sizes(WAVE22.PREDECESSOR_ROOT)
        if cls.predecessor_hashes != WAVE22.INPUT_SHA256 or cls.predecessor_sizes != WAVE22.INPUT_SIZES:
            raise RuntimeError("Wave 20 is not the exact pinned Wave 22 predecessor")
        cls.output_a, cls.audit_a = WAVE22.prepare_candidate(WAVE22.PREDECESSOR_ROOT)
        cls.output_b, cls.audit_b = WAVE22.prepare_candidate(WAVE22.PREDECESSOR_ROOT)
        cls.before = {
            resource: WAVE22.records_by_coordinate((WAVE22.PREDECESSOR_ROOT / resource).read_bytes())
            for resource in WAVE22.CHANGED_PATHS
        }
        cls.after = {
            resource: WAVE22.records_by_coordinate(cls.output_a[resource])
            for resource in WAVE22.CHANGED_PATHS
        }

    def test_unique_wave20_eleven_file_preimage_and_pinned_output_profile(self) -> None:
        self.assertEqual(tuple(WAVE22.INPUT_SHA256), WAVE22.PROFILE_PATHS)
        self.assertEqual(tuple(WAVE22.INPUT_SIZES), WAVE22.PROFILE_PATHS)
        self.assertEqual(tuple(WAVE22.TARGET_SHA256), WAVE22.PROFILE_PATHS)
        self.assertEqual(tuple(WAVE22.TARGET_SIZES), WAVE22.PROFILE_PATHS)
        self.assertEqual(self.predecessor_hashes, WAVE22.INPUT_SHA256)
        self.assertEqual(self.predecessor_sizes, WAVE22.INPUT_SIZES)
        self.assertEqual(WAVE22.sha256_bytes(self.output_a[WAVE22.BASE_MSGGAME]), WAVE22.TARGET_SHA256[WAVE22.BASE_MSGGAME])
        self.assertEqual(WAVE22.sha256_bytes(self.output_a[WAVE22.PK_MSGGAME]), WAVE22.TARGET_SHA256[WAVE22.PK_MSGGAME])
        self.assertEqual(len(self.output_a[WAVE22.BASE_MSGGAME]), WAVE22.TARGET_SIZES[WAVE22.BASE_MSGGAME])
        self.assertEqual(len(self.output_a[WAVE22.PK_MSGGAME]), WAVE22.TARGET_SIZES[WAVE22.PK_MSGGAME])
        for relative in WAVE22.PROFILE_PATHS:
            if relative not in WAVE22.CHANGED_PATHS:
                self.assertEqual(WAVE22.INPUT_SHA256[relative], WAVE22.TARGET_SHA256[relative])
                self.assertEqual(WAVE22.INPUT_SIZES[relative], WAVE22.TARGET_SIZES[relative])
        evidence = WAVE22.validate_wave20_evidence(WAVE22.PREDECESSOR_ROOT)
        self.assertEqual(evidence["profile_sha256"], WAVE22.INPUT_SHA256)
        self.assertEqual(evidence["profile_sizes"], WAVE22.INPUT_SIZES)

    def test_exact_26_targets_remove_only_0143_and_preserve_marker_layout(self) -> None:
        expected_keys = set()
        for family in WAVE22.FAMILIES:
            for resource, coordinate, preimage in (
                (WAVE22.BASE_MSGGAME, family.base_coordinate, family.base_preimage),
                (WAVE22.PK_MSGGAME, family.pk_coordinate, family.pk_preimage),
            ):
                expected_keys.add((resource, coordinate))
                with self.subTest(family=family.name, resource=resource):
                    before = self.before[resource][coordinate]
                    after = self.after[resource][coordinate]
                    WAVE22.assert_record_spec(before, preimage, f"test preimage {family.name}")
                    self.assertEqual(WAVE22.sha256_bytes(after.data), family.target.sha256)
                    self.assertEqual(len(after.data), family.target.size)
                    self.assertEqual(WAVE22.literal_texts(after), family.target_literals)
                    self.assertEqual(WAVE22.marker_topology(after), WAVE22.marker_topology(before))
                    self.assertEqual(WAVE22.opaque_spans(after), WAVE22.stripped_opaque_spans(before))
                    self.assertEqual(
                        tuple(value.hex().upper() for value in WAVE22.opaque_spans(after)),
                        family.target.opaque_spans_hex,
                    )
                    self.assertEqual(WAVE22.morphology_commands(after), ())
                    self.assertTrue(after.data.endswith(WAVE22.RECORD_TERMINATOR))
                    self.assertEqual("".join(WAVE22.literal_texts(before)).count("\n"), "".join(WAVE22.literal_texts(after)).count("\n"))
                    self.assertLessEqual("".join(WAVE22.literal_texts(after)).count("\n") + 1, 3)
        self.assertEqual(len(expected_keys), 26)

    def test_only_the_13_pairs_change_and_all_holds_are_untouched(self) -> None:
        expected_by_resource = {
            WAVE22.BASE_MSGGAME: {family.base_coordinate for family in WAVE22.FAMILIES},
            WAVE22.PK_MSGGAME: {family.pk_coordinate for family in WAVE22.FAMILIES},
        }
        for resource in WAVE22.CHANGED_PATHS:
            with self.subTest(resource=resource):
                self.assertEqual(self.before[resource].keys(), self.after[resource].keys())
                changed = {
                    coordinate
                    for coordinate in self.before[resource]
                    if self.before[resource][coordinate].data != self.after[resource][coordinate].data
                }
                self.assertEqual(changed, expected_by_resource[resource])
        for hold in WAVE22.HOLDS:
            self.assertEqual(
                self.before[WAVE22.BASE_MSGGAME][hold.base_coordinate].data,
                self.after[WAVE22.BASE_MSGGAME][hold.base_coordinate].data,
                hold.name,
            )
            self.assertEqual(
                self.before[WAVE22.PK_MSGGAME][hold.pk_coordinate].data,
                self.after[WAVE22.PK_MSGGAME][hold.pk_coordinate].data,
                hold.name,
            )

    def test_pc_whole_record_anchors_and_real_font_widths_are_pinned(self) -> None:
        references, actual_hashes = WAVE22.load_references()
        self.assertEqual(actual_hashes, {key: value[1] for key, value in WAVE22.PC_REFERENCE_PATHS.items()})
        WAVE22.validate_family_anchors(references)
        for family in WAVE22.FAMILIES:
            with self.subTest(family=family.name):
                self.assertEqual(WAVE22.font_line_widths_px(family.target_literals), family.target_font_widths_px)
                self.assertTrue(all(width <= WAVE22.DIALOGUE_MAX_LINE_PX for width in family.target_font_widths_px))
        self.assertEqual(max(max(family.target_font_widths_px) for family in WAVE22.FAMILIES), 912)

    def test_non_morphology_opaque_bytes_are_preserved_by_rebuilder(self) -> None:
        source_data = (
            b"\xA1"
            + WAVE22.LITERAL_START + "old".encode("utf-16-le") + WAVE22.LITERAL_END
            + b"\x01\x43\x12\x34\x56\x78\xB2"
            + WAVE22.LITERAL_START + "tail".encode("utf-16-le") + WAVE22.LITERAL_END
            + b"\xC3\x01\x43\x01\x00\x00\x00\x05\x05\x05"
        )
        source = WAVE22.MsgGameRecord(99, 99, 0, source_data)
        rebuilt_data = WAVE22.rebuild_static_record(source, ("new", "tail"))
        rebuilt = WAVE22.MsgGameRecord(99, 99, 0, rebuilt_data)
        self.assertEqual(WAVE22.opaque_spans(rebuilt), (b"\xA1", b"\xB2", b"\xC3\x05\x05\x05"))
        self.assertEqual(WAVE22.marker_topology(rebuilt), WAVE22.marker_topology(source))
        self.assertEqual(WAVE22.morphology_commands(rebuilt), ())
        self.assertTrue(rebuilt.data.endswith(WAVE22.RECORD_TERMINATOR))

    def test_determinism_source_policy_and_tmp_guard(self) -> None:
        self.assertEqual(self.output_a, self.output_b)
        self.assertEqual(json.dumps(self.audit_a, ensure_ascii=False, sort_keys=True), json.dumps(self.audit_b, ensure_ascii=False, sort_keys=True))
        policy = self.audit_a["source_policy"]
        self.assertTrue(policy["wave20_full_profile_required"])
        self.assertTrue(policy["pristine_pc_japanese_read"])
        self.assertTrue(policy["pc_pk_en_sc_tc_context_read"])
        self.assertFalse(policy["switch_korean_read"])
        self.assertFalse(policy["steam_game_resource_written"])
        self.assertEqual(policy["git_operation"], "absent")
        self.assertEqual(policy["release_operation"], "absent")
        self.assertEqual(self.audit_a["changed_record_count"], 26)
        self.assertEqual(self.audit_a["held_pair_count"], 7)
        with self.assertRaises(WAVE22.Wave22Error):
            WAVE22.require_tmp(WAVE22.DEFAULT_STEAM_ROOT, "Steam path")
        with self.assertRaises(WAVE22.Wave22Error):
            WAVE22.require_predecessor_root(WAVE22.REPO)

    def test_extractor_is_windows_stdout_safe_and_reports_ascii_json(self) -> None:
        environment = dict(os.environ)
        environment["PYTHONIOENCODING"] = "cp949"
        result = subprocess.run(
            [sys.executable, "-B", str(EXTRACTOR_PATH), "--index", "0"],
            cwd=SCRIPT.parents[2],
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.isascii())
        payload = json.loads(result.stdout)
        self.assertEqual(payload["families"][0]["name"], "farewell_good_news")
        self.assertEqual(payload["families"][0]["contexts"]["EN"]["size"], 153)


if __name__ == "__main__":
    unittest.main(verbosity=2)
