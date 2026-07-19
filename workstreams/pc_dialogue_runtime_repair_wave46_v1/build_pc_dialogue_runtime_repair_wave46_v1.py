#!/usr/bin/env python3
"""Build a private PC Steam dialogue-runtime repair candidate for Wave 46.

This workstream repairs six physical ``msggame`` records in three paired
families.  It begins only from the exact current Steam PC dialogue baseline,
keeps every literal marker and terminator, removes only the individually
pinned Japanese ``01 43`` inflection spans, and preserves the runtime slot in
the castle-administration family byte-for-byte.  The only writable location is
this workstream's private ``tmp`` candidate directory.
"""

from __future__ import annotations

import argparse
from collections import Counter
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
STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")

BASE_RESOURCE = "MSG/JP/msggame.bin"
PK_RESOURCE = "MSG_PK/JP/msggame.bin"
RESOURCE_PATHS = {
    BASE_RESOURCE: STEAM_ROOT / BASE_RESOURCE,
    PK_RESOURCE: STEAM_ROOT / PK_RESOURCE,
}

# The format/font helper is pinned so a later helper edit cannot silently
# change this candidate's parsing, reassembly, or width calculation.
W27_HELPER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave27_static_quality_v1"
    / "build_pc_dialogue_quality_wave27_static_quality_v1.py"
)
W27_HELPER_SHA256 = "D63EA16EECF77F769C3B4AE21579A6C1227531E7FBDD0C07BB83C3E2B3A41438"

SCHEMA = "nobu16.kr.pc-dialogue-runtime-repair-wave46.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-runtime-repair-wave46-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-runtime-repair-wave46-manifest.v1"
MAX_LINES = 3
MAX_LINE_PX = 912

# This is the current static-safe dialogue baseline, not an older source
# profile.  A candidate refuses to build if either installed packed resource
# has drifted.
INPUT_PROFILES = {
    BASE_RESOURCE: {
        "size": 1_504_410,
        "sha256": "F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB",
    },
    PK_RESOURCE: {
        "size": 1_806_538,
        "sha256": "0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092",
    },
}

# Filled from the deterministic private build below.  Build/verify always
# require these pins; ``derive-pins`` is a diagnostic command only.
TARGET_PROFILES = {
    BASE_RESOURCE: {
        "size": 1_504_354,
        "sha256": "0B5AFDFC8B54FEE826C0923F8A566C34CCBCF6F8857EFA87462EEEB1D572E8A3",
        "raw_size": 1_498_452,
        "raw_sha256": "A6A175CC803654B45A8BDF63EDF11886C46712F2CC3CCDB29C6777CD83B036EC",
    },
    PK_RESOURCE: {
        "size": 1_806_482,
        "sha256": "1C8F404C7D68AA15D93E8260BBFF1578F370EDCA688E5C57700DDAF53EA16F64",
        "raw_size": 1_799_400,
        "raw_sha256": "9AB5CE89D7FEBA9EE1B3B3CE4D2F4AD20CACD93A47C851F83F4569F079454805",
    },
}


class RuntimeRepairError(RuntimeError):
    """Raised when an input, record, opaque contract, or private output drifts."""


@dataclass(frozen=True)
class Removed0143:
    """One exact Japanese inflection command removed from an input record."""

    offset: int
    expected_hex: str

    @property
    def value(self) -> bytes:
        return bytes.fromhex(self.expected_hex)


@dataclass(frozen=True)
class Change:
    family: str
    resource: str
    coordinate: tuple[int, int]
    target_literals: tuple[str, ...]
    current_record_sha256: str
    current_record_size: int
    input_opaque_spans_hex: tuple[str, ...]
    removed_0143: tuple[Removed0143, ...]
    target_opaque_spans_hex: tuple[str, ...]
    preserved_runtime_opaque_hex: tuple[str, ...]
    target_record_sha256: str = ""
    target_record_size: int = 0
    target_line_widths_px: tuple[int, ...] = ()

    @property
    def coordinate_text(self) -> str:
        return f"{self.coordinate[0]}:{self.coordinate[1]}"


@dataclass(frozen=True)
class CandidateBundle:
    packed: Mapping[str, bytes]
    raw: Mapping[str, bytes]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


