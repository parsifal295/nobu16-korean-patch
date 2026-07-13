#!/usr/bin/env python3
"""Export a deterministic, source-text-free public MSGUI translation overlay.

Development batches may contain official English strings for translator review.
This exporter verifies those strings against the private catalog, then emits only
stable numeric ids, hashes of the stock SC strings, and project-owned Korean text.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Sequence

import msgui_catalog_v2 as catalog


LEGACY_SCHEMA = "nobu16.kr.translation.v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write((json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def load_batches(directory: Path) -> list[tuple[Path, dict[str, Any]]]:
    result: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted(directory.glob("*.json"), key=lambda item: item.name):
        value = json.loads(path.read_text(encoding="utf-8"))
        if value.get("schema") not in (catalog.BATCH_SCHEMA, LEGACY_SCHEMA):
            continue
        result.append((path, value))
    if not result:
        raise catalog.CatalogError("no supported translation batches found")
    return result


def export(args: argparse.Namespace) -> int:
    meta, rows = catalog.load_catalog(args.meta.resolve(), args.catalog.resolve())
    by_id = {int(row["id"]): row for row in rows}
    merged: dict[int, dict[str, Any]] = {}
    sources: list[dict[str, Any]] = []
    skipped_whitespace_total = 0

    for path, batch in load_batches(args.translations.resolve()):
        defaults = batch.get("defaults", {}) if batch.get("schema") == catalog.BATCH_SCHEMA else {}
        if not isinstance(defaults, dict):
            raise catalog.CatalogError(f"{path.name}: defaults must be an object")
        accepted = 0
        skipped_whitespace = 0
        for item in batch.get("entries", []):
            entry_id = int(item["id"])
            if args.max_id is not None and entry_id > args.max_id:
                continue
            if entry_id not in by_id:
                raise catalog.CatalogError(f"{path.name}: id {entry_id} outside catalog")
            row = by_id[entry_id]
            legacy_source = item.get("source")
            expected_source = item.get("source_en")
            if expected_source is None:
                expected_source = legacy_source.get("EN") if isinstance(legacy_source, dict) else legacy_source
            if expected_source is not None and expected_source != row["source"]["EN"]:
                raise catalog.CatalogError(f"{path.name}: id {entry_id} English source mismatch")
            if isinstance(legacy_source, dict) and legacy_source.get("SC") != row["source"]["SC"]:
                raise catalog.CatalogError(f"{path.name}: id {entry_id} SC source mismatch")
            supplied_hash = item.get("source_sc_utf16le_sha256")
            sc_hash = row["source_utf16le_sha256"]["SC"]
            if supplied_hash is not None and str(supplied_hash).upper() != sc_hash:
                raise catalog.CatalogError(f"{path.name}: id {entry_id} SC source hash mismatch")
            ko = item.get("ko")
            if not isinstance(ko, str) or "\x00" in ko:
                raise catalog.CatalogError(f"{path.name}: id {entry_id} invalid Korean text")
            status = item.get("status", defaults.get("status", "translated"))
            if status not in catalog.VALID_STATUSES:
                raise catalog.CatalogError(f"{path.name}: id {entry_id} invalid status")
            status, ko = catalog.canonical_translation_state(row["source"], status, ko)
            if not ko:
                overrides = item.get(
                    "invariant_overrides", defaults.get("invariant_overrides", [])
                )
                if overrides:
                    raise catalog.CatalogError(
                        f"{path.name}: id {entry_id} whitespace row cannot carry invariant overrides"
                    )
                skipped_whitespace += 1
                skipped_whitespace_total += 1
                continue
            if status not in catalog.BUILDABLE_STATUSES:
                raise catalog.CatalogError(f"{path.name}: id {entry_id} status is not buildable")
            overrides = item.get("invariant_overrides", defaults.get("invariant_overrides", []))
            if not isinstance(overrides, list) or not all(isinstance(value, str) for value in overrides):
                raise catalog.CatalogError(f"{path.name}: id {entry_id} invalid invariant overrides")
            problems = catalog.compare_invariants(
                row["source"]["SC"], ko, set(overrides), row["source"]
            )
            if problems:
                raise catalog.CatalogError(
                    f"{path.name}: id {entry_id} invariant mismatch: {'; '.join(problems)}"
                )
            public_item: dict[str, Any] = {
                "id": entry_id,
                "source_sc_utf16le_sha256": sc_hash,
                "ko": ko,
            }
            if status != "translated":
                public_item["status"] = status
            priority = item.get("priority", defaults.get("priority"))
            if priority:
                public_item["priority"] = str(priority)
            if overrides:
                public_item["invariant_overrides"] = overrides
            previous = merged.get(entry_id)
            if previous is not None and previous != public_item:
                raise catalog.CatalogError(f"conflicting duplicate translation for id {entry_id}")
            merged[entry_id] = public_item
            accepted += 1
        if accepted:
            sources.append(
                {
                    "file": path.name,
                    "sha256": sha256_file(path),
                    "accepted_entries": accepted,
                    "skipped_whitespace_entries": skipped_whitespace,
                }
            )

    stock_sc = meta["source_files"]["SC"]
    ordered = [merged[entry_id] for entry_id in sorted(merged)]
    overlay = {
        "schema": catalog.OVERLAY_SCHEMA,
        "overlay_id": args.overlay_id,
        "resource": "msgui",
        "base_language": "SC",
        "entry_count": len(ordered),
        "skipped_whitespace_entry_count": skipped_whitespace_total,
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
            "include_in_public_patch": True,
        },
        "stock_sc": {
            "packed_sha256": stock_sc["sha256"],
            "raw_sha256": stock_sc["raw_sha256"],
            "string_count": int(meta["string_count"]),
        },
        "defaults": {"status": "translated"},
        "development_batch_provenance": sources,
        "entries": ordered,
    }
    atomic_json(args.output.resolve(), overlay)
    output_sha = sha256_file(args.output.resolve())
    report = {
        "schema": "nobu16.kr.public-translation-overlay-export.v1",
        "overlay_id": args.overlay_id,
        "entry_count": len(ordered),
        "first_id": ordered[0]["id"] if ordered else None,
        "last_id": ordered[-1]["id"] if ordered else None,
        "output_sha256": output_sha,
        "contains_commercial_source_text": False,
        "source_batch_count": len(sources),
        "skipped_whitespace_entry_count": skipped_whitespace_total,
    }
    if args.report:
        atomic_json(args.report.resolve(), report)
    print(f"output={args.output.resolve()}")
    print(f"sha256={output_sha}")
    print(f"entries={len(ordered)}")
    print("contains_commercial_source_text=False")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--meta", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--translations", type=Path, required=True)
    parser.add_argument("--overlay-id", required=True)
    parser.add_argument("--max-id", type=int)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    try:
        return export(build_parser().parse_args(argv))
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError, catalog.CatalogError) as exc:
        print(f"ERROR: {exc}", file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
