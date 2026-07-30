#!/usr/bin/env python3
"""Merge the verified female-name fixes into the pinned current Steam files.

This deployment entry point is intentionally separate from the v3 preparation
builder.  The installed JP tables contain later changes and different string
counts, so the prepared historical-baseline files must never be copied over
them.  Only the reviewed component rows and three required female direct-name
rows are merged; every other installed string is preserved.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Sequence


HERE = Path(__file__).resolve().parent


class DeploymentError(ValueError):
    """Raised when a deployment input or safety invariant differs."""


def load_v3() -> Any:
    path = HERE / "build_msgdata_female_officer_components_v3_complete.py"
    spec = importlib.util.spec_from_file_location("female_component_build_v3", path)
    if spec is None or spec.loader is None:
        raise DeploymentError("cannot load the v3 component builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V3 = load_v3()
V1 = V3.V1
MSGDATA_RESOURCE = Path("MSG_PK") / "JP" / "msgdata.bin"
MSGEV_RESOURCE = Path("MSG_PK") / "JP" / "msgev.bin"
REPORT_SCHEMA = "nobu16.kr.female-officer-name-steam-merge.v3"

CURRENT_CONTRACTS = {
    MSGDATA_RESOURCE: {
        "packed_size": 492_035,
        "packed_sha256": "5E641636C9D5BCD074CDD6B9D04DF5EF60487333835425157843389AC13DEA0C",
        "raw_size": 490_088,
        "raw_sha256": "465E8B8D5A3A06909B40E998474FBAA88F713C98666052FD4E8FDD78461F8D6F",
        "string_count": 29_210,
    },
    MSGEV_RESOURCE: {
        "packed_size": 1_045_618,
        "packed_sha256": "6B8228C0A0FDDF9C4C50C167C63282EF8AE28496F3CEEF4D56E2C71B9F29430A",
        "raw_size": 1_041_508,
        "raw_sha256": "7003072AA7A31AB321F4E39120B6021494A429542842F33BE207E27904882681",
        "string_count": 17_910,
    },
}

MSGEV_PATCHES: tuple[dict[str, Any], ...] = (
    {
        "id": 745,
        "baseline_ko_utf16le_sha256": "0A5E3264EFEC61F93750BEB639D6DD0E611307E1A119BFB250C3B5E3AF8B1FE7",
        "ko": "기쓰노",
        "ko_utf16le_sha256": "E8BE0EEF772F2857C74DA8C4C854179CA6E246AECFED867D8A33793244AB782F",
    },
    {
        "id": 843,
        "baseline_ko_utf16le_sha256": "8FF1D0A8596902C3CA9F25335E5C9BDC3FFB608CB0932729B0B35881C0BBB359",
        "ko": "고마쓰",
        "ko_utf16le_sha256": "F7B78B61998EA3D95E2C39B88534659CAED277C3B635E67F021DB2D92D5B1D4F",
    },
    {
        "id": 1861,
        "baseline_ko_utf16le_sha256": "3432615CF8CD923D2CC3463D6F43F3ECD3B09190E1D8C5863F290128D6FF1EC7",
        "ko": "마쓰히메",
        "ko_utf16le_sha256": "E6F62D968241DFCF4F1309288A638671697717E2EBDD1F03AA46F2F0C5CAE691",
    },
)


def parse_pinned(path: Path, contract: dict[str, Any]) -> tuple[bytes, bytes, Any]:
    packed = path.read_bytes()
    if len(packed) != contract["packed_size"] or V1.sha256_bytes(packed) != contract["packed_sha256"]:
        raise DeploymentError(f"installed baseline differs: {path}")
    header, raw = V1.decompress_wrapper(packed)
    if len(raw) != contract["raw_size"] or V1.sha256_bytes(raw) != contract["raw_sha256"]:
        raise DeploymentError(f"installed raw baseline differs: {path}")
    table = V1.parse_message_table(raw)
    if table.string_count != contract["string_count"]:
        raise DeploymentError(f"installed string count differs: {path}")
    if V1.rebuild_message_table(table, table.texts) != raw:
        raise DeploymentError(f"installed parse/rebuild is not byte-identical: {path}")
    if header.prefix != packed[:8]:
        raise DeploymentError(f"installed wrapper prefix differs: {path}")
    return packed, raw, table


def rebuild_file(
    packed: bytes,
    raw: bytes,
    table: Any,
    patches: Sequence[dict[str, Any]],
    allow_already_target: bool,
) -> tuple[bytes, dict[str, Any]]:
    updated = list(table.texts)
    changed_ids: list[int] = []
    already_target_ids: list[int] = []
    for patch in patches:
        row_id = patch["id"]
        if not 0 <= row_id < len(updated):
            raise DeploymentError(f"patch ID is outside the installed table: {row_id}")
        if V1.text_hash(patch["ko"]) != patch["ko_utf16le_sha256"]:
            raise DeploymentError(f"replacement hash differs at ID {row_id}")
        if updated[row_id] == patch["ko"] and allow_already_target:
            already_target_ids.append(row_id)
            continue
        if V1.text_hash(updated[row_id]) != patch["baseline_ko_utf16le_sha256"]:
            raise DeploymentError(f"installed row baseline differs at ID {row_id}")
        updated[row_id] = patch["ko"]
        changed_ids.append(row_id)

    changed_set = set(changed_ids)
    if any(
        table.texts[index] != updated[index]
        for index in range(len(updated))
        if index not in changed_set
    ):
        raise DeploymentError("a non-target installed string changed in memory")
    rebuilt_raw = V1.rebuild_message_table(table, updated)
    rebuilt_table = V1.parse_message_table(rebuilt_raw)
    if rebuilt_table.texts != tuple(updated):
        raise DeploymentError("rebuilt installed table did not round-trip")
    candidate = V1.recompress_wrapper(rebuilt_raw, packed)
    header, candidate_raw = V1.decompress_wrapper(candidate)
    if candidate_raw != rebuilt_raw or header.prefix != packed[:8]:
        raise DeploymentError("rebuilt installed wrapper verification failed")
    return candidate, {
        "source_packed_size": len(packed),
        "source_packed_sha256": V1.sha256_bytes(packed),
        "candidate_packed_size": len(candidate),
        "candidate_packed_sha256": V1.sha256_bytes(candidate),
        "candidate_raw_size": len(rebuilt_raw),
        "candidate_raw_sha256": V1.sha256_bytes(rebuilt_raw),
        "string_count": rebuilt_table.string_count,
        "changed_ids": changed_ids,
        "already_target_ids": already_target_ids,
        "non_target_texts_preserved": True,
        "candidate_roundtrip": True,
    }


def build_merge(game_root: Path) -> tuple[dict[Path, bytes], dict[Path, bytes], dict[str, Any]]:
    originals: dict[Path, bytes] = {}
    candidates: dict[Path, bytes] = {}
    file_reports: dict[str, Any] = {}
    for resource, patches, allow_already in (
        (MSGDATA_RESOURCE, V3.all_patches(), True),
        (MSGEV_RESOURCE, MSGEV_PATCHES, False),
    ):
        source_path = game_root / resource
        packed, raw, table = parse_pinned(source_path, CURRENT_CONTRACTS[resource])
        candidate, report = rebuild_file(packed, raw, table, patches, allow_already)
        if source_path.read_bytes() != packed:
            raise DeploymentError(f"installed input changed during merge build: {resource}")
        originals[resource] = packed
        candidates[resource] = candidate
        file_reports[resource.as_posix()] = report
    report = {
        "schema": REPORT_SCHEMA,
        "game_root": str(game_root),
        "files": file_reports,
        "verification": {
            "msgdata_current_state_preserved_except_reviewed_components": True,
            "msgev_current_state_preserved_except_three_required_names": True,
            "all_candidates_roundtrip": True,
            "installed_files_modified_during_build": False,
        },
    }
    return originals, candidates, report


def ensure_outside_game_root(path: Path, game_root: Path) -> None:
    try:
        path.resolve().relative_to(game_root.resolve())
    except ValueError:
        return
    raise DeploymentError("staging and backup roots must be outside the game installation")


def write_staging(output_root: Path, candidates: dict[Path, bytes], report: dict[str, Any]) -> None:
    for resource, candidate in candidates.items():
        V1.atomic_write(output_root / resource, candidate)
    V1.atomic_write(output_root / "steam_merge.build-report.v3.json", V1.pretty_json(report))


def cmd_build(args: argparse.Namespace) -> int:
    game_root = args.game_root.resolve()
    output_root = args.output_root.resolve()
    ensure_outside_game_root(output_root, game_root)
    _originals, candidates, report = build_merge(game_root)
    write_staging(output_root, candidates, report)
    print(f"output_root={output_root}")
    print("msgdata_changed=" + str(len(report["files"][MSGDATA_RESOURCE.as_posix()]["changed_ids"])))
    print("msgdata_already_target=" + json.dumps(report["files"][MSGDATA_RESOURCE.as_posix()]["already_target_ids"]))
    print("msgev_changed=" + str(len(report["files"][MSGEV_RESOURCE.as_posix()]["changed_ids"])))
    print("installed_files_modified=False")
    return 0


def cmd_deploy(args: argparse.Namespace) -> int:
    game_root = args.game_root.resolve()
    staging_root = args.staging_root.resolve()
    backup_root = args.backup_root.resolve()
    ensure_outside_game_root(staging_root, game_root)
    ensure_outside_game_root(backup_root, game_root)
    if backup_root.exists() and any(backup_root.iterdir()):
        raise DeploymentError("backup root is not empty")

    originals, candidates, report = build_merge(game_root)
    for resource, candidate in candidates.items():
        staged = (staging_root / resource).read_bytes()
        if staged != candidate:
            raise DeploymentError(f"staged candidate differs from current verified merge: {resource}")

    for resource, original in originals.items():
        V1.atomic_write(backup_root / resource, original)
        if (backup_root / resource).read_bytes() != original:
            raise DeploymentError(f"backup verification failed: {resource}")
    backup_manifest = {
        "schema": REPORT_SCHEMA + ".backup",
        "game_root": str(game_root),
        "files": {
            resource.as_posix(): {
                "packed_size": len(original),
                "packed_sha256": V1.sha256_bytes(original),
            }
            for resource, original in originals.items()
        },
    }
    V1.atomic_write(backup_root / "backup-manifest.v3.json", V1.pretty_json(backup_manifest))

    try:
        for resource in (MSGDATA_RESOURCE, MSGEV_RESOURCE):
            V1.atomic_write(game_root / resource, candidates[resource])
    except Exception:
        for resource, original in originals.items():
            V1.atomic_write(game_root / resource, original)
        raise

    for resource, candidate in candidates.items():
        installed = (game_root / resource).read_bytes()
        if installed != candidate:
            for rollback_resource, original in originals.items():
                V1.atomic_write(game_root / rollback_resource, original)
            raise DeploymentError(f"post-deployment verification failed and rollback completed: {resource}")

    report["backup_root"] = str(backup_root)
    report["verification"]["installed_files_modified_during_build"] = False
    report["deployment"] = {
        "status": "APPLIED",
        "atomic_replace_per_file": True,
        "backup_verified_before_replace": True,
        "post_deployment_byte_verification": True,
        "rollback_required": False,
    }
    V1.atomic_write(staging_root / "steam_merge.deployment-report.v3.json", V1.pretty_json(report))
    print(f"game_root={game_root}")
    print(f"backup_root={backup_root}")
    print("deployment=APPLIED")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build")
    build.add_argument("--game-root", type=Path, required=True)
    build.add_argument("--output-root", type=Path, required=True)
    build.set_defaults(func=cmd_build)
    deploy = commands.add_parser("deploy")
    deploy.add_argument("--game-root", type=Path, required=True)
    deploy.add_argument("--staging-root", type=Path, required=True)
    deploy.add_argument("--backup-root", type=Path, required=True)
    deploy.set_defaults(func=cmd_deploy)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError, DeploymentError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
