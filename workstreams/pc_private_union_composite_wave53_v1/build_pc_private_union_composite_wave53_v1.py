#!/usr/bin/env python3
"""Rebuild the Wave 53 private union from the pinned W45 private baseline.

Only record-level differences from four pinned private candidates are merged.
This module neither reads a game installation nor copies a component packed
file wholesale.  Its only mutable destination is this workstream's private
``tmp/.../candidate`` directory.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
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
PRIVATE_TMP_ROOT = REPO / "tmp"
TOOLS = REPO / "tools"

BASE_MSGGAME = "MSG/JP/msggame.bin"
PK_MSGGAME = "MSG_PK/JP/msggame.bin"
PK_MSGDATA = "MSG_PK/JP/msgdata.bin"
PK_EVENT = "MSG_PK/JP/msgev.bin"
RESOURCE_ORDER = (BASE_MSGGAME, PK_MSGGAME, PK_MSGDATA, PK_EVENT)
MSGGAME_RESOURCES = frozenset((BASE_MSGGAME, PK_MSGGAME))

W45_WORKSTREAM = "pc_text_quality_wave45_safe_static_transaction_envelope_v1"
W45_BASELINE_ROOT = PRIVATE_TMP_ROOT / W45_WORKSTREAM / "candidate"
W45_AUDIT_PATH = PRIVATE_TMP_ROOT / W45_WORKSTREAM / "audit.v1.json"
W45_BUILDER = (
    REPO
    / "workstreams"
    / W45_WORKSTREAM
    / "build_pc_text_quality_wave45_safe_static_transaction_envelope_v1.py"
)
W45_BUILDER_SHA256 = "061872D8E9AB30B2D114FB0E76F60F71EDCC018EAE954BEDA2846CECAA6514C9"
W45_AUDIT_SHA256 = "A17FFD2D75290E962F752C2528B4F29077378356BB96EE7FE67A326C72F63EE5"
W45_AUDIT_SCHEMA = "nobu16.kr.pc-text-quality-wave45-safe-static-transaction-envelope-audit.v1"
W45_COMPONENT_BUILDERS = {
    "wave42": "7E95C231B4B0E39FEA2F59D2682E25FD76FC805B6B0B78C8E443829A2C7075A3",
    "wave44": "2360AC8B741CBF3D407F8E7D8215A4998B10529A7E62656D003E85228414C3F2",
}

W27_HELPER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave27_static_quality_v1"
    / "build_pc_dialogue_quality_wave27_static_quality_v1.py"
)
W27_HELPER_SHA256 = "D63EA16EECF77F769C3B4AE21579A6C1227531E7FBDD0C07BB83C3E2B3A41438"
LZ4_HELPER = TOOLS / "nobu16_lz4.py"
LZ4_HELPER_SHA256 = "96E7E934355F1B7B1764FAFA1B2809BA7D165E4ADA1DE16EA15C089790E77CFB"
TABLE_HELPER = TOOLS / "nobu16_msg_table.py"
TABLE_HELPER_SHA256 = "A4C30F57ACC67393768682ED2EDD084C3A0ACB017E29E2C0A5021E821B81E12A"


class CompositeError(RuntimeError):
    """Raised when a baseline, component, or private output drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CompositeError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def require_below(path: Path, root: Path, label: str, *, strict: bool) -> Path:
    resolved = path.resolve(strict=strict)
    boundary = root.resolve(strict=strict)
    try:
        resolved.relative_to(boundary)
    except ValueError as exc:
        raise CompositeError(f"{label} escapes its private root: {resolved}") from exc
    return resolved


def require_private_source(path: Path, label: str) -> Path:
    return require_below(path, PRIVATE_TMP_ROOT, label, strict=True)


def require_private_output(path: Path, label: str) -> Path:
    return require_below(path, TMP_ROOT, label, strict=False)


@dataclass(frozen=True)
class Profile:
    size: int
    sha256: str
    raw_size: int
    raw_sha256: str


def packed_profile_dict(profile: Profile) -> dict[str, Any]:
    return {"size": profile.size, "sha256": profile.sha256}


def profile_dict(profile: Profile) -> dict[str, Any]:
    return {
        "size": profile.size,
        "sha256": profile.sha256,
        "raw_size": profile.raw_size,
        "raw_sha256": profile.raw_sha256,
    }


# Full packed/raw profiles of the private W45 baseline used by every component.
W45_PROFILES: Mapping[str, Profile] = {
    BASE_MSGGAME: Profile(
        1_504_410,
        "F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB",
        1_498_508,
        "27F2021CED9D7E36B89025EACCF3449D5E424EE5C38C758E5E0995C8234EEB6D",
    ),
    PK_MSGGAME: Profile(
        1_806_538,
        "0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092",
        1_799_456,
        "737DAEAB7CC9257BC0F9E15523D01A0C3E807912B8D44393F75512BFB4C2A11E",
    ),
    PK_MSGDATA: Profile(
        496_991,
        "8282F12A667E11F54054856035415C7297385ADD16EC261BD952BEBB8658952A",
        495_024,
        "2D38396C29F7548A1C12691877FE9F3D5D4B2C27647D521CFEC975017977C077",
    ),
    PK_EVENT: Profile(
        994_739,
        "01287E2ECC5328C85348657EFF06553353CB8664B0FB7E1669DB9FC591D53EBE",
        990_828,
        "F3716AB98D60931CEC0FE61976D8DAD386C05B30B7167BD1BDB2CDF02EC55ACC",
    ),
}

