#!/usr/bin/env python3
"""Build a private, fail-closed Steam-PC event-name repair candidate.

This workstream changes exactly three static entries in
MSG_PK/JP/msgev.bin.  It only reads the current Steam Korean resource, the
pinned pristine PC Japanese resource, the pinned PC English resource, and the
active Steam event font.  It has no Nintendo Switch input and no Steam apply,
transaction, Git, network, or release capability.

The only write command creates an immutable candidate directory below this
workstream's tmp root.  A changed source, anchor, font metric, text contract,
or output hash fails closed rather than rebasing the candidate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import sys
import unicodedata
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
PRIVATE_TMP_ROOT = REPO / "tmp" / WORKSTREAM.name

RESOURCE = Path("MSG_PK") / "JP" / "msgev.bin"
RESOURCE_TEXT = RESOURCE.as_posix()
STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
CURRENT_STEAM_RESOURCE = STEAM_ROOT / RESOURCE
PRISTINE_PC_JP_RESOURCE = (
    STEAM_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / RESOURCE
)
PC_EN_RESOURCE = STEAM_ROOT / "MSG_PK" / "EN" / "msgev.bin"
EVENT_FONT_RESOURCE = STEAM_ROOT / "RES_JP" / "res_lang.bin"

SCHEMA = "nobu16.kr.pc-event-name-quality-wave15-candidate.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-event-name-quality-wave15-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-event-name-quality-wave15-manifest.v1"

INPUT_SIZE = 994_707
INPUT_SHA256 = "3E2323DDFAD70DAA15713DD1C4D622508BD2E610C65683C0A06D3D1FAC9827A5"
INPUT_RAW_SIZE = 990_796
INPUT_RAW_SHA256 = "2D0419F66F7FA5DD6F6D8E1E9932E8C1EAA929700707BC447954A9783F8C40EA"

PRISTINE_PC_JP_SIZE = 562_226
PRISTINE_PC_JP_SHA256 = "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84"
PC_EN_SIZE = 762_196
PC_EN_SHA256 = "BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E"

EVENT_FONT_SIZE = 161_428_458
EVENT_FONT_SHA256 = "3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7"
FONT_OUTER_ENTRY = 6
FONT_TABLE = 0
FONT_MAP_BYTES = 0x20000
FONT_RECORD_BYTES = 12
MAX_LINE_PX = 912
MAX_LINES = 3

TARGET_RAW_SIZE = 990_800
TARGET_RAW_SHA256 = "3A43DD803C48239507C4070FC6B4014B9B5521DE6A583BEC75E5DA9195D62FD9"
TARGET_SIZE = 994_711
TARGET_SHA256 = "CE1A61E6C0F85A3E7F0FD4C1DD1BF0349A99CC134A9D73B7DE1917DB6646A0C3"

LINEBREAK_RE = re.compile(r"\r\n|\n|\r")
RUNTIME_TOKEN_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
PRINTF_RE = re.compile(
    r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?"
    r"(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
WIDE_SCRIPT_RE = re.compile(
    r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u9fff\uac00-\ud7a3\uf900-\ufaff]"
)


class Wave15Error(RuntimeError):
    """Raised when a pinned input or private-output safety contract fails."""


@dataclass(frozen=True)
class Change:
    entry_id: int
    current_text: str
    target_text: str
    jp_anchor_text: str
    en_anchor_text: str
    current_text_sha256: str
    target_text_sha256: str
    jp_anchor_utf16le_sha256: str
    en_anchor_utf16le_sha256: str
    current_line_widths_px: tuple[int, ...]
    target_line_widths_px: tuple[int, ...]


@dataclass(frozen=True)
class TableResource:
    path: Path
    packed: bytes
    header: Any
    raw: bytes
    table: Any


@dataclass(frozen=True)
class CandidateBundle:
    packed: bytes
    raw: bytes
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


CHANGES = (
    Change(
        entry_id=3015,
        current_text="\ubbf8\ud0a4 \uc694\uc2dc\uc694\ub9ac",
        target_text="\ubbf8\uce20\ud0a4 \uc694\uc2dc\uc694\ub9ac",
        jp_anchor_text="\u4e09\u6728\u826f\u983c",
        en_anchor_text="Yoshiyori Mitsuki",
        current_text_sha256="28CB219E5D8FBDB0D0C5145FF7BEB026174B77FBB53399A2F2EFAA8700E99756",
        target_text_sha256="17771E37F3BAEA251D037D54E856883A0C86E90E680CD62567D38E44A0186018",
        jp_anchor_utf16le_sha256="C7F418AE853F91D350F854F6410ACE0BA2EFB5DF7829EF17B0C38DC811479A32",
        en_anchor_utf16le_sha256="AE4DEB67A9C3DFA7858949CA0CDA57AD20609ACC5F8AAE2962BC4DB54E8A2068",
        current_line_widths_px=(312,),
        target_line_widths_px=(360,),
    ),
    Change(
        entry_id=3016,
        current_text="\ubbf8\ud0a4 \uc694\ub9ac\uc4f0\ub098",
        target_text="\ubbf8\uce20\ud0a4 \uc694\ub9ac\uce20\ub098",
        jp_anchor_text="\u4e09\u6728\u81ea\u7db1",
        en_anchor_text="Yoritsuna Mitsuki",
        current_text_sha256="3EF6F51F5F2ED6A8FE67F23DE3D0C5EDF96D9D50E0A8A9E64D9B2A62B4284F37",
        target_text_sha256="E3FEBFE1AE661F7126FDDBFE603D3A8972C481C685BFD01FA5033566EEBF6B53",
        jp_anchor_utf16le_sha256="D04A6E7AA33089F60C702E2E62C2D65015751ED53A5532DB2D3714C40FAA070B",
        en_anchor_utf16le_sha256="3269C4EE44C5D54A4256ADFAA8A5997D08BB970AA8415CAAFE31053C9FCC0545",
        current_line_widths_px=(312,),
        target_line_widths_px=(360,),
    ),
    Change(
        entry_id=3084,
        current_text="\uc624\ud1a0\ubaa8 \uc9c0\uce74\uc774\uc5d0",
        target_text="\uc624\ud1a0\ubaa8 \uce58\uce74\uc774\uc5d0",
        jp_anchor_text="\u5927\u53cb\u89aa\u5bb6",
        en_anchor_text="Chikaie \u00a5tomo",
        current_text_sha256="BFE97B5118DC094195C93FD16BE8447D3F64C9525320A337506AB753D44617DF",
        target_text_sha256="0D8D92E08B423CA3ABA3BD56DF6B46B143B2920CD64B2A823C2A2C1B5AEE62EF",
        jp_anchor_utf16le_sha256="4B130220D16F222D4AB9D54F5612A84EC6614AB8D5CA8B2906B450E8F5D6F70B",
        en_anchor_utf16le_sha256="2EF4A698C6F1765B862770808E420AB6ADA311F7163F0E81FF7C508203896893",
        current_line_widths_px=(360,),
        target_line_widths_px=(360,),
    ),
)

CHANGE_BY_ID = {change.entry_id: change for change in CHANGES}
if len(CHANGE_BY_ID) != len(CHANGES):
    raise RuntimeError("Wave 15 has duplicate msgev IDs")

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper, parse_link, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave15Error(label)


def require_under(path: Path, root: Path, label: str) -> Path:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise Wave15Error(f"{label} escapes private tmp root: {resolved_path}") from exc
    return resolved_path


def require_private_output(path: Path, label: str = "candidate output") -> Path:
    return require_under(path, PRIVATE_TMP_ROOT, label)


def linebreak_vector(value: str) -> list[str]:
    return LINEBREAK_RE.findall(value)


def protected_signature(value: str) -> dict[str, Any]:
    """Return every non-text construct that must be identical across a repair."""

    escapes: list[str] = []
    controls: list[str] = []
    cursor = 0
    while cursor < len(value):
        character = value[cursor]
        if character == "\x1b":
            token = value[cursor : cursor + 3]
            if ESC_RE.fullmatch(token) is None:
                raise Wave15Error(f"malformed ESC token at U+001B offset {cursor}")
            escapes.append(token)
            cursor += 3
            continue
        if character not in ("\r", "\n") and unicodedata.category(character) == "Cc":
            controls.append(f"U+{ord(character):04X}")
        cursor += 1

    printf_matches = list(PRINTF_RE.finditer(value))
    printf_percent_offsets = {match.start() for match in printf_matches}
    return {
        "linebreak_vector": linebreak_vector(value),
        "runtime_bracket_tokens": RUNTIME_TOKEN_RE.findall(value),
        "printf_tokens": [match.group(0) for match in printf_matches],
        "unknown_percent_count": sum(
            1
            for offset, character in enumerate(value)
            if character == "%" and offset not in printf_percent_offsets
        ),
        "esc_tokens": escapes,
        "controls": controls,
    }


EMPTY_STATIC_SIGNATURE = {
    "linebreak_vector": [],
    "runtime_bracket_tokens": [],
    "printf_tokens": [],
    "unknown_percent_count": 0,
    "esc_tokens": [],
    "controls": [],
}


def validate_declared_change(change: Change) -> None:
    for actual, expected, label in (
        (text_hash(change.current_text), change.current_text_sha256, "current text hash"),
        (text_hash(change.target_text), change.target_text_sha256, "target text hash"),
        (text_hash(change.jp_anchor_text), change.jp_anchor_utf16le_sha256, "JP anchor hash"),
        (text_hash(change.en_anchor_text), change.en_anchor_utf16le_sha256, "EN anchor hash"),
    ):
        require(actual == expected, f"id {change.entry_id} declared {label} differs")
    current_signature = protected_signature(change.current_text)
    target_signature = protected_signature(change.target_text)
    require(
        current_signature == target_signature,
        f"id {change.entry_id} declared control/token/linebreak signature differs",
    )
    require(
        current_signature == EMPTY_STATIC_SIGNATURE,
        f"id {change.entry_id} is not a plain static one-line name",
    )
    require(
        len(change.current_line_widths_px) == len(change.target_line_widths_px) == 1,
        f"id {change.entry_id} declared line count is not one",
    )


for _change in CHANGES:
    validate_declared_change(_change)


def load_pinned_table(
    path: Path,
    *,
    label: str,
    expected_size: int,
    expected_sha256: str,
    require_literal_only: bool = False,
) -> TableResource:
    if not path.is_file():
        raise Wave15Error(f"{label} is absent: {path}")
    packed = path.read_bytes()
    require(len(packed) == expected_size, f"{label} size differs")
    require(sha256_bytes(packed) == expected_sha256, f"{label} SHA-256 differs")
    try:
        header, raw = decompress_wrapper(packed)
        table = parse_message_table(raw)
    except Exception as exc:
        raise Wave15Error(f"{label} cannot be parsed as a wrapped message table") from exc
    require(
        rebuild_message_table(table, table.texts) == raw,
        f"{label} unmodified message-table rebuild differs",
    )
    if require_literal_only:
        require(
            recompress_wrapper(raw, header) == packed,
            f"{label} is not the pinned literal-only LZ4 representation",
        )
    return TableResource(path.resolve(), packed, header, raw, table)


def load_current_steam_table(input_path: Path = CURRENT_STEAM_RESOURCE) -> TableResource:
    if input_path.resolve() != CURRENT_STEAM_RESOURCE.resolve():
        raise Wave15Error("Wave 15 accepts only the pinned current Steam PK msgev path")
    resource = load_pinned_table(
        CURRENT_STEAM_RESOURCE,
        label="current Steam PK msgev",
        expected_size=INPUT_SIZE,
        expected_sha256=INPUT_SHA256,
        require_literal_only=True,
    )
    require(len(resource.raw) == INPUT_RAW_SIZE, "current Steam PK msgev raw size differs")
    require(
        sha256_bytes(resource.raw) == INPUT_RAW_SHA256,
        "current Steam PK msgev raw SHA-256 differs",
    )
    return resource


def load_pc_anchors() -> tuple[TableResource, TableResource]:
    jp = load_pinned_table(
        PRISTINE_PC_JP_RESOURCE,
        label="pristine PC Japanese msgev",
        expected_size=PRISTINE_PC_JP_SIZE,
        expected_sha256=PRISTINE_PC_JP_SHA256,
    )
    en = load_pinned_table(
        PC_EN_RESOURCE,
        label="PC English msgev",
        expected_size=PC_EN_SIZE,
        expected_sha256=PC_EN_SHA256,
    )
    return jp, en


def _u32(value: bytes, offset: int, label: str) -> int:
    if offset < 0 or offset + 4 > len(value):
        raise Wave15Error(f"event font {label} is outside G1N data")
    return struct.unpack_from("<I", value, offset)[0]


def load_event_font_advance() -> tuple[Callable[[str], int], dict[str, Any]]:
    """Read only the active Steam event-font metrics needed by these names."""

    if not EVENT_FONT_RESOURCE.is_file():
        raise Wave15Error(f"active Steam event font is absent: {EVENT_FONT_RESOURCE}")
    packed = EVENT_FONT_RESOURCE.read_bytes()
    require(len(packed) == EVENT_FONT_SIZE, "active Steam event font size differs")
    require(sha256_bytes(packed) == EVENT_FONT_SHA256, "active Steam event font SHA-256 differs")
    try:
        archive = parse_link(packed)
        entry = archive.entries[FONT_OUTER_ENTRY]
        _wrapper, raw = decompress_wrapper(entry.data)
    except Exception as exc:
        raise Wave15Error("active Steam event font entry cannot be decoded") from exc

    require(raw[:8] == b"_N1G0000", "active Steam event font G1N magic differs")
    require(_u32(raw, 0x08, "declared size") == len(raw), "event font declared size differs")
    table_count = _u32(raw, 0x1C, "table count")
    require(1 <= table_count <= 32, "event font table count is implausible")
    require(FONT_TABLE < table_count, "event font table 0 is absent")
    table_offsets = tuple(_u32(raw, 0x20 + 4 * index, f"table {index} offset") for index in range(table_count))
    atlas_offset = _u32(raw, 0x14, "atlas offset")
    require(
        table_offsets == tuple(sorted(table_offsets)) and len(set(table_offsets)) == table_count,
        "event font table offsets differ",
    )
    table_offset = table_offsets[FONT_TABLE]
    table_end = table_offsets[FONT_TABLE + 1] if FONT_TABLE + 1 < table_count else atlas_offset
    record_start = table_offset + FONT_MAP_BYTES
    require(
        0 <= table_offset <= record_start <= table_end <= len(raw),
        "event font table 0 bounds differ",
    )
    record_bytes = table_end - record_start
    require(record_bytes % FONT_RECORD_BYTES == 0, "event font record region alignment differs")
    record_count = record_bytes // FONT_RECORD_BYTES
    require(record_count > 0, "event font has no table 0 records")
    mapping = struct.unpack_from("<65536H", raw, table_offset)

    def advance(character: str) -> int:
        codepoint = ord(character)
        ordinal = mapping[codepoint]
        if ordinal == 0:
            if WIDE_SCRIPT_RE.fullmatch(character) is not None:
                return 48
            raise Wave15Error(f"event font lacks U+{codepoint:04X}")
        if ordinal >= record_count:
            raise Wave15Error(f"event font maps U+{codepoint:04X} outside table 0")
        record_offset = record_start + ordinal * FONT_RECORD_BYTES
        width = raw[record_offset]
        glyph_advance = raw[record_offset + 4]
        if width != glyph_advance or glyph_advance not in (24, 48):
            raise Wave15Error(f"event font metric differs for U+{codepoint:04X}")
        return glyph_advance

    return advance, {
        "resource": "RES_JP/res_lang.bin",
        "size": EVENT_FONT_SIZE,
        "sha256": EVENT_FONT_SHA256,
        "outer_entry": FONT_OUTER_ENTRY,
        "g1n_table": FONT_TABLE,
        "g1n_size": len(raw),
        "table0_record_count": record_count,
    }


def visible_line_widths(value: str, advance: Callable[[str], int]) -> tuple[int, ...]:
    widths: list[int] = []
    for line in LINEBREAK_RE.sub("\n", value).split("\n"):
        width = 0
        cursor = 0
        while cursor < len(line):
            character = line[cursor]
            if character == "\x1b":
                token = line[cursor : cursor + 3]
                if ESC_RE.fullmatch(token) is None:
                    raise Wave15Error("event text contains malformed ESC token")
                cursor += 3
                continue
            if unicodedata.category(character) == "Cc":
                raise Wave15Error(f"event text contains control U+{ord(character):04X}")
            width += advance(character)
            cursor += 1
        widths.append(width)
    return tuple(widths)


def validate_live_change(
    change: Change,
    current_table: Any,
    jp_table: Any,
    en_table: Any,
    advance: Callable[[str], int],
) -> dict[str, Any]:
    for table, label in ((current_table, "current"), (jp_table, "JP"), (en_table, "EN")):
        require(change.entry_id < table.string_count, f"id {change.entry_id} is absent from {label}")

    current_text = current_table.texts[change.entry_id]
    jp_text = jp_table.texts[change.entry_id]
    en_text = en_table.texts[change.entry_id]
    require(current_text == change.current_text, f"id {change.entry_id} current text differs")
    require(jp_text == change.jp_anchor_text, f"id {change.entry_id} JP anchor text differs")
    require(en_text == change.en_anchor_text, f"id {change.entry_id} EN anchor text differs")
    require(
        text_hash(current_text) == change.current_text_sha256,
        f"id {change.entry_id} current text hash differs",
    )
    require(
        text_hash(jp_text) == change.jp_anchor_utf16le_sha256,
        f"id {change.entry_id} JP anchor hash differs",
    )
    require(
        text_hash(en_text) == change.en_anchor_utf16le_sha256,
        f"id {change.entry_id} EN anchor hash differs",
    )
    require(
        text_hash(change.target_text) == change.target_text_sha256,
        f"id {change.entry_id} target text hash differs",
    )

    current_signature = protected_signature(current_text)
    target_signature = protected_signature(change.target_text)
    require(
        current_signature == target_signature,
        f"id {change.entry_id} control/token/linebreak signature changed",
    )
    require(
        current_signature == EMPTY_STATIC_SIGNATURE,
        f"id {change.entry_id} unexpectedly has control/token/linebreak content",
    )

    current_widths = visible_line_widths(current_text, advance)
    target_widths = visible_line_widths(change.target_text, advance)
    require(
        current_widths == change.current_line_widths_px,
        f"id {change.entry_id} current font width differs",
    )
    require(
        target_widths == change.target_line_widths_px,
        f"id {change.entry_id} target font width differs",
    )
    require(len(target_widths) <= MAX_LINES, f"id {change.entry_id} exceeds {MAX_LINES} lines")
    require(
        all(width <= MAX_LINE_PX for width in target_widths),
        f"id {change.entry_id} exceeds {MAX_LINE_PX}px",
    )

    return {
        "id": change.entry_id,
        "current_text": current_text,
        "target_text": change.target_text,
        "current_utf16le_sha256": change.current_text_sha256,
        "target_utf16le_sha256": change.target_text_sha256,
        "anchors": {
            "pristine_pc_japanese_text": jp_text,
            "pristine_pc_japanese_utf16le_sha256": change.jp_anchor_utf16le_sha256,
            "pc_english_text": en_text,
            "pc_english_utf16le_sha256": change.en_anchor_utf16le_sha256,
        },
        "format_invariants": {
            "current": current_signature,
            "target": target_signature,
            "identical": True,
        },
        "layout": {
            "current_line_widths_px": list(current_widths),
            "target_line_widths_px": list(target_widths),
            "max_line_px": MAX_LINE_PX,
            "max_lines": MAX_LINES,
            "within_limit": True,
        },
    }


def validate_candidate(
    current: TableResource,
    candidate_packed: bytes,
    expected_texts: tuple[str, ...],
) -> tuple[bytes, Any]:
    require(len(candidate_packed) == TARGET_SIZE, "candidate packed size differs")
    require(sha256_bytes(candidate_packed) == TARGET_SHA256, "candidate packed SHA-256 differs")
    try:
        header, raw = decompress_wrapper(candidate_packed)
        table = parse_message_table(raw)
    except Exception as exc:
        raise Wave15Error("candidate cannot be parsed as a wrapped message table") from exc
    require(len(raw) == TARGET_RAW_SIZE, "candidate raw size differs")
    require(sha256_bytes(raw) == TARGET_RAW_SHA256, "candidate raw SHA-256 differs")
    require(rebuild_message_table(table, table.texts) == raw, "candidate table rebuild differs")
    require(recompress_wrapper(raw, header) == candidate_packed, "candidate LZ4 representation differs")
    require(header.prefix == current.header.prefix, "candidate LZ4 wrapper prefix changed")
    require(table.texts == expected_texts, "candidate text vector differs")
    changed_ids = {
        entry_id
        for entry_id, (before, after) in enumerate(zip(current.table.texts, table.texts))
        if before != after
    }
    require(changed_ids == set(CHANGE_BY_ID), f"candidate changed unexpected IDs: {sorted(changed_ids)}")
    for change in CHANGES:
        require(
            text_hash(table.texts[change.entry_id]) == change.target_text_sha256,
            f"id {change.entry_id} candidate target hash differs",
        )
    return raw, table


def build_manifest(audit: Mapping[str, Any]) -> dict[str, Any]:
    audit_sha256 = sha256_bytes(canonical_json(audit))
    return {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": PRIVATE_TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": RESOURCE_TEXT,
        "input": {"size": INPUT_SIZE, "sha256": INPUT_SHA256},
        "output": {"size": TARGET_SIZE, "sha256": TARGET_SHA256},
        "changed_ids": sorted(CHANGE_BY_ID),
        "audit_sha256": audit_sha256,
        "switch_korean_input": "forbidden",
        "steam_game_resource_write": "absent",
        "steam_apply": "not_implemented",
        "transaction": "not_implemented",
        "git_commit": "not_implemented",
        "network": "not_implemented",
    }


def prepare_candidate(input_path: Path = CURRENT_STEAM_RESOURCE) -> CandidateBundle:
    """Verify every fixed input and assemble the candidate wholly in memory."""

    current = load_current_steam_table(input_path)
    jp, en = load_pc_anchors()
    require(
        current.table.string_count == jp.table.string_count == en.table.string_count,
        "current/JP/EN msgev string counts differ",
    )
    advance, font_report = load_event_font_advance()

    target_texts = list(current.table.texts)
    record_audit: list[dict[str, Any]] = []
    for change in CHANGES:
        record_audit.append(validate_live_change(change, current.table, jp.table, en.table, advance))
        target_texts[change.entry_id] = change.target_text
    expected_texts = tuple(target_texts)

    candidate_raw = rebuild_message_table(current.table, expected_texts)
    require(len(candidate_raw) == TARGET_RAW_SIZE, "candidate raw size differs before compression")
    require(
        sha256_bytes(candidate_raw) == TARGET_RAW_SHA256,
        "candidate raw SHA-256 differs before compression",
    )
    candidate_packed = recompress_wrapper(candidate_raw, current.header)
    verified_raw, verified_table = validate_candidate(current, candidate_packed, expected_texts)
    require(verified_raw == candidate_raw, "candidate decompressed raw differs")

    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "platform": "Steam PC",
            "current_korean_input": "current Steam MSG_PK/JP/msgev.bin only",
            "pristine_pc_japanese_anchor_read": True,
            "pc_english_anchor_read": True,
            "switch_korean_read": False,
            "existing_korean_translation_artifacts_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
        },
        "resource": RESOURCE_TEXT,
        "input": {
            "size": INPUT_SIZE,
            "sha256": INPUT_SHA256,
            "raw_size": INPUT_RAW_SIZE,
            "raw_sha256": INPUT_RAW_SHA256,
            "string_count": current.table.string_count,
        },
        "anchors": {
            "pristine_pc_japanese": {
                "size": PRISTINE_PC_JP_SIZE,
                "sha256": PRISTINE_PC_JP_SHA256,
            },
            "pc_english": {"size": PC_EN_SIZE, "sha256": PC_EN_SHA256},
        },
        "font": font_report,
        "output": {
            "size": TARGET_SIZE,
            "sha256": TARGET_SHA256,
            "raw_size": TARGET_RAW_SIZE,
            "raw_sha256": TARGET_RAW_SHA256,
            "string_count": verified_table.string_count,
        },
        "only_changed_ids": sorted(CHANGE_BY_ID),
        "records": record_audit,
    }
    return CandidateBundle(candidate_packed, candidate_raw, audit, build_manifest(audit))


def atomic_write(path: Path, payload: bytes) -> None:
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    with temporary.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def remove_private_tree(path: Path) -> None:
    resolved = require_private_output(path, "private cleanup")
    if resolved.exists():
        shutil.rmtree(resolved)


def write_candidate(bundle: CandidateBundle, output_root: Path) -> dict[str, Any]:
    """Write one new candidate directory under tmp; never write Steam."""

    output_root = require_private_output(output_root)
    if output_root.exists():
        raise Wave15Error(f"refusing to overwrite candidate output: {output_root}")
    staging = output_root.parent / f".{output_root.name}.staging-{uuid.uuid4().hex}"
    staging = require_private_output(staging, "candidate staging output")
    if staging.exists():
        raise Wave15Error(f"candidate staging path already exists: {staging}")
    try:
        resource_path = staging / RESOURCE
        resource_path.parent.mkdir(parents=True, exist_ok=False)
        atomic_write(resource_path, bundle.packed)
        atomic_write(staging / "audit.v1.json", canonical_json(bundle.audit))
        atomic_write(staging / "candidate_manifest.v1.json", canonical_json(bundle.manifest))
        require(sha256_path(resource_path) == TARGET_SHA256, "written candidate SHA-256 differs")
        require(
            sha256_path(staging / "audit.v1.json") == bundle.manifest["audit_sha256"],
            "written audit SHA-256 differs",
        )
        os.replace(staging, output_root)
    except Exception:
        remove_private_tree(staging)
        raise
    return {
        "candidate": output_root.relative_to(REPO).as_posix(),
        "resource": (output_root / RESOURCE).relative_to(REPO).as_posix(),
        "audit": (output_root / "audit.v1.json").relative_to(REPO).as_posix(),
        "manifest": (output_root / "candidate_manifest.v1.json").relative_to(REPO).as_posix(),
        "target_sha256": TARGET_SHA256,
        "steam_game_resource_write": "absent",
    }


def print_json(value: Mapping[str, Any]) -> None:
    # Windows PowerShell hosts may use a legacy console code page.  The
    # artifacts themselves remain UTF-8, while stdout remains ASCII-safe.
    print(json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True))


def command_hash(_args: argparse.Namespace) -> int:
    bundle = prepare_candidate()
    print_json(
        {
            "status": "ok",
            "input_sha256": INPUT_SHA256,
            "target_sha256": sha256_bytes(bundle.packed),
            "changed_ids": sorted(CHANGE_BY_ID),
            "steam_game_resource_write": "absent",
        }
    )
    return 0


def command_build(args: argparse.Namespace) -> int:
    bundle = prepare_candidate()
    result = write_candidate(bundle, args.output_root)
    print_json({"status": "ok", **result})
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    hash_command = commands.add_parser("hash", help="verify the in-memory private candidate")
    hash_command.set_defaults(func=command_hash)
    build_command = commands.add_parser("build", help="write one private candidate below tmp")
    build_command.add_argument(
        "--output-root",
        type=Path,
        default=PRIVATE_TMP_ROOT / "candidate-v1",
        help="must be a new directory below this workstream's tmp root",
    )
    build_command.set_defaults(func=command_build)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError, Wave15Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
