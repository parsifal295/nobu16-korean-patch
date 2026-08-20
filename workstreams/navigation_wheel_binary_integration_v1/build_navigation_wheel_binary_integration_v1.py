#!/usr/bin/env python3
"""Integrate the reviewed B navigation-wheel atlases into v0.94 archives.

The input atlases are the deterministic PNG outputs of
``navigation_wheel_layered_rebuild_v1``.  For each of the four runtime routes,
the builder starts from the current v0.94 target archive, replaces only pixels
inside the catalogued wheel cells, and re-encodes only BC3 blocks whose desired
pixels differ.  Unselected BC3 blocks, G1T textures, nested LINK slots and
outer LINK entries must remain byte-identical.

This builder writes only below the repository ``tmp`` directory.  It never
touches the patcher release tree or a Steam installation.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


WORKSTREAM = Path(__file__).resolve().parent
REPO = WORKSTREAM.parent.parent
WORKSPACE = REPO.parent.parent
TOOLS = REPO / "tools"
CATALOG_WS = REPO / "workstreams" / "navigation_wheel_atlas_catalog_v1"
HIGHRES_WS = REPO / "workstreams" / "steam_jp_port_highres_images_v1"
for import_root in (TOOLS, CATALOG_WS, HIGHRES_WS):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

import extract_nobu16_image_atlases as atlas_codec  # noqa: E402
import nobu16_lz4 as lz4  # noqa: E402
import build_navigation_wheel_atlas_catalog_v1 as catalog  # noqa: E402
import build_steam_jp_port_highres_images_v1 as highres  # noqa: E402

try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover - user-facing dependency gate.
    raise RuntimeError("NumPy and Pillow are required for wheel archive integration") from exc


SCHEMA = "nobu16.kr.navigation-wheel-binary-integration.v1"
STATIC_SCHEMA = "nobu16.kr.navigation-wheel-layered-rebuild.v1"
STATIC_MANIFEST_SHA256 = "12B024C4FAB0D22AF3BB17E59E18543BFBE446C89D5CFB856458C98BBF78D2A4"
GENERATION_POLICY = "forbidden-and-not-used"
ROUTE_ORDER = ("base_low", "base_high", "pk_low", "pk_high")
DEFAULT_STATIC_ROOT = REPO / "tmp" / "navigation_wheel_layered_rebuild_v1" / "run_003"
DEFAULT_TARGET_ROOT = WORKSPACE / "scratch" / "release-v0940-rc-20260819-06" / "resource-input" / "target"
DEFAULT_UI_FONT = REPO / "vendor" / "noto" / "NotoSansKR-wght.ttf"


class IntegrationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise IntegrationError(message)


def sha256_bytes(payload: bytes | bytearray | memoryview) -> str:
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
    require(path.is_file(), f"{label} is not a file: {path}")
    actual = file_spec(path)
    wanted = {"size": int(expected["size"]), "sha256": str(expected["sha256"]).upper()}
    require(
        actual["size"] == wanted["size"] and actual["sha256"] == wanted["sha256"],
        f"{label} pin differs: expected={wanted} actual={actual}",
    )
    return actual


def ensure_tmp(path: Path) -> Path:
    resolved = path.resolve()
    tmp = (REPO / "tmp").resolve()
    try:
        resolved.relative_to(tmp)
    except ValueError as exc:
        raise IntegrationError(f"output must remain below {tmp}: {resolved}") from exc
    return resolved


def fresh_output(path: Path) -> Path:
    resolved = ensure_tmp(path)
    require(not resolved.exists(), f"refusing to replace existing output: {resolved}")
    resolved.mkdir(parents=True)
    return resolved


def atomic_write(path: Path, payload: bytes, *, forbidden: Iterable[Path] = ()) -> None:
    target = ensure_tmp(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    forbidden_resolved = {item.resolve() for item in forbidden}
    require(target not in forbidden_resolved, f"refusing to overwrite input: {target}")
    temporary = target.with_name(f".{target.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("xb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()


def canonical_rgba(values: "np.ndarray[Any, Any]") -> "np.ndarray[Any, Any]":
    rgba = values.astype(np.uint16)
    alpha = rgba[..., 3:4]
    premultiplied = (rgba[..., :3] * alpha + 127) // 255
    return np.concatenate((premultiplied, alpha), axis=-1)


def block_mask_from_pixels(pixel_mask: "np.ndarray[Any, Any]") -> "np.ndarray[Any, Any]":
    height, width = pixel_mask.shape
    require(width % 4 == 0 and height % 4 == 0, f"BC3 canvas is not block aligned: {width}x{height}")
    return pixel_mask.reshape(height // 4, 4, width // 4, 4).any(axis=(1, 3))


def blocks_from_mask(block_mask: "np.ndarray[Any, Any]") -> set[tuple[int, int]]:
    ys, xs = np.nonzero(block_mask)
    return {(int(x), int(y)) for y, x in zip(ys.tolist(), xs.tolist())}


def expanded_block_pixels(block_mask: "np.ndarray[Any, Any]") -> "np.ndarray[Any, Any]":
    return np.repeat(np.repeat(block_mask, 4, axis=0), 4, axis=1)


def load_static_manifest(static_root: Path) -> tuple[dict[str, Any], dict[str, Path]]:
    root = static_root.resolve(strict=True)
    manifest_path = root / "manifest.v1.json"
    require(manifest_path.is_file(), f"static manifest is missing: {manifest_path}")
    require(sha256_file(manifest_path) == STATIC_MANIFEST_SHA256, "static B manifest pin differs")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    require(manifest.get("schema") == STATIC_SCHEMA, "static manifest schema differs")
    require(manifest.get("generation_policy") == GENERATION_POLICY, "static generation policy differs")
    coverage = manifest.get("coverage", {})
    require(
        (coverage.get("routes"), coverage.get("groups"), coverage.get("placements"), coverage.get("unique_assets"))
        == (4, 150, 900, 64),
        f"static wheel coverage differs: {coverage}",
    )
    validation = manifest.get("validation", {})
    require(validation.get("clean_residual_core_pixels") == 0, "static Japanese-core residual gate failed")
    require(validation.get("full_component_geometry_outliers_5pct") == 0, "static geometry gate failed")
    require(validation.get("nontext_direction_marker_groups_preserved") == 16, "static marker coverage differs")
    require(validation.get("nontext_direction_marker_canonical_rgba_differences") == 0, "static marker preservation differs")
    previews: dict[str, Path] = {}
    for route_id in ROUTE_ORDER:
        relative = str(manifest["routes"][route_id]["atlas_preview"])
        path = root / Path(relative)
        expected = manifest["artifacts"].get(relative)
        require(expected is not None, f"static atlas artifact row is missing: {route_id}")
        validate_file(path, expected, f"static {route_id} atlas")
        previews[route_id] = path
    return manifest, previews


def wheel_mask_and_rows(
    route_manifest: Mapping[str, Any],
    width: int,
    height: int,
) -> tuple["np.ndarray[Any, Any]", list[dict[str, Any]]]:
    mask = np.zeros((height, width), dtype=bool)
    rows: list[dict[str, Any]] = []
    for family, report in route_manifest["families"].items():
        for row in report["rows"]:
            states: list[dict[str, Any]] = []
            for state in row["states"]:
                left, top, right, bottom = (int(value) for value in state["atlas_rect"])
                require(0 <= left < right <= width and 0 <= top < bottom <= height, f"wheel cell escapes atlas: {family}:{row['group']}")
                mask[top:bottom, left:right] = True
                states.append({"state": int(state["state"]), "rect": [left, top, right, bottom]})
            require(len(states) == 6, f"wheel state coverage differs: {family}:{row['group']}")
            rows.append({
                "family": family,
                "group": int(row["group"]),
                "name": str(row["name"]),
                "ko": str(row["ko"]),
                "states": states,
            })
    return mask, rows


def metric(values: "np.ndarray[Any, Any]") -> dict[str, Any]:
    require(values.size > 0, "metric input is empty")
    return {
        "mean": round(float(values.mean()), 6),
        "p95": round(float(np.percentile(values, 95)), 6),
        "maximum": int(values.max()),
    }


def contact_sheet_pages(
    output: Path,
    route_id: str,
    rows: list[dict[str, Any]],
    desired: "np.ndarray[Any, Any]",
    decoded: "np.ndarray[Any, Any]",
    ui_font: Path,
) -> list[Path]:
    files: list[Path] = []
    title_font = ImageFont.truetype(str(ui_font), 14)
    try:
        title_font.set_variation_by_axes([600])
    except (AttributeError, OSError):
        pass
    for family in dict.fromkeys(row["family"] for row in rows):
        family_rows = [row for row in rows if row["family"] == family]
        for page, start in enumerate(range(0, len(family_rows), 20), 1):
            selected = family_rows[start : start + 20]
            cell_width, cell_height, gap, left = 200, 190, 10, 180
            columns = ((0, "원하는 상태1"), (0, "BC3 상태1"), (1, "원하는 상태2"), (1, "BC3 상태2"), (3, "원하는 상태4"), (3, "BC3 상태4"))
            canvas = Image.new("RGB", (left + len(columns) * (cell_width + gap) + gap, 42 + len(selected) * (cell_height + gap) + 38), (25, 27, 31))
            draw = ImageDraw.Draw(canvas)
            for column, (_state, label) in enumerate(columns):
                draw.text((left + column * (cell_width + gap) + 42, 10), label, font=title_font, fill=(235, 236, 238))
            for row_index, row in enumerate(selected):
                y = 42 + row_index * (cell_height + gap)
                draw.text((8, y + 72), f"{row['group']:02d} {row['name']}\n{row['ko']}", font=title_font, fill=(224, 227, 231), spacing=2)
                for column, (state_index, _label) in enumerate(columns):
                    rect = row["states"][state_index]["rect"]
                    left_x, top_y, right_x, bottom_y = rect
                    matrix = desired if column % 2 == 0 else decoded
                    image = Image.fromarray(matrix[top_y:bottom_y, left_x:right_x])
                    background = Image.new("RGB", image.size, (0, 255, 0))
                    background.paste(image, (0, 0), image)
                    image = background.resize((cell_width, cell_height), Image.Resampling.LANCZOS)
                    canvas.paste(image, (left + column * (cell_width + gap), y))
            draw.text((8, canvas.height - 28), f"{route_id} / {family} / groups {start}..{start + len(selected) - 1}", font=title_font, fill=(168, 175, 186))
            path = output / "contact" / f"{route_id}_{family}_{page:02d}.png"
            path.parent.mkdir(parents=True, exist_ok=True)
            canvas.save(path, optimize=False, compress_level=9)
            files.append(path)
    return files


def rebuild_nested_with_raw(
    nested: highres.NestedLink,
    slot: int,
    header: lz4.WrapperHeader,
    raw: bytes,
) -> bytes:
    wrapper = lz4.recompress_wrapper_greedy(raw, header)
    _header, roundtrip = lz4.decompress_wrapper(wrapper)
    require(roundtrip == raw, "G1T wrapper roundtrip failed")
    rebuilt = highres.rebuild_nested_link(nested, {slot: wrapper})
    reparsed = highres.parse_nested_link(rebuilt, expected_resource_id=nested.resource_id)
    require(reparsed.table_padding == nested.table_padding, "nested table padding changed")
    for entry in nested.entries:
        if entry.index != slot:
            require(
                reparsed.entries[entry.index].data == entry.data
                and reparsed.entries[entry.index].gap_after == entry.gap_after,
                f"unrelated nested entry {entry.index} changed",
            )
    return rebuilt


def integrate_route(
    *,
    output: Path,
    route: Mapping[str, Any],
    target_path: Path,
    static_preview: Path,
    static_route: Mapping[str, Any],
    ui_font: Path,
) -> tuple[dict[str, Any], list[Path]]:
    route_id = str(route["id"])
    target_spec = validate_file(target_path, route["target"], f"{route_id} v0.94 target")
    target_blob = target_path.read_bytes()
    outer = lz4.parse_link(target_blob)
    require(lz4.rebuild_link(outer) == target_blob, f"{route_id} outer LINK identity failed")
    outer_index = int(route["outer_entry"])
    nested = highres.parse_nested_link(outer.entries[outer_index].data, expected_resource_id=int(route["resource_id"]))
    slot, header, raw, g1t = highres.g1t_wrapper_entry(nested)
    require(slot == 0, f"{route_id} nested G1T slot differs: {slot}")
    texture_index = int(route["texture_index"])
    texture = g1t.textures[texture_index]
    expected_dimensions = (2048, 2048) if route_id == "base_low" else (4096, 4096) if route_id == "base_high" else (1024, 1024) if route_id == "pk_low" else (2048, 2048)
    require((texture.width, texture.height, texture.format_code) == (*expected_dimensions, 0x5B), f"{route_id} texture contract differs")

    target_decoded_bytes = atlas_codec.decode_texture(texture)
    require(target_decoded_bytes is not None, f"{route_id} target BC3 decode failed")
    target_rgba = np.frombuffer(target_decoded_bytes, dtype=np.uint8).reshape(texture.height, texture.width, 4).copy()
    with Image.open(static_preview) as image:
        desired_rgba = np.asarray(image.convert("RGBA"), dtype=np.uint8).copy()
    require(desired_rgba.shape == target_rgba.shape, f"{route_id} desired atlas dimensions differ")

    wheel_mask, rows = wheel_mask_and_rows(static_route, texture.width, texture.height)
    expected_placements = 372 if route["edition"] == "base" else 78
    require(sum(len(row["states"]) for row in rows) == expected_placements, f"{route_id} placement coverage differs")
    requested = target_rgba.copy()
    requested[wheel_mask] = desired_rgba[wheel_mask]
    pixel_delta = wheel_mask & np.any(canonical_rgba(requested) != canonical_rgba(target_rgba), axis=-1)
    require(bool(np.any(pixel_delta)), f"{route_id} has no requested wheel delta")
    selected_block_mask = block_mask_from_pixels(pixel_delta)
    allowed = blocks_from_mask(selected_block_mask)
    payload, encoded_calls = highres.encode_selected_blocks(
        requested.tobytes(), texture.width, texture.height, texture.payload, allowed
    )
    old_blocks = np.frombuffer(texture.payload, dtype=np.uint8).reshape(-1, 16)
    new_blocks = np.frombuffer(payload, dtype=np.uint8).reshape(-1, 16)
    byte_changed_blocks = np.any(old_blocks != new_blocks, axis=1)
    changed_indices = np.nonzero(byte_changed_blocks)[0]
    blocks_wide = texture.width // 4
    changed = {(int(index % blocks_wide), int(index // blocks_wide)) for index in changed_indices.tolist()}
    require(changed and changed <= allowed, f"{route_id} BC3 changes escaped selected blocks")

    candidate_texture = atlas_codec.Texture(
        texture.index,
        texture.format_code,
        texture.width,
        texture.height,
        texture.mip_count,
        texture.extra_version,
        texture.payload_offset,
        payload,
    )
    decoded_bytes = atlas_codec.decode_texture(candidate_texture)
    require(decoded_bytes is not None, f"{route_id} candidate BC3 decode failed")
    decoded_rgba = np.frombuffer(decoded_bytes, dtype=np.uint8).reshape(texture.height, texture.width, 4).copy()
    target_canonical = canonical_rgba(target_rgba).astype(np.int16)
    desired_canonical = canonical_rgba(desired_rgba).astype(np.int16)
    decoded_canonical = canonical_rgba(decoded_rgba).astype(np.int16)
    before_error = np.abs(target_canonical - desired_canonical).mean(axis=-1)
    after_error = np.abs(decoded_canonical - desired_canonical).mean(axis=-1)
    require(float(after_error[wheel_mask].mean()) < float(before_error[wheel_mask].mean()), f"{route_id} candidate did not improve wheel fidelity")
    block_pixels = expanded_block_pixels(selected_block_mask)
    outside_blocks = ~block_pixels
    require(bool(np.array_equal(decoded_rgba[outside_blocks], target_rgba[outside_blocks])), f"{route_id} decoded pixels outside selected blocks changed")
    boundary = block_pixels & ~wheel_mask
    boundary_changes = np.any(canonical_rgba(decoded_rgba) != canonical_rgba(target_rgba), axis=-1) & boundary

    rebuilt_raw = highres.replace_g1t_payloads(raw, g1t, {texture_index: payload})
    start = texture.payload_offset
    end = start + len(texture.payload)
    require(rebuilt_raw[:start] == raw[:start] and rebuilt_raw[end:] == raw[end:], f"{route_id} G1T bytes outside wheel texture changed")
    rebuilt_nested = rebuild_nested_with_raw(nested, slot, header, rebuilt_raw)
    candidate_blob = lz4.rebuild_link(outer, {outer_index: rebuilt_nested})
    candidate_outer = lz4.parse_link(candidate_blob)
    require(lz4.rebuild_link(candidate_outer) == candidate_blob, f"{route_id} candidate outer LINK identity failed")
    changed_outer = [entry.index for entry in outer.entries if entry.data != candidate_outer.entries[entry.index].data]
    require(changed_outer == [outer_index], f"{route_id} changed outer scope differs: {changed_outer}")
    for entry in outer.entries:
        if entry.index != outer_index:
            candidate_entry = candidate_outer.entries[entry.index]
            require(entry.data == candidate_entry.data and entry.gap_after == candidate_entry.gap_after, f"{route_id} unrelated outer entry {entry.index} changed")

    destination = output / "candidate" / Path(str(route["relative_path"]))
    atomic_write(destination, candidate_blob, forbidden=(target_path,))
    contacts = contact_sheet_pages(output, route_id, rows, desired_rgba, decoded_rgba, ui_font)
    candidate_spec = file_spec(destination)
    candidate_spec["path"] = str(destination.relative_to(output)).replace("\\", "/")
    report = {
        "route": route_id,
        "archive": str(route["relative_path"]),
        "input": target_spec,
        "candidate": candidate_spec,
        "outer_entry": outer_index,
        "changed_outer_entries": changed_outer,
        "resource_id": int(route["resource_id"]),
        "nested_slot": slot,
        "texture_index": texture_index,
        "format": "BC3/0x5B",
        "dimensions": [texture.width, texture.height],
        "groups": len(rows),
        "placements": sum(len(row["states"]) for row in rows),
        "wheel_mask_pixels": int(np.count_nonzero(wheel_mask)),
        "requested_delta_pixels": int(np.count_nonzero(pixel_delta)),
        "allowed_bc3_blocks": len(allowed),
        "encoder_calls": encoded_calls,
        "changed_bc3_blocks": len(changed),
        "changed_block_bbox": highres.changed_block_bbox(sorted(changed)),
        "unselected_bc3_blocks_byte_preserved": True,
        "decoded_pixels_outside_selected_blocks_preserved": True,
        "unselected_g1t_bytes_preserved": True,
        "unselected_nested_entries_byte_preserved": True,
        "unselected_outer_entries_byte_preserved": True,
        "wheel_fidelity_before_bc3": metric(before_error[wheel_mask]),
        "wheel_fidelity_after_bc3": metric(after_error[wheel_mask]),
        "boundary_pixels_outside_wheel_inside_selected_blocks": int(np.count_nonzero(boundary)),
        "boundary_pixels_changed_by_reencoding": int(np.count_nonzero(boundary_changes)),
        "contact_sheets": [str(path.relative_to(output)).replace("\\", "/") for path in contacts],
    }
    del target_blob, outer, nested, raw, g1t, target_rgba, desired_rgba, requested
    del target_canonical, desired_canonical, decoded_canonical, decoded_rgba
    gc.collect()
    return report, [destination, *contacts]


def build(args: argparse.Namespace) -> dict[str, Any]:
    output = fresh_output(args.output_root)
    target_root = args.target_root.resolve(strict=True)
    ui_font = args.ui_font.resolve(strict=True)
    static_manifest, previews = load_static_manifest(args.static_root)
    routes = {str(route["id"]): route for route in catalog.ROUTES}
    require(tuple(routes) == ROUTE_ORDER, f"catalog route order differs: {tuple(routes)}")
    route_reports: dict[str, Any] = {}
    artifacts: list[Path] = []
    for route_id in ROUTE_ORDER:
        print(f"stage={route_id}", flush=True)
        route = routes[route_id]
        report, files = integrate_route(
            output=output,
            route=route,
            target_path=target_root / Path(str(route["relative_path"])),
            static_preview=previews[route_id],
            static_route=static_manifest["routes"][route_id],
            ui_font=ui_font,
        )
        route_reports[route_id] = report
        artifacts.extend(files)
    require(sum(int(report["placements"]) for report in route_reports.values()) == 900, "binary placement coverage differs")
    artifact_table = {
        str(path.relative_to(output)).replace("\\", "/"): {"size": path.stat().st_size, "sha256": sha256_file(path)}
        for path in sorted(artifacts)
    }
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "generation_policy": GENERATION_POLICY,
        "static_manifest": {
            "path": str((args.static_root / "manifest.v1.json").resolve()),
            "sha256": STATIC_MANIFEST_SHA256,
        },
        "coverage": {
            "routes": 4,
            "groups": 150,
            "placements": 900,
            "candidate_archives": 4,
            "contact_sheets": sum(len(value["contact_sheets"]) for value in route_reports.values()),
        },
        "routes": route_reports,
        "artifacts": artifact_table,
        "safety": {
            "archive_outputs_below_repo_tmp": True,
            "patcher_writes": 0,
            "steam_writes": 0,
            "executable_modified": False,
            "generation_used": False,
        },
    }
    canonical = (json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    report["report_sha256"] = sha256_bytes(canonical)
    report_path = output / "verification.v1.json"
    atomic_write(report_path, (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return {
        "output": str(output),
        "report": str(report_path),
        "report_sha256": report["report_sha256"],
        "candidate_archives": 4,
        "placements": 900,
        "changed_bc3_blocks": sum(int(value["changed_bc3_blocks"]) for value in route_reports.values()),
        "steam_writes": 0,
    }


def verify(args: argparse.Namespace) -> dict[str, Any]:
    root = args.candidate_root.resolve(strict=True)
    report_path = root / "verification.v1.json"
    require(report_path.is_file(), f"verification report is missing: {report_path}")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    require(report.get("schema") == SCHEMA, "verification schema differs")
    require(report.get("generation_policy") == GENERATION_POLICY, "verification generation policy differs")
    require(report["coverage"] == {"routes": 4, "groups": 150, "placements": 900, "candidate_archives": 4, "contact_sheets": 12}, f"verification coverage differs: {report['coverage']}")
    for route in catalog.ROUTES:
        route_id = str(route["id"])
        candidate = root / "candidate" / Path(str(route["relative_path"]))
        expected = report["routes"][route_id]["candidate"]
        validate_file(candidate, expected, f"{route_id} candidate")
        blob = candidate.read_bytes()
        parsed = lz4.parse_link(blob)
        require(lz4.rebuild_link(parsed) == blob, f"{route_id} candidate LINK identity failed")
        require(report["routes"][route_id]["unselected_bc3_blocks_byte_preserved"] is True, f"{route_id} BC3 preservation proof missing")
    return {
        "status": "PASS",
        "report_sha256": report["report_sha256"],
        "candidate_archives": 4,
        "placements": 900,
        "steam_writes": 0,
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    build_parser = commands.add_parser("build")
    build_parser.add_argument("--static-root", type=Path, default=DEFAULT_STATIC_ROOT)
    build_parser.add_argument("--target-root", type=Path, default=DEFAULT_TARGET_ROOT)
    build_parser.add_argument("--ui-font", type=Path, default=DEFAULT_UI_FONT)
    build_parser.add_argument("--output-root", type=Path, required=True)
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--candidate-root", type=Path, required=True)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    result = build(args) if args.command == "build" else verify(args)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (IntegrationError, lz4.LZ4Error, atlas_codec.AtlasError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
