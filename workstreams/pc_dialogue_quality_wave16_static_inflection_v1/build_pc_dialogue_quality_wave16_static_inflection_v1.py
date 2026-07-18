#!/usr/bin/env python3
"""Build a private PC-only candidate for six static ``01 43`` repairs.

Wave 16 accepts only the Steam profile produced by Wave 14.  It completes
three paired Base/PK static dialogues, removes only their pinned Japanese
``01 43`` morphology commands, and retains the ``05 05 05`` terminator.

The builder can read Steam and the pinned PC-language references, but it has
no Steam writer, Git operation, release operation, network operation, or
Switch-Korean input path.  Its only write target is this workstream's private
``tmp`` directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
MSGGAME_TOOLS = REPO / "workstreams" / "msggame"
TOOLS = REPO / "tools"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")

for module_root in (TOOLS, MSGGAME_TOOLS):
    if str(module_root) not in sys.path:
        sys.path.insert(0, str(module_root))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from msggame_format import (  # noqa: E402
    LITERAL_END,
    LITERAL_START,
    MsgGameRecord,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_msggame,
    rebuild_raw_msggame,
)


SCHEMA = "nobu16.kr.pc-dialogue-quality-wave16-static-inflection.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave16-static-inflection-audit.v1"
RECORD_TERMINATOR = b"\x05\x05\x05"
MORPHOLOGY_PREFIX = b"\x01\x43"

PROFILE_PATHS = (
    "MSG/JP/ev_strdata.bin",
    "MSG/JP/msggame.bin",
    "MSG/JP/strdata.bin",
    "MSG_PK/JP/msgbre.bin",
    "MSG_PK/JP/msgdata.bin",
    "MSG_PK/JP/msgev.bin",
    "MSG_PK/JP/msggame.bin",
    "MSG_PK/JP/msgire.bin",
    "MSG_PK/JP/msgstf.bin",
    "MSG_PK/JP/msgstf_ce.bin",
    "MSG_PK/JP/msgui.bin",
)
BASE_MSGGAME = "MSG/JP/msggame.bin"
PK_MSGGAME = "MSG_PK/JP/msggame.bin"
CHANGED_PATHS = (BASE_MSGGAME, PK_MSGGAME)

# Wave 14's applied Steam profile is the only permitted Wave 16 preimage.
INPUT_SHA256 = {
    "MSG/JP/ev_strdata.bin": "BF224468BFBCF3CC71DFF4609142A60D75091813281EE6F2333645413AD81B80",
    BASE_MSGGAME: "4D147A4AD73466E882043D8A5E47F0D4DAF37473702A8CEABAEFFBF4E76F2EB8",
    "MSG/JP/strdata.bin": "5F308F416378976C1AB0B50D4A91C9DA38C637A0A842BAB04FB48256B2103E28",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    "MSG_PK/JP/msgdata.bin": "69090EC9EEE1DF9EAFB64BB35CEFD285A5089FDE78E9A4A855EAA0AE5991C168",
    "MSG_PK/JP/msgev.bin": "3E2323DDFAD70DAA15713DD1C4D622508BD2E610C65683C0A06D3D1FAC9827A5",
    PK_MSGGAME: "BD789D1C5230159433BDB9F2FCBE4B0ABABF9D84FAD2FE1C16EED45B071CE860",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}

TARGET_SHA256 = {
    **INPUT_SHA256,
    BASE_MSGGAME: "EEA622999F38C72F2088467E04D4A885B684D3FD3CF99FB72879A72079CF9351",
    PK_MSGGAME: "9EB0FD80E7A6D50BC2A6073FDBF213E7BDB685D81DFCD9191C9C86E415D7EFCC",
}
INPUT_PACKED_SIZES = {
    BASE_MSGGAME: 1_504_639,
    PK_MSGGAME: 1_806_743,
}
TARGET_PACKED_SIZES = {
    BASE_MSGGAME: 1_504_655,
    PK_MSGGAME: 1_806_759,
}

# These are pristine Steam PC Japanese resources, not Switch resources.
PC_JP_SOURCES = {
    BASE_MSGGAME: (
        Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin"),
        "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
    ),
    PK_MSGGAME: (
        DEFAULT_STEAM_ROOT
        / "KR_PATCH_BACKUP/file_only_transaction/steam-jp-1.1.7-v0.6.0/originals/MSG_PK/JP/msggame.bin",
        "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    ),
}

# Base has no installed EN msggame.  Every Base target is paired with the
# identical PK JP dialogue below, so the PK EN/SC/TC records are the pinned
# cross-language anchors for both members of each pair.
PK_CONTEXTS = {
    "EN": (
        "MSG_PK/EN/msggame.bin",
        "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    ),
    "SC": (
        "MSG_PK/SC/msggame.bin",
        "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    ),
    "TC": (
        "MSG_PK/TC/msggame.bin",
        "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
    ),
}


@dataclass(frozen=True)
class Family:
    """A Base/PK dialogue pair and its pinned PC-language evidence."""

    name: str
    base_coordinate: tuple[int, int]
    pk_coordinate: tuple[int, int]
    jp_literals: tuple[str, ...]
    pk_context_literals: Mapping[str, tuple[str, ...]]
    pk_context_commands: Mapping[str, tuple[str, ...]]


@dataclass(frozen=True)
class Change:
    family: str
    resource: str
    coordinate: tuple[int, int]
    current_literals: tuple[str, ...]
    target_literals: tuple[str, ...]
    input_record_sha256: str
    input_record_size: int
    removed_commands_hex: tuple[str, ...]
    input_opaque_spans_hex: tuple[str, ...]
    target_record_sha256: str
    target_record_size: int

    @property
    def coordinate_text(self) -> str:
        return f"{self.coordinate[0]}:{self.coordinate[1]}"


FAMILIES = (
    Family(
        "successor_handover",
        (8, 398),
        (8, 410),
        ("かしこま", "\n後任に引き継"),
        {
            "EN": ("Acknowledged. I shall impart everything to my successor.",),
            "SC": ("遵旨，\n继承后任。",),
            "TC": ("遵命！\n臣謹奉大人之命，成為後任。",),
        },
        {"EN": (), "SC": (), "TC": ()},
    ),
    Family(
        "personal_intervention",
        (8, 969),
        (8, 981),
        ("自ら介入し\nこの調略を阻んで参",),
        {
            "EN": ("I shall step in myself to ensure that these schemes are put to an end.",),
            "SC": ("亲自出马，\n前来阻止此策略。",),
            "TC": ("將前往制止此計謀。",),
        },
        {
            "EN": (),
            "SC": ("014301000000",),
            "TC": ("014301000000",),
        },
    ),
    Family(
        "march_preparations",
        (15, 2261),
        (15, 2292),
        ("かしこま", "\n出陣の手配に移"),
        {
            "EN": ("Understood. We will begin preparations to march.",),
            "SC": ("明白。\n这就准备出阵。",),
            "TC": ("遵命！\n立刻準備出陣！",),
        },
        {"EN": (), "SC": (), "TC": ()},
    ),
)
FAMILY_BY_NAME = {family.name: family for family in FAMILIES}
if len(FAMILY_BY_NAME) != len(FAMILIES):
    raise RuntimeError("duplicate Wave 16 family")


CHANGES = (
    Change(
        "successor_handover", BASE_MSGGAME, (8, 398),
        ("알겠", "\n후임에게 인계하"),
        ("알겠습니다.", "\n후임에게 모든 것을 인계하겠습니다."),
        "C36B9A7DED9639D4E1BA57A9C50D0312C037AC835EFE312D36EDBD0A5E88DA76", 49,
        ("014368020000", "014372010000"),
        ("", "014368020000", "014372010000050505"),
        "B860F16F2C7941AD0F198A28563EF12619BD8DB89032957E8CE953BEA1E1E351", 67,
    ),
    Change(
        "personal_intervention", BASE_MSGGAME, (8, 969),
        ("몸소 개입하여\n이 조략을 막아 내겠",),
        ("몸소 개입하여\n이 조략을 막아 내겠습니다.",),
        "1BD3B6C33F8449C717EC7C67573AF80296DCEBCE2AEAD8497DE617A549351367", 59,
        ("014301000000", "01433C040000"),
        ("014301000000", "01433C040000050505"),
        "EE9B0A561E2D6736454491DFB30F8F87A2B82C194C39F44CC3E12C6375F403BC", 55,
    ),
    Change(
        "march_preparations", BASE_MSGGAME, (15, 2261),
        ("알겠", "\n출진 채비에 들어가"),
        ("알겠습니다.", "\n출진 채비에 들어가겠습니다."),
        "A6C6E8D2571D9CF8034057BBD726164DCFAC9F2096831F2133BC8824C9207C1C", 53,
        ("014368020000", "01435A040000"),
        ("", "014368020000", "01435A040000050505"),
        "A727063BF7A2A563BAAB20F7F472F5F5E96105C9C1FB38376F0D6525F79876C4", 59,
    ),
    Change(
        "successor_handover", PK_MSGGAME, (8, 410),
        ("알겠", "\n후임에게 인계하"),
        ("알겠습니다.", "\n후임에게 모든 것을 인계하겠습니다."),
        "3BE9F0047105BC04DC878474476141A73741CFC9A0C739965F77F76E501DC20B", 49,
        ("014374020000", "014372010000"),
        ("", "014374020000", "014372010000050505"),
        "B860F16F2C7941AD0F198A28563EF12619BD8DB89032957E8CE953BEA1E1E351", 67,
    ),
    Change(
        "personal_intervention", PK_MSGGAME, (8, 981),
        ("몸소 개입하여\n이 조략을 막아 내겠",),
        ("몸소 개입하여\n이 조략을 막아 내겠습니다.",),
        "1402F1DB7FF2BA401E8E9258F6CA461141F8561B32639C7A1C4D14D42A1236DC", 59,
        ("014301000000", "014348040000"),
        ("014301000000", "014348040000050505"),
        "EE9B0A561E2D6736454491DFB30F8F87A2B82C194C39F44CC3E12C6375F403BC", 55,
    ),
    Change(
        "march_preparations", PK_MSGGAME, (15, 2292),
        ("알겠", "\n출진 채비에 들어가"),
        ("알겠습니다.", "\n출진 채비에 들어가겠습니다."),
        "FA3E836B40C079D58383854ED1D720F32F18D4B7AE39B27A02C7ADD7990E1735", 53,
        ("014374020000", "014366040000"),
        ("", "014374020000", "014366040000050505"),
        "A727063BF7A2A563BAAB20F7F472F5F5E96105C9C1FB38376F0D6525F79876C4", 59,
    ),
)
CHANGE_BY_KEY = {(change.resource, change.coordinate): change for change in CHANGES}
if len(CHANGE_BY_KEY) != len(CHANGES):
    raise RuntimeError("duplicate Wave 16 target coordinate")


class Wave16Error(ValueError):
    """A profile, reference, byte-preservation, or private-output contract failed."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


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


