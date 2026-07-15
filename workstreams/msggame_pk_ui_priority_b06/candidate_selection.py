#!/usr/bin/env python3
"""Deterministically select the 300 source-free B06 UI coordinates."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
B04_ROOT = REPO_ROOT / "workstreams" / "msggame_pk_ui_priority_b04"
B05_ROOT = REPO_ROOT / "workstreams" / "msggame_pk_ui_priority_b05"
B04_OVERLAY = B04_ROOT / "public" / "msggame_ko_pk_ui_priority_b04_250.v1.json"
B05_OVERLAY = B05_ROOT / "public" / "msggame_ko_pk_ui_priority_b05_300.v1.json"
B04_OVERLAY_SHA256 = "399CC98E8C778663FFF95CD7AE052C04B1BF96DACFBA6E09E207D54E6EF55AD5"
B05_OVERLAY_SHA256 = "E67FFDC802485FFB8B1276880239CA4CE9F4098274792B993A448A36E1771808"
B04_COORDINATES_SHA256 = "9147574B5DC75C50A8BD3CB773F01B9056C7A2AC266D0B979E6CB7E42D397ECD"
B05_COORDINATES_SHA256 = "C872E6178EC8E77B4EE820A0AE06C323146E8C437B894D47ADB9E7EF5541B331"
B06_COORDINATES_SHA256 = "C21D547E380E4A579E3F15947FF62B48AD1BE20ED31F09AB0FE00608912ADC94"


def _load_b04() -> Any:
    spec = importlib.util.spec_from_file_location(
        "msggame_pk_ui_priority_b04_builder_for_b06",
        B04_ROOT / "build_msggame_pk_ui_priority_b04.py",
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the pinned B04 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _pinned_reserved(builder: Any) -> tuple[set[tuple[int, int, int]], set[tuple[int, int, int]]]:
    pins = (
        (B04_OVERLAY, B04_OVERLAY_SHA256, 250, B04_COORDINATES_SHA256),
        (B05_OVERLAY, B05_OVERLAY_SHA256, 300, B05_COORDINATES_SHA256),
    )
    result: list[set[tuple[int, int, int]]] = []
    for path, overlay_hash, count, coordinate_hash in pins:
        if builder.sha256(path.read_bytes()) != overlay_hash:
            raise RuntimeError(f"predecessor overlay pin changed: {path}")
        coordinates = builder.overlay_coordinates(path)
        if len(coordinates) != count:
            raise RuntimeError(f"predecessor coordinate count changed: {path}")
        actual_hash = builder.canonical_hash([list(value) for value in sorted(coordinates)])
        if actual_hash != coordinate_hash:
            raise RuntimeError(f"predecessor coordinate pin changed: {path}")
        result.append(coordinates)
    if result[0] & result[1]:
        raise RuntimeError("B04 and B05 predecessor coordinates overlap")
    return result[0], result[1]


def select_coordinates(builder: Any | None = None) -> tuple[list[tuple[int, int, int]], dict[str, Any]]:
    """Return 300 battle-status, deployment, advice, diplomacy, and council UI rows."""

    b04 = builder or _load_b04()
    sources = {
        "SC": b04.load_source(b04.DEFAULT_PK_SC, "SC"),
        "JP": b04.load_source(b04.DEFAULT_PK_JP, "JP"),
        "EN": b04.load_source(b04.DEFAULT_PK_EN, "EN"),
        "TC": b04.load_source(b04.DEFAULT_PK_TC, "TC"),
    }
    targets, target_hash = b04.target_coordinates(b04.DEFAULT_TARGET)
    registered, _b01 = b04.existing_coordinates(b04.DEFAULT_PROGRESS)
    reserved_b04, reserved_b05 = _pinned_reserved(b04)
    reserved = reserved_b04 | reserved_b05

    eligible: dict[int, list[tuple[int, int, int]]] = {6: [], 7: [], 9: [], 15: []}
    for coordinate in sorted(targets - registered - reserved):
        block_id, record_id, _literal_id = coordinate
        if block_id not in eligible:
            continue
        if any(coordinate not in sources[label]["literals"] for label in ("SC", "JP", "EN", "TC")):
            continue
        source = sources["SC"]["literals"][coordinate].text
        record = sources["SC"]["archive"].blocks[block_id].records[record_id]
        if len(b04.parse_record_literals(record)) != 1:
            continue
        invariants = b04.common.message_invariants(source)
        if any(invariants[key] for key in ("printf", "esc", "controls", "pua")):
            continue
        if b04.bracket_sequence(source):
            continue
        if b04.CJK_RE.search(source) is None or len(source) > 160:
            continue
        eligible[block_id].append(coordinate)

    selected = sorted(eligible[7]) + sorted(eligible[9]) + sorted(eligible[15])
    selected += sorted(
        eligible[6],
        key=lambda value: (len(sources["SC"]["literals"][value].text), value),
    )[:130]
    expected_counts = {6: 130, 7: 37, 9: 116, 15: 17}
    actual_counts = {block: sum(value[0] == block for value in selected) for block in expected_counts}
    if len(selected) != 300 or len(set(selected)) != 300 or actual_counts != expected_counts:
        raise RuntimeError(f"B06 deterministic selection changed: {len(selected)}, {actual_counts}")
    selected_hash = b04.canonical_hash([list(value) for value in sorted(selected)])
    if selected_hash != B06_COORDINATES_SHA256:
        raise RuntimeError("B06 deterministic coordinate pin changed")
    return selected, {
        "builder": b04,
        "sources": sources,
        "targets": targets,
        "target_hash": target_hash,
        "registered": registered,
        "reserved_b04": reserved_b04,
        "reserved_b05": reserved_b05,
        "eligible_counts": {key: len(value) for key, value in eligible.items()},
        "selected_counts": actual_counts,
    }


if __name__ == "__main__":
    coordinates, context = select_coordinates()
    builder = context["builder"]
    print(builder.canonical_hash([list(value) for value in sorted(coordinates)]))
    print(context["eligible_counts"])
    print(context["selected_counts"])
