#!/usr/bin/env python3
"""Check or explicitly refresh the source-free SeoulHangang demand pin.

The private font builder deliberately fails closed when the public overlay
catalog changes.  This helper recomputes the corresponding manifest pin from
the same strict overlay validation and the same pristine PC G1N preflight used
by ``build_seoulhangang_v1.py``.  Its default mode is read-only.  ``--write``
is required to replace only the ``pinned_public_korean_demand`` member of the
font manifest.

No overlay text, stock bytes, official TTF bytes, or raster pixels are written
or printed.  The only writable file is the reviewed public manifest.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
PATCH_ROOT = SCRIPT_DIR.parents[1]
GAME_ROOT = PATCH_ROOT.parent
MANIFEST_PATH = SCRIPT_DIR / "manifest.v1.json"
STOCK_RELATIVE = Path("KR_PATCH_BACKUP/officer_names_v0_1/stock/font.stock.bak")
MANIFEST_SCHEMA = "nobu16.kr.font-seoulhangang-v1-manifest.v1"
SOURCE_DESCRIPTION = (
    "all PK-loaded string overlays (seven PK resources plus exact shared "
    "MSG/SC/strdata.bin) are derived from the SHA-pinned translation-progress "
    "catalog; the plan records one source-free hash row per file"
)
EXPECTED_PK_RESOURCES = (
    "MSG_PK/SC/msgui.bin",
    "MSG_PK/SC/msgev.bin",
    "MSG_PK/SC/msgdata.bin",
    "MSG_PK/SC/msgbre.bin",
    "MSG_PK/SC/msgire.bin",
    "MSG_PK/SC/msgstf.bin",
    "MSG_PK/SC/msggame.bin",
)
EXPECTED_SHARED_RESOURCES = ("MSG/SC/strdata.bin",)
EXPECTED_FONT_RESOURCES = EXPECTED_PK_RESOURCES + EXPECTED_SHARED_RESOURCES


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load helper module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# Import, rather than duplicate, every text and stock validation primitive used
# by the reviewed private builder.  This keeps refresh and build rejection
# behavior identical for JSON, source-free policy, Korean output, controls,
# scripts, Unicode normalization, resource ownership, and the PC G1N parser.
BASE = _load_module(
    "nobu16_font_seoulhangang_v1_refresh_base",
    SCRIPT_DIR / "build_seoulhangang_v1.py",
)
PROGRESS_RELATIVE = BASE.PROGRESS_CONFIG_RELATIVE


class DemandPinError(BASE.FontBuildError):
    """Raised when refresh scope or a pinned input fails closed."""


def default_stock_path(project_root: Path = PATCH_ROOT) -> Path:
    """Return the sole accepted pristine stock input for this project."""

    return project_root.resolve().parent / STOCK_RELATIVE


def _inside(parent: Path, child: Path) -> bool:
    parent = parent.resolve()
    child = child.resolve()
    return child == parent or parent in child.parents


def _canonical_codepoint_hash(codepoints: Iterable[int]) -> str:
    return BASE.canonical_codepoint_hash(codepoints)


def collect_overlay_demand(
    project_root: Path = PATCH_ROOT,
    progress_relative: str = PROGRESS_RELATIVE,
) -> dict[str, Any]:
    """Validate and collect the eight exact PK-loaded corpora without source text."""

    project_root = project_root.resolve()
    relative_progress = BASE._safe_project_relative_path(
        progress_relative, "translation progress"
    )
    progress_path = (project_root / relative_progress).resolve()
    if not _inside(project_root, progress_path):
        raise DemandPinError("translation progress resolved outside project root")
    try:
        progress_raw = progress_path.read_bytes()
    except OSError as exc:
        raise DemandPinError(f"cannot read translation progress: {exc}") from exc
    progress = BASE.loads_json_strict(progress_raw, relative_progress.as_posix())
    resources = progress.get("resources")
    if not isinstance(resources, list):
        raise DemandPinError("translation progress resources must be an array")
    shared_resources = progress.get("shared_strings")
    if not isinstance(shared_resources, list):
        raise DemandPinError("translation progress shared_strings must be an array")

    core_string_rows = [
        row
        for row in resources
        if isinstance(row, dict) and row.get("kind") == "strings"
    ]
    shared_string_rows = [
        row
        for row in shared_resources
        if isinstance(row, dict) and row.get("kind") == "strings"
    ]
    core_paths = tuple(row.get("path") for row in core_string_rows)
    shared_paths = tuple(row.get("path") for row in shared_string_rows)
    if core_paths != EXPECTED_PK_RESOURCES:
        raise DemandPinError(
            "translation progress must contain the seven PK string resources in canonical order"
        )
    if shared_paths != EXPECTED_SHARED_RESOURCES or len(shared_string_rows) != len(shared_resources):
        raise DemandPinError(
            "translation progress shared_strings must contain only MSG/SC/strdata.bin"
        )

    all_codepoints: set[int] = set()
    source_rows: list[dict[str, Any]] = []
    resource_rows: list[dict[str, Any]] = []
    seen_resources: set[str] = set()
    seen_overlays: set[Path] = set()
    total_entries = 0

    for resource_row in core_string_rows + shared_string_rows:
        progress_resource = resource_row.get("path")
        overlay_paths = resource_row.get("overlay_globs")
        if not isinstance(progress_resource, str) or not isinstance(overlay_paths, list):
            raise DemandPinError("font string resource has an invalid path or overlay list")
        if progress_resource not in EXPECTED_FONT_RESOURCES:
            raise DemandPinError(
                f"resource outside the PK font-demand scope: {progress_resource!r}"
            )
        if progress_resource in seen_resources:
            raise DemandPinError(f"duplicate font string resource: {progress_resource}")
        seen_resources.add(progress_resource)
        if not overlay_paths:
            raise DemandPinError(
                f"font string resource has no public overlays: {progress_resource}"
            )

        resource_sources: list[dict[str, Any]] = []
        resource_entries = 0
        for logical_path in overlay_paths:
            relative = BASE._safe_project_relative_path(logical_path, progress_resource)
            path = (project_root / relative).resolve()
            if not _inside(project_root, path) or path == project_root:
                raise DemandPinError(f"{logical_path}: resolved outside project root")
            if path in seen_overlays:
                raise DemandPinError(f"overlay is listed more than once: {logical_path}")
            seen_overlays.add(path)
            if not path.is_file():
                raise DemandPinError(f"missing pinned public overlay: {logical_path}")

            raw = path.read_bytes()
            overlay = BASE.loads_json_strict(raw, str(logical_path))
            BASE._require_source_free_policy(overlay, str(logical_path))
            schema = overlay.get("schema")
            if not isinstance(schema, str) or not schema:
                raise DemandPinError(f"{logical_path}: overlay has no schema")
            actual_resource = BASE._overlay_resource(overlay, str(logical_path))
            if actual_resource not in BASE._expected_overlay_resource(progress_resource):
                raise DemandPinError(
                    f"{logical_path}: resource {actual_resource!r} does not serve "
                    f"{progress_resource!r}"
                )
            entries = overlay.get("entries")
            if not isinstance(entries, list) or not entries:
                raise DemandPinError(f"{logical_path}: entries must be a nonempty array")
            declared_count = overlay.get("entry_count")
            if declared_count is not None and declared_count != len(entries):
                raise DemandPinError(f"{logical_path}: entry_count does not match entries")

            local_codepoints: set[int] = set()
            for index, entry in enumerate(entries):
                if not isinstance(entry, dict) or "ko" not in entry:
                    raise DemandPinError(
                        f"{logical_path}: entries[{index}] has no Korean output"
                    )
                label = f"{logical_path}: entries[{index}]"
                text = BASE._validate_ko_text(entry["ko"], label)
                local_codepoints.update(BASE.renderable_characters(text, label))

            source = {
                "path": relative.as_posix(),
                "sha256": BASE.sha256_bytes(raw),
                "resource": progress_resource,
                "entry_count": len(entries),
                "schema": schema,
            }
            all_codepoints.update(local_codepoints)
            source_rows.append(source)
            resource_sources.append(source)
            resource_entries += len(entries)
            total_entries += len(entries)

        resource_rows.append(
            {
                "resource": progress_resource,
                "source_count": len(resource_sources),
                "entry_count": resource_entries,
                "source_catalog_sha256": BASE.canonical_json_hash(resource_sources),
            }
        )

    actual_resources = tuple(row["resource"] for row in resource_rows)
    if actual_resources != EXPECTED_FONT_RESOURCES:
        raise DemandPinError(
            "translation progress must contain the exact eight PK-loaded string resources in canonical order"
        )
    if not source_rows:
        raise DemandPinError("translation progress contains no PK-loaded string overlays")

    ordered = sorted(all_codepoints)
    hangul = [codepoint for codepoint in ordered if 0xAC00 <= codepoint <= 0xD7A3]
    hangul_set = set(hangul)
    non_hangul = [codepoint for codepoint in ordered if codepoint not in hangul_set]
    if not hangul:
        raise DemandPinError("pinned Korean overlays contain no Hangul syllables")

    return {
        "translation_progress": {
            "path": relative_progress.as_posix(),
            "sha256": BASE.sha256_bytes(progress_raw),
        },
        "source_count": len(source_rows),
        "source_catalog_sha256": BASE.canonical_json_hash(source_rows),
        "resource_catalog": resource_rows,
        "source_entry_count": total_entries,
        "codepoint_count": len(ordered),
        "codepoints_sha256": _canonical_codepoint_hash(ordered),
        "hangul_syllable_count": len(hangul),
        "hangul_syllables_sha256": _canonical_codepoint_hash(hangul),
        "non_hangul_count": len(non_hangul),
        "non_hangul_sha256": _canonical_codepoint_hash(non_hangul),
        # These three private rows are never serialized into the manifest.
        "_source_rows": source_rows,
        "_codepoints": ordered,
        "_hangul": hangul,
        "_non_hangul": non_hangul,
    }


def compute_pin(
    project_root: Path = PATCH_ROOT,
    stock_path: Path | None = None,
    *,
    expected_stock_sha256: str = BASE.STOCK_SC_SHA256,
    preflight_stock: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Compute the complete public demand pin from the fixed pristine backup."""

    project_root = project_root.resolve()
    required_stock = default_stock_path(project_root).resolve()
    chosen_stock = required_stock if stock_path is None else stock_path.resolve()
    if chosen_stock != required_stock:
        raise DemandPinError(
            "stock input must be officer_names_v0_1/stock/font.stock.bak"
        )
    if not chosen_stock.is_file():
        raise DemandPinError(f"missing pristine stock archive: {chosen_stock}")
    actual_stock_hash = BASE.sha256_file(chosen_stock)
    if actual_stock_hash != expected_stock_sha256:
        raise DemandPinError(
            "pristine stock SHA-256 mismatch: "
            f"expected={expected_stock_sha256} actual={actual_stock_hash}"
        )

    demand = collect_overlay_demand(project_root)
    preflight = BASE.V6.preflight_stock if preflight_stock is None else preflight_stock
    try:
        stock_blob = chosen_stock.read_bytes()
        _stock_entries, _coverage, append_plan = preflight(
            stock_blob, list(demand["_hangul"]), list(demand["_non_hangul"])
        )
    except (OSError, KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, BASE.FontBuildError):
            raise
        raise DemandPinError(f"pristine stock G1N preflight failed: {exc}") from exc

    raster_codepoints = sorted(
        {
            codepoint
            for entry_plan in append_plan.values()
            for table_plan in entry_plan.values()
            for codepoint in table_plan
        }
    )
    if not set(demand["_hangul"]).issubset(raster_codepoints):
        raise DemandPinError("all demanded Hangul must be appended to every G1N profile")
    if not raster_codepoints:
        raise DemandPinError("empty font append plan")

    append_contract: list[dict[str, Any]] = []
    try:
        for entry in (6, 7):
            for table in (0, 1):
                points = append_plan[entry][table]
                append_contract.append(
                    {
                        "entry": entry,
                        "table": table,
                        "count": len(points),
                        "codepoints_sha256": _canonical_codepoint_hash(points),
                    }
                )
    except (KeyError, TypeError) as exc:
        raise DemandPinError(f"pristine stock append plan is incomplete: {exc}") from exc

    public_keys = (
        "translation_progress",
        "source_count",
        "source_catalog_sha256",
        "resource_catalog",
        "source_entry_count",
        "codepoint_count",
        "codepoints_sha256",
        "hangul_syllable_count",
        "hangul_syllables_sha256",
        "non_hangul_count",
        "non_hangul_sha256",
    )
    return {
        **{key: demand[key] for key in public_keys},
        "raster_codepoint_count": len(raster_codepoints),
        "raster_codepoints_sha256": _canonical_codepoint_hash(raster_codepoints),
        "append_contract": append_contract,
        "sources": SOURCE_DESCRIPTION,
    }


