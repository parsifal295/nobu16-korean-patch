#!/usr/bin/env python3
"""Merge the two source-free Steam-JP msgdata P1 overlays into one candidate.

The active Steam JP v6 binary is read only.  The only complete resource this
builder can emit is a private staging file below ``KR_PATCH_WORK/tmp``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import struct
import sys
import tempfile
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = WORKSTREAM_ROOT.parents[1]
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import MessageTable, parse_message_table, rebuild_message_table  # noqa: E402


RESOURCE = "MSG_PK/JP/msgdata.bin"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "tmp" / "steam_jp_msgdata_p1_integrated_345_v1" / "candidate"
PUBLIC_OVERLAY = WORKSTREAM_ROOT / "public" / "msgdata_ko_pk_jp_p1_integrated_345.v1.json"
VALIDATION = WORKSTREAM_ROOT / "validation.v1.json"
CONTRACT = WORKSTREAM_ROOT / "source_free_contract.v1.json"

STOCK = {
    "packed_size": 496999,
    "packed_sha256": "2D1BEFF03972777FBA5EE0B8FEF24E6A03B285DA466A4DA439794D21587A0F69",
    "raw_size": 495032,
    "raw_sha256": "25593167A47B5B0F69357F71E5E9882382F346AEF1B8DCA7DB6902D7E270AB67",
    "string_count": 29218,
}
BUNDLE_COORDINATE_SHA256 = "D3A559DD853504332F46F2ED91DAFF6D30A6100C04F53907E812784374007FA6"
MERGED_BUNDLE = {"bundle_id": "p1-MSG_PK_JP-msgdata-01-plus-02", "coordinate_sha256": BUNDLE_COORDINATE_SHA256}

INPUTS = (
    {
        "bundle_id": "p1-MSG_PK_JP_msgdata-01",
        "entry_count": 175,
        "contract_relative_path": "workstreams/steam_jp_msgdata_p1_residual_175_v1/source_free_contract.v1.json",
        "contract_sha256": "B02828B4F4544330AB9078D939B0385D5FEC69BE0DCD45BCCFC93E05E02BA4C6",
        "overlay_relative_path": "workstreams/steam_jp_msgdata_p1_residual_175_v1/public/msgdata_ko_pk_jp_p1_residual_175.v1.json",
        "overlay_sha256": "DBFD1F92FEDFD415AD1CA88F63F645492285AF8B2FF256C333EC8FC36956CF8A",
    },
    {
        "bundle_id": "p1-MSG_PK_JP-msgdata-02",
        "entry_count": 170,
        "contract_relative_path": "workstreams/steam_jp_msgdata_p1_residual_170_v1/source_free_contract.v1.json",
        "contract_sha256": "FCAEFCABAB5635E359FD89FCBD72AC6885572C7ABDC5FD76C26820287CC575B1",
        "overlay_relative_path": "workstreams/steam_jp_msgdata_p1_residual_170_v1/public/msgdata_ko_pk_jp_p1_residual_170.v1.json",
        "overlay_sha256": "A10AC4CFD4D0A2DF1B5EDAD8324DB54F69703D0357BE80E4B1CF7E58059B82ED",
    },
)

OVERLAY_SCHEMA = "nobu16.kr.steam-jp-msgdata-p1-integrated-345-overlay.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-msgdata-p1-integrated-345-validation.v1"
CONTRACT_SCHEMA = "nobu16.kr.steam-jp-msgdata-p1-integrated-345-contract.v1"
MANIFEST_SCHEMA = "nobu16.kr.steam-jp-msgdata-p1-integrated-345-build-manifest.v1"

HEX64_RE = re.compile(r"[0-9A-F]{64}\Z")
KANA_RE = re.compile(r"[\u3040-\u30ff\uff66-\uff9f]")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
CJK_OR_KANA_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uf900-\ufaff]")
PRINTF_RE = re.compile(r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
LINE_BREAK_RE = re.compile(r"\r\n|\n|\r")
INVARIANT_KEYS = (
    "printf", "unknown_percent_count", "leading_whitespace", "trailing_whitespace", "esc", "controls",
    "line_breaks", "pua", "greek_symbols", "box_drawing_symbols", "ideographic_space_count",
)
SOURCE_ENTRY_FIELDS = {
    "id", "source_jp_utf16le_sha256", "ko", "ko_utf16le_sha256", "format_signature_sha256", "translation_origin",
}
MERGED_ENTRY_FIELDS = SOURCE_ENTRY_FIELDS | {"source_bundle"}


class MsgdataP1IntegratedError(ValueError):
    """Raised for source, format, merge, or private-output policy violations."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def canonical_hash(value: object) -> str:
    return sha256_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def pretty_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def atomic_write(path: Path, blob: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(blob)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def strict_object(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise MsgdataP1IntegratedError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def read_json(path: Path) -> tuple[dict[str, Any], bytes]:
    blob = path.read_bytes()
    try:
        value = json.loads(blob.decode("utf-8"), object_pairs_hook=strict_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise MsgdataP1IntegratedError(f"invalid JSON: {path}") from error
    if not isinstance(value, dict):
        raise MsgdataP1IntegratedError(f"JSON root must be an object: {path}")
    return value, blob


def path_from_repo(relative: str) -> Path:
    path = Path(relative)
    if not relative or path.is_absolute() or ".." in path.parts or "\\" in relative:
        raise MsgdataP1IntegratedError("unsafe repository-relative path")
    resolved = (REPO_ROOT / path).resolve()
    if not resolved.is_relative_to(REPO_ROOT.resolve()):
        raise MsgdataP1IntegratedError("repository-relative path escapes workspace")
    return resolved


def assert_source_free_path(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if CJK_OR_KANA_RE.search(text) or "MSG_PK/SC" in text or "RES_SC" in text or "source_sc" in text.casefold():
        raise MsgdataP1IntegratedError(f"source-free artifact contains disallowed source material: {path}")


def is_high_confidence_japanese(text: str) -> bool:
    return bool(KANA_RE.search(text)) and not bool(HANGUL_RE.search(text))


def message_invariants(text: str) -> dict[str, Any]:
    printf_matches = list(PRINTF_RE.finditer(text))
    percent_offsets = {offset for match in printf_matches for offset in range(match.start(), match.end()) if text[offset] == "%"}
    esc_matches = list(ESC_RE.finditer(text))
    esc_offsets = {offset for match in esc_matches for offset in range(match.start(), match.end())}
    return {
        "printf": [match.group(0) for match in printf_matches],
        "unknown_percent_count": sum(1 for offset, char in enumerate(text) if char == "%" and offset not in percent_offsets),
        "leading_whitespace": text[:len(text) - len(text.lstrip())],
        "trailing_whitespace": text[len(text.rstrip()):],
        "esc": [match.group(0) for match in esc_matches],
        "controls": [
            f"U+{ord(char):04X}" for offset, char in enumerate(text)
            if unicodedata.category(char) == "Cc" and char not in ("\r", "\n") and offset not in esc_offsets
        ],
        "line_breaks": LINE_BREAK_RE.findall(text),
        "pua": [f"U+{ord(char):04X}" for char in text if 0xE000 <= ord(char) <= 0xF8FF],
        "greek_symbols": [char for char in text if 0x0370 <= ord(char) <= 0x03FF],
        "box_drawing_symbols": [char for char in text if 0x2500 <= ord(char) <= 0x257F],
        "ideographic_space_count": text.count("\u3000"),
    }


def mismatch_keys(source: str, replacement: str) -> list[str]:
    before = message_invariants(source)
    after = message_invariants(replacement)
    return [key for key in INVARIANT_KEYS if before[key] != after[key]]


def load_stock(steam_root: Path) -> tuple[Path, bytes, bytes, MessageTable]:
    root = steam_root.resolve()
    source_path = (root / Path(RESOURCE)).resolve()
    if not source_path.is_relative_to(root) or not source_path.is_file():
        raise MsgdataP1IntegratedError(f"active JP resource does not exist: {source_path}")
    packed = source_path.read_bytes()
    if len(packed) != STOCK["packed_size"] or sha256_bytes(packed) != STOCK["packed_sha256"]:
        raise MsgdataP1IntegratedError("active Steam JP msgdata packed baseline does not match v6 pin")
    _header, raw = decompress_wrapper(packed)
    if len(raw) != STOCK["raw_size"] or sha256_bytes(raw) != STOCK["raw_sha256"]:
        raise MsgdataP1IntegratedError("active Steam JP msgdata raw baseline does not match v6 pin")
    table = parse_message_table(raw)
    if table.string_count != STOCK["string_count"] or rebuild_message_table(table, table.texts) != raw:
        raise MsgdataP1IntegratedError("active Steam JP msgdata structure does not match v6 pin")
    return source_path, packed, raw, table


def read_input_overlay(input_pin: Mapping[str, Any], table: MessageTable) -> list[dict[str, Any]]:
    contract_path = path_from_repo(str(input_pin["contract_relative_path"]))
    contract, contract_blob = read_json(contract_path)
    if sha256_bytes(contract_blob) != input_pin["contract_sha256"]:
        raise MsgdataP1IntegratedError(f"input contract pin differs: {input_pin['bundle_id']}")
    assert_source_free_path(contract_path)
    if contract.get("resource") != RESOURCE or contract.get("active_v6_baseline") != STOCK:
        raise MsgdataP1IntegratedError(f"input contract route/baseline differs: {input_pin['bundle_id']}")
    if contract.get("runtime_route") != {"language": "JP", "sc_container_used": False, "installed_game_file_written": False}:
        raise MsgdataP1IntegratedError(f"input contract runtime route differs: {input_pin['bundle_id']}")
    input_audit = contract.get("audit_bundle")
    if not isinstance(input_audit, dict) or input_audit.get("bundle_id") != input_pin["bundle_id"]:
        raise MsgdataP1IntegratedError(f"input audit bundle differs: {input_pin['bundle_id']}")
    overlay_locator = contract.get("overlay")
    if not isinstance(overlay_locator, dict) or overlay_locator.get("relative_path") != input_pin["overlay_relative_path"]:
        raise MsgdataP1IntegratedError(f"input overlay path differs: {input_pin['bundle_id']}")
    overlay_path = path_from_repo(str(input_pin["overlay_relative_path"]))
    overlay, overlay_blob = read_json(overlay_path)
    if sha256_bytes(overlay_blob) != input_pin["overlay_sha256"] or overlay_locator.get("sha256") != input_pin["overlay_sha256"]:
        raise MsgdataP1IntegratedError(f"input overlay pin differs: {input_pin['bundle_id']}")
    assert_source_free_path(overlay_path)
    if overlay.get("resource") != RESOURCE or overlay.get("base_language") != "JP" or overlay.get("active_v6_baseline") != STOCK:
        raise MsgdataP1IntegratedError(f"input overlay route/baseline differs: {input_pin['bundle_id']}")
    if overlay.get("audit_bundle") != input_audit or overlay.get("entry_count") != input_pin["entry_count"]:
        raise MsgdataP1IntegratedError(f"input overlay audit/count differs: {input_pin['bundle_id']}")
    entries_value = overlay.get("entries")
    if not isinstance(entries_value, list) or len(entries_value) != input_pin["entry_count"]:
        raise MsgdataP1IntegratedError(f"input overlay entries differ: {input_pin['bundle_id']}")
    entries: list[dict[str, Any]] = []
    seen: set[int] = set()
    for entry in entries_value:
        if not isinstance(entry, dict) or set(entry) != SOURCE_ENTRY_FIELDS:
            raise MsgdataP1IntegratedError(f"input entry schema differs: {input_pin['bundle_id']}")
        entry_id = entry.get("id")
        source_hash = entry.get("source_jp_utf16le_sha256")
        ko = entry.get("ko")
        if not isinstance(entry_id, int) or entry_id in seen or entry_id < 0 or entry_id >= table.string_count:
            raise MsgdataP1IntegratedError(f"input entry ID differs: {input_pin['bundle_id']}")
        seen.add(entry_id)
        if not isinstance(source_hash, str) or not HEX64_RE.fullmatch(source_hash) or source_hash != text_hash(table.texts[entry_id]):
            raise MsgdataP1IntegratedError(f"input source hash differs at id {entry_id}")
        if not isinstance(ko, str) or not ko or CJK_OR_KANA_RE.search(ko) or "\0" in ko or "\ufffd" in ko:
            raise MsgdataP1IntegratedError(f"input Korean value is unsafe at id {entry_id}")
        if entry.get("ko_utf16le_sha256") != text_hash(ko):
            raise MsgdataP1IntegratedError(f"input Korean hash differs at id {entry_id}")
        if entry.get("format_signature_sha256") != canonical_hash(message_invariants(table.texts[entry_id])):
            raise MsgdataP1IntegratedError(f"input format signature differs at id {entry_id}")
        if mismatch_keys(table.texts[entry_id], ko):
            raise MsgdataP1IntegratedError(f"input format token mismatch at id {entry_id}")
        if entry.get("translation_origin") not in {"exact_source_hash_catalog_reuse", "project_direct_translation"}:
            raise MsgdataP1IntegratedError(f"input translation origin differs at id {entry_id}")
        entries.append(dict(entry))
    return entries


def load_merged_input_entries(table: MessageTable) -> tuple[list[dict[str, Any]], dict[int, dict[str, Any]]]:
    merged: list[dict[str, Any]] = []
    expected_by_id: dict[int, dict[str, Any]] = {}
    for input_pin in INPUTS:
        for entry in read_input_overlay(input_pin, table):
            entry_id = entry["id"]
            if entry_id in expected_by_id:
                raise MsgdataP1IntegratedError(f"input overlay coordinates overlap at id {entry_id}")
            combined = {"source_bundle": input_pin["bundle_id"], **entry}
            expected_by_id[entry_id] = combined
            merged.append(combined)
    merged.sort(key=lambda entry: int(entry["id"]))
    if len(merged) != 345 or len(expected_by_id) != 345:
        raise MsgdataP1IntegratedError("input overlay total is not 345 non-overlapping entries")
    if canonical_hash([{"id": entry["id"]} for entry in merged]) != BUNDLE_COORDINATE_SHA256:
        raise MsgdataP1IntegratedError("merged coordinate contract differs")
    return merged, expected_by_id


def validate_merged_entries(table: MessageTable, entries: Sequence[Mapping[str, Any]], expected_by_id: Mapping[int, Mapping[str, Any]] | None = None) -> list[dict[str, Any]]:
    if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes)) or len(entries) != 345:
        raise MsgdataP1IntegratedError("merged entry count differs")
    normalized: list[dict[str, Any]] = []
    previous = -1
    for entry in entries:
        if not isinstance(entry, Mapping) or set(entry) != MERGED_ENTRY_FIELDS:
            raise MsgdataP1IntegratedError("merged entry schema differs")
        entry_id = entry.get("id")
        source_hash = entry.get("source_jp_utf16le_sha256")
        ko = entry.get("ko")
        if not isinstance(entry_id, int) or entry_id <= previous or entry_id < 0 or entry_id >= table.string_count:
            raise MsgdataP1IntegratedError("merged entry order or ID differs")
        previous = entry_id
        if entry.get("source_bundle") not in {item["bundle_id"] for item in INPUTS}:
            raise MsgdataP1IntegratedError(f"merged source bundle differs at id {entry_id}")
        if not isinstance(source_hash, str) or not HEX64_RE.fullmatch(source_hash) or source_hash != text_hash(table.texts[entry_id]):
            raise MsgdataP1IntegratedError(f"merged source hash differs at id {entry_id}")
        if not isinstance(ko, str) or not ko or CJK_OR_KANA_RE.search(ko) or "\0" in ko or "\ufffd" in ko:
            raise MsgdataP1IntegratedError(f"merged Korean value unsafe at id {entry_id}")
        if entry.get("ko_utf16le_sha256") != text_hash(ko):
            raise MsgdataP1IntegratedError(f"merged Korean hash differs at id {entry_id}")
        if entry.get("format_signature_sha256") != canonical_hash(message_invariants(table.texts[entry_id])):
            raise MsgdataP1IntegratedError(f"merged format signature differs at id {entry_id}")
        if mismatch_keys(table.texts[entry_id], ko):
            raise MsgdataP1IntegratedError(f"merged format token mismatch at id {entry_id}")
        if entry.get("translation_origin") not in {"exact_source_hash_catalog_reuse", "project_direct_translation"}:
            raise MsgdataP1IntegratedError(f"merged origin differs at id {entry_id}")
        normalized_entry = dict(entry)
        if expected_by_id is not None and normalized_entry != expected_by_id.get(entry_id):
            raise MsgdataP1IntegratedError(f"merged entry no longer equals pinned source-free input at id {entry_id}")
        normalized.append(normalized_entry)
    if canonical_hash([{"id": entry["id"]} for entry in normalized]) != BUNDLE_COORDINATE_SHA256:
        raise MsgdataP1IntegratedError("merged coordinate hash differs")
    return normalized


def input_header() -> list[dict[str, Any]]:
    return [dict(item) for item in INPUTS]


def make_overlay(entries: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    origins = Counter(entry["translation_origin"] for entry in entries)
    bundles = Counter(entry["source_bundle"] for entry in entries)
    return {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": "msgdata_ko_pk_jp_p1_integrated_345.v1",
        "resource": RESOURCE,
        "base_language": "JP",
        "distribution_policy": {"contains_commercial_source_text": False, "contains_complete_game_resource": False, "sc_container_used": False},
        "active_v6_baseline": dict(STOCK),
        "merged_audit_bundle": dict(MERGED_BUNDLE),
        "input_overlay_contracts": input_header(),
        "entry_count": len(entries),
        "source_bundle_counts": dict(sorted(bundles.items())),
        "translation_origin_counts": dict(sorted(origins.items())),
        "entries": list(entries),
    }


def validate_public_overlay(value: Mapping[str, Any], table: MessageTable, expected_by_id: Mapping[int, Mapping[str, Any]]) -> list[dict[str, Any]]:
    required = {
        "schema", "overlay_id", "resource", "base_language", "distribution_policy", "active_v6_baseline", "merged_audit_bundle",
        "input_overlay_contracts", "entry_count", "source_bundle_counts", "translation_origin_counts", "entries",
    }
    if set(value) != required or value.get("schema") != OVERLAY_SCHEMA or value.get("overlay_id") != "msgdata_ko_pk_jp_p1_integrated_345.v1":
        raise MsgdataP1IntegratedError("merged public overlay header differs")
    if value.get("resource") != RESOURCE or value.get("base_language") != "JP" or value.get("active_v6_baseline") != STOCK:
        raise MsgdataP1IntegratedError("merged public overlay route/baseline differs")
    if value.get("distribution_policy") != {"contains_commercial_source_text": False, "contains_complete_game_resource": False, "sc_container_used": False}:
        raise MsgdataP1IntegratedError("merged public overlay policy differs")
    if value.get("merged_audit_bundle") != MERGED_BUNDLE or value.get("input_overlay_contracts") != input_header():
        raise MsgdataP1IntegratedError("merged public overlay provenance differs")
    entries_value = value.get("entries")
    if not isinstance(entries_value, list) or value.get("entry_count") != len(entries_value):
        raise MsgdataP1IntegratedError("merged public overlay entry count differs")
    entries = validate_merged_entries(table, entries_value, expected_by_id)
    if value.get("source_bundle_counts") != dict(sorted(Counter(entry["source_bundle"] for entry in entries).items())):
        raise MsgdataP1IntegratedError("merged source bundle counts differ")
    if value.get("translation_origin_counts") != dict(sorted(Counter(entry["translation_origin"] for entry in entries).items())):
        raise MsgdataP1IntegratedError("merged origin counts differ")
    return entries


def candidate_from_entries(packed: bytes, raw: bytes, table: MessageTable, entries: Sequence[Mapping[str, Any]], expected_by_id: Mapping[int, Mapping[str, Any]] | None = None) -> tuple[bytes, bytes, list[int], int]:
    normalized = validate_merged_entries(table, entries, expected_by_id)
    target_texts = list(table.texts)
    changed_ids: list[int] = []
    for entry in normalized:
        entry_id = int(entry["id"])
        ko = str(entry["ko"])
        if target_texts[entry_id] != ko:
            changed_ids.append(entry_id)
        target_texts[entry_id] = ko
    rebuilt_raw_a = rebuild_message_table(table, target_texts)
    rebuilt_raw_b = rebuild_message_table(table, target_texts)
    if rebuilt_raw_a != rebuilt_raw_b:
        raise MsgdataP1IntegratedError("raw candidate is not deterministic")
    candidate_a = recompress_wrapper(rebuilt_raw_a, packed)
    candidate_b = recompress_wrapper(rebuilt_raw_b, packed)
    if candidate_a != candidate_b:
        raise MsgdataP1IntegratedError("packed candidate is not deterministic")
    _header, checked_raw = decompress_wrapper(candidate_a)
    checked_table = parse_message_table(checked_raw)
    if checked_raw != rebuilt_raw_a or checked_table.texts != tuple(target_texts):
        raise MsgdataP1IntegratedError("candidate parser/decompression roundtrip differs")
    if (
        checked_table.string_count != table.string_count
        or checked_table.block_offset != table.block_offset
        or checked_table.table_offset != table.table_offset
        or checked_table.table_size != table.table_size
        or checked_table.string_start != table.string_start
        or rebuild_message_table(checked_table, checked_table.texts) != checked_raw
    ):
        raise MsgdataP1IntegratedError("candidate structure differs")
    selected = {entry["id"]: entry["ko"] for entry in normalized}
    for entry_id, source in enumerate(table.texts):
        expected = selected.get(entry_id, source)
        if checked_table.texts[entry_id] != expected:
            raise MsgdataP1IntegratedError(f"candidate text differs at id {entry_id}")
        if entry_id not in selected and source.encode("utf-16le") + b"\0\0" != checked_table.texts[entry_id].encode("utf-16le") + b"\0\0":
            raise MsgdataP1IntegratedError(f"nonselected UTF-16LE payload differs at id {entry_id}")
    if any(is_high_confidence_japanese(checked_table.texts[entry_id]) for entry_id in selected):
        raise MsgdataP1IntegratedError("merged candidate retains Japanese residual in selected set")
    before_total = sum(is_high_confidence_japanese(text) for text in table.texts)
    after_total = sum(is_high_confidence_japanese(text) for text in checked_table.texts)
    if after_total != before_total - len(selected):
        raise MsgdataP1IntegratedError("merged candidate changes residuals outside selected set")
    stock_prefix = bytearray(raw[:table.table_offset])
    candidate_prefix = bytearray(checked_raw[:checked_table.table_offset])
    struct.pack_into("<I", stock_prefix, 8, 0)
    struct.pack_into("<I", candidate_prefix, 8, 0)
    if stock_prefix != candidate_prefix:
        raise MsgdataP1IntegratedError("opaque prefix differs outside logical-size field")
    return candidate_a, rebuilt_raw_a, changed_ids, after_total


def make_validation(entries: Sequence[Mapping[str, Any]], candidate: bytes, candidate_raw: bytes, changed_ids: Sequence[int], residual_after: int) -> dict[str, Any]:
    return {
        "schema": VALIDATION_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "resource": RESOURCE,
        "active_v6_baseline": dict(STOCK),
        "merged_audit_bundle": dict(MERGED_BUNDLE),
        "entry_count": len(entries),
        "source_bundle_counts": dict(sorted(Counter(entry["source_bundle"] for entry in entries).items())),
        "translation_origin_counts": dict(sorted(Counter(entry["translation_origin"] for entry in entries).items())),
        "expected_candidate": {"packed_size": len(candidate), "packed_sha256": sha256_bytes(candidate), "raw_size": len(candidate_raw), "raw_sha256": sha256_bytes(candidate_raw)},
        "effective_change_count": len(changed_ids),
        "effective_change_coordinate_sha256": canonical_hash(list(changed_ids)),
        "high_confidence_kana_residual_count_after_candidate": residual_after,
        "checks": {
            "active_v6_baseline": "OK", "input_overlay_hash_pins": "OK", "input_coordinates_overlap": "0",
            "per_entry_jp_source_hashes": "OK", "esc_printf_newline_pua_whitespace": "OK",
            "raw_deterministic_rebuild": "OK", "packed_deterministic_rebuild": "OK", "candidate_parser_roundtrip": "OK",
            "nonselected_utf16le_payloads": "OK", "selected_high_confidence_kana_residuals": "0",
            "steam_installation_written": False, "release_asset_written": False, "github_written": False,
        },
    }


def make_contract(overlay_blob: bytes, validation_blob: bytes, candidate: bytes, candidate_raw: bytes, entries: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "schema": CONTRACT_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "resource": RESOURCE,
        "runtime_route": {"language": "JP", "sc_container_used": False, "installed_game_file_written": False},
        "active_v6_baseline": dict(STOCK),
        "merged_audit_bundle": dict(MERGED_BUNDLE),
        "input_overlay_contracts": input_header(),
        "overlay": {"relative_path": "workstreams/steam_jp_msgdata_p1_integrated_345_v1/public/msgdata_ko_pk_jp_p1_integrated_345.v1.json", "sha256": sha256_bytes(overlay_blob), "entry_count": len(entries)},
        "validation": {"relative_path": "workstreams/steam_jp_msgdata_p1_integrated_345_v1/validation.v1.json", "sha256": sha256_bytes(validation_blob)},
        "expected_candidate": {"packed_size": len(candidate), "packed_sha256": sha256_bytes(candidate), "raw_size": len(candidate_raw), "raw_sha256": sha256_bytes(candidate_raw), "string_count": STOCK["string_count"]},
        "output_policy": {"complete_candidate_private_only": True, "allowed_root": "tmp", "relative_path": RESOURCE},
        "proofs": {
            "input_overlay_contracts_pinned": True, "active_v6_baseline_pinned": True, "coordinates_nonoverlapping": True,
            "per_entry_jp_source_hash_gated": True, "esc_printf_newline_pua_whitespace_preserved": True,
            "nonselected_utf16le_payloads_preserved": True, "parser_roundtrip_valid": True,
            "deterministic_raw_and_packed_rebuild": True, "steam_installation_read_only": True,
        },
    }


def require_private_output_root(output_root: Path) -> Path:
    resolved = output_root.resolve()
    private_root = (REPO_ROOT / "tmp").resolve()
    if not resolved.is_relative_to(private_root) or resolved == private_root:
        raise MsgdataP1IntegratedError("complete candidate output must be a child below KR_PATCH_WORK/tmp")
    return resolved


def freeze(steam_root: Path) -> dict[str, Any]:
    _source_path, packed, raw, table = load_stock(steam_root)
    entries, expected_by_id = load_merged_input_entries(table)
    entries = validate_merged_entries(table, entries, expected_by_id)
    candidate, candidate_raw, changed_ids, residual_after = candidate_from_entries(packed, raw, table, entries, expected_by_id)
    overlay_blob = pretty_bytes(make_overlay(entries))
    validation_blob = pretty_bytes(make_validation(entries, candidate, candidate_raw, changed_ids, residual_after))
    contract_blob = pretty_bytes(make_contract(overlay_blob, validation_blob, candidate, candidate_raw, entries))
    atomic_write(PUBLIC_OVERLAY, overlay_blob)
    atomic_write(VALIDATION, validation_blob)
    atomic_write(CONTRACT, contract_blob)
    for path in (PUBLIC_OVERLAY, VALIDATION, CONTRACT):
        assert_source_free_path(path)
    return {
        "entry_count": len(entries), "candidate_sha256": sha256_bytes(candidate), "candidate_raw_sha256": sha256_bytes(candidate_raw),
        "high_confidence_kana_residual_count_after_candidate": residual_after, "installed_game_file_modified": False,
    }


def load_frozen_inputs(steam_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], dict[int, dict[str, Any]], bytes, bytes, MessageTable]:
    _source_path, packed, raw, table = load_stock(steam_root)
    expected_entries, expected_by_id = load_merged_input_entries(table)
    contract, _contract_blob = read_json(CONTRACT)
    required = {
        "schema", "source_free", "contains_commercial_source_text", "contains_complete_game_resource", "resource", "runtime_route",
        "active_v6_baseline", "merged_audit_bundle", "input_overlay_contracts", "overlay", "validation", "expected_candidate", "output_policy", "proofs",
    }
    if set(contract) != required or contract.get("schema") != CONTRACT_SCHEMA or contract.get("resource") != RESOURCE:
        raise MsgdataP1IntegratedError("frozen contract header differs")
    if contract.get("active_v6_baseline") != STOCK or contract.get("merged_audit_bundle") != MERGED_BUNDLE or contract.get("input_overlay_contracts") != input_header():
        raise MsgdataP1IntegratedError("frozen contract provenance differs")
    if contract.get("runtime_route") != {"language": "JP", "sc_container_used": False, "installed_game_file_written": False}:
        raise MsgdataP1IntegratedError("frozen contract route differs")
    if contract.get("output_policy") != {"complete_candidate_private_only": True, "allowed_root": "tmp", "relative_path": RESOURCE}:
        raise MsgdataP1IntegratedError("frozen contract output policy differs")
    if not isinstance(contract.get("proofs"), dict) or any(value is not True for value in contract["proofs"].values()):
        raise MsgdataP1IntegratedError("frozen contract proofs are incomplete")
    overlay_locator = contract.get("overlay")
    validation_locator = contract.get("validation")
    if not isinstance(overlay_locator, dict) or not isinstance(validation_locator, dict):
        raise MsgdataP1IntegratedError("frozen artifact locators differ")
    overlay_path = path_from_repo(str(overlay_locator.get("relative_path", "")))
    overlay, overlay_blob = read_json(overlay_path)
    if sha256_bytes(overlay_blob) != overlay_locator.get("sha256"):
        raise MsgdataP1IntegratedError("frozen merged overlay hash differs")
    entries = validate_public_overlay(overlay, table, expected_by_id)
    if entries != expected_entries:
        raise MsgdataP1IntegratedError("frozen merged entries differ from input overlays")
    validation_path = path_from_repo(str(validation_locator.get("relative_path", "")))
    validation_blob = validation_path.read_bytes()
    if sha256_bytes(validation_blob) != validation_locator.get("sha256"):
        raise MsgdataP1IntegratedError("frozen validation hash differs")
    for path in (overlay_path, validation_path, CONTRACT):
        assert_source_free_path(path)
    return contract, entries, expected_by_id, packed, raw, table


def build_staging_candidate(steam_root: Path, output_root: Path) -> dict[str, Any]:
    output_root = require_private_output_root(output_root)
    source_path, stock_before, _raw_before, _table_before = load_stock(steam_root)
    contract, entries, expected_by_id, packed, raw, table = load_frozen_inputs(steam_root)
    if packed != stock_before:
        raise MsgdataP1IntegratedError("active Steam JP source changed while loading frozen inputs")
    candidate, candidate_raw, changed_ids, residual_after = candidate_from_entries(packed, raw, table, entries, expected_by_id)
    observed = {"packed_size": len(candidate), "packed_sha256": sha256_bytes(candidate), "raw_size": len(candidate_raw), "raw_sha256": sha256_bytes(candidate_raw), "string_count": table.string_count}
    if observed != contract.get("expected_candidate"):
        raise MsgdataP1IntegratedError("candidate differs from frozen contract")
    target_path = (output_root / Path(RESOURCE)).resolve()
    if target_path == source_path or not target_path.is_relative_to(output_root):
        raise MsgdataP1IntegratedError("refusing to target Steam installation or escape private output")
    atomic_write(target_path, candidate)
    if target_path.read_bytes() != candidate or source_path.read_bytes() != stock_before:
        raise MsgdataP1IntegratedError("staging write changed unexpected bytes")
    manifest = {
        "schema": MANIFEST_SCHEMA, "source_free": True, "contains_commercial_source_text": False, "contains_complete_game_resource": False,
        "resource": RESOURCE, "active_v6_baseline": dict(STOCK), "merged_audit_bundle": dict(MERGED_BUNDLE),
        "target": observed, "entry_count": len(entries), "effective_change_count": len(changed_ids),
        "effective_change_coordinate_sha256": canonical_hash(changed_ids), "high_confidence_kana_residual_count_after_candidate": residual_after,
        "output": {"relative_path": RESOURCE, "complete_candidate_private_only": True, "installed_game_file_modified": False},
        "checks": {"input_overlays": "OK", "source_hashes": "OK", "esc_printf_newline_pua_whitespace": "OK", "steam_source_unchanged": "OK"},
    }
    atomic_write(output_root / "build_manifest.v1.json", pretty_bytes(manifest))
    return {"candidate_path": str(target_path), "manifest_path": str(output_root / "build_manifest.v1.json"), **observed, "high_confidence_kana_residual_count_after_candidate": residual_after, "installed_game_file_modified": False}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    freeze_parser = commands.add_parser("freeze", help="freeze integrated source-free overlay and contract")
    freeze_parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    stage_parser = commands.add_parser("build", help="build integrated private staging candidate")
    stage_parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    stage_parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = freeze(args.steam_root) if args.command == "freeze" else build_staging_candidate(args.steam_root, args.output_root)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
