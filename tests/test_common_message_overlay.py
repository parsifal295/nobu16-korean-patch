from __future__ import annotations

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
import build_file_only_msg_recipe as message_recipe  # noqa: E402
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


class CommonMessageOverlayFixture(unittest.TestCase):
    texts = ["保留", "源氏", "太郎", "%s\r\n\x1bCA\t"]
    resource = "MSG_PK/SC/msgdata.bin"

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.game_root = self.root / "game"
        self.stock_path = self.game_root / Path(self.resource)
        self.stock_path.parent.mkdir(parents=True)
        self.raw = make_raw_message_table(list(self.texts))
        self.stock = wrap_raw(self.raw)
        self.stock_path.write_bytes(self.stock)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def overlay(self) -> dict[str, object]:
        entries = [
            {
                "id": 1,
                "source_sc_utf16le_sha256": common.text_hash(self.texts[1]),
                "ko": "김",
            },
            {
                "id": 2,
                "source_sc_utf16le_sha256": common.text_hash(self.texts[2]),
                "ko": "철수",
                "status": "reviewed",
            },
        ]
        return {
            "schema": common.OVERLAY_SCHEMA,
            "overlay_id": "officer-name-probe-v1",
            "resource": self.resource,
            "base_language": "SC",
            "entry_count": len(entries),
            "distribution_policy": {
                "contains_commercial_source_text": False,
                "contains_complete_game_resource": False,
            },
            "stock_sc": {
                "size": len(self.stock),
                "packed_sha256": common.sha256_bytes(self.stock),
                "raw_size": len(self.raw),
                "raw_sha256": common.sha256_bytes(self.raw),
                "string_count": len(self.texts),
            },
            "defaults": {"status": "translated"},
            "entries": entries,
        }

    def write_overlay(self, value: dict[str, object], name: str = "overlay.json") -> Path:
        path = self.root / name
        path.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        return path

    def test_build_is_deterministic_source_free_and_recipe_replay_compatible(self) -> None:
        overlay_path = self.write_overlay(self.overlay())
        first = common.build_overlay(self.game_root, overlay_path, self.root / "out-a")
        second = common.build_overlay(self.game_root, overlay_path, self.root / "out-b")

        for key in ("target_path", "manifest_path", "recipe_path"):
            self.assertEqual(
                Path(first[key]).read_bytes(),
                Path(second[key]).read_bytes(),
                key,
            )

        target_blob = Path(first["target_path"]).read_bytes()
        manifest_blob = Path(first["manifest_path"]).read_bytes()
        recipe_blob = Path(first["recipe_path"]).read_bytes()
        for commercial_source in ("源氏", "太郎"):
            encoded = commercial_source.encode("utf-8")
            self.assertNotIn(encoded, manifest_blob)
            self.assertNotIn(encoded, recipe_blob)

        manifest = json.loads(manifest_blob)
        self.assertEqual(common.BUILD_SCHEMA, manifest["schema"])
        self.assertEqual(2, manifest["overlay_entry_count"])
        self.assertEqual(2, manifest["changed_count"])
        self.assertFalse(manifest["commercial_source_text_included"])
        self.assertFalse(manifest["installed_game_files_modified"])
        self.assertEqual([1, 2], [row["id"] for row in manifest["changed"]])

        recipe = message_recipe.load_recipe(Path(first["recipe_path"]))
        replayed, replayed_raw = message_recipe.apply_operations(
            self.stock, recipe["operations"], len(self.texts)
        )
        self.assertEqual(target_blob, replayed)
        self.assertEqual(recipe["target"]["raw_sha256"], common.sha256_bytes(replayed_raw))
        self.assertEqual([1, 2], [row["id"] for row in recipe["operations"]])
        self.assertEqual(self.stock, self.stock_path.read_bytes())

    def test_noop_entry_is_validated_but_not_emitted(self) -> None:
        overlay = self.overlay()
        overlay["entries"][0]["ko"] = self.texts[1]  # type: ignore[index]
        path = self.write_overlay(overlay)
        result = common.build_overlay(self.game_root, path, self.root / "out")
        manifest = json.loads(Path(result["manifest_path"]).read_text(encoding="utf-8"))
        recipe = json.loads(Path(result["recipe_path"]).read_text(encoding="utf-8"))
        self.assertEqual(2, manifest["overlay_entry_count"])
        self.assertEqual(1, manifest["changed_count"])
        self.assertEqual([2], [row["id"] for row in recipe["operations"]])

    def test_same_builder_accepts_msgev_resource(self) -> None:
        resource = "MSG_PK/SC/msgev.bin"
        stock_path = self.game_root / Path(resource)
        stock_path.parent.mkdir(parents=True, exist_ok=True)
        stock_path.write_bytes(self.stock)
        overlay = self.overlay()
        overlay["resource"] = resource
        path = self.write_overlay(overlay, "msgev-overlay.json")
        result = common.build_overlay(self.game_root, path, self.root / "msgev-out")
        recipe = json.loads(Path(result["recipe_path"]).read_text(encoding="utf-8"))
        self.assertEqual(resource, recipe["source"]["relative_path"])
        self.assertEqual("msgev_sc.recipe.json", Path(result["recipe_path"]).name)

    def test_all_stock_pins_are_enforced(self) -> None:
        mutations = {
            "size": len(self.stock) + 1,
            "packed_sha256": "0" * 64,
            "raw_size": len(self.raw) + 1,
            "raw_sha256": "0" * 64,
            "string_count": len(self.texts) + 1,
        }
        for field, value in mutations.items():
            with self.subTest(field=field):
                overlay = self.overlay()
                overlay["stock_sc"][field] = value  # type: ignore[index]
                path = self.write_overlay(overlay, f"bad-{field}.json")
                with self.assertRaises(common.CommonMessageOverlayError):
                    common.build_overlay(self.game_root, path, self.root / f"out-{field}")

    def test_source_hash_is_enforced(self) -> None:
        overlay = self.overlay()
        overlay["entries"][0]["source_sc_utf16le_sha256"] = "0" * 64  # type: ignore[index]
        path = self.write_overlay(overlay)
        with self.assertRaisesRegex(common.CommonMessageOverlayError, "source hash"):
            common.build_overlay(self.game_root, path, self.root / "out")

    def test_ids_must_be_sorted_and_unique(self) -> None:
        for label, ids in (("unsorted", [2, 1]), ("duplicate", [1, 1])):
            with self.subTest(label=label):
                overlay = self.overlay()
                for entry, entry_id in zip(overlay["entries"], ids):  # type: ignore[arg-type]
                    entry["id"] = entry_id
                    entry["source_sc_utf16le_sha256"] = common.text_hash(
                        self.texts[entry_id]
                    )
                with self.assertRaises(common.CommonMessageOverlayError):
                    common.validate_overlay_shape(overlay)

    def test_blank_nul_and_format_only_replacements_are_rejected(self) -> None:
        for label, replacement in (
            ("blank", " \t"),
            ("nul", "김\x00철수"),
            ("zero-width", "\u200b"),
            ("combining", "\u0301"),
            ("escape-only", "\x1bCA"),
        ):
            with self.subTest(label=label):
                overlay = self.overlay()
                overlay["entries"][0]["ko"] = replacement  # type: ignore[index]
                with self.assertRaises(common.CommonMessageOverlayError):
                    common.validate_overlay_shape(overlay)

    def test_printf_control_and_linebreak_invariants_are_enforced(self) -> None:
        source = self.texts[3]
        variants = {
            "printf": "%d\r\n\x1bCA\t",
            "escape": "%s\r\n\x1bCB\t",
            "control": "%s\r\n\x1bCA ",
            "linebreak": "%s\n\x1bCA\t",
            "edge-whitespace": " %s\r\n\x1bCA\t",
        }
        for label, replacement in variants.items():
            with self.subTest(label=label):
                issues = common.invariant_mismatches(source, replacement)
                self.assertTrue(issues)

                overlay = self.overlay()
                overlay["entries"] = [
                    {
                        "id": 3,
                        "source_sc_utf16le_sha256": common.text_hash(source),
                        "ko": replacement,
                    }
                ]
                overlay["entry_count"] = 1
                path = self.write_overlay(overlay, f"bad-{label}.json")
                with self.assertRaisesRegex(
                    common.CommonMessageOverlayError, "invariant mismatch"
                ):
                    common.build_overlay(
                        self.game_root, path, self.root / f"out-{label}"
                    )

    def test_edge_whitespace_change_requires_explicit_opt_in(self) -> None:
        overlay = self.overlay()
        overlay["entries"][0]["ko"] = "김 "  # type: ignore[index]
        denied = self.write_overlay(overlay, "edge-denied.json")
        with self.assertRaisesRegex(
            common.CommonMessageOverlayError,
            "trailing_whitespace",
        ):
            common.build_overlay(self.game_root, denied, self.root / "edge-denied")

        overlay["entries"][0]["allow_edge_whitespace_change"] = True  # type: ignore[index]
        allowed = self.write_overlay(overlay, "edge-allowed.json")
        result = common.build_overlay(self.game_root, allowed, self.root / "edge-allowed")
        target = Path(result["target_path"]).read_bytes()
        _, target_raw = common.decompress_wrapper(target)
        self.assertEqual("김 ", parse_message_table(target_raw).texts[1])

    def test_literal_percent_is_not_reported_as_unknown(self) -> None:
        tokens, unknown = common.printf_tokens("진행률 100%% / %s")
        self.assertEqual(["%%", "%s"], tokens)
        self.assertEqual(0, unknown)

    def test_overlay_shape_blocks_wrong_resource_policy_and_hidden_fields(self) -> None:
        mutations = []
        wrong_resource = self.overlay()
        wrong_resource["resource"] = "MSG_PK/SC/msgui.bin"
        mutations.append(wrong_resource)

        wrong_policy = self.overlay()
        wrong_policy["distribution_policy"]["contains_commercial_source_text"] = True  # type: ignore[index]
        mutations.append(wrong_policy)

        hidden_source = self.overlay()
        hidden_source["entries"][0]["source_sc"] = "源氏"  # type: ignore[index]
        mutations.append(hidden_source)

        for overlay in mutations:
            with self.subTest(resource=overlay["resource"]):
                with self.assertRaises(common.CommonMessageOverlayError):
                    common.validate_overlay_shape(overlay)

    def test_duplicate_json_keys_are_rejected(self) -> None:
        path = self.root / "duplicate.json"
        path.write_text('{"schema":"a","SCHEMA":"b"}', encoding="utf-8")
        with self.assertRaisesRegex(common.CommonMessageOverlayError, "case-colliding"):
            common.load_json_strict(path)

    def test_refuses_installed_output_path(self) -> None:
        path = self.write_overlay(self.overlay())
        with self.assertRaisesRegex(common.CommonMessageOverlayError, "installed stock"):
            common.build_overlay(self.game_root, path, self.game_root)


if __name__ == "__main__":
    unittest.main()
