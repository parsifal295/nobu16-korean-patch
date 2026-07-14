#!/usr/bin/env python3
"""Build source-free Korean historical event dialogue batch10 (4161-4279)."""

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
import build_event_dialogue_batch2 as source_shared  # noqa: E402
import build_event_dialogue_batch9 as shared  # noqa: E402


BATCH_ID = "msgev_historical_events_4161_4279.v0.10"
OVERLAY_NAME = "msgev_ko_historical_events_4161_4279.v0.10.json"
EVIDENCE_NAME = "alignment_evidence.v0.10.json"
REVIEW_NAME = "review_index.v0.10.json"
VALIDATION_NAME = "validation.v0.10.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 4161
SCOPE_END = 4279
EXCLUDED_INTERNAL_IDS: tuple[int, ...] = ()
BRACKET_TOKEN_RE = shared.BRACKET_TOKEN_RE

EVENTS = (
    {
        "event_id": "amago_shinguto_purge",
        "title_ko": "아마고 신구토 숙청",
        "start_id": 4161,
        "end_id": 4179,
        "selected_count": 19,
    },
    {
        "event_id": "itsukushima_decisive_battle_preparations",
        "title_ko": "이쓰쿠시마 결전 준비",
        "start_id": 4180,
        "end_id": 4209,
        "selected_count": 30,
    },
    {
        "event_id": "taigen_sessai_death",
        "title_ko": "다이겐 셋사이의 죽음",
        "start_id": 4210,
        "end_id": 4230,
        "selected_count": 21,
    },
    {
        "event_id": "nobunaga_moves_to_kiyosu",
        "title_ko": "노부나가의 기요스 천거",
        "start_id": 4231,
        "end_id": 4235,
        "selected_count": 5,
    },
    {
        "event_id": "saito_father_son_feud_escalates",
        "title_ko": "사이토 부자의 불화 격화",
        "start_id": 4236,
        "end_id": 4249,
        "selected_count": 14,
    },
    {
        "event_id": "terutora_becomes_fushikian_kenshin",
        "title_ko": "데루토라, 후시키안 겐신으로 개명",
        "start_id": 4250,
        "end_id": 4257,
        "selected_count": 8,
    },
    {
        "event_id": "battle_of_nagaragawa",
        "title_ko": "나가라강 전투",
        "start_id": 4258,
        "end_id": 4279,
        "selected_count": 22,
    },
)