# Pins for the deterministic record-only rebuild, fixed before writing.
UNION_TARGET_PROFILES: Mapping[str, Profile] = {
    BASE_MSGGAME: Profile(
        1_504_462,
        "50E78AE5BE920454EC8F4B20A485FEF2A1237F593EBF97D205799A2AD705E2B8",
        1_498_560,
        "8B14B76B1A3479C6261D4E2D8C8FD65877B4A3783EC8AF778C9F2B49679D3706",
    ),
    PK_MSGGAME: Profile(
        1_806_414,
        "E470EA330510C571E7B142211C27C49E4E4508C1026FEA6BBC55F07675B71FD7",
        1_799_332,
        "AC952E65D578F6E6DE554229B4A48AFF44703B81CD1810C0362EB4662D3B2673",
    ),
    PK_MSGDATA: Profile(
        496_999,
        "34DAAAC9F8AE22445DD580FB5B8182FA9C6CD66C4DA78498E6B20286C5456215",
        495_032,
        "9FB501A16D7DF7D84559612A68775D75B6C1E6C0B853123194B81B7FBA8C7BDC",
    ),
    PK_EVENT: Profile(
        994_763,
        "E088299D725472827D32B3F16541DD49663C5CD80FA8CA4FF3E5C9BCBCD0B2AF",
        990_852,
        "6B313D7EA8AA86DA1E0AE25BFDC6DFEDBA6085EF465959F27E70475D0DB4F620",
    ),
}

UNION_COUNTS = {
    BASE_MSGGAME: 67,
    PK_MSGGAME: 166,
    PK_MSGDATA: 4,
    PK_EVENT: 52,
}
UNION_TOTAL_COUNT = sum(UNION_COUNTS.values())


@dataclass(frozen=True)
class ComponentSpec:
    name: str
    workstream: str
    builder_filename: str
    builder_sha256: str
    candidate_manifest_sha256: str
    component_audit_sha256: str
    manifest_schema: str
    audit_schema: str
    layout: str
    expected_count: int
    resource_outputs: Mapping[str, Profile]
    resource_counts: Mapping[str, int]

    @property
    def builder_path(self) -> Path:
        return REPO / "workstreams" / self.workstream / self.builder_filename

    @property
    def candidate_root(self) -> Path:
        return PRIVATE_TMP_ROOT / self.workstream / "candidate"


COMPONENT_SPECS = (
    ComponentSpec(
        "wave52_static_composite",
        "pc_static_composite_wave52_v1",
        "build_pc_static_composite_wave52_v1.py",
        "4A739CDE0E7A24B44F215E0BFBC9B156A8015B50A76690F845CA9795E00B7AC2",
        "40836B956F26F23BA8DCD80CA0F95F64007EBBF4B0821FD223592A1D8C63440F",
        "103A69289649D73151667637FD193C3E0AC02E33E911F56B176751DAEB9E7FE3",
        "nobu16.kr.pc-static-composite-wave52-manifest.v1",
        "nobu16.kr.pc-static-composite-wave52-audit.v1",
        "wave52",
        249,
        {
            BASE_MSGGAME: Profile(1_504_462, "367FBCD48FA824955508747A49FD4424798262C3BE75D7A67A10D859CB46B319", 1_498_560, "54F18AB680E94783E3A8D24D982236AC0FCC7D39DE76C4C9DBFA993A4CB92F35"),
            PK_MSGGAME: Profile(1_806_438, "8864670A0CFB2E55C031E0A72C64FAD19D172A556123082E9E75223BD07DC106", 1_799_356, "CDA0FD14D0C84AE7ACA81A74A1E51951274AD9ADDD6E6C755F645F17FDBD02F6"),
            PK_EVENT: Profile(994_751, "AC9C0F7FE72ADA6FA4604C1359A3FFA155BB5C166A590C3FC77BAD7C390CC90B", 990_840, "F43E2742C8D9CDAA59861C5FC9011C68C3807641D97AFDAF46AFE2521BB9AA86"),
        },
        {BASE_MSGGAME: 59, PK_MSGGAME: 157, PK_EVENT: 33},
    ),
    ComponentSpec(
        "block15_runtime_apply_rows",
        "pc_block15_runtime_candidate_v1",
        "build_pc_block15_runtime_candidate_v1.py",
        "3948D2836C7ADA29FFD7C9187FD8C82C1B2FEC19A2B2BC591284806AD06304AA",
        "D7B7921645FB778C8B83CFABDB80A37EB2627ADECB090F5D59B98004D0A031BB",
        "DAAB619C9F3F2C0FF740DAB01F3A4F5881C4921885C7C4FB5740CD2F1D8EB65C",
        "nobu16.kr.pc-block15-runtime-candidate-manifest.v1",
        "nobu16.kr.pc-block15-runtime-candidate-audit.v1",
        "block15",
        17,
        {
            BASE_MSGGAME: Profile(1_504_410, "94125746E07A8235ECF0636CDC803BADD3D3552C0617347CC7762AB742DB4C3B", 1_498_508, "0AE069E9FF45C783A9107D84D82F501C2FFA06B0D7AFAA1B218116D3786AF734"),
            PK_MSGGAME: Profile(1_806_514, "68AAB9E828B574E5E805BC7D054284E16328D4BDF5FA41A44CAE4F29E953A667", 1_799_432, "5797EC4CDDF523766FBF12585D6DD86E4C39DA79F55648D12AE0C45EF023C844"),
        },
        {BASE_MSGGAME: 8, PK_MSGGAME: 9},
    ),
    ComponentSpec(
        "npc_name_quality_wave50",
        "pc_npc_name_quality_wave50_v1",
        "build_pc_npc_name_quality_wave50_v1.py",
        "C94804B668350FE43AEC198128FEE2F1D832A9D9A2FB9E0BA29D7875FC2A88EE",
        "C300BC56D20BAD9AD80719B238BA186018FAFD093338F3CB5A9496078DE53533",
        "AF8BF382C6259FD6E3B6D65EE777DD287B55A6A06E297B48A5F106BF0D4BF80E",
        "nobu16.kr.pc-npc-name-quality-wave50-manifest.v1",
        "nobu16.kr.pc-npc-name-quality-wave50-audit.v1",
        "npc",
        16,
        {
            PK_MSGDATA: Profile(496_999, "34DAAAC9F8AE22445DD580FB5B8182FA9C6CD66C4DA78498E6B20286C5456215", 495_032, "9FB501A16D7DF7D84559612A68775D75B6C1E6C0B853123194B81B7FBA8C7BDC"),
            PK_EVENT: Profile(994_751, "F2E5D6F7399CE2B1260984D4CF7AD251FC64D3D9A0279D9E26374BCEAC6EC8AE", 990_840, "04ABDB2305F4B415B6D218370C73E5037C98BEBB0D359FAEBF4D0B91D03AC6FA"),
        },
        {PK_MSGDATA: 4, PK_EVENT: 12},
    ),
    ComponentSpec(
        "event_color_tag_reflow",
        "pc_event_color_tag_reflow_v1",
        "build_pc_event_color_tag_reflow_v1.py",
        "FD745439BB03622C6EFA357F31AB4F3FC108AFCA9E73B4B1A2699EEBCD0AD9DB",
        "EBE2984823532521313C52AA8C24D4E93F8FDAD807CAF527C0406D55C2718397",
        "A8D518D7FA9D2B4415655AC0ABA4484348DEEAE387EB781E2B247900C66537B9",
        "nobu16.kr.pc-event-color-tag-reflow-manifest.v1",
        "nobu16.kr.pc-event-color-tag-reflow-audit.v1",
        "reflow",
        7,
        {
            PK_EVENT: Profile(994_743, "AC1398EA909295AFA966D29E98F49F4F1B6C65D0BA870A51024721F91AB30D79", 990_832, "1A65DB1B7206B98D5A2600261064862A2E49DE52409DEB18EB4D07B955F25EC9"),
        },
        {PK_EVENT: 7},
    ),
)

