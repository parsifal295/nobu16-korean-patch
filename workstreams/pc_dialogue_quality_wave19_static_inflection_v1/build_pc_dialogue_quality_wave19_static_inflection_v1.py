#!/usr/bin/env python3
"""Build a private PC-only Wave 19 static-dialogue candidate.

The unique Wave 17 eleven-file private candidate is the sole Korean input.
Wave 19 reconstructs five paired Base/PK static dialogues, completing Korean
sentences and removing every Japanese 01 43 morphology command in ten
records.  It also carries two verified PK-only Wave 17 counterpart corrections,
for twelve records total.  It writes only below this workstream's private tmp
directory.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
import os
import re
import shutil
import struct
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
PREDECESSOR_CANDIDATE_ROOT = (
    REPO / "tmp" / "pc_dialogue_quality_wave17_static_quality_v1" / "candidate"
)
MSGGAME_TOOLS = REPO / "workstreams" / "msggame"
TOOLS = REPO / "tools"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")

for module_root in (TOOLS, MSGGAME_TOOLS):
    if str(module_root) not in sys.path:
        sys.path.insert(0, str(module_root))

from nobu16_lz4 import decompress_wrapper, parse_link, recompress_wrapper  # noqa: E402
from msggame_format import (  # noqa: E402
    LITERAL_END,
    LITERAL_START,
    MsgGameRecord,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_msggame,
    rebuild_raw_msggame,
)


SCHEMA = "nobu16.kr.pc-dialogue-quality-wave19-static-inflection.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave19-static-inflection-audit.v1"
BASE_MSGGAME = "MSG/JP/msggame.bin"
PK_MSGGAME = "MSG_PK/JP/msggame.bin"
CHANGED_PATHS = (BASE_MSGGAME, PK_MSGGAME)
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
MORPHOLOGY_PREFIX = b"\x01\x43"
DIALOGUE_MAX_LINE_PX = 912
FONT_RESOURCE = DEFAULT_STEAM_ROOT / "RES_JP/res_lang.bin"
FONT_SHA256 = "3798CB758E6EA48A257F1FBBBBE56E800F668E6FA2DE0CFD4B277C785A322EE7"
FONT_OUTER_ENTRY = 6
FONT_TABLE = 0
FONT_MAP_BYTES = 0x20000
FONT_RECORD_BYTES = 12
WIDE_SCRIPT_RE = re.compile(
    r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u9fff\uac00-\ud7a3\uf900-\ufaff]"
)

# Unique Wave 17 successor profile, including Issue 61 strdata/msgdata.
INPUT_SHA256 = {
    "MSG/JP/ev_strdata.bin": "BF224468BFBCF3CC71DFF4609142A60D75091813281EE6F2333645413AD81B80",
    BASE_MSGGAME: "C1B39C7344F8A095E179942A26FB4EBDECEAABC2D6A8966A0DB134B7EBE600AC",
    "MSG/JP/strdata.bin": "6E7DD096A999299C43A9A23D9E99F75C81D6A9C8116488EC541A43423871B933",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    "MSG_PK/JP/msgdata.bin": "73CF194E4EF81C20692A245DAC75C3B2A9FCF1A997B7F6755D89DBB59149F2ED",
    "MSG_PK/JP/msgev.bin": "CE1A61E6C0F85A3E7F0FD4C1DD1BF0349A99CC134A9D73B7DE1917DB6646A0C3",
    PK_MSGGAME: "9EB0FD80E7A6D50BC2A6073FDBF213E7BDB685D81DFCD9191C9C86E415D7EFCC",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}
TARGET_SHA256 = {
    **INPUT_SHA256,
    BASE_MSGGAME: "C00B78165B06A5A9D2BFBE134E847E4B00EC3E5243EE9A1981BA1BB68CFA79C6",
    PK_MSGGAME: "7D7826A575E4BA80FEE1E4FE920CBD7E16A48F0DA529D06514EDB59B11422FBC",
}
INPUT_PACKED_SIZES = {BASE_MSGGAME: 1_504_659, PK_MSGGAME: 1_806_759}
TARGET_PACKED_SIZES = {BASE_MSGGAME: 1_504_671, PK_MSGGAME: 1_806_771}

# Only PC resources are read for semantic anchoring.  These are never inputs
# to the Korean candidate reconstruction itself.
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


def _u(value: str) -> str:
    """Decode ASCII Unicode escapes without terminal-code-page dependence."""

    return value.encode("ascii").decode("unicode_escape")


@dataclass(frozen=True)
class RecordSpec:
    """Whole-record anchor plus opaque-layout and command invariants."""

    sha256: str
    size: int
    opaque_spans_hex: tuple[str, ...]
    morphology_commands_hex: tuple[str, ...] = ()


@dataclass(frozen=True)
class Family:
    name: str
    base_coordinate: tuple[int, int]
    pk_coordinate: tuple[int, int]
    sources: Mapping[str, RecordSpec]
    rationale: str


@dataclass(frozen=True)
class Change:
    family: str
    resource: str
    coordinate: tuple[int, int]
    current: RecordSpec
    target_literals: tuple[str, ...]
    target_record_sha256: str
    target_record_size: int
    target_line_upper_bounds_px: tuple[int, ...]
    edit_kind: str = "static_0143_removal"
    target_font_widths_px: tuple[int, ...] | None = None

    @property
    def coordinate_text(self) -> str:
        return f"{self.coordinate[0]}:{self.coordinate[1]}"


def spec(
    sha256: str,
    size: int,
    opaque_spans_hex: tuple[str, ...],
    morphology_commands_hex: tuple[str, ...] = (),
) -> RecordSpec:
    return RecordSpec(sha256, size, opaque_spans_hex, morphology_commands_hex)


# Full PC JP/EN/SC/TC source literals are written to audit.v1.json only after
# these whole-record anchors pass.  A record hash pins the exact literal tuple
# more strongly than a separate loose text check.
FAMILIES = (
    Family(
        "court_talks_suspended",
        (6, 4224),
        (6, 4254),
        {
            "BASE_JP": spec(
                "346E52363402C58904DA08DAD5668574322E065A2E36C1D728E68AB2A5DEFFD5",
                41,
                ("", "014314020000050505"),
                ("014314020000",),
            ),
            "PK_JP": spec(
                "E0EF62B929746AE9369EAECEB3A1B0B55EDC00AE159E12721EDBBDB707D35C52",
                41,
                ("", "01431A020000050505"),
                ("01431A020000",),
            ),
            "EN": spec(
                "82BF3302F28892CA52596991F14121CEDC2A4537303EC86429F9E4BD96EAB1E6",
                103,
                ("", "050505"),
            ),
            "SC": spec(
                "CBEF00C1A958F069131DBEFFC2F75F204F62C8F4652ECA872405535CF43C28FF",
                29,
                ("", "050505"),
            ),
            "TC": spec(
                "16B1D307D61925E5BFCE438929129B003AAB1194DE42EBBF65F264C4C5F27575",
                27,
                ("", "050505"),
            ),
        },
        "The report says that talks with the Imperial Court were suspended.",
    ),
    Family(
        "clan_service_pledge",
        (6, 4446),
        (6, 4505),
        {
            "BASE_JP": spec(
                "DC1490603CD089285D9C33B9F3E2C6B91738490C03DEB6BC37BFC3B5D6A1FD5A",
                61,
                ("", "01435A040000050505"),
                ("01435A040000",),
            ),
            "PK_JP": spec(
                "33F13AD266D15EF23A92F1D6CA5832812569AFE49182E83A96E5E62668BC8DF1",
                61,
                ("", "014366040000050505"),
                ("014366040000",),
            ),
            "EN": spec(
                "7CD948E6D05830910D882006D3EF9055A4C6FED4C9B8CEA752CCB2A6310D7338",
                199,
                ("", "050505"),
            ),
            "SC": spec(
                "B77E8D798EA710E6F19007F1239D08C018E7180A3D75C7C5BC81555178F25BF8",
                61,
                ("", "050505"),
            ),
            "TC": spec(
                "4FB7C4436FC1843B1964EB6E1D7203B68BFDC913750F40F5CBB51F2664BDC703",
                71,
                ("", "050505"),
            ),
        },
        "The speaker vows to serve with complete devotion despite short service.",
    ),
    Family(
        "village_reconstruction",
        (8, 1043),
        (8, 1055),
        {
            "BASE_JP": spec(
                "ED21EABDE922FDB26A0A4608572505E6D7E65C1BF3003B1BC427C7CC09AE2CA0",
                83,
                ("", "014314020000", "0143140200000143FC010000050505"),
                ("014314020000", "014314020000", "0143FC010000"),
            ),
            "PK_JP": spec(
                "4BC6DBD2BB394D123FA9998FD7752F7F06549FE7F5C2BC27EB8C07B9AEF7DC90",
                83,
                ("", "01431A020000", "01431A020000014302020000050505"),
                ("01431A020000", "01431A020000", "014302020000"),
            ),
            "EN": spec(
                "8E918CB3A9C53BA58D206EEA7DB606A7DEF9E0E3A5C2FEC037128CA4B79C46C2",
                235,
                ("", "050505"),
            ),
            "SC": spec(
                "816AA6298989CA732E1C1562B322FFAACC8EC463F1AEE20F546DB69E496EEBED",
                53,
                ("", "050505"),
            ),
            "TC": spec(
                "700C0FE49DCEA7171D6E5D1514870D52DA63A81C1EFAA6423D41CE47D265AE90",
                59,
                ("", "050505"),
            ),
        },
        "Both reconstruction support and the residents' gratitude are complete statements.",
    ),
    Family(
        "ronin_recruitment",
        (15, 1523),
        (15, 1538),
        {
            "BASE_JP": spec(
                "D9D8EB60038B728932D2086898B2BCE5E79EACDEC6DD8F282C493B5F4CAE8D4B",
                79,
                ("", "0143F8020000050505"),
                ("0143F8020000",),
            ),
            "PK_JP": spec(
                "269D5573796E0D2CB397A644DDC15E8BEB564B096DB20B9C1526B5196C993F16",
                79,
                ("", "014304030000050505"),
                ("014304030000",),
            ),
            "EN": spec(
                "2429DC5CBB5B2188B411DCF641A368AAA3E6534A1CE3A791C16E151910FFFFD2",
                225,
                ("", "050505"),
            ),
            "SC": spec(
                "F416F9A3E5CA0733FC846854D0CF3D003DE39240738A4913C4865745F15EEE90",
                71,
                ("", "050505"),
            ),
            "TC": spec(
                "0CE7763C27F40445370D58A9761895D2B7104F5E68AE76023254A044F652B53A",
                71,
                ("", "050505"),
            ),
        },
        "The recruitment attempt produced no result, so the Korean report must close.",
    ),
    Family(
        "final_stratagem",
        (15, 2202),
        (15, 2232),
        {
            "BASE_JP": spec(
                "35E0F6B4E949AE512F31422373F143B1425C7A096029A51DBDF33A6E603E2190",
                63,
                ("", "01437E040000050505"),
                ("01437E040000",),
            ),
            "PK_JP": spec(
                "758FDE67652D16FFA500542ED3796DB45224CF6CE366C88B519371B2D073C37E",
                63,
                ("", "01438A040000050505"),
                ("01438A040000",),
            ),
            "EN": spec(
                "96FEE1C5BB6F0E2A09A46A2352C4D5E5261778CC409DDEB3A368391738A21BF6",
                129,
                ("", "050505"),
            ),
            "SC": spec(
                "CE1BF6A296CEECA22BA0A0C811B27A053B4D386BEA166A2A4A06884670C280BD",
                55,
                ("", "050505"),
            ),
            "TC": spec(
                "0B92D93133D53E73DF8CB385482E50892FA19FA4C3A0C2F3CD94935D8D0B664D",
                63,
                ("", "050505"),
            ),
        },
        "The pledge is to use every available stratagem to fulfill the mission.",
    ),
    Family(
        "retainer_opportunity_counterpart",
        (2, 489),
        (2, 503),
        {
            "BASE_JP": spec(
                "31F2A7FD9D3E3204E1FB129AB79AE091A6C363D9C3493BBDF6A0DEC08D7662DA",
                61,
                ("", "01431E040000", "050505"),
                ("01431E040000",),
            ),
            "PK_JP": spec(
                "771B591F678D220E8337CD6A32617642D4EB375072867F6CEBD652AFFC1F3A13",
                61,
                ("", "01432A040000", "050505"),
                ("01432A040000",),
            ),
            "EN": spec(
                "EC727F1B7F30511619A68F74C828226638DC70F3D500CF30EC2EA6C5E50F81AA",
                165,
                ("", "050505"),
            ),
            "SC": spec(
                "46D4835924930673C8B06B417E982DC81A42B9DFB74DDBFDCEFEE2D62FC19B95",
                45,
                ("", "050505"),
            ),
            "TC": spec(
                "7D7BBEBEFFEB69AFA85D4529000F087ADB8175DF7FED207929CC0356CAA7108F",
                43,
                ("", "050505"),
            ),
        },
        "The retainers receive an opportunity, so the Korean verb is give rather than bestow.",
    ),
    Family(
        "encirclement_counterattack_counterpart",
        (2, 519),
        (2, 533),
        {
            "BASE_JP": spec(
                "1B7521434A2DBBD13A4BB037FEB390F1515CBC5912A72CF83575F34DD0A2FCE9",
                73,
                ("", "0143E0020000", "0143CC010000", "050505"),
                ("0143E0020000", "0143CC010000"),
            ),
            "PK_JP": spec(
                "4857A2E358A974BCB81CBC3E7F0E571741BFA8E59558FA094F473026CBFA53BD",
                73,
                ("", "0143EC020000", "0143D2010000", "050505"),
                ("0143EC020000", "0143D2010000"),
            ),
            "EN": spec(
                "1B276587756AA97D16443B31E5036EA2B92410A2FEDA6F5E34CF847611B9BC00",
                167,
                ("", "050505"),
            ),
            "SC": spec(
                "68BE13C68ABF3E4150578D781E0F30064D52E082E91792B81DE309C60D3C0EA8",
                51,
                ("", "050505"),
            ),
            "TC": spec(
                "67D6C62D736D1621C7031C10FDF95FDD5CFB119BDD302E073889D1CE8041E521",
                51,
                ("", "050505"),
            ),
        },
        "The encircling troops are the subject, so the Korean requires the subject marker.",
    ),
)
FAMILY_BY_NAME = {family.name: family for family in FAMILIES}
if len(FAMILY_BY_NAME) != len(FAMILIES):
    raise RuntimeError("duplicate Wave 19 family")


def paired_changes(
    family_name: str,
    base_current: RecordSpec,
    pk_current: RecordSpec,
    target_literals: tuple[str, ...],
    target_record_sha256: str,
    target_record_size: int,
    target_line_upper_bounds_px: tuple[int, ...],
) -> tuple[Change, Change]:
    family = FAMILY_BY_NAME[family_name]
    return (
        Change(
            family_name,
            BASE_MSGGAME,
            family.base_coordinate,
            base_current,
            target_literals,
            target_record_sha256,
            target_record_size,
            target_line_upper_bounds_px,
        ),
        Change(
            family_name,
            PK_MSGGAME,
            family.pk_coordinate,
            pk_current,
            target_literals,
            target_record_sha256,
            target_record_size,
            target_line_upper_bounds_px,
        ),
    )


CHANGES = (
    *paired_changes(
        "court_talks_suspended",
        spec(
            "AB42671C2996A8FDA23D810E59946E55464F495556987C7F11FF7BD14BD9DEE8",
            43,
            ("", "014314020000050505"),
            ("014314020000",),
        ),
        spec(
            "7087FC2CFE2B20E73D7619072D441ED377ADE69B7D86BE33070C403B95ADC8CB",
            43,
            ("", "01431A020000050505"),
            ("01431A020000",),
        ),
        (_u(r"\uc870\uc815\uc5d0 \ub300\ud55c \uad50\uc12d\uc744\n\uc911\ub2e8\ud588\uc2b5\ub2c8\ub2e4."),),
        "FB345532D044A81210117DF0E1B3932F9EFE3553A2DAD9D75D71364F30BB892F",
        45,
        (432, 336),
    ),
    *paired_changes(
        "clan_service_pledge",
        spec(
            "04E52F33109A3C3A4D3A5C5AB089C3880AAC6CD2740160FB12D6DB0A6F223E48",
            79,
            ("", "01435A040000050505"),
            ("01435A040000",),
        ),
        spec(
            "8256823A797EF95662D65F90A2705A3BC91AA2CDA4A4A21B5EC9B058E446483D",
            79,
            ("", "014366040000050505"),
            ("014366040000",),
        ),
        (
            _u(
                r"\ub2f9\uac00\ub97c \uc12c\uae34 \uc9c0 \uc5bc\ub9c8 \uc548 \ub41c \ubab8\uc774\ub098\n"
                r"\ubd84\uace8\uc1c4\uc2e0\ud558\uc5ec \uc77c\uc5d0 \uc784\ud558\uaca0\uc2b5\ub2c8\ub2e4."
            ),
        ),
        "E5A7C651C1486804BEF5413773CA6EF4C7985BDDF9E34784760D69A6C1EE8908",
        83,
        (768, 768),
    ),
    *paired_changes(
        "village_reconstruction",
        spec(
            "72F472F1720C4B65A51ADE97BF00324834161ABB0B41522D48F62B04209B0F43",
            105,
            ("", "014314020000", "0143140200000143FC010000050505"),
            ("014314020000", "014314020000", "0143FC010000"),
        ),
        spec(
            "F207FB52890F9029C1C73B25ED7C5B3C8178A3BC7C4A838694F281090AAF78BF",
            105,
            ("", "01431A020000", "01431A020000014302020000050505"),
            ("01431A020000", "01431A020000", "014302020000"),
        ),
        (
            _u(
                r"\uc2f8\uc6c0\uc73c\ub85c \ud669\ud3d0\ud574\uc9c4 \ub9c8\uc744\uc758\n"
                r"\ubd80\ud765\uc744 \uc9c0\uc6d0\ud588\uc2b5\ub2c8\ub2e4."
            ),
            _u(r"\n\ubc31\uc131\ub4e4\ub3c4 \ubb34\ucc99 \uac10\uc0ac\ud558\uace0 \uc788\uc2b5\ub2c8\ub2e4."),
        ),
        "558C5F6242EDADF8BAE54EFC81AD162536686AFC1915F5F3860710A9DC1B164E",
        103,
        (576, 504, 792),
    ),
    *paired_changes(
        "ronin_recruitment",
        spec(
            "AA2FFB4960FD6E0374371580AB013A624020909BAFBD9C11007A63747105B7E0",
            97,
            ("", "0143F8020000050505"),
            ("0143F8020000",),
        ),
        spec(
            "99F7BF2238A162604FA1B28B3E459AE821E43BB50B1FF682893251D5EEFDD2DC",
            97,
            ("", "014304030000050505"),
            ("014304030000",),
        ),
        (
            _u(
                r"\uc131\ud558\uc758 \ub0ad\uc778\uc5d0\uac8c \ub4f1\uc6a9\uc744 \uad8c\ud588\uc73c\ub098\n"
                r"\uc81c \ud798\uc774 \ubbf8\uce58\uc9c0 \ubabb\ud558\uc5ec\u2026\n"
                r"\uc131\uacfc\ub294 \uc5bb\uc9c0 \ubabb\ud588\uc2b5\ub2c8\ub2e4."
            ),
        ),
        "76FD8A5E039E1347E43B0F87BB42A063B7B2EBFF245EB711F811289F69AD1BE6",
        99,
        (744, 552, 576),
    ),
    *paired_changes(
        "final_stratagem",
        spec(
            "F21167DA2D3BF35052B49B121610B702CE7B48E53DCE77B5AD06B07A1E40B5EB",
            75,
            ("", "01437E040000050505"),
            ("01437E040000",),
        ),
        spec(
            "448824C273CB575867042C80313EB8118EA791610EDEE96F71EA6B02620CE098",
            75,
            ("", "01438A040000050505"),
            ("01438A040000",),
        ),
        (
            _u(
                r"\ubbf8\uc57d\ud55c \uc774 \ubab8\uc758 \ubaa9\uc228\uc744 \uac78\uace0\n"
                r"\uac00\uc9c4 \uacc4\ucc45\uc744 \ubaa8\ub450 \ub3d9\uc6d0\ud558\uaca0\uc2b5\ub2c8\ub2e4."
            ),
        ),
        "3626FAC6701220890456B577261D2F276CDB177D57CF3F27AFE5F343A16F47C0",
        77,
        (624, 792),
    ),
    Change(
        "retainer_opportunity_counterpart",
        PK_MSGGAME,
        (2, 503),
        spec(
            "695E6F265001FD6A1B945504D775EF8621D592B669539854297B649A16706C54",
            71,
            ("", "", "050505"),
        ),
        (
            _u(
                r"\ud718\ud558\uac00 \ub420 \uc7a5\uc218\ub4e4\uc5d0\uac8c\n"
                r"\ud65c\uc57d\uc758 \uc7a5\uc744 \ub9c8\uc74c\uaecf "
            ),
            _u(r"\uc8fc\uaca0\ub2e4!"),
        ),
        "BC4E56D7BF2495988E1122FDB775EBE1CFA975A7356C9F16EFF9DFE6EAA1B0FA",
        69,
        (480, 648),
        "literal_only_counterpart",
        (480, 624),
    ),
    Change(
        "encirclement_counterattack_counterpart",
        PK_MSGGAME,
        (2, 533),
        spec(
            "40FD363013EE0303696156FD03F9580B01FF78201EA9D6944924C3D964156AA2",
            85,
            ("", "", "", "050505"),
        ),
        (
            _u(r"\ud3ec\uc704\ubcd1\ub4e4\uc774 \ub9c8\uc74c\ub300\ub85c \ud558\uac8c \ub450\uc9c0 "),
            _u(r"\uc54a\uaca0\ub2e4.\n\uc774\ucabd\uc5d0\uc11c\ub3c4 "),
            _u(r"\ubc18\uaca9\ud558\uaca0\ub2e4!"),
        ),
        "2441FC7CBB34E16E7417A2A2F4BF014B333B267F48F15B2A2F76BBB1972A2AE9",
        89,
        (912, 552),
        "literal_only_counterpart",
        (888, 528),
    ),
)
CHANGE_BY_KEY = {(change.resource, change.coordinate): change for change in CHANGES}
if len(CHANGE_BY_KEY) != len(CHANGES):
    raise RuntimeError("duplicate Wave 19 target coordinate")


class Wave19Error(ValueError):
    """A strict profile, anchor, byte-preservation, or tmp-output guard failed."""


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
                    raise Wave19Error("truncated 01 43 command")
                commands.append(span[offset : offset + 6].hex().upper())
                offset += 6
            else:
                offset += 1
    return tuple(commands)


def stripped_opaque_spans(record: MsgGameRecord) -> tuple[bytes, ...]:
    output_spans: list[bytes] = []
    for span in opaque_spans(record):
        output = bytearray()
        offset = 0
        while offset < len(span):
            if span[offset : offset + 2] == MORPHOLOGY_PREFIX:
                if offset + 6 > len(span):
                    raise Wave19Error("truncated 01 43 command")
                offset += 6
            else:
                output.append(span[offset])
                offset += 1
        output_spans.append(bytes(output))
    return tuple(output_spans)


def output_opaque_spans(target_literals: tuple[str, ...]) -> tuple[bytes, ...]:
    return tuple(b"" for _ in target_literals) + (RECORD_TERMINATOR,)


def profile_hashes(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for relative in PROFILE_PATHS:
        path = root / relative
        if not path.is_file():
            raise Wave19Error(f"profile resource is absent: {relative}")
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
        raise Wave19Error(f"{label} profile mismatch: {json.dumps(mismatch, sort_keys=True)}")


def validate_raw_roundtrip(packed: bytes, label: str) -> None:
    header, raw = decompress_wrapper(packed)
    archive = parse_packed_msggame(packed).archive
    if rebuild_raw_msggame(archive) != raw:
        raise Wave19Error(f"{label} raw parse/rebuild differs")
    repacked = recompress_wrapper(raw, header)
    _repacked_header, roundtrip_raw = decompress_wrapper(repacked)
    if roundtrip_raw != raw:
        raise Wave19Error(f"{label} LZ4 round-trip differs")


def reject_switch_path(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    if any("switch" in part.casefold() for part in resolved.parts):
        raise Wave19Error(f"Switch input is forbidden: {label}")
    return resolved


def assert_record_spec(record: MsgGameRecord, expected: RecordSpec, label: str) -> None:
    spans = tuple(value.hex().upper() for value in opaque_spans(record))
    if (
        sha256_bytes(record.data) != expected.sha256
        or len(record.data) != expected.size
        or spans != expected.opaque_spans_hex
        or morphology_commands(record) != expected.morphology_commands_hex
    ):
        raise Wave19Error(f"{label} record invariant differs")


def record_report(record: MsgGameRecord, expected: RecordSpec) -> dict[str, Any]:
    return {
        "record_sha256": expected.sha256,
        "record_size": expected.size,
        "literals": list(literal_texts(record)),
        "opaque_spans_hex": list(expected.opaque_spans_hex),
        "morphology_commands_hex": list(expected.morphology_commands_hex),
    }


def load_references(
) -> tuple[
    dict[str, dict[tuple[int, int], MsgGameRecord]],
    dict[str, dict[tuple[int, int], MsgGameRecord]],
]:
    jp: dict[str, dict[tuple[int, int], MsgGameRecord]] = {}
    for resource, (path, expected_hash) in PC_JP_SOURCES.items():
        checked = reject_switch_path(path, f"PC JP {resource}")
        if sha256_path(checked) != expected_hash:
            raise Wave19Error(f"pristine PC JP source hash differs: {resource}")
        jp[resource] = records_by_coordinate(checked.read_bytes())

    contexts: dict[str, dict[tuple[int, int], MsgGameRecord]] = {}
    for language, (relative, expected_hash) in PK_CONTEXTS.items():
        path = reject_switch_path(DEFAULT_STEAM_ROOT / relative, f"PC PK {language}")
        if sha256_path(path) != expected_hash:
            raise Wave19Error(f"PC PK {language} context hash differs")
        contexts[language] = records_by_coordinate(path.read_bytes())
    return jp, contexts


def validate_family_anchors(
    jp: Mapping[str, Mapping[tuple[int, int], MsgGameRecord]],
    contexts: Mapping[str, Mapping[tuple[int, int], MsgGameRecord]],
) -> None:
    for family in FAMILIES:
        base = jp[BASE_MSGGAME].get(family.base_coordinate)
        pk = jp[PK_MSGGAME].get(family.pk_coordinate)
        if base is None or pk is None:
            raise Wave19Error(f"PC JP anchor is absent: {family.name}")
        assert_record_spec(base, family.sources["BASE_JP"], f"{family.name} Base JP")
        assert_record_spec(pk, family.sources["PK_JP"], f"{family.name} PK JP")
        if literal_texts(base) != literal_texts(pk):
            raise Wave19Error(f"Base/PK JP literal tuple differs: {family.name}")
        for language in PK_CONTEXTS:
            record = contexts[language].get(family.pk_coordinate)
            if record is None:
                raise Wave19Error(f"PC PK {language} anchor is absent: {family.name}")
            assert_record_spec(
                record,
                family.sources[language],
                f"{family.name} PK {language}",
            )


def validate_text(value: str, label: str) -> None:
    if not value or "\x1b" in value or "%" in value:
        raise Wave19Error(f"{label} contains a runtime marker or is empty")
    encoded = value.encode("utf-16-le")
    if LITERAL_START in encoded or LITERAL_END in encoded:
        raise Wave19Error(f"{label} encodes a reserved marker")
    for character in value:
        if character != "\n" and unicodedata.category(character) == "Cc":
            raise Wave19Error(f"{label} contains control U+{ord(character):04X}")


def line_upper_bound_px(target_literals: tuple[str, ...]) -> tuple[int, ...]:
    return tuple(
        sum(24 if character == " " else 48 for character in line)
        for line in "".join(target_literals).split("\n")
    )


def _font_u32(raw: bytes, offset: int, label: str) -> int:
    if offset < 0 or offset + 4 > len(raw):
        raise Wave19Error(f"font {label} is outside the G1N payload")
    return struct.unpack_from("<I", raw, offset)[0]


@functools.lru_cache(maxsize=1)
def font_metric_state() -> tuple[bytes, tuple[int, ...], int, int]:
    """Read active PC font metrics in memory; no temporary file is created."""

    path = reject_switch_path(FONT_RESOURCE, "active PC JP font")
    if sha256_path(path) != FONT_SHA256:
        raise Wave19Error("active PC JP font hash differs")
    try:
        archive = parse_link(path.read_bytes())
        _header, raw = decompress_wrapper(archive.entries[FONT_OUTER_ENTRY].data)
    except (IndexError, ValueError) as exc:
        raise Wave19Error("active PC JP font entry cannot be decoded") from exc
    if raw[:8] != b"_N1G0000":
        raise Wave19Error("active PC JP font G1N magic differs")
    if _font_u32(raw, 0x08, "declared size") != len(raw):
        raise Wave19Error("active PC JP font declared size differs")
    table_count = _font_u32(raw, 0x1C, "table count")
    if not 1 <= table_count <= 32 or FONT_TABLE >= table_count:
        raise Wave19Error("active PC JP font table count differs")
    offsets = tuple(
        _font_u32(raw, 0x20 + 4 * index, f"table {index} offset")
        for index in range(table_count)
    )
    atlas_offset = _font_u32(raw, 0x14, "atlas offset")
    if offsets != tuple(sorted(offsets)) or len(set(offsets)) != len(offsets):
        raise Wave19Error("active PC JP font table offsets differ")
    table_offset = offsets[FONT_TABLE]
    table_end = offsets[FONT_TABLE + 1] if FONT_TABLE + 1 < table_count else atlas_offset
    record_start = table_offset + FONT_MAP_BYTES
    if not 0 <= table_offset <= record_start <= table_end <= len(raw):
        raise Wave19Error("active PC JP font table bounds differ")
    record_bytes = table_end - record_start
    if record_bytes % FONT_RECORD_BYTES:
        raise Wave19Error("active PC JP font record alignment differs")
    record_count = record_bytes // FONT_RECORD_BYTES
    if record_count <= 0:
        raise Wave19Error("active PC JP font has no records")
    mapping = struct.unpack_from("<65536H", raw, table_offset)
    return raw, mapping, record_start, record_count


def font_advance_px(character: str) -> int:
    if len(character) != 1 or ord(character) > 0xFFFF:
        raise Wave19Error("font metric requires one BMP character")
    raw, mapping, record_start, record_count = font_metric_state()
    ordinal = mapping[ord(character)]
    if ordinal == 0:
        if WIDE_SCRIPT_RE.fullmatch(character):
            return 48
        raise Wave19Error(f"active PC JP font lacks U+{ord(character):04X}")
    if ordinal >= record_count:
        raise Wave19Error(f"active PC JP font ordinal is invalid for U+{ord(character):04X}")
    offset = record_start + ordinal * FONT_RECORD_BYTES
    width = raw[offset]
    advance = raw[offset + 4]
    if width != advance or advance not in (24, 48):
        raise Wave19Error(f"active PC JP glyph metric differs for U+{ord(character):04X}")
    return advance


def font_line_widths_px(target_literals: tuple[str, ...]) -> tuple[int, ...]:
    widths: list[int] = []
    for line in "".join(target_literals).split("\n"):
        width = 0
        for character in line:
            if unicodedata.category(character) == "Cc":
                raise Wave19Error(f"font layout has control U+{ord(character):04X}")
            width += font_advance_px(character)
        widths.append(width)
    return tuple(widths)


def rebuild_static_record(target_literals: tuple[str, ...]) -> bytes:
    payload = bytearray()
    for text in target_literals:
        payload.extend(LITERAL_START)
        payload.extend(text.encode("utf-16-le"))
        payload.extend(LITERAL_END)
    payload.extend(RECORD_TERMINATOR)
    return bytes(payload)


def validate_change(
    change: Change,
    current: Mapping[tuple[int, int], MsgGameRecord],
) -> tuple[bytes, dict[str, Any]]:
    family = FAMILY_BY_NAME.get(change.family)
    if family is None:
        raise Wave19Error(f"unknown family: {change.family}")
    expected_coordinate = (
        family.base_coordinate if change.resource == BASE_MSGGAME else family.pk_coordinate
    )
    if change.coordinate != expected_coordinate:
        raise Wave19Error(f"family coordinate mismatch: {change.resource} {change.coordinate_text}")

    record = current.get(change.coordinate)
    if record is None:
        raise Wave19Error(f"missing input record: {change.resource} {change.coordinate_text}")
    assert_record_spec(record, change.current, f"input {change.resource} {change.coordinate_text}")
    current_literals = literal_texts(record)
    expected_output_spans = output_opaque_spans(change.target_literals)
    if stripped_opaque_spans(record) != expected_output_spans:
        raise Wave19Error(
            f"non-morphology opaque bytes found: {change.resource} {change.coordinate_text}"
        )
    if change.edit_kind not in {"static_0143_removal", "literal_only_counterpart"}:
        raise Wave19Error(f"unknown edit kind: {change.edit_kind}")
    if change.edit_kind == "static_0143_removal" and not change.current.morphology_commands_hex:
        raise Wave19Error(f"static repair lacks 01 43 command: {change.coordinate_text}")
    if change.edit_kind == "literal_only_counterpart" and change.current.morphology_commands_hex:
        raise Wave19Error(f"literal-only counterpart contains 01 43: {change.coordinate_text}")
    if not all(
        command.startswith("0143") and len(command) == 12
        for command in change.current.morphology_commands_hex
    ):
        raise Wave19Error(f"removal is not restricted to full 01 43 commands: {change.coordinate_text}")

    current_text = "".join(current_literals)
    target_text = "".join(change.target_literals)
    for literal_id, value in enumerate(change.target_literals):
        validate_text(value, f"{change.coordinate_text} target literal {literal_id}")
    if current_text.count("\n") != target_text.count("\n"):
        raise Wave19Error(f"manual line count changed: {change.resource} {change.coordinate_text}")
    if target_text.count("\n") + 1 > 3:
        raise Wave19Error(f"target exceeds three explicit lines: {change.resource} {change.coordinate_text}")
    actual_bounds = line_upper_bound_px(change.target_literals)
    if actual_bounds != change.target_line_upper_bounds_px:
        raise Wave19Error(f"target line-width upper bound differs: {change.resource} {change.coordinate_text}")
    if any(width > DIALOGUE_MAX_LINE_PX for width in actual_bounds):
        raise Wave19Error(f"target line exceeds limit: {change.resource} {change.coordinate_text}")
    actual_font_widths: tuple[int, ...] | None = None
    if change.target_font_widths_px is not None:
        actual_font_widths = font_line_widths_px(change.target_literals)
        if actual_font_widths != change.target_font_widths_px:
            raise Wave19Error(f"target font width differs: {change.resource} {change.coordinate_text}")
        if any(width > DIALOGUE_MAX_LINE_PX for width in actual_font_widths):
            raise Wave19Error(f"target font line exceeds limit: {change.resource} {change.coordinate_text}")

    target = rebuild_static_record(change.target_literals)
    if len(target) != change.target_record_size:
        raise Wave19Error(f"target record size differs: {change.resource} {change.coordinate_text}")
    if sha256_bytes(target) != change.target_record_sha256:
        raise Wave19Error(f"target record SHA-256 differs: {change.resource} {change.coordinate_text}")
    target_record = MsgGameRecord(
        record.block_id,
        record.record_id,
        record.relative_offset,
        target,
    )
    if (
        literal_texts(target_record) != change.target_literals
        or morphology_commands(target_record)
        or opaque_spans(target_record) != expected_output_spans
        or marker_topology(target_record) != marker_topology(record)
        or not target_record.data.endswith(RECORD_TERMINATOR)
    ):
        raise Wave19Error(f"target record reconstruction differs: {change.resource} {change.coordinate_text}")

    return target, {
        "family": change.family,
        "edit_kind": change.edit_kind,
        "resource": change.resource,
        "coordinate": change.coordinate_text,
        "input_record_sha256": change.current.sha256,
        "target_record_sha256": change.target_record_sha256,
        "input_record_size": change.current.size,
        "target_record_size": change.target_record_size,
        "current_literals": list(current_literals),
        "target_literals": list(change.target_literals),
        "literal_marker_count": len(current_literals),
        "input_opaque_spans_hex": list(change.current.opaque_spans_hex),
        "removed_opaque_commands_hex": list(change.current.morphology_commands_hex),
        "target_opaque_spans_hex": [
            value.hex().upper() for value in expected_output_spans
        ],
        "removed_0143_command_count": len(change.current.morphology_commands_hex),
        "target_has_no_0143": True,
        "terminator_hex": RECORD_TERMINATOR.hex().upper(),
        "manual_line_count": {
            "current": current_text.count("\n") + 1,
            "target": target_text.count("\n") + 1,
        },
        "line_upper_bound_px": list(actual_bounds),
        "font_line_widths_px": list(actual_font_widths) if actual_font_widths is not None else None,
        "dialogue_max_line_px": DIALOGUE_MAX_LINE_PX,
        "rationale": family.rationale,
    }


def validate_output_records(output: Mapping[str, bytes]) -> None:
    for change in CHANGES:
        record = records_by_coordinate(output[change.resource]).get(change.coordinate)
        if record is None:
            raise Wave19Error(f"candidate lacks target: {change.resource} {change.coordinate_text}")
        if (
            sha256_bytes(record.data) != change.target_record_sha256
            or literal_texts(record) != change.target_literals
            or morphology_commands(record)
            or opaque_spans(record) != output_opaque_spans(change.target_literals)
            or not record.data.endswith(RECORD_TERMINATOR)
        ):
            raise Wave19Error(f"candidate target differs: {change.resource} {change.coordinate_text}")


def require_predecessor_root(path: Path) -> Path:
    expected = PREDECESSOR_CANDIDATE_ROOT.resolve(strict=True)
    resolved = path.resolve(strict=True)
    if resolved != expected:
        raise Wave19Error(f"input must be the unique Wave 17 candidate: {expected}")
    return resolved


def prepare_candidate(
    input_root: Path = PREDECESSOR_CANDIDATE_ROOT,
) -> tuple[dict[str, bytes], dict[str, Any]]:
    """Build the twelve-record overlay in memory after all guards pass."""

    input_root = require_predecessor_root(input_root)
    assert_profile(input_root, INPUT_SHA256, "Wave 17 predecessor")
    for resource in CHANGED_PATHS:
        packed = (input_root / resource).read_bytes()
        if len(packed) != INPUT_PACKED_SIZES[resource]:
            raise Wave19Error(f"predecessor packed size differs: {resource}")
        validate_raw_roundtrip(packed, f"Wave 17 predecessor {resource}")

    jp, contexts = load_references()
    validate_family_anchors(jp, contexts)
    current = {
        resource: records_by_coordinate((input_root / resource).read_bytes())
        for resource in CHANGED_PATHS
    }
    replacements: dict[str, dict[tuple[int, int], bytes]] = {
        resource: {} for resource in CHANGED_PATHS
    }
    audit_rows: list[dict[str, Any]] = []
    for change in CHANGES:
        if change.coordinate in replacements[change.resource]:
            raise Wave19Error(f"duplicate change: {change.resource} {change.coordinate_text}")
        target, row = validate_change(change, current[change.resource])
        replacements[change.resource][change.coordinate] = target
        audit_rows.append(row)

    output: dict[str, bytes] = {}
    for resource in CHANGED_PATHS:
        before = (input_root / resource).read_bytes()
        after = rebuild_packed_msggame(before, replacements[resource])
        if len(after) != TARGET_PACKED_SIZES[resource]:
            raise Wave19Error(f"candidate packed size differs: {resource}")
        if sha256_bytes(after) != TARGET_SHA256[resource]:
            raise Wave19Error(f"candidate packed SHA-256 differs: {resource}")
        old_records = records_by_coordinate(before)
        new_records = records_by_coordinate(after)
        if old_records.keys() != new_records.keys():
            raise Wave19Error(f"record topology changed: {resource}")
        changed = {
            coordinate
            for coordinate in old_records
            if old_records[coordinate].data != new_records[coordinate].data
        }
        if changed != set(replacements[resource]):
            raise Wave19Error(f"unexpected changed record set: {resource} {sorted(changed)}")
        validate_raw_roundtrip(after, f"candidate {resource}")
        output[resource] = after
    validate_output_records(output)

    target_hashes = {
        **INPUT_SHA256,
        **{resource: sha256_bytes(data) for resource, data in output.items()},
    }
    if target_hashes != TARGET_SHA256:
        raise Wave19Error("candidate output profile is not pinned")

    family_reports: list[dict[str, Any]] = []
    for family in FAMILIES:
        base = jp[BASE_MSGGAME][family.base_coordinate]
        pk = jp[PK_MSGGAME][family.pk_coordinate]
        family_reports.append(
            {
                "name": family.name,
                "base_coordinate": f"{family.base_coordinate[0]}:{family.base_coordinate[1]}",
                "pk_coordinate": f"{family.pk_coordinate[0]}:{family.pk_coordinate[1]}",
                "pc_base_jp": record_report(base, family.sources["BASE_JP"]),
                "pc_pk_jp": record_report(pk, family.sources["PK_JP"]),
                "pc_pk_contexts": {
                    language: record_report(
                        contexts[language][family.pk_coordinate],
                        family.sources[language],
                    )
                    for language in PK_CONTEXTS
                },
                "rationale": family.rationale,
            }
        )
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "platform": "Steam PC",
            "input": "verified Wave 17 private candidate only",
            "wave17_11_file_profile_required": True,
            "pristine_pc_japanese_read": True,
            "pc_pk_en_sc_tc_context_read": True,
            "active_pc_jp_font_read": True,
            "switch_korean_read": False,
            "steam_game_resource_written": False,
            "steam_apply_capability": "absent",
            "git_operation": "absent",
            "release_operation": "absent",
        },
        "predecessor_candidate": PREDECESSOR_CANDIDATE_ROOT.relative_to(REPO).as_posix(),
        "input_sha256": INPUT_SHA256,
        "target_sha256": target_hashes,
        "pc_jp_sha256": {
            resource: expected for resource, (_path, expected) in PC_JP_SOURCES.items()
        },
        "pc_pk_context_sha256": {
            language: expected for language, (_path, expected) in PK_CONTEXTS.items()
        },
        "font": {
            "resource": "RES_JP/res_lang.bin",
            "sha256": FONT_SHA256,
            "outer_entry": FONT_OUTER_ENTRY,
            "table": FONT_TABLE,
        },
        "families": family_reports,
        "records": audit_rows,
    }
    return output, audit


def require_tmp(path: Path, label: str) -> Path:
    root = TMP_ROOT.resolve(strict=False)
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave19Error(f"{label} must stay below {root}") from exc
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
            raise Wave19Error(f"private candidate packed size differs: {resource}")
        validate_raw_roundtrip(packed, f"private candidate {resource}")
    validate_output_records(output)


def build_candidate(
    input_root: Path,
    output_root: Path,
    audit_path: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    input_root = require_predecessor_root(input_root)
    output_root = require_tmp(output_root, "candidate output")
    audit_path = require_tmp(audit_path, "audit output")
    manifest_path = require_tmp(manifest_path, "manifest output")
    if output_root.exists() or audit_path.exists() or manifest_path.exists():
        raise Wave19Error("candidate output, audit, or manifest already exists")

    output, audit = prepare_candidate(input_root)
    output_root.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.", dir=output_root.parent))
    try:
        for relative in PROFILE_PATHS:
            destination = stage / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if relative in output:
                destination.write_bytes(output[relative])
            else:
                shutil.copy2(input_root / relative, destination)
        assert_profile(stage, TARGET_SHA256, "private candidate staging")
        os.replace(stage, output_root)
        verify_private_candidate(output_root)
        audit_bytes = (
            json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        atomic_write(audit_path, audit_bytes)
        manifest = {
            "schema": SCHEMA,
            "transaction_id": "pc-dialogue-quality-wave19-static-inflection-v1",
            "candidate_only": True,
            "predecessor_candidate": PREDECESSOR_CANDIDATE_ROOT.relative_to(REPO).as_posix(),
            "profile_paths": list(PROFILE_PATHS),
            "changed_paths": list(CHANGED_PATHS),
            "coordinates": [
                f"{change.resource}:{change.coordinate_text}" for change in CHANGES
            ],
            "input_sha256": INPUT_SHA256,
            "output_sha256": TARGET_SHA256,
            "pinned_output_sha256": TARGET_SHA256,
            "audit_sha256": sha256_bytes(audit_bytes),
            "record_count": len(CHANGES),
            "steam_write_capability": "absent",
            "steam_apply_capability": "absent",
            "git_operation": "absent",
            "release_operation": "absent",
            "real_game_qa_required_before_release": True,
        }
        atomic_write(
            manifest_path,
            (
                json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
            ).encode("utf-8"),
        )
        return manifest
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    hash_parser = sub.add_parser("hash", help="verify the in-memory candidate")
    hash_parser.add_argument("--input-root", type=Path, default=PREDECESSOR_CANDIDATE_ROOT)
    verify_parser = sub.add_parser("verify-private", help="verify a private candidate")
    verify_parser.add_argument("--candidate-root", type=Path, required=True)
    build_parser = sub.add_parser("build", help="write only below this workstream tmp root")
    build_parser.add_argument("--input-root", type=Path, default=PREDECESSOR_CANDIDATE_ROOT)
    build_parser.add_argument("--output-root", type=Path, default=TMP_ROOT / "candidate")
    build_parser.add_argument("--audit-path", type=Path, default=TMP_ROOT / "audit.v1.json")
    build_parser.add_argument(
        "--manifest-path", type=Path, default=TMP_ROOT / "build_manifest.v1.json"
    )
    args = parser.parse_args(argv)
    try:
        if args.command == "hash":
            _output, audit = prepare_candidate(args.input_root)
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
            args.input_root,
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
    except (OSError, ValueError, Wave19Error) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
