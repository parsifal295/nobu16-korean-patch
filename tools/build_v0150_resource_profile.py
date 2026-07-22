#!/usr/bin/env python3
"""Build the hash-only v0.15.0 direct-patcher resource profile."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping


SCRIPT = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT.parents[1]
V0140_PATCHER = PROJECT_ROOT / "tools" / "v0140_resource_patcher.py"
DEFAULT_OUTPUT = (
    PROJECT_ROOT
    / "release_payload"
    / "v0.15.0"
    / "v0.15.0-resource-profile.json"
)

PORT3_PATH = "RES_JP_PK_PORT/res_lang_pk_port3.bin"
PORT3_SOURCE = {
    "size": 43_484_341,
    "sha256": "51B7ED1FA81CD785591D52601035ED970C2B7D83A2DBC1D73C0B6C14E3F0D75B",
}
IMAGE_TARGETS: Mapping[str, Mapping[str, object]] = {
    "RES_JP/res_lang.bin": {
        "size": 154_714_237,
        "sha256": "952B97FAE48F5D077E4663EFBE7B2975ADDBC0A521E63F9EDE373D7A77D55600",
    },
    "RES_JP/res_lang_exp.bin": {
        "size": 13_796_051,
        "sha256": "AC55622FC5C78ECA4ECFE37D1D890D5B26F6200ED7BAF1506B784541E158B7B7",
    },
    "RES_JP_PK/res_lang_pk.bin": {
        "size": 141_893_576,
        "sha256": "9019582ABBF88B08562B366E7D5A4283C6507455F86A801946AC32CCC25C2C2F",
    },
    "RES_JP_PK_PORT/res_lang_pk_port1.bin": {
        "size": 82_905_500,
        "sha256": "E2B22DFD399E87DF109947F0F98FC58D1BF360B1B54299A6BB4D2051CE53EEA5",
    },
    "RES_JP_PK_PORT/res_lang_pk_port2.bin": {
        "size": 67_623_137,
        "sha256": "09531F21FA3BD56E2554C47942E47B5ACB61A7F279EFBF4AF85E4CAB963E4FAA",
    },
    PORT3_PATH: {
        "size": 43_161_969,
        "sha256": "BA739C28A8EE1A47C8085339F98FDCF4F317302316F93C3F74E413DB2AFEADC9",
    },
}


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V0140 = load_module("v0140_resource_patcher_for_v0150_profile", V0140_PATCHER)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def file_spec(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise RuntimeError(f"missing profile input: {path}")
    return {"size": path.stat().st_size, "sha256": sha256_file(path)}


def require_spec(path: Path, expected: Mapping[str, object], label: str) -> dict[str, object]:
    actual = file_spec(path)
    normalized = {
        "size": int(expected["size"]),
        "sha256": str(expected["sha256"]).upper(),
    }
    if actual != normalized:
        raise RuntimeError(f"{label} differs: {actual}")
    return actual


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def build_profile(
    pristine_root: Path,
    game_root: Path,
    receipt_path: Path,
    title_fix_receipt_path: Path,
) -> dict[str, object]:
    pristine_root = pristine_root.resolve(strict=True)
    game_root = game_root.resolve(strict=True)
    receipt = json.loads(receipt_path.read_text(encoding="utf-8-sig"))
    if (
        not isinstance(receipt, dict)
        or receipt.get("schema") != "nobu16.dlc_translation_steam_deployment.v1"
        or receipt.get("status") != "deployed"
        or receipt.get("file_count") != 105
        or not isinstance(receipt.get("files"), list)
        or len(receipt["files"]) != 105
    ):
        raise RuntimeError("DLC deployment receipt identity or file count differs")

    text_paths = tuple(V0140.TEXT_RESOURCE_PATHS)
    image_paths = tuple(V0140.BINARY_RESOURCE_PATHS) + (PORT3_PATH,)
    dlc_entries: dict[str, Mapping[str, object]] = {}
    for raw in receipt["files"]:
        if not isinstance(raw, Mapping):
            raise RuntimeError("DLC receipt contains a malformed file entry")
        relative = raw.get("path")
        if (
            not isinstance(relative, str)
            or relative in dlc_entries
            or not relative.endswith(".n16")
            or not relative.startswith(("DLC/JP/", "DLC_PK/JP/"))
        ):
            raise RuntimeError(f"DLC receipt path differs: {relative!r}")
        dlc_entries[relative] = raw
    title_fix_receipt = json.loads(title_fix_receipt_path.read_text(encoding="utf-8-sig"))
    if (
        not isinstance(title_fix_receipt, dict)
        or title_fix_receipt.get("schema")
        != "nobu16.dlc_translation_title_fix_deployment.v1"
        or title_fix_receipt.get("status") != "deployed"
        or title_fix_receipt.get("file_count") != 4
        or not isinstance(title_fix_receipt.get("files"), list)
        or len(title_fix_receipt["files"]) != 4
    ):
        raise RuntimeError("DLC title-fix receipt identity or file count differs")
    target_hashes = {
        path: str(entry["candidate_sha256"]).upper() for path, entry in dlc_entries.items()
    }
    for raw in title_fix_receipt["files"]:
        if not isinstance(raw, Mapping) or raw.get("path") not in dlc_entries:
            raise RuntimeError("DLC title-fix receipt contains an unsupported path")
        relative = str(raw["path"])
        if str(raw.get("prior_test_sha256", "")).upper() != target_hashes[relative]:
            raise RuntimeError(f"DLC title-fix predecessor differs: {relative}")
        target_hashes[relative] = str(raw.get("candidate_sha256", "")).upper()
    dlc_paths = tuple(sorted(dlc_entries))
    binary_paths = image_paths + dlc_paths
    all_paths = text_paths + binary_paths

    predecessors: dict[str, dict[str, object]] = {}
    targets: dict[str, dict[str, object]] = {}
    for relative in text_paths:
        predecessors[relative] = require_spec(
            pristine_root / Path(relative),
            V0140.pin_spec(V0140.PREDECESSORS[relative]),
            f"v0.14 pristine text {relative}",
        )
        targets[relative] = require_spec(
            game_root / Path(relative),
            V0140.pin_spec(V0140.TARGETS[relative]),
            f"v0.14 retained text target {relative}",
        )
    for relative in image_paths:
        source_pin = (
            PORT3_SOURCE
            if relative == PORT3_PATH
            else V0140.pin_spec(V0140.PREDECESSORS[relative])
        )
        predecessors[relative] = require_spec(
            pristine_root / Path(relative), source_pin, f"pristine image {relative}"
        )
        targets[relative] = require_spec(
            game_root / Path(relative), IMAGE_TARGETS[relative], f"reviewed image {relative}"
        )
    for relative in dlc_paths:
        entry = dlc_entries[relative]
        predecessors[relative] = require_spec(
            pristine_root / Path(relative),
            {
                "size": (pristine_root / Path(relative)).stat().st_size,
                "sha256": str(entry.get("original_sha256", "")).upper(),
            },
            f"pristine DLC {relative}",
        )
        targets[relative] = require_spec(
            game_root / Path(relative),
            {
                "size": (game_root / Path(relative)).stat().st_size,
                "sha256": target_hashes[relative],
            },
            f"translated DLC {relative}",
        )

    resource_kinds = {path: V0140.RESOURCE_KINDS[path] for path in text_paths}
    resource_kinds.update({path: "binary_bsdiff40" for path in binary_paths})
    return {
        "schema": "nobu16.kr.resource-profile.v0.15.0",
        "version": "v0.15.0",
        "text_resource_paths": list(text_paths),
        "binary_resource_paths": list(binary_paths),
        "optional_resource_paths": list(dlc_paths),
        "resource_kinds": resource_kinds,
        "expected_operation_counts": {
            path: V0140.EXPECTED_OPERATION_COUNTS[path] for path in text_paths
        },
        "predecessors": {path: predecessors[path] for path in all_paths},
        "targets": {path: targets[path] for path in all_paths},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pristine-root", type=Path, required=True)
    parser.add_argument("--game-root", type=Path, required=True)
    parser.add_argument("--dlc-receipt", type=Path, required=True)
    parser.add_argument("--dlc-title-fix-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    profile = build_profile(
        args.pristine_root,
        args.game_root,
        args.dlc_receipt,
        args.dlc_title_fix_receipt,
    )
    atomic_write(args.output.resolve(), canonical_json(profile))
    print(args.output.resolve())
    print(f"resources={len(profile['predecessors'])} binary={len(profile['binary_resource_paths'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
