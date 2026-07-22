#!/usr/bin/env python3
"""Build a private PORT3 candidate from the approved deterministic title PNGs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parent.parent
TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import nobu16_lz4 as lz4  # noqa: E402
import pc_g1t_title_codec as codec  # noqa: E402


SCHEMA = "nobu16.kr.port3-title-consistency-candidate.v1"
EXPECTED_BASE = {
    "size": 43_460_485,
    "sha256": "BE1361E17341D433931EB5740B228EF1842BF6DF2F01D4F582CE790A9A57A154",
}
TITLE_COUNT = 110
WIDTH = 1024
HEIGHT = 256
FORMAT_BC3 = 0x5B
EXPECTED_TEXCONV = {
    "size": 966_480,
    "sha256": "DCFDEC10244E02CF5037FBA089C55FB7E1326B1C8181742D77D15FA5CB5EEF06",
    "version": "2026.5.8.1",
}


class CandidateError(ValueError):
    """Raised when the narrow PORT3 title candidate contract is violated."""


@dataclass(frozen=True)
class TitleG1T:
    raw: bytes
    payload_offset: int
    payload_end: int
    bc3: bytes


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CandidateError(message)


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def file_spec(path: Path) -> dict[str, int | str]:
    return {"size": path.stat().st_size, "sha256": sha256_bytes(path.read_bytes())}


def ensure_tmp(path: Path) -> Path:
    resolved = path.resolve()
    tmp = (REPO / "tmp").resolve()
    require(resolved != tmp and tmp in resolved.parents, f"output must stay below tmp: {resolved}")
    return resolved


def atomic_write(path: Path, blob: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_bytes(blob)
    os.replace(temp, path)


def alpha_bbox(rgba: bytes, width: int, height: int) -> list[int]:
    require(len(rgba) == width * height * 4, "RGBA length differs")
    left, top, right, bottom = width, height, -1, -1
    count = 0
    for y in range(height):
        row = y * width * 4
        for x in range(width):
            if rgba[row + x * 4 + 3]:
                count += 1
                left = min(left, x)
                top = min(top, y)
                right = max(right, x)
                bottom = max(bottom, y)
    require(count > 0, "title image is blank")
    return [left, top, right, bottom, count]


def parse_title_g1t(raw: bytes) -> TitleG1T:
    require(len(raw) >= 56 and raw[:8] == b"GT1G0600", "title is not GT1G0600")
    file_size, directory_offset, texture_count, platform = struct.unpack_from("<4I", raw, 8)
    require(file_size == len(raw), "G1T file size field differs")
    require((directory_offset, texture_count, platform) == (0x20, 1, 0x0A), "G1T layout differs")
    relative_offset = struct.unpack_from("<I", raw, directory_offset)[0]
    texture_offset = directory_offset + relative_offset
    require(texture_offset == 0x24, "G1T texture offset differs")
    packed_info, format_code, packed_dimensions = struct.unpack_from("<BBB", raw, texture_offset)
    mip_count = packed_info >> 4
    width = 1 << (packed_dimensions & 0x0F)
    height = 1 << (packed_dimensions >> 4)
    require((width, height, mip_count, format_code) == (WIDTH, HEIGHT, 1, FORMAT_BC3), "title texture contract differs")
    extra_version = raw[texture_offset + 7]
    extra_length = struct.unpack_from("<I", raw, texture_offset + 8)[0]
    require((extra_version, extra_length) == (0x10, 12), "G1T extra header differs")
    payload_offset = texture_offset + 8 + extra_length
    payload_end = payload_offset + WIDTH * HEIGHT
    require(payload_end == len(raw), "G1T BC3 payload extent differs")
    return TitleG1T(raw=raw, payload_offset=payload_offset, payload_end=payload_end, bc3=raw[payload_offset:payload_end])


def replace_bc3(texture: TitleG1T, bc3: bytes) -> bytes:
    require(len(bc3) == len(texture.bc3), "replacement BC3 size differs")
    rebuilt = texture.raw[: texture.payload_offset] + bc3 + texture.raw[texture.payload_end :]
    require(parse_title_g1t(rebuilt).bc3 == bc3, "rebuilt G1T payload drifted")
    return rebuilt


def parse_dds_bc3(path: Path) -> bytes:
    blob = path.read_bytes()
    require(len(blob) == 128 + WIDTH * HEIGHT, f"DDS size differs: {path}")
    require(blob[:4] == b"DDS " and struct.unpack_from("<I", blob, 4)[0] == 124, f"DDS header differs: {path}")
    require(struct.unpack_from("<II", blob, 12) == (HEIGHT, WIDTH), f"DDS geometry differs: {path}")
    require(blob[84:88] == b"DXT5", f"DDS is not legacy DXT5: {path}")
    return blob[128:]


def merge_preserved_blocks(source_rgba: bytes, template_bc3: bytes, encoded_bc3: bytes) -> tuple[bytes, int, int]:
    require(len(template_bc3) == len(encoded_bc3) == WIDTH * HEIGHT, "BC3 merge size differs")
    output = bytearray()
    preserved = 0
    encoded = 0
    block_index = 0
    for block_y in range(HEIGHT // 4):
        for block_x in range(WIDTH // 4):
            start = block_index * 16
            template_block = template_bc3[start : start + 16]
            source_block = codec.extract_rgba_block(source_rgba, WIDTH, HEIGHT, block_x, block_y)
            if codec.decode_bc3_block(template_block) == source_block:
                output.extend(template_block)
                preserved += 1
            else:
                output.extend(encoded_bc3[start : start + 16])
                encoded += 1
            block_index += 1
    return bytes(output), preserved, encoded


def load_render_contract(render_root: Path) -> tuple[dict, dict[int, dict]]:
    report_path = render_root / "report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    require(report.get("schema") == "nobu16.kr.port3-title-consistency-dimibang-preview.v1", "render report schema differs")
    require(report.get("catalog", {}).get("entry_count") == TITLE_COUNT, "render report does not cover 110 titles")
    entries = {int(row["slot"]): row for row in report["entries"]}
    require(sorted(entries) == list(range(TITLE_COUNT)), "render report slot set differs")
    policy = report["policy"]
    require(policy["horizontal_alignment"] == "fixed left ink origin at x=24", "render alignment policy differs")
    require(policy["first_glyph_font_size_px"] == 136, "first-glyph size policy differs")
    require(policy["remaining_font_size_tiers_px"] == [112, 102, 92, 84], "remaining size tiers differ")
    return report, entries


def build(base_path: Path, render_root: Path, output_root: Path, texconv_path: Path) -> dict:
    base_path = base_path.resolve()
    render_root = render_root.resolve()
    output_root = ensure_tmp(output_root)
    texconv_path = texconv_path.resolve()
    require(file_spec(base_path) == EXPECTED_BASE, "PORT3 baseline pin differs")
    require(file_spec(texconv_path) == {"size": EXPECTED_TEXCONV["size"], "sha256": EXPECTED_TEXCONV["sha256"]}, "texconv pin differs")
    version_result = subprocess.run([str(texconv_path), "--version"], check=True, capture_output=True, text=True, errors="replace")
    require(EXPECTED_TEXCONV["version"] in version_result.stdout, "texconv version differs")
    render_report, render_entries = load_render_contract(render_root)

    dds_root = output_root / "texconv_bc3"
    dds_root.mkdir(parents=True, exist_ok=True)
    file_list = output_root / "texconv_inputs.txt"
    source_paths = [render_root / "dimibang" / f"{index:03d}.png" for index in range(TITLE_COUNT)]
    require(all(path.is_file() for path in source_paths), "one or more rendered title PNGs are missing")
    atomic_write(file_list, ("\n".join(str(path) for path in source_paths) + "\n").encode("utf-8"))
    texconv_result = subprocess.run(
        [
            str(texconv_path),
            "-y",
            "-f",
            "BC3_UNORM",
            "-m",
            "1",
            "-dx9",
            "-o",
            str(dds_root),
            "--file-list",
            str(file_list),
        ],
        check=False,
        capture_output=True,
        text=True,
        errors="replace",
    )
    require(texconv_result.returncode == 0, f"texconv failed: {texconv_result.stdout[-1000:]} {texconv_result.stderr[-1000:]}")
    require(all((dds_root / f"{index:03d}.dds").is_file() for index in range(TITLE_COUNT)), "texconv did not produce 110 DDS files")

    base_blob = base_path.read_bytes()
    outer = lz4.parse_link(base_blob)
    require(lz4.rebuild_link(outer) == base_blob, "outer LINK identity rebuild failed")
    require(len(outer.entries) == 10, "PORT3 outer entry count differs")
    inner = codec.parse_inner_link32(outer.entries[0].data)
    require(len(inner.entries) == TITLE_COUNT, "PORT3 title count differs")

    roundtrip_root = output_root / "bc3_roundtrip"
    roundtrip_root.mkdir(parents=True, exist_ok=True)
    replacements: dict[int, bytes] = {}
    rows: list[dict] = []
    for index in range(TITLE_COUNT):
        if index % 10 == 0:
            print(f"stage=encode index={index}", flush=True)
        source_path = source_paths[index]
        source_rgba, width, height = codec.decode_png(source_path.read_bytes())
        require((width, height) == (WIDTH, HEIGHT), f"rendered title geometry differs at {index}")
        source_bbox = alpha_bbox(source_rgba, width, height)
        require(20 <= source_bbox[0] <= 24 and source_bbox[3] <= 158, f"rendered title placement differs at {index}: {source_bbox}")

        wrapper_before = inner.entries[index].data
        header, raw = lz4.decompress_wrapper(wrapper_before)
        texture = parse_title_g1t(raw)
        texconv_bc3 = parse_dds_bc3(dds_root / f"{index:03d}.dds")
        bc3, preserved, encoded = merge_preserved_blocks(source_rgba, texture.bc3, texconv_bc3)
        require(bc3 != texture.bc3, f"title {index} BC3 did not change")
        rebuilt_raw = replace_bc3(texture, bc3)
        wrapper_after = lz4.recompress_wrapper_greedy(rebuilt_raw, header)
        _, roundtrip_raw = lz4.decompress_wrapper(wrapper_after)
        require(roundtrip_raw == rebuilt_raw, f"title {index} wrapper roundtrip failed")
        replacements[index] = wrapper_after

        decoded = codec.decode_bc3(bc3, WIDTH, HEIGHT)
        decoded_bbox = alpha_bbox(decoded, WIDTH, HEIGHT)
        require(decoded_bbox[0] <= 24 and decoded_bbox[3] <= 159, f"BC3 title placement differs at {index}: {decoded_bbox}")
        roundtrip_path = roundtrip_root / f"{index:03d}.png"
        atomic_write(roundtrip_path, codec.encode_rgba_png(decoded, WIDTH, HEIGHT))
        entry_report = render_entries[index]
        rows.append(
            {
                "slot": index,
                "text": entry_report["text"],
                "source_png": {"path": str(source_path), **file_spec(source_path), "alpha_bbox": source_bbox},
                "bc3_roundtrip_png": {"path": str(roundtrip_path), **file_spec(roundtrip_path), "alpha_bbox": decoded_bbox},
                "blocks": {"preserved": preserved, "encoded": encoded, "total": preserved + encoded},
                "wrapper_before_sha256": sha256_bytes(wrapper_before),
                "wrapper_after_sha256": sha256_bytes(wrapper_after),
            }
        )

    rebuilt_inner = codec.rebuild_inner_link32(inner, replacements)
    reparsed_inner = codec.parse_inner_link32(rebuilt_inner)
    require(len(reparsed_inner.entries) == TITLE_COUNT, "rebuilt title LINK count differs")
    for index in range(TITLE_COUNT):
        require(reparsed_inner.entries[index].data == replacements[index], f"title replacement drifted at {index}")

    candidate_blob = lz4.rebuild_link(outer, {0: rebuilt_inner})
    candidate_path = output_root / "candidate" / "RES_JP_PK_PORT" / "res_lang_pk_port3.bin"
    require(candidate_path.resolve() != base_path, "candidate path equals baseline")
    atomic_write(candidate_path, candidate_blob)

    candidate_outer = lz4.parse_link(candidate_blob)
    require(lz4.rebuild_link(candidate_outer) == candidate_blob, "candidate outer LINK identity failed")
    changed_outers = [i for i in range(len(outer.entries)) if outer.entries[i].data != candidate_outer.entries[i].data]
    require(changed_outers == [0], f"candidate changed outer scope differs: {changed_outers}")
    for index in range(1, len(outer.entries)):
        require(candidate_outer.entries[index].data == outer.entries[index].data, f"unrelated outer {index} changed")
    candidate_inner = codec.parse_inner_link32(candidate_outer.entries[0].data)
    changed_titles = [i for i in range(TITLE_COUNT) if inner.entries[i].data != candidate_inner.entries[i].data]
    require(changed_titles == list(range(TITLE_COUNT)), "candidate changed title scope differs")

    report = {
        "schema": SCHEMA,
        "installed_game_files_modified": False,
        "release_payload_modified": False,
        "base": {"path": str(base_path), **file_spec(base_path)},
        "render": {
            "root": str(render_root),
            "report_sha256": sha256_bytes((render_root / "report.json").read_bytes()),
            "catalog": render_report["catalog"],
            "font": render_report["fonts"][0],
            "policy": render_report["policy"],
        },
        "bc3_encoder": {
            "name": "Microsoft DirectXTex texconv",
            "path": str(texconv_path),
            **file_spec(texconv_path),
            "version": EXPECTED_TEXCONV["version"],
            "format": "BC3_UNORM / legacy DXT5 / one mip",
            "source": "https://github.com/microsoft/DirectXTex/releases/tag/may2026",
        },
        "candidate": {"path": str(candidate_path), **file_spec(candidate_path)},
        "scope": {
            "changed_outer_entries": changed_outers,
            "changed_title_slots": changed_titles,
            "unrelated_outer_entries_byte_preserved": True,
            "title_count": TITLE_COUNT,
        },
        "entries": rows,
    }
    report_path = output_root / "build_report.json"
    atomic_write(report_path, json.dumps(report, ensure_ascii=False, indent=2).encode("utf-8"))
    return {"report": str(report_path), **report}


def verify(report_path: Path) -> dict:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    require(report.get("schema") == SCHEMA, "candidate report schema differs")
    base_path = Path(report["base"]["path"])
    candidate_path = Path(report["candidate"]["path"])
    require(
        file_spec(base_path) == {"size": report["base"]["size"], "sha256": report["base"]["sha256"]},
        "baseline spec drifted",
    )
    require(file_spec(candidate_path) == {"size": report["candidate"]["size"], "sha256": report["candidate"]["sha256"]}, "candidate spec drifted")
    base_outer = lz4.parse_link(base_path.read_bytes())
    candidate_outer = lz4.parse_link(candidate_path.read_bytes())
    changed_outers = [i for i in range(len(base_outer.entries)) if base_outer.entries[i].data != candidate_outer.entries[i].data]
    require(changed_outers == [0], "verified outer scope differs")
    base_inner = codec.parse_inner_link32(base_outer.entries[0].data)
    candidate_inner = codec.parse_inner_link32(candidate_outer.entries[0].data)
    changed_titles = [i for i in range(TITLE_COUNT) if base_inner.entries[i].data != candidate_inner.entries[i].data]
    require(changed_titles == list(range(TITLE_COUNT)), "verified title scope differs")
    return {"verified": True, "changed_outers": changed_outers, "changed_title_slots": changed_titles, "candidate": file_spec(candidate_path)}


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)
    build_parser = sub.add_parser("build")
    build_parser.add_argument("--base", type=Path, required=True)
    build_parser.add_argument("--render-root", type=Path, required=True)
    build_parser.add_argument("--output-root", type=Path, required=True)
    build_parser.add_argument("--texconv", type=Path, required=True)
    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("--report", type=Path, required=True)
    return root


def main() -> None:
    args = parser().parse_args()
    if args.command == "build":
        result = build(args.base, args.render_root, args.output_root, args.texconv)
        printable = {
            "report": result["report"],
            "candidate": result["candidate"],
            "changed_outer_entries": result["scope"]["changed_outer_entries"],
            "changed_title_count": len(result["scope"]["changed_title_slots"]),
        }
    else:
        result = verify(args.report.resolve())
        printable = {
            "verified": result["verified"],
            "changed_outers": result["changed_outers"],
            "changed_title_count": len(result["changed_title_slots"]),
            "candidate": result["candidate"],
        }
    print(json.dumps(printable, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
