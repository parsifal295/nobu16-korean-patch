#!/usr/bin/env python3
"""Transplant the complete Korean JP PK wheel into TC low/high atlas records.

The JP and Traditional-Chinese archives use the same semantic record order but
not the same atlas coordinates.  This builder therefore copies decoded sprites
record by record and keeps every TC LINK, G1T, layout-table, and packing
coordinate intact.  It never copies a whole JP archive or nested resource.
"""

from __future__ import annotations

import argparse
import dataclasses
import gc
import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from PIL import Image, ImageDraw


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parent.parent
TOOLS = REPO / "tools"
IMAGE_WORKSTREAM = REPO / "workstreams" / "steam_jp_port_highres_images_v1"
TITLE_WORKSTREAM = REPO / "workstreams" / "steam_jp_title_images_v1"
for candidate in (WORKSTREAM, TOOLS, IMAGE_WORKSTREAM, TITLE_WORKSTREAM):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import extract_nobu16_image_atlases as atlas_codec  # noqa: E402
import nobu16_lz4 as lz4  # noqa: E402
import pc_g1t_title_codec as bc_codec  # noqa: E402
import build_steam_jp_port_highres_images_v1 as base  # noqa: E402
import build_steam_jp_title_images_v1 as title_v1  # noqa: E402


SCHEMA = "nobu16.kr.tc-pk-wheel-from-jp-korean.v1"
PINS: dict[str, dict[str, Any]] = {
    "jp_low": {
        "size": 141_893_576,
        "sha256": "9019582ABBF88B08562B366E7D5A4283C6507455F86A801946AC32CCC25C2C2F",
    },
    "jp_high": {
        "size": 67_623_137,
        "sha256": "09531F21FA3BD56E2554C47942E47B5ACB61A7F279EFBF4AF85E4CAB963E4FAA",
    },
    "tc_low": {
        "size": 125_095_591,
        "sha256": "19C0149A7B4F9A5CA2672F61D4D8F3C3674FC343E33AEF3E4E1ED04BAFDC5B7B",
    },
    "tc_high": {
        "size": 22_537_924,
        "sha256": "42C82BEB4524FB0E4FC9ED61AFF1EDB24422F196EC7424A831EB9E687C94EB77",
    },
}
DETAIL_LABELS = (
    "공투",
    "증원",
    "대기",
    "공성전",
    "성역할",
    "편집",
    "해제",
    "보급거점",
    "해제",
    "방어거점",
    "해제",
    "편집",
)
MAIN_LABEL = "광역"
TAIL_RECORDS = (78, 79, 80, 81)


class WheelTransplantError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise WheelTransplantError(message)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def file_spec(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "size": path.stat().st_size,
        "sha256": base.sha256_file(path),
    }


def pin(path: Path, expected: Mapping[str, Any], label: str) -> dict[str, Any]:
    actual = file_spec(path)
    require(
        actual["size"] == expected["size"] and actual["sha256"] == expected["sha256"],
        f"{label} input pin differs: {actual}",
    )
    return actual


