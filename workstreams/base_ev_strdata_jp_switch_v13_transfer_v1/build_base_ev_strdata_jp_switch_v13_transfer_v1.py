#!/usr/bin/env python3
"""Build a source-free Steam JP base ``ev_strdata.bin`` transfer overlay.

The Korean text is read only from the pinned Switch v1.3 fan-patch archive.
Every selected row is gated against the exact Steam 1.1.7 Japanese source by
slot, UTF-16LE source hash, and the full message-control invariant vector.
No game resource is written by this module.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
import zipfile
from pathlib import Path
from typing import Any, Iterable, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = SCRIPT.parents[2]
TOOLS = REPO / "tools"
sys.path.insert(0, str(TOOLS))

from build_common_message_overlay import invariant_mismatches  # noqa: E402
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import (  # noqa: E402
    MessageTable,
    parse_message_table,
    rebuild_message_table,
)


RESOURCE = "MSG/JP/ev_strdata.bin"
STEAM_ROOT = Path(r"F:/SteamLibrary/steamapps/common/NOBU16")
SWITCH_ZIP = REPO / "tmp" / "third_party_switch_v13" / "NobunagaShinsei_KoreanPatch_v1.3.zip"
SWITCH_ENTRY = "NobunagaShinsei_KR/romfs/MSG/JP/ev_strdata.bin"
# Public v5-candidate-loader interface.  These aliases intentionally remain
# explicit so a composition layer can use this workstream without knowing its
# private helper names or paths.
DEFAULT_GAME_ROOT: Path = STEAM_ROOT
DEFAULT_SWITCH_ZIP: Path = SWITCH_ZIP

OVERLAY_SCHEMA = "nobu16.kr.base-ev-strdata-jp-switch-v13-transfer-overlay.v1"
RESIDUAL_SCHEMA = "nobu16.kr.base-ev-strdata-jp-switch-v13-residual.v1"
VALIDATION_SCHEMA = "nobu16.kr.base-ev-strdata-jp-switch-v13-transfer-validation.v1"
OVERLAY_ID = "base_ev_strdata_jp_switch_v13_transfer_13045"
OVERLAY_PATH = WORKSTREAM / "public" / "ev_strdata_ko_base_jp_switch_v13_transfer_13045.v1.json"
RESIDUAL_PATH = WORKSTREAM / "public" / "ev_strdata_base_jp_switch_v13_residual_source_script_45.v1.json"
VALIDATION_PATH = WORKSTREAM / "validation.v1.json"

STEAM_JP_PIN = {
    "packed_size": 496_819,
    "packed_sha256": "EADCD167EF9684C7F077694A1A7F68966E34FD2E2EEF9DEFB7817031C3D773EB",
    "raw_size": 789_260,
    "raw_sha256": "5FBD960A4870FA4850BD725C58E67BE3A7F191960737C36E4505151FE4B7C528",
    "string_count": 17_868,
}
SWITCH_V13_PIN = {
    "archive_size": 72_977_145,
    "archive_sha256": "F4D2563C1B32DB450165C8CCF61C6947DEA904233581036E179AFA1D6A918CC4",
    "entry_size": 396_257,
    "entry_sha256": "A5D70580790330EF845EC73FDB8D6ACC89EBAD8D026DFE1B1D873C50B43CAD5D",
    "entry_crc32": "018EAC29",
    "entry_compressed_size": 314_537,
    "raw_size": 925_000,
    "raw_sha256": "1B8F7197D48598994852317B19CA3B9EC113A3B07A3B22642FBD336C21C4F7C3",
    "string_count": 17_868,
}
TARGET_PIN = {
    "packed_size": 927_573,
    "packed_sha256": "AD1A442C3588E791DB442548C2B7878ABB4D53A686C591A94AB7F4FAB719A886",
    "raw_size": 923_924,
    "raw_sha256": "1B4255E3F3DADA24EA5D526AA5DCD2D1BC73E1284891EBBE9B4E891D6FFBA162",
    "string_count": 17_868,
}
# The generic Steam-JP candidate loader only requires the packed size/hash,
# while keeping the raw and structure pins here makes this module self-auditing.
EXPECTED_CANDIDATE: dict[str, Any] = dict(TARGET_PIN)
EXPECTED_SWITCH_HANGUL_CANDIDATES = 13_090
EXPECTED_SELECTED_COUNT = 13_045
EXPECTED_RESIDUAL_COUNT = 45
EXPECTED_SELECTED_IDS_SHA256 = "E7C8B1950B67FC4DDEC2053768A600CA1799C431BF74A48544013F2BF800B346"
EXPECTED_RESIDUAL_IDS_SHA256 = "436BA9C3BA0CE19A470E34571B01A2D36832F6B7EEFB9968DB86C8FD9A4DB675"

HANGUL_RE = re.compile(r"[\uAC00-\uD7A3]")
SOURCE_SCRIPT_RE = re.compile(r"[\u3040-\u30FF\u31F0-\u31FF\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")


class TransferError(ValueError):
    """A source, overlay, or deterministic-rebuild contract failed."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def text_hash(text: str) -> str:
    return sha256(text.encode("utf-16-le"))


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def require_source_script_free(value: Any, label: str) -> None:
    """Reject CJK/kana anywhere in a public artifact, not only row payloads."""
    serialized = json.dumps(value, ensure_ascii=False, sort_keys=True)
    if SOURCE_SCRIPT_RE.search(serialized):
        raise TransferError(f"{label} contains source-script text")


