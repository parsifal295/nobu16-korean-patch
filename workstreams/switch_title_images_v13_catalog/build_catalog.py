#!/usr/bin/env python3
"""Build a source-free catalog for Switch v1.3 title-label texture slots.

The commercial Switch/PC resources are explicit read-only inputs.  The only
output is JSON metadata: hashes, dimensions, format fields, layout metrics and
human-reviewed Korean labels.  No G1T, compressed wrapper, decoded pixel, LINK
archive or complete ``res_lang.bin`` is written by this program.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


WORKSTREAM_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = WORKSTREAM_DIR.parents[1]
TOOLS_DIR = PROJECT_ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import nobu16_lz4 as lz4  # noqa: E402


SWITCH_RELEASE_VERSION = "v1.3"
SWITCH_RELEASE_URL = (
    "https://github.com/snake7594/nobunaga-shinsei-korean-patch/releases/tag/v1.3"
)
SWITCH_ZIP_SHA256 = "F4D2563C1B32DB450165C8CCF61C6947DEA904233581036E179AFA1D6A918CC4"
SWITCH_RES_LANG_MEMBER = "NobunagaShinsei_KR/romfs/RES_JP/res_lang.bin"
SWITCH_RES_LANG_SHA256 = "79B572CE211A4D18F2A6CDF0AFD0197802463D270797993BA169F0D6BB651159"
SWITCH_OUTER_ENTRY3_SHA256 = "DFFBDC025C8B6582782DB5F195676F93C5EE1442C5A9CC364EB170DB21AF2B95"
PC_OUTER_ENTRY3_SHA256 = "D358F20570582E47515EE78D4D3B77FCBAC854297F2E043D86D9159D27875B1A"

TITLE_GROUP_INDEX = 3
TITLE_SLOT_START = 0
TITLE_SLOT_END = 107
TITLE_SLOT_COUNT = TITLE_SLOT_END - TITLE_SLOT_START + 1
GROUP_SLOT_COUNT = 110
GROUP_FIXED_HEADER_SIZE = 0x20
GROUP_METADATA_RECORD_SIZE = 12
G1T_MAGIC_VERSION = b"GT1G0600"
G1T_TEXTURE_COUNT = 1
G1T_FORMAT_BC3 = 0x5B

# Source-free result of the private 108-pair pixel/contact-sheet review.  The
# decoded commercial pixels stay below tmp/**/private and are never emitted by
# this builder.  "Index-for-index" below therefore means archive structure,
# not that every Switch caption has the same meaning as the PC caption at that
# index.
SEMANTIC_PIXEL_AUDIT = {
    "reviewed_pairs": TITLE_SLOT_COUNT,
    "structural_slot_mapping_verified": True,
    "strict_semantic_index_mapping_verified": False,
    "direct_all_108_pixel_import_allowed": False,
    "raw_switch_resource_copy_allowed": False,
    "safe_translation_reference_count": 101,
    "placeholder_indices": [0],
    "definite_semantic_mismatch_indices": [24, 25],
    "terminology_or_distinction_review_indices": [15, 37, 38, 74],
    "required_remap_or_redraw_indices": [0, 24, 25],
    "switch_unique_bc3_count": 106,
    "switch_unique_rgba_count": 106,
    "switch_duplicate_pixel_groups": [[23, 42], [37, 38]],
    "pc_unique_bc3_count": 108,
    "pc_unique_rgba_count": 108,
    "v11_v13_identical_rgba_count": 0,
    "pc_rebuild_probe": {
        "indices": [1, 8],
        "covered_switch_dimensions": [[512, 64], [512, 128]],
        "placement": "vertical center without scaling (provisional)",
        "full_pc_link_rebuild_valid": True,
        "game_input_unchanged": True,
        "candidate_archives_written": False,
        "decoded_max_channel_error_by_index": {"1": 9, "8": 8},
        "runtime_screen_position_verified": False,
    },
    "notes": [
        "Switch /3/0 visibly says a temporary-caption placeholder while PC /3/0 means transaction-content overview.",
        "Switch /3/24 and /3/25 carry the two related Korean labels in the opposite semantic order from PC /3/24 and /3/25.",
        "Switch /3/37 and /3/38 are byte- and pixel-identical although the two PC captions distinguish army-force and unit organization.",
        "Every reusable translation must still be rendered onto the PC 512x128 texture layout; Switch G1T/LINK bytes are not a PC payload.",
        "An in-memory PC rebuild probe passed for one 512x64 and one 512x128 Switch source, but centered placement still requires runtime screen verification.",
    ],
}


class CatalogError(ValueError):
    """Raised when a pinned source or title-group invariant fails."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CatalogError(message)


