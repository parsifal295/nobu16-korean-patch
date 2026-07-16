#!/usr/bin/env python3
"""Build a private, JP-native staging candidate for the 125 P0 msgui residuals.

The Steam installation is read-only input.  The only complete game resource
this program can write is a candidate below ``KR_PATCH_WORK/tmp``.  Public
artifacts contain coordinates, hashes, and project-authored Korean text only;
they never contain the official Japanese source text or an SC route.
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
TRANSLATIONS = runpy.run_path(str(WORKSTREAM_ROOT / "translations.py"))["TRANSLATIONS"]


RESOURCE = "MSG_PK/JP/msgui.bin"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "tmp" / "steam_jp_msgui_p0_residual_125_v1" / "candidate"
PUBLIC_OVERLAY = WORKSTREAM_ROOT / "public" / "msgui_ko_pk_jp_p0_residual_125.v1.json"
CONTRACT = WORKSTREAM_ROOT / "source_free_contract.v1.json"
VALIDATION = WORKSTREAM_ROOT / "validation.v1.json"

STOCK = {
    "packed_size": 121608,
    "packed_sha256": "29D0C6CCC262E7AB757AA5D0819224370DEDEF4CF250E89FC88B24E600EF2169",
    "raw_size": 121108,
    "raw_sha256": "FFCCBDB6EE4C80E143B8F6F8B0DAB31DD2F01B1ED2E608A98DEA13F45B939502",
    "string_count": 5100,
}

OVERLAY_SCHEMA = "nobu16.kr.steam-jp-msgui-p0-residual-overlay.v1"
CONTRACT_SCHEMA = "nobu16.kr.steam-jp-msgui-p0-residual-contract.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-msgui-p0-residual-validation.v1"
MANIFEST_SCHEMA = "nobu16.kr.steam-jp-msgui-p0-residual-build-manifest.v1"

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
    "printf",
    "unknown_percent_count",
    "leading_whitespace",
    "trailing_whitespace",
    "esc",
    "controls",
    "line_breaks",
    "pua",
    "greek_symbols",
    "box_drawing_symbols",
    "ideographic_space_count",
)


class MsguiP0Error(ValueError):
    """Raised when a baseline, translation, or output safety proof fails."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def canonical_hash(value: object) -> str:
    return sha256_bytes(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


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
        previous = folded.get(key.casefold())
        if previous is not None:
            raise MsguiP0Error(f"duplicate or case-colliding JSON key: {previous!r}/{key!r}")
        folded[key.casefold()] = key
        result[key] = value
    return result


def read_json(path: Path) -> tuple[dict[str, Any], bytes]:
    blob = path.read_bytes()
    try:
        value = json.loads(blob.decode("utf-8-sig"), object_pairs_hook=strict_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MsguiP0Error(f"invalid JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise MsguiP0Error(f"JSON root must be an object: {path}")
    return value, blob


def message_invariants(text: str) -> dict[str, Any]:
    printf_matches = list(PRINTF_RE.finditer(text))
    printf_percent_offsets = {
        index
        for match in printf_matches
        for index in range(match.start(), match.end())
        if text[index] == "%"
    }
    esc_matches = list(ESC_RE.finditer(text))
    esc_offsets = {index for match in esc_matches for index in range(match.start(), match.end())}
    return {
        "printf": [match.group(0) for match in printf_matches],
        "unknown_percent_count": sum(
            1 for index, char in enumerate(text) if char == "%" and index not in printf_percent_offsets
        ),
        "leading_whitespace": text[: len(text) - len(text.lstrip())],
        "trailing_whitespace": text[len(text.rstrip()) :],
        "esc": [match.group(0) for match in esc_matches],
        "controls": [
            f"U+{ord(char):04X}"
            for index, char in enumerate(text)
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


def residual_ids(table: MessageTable) -> list[int]:
    return [
        entry_id
        for entry_id, text in enumerate(table.texts)
        if KANA_RE.search(text) and not HANGUL_RE.search(text)
    ]


def load_stock(steam_root: Path) -> tuple[Path, bytes, bytes, MessageTable]:
    source_path = (steam_root.resolve() / Path(RESOURCE)).resolve()
    if not source_path.is_file():
        raise MsguiP0Error(f"active JP resource does not exist: {source_path}")
    packed = source_path.read_bytes()
    if len(packed) != STOCK["packed_size"] or sha256_bytes(packed) != STOCK["packed_sha256"]:
        raise MsguiP0Error("active Steam JP msgui packed baseline does not match v6 pin")
    _header, raw = decompress_wrapper(packed)
    if len(raw) != STOCK["raw_size"] or sha256_bytes(raw) != STOCK["raw_sha256"]:
        raise MsguiP0Error("active Steam JP msgui raw baseline does not match v6 pin")
    table = parse_message_table(raw)
    if table.string_count != STOCK["string_count"]:
        raise MsguiP0Error("active Steam JP msgui string count differs from v6 pin")
    if rebuild_message_table(table, table.texts) != raw:
        raise MsguiP0Error("unchanged active JP msgui parse/rebuild is not byte-identical")
    return source_path, packed, raw, table


def require_translation_table(table: MessageTable) -> None:
    if not TRANSLATIONS or any(isinstance(entry_id, bool) or not isinstance(entry_id, int) for entry_id in TRANSLATIONS):
        raise MsguiP0Error("translation IDs must be nonempty integer keys")
    if sorted(TRANSLATIONS) != residual_ids(table):
        missing = sorted(set(residual_ids(table)) - set(TRANSLATIONS))
        extra = sorted(set(TRANSLATIONS) - set(residual_ids(table)))
        raise MsguiP0Error(f"translation table must exactly cover P0 residual IDs; missing={missing!r}, extra={extra!r}")
    for entry_id, ko in TRANSLATIONS.items():
        if not isinstance(ko, str) or not ko or "\0" in ko or "\ufffd" in ko:
            raise MsguiP0Error(f"unsafe Korean replacement at id {entry_id}")
        if CJK_OR_KANA_RE.search(ko):
            raise MsguiP0Error(f"Korean replacement retains CJK/kana at id {entry_id}")
        mismatches = mismatch_keys(table.texts[entry_id], ko)
        if mismatches:
            raise MsguiP0Error(f"format/token mismatch at id {entry_id}: {mismatches!r}")


def build_entries(table: MessageTable) -> list[dict[str, Any]]:
    require_translation_table(table)
    entries = []
    for entry_id in sorted(TRANSLATIONS):
        source = table.texts[entry_id]
        ko = TRANSLATIONS[entry_id]
        entries.append(
            {
                "id": entry_id,
                "source_jp_utf16le_sha256": text_hash(source),
                "ko": ko,
                "ko_utf16le_sha256": text_hash(ko),
                "format_signature_sha256": canonical_hash(message_invariants(source)),
            }
        )
    return entries


def validate_entries(table: MessageTable, entries: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if len(entries) != len(TRANSLATIONS):
        raise MsguiP0Error("overlay entry count differs from translation table")
    normalized: list[dict[str, Any]] = []
    ids: list[int] = []
    required = {"id", "source_jp_utf16le_sha256", "ko", "ko_utf16le_sha256", "format_signature_sha256"}
    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping) or set(entry) != required:
            raise MsguiP0Error(f"overlay entry {index} has an unexpected schema")
        entry_id = entry["id"]
        if isinstance(entry_id, bool) or not isinstance(entry_id, int) or not 0 <= entry_id < table.string_count:
            raise MsguiP0Error(f"overlay entry {index} ID is invalid")
        source_hash = entry["source_jp_utf16le_sha256"]
        ko_hash = entry["ko_utf16le_sha256"]
        signature = entry["format_signature_sha256"]
        ko = entry["ko"]
        if not all(isinstance(value, str) and HEX64_RE.fullmatch(value) for value in (source_hash, ko_hash, signature)):
            raise MsguiP0Error(f"overlay entry {entry_id} hash field is invalid")
        if not isinstance(ko, str) or not ko or "\0" in ko or "\ufffd" in ko or CJK_OR_KANA_RE.search(ko):
            raise MsguiP0Error(f"overlay entry {entry_id} Korean text is unsafe")
        source = table.texts[entry_id]
        if text_hash(source) != source_hash:
            raise MsguiP0Error(f"JP source hash mismatch at id {entry_id}")
        if text_hash(ko) != ko_hash:
            raise MsguiP0Error(f"Korean hash mismatch at id {entry_id}")
        if canonical_hash(message_invariants(source)) != signature:
            raise MsguiP0Error(f"source format signature mismatch at id {entry_id}")
        mismatches = mismatch_keys(source, ko)
        if mismatches:
            raise MsguiP0Error(f"format/token mismatch at id {entry_id}: {mismatches!r}")
        ids.append(entry_id)
        normalized.append(dict(entry))
    if ids != sorted(set(ids)) or ids != residual_ids(table):
        raise MsguiP0Error("overlay IDs are not the exact active P0 residual set")
    return normalized


def make_overlay(entries: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": "msgui_ko_pk_jp_p0_residual_125.v1",
        "resource": RESOURCE,
        "base_language": "JP",
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
            "sc_container_used": False,
        },
        "active_v6_baseline": dict(STOCK),
        "entry_count": len(entries),
        "coordinate_sha256": canonical_hash([entry["id"] for entry in entries]),
        "entries": list(entries),
    }


def validate_public_overlay(value: Mapping[str, Any], table: MessageTable) -> list[dict[str, Any]]:
    required = {
        "schema", "overlay_id", "resource", "base_language", "distribution_policy", "active_v6_baseline",
        "entry_count", "coordinate_sha256", "entries",
    }
    if set(value) != required or value["schema"] != OVERLAY_SCHEMA or value["resource"] != RESOURCE:
        raise MsguiP0Error("public overlay header differs")
    if value["overlay_id"] != "msgui_ko_pk_jp_p0_residual_125.v1" or value["base_language"] != "JP":
        raise MsguiP0Error("public overlay JP route differs")
    if value["distribution_policy"] != {
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "sc_container_used": False,
    } or value["active_v6_baseline"] != STOCK:
        raise MsguiP0Error("public overlay policy or v6 baseline differs")
    entries_value = value["entries"]
    if not isinstance(entries_value, list) or value["entry_count"] != len(entries_value):
        raise MsguiP0Error("public overlay entry count differs")
    entries = validate_entries(table, entries_value)
    if value["coordinate_sha256"] != canonical_hash([entry["id"] for entry in entries]):
        raise MsguiP0Error("public overlay coordinate digest differs")
    return entries


def candidate_from_entries(packed: bytes, raw: bytes, table: MessageTable, entries: Sequence[Mapping[str, Any]]) -> tuple[bytes, bytes, list[int]]:
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
        raise MsguiP0Error("raw candidate is not deterministic")
    candidate_a = recompress_wrapper(rebuilt_raw_a, packed)
    candidate_b = recompress_wrapper(rebuilt_raw_b, packed)
    if candidate_a != candidate_b:
        raise MsguiP0Error("packed candidate is not deterministic")
    _header, checked_raw = decompress_wrapper(candidate_a)
    checked_table = parse_message_table(checked_raw)
    if checked_raw != rebuilt_raw_a or checked_table.texts != tuple(target_texts):
        raise MsguiP0Error("candidate parse/decompression roundtrip differs")
    if residual_ids(checked_table):
        raise MsguiP0Error("candidate still contains high-confidence kana residuals")
    if rebuild_message_table(checked_table, checked_table.texts) != checked_raw:
        raise MsguiP0Error("candidate unchanged parse/rebuild differs")
    if (
        checked_table.string_count != table.string_count
        or checked_table.block_offset != table.block_offset
        or checked_table.table_offset != table.table_offset
        or checked_table.table_size != table.table_size
        or checked_table.string_start != table.string_start
    ):
        raise MsguiP0Error("candidate string table structure differs")
    selected = {entry["id"]: entry["ko"] for entry in normalized}
    for entry_id, source in enumerate(table.texts):
        expected = selected.get(entry_id, source)
        if checked_table.texts[entry_id] != expected:
            raise MsguiP0Error(f"candidate text differs at id {entry_id}")
        if entry_id not in selected:
            if source.encode("utf-16le") + b"\0\0" != checked_table.texts[entry_id].encode("utf-16le") + b"\0\0":
                raise MsguiP0Error(f"nonselected UTF-16LE payload differs at id {entry_id}")
    stock_prefix = bytearray(raw[: table.table_offset])
    candidate_prefix = bytearray(checked_raw[: checked_table.table_offset])
    struct.pack_into("<I", stock_prefix, 8, 0)
    struct.pack_into("<I", candidate_prefix, 8, 0)
    if stock_prefix != candidate_prefix:
        raise MsguiP0Error("opaque prefix differs outside logical-size field")
    return candidate_a, rebuilt_raw_a, changed_ids


def make_contract(overlay_blob: bytes, validation_blob: bytes, candidate: bytes, candidate_raw: bytes, entries: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "schema": CONTRACT_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "resource": RESOURCE,
        "runtime_route": {"language": "JP", "sc_container_used": False, "installed_game_file_written": False},
        "active_v6_baseline": dict(STOCK),
        "overlay": {
            "relative_path": "workstreams/steam_jp_msgui_p0_residual_125_v1/public/msgui_ko_pk_jp_p0_residual_125.v1.json",
            "sha256": sha256_bytes(overlay_blob),
            "entry_count": len(entries),
            "coordinate_sha256": canonical_hash([entry["id"] for entry in entries]),
        },
        "validation": {
            "relative_path": "workstreams/steam_jp_msgui_p0_residual_125_v1/validation.v1.json",
            "sha256": sha256_bytes(validation_blob),
        },
        "expected_candidate": {
            "packed_size": len(candidate),
            "packed_sha256": sha256_bytes(candidate),
            "raw_size": len(candidate_raw),
            "raw_sha256": sha256_bytes(candidate_raw),
            "string_count": STOCK["string_count"],
        },
        "output_policy": {"complete_candidate_private_only": True, "allowed_root": "tmp", "relative_path": RESOURCE},
        "proofs": {
            "active_v6_baseline_pinned": True,
            "per_entry_jp_source_hash_gated": True,
            "format_and_token_profile_preserved": True,
            "nonselected_utf16le_payloads_preserved": True,
            "parser_roundtrip_valid": True,
            "deterministic_raw_and_packed_rebuild": True,
            "steam_installation_read_only": True,
        },
    }


def make_validation(entries: Sequence[Mapping[str, Any]], candidate: bytes, candidate_raw: bytes, changed_ids: Sequence[int]) -> dict[str, Any]:
    return {
        "schema": VALIDATION_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "resource": RESOURCE,
        "active_v6_baseline": dict(STOCK),
        "entry_count": len(entries),
        "coordinate_sha256": canonical_hash([entry["id"] for entry in entries]),
        "expected_candidate": {
            "packed_size": len(candidate),
            "packed_sha256": sha256_bytes(candidate),
            "raw_size": len(candidate_raw),
            "raw_sha256": sha256_bytes(candidate_raw),
        },
        "effective_change_count": len(changed_ids),
        "effective_change_coordinate_sha256": canonical_hash(list(changed_ids)),
        "high_confidence_kana_residual_count_after_candidate": 0,
        "checks": {
            "active_v6_baseline": "OK",
            "p0_residual_set_exactly_covered": "OK",
            "per_entry_jp_source_hashes": "OK",
            "token_and_format_profiles": "OK",
            "raw_deterministic_rebuild": "OK",
            "packed_deterministic_rebuild": "OK",
            "candidate_parser_roundtrip": "OK",
            "candidate_high_confidence_kana_residuals": "0",
            "nonselected_utf16le_payloads": "OK",
            "opaque_prefix_except_logical_size": "OK",
            "steam_installation_written": False,
            "sc_container_used": False,
            "release_asset_written": False,
            "github_written": False,
        },
    }


def assert_source_free(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if CJK_OR_KANA_RE.search(text) or "MSG_PK/SC" in text or "RES_SC" in text or "source_sc" in text.casefold():
        raise MsguiP0Error(f"public artifact is not JP-route source-free: {path}")


def require_private_output_root(output_root: Path) -> Path:
    resolved = output_root.resolve()
    private_root = (REPO_ROOT / "tmp").resolve()
    if not resolved.is_relative_to(private_root) or resolved == private_root:
        raise MsguiP0Error("complete candidate output must be a child directory below KR_PATCH_WORK/tmp")
    return resolved


def path_from_repo(relative: str) -> Path:
    path = Path(relative)
    if not relative or path.is_absolute() or ".." in path.parts or "\\" in relative:
        raise MsguiP0Error("contract path escapes repository")
    resolved = (REPO_ROOT / path).resolve()
    if not resolved.is_relative_to(REPO_ROOT.resolve()):
        raise MsguiP0Error("contract path escapes repository")
    return resolved


def freeze(steam_root: Path) -> dict[str, Any]:
    _source_path, packed, raw, table = load_stock(steam_root)
    entries = build_entries(table)
    candidate, candidate_raw, changed_ids = candidate_from_entries(packed, raw, table, entries)
    overlay = make_overlay(entries)
    overlay_blob = pretty_bytes(overlay)
    validation = make_validation(entries, candidate, candidate_raw, changed_ids)
    validation_blob = pretty_bytes(validation)
    contract = make_contract(overlay_blob, validation_blob, candidate, candidate_raw, entries)
    atomic_write(PUBLIC_OVERLAY, overlay_blob)
    atomic_write(VALIDATION, validation_blob)
    atomic_write(CONTRACT, pretty_bytes(contract))
    for path in (PUBLIC_OVERLAY, VALIDATION, CONTRACT):
        assert_source_free(path)
    return {
        "entry_count": len(entries),
        "candidate_sha256": sha256_bytes(candidate),
        "candidate_raw_sha256": sha256_bytes(candidate_raw),
        "installed_game_file_modified": False,
    }


def load_frozen_inputs(steam_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], bytes, bytes, MessageTable]:
    source_path, packed, raw, table = load_stock(steam_root)
    contract, _contract_blob = read_json(CONTRACT)
    required = {
        "schema", "source_free", "contains_commercial_source_text", "contains_complete_game_resource", "resource",
        "runtime_route", "active_v6_baseline", "overlay", "validation", "expected_candidate", "output_policy", "proofs",
    }
    if set(contract) != required or contract["schema"] != CONTRACT_SCHEMA or contract["resource"] != RESOURCE:
        raise MsguiP0Error("frozen contract header differs")
    if contract["active_v6_baseline"] != STOCK or contract["runtime_route"] != {
        "language": "JP", "sc_container_used": False, "installed_game_file_written": False,
    }:
        raise MsguiP0Error("frozen contract baseline or route differs")
    if contract["output_policy"] != {"complete_candidate_private_only": True, "allowed_root": "tmp", "relative_path": RESOURCE}:
        raise MsguiP0Error("frozen contract output policy differs")
    if not isinstance(contract["proofs"], dict) or any(value is not True for value in contract["proofs"].values()):
        raise MsguiP0Error("frozen contract proofs are incomplete")
    overlay_path = path_from_repo(contract["overlay"]["relative_path"])
    overlay, overlay_blob = read_json(overlay_path)
    if sha256_bytes(overlay_blob) != contract["overlay"]["sha256"]:
        raise MsguiP0Error("frozen overlay hash differs")
    entries = validate_public_overlay(overlay, table)
    validation_path = path_from_repo(contract["validation"]["relative_path"])
    validation_blob = validation_path.read_bytes()
    if sha256_bytes(validation_blob) != contract["validation"]["sha256"]:
        raise MsguiP0Error("frozen validation hash differs")
    for path in (overlay_path, validation_path, CONTRACT):
        assert_source_free(path)
    if source_path != (steam_root.resolve() / Path(RESOURCE)).resolve():
        raise MsguiP0Error("unexpected active JP source path")
    return contract, entries, packed, raw, table


def build_staging_candidate(steam_root: Path, output_root: Path) -> dict[str, Any]:
    output_root = require_private_output_root(output_root)
    source_path, stock_before, _raw_before, _table_before = load_stock(steam_root)
    contract, entries, packed, raw, table = load_frozen_inputs(steam_root)
    if packed != stock_before:
        raise MsguiP0Error("active Steam JP source changed while loading frozen inputs")
    candidate, candidate_raw, changed_ids = candidate_from_entries(packed, raw, table, entries)
    observed = {
        "packed_size": len(candidate),
        "packed_sha256": sha256_bytes(candidate),
        "raw_size": len(candidate_raw),
        "raw_sha256": sha256_bytes(candidate_raw),
        "string_count": table.string_count,
    }
    if observed != contract["expected_candidate"]:
        raise MsguiP0Error("candidate differs from frozen deterministic contract")
    target_path = (output_root / Path(RESOURCE)).resolve()
    if target_path == source_path or not target_path.is_relative_to(output_root):
        raise MsguiP0Error("refusing to target Steam installation or escape private output")
    atomic_write(target_path, candidate)
    if target_path.read_bytes() != candidate:
        raise MsguiP0Error("written staging candidate differs")
    if source_path.read_bytes() != stock_before:
        raise MsguiP0Error("Steam JP source changed during staging build")
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "resource": RESOURCE,
        "active_v6_baseline": dict(STOCK),
        "target": observed,
        "entry_count": len(entries),
        "effective_change_count": len(changed_ids),
        "coordinate_sha256": canonical_hash([entry["id"] for entry in entries]),
        "effective_change_coordinate_sha256": canonical_hash(changed_ids),
        "output": {"relative_path": RESOURCE, "complete_candidate_private_only": True, "installed_game_file_modified": False},
        "checks": {"contract_hash": "OK", "source_hash_gates": "OK", "token_profiles": "OK", "steam_source_unchanged": "OK"},
    }
    atomic_write(output_root / "build_manifest.v1.json", pretty_bytes(manifest))
    return {"candidate_path": str(target_path), "manifest_path": str(output_root / "build_manifest.v1.json"), **observed, "installed_game_file_modified": False}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    freeze_parser = commands.add_parser("freeze", help="freeze source-free overlay, validation, and deterministic contract")
    freeze_parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    build_parser = commands.add_parser("build", help="build only a private staging candidate from frozen inputs")
    build_parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    build_parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "freeze":
        result = freeze(args.steam_root)
    else:
        result = build_staging_candidate(args.steam_root, args.output_root)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
