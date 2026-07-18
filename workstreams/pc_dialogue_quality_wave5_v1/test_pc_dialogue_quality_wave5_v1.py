#!/usr/bin/env python3
"""Regression checks for the source-gated Wave 5 dialogue candidate."""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BUILD = WORKSTREAM / "build_pc_dialogue_quality_wave5_v1.py"

spec = importlib.util.spec_from_file_location("wave5_quality", BUILD)
assert spec and spec.loader
wave5 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = wave5
spec.loader.exec_module(wave5)


class Wave5QualityTests(unittest.TestCase):
    def test_steam_ineligible_runtime_particle_rows_are_not_planned(self) -> None:
        self.assertEqual(
            wave5.PK_RUNTIME_PARTICLE_DONOR_HOLD_COORDINATES,
            {(2, 331), (6, 3696), (6, 3697)},
        )
        planned = {plan.coordinate for plan in wave5.PK_EXTRA_PLANS}
        self.assertFalse(planned & wave5.PK_RUNTIME_PARTICLE_DONOR_HOLD_COORDINATES)
        self.assertFalse(
            planned & set(wave5.PK_RUNTIME_PARTICLE_RECLASSIFICATION_BY_COORDINATE)
        )
        self.assertEqual(len(wave5.PK_RUNTIME_PARTICLE_HOLD_COORDINATES), 121)
        self.assertEqual(
            wave5.PK_RUNTIME_PARTICLE_RELATION_OVERRIDE_COORDINATES,
            {(6, 1479), (6, 1480), (6, 1481)},
        )
        self.assertFalse(planned & wave5.PK_RUNTIME_PARTICLE_GENERIC_DONOR_HOLD_COORDINATES)
        self.assertTrue(
            wave5.PK_RUNTIME_PARTICLE_RELATION_OVERRIDE_COORDINATES <= planned
        )

    def test_relation_logs_replace_particle_dependent_donors(self) -> None:
        expected = {(6, 1476), (6, 1479), (6, 1480), (6, 1481), (6, 1527)}
        self.assertEqual(set(wave5.PK_RELATION_LOG_ROWS_BY_COORDINATE), expected)
        self.assertFalse(expected & set(wave5.PK_DONOR_ROWS_BY_COORDINATE))
        self.assertTrue(expected <= {plan.coordinate for plan in wave5.PK_EXTRA_PLANS})

    def test_conflict_repairs_cover_only_reviewed_conflicts(self) -> None:
        self.assertEqual(
            wave5.PK_CONFLICT_REPAIR_COORDINATES,
            wave5.PK_SAMEPK_CONFLICT_COORDINATES,
        )
        self.assertNotIn((4, 76), wave5.PK_CONFLICT_REPAIR_COORDINATES)
        planned = {plan.coordinate for plan in wave5.PK_EXTRA_PLANS}
        self.assertTrue(wave5.PK_CONFLICT_REPAIR_COORDINATES <= planned)
        self.assertFalse(
            wave5.PK_CONFLICT_REPAIR_COORDINATES & set(wave5.PK_DONOR_ROWS_BY_COORDINATE)
        )

    def test_dangga_literals_have_exact_safe_batch_membership(self) -> None:
        coordinates = set(wave5.BASE_DANGGA_ROWS_BY_COORDINATE)
        self.assertEqual(len(coordinates), 32)
        self.assertFalse(coordinates & {(6, record) for record in range(1438, 1450)})
        self.assertTrue(coordinates <= {plan.coordinate for plan in wave5.BASE_EXTRA_PLANS})

    def test_event_linebreak_scope_is_explicit(self) -> None:
        self.assertEqual(wave5.PK_EVENT_STATIC_REPAIR_IDS, (5492, 6668))
        self.assertEqual(
            wave5.BASE_EVENT_LINEBREAK_HOLD_IDS,
            (4657, 4781, 6233, 6668, 7475, 16397),
        )
        self.assertIn(wave5.EVENT_PK_RESOURCE, wave5.CHANGED_PATHS)
        self.assertNotIn(wave5.EVENT_BASE_RESOURCE, wave5.CHANGED_PATHS)
        self.assertTrue(
            all(
                row["application_eligible"] is False
                for row in wave5.BASE_EVENT_LINEBREAK_HOLD_AUDIT_ROWS
            )
        )

    def test_residual_quality_scope_and_review_override_are_explicit(self) -> None:
        self.assertEqual(len(wave5.RESIDUAL_KOREAN_QUALITY_ROWS), 16)
        self.assertEqual(len(wave5.RESIDUAL_KOREAN_QUALITY_HOLD_ROWS), 4)
        reviewed = [
            row
            for row in wave5.RESIDUAL_KOREAN_QUALITY_ROWS
            if row["resource"] == "PK" and row["coordinate"] == "14:226"
        ]
        self.assertEqual(len(reviewed), 1)
        self.assertEqual(
            reviewed[0]["output_record_sha256"],
            "4C8A8E79432A1CAB5177F1642D7D7240A7A886FC6298544A9995EBCDFBCE5CD4",
        )
        self.assertEqual(
            reviewed[0]["literal_changes"][0]["replacement_literal_sha256"],
            "0E2DB81CDC0FE52740B7DE038AF1B73C03699896212018BCA01F7133A5833B8E",
        )

    def test_batch_preserves_unplanned_bytes_and_audit_hashes(self) -> None:
        steam = wave5.DEFAULT_STEAM_ROOT
        self.assertTrue(steam.is_dir(), steam)
        with tempfile.TemporaryDirectory(dir=REPO / "tmp") as directory:
            root = Path(directory)
            candidate = root / "candidate"
            manifest = root / "manifest.json"
            output = wave5.build_candidate(steam, candidate, manifest, allow_unpinned_output=False)
            base_residual_count = sum(
                row["resource"] == "Base" for row in wave5.RESIDUAL_KOREAN_QUALITY_ROWS
            )
            pk_residual_count = sum(
                row["resource"] == "PK" for row in wave5.RESIDUAL_KOREAN_QUALITY_ROWS
            )
            self.assertEqual(output["base_plan_count"], len(wave5.BASE_EXTRA_PLANS) + base_residual_count)
            self.assertEqual(output["pk_plan_count"], len(wave5.PK_EXTRA_PLANS) + pk_residual_count)
            self.assertEqual(output["base_residual_quality_plan_count"], base_residual_count)
            self.assertEqual(output["pk_residual_quality_plan_count"], pk_residual_count)
            self.assertEqual(
                output["residual_korean_quality"]["candidate_count"],
                len(wave5.RESIDUAL_KOREAN_QUALITY_ROWS),
            )
            self.assertEqual(
                output["event_linebreak_audit"]["pk_static_repair_ids"],
                list(wave5.PK_EVENT_STATIC_REPAIR_IDS),
            )
            self.assertEqual(output["event_linebreak_audit"]["base_changes_applied"], 0)
            self.assertEqual(
                output["output_sha256"]["MSG/JP/msggame.bin"],
                wave5.sha256_bytes((candidate / "MSG/JP/msggame.bin").read_bytes()),
            )
            self.assertEqual(
                output["output_sha256"][wave5.EVENT_PK_RESOURCE],
                wave5.sha256_bytes((candidate / wave5.EVENT_PK_RESOURCE).read_bytes()),
            )

            self.assertEqual(
                (candidate / wave5.EVENT_BASE_RESOURCE).read_bytes(),
                (steam / wave5.EVENT_BASE_RESOURCE).read_bytes(),
            )
            event_before_wrapper, event_before_raw = wave5.decompress_wrapper(
                (steam / wave5.EVENT_PK_RESOURCE).read_bytes()
            )
            event_after_wrapper, event_after_raw = wave5.decompress_wrapper(
                (candidate / wave5.EVENT_PK_RESOURCE).read_bytes()
            )
            self.assertEqual(event_before_wrapper.prefix, event_after_wrapper.prefix)
            event_before = wave5.parse_message_table(event_before_raw)
            event_after = wave5.parse_message_table(event_after_raw)
            self.assertEqual(
                wave5.rebuild_message_table(event_before, event_before.texts), event_before_raw
            )
            self.assertEqual(
                wave5.rebuild_message_table(event_after, event_after.texts), event_after_raw
            )
            self.assertEqual(
                wave5.sha256_bytes(event_after_raw), wave5.EVENT_PK_TARGET_RAW_SHA256
            )
            self.assertEqual(
                wave5.sha256_bytes((candidate / wave5.EVENT_PK_RESOURCE).read_bytes()),
                wave5.EVENT_PK_TARGET_PACKED_SHA256,
            )
            self.assertEqual(
                event_after.logical_size,
                event_before.logical_size + wave5.EVENT_PK_LOGICAL_SIZE_DELTA,
            )
            for record_id, expected_delta in (
                (5492, 0),
                (5493, -2),
                (6668, -2),
                (6669, -4),
                (event_before.string_count - 1, -4),
            ):
                self.assertEqual(
                    event_after.string_offsets[record_id] - event_before.string_offsets[record_id],
                    expected_delta,
                    record_id,
                )
            changed_event_ids = {
                record_id
                for record_id, (before_text, after_text) in enumerate(
                    zip(event_before.texts, event_after.texts)
                )
                if before_text != after_text
            }
            self.assertEqual(changed_event_ids, set(wave5.PK_EVENT_STATIC_REPAIR_IDS))
            for record_id, row in wave5.PK_EVENT_STATIC_REPAIR_ROWS_BY_ID.items():
                self.assertEqual(event_before.texts[record_id], row["current"]["literal"])
                self.assertEqual(event_after.texts[record_id], row["replacement"]["literal"])
                self.assertEqual(
                    wave5.event_text_sha256(event_after.texts[record_id]),
                    row["replacement"]["utf16le_sha256"],
                )
                self.assertEqual(
                    wave5.event_protected_contract(event_after.texts[record_id]),
                    row["replacement"]["protected_contract"],
                )
                self.assertLessEqual(
                    wave5.event_line_count(event_after.texts[record_id]),
                    row["invariants"]["line_count_max"],
                )

            source = (steam / "MSG/JP/msggame.bin").read_bytes()
            wave3 = wave5.WAVE4.WAVE3.rebuild_static_resource(
                source, wave5.WAVE4.WAVE3.BASE_PLANS, "MSG/JP/msggame.bin"
            )
            wave4 = wave5.WAVE4.rebuild_quality_resource(
                wave3,
                wave5.WAVE4.BASE_PLANS,
                "MSG/JP/msggame.bin",
                wave5.WAVE4.records_by_coordinate(wave3),
            )
            before = wave5.WAVE4.records_by_coordinate(wave4)
            after = wave5.WAVE4.records_by_coordinate((candidate / "MSG/JP/msggame.bin").read_bytes())
            base_residual_items = wave5.materialize_residual_korean_quality_plans(
                "MSG/JP/msggame.bin", wave4
            )
            base_residual_rows = {
                item[0].coordinate: (item[1], item[2]) for item in base_residual_items
            }
            plans = {
                item.coordinate: item
                for item in (*wave5.BASE_EXTRA_PLANS, *(entry[0] for entry in base_residual_items))
            }
            self.assertEqual(set(before), set(after))
            for coordinate, record in before.items():
                actual = after[coordinate]
                plan = plans.get(coordinate)
                if plan is None:
                    self.assertEqual(actual.data, record.data, coordinate)
                    continue
                if coordinate in base_residual_rows:
                    row, expected_hash = base_residual_rows[coordinate]
                    self.assertEqual(wave5.sha256_bytes(actual.data), expected_hash, coordinate)
                    self.assertEqual(
                        wave5.WAVE4.opaque_bytes(actual), wave5.WAVE4.opaque_bytes(record), coordinate
                    )
                    actual_literals = {
                        item.literal_id: item.text for item in wave5.WAVE4.parse_record_literals(actual)
                    }
                    for literal in row["literal_changes"]:
                        replacement = next(
                            item.replacement
                            for item in plan.changes
                            if item.literal_id == literal["literal_id"]
                        )
                        self.assertEqual(actual_literals[literal["literal_id"]], replacement, coordinate)
                        self.assertEqual(
                            wave5.residual_visible_line_count(replacement),
                            literal["line_count_after"],
                            coordinate,
                        )
                    continue
                self.assertEqual(
                    wave5.WAVE4.opaque_bytes(actual),
                    wave5.WAVE4.expected_opaque_after_removals(record, plan),
                    coordinate,
                )
                self.assertEqual(
                    wave5.sha256_bytes(actual.data),
                    wave5.BASE_EXPECTED_OUTPUT_RECORD_SHA256[coordinate],
                    coordinate,
                )
                self.assertLessEqual(wave5.WAVE4.rendered_literal_line_count(actual), 3)

            source_pk = (steam / "MSG_PK/JP/msggame.bin").read_bytes()
            wave3_pk = wave5.WAVE4.WAVE3.rebuild_static_resource(
                source_pk, wave5.WAVE4.WAVE3.PK_PLANS, "MSG_PK/JP/msggame.bin"
            )
            wave4_pk = wave5.WAVE4.rebuild_quality_resource(
                wave3_pk,
                wave5.WAVE4.PK_PLANS,
                "MSG_PK/JP/msggame.bin",
                wave5.WAVE4.records_by_coordinate(wave3),
            )
            before_pk = wave5.WAVE4.records_by_coordinate(wave4_pk)
            after_pk = wave5.WAVE4.records_by_coordinate((candidate / "MSG_PK/JP/msggame.bin").read_bytes())
            pk_residual_items = wave5.materialize_residual_korean_quality_plans(
                "MSG_PK/JP/msggame.bin", wave4_pk
            )
            pk_residual_rows = {
                item[0].coordinate: (item[1], item[2]) for item in pk_residual_items
            }
            pk_plans = {
                item.coordinate: item
                for item in (*wave5.PK_EXTRA_PLANS, *(entry[0] for entry in pk_residual_items))
            }
            self.assertEqual(set(before_pk), set(after_pk))
            for coordinate, record in before_pk.items():
                actual = after_pk[coordinate]
                plan = pk_plans.get(coordinate)
                if plan is None:
                    self.assertEqual(actual.data, record.data, coordinate)
                    continue
                if coordinate in pk_residual_rows:
                    row, expected_hash = pk_residual_rows[coordinate]
                    self.assertEqual(wave5.sha256_bytes(actual.data), expected_hash, coordinate)
                    self.assertEqual(
                        wave5.WAVE4.opaque_bytes(actual), wave5.WAVE4.opaque_bytes(record), coordinate
                    )
                    actual_literals = {
                        item.literal_id: item.text for item in wave5.WAVE4.parse_record_literals(actual)
                    }
                    for literal in row["literal_changes"]:
                        replacement = next(
                            item.replacement
                            for item in plan.changes
                            if item.literal_id == literal["literal_id"]
                        )
                        self.assertEqual(actual_literals[literal["literal_id"]], replacement, coordinate)
                        self.assertEqual(
                            wave5.residual_visible_line_count(replacement),
                            literal["line_count_after"],
                            coordinate,
                        )
                    continue
                self.assertEqual(
                    wave5.sha256_bytes(actual.data),
                    wave5.PK_EXPECTED_OUTPUT_RECORD_SHA256[coordinate],
                    coordinate,
                )
                if coordinate in wave5.PK_DONOR_ROWS_BY_COORDINATE:
                    self.assertEqual(wave5.WAVE4.opaque_bytes(actual), wave5.WAVE4.opaque_bytes(record), coordinate)
                    row = wave5.PK_DONOR_ROWS_BY_COORDINATE[coordinate]
                    self.assertEqual(
                        wave5.opaque_schema(actual),
                        wave5.require_opaque_schema(row, "asserted_output_opaque_schema", coordinate),
                        coordinate,
                    )
                elif coordinate in wave5.PK_RELATION_LOG_ROWS_BY_COORDINATE:
                    self.assertEqual(wave5.WAVE4.opaque_bytes(actual), wave5.WAVE4.opaque_bytes(record), coordinate)
                    row = wave5.PK_RELATION_LOG_ROWS_BY_COORDINATE[coordinate]
                    self.assertEqual(
                        wave5.opaque_schema(actual),
                        wave5.require_opaque_schema(row, "asserted_output_opaque_schema", coordinate),
                        coordinate,
                    )
                elif coordinate in wave5.PK_CONFLICT_REPAIR_ROWS_BY_COORDINATE:
                    self.assertEqual(wave5.WAVE4.opaque_bytes(actual), wave5.WAVE4.opaque_bytes(record), coordinate)
                    conflict = wave5.PK_CONFLICT_ROWS_BY_COORDINATE[coordinate]
                    repair = wave5.PK_CONFLICT_REPAIR_ROWS_BY_COORDINATE[coordinate]
                    self.assertEqual(
                        wave5.opaque_schema(actual),
                        wave5.require_opaque_schema(
                            conflict, "asserted_output_opaque_schema", coordinate
                        ),
                        coordinate,
                    )
                    self.assertEqual(
                        wave5.WAVE4.rendered_literal_line_count(actual),
                        repair["manual_line_count"],
                        coordinate,
                    )
                else:
                    self.assertEqual(
                        wave5.WAVE4.opaque_bytes(actual),
                        wave5.WAVE4.expected_opaque_after_removals(record, plan),
                        coordinate,
                    )
                    row = wave5.PK_RUNTIME_SUFFIX_ROWS_BY_COORDINATE[coordinate]
                    self.assertEqual(
                        wave5.opaque_span_contract(actual),
                        wave5.require_span_contract(row, "asserted_output_opaque_spans", coordinate),
                        coordinate,
                    )
                self.assertLessEqual(wave5.WAVE4.rendered_literal_line_count(actual), 3)


if __name__ == "__main__":
    unittest.main()
