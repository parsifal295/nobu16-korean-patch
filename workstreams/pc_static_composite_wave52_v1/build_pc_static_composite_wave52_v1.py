#!/usr/bin/env python3
"""Build a private-only union of the approved post-W45 static candidates.

This builder deliberately reads the exact installed W45 Steam-PC profiles,
then extracts record-level replacements from six independently pinned private
candidates.  It never copies a component's whole packed file: every changed
record is compared with W45, duplicate coordinates are rejected, and the
union is rebuilt from W45.  The only write target is this workstream's
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
GAME_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
TOOLS = REPO / "tools"

BASE_MSGGAME = "MSG/JP/msggame.bin"
PK_MSGGAME = "MSG_PK/JP/msggame.bin"
PK_EVENT = "MSG_PK/JP/msgev.bin"
RESOURCE_ORDER = (BASE_MSGGAME, PK_MSGGAME, PK_EVENT)

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
    """Raised when a source pin, component, or private union drifts."""


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


def reject_switch(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    require(
        not any("switch" in part.casefold() for part in resolved.parts),
        f"Nintendo Switch path is forbidden: {label}",
    )
    return resolved


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise CompositeError(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


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


# Exact installed Steam profiles produced by the already-applied W45
# transaction.  They are the only allowed baseline for every component.
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
    PK_EVENT: Profile(
        994_739,
        "01287E2ECC5328C85348657EFF06553353CB8664B0FB7E1669DB9FC591D53EBE",
        990_828,
        "F3716AB98D60931CEC0FE61976D8DAD386C05B30B7167BD1BDB2CDF02EC55ACC",
    ),
}

# The target is intentionally pinned before writing.  A rebuild that changes
# even one input record, compressor result, or component scope must fail.
UNION_TARGET_PROFILES: Mapping[str, Profile] = {
    BASE_MSGGAME: Profile(
        1_504_462,
        "367FBCD48FA824955508747A49FD4424798262C3BE75D7A67A10D859CB46B319",
        1_498_560,
        "54F18AB680E94783E3A8D24D982236AC0FCC7D39DE76C4C9DBFA993A4CB92F35",
    ),
    PK_MSGGAME: Profile(
        1_806_438,
        "8864670A0CFB2E55C031E0A72C64FAD19D172A556123082E9E75223BD07DC106",
        1_799_356,
        "CDA0FD14D0C84AE7ACA81A74A1E51951274AD9ADDD6E6C755F645F17FDBD02F6",
    ),
    PK_EVENT: Profile(
        994_751,
        "AC9C0F7FE72ADA6FA4604C1359A3FFA155BB5C166A590C3FC77BAD7C390CC90B",
        990_840,
        "F43E2742C8D9CDAA59861C5FC9011C68C3807641D97AFDAF46AFE2521BB9AA86",
    ),
}

UNION_COUNTS = {
    BASE_MSGGAME: 59,
    PK_MSGGAME: 157,
    PK_EVENT: 33,
}
UNION_TOTAL_COUNT = sum(UNION_COUNTS.values())


@dataclass(frozen=True)
class ComponentSpec:
    name: str
    workstream: str
    builder_filename: str
    builder_sha256: str
    manifest_schema: str
    audit_schema: str
    metadata_layout: str
    count_key: str
    expected_count: int
    resource_outputs: Mapping[str, Profile]
    resource_counts: Mapping[str, int]

    @property
    def candidate_root(self) -> Path:
        return TMP_ROOT.parent / self.workstream / "candidate"

    @property
    def builder_path(self) -> Path:
        return REPO / "workstreams" / self.workstream / self.builder_filename


COMPONENT_SPECS = (
    ComponentSpec(
        "wave47_battle_dialogue_static",
        "pc_battle_dialogue_static_quality_wave47_v1",
        "build_pc_battle_dialogue_static_quality_wave47_v1.py",
        "A9165C3B6F92313EEAB5A8F6E4E5534A67BE5212B3699FDACC621266EAB0D3F3",
        "nobu16.kr.pc-battle-dialogue-static-quality-wave47-manifest.v1",
        "nobu16.kr.pc-battle-dialogue-static-quality-wave47-audit.v1",
        "single",
        "changed_record_count",
        34,
        {
            PK_MSGGAME: Profile(
                1_806_594,
                "C5BAD79A8CD261864E80238A1AA558594A1BA9451CA6253B92047C952E47459D",
                1_799_512,
                "7F3C13F86CC7F038E52A05C5F75CE9B24790339FE074871B21ED85CFE31A1EB7",
            )
        },
        {PK_MSGGAME: 34},
    ),
    ComponentSpec(
        "wave48_static_ui_0143",
        "pc_dialogue_static_ui_0143_wave48_v1",
        "build_pc_dialogue_static_ui_0143_wave48_v1.py",
        "F0D3DC7538C05785BC847ECE04E66868EBF596715EF9F22BB5EC27AB29C0FD84",
        "nobu16.kr.pc-dialogue-static-ui-0143-wave48-manifest.v1",
        "nobu16.kr.pc-dialogue-static-ui-0143-wave48-audit.v1",
        "resources_map",
        "changed_record_count",
        32,
        {
            BASE_MSGGAME: Profile(
                1_504_442,
                "58DCCA79515C377A2382D893DA18C8504D0E16455C2458BE09F2167686433CED",
                1_498_540,
                "FEA6A2EAB56305E6FAF76C6D0CE32FF87E399ACE38C47F480F1CA7F5393FC335",
            ),
            PK_MSGGAME: Profile(
                1_806_574,
                "545AA7276D2B3D429FE4E58A9128AADAF4BDA4A4B6ADD58B095588EEA2759B79",
                1_799_492,
                "1D05ADB2DC07F66FE913FD4626A1B7239CC0E910D66D2E6B8C807558901FA47E",
            ),
        },
        {BASE_MSGGAME: 16, PK_MSGGAME: 16},
    ),
    ComponentSpec(
        "wave49_event_static",
        "pc_event_static_quality_wave49_v1",
        "build_pc_event_static_quality_wave49_v1.py",
        "1DBCE43D5E826AE47EF6ED82044733B82BA448043E264CA19C31A1E9AD4C6065",
        "nobu16.kr.pc-event-static-quality-wave49-manifest.v1",
        "nobu16.kr.pc-event-static-quality-wave49-audit.v1",
        "event_resource",
        "changed_record_count",
        33,
        {
            PK_EVENT: Profile(
                994_751,
                "AC9C0F7FE72ADA6FA4604C1359A3FFA155BB5C166A590C3FC77BAD7C390CC90B",
                990_840,
                "F43E2742C8D9CDAA59861C5FC9011C68C3807641D97AFDAF46AFE2521BB9AA86",
            )
        },
        {PK_EVENT: 33},
    ),
    ComponentSpec(
        "wave50_dialogue_static_blocks9_12",
        "pc_dialogue_quality_wave50_static_blocks9_12_v1",
        "build_pc_dialogue_quality_wave50_static_blocks9_12_v1.py",
        "092F97A209CD3B126145D6BF038E59738D08AF8E6AD1579B80D8393E2C887CE4",
        "nobu16.kr.pc-dialogue-quality-wave50-static-blocks9-12-manifest.v1",
        "nobu16.kr.pc-dialogue-quality-wave50-static-blocks9-12-audit.v1",
        "inputs_outputs",
        "changed_record_count",
        56,
        {
            BASE_MSGGAME: Profile(
                1_504_498,
                "BD356DA65E0FDDF3C32A1BAC42DAC5A25C2451331CAEEBE24009B7476BD379B1",
                1_498_596,
                "DC4FA2698B74687AE92B98132FB7A4E3718FCF0F428C01867D7879BFA9B9105C",
            ),
            PK_MSGGAME: Profile(
                1_806_618,
                "CC48466EE332A922069EAF2614236F2DFFA1C18D0253791AE416889C3A151BAD",
                1_799_536,
                "D157BB8EFC2F150E98BB116A69119FEE14A1F1C0A0E7005383565476B2CAD8F6",
            ),
        },
        {BASE_MSGGAME: 20, PK_MSGGAME: 36},
    ),
    ComponentSpec(
        "wave51_tutorial_static_blocks13_14",
        "pc_dialogue_quality_wave51_static_blocks13_14_v1",
        "build_pc_dialogue_quality_wave51_static_blocks13_14_v1.py",
        "051C9C5A92488FED046463073375148BFDC11DDFEF802E752B18AB256E41E73D",
        "nobu16.kr.pc-dialogue-quality-wave51-static-blocks13-14-manifest.v1",
        "nobu16.kr.pc-dialogue-quality-wave51-static-blocks13-14-audit.v1",
        "w45_inputs_outputs",
        "changed_record_count",
        54,
        {
            BASE_MSGGAME: Profile(
                1_504_366,
                "1803983A23DB63ED4FEDF67D5929786CCA8E6BF2A7F2932DA363DF95A7B2D57E",
                1_498_464,
                "5A7FFC7BFF777662EEBAC68E844C35BF3FFD7B05D7723AD6F60B9C03C669203F",
            ),
            PK_MSGGAME: Profile(
                1_806_482,
                "905DE32B79EB59BAD8B7B656B434D494F5D29271042A31B1DADFFADFE1A77FC8",
                1_799_400,
                "0D2A599230CB78AEC780E80DABEE4CF07733DF7D98FD9A283EC5659DC9D00832",
            ),
        },
        {BASE_MSGGAME: 19, PK_MSGGAME: 35},
    ),
    ComponentSpec(
        "wave51_terminal_static_0143",
        "pc_dialogue_static_terminal_0143_wave51_v1",
        "build_pc_dialogue_static_terminal_0143_wave51_v1.py",
        "99288F604BF6F421652C8AC4C8E50D1D991FB4FF7EA304261B32F729C0FCBDB5",
        "nobu16.kr.pc-dialogue-static-terminal-0143-wave51-manifest.v1",
        "nobu16.kr.pc-dialogue-static-terminal-0143-wave51-audit.v1",
        "terminal_resources",
        "static_0143_removals",
        40,
        {
            BASE_MSGGAME: Profile(
                1_504_386,
                "F3BA88A3FF7A3B297C74A0758EDC8C53FB32AD351B0A3DF5BD97AC6E6CD80906",
                1_498_484,
                "3C290BCA6E8A0F55615BA714B90F5E15B7E7C6C18EC3AAFFAEE149DE53FD98FC",
            ),
            PK_MSGGAME: Profile(
                1_806_321,
                "D9EF6224B4E6D2C11CD190A12FB2C75A58E63ED7F0D13A1FD0D57622375426BA",
                1_799_240,
                "1314CD6678F56C5B0C44A7EC41F8128F11DB496F7630FDDD1A554BD08F180C75",
            ),
        },
        {BASE_MSGGAME: 4, PK_MSGGAME: 36},
    ),
)


if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


def load_w27() -> Any:
    require(W27_HELPER.is_file(), "Wave 27 MSGGAME helper is absent")
    require(sha256_path(W27_HELPER) == W27_HELPER_SHA256, "Wave 27 MSGGAME helper hash differs")
    spec = importlib.util.spec_from_file_location("wave52_pinned_wave27", W27_HELPER)
    if spec is None or spec.loader is None:  # pragma: no cover - import guard
        raise CompositeError("cannot load Wave 27 MSGGAME helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


require(sha256_path(LZ4_HELPER) == LZ4_HELPER_SHA256, "LZ4 helper hash differs")
require(sha256_path(TABLE_HELPER) == TABLE_HELPER_SHA256, "message-table helper hash differs")
W27 = load_w27()


@dataclass(frozen=True)
class MsgGameBaseline:
    packed: bytes
    raw: bytes
    records: Mapping[tuple[int, int], Any]


@dataclass(frozen=True)
class EventBaseline:
    packed: bytes
    header: Any
    raw: bytes
    table: Any


@dataclass(frozen=True)
class ComponentBinding:
    name: str
    workstream: str
    candidate_root: str
    builder_sha256: str
    candidate_manifest_sha256: str
    component_audit_sha256: str
    changed_coordinates: Mapping[str, tuple[Any, ...]]
    changed_record_count: int


@dataclass(frozen=True)
class CandidateBundle:
    files: Mapping[str, bytes]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]
    union_coordinates: Mapping[str, tuple[Any, ...]]
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


def coordinate_text(resource: str, coordinate: Any) -> str | int:
    if resource == PK_EVENT:
        return int(coordinate)
    return f"{coordinate[0]}:{coordinate[1]}"


def normalize_declared_coordinates(resource: str, values: Any, label: str) -> tuple[Any, ...]:
    require(isinstance(values, list), f"{label} coordinate list is absent")
    if resource == PK_EVENT:
        normalized = tuple(int(value) for value in values)
        require(all(value >= 0 for value in normalized), f"{label} contains a negative event ID")
    else:
        normalized = tuple(parse_msggame_coordinate(value, label) for value in values)
    require(len(set(normalized)) == len(normalized), f"{label} contains duplicate coordinates")
    require(tuple(sorted(normalized)) == normalized, f"{label} coordinates are not sorted")
    return normalized


def component_metadata(
    spec: ComponentSpec, manifest: Mapping[str, Any]
) -> Mapping[str, tuple[Mapping[str, Any], Mapping[str, Any], tuple[Any, ...]]]:
    """Normalize the six intentionally different component manifest layouts."""

    result: dict[str, tuple[Mapping[str, Any], Mapping[str, Any], tuple[Any, ...]]] = {}
    if spec.metadata_layout == "single":
        relative = manifest.get("resource")
        require(relative in spec.resource_outputs, f"{spec.name} resource differs")
        result[str(relative)] = (
            manifest.get("input"),
            manifest.get("output"),
            normalize_declared_coordinates(str(relative), manifest.get("changed_coordinates"), spec.name),
        )
    elif spec.metadata_layout in {"resources_map", "terminal_resources"}:
        resources = manifest.get("resources")
        require(isinstance(resources, Mapping), f"{spec.name} resource map is absent")
        for relative in spec.resource_outputs:
            entry = resources.get(relative)
            require(isinstance(entry, Mapping), f"{spec.name} resource metadata is absent: {relative}")
            result[relative] = (
                entry.get("input"),
                entry.get("output"),
                normalize_declared_coordinates(relative, entry.get("changed_coordinates"), f"{spec.name} {relative}"),
            )
    elif spec.metadata_layout in {"inputs_outputs", "w45_inputs_outputs"}:
        input_key = "inputs" if spec.metadata_layout == "inputs_outputs" else "w45_inputs"
        inputs = manifest.get(input_key)
        outputs = manifest.get("outputs")
        coordinates = manifest.get("changed_coordinates")
        require(isinstance(inputs, Mapping), f"{spec.name} inputs are absent")
        require(isinstance(outputs, Mapping), f"{spec.name} outputs are absent")
        require(isinstance(coordinates, Mapping), f"{spec.name} coordinates are absent")
        for relative in spec.resource_outputs:
            result[relative] = (
                inputs.get(relative),
                outputs.get(relative),
                normalize_declared_coordinates(relative, coordinates.get(relative), f"{spec.name} {relative}"),
            )
    elif spec.metadata_layout == "event_resource":
        entry = manifest.get("resource")
        require(isinstance(entry, Mapping), f"{spec.name} event resource is absent")
        relative = entry.get("relative")
        require(relative == PK_EVENT, f"{spec.name} event resource differs")
        result[PK_EVENT] = (
            entry.get("input"),
            entry.get("output"),
            normalize_declared_coordinates(PK_EVENT, entry.get("changed_ids"), spec.name),
        )
    else:  # pragma: no cover - static spec guard
        raise CompositeError(f"unsupported component metadata layout: {spec.metadata_layout}")
    require(set(result) == set(spec.resource_outputs), f"{spec.name} resource scope differs")
    return result


def require_component_policy(spec: ComponentSpec, manifest: Mapping[str, Any], audit: Mapping[str, Any]) -> None:
    private_flag = manifest.get("candidate_only") is True or manifest.get("private_output_only") is True
    require(private_flag, f"{spec.name} is not candidate-only")

    switch_state = manifest.get("switch_korean_input", audit.get("switch_korean_input"))
    source_policy = audit.get("source_policy")
    if switch_state is not None:
        require(switch_state == "forbidden", f"{spec.name} Switch input policy differs")
    else:
        require(isinstance(source_policy, Mapping), f"{spec.name} lacks source policy")
        require(source_policy.get("switch_korean_read") is False, f"{spec.name} Switch input policy differs")

    steam_state = manifest.get("steam_game_resource_write", audit.get("steam_game_resource_write"))
    if steam_state is not None:
        require(steam_state in {"absent", False}, f"{spec.name} Steam write policy differs")
    else:
        require(isinstance(source_policy, Mapping), f"{spec.name} lacks Steam write policy")
        require(source_policy.get("steam_game_resource_written") is False, f"{spec.name} Steam write policy differs")


def load_msggame_baseline(resource: str) -> MsgGameBaseline:
    path = reject_switch(GAME_ROOT / Path(resource), f"W45 Steam PC baseline {resource}")
    packed = path.read_bytes()
    _header, raw = require_profile(packed, W45_PROFILES[resource], f"W45 Steam PC baseline {resource}")
    W27.validate_raw_roundtrip(packed, f"W45 Steam PC baseline {resource}")
    records = W27.records_by_coordinate(packed)
    require(records, f"W45 Steam PC baseline {resource} has no records")
    return MsgGameBaseline(packed, raw, records)


def load_event_baseline() -> EventBaseline:
    path = reject_switch(GAME_ROOT / Path(PK_EVENT), "W45 Steam PC baseline event")
    packed = path.read_bytes()
    header, raw = require_profile(packed, W45_PROFILES[PK_EVENT], "W45 Steam PC baseline event")
    table = parse_message_table(raw)
    require(rebuild_message_table(table, table.texts) == raw, "W45 event raw table round-trip differs")
    require(recompress_wrapper(raw, header) == packed, "W45 event packed round-trip differs")
    require(len(table.texts) == 17_916, "W45 event record count differs")
    return EventBaseline(packed, header, raw, table)


def diff_event_component(baseline: EventBaseline, payload: bytes, label: str) -> Mapping[int, str]:
    header, raw, _profile = inspect_packed(payload, label)
    table = parse_message_table(raw)
    require(len(table.texts) == len(baseline.table.texts), f"{label} event record count differs")
    require(rebuild_message_table(table, table.texts) == raw, f"{label} event raw table round-trip differs")
    require(recompress_wrapper(raw, header) == payload, f"{label} event packed round-trip differs")
    return {
        index: text
        for index, text in enumerate(table.texts)
        if text != baseline.table.texts[index]
    }


def read_component(
    spec: ComponentSpec,
    msggame_baselines: Mapping[str, MsgGameBaseline],
    event_baseline: EventBaseline,
) -> tuple[ComponentBinding, Mapping[str, Mapping[Any, Any]]]:
    root = reject_switch(spec.candidate_root, f"{spec.name} private candidate")
    tmp_parent = (REPO / "tmp").resolve(strict=True)
    try:
        root.relative_to(tmp_parent)
    except ValueError as exc:  # pragma: no cover - spec guard
        raise CompositeError(f"{spec.name} candidate is outside tmp") from exc

    expected_files = set(spec.resource_outputs) | {"audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"{spec.name} candidate file set differs")

    builder = reject_switch(spec.builder_path, f"{spec.name} builder")
    require(sha256_path(builder) == spec.builder_sha256, f"{spec.name} builder hash differs")

    try:
        manifest_bytes = (root / "candidate_manifest.v1.json").read_bytes()
        audit = json.loads((root / "audit.v1.json").read_text(encoding="utf-8"))
        manifest = json.loads(manifest_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CompositeError(f"{spec.name} candidate metadata is invalid") from exc
    require(manifest.get("schema") == spec.manifest_schema, f"{spec.name} manifest schema differs")
    require(audit.get("schema") == spec.audit_schema, f"{spec.name} audit schema differs")
    require(manifest.get("audit_sha256") == sha256_bytes(canonical_json(audit)), f"{spec.name} audit binding differs")
    require_component_policy(spec, manifest, audit)
    require(manifest.get(spec.count_key) == spec.expected_count, f"{spec.name} declared record count differs")
    require(audit.get(spec.count_key) == spec.expected_count, f"{spec.name} audit record count differs")

    metadata = component_metadata(spec, manifest)
    declared_total = sum(len(values[2]) for values in metadata.values())
    require(declared_total == spec.expected_count, f"{spec.name} declared coordinate count differs")

    differences: dict[str, Mapping[Any, Any]] = {}
    coordinates: dict[str, tuple[Any, ...]] = {}
    for resource, output_profile in spec.resource_outputs.items():
        input_meta, output_meta, declared = metadata[resource]
        require_profile_metadata(input_meta, W45_PROFILES[resource], f"{spec.name} W45 input {resource}", require_raw=False)
        require_profile_metadata(output_meta, output_profile, f"{spec.name} output {resource}", require_raw=True)
        payload = (root / Path(resource)).read_bytes()
        require_profile(payload, output_profile, f"{spec.name} candidate {resource}")

        if resource == PK_EVENT:
            changed = diff_event_component(event_baseline, payload, f"{spec.name} candidate {resource}")
        else:
            # ``diff_msggame_component`` does not re-check the baseline
            # profile; it is loaded once, pinned above, and the component
            # output profile has just been checked against its exact pin.
            W27.validate_raw_roundtrip(payload, f"{spec.name} candidate {resource}")
            records = W27.records_by_coordinate(payload)
            baseline = msggame_baselines[resource]
            require(set(records) == set(baseline.records), f"{spec.name} {resource} record coordinate set differs")
            changed = {
                coordinate: record.data
                for coordinate, record in records.items()
                if record.data != baseline.records[coordinate].data
            }
        actual = tuple(sorted(changed))
        require(actual == declared, f"{spec.name} actual changed scope differs: {resource}")
        require(len(actual) == spec.resource_counts[resource], f"{spec.name} changed count differs: {resource}")
        differences[resource] = changed
        coordinates[resource] = actual

    binding = ComponentBinding(
        name=spec.name,
        workstream=spec.workstream,
        candidate_root=root.relative_to(REPO).as_posix(),
        builder_sha256=spec.builder_sha256,
        candidate_manifest_sha256=sha256_bytes(manifest_bytes),
        component_audit_sha256=sha256_bytes(canonical_json(audit)),
        changed_coordinates=coordinates,
        changed_record_count=declared_total,
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
                prior = origins[coordinate]
                raise CompositeError(
                    f"component coordinate overlap is forbidden: {resource} {coordinate_text(resource, coordinate)} "
                    f"({prior}, {component.name})"
                )
            destination[coordinate] = value
            origins[coordinate] = component.name


def rebuild_msggame_union(
    resource: str, baseline: MsgGameBaseline, replacements: Mapping[tuple[int, int], bytes]
) -> bytes:
    packed = W27.rebuild_packed_msggame(baseline.packed, dict(replacements))
    _header, raw = require_profile(packed, UNION_TARGET_PROFILES[resource], f"union {resource}")
    W27.validate_raw_roundtrip(packed, f"union {resource}")
    records = W27.records_by_coordinate(packed)
    require(set(records) == set(baseline.records), f"union {resource} record coordinate set differs")
    actual = {
        coordinate
        for coordinate, record in records.items()
        if record.data != baseline.records[coordinate].data
    }
    require(actual == set(replacements), f"union {resource} changed scope differs")
    for coordinate, replacement in replacements.items():
        require(records[coordinate].data == replacement, f"union {resource} record differs: {coordinate_text(resource, coordinate)}")
    require(raw, f"union {resource} raw payload is empty")
    return packed


def rebuild_event_union(baseline: EventBaseline, replacements: Mapping[int, str]) -> bytes:
    targets = list(baseline.table.texts)
    for entry_id, text in replacements.items():
        require(0 <= entry_id < len(targets), f"union event ID is outside table: {entry_id}")
        targets[entry_id] = text
    raw = rebuild_message_table(baseline.table, tuple(targets))
    packed = recompress_wrapper(raw, baseline.header)
    _header, decoded = require_profile(packed, UNION_TARGET_PROFILES[PK_EVENT], "union event")
    table = parse_message_table(decoded)
    require(rebuild_message_table(table, table.texts) == decoded, "union event raw table round-trip differs")
    require(recompress_wrapper(decoded, _header) == packed, "union event packed round-trip differs")
    actual = {
        index
        for index, text in enumerate(table.texts)
        if text != baseline.table.texts[index]
    }
    require(actual == set(replacements), "union event changed scope differs")
    for entry_id, text in replacements.items():
        require(table.texts[entry_id] == text, f"union event text differs: {entry_id}")
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
    }


def prepare_candidate() -> CandidateBundle:
    msggame_baselines = {
        BASE_MSGGAME: load_msggame_baseline(BASE_MSGGAME),
        PK_MSGGAME: load_msggame_baseline(PK_MSGGAME),
    }
    event_baseline = load_event_baseline()

    replacements: dict[str, dict[Any, Any]] = {resource: {} for resource in RESOURCE_ORDER}
    provenance: dict[str, dict[Any, str]] = {resource: {} for resource in RESOURCE_ORDER}
    bindings: list[ComponentBinding] = []
    for spec in COMPONENT_SPECS:
        binding, differences = read_component(spec, msggame_baselines, event_baseline)
        register_replacements(replacements, provenance, binding, differences)
        bindings.append(binding)

    require(len(bindings) == 6, "component count differs")
    require(sum(binding.changed_record_count for binding in bindings) == UNION_TOTAL_COUNT, "component total differs")
    for resource, expected_count in UNION_COUNTS.items():
        require(len(replacements[resource]) == expected_count, f"union replacement count differs: {resource}")

    files = {
        BASE_MSGGAME: rebuild_msggame_union(BASE_MSGGAME, msggame_baselines[BASE_MSGGAME], replacements[BASE_MSGGAME]),
        PK_MSGGAME: rebuild_msggame_union(PK_MSGGAME, msggame_baselines[PK_MSGGAME], replacements[PK_MSGGAME]),
        PK_EVENT: rebuild_event_union(event_baseline, replacements[PK_EVENT]),
    }
    union_coordinates = {resource: tuple(sorted(replacements[resource])) for resource in RESOURCE_ORDER}

    audit = {
        "schema": "nobu16.kr.pc-static-composite-wave52-audit.v1",
        "source_policy": {
            "platform": "Steam PC",
            "w45_baseline_required": True,
            "switch_korean_input": "forbidden",
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "pinned_helpers_sha256": {
            "wave27_msggame": W27_HELPER_SHA256,
            "nobu16_lz4": LZ4_HELPER_SHA256,
            "nobu16_msg_table": TABLE_HELPER_SHA256,
        },
        "w45_inputs": {resource: profile_dict(profile) for resource, profile in W45_PROFILES.items()},
        "components": [binding_dict(binding) for binding in bindings],
        "excluded_component_workstreams": ["pc_dialogue_runtime_repair_wave46_v1"],
        "selection_rule": (
            "Only the exact records changed by the six named static candidate outputs are merged. "
            "Runtime, display, and other held rows absent from those outputs cannot enter this union."
        ),
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
        "schema": "nobu16.kr.pc-static-composite-wave52-manifest.v1",
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
        "component_count": len(bindings),
        "component_changed_record_count": sum(binding.changed_record_count for binding in bindings),
        "excluded_component_workstreams": ["pc_dialogue_runtime_repair_wave46_v1"],
        "switch_korean_input": "forbidden",
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
        "audit_sha256": sha256_bytes(canonical_json(audit)),
    }
    return CandidateBundle(files, audit, manifest, union_coordinates, tuple(bindings))


def write_candidate(bundle: CandidateBundle) -> Path:
    output = require_private(TMP_ROOT / "candidate", "candidate output")
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
            require_private(output, "existing candidate output")
            shutil.rmtree(output)
        os.replace(stage, output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return output


def verify_private() -> dict[str, Any]:
    bundle = prepare_candidate()
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    require(output.is_dir(), "private candidate is absent")
    expected_files = set(RESOURCE_ORDER) | {"audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()}
    require(actual_files == expected_files, "private candidate file set differs")
    for resource, payload in bundle.files.items():
        require((output / Path(resource)).read_bytes() == payload, f"private candidate differs: {resource}")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require(
        (output / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest),
        "private manifest differs",
    )
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "component_count": len(bundle.components),
        "changed_record_count": UNION_TOTAL_COUNT,
        "changed_record_count_by_resource": dict(UNION_COUNTS),
        "steam_game_resource_written": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify-private"))
    args = parser.parse_args(argv)
    if args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        result = {
            "candidate_root": output.relative_to(REPO).as_posix(),
            "component_count": len(bundle.components),
            "changed_record_count": UNION_TOTAL_COUNT,
            "changed_record_count_by_resource": dict(UNION_COUNTS),
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
