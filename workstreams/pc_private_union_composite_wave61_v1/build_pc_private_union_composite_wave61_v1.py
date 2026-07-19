#!/usr/bin/env python3
"""Build a private W61 union from W60 and direct-PC B06/B09 corrections.

Only literal payloads individually pinned to current Steam PC Korean and to
pristine PC Japanese are overlaid.  W60's opaque control bytes, runtime
tokens, event reflows, and previous literal corrections remain intact.
This module can write only its own private ``tmp`` candidate; it cannot apply
files to Steam, operate Git, access a network, or publish a release.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_ROOT = TMP_ROOT / "candidate"
W60_BUILDER = (
    REPO
    / "workstreams"
    / "pc_private_union_composite_wave60_v1"
    / "build_pc_private_union_composite_wave60_v1.py"
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


w60 = load_module("pc_private_union_wave60_for_wave61", W60_BUILDER)
w59 = w60.w59
core = w60.core
BASE = w60.BASE
PK = w60.PK
MSGDATA = w60.MSGDATA
MSGEV = w60.MSGEV
MSGGAME_RESOURCES = (BASE, PK)
ALL_RESOURCES = (BASE, PK, MSGDATA, MSGEV)

MSGA_ROOT = REPO / "workstreams" / "msggame"
TOOLS_ROOT = REPO / "tools"
for root in (MSGA_ROOT, TOOLS_ROOT):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

from msggame_format import (  # noqa: E402
    MsgGameArchive,
    parse_raw_msggame,
    parse_record_literals,
    rebuild_raw_msggame,
)
from nobu16_lz4 import decompress_wrapper  # noqa: E402


class UnionError(RuntimeError):
    """Raised when an input, target, or output contract drifts."""


@dataclass(frozen=True)
class SourceProfile:
    packed_size: int
    packed_sha256: str
    raw_size: int
    raw_sha256: str


@dataclass(frozen=True)
class Target:
    audit: str
    resource: str
    block_id: int
    record_id: int
    literal_id: int
    current_ko: str
    target_ko: str
    pc_jp: str
    rationale: str

    @property
    def coordinate(self) -> tuple[int, int, int]:
        return (self.block_id, self.record_id, self.literal_id)

    @property
    def coordinate_text(self) -> str:
        return f"{self.block_id}:{self.record_id}:{self.literal_id}"


@dataclass(frozen=True)
class DirectSource:
    path: Path
    profile: SourceProfile


@dataclass(frozen=True)
class Bundle:
    outputs: Mapping[str, bytes]
    profiles: Mapping[str, Any]
    effective: Mapping[str, Mapping[tuple[int, int, int], str]]
    classifications: Mapping[str, Mapping[str, Mapping[str, tuple[tuple[int, int, int], ...]]]]
    final_record_counts: Mapping[str, int]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


BASE_JP = DirectSource(
    Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin"),
    SourceProfile(
        610_163,
        "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
        1_337_548,
        "353010B59A3E04BFE5541162229C1CFCAD181EF0E75FCC9B6DE2043BFC515F38",
    ),
)
PK_JP = DirectSource(
    Path(
        r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP\file_only_transaction"
        r"\steam-jp-1.1.7-v0.6.0\originals\MSG_PK\JP\msggame.bin"
    ),
    SourceProfile(
        721_304,
        "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
        1_599_324,
        "F052DA62C584C024C1EAF67A706253525421E6068976657DF6A6C07EFCA5D4E8",
    ),
)
JP_SOURCES = {BASE: BASE_JP, PK: PK_JP}


def t(
    audit: str,
    resource: str,
    record_id: int,
    literal_id: int,
    current_ko: str,
    target_ko: str,
    pc_jp: str,
    rationale: str,
) -> Target:
    block_id = 6 if audit == "b06" else 9
    return Target(audit, resource, block_id, record_id, literal_id, current_ko, target_ko, pc_jp, rationale)


def paired(
    audit: str,
    base_record: int,
    pk_record: int,
    current_ko: str,
    target_ko: str,
    pc_jp: str,
    rationale: str,
) -> tuple[Target, Target]:
    return (
        t(audit, BASE, base_record, 0, current_ko, target_ko, pc_jp, rationale),
        t(audit, PK, pk_record, 0, current_ko, target_ko, pc_jp, rationale),
    )


def repeated(
    audit: str,
    resource: str,
    record_ids: tuple[int, ...],
    current_ko: str,
    target_ko: str,
    pc_jp: str,
    rationale: str,
) -> tuple[Target, ...]:
    return tuple(t(audit, resource, record_id, 0, current_ko, target_ko, pc_jp, rationale) for record_id in record_ids)


# These lists are deliberately explicit and were independently rechecked
# against only current Steam PC Korean and pristine PC Japanese.  No broad
# term replacement is allowed.
B06_TARGETS: tuple[Target, ...] = (
    t(
        "b06", PK, 751, 0,
        "주군이 지나치게 강경하면\n가신들의 사기가 꺾이지……",
        "주군이 너무 강해서는\n가신이 의기소침해지는 법…",
        "主君が強すぎては\n家臣が意気消沈する…",
        "restore strong rather than politically hard-line",
    ),
    t("b06", BASE, 851, 0, "상처가 아프는걸…", "상처가 아프군…", "傷が痛むわ…", "repair Korean predicate"),
    t("b06", PK, 853, 0, "상처가 아프는걸…", "상처가 아프군…", "傷が痛むわ…", "repair Korean predicate"),
    t("b06", BASE, 1027, 0, "뜬소문인가?", "혼담인가?", "浮いた話か？", "restore marriage-rumor sense"),
    t("b06", PK, 1029, 0, "뜬소문인가?", "혼담인가?", "浮いた話か？", "restore marriage-rumor sense"),
    t(
        "b06", PK, 1147, 0,
        "늘 감사합니다, 덕분에\n매입 가격이 낮아졌습니다.",
        "늘 감사합니다, 덕분에\n구입 가격이 낮아졌습니다.",
        "毎度ありがとうございます、おかげさまで\n購入価格が安くなっておりますぞ",
        "repair purchase-versus-buyback direction",
    ),
    *(
        t(
            "b06", PK, record_id, 0, "과분한 대임, 받자", "분에 넘치는 대임, 받들겠습니다.",
            "身に余る大任、拝命", "restore humble first-person acceptance",
        )
        for record_id in range(1442, 1454)
    ),
    t(
        "b06", PK, 3144, 0,
        "전투는 잠시 끝났습니다\n잘 받아들여 주셨습니다",
        "전투는 일단 끝났습니다\n부디 승복해 주십시오",
        "これにて戦は一旦終わり\nよくよくご承服あれ",
        "restore request form rather than completed acceptance",
    ),
    t(
        "b06", PK, 3455, 0,
        "공훈 1위는 기쁘지만,\n이 자리는 아직 제게 과분합니다.\n더욱 노력하겠습니다.",
        "공훈 1위는 기쁘지만,\n이 자리는 아직 제게는 모자랍니다.\n더욱 노력하겠습니다.",
        "勲功一位なのは嬉しいが\n地位はまだまだ役不足よ\n励まねばな",
        "restore 役不足 direction",
    ),
    t(
        "b06", BASE, 3228, 0,
        "혼인 제의, 받아들이지\n이제 우리는 인척이 되는 것\n오래도록 좋은 교분을 이어 가세",
        "혼인 제의, 받아들이지\n이제 우리는 인척이 되겠군\n오래도록 좋은 교분을 이어 가세",
        "婚姻の申し出、受け入れよう\nこれより我らは姻族となる\n末永く良きつきあいを続けようぞ",
        "complete the Korean marriage-kinship sentence",
    ),
    t(
        "b06", PK, 3235, 0,
        "혼인 제의, 받아들이지\n이제 우리는 인척이 되는 것\n오래도록 좋은 교분을 이어 가세",
        "혼인 제의, 받아들이지\n이제 우리는 인척이 되겠군\n오래도록 좋은 교분을 이어 가세",
        "婚姻の申し出、受け入れよう\nこれより我らは姻族となる\n末永く良きつきあいを続けようぞ",
        "complete the Korean marriage-kinship sentence",
    ),
    t(
        "b06", BASE, 3809, 0,
        "혼인 제의, 받아들이지\n이제 우리는 인척이 되는 것\n오래도록 좋은 사이를 이어 가세",
        "혼인 제의, 받아들이지\n이제 우리는 인척이 되겠군\n오래도록 좋은 사이를 이어 가세",
        "婚姻の申し出、受け入れよう\nこれより我らは姻族となる\n末永く良き付き合いを続けようぞ",
        "complete the Korean marriage-kinship sentence",
    ),
    t(
        "b06", PK, 3816, 0,
        "혼인 제의, 받아들이지\n이제 우리는 인척이 되는 것\n오래도록 좋은 사이를 이어 가세",
        "혼인 제의, 받아들이지\n이제 우리는 인척이 되겠군\n오래도록 좋은 사이를 이어 가세",
        "婚姻の申し出、受け入れよう\nこれより我らは姻族となる\n末永く良き付き合いを続けようぞ",
        "complete the Korean marriage-kinship sentence",
    ),
    t(
        "b06", BASE, 4449, 0,
        "뛰어남은 섬긴 세월만이 아니니\n그것을 증명해 보여라",
        "뛰어남은 섬긴 세월만이 아니니\n그것을 증명해 보이겠다",
        "優れたるは仕えし年季のみならず\nそれを証明してみせ",
        "restore speaker's first-person resolve",
    ),
    t(
        "b06", PK, 4508, 0,
        "뛰어남은 섬긴 세월만이 아니니\n그것을 증명해 보여라",
        "뛰어남은 섬긴 세월만이 아니니\n그것을 증명해 보이겠다",
        "優れたるは仕えし年季のみならず\nそれを証明してみせ",
        "restore speaker's first-person resolve",
    ),
    t(
        "b06", PK, 4795, 0,
        "\n내 승마을 살릴 명마가 있다면\n전장에서도 더욱",
        "\n내 승마를 살릴 명마가 있다면\n전장에서도 더욱",
        "\n我が馬術を活かせる名馬がいれば\n戦でもより",
        "repair the Korean object particle",
    ),
)
B09_TARGETS: tuple[Target, ...] = (
    *paired(
        "b09", 345, 389, "앞을 가로막는 자에게\n용서는 필요 없다…베어라!",
        "앞을 가로막는 자에게\n자비는 필요 없다… 베어라!", "立ち塞がる者に\n容赦は無用…斬れ！",
        "translate combat 容赦 as mercy rather than forgiveness",
    ),
    *paired("b09", 845, 903, "선명한 무공!", "눈부신 무공!", "鮮やかなる武功！", "restore vivid achievement sense"),
    *paired(
        "b09", 945, 1003, "자, 헛소문에 놀아나라…!", "자, 거짓 정보에 휘둘려라…!",
        "さあ、虚報に踊れ…！", "repair malformed Korean and 虚報 sense",
    ),
    *paired(
        "b09", 935, 993, "아뿔싸!\n혼란시키지 못했다", "아뿔싸!\n혼란에 빠뜨리지 못했다",
        "いかん！\n混乱させられなんだ", "restore the transitive battle effect",
    ),
    *paired(
        "b09", 981, 1039, "세공은 이래저래…\n마무리를 지켜보시오", "준비는 이미 끝났으니…\n마무리를 지켜보시오",
        "細工は流流…\n仕上げをご覧じろ", "retain the direct-PC-compatible W60 idiom repair",
    ),
    *paired(
        "b09", 1386, 1460, "사전 정지 작업도\n빈틈없이, 라…", "사전 준비도\n빈틈없이 해 두었군…",
        "根回しも\n抜かりなく、か…", "retain the direct-PC-compatible W60 groundwork repair",
    ),
    *paired(
        "b09", 1154, 1228, "이제\n시간문제로군요…", "이제\n시간 문제로군요…",
        "もはや\n時間の問題ですね…", "repair Korean spacing",
    ),
    *paired(
        "b09", 338, 382, "당가의 흥망은\n이 일전에 있다!", "우리 가문의 흥망은\n이 일전에 있다!",
        "当家の興廃\nこの一戦にあり！", "render 当家 as the speaker's house",
    ),
    *paired(
        "b09", 745, 799, "으음, 이 사태…\n당가의 이름에도 흠이 가겠구나",
        "으음, 이 사태…\n우리 가문의 명예에도 흠이 가겠구나", "むう、この事態…\n当家の名にも傷がつく",
        "render 当家 as the speaker's house",
    ),
    *paired(
        "b09", 746, 800, "이는… 당가의 치명상이\n될 수도 있겠습니다", "이는… 우리 가문에 치명상이\n될 수도 있겠습니다",
        "これは…当家の致命傷\nともなりかねませんね", "render 当家 as the speaker's house",
    ),
    *paired(
        "b09", 1245, 1319, "분발하라!\n당가의 승리를 위하여!", "분발하라!\n우리 가문의 승리를 위하여!",
        "発憤せよ！\n当家の勝利がために！", "render 当家 as the speaker's house",
    ),
    *paired(
        "b09", 2723, 2834, "요충지를 취합시다\n빼앗으면 이긴 것이나 다름없습니다",
        "요충지를 차지합시다\n빼앗으면 이긴 것이나 다름없습니다", "要所を取りましょう\n奪えば勝ったも同然",
        "restore capture rather than collect",
    ),
    *paired("b09", 2376, 2463, "전진! 전진하라!", "전환! 전환하라!", "転進！　転進せよ！", "restore tactical turn rather than advance"),
    *paired(
        "b09", 2414, 2501, "물러나시는 것이 좋겠습니다\n뒷일은 맡아 주십시오", "물러나시는 것이 좋겠습니다\n뒷일은 저희에게 맡겨 주십시오",
        "退かれるがよろしい\n後事は任されたし", "retain the direct-PC-compatible W60 aftermath wording",
    ),
    *repeated(
        "b09", BASE, (2485, 2510), "정은 무용\n양쪽에서 짓뭉개겠습니다", "자비는 필요 없습니다\n양쪽에서 짓뭉개겠습니다",
        "情けは無用\n両側から叩き潰します", "translate battle 情け as mercy",
    ),
    *repeated(
        "b09", PK, (2572, 2597), "정은 무용\n양쪽에서 짓뭉개겠습니다", "자비는 필요 없습니다\n양쪽에서 짓뭉개겠습니다",
        "情けは無用\n両側から叩き潰します", "translate battle 情け as mercy",
    ),
    *repeated(
        "b09", BASE, (2491, 2516), "걸려들었다!\n끼워 넣어 쳐부순다!", "걸려들었다!\n에워싸고 쳐부순다!",
        "もらった！\n挟み込んで叩く！", "restore encirclement action",
    ),
    *repeated(
        "b09", PK, (2578, 2603), "걸려들었다!\n끼워 넣어 쳐부순다!", "걸려들었다!\n에워싸고 쳐부순다!",
        "もらった！\n挟み込んで叩く！", "restore encirclement action",
    ),
    *paired(
        "b09", 2662, 2761, "달려라! 반드시\n선봉의 창을 꽂아라!", "달려라! 반드시\n일번창을 거머쥐어라!",
        "駆けよ！　必ずや\n一番槍をつけるのだ！", "restore first-spear achievement",
    ),
    *paired(
        "b09", 3776, 4094, "강화 사자가 통했군요\n방침을 두고 반목한 것이겠지요", "강화 사절이 통했군요\n방침을 두고 반목한 것이겠지요",
        "講和の使者が効きましたな\n方針を巡って仲違いしたのでしょう", "use Korean envoy noun for 使者",
    ),
    t(
        "b09", PK, 2862, 0, "우리는 앞으로만 나아갈 수 있어요!\n장비를 잡아라!", "나아갈 길은 이것뿐이다!\n설비를 빼앗아라!",
        "進む他に道はなし！\n設備を奪うのだ！", "retain the direct-PC-compatible W60 facility repair",
    ),
    t(
        "b09", PK, 2899, 0, "인력이 필요합니까?\n장비쪽으로 가보겠습니다.", "인력이 필요하군요\n설비로 향하겠습니다.",
        "人手が必要ですね\n設備に向かいます", "retain the direct-PC-compatible W60 facility repair",
    ),
    t(
        "b09", PK, 2900, 0, "장비를 양도 할 수 없습니다!\n방어를 시작합시다!", "설비는 내줄 수 없습니다!\n우리가 방어에 나섭시다!",
        "設備は渡さんぞ！\n我らが守りにつく！", "retain the direct-PC-compatible W60 facility repair",
    ),
    t("b09", PK, 2248, 0, "본환이 노려지고 있다!\n젠장, 돌아간다!", "본성이 노려지고 있다!\n젠장, 돌아간다!", "本丸が狙われておる\nええい、戻るぞ！", "normalize 本丸 as main castle"),
    t("b09", PK, 2386, 0, "본환이 목표라고?\n돌아가서 기다렸다가 친다!", "본성이 목표라고?\n돌아가서 기다렸다가 친다!", "本丸が狙いだと？\n戻れ、待ち受けて叩く", "normalize 本丸 as main castle"),
    t("b09", PK, 2958, 0, "본환으로 향하라!\n적의 퇴로를 끊어라!", "본성으로 향하라!\n적의 퇴로를 끊어라!", "本丸に向かえ\n敵の退路を潰さん！", "normalize 本丸 as main castle"),
    t("b09", PK, 2959, 0, "본환으로 향합니다\n적을 동요시키는 것입니다", "본성으로 향합니다\n적을 동요시키는 것입니다", "本丸へ向かいます\n敵の動揺を誘うのです", "normalize 本丸 as main castle"),
    t("b09", PK, 2964, 0, "본환으로 향합니다!\n적도 동요할 것입니다.", "본성으로 향합니다!\n적도 동요할 것입니다.", "本丸へ向かいます！\n敵も動揺しましょう", "normalize 本丸 as main castle"),
    t("b09", PK, 2995, 0, "본환을 파괴합니다!", "본성을 파괴합니다!", "本丸を壊します！", "normalize 本丸 as main castle"),
    t("b09", PK, 2996, 0, "본환을 파괴하겠다!", "본성을 파괴하겠다!", "本丸を破壊せん！", "normalize 本丸 as main castle"),
    t("b09", PK, 3241, 0, "본환을 내줄 수는 없다!\n서둘러 후퇴하라!", "본성을 내줄 수는 없다!\n서둘러 후퇴하라!", "本丸はやらせぬ！\n急ぎ後退せよ！", "normalize 本丸 as main castle"),
    t("b09", PK, 3243, 0, "본환의 적을 쳐부순다!\n전력으로 돌아가라!", "본성의 적을 쳐부순다!\n전력으로 돌아가라!", "本丸の敵を潰す！\n全力で引き返すのだ！", "normalize 本丸 as main castle"),
    t("b09", PK, 3247, 0, "본환에 적군이!?\n서둘러 돌아가야 해!", "본성에 적군이!?\n서둘러 돌아가야 해!", "本丸に敵勢！？\nすぐ戻らなくては！", "normalize 本丸 as main castle"),
    t(
        "b09", PK, 4113, 0, "복병이 있었다!혼란한 틈에 쳐부수자!", "복병이 있었다! 혼란한 틈에 쳐부수자!",
        "伏兵がおったぞ！混乱している内に蹴散らすぞ！", "restore missing Korean sentence space",
    ),
)
TARGETS: tuple[Target, ...] = B06_TARGETS + B09_TARGETS

# Pinned from the no-write ``profile`` command after independent B06/B09
# target-matrix review.  build/verify/diff refuse profile, wrapper, scope, or
# classification-count drift.
EXPECTED_FINAL_PROFILES: Mapping[str, Any] = {
    BASE: w59.Profile(
        1_504_450,
        "19A45737ADEF3659AB602B81F0B2A6A9A72ACC781DFB9AF6159C96692ACB8605",
        1_498_548,
        "59367CAB1955AB5A570B38010E6C8F0A1EF124CF5D7C6C0CEF3447581100DAA1",
    ),
    PK: w59.Profile(
        1_806_530,
        "BCE7E45C89629A6BBF228A55270C72F903CA82633A7392627964CAB198F21A1A",
        1_799_448,
        "86BA02DE5FEA32A853258FBFD6D4D4A51476CA2CF313AA4E975B78D357A1196F",
    ),
    MSGDATA: w59.Profile(
        496_999,
        "34DAAAC9F8AE22445DD580FB5B8182FA9C6CD66C4DA78498E6B20286C5456215",
        495_032,
        "9FB501A16D7DF7D84559612A68775D75B6C1E6C0B853123194B81B7FBA8C7BDC",
    ),
    MSGEV: w59.Profile(
        994_719,
        "664DE71FCC5CBAB45860414EE4DE5DECA721AEE227D9D8EE0EF6F8176BFC5917",
        990_808,
        "87D950696A453382AE8BEAF7D8EBBEE7DD7FAB1C1BA68B3ECB6385FB1FE29CC4",
    ),
}
EXPECTED_FINAL_WRAPPERS: Mapping[str, Any] = {
    BASE: w59.WrapperProfile("0101F6A1FB7F0000", 1_504_426),
    PK: w59.WrapperProfile("0101442672020000", 1_806_506),
}
EXPECTED_FINAL_RECORD_COUNTS = {BASE: 104, PK: 273, MSGDATA: 4, MSGEV: 115}
EXPECTED_FINAL_TOTAL_RECORDS = 496
EXPECTED_CLASS_COUNTS = {
    BASE: {
        "b06": {"fresh": 5, "already": 0, "override": 0},
        "b09": {"fresh": 13, "already": 6, "override": 1},
    },
    PK: {
        "b06": {"fresh": 20, "already": 1, "override": 1},
        "b09": {"fresh": 13, "already": 20, "override": 1},
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise UnionError(message)


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def require_private(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise UnionError(f"private candidate escapes tmp root: {resolved}") from exc
    return resolved


def literal_signature(value: str) -> tuple[int, tuple[int, ...]]:
    controls = tuple(ord(char) for char in value if ord(char) < 32 and char not in ("\n", "\r"))
    return (value.count("\n"), controls)


def load_direct_jp(resource: str) -> MsgGameArchive:
    source = JP_SOURCES[resource]
    path = source.path.resolve(strict=True)
    parts = {part.casefold() for part in path.parts}
    require("switch" not in parts and "sc" not in parts, f"non-PC source forbidden: {path}")
    packed = path.read_bytes()
    header, raw = decompress_wrapper(packed)
    profile = source.profile
    require(len(packed) == profile.packed_size, f"JP packed size drift: {resource}")
    require(sha256(packed) == profile.packed_sha256, f"JP packed hash drift: {resource}")
    require(len(raw) == profile.raw_size, f"JP raw size drift: {resource}")
    require(sha256(raw) == profile.raw_sha256, f"JP raw hash drift: {resource}")
    archive = parse_raw_msggame(raw)
    require(rebuild_raw_msggame(archive) == raw, f"JP raw round-trip drift: {resource}")
    require(header is not None, f"JP wrapper missing: {resource}")
    return archive


def literal_at(archive: MsgGameArchive, coordinate: tuple[int, int, int], label: str) -> str:
    block_id, record_id, literal_id = coordinate
    require(block_id < len(archive.blocks), f"{label}: missing block {block_id}")
    block = archive.blocks[block_id]
    require(record_id < len(block.records), f"{label}: missing record {coordinate}")
    record = block.records[record_id]
    literals = parse_record_literals(record)
    require(literal_id < len(literals), f"{label}: missing literal {coordinate}")
    return literals[literal_id].text


def target_map(resource: str, audit: str) -> dict[tuple[int, int, int], Target]:
    selected = [target for target in TARGETS if target.resource == resource and target.audit == audit]
    mapped = {target.coordinate: target for target in selected}
    require(len(mapped) == len(selected), f"duplicate {audit} target: {resource}")
    return mapped


def all_target_maps() -> dict[str, dict[str, dict[tuple[int, int, int], Target]]]:
    maps = {resource: {audit: target_map(resource, audit) for audit in ("b06", "b09")} for resource in MSGGAME_RESOURCES}
    seen: set[tuple[str, tuple[int, int, int]]] = set()
    for resource, by_audit in maps.items():
        for audit, values in by_audit.items():
            for coordinate in values:
                key = (resource, coordinate)
                require(key not in seen, f"cross-audit duplicate target: {audit} {resource} {coordinate}")
                seen.add(key)
    require(bool(seen), "W61 target list is empty")
    return maps


def parse_w60(resource: str, blob: bytes) -> MsgGameArchive:
    return w59.assert_archive_parse_roundtrip(f"W60 {resource}", blob)


def classify_and_overlay(
    resource: str,
    w45_blob: bytes,
    w60_blob: bytes,
    jp_archive: MsgGameArchive,
    by_audit: Mapping[str, Mapping[tuple[int, int, int], Target]],
) -> tuple[bytes, dict[tuple[int, int, int], str], dict[str, Mapping[str, tuple[tuple[int, int, int], ...]]]]:
    w45 = w59.assert_archive_parse_roundtrip(f"W45 {resource}", w45_blob)
    before = parse_w60(resource, w60_blob)
    effective: dict[tuple[int, int, int], str] = {}
    result: dict[str, Mapping[str, tuple[tuple[int, int, int], ...]]] = {}
    for audit, targets in by_audit.items():
        classes: dict[str, list[tuple[int, int, int]]] = {"fresh": [], "already": [], "override": []}
        for coordinate, target in sorted(targets.items()):
            source_text = literal_at(w45, coordinate, f"W45 {resource}")
            jp_text = literal_at(jp_archive, coordinate, f"JP {resource}")
            current = literal_at(before, coordinate, f"W60 {resource}")
            require(source_text == target.current_ko, f"W45 KO preimage drift: {audit} {resource} {coordinate}")
            require(jp_text == target.pc_jp, f"direct PC JP evidence drift: {audit} {resource} {coordinate}")
            require(source_text != target.target_ko, f"no-op target: {audit} {resource} {coordinate}")
            require(
                literal_signature(source_text) == literal_signature(target.target_ko),
                f"manual LF/control drift: {audit} {resource} {coordinate}",
            )
            if current == target.target_ko:
                classes["already"].append(coordinate)
            elif current == source_text:
                classes["fresh"].append(coordinate)
                effective[coordinate] = target.target_ko
            else:
                classes["override"].append(coordinate)
                effective[coordinate] = target.target_ko
        result[audit] = {name: tuple(values) for name, values in classes.items()}
    output = w59.rebuild_packed_with_literals(w60_blob, effective)
    after = parse_w60(resource, output)
    w59.assert_same_literal_topology_and_skeleton(f"W60-to-W61 {resource}", before, after)
    before_texts = w59.literal_texts(before)
    after_texts = w59.literal_texts(after)
    before_records = w59.archive_records(before)
    after_records = w59.archive_records(after)
    require(
        {coordinate for coordinate in before_texts if before_texts[coordinate] != after_texts[coordinate]} == set(effective),
        f"W61 literal scope drift: {resource}",
    )
    require(
        {key for key in before_records if before_records[key].data != after_records[key].data}
        == {(block, record) for block, record, _literal in effective},
        f"W61 record scope drift: {resource}",
    )
    return output, effective, result


def profile(blob: bytes) -> Any:
    return w59.profile(blob)


def profile_dict(value: Any) -> dict[str, Any]:
    return w59.profile_dict(value)


def prepare(*, require_output_profiles: bool) -> Bundle:
    maps = all_target_maps()
    base = w60.prepare(require_output_profiles=True)
    w60.verify_private_candidate(base)
    w45 = w59.load_w45_sources()
    outputs: dict[str, bytes] = {}
    effective: dict[str, dict[tuple[int, int, int], str]] = {}
    classifications: dict[str, dict[str, Mapping[str, tuple[tuple[int, int, int], ...]]]] = {}
    for resource in MSGGAME_RESOURCES:
        output, selected, classified = classify_and_overlay(
            resource, w45[resource], base.outputs[resource], load_direct_jp(resource), maps[resource]
        )
        outputs[resource] = output
        effective[resource] = selected
        classifications[resource] = classified
    outputs[MSGDATA] = base.outputs[MSGDATA]
    outputs[MSGEV] = base.outputs[MSGEV]
    profiles = {resource: profile(blob) for resource, blob in outputs.items()}
    base_records, base_literals = w60.msggame_counts(w45[BASE], outputs[BASE])
    pk_records, pk_literals = w60.msggame_counts(w45[PK], outputs[PK])
    w45_event = w60.W45_EVENT_PATH.read_bytes()
    final_counts = {
        BASE: base_records,
        PK: pk_records,
        MSGDATA: 4,
        MSGEV: w60.event_count(w45_event, outputs[MSGEV]),
    }
    if require_output_profiles:
        require(profiles == EXPECTED_FINAL_PROFILES, "W61 output profile drift")
        for resource in MSGGAME_RESOURCES:
            require(w59.wrapper_profile(outputs[resource]) == EXPECTED_FINAL_WRAPPERS[resource], f"W61 wrapper drift: {resource}")
        require(final_counts == EXPECTED_FINAL_RECORD_COUNTS, "W61 final record count drift")
        require(sum(final_counts.values()) == EXPECTED_FINAL_TOTAL_RECORDS, "W61 final total drift")
        class_counts = {
            resource: {
                audit: {name: len(values[name]) for name in ("fresh", "already", "override")}
                for audit, values in classifications[resource].items()
            }
            for resource in MSGGAME_RESOURCES
        }
        require(class_counts == EXPECTED_CLASS_COUNTS, "W61 classification-count drift")
    rows = []
    for resource in MSGGAME_RESOURCES:
        for audit in ("b06", "b09"):
            for target in sorted(maps[resource][audit].values(), key=lambda value: value.coordinate):
                rows.append({
                    "audit": audit,
                    "resource": resource,
                    "slot": target.coordinate_text,
                    "current_ko": target.current_ko,
                    "target_ko": target.target_ko,
                    "pc_jp": target.pc_jp,
                    "rationale": target.rationale,
                    "manual_lf_count": target.current_ko.count("\n"),
                })
    audit = {
        "schema": "nobu16.kr.pc-private-union-composite-wave61-audit.v1",
        "candidate_only": True,
        "source_policy": {
            "platform": "Steam PC direct W45 Korean and pristine PC Japanese only",
            "switch_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "base_w60": {resource: profile_dict(profile(base.outputs[resource])) for resource in ALL_RESOURCES},
        "direct_jp": {resource: profile_dict(JP_SOURCES[resource].profile) for resource in MSGGAME_RESOURCES},
        "target_rows": rows,
        "classifications": {
            resource: {
                audit_name: {name: [list(value) for value in classes[name]] for name in ("fresh", "already", "override")}
                for audit_name, classes in classifications[resource].items()
            }
            for resource in MSGGAME_RESOURCES
        },
        "w60_to_w61_changed_literals": {resource: len(effective[resource]) for resource in MSGGAME_RESOURCES},
        "w45_to_w61_literals": {BASE: base_literals, PK: pk_literals},
        "final_record_counts": final_counts,
        "final_total_records": sum(final_counts.values()),
        "outputs": {resource: profile_dict(profiles[resource]) for resource in ALL_RESOURCES},
    }
    manifest = {
        "schema": "nobu16.kr.pc-private-union-composite-wave61-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {
            resource: {
                "relative": resource,
                "output": profile_dict(profiles[resource]),
                "changed_record_count": final_counts[resource],
            }
            for resource in ALL_RESOURCES
        },
        "final_total_records": sum(final_counts.values()),
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }
    return Bundle(outputs, profiles, effective, classifications, final_counts, audit, manifest)


def write_candidate(bundle: Bundle) -> Path:
    output = require_private(CANDIDATE_ROOT)
    require(not output.exists(), f"W61 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W61 candidate staging already exists: {staging}")
    staging.mkdir(parents=True)
    try:
        for relative, blob in bundle.outputs.items():
            path = staging / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(blob)
        (staging / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (staging / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        os.replace(staging, output)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return output


def verify_private_candidate(bundle: Bundle | None = None) -> dict[str, Any]:
    bundle = bundle or prepare(require_output_profiles=True)
    root = require_private(CANDIDATE_ROOT)
    require(root.is_dir(), f"W61 candidate missing: {root}")
    expected_files = {"audit.v1.json", "candidate_manifest.v1.json", *ALL_RESOURCES}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W61 candidate file scope drift: {sorted(actual_files)}")
    for relative, blob in bundle.outputs.items():
        require((root / relative).read_bytes() == blob, f"W61 candidate differs: {relative}")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W61 audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W61 manifest differs")
    return {
        "candidate_root": root.relative_to(REPO).as_posix(),
        "final_record_counts": bundle.final_record_counts,
        "final_total_records": sum(bundle.final_record_counts.values()),
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "build_pc_private_union_composite_wave61_v1.py",
        WORKSTREAM / "test_pc_private_union_composite_wave61_v1.py",
        WORKSTREAM / "README_KO.md",
    ):
        require(path.is_file(), f"W61 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W61 trailing whitespace: {path.name}:{number}")


def command_profile() -> int:
    bundle = prepare(require_output_profiles=False)
    print(json.dumps({
        "profiles": {resource: profile_dict(value) for resource, value in bundle.profiles.items()},
        "wrappers": {resource: {
            "prefix_hex": w59.wrapper_profile(bundle.outputs[resource]).prefix_hex,
            "compressed_size": w59.wrapper_profile(bundle.outputs[resource]).compressed_size,
        } for resource in MSGGAME_RESOURCES},
        "classifications": {
            resource: {
                audit: {name: [list(value) for value in classes[name]] for name in ("fresh", "already", "override")}
                for audit, classes in bundle.classifications[resource].items()
            }
            for resource in MSGGAME_RESOURCES
        },
        "w60_to_w61_changed_literals": {resource: len(bundle.effective[resource]) for resource in MSGGAME_RESOURCES},
        "final_record_counts": bundle.final_record_counts,
        "final_total_records": sum(bundle.final_record_counts.values()),
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        return command_profile()
    if command == "build":
        bundle = prepare(require_output_profiles=True)
        write_candidate(bundle)
        print(json.dumps(verify_private_candidate(bundle), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if command == "verify-private":
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    bundle = prepare(require_output_profiles=True)
    source_whitespace_check()
    result = verify_private_candidate(bundle)
    result["private_authoring_whitespace_check"] = "passed"
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
