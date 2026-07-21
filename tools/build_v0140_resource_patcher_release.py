#!/usr/bin/env python3
"""Build the compact v0.14.0 Steam JP direct unified-patcher release ZIP.

The archive deliberately contains no complete game resource and no
``NOBU16PK.exe``. It supports only a pristine Steam JP 1.1.7 resource vector,
rebuilds ten text resources from a frozen operation ledger, and applies five
bounded BSDIFF40 deltas at the user's game directory.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Final, Mapping


VERSION: Final = "v0.14.0"
ZIP_NAME: Final = "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.14.0.zip"
MANIFEST_NAME: Final = "release_manifest.v0.14.0.json"
LEDGER_MEMBER: Final = "patches/v0.14.0-direct-resource-patch.json.gz"
PATCHER_MEMBER: Final = "NOBU16_KR_RESOURCE_PATCHER.exe"
ZIP_TIMESTAMP: Final = (2026, 7, 21, 16, 30, 0)
SCHEMA: Final = "nobu16.kr.steam-jp-direct-resource-patcher.v0.14.0"

SCRIPT: Final = Path(__file__).resolve()
PROJECT_ROOT: Final = SCRIPT.parents[1]
DEFAULT_PAYLOAD_ROOT: Final = PROJECT_ROOT / "release_payload" / VERSION
PATCHER_SOURCE: Final = PROJECT_ROOT / "tools" / "v0140_resource_patcher.py"

# The static engine remains an internal implementation detail.  The public
# ZIP exposes only the two unified launchers below; the builder rejects any
# accidental extra payload before it creates a public archive.
STATIC_ENGINE_MEMBERS: Final = (
    "OfficerEditorStaticFix/000-PatchRegistry.psd1",
    "OfficerEditorStaticFix/Invoke-Nobu16StaticPatches.ps1",
    "OfficerEditorStaticFix/Patches/001-OfficerEditorNameValidation.psd1",
    "OfficerEditorStaticFix/Patches/002-FictionalPrincessNameValidation.psd1",
    "OfficerEditorStaticFix/Patches/003-TopHeaderLayout.psd1",
    "OfficerEditorStaticFix/Patches/004-HorizontalMapLabelsDynamicWidth.psd1",
    "OfficerEditorStaticFix/Patches/005-DualResolutionAndHorizontalLandmarks.psd1",
    "OfficerEditorStaticFix/Patches/006-HorizontalMapStatusIcons.psd1",
    "OfficerEditorStaticFix/Patches/007-EventMessageTypography.psd1",
    "OfficerEditorStaticFix/Patches/008-HorizontalMapAuxiliaryIndicators.psd1",
    "OfficerEditorStaticFix/Patches/009-EventMessageParentWidth.psd1",
    "OfficerEditorStaticFix/Patches/010-EventMessageAutoWrapLimit.psd1",
    "OfficerEditorStaticFix/Patches/Payloads/004-HorizontalMapLabelsDynamicWidth.append.gz",
    "OfficerEditorStaticFix/Patches/Payloads/005-DualResolutionAndHorizontalLandmarks.append.gz",
    "OfficerEditorStaticFix/Steamless/Plugins/Steamless.API.dll",
    "OfficerEditorStaticFix/Steamless/Plugins/Steamless.Unpacker.Variant31.x64.dll",
    "OfficerEditorStaticFix/Steamless/Steamless.CLI.exe",
    "OfficerEditorStaticFix/Steamless/Steamless.CLI.exe.config",
    "OfficerEditorStaticFix/THIRD_PARTY_NOTICES.txt",
)
UNIFIED_PATCHER_SUPPORT_MEMBERS: Final = (
    "APPLY_KOREAN_PATCH.bat",
    "RESTORE_KOREAN_PATCH.bat",
    "Invoke-Nobu16KoreanPatch.ps1",
    "PATCHER_README_KO.txt",
)
SUPPORT_MEMBERS: Final = tuple(
    sorted((*STATIC_ENGINE_MEMBERS, *UNIFIED_PATCHER_SUPPORT_MEMBERS))
)
GAME_RESOURCE_PREFIXES: Final = (
    "MSG/",
    "MSG_PK/",
    "RES_JP/",
    "RES_JP_PK/",
    "RES_JP_PK_PORT/",
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load patcher module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PATCHER = load_module("v0140_resource_patcher_release", PATCHER_SOURCE)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def file_spec(blob: bytes) -> dict[str, object]:
    return {"size": len(blob), "sha256": sha256_bytes(blob)}


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def member_path(root: Path, relative: str) -> Path:
    candidate = root / Path(relative)
    if not candidate.is_file():
        raise RuntimeError(f"missing release payload file: {relative}")
    return candidate


def read_support_payload(payload_root: Path) -> dict[str, bytes]:
    payload_root = payload_root.resolve(strict=True)
    actual = {
        path.relative_to(payload_root).as_posix()
        for path in payload_root.rglob("*")
        if path.is_file()
    }
    expected = set(SUPPORT_MEMBERS)
    if actual != expected:
        raise RuntimeError(
            "release payload member set differs "
            f"(unexpected={sorted(actual - expected)}, missing={sorted(expected - actual)})"
        )
    return {relative: member_path(payload_root, relative).read_bytes() for relative in SUPPORT_MEMBERS}


def read_binary_delta_payload(binary_patch_root: Path) -> dict[str, bytes]:
    """Read exactly the five bounded BSDIFF40 payloads for direct mode."""
    binary_patch_root = binary_patch_root.resolve(strict=True)
    expected = {PATCHER.binary_patch_member(relative) for relative in PATCHER.BINARY_RESOURCE_PATHS}
    actual = {
        path.relative_to(binary_patch_root).as_posix()
        for path in binary_patch_root.rglob("*")
        if path.is_file()
    }
    if actual != expected:
        raise RuntimeError(
            "binary delta member set differs "
            f"(unexpected={sorted(actual - expected)}, missing={sorted(expected - actual)})"
        )
    payload = {
        "patches/" + relative: (binary_patch_root / Path(relative)).read_bytes()
        for relative in sorted(expected)
    }
    for relative, blob in payload.items():
        if not relative.endswith(".bsdiff") or len(blob) > PATCHER.MAX_BINARY_PATCH_BYTES:
            raise RuntimeError(f"binary delta violates payload policy: {relative}")
    return payload


def reject_game_content(members: Mapping[str, bytes]) -> None:
    for relative in members:
        normalized = relative.replace("\\", "/")
        folded = normalized.casefold()
        if normalized.startswith(GAME_RESOURCE_PREFIXES) or folded == "nobu16pk.exe":
            raise RuntimeError(f"release archive must not contain game content: {relative}")
        if folded.endswith(".bin"):
            raise RuntimeError(f"release archive must not contain a binary game resource: {relative}")


def write_zip_atomic(path: Path, members: Mapping[str, bytes]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        with zipfile.ZipFile(
            temporary,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
            strict_timestamps=True,
        ) as archive:
            for relative in sorted(members):
                info = zipfile.ZipInfo(relative, date_time=ZIP_TIMESTAMP)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                archive.writestr(info, members[relative], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def manifest_for(members: Mapping[str, bytes], ledger: Mapping[str, Any]) -> dict[str, object]:
    delta_members = {
        path: file_spec(blob)
        for path, blob in sorted(members.items())
        if path.startswith("patches/binary/") and path.endswith(".bsdiff")
    }
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "release_zip": ZIP_NAME,
        "distribution": {
            "kind": "pristine-steam-jp-1.1.7-to-v0.14.0-direct-unified-patcher",
            "complete_game_resource_count": 0,
            "game_executable_count": 0,
            "requires_exact_pristine_profile": True,
            "source_profile": ledger["source_profile"],
        },
        "resource_patcher": {
            "internal_executable": PATCHER_MEMBER,
            "executable": PATCHER_MEMBER,
            "ledger": LEDGER_MEMBER,
            "changed_resource_count": len(PATCHER.RESOURCE_PATHS),
            "text_resource_count": len(PATCHER.TEXT_RESOURCE_PATHS),
            "binary_delta_resource_count": len(PATCHER.BINARY_RESOURCE_PATHS),
            "full_preflight_resource_count": len(PATCHER.RESOURCE_PATHS),
            "changed_resources": list(PATCHER.RESOURCE_PATHS),
            "backup_directory": "KR_PATCH_BACKUP/v0.14.0-direct-patcher",
            "operation_counts": ledger["operation_counts"],
            "payload_policy": ledger["payload_policy"],
            "binary_deltas": delta_members,
            "completion_banner": {
                "creator_display": "\uc81c\uc791: \ub514\uc2dc\uc778\uc0ac\uc774\ub4dc \uc2e0\uc7a5\uc758\uc57c\ub9dd \uac24\ub7ec\ub9ac parsifal",
                "creator": "디시인사이드 신장의야망 갤러리 parsifal",
                "github": "https://github.com/parsifal295/nobu16-korean-patch",
            },
        },
        "static_installer": {
            "included": True,
            "integrated_into_unified_patcher": True,
            "engine_support_file_count": len(STATIC_ENGINE_MEMBERS),
            "registered_patch_count": 10,
        },
        "unified_patcher": {
            "apply_entrypoint": "APPLY_KOREAN_PATCH.bat",
            "restore_entrypoint": "RESTORE_KOREAN_PATCH.bat",
            "coordinator": "Invoke-Nobu16KoreanPatch.ps1",
            "apply_order": ["static_exe", "resources"],
            "restore_order": ["resources", "static_exe"],
            "public_entrypoint_count": 2,
            "compensates_pristine_static_exe_if_resource_apply_fails": True,
        },
        "files": {relative: file_spec(blob) for relative, blob in sorted(members.items())},
    }


def build(
    pristine_root: Path,
    game_root: Path,
    patcher_exe: Path,
    binary_patch_root: Path,
    output: Path,
    payload_root: Path = DEFAULT_PAYLOAD_ROOT,
) -> dict[str, object]:
    """Build a deterministic public ZIP and its sidecar manifest."""
    patcher_exe = patcher_exe.resolve(strict=True)
    if not patcher_exe.is_file():
        raise RuntimeError(f"patcher executable is not a file: {patcher_exe}")
    if patcher_exe.name != PATCHER_MEMBER:
        raise RuntimeError(f"patcher executable must be named {PATCHER_MEMBER}")

    ledger = PATCHER.build_ledger(pristine_root, game_root, binary_patch_root)
    PATCHER.verify_ledger(ledger)
    members = read_support_payload(payload_root)
    members[PATCHER_MEMBER] = patcher_exe.read_bytes()
    members[LEDGER_MEMBER] = PATCHER.canonical_ledger_bytes(ledger)
    members.update(read_binary_delta_payload(binary_patch_root))
    reject_game_content(members)

    manifest = manifest_for(members, ledger)
    members[MANIFEST_NAME] = canonical_json(manifest)
    reject_game_content(members)

    output = output.resolve()
    write_zip_atomic(output / ZIP_NAME, members)
    PATCHER.atomic_write(output / MANIFEST_NAME, members[MANIFEST_NAME])
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pristine-root", type=Path, required=True)
    parser.add_argument("--game-root", type=Path, required=True)
    parser.add_argument("--patcher-exe", type=Path, required=True)
    parser.add_argument("--binary-patch-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--payload-root", type=Path, default=DEFAULT_PAYLOAD_ROOT)
    args = parser.parse_args()
    manifest = build(
        args.pristine_root,
        args.game_root,
        args.patcher_exe,
        args.binary_patch_root,
        args.output,
        args.payload_root,
    )
    print(args.output / ZIP_NAME)
    print(json.dumps(manifest["distribution"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
