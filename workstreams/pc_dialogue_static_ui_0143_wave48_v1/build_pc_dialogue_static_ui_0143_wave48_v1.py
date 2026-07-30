#!/usr/bin/env python3
"""Build the private Wave 48 static-UI 0143-removal candidate.

This builder reads the exact W45 Steam PC Base and PK dialogue resources and
the pinned PC JP/EN/SC/TC reference files.  It rebuilds only the reviewed
sixteen static-UI families (thirty-two physical records), replacing each
literal with its reviewed Korean sentence and removing exactly one pinned
Japanese 01 43 inflection command.  It has no Steam apply, Git, network, or
release operation; its only write target is this workstream's private tmp
candidate directory.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")

BASE_RESOURCE = "MSG/JP/msggame.bin"
PK_RESOURCE = "MSG_PK/JP/msggame.bin"
RESOURCE_PATHS = {
    BASE_RESOURCE: STEAM_ROOT / BASE_RESOURCE,
    PK_RESOURCE: STEAM_ROOT / PK_RESOURCE,
}

# PC-only semantic anchors.  The original PC JP resources are deliberately
# separate from the current Korean W45 input profile; no Switch resource is
# read or named as an input.
REFERENCE_PATHS = {
    "BASE_JP": Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin"),
    "PK_JP": STEAM_ROOT
    / "KR_PATCH_BACKUP/file_only_transaction/steam-jp-1.1.7-v0.6.0/originals/MSG_PK/JP/msggame.bin",
    "EN": STEAM_ROOT / "MSG_PK/EN/msggame.bin",
    "SC": STEAM_ROOT / "MSG_PK/SC/msggame.bin",
    "TC": STEAM_ROOT / "MSG_PK/TC/msggame.bin",
}
REFERENCE_PROFILES = {
    "BASE_JP": {
        "size": 610_163,
        "sha256": "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
    },
    "PK_JP": {
        "size": 721_304,
        "sha256": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    },
    "EN": {
        "size": 737_377,
        "sha256": "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    },
    "SC": {
        "size": 540_757,
        "sha256": "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    },
    "TC": {
        "size": 546_853,
        "sha256": "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
    },
}

# The format/font helper is pinned so a later helper edit cannot silently
# change parsing, rebuilding, or Korean width measurement.
W27_HELPER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave27_static_quality_v1"
    / "build_pc_dialogue_quality_wave27_static_quality_v1.py"
)
W27_HELPER_SHA256 = "D63EA16EECF77F769C3B4AE21579A6C1227531E7FBDD0C07BB83C3E2B3A41438"

SCHEMA = "nobu16.kr.pc-dialogue-static-ui-0143-wave48.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-static-ui-0143-wave48-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-static-ui-0143-wave48-manifest.v1"
MAX_LINES = 3
MAX_LINE_PX = 912
RUNTIME_SLOT = b"\x01\x43\x01\x00\x00\x00"

# Exact current W45 Steam PC input profile.  Any drift refuses the build.
INPUT_PROFILES = {
    BASE_RESOURCE: {
        "size": 1_504_410,
        "sha256": "F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB",
    },
    PK_RESOURCE: {
        "size": 1_806_538,
        "sha256": "0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092",
    },
}

# These are re-derived and independently re-verified from the W45 profile,
# the reviewed targets below, and the pinned active PC font.
TARGET_PROFILES = {
    BASE_RESOURCE: {
        "size": 1_504_442,
        "sha256": "58DCCA79515C377A2382D893DA18C8504D0E16455C2458BE09F2167686433CED",
        "raw_size": 1_498_540,
        "raw_sha256": "FEA6A2EAB56305E6FAF76C6D0CE32FF87E399ACE38C47F480F1CA7F5393FC335",
    },
    PK_RESOURCE: {
        "size": 1_806_574,
        "sha256": "545AA7276D2B3D429FE4E58A9128AADAF4BDA4A4B6ADD58B095588EEA2759B79",
        "raw_size": 1_799_492,
        "raw_sha256": "1D05ADB2DC07F66FE913FD4626A1B7239CC0E910D66D2E6B8C807558901FA47E",
    },
}


class StaticUi0143Error(RuntimeError):
    """A pinned source, semantic anchor, record, or output guard drifted."""


@dataclass(frozen=True)
class Removed0143:
    offset: int
    expected_hex: str

    @property
    def value(self) -> bytes:
        return bytes.fromhex(self.expected_hex)


@dataclass(frozen=True)
class RecordPin:
    current_sha256: str
    current_size: int
    jp_sha256: str
    jp_size: int
    removed_0143: Removed0143
    target_sha256: str
    target_size: int
    target_line_widths_px: tuple[int, ...]


@dataclass(frozen=True)
class Family:
    name: str
    base_coordinate: tuple[int, int]
    pk_coordinate: tuple[int, int]
    base_current_literal: str
    pk_current_literal: str
    jp_literal: str
    base_target_literal: str
    pk_target_literal: str
    reference_literals: tuple[tuple[str, str], ...]
    base_pin: RecordPin
    pk_pin: RecordPin


@dataclass(frozen=True)
class Change:
    family: str
    resource: str
    coordinate: tuple[int, int]
    current_literals: tuple[str, ...]
    jp_literals: tuple[str, ...]
    target_literals: tuple[str, ...]
    reference_literals: tuple[tuple[str, str], ...]
    pin: RecordPin

    @property
    def coordinate_text(self) -> str:
        return f"{self.coordinate[0]}:{self.coordinate[1]}"

    @property
    def input_opaque_spans_hex(self) -> tuple[str, ...]:
        return ("", f"{self.pin.removed_0143.expected_hex}050505")

    @property
    def target_opaque_spans_hex(self) -> tuple[str, ...]:
        return ("", "050505")


@dataclass(frozen=True)
class CandidateBundle:
    packed: Mapping[str, bytes]
    raw: Mapping[str, bytes]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


def remove(offset: int, expected_hex: str) -> Removed0143:
    value = bytes.fromhex(expected_hex)
    if offset < 0 or len(value) != 6 or value[:2] != b"\x01\x43" or value == RUNTIME_SLOT:
        raise ValueError(f"invalid static 0143 removal: {offset}, {expected_hex}")
    return Removed0143(offset, expected_hex.upper())


# Each family is checked against original PC JP and PC EN/SC/TC before a
# Korean target is accepted.  The seven-field record pins independently bind
# current Korean input, JP source, exact removal offset, target record, and
# rendered line widths for every physical Base/PK record.
FAMILIES = (
    Family(
        "garrison",
        (6, 4146),
        (6, 4176),
        "영내의 병사가 적어지고 있어\n병력 확보를 진행하여",
        "영내의 병사가 적어지고 있어\n병력 확보를 진행하여",
        "領内の兵が少なくなっているため\n兵力の確保を進めて",
        "영내 병력이 줄고 있어\n병력 확보를 진행하고 있습니다.",
        "영내 병력이 줄고 있어\n병력 확보를 진행하고 있습니다.",
        (
            ("EN", "We are few in soldiers. We are planning to recruit."),
            ("SC", "为了准备下一次战役，\n正在确保兵力。"),
            ("TC", "為了準備下一場戰鬥，\n正在確保兵力。"),
        ),
        RecordPin("16500DC73C051E5CCDBA2BC11F986EB296C5C86F984FF3C4161DB5A7ADF65C6F", 69, "B41ABA7652157A72DC7F0FA6DD8901ABE3B66FD48931CE90343BA064C91EFFD8", 65, remove(60, "0143B2000000"), "8D2EDADD5D3A34716579D7766452CC2945E8D4F8B256A6123FD4AEF9C3C4654B", 69, (504, 720)),
        RecordPin("16500DC73C051E5CCDBA2BC11F986EB296C5C86F984FF3C4161DB5A7ADF65C6F", 69, "B41ABA7652157A72DC7F0FA6DD8901ABE3B66FD48931CE90343BA064C91EFFD8", 65, remove(60, "0143B2000000"), "8D2EDADD5D3A34716579D7766452CC2945E8D4F8B256A6123FD4AEF9C3C4654B", 69, (504, 720)),
    ),
    Family(
        "no_castle",
        (6, 4150),
        (6, 4180),
        "주위에 공략 가능한 성이 없으므로\n영지 발전에 힘써",
        "주위에 공략 가능한 성이 없으므로\n영지 발전에 힘써",
        "周囲に攻略可能な城がないため\n領地発展に努めて",
        "주위에 공략 가능한 성이 없으므로\n영지 발전에 힘쓰고 있습니다.",
        "주위에 공략 가능한 성이 없으므로\n영지 발전에 힘쓰고 있습니다.",
        (
            ("EN", "There is no castle in the vicinity for capturing. We are focusing on improving the land."),
            ("SC", "由于周围没有可攻略的城，\n因此专心发展领地。"),
            ("TC", "由於周邊無可攻略的城，\n因此正專心發展領地。"),
        ),
        RecordPin("7942946EDC3D1C85387EB3088470E61406E60CD3DC53F9EF934CA27DBF282ED4", 71, "2778BAF717AB10A2BBA09D9CFC4F61C8A374B57EF6C5A9F6531357D7156EFD26", 61, remove(62, "0143B2000000"), "777D3D17BC4315A12D5825976BEC521B66CCBE9020004441B9D269F560C67429", 79, (768, 672)),
        RecordPin("7942946EDC3D1C85387EB3088470E61406E60CD3DC53F9EF934CA27DBF282ED4", 71, "2778BAF717AB10A2BBA09D9CFC4F61C8A374B57EF6C5A9F6531357D7156EFD26", 61, remove(62, "0143B2000000"), "777D3D17BC4315A12D5825976BEC521B66CCBE9020004441B9D269F560C67429", 79, (768, 672)),
    ),
    Family(
        "dispatch",
        (6, 4171),
        (6, 4201),
        "우리 군단에서\n일부 부대를 파견",
        "우리 군단에서\n일부 부대를 파견",
        "我が軍団から\n一部の部隊を派遣",
        "우리 군단에서\n일부 부대를 파견했습니다.",
        "우리 군단에서\n일부 부대를 파견했습니다.",
        (
            ("EN", "A few units from our province have been dispatched."),
            ("SC", "已从我方军团\n派遣了一部分部队。"),
            ("TC", "現已自我的軍團派遣了一部分部隊。"),
        ),
        RecordPin("6FA6120E0DD9374E6B78F42DAA6C1A04AB68426AA1601AC008CEA2768E1967DB", 49, "930D4B13C8244F30E42079659B70F4A9CEABE251F1A8A59BE9E6465F05BAA338", 45, remove(40, "014390010000"), "CCFD0361BD44A8A78EE6A0C0068CC1078DEA7BF04CD776EF09D8A130EC08D323", 53, (312, 600)),
        RecordPin("4D9734BF124CBD981362571967C8A1C17FB72B3FB0BE41C3DA1492CC0402D75D", 49, "2DD92D60F3F369A1A873D7BBA1F23EF5F5FA127495169F6AA8121106D0A8BA6D", 45, remove(40, "014396010000"), "CCFD0361BD44A8A78EE6A0C0068CC1078DEA7BF04CD776EF09D8A130EC08D323", 53, (312, 600)),
    ),
    Family(
        "plot",
        (6, 4186),
        (6, 4216),
        "적의 성에 대한 조략을\n검토하도록 지시",
        "적의 성에 대한 조략을\n검토하도록 지시",
        "敵城への調略を\n検討するよう指示",
        "적의 성에 대한 조략을\n검토하도록 지시했습니다.",
        "적의 성에 대한 조략을\n검토하도록 지시했습니다.",
        (
            ("EN", "Give directions to begin planning covert actions on enemy targets."),
            ("SC", "指示针对敌人城的谋略\n进行检讨。"),
            ("TC", "指示針對敵城的謀略\n進行檢討。"),
        ),
        RecordPin("570044B035BB1FEF933409E96CDDA060E5602EB463A4896438AE1354F33D01EC", 57, "9C0BE0E5F6F4FF6D12956D728BEF704F4F6D396351AF4AFCE1CD6CE49915BCEE", 47, remove(48, "0143CC010000"), "1A00C80A7ACECE66F803654A2AB3D2A7A917117A1ED53D1518150B08E2185FC2", 61, (504, 576)),
        RecordPin("CE156DFACE2AC41216B00D51F6442F5FDB15D8136417CED5DADB1B0093ECB627", 57, "74F60FB7977DC56C2C7716DAC6DFAF127AB9C8EA73BC33A63B98975E25996409", 47, remove(48, "0143D2010000"), "1A00C80A7ACECE66F803654A2AB3D2A7A917117A1ED53D1518150B08E2185FC2", 61, (504, 576)),
    ),
    Family(
        "dissatisfied",
        (6, 4187),
        (6, 4217),
        "강한 불만을 품은 무장에게\n당가로 돌아서도록 권유해",
        "강한 불만을 품은 무장에게\n당가로 돌아서도록 권유해",
        "強い不満を抱く武将に\n当家への寝返りを持ちかけ",
        "강한 불만을 품은 무장에게\n당가로 돌아서도록 권유합니다.",
        "강한 불만을 품은 무장에게\n당가로 돌아서도록 권유합니다.",
        (
            ("EN", "Target discontented officers and persuade them to switch sides to our forces."),
            ("SC", "对本家有强烈不满的武将，\n有可能会叛乱。"),
            ("TC", "對抱持強烈不滿的武將\n提出投靠本家的提案。"),
        ),
        RecordPin("76EB02ED03259D7C0E26E63B2E7F4C0ADD6E6B2BECD84FD97753A45518A8CD36", 71, "05B96A36CED3B1D5C8399554D02BA96E558DF17003EA3EDCA352BE274BAF0D4A", 61, remove(62, "01433C040000"), "143545BF64923D02EAA3DF4BE2AFD60026D4AE2D651165051082C6AF28FDF4A1", 71, (600, 696)),
        RecordPin("B754150DF6ECEB969A279BC9459CA4CCE54D93F8A98FD553AD60A86FC6A47AFB", 71, "B5D52AB7181A5FA23C3FF9077A852775D89E37AC36C7A87C4EA7C20EDAF4AF9E", 61, remove(62, "014348040000"), "143545BF64923D02EAA3DF4BE2AFD60026D4AE2D651165051082C6AF28FDF4A1", 71, (600, 696)),
    ),
    Family(
        "pacify",
        (6, 4188),
        (6, 4218),
        "유사시에 원군을 요청할 수 있도록\n호족을 회유",
        "유사시에 원군을 요청할 수 있도록\n호족을 회유",
        "有事の際に援軍を要請できるよう\n国衆を懐柔",
        "유사시에 원군을 요청할 수 있도록\n호족을 회유합니다.",
        "유사시에 원군을 요청할 수 있도록\n호족을 회유합니다.",
        (
            ("EN", "Appease tribes to become able to request reinforcements in an emergency."),
            ("SC", "为了能在有必要时有援军支援，\n怀柔国众吧。"),
            ("TC", "為了能在緊急時提出援軍請求，\n對國眾實施懷柔政策。"),
        ),
        RecordPin("0BD157A1B2F3BD0A05CAEFAD7FA900B52152805E86D83563026FE737FC1B8A97", 65, "D0577F63B696019E7C3C24854CDD1CE1C3997754B18D3B1BC91D47A661DD7019", 57, remove(56, "0143CC010000"), "8619D94E7ABFB08D152760709BA37D8F313CB73EF849FB15A342B1635F2DB64B", 67, (768, 432)),
        RecordPin("28CBD4667BC7E5FE17379C49BCFC0EFF05A23EED5C1F8B55FFEF5A7BB19ABCF2", 65, "CCB86130E2ACB364612CD7F15378E4007E8A4C6DB76BE0C4BE90B07A42CEDF0A", 57, remove(56, "0143D2010000"), "8619D94E7ABFB08D152760709BA37D8F313CB73EF849FB15A342B1635F2DB64B", 67, (768, 432)),
    ),
    Family(
        "incorporate",
        (6, 4189),
        (6, 4219),
        "호족을 우리 가문의 산하에\n편입하도록 지시",
        "호족을 당가의 산하에\n편입하도록 지시",
        "国衆を当家の傘下に\n取り込むよう指示",
        "호족을 우리 가문의 산하에\n편입하도록 지시합니다.",
        "호족을 당가의 산하에\n편입하도록 지시합니다.",
        (
            ("EN", "Give directions to adopt a tribe under our banner."),
            ("SC", "下达指示，\n让国众加入本家的旗下吧。"),
            ("TC", "對國眾進行挖角，\n使其投入本家麾下。"),
        ),
        RecordPin("A5B62C39001CC7A805AEAF5DF5896E649A412F23F19CE7F58F6F4590E1887A49", 61, "113101853524A03301381D382D4BA31082C5453DEA47403078B0663CFB542A4A", 51, remove(52, "0143CC010000"), "CECD7E6DD16FA99574F907D0EA782068A9A59325BF82EEB6B88E91A872A26BD6", 63, (600, 528)),
        RecordPin("9D0FB5D1C5070067FC16ADB06ACE8D58DE4781E2D9EE1CE990D4B5A73CC163C6", 55, "0FD1A09BB137D4E7FB69B5FD626B10F991C79434E388E554A7BEE5718AEA0192", 51, remove(46, "0143D2010000"), "AD9893E33D7BBB523419612E52B1050F0F3541E43EC6F66FC30886797178FC88", 57, (480, 528)),
    ),
    Family(
        "ikki",
        (6, 4190),
        (6, 4220),
        "적 영지의 백성을 선동하여\n잇키를 일으켜 움직임을 봉",
        "적 영지의 백성을 선동하여\n잇키를 일으켜 움직임을 봉",
        "敵領の民を煽動し\n一揆を発生させて動きを封",
        "적 영지의 백성을 선동하여\n잇키를 일으켜 움직임을 봉쇄합니다.",
        "적 영지의 백성을 선동하여\n잇키를 일으켜 움직임을 봉쇄합니다.",
        (
            ("EN", "Incite a riot within enemy territory to cripple their mobility."),
            ("SC", "煽动敌方领地的民众发动起义，\n拖住部队的动作。"),
            ("TC", "煽動敵方領內居民發動一揆，\n藉以封住敵方行動。"),
        ),
        RecordPin("65B85A4A0F272661F4EE3B76BDF250BA2FE8B441500FC7AD110F6E4021AC649E", 73, "92F15F1E9B9A7EFBE620E023A1D5DC886EF0A59768AD008C94F2590496A5A3E4", 57, remove(64, "0143D2010000"), "D035F06434225CC2C9A54538C498C7BE147B876891A66AF1251BA27BB2866108", 77, (600, 816)),
        RecordPin("0FF40F012C65CBCE38DCCB3F782E124C5FF7E762ECD223D375B4A72E59274286", 73, "699C3DAFB412096EDA36DCBC65FCCABC85CB2A0931098E02BCE7AD719483237B", 57, remove(64, "0143D8010000"), "D035F06434225CC2C9A54538C498C7BE147B876891A66AF1251BA27BB2866108", 77, (600, 816)),
    ),
    Family(
        "sabotage",
        (6, 4191),
        (6, 4221),
        "적의 성에 파괴 공작을 명하여\n성의 내구와 병력에 손해를 입히",
        "적의 성에 파괴 공작을 명하여\n성의 내구와 병력에 손해를 입히",
        "敵城への破壊工作を命じ\n城の耐久と兵力に損害を与え",
        "적의 성에 파괴 공작을 명하여\n성의 내구와 병력에 피해를 입힙니다.",
        "적의 성에 파괴 공작을 명하여\n성의 내구와 병력에 피해를 입힙니다.",
        (
            ("EN", "Give a command to destabilize an enemy castle\u00d6s structure and cause damages to their forces and castle HP."),
            ("SC", "下令破坏敌方城池，\n对城池的耐久和兵力造成损失。"),
            ("TC", "對敵方城進行破壞工作，\n對敵城耐久值及兵力發生損害。"),
        ),
        RecordPin("1415081A304D450032CF49AF7C061A4E460842A2B88E2D3B48C3C98E40263554", 83, "5ADFFEF87DDC7852039C02A00F9C409397C6687F049C54689E3BE6990F0EF032", 65, remove(74, "01433C040000"), "24DDDD0CA917F3D9C55D46EC37E2F0C7357C3E76D58E1D6CE774C4AADEBC4913", 83, (672, 840)),
        RecordPin("A8C4AB9DA395AC4AEEFDF49BB3F4B650EBB569131C089DF8C664AE223C03BE37", 83, "BAC9D44B3F0EB29E9D5E119A93EEB1DC64137FB6933B3CE292E525DF61F76AF2", 65, remove(74, "014348040000"), "24DDDD0CA917F3D9C55D46EC37E2F0C7357C3E76D58E1D6CE774C4AADEBC4913", 83, (672, 840)),
    ),
    Family(
        "gift",
        (6, 4192),
        (6, 4222),
        "가보를 준비시켜\n외교 자세를 개선",
        "가보를 준비시켜\n외교 자세를 개선",
        "家宝を用意させ\n外交姿勢を改善",
        "가보를 준비시켜\n외교 자세를 개선합니다.",
        "가보를 준비시켜\n외교 자세를 개선합니다.",
        (
            ("EN", "Prepare treasures to present to improve diplomatic standing."),
            ("SC", "准备好家宝，\n改善外交态势。"),
            ("TC", "準備家寶\n以用於改善外交姿態。"),
        ),
        RecordPin("25161BE6E914D401E691EC38A63DBCB9E665E9892DA499F67CEB5C55AF4881E9", 51, "B75709E318AF9937204448AB90F9919FCD2BC885DF13E48A5DCC453C789B07D8", 45, remove(42, "0143CC010000"), "2A9B1FCC6537CF81197FE1A0A0CC18518CF1B16019D487AE3D3CBD82CA7CF77A", 53, (360, 552)),
        RecordPin("CE818BA4F71CE5EE90D7992C54C876218C49794A4FA768E826EA014EC477D54F", 51, "D9DDC592F20343A786110F332911006E0DD24ACB3C912841821490935CFF00D3", 45, remove(42, "0143D2010000"), "2A9B1FCC6537CF81197FE1A0A0CC18518CF1B16019D487AE3D3CBD82CA7CF77A", 53, (360, 552)),
    ),
    Family(
        "arson",
        (6, 4193),
        (6, 4223),
        "적의 성에 불을 지르게 하여\n병력과 병량에 손해를 입히",
        "적의 성에 불을 지르게 하여\n병력과 병량에 손해를 입히",
        "敵城に火を放たせ\n兵力と兵糧に損害を与え",
        "적의 성에 불을 지르게 하여\n병력과 병량에 피해를 입힙니다.",
        "적의 성에 불을 지르게 하여\n병력과 병량에 피해를 입힙니다.",
        (
            ("EN", "Set fire to an enemy\u00d6s castle to cause damages to their forces and supplies."),
            ("SC", "在敌方城池放火，\n对其兵力和军粮造成损害。"),
            ("TC", "對敵方城放火，\n使敵方兵力及軍糧發生損害。"),
        ),
        RecordPin("FB3D3AA4C37B155BF7488DD2FB90435F92AD8F4DC48EBDBAC3D2B14D6F72548F", 75, "E21C9FD32E223E9B880E12DD33FEEE875D8F1AECF8D0D527D3FD76FC2A61A2CC", 55, remove(66, "01433C040000"), "254C7C5AF2E17CF437335EADCEBC0D63535E79E7A63C09596193FAD2FFD52B17", 75, (624, 720)),
        RecordPin("F243B22EDDF4FC9025AC8D6ED3E725ED16E466FECD4AE242BBA29547F74BEEB9", 75, "97FCD9C8F52EDAA09FD9790DC010719998427FC1354089C248F6EB989863DC6F", 55, remove(66, "014348040000"), "254C7C5AF2E17CF437335EADCEBC0D63535E79E7A63C09596193FAD2FFD52B17", 75, (624, 720)),
    ),
    Family(
        "rumor",
        (6, 4194),
        (6, 4224),
        "적성 장수의 충성을 흔들기 위해\n당주의 나쁜 소문을 퍼뜨리",
        "적성 장수의 충성을 흔들기 위해\n당주의 나쁜 소문을 퍼뜨리",
        "敵城の将の忠誠を揺るがすため\n当主の悪しき噂を吹き込",
        "적성 장수의 충성을 흔들기 위해\n당주의 나쁜 소문을 퍼뜨립니다.",
        "적성 장수의 충성을 흔들기 위해\n당주의 나쁜 소문을 퍼뜨립니다.",
        (
            ("EN", "We\u00d6ll spread rumors on their clan leader to shake the loyalty of the enemy\u00d6s officer."),
            ("SC", "为了动摇敌城将领的忠诚，\n散播当主的恶性谣言。"),
            ("TC", "散布不利敵方家主的流言，\n使敵城將領忠誠產生動搖。"),
        ),
        RecordPin("7C871F23DF70BACC6F078DE8BF1D4E7EDB4ADD9F79574E680BBEC24C5EB70807", 79, "5463238A7AC7F5259A009EC0338CCEB786ACD0C79571889A858669F1C302A7C3", 67, remove(70, "0143A0030000"), "B0E3026498B79E9A89DEBCA82132DC79197D551F7A7741A1BF37594E9F2B2FDA", 79, (720, 720)),
        RecordPin("CD7786C7F302948D4B71D479B29F314C94140E4A4B5C7387A053F85462C43906", 79, "E0C7FB252330828E4389B0751CB6AF8393C097E54436AEAC351B377E20E15DA2", 67, remove(70, "0143AC030000"), "B0E3026498B79E9A89DEBCA82132DC79197D551F7A7741A1BF37594E9F2B2FDA", 79, (720, 720)),
    ),
    Family(
        "peasant",
        (6, 4195),
        (6, 4225),
        "석고를 늘리기 위해\n농촌을 장악",
        "석고를 늘리기 위해\n농촌을 장악",
        "石高を増やすため\n農村を掌握",
        "석고를 늘리기 위해\n농촌을 장악합니다.",
        "석고를 늘리기 위해\n농촌을 장악합니다.",
        (
            ("EN", "Seize farm and bolster crops."),
            ("SC", "为了增加石高，\n需掌控农村。"),
            ("TC", "致力將農村納入掌控\n以增加石高。"),
        ),
        RecordPin("E07C71E243647BE240BC501130C642AD135F4574658612B8920D6C350764BB56", 49, "502C153670FEA5AD3BC41452B0D61730A121C0E701812DA223C9DD0A4A99B2B4", 43, remove(40, "0143CC010000"), "E889DA5A51407E9EE3B98F05F976592CEF48330812E71E6519819E109528219A", 51, (432, 432)),
        RecordPin("4FD098A46FB312387AE14D4168045F9150387C1A33DF4BF0E458B855B8EAFE9A", 49, "65FF6EF033E8F364885441B430DCCA880B4B1EEEBF2E3720A47003682FEC6910", 43, remove(40, "0143D2010000"), "E889DA5A51407E9EE3B98F05F976592CEF48330812E71E6519819E109528219A", 51, (432, 432)),
    ),
    Family(
        "commerce",
        (6, 4196),
        (6, 4226),
        "금전 수입을 늘리기 위해\n상업을 진흥",
        "금전 수입을 늘리기 위해\n상업을 진흥",
        "金銭収入を増やすため\n商業を振興",
        "금전 수입을 늘리기 위해\n상업을 진흥합니다.",
        "금전 수입을 늘리기 위해\n상업을 진흥합니다.",
        (
            ("EN", "Promote commerce and increase gold income."),
            ("SC", "为了增加金钱收入，\n需要振兴商业。"),
            ("TC", "致力振興商業\n以增加金錢收入。"),
        ),
        RecordPin("E93D9C7C5F5B787E65FC8327C2F8C7331729DFDD08527B5AFAC95F15C2D7F2CE", 55, "EC5BE283102B34CBE3D24C1C6C64D580510F190A391E10E871631487B2C4F61F", 47, remove(46, "0143CC010000"), "6436DD6283865C51DF1BED8158E2FAC42BACFF098092D5ACAF82D3A975404F76", 57, (552, 432)),
        RecordPin("C2F5F90840FEE29B3B0A9F9BFEEBC0BD4D382D2A18D1874F613F513704D82D7B", 55, "BAD681152D7AAA45BA52C841FFE981FC1FE75239247B6006D34F20631D8D901B", 47, remove(46, "0143D2010000"), "6436DD6283865C51DF1BED8158E2FAC42BACFF098092D5ACAF82D3A975404F76", 57, (552, 432)),
    ),
    Family(
        "wall",
        (6, 4197),
        (6, 4227),
        "침공에 대비해 외벽 수복을 명하여\n성의 내구를 회복",
        "침공에 대비해 외벽 수복을 명하여\n성의 내구를 회복",
        "侵攻に備えて外壁の修復を命じ\n城の耐久を回復",
        "침공에 대비해 외벽 수복을 명하여\n성의 내구를 회복합니다.",
        "침공에 대비해 외벽 수복을 명하여\n성의 내구를 회복합니다.",
        (
            ("EN", "Order the repair of castle walls to restore castle HP and prepare for invasions."),
            ("SC", "为了应对侵略，下令修复外墙，\n恢复城池的耐久。"),
            ("TC", "為防範敵人進攻而下令修復外壁，\n恢復城耐久值。"),
        ),
        RecordPin("BB1D12D1C68FFF54045591B0155716CC4FDD09172FF60BA88835B2D2F3AB4920", 71, "51C14C628980100A66886AF0ACDBBD5CF653D256B9863725DCCDB4D435389234", 59, remove(62, "0143CC010000"), "2C0E2A09EDFC2C1821ECEA98FA6E9E6E03B73A7B38E8276FD5DC08F5BD4492B6", 73, (768, 552)),
        RecordPin("C145ADEF6D7436338B2BE3DDDAA2FD2C388A545D287C406FFFDABFCD99E90369", 71, "E3574CFB21A798EC7402EB9DCC6DA97A9D34B22ECE0AAE837688C2934D4CA0B0", 59, remove(62, "0143D2010000"), "2C0E2A09EDFC2C1821ECEA98FA6E9E6E03B73A7B38E8276FD5DC08F5BD4492B6", 73, (768, 552)),
    ),
    Family(
        "recruit",
        (6, 4198),
        (6, 4228),
        "세력 내의 유망한 낭인을\n찾아내어 등용",
        "세력 내의 유망한 낭인을\n찾아내어 등용",
        "勢力下の有望な牢人を\n探しだして登用",
        "세력 내의 유망한 낭인을\n찾아내어 등용합니다.",
        "세력 내의 유망한 낭인을\n찾아내어 등용합니다.",
        (
            ("EN", "Seek out and employ talented r\u00aanin."),
            ("SC", "从势力中寻找有前途浪人\n并登用。"),
            ("TC", "尋找勢力範圍內之賢能浪人\n以進行登庸。"),
        ),
        RecordPin("ADA2720BF46F8492D2F0AE3DA6C6240B05719C7453D3B14970899DDEF4A454A6", 57, "14F8D36906358CD4960DBA9D30D685A4DFFA583DF7EEC07D98AB27EA7F67A5BC", 51, remove(48, "0143CC010000"), "7C53D0E2455AB2F0F81A08B3431F86FCBC5A37BC36FAD17353D3D2DE0D33A700", 59, (552, 480)),
        RecordPin("1AC82EA14206F16FE7E2034ADAE9240CF4CE83BE537ED52E3740E3D0D2D77774", 57, "6D80D7AD7320487557F03E4605FBB1DCA27464B26712281C41E10508D4E9F709", 51, remove(48, "0143D2010000"), "7C53D0E2455AB2F0F81A08B3431F86FCBC5A37BC36FAD17353D3D2DE0D33A700", 59, (552, 480)),
    ),
)

if len(FAMILIES) != 16:
    raise RuntimeError("Wave 48 must declare exactly sixteen semantic families")
if len({family.base_coordinate for family in FAMILIES}) != len(FAMILIES):
    raise RuntimeError("duplicate Wave 48 Base coordinate")
if len({family.pk_coordinate for family in FAMILIES}) != len(FAMILIES):
    raise RuntimeError("duplicate Wave 48 PK coordinate")

CHANGES = tuple(
    Change(
        family.name,
        resource,
        coordinate,
        (current_literal,),
        (family.jp_literal,),
        (target_literal,),
        family.reference_literals,
        pin,
    )
    for family in FAMILIES
    for resource, coordinate, current_literal, target_literal, pin in (
        (BASE_RESOURCE, family.base_coordinate, family.base_current_literal, family.base_target_literal, family.base_pin),
        (PK_RESOURCE, family.pk_coordinate, family.pk_current_literal, family.pk_target_literal, family.pk_pin),
    )
)
if len(CHANGES) != 32 or len({(change.resource, change.coordinate) for change in CHANGES}) != len(CHANGES):
    raise RuntimeError("Wave 48 must declare exactly thirty-two unique physical records")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise StaticUi0143Error(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def reject_switch(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    if any("switch" in part.casefold() for part in resolved.parts):
        raise StaticUi0143Error(f"Nintendo Switch input is forbidden: {label}")
    return resolved


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise StaticUi0143Error(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def load_w27() -> Any:
    require(W27_HELPER.is_file(), "Wave 27 format helper is absent")
    require(sha256_path(W27_HELPER) == W27_HELPER_SHA256, "Wave 27 format helper differs")
    spec = importlib.util.spec_from_file_location("wave48_pinned_wave27", W27_HELPER)
    if spec is None or spec.loader is None:
        raise StaticUi0143Error("cannot load pinned Wave 27 helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W27 = load_w27()


def opaque_spans_with_offsets(record: Any) -> tuple[tuple[int, bytes], ...]:
    cursor = 0
    spans: list[tuple[int, bytes]] = []
    for literal in W27.parse_record_literals(record):
        spans.append((cursor, record.data[cursor : literal.marker_offset]))
        cursor = literal.marker_end
    spans.append((cursor, record.data[cursor:]))
    return tuple(spans)


def span_hexes(record: Any) -> tuple[str, ...]:
    return tuple(value.hex().upper() for _offset, value in opaque_spans_with_offsets(record))


def commands_0143(record: Any) -> tuple[tuple[int, bytes], ...]:
    commands: list[tuple[int, bytes]] = []
    for span_offset, span in opaque_spans_with_offsets(record):
        for index in range(len(span) - 5):
            if span[index : index + 2] == b"\x01\x43":
                commands.append((span_offset + index, span[index : index + 6]))
    return tuple(commands)


def opcodes_02xx(record: Any) -> tuple[str, ...]:
    values: list[str] = []
    for _offset, span in opaque_spans_with_offsets(record):
        for index in range(len(span) - 1):
            if span[index] == 0x02:
                values.append(span[index : index + 2].hex().upper())
    return tuple(values)


def validate_target_literal(value: str, label: str) -> None:
    require(value != "", f"empty target literal: {label}")
    encoded = value.encode("utf-16le")
    require(W27.LITERAL_START not in encoded and W27.LITERAL_END not in encoded, f"reserved literal marker: {label}")
    for character in value:
        if ord(character) < 0x20 and character not in "\n\r":
            raise StaticUi0143Error(f"control character in target literal: {label}")


def removal_map(change: Change, record: Any) -> dict[int, bytes]:
    commands = dict(commands_0143(record))
    expected = change.pin.removed_0143
    actual = commands.get(expected.offset)
    require(
        actual == expected.value,
        f"0143 removal pin differs: {change.family} {change.coordinate_text}; expected {expected.expected_hex} at {expected.offset}, got {actual.hex().upper() if actual else 'absent'}",
    )
    require(len(commands) == 1, f"unreviewed 0143 command exists: {change.family} {change.coordinate_text}")
    require(actual != RUNTIME_SLOT, f"runtime 014301 slot is forbidden in Wave 48: {change.family} {change.coordinate_text}")
    return {expected.offset: expected.value}


def strip_exact_removals(span_offset: int, span: bytes, removals: Mapping[int, bytes]) -> bytes:
    output = bytearray()
    cursor = 0
    while cursor < len(span):
        absolute = span_offset + cursor
        command = removals.get(absolute)
        if command is not None:
            require(span[cursor : cursor + len(command)] == command, f"pinned 0143 shifted at offset {absolute}")
            cursor += len(command)
            continue
        output.append(span[cursor])
        cursor += 1
    return bytes(output)


def rebuild_record(change: Change, before: Any) -> bytes:
    source_literals = W27.literal_texts(before)
    require(source_literals == change.current_literals, f"current literal differs: {change.family} {change.coordinate_text}")
    require(len(source_literals) == len(change.target_literals) == 1, f"literal-slot count is not one: {change.family} {change.coordinate_text}")
    removals = removal_map(change, before)
    output = bytearray()
    cursor = 0
    for literal, target in zip(W27.parse_record_literals(before), change.target_literals):
        validate_target_literal(target, f"{change.family} {change.coordinate_text}")
        output.extend(strip_exact_removals(cursor, before.data[cursor : literal.marker_offset], removals))
        output.extend(W27.LITERAL_START)
        output.extend(target.encode("utf-16le"))
        output.extend(W27.LITERAL_END)
        cursor = literal.marker_end
    output.extend(strip_exact_removals(cursor, before.data[cursor:], removals))
    return bytes(output)


def source_key_for(change: Change) -> str:
    return "BASE_JP" if change.resource == BASE_RESOURCE else "PK_JP"


def validate_reference_anchors() -> tuple[dict[str, Mapping[tuple[int, int], Any]], dict[str, Any]]:
    archives: dict[str, Mapping[tuple[int, int], Any]] = {}
    report_profiles: dict[str, dict[str, Any]] = {}
    for label, path in REFERENCE_PATHS.items():
        checked = reject_switch(path, f"PC reference {label}")
        profile = REFERENCE_PROFILES[label]
        require(
            checked.stat().st_size == profile["size"] and sha256_path(checked) == profile["sha256"],
            f"PC reference profile differs: {label}",
        )
        packed = checked.read_bytes()
        W27.validate_raw_roundtrip(packed, f"PC reference {label}")
        archives[label] = W27.records_by_coordinate(packed)
        report_profiles[label] = {
            "path": str(checked),
            "size": profile["size"],
            "sha256": profile["sha256"],
        }

    family_rows: list[dict[str, Any]] = []
    for family in FAMILIES:
        base_jp = archives["BASE_JP"].get(family.base_coordinate)
        pk_jp = archives["PK_JP"].get(family.pk_coordinate)
        require(base_jp is not None and pk_jp is not None, f"PC JP anchor missing: {family.name}")
        require(W27.literal_texts(base_jp) == (family.jp_literal,), f"Base JP semantic anchor differs: {family.name}")
        require(W27.literal_texts(pk_jp) == (family.jp_literal,), f"PK JP semantic anchor differs: {family.name}")
        require(base_jp.data.endswith(W27.RECORD_TERMINATOR) and pk_jp.data.endswith(W27.RECORD_TERMINATOR), f"JP terminator differs: {family.name}")
        anchors: dict[str, str] = {}
        for language, expected_literal in family.reference_literals:
            record = archives[language].get(family.pk_coordinate)
            require(record is not None, f"PC {language} anchor missing: {family.name}")
            require(W27.literal_texts(record) == (expected_literal,), f"PC {language} semantic anchor differs: {family.name}")
            require(record.data.endswith(W27.RECORD_TERMINATOR), f"PC {language} terminator differs: {family.name}")
            anchors[language] = expected_literal
        family_rows.append(
            {
                "family": family.name,
                "base_coordinate": f"{family.base_coordinate[0]}:{family.base_coordinate[1]}",
                "pk_coordinate": f"{family.pk_coordinate[0]}:{family.pk_coordinate[1]}",
                "jp_literal": family.jp_literal,
                "pc_reference_literals": anchors,
            }
        )
    return archives, {"profiles": report_profiles, "families": family_rows}


def validate_change(change: Change, before: Any, jp_record: Any, advance: Any, *, enforce_pins: bool) -> tuple[bytes, dict[str, Any]]:
    pin = change.pin
    require(sha256_bytes(before.data) == pin.current_sha256, f"current record hash differs: {change.family} {change.coordinate_text}")
    require(len(before.data) == pin.current_size, f"current record size differs: {change.family} {change.coordinate_text}")
    require(W27.literal_texts(before) == change.current_literals, f"current literal differs: {change.family} {change.coordinate_text}")
    require(span_hexes(before) == change.input_opaque_spans_hex, f"current opaque spans differ: {change.family} {change.coordinate_text}")
    require(before.data.endswith(W27.RECORD_TERMINATOR), f"current terminator differs: {change.family} {change.coordinate_text}")
    require(opcodes_02xx(before) == (), f"02xx opcode is forbidden in Wave 48: {change.family} {change.coordinate_text}")
    require(all(command != RUNTIME_SLOT for _offset, command in commands_0143(before)), f"014301 runtime slot is forbidden in Wave 48: {change.family} {change.coordinate_text}")

    require(sha256_bytes(jp_record.data) == pin.jp_sha256, f"JP record hash differs: {change.family} {change.coordinate_text}")
    require(len(jp_record.data) == pin.jp_size, f"JP record size differs: {change.family} {change.coordinate_text}")
    require(W27.literal_texts(jp_record) == change.jp_literals, f"JP literal differs: {change.family} {change.coordinate_text}")
    require(jp_record.data.endswith(W27.RECORD_TERMINATOR), f"JP terminator differs: {change.family} {change.coordinate_text}")

    target_text = "".join(change.target_literals)
    require(target_text.count("\n") + 1 == 2, f"Wave 48 target must remain exactly two lines: {change.family} {change.coordinate_text}")
    require(target_text.count("\n") == "".join(change.current_literals).count("\n"), f"manual LF topology differs: {change.family} {change.coordinate_text}")
    layout = W27.line_layout(change.target_literals, advance)
    require(layout["line_count"] <= MAX_LINES, f"more than three lines: {change.family} {change.coordinate_text}")
    require(layout["max_width_px"] <= MAX_LINE_PX, f"font width exceeds {MAX_LINE_PX}: {change.family} {change.coordinate_text}")
    require(not layout["wide_fallback_codepoints"], f"fallback glyph used: {change.family} {change.coordinate_text}")

    rebuilt = rebuild_record(change, before)
    after = W27.MsgGameRecord(before.block_id, before.record_id, before.relative_offset, rebuilt)
    require(W27.literal_texts(after) == change.target_literals, f"target literal differs: {change.family} {change.coordinate_text}")
    require(W27.marker_topology(after) == W27.marker_topology(before), f"literal marker topology differs: {change.family} {change.coordinate_text}")
    require(span_hexes(after) == change.target_opaque_spans_hex, f"target opaque spans differ: {change.family} {change.coordinate_text}")
    require(after.data.endswith(W27.RECORD_TERMINATOR), f"target terminator differs: {change.family} {change.coordinate_text}")
    require(opcodes_02xx(after) == (), f"target 02xx opcode differs: {change.family} {change.coordinate_text}")
    require(commands_0143(after) == (), f"target retains 0143 command: {change.family} {change.coordinate_text}")
    require(RUNTIME_SLOT not in after.data, f"target retains 014301 slot: {change.family} {change.coordinate_text}")
    if enforce_pins:
        require(sha256_bytes(after.data) == pin.target_sha256, f"target record hash differs: {change.family} {change.coordinate_text}")
        require(len(after.data) == pin.target_size, f"target record size differs: {change.family} {change.coordinate_text}")
        require(tuple(layout["line_widths_px"]) == pin.target_line_widths_px, f"target line widths differ: {change.family} {change.coordinate_text}")
    return rebuilt, {
        "family": change.family,
        "resource": change.resource,
        "coordinate": change.coordinate_text,
        "current": {
            "record_sha256": pin.current_sha256,
            "record_size": pin.current_size,
            "literals": list(change.current_literals),
            "opaque_spans_hex": list(change.input_opaque_spans_hex),
        },
        "jp": {
            "record_sha256": pin.jp_sha256,
            "record_size": pin.jp_size,
            "literals": list(change.jp_literals),
        },
        "target": {
            "record_sha256": sha256_bytes(after.data),
            "record_size": len(after.data),
            "literals": list(change.target_literals),
            "line_count": layout["line_count"],
            "line_widths_px": list(layout["line_widths_px"]),
            "max_line_px": layout["max_width_px"],
            "opaque_spans_hex": list(change.target_opaque_spans_hex),
        },
        "removed_0143": {
            "offset": pin.removed_0143.offset,
            "hex": pin.removed_0143.expected_hex,
        },
        "input_02xx_opcodes": [],
        "target_02xx_opcodes": [],
        "runtime_slot_014301_present": False,
    }


def load_current() -> tuple[dict[str, bytes], dict[str, Mapping[tuple[int, int], Any]]]:
    packed_by_resource: dict[str, bytes] = {}
    records_by_resource: dict[str, Mapping[tuple[int, int], Any]] = {}
    for resource, path in RESOURCE_PATHS.items():
        checked = reject_switch(path, f"Steam PC input {resource}")
        packed = checked.read_bytes()
        profile = INPUT_PROFILES[resource]
        require(
            len(packed) == profile["size"] and sha256_bytes(packed) == profile["sha256"],
            f"current W45 Steam profile differs: {resource}",
        )
        W27.validate_raw_roundtrip(packed, f"current W45 Steam {resource}")
        packed_by_resource[resource] = packed
        records_by_resource[resource] = W27.records_by_coordinate(packed)
    return packed_by_resource, records_by_resource


def build_unpinned() -> CandidateBundle:
    reference_archives, reference_report = validate_reference_anchors()
    packed_by_resource, records_by_resource = load_current()
    advance, font = W27.load_font_advance()
    replacements: dict[str, dict[tuple[int, int], bytes]] = {resource: {} for resource in RESOURCE_PATHS}
    rows: list[dict[str, Any]] = []
    for change in CHANGES:
        before = records_by_resource[change.resource].get(change.coordinate)
        jp_record = reference_archives[source_key_for(change)].get(change.coordinate)
        require(before is not None and jp_record is not None, f"record is absent: {change.family} {change.coordinate_text}")
        require(change.coordinate not in replacements[change.resource], f"duplicate replacement: {change.resource} {change.coordinate_text}")
        replacement, row = validate_change(change, before, jp_record, advance, enforce_pins=False)
        replacements[change.resource][change.coordinate] = replacement
        rows.append(row)

    packed_output: dict[str, bytes] = {}
    raw_output: dict[str, bytes] = {}
    for resource, packed in packed_by_resource.items():
        candidate = W27.rebuild_packed_msggame(packed, replacements[resource])
        W27.validate_raw_roundtrip(candidate, f"Wave 48 candidate {resource}")
        _header, raw = W27.decompress_wrapper(candidate)
        before = records_by_resource[resource]
        after = W27.records_by_coordinate(candidate)
        require(set(before) == set(after), f"record topology differs: {resource}")
        changed = {coordinate for coordinate in before if before[coordinate].data != after[coordinate].data}
        expected = {change.coordinate for change in CHANGES if change.resource == resource}
        require(changed == expected, f"changed record scope differs: {resource}")
        packed_output[resource] = candidate
        raw_output[resource] = raw

    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "platform": "PC only",
            "switch_korean_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "pin_derivation": {
            "input_baseline": "exact current W45 Base/PK Steam profile",
            "semantic_references": "pinned PC JP plus PC EN/SC/TC literals",
            "target_pin_status": "independently re-derived and matched the reviewed Wave 48 target pins",
        },
        "pinned_format_helper_sha256": W27_HELPER_SHA256,
        "input": INPUT_PROFILES,
        "pc_reference_anchors": reference_report,
        "font": font,
        "family_count": len(FAMILIES),
        "changed_record_count": len(CHANGES),
        "runtime_display_qa_required_before_application": True,
        "records": rows,
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {
            resource: {
                "input": INPUT_PROFILES[resource],
                "changed_coordinates": [change.coordinate_text for change in CHANGES if change.resource == resource],
            }
            for resource in RESOURCE_PATHS
        },
        "family_count": len(FAMILIES),
        "changed_record_count": len(CHANGES),
        "static_0143_removal_only": True,
        "02xx_records": 0,
        "014301_runtime_slots": 0,
        "runtime_display_qa_required_before_application": True,
        "switch_korean_input": "forbidden",
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
    }
    return CandidateBundle(packed_output, raw_output, audit, manifest)


def require_all_target_pins() -> None:
    for resource, profile in TARGET_PROFILES.items():
        require(profile["size"] > 0 and len(profile["sha256"]) == 64, f"target packed pin is absent: {resource}")
        require(profile["raw_size"] > 0 and len(profile["raw_sha256"]) == 64, f"target raw pin is absent: {resource}")
    for change in CHANGES:
        pin = change.pin
        require(
            len(pin.target_sha256) == 64 and pin.target_size > 0 and len(pin.target_line_widths_px) == 2,
            f"target record pin is absent: {change.family} {change.coordinate_text}",
        )


def prepare_candidate() -> CandidateBundle:
    require_all_target_pins()
    bundle = build_unpinned()
    advance, _font = W27.load_font_advance()
    reference_archives, _references = validate_reference_anchors()
    for resource, packed in bundle.packed.items():
        profile = TARGET_PROFILES[resource]
        require(len(packed) == profile["size"] and sha256_bytes(packed) == profile["sha256"], f"target packed profile differs: {resource}")
        raw = bundle.raw[resource]
        require(len(raw) == profile["raw_size"] and sha256_bytes(raw) == profile["raw_sha256"], f"target raw profile differs: {resource}")
        after = W27.records_by_coordinate(packed)
        current_records = W27.records_by_coordinate(RESOURCE_PATHS[resource].read_bytes())
        for change in (entry for entry in CHANGES if entry.resource == resource):
            before = current_records[change.coordinate]
            jp_record = reference_archives[source_key_for(change)][change.coordinate]
            validate_change(change, before, jp_record, advance, enforce_pins=True)
            require(
                sha256_bytes(after[change.coordinate].data) == change.pin.target_sha256,
                f"output target record differs: {change.family} {change.coordinate_text}",
            )
    audit = dict(bundle.audit)
    audit["target"] = TARGET_PROFILES
    manifest = dict(bundle.manifest)
    manifest["resources"] = {
        resource: {**manifest["resources"][resource], "output": TARGET_PROFILES[resource]}
        for resource in RESOURCE_PATHS
    }
    manifest["audit_sha256"] = sha256_bytes(canonical_json(audit))
    return CandidateBundle(bundle.packed, bundle.raw, audit, manifest)


def derived_pins() -> dict[str, Any]:
    bundle = build_unpinned()
    records = {f"{row['resource']}:{row['coordinate']}": row["target"] for row in bundle.audit["records"]}
    return {
        "target_profiles": {
            resource: {
                "size": len(packed),
                "sha256": sha256_bytes(packed),
                "raw_size": len(bundle.raw[resource]),
                "raw_sha256": sha256_bytes(bundle.raw[resource]),
            }
            for resource, packed in bundle.packed.items()
        },
        "target_records": records,
    }


def write_candidate(bundle: CandidateBundle) -> Path:
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT))
    try:
        for resource, packed in bundle.packed.items():
            target = stage / resource
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(packed)
        (stage / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (stage / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        if output.exists():
            shutil.rmtree(output)
        os.replace(stage, output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return output


def verify_private() -> dict[str, Any]:
    bundle = prepare_candidate()
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    for resource, packed in bundle.packed.items():
        path = output / resource
        require(path.is_file() and path.read_bytes() == packed, f"private candidate differs: {resource}")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require((output / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "private manifest differs")
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "family_count": len(FAMILIES),
        "changed_record_count": len(CHANGES),
        "steam_game_resource_written": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify-private", "derive-pins"))
    args = parser.parse_args(argv)
    if args.command == "derive-pins":
        result = derived_pins()
    elif args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        result = {
            "candidate_root": output.relative_to(REPO).as_posix(),
            "family_count": len(FAMILIES),
            "changed_record_count": len(CHANGES),
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
