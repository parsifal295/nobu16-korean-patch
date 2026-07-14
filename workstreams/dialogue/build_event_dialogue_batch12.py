#!/usr/bin/env python3
"""Build source-free Korean historical event dialogue batch12 (4418-4556)."""

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
import build_event_dialogue_batch11 as shared  # noqa: E402


BATCH_ID = "msgev_historical_events_4418_4556.v0.12"
OVERLAY_NAME = "msgev_ko_historical_events_4418_4556.v0.12.json"
EVIDENCE_NAME = "alignment_evidence.v0.12.json"
REVIEW_NAME = "review_index.v0.12.json"
VALIDATION_NAME = "validation.v0.12.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 4418
SCOPE_END = 4556
EXCLUDED_INTERNAL_IDS: tuple[int, ...] = ()
BRACKET_TOKEN_RE = shared.BRACKET_TOKEN_RE

EVENTS = (
    {
        "event_id": "miki_succeeds_anegakoji",
        "title_ko": "미키 가문의 아네가코지 계승",
        "start_id": 4418,
        "end_id": 4442,
        "selected_count": 25,
    },
    {
        "event_id": "takenaka_hanbei_comes_of_age",
        "title_ko": "다케나카 한베에의 원복",
        "start_id": 4443,
        "end_id": 4445,
        "selected_count": 3,
    },
    {
        "event_id": "yoshiteru_returns_to_kyoto",
        "title_ko": "아시카가 요시테루의 환교",
        "start_id": 4446,
        "end_id": 4460,
        "selected_count": 15,
    },
    {
        "event_id": "nobunaga_visits_kyoto",
        "title_ko": "오다 노부나가의 상경",
        "start_id": 4461,
        "end_id": 4474,
        "selected_count": 14,
    },
    {
        "event_id": "kagetora_meets_yoshiteru",
        "title_ko": "가게토라와 요시테루의 대면",
        "start_id": 4475,
        "end_id": 4493,
        "selected_count": 19,
    },
    {
        "event_id": "yoshimoto_head_and_soza_samonji",
        "title_ko": "요시모토의 수급과 소자 사몬지",
        "start_id": 4494,
        "end_id": 4510,
        "selected_count": 17,
    },
    {
        "event_id": "motochika_first_battle_lesson",
        "title_ko": "모토치카의 첫 출진 문답",
        "start_id": 4511,
        "end_id": 4527,
        "selected_count": 17,
    },
    {
        "event_id": "death_of_chosokabe_kunichika",
        "title_ko": "조소카베 구니치카의 죽음",
        "start_id": 4528,
        "end_id": 4556,
        "selected_count": 29,
    },
)