def _replace_top_level_member(raw: bytes, key: str, value: Any) -> bytes:
    """Replace one top-level JSON value while preserving all surrounding bytes."""

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise DemandPinError(f"font manifest is not UTF-8: {exc}") from exc
    decoder = json.JSONDecoder()
    depth = 0
    index = 0
    in_string = False
    escaped = False
    while index < len(text):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue
        if char == '"':
            if depth == 1:
                try:
                    candidate, key_end = decoder.raw_decode(text, index)
                except json.JSONDecodeError as exc:
                    raise DemandPinError(f"cannot scan font manifest: {exc}") from exc
                cursor = key_end
                while cursor < len(text) and text[cursor].isspace():
                    cursor += 1
                if candidate == key and cursor < len(text) and text[cursor] == ":":
                    value_start = cursor + 1
                    while value_start < len(text) and text[value_start].isspace():
                        value_start += 1
                    try:
                        _old_value, value_end = decoder.raw_decode(text, value_start)
                    except json.JSONDecodeError as exc:
                        raise DemandPinError(f"cannot locate manifest pin value: {exc}") from exc
                    line_start = text.rfind("\n", 0, index) + 1
                    indentation = text[line_start:index]
                    rendered_lines = json.dumps(
                        value, ensure_ascii=False, indent=2
                    ).splitlines()
                    rendered = rendered_lines[0]
                    if len(rendered_lines) > 1:
                        rendered += "\n" + "\n".join(
                            indentation + line for line in rendered_lines[1:]
                        )
                    return (text[:value_start] + rendered + text[value_end:]).encode("utf-8")
            in_string = True
            index += 1
            continue
        if char in "[{":
            depth += 1
        elif char in "]}":
            depth -= 1
        index += 1
    raise DemandPinError(f"font manifest has no top-level {key!r} member")


