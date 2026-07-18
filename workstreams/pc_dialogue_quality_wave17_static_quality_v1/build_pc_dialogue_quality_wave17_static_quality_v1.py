#!/usr/bin/env python3
"""Build the private, PC-only Wave 17 static dialogue-quality candidate.

The sole accepted input is the current eleven-file Steam PC profile containing
the Wave 15 event-name change, Wave 16 dialogue change, and the already-applied
Issue 61 fullwidth-percent repair.  The builder makes exactly three Base
msggame literal edits, writes only a private candidate below tmp, and has no
Steam, Git, release, network, or Switch-Korean capability.
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
    rebuild_record_literals,
    rebuild_packed_with_literals,
    rebuild_raw_msggame,
)


SCHEMA = "nobu16.kr.pc-dialogue-quality-wave17-static-quality.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave17-static-quality-audit.v1"
BASE_MSGGAME = "MSG/JP/msggame.bin"
PK_MSGGAME = "MSG_PK/JP/msggame.bin"
PK_MSGEV = "MSG_PK/JP/msgev.bin"
PROFILE_PATHS = (
    "MSG/JP/ev_strdata.bin",
    BASE_MSGGAME,
    "MSG/JP/strdata.bin",
    "MSG_PK/JP/msgbre.bin",
    "MSG_PK/JP/msgdata.bin",
    PK_MSGEV,
    PK_MSGGAME,
    "MSG_PK/JP/msgire.bin",
    "MSG_PK/JP/msgstf.bin",
    "MSG_PK/JP/msgstf_ce.bin",
    "MSG_PK/JP/msgui.bin",
)
CHANGED_PATHS = (BASE_MSGGAME,)
RECORD_TERMINATOR = b"\x05\x05\x05"
FONT_PATH = "RES_JP/res_lang.bin"
FONT_SHA256 = "3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7"
DIALOGUE_MAX_LINE_PX = 912
WIDE_SCRIPT_RE = re.compile(
    r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u9fff\uac00-\ud7a3\uf900-\ufaff]"
)

# This is the unique current Steam PC successor of Wave 15+16 after the
# already-applied Issue 61 repair.  The three dialogue anchors remain EEA
# (Base msggame), CE1A (PK msgev), and 9EB (PK msggame); Issue 61 additionally
# changes only the two listed non-dialogue resources.
INPUT_SHA256 = {
    "MSG/JP/ev_strdata.bin": "BF224468BFBCF3CC71DFF4609142A60D75091813281EE6F2333645413AD81B80",
    BASE_MSGGAME: "EEA622999F38C72F2088467E04D4A885B684D3FD3CF99FB72879A72079CF9351",
    "MSG/JP/strdata.bin": "6E7DD096A999299C43A9A23D9E99F75C81D6A9C8116488EC541A43423871B933",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    "MSG_PK/JP/msgdata.bin": "73CF194E4EF81C20692A245DAC75C3B2A9FCF1A997B7F6755D89DBB59149F2ED",
    PK_MSGEV: "CE1A61E6C0F85A3E7F0FD4C1DD1BF0349A99CC134A9D73B7DE1917DB6646A0C3",
    PK_MSGGAME: "9EB0FD80E7A6D50BC2A6073FDBF213E7BDB685D81DFCD9191C9C86E415D7EFCC",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}
TARGET_SHA256 = {
    **INPUT_SHA256,
    BASE_MSGGAME: "C1B39C7344F8A095E179942A26FB4EBDECEAABC2D6A8966A0DB134B7EBE600AC",
}
INPUT_BASE_PACKED_SIZE = 1_504_655
TARGET_BASE_PACKED_SIZE = 1_504_659

# PC-only semantic references.  Base has no EN msggame, so the target audit
# deliberately uses its pristine JP plus current PC SC and TC contexts.
PC_REFERENCE_PATHS = {
    "JP": (
        Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin"),
        "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
    ),
    "SC": (
        DEFAULT_STEAM_ROOT / "MSG/SC/msggame.bin",
        "B2FC3C18DA0F03ACFA93B1EAB0D09FBFCF7CD5076E667602D1AF212953A09BF7",
    ),
    "TC": (
        DEFAULT_STEAM_ROOT / "MSG/TC/msggame.bin",
        "20E710A11CDADFAF514EBC3B9C664E9C57B1A737138F29BF38CFB6527C0A5E95",
    ),
}


@dataclass(frozen=True)
class AnchorSpec:
    """A source-free PC JP/SC/TC proof for one reviewed Base record."""

    record_sha256: str
    record_size: int
    literal_utf16le_sha256: tuple[str, ...]
    literal_chain_sha256: str
    context_utf16le_sha256: str
    opaque_spans_hex: tuple[str, ...]


@dataclass(frozen=True)
class LayoutSpec:
    current_widths_px: tuple[int, ...]
    target_widths_px: tuple[int, ...]
    dialogue_limit_px: int | None


@dataclass(frozen=True)
class Change:
    """One literal-only Wave 17 correction."""

    coordinate: tuple[int, int]
    literal_id: int
    edit_kind: str
    target_literal: str | None
    term_from: str | None
    term_to: str | None
    input_record_sha256: str
    input_record_size: int
    input_literal_utf16le_sha256: tuple[str, ...]
    target_record_sha256: str
    target_record_size: int
    target_literal_utf16le_sha256: tuple[str, ...]
    opaque_spans_hex: tuple[str, ...]
    layout: LayoutSpec
    rationale: str

    @property
    def coordinate_text(self) -> str:
        return f"{self.coordinate[0]}:{self.coordinate[1]}"


def _ko(value: str) -> str:
    """Keep source literals Unicode-stable even when a legacy terminal is CP949."""

    return value.encode("ascii").decode("unicode_escape")


CHANGES = (
    Change(
        coordinate=(2, 489),
        literal_id=1,
        edit_kind="replace_literal",
        target_literal=_ko(r"\uC8FC\uACA0\uB2E4!"),
        term_from=None,
        term_to=None,
        input_record_sha256="695E6F265001FD6A1B945504D775EF8621D592B669539854297B649A16706C54",
        input_record_size=71,
        input_literal_utf16le_sha256=(
            "C04FC6EDC23D67D4B8D24860F046AA25C6644EA15BB58C3F770CBA1C883B43F3",
            "10B8C259A3B34A5004F3C4B530F2CDDA2A6CF734404DB81DD8A83FE1672837AD",
        ),
        target_record_sha256="BC4E56D7BF2495988E1122FDB775EBE1CFA975A7356C9F16EFF9DFE6EAA1B0FA",
        target_record_size=69,
        target_literal_utf16le_sha256=(
            "C04FC6EDC23D67D4B8D24860F046AA25C6644EA15BB58C3F770CBA1C883B43F3",
            "9F8D5FC921FE5EA867C86355B991C10EA422B31E5415244483B83C2FA6F1CDA2",
        ),
        opaque_spans_hex=("", "", "050505"),
        layout=LayoutSpec((480, 672), (480, 624), DIALOGUE_MAX_LINE_PX),
        rationale="The PC anchors mean 'give an opportunity/stage', not 'bestow'.",
    ),
    Change(
        coordinate=(2, 519),
        literal_id=0,
        edit_kind="replace_literal",
        target_literal=_ko(
            r"\uD3EC\uC704\uBCD1\uB4E4\uC774 \uB9C8\uC74C\uB300\uB85C "
            r"\uD558\uAC8C \uB450\uC9C0 "
        ),
        term_from=None,
        term_to=None,
        input_record_sha256="40FD363013EE0303696156FD03F9580B01FF78201EA9D6944924C3D964156AA2",
        input_record_size=85,
        input_literal_utf16le_sha256=(
            "A01B62F66F773CD6A2787D0529E3246FCAD9393470291B07CBA441F135512A18",
            "028355A6E5EED449F0F39F7ED3139D010F7908CCF7B77C3D1BCB0C3992F45634",
            "048A65922191B2A4E6B695C330B568B1F226FC3E3F882BBAC018E744179D0754",
        ),
        target_record_sha256="2441FC7CBB34E16E7417A2A2F4BF014B333B267F48F15B2A2F76BBB1972A2AE9",
        target_record_size=89,
        target_literal_utf16le_sha256=(
            "89C9A5C4A9430D9E1570CDC349C57706C908AE5AAD6BB3477F7A5A622BC480CA",
            "028355A6E5EED449F0F39F7ED3139D010F7908CCF7B77C3D1BCB0C3992F45634",
            "048A65922191B2A4E6B695C330B568B1F226FC3E3F882BBAC018E744179D0754",
        ),
        opaque_spans_hex=("", "", "", "050505"),
        layout=LayoutSpec((792, 528), (888, 528), DIALOGUE_MAX_LINE_PX),
        rationale="The PC anchors require a subject marker on the encircling troops.",
    ),
    Change(
        coordinate=(13, 328),
        literal_id=0,
        edit_kind="replace_term_once",
        target_literal=None,
        term_from=_ko(r"\uC911\uACC4\uC810"),
        term_to=_ko(r"\uACBD\uC720\uC810"),
        input_record_sha256="E71D769AD0B7AEAED2A04433BA94C81EF9282ABEE0024CBAC566202FA189B454",
        input_record_size=159,
        input_literal_utf16le_sha256=(
            "A98994074197FCC7827B72109AC7CE8BC6921631BCD8267D8D6FAD63CAA3A3D4",
        ),
        target_record_sha256="AA5A825FB7C25B5F1202F4A71036C4B822026EB11C4108F836B36E0AC5C7DDDA",
        target_record_size=159,
        target_literal_utf16le_sha256=(
            "2DB0AF4FF9A389FCA071298C84990727494E137B429D8CFC230CC5DB6D75735F",
        ),
        opaque_spans_hex=("", "050505"),
        layout=LayoutSpec((192, 1632, 1248), (192, 1632, 1248), None),
        rationale="Match the reviewed Base tutorial's existing Korean term for 中継点.",
    ),
)
CHANGE_BY_COORDINATE = {change.coordinate: change for change in CHANGES}
if len(CHANGE_BY_COORDINATE) != len(CHANGES):
    raise RuntimeError("duplicate Wave 17 record coordinate")


ANCHORS: dict[tuple[int, int], dict[str, AnchorSpec]] = {
    (2, 489): {
        "JP": AnchorSpec(
            "31F2A7FD9D3E3204E1FB129AB79AE091A6C363D9C3493BBDF6A0DEC08D7662DA",
            61,
            (
                "6AE362CD138DC2C86C5C5EC6A3B184A9C35744A8422E152EF74B8228EBD59108",
                "4B3A43F592F577FCFCB5B0E1F42BEC5182C9EDC414E1F667528F56E7CF0BE11D",
            ),
            "F1DD205368DC3B56AE50EB1CFD3A46D88D0A1416384370EE098E1C8EA205A089",
            "83A9CB21CB9F1858BFC8C72DAC523962BEC50A6DB77961B3A677F679A53DC124",
            ("", "01431E040000", "050505"),
        ),
        "SC": AnchorSpec(
            "46D4835924930673C8B06B417E982DC81A42B9DFB74DDBFDCEFEE2D62FC19B95",
            45,
            ("7DE40CED3DE54AA305F66FCE5E3974CFABA975DF452E7F8677DE363143E4FFB4",),
            "48AE1679A54F7188FA7676238AD34685B105C276F3B33CAA0E190BB5F34B8D74",
            "7DE40CED3DE54AA305F66FCE5E3974CFABA975DF452E7F8677DE363143E4FFB4",
            ("", "050505"),
        ),
        "TC": AnchorSpec(
            "7D7BBEBEFFEB69AFA85D4529000F087ADB8175DF7FED207929CC0356CAA7108F",
            43,
            ("7C34BD79BF979A52F02536F5A88B75ECEC80CCA84D3829B66C9F7D27B3E9B2D3",),
            "9415174DCAE9C993CBBD078CC31A86188894408026FDC94F8CBC6027EFDD2879",
            "7C34BD79BF979A52F02536F5A88B75ECEC80CCA84D3829B66C9F7D27B3E9B2D3",
            ("", "050505"),
        ),
    },
    (2, 519): {
        "JP": AnchorSpec(
            "1B7521434A2DBBD13A4BB037FEB390F1515CBC5912A72CF83575F34DD0A2FCE9",
            73,
            (
                "AE84B934003B53AAC53713442D34F109AEFE95498C3F4D6223D836EE5BEA1679",
                "F6002A6CE6F4E09100DC3AA4B8B337A176DE3BC5557065428B162E9766C09347",
                "4B3A43F592F577FCFCB5B0E1F42BEC5182C9EDC414E1F667528F56E7CF0BE11D",
            ),
            "631229FBCE573B368A9D3EBE3F244FD77B80C8EF1638F47DA91EA5A91B3C4EEF",
            "68E9EB971C819D669224E54BE64FFE2867B7F803AD8CAAAC9E0427CA23F3D649",
            ("", "0143E0020000", "0143CC010000", "050505"),
        ),
        "SC": AnchorSpec(
            "68BE13C68ABF3E4150578D781E0F30064D52E082E91792B81DE309C60D3C0EA8",
            51,
            ("3662F4A6651FE92CF75EE406985C3F0FB89BE4CFEE4DBC4BAC3466BF27F5D876",),
            "412567C8F09D6AEDEE9EDB3143247A0BFDAFFEA6D3D38E74103181ABFA58C69E",
            "3662F4A6651FE92CF75EE406985C3F0FB89BE4CFEE4DBC4BAC3466BF27F5D876",
            ("", "050505"),
        ),
        "TC": AnchorSpec(
            "67D6C62D736D1621C7031C10FDF95FDD5CFB119BDD302E073889D1CE8041E521",
            51,
            ("F0E2AA1590B9D2627B7BD13DF3E4F318532BECD12C7A351ED549D1C40682398C",),
            "97FF175FEFC496468BC23E998E9DF64B2662B5E3048BE79D30732A7E32960A32",
            "F0E2AA1590B9D2627B7BD13DF3E4F318532BECD12C7A351ED549D1C40682398C",
            ("", "050505"),
        ),
    },
    (13, 328): {
        "JP": AnchorSpec(
            "1DD3B601021D00CC88C7B362E78F2CE491EAFB259616774C2DF549A15200F5A7",
            135,
            ("2E026C73035A36FB63109B8136E3E1CBEF8715D4D34D8200EFBC78CEE8B6BCF6",),
            "4F00181D37B2E0BC7526B48360937B7A3AD634B594D6419BD5B7C1F07F9989BE",
            "2E026C73035A36FB63109B8136E3E1CBEF8715D4D34D8200EFBC78CEE8B6BCF6",
            ("", "050505"),
        ),
        "SC": AnchorSpec(
            "5C31F21AB689DF8D71F7659EE36E103948BA9C89A9E50984D4A5C219AE5B87DD",
            121,
            ("0D5FF95C8A08E1BD165E2B6E190E98822B461648E014A42A6B4F7B15EA209C4F",),
            "0E3A343A2BC1C073EAC76B5031E5A3F40B43040BD6AEDD944342894651A82849",
            "0D5FF95C8A08E1BD165E2B6E190E98822B461648E014A42A6B4F7B15EA209C4F",
            ("", "050505"),
        ),
        "TC": AnchorSpec(
            "E27E7E94842C715AE803686082AD4A0C11B1808E8426AB8B11E8CE1B4244B252",
            111,
            ("BDCB1AD9642499858E8B248B8EAFC4A22FD5736FC5B24A489501E789B20B48A6",),
            "75C688F740806CCED7B5E7A38D8A1C4D4E2CBC590A56BBD53968BDE1D3AD7C0C",
            "BDCB1AD9642499858E8B248B8EAFC4A22FD5736FC5B24A489501E789B20B48A6",
            ("", "050505"),
        ),
    },
}


class Wave17Error(RuntimeError):
    """Raised when a strict source, format, or output contract is violated."""


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


def literal_chain_sha256(values: tuple[str, ...]) -> str:
    return sha256_bytes("\n".join(text_sha256(value) for value in values).encode("ascii"))


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


def profile_hashes(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for relative in PROFILE_PATHS:
        path = root / relative
        if not path.is_file():
            raise Wave17Error(f"profile resource is absent: {relative}")
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
        raise Wave17Error(f"{label} profile mismatch: {json.dumps(mismatch, sort_keys=True)}")


def validate_raw_roundtrip(packed: bytes, label: str) -> None:
    header, raw = decompress_wrapper(packed)
    archive = parse_packed_msggame(packed).archive
    if rebuild_raw_msggame(archive) != raw:
        raise Wave17Error(f"{label} raw parse/rebuild differs")
    repacked = recompress_wrapper(raw, header)
    _repacked_header, roundtrip_raw = decompress_wrapper(repacked)
    if roundtrip_raw != raw:
        raise Wave17Error(f"{label} wrapper round-trip differs")


def reject_switch_path(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    if any("switch" in part.casefold() for part in resolved.parts):
        raise Wave17Error(f"Switch Korean input is forbidden: {label}")
    return resolved


def validate_pc_anchors() -> dict[str, Any]:
    archives: dict[str, dict[tuple[int, int], MsgGameRecord]] = {}
    reference_hashes: dict[str, str] = {}
    for language, (path, expected_hash) in PC_REFERENCE_PATHS.items():
        checked = reject_switch_path(path, f"PC {language}")
        actual_hash = sha256_path(checked)
        if actual_hash != expected_hash:
            raise Wave17Error(
                f"PC {language} source hash differs: expected {expected_hash}, got {actual_hash}"
            )
        archives[language] = records_by_coordinate(checked.read_bytes())
        reference_hashes[language] = actual_hash

    result: dict[str, Any] = {}
    for coordinate, by_language in ANCHORS.items():
        coordinate_text = f"{coordinate[0]}:{coordinate[1]}"
        result[coordinate_text] = {}
        for language, expected in by_language.items():
            record = archives[language].get(coordinate)
            if record is None:
                raise Wave17Error(f"PC {language} anchor lacks {coordinate_text}")
            values = literal_texts(record)
            actual_spans = tuple(value.hex().upper() for value in opaque_spans(record))
            if (
                sha256_bytes(record.data) != expected.record_sha256
                or len(record.data) != expected.record_size
                or tuple(text_sha256(value) for value in values)
                != expected.literal_utf16le_sha256
                or literal_chain_sha256(values) != expected.literal_chain_sha256
                or text_sha256("".join(values)) != expected.context_utf16le_sha256
                or actual_spans != expected.opaque_spans_hex
            ):
                raise Wave17Error(f"PC {language} anchor drift at {coordinate_text}")
            result[coordinate_text][language] = {
                "record_sha256": expected.record_sha256,
                "literal_utf16le_sha256": list(expected.literal_utf16le_sha256),
                "literal_chain_sha256": expected.literal_chain_sha256,
                "context_utf16le_sha256": expected.context_utf16le_sha256,
                "opaque_spans_hex": list(expected.opaque_spans_hex),
            }
    return {
        "reference_packed_sha256": reference_hashes,
        "records": result,
    }


def target_literals(change: Change, current: tuple[str, ...]) -> tuple[str, ...]:
    if not 0 <= change.literal_id < len(current):
        raise Wave17Error(f"{change.coordinate_text} literal index is absent")
    target = list(current)
    if change.edit_kind == "replace_literal":
        if change.target_literal is None:
            raise Wave17Error(f"{change.coordinate_text} target literal is absent")
        target[change.literal_id] = change.target_literal
    elif change.edit_kind == "replace_term_once":
        if change.term_from is None or change.term_to is None:
            raise Wave17Error(f"{change.coordinate_text} terminology replacement is absent")
        original = target[change.literal_id]
        if original.count(change.term_from) != 1:
            raise Wave17Error(f"{change.coordinate_text} expected terminology occurrence differs")
        target[change.literal_id] = original.replace(change.term_from, change.term_to)
    else:
        raise Wave17Error(f"{change.coordinate_text} unknown edit kind: {change.edit_kind}")
    return tuple(target)


def validate_literal_text(value: str, label: str) -> None:
    if "\x1b" in value or "%" in value:
        raise Wave17Error(f"{label} adds an ESC or printf marker")
    encoded = value.encode("utf-16-le")
    if LITERAL_START in encoded or LITERAL_END in encoded:
        raise Wave17Error(f"{label} encodes a reserved literal marker")
    for character in value:
        if character not in ("\n", "\r") and unicodedata.category(character) == "Cc":
            raise Wave17Error(f"{label} contains control U+{ord(character):04X}")


def text_format_signature(value: str) -> tuple[tuple[str, ...], str, str]:
    return (
        tuple(re.findall(r"\r\n|\n|\r", value)),
        value[: len(value) - len(value.lstrip())],
        value[len(value.rstrip()) :],
    )


def validate_change(change: Change, record: MsgGameRecord) -> tuple[tuple[str, ...], dict[str, Any]]:
    current = literal_texts(record)
    before_spans = opaque_spans(record)
    if (
        sha256_bytes(record.data) != change.input_record_sha256
        or len(record.data) != change.input_record_size
        or tuple(text_sha256(value) for value in current) != change.input_literal_utf16le_sha256
        or tuple(value.hex().upper() for value in before_spans) != change.opaque_spans_hex
        or not record.data.endswith(RECORD_TERMINATOR)
    ):
        raise Wave17Error(f"{change.coordinate_text} current record guard differs")

    target = target_literals(change, current)
    for literal_id, value in enumerate(target):
        validate_literal_text(value, f"{change.coordinate_text}:{literal_id}")
        if value != current[literal_id] and text_format_signature(value) != text_format_signature(
            current[literal_id]
        ):
            raise Wave17Error(f"{change.coordinate_text}:{literal_id} changes linebreak or edge whitespace")

    replacements = {
        literal_id: value
        for literal_id, value in enumerate(target)
        if value != current[literal_id]
    }
    rebuilt_data = rebuild_record_literals(record, replacements)
    rebuilt = MsgGameRecord(record.block_id, record.record_id, record.relative_offset, rebuilt_data)
    if (
        sha256_bytes(rebuilt.data) != change.target_record_sha256
        or len(rebuilt.data) != change.target_record_size
        or literal_texts(rebuilt) != target
        or tuple(text_sha256(value) for value in target) != change.target_literal_utf16le_sha256
        or opaque_spans(rebuilt) != before_spans
        or marker_topology(rebuilt) != marker_topology(record)
        or not rebuilt.data.endswith(RECORD_TERMINATOR)
    ):
        raise Wave17Error(f"{change.coordinate_text} literal/opaque reconstruction differs")

    return target, {
        "coordinate": change.coordinate_text,
        "input_record_sha256": change.input_record_sha256,
        "target_record_sha256": change.target_record_sha256,
        "input_record_size": change.input_record_size,
        "target_record_size": change.target_record_size,
        "current_literal_utf16le_sha256": list(change.input_literal_utf16le_sha256),
        "target_literal_utf16le_sha256": list(change.target_literal_utf16le_sha256),
        "input_opaque_spans_hex": list(change.opaque_spans_hex),
        "target_opaque_spans_hex": list(change.opaque_spans_hex),
        "linebreak_count": {
            "current": sum(value.count("\n") for value in current),
            "target": sum(value.count("\n") for value in target),
        },
        "rationale": change.rationale,
    }


def load_font_advance(
    steam_root: Path,
) -> tuple[Callable[[str], tuple[int, bool]], dict[str, Any]]:
    path = steam_root / FONT_PATH
    if not path.is_file():
        raise Wave17Error(f"font resource is absent: {path}")
    actual_hash = sha256_path(path)
    if actual_hash != FONT_SHA256:
        raise Wave17Error(f"font profile differs: expected {FONT_SHA256}, got {actual_hash}")
    try:
        archive = parse_link(path.read_bytes())
        _header, raw = decompress_wrapper(archive.entries[6].data)
    except (IndexError, ValueError) as exc:
        raise Wave17Error("JP font entry 6 cannot be unpacked") from exc
    with tempfile.TemporaryDirectory(prefix="nobu16_wave17_font_") as directory:
        font_path = Path(directory) / "font.g1n"
        font_path.write_bytes(raw)
        parsed = g1n.parse_g1n(font_path)
    if parsed.structural_errors or not parsed.tables:
        raise Wave17Error("JP font is structurally invalid")
    table = parsed.tables[0]

    def advance(character: str) -> tuple[int, bool]:
        if len(character) != 1:
            raise Wave17Error("font metric requires one character")
        ordinal = table.mapping[ord(character)] if ord(character) < len(table.mapping) else 0
        if ordinal == 0:
            if WIDE_SCRIPT_RE.fullmatch(character):
                return 48, True
            raise Wave17Error(f"JP font lacks glyph U+{ord(character):04X}")
        if ordinal >= len(table.records):
            raise Wave17Error(f"JP font ordinal is invalid for U+{ord(character):04X}")
        glyph = table.records[ordinal]
        if glyph.width != glyph.advance or glyph.advance not in (24, 48):
            raise Wave17Error(f"JP glyph metrics are invalid for U+{ord(character):04X}")
        return glyph.advance, False

    return advance, {
        "resource": FONT_PATH,
        "entry": 6,
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
                raise Wave17Error(f"font layout has control U+{ord(character):04X}")
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
    current: Mapping[tuple[int, int], MsgGameRecord],
    target: Mapping[tuple[int, int], MsgGameRecord],
    steam_root: Path,
) -> dict[str, Any]:
    advance, font = load_font_advance(steam_root)
    result: dict[str, Any] = {}
    for change in CHANGES:
        before = line_layout(literal_texts(current[change.coordinate]), advance)
        after = line_layout(literal_texts(target[change.coordinate]), advance)
        if (
            tuple(before["line_widths_px"]) != change.layout.current_widths_px
            or tuple(after["line_widths_px"]) != change.layout.target_widths_px
            or before["wide_fallback_codepoints"]
            or after["wide_fallback_codepoints"]
        ):
            raise Wave17Error(f"{change.coordinate_text} font layout differs")
        if change.layout.dialogue_limit_px is not None and after["max_width_px"] > change.layout.dialogue_limit_px:
            raise Wave17Error(f"{change.coordinate_text} exceeds dialogue width bound")
        if change.layout.dialogue_limit_px is None and before["line_widths_px"] != after["line_widths_px"]:
            raise Wave17Error(f"{change.coordinate_text} tutorial line widths changed")
        result[change.coordinate_text] = {
            "current": before,
            "target": after,
            "width_delta_px": [
                target_width - current_width
                for current_width, target_width in zip(
                    before["line_widths_px"], after["line_widths_px"]
                )
            ],
            "dialogue_limit_px": change.layout.dialogue_limit_px,
        }
    return {"font": font, "records": result}


def validate_output_records(packed: bytes) -> dict[tuple[int, int], MsgGameRecord]:
    records = records_by_coordinate(packed)
    for change in CHANGES:
        record = records.get(change.coordinate)
        if record is None:
            raise Wave17Error(f"candidate lacks {change.coordinate_text}")
        if (
            sha256_bytes(record.data) != change.target_record_sha256
            or len(record.data) != change.target_record_size
            or tuple(text_sha256(value) for value in literal_texts(record))
            != change.target_literal_utf16le_sha256
            or tuple(value.hex().upper() for value in opaque_spans(record))
            != change.opaque_spans_hex
            or not record.data.endswith(RECORD_TERMINATOR)
        ):
            raise Wave17Error(f"candidate record differs: {change.coordinate_text}")
    return records


def prepare_candidate(steam_root: Path) -> tuple[bytes, dict[str, Any]]:
    steam_root = steam_root.resolve(strict=True)
    assert_profile(steam_root, INPUT_SHA256, "current Steam")
    input_packed = (steam_root / BASE_MSGGAME).read_bytes()
    if len(input_packed) != INPUT_BASE_PACKED_SIZE:
        raise Wave17Error("Base msggame input size differs")
    validate_raw_roundtrip(input_packed, "current Base msggame")
    anchors = validate_pc_anchors()

    before_records = records_by_coordinate(input_packed)
    replacements: dict[tuple[int, int, int], str] = {}
    audit_records: list[dict[str, Any]] = []
    for change in CHANGES:
        record = before_records.get(change.coordinate)
        if record is None:
            raise Wave17Error(f"current Base msggame lacks {change.coordinate_text}")
        target, row = validate_change(change, record)
        for literal_id, value in enumerate(target):
            current_value = literal_texts(record)[literal_id]
            if value != current_value:
                key = (*change.coordinate, literal_id)
                if key in replacements:
                    raise Wave17Error(f"duplicate literal replacement: {key}")
                replacements[key] = value
        audit_records.append(row)

    output = rebuild_packed_with_literals(input_packed, replacements)
    if len(output) != TARGET_BASE_PACKED_SIZE or sha256_bytes(output) != TARGET_SHA256[BASE_MSGGAME]:
        raise Wave17Error("Base candidate packed output differs")
    validate_raw_roundtrip(output, "candidate Base msggame")

    after_records = validate_output_records(output)
    changed = {
        coordinate
        for coordinate in before_records
        if before_records[coordinate].data != after_records[coordinate].data
    }
    if changed != set(CHANGE_BY_COORDINATE):
        raise Wave17Error(f"candidate changed record set differs: {sorted(changed)}")
    for coordinate, record in before_records.items():
        if coordinate not in changed and record.data != after_records[coordinate].data:
            raise Wave17Error(f"unexpected record byte change: {coordinate}")

    font_layout = validate_font_layouts(before_records, after_records, steam_root)
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "platform": "Steam PC",
            "wave15_plus_wave16_issue61_successor_profile_required": True,
            "pristine_pc_japanese_read": True,
            "pc_sc_tc_context_read": True,
            "switch_korean_read": False,
            "steam_game_resource_written": False,
            "git_operation": "absent",
            "release_operation": "absent",
        },
        "input_sha256": INPUT_SHA256,
        "target_sha256": TARGET_SHA256,
        "pc_anchors": anchors,
        "font_layout": font_layout,
        "records": audit_records,
    }
    return output, audit


def require_tmp(path: Path, label: str) -> Path:
    root = TMP_ROOT.resolve(strict=False)
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave17Error(f"{label} must stay below {root}") from exc
    return resolved


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def verify_private_candidate(candidate_root: Path) -> None:
    candidate_root = require_tmp(candidate_root, "candidate root")
    assert_profile(candidate_root, TARGET_SHA256, "private candidate")
    base = (candidate_root / BASE_MSGGAME).read_bytes()
    if len(base) != TARGET_BASE_PACKED_SIZE:
        raise Wave17Error("private Base msggame size differs")
    validate_raw_roundtrip(base, "private candidate Base msggame")
    validate_output_records(base)


def build_candidate(
    steam_root: Path,
    output_root: Path,
    audit_path: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    output_root = require_tmp(output_root, "candidate output")
    audit_path = require_tmp(audit_path, "audit output")
    manifest_path = require_tmp(manifest_path, "manifest output")
    if output_root.exists() or audit_path.exists() or manifest_path.exists():
        raise Wave17Error("candidate output, audit, or manifest already exists")

    output, audit = prepare_candidate(steam_root)
    output_root.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.", dir=output_root.parent))
    try:
        for relative in PROFILE_PATHS:
            destination = stage / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if relative == BASE_MSGGAME:
                destination.write_bytes(output)
            else:
                shutil.copy2(steam_root / relative, destination)
        assert_profile(stage, TARGET_SHA256, "private candidate staging")
        os.replace(stage, output_root)
        verify_private_candidate(output_root)
        audit_bytes = (
            json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        atomic_write(audit_path, audit_bytes)
        manifest = {
            "schema": SCHEMA,
            "transaction_id": "pc-dialogue-quality-wave17-static-quality-v1",
            "candidate_only": True,
            "profile_paths": list(PROFILE_PATHS),
            "changed_paths": list(CHANGED_PATHS),
            "coordinates": [
                f"{BASE_MSGGAME}:{change.coordinate_text}:{change.literal_id}"
                for change in CHANGES
            ],
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
            (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
                "utf-8"
            ),
        )
        return manifest
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    hash_parser = sub.add_parser("hash", help="validate and hash the in-memory candidate")
    hash_parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    verify_parser = sub.add_parser("verify-private", help="verify a private candidate")
    verify_parser.add_argument("--candidate-root", type=Path, required=True)
    build_parser = sub.add_parser("build", help="write only below this workstream's tmp root")
    build_parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    build_parser.add_argument("--output-root", type=Path, default=TMP_ROOT / "candidate")
    build_parser.add_argument("--audit-path", type=Path, default=TMP_ROOT / "audit.v1.json")
    build_parser.add_argument(
        "--manifest-path", type=Path, default=TMP_ROOT / "build_manifest.v1.json"
    )
    args = parser.parse_args(argv)
    try:
        if args.command == "hash":
            _output, audit = prepare_candidate(args.steam_root)
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
            args.steam_root, args.output_root, args.audit_path, args.manifest_path
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
    except (OSError, ValueError, Wave17Error) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
