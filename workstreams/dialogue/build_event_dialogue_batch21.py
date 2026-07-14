#!/usr/bin/env python3
"""Build source-free Korean historical event dialogue batch21 (5629-5748)."""

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
import build_event_dialogue_batch20 as shared  # noqa: E402


source_shared = shared.source_shared
BATCH_ID = "msgev_historical_events_5629_5748.v0.21"
OVERLAY_NAME = "msgev_ko_historical_events_5629_5748.v0.21.json"
EVIDENCE_NAME = "alignment_evidence.v0.21.json"
REVIEW_NAME = "review_index.v0.21.json"
VALIDATION_NAME = "validation.v0.21.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 5629
SCOPE_END = 5748
EXCLUDED_INTERNAL_IDS: tuple[int, ...] = ()
BRACKET_TOKEN_RE = shared.BRACKET_TOKEN_RE

EVENTS = (
    {
        "event_id": "alliance_to_partition_imagawa",
        "title_ko": "이마가와 협공 동맹",
        "start_id": 5629,
        "end_id": 5639,
        "selected_count": 11,
    },
    {
        "event_id": "fall_of_the_amago_clan",
        "title_ko": "아마고 가문의 멸망",
        "start_id": 5640,
        "end_id": 5654,
        "selected_count": 15,
    },
    {
        "event_id": "ukita_naoie_declares_independence",
        "title_ko": "우키타 나오이에의 독립",
        "start_id": 5655,
        "end_id": 5676,
        "selected_count": 22,
    },
    {
        "event_id": "hojo_saburo_becomes_uesugi_kagetora",
        "title_ko": "호조 사부로가 우에스기 가게토라가 되다",
        "start_id": 5677,
        "end_id": 5697,
        "selected_count": 21,
    },
    {
        "event_id": "gamo_yasuhide_comes_of_age",
        "title_ko": "가모 야스히데의 원복",
        "start_id": 5698,
        "end_id": 5700,
        "selected_count": 3,
    },
    {
        "event_id": "amago_restoration_army_rises",
        "title_ko": "아마고 재흥군의 거병",
        "start_id": 5701,
        "end_id": 5720,
        "selected_count": 20,
    },
    {
        "event_id": "takeda_raid_and_battle_of_mimasetoge",
        "title_ko": "다케다의 오다와라 기습과 미마세토게 전투",
        "start_id": 5721,
        "end_id": 5748,
        "selected_count": 28,
    },
)

