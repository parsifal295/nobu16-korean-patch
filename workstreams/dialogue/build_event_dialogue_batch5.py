#!/usr/bin/env python3
"""Build source-free Korean historical event dialogue batch5 (3565-3688)."""

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
sys.path.insert(0, str(WORKSTREAM_DIR))

import build_common_message_overlay as common  # noqa: E402
import build_event_dialogue_batch4 as shared  # noqa: E402


BATCH_ID = "msgev_historical_events_3565_3688.v0.5"
OVERLAY_NAME = "msgev_ko_historical_events_3565_3688.v0.5.json"
EVIDENCE_NAME = "alignment_evidence.v0.5.json"
REVIEW_NAME = "review_index.v0.5.json"
VALIDATION_NAME = "validation.v0.5.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 3565
SCOPE_END = 3688
EXCLUDED_INTERNAL_IDS: tuple[int, ...] = ()
BRACKET_TOKEN_RE = re.compile(r"\[[a-z0-9_]+\]")

EVENTS = (
    {
        "event_id": "fall_of_saito_mino",
        "title_ko": "사이토 가문의 미노 상실",
        "start_id": 3565,
        "end_id": 3575,
        "selected_count": 11,
    },
    {
        "event_id": "saito_takamasa_isshiki_name",
        "title_ko": "사이토 다카마사의 잇시키 개성",
        "start_id": 3576,
        "end_id": 3594,
        "selected_count": 19,
    },
    {
        "event_id": "kato_truce_and_kawagoe_return",
        "title_ko": "가토 화의와 가와고에 귀환",
        "start_id": 3595,
        "end_id": 3622,
        "selected_count": 28,
    },
    {
        "event_id": "ujiyasu_fox_waka",
        "title_ko": "호조 우지야스의 여우 와카",
        "start_id": 3623,
        "end_id": 3641,
        "selected_count": 19,
    },
    {
        "event_id": "kagetora_first_campaign",
        "title_ko": "도라치요의 환속과 첫 출진",
        "start_id": 3642,
        "end_id": 3661,
        "selected_count": 20,
    },
    {
        "event_id": "mori_takamoto_education",
        "title_ko": "모리 다카모토의 교육",
        "start_id": 3662,
        "end_id": 3688,
        "selected_count": 27,
    },
)

