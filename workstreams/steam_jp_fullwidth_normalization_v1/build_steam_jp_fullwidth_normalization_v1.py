#!/usr/bin/env python3
"""Audit and safely normalize inherited fullwidth punctuation in Steam JP text.

This workstream is deliberately limited to the Japanese Steam 1.1.7 route.
It never reads an SC resource, writes an installed game file, touches an EXE,
or changes fonts.  Its automatic character map is not a generic Unicode/NFKC
fold: its character map is derived from the pinned Switch v2.2 -> v2.3 text
delta, then every current Steam v0.9 Korean coordinate is independently
preimage-hash gated before it can be changed.  Newlines, ESC controls, printf
tokens, known tags/placeholders, PUA characters, and edge whitespace are all
preserved exactly.

``emit-public`` writes source-free coordinate/hash/reversal metadata only.
``verify`` rebuilds the candidate in memory and proves it can be restored to
the exact v0.9.0 input.  ``build`` and ``restore`` may write private, offline
ZIPs below ``KR_PATCH_WORK/tmp``; neither command can target a game folder.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import struct
import sys
import tempfile
import unicodedata
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = SCRIPT.parents[2]
TMP_ROOT = REPO / "tmp"
TOOLS = REPO / "tools"
MSGGAME_TOOLS = REPO / "workstreams" / "msggame"
STRDATA_TOOLS = REPO / "workstreams" / "switch_msgbre_v11"
for root in (TOOLS, MSGGAME_TOOLS, STRDATA_TOOLS):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

from nobu16_lz4 import (  # noqa: E402
    decompress_wrapper,
    parse_link,
    recompress_wrapper,
)
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402
from msggame_format import (  # noqa: E402
    iter_literals,
    parse_packed_msggame,
    rebuild_raw_with_literals,
)
from strdata_container import parse_strdata, rebuild_strdata  # noqa: E402


SCHEMA = "nobu16.kr.steam-jp-fullwidth-normalization.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-fullwidth-normalization-validation.v1"
METADATA_PATH = WORKSTREAM / "public" / "steam_jp_fullwidth_normalization.v1.json"
VALIDATION_PATH = WORKSTREAM / "validation.v1.json"

V09_ZIP = (
    TMP_ROOT
    / "steam_jp_117_image_candidate_v1_inputs"
    / "v0.9.0"
    / "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.9.0.zip"
)
SWITCH_V22_ZIP = (
    TMP_ROOT / "switch_wheel_button_audit" / "NobunagaShinsei_KoreanPatch_v2.2.zip"
)
SWITCH_V23_ZIP = (
    TMP_ROOT / "switch_wheel_button_audit" / "NobunagaShinsei_KoreanPatch_v2.3.zip"
)

V09_ZIP_PIN = {
    "name": "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.9.0.zip",
    "size": 356_951_693,
    "sha256": "1BCC92A3CD7025D307AF9B193BDDD8F1448451024630C8414FC218F0C49FE829",
}
# These two pins are filled from the public Switch v2.2/v2.3 release assets.
# Keep the archive identity gate separate from the coordinate-diff evidence.
SWITCH_ZIP_PINS: dict[str, dict[str, Any]] = {
    "v2.2": {
        "name": "NobunagaShinsei_KoreanPatch_v2.2.zip",
        "size": 83_752_794,
        "sha256": "5E6354069E38BE22E3B3C9272A6CEC8A4B4110DF2486B9A63E84D1058C35D7F7",
    },
    "v2.3": {
        "name": "NobunagaShinsei_KoreanPatch_v2.3.zip",
        "size": 83_756_574,
        "sha256": "A085B5D7F661786CF8E6568A36CF24E7BE1ADF81D042FF8C3D2E220D46A09388",
    },
}

TARGETS = (
    "MSG/JP/ev_strdata.bin",
    "MSG/JP/msggame.bin",
    "MSG/JP/strdata.bin",
    "MSG_PK/JP/msgbre.bin",
    "MSG_PK/JP/msgdata.bin",
    "MSG_PK/JP/msgev.bin",
    "MSG_PK/JP/msggame.bin",
    "MSG_PK/JP/msgire.bin",
    "MSG_PK/JP/msgstf.bin",
    "MSG_PK/JP/msgui.bin",
    "RES_JP/res_lang.bin",
    "RES_JP_PK/res_lang_pk.bin",
    "RES_JP_PK_PORT/res_lang_pk_port1.bin",
    "RES_JP_PK_PORT/res_lang_pk_port2.bin",
)
TEXT_KINDS = {
    "MSG/JP/ev_strdata.bin": "table",
    "MSG/JP/msggame.bin": "msggame",
    "MSG/JP/strdata.bin": "strdata",
    "MSG_PK/JP/msgbre.bin": "table",
    "MSG_PK/JP/msgdata.bin": "table",
    "MSG_PK/JP/msgev.bin": "table",
    "MSG_PK/JP/msggame.bin": "msggame",
    "MSG_PK/JP/msgire.bin": "table",
    "MSG_PK/JP/msgstf.bin": "table",
    "MSG_PK/JP/msgui.bin": "table",
}
FONT_G1N_ROUTES = {
    "RES_JP/res_lang.bin": (6, 7),
    "RES_JP_PK/res_lang_pk.bin": (16, 17),
    "RES_JP_PK_PORT/res_lang_pk_port1.bin": (1,),
    "RES_JP_PK_PORT/res_lang_pk_port2.bin": (0, 1),
}
SWITCH_TEXT_MEMBERS = {
    "MSG/JP/ev_strdata.bin": "NobunagaShinsei_KR/romfs/MSG/JP/ev_strdata.bin",
    "MSG/JP/msggame.bin": "NobunagaShinsei_KR/romfs/MSG/JP/msggame.bin",
    "MSG/JP/strdata.bin": "NobunagaShinsei_KR/romfs/MSG/JP/strdata.bin",
}
HANGUL_RE = re.compile(r"[\uAC00-\uD7A3]")
FULLWIDTH_RE = re.compile(r"[\uFF01-\uFF5E\u3000]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
PRINTF_RE = re.compile(
    r"%(?:[-+ #0]*)(?:\d+|\*)?(?:\.(?:\d+|\*))?"
    r"(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)
BRACED_PLACEHOLDER_RE = re.compile(r"\{(?:\d+|[A-Za-z_][A-Za-z0-9_.:-]*)\}")
ANGLE_TAG_RE = re.compile(
    r"</?[A-Za-z][A-Za-z0-9:_-]*(?:\s+[^<>\r\n]*)?/?>"
)
BRACKET_TAG_RE = re.compile(r"\[[A-Za-z_][A-Za-z0-9_.:-]*\]")
LINE_BREAK_RE = re.compile(r"\r\n|\n|\r")
LITERAL_START = b"\x07\x07\x01"
LITERAL_END = b"\x07\x07\x02"

# The broad candidate map encodes only ASCII-width counterparts.  The actual
# map used for a build is the strict v2.2->v2.3 observed subset, never this
# whole table by itself.
ASCII_FULLWIDTH_MAP = {
    **{chr(0xFF10 + offset): chr(0x30 + offset) for offset in range(10)},
    **{chr(0xFF01 + offset): chr(0x21 + offset) for offset in range(0x5E)},
    "\u3000": " ",
}
# This is intentionally not folded into the ASCII/fullwidth table.  It is a
# distinct, direction-gated punctuation operation.  The pinned Switch v2.2
# -> v2.3 evidence changes the Korean middle dot (U+00B7) to Japanese middle
# dot (U+30FB), not the reverse; a unit test locks that direction.
KOREAN_TO_JAPANESE_MIDDLE_DOT_MAP = {"\u00b7": "\u30fb"}

# Source-free, reproducible font witnesses for the *pinned* v0.9 input ZIP.
# They were obtained by decoding every table (three tables × seven live outer
# G1N entries) with ``_font_g1n_target_coverage``.  ``load_v09_documents``
# rejects any different ZIP before this witness can be used.
FULLWIDTH_ASCII_TARGET_CODEPOINTS = (
    0x0020, 0x0021, 0x0025, 0x0028, 0x0029, 0x002B, 0x002D, 0x002E,
    0x002F, 0x0030, 0x0031, 0x0032, 0x0033, 0x0034, 0x0035, 0x0036,
    0x0037, 0x0038, 0x0039, 0x003A, 0x003E, 0x003F, 0x005B, 0x005D,
    0x007E,
)


def _all_mapped_font_report(outer_entry: int) -> dict[str, Any]:
    return {
        "outer_entry": outer_entry,
        "table_count": 3,
        "missing_evidenced_target_codepoints_by_table": {"0": [], "1": [], "2": []},
        "all_evidenced_target_codepoints_mapped": True,
    }


PINNED_FULLWIDTH_ASCII_FONT_WITNESS = {
    "input_zip_sha256": V09_ZIP_PIN["sha256"],
    "evidenced_target_codepoints": [
        f"U+{codepoint:04X}" for codepoint in FULLWIDTH_ASCII_TARGET_CODEPOINTS
    ],
    "live_g1n_outer_entry_count": 7,
    "all_evidenced_targets_mapped_in_all_live_jp_g1ns": True,
    "per_font_route": {
        "RES_JP/res_lang.bin": [_all_mapped_font_report(6), _all_mapped_font_report(7)],
        "RES_JP_PK/res_lang_pk.bin": [_all_mapped_font_report(16), _all_mapped_font_report(17)],
        "RES_JP_PK_PORT/res_lang_pk_port1.bin": [_all_mapped_font_report(1)],
        "RES_JP_PK_PORT/res_lang_pk_port2.bin": [_all_mapped_font_report(0), _all_mapped_font_report(1)],
    },
}
PINNED_BASE_MIDDLE_DOT_FONT_WITNESS = {
    "resource": "RES_JP/res_lang.bin",
    "outer_entries": [6, 7],
    "source_u00b7": [_all_mapped_font_report(6), _all_mapped_font_report(7)],
    "target_u30fb": [
        {
            "outer_entry": outer_entry,
            "table_count": 3,
            "missing_evidenced_target_codepoints_by_table": {
                "0": [], "1": [], "2": ["U+30FB"]
            },
            "all_evidenced_target_codepoints_mapped": False,
        }
        for outer_entry in (6, 7)
    ],
    "target_missing_codepoints": ["U+30FB"],
}


class NormalizationError(RuntimeError):
    """An input, invariant, or reversibility gate failed."""


@dataclass(frozen=True)
class TextCell:
    coordinate: tuple[int, ...]
    text: str


@dataclass(frozen=True)
class TextDocument:
    resource: str
    kind: str
    packed: bytes
    cells: tuple[TextCell, ...]
    rebuild: Callable[[Mapping[tuple[int, ...], str]], bytes]


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def spec(blob: bytes) -> dict[str, Any]:
    return {"size": len(blob), "sha256": sha256(blob)}


def file_spec(path: Path) -> dict[str, Any]:
    """Hash large input/output archives without retaining them in memory."""

    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
            size += len(chunk)
    return {"size": size, "sha256": digest.hexdigest().upper()}


def text_hash(text: str) -> str:
    return sha256(text.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def require(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise NormalizationError(f"{label} differs: expected={expected!r}, actual={actual!r}")


def require_true(value: Any, label: str) -> None:
    if value is not True:
        raise NormalizationError(f"{label} must be true")


def coord_json(coordinate: tuple[int, ...], kind: str) -> dict[str, int]:
    if kind == "table":
        return {"id": coordinate[0]}
    if kind == "strdata":
        return {"block_id": coordinate[0], "slot_id": coordinate[1]}
    if kind == "msggame":
        return {
            "block_id": coordinate[0],
            "record_id": coordinate[1],
            "literal_id": coordinate[2],
        }
    raise NormalizationError(f"unknown text kind: {kind}")


def coord_from_json(value: Any, kind: str) -> tuple[int, ...]:
    expected = {
        "table": ("id",),
        "strdata": ("block_id", "slot_id"),
        "msggame": ("block_id", "record_id", "literal_id"),
    }.get(kind)
    # Public metadata is serialized with sorted JSON keys.  Coordinates are
    # mappings, so their insertion order is not semantic; comparing it here
    # would reject a canonical ``block_id,literal_id,record_id`` msggame
    # object even though it has the exact required key set.  Keep the contract
    # strict by accepting only the exact set of keys, then read values in the
    # schema-defined coordinate order below.
    if expected is None or not isinstance(value, dict) or set(value) != set(expected):
        raise NormalizationError(f"invalid {kind} coordinate")
    result = tuple(value[key] for key in expected)
    if any(type(item) is not int or item < 0 for item in result):
        raise NormalizationError(f"invalid {kind} coordinate value")
    return result


def _token_spans(text: str) -> tuple[tuple[int, int], ...]:
    """Return non-overlapping control/placeholder spans in deterministic order."""

    matches: list[tuple[int, int]] = []
    for pattern in (
        ESC_RE,
        PRINTF_RE,
        BRACED_PLACEHOLDER_RE,
        ANGLE_TAG_RE,
        BRACKET_TAG_RE,
    ):
        matches.extend((match.start(), match.end()) for match in pattern.finditer(text))
    matches.sort()
    result: list[tuple[int, int]] = []
    for start, end in matches:
        if result and start < result[-1][1]:
            # Nested/overlapping patterns are still protected as one opaque span.
            prior_start, prior_end = result[-1]
            result[-1] = (prior_start, max(prior_end, end))
        else:
            result.append((start, end))
    return tuple(result)


def protected_signature(text: str) -> dict[str, Any]:
    """Return the full non-layout-changing contract for a text cell."""

    esc = [match.group(0) for match in ESC_RE.finditer(text)]
    printf = [match.group(0) for match in PRINTF_RE.finditer(text)]
    placeholders = [match.group(0) for match in BRACED_PLACEHOLDER_RE.finditer(text)]
    angle_tags = [match.group(0) for match in ANGLE_TAG_RE.finditer(text)]
    bracket_tags = [match.group(0) for match in BRACKET_TAG_RE.finditer(text)]
    protected_indexes = {
        index
        for start, end in _token_spans(text)
        for index in range(start, end)
    }
    controls = [
        f"U+{ord(char):04X}"
        for index, char in enumerate(text)
        if unicodedata.category(char) == "Cc"
        and char not in ("\r", "\n")
        and index not in protected_indexes
    ]
    return {
        "esc": esc,
        "printf": printf,
        "brace_placeholders": placeholders,
        "angle_tags": angle_tags,
        "bracket_tags": bracket_tags,
        "controls": controls,
        "line_breaks": LINE_BREAK_RE.findall(text),
        "pua": [f"U+{ord(char):04X}" for char in text if 0xE000 <= ord(char) <= 0xF8FF],
        "leading_whitespace": text[: len(text) - len(text.lstrip())],
        "trailing_whitespace": text[len(text.rstrip()) :],
    }


def normalization_operations(
    text: str,
    mapping: Mapping[str, str],
    operation_types: Mapping[str, str] | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    """Normalize only non-protected, evidenced characters and record reversal ops."""

    protected = _token_spans(text)
    # Indentation and deliberate trailing layout are content, even when an
    # upstream fullwidth-space normalization would make the glyph narrower.
    # The linebreak workstream owns layout changes; this pass never does.
    leading_end = len(text) - len(text.lstrip())
    trailing_start = len(text.rstrip())
    spans = iter(protected)
    active = next(spans, None)
    result: list[str] = []
    operations: list[dict[str, Any]] = []
    for index, char in enumerate(text):
        while active is not None and index >= active[1]:
            active = next(spans, None)
        is_protected = (
            (active is not None and active[0] <= index < active[1])
            or index < leading_end
            or index >= trailing_start
        )
        replacement = mapping.get(char)
        if replacement is not None and not is_protected:
            if len(replacement) != 1:
                raise NormalizationError("normalization map must retain one code point per character")
            result.append(replacement)
            operations.append(
                {
                    "operation_type": (operation_types or {}).get(char, "fullwidth_ascii"),
                    "char_index": index,
                    "from": f"U+{ord(char):04X}",
                    "to": f"U+{ord(replacement):04X}",
                }
            )
        else:
            result.append(char)
    normalized = "".join(result)
    if len(normalized) != len(text):
        raise NormalizationError("normalization changed string codepoint length")
    if protected_signature(normalized) != protected_signature(text):
        raise NormalizationError("normalization altered a protected/layout invariant")
    return normalized, operations


def reverse_operations(text: str, operations: Sequence[Mapping[str, Any]]) -> str:
    """Reverse an exact coordinate operation list, rejecting stale/ambiguous input."""

    output = list(text)
    prior_index = len(output)
    for operation in reversed(list(operations)):
        index = operation.get("char_index")
        before = operation.get("from")
        after = operation.get("to")
        operation_type = operation.get("operation_type")
        if type(index) is not int or not 0 <= index < len(output) or index >= prior_index:
            raise NormalizationError("invalid/non-descending reversal character index")
        if not isinstance(before, str) or not isinstance(after, str):
            raise NormalizationError("invalid reversal codepoint")
        if operation_type not in {
            "fullwidth_ascii",
            "korean_middle_dot_to_japanese_middle_dot",
        }:
            raise NormalizationError("invalid reversal operation type")
        try:
            before_char = chr(int(before.removeprefix("U+"), 16))
            after_char = chr(int(after.removeprefix("U+"), 16))
        except ValueError as exc:
            raise NormalizationError("invalid reversal codepoint notation") from exc
        if output[index] != after_char:
            raise NormalizationError("reversal input does not have the documented normalized character")
        output[index] = before_char
        prior_index = index
    return "".join(output)


def _document_table(
    resource: str, packed: bytes, *, require_identity: bool = True
) -> TextDocument:
    header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    if require_identity and rebuild_message_table(table, table.texts) != raw:
        raise NormalizationError(f"{resource}: table parse/rebuild is not byte-exact")
    cells = tuple(TextCell((entry_id,), text) for entry_id, text in enumerate(table.texts))

    def rebuild(replacements: Mapping[tuple[int, ...], str]) -> bytes:
        texts = list(table.texts)
        for coordinate, value in replacements.items():
            if len(coordinate) != 1 or coordinate[0] >= len(texts):
                raise NormalizationError(f"{resource}: invalid table replacement coordinate")
            texts[coordinate[0]] = value
        candidate_raw = rebuild_message_table(table, texts)
        check = parse_message_table(candidate_raw)
        if check.texts != tuple(texts):
            raise NormalizationError(f"{resource}: rebuilt table text verification failed")
        return recompress_wrapper(candidate_raw, header)

    return TextDocument(resource, "table", packed, cells, rebuild)


def _document_strdata(
    resource: str, packed: bytes, *, require_identity: bool = True
) -> TextDocument:
    header, raw = decompress_wrapper(packed)
    archive = parse_strdata(raw)
    if require_identity and rebuild_strdata(archive) != raw:
        raise NormalizationError(f"{resource}: strdata parse/rebuild is not byte-exact")
    cells = tuple(
        TextCell((block.block_id, slot_id), text)
        for block in archive.blocks
        for slot_id, text in enumerate(block.texts)
    )

    def rebuild(replacements: Mapping[tuple[int, ...], str]) -> bytes:
        block_texts = {block.block_id: list(block.texts) for block in archive.blocks}
        for coordinate, value in replacements.items():
            if len(coordinate) != 2 or coordinate[0] not in block_texts:
                raise NormalizationError(f"{resource}: invalid strdata replacement coordinate")
            block_id, slot_id = coordinate
            if slot_id >= len(block_texts[block_id]):
                raise NormalizationError(f"{resource}: strdata slot is out of range")
            block_texts[block_id][slot_id] = value
        candidate_raw = rebuild_strdata(archive, block_texts)
        check = parse_strdata(candidate_raw)
        expected = {
            (block_id, slot_id): value
            for block_id, values in block_texts.items()
            for slot_id, value in enumerate(values)
        }
        observed = {
            (block.block_id, slot_id): value
            for block in check.blocks
            for slot_id, value in enumerate(block.texts)
        }
        if observed != expected:
            raise NormalizationError(f"{resource}: rebuilt strdata text verification failed")
        return recompress_wrapper(candidate_raw, header)

    return TextDocument(resource, "strdata", packed, cells, rebuild)


def _document_msggame(
    resource: str, packed: bytes, *, require_identity: bool = True
) -> TextDocument:
    parsed = parse_packed_msggame(packed)
    raw = rebuild_raw_with_literals(parsed.archive, {})
    _header, original_raw = decompress_wrapper(packed)
    if require_identity and raw != original_raw:
        raise NormalizationError(f"{resource}: msggame parse/rebuild is not byte-exact")
    cells = tuple(
        TextCell((literal.block_id, literal.record_id, literal.literal_id), literal.text)
        for literal in iter_literals(parsed.archive)
    )

    def rebuild(replacements: Mapping[tuple[int, ...], str]) -> bytes:
        candidate_raw = rebuild_raw_with_literals(parsed.archive, replacements)
        check_packed = recompress_wrapper(candidate_raw, parsed.header)
        check = parse_packed_msggame(check_packed)
        observed = {
            (literal.block_id, literal.record_id, literal.literal_id): literal.text
            for literal in iter_literals(check.archive)
        }
        expected = {cell.coordinate: replacements.get(cell.coordinate, cell.text) for cell in cells}
        if observed != expected:
            raise NormalizationError(f"{resource}: rebuilt msggame text verification failed")
        return check_packed

    return TextDocument(resource, "msggame", packed, cells, rebuild)


def _switch_msggame_evidence_document(resource: str, packed: bytes) -> TextDocument:
    """Read Switch literals without importing its non-PC alignment convention.

    The Switch v2.2/v2.3 archives are evidence only.  They use block placement
    that is valid for that platform but is not the byte-exact Steam-PC
    alignment contract enforced by :func:`parse_packed_msggame`.  This reader
    deliberately has no rebuild path; it validates all directory and literal
    ranges before exposing coordinate text for a v2.2->v2.3 comparison.
    """

    _header, raw = decompress_wrapper(packed)
    if len(raw) < 4:
        raise NormalizationError(f"{resource}: Switch msggame is truncated")
    block_count = struct.unpack_from("<I", raw, 0)[0]
    directory_end = 4 + block_count * 8
    if directory_end > len(raw):
        raise NormalizationError(f"{resource}: Switch msggame directory exceeds raw data")
    blocks = [
        struct.unpack_from("<II", raw, 4 + block_id * 8)
        for block_id in range(block_count)
    ]
    if any(offset < directory_end or size < 4 or offset + size > len(raw) for offset, size in blocks):
        raise NormalizationError(f"{resource}: Switch msggame block range is invalid")
    if blocks != sorted(blocks):
        raise NormalizationError(f"{resource}: Switch msggame block order is invalid")
    cells: list[TextCell] = []
    for block_id, (block_offset, block_size) in enumerate(blocks):
        record_count = struct.unpack_from("<I", raw, block_offset)[0]
        table_end = 4 + record_count * 4
        if table_end > block_size:
            raise NormalizationError(f"{resource}: Switch record table exceeds its block")
        offsets = [
            struct.unpack_from("<I", raw, block_offset + 4 + 4 * record_id)[0]
            for record_id in range(record_count)
        ]
        if record_count and offsets[0] != table_end:
            raise NormalizationError(f"{resource}: Switch first record offset differs")
        if offsets != sorted(offsets) or any(offset < table_end or offset > block_size for offset in offsets):
            raise NormalizationError(f"{resource}: Switch record offsets are invalid")
        for record_id, relative_start in enumerate(offsets):
            relative_end = offsets[record_id + 1] if record_id + 1 < record_count else block_size
            payload = raw[block_offset + relative_start : block_offset + relative_end]
            cursor = 0
            literal_id = 0
            while True:
                start = payload.find(LITERAL_START, cursor)
                orphan_end = payload.find(LITERAL_END, cursor)
                if start < 0:
                    if orphan_end >= 0:
                        raise NormalizationError(f"{resource}: Switch orphan literal end")
                    break
                if 0 <= orphan_end < start:
                    raise NormalizationError(f"{resource}: Switch orphan literal end")
                text_start = start + len(LITERAL_START)
                end = payload.find(LITERAL_END, text_start)
                if end < 0 or payload.find(LITERAL_START, text_start, end) >= 0:
                    raise NormalizationError(f"{resource}: Switch malformed literal marker")
                encoded = payload[text_start:end]
                if len(encoded) % 2:
                    raise NormalizationError(f"{resource}: Switch literal has odd UTF-16 length")
                try:
                    text = encoded.decode("utf-16le")
                except UnicodeDecodeError as exc:
                    raise NormalizationError(f"{resource}: Switch literal is invalid UTF-16") from exc
                cells.append(TextCell((block_id, record_id, literal_id), text))
                literal_id += 1
                cursor = end + len(LITERAL_END)

    def evidence_only_rebuild(_: Mapping[tuple[int, ...], str]) -> bytes:
        raise NormalizationError("Switch evidence documents cannot be rebuilt as Steam candidates")

    return TextDocument(resource, "msggame", packed, tuple(cells), evidence_only_rebuild)


def _switch_strdata_evidence_document(resource: str, packed: bytes) -> TextDocument:
    """Read Switch ``strdata`` dynamically without imposing PC slot locks."""

    _header, raw = decompress_wrapper(packed)
    if len(raw) < 0x2C:
        raise NormalizationError(f"{resource}: Switch strdata is truncated")
    block_count, header_size = struct.unpack_from("<II", raw, 0)
    if block_count != 5 or header_size != 0x2C:
        raise NormalizationError(f"{resource}: Switch strdata outer header differs")
    descriptors: list[tuple[int, int]] = [(header_size, struct.unpack_from("<I", raw, 8)[0])]
    for block_id in range(1, block_count):
        descriptors.append(struct.unpack_from("<II", raw, 12 + 8 * (block_id - 1)))
    cells: list[TextCell] = []
    previous_end = header_size
    for block_id, (offset, logical_size) in enumerate(descriptors):
        next_offset = descriptors[block_id + 1][0] if block_id + 1 < block_count else len(raw)
        logical_end = offset + logical_size
        if offset != previous_end or logical_end > next_offset or next_offset > len(raw):
            raise NormalizationError(f"{resource}: Switch strdata block placement is invalid")
        inner = raw[offset:logical_end]
        if len(inner) < 0x14 or struct.unpack_from("<I", inner, 0x0C)[0] != 0x14:
            raise NormalizationError(f"{resource}: Switch strdata inner header differs")
        gap = raw[logical_end:next_offset]
        synthetic = struct.pack("<III", 1, 0x0C, len(inner)) + inner + gap
        try:
            table = parse_message_table(synthetic)
        except ValueError as exc:
            raise NormalizationError(f"{resource}: Switch strdata table is invalid") from exc
        cells.extend(TextCell((block_id, slot_id), text) for slot_id, text in enumerate(table.texts))
        previous_end = next_offset
    if previous_end != len(raw):
        raise NormalizationError(f"{resource}: Switch strdata does not consume raw input")

    def evidence_only_rebuild(_: Mapping[tuple[int, ...], str]) -> bytes:
        raise NormalizationError("Switch evidence documents cannot be rebuilt as Steam candidates")

    return TextDocument(resource, "strdata", packed, tuple(cells), evidence_only_rebuild)


def parse_document(
    resource: str, packed: bytes, *, require_identity: bool = True
) -> TextDocument:
    kind = TEXT_KINDS.get(resource)
    if kind == "table":
        return _document_table(resource, packed, require_identity=require_identity)
    if kind == "strdata":
        return _document_strdata(resource, packed, require_identity=require_identity)
    if kind == "msggame":
        return _document_msggame(resource, packed, require_identity=require_identity)
    raise NormalizationError(f"{resource} is not an active text resource")


def _read_zip(path: Path, expected: Mapping[str, Any], label: str) -> zipfile.ZipFile:
    if path.name != expected["name"] or not path.is_file():
        raise NormalizationError(f"{label} path/name is invalid")
    actual = file_spec(path)
    require(
        actual,
        {"size": expected["size"], "sha256": expected["sha256"]},
        f"{label} pin",
    )
    try:
        return zipfile.ZipFile(path, "r")
    except zipfile.BadZipFile as exc:
        raise NormalizationError(f"{label} is not a valid ZIP") from exc


def load_v09_documents(path: Path) -> tuple[dict[str, bytes], dict[str, TextDocument]]:
    with _read_zip(path, V09_ZIP_PIN, "v0.9 input") as archive:
        names = archive.namelist()
        if names != list(TARGETS):
            raise NormalizationError("v0.9 input member vector is not the exact fourteen-file vector")
        payloads = {relative: archive.read(relative) for relative in TARGETS}
    documents = {relative: parse_document(relative, payloads[relative]) for relative in TEXT_KINDS}
    return payloads, documents


def load_switch_documents(path: Path, release: str) -> dict[str, TextDocument]:
    pin = SWITCH_ZIP_PINS[release]
    with _read_zip(path, pin, f"Switch {release}") as archive:
        result: dict[str, TextDocument] = {}
        for resource, member in SWITCH_TEXT_MEMBERS.items():
            try:
                # v2.2/v2.3 are read-only evidence sources.  Their older
                # table padding is not necessarily canonical for the Steam
                # rebuild codec, so only the strict parser is required here;
                # byte-identity is retained as a mandatory gate for v0.9 and
                # every produced Steam candidate.
                packed = archive.read(member)
                kind = TEXT_KINDS[resource]
                result[resource] = (
                    _switch_msggame_evidence_document(resource, packed)
                    if kind == "msggame"
                    else _switch_strdata_evidence_document(resource, packed)
                    if kind == "strdata"
                    else parse_document(resource, packed, require_identity=False)
                )
            except KeyError as exc:
                raise NormalizationError(f"Switch {release} is missing {member}") from exc
    return result


def cell_map(document: TextDocument) -> dict[tuple[int, ...], str]:
    result = {cell.coordinate: cell.text for cell in document.cells}
    if len(result) != len(document.cells):
        raise NormalizationError(f"{document.resource}: duplicate text coordinate")
    return result


def codepoint_pair_map(
    before: str, after: str, allowed: Mapping[str, str]
) -> dict[str, str] | None:
    """Return exact allowed substitutions iff no other character differs."""

    if len(before) != len(after):
        return None
    pairs: dict[str, str] = {}
    for left, right in zip(before, after, strict=True):
        if left == right:
            continue
        if allowed.get(left) != right:
            return None
        if left in pairs and pairs[left] != right:
            return None
        pairs[left] = right
    return pairs if pairs else None


def classify_switch_v23_changes(
    before_docs: Mapping[str, TextDocument], after_docs: Mapping[str, TextDocument]
) -> dict[str, Any]:
    """Derive a character map from coordinate-aligned v2.2/v2.3 evidence.

    Fullwidth-to-ASCII and Korean-middle-dot-to-Japanese-middle-dot remain
    distinct evidence classes.  A row may contain both classes, but only when
    its control/layout signature is unchanged is it allowed to contribute an
    automatic punctuation map.  Linebreak-only rows are reported separately
    and never become operations in this workstream.
    """

    resources: dict[str, Any] = {}
    observed_fullwidth: dict[str, str] = {}
    observed_korean_middle_dot: dict[str, str] = {}
    total_changed = 0
    total_fullwidth = 0
    total_korean_middle_dot = 0
    total_punctuation = 0
    total_non_punctuation_changed = 0
    allowed = ASCII_FULLWIDTH_MAP | KOREAN_TO_JAPANESE_MIDDLE_DOT_MAP
    operation_types = {
        **{key: "fullwidth_ascii" for key in ASCII_FULLWIDTH_MAP},
        **{
            key: "korean_middle_dot_to_japanese_middle_dot"
            for key in KOREAN_TO_JAPANESE_MIDDLE_DOT_MAP
        },
    }
    for resource in SWITCH_TEXT_MEMBERS:
        before = cell_map(before_docs[resource])
        after = cell_map(after_docs[resource])
        if set(before) != set(after):
            raise NormalizationError(f"Switch v2.2/v2.3 coordinates differ: {resource}")
        punctuation_rows: list[dict[str, Any]] = []
        changed = 0
        for coordinate in sorted(before):
            old, new = before[coordinate], after[coordinate]
            if old == new:
                continue
            changed += 1
            pairs = codepoint_pair_map(old, new, allowed)
            if (
                pairs
                and HANGUL_RE.search(old)
                and protected_signature(old) == protected_signature(new)
                and normalization_operations(old, pairs, operation_types)[0] == new
            ):
                for left, right in pairs.items():
                    target = (
                        observed_fullwidth
                        if left in ASCII_FULLWIDTH_MAP
                        else observed_korean_middle_dot
                    )
                    current = target.get(left)
                    if current is not None and current != right:
                        raise NormalizationError("Switch v2.3 map is not one-to-one")
                    target[left] = right
                row_types = sorted({operation_types[left] for left in pairs})
                punctuation_rows.append(
                    {
                        "coordinate": coord_json(coordinate, before_docs[resource].kind),
                        "before_utf16le_sha256": text_hash(old),
                        "after_utf16le_sha256": text_hash(new),
                        "operation_types": row_types,
                        "mapping": {
                            f"U+{ord(left):04X}": f"U+{ord(right):04X}"
                            for left, right in sorted(pairs.items())
                        },
                    }
                )
        resources[resource] = {
            "kind": before_docs[resource].kind,
            "v22_v23_changed_coordinate_count": changed,
            "punctuation_only_coordinate_count": len(punctuation_rows),
            "fullwidth_ascii_coordinate_count": sum(
                "fullwidth_ascii" in row["operation_types"] for row in punctuation_rows
            ),
            "korean_middle_dot_coordinate_count": sum(
                "korean_middle_dot_to_japanese_middle_dot" in row["operation_types"]
                for row in punctuation_rows
            ),
            # A changed row that is not a pure punctuation row may also have
            # forced-break edits.  It is deliberately left to the independent
            # linebreak workstream rather than guessed here.
            "non_punctuation_changed_coordinate_count": changed - len(punctuation_rows),
            "punctuation_only_coordinates": punctuation_rows,
        }
        total_changed += changed
        total_punctuation += len(punctuation_rows)
        total_fullwidth += resources[resource]["fullwidth_ascii_coordinate_count"]
        total_korean_middle_dot += resources[resource]["korean_middle_dot_coordinate_count"]
        total_non_punctuation_changed += resources[resource]["non_punctuation_changed_coordinate_count"]
    return {
        "source_release_pair": ["v2.2", "v2.3"],
        "resources": resources,
        "observed_fullwidth_map": {
            f"U+{ord(left):04X}": f"U+{ord(right):04X}"
            for left, right in sorted(observed_fullwidth.items())
        },
        "observed_korean_middle_dot_map": {
            f"U+{ord(left):04X}": f"U+{ord(right):04X}"
            for left, right in sorted(observed_korean_middle_dot.items())
        },
        "v22_v23_changed_coordinate_count": total_changed,
        "punctuation_only_coordinate_count": total_punctuation,
        "fullwidth_ascii_coordinate_count": total_fullwidth,
        "korean_middle_dot_coordinate_count": total_korean_middle_dot,
        "non_punctuation_changed_coordinate_count": total_non_punctuation_changed,
        "linebreak_changes_not_classified_by_this_workstream": True,
    }


def _decode_evidenced_map(
    raw: Any, allowed: Mapping[str, str], label: str
) -> dict[str, str]:
    if not isinstance(raw, dict) or not raw:
        raise NormalizationError(f"Switch v2.3 observed {label} map is absent")
    result: dict[str, str] = {}
    for before, after in raw.items():
        if not isinstance(before, str) or not isinstance(after, str):
            raise NormalizationError(f"invalid Switch v2.3 {label} codepoint map")
        try:
            left = chr(int(before.removeprefix("U+"), 16))
            right = chr(int(after.removeprefix("U+"), 16))
        except ValueError as exc:
            raise NormalizationError(f"invalid Switch v2.3 {label} codepoint notation") from exc
        if allowed.get(left) != right:
            raise NormalizationError(f"Switch v2.3 map is outside explicit {label} policy")
        if left in result or right in result.values():
            raise NormalizationError("Switch v2.3 map is non-bijective")
        result[left] = right
    return result


def map_from_evidence(evidence: Mapping[str, Any]) -> dict[str, str]:
    fullwidth = _decode_evidenced_map(
        evidence.get("observed_fullwidth_map"), ASCII_FULLWIDTH_MAP, "fullwidth ASCII"
    )
    middle_dot = _decode_evidenced_map(
        evidence.get("observed_korean_middle_dot_map"),
        KOREAN_TO_JAPANESE_MIDDLE_DOT_MAP,
        "Korean middle dot",
    )
    if set(fullwidth).intersection(middle_dot) or set(fullwidth.values()).intersection(middle_dot.values()):
        raise NormalizationError("Switch v2.3 punctuation maps overlap")
    return fullwidth | middle_dot


def operation_types_from_map(mapping: Mapping[str, str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for before, after in mapping.items():
        if ASCII_FULLWIDTH_MAP.get(before) == after:
            result[before] = "fullwidth_ascii"
        elif KOREAN_TO_JAPANESE_MIDDLE_DOT_MAP.get(before) == after:
            result[before] = "korean_middle_dot_to_japanese_middle_dot"
        else:
            raise NormalizationError("automatic punctuation map includes an unsupported conversion")
    return result


def scan_active_candidate(
    documents: Mapping[str, TextDocument], mapping: Mapping[str, str]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Scan every active v0.9 JP text resource, not just dialogue resources."""

    operations: list[dict[str, Any]] = []
    resource_counts: dict[str, Any] = {}
    korean_cell_count = 0
    inherited_punctuation_cells = 0
    types = operation_types_from_map(mapping)
    for resource in TEXT_KINDS:
        document = documents[resource]
        resource_ops: list[dict[str, Any]] = []
        korean_cells = 0
        inherited_punctuation = 0
        for cell in document.cells:
            if HANGUL_RE.search(cell.text) is None:
                continue
            korean_cells += 1
            if not any(char in mapping for char in cell.text):
                continue
            inherited_punctuation += 1
            try:
                normalized, char_ops = normalization_operations(cell.text, mapping, types)
            except NormalizationError as exc:
                raise NormalizationError(
                    f"{resource} {cell.coordinate}: {exc}"
                ) from exc
            if normalized == cell.text:
                # It was only inside an explicitly protected token.
                continue
            entry = {
                "resource": resource,
                "kind": document.kind,
                "coordinate": coord_json(cell.coordinate, document.kind),
                "before_utf16le_sha256": text_hash(cell.text),
                "after_utf16le_sha256": text_hash(normalized),
                "character_operations": char_ops,
                "protected_invariants": protected_signature(cell.text),
            }
            if reverse_operations(normalized, char_ops) != cell.text:
                raise NormalizationError("reversal operation did not reproduce source text")
            resource_ops.append(entry)
        operations.extend(resource_ops)
        resource_counts[resource] = {
            "kind": document.kind,
            "text_coordinate_count": len(document.cells),
            "korean_coordinate_count": korean_cells,
            "coordinates_containing_evidenced_punctuation_characters": inherited_punctuation,
            "automatic_normalization_coordinate_count": len(resource_ops),
            "automatic_normalization_character_count": sum(
                len(row["character_operations"]) for row in resource_ops
            ),
            "automatic_fullwidth_ascii_character_count": sum(
                row["operation_type"] == "fullwidth_ascii"
                for entry in resource_ops
                for row in entry["character_operations"]
            ),
            "automatic_korean_middle_dot_character_count": sum(
                row["operation_type"] == "korean_middle_dot_to_japanese_middle_dot"
                for entry in resource_ops
                for row in entry["character_operations"]
            ),
        }
        korean_cell_count += korean_cells
        inherited_punctuation_cells += inherited_punctuation
    return operations, {
        "active_text_resource_count": len(TEXT_KINDS),
        "active_text_coordinate_count": sum(len(document.cells) for document in documents.values()),
        "active_korean_coordinate_count": korean_cell_count,
        "coordinates_containing_evidenced_punctuation_characters": inherited_punctuation_cells,
        "automatic_normalization_coordinate_count": len(operations),
        "automatic_normalization_character_count": sum(
            len(row["character_operations"]) for row in operations
        ),
        "automatic_fullwidth_ascii_character_count": sum(
            row["operation_type"] == "fullwidth_ascii"
            for entry in operations
            for row in entry["character_operations"]
        ),
        "automatic_korean_middle_dot_character_count": sum(
            row["operation_type"] == "korean_middle_dot_to_japanese_middle_dot"
            for entry in operations
            for row in entry["character_operations"]
        ),
        "per_resource": resource_counts,
    }


