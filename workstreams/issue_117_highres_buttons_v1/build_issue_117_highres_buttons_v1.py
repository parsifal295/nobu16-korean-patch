#!/usr/bin/env python3
"""Build the issue-117 and high-resolution battle-start image fixes.

Only two native PC atlas routes are changed:

* ``RES_JP_PK_PORT/res_lang_pk_port2.bin`` /2/0 texture 1 (BC7):
  six ``全承認`` buttons become ``전체 승인``; and
* ``RES_JP_PK_PORT/res_lang_pk_port1.bin`` /2/0 texture 2 (BC3):
  seven high-resolution ``開戦`` buttons receive the reviewed Korean
  ``개전`` artwork.

All unrelated outer entries, nested slots, G1T textures and compression
blocks are required to remain byte-identical.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import struct
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parent.parent
TOOLS = REPO / "tools"
HIGHRES_WORKSTREAM = REPO / "workstreams" / "steam_jp_port_highres_images_v1"
for candidate in (TOOLS, HIGHRES_WORKSTREAM):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import extract_nobu16_image_atlases as atlas_codec  # noqa: E402
import nobu16_lz4 as lz4  # noqa: E402
import build_steam_jp_port_highres_images_v1 as highres  # noqa: E402

try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover - bundled runtime invariant.
    raise RuntimeError("the bundled Pillow and NumPy runtime is required") from exc


SCHEMA = "nobu16.kr.issue-117-highres-buttons.v1"
PORT1_PIN = {
    "size": 82_947_959,
    "sha256": "00E6320DD69A22048F632840B4D95F95F9EACA947A218255AD7FDB308174DE4D",
}
PORT2_PIN = {
    "size": 67_927_579,
    "sha256": "34E77AF4B1BB496DBC5F3BE2AB4CD82DC9E429EE3B8AE683869E0B96251CD983",
}
FONT_PIN = "60D6A471E9A14F4BA563612D2577B9B6CCB2D1C599A69191B3F9F82EF80A19D1"
BATTLE_SOURCE_PINS = (
    "A634529FCBC6DD79A56AE13C7316D7567F02CA672D8B19E49D2366300202F0CC",
    "B647FF89F8D56FCB7DD60A70DE702828481782D563EFF65547EFD15A1BC61023",
    "B2FD463518F021AAB3066FF9AF43172BBBE0A8121A1664CB1CEEC895FF246FA5",
    "853BCEA430C74467AA30FEE9980D3D35AE92B67D6F7115E9FA26C696876355B9",
    "8F8E5AE57EABDD540645CD1445B5FC8B289E6B3B3F11183E2E50AFB8B56FC1AC",
    "D12660C0D895E1D540E5ED9631A1C6A3C43B8EF021CADEC90273547EAAADE640",
    "B1F5CA4009EE9E4DBC197B4EA132758427582446048BD6E68B96E6E327054F81",
)

# Logical 368x160 artwork cells in PORT2 /2/0 texture 1.  These coordinates
# were confirmed against the issue screenshot and the JP/EN/SC/TC archives.
APPROVE_ALL_CELLS: tuple[Mapping[str, Any], ...] = (
    {"name": "cyan_alt", "rect": (4, 308, 372, 468), "style": "cyan"},
    {"name": "disabled_alt", "rect": (380, 308, 748, 468), "style": "disabled"},
    {"name": "white", "rect": (2412, 188, 2780, 348), "style": "white"},
    {"name": "cyan", "rect": (2788, 188, 3156, 348), "style": "cyan"},
    {"name": "blue", "rect": (3164, 188, 3532, 348), "style": "blue"},
    {"name": "disabled", "rect": (3540, 188, 3908, 348), "style": "disabled"},
)

# Alpha>=1 native component bounds in PORT1 /2/0 texture 2.  State 0 is the
# larger highlighted variant; states 1..6 share the same 493x146 geometry.
BATTLE_TARGET_RECTS: tuple[tuple[int, int, int, int], ...] = (
    (8, 5, 516, 159),
    (534, 6, 1027, 152),
    (1054, 6, 1547, 152),
    (1574, 6, 2067, 152),
    (2094, 6, 2587, 152),
    (2614, 6, 3107, 152),
    (3134, 6, 3627, 152),
)


class BuildError(RuntimeError):
    """Raised when an input or a preservation gate differs."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BuildError(message)


