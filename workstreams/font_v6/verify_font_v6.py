#!/usr/bin/env python3
"""Verify two font-v6 builds and the tracked source-free release tree."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any, Iterable


sys.dont_write_bytecode = True
SCRIPT_DIR = Path(__file__).resolve().parent
GAME_ROOT = SCRIPT_DIR.parents[2]
PATCH_ROOT = GAME_ROOT / "KR_PATCH_WORK"
TMP_ROOT = PATCH_ROOT / "tmp"
DEFAULT_RELEASE_ROOT = SCRIPT_DIR
DEFAULT_OUTPUT = SCRIPT_DIR / "verification.json"
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
EXPECTED_RELEASE_FILES = {
    "README_KO.md",
    "build_font_v6.py",
    "compare_font_v6_builds.ps1",
    "corpus/msgdata_castle_names_9151_9542/glyph_demand.json",
    "corpus/msgev_dialogue_3202_3229/glyph_demand.json",
    "corpus/msgev_officer_names_0000_2399/glyph_demand.json",
    "corpus/msgui_0000_5099/glyph_demand.json",
    "manifest.json",
    "public/licenses/OFL-NotoSansKR.txt",
    "public/licenses/OFL-NotoSerifKR.txt",
    "public/metrics/glyphs.jsonl",
    "public/payload/glyph_pixels_entry_6.pixels",
    "public/payload/glyph_pixels_entry_7.pixels",
    "public/recipe.json",
    "rasterize_font_v6.ps1",
    "regression/p3_226.glyph_demand.json",
    "validation.json",
    "verify_font_v6.py",
}
OPTIONAL_VERIFICATION_OUTPUT = "verification.json"


class VerificationError(ValueError):
    """Raised when a font-v6 safety, corpus, or determinism gate fails."""


def load_builder() -> Any:
    path = SCRIPT_DIR / "build_font_v6.py"
    spec = importlib.util.spec_from_file_location("nobu16_font_v6_verify", path)
    if spec is None or spec.loader is None:
        raise VerificationError(f"cannot load font-v6 builder: {path}")
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
    print(f"[verify-font-v6] {message}", file=sys.stderr, flush=True)


def canonical_lines(codepoints: Iterable[int]) -> bytes:
    return "".join(
        f"U+{codepoint:04X}\n" for codepoint in sorted(set(codepoints))
    ).encode("ascii")


def file_inventory(root: Path) -> list[dict[str, Any]]:
    if not root.is_dir():
        raise VerificationError(f"missing directory: {root}")
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "size": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(
            (item for item in root.rglob("*") if item.is_file()),
            key=lambda item: item.as_posix(),
        )
    ]


def inventory_hash(rows: list[dict[str, Any]]) -> str:
    return sha256_bytes(
        "".join(
            f"{row['path']}\t{row['size']}\t{row['sha256']}\n" for row in rows
        ).encode("utf-8")
    )


def require_tmp_build(path: Path, label: str) -> None:
    try:
        path.resolve().relative_to(TMP_ROOT.resolve())
    except ValueError as exc:
        raise VerificationError(f"{label} must stay under KR_PATCH_WORK/tmp: {path}") from exc


def compare_builds(build_a: Path, build_b: Path) -> dict[str, Any]:
    require_tmp_build(build_a, "build A")
    require_tmp_build(build_b, "build B")
    if build_a.resolve() == build_b.resolve():
        raise VerificationError("font-v6 build A and build B must be distinct directories")
    rows_a = file_inventory(build_a)
    rows_b = file_inventory(build_b)
    if rows_a != rows_b:
        by_path_a = {row["path"]: row for row in rows_a}
        by_path_b = {row["path"]: row for row in rows_b}
        differing = sorted(
            path
            for path in set(by_path_a) | set(by_path_b)
            if by_path_a.get(path) != by_path_b.get(path)
        )
        raise VerificationError(f"independent font-v6 builds differ: {differing[:8]!r}")
    return {
        "exact": True,
        "file_count": len(rows_a),
        "inventory_sha256": inventory_hash(rows_a),
        "public_file_count": sum(row["path"].startswith("public/") for row in rows_a),
        "private_validation_file_count": sum(
            row["path"].startswith("private/") for row in rows_a
        ),
    }


def verify_payload_inventory(
    build_root: Path, recipe: dict[str, Any]
) -> dict[str, Any]:
    rows = recipe.get("payload_inventory")
    if not isinstance(rows, list) or len(rows) != len(EXPECTED_PUBLIC_PAYLOAD_PATHS):
        raise VerificationError("font-v6 recipe must inventory exactly five public artifacts")
    pinned: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"origin", "path", "sha256", "size"}:
            raise VerificationError("font-v6 payload inventory row has unexpected properties")
        path = row.get("path")
        digest = row.get("sha256")
        size = row.get("size")
        origin = row.get("origin")
        if (
            not isinstance(path, str)
            or path in pinned
            or not isinstance(origin, str)
            or not origin.strip()
            or type(size) is not int
            or size < 0
            or not isinstance(digest, str)
            or len(digest) != 64
            or digest != digest.upper()
            or any(character not in "0123456789ABCDEF" for character in digest)
        ):
            raise VerificationError("font-v6 payload inventory row is not canonical")
        pinned[path] = row
    if set(pinned) != EXPECTED_PUBLIC_PAYLOAD_PATHS:
        raise VerificationError("font-v6 payload inventory has a missing or extra artifact")

    actual = [
        row for row in file_inventory(build_root / "public") if row["path"] != "recipe.json"
    ]
    if {row["path"] for row in actual} != EXPECTED_PUBLIC_PAYLOAD_PATHS:
        raise VerificationError("font-v6 public tree has a missing or extra artifact")
    for row in actual:
        expected = pinned[row["path"]]
        if expected["size"] != row["size"] or expected["sha256"] != row["sha256"]:
            raise VerificationError(f"font-v6 payload pin mismatch: {row['path']}")
    expected_sizes = {
        "payload/glyph_pixels_entry_6.pixels": BUILDER.EXPECTED_PUBLIC_PIXEL_PAYLOAD_SIZES[6],
        "payload/glyph_pixels_entry_7.pixels": BUILDER.EXPECTED_PUBLIC_PIXEL_PAYLOAD_SIZES[7],
    }
    for path, size in expected_sizes.items():
        if pinned[path]["size"] != size:
            raise VerificationError(f"font-v6 pinned payload size drifted: {path}")
    metrics = build_root / "public" / "metrics" / "glyphs.jsonl"
    if metrics.read_bytes().count(b"\n") != BUILDER.EXPECTED_PUBLIC_METRICS_ROW_COUNT:
        raise VerificationError("font-v6 metrics row count drifted")
    return {
        "non_recipe_artifact_count": len(actual),
        "exact_artifact_set": True,
        "size_and_sha256_exact": True,
        "paths": [row["path"] for row in actual],
        "inventory_sha256": inventory_hash(actual),
        "pixel_payload_sizes": expected_sizes,
        "metrics_row_count": BUILDER.EXPECTED_PUBLIC_METRICS_ROW_COUNT,
    }


def exact_append_contract(value: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) != 4:
        raise VerificationError(f"{label}: expected four per-table append rows")
    expected = [
        {
            "entry": entry,
            "table": table,
            "count": BUILDER.EXPECTED_APPEND_CONTRACT[(entry, table)][0],
            "codepoints_sha256": BUILDER.EXPECTED_APPEND_CONTRACT[(entry, table)][1],
        }
        for entry in (6, 7)
        for table in (0, 1)
    ]
    if value != expected:
        raise VerificationError(f"{label}: font-v6 append contract drifted")
    return expected


def verify_corpus_contract(
    recipe: dict[str, Any], validation: dict[str, Any], manifest: dict[str, Any], union: dict[str, Any]
) -> dict[str, Any]:
    if recipe.get("schema") != "nobu16.file-only-g1n-tail-recipe.v2":
        raise VerificationError("font-v6 recipe schema mismatch")
    if validation.get("schema") != "nobu16.kr.font-v6-validation.v1":
        raise VerificationError("font-v6 validation schema mismatch")
    if manifest.get("schema") != "nobu16.kr.font-v6-build-manifest.v1":
        raise VerificationError("font-v6 manifest schema mismatch")
    if validation.get("passed") is not True:
        raise VerificationError("font-v6 validation did not pass")

    corpus = recipe.get("corpus")
    manifest_corpus = manifest.get("corpus")
    demand_contract = validation.get("demand_contract")
    if not all(isinstance(value, dict) for value in (corpus, manifest_corpus, demand_contract)):
        raise VerificationError("font-v6 corpus metadata is missing")
    if corpus.get("schema") != "nobu16.kr.font-v6-corpus-union.v1":
        raise VerificationError("font-v6 corpus schema mismatch")
    if corpus.get("sources") != union["sources"] or manifest_corpus.get("sources") != union["sources"]:
        raise VerificationError("font-v6 build does not pin exactly the four expected sources")

    expected_fields = {
        "source_non_whitespace_character_count": union["source_codepoint_count"],
        "source_non_whitespace_codepoints_sha256": union["source_union_sha256"],
        "excluded_font_token_count": union["excluded_codepoint_count"],
        "excluded_font_tokens_sha256": union["excluded_font_tokens_sha256"],
        "excluded_font_codepoints_sha256": union["excluded_codepoints_sha256"],
        "character_count": union["codepoint_count"],
        "hangul_syllable_count": union["hangul_count"],
        "non_hangul_character_count": union["non_hangul_count"],
        "union_codepoints_sha256": union["union_sha256"],
        "hangul_codepoints_sha256": union["hangul_sha256"],
        "raster_codepoint_count": BUILDER.EXPECTED_UNION["raster_codepoint_count"],
        "raster_codepoints_sha256": BUILDER.EXPECTED_UNION["raster_codepoints_sha256"],
    }
    for name, value in expected_fields.items():
        if corpus.get(name) != value or manifest_corpus.get(name) != value:
            raise VerificationError(f"font-v6 corpus field drifted: {name}")
    if (
        demand_contract.get("source_count") != BUILDER.EXPECTED_UNION["source_count"]
        or demand_contract.get("union_character_count") != union["codepoint_count"]
        or demand_contract.get("raster_hangul_count") != union["hangul_count"]
        or demand_contract.get("raster_codepoint_count")
        != BUILDER.EXPECTED_UNION["raster_codepoint_count"]
    ):
        raise VerificationError("font-v6 validation demand contract drifted")
    append = exact_append_contract(corpus.get("per_table_append_contract"), "recipe corpus")
    exact_append_contract(
        validation.get("per_table_append_contract"), "validation"
    )
    exact_append_contract(
        manifest_corpus.get("per_table_append_contract"), "manifest corpus"
    )

    complete = validation.get("complete_demand_coverage")
    if (
        not isinstance(complete, dict)
        or complete.get("demanded_character_count") != union["codepoint_count"]
        or complete.get("all_four_maps_nonzero_nonblank") is not True
        or not isinstance(complete.get("tables"), list)
        or len(complete["tables"]) != 4
    ):
        raise VerificationError("font-v6 complete-demand coverage gate failed")
    for row in complete["tables"]:
        if (
            row.get("demanded_count") != union["codepoint_count"]
            or row.get("nonzero_nonblank_count") != union["codepoint_count"]
            or row.get("codepoints_sha256") != union["union_sha256"]
            or row.get("all_nonzero_nonblank") is not True
        ):
            raise VerificationError("font-v6 per-table complete-demand proof drifted")
    p3 = validation.get("raster", {}).get("p3_226_hangul_regression", {})
    p3_payloads = p3.get("payloads")
    if (
        p3.get("shared_hangul_count") != 226
        or p3.get("metrics_byte_exact") is not True
        or not isinstance(p3_payloads, list)
        or len(p3_payloads) != 2
        or {row.get("entry") for row in p3_payloads} != {6, 7}
        or any(row.get("byte_exact") is not True for row in p3_payloads)
    ):
        raise VerificationError("font-v6 P3 raster regression failed")
    return {"sources": union["sources"], "per_table_append_contract": append}


def glyph_material(data: bytes, layout: dict[str, Any], table: int, codepoint: int) -> dict[str, Any]:
    table_offset = layout["table_offsets"][table]
    ordinal = BUILDER.BASE.read_u16(data, table_offset + 2 * codepoint)
    if ordinal == 0 or ordinal >= layout["record_counts"][table]:
        raise VerificationError(f"table {table} U+{codepoint:04X}: invalid ordinal {ordinal}")
    record_offset = table_offset + 0x20000 + 12 * ordinal
    record = data[record_offset : record_offset + 12]
    height = record[1]
    stride = abs(BUILDER.signed8(record[5]))
    pointer = BUILDER.BASE.read_u32(record, 8)
    start = layout["atlas_offset"] + pointer
    end = start + height * stride
    if height == 0 or stride == 0 or start < layout["atlas_offset"] or end > len(data):
        raise VerificationError(f"table {table} U+{codepoint:04X}: invalid glyph bounds")
    pixels = data[start:end]
    # This helper is used to prove that the stock ASCII-space material is
    # preserved byte-for-byte.  A space is legitimately all-zero, so only
    # its ordinal, bounds, record, and pixel bytes are required here.  The
    # demanded visible glyphs use BUILDER.mapped_glyph_proof(), which keeps
    # the strict nonblank check.
    return {
        "ordinal": ordinal,
        "record_sha256": sha256_bytes(record),
        "pixel_sha256": sha256_bytes(pixels),
        "pixel_length": len(pixels),
    }


def direct_coverage(
    build_root: Path, stock_path: Path, union: dict[str, Any]
) -> tuple[list[dict[str, Any]], str]:
    candidate_path = build_root / "private" / "candidate" / "res_lang.SC.font-v6.bin"
    if not candidate_path.is_file():
        raise VerificationError(f"missing private font-v6 candidate: {candidate_path}")
    if sha256_file(stock_path) != BUILDER.STOCK_ARCHIVE_SHA256:
        raise VerificationError("font-v6 stock archive SHA mismatch")
    stock_blob = stock_path.read_bytes()
    candidate_blob = candidate_path.read_bytes()
    stock_archive = BUILDER.BASE.LZ4.parse_link(stock_blob)
    candidate_archive = BUILDER.BASE.LZ4.parse_link(candidate_blob)
    if BUILDER.BASE.LZ4.rebuild_link(candidate_archive) != candidate_blob:
        raise VerificationError("font-v6 candidate LINK roundtrip failed")
    for index, stock_entry in enumerate(stock_archive.entries):
        if index not in (6, 7) and candidate_archive.entries[index].data != stock_entry.data:
            raise VerificationError(f"font-v6 untouched LINK entry changed: {index}")

    rows: list[dict[str, Any]] = []
    for entry in (6, 7):
        stock_g1n = BUILDER.BASE.extract_raw_entry(stock_archive, entry, f"stock entry {entry}")
        target_g1n = BUILDER.BASE.extract_raw_entry(candidate_archive, entry, f"target entry {entry}")
        stock_layout = BUILDER.BASE.parse_layout(stock_g1n, f"stock entry {entry}")
        target_layout = BUILDER.BASE.parse_layout(target_g1n, f"target entry {entry}")
        for table in (0, 1):
            proofs = [
                BUILDER.mapped_glyph_proof(target_g1n, target_layout, table, codepoint)
                for codepoint in union["codepoints"]
            ]
            if glyph_material(stock_g1n, stock_layout, table, 0x20) != glyph_material(
                target_g1n, target_layout, table, 0x20
            ):
                raise VerificationError(f"entry {entry} table {table}: ASCII space glyph changed")
            stock_owned = []
            table_offset = stock_layout["table_offsets"][table]
            for codepoint in union["non_hangul"]:
                if BUILDER.BASE.read_u16(stock_g1n, table_offset + 2 * codepoint) == 0:
                    continue
                before = BUILDER.mapped_glyph_proof(stock_g1n, stock_layout, table, codepoint)
                after = BUILDER.mapped_glyph_proof(target_g1n, target_layout, table, codepoint)
                if before != after:
                    raise VerificationError(
                        f"entry {entry} table {table} U+{codepoint:04X}: stock glyph changed"
                    )
                stock_owned.append(codepoint)
            rows.append(
                {
                    "entry": entry,
                    "table": table,
                    "demanded_count": len(union["codepoints"]),
                    "nonzero_nonblank_count": len(proofs),
                    "codepoints_sha256": union["union_sha256"],
                    "proof_rows_sha256": sha256_bytes(
                        json.dumps(
                            proofs, ensure_ascii=False, sort_keys=True, separators=(",", ":")
                        ).encode("utf-8")
                    ),
                    "stock_owned_non_hangul_preserved_count": len(stock_owned),
                    "ascii_space_stock_record_pixels_preserved": True,
                }
            )
    return rows, sha256_bytes(candidate_blob)


def release_tree_proof(release_root: Path, build_root: Path) -> dict[str, Any]:
    actual_files = {
        path.relative_to(release_root).as_posix()
        for path in release_root.rglob("*")
        if path.is_file()
    }
    unexpected = actual_files - EXPECTED_RELEASE_FILES - {OPTIONAL_VERIFICATION_OUTPUT}
    missing = EXPECTED_RELEASE_FILES - actual_files
    if unexpected or missing:
        raise VerificationError(
            "font-v6 release file inventory mismatch: "
            f"missing={sorted(missing)!r} unexpected={sorted(unexpected)!r}"
        )
    verification_output = release_root / OPTIONAL_VERIFICATION_OUTPUT
    if verification_output.is_file():
        previous = read_json(verification_output)
        if (
            previous.get("schema") != "nobu16.kr.font-v6-verification.v1"
            or previous.get("passed") is not True
        ):
            raise VerificationError("existing font-v6 verification output is not canonical")
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
            f"font-v6 release tree contains forbidden artifacts: {forbidden + private_dirs}"
        )
    release_public = file_inventory(release_root / "public")
    build_public = file_inventory(build_root / "public")
    if release_public != build_public:
        raise VerificationError("tracked font-v6 public tree differs from verified build A")
    for name in ("manifest.json", "validation.json"):
        if sha256_file(release_root / name) != sha256_file(build_root / name):
            raise VerificationError(f"tracked font-v6 {name} differs from build A")
    return {
        "exact_release_file_inventory": True,
        "public_file_count": len(release_public),
        "public_inventory_sha256": inventory_hash(release_public),
        "forbidden_full_resource_file_count": 0,
        "private_directory_count": 0,
        "commercial_full_resources_present": False,
    }


def verify(args: argparse.Namespace) -> dict[str, Any]:
    build_a = args.build_a.resolve()
    build_b = args.build_b.resolve()
    release_root = args.release_root.resolve()
    stock_path = args.stock_archive.resolve()
    demand_paths = (
        [path.resolve() for path in args.demand_file]
        if args.demand_file
        else [path.resolve() for path in BUILDER.DEFAULT_DEMAND_FILES]
    )
    union = BUILDER.demand_union(demand_paths)
    BUILDER.validate_expected_union(union, demand_paths)
    progress("corpus-contract:complete")

    determinism = compare_builds(build_a, build_b)
    progress("determinism:complete")
    recipe = read_json(build_a / "public" / "recipe.json")
    validation = read_json(build_a / "validation.json")
    manifest = read_json(build_a / "manifest.json")
    payload_inventory = verify_payload_inventory(build_a, recipe)
    corpus_contract = verify_corpus_contract(recipe, validation, manifest, union)
    progress("build-metadata:complete")

    table_rows, candidate_hash = direct_coverage(build_a, stock_path, union)
    expected_candidate = manifest.get("outputs", {}).get("private_candidate_archive", {}).get("sha256")
    recipe_candidate = (
        recipe.get("languages", {}).get("SC", {}).get("target_archive", {}).get("sha256")
    )
    if candidate_hash != expected_candidate or candidate_hash != recipe_candidate:
        raise VerificationError("font-v6 candidate archive hash pin mismatch")
    progress("direct-coverage:complete")
    release = release_tree_proof(release_root, build_a)
    progress("release-tree:complete")

    return {
        "schema": "nobu16.kr.font-v6-verification.v1",
        "passed": True,
        "determinism": determinism,
        "corpus": {
            "source_count": len(union["sources"]),
            "sources": corpus_contract["sources"],
            "source_non_whitespace_character_count": union["source_codepoint_count"],
            "excluded_font_token_count": union["excluded_codepoint_count"],
            "character_count": union["codepoint_count"],
            "hangul_syllable_count": union["hangul_count"],
            "non_hangul_character_count": union["non_hangul_count"],
            "union_codepoints_sha256": union["union_sha256"],
            "hangul_codepoints_sha256": union["hangul_sha256"],
            "raster_codepoint_count": BUILDER.EXPECTED_UNION["raster_codepoint_count"],
            "raster_codepoints_sha256": BUILDER.EXPECTED_UNION["raster_codepoints_sha256"],
            "font_v5_added_hangul_count": len(BUILDER.EXPECTED_V5_ADDED_HANGUL),
            "font_v5_added_hangul_sha256": BUILDER.EXPECTED_V5_ADDED_HANGUL_SHA256,
            "per_table_append_contract": corpus_contract["per_table_append_contract"],
        },
        "direct_coverage": {
            "all_four_maps_nonzero_nonblank": True,
            "ascii_space_preserved": True,
            "stock_owned_non_hangul_preserved": True,
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
    parser.add_argument(
        "--demand-file",
        type=Path,
        action="append",
        help="Pinned demand input; repeat exactly four times. Default uses font_v6/corpus.",
    )
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
    print(f"demand_sources={result['corpus']['source_count']}")
    print(f"union_characters={result['corpus']['character_count']}")
    print(f"union_hangul={result['corpus']['hangul_syllable_count']}")
    print(f"raster_codepoints={result['corpus']['raster_codepoint_count']}")
    print(f"independent_builds_exact={result['determinism']['exact']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
