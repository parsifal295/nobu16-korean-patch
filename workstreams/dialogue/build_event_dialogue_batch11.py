#!/usr/bin/env python3
"""Build source-free Korean historical event dialogue batch11 (4280-4417)."""

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
import build_event_dialogue_batch10 as shared  # noqa: E402


BATCH_ID = "msgev_historical_events_4280_4417.v0.11"
OVERLAY_NAME = "msgev_ko_historical_events_4280_4417.v0.11.json"
EVIDENCE_NAME = "alignment_evidence.v0.11.json"
REVIEW_NAME = "review_index.v0.11.json"
VALIDATION_NAME = "validation.v0.11.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 4280
SCOPE_END = 4417
EXCLUDED_INTERNAL_IDS: tuple[int, ...] = ()
BRACKET_TOKEN_RE = shared.BRACKET_TOKEN_RE

EVENTS = (
    {
        "event_id": "kagetora_priesthood_disturbance",
        "title_ko": "가게토라 출가 소동",
        "start_id": 4280,
        "end_id": 4314,
        "selected_count": 35,
    },
    {
        "event_id": "battle_of_ino_and_nobukatsu_pardon",
        "title_ko": "이노 전투와 노부카쓰의 사면",
        "start_id": 4315,
        "end_id": 4357,
        "selected_count": 43,
    },
    {
        "event_id": "fall_of_ouchi_clan",
        "title_ko": "오우치 가문의 멸망",
        "start_id": 4358,
        "end_id": 4376,
        "selected_count": 19,
    },
    {
        "event_id": "toshiie_and_matsu_marriage",
        "title_ko": "도시이에와 마쓰의 혼인",
        "start_id": 4377,
        "end_id": 4386,
        "selected_count": 10,
    },
    {
        "event_id": "akamatsu_harumasa_exile",
        "title_ko": "아카마쓰 하루마사의 추방",
        "start_id": 4387,
        "end_id": 4400,
        "selected_count": 14,
    },
    {
        "event_id": "ukita_naoie_death",
        "title_ko": "우키타 나오이에의 죽음",
        "start_id": 4401,
        "end_id": 4411,
        "selected_count": 11,
    },
    {
        "event_id": "harunobu_becomes_shingen",
        "title_ko": "하루노부, 신겐으로 개명",
        "start_id": 4412,
        "end_id": 4417,
        "selected_count": 6,
    },
)