def operations_by_resource(
    metadata: Mapping[str, Any],
    documents: Mapping[str, TextDocument],
    *,
    reverse: bool = False,
) -> dict[str, dict[tuple[int, ...], str]]:
    raw_ops = metadata.get("operations")
    if not isinstance(raw_ops, list):
        raise NormalizationError("normalization operations are missing")
    result = {resource: {} for resource in TEXT_KINDS}
    for entry in raw_ops:
        if not isinstance(entry, dict):
            raise NormalizationError("normalization operation is not an object")
        resource = entry.get("resource")
        kind = entry.get("kind")
        if resource not in documents or kind != documents[resource].kind:
            raise NormalizationError("normalization operation resource/kind differs")
        coordinate = coord_from_json(entry.get("coordinate"), str(kind))
        cells = cell_map(documents[resource])
        source = cells.get(coordinate)
        if source is None:
            raise NormalizationError("normalization operation coordinate is absent")
        original_hash = entry.get("before_utf16le_sha256")
        normalized_hash = entry.get("after_utf16le_sha256")
        char_ops = entry.get("character_operations")
        if not isinstance(char_ops, list):
            raise NormalizationError("normalization operation character list is absent")
        if reverse:
            if text_hash(source) != normalized_hash:
                raise NormalizationError("reverse input text hash differs")
            target = reverse_operations(source, char_ops)
            if text_hash(target) != original_hash:
                raise NormalizationError("reverse output text hash differs")
        else:
            if text_hash(source) != original_hash:
                raise NormalizationError("normalization input text hash differs")
            automatic_map = map_from_metadata(metadata)
            target, observed = normalization_operations(
                source, automatic_map, operation_types_from_map(automatic_map)
            )
            if observed != char_ops or text_hash(target) != normalized_hash:
                raise NormalizationError("normalization operation differs from metadata")
        if protected_signature(source) != entry.get("protected_invariants"):
            raise NormalizationError("normalization protected invariant differs")
        if coordinate in result[resource]:
            raise NormalizationError("duplicate normalization coordinate")
        result[resource][coordinate] = target
    return result


