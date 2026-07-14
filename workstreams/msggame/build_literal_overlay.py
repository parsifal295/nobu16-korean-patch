#!/usr/bin/env python3
"""Build an offline msggame.bin from a source-free literal overlay JSON."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))
sys.path.insert(0, str(WORKSTREAM_ROOT))

from build_structure_inventory import SOURCE_PINS  # noqa: E402
from msggame_format import (  # noqa: E402
    iter_literals,
    parse_packed_msggame,
    rebuild_packed_with_literals,
    sha256,
)
from nobu16_lz4 import decompress_wrapper  # noqa: E402


OVERLAY_SCHEMA = "nobu16.kr.msggame-literal-overlay.v1"
SUPPORTED_RESOURCES = frozenset(
    {"MSG_PK/SC/msggame.bin", "MSG/SC/msggame.bin"}
)


class LiteralOverlayError(ValueError):
    """Raised for an invalid or source-mismatched msggame overlay."""


def strict_object(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise LiteralOverlayError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8-sig"), object_pairs_hook=strict_object
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LiteralOverlayError(f"invalid JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise LiteralOverlayError("overlay JSON root must be an object")
    return value


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-16-le")).hexdigest().upper()


def _require_int(entry: dict[str, Any], key: str) -> int:
    value = entry.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise LiteralOverlayError(f"entry {key} must be a non-negative integer")
    return value


def apply_overlay_blob(packed: bytes, overlay: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    if overlay.get("schema") != OVERLAY_SCHEMA:
        raise LiteralOverlayError(f"unsupported overlay schema: {overlay.get('schema')!r}")
    resource = overlay.get("resource")
    if resource not in SUPPORTED_RESOURCES:
        raise LiteralOverlayError(f"unsupported resource: {resource!r}")
    if overlay.get("base_language") != "SC":
        raise LiteralOverlayError("msggame literal overlays must use SC as the base")

    stock = overlay.get("stock_sc")
    if not isinstance(stock, dict):
        raise LiteralOverlayError("stock_sc must be an object")
    if stock.get("packed_size") != len(packed) or stock.get("packed_sha256") != sha256(packed):
        raise LiteralOverlayError("packed SC source pin mismatch")

    parsed = parse_packed_msggame(packed)
    _header, raw = decompress_wrapper(packed)
    literals = {
        (literal.block_id, literal.record_id, literal.literal_id): literal
        for literal in iter_literals(parsed.archive)
    }
    expected_raw = {
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
        "record_count": parsed.archive.record_count,
        "literal_slot_count": len(literals),
    }
    for key, expected in expected_raw.items():
        if stock.get(key) != expected:
            raise LiteralOverlayError(f"stock_sc {key} mismatch")

    entries = overlay.get("entries")
    if not isinstance(entries, list):
        raise LiteralOverlayError("entries must be an array")
    replacements: dict[tuple[int, int, int], str] = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise LiteralOverlayError(f"entry {index} must be an object")
        coordinate = (
            _require_int(entry, "block_id"),
            _require_int(entry, "record_id"),
            _require_int(entry, "literal_id"),
        )
        if coordinate in replacements:
            raise LiteralOverlayError(f"duplicate literal coordinate: {coordinate}")
        source = literals.get(coordinate)
        if source is None:
            raise LiteralOverlayError(f"literal coordinate does not exist: {coordinate}")
        expected_hash = entry.get("source_sc_utf16le_sha256")
        if expected_hash != text_hash(source.text):
            raise LiteralOverlayError(f"source text hash mismatch at {coordinate}")
        replacement = entry.get("ko")
        if not isinstance(replacement, str):
            raise LiteralOverlayError(f"ko must be a string at {coordinate}")
        replacements[coordinate] = replacement

    rebuilt = rebuild_packed_with_literals(packed, replacements)
    verified = parse_packed_msggame(rebuilt)
    verified_literals = {
        (literal.block_id, literal.record_id, literal.literal_id): literal.text
        for literal in iter_literals(verified.archive)
    }
    for coordinate, replacement in replacements.items():
        if verified_literals.get(coordinate) != replacement:
            raise LiteralOverlayError(f"rebuilt literal verification failed at {coordinate}")
    if verified.archive.record_count != parsed.archive.record_count:
        raise LiteralOverlayError("record count changed during overlay build")
    _new_header, new_raw = decompress_wrapper(rebuilt)
    manifest = {
        "schema": "nobu16.kr.msggame-literal-build-manifest.v1",
        "resource": resource,
        "overlay_id": overlay.get("overlay_id"),
        "entry_count": len(replacements),
        "source": {
            "packed_size": len(packed),
            "packed_sha256": sha256(packed),
            "raw_size": len(raw),
            "raw_sha256": sha256(raw),
        },
        "target": {
            "packed_size": len(rebuilt),
            "packed_sha256": sha256(rebuilt),
            "raw_size": len(new_raw),
            "raw_sha256": sha256(new_raw),
        },
        "checks": {
            "strict_source_hashes": "OK",
            "literal_coordinates_unique": "OK",
            "variable_length_offsets_rebuilt": "OK",
            "wrapper_decompression_roundtrip": "OK",
            "rebuilt_literals_match_overlay": "OK",
        },
        "installed_game_file_written": False,
    }
    return rebuilt, manifest


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def build_overlay(
    game_root: Path, overlay_path: Path, output_root: Path
) -> dict[str, Any]:
    overlay = load_json(overlay_path)
    resource = overlay.get("resource")
    if resource not in SUPPORTED_RESOURCES:
        raise LiteralOverlayError(f"unsupported resource: {resource!r}")
    pin = SOURCE_PINS[resource]
    source_path = (game_root / Path(resource)).resolve()
    packed = source_path.read_bytes()
    if len(packed) != pin["packed_size"] or sha256(packed) != pin["packed_sha256"]:
        raise LiteralOverlayError("installed resource differs from the supported source pin")
    before = sha256(packed)
    rebuilt, manifest = apply_overlay_blob(packed, overlay)

    target_path = (output_root / Path(resource)).resolve()
    if target_path == source_path:
        raise LiteralOverlayError("refusing to overwrite the installed source file")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_bytes(rebuilt)
    manifest_path = target_path.with_suffix(target_path.suffix + ".manifest.json")
    manifest_path.write_bytes(encode_json(manifest))
    if sha256(source_path.read_bytes()) != before:
        raise LiteralOverlayError("installed source changed during offline build")
    return {
        "target_path": target_path,
        "target_sha256": sha256(rebuilt),
        "manifest_path": manifest_path,
        "entry_count": manifest["entry_count"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=REPO_ROOT.parent)
    parser.add_argument("--overlay", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = build_overlay(
            args.game_root.resolve(), args.overlay.resolve(), args.output_root.resolve()
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    for key, value in result.items():
        print(f"{key}={value}")
    print("installed_game_file_written=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
