#!/usr/bin/env python3
"""Build the public Steam JP 1.1.7 v0.11.1 release from pinned inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import uuid
import zipfile
from pathlib import Path, PurePosixPath
from typing import Final, Mapping


VERSION: Final = "v0.11.1"
ZIP_NAME: Final = "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.11.1.zip"
ZIP_TIMESTAMP: Final = (2026, 7, 18, 0, 0, 0)
SCHEMA: Final = "nobu16.kr.steam-jp-1.1.7-release.v0.11.1"
MANIFEST_NAME: Final = "release_manifest.v0.11.1.json"
PROJECT_ROOT: Final = Path(__file__).resolve().parents[1]
DEFAULT_PAYLOAD_ROOT: Final = PROJECT_ROOT / "release_payload" / "v0.11.1"

# These are the exact same 15 Korean resource pins published in v0.10.2.
GAME_TARGETS: Final = {
    "MSG/JP/ev_strdata.bin": (928_605, "6A7D90C1A95AD42DCAE2D3C3719508EDD00588288659A1D192B680CF70EAE6E4"),
    "MSG/JP/msggame.bin": (1_504_213, "8DBFCDB21BBDAAD4FE3928AD5B7AAA0D51E56D01F206DFE4D129E354FA5DEDE2"),
    "MSG/JP/strdata.bin": (957_008, "D518A91E36B9A59EAD0B5ED1FDD067941E4BF72E43AFCB19C296C8AD77C8C128"),
    "MSG_PK/JP/msgbre.bin": (478_595, "C545CD2251E61AEB0A68E10A08ADFFCD3B150C32B5D15236D90727A305B03BAE"),
    "MSG_PK/JP/msgdata.bin": (497_517, "7EAA33BC80C021A028660DF1A7934886591A1DA36DB7BC53146749C3A4AEF040"),
    "MSG_PK/JP/msgev.bin": (995_446, "B8B3B1C5A635419E590DB866C240A1B6609799E0FEA0E69F86D6208F27E5C52B"),
    "MSG_PK/JP/msggame.bin": (1_808_743, "DE606E50C9A6241BD0B85D17A000394007952093984F75DB56E296E0CCDE6B01"),
    "MSG_PK/JP/msgire.bin": (23_136, "C4977A74B98605AB350BE761C67CCF879AEE7565104F8D7FD2B725FDD5806D84"),
    "MSG_PK/JP/msgstf.bin": (17_337, "B90BB9C18C92626A3E9B0F9A2620FEFAAD9A51A2E67C95B8514CC4E4F4A5C607"),
    "MSG_PK/JP/msgui.bin": (122_568, "470FAD81852C6D80D2E1A0390F89A5590529ACE0BE5192DC1C1C58F70178D0DB"),
    "RES_JP/res_lang.bin": (161_428_458, "3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7"),
    "RES_JP/res_lang_exp.bin": (13_796_051, "AC55622FC5C78ECA4ECFE37D1D890D5B26F6200ED7BAF1506B784541E158B7B7"),
    "RES_JP_PK/res_lang_pk.bin": (141_893_576, "9019582ABBF88B08562B366E7D5A4283C6507455F86A801946AC32CCC25C2C2F"),
    "RES_JP_PK_PORT/res_lang_pk_port1.bin": (83_878_438, "F65383C72291D08B71EBA7E2EF504A8C674E7C4678445045868D98FCA5B0730D"),
    "RES_JP_PK_PORT/res_lang_pk_port2.bin": (67_623_137, "09531F21FA3BD56E2554C47942E47B5ACB61A7F279EFBF4AF85E4CAB963E4FAA"),
}

# These are the exact static-installer files in the release.  The only bundled
# executables are the unmodified, hash-pinned Steamless CLI and its one x64
# Variant 3.1 plug-in; NOBU16PK.exe itself is deliberately excluded.
EXPECTED_SUPPORT_MEMBERS: Final = (
    "APPLY_STATIC_OFFICER_EDITOR_FIX.bat",
    "OfficerEditorStaticFix/Invoke-StaticOfficerEditorFix.ps1",
    "OfficerEditorStaticFix/Steamless/Plugins/Steamless.API.dll",
    "OfficerEditorStaticFix/Steamless/Plugins/Steamless.Unpacker.Variant31.x64.dll",
    "OfficerEditorStaticFix/Steamless/Steamless.CLI.exe",
    "OfficerEditorStaticFix/Steamless/Steamless.CLI.exe.config",
    "OfficerEditorStaticFix/THIRD_PARTY_NOTICES.txt",
    "RESTORE_ORIGINAL_NOBU16PK_EXE.bat",
    "STATIC_OFFICER_EDITOR_FIX_README_KO.txt",
)
SUPPORT_TARGETS: Final = {
    "APPLY_STATIC_OFFICER_EDITOR_FIX.bat": (
        358,
        "48A68DECA8454F22B0DA7C509C4C913B8246B5998C2373EE98C57EB08E69AB68",
    ),
    "OfficerEditorStaticFix/Invoke-StaticOfficerEditorFix.ps1": (
        12_032,
        "92ADE5869923A139DF142C6A65946166B059290C00B39BD8FCD37FB5C3C2BFFA",
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
        3_227,
        "1545927C521E4C594E100B154002700A1BD57B892C96BA826C27598F92399216",
    ),
}
STATIC_EXE_PATCH: Final = {
    "delivery": "one-time-local-installer",
    "per_session_component": False,
    "process_memory_access": False,
    "target": "NOBU16PK.exe",
    "input_size": 31_978_264,
    "input_sha256": "29BC1ED66D27B9AEF5EB6CE3D126BA2BDBF86099E12B09615FE9F988F41E2246",
    "unpacked_size": 31_747_848,
    "unpacked_sha256": "BC885875A5E4288E5A1A424D99974F6F215777C03569C7EA707FDE63BDBC2B39",
    "output_size": 31_747_848,
    "output_sha256": "2E098ECB5E4335DC264F865306B990B724EA7C242B1B9F87FFC5EE2E7191797C",
    "output_authenticode": "NotSigned",
    "backup_filename": "NOBU16PK.exe.staticfix.original_1.1.7",
    "patch_site_count": 5,
    "requires_game_stopped": True,
    "requires_dotnet_framework": "4.5.2",
}
STEAMLESS: Final = {
    "name": "Steamless",
    "version": "v3.1.0.5",
    "source": "https://github.com/atom0s/Steamless",
    "license": "CC-BY-NC-ND-4.0",
    "license_url": "https://creativecommons.org/licenses/by-nc-nd/4.0/",
    "minimal_member_count": 4,
}


class ReleaseError(ValueError):
    pass


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _validate_pin(relative: str, pin: tuple[int, str]) -> None:
    canonical = PurePosixPath(relative)
    if relative != canonical.as_posix() or canonical.is_absolute() or ".." in canonical.parts:
        raise ReleaseError(f"non-canonical release member: {relative}")
    size, sha256 = pin
    if size <= 0 or len(sha256) != 64 or sha256 != sha256.upper():
        raise ReleaseError(f"invalid release pin: {relative}")
    try:
        int(sha256, 16)
    except ValueError as exc:
        raise ReleaseError(f"invalid release pin: {relative}") from exc


def _reject_forbidden_member(relative: str) -> None:
    path = PurePosixPath(relative)
    lower_parts = tuple(part.casefold() for part in path.parts)
    basename = lower_parts[-1]
    if basename.startswith("nobu16pk") and basename.endswith(".exe"):
        raise ReleaseError("the proprietary game executable must not enter a release")
    if basename.endswith(".unpacked.exe") or basename.endswith((".bak", ".orig", ".rep")):
        raise ReleaseError(f"generated executable or backup must not enter a release: {relative}")
    if any(part in {"workstreams", "tmp", "analysis", "backups", "logs", ".git"} for part in lower_parts):
        raise ReleaseError("workstreams/tmp/analysis files must not enter a release")
    if relative in EXPECTED_SUPPORT_MEMBERS:
        return
    if any("steamless" in part for part in lower_parts):
        raise ReleaseError(f"unapproved Steamless member: {relative}")
    if path.suffix.casefold() in {".exe", ".dll", ".ps1", ".bat", ".cmd"}:
        raise ReleaseError(f"unapproved executable release member: {relative}")


def validate_release_contract(
    game_targets: Mapping[str, tuple[int, str]],
    support_targets: Mapping[str, tuple[int, str]],
) -> None:
    if tuple(sorted(game_targets)) != tuple(sorted(GAME_TARGETS)):
        raise ReleaseError("game resource member vector differs from the pinned 15-file contract")
    if tuple(sorted(support_targets)) != tuple(sorted(EXPECTED_SUPPORT_MEMBERS)):
        raise ReleaseError("support member vector differs from the static-installer allowlist")
    if set(game_targets) & set(support_targets):
        raise ReleaseError("game and support member vectors overlap")
    for relative, pin in {**game_targets, **support_targets}.items():
        _validate_pin(relative, pin)
        _reject_forbidden_member(relative)


def validate_payload_directory(payload_root: Path, support_targets: Mapping[str, tuple[int, str]]) -> None:
    if not payload_root.is_dir():
        raise ReleaseError(f"missing release payload directory: {payload_root}")
    actual: list[str] = []
    for entry in sorted(payload_root.rglob("*")):
        relative = entry.relative_to(payload_root).as_posix()
        if entry.is_symlink():
            raise ReleaseError(f"release payload symlink is forbidden: {relative}")
        if entry.is_file():
            _reject_forbidden_member(relative)
            actual.append(relative)
    if actual != sorted(support_targets):
        raise ReleaseError(
            f"release payload member vector differs: expected={sorted(support_targets)!r} "
            f"actual={actual!r}"
        )


def source_specs(
    game_root: Path,
    payload_root: Path,
    game_targets: Mapping[str, tuple[int, str]],
    support_targets: Mapping[str, tuple[int, str]],
) -> tuple[dict[str, dict[str, object]], dict[str, Path]]:
    validate_release_contract(game_targets, support_targets)
    validate_payload_directory(payload_root, support_targets)
    specs: dict[str, dict[str, object]] = {}
    sources: dict[str, Path] = {}
    for relative, (expected_size, expected_hash) in sorted(game_targets.items()):
        sources[relative] = game_root / Path(relative)
        if not sources[relative].is_file():
            raise ReleaseError(f"missing release input: {sources[relative]}")
        actual_size = sources[relative].stat().st_size
        actual_hash = sha256_file(sources[relative])
        if actual_size != expected_size or actual_hash != expected_hash:
            raise ReleaseError(
                f"release input differs: {relative} size={actual_size} sha256={actual_hash}"
            )
        specs[relative] = {"size": actual_size, "sha256": actual_hash}
    for relative, (expected_size, expected_hash) in sorted(support_targets.items()):
        sources[relative] = payload_root / Path(relative)
        actual_size = sources[relative].stat().st_size
        actual_hash = sha256_file(sources[relative])
        if actual_size != expected_size or actual_hash != expected_hash:
            raise ReleaseError(
                f"release payload differs: {relative} size={actual_size} sha256={actual_hash}"
            )
        specs[relative] = {"size": actual_size, "sha256": actual_hash}
    return dict(sorted(specs.items())), sources


def make_zip(sources: Mapping[str, Path], destination: Path) -> dict[str, object]:
    if destination.exists():
        raise ReleaseError(f"refusing to overwrite: {destination}")
    with zipfile.ZipFile(
        destination,
        "x",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        strict_timestamps=True,
    ) as archive:
        for relative, source in sorted(sources.items()):
            payload = source.read_bytes()
            info = zipfile.ZipInfo(relative, date_time=ZIP_TIMESTAMP)
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            info.flag_bits |= 0x800
            archive.writestr(
                info,
                payload,
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )
    return {"size": destination.stat().st_size, "sha256": sha256_file(destination)}


def verify_zip(archive_path: Path, expected: Mapping[str, Mapping[str, object]]) -> None:
    with zipfile.ZipFile(archive_path, "r") as archive:
        names = archive.namelist()
        if names != sorted(expected):
            raise ReleaseError("release member vector differs")
        if len(names) != len(set(names)):
            raise ReleaseError("release contains duplicate members")
        for relative in names:
            _reject_forbidden_member(relative)
            payload = archive.read(relative)
            spec = expected[relative]
            if len(payload) != spec["size"] or sha256_bytes(payload) != spec["sha256"]:
                raise ReleaseError(f"release payload differs: {relative}")
        bad_member = archive.testzip()
        if bad_member is not None:
            raise ReleaseError(f"ZIP CRC validation failed: {bad_member}")


def build(
    game_root: Path,
    output: Path,
    payload_root: Path = DEFAULT_PAYLOAD_ROOT,
    *,
    game_targets: Mapping[str, tuple[int, str]] = GAME_TARGETS,
    support_targets: Mapping[str, tuple[int, str]] = SUPPORT_TARGETS,
) -> dict[str, object]:
    game_root = game_root.resolve()
    payload_root = payload_root.resolve()
    output = output.resolve()
    if output.exists():
        raise ReleaseError(f"output already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = output.parent / f".{output.name}.staging-{uuid.uuid4().hex}"
    staging.mkdir()
    try:
        inputs, sources = source_specs(
            game_root, payload_root, game_targets, support_targets
        )
        first_zip = staging / ZIP_NAME
        first_spec = make_zip(sources, first_zip)
        verify_zip(first_zip, inputs)

        rebuild_zip = staging / f"{ZIP_NAME}.rebuild"
        rebuild_spec = make_zip(sources, rebuild_zip)
        verify_zip(rebuild_zip, inputs)
        if first_spec != rebuild_spec:
            raise ReleaseError("deterministic ZIP rebuild differs")
        rebuild_zip.unlink()

        manifest: dict[str, object] = {
            "schema": SCHEMA,
            "version": VERSION,
            "game": "NOBU16 PK Steam JP 1.1.7",
            "member_count": len(inputs),
            "game_resource_count": len(game_targets),
            "support_file_count": len(support_targets),
            "members": inputs,
            "static_exe_patch": STATIC_EXE_PATCH,
            "third_party": {"steamless": STEAMLESS},
            "release_zip": {"name": ZIP_NAME, **first_spec},
            "checks": {
                "all_source_hashes_pinned": True,
                "support_member_allowlist_exact": True,
                "only_pinned_third_party_binaries_allowed": True,
                "proprietary_game_executable_excluded": True,
                "steamless_minimal_dependencies_exact": True,
                "workstreams_tmp_and_analysis_excluded": True,
                "zip_payloads_match_sources": True,
                "zip_crc_valid": True,
                "deterministic_rebuild_identical": True,
            },
        }
        (staging / MANIFEST_NAME).write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        shutil.move(str(staging), str(output))
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", required=True, type=Path)
    parser.add_argument("--payload-root", type=Path, default=DEFAULT_PAYLOAD_ROOT)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    manifest = build(args.game_root, args.output, args.payload_root)
    print(json.dumps(manifest["release_zip"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
