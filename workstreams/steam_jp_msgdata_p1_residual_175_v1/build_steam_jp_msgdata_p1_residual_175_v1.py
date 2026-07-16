#!/usr/bin/env python3
"""Freeze and build a private JP-native candidate for msgdata P1 bundle 01.

The active Steam JP file is input only.  Existing Korean text is reused only
when its published JP source hash exactly equals the active JP text.  All other
coordinates are project-authored direct translations.  Complete game-resource
output is restricted to ``KR_PATCH_WORK/tmp``.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import runpy
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
sys.path.insert(0, str(WORKSTREAM_ROOT))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import MessageTable, parse_message_table, rebuild_message_table  # noqa: E402
_TRANSLATIONS = runpy.run_path(str(WORKSTREAM_ROOT / "translations.py"))
BUNDLE_IDS = _TRANSLATIONS["BUNDLE_IDS"]
DIRECT_TRANSLATIONS = _TRANSLATIONS["DIRECT_TRANSLATIONS"]
EXPECTED_REUSE_IDS = _TRANSLATIONS["EXPECTED_REUSE_IDS"]


RESOURCE = "MSG_PK/JP/msgdata.bin"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "tmp" / "steam_jp_msgdata_p1_residual_175_v1" / "candidate"
PUBLIC_OVERLAY = WORKSTREAM_ROOT / "public" / "msgdata_ko_pk_jp_p1_residual_175.v1.json"
VALIDATION = WORKSTREAM_ROOT / "validation.v1.json"
CONTRACT = WORKSTREAM_ROOT / "source_free_contract.v1.json"
REUSE_CATALOG_RELATIVE = "workstreams/steam_jp_common_messages_v1/public/msgdata_ko_steam_jp_native.v1.json"
REUSE_CATALOG_SHA256 = "09EC40029C55D09D1420812879180DFDC9B8842BE5D374C6676189067772D051"

STOCK = {
    "packed_size": 496999,
    "packed_sha256": "2D1BEFF03972777FBA5EE0B8FEF24E6A03B285DA466A4DA439794D21587A0F69",
    "raw_size": 495032,
    "raw_sha256": "25593167A47B5B0F69357F71E5E9882382F346AEF1B8DCA7DB6902D7E270AB67",
    "string_count": 29218,
}
BUNDLE_COORDINATE_SHA256 = "9884F706F0C8C283895E74B02EBA06E6C832E5733142FB58DB7AA37F44D6EE1D"

OVERLAY_SCHEMA = "nobu16.kr.steam-jp-msgdata-p1-residual-overlay.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-msgdata-p1-residual-validation.v1"
CONTRACT_SCHEMA = "nobu16.kr.steam-jp-msgdata-p1-residual-contract.v1"
MANIFEST_SCHEMA = "nobu16.kr.steam-jp-msgdata-p1-residual-build-manifest.v1"

HEX64_RE = re.compile(r"[0-9A-F]{64}\Z")
KANA_RE = re.compile(r"[\u3040-\u30ff\uff66-\uff9f]")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
CJK_OR_KANA_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uf900-\ufaff]")
PRINTF_RE = re.compile(
    r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
LINE_BREAK_RE = re.compile(r"\r\n|\n|\r")
NON_SEMANTIC_CATEGORIES = frozenset(("Cc", "Cf", "Cs", "Mn", "Me", "Zl", "Zp", "Zs", "Cn"))
INVARIANT_KEYS = (
    "printf", "unknown_percent_count", "leading_whitespace", "trailing_whitespace", "esc", "controls",
    "line_breaks", "pua", "greek_symbols", "box_drawing_symbols", "ideographic_space_count",
)


class MsgdataP1Error(ValueError):
    """Raised for any failed baseline, reuse, format, or output proof."""


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
    result: dict[str, Any] = {}
    folded: dict[str, str] = {}
    for key, value in pairs:
        collision = folded.get(key.casefold())
        if collision is not None:
            raise MsgdataP1Error(f"duplicate or case-colliding JSON key: {collision!r}/{key!r}")
        folded[key.casefold()] = key
        result[key] = value
    return result


def read_json(path: Path) -> tuple[dict[str, Any], bytes]:
    blob = path.read_bytes()
    try:
        value = json.loads(blob.decode("utf-8-sig"), object_pairs_hook=strict_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MsgdataP1Error(f"invalid JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise MsgdataP1Error(f"JSON root must be an object: {path}")
    return value, blob


def is_high_confidence_japanese(text: str) -> bool:
    return bool(KANA_RE.search(text)) and not bool(HANGUL_RE.search(text))


def message_invariants(text: str) -> dict[str, Any]:
    printf_matches = list(PRINTF_RE.finditer(text))
    percent_offsets = {index for match in printf_matches for index in range(match.start(), match.end()) if text[index] == "%"}
    esc_matches = list(ESC_RE.finditer(text))
    esc_offsets = {index for match in esc_matches for index in range(match.start(), match.end())}
    return {
        "printf": [match.group(0) for match in printf_matches],
        "unknown_percent_count": sum(1 for index, char in enumerate(text) if char == "%" and index not in percent_offsets),
        "leading_whitespace": text[: len(text) - len(text.lstrip())],
        "trailing_whitespace": text[len(text.rstrip()) :],
        "esc": [match.group(0) for match in esc_matches],
        "controls": [
            f"U+{ord(char):04X}" for index, char in enumerate(text)
            if unicodedata.category(char) == "Cc" and char not in ("\r", "\n") and index not in esc_offsets
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


def require_bundle_shape(table: MessageTable) -> None:
    if len(BUNDLE_IDS) != 175 or tuple(sorted(set(BUNDLE_IDS))) != BUNDLE_IDS:
        raise MsgdataP1Error("P1 coordinate list must contain 175 sorted unique IDs")
    if canonical_hash([{"id": entry_id} for entry_id in BUNDLE_IDS]) != BUNDLE_COORDINATE_SHA256:
        raise MsgdataP1Error("P1 coordinate list differs from audit contract")
    if any(entry_id < 0 or entry_id >= table.string_count for entry_id in BUNDLE_IDS):
        raise MsgdataP1Error("P1 coordinate is outside active msgdata table")
    if [entry_id for entry_id in BUNDLE_IDS if not is_high_confidence_japanese(table.texts[entry_id])]:
        raise MsgdataP1Error("P1 coordinate no longer matches a high-confidence active Japanese source")
    if tuple(sorted(set(EXPECTED_REUSE_IDS))) != EXPECTED_REUSE_IDS:
        raise MsgdataP1Error("expected reuse IDs must be sorted and unique")
    if not set(EXPECTED_REUSE_IDS).issubset(BUNDLE_IDS):
        raise MsgdataP1Error("expected reuse ID is outside the P1 bundle")
    direct_ids = set(BUNDLE_IDS) - set(EXPECTED_REUSE_IDS)
    if set(DIRECT_TRANSLATIONS) != direct_ids:
        raise MsgdataP1Error("direct translations must exactly cover only non-reuse P1 IDs")


def load_stock(steam_root: Path) -> tuple[Path, bytes, bytes, MessageTable]:
    source_path = (steam_root.resolve() / Path(RESOURCE)).resolve()
    if not source_path.is_file():
        raise MsgdataP1Error(f"active JP resource does not exist: {source_path}")
    packed = source_path.read_bytes()
    if len(packed) != STOCK["packed_size"] or sha256_bytes(packed) != STOCK["packed_sha256"]:
        raise MsgdataP1Error("active Steam JP msgdata packed baseline does not match v6 pin")
    _header, raw = decompress_wrapper(packed)
    if len(raw) != STOCK["raw_size"] or sha256_bytes(raw) != STOCK["raw_sha256"]:
        raise MsgdataP1Error("active Steam JP msgdata raw baseline does not match v6 pin")
    table = parse_message_table(raw)
    if table.string_count != STOCK["string_count"] or rebuild_message_table(table, table.texts) != raw:
        raise MsgdataP1Error("active Steam JP msgdata structure does not match v6 pin")
    require_bundle_shape(table)
    return source_path, packed, raw, table


def reuse_catalog_path() -> Path:
    path = (REPO_ROOT / REUSE_CATALOG_RELATIVE).resolve()
    if not path.is_relative_to(REPO_ROOT.resolve()):
        raise MsgdataP1Error("reuse catalog path escapes repository")
    return path


def exact_reuse_values(table: MessageTable) -> dict[int, str]:
    catalog_path = reuse_catalog_path()
    catalog, blob = read_json(catalog_path)
    if sha256_bytes(blob) != REUSE_CATALOG_SHA256:
        raise MsgdataP1Error("pinned JP-native reuse catalog hash differs")
    if catalog.get("resource") != RESOURCE or not isinstance(catalog.get("entries"), list):
        raise MsgdataP1Error("reuse catalog is not MSG_PK/JP/msgdata")
    wanted_by_hash = {text_hash(table.texts[entry_id]): entry_id for entry_id in BUNDLE_IDS}
    matches: dict[int, set[str]] = {}
    for entry in catalog["entries"]:
        if not isinstance(entry, dict) or not isinstance(entry.get("ko"), str):
            continue
        source_hash = entry.get("source_jp_utf16le_sha256")
        if not isinstance(source_hash, str):
            continue
        entry_id = wanted_by_hash.get(source_hash.upper())
        if entry_id is not None:
            matches.setdefault(entry_id, set()).add(entry["ko"])
    reuse: dict[int, str] = {}
    for entry_id, values in matches.items():
        if len(values) != 1:
            raise MsgdataP1Error(f"reuse catalog has conflicting Korean values at id {entry_id}")
        reuse[entry_id] = next(iter(values))
    if tuple(sorted(reuse)) != EXPECTED_REUSE_IDS:
        raise MsgdataP1Error(f"exact source-hash reuse set differs: {sorted(reuse)!r}")
    return reuse


def validate_replacement(source: str, ko: str, entry_id: int) -> None:
    if not isinstance(ko, str) or not ko or "\0" in ko or "\ufffd" in ko:
        raise MsgdataP1Error(f"unsafe Korean replacement at id {entry_id}")
    if CJK_OR_KANA_RE.search(ko):
        raise MsgdataP1Error(f"Korean replacement retains CJK/kana at id {entry_id}")
    mismatch = mismatch_keys(source, ko)
    if mismatch:
        raise MsgdataP1Error(f"format/token mismatch at id {entry_id}: {mismatch!r}")


def build_entries(table: MessageTable) -> list[dict[str, Any]]:
    reuse = exact_reuse_values(table)
    entries: list[dict[str, Any]] = []
    for entry_id in BUNDLE_IDS:
        source = table.texts[entry_id]
        if entry_id in reuse:
            ko = reuse[entry_id]
            origin = "exact_source_hash_catalog_reuse"
        else:
            ko = DIRECT_TRANSLATIONS[entry_id]
            origin = "project_direct_translation"
        validate_replacement(source, ko, entry_id)
        entries.append(
            {
                "id": entry_id,
                "source_jp_utf16le_sha256": text_hash(source),
                "ko": ko,
                "ko_utf16le_sha256": text_hash(ko),
                "format_signature_sha256": canonical_hash(message_invariants(source)),
                "translation_origin": origin,
            }
        )
    return entries


def validate_entries(table: MessageTable, entries: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    required = {"id", "source_jp_utf16le_sha256", "ko", "ko_utf16le_sha256", "format_signature_sha256", "translation_origin"}
    if len(entries) != len(BUNDLE_IDS):
        raise MsgdataP1Error("overlay entry count differs from P1 bundle")
    normalized: list[dict[str, Any]] = []
    reuse_count = 0
    direct_count = 0
    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping) or set(entry) != required:
            raise MsgdataP1Error(f"overlay entry {index} has an unexpected schema")
        entry_id = entry["id"]
        if isinstance(entry_id, bool) or not isinstance(entry_id, int) or entry_id != BUNDLE_IDS[index]:
            raise MsgdataP1Error(f"overlay coordinate differs at index {index}")
        source_hash = entry["source_jp_utf16le_sha256"]
        ko_hash = entry["ko_utf16le_sha256"]
        format_hash = entry["format_signature_sha256"]
        ko = entry["ko"]
        origin = entry["translation_origin"]
        if not all(isinstance(value, str) and HEX64_RE.fullmatch(value) for value in (source_hash, ko_hash, format_hash)):
            raise MsgdataP1Error(f"overlay hash field is invalid at id {entry_id}")
        source = table.texts[entry_id]
        if text_hash(source) != source_hash:
            raise MsgdataP1Error(f"JP source hash mismatch at id {entry_id}")
        if text_hash(ko) != ko_hash or canonical_hash(message_invariants(source)) != format_hash:
            raise MsgdataP1Error(f"overlay Korean or format signature differs at id {entry_id}")
        validate_replacement(source, ko, entry_id)
        expected_origin = "exact_source_hash_catalog_reuse" if entry_id in EXPECTED_REUSE_IDS else "project_direct_translation"
        if origin != expected_origin:
            raise MsgdataP1Error(f"translation origin differs at id {entry_id}")
        if origin == "exact_source_hash_catalog_reuse":
            reuse_count += 1
        else:
            direct_count += 1
        normalized.append(dict(entry))
    if reuse_count != len(EXPECTED_REUSE_IDS) or direct_count != len(DIRECT_TRANSLATIONS):
        raise MsgdataP1Error("translation origin counts differ")
    return normalized


def make_overlay(entries: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    origins = Counter(entry["translation_origin"] for entry in entries)
    return {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": "msgdata_ko_pk_jp_p1_residual_175.v1",
        "resource": RESOURCE,
        "base_language": "JP",
        "distribution_policy": {"contains_commercial_source_text": False, "contains_complete_game_resource": False, "sc_container_used": False},
        "active_v6_baseline": dict(STOCK),
        "audit_bundle": {"bundle_id": "p1-MSG_PK_JP_msgdata-01", "coordinate_sha256": BUNDLE_COORDINATE_SHA256},
        "exact_reuse_catalog": {"relative_path": REUSE_CATALOG_RELATIVE, "sha256": REUSE_CATALOG_SHA256, "entry_count": len(EXPECTED_REUSE_IDS)},
        "entry_count": len(entries),
        "translation_origin_counts": dict(sorted(origins.items())),
        "entries": list(entries),
    }


def validate_public_overlay(value: Mapping[str, Any], table: MessageTable) -> list[dict[str, Any]]:
    required = {
        "schema", "overlay_id", "resource", "base_language", "distribution_policy", "active_v6_baseline", "audit_bundle",
        "exact_reuse_catalog", "entry_count", "translation_origin_counts", "entries",
    }
    if set(value) != required or value["schema"] != OVERLAY_SCHEMA or value["resource"] != RESOURCE:
        raise MsgdataP1Error("public overlay header differs")
    if value["overlay_id"] != "msgdata_ko_pk_jp_p1_residual_175.v1" or value["base_language"] != "JP":
        raise MsgdataP1Error("public overlay JP route differs")
    if value["distribution_policy"] != {"contains_commercial_source_text": False, "contains_complete_game_resource": False, "sc_container_used": False}:
        raise MsgdataP1Error("public overlay distribution policy differs")
    if value["active_v6_baseline"] != STOCK or value["audit_bundle"] != {"bundle_id": "p1-MSG_PK_JP_msgdata-01", "coordinate_sha256": BUNDLE_COORDINATE_SHA256}:
        raise MsgdataP1Error("public overlay baseline or audit bundle differs")
    if value["exact_reuse_catalog"] != {"relative_path": REUSE_CATALOG_RELATIVE, "sha256": REUSE_CATALOG_SHA256, "entry_count": len(EXPECTED_REUSE_IDS)}:
        raise MsgdataP1Error("public overlay reuse provenance differs")
    entries_value = value["entries"]
    if not isinstance(entries_value, list) or value["entry_count"] != len(entries_value):
        raise MsgdataP1Error("public overlay entry count differs")
    entries = validate_entries(table, entries_value)
    if value["translation_origin_counts"] != dict(sorted(Counter(entry["translation_origin"] for entry in entries).items())):
        raise MsgdataP1Error("public overlay origin counts differ")
    return entries


def candidate_from_entries(packed: bytes, raw: bytes, table: MessageTable, entries: Sequence[Mapping[str, Any]]) -> tuple[bytes, bytes, list[int], int]:
    normalized = validate_entries(table, entries)
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
        raise MsgdataP1Error("raw candidate is not deterministic")
    candidate_a = recompress_wrapper(rebuilt_raw_a, packed)
    candidate_b = recompress_wrapper(rebuilt_raw_b, packed)
    if candidate_a != candidate_b:
        raise MsgdataP1Error("packed candidate is not deterministic")
    _header, checked_raw = decompress_wrapper(candidate_a)
    checked_table = parse_message_table(checked_raw)
    if checked_raw != rebuilt_raw_a or checked_table.texts != tuple(target_texts):
        raise MsgdataP1Error("candidate parse/decompression roundtrip differs")
    if (
        checked_table.string_count != table.string_count
        or checked_table.block_offset != table.block_offset
        or checked_table.table_offset != table.table_offset
        or checked_table.table_size != table.table_size
        or checked_table.string_start != table.string_start
        or rebuild_message_table(checked_table, checked_table.texts) != checked_raw
    ):
        raise MsgdataP1Error("candidate string table structure differs")
    selected = {entry["id"]: entry["ko"] for entry in normalized}
    for entry_id, source in enumerate(table.texts):
        expected = selected.get(entry_id, source)
        if checked_table.texts[entry_id] != expected:
            raise MsgdataP1Error(f"candidate text differs at id {entry_id}")
        if entry_id not in selected and source.encode("utf-16le") + b"\0\0" != checked_table.texts[entry_id].encode("utf-16le") + b"\0\0":
            raise MsgdataP1Error(f"nonselected UTF-16LE payload differs at id {entry_id}")
    if any(is_high_confidence_japanese(checked_table.texts[entry_id]) for entry_id in BUNDLE_IDS):
        raise MsgdataP1Error("candidate retains a high-confidence Japanese string in the selected P1 bundle")
    before_total = sum(is_high_confidence_japanese(text) for text in table.texts)
    after_total = sum(is_high_confidence_japanese(text) for text in checked_table.texts)
    if after_total != before_total - len(BUNDLE_IDS):
        raise MsgdataP1Error("candidate high-confidence residual count differs outside selected bundle")
    stock_prefix = bytearray(raw[: table.table_offset])
    candidate_prefix = bytearray(checked_raw[: checked_table.table_offset])
    struct.pack_into("<I", stock_prefix, 8, 0)
    struct.pack_into("<I", candidate_prefix, 8, 0)
    if stock_prefix != candidate_prefix:
        raise MsgdataP1Error("opaque prefix differs outside logical-size field")
    return candidate_a, rebuilt_raw_a, changed_ids, after_total


def make_validation(entries: Sequence[Mapping[str, Any]], candidate: bytes, candidate_raw: bytes, changed_ids: Sequence[int], residual_after: int) -> dict[str, Any]:
    return {
        "schema": VALIDATION_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "resource": RESOURCE,
        "active_v6_baseline": dict(STOCK),
        "audit_bundle": {"bundle_id": "p1-MSG_PK_JP_msgdata-01", "coordinate_sha256": BUNDLE_COORDINATE_SHA256},
        "entry_count": len(entries),
        "translation_origin_counts": dict(sorted(Counter(entry["translation_origin"] for entry in entries).items())),
        "expected_candidate": {"packed_size": len(candidate), "packed_sha256": sha256_bytes(candidate), "raw_size": len(candidate_raw), "raw_sha256": sha256_bytes(candidate_raw)},
        "effective_change_count": len(changed_ids),
        "effective_change_coordinate_sha256": canonical_hash(list(changed_ids)),
        "high_confidence_kana_residual_count_after_candidate": residual_after,
        "checks": {
            "active_v6_baseline": "OK", "p1_coordinate_contract": "OK", "exact_source_hash_catalog_reuse": "OK",
            "per_entry_jp_source_hashes": "OK", "token_and_format_profiles": "OK", "raw_deterministic_rebuild": "OK",
            "packed_deterministic_rebuild": "OK", "candidate_parser_roundtrip": "OK", "nonselected_utf16le_payloads": "OK",
            "selected_high_confidence_kana_residuals": "0", "steam_installation_written": False, "sc_container_used": False,
            "release_asset_written": False, "github_written": False,
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
        "audit_bundle": {"bundle_id": "p1-MSG_PK_JP_msgdata-01", "coordinate_sha256": BUNDLE_COORDINATE_SHA256},
        "overlay": {"relative_path": "workstreams/steam_jp_msgdata_p1_residual_175_v1/public/msgdata_ko_pk_jp_p1_residual_175.v1.json", "sha256": sha256_bytes(overlay_blob), "entry_count": len(entries)},
        "validation": {"relative_path": "workstreams/steam_jp_msgdata_p1_residual_175_v1/validation.v1.json", "sha256": sha256_bytes(validation_blob)},
        "expected_candidate": {"packed_size": len(candidate), "packed_sha256": sha256_bytes(candidate), "raw_size": len(candidate_raw), "raw_sha256": sha256_bytes(candidate_raw), "string_count": STOCK["string_count"]},
        "output_policy": {"complete_candidate_private_only": True, "allowed_root": "tmp", "relative_path": RESOURCE},
        "proofs": {"active_v6_baseline_pinned": True, "catalog_reuse_exact_source_hash_only": True, "per_entry_jp_source_hash_gated": True, "format_and_token_profile_preserved": True, "nonselected_utf16le_payloads_preserved": True, "parser_roundtrip_valid": True, "deterministic_raw_and_packed_rebuild": True, "steam_installation_read_only": True},
    }


def assert_source_free(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if CJK_OR_KANA_RE.search(text) or "MSG_PK/SC" in text or "RES_SC" in text or "source_sc" in text.casefold():
        raise MsgdataP1Error(f"public artifact is not JP-route source-free: {path}")


def path_from_repo(relative: str) -> Path:
    path = Path(relative)
    if not relative or path.is_absolute() or ".." in path.parts or "\\" in relative:
        raise MsgdataP1Error("contract path escapes repository")
    resolved = (REPO_ROOT / path).resolve()
    if not resolved.is_relative_to(REPO_ROOT.resolve()):
        raise MsgdataP1Error("contract path escapes repository")
    return resolved


def require_private_output_root(output_root: Path) -> Path:
    resolved = output_root.resolve()
    private_root = (REPO_ROOT / "tmp").resolve()
    if not resolved.is_relative_to(private_root) or resolved == private_root:
        raise MsgdataP1Error("complete candidate output must be a child directory below KR_PATCH_WORK/tmp")
    return resolved


def freeze(steam_root: Path) -> dict[str, Any]:
    _source_path, packed, raw, table = load_stock(steam_root)
    entries = build_entries(table)
    candidate, candidate_raw, changed_ids, residual_after = candidate_from_entries(packed, raw, table, entries)
    overlay_blob = pretty_bytes(make_overlay(entries))
    validation_blob = pretty_bytes(make_validation(entries, candidate, candidate_raw, changed_ids, residual_after))
    contract_blob = pretty_bytes(make_contract(overlay_blob, validation_blob, candidate, candidate_raw, entries))
    atomic_write(PUBLIC_OVERLAY, overlay_blob)
    atomic_write(VALIDATION, validation_blob)
    atomic_write(CONTRACT, contract_blob)
    for path in (PUBLIC_OVERLAY, VALIDATION, CONTRACT):
        assert_source_free(path)
    return {"entry_count": len(entries), "catalog_reuse_count": len(EXPECTED_REUSE_IDS), "direct_translation_count": len(DIRECT_TRANSLATIONS), "candidate_sha256": sha256_bytes(candidate), "candidate_raw_sha256": sha256_bytes(candidate_raw), "high_confidence_kana_residual_count_after_candidate": residual_after, "installed_game_file_modified": False}


def load_frozen_inputs(steam_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], bytes, bytes, MessageTable]:
    _source_path, packed, raw, table = load_stock(steam_root)
    contract, _contract_blob = read_json(CONTRACT)
    required = {"schema", "source_free", "contains_commercial_source_text", "contains_complete_game_resource", "resource", "runtime_route", "active_v6_baseline", "audit_bundle", "overlay", "validation", "expected_candidate", "output_policy", "proofs"}
    if set(contract) != required or contract["schema"] != CONTRACT_SCHEMA or contract["resource"] != RESOURCE:
        raise MsgdataP1Error("frozen contract header differs")
    if contract["active_v6_baseline"] != STOCK or contract["runtime_route"] != {"language": "JP", "sc_container_used": False, "installed_game_file_written": False}:
        raise MsgdataP1Error("frozen contract baseline or route differs")
    if contract["audit_bundle"] != {"bundle_id": "p1-MSG_PK_JP_msgdata-01", "coordinate_sha256": BUNDLE_COORDINATE_SHA256} or contract["output_policy"] != {"complete_candidate_private_only": True, "allowed_root": "tmp", "relative_path": RESOURCE}:
        raise MsgdataP1Error("frozen contract bundle or output policy differs")
    if not isinstance(contract["proofs"], dict) or any(value is not True for value in contract["proofs"].values()):
        raise MsgdataP1Error("frozen contract proofs are incomplete")
    overlay_path = path_from_repo(contract["overlay"]["relative_path"])
    overlay, overlay_blob = read_json(overlay_path)
    if sha256_bytes(overlay_blob) != contract["overlay"]["sha256"]:
        raise MsgdataP1Error("frozen overlay hash differs")
    entries = validate_public_overlay(overlay, table)
    validation_path = path_from_repo(contract["validation"]["relative_path"])
    validation_blob = validation_path.read_bytes()
    if sha256_bytes(validation_blob) != contract["validation"]["sha256"]:
        raise MsgdataP1Error("frozen validation hash differs")
    for path in (overlay_path, validation_path, CONTRACT):
        assert_source_free(path)
    return contract, entries, packed, raw, table


def build_staging_candidate(steam_root: Path, output_root: Path) -> dict[str, Any]:
    output_root = require_private_output_root(output_root)
    source_path, stock_before, _raw_before, _table_before = load_stock(steam_root)
    contract, entries, packed, raw, table = load_frozen_inputs(steam_root)
    if packed != stock_before:
        raise MsgdataP1Error("active Steam JP source changed while loading frozen inputs")
    candidate, candidate_raw, changed_ids, residual_after = candidate_from_entries(packed, raw, table, entries)
    observed = {"packed_size": len(candidate), "packed_sha256": sha256_bytes(candidate), "raw_size": len(candidate_raw), "raw_sha256": sha256_bytes(candidate_raw), "string_count": table.string_count}
    if observed != contract["expected_candidate"]:
        raise MsgdataP1Error("candidate differs from frozen deterministic contract")
    target_path = (output_root / Path(RESOURCE)).resolve()
    if target_path == source_path or not target_path.is_relative_to(output_root):
        raise MsgdataP1Error("refusing to target Steam installation or escape private output")
    atomic_write(target_path, candidate)
    if target_path.read_bytes() != candidate or source_path.read_bytes() != stock_before:
        raise MsgdataP1Error("staging candidate write changed unexpected bytes")
    manifest = {
        "schema": MANIFEST_SCHEMA, "source_free": True, "contains_commercial_source_text": False, "contains_complete_game_resource": False,
        "resource": RESOURCE, "active_v6_baseline": dict(STOCK), "target": observed, "entry_count": len(entries),
        "effective_change_count": len(changed_ids), "coordinate_sha256": BUNDLE_COORDINATE_SHA256,
        "effective_change_coordinate_sha256": canonical_hash(changed_ids), "high_confidence_kana_residual_count_after_candidate": residual_after,
        "output": {"relative_path": RESOURCE, "complete_candidate_private_only": True, "installed_game_file_modified": False},
        "checks": {"contract_hash": "OK", "exact_catalog_reuse": "OK", "source_hash_gates": "OK", "token_profiles": "OK", "steam_source_unchanged": "OK"},
    }
    atomic_write(output_root / "build_manifest.v1.json", pretty_bytes(manifest))
    return {"candidate_path": str(target_path), "manifest_path": str(output_root / "build_manifest.v1.json"), **observed, "high_confidence_kana_residual_count_after_candidate": residual_after, "installed_game_file_modified": False}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    freeze_parser = commands.add_parser("freeze", help="freeze P1 overlay, validation, and deterministic contract")
    freeze_parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    build_parser = commands.add_parser("build", help="build a private staging candidate from frozen inputs")
    build_parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    build_parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = freeze(args.steam_root) if args.command == "freeze" else build_staging_candidate(args.steam_root, args.output_root)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