TRANSLATIONS: dict[int, str] = {
    4161: (
        "\x1bCB아마고 가문\x1bCZ은 이즈모 슈고다이였던 \x1bCA쓰네히사\x1bCZ 대에,\n"
        "\x1bCC이즈모\x1bCZ를 비롯한 주변국으로 세력을 넓혀,\n"
        "튼튼한 기반을 갖춘 전형적인 센고쿠 다이묘가 되었다."
    ),
    4162: (
        "\x1bCA쓰네히사\x1bCZ의 적장자 \x1bCA마사히사\x1bCZ가 요절하자,\n"
        "손자 \x1bCA[bm128]\x1bCZ가 잇고, \x1bCA쓰네히사\x1bCZ는\n"
        "차남 \x1bCA구니히사\x1bCZ를 적손 \x1bCA[bm128]\x1bCZ의 후견인으로 삼았다."
    ),
    4163: (
        "무공이 뛰어난 \x1bCA구니히사\x1bCZ와 그 아들 \x1bCA사네히사\x1bCZ는\n"
        "종가마저 능가하는 세력으로 자라,\n"
        "어느덧 ‘\x1bCB신구토\x1bCZ’라 불리게 되었다."
    ),
    4164: (
        "\x1bCB신구토\x1bCZ의 \x1bCA구니히사\x1bCZ 님과 \x1bCA사네히사\x1bCZ 님의 행동은\n"
        "도저히 눈뜨고 보기 어렵습니다. 너무 거만해,\n"
        "다른 가신들의 불만이 잇따르고 있습니다."
    ),
    4165: "흠…… 숙부님들은 아무래도,\n나를 주군으로 여기지 않는 모양이군.",
    4166: (
        "그대로 두어서는\n"
        "가신들에게 본보기가 서지 않습니다.\n"
        "무슨 대책을 세우시겠습니까?"
    ),
    4167: (
        "\x1bCB신구토\x1bCZ 휘하에는 국인도 많습니다.\n"
        "섣불리 멀리하면 독립할 수도 있으니……\n"
        "어찌해야 좋을지."
    ),
    4168: (
        "(이럴 때 \x1bCA모리 모토나리\x1bCZ라면……\n"
        "　어떤 수를 쓰려나.)"
    ),
    4169: (
        "수년간 \x1bCB아마고 가문\x1bCZ과 여러 번 창을 맞댄\n"
        "\x1bCA모리 모토나리\x1bCZ는 모장으로 명성이 높았고,\n"
        "적이지만 \x1bCA[bm128]\x1bCZ도 그 재능에 혀를 내둘렀다……"
    ),
    4170: (
        "좋아…… 결정했다!\n"
        "\x1bCA모리\x1bCZ와의 싸움에 대비하려면 지금은\n"
        "가문의 결속을 다져야 할 때다."
    ),
    4171: (
        "\x1bCA[bm128]\x1bCZ는 \x1bCA구니히사\x1bCZ를 \x1bCC갓산토다성\x1bCZ으로 불러,\n"
        "등성길에 자객을 보내 습격하게 했다."
    ),
    4172: "뭐냐!?\n무, 무슨 짓이냐……!\n크윽!",
    4173: (
        "어, 어리석구나…… \x1bCA[bm128]\x1bCZ!\n"
        "\x1bCB신구토\x1bCZ를 없애면 \x1bCA아마고\x1bCZ가 무사할 줄 아느냐……!\n"
        "크아악!!"
    ),
    4174: (
        "\x1bCA구니히사\x1bCZ가 죽었다는 소식에 아들 \x1bCA사네히사\x1bCZ는\n"
        "종가와 싸울 각오로 \x1bCB신구토\x1bCZ 저택에 틀어박혔으나,\n"
        "전세가 기울자 곧 자결했다."
    ),
    4175: (
        "이젠 늦었나. \x1bCA[bm128]\x1bCZ 녀석, 제법이군……\n"
        "하지만 갓 태어난 내 아이만큼은\n"
        "어떻게든 달아나게 해야 한다……"
    ),
    4176: (
        "이때 \x1bCA사네히사\x1bCZ의 어린 아들은 \x1bCA[bm128]\x1bCZ 측 추격을 피해\n"
        "\x1bCC교토\x1bCZ로 올라가 \x1bCC도후쿠지\x1bCZ에서 출가했다.\n"
        "훗날의 \x1bCA가쓰히사\x1bCZ였다."
    ),
    4177: (
        "전횡을 일삼았다지만,\n"
        "친족을 없애는 일은 뒷맛이 쓰군.\n"
        "그래도 이제 \x1bCA아마고\x1bCZ는 하나로 뭉치겠지……"
    ),
    4178: (
        "\x1bCB아마고\x1bCZ 가문의 불온 세력 \x1bCB신구토\x1bCZ는 괴멸했다.\n"
        "하지만 \x1bCB신구토\x1bCZ 숙청은 \x1bCA아마고\x1bCZ에게\n"
        "양날의 검이기도 했다."
    ),
    4179: (
        "나라 안 무사들을 묶던 \x1bCB신구토\x1bCZ가 사라지면서,\n"
        "\x1bCB아마고 가문\x1bCZ의 약화도 피할 수 없었다……"
    ),
    4180: (
        "주군 \x1bCA오우치 요시타카\x1bCZ를 치고,\n"
        "\x1bCB오우치 가문\x1bCZ의 실권을 쥔 \x1bCA스에 하루카타\x1bCZ는\n"
        "오랜 친분이 있던 \x1bCB모리 가문\x1bCZ에 협력을 청했다."
    ),
    4181: (
        "그러나 \x1bCA모리\x1bCZ 가문에서는 적장자 \x1bCA다카모토\x1bCZ가\n"
        "\x1bCA스에 하루카타\x1bCZ와의 제휴에 강하게 반대했고,\n"
        "\x1bCA모토나리\x1bCZ도 \x1bCA하루카타\x1bCZ와 결별하기로 했다."
    ),
    4182: (
        "\x1bCB모리 가문\x1bCZ은 \x1bCB오우치 가문\x1bCZ과 결전을,\n"
        "곧 \x1bCB오우치 가문\x1bCZ의 대군을 이어받은\n"
        "\x1bCA스에 하루카타\x1bCZ와 결전을 치르게 되었다……"
    ),
    4183: "\x1bCB모리 가문\x1bCZ·\x1bCC요시다 고리야마성\x1bCZ――",
    4184: (
        "\x1bCA하루카타\x1bCZ를 \x1bCC이쓰쿠시마\x1bCZ로 유인하는 계책은 성공했다.\n"
        "\x1bCA다카카게\x1bCZ, \x1bCA무라카미\x1bCZ는 어찌 되었느냐?"
    ),
    4185: "예……\n아직 결정을 내리지 못한 듯합니다.\n우리 편인지, \x1bCA스에\x1bCZ 편인지……",
    4186: "넌 그저 손을 놓고 보고만 있을 셈이냐?",
    4187: (
        "아닙니다.\n"
        "\x1bCA노미 무네카츠\x1bCZ를 사자로 보내,\n"
        "\x1bCA무라카미\x1bCZ를 설득할 생각입니다."
    ),
    4188: (
        "\x1bCA무네카츠\x1bCZ, \x1bCA무라카미\x1bCZ에게 전하라.\n"
        "배는 하룻밤만 빌려주면 된다고……"
    ),
    4189: (
        "우리가 \x1bCC이쓰쿠시마\x1bCZ로 건너가게만 도우면 된다.\n"
        "그 뒤에는 우리를 두고 돌아가도 좋다고."
    ),
    4190: "예!",
    4191: "자……\n계략과 조략은 끝났다.\n남은 건 무략뿐이겠지, \x1bCA모토하루\x1bCZ?",
    4192: (
        "그래, 맡겨 주십시오, 아버지!\n"
        "제가 가장 먼저 섬에 건너가,\n"
        "가장 먼저 \x1bCA하루카타\x1bCZ의 진으로 돌격하면 되지요?"
    ),
    4193: "흥, 대략 그렇다……\n\x1bCA다카카게\x1bCZ는――",
    4194: (
        "\x1bCA무네카츠\x1bCZ가 돌아오면 수군을 이끌고 섬으로 갑니다.\n"
        "항구에 상륙해 \x1bCA스에\x1bCZ의 진을 뒤흔듭니다.\n"
        "……맞지요?"
    ),
    4195: "……알고 있는 듯하군.\n둘 다 방심하지 마라!",
    4196: "그리고 \x1bCA다카모토\x1bCZ.\n너는 이 성에서 기다려라.",
    4197: (
        "이번 싸움은 \x1bCB모리 가문\x1bCZ의 운명을 건 큰 승부다.\n"
        "우리가 실패해 모두 전사한다면……\n"
        "\x1bCA다카모토\x1bCZ, 네가 \x1bCB모리 가문\x1bCZ을 이어야 한다."
    ),
    4198: (
        "그런 말씀 마십시오, 아버지!\n"
        "모두 전사하고 저만 남는다면,\n"
        "무슨 \x1bCB모리 가문\x1bCZ이 남겠습니까?"
    ),
    4199: "…………",
    4200: (
        "이번 싸움이 \x1bCB모리\x1bCZ의 앞날을 정합니다.\n"
        "그토록 중대한 싸움이라면 적장자인 제가\n"
        "선봉에 서야 하지 않겠습니까?"
    ),
    4201: "……하하하, 좋군!\n형님에게 그런 배짱이 있는 줄은 몰랐어.\n그럼 나와 함께 가자고!",
    4202: (
        "……\x1bCA다카모토\x1bCZ의 말이 옳다.\n"
        "좋다, \x1bCA모토하루\x1bCZ와 함께 선봉에 서라!"
    ),
    4203: "예!\n감사합니다!",
    4204: "내 발목이나 잡지 마, 형님!",
    4205: "그래!\n힘을 합쳐 \x1bCA하루카타\x1bCZ의 목을 베자!",
    4206: (
        "(천도를 저버린 자는 언젠가 망한다며,\n"
        "　\x1bCA하루카타\x1bCZ와 결별하자고 한 이도 \x1bCA다카모토\x1bCZ였다.)"
    ),
    4207: "(이 큰 싸움에서,\n　스스로 선봉을 청한 이도 \x1bCA다카모토\x1bCZ였다.)",
    4208: "(영리한 두 아우에게 가려 있었지만,\n　그는 착실히 당주의 그릇을 보이고 있었다……)",
    4209: (
        "(\x1bCA다카모토\x1bCZ, 훌륭한 장수가 되었구나.\n"
        "　이제 언제 죽음이 찾아와도,\n"
        "　여한은 없겠구나……)"
    ),
    4210: (
        "\x1bCA다이겐 셋사이\x1bCZ――\n"
        "본명은 \x1bCA규에이 쇼기쿠\x1bCZ로 \x1bCC교토\x1bCZ의 선승이었으나,\n"
        "뒤에 \x1bCC스루가\x1bCZ로 초빙되어 어린 \x1bCA요시모토\x1bCZ를 가르쳤다."
    ),
    4211: (
        "그 뒤 \x1bCA셋사이\x1bCZ는 안팎에서 \x1bCA요시모토\x1bCZ를 계속 보좌했다.\n"
        "두 사람은 힘을 합쳐 \x1bCB이마가와 가문\x1bCZ을\n"
        "센고쿠 굴지의 대다이묘로 키워 냈다."
    ),
    4212: "후후……\n나의 스승 \x1bCA셋사이\x1bCZ여.\n아직 공덕이 부족하지 않느냐?",
    4213: "이대로 죽으면,\n지옥에 다시 태어날 테니.\n몸을 더 돌보는 게 좋을 것이다……",
    4214: "\x1bCA요시모토\x1bCZ 님……\n소승도 부처를 모시는 몸.\n제 수명은 제가 압니다.",
    4215: "…………",
    4216: (
        "하지만 후회는 없습니다.\n"
        "\x1bCA요시모토\x1bCZ 님께서 천하로 나아갈 길은……\n"
        "이미 준비해 두었으니까요."
    ),
    4217: "고소슨 삼국동맹인가……\n이런 것까지 남기다니,\n스승이 제자에게 참으로 후하군.",
    4218: (
        "작은 답례일 뿐입니다.\n"
        "\x1bCA요시모토\x1bCZ 님과 함께 걸어온 반평생……\n"
        "참으로 즐거웠습니다."
    ),
    4219: (
        "제 무략을 마음껏 펼칠 수 있었던 것은……\n"
        "\x1bCA요시모토\x1bCZ 님이 계셨기 때문입니다.\n"
        "\x1bCA요시모토\x1bCZ 님을 만나 참으로 복되었습니다."
    ),
    4220: "이승에서 이토록 복을 누렸으니,\n다음에 제가 갈 곳은……\n틀림없이 지옥이겠지요.",
    4221: "그렇다면……\n지옥에서 먼저 기다려라, 나의 스승아.",
    4222: "이제 이 \x1bCA요시모토\x1bCZ가 천하를 차지하겠다!",
    4223: "그때까지,\n많은 업을 짊어지게 될 테니……",
    4224: "그럼…… 지옥의 악귀들과 싸울 준비는,\n소승이 갖춰 두겠습니다.",
    4225: "\x1bCA요시모토\x1bCZ 님……\n반드시 천하를……",
    4226: "그래, 알고 있다.\n스승의 계책을 절대 헛되게 하지 않겠다!",
    4227: "그러니 지금은 편히 잠들거라……",
    4228: (
        "\x1bCB이마가와 가문\x1bCZ은 \x1bCA요시모토\x1bCZ와 \x1bCA셋사이\x1bCZ라는\n"
        "두 수레바퀴가 떠받치고 있었다."
    ),
    4229: (
        "\x1bCA요시모토\x1bCZ는 이제 \x1bCA셋사이\x1bCZ를 잃고,\n"
        "\x1bCB이마가와\x1bCZ의 모든 것을 두 어깨에 짊어지게 됐다."
    ),
    4230: "이는 작게나마\n\x1bCB이마가와\x1bCZ의 앞날에 어두운 그림자를 드리웠다……",
    4231: (
        "\x1bCA오다 노부나가\x1bCZ는\n"
        "지금까지의 거성 \x1bCC나고야성\x1bCZ을 떠나,\n"
        "새로 얻은 \x1bCC기요스성\x1bCZ을 본거지로 삼았다."
    ),
    4232: (
        "\x1bCC기요스\x1bCZ에는 예전 오와리 슈고소가 놓였고,\n"
        "\x1bCC교토\x1bCZ·\x1bCC가마쿠라\x1bCZ 왕환로(\x1bCC도카이도\x1bCZ)와 \x1bCC이세 가도\x1bCZ가\n"
        "만나는 교통의 요충지였다."
    ),
    4233: "\x1bCC나고야\x1bCZ보다 \x1bCC기요스\x1bCZ가\n더 편리하다고 보시는군요.",
    4234: (
        "\x1bCC오와리\x1bCZ 한 나라를 다스린다면 \x1bCC기요스\x1bCZ도 좋다.\n"
        "하지만 천하를 노린다면,\n"
        "이 성도 결국 임시 거처일 뿐이다……"
    ),
    4235: "천하를 노릴 만한 성으로 옮길 때까지,\n이 땅을 힘껏 발전시키고\n힘을 비축해 둘까……",
    4236: (
        "\x1bCB미노 사이토 가문\x1bCZ에서는 전 당주 \x1bCA[bm924]\x1bCZ와\n"
        "현 당주 \x1bCA[bm921]\x1bCZ 부자의 불화가 이어지고 있었다."
    ),
    4237: (
        "무익한 다툼을 피하려 \x1bCA[bm924]\x1bCZ는 가독을\n"
        "\x1bCA[bm921]\x1bCZ에게 넘겼지만, 자신의 출생을 의심한\n"
        "\x1bCA[bm921]\x1bCZ의 불신은 더욱 커져만 갔다……"
    ),
    4238: "마침내 그 불신은,\n자신보다 \x1bCA[bm924]\x1bCZ의 총애를 받던 두 아우에게 향했다.",
    4239: (
        "큰일입니다!\n"
        "\x1bCA마고시로\x1bCZ 님과 \x1bCA기헤이지\x1bCZ 님이……\n"
        "\x1bCA[bm921]\x1bCZ 님 손에 죽었습니다!"
    ),
    4240: "뭐라고……?\n어찌 그런 일이?",
    4241: "\x1bCA[bm921]\x1bCZ 님이 병을 핑계로 두 분을 성에 불러,\n베었다고 합니다……!",
    4242: "……어리석은 놈!\n무엇 때문에 가독을 넘겨줬다고\n생각하는 것이냐! 이 바보 같은 아들아!",
    4243: (
        "\x1bCA[bm921]\x1bCZ는 \x1bCA마고시로\x1bCZ·\x1bCA기헤이지\x1bCZ를 죽였다.\n"
        "아니, \x1bCA[bm924]\x1bCZ를 친부로 보지 않은 \x1bCA[bm921]\x1bCZ는\n"
        "그들을 이복동생으로조차 여기지 않았을 것이다."
    ),
    4244: (
        "이것으로 됐다……\n"
        "훗날의 화근을 끊으려면 \x1bCA마고시로\x1bCZ와 \x1bCA기헤이지\x1bCZ를\n"
        "살려 둘 수는 없다!"
    ),
    4245: (
        "이미 아들을 둔 \x1bCA[[bm921]\x1bCZ에게,\n"
        "훗날 자식의 계승을 막을 아우들을 없앤 일은……"
    ),
    4246: (
        "센고쿠 다이묘에게는 흔한 일이었다.\n"
        "하지만 자식을 잃은 \x1bCA[[bm924]\x1bCZ에게,\n"
        "모든 것은 재앙이나 다름없었다."
    ),
    4247: "이놈…… 용서 못 한다!\n절대 용서 못 해…… \x1bCA[bm921]\x1bCZ!",
    4248: (
        "아버지, 아니 \x1bCA[bm924] 입도\x1bCZ가 뭐라 외치든,\n"
        "이제 \x1bCC미노\x1bCZ의 국주는 나다!\n"
        "방해되는 자는 모조리 없애야 한다!"
    ),
    4249: (
        "\x1bCA[bm924]\x1bCZ와 \x1bCA[bm921]\x1bCZ 부자의 대립은 더욱 격해져,\n"
        "가신들까지 두 편으로 갈라져 다투게 되었다."
    ),
    4250: (
        "불문에 깊이 귀의한 \x1bCA우에스기 데루토라\x1bCZ는,\n"
        "스승 \x1bCA야쿠오 소켄\x1bCZ이 던진 ‘불식’이란 무엇인가라는\n"
        "물음을 깊이 생각하고 있었다."
    ),
    4251: "불식……이란……",
    4252: "그저 모른다는 뜻이 아니다.\n알고자 하기만 해서는 알 수 없다는 뜻.",
    4253: "삼라만상, 모든 것을 아는 길……\n그것은 단지 아는 데 있지 않다.",
    4254: "모든 것을 부처께 맡기고,\n한결같이 불도를 걷는 것.",
    4255: "그것이 앞으로 내가 믿을 길이다!",
    4256: (
        "이를 깨달은 나의 이름……\n"
        "스승께 받은 글자와 함께 ‘\x1bCA겐신\x1bCZ’이라 하고,\n"
        "이제부터 \x1bCA후시키안 겐신\x1bCZ이라 칭하겠다!"
    ),
    4257: (
        "\x1bCA우에스기 데루토라\x1bCZ는 ‘\x1bCA우에스기 겐신\x1bCZ’으로 개명하고,\n"
        "불문에 더욱 깊이 귀의했다."
    ),
    4258: (
        "주군 \x1bCA도키 요리노리\x1bCZ를 추방하고\n"
        "\x1bCC미노\x1bCZ의 다이묘가 된 \x1bCA[b924]\x1bCZ는,\n"
        "몇 해 전부터 적장자 \x1bCA[bm921]\x1bCZ와 대립했다."
    ),
    4259: (
        "휘하 무장과 국인도 \x1bCA[bm924]\x1bCZ를 받드는 자와,\n"
        "\x1bCA[bm921]\x1bCZ를 지지하는 자로 둘로 갈려,\n"
        "충돌은 시간문제가 되었다."
    ),
    4260: (
        "마침내 양측은 \x1bCC나가라강\x1bCZ을 사이에 두고 맞섰고,\n"
        "부자가 서로를 해치는 골육상쟁이 벌어졌다."
    ),
    4261: (
        "내 아버지가 \x1bCA도키 요리노리\x1bCZ 공이라는 소문도 있다.\n"
        "저런 자를…… 어찌 아버지라 부르겠는가!\n"
        "역도 \x1bCA[bm924]\x1bCZ 입도를 쳐라!"
    ),
    4262: (
        "어리석은 아들 녀석……\n"
        "내 사위 \x1bCA노부나가\x1bCZ의 그릇에 한참 못 미친다.\n"
        "저래서야 \x1bCC미노\x1bCZ 한 나라조차 지키기 어렵겠군."
    ),
    4263: (
        "양군의 선봉이 각각 \x1bCC나가라강\x1bCZ을 건너자,\n"
        "곧 치열한 싸움이 벌어졌다.\n"
        "개전 소식은 이웃 나라 \x1bCC오와리\x1bCZ에도 전해졌다."
    ),
    4264: "주군!\n제발…… 아버님을 구원해 주십시오!",
    4265: "알고 있다!\n장인어른을 여기서 죽게 둘 수는 없다!\n서둘러 출진을 준비하라!",
    4266: (
        "하지만 \x1bCA노부나가\x1bCZ의 원군은 제때 도착하지 못했다.\n"
        "초반에는 \x1bCA[bm924]\x1bCZ 측이 유리했지만,\n"
        "중과부적으로 차츰 \x1bCA[bm921]\x1bCZ 측에 밀렸다……"
    ),
    4267: (
        "이제…… 여기까지인가.\n"
        "그 바보 아들치고는 제법 해냈구나.\n"
        "하지만 \x1bCC미노\x1bCZ의 운명도 이것으로 정해졌군……!"
    ),
    4268: "누구 없느냐!\n이 서장을 \x1bCA기초\x1bCZ의 남편 \x1bCA노부나가\x1bCZ에게 전하라!",
    4269: "\x1bCA[bm924]\x1bCZ 님, 각오하십시오!",
    4270: "크윽!",
    4271: (
        "\x1bCC미노\x1bCZ의 효웅 \x1bCA[b924]\x1bCZ가 세상을 떠났다――\n"
        "베인 머리는,\n"
        "\x1bCC미노\x1bCZ의 새 국주 \x1bCA[b921]\x1bCZ에게 보내졌다."
    ),
    4272: "나는 이제부터……\n‘아비를 죽인 자’라 불리겠지.",
    4273: (
        "하지만 \x1bCC미노\x1bCZ에 이 싸움은 피할 수 없는 길이었다.\n"
        "\x1bCA[bm924]\x1bCZ의 시신을 넘어,\n"
        "나는 새로운 \x1bCC미노\x1bCZ를 세우겠다!"
    ),
    4274: (
        "한편 \x1bCC미노·오와리 국경\x1bCZ을 넘기 전,\n"
        "\x1bCB노부나가군\x1bCZ은 \x1bCA[bm924]\x1bCZ의 전사 소식을 들었다."
    ),
    4275: "그런가…… 장인어른은 이미 쓰러지셨나.\n미안하다, \x1bCA기초\x1bCZ.\n늦고 말았다……",
    4276: "\x1bCA노부나가\x1bCZ 님께 보낼 서장을,\n\x1bCA[bm924]\x1bCZ 님께서 맡기셨습니다!",
    4277: "뭐라고!\n어서 보여라!",
    4278: (
        "서장에는 ‘\x1bCC미노\x1bCZ를 \x1bCA노부나가\x1bCZ에게 넘긴다’고 쓰였다.\n"
        "전투 중 다급히,\n"
        "적어 내린 결정이었다고 한다……"
    ),
    4279: (
        "장인어른…… \x1bCA[bm924]\x1bCZ 입도여!\n"
        "이 \x1bCA노부나가\x1bCZ가 그 뜻을 잇겠다!\n"
        "반드시 \x1bCC미노\x1bCZ를 내 손에 넣으리라!"
    ),
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    4163: ["shinguto_term_requires_glossary_review"],
    4183: ["yoshida_koriyama_castle_spacing_requires_castle_glossary_review"],
    4210: ["kyuei_shogiku_reading_requires_officer_review"],
    4217: ["kososun_triple_alliance_term_requires_glossary_review"],
    4232: ["kyoto_kamakura_route_term_requires_historical_review"],
    4245: ["stock_sc_contains_extra_open_bracket_before_bm921_preserved"],
    4246: ["stock_sc_contains_extra_open_bracket_before_bm924_preserved"],
    4250: ["yakuo_soken_and_fushiki_readings_require_specialist_review"],
    4256: ["fushikian_kenshin_reading_requires_glossary_review"],
    4271: ["b924_and_b921_short_placeholder_forms_preserved"],
}

