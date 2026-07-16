from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "steam_jp_switch_v23_linebreak_v1_builder",
    HERE / "build_steam_jp_switch_v23_linebreak_v1.py",
)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class SteamJpSwitchV23LinebreakTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inputs = builder.load_inputs(
            builder.DEFAULT_BASELINE_ZIP,
            builder.DEFAULT_SWITCH_V13_ZIP,
            builder.DEFAULT_SWITCH_V22_ZIP,
            builder.DEFAULT_SWITCH_V23_ZIP,
            builder.DEFAULT_SWITCH_V24_ZIP,
        )
        cls.overlay, cls.auxiliary = builder.make_overlay(cls.inputs)
        cls.fullwidth_metadata = builder.read_fullwidth_metadata(
            builder.DEFAULT_FULLWIDTH_METADATA_PATH
        )

    def test_01_switch_delta_and_reference_direction_are_pinned(self) -> None:
        parsed = self.inputs["parsed"]
        linebreak_ids, handoff_ids, deferred_ids = builder.classify_switch_v23_delta(
            parsed["switch_v22"][2].texts,
            parsed["switch_v23"][2].texts,
        )
        self.assertEqual(builder.EXPECTED["v23_linebreak_rows"], len(linebreak_ids))
        self.assertEqual(builder.EXPECTED["fullwidth_handoff_rows"], len(handoff_ids))
        self.assertEqual(builder.EXPECTED["deferred_rows"], len(deferred_ids))
        self.assertEqual(
            builder.EXPECTED["v23_linebreak_tokens"],
            sum(len(builder.linebreaks(parsed["switch_v22"][2].texts[entry_id])) for entry_id in linebreak_ids),
        )
        self.assertEqual(
            chr(0x30FB),
            builder.switch_reference_nonlayout_normalized(chr(0x00B7)),
        )
        self.assertEqual(
            chr(0x30FB),
            builder.switch_reference_nonlayout_normalized(chr(0x30FB)),
        )

    def test_02_640_operation_partition_and_public_target_contract(self) -> None:
        entries = self.overlay["entries"]
        kinds = Counter(entry["operation"] for entry in entries)
        self.assertEqual(builder.EXPECTED["operation_count"], len(entries))
        self.assertEqual(
            builder.EXPECTED["exact_operations"],
            kinds["switch_v23_coordinate_exact_linebreak_to_ascii_space"],
        )
        self.assertEqual(
            builder.EXPECTED["rebased_operations"],
            kinds["switch_v23_rebased_linebreak_to_ascii_space"],
        )
        self.assertEqual(
            builder.EXPECTED["residual_translation_repairs"],
            kinds["manual_korean_residual_translation_and_linebreak_repair"],
        )
        residual_ids = [
            entry["id"]
            for entry in entries
            if entry["operation"] == "manual_korean_residual_translation_and_linebreak_repair"
        ]
        self.assertEqual(
            builder.EXPECTED["residual_translation_repair_ids_sha256"],
            builder.id_vector_hash(residual_ids),
        )
        self.assertEqual(
            builder.EXPECTED["v23_linebreak_tokens"],
            sum(entry["linebreak_token_count"] for entry in entries),
        )
        for entry in entries:
            self.assertIsNotNone(builder.HANGUL_RE.search(entry["ko"]))
            self.assertIsNone(builder.LEXICAL_SOURCE_SCRIPT_RE.search(entry["ko"]))
        builder.source_free(self.overlay, "test overlay")
        builder.source_free(self.auxiliary["review"], "test review")

    def test_03_each_preimage_hash_and_operation_semantics_hold(self) -> None:
        v09 = self.inputs["parsed"]["steam_v09"][2].texts
        v22 = self.inputs["parsed"]["switch_v22"][2].texts
        v23 = self.inputs["parsed"]["switch_v23"][2].texts
        for entry in self.overlay["entries"]:
            entry_id = entry["id"]
            target, operation, count = builder.validate_linebreak_overlay_entry(v09[entry_id], entry)
            self.assertEqual(entry["ko"], target)
            self.assertEqual(entry["operation"], operation)
            self.assertEqual(entry["linebreak_token_count"], count)
            if operation == "manual_korean_residual_translation_and_linebreak_repair":
                rebuilt = builder.manual_koreanize_switch_v23_residual(entry_id, v23[entry_id])
                self.assertEqual(target, rebuilt)
                builder.assert_manual_korean_residual_translation_and_linebreak_repair(
                    v09[entry_id], v22[entry_id], v23[entry_id], target, f"test residual {entry_id}"
                )

    def test_04_linebreak_candidate_domain_is_exact(self) -> None:
        candidate, metadata = builder.apply_overlay_to_baseline(
            self.inputs["packed"]["steam_v09"], self.overlay
        )
        self.assertEqual(builder.EXPECTED["operation_count"], metadata["changed_entry_count"])
        self.assertEqual(builder.EXPECTED["v23_linebreak_tokens"], metadata["linebreak_tokens_replaced"])
        self.assertTrue(metadata["raw_parse_rebuild_valid"])
        self.assertTrue(metadata["wrapper_prefix_preserved"])
        _header, raw = builder.decompress_wrapper(candidate)
        candidate_table = builder.parse_message_table(raw)
        base_table = self.inputs["parsed"]["steam_v09"][2]
        changed = {
            entry_id
            for entry_id, (before, after) in enumerate(zip(base_table.texts, candidate_table.texts, strict=True))
            if before != after
        }
        self.assertEqual(
            {entry["id"] for entry in self.overlay["entries"]},
            changed,
        )

    def test_05_safe_fullwidth_intersection_and_composed_candidate(self) -> None:
        report = builder.fullwidth_linebreak_intersection(self.overlay, self.fullwidth_metadata)
        self.assertTrue(report["safe_ascii_only_fullwidth_model"])
        self.assertFalse(report["middle_dot_composition_included"])
        self.assertTrue(report["middle_dot_font_prerequisite_deferred"])
        self.assertEqual(0, report["manual_residual_intersection_count"])
        self.assertEqual(
            builder.EXPECTED["safe_fullwidth_metadata_sha256"],
            report["fullwidth_model_sha256"],
        )
        self.assertEqual(
            builder.EXPECTED["safe_fullwidth_ev_strdata_operation_count"],
            report["fullwidth_ev_strdata_operation_count"],
        )
        self.assertEqual(
            builder.EXPECTED["safe_fullwidth_intersection_count"],
            report["intersection_entry_count"],
        )
        self.assertEqual(
            builder.EXPECTED["safe_fullwidth_intersection_ids_sha256"],
            report["intersection_entry_ids_sha256"],
        )
        candidate, metadata = builder.apply_composed_fullwidth_and_linebreak_to_baseline(
            self.inputs["packed"]["steam_v09"], self.overlay, self.fullwidth_metadata
        )
        self.assertEqual(report, metadata["fullwidth_linebreak_composition"])
        self.assertFalse(metadata["fullwidth_operations_embedded_in_linebreak_overlay"])
        self.assertEqual(builder.EXPECTED["v23_linebreak_tokens"], metadata["linebreak_tokens_replaced"])
        self.assertTrue(metadata["raw_parse_rebuild_valid"])
        self.assertGreaterEqual(metadata["changed_entry_count"], builder.EXPECTED["operation_count"])
        self.assertIsInstance(candidate, bytes)

    def test_06_public_artifacts_are_canonical_source_free_and_deterministic(self) -> None:
        generated = builder.generate_public()
        verified = builder.verify()
        self.assertEqual("PASS", generated["status"])
        self.assertTrue(verified["deterministic_ab_equal"])
        self.assertEqual(
            generated["fullwidth_linebreak_composition"],
            verified["fullwidth_linebreak_composition"],
        )
        for path in (builder.OVERLAY_PATH, builder.REVIEW_PATH, builder.VALIDATION_PATH):
            value = json.loads(path.read_text(encoding="utf-8"))
            builder.source_free(value, f"test {path.name}")
            self.assertEqual(builder.canonical_json_bytes(value), path.read_bytes())

    def test_07_no_installed_game_write_contract(self) -> None:
        validation = builder.expected_artifacts()[2]
        self.assertFalse(validation["checks"]["installed_game_file_written"])
        self.assertFalse(validation["checks"]["switch_binary_written"])
        self.assertFalse(validation["checks"]["release_asset_written"])
        self.assertTrue(validation["checks"]["all_public_targets_korean_only"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
