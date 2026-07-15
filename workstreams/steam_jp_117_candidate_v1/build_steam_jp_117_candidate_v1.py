#!/usr/bin/env python3
"""Assemble the exact Steam PK 1.1.7 Japanese-route ten-file candidate."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Any, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = SCRIPT.parents[2]
TOOLS = REPO / "tools"
STRDATA_TOOLS = REPO / "workstreams" / "switch_msgbre_v11"
sys.path[:0] = [str(TOOLS), str(STRDATA_TOOLS)]

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from strdata_container import parse_strdata, rebuild_strdata  # noqa: E402


STEAM_ROOT = Path(r"F:/SteamLibrary/steamapps/common/NOBU16")
STEAM_PK_VERSION = "1.1.7"
STEAM_BUILD_ID = 18_823_764
SCHEMA = "nobu16.kr.steam-jp-1.1.7-candidate-manifest.v1"
VERIFICATION_SCHEMA = "nobu16.kr.steam-jp-1.1.7-candidate-verification.v1"
VERIFICATION_PATH = WORKSTREAM / "verification.v1.json"
DEFAULT_ZIP_NAME = "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.6.0.zip"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import component: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


MSGGAME = load_module(
    "nobu16_steam_jp_117_msggame",
    REPO / "workstreams" / "steam_jp_msggame_v1" / "build_steam_jp_msggame_v1.py",
)
MSGUI = load_module(
    "nobu16_steam_jp_117_msgui",
    REPO / "workstreams" / "steam_jp_msgui_v1" / "build_steam_jp_msgui_v1.py",
)
COMMON = load_module(
    "nobu16_steam_jp_117_common",
    REPO
    / "workstreams"
    / "steam_jp_common_messages_v1"
    / "build_steam_jp_common_messages_v1.py",
)
RUNTIME = load_module(
    "nobu16_steam_jp_117_runtime",
    REPO
    / "workstreams"
    / "steam_jp_runtime_skeleton_v1"
    / "build_steam_jp_runtime_skeleton_v1.py",
)


TARGETS = tuple(sorted(RUNTIME.TARGETS))
EXPECTED_TARGETS = (
    "MSG/JP/strdata.bin",
    "MSG_PK/JP/msgbre.bin",
    "MSG_PK/JP/msgdata.bin",
    "MSG_PK/JP/msgev.bin",
    "MSG_PK/JP/msggame.bin",
    "MSG_PK/JP/msgire.bin",
    "MSG_PK/JP/msgstf.bin",
    "MSG_PK/JP/msgui.bin",
    "RES_JP/res_lang.bin",
    "RES_JP_PK/res_lang_pk.bin",
)
if TARGETS != EXPECTED_TARGETS:
    raise RuntimeError("runtime ten-file target vector changed")


class CandidateError(RuntimeError):
    pass


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def file_spec(path: Path) -> dict[str, Any]:
    return {"size": path.stat().st_size, "sha256": sha256_path(path)}


def bytes_spec(blob: bytes) -> dict[str, Any]:
    return {"size": len(blob), "sha256": sha256(blob)}


def json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def predecessor_vector(steam_root: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for relative in TARGETS:
        path = steam_root / Path(relative)
        actual = file_spec(path)
        expected = RUNTIME.TARGETS[relative]
        if actual != expected:
            raise CandidateError(
                f"Steam 1.1.7 predecessor mismatch: {relative}: {actual} != {expected}"
            )
        result[relative] = actual
    return result


def build_strdata(steam_root: Path) -> tuple[bytes, dict[str, Any]]:
    overlay_path = (
        REPO
        / "workstreams"
        / "steam_jp_runtime_skeleton_v1"
        / "public"
        / "strdata_ko_jp_source_rebased_24524.v1.json"
    )
    overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
    packed = (steam_root / RUNTIME.STRDATA_RESOURCE).read_bytes()
    wrapper, raw = decompress_wrapper(packed)
    archive = parse_strdata(raw)
    replacements = {block.block_id: list(block.texts) for block in archive.blocks}
    seen: set[tuple[int, int]] = set()
    for entry in overlay["entries"]:
        coordinate = (int(entry["block_id"]), int(entry["slot_id"]))
        if coordinate in seen:
            raise CandidateError(f"duplicate strdata coordinate: {coordinate}")
        seen.add(coordinate)
        source = archive.blocks[coordinate[0]].texts[coordinate[1]]
        if entry["source_jp_utf16le_sha256"] != RUNTIME.text_hash(source):
            raise CandidateError(f"strdata JP source hash mismatch: {coordinate}")
        failures = RUNTIME.replacement_failures(source, entry["ko"])
        if failures:
            raise CandidateError(f"strdata invariant mismatch {coordinate}: {failures}")
        replacements[coordinate[0]][coordinate[1]] = entry["ko"]
    candidate_raw = rebuild_strdata(archive, replacements)
    candidate = recompress_wrapper(candidate_raw, wrapper)
    expected = RUNTIME.build_strdata(steam_root)[2]
    observed = {
        "packed_size": len(candidate),
        "packed_sha256": sha256(candidate),
        "raw_size": len(candidate_raw),
        "raw_sha256": sha256(candidate_raw),
        "changed_coordinate_count": len(seen),
    }
    if observed != expected:
        raise CandidateError(f"strdata candidate pin mismatch: {observed} != {expected}")
    return candidate, {
        "builder": "steam_jp_runtime_skeleton_v1",
        "applied_entries": len(seen),
        "candidate": bytes_spec(candidate),
    }


def build_msgui(steam_root: Path) -> tuple[bytes, dict[str, Any]]:
    _contract, entries, _overlay_blob = MSGUI.load_frozen_inputs(MSGUI.DEFAULT_CONTRACT)
    _path, packed, raw, table = MSGUI.load_stock(steam_root)
    candidate, candidate_raw, changed = MSGUI.candidate_from_entries(
        packed, raw, table, entries
    )
    expected = _contract["expected_candidate"]
    observed = {
        "packed_size": len(candidate),
        "packed_sha256": sha256(candidate),
        "raw_size": len(candidate_raw),
        "raw_sha256": sha256(candidate_raw),
        "string_count": MSGUI.STOCK_STRING_COUNT,
    }
    if observed != expected:
        raise CandidateError(f"msgui candidate pin mismatch: {observed} != {expected}")
    return candidate, {
        "builder": "steam_jp_msgui_v1",
        "mapped_entries": len(entries),
        "effective_changes": len(changed),
        "unmapped_entries": _contract["overlay"]["unmapped_entry_count"],
        "candidate": bytes_spec(candidate),
    }


def build_common(steam_root: Path) -> tuple[dict[str, bytes], dict[str, Any]]:
    overlays, _blobs = COMMON.load_public_overlays()
    candidates, metrics = COMMON.build_all(steam_root, overlays)
    validation, _raw = COMMON.read_json(COMMON.VALIDATION_PATH)
    expected = validation["candidate_hashes"]
    observed = {
        name: {"size": len(candidates[name]), "sha256": sha256(candidates[name])}
        for name in COMMON.FILES
    }
    if observed != expected:
        raise CandidateError("common-message candidate pins changed")
    return candidates, {
        "builder": "steam_jp_common_messages_v1",
        "applied_entries": sum(int(row["applied_count"]) for row in metrics),
        "unresolved_entries": sum(int(row["unresolved_count"]) for row in metrics),
        "candidates": observed,
    }


def build_msggame(steam_root: Path) -> tuple[bytes, dict[str, Any]]:
    stock = (steam_root / Path(MSGGAME.RESOURCE)).read_bytes()
    candidate, manifest = MSGGAME.build_blob(stock, MSGGAME.default_overlay_specs())
    expected = json.loads(
        (REPO / "workstreams" / "steam_jp_msggame_v1" / "verification.v1.json").read_text(
            encoding="utf-8"
        )
    )
    if manifest != expected:
        raise CandidateError("msggame verification manifest changed")
    return candidate, {
        "builder": "steam_jp_msggame_v1",
        "applied_entries": manifest["translation"]["applied_entry_count"],
        "remaining_jp_semantic": manifest["translation"]["remaining_jp_semantic_count"],
        "candidate": bytes_spec(candidate),
    }


def require_output_root(path: Path) -> Path:
    resolved = path.resolve()
    tmp_root = (REPO / "tmp").resolve()
    if resolved == tmp_root or tmp_root not in resolved.parents:
        raise CandidateError(f"output must be below repository tmp: {resolved}")
    if resolved.exists():
        raise CandidateError(f"output already exists: {resolved}")
    return resolved


def write_candidate_file(root: Path, relative: str, blob: bytes) -> dict[str, Any]:
    target = root / Path(relative)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(blob)
    if target.read_bytes() != blob:
        raise CandidateError(f"written candidate differs: {relative}")
    return bytes_spec(blob)


def copy_candidate_file(root: Path, relative: str, source: Path) -> dict[str, Any]:
    target = root / Path(relative)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    return file_spec(target)


def candidate_files(root: Path) -> list[str]:
    return sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
    )


def make_zip(candidate_root: Path, destination: Path) -> dict[str, Any]:
    with zipfile.ZipFile(
        destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6
    ) as archive:
        for relative in TARGETS:
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (candidate_root / Path(relative)).read_bytes())
    with zipfile.ZipFile(destination) as archive:
        names = [item.filename for item in archive.infolist() if not item.is_dir()]
        if names != list(TARGETS):
            raise CandidateError(f"ZIP member vector differs: {names}")
        for relative in TARGETS:
            if sha256(archive.read(relative)) != sha256_path(candidate_root / Path(relative)):
                raise CandidateError(f"ZIP payload differs: {relative}")
    return file_spec(destination)


def build_all(steam_root: Path, output_root: Path, zip_name: str) -> dict[str, Any]:
    output_root = require_output_root(output_root)
    before = predecessor_vector(steam_root)
    candidate_root = output_root / "candidate"

    strdata, strdata_meta = build_strdata(steam_root)
    msgui, msgui_meta = build_msgui(steam_root)
    common, common_meta = build_common(steam_root)
    msggame, msggame_meta = build_msggame(steam_root)

    candidates: dict[str, dict[str, Any]] = {}
    candidates["MSG/JP/strdata.bin"] = write_candidate_file(
        candidate_root, "MSG/JP/strdata.bin", strdata
    )
    candidates["MSG_PK/JP/msgui.bin"] = write_candidate_file(
        candidate_root, "MSG_PK/JP/msgui.bin", msgui
    )
    for name, blob in common.items():
        relative = f"MSG_PK/JP/{name}"
        candidates[relative] = write_candidate_file(candidate_root, relative, blob)
    candidates["MSG_PK/JP/msggame.bin"] = write_candidate_file(
        candidate_root, "MSG_PK/JP/msggame.bin", msggame
    )
    for relative, route in RUNTIME.FONT_RESOURCES.items():
        source = RUNTIME.FONT_CANDIDATE_ROOT / Path(relative)
        observed = copy_candidate_file(candidate_root, relative, source)
        if observed != route["candidate"]:
            raise CandidateError(f"font candidate pin mismatch: {relative}")
        candidates[relative] = observed

    actual_paths = candidate_files(candidate_root)
    if actual_paths != list(TARGETS):
        raise CandidateError(f"candidate root is not exact: {actual_paths}")
    if set(candidates) != set(TARGETS):
        raise CandidateError("candidate manifest does not cover exact target vector")
    after = predecessor_vector(steam_root)
    if after != before:
        raise CandidateError("Steam predecessor vector changed during offline build")

    zip_path = output_root / zip_name
    zip_spec = make_zip(candidate_root, zip_path)
    manifest = {
        "schema": SCHEMA,
        "runtime": {
            "distribution": "Steam",
            "pk_version": STEAM_PK_VERSION,
            "steam_build_id": STEAM_BUILD_ID,
            "language_route": "JP",
        },
        "candidate_root": "candidate",
        "candidate_file_count": len(candidates),
        "candidate_paths": list(TARGETS),
        "predecessors": before,
        "candidates": {key: candidates[key] for key in TARGETS},
        "components": {
            "strdata": strdata_meta,
            "msgui": msgui_meta,
            "common_messages": common_meta,
            "msggame": msggame_meta,
            "fonts": {
                "builder": "font_jp_seoulhangang_v1",
                "routes": {
                    relative: candidates[relative]
                    for relative in RUNTIME.FONT_RESOURCES
                },
            },
        },
        "zip": {"name": zip_name, **zip_spec, "member_count": len(TARGETS)},
        "checks": {
            "steam_1_1_7_predecessors_exact": True,
            "jp_route_exact": True,
            "exact_ten_files": True,
            "component_candidate_pins_exact": True,
            "zip_payloads_equal_candidates": True,
            "sc_container_used": False,
            "memory_patch": False,
            "dll_injection": False,
            "hooking": False,
            "exe_or_registry_modified": False,
            "steam_files_written": False,
        },
    }
    projection = {
        "schema": VERIFICATION_SCHEMA,
        "runtime": manifest["runtime"],
        "candidate_file_count": manifest["candidate_file_count"],
        "candidate_paths": manifest["candidate_paths"],
        "candidates": manifest["candidates"],
        "translation": {
            "strdata_applied": strdata_meta["applied_entries"],
            "msgui_mapped": msgui_meta["mapped_entries"],
            "msgui_effective_changes": msgui_meta["effective_changes"],
            "msgui_unmapped": msgui_meta["unmapped_entries"],
            "common_messages_applied": common_meta["applied_entries"],
            "common_messages_unresolved": common_meta["unresolved_entries"],
            "msggame_applied": msggame_meta["applied_entries"],
            "msggame_remaining_jp_semantic": msggame_meta["remaining_jp_semantic"],
        },
        "zip": manifest["zip"],
        "checks": {
            "steam_1_1_7_predecessors_exact": True,
            "component_candidate_pins_exact": True,
            "exact_ten_files": True,
            "zip_payloads_equal_candidates": True,
            "sc_container_used": False,
            "steam_files_written": False,
        },
    }
    expected_projection = json.loads(VERIFICATION_PATH.read_text(encoding="utf-8"))
    if projection != expected_projection:
        raise CandidateError("integrated candidate differs from tracked verification pin")
    manifest_path = output_root / "candidate_manifest.v1.json"
    manifest_path.write_bytes(json_bytes(manifest))
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, default=STEAM_ROOT)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=REPO / "tmp" / "steam_jp_117_candidate_v1",
    )
    parser.add_argument(
        "--zip-name",
        default=DEFAULT_ZIP_NAME,
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest = build_all(args.steam_root.resolve(), args.output_root, args.zip_name)
    except (CandidateError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"status=PASS")
    print(f"steam_pk_version={manifest['runtime']['pk_version']}")
    print(f"steam_build_id={manifest['runtime']['steam_build_id']}")
    print(f"candidate_files={manifest['candidate_file_count']}")
    print(f"zip_sha256={manifest['zip']['sha256']}")
    print("steam_files_written=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