# These are forbidden from the union even if a component artifact drifts.
EXCLUDED_HOLDS: Mapping[str, tuple[Any, ...]] = {
    BASE_MSGGAME: ((15, 1121),),
    PK_MSGGAME: (),
    PK_MSGDATA: (),
    PK_EVENT: (3202, 3900, 3934, 3956, 4140, 8510, 8723, 9359, 10045),
}


require(sha256_path(LZ4_HELPER) == LZ4_HELPER_SHA256, "LZ4 helper hash differs")
require(sha256_path(TABLE_HELPER) == TABLE_HELPER_SHA256, "message-table helper hash differs")
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


def load_w27() -> Any:
    require(W27_HELPER.is_file(), "Wave 27 MSGGAME helper is absent")
    require(sha256_path(W27_HELPER) == W27_HELPER_SHA256, "Wave 27 MSGGAME helper hash differs")
    spec = importlib.util.spec_from_file_location("wave53_pinned_wave27", W27_HELPER)
    if spec is None or spec.loader is None:  # pragma: no cover - import guard
        raise CompositeError("cannot load Wave 27 MSGGAME helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W27 = load_w27()


@dataclass(frozen=True)
class MsgGameBaseline:
    packed: bytes
    raw: bytes
    records: Mapping[tuple[int, int], Any]


@dataclass(frozen=True)
class TableBaseline:
    packed: bytes
    header: Any
    raw: bytes
    table: Any


@dataclass(frozen=True)
class ResourceMetadata:
    manifest_input: Mapping[str, Any]
    manifest_output: Mapping[str, Any]
    audit_input: Mapping[str, Any]
    audit_output: Mapping[str, Any]
    declared_coordinates: tuple[Any, ...]


@dataclass(frozen=True)
class ComponentBinding:
    name: str
    workstream: str
    candidate_root: str
    builder_sha256: str
    candidate_manifest_sha256: str
    component_audit_sha256: str
    changed_record_count: int
    changed_coordinates: Mapping[str, tuple[Any, ...]]
    held_coordinates: Mapping[str, tuple[Any, ...]]


@dataclass(frozen=True)
class CandidateBundle:
    files: Mapping[str, bytes]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]
    union_coordinates: Mapping[str, tuple[Any, ...]]
    held_coordinates: Mapping[str, tuple[Any, ...]]
    components: tuple[ComponentBinding, ...]


def inspect_packed(payload: bytes, label: str) -> tuple[Any, bytes, Profile]:
    try:
        header, raw = decompress_wrapper(payload)
    except Exception as exc:  # pragma: no cover - helper-specific exception
        raise CompositeError(f"cannot decompress {label}") from exc
    return header, raw, Profile(len(payload), sha256_bytes(payload), len(raw), sha256_bytes(raw))


def require_profile(payload: bytes, expected: Profile, label: str) -> tuple[Any, bytes]:
    header, raw, actual = inspect_packed(payload, label)
    require(actual == expected, f"{label} profile differs")
    return header, raw


def require_profile_metadata(value: Any, expected: Profile, label: str, *, require_raw: bool) -> None:
    require(isinstance(value, Mapping), f"{label} profile metadata is not an object")
    require(value.get("size") == expected.size, f"{label} packed size differs")
    require(value.get("sha256") == expected.sha256, f"{label} packed SHA-256 differs")
    if require_raw:
        require(value.get("raw_size") == expected.raw_size, f"{label} raw size differs")
        require(value.get("raw_sha256") == expected.raw_sha256, f"{label} raw SHA-256 differs")
    elif "raw_size" in value or "raw_sha256" in value:
        require(value.get("raw_size") == expected.raw_size, f"{label} optional raw size differs")
        require(value.get("raw_sha256") == expected.raw_sha256, f"{label} optional raw SHA-256 differs")


