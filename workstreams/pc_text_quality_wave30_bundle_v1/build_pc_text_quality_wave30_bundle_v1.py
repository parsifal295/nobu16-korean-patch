#!/usr/bin/env python3
"""Compose the disjoint Wave 28 dialogue and Wave 29 NPC candidates.

The two candidates share the exact Wave 27 eleven-file profile as predecessor
and touch disjoint resources.  This private-only bundle makes that join
explicit before the single Steam transaction and public release build.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Final, Mapping


SCRIPT: Final = Path(__file__).resolve()
WORKSTREAM: Final = SCRIPT.parent
REPO: Final = WORKSTREAM.parents[1]
TMP: Final = REPO / "tmp"
WAVE27_ROOT: Final = Path(
    r"F:\Games\NOBU16\KR_PATCH_WORK\tmp\pc_dialogue_quality_wave27_static_quality_v1\candidate"
)
WAVE28_ROOT: Final = TMP / "pc_dialogue_quality_wave28_static_quality_v1" / "candidate"
WAVE29_ROOT: Final = TMP / "pc_npc_name_quality_wave29_v1" / "candidate"
DEFAULT_OUTPUT_ROOT: Final = TMP / WORKSTREAM.name / "candidate"
DEFAULT_MANIFEST: Final = TMP / WORKSTREAM.name / "build_manifest.v1.json"
SCHEMA: Final = "nobu16.kr.pc-text-quality-wave30-bundle.v1"

PROFILE_PATHS: Final = (
    "MSG/JP/ev_strdata.bin",
    "MSG/JP/msggame.bin",
    "MSG/JP/strdata.bin",
    "MSG_PK/JP/msgbre.bin",
    "MSG_PK/JP/msgdata.bin",
    "MSG_PK/JP/msgev.bin",
    "MSG_PK/JP/msggame.bin",
    "MSG_PK/JP/msgire.bin",
    "MSG_PK/JP/msgstf.bin",
    "MSG_PK/JP/msgstf_ce.bin",
    "MSG_PK/JP/msgui.bin",
)
WAVE28_PATHS: Final = frozenset({"MSG/JP/msggame.bin", "MSG_PK/JP/msggame.bin"})
WAVE29_PATHS: Final = frozenset(
    {
        "MSG/JP/ev_strdata.bin",
        "MSG/JP/strdata.bin",
        "MSG_PK/JP/msgdata.bin",
        "MSG_PK/JP/msgev.bin",
    }
)
if WAVE28_PATHS & WAVE29_PATHS:
    raise RuntimeError("Wave 28 and Wave 29 paths must be disjoint")

WAVE27_PROFILE: Final = {
    "MSG/JP/ev_strdata.bin": (928_123, "BF224468BFBCF3CC71DFF4609142A60D75091813281EE6F2333645413AD81B80"),
    "MSG/JP/msggame.bin": (1_504_526, "4D6460F1B717FD8D424229ABD619DE4093C21929F6C42B061BAD62E163C5D3CB"),
    "MSG/JP/strdata.bin": (957_204, "6E7DD096A999299C43A9A23D9E99F75C81D6A9C8116488EC541A43423871B933"),
    "MSG_PK/JP/msgbre.bin": (484_068, "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939"),
    "MSG_PK/JP/msgdata.bin": (496_995, "73CF194E4EF81C20692A245DAC75C3B2A9FCF1A997B7F6755D89DBB59149F2ED"),
    "MSG_PK/JP/msgev.bin": (994_731, "91F4C99B1C4D21CE9A3529CB174AA1EFD9E198E8FEB6F90F5AD507CEBB4B8C4F"),
    "MSG_PK/JP/msggame.bin": (1_806_647, "AD3F6DD64C0AD360C5A8C7A4747ABFCE9B2D72BFFDD3D44940781A68AC2DE8D1"),
    "MSG_PK/JP/msgire.bin": (23_128, "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB"),
    "MSG_PK/JP/msgstf.bin": (17_341, "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B"),
    "MSG_PK/JP/msgstf_ce.bin": (18_767, "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63"),
    "MSG_PK/JP/msgui.bin": (122_733, "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7"),
}
WAVE28_PROFILE: Final = {
    **WAVE27_PROFILE,
    "MSG/JP/msggame.bin": (1_504_422, "D70BA2EBE17CE056B9E348C610FE1F82B28285BAF1940F4450AE2D7D62B2E688"),
    "MSG_PK/JP/msggame.bin": (1_806_542, "0BDE96CF07C97B0FF71EBB5C2032E62F313BA271BD772D5BC79A48E57356A0F9"),
}
WAVE29_PROFILE: Final = {
    **WAVE27_PROFILE,
    "MSG/JP/ev_strdata.bin": (928_119, "02AC90B818E8F75683CD5BACF277E91048D4510E448A8699242D3B19299FE067"),
    "MSG/JP/strdata.bin": (957_200, "37A1F6280B2663A7FF055C6A2105B5658CA62065582A66213C6D4D4AE2A79E0A"),
    "MSG_PK/JP/msgdata.bin": (496_991, "8282F12A667E11F54054856035415C7297385ADD16EC261BD952BEBB8658952A"),
    "MSG_PK/JP/msgev.bin": (994_727, "AEE0D9992B963E17B3C118AA54DACC60390936FF48876674CA7675A2A11A3668"),
}
TARGET_PROFILE: Final = {**WAVE29_PROFILE, **{path: WAVE28_PROFILE[path] for path in WAVE28_PATHS}}


class BundleError(ValueError):
    pass


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def require_under(root: Path, path: Path, label: str) -> Path:
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise BundleError(f"{label} escapes {resolved_root}: {resolved_path}") from exc
    return resolved_path


def profile(root: Path) -> dict[str, tuple[int, str]]:
    result: dict[str, tuple[int, str]] = {}
    for relative in PROFILE_PATHS:
        path = root / relative
        if not path.is_file():
            raise BundleError(f"missing profile member: {path}")
        result[relative] = (path.stat().st_size, sha256_path(path))
    return result


def require_profile(root: Path, expected: Mapping[str, tuple[int, str]], label: str) -> None:
    actual = profile(root)
    if actual != dict(expected):
        mismatch = {
            path: {"expected": expected[path], "actual": actual[path]}
            for path in PROFILE_PATHS
            if actual[path] != expected[path]
        }
        raise BundleError(f"{label} profile mismatch: {mismatch}")


def validate_inputs() -> None:
    require_profile(WAVE27_ROOT, WAVE27_PROFILE, "Wave27 predecessor")
    require_profile(WAVE28_ROOT, WAVE28_PROFILE, "Wave28 candidate")
    require_profile(WAVE29_ROOT, WAVE29_PROFILE, "Wave29 candidate")
    for path in PROFILE_PATHS:
        if path not in WAVE28_PATHS and (WAVE28_ROOT / path).read_bytes() != (WAVE27_ROOT / path).read_bytes():
            raise BundleError(f"Wave28 changed an out-of-scope path: {path}")
        if path not in WAVE29_PATHS and (WAVE29_ROOT / path).read_bytes() != (WAVE27_ROOT / path).read_bytes():
            raise BundleError(f"Wave29 changed an out-of-scope path: {path}")


def composed_payloads() -> dict[str, bytes]:
    validate_inputs()
    payloads = {path: (WAVE27_ROOT / path).read_bytes() for path in PROFILE_PATHS}
    for path in WAVE28_PATHS:
        payloads[path] = (WAVE28_ROOT / path).read_bytes()
    for path in WAVE29_PATHS:
        payloads[path] = (WAVE29_ROOT / path).read_bytes()
    actual = {path: (len(payload), sha256_bytes(payload)) for path, payload in payloads.items()}
    if actual != TARGET_PROFILE:
        raise BundleError("composed target profile mismatch")
    return payloads


def manifest_for(payloads: Mapping[str, bytes]) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "predecessor_root": str(WAVE27_ROOT),
        "input_candidates": {"wave28": str(WAVE28_ROOT), "wave29": str(WAVE29_ROOT)},
        "overlay_paths": {"wave28": sorted(WAVE28_PATHS), "wave29": sorted(WAVE29_PATHS)},
        "profile": {
            path: {"size": len(payloads[path]), "sha256": sha256_bytes(payloads[path])}
            for path in PROFILE_PATHS
        },
        "source_policy": {
            "pc_only_inputs": True,
            "alternate_platform_input": "absent",
            "steam_write_capability": "absent",
            "git_operation": "absent",
            "release_operation": "absent",
        },
    }


def write_candidate(output_root: Path) -> dict[str, object]:
    output_root = require_under(TMP, output_root, "output root")
    if output_root.exists():
        raise BundleError(f"refusing to overwrite candidate: {output_root}")
    payloads = composed_payloads()
    output_root.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".wave30-", dir=output_root.parent))
    try:
        for relative, payload in payloads.items():
            path = staging / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        actual = profile(staging)
        if actual != TARGET_PROFILE:
            raise BundleError("staged candidate profile mismatch")
        os.replace(staging, output_root)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return manifest_for(payloads)


def write_manifest(path: Path, manifest: Mapping[str, object]) -> None:
    path = require_under(TMP, path, "manifest path")
    if path.exists():
        raise BundleError(f"refusing to overwrite manifest: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_private(output_root: Path) -> dict[str, object]:
    output_root = require_under(TMP, output_root, "candidate root")
    require_profile(output_root, TARGET_PROFILE, "private candidate")
    return {
        "schema": SCHEMA,
        "candidate_root": str(output_root),
        "changed_path_count": len(WAVE28_PATHS | WAVE29_PATHS),
        "profile_sha256": {path: TARGET_PROFILE[path][1] for path in PROFILE_PATHS},
        "status": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("hash")
    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    build_parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    verify_parser = subparsers.add_parser("verify-private")
    verify_parser.add_argument("--candidate-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()

    if args.command == "hash":
        validate_inputs()
        print(json.dumps({"schema": SCHEMA, "target_profile": TARGET_PROFILE, "status": "PASS"}, indent=2, sort_keys=True))
        return 0
    if args.command == "build":
        manifest = write_candidate(args.output_root)
        write_manifest(args.manifest, manifest)
        print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    print(json.dumps(verify_private(args.candidate_root), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
