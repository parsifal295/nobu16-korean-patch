#!/usr/bin/env python3
"""Independent deterministic contracts for the private PC-only Wave 12 candidate."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_dialogue_quality_wave12_candidate_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("pc_dialogue_quality_wave12", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load Wave 12 builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


WAVE12 = load_builder()


class Wave12CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle_a = WAVE12.prepare_candidate(
            WAVE12.WAVE9_INPUT_ROOT, WAVE12.DEFAULT_FONT_ROOT
        )
        cls.bundle_b = WAVE12.prepare_candidate(
            WAVE12.WAVE9_INPUT_ROOT, WAVE12.DEFAULT_FONT_ROOT
        )

    def test_scope_and_hash_contracts_are_exact(self) -> None:
        self.assertEqual(
            WAVE12.RESOURCE_PATHS,
            ("MSG/JP/msggame.bin", "MSG_PK/JP/msggame.bin"),
        )
        self.assertEqual(WAVE12.COORDINATE, (13, 143))
        self.assertEqual(WAVE12.INPUT_RECORD_SIZE, 141)
        self.assertEqual(WAVE12.TARGET_RECORD_SIZE, 131)
        self.assertEqual(
            self.bundle_a.input_sha256,
            WAVE12.INPUT_SHA256,
        )
        self.assertEqual(
            self.bundle_a.output_sha256,
            WAVE12.TARGET_SHA256,
        )
        self.assertEqual(
            set(self.bundle_a.resources),
            set(WAVE12.RESOURCE_PATHS),
        )
        for resource in WAVE12.RESOURCE_PATHS:
            with self.subTest(resource=resource):
                self.assertEqual(
                    WAVE12.sha256_bytes(self.bundle_a.resources[resource]),
                    WAVE12.TARGET_SHA256[resource],
                )
                self.assertEqual(
                    len(self.bundle_a.resources[resource]), WAVE12.TARGET_SIZES[resource]
                )

    def test_candidate_is_deterministic_and_source_free(self) -> None:
        self.assertEqual(self.bundle_a.resources, self.bundle_b.resources)
        self.assertEqual(
            json.dumps(self.bundle_a.audit, ensure_ascii=False, sort_keys=True),
            json.dumps(self.bundle_b.audit, ensure_ascii=False, sort_keys=True),
        )
        self.assertTrue(self.bundle_a.audit["source_free"])
        self.assertFalse(self.bundle_a.audit["source_policy"]["switch_korean_used"])
        self.assertEqual(self.bundle_a.audit["steam_write_capability"], "absent")

    def test_only_the_two_target_records_change_and_controls_survive(self) -> None:
        inputs = WAVE12.validate_wave9_input(WAVE12.WAVE9_INPUT_ROOT)
        for resource in WAVE12.RESOURCE_PATHS:
            with self.subTest(resource=resource):
                before = WAVE12.records_by_coordinate(inputs[resource])
                after = WAVE12.records_by_coordinate(self.bundle_a.resources[resource])
                changed = {
                    coordinate
                    for coordinate in before
                    if before[coordinate].data != after[coordinate].data
                }
                self.assertEqual(changed, {WAVE12.COORDINATE})
                self.assertEqual(before.keys(), after.keys())
                for coordinate in before:
                    if coordinate != WAVE12.COORDINATE:
                        self.assertEqual(before[coordinate].data, after[coordinate].data)

                input_record = before[WAVE12.COORDINATE]
                output_record = after[WAVE12.COORDINATE]
                self.assertEqual(WAVE12.literal_texts(input_record), WAVE12.CURRENT_LITERALS)
                self.assertEqual(WAVE12.literal_texts(output_record), WAVE12.TARGET_LITERALS)
                self.assertEqual(
                    WAVE12.sha256_bytes(input_record.data), WAVE12.INPUT_RECORD_SHA256
                )
                self.assertEqual(
                    WAVE12.sha256_bytes(output_record.data), WAVE12.TARGET_RECORD_SHA256
                )
                self.assertEqual(len(input_record.data), 141)
                self.assertEqual(len(output_record.data), 131)
                self.assertEqual(
                    WAVE12.opaque_spans(input_record), WAVE12.opaque_spans(output_record)
                )
                self.assertEqual(
                    WAVE12.topology_hex(input_record), WAVE12.EXPECTED_MARKER_TOPOLOGY_HEX
                )
                self.assertEqual(
                    WAVE12.marker_topology(input_record), WAVE12.marker_topology(output_record)
                )
                self.assertTrue(output_record.data.endswith(WAVE12.RECORD_TERMINATOR))

    def test_pristine_pc_japanese_and_pc_english_meaning_anchors(self) -> None:
        evidence = WAVE12.validate_semantic_anchors()
        self.assertFalse(evidence["switch_korean_used"])
        self.assertEqual(
            evidence["anchors"]["base_pristine_jp"]["resource_sha256"],
            WAVE12.PC_REFERENCE_SHA256["base_pristine_jp"],
        )
        self.assertEqual(
            evidence["anchors"]["pk_pristine_jp"]["record_sha256"],
            WAVE12.PC_REFERENCE_RECORD_SHA256["pk_pristine_jp"],
        )
        self.assertEqual(
            evidence["anchors"]["pk_en"]["literal_utf16le_sha256"],
            [WAVE12.PC_REFERENCE_LITERAL_UTF16LE_SHA256["pk_en"]],
        )
        self.assertEqual(
            WAVE12.PRISTINE_PC_JP_LITERALS,
            (
                "当家はまだまだ力不足\n"
                "天下を狙うには領土を広げて力をつけ\n"
                "全国の大名に力を認めさせる必要があります",
            ),
        )
        self.assertIn("expand our domain", WAVE12.PC_EN_LITERALS[0])
        self.assertIn("respect of every", WAVE12.PC_EN_LITERALS[0])
        for path in WAVE12.PC_REFERENCE_PATHS.values():
            self.assertNotIn("switch", str(path).casefold())

    def test_target_font_layout_has_no_fallback_or_runtime_tokens(self) -> None:
        summary = self.bundle_a.audit["summary"]
        self.assertEqual(summary["manual_lines"], 3)
        self.assertEqual(summary["target_line_widths_px"], [672, 912, 888])
        self.assertLessEqual(max(summary["target_line_widths_px"]), WAVE12.MAX_LINE_PX)
        self.assertEqual(WAVE12.TARGET_LITERALS[0].count("\n"), 2)
        self.assertNotIn("\x1b", WAVE12.TARGET_LITERALS[0])
        self.assertNotIn("%", WAVE12.TARGET_LITERALS[0])
        self.assertEqual(len(self.bundle_a.audit["records"]), 2)
        for row in self.bundle_a.audit["records"]:
            with self.subTest(resource=row["resource"]):
                self.assertEqual(row["output_layout"]["line_count"], 3)
                self.assertEqual(row["output_layout"]["line_widths_px"], [672, 912, 888])
                self.assertEqual(row["output_layout"]["wide_fallback_codepoints"], [])
                self.assertEqual(row["missing_static_glyphs"], [])
                self.assertTrue(row["opaque_spans_preserved"])

    def test_manifest_is_private_and_has_no_steam_apply_operation(self) -> None:
        manifest = WAVE12.build_manifest(self.bundle_a, "A" * 64)
        self.assertEqual(manifest["changed_paths"], list(WAVE12.RESOURCE_PATHS))
        self.assertEqual(
            manifest["coordinates"],
            {
                "MSG/JP/msggame.bin": "13:143",
                "MSG_PK/JP/msggame.bin": "13:143",
            },
        )
        self.assertEqual(manifest["steam_write_capability"], "absent")
        self.assertIsNone(manifest["steam_apply_command"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
