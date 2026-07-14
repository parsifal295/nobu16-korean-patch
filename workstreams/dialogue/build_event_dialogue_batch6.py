#!/usr/bin/env python3
"""Build source-free Korean historical event dialogue batch6 (3689-3818)."""

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
import build_event_dialogue_batch5 as shared  # noqa: E402


BATCH_ID = "msgev_historical_events_3689_3818.v0.6"
OVERLAY_NAME = "msgev_ko_historical_events_3689_3818.v0.6.json"
EVIDENCE_NAME = "alignment_evidence.v0.6.json"
REVIEW_NAME = "review_index.v0.6.json"
VALIDATION_NAME = "validation.v0.6.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 3689
SCOPE_END = 3818
EXCLUDED_INTERNAL_IDS: tuple[int, ...] = ()
BRACKET_TOKEN_RE = re.compile(r"\[[a-z0-9_]+\]")

EVENTS = (
    {
        "event_id": "kawagoe_night_battle",
        "title_ko": "가와고에 야전",
        "start_id": 3689,
        "end_id": 3706,
        "selected_count": 18,
    },
    {
        "event_id": "nobunaga_coming_of_age",
        "title_ko": "오다 노부나가의 원복",
        "start_id": 3707,
        "end_id": 3709,
        "selected_count": 3,
    },
    {
        "event_id": "yoshiteru_shogunate",
        "title_ko": "제13대 쇼군과 막부 재흥의 꿈",
        "start_id": 3710,
        "end_id": 3737,
        "selected_count": 28,
    },
    {
        "event_id": "ikoma_kitsuno_romance",
        "title_ko": "노부나가와 기쓰노",
        "start_id": 3738,
        "end_id": 3763,
        "selected_count": 26,
    },
    {
        "event_id": "nagao_succession",
        "title_ko": "나가오 가문의 당주 교체",
        "start_id": 3764,
        "end_id": 3798,
        "selected_count": 35,
    },
    {
        "event_id": "raikirimaru_legend",
        "title_ko": "라이키리마루 전승",
        "start_id": 3799,
        "end_id": 3818,
        "selected_count": 20,
    },
)