TRANSLATIONS: dict[int, str] = {
    3565: (
        "\x1bCC교토\x1bCZ에서 \x1bCC미노\x1bCZ로 간 기름 장수는 지방 슈고인\n"
        "\x1bCB도키 가문\x1bCZ의 눈에 들어 유력 무장이 되었고, 그 아들\n"
        "\x1bCA[bm924]\x1bCZ 공이 \x1bCB도키\x1bCZ를 몰아내 전국 다이묘가 됐다."
    ),
    3566: (
        "하극상의 전형이던 \x1bCC미노\x1bCZ의 \x1bCB사이토 가문\x1bCZ은,\n"
        "이제 \x1bCA오다 노부나가\x1bCZ의 공세에 밀려\n"
        "4대에 걸친 역사를 끝내려 하고 있었다."
    ),
    3567: (
        "기뻐해라, \x1bCA기초\x1bCZ!\n"
        "장인어른이 내게 물려주겠다고 했던\n"
        "\x1bCC미노\x1bCZ 땅을 마침내 손에 넣었다!"
    ),
    3568: "……축하드립니다.",
    3569: "왜 그러지?\n아버지를 죽인 오라비라 해도,\n친정이 멸망하니 슬픈 것이냐?",
    3570: (
        "아닙니다. 이제 \x1bCB사이토 가문\x1bCZ에 미련은 없습니다.\n"
        "이렇게 될 운명이었겠지요.\n"
        "지금은 \x1bCC미노\x1bCZ가 하루빨리 재건되기만을 바랍니다……"
    ),
    3571: (
        "안심해라!\n"
        "\x1bCB사이토 가문\x1bCZ의 잔당을 평정한 뒤,\n"
        "나는 이 \x1bCC미노\x1bCZ 땅으로 본거지를 옮길 것이다!"
    ),
    3572: (
        "\x1bCC오와리\x1bCZ보다 \x1bCC미노\x1bCZ가 \x1bCC긴키\x1bCZ에……\n"
        "아니, 천하에 더 가까우니까!"
    ),
    3573: (
        "기쁨에 들뜬 \x1bCB오다 가문\x1bCZ과 달리,\n"
        "패배한 \x1bCA사이토 다쓰오키\x1bCZ는 미련을 떨치지 못한 채\n"
        "\x1bCC미노\x1bCZ를 떠났다……"
    ),
    3574: (
        "이놈, \x1bCA노부나가\x1bCZ!\n"
        "두고 봐라!\n"
        "언젠가…… 반드시 복수하겠다!"
    ),
    3575: (
        "\x1bCA사이토 다쓰오키\x1bCZ는 이후 \x1bCC나가라강\x1bCZ을 따라 내려가\n"
        "\x1bCC이세 나가시마\x1bCZ로 달아났다고도, 옛 인연을 좇아\n"
        "\x1bCC에치젠\x1bCZ으로 갔다고도 전해진다."
    ),
    3576: (
        "이해에 \x1bCC미노\x1bCZ의 전국 다이묘 \x1bCA사이토 다카마사\x1bCZ는\n"
        "소수의 병력만 이끌고 상경하여,\n"
        "쇼군 \x1bCA[b75]\x1bCZ에게 배알했다."
    ),
    3577: (
        "쇼군께 존안을 뵈오니 더없는 영광입니다……\n"
        "저는 \x1bCA사이토 다카마사\x1bCZ라 합니다.\n"
        "무사히 교토로 돌아오신 것을 축하드립니다."
    ),
    3578: (
        "네가 \x1bCC미노\x1bCZ의 \x1bCA사이토 다카마사\x1bCZ인가.\n"
        "소문은 들었다.\n"
        "아버지 \x1bCA[bm924]\x1bCZ 공을 죽였다던데……?"
    ),
    3579: (
        "황공합니다. \x1bCA[bm924]\x1bCZ 공은…… 제 아버지이나,\n"
        "불의를 많이 저질러 백성의 원한이 깊었습니다.\n"
        "그래서 어쩔 수 없이 토벌했습니다."
    ),
    3580: (
        "가신이 주군을 죽이고, 아들이 아버지를 죽이는 것이\n"
        "전국시대의 법도란 말인가……\n"
        "참으로 허망하구나."
    ),
    3581: (
        "그건 그렇다 치고, 쇼군께\n"
        "이번 상경을 맞아\n"
        "청이 하나 있습니다."
    ),
    3582: "호오……?\n말해 보아라.",
    3583: (
        "\x1bCB사이토 가문\x1bCZ은 미노 슈고다이직을 맡고 있으며,\n"
        "\x1bCB쇼군가\x1bCZ의 호코슈로서 쇼군께 직접\n"
        "충성을 다해 온 집안입니다."
    ),
    3584: (
        "……그 \x1bCB사이토 가문\x1bCZ의 이름은,\n"
        "네가 죽인 \x1bCA[bm924]\x1bCZ 공이 빼앗은 것이겠지.\n"
        "본래 기름 장수의 후손이라고 들었다만?"
    ),
    3585: (
        "그렇습니다.\n"
        "쇼군께 충성을 다할 수 있다면,\n"
        "\x1bCB사이토\x1bCZ라는 가문 이름도 버릴 생각입니다."
    ),
    3586: (
        "원하건대 쇼군가 오쇼반슈 가운데\n"
        "어느 한 집안의 이름을,\n"
        "이 \x1bCA다카마사\x1bCZ에게 내려 주시겠습니까."
    ),
    3587: (
        "(하극상으로 출세한 아버지를 죽인 자가,\n"
        " 오래된 가문 이름을 가장 탐내다니……\n"
        " 참으로 우스운 일이군……)"
    ),
    3588: (
        "마음대로 하거라……\n"
        "어차피 내게는 아무 권력도 없다.\n"
        "허울뿐인 쇼군에 지나지 않으니."
    ),
    3589: "예!",
    3590: (
        "\x1bCA사이토 다카마사\x1bCZ는 이때,\n"
        "쇼군 \x1bCA요시테루\x1bCZ에게 무로마치 막부 사시키의 하나이자,\n"
        "외가와 인연이 있는 \x1bCB잇시키 가문\x1bCZ의 이름을 인정받았다."
    ),
    3591: (
        "어쩌면 아버지를 죽였다는 오명과,\n"
        "자신의 출신을 둘러싼 의혹을\n"
        "\x1bCB사이토\x1bCZ라는 성과 함께 묻으려 했는지도 모른다……"
    ),
    3592: (
        "동시에 이름도 \x1bCA다카마사\x1bCZ에서 ‘\x1bCA요시타쓰\x1bCZ’로 바꾸었다.\n"
        "이는 \x1bCB잇시키 가문\x1bCZ의 통자에서\n"
        "‘요시’를 따온 것이었다."
    ),
    3593: "그러나 이 개성을,\n당사자 외에 인정한 사람은 드물었고……",
    3594: (
        "‘\x1bCA잇시키 요시타쓰\x1bCZ’로 개명한 뒤에도,\n"
        "실제로는 ‘\x1bCA사이토 요시타쓰\x1bCZ’라고 부르는 이가\n"
        "더 많았다고 한다."
    ),
    3595: (
        "\x1bCB호조 가문\x1bCZ의 시조 \x1bCA소운\x1bCZ(\x1bCA이세 소즈이\x1bCZ)은 본래,\n"
        "\x1bCA이마가와 우지치카\x1bCZ의 숙부이자 군사였고,\n"
        "훗날 독립해 \x1bCC간토\x1bCZ로 영지를 넓혀 갔다."
    ),
    3596: (
        "\x1bCA우지쓰나\x1bCZ 시대에는 \x1bCB이마가와\x1bCZ와 \x1bCB호조\x1bCZ가 별도 다이묘가 되어,\n"
        "\x1bCC스루가\x1bCZ 동부(\x1bCC후지강\x1bCZ 동쪽)를 둘러싼 패권 다툼으로\n"
        "두 가문은 차츰 적대 관계가 되었다."
    ),
    3597: (
        "\x1bCB이마가와 가문\x1bCZ으로서는 본래 지배하던 \x1bCC가토\x1bCZ를,\n"
        "가신 집안이던 \x1bCB호조 가문\x1bCZ에 빼앗긴 채\n"
        "언제까지고 내버려 둘 수는 없었다."
    ),
    3598: (
        "자, \x1bCA우지야스\x1bCZ 녀석……\n"
        "어떻게 나올지 볼 만하겠군.\n"
        "앞뒤로 적을 두고 어찌할 테냐?"
    ),
    3599: (
        "\x1bCA요시모토\x1bCZ의 계략으로 \x1bCB야마노우치\x1bCZ·\x1bCB오기야쓰\x1bCZ의\n"
        "\x1bCB양 우에스기 가문\x1bCZ에 고가쿠보 \x1bCA아시카가 하루우지\x1bCZ까지 가세해,\n"
        "\x1bCB호조 가문\x1bCZ의 \x1bCC가와고에성\x1bCZ을 공격하고 있었다……"
    ),
    3600: (
        "\x1bCA우지야스\x1bCZ는 매제 \x1bCA쓰나시게\x1bCZ를 \x1bCC가와고에성\x1bCZ 방어에 보내고,\n"
        "자신은 \x1bCC가토\x1bCZ에\n"
        "진을 친 모양이군."
    ),
    3601: (
        "군사를 나누었나.\n"
        "상투적인 병법이지만 참으로 재미없는 계책이군.\n"
        "그 정도로 이 \x1bCA요시모토\x1bCZ를 이길 수 있다 생각하느냐……"
    ),
    3602: "\x1bCB다케다군\x1bCZ도 우리를 돕고 있습니다.\n질 리가 없습니다.",
    3603: (
        "\x1bCB이마가와\x1bCZ·\x1bCB다케다\x1bCZ 연합군은 \x1bCC나가쿠보성\x1bCZ과 \x1bCC기쓰네바시\x1bCZ에서\n"
        "\x1bCA호조 우지야스\x1bCZ의 군대를 격퇴했다."
    ),
    3604: (
        "이번 전쟁은 조금 져도 상관없다.\n"
        "오히려 진정한 적은 시간이다……!\n"
        "시간이 아깝다! 어서 결판을 내야 한다!"
    ),
    3605: (
        "작은 전투의 승패에 매달릴 여유가 없다.\n"
        "\x1bCA우지야스\x1bCZ는 \x1bCA요시모토\x1bCZ의 노림수를 비껴 가며,\n"
        "기사회생의 수를 둘 때를 엿보고 있었다……"
    ),
    3606: (
        "\x1bCA우지야스\x1bCZ, 역시 내 상대가 못 되는가……\n"
        "하지만 어딘가 일부러 지는 듯하군.\n"
        "다른 계책이라도 있는 것인가?"
    ),
    3607: "\x1bCA요시모토\x1bCZ 님, 최악의 사태가 벌어졌습니다.\n미처 깨닫지 못한 소승의 불찰입니다……",
    3608: "무슨 일이냐, 무엇이 벌어졌지?",
    3609: (
        "우군인 \x1bCA다케다 하루노부\x1bCZ에게서 사자가 와,\n"
        "\x1bCB호조\x1bCZ와…… 화친하라고 권했습니다."
    ),
    3610: "뭐라고!?\n\x1bCA하루노부\x1bCZ 녀석, \x1bCB호조\x1bCZ 편으로 돌아섰나!",
    3611: (
        "\x1bCA우지야스\x1bCZ는 \x1bCA요시모토\x1bCZ의 원군인 \x1bCA다케다 하루노부\x1bCZ에 주목해,\n"
        "전투가 시작된 직후부터\n"
        "화친의 중재를 부탁해 두었다."
    ),
    3612: (
        "\x1bCA다케다 하루노부\x1bCZ에게도,\n"
        "\x1bCB이마가와\x1bCZ·\x1bCB호조 양가\x1bCZ에 동시에 선심을 쓸 수 있는\n"
        "중재자의 자리는 나쁘지 않았다."
    ),
    3613: (
        "그럼 \x1bCB호조 가문\x1bCZ이 \x1bCC가토\x1bCZ의 성을 \x1bCB이마가와 가문\x1bCZ에\n"
        "넘기는 조건으로 양가는 화친한다.\n"
        "이 조건으로 괜찮겠지?"
    ),
    3614: (
        "나는 괜찮다. \x1bCC가토\x1bCZ는 \x1bCC하코네산\x1bCZ 너머다.\n"
        "지키기도 번거로웠으니,\n"
        "깨끗이 \x1bCB이마가와 가문\x1bCZ에 넘기지."
    ),
    3615: (
        "\x1bCC가토\x1bCZ는 본래 \x1bCB이마가와 가문\x1bCZ이 다스릴 땅이다.\n"
        "제자리로 돌아왔을 뿐이라고도 할 수 있지만……\n"
        "양보받는다면 전쟁을 계속할 이유는 없다."
    ),
    3616: (
        "조금 못마땅하기는 하나,\n"
        "여기서 서로 군사를 물리고 전쟁을 끝내기로\n"
        "약속하자."
    ),
    3617: (
        "좋아, 이로써 화의는 이루어졌다!\n"
        "이 \x1bCA하루노부\x1bCZ도 애쓴 보람이 있군.\n"
        "하하하!"
    ),
    3618: "…………",
    3619: (
        "이 \x1bCB이마가와\x1bCZ·\x1bCB호조\x1bCZ·\x1bCB다케다\x1bCZ의 미묘한 관계는\n"
        "훗날 고소슨 삼국동맹으로 이어지지만,\n"
        "그것은 아직 먼 훗날의 이야기다."
    ),
    3620: (
        "지금은 불리한 형태로나마\n"
        "휴전을 얻어 낸 \x1bCA우지야스\x1bCZ가 벌써 다음 행동으로\n"
        "옮겼다는 사실에 주목해야 할 것이다……"
    ),
    3621: (
        "좋아. 이쪽 전쟁은 끝났다!\n"
        "겉으로는 패배지만,\n"
        "\x1bCC가토\x1bCZ 땅 따위 잃어도 아깝지 않다!"
    ),
    3622: "기다려라…… \x1bCA쓰나시게\x1bCZ!\n곧 \x1bCC가와고에성\x1bCZ으로 달려가마!",
    3623: (
        "어느 여름날 밤―\n"
        "\x1bCA우지야스\x1bCZ는 가까운 이들과\n"
        "높은 누각에서 더위를 식히고 있었다."
    ),
    3624: "음, 무슨 소리가 들리는군.",
    3625: "여우 울음소리야.\n이 여름에 울다니.",
    3626: "그러게요……\n여우는 여름에 우는 짐승이 아닌데,\n흉사의 전조가 아니면 좋겠습니다……",
    3627: "이봐, 형님.\n재수 없는 말은 하지 말라고!",
    3628: "그렇군……\n그럼 이건 어떠냐?",
    3629: "이때,\n\x1bCA우지야스\x1bCZ가 다음과 같은 와카를 읊었다고 전해진다.",
    3630: (
        "\u3000\u3000\u3000여름이 왔구나, 소리 높여 우는 매미의 빈 껍질 옷.\n"
        "저마다 제 몸에 맞는 옷을 입어라."
    ),
    3631: "……?",
    3632: "역시 아버님, 훌륭한 와카입니다.",
    3633: "무슨 뜻이지?",
    3634: (
        "‘키쓰’와 ‘네’ 소리를 구절 사이에 나누었습니다.\n"
        "여름 여우의 불길한 울음을 여우에게 돌려보내,\n"
        "액운을 물리치려는 와카입니다."
    ),
    3635: "그렇군…… 잘 모르겠어.\n그래도 울음소리는 정말 멎었구나!",
    3636: "하지만……\n이 일로 여우가 아버님께 해코지하지 않으면 좋겠군요……",
    3637: "걱정거리는 정말 끝이 없구나……",
    3638: (
        "\x1bCA호조 우지야스\x1bCZ는 이처럼 무략뿐 아니라,\n"
        "와카에도 통달한 문인이자 독서가였으며,\n"
        "역사서 ‘아즈마카가미’도 소장했다고 전해진다."
    ),
    3639: (
        "바로 이런 \x1bCA우지야스\x1bCZ야말로\n"
        "‘겉은 문, 속은 무’라 평가받은,\n"
        "문무를 겸비한 명장이었다."
    ),
    3640: (
        "덧붙여 이 이야기에는 뒷이야기가 있다.\n"
        "\x1bCA우지야스\x1bCZ 사후, \x1bCA우지마사\x1bCZ는 여우의 저주를 걱정하여\n"
        "‘\x1bCA호조\x1bCZ 이나리’ 신사를 세웠다."
    ),
    3641: (
        "전하는 말에 따르면,\n"
        "\x1bCA호조\x1bCZ 이나리 신사에 있는 개구리 모양의 ‘개구리 바위’는\n"
        "\x1bCC오다와라\x1bCZ에 위기가 닥치면 반드시 운다고 한다."
    ),
    3642: (
        "\x1bCA다메카게\x1bCZ 시절의 \x1bCB에치고 나가오 가문\x1bCZ은,\n"
        "주가인 \x1bCB에치고 우에스기 가문\x1bCZ의 위세를 뛰어넘어\n"
        "\x1bCC에치고\x1bCZ 제일의 세력으로 군림했다."
    ),
    3643: (
        "하지만 \x1bCA다메카게\x1bCZ는 그 과정에서 \x1bCB우에스기\x1bCZ 가신과\n"
        "\x1bCC에치고\x1bCZ의 고쿠진들과 여러 차례 충돌하여,\n"
        "모두의 지지를 받지는 못했다."
    ),
    3644: (
        "그 모순은 \x1bCA다메카게\x1bCZ가 세상을 떠나고,\n"
        "장남 \x1bCA하루카게\x1bCZ가 뒤를 이은 뒤 폭발하여,\n"
        "\x1bCB나가오 가문\x1bCZ을 이탈하는 자도 나타나기 시작했다……"
    ),
    3645: (
        "으음, 어째서 모두 내게 이를 드러내는가……\n"
        "나는 아무 짓도 하지 않았는데.\n"
        "돌아가신 아버지를 원망할 수밖에 없는가……?"
    ),
    3646: (
        "병약하고 우유부단한 \x1bCA하루카게\x1bCZ로는\n"
        "이 사태에 대처할 수 없다……\n"
        "뜻있는 가신들은 그런 걱정을 품었다."
    ),
    3647: (
        "그들의 기대를 한 몸에 받은 이는\n"
        "\x1bCA하루카게\x1bCZ와 나이 차가 큰 아우이자, \x1bCC린센지\x1bCZ에서\n"
        "불도를 닦고 있던 \x1bCA도라치요\x1bCZ였다."
    ),
    3648: (
        "\x1bCA도라치요\x1bCZ 님은 수행 중이지만 문무에 뛰어나,\n"
        "장수의 그릇을 지녔다고 들었습니다.\n"
        "부디 \x1bCB나가오 가문\x1bCZ의 위기를 구해 주십시오!"
    ),
    3649: (
        "저는 \x1bCA덴시쓰 선사\x1bCZ의 제자로서,\n"
        "이 \x1bCC린센지\x1bCZ에서 생을 마칠 생각입니다……\n"
        "무사가 될 마음은 없습니다."
    ),
    3650: (
        "갈! \x1bCA도라치요\x1bCZ여!\n"
        "나라 사람들의 기대에 부응하는 것도\n"
        "슈고다이 가문에 태어난 그대의 숙명이다."
    ),
    3651: "선사님……",
    3652: "전란의 시대를 끝내고 백성에게 평안을 가져오는 것도,\n불도가 말하는 중생제도인 것이다.",
    3653: (
        "게다가 형님인 \x1bCA하루카게\x1bCZ 공도\n"
        "고쿠진들의 반란으로 마음 아파하고 계신다.\n"
        "피를 나눈 아우인 네가 돕지 않고 어찌하겠느냐!"
    ),
    3654: (
        "알겠습니다…… 선사님.\n"
        "불초 \x1bCA도라치요\x1bCZ, 불도를 떠나\n"
        "무사로서 형님을 돕는 길을 택하겠습니다."
    ),
    3655: "오오!\n그럼 당장 원복 준비를 시작하자꾸나!",
    3656: (
        "가신들의 청을 받아 \x1bCA도라치요\x1bCZ는 원복하고, \x1bCA가게토라\x1bCZ라\n"
        "이름 지어 형 \x1bCA하루카게\x1bCZ를 섬기게 되었다.\n"
        "훗날의 \x1bCA우에스기\x1bCZ 겐신, 바로 그였다―"
    ),
    3657: (
        "원복한 지 얼마 지나지 않아,\n"
        "\x1bCA가게토라\x1bCZ는 \x1bCC도치오성\x1bCZ을 공격한 고쿠진 반란군을\n"
        "신속히 진압하며 군재의 편린을 보였다."
    ),
    3658: "참으로 훌륭한 지휘…… 저것이 첫 출진이라니!\n마치 비사문천이 현세에 나타난 듯하군……",
    3659: (
        "유약한 \x1bCA하루카게\x1bCZ와 정반대로, \x1bCA가게토라\x1bCZ의 과감한\n"
        "싸움 솜씨는 널리 알려졌고,\n"
        "아버지 \x1bCA다메카게\x1bCZ의 모습을 겹쳐 본 이도 적지 않았다."
    ),
    3660: (
        "차라리 \x1bCA하루카게\x1bCZ 님이 아니라,\n"
        "\x1bCA가게토라\x1bCZ 님이 \x1bCB나가오 가문\x1bCZ의 당주라면―\n"
        "……아니, 지금은 말하지 않겠다."
    ),
    3661: "훗날 군신이라 불린 사내의,\n전쟁으로 점철된 삶은 이렇게 막을 올렸다.",
    3662: (
        "\x1bCA모리 다카모토\x1bCZ는 \x1bCA모리 모토나리\x1bCZ와 \x1bCA묘큐\x1bCZ 사이에서 태어난,\n"
        "\x1bCB모리 가문\x1bCZ의 후계자였다."
    ),
    3663: (
        "\x1bCA다카모토\x1bCZ는 원복과 거의 동시에 \x1bCB오우치 가문\x1bCZ의 인질이 되어,\n"
        "\x1bCC야마구치\x1bCZ의 \x1bCC오우치관\x1bCZ에서\n"
        "약 3년을 보냈다."
    ),
    3664: (
        "서쪽의 교토라 불리며,\n"
        "\x1bCA요시타카\x1bCZ의 공가 취향이 집약된 \x1bCC야마구치\x1bCZ에서\n"
        "감수성 예민한 시절을 보낸 \x1bCA다카모토\x1bCZ는,"
    ),
    3665: "높은 교양과 교토풍 취향을 익혀,\n\x1bCB모리 가문\x1bCZ으로 돌아왔다.",
    3666: "\x1bCB모리 가문\x1bCZ·\x1bCC다카모토 거성\x1bCZ―",
    3667: "\x1bCA다카모토\x1bCZ.",
    3668: "예.",
    3669: (
        "오늘부터 \x1bCA시지 히로요시\x1bCZ를 네 후견인으로 붙이겠다.\n"
        "그자의 말을 잘 듣고 정진하여,\n"
        "당주로서 부끄럽지 않은 장수가 되어라!"
    ),
    3670: "다, 당주 말씀이십니까……",
    3671: "무엇을 주눅 들어 하느냐!\n알겠느냐!",
    3672: "예, 예……\n알겠습니다!",
    3673: "그리고 \x1bCA다카모토\x1bCZ.\n요즘 예능에 빠져 있다더구나.",
    3674: "그건…… 예.\n\x1bCC야마구치\x1bCZ에서 배운 노가 그리워져서……",
    3675: "노와 예능이라……\n그런 유흥은 우리 무사에게 필요 없다!",
    3676: "오직 무략과 계략, 조략만이 중요하다.\n계책이 많으면 이기고 적으면 지는 것이 전쟁이다.\n이를 명심해라!",
    3677: "예……",
    3678: "알았으면 물러가라.\n\x1bCA히로요시\x1bCZ에게 인사하고 오도록!",
    3679: "예!\n그럼 물러가겠습니다.",
    3680: "후우……",
    3681: "…………",
    3682: "……조금 심하게 말했나?",
    3683: "아닙니다.\n\x1bCA다카모토\x1bCZ는 결코 약한 아이가 아닙니다.",
    3684: "반드시 당신의 가르침을 양식 삼아,\n훌륭한 장수로 자랄 것입니다.",
    3685: "그러면 좋겠다만……\n너를 닮아서인지,\n너무 착한 것이 탈이다.",
    3686: "어머,\n그건 저를 칭찬하시는 말씀인가요?",
    3687: "후…… 그래서 그 아이를 내버려 둘 수 없는 게다.\n……너를 내버려 둘 수 없는 것처럼.",
    3688: "후후……\n기쁜 말씀입니다.",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    3565: ["dynamic_dosan_name_requires_officer_overlay_review"],
    3572: ["kinai_term_requires_glossary_review"],
    3576: ["dynamic_shogun_name_requires_officer_overlay_review"],
    3583: ["shugodai_and_hokoshu_terms_require_glossary_review"],
    3586: ["oshoshu_term_requires_glossary_review"],
    3590: ["shishiki_and_isshiki_lineage_terms_require_review"],
    3595: ["soun_ujichika_relationship_requires_historical_review"],
    3599: ["yamanouchi_and_ogigayatsu_terms_require_glossary_review"],
    3603: ["kitsunebashi_reading_requires_glossary_review"],
    3619: ["kososun_alliance_term_requires_glossary_review"],
    3630: ["waka_wordplay_requires_specialist_review"],
    3638: ["azuma_kagami_term_requires_glossary_review"],
    3641: ["frog_stone_legend_requires_style_review"],
    3649: ["tenshitsu_name_reading_requires_glossary_review"],
    3657: ["tochio_castle_reading_requires_glossary_review"],
    3662: ["myokyu_name_reading_requires_glossary_review"],
    3669: ["shiji_hiroyoshi_name_reading_requires_glossary_review"],
    3673: ["sc_name_order_typo_resolved_against_jp_en"],
}


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
    ids = list(range(SCOPE_START, SCOPE_END + 1))
    if len(ids) != 124 or ids != sorted(TRANSLATIONS):
        raise ValueError("batch5 ids are not the exact 124 displayed entries")
    return ids


