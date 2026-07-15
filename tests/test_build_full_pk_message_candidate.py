from __future__ import annotations

import json
import shutil
import struct
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_ROOT = REPO_ROOT / "tools"
MSGGAME_ROOT = REPO_ROOT / "workstreams" / "msggame"
sys.path.insert(0, str(TOOLS_ROOT))
sys.path.insert(0, str(MSGGAME_ROOT))

import build_full_pk_message_candidate as full  # noqa: E402
from msggame_format import LITERAL_END, LITERAL_START, iter_literals, parse_packed_msggame  # noqa: E402
from nobu16_lz4 import WrapperHeader, raw_lz4_compress_literal_only, recompress_wrapper  # noqa: E402
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
        encoded = text.encode("utf-16le") + b"\0\0"
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
    raw.extend(b"\0" * ((-len(raw)) % 4))
    if parse_message_table(bytes(raw)).texts != tuple(texts):
        raise AssertionError("synthetic table fixture is invalid")
    return bytes(raw)


def wrap_raw(raw: bytes) -> bytes:
    prefix = bytes.fromhex("01 01 C4 C1 FA 7F 00 00")
    compressed = raw_lz4_compress_literal_only(raw)
    return prefix + struct.pack("<QQ", len(raw), len(compressed)) + compressed


def packed_msggame_fixture() -> bytes:
    record = b"\xAA" + LITERAL_START + "SOURCE_LITERAL".encode("utf-16le") + LITERAL_END + b"\xBB"
    block = struct.pack("<II", 1, 8) + record
    raw = struct.pack("<III", 1, 12, len(block)) + block
    raw += b"\0" * ((-len(raw)) % 4)
    return recompress_wrapper(raw, WrapperHeader(b"\x01\x01\xC4\xC1\xFA\x7F\0\0", len(raw), 0))


class FullPkCandidateBuilderTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp_root = REPO_ROOT / "tmp"
        self.root = Path(tempfile.mkdtemp(prefix="full-pk-builder-test-", dir=tmp_root))
        self.addCleanup(self._cleanup_root)
        self.stock_paths: dict[str, Path] = {}
        self.progress_path = self.root / "translation_progress.json"

    def _cleanup_root(self) -> None:
        if self.root.exists():
            self.assertTrue(self.root.resolve().is_relative_to((REPO_ROOT / "tmp").resolve()))
            shutil.rmtree(self.root)

    def _relative(self, path: Path) -> str:
        return path.relative_to(REPO_ROOT).as_posix()

    def _write_json(self, relative: str, value: dict) -> str:
        path = REPO_ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return relative

    def _write_baseline(self, resource: str, blob: bytes) -> None:
        path = self.root / "baselines" / Path(resource)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(blob)
        self.stock_paths[resource] = path

    @staticmethod
    def _common_overlay(resource: str, blob: bytes, raw: bytes, texts: list[str], overlay_id: str, entries: list[tuple[int, str]]) -> dict:
        return {
            "schema": full.COMMON_SCHEMA,
            "overlay_id": overlay_id,
            "resource": resource,
            "base_language": "SC",
            "entry_count": len(entries),
            "distribution_policy": {
                "contains_commercial_source_text": False,
                "contains_complete_game_resource": False,
            },
            "stock_sc": {
                "size": len(blob),
                "packed_sha256": full.sha256_bytes(blob),
                "raw_size": len(raw),
                "raw_sha256": full.sha256_bytes(raw),
                "string_count": len(texts),
            },
            "defaults": {"status": "translated"},
            "entries": [
                {
                    "id": entry_id,
                    "source_sc_utf16le_sha256": full.text_hash(texts[entry_id]),
                    "ko": ko,
                }
                for entry_id, ko in entries
            ],
        }

    def _create_progress(self, *, geographic_override: bool = False) -> dict[str, Path]:
        overlay_globs: dict[str, list[str]] = {}

        msgui_texts = ["SOURCE_MSGUI", " "]
        msgui_raw = make_raw_message_table(msgui_texts)
        msgui_blob = wrap_raw(msgui_raw)
        self._write_baseline("MSG_PK/SC/msgui.bin", msgui_blob)
        msgui_overlay_path = self._relative(self.root / "overlays" / "msgui.json")
        self._write_json(
            msgui_overlay_path,
            {
                "schema": full.MSGUI_SCHEMA,
                "overlay_id": "synthetic-msgui-v1",
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
                    "packed_sha256": full.sha256_bytes(msgui_blob),
                    "raw_sha256": full.sha256_bytes(msgui_raw),
                    "string_count": len(msgui_texts),
                },
                "defaults": {"status": "translated"},
                "development_batch_provenance": [
                    {
                        "file": "synthetic.json",
                        "sha256": "0" * 64,
                        "accepted_entries": 1,
                        "skipped_whitespace_entries": 0,
                    }
                ],
                "entries": [
                    {
                        "id": 0,
                        "source_sc_utf16le_sha256": full.text_hash(msgui_texts[0]),
                        "ko": "메뉴",
                    }
                ],
            },
        )
        overlay_globs["MSG_PK/SC/msgui.bin"] = [msgui_overlay_path]

        for resource, output_text in (
            ("MSG_PK/SC/msgev.bin", "이벤트"),
            ("MSG_PK/SC/msgbre.bin", "열전"),
            ("MSG_PK/SC/msgire.bin", "가보"),
            ("MSG_PK/SC/msgstf.bin", "제작진"),
        ):
            texts = [f"SOURCE_{Path(resource).stem}", "SPARE"]
            raw = make_raw_message_table(texts)
            blob = wrap_raw(raw)
            self._write_baseline(resource, blob)
            path = self._relative(self.root / "overlays" / f"{Path(resource).stem}.json")
            self._write_json(
                path,
                self._common_overlay(resource, blob, raw, texts, f"synthetic-{Path(resource).stem}-v1", [(0, output_text)]),
            )
            overlay_globs[resource] = [path]

        data_resource = "MSG_PK/SC/msgdata.bin"
        data_texts = ["SOURCE_DATA", "GENERIC_NAME"]
        data_raw = make_raw_message_table(data_texts)
        data_blob = wrap_raw(data_raw)
        self._write_baseline(data_resource, data_blob)
        data_common_path = self._relative(self.root / "overlays" / "msgdata-common.json")
        self._write_json(
            data_common_path,
            self._common_overlay(data_resource, data_blob, data_raw, data_texts, "synthetic-msgdata-v1", [(1, "김")]),
        )
        data_paths = [data_common_path]
        if geographic_override:
            castle_path = self._relative(self.root / "overlays" / "castle.json")
            self._write_json(
                castle_path,
                {
                    "entries": [{"id": 1, "ko": "박", "method": "en_romaji", "status": "reviewed"}],
                    "review": {},
                    "schema": full.CASTLE_SCHEMA,
                    "source_text_free": True,
                    "target": {
                        "entry_count": 1,
                        "first_id": 1,
                        "last_id": 1,
                        "resource": data_resource,
                        "shared_suffix_id_range_not_modified": {},
                    },
                    "translation_policy": {},
                },
            )
            data_paths.append(castle_path)
        overlay_globs[data_resource] = data_paths

        game_resource = "MSG_PK/SC/msggame.bin"
        game_blob = packed_msggame_fixture()
        self._write_baseline(game_resource, game_blob)
        parsed = parse_packed_msggame(game_blob)
        literal = next(iter(iter_literals(parsed.archive)))
        _header, game_raw = full.decompress_wrapper(game_blob)
        game_overlay_path = self._relative(self.root / "overlays" / "msggame.json")
        self._write_json(
            game_overlay_path,
            {
                "schema": full.MSGGAME_SCHEMA,
                "overlay_id": "synthetic-msggame-v1",
                "resource": game_resource,
                "base_language": "SC",
                "entry_count": 1,
                "distribution_policy": {
                    "contains_commercial_source_text": False,
                    "contains_complete_game_resource": False,
                },
                "stock_sc": {
                    "packed_size": len(game_blob),
                    "packed_sha256": full.sha256_bytes(game_blob),
                    "raw_size": len(game_raw),
                    "raw_sha256": full.sha256_bytes(game_raw),
                    "record_count": parsed.archive.record_count,
                    "literal_slot_count": 1,
                },
                "defaults": {"status": "translated"},
                "entries": [
                    {
                        "block_id": literal.block_id,
                        "record_id": literal.record_id,
                        "literal_id": literal.literal_id,
                        "source_sc_utf16le_sha256": full.text_hash(literal.text),
                        "ko": "시스템 메시지",
                    }
                ],
            },
        )
        overlay_globs[game_resource] = [game_overlay_path]

        resources = [{"path": resource, "overlay_globs": overlay_globs[resource]} for resource in full.TARGET_RESOURCES]
        self.progress_path.write_text(
            json.dumps({"schema": full.PROGRESS_SCHEMA, "resources": resources}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return {
            "msgdata_common": REPO_ROOT / data_common_path,
            "msggame": REPO_ROOT / game_overlay_path,
        }

    def _build(self, name: str) -> dict:
        return full.build_candidate(
            progress_path=self.progress_path,
            stock_paths=self.stock_paths,
            output_root=self.root / name,
        )

    def test_deterministic_full_build_is_source_free_and_never_mutates_inputs(self) -> None:
        self._create_progress()
        before = {resource: path.read_bytes() for resource, path in self.stock_paths.items()}
        first = self._build("candidate-a")
        second = self._build("candidate-b")
        for resource in full.TARGET_RESOURCES:
            self.assertEqual(
                (first["output_root"] / Path(resource)).read_bytes(),
                (second["output_root"] / Path(resource)).read_bytes(),
                resource,
            )
        first_manifest = first["manifest_path"].read_bytes()
        self.assertEqual(first_manifest, second["manifest_path"].read_bytes())
        self.assertNotIn(b"SOURCE_MSGUI", first_manifest)
        self.assertNotIn(b"SOURCE_LITERAL", first_manifest)
        manifest = json.loads(first_manifest)
        self.assertEqual(full.MANIFEST_SCHEMA, manifest["schema"])
        self.assertTrue(manifest["checks"]["all_baselines_unchanged"])
        self.assertEqual(7, len(manifest["resources"]))
        for resource, expected in before.items():
            self.assertEqual(expected, self.stock_paths[resource].read_bytes(), resource)

    def test_reviewed_geographic_name_override_is_ordered_and_effective(self) -> None:
        self._create_progress(geographic_override=True)
        result = self._build("candidate-geographic")
        target = (result["output_root"] / "MSG_PK" / "SC" / "msgdata.bin").read_bytes()
        _header, raw = full.decompress_wrapper(target)
        self.assertEqual("박", parse_message_table(raw).texts[1])
        details = result["resources"]["MSG_PK/SC/msgdata.bin"]
        self.assertEqual(1, len(details["ordered_overlap_overrides"]))
        self.assertEqual(1, details["source_hash_generated_for_name_overlay_count"])

    def test_source_hash_failure_does_not_publish_output(self) -> None:
        paths = self._create_progress()
        value = json.loads(paths["msgdata_common"].read_text(encoding="utf-8"))
        value["entries"][0]["source_sc_utf16le_sha256"] = "0" * 64
        paths["msgdata_common"].write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        output = self.root / "candidate-rejected"
        with self.assertRaisesRegex(full.BuildError, "source hash mismatch"):
            full.build_candidate(
                progress_path=self.progress_path,
                stock_paths=self.stock_paths,
                output_root=output,
            )
        self.assertFalse(output.exists())

    def test_source_free_msggame_selection_and_translation_metadata_are_accepted(self) -> None:
        paths = self._create_progress()
        value = json.loads(paths["msggame"].read_text(encoding="utf-8"))
        value["translation_provenance"] = {
            "context_languages": ["SC", "JP", "EN"],
            "kind": "agent_ui_priority_full_record_translation",
            "runtime_reviewed": False,
            "source_text_embedded": False,
        }
        value["selection_policy"] = {
            "dynamic_fragments_excluded": True,
            "event_dialogue_excluded": True,
            "priority": "complete_ui_components_outside_blocks_13_14",
            "source_text_embedded": False,
        }
        paths["msggame"].write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        result = self._build("candidate-msggame-metadata")
        self.assertTrue(result["manifest_path"].is_file())

    def test_extended_ui_priority_metadata_is_accepted(self) -> None:
        paths = self._create_progress()
        value = json.loads(paths["msggame"].read_text(encoding="utf-8"))
        value["translation_provenance"] = {
            "context_languages": ["SC", "JP", "EN", "TC"],
            "kind": "parallel_agent_battle_ui_translation",
            "runtime_reviewed": False,
            "source_text_embedded": False,
            "switch_context": {
                "asset_sha256": "F4D2563C1B32DB450165C8CCF61C6947DEA904233581036E179AFA1D6A918CC4",
                "author": "snake7594",
                "release_tag": "v1.3",
                "repository_url": "https://github.com/snake7594/nobunaga-shinsei-korean-patch",
                "unique_jp_hash_alignment_count": 74,
                "use": "semantic_and_terminology_reference_only",
            },
        }
        value["selection_policy"] = {
            "block_entry_counts": {"6": 1},
            "blocks": [6],
            "event_dialogue_block_17_excluded": True,
            "format_control_pua_free_selection": True,
            "priority": "battle_ui",
            "read_only_predecessors": ["previous-a.json", "previous-b.json"],
            "single_literal_records_only": True,
            "source_text_embedded": False,
        }
        parsed = full.parse_msggame_overlay(value, "synthetic-extended-msggame")
        self.assertEqual(value["overlay_id"], parsed["overlay_id"])

    def test_msggame_metadata_cannot_claim_embedded_source_text(self) -> None:
        paths = self._create_progress()
        value = json.loads(paths["msggame"].read_text(encoding="utf-8"))
        value["translation_provenance"] = {
            "context_languages": ["SC", "JP", "EN"],
            "kind": "agent_ui_priority_full_record_translation",
            "runtime_reviewed": False,
            "source_text_embedded": True,
        }
        with self.assertRaisesRegex(full.BuildError, "source_text_embedded"):
            full.parse_msggame_overlay(value, "synthetic-msggame")

    def test_output_outside_repository_tmp_is_refused(self) -> None:
        self._create_progress()
        with tempfile.TemporaryDirectory() as external:
            with self.assertRaisesRegex(full.BuildError, "KR_PATCH_WORK/tmp"):
                full.build_candidate(
                    progress_path=self.progress_path,
                    stock_paths=self.stock_paths,
                    output_root=Path(external) / "candidate",
                )


if __name__ == "__main__":
    unittest.main()
