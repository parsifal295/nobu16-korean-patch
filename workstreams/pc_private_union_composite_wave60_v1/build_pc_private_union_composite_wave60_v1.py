#!/usr/bin/env python3
"""Build a private W60 union from W59, direct-PC B17, and event Batch D.

W59 already contains opaque MSGGAME control-byte changes.  B17 is therefore
merged as W45-derived literal deltas over W59 rather than as whole records.
The event component is a table-entry overlay and is likewise merged over W59.
This module cannot write Steam files, use Git, or publish a release.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_ROOT = TMP_ROOT / "candidate"
W59_BUILDER = (
    REPO
    / "workstreams"
    / "pc_private_union_composite_wave59_v1"
    / "build_pc_private_union_composite_wave59_v1.py"
)
W58_BUILDER = (
    REPO
    / "workstreams"
    / "pc_private_union_composite_wave58_v1"
    / "build_pc_private_union_composite_wave58_v1.py"
)
BATCH_D_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_reflow_static_batch_d_candidate_v1"
    / "build_pc_event_reflow_static_batch_d_candidate_v1.py"
)
W59_ROOT = REPO / "tmp" / "pc_private_union_composite_wave59_v1" / "candidate"
B17_ROOT = REPO / "tmp" / "pc_b17_direct_static_candidate_v2" / "candidate"
BATCH_D_ROOT = (
    REPO / "tmp" / "pc_event_reflow_static_batch_d_candidate_v1" / "candidate"
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


w59 = load_module("pc_private_union_wave59_for_wave60", W59_BUILDER)
w58 = load_module("pc_private_union_wave58_for_wave60", W58_BUILDER)
batch_d_builder = load_module("pc_event_batch_d_for_wave60", BATCH_D_BUILDER)
core = w58.core

BASE = w59.BASE
PK = w59.PK
MSGDATA = w59.MSGDATA
MSGEV = w59.MSGEV
MSGGAME_RESOURCES = (BASE, PK)
ALL_RESOURCES = (BASE, PK, MSGDATA, MSGEV)
Coord = tuple[int, int, int]
RecordCoord = tuple[int, int]
Profile = w59.Profile
WrapperProfile = w59.WrapperProfile


class UnionError(RuntimeError):
    """Raised when one of the pinned W60 merge contracts drifts."""


@dataclass(frozen=True)
class LiteralDelta:
    source_text: str
    replacement_text: str


@dataclass(frozen=True)
class Bundle:
    outputs: Mapping[str, bytes]
    profiles: Mapping[str, Any]
    b17_deltas: Mapping[str, Mapping[Coord, LiteralDelta]]
    b17_effective: Mapping[str, Mapping[Coord, str]]
    b17_classes: Mapping[str, Mapping[str, tuple[Coord, ...]]]
    event_deltas: Mapping[int, str]
    final_record_counts: Mapping[str, int]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


B17_PROFILES: Mapping[str, Any] = {
    BASE: Profile(
        1_504_406,
        "99B5096FB5532FB50DCD5C04C33E5CC38DA3DC1B959CF68A5547A77FF2C9A76B",
        1_498_504,
        "88091E502BC815E3553106D94C8B53EA2048017A0AAD15EED48582AC45234832",
    ),
    PK: Profile(
        1_806_438,
        "E5029A774F7E287316DBA00A2A516E4A6A8E599673F4FBC44D195EC9EF7900A4",
        1_799_356,
        "D315325FC80D7517826C8B226CB904849C4E6609FB1F966768B1A3B809892780",
    ),
}
B17_WRAPPERS: Mapping[str, Any] = {
    BASE: WrapperProfile("0101F6A1FB7F0000", 1_504_382),
    PK: WrapperProfile("0101442672020000", 1_806_414),
}
B17_COORDINATES: Mapping[str, tuple[Coord, ...]] = {
    BASE: (
        (17, 7, 0),
        (17, 12, 0),
        (17, 19, 0),
        (17, 20, 1),
    ),
    PK: (
        (17, 5, 0), (17, 7, 0), (17, 8, 0), (17, 12, 1),
        (17, 27, 0), (17, 51, 1), (17, 54, 0), (17, 434, 0),
        (17, 504, 0), (17, 659, 1), (17, 660, 1), (17, 661, 1),
        (17, 852, 0), (17, 871, 0), (17, 872, 1), (17, 894, 0),
        (17, 939, 1), (17, 950, 0), (17, 951, 0), (17, 952, 0),
        (17, 956, 1), (17, 957, 1), (17, 958, 1), (17, 971, 0),
        (17, 972, 0), (17, 981, 2), (17, 1004, 0), (17, 1005, 0),
        (17, 1006, 0), (17, 1007, 0), (17, 1020, 1), (17, 1021, 1),
        (17, 1022, 1), (17, 1051, 0), (17, 1065, 0), (17, 1073, 0),
        (17, 1093, 0), (17, 1120, 0), (17, 1132, 0), (17, 1137, 0),
    ),
}

W45_EVENT_PATH = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msgev.bin")
W45_EVENT_PROFILE = Profile(
    994_739,
    "01287E2ECC5328C85348657EFF06553353CB8664B0FB7E1669DB9FC591D53EBE",
    990_828,
    "F3716AB98D60931CEC0FE61976D8DAD386C05B30B7167BD1BDB2CDF02EC55ACC",
)
BATCH_D_PROFILE = Profile(
    994_743,
    "AB7B14FEFE360F6A5C48482A9B4866E8386CDF302FCAFD6C944AE7E9D6926C97",
    990_832,
    "70FAF792D88CA184A9E9A73C3CB825B7B1B872AFEADBA4CFFDD33587058303FB",
)
BATCH_D_IDS = (
    3235, 3238, 3269, 3284, 3847, 3868, 3886, 4016, 4139, 4142,
    4329, 4530, 4752, 4758, 4911, 4929, 5031, 5032, 5092, 5187,
    5209, 5334, 5411, 5515,
)
BATCH_D_HOLDS = (4999,)

# Pinned from the no-write ``profile`` command before private build/test.
EXPECTED_B17_CLASSES: Mapping[str, Mapping[str, tuple[Coord, ...]]] = {
    BASE: {
        "fresh": ((17, 7, 0), (17, 12, 0), (17, 19, 0), (17, 20, 1)),
        "already": (),
        "override": (),
    },
    PK: {
        "fresh": (
            (17, 5, 0), (17, 7, 0), (17, 51, 1), (17, 434, 0),
            (17, 659, 1), (17, 660, 1), (17, 661, 1), (17, 939, 1),
            (17, 956, 1), (17, 957, 1), (17, 958, 1), (17, 971, 0),
            (17, 972, 0), (17, 981, 2), (17, 1004, 0), (17, 1005, 0),
            (17, 1006, 0), (17, 1007, 0), (17, 1020, 1), (17, 1021, 1),
            (17, 1022, 1), (17, 1093, 0),
        ),
        "already": (
            (17, 8, 0), (17, 12, 1), (17, 27, 0), (17, 54, 0),
            (17, 1051, 0), (17, 1065, 0),
        ),
        "override": (
            (17, 504, 0), (17, 852, 0), (17, 871, 0), (17, 872, 1),
            (17, 894, 0), (17, 950, 0), (17, 951, 0), (17, 952, 0),
            (17, 1073, 0), (17, 1120, 0), (17, 1132, 0), (17, 1137, 0),
        ),
    },
}
EXPECTED_W59_TO_W60_RECORDS = {BASE: 4, PK: 34}
EXPECTED_FINAL_RECORD_COUNTS = {BASE: 86, PK: 240, MSGDATA: 4, MSGEV: 115}
EXPECTED_FINAL_TOTAL_RECORDS = 445
EXPECTED_FINAL_PROFILES: Mapping[str, Any] = {
    BASE: Profile(
        1_504_430,
        "7698CDF79797B62698FBB955B94F24F79D2F873921364D8F32AA870977972A1A",
        1_498_528,
        "D95CF0103E366552F3FCF52EE6ACCDFB50BFD4D31BE130CDC0A5353173D9235D",
    ),
    PK: Profile(
        1_806_325,
        "B0910EA8E18CC525AEE156FA7629E07FF4D300877C7715B676A25637C6BE5E13",
        1_799_244,
        "4E6A8B3E5C232C3F162B6FD1E45D8185027C66089310A6E36514327D87D9C97F",
    ),
    MSGDATA: Profile(
        496_999,
        "34DAAAC9F8AE22445DD580FB5B8182FA9C6CD66C4DA78498E6B20286C5456215",
        495_032,
        "9FB501A16D7DF7D84559612A68775D75B6C1E6C0B853123194B81B7FBA8C7BDC",
    ),
    MSGEV: Profile(
        994_719,
        "664DE71FCC5CBAB45860414EE4DE5DECA721AEE227D9D8EE0EF6F8176BFC5917",
        990_808,
        "87D950696A453382AE8BEAF7D8EBBEE7DD7FAB1C1BA68B3ECB6385FB1FE29CC4",
    ),
}
EXPECTED_FINAL_WRAPPERS: Mapping[str, Any] = {
    BASE: WrapperProfile("0101F6A1FB7F0000", 1_504_406),
    PK: WrapperProfile("0101442672020000", 1_806_301),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise UnionError(message)


def profile(blob: bytes) -> Any:
    return w59.profile(blob)


def profile_dict(value: Any) -> dict[str, Any]:
    return w59.profile_dict(value)


def require_private_component(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = (REPO / "tmp").resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise UnionError(f"{label} is not under private tmp: {resolved}") from exc
    return resolved


def require_private_output(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise UnionError(f"W60 output escapes private tmp: {resolved}") from exc
    return resolved


def parse_table(label: str, blob: bytes) -> tuple[Any, bytes, Any]:
    header, raw = core.decompress_wrapper(blob)
    table = core.parse_message_table(raw)
    require(core.rebuild_message_table(table, table.texts) == raw, f"{label}: table round-trip differs")
    return header, raw, table


def load_w59() -> dict[str, bytes]:
    root = require_private_component(W59_ROOT, "W59")
    require(root.is_dir(), f"W59 candidate missing: {root}")
    blobs: dict[str, bytes] = {}
    for relative in ALL_RESOURCES:
        path = root / relative
        require(path.is_file(), f"W59 resource missing: {relative}")
        blob = path.read_bytes()
        expected = w59.EXPECTED_FINAL_PROFILES[relative]
        wrapper = w59.EXPECTED_FINAL_WRAPPERS.get(relative)
        w59.assert_profile(f"W59 {relative}", blob, expected, wrapper)
        if relative in MSGGAME_RESOURCES:
            w59.assert_archive_parse_roundtrip(f"W59 {relative}", blob)
        else:
            parse_table(f"W59 {relative}", blob)
        blobs[relative] = blob
    return blobs


def derive_b17_deltas(w45: Mapping[str, bytes]) -> dict[str, dict[Coord, LiteralDelta]]:
    root = require_private_component(B17_ROOT, "B17 v2")
    require(root.is_dir(), f"B17 v2 candidate missing: {root}")
    result: dict[str, dict[Coord, LiteralDelta]] = {}
    for relative in MSGGAME_RESOURCES:
        candidate = (root / relative).read_bytes()
        w59.assert_profile(
            f"B17 v2 {relative}", candidate, B17_PROFILES[relative], B17_WRAPPERS[relative]
        )
        source_archive = w59.assert_archive_parse_roundtrip(f"W45 B17 {relative}", w45[relative])
        candidate_archive = w59.assert_archive_parse_roundtrip(f"B17 v2 {relative}", candidate)
        w59.assert_same_literal_topology_and_skeleton(
            f"B17 v2 {relative}", source_archive, candidate_archive
        )
        source_texts = w59.literal_texts(source_archive)
        candidate_texts = w59.literal_texts(candidate_archive)
        require(set(source_texts) == set(candidate_texts), f"B17 v2 {relative}: literal topology drift")
        delta = {
            coordinate: LiteralDelta(source_texts[coordinate], candidate_texts[coordinate])
            for coordinate in source_texts
            if source_texts[coordinate] != candidate_texts[coordinate]
        }
        require(tuple(sorted(delta)) == tuple(sorted(B17_COORDINATES[relative])), f"B17 v2 {relative}: target scope drift")
        result[relative] = delta
    return result


def overlay_b17(
    relative: str,
    w45_blob: bytes,
    w59_blob: bytes,
    deltas: Mapping[Coord, LiteralDelta],
) -> tuple[bytes, dict[Coord, str], dict[str, tuple[Coord, ...]]]:
    w45_archive = w59.assert_archive_parse_roundtrip(f"W45 overlay {relative}", w45_blob)
    before_archive = w59.assert_archive_parse_roundtrip(f"W59 overlay {relative}", w59_blob)
    w45_texts = w59.literal_texts(w45_archive)
    before_texts = w59.literal_texts(before_archive)
    classes: dict[str, list[Coord]] = {"fresh": [], "already": [], "override": []}
    effective: dict[Coord, str] = {}
    for coordinate, delta in sorted(deltas.items()):
        require(w45_texts[coordinate] == delta.source_text, f"B17 source drift: {relative} {coordinate}")
        current = before_texts[coordinate]
        if current == delta.replacement_text:
            classes["already"].append(coordinate)
        elif current == delta.source_text:
            classes["fresh"].append(coordinate)
            effective[coordinate] = delta.replacement_text
        else:
            classes["override"].append(coordinate)
            effective[coordinate] = delta.replacement_text
    frozen = {name: tuple(values) for name, values in classes.items()}
    if EXPECTED_B17_CLASSES is not None:
        require(frozen == EXPECTED_B17_CLASSES[relative], f"B17 class drift: {relative}")
    output = w59.rebuild_packed_with_literals(w59_blob, effective)
    w59.assert_same_literal_topology_and_skeleton(
        f"W59-to-W60 {relative}", before_archive,
        w59.assert_archive_parse_roundtrip(f"W60 {relative}", output),
    )
    return output, effective, frozen


def derive_batch_d_deltas(w59_event: bytes) -> tuple[dict[int, str], bytes]:
    require(W45_EVENT_PATH.is_file(), f"W45 event missing: {W45_EVENT_PATH}")
    w45_blob = W45_EVENT_PATH.read_bytes()
    w59.assert_profile("W45 event", w45_blob, W45_EVENT_PROFILE, None)
    root = require_private_component(BATCH_D_ROOT, "event Batch D")
    candidate_path = root / MSGEV
    require(candidate_path.is_file(), f"event Batch D output missing: {candidate_path}")
    candidate = candidate_path.read_bytes()
    w59.assert_profile("event Batch D", candidate, BATCH_D_PROFILE, None)
    _w45_header, _w45_raw, w45_table = parse_table("W45 event", w45_blob)
    _candidate_header, _candidate_raw, candidate_table = parse_table("event Batch D", candidate)
    require(len(w45_table.texts) == len(candidate_table.texts), "event Batch D: record topology drift")
    delta = {
        entry_id: candidate_table.texts[entry_id]
        for entry_id, text in enumerate(w45_table.texts)
        if text != candidate_table.texts[entry_id]
    }
    require(tuple(sorted(delta)) == BATCH_D_IDS, f"event Batch D: target IDs drift: {sorted(delta)}")
    for entry_id, target in delta.items():
        source = w45_table.texts[entry_id]
        require(source.count("\n") == 0 and target.count("\n") == 1, f"event Batch D LF drift: {entry_id}")
        require(
            batch_d_builder.layout_equivalent(source, target),
            f"event Batch D visible text drift: {entry_id}",
        )
    _before_header, _before_raw, before_table = parse_table("W59 event", w59_event)
    require(len(before_table.texts) == len(w45_table.texts), "W59 event topology drift")
    for entry_id in BATCH_D_IDS:
        require(before_table.texts[entry_id] == w45_table.texts[entry_id], f"event Batch D overlap: {entry_id}")
    return delta, w45_blob


def overlay_event(w59_event: bytes, event_deltas: Mapping[int, str]) -> bytes:
    header, _raw, table = parse_table("W59 event overlay", w59_event)
    texts = list(table.texts)
    for entry_id, target in event_deltas.items():
        texts[entry_id] = target
    raw = core.rebuild_message_table(table, tuple(texts))
    output = core.recompress_wrapper(raw, header)
    _output_header, output_raw, output_table = parse_table("W60 event", output)
    require(output_raw == raw, "W60 event raw mismatch")
    changed = {index for index, value in enumerate(table.texts) if value != output_table.texts[index]}
    require(changed == set(event_deltas), f"W60 event target scope drift: {sorted(changed)}")
    return output


def msggame_counts(w45_blob: bytes, output: bytes) -> tuple[int, int]:
    source = w59.assert_archive_parse_roundtrip("W45 final count", w45_blob)
    final = w59.assert_archive_parse_roundtrip("W60 final count", output)
    source_records = w59.archive_records(source)
    final_records = w59.archive_records(final)
    source_texts = w59.literal_texts(source)
    final_texts = w59.literal_texts(final)
    require(set(source_records) == set(final_records), "W60 record topology drift")
    require(set(source_texts) == set(final_texts), "W60 literal topology drift")
    return (
        sum(source_records[key].data != final_records[key].data for key in source_records),
        sum(source_texts[key] != final_texts[key] for key in source_texts),
    )


def event_count(w45_event: bytes, output: bytes) -> int:
    _header, _raw, before = parse_table("W45 event count", w45_event)
    _header, _raw, after = parse_table("W60 event count", output)
    require(len(before.texts) == len(after.texts), "W60 event table topology drift")
    return sum(left != right for left, right in zip(before.texts, after.texts))


def prepare(*, require_output_profiles: bool) -> Bundle:
    w45 = w59.load_w45_sources()
    w59_blobs = load_w59()
    b17_deltas = derive_b17_deltas(w45)
    outputs: dict[str, bytes] = {}
    b17_effective: dict[str, dict[Coord, str]] = {}
    b17_classes: dict[str, dict[str, tuple[Coord, ...]]] = {}
    for relative in MSGGAME_RESOURCES:
        output, effective, classes = overlay_b17(relative, w45[relative], w59_blobs[relative], b17_deltas[relative])
        outputs[relative] = output
        b17_effective[relative] = effective
        b17_classes[relative] = classes
    outputs[MSGDATA] = w59_blobs[MSGDATA]
    event_deltas, w45_event = derive_batch_d_deltas(w59_blobs[MSGEV])
    outputs[MSGEV] = overlay_event(w59_blobs[MSGEV], event_deltas)
    profiles = {relative: profile(blob) for relative, blob in outputs.items()}
    if require_output_profiles:
        require(EXPECTED_FINAL_PROFILES is not None, "W60 profiles are not pinned")
        require(profiles == EXPECTED_FINAL_PROFILES, "W60 output profile drift")
        require(EXPECTED_FINAL_WRAPPERS is not None, "W60 wrappers are not pinned")
        for relative in MSGGAME_RESOURCES:
            require(w59.wrapper_profile(outputs[relative]) == EXPECTED_FINAL_WRAPPERS[relative], f"W60 wrapper drift: {relative}")
    w59_to_w60_records: dict[str, int] = {}
    for relative in MSGGAME_RESOURCES:
        before = w59.assert_archive_parse_roundtrip(f"W59 scope {relative}", w59_blobs[relative])
        after = w59.assert_archive_parse_roundtrip(f"W60 scope {relative}", outputs[relative])
        before_records = w59.archive_records(before)
        after_records = w59.archive_records(after)
        before_texts = w59.literal_texts(before)
        after_texts = w59.literal_texts(after)
        changed_records = {key for key in before_records if before_records[key].data != after_records[key].data}
        expected_records = {(block_id, record_id) for block_id, record_id, _literal in b17_effective[relative]}
        require(changed_records == expected_records, f"W59-to-W60 record scope drift: {relative}")
        changed_literals = {key for key in before_texts if before_texts[key] != after_texts[key]}
        require(changed_literals == set(b17_effective[relative]), f"W59-to-W60 literal scope drift: {relative}")
        w59_to_w60_records[relative] = len(changed_records)
    base_records, base_literals = msggame_counts(w45[BASE], outputs[BASE])
    pk_records, pk_literals = msggame_counts(w45[PK], outputs[PK])
    final_counts = {
        BASE: base_records,
        PK: pk_records,
        MSGDATA: 4,
        MSGEV: event_count(w45_event, outputs[MSGEV]),
    }
    total = sum(final_counts.values())
    if EXPECTED_W59_TO_W60_RECORDS is not None:
        require(w59_to_w60_records == EXPECTED_W59_TO_W60_RECORDS, "W59-to-W60 count drift")
    if EXPECTED_FINAL_RECORD_COUNTS is not None:
        require(final_counts == EXPECTED_FINAL_RECORD_COUNTS, "W60 final record count drift")
    if EXPECTED_FINAL_TOTAL_RECORDS is not None:
        require(total == EXPECTED_FINAL_TOTAL_RECORDS, "W60 final total drift")
    audit = {
        "schema": "nobu16.kr.pc-private-union-composite-wave60-audit.v1",
        "source_policy": {
            "platform": "Steam PC direct W45 only",
            "switch_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "w59_base": {relative: profile_dict(profile(blob)) for relative, blob in w59_blobs.items()},
        "b17_component": {
            "root": B17_ROOT.relative_to(REPO).as_posix(),
            "profiles": {relative: profile_dict(B17_PROFILES[relative]) for relative in MSGGAME_RESOURCES},
            "literal_delta_counts": {relative: len(b17_deltas[relative]) for relative in MSGGAME_RESOURCES},
        },
        "b17_w59_overlay": {
            relative: {
                name: [list(value) for value in b17_classes[relative][name]]
                for name in ("fresh", "already", "override")
            }
            for relative in MSGGAME_RESOURCES
        },
        "event_batch_d": {
            "root": BATCH_D_ROOT.relative_to(REPO).as_posix(),
            "profile": profile_dict(BATCH_D_PROFILE),
            "entry_ids": list(BATCH_D_IDS),
            "hold_ids": list(BATCH_D_HOLDS),
            "w59_overlap_count": 0,
        },
        "w59_to_w60_changed_records": w59_to_w60_records,
        "w45_to_w60_literals": {BASE: base_literals, PK: pk_literals},
        "final_record_counts": final_counts,
        "final_total_records": total,
        "outputs": {relative: profile_dict(profiles[relative]) for relative in ALL_RESOURCES},
    }
    manifest = {
        "schema": "nobu16.kr.pc-private-union-composite-wave60-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {
            relative: {
                "relative": relative,
                "output": profile_dict(profiles[relative]),
                "changed_record_count": final_counts[relative],
            }
            for relative in ALL_RESOURCES
        },
        "final_total_records": total,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }
    return Bundle(outputs, profiles, b17_deltas, b17_effective, b17_classes, event_deltas, final_counts, audit, manifest)


def candidate_root() -> Path:
    return require_private_output(CANDIDATE_ROOT)


def write_candidate(bundle: Bundle) -> Path:
    output = candidate_root()
    require(not output.exists(), f"W60 candidate already exists: {output}")
    staging = require_private_output(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W60 candidate staging already exists: {staging}")
    staging.mkdir(parents=True)
    try:
        for relative, blob in bundle.outputs.items():
            path = staging / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(blob)
        (staging / "audit.v1.json").write_bytes(w59.canonical_json(bundle.audit))
        (staging / "candidate_manifest.v1.json").write_bytes(w59.canonical_json(bundle.manifest))
        os.replace(staging, output)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return output


def verify_private_candidate(bundle: Bundle | None = None) -> dict[str, Any]:
    bundle = bundle or prepare(require_output_profiles=True)
    root = candidate_root()
    require(root.is_dir(), f"W60 candidate missing: {root}")
    expected_files = {"audit.v1.json", "candidate_manifest.v1.json", *ALL_RESOURCES}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W60 candidate file scope drift: {sorted(actual_files)}")
    for relative, blob in bundle.outputs.items():
        require((root / relative).read_bytes() == blob, f"W60 candidate differs: {relative}")
    require((root / "audit.v1.json").read_bytes() == w59.canonical_json(bundle.audit), "W60 audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == w59.canonical_json(bundle.manifest), "W60 manifest differs")
    return {
        "candidate_root": root.relative_to(REPO).as_posix(),
        "final_record_counts": bundle.final_record_counts,
        "final_total_records": sum(bundle.final_record_counts.values()),
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "build_pc_private_union_composite_wave60_v1.py",
        WORKSTREAM / "test_pc_private_union_composite_wave60_v1.py",
        WORKSTREAM / "README_KO.md",
    ):
        require(path.is_file(), f"W60 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W60 trailing whitespace: {path.name}:{number}")


def command_profile() -> int:
    bundle = prepare(require_output_profiles=False)
    print(json.dumps({
        "profiles": {relative: profile_dict(value) for relative, value in bundle.profiles.items()},
        "wrappers": {relative: {
            "prefix_hex": w59.wrapper_profile(bundle.outputs[relative]).prefix_hex,
            "compressed_size": w59.wrapper_profile(bundle.outputs[relative]).compressed_size,
        } for relative in MSGGAME_RESOURCES},
        "b17_classes": {relative: {name: [list(value) for value in bundle.b17_classes[relative][name]] for name in ("fresh", "already", "override")} for relative in MSGGAME_RESOURCES},
        "w59_to_w60_records": {relative: len({(block_id, record_id) for block_id, record_id, _literal in bundle.b17_effective[relative]}) for relative in MSGGAME_RESOURCES},
        "final_record_counts": bundle.final_record_counts,
        "final_total_records": sum(bundle.final_record_counts.values()),
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        return command_profile()
    if command == "build":
        bundle = prepare(require_output_profiles=True)
        write_candidate(bundle)
        print(json.dumps(verify_private_candidate(bundle), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if command == "verify-private":
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    bundle = prepare(require_output_profiles=True)
    source_whitespace_check()
    result = verify_private_candidate(bundle)
    result["private_authoring_whitespace_check"] = "passed"
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