PREVIOUS_ARTIFACT_PINS = {
    "evidence/alignment_evidence.v0.1.json": "7AE5DF4851B4BF288C6E3EF42399A2F3F1FBD04F287E59931EA722C0AF89A37C",
    "evidence/alignment_evidence.v0.2.json": "73A2B18423C1E7A6081F2500218A260EA04A0411F07729BF5344443F9ADAD033",
    "evidence/alignment_evidence.v0.3.json": "730FD461C3FD01AAC98DA548F462090261245A001296D8D36FCF57F22E9974F3",
    "evidence/alignment_evidence.v0.4.json": "35EE8A8A3DC5EFF888B32F423884E22F67C8140213EE200A8B30391F3E03C491",
    "evidence/alignment_evidence.v0.5.json": "0D561160DBDA0CACC38DCA729A5B315603ED75B9DC94889C5B0A4DBF900AE085",
    "evidence/alignment_evidence.v0.6.json": "782E6C3460559569B54490BE77C7AD44F8D6B10A94A8355014963BFD372C6CC0",
    "evidence/alignment_evidence.v0.7.json": "E4AE64791A6130C7E2D556A9C9C4394646C7D0E07D824BCC9F26A745FB9E8559",
    "evidence/alignment_evidence.v0.8.json": "739CC3631F35788B684755EA8BDEDC9C8AECC1C45C42630C9E797264C3E73665",
    "evidence/alignment_evidence.v0.9.json": "DFEAC5B69599C239A02E5A3C1801382312691A51FF6F9A4E3F7D8D207C9426D6",
    "public/msgev_ko_event_continuation_3230_3308.v0.2.json": "2EF36C22207A8B9A1CBFDB1212A8DBA2A8C49EDAF2D68BF95DDFB07404CDA637",
    "public/msgev_ko_event_endings_3311_3440.v0.3.json": "482239403E31932E9FD735C4C6F08228F650147B0A9D523431B5F4D17CBBF1FF",
    "public/msgev_ko_event_opening_3202_3229.v0.1.json": "98C77E79256EE7B5A5CAAFAF95FDC1467F20A90F8E508E3EE975629B4EFD1C7F",
    "public/msgev_ko_historical_events_3441_3564.v0.4.json": "31A05234F6E5CCC40BF40E7AE9A19BFE5E3A229A27725B17AA21EB932811C854",
    "public/msgev_ko_historical_events_3565_3688.v0.5.json": "1E5D5E874439C7D0FC0BD93D6EB2FBAC6C249DF18A9BFBCBBE2200BCC45F75AC",
    "public/msgev_ko_historical_events_3689_3818.v0.6.json": "4111FA3388E3AC52234EAD5288BEE0959E90CFE9A3B0DB4A0DCE9A5DBE758D2E",
    "public/msgev_ko_historical_events_3819_3929.v0.7.json": "8B121FE9A3D78EC0C936732A801F1710FE4D4334AC322F9954066C10B097D392",
    "public/msgev_ko_historical_events_3930_4031.v0.8.json": "3CE22CFC77829BD1A627FB0ABE80FC387196AED74DA3B79A29EDB5FAC2D77534",
    "public/msgev_ko_historical_events_4032_4160.v0.9.json": "C5781DC398C09C776888577F3831F9C853440C5A1A0C0BC450384E4505911F9A",
    "review/review_index.v0.1.json": "2DE2BE324877ED3E6D298BE4E63AC0D4F15A09C588E5A2D79B8BA402B8C69BEC",
    "review/review_index.v0.2.json": "F90BDE5F561C489D2251A0EB6CF81FA5B4B04E4C8030682AFEC77A7B86073B7A",
    "review/review_index.v0.3.json": "5C834F7C2D130E3AC1A246CFDFC73A7248C3078F122FA7AEB60230AB3E5B7AAD",
    "review/review_index.v0.4.json": "7650A7831B8F12215AE951049EACAEE08B24119666B1DB7F74EB7ABE07002C9B",
    "review/review_index.v0.5.json": "582C7F2930496F36CA460370DD3CA47C611F4794C8DFD7A6EA1028008D921C20",
    "review/review_index.v0.6.json": "CB0DFF25C7A035EE0783D3D725E6D2029700CB095DC5FC22EF0FC07431D6D982",
    "review/review_index.v0.7.json": "74F9F475F31819A087D8C2E86F1564DEAE390197B8616E4CCE17A60F5E0D037B",
    "review/review_index.v0.8.json": "8CC9DDC3FCEF5D7A370BE4B6E8BB5AB325F5096DFE1E2719B80E410C971D032A",
    "review/review_index.v0.9.json": "42E2DA83B1391451A55B14AD06F6407D1A4F8C705B783257DD02F39A12ABEA08",
    "validation.json": "38C9294159DFDFD4CA6508EEA86B19BF175D9BB82DF7C3290AEDDBDD69823D44",
    "validation.v0.2.json": "D235D88BADEAC9159F1E3684BAA0F3FED35E1F4E2C3FCEA499C1E2AD85685F31",
    "validation.v0.3.json": "2734D895A0D224ECE9BC7BB31DF16BB57534F83BF0219BFF4B046C1EF2710B4B",
    "validation.v0.4.json": "35FDFB30F42D4081C0334C793F4E49988D1F1CCDA7FDB05BB40045882F35C936",
    "validation.v0.5.json": "F6AE6830D94549DB9D917D2F65DAE0A8BDAA59A956A10ECE17428B4BA565203A",
    "validation.v0.6.json": "1FBA570797EE49AA15874D1D3EA42AE94536FE790921D620A72413BCA49EED03",
    "validation.v0.7.json": "3EE51745A00EBDB234E9F98DED40C6C5CE6D8395E6A93EAB181E310F9E09400C",
    "validation.v0.8.json": "996727176B973D14451C65EB5AF0661BC50B40DFE53C8FAC01D26305E4751935",
    "validation.v0.9.json": "0F23B1D2B02985CDCB5E2F674630CEC250977EC830A1EC1D683364723FE97C1C",
}

