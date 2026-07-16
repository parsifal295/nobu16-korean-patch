#!/usr/bin/env python3
"""Build a private Steam JP v6 P1 ``msgev`` residual-02 candidate.

Only the coordinate contract ``p1-MSG_PK_JP_msgev-02`` is in scope.  Korean
text is reused only when a base-game ``MSG/JP/ev_strdata.bin`` public overlay
has the identical UTF-16LE Japanese source hash.  The three source hashes not
found there have compact, project-authored Korean translations in
``translations.py``.  Every replacement is source-hash and format gated.

The Steam installation is read-only.  ``freeze`` emits source-free metadata
and ``build`` writes one complete resource only below ``KR_PATCH_WORK/tmp``.
Neither command creates a release asset, touches an executable, or uses an SC
container.
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


sys.dont_write_bytecode = True
WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
sys.path[:0] = [str(TOOLS), str(WORKSTREAM)]

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import MessageTable, parse_message_table, rebuild_message_table  # noqa: E402
MANUAL_TRANSLATIONS = runpy.run_path(str(WORKSTREAM / "translations.py"))["MANUAL_TRANSLATIONS"]


RESOURCE = "MSG_PK/JP/msgev.bin"
BUNDLE_ID = "p1-MSG_PK_JP_msgev-02"
FORMAT = "common"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / "steam_jp_msgev_p1_residual_02_v1" / "candidate"
AUDIT_PATH = (
    REPO
    / "workstreams"
    / "jp_active_message_residual_audit_v1"
    / "public"
    / "active_jp_remaining_coordinates.v1.json"
)
PUBLIC_OVERLAY = WORKSTREAM / "public" / "msgev_ko_steam_jp_p1_residual_02_185.v1.json"
VALIDATION = WORKSTREAM / "validation.v1.json"
CONTRACT = WORKSTREAM / "source_free_contract.v1.json"

OVERLAY_SCHEMA = "nobu16.kr.steam-jp-msgev-p1-residual-02-overlay.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-msgev-p1-residual-02-validation.v1"
CONTRACT_SCHEMA = "nobu16.kr.steam-jp-msgev-p1-residual-02-contract.v1"
MANIFEST_SCHEMA = "nobu16.kr.steam-jp-msgev-p1-residual-02-build-manifest.v1"

STOCK = {
    "packed_size": 1_040_799,
    "packed_sha256": "A8835C3520B29A076A21014E17B17D7AAABF4AC99D37D65C891415AC17BBF3F5",
    "raw_size": 1_036_708,
    "raw_sha256": "6D87086EA6B533EAB3F3745DB7564E8D7842E7DD603AD765B2D6D900644E00FB",
    "string_count": 17_916,
}
AUDIT_PIN = {
    "size": 1_188_084,
    "sha256": "AECC6969E8AD7AA00A8CC69B1DD8F6013922ABB085EE4E8397CA4D2368141E97",
}
EXPECTED_COORDINATE_COUNT = 185
EXPECTED_COORDINATE_SHA256 = "69FE48161322FBDF99CC5AB9660CAC3438B43FB0B90443038750A02E47ADAAFC"
EXPECTED_REUSE_COUNT = 182
EXPECTED_MANUAL_IDS = (7828, 7841, 7918)
REUSE_CATALOGS = (
    {
        "relative_path": "workstreams/base_ev_strdata_jp_residual_wave11/public/ev_strdata_ko_base_jp_residual_wave11_40.v1.json",
        "size": 24_810,
        "sha256": "5F8207E5D5E0ECDA39D39C8B15EE2F1707E7A68E1FADAF70FBFF5595F552108D",
    },
    {
        "relative_path": "workstreams/base_ev_strdata_jp_switch_v13_transfer_v1/public/ev_strdata_ko_base_jp_switch_v13_transfer_13045.v1.json",
        "size": 2_939_878,
        "sha256": "1A79E514616C284C140FB8A6618BA48AD648BA88EBE4D81F618B4C551C038B2A",
    },
)

HEX64_RE = re.compile(r"[0-9A-F]{64}\Z")
KANA_RE = re.compile(r"[\u3040-\u30ff\uff66-\uff9f]")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
CJK_OR_KANA_RE = re.compile(r"[\u3040-\u30ff\uff66-\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
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
)


class MsgevP1Residual02Error(ValueError):
    """Raised for an immutable input, translation, or output contract breach."""


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


def file_spec(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise MsgevP1Residual02Error(f"required file is missing: {path}")
    blob = path.read_bytes()
    return {"size": len(blob), "sha256": sha256_bytes(blob)}


def require_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise MsgevP1Residual02Error(f"{label} differs from its exact contract")


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
    finally:
        temporary.unlink(missing_ok=True)


def strict_object(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    folded: dict[str, str] = {}
    for key, value in pairs:
        previous = folded.get(key.casefold())
        if previous is not None:
            raise MsgevP1Residual02Error(f"duplicate/case-colliding JSON key: {previous!r}/{key!r}")
        folded[key.casefold()] = key
        result[key] = value
    return result


def read_json(path: Path) -> tuple[dict[str, Any], bytes]:
    blob = path.read_bytes()
    try:
        value = json.loads(blob.decode("utf-8-sig"), object_pairs_hook=strict_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MsgevP1Residual02Error(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise MsgevP1Residual02Error(f"JSON root is not an object: {path}")
    return value, blob


def path_from_repo(relative: str) -> Path:
    value = Path(relative)
    if not relative or value.is_absolute() or ".." in value.parts or "\\" in relative:
        raise MsgevP1Residual02Error("repository-relative path is unsafe")
    path = (REPO / value).resolve()
    try:
        path.relative_to(REPO.resolve())
    except ValueError as exc:
        raise MsgevP1Residual02Error("repository-relative path escaped workspace") from exc
    return path


def message_invariants(text: str) -> dict[str, Any]:
    printf_matches = list(PRINTF_RE.finditer(text))
    printf_percent_offsets = {
        offset
        for match in printf_matches
        for offset in range(match.start(), match.end())
        if text[offset] == "%"
    }
    esc_matches = list(ESC_RE.finditer(text))
    esc_offsets = {offset for match in esc_matches for offset in range(match.start(), match.end())}
    return {
        "printf": [match.group(0) for match in printf_matches],
        "unknown_percent_count": sum(
            1 for offset, char in enumerate(text) if char == "%" and offset not in printf_percent_offsets
        ),
        "leading_whitespace": text[: len(text) - len(text.lstrip())],
        "trailing_whitespace": text[len(text.rstrip()) :],
        "esc": [match.group(0) for match in esc_matches],
        "controls": [
            f"U+{ord(char):04X}"
            for offset, char in enumerate(text)
            if unicodedata.category(char) == "Cc" and char not in ("\r", "\n") and offset not in esc_offsets
        ],
        "line_breaks": LINE_BREAK_RE.findall(text),
        "pua": [f"U+{ord(char):04X}" for char in text if 0xE000 <= ord(char) <= 0xF8FF],
    }


def mismatch_keys(source: str, replacement: str) -> list[str]:
    before = message_invariants(source)
    after = message_invariants(replacement)
    return [key for key in INVARIANT_KEYS if before[key] != after[key]]


def load_stock(steam_root: Path) -> tuple[Path, bytes, bytes, MessageTable]:
    source_path = (steam_root.resolve() / Path(RESOURCE)).resolve()
    if not source_path.is_file():
        raise MsgevP1Residual02Error(f"active JP source is missing: {source_path}")
    packed = source_path.read_bytes()
    require_equal(
        {"packed_size": len(packed), "packed_sha256": sha256_bytes(packed)},
        {"packed_size": STOCK["packed_size"], "packed_sha256": STOCK["packed_sha256"]},
        "active Steam JP v6 packed baseline",
    )
    _header, raw = decompress_wrapper(packed)
    require_equal(
        {"raw_size": len(raw), "raw_sha256": sha256_bytes(raw)},
        {"raw_size": STOCK["raw_size"], "raw_sha256": STOCK["raw_sha256"]},
        "active Steam JP v6 raw baseline",
    )
    table = parse_message_table(raw)
    require_equal(table.string_count, STOCK["string_count"], "active Steam JP v6 string count")
    if rebuild_message_table(table, table.texts) != raw:
        raise MsgevP1Residual02Error("unchanged active JP table cannot round-trip byte-identically")
    return source_path, packed, raw, table


def load_audit_bundle() -> list[int]:
    require_equal(file_spec(AUDIT_PATH), AUDIT_PIN, "active residual audit pin")
    value, _blob = read_json(AUDIT_PATH)
    bundles = value.get("recommended_parallel_bundles")
    if not isinstance(bundles, list):
        raise MsgevP1Residual02Error("audit bundle vector is missing")
    selected = [row for row in bundles if isinstance(row, dict) and row.get("bundle_id") == BUNDLE_ID]
    if len(selected) != 1:
        raise MsgevP1Residual02Error("audit bundle is missing or duplicated")
    bundle = selected[0]
    required = {
        "bundle_id", "classification", "coordinate_count", "coordinate_sha256", "coordinates",
        "first_coordinate", "format", "last_coordinate", "priority", "resource",
        "safe_application_route", "translation_lane",
    }
    if set(bundle) != required:
        raise MsgevP1Residual02Error("audit bundle schema differs")
    if (
        bundle["resource"] != RESOURCE
        or bundle["format"] != FORMAT
        or bundle["classification"] != "japanese_kana_no_hangul"
        or bundle["priority"] != "P1"
    ):
        raise MsgevP1Residual02Error("audit bundle route differs")
    coordinates = bundle["coordinates"]
    if not isinstance(coordinates, list):
        raise MsgevP1Residual02Error("audit coordinates are missing")
    ids: list[int] = []
    for coordinate in coordinates:
        if not isinstance(coordinate, dict) or set(coordinate) != {"id"}:
            raise MsgevP1Residual02Error("audit coordinate schema differs")
        entry_id = coordinate["id"]
        if isinstance(entry_id, bool) or not isinstance(entry_id, int) or entry_id < 0:
            raise MsgevP1Residual02Error("audit coordinate is invalid")
        ids.append(entry_id)
    if ids != sorted(set(ids)):
        raise MsgevP1Residual02Error("audit coordinates are not sorted and unique")
    require_equal(len(ids), EXPECTED_COORDINATE_COUNT, "audit coordinate count")
    require_equal(canonical_hash([{ "id": entry_id } for entry_id in ids]), EXPECTED_COORDINATE_SHA256, "audit coordinate digest")
    require_equal(bundle["coordinate_count"], EXPECTED_COORDINATE_COUNT, "audit bundle coordinate count")
    require_equal(bundle["coordinate_sha256"], EXPECTED_COORDINATE_SHA256, "audit bundle coordinate digest")
    first_bundle = next((row for row in bundles if isinstance(row, dict) and row.get("bundle_id") == "p1-MSG_PK_JP_msgev-01"), None)
    if not isinstance(first_bundle, dict) or not isinstance(first_bundle.get("coordinates"), list):
        raise MsgevP1Residual02Error("adjacent residual-01 audit bundle is absent")
    first_ids = {row.get("id") for row in first_bundle["coordinates"] if isinstance(row, dict)}
    if first_ids & set(ids):
        raise MsgevP1Residual02Error("residual-02 overlaps residual-01 coordinates")
    return ids


def catalog_input_specs() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for expected in REUSE_CATALOGS:
        relative = str(expected["relative_path"])
        path = path_from_repo(relative)
        actual = file_spec(path)
        require_equal(actual, {"size": expected["size"], "sha256": expected["sha256"]}, f"reuse catalog {relative}")
        result.append({"relative_path": relative, **actual})
    return result


def load_base_ev_hash_index() -> tuple[dict[str, dict[str, set[str]]], list[dict[str, Any]]]:
    """Map exact JP source hashes to Korean strings and pinned catalog paths."""

    inputs = catalog_input_specs()
    index: dict[str, dict[str, set[str]]] = {}
    for input_spec in inputs:
        path = path_from_repo(str(input_spec["relative_path"]))
        document, _blob = read_json(path)
        if document.get("resource") != "MSG/JP/ev_strdata.bin" or not isinstance(document.get("entries"), list):
            raise MsgevP1Residual02Error("reuse catalog route/schema differs")
        for entry in document["entries"]:
            if not isinstance(entry, dict):
                raise MsgevP1Residual02Error("reuse catalog entry is invalid")
            source_hash = entry.get("source_jp_utf16le_sha256")
            korean = entry.get("ko")
            if not isinstance(source_hash, str) or not HEX64_RE.fullmatch(source_hash.upper()):
                raise MsgevP1Residual02Error("reuse catalog source hash is invalid")
            if not isinstance(korean, str) or not korean or "\0" in korean or "\ufffd" in korean:
                raise MsgevP1Residual02Error("reuse catalog Korean text is invalid")
            if CJK_OR_KANA_RE.search(korean) or not HANGUL_RE.search(korean):
                raise MsgevP1Residual02Error("reuse catalog Korean text has CJK/kana or no Hangul")
            per_hash = index.setdefault(source_hash.upper(), {})
            per_hash.setdefault(korean, set()).add(str(input_spec["relative_path"]))
    return index, inputs


def resolve_entries(table: MessageTable) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    ids = load_audit_bundle()
    if any(entry_id >= table.string_count for entry_id in ids):
        raise MsgevP1Residual02Error("audit coordinate lies beyond active JP table")
    reuse_index, input_specs = load_base_ev_hash_index()
    entries: list[dict[str, Any]] = []
    reused_ids: list[int] = []
    manual_ids: list[int] = []
    for entry_id in ids:
        source = table.texts[entry_id]
        source_hash = text_hash(source)
        choices = reuse_index.get(source_hash, {})
        if len(choices) == 1:
            korean, catalogs = next(iter(choices.items()))
            provenance = {
                "kind": "base_ev_strdata_exact_source_hash_reuse",
                "catalogs": sorted(catalogs),
            }
            reused_ids.append(entry_id)
        else:
            korean = MANUAL_TRANSLATIONS.get(entry_id)
            if korean is None:
                if choices:
                    raise MsgevP1Residual02Error(f"ambiguous base reuse at id {entry_id}")
                raise MsgevP1Residual02Error(f"no exact base reuse or manual Korean at id {entry_id}")
            provenance = {"kind": "project_authored_manual_korean"}
            manual_ids.append(entry_id)
        if not isinstance(korean, str) or not korean or "\0" in korean or "\ufffd" in korean:
            raise MsgevP1Residual02Error(f"unsafe Korean replacement at id {entry_id}")
        if CJK_OR_KANA_RE.search(korean) or not HANGUL_RE.search(korean):
            raise MsgevP1Residual02Error(f"Korean replacement retains CJK/kana at id {entry_id}")
        mismatches = mismatch_keys(source, korean)
        if mismatches:
            raise MsgevP1Residual02Error(f"format/token mismatch at id {entry_id}: {mismatches!r}")
        entries.append(
            {
                "id": entry_id,
                "source_jp_utf16le_sha256": source_hash,
                "ko": korean,
                "ko_utf16le_sha256": text_hash(korean),
                "format_signature_sha256": canonical_hash(message_invariants(source)),
                "provenance": provenance,
            }
        )
    require_equal(len(reused_ids), EXPECTED_REUSE_COUNT, "exact base source-hash reuse count")
    require_equal(tuple(manual_ids), EXPECTED_MANUAL_IDS, "manual residual IDs")
    require_equal(tuple(sorted(MANUAL_TRANSLATIONS)), EXPECTED_MANUAL_IDS, "manual translation table IDs")
    require_equal(len(entries), EXPECTED_COORDINATE_COUNT, "resolved entry count")
    return entries, input_specs


def validate_entries(table: MessageTable, entries: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    required = {
        "id", "source_jp_utf16le_sha256", "ko", "ko_utf16le_sha256",
        "format_signature_sha256", "provenance",
    }
    ids = load_audit_bundle()
    if len(entries) != len(ids):
        raise MsgevP1Residual02Error("entry count differs from audit bundle")
    normalized: list[dict[str, Any]] = []
    observed_ids: list[int] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping) or set(entry) != required:
            raise MsgevP1Residual02Error(f"overlay entry {index} schema differs")
        entry_id = entry["id"]
        if isinstance(entry_id, bool) or not isinstance(entry_id, int) or entry_id not in ids:
            raise MsgevP1Residual02Error(f"overlay entry {index} id is outside residual-02")
        source_hash = entry["source_jp_utf16le_sha256"]
        korean_hash = entry["ko_utf16le_sha256"]
        format_hash = entry["format_signature_sha256"]
        korean = entry["ko"]
        if not all(isinstance(value, str) and HEX64_RE.fullmatch(value) for value in (source_hash, korean_hash, format_hash)):
            raise MsgevP1Residual02Error(f"overlay entry {entry_id} hash field is invalid")
        if not isinstance(korean, str) or not korean or "\0" in korean or "\ufffd" in korean:
            raise MsgevP1Residual02Error(f"overlay entry {entry_id} Korean text is invalid")
        if CJK_OR_KANA_RE.search(korean) or not HANGUL_RE.search(korean):
            raise MsgevP1Residual02Error(f"overlay entry {entry_id} retains CJK/kana")
        source = table.texts[entry_id]
        require_equal(text_hash(source), source_hash, f"overlay entry {entry_id} source hash")
        require_equal(text_hash(korean), korean_hash, f"overlay entry {entry_id} Korean hash")
        require_equal(canonical_hash(message_invariants(source)), format_hash, f"overlay entry {entry_id} format signature")
        mismatches = mismatch_keys(source, korean)
        if mismatches:
            raise MsgevP1Residual02Error(f"overlay entry {entry_id} format/token mismatch: {mismatches!r}")
        provenance = entry["provenance"]
        if not isinstance(provenance, Mapping) or not isinstance(provenance.get("kind"), str):
            raise MsgevP1Residual02Error(f"overlay entry {entry_id} provenance is invalid")
        observed_ids.append(entry_id)
        normalized.append(dict(entry))
    require_equal(observed_ids, ids, "overlay coordinate order")
    # Re-derive the allowed Korean string and provenance from the pinned base
    # catalogs.  A correct source hash and token profile alone is not enough
    # to prove that a purported reuse is the exact approved reuse.
    expected, _reuse_inputs = resolve_entries(table)
    require_equal(normalized, expected, "overlay exact reuse/manual resolution")
    return normalized


def make_overlay(entries: Sequence[Mapping[str, Any]], reuse_inputs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": "msgev_ko_steam_jp_p1_residual_02_185.v1",
        "resource": RESOURCE,
        "base_language": "JP",
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
            "sc_container_used": False,
        },
        "active_v6_baseline": dict(STOCK),
        "audit_bundle": {
            "bundle_id": BUNDLE_ID,
            "audit_sha256": AUDIT_PIN["sha256"],
            "coordinate_count": EXPECTED_COORDINATE_COUNT,
            "coordinate_sha256": EXPECTED_COORDINATE_SHA256,
        },
        "base_ev_reuse_inputs": [dict(value) for value in reuse_inputs],
        "entry_count": len(entries),
        "coordinate_sha256": canonical_hash([{ "id": entry["id"] } for entry in entries]),
        "entries": [dict(entry) for entry in entries],
    }


def validate_public_overlay(value: Mapping[str, Any], table: MessageTable) -> list[dict[str, Any]]:
    required = {
        "schema", "overlay_id", "resource", "base_language", "distribution_policy", "active_v6_baseline",
        "audit_bundle", "base_ev_reuse_inputs", "entry_count", "coordinate_sha256", "entries",
    }
    if set(value) != required or value.get("schema") != OVERLAY_SCHEMA:
        raise MsgevP1Residual02Error("public overlay schema differs")
    if value.get("overlay_id") != "msgev_ko_steam_jp_p1_residual_02_185.v1" or value.get("resource") != RESOURCE:
        raise MsgevP1Residual02Error("public overlay route differs")
    if value.get("base_language") != "JP" or value.get("active_v6_baseline") != STOCK:
        raise MsgevP1Residual02Error("public overlay baseline differs")
    if value.get("distribution_policy") != {
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "sc_container_used": False,
    }:
        raise MsgevP1Residual02Error("public overlay distribution policy differs")
    if value.get("audit_bundle") != {
        "bundle_id": BUNDLE_ID,
        "audit_sha256": AUDIT_PIN["sha256"],
        "coordinate_count": EXPECTED_COORDINATE_COUNT,
        "coordinate_sha256": EXPECTED_COORDINATE_SHA256,
    }:
        raise MsgevP1Residual02Error("public overlay audit contract differs")
    require_equal(value.get("base_ev_reuse_inputs"), catalog_input_specs(), "public overlay reuse inputs")
    raw_entries = value.get("entries")
    if not isinstance(raw_entries, list) or value.get("entry_count") != len(raw_entries):
        raise MsgevP1Residual02Error("public overlay entry vector differs")
    entries = validate_entries(table, raw_entries)
    require_equal(value.get("coordinate_sha256"), canonical_hash([{ "id": entry["id"] } for entry in entries]), "public overlay coordinate digest")
    return entries


def candidate_from_entries(
    packed: bytes, raw: bytes, table: MessageTable, entries: Sequence[Mapping[str, Any]]
) -> tuple[bytes, bytes, list[int]]:
    selected = validate_entries(table, entries)
    selected_ids = {int(entry["id"]) for entry in selected}
    texts = list(table.texts)
    changed: list[int] = []
    for entry in selected:
        entry_id = int(entry["id"])
        korean = str(entry["ko"])
        if texts[entry_id] != korean:
            changed.append(entry_id)
        texts[entry_id] = korean
    raw_a = rebuild_message_table(table, texts)
    raw_b = rebuild_message_table(table, texts)
    require_equal(raw_a, raw_b, "deterministic raw rebuild")
    packed_a = recompress_wrapper(raw_a, packed)
    packed_b = recompress_wrapper(raw_b, packed)
    require_equal(packed_a, packed_b, "deterministic packed rebuild")
    _header, checked_raw = decompress_wrapper(packed_a)
    checked = parse_message_table(checked_raw)
    require_equal(checked_raw, raw_a, "candidate decompression")
    require_equal(checked.texts, tuple(texts), "candidate parser text round-trip")
    if rebuild_message_table(checked, checked.texts) != checked_raw:
        raise MsgevP1Residual02Error("candidate unchanged parse/rebuild differs")
    for entry_id, source in enumerate(table.texts):
        expected = texts[entry_id]
        if checked.texts[entry_id] != expected:
            raise MsgevP1Residual02Error(f"candidate text differs at id {entry_id}")
        if entry_id not in selected_ids:
            if source.encode("utf-16le") + b"\0\0" != checked.texts[entry_id].encode("utf-16le") + b"\0\0":
                raise MsgevP1Residual02Error(f"nonselected UTF-16LE payload differs at id {entry_id}")
    if (
        checked.string_count != table.string_count
        or checked.block_offset != table.block_offset
        or checked.table_offset != table.table_offset
        or checked.table_size != table.table_size
        or checked.string_start != table.string_start
    ):
        raise MsgevP1Residual02Error("candidate message table structure differs")
    stock_prefix = bytearray(raw[: table.table_offset])
    candidate_prefix = bytearray(checked_raw[: checked.table_offset])
    struct.pack_into("<I", stock_prefix, 8, 0)
    struct.pack_into("<I", candidate_prefix, 8, 0)
    require_equal(stock_prefix, candidate_prefix, "opaque prefix except logical size")
    require_equal(changed, [entry["id"] for entry in selected], "effective changed coordinate vector")
    return packed_a, raw_a, changed


def make_validation(entries: Sequence[Mapping[str, Any]], candidate: bytes, candidate_raw: bytes, changed: Sequence[int]) -> dict[str, Any]:
    reused = sum(entry["provenance"]["kind"] == "base_ev_strdata_exact_source_hash_reuse" for entry in entries)
    manual = sum(entry["provenance"]["kind"] == "project_authored_manual_korean" for entry in entries)
    return {
        "schema": VALIDATION_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "resource": RESOURCE,
        "active_v6_baseline": dict(STOCK),
        "audit_bundle_id": BUNDLE_ID,
        "entry_count": len(entries),
        "coordinate_sha256": canonical_hash([{ "id": entry["id"] } for entry in entries]),
        "reuse_count": reused,
        "manual_count": manual,
        "manual_coordinate_sha256": canonical_hash([{ "id": entry_id } for entry_id in EXPECTED_MANUAL_IDS]),
        "expected_candidate": {
            "packed_size": len(candidate),
            "packed_sha256": sha256_bytes(candidate),
            "raw_size": len(candidate_raw),
            "raw_sha256": sha256_bytes(candidate_raw),
            "string_count": STOCK["string_count"],
        },
        "effective_change_count": len(changed),
        "effective_change_coordinate_sha256": canonical_hash([{ "id": entry_id } for entry_id in changed]),
        "checks": {
            "active_v6_baseline_pinned": True,
            "audit_coordinate_scope_exact": True,
            "residual_01_coordinate_overlap": False,
            "base_ev_reuse_requires_exact_source_hash": True,
            "base_ev_reuse_count": EXPECTED_REUSE_COUNT,
            "manual_korean_ids_exact": list(EXPECTED_MANUAL_IDS),
            "per_entry_jp_source_hash_gated": True,
            "format_and_token_profile_preserved": True,
            "nonselected_utf16le_payloads_preserved": True,
            "parser_roundtrip_valid": True,
            "deterministic_raw_and_packed_rebuild": True,
            "steam_installation_written": False,
            "sc_container_used": False,
            "release_asset_written": False,
            "github_written": False,
        },
    }


def make_contract(overlay_blob: bytes, validation_blob: bytes, validation: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": CONTRACT_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "resource": RESOURCE,
        "runtime_route": {"language": "JP", "sc_container_used": False, "installed_game_file_written": False},
        "active_v6_baseline": dict(STOCK),
        "audit_bundle": {"bundle_id": BUNDLE_ID, "coordinate_sha256": EXPECTED_COORDINATE_SHA256},
        "overlay": {
            "relative_path": "workstreams/steam_jp_msgev_p1_residual_02_v1/public/msgev_ko_steam_jp_p1_residual_02_185.v1.json",
            "sha256": sha256_bytes(overlay_blob),
            "entry_count": EXPECTED_COORDINATE_COUNT,
        },
        "validation": {
            "relative_path": "workstreams/steam_jp_msgev_p1_residual_02_v1/validation.v1.json",
            "sha256": sha256_bytes(validation_blob),
        },
        "expected_candidate": dict(validation["expected_candidate"]),
        "output_policy": {"complete_candidate_private_only": True, "allowed_root": "tmp", "relative_path": RESOURCE},
        "proofs": {
            "active_v6_baseline_pinned": True,
            "exact_base_ev_source_hash_reuse": True,
            "manual_remainder_only": True,
            "per_entry_jp_source_hash_gated": True,
            "format_and_token_profile_preserved": True,
            "nonselected_utf16le_payloads_preserved": True,
            "parser_roundtrip_valid": True,
            "deterministic_raw_and_packed_rebuild": True,
            "steam_installation_read_only": True,
        },
    }


def assert_source_free(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if CJK_OR_KANA_RE.search(text) or "MSG_PK/SC" in text or "RES_SC" in text or "source_sc" in text.casefold():
        raise MsgevP1Residual02Error(f"artifact is not JP-route source-free: {path}")


def require_private_output_root(output_root: Path) -> Path:
    resolved = output_root.resolve()
    private_root = (REPO / "tmp").resolve()
    try:
        resolved.relative_to(private_root)
    except ValueError as exc:
        raise MsgevP1Residual02Error("candidate output must stay below KR_PATCH_WORK/tmp") from exc
    if resolved == private_root:
        raise MsgevP1Residual02Error("KR_PATCH_WORK/tmp itself cannot be a candidate root")
    return resolved


def freeze(steam_root: Path) -> dict[str, Any]:
    _source_path, packed, raw, table = load_stock(steam_root)
    entries, reuse_inputs = resolve_entries(table)
    entries = validate_entries(table, entries)
    candidate, candidate_raw, changed = candidate_from_entries(packed, raw, table, entries)
    overlay = make_overlay(entries, reuse_inputs)
    overlay_blob = pretty_bytes(overlay)
    validation = make_validation(entries, candidate, candidate_raw, changed)
    validation_blob = pretty_bytes(validation)
    contract = make_contract(overlay_blob, validation_blob, validation)
    atomic_write(PUBLIC_OVERLAY, overlay_blob)
    atomic_write(VALIDATION, validation_blob)
    atomic_write(CONTRACT, pretty_bytes(contract))
    for path in (PUBLIC_OVERLAY, VALIDATION, CONTRACT):
        assert_source_free(path)
    return {
        "entry_count": len(entries),
        "reuse_count": validation["reuse_count"],
        "manual_count": validation["manual_count"],
        "candidate_sha256": sha256_bytes(candidate),
        "candidate_raw_sha256": sha256_bytes(candidate_raw),
        "installed_game_file_modified": False,
    }


def load_frozen_inputs(steam_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], bytes, bytes, MessageTable]:
    source_path, packed, raw, table = load_stock(steam_root)
    contract, _contract_blob = read_json(CONTRACT)
    required = {
        "schema", "source_free", "contains_commercial_source_text", "contains_complete_game_resource", "resource",
        "runtime_route", "active_v6_baseline", "audit_bundle", "overlay", "validation", "expected_candidate",
        "output_policy", "proofs",
    }
    if set(contract) != required or contract.get("schema") != CONTRACT_SCHEMA or contract.get("resource") != RESOURCE:
        raise MsgevP1Residual02Error("frozen contract schema/route differs")
    if contract.get("runtime_route") != {"language": "JP", "sc_container_used": False, "installed_game_file_written": False}:
        raise MsgevP1Residual02Error("frozen contract runtime route differs")
    if contract.get("active_v6_baseline") != STOCK or contract.get("audit_bundle") != {"bundle_id": BUNDLE_ID, "coordinate_sha256": EXPECTED_COORDINATE_SHA256}:
        raise MsgevP1Residual02Error("frozen contract baseline/audit differs")
    if contract.get("output_policy") != {"complete_candidate_private_only": True, "allowed_root": "tmp", "relative_path": RESOURCE}:
        raise MsgevP1Residual02Error("frozen contract output policy differs")
    if not isinstance(contract.get("proofs"), dict) or any(value is not True for value in contract["proofs"].values()):
        raise MsgevP1Residual02Error("frozen contract proofs are incomplete")
    overlay_path = path_from_repo(str(contract["overlay"].get("relative_path", "")))
    overlay, overlay_blob = read_json(overlay_path)
    require_equal(sha256_bytes(overlay_blob), contract["overlay"].get("sha256"), "frozen public overlay hash")
    entries = validate_public_overlay(overlay, table)
    validation_path = path_from_repo(str(contract["validation"].get("relative_path", "")))
    validation_blob = validation_path.read_bytes()
    require_equal(sha256_bytes(validation_blob), contract["validation"].get("sha256"), "frozen validation hash")
    for path in (overlay_path, validation_path, CONTRACT):
        assert_source_free(path)
    if source_path != (steam_root.resolve() / Path(RESOURCE)).resolve():
        raise MsgevP1Residual02Error("unexpected active source path")
    return contract, entries, packed, raw, table


def build_staging_candidate(steam_root: Path, output_root: Path) -> dict[str, Any]:
    output = require_private_output_root(output_root)
    source_path, stock_before, _raw_before, _table_before = load_stock(steam_root)
    contract, entries, packed, raw, table = load_frozen_inputs(steam_root)
    require_equal(packed, stock_before, "active Steam source while loading frozen inputs")
    candidate, candidate_raw, changed = candidate_from_entries(packed, raw, table, entries)
    observed = {
        "packed_size": len(candidate),
        "packed_sha256": sha256_bytes(candidate),
        "raw_size": len(candidate_raw),
        "raw_sha256": sha256_bytes(candidate_raw),
        "string_count": table.string_count,
    }
    require_equal(observed, contract["expected_candidate"], "candidate versus frozen contract")
    target = (output / Path(RESOURCE)).resolve()
    try:
        target.relative_to(output)
    except ValueError as exc:
        raise MsgevP1Residual02Error("candidate target escaped private output root") from exc
    if target == source_path:
        raise MsgevP1Residual02Error("refusing to target Steam installation")
    atomic_write(target, candidate)
    require_equal(target.read_bytes(), candidate, "written private candidate")
    require_equal(source_path.read_bytes(), stock_before, "Steam source after private build")
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "resource": RESOURCE,
        "active_v6_baseline": dict(STOCK),
        "target": observed,
        "entry_count": len(entries),
        "effective_change_count": len(changed),
        "coordinate_sha256": canonical_hash([{ "id": entry["id"] } for entry in entries]),
        "effective_change_coordinate_sha256": canonical_hash([{ "id": entry_id } for entry_id in changed]),
        "output": {"relative_path": RESOURCE, "complete_candidate_private_only": True, "installed_game_file_modified": False},
        "checks": {"contract_hash": "OK", "source_hash_gates": "OK", "token_profiles": "OK", "steam_source_unchanged": "OK"},
    }
    atomic_write(output / "build_manifest.v1.json", pretty_bytes(manifest))
    return {"candidate_path": str(target), "manifest_path": str(output / "build_manifest.v1.json"), **observed, "installed_game_file_modified": False}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    freeze_parser = commands.add_parser("freeze", help="write source-free overlay, validation, and contract")
    freeze_parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    build_parser = commands.add_parser("build", help="write only a private staging candidate")
    build_parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    build_parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    verify_parser = commands.add_parser("verify", help="recompute the frozen candidate without writing a resource")
    verify_parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    return parser


def verify(steam_root: Path) -> dict[str, Any]:
    contract, entries, packed, raw, table = load_frozen_inputs(steam_root)
    first, first_raw, changed = candidate_from_entries(packed, raw, table, entries)
    second, second_raw, changed_second = candidate_from_entries(packed, raw, table, entries)
    require_equal(first, second, "deterministic candidate A/B")
    require_equal(first_raw, second_raw, "deterministic raw A/B")
    require_equal(changed, changed_second, "deterministic changed IDs A/B")
    require_equal(
        {
            "packed_size": len(first), "packed_sha256": sha256_bytes(first),
            "raw_size": len(first_raw), "raw_sha256": sha256_bytes(first_raw), "string_count": table.string_count,
        },
        contract["expected_candidate"],
        "verified candidate versus frozen contract",
    )
    return {"status": "PASS", "entry_count": len(entries), "candidate_sha256": sha256_bytes(first), "output_written": False}


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "freeze":
            result = freeze(args.steam_root)
        elif args.command == "build":
            result = build_staging_candidate(args.steam_root, args.output_root)
        else:
            result = verify(args.steam_root)
    except (MsgevP1Residual02Error, OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
