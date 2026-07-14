#!/usr/bin/env python3
"""Build source-free Korean historical event dialogue batch24 (6020-6141)."""

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
import build_event_dialogue_batch23 as shared  # noqa: E402


source_shared = shared.source_shared
BATCH_ID = "msgev_historical_events_6020_6141.v0.24"
OVERLAY_NAME = "msgev_ko_historical_events_6020_6141.v0.24.json"
EVIDENCE_NAME = "alignment_evidence.v0.24.json"
REVIEW_NAME = "review_index.v0.24.json"
VALIDATION_NAME = "validation.v0.24.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 6020
SCOPE_END = 6141
EXCLUDED_INTERNAL_IDS: tuple[int, ...] = ()
BRACKET_TOKEN_RE = shared.BRACKET_TOKEN_RE

EVENTS = (
    {
        "event_id": "hideyoshi_builds_nagahama_castle",
        "title_ko": "히데요시의 나가하마 축성",
        "start_id": 6020,
        "end_id": 6045,
        "selected_count": 26,
    },
    {
        "event_id": "katakura_kojuro_comes_of_age",
        "title_ko": "가타쿠라 고주로의 원복",
        "start_id": 6046,
        "end_id": 6048,
        "selected_count": 3,
    },
    {
        "event_id": "fall_of_the_muromachi_shogunate",
        "title_ko": "무로마치 막부의 실질적 멸망",
        "start_id": 6049,
        "end_id": 6064,
        "selected_count": 16,
    },
    {
        "event_id": "shingen_marches_on_the_capital",
        "title_ko": "신겐의 상경 출진",
        "start_id": 6065,
        "end_id": 6094,
        "selected_count": 30,
    },
    {
        "event_id": "furinkazan_banner",
        "title_ko": "풍림화산 군기",
        "start_id": 6095,
        "end_id": 6118,
        "selected_count": 24,
    },
    {
        "event_id": "kenshin_mourns_shingens_death",
        "title_ko": "겐신이 애도한 신겐의 죽음",
        "start_id": 6119,
        "end_id": 6141,
        "selected_count": 23,
    },
)