def map_from_metadata(metadata: Mapping[str, Any]) -> dict[str, str]:
    policy = metadata.get("automatic_policy")
    if not isinstance(policy, dict):
        raise NormalizationError("automatic policy is absent")
    return _decode_evidenced_map(
        policy.get("applied_fullwidth_ascii_map"),
        ASCII_FULLWIDTH_MAP,
        "applied fullwidth ASCII",
    )


def materialize_candidate(
    payloads: Mapping[str, bytes],
    documents: Mapping[str, TextDocument],
    metadata: Mapping[str, Any],
    *,
    reverse: bool = False,
) -> dict[str, bytes]:
    replacements = operations_by_resource(metadata, documents, reverse=reverse)
    output = dict(payloads)
    for resource, values in replacements.items():
        if not values:
            continue
        output[resource] = documents[resource].rebuild(values)
        reparsed = parse_document(resource, output[resource])
        original = cell_map(documents[resource])
        expected = dict(original)
        expected.update(values)
        if cell_map(reparsed) != expected:
            raise NormalizationError(f"{resource}: candidate parse/rebuild output differs")
    if tuple(output) != TARGETS:
        raise NormalizationError("candidate target vector differs")
    return output


def candidate_specs(payloads: Mapping[str, bytes]) -> dict[str, dict[str, Any]]:
    if tuple(payloads) != TARGETS:
        raise NormalizationError("candidate payload vector differs")
    return {resource: spec(payloads[resource]) for resource in TARGETS}


