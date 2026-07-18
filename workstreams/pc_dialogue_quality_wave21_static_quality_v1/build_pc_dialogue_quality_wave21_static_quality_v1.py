#!/usr/bin/env python3
"""Build the private, PC-only Wave 21 static-dialogue candidate.

The sole Korean input is the verified eleven-file Wave 19 private candidate.
This builder changes exactly two literal slots in PK msggame, writes only below
this workstream's tmp root, and has no Steam, Git, release, network, or
Switch-Korean capability.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
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
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
PREDECESSOR_CANDIDATE_ROOT = (
    REPO / "tmp" / "pc_dialogue_quality_wave19_static_inflection_v1" / "candidate"
)
TOOLS = REPO / "tools"
MSGGAME_TOOLS = REPO / "workstreams" / "msggame"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")

for module_root in (TOOLS, MSGGAME_TOOLS):
    if str(module_root) not in sys.path:
        sys.path.insert(0, str(module_root))

from nobu16_lz4 import decompress_wrapper, parse_link, recompress_wrapper  # noqa: E402
import validate_g1n_surgical as g1n  # noqa: E402
from msggame_format import (  # noqa: E402
    LITERAL_END,
    LITERAL_START,
    MsgGameRecord,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_with_literals,
    rebuild_raw_msggame,
    rebuild_record_literals,
)


SCHEMA = "nobu16.kr.pc-dialogue-quality-wave21-static-quality.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave21-static-quality-audit.v1"
BASE_MSGGAME = "MSG/JP/msggame.bin"
PK_MSGGAME = "MSG_PK/JP/msggame.bin"
CHANGED_PATHS = (PK_MSGGAME,)
PROFILE_PATHS = (
    "MSG/JP/ev_strdata.bin",
    BASE_MSGGAME,
    "MSG/JP/strdata.bin",
    "MSG_PK/JP/msgbre.bin",
    "MSG_PK/JP/msgdata.bin",
    "MSG_PK/JP/msgev.bin",
    PK_MSGGAME,
    "MSG_PK/JP/msgire.bin",
    "MSG_PK/JP/msgstf.bin",
    "MSG_PK/JP/msgstf_ce.bin",
    "MSG_PK/JP/msgui.bin",
)
RECORD_TERMINATOR = b"\x05\x05\x05"
FONT_PATH = "RES_JP/res_lang.bin"
FONT_SHA256 = "3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7"
FONT_ENTRY = 6
DIALOGUE_MAX_LINE_PX = 912
WIDE_SCRIPT_RE = re.compile(
    r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u9fff\uac00-\ud7a3\uf900-\ufaff]"
)

# Exact Wave 19 private-candidate profile.  It retains the Issue 61 repair in
# strdata/msgdata and every other Wave 19 output byte.
INPUT_SHA256 = {
    "MSG/JP/ev_strdata.bin": "BF224468BFBCF3CC71DFF4609142A60D75091813281EE6F2333645413AD81B80",
    BASE_MSGGAME: "C00B78165B06A5A9D2BFBE134E847E4B00EC3E5243EE9A1981BA1BB68CFA79C6",
    "MSG/JP/strdata.bin": "6E7DD096A999299C43A9A23D9E99F75C81D6A9C8116488EC541A43423871B933",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    "MSG_PK/JP/msgdata.bin": "73CF194E4EF81C20692A245DAC75C3B2A9FCF1A997B7F6755D89DBB59149F2ED",
    "MSG_PK/JP/msgev.bin": "CE1A61E6C0F85A3E7F0FD4C1DD1BF0349A99CC134A9D73B7DE1917DB6646A0C3",
    PK_MSGGAME: "7D7826A575E4BA80FEE1E4FE920CBD7E16A48F0DA529D06514EDB59B11422FBC",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}
TARGET_SHA256 = {
    **INPUT_SHA256,
    PK_MSGGAME: "0C3C2196E59BCBC1A066DF7097B37C281F8A6236DE70876CCD7BCAB44459BEA9",
}
INPUT_PK_PACKED_SIZE = 1_806_771
TARGET_PK_PACKED_SIZE = 1_806_775

# PC source anchors only.  The JP file is the pinned original extracted by the
# PC transaction; EN/SC/TC are the current PC-language context resources.
PC_REFERENCE_PATHS = {
    "JP": (
        DEFAULT_STEAM_ROOT
        / "KR_PATCH_BACKUP/file_only_transaction/steam-jp-1.1.7-v0.6.0/originals/MSG_PK/JP/msggame.bin",
        "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    ),
    "EN": (
        DEFAULT_STEAM_ROOT / "MSG_PK/EN/msggame.bin",
        "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    ),
    "SC": (
        DEFAULT_STEAM_ROOT / "MSG_PK/SC/msggame.bin",
        "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    ),
    "TC": (
        DEFAULT_STEAM_ROOT / "MSG_PK/TC/msggame.bin",
        "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
    ),
}


class Wave21Error(RuntimeError):
    """A pinned input, source anchor, or private-output contract failed."""


@dataclass(frozen=True)
class AnchorSpec:
    record_sha256: str
    record_size: int
    literal_utf16le_sha256: tuple[str, ...]
    context_utf16le_sha256: str
    opaque_spans_hex: tuple[str, ...]


@dataclass(frozen=True)
class Change:
    coordinate: tuple[int, int]
    literal_id: int
    target_literal: str
    input_record_sha256: str
    input_record_size: int
    input_literal_utf16le_sha256: tuple[str, ...]
    target_record_sha256: str
    target_record_size: int
    target_literal_utf16le_sha256: tuple[str, ...]
    opaque_spans_hex: tuple[str, ...]
    current_widths_px: tuple[int, ...]
    target_widths_px: tuple[int, ...]
    target_max_line_px: int | None
    rationale: str

    @property
    def coordinate_text(self) -> str:
        return f"{self.coordinate[0]}:{self.coordinate[1]}"


def _ko(value: str) -> str:
    """Decode target Korean without depending on a Windows console code page."""

    return value.encode("ascii").decode("unicode_escape")


CHANGES = (
    Change(
        coordinate=(2, 249),
        literal_id=1,
        target_literal=_ko(r"\uD14C\uB2C8\n\uAC71\uC815\uD560 \uD544\uC694 \uC5C6\uB2E4."),
        input_record_sha256="FA523D60C6C76618B4DD558F115D807AC44FB3F3767D42CE29D5E4DB725360D0",
        input_record_size=67,
        input_literal_utf16le_sha256=(
            "4AEC190639BC791831967217BBE5AE1B9CD22338F6583C73964F961E11F385D9",
            "2836FE4836AAC40C6C6471EACB54634649237F8698DE0EC2038A837FC3E58FA3",
        ),
        target_record_sha256="792E61B4C625D1E5AFF7F724029B7025FC9D10A2D7D5265AE8B1A77ECA35C996",
        target_record_size=69,
        target_literal_utf16le_sha256=(
            "4AEC190639BC791831967217BBE5AE1B9CD22338F6583C73964F961E11F385D9",
            "A0A38EEF6F8138876768948A6C11C9F62F63DB84A6308E3C34391BA1CBA68BF4",
        ),
        opaque_spans_hex=("", "", "050505"),
        current_widths_px=(696, 384),
        target_widths_px=(696, 408),
        target_max_line_px=DIALOGUE_MAX_LINE_PX,
        rationale="Japanese and all PC context languages say that worrying is unnecessary.",
    ),
    Change(
        coordinate=(2, 321),
        literal_id=1,
        target_literal=_ko(
            r"\n\uBC18\uB4DC\uC2DC \uD6CC\uB96D\uD55C \uC131\uD558\uB9C8\uC744\uC744 "
            r"\uB9CC\uB4E4\uC5B4 \uBCF4\uC774\uACA0\uB2E4!"
        ),
        input_record_sha256="6EC398D898818A92434C80D4FB01363A794120E4F6E29465DF7F379ED526EED9",
        input_record_size=117,
        input_literal_utf16le_sha256=(
            "00031E7EF7AA320CB10C43093450B7D608349087A13BBAAC45839D5214D6D199",
            "8C02BCD8DAD84641218DA42550838265A787826487ED8BB829E44F07C18FF7C3",
        ),
        target_record_sha256="9836FE47911F35EEA67AD7673FDEE42F5629772D6FBA63BCCCC1F2642C4B89C4",
        target_record_size=117,
        target_literal_utf16le_sha256=(
            "00031E7EF7AA320CB10C43093450B7D608349087A13BBAAC45839D5214D6D199",
            "893192C47DEBACD596964881896672CAE653B674E4DD08ED86BCF5239EEC1C24",
        ),
        opaque_spans_hex=("", "", "050505"),
        current_widths_px=(696, 432, 984),
        target_widths_px=(696, 432, 984),
        target_max_line_px=None,
        rationale="PC JP/EN/SC/TC all construct a castle town; Korean needs an object marker.",
    ),
)
CHANGE_BY_COORDINATE = {change.coordinate: change for change in CHANGES}
if len(CHANGE_BY_COORDINATE) != len(CHANGES):
    raise RuntimeError("duplicate Wave 21 record coordinate")


ANCHORS: dict[tuple[int, int], dict[str, AnchorSpec]] = {
    (2, 249): {
        "JP": AnchorSpec(
            "391C422ABE9255EECFFD090B286B50AA0F18509E7C850B6FA6D534709A930246",
            61,
            (
                "5154888B50EEB1DBE28A7B9B176473BAAE8F617FBBF6359729D3DD2585BF1A02",
                "002BDFA575C56F8E020D4B10EB521B948276A1BC2537B61E5149A4ED76BE3B1D",
            ),
            "98F9A4E14AD2A6D250628B763A4B1D849A7CF0DC75D240FE9B9BDEEE466F17F0",
            ("", "014348040000", "014326020000050505"),
        ),
        "EN": AnchorSpec(
            "6F92060959B33BCC7853256F935170777ADA183D9ACB74EE0004721FD664B0BD",
            127,
            ("84572E6C1838F0C2FE238C98CF75C880BE8510005A6FFA84495F63682A2BC0C1",),
            "84572E6C1838F0C2FE238C98CF75C880BE8510005A6FFA84495F63682A2BC0C1",
            ("", "050505"),
        ),
        "SC": AnchorSpec(
            "24C6756ACF1E7B89217D5DFC9B2EFE07CB40BBD4CD092D180270C93D5CF51C4D",
            53,
            ("CFBD7A76D724D49369EB925354C65B0D6E0C7B76DDD82E24F94B3EC7719F2ADC",),
            "CFBD7A76D724D49369EB925354C65B0D6E0C7B76DDD82E24F94B3EC7719F2ADC",
            ("", "050505"),
        ),
        "TC": AnchorSpec(
            "28C3728A70D83BD5F38E795675F4C0DB51DC9250C3BAEDCE227ACE1971C3DAEF",
            53,
            ("722203F914DC063ED6C5B095CA829903DB7F3424E15B0773D599FA893C4B3C1B",),
            "722203F914DC063ED6C5B095CA829903DB7F3424E15B0773D599FA893C4B3C1B",
            ("", "050505"),
        ),
    },
    (2, 321): {
        "JP": AnchorSpec(
            "BC4F0DEFCC4A554DC2CD1D8ED44B54CAE73DC99285DA6271220070E485674865",
            93,
            (
                "3F18ADBA2CFD9C2AD32ABE50CD0D62B9EF832C3233E385525627B57C569AC484",
                "A2F1C974100A44777C89BEFA4E28B80EF11962E4FE148B5E66B906F1F4858CC8",
            ),
            "D035D0D6E60AF6D8F5FB2B2A59E0F5557525914C2FBACFD993537DF79B48BFD0",
            ("", "01438E000000", "014348040000050505"),
        ),
        "EN": AnchorSpec(
            "7CE78781238091A2543B93B8EF6B15C76366DFE2870A43C5A02BC4BEDE027A19",
            205,
            ("3CAB0EA1E8AABC252D470F97B090B61D631E1BCB5746F430B2882AF5DC0B9547",),
            "3CAB0EA1E8AABC252D470F97B090B61D631E1BCB5746F430B2882AF5DC0B9547",
            ("", "050505"),
        ),
        "SC": AnchorSpec(
            "101935262912F2764199F5ABC05E978B5C45D893C9BF73767024C1D43AB61AC9",
            77,
            ("4B50128C65F20758F323545479FD414872C508D474123E5CFD6B3E3F540BFE67",),
            "4B50128C65F20758F323545479FD414872C508D474123E5CFD6B3E3F540BFE67",
            ("", "050505"),
        ),
        "TC": AnchorSpec(
            "9E9D5346FF803045C24F878D6C84AD1FD90A973F4542C2CAC1C19CCD59A7512E",
            79,
            ("83553647B4C17A9BAEB9447A59FB0F53DFDBF6467788AC4F4DEC8823359A36D3",),
            "83553647B4C17A9BAEB9447A59FB0F53DFDBF6467788AC4F4DEC8823359A36D3",
            ("", "050505"),
        ),
    },
}


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


def records_by_coordinate(packed: bytes) -> dict[tuple[int, int], MsgGameRecord]:
    archive = parse_packed_msggame(packed).archive
    return {
        (record.block_id, record.record_id): record
        for block in archive.blocks
        for record in block.records
    }


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


def text_format_signature(value: str) -> tuple[tuple[str, ...], str, str]:
    return (
        tuple(re.findall(r"\r\n|\n|\r", value)),
        value[: len(value) - len(value.lstrip())],
        value[len(value.rstrip()) :],
    )


def profile_hashes(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for relative in PROFILE_PATHS:
        path = root / relative
        if not path.is_file():
            raise Wave21Error(f"profile resource is absent: {relative}")
        result[relative] = sha256_path(path)
    return result


def assert_profile(root: Path, expected: Mapping[str, str], label: str) -> None:
    actual = profile_hashes(root)
    if actual != dict(expected):
        mismatch = {
            relative: {"expected": expected.get(relative), "actual": actual.get(relative)}
            for relative in PROFILE_PATHS
            if actual.get(relative) != expected.get(relative)
        }
        raise Wave21Error(f"{label} profile mismatch: {json.dumps(mismatch, sort_keys=True)}")


def validate_raw_roundtrip(packed: bytes, label: str) -> None:
    header, raw = decompress_wrapper(packed)
    archive = parse_packed_msggame(packed).archive
    if rebuild_raw_msggame(archive) != raw:
        raise Wave21Error(f"{label} raw parse/rebuild differs")
    repacked = recompress_wrapper(raw, header)
    _header, roundtrip_raw = decompress_wrapper(repacked)
    if roundtrip_raw != raw:
        raise Wave21Error(f"{label} wrapper round-trip differs")


def reject_switch_path(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    if any("switch" in part.casefold() for part in resolved.parts):
        raise Wave21Error(f"Switch Korean input is forbidden: {label}")
    return resolved


def validate_pc_anchors() -> dict[str, Any]:
    archives: dict[str, dict[tuple[int, int], MsgGameRecord]] = {}
    packed_hashes: dict[str, str] = {}
    for language, (path, expected_hash) in PC_REFERENCE_PATHS.items():
        checked = reject_switch_path(path, f"PC {language}")
        actual_hash = sha256_path(checked)
        if actual_hash != expected_hash:
            raise Wave21Error(
                f"PC {language} source hash differs: expected {expected_hash}, got {actual_hash}"
            )
        archives[language] = records_by_coordinate(checked.read_bytes())
        packed_hashes[language] = actual_hash

    result: dict[str, Any] = {}
    for coordinate, expected_by_language in ANCHORS.items():
        coordinate_text = f"{coordinate[0]}:{coordinate[1]}"
        result[coordinate_text] = {}
        for language, expected in expected_by_language.items():
            record = archives[language].get(coordinate)
            if record is None:
                raise Wave21Error(f"PC {language} anchor lacks {coordinate_text}")
            values = literal_texts(record)
            spans_hex = tuple(value.hex().upper() for value in opaque_spans(record))
            if (
                sha256_bytes(record.data) != expected.record_sha256
                or len(record.data) != expected.record_size
                or tuple(text_sha256(value) for value in values)
                != expected.literal_utf16le_sha256
                or text_sha256("".join(values)) != expected.context_utf16le_sha256
                or spans_hex != expected.opaque_spans_hex
            ):
                raise Wave21Error(f"PC {language} anchor drift at {coordinate_text}")
            result[coordinate_text][language] = {
                "record_sha256": expected.record_sha256,
                "record_size": expected.record_size,
                "literal_utf16le_sha256": list(expected.literal_utf16le_sha256),
                "context_utf16le_sha256": expected.context_utf16le_sha256,
                "opaque_spans_hex": list(expected.opaque_spans_hex),
            }
    return {"reference_packed_sha256": packed_hashes, "records": result}


def validate_literal_text(value: str, label: str) -> None:
    if not value:
        raise Wave21Error(f"{label} target literal is empty")
    if "\0" in value:
        raise Wave21Error(f"{label} target literal contains NUL")
    for character in value:
        if unicodedata.category(character) == "Cc" and character not in "\n\r":
            raise Wave21Error(f"{label} target literal contains disallowed control")
    encoded = value.encode("utf-16-le")
    if LITERAL_START in encoded or LITERAL_END in encoded:
        raise Wave21Error(f"{label} target literal contains a reserved marker")


def validate_change(change: Change, record: MsgGameRecord) -> tuple[MsgGameRecord, dict[str, Any]]:
    current = literal_texts(record)
    before_spans = opaque_spans(record)
    before_hashes = tuple(text_sha256(value) for value in current)
    if (
        sha256_bytes(record.data) != change.input_record_sha256
        or len(record.data) != change.input_record_size
        or before_hashes != change.input_literal_utf16le_sha256
        or tuple(value.hex().upper() for value in before_spans) != change.opaque_spans_hex
        or not record.data.endswith(RECORD_TERMINATOR)
        or change.literal_id >= len(current)
    ):
        raise Wave21Error(f"{change.coordinate_text} current record guard differs")

    validate_literal_text(change.target_literal, f"{change.coordinate_text}:{change.literal_id}")
    if text_format_signature(current[change.literal_id]) != text_format_signature(
        change.target_literal
    ):
        raise Wave21Error(f"{change.coordinate_text} changes linebreak or edge whitespace")
    if current[change.literal_id] == change.target_literal:
        raise Wave21Error(f"{change.coordinate_text} target equals current literal")

    rebuilt_data = rebuild_record_literals(record, {change.literal_id: change.target_literal})
    rebuilt = MsgGameRecord(record.block_id, record.record_id, record.relative_offset, rebuilt_data)
    target = literal_texts(rebuilt)
    if (
        sha256_bytes(rebuilt.data) != change.target_record_sha256
        or len(rebuilt.data) != change.target_record_size
        or tuple(text_sha256(value) for value in target)
        != change.target_literal_utf16le_sha256
        or opaque_spans(rebuilt) != before_spans
        or marker_topology(rebuilt) != marker_topology(record)
        or not rebuilt.data.endswith(RECORD_TERMINATOR)
        or any(target[index] != current[index] for index in range(len(current)) if index != change.literal_id)
    ):
        raise Wave21Error(f"{change.coordinate_text} literal reconstruction differs")
    return rebuilt, {
        "coordinate": change.coordinate_text,
        "literal_id": change.literal_id,
        "input_record_sha256": change.input_record_sha256,
        "target_record_sha256": change.target_record_sha256,
        "input_record_size": change.input_record_size,
        "target_record_size": change.target_record_size,
        "input_literal_utf16le_sha256": list(change.input_literal_utf16le_sha256),
        "target_literal_utf16le_sha256": list(change.target_literal_utf16le_sha256),
        "opaque_spans_hex": list(change.opaque_spans_hex),
        "linebreak_count": {
            "current": "".join(current).count("\n"),
            "target": "".join(target).count("\n"),
        },
        "rationale": change.rationale,
    }


def load_font_advance() -> tuple[Callable[[str], tuple[int, bool]], dict[str, Any]]:
    path = DEFAULT_STEAM_ROOT / FONT_PATH
    if not path.is_file():
        raise Wave21Error(f"font resource is absent: {path}")
    actual_hash = sha256_path(path)
    if actual_hash != FONT_SHA256:
        raise Wave21Error(f"font profile differs: expected {FONT_SHA256}, got {actual_hash}")
    try:
        archive = parse_link(path.read_bytes())
        _header, raw = decompress_wrapper(archive.entries[FONT_ENTRY].data)
    except (IndexError, ValueError) as exc:
        raise Wave21Error("JP font entry cannot be unpacked") from exc
    with tempfile.TemporaryDirectory(prefix="nobu16_wave21_font_") as directory:
        font_path = Path(directory) / "font.g1n"
        font_path.write_bytes(raw)
        parsed = g1n.parse_g1n(font_path)
    if parsed.structural_errors or not parsed.tables:
        raise Wave21Error("JP font is structurally invalid")
    table = parsed.tables[0]

    def advance(character: str) -> tuple[int, bool]:
        if len(character) != 1:
            raise Wave21Error("font metric requires one character")
        ordinal = table.mapping[ord(character)] if ord(character) < len(table.mapping) else 0
        if ordinal == 0:
            if WIDE_SCRIPT_RE.fullmatch(character):
                return 48, True
            raise Wave21Error(f"JP font lacks glyph U+{ord(character):04X}")
        if ordinal >= len(table.records):
            raise Wave21Error(f"JP font ordinal is invalid for U+{ord(character):04X}")
        glyph = table.records[ordinal]
        if glyph.width != glyph.advance or glyph.advance not in (24, 48):
            raise Wave21Error(f"JP glyph metrics are invalid for U+{ord(character):04X}")
        return glyph.advance, False

    return advance, {
        "resource": FONT_PATH,
        "entry": FONT_ENTRY,
        "packed_sha256": actual_hash,
        "table_count": len(parsed.tables),
    }


def line_layout(
    values: tuple[str, ...], advance: Callable[[str], tuple[int, bool]]
) -> dict[str, Any]:
    widths: list[int] = []
    fallback: set[str] = set()
    for line in "".join(values).split("\n"):
        width = 0
        for character in line:
            if unicodedata.category(character) == "Cc":
                raise Wave21Error(f"font layout has control U+{ord(character):04X}")
            glyph_width, is_fallback = advance(character)
            width += glyph_width
            if is_fallback:
                fallback.add(f"U+{ord(character):04X}")
        widths.append(width)
    return {
        "line_count": len(widths),
        "line_widths_px": widths,
        "max_width_px": max(widths, default=0),
        "wide_fallback_codepoints": sorted(fallback),
    }


def validate_font_layouts(
    before: Mapping[tuple[int, int], MsgGameRecord],
    after: Mapping[tuple[int, int], MsgGameRecord],
) -> dict[str, Any]:
    advance, font = load_font_advance()
    result: dict[str, Any] = {}
    for change in CHANGES:
        current = line_layout(literal_texts(before[change.coordinate]), advance)
        target = line_layout(literal_texts(after[change.coordinate]), advance)
        if (
            tuple(current["line_widths_px"]) != change.current_widths_px
            or tuple(target["line_widths_px"]) != change.target_widths_px
            or current["wide_fallback_codepoints"]
            or target["wide_fallback_codepoints"]
        ):
            raise Wave21Error(f"{change.coordinate_text} font layout differs")
        if change.target_max_line_px is not None:
            if target["max_width_px"] > change.target_max_line_px:
                raise Wave21Error(f"{change.coordinate_text} exceeds dialogue width bound")
        elif current["line_widths_px"] != target["line_widths_px"]:
            raise Wave21Error(f"{change.coordinate_text} changes existing three-line width")
        result[change.coordinate_text] = {
            "current": current,
            "target": target,
            "width_delta_px": [
                target_width - current_width
                for current_width, target_width in zip(
                    current["line_widths_px"], target["line_widths_px"]
                )
            ],
            "target_max_line_px": change.target_max_line_px,
        }
    return {"font": font, "records": result}


def validate_output_records(packed: bytes) -> dict[tuple[int, int], MsgGameRecord]:
    records = records_by_coordinate(packed)
    for change in CHANGES:
        record = records.get(change.coordinate)
        if record is None:
            raise Wave21Error(f"candidate lacks {change.coordinate_text}")
        if (
            sha256_bytes(record.data) != change.target_record_sha256
            or len(record.data) != change.target_record_size
            or tuple(text_sha256(value) for value in literal_texts(record))
            != change.target_literal_utf16le_sha256
            or tuple(value.hex().upper() for value in opaque_spans(record))
            != change.opaque_spans_hex
            or not record.data.endswith(RECORD_TERMINATOR)
        ):
            raise Wave21Error(f"candidate record differs: {change.coordinate_text}")
    return records


def prepare_candidate(predecessor_root: Path) -> tuple[bytes, dict[str, Any]]:
    predecessor_root = reject_switch_path(predecessor_root, "Wave 19 private candidate")
    assert_profile(predecessor_root, INPUT_SHA256, "Wave 19 predecessor")
    input_packed = (predecessor_root / PK_MSGGAME).read_bytes()
    if len(input_packed) != INPUT_PK_PACKED_SIZE:
        raise Wave21Error("PK msggame input size differs")
    validate_raw_roundtrip(input_packed, "Wave 19 PK msggame")
    anchors = validate_pc_anchors()

    before = records_by_coordinate(input_packed)
    replacements: dict[tuple[int, int, int], str] = {}
    audit_records: list[dict[str, Any]] = []
    for change in CHANGES:
        record = before.get(change.coordinate)
        if record is None:
            raise Wave21Error(f"Wave 19 PK msggame lacks {change.coordinate_text}")
        _rebuilt, row = validate_change(change, record)
        key = (*change.coordinate, change.literal_id)
        if key in replacements:
            raise Wave21Error(f"duplicate literal replacement: {key}")
        replacements[key] = change.target_literal
        audit_records.append(row)

    output = rebuild_packed_with_literals(input_packed, replacements)
    if len(output) != TARGET_PK_PACKED_SIZE or sha256_bytes(output) != TARGET_SHA256[PK_MSGGAME]:
        raise Wave21Error("PK candidate packed output differs")
    validate_raw_roundtrip(output, "Wave 21 PK candidate")
    after = records_by_coordinate(output)
    if before.keys() != after.keys():
        raise Wave21Error("PK candidate record coordinates differ")
    changed = {coordinate for coordinate in before if before[coordinate].data != after[coordinate].data}
    if changed != set(CHANGE_BY_COORDINATE):
        raise Wave21Error(f"PK candidate changed unexpected records: {sorted(changed)}")
    validate_output_records(output)
    font_layout = validate_font_layouts(before, after)

    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "predecessor_profile": "wave19_private_candidate",
            "wave19_full_profile_required": True,
            "issue61_strdata_msgdata_preserved": True,
            "pristine_pc_japanese_read": True,
            "pc_en_sc_tc_context_read": True,
            "switch_korean_read": False,
            "steam_game_resource_written": False,
            "git_operation": "absent",
            "release_operation": "absent",
        },
        "predecessor_candidate_root": str(predecessor_root),
        "input_sha256": INPUT_SHA256,
        "target_sha256": TARGET_SHA256,
        "pc_anchors": anchors,
        "font_layout": font_layout,
        "records": audit_records,
        "changed_record_count": len(changed),
    }
    return output, audit


def require_tmp(path: Path, label: str) -> Path:
    root = TMP_ROOT.resolve(strict=False)
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave21Error(f"{label} must stay below {root}") from exc
    return resolved


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def verify_private_candidate(candidate_root: Path) -> None:
    candidate_root = require_tmp(candidate_root, "candidate root")
    assert_profile(candidate_root, TARGET_SHA256, "Wave 21 private candidate")
    packed = (candidate_root / PK_MSGGAME).read_bytes()
    if len(packed) != TARGET_PK_PACKED_SIZE:
        raise Wave21Error("private PK msggame size differs")
    validate_raw_roundtrip(packed, "Wave 21 private PK msggame")
    validate_output_records(packed)


def _remove_stage(stage: Path) -> None:
    if not stage.exists():
        return
    try:
        stage.resolve().relative_to(TMP_ROOT.resolve(strict=False))
    except ValueError as exc:
        raise Wave21Error("refusing to remove a stage outside the Wave 21 tmp root") from exc
    shutil.rmtree(stage)


def build_candidate(
    predecessor_root: Path,
    output_root: Path,
    audit_path: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    output_root = require_tmp(output_root, "candidate output")
    audit_path = require_tmp(audit_path, "audit output")
    manifest_path = require_tmp(manifest_path, "manifest output")
    if output_root.exists() or audit_path.exists() or manifest_path.exists():
        raise Wave21Error("candidate output, audit, or manifest already exists")

    output, audit = prepare_candidate(predecessor_root)
    output_root.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.", dir=output_root.parent))
    try:
        require_tmp(stage, "candidate stage")
        predecessor_root = reject_switch_path(predecessor_root, "Wave 19 private candidate")
        for relative in PROFILE_PATHS:
            destination = stage / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if relative == PK_MSGGAME:
                destination.write_bytes(output)
            else:
                shutil.copy2(predecessor_root / relative, destination)
        assert_profile(stage, TARGET_SHA256, "Wave 21 private staging")
        os.replace(stage, output_root)
        verify_private_candidate(output_root)
        audit_bytes = (
            json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        atomic_write(audit_path, audit_bytes)
        manifest = {
            "schema": SCHEMA,
            "transaction_id": "pc-dialogue-quality-wave21-static-quality-v1",
            "candidate_only": True,
            "predecessor_candidate_root": str(predecessor_root),
            "profile_paths": list(PROFILE_PATHS),
            "changed_paths": list(CHANGED_PATHS),
            "coordinates": [
                f"{PK_MSGGAME}:{change.coordinate_text}:{change.literal_id}"
                for change in CHANGES
            ],
            "input_sha256": INPUT_SHA256,
            "output_sha256": TARGET_SHA256,
            "pinned_output_sha256": TARGET_SHA256,
            "audit_sha256": sha256_bytes(audit_bytes),
            "record_count": len(CHANGES),
            "issue61_strdata_msgdata_preserved": True,
            "steam_write_capability": "absent",
            "git_operation": "absent",
            "release_operation": "absent",
            "real_game_qa_required_before_release": True,
        }
        atomic_write(
            manifest_path,
            (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
                "utf-8"
            ),
        )
        return manifest
    except Exception:
        _remove_stage(stage)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    hash_parser = sub.add_parser("hash", help="validate and hash the in-memory candidate")
    hash_parser.add_argument("--predecessor-root", type=Path, default=PREDECESSOR_CANDIDATE_ROOT)
    verify_parser = sub.add_parser("verify-private", help="verify a private Wave 21 candidate")
    verify_parser.add_argument("--candidate-root", type=Path, required=True)
    build_parser = sub.add_parser("build", help="write only below this workstream's tmp root")
    build_parser.add_argument("--predecessor-root", type=Path, default=PREDECESSOR_CANDIDATE_ROOT)
    build_parser.add_argument("--output-root", type=Path, default=TMP_ROOT / "candidate")
    build_parser.add_argument("--audit-path", type=Path, default=TMP_ROOT / "audit.v1.json")
    build_parser.add_argument(
        "--manifest-path", type=Path, default=TMP_ROOT / "build_manifest.v1.json"
    )
    args = parser.parse_args(argv)
    try:
        if args.command == "hash":
            _output, audit = prepare_candidate(args.predecessor_root)
            print(
                json.dumps(
                    {
                        "status": "ok",
                        "target_sha256": audit["target_sha256"],
                        "steam_write_capability": "absent",
                    },
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
        if args.command == "verify-private":
            verify_private_candidate(args.candidate_root)
            print(
                json.dumps(
                    {
                        "status": "ok",
                        "candidate_root": str(args.candidate_root),
                        "steam_write_capability": "absent",
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
            return 0
        manifest = build_candidate(
            args.predecessor_root,
            args.output_root,
            args.audit_path,
            args.manifest_path,
        )
        print(
            json.dumps(
                {
                    "status": "ok",
                    "manifest": manifest,
                    "steam_write_capability": "absent",
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    except (OSError, ValueError, Wave21Error) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
