#!/usr/bin/env python3
"""Build source-free Korean historical event dialogue batch22 (5749-5873)."""

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
import build_event_dialogue_batch21 as shared  # noqa: E402


source_shared = shared.source_shared
BATCH_ID = "msgev_historical_events_5749_5873.v0.22"
OVERLAY_NAME = "msgev_ko_historical_events_5749_5873.v0.22.json"
EVIDENCE_NAME = "alignment_evidence.v0.22.json"
REVIEW_NAME = "review_index.v0.22.json"
VALIDATION_NAME = "validation.v0.22.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 5749
SCOPE_END = 5873
EXCLUDED_INTERNAL_IDS: tuple[int, ...] = ()
BRACKET_TOKEN_RE = shared.BRACKET_TOKEN_RE

EVENTS = (
    {
        "event_id": "otomo_anti_mori_encirclement",
        "title_ko": "오토모의 모리 포위망",
        "start_id": 5749,
        "end_id": 5776,
        "selected_count": 28,
    },
    {
        "event_id": "battle_of_anegawa_preparations",
        "title_ko": "아네가와 전투 전야",
        "start_id": 5777,
        "end_id": 5802,
        "selected_count": 26,
    },
    {
        "event_id": "move_to_hamamatsu_and_okazaki_intrigue",
        "title_ko": "하마마쓰 입성과 오카자키의 불씨",
        "start_id": 5803,
        "end_id": 5816,
        "selected_count": 14,
    },
    {
        "event_id": "mogami_yoshiaki_succeeds",
        "title_ko": "모가미 요시아키의 가독 계승",
        "start_id": 5817,
        "end_id": 5838,
        "selected_count": 22,
    },
    {
        "event_id": "mogami_yoshiaki_power_stone",
        "title_ko": "모가미 요시아키의 힘돌",
        "start_id": 5839,
        "end_id": 5855,
        "selected_count": 17,
    },
    {
        "event_id": "battle_of_imayama_prologue",
        "title_ko": "이마야마 전투 전야",
        "start_id": 5856,
        "end_id": 5873,
        "selected_count": 18,
    },
)

