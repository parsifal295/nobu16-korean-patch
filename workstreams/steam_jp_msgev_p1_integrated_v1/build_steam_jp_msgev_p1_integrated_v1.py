#!/usr/bin/env python3
"""Integrate P1-01 and P1-02 source-free overlays on the active Steam JP v6 baseline.

This builder never chains one candidate onto another.  It reads the currently
active JP ``msgev`` once, proves both source-free overlays target that exact
baseline, validates every source hash and format profile against that shared
preimage, then rebuilds one private staging resource with their disjoint
replacements.  It cannot write a Steam installation, release, or GitHub file.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
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
sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import MessageTable, parse_message_table, rebuild_message_table  # noqa: E402


RESOURCE = "MSG_PK/JP/msgev.bin"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / "steam_jp_msgev_p1_integrated_v1" / "candidate"
P1_01_OVERLAY = (
    REPO / "workstreams" / "msgev_pk_base_ev_reuse_p1_v1" / "public" / "msgev_ko_pk_base_ev_reuse_p1_185.v1.json"
)
P1_02_OVERLAY = (
    REPO / "workstreams" / "steam_jp_msgev_p1_residual_02_v1" / "public" / "msgev_ko_steam_jp_p1_residual_02_185.v1.json"
)
PUBLIC_OVERLAY = WORKSTREAM / "public" / "msgev_ko_steam_jp_p1_integrated_370.v1.json"
VALIDATION = WORKSTREAM / "validation.v1.json"
CONTRACT = WORKSTREAM / "source_free_contract.v1.json"

SCHEMA = "nobu16.kr.steam-jp-msgev-p1-integrated-overlay.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-msgev-p1-integrated-validation.v1"
CONTRACT_SCHEMA = "nobu16.kr.steam-jp-msgev-p1-integrated-contract.v1"
MANIFEST_SCHEMA = "nobu16.kr.steam-jp-msgev-p1-integrated-build-manifest.v1"

STOCK = {
    "packed_size": 1_040_799,
    "packed_sha256": "A8835C3520B29A076A21014E17B17D7AAABF4AC99D37D65C891415AC17BBF3F5",
    "raw_size": 1_036_708,
    "raw_sha256": "6D87086EA6B533EAB3F3745DB7564E8D7842E7DD603AD765B2D6D900644E00FB",
    "string_count": 17_916,
}
INPUT_PINS = {
    "p1_01": {
        "path": "workstreams/msgev_pk_base_ev_reuse_p1_v1/public/msgev_ko_pk_base_ev_reuse_p1_185.v1.json",
        "size": 85_359,
        "sha256": "B4BCA472C5B553F4BEC11CF44A9D498F7F950A918B7F7FA3951B7778798A169D",
        "entry_count": 185,
    },
    "p1_02": {
        "path": "workstreams/steam_jp_msgev_p1_residual_02_v1/public/msgev_ko_steam_jp_p1_residual_02_185.v1.json",
        "size": 142_419,
        "sha256": "BBBCB3F55D7D109B11A98195355F25D7233270158F40BE1FD2B14C9B9D162200",
        "entry_count": 185,
    },
}
EXPECTED_PER_OVERLAY = 185
EXPECTED_TOTAL = 370

HEX64_RE = re.compile(r"[0-9A-F]{64}\Z")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
CJK_OR_KANA_RE = re.compile(r"[\u3040-\u30ff\uff66-\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
PRINTF_RE = re.compile(r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
LINE_BREAK_RE = re.compile(r"\r\n|\n|\r")
INVARIANT_KEYS = ("printf", "unknown_percent_count", "leading_whitespace", "trailing_whitespace", "esc", "controls", "line_breaks", "pua")


class IntegratedP1Error(ValueError):
    pass


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def text_hash(text: str) -> str:
    return sha256_bytes(text.encode("utf-16le"))


def canonical_hash(value: object) -> str:
    return sha256_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def require_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise IntegratedP1Error(f"{label} differs from its exact contract")


def strict_object(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    folded: dict[str, str] = {}
    for key, value in pairs:
        if key.casefold() in folded:
            raise IntegratedP1Error("duplicate/case-colliding JSON key")
        folded[key.casefold()] = key
        result[key] = value
    return result


def read_json(path: Path) -> tuple[dict[str, Any], bytes]:
    blob = path.read_bytes()
    try:
        value = json.loads(blob.decode("utf-8-sig"), object_pairs_hook=strict_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IntegratedP1Error(f"invalid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise IntegratedP1Error("JSON root must be an object")
    return value, blob


def file_spec(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise IntegratedP1Error(f"required input is missing: {path}")
    blob = path.read_bytes()
    return {"size": len(blob), "sha256": sha256_bytes(blob)}


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


def message_invariants(text: str) -> dict[str, Any]:
    printf_matches = list(PRINTF_RE.finditer(text))
    printf_offsets = {index for match in printf_matches for index in range(match.start(), match.end()) if text[index] == "%"}
    esc_matches = list(ESC_RE.finditer(text))
    esc_offsets = {index for match in esc_matches for index in range(match.start(), match.end())}
    return {
        "printf": [match.group(0) for match in printf_matches],
        "unknown_percent_count": sum(1 for index, char in enumerate(text) if char == "%" and index not in printf_offsets),
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
    }


def mismatch_keys(source: str, replacement: str) -> list[str]:
    before = message_invariants(source)
    after = message_invariants(replacement)
    return [key for key in INVARIANT_KEYS if before[key] != after[key]]


def load_stock(steam_root: Path) -> tuple[Path, bytes, bytes, MessageTable]:
    source = (steam_root.resolve() / Path(RESOURCE)).resolve()
    if not source.is_file():
        raise IntegratedP1Error("active Steam JP source is missing")
    packed = source.read_bytes()
    require_equal({"packed_size": len(packed), "packed_sha256": sha256_bytes(packed)}, {"packed_size": STOCK["packed_size"], "packed_sha256": STOCK["packed_sha256"]}, "active v6 packed baseline")
    _header, raw = decompress_wrapper(packed)
    require_equal({"raw_size": len(raw), "raw_sha256": sha256_bytes(raw)}, {"raw_size": STOCK["raw_size"], "raw_sha256": STOCK["raw_sha256"]}, "active v6 raw baseline")
    table = parse_message_table(raw)
    require_equal(table.string_count, STOCK["string_count"], "active v6 string count")
    if rebuild_message_table(table, table.texts) != raw:
        raise IntegratedP1Error("active v6 table cannot round-trip byte-identically")
    return source, packed, raw, table


def _validate_korean(source: str, korean: Any, entry_id: int) -> str:
    if not isinstance(korean, str) or not korean or "\0" in korean or "\ufffd" in korean:
        raise IntegratedP1Error(f"unsafe Korean replacement at {entry_id}")
    if CJK_OR_KANA_RE.search(korean) or not HANGUL_RE.search(korean):
        raise IntegratedP1Error(f"non-Korean script remains at {entry_id}")
    mismatches = mismatch_keys(source, korean)
    if mismatches:
        raise IntegratedP1Error(f"format/token mismatch at {entry_id}: {mismatches!r}")
    return korean


def load_input_overlay(label: str, path: Path, table: MessageTable) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    pin = INPUT_PINS[label]
    require_equal(file_spec(path), {"size": pin["size"], "sha256": pin["sha256"]}, f"{label} overlay pin")
    overlay, _blob = read_json(path)
    if overlay.get("resource") != RESOURCE or not isinstance(overlay.get("entries"), list):
        raise IntegratedP1Error(f"{label} overlay route/schema differs")
    if label == "p1_01":
        baseline = overlay.get("baseline")
        candidate = baseline.get("candidate") if isinstance(baseline, dict) else None
        if not isinstance(candidate, dict) or candidate.get("packed_sha256") != STOCK["packed_sha256"] or candidate.get("raw_sha256") != STOCK["raw_sha256"] or candidate.get("string_count") != STOCK["string_count"]:
            raise IntegratedP1Error("p1_01 baseline differs from active v6")
        selection = overlay.get("selection")
        if not isinstance(selection, dict) or selection.get("bundle_id") != "p1-MSG_PK_JP_msgev-01" or selection.get("entry_count") != EXPECTED_PER_OVERLAY:
            raise IntegratedP1Error("p1_01 selection differs")
        digest_field = "ids_sha256"
        origin_key = "origin"
    else:
        if overlay.get("active_v6_baseline") != STOCK:
            raise IntegratedP1Error("p1_02 baseline differs from active v6")
        audit = overlay.get("audit_bundle")
        if not isinstance(audit, dict) or audit.get("bundle_id") != "p1-MSG_PK_JP_msgev-02" or audit.get("coordinate_count") != EXPECTED_PER_OVERLAY:
            raise IntegratedP1Error("p1_02 audit selection differs")
        digest_field = "coordinate_sha256"
        origin_key = "provenance"
    rows: list[dict[str, Any]] = []
    ids: list[int] = []
    for index, entry in enumerate(overlay["entries"]):
        if not isinstance(entry, dict):
            raise IntegratedP1Error(f"{label} entry {index} is invalid")
        entry_id = entry.get("id")
        source_hash = entry.get("source_jp_utf16le_sha256")
        korean = entry.get("ko")
        if isinstance(entry_id, bool) or not isinstance(entry_id, int) or not 0 <= entry_id < table.string_count:
            raise IntegratedP1Error(f"{label} entry ID is invalid")
        if not isinstance(source_hash, str) or not HEX64_RE.fullmatch(source_hash):
            raise IntegratedP1Error(f"{label} source hash is invalid")
        source = table.texts[entry_id]
        require_equal(text_hash(source), source_hash, f"{label} source hash at {entry_id}")
        korean = _validate_korean(source, korean, entry_id)
        supplied_hash = entry.get("ko_utf16le_sha256")
        if supplied_hash is not None:
            require_equal(supplied_hash, text_hash(korean), f"{label} Korean hash at {entry_id}")
        format_hash = canonical_hash(message_invariants(source))
        supplied_format = entry.get("format_signature_sha256")
        if supplied_format is not None:
            require_equal(supplied_format, format_hash, f"{label} format hash at {entry_id}")
        origin = entry.get(origin_key)
        if label == "p1_01":
            if origin not in {"base_ev_exact_source_hash", "project_authored_manual"}:
                raise IntegratedP1Error(f"p1_01 origin differs at {entry_id}")
        elif not isinstance(origin, Mapping) or origin.get("kind") not in {"base_ev_strdata_exact_source_hash_reuse", "project_authored_manual_korean"}:
            raise IntegratedP1Error(f"p1_02 provenance differs at {entry_id}")
        rows.append({
            "id": entry_id,
            "source_jp_utf16le_sha256": source_hash,
            "ko": korean,
            "ko_utf16le_sha256": text_hash(korean),
            "format_signature_sha256": format_hash,
            "input_overlay": label,
        })
        ids.append(entry_id)
    if ids != sorted(set(ids)) or len(ids) != EXPECTED_PER_OVERLAY:
        raise IntegratedP1Error(f"{label} coordinate vector differs")
    digest = canonical_hash([{ "id": entry_id } for entry_id in ids])
    if label == "p1_01":
        require_equal(overlay["selection"].get(digest_field), digest, "p1_01 coordinate digest")
    else:
        require_equal(overlay.get(digest_field), digest, "p1_02 coordinate digest")
    return rows, {"path": pin["path"], "size": pin["size"], "sha256": pin["sha256"], "entry_count": len(rows), "coordinate_sha256": digest}


def resolve_entries(table: MessageTable) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    first, first_meta = load_input_overlay("p1_01", P1_01_OVERLAY, table)
    second, second_meta = load_input_overlay("p1_02", P1_02_OVERLAY, table)
    first_ids = {entry["id"] for entry in first}
    second_ids = {entry["id"] for entry in second}
    if first_ids & second_ids:
        raise IntegratedP1Error("P1-01/P1-02 coordinate overlap")
    entries = sorted((*first, *second), key=lambda entry: int(entry["id"]))
    if len(entries) != EXPECTED_TOTAL or len({entry["id"] for entry in entries}) != EXPECTED_TOTAL:
        raise IntegratedP1Error("integrated coordinate count differs")
    return entries, [first_meta, second_meta]


def validate_entries(table: MessageTable, entries: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    required = {"id", "source_jp_utf16le_sha256", "ko", "ko_utf16le_sha256", "format_signature_sha256", "input_overlay"}
    if len(entries) != EXPECTED_TOTAL:
        raise IntegratedP1Error("integrated entry count differs")
    normalized: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, Mapping) or set(entry) != required:
            raise IntegratedP1Error("integrated entry schema differs")
        entry_id = entry["id"]
        if isinstance(entry_id, bool) or not isinstance(entry_id, int) or not 0 <= entry_id < table.string_count:
            raise IntegratedP1Error("integrated entry ID is invalid")
        source = table.texts[entry_id]
        require_equal(text_hash(source), entry["source_jp_utf16le_sha256"], f"integrated source hash {entry_id}")
        korean = _validate_korean(source, entry["ko"], entry_id)
        require_equal(text_hash(korean), entry["ko_utf16le_sha256"], f"integrated Korean hash {entry_id}")
        require_equal(canonical_hash(message_invariants(source)), entry["format_signature_sha256"], f"integrated format hash {entry_id}")
        if entry["input_overlay"] not in INPUT_PINS:
            raise IntegratedP1Error("integrated input overlay label differs")
        normalized.append(dict(entry))
    if [entry["id"] for entry in normalized] != sorted({entry["id"] for entry in normalized}):
        raise IntegratedP1Error("integrated coordinate order differs")
    expected, _inputs = resolve_entries(table)
    require_equal(normalized, expected, "integrated exact overlay resolution")
    return normalized


def make_overlay(entries: Sequence[Mapping[str, Any]], inputs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "overlay_id": "msgev_ko_steam_jp_p1_integrated_370.v1",
        "resource": RESOURCE,
        "base_language": "JP",
        "distribution_policy": {"contains_commercial_source_text": False, "contains_complete_game_resource": False, "sc_container_used": False},
        "active_v6_baseline": dict(STOCK),
        "input_overlays": [dict(value) for value in inputs],
        "entry_count": len(entries),
        "coordinate_sha256": canonical_hash([{ "id": entry["id"] } for entry in entries]),
        "entries": [dict(entry) for entry in entries],
    }


def validate_public_overlay(overlay: Mapping[str, Any], table: MessageTable) -> list[dict[str, Any]]:
    required = {"schema", "overlay_id", "resource", "base_language", "distribution_policy", "active_v6_baseline", "input_overlays", "entry_count", "coordinate_sha256", "entries"}
    if set(overlay) != required or overlay.get("schema") != SCHEMA or overlay.get("overlay_id") != "msgev_ko_steam_jp_p1_integrated_370.v1":
        raise IntegratedP1Error("public integration overlay schema differs")
    if overlay.get("resource") != RESOURCE or overlay.get("base_language") != "JP" or overlay.get("active_v6_baseline") != STOCK:
        raise IntegratedP1Error("public integration route/baseline differs")
    if overlay.get("distribution_policy") != {"contains_commercial_source_text": False, "contains_complete_game_resource": False, "sc_container_used": False}:
        raise IntegratedP1Error("public integration distribution policy differs")
    expected, inputs = resolve_entries(table)
    require_equal(overlay.get("input_overlays"), inputs, "public integration input pins")
    raw_entries = overlay.get("entries")
    if not isinstance(raw_entries, list) or overlay.get("entry_count") != len(raw_entries):
        raise IntegratedP1Error("public integration entries differ")
    entries = validate_entries(table, raw_entries)
    require_equal(overlay.get("coordinate_sha256"), canonical_hash([{ "id": entry["id"] } for entry in entries]), "public integration coordinate digest")
    require_equal(entries, expected, "public integration exact entries")
    return entries


def candidate_from_entries(packed: bytes, raw: bytes, table: MessageTable, entries: Sequence[Mapping[str, Any]]) -> tuple[bytes, bytes, list[int]]:
    selected = validate_entries(table, entries)
    selected_ids = {int(entry["id"]) for entry in selected}
    texts = list(table.texts)
    for entry in selected:
        texts[int(entry["id"])] = str(entry["ko"])
    changed = [entry_id for entry_id in sorted(selected_ids) if table.texts[entry_id] != texts[entry_id]]
    require_equal(len(changed), EXPECTED_TOTAL, "effective integrated change count")
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
        raise IntegratedP1Error("candidate table cannot round-trip")
    for entry_id, source in enumerate(table.texts):
        if checked.texts[entry_id] != texts[entry_id]:
            raise IntegratedP1Error(f"candidate text differs at {entry_id}")
        if entry_id not in selected_ids and source.encode("utf-16le") + b"\0\0" != checked.texts[entry_id].encode("utf-16le") + b"\0\0":
            raise IntegratedP1Error(f"nonselected UTF-16LE payload differs at {entry_id}")
    if (checked.string_count, checked.block_offset, checked.table_offset, checked.table_size, checked.string_start) != (table.string_count, table.block_offset, table.table_offset, table.table_size, table.string_start):
        raise IntegratedP1Error("candidate table structure differs")
    before_prefix = bytearray(raw[: table.table_offset])
    after_prefix = bytearray(checked_raw[: checked.table_offset])
    struct.pack_into("<I", before_prefix, 8, 0)
    struct.pack_into("<I", after_prefix, 8, 0)
    require_equal(before_prefix, after_prefix, "opaque prefix except logical size")
    return packed_a, raw_a, changed


def make_validation(entries: Sequence[Mapping[str, Any]], candidate: bytes, candidate_raw: bytes, changed: Sequence[int]) -> dict[str, Any]:
    counts = {label: sum(entry["input_overlay"] == label for entry in entries) for label in INPUT_PINS}
    return {
        "schema": VALIDATION_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "resource": RESOURCE,
        "active_v6_baseline": dict(STOCK),
        "entry_count": len(entries),
        "coordinate_sha256": canonical_hash([{ "id": entry["id"] } for entry in entries]),
        "input_entry_counts": counts,
        "expected_candidate": {"packed_size": len(candidate), "packed_sha256": sha256_bytes(candidate), "raw_size": len(candidate_raw), "raw_sha256": sha256_bytes(candidate_raw), "string_count": STOCK["string_count"]},
        "effective_change_count": len(changed),
        "effective_change_coordinate_sha256": canonical_hash([{ "id": entry_id } for entry_id in changed]),
        "checks": {
            "shared_active_v6_baseline": True,
            "p1_01_entries": EXPECTED_PER_OVERLAY,
            "p1_02_entries": EXPECTED_PER_OVERLAY,
            "coordinate_overlap": False,
            "combined_changes": EXPECTED_TOTAL,
            "per_entry_source_hash_gated": True,
            "format_and_token_profile_preserved": True,
            "nonselected_utf16le_payloads_preserved": True,
            "parser_roundtrip_valid": True,
            "deterministic_raw_and_packed_rebuild": True,
            "steam_installation_written": False,
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
        "overlay": {"relative_path": "workstreams/steam_jp_msgev_p1_integrated_v1/public/msgev_ko_steam_jp_p1_integrated_370.v1.json", "sha256": sha256_bytes(overlay_blob), "entry_count": EXPECTED_TOTAL},
        "validation": {"relative_path": "workstreams/steam_jp_msgev_p1_integrated_v1/validation.v1.json", "sha256": sha256_bytes(validation_blob)},
        "expected_candidate": dict(validation["expected_candidate"]),
        "output_policy": {"complete_candidate_private_only": True, "allowed_root": "tmp", "relative_path": RESOURCE},
        "proofs": {"shared_active_v6_baseline": True, "input_overlay_pins": True, "coordinate_disjoint": True, "per_entry_source_hash_gated": True, "format_and_token_profile_preserved": True, "nonselected_utf16le_payloads_preserved": True, "deterministic_raw_and_packed_rebuild": True, "steam_installation_read_only": True},
    }


def assert_source_free(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if CJK_OR_KANA_RE.search(text) or "MSG_PK/SC" in text or "RES_SC" in text or "source_sc" in text.casefold():
        raise IntegratedP1Error(f"artifact is not JP-route source-free: {path}")


def private_output_root(value: Path) -> Path:
    output = value.resolve()
    root = (REPO / "tmp").resolve()
    try:
        output.relative_to(root)
    except ValueError as exc:
        raise IntegratedP1Error("private output must stay under KR_PATCH_WORK/tmp") from exc
    if output == root:
        raise IntegratedP1Error("tmp root cannot itself be an output")
    return output


def path_from_repo(relative: str) -> Path:
    path = Path(relative)
    if not relative or path.is_absolute() or ".." in path.parts or "\\" in relative:
        raise IntegratedP1Error("unsafe repository-relative path")
    result = (REPO / path).resolve()
    try:
        result.relative_to(REPO.resolve())
    except ValueError as exc:
        raise IntegratedP1Error("repository-relative path escaped workspace") from exc
    return result


def freeze(steam_root: Path) -> dict[str, Any]:
    _source, packed, raw, table = load_stock(steam_root)
    entries, inputs = resolve_entries(table)
    entries = validate_entries(table, entries)
    candidate, candidate_raw, changed = candidate_from_entries(packed, raw, table, entries)
    overlay_blob = canonical_bytes(make_overlay(entries, inputs))
    validation = make_validation(entries, candidate, candidate_raw, changed)
    validation_blob = canonical_bytes(validation)
    contract = make_contract(overlay_blob, validation_blob, validation)
    atomic_write(PUBLIC_OVERLAY, overlay_blob)
    atomic_write(VALIDATION, validation_blob)
    atomic_write(CONTRACT, canonical_bytes(contract))
    for path in (PUBLIC_OVERLAY, VALIDATION, CONTRACT):
        assert_source_free(path)
    return {"entry_count": len(entries), "candidate_sha256": sha256_bytes(candidate), "installed_game_file_modified": False}


def load_frozen(steam_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], bytes, bytes, MessageTable]:
    source, packed, raw, table = load_stock(steam_root)
    contract, _contract_blob = read_json(CONTRACT)
    required = {"schema", "source_free", "contains_commercial_source_text", "contains_complete_game_resource", "resource", "runtime_route", "active_v6_baseline", "overlay", "validation", "expected_candidate", "output_policy", "proofs"}
    if set(contract) != required or contract.get("schema") != CONTRACT_SCHEMA or contract.get("resource") != RESOURCE:
        raise IntegratedP1Error("frozen contract schema differs")
    if contract.get("runtime_route") != {"language": "JP", "sc_container_used": False, "installed_game_file_written": False} or contract.get("active_v6_baseline") != STOCK:
        raise IntegratedP1Error("frozen contract route/baseline differs")
    if contract.get("output_policy") != {"complete_candidate_private_only": True, "allowed_root": "tmp", "relative_path": RESOURCE}:
        raise IntegratedP1Error("frozen contract output policy differs")
    if not isinstance(contract.get("proofs"), dict) or any(value is not True for value in contract["proofs"].values()):
        raise IntegratedP1Error("frozen contract proof differs")
    overlay_path = path_from_repo(str(contract["overlay"].get("relative_path", "")))
    overlay, overlay_blob = read_json(overlay_path)
    require_equal(sha256_bytes(overlay_blob), contract["overlay"].get("sha256"), "frozen integration overlay hash")
    entries = validate_public_overlay(overlay, table)
    validation_path = path_from_repo(str(contract["validation"].get("relative_path", "")))
    validation_blob = validation_path.read_bytes()
    require_equal(sha256_bytes(validation_blob), contract["validation"].get("sha256"), "frozen integration validation hash")
    for path in (overlay_path, validation_path, CONTRACT):
        assert_source_free(path)
    if source != (steam_root.resolve() / Path(RESOURCE)).resolve():
        raise IntegratedP1Error("unexpected active source path")
    return contract, entries, packed, raw, table


def build(steam_root: Path, output_root: Path) -> dict[str, Any]:
    output = private_output_root(output_root)
    source, before, _raw, _table = load_stock(steam_root)
    contract, entries, packed, raw, table = load_frozen(steam_root)
    require_equal(packed, before, "active source while loading frozen contract")
    candidate, candidate_raw, changed = candidate_from_entries(packed, raw, table, entries)
    observed = {"packed_size": len(candidate), "packed_sha256": sha256_bytes(candidate), "raw_size": len(candidate_raw), "raw_sha256": sha256_bytes(candidate_raw), "string_count": table.string_count}
    require_equal(observed, contract["expected_candidate"], "candidate versus frozen contract")
    target = (output / Path(RESOURCE)).resolve()
    try:
        target.relative_to(output)
    except ValueError as exc:
        raise IntegratedP1Error("candidate target escaped output root") from exc
    if target == source:
        raise IntegratedP1Error("refusing to target the Steam installation")
    atomic_write(target, candidate)
    require_equal(target.read_bytes(), candidate, "written private candidate")
    require_equal(source.read_bytes(), before, "Steam source after private build")
    manifest = {"schema": MANIFEST_SCHEMA, "source_free": True, "contains_commercial_source_text": False, "contains_complete_game_resource": False, "resource": RESOURCE, "active_v6_baseline": dict(STOCK), "target": observed, "entry_count": len(entries), "effective_change_count": len(changed), "output": {"relative_path": RESOURCE, "complete_candidate_private_only": True, "installed_game_file_modified": False}, "checks": {"input_overlays": "OK", "source_hash_gates": "OK", "token_profiles": "OK", "nonselected": "OK", "steam_source_unchanged": "OK"}}
    atomic_write(output / "build_manifest.v1.json", canonical_bytes(manifest))
    return {"candidate_path": str(target), "manifest_path": str(output / "build_manifest.v1.json"), **observed, "installed_game_file_modified": False}


def verify(steam_root: Path) -> dict[str, Any]:
    contract, entries, packed, raw, table = load_frozen(steam_root)
    first, first_raw, changed = candidate_from_entries(packed, raw, table, entries)
    second, second_raw, changed_second = candidate_from_entries(packed, raw, table, entries)
    require_equal(first, second, "deterministic candidate A/B")
    require_equal(first_raw, second_raw, "deterministic raw A/B")
    require_equal(changed, changed_second, "deterministic changed IDs A/B")
    observed = {"packed_size": len(first), "packed_sha256": sha256_bytes(first), "raw_size": len(first_raw), "raw_sha256": sha256_bytes(first_raw), "string_count": table.string_count}
    require_equal(observed, contract["expected_candidate"], "verified candidate versus frozen contract")
    return {"status": "PASS", "entry_count": len(entries), "effective_change_count": len(changed), "candidate_sha256": sha256_bytes(first), "output_written": False}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    for name in ("freeze", "verify", "build"):
        child = commands.add_parser(name)
        child.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
        if name == "build":
            child.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "freeze":
            result = freeze(args.steam_root)
        elif args.command == "build":
            result = build(args.steam_root, args.output_root)
        else:
            result = verify(args.steam_root)
    except (IntegratedP1Error, OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
