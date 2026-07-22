#!/usr/bin/env python3
"""Build and verify every v0.15.1 BSDIFF40 resource delta."""

from __future__ import annotations

import argparse
import importlib.util
import os
import tempfile
from pathlib import Path
from typing import Any

import bsdiff4


SCRIPT = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT.parents[1]
PATCHER_SOURCE = PROJECT_ROOT / "tools" / "v0151_resource_patcher.py"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PATCHER = load_module("v0151_resource_patcher_for_delta_build", PATCHER_SOURCE)


def build_delta(source: Path, target: Path, output: Path, relative: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.is_file():
        patch = output.read_bytes()
        rebuilt = PATCHER.apply_bsdiff40(source.read_bytes(), patch, relative=relative)
        PATCHER.require_spec(rebuilt, PATCHER.pin_spec(PATCHER.TARGETS[relative]), relative)
        return
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output.name}.", suffix=".tmp", dir=output.parent
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        bsdiff4.file_diff(str(source), str(target), str(temporary))
        patch = temporary.read_bytes()
        descriptor_value = {
            "format": PATCHER.BINARY_PATCH_FORMAT,
            "member": PATCHER.binary_patch_member(relative),
            **PATCHER.file_spec(patch),
        }
        PATCHER.parse_binary_patch_descriptor(descriptor_value, relative)
        rebuilt = PATCHER.apply_bsdiff40(source.read_bytes(), patch, relative=relative)
        PATCHER.require_spec(rebuilt, PATCHER.pin_spec(PATCHER.TARGETS[relative]), relative)
        os.replace(temporary, output)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pristine-root", type=Path, required=True)
    parser.add_argument("--game-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    pristine_root = args.pristine_root.resolve(strict=True)
    game_root = args.game_root.resolve(strict=True)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    expected = {PATCHER.binary_patch_member(path) for path in PATCHER.BINARY_RESOURCE_PATHS}
    actual = {
        path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()
    }
    if not actual.issubset(expected):
        raise RuntimeError(f"unexpected existing delta files: {sorted(actual - expected)}")

    for index, relative in enumerate(PATCHER.BINARY_RESOURCE_PATHS, 1):
        source = PATCHER.game_path(pristine_root, relative)
        target = PATCHER.game_path(game_root, relative)
        PATCHER.require_spec(source.read_bytes(), PATCHER.pin_spec(PATCHER.PREDECESSORS[relative]), relative)
        PATCHER.require_spec(target.read_bytes(), PATCHER.pin_spec(PATCHER.TARGETS[relative]), relative)
        member = PATCHER.binary_patch_member(relative)
        build_delta(source, target, output / Path(member), relative)
        print(f"[{index}/{len(PATCHER.BINARY_RESOURCE_PATHS)}] {relative}", flush=True)

    final = {path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()}
    if final != expected:
        raise RuntimeError(f"delta member set differs: missing={sorted(expected - final)}")
    print(f"binary_deltas={len(final)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