def check_or_write(
    *,
    project_root: Path = PATCH_ROOT,
    manifest_path: Path = MANIFEST_PATH,
    write: bool = False,
    expected_stock_sha256: str = BASE.STOCK_SC_SHA256,
    preflight_stock: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Return current/stale/updated status; write only with explicit consent."""

    project_root = project_root.resolve()
    manifest_path = manifest_path.resolve()
    if not _inside(project_root, manifest_path):
        raise DemandPinError("font manifest resolved outside project root")
    try:
        original_raw = manifest_path.read_bytes()
    except OSError as exc:
        raise DemandPinError(f"cannot read font manifest: {exc}") from exc
    manifest = BASE.loads_json_strict(original_raw, str(manifest_path))
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise DemandPinError("unexpected font manifest schema")
    current = manifest.get("pinned_public_korean_demand")
    if not isinstance(current, dict):
        raise DemandPinError("font manifest has no pinned_public_korean_demand object")

    candidate = compute_pin(
        project_root,
        expected_stock_sha256=expected_stock_sha256,
        preflight_stock=preflight_stock,
    )
    status = "current" if current == candidate else "stale"
    if status == "stale" and write:
        # Avoid overwriting a concurrent manifest edit made during the stock
        # preflight.  Only the exact bytes inspected above are eligible.
        if manifest_path.read_bytes() != original_raw:
            raise DemandPinError("font manifest changed during refresh; retry")
        updated_raw = _replace_top_level_member(
            original_raw, "pinned_public_korean_demand", candidate
        )
        updated = BASE.loads_json_strict(updated_raw, str(manifest_path))
        old_other = {key: value for key, value in manifest.items() if key != "pinned_public_korean_demand"}
        new_other = {key: value for key, value in updated.items() if key != "pinned_public_korean_demand"}
        if old_other != new_other or updated.get("pinned_public_korean_demand") != candidate:
            raise DemandPinError("refusing a manifest rewrite outside the demand pin")
        BASE.atomic_write(manifest_path, updated_raw)
        status = "updated"

    return {
        "status": status,
        "manifest": str(manifest_path),
        "current_pin_sha256": BASE.canonical_json_hash(current),
        "computed_pin_sha256": BASE.canonical_json_hash(candidate),
        "translation_progress_sha256": candidate["translation_progress"]["sha256"],
        "source_count": candidate["source_count"],
        "source_entry_count": candidate["source_entry_count"],
        "codepoint_count": candidate["codepoint_count"],
        "raster_codepoint_count": candidate["raster_codepoint_count"],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check",
        action="store_true",
        help="check the current pin without writing (default)",
    )
    mode.add_argument(
        "--write",
        action="store_true",
        help="atomically replace only pinned_public_korean_demand when stale",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = check_or_write(write=args.write)
    except (DemandPinError, BASE.FontBuildError, OSError) as exc:
        print(f"error={exc}", file=sys.stderr)
        return 2
    for key in (
        "status",
        "manifest",
        "translation_progress_sha256",
        "current_pin_sha256",
        "computed_pin_sha256",
        "source_count",
        "source_entry_count",
        "codepoint_count",
        "raster_codepoint_count",
    ):
        print(f"{key}={result[key]}")
    return 1 if result["status"] == "stale" else 0


if __name__ == "__main__":
    raise SystemExit(main())
