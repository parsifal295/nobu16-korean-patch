#!/usr/bin/env python3
"""Build the Steam JP 1.1.7 v0.13.1 release candidate.

The game-resource payload remains byte-identical to v0.13.0.  This release
advances the data-driven static installer to patch 006, which dynamically
aligns map status markers with horizontal castle labels while preserving the
troop-count group below each castle crest.  The game executable itself is
never included in the ZIP.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any, Final, Mapping


VERSION: Final = "v0.13.1"
ZIP_NAME: Final = "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.13.1.zip"
ZIP_TIMESTAMP: Final = (2026, 7, 20, 14, 45, 0)
SCHEMA: Final = "nobu16.kr.steam-jp-1.1.7-release.v0.13.1"
MANIFEST_NAME: Final = "release_manifest.v0.13.1.json"

SCRIPT: Final = Path(__file__).resolve()
PROJECT_ROOT: Final = SCRIPT.parents[1]
DEFAULT_PAYLOAD_ROOT: Final = PROJECT_ROOT / "release_payload" / "v0.13.1"
UPSTREAM_PATH: Final = PROJECT_ROOT / "tools" / "build_steam_jp_v0112_release.py"
REFERENCE_PATH: Final = PROJECT_ROOT / "tools" / "build_steam_jp_v0130_release.py"


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


_reference = load_module("steam_jp_v0130_release_profile", REFERENCE_PATH)
GAME_TARGETS: Mapping[str, tuple[int, str]] = dict(_reference.GAME_TARGETS)
SUPPORT_TARGETS: Mapping[str, tuple[int, str]] = {
    **_reference.SUPPORT_TARGETS,
    "STATIC_OFFICER_EDITOR_FIX_README_KO.txt": (
        4_570,
        "0F22F088B2E485C41E75E003A22BA0284DE288AB5BD47876E685722618BE65DE",
    ),
    "OfficerEditorStaticFix/Invoke-Nobu16StaticPatches.ps1": (
        30_949,
        "C9D77584FB2CC97411111C7EC02960C3B3CE94B2301571A91AA2F9C2B885A752",
    ),
    "OfficerEditorStaticFix/000-PatchRegistry.psd1": (
        1_526,
        "9692B82195BB4AFEC12A10832157D3AE2B5807F481579E9F3175C77239487B36",
    ),
    "OfficerEditorStaticFix/Patches/006-HorizontalMapStatusIcons.psd1": (
        1_294,
        "47B668CD1988C1393F051C4253FE2E895F42D4D1228C50174232F2EB96806625",
    ),
}
STATIC_EXE_PATCH: Mapping[str, object] = {
    **_reference.STATIC_EXE_PATCH,
    "previous_output_sha256": (
        "BE983A61C81008289E2483D552122C0BE3299B5F8DD4A557FA14DA2663AC7BD6"
    ),
    "supports_previous_output_upgrade": True,
    "output_sha256": (
        "3548AD5B71168296DD03851B1F9613CAD1C325AF2AB916A11CC140DC61FA0E43"
    ),
    "output_size": 67_024_384,
    "patch_site_count": 201,
    "patch_006_site_count": 4,
    "patch_006_kind": "same-size-byte-patch",
    "patch_006_injected_code_size": 162,
    "patch_006_changed_byte_count": 150,
    "map_status_alignment": "dynamic-label-width-and-live-widget-height",
    "troop_count_alignment": "native-engine-layout-below-castle-crest",
    "troop_count_root_write": False,
    "fixed_status_offset": None,
    "validated_resolution": "1920x1080 issue-72 map-status QA",
    "validated_after_full_process_restart": True,
    "installer_architecture": "data-driven-master-registry-v3",
    "registered_patch_count": 6,
    "supports_all_registered_prefix_states": True,
    "supports_blocked_byte_patches_after_structural_overlays": True,
}
ISSUE_72_ALIGNMENT: Mapping[str, object] = {
    "issue": 72,
    "status_markers": ["battle-ready", "defensive-base", "attack-objective"],
    "status_x_formula": "native status X + rendered castle-label width",
    "status_y_formula": "label Y + (label height - status height) / 2",
    "troop_count_group_preserved": True,
    "troop_count_placement": "native engine layout below castle crest",
    "fixed_offset": None,
    "excluded_paths": [
        "castle crest icon",
        "troop-count group below castle crest",
        "special map cursor",
    ],
    "validated_resolution": "1920x1080",
    "validated_after_full_process_restart": True,
    "user_visual_confirmation": True,
}
TRANSLATION_QUALITY: Mapping[str, object] = dict(_reference.TRANSLATION_QUALITY)


def build(
    game_root: Path,
    output: Path,
    payload_root: Path = DEFAULT_PAYLOAD_ROOT,
    *,
    game_targets: Mapping[str, tuple[int, str]] = GAME_TARGETS,
    support_targets: Mapping[str, tuple[int, str]] = SUPPORT_TARGETS,
) -> dict[str, object]:
    upstream = load_configured_upstream("steam_jp_v0112_release_for_v0131")
    upstream.VERSION = VERSION
    upstream.ZIP_NAME = ZIP_NAME
    upstream.ZIP_TIMESTAMP = ZIP_TIMESTAMP
    upstream.SCHEMA = SCHEMA
    upstream.MANIFEST_NAME = MANIFEST_NAME
    upstream.GAME_TARGETS = dict(game_targets)
    upstream.SUPPORT_TARGETS = dict(support_targets)
    upstream.STATIC_EXE_PATCH = dict(STATIC_EXE_PATCH)
    manifest = upstream.build(
        game_root,
        output,
        payload_root,
        game_targets=game_targets,
        support_targets=support_targets,
    )
    manifest["translation_quality"] = dict(TRANSLATION_QUALITY)
    manifest["issue_72_alignment"] = dict(ISSUE_72_ALIGNMENT)
    (output / MANIFEST_NAME).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


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
