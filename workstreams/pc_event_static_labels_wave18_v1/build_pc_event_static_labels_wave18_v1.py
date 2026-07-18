#!/usr/bin/env python3
"""Build a private, fail-closed static-event-label candidate for Wave 18.

Exactly eight static entries in MSG_PK/JP/msgev.bin are changed.  The builder
reads only the pinned current Steam Korean table, pristine PC Japanese, and
the current PC EN/SC/TC tables plus the active Steam event-font metrics.
It has no Steam apply, transaction, Git, network, release, or Switch input.

All output is a new candidate directory below tmp/pc_event_static_labels_wave18_v1.
Any drift in a source file, source/duplicate anchor, text token signature,
font metric, or final raw/packed hash aborts rather than rebasing.
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
from typing import Any, Callable, Mapping, Sequence


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
PC_SC_RESOURCE = STEAM_ROOT / "MSG_PK" / "SC" / "msgev.bin"
PC_TC_RESOURCE = STEAM_ROOT / "MSG_PK" / "TC" / "msgev.bin"
EVENT_FONT_RESOURCE = STEAM_ROOT / "RES_JP" / "res_lang.bin"

SCHEMA = "nobu16.kr.pc-event-static-labels-wave18-candidate.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-event-static-labels-wave18-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-event-static-labels-wave18-manifest.v1"

EXPECTED_STRING_COUNT = 17_916

# The only accepted live Korean source is the already applied Wave 15 state.
INPUT_SIZE = 994_711
INPUT_SHA256 = "CE1A61E6C0F85A3E7F0FD4C1DD1BF0349A99CC134A9D73B7DE1917DB6646A0C3"
INPUT_RAW_SIZE = 990_800
INPUT_RAW_SHA256 = "3A43DD803C48239507C4070FC6B4014B9B5521DE6A583BEC75E5DA9195D62FD9"

PRISTINE_PC_JP_SIZE = 562_226
PRISTINE_PC_JP_SHA256 = "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84"
PRISTINE_PC_JP_RAW_SIZE = 894_800
PRISTINE_PC_JP_RAW_SHA256 = "07D7512BE0235753FC7BB0C7C548B61F471D9CDED01379E63B8AF8EAE013813E"

PC_EN_SIZE = 762_196
PC_EN_SHA256 = "BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E"
PC_EN_RAW_SIZE = 1_878_836
PC_EN_RAW_SHA256 = "6A1F3891412EBFF5AC3188F498C9951431154192D69E82B7ABB6F25AA934D911"

PC_SC_SIZE = 522_177
PC_SC_SHA256 = "7C443515D8B42DD5D1A516FE606DB8880F21296F7BEF0C5D067FEA7D9FC991BA"
PC_SC_RAW_SIZE = 754_708
PC_SC_RAW_SHA256 = "3ACE267E6B9774D8C940C9D7940F168B61744ADDF7C082F2CB1EA7E9BBD82B5E"

PC_TC_SIZE = 524_909
PC_TC_SHA256 = "89D183BA95C3BB83B52A5EE408664D5247C695A1DB192105A5D906737E6F78B6"
PC_TC_RAW_SIZE = 744_212
PC_TC_RAW_SHA256 = "42DC893AA9FF9D3E7B75FBCFFBEFD7C3DFC338CAB71E942C081BDC52C9024BF6"

EVENT_FONT_SIZE = 161_428_458
EVENT_FONT_SHA256 = "3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7"
FONT_OUTER_ENTRY = 6
FONT_TABLE = 0
FONT_MAP_BYTES = 0x20000
FONT_RECORD_BYTES = 12
MAX_LINE_PX = 912
MAX_LINES = 3

TARGET_SIZE = 994_727
TARGET_SHA256 = "D922E7C2B0BD4078A5DB14C87973ECB7BB1A62A4CA2EA30A03A231AB40C1E86B"
TARGET_RAW_SIZE = 990_816
TARGET_RAW_SHA256 = "86E45EA2C485FED6E1D24F74EE4E085479683C7C1269EB77710484762439B7F2"

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


class Wave18Error(RuntimeError):
    """Raised when a pinned input or private-output contract differs."""


@dataclass(frozen=True)
class SourceResource:
    language: str
    path: Path
    size: int
    sha256: str
    raw_size: int
    raw_sha256: str


@dataclass(frozen=True)
class SourceAnchor:
    language: str
    text: str
    utf16le_sha256: str


@dataclass(frozen=True)
class DuplicateAnchor:
    entry_id: int
    jp_text: str
    jp_utf16le_sha256: str
    current_ko_text: str
    current_ko_utf16le_sha256: str
    matches_target: bool


@dataclass(frozen=True)
class EraFormatAnchor:
    entry_id: int
    jp_text: str
    jp_utf16le_sha256: str
    current_ko_text: str
    current_ko_utf16le_sha256: str


@dataclass(frozen=True)
class Change:
    entry_id: int
    current_text: str
    target_text: str
    current_text_sha256: str
    target_text_sha256: str
    source_anchors: tuple[SourceAnchor, ...]
    duplicate_anchors: tuple[DuplicateAnchor, ...]
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


def source_anchors(
    jp_text: str,
    jp_hash: str,
    en_text: str,
    en_hash: str,
    sc_text: str,
    sc_hash: str,
    tc_text: str,
    tc_hash: str,
) -> tuple[SourceAnchor, ...]:
    return (
        SourceAnchor("JP", jp_text, jp_hash),
        SourceAnchor("EN", en_text, en_hash),
        SourceAnchor("SC", sc_text, sc_hash),
        SourceAnchor("TC", tc_text, tc_hash),
    )


SOURCE_RESOURCES = {
    "JP": SourceResource(
        "JP",
        PRISTINE_PC_JP_RESOURCE,
        PRISTINE_PC_JP_SIZE,
        PRISTINE_PC_JP_SHA256,
        PRISTINE_PC_JP_RAW_SIZE,
        PRISTINE_PC_JP_RAW_SHA256,
    ),
    "EN": SourceResource(
        "EN",
        PC_EN_RESOURCE,
        PC_EN_SIZE,
        PC_EN_SHA256,
        PC_EN_RAW_SIZE,
        PC_EN_RAW_SHA256,
    ),
    "SC": SourceResource(
        "SC",
        PC_SC_RESOURCE,
        PC_SC_SIZE,
        PC_SC_SHA256,
        PC_SC_RAW_SIZE,
        PC_SC_RAW_SHA256,
    ),
    "TC": SourceResource(
        "TC",
        PC_TC_RESOURCE,
        PC_TC_SIZE,
        PC_TC_SHA256,
        PC_TC_RAW_SIZE,
        PC_TC_RAW_SHA256,
    ),
}


CHANGES = (
    Change(
        entry_id=11007,
        current_text="\ud558\ud558!",
        target_text="\ud558\ud56b!",
        current_text_sha256="CE09E23C5049CFFF024A4FABF4D540D13A9AFE039A7316BAD8EE1C48C5488612",
        target_text_sha256="20C1177749D8D064F55EAB592EFAEBC5AFED32E5188F087D858ED8985FFD9DCF",
        source_anchors=source_anchors(
            "\u306f\u306f\u3063\uff01",
            "B884F74FB428D9B06445377514738D2F0CF2DF42354A23991926CC101E20E8FA",
            "Yes my lord!",
            "8E174DE88C234B656E0ADEB799D4E4E1AB6E20DB9155458E9EE5C1FD44E72B3C",
            "\u9075\u547d\uff01",
            "2858F7B4CF943F1D3DCA51D01188A1495CC714317F79F919924AA7F5C8B5AB1C",
            "\u9075\u547d\uff01",
            "2858F7B4CF943F1D3DCA51D01188A1495CC714317F79F919924AA7F5C8B5AB1C",
        ),
        duplicate_anchors=tuple(
            DuplicateAnchor(
                entry_id=anchor_id,
                jp_text="\u306f\u306f\u3063\uff01",
                jp_utf16le_sha256="B884F74FB428D9B06445377514738D2F0CF2DF42354A23991926CC101E20E8FA",
                current_ko_text="\ud558\ud56b!",
                current_ko_utf16le_sha256="20C1177749D8D064F55EAB592EFAEBC5AFED32E5188F087D858ED8985FFD9DCF",
                matches_target=True,
            )
            for anchor_id in (8267, 8954, 8975, 9118, 9593, 9595)
        ),
        current_line_widths_px=(120,),
        target_line_widths_px=(120,),
    ),
    Change(
        entry_id=14040,
        current_text="\ub383\ud3ec\ub374\ub77c\uc774",
        target_text="\ucca0\ud3ec\uc804\ub798",
        current_text_sha256="487AB0E66ACCA98774AEDA07E97ED3A5115155E3805022A8B37D336882A04222",
        target_text_sha256="1783CE86C06EE7188AEEBF28722B472B605F955F1048C5AD0C657C8B6B0F6B92",
        source_anchors=source_anchors(
            "\u30c6\u30c3\u30dd\u30a6\u30c7\u30f3\u30e9\u30a4",
            "2CDF98E472D264A8CEF51E84170D73B7E03A3078E1DF4CD443D95122F0EB056A",
            "\u30c6\u30c3\u30dd\u30a6\u30c7\u30f3\u30e9\u30a4",
            "2CDF98E472D264A8CEF51E84170D73B7E03A3078E1DF4CD443D95122F0EB056A",
            "tiepaodongchuan",
            "0AA25B358269824D8D208BC6106CD8C9629267E01B0717D1BFAC89AE74007DA4",
            "U\u9435I\u7832H\u6771M\u50b3",
            "EB4DED93CE6797A78D63F407F714E2E7B98842ED20E7FD3B489F8E7F0B845E7D",
        ),
        duplicate_anchors=(
            DuplicateAnchor(
                entry_id=14619,
                jp_text="\u30c6\u30c3\u30dd\u30a6\u30c7\u30f3\u30e9\u30a4",
                jp_utf16le_sha256="2CDF98E472D264A8CEF51E84170D73B7E03A3078E1DF4CD443D95122F0EB056A",
                current_ko_text="\ucca0\ud3ec\uc804\ub798",
                current_ko_utf16le_sha256="1783CE86C06EE7188AEEBF28722B472B605F955F1048C5AD0C657C8B6B0F6B92",
                matches_target=True,
            ),
        ),
        current_line_widths_px=(240,),
        target_line_widths_px=(192,),
    ),
    Change(
        entry_id=14386,
        current_text="\uc57c\ubcf4\uc624\uc4f0\uad6c\ubaa8\ub178",
        target_text="\uc57c\ub9dd\uc744\uc787\ub294\uc790",
        current_text_sha256="70EA289A0A1A52A8FD86F5F7154EF265F8B6C0C55ED9E1FBBCB7739DC2301E12",
        target_text_sha256="8563D1232D3D57CDA9B202BF5B4E871DC195FC488D8B6587CF04BD1662ED6E35",
        source_anchors=source_anchors(
            "\u30e4\u30dc\u30a6\u30f2\u30c4\u30b0\u30e2\u30ce",
            "4BBE02AE77ACC5FE8BA67C31E09EF1F48AB55A3418986C44637843F7DDF7A999",
            "\u30e4\u30dc\u30a6\u30f2\u30c4\u30b0\u30e2\u30ce",
            "4BBE02AE77ACC5FE8BA67C31E09EF1F48AB55A3418986C44637843F7DDF7A999",
            "jichengyewangzhiren",
            "C9BEEF4EF90CC3972ECBDD629383E40A444DE6D6991FAB999D6C52DD5910F608",
            "T\u7e7cH\u627fK\u91ceK\u671bC\u4e4bB\u4eba",
            "1D9402ED7EFCDF37032FD89E2E38741131354F7BEC82C7EDB9028251E91C5660",
        ),
        duplicate_anchors=(
            DuplicateAnchor(
                entry_id=14622,
                jp_text="\u30e4\u30dc\u30a6\u30f2\u30c4\u30b0\u30e2\u30ce",
                jp_utf16le_sha256="4BBE02AE77ACC5FE8BA67C31E09EF1F48AB55A3418986C44637843F7DDF7A999",
                current_ko_text="\uc57c\ub9dd\uc744\uc787\ub294\uc790",
                current_ko_utf16le_sha256="8563D1232D3D57CDA9B202BF5B4E871DC195FC488D8B6587CF04BD1662ED6E35",
                matches_target=True,
            ),
        ),
        current_line_widths_px=(336,),
        target_line_widths_px=(288,),
    ),
    Change(
        entry_id=14391,
        current_text="\ub374\uc1fc\uc9c4\uace0\ub178\ub780",
        target_text="\ub374\uc1fc\uc9c4\uace0\uc758\ub09c",
        current_text_sha256="FFD12229B5EEEB774EDEC300CD5E22DA527C1E8210684508B25A6401104DC013",
        target_text_sha256="17673B651C90E851B227416C48C21EE906358F4E4E353A64E369D45A03B12DEA",
        source_anchors=source_anchors(
            "\u30c6\u30f3\u30b7\u30e7\u30a6\u30b8\u30f3\u30b4\u30ce\u30e9\u30f3",
            "07FD9E005D265F31A6D17AEB008BFB916741AC47153FB58A578FEB66EF0FEA3B",
            "\u30c6\u30f3\u30b7\u30e7\u30a6\u30b8\u30f3\u30b4\u30ce\u30e9\u30f3",
            "07FD9E005D265F31A6D17AEB008BFB916741AC47153FB58A578FEB66EF0FEA3B",
            "tianzhengrenwuzhiluan",
            "F8AFB61505191FE0CCFCE44A5BC384EDA27CCF61D0A868C2F786BA42237A27D7",
            "D\u5929E\u6b63D\u58ecD\u5348C\u4e4bM\u4e82",
            "CB084D2D664F33A6C0D90D3097FD47FA1B9997EA56FCF811790CC10CB02C8E49",
        ),
        duplicate_anchors=(
            DuplicateAnchor(
                entry_id=14621,
                jp_text="\u30c6\u30f3\u30b7\u30e7\u30a6\u30b8\u30f3\u30b4\u30ce\u30e9\u30f3",
                jp_utf16le_sha256="07FD9E005D265F31A6D17AEB008BFB916741AC47153FB58A578FEB66EF0FEA3B",
                current_ko_text="\ub374\uc1fc\uc9c4\uace0\uc758\ub09c",
                current_ko_utf16le_sha256="17673B651C90E851B227416C48C21EE906358F4E4E353A64E369D45A03B12DEA",
                matches_target=True,
            ),
        ),
        current_line_widths_px=(288,),
        target_line_widths_px=(288,),
    ),
    Change(
        entry_id=14403,
        current_text="\uace0\ub9c8\ud0a4\uac00\ucfe0\ud14c\ub178\ud0c0\ud0c0\uce74\uc774",
        target_text="\uace0\ub9c8\ud0a4\ub098\uac00\ucfe0\ud14c\uc804\ud22c",
        current_text_sha256="2848E41B70A59175371D30C803FFBED6D09D75B131A59B74463669377C026A02",
        target_text_sha256="5C15341DC6CEF92CB76CBF7998B0D96BEB7D8153077B3CEC78B4F5263121E34A",
        source_anchors=source_anchors(
            "\u30b3\u30de\u30ad\u30ac\u30af\u30c6\u30ce\u30bf\u30bf\u30ab\u30a4",
            "6AD16EBCD5FC3EAFAE2870A3C2691D4F824AB1F671BEE54E6688358A7FA46AE9",
            "\u30b3\u30de\u30ad\u30ac\u30af\u30c6\u30ce\u30bf\u30bf\u30ab\u30a4",
            "6AD16EBCD5FC3EAFAE2870A3C2691D4F824AB1F671BEE54E6688358A7FA46AE9",
            "xiaomuchangjiushoudezhandou",
            "FBABB22FD3DEDCD19D110E50DFC3CBBD0BABD39D0891B95B91F16DE6E92B361D",
            "C\u5c0fH\u7267H\u9577C\u4e45D\u624bH\u7684P\u6230J\u9b25",
            "31514B58879CCBFB90BA0A2AA35E5CF98B271802F6B78D0DEC01C4F029F0294F",
        ),
        duplicate_anchors=(
            DuplicateAnchor(
                entry_id=14627,
                jp_text="\u30b3\u30de\u30ad\u30ac\u30af\u30c6\u30ce\u30bf\u30bf\u30ab\u30a4",
                jp_utf16le_sha256="6AD16EBCD5FC3EAFAE2870A3C2691D4F824AB1F671BEE54E6688358A7FA46AE9",
                current_ko_text="\uace0\ub9c8\ud0a4\ub098\uac00\ucfe0\ud14c\uc804\ud22c",
                current_ko_utf16le_sha256="5C15341DC6CEF92CB76CBF7998B0D96BEB7D8153077B3CEC78B4F5263121E34A",
                matches_target=True,
            ),
        ),
        current_line_widths_px=(528,),
        target_line_widths_px=(432,),
    ),
    Change(
        entry_id=14623,
        current_text="\uc57c\ub9c8\uc790\ud0a4\uc804\ud22c\uc544\ucf00\uce58\uc2b9\ub9ac",
        target_text="\uc57c\ub9c8\uc790\ud0a4 \uc804\ud22c\u00b7\uc544\ucf00\uce58 \uc2b9\ub9ac",
        current_text_sha256="1CAB77164CB7E32F9F65419C20FE4828DBEC182FD1AC6A15D6A283D615C4975A",
        target_text_sha256="268717A64E9CE98D8D17FBF369ADF8344BDEF767069FBC07BE0E0CBCABCBC8D5",
        source_anchors=source_anchors(
            "\u30e4\u30de\u30b6\u30ad\u30ce\u30bf\u30bf\u30ab\u30a4\u30a2\u30b1\u30c1\u30b7\u30e7\u30a6\u30ea",
            "CA017C06BD8E30DF2C8C4C99EDA416D29338CF0D36429AAA2CBE9EF29149E9C3",
            "\u30e4\u30de\u30b6\u30ad\u30ce\u30bf\u30bf\u30ab\u30a4\u30a2\u30b1\u30c1\u30b7\u30e7\u30a6\u30ea",
            "CA017C06BD8E30DF2C8C4C99EDA416D29338CF0D36429AAA2CBE9EF29149E9C3",
            "shanqizhizhanmingzhishengli",
            "FF340F0B79258FD1E5481FE13F1B2F98BF0866BDED75EB93B498EF288099E6AD",
            "C\u5c71K\u5d0eD\u4e4bP\u6230H\u660eL\u667aL\u52ddG\u5229",
            "8DEA1C6B458E8AF1A64D1C3AB508B09B813D0194BA28CE0A31BD075DC69F0695",
        ),
        duplicate_anchors=(
            DuplicateAnchor(
                entry_id=14638,
                jp_text="\u30e4\u30de\u30b6\u30ad\u30ce\u30bf\u30bf\u30ab\u30a4\u30a2\u30b1\u30c1\u30b7\u30e7\u30a6\u30ea",
                jp_utf16le_sha256="CA017C06BD8E30DF2C8C4C99EDA416D29338CF0D36429AAA2CBE9EF29149E9C3",
                current_ko_text="\uc57c\ub9c8\uc790\ud0a4 \uc804\ud22c\u00b7\uc544\ucf00\uce58 \uc2b9\ub9ac",
                current_ko_utf16le_sha256="268717A64E9CE98D8D17FBF369ADF8344BDEF767069FBC07BE0E0CBCABCBC8D5",
                matches_target=True,
            ),
        ),
        current_line_widths_px=(528,),
        target_line_widths_px=(624,),
    ),
    Change(
        entry_id=14648,
        current_text="\uc2dc\ub300\uac1c\uc694\ub374\uc1fc10\ub144",
        target_text="\uc2dc\ub300 \uac1c\uc694(\ub374\uc1fc 10\ub144)",
        current_text_sha256="3E40D6D3A5FD808A6B520E7715E29CA7B2175A4EFEB61DC013FD4C837A75C16E",
        target_text_sha256="E100CE5A7B5533CD1972C692780584DD4AD9B211D3BDF276648225617D31890C",
        source_anchors=source_anchors(
            "\u30b8\u30c0\u30a4\u30ac\u30a4\u30e8\u30a6\uff08\u30c6\u30f3\u30b7\u30e7\u30a6\u30b8\u30e5\u30a6\u30cd\u30f3\uff09",
            "C6C80E750A76DA8DCF0E4ED5802A4607A357DC4AFB254F8A775F5ED36B3A0EEE",
            "\u30b8\u30c0\u30a4\u30ac\u30a4\u30e8\u30a6\uff08\u30c6\u30f3\u30b7\u30e7\u30a6\u30b8\u30e5\u30a6\u30cd\u30f3\uff09",
            "C6C80E750A76DA8DCF0E4ED5802A4607A357DC4AFB254F8A775F5ED36B3A0EEE",
            "dummy",
            "2AB80B631AD896118B57262A7756C480D2BC0733C95357BC5EC1F4AD4A21CFAB",
            "dummy",
            "2AB80B631AD896118B57262A7756C480D2BC0733C95357BC5EC1F4AD4A21CFAB",
        ),
        duplicate_anchors=(
            DuplicateAnchor(
                entry_id=14651,
                jp_text="\u30b8\u30c0\u30a4\u30ac\u30a4\u30e8\u30a6\uff08\u30c6\u30f3\u30b7\u30e7\u30a6\u30b8\u30e5\u30a6\u30cd\u30f3\uff09",
                jp_utf16le_sha256="C6C80E750A76DA8DCF0E4ED5802A4607A357DC4AFB254F8A775F5ED36B3A0EEE",
                current_ko_text="\uc2dc\ub300\uac1c\uc694\ub374\uc1fc10\ub144",
                current_ko_utf16le_sha256="3E40D6D3A5FD808A6B520E7715E29CA7B2175A4EFEB61DC013FD4C837A75C16E",
                matches_target=False,
            ),
        ),
        current_line_widths_px=(384,),
        target_line_widths_px=(480,),
    ),
    Change(
        entry_id=14651,
        current_text="\uc2dc\ub300\uac1c\uc694\ub374\uc1fc10\ub144",
        target_text="\uc2dc\ub300 \uac1c\uc694(\ub374\uc1fc 10\ub144)",
        current_text_sha256="3E40D6D3A5FD808A6B520E7715E29CA7B2175A4EFEB61DC013FD4C837A75C16E",
        target_text_sha256="E100CE5A7B5533CD1972C692780584DD4AD9B211D3BDF276648225617D31890C",
        source_anchors=source_anchors(
            "\u30b8\u30c0\u30a4\u30ac\u30a4\u30e8\u30a6\uff08\u30c6\u30f3\u30b7\u30e7\u30a6\u30b8\u30e5\u30a6\u30cd\u30f3\uff09",
            "C6C80E750A76DA8DCF0E4ED5802A4607A357DC4AFB254F8A775F5ED36B3A0EEE",
            "\u30b8\u30c0\u30a4\u30ac\u30a4\u30e8\u30a6\uff08\u30c6\u30f3\u30b7\u30e7\u30a6\u30b8\u30e5\u30a6\u30cd\u30f3\uff09",
            "C6C80E750A76DA8DCF0E4ED5802A4607A357DC4AFB254F8A775F5ED36B3A0EEE",
            "shidaigaiyaotianzheng10nian",
            "21F463807BC05BF0182DCC07C0A083E013007B17857F2FF092C1BD6C51CAD546",
            "J\u6642E\u4ee3M\u6982I\u8981D\u5929E\u6b6310F\u5e74",
            "D5E7AE6B66303733FC50F0FF3DFC9BB83EF9D3EEC0A71E16F176D21EA7CEC36E",
        ),
        duplicate_anchors=(
            DuplicateAnchor(
                entry_id=14648,
                jp_text="\u30b8\u30c0\u30a4\u30ac\u30a4\u30e8\u30a6\uff08\u30c6\u30f3\u30b7\u30e7\u30a6\u30b8\u30e5\u30a6\u30cd\u30f3\uff09",
                jp_utf16le_sha256="C6C80E750A76DA8DCF0E4ED5802A4607A357DC4AFB254F8A775F5ED36B3A0EEE",
                current_ko_text="\uc2dc\ub300\uac1c\uc694\ub374\uc1fc10\ub144",
                current_ko_utf16le_sha256="3E40D6D3A5FD808A6B520E7715E29CA7B2175A4EFEB61DC013FD4C837A75C16E",
                matches_target=False,
            ),
        ),
        current_line_widths_px=(384,),
        target_line_widths_px=(480,),
    ),
)

CHANGE_BY_ID = {change.entry_id: change for change in CHANGES}
if len(CHANGE_BY_ID) != len(CHANGES):
    raise RuntimeError("Wave 18 has duplicate msgev IDs")

ERA_FORMAT_ANCHORS = (
    EraFormatAnchor(
        entry_id=14642,
        jp_text="\u30b8\u30c0\u30a4\u30ac\u30a4\u30e8\u30a6\uff08\u30b1\u30a4\u30c1\u30e7\u30a6\u30b4\u30cd\u30f3\uff09",
        jp_utf16le_sha256="ED268F36454AFC23FB0E7DDD82BEEB1ED78B13D3F9109CBCC36565BFBABAF610",
        current_ko_text="\uc2dc\ub300 \uac1c\uc694(\uac8c\uc774\ucd08 5\ub144)",
        current_ko_utf16le_sha256="639862271FDEC61CCE6A41B4E3D994F93125D42C9F65F1C387C54A29924FD392",
    ),
    EraFormatAnchor(
        entry_id=14643,
        jp_text="\u30b8\u30c0\u30a4\u30ac\u30a4\u30e8\u30a6\uff08\u30b1\u30a4\u30c1\u30e7\u30a6\u30b8\u30e5\u30a6\u30af\u30cd\u30f3\uff09",
        jp_utf16le_sha256="57E7B06806734FE30B4D4F0D2739F3DF93A2D43E310AF2D2B29A4CE2562C681F",
        current_ko_text="\uc2dc\ub300 \uac1c\uc694(\uac8c\uc774\ucd08 19\ub144)",
        current_ko_utf16le_sha256="48C7275B27750D5379C69DAA5CE29B150DB2A021CF60446E989A6D279F5490BE",
    ),
)

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
        raise Wave18Error(label)


def require_under(path: Path, root: Path, label: str) -> Path:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise Wave18Error(f"{label} escapes private tmp root: {resolved_path}") from exc
    return resolved_path


def require_private_output(path: Path, label: str = "candidate output") -> Path:
    return require_under(path, PRIVATE_TMP_ROOT, label)


def linebreak_vector(value: str) -> list[str]:
    return LINEBREAK_RE.findall(value)


def protected_signature(value: str) -> dict[str, Any]:
    """Return every non-text feature that must remain identical."""

    escapes: list[str] = []
    controls: list[str] = []
    cursor = 0
    while cursor < len(value):
        character = value[cursor]
        if character == "\x1b":
            token = value[cursor : cursor + 3]
            if ESC_RE.fullmatch(token) is None:
                raise Wave18Error(f"malformed ESC token at U+001B offset {cursor}")
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


def source_anchor_map(change: Change) -> dict[str, SourceAnchor]:
    result = {anchor.language: anchor for anchor in change.source_anchors}
    require(
        set(result) == {"JP", "EN", "SC", "TC"} and len(result) == len(change.source_anchors),
        f"id {change.entry_id} source anchor languages differ",
    )
    return result


def validate_declared_change(change: Change) -> None:
    require(
        text_hash(change.current_text) == change.current_text_sha256,
        f"id {change.entry_id} declared current text hash differs",
    )
    require(
        text_hash(change.target_text) == change.target_text_sha256,
        f"id {change.entry_id} declared target text hash differs",
    )
    source_map = source_anchor_map(change)
    for language, anchor in source_map.items():
        require(
            text_hash(anchor.text) == anchor.utf16le_sha256,
            f"id {change.entry_id} declared {language} anchor hash differs",
        )

    current_signature = protected_signature(change.current_text)
    target_signature = protected_signature(change.target_text)
    require(
        current_signature == target_signature == EMPTY_STATIC_SIGNATURE,
        f"id {change.entry_id} is not a plain static one-line replacement",
    )
    require(
        len(change.current_line_widths_px) == len(change.target_line_widths_px) == 1,
        f"id {change.entry_id} declared line count differs",
    )

    for duplicate in change.duplicate_anchors:
        require(
            duplicate.entry_id != change.entry_id,
            f"id {change.entry_id} has a self duplicate anchor",
        )
        require(
            text_hash(duplicate.jp_text) == duplicate.jp_utf16le_sha256,
            f"id {change.entry_id} duplicate {duplicate.entry_id} JP hash differs",
        )
        require(
            text_hash(duplicate.current_ko_text) == duplicate.current_ko_utf16le_sha256,
            f"id {change.entry_id} duplicate {duplicate.entry_id} Korean hash differs",
        )
        require(
            duplicate.jp_text == source_map["JP"].text,
            f"id {change.entry_id} duplicate {duplicate.entry_id} JP text differs",
        )
        expected_ko = change.target_text if duplicate.matches_target else change.current_text
        require(
            duplicate.current_ko_text == expected_ko,
            f"id {change.entry_id} duplicate {duplicate.entry_id} Korean relation differs",
        )


for _change in CHANGES:
    validate_declared_change(_change)


def validate_declared_era_format_anchor(anchor: EraFormatAnchor) -> None:
    require(
        text_hash(anchor.jp_text) == anchor.jp_utf16le_sha256,
        f"era format anchor {anchor.entry_id} JP hash differs",
    )
    require(
        text_hash(anchor.current_ko_text) == anchor.current_ko_utf16le_sha256,
        f"era format anchor {anchor.entry_id} Korean hash differs",
    )
    require(
        anchor.current_ko_text.startswith("\uc2dc\ub300 \uac1c\uc694(")
        and anchor.current_ko_text.endswith(")"),
        f"era format anchor {anchor.entry_id} Korean format differs",
    )


for _era_anchor in ERA_FORMAT_ANCHORS:
    validate_declared_era_format_anchor(_era_anchor)


def load_pinned_table(
    path: Path,
    *,
    label: str,
    expected_size: int,
    expected_sha256: str,
    expected_raw_size: int,
    expected_raw_sha256: str,
    require_literal_lz4: bool = False,
) -> TableResource:
    if not path.is_file():
        raise Wave18Error(f"{label} is absent: {path}")
    packed = path.read_bytes()
    require(len(packed) == expected_size, f"{label} size differs")
    require(sha256_bytes(packed) == expected_sha256, f"{label} SHA-256 differs")
    try:
        header, raw = decompress_wrapper(packed)
        table = parse_message_table(raw)
    except Exception as exc:
        raise Wave18Error(f"{label} cannot be parsed as a wrapped message table") from exc
    require(len(raw) == expected_raw_size, f"{label} raw size differs")
    require(sha256_bytes(raw) == expected_raw_sha256, f"{label} raw SHA-256 differs")
    require(
        table.string_count == EXPECTED_STRING_COUNT,
        f"{label} string count differs",
    )
    require(
        rebuild_message_table(table, table.texts) == raw,
        f"{label} unmodified message-table rebuild differs",
    )
    if require_literal_lz4:
        require(
            recompress_wrapper(raw, header) == packed,
            f"{label} LZ4 representation differs",
        )
    return TableResource(path.resolve(), packed, header, raw, table)


def load_current_steam_table(input_path: Path = CURRENT_STEAM_RESOURCE) -> TableResource:
    if input_path.resolve() != CURRENT_STEAM_RESOURCE.resolve():
        raise Wave18Error("Wave 18 accepts only the pinned current Steam PK msgev path")
    return load_pinned_table(
        CURRENT_STEAM_RESOURCE,
        label="current Steam PK msgev",
        expected_size=INPUT_SIZE,
        expected_sha256=INPUT_SHA256,
        expected_raw_size=INPUT_RAW_SIZE,
        expected_raw_sha256=INPUT_RAW_SHA256,
        require_literal_lz4=True,
    )


def load_pc_source_tables() -> dict[str, TableResource]:
    result: dict[str, TableResource] = {}
    for language, spec in SOURCE_RESOURCES.items():
        result[language] = load_pinned_table(
            spec.path,
            label=f"PC {language} msgev",
            expected_size=spec.size,
            expected_sha256=spec.sha256,
            expected_raw_size=spec.raw_size,
            expected_raw_sha256=spec.raw_sha256,
        )
    return result


def _u32(value: bytes, offset: int, label: str) -> int:
    if offset < 0 or offset + 4 > len(value):
        raise Wave18Error(f"event font {label} is outside G1N data")
    return struct.unpack_from("<I", value, offset)[0]


def load_event_font_advance() -> tuple[Callable[[str], int], dict[str, Any]]:
    """Read only active Steam event-font advances needed by the eight labels."""

    if not EVENT_FONT_RESOURCE.is_file():
        raise Wave18Error(f"active Steam event font is absent: {EVENT_FONT_RESOURCE}")
    packed = EVENT_FONT_RESOURCE.read_bytes()
    require(len(packed) == EVENT_FONT_SIZE, "active Steam event font size differs")
    require(sha256_bytes(packed) == EVENT_FONT_SHA256, "active Steam event font SHA-256 differs")
    try:
        archive = parse_link(packed)
        entry = archive.entries[FONT_OUTER_ENTRY]
        _wrapper, raw = decompress_wrapper(entry.data)
    except Exception as exc:
        raise Wave18Error("active Steam event font entry cannot be decoded") from exc

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
            raise Wave18Error(f"event font lacks U+{codepoint:04X}")
        if ordinal >= record_count:
            raise Wave18Error(f"event font maps U+{codepoint:04X} outside table 0")
        record_offset = record_start + ordinal * FONT_RECORD_BYTES
        width = raw[record_offset]
        glyph_advance = raw[record_offset + 4]
        if width != glyph_advance or glyph_advance not in (24, 48):
            raise Wave18Error(f"event font metric differs for U+{codepoint:04X}")
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
                    raise Wave18Error("event text contains malformed ESC token")
                cursor += 3
                continue
            if unicodedata.category(character) == "Cc":
                raise Wave18Error(f"event text contains control U+{ord(character):04X}")
            width += advance(character)
            cursor += 1
        widths.append(width)
    return tuple(widths)


def validate_live_change(
    change: Change,
    current_table: Any,
    source_tables: Mapping[str, Any],
    advance: Callable[[str], int],
) -> dict[str, Any]:
    source_map = source_anchor_map(change)
    require(
        change.entry_id < current_table.string_count,
        f"id {change.entry_id} is absent from current",
    )
    for language, resource in source_tables.items():
        require(
            change.entry_id < resource.table.string_count,
            f"id {change.entry_id} is absent from {language}",
        )

    current_text = current_table.texts[change.entry_id]
    require(current_text == change.current_text, f"id {change.entry_id} current text differs")
    require(
        text_hash(current_text) == change.current_text_sha256,
        f"id {change.entry_id} current text hash differs",
    )

    anchor_report: dict[str, dict[str, str]] = {}
    for language, anchor in source_map.items():
        observed = source_tables[language].table.texts[change.entry_id]
        require(observed == anchor.text, f"id {change.entry_id} {language} anchor text differs")
        require(
            text_hash(observed) == anchor.utf16le_sha256,
            f"id {change.entry_id} {language} anchor hash differs",
        )
        anchor_report[language] = {
            "text": observed,
            "utf16le_sha256": anchor.utf16le_sha256,
        }

    duplicate_report: list[dict[str, Any]] = []
    for duplicate in change.duplicate_anchors:
        require(
            duplicate.entry_id < current_table.string_count
            and duplicate.entry_id < source_tables["JP"].table.string_count,
            f"id {change.entry_id} duplicate {duplicate.entry_id} is absent",
        )
        observed_jp = source_tables["JP"].table.texts[duplicate.entry_id]
        observed_ko = current_table.texts[duplicate.entry_id]
        require(
            observed_jp == duplicate.jp_text,
            f"id {change.entry_id} duplicate {duplicate.entry_id} JP text differs",
        )
        require(
            text_hash(observed_jp) == duplicate.jp_utf16le_sha256,
            f"id {change.entry_id} duplicate {duplicate.entry_id} JP hash differs",
        )
        require(
            observed_ko == duplicate.current_ko_text,
            f"id {change.entry_id} duplicate {duplicate.entry_id} Korean text differs",
        )
        require(
            text_hash(observed_ko) == duplicate.current_ko_utf16le_sha256,
            f"id {change.entry_id} duplicate {duplicate.entry_id} Korean hash differs",
        )
        expected_ko = change.target_text if duplicate.matches_target else change.current_text
        require(
            observed_ko == expected_ko,
            f"id {change.entry_id} duplicate {duplicate.entry_id} Korean relation differs",
        )
        duplicate_report.append(
            {
                "id": duplicate.entry_id,
                "jp_text": observed_jp,
                "jp_utf16le_sha256": duplicate.jp_utf16le_sha256,
                "current_ko_text": observed_ko,
                "current_ko_utf16le_sha256": duplicate.current_ko_utf16le_sha256,
                "matches_target": duplicate.matches_target,
            }
        )

    current_signature = protected_signature(current_text)
    target_signature = protected_signature(change.target_text)
    require(
        current_signature == target_signature == EMPTY_STATIC_SIGNATURE,
        f"id {change.entry_id} control/token/linebreak signature differs",
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
        "anchors": anchor_report,
        "duplicate_anchors": duplicate_report,
        "format_invariants": {
            "current": current_signature,
            "target": target_signature,
            "identical": current_signature == target_signature,
        },
        "layout": {
            "current_line_widths_px": list(current_widths),
            "target_line_widths_px": list(target_widths),
            "max_line_px": MAX_LINE_PX,
            "max_lines": MAX_LINES,
        },
    }


def validate_era_format_anchors(current_table: Any, jp_table: Any) -> list[dict[str, Any]]:
    report: list[dict[str, Any]] = []
    for anchor in ERA_FORMAT_ANCHORS:
        require(anchor.entry_id < current_table.string_count, f"era format anchor {anchor.entry_id} is absent")
        observed_jp = jp_table.texts[anchor.entry_id]
        observed_ko = current_table.texts[anchor.entry_id]
        require(observed_jp == anchor.jp_text, f"era format anchor {anchor.entry_id} JP text differs")
        require(
            text_hash(observed_jp) == anchor.jp_utf16le_sha256,
            f"era format anchor {anchor.entry_id} JP hash differs",
        )
        require(
            observed_ko == anchor.current_ko_text,
            f"era format anchor {anchor.entry_id} Korean text differs",
        )
        require(
            text_hash(observed_ko) == anchor.current_ko_utf16le_sha256,
            f"era format anchor {anchor.entry_id} Korean hash differs",
        )
        require(
            observed_ko.startswith("\uc2dc\ub300 \uac1c\uc694(") and observed_ko.endswith(")"),
            f"era format anchor {anchor.entry_id} Korean format differs",
        )
        report.append(
            {
                "id": anchor.entry_id,
                "jp_text": observed_jp,
                "jp_utf16le_sha256": anchor.jp_utf16le_sha256,
                "current_ko_text": observed_ko,
                "current_ko_utf16le_sha256": anchor.current_ko_utf16le_sha256,
            }
        )
    return report


def validate_candidate(
    current: TableResource,
    candidate_packed: bytes,
    expected_texts: Sequence[str],
) -> tuple[bytes, Any]:
    require(len(candidate_packed) == TARGET_SIZE, "candidate packed size differs")
    require(sha256_bytes(candidate_packed) == TARGET_SHA256, "candidate packed SHA-256 differs")
    try:
        header, raw = decompress_wrapper(candidate_packed)
        table = parse_message_table(raw)
    except Exception as exc:
        raise Wave18Error("candidate cannot be parsed as a wrapped message table") from exc
    require(len(raw) == TARGET_RAW_SIZE, "candidate raw size differs")
    require(sha256_bytes(raw) == TARGET_RAW_SHA256, "candidate raw SHA-256 differs")
    require(table.string_count == EXPECTED_STRING_COUNT, "candidate string count differs")
    require(rebuild_message_table(table, table.texts) == raw, "candidate table rebuild differs")
    require(recompress_wrapper(raw, header) == candidate_packed, "candidate LZ4 representation differs")
    require(header.prefix == current.header.prefix, "candidate LZ4 wrapper prefix changed")
    require(tuple(table.texts) == tuple(expected_texts), "candidate text vector differs")
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
    """Validate all pins and assemble the private candidate wholly in memory."""

    current = load_current_steam_table(input_path)
    source_tables = load_pc_source_tables()
    require(
        all(resource.table.string_count == current.table.string_count for resource in source_tables.values()),
        "current and PC source string counts differ",
    )
    advance, font_report = load_event_font_advance()
    era_format_report = validate_era_format_anchors(current.table, source_tables["JP"].table)

    target_texts = list(current.table.texts)
    record_audit: list[dict[str, Any]] = []
    for change in CHANGES:
        record_audit.append(validate_live_change(change, current.table, source_tables, advance))
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
            "pc_simplified_chinese_anchor_read": True,
            "pc_traditional_chinese_anchor_read": True,
            "duplicate_korean_anchor_source": "current Steam MSG_PK/JP/msgev.bin only",
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
        "source_resources": {
            language: {
                "size": spec.size,
                "sha256": spec.sha256,
                "raw_size": spec.raw_size,
                "raw_sha256": spec.raw_sha256,
            }
            for language, spec in SOURCE_RESOURCES.items()
        },
        "font": font_report,
        "era_format_anchors": era_format_report,
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


def remove_private_staging(path: Path) -> None:
    resolved = require_private_output(path, "private staging cleanup")
    if resolved.exists():
        shutil.rmtree(resolved)


def write_candidate(bundle: CandidateBundle, output_root: Path) -> dict[str, Any]:
    """Write one new candidate directory under tmp; never write Steam."""

    output_root = require_private_output(output_root)
    if output_root.exists():
        raise Wave18Error(f"refusing to overwrite candidate output: {output_root}")
    output_root.parent.mkdir(parents=True, exist_ok=True)
    staging = output_root.parent / f".{output_root.name}.staging-{uuid.uuid4().hex}"
    staging = require_private_output(staging, "candidate staging output")
    if staging.exists():
        raise Wave18Error(f"candidate staging path already exists: {staging}")
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
        remove_private_staging(staging)
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
    except (OSError, ValueError, Wave18Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