def _renderable_codepoints(text: str) -> set[int]:
    """Return text glyph demand without treating controls as glyphs."""

    return {
        ord(char)
        for char in text
        if unicodedata.category(char) not in {"Cc", "Cf", "Cs", "Mn", "Me", "Zl", "Zp", "Cn"}
    }


def korean_text_demand(
    documents: Mapping[str, TextDocument],
    replacements: Mapping[str, Mapping[tuple[int, ...], str]],
) -> set[int]:
    result: set[int] = set()
    for resource, document in documents.items():
        local = replacements.get(resource, {})
        for cell in document.cells:
            text = local.get(cell.coordinate, cell.text)
            if HANGUL_RE.search(text):
                result.update(_renderable_codepoints(text))
    return result


def _font_g1n_target_coverage(
    payload: bytes, outer_entries: Sequence[int], required: Sequence[int], resource: str
) -> list[dict[str, Any]]:
    """Prove every evidenced target glyph has a mapping in every live JP tier."""

    archive = parse_link(payload)
    reports: list[dict[str, Any]] = []
    for outer_entry in outer_entries:
        if outer_entry >= len(archive.entries):
            raise NormalizationError(f"{resource}: expected G1N outer entry is missing")
        _header, raw = decompress_wrapper(archive.entries[outer_entry].data)
        if len(raw) < 0x2C or raw[:8] != b"_N1G0000":
            raise NormalizationError(f"{resource}: expected outer G1N is invalid")
        table_count = struct.unpack_from("<I", raw, 0x1C)[0]
        if table_count != 3:
            raise NormalizationError(f"{resource}: G1N table hierarchy differs")
        table_offsets = [struct.unpack_from("<I", raw, 0x20 + 4 * table)[0] for table in range(table_count)]
        missing_by_table: dict[str, list[str]] = {}
        for table, offset in enumerate(table_offsets):
            if offset + 0x20000 > len(raw):
                raise NormalizationError(f"{resource}: G1N map is truncated")
            missing = [
                f"U+{codepoint:04X}"
                for codepoint in required
                if struct.unpack_from("<H", raw, offset + 2 * codepoint)[0] == 0
            ]
            missing_by_table[str(table)] = missing
        reports.append(
            {
                "outer_entry": outer_entry,
                "table_count": table_count,
                "missing_evidenced_target_codepoints_by_table": missing_by_table,
                "all_evidenced_target_codepoints_mapped": all(
                    not missing for missing in missing_by_table.values()
                ),
            }
        )
    return reports