def parse_msggame_coordinate(value: Any, label: str) -> tuple[int, int]:
    require(isinstance(value, str) and value.count(":") == 1, f"invalid MSGGAME coordinate: {label}")
    block, record = value.split(":")
    try:
        coordinate = (int(block), int(record))
    except ValueError as exc:
        raise CompositeError(f"invalid MSGGAME coordinate: {label}") from exc
    require(coordinate[0] >= 0 and coordinate[1] >= 0, f"negative MSGGAME coordinate: {label}")
    return coordinate


def parse_msggame_slot(value: Any, label: str) -> tuple[int, int]:
    require(isinstance(value, str) and value.count(":") == 2, f"invalid MSGGAME slot: {label}")
    block, record, literal = value.split(":")
    try:
        coordinate = (int(block), int(record))
        literal_index = int(literal)
    except ValueError as exc:
        raise CompositeError(f"invalid MSGGAME slot: {label}") from exc
    require(coordinate[0] >= 0 and coordinate[1] >= 0 and literal_index >= 0, f"negative MSGGAME slot: {label}")
    return coordinate


def coordinate_text(resource: str, coordinate: Any) -> str | int:
    if resource in MSGGAME_RESOURCES:
        return f"{coordinate[0]}:{coordinate[1]}"
    return int(coordinate)


def normalize_declared_coordinates(resource: str, values: Any, label: str, *, slots: bool = False) -> tuple[Any, ...]:
    require(isinstance(values, list), f"{label} coordinate list is absent")
    if resource in MSGGAME_RESOURCES:
        normalized = tuple(parse_msggame_slot(value, label) if slots else parse_msggame_coordinate(value, label) for value in values)
    else:
        try:
            normalized = tuple(int(value) for value in values)
        except (TypeError, ValueError) as exc:
            raise CompositeError(f"invalid table ID in {label}") from exc
        require(all(value >= 0 for value in normalized), f"{label} contains a negative table ID")
    require(len(set(normalized)) == len(normalized), f"{label} contains duplicate coordinates")
    return tuple(sorted(normalized))


def load_json(path: Path, label: str) -> tuple[bytes, Mapping[str, Any]]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CompositeError(f"{label} is invalid") from exc
    require(isinstance(value, Mapping), f"{label} is not an object")
    return raw, value


def load_w45_baselines() -> tuple[Mapping[str, MsgGameBaseline], Mapping[str, TableBaseline], Mapping[str, Any]]:
    root = require_private_source(W45_BASELINE_ROOT, "W45 private baseline")
    audit_path = require_private_source(W45_AUDIT_PATH, "W45 audit")
    require(sha256_path(W45_BUILDER) == W45_BUILDER_SHA256, "W45 builder hash differs")
    audit_bytes, audit = load_json(audit_path, "W45 audit")
    require(sha256_bytes(audit_bytes) == W45_AUDIT_SHA256, "W45 audit hash differs")
    require(sha256_bytes(canonical_json(audit)) == W45_AUDIT_SHA256, "W45 audit canonical hash differs")
    require(audit.get("schema") == W45_AUDIT_SCHEMA, "W45 audit schema differs")
    require(audit.get("component_builder_sha256") == W45_COMPONENT_BUILDERS, "W45 component builder pins differ")
    require(audit.get("candidate_profile_kind") == "exact_pc_only_text_audit_11_file_set", "W45 profile kind differs")
    targets = audit.get("target")
    require(isinstance(targets, Mapping), "W45 targets are absent")
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == set(targets), "W45 private baseline file set differs")
    for relative, metadata in targets.items():
        require(isinstance(relative, str), "W45 target path is invalid")
        payload = (root / Path(relative)).read_bytes()
        require(isinstance(metadata, Mapping), f"W45 target metadata is invalid: {relative}")
        require(len(payload) == metadata.get("size"), f"W45 target size differs: {relative}")
        require(sha256_bytes(payload) == metadata.get("sha256"), f"W45 target hash differs: {relative}")

    msggames: dict[str, MsgGameBaseline] = {}
    tables: dict[str, TableBaseline] = {}
    for resource, expected in W45_PROFILES.items():
        payload = (root / Path(resource)).read_bytes()
        header, raw = require_profile(payload, expected, f"W45 private baseline {resource}")
        if resource in MSGGAME_RESOURCES:
            W27.validate_raw_roundtrip(payload, f"W45 private baseline {resource}")
            records = W27.records_by_coordinate(payload)
            require(records, f"W45 baseline has no MSGGAME records: {resource}")
            msggames[resource] = MsgGameBaseline(payload, raw, records)
        else:
            table = parse_message_table(raw)
            require(table.texts, f"W45 baseline has no table records: {resource}")
            require(rebuild_message_table(table, table.texts) == raw, f"W45 table round-trip differs: {resource}")
            require(recompress_wrapper(raw, header) == payload, f"W45 packed round-trip differs: {resource}")
            tables[resource] = TableBaseline(payload, header, raw, table)
    return msggames, tables, audit


def component_policy_is_private(manifest: Mapping[str, Any], audit: Mapping[str, Any], spec: ComponentSpec) -> None:
    require(manifest.get("candidate_only") is True, f"{spec.name} is not candidate-only")
    require(
        manifest.get("candidate_output_must_be_under") == f"tmp/{spec.workstream}",
        f"{spec.name} candidate root policy differs",
    )
    require(manifest.get("steam_game_resource_write") in {"absent", False}, f"{spec.name} game write policy differs")
    for key in ("transaction", "git_operation", "network", "release"):
        require(manifest.get(key) == "not_implemented", f"{spec.name} {key} policy differs")


