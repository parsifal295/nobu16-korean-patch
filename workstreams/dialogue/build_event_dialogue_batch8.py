#!/usr/bin/env python3
"""Build source-free Korean historical event dialogue batch8 (3930-4031)."""

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
import build_event_dialogue_batch2 as source_shared  # noqa: E402
import build_event_dialogue_batch7 as shared  # noqa: E402


BATCH_ID = "msgev_historical_events_3930_4031.v0.8"
OVERLAY_NAME = "msgev_ko_historical_events_3930_4031.v0.8.json"
EVIDENCE_NAME = "alignment_evidence.v0.8.json"
REVIEW_NAME = "review_index.v0.8.json"
VALIDATION_NAME = "validation.v0.8.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 3930
SCOPE_END = 4031
EXCLUDED_INTERNAL_IDS: tuple[int, ...] = ()
BRACKET_TOKEN_RE = re.compile(r"\[[a-z0-9_]+\]")

EVENTS = (
    {
        "event_id": "takeda_toishi_rout",
        "title_ko": "다케다군의 도이시성 패전",
        "start_id": 3930,
        "end_id": 3945,
        "selected_count": 16,
    },
    {
        "event_id": "mori_inoue_purge",
        "title_ko": "모리 모토나리의 이노에 일파 숙청",
        "start_id": 3946,
        "end_id": 3961,
        "selected_count": 16,
    },
    {
        "event_id": "ouchi_taineiji_coup",
        "title_ko": "오우치 요시타카의 최후",
        "start_id": 3962,
        "end_id": 3990,
        "selected_count": 29,
    },
    {
        "event_id": "sentoin_masakage_marriage",
        "title_ko": "센토인과 나가오 마사카게의 혼인",
        "start_id": 3991,
        "end_id": 4002,
        "selected_count": 12,
    },
    {
        "event_id": "hosokawa_ujitsuna_delegates_power",
        "title_ko": "호소카와 우지쓰나의 권한 이양",
        "start_id": 4003,
        "end_id": 4011,
        "selected_count": 9,
    },
    {
        "event_id": "oda_nobuhide_death",
        "title_ko": "오다 노부히데의 죽음과 장례",
        "start_id": 4012,
        "end_id": 4031,
        "selected_count": 20,
    },
)