def font_coverage(
    payloads: Mapping[str, bytes], required: Sequence[int]
) -> tuple[dict[str, list[dict[str, Any]]], bool]:
    """Return complete coverage reports for all seven live JP G1N outer entries."""

    reports = {
        resource: _font_g1n_target_coverage(
            payloads[resource], outer_entries, required, resource
        )
        for resource, outer_entries in FONT_G1N_ROUTES.items()
    }
    covered = all(
        report["all_evidenced_target_codepoints_mapped"]
        for route in reports.values()
        for report in route
    )
    return reports, covered


def font_demand_impact(
    payloads: Mapping[str, bytes],
    documents: Mapping[str, TextDocument],
    replacements: Mapping[str, Mapping[tuple[int, ...], str]],
    applied_fullwidth_map: Mapping[str, str],
    deferred_middle_dot_map: Mapping[str, str],
    deferred_middle_dot_scope: Mapping[str, Any],
) -> dict[str, Any]:
    """Prove ASCII targets are safe and record the deferred middle-dot blocker."""

    before = korean_text_demand(documents, {})
    after = korean_text_demand(documents, replacements)
    removed = sorted(before - after)
    added = sorted(after - before)
    ascii_targets = sorted({ord(value) for value in applied_fullwidth_map.values()})
    if tuple(ascii_targets) != FULLWIDTH_ASCII_TARGET_CODEPOINTS:
        raise NormalizationError("applied ASCII target vector differs from pinned font witness")
    # The v0.9 archive pin is enforced before this point.  Reusing its complete
    # source-free seven-G1N witness keeps public emission lightweight while
    # retaining the exact decode result in metadata.
    ascii_reports = PINNED_FULLWIDTH_ASCII_FONT_WITNESS["per_font_route"]
    ascii_covered = PINNED_FULLWIDTH_ASCII_FONT_WITNESS[
        "all_evidenced_targets_mapped_in_all_live_jp_g1ns"
    ]
    # The operation domain is text-only; no font resource has a replacement
    # map and this source-only workstream never serializes a font container.
    fonts_unchanged = all(not replacements.get(resource) for resource in FONT_G1N_ROUTES)
    if not ascii_covered:
        raise NormalizationError("an applied fullwidth-ASCII target lacks a live JP font glyph")
    if not fonts_unchanged:
        raise NormalizationError("punctuation-only candidate unexpectedly changed a font resource")

    # This single, reproducible base route observation is enough to block the
    # operation.  Do not mutate text to U+30FB until a separate font pass has
    # verified all seven live outer entries.
    if deferred_middle_dot_map != KOREAN_TO_JAPANESE_MIDDLE_DOT_MAP:
        raise NormalizationError("deferred middle-dot map differs from pinned font witness")
    middle_dot_probe = PINNED_BASE_MIDDLE_DOT_FONT_WITNESS
    return {
        "before_active_korean_codepoint_count": len(before),
        "after_active_korean_codepoint_count": len(after),
        "removed_codepoints": [f"U+{codepoint:04X}" for codepoint in removed],
        "added_codepoints": [f"U+{codepoint:04X}" for codepoint in added],
        "font_resources_unchanged_exact": fonts_unchanged,
        "applied_fullwidth_ascii": {
            "evidenced_target_codepoints": [f"U+{codepoint:04X}" for codepoint in ascii_targets],
            "live_g1n_outer_entry_count": PINNED_FULLWIDTH_ASCII_FONT_WITNESS[
                "live_g1n_outer_entry_count"
            ],
            "all_evidenced_targets_mapped_in_all_live_jp_g1ns": ascii_covered,
            "per_font_route": ascii_reports,
        },
        "deferred_korean_middle_dot": {
            "evidence_map": {
                f"U+{ord(left):04X}": f"U+{ord(right):04X}"
                for left, right in sorted(deferred_middle_dot_map.items())
            },
            "automatic_application": False,
            "reason": "font_dependency_blocked_target_unmapped_in_base_live_g1n_table",
            "v0_9_affected_coordinate_count": deferred_middle_dot_scope[
                "automatic_normalization_coordinate_count"
            ],
            "v0_9_affected_character_count": deferred_middle_dot_scope[
                "automatic_normalization_character_count"
            ],
            "base_live_coverage_probe": middle_dot_probe,
        },
        "overlay_only_font_decision": "fullwidth_ascii_eligible__middle_dot_deferred_no_font_payload_or_metric_change",
    }