TRANSLATIONS: dict[int, str] = {
    5629: "이는 \x1bCB다케다 가문\x1bCZ의 중신 \x1bCA[b110]\x1bCZ이\n갑자기 \x1bCA[b1871]\x1bCZ의 거성을 찾아온\n무렵의 일이었다……",
    5630: "뭐라, 우리 가문과 동맹을……?\n무엇을 위해서요?",
    5631: "우리 뜻은 말할 것도 없소.\n두 가문이 \x1bCB이마가와 가문\x1bCZ을 협공하여\n\x1bCC스루가·도토미 두 나라\x1bCZ를 나눠 갖자는 제안이오.",
    5632: "무슨 말씀이시오. \x1bCB다케다\x1bCZ와 \x1bCB이마가와\x1bCZ는\n예부터 동맹이었소. 특히 후계자\n\x1bCA요시노부\x1bCZ 공은 \x1bCB이마가와\x1bCZ에서 아내를 맞았을 텐데.",
    5633: "그렇소. 하지만 오케하자마 전투 이래,\n\x1bCB이마가와 가문\x1bCZ은 쇠퇴할 뿐…… 주군 \x1bCA[bm1251]\x1bCZ께서는\n이미 \x1bCA이마가와 우지자네\x1bCZ를 버리셨소.",
    5634: "뭐라고……!",
    5635: "\x1bCA요시노부\x1bCZ 공은 이미 자결했고, 정실도\n\x1bCB이마가와 가문\x1bCZ으로 돌려보냈소. 반대파도 숙청했으니,\n우리 가문은 \x1bCB이마가와\x1bCZ 타도에 나설 것이오.",
    5636: "그렇군……\n\x1bCB다케다 가문\x1bCZ은 진심인 모양이오.\n그렇다면 동맹을 맺는 데 이의 없소.",
    5637: "\x1bCB다케다\x1bCZ와 \x1bCB[bs1871]\x1bCZ은\n각각 \x1bCC스루가\x1bCZ와 \x1bCC도토미\x1bCZ를 공략하여,\n\x1bCB이마가와 가문\x1bCZ을 멸망으로 이끕시다.",
    5638: "그렇다면 \x1bCC오이가와강\x1bCZ을\n양측 영지의 경계로 삼는 것이군.\n나쁘지 않다. 받아들이마!",
    5639: "이렇게 \x1bCB이마가와 가문\x1bCZ 타도를 목표로\n\x1bCB다케다\x1bCZ·\x1bCB[bs1871]\x1bCZ 동맹이 맺어졌다――",
    5640: "\x1bCC갓산토다성\x1bCZ은 과거 \x1bCB오우치\x1bCZ와 \x1bCB모리\x1bCZ 등\n적군의 공격을 몇 번이나 물리친 견성이었지만,\n이제 함락될 위기에 놓였다.",
    5641: "안 됩니다!\n여기서 \x1bCB모리\x1bCZ에게 항복하면\n지금까지의 노고가……!",
    5642: "하지만 나는 이제 싸움에 지쳤다……\n더는 모두를 괴롭히고 싶지 않다.\n여기서 \x1bCB모리\x1bCZ에게 항복하겠다.",
    5643: "성 안과 나라에 항전파가 남아 있었으나,\n당주 \x1bCA아마고 요시히사\x1bCZ는 \x1bCB모리군\x1bCZ에 항복하기로 했다.",
    5644: "마침내 결단했군.\n이것으로 전쟁은 끝이다!",
    5645: "부디 목숨만은 살려 주십시오.",
    5646: "안심하시오.\n항복한 자의 목숨은 빼앗지 않겠소.\n\x1bCA아마고\x1bCZ 공과 가신들은 \x1bCC아키\x1bCZ로 옮기시오.",
    5647: "\x1bCA아마고 요시히사\x1bCZ 등은 \x1bCB모리 가문\x1bCZ의 본국 \x1bCC아키\x1bCZ로\n이송되었으나, 항복을 받아들이지 않은\n\x1bCA야마나카 시카노스케\x1bCZ 등은 \x1bCC이즈모타이샤\x1bCZ에서 달아났다.",
    5648: "\x1bCA요시히사\x1bCZ 님, 우리는 \x1bCB아마고 가문\x1bCZ을 부흥시키려\n끝까지 싸우겠습니다!\n안녕히 계십시오!",
    5649: "아, \x1bCA시카노스케\x1bCZ……!\n가 버렸는가……",
    5650: "그들이 너무 요란하게 날뛰면,\n내 목숨도…… 위험해질 텐데.",
    5651: "이로써 센고쿠 다이묘 \x1bCB아마고 가문\x1bCZ은 멸망했다.\n이즈모 슈고다이였던 \x1bCA쓰네히사\x1bCZ가 기반을 닦은 뒤,\n한때 \x1bCC주고쿠 11개국\x1bCZ을 다스렸으나……",
    5652: "또 하나의 주고쿠 패자 \x1bCB오우치 가문\x1bCZ과 다투며\n쇠퇴했고, 신흥 세력 \x1bCB모리\x1bCZ에게 패하여\n불과 삼대 만에 운명이 다했다.",
    5653: "하지만 \x1bCB아마고 가문\x1bCZ의 혼은,\n로닌이 되어서도 주가 부흥을 꿈꾸는\n\x1bCA야마나카 시카노스케\x1bCZ 등에게 이어졌다.",
    5654: "한편 항복한 \x1bCA요시히사\x1bCZ는\n\x1bCC아키\x1bCZ에서 연금과 다름없는 삶을 보냈고, 사실상\n\x1bCB모리 가문\x1bCZ에 붙들린 채 생을 마쳤다고 한다……",
    5655: "\x1bCB우키타 가문\x1bCZ의 기원은 분명하지 않지만,\n센고쿠 시대 전기에 비젠 슈고다이 \x1bCA우라가미 무라무네\x1bCZ를 섬긴\n\x1bCA요시이에\x1bCZ가 두각을 드러내 \x1bCB우키타\x1bCZ의 이름을 높였다.",
    5656: "하지만 \x1bCA요시이에\x1bCZ가 살해된 뒤,\n뒤를 이은 \x1bCA오키이에\x1bCZ는 세력을 지키지 못해,\n\x1bCB우키타 가문\x1bCZ은 한때 몰락을 겪었다.",
    5657: "가문이 되살아난 것은 \x1bCA오키이에\x1bCZ의 아들 \x1bCA나오이에\x1bCZ 대였다.\n효웅이라 불린 그는 비정한 모략을\n망설임 없이 실행할 수 있는 사내였다.",
    5658: "암살, 독살, 속임수처럼,\n당시에도 꺼리던 수단을\n태연히 썼다……",
    5659: "자신의 친족은 물론,\n같은 주군을 섬기는 자처럼 감정상\n피하고 싶은 상대도 주저 없이 죽였다고 한다.",
    5660: "그런 난세의 화신 \x1bCA나오이에\x1bCZ에게,\n마지막 하극상의 기회가 찾아왔다.",
    5661: "우리는 강해지고 \x1bCB우라가미\x1bCZ는 쇠했다.\n이제 내 마지막 소원을 이룰 때인가……",
    5662: "\x1bCB우키타\x1bCZ는 \x1bCA요시이에\x1bCZ 대에 \x1bCB우라가미 가문\x1bCZ을 보필했지만,\n\x1bCB우라가미 가문\x1bCZ이 내분으로 쇠퇴하자,\n주종보다 대등하다는 의식이 싹텄다.",
    5663: "\x1bCA나오이에\x1bCZ는 전공을 세워 \x1bCA우라가미 무네카게\x1bCZ에게 빚을 지우고,\n때로는 대놓고 \x1bCB우라가미 가문\x1bCZ과 대립하면서도,\n\x1bCB우라가미\x1bCZ 가신 가운데 지지자를 늘려 갔다.",
    5664: "마침내 \x1bCB우라가미\x1bCZ 가신 대부분이\n\x1bCA나오이에\x1bCZ의 명령을 따르게 되어,\n주군 \x1bCA우라가미 무네카게\x1bCZ는 뒷전으로 밀렸다.",
    5665: "할아버지가 죽은 뒤 \x1bCB우라가미\x1bCZ는 어떤 도움도\n주지 않았으니, 우리에게 은혜란 없다.\n이제 형식뿐인 주군으로 받들 이유도 없지……",
    5666: "이제 \x1bCC비젠\x1bCZ의 진정한 주인이 누구인지……\n천하에 보이는 것도 나쁘지 않겠군.\n내가 \x1bCB우라가미\x1bCZ를 대신하리라!",
    5667: "\x1bCA나오이에\x1bCZ가 마침내 움직여\n\x1bCB우라가미 가문\x1bCZ에서 독립하려 했지만,\n\x1bCB우라가미\x1bCZ의 가신들은 조금도 동요하지 않았다.",
    5668: "\x1bCA나오이에\x1bCZ의 모반에 동조한 자가 많았고,\n오히려 적극적으로 지지한 장수마저 많았기 때문이다.",
    5669: "\x1bCA나오이에\x1bCZ!\n마침내 역신이 본색을 드러냈구나!\n모두 \x1bCA나오이에\x1bCZ를 쳐라!",
    5670: "\x1bCA무네카게\x1bCZ의 필사적인 호소를 따른 가신은 거의 없었고,\n권력은 평온하다 할 만큼 빠르게 넘어갔다.",
    5671: "쫓겨난 옛 주군 \x1bCA우라가미 무네카게\x1bCZ는 이후,\n몇 번이나 거성 탈환을 시도했지만 실패했다.\n그의 말년은 묘연하여 아무도 모른다.",
    5672: "이놈, \x1bCA나오이에\x1bCZ!\n절대로…… 절대로 용서하지 않겠다!",
    5673: "\x1bCA우라가미 무네카게\x1bCZ…… 생각하면 가엾은 분이었지.\n시대가 자신을 원하지 않는다는 사실을\n전혀 보지 못했으니 말이야!",
    5674: "자, 이제부터가 진짜다……\n내 모략이 이 난세에 어디까지 통할지\n시험해 보리라.",
    5675: "이렇게 \x1bCA우키타 나오이에\x1bCZ는 하극상을 이루고,\n\x1bCC비젠\x1bCZ의 다이묘로 독립에 성공했다.",
    5676: "센고쿠 다이묘 \x1bCA우키타 나오이에\x1bCZ――\n모장의 새로운 싸움이 이제 막을 올린다……",
    5677: "\x1bCB호조 가문\x1bCZ과 \x1bCB우에스기 가문\x1bCZ의 동맹.\n세상에서 말하는 ‘엣소 동맹’은……",
    5678: "처음에는 \x1bCA호조 우지마사\x1bCZ의 아들과 \x1bCA가키자키 가게이에\x1bCZ의 아들을\n서로 인질로 교환한다는\n조건이 있었지만,",
    5679: "\x1bCA호조 우지마사\x1bCZ가 거절하여,\n급히 \x1bCA우지야스\x1bCZ의 일곱째 아들 \x1bCA호조 사부로\x1bCZ가\n인질로 \x1bCC에치고\x1bCZ에 가게 되었다.",
    5680: "\x1bCA사부로\x1bCZ의 자세한 내력은 알려지지 않았으나,\n삼국제일이라 칭송받을 만큼 미남이었다고 한다.",
    5681: "처음 뵙겠습니다.\n\x1bCA호조 우지야스\x1bCZ의 아들 \x1bCA사부로\x1bCZ입니다.",
    5682: "호오, 네가……",
    5683: "…………",
    5684: "제법 훤칠하구나. 좋다.\n이제부터 \x1bCA가게토라\x1bCZ를 자칭하라!",
    5685: "……!\n뭐라고요!?",
    5686: "‘\x1bCA가게토라\x1bCZ’는 \x1bCA[b1448]\x1bCZ의 첫 이름이다.\n\x1bCB호조 가문\x1bCZ에서 온 \x1bCA사부로\x1bCZ에게 이 이름을 내린 것은,\n가신들의 예상을 뛰어넘은 후대였다.",
    5687: "더없는 영광입니다.\n하지만 어찌하여 제게\n이토록 큰 은정을 베푸십니까?",
    5688: "마땅한 보답을 하려는 것뿐……\n그대 영혼의 갈증이 우리 \x1bCB[bs1448]\x1bCZ에\n커다란 힘을 가져다주리라!",
    5689: "영혼의 갈증…… 말입니까?",
    5690: "그렇다.\n\x1bCB호조\x1bCZ에서 태어났으나,\n\x1bCB호조\x1bCZ에게 쓰이지 못하고 잊힌 그대는……",
    5691: "이 \x1bCC에치고\x1bCZ를 죽을 땅으로,\n이 \x1bCB우에스기\x1bCZ를 자신의 집으로 삼아,\n모든 것을 불태우리라.",
    5692: "곧 그대는 이 땅에서 생을 마칠 것이다.\n그 목숨에 보답하고자 내 이름을 주마!",
    5693: "(공명정대……\n　의에는 의로써 보답한다.\n　과연 비사문천의 화신 \x1bCA[b1448]\x1bCZ인가.)",
    5694: "(말씀하신 대로,\n　나는 이곳에 뼈를 묻을 각오로 왔다.)",
    5695: "(하지만 그것은 \x1bCB우에스기\x1bCZ를 위해서가 아니다.\n　내가 \x1bCB우에스기\x1bCZ를 손에 넣고,\n　나를 버린 \x1bCB호조\x1bCZ에게 복수하기 위해서다!)",
    5696: "…………",
    5697: "이렇게 \x1bCB호조 가문\x1bCZ에서 \x1bCB우에스기 가문\x1bCZ으로 간 \x1bCA사부로\x1bCZ는\n이름을 \x1bCA우에스기 가게토라\x1bCZ로 바꾸었다.",
    5698: "\x1bCA가모 가타히데\x1bCZ의 적자 \x1bCA가모 야스히데\x1bCZ.\n그 사내가 원복 의식을 마쳤다.",
    5699: "‘결코 보통 사람이 아닐 것’이라 평가받은\n그 날카로운 눈으로 천하의 앞날을 내다보며,\n훗날 문무에 뛰어난 재능을 펼치게 된다……",
    5700: "이 순간, 난세에\n\x1bCA가모 야스히데\x1bCZ라는 사내가 풀려났다.",
    5701: "\x1bCB아마고 가문\x1bCZ 멸망 뒤, 그 부흥만을 바라며\n각지를 떠돌아 공작해 온 \x1bCA야마나카 시카노스케\x1bCZ.\n그에게 한 줄기 빛이 비쳤다……",
    5702: "한때 \x1bCB아마고\x1bCZ 종가에 맞설 세력을 가졌다는 이유로\n숙청된 \x1bCB신구토\x1bCZ――\n그 생존자를 \x1bCC교토\x1bCZ에서 찾아낸 것이다.",
    5703: "\x1bCB신구토\x1bCZ의 \x1bCA아마고 사네히사\x1bCZ가 남긴 아들 \x1bCA가쓰히사\x1bCZ.\n숙청 때 \x1bCC교토\x1bCZ로 달아나,\n\x1bCC도후쿠지\x1bCZ의 승려가 된 인물이다.",
    5704: "바로 당신이 \x1bCB아마고\x1bCZ 부흥의 열쇠입니다.\n부디 우리의 기치가 되어 주십시오!",
    5705: "\x1bCA시카노스케\x1bCZ라고 했는가.\n그대의 열의에 감복했다.\n미력하나마 나로 좋다면 함께 걷겠네!",
    5706: "\x1bCB아마고\x1bCZ의 혈통을 이은 \x1bCA가쓰히사\x1bCZ를 추대하자,\n각지에 흩어졌던 \x1bCB아마고\x1bCZ 잔당도\n\x1bCA시카노스케\x1bCZ 일행에게 협력하기 시작했다.",
    5707: "지금이 기회다! \x1bCB아마고\x1bCZ 부흥을 바라는 이들이여!\n\x1bCB모리\x1bCZ의 빈틈을 찔러 \x1bCC이즈모\x1bCZ를…… \x1bCC갓산토다성\x1bCZ을\n우리 손으로 되찾자!",
    5708: "\x1bCA시카노스케\x1bCZ·\x1bCA가쓰히사\x1bCZ가 이끄는 \x1bCB아마고\x1bCZ 재흥군은\n\x1bCC오키섬\x1bCZ에서 거병했다. \x1bCC이즈모\x1bCZ에 상륙하자 순식간에\n세력을 넓히며 여러 성을 잇달아 함락했다.",
    5709: "\x1bCB아마고\x1bCZ 잔당이라고?\n끈질긴 놈들이군……\n그렇다면 이 \x1bCA모토하루\x1bCZ가 상대해 주마!",
    5710: "\x1bCC갓산토다성\x1bCZ을 지키는 자는, \x1bCB아마고\x1bCZ를 멸망으로\n몰아넣은 \x1bCA모리 모토나리\x1bCZ의 둘째 아들 \x1bCA깃카와 모토하루\x1bCZ인가!\n상대로 부족함이 없다!",
    5711: "저 사내는 분명 \x1bCB아마고\x1bCZ의 옛 가신……\n\x1bCA야마나카 시카노스케\x1bCZ라고 했나?\n재미있군, 덤벼라!",
    5712: "기세는 좋지만 저돌적인 무사로군.\n정면에서 상대할 필요는 없다.\n가볍게 흘려보내자.",
    5713: "\x1bCA야마나카 시카노스케\x1bCZ 일행은 선전했지만,\n\x1bCB모리 가문\x1bCZ의 교묘한 전략에 밀려\n\x1bCC이즈모\x1bCZ 탈환에 실패하고 붙잡혔다.",
    5714: "\x1bCA시카노스케\x1bCZ는 유폐되었으나,\n감시가 소홀한 틈에 탈출했다고 한다.",
    5715: "이 정도쯤이야!\n이 \x1bCA시카노스케\x1bCZ가 포기할 성싶으냐!\n목을 씻고 기다려라!",
    5716: "앗, 멈춰라!\n제길, 달아났나!",
    5717: "내버려 두어라.\n몇 번을 와도 다시 꺾으면 그만이다.",
    5718: "참 끈질긴 녀석들이군.\n하지만 그 \x1bCA시카노스케\x1bCZ라는 자의 솜씨는 아깝다.\n어떻게든 \x1bCB모리\x1bCZ에서 쓸 수 없을까?",
    5719: "무리일 겁니다……\n\x1bCA시카노스케\x1bCZ의 머릿속에는\n\x1bCB아마고\x1bCZ 부흥뿐인 듯하니까요.",
    5720: "\x1bCB모리\x1bCZ 영지에서 달아나 \x1bCA가쓰히사\x1bCZ 등과 합류한\n\x1bCA시카노스케\x1bCZ는 불굴의 정신으로 이후에도\n반\x1bCB모리\x1bCZ 투쟁에 일생을 바쳤다……",
    5721: "\x1bCB이마가와 가문\x1bCZ이 \x1bCA[b1251]\x1bCZ에게 멸망하자,\n옛 동맹 \x1bCB호조\x1bCZ는 분노해 \x1bCB다케다\x1bCZ와 싸우기로 하고,\n\x1bCB우에스기\x1bCZ와 화의를 맺었다.",
    5722: "마침내 \x1bCA호조 우지마사\x1bCZ가 대군을 이끌고,\n\x1bCC스루가\x1bCZ로 출진했다.",
    5723: "\x1bCB호조\x1bCZ의 애송이가 \x1bCC스루가\x1bCZ로 출진했다고?\n어디 한 번 놀려 주마.",
    5724: "\x1bCA[bm1251]\x1bCZ는 전군에 출진을 명했다.\n모두 \x1bCA호조 우지마사\x1bCZ의 \x1bCC스루가\x1bCZ 침공을\n막으러 가는 줄 알았지만……",
    5725: "\x1bCA[bm1251]\x1bCZ는 \x1bCA우지마사\x1bCZ의 움직임을 무시하듯\n\x1bCC스루가\x1bCZ로 가지 않고, \x1bCB우에스기군\x1bCZ을 견제하면서\n\x1bCC북간토\x1bCZ를 지나 서서히 남하했다.",
    5726: "그리고 뜻밖에도 다케다 대군은\n\x1bCB호조 가문\x1bCZ의 본거지 \x1bCC오다와라성\x1bCZ을 포위했다.",
    5727: "뭐라고!\n\x1bCA[bm1251]\x1bCZ가 \x1bCC오다와라\x1bCZ로 향했다고!?\n안 돼, 돌아가자!",
    5728: "당황한 \x1bCA호조 우지마사\x1bCZ는 \x1bCC스루가\x1bCZ에서 철수하여,\n아버지와 동생들이 있는 \x1bCC오다와라\x1bCZ로 서둘렀다.",
    5729: "형님이 주력을 이끌고 자리를 비운 사이\n우리 본거지를 포위하다니……\n적이지만 \x1bCA[bm1251]\x1bCZ 입도는 역시 대단하군.",
    5730: "하지만 \x1bCC오다와라\x1bCZ는 \x1bCA[b1448]\x1bCZ의 맹공도 견딘 성이다.\n\x1bCA[bm1251]\x1bCZ도 쫓아내 주마!",
    5731: "아니다, 상대할 필요 없다.\n\x1bCA[bm1448]\x1bCZ 때처럼 흘려보내라.\n도발에 넘어가면 \x1bCA[bm1251]\x1bCZ의 뜻대로 된다.",
    5732: "\x1bCA우지야스\x1bCZ는 농성전을 택하고,\n\x1bCB다케다군\x1bCZ의 도발에 응하지 않은 채,\n성안에 틀어박혀 방어에 힘썼다.",
    5733: "이런, 역시 \x1bCA우지야스\x1bCZ 녀석은 \x1bCA우지마사\x1bCZ와 달리\n도발에 넘어오지 않는군.\n어쩔 수 없지. 귀국한다.",
    5734: "\x1bCA[b1448]\x1bCZ도 공략하지 못한 \x1bCC오다와라성\x1bCZ을 치는 것은\n어리석다고 판단한 \x1bCA[bm1251]\x1bCZ는 불과\n며칠 만에 포위를 풀었다.",
    5735: "앗!\n\x1bCB다케다군\x1bCZ이 물러갑니다.",
    5736: "추격해야 합니다!\n마침 형님도 \x1bCC스루가\x1bCZ에서 돌아올 때입니다.\n협공하면 \x1bCA[bm1251]\x1bCZ도 쓰러뜨릴 수 있습니다!",
    5737: "……그만두어라.\n\x1bCA[bm1251]\x1bCZ는 이름난 전쟁의 명수다.\n너희의 계책쯤은 벌써 읽었을 것이다.",
    5738: "하지만 등을 보인 적을\n전혀 쫓지 않으면 사기에도 영향을 줍니다.",
    5739: "천재일우의 기회입니다!\n저희에게 \x1bCB다케다\x1bCZ 추격을 맡겨 주십시오!",
    5740: "……그렇다면 마음대로 해라.",
    5741: "\x1bCA우지야스\x1bCZ의 반대를 무릅쓰고,\n\x1bCA우지테루\x1bCZ·\x1bCA우지쿠니\x1bCZ 등은 성을 나와 \x1bCB다케다군\x1bCZ을 추격했다.\n하지만 이는 바로 \x1bCA[bm1251]\x1bCZ의 함정이었다.",
    5742: "후후후. 왔구나, 애송이들아.\n\x1bCB다케다\x1bCZ의 병법을 가르쳐 주마!",
    5743: "\x1bCA[bm1251]\x1bCZ는 군을 나눠 \x1bCA우지마사\x1bCZ 부대의 합류를 막고,\n\x1bCA우지테루\x1bCZ·\x1bCA우지쿠니\x1bCZ 부대를 교묘히 \x1bCC미마세토게\x1bCZ 근처로 유인해\n요격에 성공했다.",
    5744: "\x1bCA우지테루\x1bCZ·\x1bCA우지쿠니\x1bCZ는 패잔병을 수습해 \x1bCC오다와라\x1bCZ로\n돌아왔고, 그곳에 \x1bCA우지마사\x1bCZ의 원정군도 도착했다.",
    5745: "면목 없습니다. 아버님……",
    5746: "무어라 드릴 말씀이 없습니다!",
    5747: "이런, 역시 너희로는\n\x1bCA[bm1251]\x1bCZ의 상대가 되지 않는구나.\n내가 죽은 뒤가 걱정이군……",
    5748: "나도 이제 오래 살지는 못한다.\n\x1bCB우에스기\x1bCZ와 손잡고 \x1bCB다케다\x1bCZ와 싸우기로 한 것이,\n너무 성급한 선택이었을지도 모르겠군……",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    5631: ["suruga_totomi_partition_term_requires_glossary_review"],
    5638: ["oigawa_river_name_requires_glossary_review"],
    5651: ["chugoku_eleven_provinces_term_requires_glossary_review"],
    5655: ["ukita_yoshiie_reading_requires_glossary_review"],
    5677: ["esso_alliance_term_requires_glossary_review"],
    5680: ["three_provinces_superlative_requires_style_review"],
    5693: ["bishamonten_reference_requires_glossary_review"],
    5702: ["shinguto_corps_term_requires_glossary_review"],
    5708: ["oki_island_name_requires_glossary_review"],
    5710: ["kikkawa_name_spelling_requires_glossary_review"],
    5712: ["ino_musha_metaphor_requires_style_review"],
    5721: ["hojo_takeda_campaign_context_requires_history_review"],
    5743: ["mimasetoge_battle_name_requires_glossary_review"],
}