def resource_metadata(spec: ComponentSpec, manifest: Mapping[str, Any], audit: Mapping[str, Any]) -> Mapping[str, ResourceMetadata]:
    result: dict[str, ResourceMetadata] = {}
    if spec.layout == "wave52":
        audit_union = audit.get("union")
        require(isinstance(audit_union, Mapping), "Wave 52 union audit is absent")
        for resource in spec.resource_outputs:
            result[resource] = ResourceMetadata(
                manifest.get("w45_inputs", {}).get(resource),
                manifest.get("outputs", {}).get(resource),
                audit.get("w45_inputs", {}).get(resource),
                audit_union.get("target_profiles", {}).get(resource),
                normalize_declared_coordinates(resource, manifest.get("changed_coordinates", {}).get(resource), f"{spec.name} {resource}"),
            )
    elif spec.layout == "block15":
        for resource in spec.resource_outputs:
            result[resource] = ResourceMetadata(
                manifest.get("w45_inputs", {}).get(resource),
                manifest.get("outputs", {}).get(resource),
                audit.get("w45_inputs", {}).get(resource),
                audit.get("outputs", {}).get(resource),
                normalize_declared_coordinates(resource, manifest.get("apply_coordinates", {}).get(resource), f"{spec.name} {resource}", slots=True),
            )
    elif spec.layout == "npc":
        resources = manifest.get("resources")
        audit_input = audit.get("input")
        audit_target = audit.get("target")
        require(isinstance(resources, Mapping) and isinstance(audit_input, Mapping) and isinstance(audit_target, Mapping), "NPC resource metadata is absent")
        for resource in spec.resource_outputs:
            entry = resources.get(resource)
            key = Path(resource).stem
            require(isinstance(entry, Mapping), f"NPC resource metadata is absent: {resource}")
            result[resource] = ResourceMetadata(
                entry.get("input"),
                entry.get("output"),
                audit_input.get(key),
                audit_target.get(key),
                normalize_declared_coordinates(resource, entry.get("actual_changed_ids"), f"{spec.name} {resource}"),
            )
    elif spec.layout == "reflow":
        entry = manifest.get("resource")
        require(isinstance(entry, Mapping) and entry.get("relative") == PK_EVENT, "reflow resource metadata differs")
        result[PK_EVENT] = ResourceMetadata(
            entry.get("input"),
            entry.get("output"),
            audit.get("input"),
            audit.get("target"),
            normalize_declared_coordinates(PK_EVENT, entry.get("changed_ids"), spec.name),
        )
    else:  # pragma: no cover - static spec guard
        raise CompositeError(f"unsupported component layout: {spec.layout}")
    require(set(result) == set(spec.resource_outputs), f"{spec.name} resource scope differs")
    return result


def component_declared_count(spec: ComponentSpec, manifest: Mapping[str, Any], audit: Mapping[str, Any]) -> None:
    if spec.layout == "wave52":
        audit_union = audit.get("union")
        require(manifest.get("changed_record_count") == spec.expected_count, "Wave 52 manifest count differs")
        require(isinstance(audit_union, Mapping) and audit_union.get("changed_record_count") == spec.expected_count, "Wave 52 audit count differs")
    elif spec.layout == "block15":
        require(manifest.get("apply_record_count") == spec.expected_count, "Block 15 manifest apply count differs")
        require(audit.get("apply_record_count") == spec.expected_count, "Block 15 audit apply count differs")
        require(manifest.get("hold_record_count") == 1 and audit.get("hold_record_count") == 1, "Block 15 hold count differs")
        require(audit.get("proposal_count") == 18, "Block 15 proposal count differs")
    else:
        require(manifest.get("changed_record_count") == spec.expected_count, f"{spec.name} manifest count differs")
        require(audit.get("changed_record_count") == spec.expected_count, f"{spec.name} audit count differs")


def component_held_coordinates(spec: ComponentSpec, manifest: Mapping[str, Any], audit: Mapping[str, Any]) -> Mapping[str, tuple[Any, ...]]:
    holds: dict[str, tuple[Any, ...]] = {resource: () for resource in RESOURCE_ORDER}
    if spec.layout == "block15":
        manifest_holds = manifest.get("hold_coordinates")
        require(isinstance(manifest_holds, Mapping), "Block 15 holds are absent")
        holds[BASE_MSGGAME] = normalize_declared_coordinates(BASE_MSGGAME, manifest_holds.get(BASE_MSGGAME), "Block 15 base holds", slots=True)
        holds[PK_MSGGAME] = normalize_declared_coordinates(PK_MSGGAME, manifest_holds.get(PK_MSGGAME), "Block 15 PK holds", slots=True)
        require(holds[BASE_MSGGAME] == ((15, 1121),) and not holds[PK_MSGGAME], "Block 15 hold scope differs")
    elif spec.layout == "npc":
        declared = manifest.get("explicit_holds")
        require(isinstance(declared, list) and len(declared) == 1, "NPC explicit hold count differs")
        hold = declared[0]
        require(isinstance(hold, Mapping), "NPC explicit hold is invalid")
        require(hold.get("resource") == "msgev" and hold.get("id") == 3956, "NPC explicit hold differs")
        require(hold.get("candidate_utf16le_byte_identical") is True, "NPC hold byte policy differs")
        audit_holds = audit.get("explicit_holds")
        require(isinstance(audit_holds, list) and len(audit_holds) == 1 and audit_holds[0].get("id") == 3956, "NPC audit hold differs")
        holds[PK_EVENT] = (3956,)
    elif spec.layout == "reflow":
        hard = normalize_declared_coordinates(PK_EVENT, manifest.get("hard_holds"), "reflow hard holds")
        semantic = normalize_declared_coordinates(PK_EVENT, manifest.get("semantic_holds"), "reflow semantic holds")
        require(hard == (3202, 3900, 3934, 4140, 8723, 9359, 10045), "reflow hard holds differ")
        require(semantic == (8510,), "reflow semantic holds differ")
        require(audit.get("hard_holds") == list(hard) and audit.get("semantic_holds") == list(semantic), "reflow audit holds differ")
        holds[PK_EVENT] = tuple(sorted((*hard, *semantic)))
    return holds


