#!/usr/bin/env python3
"""Build the Steam JP 1.1.7 v0.11.6 release.

This release updates the six reviewed text resources and extends the local
static EXE installer with the validated North-American top-header geometry for
the Korean path. The game executable itself is never included in the ZIP.
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from typing import Any, Final, Mapping


VERSION: Final = "v0.11.6"
ZIP_NAME: Final = "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.11.6.zip"
ZIP_TIMESTAMP: Final = (2026, 7, 18, 23, 0, 0)
SCHEMA: Final = "nobu16.kr.steam-jp-1.1.7-release.v0.11.6"
MANIFEST_NAME: Final = "release_manifest.v0.11.6.json"

SCRIPT: Final = Path(__file__).resolve()
PROJECT_ROOT: Final = SCRIPT.parents[1]
DEFAULT_PAYLOAD_ROOT: Final = PROJECT_ROOT / "release_payload" / "v0.11.6"
UPSTREAM_PATH: Final = PROJECT_ROOT / "tools" / "build_steam_jp_v0112_release.py"
REFERENCE_PATH: Final = PROJECT_ROOT / "tools" / "build_steam_jp_v0115_release.py"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load release builder: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_reference = load_module("steam_jp_v0115_release_profile", REFERENCE_PATH)
GAME_TARGETS: Mapping[str, tuple[int, str]] = {
    **_reference.GAME_TARGETS,
    "MSG/JP/ev_strdata.bin": (
        928_119,
        "02AC90B818E8F75683CD5BACF277E91048D4510E448A8699242D3B19299FE067",
    ),
    "MSG/JP/msggame.bin": (
        1_504_422,
        "D70BA2EBE17CE056B9E348C610FE1F82B28285BAF1940F4450AE2D7D62B2E688",
    ),
    "MSG/JP/strdata.bin": (
        957_200,
        "37A1F6280B2663A7FF055C6A2105B5658CA62065582A66213C6D4D4AE2A79E0A",
    ),
    "MSG_PK/JP/msgdata.bin": (
        496_991,
        "8282F12A667E11F54054856035415C7297385ADD16EC261BD952BEBB8658952A",
    ),
    "MSG_PK/JP/msgev.bin": (
        994_727,
        "AEE0D9992B963E17B3C118AA54DACC60390936FF48876674CA7675A2A11A3668",
    ),
    "MSG_PK/JP/msggame.bin": (
        1_806_542,
        "0BDE96CF07C97B0FF71EBB5C2032E62F313BA271BD772D5BC79A48E57356A0F9",
    ),
}
SUPPORT_TARGETS: Mapping[str, tuple[int, str]] = {
    **_reference.SUPPORT_TARGETS,
    "OfficerEditorStaticFix/Invoke-StaticOfficerEditorFix.ps1": (
        17_245,
        "79E274B2EB76C6D7430DA2656ACE456F58E6991955A3785C9FE7FA05C830D760",
    ),
    "STATIC_OFFICER_EDITOR_FIX_README_KO.txt": (
        4_652,
        "516C7DDDD28BF6B029BEE033FF2A34B00004A6E44E1E2C1528095AC0938215D0",
    ),
}
STATIC_EXE_PATCH: Mapping[str, object] = {
    **_reference.STATIC_EXE_PATCH,
    "officer_only_output_sha256": (
        "2E098ECB5E4335DC264F865306B990B724EA7C242B1B9F87FFC5EE2E7191797C"
    ),
    "supports_officer_only_output_upgrade": True,
    "previous_output_sha256": (
        "7CA2F1D59E02650C67F343F0776F6D05517C0486B65168E63A9AE4CBCAAFDBB2"
    ),
    "supports_previous_output_upgrade": True,
    "output_sha256": (
        "FD7F07A29DBD76E4AB18B1D1EE85D6B1677E0A4827A79E3732075D4CACBA8BB6"
    ),
    "patch_site_count": 21,
    "officer_editor_patch_site_count": 5,
    "fictional_princess_patch_site_count": 4,
    "header_layout_patch_site_count": 12,
    "header_layout_reference": "native-north-american-horizontal-geometry",
    "resource_archives_modified": False,
    "validated_resolution": "2048x1152",
    "validated_after_full_process_restart": True,
}


def build(
    game_root: Path,
    output: Path,
    payload_root: Path = DEFAULT_PAYLOAD_ROOT,
    *,
    game_targets: Mapping[str, tuple[int, str]] = GAME_TARGETS,
    support_targets: Mapping[str, tuple[int, str]] = SUPPORT_TARGETS,
) -> dict[str, object]:
    upstream = load_module("steam_jp_v0112_release_for_v0116", UPSTREAM_PATH)
    upstream.VERSION = VERSION
    upstream.ZIP_NAME = ZIP_NAME
    upstream.ZIP_TIMESTAMP = ZIP_TIMESTAMP
    upstream.SCHEMA = SCHEMA
    upstream.MANIFEST_NAME = MANIFEST_NAME
    upstream.GAME_TARGETS = dict(game_targets)
    upstream.SUPPORT_TARGETS = dict(support_targets)
    upstream.STATIC_EXE_PATCH = dict(STATIC_EXE_PATCH)
    return upstream.build(
        game_root,
        output,
        payload_root,
        game_targets=game_targets,
        support_targets=support_targets,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", required=True, type=Path)
    parser.add_argument("--payload-root", type=Path, default=DEFAULT_PAYLOAD_ROOT)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    manifest = build(args.game_root, args.output, args.payload_root)
    print(manifest["release_zip"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