def morphology_commands(record: MsgGameRecord) -> tuple[str, ...]:
    commands: list[str] = []
    for span in opaque_spans(record):
        offset = 0
        while offset < len(span):
            if span[offset : offset + 2] == MORPHOLOGY_PREFIX:
                if offset + 6 > len(span):
                    raise Wave16Error("truncated 01 43 command")
                commands.append(span[offset : offset + 6].hex().upper())
                offset += 6
            else:
                offset += 1
    return tuple(commands)


def stripped_opaque_spans(record: MsgGameRecord) -> tuple[bytes, ...]:
    """Remove only complete ``01 43 <u32>`` commands from opaque spans."""
    output_spans: list[bytes] = []
    for span in opaque_spans(record):
        output = bytearray()
        offset = 0
        while offset < len(span):
            if span[offset : offset + 2] == MORPHOLOGY_PREFIX:
                if offset + 6 > len(span):
                    raise Wave16Error("truncated 01 43 command")
                offset += 6
            else:
                output.append(span[offset])
                offset += 1
        output_spans.append(bytes(output))
    return tuple(output_spans)


def output_opaque_spans(change: Change) -> tuple[bytes, ...]:
    return tuple(b"" for _ in change.target_literals) + (RECORD_TERMINATOR,)


def profile_hashes(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for relative in PROFILE_PATHS:
        path = root / relative
        if not path.is_file():
            raise Wave16Error(f"profile resource is absent: {relative}")
        result[relative] = sha256_path(path)
    return result


def assert_profile(root: Path, expected: Mapping[str, str], label: str) -> None:
    actual = profile_hashes(root)
    if actual != dict(expected):
        mismatch = {
            path: {"expected": expected.get(path), "actual": actual.get(path)}
            for path in PROFILE_PATHS
            if actual.get(path) != expected.get(path)
        }
        raise Wave16Error(f"{label} profile mismatch: {json.dumps(mismatch, sort_keys=True)}")


def validate_raw_roundtrip(packed: bytes, label: str) -> None:
    """Require byte-exact raw rebuilding and semantic LZ4 rewrapping."""
    _header, raw = decompress_wrapper(packed)
    archive = parse_packed_msggame(packed).archive
    rebuilt_raw = rebuild_raw_msggame(archive)
    if rebuilt_raw != raw:
        raise Wave16Error(f"{label} raw parse/rebuild differs")
    repacked = recompress_wrapper(rebuilt_raw, parse_packed_msggame(packed).header)
    _repacked_header, roundtrip_raw = decompress_wrapper(repacked)
    if roundtrip_raw != raw:
        raise Wave16Error(f"{label} LZ4 round-trip differs")


def validate_text(value: str, coordinate: str, label: str) -> None:
    if not value or "\x1b" in value or "%" in value:
        raise Wave16Error(f"{coordinate} {label} contains a runtime marker or is empty")
    encoded = value.encode("utf-16-le")
    if LITERAL_START in encoded or LITERAL_END in encoded:
        raise Wave16Error(f"{coordinate} {label} encodes a reserved marker")
    for character in value:
        if character != "\n" and unicodedata.category(character) == "Cc":
            raise Wave16Error(f"{coordinate} {label} contains control U+{ord(character):04X}")


def line_upper_bound_px(value: str) -> list[int]:
    """Conservative diagnostic using 48px glyph and 24px-space widths."""
    return [sum(24 if character == " " else 48 for character in line) for line in value.split("\n")]


def rebuild_static_record(change: Change) -> bytes:
    payload = bytearray()
    for text in change.target_literals:
        payload.extend(LITERAL_START)
        payload.extend(text.encode("utf-16-le"))
        payload.extend(LITERAL_END)
    payload.extend(RECORD_TERMINATOR)
    return bytes(payload)


def load_references(
    steam_root: Path,
) -> tuple[
    dict[str, dict[tuple[int, int], MsgGameRecord]],
    dict[str, dict[tuple[int, int], MsgGameRecord]],
]:
    jp: dict[str, dict[tuple[int, int], MsgGameRecord]] = {}
    for resource, (path, expected_hash) in PC_JP_SOURCES.items():
        if not path.is_file() or sha256_path(path) != expected_hash:
            raise Wave16Error(f"pristine PC JP source hash differs: {resource}")
        jp[resource] = records_by_coordinate(path.read_bytes())

    contexts: dict[str, dict[tuple[int, int], MsgGameRecord]] = {}
    for language, (relative, expected_hash) in PK_CONTEXTS.items():
        path = steam_root / relative
        if not path.is_file() or sha256_path(path) != expected_hash:
            raise Wave16Error(f"PC PK {language} context hash differs")
        contexts[language] = records_by_coordinate(path.read_bytes())
    return jp, contexts


def validate_family_anchors(
    jp: Mapping[str, Mapping[tuple[int, int], MsgGameRecord]],
    contexts: Mapping[str, Mapping[tuple[int, int], MsgGameRecord]],
) -> None:
    """Pin PC JP and PK EN/SC/TC meaning anchors before text is rebuilt."""
    for family in FAMILIES:
        for resource, coordinate in (
            (BASE_MSGGAME, family.base_coordinate),
            (PK_MSGGAME, family.pk_coordinate),
        ):
            record = jp[resource].get(coordinate)
            if record is None or literal_texts(record) != family.jp_literals:
                raise Wave16Error(f"PC JP anchor differs: {family.name} {resource} {coordinate}")
        for language in PK_CONTEXTS:
            record = contexts[language].get(family.pk_coordinate)
            if record is None:
                raise Wave16Error(f"PC PK {language} anchor is absent: {family.name}")
            if literal_texts(record) != family.pk_context_literals[language]:
                raise Wave16Error(f"PC PK {language} anchor text differs: {family.name}")
            if morphology_commands(record) != family.pk_context_commands[language]:
                raise Wave16Error(f"PC PK {language} anchor bytecode differs: {family.name}")


def validate_change(
    change: Change,
    current: Mapping[tuple[int, int], MsgGameRecord],
    jp: Mapping[tuple[int, int], MsgGameRecord],
) -> tuple[bytes, dict[str, Any]]:
    family = FAMILY_BY_NAME.get(change.family)
    if family is None:
        raise Wave16Error(f"unknown family: {change.family}")
    expected_coordinate = family.base_coordinate if change.resource == BASE_MSGGAME else family.pk_coordinate
    if change.coordinate != expected_coordinate:
        raise Wave16Error(f"family coordinate mismatch: {change.resource} {change.coordinate_text}")

    record = current.get(change.coordinate)
    source = jp.get(change.coordinate)
    if record is None or source is None:
        raise Wave16Error(f"missing current or PC JP source record: {change.resource} {change.coordinate_text}")
    if len(record.data) != change.input_record_size:
        raise Wave16Error(f"input record size differs: {change.resource} {change.coordinate_text}")
    if sha256_bytes(record.data) != change.input_record_sha256:
        raise Wave16Error(f"input record SHA-256 differs: {change.resource} {change.coordinate_text}")
    if literal_texts(record) != change.current_literals:
        raise Wave16Error(f"current literals differ: {change.resource} {change.coordinate_text}")
    if literal_texts(source) != family.jp_literals:
        raise Wave16Error(f"PC JP literals differ: {change.resource} {change.coordinate_text}")
    if morphology_commands(record) != change.removed_commands_hex:
        raise Wave16Error(f"current morphology commands differ: {change.resource} {change.coordinate_text}")
    if morphology_commands(source) != change.removed_commands_hex:
        raise Wave16Error(f"PC JP morphology commands differ: {change.resource} {change.coordinate_text}")
    input_spans = tuple(value.hex().upper() for value in opaque_spans(record))
    if input_spans != change.input_opaque_spans_hex:
        raise Wave16Error(f"input opaque layout differs: {change.resource} {change.coordinate_text}")
    if stripped_opaque_spans(record) != output_opaque_spans(change):
        raise Wave16Error(f"non-morphology opaque bytes found: {change.resource} {change.coordinate_text}")
    if not all(command.startswith("0143") and len(command) == 12 for command in change.removed_commands_hex):
        raise Wave16Error(f"removal is not restricted to full 01 43 commands: {change.coordinate_text}")

    current_text = "".join(change.current_literals)
    target_text = "".join(change.target_literals)
    validate_text(current_text, change.coordinate_text, "current text")
    validate_text(target_text, change.coordinate_text, "target text")
    if current_text.count("\n") != target_text.count("\n"):
        raise Wave16Error(f"manual line count changed: {change.resource} {change.coordinate_text}")
    if target_text.count("\n") + 1 > 3:
        raise Wave16Error(f"target exceeds three explicit lines: {change.resource} {change.coordinate_text}")

    target = rebuild_static_record(change)
    if len(target) != change.target_record_size:
        raise Wave16Error(f"target record size differs: {change.resource} {change.coordinate_text}")
    if sha256_bytes(target) != change.target_record_sha256:
        raise Wave16Error(f"target record SHA-256 differs: {change.resource} {change.coordinate_text}")

    target_record = MsgGameRecord(
        block_id=record.block_id,
        record_id=record.record_id,
        relative_offset=record.relative_offset,
        data=target,
    )
    if literal_texts(target_record) != change.target_literals:
        raise Wave16Error(f"target literals differ: {change.resource} {change.coordinate_text}")
    if morphology_commands(target_record):
        raise Wave16Error(f"target retains 01 43: {change.resource} {change.coordinate_text}")
    if opaque_spans(target_record) != output_opaque_spans(change):
        raise Wave16Error(f"target opaque layout differs: {change.resource} {change.coordinate_text}")
    if marker_topology(target_record) != marker_topology(record):
        raise Wave16Error(f"literal marker topology changed: {change.resource} {change.coordinate_text}")

    return target, {
        "family": change.family,
        "resource": change.resource,
        "coordinate": change.coordinate_text,
        "input_record_sha256": change.input_record_sha256,
        "target_record_sha256": change.target_record_sha256,
        "input_record_size": change.input_record_size,
        "target_record_size": change.target_record_size,
        "current_literals": list(change.current_literals),
        "target_literals": list(change.target_literals),
        "literal_marker_count": len(change.current_literals),
        "input_opaque_spans_hex": list(change.input_opaque_spans_hex),
        "removed_opaque_commands_hex": list(change.removed_commands_hex),
        "target_opaque_spans_hex": [value.hex().upper() for value in output_opaque_spans(change)],
        "terminator_hex": RECORD_TERMINATOR.hex().upper(),
        "manual_line_count": {
            "current": current_text.count("\n") + 1,
            "target": target_text.count("\n") + 1,
        },
        "line_upper_bound_px": line_upper_bound_px(target_text),
    }


def validate_output_records(output: Mapping[str, bytes]) -> None:
    for change in CHANGES:
        record = records_by_coordinate(output[change.resource]).get(change.coordinate)
        if record is None:
            raise Wave16Error(f"candidate lacks target record: {change.resource} {change.coordinate_text}")
        if sha256_bytes(record.data) != change.target_record_sha256:
            raise Wave16Error(f"candidate target hash differs: {change.resource} {change.coordinate_text}")
        if literal_texts(record) != change.target_literals or morphology_commands(record):
            raise Wave16Error(f"candidate target literals/commands differ: {change.resource} {change.coordinate_text}")
        if opaque_spans(record) != output_opaque_spans(change):
            raise Wave16Error(f"candidate target opaque layout differs: {change.resource} {change.coordinate_text}")


def prepare_candidate(steam_root: Path) -> tuple[dict[str, bytes], dict[str, Any]]:
    """Build the six-record overlay in memory after all source guards pass."""
    steam_root = steam_root.resolve(strict=True)
    assert_profile(steam_root, INPUT_SHA256, "current Steam")
    for resource in CHANGED_PATHS:
        packed = (steam_root / resource).read_bytes()
        if len(packed) != INPUT_PACKED_SIZES[resource]:
            raise Wave16Error(f"current Steam packed size differs: {resource}")
        validate_raw_roundtrip(packed, f"current Steam {resource}")

    jp, contexts = load_references(steam_root)
    validate_family_anchors(jp, contexts)
    current = {
        resource: records_by_coordinate((steam_root / resource).read_bytes())
        for resource in CHANGED_PATHS
    }
    replacements: dict[str, dict[tuple[int, int], bytes]] = {resource: {} for resource in CHANGED_PATHS}
    audit_rows: list[dict[str, Any]] = []
    for change in CHANGES:
        if change.coordinate in replacements[change.resource]:
            raise Wave16Error(f"duplicate change: {change.resource} {change.coordinate_text}")
        target, row = validate_change(change, current[change.resource], jp[change.resource])
        replacements[change.resource][change.coordinate] = target
        audit_rows.append(row)

    output: dict[str, bytes] = {}
    for resource in CHANGED_PATHS:
        before = (steam_root / resource).read_bytes()
        after = rebuild_packed_msggame(before, replacements[resource])
        if len(after) != TARGET_PACKED_SIZES[resource]:
            raise Wave16Error(f"candidate packed size differs: {resource}")
        if sha256_bytes(after) != TARGET_SHA256[resource]:
            raise Wave16Error(f"candidate packed SHA-256 differs: {resource}")
        old_records = records_by_coordinate(before)
        new_records = records_by_coordinate(after)
        if old_records.keys() != new_records.keys():
            raise Wave16Error(f"record topology changed: {resource}")
        changed = {coordinate for coordinate in old_records if old_records[coordinate].data != new_records[coordinate].data}
        if changed != set(replacements[resource]):
            raise Wave16Error(f"unexpected changed record set: {resource} {sorted(changed)}")
        validate_raw_roundtrip(after, f"candidate {resource}")
        output[resource] = after
    validate_output_records(output)

    target_hashes = {**INPUT_SHA256, **{resource: sha256_bytes(data) for resource, data in output.items()}}
    if target_hashes != TARGET_SHA256:
        raise Wave16Error("candidate output profile is not pinned")
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "platform": "Steam PC",
            "wave14_profile_required": True,
            "pristine_pc_japanese_read": True,
            "pc_pk_en_sc_tc_context_read": True,
            "switch_korean_read": False,
            "steam_game_resource_written": False,
            "git_operation": "absent",
            "release_operation": "absent",
        },
        "input_sha256": INPUT_SHA256,
        "target_sha256": target_hashes,
        "pc_jp_sha256": {resource: expected for resource, (_path, expected) in PC_JP_SOURCES.items()},
        "pc_pk_context_sha256": {language: expected for language, (_path, expected) in PK_CONTEXTS.items()},
        "families": [
            {
                "name": family.name,
                "base_coordinate": f"{family.base_coordinate[0]}:{family.base_coordinate[1]}",
                "pk_coordinate": f"{family.pk_coordinate[0]}:{family.pk_coordinate[1]}",
                "pc_jp_literals": list(family.jp_literals),
                "pc_pk_context_literals": {
                    language: list(family.pk_context_literals[language]) for language in PK_CONTEXTS
                },
                "pc_pk_context_commands": {
                    language: list(family.pk_context_commands[language]) for language in PK_CONTEXTS
                },
            }
            for family in FAMILIES
        ],
        "records": audit_rows,
    }
    return output, audit