def sha256_bytes(blob: bytes | bytearray | memoryview) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def file_spec(path: Path) -> dict[str, Any]:
    return {"path": str(path), "size": path.stat().st_size, "sha256": sha256_file(path)}


def pin_file(path: Path, expected: Mapping[str, Any], label: str) -> dict[str, Any]:
    actual = file_spec(path)
    require(actual["size"] == expected["size"] and actual["sha256"] == expected["sha256"], f"{label} pin differs: {actual}")
    return actual


def atomic_write(path: Path, blob: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(blob)
    temporary.replace(path)


def fresh_output(path: Path) -> Path:
    resolved = path.resolve()
    tmp = (REPO / "tmp").resolve()
    try:
        resolved.relative_to(tmp)
    except ValueError as exc:
        raise BuildError(f"output must remain below {tmp}: {resolved}") from exc
    require(not resolved.exists(), f"refusing to replace existing output: {resolved}")
    resolved.mkdir(parents=True)
    return resolved


def load_external(dependency_root: Path) -> tuple[Any, Any, Any]:
    root = dependency_root.resolve(strict=True)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    cv2 = importlib.import_module("cv2")
    ispc = importlib.import_module("ispc_texcomp")
    decoder = importlib.import_module("texture2ddecoder")
    require(getattr(ispc, "__version__", None) == "1.0.1", "ispc_texcomp version differs")
    return cv2, ispc, decoder


def bc7_texture_payload(raw: bytes, texture: atlas_codec.Texture) -> bytes:
    require(texture.format_code == 0x5F, f"texture {texture.index} is not BC7")
    size = ((texture.width + 3) // 4) * ((texture.height + 3) // 4) * 16
    end = texture.payload_offset + size
    require(end <= len(raw), f"texture {texture.index} BC7 payload exceeds G1T")
    return raw[texture.payload_offset:end]


def decode_bc7(payload: bytes, width: int, height: int, decoder: Any) -> Image.Image:
    bgra = decoder.decode_bc7(payload, width, height)
    require(len(bgra) == width * height * 4, "BC7 decoder geometry differs")
    return Image.frombytes("RGBA", (width, height), bgra, "raw", "BGRA")


def premultiplied_resize(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    rgba = np.asarray(image.convert("RGBA"), dtype=np.uint8)
    alpha = rgba[:, :, 3:4].astype(np.float32) / 255.0
    premultiplied = rgba[:, :, :3].astype(np.float32) * alpha
    channels: list[Image.Image] = []
    for index in range(3):
        channel = Image.fromarray(np.rint(premultiplied[:, :, index]).astype(np.uint8), "L")
        channels.append(channel.resize(size, Image.Resampling.LANCZOS))
    resized_alpha = Image.fromarray(rgba[:, :, 3], "L").resize(size, Image.Resampling.LANCZOS)
    out_alpha = np.asarray(resized_alpha, dtype=np.uint8)
    out = np.zeros((size[1], size[0], 4), dtype=np.uint8)
    out[:, :, 3] = out_alpha
    denominator = np.maximum(out_alpha.astype(np.float32), 1.0)[:, :, None]
    for index, channel in enumerate(channels):
        values = np.asarray(channel, dtype=np.float32) * 255.0 / denominator[:, :, 0]
        out[:, :, index] = np.where(out_alpha > 0, np.clip(np.rint(values), 0, 255), 0).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def render_approve_all_cell(cell: Image.Image, style: str, font_path: Path, cv2: Any) -> tuple[Image.Image, dict[str, Any]]:
    require(cell.size == (368, 160), f"approve-all cell geometry differs: {cell.size}")
    source = np.asarray(cell.convert("RGBA"), dtype=np.uint8)
    rgb = source[:, :, :3]
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    value, saturation = hsv[:, :, 2], hsv[:, :, 1]
    yy, xx = np.mgrid[:160, :368]
    region = (xx >= 142) & (xx < 318) & (yy >= 38) & (yy < 118)
    if style in {"cyan", "blue"}:
        core = (value >= 220) & (saturation <= 55) & region
        kernel = 9
    elif style == "disabled":
        core = (value <= 78) & region
        kernel = 7
    elif style == "white":
        core = (value <= 195) & region
        kernel = 5
    else:  # pragma: no cover - fixed table gate.
        raise BuildError(f"unknown approve-all style: {style}")
    mask = cv2.dilate(core.astype(np.uint8) * 255, np.ones((kernel, kernel), np.uint8), iterations=1)
    require(7_000 <= int(np.count_nonzero(mask)) <= 9_500, f"Japanese label mask differs for {style}: {np.count_nonzero(mask)}")
    cleaned_bgr = cv2.inpaint(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), mask, 4, cv2.INPAINT_TELEA)
    cleaned = cv2.cvtColor(cleaned_bgr, cv2.COLOR_BGR2RGB)
    result = Image.fromarray(np.dstack([cleaned, source[:, :, 3]]).astype(np.uint8), "RGBA")

    font = ImageFont.truetype(str(font_path), 60)
    if style in {"cyan", "blue"}:
        fill = (255, 255, 255, 255)
        stroke = (55, 76, 112, 255) if style == "cyan" else (62, 86, 134, 255)
        stroke_width = 4 if style == "cyan" else 2
    elif style == "white":
        fill, stroke, stroke_width = (139, 117, 82, 255), (139, 117, 82, 255), 0
    else:
        fill, stroke, stroke_width = (61, 58, 49, 255), (61, 58, 49, 255), 0
    art = Image.new("RGBA", (300, 110), (0, 0, 0, 0))
    draw = ImageDraw.Draw(art)
    bbox = draw.textbbox((0, 0), "전체 승인", font=font, stroke_width=stroke_width)
    draw.text(
        (-bbox[0] + 4, -bbox[1] + 4),
        "전체 승인",
        font=font,
        fill=fill,
        stroke_width=stroke_width,
        stroke_fill=stroke,
    )
    artwork_bbox = art.getchannel("A").getbbox()
    require(artwork_bbox is not None, "rendered Korean label is empty")
    art = art.crop(artwork_bbox)
    if art.width > 198:
        art = premultiplied_resize(art, (198, art.height))
    x, y = 238 - art.width // 2, 80 - art.height // 2
    require(x >= 138 and x + art.width <= 338, "Korean label placement escaped the safe band")
    result.alpha_composite(art, (x, y))
    return result, {
        "style": style,
        "japanese_mask_pixels": int(np.count_nonzero(mask)),
        "font_size": 60,
        "rendered_size": list(art.size),
        "placement": [x, y],
        "label": "전체 승인",
    }


def encode_bc7_cells(
    original: Image.Image,
    requested: Image.Image,
    original_payload: bytes,
    cells: Sequence[Mapping[str, Any]],
    ispc: Any,
) -> tuple[bytes, dict[str, Any]]:
    width, height = requested.size
    require((width, height) == (4096, 1024), "approve-all BC7 texture geometry differs")
    output = bytearray(original_payload)
    blocks_wide = width // 4
    settings = ispc.BC7EncSettings.from_profile("alpha_slow")
    allowed: set[tuple[int, int]] = set()
    for cell in cells:
        left, top, right, bottom = (int(value) for value in cell["rect"])
        patch = requested.crop((left, top, right, bottom)).convert("RGBA")
        baseline = np.asarray(original.crop((left, top, right, bottom)).convert("RGBA"), dtype=np.uint8)
        candidate = np.asarray(patch, dtype=np.uint8)
        pixel_mask = np.any(baseline != candidate, axis=2)
        require(bool(np.any(pixel_mask)), f"BC7 cell has no requested pixel delta: {cell['name']}")
        block_mask = pixel_mask.reshape(patch.height // 4, 4, patch.width // 4, 4).any(axis=(1, 3))
        require(patch.width % 4 == patch.height % 4 == 0, "BC7 cell is not block aligned")
        encoded = ispc.compress_blocks_bc7(ispc.RGBASurface(patch.tobytes(), patch.width, patch.height), settings)
        require(len(encoded) == patch.width * patch.height, "BC7 encoded cell size differs")
        local_blocks_wide = patch.width // 4
        for local_y in range(patch.height // 4):
            for local_x in range(local_blocks_wide):
                if not bool(block_mask[local_y, local_x]):
                    continue
                block_x, block_y = left // 4 + local_x, top // 4 + local_y
                allowed.add((block_x, block_y))
                source = (local_y * local_blocks_wide + local_x) * 16
                target = (block_y * blocks_wide + block_x) * 16
                output[target : target + 16] = encoded[source : source + 16]
    changed = {
        (index % blocks_wide, index // blocks_wide)
        for index in range(len(original_payload) // 16)
        if original_payload[index * 16 : index * 16 + 16] != output[index * 16 : index * 16 + 16]
    }
    require(changed and changed <= allowed, "BC7 changes escaped approve-all cells")
    return bytes(output), {
        "allowed_bc7_blocks": len(allowed),
        "changed_bc7_blocks": len(changed),
        "changed_block_bbox": highres.changed_block_bbox(sorted(changed)),
        "unselected_bc7_blocks_byte_preserved": True,
        "encoder": "ispc_texcomp 1.0.1 alpha_slow",
    }


def compose_port2(raw: bytes, g1t: atlas_codec.G1T, font: Path, cv2: Any, ispc: Any, decoder: Any, preview: Path) -> tuple[bytes, dict[str, Any]]:
    require(len(g1t.textures) == 2, "PORT2 /2/0 G1T texture count differs")
    texture = g1t.textures[1]
    require((texture.format_code, texture.width, texture.height) == (0x5F, 4096, 1024), "PORT2 approve-all texture contract differs")
    original_payload = bc7_texture_payload(raw, texture)
    atlas = decode_bc7(original_payload, texture.width, texture.height, decoder)
    before = atlas.copy()
    rows: list[dict[str, Any]] = []
    for item in APPROVE_ALL_CELLS:
        rect = tuple(int(value) for value in item["rect"])
        replacement, details = render_approve_all_cell(atlas.crop(rect), str(item["style"]), font, cv2)
        atlas.paste(replacement, rect[:2])
        rows.append({"name": item["name"], "rect": list(rect), **details})
    payload, preservation = encode_bc7_cells(before, atlas, original_payload, APPROVE_ALL_CELLS, ispc)
    decoded = decode_bc7(payload, texture.width, texture.height, decoder)
    preview.parent.mkdir(parents=True, exist_ok=True)
    contact = Image.new("RGBA", (368 * 3, 160 * 2), (0, 0, 0, 0))
    for index, item in enumerate(APPROVE_ALL_CELLS):
        contact.alpha_composite(decoded.crop(tuple(item["rect"])), ((index % 3) * 368, (index // 3) * 160))
    contact.save(preview, optimize=False)
    output = bytearray(raw)
    start = texture.payload_offset
    output[start : start + len(payload)] = payload
    require(output[:start] == raw[:start] and output[start + len(payload) :] == raw[start + len(payload) :], "PORT2 bytes outside texture 1 changed")
    require(before.size == decoded.size, "PORT2 decode verification geometry differs")
    return bytes(output), {
        "outer_entry": 2,
        "resource_id": 870,
        "nested_slot": 0,
        "texture_index": 1,
        "format": "BC7/0x5F",
        "dimensions": [texture.width, texture.height],
        "cells": rows,
        "preview": file_spec(preview),
        "unselected_g1t_bytes_preserved": True,
        **preservation,
    }


def compose_port1(texture: atlas_codec.Texture, source_root: Path, preview: Path) -> tuple[bytes, dict[str, Any]]:
    require((texture.format_code, texture.width, texture.height) == (0x5B, 4096, 2048), "PORT1 battle-start texture contract differs")
    decoded = atlas_codec.decode_texture(texture)
    require(decoded is not None, "PORT1 battle-start texture could not decode")
    atlas = Image.frombytes("RGBA", (texture.width, texture.height), decoded)
    rows: list[dict[str, Any]] = []
    allowed: set[tuple[int, int]] = set()
    for state, (target, expected_hash) in enumerate(zip(BATTLE_TARGET_RECTS, BATTLE_SOURCE_PINS)):
        source_path = source_root / f"battle_start_state{state}_alpha.png"
        require(source_path.is_file(), f"missing battle-start state: {source_path}")
        require(sha256_file(source_path) == expected_hash, f"battle-start state {state} hash differs")
        source = Image.open(source_path).convert("RGBA")
        require(source.size == (264, 88), f"battle-start state {state} geometry differs: {source.size}")
        source_bbox = source.getchannel("A").getbbox()
        require(source_bbox is not None, f"battle-start state {state} is empty")
        width, height = target[2] - target[0], target[3] - target[1]
        resized = premultiplied_resize(source.crop(source_bbox), (width, height))
        atlas.paste((0, 0, 0, 0), target)
        atlas.alpha_composite(resized, target[:2])
        allowed.update(highres.rect_blocks(target, texture.width, texture.height))
        rows.append({
            "state": state,
            "source": file_spec(source_path),
            "source_alpha_bbox": list(source_bbox),
            "target_rect": list(target),
            "target_size": [width, height],
            "resampler": "premultiplied-alpha Lanczos3",
        })
    payload, encoded = highres.encode_selected_blocks(atlas.tobytes(), texture.width, texture.height, texture.payload, allowed)
    blocks_wide = texture.width // 4
    changed = [
        (index % blocks_wide, index // blocks_wide)
        for index in range(len(payload) // 16)
        if payload[index * 16 : index * 16 + 16] != texture.payload[index * 16 : index * 16 + 16]
    ]
    require(changed and set(changed) <= allowed, "PORT1 BC3 changes escaped battle-start rectangles")
    preview.parent.mkdir(parents=True, exist_ok=True)
    decoded_candidate = Image.frombytes("RGBA", (texture.width, texture.height), atlas_codec.decode_texture(atlas_codec.Texture(
        texture.index, texture.format_code, texture.width, texture.height, texture.mip_count, texture.extra_version, texture.payload_offset, payload
    )))
    contact = Image.new("RGBA", (520 * 4, 168 * 2), (0, 0, 0, 0))
    for state, target in enumerate(BATTLE_TARGET_RECTS):
        logical = (state * 520, 0, state * 520 + 520, 168)
        contact.alpha_composite(decoded_candidate.crop(logical), ((state % 4) * 520, (state // 4) * 168))
    contact.save(preview, optimize=False)
    return payload, {
        "outer_entry": 2,
        "resource_id": 3860,
        "nested_slot": 0,
        "texture_index": 2,
        "format": "BC3/0x5B",
        "dimensions": [texture.width, texture.height],
        "states": rows,
        "preview": file_spec(preview),
        "allowed_bc3_blocks": len(allowed),
        "encoded_bc3_blocks": encoded,
        "changed_bc3_blocks": len(changed),
        "changed_block_bbox": highres.changed_block_bbox(changed),
        "unselected_bc3_blocks_byte_preserved": True,
    }


def rebuild_archive(source: Path, destination: Path, replacement_outer: bytes) -> dict[str, Any]:
    blob = source.read_bytes()
    outer = lz4.parse_link(blob)
    require(lz4.rebuild_link(outer) == blob, f"outer LINK identity failed: {source}")
    candidate_blob = lz4.rebuild_link(outer, {2: replacement_outer})
    candidate = lz4.parse_link(candidate_blob)
    require(lz4.rebuild_link(candidate) == candidate_blob, f"candidate outer LINK identity failed: {destination}")
    changed = [index for index in range(len(outer.entries)) if outer.entries[index].data != candidate.entries[index].data]
    require(changed == [2], f"changed outer scope differs: {source.name}: {changed}")
    for index in range(len(outer.entries)):
        if index != 2:
            require(outer.entries[index].data == candidate.entries[index].data and outer.entries[index].gap_after == candidate.entries[index].gap_after, f"unrelated outer {index} changed")
    atomic_write(destination, candidate_blob)
    return {
        "source": file_spec(source),
        "candidate": file_spec(destination),
        "changed_outer_entries": changed,
        "unrelated_outer_entries_byte_preserved": True,
        "outer_link_identity_verified": True,
    }


def rebuild_nested_with_raw(nested: highres.NestedLink, slot: int, header: lz4.WrapperHeader, raw: bytes) -> bytes:
    wrapper = lz4.recompress_wrapper_greedy(raw, header)
    _, roundtrip = lz4.decompress_wrapper(wrapper)
    require(roundtrip == raw, "G1T wrapper roundtrip failed")
    rebuilt = highres.rebuild_nested_link(nested, {slot: wrapper})
    reparsed = highres.parse_nested_link(rebuilt, expected_resource_id=nested.resource_id)
    require(reparsed.table_padding == nested.table_padding, "nested table padding changed")
    for entry in nested.entries:
        if entry.index != slot:
            require(reparsed.entries[entry.index].data == entry.data and reparsed.entries[entry.index].gap_after == entry.gap_after, f"unrelated nested entry {entry.index} changed")
    return rebuilt


def build(args: argparse.Namespace) -> dict[str, Any]:
    port1 = args.port1.resolve(strict=True)
    port2 = args.port2.resolve(strict=True)
    source_root = args.battle_source_root.resolve(strict=True)
    font = args.font.resolve(strict=True)
    require(sha256_file(font) == FONT_PIN, "SeoulHangangEB font pin differs")
    output = fresh_output(args.output_root)
    inputs = {
        "port1": pin_file(port1, PORT1_PIN, "PORT1"),
        "port2": pin_file(port2, PORT2_PIN, "PORT2"),
        "font": file_spec(font),
    }
    cv2, ispc, decoder = load_external(args.dependency_root)

    port1_outer = lz4.parse_link(port1.read_bytes())
    port1_nested = highres.parse_nested_link(port1_outer.entries[2].data, expected_resource_id=3860)
    p1_slot, p1_header, p1_raw, p1_g1t = highres.g1t_wrapper_entry(port1_nested)
    require(p1_slot == 0 and len(p1_g1t.textures) > 2, "PORT1 G1T route differs")
    p1_payload, p1_report = compose_port1(p1_g1t.textures[2], source_root, output / "preview" / "highres_battle_start_contact.png")
    rebuilt_p1_raw = highres.replace_g1t_payloads(p1_raw, p1_g1t, {2: p1_payload})
    require(rebuilt_p1_raw[: p1_g1t.textures[2].payload_offset] == p1_raw[: p1_g1t.textures[2].payload_offset], "PORT1 bytes before texture 2 changed")
    rebuilt_p1_nested = rebuild_nested_with_raw(port1_nested, p1_slot, p1_header, rebuilt_p1_raw)

    port2_outer = lz4.parse_link(port2.read_bytes())
    port2_nested = highres.parse_nested_link(port2_outer.entries[2].data, expected_resource_id=870)
    p2_slot, p2_header, p2_raw, p2_g1t = highres.g1t_wrapper_entry(port2_nested)
    require(p2_slot == 0, "PORT2 G1T slot differs")
    rebuilt_p2_raw, p2_report = compose_port2(p2_raw, p2_g1t, font, cv2, ispc, decoder, output / "preview" / "issue117_approve_all_contact.png")
    rebuilt_p2_nested = rebuild_nested_with_raw(port2_nested, p2_slot, p2_header, rebuilt_p2_raw)

    candidate_root = output / "candidate" / "RES_JP_PK_PORT"
    archives = {
        "port1": rebuild_archive(port1, candidate_root / "res_lang_pk_port1.bin", rebuilt_p1_nested),
        "port2": rebuild_archive(port2, candidate_root / "res_lang_pk_port2.bin", rebuilt_p2_nested),
    }
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "inputs": inputs,
        "routes": {"highres_battle_start": p1_report, "issue117_approve_all": p2_report},
        "archives": archives,
        "safety": {
            "file_only": True,
            "executable_modified": False,
            "dll_injection": False,
            "process_memory_access": False,
            "game_files_written": False,
        },
    }
    report["report_sha256"] = sha256_bytes((json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8"))
    atomic_write(output / "verification.v1.json", (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return report


def verify(args: argparse.Namespace) -> dict[str, Any]:
    root = args.candidate_root.resolve(strict=True)
    report_path = root / "verification.v1.json"
    require(report_path.is_file(), f"missing verification report: {report_path}")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    require(report.get("schema") == SCHEMA, "verification schema differs")
    for key, filename in (("port1", "res_lang_pk_port1.bin"), ("port2", "res_lang_pk_port2.bin")):
        candidate = root / "candidate" / "RES_JP_PK_PORT" / filename
        expected = report["archives"][key]["candidate"]
        require(candidate.stat().st_size == expected["size"] and sha256_file(candidate) == expected["sha256"], f"candidate {key} differs")
        parsed = lz4.parse_link(candidate.read_bytes())
        require(lz4.rebuild_link(parsed) == candidate.read_bytes(), f"candidate {key} LINK identity failed")
    require(report["routes"]["issue117_approve_all"]["unselected_bc7_blocks_byte_preserved"] is True, "BC7 preservation proof missing")
    require(report["routes"]["highres_battle_start"]["unselected_bc3_blocks_byte_preserved"] is True, "BC3 preservation proof missing")
    return report


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    build_parser = commands.add_parser("build")
    build_parser.add_argument("--port1", type=Path, required=True)
    build_parser.add_argument("--port2", type=Path, required=True)
    build_parser.add_argument("--battle-source-root", type=Path, required=True)
    build_parser.add_argument("--font", type=Path, required=True)
    build_parser.add_argument("--dependency-root", type=Path, required=True)
    build_parser.add_argument("--output-root", type=Path, required=True)
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--candidate-root", type=Path, required=True)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    report = build(args) if args.command == "build" else verify(args)
    print(f"status=PASS")
    print(f"report_sha256={report['report_sha256']}")
    print("game_files_written=false")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BuildError, lz4.LZ4Error, atlas_codec.AtlasError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
