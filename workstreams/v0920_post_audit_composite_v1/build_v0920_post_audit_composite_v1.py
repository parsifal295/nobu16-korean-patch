#!/usr/bin/env python3
"""Compose the approved PK paired-reading and effect-text overlays for v0.92.0."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RESOURCE = Path("MSG_PK/JP/msgdata.bin")
SCHEMA = "nobu16.kr.v0920-post-audit-composite-validation.v1"


def import_file(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CORE = import_file(
    "v0920_post_audit_composite_core",
    REPO
    / "workstreams"
    / "steam_jp_fullwidth_normalization_v1"
    / "build_steam_jp_fullwidth_normalization_v1.py",
)

BASE_PIN = {
    "packed_size": 479_940,
    "packed_sha256": "0959A0A1BE04261B3D7F76A681937000BA8BE5FD6AC87736F0FC428E36FD7FA1",
    "raw_size": 478_040,
    "raw_sha256": "D83F4EBDFDE8EA99C6BE018A06D2D0F22C36A3C0CBF70F4751D93FB0A1164963",
    "entry_count": 29_218,
}
PAIRED_PIN = {
    "packed_size": 477_069,
    "packed_sha256": "2CFC16C4E03E32932CB803199B081C0D0D358A25E17B4C52DD1634A8F50EAD52",
    "raw_size": 475_180,
    "raw_sha256": "2A476EB0BCC8E6872FFC35FC885A277A5F87CF00B86E329C8D37FA2A0983BD7F",
    "entry_count": 29_218,
}
EFFECT_PIN = {
    "packed_size": 480_065,
    "packed_sha256": "C1BD9DEE2962CDB5869A5EF008A86DD6EACCB067F23321FD9A136C0BCEDAC224",
    "raw_size": 478_164,
    "raw_sha256": "968F9F89E7ABBA81C5E8BC7325DABB55FEED8673DB37CCAB390A07192F47B1E1",
    "entry_count": 29_218,
}

FINAL_PIN: dict[str, int | str] = {
    "packed_size": 477_193,
    "packed_sha256": "DC27B7FA285848AA46289DA4C4E722017A1B3BDAA4E36116CA8FB8D263142898",
    "raw_size": 475_304,
    "raw_sha256": "63D8F0E30114BF91F508FE329EC0CB5F119B338C38E8780159E63A98B3095556",
    "entry_count": 29_218,
}


class BuildError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def file_spec(packed: bytes, raw: bytes, count: int) -> dict[str, int | str]:
    return {
        "packed_size": len(packed),
        "packed_sha256": sha256(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256(raw),
        "entry_count": count,
    }


def load(
    root: Path, expected: dict[str, int | str]
) -> tuple[bytes, bytes, Any, dict[tuple[int, ...], str]]:
    path = root / RESOURCE
    try:
        packed = path.read_bytes()
    except OSError as exc:
        raise BuildError(f"cannot read {path}") from exc
    _header, raw = CORE.decompress_wrapper(packed)
    document = CORE.parse_document(RESOURCE.as_posix(), packed)
    values = CORE.cell_map(document)
    actual = file_spec(packed, raw, len(values))
    if actual != expected:
        raise BuildError(f"input pin differs: {path}: {actual}")
    return packed, raw, document, values


def resolved_under(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def run(base_root: Path, paired_root: Path, effect_root: Path, output_root: Path) -> dict[str, Any]:
    for input_root in (base_root, paired_root, effect_root):
        if resolved_under(output_root, input_root):
            raise BuildError("output root must not be inside an input root")
    if output_root.exists() and any(output_root.iterdir()):
        raise BuildError(f"output root is not empty: {output_root}")

    base_packed, base_raw, base_parsed, base = load(base_root, BASE_PIN)
    _paired_packed, _paired_raw, _paired_parsed, paired = load(paired_root, PAIRED_PIN)
    _effect_packed, _effect_raw, _effect_parsed, effect = load(effect_root, EFFECT_PIN)
    if set(base) != set(paired) or set(base) != set(effect):
        raise BuildError("coordinate domain differs")

    paired_diff = {coordinate: paired[coordinate] for coordinate in base if base[coordinate] != paired[coordinate]}
    effect_diff = {coordinate: effect[coordinate] for coordinate in base if base[coordinate] != effect[coordinate]}
    if len(paired_diff) != 196:
        raise BuildError(f"paired-reading diff count differs: {len(paired_diff)}")
    if len(effect_diff) != 87:
        raise BuildError(f"effect-text diff count differs: {len(effect_diff)}")
    overlap = sorted(set(paired_diff) & set(effect_diff))
    if overlap:
        raise BuildError(f"overlay coordinate overlap: {overlap}")

    replacements = {**paired_diff, **effect_diff}
    merged = dict(base)
    merged.update(replacements)
    candidate = base_parsed.rebuild(merged)
    _header, candidate_raw = CORE.decompress_wrapper(candidate)
    candidate_document = CORE.parse_document(RESOURCE.as_posix(), candidate)
    after = CORE.cell_map(candidate_document)
    if set(after) != set(base):
        raise BuildError("candidate coordinate domain differs")
    changed = {coordinate for coordinate in base if base[coordinate] != after[coordinate]}
    if changed != set(replacements):
        raise BuildError("candidate changed-coordinate vector differs")
    for coordinate, target in replacements.items():
        if after[coordinate] != target:
            raise BuildError(f"candidate target differs at {coordinate}")

    actual = file_spec(candidate, candidate_raw, len(after))
    if actual != FINAL_PIN:
        raise BuildError(f"final output pin differs: {actual}")

    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / RESOURCE
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(candidate)

    report = {
        "schema": SCHEMA,
        "resource": RESOURCE.as_posix(),
        "base": BASE_PIN,
        "paired_readings": {
            "input": PAIRED_PIN,
            "changed_coordinates": len(paired_diff),
        },
        "effect_text": {
            "input": EFFECT_PIN,
            "changed_coordinates": len(effect_diff),
        },
        "overlap_count": len(overlap),
        "final": actual,
        "changed_coordinates": len(changed),
        "coordinate_vector_sha256": sha256(
            ",".join(str(value) for value in sorted(changed)).encode("ascii")
        ),
    }
    (output_root / "validation.v0920_post_audit_composite.v1.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-root", type=Path, required=True)
    parser.add_argument("--paired-root", type=Path, required=True)
    parser.add_argument("--effect-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = run(
            args.base_root.resolve(),
            args.paired_root.resolve(),
            args.effect_root.resolve(),
            args.output_root.resolve(),
        )
    except (BuildError, CORE.NormalizationError, OSError, KeyError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report["final"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
