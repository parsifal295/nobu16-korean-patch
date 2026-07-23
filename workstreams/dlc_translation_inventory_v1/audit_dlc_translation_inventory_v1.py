#!/usr/bin/env python3
"""Inventory the current NOBU16 DLC translation surface without modifying it.

The DLC containers use three layers:

1. an executable-keyed byte stream cipher,
2. an optional raw-LZ4 wrapper, and
3. an XL13 string-pointer table.

This audit counts XL records, removes empty and known non-display metadata
records, and reports both physical patch locations and exact source-string
deduplication.  Inputs are always opened read-only.  The only optional write is
the JSON report selected by ``--output``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from nobu16_lz4 import raw_lz4_decompress  # noqa: E402


LCG_MULTIPLIER = 0x6C078965
LCG_INCREMENT = 0x3039
LANGUAGES = ("EN", "JP", "SC", "TC")

# RVA and one-language-block length in the current PK executable.
KEY_TABLES = {
    "scem": (0x1AE5190, 0x1E0),
    "gm": (0x1AE5950, 0x190),
    "gfpk": (0x1AE6010, 0x188),
    "bmt": (0x1AE61A0, 0x12C0),
    "evm": (0x1AEAEB0, 0x328),
    "tom": (0x1AEBBE0, 0x258),
}


@dataclass(frozen=True)
class FileSpec:
    family: str
    key_id: int
    cipher_id: int


@dataclass(frozen=True)
class XlRecord:
    row: int
    code_units: tuple[int, ...]


class AuditError(ValueError):
    """Raised when an input violates a validated DLC format invariant."""


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def lcg_step(state: int) -> int:
    return (state * LCG_MULTIPLIER + LCG_INCREMENT) & 0xFFFFFFFF


def lcg_byte(state: int) -> int:
    return ((state >> 24) ^ (state >> 16)) & 0xFF


class PeImage:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.blob = path.read_bytes()
        pe_offset = struct.unpack_from("<I", self.blob, 0x3C)[0]
        section_count = struct.unpack_from("<H", self.blob, pe_offset + 6)[0]
        optional_size = struct.unpack_from("<H", self.blob, pe_offset + 20)[0]
        section_table = pe_offset + 24 + optional_size
        sections: list[tuple[int, int, int]] = []
        for index in range(section_count):
            offset = section_table + index * 40
            virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from(
                "<IIII", self.blob, offset + 8
            )
            sections.append((virtual_address, max(virtual_size, raw_size), raw_pointer))
        self.sections = tuple(sections)

    def read_rva(self, rva: int, size: int) -> bytes:
        for virtual_address, span, raw_pointer in self.sections:
            if virtual_address <= rva < virtual_address + span:
                start = raw_pointer + rva - virtual_address
                end = start + size
                if end > len(self.blob):
                    raise AuditError(f"RVA 0x{rva:X} extends beyond {self.path}")
                return self.blob[start:end]
        raise AuditError(f"RVA 0x{rva:X} is not mapped by {self.path}")


class DlcDecoder:
    def __init__(self, executable: Path) -> None:
        self.pe = PeImage(executable)
        self.keys: dict[str, dict[int, int]] = {}
        for family, (rva, length) in KEY_TABLES.items():
            table: dict[int, int] = {}
            for key_id, raw_key in struct.iter_unpack("<II", self.pe.read_rva(rva, length)):
                if key_id == 0xFFFFFFFF or raw_key in (0, 0xFFFFFFFF):
                    continue
                # Some padded tables repeat zero-valued IDs.  The first real
                # record is the one reached by the game's linear lookup.
                table.setdefault(key_id, raw_key)
            self.keys[family] = table

    def _seed(self, spec: FileSpec) -> int:
        try:
            raw_key = self.keys[spec.family][spec.key_id]
        except KeyError as exc:
            raise AuditError(f"missing {spec.family} key {spec.key_id}") from exc
        state = (spec.cipher_id * spec.cipher_id) & 0xFFFFFFFF
        decoded_key = bytearray(struct.pack("<I", raw_key))
        for index in range(4):
            state = lcg_step(state)
            decoded_key[index] ^= lcg_byte(state)
        return (struct.unpack("<I", decoded_key)[0] + spec.cipher_id) & 0xFFFFFFFF

    def decrypt(self, path: Path, spec: FileSpec) -> bytes:
        state = self._seed(spec)
        output = bytearray()
        for value in path.read_bytes():
            state = lcg_step(state)
            output.append(value ^ lcg_byte(state))
        return bytes(output)

    def decode_xl(self, path: Path, spec: FileSpec) -> bytes:
        wrapper = self.decrypt(path, spec)
        if len(wrapper) < 24:
            raise AuditError(f"short DLC wrapper: {path}")
        uncompressed_size, compressed_size = struct.unpack_from("<QQ", wrapper, 8)
        payload = wrapper[24:]
        if compressed_size == 0:
            if len(payload) != uncompressed_size:
                raise AuditError(
                    f"raw wrapper length mismatch for {path}: "
                    f"{len(payload)} != {uncompressed_size}"
                )
            raw = payload
        else:
            if len(payload) != compressed_size:
                raise AuditError(
                    f"compressed wrapper length mismatch for {path}: "
                    f"{len(payload)} != {compressed_size}"
                )
            raw = raw_lz4_decompress(payload, uncompressed_size)
        if not raw.startswith(b"XL\x13\0"):
            raise AuditError(f"decoded payload is not XL13: {path}")
        return raw


def file_spec(path: Path) -> FileSpec:
    name = path.name
    match = re.fullmatch(r"scem_(\d{3})\.n16", name)
    if match:
        number = int(match.group(1))
        return FileSpec("scem", number, number)
    match = re.fullmatch(r"gm_(\d{4})\.n16", name)
    if match:
        number = int(match.group(1))
        return FileSpec("gm", number, number)
    match = re.fullmatch(r"bmt_(\d+)\.n16", name)
    if match:
        number = int(match.group(1)) - 55
        return FileSpec("bmt", number, number)
    match = re.fullmatch(r"evm_(\d{3})\.n16", name)
    if match:
        number = int(match.group(1))
        return FileSpec("evm", number, number)
    match = re.fullmatch(r"tom_(\d{4})\.n16", name)
    if match:
        number = int(match.group(1))
        return FileSpec("tom", number, number)
    raise AuditError(f"unsupported localized DLC filename: {path}")


def is_translation_container(path: Path) -> bool:
    return bool(re.fullmatch(r"(?:scem_\d{3}|gm_\d{4}|bmt_\d+|evm_\d{3}|tom_\d{4})\.n16", path.name))


def parse_xl_records(raw: bytes) -> tuple[int, tuple[XlRecord, ...]]:
    if len(raw) < 20 or raw[:4] != b"XL\x13\0":
        raise AuditError("not an XL13 payload")
    _, _, file_size, type_count, sets, width, table_offset, _ = struct.unpack_from(
        "<HHHHHhhh", raw, 0
    )
    if file_size != len(raw):
        raise AuditError(f"XL size field {file_size} != decoded size {len(raw)}")
    types = raw[16 : 16 + type_count]
    records: list[XlRecord] = []
    for row in range(sets):
        row_base = table_offset + row * width
        local = 0
        for field_type in types:
            if field_type == 0:
                relative = struct.unpack_from("<i", raw, row_base + local)[0]
                position = table_offset + relative
                if position < 0 or position >= len(raw):
                    raise AuditError(
                        f"XL row {row} pointer 0x{relative & 0xFFFFFFFF:X} is out of range"
                    )
                values: list[int] = []
                while position + 1 < len(raw):
                    value = struct.unpack_from("<H", raw, position)[0]
                    position += 2
                    if value == 0:
                        break
                    values.append(value)
                records.append(XlRecord(row, tuple(values)))
                local += 4
            elif field_type in (1, 4, 7):
                local += 4
            elif field_type in (2, 5):
                local += 2
            elif field_type in (3, 6):
                local += 1
            elif field_type == 0xFF:
                continue
            else:
                raise AuditError(f"unsupported XL field type 0x{field_type:02X}")
    return sets, tuple(records)


def is_visible_record(family: str, record: XlRecord) -> bool:
    if not record.code_units:
        return False
    if family == "evm":
        # 257 is a locale sort key; 258..267 are event-condition templates.
        return record.row <= 256
    if family == "tom":
        # Row 1 is the locale sort key between display name and description.
        return record.row in (0, 2)
    return True


def summarize_files(
    paths: Iterable[Path], decoder: DlcDecoder, base: Path
) -> tuple[dict[str, object], list[dict[str, object]], set[tuple[int, ...]]]:
    rows: list[dict[str, object]] = []
    global_sources: set[tuple[int, ...]] = set()
    physical_records = 0
    source_units = 0
    slots = 0
    nonempty = 0
    for path in sorted(paths):
        spec = file_spec(path)
        raw = decoder.decode_xl(path, spec)
        _, records = parse_xl_records(raw)
        visible = [record for record in records if is_visible_record(spec.family, record)]
        populated = [record for record in records if record.code_units]
        sources = {record.code_units for record in visible}
        global_sources.update(sources)
        slots += len(records)
        nonempty += len(populated)
        physical_records += len(visible)
        units = sum(len(record.code_units) for record in visible)
        source_units += units
        rows.append(
            {
                "path": path.relative_to(base).as_posix(),
                "family": spec.family,
                "xl_slots": len(records),
                "nonempty_records": len(populated),
                "excluded_internal_records": len(populated) - len(visible),
                "translation_records": len(visible),
                "unique_source_strings_in_file": len(sources),
                "source_code_units": units,
                "decoded_xl_sha256": sha256_bytes(raw),
            }
        )
    summary = {
        "files": len(rows),
        "xl_slots": slots,
        "nonempty_records": nonempty,
        "excluded_internal_records": nonempty - physical_records,
        "translation_records": physical_records,
        "unique_source_strings": len(global_sources),
        "source_code_units": source_units,
        "unique_source_code_units": sum(len(source) for source in global_sources),
    }
    return summary, rows, global_sources


def group_summary(rows: Sequence[dict[str, object]]) -> dict[str, dict[str, int]]:
    grouped: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "files": 0,
            "xl_slots": 0,
            "nonempty_records": 0,
            "excluded_internal_records": 0,
            "translation_records": 0,
            "source_code_units": 0,
        }
    )
    for row in rows:
        family = str(row["family"])
        group = grouped[family]
        group["files"] += 1
        for key in (
            "xl_slots",
            "nonempty_records",
            "excluded_internal_records",
            "translation_records",
            "source_code_units",
        ):
            group[key] += int(row[key])
    return dict(sorted(grouped.items()))


def relative_files(root: Path) -> dict[str, Path]:
    if not root.exists():
        return {}
    return {path.relative_to(root).as_posix(): path for path in root.rglob("*") if path.is_file()}


def delta_summary(live: Path, legacy: Path) -> dict[str, object]:
    current = relative_files(live)
    old = relative_files(legacy)
    new_paths = sorted(current.keys() - old.keys())
    removed_paths = sorted(old.keys() - current.keys())
    common = current.keys() & old.keys()
    changed_paths = sorted(
        relative for relative in common if sha256_file(current[relative]) != sha256_file(old[relative])
    )
    return {
        "current_files": len(current),
        "legacy_files": len(old),
        "new_paths": len(new_paths),
        "changed_existing_paths": len(changed_paths),
        "unchanged_existing_paths": len(common) - len(changed_paths),
        "removed_paths": len(removed_paths),
    }


def verify_legacy_localized_payloads(
    live_root: Path, legacy_root: Path, decoder: DlcDecoder
) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for language in LANGUAGES:
        old_dir = legacy_root / "DLC_PK" / language
        live_dir = live_root / "DLC_PK" / language
        if not old_dir.exists():
            continue
        for old_path in sorted(old_dir.glob("*.n16")):
            if not is_translation_container(old_path):
                continue
            live_path = live_dir / old_path.name
            if not live_path.exists():
                continue
            spec = file_spec(old_path)
            old_raw = decoder.decode_xl(old_path, spec)
            live_raw = decoder.decode_xl(live_path, spec)
            rows.append(
                {
                    "language": language,
                    "file": old_path.name,
                    "payload_equal": old_raw == live_raw,
                }
            )
    different = [row for row in rows if not row["payload_equal"]]
    return {
        "compared_payloads": len(rows),
        "equal_payloads": len(rows) - len(different),
        "different_payloads": different,
    }


def inspect_new_gfpk(live_root: Path, legacy_root: Path, decoder: DlcDecoder) -> dict[str, object]:
    live_dir = live_root / "DLC_PK" / "Common"
    old_names = {path.name for path in (legacy_root / "DLC_PK" / "Common").glob("gfPK_*.n16")}
    rows: list[dict[str, object]] = []
    for path in sorted(live_dir.glob("gfPK_*.n16")):
        if path.name in old_names:
            continue
        match = re.fullmatch(r"gfPK_(\d{5})\.n16", path.name)
        if not match:
            continue
        number = int(match.group(1))
        raw = decoder.decrypt(path, FileSpec("gfpk", number, number))
        rows.append(
            {
                "file": path.name,
                "stil_container": raw.startswith(b"STIL"),
                "embedded_gt1g_images": raw.count(b"GT1G"),
            }
        )
    return {
        "files": len(rows),
        "stil_files": sum(bool(row["stil_container"]) for row in rows),
        "files_with_five_gt1g_images": sum(row["embedded_gt1g_images"] == 5 for row in rows),
        "items": rows,
    }


def build_inventory(game_root: Path, legacy_root: Path) -> dict[str, object]:
    executable = game_root / "NOBU16PK.exe"
    decoder = DlcDecoder(executable)

    live_pk_jp = game_root / "DLC_PK" / "JP"
    old_pk_jp = legacy_root / "DLC_PK" / "JP"
    old_pk_names = {path.name for path in old_pk_jp.glob("*.n16")}
    new_translation_paths = [
        path
        for path in live_pk_jp.glob("*.n16")
        if is_translation_container(path) and path.name not in old_pk_names
    ]
    new_summary, new_rows, new_sources = summarize_files(
        new_translation_paths, decoder, game_root
    )

    full_translation_paths: list[Path] = []
    for area in ("DLC", "DLC_PK"):
        full_translation_paths.extend(
            path
            for path in (game_root / area / "JP").glob("*.n16")
            if is_translation_container(path)
        )
    full_summary, full_rows, full_sources = summarize_files(
        full_translation_paths, decoder, game_root
    )

    by_area: dict[str, dict[str, int]] = {}
    for area in ("DLC", "DLC_PK"):
        area_rows = [row for row in full_rows if str(row["path"]).startswith(area + "/")]
        by_area[area] = {
            "files": len(area_rows),
            "translation_records": sum(int(row["translation_records"]) for row in area_rows),
        }

    return {
        "schema_version": 1,
        "audit_date": "2026-07-22",
        "inputs": {
            "game_root": str(game_root),
            "legacy_root": str(legacy_root),
            "executable_sha256": sha256_file(executable),
        },
        "filesystem_delta": {
            "DLC": delta_summary(game_root / "DLC", legacy_root / "DLC"),
            "DLC_PK": delta_summary(game_root / "DLC_PK", legacy_root / "DLC_PK"),
        },
        "new_translation_scope": {
            "summary": new_summary,
            "by_family": group_summary(new_rows),
            "files": new_rows,
        },
        "full_current_translation_scope": {
            "summary": full_summary,
            "by_area": by_area,
            "by_family": group_summary(full_rows),
            "files": full_rows,
            "new_only_unique_source_strings": len(new_sources),
            "preexisting_only_unique_source_strings": len(full_sources - new_sources),
        },
        "legacy_localized_payload_check": verify_legacy_localized_payloads(
            game_root, legacy_root, decoder
        ),
        "new_common_gfpk_check": inspect_new_gfpk(game_root, legacy_root, decoder),
        "counting_policy": {
            "empty_xl_records": "excluded",
            "evm_rows_257_267": "excluded as sort keys / event-condition metadata",
            "tom_row_1": "excluded as locale sort key",
            "physical_translation_record": "one visible XL pointer record in one JP file",
            "unique_source_string": "exact tuple of JP 16-bit source code units",
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--game-root",
        type=Path,
        default=Path(r"F:\SteamLibrary\steamapps\common\NOBU16"),
    )
    parser.add_argument(
        "--legacy-root",
        type=Path,
        default=Path(r"I:\Workspaces\NOBU16-Korean\private-inputs\legacy-pc-root"),
    )
    parser.add_argument("--output", type=Path, help="Write the inventory as UTF-8 JSON")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    inventory = build_inventory(args.game_root.resolve(), args.legacy_root.resolve())
    rendered = json.dumps(inventory, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = args.output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(f"output={output}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