@dataclass(frozen=True)
class GroupSlot:
    index: int
    offset: int
    stored_size: int
    stored: bytes
    metadata: bytes


@dataclass(frozen=True)
class TitleGroup:
    blob: bytes
    slot_count: int
    table_offset: int
    logical_count: int
    metadata_offset: int
    slots: tuple[GroupSlot, ...]


def parse_title_group(blob: bytes, *, label: str) -> TitleGroup:
    require(len(blob) >= GROUP_FIXED_HEADER_SIZE, f"{label}: title group is truncated")
    require(blob[:4] == b"LINK", f"{label}: title group does not start with LINK")
    slot_count, table_offset, logical_count, metadata_offset = struct.unpack_from(
        "<IIII", blob, 4
    )
    require(slot_count == GROUP_SLOT_COUNT, f"{label}: slot_count={slot_count}, expected 110")
    require(logical_count == GROUP_SLOT_COUNT, f"{label}: logical_count={logical_count}, expected 110")
    require(table_offset == GROUP_FIXED_HEADER_SIZE, f"{label}: unexpected table offset")
    table_end = table_offset + slot_count * 8
    require(table_end <= metadata_offset, f"{label}: slot table overlaps metadata")
    metadata_end = metadata_offset + slot_count * GROUP_METADATA_RECORD_SIZE
    require(metadata_end <= len(blob), f"{label}: metadata table is truncated")

    slots: list[GroupSlot] = []
    for index in range(slot_count):
        offset, stored_size = struct.unpack_from("<II", blob, table_offset + index * 8)
        metadata_start = metadata_offset + index * GROUP_METADATA_RECORD_SIZE
        metadata = blob[metadata_start : metadata_start + GROUP_METADATA_RECORD_SIZE]
        # Switch v1.3 intentionally replaces slots 0..107.  Its trailing table
        # offsets for untouched slots 108/109 lie outside the shortened group;
        # they are recorded as unavailable rather than dereferenced.
        stored = blob[offset : offset + stored_size] if offset + stored_size <= len(blob) else b""
        slots.append(GroupSlot(index, offset, stored_size, stored, metadata))

    for index in range(TITLE_SLOT_START, TITLE_SLOT_END + 1):
        slot = slots[index]
        require(slot.stored_size > 0, f"{label}: title slot {index} is empty")
        require(
            len(slot.stored) == slot.stored_size,
            f"{label}: title slot {index} points outside the group",
        )
    return TitleGroup(
        blob=blob,
        slot_count=slot_count,
        table_offset=table_offset,
        logical_count=logical_count,
        metadata_offset=metadata_offset,
        slots=tuple(slots),
    )


def parse_single_bc3_g1t(raw: bytes, *, label: str) -> dict[str, Any]:
    require(raw[:8] == G1T_MAGIC_VERSION, f"{label}: not GT1G0600")
    require(len(raw) >= 0x38, f"{label}: G1T is truncated")
    declared_size, header_size, texture_count, platform = struct.unpack_from("<IIII", raw, 8)
    require(declared_size == len(raw), f"{label}: declared G1T size mismatch")
    require(header_size == 0x20, f"{label}: unexpected G1T header size")
    require(texture_count == G1T_TEXTURE_COUNT, f"{label}: texture_count is not 1")
    texture_relative_offset = struct.unpack_from("<I", raw, 0x18)[0]
    require(texture_relative_offset == 0, f"{label}: unexpected texture offset")
    texture_header = raw[header_size : header_size + 0x18]
    require(len(texture_header) == 0x18, f"{label}: texture header is truncated")
    format_code = texture_header[5]
    require(format_code == G1T_FORMAT_BC3, f"{label}: format is not 0x5B BC3")
    dimensions = texture_header[6]
    width = 1 << (dimensions & 0x0F)
    height = 1 << (dimensions >> 4)
    require(width % 4 == 0 and height % 4 == 0, f"{label}: invalid BC3 dimensions")
    bc3_size = width * height
    pixel_offset = len(raw) - bc3_size
    require(pixel_offset == 0x38, f"{label}: unexpected BC3 payload offset")
    bc3 = raw[pixel_offset:]
    return {
        "g1t_sha256": sha256(raw),
        "g1t_size": len(raw),
        "g1t_version": raw[4:8].decode("ascii"),
        "g1t_header_size": header_size,
        "g1t_platform_u32": platform,
        "texture_header_hex": texture_header.hex().upper(),
        "format_code": f"0x{format_code:02X}",
        "format_name": "BC3/DXT5",
        "width": width,
        "height": height,
        "bc3_payload_offset": pixel_offset,
        "bc3_payload_size": len(bc3),
        "bc3_sha256": sha256(bc3),
    }


