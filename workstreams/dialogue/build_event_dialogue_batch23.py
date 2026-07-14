#!/usr/bin/env python3
"""Build source-free Korean historical event dialogue batch23 (5874-6019)."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_DIR = SCRIPT_PATH.parent
WORKSPACE_ROOT = SCRIPT_PATH.parents[3]
TOOLS_DIR = SCRIPT_PATH.parents[2] / "tools"
sys.path.insert(0, str(TOOLS_DIR))
sys.path.insert(0, str(WORKSTREAM_DIR))

import build_common_message_overlay as common  # noqa: E402
import build_event_dialogue_batch22 as shared  # noqa: E402


source_shared = shared.source_shared
BATCH_ID = "msgev_historical_events_5874_6019.v0.23"
OVERLAY_NAME = "msgev_ko_historical_events_5874_6019.v0.23.json"
EVIDENCE_NAME = "alignment_evidence.v0.23.json"
REVIEW_NAME = "review_index.v0.23.json"
VALIDATION_NAME = "validation.v0.23.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 5874
SCOPE_END = 6019
EXCLUDED_INTERNAL_IDS: tuple[int, ...] = ()
BRACKET_TOKEN_RE = shared.BRACKET_TOKEN_RE

EVENTS = (
    {
        "event_id": "end_of_the_tenbun_war",
        "title_ko": "다테 가문 덴분의 난 종결",
        "start_id": 5874,
        "end_id": 5884,
        "selected_count": 11,
    },
    {
        "event_id": "battle_of_anegawa_and_endo_naotsune",
        "title_ko": "아네가와 전투와 엔도 나오쓰네",
        "start_id": 5885,
        "end_id": 5914,
        "selected_count": 30,
    },
    {
        "event_id": "battle_of_imayama",
        "title_ko": "이마야마 전투",
        "start_id": 5915,
        "end_id": 5937,
        "selected_count": 23,
    },
    {
        "event_id": "honganji_uprising_against_nobunaga",
        "title_ko": "혼간지의 노부나가 항쟁",
        "start_id": 5938,
        "end_id": 5955,
        "selected_count": 18,
    },
    {
        "event_id": "demon_king_of_the_sixth_heaven_letter",
        "title_ko": "제육천마왕의 서신",
        "start_id": 5956,
        "end_id": 5976,
        "selected_count": 21,
    },
    {
        "event_id": "motonaris_last_cherry_blossom_banquet",
        "title_ko": "모리 모토나리의 마지막 꽃놀이",
        "start_id": 5977,
        "end_id": 5999,
        "selected_count": 23,
    },
    {
        "event_id": "mitsuhide_receives_sakamoto_castle",
        "title_ko": "미쓰히데의 사카모토성",
        "start_id": 6000,
        "end_id": 6006,
        "selected_count": 7,
    },
    {
        "event_id": "death_of_mori_motonari",
        "title_ko": "모리 모토나리의 죽음",
        "start_id": 6007,
        "end_id": 6019,
        "selected_count": 13,
    },
)

TRANSLATIONS: dict[int, str] = {
    5874: "\x1bCB다테 가문\x1bCZ 제14대 당주 \x1bCA다테 다네무네\x1bCZ――",
    5875: "과거 적자 \x1bCA하루무네\x1bCZ와 대립해 유폐되었으나,\n탈출한 뒤 주변 세력을 규합하여,\n당주 자리를 빼앗은 \x1bCA하루무네\x1bCZ와 맞섰다.",
    5876: "부자의 다툼은 이윽고 \x1bCC오우\x1bCZ 전역을 휘말리게 해,\n끝없이 길어졌다.\n세상에서 말하는 덴분의 난이다.",
    5877: "과거 \x1bCA다네무네\x1bCZ가 자녀를 보내 연을 맺은 세력들도,\n난이 길어지자\n점차 \x1bCB다테 가문\x1bCZ에서 이반했다.",
    5878: "무익한 싸움이 계속되어도 누구에게도 득이 없다.\n그 피로감은 \x1bCB다테 가문\x1bCZ 안팎의 관계자들을\n부자 관계 회복에 나서게 했다.",
    5879: "마침내 쇼군 \x1bCA아시카가 요시테루\x1bCZ까지 중재에 나서,\n난이 시작된 지 6년여 만에\n부자는 화의를 받아들였다.",
    5880: "쇼군 \x1bCA요시테루\x1bCZ 공의 명이라면 어쩔 수 없지.\n내키지는 않지만 가독을\n\x1bCA하루무네\x1bCZ에게 넘기고 은거하겠다……",
    5881: "아버님, 불평은 그만하십시오.\n더 싸워 봐야 무익합니다.",
    5882: "…………",
    5883: "…………",
    5884: "서로 불만을 품은 채였지만,\n\x1bCB다테 가문\x1bCZ의 덴분의 난은 끝났다.\n\x1bCA하루무네\x1bCZ를 당주로 새 걸음을 시작했다……",
    5885: "\x1bCB오다\x1bCZ·\x1bCB[bs1871]\x1bCZ 연합군과\n\x1bCB아자이\x1bCZ·\x1bCB아사쿠라\x1bCZ 연합군이 \x1bCC아네가와\x1bCZ에서 격돌했고,\n초반부터 \x1bCB오다\x1bCZ·\x1bCB[bs1871]\x1bCZ 측이 우세했다.",
    5886: "\x1bCB아사쿠라군\x1bCZ에서 분전한 이는 \x1bCA마가라 나오타카\x1bCZ였다.\n\x1bCB[bs1871]군\x1bCZ의 맹공 속에서 칼을 휘둘러 싸우다,\n마지막에는 홀로 적진에 돌격해 쓰러졌다.",
    5887: "\x1bCB아사쿠라군\x1bCZ이 \x1bCB[bs1871]\x1bCZ의 공격에 패퇴할 무렵,\n\x1bCB아자이 가문\x1bCZ의 본대도 \x1bCB오다 가문\x1bCZ의 정면 공격을 받아,\n패색이 짙어지고 있었다.",
    5888: "(이번 싸움은 우리가 졌다……\n　하지만 내 싸움은 아직 끝나지 않았다!)",
    5889: "거기 있는 자, 멈춰라!",
    5890: "이런, \x1bCA엔도\x1bCZ 님.\n이번 싸움은 패배한 듯합니다.\n어서 달아나십시오!",
    5891: "\x1bCB아자이 가문\x1bCZ에는 이런 때에\n목숨만 건지려는 비겁자가 필요 없다!\n\x1bCB아자이 가문\x1bCZ을 위해 그 목을 내놓아라!",
    5892: "뭐라고……?",
    5893: "각오해라!",
    5894: "아군에게 죽다니 원통하겠지.\n하지만 나도 곧 갈 것이다.\n그대와의 차이는 한순간뿐이다……",
    5895: "\x1bCC아네가와 결전장\x1bCZ·\x1bCB오다군\x1bCZ 본진――",
    5896: "멈춰라! 대체 누구냐!",
    5897: "여기 든 것은\n\x1bCB아자이군\x1bCZ 대장 \x1bCA미타무라 사에몬노조\x1bCZ의 목이다!\n부디 \x1bCA노부나가\x1bCZ 님께서 확인해 주시길!",
    5898: "뭐라, 참말이냐!\n사실이라면 큰 공이다.\n이리 오너라……",
    5899: "(보인다, \x1bCA노부나가\x1bCZ……!\n　이 칼로 네 목을 베겠다!)",
    5900: "기다리십시오!",
    5901: "……!\n네놈은……!",
    5902: "저는 \x1bCA다케나카 한베에\x1bCZ입니다.\n\x1bCB오다\x1bCZ를 섬기기 전 한동안,\n\x1bCB아자이\x1bCZ의 식객으로 \x1bCC오미\x1bCZ에 있었습니다.",
    5903: "…………",
    5904: "제 눈을 속일 수는 없습니다.\n\x1bCB아자이 가문\x1bCZ의 \x1bCA엔도 나오쓰네\x1bCZ 공.",
    5905: "칫, 들켰나!\n나무삼보! \x1bCA노부나가\x1bCZ, 각오해라――!",
    5906: "\x1bCA엔도 나오쓰네\x1bCZ는 아군 대장의 목을 들고,\n\x1bCB오다\x1bCZ 본진에 침입했으나 \x1bCA노부나가\x1bCZ의 자리까지\n한 걸음을 남기고 원통하게 전사했다.",
    5907: "큭…… \x1bCA나가마사\x1bCZ 님……\n정말…… 죄송합니다……",
    5908: "이놈, 수상한 자식……\n\x1bCA노부나가\x1bCZ 님, 죄송합니다!",
    5909: "상관없다. 벌레의 날갯짓일 뿐이다.",
    5910: "(과연 \x1bCA노부나가\x1bCZ 님…… 눈썹 하나 움직이지 않으시다니.)",
    5911: "\x1bCA마가라\x1bCZ·\x1bCA엔도\x1bCZ 같은 맹장이 활약했지만,\n싸움은 \x1bCB아자이\x1bCZ·\x1bCB아사쿠라\x1bCZ 연합군의 패배로 끝났다.",
    5912: "\x1bCB오다\x1bCZ·\x1bCB[bs1871]\x1bCZ 진영은 대승에 환호했지만,\n\x1bCA아자이 나가마사\x1bCZ와 \x1bCA아사쿠라 요시카게\x1bCZ의 목을 베지 못해,\n두 가문에는 아직 여력이 남아 있었다.",
    5913: "\x1bCB미요시 가문\x1bCZ·\x1bCC엔랴쿠지\x1bCZ·\x1bCB혼간지\x1bCZ 등은\n세력이 커진 \x1bCA노부나가\x1bCZ를 경계해 반\x1bCA노부나가\x1bCZ로 돌아섰다.",
    5914: "\x1bCC아네가와\x1bCZ에서의 승리가\n오히려 \x1bCA노부나가\x1bCZ를 궁지로 몰아넣는,\n얄궂은 결과로 이어졌다……",
    5915: "\x1bCC히젠국\x1bCZ·\x1bCC이마야마\x1bCZ,\n\x1bCB오토모군\x1bCZ 본진――",
    5916: "저, 적습이다! 적습이다!\n적의 야습이다!",
    5917: "적진은 완전히 무너졌다!\n모두 적장의 목을 노려라!",
    5918: "이야기는 몇 시간 전으로 거슬러 올라간다.",
    5919: "\x1bCA류조지 다카노부\x1bCZ의 거성――",
    5920: "\x1bCB류조지 가문\x1bCZ 당주 \x1bCA류조지 다카노부\x1bCZ는\n\x1bCB오토모\x1bCZ와 싸우기로 결심했으나,\n\x1bCA나오시게\x1bCZ가 제안한 야습에는 동의하지 못했다.",
    5921: "\x1bCA다카노부\x1bCZ 님,\n적은 전승 축하라며 술을 돌리는 모양입니다.\n지금이야말로 야습의 기회입니다!",
    5922: "야습이라……\n아무리 그래도 너무 서두르는 것 아니냐?",
    5923: "서두르기에 야습인 것입니다!",
    5924: "으, 으음……\n잠깐 기다려라.",
    5925: "…………",
    5926: "몇 분 뒤――",
    5927: "\x1bCA나오시게\x1bCZ, 알겠다!\n당장 출진해 야습을 가하라!",
    5928: "허락하셨군요.\n그럼 곧 준비하겠습니다!",
    5929: "야습에 실패한다면,\n이 \x1bCA나오시게\x1bCZ는 성으로 돌아오지 않겠습니다.",
    5930: "그 증거로……!",
    5931: "\x1bCA나오시게\x1bCZ는 칼을 뽑아 다다미를 두 번 베었다.\n이는 \x1bCB류조지 가문\x1bCZ이 출진할 때의\n법도였다……",
    5932: "그럼 이만 물러가겠습니다!",
    5933: "\x1bCA나오시게\x1bCZ, 엄청난 기백이군……\n저런 얼굴은 처음 보는데!",
    5934: "사실은 어머니께 호되게 꾸지람을 듣고,\n야습을 결심했지만,\n창피해서 죽어도 말 못 하겠군……",
    5935: "그리고――\n죽음을 각오한 \x1bCA나오시게\x1bCZ의 야습으로,\n\x1bCB오토모군\x1bCZ은 큰 혼란에 빠졌다.",
    5936: "이마야마 전투에서 이긴 \x1bCB류조지 가문\x1bCZ은\n태세를 정비해 \x1bCB오토모군\x1bCZ과의 열세를 만회했다.\n이는 훗날의 영토 확장으로 이어졌다고 한다.",
    5937: "\x1bCB류조지\x1bCZ가 비약할 수 있었던 데에는,\n냉정하면서도 뜨거운 참모 \x1bCA나베시마 나오시게\x1bCZ의 존재가\n컸음은 말할 것도 없다.",
    5938: "전국의 문도를 이끄는 총본산 \x1bCB혼간지\x1bCZ――\n그 법주 \x1bCA겐뇨\x1bCZ는\n최근 한 가지 고민을 품고 있었다.",
    5939: "그 고민은 쇼군이 된 \x1bCA아시카가 요시아키\x1bCZ를\n돕는…… 아니, 뒤에서 조종하는 실력자,\n\x1bCA오다 노부나가\x1bCZ의 존재였다.",
    5940: "\x1bCA오다 노부나가\x1bCZ…… 신불을 가벼이 여기면서,\n서양의 기독교에는 관대하다고 들었다.\n우리 교단은 \x1bCA노부나가\x1bCZ를 어떻게 대해야 할까……?",
    5941: "과거 교토의 \x1bCB문도\x1bCZ들이\n법화 일규와 \x1bCB호소카와 가문\x1bCZ·\x1bCB롯카쿠 가문\x1bCZ에 맞서다가,\n\x1bCC야마시나 혼간지\x1bCZ가 불탄 적이 있었다……",
    5942: "불타는 \x1bCC야마시나\x1bCZ에서 피한 \x1bCA쇼뇨\x1bCZ는 \x1bCB혼간지\x1bCZ를\n\x1bCC오사카 이시야마\x1bCZ로 옮길 수밖에 없었다.",
    5943: "그런 사정도 있어, \x1bCA쇼뇨\x1bCZ의 아들 \x1bCA겐뇨\x1bCZ는\n\x1bCC교토\x1bCZ와 \x1bCC기나이\x1bCZ를 다스리는 세력과\n관계를 유지하는 데 고심했다.",
    5944: "\x1bCA[bm75]\x1bCZ 공·\x1bCA미요시 나가요시\x1bCZ와의 관계는 나쁘지 않았다.\n하지만 지금 구보님 뒤에 있는 \x1bCA노부나가\x1bCZ라는 사내는,\n아무래도 위험하게 느껴진다……",
    5945: "구보님을 꼭두각시로 삼아 \x1bCC기나이\x1bCZ 지배를 강화하고,\n그 기세는 커질 뿐……\n이윽고 우리 교단을 겨눌지도 모른다.",
    5946: "만약 \x1bCA노부나가\x1bCZ가 우리 교단의 적이 된다면,\n탄압받기 전에 선수를 쳐서,\n우리가 먼저 봉기하는 편이 나을지도 모른다……",
    5947: "아네가와에서 패했어도 \x1bCA노부나가\x1bCZ를 적대하는\n\x1bCB아사쿠라\x1bCZ·\x1bCB아자이\x1bCZ는 건재하다. 그들과 손잡으면……\n\x1bCA노부나가\x1bCZ의 위협을 미리 막을 수 있을지도 모른다.",
    5948: "아미타의 구원을 믿는 전국 문도의\n앞날에도 영향을 줄 큰 갈림길이다.\n고민되는구나……",
    5949: "고민하던 법주 \x1bCA겐뇨\x1bCZ는 마침내 결심했다.\n전국의 문도에게\n\x1bCA오다 노부나가\x1bCZ를 향한 봉기를 호소했다.",
    5950: "\x1bCA노부나가\x1bCZ는 불적이다!\n모두 일어서라!\n나무아미타불!",
    5951: "뭐라고!?\n\x1bCB혼간지\x1bCZ가 봉기했다고!?\n이놈, \x1bCA겐뇨\x1bCZ……!",
    5952: "(\x1bCB아사쿠라\x1bCZ·\x1bCB아자이\x1bCZ에 이어 \x1bCB혼간지\x1bCZ까지 등을 돌리다니.\n　쇼군인 내 권위가 낮은 것인가,\n　아니면 \x1bCA노부나가\x1bCZ의 인망이 없는 것인가……)",
    5953: "걱정 마십시오! \x1bCB혼간지\x1bCZ 따위……\n당장 진압해 보이겠습니다!",
    5954: "…………",
    5955: "마침내 일어선 \x1bCB혼간지\x1bCZ는\n이후 \x1bCB오다 가문\x1bCZ과 단속적으로 병기를 맞대며,\n10년 동안 적대하게 된다……",
    5956: "\x1bCA오다 노부나가\x1bCZ의 히에이산 소각.\n그 충격은 전국에 퍼졌고, 당연히\n\x1bCA노부나가\x1bCZ를 비난하는 목소리도 적지 않았다.",
    5957: "그중 \x1bCA노부나가\x1bCZ를 특히 격노하게 한 것은,\n평소 신앙에 열심이지 않았다는\n어느 다이묘의 비판이었다.",
    5958: "\x1bCA[b1251]\x1bCZ에게서\n당치도 않은 서신이 왔다고 하더군.",
    5959: "이놈 \x1bCA[bm1251]\x1bCZ 입도!\n출가한 몸으로 전쟁만 하는 탐욕스러운 중이,\n건방지게 의견을 보냈다. 보아라.",
    5960: "실례하겠습니다. 읽어 보지요……\n‘요즘 그대의 행실은\n신불을 두려워하지 않는 불경의 극치다.’",
    5961: "‘그대 같은 천마의 화신을 내버려 둘 수 없다.\n　조만간 상경해 그 목을 받겠다.’",
    5962: "결국,\n우리와 절교하고 싶다는 뜻입니까……?",
    5963: "지금까지 \x1bCB오다 가문\x1bCZ과 \x1bCB다케다 가문\x1bCZ은\n겉으로 우호 관계를 유지하며,\n정면으로 적대한 적은 없었다.",
    5964: "하지만 이 도전적인 문구는,\n지금까지의 관계를 청산하고\n적대하겠다는 선언으로도 읽혔다.",
    5965: "흥, \x1bCA[bm1251]\x1bCZ 녀석도 정말로\n적이 될 생각은 없겠지. 일단 출가한 몸이니,\n히에이산 일로 불평한 정도일 것이다.",
    5966: "그러고 보니, 소각 때\n\x1bCC히에이산\x1bCZ을 떠난 천태좌주 \x1bCA가쿠조 법친왕\x1bCZ이\n\x1bCC가이\x1bCZ에서 \x1bCA[bm1251]\x1bCZ의 보호를 받는다더군.",
    5967: "그 법친왕의 연줄로 조정에서\n권승정 자리를 받고 우쭐해졌지.\n서신의 서명을 보아라.",
    5968: "오, 이것이군요?\n‘천태좌주 사문 신겐’\n이거 참……",
    5969: "그놈,\n천태좌주를 보호했을 뿐인데,\n자기가 천태종을 대표한다고 생각하는군.",
    5970: "답서는 어찌하시겠습니까?",
    5971: "놈이 불교를 지키겠다고 큰소리친다면,\n나는 수행을 방해하는 마왕이라 자칭해 주마.\n‘제육천마왕’은 어떠냐?",
    5972: "‘제육천마왕’ 말입니까……\n\x1bCA[bm1251]\x1bCZ의 거짓 불도 수행을\n방해하겠다는 풍자인지요?",
    5973: "그래. 하지만……\n이제 \x1bCA[bm1251]\x1bCZ 입도와 진정 결판을 낼\n때가 다가왔는지도 모르겠군.",
    5974: "오늘날에도 \x1bCA노부나가\x1bCZ를 표현할 때 쓰는\n‘제육천마왕’은 \x1bCA[bm1251]\x1bCZ에게 보낸 답서에서\n풍자로 자칭한 것이라 전해진다.",
    5975: "하지만 서로 풍자를 주고받은 서신과 달리,\n\x1bCB오다 가문\x1bCZ과 \x1bCB다케다 가문\x1bCZ의 관계는\n점차 긴장되기 시작했다.",
    5976: "\x1bCA오다 노부나가\x1bCZ와 \x1bCA[b1251]\x1bCZ――\n난세의 두 거두는 결전의 날이 머지않았음을\n서로 의식하기 시작했다.",
    5977: "그해 봄, \x1bCC요시다 고리야마성\x1bCZ――",
    5978: "해마다 열리던 꽃놀이 연회가 열렸다.\n산꼭대기 성에서는 온갖 꽃이 피고,\n다시 지는 모습을 한눈에 볼 수 있었다.",
    5979: "연회에는 당주 \x1bCA모토나리\x1bCZ를 비롯해, 료센이라 불린\n\x1bCA깃카와 모토하루\x1bCZ·\x1bCA고바야카와 다카카게\x1bCZ도 참석했다.",
    5980: "\x1bCA모토하루\x1bCZ, \x1bCA다카카게\x1bCZ. 이리 오너라.",
    5981: "예!",
    5982: "아버님……\n평안해 보이십니다.",
    5983: "전혀 평안하지 않다, \x1bCA다카카게\x1bCZ.",
    5984: "너희 둘은 잘 들어라.\n내 목숨이 이제 오래 남지 않은 듯하다……",
    5985: "갑작스러운 말씀이군요.\n하지만 아버님께서 그렇게 말씀하신다면……",
    5986: "짐작 가는 징조가\n있다는 뜻이겠군요……",
    5987: "자기 명수도 읽지 못하고서,\n어찌 적을 꾀로 이기겠느냐.\n그래서 남겨 둘 말이 있다.",
    5988: "너희 둘은,\n목숨을 걸고\n\x1bCA데루모토\x1bCZ와 \x1bCB모리 본가\x1bCZ를 받치겠다고 맹세하겠지?",
    5989: "몇 번을 맹세했는지 모르지만……\n반드시 그리하겠습니다!",
    5990: "설령 \x1bCB고바야카와 가문\x1bCZ이 끊어지더라도,\n반드시 본가를 지키겠습니다.",
    5991: "음, 둘 다 기특하구나.\n백만일심을 잊지 마라!",
    5992: "자, 연회 자리에서 더 잔소리하면\n멋을 모르는 짓이겠지.\n너희도 마음껏 마셔라……",
    5993: "…………",
    5994: "…………",
    5995: "올해도 즐거운 꽃놀이를 맞았구나.",
    5996: "만족했다고는 할 수 없지만……\n그래도 좋은 삶이었다.",
    5997: "‘벗을 얻으니 더욱 기쁜 벚꽃,\n어제와 다른 오늘의 빛깔이여.’\n어떠냐?",
    5998: "결국 이 노래는 \x1bCA모토나리\x1bCZ가 생전에\n마지막으로 읊은 노래가 되어,\n사세구로 후세에 전해졌다……",
    5999: "모략을 다하고 전쟁에 파묻힌 삶이었지만,\n\x1bCA모토나리\x1bCZ는 마지막까지 사람의 인연을 소중히 했다.",
    6000: "히에이산 소각 뒤,\n\x1bCA오다 노부나가\x1bCZ는 공적이 뛰어난 \x1bCA아케치 미쓰히데\x1bCZ에게\n\x1bCC히에이산\x1bCZ 기슭 \x1bCC사카모토\x1bCZ에 성을 짓게 했다.",
    6001: "\x1bCC사카모토\x1bCZ는 예부터\n\x1bCC교토\x1bCZ와 \x1bCC동국\x1bCZ을 잇는 교통의 요지였다.\n그 위상에 걸맞은 성을 짓겠다……!",
    6002: "\x1bCC사카모토성\x1bCZ은 \x1bCC비와호\x1bCZ에 접해 장려한 천수를 갖추고,\n호수에서 배로 곧장 들어갈 수 있는 수성이기도 했다.",
    6003: "……이런 연유로 \x1bCA오다 노부나가\x1bCZ가 \x1bCC사카모토성\x1bCZ을\n\x1bCA미쓰히데\x1bCZ 공에게 맡겼다는 이야기입니다.",
    6004: "성을 맡다니……\n\x1bCA미쓰히데\x1bCZ는 언제부터 \x1bCA노부나가\x1bCZ의 가신이 되었느냐.\n본래 내 부하였을 텐데.",
    6005: "이제 세상에서는 \x1bCA아케치\x1bCZ 공을 \x1bCB오다\x1bCZ의 부하로\n여기는 듯합니다……",
    6006: "……마음에 들지 않는군.",
    6007: "약소 세력 \x1bCB모리 가문\x1bCZ을 이끌고 모략을 써서,\n\x1bCC주고쿠\x1bCZ의 패자까지 오른 \x1bCA모리 모토나리\x1bCZ.",
    6008: "그 긴 삶에도 마침내,\n끝날 때가 찾아오고 있었다――",
    6009: "\x1bCA데루모토\x1bCZ, \x1bCB모리 가문\x1bCZ의 일은 무엇이든\n두 숙부 \x1bCA모토하루\x1bCZ와 \x1bCA다카카게\x1bCZ에게 의지해라.\n모든 것을 혼자 정하려 하지 마라……",
    6010: "명심하겠습니다!",
    6011: "과거 \x1bCC아키\x1bCZ의 작은 영주에 불과했던 \x1bCB모리\x1bCZ가\n지금의 판도를 이룬 것은 시운과 모략의 은혜다.\n결코 교만해서는 안 된다.",
    6012: "…………",
    6013: "\x1bCA데루모토\x1bCZ…… 네게 더 영토를 넓힐\n그릇이 있다고 생각하지 않는다. 높은 뜻을 품지 마라.\n잘못해서라도 천하를 바라서는 안 된다……",
    6014: "명심하고…… 있습니다!",
    6015: "이 잔소리 많은 할아비의…… 경계……\n절대로…… 잊지…… 마라……",
    6016: "대전하――!!",
    6017: "센고쿠의 거성 \x1bCA모리 모토나리\x1bCZ, 죽다――",
    6018: "형의 갑작스러운 죽음과 동생들과의 가독 다툼.\n\x1bCB오우치\x1bCZ·\x1bCB아마고\x1bCZ와의 항쟁, 가신 숙청.\n적자의 요절과 수많은 모략……",
    6019: "그 어느 하나도 태평한 시대에는 없을,\n그야말로 센고쿠의 세상을 체현한\n파란만장한 삶이었다.",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    5876: ["tenbun_war_and_ou_region_terms_require_glossary_review"],
    5885: ["anegawa_battle_term_requires_glossary_review"],
    5886: ["magara_naotaka_name_requires_glossary_review"],
    5897: ["mitamura_saemonnojo_title_requires_glossary_review"],
    5905: ["namusan_exclamation_requires_style_review"],
    5913: ["enryakuji_honganji_terms_require_glossary_review"],
    5915: ["hizen_imayama_battle_names_require_glossary_review"],
    5931: ["ryuzoji_marching_etiquette_requires_history_review"],
    5938: ["honganji_hoshu_kennyo_titles_require_glossary_review"],
    5941: ["hokke_uprising_term_requires_glossary_review"],
    5942: ["yamashina_osaka_ishiyama_names_require_glossary_review"],
    5950: ["namu_amida_butsu_phrase_requires_style_review"],
    5966: ["kakujo_hosshinno_tendai_titles_require_glossary_review"],
    5967: ["gonsojo_rank_requires_glossary_review"],
    5968: ["tendai_zasu_shamon_shingen_title_requires_glossary_review"],
    5971: ["demon_king_sixth_heaven_term_requires_glossary_review"],
    5979: ["mori_ryosen_term_requires_glossary_review"],
    5991: ["hyakuman_isshin_motto_requires_glossary_review"],
    5997: ["motonari_death_poem_requires_poetry_review"],
    6001: ["togoku_region_term_requires_glossary_review"],
}

PREVIOUS_ARTIFACT_PINS = {
    **shared.PREVIOUS_ARTIFACT_PINS,
    "evidence/alignment_evidence.v0.22.json": (
        "8BFE5C891A6497529B1440512488719446F7FA08E940A7BD117554D4D1788B32"
    ),
    "public/msgev_ko_historical_events_5749_5873.v0.22.json": (
        "AF82BB146540FBD72A14149BD93F8CA37F0F27C080A80E42502803284BBA3029"
    ),
    "review/review_index.v0.22.json": (
        "FA44B01EFCE5E565D5BDAB875A20CA8633D58D0B44661EE18D7F17C662FB2B76"
    ),
    "validation.v0.22.json": (
        "F76C2B29E9356EEEFDF99356A6451547DD480F55B4C930EF552F943D87F8645C"
    ),
}
INSTALLED_RESOURCE_PINS = shared.INSTALLED_RESOURCE_PINS


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def write_json(path: Path, value: Any, relative_path: str) -> dict[str, Any]:
    blob = encode_json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {"path": relative_path, "size": len(blob), "sha256": sha256(blob)}


def selected_ids() -> list[int]:
    excluded = set(EXCLUDED_INTERNAL_IDS)
    return [
        entry_id for entry_id in range(SCOPE_START, SCOPE_END + 1)
        if entry_id not in excluded
    ]


def event_for(entry_id: int) -> str:
    for event in EVENTS:
        if int(event["start_id"]) <= entry_id <= int(event["end_id"]):
            return str(event["event_id"])
    raise ValueError(f"no event group for ID {entry_id}")


def source_structure(text: str) -> dict[str, Any]:
    return shared.source_structure(text)


def public_script_counts(text: str) -> dict[str, int]:
    return shared.public_script_counts(text)


def previous_artifact_snapshot() -> dict[str, Any]:
    mismatches: list[dict[str, str | None]] = []
    rows: list[dict[str, str]] = []
    for relative, expected in sorted(PREVIOUS_ARTIFACT_PINS.items()):
        path = WORKSTREAM_DIR / relative
        actual = sha256(path.read_bytes()) if path.is_file() else None
        if actual != expected:
            mismatches.append({"path": relative, "expected": expected, "actual": actual})
        rows.append({"path": relative, "sha256": expected})
    if mismatches:
        raise ValueError(f"previous dialogue artifacts changed: {mismatches}")
    return {
        "file_count": len(rows),
        "manifest_sha256": sha256(
            json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        ),
        "all_hashes_match": True,
    }


def installed_resource_snapshot() -> dict[str, dict[str, Any]]:
    return shared.installed_resource_snapshot()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=common.strict_object
    )


def build(args: argparse.Namespace) -> dict[str, Any]:
    replacements: dict[str, Any] = {
        "SCRIPT_PATH": SCRIPT_PATH,
        "BATCH_ID": BATCH_ID,
        "OVERLAY_NAME": OVERLAY_NAME,
        "EVIDENCE_NAME": EVIDENCE_NAME,
        "REVIEW_NAME": REVIEW_NAME,
        "VALIDATION_NAME": VALIDATION_NAME,
        "SCOPE_START": SCOPE_START,
        "SCOPE_END": SCOPE_END,
        "EXCLUDED_INTERNAL_IDS": EXCLUDED_INTERNAL_IDS,
        "EVENTS": EVENTS,
        "TRANSLATIONS": TRANSLATIONS,
        "UNCERTAINTY_FLAGS": UNCERTAINTY_FLAGS,
        "PREVIOUS_ARTIFACT_PINS": PREVIOUS_ARTIFACT_PINS,
        "INSTALLED_RESOURCE_PINS": INSTALLED_RESOURCE_PINS,
        "selected_ids": selected_ids,
    }
    originals = {name: getattr(shared, name) for name in replacements}
    try:
        for name, value in replacements.items():
            setattr(shared, name, value)
        result = shared.build(args)
    finally:
        for name, value in originals.items():
            setattr(shared, name, value)

    out_root = args.out_root.resolve()
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    validation_path = out_root / VALIDATION_NAME
    evidence = _load_json(evidence_path)
    review = _load_json(review_path)
    validation = _load_json(validation_path)

    loaded = {
        language: source_shared.load_source(path, language)
        for language, path in {
            "SC": args.stock_sc,
            "JP": args.stock_jp,
            "EN": args.stock_en,
        }.items()
    }
    tables = {language: value[2] for language, value in loaded.items()}
    boundary_ids = (
        5873,
        5874,
        5884,
        5885,
        5914,
        5915,
        5937,
        5938,
        5955,
        5956,
        5976,
        5977,
        5999,
        6000,
        6006,
        6007,
        6019,
        6020,
    )
    evidence["schema"] = "nobu16.kr.event-dialogue-alignment-evidence.v23"
    evidence["boundary_anchors"] = [
        {
            "id": entry_id,
            "reference_hashes": {
                language: common.text_hash(tables[language].texts[entry_id])
                for language in ("SC", "JP", "EN")
            },
        }
        for entry_id in boundary_ids
    ]
    review["schema"] = "nobu16.kr.event-dialogue-review-index.v23"
    validation["schema"] = "nobu16.kr.event-dialogue-generation-validation.v23"
    validation["font_integration"].pop(
        "current_font_or_installer_must_not_include_batch22", None
    )
    validation["font_integration"][
        "current_font_or_installer_must_not_include_batch23"
    ] = True
    integrity = validation["preexisting_integrity"]
    integrity["dialogue_v01_v22_artifacts_before"] = integrity.pop(
        "dialogue_v01_v21_artifacts_before"
    )
    integrity["dialogue_v01_v22_artifacts_after"] = integrity.pop(
        "dialogue_v01_v21_artifacts_after"
    )
    safety = validation["safety"]
    safety.pop(
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_v14_v15_v16_v17_v18_v19_v20_v21_artifacts_modified",
        None,
    )
    safety[
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_v14_v15_v16_v17_v18_v19_v20_v21_v22_artifacts_modified"
    ] = False

    overlay_path = out_root / "public" / OVERLAY_NAME
    overlay_meta = {
        "path": f"public/{OVERLAY_NAME}",
        "size": overlay_path.stat().st_size,
        "sha256": sha256(overlay_path.read_bytes()),
    }
    evidence_meta = write_json(evidence_path, evidence, f"evidence/{EVIDENCE_NAME}")
    review_meta = write_json(review_path, review, f"review/{REVIEW_NAME}")
    validation["artifacts"] = {
        "overlay": overlay_meta,
        "alignment_evidence": evidence_meta,
        "review_index": review_meta,
    }
    validation_meta = write_json(validation_path, validation, VALIDATION_NAME)
    return {
        "out_root": out_root,
        "entry_count": len(selected_ids()),
        "artifacts": {
            "overlay": overlay_meta,
            "alignment_evidence": evidence_meta,
            "review_index": review_meta,
            "generation_validation": validation_meta,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stock-sc",
        type=Path,
        default=WORKSPACE_ROOT
        / "KR_PATCH_WORK"
        / "backups"
        / "officer_name_probe_v0_1"
        / "msgev.SC.stock.bin",
    )
    parser.add_argument(
        "--stock-jp", type=Path, default=WORKSPACE_ROOT / "MSG_PK" / "JP" / "msgev.bin"
    )
    parser.add_argument(
        "--stock-en", type=Path, default=WORKSPACE_ROOT / "MSG_PK" / "EN" / "msgev.bin"
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
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
