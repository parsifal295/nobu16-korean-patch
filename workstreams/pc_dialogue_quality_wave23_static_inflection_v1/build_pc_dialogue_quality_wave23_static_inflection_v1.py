#!/usr/bin/env python3
"""Build the private PC-only Wave 23 static-dialogue candidate.

The only Korean input accepted by this builder is the completed Wave 22
eleven-file private candidate.  It reconstructs twenty reviewed Base/PK
dialogue families (forty records), retaining literal text verbatim for two
families while removing only complete ``01 43`` static morphology commands.
All writes are confined to this workstream's private ``tmp`` directory.
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
PREDECESSOR_ROOT = REPO / "tmp" / "pc_dialogue_quality_wave22_static_inflection_v1" / "candidate"
TOOLS = REPO / "tools"
MSGGAME_TOOLS = REPO / "workstreams" / "msggame"
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


SCHEMA = "nobu16.kr.pc-dialogue-quality-wave23-static-inflection.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave23-static-inflection-audit.v1"
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

# Wave 22 itself is the complete, unique eleven-file preimage.  These two
# evidence files prevent an arbitrary directory with matching changed files
# from being substituted as an input.
WAVE22_AUDIT_SHA256 = "44D6A376106D7A7BB7CF489C33B0E1890735157E79BBFB0952833D42D5CE45CE"
WAVE22_AUDIT_SIZE = 110_606
WAVE22_MANIFEST_SHA256 = "C70A1CE044A3EAF5645F3D42DDC52072CFC2AAB1FF14004C17B89B9CF71D3762"
WAVE22_MANIFEST_SIZE = 5_988
INPUT_SHA256 = {
    "MSG/JP/ev_strdata.bin": "BF224468BFBCF3CC71DFF4609142A60D75091813281EE6F2333645413AD81B80",
    BASE_MSGGAME: "3F24BD0767813552DE13D06076BB2D2360FF59FF6E081C886BFBC9525819B453",
    "MSG/JP/strdata.bin": "6E7DD096A999299C43A9A23D9E99F75C81D6A9C8116488EC541A43423871B933",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    "MSG_PK/JP/msgdata.bin": "73CF194E4EF81C20692A245DAC75C3B2A9FCF1A997B7F6755D89DBB59149F2ED",
    "MSG_PK/JP/msgev.bin": "D922E7C2B0BD4078A5DB14C87973ECB7BB1A62A4CA2EA30A03A231AB40C1E86B",
    PK_MSGGAME: "C7B879D9C88748D7BF9DDA4B9B492C1CE6F9ABC452C6A490B4E593CC5A4E302D",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}
INPUT_SIZES = {
    "MSG/JP/ev_strdata.bin": 928_123,
    BASE_MSGGAME: 1_504_711,
    "MSG/JP/strdata.bin": 957_204,
    "MSG_PK/JP/msgbre.bin": 484_068,
    "MSG_PK/JP/msgdata.bin": 496_995,
    "MSG_PK/JP/msgev.bin": 994_727,
    PK_MSGGAME: 1_806_815,
    "MSG_PK/JP/msgire.bin": 23_128,
    "MSG_PK/JP/msgstf.bin": 17_341,
    "MSG_PK/JP/msgstf_ce.bin": 18_767,
    "MSG_PK/JP/msgui.bin": 122_733,
}
TARGET_SHA256 = {
    **INPUT_SHA256,
    BASE_MSGGAME: "A5B688C4DF72F9796759A13FBEDB30C30C47873DF9228B9566127877AFD5F810",
    PK_MSGGAME: "432B4F9D3DEF80DDF8288AE82AB1A245EE44585776FC368658A47CBBD826EB8B",
}
TARGET_SIZES = {
    **INPUT_SIZES,
    BASE_MSGGAME: 1_504_691,
    PK_MSGGAME: 1_806_795,
}

PC_REFERENCE_PATHS = {
    "BASE_JP": (
        Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin"),
        "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
    ),
    "PK_JP": (
        DEFAULT_STEAM_ROOT / "KR_PATCH_BACKUP/file_only_transaction/steam-jp-1.1.7-v0.6.0/originals/MSG_PK/JP/msggame.bin",
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


class Wave23Error(ValueError):
    """A pinned input, anchor, byte-preservation, or tmp guard failed."""


@dataclass(frozen=True)
class RecordSpec:
    sha256: str
    size: int


@dataclass(frozen=True)
class Family:
    name: str
    base_coordinate: tuple[int, int]
    pk_coordinate: tuple[int, int]
    target_literals: tuple[str, ...]
    target_font_widths_px: tuple[int, ...]
    base_preimage: RecordSpec
    pk_preimage: RecordSpec
    base_jp: RecordSpec
    pk_jp: RecordSpec
    en: RecordSpec
    sc: RecordSpec
    tc: RecordSpec
    target: RecordSpec
    rationale: str
    retain_literal_text: bool = False


def spec(sha256: str, size: int) -> RecordSpec:
    return RecordSpec(sha256, size)


def _ko(value: str) -> str:
    """Keep target source ASCII-only and robust to Windows console code pages."""

    return value.encode("ascii").decode("unicode_escape")


def literals(*values: str) -> tuple[str, ...]:
    return tuple(_ko(value) for value in values)


# Every source and target record is pinned by whole-record SHA-256 plus size.
# Context anchors use the matching PK coordinate for EN/SC/TC.  The two
# retain_* families deliberately keep their Korean UTF-16 literal payloads
# byte-identical while stripping only the complete static 01 43 command.
FAMILIES = (
    Family(
        "bandit_suppression", (8, 1045), (8, 1057),
        literals(r"\uc2f8\uc6c0\uc5d0 \ud718\ub9d0\ub9b0 \ub9c8\uc744\ub85c \uac00\uc11c\n\ub3c4\uc801\uc744 \ud1a0\ubc8c\ud558\uace0 \uc654\uc2b5\ub2c8\ub2e4.", r"\n\uc774\ub85c\uc368 \ubc31\uc131\ub3c4 \ud3b8\ud788 \uc0b4 \uc218 \uc788\uc2b5\ub2c8\ub2e4."), (600, 600, 816),
        spec("AE5DACFC80B9EB2D8300A79C647B01DB8DAA48B997701D23D99A34A74914163D", 123), spec("8D1DFEB5070A7B65F2208FAA41107BC5E7E35B1FF914AF2B7C3EE13D5ADD2BF0", 123),
        spec("CDC4D6DA93059653ADD857FFC2CB077C69BEF77C08C73859C31476DD522E8AED", 103), spec("30D2C3B299B48E76E2A49310C859661FCE0CFABD15105A6EEC4F3EEA529D1620", 103),
        spec("6E9977D6FC0DF3BEC0127E1F844FF2DD595461603C2C95E4C1A48086EE129B86", 253), spec("3E79DB5D7D798C007F7557B402BBA8471CE0EB79C8E42ABE368CF532E6C98314", 69), spec("2CE06C39A7FAD749C95E40ED2C082FDDF4E3F9332C958CBA9AE699A313410B96", 63),
        spec("D989507A8471193514ECE31698515E6ABB1F0AB1290D66E5882C8954342ABC44", 115), "Bandit suppression report and its civilian benefit are complete statements.",
    ),
    Family(
        "road_repair", (8, 1052), (8, 1064),
        literals(r"\uc794\ud574\ub97c \uce58\uc6b0\uace0 \uac00\ub3c4\ub97c\n\uc815\ube44\ud588\uc2b5\ub2c8\ub2e4.", r"\n\uc774\ub85c\uc368 \uc0ac\ub78c\uc758 \uc655\ub798\ub3c4 \ub298\uc5b4\ub0a0 \uac83\uc785\ub2c8\ub2e4."), (480, 312, 888),
        spec("F4F490335A12AF2ADAD402C16D736CE72DCFBC251D213EA519CEAEE50546328E", 101), spec("45C2AD8D4AE446C80636CA68ACB5505D02979213B35E46129785411AF6FF3065", 101),
        spec("6493B2FF9F2D310E3FDCB416888D263C2730EB53E60E518448CA239977AD88B4", 87), spec("73EF0E7221B05FAA30F78083D7ADF76F4A2F9E38366502D52398EA5D7DE93594", 87),
        spec("24AF94CC13CA67365420B7C6FDED8740D9B67E5AABAC21259E1D270397DFAE96", 207), spec("50DB0C300FF8218759EC1EB7E839673E450D0C86E3CD5C208E57C79F7B6D7DE8", 61), spec("72842E42C1B0E11CFDA3BB4E8AFDCB373994551334ED109FED694DFF8185F5E0", 63),
        spec("5BA9E1729DFC88D401501766E242AB0AA4330AC5A252FE9ADF38D6EB7B2AB4DE", 97), "Road repair and restored traffic form the intended report.",
    ),
    Family(
        "persuade_people", (8, 1060), (8, 1072),
        literals(r"\ubc31\uc131\uc744 \uc124\ub4dd\ud588\uc2b5\ub2c8\ub2e4.", r"\n\uc5b4\ub824\uc6b4 \uc77c\uc77c\uc218\ub85d \ubaa8\ub450 \ud798\uc744 \ud569\uccd0\n\ud568\uaed8 \ud5e4\uccd0\ub098\uac00\uc57c \ud569\ub2c8\ub2e4."), (480, 720, 552),
        spec("84766355C465E89E78F5073858776CC3FA9B99E2F7F8E985B3C1FDF6208F7478", 101), spec("A521513823CF65CB42B95860091252A02AD7A944F19C448D68C63E9D2EEFA1D5", 101),
        spec("FDAE4C9FECAB3DC625890B809DAEDCE2808627C5BE794E2925A1953313F73D0C", 85), spec("43AE455B0189E61241849528D52878A8DB954B0D8763CB8AF90D3871CC923CBF", 85),
        spec("53CA6DE9DB204C971EE33F307BB822B9AFC11725217E2EB141898D45ECFF60B4", 189), spec("CCB6A7B5DC762D5441B5ED3635312430551F694A37E195BCD7B723F8AD397CE4", 71), spec("5350EECE79EB949149FB51DCE3DA2F061D21731BE74490D72B0E292AD5C82742", 71),
        spec("18C2A93E6CF914F62587961369992942EEF3F6C2E57A678D1B73B1DA0458F23F", 101), "The report first states persuasion, then its cooperative lesson.",
    ),
    Family(
        "apology_and_peace", (8, 1067), (8, 1079),
        literals(r"\uc0c1\ub300\uc5d0\uac8c \uc0ac\uc8c4\ud558\uace0 \uc654\uc2b5\ub2c8\ub2e4.", r"\n\ubc31\uc131\uc758 \uc0dd\ud65c\uc744 \uc704\ud611\ud558\uc9c0 \uc54a\ub3c4\ub85d\n\uc4f8\ub370\uc5c6\ub294 \uc2f8\uc6c0\uc740 \ud53c\ud574\uc57c \ud569\ub2c8\ub2e4."), (648, 696, 720),
        spec("D5FB94DDC1A5B49093AD759A0D9026D62949B4870BDC7C67C8B11A354CDD3BBA", 115), spec("DB33FE14540595FCF4FC345301644EEEB8C4F5606C30B7A2D56D04CE35F37348", 115),
        spec("FD2216D66BF7FDE352CFC5B5D356C6084E5BE0DEC3B9B0CD6721C127CD41936F", 99), spec("048053B84290A56E03384F039EBC2632DDD2B2D40147606E17AB92FF1345EA8D", 99),
        spec("B75196B86F5A28B30B6309D813B3C64CEF083DE18F8F46B583F782B6A8677C9F", 233), spec("F250C32B3D791B871ED3274D68ECEBD67925CE4B3F9E7C32A7EDFA0F0EAE4EE9", 79), spec("1EABA9715AE3A3DDDCED26EA7F0F97C695A57BFB56AE41052CE7DED60A7CB869", 77),
        spec("67ADC791C2EECECBBC98710146DF3FC45E3CB8379F897CB984E7600AA2AB1ED3", 115), "Apology is followed by the reason to avoid needless fighting.",
    ),
    Family(
        "settle_dispute", (8, 1068), (8, 1080),
        literals(r"\ubd84\uc7c1\uc744 \uc218\uc2b5\ud558\uace0 \uc654\uc2b5\ub2c8\ub2e4.", r"\n\uc0ac\uc18c\ud55c \uc77c\uc774 \uc6d0\uc778\uc774\uc5c8\ub358 \ub4ef\ud569\ub2c8\ub2e4\u2026\n\uc774\ub85c\uc368 \uc601\ub0b4\ub294 \uc6d0\ub798\ub300\ub85c \ub3cc\uc544\uac14\uc2b5\ub2c8\ub2e4."), (600, 792, 864),
        spec("EC95D6B4CCDDE72E3CEFB9D9301E3944E6931A971A548251F1CDEDC8B05B787A", 129), spec("39C2A94D8B892FAF622AB33F3210AFE9C7FFCBCD45F2895E5F0664411233AA7F", 129),
        spec("668F1DA6E7661D46DFAE83F201EF533716FC6AC02942807EC58DB335F4726B4C", 115), spec("B580C965A08B3D72F4A9E4B20E0B3FB1110386036C26E3B68C8E1DA4B795CB3B", 115),
        spec("ADC1719C554DA74EB1E3A37323111139407B4E36814E470A5610716A9833AD57", 335), spec("95CFC4B2EA3622EB4BAE8EAF3DE88AF03C333D55CF171CE493E2F7A0494D41C8", 73), spec("EEFEDC8ABE4DAAF1BEA9B3908B32CE724B1C392EE151C4F06144C465989D9D7A", 81),
        spec("B090E07145B1FCA7E022C922A165044ED60B20F24C7048F7170CAEC7529716AF", 123), "The cause and restoration of order remain separated by manual line breaks.",
    ),
    Family(
        "silver_vein", (8, 1183), (8, 1199),
        literals(r"\uc740\uc758 \uc0c8\ub85c\uc6b4 \uad11\ub9e5\uc774 \ubc1c\uacac\ub418\uc5c8\uc2b5\ub2c8\ub2e4.", r"\n\ub300\uaddc\ubaa8 \uacf5\uc0ac\ub97c \ubc8c\uc5ec\n\ucc44\uad74 \uccb4\uc81c\ub97c \uac16\ucd94\uace0\uc790 \ud569\ub2c8\ub2e4."), (816, 432, 672),
        spec("BEF9F68A9DF2589E799BAEBC5BE23CD8B5DE445B10A3576B63210A0F0B68394C", 105), spec("548EFD66D69D9883EE47C027BF5D5579FC719EE140332D41FE995A175FC602FA", 105),
        spec("D20FB5C9FF13CDB2CDB02FDD997B159FAF14B711740AA300E4BE015C164A39A2", 89), spec("38133BCB36DF3F98BE6FF107BE82ABC4DB5BBD466F213B2327C6415841427308", 89),
        spec("19E07C9C7045421F2F10104CD8094D5D71BCAB371E10B214565DD2AF9198C304", 201), spec("2C14F88168FC360727503DFF17506229F5E58AF5EEC63918253A8CCEBA2BFE5E", 83), spec("B5377ECB209EBADD4458146C5626F251C09B0C8886F5A0E2800274A0C4893913", 75),
        spec("66EED1DC3DFE4F31962C40EC9CBE172B4686304B320108305560911362AF4531", 109), "Mining development is an explicit two-step outcome and plan.",
    ),
    Family(
        "retain_vanguard", (13, 107), (13, 107),
        literals(r"\ub610\ud55c \ubb34\uc6a9\uc774 \ub6f0\uc5b4\ub09c \ubb34\uc7a5\uc774\ub2c8\n\uc2f8\uc6c0\uc5d0\uc11c\ub294 \uc120\ubd09\uc5d0 \uc11c\uc11c \uc801\uc744 \uc4f0\ub7ec\ub728\ub824\n\uc8fc\uc5c8\uc73c\uba74 \ud558\uc624"), (648, 864, 312),
        spec("58CF0183864BA6168505DA3288537A26BF08BEE4C3DD57C8DAE779EBBED4CAA5", 103), spec("70166CE45CCCBEB32D0D5695B93A5311941D9DC5B078A57B35FA7550ADD45691", 103),
        spec("6BB9DB1C482AE7EE42D25976CA6537F0AEF45B902AB9C1C42EE36A65BC0CFBD3", 87), spec("2A0B32AAD6BD44518FD5CC1657457A0A01CD14C30B6F5E8CD0AFBC776F684E12", 87),
        spec("0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850", 9), spec("0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850", 9), spec("0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850", 9),
        spec("F99CB2E512F0770F02F811C4942F4E3550DC306D55A084EE2F77269424A0C2A9", 97), "Literal text is retained; only the static Japanese morphology command is removed.", True,
    ),
    Family(
        "retain_useful_trait", (13, 121), (13, 121),
        literals(r"\ub3c4\uc6c0\uc774 \ub418\ub294 \ud2b9\uc131\ub3c4 \uac16\ucd98 \uc778\ubb3c\uc774\ub2c8\n\uc720\uc6a9\ud558\uac8c \ud65c\uc6a9\ud574\uc57c \ud560 \uc904\ub85c \uc544\ub8b0\uc624"), (768, 768),
        spec("32F55F81BEE9587B02056044CDA94F42ED26C2A3F39795A376FD331252A36A96", 89), spec("32F55F81BEE9587B02056044CDA94F42ED26C2A3F39795A376FD331252A36A96", 89),
        spec("730E5AFD79C6BF3972B1B6FFAE45D9A2D94B306599CB41BBF4DDF6799C39693C", 67), spec("730E5AFD79C6BF3972B1B6FFAE45D9A2D94B306599CB41BBF4DDF6799C39693C", 67),
        spec("0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850", 9), spec("0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850", 9), spec("0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850", 9),
        spec("BB76BEECE19BE9E1F2D1D6BE00A3BF9E032D1DBBED2450461ED249010C8CC74A", 83), "Literal text is retained; only the static Japanese morphology command is removed.", True,
    ),
    Family(
        "withdraw_offer", (15, 248), (15, 251),
        literals(r"\uae30\ud68c\ub97c \ub193\uce5c \ub4ef\ud569\ub2c8\ub2e4.", r"\n\uc774\ucabd\uc758 \uc81c\uc548\uc740 \ucca0\ud68c\ud558\uaca0\uc2b5\ub2c8\ub2e4."), (504, 696),
        spec("6F90D0EA7D1FC25B489758011D7BAE60005F3FA39A88E4D1DD86EFB002E4C14C", 67), spec("B627B2490B6C0CA4C10F94F65CAE74ABCB53A09220956E622794210554AE0D18", 67),
        spec("7DF6BA62A5F214216427D80603923504CF493A4061607D77365A882B6A022CFA", 73), spec("BC93C6DE057CDC43807675EC278F9D27E91787B928A4A55373298850636635BB", 73),
        spec("39F43492A73317CFB01F3F7159F3A1A2F4C7945B110E41F5482586EEA7E7DDBF", 147), spec("17545E5F7778BBB313D62958452F73CFBD86D5B7CC5126F60863AD8B5B972361", 43), spec("4B05906ED878F6FAAF678E6485375C381FF8ED6B76FC8CE6A970BEB22948F149", 43),
        spec("B0E6BD1862CE4595603286AA8D214FED997A8CE470BCB6F38E5656858E2455B2", 73), "The declined proposal is succinct and grammatically complete.",
    ),
    Family(
        "rumor_illusion", (15, 253), (15, 256),
        literals(r"\uc720\uc5b8\ube44\uc5b4\uc640 \ud658\uc220\ub85c \uc801\uc744 \ud604\ud639\ud558\uc624.", r"\n\uc7a5\uce58 \uc900\ube44\uc5d0 \uc5bc\ub9c8\uac04\uc758 \uc790\uae08\uc774 \ud544\uc694\ud558\uc624", r"\ub098\n\ub354 \ub9ce\uc740 \uc801\uc744 \ub04c\uc5b4\ub4e4\uc77c \uc218 \uc788\uc744 \uac83\uc774\uc624."), (768, 912, 888),
        spec("E7BFCB2655F2858A01A80CF276F348EADFD157FA7AB2E2E7AB7374A9CFE5A973", 151), spec("E7E48D89765D1A59B487E577E96E82644B2AE7B8138763C920C95547394FCD1F", 151),
        spec("F639855518BAB4A1165E08CEE6A755174C449453C30F925B8D455C955E73D4F6", 127), spec("4FE22C4B303FF56A6DDBCB31E4F106E844B3797ADFDCD660A7408A162C710073", 127),
        spec("5138FF51AD302A3081BF0A2CBCCEDC3B0DA01747EF9300FBBC957ACCD6866FEB", 379), spec("132404B4511B5EC6E71B92CDDE6AE7EEBD0F8974E2708D3DBD225C78293EAFD9", 87), spec("0EF3CC01A917CD2674420AA89E7CE14D4349E3CF6F543FDF9C0394405F57D516", 101),
        spec("0DCA492CFD86BF6FD351831439081986DDEA60D60FB8C7E36742704BAA5B1855", 147), "PC JP/EN/SC/TC all retain rumor, illusion, preparation cost, and drawing more enemies; Korean restores the conditional result and one formal speaker voice.",
    ),
    Family(
        "incitement_edict", (15, 261), (15, 264),
        literals(r"\uc120\ub3d9\uc5d0\ub294 \uc57d\uac04\uc758 \uc790\uae08\uc774 \ud544\uc694\ud558\uc624", r".\n", r"\uad50\uc11c\ub85c \ud638\uc18c\ud55c\ub2e4\uba74", r"\n\uc120\ub3d9\uc740 \ud2c0\ub9bc\uc5c6\uc774 \uc131\uacf5\ud560 \uac83\uc774\uc624."), (768, 408, 720),
        spec("1A426B4CF869C3ACABA4CC988E7451EA17DD682A7603A731AE22B38D0C7A0FED", 141), spec("5A13688FE8DC5713AA136403BC576E4CA3411C02683B552610006D89307C8DA1", 141),
        spec("4195BF28254893A763EF90B89F015E988D117D3F58268D4B3FEFE1C5894F758B", 127), spec("BED9E0A1CB7880A1E5C3C1F5BEBA65E9EA8AAD365F76A05095B27461BF4AF129", 127),
        spec("8F2573CB2B56A8CD88D9C1F2A445658776BA928051325789A14E6945FDFA69BA", 265), spec("F84C38F748190106CE4B15344D2927D9E27419631031243F0D2E47FC6F8FDDF4", 97), spec("27F8D4CA626CBCFD37F983A3AAE4C4E539C2E5A6039901C08916A0E2E37F1E94", 103),
        spec("EFC5DB6A6BE8ED858E671B74F4A1BB59AFC6D78047B8DFE57091DE5E66B4FD9E", 119), "PC JP/EN/SC/TC consistently anchor funding, an official decree, and certain success; Korean restores the condition-and-result structure in one natural formal voice.",
    ),
    Family(
        "bandit_officer", (15, 1506), (15, 1521),
        literals(r"\uc4f8 \ub9cc\ud55c \uc870\uc7a5\uc744 \uc774\uacf3\uc5d0 \ud30c\uacac\ud558\uc5ec\n\ub3c4\uc801 \ud1a0\ubc8c\uc744 \ub9e1\uaca8 \ubcf4\ub294 \uac83\uc740 \uc5b4\ub5bb\uaca0\uc18c?\n\uc88b\uc740 \ubb34\uacf5\uc744 \uc138\uc6b8 \uae30\ud68c\ub3c4 \ub420 \uac83\uc774\uc624."), (720, 864, 816),
        spec("4347E77F967AF1DFA75867C1DF66A6C7B5D851299F310C0EC300AD80AB9A0130", 121), spec("FC3AF4594D97E2F3A8ADBABDD664C2F6E3A9D26908ED20B3048FF426CB9E9608", 121),
        spec("BA9C6E88CD491D9C56FA6CBBF419A166C573375F1223383B8B7BF3FB53F3CECC", 91), spec("E6112EA55190FEF483769572F329E89A877862803EDB36594D276ACCDF2128BA", 91),
        spec("0835FCD9DC08FB409DCC871FAD04CB0DA9A0DB36266DDA6EB172DA41A09E855F", 285), spec("5FACEBA651EAC51EB31C08F9A964732EDBC55953BDF03622BFE061770C998134", 71), spec("605A3273CA992B5EDFFA7BFCFDEECBE4AA93A46BE7EC762FB1C8C53C9859DE17", 73),
        spec("93E80206EB081A7F92303E8AE16114122AE6560CE92ABF3DF9E6BAAF230554C8", 129), "Officer dispatch and its expected merit remain three readable lines.",
    ),
    Family(
        "next_country_base", (15, 1588), (15, 1618),
        literals(r"\ud55c \ub098\ub77c\uc758 \uc9c0\ubc30\uc5d0 \ub9cc\uc871\ud574\uc120 \uc548 \ub429\ub2c8\ub2e4.", r"\n\ub2e4\uc74c \ub098\ub77c\ub97c \uacf5\uaca9\ud558\uae30 \uc704\ud55c \uac70\uc810\uc73c\ub85c\n\ubc1c\uc804\uc2dc\ucf1c \ub098\uac00\uc57c \ud569\ub2c8\ub2e4."), (864, 816, 552),
        spec("2AF448F953EC4E19937E77522ADF51141E943D93AFB09A217284240D423E46F9", 123), spec("0EC2633478908D02B9835D879424630D3A0BCF70BAB97331874773B5EB1A1619", 123),
        spec("803AC8C855FBFA1870D254BE4E47118C4AF8BEB785CAA3BF964B38CA2C037A40", 97), spec("7A85E3549DBD886A4E70CC4470A952B69CA4480D33CF3B498554946C79D2C905", 97),
        spec("75D2751E8B1FAC83A32B9DB5381322B9A76DB1090C84DD00201B680F2E3A49B2", 289), spec("A7C9E82D6F0EA128141E83E9E331AD408EBC36C5C4D157909FB3347AF3ED1C9E", 85), spec("5CDCBB43702E89269A26B5847970D27E1B0BA17AB86437D79AEB3A2F6AE94282", 73),
        spec("6CE04580E0F42D4A00348A4E1C61D17DC52773AB4D3543BE497165469FAC3115", 125), "The next-country objective keeps its causal two-part phrasing.",
    ),
    Family(
        "appoint_lord", (15, 1626), (15, 1656),
        literals(r"\uc544\ubb34\ub798\ub3c4 \ube44\uc5b4 \uc788\ub294 \uad70\uc774 \uc788\ub2e4\ub358\ub370\u2026\n\ub9c8\uce68 \uc5ec\uc720\uac00 \uc788\ub294 \uc790\uac00 \uc788\uc73c\ub2c8", r"\n\uc601\uc8fc\ub85c \ub2e4\uc2a4\ub9ac\uac8c \ud558\ub294 \uac83\uc740 \uc5b4\ub5bb\uaca0\uc18c?"), (816, 672, 840),
        spec("4193A1F81C2E6CFA16D7C2F69623963DFFFEB6EBC90447DA02AF14D6374890D1", 121), spec("4193A1F81C2E6CFA16D7C2F69623963DFFFEB6EBC90447DA02AF14D6374890D1", 121),
        spec("980A3CCD871C8BA167F152A5DE2EAC748DF26636305B9E176242B2809FB68873", 105), spec("980A3CCD871C8BA167F152A5DE2EAC748DF26636305B9E176242B2809FB68873", 105),
        spec("449605D61BE90C94D8C81C115BBE71774F9B0267E6895DADECD263EFF5A0EF18", 243), spec("9B40678077708E0B635C7D3200515F068E0E4CEDC7728B8765A213F554B6BEE2", 81), spec("90BF21212711BFC9920BC164D7D2BB4FDA5C4B5335308E860CC3F0689B369565", 81),
        spec("BFB6B87B48A166A080521AE4063BFB3C4D3C8DEDB6067A7ECFCC47F43352F695", 129), "PC JP/EN/SC/TC convey an available person; Korean replaces the literal ‘empty hand’ phrasing with natural courtly wording.",
    ),
    Family(
        "diplomatic_strategy", (15, 1822), (15, 1852),
        literals(r"\ud604\uc7ac \ud2b9\ubcc4\ud788 \uc8fc\uc758\ud560 \uc138\ub825\uc740 \uc5c6\uc2b5\ub2c8\ub2e4.", r"\n\uc8fc\ubcc0 \uc138\ub825\uc758 \uc804\ub825\uc5d0 \uc720\uc758\ud558\uba70\n\uc678\uad50\u00b7\uacf5\ub7b5 \uc804\ub7b5\uc744 \uc138\uc6cc \ub098\uac00\uc57c \ud569\ub2c8\ub2e4."), (840, 648, 888),
        spec("1F5AB94946B2D71131928CA05C94543B871D4DE4CA1482D6531EBF96B24BC637", 127), spec("115E27739724A69CF200EE8A96E29C4D66B862B05BBCD7FADBA6067D8E74C756", 127),
        spec("2CF6880EB6F25C1B861C00B191468FBFADC9FA79C719A05EFE2F9E60F158FFCF", 113), spec("630ABF1AC835E1395A7982887894DC0804BC854615863359EC45AB4EDEF3D230", 113),
        spec("75443129FCB543393C521C5BAAFB3AE67E1E4C71B865161730A97439BBFC1247", 329), spec("21FEFF33FF12ACEF7432ED450CDA5814F749FB13C5C6E5E9C6C49CCEDE6641F7", 89), spec("A0350F7C49A7BDA8987C971E7825E3ACB86E714971A52094FB11BEE1EF2B41E6", 87),
        spec("36EAC9FF3F236816DC060D4E2CAEC4AC93D35C2D7FDDBE06B81D02DB17A4B01B", 131), "PC JP/EN/SC/TC identify no specially concerning force; Korean resolves the prior unnatural noun attachment.",
    ),
    Family(
        "war_preparation", (15, 1823), (15, 1853),
        literals(r"\uc804\uae30\uac00 \uc784\ubc15\ud588\uc73c\ub2c8 \uad70\ube44\ub97c \uac16\ucd94\ub824\uba74\n\uc804\uad70\uc5d0 \uacf5\ub7b5 \ubaa9\ud45c\ub97c \uc81c\uc2dc\ud574\uc57c \ud558\uc624."), (792, 792),
        spec("C910AFF0EE59E5A1A19EECA2B84F156A7CAF22020C94E2E7728B826F294907CC", 103), spec("C910AFF0EE59E5A1A19EECA2B84F156A7CAF22020C94E2E7728B826F294907CC", 103),
        spec("7F833192759F443F16F1F773E0615A482DE4798B08A02523418DB095BF2E8234", 73), spec("7F833192759F443F16F1F773E0615A482DE4798B08A02523418DB095BF2E8234", 73),
        spec("760595B454E5545B08A0EACEBA0D41511478A2915065ADAE1878337082052EA0", 159), spec("F60BEC0650D02E88BFF522BCCDAFB9BF572E4D7C4E14C7C3E5A4C0B9ABE7633D", 51), spec("E6207DCD198CA4F2B14C02A5F6DA6F457DFD843E754318F652514CA681C6B4F2", 51),
        spec("DC25E3DF3C925FB19B61FDB6E73965A6BFE83E49987DEAB811ED0BBBDA1D4A5F", 85), "War preparation remains a direct two-line order.",
    ),
    Family(
        "wait_for_invasion", (15, 1860), (15, 1890),
        literals(r"\uc8fc\ubcc0 \ub3d9\ud5a5\uc744 \uacbd\uacc4\ud558\uba70\n\uae30\ud68c\ub97c \ubcf4\uc544 \uce68\uacf5\ud574 \uc138\ub825\uc744 \ub113\ud600\uc57c \ud558\uc624."), (480, 912),
        spec("C73B09B1224F4FA58B286B48121E2DD0133FA846A47B94CAB48429B18ED017F5", 81), spec("7E006043A833BECB75B6F1E20076A514C700022D8C0F5C97C383966986A310C2", 81),
        spec("1A6076A92A0053FB599C2DBE23D43E7C10D2B0B58661C696AEC26CF8566093A8", 67), spec("03D6931E12B7B38BDC8E54A4FD32415A515081656D7AA86CCF3D5D67C9D25E4A", 67),
        spec("5F41292310D7F93F78C8066F048C42F0B1A8EBE91D2D2057258CDC46FC60A10C", 235), spec("334A3DBDF0CBF824B708003296103DF5BEBB7BC1A5CBAE91DE72A0FEF911FCFA", 67), spec("53F83DB37392C24A0D7B1ACB20796D45835BA3DAF42C5137AA678095F00E3FEB", 69),
        spec("643CD0AF81DDD875BA972150631573DA7773471AE9C3B6A8BB10A0FEE8A1D248", 77), "The final line reaches but never exceeds the 912 px limit.",
    ),
    Family(
        "strength_wait", (15, 1862), (15, 1892),
        literals(r"\ubb34\ubaa8\ud55c \uc9c4\uad70\uc740 \ubaa9\uc228\uc744 \uc783\uae30 \uc27d\uc18c.", r"\n\uad6d\ub825\uc744 \ub192\uc774\uba70 \ud0c0\uad6d\ub07c\ub9ac \uc2f8\uc6cc\n\ud53c\ud3d0\ud574\uc9c8 \ub54c\ub97c \uae30\ub2e4\ub9ac\ub294 \uac83\ub3c4 \ud55c \uc218\uaca0\uc18c."), (744, 648, 912),
        spec("BA0BFDD91716EF0390B5A7780AC1E7F74DE2E1AF99D3813416A8D69982B33322", 135), spec("0D4AA95C3584788C622B034B434795B26055065BB976E2EC12EA6662FFA046ED", 135),
        spec("972693F7213EC634E456791A266B9FDE1930948804854B6748AAB4565FDED733", 109), spec("025D24D10DEEB49F9542E4E5938C0E380A6203B77009EF1335572C4969214C92", 109),
        spec("1E375D710AB3B0CD7F94EFBD562FC0DFD8A8205E14FB939812013F894CF855F4", 341), spec("4F4A8908319F548DF3E594B9E6326E6DE8541E34AC67703D9D08DE1F9175D6B4", 79), spec("84BDC7A2E5DB93D7D22CACCCBF37A1694D0096A5484E3BDA9FAE4843ECA72C67", 79),
        spec("F7B8E3DD4C0E86D2DECC3648E81FB4E72DFA8D7A0C995392EB22E08F00488DCD", 129), "PC JP/EN/SC/TC anchor waiting for rival exhaustion; Korean repairs the broken modifier while keeping the same strategic advice.",
    ),
    Family(
        "expect_result", (15, 2194), (15, 2224),
        literals(r"\uc54c\uaca0\uc2b5\ub2c8\ub2e4.", r"\n\uc131\uacfc\ub97c \uae30\ub300", r"\ud574 \uc8fc\uc2ed\uc2dc\uc624."), (264, 552),
        spec("60A1AFBAC1B1D8901AC63827BB08E5FDB6318F1709C62F538F2B9782968FC401", 57), spec("AE16A658A12C62A7A218445720732AAEA393A57BFE5D9AAC8E88F23B2278E830", 57),
        spec("11682F5A2258A6299F7C52476EC5ABB95D0D57A19E3BEFFCA33F9A2AB7BE9813", 61), spec("BDA7577CBE1E7F81194A1AF4AA470DBC9E0B90E76C2E1FA5AFA9D7981C755596", 61),
        spec("6B9D05072A6538F5626ECD17B6C15173A989E020B11D428EB70EA7EB398209A6", 115), spec("FBD7B0E4716C22F3E655BE148B73C7BF0239C232CCC56B2B3983FF6A13AF3512", 25), spec("BEC5285CA39F0BF4651EA9ACD88508DCCC0F5DB502E1D582C7B72D2BA5E33E67", 21),
        spec("D9304219D6940467FD0E2D11344C0A2AE7B800A8F3C515FAEB4CE54B62235790", 61), "The split literal fragments retain one grammatical Korean sentence.",
    ),
    Family(
        "await_good_news", (15, 2195), (15, 2225),
        literals(r"\ubbf8\ub825\uc774\ub098\ub9c8 \ud798\uc744 \ub2e4\ud558\uaca0\uc2b5\ub2c8\ub2e4.", r"\n\ub0ad\ubcf4\ub97c \uae30\ub2e4\ub824 \uc8fc\uc2ed\uc2dc\uc624."), (696, 552),
        spec("A4A594E312ADF0C1DA2745484E8B5F058BDE535F7FBB4B23BB1915FC3167FD4F", 47), spec("65DC87AD30E6BBD2CAE9C2B8E8AA9DEB28B90DF63898F8892568C0180B6D05A5", 47),
        spec("3844D1CE755B81A2F4E0B99D733EFE14EF571AD2F5C2898CC256F65A7BED6053", 45), spec("B15659D0A29CA4F02ED6E17D0B8359793567DEE8016CA9938D1CB9E92DE8C8E3", 45),
        spec("AC2E971F79C147D954FB05FA1B0344EC8CF5C9BE9EB2D03BC7BC456F549BC0DC", 119), spec("2084B61A03E204A1E66E14B92384055F7BBABF960F696E9BCE436DF98528CE43", 45), spec("A6AEFCEF569EC2207E097705ADF719C9A826C29D505F62746A5D1F43370D9890", 35),
        spec("17C4DD5C021EDB32F2ADFE2201B770920724508E59A3FE81EEB47221B86BC80D", 75), "The modest pledge and request for good news remain complete.",
    ),
)


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
    return {(record.block_id, record.record_id): record for block in archive.blocks for record in block.records}


def literal_texts(record: MsgGameRecord) -> tuple[str, ...]:
    return tuple(literal.text for literal in parse_record_literals(record))


def opaque_spans(record: MsgGameRecord) -> tuple[bytes, ...]:
    cursor = 0
    spans: list[bytes] = []
    for literal in parse_record_literals(record):
        spans.append(record.data[cursor:literal.marker_offset])
        cursor = literal.marker_end
    spans.append(record.data[cursor:])
    return tuple(spans)


def marker_topology(record: MsgGameRecord) -> tuple[tuple[bytes, bytes], ...]:
    return tuple(
        (record.data[literal.marker_offset:literal.marker_offset + len(LITERAL_START)], record.data[literal.marker_end - len(LITERAL_END):literal.marker_end])
        for literal in parse_record_literals(record)
    )


def morphology_commands(record: MsgGameRecord) -> tuple[str, ...]:
    commands: list[str] = []
    for span in opaque_spans(record):
        cursor = 0
        while cursor < len(span):
            if span[cursor:cursor + 2] == MORPHOLOGY_PREFIX:
                if cursor + 6 > len(span):
                    raise Wave23Error("truncated 01 43 command")
                commands.append(span[cursor:cursor + 6].hex().upper())
                cursor += 6
            else:
                cursor += 1
    return tuple(commands)


def strip_0143_span(span: bytes) -> bytes:
    """Remove only complete 01 43 commands; copy every other opaque byte."""

    result = bytearray()
    cursor = 0
    while cursor < len(span):
        if span[cursor:cursor + 2] == MORPHOLOGY_PREFIX:
            if cursor + 6 > len(span):
                raise Wave23Error("truncated 01 43 command")
            cursor += 6
        else:
            result.append(span[cursor])
            cursor += 1
    return bytes(result)


def stripped_opaque_spans(record: MsgGameRecord) -> tuple[bytes, ...]:
    return tuple(strip_0143_span(span) for span in opaque_spans(record))


def assert_record_spec(record: MsgGameRecord, expected: RecordSpec, label: str) -> None:
    if sha256_bytes(record.data) != expected.sha256 or len(record.data) != expected.size:
        raise Wave23Error(f"{label} whole-record invariant differs")


def profile_hashes(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for relative in PROFILE_PATHS:
        path = root / relative
        if not path.is_file():
            raise Wave23Error(f"profile resource is absent: {relative}")
        result[relative] = sha256_path(path)
    return result


def profile_sizes(root: Path) -> dict[str, int]:
    return {relative: (root / relative).stat().st_size for relative in PROFILE_PATHS}


def assert_profile(root: Path, expected_hashes: Mapping[str, str], expected_sizes: Mapping[str, int], label: str) -> None:
    actual_hashes = profile_hashes(root)
    actual_sizes = profile_sizes(root)
    if actual_hashes != dict(expected_hashes) or actual_sizes != dict(expected_sizes):
        mismatch = {
            relative: {"expected_sha256": expected_hashes.get(relative), "actual_sha256": actual_hashes.get(relative), "expected_size": expected_sizes.get(relative), "actual_size": actual_sizes.get(relative)}
            for relative in PROFILE_PATHS
            if actual_hashes.get(relative) != expected_hashes.get(relative) or actual_sizes.get(relative) != expected_sizes.get(relative)
        }
        raise Wave23Error(f"{label} profile mismatch: {json.dumps(mismatch, sort_keys=True)}")


def reject_switch_path(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    if any("switch" in component.casefold() for component in resolved.parts):
        raise Wave23Error(f"Switch input is forbidden: {label}")
    return resolved


def require_predecessor_root(path: Path) -> Path:
    expected = PREDECESSOR_ROOT.resolve(strict=True)
    resolved = path.resolve(strict=True)
    if resolved != expected:
        raise Wave23Error(f"input must be the unique Wave 22 private candidate: {expected}")
    return resolved


def validate_wave22_evidence(root: Path) -> dict[str, Any]:
    manifest_path = root.parent / "build_manifest.v1.json"
    audit_path = root.parent / "audit.v1.json"
    if (
        not manifest_path.is_file()
        or not audit_path.is_file()
        or manifest_path.stat().st_size != WAVE22_MANIFEST_SIZE
        or audit_path.stat().st_size != WAVE22_AUDIT_SIZE
        or sha256_path(manifest_path) != WAVE22_MANIFEST_SHA256
        or sha256_path(audit_path) != WAVE22_AUDIT_SHA256
    ):
        raise Wave23Error("Wave 22 candidate evidence differs")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise Wave23Error("Wave 22 manifest is not JSON") from exc
    if (
        manifest.get("schema") != "nobu16.kr.pc-dialogue-quality-wave22-static-inflection.v1"
        or manifest.get("profile_paths") != list(PROFILE_PATHS)
        or manifest.get("output_sha256") != INPUT_SHA256
        or manifest.get("output_sizes") != INPUT_SIZES
        or manifest.get("candidate_only") is not True
    ):
        raise Wave23Error("Wave 22 manifest contract differs")
    return {
        "root": root.relative_to(REPO).as_posix(),
        "audit_sha256": WAVE22_AUDIT_SHA256,
        "manifest_sha256": WAVE22_MANIFEST_SHA256,
        "profile_sha256": INPUT_SHA256,
        "profile_sizes": INPUT_SIZES,
    }


def validate_raw_roundtrip(packed: bytes, label: str) -> None:
    header, raw = decompress_wrapper(packed)
    archive = parse_packed_msggame(packed).archive
    if rebuild_raw_msggame(archive) != raw:
        raise Wave23Error(f"{label} raw parse/rebuild differs")
    repacked = recompress_wrapper(raw, header)
    _header, rebuilt_raw = decompress_wrapper(repacked)
    if rebuilt_raw != raw:
        raise Wave23Error(f"{label} wrapper round-trip differs")


def load_references() -> tuple[dict[str, dict[tuple[int, int], MsgGameRecord]], dict[str, str]]:
    archives: dict[str, dict[tuple[int, int], MsgGameRecord]] = {}
    hashes: dict[str, str] = {}
    for language, (path, expected_hash) in PC_REFERENCE_PATHS.items():
        checked = reject_switch_path(path, f"PC {language}")
        actual = sha256_path(checked)
        if actual != expected_hash:
            raise Wave23Error(f"PC {language} source hash differs")
        archives[language] = records_by_coordinate(checked.read_bytes())
        hashes[language] = actual
    return archives, hashes


def validate_family_anchors(references: Mapping[str, Mapping[tuple[int, int], MsgGameRecord]]) -> None:
    for family in FAMILIES:
        checks = (
            ("BASE_JP", family.base_coordinate, family.base_jp),
            ("PK_JP", family.pk_coordinate, family.pk_jp),
            ("EN", family.pk_coordinate, family.en),
            ("SC", family.pk_coordinate, family.sc),
            ("TC", family.pk_coordinate, family.tc),
        )
        for language, coordinate, expected in checks:
            record = references[language].get(coordinate)
            if record is None:
                raise Wave23Error(f"{family.name} {language} anchor is absent")
            assert_record_spec(record, expected, f"{family.name} {language}")
        if literal_texts(references["BASE_JP"][family.base_coordinate]) != literal_texts(references["PK_JP"][family.pk_coordinate]):
            raise Wave23Error(f"{family.name} Base/PK Japanese literal tuple differs")


def validate_text(value: str, label: str) -> None:
    if not value or "\x1b" in value or "%" in value:
        raise Wave23Error(f"{label} contains a runtime marker or is empty")
    encoded = value.encode("utf-16-le")
    if LITERAL_START in encoded or LITERAL_END in encoded:
        raise Wave23Error(f"{label} encodes a reserved marker")
    for character in value:
        if character != "\n" and unicodedata.category(character) == "Cc":
            raise Wave23Error(f"{label} contains control U+{ord(character):04X}")


def _font_u32(raw: bytes, offset: int, label: str) -> int:
    if offset < 0 or offset + 4 > len(raw):
        raise Wave23Error(f"font {label} is outside G1N")
    return struct.unpack_from("<I", raw, offset)[0]


@functools.lru_cache(maxsize=1)
def font_metric_state() -> tuple[bytes, tuple[int, ...], int, int]:
    path = reject_switch_path(FONT_RESOURCE, "active PC JP font")
    if sha256_path(path) != FONT_SHA256:
        raise Wave23Error("active PC JP font hash differs")
    try:
        archive = parse_link(path.read_bytes())
        _header, raw = decompress_wrapper(archive.entries[FONT_OUTER_ENTRY].data)
    except (IndexError, ValueError) as exc:
        raise Wave23Error("active PC JP font entry cannot be decoded") from exc
    if raw[:8] != b"_N1G0000" or _font_u32(raw, 0x08, "declared size") != len(raw):
        raise Wave23Error("active PC JP font header differs")
    table_count = _font_u32(raw, 0x1C, "table count")
    if not 1 <= table_count <= 32 or FONT_TABLE >= table_count:
        raise Wave23Error("active PC JP font table count differs")
    offsets = tuple(_font_u32(raw, 0x20 + 4 * index, f"table {index} offset") for index in range(table_count))
    atlas_offset = _font_u32(raw, 0x14, "atlas offset")
    if offsets != tuple(sorted(offsets)) or len(set(offsets)) != len(offsets):
        raise Wave23Error("active PC JP font table offsets differ")
    table_offset = offsets[FONT_TABLE]
    table_end = offsets[FONT_TABLE + 1] if FONT_TABLE + 1 < table_count else atlas_offset
    record_start = table_offset + FONT_MAP_BYTES
    if not 0 <= table_offset <= record_start <= table_end <= len(raw):
        raise Wave23Error("active PC JP font table bounds differ")
    record_bytes = table_end - record_start
    if record_bytes % FONT_RECORD_BYTES:
        raise Wave23Error("active PC JP font record alignment differs")
    record_count = record_bytes // FONT_RECORD_BYTES
    if record_count <= 0:
        raise Wave23Error("active PC JP font has no records")
    return raw, struct.unpack_from("<65536H", raw, table_offset), record_start, record_count


def font_advance_px(character: str) -> int:
    """Return an active-font advance; a missing glyph is a hard failure."""

    if len(character) != 1 or ord(character) > 0xFFFF:
        raise Wave23Error("font metric requires one BMP character")
    raw, mapping, record_start, record_count = font_metric_state()
    ordinal = mapping[ord(character)]
    if ordinal == 0 or ordinal >= record_count:
        raise Wave23Error(f"active PC JP font has no usable glyph for U+{ord(character):04X}")
    offset = record_start + ordinal * FONT_RECORD_BYTES
    width = raw[offset]
    advance = raw[offset + 4]
    if width != advance or advance not in (24, 48):
        raise Wave23Error(f"active PC JP glyph metric differs for U+{ord(character):04X}")
    return advance


def font_line_widths_px(values: tuple[str, ...]) -> tuple[int, ...]:
    widths: list[int] = []
    for line in "".join(values).split("\n"):
        width = 0
        for character in line:
            if unicodedata.category(character) == "Cc":
                raise Wave23Error(f"font layout has control U+{ord(character):04X}")
            width += font_advance_px(character)
        widths.append(width)
    return tuple(widths)


def rebuild_static_record(source: MsgGameRecord, target_literals: tuple[str, ...]) -> bytes:
    """Replace literals while preserving every non-0143 opaque source byte."""

    source_spans = opaque_spans(source)
    if len(source_spans) != len(target_literals) + 1:
        raise Wave23Error("target changes literal-marker count")
    payload = bytearray()
    for index, value in enumerate(target_literals):
        payload.extend(strip_0143_span(source_spans[index]))
        payload.extend(LITERAL_START)
        payload.extend(value.encode("utf-16-le"))
        payload.extend(LITERAL_END)
    payload.extend(strip_0143_span(source_spans[-1]))
    return bytes(payload)


def record_report(record: MsgGameRecord) -> dict[str, Any]:
    values = literal_texts(record)
    return {
        "record_sha256": sha256_bytes(record.data),
        "record_size": len(record.data),
        "literals": list(values),
        "literal_utf16le_sha256": [sha256_bytes(value.encode("utf-16-le")) for value in values],
        "opaque_spans_hex": [span.hex().upper() for span in opaque_spans(record)],
        "morphology_commands_hex": list(morphology_commands(record)),
    }


def validate_change(family: Family, resource: str, record: MsgGameRecord) -> tuple[bytes, dict[str, Any]]:
    coordinate = family.base_coordinate if resource == BASE_MSGGAME else family.pk_coordinate
    preimage = family.base_preimage if resource == BASE_MSGGAME else family.pk_preimage
    assert_record_spec(record, preimage, f"input {resource} {coordinate[0]}:{coordinate[1]}")
    current_literals = literal_texts(record)
    if len(current_literals) != len(family.target_literals):
        raise Wave23Error(f"{family.name} changes literal-marker count")
    if family.retain_literal_text and tuple(value.encode("utf-16-le") for value in current_literals) != tuple(value.encode("utf-16-le") for value in family.target_literals):
        raise Wave23Error(f"{family.name} retain literal payload differs")
    commands = morphology_commands(record)
    if not commands or not all(command.startswith("0143") and len(command) == 12 for command in commands):
        raise Wave23Error(f"{family.name} input command guard differs")
    for literal_id, value in enumerate(family.target_literals):
        validate_text(value, f"{family.name} target literal {literal_id}")
    current_text = "".join(current_literals)
    target_text = "".join(family.target_literals)
    if current_text.count("\n") != target_text.count("\n") or target_text.count("\n") + 1 > 3:
        raise Wave23Error(f"{family.name} changes manual line count or exceeds three lines")
    font_widths = font_line_widths_px(family.target_literals)
    if font_widths != family.target_font_widths_px or any(width > DIALOGUE_MAX_LINE_PX for width in font_widths):
        raise Wave23Error(f"{family.name} active-font widths differ or exceed maximum")
    target_data = rebuild_static_record(record, family.target_literals)
    target_record = MsgGameRecord(record.block_id, record.record_id, record.relative_offset, target_data)
    if (
        sha256_bytes(target_data) != family.target.sha256
        or len(target_data) != family.target.size
        or literal_texts(target_record) != family.target_literals
        or opaque_spans(target_record) != stripped_opaque_spans(record)
        or morphology_commands(target_record)
        or marker_topology(target_record) != marker_topology(record)
        or not target_data.endswith(RECORD_TERMINATOR)
    ):
        raise Wave23Error(f"{family.name} target record reconstruction differs")
    return target_data, {
        "family": family.name,
        "resource": resource,
        "coordinate": f"{coordinate[0]}:{coordinate[1]}",
        "input_record": record_report(record),
        "target_record": record_report(target_record),
        "retain_literal_text": family.retain_literal_text,
        "removed_opaque_commands_hex": list(commands),
        "removed_0143_command_count": len(commands),
        "preserved_non_0143_opaque_spans_hex": [span.hex().upper() for span in stripped_opaque_spans(record)],
        "marker_topology_preserved": True,
        "terminator_hex": RECORD_TERMINATOR.hex().upper(),
        "manual_line_count": {"current": current_text.count("\n") + 1, "target": target_text.count("\n") + 1},
        "font_line_widths_px": list(font_widths),
        "dialogue_max_line_px": DIALOGUE_MAX_LINE_PX,
        "rationale": family.rationale,
    }


def validate_output_records(before: Mapping[str, bytes], output: Mapping[str, bytes]) -> None:
    before_records = {resource: records_by_coordinate(data) for resource, data in before.items()}
    output_records = {resource: records_by_coordinate(data) for resource, data in output.items()}
    for family in FAMILIES:
        for resource, coordinate in ((BASE_MSGGAME, family.base_coordinate), (PK_MSGGAME, family.pk_coordinate)):
            source = before_records[resource].get(coordinate)
            record = output_records[resource].get(coordinate)
            if source is None or record is None:
                raise Wave23Error(f"candidate lacks {family.name} {resource}")
            if (
                sha256_bytes(record.data) != family.target.sha256
                or len(record.data) != family.target.size
                or literal_texts(record) != family.target_literals
                or opaque_spans(record) != stripped_opaque_spans(source)
                or morphology_commands(record)
                or marker_topology(record) != marker_topology(source)
                or not record.data.endswith(RECORD_TERMINATOR)
            ):
                raise Wave23Error(f"candidate target differs: {family.name} {resource}")
    for resource in CHANGED_PATHS:
        if before_records[resource].keys() != output_records[resource].keys():
            raise Wave23Error(f"record topology changed: {resource}")
        expected = {
            family.base_coordinate if resource == BASE_MSGGAME else family.pk_coordinate
            for family in FAMILIES
        }
        changed = {coordinate for coordinate in before_records[resource] if before_records[resource][coordinate].data != output_records[resource][coordinate].data}
        if changed != expected:
            raise Wave23Error(f"unexpected changed record set: {resource} {sorted(changed)}")


def prepare_candidate(input_root: Path = PREDECESSOR_ROOT) -> tuple[dict[str, bytes], dict[str, Any]]:
    input_root = require_predecessor_root(input_root)
    wave22_evidence = validate_wave22_evidence(input_root)
    assert_profile(input_root, INPUT_SHA256, INPUT_SIZES, "Wave 22 predecessor")
    before = {resource: (input_root / resource).read_bytes() for resource in CHANGED_PATHS}
    for resource, packed in before.items():
        validate_raw_roundtrip(packed, f"Wave 22 {resource}")
    references, reference_hashes = load_references()
    validate_family_anchors(references)
    current = {resource: records_by_coordinate(data) for resource, data in before.items()}
    replacements: dict[str, dict[tuple[int, int], bytes]] = {resource: {} for resource in CHANGED_PATHS}
    rows: list[dict[str, Any]] = []
    for family in FAMILIES:
        base_record = current[BASE_MSGGAME].get(family.base_coordinate)
        pk_record = current[PK_MSGGAME].get(family.pk_coordinate)
        if base_record is None or pk_record is None:
            raise Wave23Error(f"{family.name} Base/PK input record is absent")
        if literal_texts(base_record) != literal_texts(pk_record):
            raise Wave23Error(f"{family.name} Base/PK Korean literal tuple differs")
        for resource, coordinate, record in ((BASE_MSGGAME, family.base_coordinate, base_record), (PK_MSGGAME, family.pk_coordinate, pk_record)):
            if coordinate in replacements[resource]:
                raise Wave23Error(f"duplicate replacement: {resource} {coordinate}")
            target, row = validate_change(family, resource, record)
            replacements[resource][coordinate] = target
            rows.append(row)
    output: dict[str, bytes] = {}
    for resource in CHANGED_PATHS:
        candidate = rebuild_packed_msggame(before[resource], replacements[resource])
        if len(candidate) != TARGET_SIZES[resource] or sha256_bytes(candidate) != TARGET_SHA256[resource]:
            raise Wave23Error(f"candidate packed output differs: {resource}")
        validate_raw_roundtrip(candidate, f"Wave 23 {resource}")
        output[resource] = candidate
    validate_output_records(before, output)
    target_hashes = {**INPUT_SHA256, **{resource: sha256_bytes(data) for resource, data in output.items()}}
    target_sizes = {**INPUT_SIZES, **{resource: len(data) for resource, data in output.items()}}
    if target_hashes != TARGET_SHA256 or target_sizes != TARGET_SIZES:
        raise Wave23Error("candidate output profile is not pinned")
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "platform": "Steam PC private candidate only",
            "predecessor": "complete Wave 22 eleven-file candidate",
            "wave22_full_profile_required": True,
            "pristine_pc_japanese_read": True,
            "pc_pk_en_sc_tc_context_read": True,
            "active_pc_jp_font_read": True,
            "font_fallback_allowed": False,
            "switch_korean_read": False,
            "steam_game_resource_written": False,
            "steam_apply_capability": "absent",
            "git_operation": "absent",
            "release_operation": "absent",
        },
        "predecessor_candidate": input_root.relative_to(REPO).as_posix(),
        "wave22_evidence": wave22_evidence,
        "input_sha256": INPUT_SHA256,
        "input_sizes": INPUT_SIZES,
        "target_sha256": TARGET_SHA256,
        "target_sizes": TARGET_SIZES,
        "pc_reference_sha256": reference_hashes,
        "font": {"resource": "RES_JP/res_lang.bin", "sha256": FONT_SHA256, "outer_entry": FONT_OUTER_ENTRY, "table": FONT_TABLE, "fallback": "forbidden"},
        "families": [
            {
                "name": family.name,
                "base_coordinate": f"{family.base_coordinate[0]}:{family.base_coordinate[1]}",
                "pk_coordinate": f"{family.pk_coordinate[0]}:{family.pk_coordinate[1]}",
                "retain_literal_text": family.retain_literal_text,
                "pc_base_jp": record_report(references["BASE_JP"][family.base_coordinate]),
                "pc_pk_jp": record_report(references["PK_JP"][family.pk_coordinate]),
                "pc_pk_contexts": {language: record_report(references[language][family.pk_coordinate]) for language in ("EN", "SC", "TC")},
                "rationale": family.rationale,
            }
            for family in FAMILIES
        ],
        "records": rows,
        "changed_record_count": len(rows),
        "retain_pair_count": sum(family.retain_literal_text for family in FAMILIES),
    }
    return output, audit


def require_tmp(path: Path, label: str) -> Path:
    root = TMP_ROOT.resolve(strict=False)
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave23Error(f"{label} must stay below {root}") from exc
    return resolved


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def verify_private_candidate(candidate_root: Path) -> None:
    candidate_root = require_tmp(candidate_root, "candidate root")
    assert_profile(candidate_root, TARGET_SHA256, TARGET_SIZES, "Wave 23 private candidate")
    output = {resource: (candidate_root / resource).read_bytes() for resource in CHANGED_PATHS}
    before = {resource: (PREDECESSOR_ROOT / resource).read_bytes() for resource in CHANGED_PATHS}
    for resource, packed in output.items():
        validate_raw_roundtrip(packed, f"Wave 23 private {resource}")
    validate_output_records(before, output)


def _remove_stage(stage: Path) -> None:
    if not stage.exists():
        return
    try:
        stage.resolve().relative_to(TMP_ROOT.resolve(strict=False))
    except ValueError as exc:
        raise Wave23Error("refusing to remove stage outside Wave 23 tmp root") from exc
    shutil.rmtree(stage)


def build_candidate(input_root: Path, output_root: Path, audit_path: Path, manifest_path: Path) -> dict[str, Any]:
    input_root = require_predecessor_root(input_root)
    output_root = require_tmp(output_root, "candidate output")
    audit_path = require_tmp(audit_path, "audit output")
    manifest_path = require_tmp(manifest_path, "manifest output")
    if output_root.exists() or audit_path.exists() or manifest_path.exists():
        raise Wave23Error("candidate output, audit, or manifest already exists")
    output, audit = prepare_candidate(input_root)
    output_root.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.", dir=output_root.parent))
    try:
        require_tmp(stage, "candidate stage")
        for relative in PROFILE_PATHS:
            destination = stage / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if relative in output:
                destination.write_bytes(output[relative])
            else:
                shutil.copy2(input_root / relative, destination)
        assert_profile(stage, TARGET_SHA256, TARGET_SIZES, "Wave 23 private staging")
        os.replace(stage, output_root)
        verify_private_candidate(output_root)
        audit_bytes = (json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
        atomic_write(audit_path, audit_bytes)
        manifest = {
            "schema": SCHEMA,
            "transaction_id": "pc-dialogue-quality-wave23-static-inflection-v1",
            "candidate_only": True,
            "predecessor_candidate": input_root.relative_to(REPO).as_posix(),
            "profile_paths": list(PROFILE_PATHS),
            "changed_paths": list(CHANGED_PATHS),
            "coordinates": [f"{BASE_MSGGAME}:{family.base_coordinate[0]}:{family.base_coordinate[1]}" for family in FAMILIES] + [f"{PK_MSGGAME}:{family.pk_coordinate[0]}:{family.pk_coordinate[1]}" for family in FAMILIES],
            "input_sha256": INPUT_SHA256,
            "input_sizes": INPUT_SIZES,
            "output_sha256": TARGET_SHA256,
            "output_sizes": TARGET_SIZES,
            "pinned_output_sha256": TARGET_SHA256,
            "audit_sha256": sha256_bytes(audit_bytes),
            "record_count": len(FAMILIES) * 2,
            "retain_pair_count": sum(family.retain_literal_text for family in FAMILIES),
            "steam_write_capability": "absent",
            "steam_apply_capability": "absent",
            "git_operation": "absent",
            "release_operation": "absent",
            "real_game_qa_required_before_release": True,
        }
        atomic_write(manifest_path, (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
        return manifest
    except Exception:
        _remove_stage(stage)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    hash_parser = sub.add_parser("hash", help="verify the in-memory candidate")
    hash_parser.add_argument("--input-root", type=Path, default=PREDECESSOR_ROOT)
    verify_parser = sub.add_parser("verify-private", help="verify a private Wave 23 candidate")
    verify_parser.add_argument("--candidate-root", type=Path, required=True)
    build_parser = sub.add_parser("build", help="write only below this workstream tmp root")
    build_parser.add_argument("--input-root", type=Path, default=PREDECESSOR_ROOT)
    build_parser.add_argument("--output-root", type=Path, default=TMP_ROOT / "candidate")
    build_parser.add_argument("--audit-path", type=Path, default=TMP_ROOT / "audit.v1.json")
    build_parser.add_argument("--manifest-path", type=Path, default=TMP_ROOT / "build_manifest.v1.json")
    args = parser.parse_args(argv)
    try:
        if args.command == "hash":
            _output, audit = prepare_candidate(args.input_root)
            print(json.dumps({"status": "ok", "target_sha256": audit["target_sha256"], "changed_record_count": audit["changed_record_count"], "steam_write_capability": "absent"}, ensure_ascii=False, indent=2, sort_keys=True))
            return 0
        if args.command == "verify-private":
            verify_private_candidate(args.candidate_root)
            print(json.dumps({"status": "ok", "candidate_root": str(args.candidate_root), "steam_write_capability": "absent"}, ensure_ascii=False, sort_keys=True))
            return 0
        manifest = build_candidate(args.input_root, args.output_root, args.audit_path, args.manifest_path)
        print(json.dumps({"status": "ok", "manifest": manifest, "steam_write_capability": "absent"}, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, Wave23Error) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
