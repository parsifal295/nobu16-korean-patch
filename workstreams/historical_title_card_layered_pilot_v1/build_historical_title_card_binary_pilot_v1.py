#!/usr/bin/env python3
"""Integrate the six approved prototype PNGs into two Steam-JP LINK archives.

The builder is fail-closed and writes candidates only below the repository
``tmp`` directory.  It replaces inner slots 0..2 of the two historical-title
routes and proves that every unrelated outer and inner entry is byte exact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parent.parent
WORKSPACE = REPO.parent.parent
TOOLS = REPO / "tools"
PIL_RUNTIME = (
    WORKSPACE
    / "repository"
    / "KR_PATCH_WORK"
    / "tmp"
    / "toolchain"
    / "atlas_dashboard_runtime"
)
for import_root in (PIL_RUNTIME, TOOLS):
    if import_root.is_dir() and str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from PIL import Image  # noqa: E402

import extract_nobu16_image_atlases as atlas_codec  # noqa: E402
import nobu16_lz4 as lz4  # noqa: E402
import pc_g1t_title_codec as title_codec  # noqa: E402


SCHEMA = "nobu16.kr.historical-title-card-binary-pilot.v1"
DEFAULT_PINS = WORKSTREAM / "input_pins.v1.json"
DEFAULT_TARGET = (
    WORKSPACE
    / "scratch"
    / "release-v0940-approve-all-layered-20260820-01"
    / "generator-output-03"
    / "target"
)
ROUTES = (
    {
        "id": "base_low",
        "pin": "jp_low",
        "relative_path": "RES_JP/res_lang.bin",
        "outer_entry": 4,
        "dimensions": (1024, 256),
    },
    {
        "id": "port3_high",
        "pin": "jp_high",
        "relative_path": "RES_JP_PK_PORT/res_lang_pk_port3.bin",
        "outer_entry": 2,
        "dimensions": (2048, 512),
    },
)
STATE_NAMES = ("normal_gold", "highlight_white_gold", "burst_zoom")


class BinaryPilotError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BinaryPilotError(message)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def file_spec(path: Path) -> dict[str, Any]:
    return {"path": str(path.resolve()), "size": path.stat().st_size, "sha256": sha256_file(path)}


def validate_file(path: Path, expected: Mapping[str, Any], label: str) -> dict[str, Any]:
    require(path.is_file(), f"{label} is missing: {path}")
    actual = file_spec(path)
    require(
        actual["size"] == int(expected["size"])
        and actual["sha256"] == str(expected["sha256"]).upper(),
        f"{label} pin differs: expected={dict(expected)} actual={actual}",
    )
    return actual


def ensure_output_root(raw: str | Path, *, fresh: bool) -> Path:
    root = Path(raw).resolve()
    tmp = (REPO / "tmp").resolve()
    try:
        root.relative_to(tmp)
    except ValueError as exc:
        raise BinaryPilotError(f"output root must remain below {tmp}") from exc
    require(root != tmp, "output root may not be the tmp root itself")
    if fresh:
        require(not root.exists() or not any(root.iterdir()), f"output root is not empty: {root}")
        root.mkdir(parents=True, exist_ok=True)
    else:
        require(root.is_dir(), f"output root is missing: {root}")
    return root


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_png(path: Path, dimensions: tuple[int, int]) -> bytes:
    require(path.is_file(), f"prototype PNG is missing: {path}")
    with Image.open(path) as image:
        require(image.size == dimensions, f"prototype PNG dimensions differ: {path} {image.size}")
        rgba = image.convert("RGBA").tobytes()
    require(len(rgba) == dimensions[0] * dimensions[1] * 4, f"prototype RGBA length differs: {path}")
    return rgba


def canonicalize_hidden_rgb(candidate: bytes, template: bytes) -> bytes:
    require(len(candidate) == len(template) and len(candidate) % 4 == 0, "RGBA buffers differ")
    output = bytearray(candidate)
    for offset in range(0, len(output), 4):
        if output[offset + 3] == 0 and template[offset + 3] == 0:
            output[offset : offset + 3] = template[offset : offset + 3]
    return bytes(output)


def rebuild_slot(wrapper: bytes, requested_rgba: bytes, dimensions: tuple[int, int]) -> tuple[bytes, dict[str, Any]]:
    wrapper_header, raw = lz4.decompress_wrapper(wrapper)
    g1t = atlas_codec.parse_g1t(raw)
    require(len(g1t.textures) == 1, "historical-title G1T is not single-texture")
    texture = g1t.textures[0]
    require(
        (texture.width, texture.height) == dimensions,
        f"historical-title G1T dimensions differ: {(texture.width, texture.height)}",
    )
    require(texture.format_code == 0x5B and texture.mip_count == 1, "historical-title texture is not one-mip BC3")
    template_rgba = title_codec.decode_bc3(texture.payload, texture.width, texture.height)
    canonical_rgba = canonicalize_hidden_rgb(requested_rgba, template_rgba)
    bc3, preserved, encoded = title_codec.encode_bc3(
        canonical_rgba,
        texture.width,
        texture.height,
        template_bc3=texture.payload,
    )
    payload_end = texture.payload_offset + len(texture.payload)
    rebuilt_raw = raw[: texture.payload_offset] + bc3 + raw[payload_end:]
    reparsed = atlas_codec.parse_g1t(rebuilt_raw)
    require(reparsed.textures[0].payload == bc3, "rebuilt G1T did not re-extract the BC3 payload")
    rebuilt_wrapper = (
        wrapper
        if rebuilt_raw == raw
        else lz4.recompress_wrapper(rebuilt_raw, wrapper_header)
    )
    _, roundtrip_raw = lz4.decompress_wrapper(rebuilt_wrapper)
    require(roundtrip_raw == rebuilt_raw, "rebuilt wrapper failed LZ4 round trip")
    decoded = title_codec.decode_bc3(bc3, texture.width, texture.height)
    metrics = title_codec.rgba_error_metrics(canonical_rgba, decoded)
    return rebuilt_wrapper, {
        "dimensions": list(dimensions),
        "total_blocks": len(texture.payload) // 16,
        "preserved_template_blocks": preserved,
        "deterministically_encoded_blocks": encoded,
        "changed_blocks": sum(
            1
            for offset in range(0, len(bc3), 16)
            if bc3[offset : offset + 16] != texture.payload[offset : offset + 16]
        ),
        "requested_rgba_sha256": sha256_bytes(requested_rgba),
        "canonical_rgba_sha256": sha256_bytes(canonical_rgba),
        "bc3_sha256": sha256_bytes(bc3),
        "g1t_sha256": sha256_bytes(rebuilt_raw),
        "wrapper_sha256": sha256_bytes(rebuilt_wrapper),
        "decoded_error": metrics,
    }


def build_route(
    route: Mapping[str, Any],
    baseline_root: Path,
    prototype_root: Path,
    output_root: Path,
    pins: Mapping[str, Any],
) -> dict[str, Any]:
    relative = Path(str(route["relative_path"]))
    source_path = baseline_root / relative
    source_spec = validate_file(source_path, pins["files"][route["pin"]], f"{route['id']} source")
    source_blob = source_path.read_bytes()
    outer = lz4.parse_link(source_blob)
    require(lz4.rebuild_link(outer) == source_blob, f"{route['id']} outer LINK identity failed")
    outer_index = int(route["outer_entry"])
    require(outer_index < len(outer.entries), f"{route['id']} outer entry is missing")
    original_inner_blob = outer.entries[outer_index].data
    inner = title_codec.parse_inner_link32(original_inner_blob)
    require(len(inner.entries) == 105, f"{route['id']} inner entry count differs: {len(inner.entries)}")

    replacements: dict[int, bytes] = {}
    state_rows: list[dict[str, Any]] = []
    for state, name in enumerate(STATE_NAMES):
        png = prototype_root / "candidate" / str(route["id"]) / f"state_{state}_{name}.png"
        requested = load_png(png, tuple(route["dimensions"]))
        rebuilt, metrics = rebuild_slot(inner.entries[state].data, requested, tuple(route["dimensions"]))
        replacements[state] = rebuilt
        state_rows.append(
            {
                "slot": state,
                "state": name,
                "png": file_spec(png),
                **metrics,
            }
        )

    rebuilt_inner_blob = title_codec.rebuild_inner_link32(inner, replacements)
    rebuilt_inner = title_codec.parse_inner_link32(rebuilt_inner_blob)
    changed_inner = []
    for index, (before, after) in enumerate(zip(inner.entries, rebuilt_inner.entries)):
        if before.data != after.data:
            changed_inner.append(index)
        if index not in replacements:
            require(before.data == after.data, f"{route['id']} unrelated inner slot changed: {index}")
    require(changed_inner == [0, 1, 2], f"{route['id']} changed inner slots differ: {changed_inner}")

    candidate_blob = lz4.rebuild_link(outer, {outer_index: rebuilt_inner_blob})
    candidate_outer = lz4.parse_link(candidate_blob)
    require(candidate_outer.entries[outer_index].data == rebuilt_inner_blob, f"{route['id']} outer replacement failed")
    changed_outer = []
    for index, (before, after) in enumerate(zip(outer.entries, candidate_outer.entries)):
        if before.data != after.data:
            changed_outer.append(index)
        if index != outer_index:
            require(before.data == after.data, f"{route['id']} unrelated outer entry changed: {index}")
    require(changed_outer == [outer_index], f"{route['id']} changed outer entries differ: {changed_outer}")

    candidate_path = output_root / "candidate" / relative
    candidate_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_path.write_bytes(candidate_blob)
    require(candidate_path.read_bytes() == candidate_blob, f"{route['id']} candidate write verification failed")
    require(sha256_file(source_path) == source_spec["sha256"], f"{route['id']} source changed during build")
    return {
        "route_id": route["id"],
        "relative_path": relative.as_posix(),
        "outer_entry": outer_index,
        "source": source_spec,
        "candidate": file_spec(candidate_path),
        "changed_outer_entries": changed_outer,
        "changed_inner_slots": changed_inner,
        "unchanged_outer_entries": len(outer.entries) - 1,
        "unchanged_inner_slots": len(inner.entries) - 3,
        "states": state_rows,
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    output_root = ensure_output_root(args.output_root, fresh=True)
    baseline_root = Path(args.baseline_root).resolve()
    prototype_root = Path(args.prototype_root).resolve()
    pins_path = Path(args.pins).resolve()
    pins = json.loads(pins_path.read_text(encoding="utf-8"))
    require(pins.get("schema") == "nobu16.kr.historical-title-card-layered-pilot.inputs.v1", "pin schema differs")
    prototype_report_path = prototype_root / "build_report.json"
    require(prototype_report_path.is_file(), f"prototype report is missing: {prototype_report_path}")
    prototype_report = json.loads(prototype_report_path.read_text(encoding="utf-8"))
    require(prototype_report.get("status") == "PASS", "prototype report did not pass")
    require(prototype_report.get("image_generation_used") is False, "prototype used image generation")
    require(prototype_report.get("steam_written") is False, "prototype unexpectedly wrote Steam")

    rows = [build_route(route, baseline_root, prototype_root, output_root, pins) for route in ROUTES]
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "PASS",
        "scope": "two archives, outer historical-title route, inner slots 0..2 only",
        "entry": {"jp": "独眼竜", "ko": "독안룡"},
        "prototype_report": file_spec(prototype_report_path),
        "prototype_output_manifest_sha256": prototype_report["output_manifest_sha256"],
        "input_pins": file_spec(pins_path),
        "routes": rows,
        "candidate_archives": 2,
        "changed_outer_entries": 2,
        "changed_inner_slots": 6,
        "archive_output_written_below_tmp": True,
        "steam_written": False,
    }
    report["candidate_set_sha256"] = sha256_bytes(
        json.dumps(
            [
                {
                    "relative_path": row["relative_path"],
                    "size": row["candidate"]["size"],
                    "sha256": row["candidate"]["sha256"],
                }
                for row in rows
            ],
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )
    write_json(output_root / "build_report.json", report)
    return report


def verify(args: argparse.Namespace) -> dict[str, Any]:
    output_root = ensure_output_root(args.output_root, fresh=False)
    report_path = output_root / "build_report.json"
    require(report_path.is_file(), f"binary build report is missing: {report_path}")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    require(report.get("schema") == SCHEMA and report.get("status") == "PASS", "binary report differs")
    require(report.get("changed_outer_entries") == 2, "changed outer-entry count differs")
    require(report.get("changed_inner_slots") == 6, "changed inner-slot count differs")
    require(report.get("steam_written") is False, "binary builder wrote Steam")
    for route in report["routes"]:
        candidate = output_root / "candidate" / route["relative_path"]
        require(candidate.is_file(), f"candidate is missing: {candidate}")
        require(file_spec(candidate)["size"] == route["candidate"]["size"], f"candidate size differs: {candidate}")
        require(sha256_file(candidate) == route["candidate"]["sha256"], f"candidate hash differs: {candidate}")
        blob = candidate.read_bytes()
        outer = lz4.parse_link(blob)
        inner = title_codec.parse_inner_link32(outer.entries[int(route["outer_entry"])].data)
        require(len(inner.entries) == 105, f"candidate inner count differs: {candidate}")
        for state in route["states"]:
            _, raw = lz4.decompress_wrapper(inner.entries[int(state["slot"])].data)
            texture = atlas_codec.parse_g1t(raw).textures[0]
            require(sha256_bytes(texture.payload) == state["bc3_sha256"], f"candidate BC3 differs: {candidate}")
    return report


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    subparsers = value.add_subparsers(dest="command", required=True)
    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("--baseline-root", default=str(DEFAULT_TARGET))
    build_parser.add_argument("--prototype-root", required=True)
    build_parser.add_argument("--pins", default=str(DEFAULT_PINS))
    build_parser.add_argument("--output-root", required=True)
    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--output-root", required=True)
    return value


def main(argv: Sequence[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parser().parse_args(argv)
    report = build(args) if args.command == "build" else verify(args)
    print("status=PASS")
    print(f"candidate_set_sha256={report['candidate_set_sha256']}")
    for route in report["routes"]:
        print(f"{route['route_id']}={route['candidate']['sha256']}")
    print(f"steam_written={str(report['steam_written']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
