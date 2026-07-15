#!/usr/bin/env python3
"""Read-only compatibility evidence for Switch and PC SeoulHangang font paths.

This intentionally inspects only structural headers, hashes and counts.  It
never exports a Switch G1N, raster block, LINK archive or complete resource.
The result demonstrates why the Switch patch font must not be raw-copied into
the PC PK ``RES_SC`` path.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import struct
import sys
import zipfile
from pathlib import Path
from typing import Any, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
PATCH_ROOT = SCRIPT_DIR.parents[1]
sys.dont_write_bytecode = True

SWITCH_RELEASE_ZIP_SHA256 = "931E7C5BDECD724E44987D722E71A12161448A1A583DFFB4A569A4FA58EC46F6"
SWITCH_RESOURCE_SHA256 = "E05022246DFB8383A81C915E8EDBDB85C76C12A27F3C1C9D6776CE713810C7DF"
PC_STOCK_SHA256 = "916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99"
SWITCH_RESOURCE_SUFFIX = "/romfs/RES_JP/res_lang.bin"


class EvidenceError(ValueError):
    pass


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


LZ4 = load_module("nobu16_font_seoulhangang_v1_lz4", PATCH_ROOT / "tools" / "nobu16_lz4.py")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def g1n_summary(raw: bytes, entry: int) -> dict[str, Any]:
    if len(raw) < 0x20 or raw[:8] != b"_N1G0000":
        raise EvidenceError(f"entry {entry}: not a G1N")
    declared_size, header_size, unknown, atlas_offset, palette_count, table_count = struct.unpack_from(
        "<IIIIII", raw, 0x08
    )
    if declared_size != len(raw):
        raise EvidenceError(f"entry {entry}: G1N declared size mismatch")
    if not 1 <= table_count <= 32:
        raise EvidenceError(f"entry {entry}: implausible table count")
    table_offsets = list(struct.unpack_from(f"<{table_count}I", raw, 0x20))
    if table_offsets != sorted(table_offsets) or table_offsets[0] != header_size:
        raise EvidenceError(f"entry {entry}: invalid G1N table offsets")
    if not (table_offsets[-1] < atlas_offset <= len(raw)):
        raise EvidenceError(f"entry {entry}: invalid G1N atlas offset")
    tables: list[dict[str, Any]] = []
    for table_index, table_offset in enumerate(table_offsets):
        table_end = table_offsets[table_index + 1] if table_index + 1 < table_count else atlas_offset
        record_bytes = table_end - table_offset - 0x20000
        if record_bytes < 0 or record_bytes % 12:
            raise EvidenceError(f"entry {entry} table {table_index}: malformed record region")
        mapping = struct.unpack_from("<65536H", raw, table_offset)
        tables.append(
            {
                "index": table_index,
                "record_count": record_bytes // 12,
                "mapped_nonzero_count": sum(value != 0 for value in mapping),
                "mapped_hangul_count": sum(
                    value != 0 for codepoint, value in enumerate(mapping) if 0xAC00 <= codepoint <= 0xD7A3
                ),
            }
        )
    return {
        "entry": entry,
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
        "table_count": table_count,
        "palette_count": palette_count,
        "atlas_size": len(raw) - atlas_offset,
        "tables": tables,
    }


def archive_summary(blob: bytes, label: str) -> dict[str, Any]:
    archive = LZ4.parse_link(blob)
    if LZ4.rebuild_link(archive) != blob:
        raise EvidenceError(f"{label}: LINK parse/rebuild identity failed")
    if len(archive.entries) <= 7:
        raise EvidenceError(f"{label}: font entries 6/7 are missing")
    entries = []
    for index in (6, 7):
        _header, raw = LZ4.decompress_wrapper(archive.entries[index].data)
        entries.append(g1n_summary(raw, index))
    return {
        "archive_size": len(blob),
        "archive_sha256": sha256(blob),
        "link_entry_count": len(archive.entries),
        "link_parse_rebuild_exact": True,
        "font_entries": entries,
    }


def extract_switch_resource(zip_path: Path) -> bytes:
    if sha256_file(zip_path) != SWITCH_RELEASE_ZIP_SHA256:
        raise EvidenceError("Switch v1.1 release archive SHA-256 does not match the reviewed pin")
    with zipfile.ZipFile(zip_path) as archive:
        matches = [entry for entry in archive.infolist() if entry.filename.endswith(SWITCH_RESOURCE_SUFFIX)]
        if len(matches) != 1:
            raise EvidenceError("Switch release has no unique RES_JP/res_lang.bin entry")
        return archive.read(matches[0])


def build_evidence(switch_blob: bytes, pc_blob: bytes) -> dict[str, Any]:
    if sha256(switch_blob) != SWITCH_RESOURCE_SHA256:
        raise EvidenceError("Switch RES_JP/res_lang.bin SHA-256 does not match the reviewed pin")
    if sha256(pc_blob) != PC_STOCK_SHA256:
        raise EvidenceError("PC stock RES_SC/res_lang.bin SHA-256 does not match the reviewed pin")
    switch = archive_summary(switch_blob, "Switch")
    pc = archive_summary(pc_blob, "PC")
    switch_by_entry = {item["entry"]: item for item in switch["font_entries"]}
    pc_by_entry = {item["entry"]: item for item in pc["font_entries"]}
    differences = []
    for entry in (6, 7):
        left = switch_by_entry[entry]
        right = pc_by_entry[entry]
        if left["table_count"] != right["table_count"]:
            differences.append(f"entry_{entry}_table_count")
        if left["palette_count"] != right["palette_count"]:
            differences.append(f"entry_{entry}_palette_count")
        if left["raw_size"] != right["raw_size"]:
            differences.append(f"entry_{entry}_raw_size")
        if left["raw_sha256"] != right["raw_sha256"]:
            differences.append(f"entry_{entry}_raw_hash")
    if not differences:
        raise EvidenceError("unexpectedly found no structural difference between Switch and PC fonts")
    return {
        "schema": "nobu16.kr.font-seoulhangang-v1-switch-pc-compatibility.v1",
        "inspection": {
            "read_only": True,
            "switch_resource_exported": False,
            "switch_g1n_exported": False,
            "switch_glyph_pixels_exported": False,
            "installed_game_files_modified": False,
        },
        "sources": {
            "switch_patch_release": {
                "repository": "https://github.com/snake7594/nobunaga-shinsei-korean-patch",
                "release": "https://github.com/snake7594/nobunaga-shinsei-korean-patch/releases/tag/v1.1",
                "asset_sha256": SWITCH_RELEASE_ZIP_SHA256,
            },
            "pc_stock": {"path": "RES_SC/res_lang.bin", "sha256": PC_STOCK_SHA256},
        },
        "switch": switch,
        "pc": pc,
        "raw_copy_compatible": False,
        "raw_copy_reasons": [
            "PC PK runtime target is RES_SC/res_lang.bin, while the Switch overlay is RES_JP/res_lang.bin",
            *differences,
        ],
        "conclusion": "Use the official SeoulHangang TTF as a local raster input and rebuild PC SC entries 6/7; do not copy Switch resources.",
    }


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


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--switch-release-zip", type=Path, required=True)
    parser.add_argument("--pc-stock-archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        switch_blob = extract_switch_resource(args.switch_release_zip.resolve())
        pc_blob = args.pc_stock_archive.resolve().read_bytes()
        evidence = build_evidence(switch_blob, pc_blob)
        atomic_write(args.output.resolve(), (json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
        print(f"output={args.output.resolve()}")
        print("raw_copy_compatible=False")
        return 0
    except (EvidenceError, OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
