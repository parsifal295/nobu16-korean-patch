#!/usr/bin/env python3
"""Build the Steam JP 1.1.7 v0.11.5 release with the Issue 62 EXE fix.

The game-resource profile is inherited unchanged from the published v0.11.4
policy-effect recovery. This release advances only the local EXE installer: it
retains the Issue 43 officer-editor patch and adds the caller-scoped
fictional-princess name-validation patch.
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from typing import Any, Final, Mapping


VERSION: Final = "v0.11.5"
ZIP_NAME: Final = "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.11.5.zip"
ZIP_TIMESTAMP: Final = (2026, 7, 18, 22, 0, 0)
SCHEMA: Final = "nobu16.kr.steam-jp-1.1.7-release.v0.11.5"
MANIFEST_NAME: Final = "release_manifest.v0.11.5.json"

SCRIPT: Final = Path(__file__).resolve()
PROJECT_ROOT: Final = SCRIPT.parents[1]
DEFAULT_PAYLOAD_ROOT: Final = PROJECT_ROOT / "release_payload" / "v0.11.5"
UPSTREAM_PATH: Final = PROJECT_ROOT / "tools" / "build_steam_jp_v0112_release.py"
REFERENCE_PATH: Final = PROJECT_ROOT / "tools" / "build_steam_jp_v0114_release.py"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load release builder: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_reference = load_module("steam_jp_v0114_release_profile", REFERENCE_PATH)
GAME_TARGETS: Mapping[str, tuple[int, str]] = dict(_reference.GAME_TARGETS)

SUPPORT_TARGETS: Mapping[str, tuple[int, str]] = {
    "APPLY_STATIC_OFFICER_EDITOR_FIX.bat": (
        358,
        "48A68DECA8454F22B0DA7C509C4C913B8246B5998C2373EE98C57EB08E69AB68",
    ),
    "OfficerEditorStaticFix/Invoke-StaticOfficerEditorFix.ps1": (
        14_572,
        "638B4CD1CCF3347B5D3033CB48033D0E17EFB5F2EC16BAE0802C4B15BE60D61F",
    ),
    "OfficerEditorStaticFix/Steamless/Plugins/Steamless.API.dll": (
        34_304,
        "D6ACC4B0CC768213A46FFAD0A6BF6070A6B13F79A22E0588F0AB50C950F9248C",
    ),
    "OfficerEditorStaticFix/Steamless/Plugins/Steamless.Unpacker.Variant31.x64.dll": (
        16_384,
        "790F1974F97258058CB57C20787E8A2FCB5C16CCA0911719B698580D74E38918",
    ),
    "OfficerEditorStaticFix/Steamless/Steamless.CLI.exe": (
        113_152,
        "70CD54354865EDE605EC0FBFADF15F5302AA85A777394F28B0DE6ACFD243E795",
    ),
    "OfficerEditorStaticFix/Steamless/Steamless.CLI.exe.config": (
        189,
        "E8DECC96235B5494880083EB79C22C84C6D9EF312828BAF9490BEE7782C350EC",
    ),
    "OfficerEditorStaticFix/THIRD_PARTY_NOTICES.txt": (
        523,
        "A069D20E09CE5DA24B40A7801C009FA6158A3EC3CA7860088BDEF47B4C7C93E4",
    ),
    "RESTORE_ORIGINAL_NOBU16PK_EXE.bat": (
        367,
        "D9BAE555DDE440A9665A53A10E7F6B2DD83DF77C6366D8A0B3EBE0FF21C3C358",
    ),
    "STATIC_OFFICER_EDITOR_FIX_README_KO.txt": (
        3_746,
        "4C527D29A922021DCDF8F6B2B09198C2C8EFC0F2B62D0D98785F492B20633E0B",
    ),
}

STATIC_EXE_PATCH: Mapping[str, object] = {
    "delivery": "one-time-local-installer",
    "per_session_component": False,
    "process_memory_access": False,
    "target": "NOBU16PK.exe",
    "input_size": 31_978_264,
    "input_sha256": "29BC1ED66D27B9AEF5EB6CE3D126BA2BDBF86099E12B09615FE9F988F41E2246",
    "unpacked_size": 31_747_848,
    "unpacked_sha256": "BC885875A5E4288E5A1A424D99974F6F215777C03569C7EA707FDE63BDBC2B39",
    "previous_output_sha256": "2E098ECB5E4335DC264F865306B990B724EA7C242B1B9F87FFC5EE2E7191797C",
    "supports_previous_output_upgrade": True,
    "output_size": 31_747_848,
    "output_sha256": "7CA2F1D59E02650C67F343F0776F6D05517C0486B65168E63A9AE4CBCAAFDBB2",
    "output_authenticode": "NotSigned",
    "backup_filename": "NOBU16PK.exe.staticfix.original_1.1.7",
    "patch_site_count": 9,
    "officer_editor_patch_site_count": 5,
    "fictional_princess_patch_site_count": 4,
    "shared_character_validators_modified": False,
    "requires_game_stopped": True,
    "requires_dotnet_framework": "4.5.2",
}


def build(
    game_root: Path,
    output: Path,
    payload_root: Path = DEFAULT_PAYLOAD_ROOT,
    *,
    game_targets: Mapping[str, tuple[int, str]] = GAME_TARGETS,
    support_targets: Mapping[str, tuple[int, str]] = SUPPORT_TARGETS,
) -> dict[str, object]:
    upstream = load_module("steam_jp_v0112_release_for_v0115", UPSTREAM_PATH)
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
