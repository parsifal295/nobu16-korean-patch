#!/usr/bin/env python3
"""Build a private, one-ID semantic reflow candidate for Steam JP msgev.

The only payload edit is ID 10564 in MSG_PK/JP/msgev.bin.  The current local
game state and the v0.10.0 release state are both explicit input profiles.
The game and font trees are read-only; generated candidates stay under tmp.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Mapping


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
GAME_ROOT = REPO.parent
TOOLS = REPO / "tools"
sys.path[:0] = [str(TOOLS)]

import build_common_message_overlay as common  # noqa: E402
import validate_g1n_surgical as g1n  # noqa: E402
from nobu16_lz4 import decompress_wrapper, parse_link, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


RESOURCE = Path("MSG_PK") / "JP" / "msgev.bin"
OVERLAY_PATH = WORKSTREAM / "public" / "msgev_ko_steam_jp_10564_compact_layout.v1.json"
CONTRACT_PATH = WORKSTREAM / "verification.v1.json"
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / "steam_jp_msgev_10564_compact_layout_v1" / "candidate"

OVERLAY_SCHEMA = "nobu16.kr.steam-jp-msgev-10564-compact-layout-overlay.v1"
CONTRACT_SCHEMA = "nobu16.kr.steam-jp-msgev-10564-compact-layout-verification.v1"
ENTRY_ID = 10564
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_BRACKET_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")


class LayoutError(ValueError):
    """Raised when the pinned input or compact layout contract diverges."""


def require(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise LayoutError(f"{label} differs: expected={expected!r}, actual={actual!r}")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def file_spec(path: Path) -> dict[str, Any]:
    blob = path.read_bytes()
    return {"size": len(blob), "sha256": sha256_bytes(blob)}


def read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LayoutError(f"cannot read JSON: {path}") from exc
    if not isinstance(value, dict):
        raise LayoutError(f"JSON root is not an object: {path}")
    return value


def message_profile(value: str) -> dict[str, Any]:
    invariant = common.message_invariants(value)
    return {
        "printf": list(invariant["printf"]),
        "unknown_percent_count": invariant["unknown_percent_count"],
        "esc": list(invariant["esc"]),
        "controls": list(invariant["controls"]),
        "pua": list(invariant["pua"]),
        "runtime_brackets": RUNTIME_BRACKET_RE.findall(value),
        "leading_whitespace": invariant["leading_whitespace"],
        "trailing_whitespace": invariant["trailing_whitespace"],
        "line_breaks": list(invariant["line_breaks"]),
    }


def load_contract() -> dict[str, Any]:
    contract = read_object(CONTRACT_PATH)
    require(contract.get("schema"), CONTRACT_SCHEMA, "verification schema")
    require(contract.get("resource"), RESOURCE.as_posix(), "verification resource")
    profiles = contract.get("source_profiles")
    if not isinstance(profiles, list) or len(profiles) != 2:
        raise LayoutError("verification source profile count differs")
    names: set[str] = set()
    for profile in profiles:
        if not isinstance(profile, Mapping):
            raise LayoutError("verification source profile is invalid")
        name = profile.get("name")
        packed = profile.get("packed")
        count = profile.get("string_count")
        if not isinstance(name, str) or not name or name in names:
            raise LayoutError("verification source profile name is invalid")
        names.add(name)
        if not isinstance(packed, Mapping) or not isinstance(packed.get("size"), int) or not isinstance(packed.get("sha256"), str):
            raise LayoutError(f"verification packed profile is invalid: {name}")
        if not isinstance(count, int) or count < ENTRY_ID:
            raise LayoutError(f"verification string count is invalid: {name}")
    font = contract.get("font")
    if not isinstance(font, Mapping):
        raise LayoutError("verification font is absent")
    require(font.get("resource"), "RES_JP/res_lang.bin", "verification font resource")
    require(font.get("outer_entry"), 6, "verification font entry")
    require(font.get("table"), 0, "verification font table")
    require(font.get("target_advance_px"), 48, "verification font advance")
    require(font.get("max_line_px"), 912, "verification maximum line width")
    return contract


def load_entry() -> dict[str, Any]:
    overlay = read_object(OVERLAY_PATH)
    require(overlay.get("schema"), OVERLAY_SCHEMA, "overlay schema")
    require(overlay.get("resource"), RESOURCE.as_posix(), "overlay resource")
    entries = overlay.get("entries")
    if not isinstance(entries, list) or len(entries) != 1 or not isinstance(entries[0], dict):
        raise LayoutError("overlay must contain exactly one entry")
    entry = entries[0]
    require(entry.get("id"), ENTRY_ID, "overlay ID")
    require(entry.get("operation"), "manual_compact_korean_layout", "overlay operation")
    for key in ("preimage_utf16le_sha256", "target_utf16le_sha256", "ko"):
        if not isinstance(entry.get(key), str) or not entry[key]:
            raise LayoutError(f"overlay {key} is invalid")
    if text_hash(entry["ko"]) != entry["target_utf16le_sha256"]:
        raise LayoutError("overlay target text hash differs")
    for key in ("source_line_breaks", "target_line_breaks"):
        if entry.get(key) != ["\n", "\n"]:
            raise LayoutError(f"overlay {key} differs")
    preserved = entry.get("preserved")
    if not isinstance(preserved, Mapping):
        raise LayoutError("overlay preservation profile is absent")
    required_preserved = {
        "printf": [],
        "unknown_percent_count": 0,
        "esc": ["\x1bCB", "\x1bCZ", "\x1bCB", "\x1bCZ", "\x1bCA", "\x1bCZ", "\x1bCB", "\x1bCZ", "\x1bCB", "\x1bCZ"],
        "controls": [],
        "pua": [],
        "runtime_brackets": [],
        "leading_whitespace": "",
        "trailing_whitespace": "",
    }
    require(dict(preserved), required_preserved, "overlay preservation profile")
    layout = entry.get("layout")
    if not isinstance(layout, Mapping):
        raise LayoutError("overlay layout is absent")
    require(layout.get("font_resource"), "RES_JP/res_lang.bin", "overlay font resource")
    require(layout.get("outer_entry"), 6, "overlay font entry")
    require(layout.get("table"), 0, "overlay font table")
    require(layout.get("max_line_px"), 912, "overlay max line width")
    require(layout.get("line_widths_px"), [816, 888, 768], "overlay line widths")
    target_profile = message_profile(entry["ko"])
    for key, expected in required_preserved.items():
        require(target_profile[key], expected, f"overlay target {key}")
    require(target_profile["line_breaks"], entry["target_line_breaks"], "overlay target line breaks")
    return entry


def source_profile(contract: Mapping[str, Any], packed: bytes) -> dict[str, Any]:
    observed = {"size": len(packed), "sha256": sha256_bytes(packed)}
    for profile in contract["source_profiles"]:
        if observed == dict(profile["packed"]):
            return dict(profile)
    raise LayoutError(f"unsupported MSGEV packed input: {observed}")


def font_table(game_root: Path, entry: Mapping[str, Any], contract: Mapping[str, Any]) -> tuple[Any, dict[str, Any]]:
    font_path = game_root / Path(entry["layout"]["font_resource"])
    if not font_path.is_file():
        raise LayoutError(f"missing font resource: {font_path}")
    archive = parse_link(font_path.read_bytes())
    outer_entry = int(entry["layout"]["outer_entry"])
    if not 0 <= outer_entry < len(archive.entries):
        raise LayoutError("font outer entry is absent")
    try:
        _, raw = decompress_wrapper(archive.entries[outer_entry].data)
    except Exception as exc:
        raise LayoutError("font outer entry is not an LZ4 G1N") from exc
    with tempfile.TemporaryDirectory(prefix="nobu16_msgev_layout_") as temp_dir:
        g1n_path = Path(temp_dir) / "font.g1n"
        g1n_path.write_bytes(raw)
        parsed = g1n.parse_g1n(g1n_path)
    if parsed.structural_errors:
        raise LayoutError(f"font G1N structural error: {parsed.structural_errors[0]}")
    table_index = int(entry["layout"]["table"])
    if not 0 <= table_index < len(parsed.tables):
        raise LayoutError("font table is absent")
    return parsed.tables[table_index], file_spec(font_path)


def visual_line_widths(value: str, glyph_advance: Callable[[str], int]) -> list[int]:
    widths: list[int] = []
    for line in value.split("\n"):
        width = 0
        cursor = 0
        while cursor < len(line):
            if line[cursor] == "\x1b":
                token = line[cursor : cursor + 3]
                if ESC_RE.fullmatch(token) is None:
                    raise LayoutError("malformed ESC token in layout text")
                cursor += 3
                continue
            char = line[cursor]
            if ord(char) < 0x20:
                raise LayoutError("unexpected control token in layout text")
            width += glyph_advance(char)
            cursor += 1
        widths.append(width)
    return widths


def glyph_advance_from_table(table: Any, expected_advance: int) -> Callable[[str], int]:
    def advance(char: str) -> int:
        codepoint = ord(char)
        if codepoint >= len(table.mapping):
            raise LayoutError(f"codepoint outside font map: U+{codepoint:04X}")
        ordinal = table.mapping[codepoint]
        if ordinal == 0 or ordinal >= len(table.records):
            raise LayoutError(f"missing glyph: U+{codepoint:04X}")
        record = table.records[ordinal]
        if record.width != record.advance:
            raise LayoutError(f"non-square glyph metric: U+{codepoint:04X}")
        if record.advance not in (24, expected_advance):
            raise LayoutError(f"unexpected glyph advance {record.advance}: U+{codepoint:04X}")
        return record.advance

    return advance


def validate_entry(before: str, entry: Mapping[str, Any]) -> None:
    require(text_hash(before), entry["preimage_utf16le_sha256"], "ID 10564 preimage hash")
    source = message_profile(before)
    for key, expected in entry["preserved"].items():
        require(source[key], expected, f"ID 10564 source {key}")
    require(source["line_breaks"], entry["source_line_breaks"], "ID 10564 source line breaks")


def candidate_from_game(game_root: Path) -> tuple[bytes, dict[str, Any]]:
    contract = load_contract()
    entry = load_entry()
    source_path = game_root / RESOURCE
    if not source_path.is_file():
        raise LayoutError(f"missing message resource: {source_path}")
    packed = source_path.read_bytes()
    profile = source_profile(contract, packed)
    header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    require(table.string_count, profile["string_count"], "source string count")
    require(rebuild_message_table(table, table.texts), raw, "source parse/rebuild")
    if ENTRY_ID >= table.string_count:
        raise LayoutError("ID 10564 is outside the source table")
    before = table.texts[ENTRY_ID]
    validate_entry(before, entry)

    font, font_spec = font_table(game_root, entry, contract)
    advance = glyph_advance_from_table(font, int(contract["font"]["target_advance_px"]))
    widths = visual_line_widths(entry["ko"], advance)
    require(widths, entry["layout"]["line_widths_px"], "target pixel widths")
    if len(widths) != 3 or any(width > int(entry["layout"]["max_line_px"]) for width in widths):
        raise LayoutError("target does not fit the three-line layout budget")

    final_texts = list(table.texts)
    final_texts[ENTRY_ID] = entry["ko"]
    candidate_raw = rebuild_message_table(table, final_texts)
    candidate = recompress_wrapper(candidate_raw, header)
    candidate_header, roundtrip_raw = decompress_wrapper(candidate)
    require(candidate_header.prefix, header.prefix, "candidate wrapper prefix")
    require(roundtrip_raw, candidate_raw, "candidate wrapper round-trip")
    candidate_table = parse_message_table(candidate_raw)
    require(candidate_table.texts, tuple(final_texts), "candidate text round-trip")
    changed_ids = [
        index
        for index, (source, target) in enumerate(zip(table.texts, candidate_table.texts))
        if source != target
    ]
    require(changed_ids, [ENTRY_ID], "candidate changed coordinate domain")
    report = {
        "source_profile": profile["name"],
        "source": {"packed": file_spec(source_path), "raw_sha256": sha256_bytes(raw), "string_count": table.string_count},
        "candidate": {"packed": {"size": len(candidate), "sha256": sha256_bytes(candidate)}, "raw_sha256": sha256_bytes(candidate_raw)},
        "changed_ids": changed_ids,
        "layout": {"line_widths_px": widths, "max_line_px": entry["layout"]["max_line_px"], "font": font_spec},
        "checks": {
            "preimage_hash": "OK",
            "preserved_tokens": "OK",
            "three_line_pixel_budget": "OK",
            "single_coordinate_domain": "OK",
            "parse_rebuild_round_trip": "OK",
        },
    }
    return candidate, report


def output_root(path: Path) -> Path:
    output = path.resolve()
    allowed = (REPO / "tmp").resolve()
    try:
        output.relative_to(allowed)
    except ValueError as exc:
        raise LayoutError("output root must stay below KR_PATCH_WORK/tmp") from exc
    if output == allowed:
        raise LayoutError("tmp itself cannot be the output root")
    return output


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_bytes(data)
    os.replace(temp, path)


def run_verify(args: argparse.Namespace) -> int:
    _, report = candidate_from_game(args.game_root.resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def run_build(args: argparse.Namespace) -> int:
    candidate, report = candidate_from_game(args.game_root.resolve())
    root = output_root(args.out_root)
    atomic_write(root / RESOURCE, candidate)
    atomic_write(root / "manifest.v1.json", (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    print(json.dumps({"output": str(root), **report}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify", "build"))
    parser.add_argument("--game-root", type=Path, default=GAME_ROOT)
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run_verify(args) if args.command == "verify" else run_build(args)


if __name__ == "__main__":
    raise SystemExit(main())
