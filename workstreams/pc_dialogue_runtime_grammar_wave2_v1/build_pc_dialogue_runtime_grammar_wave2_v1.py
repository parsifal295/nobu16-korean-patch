#!/usr/bin/env python3
"""Build the PC-only second repair wave for Japanese runtime grammar bytes.

This wave is deliberately coordinate-gated.  It fixes only records whose
current Korean literal text is known to be joined to Japanese inflection bytes
(``01 43 <u32>``).  Runtime name/target references are not in scope.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
MSGGAME = REPO / "workstreams" / "msggame"
sys.path[:0] = [str(TOOLS), str(MSGGAME)]

from msggame_format import (  # noqa: E402
    LITERAL_END,
    LITERAL_START,
    MsgGameRecord,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_msggame,
)


DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_OUTPUT_ROOT = REPO / "tmp" / WORKSTREAM.name / "candidate"
DEFAULT_MANIFEST = REPO / "tmp" / WORKSTREAM.name / "build_manifest.v1.json"
TERMINATOR = b"\x05\x05\x05"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-runtime-grammar-wave2.v1"

# Exact installed state after pc_dialogue_quality_wave1_v1.  All eleven files
# are copied into the candidate so the file-only transaction can use its exact
# PC text-audit profile; only the two msggame files may change.
BASELINE_SHA256 = {
    "MSG/JP/ev_strdata.bin": "25D9C029F93788053720C04BAE0C0A14A1A5983F36C68BC2EC7C46C3340D5834",
    "MSG/JP/msggame.bin": "04C9C6C63894ED2525B1107C2D251F55B081C5AB246C021CC262378F6028C938",
    "MSG/JP/strdata.bin": "10AB5E3BD9140B26EB7BC42DC5C352D4CE2905580C6A6112B13B37E12A358AFE",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    "MSG_PK/JP/msgdata.bin": "8B78403C339BEEE655B53A3F63699054DC6D9078640FE717885627E73B529752",
    "MSG_PK/JP/msgev.bin": "9572873D2BBFF3C62581F09BE2CD54225CCDD2C400D3ACC895675E2C0A2780DD",
    "MSG_PK/JP/msggame.bin": "6A3B84E4664809062E5105640F26F3CEABA69DA3675051939497590E5EFB99DE",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}
TARGET_SHA256 = {
    **BASELINE_SHA256,
    "MSG/JP/msggame.bin": "663EB8100A40AF5DE86810C0836EDCEF0A23C3AC2F01D461F9254BC73AA14900",
    "MSG_PK/JP/msggame.bin": "B3B541A86E882BA89FBC46B32FF129E269E7EDE09B17D9CC2DA6F7ED82112E6A",
}
PROFILE_TARGETS = tuple(BASELINE_SHA256)
CHANGED_PATHS = {"MSG/JP/msggame.bin", "MSG_PK/JP/msggame.bin"}


class GrammarWaveError(ValueError):
    """A pinned source record or bytecode contract did not match."""


@dataclass(frozen=True)
class RecordContract:
    base_sha256: str
    base_commands: tuple[tuple[int, bytes], ...]
    pk_sha256: str
    pk_commands: tuple[tuple[int, bytes], ...]

    def for_relative(self, relative: str) -> tuple[str, tuple[tuple[int, bytes], ...]]:
        if relative == "MSG/JP/msggame.bin":
            return self.base_sha256, self.base_commands
        if relative == "MSG_PK/JP/msggame.bin":
            return self.pk_sha256, self.pk_commands
        raise GrammarWaveError(f"unsupported message resource: {relative}")


@dataclass(frozen=True)
class LiteralPlan:
    block_id: int
    record_id: int
    replacements: tuple[tuple[int, str], ...]

    @property
    def coordinate(self) -> tuple[int, int]:
        return self.block_id, self.record_id


@dataclass(frozen=True)
class StaticPlan:
    block_id: int
    record_id: int
    text: str

    @property
    def coordinate(self) -> tuple[int, int]:
        return self.block_id, self.record_id


def cmd(offset: int, hex_value: str) -> tuple[int, bytes]:
    value = bytes.fromhex(hex_value)
    if len(value) != 6 or value[:2] != b"\x01\x43":
        raise ValueError(f"invalid 0143 command contract: {hex_value}")
    return offset, value


def contract(
    base_sha256: str,
    base_commands: tuple[tuple[int, bytes], ...],
    pk_sha256: str,
    pk_commands: tuple[tuple[int, bytes], ...],
) -> RecordContract:
    return RecordContract(base_sha256, base_commands, pk_sha256, pk_commands)


# Every coordinate is anchored to the complete original record hash and to all
# opaque 01 43 commands in that record.  The base and PK operands differ in
# some locales, so they are always represented separately.
CONTRACTS: dict[tuple[int, int], RecordContract] = {
    (12, 18): contract("DF63E8BA2205EFA36F5607661D9B8AF866AAF5519E0241C4007FA5A044812D0B", (cmd(28, "0143F6010000"), cmd(104, "014322030000")), "BA1E862D69D90671823DF5B65922222C377A106EBDA9F072C36EC8C53141BAC5", (cmd(28, "0143FC010000"), cmd(104, "01432E030000"))),
    (12, 21): contract("F0C173B89040B640D2A0014179BF14BD13204C466EBED2A698C0B9C8A6BBD55F", (cmd(88, "014394000000"),), "F0C173B89040B640D2A0014179BF14BD13204C466EBED2A698C0B9C8A6BBD55F", (cmd(88, "014394000000"),)),
    (12, 24): contract("867FFEB6B1993E1A5A3D618D7D33754C007A22D80640C77A463FA371BA37C719", (cmd(60, "014394000000"),), "867FFEB6B1993E1A5A3D618D7D33754C007A22D80640C77A463FA371BA37C719", (cmd(60, "014394000000"),)),
    (12, 26): contract("867FFEB6B1993E1A5A3D618D7D33754C007A22D80640C77A463FA371BA37C719", (cmd(60, "014394000000"),), "867FFEB6B1993E1A5A3D618D7D33754C007A22D80640C77A463FA371BA37C719", (cmd(60, "014394000000"),)),
    (12, 28): contract("867FFEB6B1993E1A5A3D618D7D33754C007A22D80640C77A463FA371BA37C719", (cmd(60, "014394000000"),), "867FFEB6B1993E1A5A3D618D7D33754C007A22D80640C77A463FA371BA37C719", (cmd(60, "014394000000"),)),
    (12, 45): contract("06646192A356A5224A953BCA12B401DEB5B291F8EE85769A815C2030D1585273", (cmd(14, "014378010000"), cmd(88, "014314020000"), cmd(118, "014302020000")), "2A8AC31E9DD8D3941A02BA8E93387E92000319CF07C1A20BEB8E664791241260", (cmd(14, "014378010000"), cmd(88, "01431A020000"), cmd(118, "014308020000"))),
    (12, 46): contract("A2DB1BA0A9A7579D868F44F6FA88420448CFD2D6F439E4BD325CD6348795A183", (cmd(100, "01433E020000"),), "BC0FE310420915D2F085005625D147988A968AD89BA4AAEF433378F8DBE999A2", (cmd(100, "01434A020000"),)),
    (12, 47): contract("850B70623600B589B27B201EB2294E951E3DC815DBCA5737B7630F6158BBD254", (cmd(14, "014378010000"), cmd(88, "014314020000"), cmd(116, "014302020000")), "C3D27F2CA4B0603BA19C45DBF42BA49D71632F63D21149F5294DF2641202575A", (cmd(14, "014378010000"), cmd(88, "01431A020000"), cmd(116, "014308020000"))),
    (12, 48): contract("F14891BE26E652EFB3BADFD06B62875A336DB97E8327B1C2FDCE4DD6B72B0F59", (cmd(96, "01433E020000"),), "4FDD9829CDBB8AC27D667105B2E4B71E67C78F39BAA23FE975960AFF5CE0F27D", (cmd(96, "01434A020000"),)),
    (12, 49): contract("477CBC3011D280D6451429152BC8684955A281AA03AA50224FB6FDB8BEB9F232", (cmd(14, "014378010000"), cmd(90, "014314020000"), cmd(122, "014302020000")), "3441E3C10C571828D738D5F0CD0CA16428E5E3813B71437B4C1A2C582EC8812F", (cmd(14, "014378010000"), cmd(90, "01431A020000"), cmd(122, "014308020000"))),
    (12, 50): contract("D90783F6C68B65BAE33BBFE3F9802307744252D14F2A15620DB4DA19DA9482F6", (cmd(108, "01433E020000"),), "B1B08F7B2511C098728BAB48CDABAE336AB71BDC188F66D6168639A362C2F413", (cmd(108, "01434A020000"),)),
    (12, 51): contract("5778CEAC41E0627648F7A08BB15196D898A7F7B7B63BB35B09764914C987A66C", (cmd(102, "014314020000"),), "C95DA0FDAC069923628E0727E3A46202459BB3ACAEBFE086DD6BD6BA1C396C0B", (cmd(102, "01431A020000"),)),
    (12, 52): contract("7100009FE77E1C65E2339B410C6C6F854F3DFA270BCB52C464B759F34CC2BC82", (cmd(94, "01433E020000"),), "D25FC466C30CB41E589EA0F0331165411FD044D9F8548FE42A13CB92AA24C32D", (cmd(94, "01434A020000"),)),
    (12, 53): contract("213A43C78E953BED2793A25CCBB9622AFCB8421CD1D2D10D3BF3BB4F36B32C69", (cmd(92, "014314020000"),), "959D9C9E63A6690A4AD4DC85336DDFE93B9351943D388D2A8F327CEE0CAFDB2F", (cmd(92, "01431A020000"),)),
    (12, 54): contract("332D405D58C31A686DDDB932CD65B975D8FEB56148CAEAB6B5BFC6F597F59EAE", (cmd(90, "01433E020000"),), "6C14F2DDA1DA92F97768AEDE4548CD4821F8DAE97F49A2AD0A2DD136167C3EE6", (cmd(90, "01434A020000"),)),
    (12, 55): contract("B114B22D70C219A2BC1EF6129C65914FA93349FFC7ED8862A026A879A61B7D6C", (cmd(14, "014378010000"), cmd(88, "014314020000"), cmd(124, "014356020000")), "237B4F4BC30E67D981B7A51BE81388B11E996B5C29C9F46AC3F6436B72EF19D1", (cmd(14, "014378010000"), cmd(88, "01431A020000"), cmd(124, "014362020000"))),
    (12, 56): contract("82EE1D988D539867C6247AB46A8B06EE8BB16595D6679A4D3ED5BDA78A26C1BD", (cmd(100, "01433E020000"),), "226CD29BD2B6F29F7CB176FC4C3C000D373F1E0D2E157BA9321C5EC495E7B9E3", (cmd(100, "01434A020000"),)),
    (12, 57): contract("1E4CAEA9B71E28392D8834CAC7AD8A6E2A53DA63384D03D55CAA97BA462B24B9", (cmd(14, "014378010000"), cmd(96, "014314020000"), cmd(126, "014302020000")), "0A7C5BC37C06DD3A2BC9FA579EFF27D60D7E6BE8D1444308720109BA6D01A925", (cmd(14, "014378010000"), cmd(96, "01431A020000"), cmd(126, "014308020000"))),
    (12, 58): contract("8B7B3E2DD6AA22F61D75E4BF327815C225BAC9A925EBF2DBEF8F6A4A94C8DCB8", (cmd(124, "01433E020000"),), "601928EEE2522E89E34D1F8E77D72647BA915DCE80B474EA634FFF0D7631455F", (cmd(124, "01434A020000"),)),
    (12, 59): contract("24582AD136F98AD5B3E9170C0743973FFB2D771FBBB875579D18A2DD092AA45F", (cmd(14, "014378010000"), cmd(84, "014314020000")), "AB28100FCB7C2A478E8D9A7EFFA762A26D803B0D59B9FDCD6BFD8265A14A48D0", (cmd(14, "014378010000"), cmd(84, "01431A020000"))),
    (12, 60): contract("08C845612021E1433DD97A2A764AC1E1ADD4BE2A081B715A93345A33702B37AF", (cmd(102, "01433E020000"),), "C393BB8FCE948EF07162FF09C55695B3728F888235F8C96B4168FC5A0980352D", (cmd(102, "01434A020000"),)),
    (12, 61): contract("7D57695618C737D265C3B3269C521D665E78EAE93FD1991D26A5A0C00793FF74", (cmd(14, "014378010000"), cmd(88, "014314020000"), cmd(120, "014302020000")), "1D989847A2C9CDBC19C6D5FEE481C10C7E0D706E0105305727E48A063A119AF5", (cmd(14, "014378010000"), cmd(88, "01431A020000"), cmd(120, "014308020000"))),
    (12, 62): contract("748115E3EF6DB871F0CAF67E353A3C120040AD964EC963EF14F7ADAA66593BC0", (cmd(96, "01433E020000"),), "911D3ED554399DA16EE1C75BCFDBDFA09ABBCCB6CF328803AD2AE0E6AAEF0686", (cmd(96, "01434A020000"),)),
    (13, 23): contract("CC156AF698215B1EBE10C04C941563CF3E7339D0285DB334495AE67F8F17E668", (cmd(56, "014352000000"),), "CC156AF698215B1EBE10C04C941563CF3E7339D0285DB334495AE67F8F17E668", (cmd(56, "014352000000"),)),
    (13, 24): contract("6AA532E3705FA40BF6F011E9B7382509B7457CE9A6E73E3B85F6E68DF02E48CE", (cmd(34, "0143B2000000"),), "6AA532E3705FA40BF6F011E9B7382509B7457CE9A6E73E3B85F6E68DF02E48CE", (cmd(34, "0143B2000000"),)),
    (13, 27): contract("DB34D1BC73BC83BC7FBB701415FDF7607B12FA8595C3F3A0915ACA84FB612325", (cmd(36, "01431A020000"), cmd(92, "014366040000")), "AAF22AC196B3C584F53FF50A6190137F7846BB88B2E63950958FDE4124A3D419", (cmd(36, "014326020000"), cmd(92, "014372040000"))),
    (13, 30): contract("438A3970BFDA2584DDFF2C9F6AF8B7BDFA6A7782239CE242348F0354B7483EC7", (cmd(32, "014324010000"),), "438A3970BFDA2584DDFF2C9F6AF8B7BDFA6A7782239CE242348F0354B7483EC7", (cmd(32, "014324010000"),)),
    (13, 32): contract("CD8DFA1D608D7A0F841A70E84E6CD5BA1C8B698A6C0965F499761A3A6F404403", (cmd(36, "0143DA020000"),), "474F3730F38851468CCD6339ABCD1511DF14D3678FAC85B523543CCBB3E3A157", (cmd(36, "0143E6020000"),)),
    (13, 46): contract("CAD7701E18D69AA5F976E9FC0638E8D710890E8783EB63FFDF234AE5ADC44935", (cmd(68, "0143DA020000"),), "E5E73CCF4AC1C043792D661FB9D0EC1C90ED019EC3B1821D35A893930A63910C", (cmd(68, "0143E6020000"),)),
    (13, 110): contract("A5A45EFC25A1F025FD41CE8C026BEE91875DDA80BAA0A71F6DF0223259766D2E", (cmd(32, "014384010000"), cmd(70, "0143D0030000")), "68BE47D3623A2A10BA0968158E2D696153E004DAC30EC1A4E607B696BAC77764", (cmd(32, "01438A010000"), cmd(70, "0143DC030000"))),
    (16, 2): contract("0675EB158E8DD684E223276D2F1185D4A39C92646D3A66EC0CA911CE758587A5", (cmd(34, "0143DA020000"),), "2E95D662CD519B47F070755B80559B45518A00477BAA093A381CDE7F613CE449", (cmd(34, "0143E6020000"),)),
    (16, 4): contract("D03D3406FE704A0471018F8E9B8B603F79DD31736D5B9FBFD12C023FAAE7333A", (cmd(36, "014356020000"),), "ED97DCC79340A1CABC58959508F81DB0E58A720CB2F56C078E3DF580F65B1FB7", (cmd(36, "014362020000"),)),
    (16, 38): contract("A12B864A626B1FB7E944B2F1BF1F6E5300D97C04CEBE226D235CC37E38E81FBB", (cmd(18, "0143E0020000"),), "3E0CB510D3E5EA8ED5FCB3E1C6269258E3577E5EF6BE9BBF0133A4B4AA19B32F", (cmd(18, "0143EC020000"),)),
}

# These plans keep their existing literal boundaries and, for regional names,
# preserve their 1B43xx colour formatting.  Only the explicitly pinned 0143
# command bytes are removed.
LITERAL_PLANS = (
    LiteralPlan(12, 18, ((0, "（……지금부터가 고비다"), (1, "\r\n　내 뜻을 이루는 그날까지\r\n　결코 걸음을 멈춰서는 안 된다"))),
    LiteralPlan(12, 21, ((0, "무, 무려! 삼직이라 하면\n「태정대신」「관백」「정이대장군」…!\n어찌 답해야 할"), (1, "까…"))),
    LiteralPlan(12, 24, ((0, "참으로 훌륭하신 결단이옵니다!\n곧바로 조정에 답신을 올리겠습니다."),)),
    LiteralPlan(12, 26, ((0, "참으로 훌륭하신 결단이옵니다!\n곧바로 조정에 답신을 올리겠습니다."),)),
    LiteralPlan(12, 28, ((0, "참으로 훌륭하신 결단이옵니다!\n곧바로 조정에 답신을 올리겠습니다."),)),
    LiteralPlan(12, 45, ((0, "축하드립니다"), (3, "의 성은 모두 우리 가문이 장악했습니다"), (4, "。\n미증유의 쾌거입니다"))),
    LiteralPlan(12, 46, ((0, "가까스로 "), (2, " 전역에\n평온을 가져올 수 있었군…\n모두, 수고했다"))),
    LiteralPlan(12, 47, ((0, "축하드립니다"), (3, "의 성은 모두 우리 가문이 장악했습니다"), (4, "。\n훌륭한 성과입니다"))),
    LiteralPlan(12, 48, ((0, "마침내 "), (2, " 전역에\n평온을 가져올 수 있었군…\n모두, 수고했다"))),
    LiteralPlan(12, 49, ((0, "축하드립니다"), (3, "의 성은 모조리 당가가 장악했습니다"), (4, "。\n전대미문의 쾌거입니다"))),
    LiteralPlan(12, 50, ((1, "의 땅에 사는 모든 백성에게\n평온을 가져다줄 수 있었군…\n모두, 수고했다"),)),
    LiteralPlan(12, 51, ((0, "참으로 경사스럽기 그지없습니다!\n당가가"), (2, "에 있는 성을 모두\n장악했습니다"))),
    LiteralPlan(12, 52, ((0, "이토록 빨리 "), (2, "의 땅을\n통일할 수 있게 되다니…\n모두, 수고했다"))),
    LiteralPlan(12, 53, ((0, "참으로 경사로운 일입니다!\n"), (2, "에 있는 성은 모두 당가가\n장악했습니다"))),
    LiteralPlan(12, 54, ((1, " 지방 일대에\n평온을 가져올 수 있었군…\n모두, 수고했다"),)),
    LiteralPlan(12, 55, ((0, "축하드립니다"), (3, "의 성은 모두 우리 가문이 장악했습니다"), (4, "。\n수백 년 만의 쾌거 아닙니까"), (5, "!"))),
    LiteralPlan(12, 56, ((0, "마침내 "), (2, "와 그 인근에\n평온을 가져올 수 있었군…\n모두, 수고했다"))),
    LiteralPlan(12, 57, ((0, "축하드립니다"), (3, " 지방의 성을 모두 우리 가문이 장악했습니다"), (4, "。\n미증유의 쾌거입니다"))),
    LiteralPlan(12, 58, ((0, "가까스로 "), (4, " 전역에\n평온을 가져올 수 있었군…\n모두, 수고했다"))),
    LiteralPlan(12, 59, ((0, "축하드립니다"), (3, "의 성은 모두 당가가\n장악했습니다"))),
    LiteralPlan(12, 60, ((0, "이토록 빨리 "), (2, " 전역에\n평온을 가져올 수 있게 되다니…\n모두, 수고했다"))),
    LiteralPlan(12, 61, ((0, "축하드립니다"), (3, "의 성은 모두 우리 가문이 장악했습니다"), (4, "。\n공전절후의 쾌거입니다"))),
    LiteralPlan(12, 62, ((0, "이 "), (2, " 지역에 마침내\n평온을 가져올 수 있었군…\n모두, 수고했다"))),
)

# These records contain no surviving opaque bytes after removal except the
# record terminator, so each becomes one complete Korean literal.
STATIC_PLANS = (
    StaticPlan(13, 23, "그러기 위해서는 무엇보다\n병량을 비축할 필요가 있다."),
    StaticPlan(13, 24, "이미 쳐들어갈 준비는 되어 있으나\n국력을 더 높여 두는 것도 한 방법일 듯하오."),
    StaticPlan(13, 27, "무엇을 하든 우선 필요한 것은 돈입니다.\n돈이 없으면 세력 확대도 이룰 수 없습니다.\n먼저 내정을 재정비해 수입을 늘려야 합니다."),
    StaticPlan(13, 30, "군을 강화하는 것은 어떻겠습니까?\n하나의 성은 몇 개의 군으로 이루어져…"),
    StaticPlan(13, 32, "또한 모든 군을\n돌볼 필요는 없습니다."),
    StaticPlan(13, 46, "적국을 힘으로 멸하는 것만이\n천하로 나아가는 유일한 길만은 아니다."),
    StaticPlan(13, 110, "다만 특필할 만한 능력은 없으나,\n특성의 힘으로 활약해 주기를 바란다."),
    StaticPlan(16, 2, "취락을 장악하는 것도\n쉽지 않다."),
    StaticPlan(16, 4, "싸움 없는 세상은\n과연 찾아올 것인가…"),
    StaticPlan(16, 38, "일손이 부족하다…\n군 개발에 힘을…"),
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def require_under(root: Path, candidate: Path, label: str) -> Path:
    root = root.resolve()
    candidate = candidate.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise GrammarWaveError(f"{label} escapes its allowed root: {candidate}") from exc
    return candidate


def output_paths(output_root: Path) -> set[str]:
    return {path.relative_to(output_root).as_posix() for path in output_root.rglob("*") if path.is_file()}


def assert_profile_sha256(steam_root: Path, expected: dict[str, str], label: str) -> None:
    actual = {
        relative: sha256_path(require_under(steam_root, steam_root / relative, "Steam source"))
        for relative in PROFILE_TARGETS
    }
    if actual != expected:
        mismatches = {path: {"expected": expected[path], "actual": actual[path]} for path in PROFILE_TARGETS if actual[path] != expected[path]}
        raise GrammarWaveError(f"Steam {label} differs from approved wave-2 state: {mismatches}")


def assert_baseline(steam_root: Path) -> None:
    assert_profile_sha256(steam_root, BASELINE_SHA256, "baseline")


def plan_coordinates() -> set[tuple[int, int]]:
    coordinates = [plan.coordinate for plan in (*LITERAL_PLANS, *STATIC_PLANS)]
    if len(coordinates) != len(set(coordinates)):
        raise GrammarWaveError("duplicate record plan coordinate")
    if set(coordinates) != set(CONTRACTS):
        raise GrammarWaveError("record plans and contracts have different coordinates")
    return set(coordinates)


def record_at(archive, coordinate: tuple[int, int]) -> MsgGameRecord:
    block_id, record_id = coordinate
    try:
        return archive.blocks[block_id].records[record_id]
    except IndexError as exc:
        raise GrammarWaveError(f"missing msggame record {block_id}:{record_id}") from exc


def opaque_spans(record: MsgGameRecord) -> tuple[tuple[int, bytes], ...]:
    cursor = 0
    spans: list[tuple[int, bytes]] = []
    for literal in parse_record_literals(record):
        spans.append((cursor, record.data[cursor:literal.marker_offset]))
        cursor = literal.marker_end
    spans.append((cursor, record.data[cursor:]))
    return tuple(spans)


def opaque_commands(record: MsgGameRecord) -> tuple[tuple[int, bytes], ...]:
    commands: list[tuple[int, bytes]] = []
    for base, span in opaque_spans(record):
        for index in range(len(span) - 5):
            if span[index:index + 2] == b"\x01\x43":
                commands.append((base + index, span[index:index + 6]))
    return tuple(commands)


def assert_contract(record: MsgGameRecord, relative: str, coordinate: tuple[int, int]) -> tuple[tuple[int, bytes], ...]:
    contract_value = CONTRACTS[coordinate]
    expected_sha256, expected_commands = contract_value.for_relative(relative)
    actual_sha256 = sha256_bytes(record.data)
    if actual_sha256 != expected_sha256:
        raise GrammarWaveError(f"record source hash differs at {relative}@{coordinate}: {actual_sha256}")
    actual_commands = opaque_commands(record)
    if actual_commands != expected_commands:
        raise GrammarWaveError(f"opaque 0143 contract differs at {relative}@{coordinate}: {actual_commands!r}")
    return expected_commands


def encode_literal(text: str, coordinate: tuple[int, int]) -> bytes:
    encoded = text.encode("utf-16-le")
    if LITERAL_START in encoded or LITERAL_END in encoded:
        raise GrammarWaveError(f"replacement contains reserved marker at {coordinate}")
    return LITERAL_START + encoded + LITERAL_END


def strip_commands(span_start: int, span: bytes, commands: tuple[tuple[int, bytes], ...]) -> bytes:
    expected = dict(commands)
    output = bytearray()
    index = 0
    while index < len(span):
        absolute = span_start + index
        command = expected.get(absolute)
        if command is not None:
            if span[index:index + 6] != command:
                raise GrammarWaveError(f"pinned 0143 command shifted at 0x{absolute:X}")
            index += 6
            continue
        if span[index:index + 2] == b"\x01\x43":
            raise GrammarWaveError(f"unplanned opaque 0143 command at 0x{absolute:X}")
        output.append(span[index])
        index += 1
    return bytes(output)


def rebuild_literal_plan(record: MsgGameRecord, relative: str, plan: LiteralPlan) -> bytes:
    coordinate = plan.coordinate
    commands = assert_contract(record, relative, coordinate)
    literals = parse_record_literals(record)
    replacements = dict(plan.replacements)
    if len(replacements) != len(plan.replacements) or any(index < 0 or index >= len(literals) for index in replacements):
        raise GrammarWaveError(f"literal plan index differs at {coordinate}")
    output = bytearray()
    cursor = 0
    for literal in literals:
        output.extend(strip_commands(cursor, record.data[cursor:literal.marker_offset], commands))
        output.extend(encode_literal(replacements.get(literal.literal_id, literal.text), coordinate))
        cursor = literal.marker_end
    output.extend(strip_commands(cursor, record.data[cursor:], commands))
    rebuilt = bytes(output)
    checked = MsgGameRecord(record.block_id, record.record_id, record.relative_offset, rebuilt)
    checked_literals = parse_record_literals(checked)
    if len(checked_literals) != len(literals) or opaque_commands(checked):
        raise GrammarWaveError(f"literal plan output structure differs at {coordinate}")
    for index, text in replacements.items():
        if checked_literals[index].text != text:
            raise GrammarWaveError(f"literal plan output differs at {coordinate}:{index}")
    return rebuilt


def rebuild_static_plan(record: MsgGameRecord, relative: str, plan: StaticPlan) -> bytes:
    coordinate = plan.coordinate
    commands = assert_contract(record, relative, coordinate)
    clean_opaque = b"".join(strip_commands(start, span, commands) for start, span in opaque_spans(record))
    if clean_opaque != TERMINATOR:
        raise GrammarWaveError(f"static plan would discard opaque bytes at {coordinate}: {clean_opaque.hex().upper()}")
    rebuilt = encode_literal(plan.text, coordinate) + TERMINATOR
    checked = MsgGameRecord(record.block_id, record.record_id, record.relative_offset, rebuilt)
    literals = parse_record_literals(checked)
    if len(literals) != 1 or literals[0].text != plan.text or opaque_commands(checked):
        raise GrammarWaveError(f"static plan output differs at {coordinate}")
    return rebuilt


def patch_msggame(source: bytes, relative: str) -> bytes:
    archive = parse_packed_msggame(source).archive
    replacements: dict[tuple[int, int], bytes] = {}
    for plan in LITERAL_PLANS:
        replacements[plan.coordinate] = rebuild_literal_plan(record_at(archive, plan.coordinate), relative, plan)
    for plan in STATIC_PLANS:
        replacements[plan.coordinate] = rebuild_static_plan(record_at(archive, plan.coordinate), relative, plan)
    if set(replacements) != plan_coordinates():
        raise GrammarWaveError("replacement coordinate set differs")
    return rebuild_packed_msggame(source, replacements)


def verify_patched_msggame(source: bytes, candidate: bytes, relative: str) -> None:
    before = parse_packed_msggame(source).archive
    after = parse_packed_msggame(candidate).archive
    if len(before.blocks) != len(after.blocks):
        raise GrammarWaveError(f"candidate block count differs at {relative}")
    literal_by_coordinate = {plan.coordinate: plan for plan in LITERAL_PLANS}
    static_by_coordinate = {plan.coordinate: plan for plan in STATIC_PLANS}
    for before_block, after_block in zip(before.blocks, after.blocks, strict=True):
        if len(before_block.records) != len(after_block.records):
            raise GrammarWaveError(f"candidate record count differs at {relative} block {before_block.block_id}")
        for original, rebuilt in zip(before_block.records, after_block.records, strict=True):
            coordinate = (original.block_id, original.record_id)
            if coordinate in literal_by_coordinate:
                expected = rebuild_literal_plan(original, relative, literal_by_coordinate[coordinate])
                if rebuilt.data != expected:
                    raise GrammarWaveError(f"literal candidate record differs at {relative}@{coordinate}")
            elif coordinate in static_by_coordinate:
                expected = rebuild_static_plan(original, relative, static_by_coordinate[coordinate])
                if rebuilt.data != expected:
                    raise GrammarWaveError(f"static candidate record differs at {relative}@{coordinate}")
            elif original.data != rebuilt.data:
                raise GrammarWaveError(f"candidate changed untouched record at {relative}@{coordinate}")


def verify_installed(steam_root: Path) -> dict[str, object]:
    """Verify the exact post-apply target without rebuilding a candidate."""
    steam_root = steam_root.resolve(strict=True)
    assert_profile_sha256(steam_root, TARGET_SHA256, "installed target")
    for relative in sorted(CHANGED_PATHS):
        archive = parse_packed_msggame((steam_root / relative).read_bytes()).archive
        for plan in LITERAL_PLANS:
            record = record_at(archive, plan.coordinate)
            literals = parse_record_literals(record)
            for index, text in plan.replacements:
                if literals[index].text != text:
                    raise GrammarWaveError(f"installed literal differs at {relative}@{plan.coordinate}:{index}")
            if opaque_commands(record):
                raise GrammarWaveError(f"installed 0143 command remains at {relative}@{plan.coordinate}")
        for plan in STATIC_PLANS:
            record = record_at(archive, plan.coordinate)
            literals = parse_record_literals(record)
            if len(literals) != 1 or literals[0].text != plan.text or opaque_commands(record):
                raise GrammarWaveError(f"installed static record differs at {relative}@{plan.coordinate}")
    return {
        "schema": MANIFEST_SCHEMA,
        "status": "PASS",
        "installed_profile": "target",
        "changed_paths": sorted(CHANGED_PATHS),
        "literal_preserving_record_count_per_resource": len(LITERAL_PLANS),
        "static_record_count_per_resource": len(STATIC_PLANS),
    }


def verify_candidate(steam_root: Path, output_root: Path) -> dict[str, object]:
    steam_root = steam_root.resolve(strict=True)
    output_root = output_root.resolve(strict=True)
    assert_baseline(steam_root)
    if output_paths(output_root) != set(PROFILE_TARGETS):
        raise GrammarWaveError("candidate tree does not contain the exact eleven-file profile")
    entries: list[dict[str, object]] = []
    for relative in PROFILE_TARGETS:
        source = require_under(steam_root, steam_root / relative, "Steam source").read_bytes()
        candidate = require_under(output_root, output_root / relative, "candidate").read_bytes()
        if relative in CHANGED_PATHS:
            if candidate == source:
                raise GrammarWaveError(f"candidate did not change expected resource: {relative}")
            verify_patched_msggame(source, candidate, relative)
        elif candidate != source:
            raise GrammarWaveError(f"candidate changed retain-only resource: {relative}")
        entries.append({"path": relative, "source_sha256": sha256_bytes(source), "candidate_sha256": sha256_bytes(candidate), "source_size": len(source), "candidate_size": len(candidate)})
    return {
        "schema": MANIFEST_SCHEMA,
        "status": "PASS",
        "changed_paths": sorted(CHANGED_PATHS),
        "entries": entries,
        "literal_preserving_record_count_per_resource": len(LITERAL_PLANS),
        "static_record_count_per_resource": len(STATIC_PLANS),
    }


def build(steam_root: Path, output_root: Path, manifest_path: Path) -> dict[str, object]:
    steam_root = steam_root.resolve(strict=True)
    assert_baseline(steam_root)
    output_root = output_root.resolve()
    allowed_output_root = (REPO / "tmp" / WORKSTREAM.name).resolve()
    try:
        output_root.relative_to(allowed_output_root)
    except ValueError as exc:
        raise GrammarWaveError(f"candidate output escapes {allowed_output_root}") from exc
    temporary_parent = output_root.parent
    temporary_parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix="candidate-", dir=temporary_parent))
    try:
        for relative in PROFILE_TARGETS:
            source_path = require_under(steam_root, steam_root / relative, "Steam source")
            destination = temporary / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            source = source_path.read_bytes()
            destination.write_bytes(patch_msggame(source, relative) if relative in CHANGED_PATHS else source)
        if output_root.exists():
            shutil.rmtree(output_root)
        os.replace(temporary, output_root)
        report = verify_candidate(steam_root, output_root)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_bytes(canonical_json(report))
        return report
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--verify-only", action="store_true", help="verify the pre-apply candidate")
    mode.add_argument("--verify-installed", action="store_true", help="verify the exact post-apply target")
    args = parser.parse_args(argv)
    try:
        if args.verify_installed:
            report = verify_installed(args.steam_root)
        elif args.verify_only:
            report = verify_candidate(args.steam_root, args.output_root)
        else:
            report = build(args.steam_root, args.output_root, args.manifest)
    except (OSError, ValueError, GrammarWaveError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
