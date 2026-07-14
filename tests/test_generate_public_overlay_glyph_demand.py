from __future__ import annotations

import copy
import json
import sys
import unittest
import unicodedata
from pathlib import Path


PATCH_ROOT = Path(__file__).resolve().parents[1]
TOOLS = PATCH_ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import generate_public_overlay_glyph_demand as demand  # noqa: E402
import msgui_catalog_v2 as msgui_catalog  # noqa: E402


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_is_rejected(self) -> None:
        with self.assertRaisesRegex(demand.DemandError, "duplicate JSON key"):
            demand.loads_json_strict(b'{"schema":1,"schema":2}')

    def test_case_colliding_key_is_rejected(self) -> None:
        with self.assertRaisesRegex(demand.DemandError, "case-colliding JSON keys"):
            demand.loads_json_strict(b'{"schema":1,"Schema":2}')

    def test_nested_case_collision_is_rejected(self) -> None:
        with self.assertRaisesRegex(demand.DemandError, "case-colliding JSON keys"):
            demand.loads_json_strict(b'{"outer":{"id":1,"ID":2}}')


class TrackedOverlayTests(unittest.TestCase):
    @staticmethod
    def loaded(kind: str) -> tuple[demand.OverlaySpec, dict[str, object], bytes]:
        spec = demand.SPECS[kind]
        raw = spec.overlay_path.read_bytes()
        overlay = demand.loads_json_strict(raw, kind)
        return spec, overlay, raw

    def test_dialogue_overlay_and_demand_are_pinned(self) -> None:
        spec = demand.SPECS["dialogue"]
        value = demand.build_demand(spec.overlay_path, spec)
        self.assertEqual(demand.DEMAND_SCHEMA, value["schema"])
        source = value["source_overlay"]
        self.assertEqual(spec.overlay_sha256, source["sha256"])
        self.assertEqual(28, source["entry_count"])
        self.assertEqual((3202, 3229), (source["first_id"], source["last_id"]))
        self.assertEqual(
            demand.id_inventory_hash(tuple(range(3202, 3230))),
            source["ordered_ids_sha256"],
        )
        excluded = {
            item["codepoint"]: item["reason"]
            for item in value["excluded_font_tokens"]
        }
        self.assertEqual(
            {
                "U+001B": "ui_control",
                "U+0041": "ui_escape_sequence_component",
                "U+0042": "ui_escape_sequence_component",
                "U+0043": "ui_escape_sequence_component",
                "U+005A": "ui_escape_sequence_component",
            },
            excluded,
        )
        self.assertNotIn("\x1b", value["characters"])
        self.assertTrue(
            all(unicodedata.is_normalized("NFC", char) for char in value["characters"])
        )
        self.assertEqual(
            spec.output_path.read_bytes(), demand.encode_json(value)
        )

    def test_castle_overlay_and_demand_are_pinned_plain_hangul(self) -> None:
        spec = demand.SPECS["castle"]
        value = demand.build_demand(spec.overlay_path, spec)
        source = value["source_overlay"]
        self.assertEqual(spec.overlay_sha256, source["sha256"])
        self.assertEqual(392, source["entry_count"])
        self.assertEqual((9151, 9542), (source["first_id"], source["last_id"]))
        self.assertEqual(0, value["excluded_font_token_count"])
        self.assertEqual(value["character_count"], value["hangul_syllable_count"])
        self.assertTrue(
            all(0xAC00 <= ord(char) <= 0xD7A3 for char in value["characters"])
        )
        self.assertEqual(
            spec.output_path.read_bytes(), demand.encode_json(value)
        )

    def test_control_and_pua_filter_matches_msgui_catalog_v2(self) -> None:
        sample = "\x1bCA한 글\n\x01\x85\ue024A"
        self.assertEqual(
            msgui_catalog.renderable_characters(sample),
            demand.renderable_characters(sample),
        )
        raw = {char for char in sample if not char.isspace()}
        rendered = set(demand.renderable_characters(sample))
        self.assertEqual(
            msgui_catalog.font_exclusion_inventory(raw, rendered),
            demand.font_exclusion_inventory(raw, rendered),
        )

    def test_unknown_dialogue_root_or_entry_key_is_rejected(self) -> None:
        spec, overlay, _ = self.loaded("dialogue")
        root_mutation = copy.deepcopy(overlay)
        root_mutation["source_sc"] = "forbidden"
        with self.assertRaisesRegex(demand.DemandError, "dialogue root keys"):
            demand.validate_dialogue_overlay(root_mutation, spec)

        entry_mutation = copy.deepcopy(overlay)
        entry_mutation["entries"][0]["source_sc"] = "forbidden"
        with self.assertRaisesRegex(demand.DemandError, r"entries\[0\].*keys"):
            demand.validate_dialogue_overlay(entry_mutation, spec)

    def test_unknown_castle_root_or_entry_key_is_rejected(self) -> None:
        spec, overlay, _ = self.loaded("castle")
        root_mutation = copy.deepcopy(overlay)
        root_mutation["source_en"] = "forbidden"
        with self.assertRaisesRegex(demand.DemandError, "castle root keys"):
            demand.validate_castle_overlay(root_mutation, spec)

        entry_mutation = copy.deepcopy(overlay)
        entry_mutation["entries"][0]["source_en"] = "forbidden"
        with self.assertRaisesRegex(demand.DemandError, r"entries\[0\].*keys"):
            demand.validate_castle_overlay(entry_mutation, spec)

    def test_nfc_and_exact_inventory_are_enforced_before_hash_pin(self) -> None:
        dialogue_spec, dialogue, _ = self.loaded("dialogue")
        nfc_mutation = copy.deepcopy(dialogue)
        nfc_mutation["entries"][0]["ko"] = "\u1100\u1161"
        with self.assertRaisesRegex(demand.DemandError, "NFC-normalized"):
            demand.validate_dialogue_overlay(nfc_mutation, dialogue_spec)

        castle_spec, castle, _ = self.loaded("castle")
        inventory_mutation = copy.deepcopy(castle)
        inventory_mutation["entries"][0], inventory_mutation["entries"][1] = (
            inventory_mutation["entries"][1],
            inventory_mutation["entries"][0],
        )
        with self.assertRaisesRegex(demand.DemandError, "exact ordered range"):
            demand.validate_castle_overlay(inventory_mutation, castle_spec)

    def test_overlay_byte_pin_rejects_any_other_serialization(self) -> None:
        spec, overlay, _ = self.loaded("dialogue")
        repacked = json.dumps(overlay, ensure_ascii=False).encode("utf-8")
        with self.assertRaisesRegex(demand.DemandError, "does not match pinned"):
            demand.validate_overlay_bytes(repacked, spec, "repacked")


if __name__ == "__main__":
    unittest.main()
