#!/usr/bin/env python3
"""Build the Steam JP 1.1.7 v0.13.0 release candidate.

The release advances four audited event/dialogue resources and adds cumulative
static patch 005 for dual-resolution horizontal map assets and horizontal
landmark names.  The game executable itself is never included in the ZIP.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any, Final, Mapping


VERSION: Final = "v0.13.0"
ZIP_NAME: Final = "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.13.0.zip"
ZIP_TIMESTAMP: Final = (2026, 7, 20, 5, 30, 0)
SCHEMA: Final = "nobu16.kr.steam-jp-1.1.7-release.v0.13.0"
MANIFEST_NAME: Final = "release_manifest.v0.13.0.json"

SCRIPT: Final = Path(__file__).resolve()
PROJECT_ROOT: Final = SCRIPT.parents[1]
DEFAULT_PAYLOAD_ROOT: Final = PROJECT_ROOT / "release_payload" / "v0.13.0"
UPSTREAM_PATH: Final = PROJECT_ROOT / "tools" / "build_steam_jp_v0112_release.py"
REFERENCE_PATH: Final = PROJECT_ROOT / "tools" / "build_steam_jp_v0120_release.py"


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


_reference = load_module("steam_jp_v0120_release_profile", REFERENCE_PATH)
GAME_TARGETS: Mapping[str, tuple[int, str]] = {
    **_reference.GAME_TARGETS,
    "MSG/JP/ev_strdata.bin": (
        928_131,
        "85CC7B26E2D9A159AABD71610A9694AD803CFADE8CCD12F1A082AE2A35E3FF45",
    ),
    "MSG/JP/msggame.bin": (
        1_504_410,
        "F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB",
    ),
    "MSG_PK/JP/msgev.bin": (
        994_739,
        "01287E2ECC5328C85348657EFF06553353CB8664B0FB7E1669DB9FC591D53EBE",
    ),
    "MSG_PK/JP/msggame.bin": (
        1_806_538,
        "0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092",
    ),
}
SUPPORT_TARGETS: Mapping[str, tuple[int, str]] = {
    **_reference.SUPPORT_TARGETS,
    "STATIC_OFFICER_EDITOR_FIX_README_KO.txt": (
        3_361,
        "9F1A9BCEBFBA014003177A1AD25C1AAAD98DDA1E56A7332677ABB5DE5F1ABDBF",
    ),
    "OfficerEditorStaticFix/Invoke-Nobu16StaticPatches.ps1": (
        29_586,
        "2DB83B1D7744D5C3947993DACD98BA5C7BB8AA2342E1A8BAA26A66B453DD176A",
    ),
    "OfficerEditorStaticFix/000-PatchRegistry.psd1": (
        1_307,
        "9B9A73A548F976BC5C2DE72636CA85BEAA196B58CD4907211B5D81CC668683DA",
    ),
    "OfficerEditorStaticFix/Patches/005-DualResolutionAndHorizontalLandmarks.psd1": (
        7_335,
        "31B31DDD996A403C8FEA1AA710FB709F352DA91AEEE35E050C98C2BF4BBE5E64",
    ),
    "OfficerEditorStaticFix/Patches/Payloads/005-DualResolutionAndHorizontalLandmarks.append.gz": (
        4_706_907,
        "F723A94E8A63409E0A5458D2790FEE7713EB805FA9E48488EF9281205E27BA1F",
    ),
}
STATIC_EXE_PATCH: Mapping[str, object] = {
    **_reference.STATIC_EXE_PATCH,
    "previous_output_sha256": (
        "A430615A2D6EAD81B0B50DB6D9055FB77BD3E6CC7EEEAE7F145D203960B5C98E"
    ),
    "supports_previous_output_upgrade": True,
    "output_sha256": (
        "BE983A61C81008289E2483D552122C0BE3299B5F8DD4A557FA14DA2663AC7BD6"
    ),
    "output_size": 67_024_384,
    "patch_site_count": 197,
    "patch_005_site_count": 48,
    "landmark_owner_patch_site_count": 11,
    "patch_005_append_size": 28_032_512,
    "patch_005_append_sha256": (
        "F89447BA89038C594319649F2E881D2B3E826E32C034E6ED2395BD34788DD11D"
    ),
    "map_label_layout": "native-north-american-horizontal-assets-dual-resolution",
    "landmark_label_layout": "native-north-american-horizontal-owner-labels",
    "resource_archives_modified": False,
    "validated_resolution": "800x450 landmark QA; reported 3840x2160 high-resolution defect",
    "validated_after_full_process_restart": True,
    "installer_architecture": "data-driven-master-registry-v3",
    "registered_patch_count": 5,
    "supports_chained_append_overlays": True,
    "supports_per_patch_state_detection": True,
    "supports_registered_patch_combinations": True,
    "partial_patch_policy": "fail-closed",
}
TRANSLATION_QUALITY: Mapping[str, object] = {
    "event_count": 26,
    "event_base_count": 8,
    "event_pk_count": 18,
    "dialogue_count": 51,
    "dialogue_base_count": 13,
    "dialogue_pk_count": 38,
    "changed_resource_count": 4,
    "source_policy": "original PC JP with PC EN/SC/TC comparison; no Switch Korean",
}


def build(
    game_root: Path,
    output: Path,
    payload_root: Path = DEFAULT_PAYLOAD_ROOT,
    *,
    game_targets: Mapping[str, tuple[int, str]] = GAME_TARGETS,
    support_targets: Mapping[str, tuple[int, str]] = SUPPORT_TARGETS,
) -> dict[str, object]:
    upstream = load_configured_upstream("steam_jp_v0112_release_for_v0130")
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
