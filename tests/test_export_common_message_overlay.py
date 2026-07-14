from __future__ import annotations

import json
import struct
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOOLS = PROJECT_ROOT / "KR_PATCH_WORK" / "tools"
sys.path.insert(0, str(TOOLS))

import build_common_message_overlay as common  # noqa: E402
import export_common_message_overlay as exporter  # noqa: E402
from nobu16_lz4 import decompress_wrapper, raw_lz4_compress_literal_only  # noqa: E402
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
    logical_size = unpadded_size - block_offset
    raw = bytearray(unpadded_size)
    struct.pack_into("<III", raw, 0, 1, block_offset, logical_size)
    struct.pack_into("<I", raw, block_offset + 0x0C, block_prefix_size)
    for entry_id, offset in enumerate(offsets):
        struct.pack_into("<I", raw, table_offset + entry_id * 4, offset)
    raw[table_offset + table_size :] = pool
    raw.extend(b"\x00" * ((-len(raw)) % 4))
    parsed = parse_message_table(bytes(raw))
    if parsed.texts != tuple(texts):
        raise AssertionError("invalid synthetic message-table fixture")
    return bytes(raw)


def wrap_raw(raw: bytes) -> bytes:
    prefix = bytes.fromhex("01 01 C4 C1 FA 7F 00 00")
    compressed = raw_lz4_compress_literal_only(raw)
    return prefix + struct.pack("<QQ", len(raw), len(compressed)) + compressed