def diff_msggame_component(baseline: MsgGameBaseline, payload: bytes, label: str) -> Mapping[tuple[int, int], bytes]:
    W27.validate_raw_roundtrip(payload, label)
    records = W27.records_by_coordinate(payload)
    require(set(records) == set(baseline.records), f"{label} record coordinate set differs")
    return {coordinate: record.data for coordinate, record in records.items() if record.data != baseline.records[coordinate].data}


def diff_table_component(baseline: TableBaseline, payload: bytes, label: str) -> Mapping[int, str]:
    header, raw, _profile = inspect_packed(payload, label)
    table = parse_message_table(raw)
    require(len(table.texts) == len(baseline.table.texts), f"{label} table count differs")
    require(rebuild_message_table(table, table.texts) == raw, f"{label} table raw round-trip differs")
    require(recompress_wrapper(raw, header) == payload, f"{label} table packed round-trip differs")
    return {index: text for index, text in enumerate(table.texts) if text != baseline.table.texts[index]}


def read_component(
    spec: ComponentSpec,
    msggame_baselines: Mapping[str, MsgGameBaseline],
    table_baselines: Mapping[str, TableBaseline],
) -> tuple[ComponentBinding, Mapping[str, Mapping[Any, Any]]]:
    root = require_private_source(spec.candidate_root, f"{spec.name} private candidate")
    require(sha256_path(spec.builder_path) == spec.builder_sha256, f"{spec.name} builder hash differs")
    expected_files = set(spec.resource_outputs) | {"audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"{spec.name} private candidate file set differs")

    manifest_bytes, manifest = load_json(root / "candidate_manifest.v1.json", f"{spec.name} manifest")
    audit_bytes, audit = load_json(root / "audit.v1.json", f"{spec.name} audit")
    require(sha256_bytes(manifest_bytes) == spec.candidate_manifest_sha256, f"{spec.name} manifest hash differs")
    require(sha256_bytes(audit_bytes) == spec.component_audit_sha256, f"{spec.name} audit hash differs")
    require(sha256_bytes(canonical_json(audit)) == spec.component_audit_sha256, f"{spec.name} audit canonical hash differs")
    require(manifest.get("schema") == spec.manifest_schema, f"{spec.name} manifest schema differs")
    require(audit.get("schema") == spec.audit_schema, f"{spec.name} audit schema differs")
    if spec.layout != "block15":
        require(manifest.get("audit_sha256") == spec.component_audit_sha256, f"{spec.name} audit binding differs")
    else:
        require(manifest.get("record_evidence_sha256") == audit.get("record_evidence_sha256"), "Block 15 record binding differs")
    component_policy_is_private(manifest, audit, spec)
    component_declared_count(spec, manifest, audit)
    metadata = resource_metadata(spec, manifest, audit)
    holds = component_held_coordinates(spec, manifest, audit)

    differences: dict[str, Mapping[Any, Any]] = {}
    coordinates: dict[str, tuple[Any, ...]] = {}
    for resource, expected_output in spec.resource_outputs.items():
        entry = metadata[resource]
        require_profile_metadata(entry.manifest_input, W45_PROFILES[resource], f"{spec.name} manifest W45 input {resource}", require_raw=spec.layout != "block15")
        require_profile_metadata(entry.audit_input, W45_PROFILES[resource], f"{spec.name} audit W45 input {resource}", require_raw=spec.layout != "block15")
        require_profile_metadata(entry.manifest_output, expected_output, f"{spec.name} manifest output {resource}", require_raw=True)
        require_profile_metadata(entry.audit_output, expected_output, f"{spec.name} audit output {resource}", require_raw=True)
        payload = (root / Path(resource)).read_bytes()
        require_profile(payload, expected_output, f"{spec.name} candidate {resource}")
        if resource in MSGGAME_RESOURCES:
            changed = diff_msggame_component(msggame_baselines[resource], payload, f"{spec.name} candidate {resource}")
        else:
            changed = diff_table_component(table_baselines[resource], payload, f"{spec.name} candidate {resource}")
        actual = tuple(sorted(changed))
        require(actual == entry.declared_coordinates, f"{spec.name} actual changed scope differs: {resource}")
        require(len(actual) == spec.resource_counts[resource], f"{spec.name} changed count differs: {resource}")
        differences[resource] = changed
        coordinates[resource] = actual

    declared_total = sum(len(values) for values in coordinates.values())
    require(declared_total == spec.expected_count, f"{spec.name} declared record count differs")
    for resource, held in holds.items():
        if not held:
            continue
        if resource in spec.resource_outputs:
            payload = (root / Path(resource)).read_bytes()
            if resource in MSGGAME_RESOURCES:
                candidate_records = W27.records_by_coordinate(payload)
                baseline_records = msggame_baselines[resource].records
                for coordinate in held:
                    require(candidate_records[coordinate].data == baseline_records[coordinate].data, f"{spec.name} changed held coordinate: {resource} {coordinate_text(resource, coordinate)}")
            else:
                _header, raw, _profile = inspect_packed(payload, f"{spec.name} held table {resource}")
                candidate_table = parse_message_table(raw)
                baseline_table = table_baselines[resource].table
                for entry_id in held:
                    require(candidate_table.texts[entry_id] == baseline_table.texts[entry_id], f"{spec.name} changed held coordinate: {resource} {entry_id}")

    binding = ComponentBinding(
        spec.name,
        spec.workstream,
        root.relative_to(REPO).as_posix(),
        spec.builder_sha256,
        spec.candidate_manifest_sha256,
        spec.component_audit_sha256,
        declared_total,
        coordinates,
        {resource: values for resource, values in holds.items() if values},
    )
    return binding, differences


def register_replacements(
    replacements: dict[str, dict[Any, Any]],
    provenance: dict[str, dict[Any, str]],
    component: ComponentBinding,
    differences: Mapping[str, Mapping[Any, Any]],
) -> None:
    for resource, records in differences.items():
        destination = replacements.setdefault(resource, {})
        origins = provenance.setdefault(resource, {})
        for coordinate, value in records.items():
            if coordinate in destination:
                raise CompositeError(
                    f"component coordinate overlap is forbidden: {resource} {coordinate_text(resource, coordinate)} "
                    f"({origins[coordinate]}, {component.name})"
                )
            destination[coordinate] = value
            origins[coordinate] = component.name


def rebuild_msggame_union(resource: str, baseline: MsgGameBaseline, replacements: Mapping[tuple[int, int], bytes]) -> bytes:
    packed = W27.rebuild_packed_msggame(baseline.packed, dict(replacements))
    _header, raw = require_profile(packed, UNION_TARGET_PROFILES[resource], f"union {resource}")
    W27.validate_raw_roundtrip(packed, f"union {resource}")
    records = W27.records_by_coordinate(packed)
    require(set(records) == set(baseline.records), f"union record set differs: {resource}")
    actual = {coordinate for coordinate, record in records.items() if record.data != baseline.records[coordinate].data}
    require(actual == set(replacements), f"union changed scope differs: {resource}")
    for coordinate, replacement in replacements.items():
        require(records[coordinate].data == replacement, f"union replacement differs: {resource} {coordinate_text(resource, coordinate)}")
    require(raw, f"union raw payload is empty: {resource}")
    return packed


def rebuild_table_union(resource: str, baseline: TableBaseline, replacements: Mapping[int, str]) -> bytes:
    targets = list(baseline.table.texts)
    for entry_id, text in replacements.items():
        require(0 <= entry_id < len(targets), f"union table ID outside range: {resource} {entry_id}")
        targets[entry_id] = text
    raw = rebuild_message_table(baseline.table, tuple(targets))
    packed = recompress_wrapper(raw, baseline.header)
    header, decoded = require_profile(packed, UNION_TARGET_PROFILES[resource], f"union {resource}")
    table = parse_message_table(decoded)
    require(rebuild_message_table(table, table.texts) == decoded, f"union table raw round-trip differs: {resource}")
    require(recompress_wrapper(decoded, header) == packed, f"union table packed round-trip differs: {resource}")
    actual = {index for index, text in enumerate(table.texts) if text != baseline.table.texts[index]}
    require(actual == set(replacements), f"union table changed scope differs: {resource}")
    for entry_id, text in replacements.items():
        require(table.texts[entry_id] == text, f"union table replacement differs: {resource} {entry_id}")
    return packed


def binding_dict(binding: ComponentBinding) -> dict[str, Any]:
    return {
        "name": binding.name,
        "workstream": binding.workstream,
        "candidate_root": binding.candidate_root,
        "builder_sha256": binding.builder_sha256,
        "candidate_manifest_sha256": binding.candidate_manifest_sha256,
        "component_audit_sha256": binding.component_audit_sha256,
        "changed_record_count": binding.changed_record_count,
        "changed_coordinates": {
            resource: [coordinate_text(resource, coordinate) for coordinate in coordinates]
            for resource, coordinates in binding.changed_coordinates.items()
        },
        "held_coordinates_excluded": {
            resource: [coordinate_text(resource, coordinate) for coordinate in coordinates]
            for resource, coordinates in binding.held_coordinates.items()
        },
    }


def hold_dict(holds: Mapping[str, tuple[Any, ...]]) -> dict[str, list[str | int]]:
    return {
        resource: [coordinate_text(resource, coordinate) for coordinate in coordinates]
        for resource, coordinates in holds.items()
        if coordinates
    }


def prepare_candidate() -> CandidateBundle:
    msggame_baselines, table_baselines, w45_audit = load_w45_baselines()
    replacements: dict[str, dict[Any, Any]] = {resource: {} for resource in RESOURCE_ORDER}
    provenance: dict[str, dict[Any, str]] = {resource: {} for resource in RESOURCE_ORDER}
    bindings: list[ComponentBinding] = []
    for spec in COMPONENT_SPECS:
        binding, differences = read_component(spec, msggame_baselines, table_baselines)
        register_replacements(replacements, provenance, binding, differences)
        bindings.append(binding)

    require(len(bindings) == 4, "component count differs")
    require(sum(binding.changed_record_count for binding in bindings) == UNION_TOTAL_COUNT, "component total differs")
    for resource, expected_count in UNION_COUNTS.items():
        require(len(replacements[resource]) == expected_count, f"union replacement count differs: {resource}")
    for resource, held in EXCLUDED_HOLDS.items():
        for coordinate in held:
            require(coordinate not in replacements[resource], f"held coordinate entered union: {resource} {coordinate_text(resource, coordinate)}")

    files = {
        BASE_MSGGAME: rebuild_msggame_union(BASE_MSGGAME, msggame_baselines[BASE_MSGGAME], replacements[BASE_MSGGAME]),
        PK_MSGGAME: rebuild_msggame_union(PK_MSGGAME, msggame_baselines[PK_MSGGAME], replacements[PK_MSGGAME]),
        PK_MSGDATA: rebuild_table_union(PK_MSGDATA, table_baselines[PK_MSGDATA], replacements[PK_MSGDATA]),
        PK_EVENT: rebuild_table_union(PK_EVENT, table_baselines[PK_EVENT], replacements[PK_EVENT]),
    }
    union_coordinates = {resource: tuple(sorted(replacements[resource])) for resource in RESOURCE_ORDER}
    holds = {resource: tuple(values) for resource, values in EXCLUDED_HOLDS.items()}

    audit = {
        "schema": "nobu16.kr.pc-private-union-composite-wave53-audit.v1",
        "source_policy": {
            "private_w45_baseline_only": True,
            "external_game_paths_read": False,
            "switch_sc_inputs": "forbidden",
            "steam_access": "forbidden",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
            "steam_game_resource_written": False,
        },
        "pinned_helpers_sha256": {
            "wave27_msggame": W27_HELPER_SHA256,
            "nobu16_lz4": LZ4_HELPER_SHA256,
            "nobu16_msg_table": TABLE_HELPER_SHA256,
        },
        "w45_baseline": {
            "workstream": W45_WORKSTREAM,
            "candidate_root": W45_BASELINE_ROOT.relative_to(REPO).as_posix(),
            "builder_sha256": W45_BUILDER_SHA256,
            "audit_sha256": W45_AUDIT_SHA256,
            "audit_schema": W45_AUDIT_SCHEMA,
            "component_builder_sha256": W45_COMPONENT_BUILDERS,
            "inputs": {resource: profile_dict(profile) for resource, profile in W45_PROFILES.items()},
            "audit_target_file_count": len(w45_audit["target"]),
        },
        "components": [binding_dict(binding) for binding in bindings],
        "selection_rule": (
            "Diff each pinned component candidate against the private W45 baseline and merge only its actual "
            "changed record coordinates. Duplicate coordinates fail even when payload bytes match; declared holds "
            "remain byte-identical to W45 and cannot enter the union."
        ),
        "excluded_holds": hold_dict(holds),
        "union": {
            "changed_record_count": UNION_TOTAL_COUNT,
            "changed_record_count_by_resource": dict(UNION_COUNTS),
            "changed_coordinates": {
                resource: [coordinate_text(resource, coordinate) for coordinate in coordinates]
                for resource, coordinates in union_coordinates.items()
            },
            "target_profiles": {resource: profile_dict(profile) for resource, profile in UNION_TARGET_PROFILES.items()},
        },
    }
    manifest = {
        "schema": "nobu16.kr.pc-private-union-composite-wave53-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": list(RESOURCE_ORDER),
        "w45_inputs": {resource: profile_dict(profile) for resource, profile in W45_PROFILES.items()},
        "outputs": {resource: profile_dict(profile) for resource, profile in UNION_TARGET_PROFILES.items()},
        "changed_record_count": UNION_TOTAL_COUNT,
        "changed_record_count_by_resource": dict(UNION_COUNTS),
        "changed_coordinates": {
            resource: [coordinate_text(resource, coordinate) for coordinate in coordinates]
            for resource, coordinates in union_coordinates.items()
        },
        "excluded_holds": hold_dict(holds),
        "component_count": len(bindings),
        "component_changed_record_count": sum(binding.changed_record_count for binding in bindings),
        "switch_sc_input": "forbidden",
        "steam_access": "forbidden",
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
        "audit_sha256": sha256_bytes(canonical_json(audit)),
    }
    return CandidateBundle(files, audit, manifest, union_coordinates, holds, tuple(bindings))


def write_candidate(bundle: CandidateBundle) -> Path:
    output = require_private_output(TMP_ROOT / "candidate", "candidate output")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT))
    try:
        for resource, payload in bundle.files.items():
            path = stage / Path(resource)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        (stage / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (stage / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        if output.exists():
            require_private_output(output, "existing candidate output")
            shutil.rmtree(output)
        os.replace(stage, output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return output


def private_file_set(output: Path) -> set[str]:
    return {path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()}


def verify_private() -> dict[str, Any]:
    bundle = prepare_candidate()
    output = require_private_output(TMP_ROOT / "candidate", "candidate output")
    require(output.is_dir(), "private candidate is absent")
    expected_files = set(RESOURCE_ORDER) | {"audit.v1.json", "candidate_manifest.v1.json"}
    require(private_file_set(output) == expected_files, "private candidate file set differs")
    for resource, payload in bundle.files.items():
        require((output / Path(resource)).read_bytes() == payload, f"private candidate differs: {resource}")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require((output / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "private manifest differs")
    return result_summary(bundle, output)


def changed_coordinates_from_file(
    resource: str,
    payload: bytes,
    msggame_baselines: Mapping[str, MsgGameBaseline],
    table_baselines: Mapping[str, TableBaseline],
) -> tuple[Any, ...]:
    if resource in MSGGAME_RESOURCES:
        changed = diff_msggame_component(msggame_baselines[resource], payload, f"diff-check {resource}")
    else:
        changed = diff_table_component(table_baselines[resource], payload, f"diff-check {resource}")
    return tuple(sorted(changed))


def diff_check() -> dict[str, Any]:
    bundle = prepare_candidate()
    output = require_private_output(TMP_ROOT / "candidate", "candidate output")
    require(output.is_dir(), "private candidate is absent; build first")
    msggame_baselines, table_baselines, _w45_audit = load_w45_baselines()
    for resource in RESOURCE_ORDER:
        payload = (output / Path(resource)).read_bytes()
        require_profile(payload, UNION_TARGET_PROFILES[resource], f"diff-check target {resource}")
        actual = changed_coordinates_from_file(resource, payload, msggame_baselines, table_baselines)
        require(actual == bundle.union_coordinates[resource], f"diff-check scope differs: {resource}")
        for coordinate in bundle.held_coordinates[resource]:
            require(coordinate not in actual, f"diff-check held coordinate changed: {resource} {coordinate_text(resource, coordinate)}")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "diff-check audit differs")
    require((output / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "diff-check manifest differs")
    return result_summary(bundle, output)


def result_summary(bundle: CandidateBundle, output: Path) -> dict[str, Any]:
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "component_count": len(bundle.components),
        "changed_record_count": UNION_TOTAL_COUNT,
        "changed_record_count_by_resource": dict(UNION_COUNTS),
        "external_game_paths_read": False,
        "steam_game_resource_written": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify-private", "diff-check"))
    args = parser.parse_args(argv)
    if args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        result = result_summary(bundle, output)
    elif args.command == "verify-private":
        result = verify_private()
    else:
        result = diff_check()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
