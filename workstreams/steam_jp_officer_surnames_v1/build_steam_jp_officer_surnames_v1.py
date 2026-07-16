#!/usr/bin/env python3
"""Recover 980 omitted Steam-JP officer surname components.

The Korean catalog is source-text-free.  Every selected coordinate is mapped
through the reviewed JP equal-hash blocks and pinned again to the pristine
Steam 1.1.7 JP ``msgdata.bin`` source hash.  No SC binary is read.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
COMMON_PATH = (
    REPO
    / "workstreams"
    / "steam_jp_common_messages_v1"
    / "build_steam_jp_common_messages_v1.py"
)
SPEC = importlib.util.spec_from_file_location("steam_jp_officer_surnames_common", COMMON_PATH)
assert SPEC is not None and SPEC.loader is not None
COMMON = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = COMMON
SPEC.loader.exec_module(COMMON)


SCHEMA = "nobu16.kr.steam-jp-officer-surname-overlay.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-officer-surname-validation.v1"
RESOURCE = "MSG_PK/JP/msgdata.bin"
NAME = "msgdata.bin"
CATALOG_PATH = REPO / "data" / "public" / "msgdata_ko_officer_names_0000_2399.v0.1.json"
CATALOG_PIN = {
    "size": 656_630,
    "sha256": "D787EB64BFFC54D1ACA2F23BC9407991FEB4FCF76D102E1EE017EEF416FE4FA3",
}
OVERLAY_PATH = HERE / "public" / "msgdata_ko_steam_jp_officer_surnames_980.v1.json"
VALIDATION_PATH = HERE / "validation.v1.json"
DEFAULT_STOCK_ROOT = Path(
    "F:/SteamLibrary/steamapps/common/NOBU16/KR_PATCH_BACKUP/file_only_transaction/"
    "steam-jp-1.1.7-v0.6.0/originals"
)
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / "steam_jp_officer_surnames_v1_candidate"

CATALOG_SURNAME_COUNT = 1_050
BASE_OWNED_CONFLICT_COUNT = 70
RECOVERED_SURNAME_COUNT = 980
PRIMARY_SURNAME_COUNT = 859
BASE_COMMON_APPLIED = 39_507
SOURCE_UNION_COUNT = 43_169
SOURCE_EQUAL_CONTRACT_COUNT = 1_796
FORMAT_BACKLOG_BEFORE = 1_710
FORMAT_BACKLOG_AFTER = 730
ALIGNMENT_GAP_BEFORE_WAVE08 = 156
ODA_SURNAME_ID = 84
ODA_GIVEN_ID = 1_266
ODA_SOURCE_HASH = "7930DAF0848B54FFA971AD8A02828B5692EA8E06664AA1714F4337AEE3499F66"


class SurnameError(ValueError):
    """A source, catalog, mapping, spacing, or structure contract differed."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def path_spec(path: Path) -> dict[str, Any]:
    blob = path.read_bytes()
    return {"size": len(blob), "sha256": sha256(blob)}


def load_catalog() -> tuple[dict[str, Any], bytes]:
    value, blob = COMMON.read_json(CATALOG_PATH)
    if {"size": len(blob), "sha256": sha256(blob)} != CATALOG_PIN:
        raise SurnameError("officer-name catalog pin differs")
    if (
        value.get("schema") != "nobu16.kr.common-message-overlay.v1"
        or value.get("entry_count") != 3_831
        or value.get("distribution_policy")
        != {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        }
    ):
        raise SurnameError("officer-name catalog contract differs")
    return value, blob


def equal_block_mapping(base_overlay: dict[str, Any]) -> dict[int, tuple[int, int]]:
    mapping: dict[int, tuple[int, int]] = {}
    blocks = base_overlay["equal_hash_blocks"]
    for block_index, block in enumerate(blocks):
        old_start = int(block["legacy_start_id"])
        current_start = int(block["steam_start_id"])
        length = int(block["length"])
        for offset in range(length):
            old_id = old_start + offset
            if old_id in mapping:
                raise SurnameError(f"equal-hash mapping overlaps at {old_id}")
            mapping[old_id] = (current_start + offset, block_index)
    return mapping


