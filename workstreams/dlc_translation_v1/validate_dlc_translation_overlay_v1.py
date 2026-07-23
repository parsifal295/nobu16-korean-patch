#!/usr/bin/env python3
"""Validate a source-free DLC Korean overlay against the private catalogue."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import unicodedata
from pathlib import Path
from typing import Any, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
DEFAULT_CATALOG = WORKSTREAM / "private" / "catalog.private.v1.json"
DEFAULT_OVERLAY = WORKSTREAM / "translations.wave01.scenario.v1.json"
DEFAULT_OUTPUT = WORKSTREAM / "validation.wave01.scenario.v1.json"
DEFAULT_RESERVATIONS = WORKSTREAM / "event_token_reservations.v1.json"

SCHEMA = "nobu16.kr.dlc-translation-overlay.v1"
VALIDATION_SCHEMA = "nobu16.kr.dlc-translation-overlay-validation.v1"
ESC_RE = re.compile(r"\x1bC[A-Z]")
RUNTIME_TOKEN_RE = re.compile(r"\[(?:bm?|[A-Za-z]+)\d+\]")
PRINTF_RE = re.compile(
    r"%(?:\d+\$)?[-+#0 ']*\d*(?:\.\d+)?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)
SOURCE_SCRIPT_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uf900-\ufaff]")

RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
RUNTIME_FULL_WIDTH_PX = 30
EVENT_MAX_EFFECTIVE_WIDTH_PX = 912
EVENT_MAX_LINES = 4


class OverlayError(ValueError):
    """Raised when an overlay violates the translation contract."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise OverlayError(f"JSON root must be an object: {path}")
    return value


def protected_tokens(text: str) -> list[str]:
    found: list[tuple[int, str]] = []
    for pattern in (ESC_RE, RUNTIME_TOKEN_RE, PRINTF_RE):
        found.extend((match.start(), match.group(0)) for match in pattern.finditer(text))
    return [value for _, value in sorted(found)]


def is_full_width(char: str) -> bool:
    codepoint = ord(char)
    return (
        0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xF900 <= codepoint <= 0xFAFF
        or 0xAC00 <= codepoint <= 0xD7A3
        or 0x1100 <= codepoint <= 0x11FF
        or 0x3130 <= codepoint <= 0x318F
        or 0xA960 <= codepoint <= 0xA97F
        or 0xD7B0 <= codepoint <= 0xD7FF
    )


