#!/usr/bin/env python3
"""Build the five-entry JP common-message wave08 j01 delta.

The tracked delta is source-text-free.  It is applied after the complete
``steam_jp_common_messages_v1`` overlay and only against the pinned pristine
Steam 1.1.7 JP ``msgev.bin``.  Output is allowed only below repository ``tmp``.
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
COMMON_PATH = REPO / "workstreams" / "steam_jp_common_messages_v1" / "build_steam_jp_common_messages_v1.py"
SPEC = importlib.util.spec_from_file_location("steam_jp_common_messages_wave08_common", COMMON_PATH)
assert SPEC is not None and SPEC.loader is not None
COMMON = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = COMMON
SPEC.loader.exec_module(COMMON)


SCHEMA = "nobu16.kr.steam-jp-common-message-wave08-delta.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-common-message-wave08-j01-validation.v1"
RESOURCE = "MSG_PK/JP/msgev.bin"
NAME = "msgev.bin"
EXPECTED_IDS = [4370, 4640, 8839, 17361, 17689]
OVERLAY_PATH = HERE / "public" / "msgev_ko_steam_jp_wave08_j01_5.v1.json"
TRIAGE_PATH = HERE / "triage.v1.json"
VALIDATION_PATH = HERE / "validation.j01.v1.json"
DEFAULT_STOCK_ROOT = Path(
    "F:/SteamLibrary/steamapps/common/NOBU16/KR_PATCH_BACKUP/file_only_transaction/"
    "steam-jp-1.1.7-v0.6.0/originals"
)
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / "steam_jp_common_messages_wave08_j01_candidate"


class Wave08Error(ValueError):
    pass


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def path_spec(path: Path) -> dict[str, Any]:
    return {"size": path.stat().st_size, "sha256": sha256(path.read_bytes())}


def load_overlay() -> tuple[dict[str, Any], bytes]:
    value, blob = COMMON.read_json(OVERLAY_PATH)
    required = {
        "schema", "overlay_id", "resource", "base_language", "distribution_policy",
        "stock_jp", "provenance", "entry_count", "ids_sha256", "source_rows_sha256", "entries",
    }
    COMMON.exact_keys(value, required, "wave08 overlay")
    if value["schema"] != SCHEMA or value["resource"] != RESOURCE or value["base_language"] != "JP":
        raise Wave08Error("wave08 overlay identity differs")
    if value["stock_jp"] != COMMON.pin_public(COMMON.STEAM_PINS[NAME]):
        raise Wave08Error("wave08 Steam JP stock pin differs")
    if value["distribution_policy"] != {
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }:
        raise Wave08Error("wave08 distribution policy differs")
    provenance = value["provenance"]
    if (
        provenance.get("sc_binary_used") is not False
        or provenance.get("sc_coordinate_used") is not False
        or provenance.get("existing_v1_overlay_preserved") is not True
        or provenance.get("resolved_previous_unmapped_count") != 5
    ):
        raise Wave08Error("wave08 provenance differs")
    entries = value["entries"]
    if not isinstance(entries, list) or value["entry_count"] != len(entries):
        raise Wave08Error("wave08 entry count differs")
    ids: list[int] = []
    source_rows: list[dict[str, Any]] = []
    for index, entry in enumerate(entries):
        COMMON.exact_keys(
            entry,
            {
                "id", "recovered_legacy_jp_id", "source_jp_utf16le_sha256",
                "legacy_source_jp_utf16le_sha256", "ko", "ko_utf16le_sha256", "resolution",
            },
            f"wave08 entries[{index}]",
        )
        entry_id = COMMON.require_int(entry["id"], "entry.id")
        COMMON.require_int(entry["recovered_legacy_jp_id"], "entry.recovered_legacy_jp_id")
        source_hash = COMMON.require_hash(entry["source_jp_utf16le_sha256"], "entry source hash")
        COMMON.require_hash(entry["legacy_source_jp_utf16le_sha256"], "legacy source hash")
        COMMON.require_hash(entry["ko_utf16le_sha256"], "Korean hash")
        ko = entry["ko"]
        if not isinstance(ko, str) or "\0" in ko or COMMON.text_hash(ko) != entry["ko_utf16le_sha256"]:
            raise Wave08Error(f"wave08 Korean payload differs at id {entry_id}")
        if entry["resolution"] not in {
            "source_typo_correction_same_meaning",
            "source_orthography_normalization_same_meaning",
        }:
            raise Wave08Error(f"wave08 resolution differs at id {entry_id}")
        ids.append(entry_id)
        source_rows.append({"id": entry_id, "source_jp_utf16le_sha256": source_hash})
    if ids != EXPECTED_IDS or COMMON.canonical_hash(ids) != value["ids_sha256"]:
        raise Wave08Error("wave08 ID vector differs")
    if COMMON.canonical_hash(source_rows) != value["source_rows_sha256"]:
        raise Wave08Error("wave08 source row vector differs")
    return value, blob


def build_blob(stock_root: Path) -> tuple[bytes, dict[str, Any]]:
    delta, overlay_blob = load_overlay()
    stock = COMMON.load_pinned(
        stock_root / Path(RESOURCE), COMMON.STEAM_PINS[NAME], "Steam 1.1.7 pristine JP msgev"
    )
    base_overlays, _blobs = COMMON.load_public_overlays()
    baseline, baseline_metrics = COMMON.build_one(NAME, stock, base_overlays[NAME])
    _prefix, baseline_raw = COMMON.decompress_wrapper(baseline)
    baseline_table = COMMON.parse_message_table(baseline_raw)
    texts = list(baseline_table.texts)
    delta_ids: set[int] = set()
    for entry in delta["entries"]:
        entry_id = int(entry["id"])
        source = stock.table.texts[entry_id]
        if COMMON.text_hash(source) != entry["source_jp_utf16le_sha256"]:
            raise Wave08Error(f"wave08 current JP source hash differs at id {entry_id}")
        if texts[entry_id] != source:
            raise Wave08Error(f"wave08 id {entry_id} overlaps the v1 overlay")
        mismatches = COMMON.common.invariant_mismatches(source, entry["ko"])
        if mismatches:
            raise Wave08Error(f"wave08 invariant mismatch at id {entry_id}: {mismatches}")
        texts[entry_id] = entry["ko"]
        delta_ids.add(entry_id)

    rebuilt_raw = COMMON.rebuild_message_table(stock.table, texts)
    reparsed = COMMON.parse_message_table(rebuilt_raw)
    if reparsed.texts != tuple(texts):
        raise Wave08Error("wave08 rebuilt table differs")
    if not COMMON._opaque_structure_preserved(stock.table, reparsed, rebuilt_raw):
        raise Wave08Error("wave08 opaque structure differs")
    for entry_id, text in enumerate(baseline_table.texts):
        if entry_id not in delta_ids and reparsed.texts[entry_id] != text:
            raise Wave08Error(f"wave08 changed non-delta id {entry_id}")
    candidate = COMMON.recompress_wrapper(rebuilt_raw, stock.packed)
    _header, roundtrip = COMMON.decompress_wrapper(candidate)
    if roundtrip != rebuilt_raw or candidate[:8] != stock.packed[:8]:
        raise Wave08Error("wave08 wrapper round-trip differs")
    metrics = {
        "resource": RESOURCE,
        "baseline_applied_count": int(baseline_metrics["applied_count"]),
        "delta_applied_count": len(delta_ids),
        "total_common_applied_count": 39_512,
        "remaining_legacy_unresolved_count": 91,
        "candidate": {
            "size": len(candidate),
            "sha256": sha256(candidate),
            "raw_size": len(rebuilt_raw),
            "raw_sha256": sha256(rebuilt_raw),
        },
        "baseline_candidate": {"size": len(baseline), "sha256": sha256(baseline)},
        "overlay": {"size": len(overlay_blob), "sha256": sha256(overlay_blob)},
        "id_domain_preserved": True,
        "non_delta_texts_preserved": True,
        "wrapper_prefix_preserved": True,
        "sc_binary_used": False,
        "sc_coordinate_used": False,
    }
    return candidate, metrics


def verify(stock_root: Path) -> dict[str, Any]:
    first, first_metrics = build_blob(stock_root)
    second, second_metrics = build_blob(stock_root)
    if first != second or first_metrics != second_metrics:
        raise Wave08Error("wave08 deterministic A/B build differs")
    validation, _blob = COMMON.read_json(VALIDATION_PATH)
    if validation.get("schema") != VALIDATION_SCHEMA:
        raise Wave08Error("wave08 validation schema differs")
    expected = validation["expected"]
    observed = {
        "candidate": first_metrics["candidate"],
        "baseline_candidate": first_metrics["baseline_candidate"],
        "overlay": first_metrics["overlay"],
        "triage": path_spec(TRIAGE_PATH),
    }
    if observed != expected:
        raise Wave08Error(f"wave08 expected vector differs: {observed} != {expected}")
    if validation["translation"] != {
        "delta_applied_count": 5,
        "total_common_applied_count": 39_512,
        "remaining_legacy_unresolved_count": 91,
    }:
        raise Wave08Error("wave08 translation totals differ")
    return {"status": "PASS", **first_metrics, "deterministic_ab_equal": True}


def output_root(path: Path) -> Path:
    resolved = path.resolve()
    tmp = (REPO / "tmp").resolve()
    if resolved == tmp or tmp not in resolved.parents or resolved.exists():
        raise Wave08Error(f"unsafe or existing output root: {resolved}")
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("verify", "build"):
        child = subparsers.add_parser(command)
        child.add_argument("--stock-root", type=Path, default=DEFAULT_STOCK_ROOT)
        if command == "build":
            child.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    if args.command == "verify":
        result = verify(args.stock_root)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    candidate, metrics = build_blob(args.stock_root)
    destination = output_root(args.output_root)
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
