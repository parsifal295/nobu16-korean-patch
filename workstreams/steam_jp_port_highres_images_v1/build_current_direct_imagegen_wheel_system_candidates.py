#!/usr/bin/env python3
"""Build current-baseline wheel/PK/system-button candidates from direct ImageGen assets.

The builder never redraws glyphs and never clips generated artwork to a
Japanese/native foreground mask.  Native masks are used only to clear the old
sprite and to bound the set of BC3 blocks that may change.  The complete
generated foreground is then placed at the original metadata/component center.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import numpy as np
from PIL import Image


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parent.parent
TOOLS = REPO / "tools"
TITLE_WORKSTREAM = REPO / "workstreams" / "steam_jp_title_images_v1"
for candidate in (WORKSTREAM, TOOLS, TITLE_WORKSTREAM):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import extract_nobu16_image_atlases as atlas_codec  # noqa: E402
import nobu16_lz4 as lz4  # noqa: E402
import build_steam_jp_title_images_v1 as title_v1  # noqa: E402
import build_steam_jp_port_highres_images_v1 as base  # noqa: E402
from build_full_runtime_wheel_imagegen_candidates import (  # noqa: E402
    centered_main_mask,
    detail_group_records,
    parse_layout,
)


SCHEMA = "nobu16.kr.current-direct-imagegen-wheel-system-candidates.v1"
PINS = {
    "base_low": {"size": 160_721_213, "sha256": "2AD3B5612D88B0654BED1F3ED9CE5FEF214DABFE8FA312C7A2EBE16A27F7B17A"},
    "base_high": {"size": 81_535_039, "sha256": "8D9E8F7A8E5F0C5F1FA59909C53E9D5BAA9C963D08A2622DDBA60F86D89307D5"},
    "pk_low": {"size": 141_746_742, "sha256": "EC758BC9B87F98B42E01CA6F841D963811BB944D113E2C65A1E9F5AE19F1DF08"},
    "pk_high": {"size": 67_086_423, "sha256": "F18D99C4802AAB78C60C372FF0106ABD61ABDD8C026DC53CAE8FDE47C992C205"},
    "port3": {"size": 43_484_341, "sha256": "51B7ED1FA81CD785591D52601035ED970C2B7D83A2DBC1D73C0B6C14E3F0D75B"},
}


class CandidateError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CandidateError(message)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def file_spec(path: Path) -> dict[str, Any]:
    return {"path": str(path), "size": path.stat().st_size, "sha256": base.sha256_file(path)}


def pin(path: Path, expected: Mapping[str, Any], label: str) -> dict[str, Any]:
    actual = file_spec(path)
    require(actual["size"] == expected["size"] and actual["sha256"] == expected["sha256"], f"{label} pin differs: {actual}")
    return actual


def premultiplied_resize(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    rgba = image.convert("RGBA")
    raw = title_v1.resize_rgba_lanczos3_premultiplied(rgba.tobytes(), rgba.width, rgba.height, size[0], size[1])
    return Image.frombytes("RGBA", size, raw)


def alpha_blocks(alpha: Image.Image, x0: int, y0: int, atlas_width: int) -> set[tuple[int, int]]:
    array = np.asarray(alpha, dtype=np.uint8)
    ys, xs = np.nonzero(array >= 8)
    if not len(xs):
        return set()
    blocks_wide = atlas_width // 4
    ids = np.unique(((ys + y0) // 4).astype(np.int64) * blocks_wide + ((xs + x0) // 4))
    return {(int(value % blocks_wide), int(value // blocks_wide)) for value in ids.tolist()}


def changed_blocks(before: bytes, after: bytes, width: int, height: int) -> list[tuple[int, int]]:
    require(len(before) == len(after) == width * height, "BC3 payload geometry differs")
    blocks_wide = width // 4
    return [
        (index % blocks_wide, index // blocks_wide)
        for index in range(len(before) // 16)
        if before[index * 16 : index * 16 + 16] != after[index * 16 : index * 16 + 16]
    ]


def place_in_canvas(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    require(image.width <= size[0] and image.height <= size[1], f"generated sprite exceeds placement canvas: {image.size} > {size}")
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    canvas.alpha_composite(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def normalize_complete_to_canvas(image: Image.Image, size: tuple[int, int], margin: int = 2) -> Image.Image:
    bbox = image.getchannel("A").getbbox()
    require(bbox is not None, "cannot normalize an empty generated sprite")
    sprite = image.crop(bbox)
    scale = min(1.0, (size[0] - margin * 2) / sprite.width, (size[1] - margin * 2) / sprite.height)
    resized = premultiplied_resize(sprite, (max(1, int(round(sprite.width * scale))), max(1, int(round(sprite.height * scale)))))
    return place_in_canvas(resized, size)


def fit_complete_sprite_to_native_geometry(
    cell: Image.Image,
    native_mask: Image.Image,
    prior_occupancy: np.ndarray,
) -> tuple[Image.Image, dict[str, Any]]:
    """Uniformly fit a complete generated sprite without mask clipping.

    Packed logical cells overlap in this atlas.  The native foreground bounds
    therefore provide the safe geometric envelope.  If the generated silhouette
    still touches an already placed neighbour, the complete sprite is uniformly
    reduced in deterministic 2% steps around the same native center.
    """

    generated_bbox = cell.getchannel("A").getbbox()
    native_bbox = native_mask.getbbox()
    require(generated_bbox is not None and native_bbox is not None, "cannot fit an empty sprite")
    sprite = cell.crop(generated_bbox)
    native_w, native_h = native_bbox[2] - native_bbox[0], native_bbox[3] - native_bbox[1]
    scale = min(1.0, max(1, native_w - 2) / sprite.width, max(1, native_h - 2) / sprite.height)
    native_cx = (native_bbox[0] + native_bbox[2]) / 2.0
    native_cy = (native_bbox[1] + native_bbox[3]) / 2.0
    for attempt in range(41):
        width = max(1, int(round(sprite.width * scale)))
        height = max(1, int(round(sprite.height * scale)))
        resized = premultiplied_resize(sprite, (width, height))
        x = int(round(native_cx - width / 2.0))
        y = int(round(native_cy - height / 2.0))
        x = min(max(0, x), cell.width - width)
        y = min(max(0, y), cell.height - height)
        canvas = Image.new("RGBA", cell.size, (0, 0, 0, 0))
        canvas.alpha_composite(resized, (x, y))
        active = np.asarray(canvas.getchannel("A"), dtype=np.uint8) >= 8
        collision_pixels = int(np.count_nonzero(prior_occupancy & active))
        if collision_pixels == 0:
            return canvas, {
                "generated_input_bbox": list(generated_bbox),
                "native_geometry_bbox": list(native_bbox),
                "geometric_scale": scale,
                "geometric_placement": [x, y],
                "geometric_size": [width, height],
                "collision_shrink_attempts": attempt,
                "collision_pixels": 0,
                "complete_sprite_preserved": True,
                "native_mask_clipping": False,
            }
        scale *= 0.98
    raise CandidateError(f"complete generated sprite cannot fit native packed geometry: native={native_bbox} generated={generated_bbox}")


def compose_operations(
    texture: atlas_codec.Texture,
    operations: list[dict[str, Any]],
    *,
    method: str,
) -> tuple[bytes, Image.Image, dict[str, Any]]:
    require(texture.format_code == 0x5B, "target texture is not BC3")
    decoded = atlas_codec.decode_texture(texture)
    require(decoded is not None, "target texture cannot decode")
    atlas = Image.frombytes("RGBA", (texture.width, texture.height), decoded)
    before = atlas.copy()
    allowed: set[tuple[int, int]] = set()
    occupancy = np.zeros((texture.height, texture.width), dtype=np.bool_)
    operation_report: list[dict[str, Any]] = []

    for operation in operations:
        rect = tuple(int(value) for value in operation["rect"])
        x0, y0, x1, y1 = rect
        cell = operation["cell"].convert("RGBA")
        require(cell.size == (x1 - x0, y1 - y0), f"cell geometry differs at {rect}: {cell.size}")
        if x0 < 0 or y0 < 0 or x1 > texture.width or y1 > texture.height:
            crop = (max(0, -x0), max(0, -y0), cell.width - max(0, x1 - texture.width), cell.height - max(0, y1 - texture.height))
            discarded = np.asarray(cell.getchannel("A"), dtype=np.uint8) >= 8
            kept = np.zeros_like(discarded)
            kept[crop[1] : crop[3], crop[0] : crop[2]] = True
            require(not np.any(discarded & ~kept), f"generated foreground would be clipped by atlas boundary: {rect}")
            cell = cell.crop(crop)
            x0, y0, x1, y1 = max(0, x0), max(0, y0), min(texture.width, x1), min(texture.height, y1)
            rect = (x0, y0, x1, y1)
            operation["rect"] = list(rect)
            operation["transparent_boundary_crop"] = list(crop)
        require(0 <= x0 < x1 <= texture.width and 0 <= y0 < y1 <= texture.height, f"operation escapes atlas: {rect}")
        native = before.crop(rect)
        native_mask, mask_stats = centered_main_mask(native, 1)
        require(native_mask.getbbox() is not None, f"native sprite is empty at {rect}")
        prior = occupancy[y0:y1, x0:x1]
        cell, geometry_stats = fit_complete_sprite_to_native_geometry(cell, native_mask, prior)
        new_alpha = cell.getchannel("A")
        new_active = np.asarray(new_alpha, dtype=np.uint8) >= 8
        collision_pixels = int(np.count_nonzero(prior & new_active))
        require(collision_pixels == 0, f"generated foreground collision at {rect}: {collision_pixels} pixels; operation={operation.get('family')}:{operation.get('group')}:{operation.get('state')}")
        prior |= new_active
        allowed.update(alpha_blocks(native_mask, x0, y0, texture.width))
        allowed.update(alpha_blocks(new_alpha, x0, y0, texture.width))
        operation["native_mask"] = native_mask
        operation["cell"] = cell
        operation_report.append({
            **{key: value for key, value in operation.items() if key not in {"cell", "native_mask"}},
            **mask_stats,
            "generated_bbox": list(new_alpha.getbbox()),
            **geometry_stats,
        })

    # All old components are cleared before any new foreground is placed.  This
    # prevents a later overlapping logical cell from erasing an earlier result.
    for operation in operations:
        rect = tuple(operation["rect"])
        atlas.paste((0, 0, 0, 0), rect, operation["native_mask"])
    for operation in operations:
        rect = tuple(operation["rect"])
        atlas.alpha_composite(operation["cell"], (rect[0], rect[1]))

    requested = atlas.tobytes()
    payload, encoded = base.encode_selected_blocks(requested, texture.width, texture.height, texture.payload, allowed)
    actual = changed_blocks(texture.payload, payload, texture.width, texture.height)
    require(actual and set(actual) <= allowed, "encoded changes escaped the old/new foreground block union")
    return payload, atlas, {
        "method": method,
        "dimensions": [texture.width, texture.height],
        "operations": operation_report,
        "operation_count": len(operation_report),
        "allowed_bc3_blocks": len(allowed),
        "encoded_bc3_blocks": encoded,
        "changed_bc3_blocks": len(actual),
        "changed_block_bbox": base.changed_block_bbox(actual),
        "native_mask_used_only_for_clearing": True,
        "generated_foreground_not_clipped": True,
        "generated_foreground_collision_pixels": 0,
        "unselected_bc3_blocks_byte_preserved": True,
    }


def base_wheel_operations(
    table_padding: bytes,
    mapping: dict[str, Any],
    detail_prepared: Path,
    main_prepared: Path,
    *,
    scale: int,
) -> list[dict[str, Any]]:
    records = parse_layout(table_padding)
    detail_cell = (200, 190) if scale == 2 else (100, 95)
    detail_core = (192, 176) if scale == 2 else (96, 88)
    detail_padding = (4, 12) if scale == 2 else (2, 6)
    main_core = 208 if scale == 2 else 104
    by_group: dict[int, dict[str, Any]] = {}
    for item in mapping["groups"]:
        for group in item["targets"]:
            require(int(group) not in by_group, f"base detail group mapped twice: {group}")
            by_group[int(group)] = item
    require(set(by_group) == set(range(57)), "base detail group coverage differs")

    detail_strips: dict[str, Image.Image] = {}
    for item in mapping["groups"]:
        name = item["name"]
        high = Image.open(detail_prepared / f"{name}_physical_alpha.png").convert("RGBA")
        require(high.size == (1200, 190), f"base detail prepared geometry differs: {name} {high.size}")
        detail_strips[name] = high if scale == 2 else premultiplied_resize(high, (600, 95))

    operations: list[dict[str, Any]] = []
    for group, record_indices in enumerate(detail_group_records()):
        item = by_group[group]
        strip = detail_strips[item["name"]]
        for state, record_index in enumerate(record_indices):
            x, y, width, height, third = records[record_index]
            require((width, height, third) == (*detail_core, 0), f"base detail record {record_index} differs")
            rect = (x - detail_padding[0], y - detail_padding[1], x - detail_padding[0] + detail_cell[0], y - detail_padding[1] + detail_cell[1])
            cell = strip.crop((state * detail_cell[0], 0, (state + 1) * detail_cell[0], detail_cell[1]))
            operations.append({"family": "base_detail", "group": group, "name": item["name"], "ko": item["ko"], "state": state + 1, "record": record_index, "rect": list(rect), "cell": cell})

    main_names = ("assessment", "appointment", "military", "domestic", "diplomacy")
    for group, name in enumerate(main_names):
        high = Image.open(main_prepared / f"main_{group}_{name}_alpha.png").convert("RGBA")
        require(high.size == (1248, 208), f"base main prepared geometry differs: {name} {high.size}")
        strip = high if scale == 2 else premultiplied_resize(high, (624, 104))
        for state in range(6):
            record_index = 252 + group * 6 + state
            x, y, width, height, third = records[record_index]
            require((width, height, third) == (main_core, main_core, 0), f"base main record {record_index} differs")
            rect = (x, y, x + main_core, y + main_core)
            cell = strip.crop((state * main_core, 0, (state + 1) * main_core, main_core))
            operations.append({"family": "base_main", "group": group, "name": name, "state": state + 1, "record": record_index, "rect": list(rect), "cell": cell})
    return operations


def parse_pk_layout(table_padding: bytes) -> list[tuple[int, int, int, int, int]]:
    require(len(table_padding) >= 32, "PK layout table is too short")
    layout = table_padding[24:]
    require(len(layout) % 12 == 8, "PK layout byte count differs")
    records = []
    for index in range((len(layout) - 8) // 12):
        first = int.from_bytes(layout[index * 12 : index * 12 + 4], "little")
        second = int.from_bytes(layout[index * 12 + 4 : index * 12 + 8], "little")
        third = int.from_bytes(layout[index * 12 + 8 : index * 12 + 12], "little")
        records.append((first & 0xFFFF, first >> 16, second & 0xFFFF, second >> 16, third))
    require(len(records) == 82, f"PK layout record count differs: {len(records)}")
    return records


def pk_wheel_operations(table_padding: bytes, prepared: Path, *, scale: int) -> list[dict[str, Any]]:
    records = parse_pk_layout(table_padding)
    group_indices = [list(range(0, 6))] + [list(range(index, index + 6)) for index in range(12, 78, 6)]
    require(len(group_indices) == 12, "PK detail group count differs")
    operations: list[dict[str, Any]] = []
    if scale == 2:
        detail_cell_size = (200, 190)
        detail_core = (192, 176)
        detail_padding = (4, 12)
        placement_size = detail_cell_size
    else:
        detail_cell_size = (100, 95)
        detail_core = (96, 88)
        detail_padding = (4, 4)
        placement_size = (104, 96)

    for group, indices in enumerate(group_indices):
        high = Image.open(prepared / f"pk_detail_{group:02d}_alpha.png").convert("RGBA")
        require(high.size == (1200, 190), f"PK detail prepared geometry differs: {group}")
        strip = high if scale == 2 else premultiplied_resize(high, (600, 95))
        for state, record_index in enumerate(indices):
            x, y, width, height, third = records[record_index]
            require((width, height, third) == (*detail_core, 0), f"PK detail record {record_index} differs")
            if scale == 2:
                rect = (x - 4, y - 4, x + 196, y + 180)
                source_cell = strip.crop((state * 200, 0, (state + 1) * 200, 190))
                cell = normalize_complete_to_canvas(source_cell, (200, 184))
            else:
                rect = (x - 4, y - 4, x + 100, y + 92)
                source_cell = strip.crop((state * 100, 0, (state + 1) * 100, 95))
                cell = place_in_canvas(source_cell, placement_size)
            operations.append({"family": "pk_detail", "group": group, "state": state + 1, "record": record_index, "rect": list(rect), "cell": cell})

    high_main = Image.open(prepared / "pk_main_00_alpha.png").convert("RGBA")
    require(high_main.size == (1224, 188), f"PK main prepared geometry differs: {high_main.size}")
    if scale == 2:
        main_strip = high_main
        main_cell_size = (204, 188)
    else:
        main_strip = premultiplied_resize(high_main, (612, 94))
        main_cell_size = (102, 94)
    for state, record_index in enumerate(range(6, 12)):
        x, y, width, height, third = records[record_index]
        if scale == 2:
            require((width, height, third) == (196, 180, 0), f"PK main record {record_index} differs")
            rect = (x - 4, y - 4, x + 200, y + 184)
            cell = main_strip.crop((state * 204, 0, (state + 1) * 204, 188))
        else:
            require((width, height, third) == (96, 88, 0), f"PK low main record {record_index} differs")
            rect = (x - 4, y - 4, x + 100, y + 92)
            source_cell = main_strip.crop((state * 102, 0, (state + 1) * 102, 94))
            cell = place_in_canvas(source_cell, (104, 96))
        operations.append({"family": "pk_main", "group": 0, "name": "wide_area", "ko": "광역", "state": state + 1, "record": record_index, "rect": list(rect), "cell": cell})
    return operations


def centered_rect(artwork_box: Sequence[int], cell_size: tuple[int, int]) -> list[int]:
    cx = (int(artwork_box[0]) + int(artwork_box[2])) / 2.0
    cy = (int(artwork_box[1]) + int(artwork_box[3])) / 2.0
    x0 = int(round(cx - cell_size[0] / 2.0))
    y0 = int(round(cy - cell_size[1] / 2.0))
    return [x0, y0, x0 + cell_size[0], y0 + cell_size[1]]


def low_system_button_operations(prepared: Path) -> list[dict[str, Any]]:
    manifest = json.loads((prepared / "manifest.json").read_text(encoding="utf-8"))
    require(manifest.get("schema") == "nobu16.kr.system-buttons-low-imagegen-direct-prepared.v1", "low system prepared schema differs")
    operations: list[dict[str, Any]] = []
    for name, item in manifest["targets"].items():
        for state_item in item["states"]:
            state = int(state_item["state"])
            cell = Image.open(state_item["alpha"]["path"]).convert("RGBA")
            require(cell.size == (192, 88), f"low system cell geometry differs: {name}:{state}")
            operations.append({
                "family": "system_button_low", "name": name, "ko": item["ko"], "state": state,
                "component_index": state_item["component_index"],
                "rect": centered_rect(state_item["artwork_box"], cell.size), "cell": cell,
            })
    battle = manifest["battle_start"]
    for state_item in battle["states"]:
        state = int(state_item["state"])
        cell = Image.open(state_item["alpha"]["path"]).convert("RGBA")
        require(cell.size == (264, 88), f"battle-start cell geometry differs: {state}")
        operations.append({
            "family": "system_button_low_battle_start", "name": "battle_start", "ko": battle["ko"], "state": state,
            "rect": centered_rect(state_item["artwork_box"], cell.size), "cell": cell,
        })
    require(len(operations) == 127, "low system button state count differs")
    return operations


def high_system_button_operations(prepared: Path) -> list[dict[str, Any]]:
    manifest = json.loads((prepared / "manifest.json").read_text(encoding="utf-8"))
    require(manifest.get("schema") == "nobu16.kr.system-buttons-high-imagegen-direct-prepared.v1", "high system prepared schema differs")
    operations: list[dict[str, Any]] = []
    for name, item in manifest["targets"].items():
        for state_item in item["states"]:
            state = int(state_item["state"])
            cell = Image.open(state_item["alpha"]["path"]).convert("RGBA")
            require(cell.size == (376, 168), f"high system cell geometry differs: {name}:{state}")
            operations.append({
                "family": "system_button_high", "name": name, "ko": item["ko"], "state": state,
                "rect": centered_rect(state_item["artwork_box"], cell.size), "cell": cell,
            })
    require(len(operations) == 120, "high system button state count differs")
    return operations


def rebuild_nested_texture(
    nested_blob: bytes,
    *,
    resource_id: int,
    texture_index: int,
    operation_builder: Callable[[bytes], list[dict[str, Any]]],
    method: str,
    preview: Path,
) -> tuple[bytes, dict[str, Any]]:
    nested = base.parse_nested_link(nested_blob, expected_resource_id=resource_id)
    slot, header, raw, g1t = base.g1t_wrapper_entry(nested)
    require(texture_index < len(g1t.textures), f"texture {texture_index} is absent")
    texture = g1t.textures[texture_index]
    operations = operation_builder(nested.table_padding)
    payload, composed, composition = compose_operations(texture, operations, method=method)
    rebuilt_raw = base.replace_g1t_payloads(raw, g1t, {texture_index: payload})
    require(len(rebuilt_raw) == len(raw), "G1T raw size changed")
    wrapper = lz4.recompress_wrapper_greedy(rebuilt_raw, header)
    _, roundtrip = lz4.decompress_wrapper(wrapper)
    require(roundtrip == rebuilt_raw, "G1T wrapper roundtrip failed")
    rebuilt_nested = base.rebuild_nested_link(nested, {slot: wrapper})
    reparsed = base.parse_nested_link(rebuilt_nested, expected_resource_id=resource_id)
    require(reparsed.table_padding == nested.table_padding, "layout/table padding changed")
    for entry in nested.entries:
        if entry.index != slot:
            require(reparsed.entries[entry.index].data == entry.data and reparsed.entries[entry.index].gap_after == entry.gap_after, f"nested entry {entry.index} changed")
    preview.parent.mkdir(parents=True, exist_ok=True)
    composed.save(preview, optimize=False)
    result = {
        "resource_id": resource_id,
        "nested_slot": slot,
        "texture_index": texture_index,
        "preview": file_spec(preview),
        "composition": composition,
        "layout_table_byte_preserved": True,
        "unselected_nested_entries_byte_preserved": True,
        "unselected_g1t_bytes_preserved": True,
    }
    del raw, rebuilt_raw, composed
    gc.collect()
    return rebuilt_nested, result


def rebuild_archive(source: Path, destination: Path, replacements: dict[int, bytes], expected_changed: Sequence[int]) -> dict[str, Any]:
    blob = source.read_bytes()
    outer = lz4.parse_link(blob)
    require(lz4.rebuild_link(outer) == blob, "source outer LINK identity failed")
    before = base.outer_hashes(outer)
    candidate_blob = lz4.rebuild_link(outer, replacements)
    candidate = lz4.parse_link(candidate_blob)
    require(lz4.rebuild_link(candidate) == candidate_blob, "candidate outer LINK identity failed")
    after = base.outer_hashes(candidate)
    changed = [index for index in range(len(candidate.entries)) if before[str(index)] != after[str(index)]]
    require(changed == list(expected_changed), f"changed outer scope differs: {changed}")
    for index in range(len(candidate.entries)):
        if index not in expected_changed:
            require(candidate.entries[index].data == outer.entries[index].data and candidate.entries[index].gap_after == outer.entries[index].gap_after, f"outer entry {index} changed")
    base.atomic_write(destination, candidate_blob, forbidden=(source,))
    return {
        "source": file_spec(source),
        "candidate": file_spec(destination),
        "changed_outer_entries": changed,
        "unrelated_outer_entries_byte_preserved": True,
        "outer_link_identity_verified": True,
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    paths = {name: getattr(args, name).resolve(strict=True) for name in ("base_low", "base_high", "pk_low", "pk_high", "port3")}
    detail_prepared = args.detail_prepared.resolve(strict=True)
    main_prepared = args.main_prepared.resolve(strict=True)
    pk_prepared = args.pk_prepared.resolve(strict=True)
    low_system_prepared = args.low_system_prepared.resolve(strict=True)
    high_system_prepared = args.high_system_prepared.resolve(strict=True)
    mapping_path = args.mapping.resolve(strict=True)
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    require(mapping.get("schema") == "nobu16.kr.wheel-detail-groups.v1" and len(mapping.get("groups", [])) == 46, "base wheel mapping differs")
    output = base.fresh_output(args.output.resolve())
    inputs = {name: pin(paths[name], PINS[name], name) for name in paths}
    inputs.update({
        "detail_prepared_manifest": file_spec(detail_prepared / "manifest.json"),
        "main_prepared_manifest": file_spec(main_prepared / "manifest.json"),
        "pk_prepared_manifest": file_spec(pk_prepared / "manifest.json"),
        "low_system_prepared_manifest": file_spec(low_system_prepared / "manifest.json"),
        "high_system_prepared_manifest": file_spec(high_system_prepared / "manifest.json"),
        "mapping": file_spec(mapping_path),
    })

    low_outer = lz4.parse_link(paths["base_low"].read_bytes())
    high_outer = lz4.parse_link(paths["base_high"].read_bytes())
    pk_low_outer = lz4.parse_link(paths["pk_low"].read_bytes())
    pk_high_outer = lz4.parse_link(paths["pk_high"].read_bytes())

    print("stage=base_low_wheel", flush=True)
    low_wheel_nested, low_wheel = rebuild_nested_texture(
        low_outer.entries[8].data, resource_id=474, texture_index=0,
        operation_builder=lambda table: base_wheel_operations(table, mapping, detail_prepared, main_prepared, scale=1),
        method="direct_imagegen_complete_base_detail_and_main_low", preview=output / "preview" / "base_wheel_low.png")
    print("stage=system_buttons_low", flush=True)
    low_system_nested, low_system = rebuild_nested_texture(
        low_outer.entries[5].data, resource_id=3856, texture_index=1,
        operation_builder=lambda _table: low_system_button_operations(low_system_prepared),
        method="direct_imagegen_complete_system_buttons_low_20x6_plus_battle_7", preview=output / "preview" / "system_buttons_low.png")
    print("stage=system_buttons_high", flush=True)
    high_system_nested, high_system = rebuild_nested_texture(
        high_outer.entries[2].data, resource_id=3860, texture_index=1,
        operation_builder=lambda _table: high_system_button_operations(high_system_prepared),
        method="direct_imagegen_complete_system_buttons_high_20x6", preview=output / "preview" / "system_buttons_high.png")
    print("stage=base_high_wheel", flush=True)
    high_wheel_nested, high_wheel = rebuild_nested_texture(
        high_outer.entries[3].data, resource_id=474, texture_index=0,
        operation_builder=lambda table: base_wheel_operations(table, mapping, detail_prepared, main_prepared, scale=2),
        method="direct_imagegen_complete_base_detail_and_main_high", preview=output / "preview" / "base_wheel_high.png")
    print("stage=pk_low_wheel", flush=True)
    pk_low_nested, pk_low_wheel = rebuild_nested_texture(
        pk_low_outer.entries[1].data, resource_id=81, texture_index=0,
        operation_builder=lambda table: pk_wheel_operations(table, pk_prepared, scale=1),
        method="direct_imagegen_complete_pk_detail_and_wide_area_low", preview=output / "preview" / "pk_wheel_low.png")
    print("stage=pk_high_wheel", flush=True)
    pk_high_nested, pk_high_wheel = rebuild_nested_texture(
        pk_high_outer.entries[3].data, resource_id=81, texture_index=0,
        operation_builder=lambda table: pk_wheel_operations(table, pk_prepared, scale=2),
        method="direct_imagegen_complete_pk_detail_and_wide_area_high", preview=output / "preview" / "pk_wheel_high.png")

    candidates = {
        "base_low": rebuild_archive(paths["base_low"], output / "candidate" / "RES_JP" / "res_lang.bin", {5: low_system_nested, 8: low_wheel_nested}, [5, 8]),
        "base_high": rebuild_archive(paths["base_high"], output / "candidate" / "RES_JP_PK_PORT" / "res_lang_pk_port1.bin", {2: high_system_nested, 3: high_wheel_nested}, [2, 3]),
        "pk_low": rebuild_archive(paths["pk_low"], output / "candidate" / "RES_JP_PK" / "res_lang_pk.bin", {1: pk_low_nested}, [1]),
        "pk_high": rebuild_archive(paths["pk_high"], output / "candidate" / "RES_JP_PK_PORT" / "res_lang_pk_port2.bin", {3: pk_high_nested}, [3]),
    }
    report = {
        "schema": SCHEMA,
        "inputs": inputs,
        "asset_coverage": {"base_detail_unique": 46, "base_detail_groups": 57, "base_main_groups": 5, "pk_detail_groups": 12, "pk_main_groups": 1, "system_buttons_standard_labels": 20, "system_buttons_low_states": 127, "system_buttons_high_states": 120},
        "routes": {"base_low_wheel": low_wheel, "system_buttons_low": low_system, "system_buttons_high": high_system, "base_high_wheel": high_wheel, "pk_low_wheel": pk_low_wheel, "pk_high_wheel": pk_high_wheel},
        "candidates": candidates,
        "port3": {"input": inputs["port3"], "changed": False, "candidate_not_needed": True},
        "live_files_written": False,
    }
    report_path = output / "build_report.json"
    base.write_json(report_path, report, forbidden=tuple(paths.values()))
    return {"report": str(report_path), "candidates": {key: value["candidate"] for key, value in candidates.items()}}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    for name in ("base_low", "base_high", "pk_low", "pk_high", "port3"):
        result.add_argument(f"--{name.replace('_', '-')}", dest=name, type=Path, required=True)
    result.add_argument("--detail-prepared", type=Path, required=True)
    result.add_argument("--main-prepared", type=Path, required=True)
    result.add_argument("--pk-prepared", type=Path, required=True)
    result.add_argument("--low-system-prepared", type=Path, required=True)
    result.add_argument("--high-system-prepared", type=Path, required=True)
    result.add_argument("--mapping", type=Path, required=True)
    result.add_argument("--output", type=Path, required=True)
    return result


def main() -> None:
    print(json.dumps(build(parser().parse_args()), ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