class CommonMessageExporterFixture(unittest.TestCase):
    resource = "MSG_PK/SC/msgdata.bin"
    texts = {
        "SC": ["保留", "源氏", "太郎", "%s\r\n\x1bCA"],
        "EN": ["Keep", "Minamoto", "Taro", "%s\r\n\x1bCA"],
        "JP": ["保持", "みなもと", "たろう", "%s\r\n\x1bCA"],
    }

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.game_root = self.root / "game"
        self.stock_paths: dict[str, Path] = {}
        self.stocks: dict[str, bytes] = {}
        for language, texts in self.texts.items():
            raw = make_raw_message_table(list(texts))
            stock = wrap_raw(raw)
            path = self.game_root / f"MSG_PK/{language}/msgdata.bin"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(stock)
            self.stock_paths[language] = path
            self.stocks[language] = stock

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def batch(
        self,
        rows: list[dict[str, object]],
        languages: tuple[str, ...] = ("SC",),
        resource_name: str = "msgdata.bin",
    ) -> dict[str, object]:
        source_files = {
            language: {
                "path": f"MSG_PK/{language}/{resource_name}",
                "sha256": common.sha256_bytes(self.stocks[language]),
            }
            for language in languages
        }
        entries = []
        for row in rows:
            entry_id = int(row["id"])
            source = {
                language: self.texts[language][entry_id] for language in languages
            }
            source.update(row.get("source", {}))  # type: ignore[arg-type]
            entry: dict[str, object] = {
                "id": entry_id,
                "source": source,
                "ko": row["ko"],
            }
            if "status" in row:
                entry["status"] = row["status"]
            if "allow_edge_whitespace_change" in row:
                entry["allow_edge_whitespace_change"] = row[
                    "allow_edge_whitespace_change"
                ]
            entries.append(entry)
        return {
            "schema": exporter.PRIVATE_SCHEMA,
            "scope": "synthetic_officer_names",
            "version": "0.1",
            "base_languages": list(languages),
            "source_files": source_files,
            "entries": entries,
        }

    def write_batch(self, name: str, value: dict[str, object]) -> Path:
        path = self.root / name
        path.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        return path

    def test_deterministic_merge_is_source_free_and_builder_compatible(self) -> None:
        batch_a = self.write_batch(
            "a.json",
            self.batch(
                [
                    {"id": 2, "ko": "철수", "status": "reviewed"},
                    {"id": 1, "ko": "김"},
                ],
                ("SC", "EN", "JP"),
            ),
        )
        batch_b = self.write_batch(
            "b.json", self.batch([{"id": 1, "ko": "김"}], ("SC",))
        )
        first_path = self.root / "first.json"
        second_path = self.root / "second.json"
        first = exporter.export_overlay(
            [batch_b, batch_a],
            self.stock_paths,
            first_path,
            "officer-names-v1",
        )
        second = exporter.export_overlay(
            [batch_a, batch_b],
            self.stock_paths,
            second_path,
            "officer-names-v1",
        )

        self.assertEqual(first_path.read_bytes(), second_path.read_bytes())
        self.assertEqual(first["output_sha256"], second["output_sha256"])
        overlay_blob = first_path.read_bytes()
        for official_text in ("源氏", "太郎", "Minamoto", "Taro", "みなもと", "たろう"):
            self.assertNotIn(official_text.encode("utf-8"), overlay_blob)

        overlay = json.loads(overlay_blob)
        common.validate_overlay_shape(overlay)
        self.assertEqual([1, 2], [entry["id"] for entry in overlay["entries"]])
        self.assertEqual(2, overlay["entry_count"])
        self.assertEqual("reviewed", overlay["entries"][1]["status"])
        self.assertFalse(
            overlay["distribution_policy"]["contains_commercial_source_text"]
        )
        self.assertFalse(
            overlay["distribution_policy"]["contains_complete_game_resource"]
        )

        built = common.build_overlay(self.game_root, first_path, self.root / "built")
        _, built_raw = decompress_wrapper(Path(built["target_path"]).read_bytes())
        built_texts = parse_message_table(built_raw).texts
        self.assertEqual("김", built_texts[1])
        self.assertEqual("철수", built_texts[2])
        self.assertEqual(self.stocks["SC"], self.stock_paths["SC"].read_bytes())

    def test_identical_duplicates_dedupe_but_conflicts_fail(self) -> None:
        batch_a = self.write_batch(
            "a.json", self.batch([{"id": 1, "ko": "김"}, {"id": 1, "ko": "김"}])
        )
        output = self.root / "deduped.json"
        exporter.export_overlay(
            [batch_a], {"SC": self.stock_paths["SC"]}, output, "deduped-v1"
        )
        self.assertEqual(1, json.loads(output.read_text(encoding="utf-8"))["entry_count"])

        batch_b = self.write_batch(
            "b.json", self.batch([{"id": 1, "ko": "박"}])
        )
        with self.assertRaisesRegex(
            common.CommonMessageOverlayError, "conflicting duplicate"
        ):
            exporter.export_overlay(
                [batch_a, batch_b],
                {"SC": self.stock_paths["SC"]},
                self.root / "conflict.json",
                "conflict-v1",
            )

    def test_optional_en_jp_sources_and_stock_hashes_are_enforced(self) -> None:
        base = self.batch([{"id": 1, "ko": "김"}], ("SC", "EN", "JP"))

        missing_path = self.write_batch("missing.json", base)
        with self.assertRaisesRegex(common.CommonMessageOverlayError, "missing stock"):
            exporter.export_overlay(
                [missing_path],
                {"SC": self.stock_paths["SC"]},
                self.root / "missing-output.json",
                "missing-v1",
            )

        wrong_source = deepcopy(base)
        wrong_source["entries"][0]["source"]["EN"] = "Wrong"  # type: ignore[index]
        wrong_source_path = self.write_batch("wrong-source.json", wrong_source)
        with self.assertRaisesRegex(common.CommonMessageOverlayError, "EN source mismatch"):
            exporter.export_overlay(
                [wrong_source_path],
                self.stock_paths,
                self.root / "wrong-source-output.json",
                "wrong-source-v1",
            )

        wrong_hash = deepcopy(base)
        wrong_hash["source_files"]["JP"]["sha256"] = "0" * 64  # type: ignore[index]
        wrong_hash_path = self.write_batch("wrong-hash.json", wrong_hash)
        with self.assertRaisesRegex(common.CommonMessageOverlayError, "JP stock packed"):
            exporter.export_overlay(
                [wrong_hash_path],
                self.stock_paths,
                self.root / "wrong-hash-output.json",
                "wrong-hash-v1",
            )

    def test_invalid_private_data_and_invariants_fail_closed(self) -> None:
        cases: list[tuple[str, dict[str, object], str]] = []

        no_op = self.batch([{"id": 1, "ko": self.texts["SC"][1]}])
        cases.append(("no-op", no_op, "no-op"))

        bad_invariant = self.batch(
            [{"id": 3, "ko": "%d\r\n\x1bCA"}], ("SC",)
        )
        cases.append(("invariant", bad_invariant, "invariant mismatch"))

        hidden_field = self.batch([{"id": 1, "ko": "김"}])
        hidden_field["entries"][0]["note"] = "hidden"  # type: ignore[index]
        cases.append(("hidden", hidden_field, "keys differ"))

        wrong_resource = self.batch([{"id": 1, "ko": "김"}])
        wrong_resource["source_files"]["SC"]["path"] = "MSG_PK/SC/msgui.bin"  # type: ignore[index]
        cases.append(("resource", wrong_resource, "must be one of"))

        for label, batch, message in cases:
            with self.subTest(label=label):
                path = self.write_batch(f"{label}.json", batch)
                with self.assertRaisesRegex(common.CommonMessageOverlayError, message):
                    exporter.export_overlay(
                        [path],
                        {"SC": self.stock_paths["SC"]},
                        self.root / f"{label}-output.json",
                        f"{label}-v1",
                    )

    def test_msgev_is_supported_and_mixed_resources_are_rejected(self) -> None:
        msgev_stock = self.game_root / "MSG_PK/SC/msgev.bin"
        msgev_stock.parent.mkdir(parents=True, exist_ok=True)
        msgev_stock.write_bytes(self.stocks["SC"])
        msgev_batch = self.write_batch(
            "msgev.json",
            self.batch([{"id": 1, "ko": "김"}], ("SC",), "msgev.bin"),
        )
        msgdata_batch = self.write_batch(
            "msgdata.json", self.batch([{"id": 2, "ko": "철수"}], ("SC",))
        )

        output = self.root / "msgev-overlay.json"
        exporter.export_overlay(
            [msgev_batch], {"SC": msgev_stock}, output, "msgev-v1"
        )
        self.assertEqual(
            "MSG_PK/SC/msgev.bin",
            json.loads(output.read_text(encoding="utf-8"))["resource"],
        )
        with self.assertRaisesRegex(common.CommonMessageOverlayError, "same common-message"):
            exporter.export_overlay(
                [msgdata_batch, msgev_batch],
                {"SC": self.stock_paths["SC"]},
                self.root / "mixed.json",
                "mixed-v1",
            )

    def test_edge_whitespace_change_requires_explicit_opt_in(self) -> None:
        denied = self.write_batch(
            "edge-denied.json",
            self.batch([{"id": 1, "ko": "김 "}]),
        )
        with self.assertRaisesRegex(
            common.CommonMessageOverlayError,
            "trailing_whitespace",
        ):
            exporter.export_overlay(
                [denied],
                {"SC": self.stock_paths["SC"]},
                self.root / "edge-denied-output.json",
                "edge-denied-v1",
            )

        allowed = self.write_batch(
            "edge-allowed.json",
            self.batch(
                [
                    {
                        "id": 1,
                        "ko": "김 ",
                        "allow_edge_whitespace_change": True,
                    }
                ]
            ),
        )
        output = self.root / "edge-allowed-output.json"
        exporter.export_overlay(
            [allowed],
            {"SC": self.stock_paths["SC"]},
            output,
            "edge-allowed-v1",
        )
        entry = json.loads(output.read_text(encoding="utf-8"))["entries"][0]
        self.assertTrue(entry["allow_edge_whitespace_change"])
        self.assertEqual("김 ", entry["ko"])


if __name__ == "__main__":
    unittest.main()
