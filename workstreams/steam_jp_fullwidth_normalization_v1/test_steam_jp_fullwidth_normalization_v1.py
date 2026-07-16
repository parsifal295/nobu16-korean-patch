"""Regression tests for the source-only Steam JP punctuation normalizer."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
BUILDER_PATH = ROOT / "build_steam_jp_fullwidth_normalization_v1.py"
SPEC = importlib.util.spec_from_file_location(
    "steam_jp_fullwidth_normalization_v1", BUILDER_PATH
)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class SteamJPFullwidthNormalizationV1Tests(unittest.TestCase):
    def test_coordinate_decoder_accepts_canonical_key_order_without_relaxing_key_set(self) -> None:
        # ``canonical_json(..., sort_keys=True)`` stores this mapping in
        # alphabetical order, not the schema tuple order for msggame.
        canonical_msggame = json.loads(
            '{"block_id": 4, "literal_id": 9, "record_id": 7}'
        )
        self.assertEqual(
            builder.coord_from_json(canonical_msggame, "msggame"),
            (4, 7, 9),
        )
        with self.assertRaises(builder.NormalizationError):
            builder.coord_from_json(
                {"block_id": 4, "record_id": 7, "unexpected": 9},
                "msggame",
            )

    def test_fullwidth_normalization_preserves_tokens_layout_and_edge_spaces(self) -> None:
        mapping = {"Ａ": "A", "１": "1", "　": " "}
        text = "　Ａ １ <tag data=１> \x1bC１ %s {slot} [TAG]\n"
        normalized, operations = builder.normalization_operations(text, mapping)
        self.assertEqual(normalized, "　A 1 <tag data=１> \x1bC１ %s {slot} [TAG]\n")
        self.assertEqual(
            [(item["from"], item["to"]) for item in operations],
            [("U+FF21", "U+0041"), ("U+FF11", "U+0031")],
        )
        self.assertEqual(builder.protected_signature(normalized), builder.protected_signature(text))
        self.assertEqual(builder.reverse_operations(normalized, operations), text)

    def test_normalization_rejects_conversion_that_would_create_a_printf_token(self) -> None:
        with self.assertRaisesRegex(builder.NormalizationError, "protected/layout invariant"):
            builder.normalization_operations("％s", {"％": "%"})

    def test_middle_dot_direction_is_locked_to_switch_v22_to_v23(self) -> None:
        evidence = {
            "observed_fullwidth_map": {"U+FF11": "U+0031"},
            "observed_korean_middle_dot_map": {"U+00B7": "U+30FB"},
        }
        mapping = builder.map_from_evidence(evidence)
        self.assertEqual(mapping["·"], chr(0x30FB))
        output, operations = builder.normalization_operations(
            "가·나", mapping, builder.operation_types_from_map(mapping)
        )
        self.assertEqual(output, "가" + chr(0x30FB) + "나")
        self.assertEqual(
            operations,
            [
                {
                    "operation_type": "korean_middle_dot_to_japanese_middle_dot",
                    "char_index": 1,
                    "from": "U+00B7",
                    "to": "U+30FB",
                }
            ],
        )
        self.assertEqual(builder.reverse_operations(output, operations), "가·나")
        with self.assertRaises(builder.NormalizationError):
            builder.map_from_evidence(
                {
                    "observed_fullwidth_map": {"U+FF11": "U+0031"},
                    "observed_korean_middle_dot_map": {"U+30FB": "U+00B7"},
                }
            )

    def test_reverse_rejects_stale_character_or_invalid_operation_type(self) -> None:
        operation = {
            "operation_type": "fullwidth_ascii",
            "char_index": 0,
            "from": "U+FF11",
            "to": "U+0031",
        }
        with self.assertRaises(builder.NormalizationError):
            builder.reverse_operations("2", [operation])
        operation["operation_type"] = "wrong_direction"
        with self.assertRaises(builder.NormalizationError):
            builder.reverse_operations("1", [operation])

    def test_pinned_inputs_and_policy_are_not_generic_unicode_folding(self) -> None:
        self.assertEqual(len(builder.TARGETS), 14)
        self.assertFalse(any("/SC/" in value or value.startswith("RES_SC") for value in builder.TARGETS))
        self.assertEqual(
            builder.KOREAN_TO_JAPANESE_MIDDLE_DOT_MAP,
            {"·": chr(0x30FB)},
        )
        for pin in (builder.V09_ZIP_PIN, *builder.SWITCH_ZIP_PINS.values()):
            self.assertEqual(len(pin["sha256"]), 64)
            self.assertTrue(all(character in "0123456789ABCDEF" for character in pin["sha256"]))

    def test_in_memory_metadata_build_applies_fullwidth_only_and_defers_middle_dot(self) -> None:
        metadata = builder.make_metadata(
            builder.V09_ZIP, builder.SWITCH_V22_ZIP, builder.SWITCH_V23_ZIP
        )
        self.assertTrue(metadata["operations"])
        self.assertTrue(metadata["deferred_korean_middle_dot"]["operations"])
        self.assertEqual(
            metadata["automatic_policy"]["applied_fullwidth_ascii_map"],
            metadata["automatic_policy"]["observed_fullwidth_map"],
        )
        self.assertEqual(
            metadata["deferred_korean_middle_dot"]["mode"],
            "font_dependency_blocked_not_applied",
        )
        self.assertTrue(
            metadata["font_demand_impact"]["applied_fullwidth_ascii"][
                "all_evidenced_targets_mapped_in_all_live_jp_g1ns"
            ]
        )

    def test_output_path_rejects_outside_tmp_before_any_directory_is_created(self) -> None:
        with tempfile.TemporaryDirectory(prefix=".fullwidth-safe-output-", dir=builder.TMP_ROOT) as raw:
            tmp_root = Path(raw)
            outside = tmp_root.parent / "must-not-be-created" / "candidate.zip"
            with mock.patch.object(builder, "TMP_ROOT", tmp_root):
                with self.assertRaises(builder.NormalizationError):
                    builder.prepare_new_tmp_file(outside, "outside regression")
            self.assertFalse(outside.parent.exists())

    def test_output_path_rejects_mocked_reparse_component(self) -> None:
        with tempfile.TemporaryDirectory(prefix=".fullwidth-reparse-", dir=builder.TMP_ROOT) as raw:
            tmp_root = Path(raw)
            nested = tmp_root / "nested"
            nested.mkdir()

            def mocked_reparse(path: Path) -> str | None:
                return "junction" if Path(path) == nested else None

            with (
                mock.patch.object(builder, "TMP_ROOT", tmp_root),
                mock.patch.object(builder, "_reparse_kind", side_effect=mocked_reparse),
            ):
                with self.assertRaises(builder.NormalizationError):
                    builder.prepare_new_tmp_file(nested / "candidate.zip", "junction regression")

    def test_public_metadata_is_source_free_and_hash_gated(self) -> None:
        metadata = builder.read_metadata()
        validation = json.loads(builder.VALIDATION_PATH.read_text(encoding="utf-8"))
        builder.validate_metadata(metadata)
        self.assertTrue(builder.source_free(metadata))
        self.assertEqual(
            metadata["automatic_policy"]["candidate_application_scope"],
            "all_active_v0.9_korean_cells_with_per_coordinate_preimage_hash_gate",
        )
        self.assertEqual(
            metadata["automatic_policy"]["observed_korean_middle_dot_map"],
            {"U+00B7": "U+30FB"},
        )
        self.assertTrue(
            validation["checks"]["korean_middle_dot_direction_is_u00b7_to_u30fb"]
        )
        self.assertTrue(
            validation["checks"]["font_coverage_all_applied_fullwidth_ascii_targets_proven"]
        )
        self.assertTrue(
            validation["checks"]["korean_middle_dot_is_font_dependency_blocked_and_not_applied"]
        )


if __name__ == "__main__":
    unittest.main()
