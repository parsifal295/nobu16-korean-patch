#!/usr/bin/env python3
"""Build the Steam JP 1.1.7 v0.12.0 release.

This release keeps the reviewed v0.11.6 resources and adds horizontal Korean
map labels with dynamically sized normal and highlighted plates. The game
executable itself is never included in the ZIP.
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from typing import Any, Final, Mapping


VERSION: Final = "v0.12.0"
ZIP_NAME: Final = "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.12.0.zip"
ZIP_TIMESTAMP: Final = (2026, 7, 19, 16, 0, 0)
SCHEMA: Final = "nobu16.kr.steam-jp-1.1.7-release.v0.12.0"
MANIFEST_NAME: Final = "release_manifest.v0.12.0.json"

SCRIPT: Final = Path(__file__).resolve()
PROJECT_ROOT: Final = SCRIPT.parents[1]
DEFAULT_PAYLOAD_ROOT: Final = PROJECT_ROOT / "release_payload" / "v0.12.0"
UPSTREAM_PATH: Final = PROJECT_ROOT / "tools" / "build_steam_jp_v0112_release.py"
REFERENCE_PATH: Final = PROJECT_ROOT / "tools" / "build_steam_jp_v0116_release.py"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load release builder: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_configured_upstream(name: str) -> Any:
    """Load the shared builder with this release's exact support allowlist."""
    module = load_module(name, UPSTREAM_PATH)
    module.EXPECTED_SUPPORT_MEMBERS = tuple(sorted(SUPPORT_TARGETS))
    return module


_reference = load_module("steam_jp_v0116_release_profile", REFERENCE_PATH)
GAME_TARGETS: Mapping[str, tuple[int, str]] = dict(_reference.GAME_TARGETS)
SUPPORT_TARGETS: Mapping[str, tuple[int, str]] = {
    **_reference.SUPPORT_TARGETS,
    "STATIC_OFFICER_EDITOR_FIX_README_KO.txt": (
        3_171,
        "F1D0D3B7DED819ACC5DDBA7611A0EEEE52E017364ED918E05DB57F8CFF4880B0",
    ),
    "OfficerEditorStaticFix/Invoke-Nobu16StaticPatches.ps1": (
        27_444,
        "B9224428C26AD655AAC7B83C78312387D96F270E997B9A163EFFAF8E7C47F7A2",
    ),
    "OfficerEditorStaticFix/000-PatchRegistry.psd1": (
        1_076,
        "289F0E0366917AE3EFFF57E749F3C625CB7DDDC1F0173F74ABF7819A85230C4E",
    ),
    "OfficerEditorStaticFix/Steamless/Steamless.CLI.exe.config": (
        188,
        "84C420F392B59E32409E308AA67D9CDC3BB1BC7496A2403EF5BB0EB8ADF62763",
    ),
    "OfficerEditorStaticFix/Patches/004-HorizontalMapLabelsDynamicWidth.psd1": (
        16_177,
        "D009D596ACC5E1B3A4FC7D74913B5D17F87FA199B38956FBAC456130DEDA754B",
    ),
    "OfficerEditorStaticFix/Patches/Payloads/004-HorizontalMapLabelsDynamicWidth.append.gz": (
        1_580_771,
        "BFA9F42C9021208349021A6A26193ADE0C83DE6B797CBDA7E15E59D463630A95",
    ),
}
STATIC_EXE_PATCH: Mapping[str, object] = {
    **_reference.STATIC_EXE_PATCH,
    "previous_output_sha256": (
        "FD7F07A29DBD76E4AB18B1D1EE85D6B1677E0A4827A79E3732075D4CACBA8BB6"
    ),
    "supports_previous_output_upgrade": True,
    "output_sha256": (
        "A430615A2D6EAD81B0B50DB6D9055FB77BD3E6CC7EEEAE7F145D203960B5C98E"
    ),
    "output_size": 38_991_872,
    "patch_site_count": 149,
    "map_label_patch_site_count": 128,
    "map_label_append_size": 7_244_024,
    "map_label_append_sha256": (
        "5C28CF48729EBC132FEEF74E4E373084125D2B1F3E44A36C58BEA05F44DC360D"
    ),
    "map_label_layout": "native-north-american-horizontal-assets",
    "map_label_width_policy": "UTF-16 NUL-terminated dynamic measurement",
    "fixed_character_ceiling": None,
    "resource_archives_modified": False,
    "validated_resolution": "1920x1080",
    "validated_after_full_process_restart": True,
    "installer_architecture": "data-driven-master-registry-v2",
    "patch_definition_format": "PowerShell-data-file",
    "patch_registry_manifest": "OfficerEditorStaticFix/000-PatchRegistry.psd1",
    "registered_patch_count": 4,
    "supports_per_patch_state_detection": True,
    "supports_registered_patch_combinations": True,
    "supports_structural_append_overlay": True,
    "partial_patch_policy": "fail-closed",
}


def build(
    game_root: Path,
    output: Path,
    payload_root: Path = DEFAULT_PAYLOAD_ROOT,
    *,
    game_targets: Mapping[str, tuple[int, str]] = GAME_TARGETS,
    support_targets: Mapping[str, tuple[int, str]] = SUPPORT_TARGETS,
) -> dict[str, object]:
    upstream = load_configured_upstream("steam_jp_v0112_release_for_v0120")
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
