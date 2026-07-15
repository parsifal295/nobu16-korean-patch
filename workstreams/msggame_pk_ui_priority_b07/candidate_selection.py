#!/usr/bin/env python3
"""Deterministically select the 300 source-free B07 PK msggame UI coordinates."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
B04_ROOT = REPO_ROOT / "workstreams" / "msggame_pk_ui_priority_b04"
RESOURCE = "MSG_PK/SC/msggame.bin"
SELF_RELATIVE = (
    WORKSTREAM_ROOT / "public" / "msggame_ko_pk_ui_priority_b07_300.v1.json"
).relative_to(REPO_ROOT).as_posix()
B06_RELATIVE = (
    REPO_ROOT
    / "workstreams"
    / "msggame_pk_ui_priority_b06"
    / "public"
    / "msggame_ko_pk_ui_priority_b06_300.v1.json"
).relative_to(REPO_ROOT).as_posix()

# B06 is the immutable selection boundary.  Self and future registrations are
# validated but deliberately excluded from the input set used to select B07.
PREFIX_PATTERN_COUNT = 33
PREFIX_PATTERNS_SHA256 = "91EAF864168DAD3E05417F0FFB8E723ABEDD0761739AB40EEE1525C16893DDB2"
PREFIX_ENTRY_COUNT = 11_422
PREFIX_COORDINATES_SHA256 = "07BE1759E63D2A3690F5ED2A0DB3E3966531C1E487028B6574FDFDCB67722A8A"
B07_COORDINATES_SHA256 = "51D54B18F1E4BB88F8123DF0B16DF4630B52D8A04958648F6B11591FAA9178ED"
SELF_OVERLAY_SHA256 = "6292D829DA64C1E3A0476CF0B3248161E7317AB53D6F0D00B98663F5BAF74BD6"


def _load_b04() -> Any:
    spec = importlib.util.spec_from_file_location(
        "msggame_pk_ui_priority_b04_builder_for_b07",
        B04_ROOT / "build_msggame_pk_ui_priority_b04.py",
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the pinned B04 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _progress_patterns(progress_path: Path) -> list[str]:
    progress = _read_json(progress_path)
    resources = progress.get("resources")
    matches = [item for item in resources if item.get("path") == RESOURCE] if isinstance(resources, list) else []
    if len(matches) != 1:
        raise ValueError("progress must contain exactly one PK msggame resource")
    patterns = matches[0].get("overlay_globs")
    if not isinstance(patterns, list) or not all(isinstance(value, str) for value in patterns):
        raise ValueError("PK msggame progress overlay list is invalid")
    return patterns


def _resolve_pattern(pattern: str) -> Path:
    matches = sorted(REPO_ROOT.glob(pattern))
    if len(matches) != 1:
        raise ValueError(f"progress pattern {pattern!r} resolved to {len(matches)} files")
    return matches[0]


def _overlay_coordinates(builder: Any, path: Path) -> set[tuple[int, int, int]]:
    payload = _read_json(path)
    if payload.get("resource") != RESOURCE:
        raise ValueError(f"overlay resource mismatch: {path}")
    policy = payload.get("distribution_policy")
    if (
        not isinstance(policy, dict)
        or policy.get("contains_commercial_source_text") is not False
        or policy.get("contains_complete_game_resource") is not False
    ):
        raise ValueError(f"overlay lacks an explicit source-free distribution policy: {path}")
    entries = payload.get("entries")
    if not isinstance(entries, list):
        raise ValueError(f"overlay entries are invalid: {path}")
    coordinates: set[tuple[int, int, int]] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError(f"overlay entry is invalid: {path}")
        coordinate = (entry.get("block_id"), entry.get("record_id"), entry.get("literal_id"))
        if not all(type(value) is int for value in coordinate):
            raise ValueError(f"overlay coordinate is invalid: {path}")
        coordinates.add(coordinate)
    if len(coordinates) != len(entries):
        raise ValueError(f"overlay contains duplicate coordinates: {path}")
    if builder.script_counts(path.read_text(encoding="utf-8")) != {
        "cjk_unified_count": 0,
        "kana_count": 0,
    }:
        raise ValueError(f"commercial source script leaked into overlay: {path}")
    return coordinates


def _history(
    builder: Any,
    progress_path: Path,
) -> dict[str, Any]:
    patterns = _progress_patterns(progress_path)
    if patterns.count(B06_RELATIVE) != 1:
        raise ValueError("B06 boundary must be registered exactly once")
    boundary = patterns.index(B06_RELATIVE)
    prefix_patterns = patterns[: boundary + 1]
    suffix_patterns = patterns[boundary + 1 :]
    if len(prefix_patterns) != PREFIX_PATTERN_COUNT:
        raise ValueError("B06 prefix pattern count changed")
    if builder.canonical_hash(prefix_patterns) != PREFIX_PATTERNS_SHA256:
        raise ValueError("B06 prefix pattern order changed")

    prefix_coordinates: set[tuple[int, int, int]] = set()
    for pattern in prefix_patterns:
        coordinates = _overlay_coordinates(builder, _resolve_pattern(pattern))
        overlap = prefix_coordinates & coordinates
        if overlap:
            raise ValueError(f"registered prefix overlays overlap at {sorted(overlap)[:3]}")
        prefix_coordinates.update(coordinates)
    if len(prefix_coordinates) != PREFIX_ENTRY_COUNT:
        raise ValueError("B06 prefix entry count changed")
    if (
        builder.canonical_hash([list(value) for value in sorted(prefix_coordinates)])
        != PREFIX_COORDINATES_SHA256
    ):
        raise ValueError("B06 prefix coordinate set changed")

    self_coordinates: set[tuple[int, int, int]] = set()
    future_coordinates: set[tuple[int, int, int]] = set()
    future_paths: list[str] = []
    self_count = 0
    for pattern in suffix_patterns:
        resolved = _resolve_pattern(pattern)
        if resolved.relative_to(REPO_ROOT).as_posix() != pattern:
            raise ValueError("post-B06 overlays must use exact logical paths")
        coordinates = _overlay_coordinates(builder, resolved)
        if coordinates & prefix_coordinates:
            raise ValueError(f"post-B06 overlay overlaps the immutable prefix: {pattern}")
        if pattern == SELF_RELATIVE:
            self_count += 1
            if self_count != 1:
                raise ValueError("B07 self overlay is registered more than once")
            if builder.sha256(resolved.read_bytes()) != SELF_OVERLAY_SHA256:
                raise ValueError("B07 self overlay SHA-256 changed")
            if _read_json(resolved).get("overlay_id") != "msggame_pk_ui_priority_b07_300.v1":
                raise ValueError("B07 self overlay id changed")
            self_coordinates = coordinates
            continue
        if coordinates & future_coordinates:
            raise ValueError(f"future overlays overlap each other: {pattern}")
        future_coordinates.update(coordinates)
        future_paths.append(pattern)
    if self_coordinates & future_coordinates:
        raise ValueError("future overlay overlaps B07 self overlay")
    return {
        "prefix_patterns": prefix_patterns,
        "suffix_patterns": suffix_patterns,
        "prefix_coordinates": prefix_coordinates,
        "self_coordinates": self_coordinates,
        "future_coordinates": future_coordinates,
        "future_paths": future_paths,
        "self_registration_count": self_count,
    }


def select_coordinates(
    builder: Any | None = None,
    progress_path: Path | None = None,
) -> tuple[list[tuple[int, int, int]], dict[str, Any]]:
    """Return 300 management/report/help UI fragments, excluding narrative blocks."""

    b04 = builder or _load_b04()
    sources = {
        "SC": b04.load_source(b04.DEFAULT_PK_SC, "SC"),
        "JP": b04.load_source(b04.DEFAULT_PK_JP, "JP"),
        "EN": b04.load_source(b04.DEFAULT_PK_EN, "EN"),
        "TC": b04.load_source(b04.DEFAULT_PK_TC, "TC"),
    }
    targets, target_hash = b04.target_coordinates(b04.DEFAULT_TARGET)
    history = _history(b04, (progress_path or b04.DEFAULT_PROGRESS).resolve())
    for label in ("prefix_coordinates", "self_coordinates", "future_coordinates"):
        outside_target = history[label] - targets
        if outside_target:
            raise RuntimeError(f"{label} escaped the exact target catalog: {min(outside_target)}")
    remaining = targets - history["prefix_coordinates"]

    def has_sc_text(coordinate: tuple[int, int, int]) -> bool:
        literal = sources["SC"]["literals"].get(coordinate)
        return literal is not None and b04.CJK_RE.search(literal.text) is not None

    # Block 6: all remaining independent, format-free diplomacy/operation UI.
    block6: list[tuple[int, int, int]] = []
    for coordinate in sorted(value for value in remaining if value[0] == 6):
        block_id, record_id, _literal_id = coordinate
        if not has_sc_text(coordinate):
            continue
        if any(coordinate not in sources[label]["literals"] for label in ("JP", "EN", "TC")):
            continue
        record = sources["SC"]["archive"].blocks[block_id].records[record_id]
        if len(b04.parse_record_literals(record)) != 1:
            continue
        source = sources["SC"]["literals"][coordinate].text
        invariants = b04.common.message_invariants(source)
        if any(invariants[key] for key in ("printf", "esc", "controls", "pua")):
            continue
        if b04.bracket_sequence(source) or len(source) > 160:
            continue
        block6.append(coordinate)

    # Block 8: management/result/status reports.  Dialogue deaths and combat
    # barks are skipped; multi-literal UI reports remain in their exact slots.
    block8_excluded = {
        (8, 254, 3),
        (8, 255, 1),
        (8, 255, 2),
        (8, 304, 0),
        (8, 400, 1),
    }
    block8_extra = {
        (8, 233, 0),
        (8, 233, 1),
        (8, 234, 0),
        (8, 234, 1),
        (8, 238, 0),
        (8, 240, 0),
        (8, 240, 1),
        (8, 242, 0),
        (8, 243, 0),
        (8, 243, 1),
        (8, 245, 1),
        (8, 246, 0),
        (8, 246, 1),
        (8, 247, 1),
        (8, 248, 0),
        (8, 249, 1),
        (8, 250, 1),
        (8, 251, 0),
    }
    block8: list[tuple[int, int, int]] = []
    for coordinate in sorted(value for value in remaining if value[0] == 8):
        _block_id, record_id, _literal_id = coordinate
        if coordinate in block8_excluded or not has_sc_text(coordinate):
            continue
        if coordinate in block8_extra or (252 <= record_id <= 425) or (607 <= record_id <= 1043) or (1095 <= record_id <= 1194) or (1231 <= record_id <= 1243):
            block8.append(coordinate)

    # Blocks 13/14: tutorial/help UI.  Punctuation-only and sigma layout slots
    # are excluded because they are not translatable text.
    punctuation_only = {
        (13, 229, 1),
        (13, 289, 1),
        (13, 293, 1),
        (13, 297, 1),
        (13, 301, 1),
        (14, 221, 4),
        (14, 221, 6),
        (14, 222, 4),
    }
    block13 = sorted(
        coordinate
        for coordinate in remaining
        if coordinate[0] == 13 and coordinate not in punctuation_only and has_sc_text(coordinate)
    )
    block14 = sorted(
        coordinate
        for coordinate in remaining
        if coordinate[0] == 14 and coordinate not in punctuation_only and has_sc_text(coordinate)
    )

    selected = sorted(block6 + block8 + block13 + block14)
    counts = {block: sum(value[0] == block for value in selected) for block in (6, 8, 13, 14)}
    expected_counts = {6: 28, 8: 227, 13: 28, 14: 17}
    if len(selected) != 300 or len(set(selected)) != 300 or counts != expected_counts:
        raise RuntimeError(f"B07 deterministic selection changed: {len(selected)}, {counts}")
    selected_set = set(selected)
    if not selected_set <= targets or selected_set & history["prefix_coordinates"]:
        raise RuntimeError("B07 selection escaped target or overlaps the B06 prefix")
    if selected_set & history["future_coordinates"]:
        raise RuntimeError("a future overlay overlaps the pinned B07 selection")
    if history["self_registration_count"]:
        if history["self_coordinates"] != selected_set:
            raise RuntimeError("registered B07 self overlay differs from the pinned selection")

    selected_hash = b04.canonical_hash([list(value) for value in selected])
    if selected_hash != B07_COORDINATES_SHA256:
        raise RuntimeError("B07 deterministic coordinate pin changed")
    return selected, {
        "builder": b04,
        "sources": sources,
        "targets": targets,
        "target_hash": target_hash,
        "history": history,
        "selected_counts": counts,
        "selected_sha256": selected_hash,
    }


if __name__ == "__main__":
    coordinates, context = select_coordinates()
    print(context["selected_sha256"])
    print(context["selected_counts"])
    print(context["history"]["self_registration_count"], context["history"]["future_paths"])
