#!/usr/bin/env python3
"""Generate a source-free glyph-demand inventory from the public officer overlay."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
GAME_ROOT = SCRIPT_DIR.parents[3]
PATCH_ROOT = GAME_ROOT / "KR_PATCH_WORK"
DEFAULT_OVERLAY = PATCH_ROOT / "data" / "public" / "msgev_ko_officer_names_0000_2399.v0.1.json"
DEFAULT_OUTPUT = SCRIPT_DIR / "corpus" / "msgev_officer_names_0000_2399" / "glyph_demand.json"
EXPECTED_ENTRY_COUNT = 2207
EXPECTED_IDS = list(range(EXPECTED_ENTRY_COUNT))
OVERLAY_SCHEMA = "nobu16.kr.common-message-overlay.v1"
DEMAND_SCHEMA = "nobu16.kr.glyph-demand.v1"
NAME_PATTERN = re.compile(r"[가-힣]+(?: [가-힣]+)?\Z")
HASH_PATTERN = re.compile(r"[0-9A-F]{64}\Z")


class DemandError(ValueError):
    """Raised when the public officer overlay is unsafe or inconsistent."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DemandError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def read_json(path: Path) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=reject_duplicate_keys)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DemandError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise DemandError(f"{path}: top-level JSON value must be an object")
    return value, raw


def project_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(GAME_ROOT).as_posix()
    except ValueError as exc:
        raise DemandError(f"input must stay inside the game workspace: {path}") from exc


def validate_overlay(path: Path) -> tuple[dict[str, Any], bytes, list[str]]:
    overlay, raw = read_json(path)
    if overlay.get("schema") != OVERLAY_SCHEMA:
        raise DemandError(f"unsupported overlay schema: {overlay.get('schema')!r}")
    if overlay.get("resource") != "MSG_PK/SC/msgev.bin":
        raise DemandError(f"wrong overlay resource: {overlay.get('resource')!r}")
    entries = overlay.get("entries")
    if not isinstance(entries, list):
        raise DemandError("overlay entries must be an array")
    if overlay.get("entry_count") != len(entries) or len(entries) != EXPECTED_ENTRY_COUNT:
        raise DemandError(
            f"expected exactly {EXPECTED_ENTRY_COUNT} officer entries, got {len(entries)}"
        )

    ids: list[int] = []
    names: list[str] = []
    allowed_entry_keys = {
        "id",
        "ko",
        "source_sc_utf16le_sha256",
        "status",
        "allow_edge_whitespace_change",
    }
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise DemandError(f"entries[{index}] must be an object")
        extra = set(entry) - allowed_entry_keys
        if extra:
            raise DemandError(f"entries[{index}] has unsupported keys: {sorted(extra)!r}")
        if not {"id", "ko", "source_sc_utf16le_sha256"}.issubset(entry):
            raise DemandError(f"entries[{index}] is missing a required key")
        entry_id = entry["id"]
        name = entry["ko"]
        source_hash = entry["source_sc_utf16le_sha256"]
        if type(entry_id) is not int:
            raise DemandError(f"entries[{index}].id must be an integer")
        if not isinstance(name, str) or not unicodedata.is_normalized("NFC", name):
            raise DemandError(f"entries[{index}].ko must be NFC text")
        if NAME_PATTERN.fullmatch(name) is None:
            raise DemandError(
                f"entries[{index}].ko must contain only Hangul syllables and one optional ASCII space"
            )
        if not isinstance(source_hash, str) or HASH_PATTERN.fullmatch(source_hash) is None:
            raise DemandError(f"entries[{index}].source_sc_utf16le_sha256 is not canonical")
        ids.append(entry_id)
        names.append(name)
    if ids != EXPECTED_IDS:
        raise DemandError("officer ids must be the exact ordered range 0..2206")
    return overlay, raw, names


def build_demand(overlay_path: Path) -> dict[str, Any]:
    overlay, overlay_raw, names = validate_overlay(overlay_path)
    characters = sorted(
        {character for name in names for character in name if not character.isspace()},
        key=ord,
    )
    if not characters or any(not (0xAC00 <= ord(character) <= 0xD7A3) for character in characters):
        raise DemandError("officer font demand must contain only precomposed Hangul syllables")
    codepoint_lines = "".join(f"U+{ord(character):04X}\n" for character in characters).encode("ascii")
    empty_exclusions = json.dumps(
        [], ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    codepoints = [f"U+{ord(character):04X}" for character in characters]
    return {
        "schema": DEMAND_SCHEMA,
        "source": "Korean names in the source-free public msgev officer overlay",
        "source_overlay": {
            "path": project_relative(overlay_path),
            "sha256": sha256_bytes(overlay_raw),
            "schema": overlay["schema"],
            "overlay_id": overlay.get("overlay_id"),
            "entry_count": len(names),
        },
        "source_non_whitespace_character_count": len(characters),
        "source_non_whitespace_codepoints_sha256": sha256_bytes(codepoint_lines),
        "font_exclusion_policy": "exclude ESC command components, C0/C1 controls, and game PUA icons from G1N raster demand",
        "excluded_font_token_count": 0,
        "excluded_font_tokens": [],
        "excluded_font_tokens_sha256": sha256_bytes(empty_exclusions),
        "character_count": len(characters),
        "characters": characters,
        "codepoints": codepoints,
        "hangul_syllable_count": len(characters),
        "hangul_syllables": characters,
        "hangul_syllable_codepoints": codepoints,
        "hangul_jamo_count": 0,
        "hangul_jamo": [],
        "hangul_jamo_codepoints": [],
    }


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--overlay", type=Path, default=DEFAULT_OVERLAY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if the existing output is not byte-identical; do not write.",
    )
    args = parser.parse_args(argv)
    try:
        overlay_path = args.overlay.resolve()
        output_path = args.output.resolve()
        expected = encode_json(build_demand(overlay_path))
        if args.check:
            actual = output_path.read_bytes()
            if actual != expected:
                raise DemandError(f"stale officer glyph demand: {output_path}")
        else:
            atomic_write(output_path, expected)
    except (OSError, DemandError) as exc:
        parser.exit(2, f"error: {exc}\n")
    value = json.loads(expected.decode("utf-8"))
    print(f"output={output_path}")
    print(f"officer_entries={value['source_overlay']['entry_count']}")
    print(f"hangul_syllables={value['hangul_syllable_count']}")
    print(f"sha256={sha256_bytes(expected)}")
    print(f"check_only={args.check}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
