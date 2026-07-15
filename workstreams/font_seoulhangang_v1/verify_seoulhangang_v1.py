#!/usr/bin/env python3
"""Compare two local SeoulHangang v1 builds without exporting game/font bytes."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
PATCH_ROOT = SCRIPT_DIR.parents[1]
sys.dont_write_bytecode = True


class VerifyError(ValueError):
    pass


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


G1N = load_module("nobu16_font_seoulhangang_v1_validator", PATCH_ROOT / "tools" / "validate_g1n_surgical.py")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def canonical_codepoint_hash(codepoints: set[int]) -> str:
    return sha256(
        "".join(f"U+{codepoint:04X}\\n" for codepoint in sorted(codepoints)).encode("ascii")
    )


def load_manifest(root: Path) -> tuple[dict[str, Any], bytes]:
    path = root / "private" / "build_manifest.json"
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerifyError(f"cannot read private build manifest {path}: {exc}") from exc
    if not isinstance(value, dict) or value.get("schema") != "nobu16.kr.font-seoulhangang-v1-private-build.v1":
        raise VerifyError(f"invalid private build manifest: {path}")
    policy = value.get("distribution")
    if not isinstance(policy, dict) or any(policy.get(key) is not False for key in (
        "official_ttf_included", "seoulhangang_raster_payload_included", "stock_g1n_or_link_included", "complete_candidate_publicly_distributable"
    )):
        raise VerifyError(f"distribution policy mismatch: {path}")
    return value, raw


def load_demand_codepoints(root: Path) -> tuple[set[int], bytes]:
    path = root / "plan.json"
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerifyError(f"cannot read private build plan {path}: {exc}") from exc
    if not isinstance(value, dict) or value.get("schema") != "nobu16.kr.font-seoulhangang-v1-plan.v1":
        raise VerifyError(f"invalid private build plan: {path}")
    raw_points = value.get("glyph_demand_codepoints")
    if not isinstance(raw_points, list) or not raw_points:
        raise VerifyError(f"private build plan has no explicit glyph demand: {path}")
    if not all(isinstance(point, int) and 0 <= point <= 0xFFFF for point in raw_points):
        raise VerifyError(f"private build glyph demand is outside BMP: {path}")
    if raw_points != sorted(raw_points) or len(raw_points) != len(set(raw_points)):
        raise VerifyError(f"private build glyph demand is not sorted and unique: {path}")
    points = set(raw_points)
    if value.get("glyph_demand_codepoints_sha256") != canonical_codepoint_hash(points):
        raise VerifyError(f"private build glyph-demand hash mismatch: {path}")
    return points, raw


def candidate_summary(
    root: Path, manifest: dict[str, Any], demand_codepoints: set[int]
) -> dict[str, Any]:
    entries = manifest.get("entries")
    if not isinstance(entries, list) or [item.get("entry") for item in entries] != [6, 7]:
        raise VerifyError("private manifest entry order is invalid")
    summaries = []
    coverage = []
    for item in entries:
        entry = int(item["entry"])
        path = root / "private" / "candidate" / f"SC_{entry}.seoulhangang-v1.g1n"
        raw = path.read_bytes()
        if sha256(raw) != item.get("sha256") or len(raw) != item.get("size"):
            raise VerifyError(f"entry {entry} hash/size does not match its private manifest")
        parsed = G1N.parse_g1n(path)
        if parsed.structural_errors:
            raise VerifyError(f"entry {entry} has G1N structural errors: {parsed.structural_errors[:1]}")
        for table in parsed.tables:
            mapped = {codepoint for codepoint, ordinal in enumerate(table.mapping) if ordinal}
            missing = sorted(demand_codepoints - mapped)
            if missing:
                preview = ", ".join(f"U+{codepoint:04X}" for codepoint in missing[:8])
                raise VerifyError(
                    f"entry {entry} table {table.index} misses {len(missing)} demanded glyphs: {preview}"
                )
            coverage.append(
                {
                    "entry": entry,
                    "table": table.index,
                    "mapped_demand_count": len(demand_codepoints),
                    "missing_demand_count": 0,
                }
            )
        summaries.append(
            {
                "entry": entry,
                "sha256": sha256(raw),
                "size": len(raw),
                "table_count": parsed.table_count,
                "record_counts": [table.record_count for table in parsed.tables],
            }
        )
    archive = root / "private" / "candidate" / "res_lang.SC.seoulhangang-v1.bin"
    archive_raw = archive.read_bytes()
    candidate = manifest.get("candidate_archive")
    if not isinstance(candidate, dict) or sha256(archive_raw) != candidate.get("sha256") or len(archive_raw) != candidate.get("size"):
        raise VerifyError("candidate archive hash/size does not match its private manifest")
    return {
        "entries": summaries,
        "archive_sha256": sha256(archive_raw),
        "archive_size": len(archive_raw),
        "glyph_demand_coverage": {
            "codepoint_count": len(demand_codepoints),
            "codepoints_sha256": canonical_codepoint_hash(demand_codepoints),
            "tables": coverage,
        },
    }


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


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-a", type=Path, required=True)
    parser.add_argument("--build-b", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        build_a = args.build_a.resolve()
        build_b = args.build_b.resolve()
        manifest_a, raw_a = load_manifest(build_a)
        manifest_b, raw_b = load_manifest(build_b)
        demand_a, plan_raw_a = load_demand_codepoints(build_a)
        demand_b, plan_raw_b = load_demand_codepoints(build_b)
        summary_a = candidate_summary(build_a, manifest_a, demand_a)
        summary_b = candidate_summary(build_b, manifest_b, demand_b)
        if raw_a != raw_b:
            raise VerifyError("private build manifests differ")
        if plan_raw_a != plan_raw_b:
            raise VerifyError("private build plans differ")
        if demand_a != demand_b:
            raise VerifyError("private build glyph demands differ")
        if summary_a != summary_b:
            raise VerifyError("private candidate hashes or G1N structures differ")
        result = {
            "schema": "nobu16.kr.font-seoulhangang-v1-ab-verification.v1",
            "build_manifest_sha256": sha256(raw_a),
            "candidate": summary_a,
            "manifest_byte_identical": True,
            "candidate_byte_identical": True,
            "g1n_structural_validation": True,
            "full_pk_glyph_demand_coverage": True,
            "installed_game_files_modified": False,
            "official_ttf_or_raster_payload_in_public_output": False,
        }
        atomic_write(args.output.resolve(), (json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
        print(f"output={args.output.resolve()}")
        print("candidate_byte_identical=True")
        return 0
    except (VerifyError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
