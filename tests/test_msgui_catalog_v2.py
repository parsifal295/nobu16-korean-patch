from __future__ import annotations

import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS = PROJECT_ROOT / "KR_PATCH_WORK" / "tools"
sys.path.insert(0, str(TOOLS))

import msgui_catalog_v2 as catalog  # noqa: E402
import build_file_only_msg_recipe as message_recipe  # noqa: E402
import export_public_translation_overlay as overlay_exporter  # noqa: E402
import verify_msgui_asymmetric_v02 as asymmetric_verifier  # noqa: E402


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

    def test_unqualified_line_break_override_is_rejected(self) -> None:
        source = "첫 줄\n둘째 줄"
        self.assertTrue(catalog.compare_invariants(source, "한 줄", set()))
        issues = catalog.compare_invariants(source, "한 줄", {"line_breaks"})
        self.assertTrue(any("unsupported invariant override" in issue for issue in issues))
        self.assertTrue(any(issue.startswith("line_breaks:") for issue in issues))

    def test_jp_reference_override_preserves_printf_and_line_break_contract(self) -> None:
        source_sc = " "
        references = {"JP": "%s와 %s가 선택됨\n해제 확인"}
        replacement = "%s와(과) %s이(가) 선택되어 있습니다.\n해제하시겠습니까?"
        overrides = {"printf:JP", "line_breaks:JP"}
        self.assertEqual(
            [],
            catalog.compare_invariants(
                source_sc, replacement, overrides, references
            ),
        )
        issues = catalog.compare_invariants(
            source_sc, "%s 하나만 남음", overrides, references
        )
        self.assertTrue(any(issue.startswith("printf:") for issue in issues))
        self.assertTrue(any(issue.startswith("line_breaks:") for issue in issues))

    def test_unknown_or_unpinned_override_is_rejected(self) -> None:
        issues = catalog.compare_invariants(" ", "%s", {"printf:XX"}, {})
        self.assertTrue(any("unsupported invariant override" in issue for issue in issues))


class TranslationStateTests(unittest.TestCase):
    def test_whitespace_only_noop_is_never_buildable(self) -> None:
        structural = {language: " " for language in catalog.LANGUAGES}
        asymmetric = {language: " " for language in catalog.LANGUAGES}
        asymmetric["JP"] = "表示文"
        self.assertEqual(
            ("empty", ""),
            catalog.canonical_translation_state(structural, "translated", "\u3000"),
        )
        self.assertEqual(
            ("untranslated", ""),
            catalog.canonical_translation_state(asymmetric, "translated", " "),
        )

    def test_real_translation_keeps_requested_status(self) -> None:
        source = {language: " " for language in catalog.LANGUAGES}
        self.assertEqual(
            ("reviewed", "성명 표시"),
            catalog.canonical_translation_state(source, "reviewed", "성명 표시"),
        )

    def test_zero_width_or_combining_only_text_is_not_buildable(self) -> None:
        source = {language: " " for language in catalog.LANGUAGES}
        source["JP"] = "表示文"
        for invisible in ("\u200b", "\ufeff", "\u0301"):
            self.assertFalse(catalog.has_semantic_text(invisible))
            self.assertEqual(
                ("untranslated", ""),
                catalog.canonical_translation_state(source, "translated", invisible),
            )
        self.assertTrue(catalog.has_semantic_text("\ue024"))


