#!/usr/bin/env python3
"""Validate and assemble the five source-free Steam JP msggame wave07 overlays."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = SCRIPT.parents[2]
PARTITION = REPO / "workstreams" / "msggame_pk_jp_native_wave06" / "partition.v1.json"
VARIANTS = WORKSTREAM / "contextual_variants.v1.json"
RESOURCE = "MSG_PK/JP/msggame.bin"
EXPECTED_BATCH_COUNTS = {"j01": 970, "j02": 969, "j03": 761, "j04": 680, "j05": 681}
EXPECTED_TOTAL = 4_061
EXPECTED_COMPLETE = 28_272
DEFAULT_STOCK = Path(r"F:/SteamLibrary/steamapps/common/NOBU16/MSG_PK/JP/msggame.bin")
DEFAULT_BACKUP_STOCK = Path(
    r"F:/SteamLibrary/steamapps/common/NOBU16/KR_PATCH_BACKUP/file_only_transaction/"
    r"steam-jp-1.1.7-v0.6.0/originals/MSG_PK/JP/msggame.bin"
)


class IntegrationError(ValueError):
    pass


def load_steam_builder():
    path = REPO / "workstreams" / "steam_jp_msggame_v1" / "build_steam_jp_msggame_v1.py"
    spec = importlib.util.spec_from_file_location("nobu16_wave07_steam_builder", path)
    if spec is None or spec.loader is None:
        raise IntegrationError("cannot load Steam JP msggame builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


STEAM = load_steam_builder()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise IntegrationError(f"JSON root is not an object: {path}")
    return value


def overlay_path(batch_id: str) -> Path:
    public = REPO / "workstreams" / f"msggame_pk_jp_native_wave07_{batch_id}" / "public"
    matches = sorted(public.glob("*.json"))
    if len(matches) != 1:
        raise IntegrationError(f"{batch_id} must expose exactly one public overlay: {matches}")
    return matches[0]


def partition_coordinates() -> dict[str, set[tuple[int, int, int]]]:
    payload = read_json(PARTITION)
    if payload.get("base_language") != "JP" or payload.get("batch_count") != 5:
        raise IntegrationError("wave06 JP partition contract changed")
    result: dict[str, set[tuple[int, int, int]]] = {}
    for batch in payload.get("batches", []):
        batch_id = batch.get("batch_id")
        if batch_id not in EXPECTED_BATCH_COUNTS:
            raise IntegrationError(f"unexpected partition batch {batch_id!r}")
        coordinates = {tuple(item) for item in batch.get("coordinates", [])}
        if len(coordinates) != EXPECTED_BATCH_COUNTS[batch_id]:
            raise IntegrationError(f"partition count changed for {batch_id}")
        result[batch_id] = coordinates
    if set(result) != set(EXPECTED_BATCH_COUNTS):
        raise IntegrationError("partition does not contain exactly j01..j05")
    union = set().union(*result.values())
    if len(union) != EXPECTED_TOTAL or sum(map(len, result.values())) != EXPECTED_TOTAL:
        raise IntegrationError("partition batches overlap or do not cover 4,061 coordinates")
    return result


def allowed_variants() -> dict[str, dict[tuple[int, int, int], str]]:
    payload = read_json(VARIANTS)
    if payload.get("schema") != "nobu16.kr.msggame-jp-wave07-contextual-variants.v1":
        raise IntegrationError("unsupported contextual variant schema")
    if payload.get("source_text_free") is not True:
        raise IntegrationError("contextual variant review is not source-free")
    result: dict[str, dict[tuple[int, int, int], str]] = {}
    for entry in payload.get("entries", []):
        if set(entry) != {
            "source_jp_utf16le_sha256",
            "allowed_ko",
            "coordinate_variants",
            "reason",
        }:
            raise IntegrationError("contextual variant entry has unexpected fields")
        source_hash = entry["source_jp_utf16le_sha256"]
        values = entry["allowed_ko"]
        variants = entry["coordinate_variants"]
        if (
            not isinstance(source_hash, str)
            or len(source_hash) != 64
            or not isinstance(values, list)
            or len(values) < 2
            or len(values) != len(set(values))
            or not all(isinstance(value, str) for value in values)
            or not isinstance(variants, list)
            or len(variants) != len(values)
            or not isinstance(entry["reason"], str)
        ):
            raise IntegrationError("invalid contextual variant entry")
        if source_hash in result:
            raise IntegrationError("duplicate contextual variant source hash")
        coordinate_map: dict[tuple[int, int, int], str] = {}
        variant_values: set[str] = set()
        for variant in variants:
            if not isinstance(variant, dict) or set(variant) != {"coordinates", "ko"}:
                raise IntegrationError("invalid coordinate variant entry")
            korean = variant["ko"]
            coordinates = variant["coordinates"]
            if (
                korean not in values
                or korean in variant_values
                or not isinstance(coordinates, list)
                or not coordinates
            ):
                raise IntegrationError("invalid contextual coordinate variant")
            variant_values.add(korean)
            for coordinate in coordinates:
                if (
                    not isinstance(coordinate, list)
                    or len(coordinate) != 3
                    or any(
                        isinstance(item, bool) or not isinstance(item, int) or item < 0
                        for item in coordinate
                    )
                ):
                    raise IntegrationError("invalid contextual variant coordinate")
                key = tuple(coordinate)
                if key in coordinate_map:
                    raise IntegrationError("duplicate contextual variant coordinate")
                coordinate_map[key] = korean
        if variant_values != set(values):
            raise IntegrationError("allowed KO values and coordinate variants differ")
        result[source_hash] = coordinate_map
    return result


def validate_batches(stock_bytes: bytes) -> tuple[list[tuple[Path, str, int]], dict[str, Any]]:
    partition = partition_coordinates()
    stock = STEAM.stock_context(stock_bytes)
    overlay_specs: list[tuple[Path, str, int]] = []
    all_coordinates: set[tuple[int, int, int]] = set()
    by_source_hash: dict[str, dict[tuple[int, int, int], str]] = defaultdict(dict)
    rows: list[dict[str, Any]] = []
    for batch_id in EXPECTED_BATCH_COUNTS:
        path = overlay_path(batch_id)
        raw = path.read_bytes()
        payload = read_json(path)
        expected_count = EXPECTED_BATCH_COUNTS[batch_id]
        replacements, row = STEAM.load_overlay(path, None, expected_count, stock)
        if set(replacements) != partition[batch_id]:
            raise IntegrationError(f"{batch_id} overlay coordinates differ from partition")
        overlap = all_coordinates & set(replacements)
        if overlap:
            raise IntegrationError(f"wave07 overlays overlap at {sorted(overlap)[:3]}")
        all_coordinates.update(replacements)
        for entry in payload["entries"]:
            current = (entry["block_id"], entry["record_id"], entry["literal_id"])
            by_source_hash[entry["source_jp_utf16le_sha256"]][current] = entry["ko"]
        digest = sha256(raw)
        overlay_specs.append((path, digest, expected_count))
        rows.append({"batch_id": batch_id, **row})
    if len(all_coordinates) != EXPECTED_TOTAL:
        raise IntegrationError("wave07 union does not cover exactly 4,061 coordinates")

    observed_conflicts = {
        source_hash: coordinate_map
        for source_hash, coordinate_map in by_source_hash.items()
        if len(set(coordinate_map.values())) > 1
    }
    reviewed_conflicts = allowed_variants()
    if observed_conflicts != reviewed_conflicts:
        missing = sorted(set(observed_conflicts) - set(reviewed_conflicts))
        stale = sorted(set(reviewed_conflicts) - set(observed_conflicts))
        mismatched = sorted(
            key
            for key in set(observed_conflicts) & set(reviewed_conflicts)
            if observed_conflicts[key] != reviewed_conflicts[key]
        )
        raise IntegrationError(
            f"repeated JP source review mismatch: missing={missing}, stale={stale}, "
            f"mismatched={mismatched}"
        )
    return overlay_specs, {
        "overlay_rows": rows,
        "coordinate_count": len(all_coordinates),
        "unique_source_hash_count": len(by_source_hash),
        "contextual_variant_source_count": len(observed_conflicts),
        "coordinates_sha256": STEAM.coordinate_hash(all_coordinates),
    }


def resolve_stock(requested: Path | None) -> Path:
    candidates = [requested] if requested is not None else [DEFAULT_STOCK, DEFAULT_BACKUP_STOCK]
    for candidate in candidates:
        if candidate is None or not candidate.is_file():
            continue
        raw = candidate.read_bytes()
        if len(raw) == STEAM.STOCK_PIN["packed_size"] and sha256(raw) == STEAM.STOCK_PIN["packed_sha256"]:
            return candidate
    raise IntegrationError("exact Steam PK v1.1.7 JP stock msggame.bin was not found")


def build_complete(stock_path: Path) -> tuple[bytes, dict[str, Any], dict[str, Any]]:
    stock_bytes = stock_path.read_bytes()
    wave_specs, integration = validate_batches(stock_bytes)
    specs = [*STEAM.default_overlay_specs(), *wave_specs]
    first, first_manifest = STEAM.build_blob(
        stock_bytes,
        specs,
        expected_foundation=EXPECTED_COMPLETE,
        expected_remaining=0,
    )
    second, second_manifest = STEAM.build_blob(
        stock_bytes,
        specs,
        expected_foundation=EXPECTED_COMPLETE,
        expected_remaining=0,
    )
    if first != second or canonical_json(first_manifest) != canonical_json(second_manifest):
        raise IntegrationError("complete wave07 rebuild is not deterministic")
    if first_manifest["translation"] != {
        "applied_entry_count": EXPECTED_COMPLETE,
        "semantic_target_count": EXPECTED_COMPLETE,
        "remaining_jp_semantic_count": 0,
    }:
        raise IntegrationError("complete translation count contract failed")
    return first, first_manifest, integration


def command_check(args: argparse.Namespace) -> int:
    stock = resolve_stock(args.stock)
    candidate, manifest, integration = build_complete(stock)
    print(f"stock={stock}")
    print(f"wave07_entries={integration['coordinate_count']}")
    print(f"applied_entries={manifest['translation']['applied_entry_count']}")
    print(f"remaining_jp_semantic={manifest['translation']['remaining_jp_semantic_count']}")
    print(f"candidate_sha256={sha256(candidate)}")
    print("status=PASS")
    return 0


def command_build(args: argparse.Namespace) -> int:
    stock = resolve_stock(args.stock)
    candidate, manifest, integration = build_complete(stock)
    output = args.output.resolve()
    tmp_root = (REPO / "tmp").resolve()
    if output == tmp_root or tmp_root not in output.parents:
        raise IntegrationError("output must be below repository tmp")
    if output.exists() and any(output.iterdir()):
        raise IntegrationError("output directory must be absent or empty")
    candidate_path = output / "candidate" / RESOURCE
    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_path.write_bytes(candidate)
    (output / "build_manifest.json").write_bytes(canonical_json(manifest))
    (output / "integration_manifest.json").write_bytes(canonical_json(integration))
    print(f"candidate={candidate_path}")
    print(f"candidate_sha256={sha256(candidate)}")
    print("status=PASS")
    return 0


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    sub = value.add_subparsers(dest="command", required=True)
    for name, handler in (("check", command_check), ("build", command_build)):
        command = sub.add_parser(name)
        command.add_argument("--stock", type=Path)
        if name == "build":
            command.add_argument(
                "--output", type=Path, default=REPO / "tmp" / "msggame_wave07_complete"
            )
        command.set_defaults(handler=handler)
    return value


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        return int(args.handler(args))
    except (IntegrationError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