def parse_pk_layout(table_padding: bytes) -> list[tuple[int, int, int, int, int]]:
    require(len(table_padding) >= 32, "PK layout table is too short")
    layout = table_padding[24:]
    require(len(layout) % 12 == 8, f"PK layout byte count differs: {len(layout)}")
    records: list[tuple[int, int, int, int, int]] = []
    for index in range((len(layout) - 8) // 12):
        first, second, third = struct.unpack_from("<III", layout, index * 12)
        records.append(
            (first & 0xFFFF, first >> 16, second & 0xFFFF, second >> 16, third)
        )
    require(len(records) == 82, f"PK layout record count differs: {len(records)}")
    return records


def detail_group_records() -> list[list[int]]:
    result = [list(range(0, 6))]
    result.extend(list(range(start, start + 6)) for start in range(12, 78, 6))
    require(len(result) == 12, "PK detail group count differs")
    flattened = [record for group in result for record in group]
    require(
        flattened == list(range(0, 6)) + list(range(12, 78)),
        "PK detail record coverage differs",
    )
    return result


def active_records() -> list[int]:
    result = [record for group in detail_group_records() for record in group]
    result.extend(range(6, 12))
    result.sort()
    require(result == list(range(78)), "PK active record coverage differs")
    return result


def record_rect(record: Sequence[int]) -> tuple[int, int, int, int]:
    x, y, width, height, third = (int(value) for value in record)
    require(width > 0 and height > 0 and third == 0, f"invalid active record: {record}")
    return (x - 4, y - 4, x + width + 4, y + height + 4)


def clipped_rect(
    rect: Sequence[int], width: int, height: int
) -> tuple[int, int, int, int]:
    left, top, right, bottom = (int(value) for value in rect)
    clipped = (
        max(0, left),
        max(0, top),
        min(width, right),
        min(height, bottom),
    )
    require(
        clipped[0] < clipped[2] and clipped[1] < clipped[3],
        f"record cell is outside atlas: {tuple(rect)}",
    )
    return clipped


def validate_layout(
    records: Sequence[Sequence[int]], *, scale: int, route: str
) -> dict[str, Any]:
    require(len(records) == 82, f"{route} record count differs")
    expected_detail = (96, 88) if scale == 1 else (192, 176)
    for record_index in [record for group in detail_group_records() for record in group]:
        _, _, width, height, third = records[record_index]
        require(
            (width, height, third) == (*expected_detail, 0),
            f"{route} detail record {record_index} differs: {(width, height, third)}",
        )
    main_geometries = {
        (int(records[index][2]), int(records[index][3]), int(records[index][4]))
        for index in range(6, 12)
    }
    allowed_main = (
        {(96, 88, 0)}
        if scale == 1
        else {(192, 176, 0), (196, 180, 0)}
    )
    require(
        len(main_geometries) == 1 and main_geometries <= allowed_main,
        f"{route} main geometry differs: {sorted(main_geometries)}",
    )
    rects = {index: record_rect(records[index]) for index in active_records()}
    overlaps: list[tuple[int, int]] = []
    for first in range(78):
        for second in range(first + 1, 78):
            a, b = rects[first], rects[second]
            if (
                max(a[0], b[0]) < min(a[2], b[2])
                and max(a[1], b[1]) < min(a[3], b[3])
            ):
                overlaps.append((first, second))
    require(not overlaps, f"{route} active cells overlap: {overlaps[:8]}")
    return {
        "record_count": len(records),
        "active_record_count": 78,
        "detail_record_count": 72,
        "main_record_count": 6,
        "tail_records": list(TAIL_RECORDS),
        "detail_core": list(expected_detail),
        "main_core": list(next(iter(main_geometries))[:2]),
        "active_cells_non_overlapping": True,
    }


def extract_cell(
    atlas: Image.Image, rect: Sequence[int]
) -> Image.Image:
    left, top, right, bottom = (int(value) for value in rect)
    cell = Image.new("RGBA", (right - left, bottom - top), (0, 0, 0, 0))
    source = clipped_rect(rect, atlas.width, atlas.height)
    cell.paste(
        atlas.crop(source),
        (source[0] - left, source[1] - top),
    )
    return cell


def premultiplied_resize(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    rgba = image.convert("RGBA")
    raw = title_v1.resize_rgba_lanczos3_premultiplied(
        rgba.tobytes(), rgba.width, rgba.height, size[0], size[1]
    )
    return Image.frombytes("RGBA", size, raw)


def paste_cell_replace(
    atlas: Image.Image, rect: Sequence[int], cell: Image.Image
) -> None:
    left, top, right, bottom = (int(value) for value in rect)
    require(cell.size == (right - left, bottom - top), "paste cell geometry differs")
    target = clipped_rect(rect, atlas.width, atlas.height)
    source = (
        target[0] - left,
        target[1] - top,
        target[2] - left,
        target[3] - top,
    )
    atlas.paste(cell.crop(source), (target[0], target[1]))


def rect_blocks_clipped(
    rect: Sequence[int], width: int, height: int
) -> set[tuple[int, int]]:
    left, top, right, bottom = clipped_rect(rect, width, height)
    require(
        left % 4 == top % 4 == right % 4 == bottom % 4 == 0,
        f"record cell is not BC3 aligned after clipping: {(left, top, right, bottom)}",
    )
    return {
        (block_x, block_y)
        for block_y in range(top // 4, bottom // 4)
        for block_x in range(left // 4, right // 4)
    }


def changed_blocks(
    before: bytes, after: bytes, width: int, height: int
) -> list[tuple[int, int]]:
    require(len(before) == len(after) == width * height, "BC3 geometry differs")
    blocks_wide = width // 4
    return [
        (index % blocks_wide, index // blocks_wide)
        for index in range(len(before) // 16)
        if before[index * 16 : index * 16 + 16]
        != after[index * 16 : index * 16 + 16]
    ]


def verify_selected_encoding(
    requested: bytes,
    template: bytes,
    candidate: bytes,
    width: int,
    height: int,
    allowed: set[tuple[int, int]],
) -> dict[str, Any]:
    require(
        len(requested) == width * height * 4,
        "requested RGBA geometry differs",
    )
    require(
        len(template) == len(candidate) == width * height,
        "candidate BC3 geometry differs",
    )
    blocks_wide = width // 4
    expected_changed = 0
    retained_identical = 0
    for block_y in range(height // 4):
        for block_x in range(blocks_wide):
            index = block_y * blocks_wide + block_x
            start = index * 16
            before_block = template[start : start + 16]
            after_block = candidate[start : start + 16]
            if (block_x, block_y) not in allowed:
                require(
                    after_block == before_block,
                    f"unselected BC3 block changed: {(block_x, block_y)}",
                )
                continue
            desired_rgba = bc_codec.extract_rgba_block(
                requested, width, height, block_x, block_y
            )
            if bc_codec.decode_bc3_block(before_block) == desired_rgba:
                require(
                    after_block == before_block,
                    f"already-identical block was rewritten: {(block_x, block_y)}",
                )
                retained_identical += 1
            else:
                expected = bc_codec.encode_bc3_block(desired_rgba)
                require(
                    after_block == expected,
                    f"selected block was not source-derived: {(block_x, block_y)}",
                )
                expected_changed += int(after_block != before_block)
    actual_changed = changed_blocks(template, candidate, width, height)
    require(
        set(actual_changed) <= allowed,
        "encoded changes escaped active TC record cells",
    )
    require(expected_changed == len(actual_changed), "changed block count differs")
    return {
        "selected_blocks_source_derived": True,
        "unselected_blocks_byte_preserved": True,
        "allowed_bc3_blocks": len(allowed),
        "changed_bc3_blocks": len(actual_changed),
        "already_identical_blocks_retained": retained_identical,
        "changed_block_bbox": base.changed_block_bbox(actual_changed),
    }


def rgba_difference_metrics(
    reference: Image.Image, candidate: Image.Image
) -> dict[str, Any]:
    require(reference.size == candidate.size, "RGBA comparison geometry differs")
    left = np.asarray(reference, dtype=np.int16)
    right = np.asarray(candidate, dtype=np.int16)
    difference = np.abs(left - right)
    alpha_union = (left[:, :, 3] >= 8) | (right[:, :, 3] >= 8)
    selected = difference[alpha_union] if np.any(alpha_union) else difference.reshape(-1, 4)
    return {
        "mean_absolute_error_rgba": float(np.mean(selected)),
        "maximum_absolute_error_rgba": int(np.max(selected)),
        "alpha_union_pixels": int(np.count_nonzero(alpha_union)),
    }


def make_contact(
    before: Image.Image,
    after: Image.Image,
    records: Sequence[Sequence[int]],
    destination: Path,
) -> None:
    groups: list[tuple[str, list[int]]] = [
        ("MAIN  records 06-11", list(range(6, 12)))
    ]
    groups.extend(
        (f"DETAIL {group:02d}  records {indices[0]:02d}-{indices[-1]:02d}", indices)
        for group, indices in enumerate(detail_group_records())
    )
    cell_width = max(record_rect(records[index])[2] - record_rect(records[index])[0] for index in active_records())
    cell_height = max(record_rect(records[index])[3] - record_rect(records[index])[1] for index in active_records())
    strip_width = cell_width * 6
    label_height = 22
    gap = 12
    row_height = label_height + cell_height
    canvas = Image.new(
        "RGB",
        (strip_width * 2 + gap, row_height * len(groups) + 24),
        (24, 24, 24),
    )
    draw = ImageDraw.Draw(canvas)
    draw.text((4, 4), "BEFORE TC", fill=(255, 255, 255))
    draw.text((strip_width + gap + 4, 4), "AFTER JP-KOREAN TRANSPLANT", fill=(255, 255, 255))
    for row, (label, indices) in enumerate(groups):
        y = 24 + row * row_height
        draw.text((4, y + 4), label, fill=(255, 255, 255))
        draw.text((strip_width + gap + 4, y + 4), label, fill=(255, 255, 255))
        for column, index in enumerate(indices):
            rect = record_rect(records[index])
            before_cell = extract_cell(before, rect)
            after_cell = extract_cell(after, rect)
            x = column * cell_width + (cell_width - before_cell.width) // 2
            green_before = Image.new("RGBA", before_cell.size, (28, 92, 132, 255))
            green_before.alpha_composite(before_cell)
            canvas.paste(green_before.convert("RGB"), (x, y + label_height))
            x_after = strip_width + gap + column * cell_width + (cell_width - after_cell.width) // 2
            green_after = Image.new("RGBA", after_cell.size, (28, 92, 132, 255))
            green_after.alpha_composite(after_cell)
            canvas.paste(green_after.convert("RGB"), (x_after, y + label_height))
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination, optimize=False)


def make_supply_base_contact(
    before: Image.Image,
    after: Image.Image,
    records: Sequence[Sequence[int]],
    destination: Path,
) -> None:
    indices = detail_group_records()[7]
    cells_before = [extract_cell(before, record_rect(records[index])) for index in indices]
    cells_after = [extract_cell(after, record_rect(records[index])) for index in indices]
    cell_width = max(cell.width for cell in cells_before + cells_after)
    cell_height = max(cell.height for cell in cells_before + cells_after)
    canvas = Image.new("RGB", (cell_width * 6, cell_height * 2 + 44), (24, 24, 24))
    draw = ImageDraw.Draw(canvas)
    draw.text((4, 4), "GROUP 07 BEFORE TC", fill=(255, 255, 255))
    draw.text((4, cell_height + 26), "GROUP 07 AFTER KO", fill=(255, 255, 255))
    for row, cells in enumerate((cells_before, cells_after)):
        for column, cell in enumerate(cells):
            green = Image.new("RGBA", cell.size, (28, 92, 132, 255))
            green.alpha_composite(cell)
            canvas.paste(
                green.convert("RGB"),
                (
                    column * cell_width + (cell_width - cell.width) // 2,
                    22 + row * (cell_height + 22),
                ),
            )
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination, optimize=False)


def load_route(
    path: Path,
    *,
    outer_index: int,
    scale: int,
    route: str,
) -> dict[str, Any]:
    blob = path.read_bytes()
    outer = lz4.parse_link(blob)
    require(lz4.rebuild_link(outer) == blob, f"{route} outer LINK identity failed")
    nested = base.parse_nested_link(
        outer.entries[outer_index].data, expected_resource_id=81
    )
    slot, wrapper_header, raw, g1t = base.g1t_wrapper_entry(nested)
    require(len(g1t.textures) >= 1, f"{route} has no G1T texture")
    texture = g1t.textures[0]
    expected_size = (1024, 1024) if scale == 1 else (2048, 2048)
    require(
        (texture.width, texture.height, texture.format_code)
        == (*expected_size, 0x5B),
        f"{route} texture contract differs: {(texture.width, texture.height, texture.format_code)}",
    )
    decoded = atlas_codec.decode_texture(texture)
    require(decoded is not None, f"{route} texture decode failed")
    records = parse_pk_layout(nested.table_padding)
    layout = validate_layout(records, scale=scale, route=route)
    return {
        "path": path,
        "blob": blob,
        "outer": outer,
        "outer_index": outer_index,
        "nested": nested,
        "slot": slot,
        "wrapper_header": wrapper_header,
        "raw": raw,
        "g1t": g1t,
        "texture": texture,
        "atlas": Image.frombytes("RGBA", expected_size, decoded),
        "records": records,
        "layout": layout,
    }


def compose_route(
    source: Mapping[str, Any],
    target: Mapping[str, Any],
    *,
    scale: int,
    route: str,
) -> tuple[bytes, Image.Image, dict[str, Any]]:
    source_atlas: Image.Image = source["atlas"]
    target_atlas: Image.Image = target["atlas"]
    source_records = source["records"]
    target_records = target["records"]
    requested = target_atlas.copy()
    allowed: set[tuple[int, int]] = set()
    operations: list[dict[str, Any]] = []
    prepared_cells: dict[int, Image.Image] = {}

    for record_index in active_records():
        source_rect = record_rect(source_records[record_index])
        target_rect = record_rect(target_records[record_index])
        source_cell = extract_cell(source_atlas, source_rect)
        target_size = (
            target_rect[2] - target_rect[0],
            target_rect[3] - target_rect[1],
        )
        resized = source_cell.size != target_size
        if resized:
            source_cell = premultiplied_resize(source_cell, target_size)
        paste_cell_replace(requested, target_rect, source_cell)
        allowed.update(
            rect_blocks_clipped(
                target_rect, target_atlas.width, target_atlas.height
            )
        )
        prepared_cells[record_index] = source_cell
        family = "main" if 6 <= record_index <= 11 else "detail"
        group = (
            None
            if family == "main"
            else next(
                group
                for group, indices in enumerate(detail_group_records())
                if record_index in indices
            )
        )
        operations.append(
            {
                "record": record_index,
                "family": family,
                "group": group,
                "label": MAIN_LABEL if family == "main" else DETAIL_LABELS[int(group)],
                "source_rect": list(source_rect),
                "target_rect": list(target_rect),
                "source_cell_size": list(extract_cell(source_atlas, source_rect).size),
                "target_cell_size": list(target_size),
                "premultiplied_resize": resized,
            }
        )

    requested_bytes = requested.tobytes()
    target_texture = target["texture"]
    payload, encoded = base.encode_selected_blocks(
        requested_bytes,
        target_texture.width,
        target_texture.height,
        target_texture.payload,
        allowed,
    )
    encoding = verify_selected_encoding(
        requested_bytes,
        target_texture.payload,
        payload,
        target_texture.width,
        target_texture.height,
        allowed,
    )
    require(
        encoding["changed_bc3_blocks"] == encoded,
        f"{route} encoded block count differs",
    )
    candidate_texture = dataclasses.replace(target_texture, payload=payload)
    candidate_rgba = atlas_codec.decode_texture(candidate_texture)
    require(candidate_rgba is not None, f"{route} candidate decode failed")
    candidate_atlas = Image.frombytes(
        "RGBA", (target_texture.width, target_texture.height), candidate_rgba
    )

    record_metrics: list[dict[str, Any]] = []
    for operation in operations:
        record_index = int(operation["record"])
        candidate_cell = extract_cell(
            candidate_atlas, record_rect(target_records[record_index])
        )
        metrics = rgba_difference_metrics(prepared_cells[record_index], candidate_cell)
        record_metrics.append({"record": record_index, **metrics})

    return payload, candidate_atlas, {
        "route": route,
        "scale": scale,
        "method": "decoded_jp_korean_sprite_to_matching_tc_semantic_record",
        "active_records": active_records(),
        "active_record_count": 78,
        "detail_groups": len(DETAIL_LABELS),
        "detail_labels": list(DETAIL_LABELS),
        "main_label": MAIN_LABEL,
        "tail_records_not_sprite_labels": list(TAIL_RECORDS),
        "operations": operations,
        "record_metrics": record_metrics,
        "high_main_only_resize": scale == 2,
        "tc_layout_and_coordinates_preserved": True,
        "full_active_cell_replacement": True,
        "source_derived_block_verification": encoding,
    }


def rebuild_target(
    target: Mapping[str, Any],
    payload: bytes,
    destination: Path,
) -> dict[str, Any]:
    raw = target["raw"]
    g1t = target["g1t"]
    rebuilt_raw = base.replace_g1t_payloads(raw, g1t, {0: payload})
    require(len(rebuilt_raw) == len(raw), "target G1T raw size changed")
    for texture in g1t.textures[1:]:
        start = texture.payload_offset
        require(
            rebuilt_raw[start : start + len(texture.payload)] == texture.payload,
            f"unselected texture {texture.index} changed",
        )
    wrapper = lz4.recompress_wrapper_greedy(rebuilt_raw, target["wrapper_header"])
    _, roundtrip = lz4.decompress_wrapper(wrapper)
    require(roundtrip == rebuilt_raw, "target G1T wrapper roundtrip failed")
    nested = target["nested"]
    rebuilt_nested = base.rebuild_nested_link(nested, {target["slot"]: wrapper})
    reparsed_nested = base.parse_nested_link(
        rebuilt_nested, expected_resource_id=81
    )
    require(
        reparsed_nested.table_padding == nested.table_padding,
        "TC PK layout/table padding changed",
    )
    for entry in nested.entries:
        if entry.index == target["slot"]:
            continue
        require(
            reparsed_nested.entries[entry.index].data == entry.data
            and reparsed_nested.entries[entry.index].gap_after == entry.gap_after,
            f"unselected nested entry {entry.index} changed",
        )

    outer = target["outer"]
    before_hashes = base.outer_hashes(outer)
    candidate_blob = lz4.rebuild_link(
        outer, {target["outer_index"]: rebuilt_nested}
    )
    candidate_outer = lz4.parse_link(candidate_blob)
    require(
        lz4.rebuild_link(candidate_outer) == candidate_blob,
        "candidate outer LINK identity failed",
    )
    after_hashes = base.outer_hashes(candidate_outer)
    changed_outer = [
        index
        for index in range(len(candidate_outer.entries))
        if before_hashes[str(index)] != after_hashes[str(index)]
    ]
    require(
        changed_outer == [target["outer_index"]],
        f"changed outer scope differs: {changed_outer}",
    )
    for entry in outer.entries:
        if entry.index == target["outer_index"]:
            continue
        require(
            candidate_outer.entries[entry.index].data == entry.data
            and candidate_outer.entries[entry.index].gap_after == entry.gap_after,
            f"unselected outer entry {entry.index} changed",
        )
    base.atomic_write(destination, candidate_blob, forbidden=(target["path"],))
    return {
        "source": file_spec(target["path"]),
        "candidate": file_spec(destination),
        "changed_outer_entries": changed_outer,
        "resource_id": 81,
        "texture_index": 0,
        "layout_table_byte_preserved": True,
        "unselected_g1t_bytes_preserved": True,
        "unselected_nested_entries_byte_preserved": True,
        "unselected_outer_entries_byte_preserved": True,
        "outer_link_identity_verified": True,
        "wrapper_roundtrip_verified": True,
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    paths = {
        name: getattr(args, name).resolve(strict=True)
        for name in ("jp_low", "jp_high", "tc_low", "tc_high")
    }
    inputs = {
        name: pin(paths[name], PINS[name], name)
        for name in paths
    }
    output = base.fresh_output(args.output.resolve())

    routes: dict[str, Any] = {}
    candidates: dict[str, Any] = {}
    for scale_name, scale, outer_index in (
        ("low", 1, 1),
        ("high", 2, 3),
    ):
        print(f"stage={scale_name}_load", flush=True)
        jp = load_route(
            paths[f"jp_{scale_name}"],
            outer_index=outer_index,
            scale=scale,
            route=f"JP_{scale_name}",
        )
        tc = load_route(
            paths[f"tc_{scale_name}"],
            outer_index=outer_index,
            scale=scale,
            route=f"TC_{scale_name}",
        )
        require(
            jp["layout"]["active_record_count"]
            == tc["layout"]["active_record_count"]
            == 78,
            f"{scale_name} semantic record coverage differs",
        )
        print(f"stage={scale_name}_compose", flush=True)
        payload, candidate_atlas, composition = compose_route(
            jp, tc, scale=scale, route=f"TC_{scale_name}"
        )
        preview = output / "preview" / f"tc_pk_wheel_{scale_name}_before_after.png"
        supply_preview = (
            output / "preview" / f"tc_pk_wheel_{scale_name}_group07_supply_base.png"
        )
        make_contact(tc["atlas"], candidate_atlas, tc["records"], preview)
        make_supply_base_contact(
            tc["atlas"], candidate_atlas, tc["records"], supply_preview
        )
        composition["preview"] = file_spec(preview)
        composition["supply_base_preview"] = file_spec(supply_preview)
        destination = (
            output
            / "candidate"
            / ("RES_TC_PK" if scale == 1 else "RES_TC_PK_PORT")
            / ("res_lang_pk.bin" if scale == 1 else "res_lang_pk_port2.bin")
        )
        print(f"stage={scale_name}_rebuild", flush=True)
        candidate = rebuild_target(tc, payload, destination)
        routes[scale_name] = {
            "jp_layout": jp["layout"],
            "tc_layout": tc["layout"],
            "composition": composition,
        }
        candidates[scale_name] = candidate
        del jp, tc, payload, candidate_atlas
        gc.collect()

    report = {
        "schema": SCHEMA,
        "inputs": inputs,
        "scope": {
            "languages": ["TC"],
            "source_language_route": "JP with verified Korean wheel build",
            "resolutions": ["low 1024 atlas", "high 2048 atlas"],
            "active_records_per_route": 78,
            "detail_state_records_per_route": 72,
            "main_state_records_per_route": 6,
            "detail_labels": list(DETAIL_LABELS),
            "main_label": MAIN_LABEL,
            "inactive_tail_records_preserved": list(TAIL_RECORDS),
        },
        "routes": routes,
        "candidates": candidates,
        "qa": {
            "all_active_tc_cells_replaced_from_jp_korean": True,
            "tc_text_pixels_cannot_survive_inside_active_cells": True,
            "jp_or_tc_archive_wholesale_copy_used": False,
            "tc_layout_metadata_preserved": True,
            "real_game_runtime_qa_pending": True,
            "required_runtime_resolution": "1920x1080",
            "full_process_restart_required": True,
        },
        "steam_files_written": False,
    }
    report_path = output / "build_report.json"
    base.write_json(
        report_path,
        report,
        forbidden=tuple(paths.values()),
    )
    return {
        "report": str(report_path),
        "candidates": {
            name: item["candidate"] for name, item in candidates.items()
        },
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--jp-low", type=Path, required=True)
    result.add_argument("--jp-high", type=Path, required=True)
    result.add_argument("--tc-low", type=Path, required=True)
    result.add_argument("--tc-high", type=Path, required=True)
    result.add_argument("--output", type=Path, required=True)
    return result


def main() -> None:
    print(json.dumps(build(parser().parse_args()), ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
