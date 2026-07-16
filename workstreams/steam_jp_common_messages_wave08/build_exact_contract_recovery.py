#!/usr/bin/env python3
"""Validate and replay the 1,796 source-equal JP common-message contracts.

These coordinates were present in the completed tracked translation union and
map exactly through the v1 JP equal-hash blocks, but were omitted from the v1
overlay because their Korean value already equals the current JP value.  The
contract shards make that coverage explicit without changing candidate bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
COMMON_PATH = REPO / "workstreams" / "steam_jp_common_messages_v1" / "build_steam_jp_common_messages_v1.py"
SPEC = importlib.util.spec_from_file_location("steam_jp_common_exact_common", COMMON_PATH)
assert SPEC is not None and SPEC.loader is not None
COMMON = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = COMMON
SPEC.loader.exec_module(COMMON)


SCHEMA = "nobu16.kr.steam-jp-common-message-exact-contract.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-common-message-exact-recovery-validation.v1"
SOURCE_UNION_MANIFEST_SHA256 = "218C1FB47DCCDAE07A3B10C6664EAC2A0E426DA8733A46143BC6D92B8CF682B3"
PUBLIC_ROOT = HERE / "public" / "exact_contract"
EVIDENCE_PATH = HERE / "evidence" / "exact_contract_recovery.v1.json"
VALIDATION_PATH = HERE / "validation.exact_contract.v1.json"
DEFAULT_STOCK_ROOT = Path(
    "F:/SteamLibrary/steamapps/common/NOBU16/KR_PATCH_BACKUP/file_only_transaction/"
    "steam-jp-1.1.7-v0.6.0/originals"
)
SHARDS = (
    "msgev_exact_contract_83.v1.json",
    "msgdata_exact_contract_s01_286.v1.json",
    "msgdata_exact_contract_s02_286.v1.json",
    "msgdata_exact_contract_s03_286.v1.json",
    "msgdata_exact_contract_s04_285.v1.json",
    "msgdata_exact_contract_s05_285.v1.json",
    "msgdata_exact_contract_s06_285.v1.json",
)
EXPECTED_COUNTS = {"msgev.bin": 83, "msgdata.bin": 1713}
EXPECTED_SHARD_COUNTS = [83, 286, 286, 286, 285, 285, 285]


class ExactContractError(ValueError):
    pass


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def path_spec(path: Path) -> dict[str, Any]:
    return {"size": path.stat().st_size, "sha256": sha256(path.read_bytes())}


def _expand_groups(value: dict[str, Any]) -> list[dict[str, Any]]:
    groups = value.get("groups")
    if not isinstance(groups, list) or not groups:
        raise ExactContractError("group-encoded contract has no groups")
    rows: list[dict[str, Any]] = []
    for index, group in enumerate(groups):
        COMMON.exact_keys(group, {"ko", "ranges", "text_utf16le_sha256"}, f"groups[{index}]")
        ko = group["ko"]
        digest = COMMON.require_hash(group["text_utf16le_sha256"], "group text hash")
        if not isinstance(ko, str) or "\0" in ko or COMMON.text_hash(ko) != digest:
            raise ExactContractError(f"invalid group value at index {index}")
        ranges = group["ranges"]
        if not isinstance(ranges, list) or not ranges:
            raise ExactContractError(f"empty group ranges at index {index}")
        for span in ranges:
            if not isinstance(span, list) or len(span) != 3:
                raise ExactContractError(f"invalid group span at index {index}")
            old_start, current_start, length = (
                COMMON.require_int(span[0], "legacy start"),
                COMMON.require_int(span[1], "current start"),
                COMMON.require_int(span[2], "span length", 1),
            )
            rows.extend(
                {
                    "legacy_jp_id": old_start + offset,
                    "id": current_start + offset,
                    "ko": ko,
                    "text_hash": digest,
                }
                for offset in range(length)
            )
    return sorted(rows, key=lambda row: (row["legacy_jp_id"], row["id"]))


def _expand_indexed(value: dict[str, Any]) -> list[dict[str, Any]]:
    if value.get("encoding") != "indexed_value_table_v1":
        raise ExactContractError("unsupported indexed encoding")
    table = value.get("value_table")
    mappings = value.get("mappings")
    if not isinstance(table, list) or not table or not isinstance(mappings, list):
        raise ExactContractError("indexed contract table differs")
    values: list[tuple[str, str]] = []
    for index, item in enumerate(table):
        if not isinstance(item, list) or len(item) != 2:
            raise ExactContractError(f"invalid value table row {index}")
        ko, digest = item
        digest = COMMON.require_hash(digest, "indexed text hash")
        if not isinstance(ko, str) or "\0" in ko or COMMON.text_hash(ko) != digest:
            raise ExactContractError(f"invalid indexed value {index}")
        values.append((ko, digest))
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(mappings):
        if not isinstance(item, list) or len(item) != 3:
            raise ExactContractError(f"invalid mapping row {index}")
        old_id = COMMON.require_int(item[0], "legacy id")
        current_id = COMMON.require_int(item[1], "current id")
        value_id = COMMON.require_int(item[2], "value id")
        if value_id >= len(values):
            raise ExactContractError(f"value id is outside table at mapping {index}")
        ko, digest = values[value_id]
        rows.append({"legacy_jp_id": old_id, "id": current_id, "ko": ko, "text_hash": digest})
    return rows


def expand_contract(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], bytes]:
    value, blob = COMMON.read_json(path)
    common_keys = {
        "schema", "overlay_id", "resource", "base_language", "distribution_policy",
        "stock_jp", "provenance", "entry_count", "equal_hash_blocks_sha256",
        "ids_sha256", "mapping_rows_sha256", "source_rows_sha256", "shard",
    }
    if "groups" in value:
        COMMON.exact_keys(value, common_keys | {"groups"}, path.name)
        rows = _expand_groups(value)
    else:
        COMMON.exact_keys(value, common_keys | {"encoding", "mappings", "value_table"}, path.name)
        rows = _expand_indexed(value)
    if value["schema"] != SCHEMA or value["base_language"] != "JP":
        raise ExactContractError(f"contract identity differs: {path.name}")
    if value["distribution_policy"] != {
        "contains_commercial_source_text": False,
        "contains_complete_game_resource": False,
    }:
        raise ExactContractError(f"contract distribution policy differs: {path.name}")
    resource = value["resource"]
    if resource not in {"MSG_PK/JP/msgev.bin", "MSG_PK/JP/msgdata.bin"}:
        raise ExactContractError(f"unsupported contract resource: {resource}")
    name = Path(resource).name
    if value["stock_jp"] != COMMON.pin_public(COMMON.STEAM_PINS[name]):
        raise ExactContractError(f"contract stock pin differs: {path.name}")
    if value["entry_count"] != len(rows):
        raise ExactContractError(f"contract entry count differs: {path.name}")
    ids = [row["id"] for row in rows]
    mappings = [{"id": row["id"], "legacy_jp_id": row["legacy_jp_id"]} for row in rows]
    source_rows = [
        {"id": row["id"], "source_jp_utf16le_sha256": row["text_hash"]}
        for row in rows
    ]
    if ids != sorted(set(ids)) or COMMON.canonical_hash(ids) != value["ids_sha256"]:
        raise ExactContractError(f"contract ID vector differs: {path.name}")
    if COMMON.canonical_hash(mappings) != value["mapping_rows_sha256"]:
        raise ExactContractError(f"contract mapping vector differs: {path.name}")
    if COMMON.canonical_hash(source_rows) != value["source_rows_sha256"]:
        raise ExactContractError(f"contract source vector differs: {path.name}")
    provenance = value["provenance"]
    if (
        provenance.get("source_union_manifest_sha256") != SOURCE_UNION_MANIFEST_SHA256
        or provenance.get("source_union_values_equal_current_jp") is not True
        or provenance.get("sc_binary_used") is not False
    ):
        raise ExactContractError(f"contract provenance differs: {path.name}")
    base_path = REPO / provenance["existing_v1_overlay_path"]
    if path_spec(base_path)["sha256"] != provenance["existing_v1_overlay_sha256"]:
        raise ExactContractError(f"existing v1 overlay pin differs: {path.name}")
    base_value, _base_blob = COMMON.read_json(base_path)
    if COMMON.canonical_hash(base_value["equal_hash_blocks"]) != value["equal_hash_blocks_sha256"]:
        raise ExactContractError(f"equal-hash block pin differs: {path.name}")
    return value, rows, blob


def load_contracts() -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
    artifacts: list[dict[str, Any]] = []
    counts: list[int] = []
    all_coordinates: set[tuple[str, int]] = set()
    for filename in SHARDS:
        path = PUBLIC_ROOT / filename
        value, rows, blob = expand_contract(path)
        name = Path(value["resource"]).name
        counts.append(len(rows))
        for row in rows:
            coordinate = (name, row["id"])
            if coordinate in all_coordinates:
                raise ExactContractError(f"duplicate current coordinate: {coordinate}")
            all_coordinates.add(coordinate)
        by_name[name].extend(rows)
        artifacts.append({
            "path": path.relative_to(REPO).as_posix(),
            "size": len(blob),
            "sha256": sha256(blob),
            "entry_count": len(rows),
            "resource": value["resource"],
        })
    if counts != EXPECTED_SHARD_COUNTS:
        raise ExactContractError(f"shard count vector differs: {counts}")
    if {name: len(rows) for name, rows in by_name.items()} != EXPECTED_COUNTS:
        raise ExactContractError("resource contract totals differ")
    return dict(by_name), artifacts


def verify_stock(stock_root: Path) -> dict[str, Any]:
    contracts, artifacts = load_contracts()
    base_overlays, _base_blobs = COMMON.load_public_overlays()
    resources: dict[str, Any] = {}
    combined_coordinates: list[dict[str, Any]] = []
    for name in ("msgev.bin", "msgdata.bin"):
        rows = contracts[name]
        stock = COMMON.load_pinned(
            stock_root / "MSG_PK" / "JP" / name,
            COMMON.STEAM_PINS[name],
            f"Steam 1.1.7 pristine JP {name}",
        )
        baseline, baseline_metrics = COMMON.build_one(name, stock, base_overlays[name])
        _header, baseline_raw = COMMON.decompress_wrapper(baseline)
        table = COMMON.parse_message_table(baseline_raw)
        existing_ids = {int(entry["id"]) for entry in base_overlays[name]["entries"]}
        blocks = base_overlays[name]["equal_hash_blocks"]
        texts = list(table.texts)
        for row in rows:
            old_id, current_id = row["legacy_jp_id"], row["id"]
            hits = [
                block for block in blocks
                if block["legacy_start_id"] <= old_id < block["legacy_start_id"] + block["length"]
            ]
            if len(hits) != 1:
                raise ExactContractError(f"{name}: legacy id {old_id} has no unique equal block")
            block = hits[0]
            mapped = block["steam_start_id"] + old_id - block["legacy_start_id"]
            if mapped != current_id:
                raise ExactContractError(f"{name}: mapping differs at legacy id {old_id}")
            if current_id in existing_ids:
                raise ExactContractError(f"{name}: contract overlaps v1 at id {current_id}")
            source = stock.table.texts[current_id]
            if COMMON.text_hash(source) != row["text_hash"] or source != row["ko"]:
                raise ExactContractError(f"{name}: source-equal contract differs at id {current_id}")
            if COMMON.common.invariant_mismatches(source, row["ko"]):
                raise ExactContractError(f"{name}: invariant differs at id {current_id}")
            if texts[current_id] != source:
                raise ExactContractError(f"{name}: contract overlaps baseline candidate at id {current_id}")
            texts[current_id] = row["ko"]
            combined_coordinates.append({"resource": f"MSG_PK/JP/{name}", "id": current_id})
        rebuilt_raw = COMMON.rebuild_message_table(stock.table, texts)
        candidate = COMMON.recompress_wrapper(rebuilt_raw, stock.packed)
        if candidate != baseline or rebuilt_raw != baseline_raw:
            raise ExactContractError(f"{name}: exact contracts unexpectedly changed candidate bytes")
        resources[name] = {
            "existing_v1_entry_count": int(baseline_metrics["applied_count"]),
            "exact_contract_entry_count": len(rows),
            "contract_coverage_count": int(baseline_metrics["applied_count"]) + len(rows),
            "existing_v1_overlap_count": 0,
            "candidate_byte_change_count": 0,
            "candidate": {"size": len(candidate), "sha256": sha256(candidate)},
        }
    combined_coordinates.sort(key=lambda row: (row["resource"], row["id"]))
    return {
        "status": "PASS",
        "exact_contract_entry_count": sum(EXPECTED_COUNTS.values()),
        "total_common_contract_coverage_count": 39_507 + sum(EXPECTED_COUNTS.values()),
        "effective_korean_change_count": 39_507,
        "coordinates_sha256": COMMON.canonical_hash(combined_coordinates),
        "resources": resources,
        "artifacts": artifacts,
        "proofs": {
            "existing_v1_overlap_zero": True,
            "equal_hash_block_mapping_exact": True,
            "current_jp_source_hash_exact": True,
            "format_invariants_exact": True,
            "source_union_values_equal_current_jp": True,
            "candidate_bytes_unchanged": True,
            "sc_binary_used": False,
        },
    }


def _target_union_entries(source_resource: str) -> dict[int, Any]:
    """Load only tracked source-free overlay JSON for one audit resource."""
    route_path = REPO / "workstreams" / "jp_pk_message_route_audit_v1" / "build_jp_pk_message_route_audit_v1.py"
    spec = importlib.util.spec_from_file_location("steam_jp_common_exact_route_audit", route_path)
    assert spec is not None and spec.loader is not None
    route = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = route
    spec.loader.exec_module(route)
    progress, _blob = route.read_json(route.DEFAULT_PROGRESS)
    progress_row = next(
        row for row in progress["resources"] + progress["shared_strings"]
        if row.get("path") == source_resource
    )
    ordered: list[str] = []
    for pattern in progress_row["overlay_globs"]:
        for path in sorted(route.REPO_ROOT.glob(pattern), key=lambda item: item.as_posix().casefold()):
            relative = path.relative_to(route.REPO_ROOT).as_posix()
            if relative not in ordered:
                ordered.append(relative)
    for relative in route.SUPPLEMENTAL_OVERLAYS.get(source_resource, ()):
        if relative not in ordered:
            ordered.append(relative)
    effective: dict[int, Any] = {}
    previous_kind: dict[int, str] = {}
    for relative in ordered:
        path = route.safe_repo_file(relative)
        value, blob = route.read_json(path)
        overlay = route.OverlayFile(source_resource, relative, path, blob, value)
        rows = route.normalize_common_file(overlay)
        kind = "geographic" if value.get("schema") in {route.full.CASTLE_SCHEMA, route.full.PROVINCE_SCHEMA} else "common"
        for row in rows:
            coordinate = int(row.coordinate)
            allowed = (
                source_resource.endswith("msgdata.bin")
                and coordinate in effective
                and previous_kind[coordinate] == "common"
                and kind == "geographic"
            )
            if coordinate in effective and not allowed:
                raise ExactContractError(f"unapproved tracked union duplicate: {coordinate}")
            effective[coordinate] = row
            previous_kind[coordinate] = kind
    return effective


def audit_source_union() -> dict[str, Any]:
    contracts, _artifacts = load_contracts()
    source_by_name = {
        "msgev.bin": "MSG_PK/SC/msgev.bin",
        "msgdata.bin": "MSG_PK/SC/msgdata.bin",
    }
    audited = 0
    for name, rows in contracts.items():
        union = _target_union_entries(source_by_name[name])
        for filename in SHARDS:
            value, shard_rows, _blob = expand_contract(PUBLIC_ROOT / filename)
            if Path(value["resource"]).name != name:
                continue
            ko_rows = []
            for row in shard_rows:
                source_entry = union[row["legacy_jp_id"]]
                digest = COMMON.text_hash(source_entry.ko)
                if digest != row["text_hash"] or source_entry.ko != row["ko"]:
                    raise ExactContractError(
                        f"tracked union KO differs: {name}:{row['legacy_jp_id']}"
                    )
                ko_rows.append({
                    "ko_utf16le_sha256": digest,
                    "legacy_jp_id": row["legacy_jp_id"],
                })
                audited += 1
            if COMMON.canonical_hash(ko_rows) != value["provenance"]["source_union_ko_rows_sha256"]:
                raise ExactContractError(f"tracked union KO vector differs: {filename}")
    if audited != 1796:
        raise ExactContractError(f"tracked union audit count differs: {audited}")
    return {"status": "PASS", "audited_entry_count": audited, "source_binary_used": False}


def verify(stock_root: Path, include_union_audit: bool = False) -> dict[str, Any]:
    first = verify_stock(stock_root)
    second_contracts, second_artifacts = load_contracts()
    if (
        {name: len(rows) for name, rows in second_contracts.items()} != EXPECTED_COUNTS
        or second_artifacts != first["artifacts"]
    ):
        raise ExactContractError("deterministic contract reload differs")
    validation, _blob = COMMON.read_json(VALIDATION_PATH)
    if validation.get("schema") != VALIDATION_SCHEMA:
        raise ExactContractError("validation schema differs")
    projection = {
        "exact_contract_entry_count": first["exact_contract_entry_count"],
        "total_common_contract_coverage_count": first["total_common_contract_coverage_count"],
        "effective_korean_change_count": first["effective_korean_change_count"],
        "coordinates_sha256": first["coordinates_sha256"],
        "resources": first["resources"],
        "artifacts": first["artifacts"],
        "proofs": first["proofs"],
        "evidence": path_spec(EVIDENCE_PATH),
    }
    if projection != validation.get("expected"):
        raise ExactContractError("tracked validation projection differs")
    result = {**first, "deterministic_ab_equal": True}
    if include_union_audit:
        result["source_union_audit"] = audit_source_union()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "audit-source-union"))
    parser.add_argument("--stock-root", type=Path, default=DEFAULT_STOCK_ROOT)
    args = parser.parse_args()
    result = (
        audit_source_union()
        if args.command == "audit-source-union"
        else verify(args.stock_root)
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
