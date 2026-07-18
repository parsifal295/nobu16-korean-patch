#!/usr/bin/env python3
"""Patch name-validation failures in unpacked NOBU16PK 1.1.7.

The officer-editor patch is deliberately applied inside validator RVA
0x00BB0110.  The fictional-princess naming patch is deliberately applied to
the four character-predicate calls inside RVA 0x00EB4660, replacing each call
with ``mov eax, 1``.  Both patches remain caller-scoped; the shared character
validators are not changed.  Optionally, the officer editor's combined-name
length failure branch can also be forced to its existing continue path.

Only the exact pinned Steamless v3.1.0.5 output is accepted, and output inside
the live Steam game directory is refused.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path


EXPECTED_INPUT_SHA256 = (
    "BC885875A5E4288E5A1A424D99974F6F215777C03569C7EA707FDE63BDBC2B39"
)
EXPECTED_ENTRY_RVA = 0x012FE4D0
EXPECTED_FUNCTION_RVA = 0x00BB0110
EXPECTED_FUNCTION_PREFIX = bytes.fromhex(
    "48 89 5C 24 10 55 56 57 41 54 41 55 41 56 41 57 48 83 EC 30"
)
EXPECTED_PRINCESS_FUNCTION_RVA = 0x00EB4660
EXPECTED_PRINCESS_FUNCTION_PREFIX = bytes.fromhex(
    "40 53 48 81 EC 80 00 00 00 83 B9 E8 01 00 00 00 48 8B D9"
)

PATCHES = {
    "visible_surname_character": {
        "rva": 0x00BB0230,
        "before": bytes.fromhex("0F 84 B4 01 00 00"),
        "after": bytes.fromhex("90 90 90 90 90 90"),
        "meaning": (
            "do not jump to validator result 1 / EAX=0 when the visible "
            "surname character predicate returns zero"
        ),
    },
    "visible_given_name_character": {
        "rva": 0x00BB0240,
        "before": bytes.fromhex("0F 84 A4 01 00 00"),
        "after": bytes.fromhex("90 90 90 90 90 90"),
        "meaning": (
            "do not jump to validator result 1 / EAX=0 when the visible "
            "given-name character predicate returns zero"
        ),
    },
    "surname_reading_character": {
        "rva": 0x00BB0256,
        "before": bytes.fromhex("0F 84 8E 01 00 00"),
        "after": bytes.fromhex("90 90 90 90 90 90"),
        "meaning": (
            "do not jump to validator result 1 / EAX=0 when the surname "
            "reading-field character predicate returns zero"
        ),
    },
    "given_name_reading_character": {
        "rva": 0x00BB0267,
        "before": bytes.fromhex("0F 84 7D 01 00 00"),
        "after": bytes.fromhex("90 90 90 90 90 90"),
        "meaning": (
            "do not jump to validator result 1 / EAX=0 when the given-name "
            "reading-field character predicate returns zero"
        ),
    },
    "combined_name_length": {
        "rva": 0x00BB02C8,
        "before": bytes.fromhex("7E 0C"),
        "after": bytes.fromhex("EB 0C"),
        "meaning": (
            "always take the validator's existing in-range continuation "
            "instead of returning result 2 / EAX=0"
        ),
    },
    "princess_entered_name_character": {
        "rva": 0x00EB47BF,
        "before": bytes.fromhex("E8 4C 6E CE FF"),
        "after": bytes.fromhex("B8 01 00 00 00"),
        "meaning": (
            "make the fictional-princess entered-name character predicate "
            "succeed without changing its non-empty or length checks"
        ),
    },
    "princess_entered_reading_character": {
        "rva": 0x00EB47E0,
        "before": bytes.fromhex("E8 CB 6E CE FF"),
        "after": bytes.fromhex("B8 01 00 00 00"),
        "meaning": (
            "make the fictional-princess entered-reading character predicate "
            "succeed without changing its non-empty or length checks"
        ),
    },
    "princess_existing_surname_character": {
        "rva": 0x00EB484F,
        "before": bytes.fromhex("E8 BC 6D CE FF"),
        "after": bytes.fromhex("B8 01 00 00 00"),
        "meaning": (
            "make the fictional-princess inherited-surname character "
            "predicate succeed"
        ),
    },
    "princess_existing_surname_reading_character": {
        "rva": 0x00EB4878,
        "before": bytes.fromhex("E8 33 6E CE FF"),
        "after": bytes.fromhex("B8 01 00 00 00"),
        "meaning": (
            "make the fictional-princess inherited-surname-reading "
            "character predicate succeed"
        ),
    },
}

LIVE_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")


def sha256(data: bytes | bytearray) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def parse_pe(data: bytes | bytearray) -> dict[str, object]:
    if len(data) < 0x400 or data[:2] != b"MZ":
        raise ValueError("input is not a PE file")
    pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe_offset : pe_offset + 4] != b"PE\0\0":
        raise ValueError("invalid PE signature")
    coff = pe_offset + 4
    section_count = struct.unpack_from("<H", data, coff + 2)[0]
    optional_size = struct.unpack_from("<H", data, coff + 16)[0]
    optional = coff + 20
    if struct.unpack_from("<H", data, optional)[0] != 0x20B:
        raise ValueError("expected a PE32+ executable")
    entry_rva = struct.unpack_from("<I", data, optional + 16)[0]
    checksum_offset = optional + 64
    section_table = optional + optional_size
    sections: list[dict[str, int | str]] = []
    for index in range(section_count):
        offset = section_table + index * 40
        name = (
            data[offset : offset + 8].rstrip(b"\0").decode("ascii", errors="strict")
        )
        virtual_size, rva, raw_size, raw_offset = struct.unpack_from(
            "<IIII", data, offset + 8
        )
        characteristics = struct.unpack_from("<I", data, offset + 36)[0]
        sections.append(
            {
                "name": name,
                "rva": rva,
                "virtual_size": virtual_size,
                "raw_size": raw_size,
                "raw_offset": raw_offset,
                "characteristics": characteristics,
            }
        )
    return {
        "entry_rva": entry_rva,
        "checksum_offset": checksum_offset,
        "sections": sections,
    }


def rva_to_file_offset(pe: dict[str, object], rva: int) -> int:
    sections = pe["sections"]
    assert isinstance(sections, list)
    for section in sections:
        assert isinstance(section, dict)
        start = int(section["rva"])
        size = max(int(section["virtual_size"]), int(section["raw_size"]))
        if start <= rva < start + size:
            return int(section["raw_offset"]) + (rva - start)
    raise ValueError(f"RVA 0x{rva:X} is not mapped by a section")


def pe_checksum(data: bytes | bytearray, checksum_offset: int) -> int:
    total = 0
    length = len(data)
    for offset in range(0, length, 2):
        if checksum_offset <= offset < checksum_offset + 4:
            word = 0
        else:
            high = data[offset + 1] if offset + 1 < length else 0
            word = data[offset] | (high << 8)
        total = (total + word) & 0xFFFFFFFF
        total = (total & 0xFFFF) + (total >> 16)
    total = (total & 0xFFFF) + (total >> 16)
    return (total + length) & 0xFFFFFFFF


def outside_live_steam(path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(LIVE_STEAM_ROOT.resolve())
    except ValueError:
        return resolved
    raise ValueError(f"refusing to write inside the live Steam directory: {resolved}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="exact unpacked 1.1.7 executable")
    parser.add_argument("output", type=Path, help="patched output outside live Steam")
    parser.add_argument(
        "--include-length",
        action="store_true",
        help="also bypass the combined-name length failure (variant B)",
    )
    parser.add_argument("--force", action="store_true", help="replace output")
    args = parser.parse_args()

    try:
        output = outside_live_steam(args.output)
        if output.exists() and not args.force:
            raise ValueError(f"output already exists (use --force): {output}")
        original = args.input.resolve().read_bytes()
        original_hash = sha256(original)
        if original_hash != EXPECTED_INPUT_SHA256:
            raise ValueError(
                "input hash is not the pinned Steamless v3.1.0.5 output; "
                f"expected {EXPECTED_INPUT_SHA256}, got {original_hash}"
            )

        pe = parse_pe(original)
        if int(pe["entry_rva"]) != EXPECTED_ENTRY_RVA:
            raise ValueError(
                f"unexpected entry RVA 0x{int(pe['entry_rva']):X}; "
                f"expected 0x{EXPECTED_ENTRY_RVA:X}"
            )
        sections = pe["sections"]
        assert isinstance(sections, list)
        section_names = [str(item["name"]) for item in sections]
        if ".bind" in section_names or ".text" not in section_names:
            raise ValueError(f"unexpected unpacked section set: {section_names}")

        function_offset = rva_to_file_offset(pe, EXPECTED_FUNCTION_RVA)
        prefix = original[
            function_offset : function_offset + len(EXPECTED_FUNCTION_PREFIX)
        ]
        if prefix != EXPECTED_FUNCTION_PREFIX:
            raise ValueError(
                "validator function preimage mismatch at "
                f"RVA 0x{EXPECTED_FUNCTION_RVA:X}: {prefix.hex(' ').upper()}"
            )

        princess_function_offset = rva_to_file_offset(
            pe, EXPECTED_PRINCESS_FUNCTION_RVA
        )
        princess_prefix = original[
            princess_function_offset : princess_function_offset
            + len(EXPECTED_PRINCESS_FUNCTION_PREFIX)
        ]
        if princess_prefix != EXPECTED_PRINCESS_FUNCTION_PREFIX:
            raise ValueError(
                "fictional-princess naming function preimage mismatch at "
                f"RVA 0x{EXPECTED_PRINCESS_FUNCTION_RVA:X}: "
                f"{princess_prefix.hex(' ').upper()}"
            )

        selected = [
            "visible_surname_character",
            "visible_given_name_character",
            "surname_reading_character",
            "given_name_reading_character",
            "princess_entered_name_character",
            "princess_entered_reading_character",
            "princess_existing_surname_character",
            "princess_existing_surname_reading_character",
        ]
        variant = "A_editor_and_princess_character_checks"
        if args.include_length:
            selected.append("combined_name_length")
            variant = "B_editor_and_princess_character_checks_and_combined_length"

        patched = bytearray(original)
        records: list[dict[str, object]] = []
        for name in selected:
            spec = PATCHES[name]
            rva = int(spec["rva"])
            before = bytes(spec["before"])
            after = bytes(spec["after"])
            offset = rva_to_file_offset(pe, rva)
            actual = bytes(patched[offset : offset + len(before)])
            if actual != before:
                raise ValueError(
                    f"preimage mismatch for {name} at RVA 0x{rva:X}: "
                    f"{actual.hex(' ').upper()}"
                )
            patched[offset : offset + len(before)] = after
            records.append(
                {
                    "name": name,
                    "meaning": spec["meaning"],
                    "rva": f"0x{rva:08X}",
                    "file_offset": f"0x{offset:08X}",
                    "before": before.hex(" ").upper(),
                    "after": after.hex(" ").upper(),
                }
            )

        checksum_offset = int(pe["checksum_offset"])
        struct.pack_into("<I", patched, checksum_offset, 0)
        checksum = pe_checksum(patched, checksum_offset)
        struct.pack_into("<I", patched, checksum_offset, checksum)

        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_name(output.name + ".tmp")
        temporary.write_bytes(patched)
        os.replace(temporary, output)

        manifest = {
            "schema": "nobu16.static-name-validation-patch.v4",
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "variant": variant,
            "input": str(args.input.resolve()),
            "input_sha256": original_hash,
            "output": str(output),
            "output_sha256": sha256(patched),
            "pe_checksum": f"0x{checksum:08X}",
            "entry_rva": f"0x{int(pe['entry_rva']):08X}",
            "patches": records,
            "live_steam_files_written": False,
            "deprecated_dispatcher_patch_used": False,
            "deprecated_two_character_branch_patch_used": False,
            "all_four_character_failure_branches_patched": True,
            "princess_naming_character_predicates_patched": True,
            "shared_character_validators_modified": False,
        }
        manifest_path = output.with_name(output.name + ".manifest.json")
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, struct.error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