def removed(offset: int, expected_hex: str) -> Removed0143:
    value = bytes.fromhex(expected_hex)
    if offset < 0 or len(value) != 6 or value[:2] != b"\x01\x43":
        raise ValueError(f"invalid removable 0143 contract: {offset}, {expected_hex}")
    return Removed0143(offset, expected_hex.upper())


# A and B retain their original literal-slot topology even though their
# Japanese grammar bytes are removed.  C deliberately keeps the first opaque
# span after literal 0 (014301000000): it is a runtime slot, not inflection.
CHANGES = (
    Change(
        "difficulty_with_caution",
        BASE_RESOURCE,
        (15, 220),
        ("다소 어려운 일", "입니다.", "\n신중히 판단하", "십시오."),
        "1628EC8185F016AD8E25AE047CAABC79058A6F5AC81AA59EB1C089362B3711C6",
        85,
        ("", "014384040000", "01435A040000", "01438A040000", "014396010000050505"),
        (
            removed(18, "014384040000"),
            removed(40, "01435A040000"),
            removed(60, "01438A040000"),
            removed(76, "014396010000"),
        ),
        ("", "", "", "", "050505"),
        (),
        "329C4D5945D017977FE9A5C9B4CC658E8908FD323229EA5478885C1BE242A662",
        75,
        (504, 480),
    ),
    Change(
        "difficulty_with_caution",
        PK_RESOURCE,
        (15, 223),
        ("다소 어려운 일", "입니다.", "\n신중히 판단하", "십시오."),
        "74B63D4EA8CCB875B34B38834FDE30094E50B4E89896ACF4CA75DA22FF0B78C9",
        85,
        ("", "014390040000", "014366040000", "014396040000", "01439C010000050505"),
        (
            removed(18, "014390040000"),
            removed(40, "014366040000"),
            removed(60, "014396040000"),
            removed(76, "01439C010000"),
        ),
        ("", "", "", "", "050505"),
        (),
        "329C4D5945D017977FE9A5C9B4CC658E8908FD323229EA5478885C1BE242A662",
        75,
        (504, 480),
    ),
    Change(
        "difficulty_short",
        BASE_RESOURCE,
        (15, 270),
        ("다소 어려운 일", "입니다."),
        "4F969D331548C598271C11D764E23ED9D6B3D62CF0D8A70C0DEC2F6270D9EC0A",
        49,
        ("", "014384040000", "01435A040000050505"),
        (removed(18, "014384040000"), removed(40, "01435A040000")),
        ("", "", "050505"),
        (),
        "ECE278D48B4C9CCA20283D0DAAA0A938180AF373D9E5D10F4BEEABD09F1E91B6",
        39,
        (504,),
    ),
    Change(
        "difficulty_short",
        PK_RESOURCE,
        (15, 273),
        ("다소 어려운 일", "입니다."),
        "B12E845B87B1BAA62D6B8C7E93DC0F54C369C32CBA31008E1AC603950F3D6CF4",
        49,
        ("", "014390040000", "014366040000050505"),
        (removed(18, "014390040000"), removed(40, "014366040000")),
        ("", "", "050505"),
        (),
        "ECE278D48B4C9CCA20283D0DAAA0A938180AF373D9E5D10F4BEEABD09F1E91B6",
        39,
        (504,),
    ),
    Change(
        "castle_administration_runtime_slot",
        BASE_RESOURCE,
        (6, 4410),
        (
            "당분간 전투에 나설 성이 아니니\n",
            "의 정무 역량을\n",
            "활용하려는 뜻은 압니다만…",
        ),
        "055EFE07FED37661D19E259A9C620886A7315D9D27C4784EF0E8F455CB953586",
        145,
        ("", "014301000000", "01433C040000", "050505"),
        (removed(126, "01433C040000"),),
        ("", "014301000000", "", "050505"),
        ("014301000000",),
        "6DCA9449A9B9EF1D2DFE13938FF068496370D29E6AB31D10C60366D44D4C3156",
        109,
        (720, 336, 624),
    ),
    Change(
        "castle_administration_runtime_slot",
        PK_RESOURCE,
        (6, 4469),
        (
            "당분간 전투에 나설 성이 아니니\n",
            "의 정무 역량을\n",
            "활용하려는 뜻은 압니다만…",
        ),
        "006E26B485F1D4315EDBB6B7BA8341D5875DF564AB4CC023524D21BDCE971222",
        145,
        ("", "014301000000", "014348040000", "050505"),
        (removed(126, "014348040000"),),
        ("", "014301000000", "", "050505"),
        ("014301000000",),
        "6DCA9449A9B9EF1D2DFE13938FF068496370D29E6AB31D10C60366D44D4C3156",
        109,
        (720, 336, 624),
    ),
)


