#!/usr/bin/env python3
"""Build the private W59 literal-only overlay on the pinned W58 PC union.

W58 already contains opaque MSGGAME runtime/control-byte changes.  Therefore
this builder never copies a component record over W58.  It derives only the
W45-to-component literal deltas, validates their opaque skeletons, then
applies those literals directly to the W58 packed files.

The module has no Steam apply, Git, network, or release operation.  Its sole
write target is ``tmp/pc_private_union_composite_wave59_v1/candidate``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
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
W58_ROOT = (
    REPO / "tmp" / "pc_private_union_composite_wave58_v1" / "candidate"
)
PARSER_DIR = REPO / "workstreams" / "msggame"
if str(PARSER_DIR) not in sys.path:
    sys.path.insert(0, str(PARSER_DIR))

from msggame_format import (  # noqa: E402
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_with_literals,
    rebuild_raw_msggame,
)
from nobu16_lz4 import decompress_wrapper  # noqa: E402


BASE = "MSG/JP/msggame.bin"
PK = "MSG_PK/JP/msggame.bin"
MSGDATA = "MSG_PK/JP/msgdata.bin"
MSGEV = "MSG_PK/JP/msgev.bin"
MSGGAME_RESOURCES = (BASE, PK)
ALL_RESOURCES = (BASE, PK, MSGDATA, MSGEV)
Coord = tuple[int, int, int]
RecordCoord = tuple[int, int]


class UnionError(RuntimeError):
    """Raised when a pinned source, component, or overlay invariant drifts."""


@dataclass(frozen=True)
class Profile:
    packed_size: int
    packed_sha256: str
    raw_size: int
    raw_sha256: str


@dataclass(frozen=True)
class WrapperProfile:
    prefix_hex: str
    compressed_size: int


@dataclass(frozen=True)
class ComponentSpec:
    name: str
    root: Path
    profiles: Mapping[str, Profile]
    wrappers: Mapping[str, WrapperProfile]
    expected_coordinates: Mapping[str, tuple[Coord, ...]]


@dataclass(frozen=True)
class LiteralDelta:
    source_text: str
    replacement_text: str
    component: str


@dataclass(frozen=True)
class Bundle:
    outputs: Mapping[str, bytes]
    output_profiles: Mapping[str, Profile]
    component_deltas: Mapping[str, Mapping[str, Mapping[Coord, LiteralDelta]]]
    merged: Mapping[str, Mapping[Coord, LiteralDelta]]
    effective_overlays: Mapping[str, Mapping[Coord, str]]
    classifications: Mapping[str, Mapping[str, tuple[Coord, ...]]]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


W45_PATHS: Mapping[str, Path] = {
    BASE: Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG\JP\msggame.bin"),
    PK: Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"),
}

W45_PROFILES: Mapping[str, Profile] = {
    BASE: Profile(
        1_504_410,
        "F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB",
        1_498_508,
        "27F2021CED9D7E36B89025EACCF3449D5E424EE5C38C758E5E0995C8234EEB6D",
    ),
    PK: Profile(
        1_806_538,
        "0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092",
        1_799_456,
        "737DAEAB7CC9257BC0F9E15523D01A0C3E807912B8D44393F75512BFB4C2A11E",
    ),
}
W45_WRAPPERS: Mapping[str, WrapperProfile] = {
    BASE: WrapperProfile("0101F6A1FB7F0000", 1_504_386),
    PK: WrapperProfile("0101442672020000", 1_806_514),
}

W58_PROFILES: Mapping[str, Profile] = {
    BASE: Profile(
        1_504_446,
        "F9EFC3744F8FEAA2388EA4025DB87CE50B517AD35D3620C530C0EB9D41354168",
        1_498_544,
        "9ACDCA2A8242A0B97780C6552B955C432D7B32AC258B9C26FC2CCF848E5D5B5D",
    ),
    PK: Profile(
        1_806_402,
        "A5A0865425010F95064CE68EA102EB445A7E7734B47AFFD5A80D10B3F07B7EEF",
        1_799_320,
        "7573CDF410DA1FA64EF718C3E6DFB064A49BA7867FF5A4BCE67FA91607053A47",
    ),
    MSGDATA: Profile(
        496_999,
        "34DAAAC9F8AE22445DD580FB5B8182FA9C6CD66C4DA78498E6B20286C5456215",
        495_032,
        "9FB501A16D7DF7D84559612A68775D75B6C1E6C0B853123194B81B7FBA8C7BDC",
    ),
    MSGEV: Profile(
        994_715,
        "959202F26B8D49A1D554688DA5B6DE29521405E13131DB9BE156C22728FC20A7",
        990_804,
        "DD08819BE730C922707D219F68CFBD6120BEE43B677B578CC3B0B37D3EAFC552",
    ),
}
W58_WRAPPERS: Mapping[str, WrapperProfile] = {
    BASE: WrapperProfile("0101F6A1FB7F0000", 1_504_422),
    PK: WrapperProfile("0101442672020000", 1_806_378),
}

COMPONENTS: tuple[ComponentSpec, ...] = (
    ComponentSpec(
        "b14_static_v1",
        REPO / "tmp" / "pc_b14_static_quality_candidate_v1" / "candidate",
        {
            BASE: Profile(
                1_504_406,
                "1026BA0B43F7CFC172F49D2FB48FF9AC4B3B2511087BF0A2791BD82128B62675",
                1_498_504,
                "86D3D55F53365AE0AA6A75C76955CCC4ABE9C2C1B9922DB0202B3314C45AF69D",
            ),
            PK: Profile(
                1_806_530,
                "268E70CC0040A597E561E57972D7C68AD87329AFB3DBE4D36B62CB42BDEF815F",
                1_799_448,
                "129BF95062EEE0251B9A5A04922AAAA20FF275FA99AC2D5B1CA6A4543DF7EA29",
            ),
        },
        {
            BASE: WrapperProfile("0101F6A1FB7F0000", 1_504_382),
            PK: WrapperProfile("0101442672020000", 1_806_506),
        },
        {
            BASE: ((14, 32, 3), (14, 113, 1), (14, 117, 3)),
            PK: (
                (14, 48, 3),
                (14, 51, 1),
                (14, 156, 1),
                (14, 157, 1),
                (14, 225, 1),
                (14, 226, 1),
                (14, 227, 1),
            ),
        },
    ),
    ComponentSpec(
        "b15_static_v2",
        REPO / "tmp" / "pc_b15_static_quality_candidate_v2" / "candidate",
        {
            BASE: Profile(
                1_504_410,
                "F8D6B86536654D0E0FE8C721F8068964C8F908759CC372E5DDBAB4D8489ACB04",
                1_498_508,
                "F23B2869E9D2526B5C49D809C7489E6B954FC285DBC2E2EBFE91A2E528F5B440",
            ),
            PK: Profile(
                1_806_538,
                "712798DA7ACF7182340BC996359F45F324FF4CE41D41699420819406F1E95EBC",
                1_799_456,
                "03E505277F9CB4D8AE15715742802A4DC6BA782BE410ED7E404E3464D08C6962",
            ),
        },
        {
            BASE: WrapperProfile("0101F6A1FB7F0000", 1_504_386),
            PK: WrapperProfile("0101442672020000", 1_806_514),
        },
        {
            BASE: (
                (15, 1460, 0),
                (15, 1875, 1),
                (15, 1890, 1),
                (15, 2030, 1),
                (15, 2114, 1),
                (15, 2131, 1),
            ),
            PK: (
                (15, 1475, 0),
                (15, 2060, 1),
                (15, 2144, 1),
                (15, 2161, 1),
            ),
        },
    ),
    ComponentSpec(
        "b15_highrisk_static_v1",
        REPO / "tmp" / "pc_b15_highrisk_static_candidate_v1" / "candidate",
        {
            BASE: Profile(
                1_504_402,
                "B69C95ADC52B7261E409B49E7CE907A10049439C629473E6D6DEF31E59DB0952",
                1_498_500,
                "35C566AF0E9F24A04E91D0CDBBD5C8057924BE5D40D1A958ACC5E49D0675F818",
            ),
            PK: Profile(
                1_806_530,
                "D1FFFD772CD35B14113ED18076F572284D2B372234396AC3B9F74ED31FE814F7",
                1_799_448,
                "5D89EFA87DC51E29F91357B1B95C4D74B1CF7E1406024AC893917DA98EC30CD5",
            ),
        },
        {
            BASE: WrapperProfile("0101F6A1FB7F0000", 1_504_378),
            PK: WrapperProfile("0101442672020000", 1_806_506),
        },
        {
            BASE: ((15, 2348, 0),),
            PK: ((15, 2379, 0),),
        },
    ),
)

EXPECTED_W58_RECORD_OVERLAPS: Mapping[str, frozenset[RecordCoord]] = {
    BASE: frozenset(
        {(14, 32), (14, 113), (14, 117), (15, 1875), (15, 1890)}
    ),
    PK: frozenset({(14, 48), (14, 51)}),
}
EXPECTED_W58_LITERAL_OVERRIDES: Mapping[str, frozenset[Coord]] = {
    BASE: frozenset({(14, 32, 3), (14, 117, 3)}),
    PK: frozenset({(14, 48, 3)}),
}
EXPECTED_W58_ALREADY: Mapping[str, frozenset[Coord]] = {
    BASE: frozenset({(14, 113, 1), (15, 1875, 1), (15, 1890, 1)}),
    PK: frozenset({(14, 51, 1)}),
}
EXPECTED_EFFECTIVE_LITERAL_COUNTS = {BASE: 7, PK: 11}
EXPECTED_W58_TO_FINAL_RECORD_COUNTS = {BASE: 7, PK: 11}
EXPECTED_W45_TO_FINAL_RECORD_COUNTS = {BASE: 82, PK: 219}
EXPECTED_W45_TO_FINAL_LITERAL_COUNTS = {BASE: 78, PK: 190}
EXPECTED_FINAL_RECORD_COUNTS = {BASE: 82, PK: 219, MSGDATA: 4, MSGEV: 91}
EXPECTED_FINAL_TOTAL_RECORDS = 396

EXPECTED_FINAL_PROFILES: Mapping[str, Profile] = {
    BASE: Profile(
        1_504_434,
        "10DB93BDB12D708F82EB654FCFEF6D8334C831A141D0BB523E6027F6ED312CC2",
        1_498_532,
        "9CF2E73DA2CF13FD605D4432602DA6081F1E723E2601D909C34D68E08FD125B8",
    ),
    PK: Profile(
        1_806_390,
        "4940E59F0F9D2EA3D18C5090201FFD8BEF2901CEB6F321004F7F4263DB722FDF",
        1_799_308,
        "7F0882875F2BF572D09C3CF21673A726BBCFBF47C44FA4D25380280CD7E2521B",
    ),
    MSGDATA: W58_PROFILES[MSGDATA],
    MSGEV: W58_PROFILES[MSGEV],
}
EXPECTED_FINAL_WRAPPERS: Mapping[str, WrapperProfile] = {
    BASE: WrapperProfile("0101F6A1FB7F0000", 1_504_410),
    PK: WrapperProfile("0101442672020000", 1_806_366),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise UnionError(message)


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def profile(blob: bytes) -> Profile:
    _header, raw = decompress_wrapper(blob)
    return Profile(len(blob), sha256(blob), len(raw), sha256(raw))


def profile_dict(value: Profile) -> dict[str, Any]:
    return {
        "size": value.packed_size,
        "sha256": value.packed_sha256,
        "raw_size": value.raw_size,
        "raw_sha256": value.raw_sha256,
    }


def wrapper_profile(blob: bytes) -> WrapperProfile:
    header, _raw = decompress_wrapper(blob)
    return WrapperProfile(header.prefix.hex().upper(), header.compressed_size)


def assert_profile(
    label: str,
    blob: bytes,
    expected: Profile,
    expected_wrapper: WrapperProfile | None = None,
) -> None:
    actual = profile(blob)
    require(actual == expected, f"{label}: profile hash/size differs: {actual!r}")
    if expected_wrapper is not None:
        actual_wrapper = wrapper_profile(blob)
        require(
            actual_wrapper == expected_wrapper,
            f"{label}: wrapper profile differs: {actual_wrapper!r}",
        )


def require_private_component(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    private_root = (REPO / "tmp").resolve(strict=False)
    try:
        resolved.relative_to(private_root)
    except ValueError as exc:
        raise UnionError(f"{label}: component is not a private tmp candidate") from exc
    return resolved


def require_private_output(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise UnionError(f"W59 output escapes private tmp root: {resolved}") from exc
    return resolved


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def archive_records(archive: Any) -> dict[RecordCoord, Any]:
    return {
        (record.block_id, record.record_id): record
        for block in archive.blocks
        for record in block.records
    }


def literal_texts(archive: Any) -> dict[Coord, str]:
    return {
        (literal.block_id, literal.record_id, literal.literal_id): literal.text
        for block in archive.blocks
        for record in block.records
        for literal in parse_record_literals(record)
    }


def record_skeleton(record: Any) -> bytes:
    """Return the exact record bytecode with only literal text payloads masked."""

    output: list[bytes] = []
    cursor = 0
    for literal in parse_record_literals(record):
        output.append(record.data[cursor : literal.marker_offset])
        output.append(b"<literal-text>")
        cursor = literal.marker_end
    output.append(record.data[cursor:])
    return b"".join(output)


def assert_archive_parse_roundtrip(label: str, packed: bytes) -> Any:
    parsed = parse_packed_msggame(packed)
    _header, raw = decompress_wrapper(packed)
    require(
        rebuild_raw_msggame(parsed.archive) == raw,
        f"{label}: parser raw rebuild differs",
    )
    return parsed.archive


def assert_same_literal_topology_and_skeleton(
    label: str,
    before: Any,
    after: Any,
) -> None:
    before_records = archive_records(before)
    after_records = archive_records(after)
    require(
        set(before_records) == set(after_records),
        f"{label}: record coordinate topology differs",
    )
    for coordinate in sorted(before_records):
        before_record = before_records[coordinate]
        after_record = after_records[coordinate]
        before_literals = parse_record_literals(before_record)
        after_literals = parse_record_literals(after_record)
        require(
            len(before_literals) == len(after_literals),
            f"{label}: literal slot topology differs at {coordinate}",
        )
        require(
            record_skeleton(before_record) == record_skeleton(after_record),
            f"{label}: opaque record bytes differ at {coordinate}",
        )
        for before_literal, after_literal in zip(before_literals, after_literals):
            require(
                before_literal.literal_id == after_literal.literal_id,
                f"{label}: literal id drift at {coordinate}",
            )
            require(
                before_literal.text.count("\n") == after_literal.text.count("\n"),
                f"{label}: manual LF topology drift at "
                f"{coordinate + (before_literal.literal_id,)}",
            )


def load_w45_sources() -> dict[str, bytes]:
    sources: dict[str, bytes] = {}
    for relative in MSGGAME_RESOURCES:
        path = W45_PATHS[relative]
        require(path.is_file(), f"W45 direct PC source missing: {path}")
        blob = path.read_bytes()
        assert_profile(
            f"W45 {relative}", blob, W45_PROFILES[relative], W45_WRAPPERS[relative]
        )
        assert_archive_parse_roundtrip(f"W45 {relative}", blob)
        sources[relative] = blob
    return sources


def load_w58_sources() -> dict[str, bytes]:
    root = require_private_component(W58_ROOT, "W58")
    require(root.is_dir(), f"W58 private union candidate missing: {root}")
    sources: dict[str, bytes] = {}
    for relative in ALL_RESOURCES:
        path = root / relative
        require(path.is_file(), f"W58 resource missing: {relative}")
        blob = path.read_bytes()
        assert_profile(
            f"W58 {relative}",
            blob,
            W58_PROFILES[relative],
            W58_WRAPPERS.get(relative),
        )
        if relative in MSGGAME_RESOURCES:
            assert_archive_parse_roundtrip(f"W58 {relative}", blob)
        sources[relative] = blob
    return sources


def derive_component_literal_delta(
    component: ComponentSpec,
    relative: str,
    source_blob: bytes,
) -> dict[Coord, LiteralDelta]:
    candidate_root = require_private_component(component.root, component.name)
    candidate_path = candidate_root / relative
    require(candidate_path.is_file(), f"{component.name}: missing {relative}")
    candidate_blob = candidate_path.read_bytes()
    assert_profile(
        f"{component.name} {relative}",
        candidate_blob,
        component.profiles[relative],
        component.wrappers[relative],
    )

    source_archive = assert_archive_parse_roundtrip(
        f"W45 source for {component.name} {relative}", source_blob
    )
    candidate_archive = assert_archive_parse_roundtrip(
        f"{component.name} {relative}", candidate_blob
    )
    assert_same_literal_topology_and_skeleton(
        f"{component.name} {relative}", source_archive, candidate_archive
    )

    source_texts = literal_texts(source_archive)
    candidate_texts = literal_texts(candidate_archive)
    require(
        set(source_texts) == set(candidate_texts),
        f"{component.name} {relative}: literal coordinate topology differs",
    )
    delta = {
        coordinate: LiteralDelta(source_texts[coordinate], candidate_texts[coordinate], component.name)
        for coordinate in source_texts
        if source_texts[coordinate] != candidate_texts[coordinate]
    }
    require(
        tuple(sorted(delta)) == tuple(sorted(component.expected_coordinates[relative])),
        f"{component.name} {relative}: literal delta scope differs: {sorted(delta)}",
    )
    return delta


def derive_component_deltas(
    w45_sources: Mapping[str, bytes],
) -> dict[str, dict[str, dict[Coord, LiteralDelta]]]:
    all_deltas: dict[str, dict[str, dict[Coord, LiteralDelta]]] = {}
    for component in COMPONENTS:
        root = require_private_component(component.root, component.name)
        require(root.is_dir(), f"component candidate missing: {component.name}")
        all_deltas[component.name] = {
            relative: derive_component_literal_delta(component, relative, w45_sources[relative])
            for relative in MSGGAME_RESOURCES
        }
    return all_deltas


def merge_component_deltas(
    component_deltas: Mapping[str, Mapping[str, Mapping[Coord, LiteralDelta]]],
) -> dict[str, dict[Coord, LiteralDelta]]:
    merged: dict[str, dict[Coord, LiteralDelta]] = {relative: {} for relative in MSGGAME_RESOURCES}
    for component in COMPONENTS:
        for relative in MSGGAME_RESOURCES:
            for coordinate, incoming in component_deltas[component.name][relative].items():
                existing = merged[relative].get(coordinate)
                require(
                    existing is None,
                    f"component literal target overlaps: {relative} {coordinate} "
                    f"{existing.component if existing else '?'}->{component.name}",
                )
                merged[relative][coordinate] = incoming
    require(
        {relative: len(values) for relative, values in merged.items()}
        == {BASE: 10, PK: 12},
        "merged component literal count differs",
    )
    return merged


def derive_w58_overlay(
    relative: str,
    w45_blob: bytes,
    w58_blob: bytes,
    merged: Mapping[Coord, LiteralDelta],
) -> tuple[dict[Coord, str], dict[str, tuple[Coord, ...]], tuple[RecordCoord, ...]]:
    w45_archive = assert_archive_parse_roundtrip(f"W45 overlay {relative}", w45_blob)
    w58_archive = assert_archive_parse_roundtrip(f"W58 overlay {relative}", w58_blob)
    w45_records = archive_records(w45_archive)
    w58_records = archive_records(w58_archive)
    require(set(w45_records) == set(w58_records), f"W58 {relative}: record topology drift")
    w45_texts = literal_texts(w45_archive)
    w58_texts = literal_texts(w58_archive)
    require(set(w45_texts) == set(w58_texts), f"W58 {relative}: literal topology drift")

    record_overlaps = tuple(
        sorted(
            {
                (block_id, record_id)
                for block_id, record_id, _literal_id in merged
                if w45_records[(block_id, record_id)].data
                != w58_records[(block_id, record_id)].data
            }
        )
    )
    require(
        frozenset(record_overlaps) == EXPECTED_W58_RECORD_OVERLAPS[relative],
        f"W58 {relative}: opaque record overlap differs: {record_overlaps}",
    )

    categories: dict[str, list[Coord]] = {"fresh": [], "already": [], "override": []}
    effective: dict[Coord, str] = {}
    for coordinate, delta in sorted(merged.items()):
        require(
            w45_texts[coordinate] == delta.source_text,
            f"{relative} {coordinate}: component source no longer equals W45",
        )
        current = w58_texts[coordinate]
        if current == delta.replacement_text:
            categories["already"].append(coordinate)
        elif current == delta.source_text:
            categories["fresh"].append(coordinate)
            effective[coordinate] = delta.replacement_text
        else:
            require(
                coordinate in EXPECTED_W58_LITERAL_OVERRIDES[relative],
                f"{relative} {coordinate}: unexpected W58 literal conflict",
            )
            categories["override"].append(coordinate)
            effective[coordinate] = delta.replacement_text

    classified = {key: tuple(values) for key, values in categories.items()}
    require(
        frozenset(classified["override"]) == EXPECTED_W58_LITERAL_OVERRIDES[relative],
        f"{relative}: W58 literal override set differs",
    )
    require(
        frozenset(classified["already"]) == EXPECTED_W58_ALREADY[relative],
        f"{relative}: W58 already-applied set differs",
    )
    require(
        len(effective) == EXPECTED_EFFECTIVE_LITERAL_COUNTS[relative],
        f"{relative}: effective literal overlay count differs",
    )
    return effective, classified, record_overlaps


def assert_w58_overlay_preserves_non_targets(
    relative: str,
    w58_blob: bytes,
    final_blob: bytes,
    effective: Mapping[Coord, str],
) -> dict[str, int]:
    w58_archive = assert_archive_parse_roundtrip(f"W58 verify {relative}", w58_blob)
    final_archive = assert_archive_parse_roundtrip(f"W59 verify {relative}", final_blob)
    assert_same_literal_topology_and_skeleton(
        f"W58-to-W59 {relative}", w58_archive, final_archive
    )
    w58_records = archive_records(w58_archive)
    final_records = archive_records(final_archive)
    w58_texts = literal_texts(w58_archive)
    final_texts = literal_texts(final_archive)
    changed_records = {
        coordinate
        for coordinate in w58_records
        if w58_records[coordinate].data != final_records[coordinate].data
    }
    expected_records = {(block_id, record_id) for block_id, record_id, _literal_id in effective}
    require(
        changed_records == expected_records,
        f"W58-to-W59 {relative}: changed record scope differs: {sorted(changed_records)}",
    )
    changed_literals = {
        coordinate for coordinate in w58_texts if w58_texts[coordinate] != final_texts[coordinate]
    }
    require(
        changed_literals == set(effective),
        f"W58-to-W59 {relative}: changed literal scope differs: {sorted(changed_literals)}",
    )
    for coordinate, before in w58_texts.items():
        if coordinate in effective:
            require(
                final_texts[coordinate] == effective[coordinate],
                f"W58-to-W59 {relative}: target text mismatch at {coordinate}",
            )
        else:
            require(
                final_texts[coordinate] == before,
                f"W58-to-W59 {relative}: non-target literal changed at {coordinate}",
            )
    require(
        len(changed_records) == EXPECTED_W58_TO_FINAL_RECORD_COUNTS[relative],
        f"W58-to-W59 {relative}: changed record count differs",
    )
    return {"record_count": len(changed_records), "literal_count": len(changed_literals)}


def w45_to_final_counts(relative: str, w45_blob: bytes, final_blob: bytes) -> dict[str, int]:
    source_archive = assert_archive_parse_roundtrip(f"W45 final count {relative}", w45_blob)
    final_archive = assert_archive_parse_roundtrip(f"W59 final count {relative}", final_blob)
    source_records = archive_records(source_archive)
    final_records = archive_records(final_archive)
    source_texts = literal_texts(source_archive)
    final_texts = literal_texts(final_archive)
    require(set(source_records) == set(final_records), f"W45-to-W59 {relative}: topology drift")
    require(set(source_texts) == set(final_texts), f"W45-to-W59 {relative}: literal topology drift")
    records = sum(
        source_records[coordinate].data != final_records[coordinate].data
        for coordinate in source_records
    )
    literals = sum(source_texts[coordinate] != final_texts[coordinate] for coordinate in source_texts)
    require(
        records == EXPECTED_W45_TO_FINAL_RECORD_COUNTS[relative],
        f"W45-to-W59 {relative}: final record count differs: {records}",
    )
    require(
        literals == EXPECTED_W45_TO_FINAL_LITERAL_COUNTS[relative],
        f"W45-to-W59 {relative}: final literal count differs: {literals}",
    )
    return {"record_count": records, "literal_count": literals}


def prepare(*, require_output_profiles: bool) -> Bundle:
    """Load pinned W45/W58/components and derive the literal-only W59 output."""

    w45_sources = load_w45_sources()
    w58_sources = load_w58_sources()
    component_deltas = derive_component_deltas(w45_sources)
    merged = merge_component_deltas(component_deltas)

    effective_overlays: dict[str, dict[Coord, str]] = {}
    classifications: dict[str, dict[str, tuple[Coord, ...]]] = {}
    record_overlaps: dict[str, tuple[RecordCoord, ...]] = {}
    outputs: dict[str, bytes] = {}
    for relative in MSGGAME_RESOURCES:
        effective, classified, overlaps = derive_w58_overlay(
            relative, w45_sources[relative], w58_sources[relative], merged[relative]
        )
        effective_overlays[relative] = effective
        classifications[relative] = classified
        record_overlaps[relative] = overlaps
        outputs[relative] = rebuild_packed_with_literals(w58_sources[relative], effective)

    # W59 only overlays MSGGAME.  The two W58 resources remain byte-identical.
    outputs[MSGDATA] = w58_sources[MSGDATA]
    outputs[MSGEV] = w58_sources[MSGEV]
    output_profiles = {relative: profile(blob) for relative, blob in outputs.items()}
    if require_output_profiles:
        require(output_profiles == EXPECTED_FINAL_PROFILES, "W59 final output profiles differ")
        for relative in MSGGAME_RESOURCES:
            require(
                wrapper_profile(outputs[relative]) == EXPECTED_FINAL_WRAPPERS[relative],
                f"W59 {relative}: final wrapper profile differs",
            )

    w58_to_final = {
        relative: assert_w58_overlay_preserves_non_targets(
            relative, w58_sources[relative], outputs[relative], effective_overlays[relative]
        )
        for relative in MSGGAME_RESOURCES
    }
    w45_to_final = {
        relative: w45_to_final_counts(relative, w45_sources[relative], outputs[relative])
        for relative in MSGGAME_RESOURCES
    }
    final_record_counts = {
        BASE: w45_to_final[BASE]["record_count"],
        PK: w45_to_final[PK]["record_count"],
        MSGDATA: 4,
        MSGEV: 91,
    }
    require(final_record_counts == EXPECTED_FINAL_RECORD_COUNTS, "W59 final record scope differs")
    require(
        sum(final_record_counts.values()) == EXPECTED_FINAL_TOTAL_RECORDS,
        "W59 final total record count differs",
    )
    require(outputs[MSGDATA] == w58_sources[MSGDATA], "W59 msgdata changed")
    require(outputs[MSGEV] == w58_sources[MSGEV], "W59 msgev changed")

    component_counts = {
        component.name: {
            relative: len(component_deltas[component.name][relative])
            for relative in MSGGAME_RESOURCES
        }
        for component in COMPONENTS
    }
    audit: dict[str, Any] = {
        "schema": "nobu16.kr.pc-private-union-composite-wave59-audit.v1",
        "source_policy": {
            "platform": "Steam PC direct W45 only",
            "switch_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "w45_sources": {relative: profile_dict(profile(blob)) for relative, blob in w45_sources.items()},
        "w58_base": {relative: profile_dict(profile(blob)) for relative, blob in w58_sources.items()},
        "components": {
            component.name: {
                "candidate_root": component.root.relative_to(REPO).as_posix(),
                "profiles": {
                    relative: profile_dict(component.profiles[relative])
                    for relative in MSGGAME_RESOURCES
                },
                "literal_delta_count": component_counts[component.name],
            }
            for component in COMPONENTS
        },
        "component_literal_conflicts": [],
        "component_literal_conflict_count": 0,
        "w58_record_level_overlaps": {
            relative: [list(value) for value in record_overlaps[relative]]
            for relative in MSGGAME_RESOURCES
        },
        "w58_literal_overlay": {
            relative: {
                key: [list(value) for value in classifications[relative][key]]
                for key in ("fresh", "already", "override")
            }
            for relative in MSGGAME_RESOURCES
        },
        "w58_to_w59": w58_to_final,
        "w45_to_w59": w45_to_final,
        "final_record_counts": final_record_counts,
        "final_total_records": EXPECTED_FINAL_TOTAL_RECORDS,
        "outputs": {relative: profile_dict(output_profiles[relative]) for relative in ALL_RESOURCES},
    }
    manifest: dict[str, Any] = {
        "schema": "nobu16.kr.pc-private-union-composite-wave59-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {
            relative: {
                "relative": relative,
                "output": profile_dict(output_profiles[relative]),
                "changed_record_count": final_record_counts[relative],
            }
            for relative in ALL_RESOURCES
        },
        "final_total_records": EXPECTED_FINAL_TOTAL_RECORDS,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }
    return Bundle(
        outputs,
        output_profiles,
        component_deltas,
        merged,
        effective_overlays,
        classifications,
        audit,
        manifest,
    )


def candidate_root() -> Path:
    return require_private_output(CANDIDATE_ROOT)


def write_candidate(bundle: Bundle) -> Path:
    output = candidate_root()
    require(not output.exists(), f"candidate already exists: {output}")
    staging = require_private_output(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"candidate staging already exists: {staging}")
    staging.mkdir(parents=True)
    for relative, blob in bundle.outputs.items():
        destination = staging / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(blob)
    (staging / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
    (staging / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
    os.replace(staging, output)
    return output


def verify_private_candidate(bundle: Bundle | None = None) -> dict[str, Any]:
    """Require exact private output and re-run literal/opaque preservation proof."""

    bundle = bundle or prepare(require_output_profiles=True)
    root = candidate_root()
    require(root.is_dir(), f"W59 candidate missing: {root}")
    expected_files = {"audit.v1.json", "candidate_manifest.v1.json", *ALL_RESOURCES}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W59 candidate file scope differs: {sorted(actual_files)}")
    for relative, expected in bundle.outputs.items():
        actual = (root / relative).read_bytes()
        require(actual == expected, f"W59 candidate bytes differ: {relative}")
        assert_profile(
            f"W59 candidate {relative}",
            actual,
            EXPECTED_FINAL_PROFILES[relative],
            EXPECTED_FINAL_WRAPPERS.get(relative),
        )
    require(
        (root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit),
        "W59 candidate audit differs",
    )
    require(
        (root / "candidate_manifest.v1.json").read_bytes()
        == canonical_json(bundle.manifest),
        "W59 candidate manifest differs",
    )
    return {
        "candidate_root": root.relative_to(REPO).as_posix(),
        "candidate_only": True,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
        "component_literal_conflicts": 0,
        "w58_to_w59_changed_records": EXPECTED_W58_TO_FINAL_RECORD_COUNTS,
        "final_record_counts": EXPECTED_FINAL_RECORD_COUNTS,
        "final_total_records": EXPECTED_FINAL_TOTAL_RECORDS,
    }


def build_private_candidate() -> dict[str, Any]:
    """Create W59 once or verify the same pinned private candidate if it exists."""

    bundle = prepare(require_output_profiles=True)
    if not candidate_root().exists():
        write_candidate(bundle)
    return verify_private_candidate(bundle)


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "build_pc_private_union_composite_wave59_v1.py",
        WORKSTREAM / "test_pc_private_union_composite_wave59_v1.py",
        WORKSTREAM / "README_KO.md",
    ):
        require(path.is_file(), f"authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        bundle = prepare(require_output_profiles=False)
        print(
            json.dumps(
                {
                    "output_profiles": {
                        relative: profile_dict(value)
                        for relative, value in bundle.output_profiles.items()
                    },
                    "final_record_counts": EXPECTED_FINAL_RECORD_COUNTS,
                    "final_total_records": EXPECTED_FINAL_TOTAL_RECORDS,
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if command == "build":
        result = build_private_candidate()
    elif command == "verify-private":
        result = verify_private_candidate()
    else:
        bundle = prepare(require_output_profiles=True)
        source_whitespace_check()
        result = verify_private_candidate(bundle)
        result["private_authoring_whitespace_check"] = "passed"
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