TRANSLATIONS: dict[int, str] = {
    6020: "\x1bCC오미국\x1bCZ·\x1bCC이마하마\x1bCZ――",
    6021: "\x1bCB아자이 가문\x1bCZ이 멸망한 뒤,\n\x1bCA오다 노부나가\x1bCZ는 \x1bCA기노시타 히데요시\x1bCZ에게 명해,\n\x1bCC오다니성\x1bCZ과 가까운 \x1bCC이마하마\x1bCZ에 새 성을 짓게 했다.",
    6022: "원숭이,\n이 땅의 이름은 정했느냐?",
    6023: "예!\n주군의 이름에서 ‘나가’ 한 글자를 받아,\n‘\x1bCC나가하마\x1bCZ’라 하고자 합니다……",
    6024: "흥, 참으로 네답구나.\n네놈 같은 아첨꾼에게 어울리는 이름이다!\n나라면 그런 이름은 떠올리지도 못했을 게다.",
    6025: "아, 아하하……\n참으로 매서운 말씀이십니다.\n당장 다시 생각하겠습니다――",
    6026: "됐다. 나라면 쓰지 않겠지만,\n이 땅을 쓰는 것은 너다.\n너다운 이름을 붙이면 되겠지.",
    6027: "그, 그렇습니다.\n주군께 어울리지 않는 이름이니 제가……\n뭐, 뭐라고 하셨습니까!?",
    6028: "이 땅을 제게 주신다고요?",
    6029: "뭐냐, 필요 없느냐?\n그렇다면 \x1bCA미쓰히데\x1bCZ에게라도――",
    6030: "아니 아니 아니옵니다!\n감사히 받겠습니다!\n분에 넘치는 영광이옵니다!",
    6031: "흥, 네다운 아첨꾼의 성이로군.\n네 재주가 드러나는 성과 마을을 세워라!",
    6032: "나다운 성이라……\n좋아, 좋아, 좋아!\n해내고 말겠다!",
    6033: "(\x1bCC교토\x1bCZ와도 가깝고 정말 좋은 곳이군……\n　언젠가는 나도 천하를 노리는 한 사람이 될 터.)",
    6034: "원숭이!",
    6035: "예, 예엣!",
    6036: "말하는 걸 깜빡했는데,\n너, 이름을 바꾸어라!",
    6037: "이제 성주가 될 몸이다.\n천하에 이름이 알려져도\n부끄럽지 않을 이름을 생각해 두어라!",
    6038: "예, 예엣!",
    6039: "후우……\n한순간도 방심할 수 없는 분이군……",
    6040: "\x1bCA히데요시\x1bCZ의 손으로 완공된 \x1bCC나가하마성\x1bCZ은\n\x1bCC비와호\x1bCZ 수운을 충분히 활용하고자,\n성 안에 수문을 둔 획기적인 설계였다.",
    6041: "성하마을도 물자 유통과 집적에 유리하도록,\n동서로 앞면을 낸 세로 마을과\n남북으로 앞면을 낸 가로 마을을 함께 배치했다.",
    6042: "\x1bCC나가하마\x1bCZ의 성하마을은 훗날 \x1bCC오사카\x1bCZ와\n\x1bCC후시미\x1bCZ 등 대규모 성하마을의 본보기가 되었다……",
    6043: "\x1bCA노부나가\x1bCZ의 말처럼,\n도시 계획의 천재 \x1bCA히데요시\x1bCZ의 재능이\n남김없이 발휘되기 시작했다.",
    6044: "그래, 새 이름은\n\x1bCA시바타\x1bCZ 님과 \x1bCA니와\x1bCZ 공의 이름에서 한 글자씩 받아,\n‘\x1bCA하시바\x1bCZ’로 해야겠군.",
    6045: "아첨꾼이라 불려도 상관없다……\n가문 안에 적을 만들고 싶지는 않으니까.",
    6046: "\x1bCA가타쿠라 고주로 가게쓰나\x1bCZ――\n그 사내가 원복 의식을 마쳤다.",
    6047: "그의 ‘지략’은 전쟁을 승리로 이끌 뿐 아니라,\n훗날 \x1bCB다테 가문\x1bCZ을 바른길로 이끄는 이정표가 된다.",
    6048: "이 순간, \x1bCA가타쿠라 고주로\x1bCZ라는 사내가\n난세라는 무대에 첫발을 내디뎠다……",
    6049: "\x1bCA[b1251]\x1bCZ의 파죽지세는 반\x1bCA노부나가\x1bCZ 연합의\n사기를 북돋았을 뿐 아니라, 쇼군 \x1bCA아시카가 요시아키\x1bCZ의\n마음까지 크게 뒤흔들었다.",
    6050: "마침내 \x1bCA요시아키\x1bCZ는 \x1bCC교토\x1bCZ를 탈출했다.\n남쪽 오구라 연못에 자리한 \x1bCC마키시마성\x1bCZ을 거점으로,\n\x1bCA노부나가군\x1bCZ에 반기를 든 것이다.",
    6051: "이때를 기다렸다, 이놈 \x1bCA노부나가\x1bCZ!\n나는 장식품에 불과한 쇼군이 아니다!\n\x1bCA[bm1251]\x1bCZ의 상경에 맞춰 너를 버리겠다!",
    6052: "하지만 이때 \x1bCA[bm1251]\x1bCZ는 이미 병으로 죽었고,\n유언으로 죽음을 숨기라 했지만,\n그 사실은 점차 세상에 퍼지고 있었다……",
    6053: "어리석은 구보여……\n시세도 읽지 못하고 \x1bCA[bm1251]\x1bCZ만 믿어\n이 \x1bCA노부나가\x1bCZ를 배반하다니!",
    6054: "저런 작은 성에…… 저토록 한심한 진세라니.\n저래도 무가의 동량이라 할 수 있나.\n이제 \x1bCC교토\x1bCZ에 쇼군은 필요 없다. 쳐라!",
    6055: "이제 저도 구보님을 따를 생각이 없습니다.\n앞으로는 \x1bCB오다 가문\x1bCZ에 뼈를 묻을 각오입니다.\n\x1bCA아케치\x1bCZ 공, 함께…… \x1bCC마키시마성\x1bCZ을 공격합시다.",
    6056: "\x1bCA호소카와\x1bCZ 공, 심중을 헤아립니다……\n제가 돕겠습니다.",
    6057: "기대했던 \x1bCB다케다\x1bCZ의 원군도 없고 가신마저 떠나,\n고립된 \x1bCC마키시마성\x1bCZ의 \x1bCA요시아키\x1bCZ는\n\x1bCB오다군\x1bCZ의 맹공을 견디지 못하고 성문을 열었다.",
    6058: "하지만 \x1bCA요시아키\x1bCZ는 \x1bCC교토\x1bCZ로 돌아가기를 단호히 거부했다.\n\x1bCA노부나가\x1bCZ도 \x1bCA요시아키\x1bCZ의 목숨을 빼앗지 않아,\n두 사람의 고집이 맞부딪쳤다……",
    6059: "\x1bCA요시아키\x1bCZ는 \x1bCA아케치\x1bCZ·\x1bCA호소카와\x1bCZ 등 옛 신하의 설득도 거부하고,\n오히려 그들을 곧장 돌려보냈다.\n협상이 결렬된 채 \x1bCA요시아키\x1bCZ는 \x1bCC교토\x1bCZ를 떠났다.",
    6060: "흥! 돌아가신 아버님과 형님……\n아니, 역대 쇼군 중에도 \x1bCC교토\x1bCZ를 떠나\n지방에서 재기한 이는 얼마든지 있다!",
    6061: "형님이 해를 입은 뒤 그 사내를 의지하기 전……\n여러 나라를 떠돌던 때로 돌아갔다 생각하면,\n이 정도는 고난도 아니다!",
    6062: "잘 들어라! 나는 반드시 재기한다!\n\x1bCA노부나가\x1bCZ를 토벌하고…… \x1bCC교토\x1bCZ로 돌아가겠다!\n기다리고 있어라!",
    6063: "오늘날에는 막부의 수장인 무로마치 공, 곧\n\x1bCA요시아키\x1bCZ가 \x1bCC교토\x1bCZ를 떠난 일을 무로마치 막부의\n실질적인 멸망으로 본다……",
    6064: "하지만 \x1bCA요시아키\x1bCZ는 정이대장군직을 유지한 채,\n여러 나라 다이묘에게 의지하며 \x1bCC교토\x1bCZ 탈환을 꿈꾸고,\n두 번째 유랑길에 오르게 되었다……",
    6065: "\x1bCB혼간지\x1bCZ의 법주 \x1bCA겐뇨\x1bCZ는\n\x1bCA오다 노부나가\x1bCZ를 치기 위해 봉기했다.\n전국의 문도에게 \x1bCA노부나가\x1bCZ 타도를 호소했다.",
    6066: "\x1bCB혼간지\x1bCZ의 역대 법주는 종조 \x1bCA신란\x1bCZ을 따라 혼인했고,\n\x1bCA겐뇨\x1bCZ도 열네 살에 좌대신 \x1bCA산조 긴요리\x1bCZ의 딸\n\x1bCA뇨슌니\x1bCZ와 혼인했다.",
    6067: "\x1bCA뇨슌니\x1bCZ의 언니는 \x1bCA[b1251]\x1bCZ의 아내 \x1bCA산조노카타\x1bCZ였다.\n\x1bCA[bm1251]\x1bCZ과 \x1bCA겐뇨\x1bCZ는 동서지간, 당시 말로는\n‘아이무코’가 된 것이다.",
    6068: "그리하여 \x1bCA겐뇨\x1bCZ는 동서인 \x1bCA[bm1251]\x1bCZ에게도\n\x1bCA노부나가\x1bCZ 타도 포위망에 가담해 달라고\n몇 번이나 요청했다……",
    6069: "우리 가문은 지금까지 \x1bCB오다 가문\x1bCZ과\n겉으로 충돌하지 않고 지내 왔지만……",
    6070: "\x1bCB[bs1448] 가문\x1bCZ과 싸울 때도\n잇코 일규의 도움을 받았으니,\n\x1bCA겐뇨\x1bCZ 쇼닌의 요청을 무시할 수도 없다……",
    6071: "\x1bCA노부나가\x1bCZ의 동맹 \x1bCB[bs1871] 가문\x1bCZ과 불화가 있었지만,\n\x1bCB다케다\x1bCZ는 지금까지 \x1bCB오다 가문\x1bCZ과 화친을 유지해,\n정면으로 적대한 적은 없었다.",
    6072: "하지만 쇼군 \x1bCA요시아키\x1bCZ 공을 꼭두각시로 부리고,\n\x1bCC히에이산\x1bCZ에 불까지 지른\n\x1bCA노부나가\x1bCZ의 행실이 눈에 거슬리는 것도 사실이다.",
    6073: "(나도 벌써 쉰 고개를 넘었다……\n　천하에 이름을 떨칠\n　마지막 기회일지도 모른다.)",
    6074: "좋아…… 거병하자!",
    6075: "우리 가문은 이제 \x1bCB오다 가문\x1bCZ과 관계를 끊는다.\n\x1bCA오다 노부나가\x1bCZ를 쓰러뜨리고자,\n\x1bCC교토\x1bCZ를 향해 군사를 일으킨다!",
    6076: "이로써 \x1bCA[bm1251]\x1bCZ은 상경을 결심했다――\n그 결의를 밝히고자,\n가문의 중신들을 군의에 불러 모았다.",
    6077: "이제 우리는 \x1bCC교토\x1bCZ로 향한다.\n이번 군의는 이를 위한 것이다!\n\x1bCA겐시로\x1bCZ!",
    6078: "예!\n여기 있습니다!",
    6079: "네 아카조나에가 선봉을 맡아라.\n먼저 \x1bCC미카와\x1bCZ를 엿보며 \x1bCA[bm1871]\x1bCZ를 위협하고,\n그 뒤 내 본대에 합류하라!",
    6080: "맡겨 주십시오!",
    6081: "아카조나에의 무서움을\n\x1bCA[bm1871]\x1bCZ에게 똑똑히 새겨 주겠습니다!",
    6082: "\x1bCA[bm44]\x1bCZ!\n너는 \x1bCC미노\x1bCZ로 가라.\n\x1bCC이와무라\x1bCZ를 포위해 \x1bCA노부나가\x1bCZ를 붙들어 두어라.",
    6083: "예!",
    6084: "\x1bCA노부나가\x1bCZ의 움직임을 묶어,\n\x1bCB[bs1871]\x1bCZ만 우리를 상대하게 할 계책이군요……\n알겠습니다. 맡겨 주십시오.",
    6085: "\x1bCA[bs1638]\x1bCZ는 \x1bCB[bs1871]\x1bCZ의 지성을 함락시키며,\n내 본대에 합류하라.",
    6086: "알겠습니다.",
    6087: "나머지는 모두 내 본대에 합류하라.\n\x1bCB[bs1871]\x1bCZ과 \x1bCB오다\x1bCZ의 영지를 당당히 가로질러,\n\x1bCC교토\x1bCZ를 향한다!",
    6088: "그렇다면 모두,\n다테나시 앞에 맹세하라!",
    6089: "미하타와 다테나시도 굽어살피소서!",
    6090: "미하타와 다테나시도 굽어살피소서!",
    6091: "내 앞길을 막는 적은 모조리 짓밟아라!\n\x1bCC오와리\x1bCZ와 \x1bCC미카와\x1bCZ의 애송이들에게……\n갈고닦은 내 군략을 보여 주마!",
    6092: "\x1bCA[bm1251]\x1bCZ, 상경을 위해 일어서다――\n그 충격은 순식간에 여러 나라로 퍼져,\n그 \x1bCA노부나가\x1bCZ마저 전율하게 했다……",
    6093: "이제 막 반\x1bCA노부나가\x1bCZ 포위망에 가담한\n최대 최강의 비장의 패가 일으킨 소용돌이는――",
    6094: "\x1bCB오다\x1bCZ·\x1bCB다케다\x1bCZ 두 가문에만 그치지 않고,\n천하와 관계된 여러 나라 다이묘까지\n모조리 휘말리게 한다.",
    6095: "\x1bCC쓰쓰지가사키관\x1bCZ――",
    6096: "\x1bCB다케다 가문\x1bCZ에서도 무용으로 이름난 장수들이\n\x1bCA[b1251]\x1bCZ의 부름을 받고 모였다.",
    6097: "모두 모였느냐?",
    6098: "당주님, 다음 싸움은 어디입니까?",
    6099: "그래서 선봉은 누구입니까?",
    6100: "아, 아니……\n그런 것이 아니다.",
    6101: "너희를 모은 것은,\n새 군기를 보여 주기 위해서다.",
    6102: "오오,\n군기 말씀이십니까?",
    6103: "그래, 이것이다.",
    6104: "이것은……\n‘빠르기는 바람과 같고’",
    6105: "‘고요하기는 숲과 같으며’",
    6106: "‘침략하기는 불과 같고’",
    6107: "‘움직이지 않기는 산과 같다.’ \n이 글귀는 분명……\n‘손자’의 가르침이지요.",
    6108: "정확히 보셨소.\n역시 \x1bCB다케다 가문\x1bCZ의 중신들이십니다.",
    6109: "이것이 바로 ‘손자사여의 깃발’이다.\n앞으로 이 깃발을 내걸 생각이다.",
    6110: "감정이나 기세에 휩쓸리지 말고,\n오직 병법의 이치를 따라야 한다는 뜻이지.",
    6111: "병법의 진수인 ‘허실’과 ‘표리’도 아우르니,\n당주님의 군략에 어울리는 깃발입니다.",
    6112: "역시 당주님이십니다.\n참으로 훌륭한 생각입니다.",
    6113: "……음!\n바로 그렇다.",
    6114: "우리 \x1bCB다케다 가문\x1bCZ에 어울리는 군기입니다!",
    6115: "그럼 결정됐군.\n앞으로 손자사여를 우리의 군기로 삼는다!",
    6116: "\x1bCB다케다 가문\x1bCZ의 유명한 ‘풍림화산’ 군기.\n언제부터 썼는지, 애초에 실제로\n사용했는지조차 분명하지 않다.",
    6117: "하지만 병법의 가르침을 중시한 \x1bCB다케다군\x1bCZ의 상징으로,\n이 깃발은 후세에도 거듭 이야기되었다……",
    6118: "‘\x1bCB다케다 가문\x1bCZ이라면 이 깃발’이라는 인상을\n사람들의 마음에 강하게 남긴 것이다.",
    6119: "…………",
    6120: "보고드립니다!\n\x1bCA다케다 호쇼인 [bm1251]\x1bCZ께서\n돌아가셨다는 소식입니다!",
    6121: "확실한 소식이냐……?",
    6122: "예……!\n\x1bCB호조\x1bCZ의 수하에게서 얻은 소식입니다!",
    6123: "그런가…… 물러가라.",
    6124: "예!",
    6125: "천명이라지만…… 참으로 아깝구나.\n영웅호걸이란 \x1bCA[bm1251]\x1bCZ 같은 이를 두고 하는 말.\n이로써 \x1bCC간토\x1bCZ에서 무사가 사라졌군……",
    6126: "군사를 \x1bCC시나노\x1bCZ로 보내시겠습니까?",
    6127: "필요 없다.\n\x1bCA가쓰요리\x1bCZ로는 가슴이 뛰지 않아……",
    6128: "\x1bCC시나노\x1bCZ 따위는 언제든 빼앗을 수 있다.\n지금부터 사흘간 성 아래에서 음악을 금하라!\n다음 평정은 그 뒤에 연다.",
    6129: "\x1bCA[bm1251]\x1bCZ이 죽었다니……",
    6130: "주군께서 눈물을 흘리시다니,\n보기 드문 일이군.",
    6131: "그토록 \x1bCA[bm1251]\x1bCZ의 죽음이 아쉬우신가.",
    6132: "\x1bCA가게이에\x1bCZ 공이라면,\n그 마음을 이해하시지 않습니까?",
    6133: "묻지 않아도 알 일이다!\n무사의 숙적을 병마에 빼앗기다니……\n어찌 눈물을 흘리지 않겠는가!",
    6134: "그대는 왜 우는가……",
    6135: "가슴이 뛰지 않는다니……\n\x1bCB우에스기\x1bCZ의 의에는 어긋날지 모르나,\n참으로 주군다운 말씀이군.",
    6136: "참으로 그렇소.\n우리 마음도 떨리는군요.",
    6137: "\x1bCA[b1448]\x1bCZ와 \x1bCA[b1251]\x1bCZ――",
    6138: "서로를 싫어하고 미워했으며,\n서로를 존경하고 이해했다……",
    6139: "두 사람의 관계는 오늘날에도 여러 설이 있지만,\n누구도 진실을 알 수 없다.",
    6140: "다만 몇 번이나 격전을 벌인 호적수가\n자신의 손이 닿지 않는 곳으로 떠났다.",
    6141: "그 사실이\n\x1bCA[bm1448]\x1bCZ의 마음을 뒤흔들었으리라는 것은,\n무리한 상상만은 아닐 것이다……",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    6020: ["omi_imahama_place_names_require_glossary_review"],
    6023: ["nagahama_name_derivation_requires_history_review"],
    6041: ["castle_town_street_layout_terms_require_history_review"],
    6044: ["hashiba_name_derivation_requires_glossary_review"],
    6046: ["katakura_kojuro_kagetsuna_name_requires_glossary_review"],
    6050: ["ogura_pond_makishima_castle_names_require_glossary_review"],
    6063: ["muromachi_shogunate_fall_interpretation_requires_history_review"],
    6064: ["seiitaishogun_title_requires_glossary_review"],
    6066: ["honganji_family_names_and_titles_require_glossary_review"],
    6067: ["aimuko_historical_kinship_term_requires_glossary_review"],
    6070: ["ikko_ikki_and_shonin_terms_require_glossary_review"],
    6076: ["joraku_rendered_as_capital_march_requires_style_review"],
    6079: ["akazonae_term_requires_glossary_review"],
    6088: ["tatenashi_armor_oath_requires_history_review"],
    6089: ["mihata_tatenashi_war_cry_requires_history_review"],
    6095: ["tsutsujigasaki_palace_term_requires_glossary_review"],
    6109: ["sonshi_shijo_banner_term_requires_glossary_review"],
    6116: ["furinkazan_banner_term_requires_glossary_review"],
    6120: ["takeda_hosshoin_title_requires_glossary_review"],
    6125: ["kanto_warrior_eulogy_requires_style_review"],
}