def switch_archive_spec(path: Path, release: str) -> dict[str, Any]:
    expected = SWITCH_ZIP_PINS[release]
    if path.name != expected["name"] or not path.is_file():
        raise NormalizationError(f"Switch {release} path/name is invalid")
    current = file_spec(path)
    if current["size"] != expected["size"]:
        raise NormalizationError(f"Switch {release} size differs")
    if current["sha256"] != expected["sha256"]:
        raise NormalizationError(f"Switch {release} SHA-256 differs")
    return {"name": path.name, **current}


def make_metadata(v09_zip: Path, switch_v22: Path, switch_v23: Path) -> dict[str, Any]:
    payloads, documents = load_v09_documents(v09_zip)
    before_docs = load_switch_documents(switch_v22, "v2.2")
    after_docs = load_switch_documents(switch_v23, "v2.3")
    evidence = classify_switch_v23_changes(before_docs, after_docs)
    # Both evidence maps are decoded and preserved.  Only the fullwidth ASCII
    # subset is applied now: U+30FB is missing from a required base G1N table.
    # The exact middle-dot coordinate/hash operations remain public deferred
    # evidence for a future font-complete pass.
    mapping = map_from_evidence(evidence)
    fullwidth_mapping = _decode_evidenced_map(
        evidence["observed_fullwidth_map"], ASCII_FULLWIDTH_MAP, "fullwidth ASCII"
    )
    middle_dot_mapping = _decode_evidenced_map(
        evidence["observed_korean_middle_dot_map"],
        KOREAN_TO_JAPANESE_MIDDLE_DOT_MAP,
        "Korean middle dot",
    )
    if mapping != fullwidth_mapping | middle_dot_mapping:
        raise NormalizationError("combined evidence map differs from its components")
    operations, scope = scan_active_candidate(documents, fullwidth_mapping)
    deferred_middle_dot_operations, deferred_middle_dot_scope = scan_active_candidate(
        documents, middle_dot_mapping
    )
    operation_model = {
        "automatic_policy": {
            "applied_fullwidth_ascii_map": evidence["observed_fullwidth_map"],
        },
        "operations": operations,
    }
    replacements = operations_by_resource(operation_model, documents)
    demand_impact = font_demand_impact(
        payloads,
        documents,
        replacements,
        fullwidth_mapping,
        middle_dot_mapping,
        deferred_middle_dot_scope,
    )
    return {
        "schema": SCHEMA,
        "runtime": {
            "distribution": "Steam",
            "pk_version": "1.1.7",
            "steam_build_id": 18_823_764,
            "language_route": "JP",
        },
        "input": {
            "release": "v0.9.0",
            "zip": {"name": v09_zip.name, **file_spec(v09_zip)},
            "candidate_targets": list(TARGETS),
            "candidate_before": candidate_specs(payloads),
        },
        "switch_v23_evidence": {
            "v2.2_zip": switch_archive_spec(switch_v22, "v2.2"),
            "v2.3_zip": switch_archive_spec(switch_v23, "v2.3"),
            **evidence,
        },
        "automatic_policy": {
            "mode": "v2.2_to_v2.3_character_map_derived__v0.9_coordinate_preimage_hash_gated",
            "unicode_nfkc_used": False,
            "observed_fullwidth_map": evidence["observed_fullwidth_map"],
            "observed_korean_middle_dot_map": evidence[
                "observed_korean_middle_dot_map"
            ],
            "applied_fullwidth_ascii_map": evidence["observed_fullwidth_map"],
            "deferred_korean_middle_dot_map": evidence[
                "observed_korean_middle_dot_map"
            ],
            "character_map_evidence_scope": "pinned_switch_v2.2_to_v2.3_coordinate_aligned_delta",
            "candidate_application_scope": "all_active_v0.9_korean_cells_with_per_coordinate_preimage_hash_gate",
            "korean_middle_dot_direction": "U+00B7_to_U+30FB",
            "protected_tokens": [
                "ESC_C",
                "printf",
                "brace_placeholder",
                "angle_tag",
                "bracket_tag",
            ],
            "preserved_invariants": [
                "controls",
                "ESC_C",
                "printf",
                "brace_placeholders",
                "angle_tags",
                "bracket_tags",
                "line_breaks",
                "PUA",
                "leading_whitespace",
                "trailing_whitespace",
            ],
            "linebreak_removal_applied": False,
            "font_metric_change_applied": False,
        },
        "scope": scope,
        "operations": operations,
        "deferred_korean_middle_dot": {
            "mode": "font_dependency_blocked_not_applied",
            "operation_count": len(deferred_middle_dot_operations),
            "character_operation_count": sum(
                len(row["character_operations"])
                for row in deferred_middle_dot_operations
            ),
            "scope": deferred_middle_dot_scope,
            "operations": deferred_middle_dot_operations,
        },
        "font_demand_impact": demand_impact,
        "reversal": {
            "mode": "coordinate_hash_gated_character_operations",
            "per_coordinate_source_text_restored_exact": True,
            "operation_count": len(operations),
            "character_operation_count": sum(len(row["character_operations"]) for row in operations),
            "requires_after_utf16le_sha256_match": True,
        },
        "safety": {
            "source_text_free": True,
            "complete_game_resource_included": False,
            "installed_game_file_written": False,
            "executable_modified": False,
            "registry_modified": False,
            "memory_patch": False,
            "dll_injection": False,
            "hooking": False,
        },
    }