PREVIOUS_ARTIFACT_PINS = {
    **shared.PREVIOUS_ARTIFACT_PINS,
    "evidence/alignment_evidence.v0.20.json": (
        "985022FF073D4E0ABF3DCE1CFACEE19D987B2F1EFD9B54630B1E1D92A14C44E7"
    ),
    "public/msgev_ko_historical_events_5487_5628.v0.20.json": (
        "6DC7501382513265CDB73C66AF7750508AFDA3488FE17E493A6C3978CAD10167"
    ),
    "review/review_index.v0.20.json": (
        "9AE10934F16CEBB130C7EA3A477A583697BF97E3ECD83959C9FF1D166039AB1C"
    ),
    "validation.v0.20.json": (
        "F6032C1D0DE4A251418323F3A1B64B29FF18755E957CEF0CFF80396A13759483"
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
        5628,
        5629,
        5639,
        5640,
        5654,
        5655,
        5676,
        5677,
        5697,
        5698,
        5700,
        5701,
        5720,
        5721,
        5748,
        5749,
    )
    evidence["schema"] = "nobu16.kr.event-dialogue-alignment-evidence.v21"
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
    review["schema"] = "nobu16.kr.event-dialogue-review-index.v21"
    validation["schema"] = "nobu16.kr.event-dialogue-generation-validation.v21"
    validation["font_integration"].pop(
        "current_font_or_installer_must_not_include_batch20", None
    )
    validation["font_integration"][
        "current_font_or_installer_must_not_include_batch21"
    ] = True
    integrity = validation["preexisting_integrity"]
    integrity["dialogue_v01_v20_artifacts_before"] = integrity.pop(
        "dialogue_v01_v19_artifacts_before"
    )
    integrity["dialogue_v01_v20_artifacts_after"] = integrity.pop(
        "dialogue_v01_v19_artifacts_after"
    )
    safety = validation["safety"]
    safety.pop(
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_v14_v15_v16_v17_v18_v19_artifacts_modified",
        None,
    )
    safety[
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_v14_v15_v16_v17_v18_v19_v20_artifacts_modified"
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
