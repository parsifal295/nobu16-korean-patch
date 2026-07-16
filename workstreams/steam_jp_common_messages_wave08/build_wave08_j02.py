#!/usr/bin/env python3
"""Build the two-entry Steam JP common-message wave08 j02 delta."""

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
    "steam_jp_common_messages_wave08_j02_common", COMMON_PATH
)
assert SPEC is not None and SPEC.loader is not None
COMMON = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = COMMON
SPEC.loader.exec_module(COMMON)


SCHEMA = "nobu16.kr.steam-jp-common-message-wave08-delta.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-common-message-wave08-j02-validation.v1"
BATCH_ID = "j02_msgev_officer_names"
RESOURCE = "MSG_PK/JP/msgev.bin"
NAME = "msgev.bin"
EXPECTED_IDS = [301, 1584]
TRANSLATIONS = {
    301: "겐코 에탄",
    1584: "오후지 노부모토",
}
RESOLUTION = "current_officer_identity_translation"
OVERLAY_PATH = HERE / "public" / "msgev_ko_steam_jp_wave08_j02_2.v1.json"
TRIAGE_PATH = HERE / "triage.v1.json"
VALIDATION_PATH = HERE / "validation.j02.v1.json"
DEFAULT_STOCK_ROOT = Path(
    "F:/SteamLibrary/steamapps/common/NOBU16/KR_PATCH_BACKUP/file_only_transaction/"
    "steam-jp-1.1.7-v0.6.0/originals"
)
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / "steam_jp_common_messages_wave08_j02_candidate"
BASELINE_GLOBAL_APPLIED = 39_507
LEGACY_UNRESOLVED = 96


