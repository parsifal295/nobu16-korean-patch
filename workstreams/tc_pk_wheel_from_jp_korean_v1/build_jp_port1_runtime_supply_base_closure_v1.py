#!/usr/bin/env python3
"""Replace PORT1 resource-42 Japanese supply-base wheel duplicates with Korean."""

from __future__ import annotations

import argparse
import dataclasses
import gc
import json
import sys
from pathlib import Path
from typing import Any, Mapping

from PIL import Image, ImageDraw


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parent.parent
TOOLS = REPO / "tools"
IMAGE_WORKSTREAM = REPO / "workstreams" / "steam_jp_port_highres_images_v1"
for candidate in (WORKSTREAM, TOOLS, IMAGE_WORKSTREAM):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import extract_nobu16_image_atlases as atlas_codec  # noqa: E402
import nobu16_lz4 as lz4  # noqa: E402
import build_steam_jp_port_highres_images_v1 as base  # noqa: E402
import build_tc_pk_wheel_from_jp_korean_v1 as wheel  # noqa: E402


SCHEMA = "nobu16.kr.jp-port1-runtime-supply-base-closure.v1"
PINS: dict[str, dict[str, Any]] = {
    "port1": {
        "size": 82_910_041,
        "sha256": "BC4C87DD1D93BF944929E6341517828365C59203913E98302DF1A843571623D2",
    },
    "pk_low": {
        "size": 141_893_576,
        "sha256": "9019582ABBF88B08562B366E7D5A4283C6507455F86A801946AC32CCC25C2C2F",
    },
    "pk_high": {
        "size": 67_623_137,
        "sha256": "09531F21FA3BD56E2554C47942E47B5ACB61A7F279EFBF4AF85E4CAB963E4FAA",
    },
}
TARGET_OUTERS = {1: 36, 2: 37}
SOURCE_RECORDS = tuple(range(48, 54))
TARGET_RECORDS = tuple(range(32, 38))


class RuntimeSupplyBaseError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeSupplyBaseError(message)


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