def expected_overlay(stock_root: Path) -> dict[str, Any]:
    catalog, catalog_blob = load_catalog()
    base_overlays, base_blobs = COMMON.load_public_overlays()
    base = base_overlays[NAME]
    mapping = equal_block_mapping(base)
    stock = COMMON.load_pinned(
        stock_root / Path(RESOURCE),
        COMMON.STEAM_PINS[NAME],
        "Steam 1.1.7 pristine JP msgdata",
    )
    base_ids = {int(entry["id"]) for entry in base["entries"]}
    surname_rows = [
        entry for entry in catalog["entries"] if entry.get("allow_edge_whitespace_change") is True
    ]
    if len(surname_rows) != CATALOG_SURNAME_COUNT:
        raise SurnameError("catalog surname count differs")

    entries: list[dict[str, Any]] = []
    base_owned: list[int] = []
    primary_count = 0
    for row in surname_rows:
        legacy_id = COMMON.require_int(row.get("id"), "catalog surname id")
        mapped = mapping.get(legacy_id)
        if mapped is None:
            raise SurnameError(f"surname is outside JP equal-hash blocks: {legacy_id}")
        current_id, block_index = mapped
        korean = row.get("ko")
        if (
            not isinstance(korean, str)
            or not korean.endswith(" ")
            or korean.rstrip() + " " != korean
            or "\0" in korean
        ):
            raise SurnameError(f"surname spacing differs at {legacy_id}")
        if current_id in base_ids:
            base_owned.append(current_id)
            continue
        source = stock.table.texts[current_id]
        mismatches = COMMON.common.invariant_mismatches(
            source, korean, allow_edge_whitespace_change=True
        )
        if mismatches:
            raise SurnameError(f"surname invariant differs at {current_id}: {mismatches}")
        if source == korean:
            raise SurnameError(f"surname recovery is a no-op at {current_id}")
        if legacy_id <= 937:
            primary_count += 1
        entries.append(
            {
                "id": current_id,
                "legacy_catalog_id": legacy_id,
                "mapping_block_index": block_index,
                "source_jp_utf16le_sha256": COMMON.text_hash(source),
                "ko": korean,
                "ko_utf16le_sha256": COMMON.text_hash(korean),
                "allow_edge_whitespace_change": True,
            }
        )

    entries.sort(key=lambda entry: int(entry["id"]))
    ids = [int(entry["id"]) for entry in entries]
    if (
        len(entries) != RECOVERED_SURNAME_COUNT
        or len(base_owned) != BASE_OWNED_CONFLICT_COUNT
        or primary_count != PRIMARY_SURNAME_COUNT
        or ids != sorted(set(ids))
    ):
        raise SurnameError("surname recovery partition differs")
    oda = [entry for entry in entries if entry["id"] == ODA_SURNAME_ID]
    if (
        len(oda) != 1
        or oda[0]["legacy_catalog_id"] != ODA_SURNAME_ID
        or oda[0]["source_jp_utf16le_sha256"] != ODA_SOURCE_HASH
        or oda[0]["ko"] != "오다 "
    ):
        raise SurnameError("Oda surname regression vector differs")
    source_rows = [
        {"id": entry["id"], "source_jp_utf16le_sha256": entry["source_jp_utf16le_sha256"]}
        for entry in entries
    ]
    return {
        "schema": SCHEMA,
        "overlay_id": "msgdata_ko_steam_jp_officer_surnames_980.v1",
        "resource": RESOURCE,
        "base_language": "JP",
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_jp": COMMON.pin_public(COMMON.STEAM_PINS[NAME]),
        "provenance": {
            "korean_catalog": CATALOG_PATH.relative_to(REPO).as_posix(),
            "korean_catalog_sha256": sha256(catalog_blob),
            "mapping_method": "reviewed_jp_equal_hash_blocks_then_current_jp_source_hash",
            "base_overlay_sha256": sha256(base_blobs[NAME]),
            "catalog_surname_count": CATALOG_SURNAME_COUNT,
            "base_owned_conflict_count": BASE_OWNED_CONFLICT_COUNT,
            "recovered_format_blocked_count": RECOVERED_SURNAME_COUNT,
            "sc_binary_used": False,
            "sc_runtime_path_used": False,
            "current_jp_source_hashes_fail_closed": True,
        },
        "entry_count": len(entries),
        "primary_surname_count": primary_count,
        "ids_sha256": COMMON.canonical_hash(ids),
        "base_owned_ids_sha256": COMMON.canonical_hash(sorted(base_owned)),
        "source_rows_sha256": COMMON.canonical_hash(source_rows),
        "entries": entries,
    }


