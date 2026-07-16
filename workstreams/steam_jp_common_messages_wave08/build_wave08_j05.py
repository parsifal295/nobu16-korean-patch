#!/usr/bin/env python3
"""Build the six-entry Steam-JP wave08 j05 current-revision delta."""

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
SPEC = importlib.util.spec_from_file_location(
    "steam_jp_common_messages_wave08_j05_common", COMMON_PATH
)
assert SPEC is not None and SPEC.loader is not None
COMMON = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = COMMON
SPEC.loader.exec_module(COMMON)


SCHEMA = "nobu16.kr.steam-jp-common-message-wave08-delta.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-common-message-wave08-j05-validation.v1"
BATCH_ID = "j05_msgdata_live_revisions"
RESOURCE = "MSG_PK/JP/msgdata.bin"
NAME = "msgdata.bin"
EXPECTED_IDS = [15021, 22663, 23164, 25208, 25463, 25900]
EXPECTED_LEGACY_IDS = [15017, 22655, 23156, 25200, 25455, 25892]
OVERLAY_PATH = (
    HERE / "public" / "msgdata_ko_steam_jp_wave08_j05_live_revisions_6.v1.json"
)
TRIAGE_PATH = HERE / "triage.v1.json"
VALIDATION_PATH = HERE / "validation.j05.v1.json"
DEFAULT_STOCK_ROOT = Path(
    "F:/SteamLibrary/steamapps/common/NOBU16/KR_PATCH_BACKUP/file_only_transaction/"
    "steam-jp-1.1.7-v0.6.0/originals"
)
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / "steam_jp_common_messages_wave08_j05_candidate"