TRANSLATIONS: dict[int, str] = {
    4418: "\x1bCC히다국\x1bCZ――",
    4419: (
        "\x1bCB미키 가문\x1bCZ 당주 \x1bCA미키 요시요리\x1bCZ는 조정으로부터\n"
        "종5위하 히다노카미에 임명되었다."
    ),
    4420: "아버님,\n히다노카미 취임을 축하드립니다.",
    4421: (
        "\x1bCA요리쓰나\x1bCZ냐……\n"
        "나는 여기서 멈출 사람이 아니다.\n"
        "히다노카미는 그저 과정일 뿐이지."
    ),
    4422: "그 말씀은……?",
    4423: "내게는 큰 뜻이 있다.\n듣고 싶으냐?\n듣고 싶겠지?",
    4424: "……어떤 뜻을 품고 계십니까?",
    4425: "내 소원은 말이다,\n주나곤 관직을 얻는 것이다!",
    4426: (
        "그, 그러십니까……\n"
        "(주나곤은 구교의 반열에 드는 고위직.\n"
        "　지방 무사가 바랄 자리가 아닌데……)"
    ),
    4427: "그런데 조정에서 좀처럼 소식이 없구나.\n어째서라고 생각하느냐?",
    4428: "그, 글쎄요……\n저로서는 잘 모르겠습니다.",
    4429: "……아니, 너도 알고 있을 터.\n말해 보아라.",
    4430: (
        "……아무래도 가문의 격 때문이 아닐까요?\n"
        "주나곤은 도읍의 \x1bCB세이가케\x1bCZ나 \x1bCB다이진케\x1bCZ 같은\n"
        "유서 깊은 공가가 맡는 자리이니……"
    ),
    4431: (
        "역시 내 아들답구나. 바로 그렇다.\n"
        "하지만 지금은 전국시대다.\n"
        "실력만 있으면 가문의 격쯤 바꿀 수 있다!"
    ),
    4432: "그래서 생각해 보았는데……\n너, 이름을 바꾸어라.",
    4433: "예?\n갑자기 무슨 말씀이십니까……",
    4434: (
        "한때 히다 고쿠시를 칭한 \x1bCB아네가코지 가문\x1bCZ은\n"
        "내란으로 쇠약해져 이제 대가 끊겼다."
    ),
    4435: (
        "\x1bCC히다\x1bCZ를 다스리는 우리 가문이 그 이름을 잇는다 해도\n"
        "누구도 시비를 걸지 못할 것이다!"
    ),
    4436: (
        "너는 히다 고쿠시 \x1bCB아네가코지 가문\x1bCZ의 이름을 이어,\n"
        "이제부터 \x1bCA아네가코지 요리쓰나\x1bCZ라 하라!"
    ),
    4437: (
        "아니요, 사양하겠습니다.\n"
        "\x1bCB미키 가문\x1bCZ과 \x1bCB아네가코지 가문\x1bCZ은\n"
        "격이 너무나 다르기 때문입니다……"
    ),
    4438: "……아비의 말을 듣지 않겠다는 게냐!\n모두 너를 위해서 하는 일이다!",
    4439: (
        "……알겠습니다.\n"
        "아버님께서 그토록 말씀하신다면,\n"
        "이제부터 \x1bCA아네가코지\x1bCZ…… \x1bCA요리쓰나\x1bCZ로 살겠습니다."
    ),
    4440: (
        "음, 참 좋은 이름이구나!\n"
        "네가 \x1bCB아네가코지 가문\x1bCZ을 이으면 가문의 격도 오른다.\n"
        "염원하던 주나곤에 또 한 걸음 다가섰구나!"
    ),
    4441: (
        "(정말 곤란한 아버님이시군……\n"
        "　아들이 \x1bCB아네가코지\x1bCZ의 이름을 잇는다고\n"
        "　조정이 우리 격을 인정해 줄까……)"
    ),
    4442: (
        "그리하여 히다 다이묘 \x1bCB미키 가문\x1bCZ의 후계자\n"
        "\x1bCA미키 요리쓰나\x1bCZ는 이름을 바꾸어\n"
        "\x1bCA아네가코지 요리쓰나\x1bCZ가 되었다……"
    ),
    4443: "\x1bCA다케나카 한베에\x1bCZ――\n그 사내는 원복 의식을 마쳤다.",
    4444: (
        "무력이 아닌 지략으로 수많은 싸움을\n"
        "승리로 이끄는 그 재능은 훗날\n"
        "‘금공명’이라 칭송받게 된다……"
    ),
    4445: (
        "바로 이때, \x1bCA다케나카 한베에\x1bCZ라는 사내가\n"
        "난세에 풀려난 것이다……"
    ),
    4446: (
        "\x1bCA미요시 나가요시\x1bCZ와 대립해 다시 \x1bCC교토\x1bCZ를 떠나,\n"
        "\x1bCC구쓰키다니\x1bCZ로 피신한 쇼군 \x1bCA[b75]\x1bCZ――"
    ),
    4447: (
        "하지만 쇼군은 본디 \x1bCC교토\x1bCZ와 \x1bCC무로마치 어소\x1bCZ의 주인으로,\n"
        "\x1bCC오미\x1bCZ에 오래 머무는 것은 \x1bCA[bm75]\x1bCZ의 뜻이 아니었다."
    ),
    4448: (
        "생각해 보면 쇼군에 오른 지 십여 년……\n"
        "\x1bCC교토\x1bCZ에 있던 때는 고작 몇 년뿐.\n"
        "이래서는 구보라는 이름뿐이로구나……"
    ),
    4449: (
        "이번에는 반드시 \x1bCB미요시\x1bCZ 무리를\n"
        "\x1bCC교토\x1bCZ에서 몰아내고 \x1bCC무로마치\x1bCZ 어소로 돌아가,\n"
        "천하의 정치를 되찾겠다!"
    ),
    4450: (
        "출진을 결심한 \x1bCA[bm75]\x1bCZ는 \x1bCC히에이산\x1bCZ을 넘어,\n"
        "\x1bCC교토\x1bCZ 북쪽 교외 \x1bCC기타시라카와\x1bCZ에서 \x1bCB미요시군\x1bCZ과\n"
        "격전을 벌였다."
    ),
    4451: (
        "구보 녀석, 이번에는 진심이군.\n"
        "병력은 우리의 2할도 되지 않으면서,\n"
        "끈질기게 공격해 오다니……"
    ),
    4452: (
        "적이 아무리 몰락했어도 쇼군입니다.\n"
        "가담하는 무사가 많아 함부로 공격할 수도 없고……\n"
        "참으로 성가신 분이십니다."
    ),
    4453: (
        "\x1bCA[bm75]\x1bCZ 측은 \x1bCC교토\x1bCZ 북동쪽의 \x1bCC승군산\x1bCZ을 점거해,\n"
        "장기전에 대비하는 모습을 보였다.\n"
        "아버지 \x1bCA요시하루\x1bCZ가 예전에 정비한 성채였다……"
    ),
    4454: (
        "\x1bCC승군산\x1bCZ이라니 \x1bCB아시카가 가문\x1bCZ에 어울리는 이름이구나.\n"
        "이제부터 \x1bCC쇼군산\x1bCZ이라 고쳐 부를까.\n"
        "이 산에 틀어박혀 \x1bCB미요시군\x1bCZ과 싸우겠다!"
    ),
    4455: (
        "그러나 장기전은 양쪽 모두에게 이롭지 않았다.\n"
        "\x1bCB미요시 측\x1bCZ은 쇼군을 돕던 \x1bCB롯카쿠 가문\x1bCZ을 움직여,\n"
        "화친을 위한 교섭을 진행했다……"
    ),
    4456: (
        "\x1bCA[bm75]\x1bCZ 공과 가신들이 \x1bCC교토\x1bCZ 어소로 돌아가는 것,\n"
        "쇼군으로서의 권위를 존중하는 것,\n"
        "모두 받아들이겠습니다……"
    ),
    4457: (
        "우리도 \x1bCB미요시 가문\x1bCZ 사람을 요직에 기용하고,\n"
        "관직을 얻도록 주선하는 일에\n"
        "동의하겠다."
    ),
    4458: (
        "이렇게 \x1bCB아시카가\x1bCZ와 \x1bCB미요시\x1bCZ 양측의 화의가 이루어져,\n"
        "\x1bCA[bm75]\x1bCZ는 몇 년 만에 \x1bCC교토\x1bCZ로 돌아갔다."
    ),
    4459: (
        "흥, 구보가 얌전히 우리 가마가 되어 준다면\n"
        "이쪽도 손쓸 필요가 없지.\n"
        "장식물로 실컷 이용해 주마……"
    ),
    4460: (
        "\x1bCB아시카가\x1bCZ와 \x1bCB미요시\x1bCZ는 결국 동상이몽일 뿐이었다.\n"
        "이상을 품고 교토로 돌아온 \x1bCA[bm75]\x1bCZ는 머지않아\n"
        "현실과의 괴리에 괴로워하게 된다……"
    ),
    4461: (
        "이해에 \x1bCA오다 노부나가\x1bCZ는 몇몇 가신만 거느리고,\n"
        "몰래 \x1bCC사카이\x1bCZ와 \x1bCC난토\x1bCZ, \x1bCC교토\x1bCZ 등을 둘러보았다."
    ),
    4462: (
        "그때 \x1bCC교토\x1bCZ로 돌아와 있던 쇼군\n"
        "\x1bCA[b75]\x1bCZ도 알현했다고 전한다."
    ),
    4463: (
        "오, \x1bCA노부히데\x1bCZ의 아들이로구나.\n"
        "제법 당찬 얼굴이야.\n"
        "\x1bCC교토\x1bCZ를 보니 어떠하냐?"
    ),
    4464: (
        "시장과 사찰의 규모는 \x1bCC오와리\x1bCZ 같은\n"
        "시골과는 비교조차 할 수 없습니다.\n"
        "과연 나라의 도읍입니다."
    ),
    4465: (
        "……하지만 어딘가 어수선하고 통일감이 없습니다.\n"
        "백성을 다스릴 ‘무’가 부족한 탓일지도 모르지요."
    ),
    4466: (
        "아픈 곳을 찌르는구나……\n"
        "나도 검술은 익혔으나, 무가의 우두머리에 걸맞은\n"
        "병력은 갖추지 못했다."
    ),
    4467: (
        "그대 같은 사내가 \x1bCB미요시\x1bCZ 무리를 대신해,\n"
        "무력으로 \x1bCC교토\x1bCZ를 다스려 준다면\n"
        "세상도 달라질지 모르겠구나……"
    ),
    4468: "구보 님……",
    4469: (
        "\x1bCC교토\x1bCZ에 머무는 동안 \x1bCA노부나가\x1bCZ 일행이\n"
        "정체불명의 자객에게 저격당했다는 일화도 전한다."
    ),
    4470: (
        "내가 교토에 온 줄 알고 벌인 짓인가.\n"
        "누구의 소행인지 밝혀내라!"
    ),
    4471: (
        "예! 조사한 바로는,\n"
        "\x1bCC미노\x1bCZ의 \x1bCB사이토 가문\x1bCZ이 보낸 자인 듯합니다……"
    ),
    4472: (
        "\x1bCA[b921]\x1bCZ인가……\n"
        "이런 얼빠진 자객을 보내다니,\n"
        "그놈다운 경솔함이군."
    ),
    4473: (
        "하지만 장인어른이 살아 계실 때는\n"
        "\x1bCC미노\x1bCZ에 조총이 부족하다 한탄하셨는데,\n"
        "이제 저격에 쓸 정도가 되었나."
    ),
    4474: "어쨌든 눈엣가시다.\n어서 \x1bCC미노\x1bCZ를 제압해야겠군……",
    4475: (
        "몇 해 전 \x1bCA[b1448]\x1bCZ가 처음 상경했을 때는,\n"
        "쇼군 \x1bCA[b75]\x1bCZ가 \x1bCC교토\x1bCZ에 없어\n"
        "두 사람이 만나지 못했다."
    ),
    4476: (
        "이해에 \x1bCA[bm1448]\x1bCZ가 다시 소수의 수행원만 데리고\n"
        "상경하자, 마침내 \x1bCA요시테루\x1bCZ와\n"
        "대면할 수 있었다."
    ),
    4477: (
        "그대가 \x1bCA[b1448]\x1bCZ인가.\n"
        "소문은 익히 들었다.\n"
        "과연 믿음직한 무인이로군."
    ),
    4478: (
        "예, 황송합니다.\n"
        "이번에 상경한 것은 간토 간레이직에 관해\n"
        "구보 님의 허락을 받고자 해서입니다……"
    ),
    4479: (
        "알고 있다.\n"
        "\x1bCA노리마사\x1bCZ는 \x1bCC간토\x1bCZ에서 달아났다지.\n"
        "그 직책을 감당할 수 없을 것이다."
    ),
    4480: (
        "\x1bCB우에스기\x1bCZ 적통이 위태로운 지금, 그대는 스스로의 힘으로\n"
        "\x1bCC에치고\x1bCZ를 굳건히 다스리고 있다.\n"
        "간토 간레이를 이어도 이견이 없겠지."
    ),
    4481: (
        "참으로 영광입니다……\n"
        "이제 거리낌 없이 \x1bCC간토\x1bCZ로 산을 넘어,\n"
        "\x1bCB호조\x1bCZ와 싸울 명분을 얻었습니다."
    ),
    4482: (
        "이 난세에는 무엇보다 힘이 말을 한다.\n"
        "나 \x1bCA[bm75]\x1bCZ도 쇼군 자리에 있으면서,\n"
        "힘이 없어 \x1bCC교토\x1bCZ에서 몇 번이나 쫓겨났지……"
    ),
    4483: (
        "\x1bCB미요시\x1bCZ도 \x1bCB마쓰나가\x1bCZ도 \x1bCB아시카가\x1bCZ의 권위보다\n"
        "힘을 좇는 속물들이다. 하지만 그들에게 기대지 않으면\n"
        "\x1bCC교토\x1bCZ에 머무는 것조차 불가능하다."
    ),
    4484: "구보 님……",
    4485: (
        "이 어지러운 세상에서 그대처럼\n"
        "전통의 권위를 중히 여기는 무사를 만난 것은\n"
        "귀한 인연이었다. 무엇이든 돕겠다."
    ),
    4486: (
        "간토 간레이직에 가문의 격이 부족하다면,\n"
        "내 이름 한 글자를 내려 \x1bCA데루토라\x1bCZ라 하겠다.\n"
        "그러면 위신도 서겠지."
    ),
    4487: (
        "아니요, 너무나 황송한 말씀입니다……!\n"
        "\x1bCA[bm1448]\x1bCZ는 아직 \x1bCB우에스기\x1bCZ의 가신.\n"
        "구보 님께는 가신의 가신일 뿐입니다."
    ),
    4488: (
        "감사한 제안이오나, \x1bCB호조\x1bCZ를 몰아내고\n"
        "\x1bCC간토\x1bCZ를 평정해 간레이직을 이은 뒤에\n"
        "다시 받도록 하겠습니다……"
    ),
    4489: (
        "그런가, 욕심 없는 사내로군.\n"
        "좋다, \x1bCA[bm1448]\x1bCZ. 가능한 오래 \x1bCC교토\x1bCZ에 머물며\n"
        "나를 뒷받침해 다오."
    ),
    4490: (
        "예!\n"
        "과분한 말씀입니다.\n"
        "\x1bCA[bm1448]\x1bCZ, 미력이나마 힘을 다하겠습니다……"
    ),
    4491: (
        "\x1bCA요시테루\x1bCZ와 \x1bCA[bm1448]\x1bCZ는 신분은 달랐지만,\n"
        "첫 대면에서 의기투합하여 각자의 자리에서\n"
        "서로를 돕기로 맹세했다."
    ),
    4492: (
        "이때 \x1bCA[bm1448]\x1bCZ가 \x1bCC교토\x1bCZ에 얼마나 머물렀는지는\n"
        "기록에 없으나, \x1bCA요시테루\x1bCZ의 요청으로\n"
        "상당히 오랫동안 체류했다고 한다."
    ),
    4493: (
        "그동안 간파쿠 \x1bCA고노에 사키히사\x1bCZ를 비롯한\n"
        "\x1bCC교토\x1bCZ의 명사들과도 교류를 깊게 했다."
    ),
    4494: (
        "오케하자마 전투에서,\n"
        "\x1bCB오다군\x1bCZ은 하나같이 투지를 불태우며\n"
        "‘\x1bCA요시모토\x1bCZ의 목을 반드시 베겠다’고 맹세했다."
    ),
    4495: (
        "\x1bCA노부나가\x1bCZ도 말에서 내려 우마마와리슈를 이끌고,\n"
        "졸병들 사이에서 직접 칼을 휘둘렀다."
    ),
    4496: (
        "몇 번이나 거센 반격에 밀리면서도,\n"
        "\x1bCB이마가와군\x1bCZ의 중심부를 궁지로 몰았다고 전한다."
    ),
    4497: "그리고――",
    4498: (
        "아뢰옵니다!\n"
        "\x1bCA모리 신스케\x1bCZ 님이 적장 \x1bCA요시모토\x1bCZ를 베었습니다!"
    ),
    4499: "그런가…… 장하다!\n수급을 확인하겠다. 당장 가져와라!",
    4500: "예, 여기 있습니다.",
    4501: "…………",
    4502: (
        "(이것이 가이도 제일의 무사 \x1bCA이마가와 지부타이후\x1bCZ인가.\n"
        "　이것이 오랫동안 나를 괴롭힌 자……)"
    ),
    4503: "(무거운 수급이로군……\n　하지만 살아 있을 때 사람의 목은 가벼운 법.)",
    4504: "응?\n이것은?",
    4505: "예!\n\x1bCA요시모토\x1bCZ가 늘 차고 다니던 칼입니다.",
    4506: (
        "\x1bCA노부나가\x1bCZ는 \x1bCA요시모토\x1bCZ가 지녔던\n"
        "‘소자 사몬지’ 칼에 다음과 같이 새기고,\n"
        "자신의 애도로 삼았다고 전한다."
    ),
    4507: (
        "　에이로쿠 3년 5월 19일\n"
        "　요시모토를 토벌하고 그 칼에 새김\n"
        "　　　오다 오와리노카미 노부나가"
    ),
    4508: (
        "가이도 제일의 무사 \x1bCA이마가와 요시모토\x1bCZ의 죽음은\n"
        "한 다이묘에 불과했던 \x1bCA오다 노부나가\x1bCZ를\n"
        "전국시대의 중심 무대로 밀어 올렸을 뿐 아니라……"
    ),
    4509: (
        "고소슨 삼국동맹의 동요와,\n"
        "그에 따른 \x1bCA[b1448]\x1bCZ의 간토 출병,\n"
        "\x1bCB미카와 마쓰다이라 가문\x1bCZ의 독립 등,"
    ),
    4510: "여러 지역과 인물에게\n커다란 영향을 미쳤다.",
    4511: "분고, 한 가지 가르쳐 주겠느냐?",
    4512: "예!\n도련님, 무슨 일이십니까?",
    4513: (
        "‘분고’는 \x1bCA진젠지 야스코레\x1bCZ를 가리킨다.\n"
        "분고노카미를 자칭했기에 그렇게 불렸다.\n"
        "\x1bCA조소카베 모토치카\x1bCZ의 병법 스승이자 교육 담당이었다."
    ),
    4514: (
        "곧 첫 출진을 맞게 되는데……\n"
        "나는 창으로 사람을 찔러 본 적이 없다.\n"
        "그 방법을 가르쳐 주겠느냐?"
    ),
    4515: "도, 도련님!\n수없이 가르쳐 드리지 않았습니까!",
    4516: (
        "그래, 연습은 했지.\n"
        "창을 다룰 수는 있지만,\n"
        "사람을 찔러 본 적은 한 번도 없다."
    ),
    4517: (
        "……적의 눈을 찌르십시오.\n"
        "막기 어렵고, 설령 죽이지 못하더라도\n"
        "눈을 다치면 싸울 수 없습니다."
    ),
    4518: "그렇군, 기억해 두겠다.\n하나 더 묻고 싶은데……",
    4519: "(아직도 남았나……)",
    4520: (
        "대장이라는 자는,\n"
        "모두의 앞에서 나아가야 하느냐?\n"
        "아니면 뒤에서 따라가야 하느냐?"
    ),
    4521: (
        "대장은 병사와 달라,\n"
        "직접 적의 목을 베는 역할은 아닙니다.\n"
        "또한 결코 달아나서도 안 됩니다."
    ),
    4522: (
        "그러므로,\n"
        "대장은 모두보다 앞서야 한다고 합니다.\n"
        "병사 앞에 서서 명령을 내려야 합니다."
    ),
    4523: "그렇군……\n고맙다.",
    4524: (
        "(아아……\n"
        "　주변 사람들은 어리석은 이를 보듯 한다.\n"
        "　저자가 히메와코라며 비웃고 있겠지.)"
    ),
    4525: (
        "(하지만 그것이야말로 잘못이다……\n"
        "　도련님의 그릇은 범인이 헤아릴 수 없다.\n"
        "　반드시 \x1bCC시코쿠\x1bCZ의 주인이 되실 분이다.)"
    ),
    4526: "(아마도……)",
    4527: "…………",
    4528: (
        "\x1bCA조소카베 구니치카\x1bCZ의 아버지 \x1bCA가네쓰구\x1bCZ는,\n"
        "협력하던 \x1bCB모토야마 가문\x1bCZ 등 \x1bCC도사\x1bCZ 호족의 배신으로\n"
        "멸망 직전까지 몰렸다."
    ),
    4529: (
        "\x1bCA구니치카\x1bCZ는 고난 끝에 \x1bCB조소카베 가문\x1bCZ을 재건하고,\n"
        "세력을 넓혀 마침내 원수인\n"
        "\x1bCB모토야마 가문\x1bCZ을 궁지로 몰았다."
    ),
    4530: "그러나 \x1bCA구니치카\x1bCZ를 병마가 무정하게 덮쳤다.",
    4531: "\x1bCA모토치카\x1bCZ, 잘 들어라.",
    4532: "예.",
    4533: "내 아버지 \x1bCA가네쓰구\x1bCZ는,\n나보다 훨씬 용맹한 대장이었다.",
    4534: "하지만 그 때문에 교만해졌고,\n신의를 잃어 배신당한 끝에 멸망했다.",
    4535: (
        "그러니……\n"
        "사람의 신의를 잃지 말라 하기는 쉽다.\n"
        "하지만 내가 할 말은 그것이 아니다."
    ),
    4536: "…………",
    4537: (
        "신의를 잃는 일도 또한 난세의 이치다.\n"
        "잃고도 살아남을 힘을 지니거나,\n"
        "잃을 것까지 내다보고 계책을 세워라."
    ),
    4538: (
        "너라면 어느 길이든 택할 수 있겠지.\n"
        "미덥지 못한 후계자라 여겼는데,\n"
        "내가 잘못 보았구나……"
    ),
    4539: (
        "\x1bCA모토치카\x1bCZ, 너는 반드시\n"
        "\x1bCC시코쿠\x1bCZ를 손에 넣을 수 있다.\n"
        "네 장수로서의 재능은 나도 미치지 못한다."
    ),
    4540: "예.\n모든 일을 이 \x1bCA모토치카\x1bCZ에게 맡겨 주십시오.",
    4541: "\x1bCA치카사다\x1bCZ, \x1bCA치카야스\x1bCZ……",
    4542: "예!",
    4543: "예!",
    4544: "너희도 알고 있겠지만……\n\x1bCA모토치카\x1bCZ를 보필하라.",
    4545: "너희가 거역하더라도,\n이길 수 있는 사내가 아니다.",
    4546: "……반드시 그리하겠습니다.",
    4547: "맡겨 주십시오.",
    4548: (
        "분하구나.\n"
        "\x1bCB모토야마\x1bCZ가 멸망하는 꼴을 보지 못하고,\n"
        "내가 먼저 가다니……"
    ),
    4549: (
        "\x1bCA모토치카\x1bCZ.\n"
        "\x1bCB모토야마\x1bCZ를 치는 것이 곧 나를 위한 공양이다.\n"
        "상례가 끝나거든 곧바로 갑옷을 입어라."
    ),
    4550: "아버님, 부디 편히 쉬십시오!",
    4551: "좋다……\n그럼 나는 군신이 되어 \x1bCB조소카베\x1bCZ를 지키마……",
    4552: "아버님!",
    4553: "아버님……",
    4554: "…………",
    4555: (
        "멸망 직전의 \x1bCB조소카베 가문\x1bCZ을\n"
        "‘들판의 호랑이’라 불린 용맹으로 재건한\n"
        "\x1bCA조소카베 구니치카\x1bCZ는 여기서 생을 마쳤다."
    ),
    4556: (
        "\x1bCA구니치카\x1bCZ가 품은 \x1bCC도사\x1bCZ 통일의 꿈은,\n"
        "그가 고안한 ‘이치료구소쿠’ 제도와 함께\n"
        "적자 \x1bCA모토치카\x1bCZ에게 맡겨졌다."
    ),
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    4419: ["miki_yoshiyori_and_hida_no_kami_terms_require_glossary_review"],
    4430: ["court_house_rank_terms_require_glossary_review"],
    4444: ["ima_komei_epithet_rendering_requires_review"],
    4453: ["shogunyama_kanji_wordplay_requires_review"],
    4493: ["konoe_sakihisa_name_requires_glossary_review"],
    4502: ["jibu_taiyu_court_title_requires_glossary_review"],
    4506: ["soza_samonji_reading_requires_glossary_review"],
    4507: ["sword_inscription_requires_historical_review"],
    4513: ["jinzenji_yasukore_name_requires_glossary_review"],
    4524: ["himewako_epithet_requires_glossary_review"],
    4528: ["chosokabe_kanetsugu_name_requires_glossary_review"],
    4556: ["ichiryo_gusoku_term_requires_glossary_review"],
}