def source_free(value: Any) -> bool:
    """Metadata may contain Hangul and codepoint labels, never JP source text."""

    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return re.search(r"[\u3040-\u30FF\u31F0-\u31FF\u3400-\u9FFF\uF900-\uFAFF]", text) is None


def validate_metadata(metadata: Mapping[str, Any]) -> None:
    require(metadata.get("schema"), SCHEMA, "metadata schema")
    require_true(metadata.get("safety", {}).get("source_text_free"), "source_free flag")
    require_true(source_free(metadata), "source-free metadata scan")
    policy = metadata.get("automatic_policy")
    if not isinstance(policy, dict):
        raise NormalizationError("automatic policy is missing")
    require(policy.get("unicode_nfkc_used"), False, "unicode NFKC policy")
    require(policy.get("linebreak_removal_applied"), False, "linebreak policy")
    require(policy.get("font_metric_change_applied"), False, "font policy")
    require(
        policy.get("character_map_evidence_scope"),
        "pinned_switch_v2.2_to_v2.3_coordinate_aligned_delta",
        "character-map evidence scope",
    )
    require(
        policy.get("candidate_application_scope"),
        "all_active_v0.9_korean_cells_with_per_coordinate_preimage_hash_gate",
        "candidate application scope",
    )
    require(
        policy.get("korean_middle_dot_direction"),
        "U+00B7_to_U+30FB",
        "Korean middle-dot direction",
    )
    mapping = map_from_metadata(metadata)
    if not mapping:
        raise NormalizationError("automatic map is empty")
    scope = metadata.get("scope")
    if not isinstance(scope, dict):
        raise NormalizationError("scope is missing")
    raw_ops = metadata.get("operations")
    if not isinstance(raw_ops, list):
        raise NormalizationError("operations are missing")
    require(scope.get("automatic_normalization_coordinate_count"), len(raw_ops), "operation count")
    evidence = metadata.get("switch_v23_evidence")
    if not isinstance(evidence, dict):
        raise NormalizationError("Switch evidence is missing")
    require(
        evidence.get("observed_fullwidth_map"),
        policy.get("observed_fullwidth_map"),
        "fullwidth evidence map",
    )
    require(
        evidence.get("observed_korean_middle_dot_map"),
        policy.get("observed_korean_middle_dot_map"),
        "Korean middle-dot evidence map",
    )
    require(
        policy.get("observed_korean_middle_dot_map"),
        {"U+00B7": "U+30FB"},
        "Korean middle-dot map direction",
    )
    require(
        policy.get("applied_fullwidth_ascii_map"),
        policy.get("observed_fullwidth_map"),
        "applied fullwidth map",
    )
    require(
        policy.get("deferred_korean_middle_dot_map"),
        policy.get("observed_korean_middle_dot_map"),
        "deferred Korean middle-dot map",
    )
    deferred = metadata.get("deferred_korean_middle_dot")
    if not isinstance(deferred, dict):
        raise NormalizationError("deferred Korean middle-dot record is missing")
    require(
        deferred.get("mode"),
        "font_dependency_blocked_not_applied",
        "deferred Korean middle-dot mode",
    )
    if not isinstance(deferred.get("operations"), list):
        raise NormalizationError("deferred Korean middle-dot operations are missing")
    require(
        deferred.get("operation_count"),
        len(deferred["operations"]),
        "deferred Korean middle-dot operation count",
    )
    demand = metadata.get("font_demand_impact")
    if not isinstance(demand, dict):
        raise NormalizationError("font-demand impact is missing")
    require_true(
        demand.get("font_resources_unchanged_exact"),
        "font payload non-mutation",
    )
    applied_coverage = demand.get("applied_fullwidth_ascii")
    if not isinstance(applied_coverage, dict):
        raise NormalizationError("applied fullwidth font coverage is missing")
    require_true(
        applied_coverage.get("all_evidenced_targets_mapped_in_all_live_jp_g1ns"),
        "applied fullwidth font coverage",
    )
    require(
        applied_coverage.get("live_g1n_outer_entry_count"),
        7,
        "live JP G1N outer-entry count",
    )
    middle_dot_font = demand.get("deferred_korean_middle_dot")
    if not isinstance(middle_dot_font, dict):
        raise NormalizationError("deferred middle-dot font evidence is missing")
    require(middle_dot_font.get("automatic_application"), False, "deferred middle-dot application")
    if "U+30FB" not in middle_dot_font.get("base_live_coverage_probe", {}).get(
        "target_missing_codepoints", []
    ):
        raise NormalizationError("deferred middle-dot blocker is not evidenced")


def validation_projection(metadata: Mapping[str, Any]) -> dict[str, Any]:
    validate_metadata(metadata)
    return {
        "schema": VALIDATION_SCHEMA,
        "status": "PASS",
        "runtime": metadata["runtime"],
        "input": {
            "zip": metadata["input"]["zip"],
            "candidate_target_count": len(metadata["input"]["candidate_targets"]),
        },
        "switch_v23_evidence": {
            "v2.2_zip": metadata["switch_v23_evidence"]["v2.2_zip"],
            "v2.3_zip": metadata["switch_v23_evidence"]["v2.3_zip"],
            "v22_v23_changed_coordinate_count": metadata["switch_v23_evidence"]["v22_v23_changed_coordinate_count"],
            "punctuation_only_coordinate_count": metadata["switch_v23_evidence"]["punctuation_only_coordinate_count"],
            "fullwidth_ascii_coordinate_count": metadata["switch_v23_evidence"]["fullwidth_ascii_coordinate_count"],
            "korean_middle_dot_coordinate_count": metadata["switch_v23_evidence"]["korean_middle_dot_coordinate_count"],
            "non_punctuation_changed_coordinate_count": metadata["switch_v23_evidence"]["non_punctuation_changed_coordinate_count"],
            "linebreak_changes_not_classified_by_this_workstream": metadata["switch_v23_evidence"]["linebreak_changes_not_classified_by_this_workstream"],
            "observed_fullwidth_map": metadata["automatic_policy"]["observed_fullwidth_map"],
            "observed_korean_middle_dot_map": metadata["automatic_policy"]["observed_korean_middle_dot_map"],
        },
        "scope": metadata["scope"],
        "candidate_before": metadata["input"]["candidate_before"],
        "font_demand_impact": metadata["font_demand_impact"],
        "deferred_korean_middle_dot": {
            "mode": metadata["deferred_korean_middle_dot"]["mode"],
            "operation_count": metadata["deferred_korean_middle_dot"]["operation_count"],
            "character_operation_count": metadata["deferred_korean_middle_dot"]["character_operation_count"],
            "scope": metadata["deferred_korean_middle_dot"]["scope"],
        },
        "reversal": metadata["reversal"],
        "checks": {
            "active_jp_text_resources_scanned": True,
            "automatic_scope_uses_switch_v22_v23_map_plus_v0_9_hash_gates": True,
            "korean_middle_dot_direction_is_u00b7_to_u30fb": True,
            "korean_middle_dot_is_font_dependency_blocked_and_not_applied": True,
            "unicode_nfkc_not_used": True,
            "controls_placeholders_and_layout_preserved": True,
            "linebreak_removal_not_mixed_into_this_workstream": True,
            "font_metric_change_not_mixed_into_this_workstream": True,
            "font_coverage_all_applied_fullwidth_ascii_targets_proven": True,
            "reverse_restores_each_hash_gated_source_coordinate": True,
            "installed_game_file_written": False,
        },
    }


