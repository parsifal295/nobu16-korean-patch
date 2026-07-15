#!/usr/bin/env python3
"""Compose verified G1N font entries onto an existing PC ``res_lang.bin``.

Only outer LINK entries 6 and 7 are replaced.  Every other wrapped entry,
including title-image entry 3, must remain byte-identical to the selected base
archive.  Inputs are SHA-pinned on the command line and output is restricted to
the repository's ignored ``tmp`` tree; no installed game file is written.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any, Sequence


SCRIPT_PATH = Path(__file__).resolve()
TOOLS_ROOT = SCRIPT_PATH.parent
REPO_ROOT = TOOLS_ROOT.parent
TMP_ROOT = (REPO_ROOT / "tmp").resolve()
sys.dont_write_bytecode = True


class ComposeError(ValueError):
    pass


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


FONT = load_module("nobu16_compose_font_recipe", TOOLS_ROOT / "build_file_only_font_recipe.py")
LZ4 = FONT.LZ4


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def require_input(path: Path, expected_sha256: str, label: str) -> bytes:
    if not path.is_file():
        raise ComposeError(f"missing {label}: {path}")
    data = path.read_bytes()
    actual = sha256(data)
    if actual != expected_sha256.upper():
        raise ComposeError(
            f"{label} SHA-256 mismatch: expected={expected_sha256.upper()} actual={actual}"
        )
    return data


def validate_output_root(output_root: Path, inputs: Sequence[Path]) -> Path:
    resolved = output_root.resolve()
    if TMP_ROOT not in resolved.parents:
        raise ComposeError(f"output root must be a child of {TMP_ROOT}: {resolved}")
    if resolved == TMP_ROOT:
        raise ComposeError("tmp root itself cannot be an output root")
    for source in inputs:
        source = source.resolve()
        if resolved == source or resolved in source.parents or source in resolved.parents:
            raise ComposeError(f"output root overlaps input: {source}")
    if resolved.exists() and any(resolved.iterdir()):
        raise ComposeError(f"output root must be absent or empty: {resolved}")
    return resolved


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


def compose(base_blob: bytes, font_blob: bytes) -> tuple[bytes, dict[str, Any]]:
    base = LZ4.parse_link(base_blob)
    font = LZ4.parse_link(font_blob)
    if LZ4.rebuild_link(base) != base_blob:
        raise ComposeError("base LINK parse/rebuild identity failed")
    if LZ4.rebuild_link(font) != font_blob:
        raise ComposeError("font LINK parse/rebuild identity failed")
    if len(base.entries) != len(font.entries) or len(base.entries) <= 7:
        raise ComposeError("base/font LINK entry sets are incompatible")

    replacements = {
        entry: FONT.extract_raw_entry(font, entry, f"font candidate entry {entry}")
        for entry in (6, 7)
    }
    candidate_blob = FONT.build_candidate_archive(base_blob, replacements)
    candidate = LZ4.parse_link(candidate_blob)
    if LZ4.rebuild_link(candidate) != candidate_blob:
        raise ComposeError("composed LINK parse/rebuild identity failed")

    preserved = []
    for index, base_entry in enumerate(base.entries):
        if index in replacements:
            actual = FONT.extract_raw_entry(candidate, index, f"composed entry {index}")
            if actual != replacements[index]:
                raise ComposeError(f"composed font entry {index} differs from verified source")
        else:
            if candidate.entries[index].data != base_entry.data:
                raise ComposeError(f"untouched LINK entry {index} changed")
            preserved.append(index)

    title_index = 3
    title_sha = sha256(base.entries[title_index].data)
    if sha256(candidate.entries[title_index].data) != title_sha:
        raise ComposeError("title-image LINK entry 3 changed")
    report = {
        "schema": "nobu16.kr.pc-font-candidate-compose.v1",
        "file_only": True,
        "process_memory_access": False,
        "dll_injection": False,
        "hooking": False,
        "executable_modified": False,
        "registry_modified": False,
        "installed_game_files_modified": False,
        "replacement_entries": [
            {"entry": entry, "raw_sha256": sha256(replacements[entry]), "raw_size": len(replacements[entry])}
            for entry in (6, 7)
        ],
        "preserved_entry_count": len(preserved),
        "preserved_entry_indices": preserved,
        "title_images": {
            "outer_link_entry": title_index,
            "wrapped_sha256": title_sha,
            "byte_identical_to_base": True,
        },
        "link_roundtrip_exact": True,
    }
    return candidate_blob, report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-archive", type=Path, required=True)
    parser.add_argument("--base-sha256", required=True)
    parser.add_argument("--font-candidate", type=Path, required=True)
    parser.add_argument("--font-sha256", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        base_path = args.base_archive.resolve()
        font_path = args.font_candidate.resolve()
        output_root = validate_output_root(args.output_root, (base_path, font_path))
        base_blob = require_input(base_path, args.base_sha256, "base archive")
        font_blob = require_input(font_path, args.font_sha256, "verified font candidate")
        candidate, report = compose(base_blob, font_blob)
        report["inputs"] = {
            "base_archive": {"sha256": sha256(base_blob), "size": len(base_blob)},
            "font_candidate": {"sha256": sha256(font_blob), "size": len(font_blob)},
        }
        report["candidate"] = {"sha256": sha256(candidate), "size": len(candidate)}
        archive_path = output_root / "private" / "candidate" / "res_lang.SC.font-composed.bin"
        report_path = output_root / "build_report.json"
        atomic_write(archive_path, candidate)
        atomic_write(
            report_path,
            (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        )
        print(f"candidate={archive_path}")
        print(f"candidate_sha256={report['candidate']['sha256']}")
        print("title_images_byte_identical=True")
        print("installed_game_files_modified=False")
        return 0
    except (ComposeError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