def slot_metadata(slot: GroupSlot, *, source: str) -> dict[str, Any]:
    header, raw = lz4.decompress_wrapper(slot.stored)
    g1t = parse_single_bc3_g1t(raw, label=f"{source} /3/{slot.index}")
    return {
        "path": f"/3/{slot.index}",
        "group_offset": slot.offset,
        "stored_size": slot.stored_size,
        "stored_sha256": sha256(slot.stored),
        "wrapper_prefix_hex": header.prefix.hex().upper(),
        "wrapper_uncompressed_size": header.uncompressed_size,
        "wrapper_compressed_size": header.compressed_size,
        "group_metadata_hex": slot.metadata.hex().upper(),
        **g1t,
    }


def read_switch_archive(path: Path) -> tuple[bytes, dict[str, Any]]:
    zip_blob = path.read_bytes()
    require(sha256(zip_blob) == SWITCH_ZIP_SHA256, "Switch v1.3 ZIP SHA-256 mismatch")
    with zipfile.ZipFile(path) as archive:
        matching = [name for name in archive.namelist() if name == SWITCH_RES_LANG_MEMBER]
        require(len(matching) == 1, "Switch ZIP has no unique RES_JP/res_lang.bin")
        res_lang = archive.read(matching[0])
    require(sha256(res_lang) == SWITCH_RES_LANG_SHA256, "Switch res_lang SHA-256 mismatch")
    outer = lz4.parse_link(res_lang)
    require(lz4.rebuild_link(outer) == res_lang, "Switch outer LINK identity failed")
    require(len(outer.entries) > TITLE_GROUP_INDEX, "Switch outer LINK has no entry 3")
    group_blob = outer.entries[TITLE_GROUP_INDEX].data
    require(sha256(group_blob) == SWITCH_OUTER_ENTRY3_SHA256, "Switch /3 SHA-256 mismatch")
    return group_blob, {
        "release": SWITCH_RELEASE_VERSION,
        "release_url": SWITCH_RELEASE_URL,
        "zip_sha256": SWITCH_ZIP_SHA256,
        "zip_size": len(zip_blob),
        "res_lang_member": SWITCH_RES_LANG_MEMBER,
        "res_lang_sha256": SWITCH_RES_LANG_SHA256,
        "res_lang_size": len(res_lang),
        "outer_link_entry": TITLE_GROUP_INDEX,
        "outer_link_entry_sha256": SWITCH_OUTER_ENTRY3_SHA256,
        "outer_link_entry_size": len(group_blob),
    }


def read_pc_archive(path: Path) -> tuple[bytes, dict[str, Any]]:
    res_lang = path.read_bytes()
    outer = lz4.parse_link(res_lang)
    require(lz4.rebuild_link(outer) == res_lang, "PC outer LINK identity failed")
    require(len(outer.entries) > TITLE_GROUP_INDEX, "PC outer LINK has no entry 3")
    group_blob = outer.entries[TITLE_GROUP_INDEX].data
    require(sha256(group_blob) == PC_OUTER_ENTRY3_SHA256, "PC /3 SHA-256 mismatch")
    return group_blob, {
        "runtime_path": "RES_SC/res_lang.bin",
        "input_res_lang_sha256": sha256(res_lang),
        "input_res_lang_size": len(res_lang),
        "outer_link_entry": TITLE_GROUP_INDEX,
        "outer_link_entry_sha256": PC_OUTER_ENTRY3_SHA256,
        "outer_link_entry_size": len(group_blob),
        "note": "Entry /3 is byte-identical across the audited SC font-only candidates.",
    }


