#!/usr/bin/env python3
"""Build a private, static-only Steam-PC dialogue-quality candidate.

Wave 50 contains only the reviewed block 9 battle-dialogue corrections and
the paired block 12:51 family-status sentence.  The Korean target text was
reviewed against pristine Steam-PC Japanese with PC EN/SC/TC used as context;
Nintendo Switch Korean is deliberately not read.  Runtime ``02xx`` slots and
all ``0143`` command records are forbidden.  This script has no Steam apply,
transaction, Git, network, or release operation and writes only below its
private ``tmp`` directory.
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
RESOURCE_ORDER = (BASE_RESOURCE, PK_RESOURCE)

# The Base original is the preserved PC-Japanese game resource.  PK Japanese
# comes from the exact Steam 1.1.7 original backup used by the prior W45
# transaction.  Neither path may resolve through a Switch directory.
BASE_PC_JP_SOURCE = Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin")
PK_PC_JP_SOURCE = (
    STEAM_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / PK_RESOURCE
)

W27_HELPER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave27_static_quality_v1"
    / "build_pc_dialogue_quality_wave27_static_quality_v1.py"
)
W27_HELPER_SHA256 = "D63EA16EECF77F769C3B4AE21579A6C1227531E7FBDD0C07BB83C3E2B3A41438"

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave50-static-blocks9-12.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave50-static-blocks9-12-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave50-static-blocks9-12-manifest.v1"
MAX_LINES = 3
MAX_LINE_PX = 912


class Wave50Error(RuntimeError):
    """Raised when a source, record contract, or private output differs."""


@dataclass(frozen=True)
class ResourceSpec:
    resource: str
    current_path: Path
    pc_jp_source: Path
    current_profile: Mapping[str, Any]
    pc_jp_profile: Mapping[str, Any]


@dataclass(frozen=True)
class Change:
    resource: str
    coordinate: tuple[int, int]
    target_literals: tuple[str, ...]
    reason: str

    @property
    def coordinate_text(self) -> str:
        return f"{self.coordinate[0]}:{self.coordinate[1]}"

    @property
    def identity(self) -> tuple[str, tuple[int, int]]:
        return self.resource, self.coordinate


@dataclass(frozen=True)
class RecordPin:
    current_sha256: str
    current_size: int
    pc_jp_sha256: str
    target_sha256: str
    target_size: int
    target_line_widths_px: tuple[int, ...]


# Exact W45-installed Steam baseline.  A drifted game directory is rejected
# before any private candidate is composed.
RESOURCE_SPECS = {
    BASE_RESOURCE: ResourceSpec(
        resource=BASE_RESOURCE,
        current_path=STEAM_ROOT / BASE_RESOURCE,
        pc_jp_source=BASE_PC_JP_SOURCE,
        current_profile={
            "size": 1_504_410,
            "sha256": "F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB",
        },
        pc_jp_profile={
            "sha256": "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
        },
    ),
    PK_RESOURCE: ResourceSpec(
        resource=PK_RESOURCE,
        current_path=STEAM_ROOT / PK_RESOURCE,
        pc_jp_source=PK_PC_JP_SOURCE,
        current_profile={
            "size": 1_806_538,
            "sha256": "0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092",
        },
        pc_jp_profile={
            "sha256": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
        },
    ),
}

# Filled from ``derive-pins`` before ``build`` or ``verify-private`` are
# allowed.  Keeping output profiles in the source means a private candidate
# cannot silently absorb a compression, font, source, or target drift.
TARGET_PROFILES: Mapping[str, Mapping[str, Any]] = {
    BASE_RESOURCE: {
        "size": 1504498,
        "sha256": "BD356DA65E0FDDF3C32A1BAC42DAC5A25C2451331CAEEBE24009B7476BD379B1",
        "raw_size": 1498596,
        "raw_sha256": "DC4FA2698B74687AE92B98132FB7A4E3718FCF0F428C01867D7879BFA9B9105C",
    },
    PK_RESOURCE: {
        "size": 1806618,
        "sha256": "CC48466EE332A922069EAF2614236F2DFFA1C18D0253791AE416889C3A151BAD",
        "raw_size": 1799536,
        "raw_sha256": "D157BB8EFC2F150E98BB116A69119FEE14A1F1C0A0E7005383565476B2CAD8F6",
    },
}


# The 35 core PK block-9 corrections from the review.  Six language-style
# candidates (707, 797, 993, 1051, 1692, 1908) remain out of scope, as do
# 9:3867, 9:3926, all runtime records, and all 0143-command records.
PK_BLOCK9_CHANGES = (
    Change(PK_RESOURCE, (9, 385), ("목숨을 걸어야만\n살길이 열릴 때도 있다…가거라!",), "수사와 의미를 바로잡음"),
    Change(PK_RESOURCE, (9, 958), ("다케다의 군법을\n눈으로 보고, 귀로 들어라!",), "군법 구절의 의미를 바로잡음"),
    Change(PK_RESOURCE, (9, 1039), ("준비는 이미 끝났으니…\n마무리를 지켜보시오",), "관용구의 의미를 바로잡음"),
    Change(PK_RESOURCE, (9, 1187), ("조금… 궁지에 몰리고\n말았군요.",), "어미와 띄어쓰기를 바로잡음"),
    Change(PK_RESOURCE, (9, 1327), ("가자, 비탈 돌격이다!",), "전술명 逆落とし를 바로잡음"),
    Change(PK_RESOURCE, (9, 1328), ("나의 비탈 돌격을\n똑똑히 맛보아라!",), "전술명 逆落とし를 바로잡음"),
    Change(PK_RESOURCE, (9, 1424), ("분하나\n훌륭한 비탈 돌격이로다",), "전술명 逆落とし를 바로잡음"),
    Change(PK_RESOURCE, (9, 1460), ("사전 준비도\n빈틈없이 해 두었군…",), "근회(根回し) 문맥을 바로잡음"),
    Change(PK_RESOURCE, (9, 1814), ("주군을 치게 두지 마라!\n맞설 자 아무도 없느냐!",), "호령의 의미를 바로잡음"),
    Change(PK_RESOURCE, (9, 1994), ("가슴이 후련해진다는 게\n이런 것이로다!",), "관용구를 자연스럽게 바로잡음"),
    # The active font has no glyph for ``턱``; ``함부로`` keeps 闇雲に
    # (recklessly / blindly) while remaining renderable.
    Change(PK_RESOURCE, (9, 2135), ("함부로 덤비기만 한다고\n병법이 되는 건 아니지 않느냐",), "문장 성분을 바로잡음"),
    Change(PK_RESOURCE, (9, 2248), ("본성이 노려지고 있다!\n젠장, 돌아간다!",), "本丸을 본성으로 바로잡음"),
    Change(PK_RESOURCE, (9, 2386), ("본성이 목표라고?\n돌아가서 기다렸다가 친다!",), "本丸을 본성으로 바로잡음"),
    Change(PK_RESOURCE, (9, 2463), ("방향을 틀어라! 뒤로 돌아라!",), "転進의 의미를 바로잡음"),
    Change(PK_RESOURCE, (9, 2501), ("물러나시는 것이 좋겠습니다\n뒷일은 저희에게 맡겨 주십시오",), "후사를 맡는 문맥을 바로잡음"),
    Change(PK_RESOURCE, (9, 2572), ("자비는 필요 없습니다\n양쪽에서 짓뭉개겠습니다",), "情けは無用의 의미를 바로잡음"),
    Change(PK_RESOURCE, (9, 2597), ("자비는 필요 없습니다\n양쪽에서 짓뭉개겠습니다",), "情けは無用의 의미를 바로잡음"),
    Change(PK_RESOURCE, (9, 2862), ("나아갈 길은 이것뿐이다!\n설비를 빼앗아라!",), "設備를 설비로 바로잡음"),
    Change(PK_RESOURCE, (9, 2899), ("인력이 필요하군요\n설비로 향하겠습니다.",), "설비 대사의 의미와 어미를 바로잡음"),
    Change(PK_RESOURCE, (9, 2900), ("설비는 내줄 수 없습니다!\n우리가 방어에 나섭시다!",), "設備와 수비 주체를 바로잡음"),
    Change(PK_RESOURCE, (9, 2958), ("본성으로 향하라!\n적의 퇴로를 끊어라!",), "本丸을 본성으로 바로잡음"),
    Change(PK_RESOURCE, (9, 2959), ("본성으로 향합니다\n적을 동요시키는 것입니다",), "本丸을 본성으로 바로잡음"),
    Change(PK_RESOURCE, (9, 2964), ("본성으로 향합니다!\n적도 동요할 것입니다.",), "本丸을 본성으로 바로잡음"),
    Change(PK_RESOURCE, (9, 2995), ("본성을 파괴합니다!",), "本丸을 본성으로 바로잡음"),
    Change(PK_RESOURCE, (9, 2996), ("본성을 파괴하겠다!",), "本丸을 본성으로 바로잡음"),
    Change(PK_RESOURCE, (9, 3241), ("본성을 내줄 수는 없다!\n서둘러 후퇴하라!",), "本丸을 본성으로 바로잡음"),
    Change(PK_RESOURCE, (9, 3243), ("본성의 적을 쳐부순다!\n전력으로 돌아가라!",), "本丸을 본성으로 바로잡음"),
    Change(PK_RESOURCE, (9, 3247), ("본성에 적군이!?\n서둘러 돌아가야 해!",), "本丸을 본성으로 바로잡음"),
    Change(PK_RESOURCE, (9, 3281), ("그리 두지는 않겠다!\n측면을 내주지 마라!",), "어미를 바로잡음"),
    Change(PK_RESOURCE, (9, 3337), ("물러난다\n더 싸워 봐야 얻을 건 없다",), "恩의 오역을 바로잡음"),
    Change(PK_RESOURCE, (9, 3344), ("물러난다\n더 싸워 봐야 얻을 건 없다",), "恩의 오역을 바로잡음"),
    Change(PK_RESOURCE, (9, 3364), ("그리해서는 아니 되옵니다\n재고해 주시오",), "어미를 바로잡음"),
    Change(PK_RESOURCE, (9, 3920), ("내 무용은 진서 제일이다!\n다음 적은 어디냐!",), "鎮西와 적의 뜻을 바로잡음"),
    Change(PK_RESOURCE, (9, 4001), ("여기는 더는 버틸 수 없다…\n후방의 설비로 적을 막아라!",), "設備를 설비로 바로잡음"),
    Change(PK_RESOURCE, (9, 4113), ("복병이 있었다! 혼란한 틈에 쳐부수자!",), "문장 경계 띄어쓰기를 바로잡음"),
)

# Only Base rows whose current Korean, pristine PC-Japanese literal sequence,
# marker topology, and opaque bytes exactly match an included PK family are
# carried over.  Duplicate Base responses are intentionally retained because
# they are separate displayed records.  No guessed Base pairing is included.
BASE_MATCHING_BLOCK9_CHANGES = (
    Change(BASE_RESOURCE, (9, 341), ("목숨을 걸어야만\n살길이 열릴 때도 있다…가거라!",), "PK 9:385와 정확히 일치하는 Base 대응"),
    Change(BASE_RESOURCE, (9, 900), ("다케다의 군법을\n눈으로 보고, 귀로 들어라!",), "PK 9:958과 정확히 일치하는 Base 대응"),
    Change(BASE_RESOURCE, (9, 981), ("준비는 이미 끝났으니…\n마무리를 지켜보시오",), "PK 9:1039와 정확히 일치하는 Base 대응"),
    Change(BASE_RESOURCE, (9, 1114), ("조금… 궁지에 몰리고\n말았군요.",), "PK 9:1187과 정확히 일치하는 Base 대응"),
    Change(BASE_RESOURCE, (9, 1253), ("가자, 비탈 돌격이다!",), "PK 9:1327과 정확히 일치하는 Base 대응"),
    Change(BASE_RESOURCE, (9, 1254), ("나의 비탈 돌격을\n똑똑히 맛보아라!",), "PK 9:1328과 정확히 일치하는 Base 대응"),
    Change(BASE_RESOURCE, (9, 1350), ("분하나\n훌륭한 비탈 돌격이로다",), "PK 9:1424와 정확히 일치하는 Base 대응"),
    Change(BASE_RESOURCE, (9, 1386), ("사전 준비도\n빈틈없이 해 두었군…",), "PK 9:1460과 정확히 일치하는 Base 대응"),
    Change(BASE_RESOURCE, (9, 1740), ("주군을 치게 두지 마라!\n맞설 자 아무도 없느냐!",), "PK 9:1814와 정확히 일치하는 Base 대응"),
    Change(BASE_RESOURCE, (9, 1920), ("가슴이 후련해진다는 게\n이런 것이로다!",), "PK 9:1994와 정확히 일치하는 Base 대응"),
    Change(BASE_RESOURCE, (9, 2061), ("함부로 덤비기만 한다고\n병법이 되는 건 아니지 않느냐",), "PK 9:2135와 정확히 일치하는 Base 대응"),
    Change(BASE_RESOURCE, (9, 2376), ("방향을 틀어라! 뒤로 돌아라!",), "PK 9:2463과 정확히 일치하는 Base 대응"),
    Change(BASE_RESOURCE, (9, 2414), ("물러나시는 것이 좋겠습니다\n뒷일은 저희에게 맡겨 주십시오",), "PK 9:2501과 정확히 일치하는 Base 대응"),
    Change(BASE_RESOURCE, (9, 2485), ("자비는 필요 없습니다\n양쪽에서 짓뭉개겠습니다",), "PK 9:2572/2597과 정확히 일치하는 Base 대응"),
    Change(BASE_RESOURCE, (9, 2510), ("자비는 필요 없습니다\n양쪽에서 짓뭉개겠습니다",), "PK 9:2572/2597과 정확히 일치하는 Base 대응"),
    Change(BASE_RESOURCE, (9, 3055), ("그리 두지는 않겠다!\n측면을 내주지 마라!",), "PK 9:3281과 정확히 일치하는 Base 대응"),
    Change(BASE_RESOURCE, (9, 3111), ("물러난다\n더 싸워 봐야 얻을 건 없다",), "PK 9:3337/3344과 정확히 일치하는 Base 대응"),
    Change(BASE_RESOURCE, (9, 3118), ("물러난다\n더 싸워 봐야 얻을 건 없다",), "PK 9:3337/3344과 정확히 일치하는 Base 대응"),
    Change(BASE_RESOURCE, (9, 3138), ("그리해서는 아니 되옵니다\n재고해 주시오",), "PK 9:3364와 정확히 일치하는 Base 대응"),
)

BLOCK12_51_TARGET = (
    "참으로 경사스럽기 그지없습니다!\n우리 가문이",
    "고신",
    "에 있는 성을 모두\n장악했습니다",
    "！",
)
BLOCK12_51_CHANGES = (
    Change(BASE_RESOURCE, (12, 51), BLOCK12_51_TARGET, "当家와 성 장악 문맥을 바로잡음"),
    Change(PK_RESOURCE, (12, 51), BLOCK12_51_TARGET, "当家와 성 장악 문맥을 바로잡음"),
)

CHANGES = BASE_MATCHING_BLOCK9_CHANGES + PK_BLOCK9_CHANGES + BLOCK12_51_CHANGES

# Exact, byte-identical Base/PK families established from the W45 Korean
# input and the pristine PC-Japanese source.  The mapping is an executable
# guard: no Base record is included merely because its wording looks similar.
BASE_TO_PK_EQUIVALENTS: Mapping[tuple[int, int], tuple[tuple[int, int], ...]] = {
    (9, 341): ((9, 385),),
    (9, 900): ((9, 958),),
    (9, 981): ((9, 1039),),
    (9, 1114): ((9, 1187),),
    (9, 1253): ((9, 1327),),
    (9, 1254): ((9, 1328),),
    (9, 1350): ((9, 1424),),
    (9, 1386): ((9, 1460),),
    (9, 1740): ((9, 1814),),
    (9, 1920): ((9, 1994),),
    (9, 2061): ((9, 2135),),
    (9, 2376): ((9, 2463),),
    (9, 2414): ((9, 2501),),
    (9, 2485): ((9, 2572), (9, 2597)),
    (9, 2510): ((9, 2572), (9, 2597)),
    (9, 3055): ((9, 3281),),
    (9, 3111): ((9, 3337), (9, 3344)),
    (9, 3118): ((9, 3337), (9, 3344)),
    (9, 3138): ((9, 3364),),
}
EXCLUDED_STYLE_HOLDS = ((9, 707), (9, 797), (9, 993), (9, 1051), (9, 1692), (9, 1908))
EXCLUDED_STATIC_HOLDS = ((9, 3867), (9, 3926))

if len(PK_BLOCK9_CHANGES) != 35:
    raise RuntimeError("Wave 50 PK block-9 scope must contain 35 records")
if len(BASE_MATCHING_BLOCK9_CHANGES) != 19:
    raise RuntimeError("Wave 50 verified Base counterpart scope must contain 19 records")
if len(CHANGES) != 56 or len({change.identity for change in CHANGES}) != len(CHANGES):
    raise RuntimeError("Wave 50 scope is incomplete or has duplicate resource-qualified coordinates")
if set(BASE_TO_PK_EQUIVALENTS) != {change.coordinate for change in BASE_MATCHING_BLOCK9_CHANGES}:
    raise RuntimeError("Wave 50 Base/PK equivalence proof scope differs")


# Derived from the exact W45 baseline with ``derive-pins`` and then embedded.
# The record map is keyed by (resource, coordinate) to avoid accidental Base/
# PK coordinate conflation.
RECORD_PINS: Mapping[tuple[str, tuple[int, int]], RecordPin] = {
    (PK_RESOURCE, (12, 51)): RecordPin(
        "37E93D948FC81B4BBED85789232DF8DDCF24505D56103AFA74BE0B1776AA874E", 115,
        "510DA7ABCB335750852F29F6E058A021E7FA882CE3FBAE89E9F036D7544A7F7D",
        "C92E5A721067B432F126225C30C868A2E35590DF85BDC691B41474F34FC20ED9", 121, (744, 768, 336),
    ),
    (PK_RESOURCE, (9, 1039)): RecordPin(
        "AB329EA4F0F91C2AB9E2E8E4EDA66E0CD5EA25191B81F0C5CDA6F08DD015161B", 49,
        "339450BC5E5AB96636830EAA30A178E43B4DF06A6723879925204B9BBA069DA9",
        "185F424C7E3E037A25ABA7C092DDFE564D858A502B4D2125805A117F7B136601", 55, (528, 456),
    ),
    (PK_RESOURCE, (9, 1187)): RecordPin(
        "3FB222A568D85169F4CE86EFB1F05167E5A24E0438F799E95557CC199EC1E70C", 45,
        "F13EB1DBE0B16583FB74671BC0A58E0D606FFEED30205417F14AF0403C49DDF9",
        "538205A6CD0D7783A55A25238B3CB8CB55E1EDEC92D143D6DBC457D034E898A5", 43, (480, 216),
    ),
    (PK_RESOURCE, (9, 1327)): RecordPin(
        "5D5756C42567DB9ADA819739DF9891999DD49047BA5A2F3B2B5E95BFB68B6E61", 27,
        "2DDCCDB6D76AF3653A3F95C625167D59A201CFE363FF3DE6B24109DEB48168AB",
        "D6CE26FE8D772054456FDC993F62A778D0C480B313DF0399FB657C425C729153", 33, (480,),
    ),
    (PK_RESOURCE, (9, 1328)): RecordPin(
        "256A858652E2E3C1CF0467C8F9A8C35EBC3C6A77F600B1AFE87E886504871221", 45,
        "D93F09756A7F01986826827F8F9D402FC616302609236113C4F7B02CE76589FF",
        "5CCB993231E2ED57E1EA68DFA4EAC792C7AD91E30F5D37B96BA94327B021BFCB", 47, (384, 384),
    ),
    (PK_RESOURCE, (9, 1424)): RecordPin(
        "8F57680AF0F4D58502026C917E989E4D3862BB8CECE47DBACB6C35DC784E981C", 41,
        "9E0A0F817E6633EAC1995CC7CD8B8B98299678D1052B1A8517D4CCEFDA96FC3B",
        "97F6406267A85B0FE55C38E501A81AED7F035BDE0285432BF9BE90A13771F4C0", 41, (144, 528),
    ),
    (PK_RESOURCE, (9, 1460)): RecordPin(
        "4353868BF1DDA75FD8F78BA3416C029A9D9A85BD0826076AC58ECC3607094B39", 45,
        "7766D827FF91228F76290B45A3C32ED2AD726AB7620BA0E82593AADEB30432A5",
        "2E6D8346F1EFEC2A17B3E4459A3A66C0D62924034B2242A820B447C41902C473", 45, (264, 480),
    ),
    (PK_RESOURCE, (9, 1814)): RecordPin(
        "288613E9B339BE621883EA353DA5577A85D3D6716894D739D9CB98A2047448DE", 57,
        "0570B6F995B3745BAA48E77565F3327449BD83D5134E37301B73D9EDC20AED7E",
        "CEFDA4075AD598156ADB3B41601223FE1858C75522514CBB070E93ED7EF2ED7E", 63, (528, 528),
    ),
    (PK_RESOURCE, (9, 1994)): RecordPin(
        "663AF755316712047027833211568871CC84CCE75122095CC2C119EAE243E981", 51,
        "2D541048B135DF08F9A0430F902AD4D1875C0EA638E1BF5F44C3A46655FFD3BB",
        "77C71BA63B242A372F9B20B9D0A5A8F7D30A4E854C62D99448796BA9BC63DCFF", 51, (528, 336),
    ),
    (PK_RESOURCE, (9, 2135)): RecordPin(
        "DEAEF9E7D2303F403E8977D2E39466F08F37A530288B9944E71AABEB032E465B", 59,
        "A112B00FE6D5B152EA550E7B14237130CB4B33C9457D29299FDB9A42A10D0E4A",
        "DCADE9A0F1D1B99CCC8E3FBC9D3463F0706041CD88E4036E038E81E525536D57", 67, (528, 672),
    ),
    (PK_RESOURCE, (9, 2248)): RecordPin(
        "C9D915A3D596E9AB9BA205CCD73C932D1317548AD057D06E319EDFEF3A1E7485", 53,
        "A346239248AD26C5F80E1FFD0EA11DCD9AFAE792A79BF0684FF79626321B67EC",
        "8F2AB90A4880C7DA4637864D6C8EDF4DC83E9BC02DA0DEA4F6D1DAE76CA71671", 53, (504, 360),
    ),
    (PK_RESOURCE, (9, 2386)): RecordPin(
        "BB80987F4029D73549E23A11527AC474EB0E6BB00D2477AF6745A3A572A2A9B0", 57,
        "399D214BAAC6D246BAB41C87B06D397FEE48EA022A514D8EC40A309FE206797E",
        "F6B1DEED296A279E7CF9D7EB5D8707AB5D65E557B0E98D3CDB6D8313A484CE8F", 57, (384, 600),
    ),
    (PK_RESOURCE, (9, 2463)): RecordPin(
        "E2A3BE8162C3882EE383F8420FD7B1D02274C4C9F3268030F4F08AEA32D391F8", 27,
        "B46FD7D157E63E12B104AC14B6C024E9EED8C90D040082A975861D76EA4E9232",
        "A39A071A50EF9B2F1EF53EFBED2F5482BA39B1A659BBD12DC673C850EF309269", 41, (648,),
    ),
    (PK_RESOURCE, (9, 2501)): RecordPin(
        "483BBCF88007B53529EEF814E34DDD71941CCA36590365FFD73384B6A9AB3811", 61,
        "FCEFB12C8F049DCB3C6FA6526C4FC93E26639C59F43CDFD4088F0742516104C6",
        "33901FDBB84FD065733B9E432812F4D4C38F6835D839EC034B5FCD76687F529A", 71, (624, 696),
    ),
    (PK_RESOURCE, (9, 2572)): RecordPin(
        "620EF091DBEBE32A66CD169D4AE44A92DFA4A2EDCDE2ADD2BC70A493EFFDF65F", 45,
        "CAFE9D6BE5D6F79D29B9BB0E59EB11F24DA21B7197262589E1E717F2E3DE07B3",
        "618C78604CBFBA90EE4761834CAE3CD3A9885B84C5A1E49213C76B5E46719BCD", 57, (480, 552),
    ),
    (PK_RESOURCE, (9, 2597)): RecordPin(
        "620EF091DBEBE32A66CD169D4AE44A92DFA4A2EDCDE2ADD2BC70A493EFFDF65F", 45,
        "CAFE9D6BE5D6F79D29B9BB0E59EB11F24DA21B7197262589E1E717F2E3DE07B3",
        "618C78604CBFBA90EE4761834CAE3CD3A9885B84C5A1E49213C76B5E46719BCD", 57, (480, 552),
    ),
    (PK_RESOURCE, (9, 2862)): RecordPin(
        "2823193756EBC169C06AC3F631CCD20814C364497A3D17036C991174093A8AE6", 65,
        "B96BF32C5571CDD997993DFD71623E3FEABBB1975B1A3442EF0ED10C3EA9D9A0",
        "67F5862DD27A2AA730BDF0E0482A70C1383A59408537DAB982A073A67EE58840", 55, (552, 384),
    ),
    (PK_RESOURCE, (9, 2899)): RecordPin(
        "6C1F9AEB399623CF521250DAB213DC3726F076F0D6DD19CDD7986678BDA490F3", 57,
        "012FB52A8ACD97C07C2F156912B7880D0AD5D1925E9C9DCE232EC7FD5E380FDB",
        "5A118FB396C44331C4B7197A89DE83897D568287A98EF8A1A3F2AEBB6EA24FFF", 51, (408, 480),
    ),
    (PK_RESOURCE, (9, 2900)): RecordPin(
        "190B6B5DF177070F20C8D562F4F44555756E573C6AFD8F10BB5B9CE46A926DFA", 63,
        "6CC8105952F48DB8D3D389612731D866ECD4EED549C0E3FAA9BA15AD9A8A90BF",
        "8224AC43C04CCD6C86D42BC1F69DA42EC46F95A0B4898D7F844811F794B8018E", 65, (576, 552),
    ),
    (PK_RESOURCE, (9, 2958)): RecordPin(
        "F687DDE3E612A9974D2846D99CC3E65F317E81E095F521D7722C364FA6ED79FC", 51,
        "D66F0AF76C881BA6909DEC28BB66CAB472D9018123293D25E3FACC79DCC3269A",
        "CCEDE0B953161D19CC6E6DF9358171E4C8AC871BAAF7D1967691433797E49DFC", 51, (384, 456),
    ),
    (PK_RESOURCE, (9, 2959)): RecordPin(
        "CE81601D2F919F259188E707D22318882519DF19518FEAD3BA3C094FF98841E3", 55,
        "40DCCDA68307511C5FFD31CA3ED416AB2579954719A507579E7490B17A5D85F2",
        "98F5FCFE3B7C1F2E7F8F354648533602608BD70F5F527D7336CCABAF36BCC469", 55, (408, 576),
    ),
    (PK_RESOURCE, (9, 2964)): RecordPin(
        "DDAC73DEDD54361BEA7F85F3A1404A5B03877F142D05A379A2CA080409FA3807", 55,
        "E9212199AEB92634D2314659719FC81FD0D8BC783C111CD4C60C4C35F9772C41",
        "5039B212811A907745EE7E066D97E1B5C0B0A2C504E77FF263055339DA9779D4", 55, (432, 504),
    ),
    (PK_RESOURCE, (9, 2995)): RecordPin(
        "4EDDD22832C575E3FE6D4C3FADE1AB552CC1E748702D0F0C41591BA4CEE647E6", 29,
        "E8A520E9079DF6633F3A76953720E5769246C5E6471084C2042EA1787633ED24",
        "80D228591865AA122645B465CF391C865C5EA9232F8DAB9F8FE3B3CA11004B9E", 29, (432,),
    ),
    (PK_RESOURCE, (9, 2996)): RecordPin(
        "F60A7E80934241740FFBA5FBC8F553931AEA67D3D55289E77B4B82ACC8B47DF9", 29,
        "F6B3D0C34660C49E77AC082BB26DD3ECD146B21CEA22CC190870804ABB0328E0",
        "0AFD35E7E814C42F04EA23AAC6A1B943F097804551EE3B298158D9F6780F4635", 29, (432,),
    ),
    (PK_RESOURCE, (9, 3241)): RecordPin(
        "41D18FFF8A0526C39BD03135AEB7945A97150C7DACB4DE38CC5C46BF8A4B7BC8", 55,
        "22DFBA8890CF8473DB9C07ECCF14A2F32062E01C7C613EBB178737139F49CEAE",
        "DC5343FA556E60B427FF8E83B1B27A34B00C86CB8BAE2048E5EB7EC273003DE5", 55, (528, 384),
    ),
    (PK_RESOURCE, (9, 3243)): RecordPin(
        "597C2C24C808A46BE58B35B6237319A233684426B65D33D7B9943064C23401CA", 55,
        "2DE80283094B700D8FA3897C1074996BBBD1035D801AD222FAB82115532BE9CD",
        "712E7BF7CC90B8F2BCC6D8E1ECF6510D09918ED4CCC0A1DBC2170131BA1D256E", 55, (504, 432),
    ),
    (PK_RESOURCE, (9, 3247)): RecordPin(
        "2E4B59816C9DE6D7A7D7288B676419CAF2608C91D382C50D3612EB62F0E16EE2", 51,
        "C73D24BCADC58F8FE30CF8EF038BF1AC27B1480AE0DEB8DD0828FF5D932197F5",
        "CF6BAF9268BD9980315F2F8E0818182B6EB659E1273FCD37FE86E3CD28E8C0B8", 51, (360, 456),
    ),
    (PK_RESOURCE, (9, 3281)): RecordPin(
        "9D772FEA1967E2EE419A2F22A03B11779E143A84E3BDAEB5AB241D348EAF8C54", 53,
        "865A6E4C0A1B1EFE794A0B7F9EFA9979120437AA16283391421BB0CC248A0745",
        "5AD38AC8EDB1EB11FBCE7DB118EEE41067C8C229905C396996A7D36963B3B8D8", 55, (456, 456),
    ),
    (PK_RESOURCE, (9, 3337)): RecordPin(
        "1693E87CACA2DC3F27102CB661AC0008E0FBF3987E71599040E57FAF3C134C8B", 47,
        "2D4B08EF36CAEF5129BFA2FB06FA76B5C9E820CBC35F6D2BBCD39D337FF6B59E",
        "BF5EC3C21E5F2246B61C8D4EF757EBC4791D38857DC9A1C8311B6B3CBCFCA25F", 49, (192, 600),
    ),
    (PK_RESOURCE, (9, 3344)): RecordPin(
        "1693E87CACA2DC3F27102CB661AC0008E0FBF3987E71599040E57FAF3C134C8B", 47,
        "2D4B08EF36CAEF5129BFA2FB06FA76B5C9E820CBC35F6D2BBCD39D337FF6B59E",
        "BF5EC3C21E5F2246B61C8D4EF757EBC4791D38857DC9A1C8311B6B3CBCFCA25F", 49, (192, 600),
    ),
    (PK_RESOURCE, (9, 3364)): RecordPin(
        "C914BE2A2031FF55CA2D6BEB48097D8B5FD16F418A56268560279168AC6809EE", 47,
        "021E88217E87CE9538ADD550749D91455150C60D2F574202385B83D0C5C80A13",
        "47C4AFF4A19FF410D770261F3E896F8E01F5461F554C3383024BD9F43EBBFF07", 51, (576, 312),
    ),
    (PK_RESOURCE, (9, 385)): RecordPin(
        "B94E724634C5410AA6603FB89495038C5B93EE0EFFDD814375505B55B87322A1", 59,
        "4869415167BC0003FAF94ED3CF984198AB59E25A71136CC94F680C94041E909C",
        "7DF8631E0EA98E9F11773BB5CCE9546FCEE1B01365078C81BB6ECCC17733A913", 61, (360, 720),
    ),
    (PK_RESOURCE, (9, 3920)): RecordPin(
        "4F07B6FC58DEB18D21724B0CECB3BB26A1C17B564ED8DD51F2E64DF03B22D274", 59,
        "F6257ED18F84340E556EB84EEA4823784A71921DFB9662F7C592110467960082",
        "27FE3EA3514571A6D7969A5B0D42B95C1A7375B098165B1C97D116E7E1FF35DF", 59, (576, 408),
    ),
    (PK_RESOURCE, (9, 4001)): RecordPin(
        "84BD94CC2030DDB7351C8AF5042D849310625CF6CD8CDFD3CC69D44FF8F1D62D", 71,
        "3CE980D93D6FF7E77051A0C21B9FD4FA3141FAF99295FF3A7847B62AF49D707F",
        "B1C24A201DC65A067402FB765EFBE98621571EFE4AB197C42CA8671555688464", 71, (624, 624),
    ),
    (PK_RESOURCE, (9, 4113)): RecordPin(
        "36853392B2DFB50EE5E2FF21183090583361FA2835511057F92947E7974C37EC", 49,
        "C0BC47D7D7B66CFE42B932A8622766D3ED75EAAB555BD48BB646B67902DDA360",
        "A1C33D6CFD7C3CEE040C02C9A7B507922DD53A5DFB41BD9BB629E93087223871", 51, (864,),
    ),
    (PK_RESOURCE, (9, 958)): RecordPin(
        "67332C06277ADB19923E35E6D0ACAC3F7249C9207E5BE1CB5083564D75181208", 57,
        "C2ED28E46F9179AAA5F5F115C6B4335A52E7649BD6E5F4828319BB8A0276C9DC",
        "1CD27BF5621128AB6B72305D153F6DA31966234099914396D2AE4C9BD414FD04", 57, (360, 600),
    ),
    (BASE_RESOURCE, (12, 51)): RecordPin(
        "37E93D948FC81B4BBED85789232DF8DDCF24505D56103AFA74BE0B1776AA874E", 115,
        "206D2922783AD3C838B3EE17027EA17A01E8F400A31DD550D0E8789A23DC8B05",
        "C92E5A721067B432F126225C30C868A2E35590DF85BDC691B41474F34FC20ED9", 121, (744, 768, 336),
    ),
    (BASE_RESOURCE, (9, 1114)): RecordPin(
        "3FB222A568D85169F4CE86EFB1F05167E5A24E0438F799E95557CC199EC1E70C", 45,
        "F13EB1DBE0B16583FB74671BC0A58E0D606FFEED30205417F14AF0403C49DDF9",
        "538205A6CD0D7783A55A25238B3CB8CB55E1EDEC92D143D6DBC457D034E898A5", 43, (480, 216),
    ),
    (BASE_RESOURCE, (9, 1253)): RecordPin(
        "5D5756C42567DB9ADA819739DF9891999DD49047BA5A2F3B2B5E95BFB68B6E61", 27,
        "2DDCCDB6D76AF3653A3F95C625167D59A201CFE363FF3DE6B24109DEB48168AB",
        "D6CE26FE8D772054456FDC993F62A778D0C480B313DF0399FB657C425C729153", 33, (480,),
    ),
    (BASE_RESOURCE, (9, 1254)): RecordPin(
        "256A858652E2E3C1CF0467C8F9A8C35EBC3C6A77F600B1AFE87E886504871221", 45,
        "D93F09756A7F01986826827F8F9D402FC616302609236113C4F7B02CE76589FF",
        "5CCB993231E2ED57E1EA68DFA4EAC792C7AD91E30F5D37B96BA94327B021BFCB", 47, (384, 384),
    ),
    (BASE_RESOURCE, (9, 1350)): RecordPin(
        "8F57680AF0F4D58502026C917E989E4D3862BB8CECE47DBACB6C35DC784E981C", 41,
        "9E0A0F817E6633EAC1995CC7CD8B8B98299678D1052B1A8517D4CCEFDA96FC3B",
        "97F6406267A85B0FE55C38E501A81AED7F035BDE0285432BF9BE90A13771F4C0", 41, (144, 528),
    ),
    (BASE_RESOURCE, (9, 1386)): RecordPin(
        "4353868BF1DDA75FD8F78BA3416C029A9D9A85BD0826076AC58ECC3607094B39", 45,
        "7766D827FF91228F76290B45A3C32ED2AD726AB7620BA0E82593AADEB30432A5",
        "2E6D8346F1EFEC2A17B3E4459A3A66C0D62924034B2242A820B447C41902C473", 45, (264, 480),
    ),
    (BASE_RESOURCE, (9, 1740)): RecordPin(
        "288613E9B339BE621883EA353DA5577A85D3D6716894D739D9CB98A2047448DE", 57,
        "0570B6F995B3745BAA48E77565F3327449BD83D5134E37301B73D9EDC20AED7E",
        "CEFDA4075AD598156ADB3B41601223FE1858C75522514CBB070E93ED7EF2ED7E", 63, (528, 528),
    ),
    (BASE_RESOURCE, (9, 1920)): RecordPin(
        "663AF755316712047027833211568871CC84CCE75122095CC2C119EAE243E981", 51,
        "2D541048B135DF08F9A0430F902AD4D1875C0EA638E1BF5F44C3A46655FFD3BB",
        "77C71BA63B242A372F9B20B9D0A5A8F7D30A4E854C62D99448796BA9BC63DCFF", 51, (528, 336),
    ),
    (BASE_RESOURCE, (9, 2061)): RecordPin(
        "DEAEF9E7D2303F403E8977D2E39466F08F37A530288B9944E71AABEB032E465B", 59,
        "A112B00FE6D5B152EA550E7B14237130CB4B33C9457D29299FDB9A42A10D0E4A",
        "DCADE9A0F1D1B99CCC8E3FBC9D3463F0706041CD88E4036E038E81E525536D57", 67, (528, 672),
    ),
    (BASE_RESOURCE, (9, 2376)): RecordPin(
        "E2A3BE8162C3882EE383F8420FD7B1D02274C4C9F3268030F4F08AEA32D391F8", 27,
        "B46FD7D157E63E12B104AC14B6C024E9EED8C90D040082A975861D76EA4E9232",
        "A39A071A50EF9B2F1EF53EFBED2F5482BA39B1A659BBD12DC673C850EF309269", 41, (648,),
    ),
    (BASE_RESOURCE, (9, 2414)): RecordPin(
        "483BBCF88007B53529EEF814E34DDD71941CCA36590365FFD73384B6A9AB3811", 61,
        "FCEFB12C8F049DCB3C6FA6526C4FC93E26639C59F43CDFD4088F0742516104C6",
        "33901FDBB84FD065733B9E432812F4D4C38F6835D839EC034B5FCD76687F529A", 71, (624, 696),
    ),
    (BASE_RESOURCE, (9, 2485)): RecordPin(
        "620EF091DBEBE32A66CD169D4AE44A92DFA4A2EDCDE2ADD2BC70A493EFFDF65F", 45,
        "CAFE9D6BE5D6F79D29B9BB0E59EB11F24DA21B7197262589E1E717F2E3DE07B3",
        "618C78604CBFBA90EE4761834CAE3CD3A9885B84C5A1E49213C76B5E46719BCD", 57, (480, 552),
    ),
    (BASE_RESOURCE, (9, 2510)): RecordPin(
        "620EF091DBEBE32A66CD169D4AE44A92DFA4A2EDCDE2ADD2BC70A493EFFDF65F", 45,
        "CAFE9D6BE5D6F79D29B9BB0E59EB11F24DA21B7197262589E1E717F2E3DE07B3",
        "618C78604CBFBA90EE4761834CAE3CD3A9885B84C5A1E49213C76B5E46719BCD", 57, (480, 552),
    ),
    (BASE_RESOURCE, (9, 3055)): RecordPin(
        "9D772FEA1967E2EE419A2F22A03B11779E143A84E3BDAEB5AB241D348EAF8C54", 53,
        "865A6E4C0A1B1EFE794A0B7F9EFA9979120437AA16283391421BB0CC248A0745",
        "5AD38AC8EDB1EB11FBCE7DB118EEE41067C8C229905C396996A7D36963B3B8D8", 55, (456, 456),
    ),
    (BASE_RESOURCE, (9, 3111)): RecordPin(
        "1693E87CACA2DC3F27102CB661AC0008E0FBF3987E71599040E57FAF3C134C8B", 47,
        "2D4B08EF36CAEF5129BFA2FB06FA76B5C9E820CBC35F6D2BBCD39D337FF6B59E",
        "BF5EC3C21E5F2246B61C8D4EF757EBC4791D38857DC9A1C8311B6B3CBCFCA25F", 49, (192, 600),
    ),
    (BASE_RESOURCE, (9, 3118)): RecordPin(
        "1693E87CACA2DC3F27102CB661AC0008E0FBF3987E71599040E57FAF3C134C8B", 47,
        "2D4B08EF36CAEF5129BFA2FB06FA76B5C9E820CBC35F6D2BBCD39D337FF6B59E",
        "BF5EC3C21E5F2246B61C8D4EF757EBC4791D38857DC9A1C8311B6B3CBCFCA25F", 49, (192, 600),
    ),
    (BASE_RESOURCE, (9, 3138)): RecordPin(
        "C914BE2A2031FF55CA2D6BEB48097D8B5FD16F418A56268560279168AC6809EE", 47,
        "021E88217E87CE9538ADD550749D91455150C60D2F574202385B83D0C5C80A13",
        "47C4AFF4A19FF410D770261F3E896F8E01F5461F554C3383024BD9F43EBBFF07", 51, (576, 312),
    ),
    (BASE_RESOURCE, (9, 341)): RecordPin(
        "B94E724634C5410AA6603FB89495038C5B93EE0EFFDD814375505B55B87322A1", 59,
        "4869415167BC0003FAF94ED3CF984198AB59E25A71136CC94F680C94041E909C",
        "7DF8631E0EA98E9F11773BB5CCE9546FCEE1B01365078C81BB6ECCC17733A913", 61, (360, 720),
    ),
    (BASE_RESOURCE, (9, 900)): RecordPin(
        "67332C06277ADB19923E35E6D0ACAC3F7249C9207E5BE1CB5083564D75181208", 57,
        "C2ED28E46F9179AAA5F5F115C6B4335A52E7649BD6E5F4828319BB8A0276C9DC",
        "1CD27BF5621128AB6B72305D153F6DA31966234099914396D2AE4C9BD414FD04", 57, (360, 600),
    ),
    (BASE_RESOURCE, (9, 981)): RecordPin(
        "AB329EA4F0F91C2AB9E2E8E4EDA66E0CD5EA25191B81F0C5CDA6F08DD015161B", 49,
        "339450BC5E5AB96636830EAA30A178E43B4DF06A6723879925204B9BBA069DA9",
        "185F424C7E3E037A25ABA7C092DDFE564D858A502B4D2125805A117F7B136601", 55, (528, 456),
    ),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave50Error(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def reject_switch(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    if any("switch" in part.casefold() for part in resolved.parts):
        raise Wave50Error(f"Nintendo Switch path is forbidden: {label}")
    return resolved


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave50Error(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def load_w27() -> Any:
    require(W27_HELPER.is_file(), "Wave 27 format helper is absent")
    require(sha256_path(W27_HELPER) == W27_HELPER_SHA256, "Wave 27 format helper differs")
    spec = importlib.util.spec_from_file_location("wave50_pinned_wave27", W27_HELPER)
    if spec is None or spec.loader is None:
        raise Wave50Error("cannot load Wave 27 format helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W27 = load_w27()


def records_by_coordinate(packed: bytes) -> Mapping[tuple[int, int], Any]:
    return W27.records_by_coordinate(packed)


def opaque_hexes(record: Any) -> tuple[str, ...]:
    return tuple(span.hex().upper() for span in W27.opaque_spans(record))


def runtime_opcodes(record: Any) -> tuple[str, ...]:
    values: list[str] = []
    for span in W27.opaque_spans(record):
        for index, value in enumerate(span[:-1]):
            if value == 0x02:
                values.append(span[index : index + 2].hex().upper())
    return tuple(values)


def validate_target_literal(value: str, label: str) -> None:
    require(value != "", f"empty target literal: {label}")
    encoded = value.encode("utf-16le")
    require(W27.LITERAL_START not in encoded and W27.LITERAL_END not in encoded, f"reserved marker in target: {label}")
    require(all(ord(char) >= 0x20 or char in "\n\r" for char in value), f"control character in target: {label}")


def load_inputs() -> tuple[
    Mapping[str, bytes],
    Mapping[str, Mapping[tuple[int, int], Any]],
    Mapping[str, Mapping[tuple[int, int], Any]],
]:
    packed_by_resource: dict[str, bytes] = {}
    current_by_resource: dict[str, Mapping[tuple[int, int], Any]] = {}
    pc_jp_by_resource: dict[str, Mapping[tuple[int, int], Any]] = {}
    for resource in RESOURCE_ORDER:
        spec = RESOURCE_SPECS[resource]
        current_path = reject_switch(spec.current_path, f"current Steam PC {resource}")
        source_path = reject_switch(spec.pc_jp_source, f"pristine PC Japanese {resource}")
        packed = current_path.read_bytes()
        require(
            len(packed) == spec.current_profile["size"]
            and sha256_bytes(packed) == spec.current_profile["sha256"],
            f"current W45 input profile differs: {resource}",
        )
        W27.validate_raw_roundtrip(packed, f"Wave 50 current Steam {resource}")
        source_packed = source_path.read_bytes()
        require(
            sha256_bytes(source_packed) == spec.pc_jp_profile["sha256"],
            f"pristine PC Japanese source profile differs: {resource}",
        )
        W27.validate_raw_roundtrip(source_packed, f"Wave 50 PC Japanese {resource}")
        packed_by_resource[resource] = packed
        current_by_resource[resource] = records_by_coordinate(packed)
        pc_jp_by_resource[resource] = records_by_coordinate(source_packed)
    validate_exact_base_counterparts(current_by_resource, pc_jp_by_resource)
    return packed_by_resource, current_by_resource, pc_jp_by_resource


def validate_exact_base_counterparts(
    current_by_resource: Mapping[str, Mapping[tuple[int, int], Any]],
    pc_jp_by_resource: Mapping[str, Mapping[tuple[int, int], Any]],
) -> None:
    targets = {change.identity: change.target_literals for change in CHANGES}
    for base_coordinate, pk_coordinates in BASE_TO_PK_EQUIVALENTS.items():
        base_current = current_by_resource[BASE_RESOURCE][base_coordinate]
        base_source = pc_jp_by_resource[BASE_RESOURCE][base_coordinate]
        for pk_coordinate in pk_coordinates:
            pk_current = current_by_resource[PK_RESOURCE][pk_coordinate]
            pk_source = pc_jp_by_resource[PK_RESOURCE][pk_coordinate]
            label = f"Base {base_coordinate} / PK {pk_coordinate}"
            require(base_current.data == pk_current.data, f"current Base/PK family differs: {label}")
            require(base_source.data == pk_source.data, f"PC Japanese Base/PK family differs: {label}")
            require(targets[(BASE_RESOURCE, base_coordinate)] == targets[(PK_RESOURCE, pk_coordinate)], f"Base/PK target differs: {label}")

    # Block 12:51 carries styled ``고신`` literals.  The two PC-Japanese raw
    # records are not byte-identical, so assert the text and bytecode topology
    # that matters for a safe replacement instead of asserting raw equality.
    base_coordinate = (12, 51)
    base_current = current_by_resource[BASE_RESOURCE][base_coordinate]
    pk_current = current_by_resource[PK_RESOURCE][base_coordinate]
    base_source = pc_jp_by_resource[BASE_RESOURCE][base_coordinate]
    pk_source = pc_jp_by_resource[PK_RESOURCE][base_coordinate]
    require(W27.literal_texts(base_current) == W27.literal_texts(pk_current), "current block 12:51 Base/PK literals differ")
    require(W27.literal_texts(base_source) == W27.literal_texts(pk_source), "PC Japanese block 12:51 Base/PK literals differ")
    require(W27.marker_topology(base_current) == W27.marker_topology(pk_current), "current block 12:51 Base/PK marker topology differs")
    require(W27.marker_topology(base_source) == W27.marker_topology(pk_source), "PC Japanese block 12:51 Base/PK marker topology differs")
    require(W27.opaque_spans(base_current) == W27.opaque_spans(pk_current), "current block 12:51 Base/PK opaque bytes differ")
    require(targets[(BASE_RESOURCE, base_coordinate)] == targets[(PK_RESOURCE, base_coordinate)], "block 12:51 Base/PK target differs")


def validate_change(
    change: Change,
    before: Any,
    pc_jp: Any,
    advance: Any,
    *,
    enforce_pins: bool,
) -> tuple[bytes, dict[str, Any]]:
    label = f"{change.resource}:{change.coordinate_text}"
    require(change.coordinate == (before.block_id, before.record_id), f"current coordinate differs: {label}")
    require(change.coordinate == (pc_jp.block_id, pc_jp.record_id), f"PC Japanese coordinate differs: {label}")
    current_literals = W27.literal_texts(before)
    source_literals = W27.literal_texts(pc_jp)
    require(len(current_literals) == len(change.target_literals), f"literal slot count differs: {label}")
    require(len(source_literals) == len(current_literals), f"PC Japanese literal slot count differs: {label}")
    require(W27.marker_topology(pc_jp) == W27.marker_topology(before), f"PC Japanese marker topology differs: {label}")
    require(before.data.endswith(W27.RECORD_TERMINATOR), f"current terminator differs: {label}")
    require(pc_jp.data.endswith(W27.RECORD_TERMINATOR), f"PC Japanese terminator differs: {label}")
    require(not runtime_opcodes(before), f"runtime 02xx token forbidden: {label}")
    require(not W27.complete_0143_commands(W27.opaque_spans(before)), f"0143 command forbidden: {label}")
    require("".join(current_literals).count("\n") == "".join(change.target_literals).count("\n"), f"manual LF count differs: {label}")
    for target in change.target_literals:
        validate_target_literal(target, label)

    layout = W27.line_layout(change.target_literals, advance)
    require(layout["line_count"] <= MAX_LINES, f"more than {MAX_LINES} lines: {label}")
    require(layout["max_width_px"] <= MAX_LINE_PX, f"line width exceeds {MAX_LINE_PX}px: {label}")
    require(not layout["wide_fallback_codepoints"], f"fallback glyph in target: {label}")

    rebuilt = W27.rebuild_static_record(before, change.target_literals)
    after = W27.MsgGameRecord(before.block_id, before.record_id, before.relative_offset, rebuilt)
    require(W27.literal_texts(after) == change.target_literals, f"target literal differs: {label}")
    require(W27.marker_topology(after) == W27.marker_topology(before), f"marker topology differs: {label}")
    require(W27.opaque_spans(after) == W27.opaque_spans(before), f"opaque bytes differ: {label}")
    require(after.data.endswith(W27.RECORD_TERMINATOR), f"target terminator differs: {label}")

    if enforce_pins:
        pin = RECORD_PINS.get(change.identity)
        require(pin is not None, f"record pin is absent: {label}")
        require(sha256_bytes(before.data) == pin.current_sha256 and len(before.data) == pin.current_size, f"current record pin differs: {label}")
        require(sha256_bytes(pc_jp.data) == pin.pc_jp_sha256, f"PC Japanese record pin differs: {label}")
        require(sha256_bytes(after.data) == pin.target_sha256 and len(after.data) == pin.target_size, f"target record pin differs: {label}")
        require(tuple(layout["line_widths_px"]) == pin.target_line_widths_px, f"line-width pin differs: {label}")

    return rebuilt, {
        "resource": change.resource,
        "coordinate": change.coordinate_text,
        "reason": change.reason,
        "current_record_sha256": sha256_bytes(before.data),
        "current_record_size": len(before.data),
        "pc_jp_record_sha256": sha256_bytes(pc_jp.data),
        "target_record_sha256": sha256_bytes(after.data),
        "target_record_size": len(after.data),
        "literal_slot_count": len(change.target_literals),
        "input_manual_lf_count": "".join(current_literals).count("\n"),
        "target_manual_lf_count": "".join(change.target_literals).count("\n"),
        "input_opaque_spans_hex": list(opaque_hexes(before)),
        "target_opaque_spans_hex": list(opaque_hexes(after)),
        "runtime_02xx_opcodes": list(runtime_opcodes(before)),
        "target_line_widths_px": list(layout["line_widths_px"]),
        "target_max_line_px": layout["max_width_px"],
        "target_literals": list(change.target_literals),
    }


def build_unpinned() -> tuple[
    Mapping[str, bytes],
    Mapping[str, bytes],
    list[dict[str, Any]],
    Mapping[str, Mapping[tuple[int, int], Any]],
    Mapping[str, Mapping[tuple[int, int], Any]],
]:
    inputs, current_by_resource, pc_jp_by_resource = load_inputs()
    advance, _font = W27.load_font_advance()
    packed_by_resource: dict[str, bytes] = {}
    raw_by_resource: dict[str, bytes] = {}
    rows: list[dict[str, Any]] = []
    for resource in RESOURCE_ORDER:
        current = current_by_resource[resource]
        pc_jp = pc_jp_by_resource[resource]
        replacements: dict[tuple[int, int], bytes] = {}
        scoped = tuple(change for change in CHANGES if change.resource == resource)
        for change in scoped:
            before = current.get(change.coordinate)
            source = pc_jp.get(change.coordinate)
            require(before is not None and source is not None, f"record absent: {resource}:{change.coordinate_text}")
            require(change.coordinate not in replacements, f"duplicate coordinate: {resource}:{change.coordinate_text}")
            replacement, row = validate_change(change, before, source, advance, enforce_pins=False)
            replacements[change.coordinate] = replacement
            rows.append(row)
        candidate = W27.rebuild_packed_msggame(inputs[resource], replacements)
        W27.validate_raw_roundtrip(candidate, f"Wave 50 private candidate {resource}")
        _header, raw = W27.decompress_wrapper(candidate)
        after = records_by_coordinate(candidate)
        changed = {coordinate for coordinate, record in current.items() if record.data != after[coordinate].data}
        expected = {change.coordinate for change in scoped}
        require(changed == expected and set(current) == set(after), f"changed record scope differs: {resource}")
        packed_by_resource[resource] = candidate
        raw_by_resource[resource] = raw
    return packed_by_resource, raw_by_resource, rows, current_by_resource, pc_jp_by_resource


def derive_pins() -> dict[str, Any]:
    packed_by_resource, raw_by_resource, rows, _current, _pc_jp = build_unpinned()
    return {
        "target_profiles": {
            resource: {
                "size": len(packed_by_resource[resource]),
                "sha256": sha256_bytes(packed_by_resource[resource]),
                "raw_size": len(raw_by_resource[resource]),
                "raw_sha256": sha256_bytes(raw_by_resource[resource]),
            }
            for resource in RESOURCE_ORDER
        },
        "record_pins": {
            f"{row['resource']}:{row['coordinate']}": {
                "current_sha256": row["current_record_sha256"],
                "current_size": row["current_record_size"],
                "pc_jp_sha256": row["pc_jp_record_sha256"],
                "target_sha256": row["target_record_sha256"],
                "target_size": row["target_record_size"],
                "target_line_widths_px": row["target_line_widths_px"],
            }
            for row in rows
        },
    }


def require_pins() -> None:
    require(set(TARGET_PROFILES) == set(RESOURCE_ORDER), "target output profiles are incomplete")
    for resource in RESOURCE_ORDER:
        require({"size", "sha256", "raw_size", "raw_sha256"} <= set(TARGET_PROFILES[resource]), f"target profile pin is absent: {resource}")
    require(len(RECORD_PINS) == len(CHANGES), "record pins are incomplete")
    require(set(RECORD_PINS) == {change.identity for change in CHANGES}, "record pin identities differ")


def prepare_candidate() -> tuple[Mapping[str, bytes], Mapping[str, bytes], dict[str, Any], dict[str, Any]]:
    require_pins()
    packed_by_resource, raw_by_resource, _rows_unpinned, current_by_resource, pc_jp_by_resource = build_unpinned()
    for resource in RESOURCE_ORDER:
        profile = TARGET_PROFILES[resource]
        require(len(packed_by_resource[resource]) == profile["size"] and sha256_bytes(packed_by_resource[resource]) == profile["sha256"], f"target packed profile differs: {resource}")
        require(len(raw_by_resource[resource]) == profile["raw_size"] and sha256_bytes(raw_by_resource[resource]) == profile["raw_sha256"], f"target raw profile differs: {resource}")

    advance, font = W27.load_font_advance()
    rows: list[dict[str, Any]] = []
    for change in CHANGES:
        before = current_by_resource[change.resource][change.coordinate]
        source = pc_jp_by_resource[change.resource][change.coordinate]
        replacement, row = validate_change(change, before, source, advance, enforce_pins=True)
        after = records_by_coordinate(packed_by_resource[change.resource])[change.coordinate]
        require(after.data == replacement, f"rebuilt record differs: {change.resource}:{change.coordinate_text}")
        rows.append(row)

    by_resource = {
        resource: sum(change.resource == resource for change in CHANGES)
        for resource in RESOURCE_ORDER
    }
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "platform": "Steam PC",
            "pc_jp_primary": True,
            "pc_en_sc_tc_context_reviewed_before_builder": True,
            "pc_en_sc_tc_builder_input": False,
            "switch_korean_read": False,
            "runtime_02xx_records": "forbidden",
            "0143_command_records": "forbidden",
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "pinned_format_helper_sha256": W27_HELPER_SHA256,
        "inputs": {resource: RESOURCE_SPECS[resource].current_profile for resource in RESOURCE_ORDER},
        "pc_jp_sources": {resource: RESOURCE_SPECS[resource].pc_jp_profile for resource in RESOURCE_ORDER},
        "targets": TARGET_PROFILES,
        "font": font,
        "max_lines": MAX_LINES,
        "max_line_px": MAX_LINE_PX,
        "changed_record_count": len(CHANGES),
        "changed_record_count_by_resource": by_resource,
        "records": rows,
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": list(RESOURCE_ORDER),
        "inputs": {resource: RESOURCE_SPECS[resource].current_profile for resource in RESOURCE_ORDER},
        "outputs": TARGET_PROFILES,
        "changed_coordinates": {
            resource: [change.coordinate_text for change in CHANGES if change.resource == resource]
            for resource in RESOURCE_ORDER
        },
        "changed_record_count": len(CHANGES),
        "changed_record_count_by_resource": by_resource,
        "switch_korean_input": "forbidden",
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
        "audit_sha256": sha256_bytes(canonical_json(audit)),
    }
    return packed_by_resource, raw_by_resource, audit, manifest


def write_candidate(bundle: tuple[Mapping[str, bytes], Mapping[str, bytes], dict[str, Any], dict[str, Any]]) -> Path:
    packed_by_resource, _raw_by_resource, audit, manifest = bundle
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT))
    try:
        for resource in RESOURCE_ORDER:
            resource_path = stage / resource
            resource_path.parent.mkdir(parents=True, exist_ok=True)
            resource_path.write_bytes(packed_by_resource[resource])
        (stage / "audit.v1.json").write_bytes(canonical_json(audit))
        (stage / "candidate_manifest.v1.json").write_bytes(canonical_json(manifest))
        if output.exists():
            shutil.rmtree(output)
        os.replace(stage, output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return output


def verify_private() -> dict[str, Any]:
    packed_by_resource, _raw_by_resource, audit, manifest = prepare_candidate()
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    for resource in RESOURCE_ORDER:
        require((output / resource).read_bytes() == packed_by_resource[resource], f"private candidate resource differs: {resource}")
    require((output / "audit.v1.json").read_bytes() == canonical_json(audit), "private audit differs")
    require((output / "candidate_manifest.v1.json").read_bytes() == canonical_json(manifest), "private manifest differs")
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "changed_record_count": len(CHANGES),
        "changed_record_count_by_resource": {
            resource: sum(change.resource == resource for change in CHANGES)
            for resource in RESOURCE_ORDER
        },
        "steam_game_resource_written": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("derive-pins", "build", "verify-private"))
    args = parser.parse_args(argv)
    if args.command == "derive-pins":
        result = derive_pins()
    elif args.command == "build":
        output = write_candidate(prepare_candidate())
        result = {
            "candidate_root": output.relative_to(REPO).as_posix(),
            "changed_record_count": len(CHANGES),
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