TRANSLATIONS: dict[int, str] = {
    3930: (
        "\x1bCC가이\x1bCZ의 전국 다이묘 \x1bCA[b1251]\x1bCZ 공이\n"
        "본격적으로 침공을 시작한 지 몇 해,\n"
        "\x1bCC시나노\x1bCZ는 차츰 \x1bCB다케다 가문\x1bCZ에 잠식되고 있었다……"
    ),
    3931: (
        "\x1bCC신슈\x1bCZ는 우리의 땅이다.\n"
        "\x1bCA[bm1251]\x1bCZ 공의 뜻대로 두지는 않겠다!"
    ),
    3932: (
        "\x1bCC시나노\x1bCZ의 여러 세력 가운데,\n"
        "반\x1bCB다케다\x1bCZ의 기치를 든 이는 예부터 \x1bCC신슈\x1bCZ를 다스린\n"
        "\x1bCB무라카미 가문\x1bCZ의 \x1bCA요시키요\x1bCZ였다."
    ),
    3933: (
        "\x1bCA요시키요\x1bCZ는 일찍이 \x1bCC우에다하라\x1bCZ에서 \x1bCA[bm1251]\x1bCZ 공의\n"
        "군을 꺾어, \x1bCA[bm1251]\x1bCZ 공에 맞설 뜻이\n"
        "\x1bCB시나노 무사들\x1bCZ 가운데서도 특히 강했다."
    ),
    3934: (
        "\x1bCA무라카미 요시키요\x1bCZ만 쓰러뜨리면,\n"
        "\x1bCC시나노 중부\x1bCZ와 \x1bCC시나노 북부\x1bCZ의 세력은 저절로 따른다.\n"
        "\x1bCA요시키요\x1bCZ를 철저히 짓밟아 주마!"
    ),
    3935: (
        "\x1bCA[bm1251]\x1bCZ 공은 대군을 이끌고,\n"
        "\x1bCA요시키요\x1bCZ가 다른 방면에 출병한 틈을 타,\n"
        "\x1bCC치이사가타\x1bCZ의 요충 \x1bCC도이시성\x1bCZ에 다가갔다."
    ),
    3936: (
        "\x1bCA[bm1251]\x1bCZ 공의 그간 전과와\n"
        "전략·경험을 생각하면 \x1bCC도이시성\x1bCZ쯤은\n"
        "쉽게 함락될 듯했다. 그러나……"
    ),
    3937: (
        "\x1bCA[bm1251]\x1bCZ 놈이 왔구나!\n"
        "즉시 \x1bCC도이시성\x1bCZ으로 간다!"
    ),
    3938: (
        "\x1bCB다케다군\x1bCZ의 내습을 들은 \x1bCA무라카미 요시키요\x1bCZ는 즉시\n"
        "군을 돌려 \x1bCC도이시성\x1bCZ 구원에 나섰다."
    ),
    3939: (
        "\x1bCA요시키요\x1bCZ 놈, 생각보다 움직임이 빠르군.\n"
        "하지만 그가 돌아오기 전에\n"
        "성을 떨어뜨리면 그만이다!"
    ),
    3940: (
        "하지만 성병보다 열 배 많은 \x1bCB다케다군\x1bCZ도\n"
        "\x1bCC도이시성\x1bCZ을 좀처럼 함락하지 못했다.\n"
        "\x1bCA[bm1251]\x1bCZ 공의 초조함은 커져만 갔다……"
    ),
    3941: (
        "\x1bCC도이시성\x1bCZ과 \x1bCB무라카미\x1bCZ 병사를 얕보았구나!\n"
        "\x1bCA[b1251]\x1bCZ! 여기서 네놈을 치겠다!"
    ),
    3942: "크윽!",
    3943: (
        "예상보다 빨리 도착한 \x1bCA무라카미 요시키요\x1bCZ는\n"
        "\x1bCC도이시성\x1bCZ 병사들과 함께 \x1bCB다케다군\x1bCZ을 협공했고,\n"
        "\x1bCB다케다군\x1bCZ은 크게 혼란에 빠져 물러났다."
    ),
    3944: (
        "\x1bCA무라카미 요시키요\x1bCZ…… 제법이구나!\n"
        "\x1bCC우에다하라\x1bCZ에 이어 여기서도 나를 괴롭히다니.\n"
        "참으로 내 숙적이다……"
    ),
    3945: (
        "뼈아픈 패배를 당한 \x1bCB다케다 측\x1bCZ은\n"
        "이 싸움을 '도이시 붕괴'라 불렀다고 한다……"
    ),
    3946: (
        "\x1bCB아키 모리씨\x1bCZ는 고케닌 \x1bCB오에씨\x1bCZ의 후예. 전국 중기까지\n"
        "주변 세력에 휘둘리던 일족이었다."
    ),
    3947: (
        "이윽고 같은 약소 고쿠진들을 모아,\n"
        "거대 세력에 맞서게 되었고,\n"
        "\x1bCB모리 가문\x1bCZ은 \x1bCA모토나리\x1bCZ 대에 크게 도약했지만……"
    ),
    3948: (
        "가문에는 한때 \x1bCA모리\x1bCZ와 동격이던 고쿠진도 있어,\n"
        "주군이라 해도 그들을 강권으로 다스릴 만큼\n"
        "\x1bCA모리\x1bCZ의 우위는 확고하지 않았다."
    ),
    3949: (
        "그중 \x1bCA이노에 모토카네\x1bCZ 일파는 \x1bCA모리\x1bCZ의 가신이면서도,\n"
        "횡포를 자주 부렸고,\n"
        "주가의 명령도 듣지 않았다."
    ),
    3950: "그런가.\n사찰과 신사 영지의 논밭을 멋대로……\n심각한 일이로군.",
    3951: (
        "예!\n"
        "\x1bCB이노에 일파\x1bCZ는 사찰 영지만이 아니라,\n"
        "다른 가신의 영지까지 빼앗고 있습니다……"
    ),
    3952: "영지 강탈을 막으려던 무사까지\n죽였다고 합니다!",
    3953: (
        "그 지경이면 더는 내버려 둘 수 없군……\n"
        "우선 \x1bCA이노에 모토카네\x1bCZ를 평정 자리에 부르자.\n"
        "사람들 앞에서 내가 직접 타이르겠다."
    ),
    3954: (
        "\x1bCB이노에 일파\x1bCZ 횡포를 막으려 \x1bCA모토나리\x1bCZ는 \x1bCA모토카네\x1bCZ를 불렀으나,\n"
        "\x1bCA모토카네\x1bCZ는 갖은 핑계를 대며 등성을 거부했다……"
    ),
    3955: (
        "이런, 등성 명령조차 듣지 않는가.\n"
        "어쩔 수 없군. 여기서는 악귀가 되어야겠어……"
    ),
    3956: (
        "\x1bCA모토나리\x1bCZ는 몰래 자객을 보내 \x1bCA이노에 모토카네\x1bCZ를 암살했다.\n"
        "이어 동요한 \x1bCB이노에 일파\x1bCZ의 저택을 급습해,\n"
        "일족 30여 명을 단숨에 숙청했다."
    ),
    3957: (
        "그 뒤 \x1bCA모토나리\x1bCZ는 가문에 문서를 반포해,\n"
        "\x1bCB이노에 일파\x1bCZ의 죄목을 무려 11개나 열거하고,\n"
        "그들의 잘못을 대대적으로 알렸다."
    ),
    3958: (
        "전광석화 같은 숙청에\n"
        "\x1bCA모리\x1bCZ 가신들은 떨었고, 200명이 넘는 이들이\n"
        "\x1bCA모리\x1bCZ에게 충성을 맹세하는 서약서를 올렸다."
    ),
    3959: (
        "이런, 이런…… 잃은 것도 많았지만,\n"
        "이제 가문이 다잡힐지 모르겠군.\n"
        "비 온 뒤 땅이 굳으면 좋으련만."
    ),
    3960: (
        "교묘한 수였지만,\n"
        "어디까지나 \x1bCA모토나리\x1bCZ의 비정한 결단으로,\n"
        "\x1bCB이노에 일파\x1bCZ의 영향력은 가문에서 사라졌다."
    ),
    3961: (
        "여러 세력이 뒤섞인 \x1bCB모리 가문\x1bCZ이\n"
        "전국 다이묘로 권력을 집중하려면,\n"
        "피할 수 없는 길이었던 것일까……"
    ),
    3962: (
        "갓산토다성 전투에서 대패한 \x1bCA오우치 요시타카\x1bCZ는\n"
        "정무에 흥미를 잃고 유흥에 빠졌으며,\n"
        "백성에게도 무거운 부담을 지웠다……"
    ),
    3963: (
        "주군, \x1bCB오우치 가문\x1bCZ은 \x1bCC사이고쿠\x1bCZ 제일의 대다이묘입니다.\n"
        "와카와 다회도 좋지만,\n"
        "무사의 본분은 무예임을 잊지 마십시오……"
    ),
    3964: (
        "\x1bCA다카후사\x1bCZ인가, 시끄럽구나.\n"
        "나는 아무래도 싸움에는 맞지 않는 듯하다.\n"
        "군무는 네게 맡기겠다."
    ),
    3965: (
        "싸움도 중요하지만,\n"
        "문화를 키우고 지키는 것도 다이묘의 중요한 역할이오.\n"
        "그리 눈을 부릅뜰 일은 아니지 않소……"
    ),
    3966: (
        "(……주군 곁의 문약한 무리들이,\n"
        "　주군을 더욱 무르게 만들고 있다.\n"
        "　이대로면 \x1bCB오우치 가문\x1bCZ의 앞날은 어둡다.)"
    ),
    3967: (
        "\x1bCA스에 다카후사\x1bCZ는 \x1bCB오우치\x1bCZ의 앞날을 걱정해 \x1bCA요시타카\x1bCZ의 조카\n"
        "\x1bCA하루히데\x1bCZ를 \x1bCB오토모\x1bCZ에서 \x1bCC야마구치\x1bCZ로 몰래 불렀다……"
    ),
    3968: (
        "\x1bCA하루히데\x1bCZ는 \x1bCA요시아키\x1bCZ·\x1bCA요시타카\x1bCZ 누이의 아들. "
        "\x1bCA그\x1bCZ의 양자였다가 \x1bCA그\x1bCZ에게 친자가 생겨 "
        "\x1bCB오토모\x1bCZ로 돌아갔다."
    ),
    3969: (
        "몰래 \x1bCA요시타카\x1bCZ의 후계자를 마련한 \x1bCA다카후사\x1bCZ는,\n"
        "\x1bCB오우치 가문\x1bCZ을 따르던 \x1bCA모리 모토나리\x1bCZ 등의 지지도 얻어,\n"
        "착착 주가 전복 계획을 다듬었다……"
    ),
    3970: (
        "그리고 어느 날……\n"
        "마침내 \x1bCA다카후사\x1bCZ는 \x1bCA하루히데\x1bCZ를 받들어 거병했다.\n"
        "순식간에 여러 성을 평정하고 \x1bCC야마구치\x1bCZ로 다가갔다."
    ),
    3971: (
        "\x1bCA요시타카\x1bCZ 님께서는 은거하시고,\n"
        "속히 \x1bCA하루히데\x1bCZ 님께 가독을 넘기십시오!\n"
        "이 모두가 \x1bCB오우치 가문\x1bCZ을 위해서입니다."
    ),
    3972: (
        "어, 어리석은 소리 마라!\n"
        "네가 받드는 \x1bCA하루히데\x1bCZ는 \x1bCB오우치 가문\x1bCZ 당주의 그릇이 아니다!\n"
        "\x1bCB오우치\x1bCZ를 위한 일이 될 리 없다!"
    ),
    3973: (
        "적어도 유흥에만 빠진 \x1bCA요시타카\x1bCZ 님보다는,\n"
        "제가 하는 말을 모두 받아들이는\n"
        "\x1bCA하루히데\x1bCZ 님이 \x1bCB오우치\x1bCZ를 위해 더 낫겠지요……"
    ),
    3974: (
        "\x1bCA하루히데\x1bCZ를 꼭두각시로 삼아,\n"
        "\x1bCB오우치 가문\x1bCZ을 네 것으로 만들 셈이냐!"
    ),
    3975: (
        "어떻게 생각하시든 상관없습니다.\n"
        "제게는 이것이야말로,\n"
        "\x1bCB오우치 가문\x1bCZ에 충성을 다하는 길입니다."
    ),
    3976: "네가 이런 사내였다니……\n내가 잘못 보았던 것인가!",
    3977: (
        "후후후…… \x1bCB오우치\x1bCZ에 필요한 건 \x1bCA요시타카\x1bCZ가 아닌 \x1bCA다카후사\x1bCZ다!\n"
        "자, 가독을 넘기시오!"
    ),
    3978: "크윽……\n이렇게 포위되었으니 달아날 수 없나!",
    3979: "포기하시면 안 됩니다!\n자, 이쪽으로!",
    3980: "서라!\n놓치지 않겠다!",
    3981: (
        "\x1bCA다카토요\x1bCZ의 분전으로 \x1bCA요시타카\x1bCZ는 포위를 뚫었다.\n"
        "\x1bCB스에군\x1bCZ을 피해 \x1bCC나가토\x1bCZ의 \x1bCC다이네이지\x1bCZ로 갔으나 다시 포위됐다."
    ),
    3982: (
        "\x1bCA다카토요\x1bCZ…… 이제 됐다. 여기까지다.\n"
        "나는 이곳에서 할복하겠다…… 가이샤쿠해 다오.\n"
        "\x1bCB오우치 가문\x1bCZ의 역사도 여기서 끝이다!"
    ),
    3983: (
        "'치는 자와 맞는 자 모두……\n"
        "　이슬과 같고 번개와 같으니,\n"
        "　마땅히 이와 같이 볼지어다.'"
    ),
    3984: "주군―!",
    3985: "뭐라고, 자결하셨다……!?\n그, 그런가……",
    3986: (
        "\x1bCA다카후사\x1bCZ는 \x1bCA요시타카\x1bCZ가 \x1bCA하루히데\x1bCZ에게 가독을 넘기고\n"
        "은거하기만을 바랐지 목숨까지 빼앗을 생각은 없었기에,\n"
        "주군의 자결 소식에 동요했다."
    ),
    3987: (
        "그러나 동요는 한순간뿐이었다.\n"
        "그 뒤로는 담담히 사후 처리를 진행해,\n"
        "\x1bCB오우치 가문\x1bCZ을 평온한 상태로 되돌렸다."
    ),
    3988: (
        "\x1bCA다카후사\x1bCZ는 \x1bCA하루히데\x1bCZ에게 한 자를 받아 \x1bCA하루카타\x1bCZ로 고쳤고,\n"
        "\x1bCA하루히데\x1bCZ는 쇼군에게 '요시'를 받아,\n"
        "\x1bCA요시나가\x1bCZ로 이름을 바꿨다."
    ),
    3989: (
        "하지만 \x1bCA하루카타\x1bCZ의 강압적인 방식은 마찰을 불렀고,\n"
        "옛 주군을 죽음으로 몰았다는 비판까지 겹쳐,\n"
        "\x1bCA모리 모토나리\x1bCZ 등의 지지를 잃어 갔다."
    ),
    3990: (
        "\x1bCA다카후사\x1bCZ에서 \x1bCA하루카타\x1bCZ로 이름을 바꾼 그의 생각과 달리,\n"
        "\x1bCB오우치 가문\x1bCZ은 이후 더 깊은 동란의 소용돌이에\n"
        "휘말려 갔다……"
    ),
    3991: (
        "\x1bCB후추 나가오 가문\x1bCZ과 \x1bCB우에다 나가오 가문\x1bCZ 당주는\n"
        "오랜 다툼을 끝냈고, 화해의 증표로\n"
        "혼인을 추진했다."
    ),
    3992: (
        "누님, 죄송합니다.\n"
        "\x1bCA[bm1448]\x1bCZ 공은 누님을 정략의 도구로 삼을 생각은\n"
        "추호도 없습니다만……"
    ),
    3993: (
        "알고 있단다, \x1bCA[bm1448]\x1bCZ 공.\n"
        "나는 이번 혼인을\n"
        "결코 부정적으로 생각하지 않아."
    ),
    3994: (
        "오라버니와 \x1bCA[bm1448]\x1bCZ 공을 다뤄 지위를 굳힌 \x1bCA마사카게\x1bCZ\n"
        "님이 내 남편이라니…… 유쾌하지 않겠니?"
    ),
    3995: (
        "\x1bCA마사카게\x1bCZ는 방심할 수 없는 사내지만,\n"
        "\x1bCB나가오 가문\x1bCZ에 없어서는 안 될 인재이기도 합니다."
    ),
    3996: (
        "누님은 물론, 이제 매형이 될 \x1bCA마사카게\x1bCZ 공도\n"
        "\x1bCA[bm1448]\x1bCZ 공이 결코 소홀히 대하지 않겠습니다.\n"
        "마음 편히 시집가 주십시오……"
    ),
    3997: (
        "그리하여 \x1bCA[bm1448]\x1bCZ 공의 누이 \x1bCA센토인\x1bCZ은\n"
        "\x1bCB우에다 가문\x1bCZ 당주 \x1bCA나가오 마사카게\x1bCZ에게 시집갔다……"
    ),
    3998: "부족한 사람이오나,\n잘 부탁드립니다.",
    3999: (
        "음. 나야말로 잘 부탁하오.\n"
        "당주의 누이를 아내로 맞는 것이니,\n"
        "나도 좋은 남편이 되도록 힘쓰겠소."
    ),
    4000: "어머.\n그렇다면 저도 좋은 아내가 되겠습니다.\n후후후……",
    4001: (
        "\x1bCA마사카게\x1bCZ는 정식으로 주군 \x1bCA[b1448]\x1bCZ 공의 매형이 되어,\n"
        "이후 일문중의 실력자로 활약했다."
    ),
    4002: (
        "정략으로 맺어졌지만 \x1bCA마사카게\x1bCZ와 \x1bCA센토인\x1bCZ은 금슬이 좋았고,\n"
        "두 사람 사이에는 두 아들과 두 딸이 태어났다……"
    ),
    4003: (
        "에구치 전투에서 \x1bCA하루모토\x1bCZ의 군세를 물리쳐,\n"
        "간레이 \x1bCB호소카와 가문\x1bCZ의 적류로\n"
        "인정받게 된 \x1bCA호소카와 우지쓰나\x1bCZ―"
    ),
    4004: (
        "하지만 모두가 보기에\n"
        "에구치 전투의 주역은 \x1bCA미요시 나가요시\x1bCZ 삼형제였고,\n"
        "\x1bCA우지쓰나\x1bCZ가 나설 일은 거의 없었다."
    ),
    4005: (
        "모두 나를 꼭두각시라 부른다……\n"
        "실권이 없는 건 사실이나 어쩔 수 없지.\n"
        "그 싸움에서 공을 세운 건 \x1bCB미요시 가문\x1bCZ의 사람들이다."
    ),
    4006: (
        "지금은 \x1bCA미요시 나가요시\x1bCZ가 나를 주군으로 대하지만,\n"
        "장차 나도 배신당할지 모른다.\n"
        "\x1bCA하루모토\x1bCZ처럼……"
    ),
    4007: (
        "자신과 \x1bCB미요시 가문\x1bCZ의 앞날을 불안해한\n"
        "\x1bCA호소카와 우지쓰나\x1bCZ는,\n"
        "적극적으로 권한을 \x1bCA미요시 나가요시\x1bCZ에게 넘겼다."
    ),
    4008: (
        "하극상이 당연시되던 이 시대에,\n"
        "\x1bCA우지쓰나\x1bCZ는 자신의 처지를 뛰어넘을\n"
        "역량을 지닌 주군이 아니었고……"
    ),
    4009: (
        "\x1bCA나가요시\x1bCZ의 좋은 협력자라는 자리에 머물러,\n"
        "자신의 안녕을 꾀했다."
    ),
    4010: (
        "\x1bCA나가요시\x1bCZ도 이 '주군'의 권한 이양 의사를 존중해,\n"
        "\x1bCA하루모토\x1bCZ와 달리 추방하지 않고,\n"
        "그 지위를 보전해 주었다."
    ),
    4011: (
        "그리하여 세력으로서의 '\x1bCB호소카와 가문\x1bCZ'은,\n"
        "'\x1bCB미요시 가문\x1bCZ'으로 탈바꿈해 갔다."
    ),
    4012: "\x1bCA오다 노부히데\x1bCZ―",
    4013: (
        "\x1bCC쓰시마\x1bCZ와 \x1bCC아쓰타\x1bCZ 같은 상업 도시를 지배해,\n"
        "풍부한 경제력으로 \x1bCB오다 가문\x1bCZ의 기반을 다진 명장."
    ),
    4014: (
        "하지만 대외적으로는 어디까지나\n"
        "슈고다이의 가신이라는 처지에 머물렀고,\n"
        "가문도 \x1bCC오와리국\x1bCZ도 통일하지 못했다……"
    ),
    4015: (
        "영지가 좁았기에,\n"
        "\x1bCA사이토\x1bCZ와 \x1bCA이마가와\x1bCZ 같은 국외의 강적에게\n"
        "차츰 밀리기 시작했다."
    ),
    4016: "그러던 중, 그는 유행병으로 쓰러졌다……",
    4017: "흐, 하하하……\n원통하구나!",
    4018: (
        "이제 \x1bCA노부나가\x1bCZ의 천하가 시작되려는데,\n"
        "가독도 넘기지 못하고 내 운이 다하다니!"
    ),
    4019: (
        "\x1bCA노부나가\x1bCZ야……\n"
        "저세상의 내게 보여 다오.\n"
        "\x1bCA오다\x1bCZ의 천하를…… 네 세상을!"
    ),
    4020: (
        "'오와리의 호랑이' \x1bCA오다 노부히데\x1bCZ가 세상을 떠났다.\n"
        "그 죽음은 \x1bCB오다 가문\x1bCZ을 크게 뒤흔들었다."
    ),
    4021: (
        "\x1bCA노부히데\x1bCZ와 달리 가문의 많은 이들은,\n"
        "차기 당주 \x1bCA노부나가\x1bCZ에게\n"
        "큰 불안을 품고 있었다."
    ),
    4022: (
        "그리고,\n"
        "그 불안이 현실이 되는 사건이\n"
        "\x1bCA노부히데\x1bCZ의 장례 날 일어났다."
    ),
    4023: "도, 도련님!\n그 모습은……!?\n대체 무엇을……",
    4024: "…………",
    4025: (
        "(아버지가 죽었다……\n"
        "　그토록 난세를 꿰뚫어 본 사람도,\n"
        "　아무것도 하지 못하고 죽는구나……)"
    ),
    4026: (
        "(나도 아버지처럼 죽는가?\n"
        "　당주니 다이묘니 불려도,\n"
        "　아무것도 이루지 못한 채 죽는가?)"
    ),
    4027: "나는……!",
    4028: "도, 도련님……\n어찌 그런 짓을……",
    4029: (
        "\x1bCA노부나가\x1bCZ는 \x1bCA노부히데\x1bCZ의 위패에 향가루를 내던지고,\n"
        "그대로 장례 자리를 떠났다고 전한다."
    ),
    4030: (
        "새 당주의 이해할 수 없는 행동에,\n"
        "\x1bCB오다\x1bCZ 가신들의 불안은 다시 커졌고,\n"
        "배신과 이반이 잇따랐다."
    ),
    4031: (
        "\x1bCA노부나가\x1bCZ의 아우 \x1bCA노부카쓰\x1bCZ를\n"
        "새 당주로 세우려는 움직임까지 드러났다……"
    ),
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    3930: ["dynamic_takeda_shingen_name_requires_officer_overlay_review"],
    3934: ["central_and_northern_shinano_labels_require_glossary_review"],
    3935: ["chiisagata_reading_requires_glossary_review"],
    3945: ["toishi_rout_term_requires_glossary_review"],
    3946: ["oe_clan_reading_requires_review"],
    3949: ["inoue_motokane_name_reading_requires_review"],
    3963: ["waka_and_saikoku_terms_require_glossary_review"],
    3967: ["haruhide_relationship_and_name_require_review"],
    3968: ["source_has_no_manual_linebreak_runtime_wrap_review_required"],
    3981: ["taineiji_reading_requires_glossary_review"],
    3983: ["buddhist_death_verse_requires_specialist_review"],
    3988: ["henki_name_changes_require_glossary_review"],
    3994: ["positive_tone_resolved_against_sc_jp_due_en_conflict"],
    3997: ["sentoin_reading_requires_review"],
    4003: ["hosokawa_kanrei_lineage_term_requires_glossary_review"],
    4029: ["incense_powder_funeral_term_requires_glossary_review"],
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
    if len(ids) != 102 or ids != sorted(TRANSLATIONS):
        raise ValueError("batch8 ids are not the exact 102 displayed entries")
    return ids


def event_for(entry_id: int) -> str:
    matches = [
        event["event_id"]
        for event in EVENTS
        if event["start_id"] <= entry_id <= event["end_id"]
    ]
    if len(matches) != 1:
        raise ValueError(f"id {entry_id} does not map to one batch8 event group")
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
            f"batch8 range contains all-language shared internal keys: {display_failures}"
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
        3929,
        3930,
        3945,
        3946,
        3961,
        3962,
        3990,
        3991,
        4002,
        4003,
        4011,
        4012,
        4031,
        4032,
    )
    evidence = {
        "schema": "nobu16.kr.event-dialogue-alignment-evidence.v8",
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
        "schema": "nobu16.kr.event-dialogue-review-index.v8",
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
        raise ValueError("batch8 public artifact contains source-script text")

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
    validation = {
        "schema": "nobu16.kr.event-dialogue-generation-validation.v8",
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
            "entries_over_32": entries_over_32,
            "source_fixed_linebreak_exceptions": [
                entry_id
                for entry_id in entries_over_32
                if "\n" not in tables["SC"].texts[entry_id]
            ],
            "runtime_layout_review_required": True,
        },
        "font_integration": {
            "state": "deferred_not_computed",
            "current_font_or_installer_must_not_include_batch8": True,
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
            "existing_v01_v02_v03_v04_v05_v06_v07_artifacts_modified": False,
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
