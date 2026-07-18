#!/usr/bin/env python3
"""Build the private, PC-only Wave 22 static-dialogue candidate.

The unique Korean input is the complete eleven-file Wave 20 private text
bundle.  Wave 22 reconstructs thirteen reviewed Base/PK dialogue families
(twenty-six records) and removes only their complete Japanese ``01 43``
morphology commands.  It never writes a Steam resource, original game file,
Git state, release, or network resource; output is confined to this
workstream's private ``tmp`` directory.
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
PREDECESSOR_ROOT = REPO / "tmp" / "pc_text_quality_wave20_bundle_v1" / "candidate-v1"
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


SCHEMA = "nobu16.kr.pc-dialogue-quality-wave22-static-inflection.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave22-static-inflection-audit.v1"
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
WIDE_SCRIPT_RE = re.compile(r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u9fff\uac00-\ud7a3\uf900-\ufaff]")

# Wave 20 is deliberately a complete eleven-file preimage, not a current
# Steam directory.  Its bundle evidence is pinned in addition to all files.
WAVE20_MANIFEST_SHA256 = "8FC52535D8B6AD50D12279355AF17410377A12C55E17A70455F613BBC871B6BB"
WAVE20_AUDIT_SHA256 = "81F4523A0FD0F6B5392128C0F9B4C1C6E02C2CDEE3C03A1F094D740678F078F1"
WAVE20_MANIFEST_SIZE = 3_645
WAVE20_AUDIT_SIZE = 11_850
INPUT_SHA256 = {
    "MSG/JP/ev_strdata.bin": "BF224468BFBCF3CC71DFF4609142A60D75091813281EE6F2333645413AD81B80",
    BASE_MSGGAME: "C00B78165B06A5A9D2BFBE134E847E4B00EC3E5243EE9A1981BA1BB68CFA79C6",
    "MSG/JP/strdata.bin": "6E7DD096A999299C43A9A23D9E99F75C81D6A9C8116488EC541A43423871B933",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    "MSG_PK/JP/msgdata.bin": "73CF194E4EF81C20692A245DAC75C3B2A9FCF1A997B7F6755D89DBB59149F2ED",
    "MSG_PK/JP/msgev.bin": "D922E7C2B0BD4078A5DB14C87973ECB7BB1A62A4CA2EA30A03A231AB40C1E86B",
    PK_MSGGAME: "0C3C2196E59BCBC1A066DF7097B37C281F8A6236DE70876CCD7BCAB44459BEA9",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}
INPUT_SIZES = {
    "MSG/JP/ev_strdata.bin": 928_123,
    BASE_MSGGAME: 1_504_671,
    "MSG/JP/strdata.bin": 957_204,
    "MSG_PK/JP/msgbre.bin": 484_068,
    "MSG_PK/JP/msgdata.bin": 496_995,
    "MSG_PK/JP/msgev.bin": 994_727,
    PK_MSGGAME: 1_806_775,
    "MSG_PK/JP/msgire.bin": 23_128,
    "MSG_PK/JP/msgstf.bin": 17_341,
    "MSG_PK/JP/msgstf_ce.bin": 18_767,
    "MSG_PK/JP/msgui.bin": 122_733,
}
TARGET_SHA256 = {
    **INPUT_SHA256,
    BASE_MSGGAME: "3F24BD0767813552DE13D06076BB2D2360FF59FF6E081C886BFBC9525819B453",
    PK_MSGGAME: "C7B879D9C88748D7BF9DDA4B9B492C1CE6F9ABC452C6A490B4E593CC5A4E302D",
}
TARGET_SIZES = {
    **INPUT_SIZES,
    BASE_MSGGAME: 1_504_711,
    PK_MSGGAME: 1_806_815,
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


class Wave22Error(ValueError):
    """A pinned input, anchor, byte-preservation, or tmp-output guard failed."""


@dataclass(frozen=True)
class RecordSpec:
    sha256: str
    size: int
    opaque_spans_hex: tuple[str, ...]
    morphology_commands_hex: tuple[str, ...] = ()


@dataclass(frozen=True)
class Family:
    name: str
    base_coordinate: tuple[int, int]
    pk_coordinate: tuple[int, int]
    target_literals: tuple[str, ...]
    base_preimage: RecordSpec
    pk_preimage: RecordSpec
    base_jp: RecordSpec
    pk_jp: RecordSpec
    en: RecordSpec
    sc: RecordSpec
    tc: RecordSpec
    target: RecordSpec
    target_font_widths_px: tuple[int, ...]
    rationale: str


@dataclass(frozen=True)
class Hold:
    name: str
    base_coordinate: tuple[int, int]
    pk_coordinate: tuple[int, int]
    reason: str


def spec(sha256: str, size: int, spans: tuple[str, ...], commands: tuple[str, ...] = ()) -> RecordSpec:
    return RecordSpec(sha256, size, spans, commands)


def _ko(value: str) -> str:
    """Keep target source robust to a Windows console code page."""

    return value.encode("ascii").decode("unicode_escape")


# Whole-record SHA-256 values pin every literal and opaque byte at its exact
# coordinate.  Context-language anchors use the matching PK coordinate.
FAMILIES = (
    Family(
        "farewell_good_news", (2, 557), (2, 574),
        (_ko(r"\ubc30\uc6c5\ud574 \uc8fc\uc154\uc11c \uac10\uc0ac\ud558\uc624"), _ko(r".\n\uc88b\uc740 \uc18c\uc2dd\uc744 \uae30\ub2e4\ub824 \uc8fc\uc2dc\uc624.")),
        spec("00DACCEAC24370B8BACD8E00EB7235EF1F5A70FDE44677FDB27F0A1F035A6D55", 67, ("014384040000", "014336040000", "014342010000050505"), ("014384040000", "014336040000", "014342010000")),
        spec("1A9A66F4365516A1DF6E3E35874C76F19B742ACBCAF71D4AD3AA4A9DA37A3AD4", 67, ("014390040000", "014342040000", "014342010000050505"), ("014390040000", "014342040000", "014342010000")),
        spec("0B88274BD1AA7550E5311823B4FA3E7A3DDC67F8502C4855B7D75EBDCCA58E3B", 63, ("014384040000", "014336040000", "014342010000050505"), ("014384040000", "014336040000", "014342010000")),
        spec("15ACC8B8F735E8A6CA40E374955ABFEF37B63B8E5834D8612559C4963400C2F6", 63, ("014390040000", "014342040000", "014342010000050505"), ("014390040000", "014342040000", "014342010000")),
        spec("BC57E4346B000AC2BAAA858ED4990F0D62CF8B8FD0B8A54936B094A44F79D010", 153, ("", "050505")),
        spec("60EEE0D6CBD0A8BF05D538FF935A2D58E9064C1F67828C87C28DBCF5376EBBBA", 43, ("", "050505")),
        spec("A3F4F7D72EFACF0ED48B57F245E664AC3B5C8B2F99C56C66FD33941B67E24C86", 45, ("", "050505")),
        spec("60727508EC4E6B8A5A542DBC1312D81CA817EA14BB98170D71BFF7A1FB90C7AD", 73, ("", "", "050505")),
        (552, 624), "Farewell thanks and a promise of good news are complete statements.",
    ),
    Family(
        "territory_development", (6, 4151), (6, 4181),
        (_ko(r"\uc8fc\uc704\uc5d0 \uacf5\ub7b5\ud560 \uc131\uc774 \uc5c6\uc5b4\n\uc601\ub0b4 \ubc1c\uc804\uc5d0 \ud798\uc4f0\uace0 \uc788\uc2b5\ub2c8\ub2e4."), _ko(r"\n\ubaa8\ub4e0 \ucde8\ub77d\uc740 \uc774\ubbf8 \uc7a5\uc545\ud588\uc2b5\ub2c8\ub2e4.")),
        spec("25E6BB3F1D2765D9167A06945AD146E278D930D7D334E7E8962905863AB83100", 117, ("", "014390010000", "0143140200000143F6010000050505"), ("014390010000", "014314020000", "0143F6010000")),
        spec("BCAF8DEB664747EFDAE15410B6269E20C60BFF7C80754FF64FCF5627B97537BF", 117, ("", "014396010000", "01431A0200000143FC010000050505"), ("014396010000", "01431A020000", "0143FC010000")),
        spec("65995076C361ED576098AF6404CD268E2807179D7F9C12B9ADF6A5449E940CCD", 103, ("", "014390010000", "0143140200000143F6010000050505"), ("014390010000", "014314020000", "0143F6010000")),
        spec("81B8E7B7A5E7E7E4656154F3ED07E779C01B0B5D354A19F1EB41469368E8EB4E", 103, ("", "014396010000", "01431A0200000143FC010000050505"), ("014396010000", "01431A020000", "0143FC010000")),
        spec("AE06B432EA91898B80749F9AE85C07719BEB923BEEF4CF1110E4A109243947A0", 283, ("", "050505")),
        spec("3122441A8CBDC1870F629543A5C38FCC194739CF9C6E5A388385533713D64316", 75, ("", "050505")),
        spec("FCD980494CDAF38EAB48C7F57C9E8D603811A09F22528E1A5803077E6534ED25", 77, ("", "050505")),
        spec("A0A6BA9376E6CCD5609452C5362B9DEA801DFEE190952BF090438032313BF8A2", 111, ("", "", "050505")),
        (552, 672, 720), "No nearby castle remains; development and settlement control are complete.",
    ),
    Family(
        "orders_worthy_result", (6, 4178), (6, 4208),
        (_ko(r"\uc54c\uaca0\uc2b5\ub2c8\ub2e4."), _ko(r"\n\ubc18\ub4dc\uc2dc \uc8fc\uba85\uc5d0 \uac78\ub9de\uc740 \uc131\uacfc\ub97c\n\uac00\ubb38\uc5d0 \uac00\uc838\uc624\uaca0\uc2b5\ub2c8\ub2e4.")),
        spec("E6126FBB6BD78DD5F95B100F214E2089544A8252D363558B6FFDF29E89A62D15", 77, ("", "014368020000", "01437E040000050505"), ("014368020000", "01437E040000")),
        spec("0C1D2DBF12CC1345D3F9FEF19B9634259B2CCF545231DABE0BB775500627954D", 77, ("", "014374020000", "01438A040000050505"), ("014374020000", "01438A040000")),
        spec("7AE5684F0822E44E118FD911B55F05631A8850322FC93DD3AE5EAEDF702A560E", 67, ("", "014368020000", "01437E040000050505"), ("014368020000", "01437E040000")),
        spec("8B501A428C1C71F7D7DA61BA1B9357745A2FB52D88DE2B62FCA68C35B62967B7", 67, ("", "014374020000", "01438A040000050505"), ("014374020000", "01438A040000")),
        spec("A0B7894AA09C3D382121B90AA1A1E5283AF2A4115800B9BA2D4A2DB03129AB4B", 147, ("", "050505")),
        spec("64A9DD6C482C690CB472FFEF885AB82F67CC2E28F7AB7F8F48947937B258DCBF", 51, ("", "050505")),
        spec("C80FE080BD466DEE7A3911A7B6215E84CCB443D7EB2C3E6D84B3D74D335FE4BF", 49, ("", "050505")),
        spec("DA279492AD29C0951C7DE9159777B47880EA8BD0169FE97D82626939080EE5A1", 85, ("", "", "050505")),
        (264, 648, 528), "The speaker acknowledges an order and vows a result worthy of it.",
    ),
    Family(
        "clan_order_pledge", (6, 4179), (6, 4209),
        (_ko(r"\uc54c\uaca0\uc2b5\ub2c8\ub2e4."), _ko(r"\n\ub2f9\uac00\ub97c \uc704\ud574 \uc8fc\uba85\uc744 \uc644\uc218\ud558\uace0\uc790\n\uc804\ub825\uc744 \ub2e4\ud558\uaca0\uc2b5\ub2c8\ub2e4.")),
        spec("A352A9A5A5C3BEE704C68C1B0C1E6287E0D66F6304971B8894A7FD23A5A05A19", 87, ("014352030000", "014314020000", "0143B4010000050505"), ("014352030000", "014314020000", "0143B4010000")),
        spec("34587BD5C9A80C69C98538E18FA29A71F154594218411DF6EBE01F33F6790A6C", 87, ("01435E030000", "01431A020000", "0143BA010000050505"), ("01435E030000", "01431A020000", "0143BA010000")),
        spec("AAC8098355E223226D7925B36975BF88C79187A7F9D66D5CE09910F2C0DB2440", 83, ("014352030000", "014314020000", "0143B4010000050505"), ("014352030000", "014314020000", "0143B4010000")),
        spec("4A8AAE9F13FC6025AFDB7C0ED42A3B2CF48531F8F77A9D3F0A9C09D012840F29", 83, ("01435E030000", "01431A020000", "0143BA010000050505"), ("01435E030000", "01431A020000", "0143BA010000")),
        spec("68C3D08699C7666DE3C001982C2DAE6AB7E676D26E0955C5B3CB0C589AAC3343", 201, ("", "050505")),
        spec("E2D64CCE173C5243A5696E5D572D6116E6D7A8C952721AC9AEDD74D6E4C6D383", 49, ("", "050505")),
        spec("D902B02099DA565809AEC6A1C936F72F75010D249E2FFB4CB90A26FB01473144", 57, ("", "050505")),
        spec("F7DF9C39FEFDD1CD471E801330D1AB90A61689295575E5EFA60ED7D7CDB9377D", 85, ("", "", "050505")),
        (264, 696, 480), "The speaker will give everything to fulfil the lord's order for the clan.",
    ),
    Family(
        "enemy_castle_stratagem", (6, 4181), (6, 4211),
        (_ko(r"\uc801\uc131 \uacf5\ub7b5\uc758 \ub73b\uc744 \uac01 \uc131\uc8fc\uc5d0\uac8c \uc804\ud588\ub354\ub2c8\n\ub2e4\uc74c \uc131\uc5d0\uc11c \uad6c\uccb4\uc548\uc774 \ub098\uc654\uc2b5\ub2c8\ub2e4."), _ko(r"\n\uc5b4\ub290 \uc131\uc8fc\uc758 \uacc4\ucc45\uc744 \uc4f8\uc9c0"), _ko(r" \uba85\ud574 \uc8fc\uc2ed\uc2dc\uc624.")),
        spec("E4D4C662FB124798286B761EFB1ACBB50DD1064F526CA8D1F6A3995F52CE6768", 153, ("", "014314020000", "01438A040000", "0143BE000000050505"), ("014314020000", "01438A040000", "0143BE000000")),
        spec("2573885533B11CBAE65B993F214BFA7B1618387769EDBEA4169E255EFF2B7432", 153, ("", "01431A020000", "014396040000", "0143BE000000050505"), ("01431A020000", "014396040000", "0143BE000000")),
        spec("E0CF8E46A50F1AA43D36E9BB0376F434DA09B3074D0423828FE591760625D860", 133, ("", "014314020000", "01438A040000", "0143BE000000050505"), ("014314020000", "01438A040000", "0143BE000000")),
        spec("722760937B0DDAA5CCE817E8B7C426A7E021E0F9CAB2B3F018953666AC48CFCF", 133, ("", "01431A020000", "014396040000", "0143BE000000050505"), ("01431A020000", "014396040000", "0143BE000000")),
        spec("BCD7F1972023999BA6EFDA0A39365A1545EE5539D08243196B430A4EF8232AEC", 375, ("", "050505")),
        spec("1851A26DA7D2F2B4A36B15EA61F0D4B199E12706C500F2A52CF9DE51E8173647", 103, ("", "050505")),
        spec("7B53BF551C915EB61818C24BFE6B1586132EDF92099FC44E8D7949C6B1A8B38A", 113, ("", "050505")),
        spec("EC8E017EA6AB1D0440E8F1BCFCAAC326FE9FAD686BA2533D815089E918A04D6A", 147, ("", "", "", "050505")),
        (888, 768, 912), "Each castle lord supplied a concrete stratagem; the player must choose one.",
    ),
    Family(
        "acknowledgement", (6, 4391), (6, 4450),
        (_ko(r"\uc54c\uaca0\uc2b5\ub2c8\ub2e4."),),
        spec("1B773DBF1BE2EB828648986772F70B434FA34EA65F2166178B7D6CAC4F60F8C2", 21, ("", "014314020000050505"), ("014314020000",)),
        spec("BC3483C1C848A227F3FA30D05E43DC4FDF64102F107BAB01DACD0E01391B7207", 21, ("", "01431A020000050505"), ("01431A020000",)),
        spec("B8A00BD696D28F4A1B6C48D9BD03BB2E4D7C702C53D6B5AD9E5752D3E39611E3", 25, ("", "014314020000050505"), ("014314020000",)),
        spec("D55DE367ED9B008C67B9C96EFD2184C44E723E9F04B3F411B88B0F63A362A43F", 25, ("", "01431A020000050505"), ("01431A020000",)),
        spec("F6E362EFCE2E29F9CD952912C14F38F8C97052A0965039C1E6A0C293BB24A0CB", 31, ("", "050505")),
        spec("1BD0D6A536294E3249D7F637D5C0D3F1280FCD9384B4EFD99F42F34FF32C8919", 17, ("", "050505")),
        spec("9D99A63200C116D3327226225697248B8D3EF7AC0A3B1A47CBA7DD1906A1F30B", 13, ("", "050505")),
        spec("ECD96BA5816E51B04DDB3671B476F8B010FC0053EA66F84FB7BFA73E52A7D61B", 21, ("", "050505")),
        (264,), "All PC languages are a concise acknowledgement.",
    ),
    Family(
        "start_after_mission_and_battle", (6, 4392), (6, 4451),
        (_ko(r"\uc54c\uaca0\uc2b5\ub2c8\ub2e4."), _ko(r"\n\uc784\ubb34\uc640 \uc804\ud22c\uac00 \ub05d\ub098\ub294 \ub300\ub85c\n\ucc29\uc218\ud558\uaca0\uc2b5\ub2c8\ub2e4.")),
        spec("106F9356EDF3AAB18535AE3E775C2BE64E93C9671284C8ECEA93065FFA79B599", 69, ("", "014314020000", "0143CC010000050505"), ("014314020000", "0143CC010000")),
        spec("0BF73259DA5DF01E67BF66F35B354C17194598B32215DC31ED3D8120A602B6FA", 69, ("", "01431A020000", "0143D2010000050505"), ("01431A020000", "0143D2010000")),
        spec("88AB6E09C73C56219A9891037DA75D8E179A945DB840300DEEE0F87695847516", 65, ("", "014314020000", "0143CC010000050505"), ("014314020000", "0143CC010000")),
        spec("C9EB8B415CF45D738C30DB05DBCE03C861CA394CCEC16DB06A7FF80781195B6A", 65, ("", "01431A020000", "0143D2010000050505"), ("01431A020000", "0143D2010000")),
        spec("4167EA710E92499739B4CCCCF8EFCEBD754085235D80F5F4037FA0A9B38001DB", 159, ("", "050505")),
        spec("90701E2050AFF79033EE3A26F39D4173E9D94F109858EFCDF7473F4646960117", 51, ("", "050505")),
        spec("D5EBF49ED67598074D7C61A96F14F2F1D77E0B4B7ECADD7DE3F737E2ED3A1E4A", 53, ("", "050505")),
        spec("C40FD2DB890445807C5D58B5912FE85EB12317A0C9196FB43272A40EBE06A04C", 75, ("", "", "050505")),
        (264, 600, 360), "Work begins once both the mission and battle have concluded.",
    ),
    Family(
        "start_after_return_from_battle", (6, 4393), (6, 4452),
        (_ko(r"\uc54c\uaca0\uc2b5\ub2c8\ub2e4."), _ko(r"\n\uc804\ud22c\uc5d0\uc11c \ub3cc\uc544\uc624\ub294 \ub300\ub85c\n\ucc29\uc218\ud558\uaca0\uc2b5\ub2c8\ub2e4.")),
        spec("3F023D9ECC15E0FABFB989350129B4F12B1E01AE7E6FA1B9F4AA1C76B1E2AEB1", 65, ("", "014314020000", "0143CC010000050505"), ("014314020000", "0143CC010000")),
        spec("5E7CF9B6D4E3FE6DC35C5D299C991DA90E71C0E010121234933DABA9F26D20C1", 65, ("", "01431A020000", "0143D2010000050505"), ("01431A020000", "0143D2010000")),
        spec("334E734695ECD7100AE1B771DDA6EA2BB228D05E5F930716E0ECAD01E74E0E16", 59, ("", "014314020000", "0143CC010000050505"), ("014314020000", "0143CC010000")),
        spec("228B0224CE57A0D90DCBBA96F82471ACFB8B985A9E1E3C7C11D2BBAEB8C0CB62", 59, ("", "01431A020000", "0143D2010000050505"), ("01431A020000", "0143D2010000")),
        spec("C8D53AA60F46B6B3CF76D60FE23FE184E47AFAA2042D11E00FDF935AE08A058B", 149, ("", "050505")),
        spec("1D684D6BAFE8413E041726E77D795B4B08D8D4EAFE2213245DB56D00C434D9B3", 47, ("", "050505")),
        spec("8598F3F617E6B90F2611DB480048D15F4D1583D657D0EF5C9E5BBFEF4D5FEC93", 39, ("", "050505")),
        spec("3D4933B4FD7BDFBD0CB17BBD66DED4616DD2C4EEE5880DD7B271C904F1E1F6EB", 71, ("", "", "050505")),
        (264, 528, 360), "Work begins immediately after the speaker returns from battle.",
    ),
    Family(
        "start_after_mission", (6, 4394), (6, 4453),
        (_ko(r"\uc54c\uaca0\uc2b5\ub2c8\ub2e4."), _ko(r"\n\uc784\ubb34\ub97c \ub9c8\uce58\ub294 \ub300\ub85c\n\ucc29\uc218\ud558\uaca0\uc2b5\ub2c8\ub2e4.")),
        spec("BB7EB773230F8A58285A9CB9A9434D5F14A9A44CB16C0A68B21B13E5F224442F", 63, ("", "014314020000", "0143CC010000050505"), ("014314020000", "0143CC010000")),
        spec("72D6850D798F6B8A39A87088418F7BB06E75F11937083DEE57AF150871ED7E78", 63, ("", "01431A020000", "0143D2010000050505"), ("01431A020000", "0143D2010000")),
        spec("FCD215409212E7E0D4C3712C85344281D5D2B5166A95B4BCF8D2B20FF6D4CEAC", 59, ("", "014314020000", "0143CC010000050505"), ("014314020000", "0143CC010000")),
        spec("78E6964945F4140B1FBC2395E0B60FB2BCF6CE45B1CFAF13E19B3DE6DE27AF59", 59, ("", "01431A020000", "0143D2010000050505"), ("01431A020000", "0143D2010000")),
        spec("7F8AB09E3BD8FF5780B628DA04F5A41FC2D7B0D5EE01C424416582FB90F13E32", 139, ("", "050505")),
        spec("A500AD422F51367BF489B8C8A89A337AC62F4E13BCD1C1FA935656DB134B2C49", 45, ("", "050505")),
        spec("2A5B42529E06DE6D79F7F84F67691AB704A495B9237F2EC7B7DF2043F9DE5229", 37, ("", "050505")),
        spec("DB89E9ECB11C9492CAC260D2C19ADD937147E6FA89D368DB72F02E18B8C6E1A4", 67, ("", "", "050505")),
        (264, 432, 360), "Work begins as soon as the mission ends.",
    ),
    Family(
        "spear_recruitment_reconsider", (6, 4404), (6, 4463),
        (_ko(r"\uacfc\uc5f0, \ucc3d\uc744 \ub2e4\ub8f0 \uc774\ub97c"), _ko(r" \uc6d0\ud558\uc2dc\ub294\uad70\uc694."), _ko(r"\n\ud558\uc9c0\ub9cc\u2026 \uc778\uc120\uc740 \uc7ac\uace0\ud574 \uc8fc\uc2ed\uc2dc\uc624.")),
        spec("4E25FAC2ACA298534761CC8834BF1E08FA9BCD1660FFB0B4394810236343A89B", 91, ("", "01438A040000", "01430C010000", "0143BE000000050505"), ("01438A040000", "01430C010000", "0143BE000000")),
        spec("2A06629895AA349359F4772944742518B946CBDE771015F3EC99FE0DFD066B1A", 91, ("", "014396040000", "01430C010000", "0143BE000000050505"), ("014396040000", "01430C010000", "0143BE000000")),
        spec("0DB59BED0DBF63782D35A86445EB376DEDEA27593CA1B0505F5DF8378EBEB02D", 85, ("", "01438A040000", "01430C010000", "0143BE000000050505"), ("01438A040000", "01430C010000", "0143BE000000")),
        spec("8501D0296E5C4B6C68CE42012307716D83C4EA88B8CB339EB812E6FBE8C7DDEF", 85, ("", "014396040000", "01430C010000", "0143BE000000050505"), ("014396040000", "01430C010000", "0143BE000000")),
        spec("590CC4A7304B3DA67113B36AC50EE76F669FCBA623E3FD07E28C4774A4A27610", 297, ("", "050505")),
        spec("04FE91C55FE4E73B37C9EE97499855F49A1CA0646581A53DE5C0C33A995883CA", 73, ("", "050505")),
        spec("CCB5C6FB4BF1589BE346787174CCCD453F31B7A98CC85A5633E04A5812286178", 79, ("", "050505")),
        spec("A2F0A01903016F56D6D1EDA83DCD7C3B0A9696F6C6B8F95A29D4260168E4DF40", 99, ("", "", "", "050505")),
        (816, 768), "A spear specialist asks that the proposed appointment be reconsidered.",
    ),
    Family(
        "rear_service_landholder", (6, 4439), (6, 4498),
        (_ko(r"\ud6c4\ubc29\uc5d0\uc11c \ubc31\uc131\uc744 \uc12c\uae30\ub294 \uac83\uc774 \ubcf8\ubd84\uc774\uc624.\n\ubd80\ub514 \uc601\uc8fc\ub85c \uc784\uba85\ud574 \uc8fc\uc2dc\uc624."),),
        spec("7D36566C866724DC0092FD3B5FDA3C9A3330F5F49C095AFC9BE335CB957F4D1D", 77, ("", "014342010000050505"), ("014342010000",)),
        spec("7D36566C866724DC0092FD3B5FDA3C9A3330F5F49C095AFC9BE335CB957F4D1D", 77, ("", "014342010000050505"), ("014342010000",)),
        spec("CFB9228F617E0F818233AEAE0C359C9D5F7603EADD7F7AEC3C2359DAA3DC63BF", 65, ("", "014342010000050505"), ("014342010000",)),
        spec("CFB9228F617E0F818233AEAE0C359C9D5F7603EADD7F7AEC3C2359DAA3DC63BF", 65, ("", "014342010000050505"), ("014342010000",)),
        spec("DC8657899E433612C90B29EE96CF39FD6B741E1405C702CA32C8B8EAD916EBAE", 235, ("", "050505")),
        spec("6FAFC398C9BBFAF019A0279ABAA037E2AADBC67C833977BE311F294F7E3B441B", 63, ("", "050505")),
        spec("324A1F04DAC233F48640D9E1AC78251D41C2AA201883CE3D6FBEA0848FCC7F89", 63, ("", "050505")),
        spec("DAA15636C17D2C12CFBA62637F238805CC64C773C7213B620D11CDB84246FD54", 83, ("", "050505")),
        (888, 624), "The speaker asks to serve the people as a landholder away from battle.",
    ),
    Family(
        "serve_clan_anywhere", (6, 4456), (6, 4515),
        (_ko(r"\uc5b4\ub290 \ub545\uc5d0\uc11c\ub4e0 \ub2f9\uac00\ub97c \uc704\ud574\n\uc804\ub825\uc744 \ub2e4\ud558\uaca0\uc2b5\ub2c8\ub2e4."),),
        spec("4C330E8FA9CBF42AE88CBFD5AA3E87A8A191EA77034D2A341009759EC1F36C13", 63, ("", "01432C020000050505"), ("01432C020000",)),
        spec("4EF8825AC77AB815A2E00E7EA5E7C8444D06F9636305A95E1260A16965F1AAC0", 63, ("", "014338020000050505"), ("014338020000",)),
        spec("51B26E59AC4910BB043979D8DB847CB206FAD0A6395A835BC23512569CE913AC", 57, ("", "01432C020000050505"), ("01432C020000",)),
        spec("F3872F9AA4B99A36B6B07E2905D70460D4C6F17A0147356E308D5F2F011A25CA", 57, ("", "014338020000050505"), ("014338020000",)),
        spec("EA0AE4534251288E9844DA8D89ED3D32BAACCB14911AC83A817FAEB312E64AD1", 179, ("", "050505")),
        spec("CB9FE5FF91A9CA1860E660AC5CD8C81CAFD1C0123A6607F3AAABA5D4C010B17D", 43, ("", "050505")),
        spec("3568B78BE170DB0C56E86EF1D66EAD78A919361D420047212C725D86B6163A2B", 43, ("", "050505")),
        spec("7B101122BE2A8859A8681EA8F2A2E412437C45CFF64B7291DB841C876519A7DD", 61, ("", "050505")),
        (600, 480), "The speaker will serve the clan with all strength in any land.",
    ),
    Family(
        "dismissal_reconsider", (6, 4460), (6, 4519),
        (_ko(r"\ud639\uc2dc \uc800\ub97c \ud574\uc784\ud558\ub824 \ud558\uc2ed\ub2c8\uae4c?"), _ko(r"\n\ubd80\ub514"), _ko(r" \ub2e4\uc2dc \uc0dd\uac01\ud574 \uc8fc\uc2ed\uc2dc\uc624\u2026")),
        spec("4279F42286E06C5297DFFB7AB71D7EC3D60D1101DE0011AF69ADC6B6BB32964C", 69, ("", "014324010000", "014384040000", "050505"), ("014324010000", "014384040000")),
        spec("4592B916D1036C599C3CD712EEEF60198752740DCABC04E0F69FD235E35E5B0B", 69, ("", "014324010000", "014390040000", "050505"), ("014324010000", "014390040000")),
        spec("55CA2B9DCE129EDB9CFB93C4EE8239BC822997AC08F6C9FB80E71935D35E1084", 73, ("", "014324010000", "014384040000", "050505"), ("014324010000", "014384040000")),
        spec("37538FBC7AD491D73C90CA3F51083A422F1B8CC3A515E3DE8D2434C0B5F1BACF", 73, ("", "014324010000", "014390040000", "050505"), ("014324010000", "014390040000")),
        spec("F57ED8A681FA18672A3E995C60FD1C95DDDBD27DBF0B1165E59D67C73F53AF06", 159, ("", "050505")),
        spec("955A9EB262ED95A033C9918E356EF498C375F1D55AE552A4771C583AAF9E787C", 51, ("", "050505")),
        spec("44F7A3E6F6BB34A0E420FD04B457157B74289102CD906B810AEA2DA7DC46480C", 37, ("", "050505")),
        spec("DCB8E97031EADE4E9515589D996ED1FB9071AA3963340BBF5C79AC46A9026C00", 85, ("", "", "", "050505")),
        (672, 648), "The speaker asks whether dismissal is intended and requests reconsideration.",
    ),
)
FAMILY_BY_NAME = {family.name: family for family in FAMILIES}
if len(FAMILY_BY_NAME) != len(FAMILIES):
    raise RuntimeError("duplicate Wave 22 family")

HOLDS = (
    Hold("placeholder_hoge", (1, 21), (1, 21), "JP placeholder wording and empty PC contexts provide no semantic anchor."),
    Hold("gunner_face_fragment", (6, 2253), (6, 2259), "The subject/object between fragments is absent and context alignment is unreliable."),
    Hold("imperial_court_actor_fragment", (6, 4225), (6, 4255), "The sentence starts with an object particle; actor/context is absent."),
    Hold("civil_administration_subject", (6, 4441), (6, 4500), "The subject is unresolved and JP/Chinese versus EN viewpoint differs."),
    Hold("concurrent_post_actor", (6, 4458), (6, 4517), "A blank line, 이(가), and actor are runtime/context dependent."),
    Hold("service_recipient_fragment", (7, 263), (7, 267), "The recipient token before 을 위해 is absent."),
    Hold("offer_recipient_fragment", (7, 265), (7, 269), "The recipient token before 을 위해서라면 is absent."),
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
        spans.append(record.data[cursor:literal.marker_offset])
        cursor = literal.marker_end
    spans.append(record.data[cursor:])
    return tuple(spans)


def marker_topology(record: MsgGameRecord) -> tuple[tuple[bytes, bytes], ...]:
    return tuple(
        (
            record.data[literal.marker_offset:literal.marker_offset + len(LITERAL_START)],
            record.data[literal.marker_end - len(LITERAL_END):literal.marker_end],
        )
        for literal in parse_record_literals(record)
    )


def morphology_commands(record: MsgGameRecord) -> tuple[str, ...]:
    commands: list[str] = []
    for span in opaque_spans(record):
        cursor = 0
        while cursor < len(span):
            if span[cursor:cursor + 2] == MORPHOLOGY_PREFIX:
                if cursor + 6 > len(span):
                    raise Wave22Error("truncated 01 43 command")
                commands.append(span[cursor:cursor + 6].hex().upper())
                cursor += 6
            else:
                cursor += 1
    return tuple(commands)


def stripped_opaque_spans(record: MsgGameRecord) -> tuple[bytes, ...]:
    output: list[bytes] = []
    for span in opaque_spans(record):
        result = bytearray()
        cursor = 0
        while cursor < len(span):
            if span[cursor:cursor + 2] == MORPHOLOGY_PREFIX:
                if cursor + 6 > len(span):
                    raise Wave22Error("truncated 01 43 command")
                cursor += 6
            else:
                result.append(span[cursor])
                cursor += 1
        output.append(bytes(result))
    return tuple(output)


def strip_0143_span(span: bytes) -> bytes:
    """Remove only complete morphology commands, retaining every other byte."""

    output = bytearray()
    cursor = 0
    while cursor < len(span):
        if span[cursor:cursor + 2] == MORPHOLOGY_PREFIX:
            if cursor + 6 > len(span):
                raise Wave22Error("truncated 01 43 command")
            cursor += 6
        else:
            output.append(span[cursor])
            cursor += 1
    return bytes(output)


def profile_hashes(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for relative in PROFILE_PATHS:
        path = root / relative
        if not path.is_file():
            raise Wave22Error(f"profile resource is absent: {relative}")
        result[relative] = sha256_path(path)
    return result


def profile_sizes(root: Path) -> dict[str, int]:
    return {relative: (root / relative).stat().st_size for relative in PROFILE_PATHS}


def assert_profile(root: Path, expected_hashes: Mapping[str, str], expected_sizes: Mapping[str, int], label: str) -> None:
    actual_hashes = profile_hashes(root)
    actual_sizes = profile_sizes(root)
    if actual_hashes != dict(expected_hashes) or actual_sizes != dict(expected_sizes):
        mismatch = {
            relative: {
                "expected_sha256": expected_hashes.get(relative),
                "actual_sha256": actual_hashes.get(relative),
                "expected_size": expected_sizes.get(relative),
                "actual_size": actual_sizes.get(relative),
            }
            for relative in PROFILE_PATHS
            if actual_hashes.get(relative) != expected_hashes.get(relative)
            or actual_sizes.get(relative) != expected_sizes.get(relative)
        }
        raise Wave22Error(f"{label} profile mismatch: {json.dumps(mismatch, sort_keys=True)}")


def require_predecessor_root(path: Path) -> Path:
    expected = PREDECESSOR_ROOT.resolve(strict=True)
    resolved = path.resolve(strict=True)
    if resolved != expected:
        raise Wave22Error(f"input must be the unique Wave 20 private candidate: {expected}")
    return resolved


def validate_wave20_evidence(root: Path) -> dict[str, Any]:
    manifest_path = root / "bundle_manifest.v1.json"
    audit_path = root / "audit.v1.json"
    if (
        not manifest_path.is_file()
        or not audit_path.is_file()
        or manifest_path.stat().st_size != WAVE20_MANIFEST_SIZE
        or audit_path.stat().st_size != WAVE20_AUDIT_SIZE
        or sha256_path(manifest_path) != WAVE20_MANIFEST_SHA256
        or sha256_path(audit_path) != WAVE20_AUDIT_SHA256
    ):
        raise Wave22Error("Wave 20 bundle evidence differs")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise Wave22Error("Wave 20 bundle manifest is not JSON") from exc
    if (
        manifest.get("schema") != "nobu16.kr.pc-text-quality-wave20-bundle-manifest.v1"
        or manifest.get("profile_paths") != list(PROFILE_PATHS)
        or manifest.get("final_sha256") != INPUT_SHA256
        or manifest.get("final_sizes") != INPUT_SIZES
        or manifest.get("candidate_only") is not True
    ):
        raise Wave22Error("Wave 20 bundle manifest contract differs")
    return {
        "root": root.relative_to(REPO).as_posix(),
        "manifest_sha256": WAVE20_MANIFEST_SHA256,
        "audit_sha256": WAVE20_AUDIT_SHA256,
        "profile_sha256": INPUT_SHA256,
        "profile_sizes": INPUT_SIZES,
    }


def validate_raw_roundtrip(packed: bytes, label: str) -> None:
    header, raw = decompress_wrapper(packed)
    archive = parse_packed_msggame(packed).archive
    if rebuild_raw_msggame(archive) != raw:
        raise Wave22Error(f"{label} raw parse/rebuild differs")
    repacked = recompress_wrapper(raw, header)
    _header, rebuilt_raw = decompress_wrapper(repacked)
    if rebuilt_raw != raw:
        raise Wave22Error(f"{label} wrapper round-trip differs")


def reject_switch_path(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    if any("switch" in component.casefold() for component in resolved.parts):
        raise Wave22Error(f"Switch input is forbidden: {label}")
    return resolved


def assert_record_spec(record: MsgGameRecord, expected: RecordSpec, label: str) -> None:
    actual_spans = tuple(value.hex().upper() for value in opaque_spans(record))
    if (
        sha256_bytes(record.data) != expected.sha256
        or len(record.data) != expected.size
        or actual_spans != expected.opaque_spans_hex
        or morphology_commands(record) != expected.morphology_commands_hex
    ):
        raise Wave22Error(f"{label} whole-record invariant differs")


def record_report(record: MsgGameRecord, expected: RecordSpec) -> dict[str, Any]:
    values = literal_texts(record)
    return {
        "record_sha256": expected.sha256,
        "record_size": expected.size,
        "literals": list(values),
        "literal_utf16le_sha256": [sha256_bytes(value.encode("utf-16-le")) for value in values],
        "opaque_spans_hex": list(expected.opaque_spans_hex),
        "morphology_commands_hex": list(expected.morphology_commands_hex),
    }


def load_references() -> tuple[dict[str, dict[tuple[int, int], MsgGameRecord]], dict[str, str]]:
    archives: dict[str, dict[tuple[int, int], MsgGameRecord]] = {}
    hashes: dict[str, str] = {}
    for language, (path, expected_hash) in PC_REFERENCE_PATHS.items():
        checked = reject_switch_path(path, f"PC {language}")
        actual = sha256_path(checked)
        if actual != expected_hash:
            raise Wave22Error(f"PC {language} source hash differs")
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
                raise Wave22Error(f"{family.name} {language} anchor is absent")
            assert_record_spec(record, expected, f"{family.name} {language}")
        if literal_texts(references["BASE_JP"][family.base_coordinate]) != literal_texts(references["PK_JP"][family.pk_coordinate]):
            raise Wave22Error(f"{family.name} Base/PK JP literal tuple differs")


def validate_text(value: str, label: str) -> None:
    if not value or "\x1b" in value or "%" in value:
        raise Wave22Error(f"{label} contains a runtime marker or is empty")
    encoded = value.encode("utf-16-le")
    if LITERAL_START in encoded or LITERAL_END in encoded:
        raise Wave22Error(f"{label} encodes a reserved marker")
    for character in value:
        if character != "\n" and unicodedata.category(character) == "Cc":
            raise Wave22Error(f"{label} contains control U+{ord(character):04X}")


def line_upper_bound_px(values: tuple[str, ...]) -> tuple[int, ...]:
    return tuple(sum(24 if char == " " else 48 for char in line) for line in "".join(values).split("\n"))


def _font_u32(raw: bytes, offset: int, label: str) -> int:
    if offset < 0 or offset + 4 > len(raw):
        raise Wave22Error(f"font {label} is outside G1N")
    return struct.unpack_from("<I", raw, offset)[0]


@functools.lru_cache(maxsize=1)
def font_metric_state() -> tuple[bytes, tuple[int, ...], int, int]:
    path = reject_switch_path(FONT_RESOURCE, "active PC JP font")
    if sha256_path(path) != FONT_SHA256:
        raise Wave22Error("active PC JP font hash differs")
    try:
        archive = parse_link(path.read_bytes())
        _header, raw = decompress_wrapper(archive.entries[FONT_OUTER_ENTRY].data)
    except (IndexError, ValueError) as exc:
        raise Wave22Error("active PC JP font entry cannot be decoded") from exc
    if raw[:8] != b"_N1G0000" or _font_u32(raw, 0x08, "declared size") != len(raw):
        raise Wave22Error("active PC JP font header differs")
    table_count = _font_u32(raw, 0x1C, "table count")
    if not 1 <= table_count <= 32 or FONT_TABLE >= table_count:
        raise Wave22Error("active PC JP font table count differs")
    offsets = tuple(_font_u32(raw, 0x20 + 4 * index, f"table {index} offset") for index in range(table_count))
    atlas_offset = _font_u32(raw, 0x14, "atlas offset")
    if offsets != tuple(sorted(offsets)) or len(set(offsets)) != len(offsets):
        raise Wave22Error("active PC JP font table offsets differ")
    table_offset = offsets[FONT_TABLE]
    table_end = offsets[FONT_TABLE + 1] if FONT_TABLE + 1 < table_count else atlas_offset
    record_start = table_offset + FONT_MAP_BYTES
    if not 0 <= table_offset <= record_start <= table_end <= len(raw):
        raise Wave22Error("active PC JP font table bounds differ")
    record_bytes = table_end - record_start
    if record_bytes % FONT_RECORD_BYTES:
        raise Wave22Error("active PC JP font record alignment differs")
    record_count = record_bytes // FONT_RECORD_BYTES
    if record_count <= 0:
        raise Wave22Error("active PC JP font has no records")
    mapping = struct.unpack_from("<65536H", raw, table_offset)
    return raw, mapping, record_start, record_count


def font_advance_px(character: str) -> int:
    if len(character) != 1 or ord(character) > 0xFFFF:
        raise Wave22Error("font metric requires one BMP character")
    raw, mapping, record_start, record_count = font_metric_state()
    ordinal = mapping[ord(character)]
    if ordinal == 0:
        if WIDE_SCRIPT_RE.fullmatch(character):
            return 48
        raise Wave22Error(f"active PC JP font lacks U+{ord(character):04X}")
    if ordinal >= record_count:
        raise Wave22Error(f"active PC JP font ordinal is invalid for U+{ord(character):04X}")
    offset = record_start + ordinal * FONT_RECORD_BYTES
    width = raw[offset]
    advance = raw[offset + 4]
    if width != advance or advance not in (24, 48):
        raise Wave22Error(f"active PC JP glyph metric differs for U+{ord(character):04X}")
    return advance


def font_line_widths_px(values: tuple[str, ...]) -> tuple[int, ...]:
    result: list[int] = []
    for line in "".join(values).split("\n"):
        width = 0
        for character in line:
            if unicodedata.category(character) == "Cc":
                raise Wave22Error(f"font layout has control U+{ord(character):04X}")
            width += font_advance_px(character)
        result.append(width)
    return tuple(result)


def rebuild_static_record(source: MsgGameRecord, target_literals: tuple[str, ...]) -> bytes:
    """Replace literal text while retaining every non-0143 opaque source byte."""

    source_spans = opaque_spans(source)
    if len(source_spans) != len(target_literals) + 1:
        raise Wave22Error("target changes literal-marker count")
    payload = bytearray()
    for index, value in enumerate(target_literals):
        payload.extend(strip_0143_span(source_spans[index]))
        payload.extend(LITERAL_START)
        payload.extend(value.encode("utf-16-le"))
        payload.extend(LITERAL_END)
    payload.extend(strip_0143_span(source_spans[-1]))
    return bytes(payload)


def validate_change(family: Family, resource: str, record: MsgGameRecord) -> tuple[bytes, dict[str, Any]]:
    coordinate = family.base_coordinate if resource == BASE_MSGGAME else family.pk_coordinate
    expected = family.base_preimage if resource == BASE_MSGGAME else family.pk_preimage
    assert_record_spec(record, expected, f"input {resource} {coordinate[0]}:{coordinate[1]}")
    current_literals = literal_texts(record)
    if len(current_literals) != len(family.target_literals):
        raise Wave22Error(f"{family.name} changes literal-marker count")
    if not expected.morphology_commands_hex or not all(command.startswith("0143") and len(command) == 12 for command in expected.morphology_commands_hex):
        raise Wave22Error(f"{family.name} command guard is not a complete 01 43 sequence")
    for literal_id, value in enumerate(family.target_literals):
        validate_text(value, f"{family.name} target literal {literal_id}")
    current_text = "".join(current_literals)
    target_text = "".join(family.target_literals)
    if current_text.count("\n") != target_text.count("\n") or target_text.count("\n") + 1 > 3:
        raise Wave22Error(f"{family.name} changes manual line count or exceeds three lines")
    # The upper bound treats all non-space glyphs as wide and is audit-only;
    # the active-font measurement below is the release gate.
    upper_bounds = line_upper_bound_px(family.target_literals)
    font_widths = font_line_widths_px(family.target_literals)
    if font_widths != family.target_font_widths_px or any(width > DIALOGUE_MAX_LINE_PX for width in font_widths):
        raise Wave22Error(f"{family.name} active-font width differs or exceeds maximum")
    preserved_spans = stripped_opaque_spans(record)
    target = rebuild_static_record(record, family.target_literals)
    target_record = MsgGameRecord(record.block_id, record.record_id, record.relative_offset, target)
    if (
        sha256_bytes(target) != family.target.sha256
        or len(target) != family.target.size
        or literal_texts(target_record) != family.target_literals
        or opaque_spans(target_record) != preserved_spans
        or tuple(value.hex().upper() for value in preserved_spans) != family.target.opaque_spans_hex
        or morphology_commands(target_record)
        or marker_topology(target_record) != marker_topology(record)
        or not target.endswith(RECORD_TERMINATOR)
    ):
        raise Wave22Error(f"{family.name} target record reconstruction differs")
    return target, {
        "family": family.name,
        "resource": resource,
        "coordinate": f"{coordinate[0]}:{coordinate[1]}",
        "input_record": record_report(record, expected),
        "target_record": record_report(target_record, family.target),
        "current_literals": list(current_literals),
        "target_literals": list(family.target_literals),
        "removed_opaque_commands_hex": list(expected.morphology_commands_hex),
        "removed_0143_command_count": len(expected.morphology_commands_hex),
        "target_has_no_0143": True,
        "target_opaque_spans_hex": [value.hex().upper() for value in preserved_spans],
        "terminator_hex": RECORD_TERMINATOR.hex().upper(),
        "manual_line_count": {"current": current_text.count("\n") + 1, "target": target_text.count("\n") + 1},
        "line_upper_bound_px": list(upper_bounds),
        "font_line_widths_px": list(font_widths),
        "dialogue_max_line_px": DIALOGUE_MAX_LINE_PX,
        "rationale": family.rationale,
    }


def validate_output_records(output: Mapping[str, bytes]) -> None:
    for family in FAMILIES:
        for resource, coordinate in ((BASE_MSGGAME, family.base_coordinate), (PK_MSGGAME, family.pk_coordinate)):
            record = records_by_coordinate(output[resource]).get(coordinate)
            if record is None:
                raise Wave22Error(f"candidate lacks {family.name} {resource}")
            if (
                sha256_bytes(record.data) != family.target.sha256
                or len(record.data) != family.target.size
                or literal_texts(record) != family.target_literals
                or tuple(value.hex().upper() for value in opaque_spans(record)) != family.target.opaque_spans_hex
                or morphology_commands(record)
                or not record.data.endswith(RECORD_TERMINATOR)
            ):
                raise Wave22Error(f"candidate target differs: {family.name} {resource}")


def validate_holds_unchanged(before: Mapping[str, bytes], after: Mapping[str, bytes]) -> None:
    before_records = {resource: records_by_coordinate(data) for resource, data in before.items()}
    after_records = {resource: records_by_coordinate(data) for resource, data in after.items()}
    for hold in HOLDS:
        for resource, coordinate in ((BASE_MSGGAME, hold.base_coordinate), (PK_MSGGAME, hold.pk_coordinate)):
            if before_records[resource][coordinate].data != after_records[resource][coordinate].data:
                raise Wave22Error(f"held fragment changed: {hold.name} {resource}")


def prepare_candidate(input_root: Path = PREDECESSOR_ROOT) -> tuple[dict[str, bytes], dict[str, Any]]:
    input_root = require_predecessor_root(input_root)
    wave20_evidence = validate_wave20_evidence(input_root)
    assert_profile(input_root, INPUT_SHA256, INPUT_SIZES, "Wave 20 predecessor")
    before = {resource: (input_root / resource).read_bytes() for resource in CHANGED_PATHS}
    for resource, packed in before.items():
        if len(packed) != INPUT_SIZES[resource]:
            raise Wave22Error(f"Wave 20 packed size differs: {resource}")
        validate_raw_roundtrip(packed, f"Wave 20 {resource}")
    references, reference_hashes = load_references()
    validate_family_anchors(references)

    current = {resource: records_by_coordinate(data) for resource, data in before.items()}
    replacements: dict[str, dict[tuple[int, int], bytes]] = {resource: {} for resource in CHANGED_PATHS}
    rows: list[dict[str, Any]] = []
    for family in FAMILIES:
        for resource, coordinate in ((BASE_MSGGAME, family.base_coordinate), (PK_MSGGAME, family.pk_coordinate)):
            if coordinate in replacements[resource]:
                raise Wave22Error(f"duplicate replacement: {resource} {coordinate}")
            target, row = validate_change(family, resource, current[resource][coordinate])
            replacements[resource][coordinate] = target
            rows.append(row)

    output: dict[str, bytes] = {}
    for resource in CHANGED_PATHS:
        candidate = rebuild_packed_msggame(before[resource], replacements[resource])
        if len(candidate) != TARGET_SIZES[resource] or sha256_bytes(candidate) != TARGET_SHA256[resource]:
            raise Wave22Error(f"candidate packed output differs: {resource}")
        validate_raw_roundtrip(candidate, f"Wave 22 {resource}")
        old_records = records_by_coordinate(before[resource])
        new_records = records_by_coordinate(candidate)
        if old_records.keys() != new_records.keys():
            raise Wave22Error(f"record topology changed: {resource}")
        changed = {coordinate for coordinate in old_records if old_records[coordinate].data != new_records[coordinate].data}
        if changed != set(replacements[resource]):
            raise Wave22Error(f"unexpected changed record set: {resource} {sorted(changed)}")
        output[resource] = candidate
    validate_output_records(output)
    validate_holds_unchanged(before, output)

    target_hashes = {**INPUT_SHA256, **{resource: sha256_bytes(data) for resource, data in output.items()}}
    target_sizes = {**INPUT_SIZES, **{resource: len(data) for resource, data in output.items()}}
    if target_hashes != TARGET_SHA256 or target_sizes != TARGET_SIZES:
        raise Wave22Error("candidate output profile is not pinned")
    family_reports = []
    for family in FAMILIES:
        family_reports.append({
            "name": family.name,
            "base_coordinate": f"{family.base_coordinate[0]}:{family.base_coordinate[1]}",
            "pk_coordinate": f"{family.pk_coordinate[0]}:{family.pk_coordinate[1]}",
            "pc_base_jp": record_report(references["BASE_JP"][family.base_coordinate], family.base_jp),
            "pc_pk_jp": record_report(references["PK_JP"][family.pk_coordinate], family.pk_jp),
            "pc_pk_contexts": {
                "EN": record_report(references["EN"][family.pk_coordinate], family.en),
                "SC": record_report(references["SC"][family.pk_coordinate], family.sc),
                "TC": record_report(references["TC"][family.pk_coordinate], family.tc),
            },
            "rationale": family.rationale,
        })
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "platform": "Steam PC private candidate only",
            "predecessor": "complete Wave 20 eleven-file candidate",
            "wave20_full_profile_required": True,
            "pristine_pc_japanese_read": True,
            "pc_pk_en_sc_tc_context_read": True,
            "active_pc_jp_font_read": True,
            "switch_korean_read": False,
            "steam_game_resource_written": False,
            "steam_apply_capability": "absent",
            "git_operation": "absent",
            "release_operation": "absent",
        },
        "predecessor_candidate": input_root.relative_to(REPO).as_posix(),
        "wave20_evidence": wave20_evidence,
        "input_sha256": INPUT_SHA256,
        "input_sizes": INPUT_SIZES,
        "target_sha256": TARGET_SHA256,
        "target_sizes": TARGET_SIZES,
        "pc_reference_sha256": reference_hashes,
        "font": {"resource": "RES_JP/res_lang.bin", "sha256": FONT_SHA256, "outer_entry": FONT_OUTER_ENTRY, "table": FONT_TABLE},
        "families": family_reports,
        "records": rows,
        "changed_record_count": len(rows),
        "held_pairs": [
            {"name": hold.name, "base_coordinate": f"{hold.base_coordinate[0]}:{hold.base_coordinate[1]}", "pk_coordinate": f"{hold.pk_coordinate[0]}:{hold.pk_coordinate[1]}", "reason": hold.reason}
            for hold in HOLDS
        ],
        "held_pair_count": len(HOLDS),
    }
    return output, audit


def require_tmp(path: Path, label: str) -> Path:
    root = TMP_ROOT.resolve(strict=False)
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave22Error(f"{label} must stay below {root}") from exc
    return resolved


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def verify_private_candidate(candidate_root: Path) -> None:
    candidate_root = require_tmp(candidate_root, "candidate root")
    assert_profile(candidate_root, TARGET_SHA256, TARGET_SIZES, "Wave 22 private candidate")
    output = {resource: (candidate_root / resource).read_bytes() for resource in CHANGED_PATHS}
    before = {resource: (PREDECESSOR_ROOT / resource).read_bytes() for resource in CHANGED_PATHS}
    for resource, packed in output.items():
        validate_raw_roundtrip(packed, f"Wave 22 private {resource}")
    validate_output_records(output)
    validate_holds_unchanged(before, output)


def _remove_stage(stage: Path) -> None:
    if not stage.exists():
        return
    try:
        stage.resolve().relative_to(TMP_ROOT.resolve(strict=False))
    except ValueError as exc:
        raise Wave22Error("refusing to remove stage outside Wave 22 tmp root") from exc
    shutil.rmtree(stage)


def build_candidate(input_root: Path, output_root: Path, audit_path: Path, manifest_path: Path) -> dict[str, Any]:
    input_root = require_predecessor_root(input_root)
    output_root = require_tmp(output_root, "candidate output")
    audit_path = require_tmp(audit_path, "audit output")
    manifest_path = require_tmp(manifest_path, "manifest output")
    if output_root.exists() or audit_path.exists() or manifest_path.exists():
        raise Wave22Error("candidate output, audit, or manifest already exists")
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
        assert_profile(stage, TARGET_SHA256, TARGET_SIZES, "Wave 22 private staging")
        os.replace(stage, output_root)
        verify_private_candidate(output_root)
        audit_bytes = (json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
        atomic_write(audit_path, audit_bytes)
        manifest = {
            "schema": SCHEMA,
            "transaction_id": "pc-dialogue-quality-wave22-static-inflection-v1",
            "candidate_only": True,
            "predecessor_candidate": input_root.relative_to(REPO).as_posix(),
            "profile_paths": list(PROFILE_PATHS),
            "changed_paths": list(CHANGED_PATHS),
            "coordinates": [
                f"{BASE_MSGGAME}:{family.base_coordinate[0]}:{family.base_coordinate[1]}"
                for family in FAMILIES
            ] + [
                f"{PK_MSGGAME}:{family.pk_coordinate[0]}:{family.pk_coordinate[1]}"
                for family in FAMILIES
            ],
            "input_sha256": INPUT_SHA256,
            "input_sizes": INPUT_SIZES,
            "output_sha256": TARGET_SHA256,
            "output_sizes": TARGET_SIZES,
            "pinned_output_sha256": TARGET_SHA256,
            "audit_sha256": sha256_bytes(audit_bytes),
            "record_count": len(FAMILIES) * 2,
            "held_pair_count": len(HOLDS),
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
    verify_parser = sub.add_parser("verify-private", help="verify a private Wave 22 candidate")
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
            print(json.dumps({"status": "ok", "target_sha256": audit["target_sha256"], "steam_write_capability": "absent"}, ensure_ascii=False, indent=2, sort_keys=True))
            return 0
        if args.command == "verify-private":
            verify_private_candidate(args.candidate_root)
            print(json.dumps({"status": "ok", "candidate_root": str(args.candidate_root), "steam_write_capability": "absent"}, ensure_ascii=False, sort_keys=True))
            return 0
        manifest = build_candidate(args.input_root, args.output_root, args.audit_path, args.manifest_path)
        print(json.dumps({"status": "ok", "manifest": manifest, "steam_write_capability": "absent"}, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, Wave22Error) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
