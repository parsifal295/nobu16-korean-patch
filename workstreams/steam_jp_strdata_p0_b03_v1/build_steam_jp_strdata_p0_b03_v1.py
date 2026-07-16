#!/usr/bin/env python3
"""P0-03 configuration and formatting repairs for Steam JP ``strdata``.

This workstream owns the next non-overlapping 350-coordinate P0 contract.
It reuses the pinned P0-01 binary engine, but derives an isolated overlay and
repairs three verified Switch-reference typography artifacts before any
candidate is accepted: two full-width percent signs and one Japanese middle
dot.  The repairs retain source format tokens and remove all Japanese glyphs.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Iterable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPOSITORY = SCRIPT.parents[2]
ENGINE_PATH = (
    REPOSITORY
    / "workstreams"
    / "steam_jp_strdata_p0_b01_v1"
    / "build_steam_jp_strdata_p0_b01_v1.py"
)
SPEC = importlib.util.spec_from_file_location("steam_jp_strdata_p0_engine", ENGINE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load shared pinned strdata engine: {ENGINE_PATH}")
engine = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = engine
SPEC.loader.exec_module(engine)


WORKSTREAM_ID = "steam-jp-strdata-p0-b03-350-v1"
BUNDLE_ID = "p0-MSG_JP_strdata-03"
OVERLAY_NAME = "strdata_ko_steam_jp_p0_b03_350.v1.json"
EXPECTED_COORDINATE_COUNT = 350
EXPECTED_COORDINATE_SHA256 = "E93B58820385F38A01F4DD54E6D3EA28B2771E19E05E589BBF56DC469FFC7815"
DEFAULT_OVERLAY = WORKSTREAM / "public" / OVERLAY_NAME
SAFE_TMP_ROOT = REPOSITORY / "tmp" / "steam_jp_strdata_p0_b03_v1"

# Source-free project wording corrections, each checked against the active JP
# format invariants below.  The full-width percent is required because it is a
# literal suffix in the JP UI format; the Korean middle dot replaces a residual
# Japanese punctuation glyph without changing controls or printf tokens.
SAFE_KO_OVERRIDES = {
    (0, 22292): "금산정, 은산정의\n금전 수입%+d％",
    (0, 22302): "대장간정의 효과량%+d％",
    (0, 22373): "성하시설\x1bC3%s\x1bCZ·\x1bC3%s\x1bCZ의 비용%+d",
}


def configure_engine() -> None:
    engine.WORKSTREAM = WORKSTREAM
    engine.WORKSTREAM_ID = WORKSTREAM_ID
    engine.BUNDLE_ID = BUNDLE_ID
    engine.OVERLAY_NAME = OVERLAY_NAME
    engine.EXPECTED_COORDINATE_COUNT = EXPECTED_COORDINATE_COUNT
    engine.EXPECTED_COORDINATE_SHA256 = EXPECTED_COORDINATE_SHA256
    engine.DEFAULT_OVERLAY = DEFAULT_OVERLAY
    engine.SAFE_TMP_ROOT = SAFE_TMP_ROOT


def derive_overlay(active_input: Path, old_jp_input: Path, switch_zip: Path, output: Path) -> dict[str, Any]:
    """Derive B03 only after source equivalence, applying three safe repairs."""

    engine.require_workstream_output(output)
    _, _, active = engine.parse_pinned_archive(active_input, engine.ACTIVE_PIN, "active Steam JP")
    _, _, old = engine.parse_pinned_archive(old_jp_input, engine.OLD_JP_PIN, "official JP reference backup")
    switch_packed = engine.switch_member_bytes(switch_zip)
    switch_raw = engine.verify_packed_pin(switch_packed, engine.SWITCH_MEMBER_PIN, "Switch v1.3 JP member")
    switch = engine.parse_raw_strdata(switch_raw)
    coordinates, source_hashes, _ = engine.load_coordinate_contract()
    active_text = engine.coordinate_texts(active)
    old_text = engine.coordinate_texts(old)
    switch_text = engine.coordinate_texts(switch)
    entries: list[dict[str, Any]] = []
    repaired_coordinates: list[dict[str, int]] = []
    for coordinate in coordinates:
        key = (coordinate["block_id"], coordinate["slot_id"])
        source, previous, reference = active_text[key], old_text[key], switch_text[key]
        if source != previous:
            raise engine.StrdataP0Error(f"active JP source differs from official JP reference at {key}")
        if engine.text_hash(source) != source_hashes[key]:
            raise engine.StrdataP0Error(f"active JP source hash differs from P0 contract at {key}")
        korean = SAFE_KO_OVERRIDES.get(key, reference)
        if key in SAFE_KO_OVERRIDES:
            repaired_coordinates.append({"block_id": key[0], "slot_id": key[1]})
        mismatches = engine.common.invariant_mismatches(source, korean)
        if mismatches:
            raise engine.StrdataP0Error(f"Korean invariant mismatch at {key}: {mismatches!r}")
        if not engine.common.has_semantic_text(korean) or engine.KANA_OR_CJK.search(korean) or not engine.HANGUL.search(korean):
            raise engine.StrdataP0Error(f"Korean value is not safe Hangul text at {key}")
        entries.append(
            {
                "block_id": key[0],
                "slot_id": key[1],
                "source_jp_utf16le_sha256": engine.text_hash(source),
                "ko": korean,
                "ko_utf16le_sha256": engine.text_hash(korean),
                "status": "translated",
            }
        )
    if len(repaired_coordinates) != len(SAFE_KO_OVERRIDES):
        raise engine.StrdataP0Error("not every B03 formatting repair was selected by the contract")
    overlay = {
        "schema": engine.OVERLAY_SCHEMA,
        "overlay_id": WORKSTREAM_ID,
        "resource": engine.RESOURCE,
        "base_language": "JP",
        "entry_count": len(entries),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_jp": engine.ACTIVE_PIN,
        "coordinate_contract": {
            "path": engine.COORDINATE_CONTRACT.relative_to(engine.REPOSITORY).as_posix(),
            "bundle_id": BUNDLE_ID,
            "coordinate_count": EXPECTED_COORDINATE_COUNT,
            "coordinate_sha256": EXPECTED_COORDINATE_SHA256,
        },
        "defaults": {"status": "translated"},
        "entries": entries,
    }
    engine.atomic_write(output, engine.json_bytes(overlay))
    checked, blob = engine.load_overlay(output)
    if checked != overlay:
        raise engine.StrdataP0Error("serialized B03 overlay did not round-trip exactly")
    return {
        "action": "derive-overlay",
        "output": str(output),
        "output_size": len(blob),
        "output_sha256": engine.sha256(blob),
        "translated_entries": len(entries),
        "exact_active_to_official_jp_source_matches": len(entries),
        "formatting_repairs": repaired_coordinates,
        "game_install_modified": False,
        "release_modified": False,
        "github_modified": False,
    }


def main(argv: Iterable[str] | None = None) -> int:
    configure_engine()
    engine.derive_overlay = derive_overlay
    return engine.main(argv)


configure_engine()
engine.derive_overlay = derive_overlay


if __name__ == "__main__":
    raise SystemExit(main())