def load_overlay(stock_root: Path) -> tuple[dict[str, Any], bytes]:
    value, blob = COMMON.read_json(OVERLAY_PATH)
    expected = expected_overlay(stock_root)
    if value != expected or blob != COMMON.pretty_bytes(expected):
        raise SurnameError("tracked surname overlay differs from deterministic model")
    return value, blob


def build_blob(stock_root: Path) -> tuple[bytes, dict[str, Any]]:
    overlay, overlay_blob = load_overlay(stock_root)
    stock = COMMON.load_pinned(
        stock_root / Path(RESOURCE),
        COMMON.STEAM_PINS[NAME],
        "Steam 1.1.7 pristine JP msgdata",
    )
    base_overlays, _base_blobs = COMMON.load_public_overlays()
    baseline, baseline_metrics = COMMON.build_one(NAME, stock, base_overlays[NAME])
    _wrapper, baseline_raw = COMMON.decompress_wrapper(baseline)
    baseline_table = COMMON.parse_message_table(baseline_raw)
    texts = list(baseline_table.texts)
    changed: set[int] = set()
    for entry in overlay["entries"]:
        entry_id = int(entry["id"])
        source = stock.table.texts[entry_id]
        if COMMON.text_hash(source) != entry["source_jp_utf16le_sha256"]:
            raise SurnameError(f"current JP source hash differs at {entry_id}")
        if texts[entry_id] != source:
            raise SurnameError(f"surname overlaps base overlay at {entry_id}")
        mismatches = COMMON.common.invariant_mismatches(
            source, entry["ko"], allow_edge_whitespace_change=True
        )
        if mismatches:
            raise SurnameError(f"surname invariant differs at {entry_id}: {mismatches}")
        texts[entry_id] = entry["ko"]
        changed.add(entry_id)
    if texts[ODA_SURNAME_ID] + texts[ODA_GIVEN_ID] != "오다 노부나가":
        raise SurnameError("Oda Nobunaga recomposition differs")

    rebuilt_raw = COMMON.rebuild_message_table(stock.table, texts)
    reparsed = COMMON.parse_message_table(rebuilt_raw)
    if reparsed.texts != tuple(texts):
        raise SurnameError("rebuilt surname table differs")
    if not COMMON._opaque_structure_preserved(stock.table, reparsed, rebuilt_raw):
        raise SurnameError("surname candidate opaque structure differs")
    for entry_id, text in enumerate(baseline_table.texts):
        if entry_id not in changed and reparsed.texts[entry_id] != text:
            raise SurnameError(f"non-surname text changed at {entry_id}")
    candidate = COMMON.recompress_wrapper(rebuilt_raw, stock.packed)
    _header, roundtrip = COMMON.decompress_wrapper(candidate)
    if roundtrip != rebuilt_raw or candidate[:8] != stock.packed[:8]:
        raise SurnameError("surname candidate wrapper round-trip differs")
    return candidate, {
        "resource": RESOURCE,
        "baseline_applied_count": int(baseline_metrics["applied_count"]),
        "surname_delta_count": len(changed),
        "global_common_applied_count_without_wave08": BASE_COMMON_APPLIED + len(changed),
        "format_contract_backlog_before": FORMAT_BACKLOG_BEFORE,
        "format_contract_backlog_after": FORMAT_BACKLOG_AFTER,
        "candidate": {
            "size": len(candidate),
            "sha256": sha256(candidate),
            "raw_size": len(rebuilt_raw),
            "raw_sha256": sha256(rebuilt_raw),
        },
        "baseline_candidate": {"size": len(baseline), "sha256": sha256(baseline)},
        "overlay": {"size": len(overlay_blob), "sha256": sha256(overlay_blob)},
        "oda_nobunaga_recomposition": "오다 노부나가",
        "id_domain_preserved": True,
        "non_delta_texts_preserved": True,
        "wrapper_prefix_preserved": True,
        "sc_binary_used": False,
    }


