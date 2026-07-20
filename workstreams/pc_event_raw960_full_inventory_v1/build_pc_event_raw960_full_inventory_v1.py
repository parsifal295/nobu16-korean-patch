#!/usr/bin/env python3
"""Create a hash-pinned, read-only inventory for the live PK event route.

The earlier full-layout reviews use a pre-static-007 912px/three-line policy.
This inventory intentionally does not inherit those pass results.  It measures
the current Steam W71 target with the observed raw G1N 960px/four-line policy
and leaves any unresolved dynamic-name row on hold rather than manufacturing a
name-width reservation.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
INVENTORY_PATH = TMP_ROOT / "inventory.v1.jsonl"
SUMMARY_PATH = TMP_ROOT / "summary.v1.json"
W71_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_anegawa_raw960_wave71_v1"
    / "build_pc_event_anegawa_raw960_wave71_v1.py"
)
STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
MSGEV_RELATIVE = "MSG_PK/JP/msgev.bin"

PK_BODY_START = 3_000
PK_BODY_END = 11_009
EXPECTED_BODY_ROW_COUNT = 8_006
EXPECTED_PACKED_SHA256 = "229A6EB7888BCC9838DC3B96F532F61F431FB3DEF5ED661D3253FF49F5D2991D"
EXPECTED_RAW_SHA256 = "0CA883CCAA94672F261640CA416FA5C2C15F2CFE112ED3D2523C156180DBEB15"
EXPECTED_PACKED_SIZE = 995_289
EXPECTED_RAW_SIZE = 991_376

RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
RAW_LINE_LIMIT_PX = 960
MAX_LINES = 4
DRAW_FONT_PX = 30

ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+ #0]*\d*(?:\.\d+)?[A-Za-z]")
LINEBREAK_RE = re.compile(r"\r\n|\n|\r")


class InventoryError(RuntimeError):
    """Raised when the live resource or inventory contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InventoryError(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise InventoryError(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


w71 = load_module("pc_event_wave71_for_raw960_inventory", W71_BUILDER)


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def jsonl_bytes(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return b"".join(
        (json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        for row in rows
    )


def require_under_tmp(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise InventoryError(f"output escapes private tmp root: {resolved}") from exc
    return resolved


def is_full_width_visible(character: str) -> bool:
    codepoint = ord(character)
    return (
        0x1100 <= codepoint <= 0x11FF
        or 0x3130 <= codepoint <= 0x318F
        or 0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xAC00 <= codepoint <= 0xD7AF
        or 0xF900 <= codepoint <= 0xFAFF
    )


def contains_linebreak_inside_colour(value: str) -> bool:
    in_span = False
    cursor = 0
    while cursor < len(value):
        if value[cursor] == "\x1b":
            token = value[cursor : cursor + 3]
            if ESC_RE.fullmatch(token) is None:
                return True
            if token == "\x1bCZ":
                if not in_span:
                    return True
                in_span = False
            else:
                if in_span:
                    return True
                in_span = True
            cursor += 3
            continue
        if in_span and value[cursor] in "\r\n":
            return True
        cursor += 1
    return in_span


def control_signature(value: str) -> Mapping[str, Any]:
    controls = []
    for character in value:
        if character in "\r\n\x1b":
            continue
        if unicodedata.category(character) == "Cc":
            controls.append(f"U+{ord(character):04X}")
    return {
        "esc_tags": ESC_RE.findall(value),
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf_tokens": PRINTF_RE.findall(value),
        "other_c0_controls": controls,
        "linebreak_count": len(LINEBREAK_RE.findall(value)),
        "linebreak_inside_colour_or_malformed_colour": contains_linebreak_inside_colour(value),
    }


def known_reservation(entry_id: int, token: str) -> tuple[str, str] | None:
    """Return only scene-specific reservations proved by W71, never global guesses."""
    if entry_id in set(w71.scene_ids()) and token in w71.RUNTIME_RESERVATIONS:
        return w71.RUNTIME_RESERVATIONS[token], "W71 Anegawa scene-specific conservative reservation"
    return None


def rendered_line(entry_id: int, source: str) -> Mapping[str, Any]:
    """Measure a manual line without pretending unresolved runtime names are known."""
    template: list[str] = []
    static_display: list[str] = []
    resolved_display: list[str] = []
    runtime: list[Mapping[str, Any]] = []
    unresolved = False
    cursor = 0
    while cursor < len(source):
        character = source[cursor]
        if character == "\x1b":
            token = source[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token: {token!r}")
            cursor += 3
            continue
        match = RUNTIME_RE.match(source, cursor)
        if match is not None:
            token = match.group(0)
            resolved = known_reservation(entry_id, token)
            template.append("{" + token + "}")
            if resolved is None:
                unresolved = True
                runtime.append(
                    {
                        "token": token,
                        "resolved_display": None,
                        "reservation_evidence": None,
                        "status": "unresolved_runtime_hold",
                    }
                )
            else:
                display, evidence = resolved
                static_display.append(display)
                resolved_display.append(display)
                runtime.append(
                    {
                        "token": token,
                        "resolved_display": display,
                        "reservation_evidence": evidence,
                        "status": "scene_specific_reservation",
                    }
                )
            cursor = match.end()
            continue
        require(unicodedata.category(character) != "Cc", f"unexpected visible control U+{ord(character):04X}")
        template.append(character)
        static_display.append(character)
        resolved_display.append(character)
        cursor += 1

    static_text = "".join(static_display)
    template_text = "".join(template)
    static_full = sum(1 for char in static_text if is_full_width_visible(char))
    static_half = len(static_text) - static_full
    static_raw = static_full * RAW_FULL_WIDTH_PX + static_half * RAW_HALF_WIDTH_PX
    display = None if unresolved else "".join(resolved_display)
    if display is None:
        full = half = raw = effective = over = margin = min_wrap = None
    else:
        full = sum(1 for char in display if is_full_width_visible(char))
        half = len(display) - full
        raw = full * RAW_FULL_WIDTH_PX + half * RAW_HALF_WIDTH_PX
        effective = math.ceil(raw * DRAW_FONT_PX / RAW_FULL_WIDTH_PX)
        over = raw > RAW_LINE_LIMIT_PX
        margin = RAW_LINE_LIMIT_PX - raw
        min_wrap = max(1, math.ceil(raw / RAW_LINE_LIMIT_PX))
    return {
        "display_string": display,
        "display_template": template_text,
        "static_display_string": static_text,
        "runtime_tokens": runtime,
        "raw_g1n_width_px": raw,
        "effective_width_px": effective,
        "full_width_character_count": full,
        "half_width_character_count": half,
        "raw_margin_px": margin,
        "over_live_raw_960px": over,
        "predicted_min_auto_wrap_lines": min_wrap,
        "static_raw_g1n_width_px": static_raw,
        "static_effective_width_px": math.ceil(static_raw * DRAW_FONT_PX / RAW_FULL_WIDTH_PX),
        "static_full_width_character_count": static_full,
        "static_half_width_character_count": static_half,
    }


def entry_row(entry_id: int, ko: str, jp: str) -> Mapping[str, Any]:
    ko_signature = control_signature(ko)
    jp_signature = control_signature(jp)
    lines = LINEBREAK_RE.sub("\n", ko).split("\n")
    metrics = [rendered_line(entry_id, line) for line in lines]
    has_unknown_runtime = any(
        item["status"] == "unresolved_runtime_hold"
        for metric in metrics
        for item in metric["runtime_tokens"]
    )
    control_match = {
        key: ko_signature[key] == jp_signature[key]
        for key in ("esc_tags", "runtime_tokens", "printf_tokens")
    }
    known_widths = [metric["raw_g1n_width_px"] for metric in metrics]
    max_known_width = max((width for width in known_widths if width is not None), default=None)
    predicted = [metric["predicted_min_auto_wrap_lines"] for metric in metrics]
    if ko_signature["linebreak_inside_colour_or_malformed_colour"]:
        status = "structural_colour_hold"
    elif not all(control_match.values()):
        status = "control_signature_hold"
    elif len(lines) > MAX_LINES:
        status = "manual_line_limit_fail"
    elif has_unknown_runtime:
        status = "runtime_reservation_hold"
    elif any(metric["over_live_raw_960px"] for metric in metrics):
        status = "raw_width_fail"
    elif entry_id in set(w71.scene_ids()):
        status = "W71_semantic_layout_reviewed"
    else:
        status = "semantic_layout_review_pending"
    return {
        "entry_id": entry_id,
        "current_ko_utf16le_sha256": text_hash(ko),
        "direct_pc_jp_utf16le_sha256": text_hash(jp),
        "jp_lf_policy": "ignored",
        "jp_manual_lf_count": jp_signature["linebreak_count"],
        "ko_manual_lf_count": ko_signature["linebreak_count"],
        "manual_line_count": len(lines),
        "max_manual_lines": MAX_LINES,
        "control_signature": {
            "current_ko": ko_signature,
            "direct_pc_jp": jp_signature,
            "cross_language_match": control_match,
        },
        "lines": [dict({"line_number": index + 1}, **metric) for index, metric in enumerate(metrics)],
        "max_known_raw_g1n_width_px": max_known_width,
        "predicted_min_total_auto_wrapped_lines": None if any(item is None for item in predicted) else sum(predicted),
        "status": status,
    }


def source_tables() -> tuple[bytes, bytes, Any, Any]:
    path = STEAM_ROOT / MSGEV_RELATIVE
    packed = path.read_bytes()
    require(len(packed) == EXPECTED_PACKED_SIZE, "live msgev packed size differs from W71 target")
    require(sha256(packed) == EXPECTED_PACKED_SHA256, "live msgev packed hash differs from W71 target")
    _header, raw, ko_table = w71.w66.w60.parse_table("current Steam PK event", packed)
    require(len(raw) == EXPECTED_RAW_SIZE, "live msgev raw size differs from W71 target")
    require(sha256(raw) == EXPECTED_RAW_SHA256, "live msgev raw hash differs from W71 target")
    jp_blob, _profile = w71.w66.w62.load_direct_jp_event()
    _jp_header, _jp_raw, jp_table = w71.w66.w60.parse_table("direct PC Japanese event", jp_blob)
    require(len(ko_table.texts) == len(jp_table.texts), "KO/JP event table length drift")
    return packed, raw, ko_table, jp_table


def build_inventory() -> tuple[tuple[Mapping[str, Any], ...], Mapping[str, Any]]:
    packed, raw, ko_table, jp_table = source_tables()
    ids = tuple(
        entry_id
        for entry_id in range(PK_BODY_START, PK_BODY_END + 1)
        if ko_table.texts[entry_id] and jp_table.texts[entry_id]
    )
    require(len(ids) == EXPECTED_BODY_ROW_COUNT, "PK event body scope drift")
    rows = tuple(entry_row(entry_id, ko_table.texts[entry_id], jp_table.texts[entry_id]) for entry_id in ids)
    statuses = Counter(str(row["status"]) for row in rows)
    runtime_tokens = Counter(
        token["token"]
        for row in rows
        for line in row["lines"]
        for token in line["runtime_tokens"]
    )
    topology = Counter(int(row["manual_line_count"]) for row in rows)
    summary = {
        "schema": "nobu16.kr.pc-event-raw960-full-inventory.v1",
        "candidate_only": False,
        "read_only": True,
        "semantic_completion": False,
        "route": {
            "resource": MSGEV_RELATIVE,
            "id_range": [PK_BODY_START, PK_BODY_END],
            "nonempty_ko_and_jp_rows": len(rows),
            "out_of_route_rows": len(ko_table.texts) - len(rows),
        },
        "input": {
            "steam_path": str(STEAM_ROOT / MSGEV_RELATIVE),
            "packed_sha256": sha256(packed),
            "packed_size": len(packed),
            "raw_sha256": sha256(raw),
            "raw_size": len(raw),
        },
        "layout_policy": {
            "word_wrap_metric": "raw G1N advances",
            "raw_full_width_px": RAW_FULL_WIDTH_PX,
            "raw_half_width_px": RAW_HALF_WIDTH_PX,
            "raw_line_limit_px": RAW_LINE_LIMIT_PX,
            "max_lines": MAX_LINES,
            "display_effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "japanese_source_linebreak_policy": "ignored",
        },
        "manual_line_topology": {str(key): topology[key] for key in sorted(topology)},
        "status_counts": dict(sorted(statuses.items())),
        "runtime_tokens": {
            "unique_token_count": len(runtime_tokens),
            "occurrence_count": sum(runtime_tokens.values()),
            "occurrences_by_token": dict(sorted(runtime_tokens.items())),
            "unresolved_policy": "hold; do not infer name width from same numeric event-table ID",
        },
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }
    return rows, summary


def write_outputs(rows: tuple[Mapping[str, Any], ...], summary: Mapping[str, Any]) -> Mapping[str, str]:
    root = require_under_tmp(TMP_ROOT)
    inventory = require_under_tmp(INVENTORY_PATH)
    summary_path = require_under_tmp(SUMMARY_PATH)
    root.mkdir(parents=True, exist_ok=True)
    staging_inventory = require_under_tmp(root / ".inventory.staging")
    staging_summary = require_under_tmp(root / ".summary.staging")
    require(not staging_inventory.exists() and not staging_summary.exists(), "stale inventory staging file exists")
    try:
        staging_inventory.write_bytes(jsonl_bytes(rows))
        staging_summary.write_bytes(canonical_json(summary))
        os.replace(staging_inventory, inventory)
        os.replace(staging_summary, summary_path)
    finally:
        staging_inventory.unlink(missing_ok=True)
        staging_summary.unlink(missing_ok=True)
    return {
        "inventory": inventory.relative_to(REPO).as_posix(),
        "summary": summary_path.relative_to(REPO).as_posix(),
    }


def validate_outputs(rows: tuple[Mapping[str, Any], ...], summary: Mapping[str, Any]) -> Mapping[str, Any]:
    inventory = require_under_tmp(INVENTORY_PATH)
    summary_path = require_under_tmp(SUMMARY_PATH)
    require(inventory.is_file() and summary_path.is_file(), "inventory outputs are missing; run write first")
    require(inventory.read_bytes() == jsonl_bytes(rows), "inventory output differs from current live input")
    require(summary_path.read_bytes() == canonical_json(summary), "summary output differs from current live input")
    return {
        "status": "PASS",
        "row_count": len(rows),
        "inventory": inventory.relative_to(REPO).as_posix(),
        "summary": summary_path.relative_to(REPO).as_posix(),
        "steam_game_resource_written": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "README_KO.md",
        WORKSTREAM / "build_pc_event_raw960_full_inventory_v1.py",
        WORKSTREAM / "test_pc_event_raw960_full_inventory_v1.py",
    ):
        require(path.is_file(), f"authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "write", "validate"))
    command = parser.parse_args().command
    rows, summary = build_inventory()
    if command == "profile":
        print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if command == "write":
        result = dict(write_outputs(rows, summary))
        result.update({"status": "PASS", "row_count": len(rows), "steam_game_resource_written": False})
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    source_whitespace_check()
    print(json.dumps(validate_outputs(rows, summary), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