class Wave08J05Error(ValueError):
    """A j05 source, structure, translation, or output contract failed."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def load_triage_batch() -> dict[str, Any]:
    triage, _blob = COMMON.read_json(TRIAGE_PATH)
    matches = [row for row in triage.get("batches", []) if row.get("batch_id") == BATCH_ID]
    if len(matches) != 1:
        raise Wave08J05Error("wave08 j05 triage batch is absent or duplicated")
    batch = matches[0]
    expected = {
        "resource": RESOURCE,
        "semantic_entry_count": 6,
        "translation_action": "translate",
        "current_ids": EXPECTED_IDS,
        "legacy_ids": EXPECTED_LEGACY_IDS,
        "current_ids_sha256": COMMON.canonical_hash(EXPECTED_IDS),
        "source_rows_sha256": "2444099BD0948840E866A13FEE364D0AE4A6E30D04C3E055E2304F6817C5EAFF",
    }
    for key, value in expected.items():
        if batch.get(key) != value:
            raise Wave08J05Error(f"wave08 j05 triage {key} differs")
    return batch


def load_overlay() -> tuple[dict[str, Any], bytes]:
    value, blob = COMMON.read_json(OVERLAY_PATH)
    COMMON.exact_keys(
        value,
        {
            "schema", "overlay_id", "resource", "base_language",
            "distribution_policy", "stock_jp", "provenance", "entry_count",
            "ids_sha256", "source_rows_sha256", "entries",
        },
        "wave08 j05 overlay",
    )
    if (
        value["schema"] != SCHEMA
        or value["resource"] != RESOURCE
        or value["base_language"] != "JP"
    ):
        raise Wave08J05Error("wave08 j05 overlay identity differs")
    if value["stock_jp"] != COMMON.pin_public(COMMON.STEAM_PINS[NAME]):
        raise Wave08J05Error("wave08 j05 Steam JP stock pin differs")
    if value["distribution_policy"] != {
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }:
        raise Wave08J05Error("wave08 j05 distribution policy differs")
    expected_provenance = {
        "batch_id": BATCH_ID,
        "builder_reads_pristine_jp_only": True,
        "existing_v1_overlay_preserved": True,
        "mapping_method": "current_steam_jp_id_manual_semantic_revision_translation",
        "official_multilingual_reference_is_build_dependency": False,
        "official_multilingual_same_id_reviewed": True,
        "resolved_previous_unmapped_count": 6,
    }
    if value["provenance"] != expected_provenance:
        raise Wave08J05Error("wave08 j05 provenance differs")
    entries = value["entries"]
    if not isinstance(entries, list) or value["entry_count"] != len(entries):
        raise Wave08J05Error("wave08 j05 entry count differs")
    ids: list[int] = []
    legacy_ids: list[int] = []
    source_rows: list[dict[str, Any]] = []
    for index, entry in enumerate(entries):
        COMMON.exact_keys(
            entry,
            {
                "id", "recovered_legacy_jp_id", "source_jp_utf16le_sha256",
                "ko", "ko_utf16le_sha256", "translation_role",
            },
            f"wave08 j05 entries[{index}]",
        )
        entry_id = COMMON.require_int(entry["id"], "entry.id")
        legacy_id = COMMON.require_int(
            entry["recovered_legacy_jp_id"], "entry.recovered_legacy_jp_id"
        )
        source_hash = COMMON.require_hash(
            entry["source_jp_utf16le_sha256"], "entry source hash"
        )
        COMMON.require_hash(entry["ko_utf16le_sha256"], "entry Korean hash")
        ko = entry["ko"]
        if (
            not isinstance(ko, str)
            or "\0" in ko
            or not COMMON.common.has_semantic_text(ko)
            or COMMON.text_hash(ko) != entry["ko_utf16le_sha256"]
            or entry["translation_role"] != "current_semantic_revision"
        ):
            raise Wave08J05Error(f"wave08 j05 Korean payload differs at {entry_id}")
        ids.append(entry_id)
        legacy_ids.append(legacy_id)
        source_rows.append({"id": entry_id, "source_jp_utf16le_sha256": source_hash})
    if ids != EXPECTED_IDS or COMMON.canonical_hash(ids) != value["ids_sha256"]:
        raise Wave08J05Error("wave08 j05 ID vector differs")
    if legacy_ids != EXPECTED_LEGACY_IDS:
        raise Wave08J05Error("wave08 j05 legacy ID vector differs")
    if COMMON.canonical_hash(source_rows) != value["source_rows_sha256"]:
        raise Wave08J05Error("wave08 j05 source-row vector differs")
    batch = load_triage_batch()
    if value["source_rows_sha256"] != batch["source_rows_sha256"]:
        raise Wave08J05Error("wave08 j05 overlay/triage source rows differ")
    return value, blob


def build_blob(stock_root: Path) -> tuple[bytes, dict[str, Any]]:
    delta, overlay_blob = load_overlay()
    stock = COMMON.load_pinned(
        stock_root / Path(RESOURCE),
        COMMON.STEAM_PINS[NAME],
        "Steam 1.1.7 pristine JP msgdata",
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
            raise Wave08J05Error(f"wave08 j05 JP source hash differs at {entry_id}")
        if texts[entry_id] != source:
            raise Wave08J05Error(f"wave08 j05 ID {entry_id} overlaps the v1 overlay")
        mismatches = COMMON.common.invariant_mismatches(source, entry["ko"])
        if mismatches:
            raise Wave08J05Error(
                f"wave08 j05 invariant mismatch at {entry_id}: {mismatches}"
            )
        texts[entry_id] = entry["ko"]
        delta_ids.add(entry_id)

    rebuilt_raw = COMMON.rebuild_message_table(stock.table, texts)
    reparsed = COMMON.parse_message_table(rebuilt_raw)
    if reparsed.texts != tuple(texts):
        raise Wave08J05Error("wave08 j05 rebuilt table differs")
    if not COMMON._opaque_structure_preserved(stock.table, reparsed, rebuilt_raw):
        raise Wave08J05Error("wave08 j05 opaque structure differs")
    for entry_id, text in enumerate(baseline_table.texts):
        if entry_id not in delta_ids and reparsed.texts[entry_id] != text:
            raise Wave08J05Error(f"wave08 j05 changed non-delta ID {entry_id}")
    candidate = COMMON.recompress_wrapper(rebuilt_raw, stock.packed)
    _header, roundtrip = COMMON.decompress_wrapper(candidate)
    if roundtrip != rebuilt_raw or candidate[:8] != stock.packed[:8]:
        raise Wave08J05Error("wave08 j05 wrapper round-trip differs")
    metrics = {
        "resource": RESOURCE,
        "baseline_applied_count": int(baseline_metrics["applied_count"]),
        "delta_applied_count": len(delta_ids),
        "total_common_applied_count": 39_513,
        "remaining_legacy_unresolved_count": 90,
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
        "builder_read_pristine_jp_only": True,
    }
    return candidate, metrics


def verify(stock_root: Path) -> dict[str, Any]:
    first, first_metrics = build_blob(stock_root)
    second, second_metrics = build_blob(stock_root)
    if first != second or first_metrics != second_metrics:
        raise Wave08J05Error("wave08 j05 deterministic A/B build differs")
    validation, _blob = COMMON.read_json(VALIDATION_PATH)
    if validation.get("schema") != VALIDATION_SCHEMA:
        raise Wave08J05Error("wave08 j05 validation schema differs")
    observed = {
        "candidate": first_metrics["candidate"],
        "baseline_candidate": first_metrics["baseline_candidate"],
        "overlay": first_metrics["overlay"],
    }
    if observed != validation["expected"]:
        raise Wave08J05Error(
            f"wave08 j05 expected vector differs: {observed} != {validation['expected']}"
        )
    if validation["translation"] != {
        "delta_applied_count": 6,
        "total_common_applied_count": 39_513,
        "remaining_legacy_unresolved_count": 90,
    }:
        raise Wave08J05Error("wave08 j05 translation totals differ")
    return {"status": "PASS", **first_metrics, "deterministic_ab_equal": True}


def output_root(path: Path) -> Path:
    resolved = path.resolve()
    tmp = (REPO / "tmp").resolve()
    if resolved == tmp or tmp not in resolved.parents or resolved.exists():
        raise Wave08J05Error(f"unsafe or existing output root: {resolved}")
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
        print(json.dumps(verify(args.stock_root), ensure_ascii=False, indent=2, sort_keys=True))
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