TRANSLATIONS: dict[int, str] = {
    5749: "과거 \x1bCA오토모[bm473]\x1bCZ은 동생 \x1bCA요시나가\x1bCZ를 \x1bCB오우치 가문\x1bCZ에\n양자로 보내고, \x1bCB오우치\x1bCZ·\x1bCB오토모\x1bCZ 연합으로\n\x1bCC북규슈\x1bCZ를 휩쓸려 했다……",
    5750: "하지만 \x1bCA모리 모토나리\x1bCZ가 \x1bCA오우치 요시나가\x1bCZ를 멸해\n그 계획은 무너졌다. 동생을 죽음으로 내몬\n\x1bCB모리\x1bCZ에 원한을 품게 되었다.",
    5751: "그 뒤 \x1bCB오토모\x1bCZ와 \x1bCB모리\x1bCZ 두 가문은\n\x1bCC북규슈\x1bCZ의 주도권을 두고\n몇 번이나 격전을 벌였다……",
    5752: "\x1bCB모리\x1bCZ 놈들…… 제 손으로 \x1bCA요시나가\x1bCZ를\n죽음에 몰아넣고도, 마치 \x1bCB오우치 가문\x1bCZ의\n후계자인 양 굴다니 불손하기 짝이 없다.",
    5753: "하지만 이렇게 일진일퇴해서는 결판이 나지 않는다.\n다른 세력도 끌어들여\n\x1bCB모리\x1bCZ 포위망을 만들어야겠군……",
    5754: "듣자 하니 \x1bCB모리\x1bCZ는 모략의 달인이라 자부한다지.\n그렇다면 모략에는 모략으로…… 장기를 빼앗아 주마.",
    5755: "\x1bCA[bm473]\x1bCZ은 \x1bCB모리 가문\x1bCZ 주변 세력 가운데\n이해가 같은 이들을 골라\n공동 작전을 제안했다.",
    5756: "\x1bCC비젠\x1bCZ의 \x1bCB우라가미 가문\x1bCZ, \x1bCC도사\x1bCZ의 \x1bCB이치조 가문\x1bCZ,\n그리고 \x1bCB모리\x1bCZ를 따르던 \x1bCB무라카미 수군\x1bCZ까지 끌어들였다.",
    5757: "또한 \x1bCB모리\x1bCZ를 증오하는\n\x1bCA야마나카 시카노스케\x1bCZ·\x1bCA아마고 가쓰히사\x1bCZ 등도 지원했다.",
    5758: "그리고 오랫동안 \x1bCB오토모 가문\x1bCZ이 보호해 온,\n\x1bCB오우치 가문\x1bCZ의 피를 이은 \x1bCA오우치 데루히로\x1bCZ를\n옛 \x1bCB오우치\x1bCZ 저택이 있던 \x1bCC야마구치\x1bCZ로 보냈다.",
    5759: "지금이야말로 \x1bCB오우치 가문\x1bCZ 부흥의 때다!\n\x1bCB오우치\x1bCZ를 멸한 원수 \x1bCB모리\x1bCZ를 쓰러뜨리자!",
    5760: "\x1bCB모리 가문\x1bCZ·\x1bCA요시다 고리야마성\x1bCZ――",
    5761: "이런, \x1bCA[bm473]\x1bCZ 녀석.\n제법 큰일을 벌였군.\n\x1bCB오우치\x1bCZ의 혈족까지 내세우다니.",
    5762: "\x1bCA[bm473]\x1bCZ에게 이만한 정치력이 있다니,\n의외로군.\n아버님, 어찌하시겠습니까?",
    5763: "결국 ‘\x1bCB모리\x1bCZ가 밉다’는 이유만으로 손잡은\n약한 유대…… 오합지졸에 불과하다.\n연계하지 못하게 막고 하나씩 무너뜨리면 된다.",
    5764: "사방이 적에게 둘러싸였지만,\n\x1bCA모리 모토나리\x1bCZ는 외교와 모략을 활용해\n냉정히 대처하며 포위망을 무너뜨렸다……",
    5765: "이런, 늙은 몸에는 고된 일이군.\n\x1bCB아마고\x1bCZ와 \x1bCB오우치\x1bCZ 잔당을 처단하는 일은\n아들들에게 맡겨도 되겠지.",
    5766: "안심하십시오.",
    5767: "저희에게 맡기십시오!",
    5768: "\x1bCA모토하루\x1bCZ·\x1bCA다카카게\x1bCZ 등은 \x1bCA시카노스케\x1bCZ의\n\x1bCB아마고\x1bCZ 재흥군을 물리치는 한편, \x1bCC야마구치\x1bCZ에 상륙한\n\x1bCA오우치 데루히로\x1bCZ를 공격했다.",
    5769: "큭……\n\x1bCB오우치\x1bCZ 부흥은 이루지 못했나!\n\x1bCB모리\x1bCZ 놈! \x1bCB모리\x1bCZ 놈――!!",
    5770: "힘이 다한 \x1bCA오우치 데루히로\x1bCZ는\n\x1bCC스오 차우스산\x1bCZ에서 자결했다.\n\x1bCB모리 가문\x1bCZ의 위기는 일단 지나갔다……",
    5771: "어떻게든 수습했군.\n\x1bCA모토하루\x1bCZ와 \x1bCA다카카게\x1bCZ가 양쪽 수레바퀴처럼 \x1bCB모리\x1bCZ를 받치면\n당분간은 평안하겠지.",
    5772: "그나저나 \x1bCB오우치\x1bCZ와 \x1bCB아마고\x1bCZ……\n둘 다 내가 젊었을 때는 멀리 우러러보던\n부러운 대다이묘였는데……",
    5773: "고전 끝에 쓰러뜨린 두 가문이 모두\n부흥을 꿈꾸며 \x1bCB모리\x1bCZ에 도전해 오다니.\n오래 살고 볼 일이군……",
    5774: "\x1bCB오토모 가문\x1bCZ·\x1bCC후나이관\x1bCZ――",
    5775: "으음…… 포위망이 깨졌나.\n하지만 \x1bCB모리\x1bCZ도 \x1bCC북규슈\x1bCZ에서 철수한 모양이군……\n지금은 그것으로 충분하다.",
    5776: "당분간은\n\x1bCC규슈\x1bCZ로 건너올 여력도 없겠지.\n그사이 우리 세력을 키우자……",
    5777: "\x1bCC가네가사키\x1bCZ의 위기에서 벗어난 \x1bCA오다 노부나가\x1bCZ는\n\x1bCC기후\x1bCZ로 돌아오자마자 태세를 정비해,\n\x1bCB아자이 가문\x1bCZ 토벌 의지를 드러냈다.",
    5778: "\x1bCB오다 가문\x1bCZ·\x1bCA오다 노부나가\x1bCZ의 거성――",
    5779: "\x1bCB아자이\x1bCZ는 우리를 배신하고 \x1bCB아사쿠라\x1bCZ를 택했다!\n놈들을 내버려 두면,\n\x1bCC기후\x1bCZ에서 \x1bCC교토\x1bCZ로 가는 길이 위협받는다!",
    5780: "적이 된 이상 \x1bCB아자이\x1bCZ를 신속히 멸하고,\n\x1bCC오미\x1bCZ를 우리 것으로 만들어야 한다.\n이번에는 \x1bCA[bm1871]\x1bCZ에게 후방 지원을 부탁했다.",
    5781: "군의를 마친다.\n모두 준비를 마치는 대로 집결하라!\n\x1bCB[bs1871]군\x1bCZ에 뒤처지지 마라!",
    5782: "주군께서 크게 노하신 듯하군.",
    5783: "당연하지!\n\x1bCA나가마사\x1bCZ 녀석, \x1bCA오이치\x1bCZ 님과 혼인하고도……\n용서할 수 없다!",
    5784: "우리가 \x1bCB[bs1871] 가문\x1bCZ에 원군을 청한다면,\n\x1bCB아자이 가문\x1bCZ도 \x1bCB아사쿠라 가문\x1bCZ에 구원을 청하겠지……\n큰 싸움이 되겠군.",
    5785: "\x1bCA오다 노부나가\x1bCZ가 \x1bCA[b1871]\x1bCZ의 군대와 함께\n\x1bCC오미\x1bCZ로 진군한다는 소식이 \x1bCC오다니성\x1bCZ에도 전해지자,\n\x1bCA아자이 나가마사\x1bCZ는 \x1bCA아사쿠라 요시카게\x1bCZ에게 구원을 청했다.",
    5786: "\x1bCB아자이 가문\x1bCZ·\x1bCA아자이 나가마사\x1bCZ의 거성――",
    5787: "아뢰옵니다, 주군.\n\x1bCA아사쿠라 가게타케\x1bCZ 공의 병사들이\n도착했다고 합니다.",
    5788: "뭐라?\n\x1bCA요시카게\x1bCZ 공께서는 직접 오지 않으셨나?",
    5789: "\x1bCA아사쿠라 요시카게\x1bCZ 님은 \x1bCC쓰루가\x1bCZ에 남아,\n후방을 굳히겠다고 하셨습니다.",
    5790: "어찌 이럴 수가!!\n나는 의형을 배신하면서까지 오랜 인연을 중히 여겨,\n아사쿠라를 택했는데 직접 구원하지 않다니……",
    5791: "……하지만,\n\x1bCB아사쿠라\x1bCZ에는 고 \x1bCA소테키\x1bCZ 님이\n단련한 정예병이 있습니다.",
    5792: "아니다, \x1bCB아사쿠라군\x1bCZ에 기대지 않겠다!\n\x1bCA노부나가\x1bCZ를 배신한 것은 내가 택한 길이다.\n\x1bCB아자이\x1bCZ의 병사로 \x1bCA노부나가\x1bCZ의 목을 베겠다!",
    5793: "주군……",
    5794: "\x1bCA오이치\x1bCZ,\n그대에게 미안하다.\n이제 의형과 정면으로 싸우게 됐다.",
    5795: "아닙니다. 저는 이미 \x1bCB아자이 가문\x1bCZ의 사람입니다.\n오라버니보다 남편인 주군을 따르겠습니다.\n마음에 두지 마시고…… 싸우십시오……",
    5796: "미안하다, \x1bCA오이치\x1bCZ……",
    5797: "주군――!\n선봉은 이 \x1bCA가즈마사\x1bCZ에게 맡겨 주십시오!",
    5798: "\x1bCB아사쿠라\x1bCZ의 겁쟁이들이 없어도,\n\x1bCB아자이\x1bCZ의 의기를 보여 주겠습니다!",
    5799: "부탁한다, \x1bCA가즈마사\x1bCZ! \x1bCA나오쓰네\x1bCZ!\n힘든 싸움에 끌어들여 미안하다.\n하지만 부디 나를 받쳐 다오!",
    5800: "맡겨 주십시오!!",
    5801: "예!\n……반드시 \x1bCB아자이\x1bCZ에 승리를 안기겠습니다!",
    5802: "\x1bCB오다\x1bCZ·\x1bCB[bs1871]\x1bCZ·\x1bCB아자이\x1bCZ·\x1bCB아사쿠라\x1bCZ……\n네 다이묘의 정예가 모인 회전,\n아네가와 전투가 시작되려 했다……",
    5803: "\x1bCC히쿠마성\x1bCZ을 함락한 \x1bCA[b1871]\x1bCZ는\n마침내 \x1bCC도토미\x1bCZ 공략을 이루었다……",
    5804: "\x1bCA다다쓰구\x1bCZ.\n나는 \x1bCC오카자키\x1bCZ에서 이곳으로 옮겨,\n\x1bCB다케다\x1bCZ에 대비할 생각이다.",
    5805: "예!\n그러면 \x1bCC오카자키\x1bCZ는 어찌하시겠습니까?",
    5806: "\x1bCA노부야스\x1bCZ의 성으로 삼겠다.",
    5807: "…………",
    5808: "이 성은 서쪽 방비가 약하군……\n니노마루를 넓혀 굳혀야 한다.",
    5809: "게다가 ‘물러나는 말’이라는 이름은 영 좋지 않군.\n옛 이름인 \x1bCC하마마쓰\x1bCZ로 바꾸는 게 어떠냐?",
    5810: "좋은 생각이십니다.",
    5811: "(주군은 \x1bCC미카와\x1bCZ를 떠나고 싶어 하시는군.\n　\x1bCC미카와\x1bCZ의 부인과는 사이가 나쁘고,\n　\x1bCC오카자키\x1bCZ에는 \x1bCB이마가와\x1bCZ와 연이 있는 자가 많다……)",
    5812: "(고민 많은 \x1bCC오카자키\x1bCZ를 떠나려는 마음은 이해한다.\n　하지만 작은 일을 해결하지 않고 두었다가,\n　훗날 큰일이 되지 않아야 할 텐데……)",
    5813: "\x1bCA쓰키야마도노\x1bCZ라 불린 \x1bCA세나히메\x1bCZ는,\n\x1bCA이마가와 요시모토\x1bCZ의 양녀로 \x1bCB[bs1871]\x1bCZ에 시집왔으나,\n\x1bCA[bm1871]\x1bCZ와의 부부 사이는 이미 얼어붙었다……",
    5814: "\x1bCA쓰키야마도노\x1bCZ는 \x1bCC오카자키성\x1bCZ에 들어가는 것조차 허락받지 못해,\n성 밖 절에서 살고 있었다.",
    5815: "그런 처지의 \x1bCA쓰키야마도노\x1bCZ와 아들 \x1bCA노부야스\x1bCZ를\n권력 다툼에 이용하려는 자들은,\n대부분 \x1bCC오카자키성\x1bCZ에 출사한 이들이었고……",
    5816: "\x1bCA[bm1871]\x1bCZ가 \x1bCC하마마쓰성\x1bCZ을 중시하게 되자,\n\x1bCC오카자키성\x1bCZ으로 돌아온 \x1bCA쓰키야마도노\x1bCZ 등을 둘러싸고,\n더 거센 모략의 폭풍이 휘몰아쳤다……",
    5817: "이날 \x1bCB모가미 가문\x1bCZ 당주 \x1bCA모가미 요시모리\x1bCZ가 은거하고,\n적자 \x1bCA모가미 요시아키\x1bCZ가 새 당주가 되었다.",
    5818: "\x1bCA요시모리\x1bCZ가 은거한 까닭은 지금도 분명하지 않다.\n\x1bCA요시모리\x1bCZ와 \x1bCA요시아키\x1bCZ 사이에 다툼이 있었다고도,\n없었다고도 전해진다.",
    5819: "\x1bCB다테 가문\x1bCZ·\x1bCA다테 데루무네\x1bCZ의 거성――",
    5820: "\x1bCA요시아키\x1bCZ 공이 \x1bCB모가미\x1bCZ의 당주가 된 모양이군.",
    5821: "그렇습니다.",
    5822: "\x1bCA요시아키\x1bCZ 공은 어떤 사람이지?",
    5823: "어떤 사람이라……\n여동생을 아끼는 좋은 오라버니입니다.",
    5824: "제게도 자주 편지를 보내십니다.\n보시겠습니까?",
    5825: "……아니, 지금은 됐다.\n전에 본 적이 있어서.",
    5826: "(세심한 편지였지……\n　사람은 겉만 보고 알 수 없는 법이군.)",
    5827: "그 밖에는 없느냐?",
    5828: "그렇게 물으셔도……\n오라버니는 세상의 소문과 같은 분입니다.",
    5829: "무용이 뛰어나고 자비로워,\n병사와 백성 모두 따르지 않는 이가 없습니다.",
    5830: "그런가……\n‘우슈의 여우’라고도 불린다던데.",
    5831: "여우라니……\n오라버니를 못마땅해하는 자가\n퍼뜨린 소문이겠지요.",
    5832: "성품이 너그럽고 용감하며 삿되지 않고,\n도량이 넓고 정직해 겉과 속이 다르지 않습니다.",
    5833: "그래서 저는 오히려 걱정합니다.\n이 난세에 간악한 자가\n오라버니를 속이지 않을까 하고요.",
    5834: "(말을 절반만 믿는다고 해도……\n　교활한 사내는 아닌 듯하군.)",
    5835: "(엄청난 괴력의 소유자라 들었는데, 싸움은 어떨까.\n　언젠가 전장에서 시험해 보도록 하지.)",
    5836: "\x1bCB모가미 가문\x1bCZ과 \x1bCB다테 가문\x1bCZ은 인척이었지만,\n서로 돕기보다\n서로 견제하는 면이 강했다……",
    5837: "그 관계는 매우 팽팽하여,\n어느 한쪽에 빈틈이 생기면\n전쟁이 벌어질 수도 있었다.",
    5838: "\x1bCA요시아키\x1bCZ가 막 당주가 되어 기반이 불안하니,\n\x1bCA데루무네\x1bCZ가 빈틈을 살피는 것은\n자연스러운 흐름이었다.",
    5839: "\x1bCC우슈\x1bCZ·\x1bCC자오온천\x1bCZ――",
    5840: "\x1bCA모가미 요시모리\x1bCZ의 적자 \x1bCA모가미 요시아키\x1bCZ는\n사냥을 즐긴 뒤,\n온천에 몸을 담그려 했다.",
    5841: "으음……\n사냥 뒤의 온천……\n이것이야말로 극락이군.",
    5842: "……이라고 말하고 싶지만,\n멋을 모르는 자가 있군…… 나와라!",
    5843: "너희는 누구냐?\n목욕하는 데 무기 따위 필요 없을 텐데.",
    5844: "……우리는 산적이다.\n가진 것을 전부 내놓아라!",
    5845: "하하하!\n목욕 중인 사람에게 가진 것을 내놓으라니,\n재미있는 말을 하는군.",
    5846: "(하나, 둘…… 세 명인가……\n　뭐, 어떻게든 되겠지.)",
    5847: "이봐, 산적들아.\n저기 있는 돌을 보아라!",
    5848: "돌……?",
    5849: "\x1bCA요시아키\x1bCZ와 산적 사이에는,\n사람이 두 팔을 벌려야 겨우 안을 만큼\n커다란 돌이 놓여 있었다.",
    5850: "너희는\n저 돌을 들어 올릴 수 있느냐?",
    5851: "…………",
    5852: "후후……\n그것도 못 한다면 나를 이길 수 없다.",
    5853: "헛소리를…… 각오해라!",
    5854: "이때 \x1bCA요시아키\x1bCZ는\n산적 두목을 죽이고,\n나머지 둘에게 상처를 입혔다고 한다.",
    5855: "또한 \x1bCA요시아키\x1bCZ가 가신들과 힘을 겨뤄\n들어 올린 거석은 ‘요시아키 공의 힘돌’이라 불리며,\n지금도 \x1bCC자오온천\x1bCZ에 자리한다고 한다……",
    5856: "\x1bCC하카타\x1bCZ는 \x1bCC북규슈\x1bCZ의 거대한 무역항으로,\n규슈 탐제 \x1bCA[b473]\x1bCZ과\n주고쿠의 패자 \x1bCA모리 모토나리\x1bCZ가 치열하게 다퉜다.",
    5857: "그 와중에,\n\x1bCC히젠\x1bCZ에서 주가 \x1bCB쇼니 가문\x1bCZ을 무너뜨리고,\n세력을 넓힌 \x1bCA류조지 다카노부\x1bCZ가 두각을 드러냈다.",
    5858: "\x1bCB오토모 가문\x1bCZ·\x1bCA[b473]\x1bCZ의 거성――",
    5859: "흥, \x1bCA모토나리\x1bCZ 그 늙은 여우!\n마침내 \x1bCC하카타\x1bCZ를 포기한 모양이군.",
    5860: "\x1bCA요시오카\x1bCZ 공의 계책이 통한 듯합니다.\n\x1bCA모토나리\x1bCZ는 이제\n\x1bCC주고쿠\x1bCZ를 떠날 수 없을 겁니다.",
    5861: "그런가.\n그렇다면 이제야 그 난폭한 \x1bCA다카노부\x1bCZ를\n제대로 징벌할 수 있겠군!",
    5862: "예.\n그러니 전쟁을 준비하시지요.",
    5863: "\x1bCB류조지 가문\x1bCZ·\x1bCA류조지 다카노부\x1bCZ의 거성――",
    5864: "\x1bCB오토모\x1bCZ가 마침내 병사를 모으기 시작했군.\n이 \x1bCC히젠\x1bCZ을 노리는 모양이다.",
    5865: "쳇…… 정말 오는 건가……\n내가 너무 요란하게 날뛰었나?\n이제 사과해도 용서하지 않겠지……",
    5866: "이대로 우리 영지를 넓히면,\n반드시 \x1bCC지쿠젠\x1bCZ과 \x1bCC지쿠고\x1bCZ를 침범하게 된다.\n결판을 내는 수밖에 없다!",
    5867: "그렇지……\n그럼 각오를 굳혀 볼까!",
    5868: "\x1bCA다카노부\x1bCZ 님께서 각오하셔도,\n가신들은 아직 \x1bCB오토모\x1bCZ를 두려워합니다.\n싸워야 한다고 설득해야 합니다.",
    5869: "그런 일은 네게 맡기마, \x1bCA나오시게\x1bCZ!\n나는 잠자코 고개만 끄덕이마!",
    5870: "\x1bCA류조지 다카노부\x1bCZ와\n중신 \x1bCA나베시마 나오시게\x1bCZ는 의형제였다.",
    5871: "\x1bCA다카노부\x1bCZ의 아버지 \x1bCA치카이에\x1bCZ가 죽은 뒤,\n\x1bCA게이긴니\x1bCZ는 \x1bCB류조지\x1bCZ에 \x1bCA나베시마\x1bCZ의 힘이 필요하다고 판단해,\n\x1bCA나오시게\x1bCZ의 아버지 \x1bCA기요후사\x1bCZ의 계실이 되었다.",
    5872: "\x1bCA게이긴니\x1bCZ의 예상대로,\n\x1bCA나오시게\x1bCZ는 군사와 정치 양면에서 재능을 꽃피워,\n이제 \x1bCB류조지 가문\x1bCZ에 없어서는 안 될 인재가 되었다.",
    5873: "\x1bCA다카노부\x1bCZ와 \x1bCA나오시게\x1bCZ――\n두 주종이 맞닥뜨린 최대의 위기,\n이마야마 전투가 시작되려 했다……",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    5749: ["otomo_dynamic_name_prefix_requires_runtime_review"],
    5756: ["murakami_navy_term_requires_glossary_review"],
    5770: ["suo_chausuyama_name_requires_glossary_review"],
    5802: ["anegawa_battle_term_requires_glossary_review"],
    5803: ["hikuma_hamamatsu_castle_name_requires_glossary_review"],
    5813: ["tsukiyamadono_senahime_titles_require_glossary_review"],
    5817: ["mogami_yoshiaki_reading_requires_glossary_review"],
    5830: ["ushu_fox_epithet_requires_glossary_review"],
    5839: ["ushu_zao_onsen_names_require_glossary_review"],
    5855: ["yoshiaki_power_stone_name_requires_glossary_review"],
    5856: ["kyushu_tandai_title_requires_history_review"],
    5857: ["shoni_clan_name_requires_glossary_review"],
    5871: ["keiginni_name_reading_requires_glossary_review"],
    5873: ["imayama_battle_term_requires_glossary_review"],
}