def load_resource42(
    outer: lz4.LinkArchive,
    *,
    outer_index: int,
    scale: int,
) -> dict[str, Any]:
    nested = base.parse_nested_link(
        outer.entries[outer_index].data, expected_resource_id=42
    )
    slot, wrapper_header, raw, g1t = base.g1t_wrapper_entry(nested)
    require(len(g1t.textures) == 1, f"resource42 outer {outer_index} texture count differs")
    texture = g1t.textures[0]
    expected_dimensions = (512, 256) if scale == 1 else (1024, 512)
    require(
        (texture.width, texture.height, texture.format_code)
        == (*expected_dimensions, 0x5B),
        f"resource42 outer {outer_index} texture differs: "
        f"{(texture.width, texture.height, texture.format_code)}",
    )
    # Resource 42 has 42 records, unlike the 82-record PK-wheel resource.
    # Reparse the same table without the PK count gate.
    layout = nested.table_padding[24:]
    records = []
    import struct

    for index in range((len(layout) - 8) // 12):
        first, second, third = struct.unpack_from("<III", layout, index * 12)
        records.append(
            (first & 0xFFFF, first >> 16, second & 0xFFFF, second >> 16, third)
        )
    require(len(records) == 42, f"resource42 record count differs: {len(records)}")
    expected_core = (96, 88, 0) if scale == 1 else (192, 176, 0)
    expected_positions = (
        [(4, 4), (108, 4), (212, 4), (316, 4), (4, 100), (108, 100)]
        if scale == 1
        else [(4, 4), (204, 4), (404, 4), (604, 4), (804, 4), (4, 188)]
    )
    for state, record_index in enumerate(TARGET_RECORDS):
        x, y, width, height, third = records[record_index]
        require(
            (x, y) == expected_positions[state]
            and (width, height, third) == expected_core,
            f"resource42 outer {outer_index} record {record_index} differs: "
            f"{records[record_index]}",
        )
    decoded = atlas_codec.decode_texture(texture)
    require(decoded is not None, f"resource42 outer {outer_index} decode failed")
    return {
        "outer_index": outer_index,
        "nested": nested,
        "slot": slot,
        "wrapper_header": wrapper_header,
        "raw": raw,
        "g1t": g1t,
        "texture": texture,
        "records": records,
        "atlas": Image.frombytes("RGBA", expected_dimensions, decoded),
    }


def make_contact(
    before: Image.Image,
    after: Image.Image,
    records: list[tuple[int, int, int, int, int]],
    destination: Path,
) -> None:
    before_cells = [
        wheel.extract_cell(before, wheel.record_rect(records[index]))
        for index in TARGET_RECORDS
    ]
    after_cells = [
        wheel.extract_cell(after, wheel.record_rect(records[index]))
        for index in TARGET_RECORDS
    ]
    cell_width = max(cell.width for cell in before_cells + after_cells)
    cell_height = max(cell.height for cell in before_cells + after_cells)
    canvas = Image.new(
        "RGB", (cell_width * 6, cell_height * 2 + 44), (24, 24, 24)
    )
    draw = ImageDraw.Draw(canvas)
    draw.text((4, 4), "RESOURCE 42 BEFORE JP", fill=(255, 255, 255))
    draw.text((4, cell_height + 26), "RESOURCE 42 AFTER KO", fill=(255, 255, 255))
    for row, cells in enumerate((before_cells, after_cells)):
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


def compose_resource42(
    source: Mapping[str, Any],
    target: Mapping[str, Any],
    *,
    scale: int,
    preview: Path,
) -> tuple[bytes, dict[str, Any]]:
    source_atlas: Image.Image = source["atlas"]
    target_atlas: Image.Image = target["atlas"]
    requested = target_atlas.copy()
    allowed: set[tuple[int, int]] = set()
    operations: list[dict[str, Any]] = []

    for state, (source_record, target_record) in enumerate(
        zip(SOURCE_RECORDS, TARGET_RECORDS), start=1
    ):
        source_rect = wheel.record_rect(source["records"][source_record])
        target_rect = wheel.record_rect(target["records"][target_record])
        source_cell = wheel.extract_cell(source_atlas, source_rect)
        target_size = (
            target_rect[2] - target_rect[0],
            target_rect[3] - target_rect[1],
        )
        require(
            source_cell.size == target_size,
            f"state {state} source/target geometry differs: "
            f"{source_cell.size} != {target_size}",
        )
        wheel.paste_cell_replace(requested, target_rect, source_cell)
        allowed.update(
            wheel.rect_blocks_clipped(
                target_rect, target_atlas.width, target_atlas.height
            )
        )
        operations.append(
            {
                "state": state,
                "source_resource_id": 81,
                "source_record": source_record,
                "source_rect": list(source_rect),
                "target_resource_id": 42,
                "target_record": target_record,
                "target_rect": list(target_rect),
                "cell_size": list(target_size),
            }
        )

    texture = target["texture"]
    requested_bytes = requested.tobytes()
    payload, encoded = base.encode_selected_blocks(
        requested_bytes,
        texture.width,
        texture.height,
        texture.payload,
        allowed,
    )
    encoding = wheel.verify_selected_encoding(
        requested_bytes,
        texture.payload,
        payload,
        texture.width,
        texture.height,
        allowed,
    )
    require(
        encoding["changed_bc3_blocks"] == encoded,
        "resource42 encoded block count differs",
    )
    candidate_texture = dataclasses.replace(texture, payload=payload)
    decoded = atlas_codec.decode_texture(candidate_texture)
    require(decoded is not None, "resource42 candidate decode failed")
    candidate_atlas = Image.frombytes(
        "RGBA", (texture.width, texture.height), decoded
    )
    make_contact(target_atlas, candidate_atlas, target["records"], preview)
    return payload, {
        "scale": scale,
        "outer": target["outer_index"],
        "resource_id": 42,
        "texture_index": 0,
        "dimensions": [texture.width, texture.height],
        "operations": operations,
        "operation_count": len(operations),
        "source_label": "보급거점",
        "target_japanese_label": "補給拠点",
        "full_cell_replacement": True,
        "source_derived_block_verification": encoding,
        "preview": file_spec(preview),
    }


def rebuild_nested(
    target: Mapping[str, Any],
    payload: bytes,
) -> tuple[bytes, dict[str, Any]]:
    raw = target["raw"]
    rebuilt_raw = base.replace_g1t_payloads(raw, target["g1t"], {0: payload})
    require(len(rebuilt_raw) == len(raw), "resource42 G1T raw size changed")
    wrapper = lz4.recompress_wrapper_greedy(
        rebuilt_raw, target["wrapper_header"]
    )
    _, roundtrip = lz4.decompress_wrapper(wrapper)
    require(roundtrip == rebuilt_raw, "resource42 wrapper roundtrip failed")
    nested = target["nested"]
    rebuilt = base.rebuild_nested_link(nested, {target["slot"]: wrapper})
    reparsed = base.parse_nested_link(rebuilt, expected_resource_id=42)
    require(
        reparsed.table_padding == nested.table_padding,
        "resource42 layout/table padding changed",
    )
    for entry in nested.entries:
        if entry.index == target["slot"]:
            continue
        require(
            reparsed.entries[entry.index].data == entry.data
            and reparsed.entries[entry.index].gap_after == entry.gap_after,
            f"resource42 unselected nested entry {entry.index} changed",
        )
    return rebuilt, {
        "layout_table_byte_preserved": True,
        "unselected_nested_entries_byte_preserved": True,
        "wrapper_roundtrip_verified": True,
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    paths = {
        name: getattr(args, name).resolve(strict=True)
        for name in ("port1", "pk_low", "pk_high")
    }
    inputs = {name: pin(paths[name], PINS[name], name) for name in paths}
    output = base.fresh_output(args.output.resolve())

    port1_blob = paths["port1"].read_bytes()
    port1_outer = lz4.parse_link(port1_blob)
    require(
        lz4.rebuild_link(port1_outer) == port1_blob,
        "PORT1 outer LINK identity failed",
    )
    source_low = wheel.load_route(
        paths["pk_low"], outer_index=1, scale=1, route="JP_PK_low"
    )
    source_high = wheel.load_route(
        paths["pk_high"], outer_index=3, scale=2, route="JP_PK_high"
    )

    replacements: dict[int, bytes] = {}
    routes: dict[str, Any] = {}
    for scale_name, scale, source in (
        ("low", 1, source_low),
        ("high", 2, source_high),
    ):
        outer_index = TARGET_OUTERS[scale]
        target = load_resource42(
            port1_outer, outer_index=outer_index, scale=scale
        )
        preview = (
            output
            / "preview"
            / f"resource42_outer{outer_index}_{scale_name}_before_after.png"
        )
        payload, composition = compose_resource42(
            source, target, scale=scale, preview=preview
        )
        rebuilt, rebuild = rebuild_nested(target, payload)
        replacements[outer_index] = rebuilt
        routes[scale_name] = {
            "composition": composition,
            "rebuild": rebuild,
        }
        del target, payload
        gc.collect()

    before_hashes = base.outer_hashes(port1_outer)
    candidate_blob = lz4.rebuild_link(port1_outer, replacements)
    candidate_outer = lz4.parse_link(candidate_blob)
    require(
        lz4.rebuild_link(candidate_outer) == candidate_blob,
        "PORT1 candidate outer LINK identity failed",
    )
    after_hashes = base.outer_hashes(candidate_outer)
    changed = [
        index
        for index in range(len(candidate_outer.entries))
        if before_hashes[str(index)] != after_hashes[str(index)]
    ]
    require(changed == [36, 37], f"PORT1 changed outer scope differs: {changed}")
    for entry in port1_outer.entries:
        if entry.index in replacements:
            continue
        require(
            candidate_outer.entries[entry.index].data == entry.data
            and candidate_outer.entries[entry.index].gap_after == entry.gap_after,
            f"PORT1 unselected outer entry {entry.index} changed",
        )

    candidate_path = (
        output
        / "candidate"
        / "RES_JP_PK_PORT"
        / "res_lang_pk_port1.bin"
    )
    base.atomic_write(
        candidate_path, candidate_blob, forbidden=tuple(paths.values())
    )
    report = {
        "schema": SCHEMA,
        "inputs": inputs,
        "runtime_evidence": {
            "resolution": "1920x1080",
            "full_restart_after_previous_deployment": True,
            "process_start": "2026-07-27T11:47:16+09:00",
            "observed_japanese_label": "補給拠点",
            "pixel_template_exact_match": {
                "archive": str(paths["port1"]),
                "outer": 37,
                "resource_id": 42,
                "records": [35, 37],
                "score": 0.0,
            },
        },
        "source": {
            "resource_id": 81,
            "label": "보급거점",
            "records": list(SOURCE_RECORDS),
        },
        "target": {
            "resource_id": 42,
            "label": "補給拠点",
            "records": list(TARGET_RECORDS),
            "outers": [36, 37],
        },
        "routes": routes,
        "candidate": file_spec(candidate_path),
        "changed_outer_entries": changed,
        "unselected_outer_entries_byte_preserved": True,
        "steam_files_written": False,
        "runtime_qa_pending": True,
    }
    report_path = output / "build_report.json"
    base.write_json(
        report_path, report, forbidden=tuple(paths.values())
    )
    return {
        "report": str(report_path),
        "candidate": report["candidate"],
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--port1", type=Path, required=True)
    result.add_argument("--pk-low", type=Path, required=True)
    result.add_argument("--pk-high", type=Path, required=True)
    result.add_argument("--output", type=Path, required=True)
    return result


def main() -> None:
    print(json.dumps(build(parser().parse_args()), ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
