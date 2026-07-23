#!/usr/bin/env python3
"""Reuse unanimous exact-hash Korean from prior public event workstreams."""

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
DEFAULT_OUTPUT = WORKSTREAM / "translations.wave09.exact_public_event_reuse.v1.json"

OVERLAY_SCHEMA = "nobu16.kr.dlc-translation-overlay.v1"
ESC_RE = re.compile(r"\x1bC[A-Z]")
RUNTIME_TOKEN_RE = re.compile(r"\[(?:bm?|[A-Za-z]+)\d+\]")
PRINTF_RE = re.compile(
    r"%(?:\d+\$)?[-+#0 ']*\d*(?:\.\d+)?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)
SOURCE_SCRIPT_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uf900-\ufaff]")


class ReuseError(ValueError):
    """Raised when prior-public exact reuse is ambiguous or malformed."""


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
        for entry in read_json(path).get("entries", []):
            if not isinstance(entry, dict) or not isinstance(entry.get("source_id"), str):
                raise ReuseError(f"authored overlay entry differs: {path}")
            result.add(entry["source_id"])
    return result


def public_donors() -> tuple[
    dict[str, set[str]], dict[tuple[str, str], set[Path]], dict[Path, str]
]:
    candidates: dict[str, set[str]] = defaultdict(set)
    origins: dict[tuple[str, str], set[Path]] = defaultdict(set)
    file_hashes: dict[Path, str] = {}
    for path in sorted((REPO / "workstreams").glob("*/public/*.json")):
        if WORKSTREAM in path.parents:
            continue
        document = read_json(path)
        file_hashes[path] = sha256(canonical_json(document))
        for key in ("entries", "rows", "overrides", "translations"):
            rows = document.get(key)
            if not isinstance(rows, list):
                continue
            for entry in rows:
                if not isinstance(entry, dict):
                    continue
                source_hash = (
                    entry.get("source_jp_utf16le_sha256")
                    or entry.get("jp_utf16le_sha256")
                    or entry.get("source_utf16le_sha256")
                )
                korean = entry.get("ko") or entry.get("translation") or entry.get("target")
                if isinstance(korean, dict):
                    korean = korean.get("text")
                if isinstance(source_hash, str) and isinstance(korean, str) and korean:
                    normalized = source_hash.lower()
                    candidates[normalized].add(korean)
                    origins[(normalized, korean)].add(path)
    return candidates, origins, file_hashes


def build_overlay(catalog: dict[str, Any], output: Path) -> dict[str, Any]:
    candidates, origins, file_hashes = public_donors()
    already_authored = authored_source_ids(output)
    sources = {value["source_id"]: value for value in catalog["sources"]}
    selected = [
        placement
        for placement in catalog["placements"]
        if placement["family"] == "evm"
        and placement["is_new_path"]
        and placement["source_id"] not in already_authored
        and len(candidates.get(placement["jp_utf16le_sha256"], ())) == 1
    ]
    if not selected:
        raise ReuseError("prior-public exact donor selected zero new event placements")
    selected_source_ids = {value["source_id"] for value in selected}
    used_paths: set[Path] = set()
    entries: list[dict[str, str]] = []
    for source_id in sorted(selected_source_ids):
        source = sources[source_id]
        values = candidates[source["jp_utf16le_sha256"]]
        if len(values) != 1:
            raise ReuseError(f"selected source donor is no longer unanimous: {source_id}")
        korean = next(iter(values))
        used_paths.update(origins[(source["jp_utf16le_sha256"], korean)])
        if SOURCE_SCRIPT_RE.search(korean):
            raise ReuseError(f"source script remains in public donor: {source_id}")
        if protected_tokens(korean) != protected_tokens(source["jp"]):
            raise ReuseError(f"protected token sequence differs in public donor: {source_id}")
        entries.append({"source_id": source_id, "ko": korean})

    return {
        "schema": OVERLAY_SCHEMA,
        "wave": "wave09_exact_public_event_reuse",
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
            "reuse_gate": "exact_full_jp_utf16le_sha256_and_global_unanimity",
        },
        "provenance": {
            "donors": [
                {
                    "path": path.relative_to(REPO).as_posix(),
                    "sha256": file_hashes[path],
                }
                for path in sorted(used_paths)
            ],
            "conflicting_source_hashes_excluded": sum(
                len(values) > 1 for values in candidates.values()
            ),
            "private_catalog_sha256": sha256(canonical_json(catalog)),
        },
        "entries": entries,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--validate", action="store_true")
    args = parser.parse_args(argv)

    overlay = build_overlay(read_json(args.catalog), args.output)
    blob = canonical_json(overlay)
    if args.write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(blob)
    elif not args.output.is_file() or args.output.read_bytes() != blob:
        raise ReuseError(f"prior-public exact reuse overlay drifted: {args.output}")
    print(
        json.dumps(
            {
                "entries": len(overlay["entries"]),
                "target_placements": len(overlay["scope"]["placement_ids"]),
                "donor_files": len(overlay["provenance"]["donors"]),
                "steam_writes": 0,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