PREVIOUS_ARTIFACT_PINS = {
    **shared.PREVIOUS_ARTIFACT_PINS,
    "evidence/alignment_evidence.v0.11.json": (
        "759E031F61D525B6B895CBB4258F135A06B83AA7D93744D53365F13F91245BD7"
    ),
    "public/msgev_ko_historical_events_4280_4417.v0.11.json": (
        "E6A366499D89317F78C1E96BA546D10AB9ABE3FF9B49E49C299F6B69C38E3C23"
    ),
    "review/review_index.v0.11.json": (
        "3D9DF5E03F6F5F29C64E6B31EFCAF4E4C998A5F69B01825583002B76603923BA"
    ),
    "validation.v0.11.json": (
        "5A2E6BEF1798C8BACB11F6D032C046277C2296A12C27DED7124C5639443BF6C8"
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
    if len(ids) != 139 or ids != sorted(TRANSLATIONS):
        raise ValueError("batch12 ids are not the exact 139 displayed entries")
    return ids


def event_for(entry_id: int) -> str:
    matches = [
        event["event_id"]
        for event in EVENTS
        if event["start_id"] <= entry_id <= event["end_id"]
    ]
    if len(matches) != 1:
        raise ValueError(f"id {entry_id} does not map to one batch12 event group")
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
        4417,
        4418,
        4442,
        4443,
        4445,
        4446,
        4460,
        4461,
        4474,
        4475,
        4493,
        4494,
        4510,
        4511,
        4527,
        4528,
        4556,
        4557,
    )
    evidence["schema"] = "nobu16.kr.event-dialogue-alignment-evidence.v12"
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
    review["schema"] = "nobu16.kr.event-dialogue-review-index.v12"
    validation["schema"] = "nobu16.kr.event-dialogue-generation-validation.v12"
    validation["font_integration"].pop(
        "current_font_or_installer_must_not_include_batch11", None
    )
    validation["font_integration"][
        "current_font_or_installer_must_not_include_batch12"
    ] = True
    integrity = validation["preexisting_integrity"]
    integrity["dialogue_v01_v11_artifacts_before"] = integrity.pop(
        "dialogue_v01_v10_artifacts_before"
    )
    integrity["dialogue_v01_v11_artifacts_after"] = integrity.pop(
        "dialogue_v01_v10_artifacts_after"
    )
    safety = validation["safety"]
    safety.pop(
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_artifacts_modified",
        None,
    )
    safety[
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_artifacts_modified"
    ] = False

    overlay_path = out_root / "public" / OVERLAY_NAME
    overlay_meta = {
        "path": f"public/{OVERLAY_NAME}",
        "size": overlay_path.stat().st_size,
        "sha256": sha256(overlay_path.read_bytes()),
    }
    evidence_meta = write_json(
        evidence_path, evidence, f"evidence/{EVIDENCE_NAME}"
    )
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
