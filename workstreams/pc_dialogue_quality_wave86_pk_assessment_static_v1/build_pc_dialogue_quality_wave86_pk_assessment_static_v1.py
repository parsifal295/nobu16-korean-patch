#!/usr/bin/env python3
"""Build a private PK outcome-assessment static dialogue candidate.

Wave 86 accepts only the exact Wave 85 private candidate.  It completes the
eight fixed PK block-15 assessment lines whose Korean literals stop before a
terminal Japanese static 0143 inflection command.  This script writes only
under its own private tmp directory; it has no Steam, Git, network, or
release operation.
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

BASE_RESOURCE = "MSG/JP/msggame.bin"
PK_RESOURCE = "MSG_PK/JP/msggame.bin"
RESOURCE_ORDER = (BASE_RESOURCE, PK_RESOURCE)

W85_CANDIDATE_ROOT = REPO / "tmp" / "pc_dialogue_quality_wave85_b2_static_completion_v1" / "candidate"
W27_HELPER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave27_static_quality_v1"
    / "build_pc_dialogue_quality_wave27_static_quality_v1.py"
)
W27_HELPER_SHA256 = "D63EA16EECF77F769C3B4AE21579A6C1227531E7FBDD0C07BB83C3E2B3A41438"

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave86-pk-assessment-static.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave86-pk-assessment-static-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave86-pk-assessment-static-manifest.v1"

# Fixed-person-dialogue MSGGAME baseline.  This is the validated terminal-0143
# route (not the 30px/4-line MS GEV event widget): raw G1N 48px/24px advances,
# at most three lines, and an 888px raw line cap.
MAX_PERSON_DIALOGUE_LINES = 3
MAX_PERSON_DIALOGUE_RAW_LINE_PX = 888
RAW_G1N_FULL_WIDTH_ADVANCE = 48

INPUT_PROFILES: Mapping[str, Mapping[str, Any]] = {
    BASE_RESOURCE: {
        "kind": "wave85_private_candidate_byte_identical",
        "path": W85_CANDIDATE_ROOT / BASE_RESOURCE,
        "size": 1_504_458,
        "sha256": "27C0D9A5FEE6D212105EE6E6BA14F5DF7B653C0073DBF80AAEBB697D34CC51B2",
        "raw_size": 1_498_556,
        "raw_sha256": "213BA9519E7E3C4B89BA300AB110CBFB3544FAE0407F2CF66906157761C3FDC1",
    },
    PK_RESOURCE: {
        "kind": "wave85_private_candidate_byte_identical_from_wave83",
        "path": W85_CANDIDATE_ROOT / PK_RESOURCE,
        "size": 1_806_550,
        "sha256": "37782D6E96CC6E9C1D60AF50FA5A68AD7C7CC8BE724CEF85EE2E38F2D074B0A7",
        "raw_size": 1_799_468,
        "raw_sha256": "6089EA69FAF5F8730F665B4A82C79D5F0C1FE0B0993C963244BA578CD8D9C44C",
    },
}

W85_EVIDENCE: Mapping[str, Mapping[str, Any]] = {
    "audit.v1.json": {
        "path": W85_CANDIDATE_ROOT / "audit.v1.json",
        "size": 20_736,
        "sha256": "4C93EC63B9FD3919A80AFFCD64FAA8AD9E4E77B6EB1C1E6809E5075D3588AD6D",
    },
    "build_manifest.v1.json": {
        "path": W85_CANDIDATE_ROOT / "build_manifest.v1.json",
        "size": 2_592,
        "sha256": "CD8D8A2AE0BB8EF9E78AF1FEFEFE57ABA6DC8ADC459502B9E0B42CE4816A0AEF",
    },
}

TARGET_PROFILES: Mapping[str, Mapping[str, Any]] = {
    BASE_RESOURCE: {
        "size": 1_504_458,
        "sha256": "27C0D9A5FEE6D212105EE6E6BA14F5DF7B653C0073DBF80AAEBB697D34CC51B2",
        "raw_size": 1_498_556,
        "raw_sha256": "213BA9519E7E3C4B89BA300AB110CBFB3544FAE0407F2CF66906157761C3FDC1",
    },
    PK_RESOURCE: {
        "size": 1_806_590,
        "sha256": "716740362F54231FB92009160E4DDCC6E7BF7E7AE02919954676D6B3E2317A0E",
        "raw_size": 1_799_508,
        "raw_sha256": "2F3B7647E94CE713FA203C71CD84D1B37010AA1569DB12657AE19401966A036E",
    },
}

STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
PC_SOURCE_PROFILES: Mapping[str, tuple[Path, str]] = {
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


class Wave86Error(RuntimeError):
    """Raised if a source, predecessor, or surgical output contract drifts."""


@dataclass(frozen=True)
class Change:
    name: str
    coordinate: tuple[int, int]
    source_jp_literal: str
    target_literal: str
    current_record_sha256: str
    current_record_size: int
    target_record_sha256: str
    target_record_size: int
    target_raw_g1n_line_widths_px: tuple[int, ...]
    input_opaque_spans_hex: tuple[str, str]
    static_0143_commands: tuple[str, ...]
    source_record_sha256: Mapping[str, str]


@dataclass(frozen=True)
class CandidateBundle:
    packed: Mapping[str, bytes]
    raw: Mapping[str, bytes]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


def source_hashes(pk_jp: str, en: str, sc: str, tc: str) -> Mapping[str, str]:
    return {"PK_JP": pk_jp, "EN": en, "SC": sc, "TC": tc}


POSITIVE_SOURCES = source_hashes(
    "2C7FCB316094F13AF854907357C6665CEE8174A8861BCA1234ECB9B635B11233",
    "067DB003509D6A640110749B67C9F1A47B2528CB540E808F2F66AAEFFF5BE55A",
    "7AFB14D3BBE1897C6C9F599E28402AC78CACD74901C7D310BDA1ECDDD5F67F22",
    "9D8880F6F9305ECCC693FD034E1FCC11A7BEC28F6B5A11884EF3F0388610AEA9",
)
ADEQUATE_SOURCES = source_hashes(
    "3120AB76EE47D70883003C694E84C47A318DF4DC4321F0261B33ECCD8CFC3E05",
    "D53F5DAF262D9CB2BBC726237C1E0FEB6E964366FA916EBFB42BDDFE3B664D51",
    "B48FBD190FDF38FD145F73205260D873B409F33118C1A8BF0D15EA93D49B30D6",
    "46DAA5D0BD138DB8F9C4C3E28651B9F9D140C2014BDDAFB9F144C542E03EC7D5",
)


def positive_change(record_id: int) -> Change:
    return Change(
        f"positive_outcome_{record_id}",
        (15, record_id),
        "これならば良き成果が\n得られ",
        "이거라면 좋은 성과를\n얻을 수 있습니다.",
        "EC10F5AC973916ED9FE1F3036072ED6145767E533921994F36FAC02E1A1435F0",
        47,
        "BC81D1FA4B63922E63CCCD6C17F1E05DAC96BD0A6304150202B0314C2DCBA89A",
        53,
        (480, 408),
        ("", "01432A040000050505"),
        ("01432A040000",),
        POSITIVE_SOURCES,
    )


def adequate_change(record_id: int) -> Change:
    return Change(
        f"adequate_outcome_{record_id}",
        (15, record_id),
        "まずまずの成果は\n得られ",
        "그럭저럭의 성과는\n거둘 수 있습니다.",
        "34DD2580115428F34DFDE84F74514BBBFEE2A163668766B973AF1F83A191E30E",
        45,
        "909CAC1C7063583BFF43C99D0FBE1F00F27DDAC360968705112D957980173EC0",
        49,
        (408, 408),
        ("", "01432A040000050505"),
        ("01432A040000",),
        ADEQUATE_SOURCES,
    )


CHANGES = (
    positive_change(231),
    adequate_change(232),
    positive_change(235),
    adequate_change(236),
    positive_change(239),
    adequate_change(240),
    positive_change(243),
    adequate_change(244),
)


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave86Error(label)


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
        raise Wave86Error(f"Nintendo Switch path is forbidden: {label}")
    return resolved


def require_under(path: Path, root: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    root_resolved = root.resolve(strict=True)
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise Wave86Error(f"{label} escapes required root: {resolved}") from exc
    return resolved


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave86Error(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def load_w27() -> Any:
    require(W27_HELPER.is_file(), "Wave 27 helper is absent")
    require(sha256_path(W27_HELPER) == W27_HELPER_SHA256, "pinned Wave 27 helper differs")
    spec = importlib.util.spec_from_file_location("wave86_imported_wave27", W27_HELPER)
    if spec is None or spec.loader is None:
        raise Wave86Error("cannot load pinned Wave 27 helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W27 = load_w27()


def validate_w85_evidence() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for name, profile in W85_EVIDENCE.items():
        path = require_under(Path(profile["path"]), W85_CANDIDATE_ROOT, f"Wave 85 evidence {name}")
        require(path.stat().st_size == profile["size"], f"Wave 85 evidence size differs: {name}")
        actual_hash = sha256_path(path)
        require(actual_hash == profile["sha256"], f"Wave 85 evidence hash differs: {name}")
        result[name] = {"size": path.stat().st_size, "sha256": actual_hash}
    return result


def load_predecessors() -> tuple[dict[str, bytes], dict[str, Mapping[tuple[int, int], Any]], dict[str, Any]]:
    evidence = validate_w85_evidence()
    packed_by_resource: dict[str, bytes] = {}
    records_by_resource: dict[str, Mapping[tuple[int, int], Any]] = {}
    summary: dict[str, Any] = {}
    for resource in RESOURCE_ORDER:
        profile = INPUT_PROFILES[resource]
        path = require_under(Path(profile["path"]), W85_CANDIDATE_ROOT, f"Wave 85 predecessor {resource}")
        packed = path.read_bytes()
        require(len(packed) == profile["size"], f"predecessor size differs: {resource}")
        require(sha256_bytes(packed) == profile["sha256"], f"predecessor hash differs: {resource}")
        W27.validate_raw_roundtrip(packed, f"Wave 86 predecessor {resource}")
        _header, raw = W27.decompress_wrapper(packed)
        require(len(raw) == profile["raw_size"], f"predecessor raw size differs: {resource}")
        require(sha256_bytes(raw) == profile["raw_sha256"], f"predecessor raw hash differs: {resource}")
        packed_by_resource[resource] = packed
        records_by_resource[resource] = W27.records_by_coordinate(packed)
        summary[resource] = {
            "kind": profile["kind"],
            "path": path.relative_to(REPO).as_posix(),
            "size": len(packed),
            "sha256": sha256_bytes(packed),
            "raw_size": len(raw),
            "raw_sha256": sha256_bytes(raw),
        }
    return packed_by_resource, records_by_resource, {
        "resources": summary,
        "wave85_evidence": evidence,
    }


def load_source_records() -> tuple[dict[str, Mapping[tuple[int, int], Any]], dict[str, str]]:
    records: dict[str, Mapping[tuple[int, int], Any]] = {}
    hashes: dict[str, str] = {}
    for language, (path, expected_hash) in PC_SOURCE_PROFILES.items():
        checked = reject_switch(path, f"PC {language} source")
        actual_hash = sha256_path(checked)
        require(actual_hash == expected_hash, f"PC {language} source profile differs")
        records[language] = W27.records_by_coordinate(checked.read_bytes())
        hashes[language] = actual_hash
    return records, hashes


def opaque_02xx_prefixes(record: Any) -> tuple[str, ...]:
    found: list[str] = []
    for span in W27.opaque_spans(record):
        for index in range(len(span) - 1):
            if span[index] == 0x02:
                found.append(span[index:index + 2].hex().upper())
    return tuple(found)


def static_person_dialogue_layout(value: str, advance: Any) -> dict[str, Any]:
    """Measure fixed MSGGAME person dialogue with its raw-G1N layout contract."""

    reports: list[dict[str, Any]] = []
    fallback: set[str] = set()
    for visible_line in value.split("\n"):
        raw_width = 0
        full_width_count = 0
        half_width_count = 0
        for char in visible_line:
            raw_advance, used_fallback = advance(char)
            if raw_advance == RAW_G1N_FULL_WIDTH_ADVANCE:
                full_width_count += 1
            elif raw_advance == RAW_G1N_FULL_WIDTH_ADVANCE // 2:
                half_width_count += 1
            else:
                raise Wave86Error(f"unexpected G1N advance U+{ord(char):04X}: {raw_advance}")
            raw_width += raw_advance
            if used_fallback:
                fallback.add(f"U+{ord(char):04X}")
        reports.append(
            {
                "display_string": visible_line,
                "raw_g1n_width_px": raw_width,
                "static_person_dialogue_width_px": raw_width,
                "full_width_character_count": full_width_count,
                "half_width_character_count": half_width_count,
                "exceeds_static_person_dialogue_width": (
                    raw_width > MAX_PERSON_DIALOGUE_RAW_LINE_PX
                ),
            }
        )
    return {
        "line_count": len(reports),
        "raw_g1n_line_widths_px": tuple(row["raw_g1n_width_px"] for row in reports),
        "static_person_dialogue_line_widths_px": tuple(
            row["static_person_dialogue_width_px"] for row in reports
        ),
        "max_static_person_dialogue_width_px": max(
            (row["static_person_dialogue_width_px"] for row in reports),
            default=0,
        ),
        "any_static_person_dialogue_line_exceeds_888px": any(
            row["exceeds_static_person_dialogue_width"] for row in reports
        ),
        "wide_fallback_codepoints": tuple(sorted(fallback)),
        "lines": tuple(reports),
    }


def validate_source_anchor(change: Change, sources: Mapping[str, Mapping[tuple[int, int], Any]]) -> dict[str, Any]:
    require(set(change.source_record_sha256) == set(PC_SOURCE_PROFILES), f"source hash scope differs: {change.name}")
    result: dict[str, Any] = {}
    for language in PC_SOURCE_PROFILES:
        record = sources[language].get(change.coordinate)
        require(record is not None, f"source coordinate is absent: {change.name} {language}")
        actual_hash = W27.sha256_bytes(record.data)
        require(actual_hash == change.source_record_sha256[language], f"source record differs: {change.name} {language}")
        literals = W27.literal_texts(record)
        require(len(literals) == 1 and literals[0], f"source literal topology differs: {change.name} {language}")
        if language == "PK_JP":
            require(literals == (change.source_jp_literal,), f"PK Japanese literal differs: {change.name}")
        result[language] = {
            "coordinate": f"{change.coordinate[0]}:{change.coordinate[1]}",
            "record_sha256": actual_hash,
            "visible_text_utf16le_sha256": sha256_bytes(literals[0].encode("utf-16le")),
            "visible_literal": literals[0],
        }
    return result


def validate_change(change: Change, before: Any, advance: Any) -> tuple[bytes, dict[str, Any]]:
    require(W27.sha256_bytes(before.data) == change.current_record_sha256, f"current record hash differs: {change.name}")
    require(len(before.data) == change.current_record_size, f"current record size differs: {change.name}")
    require(before.data.endswith(W27.RECORD_TERMINATOR), f"terminator differs: {change.name}")
    require(len(W27.literal_texts(before)) == 1, f"literal count differs: {change.name}")
    require(
        tuple(span.hex().upper() for span in W27.opaque_spans(before)) == change.input_opaque_spans_hex,
        f"input opaque spans differ: {change.name}",
    )
    commands = W27.complete_0143_commands(W27.opaque_spans(before))
    require(commands == change.static_0143_commands, f"static 0143 command set differs: {change.name}")
    require("014301000000" not in commands, f"runtime 0143 slot is forbidden: {change.name}")
    require(not opaque_02xx_prefixes(before), f"02xx opcode is forbidden: {change.name}")
    spans = W27.opaque_spans(before)
    require(
        W27.strip_complete_0143(spans[-1]) == W27.RECORD_TERMINATOR
        and all(not W27.complete_0143_commands((span,)) for span in spans[:-1]),
        f"static 0143 must be terminal-only: {change.name}",
    )

    before_text = W27.literal_texts(before)[0]
    require(before_text.count("\n") == change.target_literal.count("\n") == 1, f"two-line topology differs: {change.name}")
    layout = static_person_dialogue_layout(change.target_literal, advance)
    require(
        tuple(layout["raw_g1n_line_widths_px"]) == change.target_raw_g1n_line_widths_px,
        f"target raw G1N width differs: {change.name}",
    )
    require(
        layout["line_count"] == 2
        and layout["line_count"] <= MAX_PERSON_DIALOGUE_LINES
        and not layout["any_static_person_dialogue_line_exceeds_888px"],
        f"target person-dialogue layout differs: {change.name}",
    )
    require(not layout["wide_fallback_codepoints"], f"target fallback glyph differs: {change.name}")

    rebuilt = W27.rebuild_static_record(before, (change.target_literal,))
    after = W27.MsgGameRecord(before.block_id, before.record_id, before.relative_offset, rebuilt)
    require(W27.literal_texts(after) == (change.target_literal,), f"target literal differs: {change.name}")
    require(W27.marker_topology(after) == W27.marker_topology(before), f"marker topology differs: {change.name}")
    require(W27.opaque_spans(after) == W27.stripped_opaque_spans(before), f"opaque topology differs: {change.name}")
    require(tuple(span.hex().upper() for span in W27.opaque_spans(after)) == ("", "050505"), f"target opaque spans differ: {change.name}")
    require(not W27.complete_0143_commands(W27.opaque_spans(after)), f"static 0143 remains: {change.name}")
    require(not opaque_02xx_prefixes(after), f"02xx opcode introduced: {change.name}")
    require(after.data.endswith(W27.RECORD_TERMINATOR), f"target terminator differs: {change.name}")
    require(W27.sha256_bytes(after.data) == change.target_record_sha256, f"target record hash differs: {change.name}")
    require(len(after.data) == change.target_record_size, f"target record size differs: {change.name}")

    return rebuilt, {
        "name": change.name,
        "resource": PK_RESOURCE,
        "coordinate": f"{change.coordinate[0]}:{change.coordinate[1]}",
        "source_pk_jp_literal": change.source_jp_literal,
        "display_literal": change.target_literal,
        "current_record_sha256": change.current_record_sha256,
        "target_record_sha256": change.target_record_sha256,
        "current_record_size": change.current_record_size,
        "target_record_size": change.target_record_size,
        "display_line_count": layout["line_count"],
        "manual_line_break_count": change.target_literal.count("\n"),
        "target_raw_g1n_line_widths_px": list(layout["raw_g1n_line_widths_px"]),
        "target_static_person_dialogue_line_widths_px": list(
            layout["static_person_dialogue_line_widths_px"]
        ),
        "target_max_static_person_dialogue_width_px": layout[
            "max_static_person_dialogue_width_px"
        ],
        "target_any_static_person_dialogue_line_exceeds_888px": layout[
            "any_static_person_dialogue_line_exceeds_888px"
        ],
        "display_lines": list(layout["lines"]),
        "input_opaque_spans_hex": list(change.input_opaque_spans_hex),
        "target_opaque_spans_hex": ["", "050505"],
        "removed_static_0143_commands": list(change.static_0143_commands),
        "runtime_0143_slot_present": False,
        "input_02xx_opcodes": [],
        "target_02xx_opcodes": [],
    }


def prepare_candidate() -> CandidateBundle:
    packed_before, records_before, predecessor = load_predecessors()
    sources, source_file_hashes = load_source_records()
    advance, font = W27.load_font_advance()
    replacements: dict[tuple[int, int], bytes] = {}
    rows: list[dict[str, Any]] = []

    for change in CHANGES:
        before = records_before[PK_RESOURCE].get(change.coordinate)
        require(before is not None, f"predecessor coordinate is absent: {change.name}")
        replacement, row = validate_change(change, before, advance)
        require(change.coordinate not in replacements, f"duplicate change coordinate: {change.name}")
        replacements[change.coordinate] = replacement
        row["pc_source_anchor"] = validate_source_anchor(change, sources)
        rows.append(row)

    packed_after: dict[str, bytes] = {}
    raw_after: dict[str, bytes] = {}
    non_target_counts: dict[str, int] = {}
    for resource in RESOURCE_ORDER:
        source = packed_before[resource]
        resource_replacements = replacements if resource == PK_RESOURCE else {}
        candidate = W27.rebuild_packed_msggame(source, resource_replacements)
        profile = TARGET_PROFILES[resource]
        require(len(candidate) == profile["size"], f"target packed size differs: {resource}")
        require(sha256_bytes(candidate) == profile["sha256"], f"target packed hash differs: {resource}")
        W27.validate_raw_roundtrip(candidate, f"Wave 86 candidate {resource}")
        _header, raw = W27.decompress_wrapper(candidate)
        require(len(raw) == profile["raw_size"], f"target raw size differs: {resource}")
        require(sha256_bytes(raw) == profile["raw_sha256"], f"target raw hash differs: {resource}")

        before_records = records_before[resource]
        after_records = W27.records_by_coordinate(candidate)
        require(set(before_records) == set(after_records), f"record coordinate set differs: {resource}")
        expected_changed = set(resource_replacements)
        actual_changed = {
            coordinate
            for coordinate, before in before_records.items()
            if before.data != after_records[coordinate].data
        }
        require(actual_changed == expected_changed, f"changed record scope differs: {resource}")
        for coordinate, before in before_records.items():
            if coordinate not in expected_changed:
                require(before.data == after_records[coordinate].data, f"non-target record changed: {resource} {coordinate}")
        if resource == PK_RESOURCE:
            for change in CHANGES:
                require(
                    W27.sha256_bytes(after_records[change.coordinate].data) == change.target_record_sha256,
                    f"output record differs: {change.name}",
                )
        else:
            require(candidate == source, "Base must remain byte-identical from Wave 85")

        packed_after[resource] = candidate
        raw_after[resource] = raw
        non_target_counts[resource] = len(before_records) - len(expected_changed)

    audit: Mapping[str, Any] = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "predecessor": "exact Wave 85 private candidate",
            "pc_pk_jp_en_sc_tc_read": True,
            "switch_korean_read": False,
            "sentence_shortening": "forbidden",
            "manual_line_break_topology": "semantic two-line layout preserved",
            "layout_baseline": {
                "widget": "fixed MSGGAME person dialogue / terminal static 0143",
                "raw_g1n_full_width_advance_px": RAW_G1N_FULL_WIDTH_ADVANCE,
                "raw_g1n_half_width_advance_px": RAW_G1N_FULL_WIDTH_ADVANCE // 2,
                "max_raw_g1n_line_width_px": MAX_PERSON_DIALOGUE_RAW_LINE_PX,
                "max_lines": MAX_PERSON_DIALOGUE_LINES,
                "event_msgev_30px_4line_rule": "not applied",
            },
            "steam_game_resource_written": False,
            "steam_transaction_capability": "absent",
            "git_operation": "absent",
            "network_operation": "absent",
            "release_operation": "absent",
        },
        "predecessor": predecessor,
        "pc_source_packed_sha256": source_file_hashes,
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
            for resource in RESOURCE_ORDER
        },
    }
    manifest: Mapping[str, Any] = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "predecessor": predecessor,
        "resources": {
            resource: {
                "input": {
                    "size": INPUT_PROFILES[resource]["size"],
                    "sha256": INPUT_PROFILES[resource]["sha256"],
                },
                "output": {
                    "size": TARGET_PROFILES[resource]["size"],
                    "sha256": TARGET_PROFILES[resource]["sha256"],
                },
                "changed_coordinates": [
                    f"{change.coordinate[0]}:{change.coordinate[1]}"
                    for change in CHANGES
                    if resource == PK_RESOURCE
                ],
            }
            for resource in RESOURCE_ORDER
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
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "changed_record_count": len(CHANGES),
        "base_byte_identical_from_wave85": True,
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
            "changed_record_count": len(CHANGES),
            "base_byte_identical_from_wave85": True,
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