class Wave08J02Error(ValueError):
    """A j02 source, translation, structure, or output contract differed."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def path_spec(path: Path) -> dict[str, Any]:
    blob = path.read_bytes()
    return {"size": len(blob), "sha256": sha256(blob)}


def read_triage_batch() -> tuple[dict[str, Any], dict[str, Any]]:
    triage, _blob = COMMON.read_json(TRIAGE_PATH)
    batches = [row for row in triage.get("batches", []) if row.get("batch_id") == BATCH_ID]
    if len(batches) != 1:
        raise Wave08J02Error("j02 triage batch is not unique")
    batch = batches[0]
    if (
        batch.get("resource") != RESOURCE
        or batch.get("current_ids") != EXPECTED_IDS
        or batch.get("semantic_entry_count") != len(EXPECTED_IDS)
        or batch.get("translation_action") != "translate"
        or COMMON.canonical_hash(EXPECTED_IDS) != batch.get("current_ids_sha256")
    ):
        raise Wave08J02Error("j02 triage scope differs")
    return triage, batch


def legacy_rows(triage: dict[str, Any], batch: dict[str, Any]) -> dict[int, dict[str, Any]]:
    review_path = REPO / triage["provenance"]["legacy_unresolved_review"]
    if path_spec(review_path)["sha256"] != triage["provenance"]["legacy_unresolved_review_sha256"]:
        raise Wave08J02Error("legacy unresolved review pin differs")
    review, _blob = COMMON.read_json(review_path)
    resources = [row for row in review.get("resources", []) if row.get("resource") == RESOURCE]
    if len(resources) != 1:
        raise Wave08J02Error("legacy msgev review is not unique")
    wanted = set(batch["legacy_ids"])
    result = {
        int(row["legacy_jp_id"]): row
        for row in resources[0].get("entries", [])
        if int(row.get("legacy_jp_id", -1)) in wanted
    }
    if set(result) != wanted or any(row.get("coverage") != "unresolved" for row in result.values()):
        raise Wave08J02Error("legacy j02 review rows differ")
    return result


def expected_overlay(stock_root: Path) -> dict[str, Any]:
    triage, batch = read_triage_batch()
    stock = COMMON.load_pinned(
        stock_root / Path(RESOURCE),
        COMMON.STEAM_PINS[NAME],
        "Steam 1.1.7 pristine JP msgev",
    )
    old = legacy_rows(triage, batch)
    source_rows: list[dict[str, Any]] = []
    entries: list[dict[str, Any]] = []
    for legacy_id, entry_id in zip(batch["legacy_ids"], EXPECTED_IDS, strict=True):
        source_hash = COMMON.text_hash(stock.table.texts[entry_id])
        korean = TRANSLATIONS[entry_id]
        source_rows.append({"id": entry_id, "source_jp_utf16le_sha256": source_hash})
        entries.append(
            {
                "id": entry_id,
                "recovered_legacy_jp_id": legacy_id,
                "source_jp_utf16le_sha256": source_hash,
                "legacy_source_jp_utf16le_sha256": old[legacy_id][
                    "source_jp_utf16le_sha256"
                ],
                "ko": korean,
                "ko_utf16le_sha256": COMMON.text_hash(korean),
                "resolution": RESOLUTION,
            }
        )
    source_rows_hash = COMMON.canonical_hash(source_rows)
    if source_rows_hash != batch["source_rows_sha256"]:
        raise Wave08J02Error("j02 current JP source row vector differs")
    return {
        "schema": SCHEMA,
        "overlay_id": "msgev_ko_steam_jp_wave08_j02_officer_names_2.v1",
        "resource": RESOURCE,
        "base_language": "JP",
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_jp": COMMON.pin_public(COMMON.STEAM_PINS[NAME]),
        "provenance": {
            "mapping_method": "manual_current_jp_identity_translation",
            "resolved_previous_unmapped_count": len(EXPECTED_IDS),
            "existing_v1_overlay_preserved": True,
            "sc_binary_used": False,
            "sc_coordinate_used": False,
        },
        "entry_count": len(entries),
        "ids_sha256": batch["current_ids_sha256"],
        "source_rows_sha256": source_rows_hash,
        "entries": entries,
    }


def load_overlay(stock_root: Path) -> tuple[dict[str, Any], bytes]:
    value, blob = COMMON.read_json(OVERLAY_PATH)
    expected = expected_overlay(stock_root)
    if value != expected or blob != COMMON.pretty_bytes(expected):
        raise Wave08J02Error("tracked j02 overlay differs from deterministic model")
    return value, blob


def build_blob(stock_root: Path) -> tuple[bytes, dict[str, Any]]:
    delta, overlay_blob = load_overlay(stock_root)
    stock = COMMON.load_pinned(
        stock_root / Path(RESOURCE),
        COMMON.STEAM_PINS[NAME],
        "Steam 1.1.7 pristine JP msgev",
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
            raise Wave08J02Error(f"j02 current JP source hash differs at id {entry_id}")
        if texts[entry_id] != source:
            raise Wave08J02Error(f"j02 id {entry_id} overlaps the v1 overlay")
        mismatches = COMMON.common.invariant_mismatches(source, entry["ko"])
        if mismatches:
            raise Wave08J02Error(f"j02 invariant mismatch at id {entry_id}: {mismatches}")
        texts[entry_id] = entry["ko"]
        delta_ids.add(entry_id)

    rebuilt_raw = COMMON.rebuild_message_table(stock.table, texts)
    reparsed = COMMON.parse_message_table(rebuilt_raw)
    if reparsed.texts != tuple(texts):
        raise Wave08J02Error("j02 rebuilt table differs")
    if not COMMON._opaque_structure_preserved(stock.table, reparsed, rebuilt_raw):
        raise Wave08J02Error("j02 opaque structure differs")
    for entry_id, text in enumerate(baseline_table.texts):
        if entry_id not in delta_ids and reparsed.texts[entry_id] != text:
            raise Wave08J02Error(f"j02 changed non-delta id {entry_id}")
    candidate = COMMON.recompress_wrapper(rebuilt_raw, stock.packed)
    _header, roundtrip = COMMON.decompress_wrapper(candidate)
    if roundtrip != rebuilt_raw or candidate[:8] != stock.packed[:8]:
        raise Wave08J02Error("j02 wrapper round-trip differs")
    return candidate, {
        "resource": RESOURCE,
        "baseline_applied_count": int(baseline_metrics["applied_count"]),
        "delta_applied_count": len(delta_ids),
        "total_common_applied_count": BASELINE_GLOBAL_APPLIED + len(delta_ids),
        "remaining_legacy_unresolved_count": LEGACY_UNRESOLVED - len(delta_ids),
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


def validation_model(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": VALIDATION_SCHEMA,
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "expected": {
            "candidate": metrics["candidate"],
            "baseline_candidate": metrics["baseline_candidate"],
            "overlay": metrics["overlay"],
            "triage": path_spec(TRIAGE_PATH),
        },
        "translation": {
            "delta_applied_count": len(EXPECTED_IDS),
            "total_common_applied_count": BASELINE_GLOBAL_APPLIED + len(EXPECTED_IDS),
            "remaining_legacy_unresolved_count": LEGACY_UNRESOLVED - len(EXPECTED_IDS),
        },
        "proofs": {
            "deterministic_ab_equal": True,
            "existing_v1_overlay_preserved": True,
            "id_domain_preserved": True,
            "non_delta_texts_preserved": True,
            "source_hashes_fail_closed": True,
            "wrapper_prefix_preserved": True,
        },
        "safety": {
            "complete_candidate_binary_tracked": False,
            "installed_game_files_modified": False,
            "sc_binary_used": False,
            "sc_coordinate_used": False,
        },
    }


def generate(stock_root: Path) -> dict[str, Any]:
    overlay = expected_overlay(stock_root)
    OVERLAY_PATH.parent.mkdir(parents=True, exist_ok=True)
    OVERLAY_PATH.write_bytes(COMMON.pretty_bytes(overlay))
    first, first_metrics = build_blob(stock_root)
    second, second_metrics = build_blob(stock_root)
    if first != second or first_metrics != second_metrics:
        raise Wave08J02Error("j02 deterministic A/B build differs")
    VALIDATION_PATH.write_bytes(COMMON.pretty_bytes(validation_model(first_metrics)))
    return {"status": "GENERATED", **first_metrics, "deterministic_ab_equal": True}


def verify(stock_root: Path) -> dict[str, Any]:
    first, first_metrics = build_blob(stock_root)
    second, second_metrics = build_blob(stock_root)
    if first != second or first_metrics != second_metrics:
        raise Wave08J02Error("j02 deterministic A/B build differs")
    validation, blob = COMMON.read_json(VALIDATION_PATH)
    expected = validation_model(first_metrics)
    if validation != expected or blob != COMMON.pretty_bytes(expected):
        raise Wave08J02Error("tracked j02 validation differs from deterministic model")
    return {"status": "PASS", **first_metrics, "deterministic_ab_equal": True}


def output_root(path: Path) -> Path:
    resolved = path.resolve()
    tmp = (REPO / "tmp").resolve()
    if resolved == tmp or tmp not in resolved.parents or resolved.exists():
        raise Wave08J02Error(f"unsafe or existing output root: {resolved}")
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("generate", "verify", "build"):
        child = subparsers.add_parser(command)
        child.add_argument("--stock-root", type=Path, default=DEFAULT_STOCK_ROOT)
        if command == "build":
            child.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()
    if args.command == "generate":
        result = generate(args.stock_root)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
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
