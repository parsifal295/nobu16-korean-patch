#!/usr/bin/env python3
"""Read-only PC-only triage for the next Korean character-dialogue repairs.

The catalogue deliberately contains only static ``msggame`` records where the
installed Korean JP-route resource still carries Japanese ``01 43`` inflection
commands, while the same PC EN/SC/TC record carries none.  It is a review
catalogue, not an overlay builder: it never rebuilds a message archive, writes
Steam, or uses a Switch Korean asset.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
MSGGAME = REPO / "workstreams" / "msggame"
WAVE4_PATH = REPO / "workstreams" / "pc_dialogue_quality_wave4_v1" / "build_pc_dialogue_quality_wave4_v1.py"
RESULT = WORKSTREAM / "pc_dialogue_quality_triage_candidates.v1.json"
EVENT_RESULT = WORKSTREAM / "pk_msgev_okehazama_4494_4510_priority.v1.json"
VALIDATION = WORKSTREAM / "validation.v1.json"

sys.path[:0] = [str(TOOLS), str(MSGGAME)]

from msggame_format import parse_packed_msggame, parse_record_literals  # noqa: E402
from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
SOURCE_PATHS = {
    "base_current_ko": STEAM / "MSG" / "JP" / "msggame.bin",
    "base_pristine_pc_jp": Path(r"I:\Workspaces\NOBU16-Korean\private-inputs\legacy-pc-root\MSG\JP\msggame.bin"),
    "base_pc_sc": STEAM / "MSG" / "SC" / "msggame.bin",
    "base_pc_tc": STEAM / "MSG" / "TC" / "msggame.bin",
    "pk_current_ko": STEAM / "MSG_PK" / "JP" / "msggame.bin",
    "pk_pristine_pc_jp": (
        STEAM
        / "KR_PATCH_BACKUP"
        / "file_only_transaction"
        / "steam-jp-1.1.7-v0.6.0"
        / "originals"
        / "MSG_PK"
        / "JP"
        / "msggame.bin"
    ),
    "pk_pc_en": STEAM / "MSG_PK" / "EN" / "msggame.bin",
    "pk_pc_sc": STEAM / "MSG_PK" / "SC" / "msggame.bin",
    "pk_pc_tc": STEAM / "MSG_PK" / "TC" / "msggame.bin",
}
EXPECTED_SOURCE_SHA256 = {
    "base_current_ko": "83C4DF9326DB1487707FDABE9CF2A00380144D14D3AC4A4FCD02513C8E3C279E",
    "base_pristine_pc_jp": "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
    "base_pc_sc": "B2FC3C18DA0F03ACFA93B1EAB0D09FBFCF7CD5076E667602D1AF212953A09BF7",
    "base_pc_tc": "20E710A11CDADFAF514EBC3B9C664E9C57B1A737138F29BF38CFB6527C0A5E95",
    "pk_current_ko": "31950B8213AC80C9BCB866163EE7B4B655440ADF863DED21186273E3F8A34BDB",
    "pk_pristine_pc_jp": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    "pk_pc_en": "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    "pk_pc_sc": "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    "pk_pc_tc": "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
}

SCHEMA = "nobu16.kr.pc-dialogue-quality-triage.v1"
VALIDATION_SCHEMA = "nobu16.kr.pc-dialogue-quality-triage-validation.v1"
EXPECTED_CANDIDATE_COUNT = 30
TERMINATOR = b"\x05\x05\x05"

EVENT_SOURCE_PATHS = {
    "current_pc_ko": STEAM / "MSG_PK" / "JP" / "msgev.bin",
    "pristine_pc_jp": (
        STEAM
        / "KR_PATCH_BACKUP"
        / "file_only_transaction"
        / "steam-jp-1.1.7-v0.6.0"
        / "originals"
        / "MSG_PK"
        / "JP"
        / "msgev.bin"
    ),
    "pc_en": STEAM / "MSG_PK" / "EN" / "msgev.bin",
    "pc_sc": STEAM / "MSG_PK" / "SC" / "msgev.bin",
    "pc_tc": STEAM / "MSG_PK" / "TC" / "msgev.bin",
}
EVENT_SOURCE_SHA256 = {
    "current_pc_ko": "134F6356B194AE319125D369A23EBDA11CA8C75FB79EFA7C987D956EDD4CF154",
    "pristine_pc_jp": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
    "pc_en": "BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E",
    "pc_sc": "7C443515D8B42DD5D1A516FE606DB8880F21296F7BEF0C5D067FEA7D9FC991BA",
    "pc_tc": "89D183BA95C3BB83B52A5EE408664D5247C695A1DB192105A5D906737E6F78B6",
}
EVENT_STRING_COUNT = 17_916

# These coordinates were repaired in Wave 7 and must never re-enter this
# independent catalogue.
WAVE7_EXCLUDED = {
    ("base", 6, 1518),
    ("base", 6, 1519),
    ("base", 6, 1520),
    ("pk", 6, 1524),
    ("pk", 6, 1525),
    ("pk", 6, 1526),
    ("pk", 6, 3887),
    ("pk", 8, 1095),
    ("pk", 8, 1104),
    ("pk", 8, 1111),
    ("pk", 8, 1178),
    ("pk", 8, 1180),
}


class TriageError(ValueError):
    """A pinned source or conservative static-safety contract changed."""


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    expected_ko: str
    expected_jp: str
    recommendation_ko: str
    rationale: str
    base_coordinate: tuple[int, int] | None
    pk_coordinate: tuple[int, int]


@dataclass(frozen=True)
class EventCandidate:
    entry_id: int
    expected_ko: str
    expected_jp: str
    recommendation_ko: str
    rationale: str


# Every recommendation preserves the existing manual line count.  The first
# eighteen entries are exact Base/PK source pairs; the remaining twelve are PK
# only.  All are static after removal of their JP-only 0143 fragments.
CANDIDATES = (
    Candidate(
        "C01",
        "백성을 다스리는 비결은 오직 진심뿐\n이 군의 장악은！",
        "民を治める極意は真心あるのみ\nこの郡の掌握は！",
        "백성을 다스리는 비결은 오직 진심뿐.\n이 군의 장악은 제게 맡기십시오!",
        "문장 끝이 일본어 0143 명령에 의존해 ‘이 군의 장악은’으로 끊긴다.",
        (2, 212),
        (2, 218),
    ),
    Candidate(
        "C02",
        "능숙한 언변으로 반드시 신용을\n얻어 오겠！",
        "得意の弁舌で必ずや信用を\n勝ち取って参！",
        "능숙한 언변으로 반드시 신용을\n얻어 오겠습니다!",
        "한국어 서술어 ‘얻어 오겠’이 미완성으로 끝난다.",
        (2, 216),
        (2, 222),
    ),
    Candidate(
        "C03",
        "내 영지는 한 치도 침범케 하지!\n굳게 지키는 데 전념한다！",
        "我が領地は寸土も侵させ！\n堅守に徹する！",
        "내 영지는 한 치도 침범하게 두지 않겠다!\n굳게 지키는 데 전념하겠다!",
        "부정 종결과 선언체가 일본어 0143 명령 뒤에 남아 한국어 문장이 불안정하다.",
        (2, 219),
        (2, 225),
    ),
    Candidate(
        "C04",
        "싸움이야말로 무가의 본분! 내 활약을\n기대！",
        "戦こそ武家の本分！　我が働きに\n期待！",
        "싸움이야말로 무가의 본분! 내 활약을\n기대해도 좋다!",
        "명령형 종결이 빠져 ‘내 활약을 기대’에서 끊긴다.",
        (2, 224),
        (2, 230),
    ),
    Candidate(
        "C05",
        "강공 따위 두려울 것 없\n지금이야말로 반격의 때！",
        "強攻など恐るるに足り\n今こそ反攻の時！",
        "강공 따위 두려울 것 없다.\n지금이야말로 반격의 때다!",
        "두 문장 모두 한국어 종결어미가 빠져 있다.",
        (2, 227),
        (2, 233),
    ),
    Candidate(
        "C06",
        "뒷일은…\n머리 쓰는 법이 다르까닭에…",
        "裏の仕事は…\n頭の使い方が違ゆえ…",
        "뒷일은 내게 맡겨라…\n머리 쓰는 법이 다르기 때문이지…",
        "‘다르까닭에’는 조사 결합 오류이며, 원문의 ‘맡겨라’ 의미도 빠졌다.",
        (2, 235),
        (2, 241),
    ),
    Candidate(
        "C07",
        "수상 전투에서는 질 수 없\n우리에게 해신의 가호가 있기를",
        "水上の戦いでは負けられ\n我らに海神の加護あらんことを",
        "수상 전투에서는 질 수 없다.\n우리에게 해신의 가호가 있기를.",
        "첫 문장의 부정 종결이 누락됐다.",
        (2, 238),
        (2, 244),
    ),
    Candidate(
        "C08",
        "재해는 최소한으로 억제하그러니\n걱정은 무용",
        "災害は最小限で抑えゆえ\n心配は無用",
        "재해는 최소한으로 억제할 테니\n걱정은 무용이다.",
        "‘억제하그러니’는 어간과 접속어미가 잘못 결합된 명백한 문법 오류다.",
        (2, 243),
        (2, 249),
    ),
    Candidate(
        "C09",
        "속히 성을 수선하여 적의\n공격에 대비한다！",
        "速やかに城を修繕し、敵からの\n攻撃に備える！",
        "속히 성을 수선하여 적의\n공격에 대비하겠다!",
        "대사체의 선언을 한국어 완결형으로 고정한다.",
        (2, 244),
        (2, 250),
    ),
    Candidate(
        "C10",
        "길 정비에는 자신이\n부디 성과로기대",
        "道の整備には自信が\nぜひとも成果に期待",
        "길 정비에는 자신이 있으니\n부디 성과를 기대해 주십시오.",
        "‘성과로기대’는 조사 누락과 띄어쓰기 결합 오류다.",
        (2, 246),
        (2, 252),
    ),
    Candidate(
        "C11",
        "지금이야말로 기마철포대의 위력을\n똑똑히 보여주마！",
        "今こそ、騎馬鉄砲隊の威力\n思い知らせてくれ！",
        "지금이야말로 기마철포대의 위력을\n똑똑히 보여 주마!",
        "같은 문장에 남은 일본식 전각 종결과 결합 표기를 정리한다.",
        (2, 253),
        (2, 259),
    ),
    Candidate(
        "C12",
        "명인이라 칭송받는 축성 솜씨를,\n마음껏 발휘하겠!\n반드시 훌륭한 성하마을로 만들어 보이겠",
        "名手と謳われし普請の腕、\n存分に発揮！\n必ずや見事な城下にしてみせ",
        "명인이라 칭송받는 축성 솜씨를\n마음껏 발휘하겠다!\n반드시 훌륭한 성하마을로 만들어 보이겠다!",
        "두 서술어가 미완성으로 끝나고, 일본식 종결부호가 섞여 있다.",
        None,
        (2, 321),
    ),
    Candidate(
        "C13",
        "모략이라면 이에게 맡기십시오!\n즉시 첩자를 보내 우리의 계책이\n성공하도록 지휘하겠",
        "謀とあらばこのにお任せを！\n直ちに間者を遣わし、我らが策が\n成就するよう、差配",
        "모략이라면 제게 맡기십시오!\n즉시 첩자를 보내 우리의 계책이\n성공하도록 지휘하겠습니다.",
        "지시 대상이 ‘이’로 잘못 남고, 마지막 서술어도 미완성이다.",
        None,
        (2, 325),
    ),
    Candidate(
        "C14",
        "내 개를 전령으로 써서\n훌륭히 이끌어 보이겠",
        "我が犬を伝令に用いて\n見事率いてみせ",
        "내 개를 전령으로 써서\n훌륭히 이끌어 보이겠다.",
        "의도적인 ‘개를 전령으로’ 내용은 보존하되, 미완성 종결만 고친다.",
        None,
        (2, 357),
    ),
    Candidate(
        "C15",
        "지혜와 재주는 익혀도 짐이 되지 않는다…\n『이로하 노래』의 가르침을 널리 알리겠",
        "知恵能は身につきぬれど荷にならず…\n『いろは歌』の教えを広めるとし",
        "지혜와 재주는 익혀도 짐이 되지 않는다…\n『이로하 노래』의 가르침을 널리 알리겠다.",
        "의미는 유지되어 있으나 마지막 한국어 종결이 누락됐다.",
        None,
        (2, 358),
    ),
    Candidate(
        "C16",
        "상대의 마음을 얻는 방법은 알고 있\n우리에게 유리하도록\n일을 이끌어 보이겠",
        "相手の懐に入る術は心得て\n我らに有利となるよう\n事を運んでご覧に入れ",
        "상대의 마음을 얻는 방법은 알고 있다.\n우리에게 유리하도록\n일을 이끌어 보이겠다.",
        "첫·마지막 서술어가 모두 0143 명령에 기대어 한국어로 끝나지 않는다.",
        None,
        (2, 359),
    ),
    Candidate(
        "C17",
        "전선에 선 이상\n죽기를 각오하고 싸우겠！",
        "前線に立つからには\n決死の覚悟で戦う！",
        "전선에 선 이상\n죽기를 각오하고 싸우겠다!",
        "대사체 종결을 한국어 완결형으로 고정한다.",
        None,
        (2, 360),
    ),
    Candidate(
        "C18",
        "방울 소리가 울리는 곳에 내가 있다!\n덤빌 자는！",
        "鈴の音の鳴るところに我はあり！\nかかってくる者は！",
        "방울 소리가 울리는 곳에 내가 있다!\n덤빌 자는 없느냐!",
        "원문과 PC EN/SC/TC가 요구하는 도발 의문문이 한국어에서 잘렸다.",
        None,
        (2, 361),
    ),
    Candidate(
        "C19",
        "창을 겨누어라!\n기마대가 마음대로 하게 두지 않겠다！",
        "槍を構え！\n騎馬隊の好きにはさせ！",
        "창을 겨누어라!\n기마대가 마음대로 하게 두지 않겠다!",
        "문장 자체는 완결돼 보이지만, JP 전용 0143 명령과 전각 종결이 남아 있다.",
        None,
        (2, 363),
    ),
    Candidate(
        "C20",
        "아직… 아직 포기하지 않겠!\n몇 번이고 되찾아 보이겠！",
        "まだ…まだ諦め！\n何度でも奪い返してみせる！",
        "아직… 아직 포기하지 않겠다!\n몇 번이고 되찾아 보이겠다!",
        "두 한국어 종결어미가 잘려 있다.",
        None,
        (2, 364),
    ),
    Candidate(
        "C21",
        "서로의 가문을 지키기 위해\n우리가 손을 잡는 것은 좋은 일이겠지\n잠시 함께 싸우겠",
        "互いの家を守るため\n我らが手を結ぶのは良い話\nしばし共に戦",
        "서로의 가문을 지키기 위해\n우리가 손을 잡는 것은 좋은 일이겠지.\n잠시 함께 싸우겠다.",
        "두 번째·세 번째 행의 종결이 한국어로 완성되지 않았다.",
        None,
        (2, 366),
    ),
    Candidate(
        "C22",
        "하늘이여 보라!\n백성을 위해 이 몸 바쳐！",
        "天よ見て！\n民のためにこの身捧げ！",
        "하늘이여, 보라!\n백성을 위해 이 몸을 바치겠다!",
        "목적격과 선언 종결이 빠져 있다.",
        (2, 408),
        (2, 415),
    ),
    Candidate(
        "C23",
        "사나운 적에게는 매와 같이!\n용병의 극의는 이것！",
        "荒ぶる敵には、鷹の如くに！\n用兵の極意はこれ！",
        "사나운 적에게는 매와 같이!\n용병의 극의는 이것이다!",
        "‘용병의 극의는 이것’이 미완성 서술문으로 남는다.",
        (2, 410),
        (2, 417),
    ),
    Candidate(
        "C24",
        "내 검술\n그 일단을 여기서 보여！",
        "我が剣技\nその一端をここに見せ！",
        "내 검술의\n일단을 여기서 보여 주마!",
        "소유격과 동사 종결이 빠져 문장이 끊긴다.",
        (2, 412),
        (2, 419),
    ),
    Candidate(
        "C25",
        "히익! …뭐, 뭐지?\n저, 적이 혼란에 빠졌！",
        "ひょえー！　…な、なんじゃ？\nて、敵が取り乱しておる！",
        "히익! …뭐, 뭐지?\n저, 적이 혼란에 빠졌다!",
        "현재형이 미완성이고, 상대 언어 종결 명령이 남아 있다.",
        None,
        (2, 446),
    ),
    Candidate(
        "C26",
        "히익!\n저, 적이 혼란에 빠졌！",
        "ひょえー！\nて、敵が取り乱しておる！",
        "히익!\n저, 적이 혼란에 빠졌다!",
        "C25와 같은 대사의 짧은 변형으로 종결 오류가 동일하다.",
        None,
        (2, 447),
    ),
    Candidate(
        "C27",
        "휘하가 될 장수들에게\n활약의 장을 마음껏 내리어！",
        "配下となる将らに\n活躍の場を存分に与え！",
        "휘하가 될 장수들에게\n활약의 장을 마음껏 내리겠다!",
        "‘내리어’가 대사 종결로 끝나 문장이 미완성이다.",
        (2, 489),
        (2, 503),
    ),
    Candidate(
        "C28",
        "무가에도 풍류는 빠질 수 없\n풍류의 마음이야말로 교섭의 요체인가 하옵니다",
        "武家にも風流は欠かせ\n雅びの心こそ交渉の要諦かと",
        "무가에도 풍류는 빠질 수 없지요.\n풍류의 마음이야말로 교섭의 요체라 하옵니다.",
        "부정 종결과 인용 종결이 일본어 명령의 영향을 받아 끊겼다.",
        (2, 502),
        (2, 516),
    ),
    Candidate(
        "C29",
        "출진。나의 병법을\n똑똑히 보여 드리",
        "出陣。我が兵法\nとくとご覧に入れ",
        "출진! 나의 병법을\n똑똑히 보여 드리겠습니다.",
        "일본식 마침표와 한국어 미완성 경어가 함께 남아 있다.",
        (2, 512),
        (2, 526),
    ),
    Candidate(
        "C30",
        "포위병 마음대로 두지\n이쪽에서도 반격！",
        "包囲兵の好きにはさせ\nこちらからも反撃！",
        "포위병 마음대로 하게 두지 않겠다.\n이쪽에서도 반격하겠다!",
        "두 행 모두 한국어 서술어·종결이 누락됐다.",
        (2, 519),
        (2, 533),
    ),
)


EVENT_CANDIDATES = (
    EventCandidate(
        4495,
        "\x1bCA노부나가\x1bCZ도 말에서 내려\n우마마와리슈를 이끌고,\n졸병들 사이에서 직접 칼을 휘둘렀다.",
        "\x1bCA信長\x1bCZも馬を下り、馬廻衆を引き連れ\n雑兵に交じって自ら刀を振るい、",
        "\x1bCA노부나가\x1bCZ도 말에서 내려\n측근 무사들을 이끌고,\n졸병들 사이에서 직접 칼을 휘둘렀다.",
        "馬廻衆를 음역한 ‘우마마와리슈’를 PC EN의 closest officers와 SC/TC의 의미에 맞춰 풀어쓴다.",
    ),
    EventCandidate(
        4502,
        "(이것이 가이도 제일의 무사\n\x1bCA이마가와 지부타이후\x1bCZ인가.\n이것이 오랫동안 나를 괴롭힌 자……)",
        "（これが海道一の弓取り・\x1bCA今川治部大輔\x1bCZか\n　これが、俺を長年苦しめたもの…）",
        "(이것이 도카이도 제일의 무장,\n\x1bCA이마가와 요시모토\x1bCZ인가.\n이것이 오랫동안 나를 괴롭힌 자……)",
        "海道一の弓取り와 治部大輔의 불명확한 음역을, 해당 인물의 통용 이름과 역할로 바꿔 이해 가능하게 한다.",
    ),
    EventCandidate(
        4506,
        "\x1bCA노부나가\x1bCZ는 \x1bCA요시모토\x1bCZ가 지녔던 ‘소자\n사몬지’ 칼에 다음과 같이 새기고,\n자신의 애도로 삼았다고 전한다.",
        "\x1bCA信長\x1bCZは\x1bCA義元\x1bCZの所持していた\n「宗三左文字」の太刀にこう刻み、\n自らの愛刀にしたと伝わっている。",
        "\x1bCA노부나가\x1bCZ는 \x1bCA요시모토\x1bCZ가 지녔던 ‘소자\n사몬지’ 칼에 다음과 같이 새기고,\n그 칼을 애검으로 삼았다고 전한다.",
        "愛刀의 동음이의어 ‘애도’ 대신 뜻이 분명한 ‘애검’을 사용한다.",
    ),
    EventCandidate(
        4508,
        "\x1bCA이마가와 요시모토\x1bCZ의 죽음은\n한 다이묘였던 \x1bCA오다 노부나가\x1bCZ를\n전국시대 중심으로 밀어 올렸다…",
        "海道一の弓取り、\n\x1bCA今川義元\x1bCZの死は一大名\x1bCA織田信長\x1bCZを\n戦国の表舞台に押し上げただけでなく…",
        "도카이도 제일의 무장이던\n\x1bCA이마가와 요시모토\x1bCZ의 죽음은\n\x1bCA노부나가\x1bCZ를 천하의 중심에 세웠다…",
        "원문의 수식어를 되살리고 ‘전국시대 중심’의 어색한 결합을 자연스러운 서술로 고친다. 다음 문장의 ‘또한’으로 영향을 이어 간다.",
    ),
    EventCandidate(
        4509,
        "고소슨 삼국동맹의 동요와,\n그에 따른 \x1bCA[b1448]\x1bCZ의 간토 출병,\n\x1bCB미카와 마쓰다이라 가문\x1bCZ의 독립 등,",
        "甲相駿三国同盟の動揺、\nそれによる\x1bCA[b1448]\x1bCZによる関東出兵\n\x1bCB三河松平家\x1bCZの独立など、",
        "또한, 갑상준 삼국 동맹의 동요와,\n그에 따른 \x1bCA[b1448]\x1bCZ의 간토 출병,\n\x1bCB미카와 마쓰다이라 가문\x1bCZ의 독립 등,",
        "甲相駿의 의미를 잃은 ‘고소슨’ 음역을 한자음 기반의 ‘갑상준’으로 바로잡고, 앞 문장의 영향 관계를 자연스럽게 잇는다.",
    ),
)


def load_wave4() -> Any:
    spec = importlib.util.spec_from_file_location("triage_wave4", WAVE4_PATH)
    if spec is None or spec.loader is None:
        raise TriageError(f"cannot load parser helper: {WAVE4_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


WAVE4 = load_wave4()


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


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def coordinate_text(coordinate: tuple[int, int]) -> str:
    return f"{coordinate[0]}:{coordinate[1]}"


def record_text(record: Any) -> str:
    return "".join(literal.text for literal in parse_record_literals(record))


def record_literals(record: Any) -> list[str]:
    return [literal.text for literal in parse_record_literals(record)]


def source_records() -> tuple[dict[str, dict[tuple[int, int], Any]], dict[str, str]]:
    records: dict[str, dict[tuple[int, int], Any]] = {}
    hashes: dict[str, str] = {}
    for name, path in SOURCE_PATHS.items():
        if not path.is_file():
            raise TriageError(f"required PC source is absent: {path}")
        actual = sha256_path(path)
        expected = EXPECTED_SOURCE_SHA256[name]
        if actual != expected:
            raise TriageError(f"source hash changed for {name}: {actual}")
        hashes[name] = actual
        records[name] = WAVE4.records_by_coordinate(path.read_bytes())
    return records, hashes


def target_sources(resource: str) -> tuple[str, str, tuple[str, ...]]:
    if resource == "base":
        return "base_current_ko", "base_pristine_pc_jp", ("base_pc_sc", "base_pc_tc")
    if resource == "pk":
        return "pk_current_ko", "pk_pristine_pc_jp", ("pk_pc_en", "pk_pc_sc", "pk_pc_tc")
    raise TriageError(f"unknown resource family: {resource}")


def inspect_target(
    records: dict[str, dict[tuple[int, int], Any]],
    resource: str,
    coordinate: tuple[int, int],
    expected_ko: str,
    expected_jp: str,
) -> dict[str, Any]:
    if (resource, *coordinate) in WAVE7_EXCLUDED:
        raise TriageError(f"Wave 7 coordinate was reintroduced: {resource} {coordinate_text(coordinate)}")
    current_name, jp_name, reference_names = target_sources(resource)
    try:
        current = records[current_name][coordinate]
        jp = records[jp_name][coordinate]
    except KeyError as exc:
        raise TriageError(f"missing PC record {resource} {coordinate_text(coordinate)}") from exc
    current_text = record_text(current)
    jp_text = record_text(jp)
    if current_text != expected_ko:
        raise TriageError(f"current KO text differs at {resource} {coordinate_text(coordinate)}")
    if jp_text != expected_jp:
        raise TriageError(f"PC JP text differs at {resource} {coordinate_text(coordinate)}")

    commands = WAVE4.opaque_commands(current)
    if not commands:
        raise TriageError(f"current KO has no 0143 command at {resource} {coordinate_text(coordinate)}")
    opaque = WAVE4.opaque_bytes(current)
    expected_opaque = b"".join(command for _offset, command in commands) + TERMINATOR
    if opaque != expected_opaque:
        raise TriageError(f"record is not fully static at {resource} {coordinate_text(coordinate)}")
    if any(command[:2] != b"\x01\x43" or len(command) != 6 for _offset, command in commands):
        raise TriageError(f"invalid opaque command at {resource} {coordinate_text(coordinate)}")

    reference_texts: dict[str, str] = {}
    for reference_name in reference_names:
        try:
            reference = records[reference_name][coordinate]
        except KeyError as exc:
            raise TriageError(
                f"same-record PC reference is absent at {resource} {coordinate_text(coordinate)} in {reference_name}"
            ) from exc
        if WAVE4.opaque_commands(reference):
            raise TriageError(
                f"PC reference retains 0143 at {resource} {coordinate_text(coordinate)} in {reference_name}"
            )
        reference_texts[reference_name] = record_text(reference)
    if not any(text.strip() for text in reference_texts.values()):
        raise TriageError(f"all PC EN/SC/TC references are empty at {resource} {coordinate_text(coordinate)}")

    return {
        "coordinate": coordinate_text(coordinate),
        "current_record_sha256": sha256_bytes(current.data),
        "current_literals": record_literals(current),
        "current_korean": current_text,
        "pristine_pc_japanese": jp_text,
        "current_0143_commands": [
            {"offset": offset, "hex": command.hex().upper()}
            for offset, command in commands
        ],
        "static_opaque_bytes": opaque.hex().upper(),
        "pc_reference_texts": reference_texts,
    }


def candidate_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if len(CANDIDATES) != EXPECTED_CANDIDATE_COUNT:
        raise TriageError(f"candidate count differs: {len(CANDIDATES)}")
    if len({candidate.candidate_id for candidate in CANDIDATES}) != EXPECTED_CANDIDATE_COUNT:
        raise TriageError("candidate id is duplicated")
    if len({candidate.pk_coordinate for candidate in CANDIDATES}) != EXPECTED_CANDIDATE_COUNT:
        raise TriageError("PK coordinate is duplicated")

    records, hashes = source_records()
    rows: list[dict[str, Any]] = []
    for candidate in CANDIDATES:
        if candidate.expected_ko.count("\n") != candidate.recommendation_ko.count("\n"):
            raise TriageError(f"manual line count changes in recommendation {candidate.candidate_id}")
        targets: dict[str, Any] = {}
        if candidate.base_coordinate is not None:
            targets["base"] = inspect_target(
                records,
                "base",
                candidate.base_coordinate,
                candidate.expected_ko,
                candidate.expected_jp,
            )
        targets["pk"] = inspect_target(
            records,
            "pk",
            candidate.pk_coordinate,
            candidate.expected_ko,
            candidate.expected_jp,
        )
        rows.append(
            {
                "schema": SCHEMA,
                "id": candidate.candidate_id,
                "scope": "PC character dialogue / static 0143 cleanup",
                "targets": targets,
                "current_korean": candidate.expected_ko,
                "pc_japanese": candidate.expected_jp,
                "signal": (
                    "installed KO static record retains JP-only 0143 inflection command(s); "
                    "same-record PC EN/SC/TC has none"
                ),
                "rationale": candidate.rationale,
                "recommended_korean": candidate.recommendation_ko,
                "safe_apply_contract": {
                    "operation": "replace static record with one Korean literal and remove every 0143 command",
                    "manual_line_count_before": candidate.expected_ko.count("\n") + 1,
                    "manual_line_count_after": candidate.recommendation_ko.count("\n") + 1,
                    "required_remaining_opaque_bytes": TERMINATOR.hex().upper(),
                    "runtime_tokens_present": False,
                    "real_game_qa_required_before_release": True,
                },
            }
        )

    validation = {
        "schema": VALIDATION_SCHEMA,
        "candidate_count": len(rows),
        "candidate_ids": [row["id"] for row in rows],
        "candidate_coordinate_sha256": sha256_bytes(
            "".join(
                f"{row['id']}|{row['targets'].get('base', {}).get('coordinate', '-')}|{row['targets']['pk']['coordinate']}\n"
                for row in rows
            ).encode("ascii")
        ),
        "source_file_sha256": hashes,
        "source_policy": {
            "platform": "Steam PC",
            "allowed": ["PC Japanese", "PC English", "PC Simplified Chinese", "PC Traditional Chinese", "current PC Korean"],
            "switch_korean_translation_used": False,
            "steam_game_resource_written": False,
            "message_archive_rebuilt": False,
        },
        "static_contract": (
            "every target contains only removable 0143 commands plus 050505; "
            "same-record PC EN/SC/TC contains no 0143"
        ),
        "wave7_coordinate_reintroduced": False,
    }
    return rows, validation


def event_format_profile(text: str) -> dict[str, Any]:
    return {
        "esc_tags": re.findall(r"\x1bC.", text, re.DOTALL),
        "runtime_tokens": re.findall(r"\[[A-Za-z]+\d+\]", text),
        "printf_tokens": re.findall(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]", text),
        "manual_line_count": text.count("\n") + 1,
        "leading_whitespace": text[: len(text) - len(text.lstrip())],
        "trailing_whitespace": text[len(text.rstrip()) :],
    }


def event_tables() -> tuple[dict[str, Any], dict[str, str]]:
    tables: dict[str, Any] = {}
    hashes: dict[str, str] = {}
    for name, path in EVENT_SOURCE_PATHS.items():
        if not path.is_file():
            raise TriageError(f"required PC event source is absent: {path}")
        actual = sha256_path(path)
        if actual != EVENT_SOURCE_SHA256[name]:
            raise TriageError(f"event source hash changed for {name}: {actual}")
        _header, raw = decompress_wrapper(path.read_bytes())
        table = parse_message_table(raw)
        if table.string_count != EVENT_STRING_COUNT:
            raise TriageError(f"event table count changed for {name}: {table.string_count}")
        tables[name] = table
        hashes[name] = actual
    return tables, hashes


def event_priority_report() -> tuple[dict[str, Any], dict[str, Any]]:
    tables, hashes = event_tables()
    rows: list[dict[str, Any]] = []
    for candidate in EVENT_CANDIDATES:
        entry_id = candidate.entry_id
        if not 4494 <= entry_id <= 4510:
            raise TriageError(f"event candidate escapes requested range: {entry_id}")
        current = tables["current_pc_ko"].texts[entry_id]
        jp = tables["pristine_pc_jp"].texts[entry_id]
        if current != candidate.expected_ko:
            raise TriageError(f"current event Korean differs at {entry_id}")
        if jp != candidate.expected_jp:
            raise TriageError(f"PC event Japanese differs at {entry_id}")
        if event_format_profile(current) != event_format_profile(candidate.recommendation_ko):
            raise TriageError(f"event format contract differs at {entry_id}")
        rows.append(
            {
                "id": entry_id,
                "current_korean": current,
                "pc_japanese": jp,
                "pc_reference_texts": {
                    language: tables[language].texts[entry_id]
                    for language in ("pc_en", "pc_sc", "pc_tc")
                },
                "rationale": candidate.rationale,
                "recommended_korean": candidate.recommendation_ko,
                "safe_apply_contract": {
                    "esc_runtime_printf_and_edge_whitespace_unchanged": True,
                    "manual_line_count_before": current.count("\n") + 1,
                    "manual_line_count_after": candidate.recommendation_ko.count("\n") + 1,
                    "real_game_qa_required_before_release": True,
                },
            }
        )

    excluded_id = 4504
    expected_current = "응?\n이것은?"
    if tables["current_pc_ko"].texts[excluded_id] != expected_current:
        raise TriageError("intentional-question current Korean differs at 4504")
    english = tables["pc_en"].texts[excluded_id]
    traditional = tables["pc_tc"].texts[excluded_id]
    if "?" not in english or "？" not in traditional:
        raise TriageError("intentional-question corroboration differs at 4504")

    report = {
        "schema": "nobu16.kr.pk-msgev-okehazama-priority-triage.v1",
        "resource": "MSG_PK/JP/msgev.bin",
        "reviewed_id_range": [4494, 4510],
        "candidate_count": len(rows),
        "candidates": rows,
        "explicitly_excluded": [
            {
                "id": excluded_id,
                "current_korean": expected_current,
                "reason": "EN and TC retain intentional question marks; not a broken-glyph or translation candidate.",
                "pc_en": english,
                "pc_tc": traditional,
            }
        ],
        "source_policy": {
            "platform": "Steam PC",
            "allowed": ["PC Japanese", "PC English", "PC Simplified Chinese", "PC Traditional Chinese", "current PC Korean"],
            "switch_korean_translation_used": False,
            "steam_game_resource_written": False,
        },
    }
    validation = {
        "candidate_ids": [row["id"] for row in rows],
        "candidate_coordinate_sha256": sha256_bytes(
            "".join(f"{row['id']}\n" for row in rows).encode("ascii")
        ),
        "source_file_sha256": hashes,
        "explicitly_excluded_ids": [excluded_id],
        "range_fully_read": True,
        "switch_korean_translation_used": False,
        "steam_game_resource_written": False,
    }
    return report, validation


def write_outputs(rows: Iterable[dict[str, Any]], validation: dict[str, Any], event_report: dict[str, Any]) -> None:
    atomic_write(RESULT, canonical_json(list(rows)))
    atomic_write(EVENT_RESULT, canonical_json(event_report))
    atomic_write(VALIDATION, canonical_json(validation))


def validate_outputs(rows: list[dict[str, Any]], validation: dict[str, Any], event_report: dict[str, Any]) -> None:
    if not RESULT.is_file() or not EVENT_RESULT.is_file() or not VALIDATION.is_file():
        raise TriageError("triage result, event result, or validation is absent")
    if RESULT.read_bytes() != canonical_json(rows):
        raise TriageError("triage result differs from regenerated PC-only audit")
    if EVENT_RESULT.read_bytes() != canonical_json(event_report):
        raise TriageError("event priority result differs from regenerated PC-only audit")
    if VALIDATION.read_bytes() != canonical_json(validation):
        raise TriageError("validation differs from regenerated PC-only audit")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write workstream-only audit artifacts")
    parser.add_argument("--validate", action="store_true", help="compare committed artifacts with regenerated audit")
    args = parser.parse_args(argv)
    try:
        rows, validation = candidate_rows()
        event_report, event_validation = event_priority_report()
        validation["pk_msgev_okehazama_4494_4510_priority"] = event_validation
        if args.write:
            write_outputs(rows, validation, event_report)
        if args.validate:
            validate_outputs(rows, validation, event_report)
    except (OSError, ValueError, TriageError, WAVE4.QualityError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    print(
        json.dumps(
            {
                "status": "PASS",
                "candidate_count": len(rows),
                "event_priority_candidate_count": event_report["candidate_count"],
                "steam_game_resource_written": False,
                "switch_korean_translation_used": False,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