TRANSLATIONS: dict[int, str] = {
    4280: (
        "이 무렵, \x1bCC에치고 가스가야마성\x1bCZ에서는\n"
        "\x1bCA[bs1448]\x1bCZ 가신들이 큰 혼란에 빠져 있었다."
    ),
    4281: (
        "당주 \x1bCA[bm1448]\x1bCZ가 모든 정무를 내팽개치고,\n"
        "\x1bCC비샤몬도\x1bCZ에 틀어박힌 채\n"
        "도무지 나오지 않았기 때문이다……"
    ),
    4282: "벌써 닷새가 넘도록 나오지 않으시다니!",
    4283: "대체 무슨 일이신지……",
    4284: "아!\n나오셨다!",
    4285: (
        "……결심했다.\n"
        "\x1bCB[bs1448] 가문\x1bCZ의 당주 자리에서 물러나,\n"
        "곧바로 출가하겠다……"
    ),
    4286: (
        "갑자기 무슨 말씀이십니까!\n"
        "은거하시기에는 아직 너무 젊으신데,\n"
        "농담도 지나치십니다……"
    ),
    4287: (
        "농담이 아니다.\n"
        "반드시 출가하겠다!\n"
        "지금부터 \x1bCC고야산\x1bCZ으로 떠난다!"
    ),
    4288: (
        "\x1bCA[bm1448]\x1bCZ는 겨우 \x1bCC비샤몬도\x1bCZ에서 나온 뒤,\n"
        "갑작스레 출가를 선언하여,\n"
        "가신들을 더 큰 혼란에 빠뜨렸다."
    ),
    4289: (
        "\x1bCB[bs1448] 가문\x1bCZ을 섬기며 \x1bCA[bm1448]\x1bCZ 옹립에 힘쓴\n"
        "\x1bCA오쿠마 도모히데\x1bCZ마저 혼란을 틈타 \x1bCB다케다 가문\x1bCZ과\n"
        "손잡고 반기를 들었다……"
    ),
    4290: (
        "다급해진 가신들은 \x1bCA[bm1448]\x1bCZ를 막을 유일한 인물,\n"
        "그 스승 \x1bCA덴시쓰 고이쿠\x1bCZ에게 도움을 청했다."
    ),
    4291: (
        "주군께서는 무조건 출가하겠다는 말씀뿐입니다……\n"
        "\x1bCA고이쿠\x1bCZ 님께서 부디,\n"
        "마음을 돌리도록 간언해 주시겠습니까?"
    ),
    4292: (
        "흐음…… 소승은 평소 \x1bCA[bm1448]\x1bCZ의 편지를 받기에,\n"
        "\x1bCA가게토라\x1bCZ가 무엇을 불안해하는지\n"
        "알고 있소."
    ),
    4293: (
        "그렇다면…… 대체 무엇입니까?\n"
        "\x1bCA[bm1448]\x1bCZ 님은 무엇을 근심하여 출가하려 하십니까?"
    ),
    4294: (
        "그대들 스스로 가슴에 손을 얹고 생각해 보라!\n"
        "답은 그 안에 있느니라……"
    ),
    4295: (
        "송구하오나 지금은 선문답을\n"
        "나눌 때가 아닙니다!\n"
        "한시라도 빨리 \x1bCA[bm1448]\x1bCZ 님을 막아야……"
    ),
    4296: (
        "선문답이 아니다. \x1bCA[bm1448]\x1bCZ를 가장 괴롭힌 근심은……\n"
        "바로 그대들 \x1bCB[bs1448] 가문\x1bCZ의 가신과\n"
        "\x1bCB에치고 고쿠진\x1bCZ의 행실이다!"
    ),
    4297: "뭐라고……!",
    4298: (
        "밖에는 \x1bCB다케다\x1bCZ와 잇코잇키 같은 적이 있고,\n"
        "안에는 \x1bCA오쿠마\x1bCZ 같은 역도가 있으니,\n"
        "\x1bCC에치고\x1bCZ는 지금 전례 없는 위기에 놓였다."
    ),
    4299: (
        "그런데도 그대들은 \x1bCC에치고\x1bCZ를 이끄는 슈고다이\n"
        "\x1bCA[b1448]\x1bCZ의 명을 따르지 않고, 저마다의 이해로\n"
        "대립하며 서로 미워하고 있지 않느냐!"
    ),
    4300: "크윽…… 반박할 말이 없습니다.",
    4301: (
        "다사다난한 때일수록 가장 필요한 것은\n"
        "모두 하나로 뭉치는 유대가 아니겠느냐."
    ),
    4302: (
        "\x1bCA[bm1448]\x1bCZ는 \x1bCB[bs1448] 가문\x1bCZ의 결속을 못 느껴\n"
        "출가하겠다고 한 것이다. 소승이 어떤\n"
        "간언을 해도 소용없을 터……"
    ),
    4303: (
        "우리 때문에 \x1bCA가게토라\x1bCZ 님께서 출가하신다면,\n"
        "우리가 하나로 뭉쳐 \x1bCA가게토라\x1bCZ 님을 받들겠다고\n"
        "맹세하는 수밖에 없겠군."
    ),
    4304: (
        "\x1bCA나가오 마사카게\x1bCZ는 가신과 고쿠진을 두루 설득했고,\n"
        "가신들은 연명으로 \x1bCA가게토라\x1bCZ에게 충성을 맹세하는\n"
        "서장을 만들었다."
    ),
    4305: (
        "성에서 보는 \x1bCC에치고\x1bCZ의 산들도 이제 마지막인가……\n"
        "그럼 \x1bCC고야산\x1bCZ으로 떠나자."
    ),
    4306: (
        "잠시만 기다리십시오! \x1bCA[bm1448]\x1bCZ 님,\n"
        "\x1bCC고야산\x1bCZ행을 다시 생각해 주십시오.\n"
        "먼저 이것을 보아 주십시오!"
    ),
    4307: (
        "이것은…… 가신들의 연서장?\n"
        "그럼 모두가 내 근심을 이해해 준 것인가!"
    ),
    4308: (
        "모든 가신이 \x1bCC가스가야마\x1bCZ에 인질을 보내,\n"
        "충절의 증표로 삼는 일도 받아들였습니다."
    ),
    4309: (
        "그런가…… 내가 슈고다이를 이은 뒤 오랫동안\n"
        "이루지 못한 \x1bCB에치고 무사단\x1bCZ의 단결이\n"
        "마침내 이루어진 것인가……"
    ),
    4310: (
        "부디 다시 생각해 주십시오!\n"
        "가신들의 이 열의를 보시고도,\n"
        "아직 출가의 뜻을 거두지 않으시겠습니까!"
    ),
    4311: (
        "아니다. 모두의 성의…… 감사히 받겠다.\n"
        "지금 성으로 돌아가 정무에 복귀하겠다!\n"
        "매형께도 고생을 끼쳤군."
    ),
    4312: (
        "아니, 별말씀을.\n"
        "이제부터가 \x1bCB[bs1448] 가문\x1bCZ의 재출발이오.\n"
        "나는 그저 조금 도왔을 뿐이오."
    ),
    4313: (
        "\x1bCA[bm1448]\x1bCZ의 출가 선언으로 \x1bCC에치고\x1bCZ 무사들은 뭉쳤고,\n"
        "\x1bCA[bm1448]\x1bCZ의 지휘로 \x1bCA오쿠마\x1bCZ를 꺾어 \x1bCC엣추\x1bCZ로 내쫓았다."
    ),
    4314: (
        "\x1bCA[bm1448]\x1bCZ는 국내의 인심을 하나로 모은 뒤,\n"
        "마침내 외부의 적 \x1bCB다케다 가문\x1bCZ과 맞설\n"
        "각오를 새로이 다졌다."
    ),
    4315: (
        "\x1bCA오다 간주로 노부카쓰\x1bCZ――\n"
        "이름은 \x1bCA노부유키\x1bCZ, 또는 \x1bCA다쓰나리\x1bCZ라고도 했다.\n"
        "\x1bCA사부로 노부나가\x1bCZ의 유일한 친동생이었다."
    ),
    4316: (
        "파천황의 멍청이라 불린 형과 달리,\n"
        "예의 바르고 성실한 \x1bCA노부카쓰\x1bCZ는\n"
        "가신들도 그 성장을 기대했다."
    ),
    4317: (
        "아버지가 죽은 뒤에도 \x1bCA노부나가\x1bCZ의 행실은 그대로였고,\n"
        "품행이 바른 \x1bCA노부카쓰\x1bCZ가 \x1bCB오다\x1bCZ의 당주에 알맞다는\n"
        "목소리가 커지며 형제 사이는 틀어졌다."
    ),
    4318: (
        "마침내 \x1bCA노부카쓰\x1bCZ도 자신을 향한 기대에 부응하여,\n"
        "형을 밀어내고 당주가 되겠다는 야심을 품기 시작했다……"
    ),
    4319: (
        "그리고 \x1bCA노부나가\x1bCZ가 의지하던 장인\n"
        "\x1bCA사이토 도산\x1bCZ이 죽은 일을 계기로,\n"
        "사태는 크게 움직이기 시작했다."
    ),
    4320: "뭐, \x1bCA간주로\x1bCZ가?",
    4321: (
        "예!\n"
        "공공연히 주군께 반기를 들었습니다.\n"
        "가신 중에도 \x1bCA노부카쓰\x1bCZ 님을 따르는 자가 많아……"
    ),
    4322: "호오.\n누구누구냐?",
    4323: (
        "\x1bCA하야시 히데사다\x1bCZ와 아우 \x1bCA미마사카노카미\x1bCZ,\n"
        "그리고 \x1bCA시바타 곤로쿠 가쓰이에\x1bCZ 등입니다……"
    ),
    4324: (
        "\x1bCA곤로쿠\x1bCZ마저 나를 버리고 \x1bCA간주로\x1bCZ에게 붙었나……\n"
        "흥, 재미있군.\n"
        "한꺼번에 따끔한 맛을 보여 주마."
    ),
    4325: (
        "\x1bCA노부나가\x1bCZ와 \x1bCA노부카쓰\x1bCZ 형제의 군대가 \x1bCC이노\x1bCZ에서 맞붙었다.\n"
        "형보다 두 배 넘는 병력이라 \x1bCA노부카쓰\x1bCZ가 유리해 보였다."
    ),
    4326: (
        "하지만 평소의 멍청이 같은 모습과 달리,\n"
        "\x1bCA노부나가\x1bCZ가 직접 선두에서 돌격하자\n"
        "아시가루들이 분발해 전세를 뒤집었다."
    ),
    4327: (
        "반란군이라는 거리낌을 품은 \x1bCA노부카쓰\x1bCZ 측 장병들은\n"
        "전장에서 \x1bCA노부나가\x1bCZ의 호통을 듣자,\n"
        "싸우지도 않고 달아난 자가 많았다고 한다."
    ),
    4328: (
        "형의 압도적인 강함을 본 \x1bCA노부카쓰\x1bCZ는,\n"
        "\x1bCC스에모리성\x1bCZ으로 몰리고 말았다."
    ),
    4329: "말도 안 돼…… 이렇게 쉽게…… 패하다니!",
    4330: (
        "\x1bCC오와리\x1bCZ 사람들은 모두 형에게 질렸어!\n"
        "다들 내가 당주가 되길 바랐잖아!\n"
        "그렇지 않느냐, \x1bCA가쓰이에\x1bCZ!"
    ),
    4331: "그러하옵니다……\n변명의 여지가 없습니다.",
    4332: (
        "(설마 그 멍청이 주군이 그토록 강할 줄이야……\n"
        "　그나저나 참으로 훌륭한 싸움이었다……)"
    ),
    4333: (
        "크윽…… 어찌해야 하지?\n"
        "형이라면 절대 나를 용서하지 않을 텐데.\n"
        "차라리 다른 가문에 항복할까……"
    ),
    4334: "아뢰옵니다!\n적진에서 사자가 왔습니다.",
    4335: (
        "이런 때에 사자라니 무슨 뜻이냐!\n"
        "서, 설마 항복을 권해 놓고 속여 죽이려는가!?\n"
        "그 수에는 넘어가지 않는다!!"
    ),
    4336: (
        "아닙니다. \x1bCA노부나가\x1bCZ 님께서……\n"
        "\x1bCA노부카쓰\x1bCZ 님을 용서하시겠다고 합니다.\n"
        "두 분의 어머님께서 중재하셨다 합니다……"
    ),
    4337: (
        "그런 까닭이다, \x1bCA노부카쓰\x1bCZ.\n"
        "어머님의 부탁이니 이번에는 용서해 주마!\n"
        "다만 이 성은 몰수한다."
    ),
    4338: "혀, 형님!\n어째서 여기에……?",
    4339: (
        "쓸데없는 문답을 나눌 여유가 있느냐?\n"
        "내 마음이 바뀌기 전에 어머님께\n"
        "감사드리러 가는 편이 낫지 않겠느냐?"
    ),
    4340: (
        "히익……\n"
        "지, 지당하십니다!\n"
        "여, 역시 형님이십니다!"
    ),
    4341: (
        "자…… \x1bCA곤로쿠\x1bCZ, 어떠냐?\n"
        "조금은 정신이 들었느냐?"
    ),
    4342: "\x1bCA노부카쓰\x1bCZ 님을 정말 용서하시는 것입니까?",
    4343: (
        "방금 말한 그대로다. 애초에 이번 일은,\n"
        "어리석은 아우가 장난을 친 것뿐이다.\n"
        "용서고 뭐고 털끝만큼도 신경 쓰지 않는다!"
    ),
    4344: (
        "그보다 \x1bCA가쓰이에\x1bCZ!\n"
        "나는 네가 이제 어찌할지가 더 궁금하다."
    ),
    4345: "……물론 할복하여 사죄하겠습니다.",
    4346: (
        "하하하!\n"
        "참으로 시시한 대답이군.\n"
        "너는 정말 재미없는 사내다, \x1bCA가쓰이에\x1bCZ!"
    ),
    4347: (
        "하지만 네 싸움 솜씨는 으뜸이더군!\n"
        "이토록 가슴 뛰는 싸움은 처음이었다."
    ),
    4348: (
        "어떠냐,\n"
        "그 시시한 배를 내게 맡기지 않겠느냐?\n"
        "나는 아직 네 싸움을 더 보고 싶다!"
    ),
    4349: (
        "……\x1bCA노부나가\x1bCZ 님께서,\n"
        "\x1bCB오다\x1bCZ의 당주가 될 그릇이라면 말입니다."
    ),
    4350: (
        "무슨 말을 하나 했더니…… 그런 것이냐.\n"
        "그래, 애초에 나는\n"
        "\x1bCB오다\x1bCZ의 당주가 될 그릇이 아닐지도 모르지."
    ),
    4351: "그렇다면 거절하겠습니다……",
    4352: (
        "나는 처음부터 \x1bCB오다\x1bCZ 가문 따위는 보지 않았다.\n"
        "천하의 주인이 될 사내이기 때문이다.\n"
        "\x1bCB오다\x1bCZ라는 그릇은 내게 너무 작다!"
    ),
    4353: "천하!?\n그런…… 허, 허황된 말씀을!",
    4354: (
        "허황되다 생각하면 나를 따라와라.\n"
        "내 곁에서 끝까지 지켜보아라!"
    ),
    4355: (
        "(혹시…… 정말로\n"
        "　천하를…… 아니, 설마.)"
    ),
    4356: (
        "\x1bCA노부카쓰\x1bCZ의 반란은 싱겁게 끝났다.\n"
        "어머니 \x1bCA도타고젠\x1bCZ의 중재로,\n"
        "\x1bCA노부카쓰\x1bCZ와 그를 따른 자들은 목숨을 건졌다."
    ),
    4357: (
        "비 온 뒤 땅이 굳는다는 말처럼, 이 싸움으로 \x1bCA노부나가\x1bCZ는\n"
        "\x1bCB오다 가문\x1bCZ 당주의 지위를 굳혔다."
    ),
    4358: (
        "\x1bCB오우치 가문\x1bCZ은 헤이안 말기부터 스오노스케를 맡았고,\n"
        "무로마치 시대에는 사이고쿠 제일의 세력을 이룬\n"
        "명문 중의 명문이었다."
    ),
    4359: (
        "\x1bCA오우치 마사히로\x1bCZ는 오닌의 난에서 서군의 중진이 되었고,\n"
        "그 아들 \x1bCA오우치 요시오키\x1bCZ는 \x1bCA호소카와 다카쿠니\x1bCZ와 상경해,\n"
        "간레이 대리로 막부 정치를 맡았다."
    ),
    4360: (
        "\x1bCA요시오키\x1bCZ의 아들 \x1bCA요시타카\x1bCZ도 지방 센고쿠 다이묘로서는\n"
        "이례적인 종2위까지 올라 영화를 누렸으나,\n"
        "\x1bCA스에 하루카타\x1bCZ의 모반으로 목숨을 잃었다."
    ),
    4361: (
        "그 \x1bCA하루카타\x1bCZ가 이쓰쿠시마 전투에서 죽자,\n"
        "\x1bCA하루카타\x1bCZ가 떠받든 당주 \x1bCA요시나가\x1bCZ의 위신도 추락했다.\n"
        "\x1bCB오우치 가문\x1bCZ은 계속 쇠퇴해 갔다."
    ),
    4362: (
        "\x1bCA스에 하루카타\x1bCZ를 멸한 \x1bCB모리 가문\x1bCZ의 마수는 마침내\n"
        "\x1bCA오우치 요시나가\x1bCZ의 눈앞까지 다가왔다.\n"
        "명문의 종말이 가까워지고 있었다……"
    ),
    4363: (
        "내가 대체 무얼 했단 말이냐!\n"
        "어째서 \x1bCA모리 모토나리\x1bCZ는 나를 적대하는가?\n"
        "\x1bCA하루카타\x1bCZ를 잃은 내가 원망한다면 모를까……"
    ),
    4364: (
        "생각해 보면…… 내 인생은 무엇이었나.\n"
        "\x1bCA스에 하루카타\x1bCZ가 나를 \x1bCB오토모 가문\x1bCZ에서 데려와,\n"
        "선대 당주 \x1bCA요시타카\x1bCZ 공을 몰아내고……"
    ),
    4365: (
        "사이고쿠 제일이라는 \x1bCB오우치\x1bCZ의 당주가 되어도,\n"
        "내게는 아무런 자유도 없었다……\n"
        "실권은 모두 \x1bCA하루카타\x1bCZ가 쥐고 있었다……"
    ),
    4366: (
        "나는 무엇을 위해 \x1bCC규슈\x1bCZ에서\n"
        "양자로 온 것이냐?\n"
        "꼭두각시가 되기 위해서였나?"
    ),
    4367: (
        "그 \x1bCA하루카타\x1bCZ를 죽인 \x1bCB모리\x1bCZ가 마침내\n"
        "\x1bCB오우치\x1bCZ의 본거지까지 쳐들어오는구나.\n"
        "내게는 이제 \x1bCA하루카타\x1bCZ 같은 군사도 없다……"
    ),
    4368: (
        "이미 \x1bCB오우치 가문\x1bCZ의 주요 무장은 죽거나 달아났고,\n"
        "\x1bCB모리군\x1bCZ이 포위한 \x1bCC조후쿠지\x1bCZ에는\n"
        "\x1bCA요시나가\x1bCZ와 얼마 안 되는 병사만 남았다……"
    ),
    4369: (
        "허울뿐인 당주로 떠받들린 끝에,\n"
        "한 수 아래라 여기던 \x1bCB모리\x1bCZ에게 몰리다니,\n"
        "\x1bCA오우치 요시나가\x1bCZ 공…… 참으로 가련한 분이로다."
    ),
    4370: (
        "하지만 여기서 멸망해 주어야겠소.\n"
        "한때 영화를 누린 가문도 힘을 잃었다면,\n"
        "새로운 세력에 자리를 내주어야 하는 법."
    ),
    4371: (
        "사이고쿠 제일의 명문 \x1bCB오우치 가문\x1bCZ을 쓰러뜨리고,\n"
        "\x1bCB모리\x1bCZ의 이름을 새로운 \x1bCC주고쿠\x1bCZ의 패자로 떨친다.\n"
        "이 또한 센고쿠의 이치로다……"
    ),
    4372: (
        "흥…… 새 시대에 필요 없는 자가 언제까지고\n"
        "푸념을 늘어놓아도 소용없지.\n"
        "남은 길은 후진에게 속히 넘겨주는 것뿐인가."
    ),
    4373: (
        "그렇다면 마지막만큼은,\n"
        "명문의 막을 내리기에 걸맞게\n"
        "훌륭히 할복하여 생을 마치리라……!"
    ),
    4374: (
        "“스러지게 한다고 무엇을 원망하랴.\n"
        "때가 오면 폭풍 없이도 꽃은 지는 것을.”"
    ),
    4375: (
        "이렇게 헤이안 시대부터 이어진 명문 \x1bCB오우치 가문\x1bCZ은,\n"
        "17대 400년에 걸친 역사의 막을 내렸다……"
    ),
    4376: (
        "그 자리를 대신해 \x1bCB오우치\x1bCZ를 멸한 \x1bCB모리 가문\x1bCZ이,\n"
        "새로운 대다이묘로서\n"
        "\x1bCC주고쿠 지방\x1bCZ에 군림하게 되었다."
    ),
    4377: "\x1bCB오다 가문\x1bCZ 본거지――",
    4378: (
        "‘창의 마타자’.\n"
        "사람들은 창으로 무공을 쌓은 사내,\n"
        "\x1bCA마에다 도시이에\x1bCZ를 그렇게 불렀다."
    ),
    4379: (
        "\x1bCA노부나가\x1bCZ 측근의 정예, 아카호로슈의\n"
        "필두로 중용되기에 이른 \x1bCA도시이에\x1bCZ는,\n"
        "가정을 꾸리기로 결심했다."
    ),
    4380: (
        "아버지는 돌아가시고, 어머니에게는 쫓겨나고……\n"
        "마쓰, 네가 더 고생할 까닭은 없어."
    ),
    4381: "서방님……",
    4382: (
        "네가 이제부터 맞이할 나날은,\n"
        "마음 편하고 행복한 매일이다.\n"
        "그 나날을 지키는 건 내 몫이야."
    ),
    4383: (
        "그리고 언젠가 우리 아이가 태어나면,\n"
        "이번에는 우리가 아버지와 어머니가 되어\n"
        "아이들을 지켜 주자!"
    ),
    4384: "……예!",
    4385: (
        "어릴 때부터 남매처럼 자란 두 사람은,\n"
        "이렇게 평생의 연을 맺었다."
    ),
    4386: (
        "\x1bCA도시이에\x1bCZ와 아내 \x1bCA마쓰\x1bCZ는,\n"
        "훗날 두 아들과 아홉 딸을 두었으며,\n"
        "오늘날까지 금실 좋은 부부로 전해진다."
    ),
    4387: (
        "\x1bCB아카마쓰 가문\x1bCZ은 가키쓰의 변에서 쇼군\n"
        "\x1bCA아시카가 요시노리\x1bCZ를 암살해 막부의 추토로 멸망했으나,\n"
        "오닌의 난에서 세운 공을 인정받아 부활했다."
    ),
    4388: (
        "그 뒤에도 \x1bCB쇼군가\x1bCZ와 간레이 \x1bCB호소카와 가문\x1bCZ에 밀접히 얽혀,\n"
        "중앙 정계와 관계를 이어 간 반면,\n"
        "본거지 \x1bCC하리마\x1bCZ의 지배력은 약해졌다."
    ),
    4389: (
        "슈고다이 \x1bCB우라가미 가문\x1bCZ의 흥기, \x1bCB아마고 가문\x1bCZ의 침입……\n"
        "여러 요인으로 \x1bCB아카마쓰 가문\x1bCZ의 지배지는 줄었고,\n"
        "하리마 슈고는 이름뿐인 존재가 되었다."
    ),
    4390: (
        "요즘 \x1bCB우라가미 가문\x1bCZ은 이제 본가의 은혜도 잊고,\n"
        "마치 독립한 다이묘처럼\n"
        "행세하고 있다……"
    ),
    4391: (
        "이웃 \x1bCB아마고 가문\x1bCZ도,\n"
        "\x1bCC비젠\x1bCZ과 \x1bCC미마사카\x1bCZ에 그치지 않고 하리마 슈고직까지 노리며,\n"
        "마수를 뻗쳐 오는 형편……"
    ),
    4392: (
        "그런데 당주 \x1bCA하루마사\x1bCZ 님은 패기도 없이,\n"
        "가운을 기울게 할 뿐인 분……\n"
        "이대로라면 \x1bCB아카마쓰\x1bCZ의 미래는 없다."
    ),
    4393: (
        "차라리 일찍 은거하시고,\n"
        "후계자 \x1bCA지로\x1bCZ 님께 가독을 넘기시면\n"
        "좋으련만……"
    ),
    4394: (
        "\x1bCB아카마쓰\x1bCZ 가신들은 당주 \x1bCA하루마사\x1bCZ를 내쫓으려 몰래 꾀하고,\n"
        "\x1bCA하루마사\x1bCZ의 적장자 \x1bCA요시스케\x1bCZ를\n"
        "옹립할 길을 찾았다."
    ),
    4395: (
        "\x1bCA요시스케\x1bCZ도 가문의 기대에 부응하여,\n"
        "아버지 \x1bCA하루마사\x1bCZ의 추방을 받아들였다.\n"
        "그리고 결행의 날이 찾아왔다……"
    ),
    4396: "이놈들……\n나를 내쫓겠다는 것이냐!",
    4397: (
        "이제 \x1bCB아카마쓰 가문\x1bCZ을 위해 아버님은 필요 없습니다.\n"
        "앞으로는 이 \x1bCA요시스케\x1bCZ에게 모든 일을 맡기고,\n"
        "편안히 은거하시는 게 좋겠습니다……"
    ),
    4398: "닥쳐라!\n나는 인정 못 한다. 인정 못 해!",
    4399: (
        "\x1bCA하루마사\x1bCZ는 끝까지 저항했으나,\n"
        "가신 대부분이 \x1bCA요시스케\x1bCZ를 지지했고,\n"
        "실의에 빠진 \x1bCA하루마사\x1bCZ는 마침내 성을 떠났다……"
    ),
    4400: (
        "그 뒤 사위 \x1bCA아카마쓰 마사히데\x1bCZ에게 의지해\n"
        "다시 저항했으나, 그마저 실패했다.\n"
        "결국 이웃 나라로 몰락해 갔다……"
    ),
    4401: (
        "크윽……\n"
        "분하구나!!\n"
        "뜻도 이루지 못하고…… 이렇게 죽어야 한단 말인가!"
    ),
    4402: (
        "\x1bCC비젠\x1bCZ의 효웅이라 불리며 배신도 속임수도\n"
        "마다하지 않고 온갖 책모를 부린 사내가,\n"
        "마지막 순간을 맞으려 하고 있었다……"
    ),
    4403: (
        "후계자 \x1bCA하치로\x1bCZ는 아직 어리다.\n"
        "내가 여기서 쓰러지면 \x1bCA나오이에\x1bCZ가 한 대에 일군\n"
        "\x1bCB우키타 가문\x1bCZ도 어찌 될지 모른다……"
    ),
    4404: (
        "\x1bCA하치로\x1bCZ……! 내가 세상을 뜨면,\n"
        "오직 \x1bCA[b754]\x1bCZ 공을 의지하여라.\n"
        "그 이름 한 자를 받아 \x1bCA히데이에\x1bCZ라 자칭하거라……"
    ),
    4405: "아버님!\n그런 약한 말씀은 마십시오……!",
    4406: (
        "아니다. 내 몸은 내가 잘 안다.\n"
        "여기서 죽는 건 원통하지만,\n"
        "이제 \x1bCB우키타\x1bCZ는 네게 맡기는 수밖에…… 없다."
    ),
    4407: "아버님……!",
    4408: "잘 들어라!\n\x1bCA[b754]\x1bCZ 공의 곁을 떠나지 마라!",
    4409: (
        "온갖 권모술수를 다한 이 사내의\n"
        "목숨을 앗아 간 것은,\n"
        "엉덩이에 난 커다란 종기였다고 한다."
    ),
    4410: (
        "그동안 \x1bCA나오이에\x1bCZ가 묻어 버린 수많은 적의 원한이\n"
        "뭉친 듯한 종기는 가라앉지 않았고,\n"
        "마침내 효웅을 죽음에 이르게 했다."
    ),
    4411: (
        "\x1bCB우키타 가문\x1bCZ은 젊은 \x1bCA히데이에\x1bCZ가 이었고,\n"
        "\x1bCA히데이에\x1bCZ는 아버지의 유언대로\n"
        "\x1bCA[b754]\x1bCZ를 의지하게 되었다……"
    ),
    4412: (
        "이 무렵, \x1bCA다케다 하루노부\x1bCZ는 갑자기 출가하여,\n"
        "법명을 ‘\x1bCA도쿠에이켄 신겐\x1bCZ’이라 했다."
    ),
    4413: (
        "본래 스와 대명신을 믿기는 했지만,\n"
        "불교와 그리 깊은 인연이 없던 사내였기에\n"
        "출가한 까닭은 분명하지 않다."
    ),
    4414: (
        "\x1bCA나가오 가게토라\x1bCZ와의 싸움에 전념하려고,\n"
        "기근의 해결을 빌려고, 또는 후계자\n"
        "\x1bCA요시노부\x1bCZ에게 슈고직을 넘기려고…… 여러 설이 있다."
    ),
    4415: (
        "나도 슬슬 마흔에 가까워졌다.\n"
        "불도라는 것에 구원을 구해도\n"
        "벌을 받지는 않겠지……"
    ),
    4416: (
        "부처를 공경하는 모습을 보인다면,\n"
        "싸움에만 빠져 백성에게도 버림받은\n"
        "아버지의 전철은 밟지 않겠지……"
    ),
    4417: (
        "그러나 출가한 뒤에도 \x1bCA하루노부\x1bCZ, 곧 \x1bCA신겐\x1bCZ은\n"
        "변함없이 모든 정무를 살폈고,\n"
        "당주로서 실권을 계속 쥐었다."
    ),
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    4290: ["tenshitsu_koiku_reading_requires_glossary_review"],
    4315: ["nobukatsu_aliases_require_historical_review"],
    4323: ["mimasaka_no_kami_title_rendering_requires_review"],
    4374: ["death_poem_requires_literary_review"],
    4378: ["yari_no_mataza_sobriquet_requires_glossary_review"],
    4385: ["nise_no_en_marriage_idiom_requires_style_review"],
    4412: ["tokueiken_shingen_reading_requires_glossary_review"],
}

