#!/usr/bin/env python3
"""P0-02 configuration for the audited Steam JP ``strdata`` build engine.

This independent workstream owns a different, exact P0 coordinate contract
and its own source-free overlay and temporary output root.  It deliberately
reuses the P0-01 binary-format engine: doing so keeps the active-JP pin,
structure-preservation, non-selected-coordinate, and deterministic-build
checks byte-for-byte identical while the translation data remains isolated.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Iterable


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


WORKSTREAM_ID = "steam-jp-strdata-p0-b02-350-v1"
BUNDLE_ID = "p0-MSG_JP_strdata-02"
OVERLAY_NAME = "strdata_ko_steam_jp_p0_b02_350.v1.json"
EXPECTED_COORDINATE_COUNT = 350
EXPECTED_COORDINATE_SHA256 = "8083C00E140022FD59D6BDCF3CE100DE6BA96C6070237CB3BFEA9D641C73EC6B"
DEFAULT_OVERLAY = WORKSTREAM / "public" / OVERLAY_NAME
SAFE_TMP_ROOT = REPOSITORY / "tmp" / "steam_jp_strdata_p0_b02_v1"


def configure_engine() -> None:
    """Bind the shared format engine to this workstream's immutable scope."""

    engine.WORKSTREAM = WORKSTREAM
    engine.WORKSTREAM_ID = WORKSTREAM_ID
    engine.BUNDLE_ID = BUNDLE_ID
    engine.OVERLAY_NAME = OVERLAY_NAME
    engine.EXPECTED_COORDINATE_COUNT = EXPECTED_COORDINATE_COUNT
    engine.EXPECTED_COORDINATE_SHA256 = EXPECTED_COORDINATE_SHA256
    engine.DEFAULT_OVERLAY = DEFAULT_OVERLAY
    engine.SAFE_TMP_ROOT = SAFE_TMP_ROOT


configure_engine()


def main(argv: Iterable[str] | None = None) -> int:
    configure_engine()
    return engine.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
