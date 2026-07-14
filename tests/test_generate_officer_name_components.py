from __future__ import annotations

import argparse
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS = PROJECT_ROOT / "KR_PATCH_WORK" / "tools"
sys.path.insert(0, str(TOOLS))

import build_common_message_overlay as common  # noqa: E402
import generate_officer_name_components as components  # noqa: E402
from nobu16_lz4 import raw_lz4_compress_literal_only  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


def make_raw_message_table(texts: list[str]) -> bytes:
    block_offset = 0x0C
    block_prefix_size = 0x14
    table_offset = block_offset + block_prefix_size
    table_size = len(texts) * 4
    offsets: list[int] = []
    pool = bytearray()
    relative = table_size
    for text in texts:
        encoded = text.encode("utf-16le") + b"\x00\x00"
        offsets.append(relative)
        pool.extend(encoded)
        relative += len(encoded)
    unpadded_size = table_offset + table_size + len(pool)
    raw = bytearray(unpadded_size)
    struct.pack_into("<III", raw, 0, 1, block_offset, unpadded_size - block_offset)
    struct.pack_into("<I", raw, block_offset + 0x0C, block_prefix_size)
    for entry_id, offset in enumerate(offsets):
        struct.pack_into("<I", raw, table_offset + entry_id * 4, offset)
    raw[table_offset + table_size :] = pool
    raw.extend(b"\x00" * ((-len(raw)) % 4))
    parsed = parse_message_table(bytes(raw))
    if parsed.texts != tuple(texts):
        raise AssertionError("bad synthetic table")
    return bytes(raw)


def wrap_raw(raw: bytes) -> bytes:
    prefix = bytes.fromhex("01 01 C4 C1 FA 7F 00 00")
    compressed = raw_lz4_compress_literal_only(raw)
    return prefix + struct.pack("<QQ", len(raw), len(compressed)) + compressed


