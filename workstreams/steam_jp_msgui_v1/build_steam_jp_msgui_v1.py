#!/usr/bin/env python3
"""Freeze and build the Steam Japanese-native PK ``msgui.bin`` candidate.

The release input is a source-text-free JP overlay containing only numeric
string IDs, hashes of the corresponding official JP strings, and
project-authored Korean replacements.  A candidate is always rebuilt from the
pinned Steam JP stock file.  Neither an SC container nor a previously patched
binary is accepted by this program.

Complete game-resource output is restricted to ``KR_PATCH_WORK/tmp``.  The
installed game file is read-only input and is hash-checked again after every
build.
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
REPO_ROOT = SCRIPT_PATH.parents[2]
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))

from nobu16_lz4 import LZ4Error, decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import (  # noqa: E402
    MessageTable,
    MessageTableError,
    parse_message_table,
    rebuild_message_table,
)


RESOURCE = "MSG_PK/JP/msgui.bin"
DEFAULT_GAME_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_SOURCE_OVERLAY = REPO_ROOT / "data" / "public" / "msgui_ko_0000_5099.v0.2.json"
DEFAULT_PUBLIC_OVERLAY = WORKSTREAM_ROOT / "public" / "msgui_ko_pk_jp_steam_native_v1.json"
DEFAULT_AUDIT = WORKSTREAM_ROOT / "remap_audit.v1.json"
DEFAULT_CONTRACT = WORKSTREAM_ROOT / "source_free_contract.v1.json"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "tmp" / "steam_jp_msgui_v1"

SOURCE_OVERLAY_SHA256 = "5DC3C0E14E2131FC2BB4252DF3B25E1F10E462205EAB715E2923298A714B8C14"
SOURCE_OVERLAY_ENTRY_COUNT = 4037

STOCK_PACKED_SIZE = 64976
STOCK_PACKED_SHA256 = "9775D4B7253828899F7EF0DF2E88AB28121ACB260E1381F3D706C6A1065D504A"
STOCK_RAW_SIZE = 105864
STOCK_RAW_SHA256 = "F79AE8B004AAE73F5F67ED0F858AAD74083649040F69A317E48212F74761095C"
STOCK_STRING_COUNT = 5100

OVERLAY_SCHEMA = "nobu16.kr.steam-jp-msgui-overlay.v1"
AUDIT_SCHEMA = "nobu16.kr.steam-jp-msgui-remap-audit.v1"
CONTRACT_SCHEMA = "nobu16.kr.steam-jp-msgui-source-free-contract.v1"
MANIFEST_SCHEMA = "nobu16.kr.steam-jp-msgui-build-manifest.v1"
SOURCE_OVERLAY_SCHEMA = "nobu16.kr.msgui-translation-overlay.v1"

HEX64_RE = re.compile(r"[0-9A-F]{64}\Z")
PRINTF_RE = re.compile(
    r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?"
    r"(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
LINE_BREAK_RE = re.compile(r"\r\n|\n|\r")
NON_SEMANTIC_CATEGORIES = frozenset(
    ("Cc", "Cf", "Cs", "Mn", "Me", "Zl", "Zp", "Zs", "Cn")
)
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


class SteamJpMsguiError(ValueError):
    """Raised when any frozen structure or source-free boundary differs."""


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def text_hash(text: str) -> str:
    return sha256_bytes(text.encode("utf-16le"))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def canonical_hash(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def pretty_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def atomic_write(path: Path, blob: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
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
            raise SteamJpMsguiError(
                f"duplicate or case-colliding JSON key {collision!r}/{key!r}"
            )
        folded[key.casefold()] = key
        result[key] = value
    return result


def read_json(path: Path) -> tuple[dict[str, Any], bytes]:
    blob = path.read_bytes()
    try:
        value = json.loads(blob.decode("utf-8-sig"), object_pairs_hook=strict_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SteamJpMsguiError(f"invalid JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SteamJpMsguiError(f"JSON root must be an object: {path}")
    return value, blob


def require_exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        raise SteamJpMsguiError(
            f"{label} keys differ: missing={sorted(expected - actual)!r}, "
            f"unknown={sorted(actual - expected)!r}"
        )


def require_hash(value: Any, label: str) -> str:
    if not isinstance(value, str) or HEX64_RE.fullmatch(value) is None:
        raise SteamJpMsguiError(f"{label} must be an uppercase SHA-256")
    return value


def require_int(value: Any, label: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise SteamJpMsguiError(f"{label} must be an integer >= {minimum}")
    return value


def has_semantic_text(text: str) -> bool:
    consumed = {
        index
        for match in ESC_RE.finditer(text)
        for index in range(match.start(), match.end())
    }
    return any(
        index not in consumed
        and not char.isspace()
        and unicodedata.category(char) not in NON_SEMANTIC_CATEGORIES
        for index, char in enumerate(text)
    )


def has_cjk_or_kana(text: str) -> bool:
    return any(
        0x3040 <= ord(char) <= 0x30FF
        or 0x3400 <= ord(char) <= 0x9FFF
        or 0xF900 <= ord(char) <= 0xFAFF
        for char in text
    )


def message_invariants(text: str) -> dict[str, Any]:
    printf_matches = list(PRINTF_RE.finditer(text))
    consumed_percent = {
        index
        for match in printf_matches
        for index in range(match.start(), match.end())
        if text[index] == "%"
    }
    escape_matches = list(ESC_RE.finditer(text))
    consumed_escape = {
        index
        for match in escape_matches
        for index in range(match.start(), match.end())
    }
    return {
        "printf": [match.group(0) for match in printf_matches],
        "unknown_percent_count": sum(
            1
            for index, char in enumerate(text)
            if char == "%" and index not in consumed_percent
        ),
        "leading_whitespace": text[: len(text) - len(text.lstrip())],
        "trailing_whitespace": text[len(text.rstrip()) :],
        "esc": [match.group(0) for match in escape_matches],
        "controls": [
            f"U+{ord(char):04X}"
            for index, char in enumerate(text)
            if unicodedata.category(char) == "Cc"
            and char not in ("\r", "\n")
            and index not in consumed_escape
        ],
        "line_breaks": LINE_BREAK_RE.findall(text),
        "pua": [
            f"U+{ord(char):04X}"
            for char in text
            if 0xE000 <= ord(char) <= 0xF8FF
        ],
    }


def mismatch_keys(source: str, replacement: str) -> list[str]:
    before = message_invariants(source)
    after = message_invariants(replacement)
    return [key for key in INVARIANT_KEYS if before[key] != after[key]]


def stock_spec() -> dict[str, Any]:
    return {
        "packed_size": STOCK_PACKED_SIZE,
        "packed_sha256": STOCK_PACKED_SHA256,
        "raw_size": STOCK_RAW_SIZE,
        "raw_sha256": STOCK_RAW_SHA256,
        "string_count": STOCK_STRING_COUNT,
    }


def validate_stock_spec(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SteamJpMsguiError(f"{label} must be an object")
    require_exact_keys(
        value,
        {"packed_size", "packed_sha256", "raw_size", "raw_sha256", "string_count"},
        label,
    )
    normalized = {
        "packed_size": require_int(value["packed_size"], f"{label}.packed_size", minimum=1),
        "packed_sha256": require_hash(value["packed_sha256"], f"{label}.packed_sha256"),
        "raw_size": require_int(value["raw_size"], f"{label}.raw_size", minimum=1),
        "raw_sha256": require_hash(value["raw_sha256"], f"{label}.raw_sha256"),
        "string_count": require_int(value["string_count"], f"{label}.string_count", minimum=1),
    }
    if normalized != stock_spec():
        raise SteamJpMsguiError(f"{label} differs from the frozen Steam JP stock")
    return normalized


def load_stock(game_root: Path) -> tuple[Path, bytes, bytes, MessageTable]:
    source_path = (game_root.resolve() / Path(RESOURCE)).resolve()
    packed = source_path.read_bytes()
    if len(packed) != STOCK_PACKED_SIZE or sha256_bytes(packed) != STOCK_PACKED_SHA256:
        raise SteamJpMsguiError(
            f"Steam JP packed stock mismatch: size={len(packed)} "
            f"sha256={sha256_bytes(packed)}"
        )
    _header, raw = decompress_wrapper(packed)
    if len(raw) != STOCK_RAW_SIZE or sha256_bytes(raw) != STOCK_RAW_SHA256:
        raise SteamJpMsguiError(
            f"Steam JP raw stock mismatch: size={len(raw)} sha256={sha256_bytes(raw)}"
        )
    table = parse_message_table(raw)
    if table.string_count != STOCK_STRING_COUNT:
        raise SteamJpMsguiError(
            f"Steam JP string count {table.string_count} != {STOCK_STRING_COUNT}"
        )
    if rebuild_message_table(table, table.texts) != raw:
        raise SteamJpMsguiError("Steam JP unchanged parse/rebuild is not byte-identical")
    return source_path, packed, raw, table


def load_source_overlay(path: Path) -> tuple[list[dict[str, Any]], bytes]:
    value, blob = read_json(path)
    observed = sha256_bytes(blob)
    if observed != SOURCE_OVERLAY_SHA256:
        raise SteamJpMsguiError(
            f"Korean source overlay hash mismatch: expected={SOURCE_OVERLAY_SHA256}, "
            f"observed={observed}"
        )
    if value.get("schema") != SOURCE_OVERLAY_SCHEMA:
        raise SteamJpMsguiError("unsupported Korean source overlay schema")
    if value.get("resource") != "msgui" or value.get("entry_count") != SOURCE_OVERLAY_ENTRY_COUNT:
        raise SteamJpMsguiError("Korean source overlay resource/count mismatch")
    raw_entries = value.get("entries")
    if not isinstance(raw_entries, list) or len(raw_entries) != SOURCE_OVERLAY_ENTRY_COUNT:
        raise SteamJpMsguiError("Korean source overlay entries mismatch")
    entries: list[dict[str, Any]] = []
    ids: list[int] = []
    for index, item in enumerate(raw_entries):
        if not isinstance(item, dict):
            raise SteamJpMsguiError(f"source overlay entry {index} must be an object")
        entry_id = require_int(item.get("id"), f"source overlay entry {index}.id")
        ko = item.get("ko")
        if (
            not isinstance(ko, str)
            or "\0" in ko
            or not has_semantic_text(ko)
            or has_cjk_or_kana(ko)
            or "\ufffd" in ko
        ):
            raise SteamJpMsguiError(f"source overlay id {entry_id} has unsafe Korean text")
        ids.append(entry_id)
        entries.append({"id": entry_id, "ko": ko})
    if ids != sorted(set(ids)):
        raise SteamJpMsguiError("Korean source overlay IDs must be sorted and unique")
    if ids and ids[-1] >= STOCK_STRING_COUNT:
        raise SteamJpMsguiError("Korean source overlay contains an ID outside Steam JP msgui")
    return entries, blob


def remap_entries(
    source_entries: Sequence[dict[str, Any]], table: MessageTable
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for entry in source_entries:
        entry_id = int(entry["id"])
        ko = str(entry["ko"])
        jp = table.texts[entry_id]
        mismatches = mismatch_keys(jp, ko)
        if mismatches:
            rejected.append(
                {
                    "id": entry_id,
                    "mismatch_keys": mismatches,
                    "source_jp_utf16le_sha256": text_hash(jp),
                    "ko_utf16le_sha256": text_hash(ko),
                }
            )
            continue
        accepted.append(
            {
                "id": entry_id,
                "source_jp_utf16le_sha256": text_hash(jp),
                "ko": ko,
            }
        )
    return accepted, rejected


def coordinate_hash(ids: Iterable[int]) -> str:
    return canonical_hash(sorted(ids))


def make_public_overlay(
    accepted: Sequence[dict[str, Any]], rejected_count: int, source_blob: bytes, table: MessageTable
) -> dict[str, Any]:
    no_op_count = sum(table.texts[int(entry["id"])] == entry["ko"] for entry in accepted)
    return {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": "msgui_ko_pk_jp_steam_native_v1",
        "resource": RESOURCE,
        "base_language": "JP",
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
            "include_in_public_patch": True,
        },
        "source_overlay_provenance": {
            "relative_path": "data/public/msgui_ko_0000_5099.v0.2.json",
            "sha256": sha256_bytes(source_blob),
            "entry_count": SOURCE_OVERLAY_ENTRY_COUNT,
        },
        "stock_jp": stock_spec(),
        "mapping_policy": {
            "coordinate": "numeric MSGUI string ID in the pinned 5100-slot JP table",
            "source_guard": "SHA-256 of exact UTF-16LE JP source string",
            "format_guard": list(INVARIANT_KEYS),
            "requires_exact_format_profile": True,
            "sc_container_used": False,
            "legacy_candidate_binary_used": False,
        },
        "entry_count": len(accepted),
        "effective_change_count": len(accepted) - no_op_count,
        "no_op_count": no_op_count,
        "rejected_entry_count": rejected_count,
        "entries": list(accepted),
    }


def make_audit(
    accepted: Sequence[dict[str, Any]],
    rejected: Sequence[dict[str, Any]],
    source_blob: bytes,
) -> dict[str, Any]:
    reason_dictionary = sorted({key for row in rejected for key in row["mismatch_keys"]})
    reason_index = {reason: index for index, reason in enumerate(reason_dictionary)}
    compact_rejected = [
        [
            row["id"],
            [reason_index[key] for key in row["mismatch_keys"]],
            row["source_jp_utf16le_sha256"],
            row["ko_utf16le_sha256"],
        ]
        for row in rejected
    ]
    counts = Counter(key for row in rejected for key in row["mismatch_keys"])
    return {
        "schema": AUDIT_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "resource": RESOURCE,
        "stock_jp": stock_spec(),
        "source_overlay": {
            "relative_path": "data/public/msgui_ko_0000_5099.v0.2.json",
            "sha256": sha256_bytes(source_blob),
            "entry_count": SOURCE_OVERLAY_ENTRY_COUNT,
        },
        "result": {
            "input_entry_count": SOURCE_OVERLAY_ENTRY_COUNT,
            "mapped_entry_count": len(accepted),
            "unmapped_entry_count": len(rejected),
            "mapped_coordinate_sha256": coordinate_hash(int(row["id"]) for row in accepted),
            "unmapped_coordinate_sha256": coordinate_hash(int(row["id"]) for row in rejected),
            "reason_dictionary": reason_dictionary,
            "reason_counts": dict(sorted(counts.items())),
            "unmapped_encoding": "[id,mismatch_reason_indexes,source_jp_utf16le_sha256,ko_utf16le_sha256]",
            "unmapped_entries": compact_rejected,
        },
        "proof": {
            "runtime_container_language": "JP",
            "jp_source_hash_guarded": True,
            "jp_format_profile_guarded": True,
            "sc_container_used": False,
            "legacy_candidate_binary_used": False,
            "publisher_source_text_embedded": False,
        },
    }


def validate_public_overlay(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, dict):
        raise SteamJpMsguiError("JP overlay root must be an object")
    require_exact_keys(
        value,
        {
            "schema",
            "overlay_id",
            "resource",
            "base_language",
            "distribution_policy",
            "source_overlay_provenance",
            "stock_jp",
            "mapping_policy",
            "entry_count",
            "effective_change_count",
            "no_op_count",
            "rejected_entry_count",
            "entries",
        },
        "JP overlay",
    )
    if value["schema"] != OVERLAY_SCHEMA or value["resource"] != RESOURCE:
        raise SteamJpMsguiError("JP overlay schema/resource mismatch")
    if value["base_language"] != "JP":
        raise SteamJpMsguiError("JP overlay base_language must be JP")
    if value["overlay_id"] != "msgui_ko_pk_jp_steam_native_v1":
        raise SteamJpMsguiError("JP overlay ID mismatch")
    if value["distribution_policy"] != {
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "include_in_public_patch": True,
    }:
        raise SteamJpMsguiError("JP overlay distribution policy is unsafe")
    validate_stock_spec(value["stock_jp"], "JP overlay stock_jp")
    provenance = value["source_overlay_provenance"]
    if not isinstance(provenance, dict):
        raise SteamJpMsguiError("JP overlay provenance must be an object")
    require_exact_keys(provenance, {"relative_path", "sha256", "entry_count"}, "JP overlay provenance")
    if provenance != {
        "relative_path": "data/public/msgui_ko_0000_5099.v0.2.json",
        "sha256": SOURCE_OVERLAY_SHA256,
        "entry_count": SOURCE_OVERLAY_ENTRY_COUNT,
    }:
        raise SteamJpMsguiError("JP overlay provenance differs")
    policy = value["mapping_policy"]
    if not isinstance(policy, dict):
        raise SteamJpMsguiError("JP overlay mapping policy must be an object")
    require_exact_keys(
        policy,
        {
            "coordinate",
            "source_guard",
            "format_guard",
            "requires_exact_format_profile",
            "sc_container_used",
            "legacy_candidate_binary_used",
        },
        "JP overlay mapping policy",
    )
    if (
        policy["format_guard"] != list(INVARIANT_KEYS)
        or policy["requires_exact_format_profile"] is not True
        or policy["sc_container_used"] is not False
        or policy["legacy_candidate_binary_used"] is not False
    ):
        raise SteamJpMsguiError("JP overlay mapping policy differs")
    entries = value["entries"]
    if not isinstance(entries, list):
        raise SteamJpMsguiError("JP overlay entries must be an array")
    if require_int(value["entry_count"], "JP overlay entry_count") != len(entries):
        raise SteamJpMsguiError("JP overlay entry_count differs")
    no_op_count = require_int(value["no_op_count"], "JP overlay no_op_count")
    effective_count = require_int(value["effective_change_count"], "JP overlay effective count")
    if effective_count + no_op_count != len(entries):
        raise SteamJpMsguiError("JP overlay effective/no-op counts differ")
    require_int(value["rejected_entry_count"], "JP overlay rejected count")
    ids: list[int] = []
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(entries):
        if not isinstance(item, dict):
            raise SteamJpMsguiError(f"JP overlay entry {index} must be an object")
        require_exact_keys(item, {"id", "source_jp_utf16le_sha256", "ko"}, f"JP overlay entry {index}")
        entry_id = require_int(item["id"], f"JP overlay entry {index}.id")
        if entry_id >= STOCK_STRING_COUNT:
            raise SteamJpMsguiError(f"JP overlay id {entry_id} is outside stock")
        source_hash = require_hash(
            item["source_jp_utf16le_sha256"], f"JP overlay entry {index}.source hash"
        )
        ko = item["ko"]
        if (
            not isinstance(ko, str)
            or "\0" in ko
            or "\ufffd" in ko
            or not has_semantic_text(ko)
            or has_cjk_or_kana(ko)
        ):
            raise SteamJpMsguiError(f"JP overlay id {entry_id} has unsafe Korean text")
        ids.append(entry_id)
        normalized.append(
            {"id": entry_id, "source_jp_utf16le_sha256": source_hash, "ko": ko}
        )
    if ids != sorted(set(ids)):
        raise SteamJpMsguiError("JP overlay IDs must be sorted and unique")
    return normalized


def candidate_from_entries(
    packed: bytes,
    raw: bytes,
    table: MessageTable,
    entries: Sequence[dict[str, Any]],
) -> tuple[bytes, bytes, list[int]]:
    texts = list(table.texts)
    changed_ids: list[int] = []
    for entry in entries:
        entry_id = int(entry["id"])
        source = texts[entry_id]
        if text_hash(source) != entry["source_jp_utf16le_sha256"]:
            raise SteamJpMsguiError(f"JP source hash mismatch at id {entry_id}")
        mismatches = mismatch_keys(source, str(entry["ko"]))
        if mismatches:
            raise SteamJpMsguiError(
                f"JP format profile mismatch at id {entry_id}: {mismatches!r}"
            )
        if source != entry["ko"]:
            changed_ids.append(entry_id)
        texts[entry_id] = str(entry["ko"])

    rebuilt_raw_a = rebuild_message_table(table, texts)
    rebuilt_raw_b = rebuild_message_table(table, texts)
    if rebuilt_raw_a != rebuilt_raw_b:
        raise SteamJpMsguiError("raw candidate A/B differs")
    candidate_a = recompress_wrapper(rebuilt_raw_a, packed)
    candidate_b = recompress_wrapper(rebuilt_raw_b, packed)
    if candidate_a != candidate_b:
        raise SteamJpMsguiError("packed candidate A/B differs")
    _header, check_raw = decompress_wrapper(candidate_a)
    if check_raw != rebuilt_raw_a:
        raise SteamJpMsguiError("candidate wrapper decompression differs")
    check_table = parse_message_table(check_raw)
    if check_table.texts != tuple(texts):
        raise SteamJpMsguiError("candidate table texts differ")
    if rebuild_message_table(check_table, check_table.texts) != check_raw:
        raise SteamJpMsguiError("candidate unchanged parse/rebuild differs")

    selected = {int(entry["id"]): str(entry["ko"]) for entry in entries}
    for entry_id, source in enumerate(table.texts):
        expected = selected.get(entry_id, source)
        if check_table.texts[entry_id] != expected:
            raise SteamJpMsguiError(f"candidate record mismatch at id {entry_id}")
        if entry_id not in selected:
            source_payload = source.encode("utf-16le") + b"\0\0"
            target_payload = check_table.texts[entry_id].encode("utf-16le") + b"\0\0"
            if source_payload != target_payload:
                raise SteamJpMsguiError(f"nonselected UTF-16LE bytes differ at id {entry_id}")

    if (
        check_table.string_count != table.string_count
        or check_table.block_offset != table.block_offset
        or check_table.table_offset != table.table_offset
        or check_table.table_size != table.table_size
        or check_table.string_start != table.string_start
    ):
        raise SteamJpMsguiError("candidate table structure differs")

    # The logical-size u32 at offset 8 is expected to change.  Every other
    # opaque byte before the offset table must remain stock-exact.
    stock_prefix = bytearray(raw[: table.table_offset])
    target_prefix = bytearray(check_raw[: check_table.table_offset])
    struct.pack_into("<I", stock_prefix, 8, 0)
    struct.pack_into("<I", target_prefix, 8, 0)
    if stock_prefix != target_prefix:
        raise SteamJpMsguiError("opaque raw prefix differs outside logical-size field")
    return candidate_a, rebuilt_raw_a, changed_ids


def make_contract(
    overlay_blob: bytes,
    audit_blob: bytes,
    overlay: Mapping[str, Any],
    candidate: bytes,
    candidate_raw: bytes,
) -> dict[str, Any]:
    return {
        "schema": CONTRACT_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "resource": RESOURCE,
        "runtime_route": {
            "language": "JP",
            "game_root_default": str(DEFAULT_GAME_ROOT).replace("\\", "/"),
            "installed_game_file_modified_by_builder": False,
            "sc_container_used": False,
            "legacy_candidate_binary_used": False,
        },
        "stock_jp": stock_spec(),
        "overlay": {
            "relative_path": "workstreams/steam_jp_msgui_v1/public/msgui_ko_pk_jp_steam_native_v1.json",
            "sha256": sha256_bytes(overlay_blob),
            "entry_count": int(overlay["entry_count"]),
            "effective_change_count": int(overlay["effective_change_count"]),
            "unmapped_entry_count": int(overlay["rejected_entry_count"]),
        },
        "remap_audit": {
            "relative_path": "workstreams/steam_jp_msgui_v1/remap_audit.v1.json",
            "sha256": sha256_bytes(audit_blob),
        },
        "expected_candidate": {
            "packed_size": len(candidate),
            "packed_sha256": sha256_bytes(candidate),
            "raw_size": len(candidate_raw),
            "raw_sha256": sha256_bytes(candidate_raw),
            "string_count": STOCK_STRING_COUNT,
        },
        "output_policy": {
            "complete_candidate_private_only": True,
            "allowed_root": "tmp",
            "relative_path": RESOURCE,
        },
        "required_proofs": {
            "packed_and_raw_stock_pinned": True,
            "per_entry_jp_source_hash_pinned": True,
            "exact_jp_format_profile_required": True,
            "record_count_and_order_preserved": True,
            "nonselected_strings_and_utf16le_payloads_preserved": True,
            "opaque_prefix_preserved_except_logical_size": True,
            "packed_build_reproducible_ab": True,
            "installed_stock_rechecked_after_build": True,
        },
    }


def validate_contract(value: Any, contract_path: Path) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SteamJpMsguiError("source-free contract root must be an object")
    require_exact_keys(
        value,
        {
            "schema",
            "source_free",
            "contains_commercial_source_text",
            "contains_complete_game_resource",
            "resource",
            "runtime_route",
            "stock_jp",
            "overlay",
            "remap_audit",
            "expected_candidate",
            "output_policy",
            "required_proofs",
        },
        "source-free contract",
    )
    if (
        value["schema"] != CONTRACT_SCHEMA
        or value["source_free"] is not True
        or value["contains_commercial_source_text"] is not False
        or value["contains_complete_game_resource"] is not False
        or value["resource"] != RESOURCE
    ):
        raise SteamJpMsguiError("source-free contract header differs")
    validate_stock_spec(value["stock_jp"], "contract stock_jp")
    route = value["runtime_route"]
    if not isinstance(route, dict):
        raise SteamJpMsguiError("contract runtime_route must be an object")
    require_exact_keys(
        route,
        {
            "language",
            "game_root_default",
            "installed_game_file_modified_by_builder",
            "sc_container_used",
            "legacy_candidate_binary_used",
        },
        "contract runtime_route",
    )
    if (
        route["language"] != "JP"
        or route["installed_game_file_modified_by_builder"] is not False
        or route["sc_container_used"] is not False
        or route["legacy_candidate_binary_used"] is not False
    ):
        raise SteamJpMsguiError("contract runtime route is unsafe")
    output_policy = value["output_policy"]
    if output_policy != {
        "complete_candidate_private_only": True,
        "allowed_root": "tmp",
        "relative_path": RESOURCE,
    }:
        raise SteamJpMsguiError("contract output policy differs")
    proofs = value["required_proofs"]
    if not isinstance(proofs, dict) or not proofs or any(flag is not True for flag in proofs.values()):
        raise SteamJpMsguiError("contract required proofs are incomplete")
    overlay = value["overlay"]
    if not isinstance(overlay, dict):
        raise SteamJpMsguiError("contract overlay must be an object")
    require_exact_keys(
        overlay,
        {"relative_path", "sha256", "entry_count", "effective_change_count", "unmapped_entry_count"},
        "contract overlay",
    )
    require_hash(overlay["sha256"], "contract overlay hash")
    for key in ("entry_count", "effective_change_count", "unmapped_entry_count"):
        require_int(overlay[key], f"contract overlay {key}")
    audit = value["remap_audit"]
    if not isinstance(audit, dict):
        raise SteamJpMsguiError("contract remap_audit must be an object")
    require_exact_keys(audit, {"relative_path", "sha256"}, "contract remap_audit")
    require_hash(audit["sha256"], "contract remap_audit hash")
    expected = value["expected_candidate"]
    if not isinstance(expected, dict):
        raise SteamJpMsguiError("contract expected_candidate must be an object")
    require_exact_keys(
        expected,
        {"packed_size", "packed_sha256", "raw_size", "raw_sha256", "string_count"},
        "contract expected_candidate",
    )
    require_hash(expected["packed_sha256"], "expected candidate packed hash")
    require_hash(expected["raw_sha256"], "expected candidate raw hash")
    for key in ("packed_size", "raw_size", "string_count"):
        require_int(expected[key], f"expected candidate {key}", minimum=1)
    if contract_path.resolve() != DEFAULT_CONTRACT.resolve():
        # Alternate contract paths are supported for tamper tests, but every
        # referenced public artifact remains rooted in this repository.
        pass
    return value


def path_from_repo(relative: Any, label: str) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise SteamJpMsguiError(f"{label} must be a forward-slash relative path")
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise SteamJpMsguiError(f"{label} escapes the repository")
    resolved = (REPO_ROOT / path).resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise SteamJpMsguiError(f"{label} escapes the repository") from exc
    return resolved


def require_private_output_root(output_root: Path) -> Path:
    resolved = output_root.resolve()
    private_root = (REPO_ROOT / "tmp").resolve()
    try:
        relative = resolved.relative_to(private_root)
    except ValueError as exc:
        raise SteamJpMsguiError("complete candidate output must stay below KR_PATCH_WORK/tmp") from exc
    if not relative.parts:
        raise SteamJpMsguiError("output root must be a child directory below KR_PATCH_WORK/tmp")
    return resolved


def load_frozen_inputs(contract_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], bytes]:
    contract_value, _contract_blob = read_json(contract_path)
    contract = validate_contract(contract_value, contract_path)
    overlay_path = path_from_repo(contract["overlay"]["relative_path"], "contract overlay path")
    overlay_value, overlay_blob = read_json(overlay_path)
    if sha256_bytes(overlay_blob) != contract["overlay"]["sha256"]:
        raise SteamJpMsguiError("frozen JP overlay hash differs from contract")
    entries = validate_public_overlay(overlay_value)
    if (
        len(entries) != contract["overlay"]["entry_count"]
        or overlay_value["effective_change_count"] != contract["overlay"]["effective_change_count"]
        or overlay_value["rejected_entry_count"] != contract["overlay"]["unmapped_entry_count"]
    ):
        raise SteamJpMsguiError("frozen JP overlay counts differ from contract")
    audit_path = path_from_repo(contract["remap_audit"]["relative_path"], "contract audit path")
    if sha256_file(audit_path) != contract["remap_audit"]["sha256"]:
        raise SteamJpMsguiError("remap audit hash differs from contract")
    return contract, entries, overlay_blob


def freeze_contract(game_root: Path, output_root: Path) -> dict[str, Any]:
    _source_path, packed, raw, table = load_stock(game_root)
    source_entries, source_blob = load_source_overlay(DEFAULT_SOURCE_OVERLAY)
    accepted, rejected = remap_entries(source_entries, table)
    overlay = make_public_overlay(accepted, len(rejected), source_blob, table)
    audit = make_audit(accepted, rejected, source_blob)
    overlay_blob = pretty_bytes(overlay)
    audit_blob = pretty_bytes(audit)
    candidate, candidate_raw, _changed = candidate_from_entries(
        packed, raw, table, accepted
    )
    contract = make_contract(overlay_blob, audit_blob, overlay, candidate, candidate_raw)
    atomic_write(DEFAULT_PUBLIC_OVERLAY, overlay_blob)
    atomic_write(DEFAULT_AUDIT, audit_blob)
    atomic_write(DEFAULT_CONTRACT, pretty_bytes(contract))
    result = build_candidate(game_root, DEFAULT_CONTRACT, output_root)
    return {
        **result,
        "mapped_entry_count": len(accepted),
        "unmapped_entry_count": len(rejected),
        "overlay_sha256": sha256_bytes(overlay_blob),
        "audit_sha256": sha256_bytes(audit_blob),
    }


def build_candidate(game_root: Path, contract_path: Path, output_root: Path) -> dict[str, Any]:
    output_root = require_private_output_root(output_root)
    contract, entries, overlay_blob = load_frozen_inputs(contract_path)
    source_path, packed, raw, table = load_stock(game_root)
    source_hash_before = sha256_bytes(packed)
    candidate, candidate_raw, changed_ids = candidate_from_entries(
        packed, raw, table, entries
    )
    expected = contract["expected_candidate"]
    observed = {
        "packed_size": len(candidate),
        "packed_sha256": sha256_bytes(candidate),
        "raw_size": len(candidate_raw),
        "raw_sha256": sha256_bytes(candidate_raw),
        "string_count": STOCK_STRING_COUNT,
    }
    if observed != expected:
        raise SteamJpMsguiError(
            f"candidate differs from frozen reproducibility pin: expected={expected!r}, "
            f"observed={observed!r}"
        )

    target_path = (output_root / Path(RESOURCE)).resolve()
    if target_path == source_path:
        raise SteamJpMsguiError("refusing to overwrite installed Steam stock")
    try:
        target_path.relative_to(output_root)
    except ValueError as exc:
        raise SteamJpMsguiError("candidate target escapes output root") from exc
    atomic_write(target_path, candidate)
    if target_path.read_bytes() != candidate:
        raise SteamJpMsguiError("written candidate bytes differ")

    source_after = source_path.read_bytes()
    if sha256_bytes(source_after) != source_hash_before or source_after != packed:
        raise SteamJpMsguiError("installed Steam stock changed during build")

    all_ids = {int(entry["id"]) for entry in entries}
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "resource": RESOURCE,
        "stock_jp": stock_spec(),
        "overlay": {
            "sha256": sha256_bytes(overlay_blob),
            "entry_count": len(entries),
            "coordinate_sha256": coordinate_hash(all_ids),
        },
        "target": observed,
        "effective_change_count": len(changed_ids),
        "effective_change_coordinate_sha256": coordinate_hash(changed_ids),
        "no_op_count": len(entries) - len(changed_ids),
        "unmapped_entry_count": contract["overlay"]["unmapped_entry_count"],
        "output": {
            "relative_path": RESOURCE,
            "complete_candidate_private_only": True,
            "installed_game_file_modified": False,
        },
        "verification": {
            "packed_and_raw_stock_pins": "OK",
            "per_entry_jp_source_hashes": "OK",
            "exact_jp_format_profiles": "OK",
            "record_count_and_order": "OK",
            "nonselected_strings_and_utf16le_payloads": "OK",
            "opaque_prefix_except_logical_size": "OK",
            "raw_build_ab_reproducibility": "OK",
            "packed_build_ab_reproducibility": "OK",
            "packed_decompression_roundtrip": "OK",
            "installed_stock_unchanged": "OK",
            "sc_container_used": False,
            "legacy_candidate_binary_used": False,
        },
    }
    manifest_path = output_root / "build_manifest.v1.json"
    atomic_write(manifest_path, pretty_bytes(manifest))
    return {
        "candidate_path": str(target_path),
        "manifest_path": str(manifest_path),
        "candidate_sha256": observed["packed_sha256"],
        "candidate_raw_sha256": observed["raw_sha256"],
        "mapped_entry_count": len(entries),
        "effective_change_count": len(changed_ids),
        "unmapped_entry_count": contract["overlay"]["unmapped_entry_count"],
        "installed_game_file_modified": False,
    }


def print_result(result: Mapping[str, Any]) -> None:
    for key, value in result.items():
        print(f"{key}={value}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    freeze = subparsers.add_parser(
        "freeze", help="re-audit the pinned Korean overlay and freeze the JP contract"
    )
    freeze.add_argument("--game-root", type=Path, default=DEFAULT_GAME_ROOT)
    freeze.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT / "freeze")

    build = subparsers.add_parser(
        "build", help="build a private candidate solely from the frozen JP overlay"
    )
    build.add_argument("--game-root", type=Path, default=DEFAULT_GAME_ROOT)
    build.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    build.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT / "candidate")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "freeze":
            result = freeze_contract(args.game_root, args.output_root)
        else:
            result = build_candidate(args.game_root, args.contract, args.output_root)
        print_result(result)
        return 0
    except (
        OSError,
        KeyError,
        TypeError,
        json.JSONDecodeError,
        LZ4Error,
        MessageTableError,
        SteamJpMsguiError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
