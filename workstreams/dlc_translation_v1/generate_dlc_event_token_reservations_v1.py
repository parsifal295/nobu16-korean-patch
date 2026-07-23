#!/usr/bin/env python3
"""Freeze source-free runtime-name reservations for every DLC event token."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = SCRIPT.parents[2]
sys.path.insert(0, str(REPO / "tools"))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


DEFAULT_GAME_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_CATALOG = WORKSTREAM / "private" / "catalog.private.v1.json"
DEFAULT_OUTPUT = WORKSTREAM / "event_token_reservations.v1.json"

SCHEMA = "nobu16.kr.dlc-event-token-reservations.v1"
TOKEN_RE = re.compile(r"\[([a-z]+)(\d+)\]")
ESC_RE = re.compile(r"\x1bC[A-Z]")

RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
RUNTIME_FULL_WIDTH_PX = 30
RUNTIME_MAX_LINE_PX = 912
RUNTIME_MAX_LINES = 4


class ReservationError(ValueError):
    """Raised when token lookup or the pinned layout baseline differs."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ReservationError(f"JSON root must be an object: {path}")
    return value


def is_full_width(char: str) -> bool:
    codepoint = ord(char)
    return (
        0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xF900 <= codepoint <= 0xFAFF
        or 0xAC00 <= codepoint <= 0xD7A3
        or 0x1100 <= codepoint <= 0x11FF
        or 0x3130 <= codepoint <= 0x318F
        or 0xA960 <= codepoint <= 0xA97F
        or 0xD7B0 <= codepoint <= 0xD7FF
    )


def width_profile(text: str) -> dict[str, int]:
    visible = ESC_RE.sub("", text)
    full = 0
    half = 0
    for char in visible:
        if char in "\r\n":
            raise ReservationError("runtime name unexpectedly contains a line break")
        if unicodedata.category(char) == "Cc":
            raise ReservationError(f"runtime name contains control U+{ord(char):04X}")
        if is_full_width(char):
            full += 1
        else:
            half += 1
    raw = full * RAW_FULL_WIDTH_PX + half * RAW_HALF_WIDTH_PX
    return {
        "full_width_characters": full,
        "half_width_characters": half,
        "raw_g1n_width_px": raw,
        "scaled_effective_width_px": math.ceil(
            raw * RUNTIME_FULL_WIDTH_PX / RAW_FULL_WIDTH_PX
        ),
    }


def generate(game_root: Path, catalog: dict[str, Any]) -> dict[str, Any]:
    token_counts: Counter[str] = Counter()
    placement_sets: dict[str, set[str]] = defaultdict(set)
    sources = {value["source_id"]: value for value in catalog["sources"]}
    event_placements = [
        value for value in catalog["placements"] if value["family"] == "evm"
    ]
    for placement in event_placements:
        text = sources[placement["source_id"]]["jp"]
        for token in TOKEN_RE.findall(text):
            spelling = f"[{token[0]}{token[1]}]"
            token_counts[spelling] += 1
            placement_sets[spelling].add(placement["placement_id"])

    source_path = game_root / "MSG_PK" / "JP" / "msgev.bin"
    packed = source_path.read_bytes()
    _header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    if rebuild_message_table(table, table.texts) != raw:
        raise ReservationError("active msgev table does not rebuild deterministically")

    reservations: dict[str, dict[str, Any]] = {}
    for spelling in sorted(token_counts):
        match = TOKEN_RE.fullmatch(spelling)
        if match is None:
            raise ReservationError(f"runtime token parser differs: {spelling}")
        prefix, suffix = match.groups()
        name_id = int(suffix)
        if not 0 <= name_id < table.string_count:
            raise ReservationError(f"runtime name ID is outside msgev: {spelling}")
        full_name = table.texts[name_id]
        profile = width_profile(full_name)
        if profile["raw_g1n_width_px"] <= 0:
            raise ReservationError(f"runtime name has zero reserved width: {spelling}")
        reservations[spelling] = {
            "prefix": prefix,
            "source_name_id": name_id,
            "source_name_utf16le_sha256": sha256(full_name.encode("utf-16le")),
            "occurrence_count": token_counts[spelling],
            "placement_count": len(placement_sets[spelling]),
            **profile,
        }

    new_event_ids = {
        value["source_id"] for value in event_placements if value["is_new_path"]
    }
    return {
        "schema": SCHEMA,
        "resource": "MSG_PK/JP/msgev.bin",
        "source": {
            "packed_sha256": sha256(packed),
            "raw_sha256": sha256(raw),
            "string_count": table.string_count,
        },
        "catalog": {
            "private_catalog_sha256": sha256(canonical_json(catalog)),
            "event_placements": len(event_placements),
            "new_event_unique_sources": len(new_event_ids),
        },
        "baseline": {
            "name": "static_patch_007",
            "raw_full_width_px": RAW_FULL_WIDTH_PX,
            "raw_half_width_px": RAW_HALF_WIDTH_PX,
            "runtime_full_width_px": RUNTIME_FULL_WIDTH_PX,
            "scale": "30/48",
            "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "max_effective_line_width_px": RUNTIME_MAX_LINE_PX,
            "max_lines": RUNTIME_MAX_LINES,
            "line_spacing_setting": 8,
        },
        "policy": {
            "full_width_characters": "Hangul and Han ideographs",
            "half_width_characters": "spaces, Latin, digits, and ordinary punctuation",
            "runtime_prefix_semantics_assumed": False,
            "every_token_reserves_entire_referenced_name": True,
            "commercial_name_text_included": False,
            "steam_writes": 0,
        },
        "counts": {
            "unique_token_spellings": len(reservations),
            "unique_referenced_name_ids": len(
                {value["source_name_id"] for value in reservations.values()}
            ),
            "token_occurrences": sum(token_counts.values()),
        },
        "reservations": reservations,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=DEFAULT_GAME_ROOT)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--validate", action="store_true")
    args = parser.parse_args(argv)

    catalog = read_json(args.catalog)
    document = generate(args.game_root.resolve(), catalog)
    blob = canonical_json(document)
    if args.write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(blob)
    elif not args.output.is_file() or args.output.read_bytes() != blob:
        raise ReservationError(f"reservation artifact drifted: {args.output}")
    print(json.dumps(document["counts"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
