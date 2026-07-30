#!/usr/bin/env python3
"""Build encrypted DLC translation candidates in an ignored private stage.

The source game tree is read-only.  Korean overlays are applied to decoded
XL13 rows, the original wrapper mode and opaque prefix are retained, and the
result is encrypted with the executable-derived key.  Every candidate is then
decrypted again and compared at both the XL metadata and row-text levels.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = SCRIPT.parents[2]
AUDIT_SCRIPT = (
    REPO
    / "workstreams"
    / "dlc_translation_inventory_v1"
    / "audit_dlc_translation_inventory_v1.py"
)
sys.path.insert(0, str(REPO / "tools"))

from nobu16_lz4 import raw_lz4_compress_greedy, raw_lz4_decompress  # noqa: E402


DEFAULT_GAME_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_CATALOG = WORKSTREAM / "private" / "catalog.private.v1.json"
DEFAULT_OVERLAY = WORKSTREAM / "translations.wave01.scenario.v1.json"
DEFAULT_STAGE = WORKSTREAM / "private" / "stage" / "wave01_scenario_046_051"
DEFAULT_MANIFEST = WORKSTREAM / "candidate.wave01.scenario.v1.json"

OVERLAY_SCHEMA = "nobu16.kr.dlc-translation-overlay.v1"
MANIFEST_SCHEMA = "nobu16.kr.dlc-translation-candidate.v1"


class CandidateError(ValueError):
    """Raised when a candidate violates a pinned format or safety invariant."""


@dataclass(frozen=True)
class XlTable:
    blob: bytes
    sets: int
    width: int
    table_offset: int
    types: tuple[int, ...]
    string_field_offset: int
    table_end: int
    texts: tuple[str, ...]


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise CandidateError(f"JSON root must be an object: {path}")
    return value


def load_audit_module() -> Any:
    spec = importlib.util.spec_from_file_location("dlc_inventory_candidate_v1", AUDIT_SCRIPT)
    if spec is None or spec.loader is None:
        raise CandidateError(f"cannot import inventory helper: {AUDIT_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def field_size(field_type: int) -> int:
    if field_type in (0, 1, 4, 7):
        return 4
    if field_type in (2, 5):
        return 2
    if field_type in (3, 6):
        return 1
    if field_type == 0xFF:
        return 0
    raise CandidateError(f"unsupported XL field type 0x{field_type:02X}")


def parse_xl(raw: bytes) -> XlTable:
    if len(raw) < 20 or raw[:4] != b"XL\x13\0":
        raise CandidateError("decoded candidate is not XL13")
    _, _, file_size, type_count, sets, width, table_offset, _ = struct.unpack_from(
        "<HHHHHhhh", raw, 0
    )
    if file_size != len(raw):
        raise CandidateError(f"XL size field {file_size} != decoded size {len(raw)}")
    types = tuple(raw[16 : 16 + type_count])
    string_offsets: list[int] = []
    local = 0
    for value in types:
        if value == 0:
            string_offsets.append(local)
        local += field_size(value)
    if len(string_offsets) != 1:
        raise CandidateError(f"expected one string field, found {len(string_offsets)}")
    if local != width:
        raise CandidateError(f"XL field width {local} != row width {width}")
    string_field_offset = string_offsets[0]
    table_end = table_offset + sets * width
    if table_end > len(raw):
        raise CandidateError("XL row table extends beyond the decoded payload")

    texts: list[str] = []
    starts: list[int] = []
    ends: list[int] = []
    for row in range(sets):
        field = table_offset + row * width + string_field_offset
        relative = struct.unpack_from("<i", raw, field)[0]
        start = table_offset + relative
        if start < table_end or start >= len(raw) or start & 1:
            raise CandidateError(f"XL row {row} has invalid string pointer {relative}")
        end = start
        while end + 1 < len(raw) and raw[end : end + 2] != b"\0\0":
            end += 2
        if end + 1 >= len(raw):
            raise CandidateError(f"XL row {row} has no UTF-16LE terminator")
        try:
            text = raw[start:end].decode("utf-16le", errors="strict")
        except UnicodeDecodeError as exc:
            raise CandidateError(f"XL row {row} is invalid UTF-16LE: {exc}") from exc
        texts.append(text)
        starts.append(start)
        ends.append(end + 2)
    if min(starts) != table_end:
        raise CandidateError("opaque bytes exist between the XL table and string pool")
    if max(ends) != len(raw):
        raise CandidateError("opaque bytes exist after the XL string pool")
    return XlTable(
        blob=raw,
        sets=sets,
        width=width,
        table_offset=table_offset,
        types=types,
        string_field_offset=string_field_offset,
        table_end=table_end,
        texts=tuple(texts),
    )


def rebuild_xl(table: XlTable, replacements: dict[int, str]) -> bytes:
    if any(row < 0 or row >= table.sets for row in replacements):
        raise CandidateError("replacement row is outside the XL table")
    prefix = bytearray(table.blob[: table.table_end])
    pool = bytearray()
    for row, original in enumerate(table.texts):
        text = replacements.get(row, original)
        if not isinstance(text, str) or "\0" in text:
            raise CandidateError(f"XL row {row} has an invalid replacement string")
        encoded = text.encode("utf-16le", errors="strict")
        absolute = table.table_end + len(pool)
        relative = absolute - table.table_offset
        if relative > 0x7FFFFFFF:
            raise CandidateError("XL string pointer exceeds signed 32-bit range")
        field = table.table_offset + row * table.width + table.string_field_offset
        struct.pack_into("<i", prefix, field, relative)
        pool.extend(encoded)
        pool.extend(b"\0\0")
    rebuilt = prefix + pool
    if len(rebuilt) > 0xFFFF:
        raise CandidateError(f"rebuilt XL exceeds its u16 size field: {len(rebuilt)}")
    struct.pack_into("<H", rebuilt, 4, len(rebuilt))
    return bytes(rebuilt)


def decode_wrapper(wrapper: bytes) -> tuple[bytes, bytes, bool]:
    if len(wrapper) < 24:
        raise CandidateError("DLC wrapper is shorter than 24 bytes")
    uncompressed_size, compressed_size = struct.unpack_from("<QQ", wrapper, 8)
    payload = wrapper[24:]
    if compressed_size == 0:
        if len(payload) != uncompressed_size:
            raise CandidateError("raw DLC wrapper size mismatch")
        return wrapper[:8], payload, False
    if len(payload) != compressed_size:
        raise CandidateError("compressed DLC wrapper size mismatch")
    return wrapper[:8], raw_lz4_decompress(payload, uncompressed_size), True


def encode_wrapper(raw: bytes, prefix: bytes, compressed: bool) -> bytes:
    if len(prefix) != 8:
        raise CandidateError("DLC wrapper prefix must be eight bytes")
    if not compressed:
        return prefix + struct.pack("<QQ", len(raw), 0) + raw
    payload = raw_lz4_compress_greedy(raw)
    return prefix + struct.pack("<QQ", len(raw), len(payload)) + payload


def crypt_blob(decoder: Any, blob: bytes, file_spec: Any) -> bytes:
    """Apply the symmetric DLC XOR stream used for both encrypt and decrypt."""
    state = decoder._seed(file_spec)
    output = bytearray()
    for value in blob:
        state = (state * 0x6C078965 + 0x3039) & 0xFFFFFFFF
        key_byte = ((state >> 24) ^ (state >> 16)) & 0xFF
        output.append(value ^ key_byte)
    return bytes(output)


def assert_metadata_preserved(before: XlTable, after: XlTable) -> None:
    if (
        before.sets,
        before.width,
        before.table_offset,
        before.types,
        before.string_field_offset,
    ) != (
        after.sets,
        after.width,
        after.table_offset,
        after.types,
        after.string_field_offset,
    ):
        raise CandidateError("XL topology changed during rebuild")
    left = bytearray(before.blob[: before.table_end])
    right = bytearray(after.blob[: after.table_end])
    left[4:6] = b"\0\0"
    right[4:6] = b"\0\0"
    for row in range(before.sets):
        field = before.table_offset + row * before.width + before.string_field_offset
        left[field : field + 4] = b"\0" * 4
        right[field : field + 4] = b"\0" * 4
    if left != right:
        raise CandidateError("opaque XL header or row metadata changed")


def ensure_safe_stage(stage: Path, game_root: Path) -> None:
    stage = stage.resolve()
    game_root = game_root.resolve()
    workstream = WORKSTREAM.resolve()
    if stage == game_root or game_root in stage.parents:
        raise CandidateError("candidate stage must not be inside the Steam game tree")
    if stage != workstream and workstream not in stage.parents:
        raise CandidateError("candidate stage must remain inside this workstream")
    if "private" not in {part.lower() for part in stage.parts}:
        raise CandidateError("candidate binaries must remain below an ignored private directory")


def input_hash(catalog: dict[str, Any], relative: str) -> str:
    area = relative.split("/", 1)[0]
    key = f"JP:{relative}"
    try:
        return catalog["inputs"]["localized_file_sha256"][area][key]
    except KeyError as exc:
        raise CandidateError(f"catalogue has no pinned input hash for {relative}") from exc


def scoped_placements(
    catalog: dict[str, Any], scope: dict[str, Any]
) -> list[dict[str, Any]]:
    if set(scope) == {"path_regex"}:
        try:
            path_re = re.compile(scope["path_regex"])
        except (TypeError, re.error) as exc:
            raise CandidateError(f"invalid overlay path scope: {exc}") from exc
        return [
            value
            for value in catalog["placements"]
            if path_re.fullmatch(value["path"])
        ]
    if set(scope) == {"placement_ids"}:
        placement_ids = scope["placement_ids"]
        if (
            not isinstance(placement_ids, list)
            or not placement_ids
            or any(not isinstance(value, str) for value in placement_ids)
            or len(set(placement_ids)) != len(placement_ids)
        ):
            raise CandidateError("scope placement_ids must be unique nonempty strings")
        by_id = {
            value["placement_id"]: value for value in catalog["placements"]
        }
        missing = set(placement_ids) - set(by_id)
        if missing:
            raise CandidateError(
                f"scope contains unknown placement IDs: {sorted(missing)}"
            )
        return [by_id[value] for value in placement_ids]
    raise CandidateError("scope must contain exactly path_regex or placement_ids")


def build_candidates(
    game_root: Path,
    stage: Path,
    catalog: dict[str, Any],
    overlay: dict[str, Any],
) -> tuple[dict[str, Any], dict[Path, bytes]]:
    if overlay.get("schema") != OVERLAY_SCHEMA:
        raise CandidateError("overlay schema changed")
    scope = overlay.get("scope", {})
    if not isinstance(scope, dict):
        raise CandidateError("overlay scope must be an object")
    entries = overlay.get("entries")
    if not isinstance(entries, list):
        raise CandidateError("overlay entries must be an array")
    translations = {entry["source_id"]: entry["ko"] for entry in entries}
    if len(translations) != len(entries):
        raise CandidateError("overlay has duplicate source IDs")

    source_by_id = {value["source_id"]: value for value in catalog["sources"]}
    scoped = scoped_placements(catalog, scope)
    scoped_ids = {value["source_id"] for value in scoped}
    if set(translations) != scoped_ids:
        raise CandidateError("overlay entries do not exactly cover the scoped catalogue sources")
    by_path: dict[str, list[dict[str, Any]]] = {}
    for placement in scoped:
        by_path.setdefault(placement["path"], []).append(placement)

    audit = load_audit_module()
    executable = game_root / "NOBU16PK.exe"
    if sha256(executable.read_bytes()) != catalog["inputs"]["executable_sha256"]:
        raise CandidateError("game executable differs from the catalogued key source")
    decoder = audit.DlcDecoder(executable)
    outputs: dict[Path, bytes] = {}
    files: list[dict[str, Any]] = []
    total_rows = 0

    for relative, placements in sorted(by_path.items()):
        source_path = game_root / Path(relative)
        source_blob = source_path.read_bytes()
        if sha256(source_blob) != input_hash(catalog, relative):
            raise CandidateError(f"catalogued input hash changed: {relative}")
        spec = audit.file_spec(source_path)
        source_wrapper = decoder.decrypt(source_path, spec)
        prefix, source_raw, compressed = decode_wrapper(source_wrapper)
        before = parse_xl(source_raw)
        replacements: dict[int, str] = {}
        changed_rows: list[dict[str, Any]] = []
        for placement in sorted(placements, key=lambda value: value["row"]):
            row = int(placement["row"])
            if sha256(before.texts[row].encode("utf-16le")) != placement["jp_utf16le_sha256"]:
                raise CandidateError(f"source row drifted: {placement['placement_id']}")
            source_id = placement["source_id"]
            if before.texts[row] != source_by_id[source_id]["jp"]:
                raise CandidateError(f"private catalogue source mismatch: {placement['placement_id']}")
            korean = translations[source_id]
            replacements[row] = korean
            changed_rows.append(
                {
                    "row": row,
                    "source_id": source_id,
                    "ko_utf16le_sha256": sha256(korean.encode("utf-16le")),
                }
            )
        rebuilt_raw = rebuild_xl(before, replacements)
        rebuilt_wrapper = encode_wrapper(rebuilt_raw, prefix, compressed)
        encrypted = crypt_blob(decoder, rebuilt_wrapper, spec)

        # Full encrypted round trip using the same executable-derived decoder.
        roundtrip_wrapper = crypt_blob(decoder, encrypted, spec)
        if roundtrip_wrapper != rebuilt_wrapper:
            raise CandidateError(f"cipher round trip failed: {relative}")
        out_prefix, roundtrip_raw, out_compressed = decode_wrapper(roundtrip_wrapper)
        if out_prefix != prefix or out_compressed != compressed or roundtrip_raw != rebuilt_raw:
            raise CandidateError(f"wrapper round trip failed: {relative}")
        after = parse_xl(roundtrip_raw)
        assert_metadata_preserved(before, after)
        for row, original in enumerate(before.texts):
            expected = replacements.get(row, original)
            if after.texts[row] != expected:
                raise CandidateError(f"row {row} failed round trip: {relative}")

        output_path = stage / Path(relative)
        outputs[output_path] = encrypted
        total_rows += len(changed_rows)
        files.append(
            {
                "path": relative,
                "input_sha256": sha256(source_blob),
                "output_sha256": sha256(encrypted),
                "source_decoded_xl_sha256": sha256(source_raw),
                "candidate_decoded_xl_sha256": sha256(rebuilt_raw),
                "wrapper_mode": "compressed_raw_lz4" if compressed else "stored_raw",
                "changed_rows": changed_rows,
                "unchanged_rows": before.sets - len(changed_rows),
                "xl_sets": before.sets,
            }
        )

    manifest = {
        "schema": MANIFEST_SCHEMA,
        "wave": overlay.get("wave"),
        "status": "static_roundtrip_validated_pending_runtime_qa",
        "private_catalog_sha256": sha256(canonical_json(catalog)),
        "overlay_sha256": sha256(canonical_json(overlay)),
        "summary": {
            "candidate_files": len(files),
            "translated_placements": total_rows,
            "encrypted_roundtrip_failures": 0,
            "wrapper_roundtrip_failures": 0,
            "xl_metadata_failures": 0,
            "row_text_failures": 0,
            "steam_writes": 0,
            "runtime_qa_complete": False,
        },
        "files": files,
    }
    return manifest, outputs


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=DEFAULT_GAME_ROOT)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--overlay", type=Path, default=DEFAULT_OVERLAY)
    parser.add_argument("--stage", type=Path, default=DEFAULT_STAGE)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--validate", action="store_true")
    args = parser.parse_args(argv)

    game_root = args.game_root.resolve()
    stage = args.stage.resolve()
    ensure_safe_stage(stage, game_root)
    catalog = read_json(args.catalog)
    overlay = read_json(args.overlay)
    manifest, outputs = build_candidates(game_root, stage, catalog, overlay)
    manifest_blob = canonical_json(manifest)

    if args.write:
        for path, blob in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(blob)
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_bytes(manifest_blob)
    else:
        for path, blob in outputs.items():
            if not path.is_file() or path.read_bytes() != blob:
                raise CandidateError(f"candidate drifted: {path}")
        if not args.manifest.is_file() or args.manifest.read_bytes() != manifest_blob:
            raise CandidateError(f"candidate manifest drifted: {args.manifest}")
    print(json.dumps(manifest["summary"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
