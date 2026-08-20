#!/usr/bin/env python3
"""Build the approved medium B-font ordinary-button atlases.

The builder is deliberately static and archive-free.  It reconstructs each
stock button body from other cells in the same original JP atlas, preserves
icon pixels, renders the approved Korean label at 30/60 px, and writes two
full-size preview atlases below ``tmp``.  Archive integration is a separate,
block-scoped step.
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
PILOT_WS = REPO / "workstreams" / "ordinary_button_layered_render_pilot_v1"
CATALOG_WS = REPO / "workstreams" / "ordinary_button_atlas_catalog_v1"
for candidate in (PILOT_WS, CATALOG_WS):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import build_ordinary_button_atlas_catalog_v1 as atlas_catalog  # noqa: E402
import build_ordinary_button_layered_render_pilot_v1 as pilot  # noqa: E402

try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover - workspace runtime invariant.
    raise RuntimeError("NumPy and Pillow are required") from exc


SCHEMA = "nobu16.kr.ordinary-button-layered-rebuild.v1"
GENERATION_POLICY = "forbidden-and-not-used"
ROUTE_ORDER = ("common_low", "common_high_standard")
STATE_COUNT = 6
VARIANT = "medium"
STANDARD_NAMES = (
    "approve", "stop", "close", "deny", "release_all", "confirm", "reject", "back", "no", "hime",
    "command", "renegotiate", "accept", "dispose", "skip", "start", "recruit", "warrior", "yes", "next",
)

DEFAULT_CATALOG = CATALOG_WS / "ordinary_button_catalog_v1.json"
DEFAULT_SOURCE_ROOT = WORKSPACE / "scratch" / "release-v0940-wheel-b-20260819-01" / "resource-input" / "source"
DEFAULT_TARGET_ROOT = WORKSPACE / "scratch" / "release-v0940-wheel-b-20260819-01" / "resource-input" / "target"
DEFAULT_FONT = WORKSPACE / "repository" / "KR_PATCH_WORK" / "tmp" / "third_party_fonts" / "SeoulHangangEB.ttf"
DEFAULT_UI_FONT = REPO / "vendor" / "noto" / "NotoSansKR-wght.ttf"


class RebuildError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RebuildError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def file_spec(path: Path) -> dict[str, Any]:
    return {"path": str(path.resolve()), "size": path.stat().st_size, "sha256": sha256_file(path)}


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def fresh_output(path: Path) -> Path:
    value = path.resolve()
    tmp_root = (REPO / "tmp").resolve()
    try:
        value.relative_to(tmp_root)
    except ValueError as exc:
        raise RebuildError(f"output must stay below {tmp_root}: {value}") from exc
    require(not value.exists(), f"refusing to replace existing output: {value}")
    value.mkdir(parents=True)
    return value


def canonical_changed(a: "np.ndarray[Any, Any]", b: "np.ndarray[Any, Any]") -> "np.ndarray[Any, Any]":
    return np.any(pilot.wheel.canonical_rgba(a) != pilot.wheel.canonical_rgba(b), axis=-1)


def contact_pages(
    output: Path,
    route_id: str,
    labels: Sequence[Mapping[str, Any]],
    source: Mapping[str, "np.ndarray[Any, Any]"],
    clean: Mapping[str, "np.ndarray[Any, Any]"],
    final: Mapping[str, "np.ndarray[Any, Any]"],
    ui_font_path: Path,
) -> list[Path]:
    files: list[Path] = []
    font = ImageFont.truetype(str(ui_font_path), 15)
    try:
        font.set_variation_by_axes([650])
    except (AttributeError, OSError):
        pass
    columns = (
        (1, "JP 상태2", "source"), (1, "클린 상태2", "clean"), (1, "완성 상태2", "final"),
        (0, "완성 상태1", "final"), (3, "완성 상태4", "final"), (5, "완성 상태6", "final"),
    )
    for page, start in enumerate(range(0, len(labels), 10), 1):
        selected = labels[start : start + 10]
        cell_width, cell_height, left, gap, top = 384, 176, 160, 8, 44
        canvas = Image.new(
            "RGB",
            (left + len(columns) * (cell_width + gap) + gap, top + len(selected) * (cell_height + gap) + 34),
            (25, 27, 31),
        )
        draw = ImageDraw.Draw(canvas)
        for column, (_state, title, _kind) in enumerate(columns):
            draw.text((left + column * (cell_width + gap) + 140, 12), title, font=font, fill=(235, 236, 238))
        for row_index, label in enumerate(selected):
            name = str(label["name"])
            y = top + row_index * (cell_height + gap)
            draw.text((8, y + 63), f"{start + row_index:02d} {name}\n{label['ko']}", font=font, fill=(224, 227, 231), spacing=3)
            for column, (state, _title, kind) in enumerate(columns):
                values = source[name] if kind == "source" else clean[name] if kind == "clean" else final[name]
                canvas.paste(pilot.flatten_cell(values[state], route_id), (left + column * (cell_width + gap), y))
        draw.text(
            (8, canvas.height - 25),
            f"{route_id} / B Medium / 30px low, 60px high / deterministic original-layer reconstruction",
            font=font,
            fill=(165, 173, 184),
        )
        path = output / "contact" / f"{route_id}_medium_{page:02d}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(path, optimize=False, compress_level=9)
        files.append(path)
    return files


def build(args: argparse.Namespace) -> dict[str, Any]:
    output = fresh_output(args.output)
    catalog_path = args.catalog.resolve(strict=True)
    source_root = args.source_root.resolve(strict=True)
    target_root = args.target_root.resolve(strict=True)
    font_path = args.font.resolve(strict=True)
    ui_font_path = args.ui_font.resolve(strict=True)
    pilot.validate_file(font_path, {"size": font_path.stat().st_size, "sha256": pilot.FONT_SHA256}, "B font")
    pilot.validate_file(ui_font_path, {"size": ui_font_path.stat().st_size, "sha256": pilot.UI_FONT_SHA256}, "UI font")
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    require(catalog.get("schema") == atlas_catalog.SCHEMA, "ordinary-button catalog schema differs")
    labels = [item for item in catalog["labels"] if item["name"] in STANDARD_NAMES]
    require(tuple(str(item["name"]) for item in labels) == STANDARD_NAMES, "standard label order or coverage differs")
    labels_by_name = {str(item["name"]): item for item in labels}
    require(labels_by_name["release_all"]["ko"] == "전부해방", "release_all must render as 전부해방")

    cache: dict[tuple[Path, int, int], atlas_catalog.LoadedG1T] = {}
    route_reports: dict[str, Any] = {}
    artifacts: list[Path] = []
    total_icon_differences = 0
    total_outside_union = 0
    all_fit_scales: list[float] = []

    for route_id in ROUTE_ORDER:
        print(f"stage={route_id}:load", flush=True)
        route = catalog["routes"][route_id]
        rows = pilot.route_rows(catalog, route_id)
        archive = Path(str(route["archive"]))
        source_path = source_root / archive
        target_path = target_root / archive
        source_spec = pilot.validate_file(source_path, route["source"], f"{route_id} stock source")
        target_spec = pilot.validate_file(target_path, route["target"], f"{route_id} v0.94 target")
        source_atlas, source_resource = pilot.load_atlas(source_path, route, cache)
        target_atlas, target_resource = pilot.load_atlas(target_path, route, cache)
        require(source_atlas.shape == target_atlas.shape, f"{route_id} source/target atlas dimensions differ")
        groups = pilot.extract_groups(source_atlas, rows)
        donor_samples = [groups[group] for group in range(20)]
        donor_cores = [pilot.original_foreground_core(sample, route_id) for sample in donor_samples]
        desired_atlas = target_atlas.copy()
        write_mask = np.zeros(target_atlas.shape[:2], dtype=bool)
        cell_size = (groups.shape[3], groups.shape[2])
        source_selected: dict[str, np.ndarray[Any, Any]] = {}
        clean_selected: dict[str, np.ndarray[Any, Any]] = {}
        final_selected: dict[str, np.ndarray[Any, Any]] = {}
        group_reports: list[dict[str, Any]] = []

        for group, name in enumerate(STANDARD_NAMES):
            print(f"stage={route_id}:group={group:02d}:{name}", flush=True)
            source = groups[group]
            cleanup, mask_report = pilot.label_cleanup_mask(source, route_id, name)
            clean, donor_report = pilot.clean_group(
                source,
                cleanup,
                donor_samples=donor_samples,
                donor_cores=donor_cores,
                route_id=route_id,
            )
            protected_end = pilot.icon_protect_end(route_id, name)
            geometry = pilot.source_label_geometry(source, clean, cleanup, protected_end=protected_end)
            scale = pilot.scale_for_route(route_id)
            # The cleanup extent follows the original JP glyphs and can be much
            # narrower than the real button text lane (for example 姫 -> 공주).
            # Rendering therefore uses the physical inner lane; icon buttons
            # start after the byte-exact protected icon region.
            render_safe_zone = (
                protected_end + 6 * scale if protected_end else 8 * scale,
                cell_size[0] - 8 * scale,
            )
            render_center = tuple(float(value) for value in geometry["source_median_center"])
            require(render_safe_zone[0] < render_center[0] < render_safe_zone[1], f"render center escaped physical lane: {route_id} {name}")
            geometry["render_safe_zone_x"] = list(render_safe_zone)
            layers, typography = pilot.render_layers(
                route_id=route_id,
                text=str(labels_by_name[name]["ko"]),
                variant=VARIANT,
                cell_size=cell_size,
                center=render_center,
                safe_zone=render_safe_zone,
                font_path=font_path,
            )
            fit_scale = float(typography["uniform_fit_scale"])
            all_fit_scales.append(fit_scale)
            require(fit_scale == 1.0, f"Medium label required fit scaling: {route_id} {name} {fit_scale}")
            final = np.stack([pilot.wheel.alpha_composite(clean[state], layers[state]) for state in range(STATE_COUNT)])

            icon_differences = 0
            if protected_end:
                icon_differences = int(np.count_nonzero(np.any(final[:, :, :protected_end] != source[:, :, :protected_end], axis=-1)))
                require(icon_differences == 0, f"protected icon region changed: {route_id} {name}")
            outside_union = 0
            state_reports: list[dict[str, Any]] = []
            selected_rows = sorted((row for row in rows if int(row["group"]) == group), key=lambda row: int(row["state"]))
            require([int(row["state"]) for row in selected_rows] == list(range(1, 7)), f"state coverage differs: {route_id} {name}")
            for state, row in enumerate(selected_rows):
                allowed = cleanup | (layers[state, ..., 3] > 0)
                escaped = int(np.count_nonzero(canonical_changed(final[state], source[state]) & ~allowed))
                require(escaped == 0, f"composite escaped label union: {route_id} {name} state {state + 1}")
                outside_union += escaped
                x0, y0, x1, y1 = (int(value) for value in row["processing_rect"])
                require((x1 - x0, y1 - y0) == cell_size, f"cell geometry differs: {route_id} {name}")
                require(not bool(np.any(write_mask[y0:y1, x0:x1])), f"standard cells overlap: {route_id} {name}")
                desired_atlas[y0:y1, x0:x1] = final[state]
                write_mask[y0:y1, x0:x1] = True
                state_reports.append(
                    {
                        "state": state + 1,
                        "processing_rect": [x0, y0, x1, y1],
                        "outside_cleanup_and_new_label_changed_pixels": escaped,
                        "changed_from_stock_pixels": int(np.count_nonzero(canonical_changed(final[state], source[state]))),
                    }
                )

            name_dir = output / route_id / f"{group:02d}_{name}"
            name_dir.mkdir(parents=True)
            source2 = name_dir / "source_state_2.png"
            clean2 = name_dir / "clean_state_2.png"
            mask_path = name_dir / "cleanup_mask.png"
            Image.fromarray(source[1]).save(source2, optimize=False, compress_level=9)
            Image.fromarray(clean[1]).save(clean2, optimize=False, compress_level=9)
            Image.fromarray(cleanup.astype(np.uint8) * 255).save(mask_path, optimize=False, compress_level=9)
            artifacts.extend((source2, clean2, mask_path))
            final_paths: list[str] = []
            for state in range(STATE_COUNT):
                path = name_dir / f"medium_state_{state + 1}.png"
                Image.fromarray(final[state]).save(path, optimize=False, compress_level=9)
                artifacts.append(path)
                final_paths.append(str(path.relative_to(output)).replace("\\", "/"))

            source_selected[name] = source
            clean_selected[name] = clean
            final_selected[name] = final
            total_icon_differences += icon_differences
            total_outside_union += outside_union
            group_reports.append(
                {
                    "group": group,
                    "name": name,
                    "jp": labels_by_name[name]["jp"],
                    "ko": labels_by_name[name]["ko"],
                    "mask": mask_report,
                    "donor_reconstruction": donor_report,
                    "source_label_geometry": geometry,
                    "typography": typography,
                    "protected_icon_canonical_rgba_differences": icon_differences,
                    "states": state_reports,
                    "final_files": final_paths,
                }
            )

        require(int(np.count_nonzero(write_mask)) == sum((int(r["processing_rect"][2]) - int(r["processing_rect"][0])) * (int(r["processing_rect"][3]) - int(r["processing_rect"][1])) for r in rows), f"{route_id} write mask coverage differs")
        outside_target_changes = int(np.count_nonzero(canonical_changed(desired_atlas, target_atlas) & ~write_mask))
        require(outside_target_changes == 0, f"{route_id} desired atlas escaped standard cells")
        preview = output / "atlas" / f"{route_id}_medium.png"
        preview.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(desired_atlas).save(preview, optimize=False, compress_level=9)
        artifacts.append(preview)
        contacts = contact_pages(output, route_id, labels, source_selected, clean_selected, final_selected, ui_font_path)
        artifacts.extend(contacts)
        route_reports[route_id] = {
            "archive": str(archive).replace("\\", "/"),
            "source": source_spec,
            "target": target_spec,
            "source_resource": source_resource,
            "target_resource": target_resource,
            "dimensions": [target_atlas.shape[1], target_atlas.shape[0]],
            "cell_size": list(cell_size),
            "groups": group_reports,
            "group_count": len(group_reports),
            "placements": len(rows),
            "standard_cell_pixels": int(np.count_nonzero(write_mask)),
            "outside_standard_cell_changed_pixels": outside_target_changes,
            "atlas_preview": str(preview.relative_to(output)).replace("\\", "/"),
            "contact_sheets": [str(path.relative_to(output)).replace("\\", "/") for path in contacts],
        }

    require(total_icon_differences == 0, "icon preservation aggregate failed")
    require(total_outside_union == 0, "non-label preservation aggregate failed")
    require(min(all_fit_scales) == 1.0, "at least one Medium label was scaled")
    artifact_table = {
        str(path.relative_to(output)).replace("\\", "/"): {"size": path.stat().st_size, "sha256": sha256_file(path)}
        for path in sorted(artifacts)
    }
    manifest = {
        "schema": SCHEMA,
        "generation_policy": GENERATION_POLICY,
        "archive_writes": 0,
        "patcher_writes": 0,
        "steam_writes": 0,
        "variant": VARIANT,
        "font": {"candidate": "B", "name": "SeoulHangang ExtraBold", "sha256": pilot.FONT_SHA256},
        "coverage": {"routes": 2, "groups": 20, "states_per_group": 6, "placements": 240, "atlas_previews": 2},
        "labels": labels,
        "inputs": {"catalog": file_spec(catalog_path)},
        "routes": route_reports,
        "validation": {
            "clean_body_derived_only_from_original_same_atlas_groups": True,
            "generation_used": False,
            "all_uniform_fit_scales": 1.0,
            "protected_icon_canonical_rgba_differences": total_icon_differences,
            "outside_cleanup_and_new_label_changed_pixels": total_outside_union,
            "outside_standard_cells_changed_pixels": 0,
            "overlap_pixels": 0,
            "release_all_label": "전부해방",
        },
        "artifacts": artifact_table,
    }
    manifest_path = output / "manifest.v1.json"
    write_json(manifest_path, manifest)
    return {
        "output": str(output),
        "manifest": str(manifest_path),
        "manifest_sha256": sha256_file(manifest_path),
        "groups": 20,
        "placements": 240,
        "artifacts": len(artifact_table),
    }


def verify(args: argparse.Namespace) -> dict[str, Any]:
    root = args.root.resolve(strict=True)
    manifest_path = root / "manifest.v1.json"
    require(manifest_path.is_file(), f"manifest is missing: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    require(manifest.get("schema") == SCHEMA, "manifest schema differs")
    require(manifest.get("generation_policy") == GENERATION_POLICY, "generation policy differs")
    require(manifest.get("coverage") == {"routes": 2, "groups": 20, "states_per_group": 6, "placements": 240, "atlas_previews": 2}, "coverage differs")
    validation = manifest["validation"]
    require(validation == {
        "clean_body_derived_only_from_original_same_atlas_groups": True,
        "generation_used": False,
        "all_uniform_fit_scales": 1.0,
        "protected_icon_canonical_rgba_differences": 0,
        "outside_cleanup_and_new_label_changed_pixels": 0,
        "outside_standard_cells_changed_pixels": 0,
        "overlap_pixels": 0,
        "release_all_label": "전부해방",
    }, f"validation differs: {validation}")
    for relative, expected in manifest["artifacts"].items():
        path = root / Path(relative)
        require(path.is_file(), f"artifact is missing: {relative}")
        require(path.stat().st_size == int(expected["size"]) and sha256_file(path) == str(expected["sha256"]), f"artifact pin differs: {relative}")
    return {"status": "PASS", "manifest_sha256": sha256_file(manifest_path), "groups": 20, "placements": 240}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    build_parser = commands.add_parser("build")
    build_parser.add_argument("--output", type=Path, required=True)
    build_parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    build_parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    build_parser.add_argument("--target-root", type=Path, default=DEFAULT_TARGET_ROOT)
    build_parser.add_argument("--font", type=Path, default=DEFAULT_FONT)
    build_parser.add_argument("--ui-font", type=Path, default=DEFAULT_UI_FONT)
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
    except (RebuildError, pilot.PilotError, atlas_catalog.CatalogError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
