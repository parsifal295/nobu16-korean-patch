#!/usr/bin/env python3
"""Build and strictly verify the v0.94.1 dynamic clan-label resource overlay."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Sequence


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "tools"))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.dynamic-clan-force-label-validation.v1"
OVERLAY_SCHEMA = "nobu16.kr.dynamic-clan-force-label-overlay.v1"
OVERLAY_PATH = HERE / "dynamic_clan_force_label.overlay.v1.json"
VALIDATION_NAME = "validation.dynamic_clan_force_label.v1.json"
RESOURCE = Path("MSG_PK/JP/msgui.bin")
TARGET_ID = 1139
SOURCE_TEXT = "%s 세력"
TARGET_TEXT = "%s 가문"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")

INPUT_SPEC = {
    "packed_size": 122_733,
    "packed_sha256": "C737796FE317FCEB5F0D315548DE6F2BAA683FE17B85CCAE1818FC5BD43BBC50",
    "raw_size": 122_228,
    "raw_sha256": "2CF4626FD9C12C25118B1D38BCA8C053CDB59425AE3C8E0E721AB16CCDBD5DBF",
    "string_count": 5_100,
}
OUTPUT_SPEC = {
    "packed_size": 122_733,
    "packed_sha256": "61D1C6691B97058D02753C088F95FB044DA09E015520A9FA74CC2050C7113EC9",
    "raw_size": 122_228,
    "raw_sha256": "51478423FD99FF0F3231F5029F9E4998E05BA29C0CCA340400C87E7DE5047645",
}


class BuildError(RuntimeError):
    """Raised when an input, overlay, or surgical-output contract differs."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def utf16le_sha256(text: str) -> str:
    return sha256(text.encode("utf-16le"))


def resolved_under(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def packed_raw_spec(packed: bytes) -> tuple[dict[str, int | str], Any, bytes]:
    header, raw = decompress_wrapper(packed)
    return (
        {
            "packed_size": len(packed),
            "packed_sha256": sha256(packed),
            "raw_size": len(raw),
            "raw_sha256": sha256(raw),
        },
        header,
        raw,
    )


def load_overlay() -> dict[str, Any]:
    payload = json.loads(OVERLAY_PATH.read_text(encoding="utf-8"))
    if payload.get("schema") != OVERLAY_SCHEMA:
        raise BuildError("overlay schema differs")
    entries = payload.get("entries", ())
    if payload.get("entry_count") != 1 or len(entries) != 1:
        raise BuildError("overlay must contain exactly one entry")
    entry = entries[0]
    expected = {
        "resource": RESOURCE.as_posix(),
        "id": TARGET_ID,
        "source_ko": SOURCE_TEXT,
        "source_ko_utf16le_sha256": utf16le_sha256(SOURCE_TEXT),
        "ko": TARGET_TEXT,
        "ko_utf16le_sha256": utf16le_sha256(TARGET_TEXT),
        "reason": "use_the_same_clan_suffix_for_runtime_created_forces",
    }
    if entry != expected:
        raise BuildError("overlay entry differs")
    runtime = payload.get("runtime_contract", {})
    if runtime.get("format_marker") != TARGET_TEXT:
        raise BuildError("runtime format marker differs")
    if runtime.get("argument_normalization") != "trim_trailing_u0020_only":
        raise BuildError("runtime argument-normalization policy differs")
    if runtime.get("preserve_source_surname_spacing") is not True:
        raise BuildError("surname source-spacing policy differs")
    policy = payload.get("distribution_policy", {})
    if any(
        policy.get(key) is not False
        for key in (
            "contains_commercial_source_text",
            "contains_complete_game_resource",
            "contains_switch_binary",
        )
    ):
        raise BuildError("overlay distribution policy differs")
    return payload


def build_candidate(input_root: Path, output_root: Path) -> dict[str, Any]:
    input_root = input_root.resolve()
    output_root = output_root.resolve()
    if resolved_under(output_root, input_root):
        raise BuildError("output root must not be inside input root")
    if resolved_under(output_root, DEFAULT_STEAM_ROOT):
        raise BuildError("refusing to write a build candidate into the Steam installation")
    if output_root.exists() and any(output_root.iterdir()):
        raise BuildError(f"output root is not empty: {output_root}")

    overlay = load_overlay()
    source_path = input_root / RESOURCE
    if not source_path.is_file():
        raise BuildError(f"input resource is missing: {source_path}")
    packed = source_path.read_bytes()
    input_actual, header, raw = packed_raw_spec(packed)
    if input_actual != {key: INPUT_SPEC[key] for key in input_actual}:
        raise BuildError(f"input packed/raw pin differs: {input_actual}")
    if recompress_wrapper(raw, header) != packed:
        raise BuildError("input wrapper is not deterministic literal-only")

    table = parse_message_table(raw)
    if table.string_count != INPUT_SPEC["string_count"]:
        raise BuildError(f"input string count differs: {table.string_count}")
    if rebuild_message_table(table, table.texts) != raw:
        raise BuildError("input unchanged rebuild differs")
    if table.texts[TARGET_ID] != SOURCE_TEXT:
        raise BuildError(f"input target text differs: {table.texts[TARGET_ID]!r}")

    texts = list(table.texts)
    texts[TARGET_ID] = TARGET_TEXT
    rebuilt_raw = rebuild_message_table(table, texts)
    candidate = recompress_wrapper(rebuilt_raw, header)
    output_actual, output_header, decoded = packed_raw_spec(candidate)
    if output_actual != OUTPUT_SPEC:
        raise BuildError(f"output packed/raw pin differs: {output_actual}")
    if output_header.prefix != header.prefix or decoded != rebuilt_raw:
        raise BuildError("output wrapper round-trip differs")

    check = parse_message_table(decoded)
    changed = tuple(
        index
        for index, (before, after) in enumerate(zip(table.texts, check.texts, strict=True))
        if before != after
    )
    if changed != (TARGET_ID,) or check.texts[TARGET_ID] != TARGET_TEXT:
        raise BuildError(f"changed ID vector differs: {changed}")

    destination = output_root / RESOURCE
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(candidate)
    report = {
        "schema": SCHEMA,
        "release": "0.94.1",
        "resource": RESOURCE.as_posix(),
        "coordinate": [TARGET_ID],
        "changed_text_count": 1,
        "all_other_texts_unchanged": True,
        "input": input_actual,
        "target": output_actual,
        "runtime_contract": overlay["runtime_contract"],
    }
    validation = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    (output_root / VALIDATION_NAME).write_text(validation, encoding="utf-8", newline="\n")
    return report


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = build_candidate(args.input_root, args.output_root)
    except (BuildError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