def strict_object(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    folded: set[str] = set()
    for key, value in pairs:
        normalized = key.casefold()
        if normalized in folded:
            raise TransferError(f"duplicate or case-colliding JSON key: {key!r}")
        folded.add(normalized)
        result[key] = value
    return result


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_object)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TransferError(f"cannot read strict JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise TransferError(f"JSON root must be an object: {path}")
    return value


def ids_sha256(ids: Iterable[int]) -> str:
    return sha256("".join(f"{entry_id}\n" for entry_id in ids).encode("ascii"))


def spec(blob: bytes) -> dict[str, Any]:
    return {"size": len(blob), "sha256": sha256(blob)}


def require_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise TransferError(f"{label} differs: {actual!r} != {expected!r}")


def load_steam_jp(steam_root: Path) -> tuple[bytes, Any, bytes, MessageTable]:
    path = steam_root / Path(RESOURCE)
    packed = path.read_bytes()
    require_equal(len(packed), STEAM_JP_PIN["packed_size"], "Steam JP packed size")
    require_equal(sha256(packed), STEAM_JP_PIN["packed_sha256"], "Steam JP packed SHA-256")
    wrapper, raw = decompress_wrapper(packed)
    require_equal(len(raw), STEAM_JP_PIN["raw_size"], "Steam JP raw size")
    require_equal(sha256(raw), STEAM_JP_PIN["raw_sha256"], "Steam JP raw SHA-256")
    table = parse_message_table(raw)
    require_equal(table.string_count, STEAM_JP_PIN["string_count"], "Steam JP string count")
    if rebuild_message_table(table, table.texts) != raw:
        raise TransferError("Steam JP ev_strdata parse/rebuild is not byte-identical")
    return packed, wrapper, raw, table


def load_switch_v13(switch_zip: Path) -> tuple[bytes, Any, bytes, MessageTable]:
    archive_blob = switch_zip.read_bytes()
    require_equal(len(archive_blob), SWITCH_V13_PIN["archive_size"], "Switch v1.3 ZIP size")
    require_equal(sha256(archive_blob), SWITCH_V13_PIN["archive_sha256"], "Switch v1.3 ZIP SHA-256")
    try:
        with zipfile.ZipFile(switch_zip) as archive:
            info = archive.getinfo(SWITCH_ENTRY)
            require_equal(info.file_size, SWITCH_V13_PIN["entry_size"], "Switch entry size")
            require_equal(info.compress_size, SWITCH_V13_PIN["entry_compressed_size"], "Switch entry compressed size")
            require_equal(f"{info.CRC:08X}", SWITCH_V13_PIN["entry_crc32"], "Switch entry CRC32")
            packed = archive.read(info)
    except (OSError, KeyError, zipfile.BadZipFile) as exc:
        raise TransferError(f"cannot read pinned Switch v1.3 entry: {exc}") from exc
    require_equal(sha256(packed), SWITCH_V13_PIN["entry_sha256"], "Switch entry SHA-256")
    wrapper, raw = decompress_wrapper(packed)
    require_equal(len(raw), SWITCH_V13_PIN["raw_size"], "Switch entry raw size")
    require_equal(sha256(raw), SWITCH_V13_PIN["raw_sha256"], "Switch entry raw SHA-256")
    table = parse_message_table(raw)
    require_equal(table.string_count, SWITCH_V13_PIN["string_count"], "Switch entry string count")
    if rebuild_message_table(table, table.texts) != raw:
        raise TransferError("Switch ev_strdata parse/rebuild is not byte-identical")
    return packed, wrapper, raw, table


def select_transfer_entries(
    steam_table: MessageTable, switch_table: MessageTable
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    require_equal(switch_table.string_count, steam_table.string_count, "Steam/Switch string count")
    selected: list[dict[str, Any]] = []
    residual: list[dict[str, Any]] = []
    hangul_candidates = 0
    for entry_id, (source_jp, switch_text) in enumerate(zip(steam_table.texts, switch_table.texts, strict=True)):
        if not HANGUL_RE.search(switch_text):
            continue
        hangul_candidates += 1
        source_hash = text_hash(source_jp)
        if SOURCE_SCRIPT_RE.search(switch_text):
            residual.append(
                {
                    "id": entry_id,
                    "source_jp_utf16le_sha256": source_hash,
                    "reason": "contains_source_script",
                }
            )
            continue
        if "\0" in switch_text:
            raise TransferError(f"Switch row {entry_id} has an embedded NUL")
        if not unicodedata.is_normalized("NFC", switch_text):
            raise TransferError(f"Switch row {entry_id} is not NFC")
        failures = invariant_mismatches(source_jp, switch_text)
        if failures:
            raise TransferError(f"Steam JP invariant mismatch at id {entry_id}: {failures}")
        selected.append(
            {
                "id": entry_id,
                "source_jp_utf16le_sha256": source_hash,
                "ko": switch_text,
            }
        )
    if hangul_candidates != EXPECTED_SWITCH_HANGUL_CANDIDATES:
        raise TransferError(f"Switch Hangul candidate count changed: {hangul_candidates}")
    if len(selected) != EXPECTED_SELECTED_COUNT or len(residual) != EXPECTED_RESIDUAL_COUNT:
        raise TransferError(f"Switch transfer partition changed: selected={len(selected)}, residual={len(residual)}")
    if ids_sha256(row["id"] for row in selected) != EXPECTED_SELECTED_IDS_SHA256:
        raise TransferError("selected ID vector changed")
    if ids_sha256(row["id"] for row in residual) != EXPECTED_RESIDUAL_IDS_SHA256:
        raise TransferError("residual ID vector changed")
    return selected, residual, hangul_candidates


def make_overlay(selected: Sequence[dict[str, Any]], hangul_candidates: int) -> dict[str, Any]:
    return {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": OVERLAY_ID,
        "resource": RESOURCE,
        "base_language": "JP",
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
            "contains_switch_binary": False,
        },
        "stock_jp": dict(STEAM_JP_PIN),
        "switch_v13": {
            "archive_relative_path": "tmp/third_party_switch_v13/NobunagaShinsei_KoreanPatch_v1.3.zip",
            "archive_sha256": SWITCH_V13_PIN["archive_sha256"],
            "entry_path": SWITCH_ENTRY,
            "entry_sha256": SWITCH_V13_PIN["entry_sha256"],
            "raw_sha256": SWITCH_V13_PIN["raw_sha256"],
            "string_count": SWITCH_V13_PIN["string_count"],
        },
        "selection": {
            "switch_hangul_candidate_count": hangul_candidates,
            "selected_count": len(selected),
            "excluded_source_script_count": EXPECTED_RESIDUAL_COUNT,
            "selected_ids_sha256": ids_sha256(row["id"] for row in selected),
            "excluded_ids_sha256": EXPECTED_RESIDUAL_IDS_SHA256,
        },
        "entry_count": len(selected),
        "entries": list(selected),
    }


def make_residual(residual: Sequence[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema": RESIDUAL_SCHEMA,
        "resource": RESOURCE,
        "base_language": "JP",
        "reason": "source_script_in_switch_text",
        "entry_count": len(residual),
        "ids_sha256": ids_sha256(row["id"] for row in residual),
        "entries": list(residual),
    }


def validate_public_artifacts(
    overlay: dict[str, Any], residual: dict[str, Any], steam_table: MessageTable
) -> dict[int, str]:
    require_source_script_free(overlay, "overlay")
    require_source_script_free(residual, "residual")
    expected_overlay_keys = {
        "schema", "overlay_id", "resource", "base_language", "distribution_policy",
        "stock_jp", "switch_v13", "selection", "entry_count", "entries",
    }
    if set(overlay) != expected_overlay_keys:
        raise TransferError("overlay root keys differ")
    require_equal(overlay["schema"], OVERLAY_SCHEMA, "overlay schema")
    require_equal(overlay["overlay_id"], OVERLAY_ID, "overlay ID")
    require_equal(overlay["resource"], RESOURCE, "overlay resource")
    require_equal(overlay["base_language"], "JP", "overlay base language")
    require_equal(overlay["stock_jp"], STEAM_JP_PIN, "overlay stock pin")
    policy = overlay["distribution_policy"]
    if policy != {
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
        "contains_switch_binary": False,
    }:
        raise TransferError("overlay distribution policy differs")
    switch = overlay["switch_v13"]
    if not isinstance(switch, dict) or switch.get("archive_sha256") != SWITCH_V13_PIN["archive_sha256"]:
        raise TransferError("overlay Switch archive pin differs")
    if switch.get("entry_path") != SWITCH_ENTRY or switch.get("entry_sha256") != SWITCH_V13_PIN["entry_sha256"]:
        raise TransferError("overlay Switch entry pin differs")
    if switch.get("raw_sha256") != SWITCH_V13_PIN["raw_sha256"] or switch.get("string_count") != SWITCH_V13_PIN["string_count"]:
        raise TransferError("overlay Switch raw pin differs")

    expected_residual_keys = {"schema", "resource", "base_language", "reason", "entry_count", "ids_sha256", "entries"}
    if set(residual) != expected_residual_keys:
        raise TransferError("residual root keys differ")
    require_equal(residual["schema"], RESIDUAL_SCHEMA, "residual schema")
    require_equal(residual["resource"], RESOURCE, "residual resource")
    require_equal(residual["base_language"], "JP", "residual base language")
    require_equal(residual["reason"], "source_script_in_switch_text", "residual reason")

    entries = overlay["entries"]
    residual_entries = residual["entries"]
    if not isinstance(entries, list) or not isinstance(residual_entries, list):
        raise TransferError("overlay/residual entries must be arrays")
    require_equal(overlay["entry_count"], len(entries), "overlay entry count")
    require_equal(residual["entry_count"], len(residual_entries), "residual entry count")
    require_equal(len(entries), EXPECTED_SELECTED_COUNT, "expected overlay entry count")
    require_equal(len(residual_entries), EXPECTED_RESIDUAL_COUNT, "expected residual entry count")
    entry_ids = [row.get("id") if isinstance(row, dict) else None for row in entries]
    residual_ids = [row.get("id") if isinstance(row, dict) else None for row in residual_entries]
    if entry_ids != sorted(set(entry_ids)) or residual_ids != sorted(set(residual_ids)):
        raise TransferError("overlay/residual IDs are not sorted and unique")
    if set(entry_ids) & set(residual_ids):
        raise TransferError("overlay and residual IDs overlap")
    require_equal(ids_sha256(entry_ids), EXPECTED_SELECTED_IDS_SHA256, "overlay ID SHA-256")
    require_equal(ids_sha256(residual_ids), EXPECTED_RESIDUAL_IDS_SHA256, "residual ID SHA-256")
    selection = overlay["selection"]
    expected_selection = {
        "switch_hangul_candidate_count": EXPECTED_SWITCH_HANGUL_CANDIDATES,
        "selected_count": EXPECTED_SELECTED_COUNT,
        "excluded_source_script_count": EXPECTED_RESIDUAL_COUNT,
        "selected_ids_sha256": EXPECTED_SELECTED_IDS_SHA256,
        "excluded_ids_sha256": EXPECTED_RESIDUAL_IDS_SHA256,
    }
    require_equal(selection, expected_selection, "overlay selection")
    require_equal(residual["ids_sha256"], EXPECTED_RESIDUAL_IDS_SHA256, "residual IDs SHA-256")

    replacements: dict[int, str] = {}
    for index, row in enumerate(entries):
        if not isinstance(row, dict) or set(row) != {"id", "source_jp_utf16le_sha256", "ko"}:
            raise TransferError(f"overlay entry {index} shape differs")
        entry_id = row["id"]
        korean = row["ko"]
        if type(entry_id) is not int or not 0 <= entry_id < steam_table.string_count:
            raise TransferError(f"overlay entry {index} has invalid id")
        if not isinstance(korean, str) or not HANGUL_RE.search(korean) or SOURCE_SCRIPT_RE.search(korean):
            raise TransferError(f"overlay entry {entry_id} is not source-script-free Korean")
        if "\0" in korean or not unicodedata.is_normalized("NFC", korean):
            raise TransferError(f"overlay entry {entry_id} has invalid Korean text")
        source = steam_table.texts[entry_id]
        require_equal(row["source_jp_utf16le_sha256"], text_hash(source), f"overlay source hash at {entry_id}")
        mismatches = invariant_mismatches(source, korean)
        if mismatches:
            raise TransferError(f"overlay invariant mismatch at {entry_id}: {mismatches}")
        replacements[entry_id] = korean
    for index, row in enumerate(residual_entries):
        if not isinstance(row, dict) or set(row) != {"id", "source_jp_utf16le_sha256", "reason"}:
            raise TransferError(f"residual entry {index} shape differs")
        entry_id = row["id"]
        if type(entry_id) is not int or not 0 <= entry_id < steam_table.string_count:
            raise TransferError(f"residual entry {index} has invalid id")
        require_equal(row["reason"], "contains_source_script", f"residual reason at {entry_id}")
        require_equal(row["source_jp_utf16le_sha256"], text_hash(steam_table.texts[entry_id]), f"residual source hash at {entry_id}")
    return replacements


def _build_blob_from_overlay(
    stock_packed: bytes, wrapper: Any, raw: bytes, table: MessageTable,
    overlay: dict[str, Any], residual: dict[str, Any],
) -> tuple[bytes, dict[str, Any]]:
    require_equal(spec(stock_packed), {"size": STEAM_JP_PIN["packed_size"], "sha256": STEAM_JP_PIN["packed_sha256"]}, "stock packed pin")
    require_equal(spec(raw), {"size": STEAM_JP_PIN["raw_size"], "sha256": STEAM_JP_PIN["raw_sha256"]}, "stock raw pin")
    replacements = validate_public_artifacts(overlay, residual, table)
    texts = list(table.texts)
    for entry_id, korean in replacements.items():
        texts[entry_id] = korean
    candidate_raw = rebuild_message_table(table, texts)
    candidate = recompress_wrapper(candidate_raw, wrapper)
    candidate_wrapper, roundtrip_raw = decompress_wrapper(candidate)
    if candidate_wrapper.prefix != wrapper.prefix or roundtrip_raw != candidate_raw:
        raise TransferError("candidate wrapper round trip differs")
    candidate_table = parse_message_table(candidate_raw)
    require_equal(candidate_table.string_count, table.string_count, "candidate string count")
    for entry_id, korean in replacements.items():
        require_equal(candidate_table.texts[entry_id], korean, f"candidate replacement at {entry_id}")
    observed_target = {
        "packed_size": len(candidate),
        "packed_sha256": sha256(candidate),
        "raw_size": len(candidate_raw),
        "raw_sha256": sha256(candidate_raw),
        "string_count": candidate_table.string_count,
    }
    require_equal(observed_target, TARGET_PIN, "candidate target pin")
    manifest = {
        "schema": VALIDATION_SCHEMA,
        "resource": RESOURCE,
        "runtime": {"distribution": "Steam", "base_language_route": "JP", "steam_pk_version": "1.1.7"},
        "stock_jp": dict(STEAM_JP_PIN),
        "switch_v13": {
            "archive_sha256": SWITCH_V13_PIN["archive_sha256"],
            "entry_path": SWITCH_ENTRY,
            "entry_sha256": SWITCH_V13_PIN["entry_sha256"],
            "raw_sha256": SWITCH_V13_PIN["raw_sha256"],
        },
        "selection": dict(overlay["selection"]),
        "candidate": TARGET_PIN | {"changed_entry_count": len(replacements)},
        "checks": {
            "steam_jp_stock_hash_gate": True,
            "switch_v13_archive_hash_gate": True,
            "switch_v13_entry_hash_gate": True,
            "steam_switch_slot_count_equal": True,
            "jp_source_hash_gate": True,
            "control_linebreak_placeholder_invariants": True,
            "source_script_entries_excluded": True,
            "overlay_source_free": True,
            "candidate_parse_roundtrip": True,
            "wrapper_prefix_preserved": True,
            "installed_game_file_written": False,
            "sc_container_used": False,
        },
    }
    return candidate, manifest


def _derive_models(
    game_root: Path, switch_zip: Path,
) -> tuple[bytes, Any, bytes, MessageTable, dict[str, Any], dict[str, Any]]:
    """Load pinned private inputs and derive their source-free public model."""
    stock, wrapper, raw, steam_table = load_steam_jp(game_root)
    _switch_packed, _switch_wrapper, _switch_raw, switch_table = load_switch_v13(switch_zip)
    selected, residual_rows, hangul_candidates = select_transfer_entries(steam_table, switch_table)
    overlay = make_overlay(selected, hangul_candidates)
    residual = make_residual(residual_rows)
    validate_public_artifacts(overlay, residual, steam_table)
    return stock, wrapper, raw, steam_table, overlay, residual


def build_blob(
    game_root: Path = DEFAULT_GAME_ROOT,
    switch_zip: Path = DEFAULT_SWITCH_ZIP,
) -> tuple[bytes, dict[str, Any]]:
    """Return the complete base-event candidate in memory; never writes Steam.

    This is the narrow, public composition interface used by the v5 candidate
    assembler.  It derives the overlay from the pinned Switch input and refuses
    to proceed if the tracked source-free JSON no longer equals that model.
    """
    stock, wrapper, raw, steam_table, expected_overlay, expected_residual = _derive_models(
        game_root, switch_zip
    )
    tracked_overlay = read_json(OVERLAY_PATH)
    tracked_residual = read_json(RESIDUAL_PATH)
    require_equal(tracked_overlay, expected_overlay, "tracked public overlay model")
    require_equal(tracked_residual, expected_residual, "tracked residual model")
    candidate, metrics = _build_blob_from_overlay(
        stock, wrapper, raw, steam_table, tracked_overlay, tracked_residual
    )
    require_equal(metrics["candidate"], TARGET_PIN | {"changed_entry_count": EXPECTED_SELECTED_COUNT}, "candidate metrics")
    return candidate, metrics


def verify(
    game_root: Path = DEFAULT_GAME_ROOT,
    switch_zip: Path = DEFAULT_SWITCH_ZIP,
) -> dict[str, Any]:
    """A/B-verify the public interface without writing an installed resource."""
    source_path = game_root / Path(RESOURCE)
    before = spec(source_path.read_bytes())
    first, metrics = build_blob(game_root, switch_zip)
    second, second_metrics = build_blob(game_root, switch_zip)
    if first != second or json_bytes(metrics) != json_bytes(second_metrics):
        raise TransferError("deterministic A/B candidate differs")
    tracked_validation = read_json(VALIDATION_PATH)
    require_equal(tracked_validation, metrics, "tracked validation model")
    require_equal(spec(source_path.read_bytes()), before, "installed Steam source after verification")
    return {"status": "PASS", **metrics, "deterministic_ab_equal": True}


def write_bytes(path: Path, blob: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    if path.read_bytes() != blob:
        raise TransferError(f"write verification failed: {path}")


def emit_public(game_root: Path, switch_zip: Path) -> dict[str, Any]:
    stock, wrapper, raw, steam_table, overlay, residual = _derive_models(game_root, switch_zip)
    candidate, validation = _build_blob_from_overlay(
        stock, wrapper, raw, steam_table, overlay, residual
    )
    # The candidate stays in memory. Only source-free metadata is written here.
    if not candidate:
        raise TransferError("empty candidate")
    write_bytes(OVERLAY_PATH, json_bytes(overlay))
    write_bytes(RESIDUAL_PATH, json_bytes(residual))
    write_bytes(VALIDATION_PATH, json_bytes(validation))
    return validation


def require_output_root(path: Path) -> Path:
    resolved = path.resolve()
    tmp_root = (REPO / "tmp").resolve()
    if resolved == tmp_root or tmp_root not in resolved.parents:
        raise TransferError(f"output root must be a child of repository tmp: {resolved}")
    if resolved.exists():
        raise TransferError(f"output root already exists: {resolved}")
    return resolved


def build_private_candidate(
    game_root: Path, switch_zip: Path, output_root: Path
) -> dict[str, Any]:
    first, manifest = build_blob(game_root, switch_zip)
    second, second_manifest = build_blob(game_root, switch_zip)
    if first != second or json_bytes(manifest) != json_bytes(second_manifest):
        raise TransferError("A/B deterministic build differs")
    output_root = require_output_root(output_root)
    candidate_path = output_root / "candidate" / Path(RESOURCE)
    write_bytes(candidate_path, first)
    write_bytes(output_root / "candidate_manifest.v1.json", json_bytes(manifest))
    return manifest


def verify_candidate(
    game_root: Path, switch_zip: Path, candidate_path: Path
) -> dict[str, Any]:
    expected, manifest = build_blob(game_root, switch_zip)
    actual = candidate_path.read_bytes()
    require_equal(actual, expected, "candidate bytes")
    _wrapper, actual_raw = decompress_wrapper(actual)
    actual_table = parse_message_table(actual_raw)
    require_equal(actual_table.string_count, TARGET_PIN["string_count"], "candidate string count")
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    emit = sub.add_parser("emit-public", help="Regenerate source-free public overlay and validation only")
    emit.add_argument("--steam-root", type=Path, default=DEFAULT_GAME_ROOT)
    emit.add_argument("--switch-zip", type=Path, default=DEFAULT_SWITCH_ZIP)
    emit.set_defaults(func=lambda args: emit_public(args.steam_root.resolve(), args.switch_zip.resolve()))
    build = sub.add_parser("build", help="Build an isolated candidate below repository tmp")
    build.add_argument("--steam-root", type=Path, default=DEFAULT_GAME_ROOT)
    build.add_argument("--switch-zip", type=Path, default=DEFAULT_SWITCH_ZIP)
    build.add_argument("--output-root", type=Path, default=REPO / "tmp" / "base_ev_strdata_jp_switch_v13_transfer_v1_candidate")
    build.set_defaults(func=lambda args: build_private_candidate(args.steam_root.resolve(), args.switch_zip.resolve(), args.output_root))
    verify = sub.add_parser("verify", help="Verify a candidate against public source-free artifacts")
    verify.add_argument("--steam-root", type=Path, default=DEFAULT_GAME_ROOT)
    verify.add_argument("--switch-zip", type=Path, default=DEFAULT_SWITCH_ZIP)
    verify.add_argument("--candidate", type=Path, required=True)
    verify.set_defaults(func=lambda args: verify_candidate(args.steam_root.resolve(), args.switch_zip.resolve(), args.candidate.resolve()))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest = args.func(args)
    except (OSError, ValueError, TransferError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("status=PASS")
    print(f"resource={RESOURCE}")
    print(f"selected={EXPECTED_SELECTED_COUNT}")
    print(f"residual_source_script={EXPECTED_RESIDUAL_COUNT}")
    print(f"candidate_sha256={manifest['candidate']['packed_sha256']}")
    print("installed_game_file_written=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
