#!/usr/bin/env python3
"""Build source-free, private Steam-JP candidates for the final small text tails.

The active Steam JP files are hash-gated read-only inputs.  The only complete
resources this program can write are private staging candidates under
``KR_PATCH_WORK/tmp``.  Public artifacts contain Korean replacements and
source hashes, never commercial Japanese strings or a game resource.
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
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = WORKSTREAM_ROOT.parents[1]
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))
sys.path.insert(0, str(WORKSTREAM_ROOT))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import MessageTable, parse_message_table, rebuild_message_table  # noqa: E402
from translations import EV_STRDATA_REUSE, MSGBRE_REUSE, MSGSTF_DIRECT  # noqa: E402


DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_OUTPUT_BASE = REPO_ROOT / "tmp" / "steam_jp_tail_message_tables_v1"
PUBLIC_ROOT = WORKSTREAM_ROOT / "public"
VALIDATION_ROOT = WORKSTREAM_ROOT / "validation"

SPECS: dict[str, dict[str, Any]] = {
    "ev": {
        "key": "ev",
        "resource": "MSG/JP/ev_strdata.bin",
        "overlay_name": "ev_strdata_ko_base_jp_tail_5.v1.json",
        "overlay_id": "ev_strdata_ko_base_jp_tail_5.v1",
        "stock": {
            "packed_size": 928464,
            "packed_sha256": "9ED892E85AF18EB3BC965A834853969BC06F486A2466A83F3CEBED1B8D5433C0",
            "raw_size": 924812,
            "raw_sha256": "205BA7CA7873411B03C51D1931C277DA9BA8E56700B5EA0D8EDB82B49BD45ABE",
            "string_count": 17868,
        },
        "ids": (3917, 4835, 7260, 8818, 8904),
        "coordinate_sha256": "4D495C297FC9EED9B6E317EC2D4F5718DBD31A1A96B73A200B89E1038D040BE2",
        "source_hashes": {
            3917: "81B3FD52E181F013A72065C4D31CC614EF161E489D18766CD20DA49BA3FE1B8D",
            4835: "716A34A85C23281EBAC8C828ED95D9214E5BBC683F474808ABB3DDECA06315E0",
            7260: "C999C78BF24861002DEF07BA3BA2D0BC0A3690C6E9FA446B9FE716E2F876E953",
            8818: "486A9D15FDF3C39BDF6C23F04EEE748BB0691D5F77155C1678C944A7A8556C14",
            8904: "B45CA1F5D46F3C4922F2EEF9BCDAD88F3663D724F54F209000D3A04318E5BC80",
        },
        "reuse": EV_STRDATA_REUSE,
        "direct": {},
        "catalogs": (
            {
                "relative_path": "workstreams/steam_jp_common_messages_v1/public/msgev_ko_steam_jp_native.v1.json",
                "sha256": "47742330C4375A6BB6AC19ED0F7E8040CF57E22EF39BEDEE7FF4959520B1575C",
            },
        ),
        "global_residual_after": 0,
    },
    "bre": {
        "key": "bre",
        "resource": "MSG_PK/JP/msgbre.bin",
        "overlay_name": "msgbre_ko_pk_jp_tail_1.v1.json",
        "overlay_id": "msgbre_ko_pk_jp_tail_1.v1",
        "stock": {
            "packed_size": 478527,
            "packed_sha256": "EA797D2B4098756941A1922DF154786B5734A7ED9564F2E6C21695AD4AE93167",
            "raw_size": 476632,
            "raw_sha256": "D4B1BAB427E93FD7049BBFCA86376EFBE44454B53EFADAE81A703BC67B8C11A5",
            "string_count": 3000,
        },
        "ids": (1950,),
        "coordinate_sha256": "231487657C5CDD301217A96F5F9B5BA6286A459D36713E5B839AC706A8EADE7C",
        "source_hashes": {1950: "ABF97E2E3C84E2825964CC26FF516177690202C89085E98C9A8CDDF79CE28890"},
        "reuse": MSGBRE_REUSE,
        "direct": {},
        "catalogs": (
            {
                "relative_path": "workstreams/steam_jp_strdata_p0_b04_v1/public/strdata_ko_steam_jp_p0_b04_350.v1.json",
                "sha256": "EF45441B5DAB00B6F569A3FD5F6BF4538F2FE0E02DE1512FEE60B4C65A8A92F2",
            },
        ),
        "global_residual_after": 0,
    },
    "stf": {
        "key": "stf",
        "resource": "MSG_PK/JP/msgstf.bin",
        "overlay_name": "msgstf_ko_pk_jp_tail_1.v1.json",
        "overlay_id": "msgstf_ko_pk_jp_tail_1.v1",
        "stock": {
            "packed_size": 17104,
            "packed_sha256": "FE97F9C0C34D0131D7CDD3CEC4AF4B453CC7148F34FD80E7EFD31DE500F12593",
            "raw_size": 17012,
            "raw_sha256": "C55F20A4F02F95D2ABAFC1A68FD9A84F407743028202B6BE41CF169872C0075A",
            "string_count": 20,
        },
        "ids": (5,),
        "coordinate_sha256": "69520AE1328FAAB60B590D1EDC2EAD38872FDD97C4FE4DA0A3425064D94CF585",
        "source_hashes": {5: "DF1FC37E37CA7F1B6411222C309ED038FD30B6C6F8C7B6FF0B3ECD39A0FC4235"},
        "reuse": {},
        "direct": MSGSTF_DIRECT,
        "catalogs": (),
        "global_residual_after": 0,
    },
}

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


class TailMessageTablesError(ValueError):
    """Raised when a source, token, or staging policy gate fails."""


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
            raise TailMessageTablesError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def read_json(path: Path) -> tuple[dict[str, Any], bytes]:
    blob = path.read_bytes()
    try:
        value = json.loads(blob.decode("utf-8"), object_pairs_hook=strict_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise TailMessageTablesError(f"invalid JSON: {path}") from error
    if not isinstance(value, dict):
        raise TailMessageTablesError(f"JSON root must be an object: {path}")
    return value, blob


def path_from_repo(relative: str) -> Path:
    path = Path(relative)
    if not relative or path.is_absolute() or ".." in path.parts or "\\" in relative:
        raise TailMessageTablesError("repository-relative path is unsafe")
    resolved = (REPO_ROOT / path).resolve()
    if not resolved.is_relative_to(REPO_ROOT.resolve()):
        raise TailMessageTablesError("repository-relative path escapes workspace")
    return resolved


def spec_paths(spec: Mapping[str, Any]) -> tuple[Path, Path, Path]:
    overlay = PUBLIC_ROOT / str(spec["overlay_name"])
    validation = VALIDATION_ROOT / f"{spec['key']}.v1.json"
    contract = WORKSTREAM_ROOT / f"source_free_contract.{spec['key']}.v1.json"
    return overlay, validation, contract


def schema(spec: Mapping[str, Any], suffix: str) -> str:
    return f"nobu16.kr.steam-jp-tail-{spec['key']}-{suffix}.v1"


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
        "leading_whitespace": text[: len(text) - len(text.lstrip())],
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
        "ideographic_space_count": text.count("　"),
    }


def mismatch_keys(source: str, replacement: str) -> list[str]:
    before = message_invariants(source)
    after = message_invariants(replacement)
    return [key for key in INVARIANT_KEYS if before[key] != after[key]]


def require_spec_shape(spec: Mapping[str, Any], table: MessageTable) -> None:
    ids = tuple(spec["ids"])
    if not ids or tuple(sorted(set(ids))) != ids:
        raise TailMessageTablesError(f"{spec['key']} coordinate IDs must be sorted and unique")
    if canonical_hash([{"id": entry_id} for entry_id in ids]) != spec["coordinate_sha256"]:
        raise TailMessageTablesError(f"{spec['key']} coordinate contract differs")
    if any(entry_id < 0 or entry_id >= table.string_count for entry_id in ids):
        raise TailMessageTablesError(f"{spec['key']} coordinate is outside table")
    if any(not is_high_confidence_japanese(table.texts[entry_id]) for entry_id in ids):
        raise TailMessageTablesError(f"{spec['key']} is no longer an active JP residual set")
    source_hashes = spec["source_hashes"]
    if set(source_hashes) != set(ids):
        raise TailMessageTablesError(f"{spec['key']} source hash coverage differs")
    for entry_id in ids:
        if source_hashes[entry_id] != text_hash(table.texts[entry_id]):
            raise TailMessageTablesError(f"{spec['key']} source text identity differs at id {entry_id}")
    reuse_ids = set(spec["reuse"])
    direct_ids = set(spec["direct"])
    if reuse_ids & direct_ids or reuse_ids | direct_ids != set(ids):
        raise TailMessageTablesError(f"{spec['key']} reuse/direct partitions differ")


def load_stock(spec: Mapping[str, Any], steam_root: Path) -> tuple[Path, bytes, bytes, MessageTable]:
    root = steam_root.resolve()
    source_path = (root / Path(str(spec["resource"]))).resolve()
    if not source_path.is_relative_to(root) or not source_path.is_file():
        raise TailMessageTablesError(f"active JP resource does not exist: {source_path}")
    packed = source_path.read_bytes()
    stock = spec["stock"]
    if len(packed) != stock["packed_size"] or sha256_bytes(packed) != stock["packed_sha256"]:
        raise TailMessageTablesError(f"active Steam JP {spec['key']} packed baseline differs")
    _header, raw = decompress_wrapper(packed)
    if len(raw) != stock["raw_size"] or sha256_bytes(raw) != stock["raw_sha256"]:
        raise TailMessageTablesError(f"active Steam JP {spec['key']} raw baseline differs")
    table = parse_message_table(raw)
    if table.string_count != stock["string_count"] or rebuild_message_table(table, table.texts) != raw:
        raise TailMessageTablesError(f"active Steam JP {spec['key']} structure differs")
    require_spec_shape(spec, table)
    return source_path, packed, raw, table


def exact_reuse_values(spec: Mapping[str, Any], table: MessageTable) -> dict[int, str]:
    expected_reuse: Mapping[int, str] = spec["reuse"]
    if not expected_reuse:
        return {}
    ids_by_hash: dict[str, set[int]] = defaultdict(set)
    for entry_id in expected_reuse:
        ids_by_hash[text_hash(table.texts[entry_id])].add(entry_id)
    found: dict[int, set[str]] = defaultdict(set)
    for catalog_pin in spec["catalogs"]:
        path = path_from_repo(str(catalog_pin["relative_path"]))
        catalog, blob = read_json(path)
        if sha256_bytes(blob) != catalog_pin["sha256"]:
            raise TailMessageTablesError(f"pinned reuse catalogue differs: {catalog_pin['relative_path']}")
        entries = catalog.get("entries")
        if not isinstance(entries, list):
            raise TailMessageTablesError(f"reuse catalogue has no entry list: {catalog_pin['relative_path']}")
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("ko"), str):
                continue
            source_hash = entry.get("source_jp_utf16le_sha256")
            if not isinstance(source_hash, str):
                continue
            for entry_id in ids_by_hash.get(source_hash.upper(), set()):
                found[entry_id].add(entry["ko"])
    reuse: dict[int, str] = {}
    for entry_id, expected in expected_reuse.items():
        values = found.get(entry_id, set())
        if values != {expected}:
            raise TailMessageTablesError(f"exact source-hash reuse differs at {spec['key']} id {entry_id}")
        reuse[entry_id] = expected
    return reuse


def validate_replacement(source: str, ko: str, entry_id: int) -> None:
    if not isinstance(ko, str) or not ko or "\0" in ko or "\ufffd" in ko:
        raise TailMessageTablesError(f"unsafe Korean replacement at id {entry_id}")
    if CJK_OR_KANA_RE.search(ko):
        raise TailMessageTablesError(f"Korean replacement retains CJK/kana at id {entry_id}")
    mismatch = mismatch_keys(source, ko)
    if mismatch:
        raise TailMessageTablesError(f"format/token mismatch at id {entry_id}: {mismatch!r}")


def build_entries(spec: Mapping[str, Any], table: MessageTable) -> list[dict[str, Any]]:
    reuse = exact_reuse_values(spec, table)
    entries: list[dict[str, Any]] = []
    for entry_id in spec["ids"]:
        source = table.texts[entry_id]
        if entry_id in reuse:
            ko = reuse[entry_id]
            origin = "exact_source_hash_catalog_reuse"
        else:
            ko = spec["direct"][entry_id]
            origin = "project_direct_translation"
        validate_replacement(source, ko, entry_id)
        entries.append({
            "id": entry_id,
            "source_jp_utf16le_sha256": text_hash(source),
            "ko": ko,
            "ko_utf16le_sha256": text_hash(ko),
            "format_signature_sha256": canonical_hash(message_invariants(source)),
            "translation_origin": origin,
        })
    return entries


def validate_entries(spec: Mapping[str, Any], table: MessageTable, entries: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    required = {"id", "source_jp_utf16le_sha256", "ko", "ko_utf16le_sha256", "format_signature_sha256", "translation_origin"}
    ids = tuple(spec["ids"])
    if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes)) or len(entries) != len(ids):
        raise TailMessageTablesError("entry list count differs")
    normalized: list[dict[str, Any]] = []
    for entry_id, entry in zip(ids, entries, strict=True):
        if not isinstance(entry, Mapping) or set(entry) != required or entry.get("id") != entry_id:
            raise TailMessageTablesError("entry schema or order differs")
        source = table.texts[entry_id]
        source_hash = entry["source_jp_utf16le_sha256"]
        ko = entry["ko"]
        if not isinstance(source_hash, str) or not HEX64_RE.fullmatch(source_hash) or source_hash != text_hash(source):
            raise TailMessageTablesError(f"JP source hash differs at id {entry_id}")
        if source_hash != spec["source_hashes"][entry_id]:
            raise TailMessageTablesError(f"pinned JP source hash differs at id {entry_id}")
        if not isinstance(ko, str) or entry.get("ko_utf16le_sha256") != text_hash(ko):
            raise TailMessageTablesError(f"Korean hash differs at id {entry_id}")
        if entry.get("format_signature_sha256") != canonical_hash(message_invariants(source)):
            raise TailMessageTablesError(f"format signature differs at id {entry_id}")
        expected_origin = "exact_source_hash_catalog_reuse" if entry_id in spec["reuse"] else "project_direct_translation"
        if entry.get("translation_origin") != expected_origin:
            raise TailMessageTablesError(f"translation origin differs at id {entry_id}")
        expected = spec["reuse"].get(entry_id, spec["direct"].get(entry_id))
        if ko != expected:
            raise TailMessageTablesError(f"expected Korean value differs at id {entry_id}")
        validate_replacement(source, ko, entry_id)
        normalized.append(dict(entry))
    return normalized


def reuse_catalog_header(spec: Mapping[str, Any]) -> list[dict[str, str]]:
    return [dict(item) for item in spec["catalogs"]]


def make_overlay(spec: Mapping[str, Any], entries: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    origins = Counter(str(entry["translation_origin"]) for entry in entries)
    return {
        "schema": schema(spec, "overlay"),
        "overlay_id": spec["overlay_id"],
        "resource": spec["resource"],
        "base_language": "JP",
        "distribution_policy": {"contains_commercial_source_text": False, "contains_complete_game_resource": False, "sc_container_used": False},
        "active_v6_baseline": dict(spec["stock"]),
        "audit_bundle": {"coordinate_sha256": spec["coordinate_sha256"], "entry_ids": list(spec["ids"])},
        "exact_reuse_catalogs": reuse_catalog_header(spec),
        "entry_count": len(entries),
        "translation_origin_counts": dict(sorted(origins.items())),
        "entries": list(entries),
    }


def validate_public_overlay(spec: Mapping[str, Any], value: Mapping[str, Any], table: MessageTable) -> list[dict[str, Any]]:
    required = {
        "schema", "overlay_id", "resource", "base_language", "distribution_policy", "active_v6_baseline", "audit_bundle",
        "exact_reuse_catalogs", "entry_count", "translation_origin_counts", "entries",
    }
    expected_bundle = {"coordinate_sha256": spec["coordinate_sha256"], "entry_ids": list(spec["ids"])}
    if set(value) != required or value.get("schema") != schema(spec, "overlay") or value.get("overlay_id") != spec["overlay_id"]:
        raise TailMessageTablesError("public overlay header differs")
    if value.get("resource") != spec["resource"] or value.get("base_language") != "JP":
        raise TailMessageTablesError("public overlay route differs")
    if value.get("distribution_policy") != {"contains_commercial_source_text": False, "contains_complete_game_resource": False, "sc_container_used": False}:
        raise TailMessageTablesError("public overlay distribution policy differs")
    if value.get("active_v6_baseline") != spec["stock"] or value.get("audit_bundle") != expected_bundle:
        raise TailMessageTablesError("public overlay baseline or audit differs")
    if value.get("exact_reuse_catalogs") != reuse_catalog_header(spec):
        raise TailMessageTablesError("public overlay reuse pins differ")
    entries_value = value.get("entries")
    if not isinstance(entries_value, list) or value.get("entry_count") != len(entries_value):
        raise TailMessageTablesError("public overlay entry count differs")
    entries = validate_entries(spec, table, entries_value)
    expected_origins = dict(sorted(Counter(str(entry["translation_origin"]) for entry in entries).items()))
    if value.get("translation_origin_counts") != expected_origins:
        raise TailMessageTablesError("public overlay origin counts differ")
    return entries


def candidate_from_entries(spec: Mapping[str, Any], packed: bytes, raw: bytes, table: MessageTable, entries: Sequence[Mapping[str, Any]]) -> tuple[bytes, bytes, list[int], int]:
    normalized = validate_entries(spec, table, entries)
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
        raise TailMessageTablesError("raw candidate is not deterministic")
    candidate_a = recompress_wrapper(rebuilt_raw_a, packed)
    candidate_b = recompress_wrapper(rebuilt_raw_b, packed)
    if candidate_a != candidate_b:
        raise TailMessageTablesError("packed candidate is not deterministic")
    _header, checked_raw = decompress_wrapper(candidate_a)
    checked_table = parse_message_table(checked_raw)
    if checked_raw != rebuilt_raw_a or checked_table.texts != tuple(target_texts):
        raise TailMessageTablesError("candidate parser/decompression roundtrip differs")
    if (
        checked_table.string_count != table.string_count
        or checked_table.block_offset != table.block_offset
        or checked_table.table_offset != table.table_offset
        or checked_table.table_size != table.table_size
        or checked_table.string_start != table.string_start
        or rebuild_message_table(checked_table, checked_table.texts) != checked_raw
    ):
        raise TailMessageTablesError("candidate table structure differs")
    selected = {int(entry["id"]): str(entry["ko"]) for entry in normalized}
    for entry_id, source in enumerate(table.texts):
        expected = selected.get(entry_id, source)
        if checked_table.texts[entry_id] != expected:
            raise TailMessageTablesError(f"candidate text differs at id {entry_id}")
        if entry_id not in selected and source.encode("utf-16le") + b"\0\0" != checked_table.texts[entry_id].encode("utf-16le") + b"\0\0":
            raise TailMessageTablesError(f"nonselected UTF-16LE payload differs at id {entry_id}")
    if any(is_high_confidence_japanese(checked_table.texts[entry_id]) for entry_id in spec["ids"]):
        raise TailMessageTablesError("selected bundle retains a high-confidence Japanese value")
    residual_after = sum(is_high_confidence_japanese(text) for text in checked_table.texts)
    if residual_after != spec["global_residual_after"]:
        raise TailMessageTablesError("high-confidence Japanese residual total differs outside selected bundle")
    stock_prefix = bytearray(raw[:table.table_offset])
    candidate_prefix = bytearray(checked_raw[:checked_table.table_offset])
    struct.pack_into("<I", stock_prefix, 8, 0)
    struct.pack_into("<I", candidate_prefix, 8, 0)
    if stock_prefix != candidate_prefix:
        raise TailMessageTablesError("opaque prefix differs outside logical-size field")
    return candidate_a, rebuilt_raw_a, changed_ids, residual_after


def make_validation(spec: Mapping[str, Any], entries: Sequence[Mapping[str, Any]], candidate: bytes, candidate_raw: bytes, changed_ids: Sequence[int], residual_after: int) -> dict[str, Any]:
    origins = Counter(str(entry["translation_origin"]) for entry in entries)
    return {
        "schema": schema(spec, "validation"),
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "resource": spec["resource"],
        "active_v6_baseline": dict(spec["stock"]),
        "audit_bundle": {"coordinate_sha256": spec["coordinate_sha256"], "entry_ids": list(spec["ids"])},
        "entry_count": len(entries),
        "translation_origin_counts": dict(sorted(origins.items())),
        "expected_candidate": {"packed_size": len(candidate), "packed_sha256": sha256_bytes(candidate), "raw_size": len(candidate_raw), "raw_sha256": sha256_bytes(candidate_raw)},
        "effective_change_count": len(changed_ids),
        "effective_change_coordinate_sha256": canonical_hash(list(changed_ids)),
        "high_confidence_kana_residual_count_after_candidate": residual_after,
        "checks": {
            "active_v6_baseline": "OK", "coordinate_contract": "OK", "exact_source_hash_catalog_reuse": "OK",
            "per_entry_jp_source_hashes": "OK", "token_and_format_profiles": "OK", "raw_deterministic_rebuild": "OK",
            "packed_deterministic_rebuild": "OK", "candidate_parser_roundtrip": "OK", "nonselected_utf16le_payloads": "OK",
            "selected_high_confidence_kana_residuals": "0", "steam_installation_written": False, "sc_container_used": False,
            "release_asset_written": False, "github_written": False,
        },
    }


def relative_from_repo(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def make_contract(spec: Mapping[str, Any], overlay_path: Path, validation_path: Path, overlay_blob: bytes, validation_blob: bytes, candidate: bytes, candidate_raw: bytes, entries: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "schema": schema(spec, "contract"),
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "resource": spec["resource"],
        "runtime_route": {"language": "JP", "sc_container_used": False, "installed_game_file_written": False},
        "active_v6_baseline": dict(spec["stock"]),
        "audit_bundle": {"coordinate_sha256": spec["coordinate_sha256"], "entry_ids": list(spec["ids"])},
        "overlay": {"relative_path": relative_from_repo(overlay_path), "sha256": sha256_bytes(overlay_blob), "entry_count": len(entries)},
        "validation": {"relative_path": relative_from_repo(validation_path), "sha256": sha256_bytes(validation_blob)},
        "expected_candidate": {"packed_size": len(candidate), "packed_sha256": sha256_bytes(candidate), "raw_size": len(candidate_raw), "raw_sha256": sha256_bytes(candidate_raw), "string_count": spec["stock"]["string_count"]},
        "output_policy": {"complete_candidate_private_only": True, "allowed_root": "tmp", "relative_path": spec["resource"]},
        "proofs": {
            "active_v6_baseline_pinned": True, "catalog_reuse_exact_source_hash_only": True,
            "per_entry_jp_source_hash_gated": True, "format_and_token_profile_preserved": True,
            "nonselected_utf16le_payloads_preserved": True, "parser_roundtrip_valid": True,
            "deterministic_raw_and_packed_rebuild": True, "steam_installation_read_only": True,
        },
    }


def assert_source_free(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if CJK_OR_KANA_RE.search(text) or "MSG_PK/SC" in text or "RES_SC" in text or "source_sc" in text.casefold():
        raise TailMessageTablesError(f"public artifact is not JP-route source-free: {path}")


def require_private_output_root(output_root: Path) -> Path:
    resolved = output_root.resolve()
    private_root = (REPO_ROOT / "tmp").resolve()
    if not resolved.is_relative_to(private_root) or resolved == private_root:
        raise TailMessageTablesError("complete candidate output must be a child below KR_PATCH_WORK/tmp")
    return resolved


def freeze_one(spec: Mapping[str, Any], steam_root: Path) -> dict[str, Any]:
    _source_path, packed, raw, table = load_stock(spec, steam_root)
    entries = build_entries(spec, table)
    candidate, candidate_raw, changed_ids, residual_after = candidate_from_entries(spec, packed, raw, table, entries)
    overlay_path, validation_path, contract_path = spec_paths(spec)
    overlay_blob = pretty_bytes(make_overlay(spec, entries))
    validation_blob = pretty_bytes(make_validation(spec, entries, candidate, candidate_raw, changed_ids, residual_after))
    contract_blob = pretty_bytes(make_contract(spec, overlay_path, validation_path, overlay_blob, validation_blob, candidate, candidate_raw, entries))
    atomic_write(overlay_path, overlay_blob)
    atomic_write(validation_path, validation_blob)
    atomic_write(contract_path, contract_blob)
    for path in (overlay_path, validation_path, contract_path):
        assert_source_free(path)
    return {
        "entry_count": len(entries), "catalog_reuse_count": len(spec["reuse"]), "direct_translation_count": len(spec["direct"]),
        "candidate_sha256": sha256_bytes(candidate), "candidate_raw_sha256": sha256_bytes(candidate_raw),
        "high_confidence_kana_residual_count_after_candidate": residual_after, "installed_game_file_modified": False,
    }


def load_frozen_inputs(spec: Mapping[str, Any], steam_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], bytes, bytes, MessageTable]:
    _source_path, packed, raw, table = load_stock(spec, steam_root)
    overlay_path, validation_path, contract_path = spec_paths(spec)
    contract, _contract_blob = read_json(contract_path)
    required = {
        "schema", "source_free", "contains_commercial_source_text", "contains_complete_game_resource", "resource", "runtime_route",
        "active_v6_baseline", "audit_bundle", "overlay", "validation", "expected_candidate", "output_policy", "proofs",
    }
    expected_bundle = {"coordinate_sha256": spec["coordinate_sha256"], "entry_ids": list(spec["ids"])}
    if set(contract) != required or contract.get("schema") != schema(spec, "contract") or contract.get("resource") != spec["resource"]:
        raise TailMessageTablesError("frozen contract header differs")
    if contract.get("active_v6_baseline") != spec["stock"] or contract.get("audit_bundle") != expected_bundle:
        raise TailMessageTablesError("frozen contract baseline or audit differs")
    if contract.get("runtime_route") != {"language": "JP", "sc_container_used": False, "installed_game_file_written": False}:
        raise TailMessageTablesError("frozen contract route differs")
    if contract.get("output_policy") != {"complete_candidate_private_only": True, "allowed_root": "tmp", "relative_path": spec["resource"]}:
        raise TailMessageTablesError("frozen contract output policy differs")
    if not isinstance(contract.get("proofs"), dict) or any(value is not True for value in contract["proofs"].values()):
        raise TailMessageTablesError("frozen contract proofs are incomplete")
    overlay_value = contract.get("overlay")
    validation_value = contract.get("validation")
    if not isinstance(overlay_value, dict) or not isinstance(validation_value, dict):
        raise TailMessageTablesError("frozen contract artifact locator differs")
    if overlay_value.get("relative_path") != relative_from_repo(overlay_path) or validation_value.get("relative_path") != relative_from_repo(validation_path):
        raise TailMessageTablesError("frozen contract artifact path differs")
    overlay, overlay_blob = read_json(overlay_path)
    if sha256_bytes(overlay_blob) != overlay_value.get("sha256"):
        raise TailMessageTablesError("frozen overlay hash differs")
    entries = validate_public_overlay(spec, overlay, table)
    validation_blob = validation_path.read_bytes()
    if sha256_bytes(validation_blob) != validation_value.get("sha256"):
        raise TailMessageTablesError("frozen validation hash differs")
    for path in (overlay_path, validation_path, contract_path):
        assert_source_free(path)
    return contract, entries, packed, raw, table


def build_staging_candidate(spec: Mapping[str, Any], steam_root: Path, output_root: Path) -> dict[str, Any]:
    output_root = require_private_output_root(output_root)
    source_path, stock_before, _raw_before, _table_before = load_stock(spec, steam_root)
    contract, entries, packed, raw, table = load_frozen_inputs(spec, steam_root)
    if packed != stock_before:
        raise TailMessageTablesError("active Steam JP source changed while loading frozen inputs")
    candidate, candidate_raw, changed_ids, residual_after = candidate_from_entries(spec, packed, raw, table, entries)
    observed = {
        "packed_size": len(candidate), "packed_sha256": sha256_bytes(candidate),
        "raw_size": len(candidate_raw), "raw_sha256": sha256_bytes(candidate_raw), "string_count": table.string_count,
    }
    if observed != contract.get("expected_candidate"):
        raise TailMessageTablesError("candidate differs from frozen deterministic contract")
    target_path = (output_root / Path(str(spec["resource"]))).resolve()
    if target_path == source_path or not target_path.is_relative_to(output_root):
        raise TailMessageTablesError("refusing to target Steam installation or escape private output")
    atomic_write(target_path, candidate)
    if target_path.read_bytes() != candidate or source_path.read_bytes() != stock_before:
        raise TailMessageTablesError("staging write changed unexpected bytes")
    manifest = {
        "schema": schema(spec, "build-manifest"), "source_free": True, "contains_commercial_source_text": False, "contains_complete_game_resource": False,
        "resource": spec["resource"], "active_v6_baseline": dict(spec["stock"]), "target": observed, "entry_count": len(entries),
        "coordinate_sha256": spec["coordinate_sha256"], "effective_change_count": len(changed_ids),
        "effective_change_coordinate_sha256": canonical_hash(changed_ids),
        "high_confidence_kana_residual_count_after_candidate": residual_after,
        "output": {"relative_path": spec["resource"], "complete_candidate_private_only": True, "installed_game_file_modified": False},
        "checks": {"contract_hash": "OK", "exact_catalog_reuse": "OK", "source_hash_gates": "OK", "token_profiles": "OK", "steam_source_unchanged": "OK"},
    }
    atomic_write(output_root / "build_manifest.v1.json", pretty_bytes(manifest))
    return {
        "candidate_path": str(target_path), "manifest_path": str(output_root / "build_manifest.v1.json"),
        **observed, "high_confidence_kana_residual_count_after_candidate": residual_after, "installed_game_file_modified": False,
    }


def selected_specs(target: str) -> tuple[dict[str, Any], ...]:
    if target == "all":
        return tuple(SPECS[key] for key in ("ev", "bre", "stf"))
    return (SPECS[target],)


def output_root_for(spec: Mapping[str, Any], target: str, supplied: Path | None) -> Path:
    if supplied is None:
        return DEFAULT_OUTPUT_BASE / str(spec["key"]) / "candidate"
    if target == "all":
        return supplied / str(spec["key"]) / "candidate"
    return supplied


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (("freeze", "freeze source-free overlays, validations, and contracts"), ("build", "build private staging candidates from frozen inputs")):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("--target", choices=("all", "ev", "bre", "stf"), default="all")
        command.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
        if name == "build":
            command.add_argument("--output-root", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    results: dict[str, dict[str, Any]] = {}
    for spec in selected_specs(args.target):
        if args.command == "freeze":
            results[str(spec["key"])] = freeze_one(spec, args.steam_root)
        else:
            results[str(spec["key"])] = build_staging_candidate(spec, args.steam_root, output_root_for(spec, args.target, args.output_root))
    print(json.dumps(results, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
