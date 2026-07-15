#!/usr/bin/env python3
"""Deterministically select the 300 source-free B05 UI coordinates."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
B04_ROOT = REPO_ROOT / "workstreams" / "msggame_pk_ui_priority_b04"
B04_OVERLAY = B04_ROOT / "public" / "msggame_ko_pk_ui_priority_b04_250.v1.json"
B04_OVERLAY_SHA256 = "399CC98E8C778663FFF95CD7AE052C04B1BF96DACFBA6E09E207D54E6EF55AD5"
B04_COORDINATES_SHA256 = "9147574B5DC75C50A8BD3CB773F01B9056C7A2AC266D0B979E6CB7E42D397ECD"
B05_COORDINATES_SHA256 = "C872E6178EC8E77B4EE820A0AE06C323146E8C437B894D47ADB9E7EF5541B331"


def _load_b04() -> Any:
    spec = importlib.util.spec_from_file_location(
        "msggame_pk_ui_priority_b04_builder_for_b05",
        B04_ROOT / "build_msggame_pk_ui_priority_b04.py",
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the pinned B04 builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def select_coordinates(builder: Any | None = None) -> tuple[list[tuple[int, int, int]], dict[str, Any]]:
    """Return B05 coordinates plus loaded multilingual context.

    Blocks 8 and 13 contain management/report/menu UI.  Block 15 contains
    advice, operation-result, prompt, and confirmation messages.  Only an
    independent one-literal SC record without format/control/PUA/bracket
    structure is eligible.  This makes every replacement independently
    reviewable and keeps the runtime structure invariant exact.
    """

    b04 = builder or _load_b04()
    sources = {
        "SC": b04.load_source(b04.DEFAULT_PK_SC, "SC"),
        "JP": b04.load_source(b04.DEFAULT_PK_JP, "JP"),
        "EN": b04.load_source(b04.DEFAULT_PK_EN, "EN"),
        "TC": b04.load_source(b04.DEFAULT_PK_TC, "TC"),
    }
    targets, target_hash = b04.target_coordinates(b04.DEFAULT_TARGET)
    registered, _b01 = b04.existing_coordinates(b04.DEFAULT_PROGRESS)

    overlay_blob = B04_OVERLAY.read_bytes()
    if b04.sha256(overlay_blob) != B04_OVERLAY_SHA256:
        raise RuntimeError("B04 overlay pin changed")
    reserved = b04.overlay_coordinates(B04_OVERLAY)
    if len(reserved) != 250:
        raise RuntimeError("B04 reserved coordinate count changed")
    reserved_hash = b04.canonical_hash([list(value) for value in sorted(reserved)])
    if reserved_hash != B04_COORDINATES_SHA256:
        raise RuntimeError("B04 reserved coordinate pin changed")

    eligible: dict[int, list[tuple[int, int, int]]] = {8: [], 13: [], 15: []}
    for coordinate in sorted(targets - registered - reserved):
        block_id, record_id, _literal_id = coordinate
        if block_id not in eligible:
            continue
        source_literal = sources["SC"]["literals"].get(coordinate)
        if source_literal is None or any(coordinate not in sources[label]["literals"] for label in ("JP", "EN", "TC")):
            continue
        source = source_literal.text
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

    # All reviewed block-13 menu guidance and block-8 management/report UI,
    # followed by the 149 shortest block-15 advice/prompt/result messages.
    selected = sorted(eligible[13]) + sorted(eligible[8])
    selected += sorted(eligible[15], key=lambda value: (len(sources["SC"]["literals"][value].text), value))[:149]
    if len(selected) != 300 or len(set(selected)) != 300:
        raise RuntimeError(f"B05 deterministic selection changed: {len(selected)}")
    selected_hash = b04.canonical_hash([list(value) for value in sorted(selected)])
    if selected_hash != B05_COORDINATES_SHA256:
        raise RuntimeError("B05 deterministic coordinate pin changed")
    return selected, {
        "builder": b04,
        "sources": sources,
        "targets": targets,
        "target_hash": target_hash,
        "registered": registered,
        "reserved_b04": reserved,
        "eligible_counts": {key: len(value) for key, value in eligible.items()},
    }


if __name__ == "__main__":
    coordinates, context = select_coordinates()
    builder = context["builder"]
    print(builder.canonical_hash([list(value) for value in sorted(coordinates)]))
    print(context["eligible_counts"])
    print({block: sum(value[0] == block for value in coordinates) for block in (8, 13, 15)})