def read_labels(path: Path) -> Mapping[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(payload, dict), "labels file must be a JSON object")
    labels = payload.get("labels")
    require(isinstance(labels, dict), "labels file must contain a labels object")
    allowed = {str(index) for index in range(TITLE_SLOT_START, TITLE_SLOT_END + 1)}
    require(set(labels).issubset(allowed), "labels file contains an out-of-range slot")
    return labels


def build_catalog(
    *, switch_zip: Path, pc_res_lang: Path, labels_path: Path
) -> dict[str, Any]:
    switch_group_blob, switch_source = read_switch_archive(switch_zip)
    pc_group_blob, pc_source = read_pc_archive(pc_res_lang)
    switch_group = parse_title_group(switch_group_blob, label="Switch v1.3 /3")
    pc_group = parse_title_group(pc_group_blob, label="PC SC /3")
    labels = read_labels(labels_path)

    entries: list[dict[str, Any]] = []
    readable = 0
    needs_review = 0
    switch_dimensions: dict[str, int] = {}
    for index in range(TITLE_SLOT_START, TITLE_SLOT_END + 1):
        switch = slot_metadata(switch_group.slots[index], source="Switch")
        pc = slot_metadata(pc_group.slots[index], source="PC")
        label_data = labels.get(str(index), {})
        require(isinstance(label_data, dict), f"label {index} must be an object")
        korean = label_data.get("korean")
        status = label_data.get("status", "needs_review")
        confidence = label_data.get("confidence")
        note = label_data.get("note")
        if status == "verified":
            require(isinstance(korean, str) and korean.strip(), f"verified label {index} is empty")
            readable += 1
        else:
            require(status == "needs_review", f"unsupported label status at slot {index}")
            require(korean in (None, ""), f"unverified label {index} must not publish text")
            korean = None
            needs_review += 1
        key = f"{switch['width']}x{switch['height']}"
        switch_dimensions[key] = switch_dimensions.get(key, 0) + 1
        entries.append(
            {
                "id": index,
                "path": f"/3/{index}",
                "korean_label": korean,
                "label_status": status,
                "label_confidence": confidence,
                "label_note": note,
                "layout": {
                    "switch_dimensions": [switch["width"], switch["height"]],
                    "pc_dimensions": [pc["width"], pc["height"]],
                    "requires_pc_canvas_expansion": switch["height"] != pc["height"],
                },
                "switch": switch,
                "pc": pc,
            }
        )

    require(len(entries) == TITLE_SLOT_COUNT, "catalog entry count mismatch")
    return {
        "schema": "nobu16.switch-title-image-catalog.v0.1",
        "source_free": True,
        "contains_commercial_pixels": False,
        "contains_g1t_or_link_payloads": False,
        "scope": {
            "switch_paths": "/3/0..107",
            "pc_paths": "/3/0..107",
            "correlation": "structural slot index-for-index only",
            "semantic_correlation": "not strict; see semantic_pixel_audit",
            "entry_count": TITLE_SLOT_COUNT,
            "switch_group_slot_count": switch_group.slot_count,
            "pc_group_slot_count": pc_group.slot_count,
        },
        "sources": {"switch": switch_source, "pc": pc_source},
        "summary": {
            "entries": len(entries),
            "verified_korean_labels": readable,
            "needs_review": needs_review,
            "switch_dimensions": dict(sorted(switch_dimensions.items())),
            "pc_dimensions": {"512x128": len(entries)},
            "switch_format": "0x5B BC3/DXT5",
            "pc_format": "0x5B BC3/DXT5",
        },
        "semantic_pixel_audit": SEMANTIC_PIXEL_AUDIT,
        "entries": entries,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--switch-zip", type=Path, required=True)
    parser.add_argument("--pc-res-lang", type=Path, required=True)
    parser.add_argument(
        "--labels",
        type=Path,
        default=WORKSTREAM_DIR / "labels.review.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=WORKSTREAM_DIR / "catalog.v0.1.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    catalog = build_catalog(
        switch_zip=args.switch_zip,
        pc_res_lang=args.pc_res_lang,
        labels_path=args.labels,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"output={args.output}")
    print(f"entries={catalog['summary']['entries']}")
    print(f"verified_korean_labels={catalog['summary']['verified_korean_labels']}")
    print(f"needs_review={catalog['summary']['needs_review']}")
    print(f"switch_dimensions={catalog['summary']['switch_dimensions']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
