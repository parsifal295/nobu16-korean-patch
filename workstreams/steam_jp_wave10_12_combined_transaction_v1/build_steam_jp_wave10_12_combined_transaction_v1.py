#!/usr/bin/env python3
"""Build the private Steam JP Wave 10--12 combined text transaction candidate.

This builder starts from the pinned full 11-file Steam Wave 9 profile.  It
rebuilds only the two ``msggame.bin`` resources, while copying the other nine
profile files byte-for-byte.  It is intentionally a candidate-only tool: it
has no Steam writer or game-launch capability.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
WAVE9_INPUT_ROOT = (
    REPO / "tmp" / "steam_jp_wave9_combined_transaction_v1" / "candidate-build-2"
)

WAVE10_SOURCE = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave10_candidate_v1"
    / "build_pc_dialogue_quality_wave10_candidate_v1.py"
)
WAVE11_SOURCE = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave11_candidate_v1"
    / "build_pc_dialogue_quality_wave11_candidate_v1.py"
)
WAVE12_SOURCE = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave12_candidate_v1"
    / "build_pc_dialogue_quality_wave12_candidate_v1.py"
)

SCHEMA = "nobu16.kr.steam-jp-wave10-12-combined-transaction.v1"
AUDIT_SCHEMA = "nobu16.kr.steam-jp-wave10-12-combined-transaction-audit.v1"
TRANSACTION_ID = "steam-jp-wave10-12-combined-transaction-v1"

PROFILE_PATHS = (
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
CHANGED_PATHS = ("MSG/JP/msggame.bin", "MSG_PK/JP/msggame.bin")
BASE_MSGGAME_PATH = CHANGED_PATHS[0]
PK_MSGGAME_PATH = CHANGED_PATHS[1]

# The exact Steam Wave 9 target profile is this transaction's only accepted
# input.  It intentionally includes all 11 files, not merely the two files to
# be written later by the separate PowerShell transaction writer.
INPUT_SHA256 = {
    "MSG/JP/ev_strdata.bin": "3A7BE17B7DA97B89BD82DFFF44EBC28DA2D3AA91D2E970A0F6C26DE22C657A22",
    "MSG/JP/msggame.bin": "7EB3F61CE008C02BA48C191CE95E162CD0BCA76CF3E1C45482FC6CE92E6E0492",
    "MSG/JP/strdata.bin": "10AB5E3BD9140B26EB7BC42DC5C352D4CE2905580C6A6112B13B37E12A358AFE",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    "MSG_PK/JP/msgdata.bin": "8B78403C339BEEE655B53A3F63699054DC6D9078640FE717885627E73B529752",
    "MSG_PK/JP/msgev.bin": "73DEC80A85B5441AFFFA725DAB72CF02D334D29B297AD08050BC496D532CB8F3",
    "MSG_PK/JP/msggame.bin": "209B96CADE84D82810A8A79CA362DFA1B6665A8C601D3DB2C3DC0F96986E9930",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}

# The PK value is a fixed hash derived by applying the three disjoint record
# contracts together to the Wave 9 input.  It is deliberately not any one
# component's stand-alone target hash.
PK_COMBINED_TARGET_SHA256 = "6557733B50CBA6435FB51EC71472FF4B06A321AF92F825EAA3C531DE7722E0A6"
TARGET_SHA256 = {
    **INPUT_SHA256,
    BASE_MSGGAME_PATH: "C74A5D2382D809FAF3EF6A78751872C6B99DAC15FCAB21CEA73E0C904736A347",
    PK_MSGGAME_PATH: PK_COMBINED_TARGET_SHA256,
}


class TransactionError(RuntimeError):
    """A pinned transaction contract or candidate output was violated."""


@dataclass(frozen=True)
class CandidatePayload:
    files: Mapping[str, bytes]
    input_sha256: Mapping[str, str]
    output_sha256: Mapping[str, str]
    audit: Mapping[str, Any]


_components: tuple[Any, Any, Any] | None = None


def require(condition: bool, message: str) -> None:
    if not condition:
        raise TransactionError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def coordinate_text(coordinate: tuple[int, int]) -> str:
    return f"{coordinate[0]}:{coordinate[1]}"


def require_under(path: Path, root: Path, label: str) -> Path:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise TransactionError(
            f"{label} escapes {resolved_root}: {resolved_path}"
        ) from exc
    return resolved_path


def require_tmp(path: Path, label: str) -> Path:
    return require_under(path, TMP_ROOT, label)


def relative_to_repo(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def load_component(module_name: str, source: Path) -> Any:
    if not source.is_file():
        raise TransactionError(f"component source is absent: {source}")
    spec = importlib.util.spec_from_file_location(module_name, source)
    if spec is None or spec.loader is None:
        raise TransactionError(f"cannot load component source: {source}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_components() -> tuple[Any, Any, Any]:
    global _components
    if _components is None:
        _components = (
            load_component("steam_w10_12_component_wave10", WAVE10_SOURCE),
            load_component("steam_w10_12_component_wave11", WAVE11_SOURCE),
            load_component("steam_w10_12_component_wave12", WAVE12_SOURCE),
        )
    return _components


def validate_component_contracts(wave10: Any, wave11: Any, wave12: Any) -> None:
    expected_pk_input = INPUT_SHA256[PK_MSGGAME_PATH]
    require(wave10.INPUT_SHA256 == expected_pk_input, "Wave 10 input is not Steam Wave 9 PK")
    require(wave11.INPUT_SHA256 == expected_pk_input, "Wave 11 input is not Steam Wave 9 PK")
    require(
        wave12.INPUT_SHA256[BASE_MSGGAME_PATH] == INPUT_SHA256[BASE_MSGGAME_PATH],
        "Wave 12 Base input is not Steam Wave 9",
    )
    require(
        wave12.INPUT_SHA256[PK_MSGGAME_PATH] == expected_pk_input,
        "Wave 12 PK input is not Steam Wave 9",
    )
    require(
        wave12.TARGET_SHA256[BASE_MSGGAME_PATH] == TARGET_SHA256[BASE_MSGGAME_PATH],
        "Wave 12 Base target hash contract differs",
    )
    require(len(wave10.PK_RECORD_IDS) == 12, "Wave 10 record-count contract differs")
    require(len(wave11.CHANGES) == 8, "Wave 11 record-count contract differs")


def validate_wave9_profile(input_root: Path) -> dict[str, bytes]:
    root = require_under(input_root, REPO / "tmp", "Wave 9 input root")
    if not root.is_dir():
        raise TransactionError(f"Wave 9 input root is absent: {root}")
    files: dict[str, bytes] = {}
    for relative in PROFILE_PATHS:
        path = root / Path(relative)
        if not path.is_file():
            raise TransactionError(f"Wave 9 input profile is missing {relative}")
        payload = path.read_bytes()
        actual = sha256_bytes(payload)
        if actual != INPUT_SHA256[relative]:
            raise TransactionError(
                f"Wave 9 input hash differs for {relative}: "
                f"expected {INPUT_SHA256[relative]}, got {actual}"
            )
        files[relative] = payload
    return files


def assert_disjoint_coordinate_sets(
    wave10_coordinates: set[tuple[int, int]],
    wave11_coordinates: set[tuple[int, int]],
    wave12_coordinates: set[tuple[int, int]],
) -> None:
    overlaps = {
        "wave10_wave11": sorted(wave10_coordinates & wave11_coordinates),
        "wave10_wave12": sorted(wave10_coordinates & wave12_coordinates),
        "wave11_wave12": sorted(wave11_coordinates & wave12_coordinates),
    }
    if any(overlaps.values()):
        rendered = {key: [coordinate_text(value) for value in values] for key, values in overlaps.items()}
        raise TransactionError(f"PK component record overlap is forbidden: {rendered}")


def changed_coordinates(input_packed: bytes, output_packed: bytes, parser: Any) -> set[tuple[int, int]]:
    before = parser(input_packed)
    after = parser(output_packed)
    if before.keys() != after.keys():
        raise TransactionError("msggame record topology changed")
    return {coordinate for coordinate in before if before[coordinate].data != after[coordinate].data}


def validate_union_output(
    input_packed: bytes,
    output_packed: bytes,
    expected_records: Mapping[tuple[int, int], Any],
    parser: Any,
    label: str,
) -> None:
    before = parser(input_packed)
    after = parser(output_packed)
    if before.keys() != after.keys():
        raise TransactionError(f"{label} changed msggame record topology")
    changed = {coordinate for coordinate in before if before[coordinate].data != after[coordinate].data}
    expected = set(expected_records)
    if changed != expected:
        raise TransactionError(
            f"{label} changed record scope differs: expected={sorted(expected)} actual={sorted(changed)}"
        )
    for coordinate, expected_record in expected_records.items():
        if after[coordinate].data != expected_record.data:
            raise TransactionError(f"{label} rebuilt record differs at {coordinate_text(coordinate)}")


def assert_output_profile(files: Mapping[str, bytes]) -> dict[str, str]:
    if tuple(files.keys()) != PROFILE_PATHS:
        raise TransactionError("candidate profile path order differs")
    hashes = {relative: sha256_bytes(files[relative]) for relative in PROFILE_PATHS}
    for relative in PROFILE_PATHS:
        expected = TARGET_SHA256[relative]
        if hashes[relative] != expected:
            raise TransactionError(
                f"candidate output hash differs for {relative}: "
                f"expected {expected}, got {hashes[relative]}"
            )
    return hashes


def prepare_candidate(input_root: Path) -> CandidatePayload:
    input_files = validate_wave9_profile(input_root)
    wave10, wave11, wave12 = load_components()
    validate_component_contracts(wave10, wave11, wave12)

    # Wave 12 alters one identical Base/PK record.  The Base output remains a
    # one-record change; the PK copy is placed into the later disjoint union.
    base_before = wave12.records_by_coordinate(input_files[BASE_MSGGAME_PATH])
    base_input_record = base_before.get(wave12.COORDINATE)
    if base_input_record is None:
        raise TransactionError(f"Base msggame lacks {coordinate_text(wave12.COORDINATE)}")
    wave12.validate_input_record(base_input_record, BASE_MSGGAME_PATH)
    base_output_record = wave12.rebuild_static_record(base_input_record, BASE_MSGGAME_PATH)
    base_output = wave12.rebuild_packed_msggame(
        input_files[BASE_MSGGAME_PATH], {wave12.COORDINATE: base_output_record.data}
    )
    wave12.validate_full_output(
        BASE_MSGGAME_PATH,
        input_files[BASE_MSGGAME_PATH],
        base_output,
        base_output_record,
    )
    require(
        sha256_bytes(base_output) == TARGET_SHA256[BASE_MSGGAME_PATH],
        "combined Base output differs from the pinned Wave 12 target",
    )

    pk_input = input_files[PK_MSGGAME_PATH]
    pk_before = wave10.records_by_coordinate(pk_input)
    wave10_coordinates = {(6, record_id) for record_id in wave10.PK_RECORD_IDS}
    wave11_coordinates = {change.record_coordinate for change in wave11.CHANGES}
    wave12_coordinates = {wave12.COORDINATE}
    assert_disjoint_coordinate_sets(wave10_coordinates, wave11_coordinates, wave12_coordinates)

    expected_pk_records: dict[tuple[int, int], Any] = {}
    replacements: dict[tuple[int, int], bytes] = {}
    for coordinate in sorted(wave10_coordinates):
        record = pk_before.get(coordinate)
        if record is None:
            raise TransactionError(f"PK msggame lacks Wave 10 {coordinate_text(coordinate)}")
        wave10.validate_input_record(record, coordinate)
        output_record = wave10.rebuild_static_record(record, coordinate)
        expected_pk_records[coordinate] = output_record
        replacements[coordinate] = output_record.data

    for change in wave11.CHANGES:
        coordinate = change.record_coordinate
        record = pk_before.get(coordinate)
        if record is None:
            raise TransactionError(f"PK msggame lacks Wave 11 {change.label}")
        wave11.validate_input_record(record, change)
        output_record = wave11.rebuild_change(record, change)
        expected_pk_records[coordinate] = output_record
        replacements[coordinate] = output_record.data

    pk_wave12_input_record = pk_before.get(wave12.COORDINATE)
    if pk_wave12_input_record is None:
        raise TransactionError(f"PK msggame lacks Wave 12 {coordinate_text(wave12.COORDINATE)}")
    wave12.validate_input_record(pk_wave12_input_record, PK_MSGGAME_PATH)
    pk_wave12_output_record = wave12.rebuild_static_record(
        pk_wave12_input_record, PK_MSGGAME_PATH
    )
    expected_pk_records[wave12.COORDINATE] = pk_wave12_output_record
    replacements[wave12.COORDINATE] = pk_wave12_output_record.data

    require(len(replacements) == 21, "PK combined record count must be 12 + 8 + 1")
    pk_output = wave10.rebuild_packed_msggame(pk_input, replacements)
    validate_union_output(
        pk_input,
        pk_output,
        expected_pk_records,
        wave10.records_by_coordinate,
        "PK combined",
    )
    pk_output_sha256 = sha256_bytes(pk_output)
    require(
        pk_output_sha256 == PK_COMBINED_TARGET_SHA256,
        "combined PK output differs from its pinned target hash: "
        f"expected {PK_COMBINED_TARGET_SHA256}, got {pk_output_sha256}",
    )

    output_files = dict(input_files)
    output_files[BASE_MSGGAME_PATH] = base_output
    output_files[PK_MSGGAME_PATH] = pk_output
    output_hashes = assert_output_profile(output_files)
    for relative in PROFILE_PATHS:
        if relative not in CHANGED_PATHS:
            require(
                output_files[relative] == input_files[relative],
                f"candidate changed an untouched profile file: {relative}",
            )

    audit = {
        "schema": AUDIT_SCHEMA,
        "transaction_id": TRANSACTION_ID,
        "source_free": True,
        "steam_write_capability": "absent",
        "game_launch_capability": "absent",
        "input_sha256": dict(INPUT_SHA256),
        "output_sha256": output_hashes,
        "profile_paths": list(PROFILE_PATHS),
        "changed_paths": list(CHANGED_PATHS),
        "scope": {
            "candidate_file_writes": list(CHANGED_PATHS),
            "excluded_asset_domains": ["RES_JP", "font", "HUD"],
            "full_profile_validation": True,
        },
        "components": {
            "wave10": {
                "physical_pk_records": len(wave10_coordinates),
                "coordinates": [coordinate_text(value) for value in sorted(wave10_coordinates)],
                "standalone_target_sha256": wave10.TARGET_SHA256,
            },
            "wave11": {
                "physical_pk_records": len(wave11_coordinates),
                "coordinates": [coordinate_text(value) for value in sorted(wave11_coordinates)],
                "standalone_target_sha256": wave11.TARGET_SHA256,
            },
            "wave12": {
                "physical_base_records": 1,
                "physical_pk_records": 1,
                "coordinate": coordinate_text(wave12.COORDINATE),
                "standalone_target_sha256": dict(wave12.TARGET_SHA256),
            },
        },
        "pk_record_overlap": {
            "required": 0,
            "actual": 0,
            "component_coordinate_counts": {
                "wave10": len(wave10_coordinates),
                "wave11": len(wave11_coordinates),
                "wave12": len(wave12_coordinates),
            },
            "combined_physical_records": len(replacements),
        },
        "record_contract": {
            "base_changed_coordinates": [coordinate_text(wave12.COORDINATE)],
            "pk_changed_coordinate_count": len(
                changed_coordinates(pk_input, pk_output, wave10.records_by_coordinate)
            ),
            "base_output_record_sha256": sha256_bytes(base_output_record.data),
            "pk_wave12_output_record_sha256": sha256_bytes(pk_wave12_output_record.data),
        },
    }
    return CandidatePayload(
        files=output_files,
        input_sha256=dict(INPUT_SHA256),
        output_sha256=output_hashes,
        audit=audit,
    )


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="wb", prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False
    ) as stream:
        temporary = Path(stream.name)
        stream.write(payload)
    try:
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def write_json(path: Path, value: Mapping[str, Any]) -> str:
    payload = canonical_json(value)
    atomic_write(path, payload)
    return sha256_bytes(payload)


def write_candidate(bundle: CandidatePayload, output_root: Path) -> None:
    root = require_tmp(output_root, "candidate output")
    if root.exists():
        raise TransactionError(f"refusing to overwrite candidate output: {root}")
    for relative in PROFILE_PATHS:
        destination = root / Path(relative)
        atomic_write(destination, bundle.files[relative])
        actual = sha256_path(destination)
        if actual != bundle.output_sha256[relative]:
            raise TransactionError(f"written candidate hash differs for {relative}")


def build_manifest(bundle: CandidatePayload, audit_sha256: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "transaction_id": TRANSACTION_ID,
        "candidate_only_builder": True,
        "steam_write_capability": "absent",
        "steam_apply_command": None,
        "game_launch_capability": "absent",
        "profile_paths": list(PROFILE_PATHS),
        "changed_paths": list(CHANGED_PATHS),
        "input_sha256": dict(bundle.input_sha256),
        "output_sha256": dict(bundle.output_sha256),
        "pinned_output_sha256": dict(TARGET_SHA256),
        "audit_schema": AUDIT_SCHEMA,
        "audit_sha256": audit_sha256,
        "scope": {
            "writer_paths": list(CHANGED_PATHS),
            "excluded_asset_domains": ["RES_JP", "font", "HUD"],
            "full_profile_pre_post_validation": True,
        },
        "component_contract": {
            "wave10_pk_records": 12,
            "wave11_pk_records": 8,
            "wave12_base_records": 1,
            "wave12_pk_records": 1,
            "pk_record_overlap": 0,
            "pk_combined_target_sha256": PK_COMBINED_TARGET_SHA256,
        },
    }


def print_json(value: Mapping[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def command_verify(args: argparse.Namespace) -> int:
    bundle = prepare_candidate(args.input_root)
    print_json(
        {
            "status": "ok",
            "input_root": relative_to_repo(args.input_root),
            "profile_files": len(PROFILE_PATHS),
            "changed_paths": list(CHANGED_PATHS),
            "output_sha256": dict(bundle.output_sha256),
            "steam_write_capability": "absent",
        }
    )
    return 0


def command_build(args: argparse.Namespace) -> int:
    output_root = require_tmp(args.output_root, "candidate output")
    audit_path = require_tmp(args.audit_path, "audit output")
    manifest_path = require_tmp(args.manifest, "manifest output")
    bundle = prepare_candidate(args.input_root)
    write_candidate(bundle, output_root)
    audit_sha256 = write_json(audit_path, bundle.audit)
    manifest_sha256 = write_json(manifest_path, build_manifest(bundle, audit_sha256))
    print_json(
        {
            "status": "ok",
            "candidate": relative_to_repo(output_root),
            "audit": relative_to_repo(audit_path),
            "manifest": relative_to_repo(manifest_path),
            "audit_sha256": audit_sha256,
            "manifest_sha256": manifest_sha256,
            "output_sha256": dict(bundle.output_sha256),
            "steam_write_capability": "absent",
        }
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    verify = subparsers.add_parser("verify", help="validate the in-memory combined candidate")
    verify.add_argument("--input-root", type=Path, default=WAVE9_INPUT_ROOT)
    verify.set_defaults(func=command_verify)
    build = subparsers.add_parser("build", help="write a private candidate, audit, and manifest")
    build.add_argument("--input-root", type=Path, default=WAVE9_INPUT_ROOT)
    build.add_argument("--output-root", type=Path, default=TMP_ROOT / "candidate-build-1")
    build.add_argument("--audit-path", type=Path, default=TMP_ROOT / "audit.v1.json")
    build.add_argument("--manifest", type=Path, default=TMP_ROOT / "build_manifest.v1.json")
    build.set_defaults(func=command_build)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except TransactionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
