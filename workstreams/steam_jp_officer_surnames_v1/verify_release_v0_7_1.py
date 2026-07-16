#!/usr/bin/env python3
"""Verify the tracked v0.7.1 hash manifest and an optional release ZIP."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "release_manifest.v0.7.1.json"
EXPECTED_PATHS = {
    "MSG/JP/strdata.bin",
    "MSG_PK/JP/msgbre.bin",
    "MSG_PK/JP/msgdata.bin",
    "MSG_PK/JP/msgev.bin",
    "MSG_PK/JP/msggame.bin",
    "MSG_PK/JP/msgire.bin",
    "MSG_PK/JP/msgstf.bin",
    "MSG_PK/JP/msgui.bin",
    "RES_JP/res_lang.bin",
    "RES_JP_PK/res_lang_pk.bin",
    "RES_JP_PK_PORT/res_lang_pk_port1.bin",
    "RES_JP_PK_PORT/res_lang_pk_port2.bin",
}
FONT_PATHS = {
    "RES_JP/res_lang.bin",
    "RES_JP_PK/res_lang_pk.bin",
    "RES_JP_PK_PORT/res_lang_pk_port1.bin",
    "RES_JP_PK_PORT/res_lang_pk_port2.bin",
}
HASH = re.compile(r"^[0-9A-F]{64}$")
SURNAME_MSGDATA_HASH = "FF8D4BB10D93CED860AF17AA5CECB3EDCED97887D69F8862AAF9D4161D790F65"


class ReleaseVerificationError(ValueError):
    """The release manifest or ZIP differs from the exact hotfix vector."""


def sha256_stream(stream) -> str:
    digest = hashlib.sha256()
    while chunk := stream.read(1024 * 1024):
        digest.update(chunk)
    return digest.hexdigest().upper()


def load_manifest(path: Path = MANIFEST) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != "nobu16.kr.steam-jp-hotfix-release-manifest.v1":
        raise ReleaseVerificationError("release manifest schema differs")
    release = value.get("release", {})
    if (
        release.get("tag") != "v0.7.1"
        or release.get("stable") is not True
        or release.get("prerelease") is not False
    ):
        raise ReleaseVerificationError("release identity differs")
    runtime = value.get("runtime", {})
    if runtime != {
        "distribution": "Steam",
        "pk_version": "1.1.7",
        "steam_build_id": 18823764,
        "language_route": "JP",
    }:
        raise ReleaseVerificationError("runtime identity differs")
    asset = value.get("asset", {})
    if (
        asset.get("name") != "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.7.1.zip"
        or asset.get("size") != 356_143_102
        or asset.get("sha256")
        != "B54E4BD95C1049C3E84800CA643F90E6A984733FE4F2E95BE063A086CB0BA1AE"
    ):
        raise ReleaseVerificationError("release asset identity differs")
    scope = value.get("scope", {})
    if scope != {
        "entry_count": 12,
        "officer_surnames_recovered": 980,
        "font_container_count": 4,
        "commercial_binary_bytes_included": False,
    }:
        raise ReleaseVerificationError("release scope differs")
    entries = value.get("entries")
    if not isinstance(entries, list) or len(entries) != 12:
        raise ReleaseVerificationError("release entry count differs")
    by_path = {row.get("path"): row for row in entries if isinstance(row, dict)}
    if set(by_path) != EXPECTED_PATHS or len(by_path) != len(entries):
        raise ReleaseVerificationError("exact-12 path vector differs")
    for path, row in by_path.items():
        if not isinstance(row.get("size"), int) or row["size"] <= 0:
            raise ReleaseVerificationError(f"invalid entry size: {path}")
        if not isinstance(row.get("sha256"), str) or not HASH.fullmatch(row["sha256"]):
            raise ReleaseVerificationError(f"invalid entry hash: {path}")
    if by_path["MSG_PK/JP/msgdata.bin"]["sha256"] != SURNAME_MSGDATA_HASH:
        raise ReleaseVerificationError("surname msgdata hash differs")
    if not FONT_PATHS <= set(by_path):
        raise ReleaseVerificationError("four JP font containers are incomplete")
    return value


def verify_zip(path: Path, manifest: dict) -> dict:
    if path.stat().st_size != manifest["asset"]["size"]:
        raise ReleaseVerificationError("ZIP size differs")
    with path.open("rb") as stream:
        if sha256_stream(stream) != manifest["asset"]["sha256"]:
            raise ReleaseVerificationError("ZIP hash differs")
    expected = {row["path"]: row for row in manifest["entries"]}
    with zipfile.ZipFile(path) as archive:
        files = [item for item in archive.infolist() if not item.is_dir()]
        names = [item.filename.replace("\\", "/") for item in files]
        if set(names) != set(expected) or len(names) != len(expected):
            raise ReleaseVerificationError("ZIP exact-12 path vector differs")
        for item, name in zip(files, names, strict=True):
            row = expected[name]
            if item.file_size != row["size"]:
                raise ReleaseVerificationError(f"ZIP entry size differs: {name}")
            with archive.open(item) as stream:
                if sha256_stream(stream) != row["sha256"]:
                    raise ReleaseVerificationError(f"ZIP entry hash differs: {name}")
    return {"status": "PASS", "entry_count": len(expected), "font_container_count": 4}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", type=Path)
    args = parser.parse_args()
    manifest = load_manifest()
    result = {"status": "PASS", "manifest": str(MANIFEST), "entry_count": 12}
    if args.zip is not None:
        result["zip"] = verify_zip(args.zip, manifest)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
