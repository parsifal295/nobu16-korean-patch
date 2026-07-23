#!/usr/bin/env python3
"""Compose every validated DLC translation wave into one complete overlay."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
DEFAULT_CATALOG = WORKSTREAM / "private" / "catalog.private.v1.json"
DEFAULT_OUTPUT = WORKSTREAM / "translations.integrated.v1.json"

OVERLAY_SCHEMA = "nobu16.kr.dlc-translation-overlay.v1"
INTEGRATED_SCHEMA = "nobu16.kr.dlc-translation-overlay.v1"


class IntegrationError(ValueError):
    """Raised when translation waves cannot form one exact full overlay."""


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise IntegrationError(f"JSON root must be an object: {path}")
    return value


def selected_placement_ids(
    catalog: dict[str, Any], overlay: dict[str, Any]
) -> set[str]:
    scope = overlay.get("scope")
    entries = overlay.get("entries")
    if not isinstance(scope, dict) or not isinstance(entries, list):
        raise IntegrationError("overlay must contain scope and entries")
    source_ids = {
        entry.get("source_id")
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("source_id"), str)
    }
    if len(source_ids) != len(entries):
        raise IntegrationError("overlay contains malformed or duplicate entries")

    if "placement_ids" in scope:
        values = scope["placement_ids"]
        if not isinstance(values, list) or not all(
            isinstance(value, str) for value in values
        ):
            raise IntegrationError("scope.placement_ids must be a string array")
        if len(values) != len(set(values)):
            raise IntegrationError("scope.placement_ids contains duplicates")
        return set(values)

    if "path_regex" in scope:
        pattern = scope["path_regex"]
        if not isinstance(pattern, str):
            raise IntegrationError("scope.path_regex must be a string")
        matcher = re.compile(pattern)
        return {
            placement["placement_id"]
            for placement in catalog["placements"]
            if matcher.search(placement["path"])
            and placement["source_id"] in source_ids
        }

    raise IntegrationError("unsupported overlay scope")


def build_integrated_overlay(catalog: dict[str, Any]) -> dict[str, Any]:
    wave_paths = sorted(WORKSTREAM.glob("translations.wave*.v1.json"))
    if not wave_paths:
        raise IntegrationError("no translation wave overlays found")

    catalog_placements = {
        placement["placement_id"]: placement for placement in catalog["placements"]
    }
    catalog_sources = {
        source["source_id"]: source for source in catalog["sources"]
    }
    placement_owner: dict[str, str] = {}
    translations: dict[str, str] = {}
    translation_owner: dict[str, str] = {}
    provenance: list[dict[str, Any]] = []

    for path in wave_paths:
        overlay = read_json(path)
        if overlay.get("schema") != OVERLAY_SCHEMA:
            raise IntegrationError(f"unexpected overlay schema: {path}")
        wave = overlay.get("wave")
        if not isinstance(wave, str) or not wave:
            raise IntegrationError(f"wave name is missing: {path}")
        selected = selected_placement_ids(catalog, overlay)
        unknown_placements = selected - set(catalog_placements)
        if unknown_placements:
            raise IntegrationError(
                f"unknown placements in {path}: {sorted(unknown_placements)}"
            )
        for placement_id in selected:
            prior = placement_owner.get(placement_id)
            if prior is not None:
                raise IntegrationError(
                    f"placement selected by multiple waves: {placement_id}: "
                    f"{prior}, {wave}"
                )
            placement_owner[placement_id] = wave

        entries = overlay["entries"]
        for entry in entries:
            source_id = entry["source_id"]
            korean = entry["ko"]
            if source_id not in catalog_sources:
                raise IntegrationError(f"unknown source_id in {path}: {source_id}")
            if not isinstance(korean, str) or not korean:
                raise IntegrationError(f"empty Korean translation in {path}: {source_id}")
            prior = translations.get(source_id)
            if prior is not None and prior != korean:
                raise IntegrationError(
                    f"conflicting Korean for {source_id}: "
                    f"{translation_owner[source_id]}, {wave}"
                )
            translations[source_id] = korean
            translation_owner.setdefault(source_id, wave)

        provenance.append(
            {
                "path": path.relative_to(WORKSTREAM).as_posix(),
                "sha256": sha256(path.read_bytes()),
                "target_placements": len(selected),
                "unique_sources": len({
                    catalog_placements[placement_id]["source_id"]
                    for placement_id in selected
                }),
                "wave": wave,
            }
        )

    missing_placements = set(catalog_placements) - set(placement_owner)
    if missing_placements:
        raise IntegrationError(
            f"integrated coverage is incomplete: {sorted(missing_placements)}"
        )
    if len(placement_owner) != len(catalog_placements):
        raise IntegrationError("integrated placement coverage count differs")

    selected_source_ids = {
        placement["source_id"] for placement in catalog["placements"]
    }
    missing_sources = selected_source_ids - set(translations)
    extra_sources = set(translations) - selected_source_ids
    if missing_sources or extra_sources:
        raise IntegrationError(
            f"integrated source coverage differs: "
            f"missing={sorted(missing_sources)}, extra={sorted(extra_sources)}"
        )

    return {
        "schema": INTEGRATED_SCHEMA,
        "wave": "integrated_dlc_translation_v1",
        "status": "complete_static_validation_pending_runtime_qa",
        "scope": {"placement_ids": sorted(placement_owner)},
        "policy": {
            "base_language": "JP",
            "crosscheck_languages": ["SC", "TC", "EN"],
            "contains_commercial_source_text": False,
            "coordinate_override_supported": True,
            "event_layout_baseline": "static_patch_007_30px_912px_4lines",
            "steam_writes": 0,
        },
        "provenance": {
            "private_catalog_sha256": sha256(canonical_json(catalog)),
            "waves": provenance,
        },
        "summary": {
            "source_overrides": len(translations),
            "target_placements": len(placement_owner),
            "wave_overlays": len(wave_paths),
        },
        "entries": [
            {"source_id": source_id, "ko": translations[source_id]}
            for source_id in sorted(translations)
        ],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--validate", action="store_true")
    args = parser.parse_args(argv)

    integrated = build_integrated_overlay(read_json(args.catalog))
    blob = canonical_json(integrated)
    if args.write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(blob)
    elif not args.output.is_file() or args.output.read_bytes() != blob:
        raise IntegrationError(f"integrated overlay drifted: {args.output}")

    print(
        json.dumps(
            {
                "source_overrides": integrated["summary"]["source_overrides"],
                "target_placements": integrated["summary"]["target_placements"],
                "wave_overlays": integrated["summary"]["wave_overlays"],
                "steam_writes": 0,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