def require_tmp(path: Path, label: str) -> Path:
    root = TMP_ROOT.resolve(strict=False)
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave16Error(f"{label} must stay below {root}") from exc
    return resolved


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def verify_private_candidate(candidate_root: Path) -> None:
    candidate_root = require_tmp(candidate_root, "candidate root")
    assert_profile(candidate_root, TARGET_SHA256, "private candidate")
    output = {resource: (candidate_root / resource).read_bytes() for resource in CHANGED_PATHS}
    for resource, packed in output.items():
        if len(packed) != TARGET_PACKED_SIZES[resource]:
            raise Wave16Error(f"private candidate packed size differs: {resource}")
    validate_output_records(output)


def build_candidate(steam_root: Path, output_root: Path, audit_path: Path, manifest_path: Path) -> dict[str, Any]:
    output_root = require_tmp(output_root, "candidate output")
    audit_path = require_tmp(audit_path, "audit output")
    manifest_path = require_tmp(manifest_path, "manifest output")
    if output_root.exists() or audit_path.exists() or manifest_path.exists():
        raise Wave16Error("candidate output, audit, or manifest already exists")

    output, audit = prepare_candidate(steam_root)
    output_root.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.", dir=output_root.parent))
    try:
        for relative in PROFILE_PATHS:
            destination = stage / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if relative in output:
                destination.write_bytes(output[relative])
            else:
                shutil.copy2(steam_root / relative, destination)
        assert_profile(stage, TARGET_SHA256, "private candidate staging")
        os.replace(stage, output_root)
        verify_private_candidate(output_root)
        audit_bytes = (json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
        atomic_write(audit_path, audit_bytes)
        manifest = {
            "schema": SCHEMA,
            "transaction_id": "pc-dialogue-quality-wave16-static-inflection-v1",
            "profile_paths": list(PROFILE_PATHS),
            "changed_paths": list(CHANGED_PATHS),
            "coordinates": [f"{change.resource}:{change.coordinate_text}" for change in CHANGES],
            "input_sha256": INPUT_SHA256,
            "output_sha256": TARGET_SHA256,
            "pinned_output_sha256": TARGET_SHA256,
            "audit_sha256": sha256_bytes(audit_bytes),
            "record_count": len(CHANGES),
            "steam_write_capability": "absent",
            "git_operation": "absent",
            "release_operation": "absent",
            "real_game_qa_required_before_release": True,
        }
        atomic_write(
            manifest_path,
            (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        )
        return manifest
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    hash_parser = sub.add_parser("hash", help="calculate and verify the deterministic private candidate")
    hash_parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    verify_parser = sub.add_parser("verify-private", help="verify a candidate already under this workstream's tmp root")
    verify_parser.add_argument("--candidate-root", type=Path, required=True)
    build_parser = sub.add_parser("build", help="write a candidate only below this workstream's tmp root")
    build_parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    build_parser.add_argument("--output-root", type=Path, default=TMP_ROOT / "candidate")
    build_parser.add_argument("--audit-path", type=Path, default=TMP_ROOT / "audit.v1.json")
    build_parser.add_argument("--manifest-path", type=Path, default=TMP_ROOT / "build_manifest.v1.json")
    args = parser.parse_args(argv)
    try:
        if args.command == "hash":
            _output, audit = prepare_candidate(args.steam_root)
            print(json.dumps({"status": "ok", "target_sha256": audit["target_sha256"], "steam_write_capability": "absent"}, ensure_ascii=False, indent=2, sort_keys=True))
            return 0
        if args.command == "verify-private":
            verify_private_candidate(args.candidate_root)
            print(json.dumps({"status": "ok", "candidate_root": str(args.candidate_root), "steam_write_capability": "absent"}, ensure_ascii=False, sort_keys=True))
            return 0
        manifest = build_candidate(args.steam_root, args.output_root, args.audit_path, args.manifest_path)
        print(json.dumps({"status": "ok", "manifest": manifest, "steam_write_capability": "absent"}, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, Wave16Error) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