class PublicOverlayExporterTests(unittest.TestCase):
    @staticmethod
    def fixture() -> tuple[dict[str, object], list[dict[str, object]]]:
        source = {"EN": "Source", "JP": "表示", "SC": "来源", "TC": "來源"}
        meta = {
            "string_count": 1,
            "source_files": {
                "SC": {"sha256": "1" * 64, "raw_sha256": "2" * 64}
            },
        }
        rows = [
            {
                "id": 0,
                "source": source,
                "source_utf16le_sha256": {
                    language: catalog.text_hash(text) for language, text in source.items()
                },
            }
        ]
        return meta, rows

    @staticmethod
    def args(root: Path) -> argparse.Namespace:
        return argparse.Namespace(
            meta=root / "meta.json",
            catalog=root / "catalog.jsonl",
            translations=root / "translations",
            overlay_id="test-overlay",
            max_id=None,
            output=root / "public.json",
            report=None,
        )

    @staticmethod
    def public_overlay_fixture() -> dict[str, object]:
        return {
            "schema": catalog.OVERLAY_SCHEMA,
            "overlay_id": "test-overlay",
            "resource": "msgui",
            "base_language": "SC",
            "entry_count": 1,
            "skipped_whitespace_entry_count": 0,
            "distribution_policy": {
                "contains_commercial_source_text": False,
                "contains_complete_game_resource": False,
                "include_in_public_patch": True,
            },
            "stock_sc": {
                "packed_sha256": "1" * 64,
                "raw_sha256": "2" * 64,
                "string_count": 1,
            },
            "defaults": {"status": "translated"},
            "development_batch_provenance": [
                {
                    "file": "01.json",
                    "sha256": "3" * 64,
                    "accepted_entries": 1,
                    "skipped_whitespace_entries": 0,
                }
            ],
            "entries": [
                {
                    "id": 0,
                    "source_sc_utf16le_sha256": "4" * 64,
                    "ko": "번역",
                }
            ],
        }

    def test_strict_json_rejects_case_colliding_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "overlay.json"
            path.write_text('{"schema":1,"Schema":2}', encoding="utf-8")
            with self.assertRaises(catalog.CatalogError):
                catalog.load_json_strict(path)

    def test_public_overlay_shape_rejects_unknown_entry_field(self) -> None:
        overlay = self.public_overlay_fixture()
        catalog.validate_translation_overlay_shape(overlay)
        overlay["entries"][0]["source_sc"] = "상용 원문"  # type: ignore[index]
        with self.assertRaises(catalog.CatalogError):
            catalog.validate_translation_overlay_shape(overlay)

    def test_public_overlay_shape_rejects_freeform_metadata(self) -> None:
        overlay = self.public_overlay_fixture()
        overlay["entries"][0]["priority"] = "private source text"  # type: ignore[index]
        with self.assertRaises(catalog.CatalogError):
            catalog.validate_translation_overlay_shape(overlay)

        overlay = self.public_overlay_fixture()
        overlay["entries"][0]["status"] = "reviewed"  # type: ignore[index]
        overlay["entries"][0]["invariant_overrides"] = [  # type: ignore[index]
            "printf:JP",
            "printf:JP",
        ]
        with self.assertRaises(catalog.CatalogError):
            catalog.validate_translation_overlay_shape(overlay)

    def test_public_overlay_shape_reconciles_skipped_provenance(self) -> None:
        overlay = self.public_overlay_fixture()
        overlay["skipped_whitespace_entry_count"] = 1
        with self.assertRaises(catalog.CatalogError):
            catalog.validate_translation_overlay_shape(overlay)

    def test_loader_ignores_legacy_non_msgui_batches(self) -> None:
        legacy_msgui = {
            "schema": overlay_exporter.LEGACY_SCHEMA,
            "source_files": {"SC": {"path": "MSG_PK/SC/msgui.bin"}},
            "entries": [],
        }
        legacy_msgdata = {
            "schema": overlay_exporter.LEGACY_SCHEMA,
            "source_files": {"SC": {"path": "MSG_PK\\SC\\msgdata.bin"}},
            "entries": [],
        }
        current_msgui = {
            "schema": catalog.BATCH_SCHEMA,
            "resource": "msgui",
            "base_language": "SC",
            "entries": [],
        }
        current_msgev = {
            "schema": catalog.BATCH_SCHEMA,
            "resource": "msgev",
            "base_language": "SC",
            "entries": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            translations = root / "translations"
            translations.mkdir()
            fixtures = {
                "01_ui_legacy.json": legacy_msgui,
                "02_data_legacy.json": legacy_msgdata,
                "03_ui_current.json": current_msgui,
                "04_event_current.json": current_msgev,
            }
            for name, value in fixtures.items():
                (translations / name).write_text(json.dumps(value), encoding="utf-8")
            loaded = overlay_exporter.load_batches(translations)
        self.assertEqual(
            ["01_ui_legacy.json", "03_ui_current.json"],
            [path.name for path, _ in loaded],
        )

    def test_exporter_requires_reviewed_status_for_overrides(self) -> None:
        meta, rows = self.fixture()
        batch = {
            "schema": catalog.BATCH_SCHEMA,
            "entries": [
                {
                    "id": 0,
                    "ko": "번역",
                    "status": "translated",
                    "invariant_overrides": ["printf:JP"],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            batch_path = root / "01.json"
            batch_path.write_text("{}", encoding="utf-8")
            with mock.patch.object(catalog, "load_catalog", return_value=(meta, rows)), mock.patch.object(
                overlay_exporter, "load_batches", return_value=[(batch_path, batch)]
            ):
                with self.assertRaises(catalog.CatalogError):
                    overlay_exporter.export(self.args(root))

    def test_later_blank_batch_withdraws_earlier_translation(self) -> None:
        meta, rows = self.fixture()
        first = {
            "schema": catalog.BATCH_SCHEMA,
            "entries": [{"id": 0, "ko": "번역", "status": "translated"}],
        }
        second = {
            "schema": catalog.BATCH_SCHEMA,
            "entries": [{"id": 0, "ko": " ", "status": "translated"}],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first_path = root / "01.json"
            second_path = root / "02.json"
            first_path.write_text("{}", encoding="utf-8")
            second_path.write_text("{}", encoding="utf-8")
            with mock.patch.object(catalog, "load_catalog", return_value=(meta, rows)), mock.patch.object(
                overlay_exporter,
                "load_batches",
                return_value=[(first_path, first), (second_path, second)],
            ):
                overlay_exporter.export(self.args(root))
            exported = json.loads((root / "public.json").read_text(encoding="utf-8"))
            self.assertEqual(0, exported["entry_count"])
            self.assertEqual([], exported["entries"])
            self.assertEqual(1, exported["skipped_whitespace_entry_count"])


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
    def test_asymmetric_v02_source_free_candidate(self) -> None:
        project = PROJECT_ROOT / "KR_PATCH_WORK"
        candidate = project / "workstreams" / "msgui_full" / "asymmetric_v02"
        if not candidate.exists():
            self.skipTest("MSGUI asymmetric v0.2 candidate is absent")
        report = asymmetric_verifier.verify(project)
        self.assertTrue(report["valid"])
        self.assertEqual(86, report["new_translations"])
        self.assertEqual(3922, report["message_operations"])
        self.assertFalse(report["release_eligible"])

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
        catalog.validate_translation_overlay_shape(overlay)
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
            self.assertTrue(
                catalog.has_semantic_text(entry["ko"]),
                f"non-semantic public row: {entry['id']}",
            )

        by_id = {entry["id"]: entry for entry in overlay["entries"]}
        self.assertEqual("성명 표시", by_id[2498]["ko"])
        self.assertEqual(["printf:JP"], by_id[3784]["invariant_overrides"])
        self.assertEqual(
            ["printf:JP", "line_breaks:JP"],
            by_id[3855]["invariant_overrides"],
        )

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
