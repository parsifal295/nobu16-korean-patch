#!/usr/bin/env python3
"""Build the Wave 83 private static-difficulty dialogue successor candidate.

The Base resource starts at the current Steam LF-repair state.  The PK
resource starts only at the exact Wave 82 private candidate, never at the
installed Steam file.  The builder only writes below its own ``tmp`` root.
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
STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")

BASE_RESOURCE = "MSG/JP/msggame.bin"
PK_RESOURCE = "MSG_PK/JP/msggame.bin"
BASE_STEAM_PATH = STEAM_ROOT / BASE_RESOURCE
W82_CANDIDATE_ROOT = REPO / "tmp" / "pc_dialogue_quality_wave82_b15_static_plans_v1" / "candidate"
W82_PK_PATH = W82_CANDIDATE_ROOT / PK_RESOURCE

W27_HELPER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave27_static_quality_v1"
    / "build_pc_dialogue_quality_wave27_static_quality_v1.py"
)
W27_HELPER_SHA256 = "D63EA16EECF77F769C3B4AE21579A6C1227531E7FBDD0C07BB83C3E2B3A41438"

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave83-difficulty-static.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave83-difficulty-static-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave83-difficulty-static-manifest.v1"
MAX_LINES = 3
MAX_LINE_PX = 912

INPUT_PROFILES = {
    BASE_RESOURCE: {
        "kind": "current_steam_after_person_template_lf_repair",
        "path": BASE_STEAM_PATH,
        "size": 1_504_474,
        "sha256": "4E74E5241485E6DEDD290B81781259010D9D49EA9F76DE7166B090657C535374",
        "raw_size": 1_498_572,
        "raw_sha256": "51A0BE049FAA9A752F237AAA26355F68990EF8251E3373DF9301714C20112501",
    },
    PK_RESOURCE: {
        "kind": "wave82_private_candidate",
        "path": W82_PK_PATH,
        "size": 1_806_570,
        "sha256": "3F6F85E503F0FF5FA4E3C53E2B51DE12622E2E9AAE74F0C18A18A4832848C2C7",
        "raw_size": 1_799_488,
        "raw_sha256": "23E709A424D654A43498D748B3CB7BB2E49439A72AEE5B8133423C56CB5732B5",
    },
}
W82_EVIDENCE = {
    "audit.v1.json": {
        "path": W82_CANDIDATE_ROOT / "audit.v1.json",
        "size": 5_944,
        "sha256": "A09EB2C05015F2AD6CB23DBF325642ECCB2C0039F749A8C908A2FB43B2E5EF8F",
    },
    "build_manifest.v1.json": {
        "path": W82_CANDIDATE_ROOT / "build_manifest.v1.json",
        "size": 938,
        "sha256": "BAD75F3FF5765AD37C2CA7F306394A4E57693761818051A2A95E88C0020C876A",
    },
}
TARGET_PROFILES = {
    BASE_RESOURCE: {
        "size": 1_504_454,
        "sha256": "8C30433BC9D7137CC67A427793F6050956FDB7E74843A8FBFE1ED8C233BAD9DF",
        "raw_size": 1_498_552,
        "raw_sha256": "E86DB902EA7948CD5FDEB11F1DC0AEE8C3A6E7392FE5B483D9D72670B82AD236",
    },
    PK_RESOURCE: {
        "size": 1_806_550,
        "sha256": "37782D6E96CC6E9C1D60AF50FA5A68AD7C7CC8BE724CEF85EE2E38F2D074B0A7",
        "raw_size": 1_799_468,
        "raw_sha256": "6089EA69FAF5F8730F665B4A82C79D5F0C1FE0B0993C963244BA578CD8D9C44C",
    },
}

PC_SOURCES = {
    "BASE_JP": (
        Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin"),
        "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
    ),
    "PK_JP": (
        STEAM_ROOT
        / "KR_PATCH_BACKUP"
        / "file_only_transaction"
        / "steam-jp-1.1.7-v0.6.0"
        / "originals"
        / "MSG_PK"
        / "JP"
        / "msggame.bin",
        "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    ),
    "EN": (
        STEAM_ROOT / "MSG_PK/EN/msggame.bin",
        "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    ),
    "SC": (
        STEAM_ROOT / "MSG_PK/SC/msggame.bin",
        "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    ),
    "TC": (
        STEAM_ROOT / "MSG_PK/TC/msggame.bin",
        "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
    ),
}


class Wave83Error(RuntimeError):
    """A predecessor, source anchor, or surgical invariant drifted."""


@dataclass(frozen=True)
class Change:
    name: str
    resource: str
    coordinate: tuple[int, int]
    target_literals: tuple[str, ...]
    current_record_sha256: str
    current_record_size: int
    target_record_sha256: str
    target_record_size: int
    target_line_widths_px: tuple[int, ...]
    input_opaque_spans_hex: tuple[str, ...]
    static_0143_commands: tuple[str, ...]
    source_coordinates: Mapping[str, tuple[int, int]]
    source_record_sha256: Mapping[str, str]


@dataclass(frozen=True)
class CandidateBundle:
    packed: Mapping[str, bytes]
    raw: Mapping[str, bytes]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


CAUTION_SOURCES = {
    "BASE_JP": (15, 220),
    "PK_JP": (15, 223),
    "EN": (15, 223),
    "SC": (15, 223),
    "TC": (15, 223),
}
CAUTION_SOURCE_HASHES = {
    "BASE_JP": "64DC5C9003D4C8289E9139EF95BA199083DE7A9D58A3B0CA4A9DF2A6BC3F3909",
    "PK_JP": "0F2853E04376A509ED0BDA92D4AD1E07DAB756768C97C63CD3DE11C3B923A170",
    "EN": "6E841B430595A95B2D167D891AD9DEE823473EB7E16D01F9001D7316A1BFE11E",
    "SC": "0857CC59462D72E03C2C10CFE2B8D167CCB38590C96D23904A05564564EB9AE6",
    "TC": "3FD99590F2FDCF768FFA074AE280A8EF0F11ABD8D7F90649CD80513F1B23544A",
}
SHORT_SOURCES = {
    "BASE_JP": (15, 270),
    "PK_JP": (15, 273),
    "EN": (15, 273),
    "SC": (15, 273),
    "TC": (15, 273),
}
SHORT_SOURCE_HASHES = {
    "BASE_JP": "5560FC95D81FA1E25C51E3272CF917EE0579C1D937DCA490BE680D1554B32209",
    "PK_JP": "BAE6EC09D2BFAD07BC81600BB610C99E2ED3E50247652FC8B1D8F85F97DE0412",
    "EN": "64E27B27D6BFC7D49E9C9933E1EBF8B76A7514412F9588EF836DA4BA218B74BB",
    "SC": "5E63FE310E4E90F10534FA14F514BA82B311B54FE061E529B553076AF104C32D",
    "TC": "CCA9A48213D94EBF07E197B9EB1BCEE0CC926DD5DE186A2697AFDEF8BD7187C0",
}


CHANGES = (
    Change(
        "difficulty_with_caution_base",
        BASE_RESOURCE,
        (15, 220),
        ("다소 어려운 일", "입니다.", "\n신중히 판단하", "십시오."),
        "1628EC8185F016AD8E25AE047CAABC79058A6F5AC81AA59EB1C089362B3711C6",
        85,
        "329C4D5945D017977FE9A5C9B4CC658E8908FD323229EA5478885C1BE242A662",
        75,
        (504, 480),
        ("", "014384040000", "01435A040000", "01438A040000", "014396010000050505"),
        ("014384040000", "01435A040000", "01438A040000", "014396010000"),
        CAUTION_SOURCES,
        CAUTION_SOURCE_HASHES,
    ),
    Change(
        "difficulty_with_caution_pk",
        PK_RESOURCE,
        (15, 223),
        ("다소 어려운 일", "입니다.", "\n신중히 판단하", "십시오."),
        "74B63D4EA8CCB875B34B38834FDE30094E50B4E89896ACF4CA75DA22FF0B78C9",
        85,
        "329C4D5945D017977FE9A5C9B4CC658E8908FD323229EA5478885C1BE242A662",
        75,
        (504, 480),
        ("", "014390040000", "014366040000", "014396040000", "01439C010000050505"),
        ("014390040000", "014366040000", "014396040000", "01439C010000"),
        CAUTION_SOURCES,
        CAUTION_SOURCE_HASHES,
    ),
    Change(
        "difficulty_short_base",
        BASE_RESOURCE,
        (15, 270),
        ("다소 어려운 일", "입니다."),
        "4F969D331548C598271C11D764E23ED9D6B3D62CF0D8A70C0DEC2F6270D9EC0A",
        49,
        "ECE278D48B4C9CCA20283D0DAAA0A938180AF373D9E5D10F4BEEABD09F1E91B6",
        39,
        (504,),
        ("", "014384040000", "01435A040000050505"),
        ("014384040000", "01435A040000"),
        SHORT_SOURCES,
        SHORT_SOURCE_HASHES,
    ),
    Change(
        "difficulty_short_pk",
        PK_RESOURCE,
        (15, 273),
        ("다소 어려운 일", "입니다."),
        "B12E845B87B1BAA62D6B8C7E93DC0F54C369C32CBA31008E1AC603950F3D6CF4",
        49,
        "ECE278D48B4C9CCA20283D0DAAA0A938180AF373D9E5D10F4BEEABD09F1E91B6",
        39,
        (504,),
        ("", "014390040000", "014366040000050505"),
        ("014390040000", "014366040000"),
        SHORT_SOURCES,
        SHORT_SOURCE_HASHES,
    ),
)


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave83Error(label)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def reject_switch(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    if any("switch" in part.casefold() for part in resolved.parts):
        raise Wave83Error(f"Nintendo Switch path is forbidden: {label}")
    return resolved


def require_under(path: Path, root: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    try:
        resolved.relative_to(root.resolve(strict=True))
    except ValueError as exc:
        raise Wave83Error(f"{label} escapes required root: {resolved}") from exc
    return resolved


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave83Error(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def load_w27() -> Any:
    require(W27_HELPER.is_file(), "Wave 27 helper is absent")
    require(sha256_path(W27_HELPER) == W27_HELPER_SHA256, "pinned Wave 27 helper differs")
    spec = importlib.util.spec_from_file_location("wave83_imported_wave27", W27_HELPER)
    if spec is None or spec.loader is None:
        raise Wave83Error("cannot load pinned Wave 27 helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W27 = load_w27()


def input_path(resource: str) -> Path:
    profile = INPUT_PROFILES[resource]
    path = Path(profile["path"])
    if resource == BASE_RESOURCE:
        return reject_switch(path, "current Steam Base dialogue")
    return require_under(path, W82_CANDIDATE_ROOT, "Wave 82 PK predecessor")


def validate_w82_evidence() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for name, spec in W82_EVIDENCE.items():
        path = require_under(Path(spec["path"]), W82_CANDIDATE_ROOT, f"Wave 82 evidence {name}")
        actual_size = path.stat().st_size
        actual_hash = sha256_path(path)
        require(actual_size == spec["size"] and actual_hash == spec["sha256"], f"Wave 82 evidence differs: {name}")
        result[name] = {"size": actual_size, "sha256": actual_hash}
    return result


def load_predecessors() -> tuple[dict[str, bytes], dict[str, Mapping[tuple[int, int], Any]], dict[str, dict[str, Any]]]:
    validate_w82_evidence()
    packed_by_resource: dict[str, bytes] = {}
    records_by_resource: dict[str, Mapping[tuple[int, int], Any]] = {}
    predecessor_summary: dict[str, dict[str, Any]] = {}
    for resource, profile in INPUT_PROFILES.items():
        path = input_path(resource)
        packed = path.read_bytes()
        require(len(packed) == profile["size"] and sha256_bytes(packed) == profile["sha256"], f"predecessor profile differs: {resource}")
        W27.validate_raw_roundtrip(packed, f"Wave 83 predecessor {resource}")
        _header, raw = W27.decompress_wrapper(packed)
        require(len(raw) == profile["raw_size"] and sha256_bytes(raw) == profile["raw_sha256"], f"predecessor raw profile differs: {resource}")
        packed_by_resource[resource] = packed
        records_by_resource[resource] = W27.records_by_coordinate(packed)
        predecessor_summary[resource] = {
            "kind": profile["kind"],
            "path": path.relative_to(REPO).as_posix() if path.is_relative_to(REPO) else str(path),
            "size": len(packed),
            "sha256": sha256_bytes(packed),
            "raw_size": len(raw),
            "raw_sha256": sha256_bytes(raw),
        }
    return packed_by_resource, records_by_resource, predecessor_summary


def load_source_records() -> tuple[dict[str, Mapping[tuple[int, int], Any]], dict[str, str]]:
    records: dict[str, Mapping[tuple[int, int], Any]] = {}
    hashes: dict[str, str] = {}
    for language, (path, expected_hash) in PC_SOURCES.items():
        checked = reject_switch(path, f"PC {language} source")
        actual_hash = sha256_path(checked)
        require(actual_hash == expected_hash, f"PC {language} source profile differs")
        records[language] = W27.records_by_coordinate(checked.read_bytes())
        hashes[language] = actual_hash
    return records, hashes


def validate_source_anchor(change: Change, sources: Mapping[str, Mapping[tuple[int, int], Any]]) -> dict[str, Any]:
    contexts: dict[str, Any] = {}
    require(set(change.source_coordinates) == set(change.source_record_sha256), f"source anchor map differs: {change.name}")
    for language, coordinate in change.source_coordinates.items():
        record = sources[language].get(coordinate)
        require(record is not None and W27.literal_texts(record), f"source coordinate is absent: {change.name} {language}")
        actual = W27.sha256_bytes(record.data)
        require(actual == change.source_record_sha256[language], f"source record differs: {change.name} {language}")
        contexts[language] = {
            "coordinate": f"{coordinate[0]}:{coordinate[1]}",
            "record_sha256": actual,
            "literal_count": len(W27.literal_texts(record)),
            "visible_text_utf16le_sha256": sha256_bytes("".join(W27.literal_texts(record)).encode("utf-16le")),
        }
    return contexts


def opaque_02xx_prefixes(record: Any) -> tuple[str, ...]:
    values: list[str] = []
    for span in W27.opaque_spans(record):
        for offset in range(len(span) - 1):
            if span[offset] == 0x02:
                values.append(span[offset : offset + 2].hex().upper())
    return tuple(values)


def validate_change(change: Change, before: Any, advance: Any) -> tuple[bytes, dict[str, Any]]:
    require(W27.sha256_bytes(before.data) == change.current_record_sha256, f"current record differs: {change.name}")
    require(len(before.data) == change.current_record_size, f"current record size differs: {change.name}")
    require(before.data.endswith(W27.RECORD_TERMINATOR), f"record terminator differs: {change.name}")
    require(len(W27.literal_texts(before)) == len(change.target_literals), f"literal count differs: {change.name}")
    before_spans = tuple(span.hex().upper() for span in W27.opaque_spans(before))
    require(before_spans == change.input_opaque_spans_hex, f"input opaque spans differ: {change.name}")
    commands = W27.complete_0143_commands(W27.opaque_spans(before))
    require(commands == change.static_0143_commands, f"0143 command set differs: {change.name}")
    require("014301000000" not in commands, f"runtime 0143 slot is forbidden: {change.name}")
    require(not opaque_02xx_prefixes(before), f"02xx opcode is forbidden: {change.name}")
    current_text = "".join(W27.literal_texts(before))
    target_text = "".join(change.target_literals)
    require(current_text.count("\n") == target_text.count("\n"), f"manual line count differs: {change.name}")
    layout = W27.line_layout(change.target_literals, advance)
    require(tuple(layout["line_widths_px"]) == change.target_line_widths_px, f"target line widths differ: {change.name}")
    require(layout["line_count"] <= MAX_LINES and layout["max_width_px"] <= MAX_LINE_PX, f"target exceeds dialogue layout: {change.name}")
    require(not layout["wide_fallback_codepoints"], f"target has fallback glyph: {change.name}")
    rebuilt = W27.rebuild_static_record(before, change.target_literals)
    after = W27.MsgGameRecord(before.block_id, before.record_id, before.relative_offset, rebuilt)
    require(W27.literal_texts(after) == change.target_literals, f"target literals differ: {change.name}")
    require(W27.marker_topology(after) == W27.marker_topology(before), f"marker topology differs: {change.name}")
    require(W27.opaque_spans(after) == W27.stripped_opaque_spans(before), f"opaque mutation differs: {change.name}")
    target_spans = tuple(span.hex().upper() for span in W27.opaque_spans(after))
    require(target_spans == ("",) * len(change.target_literals) + ("050505",), f"target opaque spans differ: {change.name}")
    require(not W27.complete_0143_commands(W27.opaque_spans(after)), f"static 0143 remains: {change.name}")
    require(not opaque_02xx_prefixes(after), f"02xx opcode was introduced: {change.name}")
    require(after.data.endswith(W27.RECORD_TERMINATOR), f"target terminator differs: {change.name}")
    require(W27.sha256_bytes(after.data) == change.target_record_sha256, f"target record hash differs: {change.name}")
    require(len(after.data) == change.target_record_size, f"target record size differs: {change.name}")
    return rebuilt, {
        "name": change.name,
        "resource": change.resource,
        "coordinate": f"{change.coordinate[0]}:{change.coordinate[1]}",
        "current_record_sha256": change.current_record_sha256,
        "target_record_sha256": change.target_record_sha256,
        "current_record_size": change.current_record_size,
        "target_record_size": change.target_record_size,
        "manual_line_count": target_text.count("\n"),
        "target_line_widths_px": list(change.target_line_widths_px),
        "input_opaque_spans_hex": list(change.input_opaque_spans_hex),
        "target_opaque_spans_hex": list(target_spans),
        "removed_static_0143_commands": list(change.static_0143_commands),
        "runtime_0143_slot_present": False,
        "input_02xx_opcodes": [],
        "target_02xx_opcodes": [],
    }


def prepare_candidate() -> CandidateBundle:
    packed_before, records_before, predecessor_summary = load_predecessors()
    sources, source_hashes = load_source_records()
    advance, font = W27.load_font_advance()
    replacements: dict[str, dict[tuple[int, int], bytes]] = {BASE_RESOURCE: {}, PK_RESOURCE: {}}
    rows: list[dict[str, Any]] = []
    for change in CHANGES:
        before = records_before[change.resource].get(change.coordinate)
        require(before is not None, f"predecessor coordinate is absent: {change.name}")
        replacement, row = validate_change(change, before, advance)
        row["pc_source_anchor"] = validate_source_anchor(change, sources)
        replacements[change.resource][change.coordinate] = replacement
        rows.append(row)
    packed_after: dict[str, bytes] = {}
    raw_after: dict[str, bytes] = {}
    non_target_counts: dict[str, int] = {}
    for resource in (BASE_RESOURCE, PK_RESOURCE):
        candidate = W27.rebuild_packed_msggame(packed_before[resource], replacements[resource])
        profile = TARGET_PROFILES[resource]
        require(len(candidate) == profile["size"] and sha256_bytes(candidate) == profile["sha256"], f"target packed profile differs: {resource}")
        W27.validate_raw_roundtrip(candidate, f"Wave 83 private candidate {resource}")
        _header, raw = W27.decompress_wrapper(candidate)
        require(len(raw) == profile["raw_size"] and sha256_bytes(raw) == profile["raw_sha256"], f"target raw profile differs: {resource}")
        after_records = W27.records_by_coordinate(candidate)
        before_records = records_before[resource]
        require(set(before_records) == set(after_records), f"record coordinate set differs: {resource}")
        expected_changed = set(replacements[resource])
        changed = {coordinate for coordinate in before_records if before_records[coordinate].data != after_records[coordinate].data}
        require(changed == expected_changed, f"changed record scope differs: {resource}")
        non_target_count = 0
        for coordinate, before in before_records.items():
            if coordinate in expected_changed:
                continue
            require(before.data == after_records[coordinate].data, f"non-target record changed: {resource} {coordinate}")
            non_target_count += 1
        for change in (item for item in CHANGES if item.resource == resource):
            require(W27.sha256_bytes(after_records[change.coordinate].data) == change.target_record_sha256, f"output record differs: {change.name}")
        packed_after[resource] = candidate
        raw_after[resource] = raw
        non_target_counts[resource] = non_target_count
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "pc_jp_en_sc_tc_only": True,
            "switch_korean_read": False,
            "steam_game_resource_written": False,
            "steam_transaction_capability": "absent",
            "git_operation": "absent",
            "network_operation": "absent",
            "release_operation": "absent",
        },
        "predecessors": predecessor_summary,
        "wave82_evidence": validate_w82_evidence(),
        "pc_source_packed_sha256": source_hashes,
        "font": font,
        "records": rows,
        "changed_record_count": len(CHANGES),
        "non_target_record_counts": non_target_counts,
        "non_target_record_byte_identity": "PASS",
        "target": {
            resource: {
                "size": len(packed_after[resource]),
                "sha256": sha256_bytes(packed_after[resource]),
                "raw_size": len(raw_after[resource]),
                "raw_sha256": sha256_bytes(raw_after[resource]),
            }
            for resource in (BASE_RESOURCE, PK_RESOURCE)
        },
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "predecessors": predecessor_summary,
        "resources": {
            resource: {
                "input": {"size": INPUT_PROFILES[resource]["size"], "sha256": INPUT_PROFILES[resource]["sha256"]},
                "output": {"size": TARGET_PROFILES[resource]["size"], "sha256": TARGET_PROFILES[resource]["sha256"]},
                "changed_coordinates": [f"{change.coordinate[0]}:{change.coordinate[1]}" for change in CHANGES if change.resource == resource],
            }
            for resource in (BASE_RESOURCE, PK_RESOURCE)
        },
        "changed_record_count": len(CHANGES),
        "audit_sha256": sha256_bytes(canonical_json(audit)),
        "switch_korean_input": "forbidden",
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
    }
    return CandidateBundle(packed_after, raw_after, audit, manifest)


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
        (stage / "build_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
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
    require((output / "build_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "private manifest differs")
    return {"candidate_root": output.relative_to(REPO).as_posix(), "changed_record_count": len(CHANGES), "steam_game_resource_written": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify-private"))
    args = parser.parse_args(argv)
    if args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        print(json.dumps({"candidate_root": output.relative_to(REPO).as_posix(), "changed_record_count": len(CHANGES), "steam_game_resource_written": False}, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(json.dumps(verify_private(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