PREVIOUS_ARTIFACT_PINS = {
    **shared.PREVIOUS_ARTIFACT_PINS,
    "evidence/alignment_evidence.v0.21.json": (
        "0527A2BEFE4ECDA85347FF7707F0ADF60644068E902A323BD9ECA1BA95D64B21"
    ),
    "public/msgev_ko_historical_events_5629_5748.v0.21.json": (
        "EB34E1613FE97736B8C0B5A308956431E6BA0756FB4076E19AA5F52291743854"
    ),
    "review/review_index.v0.21.json": (
        "6AA964CB89C096CD3558A73D0D8CB173BDE6A164E63B35E0C678223B07F0E682"
    ),
    "validation.v0.21.json": (
        "71091235581C26D22EBEEBB52F05DC9F2BC08D55CAD4253552A8092B75F93476"
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
        5748,
        5749,
        5776,
        5777,
        5802,
        5803,
        5816,
        5817,
        5838,
        5839,
        5855,
        5856,
        5873,
        5874,
    )
    evidence["schema"] = "nobu16.kr.event-dialogue-alignment-evidence.v22"
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
    review["schema"] = "nobu16.kr.event-dialogue-review-index.v22"
    validation["schema"] = "nobu16.kr.event-dialogue-generation-validation.v22"
    validation["font_integration"].pop(
        "current_font_or_installer_must_not_include_batch21", None
    )
    validation["font_integration"][
        "current_font_or_installer_must_not_include_batch22"
    ] = True
    integrity = validation["preexisting_integrity"]
    integrity["dialogue_v01_v21_artifacts_before"] = integrity.pop(
        "dialogue_v01_v20_artifacts_before"
    )
    integrity["dialogue_v01_v21_artifacts_after"] = integrity.pop(
        "dialogue_v01_v20_artifacts_after"
    )
    safety = validation["safety"]
    safety.pop(
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_v14_v15_v16_v17_v18_v19_v20_artifacts_modified",
        None,
    )
    safety[
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_v14_v15_v16_v17_v18_v19_v20_v21_artifacts_modified"
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