PREVIOUS_ARTIFACT_PINS = {
    **shared.PREVIOUS_ARTIFACT_PINS,
    "evidence/alignment_evidence.v0.23.json": (
        "6FC7B0AB0720E83CC1D912D3D1DE2051FA5D4480AC861FC452BC8235D7A010DC"
    ),
    "public/msgev_ko_historical_events_5874_6019.v0.23.json": (
        "EDCE4AF6BC0CA2C0E5F00C7C186D2744F5621D145DC98C805F61DE289374F5C8"
    ),
    "review/review_index.v0.23.json": (
        "52F3129C2B71504450A9C5C20E900F98B579AB2BF4F652BCFE87EBBAFA566564"
    ),
    "validation.v0.23.json": (
        "E3FE49CB5DAD8F9D09302F6AE19F8FA39787A8B1D8C18F95E7D04F0F321D3035"
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
        6019,
        6020,
        6045,
        6046,
        6048,
        6049,
        6064,
        6065,
        6094,
        6095,
        6118,
        6119,
        6141,
        6142,
    )
    evidence["schema"] = "nobu16.kr.event-dialogue-alignment-evidence.v24"
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
    review["schema"] = "nobu16.kr.event-dialogue-review-index.v24"
    validation["schema"] = "nobu16.kr.event-dialogue-generation-validation.v24"
    validation["font_integration"].pop(
        "current_font_or_installer_must_not_include_batch23", None
    )
    validation["font_integration"][
        "current_font_or_installer_must_not_include_batch24"
    ] = True
    integrity = validation["preexisting_integrity"]
    integrity["dialogue_v01_v23_artifacts_before"] = integrity.pop(
        "dialogue_v01_v22_artifacts_before"
    )
    integrity["dialogue_v01_v23_artifacts_after"] = integrity.pop(
        "dialogue_v01_v22_artifacts_after"
    )
    safety = validation["safety"]
    safety.pop(
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_v14_v15_v16_v17_v18_v19_v20_v21_v22_artifacts_modified",
        None,
    )
    safety[
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_v14_v15_v16_v17_v18_v19_v20_v21_v22_v23_artifacts_modified"
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