def validation_model(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": VALIDATION_SCHEMA,
        "status": "PASS",
        "resource": RESOURCE,
        "translation": {
            "catalog_surname_count": CATALOG_SURNAME_COUNT,
            "base_owned_conflict_count": BASE_OWNED_CONFLICT_COUNT,
            "recovered_surname_count": RECOVERED_SURNAME_COUNT,
            "primary_surname_count": PRIMARY_SURNAME_COUNT,
            "format_contract_backlog_before": FORMAT_BACKLOG_BEFORE,
            "format_contract_backlog_after": FORMAT_BACKLOG_AFTER,
        },
        "accounting": {
            "source_union_count": SOURCE_UNION_COUNT,
            "source_equal_contract_count": SOURCE_EQUAL_CONTRACT_COUNT,
            "alignment_gap_before_wave08": ALIGNMENT_GAP_BEFORE_WAVE08,
        },
        "expected": {
            "candidate": metrics["candidate"],
            "baseline_candidate": metrics["baseline_candidate"],
            "overlay": metrics["overlay"],
            "catalog": path_spec(CATALOG_PATH),
        },
        "proofs": {
            "oda_nobunaga_recomposition": metrics["oda_nobunaga_recomposition"],
            "deterministic_ab_equal": True,
            "current_jp_source_hashes_fail_closed": True,
            "base_owned_conflicts_preserved": True,
            "id_domain_preserved": True,
            "non_delta_texts_preserved": True,
            "wrapper_prefix_preserved": True,
        },
        "safety": {
            "complete_candidate_binary_tracked": False,
            "installed_game_files_modified": False,
            "sc_binary_used": False,
        },
    }


def generate(stock_root: Path) -> dict[str, Any]:
    OVERLAY_PATH.parent.mkdir(parents=True, exist_ok=True)
    OVERLAY_PATH.write_bytes(COMMON.pretty_bytes(expected_overlay(stock_root)))
    first, first_metrics = build_blob(stock_root)
    second, second_metrics = build_blob(stock_root)
    if first != second or first_metrics != second_metrics:
        raise SurnameError("surname deterministic A/B build differs")
    VALIDATION_PATH.write_bytes(COMMON.pretty_bytes(validation_model(first_metrics)))
    return {"status": "GENERATED", **first_metrics, "deterministic_ab_equal": True}


def verify(stock_root: Path) -> dict[str, Any]:
    first, first_metrics = build_blob(stock_root)
    second, second_metrics = build_blob(stock_root)
    if first != second or first_metrics != second_metrics:
        raise SurnameError("surname deterministic A/B build differs")
    validation, blob = COMMON.read_json(VALIDATION_PATH)
    expected = validation_model(first_metrics)
    if validation != expected or blob != COMMON.pretty_bytes(expected):
        raise SurnameError("tracked surname validation differs")
    return {"status": "PASS", **first_metrics, "deterministic_ab_equal": True}


def safe_output(path: Path) -> Path:
    resolved = path.resolve()
    tmp = (REPO / "tmp").resolve()
    if resolved == tmp or tmp not in resolved.parents or resolved.exists():
        raise SurnameError(f"unsafe or existing output root: {resolved}")
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("generate", "verify", "build"):
        child = commands.add_parser(command)
        child.add_argument("--stock-root", type=Path, default=DEFAULT_STOCK_ROOT)
        if command == "build":
            child.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    if args.command == "generate":
        print(json.dumps(generate(args.stock_root), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "verify":
        print(json.dumps(verify(args.stock_root), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    candidate, metrics = build_blob(args.stock_root)
    destination = safe_output(args.output_root)
    try:
        target = destination / Path(RESOURCE)
        target.parent.mkdir(parents=True, exist_ok=False)
        target.write_bytes(candidate)
        (destination / "private_manifest.json").write_bytes(COMMON.pretty_bytes(metrics))
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