def _lexical_absolute(path: Path) -> Path:
    """Return an absolute path without resolving a possible reparse escape."""

    return Path(os.path.abspath(os.fspath(path)))


def _reparse_kind(path: Path) -> str | None:
    """Classify a symlink, junction, or other Windows reparse point safely."""

    try:
        if path.is_symlink():
            return "symlink"
        if path.is_junction():
            return "junction"
        info = path.lstat()
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise NormalizationError(f"cannot inspect output path component: {path}") from exc
    if stat.S_ISLNK(info.st_mode):
        return "symlink"
    reparse_attribute = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x0400)
    if getattr(info, "st_file_attributes", 0) & reparse_attribute:
        return "reparse point"
    return None


def _reject_reparse(path: Path, label: str) -> None:
    kind = _reparse_kind(path)
    if kind is not None:
        raise NormalizationError(f"{label} must not be a {kind}: {path}")


def _tmp_roots() -> tuple[Path, Path]:
    """Return checked lexical/resolved tmp roots without following a junction."""

    lexical = _lexical_absolute(TMP_ROOT)
    _reject_reparse(lexical, "repository tmp root")
    if not lexical.is_dir():
        raise NormalizationError(f"repository tmp root is not a directory: {lexical}")
    try:
        resolved = lexical.resolve(strict=True)
    except OSError as exc:
        raise NormalizationError(f"cannot resolve repository tmp root: {lexical}") from exc
    return lexical, resolved


def assert_safe_tmp_path(
    path: Path,
    label: str,
    *,
    require_exists: bool = False,
) -> Path:
    """Prove a path is lexically/resolved below a reparse-free ``tmp`` tree."""

    tmp_lexical, tmp_resolved = _tmp_roots()
    lexical = _lexical_absolute(path)
    try:
        relative = lexical.relative_to(tmp_lexical)
    except ValueError as exc:
        raise NormalizationError(f"{label} must be below KR_PATCH_WORK/tmp: {lexical}") from exc
    if not relative.parts:
        raise NormalizationError(f"{label} must not be the KR_PATCH_WORK/tmp root")
    current = tmp_lexical
    for component in relative.parts:
        current = current / component
        _reject_reparse(current, f"{label} path component")
    try:
        resolved = lexical.resolve(strict=require_exists)
    except FileNotFoundError as exc:
        raise NormalizationError(f"{label} is missing: {lexical}") from exc
    except OSError as exc:
        raise NormalizationError(f"cannot resolve {label}: {lexical}") from exc
    if resolved == tmp_resolved or tmp_resolved not in resolved.parents:
        raise NormalizationError(f"{label} escapes KR_PATCH_WORK/tmp after resolve: {resolved}")
    return resolved


def ensure_safe_tmp_directory(path: Path, label: str) -> Path:
    """Create only ordinary, checked directory components below ``tmp``."""

    lexical_target = _lexical_absolute(path)
    tmp_lexical, tmp_resolved = _tmp_roots()
    if lexical_target == tmp_lexical:
        return tmp_resolved
    assert_safe_tmp_path(lexical_target, label)
    relative = lexical_target.relative_to(tmp_lexical)
    current = tmp_lexical
    for component in relative.parts:
        current = current / component
        assert_safe_tmp_path(current, f"{label} directory")
        if not current.exists():
            try:
                current.mkdir()
            except FileExistsError:
                # A concurrent creator is admissible only if its post-check
                # still proves it is an ordinary tmp-contained directory.
                pass
        checked = assert_safe_tmp_path(current, f"{label} directory", require_exists=True)
        if not checked.is_dir():
            raise NormalizationError(f"{label} component is not a directory: {checked}")
    return assert_safe_tmp_path(lexical_target, label, require_exists=True)


def prepare_new_tmp_file(path: Path, label: str) -> Path:
    """Return a fresh, safe tmp file target without creating it yet."""

    lexical = _lexical_absolute(path)
    if lexical.name in {"", ".", ".."}:
        raise NormalizationError(f"{label} must name a file")
    assert_safe_tmp_path(lexical, label)
    parent = ensure_safe_tmp_directory(lexical.parent, f"{label} parent")
    destination = parent / lexical.name
    assert_safe_tmp_path(destination, label)
    if destination.exists() or _reparse_kind(destination) is not None:
        raise NormalizationError(f"{label} already exists or is a reparse point: {destination}")
    return destination


def atomic_write(path: Path, blob: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(blob)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def write_zip(payloads: Mapping[str, bytes], destination: Path) -> dict[str, Any]:
    destination = prepare_new_tmp_file(destination, "output ZIP")
    with zipfile.ZipFile(destination, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for relative in TARGETS:
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, payloads[relative])
    checked = assert_safe_tmp_path(destination, "output ZIP", require_exists=True)
    if not checked.is_file():
        raise NormalizationError(f"output ZIP is not a regular file: {checked}")
    with zipfile.ZipFile(checked, "r") as archive:
        require(archive.namelist(), list(TARGETS), "output ZIP member vector")
        for relative in TARGETS:
            require(archive.read(relative), payloads[relative], f"output ZIP payload {relative}")
    return {"name": checked.name, **file_spec(checked)}


def read_metadata(path: Path = METADATA_PATH) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise NormalizationError(f"cannot read metadata: {exc}") from exc
    if not isinstance(value, dict):
        raise NormalizationError("metadata root is not an object")
    validate_metadata(value)
    return value


def verify(v09_zip: Path, switch_v22: Path, switch_v23: Path) -> dict[str, Any]:
    expected = read_metadata()
    actual = make_metadata(v09_zip, switch_v22, switch_v23)
    require(actual, expected, "recomputed metadata")
    require(validation_projection(actual), json.loads(VALIDATION_PATH.read_text(encoding="utf-8")), "validation projection")
    return validation_projection(actual)


def command_emit_public(args: argparse.Namespace) -> int:
    metadata = make_metadata(args.v09_zip, args.switch_v22_zip, args.switch_v23_zip)
    validate_metadata(metadata)
    validation = validation_projection(metadata)
    atomic_write(METADATA_PATH, canonical_json(metadata))
    atomic_write(VALIDATION_PATH, canonical_json(validation))
    print("status=PASS")
    print(f"automatic_coordinates={metadata['scope']['automatic_normalization_coordinate_count']}")
    print(f"automatic_characters={metadata['scope']['automatic_normalization_character_count']}")
    print("steam_files_written=False")
    return 0


def command_verify(args: argparse.Namespace) -> int:
    validation = verify(args.v09_zip, args.switch_v22_zip, args.switch_v23_zip)
    print("status=PASS")
    print(f"automatic_coordinates={validation['scope']['automatic_normalization_coordinate_count']}")
    print(f"automatic_characters={validation['scope']['automatic_normalization_character_count']}")
    print("steam_files_written=False")
    return 0


def command_build(args: argparse.Namespace) -> int:
    metadata = read_metadata()
    payloads, documents = load_v09_documents(args.v09_zip)
    candidate = materialize_candidate(payloads, documents, metadata)
    zip_spec = write_zip(candidate, args.output_zip)
    print("status=PASS")
    print(f"zip_sha256={zip_spec['sha256']}")
    print("steam_files_written=False")
    return 0


def command_restore(args: argparse.Namespace) -> int:
    metadata = read_metadata()
    with zipfile.ZipFile(args.normalized_zip, "r") as archive:
        require(archive.namelist(), list(TARGETS), "normalized input member vector")
        payloads = {relative: archive.read(relative) for relative in TARGETS}
    documents = {resource: parse_document(resource, payloads[resource]) for resource in TEXT_KINDS}
    restored = materialize_candidate(payloads, documents, metadata, reverse=True)
    require(restored, dict(load_v09_documents(args.v09_zip)[0]), "restored v0.9 payload vector")
    zip_spec = write_zip(restored, args.output_zip)
    print("status=PASS")
    print(f"zip_sha256={zip_spec['sha256']}")
    print("steam_files_written=False")
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)

    def inputs(command: argparse.ArgumentParser, *, switch: bool) -> None:
        command.add_argument("--v09-zip", type=Path, default=V09_ZIP)
        if switch:
            command.add_argument("--switch-v22-zip", type=Path, default=SWITCH_V22_ZIP)
            command.add_argument("--switch-v23-zip", type=Path, default=SWITCH_V23_ZIP)

    emit = commands.add_parser("emit-public")
    inputs(emit, switch=True)
    verify_parser = commands.add_parser("verify")
    inputs(verify_parser, switch=True)
    build = commands.add_parser("build")
    inputs(build, switch=False)
    build.add_argument("--output-zip", type=Path, required=True)
    restore = commands.add_parser("restore")
    inputs(restore, switch=False)
    restore.add_argument("--normalized-zip", type=Path, required=True)
    restore.add_argument("--output-zip", type=Path, required=True)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "emit-public":
            return command_emit_public(args)
        if args.command == "verify":
            return command_verify(args)
        if args.command == "build":
            return command_build(args)
        return command_restore(args)
    except (NormalizationError, OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