if len({(change.resource, change.coordinate) for change in CHANGES}) != len(CHANGES):
    raise RuntimeError("Wave 46 resource-qualified coordinates must be unique")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeRepairError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def reject_switch(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    if any("switch" in part.casefold() for part in resolved.parts):
        raise RuntimeRepairError(f"Nintendo Switch path is forbidden: {label}")
    return resolved


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise RuntimeRepairError(f"{label} escapes the private tmp root: {resolved}") from exc
    return resolved


def load_w27() -> Any:
    require(W27_HELPER.is_file(), "Wave 27 format helper is absent")
    require(sha256_path(W27_HELPER) == W27_HELPER_SHA256, "Wave 27 format helper differs")
    spec = importlib.util.spec_from_file_location("wave46_pinned_wave27", W27_HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeRepairError("cannot load the pinned Wave 27 format helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W27 = load_w27()


def opaque_spans_with_offsets(record: Any) -> tuple[tuple[int, bytes], ...]:
    cursor = 0
    spans: list[tuple[int, bytes]] = []
    for literal in W27.parse_record_literals(record):
        spans.append((cursor, record.data[cursor : literal.marker_offset]))
        cursor = literal.marker_end
    spans.append((cursor, record.data[cursor:]))
    return tuple(spans)


def span_hexes(record: Any) -> tuple[str, ...]:
    return tuple(value.hex().upper() for _offset, value in opaque_spans_with_offsets(record))


def commands_0143(record: Any) -> tuple[tuple[int, bytes], ...]:
    commands: list[tuple[int, bytes]] = []
    for span_offset, span in opaque_spans_with_offsets(record):
        for index in range(len(span) - 5):
            if span[index : index + 2] == b"\x01\x43":
                commands.append((span_offset + index, span[index : index + 6]))
    return tuple(commands)


def opcodes_02xx(record: Any) -> tuple[str, ...]:
    """Return opaque two-byte 02xx prefixes, preserving their exact order."""
    values: list[str] = []
    for _offset, span in opaque_spans_with_offsets(record):
        for index in range(len(span) - 1):
            if span[index] == 0x02:
                values.append(span[index : index + 2].hex().upper())
    return tuple(values)


def removal_map(change: Change, record: Any) -> dict[int, bytes]:
    expected = {item.offset: item.value for item in change.removed_0143}
    require(len(expected) == len(change.removed_0143), f"duplicate 0143 offsets: {change.family} {change.coordinate_text}")
    actual = dict(commands_0143(record))
    mismatch = {
        f"0x{offset:X}": {
            "expected": value.hex().upper(),
            "actual": actual.get(offset, b"").hex().upper(),
        }
        for offset, value in expected.items()
        if actual.get(offset) != value
    }
    require(not mismatch, f"0143 removal contract differs: {change.family} {change.coordinate_text}: {mismatch}")
    return expected


def strip_exact_removals(span_offset: int, span: bytes, removals: Mapping[int, bytes]) -> bytes:
    output = bytearray()
    cursor = 0
    while cursor < len(span):
        absolute = span_offset + cursor
        command = removals.get(absolute)
        if command is not None:
            require(span[cursor : cursor + len(command)] == command, f"pinned 0143 shifted at 0x{absolute:X}")
            cursor += len(command)
            continue
        output.append(span[cursor])
        cursor += 1
    return bytes(output)


def validate_target_literal(value: str, label: str) -> None:
    require(value != "", f"empty target literal: {label}")
    encoded = value.encode("utf-16le")
    require(W27.LITERAL_START not in encoded and W27.LITERAL_END not in encoded, f"reserved literal marker: {label}")
    for character in value:
        if ord(character) < 0x20 and character not in "\n\r":
            raise RuntimeRepairError(f"control character in target literal: {label}")


def rebuild_record(change: Change, before: Any) -> bytes:
    literals = W27.literal_texts(before)
    require(len(literals) == len(change.target_literals), f"literal count differs: {change.family} {change.coordinate_text}")
    removals = removal_map(change, before)
    output = bytearray()
    cursor = 0
    for literal, target in zip(W27.parse_record_literals(before), change.target_literals):
        validate_target_literal(target, f"{change.family} {change.coordinate_text}")
        output.extend(strip_exact_removals(cursor, before.data[cursor : literal.marker_offset], removals))
        output.extend(W27.LITERAL_START)
        output.extend(target.encode("utf-16le"))
        output.extend(W27.LITERAL_END)
        cursor = literal.marker_end
    output.extend(strip_exact_removals(cursor, before.data[cursor:], removals))
    return bytes(output)


def expected_remaining_0143(before: Any, change: Change) -> Counter[bytes]:
    removed_by_offset = {entry.offset: entry.value for entry in change.removed_0143}
    values = Counter(value for offset, value in commands_0143(before) if offset not in removed_by_offset)
    return values


def validate_change(change: Change, before: Any, advance: Any, *, enforce_pins: bool) -> tuple[bytes, dict[str, Any]]:
    require(sha256_bytes(before.data) == change.current_record_sha256, f"current record hash differs: {change.family} {change.coordinate_text}")
    require(len(before.data) == change.current_record_size, f"current record size differs: {change.family} {change.coordinate_text}")
    require(span_hexes(before) == change.input_opaque_spans_hex, f"input opaque spans differ: {change.family} {change.coordinate_text}")
    require(before.data.endswith(W27.RECORD_TERMINATOR), f"input terminator differs: {change.family} {change.coordinate_text}")
    require(len(W27.literal_texts(before)) == len(change.target_literals), f"input marker/literal count differs: {change.family} {change.coordinate_text}")
    before_lf_count = "".join(W27.literal_texts(before)).count("\n")
    target_lf_count = "".join(change.target_literals).count("\n")
    require(before_lf_count == target_lf_count, f"manual LF count differs: {change.family} {change.coordinate_text}")
    layout = W27.line_layout(change.target_literals, advance)
    require(layout["line_count"] <= MAX_LINES, f"more than three lines: {change.family} {change.coordinate_text}")
    require(layout["max_width_px"] <= MAX_LINE_PX, f"font width exceeds {MAX_LINE_PX}px: {change.family} {change.coordinate_text}")
    require(not layout["wide_fallback_codepoints"], f"fallback glyph used: {change.family} {change.coordinate_text}")

    rebuilt = rebuild_record(change, before)
    after = W27.MsgGameRecord(before.block_id, before.record_id, before.relative_offset, rebuilt)
    require(W27.literal_texts(after) == change.target_literals, f"target literal tuple differs: {change.family} {change.coordinate_text}")
    require(len(W27.literal_texts(after)) == len(W27.literal_texts(before)), f"target marker/literal count differs: {change.family} {change.coordinate_text}")
    require(W27.marker_topology(after) == W27.marker_topology(before), f"literal marker topology differs: {change.family} {change.coordinate_text}")
    require(span_hexes(after) == change.target_opaque_spans_hex, f"target opaque spans differ: {change.family} {change.coordinate_text}")
    require(after.data.endswith(W27.RECORD_TERMINATOR), f"target terminator differs: {change.family} {change.coordinate_text}")
    require(opcodes_02xx(after) == opcodes_02xx(before), f"02xx opaque token differs: {change.family} {change.coordinate_text}")
    for runtime_hex in change.preserved_runtime_opaque_hex:
        runtime = bytes.fromhex(runtime_hex)
        require(sum(span.count(runtime) for _offset, span in opaque_spans_with_offsets(before)) == 1, f"input runtime slot differs: {change.family} {change.coordinate_text}")
        require(sum(span.count(runtime) for _offset, span in opaque_spans_with_offsets(after)) == 1, f"runtime slot was not preserved exactly: {change.family} {change.coordinate_text}")
    require(Counter(value for _offset, value in commands_0143(after)) == expected_remaining_0143(before, change), f"unlisted 0143 command changed: {change.family} {change.coordinate_text}")
    if enforce_pins:
        require(sha256_bytes(after.data) == change.target_record_sha256, f"target record hash differs: {change.family} {change.coordinate_text}")
        require(len(after.data) == change.target_record_size, f"target record size differs: {change.family} {change.coordinate_text}")
        require(tuple(layout["line_widths_px"]) == change.target_line_widths_px, f"target font widths differ: {change.family} {change.coordinate_text}")
    return rebuilt, {
        "family": change.family,
        "resource": change.resource,
        "coordinate": change.coordinate_text,
        "current_record_sha256": change.current_record_sha256,
        "current_record_size": change.current_record_size,
        "target_record_sha256": sha256_bytes(after.data),
        "target_record_size": len(after.data),
        "literal_slot_count": len(change.target_literals),
        "input_manual_lf_count": before_lf_count,
        "target_manual_lf_count": target_lf_count,
        "target_visible_text": "".join(change.target_literals),
        "target_literals": list(change.target_literals),
        "target_line_widths_px": list(layout["line_widths_px"]),
        "target_max_line_px": layout["max_width_px"],
        "input_opaque_spans_hex": list(change.input_opaque_spans_hex),
        "removed_0143": [{"offset": entry.offset, "hex": entry.expected_hex} for entry in change.removed_0143],
        "target_opaque_spans_hex": list(change.target_opaque_spans_hex),
        "preserved_runtime_opaque_hex": list(change.preserved_runtime_opaque_hex),
        "input_02xx_opcodes": list(opcodes_02xx(before)),
        "target_02xx_opcodes": list(opcodes_02xx(after)),
        "runtime_display_qa_required": bool(change.preserved_runtime_opaque_hex),
    }


def load_current() -> tuple[dict[str, bytes], dict[str, Mapping[tuple[int, int], Any]]]:
    packed_by_resource: dict[str, bytes] = {}
    records_by_resource: dict[str, Mapping[tuple[int, int], Any]] = {}
    for resource, path in RESOURCE_PATHS.items():
        checked = reject_switch(path, f"Steam input {resource}")
        packed = checked.read_bytes()
        profile = INPUT_PROFILES[resource]
        require(len(packed) == profile["size"] and sha256_bytes(packed) == profile["sha256"], f"current Steam profile differs: {resource}")
        W27.validate_raw_roundtrip(packed, f"current Steam {resource}")
        packed_by_resource[resource] = packed
        records_by_resource[resource] = W27.records_by_coordinate(packed)
    return packed_by_resource, records_by_resource


def build_unpinned() -> CandidateBundle:
    packed_by_resource, records_by_resource = load_current()
    advance, font = W27.load_font_advance()
    replacements: dict[str, dict[tuple[int, int], bytes]] = {resource: {} for resource in RESOURCE_PATHS}
    rows: list[dict[str, Any]] = []
    for change in CHANGES:
        before = records_by_resource[change.resource].get(change.coordinate)
        require(before is not None, f"record is absent: {change.family} {change.coordinate_text}")
        require(change.coordinate not in replacements[change.resource], f"duplicate replacement: {change.resource} {change.coordinate_text}")
        replacement, row = validate_change(change, before, advance, enforce_pins=False)
        replacements[change.resource][change.coordinate] = replacement
        rows.append(row)

    packed_output: dict[str, bytes] = {}
    raw_output: dict[str, bytes] = {}
    for resource, packed in packed_by_resource.items():
        candidate = W27.rebuild_packed_msggame(packed, replacements[resource])
        W27.validate_raw_roundtrip(candidate, f"Wave 46 candidate {resource}")
        _header, raw = W27.decompress_wrapper(candidate)
        before = records_by_resource[resource]
        after = W27.records_by_coordinate(candidate)
        require(set(before) == set(after), f"record topology differs: {resource}")
        changed = {coordinate for coordinate in before if before[coordinate].data != after[coordinate].data}
        expected = {change.coordinate for change in CHANGES if change.resource == resource}
        require(changed == expected, f"changed record scope differs: {resource}")
        packed_output[resource] = candidate
        raw_output[resource] = raw

    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "platform": "Steam PC",
            "switch_korean_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "pinned_format_helper_sha256": W27_HELPER_SHA256,
        "input": INPUT_PROFILES,
        "font": font,
        "changed_record_count": len(CHANGES),
        "runtime_display_qa_required_before_application": True,
        "records": rows,
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {
            resource: {
                "input": INPUT_PROFILES[resource],
                "changed_coordinates": [change.coordinate_text for change in CHANGES if change.resource == resource],
            }
            for resource in RESOURCE_PATHS
        },
        "changed_record_count": len(CHANGES),
        "runtime_display_qa_required_before_application": True,
        "switch_korean_input": "forbidden",
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
    }
    return CandidateBundle(packed_output, raw_output, audit, manifest)


def require_all_target_pins() -> None:
    for resource, profile in TARGET_PROFILES.items():
        require(profile["size"] > 0 and len(profile["sha256"]) == 64, f"target packed profile pin is absent: {resource}")
        require(profile["raw_size"] > 0 and len(profile["raw_sha256"]) == 64, f"target raw profile pin is absent: {resource}")
    for change in CHANGES:
        require(len(change.target_record_sha256) == 64 and change.target_record_size > 0 and change.target_line_widths_px, f"target record pin is absent: {change.family} {change.coordinate_text}")


def prepare_candidate() -> CandidateBundle:
    require_all_target_pins()
    unpinned = build_unpinned()
    advance, _font = W27.load_font_advance()
    for resource, packed in unpinned.packed.items():
        profile = TARGET_PROFILES[resource]
        require(len(packed) == profile["size"] and sha256_bytes(packed) == profile["sha256"], f"target packed profile differs: {resource}")
        raw = unpinned.raw[resource]
        require(len(raw) == profile["raw_size"] and sha256_bytes(raw) == profile["raw_sha256"], f"target raw profile differs: {resource}")
        after = W27.records_by_coordinate(packed)
        for change in (entry for entry in CHANGES if entry.resource == resource):
            before = W27.records_by_coordinate(RESOURCE_PATHS[resource].read_bytes())[change.coordinate]
            validate_change(change, before, advance, enforce_pins=True)
            require(sha256_bytes(after[change.coordinate].data) == change.target_record_sha256, f"output target record differs: {change.family} {change.coordinate_text}")
    audit = dict(unpinned.audit)
    audit["target"] = TARGET_PROFILES
    manifest = dict(unpinned.manifest)
    manifest["resources"] = {
        resource: {
            **manifest["resources"][resource],
            "output": TARGET_PROFILES[resource],
        }
        for resource in RESOURCE_PATHS
    }
    manifest["audit_sha256"] = sha256_bytes(canonical_json(audit))
    return CandidateBundle(unpinned.packed, unpinned.raw, audit, manifest)


def derived_pins() -> dict[str, Any]:
    bundle = build_unpinned()
    rows = {f"{row['resource']}:{row['coordinate']}": row for row in bundle.audit["records"]}
    return {
        "target_profiles": {
            resource: {
                "size": len(packed),
                "sha256": sha256_bytes(packed),
                "raw_size": len(bundle.raw[resource]),
                "raw_sha256": sha256_bytes(bundle.raw[resource]),
            }
            for resource, packed in bundle.packed.items()
        },
        "target_records": {
            key: {
                "sha256": row["target_record_sha256"],
                "size": row["target_record_size"],
                "line_widths_px": row["target_line_widths_px"],
            }
            for key, row in rows.items()
        },
    }


def write_candidate(bundle: CandidateBundle) -> Path:
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT))
    try:
        for resource, packed in bundle.packed.items():
            target = stage / resource
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(packed)
        (stage / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (stage / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        if output.exists():
            shutil.rmtree(output)
        os.replace(stage, output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return output


def verify_private() -> dict[str, Any]:
    bundle = prepare_candidate()
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    for resource, packed in bundle.packed.items():
        path = output / resource
        require(path.is_file() and path.read_bytes() == packed, f"private candidate differs: {resource}")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require((output / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "private manifest differs")
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "changed_record_count": len(CHANGES),
        "runtime_display_qa_required": True,
        "steam_game_resource_written": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify-private", "derive-pins"))
    args = parser.parse_args(argv)
    if args.command == "derive-pins":
        result = derived_pins()
    elif args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        result = {
            "candidate_root": output.relative_to(REPO).as_posix(),
            "changed_record_count": len(CHANGES),
            "runtime_display_qa_required": True,
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