class OfficerComponentFixture(unittest.TestCase):
    texts = {
        "SC": ["织田", "信长", "小田", "信忠", "织田", "甲", "乙丙", "甲乙", "丙", "保留"],
        "EN": ["Oda", "Nobunaga", "Oda", "Nobutada", "Oda", "S", "G", "S", "G", "Keep"],
        "JP": ["織田", "信長", "小田", "信忠", "織田", "甲", "乙丙", "甲乙", "丙", "保持"],
    }

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.stock_paths: dict[str, Path] = {}
        for language in components.LANGUAGES:
            stock = wrap_raw(make_raw_message_table(self.texts[language]))
            path = self.root / f"stock/{language}/msgdata.bin"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(stock)
            self.stock_paths[language] = path

        self.full_entries = [
            {
                "id": 0,
                "source": {"SC": "织田信长", "EN": "Nobunaga Oda", "JP": "織田信長"},
                "ko": "오다 노부나가",
                "status": "translated",
            },
            {
                "id": 1,
                "source": {"SC": "甲乙丙", "EN": "G S", "JP": "甲乙丙"},
                "ko": "가 나",
                "status": "translated",
            },
        ]
        source_files = {
            language: {
                "path": f"MSG_PK/{language}/msgev.bin",
                "sha256": "A" * 64,
            }
            for language in components.LANGUAGES
        }
        self.full_catalog = self.root / "full.json"
        self.full_catalog.write_text(
            json.dumps(
                {
                    "schema": components.PRIVATE_SCHEMA,
                    "scope": "msgev_officer_names_0000_2399",
                    "version": "0.1",
                    "base_languages": ["SC", "EN", "JP"],
                    "source_files": source_files,
                    "entries": self.full_entries,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        self.full_report = self.root / "full-report.json"
        self.full_report.write_text(
            json.dumps(
                {
                    "schema": components.FULL_REPORT_SCHEMA,
                    "officer_count": 2,
                    "generated_count": 2,
                    "unresolved_count": 0,
                    "method_counts": {"fixture": 2},
                    "rows": [
                        {
                            "id": row["id"],
                            "jp": row["source"]["JP"],
                            "en": row["source"]["EN"],
                            "ko": row["ko"],
                            "method": "fixture",
                        }
                        for row in self.full_entries
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def args(
        self,
        root: Path,
        table_inputs: dict[str, Path] | None = None,
    ) -> argparse.Namespace:
        table_inputs = table_inputs or self.stock_paths
        return argparse.Namespace(
            full_catalog=self.full_catalog,
            full_report=self.full_report,
            msgdata_sc=table_inputs["SC"],
            msgdata_en=table_inputs["EN"],
            msgdata_jp=table_inputs["JP"],
            stock_sc=self.stock_paths["SC"] if table_inputs is not self.stock_paths else None,
            stock_en=self.stock_paths["EN"] if table_inputs is not self.stock_paths else None,
            stock_jp=self.stock_paths["JP"] if table_inputs is not self.stock_paths else None,
            private_output=root / "private.json",
            public_output=root / "public.json",
            report_output=root / "report.json",
            verification_root=root / "verification",
            public_build_output_root=root / "workstream-public",
            overlay_id="fixture-components-v0.1",
            version="0.1",
            expected_officer_count=2,
        )

    def write_jsonl_inputs(self) -> dict[str, Path]:
        result: dict[str, Path] = {}
        for language in components.LANGUAGES:
            path = self.root / f"jsonl/msgdata.{language}.jsonl"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                "".join(
                    json.dumps(
                        {"id": entry_id, "text": text, "translation": ""},
                        ensure_ascii=False,
                        separators=(",", ":"),
                    )
                    + "\n"
                    for entry_id, text in enumerate(self.texts[language])
                ),
                encoding="utf-8",
            )
            result[language] = path
        return result

    def test_end_to_end_is_conservative_source_free_and_deterministic(self) -> None:
        first_root = self.root / "first"
        public_build_root = first_root / "workstream-public"
        public_build_root.mkdir(parents=True)
        msgev_manifest = public_build_root / "msgev.build-manifest.json"
        msgev_recipe = public_build_root / "msgev_sc.recipe.json"
        msgev_manifest.write_bytes(b"existing-msgev-manifest")
        msgev_recipe.write_bytes(b"existing-msgev-recipe")
        first = components.generate_components(self.args(first_root))

        private = json.loads((first_root / "private.json").read_text(encoding="utf-8"))
        public = json.loads((first_root / "public.json").read_text(encoding="utf-8"))
        self.assertEqual([0, 1, 4], [entry["id"] for entry in private["entries"]])
        self.assertNotIn(2, [entry["id"] for entry in private["entries"]])
        self.assertEqual("오다 ", private["entries"][0]["ko"])
        self.assertTrue(private["entries"][0]["allow_edge_whitespace_change"])
        self.assertEqual("노부나가", private["entries"][1]["ko"])
        self.assertNotIn("allow_edge_whitespace_change", private["entries"][1])
        self.assertEqual([0, 1, 4], [entry["id"] for entry in public["entries"]])
        self.assertEqual(3, public["entry_count"])
        self.assertEqual(1, first["matched_officer_count"])
        self.assertEqual(1, first["unresolved_officer_count"])
        self.assertEqual(
            {"ambiguous_exact_component_pairs": 1},
            first["unresolved_reason_counts"],
        )
        self.assertTrue(first["verification"]["recipe_replay_exact"])
        self.assertTrue(first["verification"]["build_a_b_byte_identical"])
        self.assertEqual(2, first["full_msgev_translated_officer_count"])
        self.assertEqual(0, first["full_msgev_unresolved_officer_count"])
        self.assertEqual(1, first["msgdata_split_excluded_officer_count"])
        self.assertTrue(
            first["msgdata_split_exclusions_leave_full_msgev_translation_intact"]
        )
        self.assertEqual(0, first["public_overlay"]["cjk_unified_ideograph_count"])
        self.assertFalse(first["public_overlay"]["source_original_fields_present"])
        self.assertTrue(
            first["public_build_artifacts"]["recipe_replays_tmp_target_exact"]
        )
        self.assertEqual(
            0,
            first["public_build_artifacts"]["manifest_cjk_unified_ideograph_count"],
        )
        self.assertEqual(
            0,
            first["public_build_artifacts"]["recipe_cjk_unified_ideograph_count"],
        )
        self.assertEqual(b"existing-msgev-manifest", msgev_manifest.read_bytes())
        self.assertEqual(b"existing-msgev-recipe", msgev_recipe.read_bytes())
        self.assertEqual(
            (first_root / "verification/build_a/msgdata.build-manifest.json").read_bytes(),
            (public_build_root / "msgdata.build-manifest.json").read_bytes(),
        )
        self.assertEqual(
            (first_root / "verification/build_a/msgdata_sc.recipe.json").read_bytes(),
            (public_build_root / "msgdata_sc.recipe.json").read_bytes(),
        )
        self.assertFalse((public_build_root / "MSG_PK/SC/msgdata.bin").exists())
        public_blob = (first_root / "public.json").read_bytes()
        self.assertEqual(0, components.count_cjk_unified(public_blob.decode("utf-8")))
        self.assertFalse(components.contains_source_original_fields(public))
        for source_text in ("织田", "信长", "織田", "信長", "Oda", "Nobunaga"):
            self.assertNotIn(source_text.encode("utf-8"), public_blob)

        jsonl_root = self.root / "jsonl-run"
        second = components.generate_components(
            self.args(jsonl_root, self.write_jsonl_inputs())
        )
        for name in ("private.json", "public.json", "report.json"):
            self.assertEqual(
                (first_root / name).read_bytes(),
                (jsonl_root / name).read_bytes(),
                name,
            )
        for name in ("msgdata.build-manifest.json", "msgdata_sc.recipe.json"):
            self.assertEqual(
                (first_root / "workstream-public" / name).read_bytes(),
                (jsonl_root / "workstream-public" / name).read_bytes(),
                name,
            )
        self.assertEqual(first["verification"], second["verification"])

    def test_component_translation_conflicts_reject_every_involved_officer(self) -> None:
        tables = {
            language: components.load_stock_table(
                language, self.stock_paths[language], None
            )
            for language in components.LANGUAGES
        }
        entries = [
            self.full_entries[0],
            {
                **self.full_entries[0],
                "id": 1,
                "ko": "오타 노부나가",
            },
        ]
        private, report = components.analyze_components(
            entries, {0: "fixture", 1: "fixture"}, tables
        )
        self.assertEqual([], private)
        self.assertEqual(0, report["matched_officer_count"])
        self.assertEqual(2, report["unresolved_officer_count"])
        self.assertEqual(
            {"component_translation_conflict": 2},
            report["unresolved_reason_counts"],
        )
        self.assertEqual([0, 4], [row["msgdata_id"] for row in report["component_conflicts"]])

    def test_regression_gate_checks_ids_recomposition_and_spacing(self) -> None:
        root = self.root / "regression"
        report = components.generate_components(self.args(root))
        private = json.loads((root / "private.json").read_text(encoding="utf-8"))
        tables = {
            language: components.load_stock_table(
                language, self.stock_paths[language], None
            )
            for language in components.LANGUAGES
        }
        expected = {
            0: {
                "ko": "오다 노부나가",
                "surname_ids": [0, 4],
                "given_ids": [1],
            }
        }
        checks = components.validate_regression_expectations(
            self.full_entries,
            report,
            private["entries"],
            tables,
            expected,
        )
        self.assertEqual("OK", checks[0]["sc_jp_en_recomposition"])
        self.assertEqual("OK", checks[0]["surname_spacing"])
        self.assertEqual("OK", checks[0]["given_spacing"])

        expected[0]["surname_ids"] = [2]
        with self.assertRaisesRegex(
            components.OfficerComponentError, "surname_ids differs"
        ):
            components.validate_regression_expectations(
                self.full_entries,
                report,
                private["entries"],
                tables,
                expected,
            )

    def test_stale_jsonl_is_rejected_before_outputs(self) -> None:
        jsonl = self.write_jsonl_inputs()
        rows = [
            json.loads(line)
            for line in jsonl["SC"].read_text(encoding="utf-8").splitlines()
        ]
        rows[0]["text"] = "다른 값"
        jsonl["SC"].write_text(
            "".join(
                json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
                for row in rows
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(
            components.OfficerComponentError, "does not match the pinned stock"
        ):
            components.generate_components(self.args(self.root / "bad", jsonl))
        self.assertFalse((self.root / "bad/public.json").exists())


if __name__ == "__main__":
    unittest.main()