INSTALLED_RESOURCE_PINS = {
    "MSG_PK/SC/msgev.bin": {
        "size": 770724,
        "sha256": "86D354C1EB33C653091A28CA9EB284622BA917D4BACB7D4160C1626175A079CD",
    },
    "MSG_PK/JP/msgev.bin": {
        "size": 555784,
        "sha256": "03426B59D32EB628021DE43BC02FF82B56B04D97C25CE37F735630EA7C4E2002",
    },
    "MSG_PK/EN/msgev.bin": {
        "size": 758160,
        "sha256": "95CDB15F1AED529C95ADDE784A750059E90060A44DF1EA208EB4A56E2F685640",
    },
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
    if len(ids) != 119 or ids != sorted(TRANSLATIONS):
        raise ValueError("batch10 ids are not the exact 119 displayed entries")
    return ids


def event_for(entry_id: int) -> str:
    matches = [
        event["event_id"]
        for event in EVENTS
        if event["start_id"] <= entry_id <= event["end_id"]
    ]
    if len(matches) != 1:
        raise ValueError(f"id {entry_id} does not map to one batch10 event group")
    return str(matches[0])


def source_structure(text: str) -> dict[str, Any]:
    return shared.source_structure(text)


def public_script_counts(text: str) -> dict[str, int]:
    return shared.public_script_counts(text)


def previous_artifact_snapshot() -> dict[str, Any]:
    mismatches: list[dict[str, Any]] = []
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
    snapshot: dict[str, dict[str, Any]] = {}
    mismatches: list[dict[str, Any]] = []
    for relative, expected in sorted(INSTALLED_RESOURCE_PINS.items()):
        path = WORKSPACE_ROOT / relative
        blob = path.read_bytes()
        actual = {"size": len(blob), "sha256": sha256(blob)}
        if actual != expected:
            mismatches.append({"path": relative, "expected": expected, "actual": actual})
        snapshot[relative] = actual
    if mismatches:
        raise ValueError(f"installed msgev baseline changed: {mismatches}")
    return snapshot


def build(args: argparse.Namespace) -> dict[str, Any]:
    ids = selected_ids()
    previous_before = previous_artifact_snapshot()
    installed_before = installed_resource_snapshot()
    loaded = {
        language: source_shared.load_source(path, language)
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
        if len({tables[language].texts[entry_id] for language in ("SC", "JP", "EN")})
        == 1
    ]
    if display_failures:
        raise ValueError(
            f"batch10 range contains all-language shared internal keys: {display_failures}"
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

    visible_lengths = {
        entry_id: [
            len(common.ESC_RE.sub("", line))
            for line in TRANSLATIONS[entry_id].splitlines()
        ]
        for entry_id in ids
    }
    entries_over_32 = [
        entry_id
        for entry_id, lengths in visible_lengths.items()
        if max(lengths) > 32
    ]
    if entries_over_32:
        raise ValueError(f"authored lines exceed 32 codepoints: {entries_over_32}")

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
        4160,
        4161,
        4179,
        4180,
        4209,
        4210,
        4230,
        4231,
        4235,
        4236,
        4249,
        4250,
        4257,
        4258,
        4279,
        4280,
    )
    evidence = {
        "schema": "nobu16.kr.event-dialogue-alignment-evidence.v10",
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
        "schema": "nobu16.kr.event-dialogue-review-index.v10",
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
        raise ValueError("batch10 public artifact contains source-script text")

    previous_after = previous_artifact_snapshot()
    installed_after = installed_resource_snapshot()
    if previous_before != previous_after:
        raise ValueError("previous dialogue artifact snapshot changed during build")
    if installed_before != installed_after:
        raise ValueError("installed msgev snapshot changed during build")

    validation = {
        "schema": "nobu16.kr.event-dialogue-generation-validation.v10",
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
            "entries_over_32": [],
            "source_fixed_linebreak_exceptions": [],
            "runtime_layout_review_required": True,
        },
        "font_integration": {
            "state": "deferred_not_computed",
            "current_font_or_installer_must_not_include_batch10": True,
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
        "preexisting_integrity": {
            "dialogue_v01_v09_artifacts_before": previous_before,
            "dialogue_v01_v09_artifacts_after": previous_after,
            "installed_msgev_before": installed_before,
            "installed_msgev_after": installed_after,
        },
        "safety": {
            "installed_game_files_modified": False,
            "font_files_modified": False,
            "installer_modified": False,
            "root_readme_or_progress_modified": False,
            "common_builder_or_other_workstream_modified": False,
            "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_artifacts_modified": False,
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
