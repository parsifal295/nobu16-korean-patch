#!/usr/bin/env python3
"""Integrate the approved ordinary-button atlases into two v0.94 archives.

Only BC3 blocks intersecting actual standard-button pixel deltas are encoded.
Every other BC3 block, G1T texture, nested LINK slot and outer LINK entry must
remain byte-identical.  Outputs are staged below ``tmp`` only.
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
CATALOG_WS = REPO / "workstreams" / "ordinary_button_atlas_catalog_v1"
HIGHRES_WS = REPO / "workstreams" / "steam_jp_port_highres_images_v1"
NAV_INTEGRATION_WS = REPO / "workstreams" / "navigation_wheel_binary_integration_v1"
for candidate in (TOOLS, CATALOG_WS, HIGHRES_WS, NAV_INTEGRATION_WS):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import build_navigation_wheel_binary_integration_v1 as nav_integration  # noqa: E402
import build_ordinary_button_atlas_catalog_v1 as atlas_catalog  # noqa: E402
import build_steam_jp_port_highres_images_v1 as highres  # noqa: E402
import extract_nobu16_image_atlases as atlas_codec  # noqa: E402
import nobu16_lz4 as lz4  # noqa: E402

try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover - workspace runtime invariant.
    raise RuntimeError("NumPy and Pillow are required") from exc


SCHEMA = "nobu16.kr.ordinary-button-binary-integration.v1"
STATIC_SCHEMA = "nobu16.kr.ordinary-button-layered-rebuild.v1"
STATIC_MANIFEST_SHA256 = "51D2C7D8CFC04161830464CEBA3BBB607982CA119076180641C7107C1B0684EF"
GENERATION_POLICY = "forbidden-and-not-used"
ROUTE_ORDER = ("common_low", "common_high_standard")
DEFAULT_CATALOG = CATALOG_WS / "ordinary_button_catalog_v1.json"
DEFAULT_STATIC_ROOT = REPO / "tmp" / "ordinary_button_layered_rebuild_v1" / "run_003"
DEFAULT_TARGET_ROOT = WORKSPACE / "scratch" / "release-v0940-wheel-b-20260819-01" / "resource-input" / "target"
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
    require(actual["size"] == int(expected["size"]) and actual["sha256"] == str(expected["sha256"]).upper(), f"{label} pin differs: expected={dict(expected)} actual={actual}")
    return actual


def ensure_tmp(path: Path) -> Path:
    value = path.resolve()
    tmp = (REPO / "tmp").resolve()
    try:
        value.relative_to(tmp)
    except ValueError as exc:
        raise IntegrationError(f"output must stay below {tmp}: {value}") from exc
    return value


def fresh_output(path: Path) -> Path:
    value = ensure_tmp(path)
    require(not value.exists(), f"refusing to replace existing output: {value}")
    value.mkdir(parents=True)
    return value


def atomic_write(path: Path, payload: bytes, *, forbidden: Iterable[Path] = ()) -> None:
    target = ensure_tmp(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    require(target not in {item.resolve() for item in forbidden}, f"refusing to overwrite input: {target}")
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
    return np.concatenate(((rgba[..., :3] * alpha + 127) // 255, alpha), axis=-1)


def block_mask_from_pixels(mask: "np.ndarray[Any, Any]") -> "np.ndarray[Any, Any]":
    height, width = mask.shape
    require(width % 4 == 0 and height % 4 == 0, f"BC3 atlas is not block-aligned: {width}x{height}")
    return mask.reshape(height // 4, 4, width // 4, 4).any(axis=(1, 3))


def expanded_block_pixels(mask: "np.ndarray[Any, Any]") -> "np.ndarray[Any, Any]":
    return np.repeat(np.repeat(mask, 4, axis=0), 4, axis=1)


def metric(values: "np.ndarray[Any, Any]") -> dict[str, Any]:
    require(values.size > 0, "metric input is empty")
    return {"mean": round(float(values.mean()), 6), "p95": round(float(np.percentile(values, 95)), 6), "maximum": int(values.max())}


def standard_mask_and_groups(catalog: Mapping[str, Any], route_id: str, width: int, height: int) -> tuple["np.ndarray[Any, Any]", list[dict[str, Any]]]:
    rows = [row for row in catalog["placements"] if row["route"] == route_id and row["family"] == "standard"]
    require(len(rows) == 120, f"{route_id} standard placement coverage differs")
    mask = np.zeros((height, width), dtype=bool)
    groups: list[dict[str, Any]] = []
    for group in range(20):
        selected = sorted((row for row in rows if int(row["group"]) == group), key=lambda row: int(row["state"]))
        require([int(row["state"]) for row in selected] == list(range(1, 7)), f"{route_id} group {group} states differ")
        states: list[dict[str, Any]] = []
        for row in selected:
            left, top, right, bottom = (int(value) for value in row["processing_rect"])
            require(0 <= left < right <= width and 0 <= top < bottom <= height, f"{route_id} group {group} escapes atlas")
            require(not bool(np.any(mask[top:bottom, left:right])), f"{route_id} standard cells overlap")
            mask[top:bottom, left:right] = True
            states.append({"state": int(row["state"]), "rect": [left, top, right, bottom]})
        groups.append({"group": group, "name": str(selected[0]["name"]), "ko": str(selected[0]["ko"]), "states": states})
    return mask, groups


def contact_pages(output: Path, route_id: str, groups: list[dict[str, Any]], desired: "np.ndarray[Any, Any]", decoded: "np.ndarray[Any, Any]", ui_font: Path) -> list[Path]:
    files: list[Path] = []
    font = ImageFont.truetype(str(ui_font), 15)
    try:
        font.set_variation_by_axes([650])
    except (AttributeError, OSError):
        pass
    for page, start in enumerate(range(0, len(groups), 10), 1):
        selected = groups[start : start + 10]
        cell_width, cell_height, gap, left, top = 384, 176, 8, 160, 44
        columns = ((0, "원하는 상태1"), (0, "BC3 상태1"), (1, "원하는 상태2"), (1, "BC3 상태2"), (3, "원하는 상태4"), (3, "BC3 상태4"))
        canvas = Image.new("RGB", (left + len(columns) * (cell_width + gap) + gap, top + len(selected) * (cell_height + gap) + 34), (25, 27, 31))
        draw = ImageDraw.Draw(canvas)
        for column, (_state, title) in enumerate(columns):
            draw.text((left + column * (cell_width + gap) + 130, 12), title, font=font, fill=(235, 236, 238))
        for row_index, group in enumerate(selected):
            y = top + row_index * (cell_height + gap)
            draw.text((8, y + 63), f"{group['group']:02d} {group['name']}\n{group['ko']}", font=font, fill=(224, 227, 231), spacing=3)
            for column, (state, _title) in enumerate(columns):
                left_x, top_y, right_x, bottom_y = group["states"][state]["rect"]
                matrix = desired if column % 2 == 0 else decoded
                image = Image.fromarray(matrix[top_y:bottom_y, left_x:right_x])
                background = Image.new("RGB", image.size, (0, 255, 32))
                background.paste(image, (0, 0), image)
                if image.size != (cell_width, cell_height):
                    background = background.resize((cell_width, cell_height), Image.Resampling.NEAREST)
                canvas.paste(background, (left + column * (cell_width + gap), y))
        draw.text((8, canvas.height - 25), f"{route_id} / desired vs block-scoped BC3", font=font, fill=(165, 173, 184))
        path = output / "contact" / f"{route_id}_bc3_{page:02d}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(path, optimize=False, compress_level=9)
        files.append(path)
    return files


def load_static(static_root: Path) -> tuple[dict[str, Any], dict[str, Path]]:
    root = static_root.resolve(strict=True)
    path = root / "manifest.v1.json"
    require(path.is_file(), f"static manifest is missing: {path}")
    require(sha256_file(path) == STATIC_MANIFEST_SHA256, "static manifest pin differs")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    require(manifest.get("schema") == STATIC_SCHEMA, "static manifest schema differs")
    require(manifest.get("generation_policy") == GENERATION_POLICY, "static generation policy differs")
    require(manifest.get("coverage") == {"routes": 2, "groups": 20, "states_per_group": 6, "placements": 240, "atlas_previews": 2}, "static coverage differs")
    require(manifest["validation"]["protected_icon_canonical_rgba_differences"] == 0, "static icon gate failed")
    require(manifest["validation"]["release_all_label"] == "전부해방", "static release-all label differs")
    previews: dict[str, Path] = {}
    for route_id in ROUTE_ORDER:
        relative = str(manifest["routes"][route_id]["atlas_preview"])
        preview = root / Path(relative)
        validate_file(preview, manifest["artifacts"][relative], f"static {route_id} atlas")
        previews[route_id] = preview
    return manifest, previews


def integrate_route(*, output: Path, catalog: Mapping[str, Any], route: Mapping[str, Any], target_path: Path, preview: Path, ui_font: Path) -> tuple[dict[str, Any], list[Path]]:
    route_id = str(route["id"])
    target_spec = validate_file(target_path, route["target"], f"{route_id} v0.94 target")
    target_blob = target_path.read_bytes()
    outer = lz4.parse_link(target_blob)
    require(lz4.rebuild_link(outer) == target_blob, f"{route_id} outer LINK identity failed")
    outer_index = int(route["outer_entry"])
    nested = highres.parse_nested_link(outer.entries[outer_index].data, expected_resource_id=int(route["resource_id"]))
    slot, header, raw, g1t = highres.g1t_wrapper_entry(nested)
    require(slot == int(route["nested_slot"]), f"{route_id} nested slot differs")
    texture_index = int(route["texture_index"])
    texture = g1t.textures[texture_index]
    require((texture.width, texture.height, texture.format_code) == (*route["dimensions"], 0x5B), f"{route_id} texture contract differs")
    target_bytes = atlas_codec.decode_texture(texture)
    require(target_bytes is not None, f"{route_id} target BC3 decode failed")
    target_rgba = np.frombuffer(target_bytes, dtype=np.uint8).reshape(texture.height, texture.width, 4).copy()
    with Image.open(preview) as image:
        desired_rgba = np.asarray(image.convert("RGBA"), dtype=np.uint8).copy()
    require(desired_rgba.shape == target_rgba.shape, f"{route_id} desired dimensions differ")
    standard_mask, groups = standard_mask_and_groups(catalog, route_id, texture.width, texture.height)
    requested = target_rgba.copy()
    requested[standard_mask] = desired_rgba[standard_mask]
    pixel_delta = standard_mask & np.any(canonical_rgba(requested) != canonical_rgba(target_rgba), axis=-1)
    require(bool(np.any(pixel_delta)), f"{route_id} has no ordinary-button delta")
    block_mask = block_mask_from_pixels(pixel_delta)
    ys, xs = np.nonzero(block_mask)
    allowed = {(int(x), int(y)) for y, x in zip(ys.tolist(), xs.tolist())}
    payload, encoder_calls = highres.encode_selected_blocks(requested.tobytes(), texture.width, texture.height, texture.payload, allowed)
    old_blocks = np.frombuffer(texture.payload, dtype=np.uint8).reshape(-1, 16)
    new_blocks = np.frombuffer(payload, dtype=np.uint8).reshape(-1, 16)
    indices = np.nonzero(np.any(old_blocks != new_blocks, axis=1))[0]
    blocks_wide = texture.width // 4
    changed = {(int(index % blocks_wide), int(index // blocks_wide)) for index in indices.tolist()}
    require(changed and changed <= allowed, f"{route_id} BC3 changes escaped selected blocks")

    candidate_texture = atlas_codec.Texture(texture.index, texture.format_code, texture.width, texture.height, texture.mip_count, texture.extra_version, texture.payload_offset, payload)
    decoded_bytes = atlas_codec.decode_texture(candidate_texture)
    require(decoded_bytes is not None, f"{route_id} candidate BC3 decode failed")
    decoded_rgba = np.frombuffer(decoded_bytes, dtype=np.uint8).reshape(texture.height, texture.width, 4).copy()
    target_canonical = canonical_rgba(target_rgba).astype(np.int16)
    desired_canonical = canonical_rgba(desired_rgba).astype(np.int16)
    decoded_canonical = canonical_rgba(decoded_rgba).astype(np.int16)
    before_error = np.abs(target_canonical - desired_canonical).mean(axis=-1)
    after_error = np.abs(decoded_canonical - desired_canonical).mean(axis=-1)
    require(float(after_error[standard_mask].mean()) < float(before_error[standard_mask].mean()), f"{route_id} BC3 did not improve fidelity")
    block_pixels = expanded_block_pixels(block_mask)
    require(bool(np.array_equal(decoded_rgba[~block_pixels], target_rgba[~block_pixels])), f"{route_id} decoded pixels outside selected blocks changed")
    boundary = block_pixels & ~standard_mask
    boundary_changes = boundary & np.any(canonical_rgba(decoded_rgba) != canonical_rgba(target_rgba), axis=-1)

    rebuilt_raw = highres.replace_g1t_payloads(raw, g1t, {texture_index: payload})
    start = texture.payload_offset
    end = start + len(texture.payload)
    require(rebuilt_raw[:start] == raw[:start] and rebuilt_raw[end:] == raw[end:], f"{route_id} G1T bytes outside standard texture changed")
    rebuilt_nested = nav_integration.rebuild_nested_with_raw(nested, slot, header, rebuilt_raw)
    candidate_blob = lz4.rebuild_link(outer, {outer_index: rebuilt_nested})
    candidate_outer = lz4.parse_link(candidate_blob)
    require(lz4.rebuild_link(candidate_outer) == candidate_blob, f"{route_id} candidate LINK identity failed")
    changed_outer = [entry.index for entry in outer.entries if entry.data != candidate_outer.entries[entry.index].data]
    require(changed_outer == [outer_index], f"{route_id} changed outer scope differs: {changed_outer}")
    for entry in outer.entries:
        if entry.index != outer_index:
            candidate_entry = candidate_outer.entries[entry.index]
            require(entry.data == candidate_entry.data and entry.gap_after == candidate_entry.gap_after, f"{route_id} unrelated outer entry changed: {entry.index}")

    destination = output / "candidate" / Path(str(route["archive"]))
    atomic_write(destination, candidate_blob, forbidden=(target_path,))
    contacts = contact_pages(output, route_id, groups, desired_rgba, decoded_rgba, ui_font)
    candidate_spec = file_spec(destination)
    candidate_spec["path"] = str(destination.relative_to(output)).replace("\\", "/")
    report = {
        "route": route_id,
        "archive": str(route["archive"]),
        "input": target_spec,
        "candidate": candidate_spec,
        "outer_entry": outer_index,
        "changed_outer_entries": changed_outer,
        "resource_id": int(route["resource_id"]),
        "nested_slot": slot,
        "texture_index": texture_index,
        "format": "BC3/0x5B",
        "dimensions": [texture.width, texture.height],
        "groups": len(groups),
        "placements": sum(len(group["states"]) for group in groups),
        "standard_mask_pixels": int(np.count_nonzero(standard_mask)),
        "requested_delta_pixels": int(np.count_nonzero(pixel_delta)),
        "allowed_bc3_blocks": len(allowed),
        "encoder_calls": encoder_calls,
        "changed_bc3_blocks": len(changed),
        "changed_block_bbox": highres.changed_block_bbox(sorted(changed)),
        "unselected_bc3_blocks_byte_preserved": True,
        "decoded_pixels_outside_selected_blocks_preserved": True,
        "unselected_g1t_bytes_preserved": True,
        "unselected_nested_entries_byte_preserved": True,
        "unselected_outer_entries_byte_preserved": True,
        "other_textures_in_same_g1t_byte_preserved": True,
        "fidelity_before_bc3": metric(before_error[standard_mask]),
        "fidelity_after_bc3": metric(after_error[standard_mask]),
        "boundary_pixels_outside_standard_cells_inside_selected_blocks": int(np.count_nonzero(boundary)),
        "boundary_pixels_changed_by_reencoding": int(np.count_nonzero(boundary_changes)),
        "contact_sheets": [str(path.relative_to(output)).replace("\\", "/") for path in contacts],
    }
    del target_blob, outer, nested, raw, g1t, target_rgba, desired_rgba, requested, decoded_rgba
    del target_canonical, desired_canonical, decoded_canonical
    gc.collect()
    return report, [destination, *contacts]


def build(args: argparse.Namespace) -> dict[str, Any]:
    output = fresh_output(args.output_root)
    catalog_path = args.catalog.resolve(strict=True)
    target_root = args.target_root.resolve(strict=True)
    ui_font = args.ui_font.resolve(strict=True)
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    require(catalog.get("schema") == atlas_catalog.SCHEMA, "catalog schema differs")
    static_manifest, previews = load_static(args.static_root)
    routes = {route_id: {"id": route_id, **catalog["routes"][route_id]} for route_id in ROUTE_ORDER}
    route_reports: dict[str, Any] = {}
    artifacts: list[Path] = []
    for route_id in ROUTE_ORDER:
        print(f"stage={route_id}", flush=True)
        route = routes[route_id]
        report, files = integrate_route(output=output, catalog=catalog, route=route, target_path=target_root / Path(str(route["archive"])), preview=previews[route_id], ui_font=ui_font)
        route_reports[route_id] = report
        artifacts.extend(files)
    require(sum(int(report["placements"]) for report in route_reports.values()) == 240, "binary placement coverage differs")
    artifact_table = {str(path.relative_to(output)).replace("\\", "/"): {"size": path.stat().st_size, "sha256": sha256_file(path)} for path in sorted(artifacts)}
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "generation_policy": GENERATION_POLICY,
        "static_manifest": {"path": str((args.static_root / "manifest.v1.json").resolve()), "sha256": STATIC_MANIFEST_SHA256},
        "coverage": {"routes": 2, "groups": 40, "placements": 240, "candidate_archives": 2, "contact_sheets": 4},
        "routes": route_reports,
        "artifacts": artifact_table,
        "safety": {"archive_outputs_below_repo_tmp": True, "patcher_writes": 0, "steam_writes": 0, "executable_modified": False, "generation_used": False},
    }
    canonical = (json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    report["report_sha256"] = sha256_bytes(canonical)
    path = output / "verification.v1.json"
    atomic_write(path, (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return {"output": str(output), "report": str(path), "report_sha256": report["report_sha256"], "candidate_archives": 2, "placements": 240, "changed_bc3_blocks": sum(int(value["changed_bc3_blocks"]) for value in route_reports.values()), "steam_writes": 0}


def verify(args: argparse.Namespace) -> dict[str, Any]:
    root = args.root.resolve(strict=True)
    path = root / "verification.v1.json"
    require(path.is_file(), f"verification report is missing: {path}")
    report = json.loads(path.read_text(encoding="utf-8"))
    require(report.get("schema") == SCHEMA, "verification schema differs")
    require(report.get("generation_policy") == GENERATION_POLICY, "generation policy differs")
    require(report.get("coverage") == {"routes": 2, "groups": 40, "placements": 240, "candidate_archives": 2, "contact_sheets": 4}, "coverage differs")
    for route_id in ROUTE_ORDER:
        route = report["routes"][route_id]
        candidate = root / "candidate" / Path(str(route["archive"]))
        validate_file(candidate, route["candidate"], f"{route_id} candidate")
        blob = candidate.read_bytes()
        parsed = lz4.parse_link(blob)
        require(lz4.rebuild_link(parsed) == blob, f"{route_id} candidate LINK identity failed")
        require(route["unselected_bc3_blocks_byte_preserved"] is True and route["other_textures_in_same_g1t_byte_preserved"] is True, f"{route_id} preservation proof differs")
    for relative, expected in report["artifacts"].items():
        validate_file(root / Path(relative), expected, f"artifact {relative}")
    return {"status": "PASS", "report_sha256": report["report_sha256"], "candidate_archives": 2, "placements": 240, "steam_writes": 0}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    build_parser = commands.add_parser("build")
    build_parser.add_argument("--static-root", type=Path, default=DEFAULT_STATIC_ROOT)
    build_parser.add_argument("--target-root", type=Path, default=DEFAULT_TARGET_ROOT)
    build_parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    build_parser.add_argument("--ui-font", type=Path, default=DEFAULT_UI_FONT)
    build_parser.add_argument("--output-root", type=Path, required=True)
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--root", type=Path, required=True)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    value = build(args) if args.command == "build" else verify(args)
    print(json.dumps(value, ensure_ascii=False, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (IntegrationError, lz4.LZ4Error, atlas_codec.AtlasError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
