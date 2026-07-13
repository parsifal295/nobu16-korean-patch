from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS = PROJECT_ROOT / "KR_PATCH_WORK" / "tools"
sys.path.insert(0, str(TOOLS))

import msgui_catalog_v2 as catalog  # noqa: E402
import build_file_only_msg_recipe as message_recipe  # noqa: E402


class InvariantTests(unittest.TestCase):
    def test_printf_sequence_is_order_sensitive(self) -> None:
        source = "%s의 병력 %3d"
        self.assertEqual([], catalog.compare_invariants(source, "%s 병력 %3d", set()))
        issues = catalog.compare_invariants(source, "%3d 병력 %s", set())
        self.assertTrue(any(issue.startswith("printf:") for issue in issues))

    def test_escape_and_private_icon_are_required(self) -> None:
        source = "\x1bCQ\ue024\x1bCZ 군비 중"
        issues = catalog.compare_invariants(source, "군비 중", set())
        self.assertTrue(any(issue.startswith("esc:") for issue in issues))
        self.assertTrue(any(issue.startswith("pua:") for issue in issues))

    def test_only_reviewed_line_breaks_may_be_overridden_by_merge_policy(self) -> None:
        source = "첫 줄\n둘째 줄"
        self.assertTrue(catalog.compare_invariants(source, "한 줄", set()))
        self.assertEqual([], catalog.compare_invariants(source, "한 줄", {"line_breaks"}))


class GlyphDemandTests(unittest.TestCase):
    def test_ui_escape_sequences_are_not_font_glyphs(self) -> None:
        rows = [{"status": "translated", "ko": "\x1bCQ\ue024\x1bCZ 한"}]
        demand = catalog.glyph_demand(rows)
        self.assertEqual(["U+D55C"], demand["codepoints"])
        self.assertEqual(6, demand["source_non_whitespace_character_count"])
        self.assertEqual(5, demand["excluded_font_token_count"])
        self.assertEqual(
            {
                "U+001B": "ui_control",
                "U+0043": "ui_escape_sequence_component",
                "U+0051": "ui_escape_sequence_component",
                "U+005A": "ui_escape_sequence_component",
                "U+E024": "game_private_icon",
            },
            {row["codepoint"]: row["reason"] for row in demand["excluded_font_tokens"]},
        )
        self.assertNotIn("U+001B", demand["codepoints"])
        self.assertNotIn("U+0043", demand["codepoints"])
        self.assertNotIn("U+0051", demand["codepoints"])
        self.assertNotIn("U+005A", demand["codepoints"])
        self.assertNotIn("U+E024", demand["codepoints"])


class CurrentArtifactTests(unittest.TestCase):
    def test_current_p3_catalog_is_valid(self) -> None:
        root = PROJECT_ROOT / "KR_PATCH_WORK" / "workstreams" / "msgui_full" / "catalog_v2"
        if not (root / "msgui.catalog.p3.jsonl").exists():
            self.skipTest("development catalog is intentionally absent from a public checkout")
        meta, rows = catalog.load_catalog(
            root / "msgui.meta.json", root / "msgui.catalog.p3.jsonl"
        )
        report = catalog.validate_catalog(meta, rows, None)
        self.assertTrue(report["valid"], report["errors"])
        self.assertEqual(279, report["buildable_count"])

    def test_public_overlay_omits_complete_source_text(self) -> None:
        public_dir = PROJECT_ROOT / "KR_PATCH_WORK" / "data" / "public"
        overlays = sorted(public_dir.glob("msgui_ko_*.json"))
        self.assertTrue(overlays, "no public MSGUI overlay found")
        overlay = json.loads(overlays[-1].read_text(encoding="utf-8"))
        self.assertEqual(catalog.OVERLAY_SCHEMA, overlay["schema"])
        self.assertFalse(
            overlay["distribution_policy"]["contains_commercial_source_text"]
        )
        self.assertFalse(
            overlay["distribution_policy"]["contains_complete_game_resource"]
        )
        allowed = {
            "id",
            "source_sc_utf16le_sha256",
            "ko",
            "status",
            "priority",
            "invariant_overrides",
        }
        self.assertEqual(overlay["entry_count"], len(overlay["entries"]))
        for entry in overlay["entries"]:
            self.assertLessEqual(set(entry), allowed)
            self.assertNotIn("source_en", entry)
            self.assertNotIn("source_sc", entry)

    def test_operation_index_tampering_is_rejected(self) -> None:
        operation_ids = [7]
        operation_ids_blob = json.dumps(operation_ids, separators=(",", ":")).encode("utf-8")
        recipe = {
            "schema": message_recipe.SCHEMA,
            "scope": "msgui_catalog_v2",
            "file_only": True,
            "language": "SC",
            "operations": [
                {
                    "id": 7,
                    "source_utf16le_sha256": "0" * 64,
                    "replacement": "시험",
                }
            ],
            "operation_index": {
                "count": 1,
                "ids_sha256": message_recipe.sha256_bytes(operation_ids_blob),
                "sorted_unique": True,
            },
        }
        recipe["operation_index"]["count"] += 1
        with tempfile.TemporaryDirectory() as directory:
            tampered = Path(directory) / "tampered.json"
            tampered.write_text(json.dumps(recipe, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(ValueError):
                message_recipe.load_recipe(tampered)


if __name__ == "__main__":
    unittest.main()
