#!/usr/bin/env python3
"""Build the source-free Korean msgbre biography batch 1 (IDs 0-128)."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_DIR = SCRIPT_PATH.parent
WORKSPACE_ROOT = SCRIPT_PATH.parents[3]
TOOLS_DIR = SCRIPT_PATH.parents[2] / "tools"
sys.path.insert(0, str(TOOLS_DIR))

import build_common_message_overlay as common  # noqa: E402
from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


BATCH_ID = "msgbre_biographies_0000_0128.v0.1"
OVERLAY_NAME = "msgbre_ko_biographies_0000_0128.v0.1.json"
EVIDENCE_NAME = "alignment_evidence.v0.1.json"
REVIEW_NAME = "review_index.v0.1.json"
VALIDATION_NAME = "validation.v0.1.json"
STRING_COUNT = 3_000
SCOPE_START = 0
SCOPE_END = 128
NEXT_START_ID = 129

SOURCE_PINS: dict[str, dict[str, Any]] = {
    "SC": {
        "logical_path": "MSG_PK/SC/msgbre.bin",
        "size": 226_918,
        "packed_sha256": "AD1FEC313228AADB00581C25AE59D8C6AFF54DD771A4D0F7BC35CD1B44D77B8D",
        "raw_size": 291_256,
        "raw_sha256": "E0343DCDB1BE7C62E515DE52B9045DC54A4D8FE77BF9B6F0836A3478CBD77779",
    },
    "JP": {
        "logical_path": "MSG_PK/JP/msgbre.bin",
        "size": 221_127,
        "packed_sha256": "DA9BE8242CF0A90592D573DF676ECDE26566B11C5707273EEB4AF5BA54132AD5",
        "raw_size": 333_516,
        "raw_sha256": "02237F07362E0E3DFF92C0E999A29B887EBE5971B1C3EF8F26EAA5C969FB9668",
    },
    "EN": {
        "logical_path": "MSG_PK/EN/msgbre.bin",
        "size": 295_601,
        "packed_sha256": "6A3F7415187F8D7E4442972C7F6AAA4C3D2C2CD5EE4584B72D130295FEDCBA47",
        "raw_size": 836_320,
        "raw_sha256": "8445078E7691461D791364208A4286A00D73F0FE4DF73569D376FE9E05986F64",
    },
}

TRANSLATIONS: dict[int, str] = {
    0: "검술가. 본명은 히사타다. 휴가 우도의 바위굴에서 수행하던 중 오의를 깨쳐 ‘가게류’를 창시했다고 한다. 아들 무네미치는 검성 가미이즈미 노부쓰나의 스승이다.",
    1: "검술가. 호는 겐코사이. 가게류 창시자 이코사이의 아들이다. 사루토비카게류를 깨치고 엔비노타치를 고안했다. 사타케 요시시게와 검성 가미이즈미 노부쓰나를 제자로 두었다.",
    2: "오우치 가신. 부교를 맡았다. 스기 시게노리와 대립했다가 훗날 화해했다. 사가라 다케토를 스에 하루카타에게 참소해 하루카타가 모반하는 계기를 만들었다. 모리 가문과 싸우다 전사했다.",
    3: "도요토미 가신. 시즈가타케 전투 등에 종군해 공을 세우고 에치젠 기타노쇼 20만 석을 받았다. 세키가하라 전투에서는 서군에 속했으나 병상에 있었고 전후 곧 병사해 영지만 몰수되었다.",
    4: "처음에는 이마가와, 다음에는 도쿠가와를 섬겨 아네가와 전투에서 활약했다. 뒤에 출분해 니와 나가히데와 도요토미 히데요시·히데요리를 섬기고 나나테구미 조장이 되었다. 오사카 전투 뒤 도쿠가와로 돌아왔다.",
    5: "소마 가신. 시나노라 칭했다. 구로키성의 성주 대리를 맡았다. 뒤에 나카무라성 성주 대리 나카무라 시키부와 공모해 모반하고 다나카성을 공격하려 했으나 소마 모리타네·요시타네 군에 패해 전사했다.",
    6: "도쿠가와 가신. 도이 도시카쓰 등과 함께 도쿠가와 이에미쓰의 후견인이 되었다. 이에미쓰의 노여움을 사 영지를 잃은 뒤 출사 요청을 거절하고 은거했다. 아들 무네토시는 이에미쓰의 아들 이에쓰나의 후견인이 되었다.",
    7: "도쿠가와 가신. 도쿠가와 히데타다의 후견인을 맡았다. 세키가하라 전투 뒤 나이토 기요나리 등과 함께 에도 부교와 간토 총부교를 지냈다. 그러나 훗날 주군 이에야스의 노여움을 사 칩거했다.",
    8: "단바의 호족. 나오마사의 형이다. 호소카와 가문의 내분에서 하루모토를 지지해 하루쿠니를 돕던 하타노 가문의 공격을 받고 하리마로 달아났다. 뒤에 하루모토 정권이 안정되자 옛 영지로 돌아왔다.",
    9: "단바의 호족. 에치젠노카미라 칭했다. 단바 슈고다이 나이토 가문에 영지를 빼앗겨 한때 하리마로 피신했으나 뒤에 돌아왔다. 둘째 아들 나오마사는 아카이 가문의 방계인 오기노 가문을 이었다.",
    10: "단바의 호족. 도키이에의 둘째 아들이다. 형 이에키요가 전사한 뒤 어린 조카 다다이에를 보좌했다. 아케치 미쓰히데의 단바 평정군을 격퇴하는 등 무용이 뛰어나 ‘단바의 붉은 귀신’이라 불렸다.",
    11: "사가라 가신. 사쓰마 국경의 오구치성을 지켰다. 무예에 뛰어난 가신을 많이 거느려 시마즈 가문의 공세를 여러 차례 물리쳤고, 시마즈 요시히로를 궁지에 몰아 가와카미 히사아키를 죽였다.",
    12: "아자이 가신. 가이호 쓰나치카·아메노모리 야헤에와 함께 ‘가이·아카오·아메노모리 삼장’이라 불렸다. 주군의 거성 오다니성에 아카오 구루와를 두고 지켰다. 주가가 멸망할 때 포로가 되어 참수되었다.",
    13: "유리 12두의 한 사람. 센보쿠 오마가리성주 마에다 미치노부가 침공하자 맞아 싸워 물리쳤다. 그러나 몇 년 뒤 미치노부의 둘째 아들 도시무네가 벌인 복수전에서 패해 전사했다고 한다.",
    14: "유리 12두의 한 사람. 유리군을 침공한 다이호지 요시우지가 아카오쓰 영지에 다가오자 안도 지카스에에게 구원을 청했다. 안도 가문의 원군을 얻은 미쓰마사는 아라사와 전투에서 다이호지군을 괴멸시켰다.",
    15: "모리 가신. 주군 다카모토의 신임을 받아 오봉행 제도가 세워진 뒤 수석 봉행이 되었다. 다카모토가 이즈모 원정 도중 급사하자 그 책임을 추궁받아 살해되었다.",
    16: "도요토미 가신. 세키가하라 전투에서 서군에 속했으나 구쓰키 모토쓰나 등과 함께 동군으로 돌아섰다. 전후 영지를 잃어 가가 마에다 가문을 섬겼으며, 물이 불어난 엣추 다이몬강에서 익사했다.",
    17: "우라가미 가신. 사카네성주. 묘젠지 전투 등에 종군했다. 우키타 나오이에가 주가의 거성 덴진야마성을 공격할 때 나오이에와 내통해 주가 멸망의 원인을 만들었다. 이후 나오이에를 섬겼다.",
    18: "우키타 가신. 가게치카의 아들. 주가의 내분 뒤 국정을 맡았다. 세키가하라 전투에서는 우키타군의 선봉을 맡았다. 뒤에 오사카성에 들어가 오사카 전투에서 기리시탄 무사들을 이끌고 분전했다.",
    19: "아카마쓰 가신. 에다요시성주. 이름은 마사카제라고도 한다. 구로다 요시타카의 외조부다. 무코가와라 전투에서 우라가미 무라무네를 격파했다. 레이제이파 시가에 정통해 간파쿠 고노에 다네이에에게 와카를 가르쳤다.",
    20: "아마고 가신. 이즈모 세토야마성주. 아들 미쓰키요와 함께 오우치 요시타카의 이즈모 침공군에 맞섰으나 미쓰키요가 전사하자 항복했다. 오우치군이 철수한 뒤 거성을 되찾는 데 성공했다.",
    21: "아마고 가신. 세토야마성주. 히사키요의 적장자다. 오우치 요시타카의 이즈모 침공군에 맞서 모리 가신 구마가이 나오쓰구를 죽이는 등 활약했으나 스에 하루카타의 가신이 쏜 화살에 목을 맞아 전사했다.",
    22: "아마고 가신. 세토야마성주. 미쓰키요의 셋째 아들이다. 아버지의 장렬한 죽음에 감동한 주군 하루히사가 영지를 늘려 주었다. 뒤에 모리 모토나리의 이즈모 침공군에 항복해 모리 가문을 섬겼다.",
    23: "기쿠치 가신. 주군 요시타케가 히고 구마모토성을 되찾을 때 오토모 편에 서서, 공으로 히고 와이후성주가 되어 기쿠치군을 다스렸다. 뒤에 구마베 지카나가와 대립해 싸웠으나 패했다.",
    24: "류조지 가신. 히고 와이후성주. 지카이에의 아들이다. 주군 다카노부가 거취를 의심해 인질을 죽이자 시마즈 가문에 속했다. 도요토미 히데요시의 규슈 정벌 뒤에도 거성을 되찾지 못했다.",
    25: "가토 기요마사 가신. 무네이에의 아들. 딸은 가토 기요마사의 측실이었다. 가토 16장의 한 사람이다. 뒤에 기요마사의 주선으로 도요토미 히데요리를 섬겨 오사카 전투에서 분전했고, 덴노지구치 전투에서 전사했다.",
    26: "시마바라의 난을 이끈 아마쿠사 17인의 한 사람. 지카타케의 아들이다. 오사카 전투 때 아버지와 함께 오사카성에 농성했다가 탈출했다. 시마바라의 난에서는 하라성 혼마루 근처를 지키다 일대일 승부 끝에 전사했다.",
    27: "하루마사의 아들. 오다 노부나가와 내통했으나 우라가미 마사무네와 싸워 패하고 몰락했다. 아카마쓰 가문은 무라카미 겐지의 흐름을 이으며, 겐무 신정 수립에 공헌한 아카마쓰 노리무라 엔신을 시조로 한다.",
    28: "도요토미 가신. 아카마쓰 마사히데의 아들. 후지와라 세이카에게 한학을 배웠다. 세키가하라 전투에서 서군에서 동군으로 돌아섰으나 이나바 돗토리성 아랫마을을 불태운 탓에 도쿠가와 이에야스의 명으로 자결했다.",
    29: "아카마쓰 가신. 다쓰노성주. 주군 하루마사를 거성에 맞아들였다. 우라가미 마사무네를 죽이고 벳쇼 야스하루와 연합해 고데라 마사모토·구로다 모토타카 등과 싸웠다. 뒤에 독살되었다고 한다.",
    30: "하리마 슈고. 가신 우라가미 무라무네의 꼭두각시가 되었다. 뒤에 호소카와 하루모토와 내통해 다이모쓰쿠즈레 전투에서 무라무네를 죽였으나 아마고 하루히사의 공격을 받는 등 영국 통치는 명목뿐이었다.",
    31: "도요토미 가신. 노리후사의 아들. 아버지가 죽은 뒤 아와 스미요시 1만 석을 이었다. 세키가하라 전투에서는 서군에 속해 오미 사와야마성에 농성했다. 함락 직전 탈출했으나 전후 교토에서 자결했다.",
    32: "도요토미 가신. 요시스케의 아들. 히데요시의 하리마 평정군에 항복해 하리마 오시오 1만 석을 인정받았다. 시즈가타케·고마키 나가쿠테 전투와 시코쿠 정벌에 종군해 아와 스미요시 1만 석을 더 받았다.",
    33: "아카마쓰 가신. 마사노리의 서자라고 한다. 마사노리의 사위가 된 요시무라가 아카마쓰 가문을 이었기에 시오야성주 우노 마사히데의 양자가 되었다. 마사히데가 다쓰노성을 쌓은 뒤 그 성주가 되었다.",
    34: "도사의 호족. 야마시로노카미라 칭했다. 아키성주. 적자가 없는 채 일찍 죽어 아들 구니토라가 가독을 이었다. 아키 가문은 진신의 난 때 도사로 유배된 소가노 아카오에의 후예라고 한다.",
    35: "도사의 호족. 아키성주. 조소카베 모토치카가 거성 도사 오코성으로 초청했으나 거절하고 맞서 싸웠다. 그러나 모토치카의 계략으로 가신단이 내부에서 무너져 패한 뒤 자결했다.",
    36: "사네스에의 맏아들. 아버지가 주군의 노여움을 사 칩거 처분을 받자 뒤를 이어 히타치 시시도번 제2대 번주가 되었다. 성품이 성실해 막부에 힘껏 봉사했고, 그 결과 영지가 늘어 무쓰 미하루로 옮겼다.",
    37: "지쿠젠의 호족. 아키즈키 다네자네의 둘째 아들. 도요토미 히데요시에게 항복해 휴가 노베오카 5만 석을 받았다. 세키가하라 전투에서 동군으로 돌아서 영지를 지켰으나 뒤에 모반인의 친족을 숨긴 죄로 영지를 몰수당했다.",
    38: "지쿠젠의 호족. 고쇼산성주. 후미타네의 둘째 아들. 모리 가문의 원조를 받아 오토모 가문에서 거성을 되찾았다. 도요토미 히데요시의 규슈 정벌군에 패했으나 ‘나라시바’ 차이레를 바쳐 영지 몰수를 면했다.",
    39: "다네나가의 사위 다네사다의 적장자. 병약해 폐적된 아버지를 대신해 다네나가의 후계자가 되었다. 다네나가가 죽은 뒤 휴가 다카나베 3만 석의 제2대 번주가 되었다.",
    40: "아키즈키 가신. 우마가타케성주. 아키즈키 후미타네의 아들. 부젠의 호족 나가노 가문을 이었다. 형 아키즈키 다네자네와 함께 오토모 가문과 싸웠다. 나가노 가문은 다이라노 기요모리의 사촌 야스모리를 시조로 한다.",
    41: "지쿠젠의 호족. 고쇼산성주. 다네자네의 맏아들. 도요토미 히데요시의 규슈 정벌군에 항복해 휴가 다카나베 3만 석으로 전봉되었다. 세키가하라 전투에서는 동군으로 돌아서 전후 영지를 인정받았다.",
    42: "지쿠젠의 호족. 고쇼산성주. 오토모 가문에 속했으나 처우에 불만을 품고 모리 모토나리와 손잡아 반기를 들었다. 오토모군 2만 명을 상대로 선전했지만 수적 열세를 이기지 못하고 패해 자결했다.",
    43: "후카야 우에스기 가신. 오다와라 정벌에서 도요토미 대군을 상대로 후카야성을 끝까지 지켰다. 뒤에 도쿠가와 이에야스를 섬겼다. 세키가하라 전투 뒤 우에스기 가게카쓰에게 항복을 권해 받아들이게 했다.",
    44: "다케다 가신. 이나슈를 통솔했다. 도쿠가와 이에야스가 ‘다케다군의 성난 황소’라 평할 만큼 용맹한 장수였다. 이와무라성에 농성해 오다 노부나가군과 싸웠으나 패해 포로가 된 뒤 책형을 당했다.",
    45: "사이토 가신이자 아케치 미쓰히데의 숙부. 도산과 요시타쓰의 내전 때 도산 편에 서서 요시타쓰군의 거성 아케치성 공격을 받았다. 농성하며 맞섰으나 패해 자결했다.",
    46: "미노의 호족. 아케치성주. 딸은 사이토 도산에게 시집가 오다 노부나가의 정실 기초를 낳았다. 아케치 가문은 도키 가문의 방계로, 초대 미노 슈고 도키 요리사다의 아들 요리모토를 시조로 한다고 한다.",
    47: "오다 가신. 뛰어난 재주와 교양으로 중용되었으나 돌연 모반을 일으켜 혼노지에서 노부나가를 죽였다. 하지만 사후 공작에 실패해 야마자키 전투에서 패하고 도주 중 목숨을 잃었다.",
    48: "아케치 가신. 장인 미쓰히데를 따라 혼노지의 변에 가담했다. 야마자키 전투에서는 아즈치성을 지켰으나 본군의 패전 소식을 듣고 사카모토성으로 물러났다. 보물을 포위군에 넘긴 뒤 자결했다.",
    49: "오미의 센고쿠 다이묘. 오다니성주. 스케마사의 아들. 롯카쿠 가문의 산하로 들어가는 정책을 택해 가신들의 불만을 샀고, 뒤에 아들 나가마사에게 가독을 넘겼다. 아자이 가문이 멸망할 때 자결했다.",
    50: "오미의 센고쿠 다이묘. 오다니성주. 히사마사의 아들. 오다 노부나가의 누이 이치를 아내로 맞았으나 아사쿠라 가문과의 우의를 중시해 노부나가와 적대했다. 거성이 공격받자 이치와 딸들을 노부나가에게 맡기고 자결했다.",
    51: "아자이 가문의 방계. 종가 당주 나가마사가 오다 노부나가와의 동맹을 깨려 하자 강경하게 반대했다. 뒤에 오다니성 전투에서 오다군에 패해 포로가 되었고 처형당했다.",
    52: "오미의 센고쿠 다이묘. 오다니성주. 처음에는 교고쿠 가문을 섬겼으나 주가의 내분을 틈타 세력을 넓혔다. 아사쿠라 가문의 지원을 받아 롯카쿠 사다요리군을 격퇴하고 고호쿠의 패자가 되었다.",
    53: "오토모 가신. 시마즈군이 분고를 침공해 다이바루성을 공격하자 성에 ‘빈집의 화승’ 장치를 걸고 철수했다. 불타는 성에 들어온 시마즈군을 기습해 큰 피해를 입혔다.",
    54: "아사쿠라 가문 제5대 당주. 다카카게의 적장자. 쇼군 아시카가 요시아키와 손잡아 오다 노부나가 포위망의 한 축을 맡았으나 점차 세력을 잃었다. 도네자카 전투에서 패한 뒤 일족의 배신을 받고 자결했다.",
    55: "아사쿠라 가신. 아사쿠라 가문 제3대 당주 사다카게의 아들. 아사쿠라 소테키의 양자가 되었다. 쓰루가성주를 맡아 양부와 함께 가가·와카사·긴키 각지를 전전하며 활약했고, 뒤에 쓰루가 군지가 되었다.",
    56: "아사쿠라 가신. 가게타카의 아들. 오다 노부나가 추격군의 총대장을 맡았다. 주군 요시카게가 도네자카 전투에서 패한 뒤 노부나가와 내통해 요시카게를 자결시켰다. 훗날 잇코잇키 세력에게 죽었다.",
    57: "아사쿠라 가신. 가게타카의 아들. 아네가와 전투에서 아사쿠라군 총대장으로 분전했다. 주가 멸망 뒤 오다 노부나가에게 속했으나 잇코잇키에 항복해 노부나가의 노여움을 사고 자결을 명받았다.",
    58: "아사쿠라 가신. 사다카게의 둘째 아들. 형 다카카게와 대립해 군지직에서 파면되었다. 혼간지 가문과 손잡고 다카카게 타도를 내걸었으나 이루지 못하고 서국으로 달아났다. 풍류를 즐긴 인물이었다고 한다.",
    59: "아사쿠라 가신. 아사쿠라 도시카게의 동생 쓰네카게의 손자. 아사쿠라 소테키가 병으로 귀국한 뒤 잇코잇키 토벌군의 대장이 되어 가가에 출진했다. 뒤에 세 아들을 잇달아 잃고 얼마 지나지 않아 죽었다.",
    60: "아사쿠라 가신. 아사쿠라 소테키의 가가 잇코잇키 공격에서 전공을 세웠다. 네 봉행 중 한 사람으로 내정에서 수완을 발휘했다. 요시카게가 이누오모노를 열었을 때 호화로운 차림으로 모두를 놀라게 했다.",
    61: "아사쿠라 가문 제4대 당주. 뛰어난 정치 수완으로 에치젠을 안정시키고 아사쿠라 가문의 전성기를 열었다. 이웃 가가를 적극적으로 침공해 잇코잇키군과 싸웠다. 가도에도 뛰어났다.",
    62: "아사쿠라 가신. 아사쿠라 가문 초대 당주 도시카게의 아들. 군부교를 맡아 주변 여러 구니에 출병하며 아사쿠라 가문의 무위를 널리 알렸다. 가가 잇코잇키 토벌 중 병을 얻어 귀국한 뒤 죽었다.",
    63: "도요토미 가신. 나가마사의 적장자. 세키가하라 전투에서 동군에 속했고, 전후 기이 와카야마 37만 석을 받았다. 뒤에 가토 기요마사와 협력해 도쿠가와 이에야스와 도요토미 히데요리의 회견을 성사시켰다.",
    64: "나가마사의 셋째 아들. 도쿠가와 히데타다를 섬겨 오사카 전투에서 공을 세웠다. 뒤에 영지가 늘어 히타치 가사마 5만 3천 석으로 전봉되었다. 마쓰노오로카에서 기라 고즈케노스케를 벤 아사노 다쿠미노카미는 나가시게의 증손이다.",
    65: "도요토미 가신. 히데요시의 정실 네네의 의동생. 오봉행의 수석으로 주가의 정무에 참여했다. 히데요시가 죽은 뒤 이시다 미쓰나리와 대립해 도쿠가와 이에야스에게 접근했고, 이후 도쿠가와 가문을 섬겼다.",
    66: "도쿠가와 가신. 나가마사의 둘째 아들. 형 요시나가가 죽은 뒤 기이 와카야마 번주가 되었다. 오사카 여름 전투에서 하나와 나오유키를 죽이는 등 활약했다. 후쿠시마 가문이 영지를 잃은 뒤 아키 히로시마 42만 석을 받았다.",
    67: "이마가와 가신. 아즈키자카 전투 등에서 공을 세웠다. 주가 멸망 뒤 다케다 신겐을 섬겨 스루가 선방중이 되었다. 다케다 가문이 멸망할 때 거성 이하라관이 공격받아 패한 뒤 자결했다.",
    68: "이마가와 가신. 야스요시의 아들. 스루가에서 쫓겨난 주군 우지자네를 거성 가케가와성에 맞아들여 도쿠가와군과 싸웠다. 5개월 농성 끝에 성을 열고 우지자네와 함께 사가미로 달아났다.",
    69: "이마가와 가신. 가케가와성주를 맡았다. 1548년 아즈키자카 전투에서 다이겐 셋사이를 보좌해 오다 노부히데군을 격파하는 등 이마가와 가문의 서방 침공군 선봉으로 활약했다.",
    70: "데와의 호족. 노리요리의 둘째 아들. 안도 가문과 손잡아 형 노리스케를 자결시키고 당주가 되었다. 뒤에 쓰가루 가문과 결탁해 모반을 꾀하다 안도 지카스에가 마련한 연회에 유인되어 살해되었다.",
    71: "데와의 호족. 돗코성주. 노리요리의 적장자. 안도 가문에 종속되려 한 동생 가쓰요리와 대립했다. 뒤에 가쓰요리의 안내를 받은 안도군의 공격을 받고 자결했다.",
    72: "데와의 호족. 도모요리의 아들. 가이국 아사리향에서 데와 히나이 지방으로 옮겨 돗코성을 쌓았다. 또 동생들을 주변 성에 배치해 히나이에 대한 지배권을 확립했다.",
    73: "아사리 가신. 노리요리의 동생. 하나오카성주. 노리요리·노리스케·가쓰요리를 섬겨 북쪽 수비를 맡았다. 가쓰요리가 안도 가문에서 독립하려 할 때 안도 지카스에와 야마다 전투에서 싸우다 패사했다.",
    74: "데와의 호족. 가쓰요리의 아들. 아버지가 모살된 뒤 쓰가루에 몸을 숨겼다. 훗날 안도 가문의 대관으로 히나이를 다스렸으나 군역금을 내지 않은 문제가 생겨 소송 중 오사카에서 급사했다.",
    75: "무로마치 막부 제13대 쇼군. 쓰카하라 보쿠덴과 가미이즈미 노부쓰나 등에게 배운 검호다. 잃어버린 막부 권력을 되찾으려 힘썼으나 훗날 마쓰나가 히사미치 등의 기습을 받아 홀로 분전한 끝에 자결했다.",
    76: "고가 구보. 하루우지의 아들. 호조 가문의 보호 아래 성장해 고가성으로 돌아왔으나 실권은 없었다. 죽은 뒤 고가 아시카가 가문이 끊기자 딸 우지히메가 기쓰레가와 가문을 세웠다.",
    77: "무로마치 막부 제15대 쇼군. 오다 노부나가의 후원으로 쇼군직에 올랐으나 뒤에 대립해 주변 여러 구니와 노부나가 포위망을 폈다. 직접 거병했지만 노부나가군에 패해 교토에서 쫓겨났다.",
    78: "무로마치 막부 제12대 쇼군. 아와에서 거병한 미요시 모토나가에게 패해 오미로 달아났다. 모토나가가 죽은 뒤 호소카와 하루모토의 옹립으로 교토에 돌아왔으나 훗날 하루모토와 대립해 쇼군직을 사임했다.",
    79: "오유미 고쇼. 고가 구보 마사우지의 아들. 아버지 등과 대립해 떠돌다가 마리야쓰 다케다 가문의 후원을 얻어 오유미성에 들어갔다. 뒤에 사토미 가문과 연합해 고노다이에서 호조 가문과 싸웠으나 패사했다.",
    80: "고가 구보. 다카모토의 아들. 아시카가 일문으로서 간토 무사들의 굳건한 지지를 받아 호조 가문도 회유에 신경을 썼다. 뒤에 호조 가문에 반항해 오다와라에 유폐되었다.",
    81: "간토 간레이. 고가 구보 다카모토의 아들. 우에스기 노리후사의 양자가 되어 우에스기 노리히로라 칭했다. 간토 교로쿠 내란에서 패해 간토 간레이직을 잃고 아시카가 성씨로 돌아갔다.",
    82: "오유미 구보 요시아키의 손자. 요리즈미의 아들. 형이 죽은 뒤 형의 정실 아시카가 우지히메, 곧 고가 구보 아시카가 요시우지의 딸과 혼인해 형이 남긴 영지를 이었다. 뒤에 기쓰레가와번 초대 번주가 되었다.",
    83: "시모쓰케 기쓰레가와성주. 오유미 고쇼 요시아키의 아들. 아버지가 제1차 고노다이 전투에서 전사해 각지를 떠돌았다. 뒤에 도요토미 히데요시를 섬겼다. 딸 시마코는 도요토미 히데요시의 측실이 되었다.",
    84: "단바의 호족. 히카미군 고무로성주. 다른 호족들과 함께 오다 노부나가의 단바 침공군에 맞섰다. 1579년 5월 하시바 히데나가군의 공격으로 성이 함락되어 멸망했다.",
    85: "다케다 가신. 미타케성주. 시모쓰케노카미라 칭했다. 미카타가하라 전투 뒤 후타마타성주가 되었다. 주가가 나가시노 전투에서 대패한 뒤 도쿠가와 이에야스군에 거성을 포위당했고, 수비 중 병사했다.",
    86: "다케다 가신. 노부모리의 아들. 후타마타성주를 맡아 아버지와 함께 도쿠가와군과 싸웠다. 주가 멸망 뒤 도쿠가와 가문을 섬겨 시나노 공략에 참가했으나 이와오성 공격전에서 총탄을 맞고 전사했다.",
    87: "모리키요의 서자. 생모가 시라뵤시였기 때문인지 가독 계승 후보에서 제외되어 가신 도미타 요시자네의 손에서 자랐다. 뒤에 요시자네의 옹립으로 모반을 일으켰으나 패해 자결했다.",
    88: "아시나 가문 제17대 당주. 모리우지의 적장자. 아버지가 은거하자 가독을 이었으나 사타케 가문과 항쟁하던 중 요절했다. 모리오키의 병을 고치려고 아버지가 영내의 술 제조를 금한 적도 있다.",
    89: "아시나 가문 제16대 당주. 아시나 가문을 다테 가문과 나란히 오슈 굴지의 다이묘로 키운 중흥의 시조다. 동맹을 능숙하게 이용해 아이즈 전역에서 북부 에치고에 이르는 영지를 얻었다.",
    90: "아시나 가문 제15대 당주. 이나와시로 가문의 반란을 진압하고 다테 다네무네의 가사이 가문 공격을 도왔으며 이와키·시라카와 유키 가문과 싸우는 등 사실상 아이즈 슈고로 행동했다.",
    91: "히고의 호족. 이와오성주. 고레타네의 아들. 겨우 3세에 아소 대궁사가 되었다. 도요토미 히데요시에게 항복해 삿사 나리마사를 섬겼으나 히고 고쿠진 봉기를 선동했다는 참소로 살해되었다.",
    92: "히고의 호족. 이와오성주. 고레토요의 아들. 형 고레마사에게 아들이 없어 형의 양자가 되어 가독을 잇고 아소 대궁사에 취임했다. 그러나 불과 한 달 뒤 죽었다.",
    93: "히고의 호족. 이와오성주. 고레토요의 아들. 아소 대궁사를 맡고 오토모 가문에 속했다. 가신 가이 지카나오의 도움으로 류조지·시마즈 가문과 화평 교섭을 벌여 영지를 지켰다.",
    94: "아소 대궁사. 고레노리의 맏아들. 기쿠치 가신들에게 옹립되어 기쿠치 가문을 이었으나 오토모 가문과 대립해 추방당했다. 아소 대궁사직을 두고 동생 고레토요와 싸웠지만 패해 사쓰마로 달아났다.",
    95: "히고의 호족. 이와오성주. 한때 형 고레나가에게 거성에서 쫓겨났으나 가신 가이 지카노부의 도움으로 아소 대궁사직을 되찾았다. 뒤에 황궁 수리비를 바치고 내려온 칙사를 맞았다.",
    96: "지쿠젠의 호족. 야마가성주. 아소 가문은 온가군 야마가의 지토를 지낸 우쓰노미야 이에마사를 시조로 하는 우쓰노미야 가문의 방계다. 도요토미 히데요시의 규슈 정벌군에 항복한 뒤 지쿠고로 전봉되었다.",
    97: "지쿠젠의 호족. 하나오성주. 다카모리의 동생. 사가라 다케토가 실각하자 성주가 되었다. 뒤에 야마가성주 아소 다카자네와 대립해 무나카타 우지사다의 지원을 받은 다카자네에게 패하고 시마즈 가문에 의탁했다.",
    98: "지쿠젠의 호족. 오카성주. 오우치 가문에 속했으나 같은 일족인 호바시라야마성주 아소 가문이 오토모 가문에 접근하려 해 대립했다. 뒤에 그 아소 가문의 공격으로 성이 함락되어 전사했다.",
    99: "아키의 호족. 모리 가문에 속했다. 이쓰쿠시마 전투와 보초 제압전 등에서 선봉을 맡았다. 한편 부역 부담에 항의하고 이즈모 원정을 꺼리는 등 일정한 독립성도 유지했다.",
    100: "히다의 호족. 호라성주. 나오모리의 아들. 아버지가 죽은 뒤 가독을 이었다. 다케다 가문과 우호를 맺었으나 뒤에 우에스기 가문과 손잡은 사촌 에마 데루모리와 대립해 공격받고 패한 뒤 자결했다.",
    101: "히다의 호족. 에마 도키쓰네의 둘째 아들이며 에마 도키모리의 동생이다. 아소노의 호라성을 거성으로 삼아 아소노라는 성씨를 썼다. 도키모리와 그 아들 요시모리는 훗날 조카 에마 데루모리에게 살해되었다.",
    102: "오다 가신. 후유야스의 아들. 아버지가 죽은 뒤 가독을 이어 아와지 수군을 이끌었다. 처음에는 이시야마 혼간지와 손잡았으나 오다 노부나가의 긴키 평정군에 항복했고, 기즈가와구치 전투에서 모리 수군과 싸웠다.",
    103: "미요시 가신. 미요시 모토나가의 셋째 아들. 아타기 가문을 이어 아와지 수군을 통솔했다. 형 미요시 나가요시를 도와 활약했으나 마쓰나가 히사히데의 참소로 형에게 살해되었다. 시가·서예·다도에 뛰어났다.",
    104: "단바의 호족. 히카미군 야마가키성주. 아다치 가문은 미나모토 가문 4대를 섬겼고 무사시국 아다치군을 다스린 후지와라 도모토를 시조로 한다. 1579년 하시바 히데나가군의 공격으로 성이 함락되어 전사했다.",
    105: "가토 가신. 세키가하라 전투 때 주군 요시아키의 거성 이요 마사키성에서 유수를 맡아 모리군을 격퇴했고 가로가 되었다. 하천 공사에 뛰어나 영내의 관개와 수방 사업을 시행했다.",
    106: "아자이 가신. 야마모토야마성주. 주가 멸망 뒤 오다 노부나가에게 속해 에치젠 공격에 종군했다. 혼노지의 변 뒤 아케치 미쓰히데에게 속했고, 미쓰히데가 죽은 뒤 아들 사다히로와 함께 살해되었다.",
    107: "마쓰마에번 무사. 히이시관주 아쓰야 시게마사의 후예. 마쓰마에성에 불이 나 화약고가 폭발했을 때 사카이 히로타네와 함께 뛰어들어 번주 기미히로를 구했으나 자신은 중상을 입고 죽었다.",
    108: "다케다 가신. 아토베 가문은 시나노 사쿠군 출신으로 가이 슈고다이도 지낸 명문이다. 하라 마사타네와 함께 주군 가쓰요리의 측근을 맡았다. 다케다 가문 멸망 때 스와에서 전사했으며 간신이라는 평가를 받았다.",
    109: "아시나 가신. 다테 가문의 거듭된 침공을 계속 물리쳐 ‘북쪽의 문지기’라 두려움을 샀다. 다테 마사무네의 계략으로 내응한 일족의 기습을 받아 자결했다.",
    110: "다케다 가신. 일문중의 우두머리 격이다. 전투에서는 주로 본진을 지켰다. 다케다 가문 멸망 뒤 도쿠가와 이에야스에게 항복했다. 혼노지의 변을 알고 사카이에서 본국으로 돌아가던 길에 정체 모를 자에게 살해되었다.",
    111: "다케다 가신. 다케다 노부토라의 둘째 딸을 정실로 맞은 일문중이다. 가이와 스루가 국경에 가까운 가와치 지방을 다스리며 주로 이마가와 가문과의 외교에서 활약했다. 노부토라 추방 뒤 하루노부를 섬겼다.",
    112: "오노데라 가신. 당주 데루미치가 주색에 빠져 간언한 가신들을 가차 없이 처벌했으나 뜻을 굽히지 않고 쓴소리를 올렸다. 결국 데루미치가 보낸 자객에게 살해되었다.",
    113: "도쿠가와 가신. 후시미성 수비대장 등을 역임했다. 오사카 전투에서는 히데타다를 따라 출진해 공을 세웠다. 뒤에 로주가 되어 막정에서 중책을 맡았다. 사임 뒤 오사카 조다이가 되었고 그곳에서 죽었다.",
    114: "이에야스의 조부 마쓰다이라 기요야스가 암살된 ‘모리야마쿠즈레’의 당사자. 모리야마성 공략을 위해 진을 친 동안 모반설이 돌던 아버지 사다요시가 처형된 것으로 오해해 기요야스를 베었다.",
    115: "마쓰다이라 가신. 아들 야히치로가 주군 기요야스를 잘못 죽이자 책임을 지고 자결하려 했으나 제지당했다. 기요야스의 아들 히로타다가 오카자키성으로 돌아오는 데 힘썼고, 이후 보좌역으로 활약했다.",
    116: "데와의 호족. 이데하 신사의 별당직을 맡았다. 1533년 이와이데관을 쌓아 거성으로 삼았다. 아들 사다쓰구는 모가미 가문에 속해 1588년 주고리가하라 전투에서 전사했다.",
    117: "이마가와 가신. 주가의 거성 슨푸성을 오카베 마사쓰나와 함께 지켰으나 다케다 신겐의 스루가 침공군에 패해 본관지 아베로 물러났다. 이후 도쿠가와 가문에 속해 각지에서 다케다군과 싸웠다.",
    118: "우에스기 가신. 사카타성주. 주가의 아이즈 전봉을 따라 시로이시 조다이를 맡았다. 세키가하라 전투 때 항전을 주장했다. 뒤에 거성을 비운 틈을 타 다테군이 공격해 성을 잃었다.",
    119: "우에스기 가신. 산조성주. 처음 이름은 나가시게. 제4차 가와나카지마 전투에서 후군을 맡아 사이조산을 습격한 다케다군 별동대와 싸웠다. 겐신이 죽은 뒤 가게카쓰를 섬겨 수많은 전공을 세웠다.",
    120: "히고의 기리시탄. 이름은 도키사다. 가혹한 징세에 시달리던 농민을 이끌고 막부군과 싸웠다. 봉기군은 선전했으나 군량이 끊긴 끝에 총공격을 받아 모두 전멸했다.",
    121: "이즈모의 센고쿠 다이묘. 갓산토다성주. 하루히사의 아들. 거성에 농성해 모리 모토나리의 이즈모 원정군에 맞섰으나 수석 가로 우야마 히사카네를 죽이는 등 모토나리의 이간책에 무너졌다.",
    122: "아마고 가신. 주군 하루히사, 곧 형 쓰네히사의 손자가 추진한 아키 침공에 반대해 ‘겁쟁이 야슈’라는 비난을 받았다. 결국 아마고군이 대패하자 퇴각군의 후군을 맡아 분전하다 전사했다.",
    123: "이즈모의 센고쿠 다이묘. 교고쿠 가문을 섬겼으나 영지 횡령죄로 이즈모 슈고다이에서 파면되었다. 뒤에 거성 갓산토다성을 되찾고 세력을 넓혀 주고쿠 11개 구니의 태수가 되었다.",
    124: "아마고 가신. 쓰네히사의 둘째 아들. 신구토를 이끌어 조카 하루히사를 보좌했다. 종가를 능가하는 세력을 자랑했으나 뒤에 대립했고, 지배 체제 강화를 노린 하루히사에게 숙청되었다.",
    125: "마사히사의 아들. 야마나카 유키모리 등의 옹립을 받아 아마고 가문 재흥을 꾀했다. 오다 노부나가를 의지해 이즈모 입국을 시도했으나 실패했고, 뒤에 하리마 고즈키성 전투에서 모리군에 패해 자결했다.",
    126: "아마고 가신. 엔야 오키히사의 적장자. 아버지 오키히사의 모반 뒤 용서받아 아마고 성씨로 돌아왔으나 제1차 갓산토다성 전투에서 반아마고 편에 섰기에 하루히사에게 숙청되었다.",
    127: "아마고 가신. 구니히사의 맏아들. 아버지와 함께 신구토를 이끌었다. 세력이 커지면서 종가의 하루히사와 대립했고, 지배 체제 강화를 꾀한 하루히사에게 아버지와 함께 숙청되었다.",
    128: "이즈모의 센고쿠 다이묘. 조부 쓰네히사가 죽은 뒤 가독을 이었다. 적극적인 외정으로 아마고 가문의 최대 판도를 세웠다. 취약한 지배 체제를 다지기 위해 신구토를 숙청했다.",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    0: ["school_and_person_readings_require_glossary_review"],
    1: ["school_and_technique_readings_require_glossary_review"],
    12: ["collective_epithet_rendering_requires_glossary_review"],
    23: ["waifu_castle_reading_requires_glossary_review"],
    38: ["tea_utensil_reading_requires_glossary_review"],
    53: ["rusu_no_hinawa_term_requires_context_review"],
    57: ["given_name_reading_requires_officer_catalog_crosscheck"],
    64: ["matsuno_oroka_term_requires_glossary_review"],
    82: ["given_name_reading_requires_officer_catalog_crosscheck"],
    87: ["subject_given_name_requires_officer_catalog_crosscheck"],
    97: ["given_name_reading_requires_officer_catalog_crosscheck"],
    107: ["hiishi_place_reading_requires_glossary_review"],
    116: ["idewa_shrine_reading_requires_glossary_review"],
}

CJK_UNIFIED_RE = re.compile("[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
KANA_RE = re.compile("[\u3040-\u30ff\u31f0-\u31ff]")
BRACKET_TOKEN_RE = re.compile(r"\[[a-z0-9_]+\]")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def write_json(path: Path, value: Any) -> dict[str, Any]:
    blob = encode_json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {"path": path.name, "size": len(blob), "sha256": sha256(blob)}


def selected_ids() -> list[int]:
    ids = list(range(SCOPE_START, SCOPE_END + 1))
    if ids != sorted(TRANSLATIONS) or len(ids) != 129:
        raise ValueError("batch1 translations must exactly cover IDs 0-128")
    return ids


def load_source(path: Path, language: str) -> tuple[bytes, bytes, Any]:
    pin = SOURCE_PINS[language]
    packed = path.read_bytes()
    if len(packed) != pin["size"] or sha256(packed) != pin["packed_sha256"]:
        raise ValueError(f"{language} packed msgbre source does not match its pin")
    _, raw = decompress_wrapper(packed)
    if len(raw) != pin["raw_size"] or sha256(raw) != pin["raw_sha256"]:
        raise ValueError(f"{language} raw msgbre source does not match its pin")
    table = parse_message_table(raw)
    if table.string_count != STRING_COUNT:
        raise ValueError(f"{language} msgbre has {table.string_count} entries")
    if rebuild_message_table(table, table.texts) != raw:
        raise ValueError(f"{language} msgbre parse/rebuild is not byte-identical")
    return packed, raw, table


def source_structure(text: str) -> dict[str, Any]:
    invariant = common.message_invariants(text)
    return {
        "utf16_code_units": len(text.encode("utf-16le")) // 2,
        "printf_tokens": invariant["printf"],
        "unknown_percent_count": invariant["unknown_percent_count"],
        "esc_sequences": invariant["esc"],
        "control_codepoints": invariant["controls"],
        "line_breaks": invariant["line_breaks"],
        "private_use_codepoints": invariant["pua"],
        "custom_bracket_placeholders": BRACKET_TOKEN_RE.findall(text),
        "leading_whitespace_utf16le_sha256": common.text_hash(
            invariant["leading_whitespace"]
        ),
        "trailing_whitespace_utf16le_sha256": common.text_hash(
            invariant["trailing_whitespace"]
        ),
    }


def script_counts(text: str) -> dict[str, int]:
    return {
        "cjk_unified_count": len(CJK_UNIFIED_RE.findall(text)),
        "kana_count": len(KANA_RE.findall(text)),
    }


def validate_overlay(overlay: dict[str, Any], ids: list[int]) -> None:
    """Validate the msgbre overlay locally until the shared builder adds it."""
    expected_root = {
        "schema",
        "overlay_id",
        "resource",
        "base_language",
        "entry_count",
        "distribution_policy",
        "stock_sc",
        "defaults",
        "entries",
    }
    if set(overlay) != expected_root:
        raise ValueError("msgbre overlay root keys differ")
    if overlay["schema"] != common.OVERLAY_SCHEMA:
        raise ValueError("msgbre overlay schema differs")
    if overlay["resource"] != "MSG_PK/SC/msgbre.bin":
        raise ValueError("msgbre overlay resource differs")
    if overlay["base_language"] != "SC" or overlay["entry_count"] != len(ids):
        raise ValueError("msgbre overlay scope differs")
    entries = overlay["entries"]
    if [entry["id"] for entry in entries] != ids:
        raise ValueError("msgbre overlay IDs differ")
    required_entry_keys = {"id", "source_sc_utf16le_sha256", "ko"}
    if any(set(entry) != required_entry_keys for entry in entries):
        raise ValueError("msgbre public entries must contain only ID, SC hash, and Korean")
    if any(not entry["ko"] or "\x00" in entry["ko"] for entry in entries):
        raise ValueError("msgbre Korean replacement is empty or contains NUL")
    if any(re.fullmatch(r"[0-9A-F]{64}", entry["source_sc_utf16le_sha256"]) is None for entry in entries):
        raise ValueError("msgbre SC source hash is malformed")


def build(args: argparse.Namespace) -> dict[str, Any]:
    ids = selected_ids()
    paths = {"SC": args.stock_sc, "JP": args.stock_jp, "EN": args.stock_en}
    loaded = {language: load_source(path, language) for language, path in paths.items()}
    tables = {language: value[2] for language, value in loaded.items()}

    empty_ids = [
        entry_id
        for entry_id in ids
        if any(not tables[language].texts[entry_id] for language in ("SC", "JP", "EN"))
    ]
    if empty_ids:
        raise ValueError(f"selected aligned range contains empty entries: {empty_ids}")
    if not all(tables[language].texts[NEXT_START_ID] for language in ("SC", "JP", "EN")):
        raise ValueError("next-start boundary ID 129 must be non-empty in all languages")

    overlay_entries: list[dict[str, Any]] = []
    evidence_entries: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for entry_id in ids:
        source_sc = tables["SC"].texts[entry_id]
        replacement = TRANSLATIONS[entry_id]
        problems = common.invariant_mismatches(source_sc, replacement)
        source_placeholders = BRACKET_TOKEN_RE.findall(source_sc)
        replacement_placeholders = BRACKET_TOKEN_RE.findall(replacement)
        if source_placeholders != replacement_placeholders:
            problems.append(
                "custom_bracket_placeholders: "
                f"source={source_placeholders!r}, ko={replacement_placeholders!r}"
            )
        if problems:
            failures.append({"id": entry_id, "problems": problems})
        overlay_entries.append(
            {
                "id": entry_id,
                "source_sc_utf16le_sha256": common.text_hash(source_sc),
                "ko": replacement,
            }
        )
        evidence_entries.append(
            {
                "id": entry_id,
                "references": {
                    language: {
                        "utf16le_sha256": common.text_hash(
                            tables[language].texts[entry_id]
                        ),
                        "structure": source_structure(tables[language].texts[entry_id]),
                    }
                    for language in ("SC", "JP", "EN")
                },
                "manual_semantic_crosscheck": True,
            }
        )
    if failures:
        raise ValueError(f"replacement invariants failed: {failures}")

    sc_packed, sc_raw, _ = loaded["SC"]
    overlay = {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": "MSG_PK/SC/msgbre.bin",
        "base_language": "SC",
        "entry_count": len(ids),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "size": len(sc_packed),
            "packed_sha256": sha256(sc_packed),
            "raw_size": len(sc_raw),
            "raw_sha256": sha256(sc_raw),
            "string_count": STRING_COUNT,
        },
        "defaults": {"status": "translated"},
        "entries": overlay_entries,
    }
    validate_overlay(overlay, ids)

    anchor_ids = (SCOPE_START, SCOPE_END, NEXT_START_ID)
    evidence = {
        "schema": "nobu16.kr.msgbre-alignment-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": "msgbre",
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "selected_nonempty_entry_count": len(ids),
            "next_start_id": NEXT_START_ID,
        },
        "alignment_basis": [
            "same_resource_role",
            "same_3000_entry_count",
            "same_numeric_string_ids",
            "all_selected_entries_nonempty_in_sc_jp_en",
            "manual_semantic_crosscheck_of_selected_entries",
        ],
        "source_files": {
            language: {**SOURCE_PINS[language], "string_count": STRING_COUNT}
            for language in ("SC", "JP", "EN")
        },
        "boundary_anchors": [
            {
                "id": entry_id,
                "reference_hashes": {
                    language: common.text_hash(tables[language].texts[entry_id])
                    for language in ("SC", "JP", "EN")
                },
            }
            for entry_id in anchor_ids
        ],
        "entry_count": len(ids),
        "entries": evidence_entries,
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.msgbre-review-index.v1",
        "batch_id": BATCH_ID,
        "quality_state": "draft_not_human_or_runtime_reviewed",
        "entry_count": len(ids),
        "entries": [
            {
                "id": entry_id,
                "status": "translated",
                "translation_origin": "assistant_generated_draft_from_pinned_sc_jp_en",
                "automated_draft": True,
                "human_review_required": True,
                "runtime_reviewed": False,
                "uncertainty_flags": UNCERTAINTY_FLAGS.get(entry_id, []),
            }
            for entry_id in ids
        ],
        "contains_commercial_source_text": False,
    }

    out_root = args.out_root.resolve()
    artifacts: dict[str, dict[str, Any]] = {}
    artifacts["overlay"] = write_json(out_root / "public" / OVERLAY_NAME, overlay)
    artifacts["alignment_evidence"] = write_json(
        out_root / "evidence" / EVIDENCE_NAME, evidence
    )
    artifacts["review_index"] = write_json(
        out_root / "review" / REVIEW_NAME, review
    )

    public_paths = {
        "overlay": out_root / "public" / OVERLAY_NAME,
        "alignment_evidence": out_root / "evidence" / EVIDENCE_NAME,
        "review_index": out_root / "review" / REVIEW_NAME,
    }
    source_free_scan = {
        name: script_counts(path.read_text(encoding="utf-8"))
        for name, path in public_paths.items()
    }
    if any(
        counts != {"cjk_unified_count": 0, "kana_count": 0}
        for counts in source_free_scan.values()
    ):
        raise ValueError("public artifact contains source-script text")

    validation = {
        "schema": "nobu16.kr.msgbre-generation-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "selected_nonempty_entry_count": len(ids),
            "next_start_id": NEXT_START_ID,
            "selected_ids_sha256": sha256(
                json.dumps(ids, separators=(",", ":")).encode("utf-8")
            ),
        },
        "source_alignment": {
            "languages": ["SC", "JP", "EN"],
            "string_count_each": STRING_COUNT,
            "selected_reference_hash_count": len(ids) * 3,
            "manual_semantic_crosschecks": len(ids),
            "selected_nonempty_in_all_languages": len(ids),
        },
        "replacement_invariants": {
            "checked": len(ids),
            "failures": 0,
            "custom_bracket_placeholder_checks": len(ids),
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "leading_whitespace",
                "trailing_whitespace",
                "esc_sequences_in_order",
                "control_characters",
                "line_break_sequence",
                "private_use_codepoints",
                "custom_bracket_placeholders_in_order",
            ],
        },
        "translation_status": {
            "translated_draft": len(ids),
            "human_review_required": len(ids),
            "runtime_reviewed": 0,
            "specific_uncertainty_entries": len(UNCERTAINTY_FLAGS),
        },
        "source_free_scan": source_free_scan,
        "artifacts": artifacts,
        "generator": {
            "path": SCRIPT_PATH.name,
            "sha256": sha256(SCRIPT_PATH.read_bytes()),
        },
        "reproducibility": {
            "required_runs": ["isolated_a", "isolated_b", "final"],
            "byte_identical_artifacts_required": True,
        },
        "safety": {
            "installed_game_files_modified": False,
            "font_files_modified": False,
            "installer_modified": False,
            "root_readme_modified": False,
            "other_workstreams_modified": False,
        },
    }
    artifacts["generation_validation"] = write_json(
        out_root / VALIDATION_NAME, validation
    )
    return {"out_root": out_root, "entry_count": len(ids), "artifacts": artifacts}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stock-sc", type=Path, default=WORKSPACE_ROOT / "MSG_PK" / "SC" / "msgbre.bin"
    )
    parser.add_argument(
        "--stock-jp", type=Path, default=WORKSPACE_ROOT / "MSG_PK" / "JP" / "msgbre.bin"
    )
    parser.add_argument(
        "--stock-en", type=Path, default=WORKSPACE_ROOT / "MSG_PK" / "EN" / "msgbre.bin"
    )
    parser.add_argument("--out-root", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    try:
        result = build(parse_args())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={result['out_root']}")
    print(f"entries={result['entry_count']}")
    for name, artifact in result["artifacts"].items():
        print(f"{name}_sha256={artifact['sha256']}")
    print(f"next_start_id={NEXT_START_ID}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