def event_for(entry_id: int) -> str:
    matches = [
        event["event_id"]
        for event in EVENTS
        if event["start_id"] <= entry_id <= event["end_id"]
    ]
    if len(matches) != 1:
        raise ValueError(f"id {entry_id} does not map to one batch5 event group")
    return str(matches[0])


def source_structure(text: str) -> dict[str, Any]:
    value = shared.source_structure(text)
    value["bracket_tokens"] = BRACKET_TOKEN_RE.findall(text)
    return value


def public_script_counts(text: str) -> dict[str, int]:
    return shared.public_script_counts(text)


def build(args: argparse.Namespace) -> dict[str, Any]:
    ids = selected_ids()
    loaded = {
        language: shared.shared.load_source(path, language)
        for language, path in {
            "SC": args.stock_sc,
            "JP": args.stock_jp,
            "EN": args.stock_en,
        }.items()
    }
    tables = {language: value[2] for language, value in loaded.items()}

    display_failures = [
        entry_id
        for entry_id in ids
        if len(
            {
                tables[language].texts[entry_id]
                for language in ("SC", "JP", "EN")
            }
        )
        == 1
    ]
    if display_failures:
        raise ValueError(
            f"batch5 range contains all-language shared internal keys: {display_failures}"
        )

    overlay_entries: list[dict[str, Any]] = []
    evidence_entries: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for entry_id in ids:
        source_sc = tables["SC"].texts[entry_id]
        replacement = TRANSLATIONS[entry_id]
        problems = common.invariant_mismatches(source_sc, replacement)
        source_tokens = BRACKET_TOKEN_RE.findall(source_sc)
        replacement_tokens = BRACKET_TOKEN_RE.findall(replacement)
        if source_tokens != replacement_tokens:
            problems.append(
                f"bracket_tokens: source={source_tokens!r}, ko={replacement_tokens!r}"
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
                "event_id": event_for(entry_id),
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
        "resource": "MSG_PK/SC/msgev.bin",
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
    common.validate_overlay_shape(overlay)

    boundary_ids = (
        3564,
        3565,
        3575,
        3576,
        3594,
        3595,
        3622,
        3623,
        3641,
        3642,
        3661,
        3662,
        3688,
        3689,
    )
    evidence = {
        "schema": "nobu16.kr.event-dialogue-alignment-evidence.v5",
        "batch_id": BATCH_ID,
        "resource": "msgev",
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "selected_entry_count": len(ids),
            "excluded_internal_entry_count": 0,
        },
        "alignment_basis": [
            "same_resource_role",
            "same_17910_entry_count",
            "same_numeric_string_ids",
            "manual_semantic_crosscheck_of_selected_entries",
            "no_all_language_shared_internal_keys_in_selected_range",
        ],
        "source_files": {
            language: {**SOURCE_PINS[language], "string_count": STRING_COUNT}
            for language in ("SC", "JP", "EN")
        },
        "event_groups": list(EVENTS),
        "boundary_anchors": [
            {
                "id": entry_id,
                "reference_hashes": {
                    language: common.text_hash(tables[language].texts[entry_id])
                    for language in ("SC", "JP", "EN")
                },
            }
            for entry_id in boundary_ids
        ],
        "excluded_internal_entries": [],
        "entry_count": len(ids),
        "entries": evidence_entries,
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.event-dialogue-review-index.v5",
        "batch_id": BATCH_ID,
        "quality_state": "draft_not_human_or_runtime_reviewed",
        "entry_count": len(ids),
        "entries": [
            {
                "id": entry_id,
                "event_id": event_for(entry_id),
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
    artifacts["overlay"] = write_json(
        out_root / "public" / OVERLAY_NAME, overlay, f"public/{OVERLAY_NAME}"
    )
    artifacts["alignment_evidence"] = write_json(
        out_root / "evidence" / EVIDENCE_NAME,
        evidence,
        f"evidence/{EVIDENCE_NAME}",
    )
    artifacts["review_index"] = write_json(
        out_root / "review" / REVIEW_NAME, review, f"review/{REVIEW_NAME}"
    )

    public_paths = {
        "overlay": out_root / "public" / OVERLAY_NAME,
        "alignment_evidence": out_root / "evidence" / EVIDENCE_NAME,
        "review_index": out_root / "review" / REVIEW_NAME,
    }
    source_free_scan = {
        name: public_script_counts(path.read_text(encoding="utf-8"))
        for name, path in public_paths.items()
    }
    if any(
        value != {"cjk_unified_count": 0, "kana_count": 0}
        for value in source_free_scan.values()
    ):
        raise ValueError("batch5 public artifact contains source-script text")

    visible_lengths = {
        entry_id: [
            len(common.ESC_RE.sub("", line))
            for line in TRANSLATIONS[entry_id].splitlines()
        ]
        for entry_id in ids
    }
    validation = {
        "schema": "nobu16.kr.event-dialogue-generation-validation.v5",
        "batch_id": BATCH_ID,
        "passed": True,
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "selected_entry_count": len(ids),
            "selected_ids_sha256": sha256(
                json.dumps(ids, separators=(",", ":")).encode("utf-8")
            ),
            "excluded_internal_entry_count": 0,
            "excluded_internal_ids_sha256": sha256(b"[]"),
        },
        "source_alignment": {
            "languages": ["SC", "JP", "EN"],
            "string_count_each": STRING_COUNT,
            "selected_reference_hash_count": len(ids) * 3,
            "manual_semantic_crosschecks": len(ids),
        },
        "replacement_invariants": {
            "checked": len(ids),
            "failures": 0,
            "custom_bracket_placeholder_checks": len(ids),
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "edge_whitespace",
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
        "layout_heuristic": {
            "max_authored_line_codepoints_excluding_esc": max(
                length for lengths in visible_lengths.values() for length in lengths
            ),
            "entries_over_32": [
                entry_id
                for entry_id, lengths in visible_lengths.items()
                if max(lengths) > 32
            ],
            "runtime_layout_review_required": True,
        },
        "font_integration": {
            "state": "deferred_not_computed",
            "current_font_or_installer_must_not_include_batch5": True,
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
            "existing_v01_v02_v03_v04_artifacts_modified": False,
        },
    }
    artifacts["generation_validation"] = write_json(
        out_root / VALIDATION_NAME, validation, VALIDATION_NAME
    )
    return {"out_root": out_root, "entry_count": len(ids), "artifacts": artifacts}


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
