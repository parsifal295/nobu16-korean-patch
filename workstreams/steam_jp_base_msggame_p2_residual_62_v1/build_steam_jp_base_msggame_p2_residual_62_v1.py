#!/usr/bin/env python3
"""Build a private Steam-JP base ``msggame.bin`` P2 residual candidate.

The P2 set consists of 62 active JP literals: two Korean bullet forms and
three exact-source-hash Korean dialogue reuses.  The Steam installation is an
input only; complete resources may be written only below ``KR_PATCH_WORK/tmp``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import runpy
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = WORKSTREAM_ROOT.parents[1]
TOOLS_ROOT = REPO_ROOT / "tools"
MSGGAME_ROOT = REPO_ROOT / "workstreams" / "msggame"
sys.path[:0] = [str(TOOLS_ROOT), str(MSGGAME_ROOT), str(WORKSTREAM_ROOT)]

import build_common_message_overlay as common  # noqa: E402
import msggame_format as msggame  # noqa: E402
from nobu16_lz4 import decompress_wrapper, recompress_wrapper_greedy  # noqa: E402
EXPECTED_REUSE_BY_SOURCE_HASH = runpy.run_path(
    str(WORKSTREAM_ROOT / "translations.py")
)["EXPECTED_REUSE_BY_SOURCE_HASH"]


RESOURCE = "MSG/JP/msggame.bin"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "tmp" / "steam_jp_base_msggame_p2_residual_62_v1" / "candidate"
PUBLIC_OVERLAY = WORKSTREAM_ROOT / "public" / "msggame_ko_base_jp_p2_residual_62.v1.json"
VALIDATION = WORKSTREAM_ROOT / "validation.v1.json"
CONTRACT = WORKSTREAM_ROOT / "source_free_contract.v1.json"

STOCK = {
    "packed_size": 649347,
    "packed_sha256": "E54D7AB55CB981B7973FBF8657A276520EBFA881D3439BE94A2D14086B293177",
    "raw_size": 1498276,
    "raw_sha256": "183F7867817FBDAAE8E8B1DE547AEAC9B80C6A818604DD26FBF57BABD2FC10E2",
    "block_count": 18,
    "record_count": 19152,
    "literal_count": 24262,
}
BUNDLE_COORDINATE_SHA256 = "A882DC7B496535932DBB7C27C8191B66454B14F09F84BBF31BFDB39697F185F4"
AUDIT_BUNDLE = {"bundle_id": "p2-MSG_JP-msggame-residual-62", "coordinate_sha256": BUNDLE_COORDINATE_SHA256}

REUSE_CATALOGS = (
    {
        "relative_path": "workstreams/msggame_pk_jp_native_wave06/public/msggame_ko_pk_jp_native_steam_prior_rebased_9386.v1.json",
        "sha256": "9F2E8498E45899E55D8AF8221434DBB35D1D2660C96F43E678C0A065D059D974",
    },
    {
        "relative_path": "workstreams/msggame_pk_jp_native_wave06/public/msggame_ko_pk_jp_native_steam_switch_v13_exact_14825.v1.json",
        "sha256": "40C2DCCCDBA0F0FCFD99063531C116F82006E7DFE078F67F930F5EBEDB328045",
    },
    {
        "relative_path": "workstreams/msggame_pk_jp_native_wave07_j04/public/msggame_ko_pk_jp_native_wave07_j04_680.v1.json",
        "sha256": "DDC3B34DB5A1B6428D028435DF65C67ECA7E5698F94C2912D03DAF18EB4524DC",
    },
)

OVERLAY_SCHEMA = "nobu16.kr.steam-jp-base-msggame-p2-residual-overlay.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-base-msggame-p2-residual-validation.v1"
CONTRACT_SCHEMA = "nobu16.kr.steam-jp-base-msggame-p2-residual-contract.v1"
MANIFEST_SCHEMA = "nobu16.kr.steam-jp-base-msggame-p2-residual-build-manifest.v1"

HEX64_RE = re.compile(r"[0-9A-F]{64}\Z")
KANA_RE = re.compile(r"[\u3040-\u30ff\uff66-\uff9f]")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
CJK_OR_KANA_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uf900-\ufaff]")
ENTRY_FIELDS = {
    "block_id", "record_id", "literal_id", "source_jp_utf16le_sha256", "ko", "ko_utf16le_sha256",
    "format_signature_sha256", "translation_origin",
}


class P2Error(ValueError):
    """Raised for an invalid stock source, reuse, format, or output contract."""


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
            raise P2Error(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def read_json(path: Path) -> tuple[dict[str, Any], bytes]:
    blob = path.read_bytes()
    try:
        value = json.loads(blob.decode("utf-8"), object_pairs_hook=strict_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise P2Error(f"invalid JSON: {path}") from error
    if not isinstance(value, dict):
        raise P2Error(f"JSON root must be an object: {path}")
    return value, blob


def path_from_repo(relative: str) -> Path:
    path = Path(relative)
    if not relative or path.is_absolute() or ".." in path.parts or "\\" in relative:
        raise P2Error("unsafe repository-relative path")
    resolved = (REPO_ROOT / path).resolve()
    if not resolved.is_relative_to(REPO_ROOT.resolve()):
        raise P2Error("repository-relative path escapes workspace")
    return resolved


def coordinate_key(block_id: int, record_id: int, literal_id: int) -> tuple[int, int, int]:
    return (block_id, record_id, literal_id)


def coordinate_hash(coordinates: Iterable[tuple[int, int, int]]) -> str:
    return sha256_bytes("".join(f"{block}:{record}:{literal}\n" for block, record, literal in sorted(coordinates)).encode("ascii"))


def is_high_confidence_japanese(text: str) -> bool:
    return bool(KANA_RE.search(text)) and not bool(HANGUL_RE.search(text))


def assert_source_free_path(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if CJK_OR_KANA_RE.search(text) or "MSG_PK/SC" in text or "RES_SC" in text or "source_sc" in text.casefold():
        raise P2Error(f"source-free artifact contains source script or wrong route: {path}")


def literal_map(archive: msggame.MsgGameArchive) -> dict[tuple[int, int, int], Any]:
    return {coordinate_key(item.block_id, item.record_id, item.literal_id): item for item in msggame.iter_literals(archive)}


def normalized_structure_raw(archive: msggame.MsgGameArchive) -> bytes:
    empty_literals = {coordinate_key(item.block_id, item.record_id, item.literal_id): "" for item in msggame.iter_literals(archive)}
    return msggame.rebuild_raw_with_literals(archive, empty_literals)


def stock_context(steam_root: Path) -> dict[str, Any]:
    root = steam_root.resolve()
    source_path = (root / Path(RESOURCE)).resolve()
    if not source_path.is_relative_to(root) or not source_path.is_file():
        raise P2Error(f"active JP resource does not exist: {source_path}")
    packed = source_path.read_bytes()
    if len(packed) != STOCK["packed_size"] or sha256_bytes(packed) != STOCK["packed_sha256"]:
        raise P2Error("active Steam JP base msggame packed baseline differs")
    header, raw = decompress_wrapper(packed)
    if len(raw) != STOCK["raw_size"] or sha256_bytes(raw) != STOCK["raw_sha256"]:
        raise P2Error("active Steam JP base msggame raw baseline differs")
    parsed = msggame.parse_packed_msggame(packed)
    literals = literal_map(parsed.archive)
    if (
        len(parsed.archive.blocks) != STOCK["block_count"]
        or parsed.archive.record_count != STOCK["record_count"]
        or len(literals) != STOCK["literal_count"]
        or msggame.rebuild_raw_msggame(parsed.archive) != raw
    ):
        raise P2Error("active Steam JP base msggame structure differs")
    selected = sorted(
        (coordinate for coordinate, literal in literals.items() if is_high_confidence_japanese(literal.text)),
    )
    if len(selected) != 62 or coordinate_hash(selected) != BUNDLE_COORDINATE_SHA256:
        raise P2Error("P2 coordinate contract differs from active JP base msggame")
    source_hashes = {text_hash(literals[coordinate].text) for coordinate in selected}
    if source_hashes != set(EXPECTED_REUSE_BY_SOURCE_HASH):
        raise P2Error("P2 active JP source-hash partition differs")
    return {
        "source_path": source_path,
        "packed": packed,
        "header": header,
        "raw": raw,
        "parsed": parsed,
        "literals": literals,
        "selected": selected,
        "normalized_structure_sha256": sha256_bytes(normalized_structure_raw(parsed.archive)),
    }


def exact_reuse_values() -> dict[str, str]:
    found: dict[str, set[str]] = defaultdict(set)
    for catalog_pin in REUSE_CATALOGS:
        path = path_from_repo(str(catalog_pin["relative_path"]))
        value, blob = read_json(path)
        if sha256_bytes(blob) != catalog_pin["sha256"]:
            raise P2Error(f"pinned reuse catalogue differs: {catalog_pin['relative_path']}")
        assert_source_free_path(path)
        def walk(node: Any) -> None:
            if isinstance(node, dict):
                source_hash = node.get("source_jp_utf16le_sha256")
                ko = node.get("ko")
                if isinstance(source_hash, str) and isinstance(ko, str) and source_hash.upper() in EXPECTED_REUSE_BY_SOURCE_HASH:
                    found[source_hash.upper()].add(ko)
                for child in node.values():
                    walk(child)
            elif isinstance(node, list):
                for child in node:
                    walk(child)
        walk(value)
    for source_hash, expected in EXPECTED_REUSE_BY_SOURCE_HASH.items():
        if found.get(source_hash, set()) != {expected}:
            raise P2Error(f"exact source-hash reuse differs for source {source_hash}")
    return dict(EXPECTED_REUSE_BY_SOURCE_HASH)


def validate_replacement(source: str, ko: str, coordinate: tuple[int, int, int]) -> None:
    if not isinstance(ko, str) or not ko or "\0" in ko or "\ufffd" in ko:
        raise P2Error(f"unsafe Korean replacement at {coordinate}")
    if CJK_OR_KANA_RE.search(ko):
        raise P2Error(f"Korean replacement retains CJK/kana at {coordinate}")
    mismatch = common.invariant_mismatches(source, ko)
    if mismatch:
        raise P2Error(f"ESC/printf/newline/PUA/whitespace mismatch at {coordinate}: {mismatch!r}")


def build_entries(stock: Mapping[str, Any]) -> list[dict[str, Any]]:
    reuse = exact_reuse_values()
    literals = stock["literals"]
    entries: list[dict[str, Any]] = []
    for coordinate in stock["selected"]:
        source = literals[coordinate].text
        source_hash = text_hash(source)
        ko = reuse[source_hash]
        validate_replacement(source, ko, coordinate)
        entries.append({
            "block_id": coordinate[0], "record_id": coordinate[1], "literal_id": coordinate[2],
            "source_jp_utf16le_sha256": source_hash, "ko": ko, "ko_utf16le_sha256": text_hash(ko),
            "format_signature_sha256": canonical_hash(common.message_invariants(source)),
            "translation_origin": "exact_source_hash_catalog_reuse",
        })
    return entries


def validate_entries(stock: Mapping[str, Any], entries: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes)) or len(entries) != 62:
        raise P2Error("P2 entry count differs")
    expected_coords = list(stock["selected"])
    expected_reuse = exact_reuse_values()
    normalized: list[dict[str, Any]] = []
    for coordinate, entry in zip(expected_coords, entries, strict=True):
        if not isinstance(entry, Mapping) or set(entry) != ENTRY_FIELDS:
            raise P2Error("P2 entry schema differs")
        if coordinate_key(entry.get("block_id"), entry.get("record_id"), entry.get("literal_id")) != coordinate:
            raise P2Error("P2 entry coordinate/order differs")
        source = stock["literals"][coordinate].text
        source_hash = text_hash(source)
        ko = entry.get("ko")
        if entry.get("source_jp_utf16le_sha256") != source_hash or not HEX64_RE.fullmatch(source_hash):
            raise P2Error(f"P2 source hash differs at {coordinate}")
        if not isinstance(ko, str) or entry.get("ko_utf16le_sha256") != text_hash(ko):
            raise P2Error(f"P2 Korean hash differs at {coordinate}")
        if entry.get("format_signature_sha256") != canonical_hash(common.message_invariants(source)):
            raise P2Error(f"P2 format signature differs at {coordinate}")
        if entry.get("translation_origin") != "exact_source_hash_catalog_reuse" or ko != expected_reuse[source_hash]:
            raise P2Error(f"P2 exact reuse differs at {coordinate}")
        validate_replacement(source, ko, coordinate)
        normalized.append(dict(entry))
    return normalized


def reuse_catalog_header() -> list[dict[str, str]]:
    return [dict(item) for item in REUSE_CATALOGS]


def make_overlay(entries: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": "msggame_ko_base_jp_p2_residual_62.v1",
        "resource": RESOURCE,
        "base_language": "JP",
        "distribution_policy": {"contains_commercial_source_text": False, "contains_complete_game_resource": False, "sc_container_used": False},
        "active_v6_baseline": dict(STOCK),
        "audit_bundle": dict(AUDIT_BUNDLE),
        "exact_reuse_catalogs": reuse_catalog_header(),
        "entry_count": len(entries),
        "translation_origin_counts": dict(sorted(Counter(entry["translation_origin"] for entry in entries).items())),
        "entries": list(entries),
    }


def validate_public_overlay(value: Mapping[str, Any], stock: Mapping[str, Any]) -> list[dict[str, Any]]:
    required = {
        "schema", "overlay_id", "resource", "base_language", "distribution_policy", "active_v6_baseline", "audit_bundle",
        "exact_reuse_catalogs", "entry_count", "translation_origin_counts", "entries",
    }
    if set(value) != required or value.get("schema") != OVERLAY_SCHEMA or value.get("overlay_id") != "msggame_ko_base_jp_p2_residual_62.v1":
        raise P2Error("P2 public overlay header differs")
    if value.get("resource") != RESOURCE or value.get("base_language") != "JP" or value.get("active_v6_baseline") != STOCK:
        raise P2Error("P2 public overlay route/baseline differs")
    if value.get("distribution_policy") != {"contains_commercial_source_text": False, "contains_complete_game_resource": False, "sc_container_used": False}:
        raise P2Error("P2 public overlay policy differs")
    if value.get("audit_bundle") != AUDIT_BUNDLE or value.get("exact_reuse_catalogs") != reuse_catalog_header():
        raise P2Error("P2 public overlay provenance differs")
    entries_value = value.get("entries")
    if not isinstance(entries_value, list) or value.get("entry_count") != len(entries_value):
        raise P2Error("P2 public overlay entry count differs")
    entries = validate_entries(stock, entries_value)
    if value.get("translation_origin_counts") != {"exact_source_hash_catalog_reuse": 62}:
        raise P2Error("P2 public overlay origin counts differ")
    return entries


def candidate_from_entries(stock: Mapping[str, Any], entries: Sequence[Mapping[str, Any]]) -> tuple[bytes, bytes, list[tuple[int, int, int]], int]:
    normalized = validate_entries(stock, entries)
    replacements = {coordinate_key(entry["block_id"], entry["record_id"], entry["literal_id"]): entry["ko"] for entry in normalized}
    rebuilt_raw_a = msggame.rebuild_raw_with_literals(stock["parsed"].archive, replacements)
    rebuilt_raw_b = msggame.rebuild_raw_with_literals(stock["parsed"].archive, replacements)
    if rebuilt_raw_a != rebuilt_raw_b:
        raise P2Error("raw candidate is not deterministic")
    candidate_a = recompress_wrapper_greedy(rebuilt_raw_a, stock["header"])
    candidate_b = recompress_wrapper_greedy(rebuilt_raw_b, stock["header"])
    if candidate_a != candidate_b:
        raise P2Error("packed candidate is not deterministic")
    header, candidate_raw = decompress_wrapper(candidate_a)
    parsed = msggame.parse_packed_msggame(candidate_a)
    literals = literal_map(parsed.archive)
    if candidate_raw != rebuilt_raw_a or header.prefix != stock["header"].prefix or set(literals) != set(stock["literals"]):
        raise P2Error("candidate wrapper or literal coordinate set differs")
    if len(parsed.archive.blocks) != STOCK["block_count"] or parsed.archive.record_count != STOCK["record_count"]:
        raise P2Error("candidate block or record count differs")
    if [len(block.records) for block in parsed.archive.blocks] != [len(block.records) for block in stock["parsed"].archive.blocks]:
        raise P2Error("candidate per-block record counts differ")
    if msggame.rebuild_raw_msggame(parsed.archive) != candidate_raw:
        raise P2Error("candidate raw parser/rebuild differs")
    if sha256_bytes(normalized_structure_raw(parsed.archive)) != stock["normalized_structure_sha256"]:
        raise P2Error("candidate nonliteral structure differs")
    for coordinate, source_literal in stock["literals"].items():
        expected = replacements.get(coordinate, source_literal.text)
        if literals[coordinate].text != expected:
            raise P2Error(f"candidate literal differs at {coordinate}")
        if coordinate not in replacements and literals[coordinate].text.encode("utf-16le") + b"\0\0" != source_literal.text.encode("utf-16le") + b"\0\0":
            raise P2Error(f"nonselected UTF-16LE payload differs at {coordinate}")
    if any(is_high_confidence_japanese(literals[coordinate].text) for coordinate in stock["selected"]):
        raise P2Error("candidate retains active Japanese residual in selected P2 set")
    after_total = sum(is_high_confidence_japanese(item.text) for item in literals.values())
    if after_total != 0:
        raise P2Error(f"candidate retains unexpected high-confidence Japanese literals: {after_total}")
    return candidate_a, candidate_raw, sorted(replacements), after_total


def make_validation(entries: Sequence[Mapping[str, Any]], candidate: bytes, candidate_raw: bytes, changed: Sequence[tuple[int, int, int]], residual_after: int) -> dict[str, Any]:
    return {
        "schema": VALIDATION_SCHEMA,
        "source_free": True,
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "resource": RESOURCE,
        "active_v6_baseline": dict(STOCK),
        "audit_bundle": dict(AUDIT_BUNDLE),
        "entry_count": len(entries),
        "translation_origin_counts": {"exact_source_hash_catalog_reuse": len(entries)},
        "expected_candidate": {"packed_size": len(candidate), "packed_sha256": sha256_bytes(candidate), "raw_size": len(candidate_raw), "raw_sha256": sha256_bytes(candidate_raw)},
        "effective_change_count": len(changed),
        "effective_change_coordinate_sha256": coordinate_hash(changed),
        "high_confidence_kana_residual_count_after_candidate": residual_after,
        "checks": {
            "active_v6_baseline": "OK", "exact_source_hash_catalog_reuse": "OK", "per_entry_jp_source_hashes": "OK",
            "esc_printf_newline_pua_whitespace": "OK", "raw_parser_roundtrip": "OK", "packed_deterministic_rebuild": "OK",
            "literal_coordinate_set_preserved": "OK", "nonliteral_structure_preserved": "OK", "nonselected_utf16le_payloads": "OK",
            "selected_high_confidence_kana_residuals": "0", "steam_installation_written": False,
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
        "audit_bundle": dict(AUDIT_BUNDLE),
        "exact_reuse_catalogs": reuse_catalog_header(),
        "overlay": {"relative_path": "workstreams/steam_jp_base_msggame_p2_residual_62_v1/public/msggame_ko_base_jp_p2_residual_62.v1.json", "sha256": sha256_bytes(overlay_blob), "entry_count": len(entries)},
        "validation": {"relative_path": "workstreams/steam_jp_base_msggame_p2_residual_62_v1/validation.v1.json", "sha256": sha256_bytes(validation_blob)},
        "expected_candidate": {"packed_size": len(candidate), "packed_sha256": sha256_bytes(candidate), "raw_size": len(candidate_raw), "raw_sha256": sha256_bytes(candidate_raw), "literal_count": STOCK["literal_count"]},
        "output_policy": {"complete_candidate_private_only": True, "allowed_root": "tmp", "relative_path": RESOURCE},
        "proofs": {
            "active_v6_baseline_pinned": True, "catalog_reuse_exact_source_hash_only": True,
            "per_entry_jp_source_hash_gated": True, "esc_printf_newline_pua_whitespace_preserved": True,
            "literal_coordinate_set_preserved": True, "nonliteral_structure_preserved": True,
            "nonselected_utf16le_payloads_preserved": True, "parser_roundtrip_valid": True,
            "deterministic_packed_rebuild": True, "steam_installation_read_only": True,
        },
    }


def require_private_output_root(output_root: Path) -> Path:
    resolved = output_root.resolve()
    private_root = (REPO_ROOT / "tmp").resolve()
    if not resolved.is_relative_to(private_root) or resolved == private_root:
        raise P2Error("complete candidate output must be a child below KR_PATCH_WORK/tmp")
    return resolved


def freeze(steam_root: Path) -> dict[str, Any]:
    stock = stock_context(steam_root)
    entries = build_entries(stock)
    candidate, candidate_raw, changed, residual_after = candidate_from_entries(stock, entries)
    overlay_blob = pretty_bytes(make_overlay(entries))
    validation_blob = pretty_bytes(make_validation(entries, candidate, candidate_raw, changed, residual_after))
    contract_blob = pretty_bytes(make_contract(overlay_blob, validation_blob, candidate, candidate_raw, entries))
    atomic_write(PUBLIC_OVERLAY, overlay_blob)
    atomic_write(VALIDATION, validation_blob)
    atomic_write(CONTRACT, contract_blob)
    for path in (PUBLIC_OVERLAY, VALIDATION, CONTRACT):
        assert_source_free_path(path)
    return {"entry_count": len(entries), "candidate_sha256": sha256_bytes(candidate), "candidate_raw_sha256": sha256_bytes(candidate_raw), "high_confidence_kana_residual_count_after_candidate": residual_after, "installed_game_file_modified": False}


def load_frozen_inputs(steam_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    stock = stock_context(steam_root)
    contract, _contract_blob = read_json(CONTRACT)
    required = {
        "schema", "source_free", "contains_commercial_source_text", "contains_complete_game_resource", "resource", "runtime_route",
        "active_v6_baseline", "audit_bundle", "exact_reuse_catalogs", "overlay", "validation", "expected_candidate", "output_policy", "proofs",
    }
    if set(contract) != required or contract.get("schema") != CONTRACT_SCHEMA or contract.get("resource") != RESOURCE:
        raise P2Error("frozen P2 contract header differs")
    if contract.get("active_v6_baseline") != STOCK or contract.get("audit_bundle") != AUDIT_BUNDLE or contract.get("exact_reuse_catalogs") != reuse_catalog_header():
        raise P2Error("frozen P2 contract provenance differs")
    if contract.get("runtime_route") != {"language": "JP", "sc_container_used": False, "installed_game_file_written": False}:
        raise P2Error("frozen P2 contract route differs")
    if contract.get("output_policy") != {"complete_candidate_private_only": True, "allowed_root": "tmp", "relative_path": RESOURCE}:
        raise P2Error("frozen P2 contract output policy differs")
    if not isinstance(contract.get("proofs"), dict) or any(value is not True for value in contract["proofs"].values()):
        raise P2Error("frozen P2 contract proofs are incomplete")
    overlay_locator = contract.get("overlay")
    validation_locator = contract.get("validation")
    if not isinstance(overlay_locator, dict) or not isinstance(validation_locator, dict):
        raise P2Error("frozen P2 artifact locator differs")
    overlay_path = path_from_repo(str(overlay_locator.get("relative_path", "")))
    overlay, overlay_blob = read_json(overlay_path)
    if sha256_bytes(overlay_blob) != overlay_locator.get("sha256"):
        raise P2Error("frozen P2 overlay hash differs")
    entries = validate_public_overlay(overlay, stock)
    validation_path = path_from_repo(str(validation_locator.get("relative_path", "")))
    validation_blob = validation_path.read_bytes()
    if sha256_bytes(validation_blob) != validation_locator.get("sha256"):
        raise P2Error("frozen P2 validation hash differs")
    for path in (overlay_path, validation_path, CONTRACT):
        assert_source_free_path(path)
    return contract, entries, stock


def build_staging_candidate(steam_root: Path, output_root: Path) -> dict[str, Any]:
    output_root = require_private_output_root(output_root)
    before_stock = stock_context(steam_root)
    contract, entries, stock = load_frozen_inputs(steam_root)
    if stock["packed"] != before_stock["packed"]:
        raise P2Error("active Steam JP source changed while loading frozen P2 inputs")
    candidate, candidate_raw, changed, residual_after = candidate_from_entries(stock, entries)
    observed = {"packed_size": len(candidate), "packed_sha256": sha256_bytes(candidate), "raw_size": len(candidate_raw), "raw_sha256": sha256_bytes(candidate_raw), "literal_count": len(stock["literals"])}
    if observed != contract.get("expected_candidate"):
        raise P2Error("P2 candidate differs from frozen contract")
    target_path = (output_root / Path(RESOURCE)).resolve()
    if target_path == stock["source_path"] or not target_path.is_relative_to(output_root):
        raise P2Error("refusing to target Steam installation or escape private output")
    atomic_write(target_path, candidate)
    if target_path.read_bytes() != candidate or stock["source_path"].read_bytes() != before_stock["packed"]:
        raise P2Error("P2 staging write changed unexpected bytes")
    manifest = {
        "schema": MANIFEST_SCHEMA, "source_free": True, "contains_commercial_source_text": False, "contains_complete_game_resource": False,
        "resource": RESOURCE, "active_v6_baseline": dict(STOCK), "audit_bundle": dict(AUDIT_BUNDLE), "target": observed,
        "entry_count": len(entries), "effective_change_count": len(changed), "effective_change_coordinate_sha256": coordinate_hash(changed),
        "high_confidence_kana_residual_count_after_candidate": residual_after,
        "output": {"relative_path": RESOURCE, "complete_candidate_private_only": True, "installed_game_file_modified": False},
        "checks": {"exact_catalog_reuse": "OK", "source_hashes": "OK", "format_invariants": "OK", "steam_source_unchanged": "OK"},
    }
    atomic_write(output_root / "build_manifest.v1.json", pretty_bytes(manifest))
    return {"candidate_path": str(target_path), "manifest_path": str(output_root / "build_manifest.v1.json"), **observed, "high_confidence_kana_residual_count_after_candidate": residual_after, "installed_game_file_modified": False}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    freeze_parser = commands.add_parser("freeze", help="freeze P2 source-free overlay and contract")
    freeze_parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    build_parser = commands.add_parser("build", help="build a P2 private staging candidate")
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
