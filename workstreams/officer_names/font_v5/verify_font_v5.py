#!/usr/bin/env python3
"""Verify two independent font-v5 builds and the tracked source-free release tree."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import struct
import sys
from pathlib import Path
from typing import Any, Iterable


sys.dont_write_bytecode = True
SCRIPT_DIR = Path(__file__).resolve().parent
GAME_ROOT = SCRIPT_DIR.parents[3]
PATCH_ROOT = GAME_ROOT / "KR_PATCH_WORK"
TMP_ROOT = PATCH_ROOT / "tmp"
DEFAULT_OVERLAY = PATCH_ROOT / "data" / "public" / "msgev_ko_officer_names_0000_2399.v0.1.json"
DEFAULT_OFFICER_DEMAND = SCRIPT_DIR / "corpus" / "msgev_officer_names_0000_2399" / "glyph_demand.json"
DEFAULT_MSGUI_DEMAND = SCRIPT_DIR / "corpus" / "msgui_0000_5099" / "glyph_demand.json"
DEFAULT_RELEASE_ROOT = SCRIPT_DIR
DEFAULT_OUTPUT = SCRIPT_DIR / "verification.json"
MSGUI_V4_DEMAND_SHA256 = "7DBF97C2AC889F2FB33856A1A8096A1DB091C4D25DB411E73E95E5D0FB7E0D16"
OFFICER_CODEPOINTS_SHA256 = "491F1A933DA51A426927DEFE247481CD3BBA8D57EDAD5C4482387528E19E94B8"
UNION_CODEPOINTS_SHA256 = "25B07F5B7943D33367C18ACC071747555363378AA19A979F11F94B7E882265A4"
EXPECTED_OFFICER_HANGUL_COUNT = 125
EXPECTED_UNION_CHARACTER_COUNT = 655
EXPECTED_UNION_HANGUL_COUNT = 554
EXPECTED_OFFICER_COUNT = 2207
EXPECTED_LONGEST = {
    239: "이타베오카 고세츠사이",
    1681: "히토츠야나기 나오모리",
    1885: "마츠다이라 다다아키라",
}
EXPECTED_FAMOUS = {
    106: "아츠지 사다유키",
    216: "이시다 미츠나리",
    558: "오다 노부나가",
}
EXPECTED_CORRECTED = {
    162: "안요지 우지타네",
    231: "이즈모노 오쿠니",
    516: "오카모토 겐이츠",
    1179: "조슌인",
    1302: "치지와 미게루",
    1584: "네고로 긴세키사이",
    1666: "반 단에몬",
    1674: "히코츠루",
    1739: "호조 겐안",
    1752: "호조인 인에이",
    1831: "마에다 겐이",
    2134: "유지 사다토키",
}
FORBIDDEN_RELEASE_SUFFIXES = {
    ".bin", ".g1n", ".g1t", ".ttf", ".dll", ".exe", ".pyc", ".bak", ".orig"
}
EXPECTED_PUBLIC_PAYLOAD_PATHS = {
    "licenses/OFL-NotoSansKR.txt",
    "licenses/OFL-NotoSerifKR.txt",
    "metrics/glyphs.jsonl",
    "payload/glyph_pixels_entry_6.pixels",
    "payload/glyph_pixels_entry_7.pixels",
}


class VerificationError(ValueError):
    """Raised when a font-v5 safety, coverage, or determinism gate fails."""


def load_builder() -> Any:
    path = SCRIPT_DIR / "build_font_v5.py"
    spec = importlib.util.spec_from_file_location("nobu16_officer_font_v5_verify", path)
    if spec is None or spec.loader is None:
        raise VerificationError(f"cannot load font-v5 builder: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = load_builder()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise VerificationError(f"{path}: expected a JSON object")
    return value


def atomic_write_json(path: Path, value: Any) -> None:
    data = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
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


def progress(message: str) -> None:
    """Emit a flushed stage marker so long-running archive checks are observable."""
    print(f"[verify-font-v5] {message}", file=sys.stderr, flush=True)


def canonical_lines(codepoints: Iterable[int]) -> bytes:
    return "".join(f"U+{codepoint:04X}\n" for codepoint in sorted(set(codepoints))).encode("ascii")


def parse_demand_codepoints(value: dict[str, Any], label: str) -> list[int]:
    rows = value.get("codepoints")
    if not isinstance(rows, list):
        raise VerificationError(f"{label}: codepoints must be an array")
    result: list[int] = []
    for item in rows:
        if not isinstance(item, str) or len(item) != 6 or not item.startswith("U+"):
            raise VerificationError(f"{label}: non-canonical codepoint {item!r}")
        try:
            result.append(int(item[2:], 16))
        except ValueError as exc:
            raise VerificationError(f"{label}: non-hex codepoint {item!r}") from exc
    if result != sorted(set(result)):
        raise VerificationError(f"{label}: codepoints are not unique and sorted")
    return result


def file_inventory(root: Path) -> list[dict[str, Any]]:
    if not root.is_dir():
        raise VerificationError(f"missing directory: {root}")
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "size": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted((item for item in root.rglob("*") if item.is_file()), key=lambda item: item.as_posix())
    ]


def inventory_hash(rows: list[dict[str, Any]]) -> str:
    return sha256_bytes(
        "".join(f"{row['path']}\t{row['size']}\t{row['sha256']}\n" for row in rows).encode("utf-8")
    )


def verify_recipe_payload_inventory(
    build_root: Path, recipe: dict[str, Any]
) -> dict[str, Any]:
    """Require exact recipe pins for every non-recipe public artifact."""
    rows = recipe.get("payload_inventory")
    if not isinstance(rows, list) or len(rows) != len(EXPECTED_PUBLIC_PAYLOAD_PATHS):
        raise VerificationError("font-v5 recipe must inventory exactly five public artifacts")

    by_path: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"origin", "path", "sha256", "size"}:
            raise VerificationError("font-v5 payload inventory row has unexpected properties")
        path = row.get("path")
        origin = row.get("origin")
        size = row.get("size")
        digest = row.get("sha256")
        if (
            not isinstance(path, str)
            or path in by_path
            or not isinstance(origin, str)
            or not origin.strip()
            or type(size) is not int
            or size < 0
            or not isinstance(digest, str)
            or len(digest) != 64
            or digest != digest.upper()
            or any(character not in "0123456789ABCDEF" for character in digest)
        ):
            raise VerificationError("font-v5 payload inventory row is not canonical")
        by_path[path] = row

    if set(by_path) != EXPECTED_PUBLIC_PAYLOAD_PATHS:
        raise VerificationError("font-v5 payload inventory has a missing or extra artifact")

    actual_rows = [
        row for row in file_inventory(build_root / "public") if row["path"] != "recipe.json"
    ]
    if {row["path"] for row in actual_rows} != EXPECTED_PUBLIC_PAYLOAD_PATHS:
        raise VerificationError("font-v5 public tree has a missing or extra non-recipe artifact")
    for actual in actual_rows:
        pinned = by_path[actual["path"]]
        if pinned["size"] != actual["size"] or pinned["sha256"] != actual["sha256"]:
            raise VerificationError(
                f"font-v5 payload inventory size/SHA mismatch: {actual['path']}"
            )

    return {
        "non_recipe_artifact_count": len(actual_rows),
        "exact_artifact_set": True,
        "size_and_sha256_exact": True,
        "paths": [row["path"] for row in actual_rows],
        "inventory_sha256": inventory_hash(actual_rows),
    }


def require_tmp_build(path: Path, label: str) -> None:
    try:
        path.resolve().relative_to(TMP_ROOT.resolve())
    except ValueError as exc:
        raise VerificationError(f"{label} must stay under KR_PATCH_WORK/tmp: {path}") from exc


def compare_builds(build_a: Path, build_b: Path) -> dict[str, Any]:
    require_tmp_build(build_a, "build A")
    require_tmp_build(build_b, "build B")
    rows_a = file_inventory(build_a)
    rows_b = file_inventory(build_b)
    if rows_a != rows_b:
        paths_a = {row["path"]: row for row in rows_a}
        paths_b = {row["path"]: row for row in rows_b}
        differing = sorted(
            path for path in set(paths_a) | set(paths_b) if paths_a.get(path) != paths_b.get(path)
        )
        raise VerificationError(f"independent builds differ: {differing[:8]!r}")
    return {
        "exact": True,
        "file_count": len(rows_a),
        "inventory_sha256": inventory_hash(rows_a),
        "public_file_count": sum(row["path"].startswith("public/") for row in rows_a),
        "private_validation_file_count": sum(row["path"].startswith("private/") for row in rows_a),
    }


def overlay_names(path: Path) -> tuple[dict[int, str], str, int]:
    overlay = read_json(path)
    entries = overlay.get("entries")
    if (
        overlay.get("schema") != "nobu16.kr.common-message-overlay.v1"
        or overlay.get("resource") != "MSG_PK/SC/msgev.bin"
        or not isinstance(entries, list)
        or len(entries) != EXPECTED_OFFICER_COUNT
        or overlay.get("entry_count") != EXPECTED_OFFICER_COUNT
    ):
        raise VerificationError("officer overlay identity/count gate failed")
    names: dict[int, str] = {}
    for expected_id, entry in enumerate(entries):
        if not isinstance(entry, dict) or entry.get("id") != expected_id or not isinstance(entry.get("ko"), str):
            raise VerificationError(f"officer overlay id/text alignment failed at {expected_id}")
        names[expected_id] = entry["ko"]
    for entry_id, expected in {
        **EXPECTED_FAMOUS,
        **EXPECTED_LONGEST,
        **EXPECTED_CORRECTED,
    }.items():
        if names[entry_id] != expected:
            raise VerificationError(
                f"officer name regression at {entry_id}: {names[entry_id]!r} != {expected!r}"
            )
    longest = max(len(name) for name in names.values())
    if longest != 11 or {entry_id for entry_id, name in names.items() if len(name) == longest} != set(EXPECTED_LONGEST):
        raise VerificationError("longest-name runtime-QA set changed")
    space_occurrences = sum(name.count(" ") for name in names.values())
    return names, sha256_file(path), space_occurrences


def glyph_material(data: bytes, layout: dict[str, Any], table: int, codepoint: int) -> dict[str, Any]:
    table_offset = layout["table_offsets"][table]
    ordinal = BUILDER.BASE.read_u16(data, table_offset + 2 * codepoint)
    if ordinal == 0 or ordinal >= layout["record_counts"][table]:
        raise VerificationError(
            f"entry table {table} U+{codepoint:04X}: invalid ordinal {ordinal}"
        )
    record_offset = table_offset + 0x20000 + 12 * ordinal
    record = data[record_offset : record_offset + 12]
    height = record[1]
    stride = abs(BUILDER.signed8(record[5]))
    pointer = BUILDER.BASE.read_u32(record, 8)
    pixel_length = height * stride
    start = layout["atlas_offset"] + pointer
    end = start + pixel_length
    if height == 0 or stride == 0 or start < layout["atlas_offset"] or end > len(data):
        raise VerificationError(f"entry table {table} U+{codepoint:04X}: invalid glyph bounds")
    pixels = data[start:end]
    return {
        "ordinal": ordinal,
        "record_sha256": sha256_bytes(record),
        "pixel_sha256": sha256_bytes(pixels),
        "pixel_length": len(pixels),
        "nonzero_pixel_bytes": sum(byte != 0 for byte in pixels),
    }


def direct_coverage(
    build_root: Path,
    stock_path: Path,
    officer_codepoints: list[int],
    msgui_codepoints: list[int],
) -> tuple[list[dict[str, Any]], str]:
    candidate_path = build_root / "private" / "candidate" / "res_lang.SC.font-v5.bin"
    if not candidate_path.is_file():
        raise VerificationError(f"missing private font-v5 candidate: {candidate_path}")
    progress("direct-coverage:read-archives")
    stock_blob = stock_path.read_bytes()
    candidate_blob = candidate_path.read_bytes()
    progress("direct-coverage:parse-link")
    stock_archive = BUILDER.BASE.LZ4.parse_link(stock_blob)
    candidate_archive = BUILDER.BASE.LZ4.parse_link(candidate_blob)
    progress("direct-coverage:roundtrip-link")
    if BUILDER.BASE.LZ4.rebuild_link(candidate_archive) != candidate_blob:
        raise VerificationError("candidate LINK roundtrip failed")

    table_rows: list[dict[str, Any]] = []
    for entry in (6, 7):
        progress(f"direct-coverage:entry-{entry}")
        stock_g1n = BUILDER.BASE.extract_raw_entry(stock_archive, entry, f"stock entry {entry}")
        candidate_g1n = BUILDER.BASE.extract_raw_entry(candidate_archive, entry, f"candidate entry {entry}")
        stock_layout = BUILDER.BASE.parse_layout(stock_g1n, f"stock entry {entry}")
        target_layout = BUILDER.BASE.parse_layout(candidate_g1n, f"candidate entry {entry}")
        for table in (0, 1):
            officer_proofs = [
                BUILDER.mapped_glyph_proof(candidate_g1n, target_layout, table, codepoint)
                for codepoint in officer_codepoints
            ]
            msgui_proofs = [
                BUILDER.mapped_glyph_proof(candidate_g1n, target_layout, table, codepoint)
                for codepoint in msgui_codepoints
            ]
            stock_space = glyph_material(stock_g1n, stock_layout, table, 0x20)
            target_space = glyph_material(candidate_g1n, target_layout, table, 0x20)
            if stock_space != target_space:
                raise VerificationError(f"entry {entry} table {table}: ASCII space glyph changed")
            table_rows.append(
                {
                    "entry": entry,
                    "table": table,
                    "officer_hangul_required_count": len(officer_codepoints),
                    "officer_hangul_nonzero_nonblank_count": len(officer_proofs),
                    "officer_hangul_missing_count": 0,
                    "officer_hangul_proof_sha256": sha256_bytes(
                        json.dumps(
                            officer_proofs,
                            ensure_ascii=False,
                            sort_keys=True,
                            separators=(",", ":"),
                        ).encode("utf-8")
                    ),
                    "ascii_space_required": True,
                    "ascii_space_ordinal_nonzero": True,
                    "ascii_space_stock_record_pixels_preserved": True,
                    "ascii_space_proof": target_space,
                    "msgui_required_count": len(msgui_codepoints),
                    "msgui_nonzero_nonblank_count": len(msgui_proofs),
                    "msgui_missing_count": 0,
                    "msgui_proof_sha256": sha256_bytes(
                        json.dumps(
                            msgui_proofs,
                            ensure_ascii=False,
                            sort_keys=True,
                            separators=(",", ":"),
                        ).encode("utf-8")
                    ),
                }
            )
    return table_rows, sha256_bytes(candidate_blob)


def release_tree_proof(release_root: Path, build_root: Path) -> dict[str, Any]:
    forbidden = [
        path.relative_to(release_root).as_posix()
        for path in release_root.rglob("*")
        if path.is_file() and path.suffix.lower() in FORBIDDEN_RELEASE_SUFFIXES
    ]
    private_dirs = [
        path.relative_to(release_root).as_posix()
        for path in release_root.rglob("private")
        if path.is_dir()
    ]
    if forbidden or private_dirs:
        raise VerificationError(
            f"release tree contains forbidden private/full-resource artifacts: {forbidden + private_dirs}"
        )
    release_public = file_inventory(release_root / "public")
    build_public = file_inventory(build_root / "public")
    if release_public != build_public:
        raise VerificationError("tracked public tree differs from verified build A")
    for name in ("manifest.json", "validation.json"):
        if sha256_file(release_root / name) != sha256_file(build_root / name):
            raise VerificationError(f"tracked {name} differs from verified build A")
    return {
        "public_file_count": len(release_public),
        "public_inventory_sha256": inventory_hash(release_public),
        "forbidden_full_resource_file_count": 0,
        "private_directory_count": 0,
        "commercial_full_resources_present": False,
        "generated_pixel_payloads_present": sorted(
            row["path"] for row in release_public if row["path"].endswith(".pixels")
        ),
    }


def verify(args: argparse.Namespace) -> dict[str, Any]:
    build_a = args.build_a.resolve()
    build_b = args.build_b.resolve()
    release_root = args.release_root.resolve()
    overlay_path = args.officer_overlay.resolve()
    officer_demand_path = args.officer_demand.resolve()
    msgui_demand_path = args.msgui_demand.resolve()
    stock_path = args.stock_archive.resolve()

    progress("compare-builds:start")
    determinism = compare_builds(build_a, build_b)
    progress("compare-builds:complete")
    names, overlay_hash, space_occurrences = overlay_names(overlay_path)
    progress("overlay-regressions:complete")
    officer_characters = sorted(
        {character for name in names.values() for character in name if character != " "},
        key=ord,
    )
    if any(not (0xAC00 <= ord(character) <= 0xD7A3) for character in officer_characters):
        raise VerificationError("officer overlay contains a non-Hangul non-space character")
    officer_codepoints = [ord(character) for character in officer_characters]
    if (
        len(officer_codepoints) != EXPECTED_OFFICER_HANGUL_COUNT
        or sha256_bytes(canonical_lines(officer_codepoints)) != OFFICER_CODEPOINTS_SHA256
    ):
        raise VerificationError("officer Hangul count/hash regression gate failed")

    officer_demand = read_json(officer_demand_path)
    demand_officer_codepoints = parse_demand_codepoints(officer_demand, "officer demand")
    if demand_officer_codepoints != officer_codepoints:
        raise VerificationError("officer glyph demand is stale or incomplete")
    source_overlay = officer_demand.get("source_overlay")
    if (
        not isinstance(source_overlay, dict)
        or source_overlay.get("sha256") != overlay_hash
        or source_overlay.get("entry_count") != EXPECTED_OFFICER_COUNT
    ):
        raise VerificationError("officer glyph-demand source pin does not match the overlay")

    if sha256_file(msgui_demand_path) != MSGUI_V4_DEMAND_SHA256:
        raise VerificationError("existing msgui font-v4 glyph-demand regression fixture drifted")
    msgui_demand = read_json(msgui_demand_path)
    msgui_codepoints = parse_demand_codepoints(msgui_demand, "msgui demand")
    union_codepoints = sorted(set(officer_codepoints) | set(msgui_codepoints))
    union_hangul = [codepoint for codepoint in union_codepoints if 0xAC00 <= codepoint <= 0xD7A3]
    if (
        len(union_codepoints) != EXPECTED_UNION_CHARACTER_COUNT
        or len(union_hangul) != EXPECTED_UNION_HANGUL_COUNT
        or sha256_bytes(canonical_lines(union_codepoints)) != UNION_CODEPOINTS_SHA256
    ):
        raise VerificationError("msgui + officer union count/hash regression gate failed")
    progress("corpus-union:complete")

    recipe = read_json(build_a / "public" / "recipe.json")
    validation = read_json(build_a / "validation.json")
    manifest = read_json(build_a / "manifest.json")
    payload_inventory = verify_recipe_payload_inventory(build_a, recipe)
    progress("payload-inventory:complete")
    validation_inventory = validation.get("public_payload_inventory")
    if (
        not isinstance(validation_inventory, dict)
        or validation_inventory.get("non_recipe_artifact_count") != 5
        or validation_inventory.get("exact_artifact_set") is not True
        or validation_inventory.get("size_and_sha256_exact") is not True
        or validation_inventory.get("paths")
        != [relative for relative, _origin in BUILDER.PUBLIC_PAYLOAD_ARTIFACTS]
    ):
        raise VerificationError("font-v5 build validation lacks the exact payload inventory proof")
    corpus = recipe.get("corpus")
    if not isinstance(corpus, dict):
        raise VerificationError("font-v5 recipe is missing its corpus contract")
    if (
        corpus.get("union_codepoints_sha256") != sha256_bytes(canonical_lines(union_codepoints))
        or corpus.get("hangul_codepoints_sha256") != sha256_bytes(canonical_lines(union_hangul))
        or corpus.get("character_count") != len(union_codepoints)
        or corpus.get("hangul_syllable_count") != len(union_hangul)
    ):
        raise VerificationError("font-v5 recipe union does not equal msgui + officer demands")
    if validation.get("passed") is not True:
        raise VerificationError("font-v5 build validation did not pass")
    complete = validation.get("complete_demand_coverage")
    if (
        not isinstance(complete, dict)
        or complete.get("demanded_character_count") != len(union_codepoints)
        or complete.get("all_four_maps_nonzero_nonblank") is not True
    ):
        raise VerificationError("font-v5 complete-demand coverage gate failed")
    p3 = validation.get("raster", {}).get("p3_226_hangul_regression", {})
    if (
        p3.get("shared_hangul_count") != 226
        or p3.get("metrics_byte_exact") is not True
        or any(row.get("byte_exact") is not True for row in p3.get("payloads", []))
    ):
        raise VerificationError("font-v5 P3/msgui raster regression gate failed")

    progress("direct-coverage:start")
    table_rows, candidate_hash = direct_coverage(
        build_a, stock_path, officer_codepoints, msgui_codepoints
    )
    progress("direct-coverage:complete")
    expected_candidate_hash = manifest.get("outputs", {}).get("private_candidate_archive", {}).get("sha256")
    if candidate_hash != expected_candidate_hash:
        raise VerificationError("candidate archive hash differs from the build manifest")
    release = release_tree_proof(release_root, build_a)
    progress("release-tree:complete")

    longest_rows = [
        {"id": entry_id, "ko": names[entry_id], "character_count_including_space": len(names[entry_id])}
        for entry_id in sorted(EXPECTED_LONGEST)
    ]
    famous_rows = [
        {"id": entry_id, "ko": names[entry_id]}
        for entry_id in sorted(EXPECTED_FAMOUS)
    ]
    corrected_rows = [
        {"id": entry_id, "ko": names[entry_id]}
        for entry_id in sorted(EXPECTED_CORRECTED)
    ]
    return {
        "schema": "nobu16.kr.font-v5-verification.v1",
        "passed": True,
        "determinism": determinism,
        "officer_overlay": {
            "sha256": overlay_hash,
            "entry_count": EXPECTED_OFFICER_COUNT,
            "id_range": [0, 2206],
            "only_precomposed_hangul_and_ascii_space": True,
            "unique_hangul_syllable_count": len(officer_codepoints),
            "ascii_space_occurrence_count": space_occurrences,
            "missing_hangul_count_across_all_four_maps": 0,
            "missing_ascii_space_count_across_all_four_maps": 0,
            "longest_runtime_qa_names": longest_rows,
            "famous_runtime_qa_names": famous_rows,
            "corrected_name_regressions": corrected_rows,
        },
        "msgui_regression": {
            "font_v4_demand_sha256": MSGUI_V4_DEMAND_SHA256,
            "character_count": len(msgui_codepoints),
            "hangul_syllable_count": int(msgui_demand["hangul_syllable_count"]),
            "all_codepoints_present_in_v5_union": set(msgui_codepoints).issubset(union_codepoints),
            "missing_count_across_all_four_maps": 0,
            "p3_226_pixels_and_metrics_byte_exact": True,
        },
        "union": {
            "character_count": len(union_codepoints),
            "hangul_syllable_count": len(union_hangul),
            "codepoints_sha256": sha256_bytes(canonical_lines(union_codepoints)),
            "hangul_codepoints_sha256": sha256_bytes(canonical_lines(union_hangul)),
            "all_four_maps_nonzero_nonblank_for_nonspace_demand": True,
            "tables": table_rows,
        },
        "outputs": {
            "recipe_sha256": sha256_file(build_a / "public" / "recipe.json"),
            "metrics_sha256": sha256_file(build_a / "public" / "metrics" / "glyphs.jsonl"),
            "manifest_sha256": sha256_file(build_a / "manifest.json"),
            "validation_sha256": sha256_file(build_a / "validation.json"),
            "private_candidate_archive_sha256": candidate_hash,
            "private_candidate_distribution_forbidden": True,
            "public_payload_inventory": payload_inventory,
        },
        "release_tree": release,
        "safety": {
            "build_outputs_confined_to_ignored_tmp": True,
            "installed_game_files_modified": False,
            "process_memory_access": False,
            "registry_access": False,
            "runtime_patch_features": [],
            "full_res_lang_present_in_release_tree": False,
        },
        "runtime_verified": False,
        "release_eligible": False,
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-a", type=Path, required=True)
    parser.add_argument("--build-b", type=Path, required=True)
    parser.add_argument("--officer-overlay", type=Path, default=DEFAULT_OVERLAY)
    parser.add_argument("--officer-demand", type=Path, default=DEFAULT_OFFICER_DEMAND)
    parser.add_argument("--msgui-demand", type=Path, default=DEFAULT_MSGUI_DEMAND)
    parser.add_argument(
        "--stock-archive",
        type=Path,
        required=True,
        help="Explicit pristine SC font archive/backup; installed-file fallback is forbidden.",
    )
    parser.add_argument("--release-root", type=Path, default=DEFAULT_RELEASE_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    try:
        result = verify(args)
        atomic_write_json(args.output.resolve(), result)
    except (OSError, VerificationError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")
    print(f"output={args.output.resolve()}")
    print(f"officer_entries={result['officer_overlay']['entry_count']}")
    print(f"officer_hangul={result['officer_overlay']['unique_hangul_syllable_count']}")
    print(f"union_characters={result['union']['character_count']}")
    print(f"independent_builds_exact={result['determinism']['exact']}")
    print("all_officer_hangul_and_ascii_space_four_maps_missing=0")
    print("existing_msgui_regression_missing=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