PREVIOUS_ARTIFACT_PINS = {
    **shared.PREVIOUS_ARTIFACT_PINS,
    "evidence/alignment_evidence.v0.10.json": (
        "A1D8BE1BDF0CD801E5FBBEA2E99BB6B1D00957E792FD32C7637E0799981EF089"
    ),
    "public/msgev_ko_historical_events_4161_4279.v0.10.json": (
        "30C843032B2C8B7F8204840E02BEED3D67935F3E46770BF9C1EA889B5EEB763A"
    ),
    "review/review_index.v0.10.json": (
        "5D5C7CD307C88DCB4E54262C178094261E7319C1FE8AFFAD5C15C598D9ABD927"
    ),
    "validation.v0.10.json": (
        "D62BF8D021C6993523083C99CC83EA9E68699320FA79A038992D8FCF45D996C8"
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
    ids = list(range(SCOPE_START, SCOPE_END + 1))
    if len(ids) != 138 or ids != sorted(TRANSLATIONS):
        raise ValueError("batch11 ids are not the exact 138 displayed entries")
    return ids


def event_for(entry_id: int) -> str:
    matches = [
        event["event_id"]
        for event in EVENTS
        if event["start_id"] <= entry_id <= event["end_id"]
    ]
    if len(matches) != 1:
        raise ValueError(f"id {entry_id} does not map to one batch11 event group")
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
            f"batch11 range contains all-language shared internal keys: {display_failures}"
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
        details = {entry_id: visible_lengths[entry_id] for entry_id in entries_over_32}
        raise ValueError(f"authored lines exceed 32 codepoints: {details}")

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
        4279,
        4280,
        4314,
        4315,
        4357,
        4358,
        4376,
        4377,
        4386,
        4387,
        4400,
        4401,
        4411,
        4412,
        4417,
        4418,
    )
    evidence = {
        "schema": "nobu16.kr.event-dialogue-alignment-evidence.v11",
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
        "schema": "nobu16.kr.event-dialogue-review-index.v11",
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
        raise ValueError("batch11 public artifact contains source-script text")

    previous_after = previous_artifact_snapshot()
    installed_after = installed_resource_snapshot()
    if previous_before != previous_after:
        raise ValueError("previous dialogue artifact snapshot changed during build")
    if installed_before != installed_after:
        raise ValueError("installed msgev snapshot changed during build")

    validation = {
        "schema": "nobu16.kr.event-dialogue-generation-validation.v11",
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
            "current_font_or_installer_must_not_include_batch11": True,
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
            "dialogue_v01_v10_artifacts_before": previous_before,
            "dialogue_v01_v10_artifacts_after": previous_after,
            "installed_msgev_before": installed_before,
            "installed_msgev_after": installed_after,
        },
        "safety": {
            "installed_game_files_modified": False,
            "font_files_modified": False,
            "installer_modified": False,
            "root_readme_or_progress_modified": False,
            "common_builder_or_other_workstream_modified": False,
            "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_artifacts_modified": False,
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