def event_line_layout(
    line: str, reservation_rows: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    visible = ESC_RE.sub("", line)
    full = 0
    half = 0
    runtime: list[dict[str, Any]] = []
    cursor = 0
    for match in RUNTIME_TOKEN_RE.finditer(visible):
        plain = visible[cursor : match.start()]
        for char in plain:
            if unicodedata.category(char) == "Cc":
                raise OverlayError(
                    f"unexpected event layout control U+{ord(char):04X}"
                )
            if is_full_width(char):
                full += 1
            else:
                half += 1
        token = match.group(0)
        try:
            reservation = reservation_rows[token]
        except KeyError as exc:
            raise OverlayError(f"runtime token has no DLC reservation: {token}") from exc
        token_full = reservation["full_width_characters"]
        token_half = reservation["half_width_characters"]
        if type(token_full) is not int or type(token_half) is not int:
            raise OverlayError(f"runtime token reservation shape differs: {token}")
        full += token_full
        half += token_half
        runtime.append(
            {
                "token": token,
                "source_name_id": reservation["source_name_id"],
                "raw_g1n_width_px": reservation["raw_g1n_width_px"],
                "scaled_effective_width_px": reservation[
                    "scaled_effective_width_px"
                ],
            }
        )
        cursor = match.end()
    for char in visible[cursor:]:
        if unicodedata.category(char) == "Cc":
            raise OverlayError(f"unexpected event layout control U+{ord(char):04X}")
        if is_full_width(char):
            full += 1
        else:
            half += 1
    raw = full * RAW_FULL_WIDTH_PX + half * RAW_HALF_WIDTH_PX
    effective = math.ceil(raw * RUNTIME_FULL_WIDTH_PX / RAW_FULL_WIDTH_PX)
    return {
        "visible_string": visible,
        "raw_g1n_width_px": raw,
        "scaled_effective_width_px": effective,
        "full_width_character_count": full,
        "half_width_character_count": half,
        "runtime_token_reservations": runtime,
        "exceeds_912px": effective > EVENT_MAX_EFFECTIVE_WIDTH_PX,
    }


def select_scoped_placements(
    catalog: dict[str, Any], scope: dict[str, Any]
) -> list[dict[str, Any]]:
    if set(scope) == {"path_regex"}:
        try:
            path_re = re.compile(scope["path_regex"])
        except (TypeError, re.error) as exc:
            raise OverlayError(f"invalid scope path_regex: {exc}") from exc
        return [
            value
            for value in catalog["placements"]
            if path_re.fullmatch(value["path"])
        ]
    if set(scope) == {"placement_ids"}:
        placement_ids = scope["placement_ids"]
        if (
            not isinstance(placement_ids, list)
            or not placement_ids
            or any(not isinstance(value, str) for value in placement_ids)
            or len(set(placement_ids)) != len(placement_ids)
        ):
            raise OverlayError("scope placement_ids must be unique nonempty strings")
        by_id = {
            value["placement_id"]: value for value in catalog["placements"]
        }
        missing = set(placement_ids) - set(by_id)
        if missing:
            raise OverlayError(f"scope contains unknown placement IDs: {sorted(missing)}")
        return [by_id[value] for value in placement_ids]
    raise OverlayError("scope must contain exactly path_regex or placement_ids")


def validate_overlay(
    catalog: dict[str, Any],
    overlay: dict[str, Any],
    reservations: dict[str, Any],
) -> dict[str, Any]:
    if overlay.get("schema") != SCHEMA:
        raise OverlayError("overlay schema changed")
    scope = overlay.get("scope")
    if not isinstance(scope, dict):
        raise OverlayError("scope must be an object")

    sources = {value["source_id"]: value for value in catalog["sources"]}
    scoped_placements = select_scoped_placements(catalog, scope)
    if not scoped_placements:
        raise OverlayError("overlay scope selects zero catalogue placements")
    scoped_source_ids = {value["source_id"] for value in scoped_placements}

    entries = overlay.get("entries")
    if not isinstance(entries, list):
        raise OverlayError("entries must be an array")
    seen: set[str] = set()
    validations: list[dict[str, Any]] = []
    event_layout_rows = 0
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or set(entry) != {"source_id", "ko"}:
            raise OverlayError(f"entry {index} must contain exactly source_id and ko")
        source_id = entry["source_id"]
        ko = entry["ko"]
        if not isinstance(source_id, str) or source_id in seen:
            raise OverlayError(f"invalid or duplicate source_id at entry {index}")
        seen.add(source_id)
        if source_id not in scoped_source_ids:
            raise OverlayError(f"entry is outside overlay scope: {source_id}")
        if not isinstance(ko, str) or not ko:
            raise OverlayError(f"empty Korean translation: {source_id}")
        if SOURCE_SCRIPT_RE.search(ko):
            raise OverlayError(f"Japanese/Chinese source script remains: {source_id}")
        source = sources[source_id]
        jp = source["jp"]
        if protected_tokens(ko) != protected_tokens(jp):
            raise OverlayError(f"protected token sequence changed: {source_id}")
        selected = [
            value for value in scoped_placements if value["source_id"] == source_id
        ]
        if any(value["family"] == "scem" for value in selected):
            if ko.count("\n") != jp.count("\n"):
                raise OverlayError(f"scenario line count changed: {source_id}")
        validation = {
            "source_id": source_id,
            "target_placements": [value["placement_id"] for value in selected],
            "ko_utf16le_sha256": sha256(ko.encode("utf-16le")),
            "line_count": ko.count("\n") + 1,
            "protected_tokens": protected_tokens(ko),
        }
        event_selected = [value for value in selected if value["family"] == "evm"]
        if event_selected:
            lines = re.split(r"\r\n|\r|\n", ko)
            if len(lines) > EVENT_MAX_LINES:
                raise OverlayError(
                    f"event row exceeds {EVENT_MAX_LINES} lines: {source_id}"
                )
            line_layouts = [
                event_line_layout(line, reservations["reservations"]) for line in lines
            ]
            if any(value["exceeds_912px"] for value in line_layouts):
                raise OverlayError(
                    f"event row exceeds {EVENT_MAX_EFFECTIVE_WIDTH_PX}px: {source_id}"
                )
            validation["event_layout"] = [
                {
                    "placement_id": placement["placement_id"],
                    "line_count": len(lines),
                    "lines": line_layouts,
                }
                for placement in event_selected
            ]
            event_layout_rows += len(event_selected)
        validations.append(validation)

    missing = scoped_source_ids - seen
    extra = seen - scoped_source_ids
    if missing or extra:
        raise OverlayError(
            f"overlay coverage mismatch: missing={sorted(missing)}, extra={sorted(extra)}"
        )
    overlay_blob = canonical_json(overlay)
    return {
        "schema": VALIDATION_SCHEMA,
        "wave": overlay.get("wave"),
        "overlay_sha256": sha256(overlay_blob),
        "private_catalog_sha256": sha256(canonical_json(catalog)),
        "summary": {
            "entries": len(entries),
            "target_placements": len(scoped_placements),
            "unique_sources": len(scoped_source_ids),
            "protected_token_failures": 0,
            "source_script_residuals": 0,
            "scenario_line_count_failures": 0,
            "event_layout_rows": event_layout_rows,
            "event_layout_failures": 0,
            "event_layout_baseline": {
                "raw_full_width_px": RAW_FULL_WIDTH_PX,
                "raw_half_width_px": RAW_HALF_WIDTH_PX,
                "effective_scale": "30/48",
                "max_effective_width_px": EVENT_MAX_EFFECTIVE_WIDTH_PX,
                "max_lines": EVENT_MAX_LINES,
            },
            "steam_writes": 0,
        },
        "entries": sorted(validations, key=lambda value: value["source_id"]),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--overlay", type=Path, default=DEFAULT_OVERLAY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--reservations", type=Path, default=DEFAULT_RESERVATIONS)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--validate", action="store_true")
    args = parser.parse_args(argv)

    catalog = read_json(args.catalog)
    overlay = read_json(args.overlay)
    reservations = read_json(args.reservations)
    validation = validate_overlay(catalog, overlay, reservations)
    blob = canonical_json(validation)
    if args.write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(blob)
    elif not args.output.is_file() or args.output.read_bytes() != blob:
        raise OverlayError(f"validation artifact drifted: {args.output}")
    print(json.dumps(validation["summary"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
