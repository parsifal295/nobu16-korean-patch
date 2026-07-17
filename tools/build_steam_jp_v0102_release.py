#!/usr/bin/env python3
"""Build the public Steam JP 1.1.7 v0.10.2 release from a pinned live tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import uuid
import zipfile
from pathlib import Path
from typing import Final


VERSION: Final = "v0.10.2"
ZIP_NAME: Final = "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.10.2.zip"
ZIP_TIMESTAMP: Final = (2026, 7, 17, 0, 0, 0)
SCHEMA: Final = "nobu16.kr.steam-jp-1.1.7-release.v0.10.2"
MANIFEST_NAME: Final = "release_manifest.v0.10.2.json"

TARGETS: Final = {
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


def source_specs(game_root: Path) -> dict[str, dict[str, object]]:
    specs: dict[str, dict[str, object]] = {}
    for relative, (expected_size, expected_hash) in sorted(TARGETS.items()):
        source = game_root / Path(relative)
        if not source.is_file():
            raise ReleaseError(f"missing release input: {source}")
        actual_size = source.stat().st_size
        actual_hash = sha256_file(source)
        if actual_size != expected_size or actual_hash != expected_hash:
            raise ReleaseError(
                f"release input differs: {relative} "
                f"size={actual_size} sha256={actual_hash}"
            )
        specs[relative] = {"size": actual_size, "sha256": actual_hash}
    return specs


def make_zip(game_root: Path, destination: Path) -> dict[str, object]:
    if destination.exists():
        raise ReleaseError(f"refusing to overwrite: {destination}")
    with zipfile.ZipFile(
        destination,
        "x",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        strict_timestamps=True,
    ) as archive:
        for relative in sorted(TARGETS):
            payload = (game_root / Path(relative)).read_bytes()
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


def verify_zip(archive_path: Path, expected: dict[str, dict[str, object]]) -> None:
    with zipfile.ZipFile(archive_path, "r") as archive:
        names = archive.namelist()
        if names != sorted(TARGETS):
            raise ReleaseError("release member vector differs")
        for relative in names:
            payload = archive.read(relative)
            spec = expected[relative]
            if len(payload) != spec["size"] or sha256_bytes(payload) != spec["sha256"]:
                raise ReleaseError(f"release payload differs: {relative}")
        bad_member = archive.testzip()
        if bad_member is not None:
            raise ReleaseError(f"ZIP CRC validation failed: {bad_member}")


def build(game_root: Path, output: Path) -> dict[str, object]:
    game_root = game_root.resolve()
    output = output.resolve()
    if output.exists():
        raise ReleaseError(f"output already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = output.parent / f".{output.name}.staging-{uuid.uuid4().hex}"
    staging.mkdir()
    try:
        inputs = source_specs(game_root)
        first_zip = staging / ZIP_NAME
        first_spec = make_zip(game_root, first_zip)
        verify_zip(first_zip, inputs)

        rebuild_zip = staging / f"{ZIP_NAME}.rebuild"
        rebuild_spec = make_zip(game_root, rebuild_zip)
        verify_zip(rebuild_zip, inputs)
        if first_spec != rebuild_spec:
            raise ReleaseError("deterministic ZIP rebuild differs")
        rebuild_zip.unlink()

        manifest: dict[str, object] = {
            "schema": SCHEMA,
            "version": VERSION,
            "game": "NOBU16 PK Steam JP 1.1.7",
            "member_count": len(inputs),
            "members": inputs,
            "release_zip": {"name": ZIP_NAME, **first_spec},
            "checks": {
                "all_source_hashes_pinned": True,
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
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    manifest = build(args.game_root, args.output)
    print(json.dumps(manifest["release_zip"], ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
