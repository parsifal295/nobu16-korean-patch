#!/usr/bin/env python3
"""Reuse current common-message Korean for exact-hash remaining DLC rows."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = SCRIPT.parents[2]
DEFAULT_CATALOG = WORKSTREAM / "private" / "catalog.private.v1.json"
DEFAULT_DONOR_DIR = REPO / "workstreams" / "steam_jp_common_messages_v1" / "public"
DEFAULT_OUTPUT = WORKSTREAM / "translations.wave06.exact_common_reuse.v1.json"

OVERLAY_SCHEMA = "nobu16.kr.dlc-translation-overlay.v1"
ESC_RE = re.compile(r"\x1bC[A-Z]")
RUNTIME_TOKEN_RE = re.compile(r"\[(?:bm?|[A-Za-z]+)\d+\]")
PRINTF_RE = re.compile(
    r"%(?:\d+\$)?[-+#0 ']*\d*(?:\.\d+)?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)
SOURCE_SCRIPT_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uf900-\ufaff]")


class ReuseError(ValueError):
    """Raised when a common-message exact-reuse invariant differs."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ReuseError(f"JSON root must be an object: {path}")
    return value


def protected_tokens(text: str) -> list[str]:
    found: list[tuple[int, str]] = []
    for pattern in (ESC_RE, RUNTIME_TOKEN_RE, PRINTF_RE):
        found.extend((match.start(), match.group(0)) for match in pattern.finditer(text))
    return [value for _, value in sorted(found)]


def authored_source_ids(output: Path) -> set[str]:
    result: set[str] = set()
    for path in sorted(WORKSTREAM.glob("translations.wave*.v1.json")):
        if path.resolve() == output.resolve():
            continue
        document = read_json(path)
        for entry in document.get("entries", []):
            if not isinstance(entry, dict) or not isinstance(entry.get("source_id"), str):
                raise ReuseError(f"authored overlay entry differs: {path}")
            result.add(entry["source_id"])
    return result


def donor_map(donor_dir: Path) -> tuple[dict[str, str], list[dict[str, str]], int]:
    candidates: dict[str, set[str]] = defaultdict(set)
    inputs: list[dict[str, str]] = []
    paths = sorted(donor_dir.glob("*_ko_steam_jp_native.v1.json"))
    if not paths:
        raise ReuseError(f"common-message donor overlays are absent: {donor_dir}")
    for path in paths:
        document = read_json(path)
        inputs.append(
            {
                "path": path.relative_to(REPO).as_posix(),
                "sha256": sha256(canonical_json(document)),
            }
        )
        for entry in document.get("entries", []):
            if not isinstance(entry, dict):
                raise ReuseError(f"common donor entry differs: {path}")
            source_hash = entry.get("source_jp_utf16le_sha256")
            korean = entry.get("ko")
            if isinstance(source_hash, str) and isinstance(korean, str) and korean:
                candidates[source_hash.lower()].add(korean)
    conflicts = sum(len(values) != 1 for values in candidates.values())
    return (
        {key: next(iter(values)) for key, values in candidates.items() if len(values) == 1},
        inputs,
        conflicts,
    )


def build_overlay(
    catalog: dict[str, Any], donor_dir: Path, output: Path
) -> dict[str, Any]:
    donors, donor_inputs, conflict_count = donor_map(donor_dir)
    already_authored = authored_source_ids(output)
    sources = {value["source_id"]: value for value in catalog["sources"]}
    selected = [
        placement
        for placement in catalog["placements"]
        if placement["source_id"] not in already_authored
        and placement["jp_utf16le_sha256"] in donors
    ]
    if not selected:
        raise ReuseError("exact common donor selected zero DLC placements")
    selected_source_ids = {value["source_id"] for value in selected}
    entries: list[dict[str, str]] = []
    for source_id in sorted(selected_source_ids):
        source = sources[source_id]
        korean = donors[source["jp_utf16le_sha256"]]
        if SOURCE_SCRIPT_RE.search(korean):
            raise ReuseError(f"source script remains in common donor: {source_id}")
        if protected_tokens(korean) != protected_tokens(source["jp"]):
            raise ReuseError(f"protected token sequence differs in common donor: {source_id}")
        if any(value["family"] == "scem" for value in selected if value["source_id"] == source_id):
            if korean.count("\n") != source["jp"].count("\n"):
                raise ReuseError(f"scenario line count differs in common donor: {source_id}")
        entries.append({"source_id": source_id, "ko": korean})

    return {
        "schema": OVERLAY_SCHEMA,
        "wave": "wave06_exact_common_reuse",
        "status": "exact_hash_reuse_static_validation_pending_runtime_qa",
        "scope": {
            "placement_ids": sorted(value["placement_id"] for value in selected)
        },
        "policy": {
            "base_language": "JP",
            "crosscheck_languages": ["SC", "TC", "EN"],
            "contains_commercial_source_text": False,
            "coordinate_override_supported": True,
            "event_layout_baseline": "static_patch_007_30px_912px_4lines",
            "reuse_gate": "exact_full_jp_utf16le_sha256_and_unanimous_korean",
        },
        "provenance": {
            "donors": donor_inputs,
            "conflicting_donor_hashes_excluded": conflict_count,
            "private_catalog_sha256": sha256(canonical_json(catalog)),
        },
        "entries": entries,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--donor-dir", type=Path, default=DEFAULT_DONOR_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--validate", action="store_true")
    args = parser.parse_args(argv)

    catalog = read_json(args.catalog)
    overlay = build_overlay(catalog, args.donor_dir, args.output)
    blob = canonical_json(overlay)
    if args.write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(blob)
    elif not args.output.is_file() or args.output.read_bytes() != blob:
        raise ReuseError(f"exact common reuse overlay drifted: {args.output}")
    print(
        json.dumps(
            {
                "entries": len(overlay["entries"]),
                "target_placements": len(overlay["scope"]["placement_ids"]),
                "steam_writes": 0,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