TRANSLATIONS: dict[int, str] = {
    3689: (
        "\x1bCA호조 우지쓰나\x1bCZ의 죽음을 계기로, 억눌려 있던\n"
        "\x1bCC스루가\x1bCZ의 \x1bCA이마가와 요시모토\x1bCZ가 움직이기 시작했다."
    ),
    3690: (
        "\x1bCA요시모토\x1bCZ의 조략으로 \x1bCB야마노우치 우에스기 가문\x1bCZ과,\n"
        "\x1bCB오기야쓰 우에스기 가문\x1bCZ·\x1bCB고가 아시카가 가문\x1bCZ이\n"
        "함께 봉기해 \x1bCC가와고에성\x1bCZ을 포위했다."
    ),
    3691: (
        "정작 \x1bCA요시모토\x1bCZ는 \x1bCA[b1251]\x1bCZ 공의 중재로,\n"
        "염원하던 \x1bCC가토\x1bCZ 탈환에 성공하자\n"
        "곧바로 \x1bCB호조\x1bCZ와 화친했지만……"
    ),
    3692: (
        "\x1bCA요시모토\x1bCZ에게 부추김을 받은 \x1bCB양 우에스기 가문\x1bCZ과 \x1bCB고가쿠보\x1bCZ는\n"
        "여전히 \x1bCC가와고에성\x1bCZ을 포위하고 있었다.\n"
        "성을 지킨 이는 \x1bCA우지야스\x1bCZ의 매제 \x1bCA[bm790]\x1bCZ 공이었다……"
    ),
    3693: "8만이나 데려오다니……\n우리도 참 미움을 샀군.",
    3694: (
        "\x1bCC가와고에성\x1bCZ을 지키는 \x1bCA우지야스\x1bCZ의 매제 \x1bCA[bm790]\x1bCZ 공은\n"
        "대군의 맹공을 필사적으로 버텼고,\n"
        "농성전은 이미 몇 달째 이어지고 있었다."
    ),
    3695: "\x1bCC스루가\x1bCZ로 간 형님은 어찌 되었을까.\n승산이 있다고 했지만……",
    3696: "그리고―",
    3697: "일기당천의 용사들이여!\n우리 \x1bCB호조\x1bCZ의 흥망이 이 한판에 달렸다!",
    3698: "가자, 포위군을 짓밟아라!\n전군, 나를 따르라!!",
    3699: (
        "뭐라, \x1bCA호조 우지야스\x1bCZ가 왔다고!?\n"
        "어째서냐? 그자는 \x1bCC가토\x1bCZ에서\n"
        "\x1bCA이마가와 요시모토\x1bCZ와 싸우고 있지 않았나!"
    ),
    3700: (
        "\x1bCB호조 가문\x1bCZ 제3대 당주 \x1bCA호조 우지야스\x1bCZ가 건곤일척으로\n"
        "감행한 야습은 훌륭히 성공했다.\n"
        "\x1bCB우에스기\x1bCZ·\x1bCB아시카가\x1bCZ 포위군은 큰 혼란에 빠졌다."
    ),
    3701: "좋아! 기다렸다고, 형님!",
    3702: "성문을 열어라! 반격이다!\n성안에서도 출격한다!",
    3703: (
        "거기에 \x1bCC가와고에성\x1bCZ 안에서 뛰쳐나온\n"
        "‘지키하치만’의 맹장 \x1bCA[bm790]\x1bCZ 공의 군대까지 가세해,\n"
        "협공을 받은 포위군은 완전히 무너졌다."
    ),
    3704: (
        "\x1bCB오기야쓰 우에스기 가문\x1bCZ 당주 \x1bCA우에스기 도모사다\x1bCZ는 전사했다.\n"
        "\x1bCB야마노우치 우에스기 가문\x1bCZ 당주 \x1bCA우에스기 노리마사\x1bCZ와\n"
        "고가쿠보 \x1bCA아시카가 하루우지\x1bCZ는 군대를 버리고 달아났다."
    ),
    3705: (
        "이 압도적인 전과로 예부터\n"
        "\x1bCC간토\x1bCZ를 지배해 온 세 가문의 세력은 크게 쇠퇴했다."
    ),
    3706: (
        "후세에 ‘가와고에 야전’이라 불린\n"
        "이 기적적인 승리는 \x1bCB호조 가문\x1bCZ을\n"
        "\x1bCC간토\x1bCZ의 패자로 밀어 올렸다……"
    ),
    3707: (
        "\x1bCA오다 노부히데\x1bCZ의 적장자 \x1bCA깃포시\x1bCZ,\n"
        "이제는 \x1bCA사부로 노부나가\x1bCZ.\n"
        "그 사내가 막 원복 의식을 마쳤다."
    ),
    3708: (
        "평소 천하의 멍청이라 평가받은 것은,\n"
        "보통 사람은 생각조차 못 할\n"
        "커다란 뜻을 가슴에 품었기 때문이었다……"
    ),
    3709: (
        "바로 이 순간,\n"
        "\x1bCA오다 노부나가\x1bCZ라는 사내가\n"
        "난세에 풀려났다."
    ),
    3710: (
        "전국시대에 들어서자,\n"
        "간레이가 쇼군을 보좌해 정무를 맡던 틀이 무너졌다.\n"
        "쇼군 \x1bCB아시카가 가문\x1bCZ과 간레이 \x1bCB호소카와 가문\x1bCZ도 분열했다……"
    ),
    3711: (
        "그 분열로 여러 차례 대립자들과 싸우며,\n"
        "교토 입성과 퇴거를 되풀이한 이가\n"
        "제12대 쇼군 \x1bCA아시카가 요시하루\x1bCZ였다."
    ),
    3712: (
        "이해에 \x1bCB호소카와 게이초 가문\x1bCZ의 가독을 둘러싸고,\n"
        "\x1bCA하루모토\x1bCZ와 \x1bCA우지쓰나\x1bCZ의 양 \x1bCB호소카와 진영\x1bCZ이 격돌해,\n"
        "\x1bCA요시하루\x1bCZ는 다시 교토를 떠나야 했다."
    ),
    3713: (
        "\x1bCA요시하루\x1bCZ는 적장자 \x1bCA기쿠도마루\x1bCZ를 데리고,\n"
        "\x1bCC단바\x1bCZ를 거쳐 \x1bCC오미\x1bCZ의 \x1bCC구쓰키다니\x1bCZ로 달아났다.\n"
        "거기서 \x1bCA기쿠도마루\x1bCZ를 원복해 \x1bCA[bm75]\x1bCZ 공으로 개명했다."
    ),
    3714: (
        "\x1bCA요시하루\x1bCZ는 11세에 쇼군직에 오른 뒤,\n"
        "25년간 거듭된 전쟁에 지쳐\n"
        "더는 쇼군직에 아무 미련도 없었다……"
    ),
    3715: (
        "\x1bCA요시하루\x1bCZ는 자신처럼 11세에 원복한 아들에게\n"
        "쇼군 자리를 물려주었다.\n"
        "\x1bCA[bm75]\x1bCZ 공은 무로마치 막부 제13대 쇼군에 올랐다."
    ),
    3716: "\x1bCA[bm75]\x1bCZ 님,\n쇼군 취임을 진심으로 축하드립니다.",
    3717: "\x1bCA[bm1773]\x1bCZ 공인가……\n우리 사이에 딱딱한 인사는 필요 없다.",
    3718: "그보다!\n천하를 위해, 막부를 위해,\n앞으로 더욱 힘써 주기를 기대하마!",
    3719: "예! 맡겨 주십시오!",
    3720: (
        "\x1bCA[bm1773]\x1bCZ 공, 아버님도 나와 마찬가지로\n"
        "막부의 옛 위광을 되찾고자\n"
        "힘을 다하셨지만 이루지 못했다."
    ),
    3721: "그 이유를 아느냐?",
    3722: "……아닙니다. 어째서입니까?",
    3723: "간단하다.\n힘이 부족했기 때문이다.\n막부의 적을 치고 억누를 힘이 말이다!",
    3724: "힘 말씀이십니까……",
    3725: "이 난세에는 힘없는 자는 멸망할 뿐이다……\n너와 함께 검술을 배우는 것도 그 때문이다.",
    3726: "물론,\n검술만으로 막부를 강하게 만들 수 있다고는\n생각하지 않는다.",
    3727: "하지만,\n무가를 이끄는 쇼군부터 강하지 않으면\n막부도 강해질 수 없다!",
    3728: "과연 그렇습니다.",
    3729: (
        "강한 쇼군이 되어,\n"
        "강한 막부를 다시 한번 되살리겠다……\n"
        "\x1bCA[bm1773]\x1bCZ 공, 내가 반드시 이루어 내마!"
    ),
    3730: "이 \x1bCA[bm1773]\x1bCZ,\n목숨을 걸고 쇼군을 돕겠습니다!",
    3731: "(그렇게 말하기는 했지만……\n 막부의 쇠퇴는,\n 이제 힘으로도 어찌할 수 없다.)",
    3732: "(조용히 유능한 자를 요직에 앉히고,\n 때를 기다리는 편이 나으련만……\n 그런 수완을 쓰실 분은 아니지.)",
    3733: "(그럼 나는 앞으로 어찌해야 할까……)",
    3734: (
        "\x1bCA아시카가 요시하루\x1bCZ가 쇼군 자리를 물려준 까닭은,\n"
        "\x1bCA[bm75]\x1bCZ 공이 자신이 취임했던 나이에\n"
        "이르렀기 때문만은 아니었다……"
    ),
    3735: (
        "자신이 늙기 전에 아들을 뒤에서 보좌하며,\n"
        "쇼군으로 키우려는\n"
        "뜻도 있었다고 여겨진다."
    ),
    3736: (
        "훗날 \x1bCA[bm75]\x1bCZ 공은 ‘검성’ \x1bCA쓰카하라 보쿠덴\x1bCZ에게 배워,\n"
        "역대 쇼군을 뛰어넘는 검술을 지니게 되었다."
    ),
    3737: "하지만 그 때문에 힘을 지나치게 믿었고,\n막부의 존립은 더욱 위태로워졌다……",
    3738: (
        "\x1bCC오와리\x1bCZ에 \x1bCB이코마 가문\x1bCZ이라는 토호가 있었다.\n"
        "당주 \x1bCA이에무네\x1bCZ는 무사이면서 장사도 했고,\n"
        "그 저택에는 수많은 사람이 드나들었다."
    ),
    3739: "다른 나라 사람이 많이 드나든다는 것은,\n그만큼 많은 정보도 모인다는 뜻이다.",
    3740: (
        "새것을 좋아하고 \x1bCC오와리\x1bCZ 한 나라를 넘어\n"
        "천하를 바라보던 \x1bCB오다 가문\x1bCZ의 젊은 주군 \x1bCA노부나가\x1bCZ도,\n"
        "\x1bCC이코마 저택\x1bCZ에 자주 머물렀다고 한다."
    ),
    3741: (
        "하지만 \x1bCA노부나가\x1bCZ의 목적은 정보뿐이 아니었다.\n"
        "이 저택을 찾는 데는\n"
        "또 다른 이유가 있었다……"
    ),
    3742: "이런, 이런……\n\x1bCA사부로\x1bCZ 님, 어서 오십시오.",
    3743: "음!\n지금 다른 나라에서 온 손님 중에,\n재미있는 사람은 묵고 있지 않나?",
    3744: "요즘은 여행 상인도 적어서,\n저희도 따분할 지경입니다……",
    3745: "그런가, 아쉽군.\n다른 나라 사람과의 이야기는 다음으로 미루지.\n그런데…… 자네 딸은 집에 있나?",
    3746: "아하……\n오늘도 그쪽이 목적이셨군요?",
    3747: "아니, 뭐 그런 건 아니지만……\n그래서 있나, 없나!",
    3748: "있습니다, 있고말고요.\n이봐, \x1bCA오다\x1bCZ의 젊은 주군께서 오셨다!\n어서 나와 맞이하지 못할까!",
    3749: (
        "\x1bCA이코마 이에무네\x1bCZ에게는 딸이 여럿 있었는데,\n"
        "그중 둘째 딸은 이름난 미인이었고,\n"
        "\x1bCA노부나가\x1bCZ가 저택을 찾는 이유 중 하나였다."
    ),
    3750: "도련님, 또 오셨군요.\n평안하신지요……",
    3751: "또 와 버렸구나.\n너무 자주 오면 소문이 날 테니,\n얼굴을 가리고 왔다만.",
    3752: "이제 성에서 여기까지 오가는 것도 지쳤다.\n차라리 내 성으로 오지 않겠느냐?",
    3753: "놀리지 마십시오…… 저처럼 친정으로 돌아온 여자가\n어찌 도련님 곁에 오르겠습니까……\n황공한 일입니다.",
    3754: "이 여인은 과거 \x1bCB도타 가문\x1bCZ에 시집갔다가,\n남편과 사별하고 친정으로 돌아온 사연이 있었다.",
    3755: "게다가 도련님은 조만간,\n\x1bCC미노\x1bCZ에서 공주를 맞이하시지요?\n다른 나라 사람들도 이야기하더군요.",
    3756: "……모른다. 아버지가 멋대로 정한 혼담이다.\n\x1bCC미노\x1bCZ의 무리와 화친하기 위해서지.\n그런 일에 내가 따를 의리는 없다.",
    3757: "그런 말씀은 마십시오……\n분명 아름다운 공주일 겁니다.",
    3758: "글쎄다. 독사 같은 사내의 딸이니까.\n게다가 그쪽도 친정으로 돌아온 몸이라는 소문이 있다.",
    3759: "부모가 정한 신부도 신부다. 혼례도 올리겠지.\n하지만 내가 진정 곁에 두고 싶은 사람은\n바로 너다.",
    3760: "도련님……",
    3761: "이 여인의 본명은 전해지지 않지만,\n후세에 ‘\x1bCA기쓰노\x1bCZ’라는 이름이 남았다.",
    3762: (
        "정실 \x1bCA노히메\x1bCZ를 맞기 전부터 \x1bCA노부나가\x1bCZ와 밀회를 거듭한\n"
        "이 여인에게, \x1bCA노부나가\x1bCZ의 아명 ‘\x1bCA깃포시\x1bCZ’에서\n"
        "한 글자를 따 이름을 붙였다고도 볼 수 있다."
    ),
    3763: "결국 \x1bCA노부나가\x1bCZ는 훗날 \x1bCA기쓰노\x1bCZ와의 사이에서,\n적장자를 비롯한 세 아이를 두게 된다……",
    3764: (
        "병약한 \x1bCA하루카게\x1bCZ가 \x1bCB나가오 가문\x1bCZ의 당주가 된 뒤,\n"
        "국내 유력 무사들은 \x1bCA하루카게\x1bCZ에게 불복해 반란을 거듭했다."
    ),
    3765: (
        "우유부단한 \x1bCA하루카게\x1bCZ는 이 사태에 전혀 대처하지 못해,\n"
        "나이 차가 큰 아우 \x1bCA[bm1448]\x1bCZ 공에게만\n"
        "반란군 진압을 맡겼다."
    ),
    3766: (
        "\x1bCA[bm1448]\x1bCZ 공의 싸움은 막 첫 출진을 마친\n"
        "소년의 것이라고는 믿을 수 없었고,\n"
        "사람들은 피어난 군재에 혀를 내둘렀다."
    ),
    3767: (
        "예전부터 많은 \x1bCB나가오\x1bCZ 가신은\n"
        "\x1bCA하루카게\x1bCZ의 통치에 불만을 품었고,\n"
        "\x1bCA[bm1448]\x1bCZ 공이 당주에 오르기를 바라게 되었지만―"
    ),
    3768: "거절한다! 내가 무사가 된 건 오직 형님을 돕기 위해서다!\n형님을 제치고 당주가 될 수는 없다……",
    3769: "하지만 \x1bCA하루카게\x1bCZ 님으로는\n더는 \x1bCA나가오\x1bCZ 가문을 이끌 수 없습니다!",
    3770: "\x1bCA[bm1448]\x1bCZ 님,\n부디 저희 뜻을 헤아리시어,\n\x1bCB나가오 가문\x1bCZ의 당주가 되어 주십시오!",
    3771: "끈질기구나!\n그런 망언을 계속한다면,\n나는 당장 \x1bCC린센지\x1bCZ로 돌아가 수행하겠다!",
    3772: "\x1bCA도라치요\x1bCZ여!\n절은 도피처로 삼는 곳이 아니다.",
    3773: "선사님! 제 말은 거짓이 아닙니다.\n저는 지금도 선사님의 제자로서,\n\x1bCC린센지\x1bCZ에서 일생을 마칠 각오가……",
    3774: "그렇게는 안 된다. 사람에게는 타고난 재주가 있다.\n너는 형님에게 없는 자질을 지녔음을,\n모두가 인정하고 있다……",
    3775: "게다가 계속 당주로 일한다면 병으로 고생하는\n\x1bCA하루카게\x1bCZ 공에게 더 큰 부담이 간다.\n오히려 형님을 괴롭히게 될 것이다.",
    3776: "피를 나눈 아우인 네가,\n형님을 고통에서 풀어 드려라……",
    3777: "알겠습니다…… 선사님.\n그것으로 형님을 구할 수 있다면,\n불초 \x1bCA[bm1448]\x1bCZ, 가시밭길을 걷겠습니다.",
    3778: "\x1bCA[bm1448]\x1bCZ 공이 당주 계승을 받아들이자,\n가신들은 마침내 \x1bCA하루카게\x1bCZ에게 은거를 요구했다.",
    3779: "\x1bCA하루카게\x1bCZ 님!\n저희 가신들이 아뢸 말씀이 있습니다.",
    3780: "무슨 일이냐?\n거리낌 없이 말해 보아라.",
    3781: "예! 부디……\n에치고 슈고다이와 \x1bCB나가오 가문\x1bCZ의 당주 자리를……\n\x1bCA[bm1448]\x1bCZ 님께 넘겨 주십시오!",
    3782: "\x1bCA[bm1448]\x1bCZ 공이라고……?\n설마 너희가……\n나를 배신하고 모반을 일으키려는 것이냐!",
    3783: "아닙니다. 모반이 아닙니다……\n\x1bCA하루카게\x1bCZ 님께서 \x1bCA[bm1448]\x1bCZ 공을 양자로 맞으시고,\n조용히 은거해 주시기를 바랄 뿐입니다.",
    3784: "은거라고……?\n허튼소리 마라!\n그게 모반이 아니면 무엇이냐!",
    3785: "본가의 주군인 에치고 슈고 \x1bCA우에스기 사다자네\x1bCZ 님도\n이 의견에 동의하셨습니다.",
    3786: "\x1bCA사다자네\x1bCZ 님까지……? 언제!\n너희…… 모의했구나!!",
    3787: "\x1bCA하루카게\x1bCZ 님, 조금 진정하십시오.",
    3788: "그대는…… \x1bCC린센지\x1bCZ의 \x1bCA덴시쓰 선사\x1bCZ?",
    3789: (
        "\x1bCA[bm1448]\x1bCZ 공의 스승이자 \x1bCC린센지\x1bCZ 주지로 신자가 많은\n"
        "\x1bCA덴시쓰 고이쿠\x1bCZ도 설득에 나서,\n"
        "\x1bCA하루카게\x1bCZ에게 은거를 거듭 권했다. 그리고……"
    ),
    3790: "알겠다…… 선사의 말이\n하나하나 가슴에 박혔다. 너희 조언대로\n당주 자리를…… \x1bCA[bm1448]\x1bCZ 공에게 넘기마.",
    3791: "잘 결단하셨습니다.\n앞으로는 편히 요양하십시오……",
    3792: "형님……\n이런 상황에 이르다니, 저는……",
    3793: "\x1bCA[bm1448]\x1bCZ 공! 당주의 길은 결코 쉽지 않다.\n하지만 너라면 할 수 있을 것이다.\n\x1bCB나가오 가문\x1bCZ을…… 부탁한다!",
    3794: "예!",
    3795: "\x1bCA나가오 하루카게\x1bCZ는 아우 \x1bCA[bm1448]\x1bCZ 공을 양자로 맞아,\n은거하고 \x1bCA[bm1448]\x1bCZ 공에게 당주 자리를 넘겼다.",
    3796: "병약한 \x1bCA하루카게\x1bCZ가 요양에 들어간 한편,\n\x1bCB나가오 가문\x1bCZ은 새 당주 아래 새로운 첫걸음을 내디뎠지만,\n모든 일이 평온하게 끝난 것은 아니었다.",
    3797: "\x1bCA하루카게\x1bCZ 공이 은거하다니 참으로 통탄할 일이다.\n\x1bCA[b1448]\x1bCZ 공은 대체 어떤 사내인가……",
    3798: (
        "\x1bCC에치고\x1bCZ에는 \x1bCA하루카게\x1bCZ를 지지한 유력자도 있었다.\n"
        "특히 \x1bCB우에다 나가오 가문\x1bCZ의 \x1bCA마사카게\x1bCZ와\n"
        "\x1bCA[bm1448]\x1bCZ 공 사이에는 미묘한 앙금이 남았다……"
    ),
    3799: "\x1bCA[b1730]\x1bCZ 공―\x1bCB오토모 가문\x1bCZ의 맹장이다.",
    3800: "두뇌가 명민하고 무용이 빼어났으며,\n인재를 키우고 백성을 아끼는 데 비할 자가 없었다.\n젊어서부터 수많은 전장에서 공을 세웠다.",
    3801: "어느 무더운 여름날,\n\x1bCA[bm1730]\x1bCZ 공이 큰 나무 아래에서 쉬고 있자,\n갑자기 비가 내리기 시작했다.",
    3802: "음? 비인가……?",
    3803: "이런,\n어느새 잠들었나 보군.",
    3804: "성으로 돌아가야 하지만 소나기인가……\n뭐, 곧 그치겠지.",
    3805: "……그때까지 한숨 더 자도 되겠군.\n지도리도 젖게 하고 싶지 않으니.",
    3806: "\x1bCA[bm1730]\x1bCZ 공은 아끼는 지도리 다치를 곁에 세우고,\n다시 큰 나무 아래에 몸을 누였다.\n연전의 피로가 그를 편안한 잠으로 이끌었다.",
    3807: "―바로 그때였다.",
    3808: "이 기괴한 빛은……!?",
    3809: "이 요괴 놈!\n내 칼을 받아라!",
    3810: "본래 벼락을 맞으면 목숨을 건질 수 없다.\n하지만 다행히 번개는 \x1bCA[bm1730]\x1bCZ 공이 아니라,\n조금 전까지 기대 있던 큰 나무에 떨어졌다.",
    3811: "그렇다 해도 벼락이 바로 곁에 떨어졌다.\n그 격렬한 충격에 \x1bCA[bm1730]\x1bCZ 공조차\n의식이 흐려져 환상을 보았다.",
    3812: "방금 나는 분명히 베었다…… 뇌신을!",
    3813: "그 벼락을 맞고도 손발이 조금\n저릴 뿐, 상처는 하나도 없다.\n그것이 증거다!",
    3814: "뇌신을 벨 수 있었던 것은\n이 지도리 다치 덕분이다……\n음!?",
    3815: "하얗게 빛나는군…… 그래.\n이제부터 ‘라이키리마루’라 이름 짓겠다!\n앞으로도 이 \x1bCA[bm1730]\x1bCZ 공을 지켜 다오!",
    3816: "비도 그쳤나……\n음? 다리에 힘이 들어가지 않는군.\n이 나도 놀라 주저앉은 것인가?",
    3817: "낙뢰의 영향인지, 이후 \x1bCA[bm1730]\x1bCZ 공은\n다리를 쓰기 어려워져,\n가마를 타고 전장에 나갔다고 전해진다.",
    3818: "하지만 그 투지는 만년까지 쇠하지 않았고,\n사람들은 이 사건과 용맹한 모습 때문에\n\x1bCA[bm1730]\x1bCZ 공을 ‘뇌신’이라 부르며 두려워했다……",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    3692: ["tsunashige_relationship_resolved_against_jp_en"],
    3703: ["jikihachiman_title_requires_glossary_review"],
    3706: ["kawagoe_night_battle_term_requires_glossary_review"],
    3707: ["kipposhi_and_saburo_name_readings_require_review"],
    3712: ["hosokawa_keicho_term_requires_glossary_review"],
    3713: ["kutsukidani_reading_requires_glossary_review"],
    3716: ["dynamic_yoshiteru_name_requires_officer_overlay_review"],
    3717: ["dynamic_retainer_name_requires_officer_overlay_review"],
    3736: ["tsukahara_bokuden_name_reading_requires_review"],
    3738: ["ikoma_iemune_name_reading_requires_review"],
    3761: ["kitsuno_name_reading_requires_glossary_review"],
    3764: ["echigo_shugodai_context_requires_glossary_review"],
    3771: ["rinsenji_reading_requires_glossary_review"],
    3785: ["uesugi_sadazane_name_reading_requires_review"],
    3789: ["tenshitsu_koiku_name_reading_requires_review"],
    3798: ["ueda_nagao_and_masakage_names_require_review"],
    3799: ["dynamic_otomo_warrior_identity_requires_officer_overlay_review"],
    3806: ["chidori_tachi_term_requires_glossary_review"],
    3815: ["raikirimaru_term_requires_glossary_review"],
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
    if len(ids) != 130 or ids != sorted(TRANSLATIONS):
        raise ValueError("batch6 ids are not the exact 130 displayed entries")
    return ids


def event_for(entry_id: int) -> str:
    matches = [
        event["event_id"]
        for event in EVENTS
        if event["start_id"] <= entry_id <= event["end_id"]
    ]
    if len(matches) != 1:
        raise ValueError(f"id {entry_id} does not map to one batch6 event group")
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
        language: shared.shared.shared.load_source(path, language)
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
            f"batch6 range contains all-language shared internal keys: {display_failures}"
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
        3688,
        3689,
        3706,
        3707,
        3709,
        3710,
        3737,
        3738,
        3763,
        3764,
        3798,
        3799,
        3818,
        3819,
    )
    evidence = {
        "schema": "nobu16.kr.event-dialogue-alignment-evidence.v6",
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
        "schema": "nobu16.kr.event-dialogue-review-index.v6",
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
        raise ValueError("batch6 public artifact contains source-script text")

    visible_lengths = {
        entry_id: [
            len(common.ESC_RE.sub("", line))
            for line in TRANSLATIONS[entry_id].splitlines()
        ]
        for entry_id in ids
    }
    validation = {
        "schema": "nobu16.kr.event-dialogue-generation-validation.v6",
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
            "current_font_or_installer_must_not_include_batch6": True,
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
            "root_readme_or_progress_modified": False,
            "existing_v01_v02_v03_v04_v05_artifacts_modified": False,
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
