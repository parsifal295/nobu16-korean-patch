#!/usr/bin/env python3
"""Build a private, file-only SeoulHangang G1N candidate for PC PK.

The builder intentionally does *not* publish a font file, raster payload, G1N,
LINK archive, or complete ``res_lang.bin``.  It takes a locally acquired,
SHA-pinned official SeoulHangang Medium TTF plus a user-owned pristine PC
``RES_SC/res_lang.bin`` backup and writes a new candidate only below an
explicit local output root.  It never overwrites either input or an installed
game file.

The default corpus is deliberately pinned to source-free public Korean
overlays, including every registered strict Switch-v1.1-to-PK transfer.  A source
change must be reviewed and its pin updated here before it can alter glyph
demand.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Any, Iterable, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
PATCH_ROOT = SCRIPT_DIR.parents[1]
GAME_ROOT = PATCH_ROOT.parent
sys.dont_write_bytecode = True

STOCK_SC_SHA256 = "916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99"
OFFICIAL_ARCHIVE_URL = "https://www.seoul.go.kr/upload/seoul/font/seoul_font3.zip"
OFFICIAL_ARCHIVE_SHA256 = "7AB485B98F5B1A1B05CFD04484DD49A62F856BE8506223CD99E5EA1A33E400A7"
SEOUL_HANGANG_M_SHA256 = "D27E1B26B55E507BEC1045962C954CF426D79605009C720FAD1C9EF808E312CB"
SEOUL_HANGANG_M_SIZE = 7_627_124
SEOUL_HANGANG_M_FAMILY = "SeoulHangang M"

ESC_COMMAND_RE = re.compile("\\x1bC.", re.DOTALL)
DEMAND_MANIFEST = SCRIPT_DIR / "manifest.v1.json"
PROGRESS_CONFIG_RELATIVE = "data/public/translation_progress.v0.1.json"
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

PROFILES = (
    {"entry": 6, "table": 0, "family": SEOUL_HANGANG_M_FAMILY, "style": "Regular", "raster_size": 46, "cell": 48},
    {"entry": 6, "table": 1, "family": SEOUL_HANGANG_M_FAMILY, "style": "Regular", "raster_size": 46, "cell": 48},
    {"entry": 7, "table": 0, "family": SEOUL_HANGANG_M_FAMILY, "style": "Regular", "raster_size": 32, "cell": 32},
    {"entry": 7, "table": 1, "family": SEOUL_HANGANG_M_FAMILY, "style": "Regular", "raster_size": 32, "cell": 32},
)


class FontBuildError(ValueError):
    """Raised when a pinned source or a G1N safety contract fails."""


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load helper module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# Reuse the already reviewed PC two-table G1N append implementation.  It is
# imported as source and never causes a stock archive to be written.
V6 = load_module(
    "nobu16_font_seoulhangang_v1_v6base",
    PATCH_ROOT / "workstreams" / "font_v6" / "build_font_v6.py",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_cp(codepoint: int) -> str:
    return f"U+{codepoint:04X}"


def canonical_codepoint_hash(codepoints: Iterable[int]) -> str:
    return sha256_bytes(
        "".join(f"{canonical_cp(codepoint)}\\n" for codepoint in sorted(codepoints)).encode("ascii")
    )


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    casefolded: set[str] = set()
    for key, value in pairs:
        folded = key.casefold()
        if key in result or folded in casefolded:
            raise FontBuildError(f"duplicate/case-colliding JSON key: {key!r}")
        result[key] = value
        casefolded.add(folded)
    return result


def loads_json_strict(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FontBuildError(f"{label}: invalid UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise FontBuildError(f"{label}: top-level JSON must be an object")
    return value


def _require_source_free_policy(overlay: dict[str, Any], label: str) -> None:
    policy = overlay.get("distribution_policy")
    if isinstance(policy, dict):
        if policy.get("contains_commercial_source_text") is not False:
            raise FontBuildError(f"{label}: commercial source text is not explicitly excluded")
        if policy.get("contains_complete_game_resource") is not False:
            raise FontBuildError(f"{label}: complete game resource is not explicitly excluded")
        return
    # The reviewed castle-name overlay predates the common overlay schema.  It
    # makes the same safety claim under its schema-specific field instead.
    if overlay.get("source_text_free") is not True:
        raise FontBuildError(f"{label}: missing source-free distribution declaration")


def canonical_json_hash(value: Any) -> str:
    return sha256_bytes(
        json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )


def _safe_project_relative_path(value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise FontBuildError(f"{label}: expected a nonempty relative path")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise FontBuildError(f"{label}: path escapes the project root")
    return path


def _overlay_resource(overlay: dict[str, Any], label: str) -> str:
    direct = overlay.get("resource")
    if isinstance(direct, str):
        return direct
    target = overlay.get("target")
    if isinstance(target, dict) and isinstance(target.get("resource"), str):
        return str(target["resource"])
    raise FontBuildError(f"{label}: overlay has no declared target resource")


def _expected_overlay_resource(progress_resource: str) -> set[str]:
    # msgui v0.2 predates the full logical-path convention.  Every other PK
    # overlay must name the exact progress resource it serves.
    if progress_resource == "MSG_PK/SC/msgui.bin":
        return {"msgui", progress_resource}
    return {progress_resource}


def _validate_ko_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or "\x00" in value:
        raise FontBuildError(f"{label}: ko must be nonempty text without NUL")
    if not unicodedata.is_normalized("NFC", value):
        raise FontBuildError(f"{label}: ko must be NFC-normalized")
    return value


def _contains_forbidden_script(text: str) -> bool:
    return any(
        0x3040 <= ord(char) <= 0x30FF
        or 0x31F0 <= ord(char) <= 0x31FF
        or 0x3400 <= ord(char) <= 0x4DBF
        or 0x4E00 <= ord(char) <= 0x9FFF
        or 0xF900 <= ord(char) <= 0xFAFF
        or 0xFF66 <= ord(char) <= 0xFF9F
        for char in text
    )


def renderable_characters(text: str, label: str) -> set[int]:
    """Return the BMP glyph demand while excluding game control/icon tokens."""

    consumed = {
        index
        for match in ESC_COMMAND_RE.finditer(text)
        for index in range(match.start(), match.end())
    }
    malformed = [
        index for index, char in enumerate(text) if char == "\x1b" and index not in consumed
    ]
    if malformed:
        raise FontBuildError(f"{label}: malformed ESC command")

    result: set[int] = set()
    for index, char in enumerate(text):
        codepoint = ord(char)
        if index in consumed or char.isspace():
            continue
        if codepoint < 0x20 or 0x7F <= codepoint <= 0x9F:
            continue
        if 0xE000 <= codepoint <= 0xF8FF:
            continue
        if codepoint > 0xFFFF:
            raise FontBuildError(f"{label}: non-BMP glyph {canonical_cp(codepoint)} is unsupported by G1N")
        if _contains_forbidden_script(char):
            raise FontBuildError(
                f"{label}: forbidden CJK ideograph or kana {canonical_cp(codepoint)} in Korean overlay"
            )
        result.add(codepoint)
    return result


def load_default_overlay_demand() -> dict[str, Any]:
    """Collect every current PK-loaded public overlay through a pinned progress map.

    The old four-source list covered MSGUI and only the then-registered Switch transfers but
    excluded approved Korean overlays in the other PK message resources.  A
    full font candidate must cover the same seven PK resources plus the exact
    shared ``MSG/SC/strdata.bin`` resource reported by
    ``translation_progress.v0.1.json``.  No other base-game message path is
    accepted.  The progress file and the derived
    source-hash catalog are both pinned in ``manifest.v1.json``: changing an
    overlay, its order, or the configured PK scope therefore fails closed
    until the font demand is consciously reviewed and refreshed.
    """

    try:
        manifest = loads_json_strict(DEMAND_MANIFEST.read_bytes(), "font demand manifest")
    except OSError as exc:
        raise FontBuildError(f"cannot read font demand manifest: {exc}") from exc
    demand_pin = manifest.get("pinned_public_korean_demand")
    if not isinstance(demand_pin, dict):
        raise FontBuildError("font demand manifest has no pinned_public_korean_demand object")
    progress_pin = demand_pin.get("translation_progress")
    if not isinstance(progress_pin, dict):
        raise FontBuildError("font demand manifest has no translation_progress pin")
    if progress_pin.get("path") != PROGRESS_CONFIG_RELATIVE:
        raise FontBuildError("font demand manifest has an unexpected translation-progress path")

    progress_path = PATCH_ROOT / PROGRESS_CONFIG_RELATIVE
    try:
        progress_raw = progress_path.read_bytes()
    except OSError as exc:
        raise FontBuildError(f"cannot read translation progress: {exc}") from exc
    progress_hash = sha256_bytes(progress_raw)
    if progress_pin.get("sha256") != progress_hash:
        raise FontBuildError(
            "translation progress SHA-256 changed; refresh the font-demand pin before building"
        )
    progress = loads_json_strict(progress_raw, PROGRESS_CONFIG_RELATIVE)
    resources = progress.get("resources")
    if not isinstance(resources, list):
        raise FontBuildError("translation progress resources must be an array")
    shared_resources = progress.get("shared_strings")
    if not isinstance(shared_resources, list):
        raise FontBuildError("translation progress shared_strings must be an array")

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
        raise FontBuildError(
            "translation progress must contain the seven PK string resources in canonical order"
        )
    if shared_paths != EXPECTED_SHARED_RESOURCES or len(shared_string_rows) != len(shared_resources):
        raise FontBuildError(
            "translation progress shared_strings must contain only MSG/SC/strdata.bin"
        )

    all_codepoints: set[int] = set()
    source_rows: list[dict[str, Any]] = []
    resource_rows: list[dict[str, Any]] = []
    seen_overlays: set[Path] = set()
    total_entries = 0

    for resource_row in core_string_rows + shared_string_rows:
        progress_resource = resource_row.get("path")
        overlay_paths = resource_row.get("overlay_globs")
        if not isinstance(progress_resource, str) or not isinstance(overlay_paths, list):
            raise FontBuildError("font string resource has an invalid path or overlay list")
        if progress_resource not in EXPECTED_FONT_RESOURCES:
            raise FontBuildError(
                f"resource outside the PK font-demand scope: {progress_resource!r}"
            )
        if not overlay_paths:
            raise FontBuildError(f"font string resource has no public overlays: {progress_resource}")

        resource_sources: list[dict[str, Any]] = []
        resource_entries = 0
        for logical_path in overlay_paths:
            relative = _safe_project_relative_path(logical_path, progress_resource)
            path = (PATCH_ROOT / relative).resolve()
            if PATCH_ROOT.resolve() not in path.parents:
                raise FontBuildError(f"{logical_path}: resolved outside project root")
            if path in seen_overlays:
                raise FontBuildError(f"overlay is listed more than once: {logical_path}")
            seen_overlays.add(path)
            if not path.is_file():
                raise FontBuildError(f"missing pinned public overlay: {logical_path}")
            raw = path.read_bytes()
            actual_hash = sha256_bytes(raw)
            overlay = loads_json_strict(raw, logical_path)
            _require_source_free_policy(overlay, logical_path)
            schema = overlay.get("schema")
            if not isinstance(schema, str) or not schema:
                raise FontBuildError(f"{logical_path}: overlay has no schema")
            actual_resource = _overlay_resource(overlay, logical_path)
            if actual_resource not in _expected_overlay_resource(progress_resource):
                raise FontBuildError(
                    f"{logical_path}: resource {actual_resource!r} does not serve {progress_resource!r}"
                )
            entries = overlay.get("entries")
            if not isinstance(entries, list) or not entries:
                raise FontBuildError(f"{logical_path}: entries must be a nonempty array")
            declared_count = overlay.get("entry_count")
            if declared_count is not None and declared_count != len(entries):
                raise FontBuildError(f"{logical_path}: entry_count does not match entries")

            local_codepoints: set[int] = set()
            for index, entry in enumerate(entries):
                if not isinstance(entry, dict) or "ko" not in entry:
                    raise FontBuildError(f"{logical_path}: entries[{index}] has no Korean output")
                text = _validate_ko_text(entry["ko"], f"{logical_path}: entries[{index}]")
                local_codepoints.update(renderable_characters(text, f"{logical_path}: entries[{index}]"))
            source = {
                "path": relative.as_posix(),
                "sha256": actual_hash,
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
                "source_catalog_sha256": canonical_json_hash(resource_sources),
            }
        )

    if not source_rows:
        raise FontBuildError("translation progress contains no PK-loaded string overlays")
    expected_resources = demand_pin.get("resource_catalog")
    if expected_resources != resource_rows:
        raise FontBuildError("font resource catalog changed; refresh the font-demand pin before building")
    if demand_pin.get("source_count") != len(source_rows):
        raise FontBuildError("font source count changed; refresh the font-demand pin before building")
    if demand_pin.get("source_entry_count") != total_entries:
        raise FontBuildError("font source entry count changed; refresh the font-demand pin before building")
    if demand_pin.get("source_catalog_sha256") != canonical_json_hash(source_rows):
        raise FontBuildError("font source catalog changed; refresh the font-demand pin before building")

    # Keep a source row per file in the plan so an offline reviewer can
    # identify every Korean corpus input without exporting any game strings.
    # Each row contains only project paths, hashes, schemas, and counts.
    ordered = sorted(all_codepoints)
    hangul = [codepoint for codepoint in ordered if 0xAC00 <= codepoint <= 0xD7A3]
    hangul_set = set(hangul)
    non_hangul = [codepoint for codepoint in ordered if codepoint not in hangul_set]
    if not hangul:
        raise FontBuildError("pinned Korean overlays contain no Hangul syllables")
    glyph_demand_metrics = {
        "codepoint_count": len(ordered),
        "codepoints_sha256": canonical_codepoint_hash(ordered),
        "hangul_syllable_count": len(hangul),
        "hangul_syllables_sha256": canonical_codepoint_hash(hangul),
        "non_hangul_count": len(non_hangul),
        "non_hangul_sha256": canonical_codepoint_hash(non_hangul),
    }
    for key, actual in glyph_demand_metrics.items():
        if demand_pin.get(key) != actual:
            raise FontBuildError(
                f"glyph-demand {key} changed; refresh the font-demand pin before building"
            )
    append_contract_pin = demand_pin.get("append_contract")
    if not isinstance(append_contract_pin, list):
        raise FontBuildError("font demand manifest has no append contract")
    raster_count_pin = demand_pin.get("raster_codepoint_count")
    raster_hash_pin = demand_pin.get("raster_codepoints_sha256")
    if not isinstance(raster_count_pin, int) or not isinstance(raster_hash_pin, str):
        raise FontBuildError("font demand manifest has no raster-demand pin")
    return {
        "schema": "nobu16.kr.font-seoulhangang-v1-demand.v1",
        "translation_progress": {
            "path": PROGRESS_CONFIG_RELATIVE,
            "sha256": progress_hash,
        },
        "source_catalog_sha256": canonical_json_hash(source_rows),
        "resource_catalog": resource_rows,
        "sources": source_rows,
        "source_count": len(source_rows),
        "source_entry_count": total_entries,
        **glyph_demand_metrics,
        "codepoints": ordered,
        "hangul": hangul,
        "non_hangul": non_hangul,
        "_pinned_append_contract": append_contract_pin,
        "_pinned_raster_codepoint_count": raster_count_pin,
        "_pinned_raster_codepoints_sha256": raster_hash_pin,
    }

def require_stock_archive(path: Path) -> bytes:
    if not path.is_file():
        raise FontBuildError(f"missing stock RES_SC archive: {path}")
    digest = sha256_file(path)
    if digest != STOCK_SC_SHA256:
        raise FontBuildError(
            f"stock RES_SC SHA-256 mismatch: expected={STOCK_SC_SHA256} actual={digest}"
        )
    return path.read_bytes()


def build_plan(stock_blob: bytes, demand: dict[str, Any]) -> dict[str, Any]:
    _stock_entries, coverage, append_plan = V6.preflight_stock(
        stock_blob, list(demand["hangul"]), list(demand["non_hangul"])
    )
    raster_codepoints = sorted(
        {
            codepoint
            for entry_plan in append_plan.values()
            for table_plan in entry_plan.values()
            for codepoint in table_plan
        }
    )
    if not set(demand["hangul"]).issubset(raster_codepoints):
        raise FontBuildError("all demanded Hangul must be appended to every G1N profile")
    if not raster_codepoints:
        raise FontBuildError("empty font append plan")

    append_summary = []
    for entry in (6, 7):
        for table in (0, 1):
            points = append_plan[entry][table]
            append_summary.append(
                {
                    "entry": entry,
                    "table": table,
                    "count": len(points),
                    "codepoints_sha256": canonical_codepoint_hash(points),
                }
            )
    if demand["_pinned_append_contract"] != append_summary:
        raise FontBuildError("G1N append contract changed; refresh the font-demand pin before building")
    raster_hash = canonical_codepoint_hash(raster_codepoints)
    if demand["_pinned_raster_codepoint_count"] != len(raster_codepoints):
        raise FontBuildError("raster glyph count changed; refresh the font-demand pin before building")
    if demand["_pinned_raster_codepoints_sha256"] != raster_hash:
        raise FontBuildError("raster glyph catalog changed; refresh the font-demand pin before building")
    return {
        "schema": "nobu16.kr.font-seoulhangang-v1-plan.v1",
        "file_only": True,
        "installed_game_files_modified": False,
        "process_memory_access": False,
        "registry_access": False,
        "stock_archive": {
            "path": "RES_SC/res_lang.bin",
            "sha256": sha256_bytes(stock_blob),
            "size": len(stock_blob),
        },
        "demand": {
            key: value
            for key, value in demand.items()
            if key not in {"codepoints", "hangul", "non_hangul"} and not key.startswith("_pinned_")
        },
        "raster_codepoint_count": len(raster_codepoints),
        "raster_codepoints_sha256": raster_hash,
        # Codepoints are source-free metadata.  Keeping the complete demand in
        # the private plan lets the independent verifier prove that every
        # configured PK overlay glyph maps in every runtime G1N table.
        "glyph_demand_codepoints": list(demand["codepoints"]),
        "glyph_demand_codepoints_sha256": canonical_codepoint_hash(demand["codepoints"]),
        "append_contract": append_summary,
        "stock_coverage": coverage,
        "font": {
            "family": SEOUL_HANGANG_M_FAMILY,
            "file_name": "SeoulHangangM.ttf",
            "sha256": SEOUL_HANGANG_M_SHA256,
            "size": SEOUL_HANGANG_M_SIZE,
            "official_archive_url": OFFICIAL_ARCHIVE_URL,
            "official_archive_sha256": OFFICIAL_ARCHIVE_SHA256,
        },
        "raster_codepoints": raster_codepoints,
        "append_plan": {
            str(entry): {str(table): append_plan[entry][table] for table in (0, 1)}
            for entry in (6, 7)
        },
    }


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def validate_output_root(output_root: Path, protected: Sequence[Path]) -> None:
    resolved = output_root.resolve()
    workspace = PATCH_ROOT.resolve()
    game_root = GAME_ROOT.resolve()
    local_tmp = (PATCH_ROOT / "tmp").resolve()

    # An output below the game tree is safe only when it is a child of this
    # workspace's ignored tmp directory.  This rules out a typo such as a
    # live ``RES_SC`` destination while still allowing an explicit external
    # scratch drive.  The tmp root itself is not a build root: it would make
    # its contents look like one candidate and makes the empty-root contract
    # too broad.
    in_workspace_tmp = local_tmp in resolved.parents
    if resolved in (workspace, game_root, SCRIPT_DIR.resolve(), local_tmp):
        raise FontBuildError(f"unsafe output root: {resolved}")
    if game_root in resolved.parents and not in_workspace_tmp:
        raise FontBuildError(
            f"output root inside the game tree must be below {local_tmp}: {resolved}"
        )
    for source in protected:
        source_path = source.resolve()
        if (
            resolved == source_path
            or source_path in resolved.parents
            or resolved in source_path.parents
        ):
            raise FontBuildError(f"output root overlaps an input: {resolved}")
    if resolved.exists() and any(resolved.iterdir()):
        raise FontBuildError(f"output root must be absent or empty: {resolved}")


def raster_request(font_path: Path, raster_codepoints: Sequence[int]) -> dict[str, Any]:
    return {
        "schema": "nobu16.kr.font-seoulhangang-v1-raster-request.v1",
        "font": {
            "path": str(font_path),
            "sha256": SEOUL_HANGANG_M_SHA256,
            "family": SEOUL_HANGANG_M_FAMILY,
        },
        "codepoints": [canonical_cp(codepoint) for codepoint in raster_codepoints],
        "profiles": list(PROFILES),
    }


def run_rasterizer(powershell: Path, request_path: Path, output_root: Path) -> dict[str, Any]:
    helper = SCRIPT_DIR / "rasterize_seoulhangang_v1.ps1"
    command = [
        str(powershell),
        "-NoProfile",
        "-NonInteractive",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(helper),
        "-RequestPathInput",
        str(request_path),
        "-OutputDirectory",
        str(output_root),
    ]
    completed = subprocess.run(
        command,
        cwd=PATCH_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        raise FontBuildError(
            "SeoulHangang rasterizer failed\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
    result_path = output_root / "raster_result.json"
    try:
        return loads_json_strict(result_path.read_bytes(), "raster result")
    except OSError as exc:
        raise FontBuildError(f"rasterizer did not produce a result: {exc}") from exc


def validate_raster_result(
    result: dict[str, Any], raster_root: Path, expected_codepoints: Sequence[int]
) -> dict[int, bytes]:
    expected = [canonical_cp(codepoint) for codepoint in expected_codepoints]
    if result.get("schema") != "nobu16.kr.font-seoulhangang-v1-raster-result.v1":
        raise FontBuildError("unsupported raster result schema")
    if result.get("codepoints") != expected:
        raise FontBuildError("raster result codepoint order mismatch")
    payload_descriptors = result.get("payloads")
    if not isinstance(payload_descriptors, list):
        raise FontBuildError("raster result payloads must be a list")
    payloads: dict[int, bytes] = {}
    for item in payload_descriptors:
        if not isinstance(item, dict):
            raise FontBuildError("invalid raster payload descriptor")
        entry = item.get("entry")
        if entry not in (6, 7) or entry in payloads:
            raise FontBuildError("raster result entry set is invalid")
        expected_name = f"glyph_pixels_entry_{entry}.pixels"
        if item.get("path") != expected_name:
            raise FontBuildError(f"entry {entry}: raster payload path is not canonical")
        payload_path = raster_root / expected_name
        data = payload_path.read_bytes()
        cell = 48 if entry == 6 else 32
        expected_size = 2 * len(expected_codepoints) * (cell // 2) * cell
        if len(data) != expected_size or item.get("size") != expected_size:
            raise FontBuildError(f"entry {entry}: raster payload size mismatch")
        if sha256_bytes(data) != item.get("sha256"):
            raise FontBuildError(f"entry {entry}: raster payload hash mismatch")
        payloads[entry] = data
    if set(payloads) != {6, 7}:
        raise FontBuildError("raster result must have entries 6 and 7")
    profiles = result.get("profiles")
    if not isinstance(profiles, list) or len(profiles) != 4:
        raise FontBuildError("raster result must have four profiles")
    expected_profiles = [
        (profile["entry"], profile["table"], profile["family"], profile["style"], profile["raster_size"], profile["cell"])
        for profile in PROFILES
    ]
    actual_profiles = []
    for profile in profiles:
        if not isinstance(profile, dict):
            raise FontBuildError("raster profile descriptor is invalid")
        actual_profiles.append(
            (
                profile.get("entry"),
                profile.get("table"),
                profile.get("family"),
                profile.get("style"),
                profile.get("raster_size"),
                profile.get("cell"),
            )
        )
    if actual_profiles != expected_profiles:
        raise FontBuildError("raster profile geometry does not match the PC G1N contract")

    for profile in profiles:
        glyphs = profile.get("glyphs")
        if not isinstance(glyphs, list) or len(glyphs) != len(expected_codepoints):
            raise FontBuildError("raster profile glyph count mismatch")
        entry = int(profile["entry"])
        table = int(profile["table"])
        cell = int(profile["cell"])
        pixel_size = (cell // 2) * cell
        offset = table * len(expected_codepoints) * pixel_size
        pixel_blob = payloads[entry]
        for index, glyph in enumerate(glyphs):
            if not isinstance(glyph, dict):
                raise FontBuildError("raster glyph descriptor is invalid")
            if glyph.get("codepoint") != expected[index]:
                raise FontBuildError("raster glyph codepoint order mismatch")
            pixels = pixel_blob[offset + index * pixel_size : offset + (index + 1) * pixel_size]
            if len(pixels) != pixel_size or glyph.get("pixel_size") != pixel_size:
                raise FontBuildError("raster glyph pixel size mismatch")
            if glyph.get("pixel_sha256") != sha256_bytes(pixels):
                raise FontBuildError("raster glyph pixel hash mismatch")
            if int(glyph.get("ink_count", 0)) <= 0:
                raise FontBuildError("raster profile contains a blank glyph")
            if int(glyph.get("minimum_margin", 0)) < 1:
                raise FontBuildError("raster profile has a glyph touching its cell edge")
    return payloads


def require_official_font(path: Path) -> None:
    if not path.is_file():
        raise FontBuildError(f"official SeoulHangang M TTF is missing: {path}")
    if path.stat().st_size != SEOUL_HANGANG_M_SIZE:
        raise FontBuildError("SeoulHangang M TTF size does not match the official pin")
    actual = sha256_file(path)
    if actual != SEOUL_HANGANG_M_SHA256:
        raise FontBuildError(
            f"SeoulHangang M TTF SHA-256 mismatch: expected={SEOUL_HANGANG_M_SHA256} actual={actual}"
        )


def private_build(
    stock_blob: bytes,
    font_path: Path,
    plan: dict[str, Any],
    output_root: Path,
    powershell: Path,
) -> dict[str, Any]:
    require_official_font(font_path)
    raster_points = [int(value) for value in plan["raster_codepoints"]]
    request_path = output_root / "private" / "raster_request.json"
    raster_root = output_root / "private" / "raster"
    atomic_write(request_path, encode_json(raster_request(font_path, raster_points)))
    raster_result = run_rasterizer(powershell, request_path, raster_root)
    full_pixels = validate_raster_result(raster_result, raster_root, raster_points)

    stock_archive = V6.BASE.LZ4.parse_link(stock_blob)
    if V6.BASE.LZ4.rebuild_link(stock_archive) != stock_blob:
        raise FontBuildError("stock LINK parse/rebuild identity failed")
    candidates: dict[int, bytes] = {}
    entry_recipes: dict[str, Any] = {}
    entry_validation: list[dict[str, Any]] = []
    for entry in (6, 7):
        stock_entry = V6.BASE.extract_raw_entry(stock_archive, entry, f"SC stock entry {entry}")
        table_plan = {
            table: [int(value) for value in plan["append_plan"][str(entry)][str(table)]]
            for table in (0, 1)
        }
        candidate, recipe, validation, _unused_public_pixels = V6.build_entry(
            stock_entry, full_pixels[entry], entry, raster_points, table_plan
        )
        candidates[entry] = candidate
        entry_recipes[str(entry)] = recipe
        entry_validation.append(validation)
        atomic_write(output_root / "private" / "candidate" / f"SC_{entry}.seoulhangang-v1.g1n", candidate)

    candidate_archive = V6.BASE.build_candidate_archive(stock_blob, candidates)
    parsed = V6.BASE.LZ4.parse_link(candidate_archive)
    if V6.BASE.LZ4.rebuild_link(parsed) != candidate_archive:
        raise FontBuildError("candidate LINK parse/rebuild identity failed")
    for index, stock_entry in enumerate(stock_archive.entries):
        if index in (6, 7):
            rebuilt = V6.BASE.extract_raw_entry(parsed, index, f"SC candidate entry {index}")
            if rebuilt != candidates[index]:
                raise FontBuildError(f"candidate entry {index} re-extraction mismatch")
        elif parsed.entries[index].data != stock_entry.data:
            raise FontBuildError(f"candidate changed untouched LINK entry {index}")
    archive_path = output_root / "private" / "candidate" / "res_lang.SC.seoulhangang-v1.bin"
    atomic_write(archive_path, candidate_archive)

    build_manifest = {
        "schema": "nobu16.kr.font-seoulhangang-v1-private-build.v1",
        "file_only": True,
        "installed_game_files_modified": False,
        "process_memory_access": False,
        "registry_access": False,
        "distribution": {
            "official_ttf_included": False,
            "seoulhangang_raster_payload_included": False,
            "stock_g1n_or_link_included": False,
            "complete_candidate_publicly_distributable": False,
        },
        "stock_archive_sha256": sha256_bytes(stock_blob),
        "font": {
            "file_name": font_path.name,
            "sha256": sha256_file(font_path),
            "family": SEOUL_HANGANG_M_FAMILY,
        },
        "plan_sha256": sha256_bytes(encode_json(plan)),
        "raster_result_sha256": sha256_file(raster_root / "raster_result.json"),
        "candidate_archive": {
            "path": "private/candidate/res_lang.SC.seoulhangang-v1.bin",
            "sha256": sha256_bytes(candidate_archive),
            "size": len(candidate_archive),
        },
        "entries": [
            {
                "entry": entry,
                "sha256": sha256_bytes(candidates[entry]),
                "size": len(candidates[entry]),
            }
            for entry in (6, 7)
        ],
        "entry_recipes": entry_recipes,
        "entry_validation": entry_validation,
    }
    atomic_write(output_root / "private" / "build_manifest.json", encode_json(build_manifest))
    return build_manifest


def command_plan(args: argparse.Namespace) -> int:
    stock_path = Path(args.stock_archive).resolve()
    output_root = Path(args.output_root).resolve()
    validate_output_root(output_root, (stock_path,))
    stock_blob = require_stock_archive(stock_path)
    plan = build_plan(stock_blob, load_default_overlay_demand())
    output_root.mkdir(parents=True, exist_ok=True)
    atomic_write(output_root / "plan.json", encode_json(plan))
    print(f"plan={output_root / 'plan.json'}")
    print(f"raster_codepoints={plan['raster_codepoint_count']}")
    print(f"hangul={plan['demand']['hangul_syllable_count']}")
    print("installed_game_files_modified=False")
    return 0


def command_build(args: argparse.Namespace) -> int:
    stock_path = Path(args.stock_archive).resolve()
    font_path = Path(args.font).resolve()
    powershell = Path(args.powershell).resolve()
    output_root = Path(args.output_root).resolve()
    if not powershell.is_file():
        raise FontBuildError(f"PowerShell executable is missing: {powershell}")
    validate_output_root(output_root, (stock_path, font_path))
    stock_blob = require_stock_archive(stock_path)
    plan = build_plan(stock_blob, load_default_overlay_demand())
    output_root.mkdir(parents=True, exist_ok=True)
    atomic_write(output_root / "plan.json", encode_json(plan))
    result = private_build(stock_blob, font_path, plan, output_root, powershell)
    print(f"private_manifest={output_root / 'private' / 'build_manifest.json'}")
    print(f"candidate_sha256={result['candidate_archive']['sha256']}")
    print("installed_game_files_modified=False")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("plan", "validate the pinned Korean corpus and write a source-free append plan"),
        ("build", "create a local private candidate from official SeoulHangang M"),
    ):
        command = subparsers.add_parser(name, help=help_text)
        command.add_argument("--stock-archive", type=Path, required=True)
        command.add_argument("--output-root", type=Path, required=True)
        if name == "build":
            command.add_argument("--font", type=Path, required=True)
            command.add_argument(
                "--powershell",
                type=Path,
                default=Path(os.environ.get("SystemRoot", r"C:\\Windows")) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe",
            )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "plan":
            return command_plan(args)
        return command_build(args)
    except (FontBuildError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
