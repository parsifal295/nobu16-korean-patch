#!/usr/bin/env python3
"""Verify and publish the source-free WaveC non-caller assignment."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
REPO = next(
    parent
    for parent in SCRIPT.parents
    if (parent / "workstreams" / "pk_msggame_runtime_vm_audit_v1").is_dir()
)
TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
PRIVATE_BUILDER = (
    TMP / "build_pk_msggame_waveC_noncaller_packets.private.v1.py"
)
PRIVATE_MANIFEST = (
    TMP / "pk_msggame_waveC_noncaller_assignment.private.v1.json"
)
PRIVATE_PACKETS = tuple(
    TMP / "pk_msggame_waveC_noncaller_packets" / f"bundle{index}.private.v1.json"
    for index in range(3)
)
DEFAULT_PUBLIC = (
    SCRIPT.parent
    / "public"
    / "pk_msggame_waveC_noncaller_assignment.source_free.v1.json"
)
EXPECTED_INPUT_SHA256 = {
    "private_builder":
        "E661086CC0A9648B86C38B0BCCDFBB20292CC8639FCC46D698A028BF73433F4F",
    "private_manifest":
        "59771CEFF36F531C795DCF11F881AA2907F07FAC361C73A154100C4AC62051FB",
    "packet0":
        "00D0DBE15DA431656B28A3FB3071AFEA39D9CE7B3734E1F25E58CD96ADE7A9C1",
    "packet1":
        "B2E0340202AC6A093BF06EE736F779D4878200055728A40A72CCD195F18ABAFB",
    "packet2":
        "82E2722A3596C2DD4E5C80AE51745E164DF9BD594D0C88B095941310AA1C86DF",
}
EXPECTED_PUBLIC_SHA256: str | None = (
    "8AE1B4FE9FFD93C419E62DAFA1E099272CCE70A8A0B8E8B771838A27E4453A4A"
)


class AssignmentError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssignmentError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_module(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(
        "pk_waveC_private_assignment_engine", path
    )
    require(spec is not None and spec.loader is not None, "cannot load builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def build_public() -> tuple[bytes, dict[str, Any]]:
    observed = {
        "private_builder": sha256_file(PRIVATE_BUILDER),
        "private_manifest": sha256_file(PRIVATE_MANIFEST),
        **{
            f"packet{index}": sha256_file(path)
            for index, path in enumerate(PRIVATE_PACKETS)
        },
    }
    require(
        observed == EXPECTED_INPUT_SHA256,
        f"frozen WaveC assignment drift: {observed}",
    )

    engine = load_module(PRIVATE_BUILDER)
    packets, manifest_payload, rebuilt = engine.build_outputs()
    require(
        manifest_payload == PRIVATE_MANIFEST.read_bytes(),
        "private manifest does not reproduce",
    )
    require(
        all(
            payload == path.read_bytes()
            for payload, path in zip(packets, PRIVATE_PACKETS)
        ),
        "private packet does not reproduce",
    )
    manifest = json.loads(manifest_payload)
    scope = manifest["scope"]
    require(
        manifest["status"] == "PASS"
        and scope["checkpoint_pending_coordinate_count"] == 3_293
        and scope["WaveB_caller_coordinate_count"] == 1_214
        and scope["noncaller_coordinate_count"] == 2_079
        and scope["noncaller_root_count"] == 1_678
        and scope["noncaller_unit_count"] == 726,
        "WaveC scope drift",
    )
    require(
        [row["coordinate_count"] for row in manifest["bundles"]]
        == [693, 693, 693]
        and [row["unit_count"] for row in manifest["bundles"]]
        == [242, 242, 242],
        "WaveC balance drift",
    )

    public = {
        "schema":
            "nobu16.kr.pk-msggame-waveC-noncaller-assignment.source-free.v1",
        "method": manifest["method"],
        "release_target": "0.15.0",
        "inputs": {
            "private_builder_sha256": observed["private_builder"],
            "private_manifest_sha256": observed["private_manifest"],
            "packet_sha256": [
                observed["packet0"],
                observed["packet1"],
                observed["packet2"],
            ],
        },
        "scope": scope,
        "bundles": [
            {
                "packet_id": row["packet_id"],
                "coordinate_count": row["coordinate_count"],
                "coordinate_sha256": row["coordinate_sha256"],
                "root_count": row["root_count"],
                "root_sha256": row["root_sha256"],
                "unit_count": row["unit_count"],
                "packet_sha256": row["packet_sha256"],
            }
            for row in manifest["bundles"]
        ],
        "proof": {
            **manifest["proof"],
            "private_builder_reproduced": True,
            "private_manifest_reproduced": True,
            "private_packets_reproduced": True,
            "global_unit_ids_unique": True,
        },
        "privacy": {
            "source_free": True,
            "contains_dialogue_bodies": False,
            "contains_translations": False,
            "private_packets_stay_below_tmp": True,
        },
        "status": "PASS",
        "steam_write_performed": False,
    }
    require(rebuilt == manifest, "private builder value drift")
    payload = (
        json.dumps(public, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    ).encode("ascii")
    return payload, public


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--bootstrap-output-pin", action="store_true")
    parser.add_argument("--public", type=Path, default=DEFAULT_PUBLIC)
    args = parser.parse_args(argv)

    payload, public = build_public()
    observed = sha256_bytes(payload)
    if args.bootstrap_output_pin:
        require(args.write, "pin may only be bootstrapped with --write")
    else:
        require(EXPECTED_PUBLIC_SHA256 is not None, "unfrozen public pin")
        require(observed == EXPECTED_PUBLIC_SHA256, "public output drift")
    if args.write:
        atomic_write(args.public, payload)
    else:
        require(args.public.read_bytes() == payload, "public file drift")
    print(
        json.dumps(
            {
                "status": public["status"],
                "scope": public["scope"],
                "public_sha256": observed,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
