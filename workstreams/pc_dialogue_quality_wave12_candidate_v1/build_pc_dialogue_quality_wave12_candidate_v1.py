#!/usr/bin/env python3
"""Build the private PC-only Wave 12 static dialogue candidate.

Wave 12 has one deliberately narrow correction: the same fully static
``13:143:0`` dialogue literal in the Base and PK ``msggame.bin`` resources.
It consumes only the pinned private Wave 9 candidate, writes only below this
workstream's ``tmp`` root, and has no Steam-apply capability.

The wording is anchored to pristine Steam-PC Japanese and PC English. Nintendo
Switch Korean assets are not read or used as references.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
MSGGAME_TOOLS = REPO / "workstreams" / "msggame"
PRIVATE_TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
WAVE9_INPUT_ROOT = (
    REPO / "tmp" / "pc_dialogue_runtime_wave9_candidate_v1" / "candidate-build-1"
)
DEFAULT_FONT_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave12-candidate.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave12-audit.v1"
RESOURCE_PATHS = ("MSG/JP/msggame.bin", "MSG_PK/JP/msggame.bin")
COORDINATE = (13, 143)
RECORD_TERMINATOR = b"\x05\x05\x05"
LITERAL_START = b"\x07\x07\x01"
LITERAL_END = b"\x07\x07\x02"
MAX_LINES = 3
MAX_LINE_PX = 912
EXPECTED_TARGET_LINE_WIDTHS = (672, 912, 888)
FONT_SHA256 = "3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7"
# The second allowed outer profile is a separately staged UI-image/HUD asset
# variant.  Its target-glyph advances were compared with the released profile;
# they are identical for this candidate.  Unknown font profiles still fail.
ALLOWED_FONT_OUTER_SHA256 = frozenset(
    (
        FONT_SHA256,
        "82792DB9EB9B8FB2088A05EF9E66AEC4A5DADB36A919A155155942D270DC2EDB",
    )
)
WIDE_SCRIPT_RE = re.compile(
    r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u9fff\uac00-\ud7a3\uf900-\ufaff]"
)

# These are Wave 9 private-candidate inputs, not implicit reads from Steam.
INPUT_SHA256 = {
    "MSG/JP/msggame.bin": "7EB3F61CE008C02BA48C191CE95E162CD0BCA76CF3E1C45482FC6CE92E6E0492",
    "MSG_PK/JP/msggame.bin": "209B96CADE84D82810A8A79CA362DFA1B6665A8C601D3DB2C3DC0F96986E9930",
}
INPUT_SIZES = {
    "MSG/JP/msggame.bin": 1_504_655,
    "MSG_PK/JP/msggame.bin": 1_806_795,
}
TARGET_SHA256 = {
    "MSG/JP/msggame.bin": "C74A5D2382D809FAF3EF6A78751872C6B99DAC15FCAB21CEA73E0C904736A347",
    "MSG_PK/JP/msggame.bin": "F53BBB2FA4247A0CBAC4538DA84F94376DC40E83A7CF1491D4C1E81C9DE21CBF",
}
TARGET_SIZES = {
    "MSG/JP/msggame.bin": 1_504_643,
    "MSG_PK/JP/msggame.bin": 1_806_783,
}

CURRENT_LITERALS = (
    "당가는 아직 세력이 미약하오.\n"
    "천하를 노리려면 영토를 넓혀 국력을 기르고,\n"
    "전국의 다이묘에게 그 힘을 인정받아야 하오.",
)
TARGET_LITERALS = (
    "우리 가문은 아직 역부족이오.\n"
    "천하를 노리려면 영토를 넓혀 힘을 길러,\n"
    "다이묘 모두에게 힘을 인정받아야 하오.",
)
PRISTINE_PC_JP_LITERALS = (
    "当家はまだまだ力不足\n"
    "天下を狙うには領土を広げて力をつけ\n"
    "全国の大名に力を認めさせる必要があります",
)
PC_EN_LITERALS = (
    "Our clan is still much too weak. We must expand our domain, grow our forces, "
    "and command the respect of every daimyª if we are to take claim of the nation.",
)

INPUT_RECORD_SHA256 = "653E135A85D8122FE183E108AE03A3E7425310F832FAD822CB2277A43156BD41"
INPUT_RECORD_SIZE = 141
TARGET_RECORD_SHA256 = "B55F12653186A806885523B54CF2C4E60AFAD038CE2198B808386E2776985EA6"
TARGET_RECORD_SIZE = 131
INPUT_LITERAL_UTF16LE_SHA256 = "28FBCFC428E1ADBABA0B6B4729C7E93C79565663BE35402BB24CEA6A050F73FF"
TARGET_LITERAL_UTF16LE_SHA256 = "68C7DDDA7121B8F42D43D5E1FC0CCD1A67CFC7FB7EA89721B96E1DE077428864"
EXPECTED_OPAQUE_SPANS_HEX = ("", "050505")
EXPECTED_MARKER_TOPOLOGY_HEX = (("070701", "070702"),)

BASE_PRISTINE_JP_PATH = REPO.parent / "MSG" / "JP" / "msggame.bin"
PK_PRISTINE_JP_PATH = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
    r"\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals"
    r"\MSG_PK\JP\msggame.bin"
)
PC_EN_PATH = REPO.parent / "MSG_PK" / "EN" / "msggame.bin"
PC_REFERENCE_PATHS = {
    "base_pristine_jp": BASE_PRISTINE_JP_PATH,
    "pk_pristine_jp": PK_PRISTINE_JP_PATH,
    "pk_en": PC_EN_PATH,
}
PC_REFERENCE_SHA256 = {
    "base_pristine_jp": "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
    "pk_pristine_jp": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    "pk_en": "14D9A20ECB35F35C91D14947921CF09F5EAF960F8FA4D70F703F2366DB1D13AF",
}
PC_REFERENCE_RECORD_SHA256 = {
    "base_pristine_jp": "4E82412FC2D23B905DDD72D75D26E585603EB4BBB6A3CD51CA3F0542FF338D4B",
    "pk_pristine_jp": "4E82412FC2D23B905DDD72D75D26E585603EB4BBB6A3CD51CA3F0542FF338D4B",
    "pk_en": "026AA02CA4B181A37AD2A621173ABF8BB0AF6A7B635875CE73F0A2CFBCC1C3BA",
}
PC_REFERENCE_LITERAL_UTF16LE_SHA256 = {
    "base_pristine_jp": "1D3C07E302FA702AFB279AE26EA6CE94572A3B06F446784FEE594ACD39BAF635",
    "pk_pristine_jp": "1D3C07E302FA702AFB279AE26EA6CE94572A3B06F446784FEE594ACD39BAF635",
    "pk_en": "22E07CE37625A8BA3F0BD1B8BA3D1D920A197F5246CECEF206D224EFC2FA84C3",
}


class Wave12Error(RuntimeError):
    """A Wave 12 source, preservation, or output contract was violated."""


for module_root in (TOOLS, MSGGAME_TOOLS):
    if str(module_root) not in sys.path:
        sys.path.insert(0, str(module_root))

from nobu16_lz4 import decompress_wrapper, parse_link  # noqa: E402
import validate_g1n_surgical as g1n  # noqa: E402
from msggame_format import (  # noqa: E402
    MsgGameRecord,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_msggame,
    rebuild_record_literals,
)


@dataclass(frozen=True)
class CandidateBundle:
    resources: Mapping[str, bytes]
    input_sha256: Mapping[str, str]
    output_sha256: Mapping[str, str]
    audit: Mapping[str, Any]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def coordinate_text(coordinate: tuple[int, int]) -> str:
    return f"{coordinate[0]}:{coordinate[1]}"


def require_under(path: Path, root: Path, label: str) -> Path:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise Wave12Error(f"{label} escapes {resolved_root}: {resolved_path}") from exc
    return resolved_path


def require_private_output(path: Path, label: str) -> Path:
    return require_under(path, PRIVATE_TMP_ROOT, label)


def reject_switch_path(path: Path, label: str) -> Path:
    resolved = path.resolve()
    if any("switch" in part.casefold() for part in resolved.parts):
        raise Wave12Error(f"Nintendo Switch Korean reference is forbidden: {label}")
    return resolved


def literal_texts(record: MsgGameRecord) -> tuple[str, ...]:
    return tuple(literal.text for literal in parse_record_literals(record))


def opaque_spans(record: MsgGameRecord) -> tuple[bytes, ...]:
    cursor = 0
    spans: list[bytes] = []
    for literal in parse_record_literals(record):
        spans.append(record.data[cursor : literal.marker_offset])
        cursor = literal.marker_end
    spans.append(record.data[cursor:])
    return tuple(spans)


def marker_topology(record: MsgGameRecord) -> tuple[tuple[bytes, bytes], ...]:
    return tuple(
        (
            record.data[literal.marker_offset : literal.marker_offset + len(LITERAL_START)],
            record.data[literal.marker_end - len(LITERAL_END) : literal.marker_end],
        )
        for literal in parse_record_literals(record)
    )


def topology_hex(record: MsgGameRecord) -> tuple[tuple[str, str], ...]:
    return tuple(
        (start.hex().upper(), end.hex().upper())
        for start, end in marker_topology(record)
    )


def records_by_coordinate(packed: bytes) -> dict[tuple[int, int], MsgGameRecord]:
    parsed = parse_packed_msggame(packed)
    return {
        (record.block_id, record.record_id): record
        for block in parsed.archive.blocks
        for record in block.records
    }


def measure_line_layout(
    literals: tuple[str, ...], advance: Callable[[str], tuple[int, bool]]
) -> dict[str, Any]:
    text = "".join(literals)
    widths: list[int] = []
    fallback_codepoints: set[str] = set()
    for line in text.split("\n"):
        width = 0
        for character in line:
            if unicodedata.category(character) == "Cc":
                raise Wave12Error(f"literal contains control U+{ord(character):04X}")
            character_width, fallback = advance(character)
            width += character_width
            if fallback:
                fallback_codepoints.add(f"U+{ord(character):04X}")
        widths.append(width)
    return {
        "line_count": len(widths),
        "line_widths_px": widths,
        "max_width_px": max(widths, default=0),
        "wide_fallback_codepoints": sorted(fallback_codepoints),
    }


def validate_target_layout(layout: Mapping[str, Any]) -> None:
    if layout["line_count"] != MAX_LINES:
        raise Wave12Error(
            f"Wave 12 must retain exactly {MAX_LINES} intentional lines: {layout}"
        )
    if tuple(layout["line_widths_px"]) != EXPECTED_TARGET_LINE_WIDTHS:
        raise Wave12Error(
            "Wave 12 target font widths differ: "
            f"expected {list(EXPECTED_TARGET_LINE_WIDTHS)}, got {layout['line_widths_px']}"
        )
    if layout["max_width_px"] > MAX_LINE_PX:
        raise Wave12Error(f"Wave 12 target exceeds {MAX_LINE_PX}px")
    if layout["wide_fallback_codepoints"]:
        raise Wave12Error(
            "Wave 12 target relies on fallback glyph widths: "
            f"{layout['wide_fallback_codepoints']}"
        )


def load_font_advance(
    font_root: Path,
) -> tuple[Callable[[str], tuple[int, bool]], dict[str, Any]]:
    font_path = (font_root / "RES_JP" / "res_lang.bin").resolve()
    if not font_path.is_file():
        raise Wave12Error(f"PC JP font resource is absent: {font_path}")
    actual_font_sha256 = sha256_path(font_path)
    if actual_font_sha256 not in ALLOWED_FONT_OUTER_SHA256:
        raise Wave12Error(
            "PC JP font hash is not an approved layout profile: "
            f"expected one of {sorted(ALLOWED_FONT_OUTER_SHA256)}, got {actual_font_sha256}"
        )
    try:
        archive = parse_link(font_path.read_bytes())
        _header, raw = decompress_wrapper(archive.entries[6].data)
    except (IndexError, ValueError) as exc:
        raise Wave12Error("PC JP font entry 6 cannot be unpacked") from exc
    with tempfile.TemporaryDirectory(prefix="nobu16_wave12_font_") as directory:
        g1n_path = Path(directory) / "font.g1n"
        g1n_path.write_bytes(raw)
        parsed = g1n.parse_g1n(g1n_path)
    if parsed.structural_errors or not parsed.tables:
        raise Wave12Error("PC JP font entry 6 is structurally invalid")
    table = parsed.tables[0]

    def advance(character: str) -> tuple[int, bool]:
        if len(character) != 1:
            raise Wave12Error("font width requests must contain exactly one character")
        codepoint = ord(character)
        ordinal = table.mapping[codepoint] if codepoint < len(table.mapping) else 0
        if ordinal == 0:
            if WIDE_SCRIPT_RE.fullmatch(character):
                return 48, True
            raise Wave12Error(f"PC JP font lacks glyph U+{codepoint:04X}")
        if ordinal >= len(table.records):
            raise Wave12Error(f"invalid PC JP glyph ordinal for U+{codepoint:04X}")
        glyph = table.records[ordinal]
        if glyph.width != glyph.advance or glyph.advance not in (24, 48):
            raise Wave12Error(f"invalid PC JP glyph metrics for U+{codepoint:04X}")
        return glyph.advance, False

    return advance, {
        "resource": "RES_JP/res_lang.bin",
        "entry": 6,
        "packed_sha256": actual_font_sha256,
        "table_count": len(parsed.tables),
    }


def validate_static_literal_safety(text: str) -> None:
    if text.count("\n") != MAX_LINES - 1:
        raise Wave12Error("Wave 12 target must have exactly two manual line breaks")
    if "\x1b" in text:
        raise Wave12Error("Wave 12 target must not add an ESC runtime token")
    if "%" in text:
        raise Wave12Error("Wave 12 target must not add a printf-style token")
    if LITERAL_START in text.encode("utf-16-le") or LITERAL_END in text.encode("utf-16-le"):
        raise Wave12Error("Wave 12 target encodes a reserved literal marker")
    for character in text:
        if character != "\n" and unicodedata.category(character) == "Cc":
            raise Wave12Error(f"Wave 12 target has control U+{ord(character):04X}")


def validate_wave9_input(input_root: Path) -> dict[str, bytes]:
    resolved = require_under(input_root, REPO / "tmp", "Wave 9 input")
    reject_switch_path(resolved, "Wave 9 input")
    if not resolved.is_dir():
        raise Wave12Error(f"Wave 9 private candidate root is absent: {resolved}")

    resources: dict[str, bytes] = {}
    for resource in RESOURCE_PATHS:
        path = resolved / Path(resource)
        if not path.is_file():
            raise Wave12Error(f"Wave 9 input resource is absent: {path}")
        packed = path.read_bytes()
        actual = sha256_bytes(packed)
        if actual != INPUT_SHA256[resource]:
            raise Wave12Error(
                f"Wave 9 input hash differs for {resource}: "
                f"expected {INPUT_SHA256[resource]}, got {actual}"
            )
        if len(packed) != INPUT_SIZES[resource]:
            raise Wave12Error(
                f"Wave 9 input size differs for {resource}: "
                f"expected {INPUT_SIZES[resource]}, got {len(packed)}"
            )
        resources[resource] = packed
    return resources


def validate_semantic_anchors() -> dict[str, Any]:
    expected_literals = {
        "base_pristine_jp": PRISTINE_PC_JP_LITERALS,
        "pk_pristine_jp": PRISTINE_PC_JP_LITERALS,
        "pk_en": PC_EN_LITERALS,
    }
    evidence: dict[str, dict[str, Any]] = {}
    for label, source_path in PC_REFERENCE_PATHS.items():
        path = reject_switch_path(source_path, label)
        if not path.is_file():
            raise Wave12Error(f"PC semantic anchor is absent: {label}: {path}")
        resource_sha256 = sha256_path(path)
        if resource_sha256 != PC_REFERENCE_SHA256[label]:
            raise Wave12Error(
                f"PC semantic anchor hash differs for {label}: "
                f"expected {PC_REFERENCE_SHA256[label]}, got {resource_sha256}"
            )
        record = records_by_coordinate(path.read_bytes()).get(COORDINATE)
        if record is None:
            raise Wave12Error(f"PC semantic anchor lacks {coordinate_text(COORDINATE)}: {label}")
        if sha256_bytes(record.data) != PC_REFERENCE_RECORD_SHA256[label]:
            raise Wave12Error(f"PC semantic anchor record hash differs for {label}")
        if literal_texts(record) != expected_literals[label]:
            raise Wave12Error(f"PC semantic anchor literal differs for {label}")
        literal_hashes = [text_sha256(value) for value in literal_texts(record)]
        if literal_hashes != [PC_REFERENCE_LITERAL_UTF16LE_SHA256[label]]:
            raise Wave12Error(f"PC semantic anchor literal hash differs for {label}")
        evidence[label] = {
            "resource_sha256": resource_sha256,
            "record_sha256": sha256_bytes(record.data),
            "literal_utf16le_sha256": literal_hashes,
        }
    return {
        "switch_korean_used": False,
        "excluded": ["Nintendo Switch Korean"],
        "anchors": evidence,
    }


def validate_input_record(record: MsgGameRecord, resource: str) -> None:
    if len(record.data) != INPUT_RECORD_SIZE:
        raise Wave12Error(f"{resource} input record size differs")
    if sha256_bytes(record.data) != INPUT_RECORD_SHA256:
        raise Wave12Error(f"{resource} input record hash differs")
    if literal_texts(record) != CURRENT_LITERALS:
        raise Wave12Error(f"{resource} input literal differs")
    if text_sha256(CURRENT_LITERALS[0]) != INPUT_LITERAL_UTF16LE_SHA256:
        raise Wave12Error("Wave 12 current literal hash constant differs")
    if tuple(value.hex().upper() for value in opaque_spans(record)) != EXPECTED_OPAQUE_SPANS_HEX:
        raise Wave12Error(f"{resource} input opaque spans differ")
    if topology_hex(record) != EXPECTED_MARKER_TOPOLOGY_HEX:
        raise Wave12Error(f"{resource} input marker topology differs")
    if not record.data.endswith(RECORD_TERMINATOR):
        raise Wave12Error(f"{resource} input record lacks terminator")


def rebuild_static_record(record: MsgGameRecord, resource: str) -> MsgGameRecord:
    output_data = rebuild_record_literals(record, {0: TARGET_LITERALS[0]})
    output = MsgGameRecord(
        block_id=record.block_id,
        record_id=record.record_id,
        relative_offset=record.relative_offset,
        data=output_data,
    )
    if len(output.data) != TARGET_RECORD_SIZE:
        raise Wave12Error(f"{resource} output record size differs")
    if sha256_bytes(output.data) != TARGET_RECORD_SHA256:
        raise Wave12Error(f"{resource} output record hash differs")
    if literal_texts(output) != TARGET_LITERALS:
        raise Wave12Error(f"{resource} output literal differs")
    if text_sha256(TARGET_LITERALS[0]) != TARGET_LITERAL_UTF16LE_SHA256:
        raise Wave12Error("Wave 12 target literal hash constant differs")
    if tuple(value.hex().upper() for value in opaque_spans(output)) != EXPECTED_OPAQUE_SPANS_HEX:
        raise Wave12Error(f"{resource} output opaque spans differ")
    if topology_hex(output) != EXPECTED_MARKER_TOPOLOGY_HEX:
        raise Wave12Error(f"{resource} output marker topology differs")
    if opaque_spans(record) != opaque_spans(output):
        raise Wave12Error(f"{resource} output lost opaque bytes")
    if marker_topology(record) != marker_topology(output):
        raise Wave12Error(f"{resource} output changed marker topology")
    if not output.data.endswith(RECORD_TERMINATOR):
        raise Wave12Error(f"{resource} output record lost terminator")
    return output


def validate_full_output(
    resource: str,
    input_packed: bytes,
    output_packed: bytes,
    expected_record: MsgGameRecord,
) -> None:
    before = records_by_coordinate(input_packed)
    after = records_by_coordinate(output_packed)
    if before.keys() != after.keys():
        raise Wave12Error(f"{resource} changed record topology")
    changed = {
        coordinate for coordinate in before if before[coordinate].data != after[coordinate].data
    }
    if changed != {COORDINATE}:
        raise Wave12Error(
            f"{resource} changed records outside {coordinate_text(COORDINATE)}: {sorted(changed)}"
        )
    if after[COORDINATE].data != expected_record.data:
        raise Wave12Error(f"{resource} rebuilt target record differs")
    for coordinate, before_record in before.items():
        if coordinate != COORDINATE and after[coordinate].data != before_record.data:
            raise Wave12Error(f"{resource} changed non-target record {coordinate_text(coordinate)}")


def audit_row(
    resource: str,
    input_record: MsgGameRecord,
    output_record: MsgGameRecord,
    input_layout: Mapping[str, Any],
    output_layout: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "resource": resource,
        "coordinate": coordinate_text(COORDINATE),
        "input_record_sha256": sha256_bytes(input_record.data),
        "output_record_sha256": sha256_bytes(output_record.data),
        "input_record_size": len(input_record.data),
        "output_record_size": len(output_record.data),
        "literal_slot_count": len(literal_texts(input_record)),
        "input_literal_utf16le_sha256": [text_sha256(value) for value in literal_texts(input_record)],
        "output_literal_utf16le_sha256": [text_sha256(value) for value in literal_texts(output_record)],
        "input_opaque_spans_hex": [value.hex().upper() for value in opaque_spans(input_record)],
        "output_opaque_spans_hex": [value.hex().upper() for value in opaque_spans(output_record)],
        "opaque_spans_preserved": opaque_spans(input_record) == opaque_spans(output_record),
        "literal_marker_topology": [
            {"start": start.hex().upper(), "end": end.hex().upper()}
            for start, end in marker_topology(input_record)
        ],
        "terminator_hex": RECORD_TERMINATOR.hex().upper(),
        "input_layout": dict(input_layout),
        "output_layout": dict(output_layout),
        "missing_static_glyphs": [],
    }


def prepare_candidate(input_root: Path, font_root: Path) -> CandidateBundle:
    validate_static_literal_safety(TARGET_LITERALS[0])
    input_resources = validate_wave9_input(input_root)
    anchor_evidence = validate_semantic_anchors()
    advance, font_evidence = load_font_advance(font_root)
    input_layout = measure_line_layout(CURRENT_LITERALS, advance)
    output_layout = measure_line_layout(TARGET_LITERALS, advance)
    validate_target_layout(output_layout)

    output_resources: dict[str, bytes] = {}
    records: list[dict[str, Any]] = []
    for resource in RESOURCE_PATHS:
        input_packed = input_resources[resource]
        before = records_by_coordinate(input_packed)
        input_record = before.get(COORDINATE)
        if input_record is None:
            raise Wave12Error(f"{resource} lacks {coordinate_text(COORDINATE)}")
        validate_input_record(input_record, resource)
        output_record = rebuild_static_record(input_record, resource)
        output_packed = rebuild_packed_msggame(input_packed, {COORDINATE: output_record.data})
        validate_full_output(resource, input_packed, output_packed, output_record)
        actual_output_sha256 = sha256_bytes(output_packed)
        if actual_output_sha256 != TARGET_SHA256[resource]:
            raise Wave12Error(
                f"{resource} target hash differs: "
                f"expected {TARGET_SHA256[resource]}, got {actual_output_sha256}"
            )
        if len(output_packed) != TARGET_SIZES[resource]:
            raise Wave12Error(
                f"{resource} target size differs: "
                f"expected {TARGET_SIZES[resource]}, got {len(output_packed)}"
            )
        output_resources[resource] = output_packed
        records.append(audit_row(resource, input_record, output_record, input_layout, output_layout))

    audit = {
        "schema": AUDIT_SCHEMA,
        "source_free": True,
        "literal_source_text_embedded": False,
        "source_policy": {
            "platform": "Steam PC",
            "input_text_profile": "private Wave 9 candidate",
            "semantic_anchor": "pristine PC Japanese + PC English",
            "switch_korean_used": False,
            "excluded": ["Nintendo Switch Korean"],
        },
        "steam_write_capability": "absent",
        "input_sha256": dict(INPUT_SHA256),
        "output_sha256": dict(TARGET_SHA256),
        "font_evidence": font_evidence,
        "semantic_anchor_evidence": anchor_evidence,
        "summary": {
            "changed_resources": list(RESOURCE_PATHS),
            "physical_records": len(RESOURCE_PATHS),
            "logical_sentences": 1,
            "coordinate": coordinate_text(COORDINATE),
            "manual_lines": MAX_LINES,
            "max_line_px": MAX_LINE_PX,
            "target_line_widths_px": list(EXPECTED_TARGET_LINE_WIDTHS),
            "real_game_qa_required_before_release": True,
        },
        "records": records,
    }
    return CandidateBundle(
        resources=output_resources,
        input_sha256=dict(INPUT_SHA256),
        output_sha256=dict(TARGET_SHA256),
        audit=audit,
    )


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def write_json(path: Path, value: Mapping[str, Any]) -> str:
    payload = canonical_json(value)
    atomic_write(path, payload)
    return sha256_bytes(payload)


def write_candidate(bundle: CandidateBundle, output_root: Path) -> None:
    output_root = require_private_output(output_root, "candidate output")
    if output_root.exists():
        raise Wave12Error(f"refusing to overwrite candidate output: {output_root}")
    for resource in RESOURCE_PATHS:
        destination = output_root / Path(resource)
        atomic_write(destination, bundle.resources[resource])
        actual = sha256_path(destination)
        if actual != bundle.output_sha256[resource]:
            raise Wave12Error(f"written candidate hash differs for {resource}")


def build_manifest(bundle: CandidateBundle, audit_sha256: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "source_free_audit": True,
        "source_free_audit_sha256": audit_sha256,
        "steam_write_capability": "absent",
        "steam_apply_command": None,
        "input_sha256": dict(bundle.input_sha256),
        "output_sha256": dict(bundle.output_sha256),
        "changed_paths": list(RESOURCE_PATHS),
        "coordinates": {
            resource: coordinate_text(COORDINATE) for resource in RESOURCE_PATHS
        },
        "real_game_qa_required_before_release": True,
    }


def print_json(value: Mapping[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def command_hash(args: argparse.Namespace) -> int:
    bundle = prepare_candidate(args.input_root, args.font_root)
    print_json(
        {
            "status": "ok",
            "candidate_records": len(RESOURCE_PATHS),
            "output_sha256": dict(bundle.output_sha256),
            "steam_write_capability": "absent",
        }
    )
    return 0


def command_audit(args: argparse.Namespace) -> int:
    audit_path = require_private_output(args.audit_path, "audit output")
    bundle = prepare_candidate(args.input_root, args.font_root)
    audit_sha256 = write_json(audit_path, bundle.audit)
    print_json(
        {
            "status": "ok",
            "audit": audit_path.relative_to(REPO).as_posix(),
            "audit_sha256": audit_sha256,
            "output_sha256": dict(bundle.output_sha256),
            "steam_write_capability": "absent",
        }
    )
    return 0


def command_build(args: argparse.Namespace) -> int:
    output_root = require_private_output(args.output_root, "candidate output")
    audit_path = require_private_output(args.audit_path, "audit output")
    manifest_path = require_private_output(args.manifest, "manifest output")
    bundle = prepare_candidate(args.input_root, args.font_root)
    write_candidate(bundle, output_root)
    audit_sha256 = write_json(audit_path, bundle.audit)
    manifest_sha256 = write_json(manifest_path, build_manifest(bundle, audit_sha256))
    print_json(
        {
            "status": "ok",
            "candidate": output_root.relative_to(REPO).as_posix(),
            "audit": audit_path.relative_to(REPO).as_posix(),
            "manifest": manifest_path.relative_to(REPO).as_posix(),
            "audit_sha256": audit_sha256,
            "manifest_sha256": manifest_sha256,
            "output_sha256": dict(bundle.output_sha256),
            "steam_write_capability": "absent",
        }
    )
    return 0


def add_input_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--input-root", type=Path, default=WAVE9_INPUT_ROOT)
    parser.add_argument("--font-root", type=Path, default=DEFAULT_FONT_ROOT)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    hash_parser = subparsers.add_parser("hash", help="validate and print target hashes")
    add_input_arguments(hash_parser)
    hash_parser.set_defaults(func=command_hash)

    audit_parser = subparsers.add_parser("audit", help="write a source-free private audit")
    add_input_arguments(audit_parser)
    audit_parser.add_argument(
        "--audit-path",
        type=Path,
        default=PRIVATE_TMP_ROOT / "audit_pc_dialogue_quality_wave12.v1.json",
    )
    audit_parser.set_defaults(func=command_audit)

    candidate_parser = subparsers.add_parser(
        "build", help="write the private candidate, audit, and manifest"
    )
    add_input_arguments(candidate_parser)
    candidate_parser.add_argument(
        "--output-root", type=Path, default=PRIVATE_TMP_ROOT / "candidate-build-1"
    )
    candidate_parser.add_argument(
        "--audit-path",
        type=Path,
        default=PRIVATE_TMP_ROOT / "audit_pc_dialogue_quality_wave12.v1.json",
    )
    candidate_parser.add_argument(
        "--manifest",
        type=Path,
        default=PRIVATE_TMP_ROOT / "build_manifest.v1.json",
    )
    candidate_parser.set_defaults(func=command_build)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except Wave12Error as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
