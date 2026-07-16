#!/usr/bin/env python3
"""Build Steam-JP wave08 batches j06-j09 (19 semantic entries)."""

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


def import_file(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


COMMON = import_file(
    "steam_jp_common_messages_wave08_j06_j09_common",
    REPO
    / "workstreams"
    / "steam_jp_common_messages_v1"
    / "build_steam_jp_common_messages_v1.py",
)
TEXT = import_file(
    "steam_jp_common_messages_wave08_j06_j09_text",
    HERE / "translations_j06_j09.py",
)


SCHEMA = "nobu16.kr.steam-jp-common-message-wave08-delta.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-common-message-wave08-j06-j09-validation.v1"
TRIAGE_PATH = HERE / "triage.v1.json"
VALIDATION_PATH = HERE / "validation.j06_j09.v1.json"
DEFAULT_STOCK_ROOT = Path(
    "F:/SteamLibrary/steamapps/common/NOBU16/KR_PATCH_BACKUP/file_only_transaction/"
    "steam-jp-1.1.7-v0.6.0/originals"
)
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / "steam_jp_common_messages_wave08_j06_j09_candidate"
BASELINE_GLOBAL_APPLIED = 39_507
LEGACY_UNRESOLVED = 96

BATCHES: tuple[dict[str, Any], ...] = (
    {
        "batch_id": "j06_msgdata_legend_names",
        "resource": "MSG_PK/JP/msgdata.bin",
        "name": "msgdata.bin",
        "ids": list(range(26_619, 26_625)),
        "legacy_ids": list(range(26_611, 26_617)),
        "translations": TEXT.J06_MSGDATA_LEGEND_NAMES,
        "action": "translate",
        "resolution": "new_current_semantic_legend_name_translation",
        "overlay_id": "msgdata_ko_steam_jp_wave08_j06_legend_names_6.v1",
        "overlay_path": HERE
        / "public"
        / "msgdata_ko_steam_jp_wave08_j06_legend_names_6.v1.json",
    },
    {
        "batch_id": "j07_msgdata_legend_reading_keys",
        "resource": "MSG_PK/JP/msgdata.bin",
        "name": "msgdata.bin",
        "ids": list(range(26_875, 26_881)),
        "legacy_ids": list(range(26_867, 26_873)),
        "translations": TEXT.J07_MSGDATA_LEGEND_READING_KEYS,
        "action": "translate_as_korean_search_keys",
        "resolution": "new_current_semantic_korean_search_key_translation",
        "overlay_id": "msgdata_ko_steam_jp_wave08_j07_legend_reading_keys_6.v1",
        "overlay_path": HERE
        / "public"
        / "msgdata_ko_steam_jp_wave08_j07_legend_reading_keys_6.v1.json",
    },
    {
        "batch_id": "j08_msgdata_legend_descriptions",
        "resource": "MSG_PK/JP/msgdata.bin",
        "name": "msgdata.bin",
        "ids": list(range(27_131, 27_137)),
        "legacy_ids": list(range(27_123, 27_129)),
        "translations": TEXT.J08_MSGDATA_LEGEND_DESCRIPTIONS,
        "action": "translate",
        "resolution": "new_current_semantic_legend_description_translation",
        "overlay_id": "msgdata_ko_steam_jp_wave08_j08_legend_descriptions_6.v1",
        "overlay_path": HERE
        / "public"
        / "msgdata_ko_steam_jp_wave08_j08_legend_descriptions_6.v1.json",
    },
    {
        "batch_id": "j09_msgstf_credit_update",
        "resource": "MSG_PK/JP/msgstf.bin",
        "name": "msgstf.bin",
        "ids": [7],
        "legacy_ids": [7],
        "translations": TEXT.J09_MSGSTF_CREDIT_UPDATE,
        "action": "update_existing_credit_translation",
        "resolution": "current_credit_roster_revision_translation",
        "overlay_id": "msgstf_ko_steam_jp_wave08_j09_credit_update_1.v1",
        "overlay_path": HERE
        / "public"
        / "msgstf_ko_steam_jp_wave08_j09_credit_update_1.v1.json",
    },
)


class Wave08J06J09Error(ValueError):
    """A j06-j09 source, translation, structure, or output contract differed."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def path_spec(path: Path) -> dict[str, Any]:
    blob = path.read_bytes()
    return {"size": len(blob), "sha256": sha256(blob)}


def triage_batches() -> dict[str, dict[str, Any]]:
    triage, _blob = COMMON.read_json(TRIAGE_PATH)
    rows = {row.get("batch_id"): row for row in triage.get("batches", [])}
    result: dict[str, dict[str, Any]] = {}
    for spec in BATCHES:
        batch_id = spec["batch_id"]
        row = rows.get(batch_id)
        if not isinstance(row, dict):
            raise Wave08J06J09Error(f"triage batch is absent: {batch_id}")
        expected = {
            "resource": spec["resource"],
            "current_ids": spec["ids"],
            "legacy_ids": spec["legacy_ids"],
            "semantic_entry_count": len(spec["ids"]),
            "translation_action": spec["action"],
            "current_ids_sha256": COMMON.canonical_hash(spec["ids"]),
        }
        for key, value in expected.items():
            if row.get(key) != value:
                raise Wave08J06J09Error(f"{batch_id} triage {key} differs")
        if set(spec["translations"]) != set(spec["ids"]):
            raise Wave08J06J09Error(f"{batch_id} translation ID domain differs")
        result[batch_id] = row
    return result


def expected_overlay(spec: dict[str, Any], stock_root: Path) -> dict[str, Any]:
    batch = triage_batches()[spec["batch_id"]]
    stock = COMMON.load_pinned(
        stock_root / Path(spec["resource"]),
        COMMON.STEAM_PINS[spec["name"]],
        f"Steam 1.1.7 pristine JP {spec['name']}",
    )
    entries: list[dict[str, Any]] = []
    source_rows: list[dict[str, Any]] = []
    for legacy_id, entry_id in zip(spec["legacy_ids"], spec["ids"], strict=True):
        source = stock.table.texts[entry_id]
        korean = spec["translations"][entry_id]
        mismatches = COMMON.common.invariant_mismatches(source, korean)
        if mismatches:
            raise Wave08J06J09Error(
                f"{spec['batch_id']} invariant mismatch at {entry_id}: {mismatches}"
            )
        source_hash = COMMON.text_hash(source)
        source_rows.append({"id": entry_id, "source_jp_utf16le_sha256": source_hash})
        entries.append(
            {
                "id": entry_id,
                "recovered_legacy_jp_id": legacy_id,
                "source_jp_utf16le_sha256": source_hash,
                "ko": korean,
                "ko_utf16le_sha256": COMMON.text_hash(korean),
                "resolution": spec["resolution"],
            }
        )
    source_rows_hash = COMMON.canonical_hash(source_rows)
    if source_rows_hash != batch["source_rows_sha256"]:
        raise Wave08J06J09Error(f"{spec['batch_id']} source row vector differs")
    return {
        "schema": SCHEMA,
        "overlay_id": spec["overlay_id"],
        "resource": spec["resource"],
        "base_language": "JP",
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_jp": COMMON.pin_public(COMMON.STEAM_PINS[spec["name"]]),
        "provenance": {
            "batch_id": spec["batch_id"],
            "mapping_method": "manual_current_steam_jp_semantic_translation",
            "resolved_previous_unmapped_count": len(spec["ids"]),
            "existing_v1_overlay_preserved": True,
            "official_multilingual_reference_is_build_dependency": False,
            "sc_binary_used": False,
            "sc_coordinate_used": False,
        },
        "entry_count": len(entries),
        "ids_sha256": batch["current_ids_sha256"],
        "source_rows_sha256": source_rows_hash,
        "entries": entries,
    }


def load_overlays(stock_root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, bytes]]:
    values: dict[str, dict[str, Any]] = {}
    blobs: dict[str, bytes] = {}
    for spec in BATCHES:
        value, blob = COMMON.read_json(spec["overlay_path"])
        expected = expected_overlay(spec, stock_root)
        if value != expected or blob != COMMON.pretty_bytes(expected):
            raise Wave08J06J09Error(f"tracked overlay differs: {spec['batch_id']}")
        values[spec["batch_id"]] = value
        blobs[spec["batch_id"]] = blob
    return values, blobs


def build_candidates(stock_root: Path) -> tuple[dict[str, bytes], dict[str, Any]]:
    overlays, overlay_blobs = load_overlays(stock_root)
    base_overlays, _base_blobs = COMMON.load_public_overlays()
    candidates: dict[str, bytes] = {}
    resource_metrics: list[dict[str, Any]] = []
    for name in ("msgdata.bin", "msgstf.bin"):
        related = [spec for spec in BATCHES if spec["name"] == name]
        resource = related[0]["resource"]
        stock = COMMON.load_pinned(
            stock_root / Path(resource),
            COMMON.STEAM_PINS[name],
            f"Steam 1.1.7 pristine JP {name}",
        )
        baseline, baseline_metrics = COMMON.build_one(name, stock, base_overlays[name])
        _prefix, baseline_raw = COMMON.decompress_wrapper(baseline)
        baseline_table = COMMON.parse_message_table(baseline_raw)
        texts = list(baseline_table.texts)
        delta_ids: set[int] = set()
        for spec in related:
            for entry in overlays[spec["batch_id"]]["entries"]:
                entry_id = int(entry["id"])
                source = stock.table.texts[entry_id]
                if COMMON.text_hash(source) != entry["source_jp_utf16le_sha256"]:
                    raise Wave08J06J09Error(f"JP source hash differs: {name}:{entry_id}")
                if texts[entry_id] != source:
                    raise Wave08J06J09Error(f"ID overlaps v1 overlay: {name}:{entry_id}")
                if entry_id in delta_ids:
                    raise Wave08J06J09Error(f"duplicate delta ID: {name}:{entry_id}")
                texts[entry_id] = entry["ko"]
                delta_ids.add(entry_id)

        rebuilt_raw = COMMON.rebuild_message_table(stock.table, texts)
        reparsed = COMMON.parse_message_table(rebuilt_raw)
        if reparsed.texts != tuple(texts):
            raise Wave08J06J09Error(f"rebuilt table differs: {name}")
        if not COMMON._opaque_structure_preserved(stock.table, reparsed, rebuilt_raw):
            raise Wave08J06J09Error(f"opaque structure differs: {name}")
        for entry_id, text in enumerate(baseline_table.texts):
            if entry_id not in delta_ids and reparsed.texts[entry_id] != text:
                raise Wave08J06J09Error(f"non-delta text changed: {name}:{entry_id}")
        candidate = COMMON.recompress_wrapper(rebuilt_raw, stock.packed)
        _header, roundtrip = COMMON.decompress_wrapper(candidate)
        if roundtrip != rebuilt_raw or candidate[:8] != stock.packed[:8]:
            raise Wave08J06J09Error(f"wrapper round-trip differs: {name}")
        candidates[name] = candidate
        resource_metrics.append(
            {
                "resource": resource,
                "baseline_applied_count": int(baseline_metrics["applied_count"]),
                "delta_applied_count": len(delta_ids),
                "candidate": {
                    "size": len(candidate),
                    "sha256": sha256(candidate),
                    "raw_size": len(rebuilt_raw),
                    "raw_sha256": sha256(rebuilt_raw),
                },
                "baseline_candidate": {
                    "size": len(baseline),
                    "sha256": sha256(baseline),
                },
                "id_domain_preserved": True,
                "non_delta_texts_preserved": True,
                "wrapper_prefix_preserved": True,
            }
        )
    delta_count = sum(row["delta_applied_count"] for row in resource_metrics)
    return candidates, {
        "resources": resource_metrics,
        "overlays": {
            batch_id: {"size": len(blob), "sha256": sha256(blob)}
            for batch_id, blob in sorted(overlay_blobs.items())
        },
        "delta_applied_count": delta_count,
        "total_common_applied_count": BASELINE_GLOBAL_APPLIED + delta_count,
        "remaining_legacy_unresolved_count": LEGACY_UNRESOLVED - delta_count,
        "sc_binary_used": False,
        "sc_coordinate_used": False,
    }


def validation_model(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": VALIDATION_SCHEMA,
        "batch_ids": [spec["batch_id"] for spec in BATCHES],
        "resources": [spec["resource"] for spec in BATCHES],
        "expected": {
            "resources": metrics["resources"],
            "overlays": metrics["overlays"],
            "triage": path_spec(TRIAGE_PATH),
        },
        "translation": {
            "delta_applied_count": 19,
            "total_common_applied_count": 39_526,
            "remaining_legacy_unresolved_count": 77,
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
            "complete_candidate_binaries_tracked": False,
            "installed_game_files_modified": False,
            "official_multilingual_reference_is_build_dependency": False,
            "sc_binary_used": False,
            "sc_coordinate_used": False,
        },
    }


def generate(stock_root: Path) -> dict[str, Any]:
    for spec in BATCHES:
        spec["overlay_path"].parent.mkdir(parents=True, exist_ok=True)
        spec["overlay_path"].write_bytes(COMMON.pretty_bytes(expected_overlay(spec, stock_root)))
    first, first_metrics = build_candidates(stock_root)
    second, second_metrics = build_candidates(stock_root)
    if first != second or first_metrics != second_metrics:
        raise Wave08J06J09Error("deterministic A/B build differs")
    VALIDATION_PATH.write_bytes(COMMON.pretty_bytes(validation_model(first_metrics)))
    return {"status": "GENERATED", **first_metrics, "deterministic_ab_equal": True}


def verify(stock_root: Path) -> dict[str, Any]:
    first, first_metrics = build_candidates(stock_root)
    second, second_metrics = build_candidates(stock_root)
    if first != second or first_metrics != second_metrics:
        raise Wave08J06J09Error("deterministic A/B build differs")
    validation, blob = COMMON.read_json(VALIDATION_PATH)
    expected = validation_model(first_metrics)
    if validation != expected or blob != COMMON.pretty_bytes(expected):
        raise Wave08J06J09Error("tracked validation differs from deterministic model")
    return {"status": "PASS", **first_metrics, "deterministic_ab_equal": True}


def output_root(path: Path) -> Path:
    resolved = path.resolve()
    tmp = (REPO / "tmp").resolve()
    if resolved == tmp or tmp not in resolved.parents or resolved.exists():
        raise Wave08J06J09Error(f"unsafe or existing output root: {resolved}")
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
        print(json.dumps(generate(args.stock_root), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.command == "verify":
        print(json.dumps(verify(args.stock_root), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    candidates, metrics = build_candidates(args.stock_root)
    destination = output_root(args.output_root)
    try:
        for name, candidate in candidates.items():
            target = destination / "MSG_PK" / "JP" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(candidate)
        (destination / "private_manifest.json").write_bytes(COMMON.pretty_bytes(metrics))
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
