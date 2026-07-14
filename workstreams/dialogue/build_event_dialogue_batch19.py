#!/usr/bin/env python3
"""Build source-free Korean historical event dialogue batch19 (5359-5486)."""

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
import build_event_dialogue_batch18 as shared  # noqa: E402


BATCH_ID = "msgev_historical_events_5359_5486.v0.19"
OVERLAY_NAME = "msgev_ko_historical_events_5359_5486.v0.19.json"
EVIDENCE_NAME = "alignment_evidence.v0.19.json"
REVIEW_NAME = "review_index.v0.19.json"
VALIDATION_NAME = "validation.v0.19.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 5359
SCOPE_END = 5486
EXCLUDED_INTERNAL_IDS: tuple[int, ...] = ()
BRACKET_TOKEN_RE = shared.BRACKET_TOKEN_RE

EVENTS = (
    {
        "event_id": "sunomata_fortress_and_hachisuka_koroku",
        "title_ko": "스노마타 축성과 하치스카 고로쿠",
        "start_id": 5359,
        "end_id": 5382,
        "selected_count": 24,
    },
    {
        "event_id": "fall_of_nagano_and_minowa",
        "title_ko": "나가노 가문과 미노와성의 최후",
        "start_id": 5383,
        "end_id": 5411,
        "selected_count": 29,
    },
    {
        "event_id": "oichi_marries_azai_nagamasa",
        "title_ko": "오이치와 아자이 나가마사의 혼인",
        "start_id": 5412,
        "end_id": 5438,
        "selected_count": 27,
    },
    {
        "event_id": "shikanosuke_prays_for_seven_hardships",
        "title_ko": "시카노스케의 칠난팔고 기원",
        "start_id": 5439,
        "end_id": 5447,
        "selected_count": 9,
    },
    {
        "event_id": "mino_triumvirate_turns_from_saito",
        "title_ko": "미노 삼인중의 사이토 이반",
        "start_id": 5448,
        "end_id": 5464,
        "selected_count": 17,
    },
    {
        "event_id": "nobunaga_refuses_shogunal_titles",
        "title_ko": "노부나가의 간레이와 부쇼군직 거절",
        "start_id": 5465,
        "end_id": 5486,
        "selected_count": 22,
    },
)

TRANSLATIONS: dict[int, str] = {
    5359: "\x1bCB오다\x1bCZ 가신 \x1bCA[b754]\x1bCZ은 고민에 빠졌다.",
    5360: "으음, 주군께서 \x1bCC미노\x1bCZ 공략을 위해\n스노마타에 성채를 지으라 명하셨는데……",
    5361: "중신들이 잇달아 도전했으나 모두 실패했다.\n내가 그 까다로운 임무를 맡겠다 했지만……",
    5362: "\x1bCB사이토\x1bCZ의 영지와 너무 가까워 성채를 짓기 시작하면,\n군사를 보내 순식간에 무너뜨릴 테지.",
    5363: "으으, 이 난제를\n어찌 풀어야 한단 말인가……!?",
    5364: "적병을 먼저 물리친다면,\n그 뒤에는 성채만 지으면 되지 않는가?",
    5365: "지리의 이점과 사람의 화합…… 그 둘을 얻으면,\n어쩌면 성공할 수 있다!",
    5366: "\x1bCA[bm754]\x1bCZ은 인맥을 좇아 \x1bCC나가라강\x1bCZ의 수운을 장악한\n강력한 \x1bCB가와나미중\x1bCZ을 찾아갔다.",
    5367: "그리고 \x1bCB가와나미중\x1bCZ 두령 \x1bCA하치스카 고로쿠\x1bCZ와\n마주했다.",
    5368: "\x1bCA[bm754]\x1bCZ 공이라 했나.\n우리 \x1bCB가와나미중\x1bCZ은 \x1bCB사이토\x1bCZ 편이다.",
    5369: "무슨 일로 왔는지는 모르나, 네 목을 베어\n\x1bCB사이토\x1bCZ에게 바쳐도 된다!",
    5370: "아이쿠, 그것만은 봐주십시오.\n좋은 제안을 하나 가져왔습니다.",
    5371: "우선 제 말을 들어 주십시오.\n절대 손해 보게 하지 않겠습니다.",
    5372: "\x1bCA[bm754]\x1bCZ은 \x1bCA사이토 다쓰오키\x1bCZ의 어리석음을 지적하고,\n\x1bCB사이토\x1bCZ를 따르면 \x1bCB오다\x1bCZ의 적이 되어 망한다고 경고했다.",
    5373: "지금 \x1bCB오다\x1bCZ 편에 서면 좋은 지위를 얻을 거라며,\n\x1bCA고로쿠\x1bCZ를 열심히 설득했다.",
    5374: "알겠다. 우리도 계속 \x1bCB사이토\x1bCZ를 따르는 건\n위험하다고 생각하던 참이다.",
    5375: "하지만 단순히 귀순하라는 얘기는 아니겠지.\n우리가 무얼 해 주면 되나?",
    5376: "\x1bCC스노마타\x1bCZ에 성채를 짓고 싶습니다.\n공사 중에 \x1bCB사이토\x1bCZ가 군사를 보내 온다면……",
    5377: "기습하여 물리쳐 주십시오.\n\x1bCB가와나미중\x1bCZ이라면 지리에도 밝지 않습니까?",
    5378: "……좋다. \x1bCA오다\x1bCZ로 돌아설 때 바칠\n선물로도 충분하겠군.",
    5379: "정말 감사합니다!\n이제 성공한 것이나 다름없습니다!",
    5380: "\x1bCB가와나미중\x1bCZ을 \x1bCB오다 가문\x1bCZ으로 끌어들인 덕분에,\n\x1bCA히데요시\x1bCZ는 \x1bCC스노마타\x1bCZ 성채를 훌륭히 완성했다.",
    5381: "\x1bCC스노마타\x1bCZ 성채는 \x1bCC미노\x1bCZ 공략에 이바지했으며,\n\x1bCA[bm754]\x1bCZ의 출세를 여는 발판이 되었다.",
    5382: "\x1bCB가와나미중\x1bCZ은 \x1bCB오다\x1bCZ 휘하가 되고, \x1bCA고로쿠\x1bCZ와 \x1bCA[bm754]\x1bCZ은\n함께 전국의 무대로 나아갔다.",
    5383: "과거 \x1bCA나가노 나리마사\x1bCZ는\n\x1bCC코즈케 미노와성\x1bCZ의 성주로서,\n그 지역의 \x1bCB미노와중\x1bCZ을 이끌었다.",
    5384: "당시 \x1bCC코즈케\x1bCZ는 \x1bCB우에스기\x1bCZ, \x1bCB다케다\x1bCZ, \x1bCB호조\x1bCZ의 경계라\n분쟁이 끊이지 않는 땅이었다.",
    5385: "독립을 지킨 그는 ‘\x1bCC조슈\x1bCZ의 호랑이’라 불린 명장이었다.",
    5386: "그러나 그조차 세월이라는 적을 이기지 못해,\n끝내 병으로 쓰러졌다.",
    5387: "죽을 때를 깨달은 그는 적자 \x1bCA나리모리\x1bCZ를 불러,\n마지막 유언을 남겼다.",
    5388: "잘 들어라. 내가 죽거든 무덤은 이정표처럼\n소박하게 만들고, 법요는 치르지 마라.",
    5389: "내 무덤 앞에 적의 목을 하나라도 더 바쳐라.\n그리고 절대 적에게 항복하지 마라.",
    5390: "무운이 다하면 깨끗이 전사하라.\n그보다 더한 효도는 없다.",
    5391: "참으로 장렬한 유언이었다.\n\x1bCA나리모리\x1bCZ는 눈물을 흘리며 아버지께 답했다.",
    5392: "아버님, 안심하십시오.\n이 \x1bCA나리모리\x1bCZ, 반드시 말씀을 지키겠습니다.",
    5393: "그 말을 들은 \x1bCA나리마사\x1bCZ는 만족스레 고개를 끄덕이고,\n근심 어린 눈으로 하늘을 보며 숨을 거두었다.",
    5394: "아들과 자신의 적을 생각하며,\n그는 \x1bCB나가노 가문\x1bCZ의 앞날을 내다본 것인지도 모른다.",
    5395: "조슈의 호랑이가 죽었다는 소식은 \x1bCC간토 여러 나라\x1bCZ에 퍼졌다.",
    5396: "그 죽음을 가장 기뻐한 이는 \x1bCC가이\x1bCZ의\n\x1bCA[b1251]\x1bCZ이었을 것이다.",
    5397: "과거 \x1bCA[bm1251]\x1bCZ은 여러 번 \x1bCC코즈케\x1bCZ로 출병했으나,\n매번 \x1bCA나리마사\x1bCZ에게 막혔다.",
    5398: "후후, \x1bCA나리마사\x1bCZ가 있는 한 \x1bCC조슈\x1bCZ를 얻지 못한다 여겼는데,\n이제야 운이 따르는구나!",
    5399: "\x1bCA나리마사\x1bCZ가 죽었으니 \x1bCC코즈케\x1bCZ는 손에 넣은 셈이다.\n당장 군사를 보내라!",
    5400: "\x1bCA[bm1251]\x1bCZ은 대군을 이끌고 \x1bCC코즈케\x1bCZ로 출진했다.",
    5401: "망할 \x1bCA[bm1251] 땡중\x1bCZ, 아버지가 죽은 걸 알자\n곧바로 쳐들어왔구나.\n하지만 우리는 결코 굴복하지 않는다!",
    5402: "\x1bCA나리모리\x1bCZ는 필사적으로 맞서 한 번 \x1bCB다케다군\x1bCZ을 물리쳤지만,\n적은 다시 대군으로 몰려왔다.",
    5403: "여러 성이 \x1bCB다케다군\x1bCZ에 함락되거나 계략에 넘어갔고,\n마침내 거성 \x1bCC미노와성\x1bCZ만 고립되었다.",
    5404: "\x1bCA나리모리\x1bCZ는 굴하지 않고 계속 싸웠으나,\n수가 너무 적었고,\n\x1bCC미노와성\x1bCZ은 곧 함락될 지경이었다.",
    5405: "\x1bCA나리모리\x1bCZ는 불당에서 아버지의 위패에 절하며,\n피를 토하는 심정으로 말했다.",
    5406: "아버님, 말씀하신 대로\n제 목숨을 아끼지 않겠습니다.",
    5407: "그 말을 마친 그는 일족과 가신들과 함께,\n그 자리에서 자결하여 생을 마쳤다.",
    5408: "이렇게 \x1bCB나가노 가문\x1bCZ은 멸망했고, 정예로 이름난\n\x1bCB미노와중\x1bCZ도 \x1bCB다케다\x1bCZ에 항복했다.",
    5409: "하지만 \x1bCA[bm1251]\x1bCZ의 거듭된 권유를 단호히 거절하고,\n여러 나라를 떠돈 자도 있었다.",
    5410: "그 이름은 \x1bCA가미이즈미 노부츠나\x1bCZ.\n코즈케 제일창의 감장을 받은 용맹한 무사였다.",
    5411: "훗날 검성으로 칭송된 신카게류의 창시자다.",
    5412: "\x1bCA오다 노부나가\x1bCZ는 \x1bCC미노\x1bCZ 침공을 시작함과 동시에,\n훗날 상경할 때를 대비해\n\x1bCC오미\x1bCZ를 조사하기 시작했다.",
    5413: "살무사의 자식들은 하찮다.\n하지만 \x1bCC오와리\x1bCZ에서 너무 많은 시간을 썼군……",
    5414: "여기서 더 시간을 버리기는 아깝다.\n외교로 공세를 펼쳐 볼까……",
    5415: "오라버니, 무슨 말씀이십니까?",
    5416: "\x1bCA오이치\x1bCZ여……\n\x1bCC오미\x1bCZ로 가거라.\n\x1bCA아자이 나가마사\x1bCZ에게 시집가라!",
    5417: "……알겠습니다.\n곧 준비하겠습니다.",
    5418: "참으로 순순히 따르는구나.\n잘 알지도 못하는 사내와 부부가 되는데,\n망설여지지 않느냐?",
    5419: "오라버니께 반대해도 소용없으니까요.\n게다가 오라버니께서 고르신 배필이라면,\n분명 훌륭한 분일 테지요.",
    5420: "역시 \x1bCA오이치\x1bCZ로구나.\n안심해라. \x1bCA나가마사\x1bCZ는 장차 \x1bCC오미\x1bCZ 한 나라를 맡을,\n믿음직한 젊은 무사라 들었다.",
    5421: "내 매제가 될 \x1bCA나가마사\x1bCZ도 내 오른팔이 되어,\n함께 천하로 가는 길을 걷게 될 것이다.\n그 인연의 열쇠가 바로 \x1bCA오이치\x1bCZ, 너다!",
    5422: "(오라버니께 도움이 될 수 있다면 저는……\n　안녕히 계세요, 오라버니.\n　부디 오래도록 건강하세요.)",
    5423: "\x1bCB아자이 가문\x1bCZ·\x1bCC오다니성\x1bCZ――",
    5424: "\x1bCA나오쓰네\x1bCZ.\n그대는 이 제안을 거절해야 한다는 말인가?",
    5425: "그렇습니다……\n\x1bCC오와리\x1bCZ의 주인 \x1bCA노부나가\x1bCZ는 속을 알 수 없는 사내입니다.",
    5426: "화평을 지켜도 속마음을 결코 보이지 않을 겁니다.\n언제 우리에게 칼을 겨눌지 모릅니다.\n손을 잡아도 평안해질 수 없습니다.",
    5427: "그러니 믿음직하지 않아도,\n선대부터 인연이 있는 \x1bCB아사쿠라\x1bCZ를 중시하자는 것인가?",
    5428: "……그렇습니다.",
    5429: "그런 생각으로는\n이 난세를 헤쳐 나갈 수 없다고 본다.",
    5430: "게다가 나는 \x1bCB아자이 가문\x1bCZ을 아버지 때보다 번성시키고,\n훗날 \x1bCC교토\x1bCZ로 올라갈 생각이다.\n그러려면 \x1bCA오다\x1bCZ 공의 도움이 필요하다.",
    5431: "…………",
    5432: "그 목적을 위해서다, \x1bCA나오쓰네\x1bCZ.\n모두를 설득하도록 나를 도와다오!",
    5433: "……주군의 명이라면 어쩔 수 없군요.\n따르겠습니다.",
    5434: "\x1bCB아자이 가문\x1bCZ은 \x1bCA나가마사\x1bCZ의 조부 \x1bCA스케마사\x1bCZ 때부터\n\x1bCB아사쿠라 가문\x1bCZ과 동맹했으며, \x1bCA나가마사\x1bCZ도\n\x1bCB아사쿠라 가문\x1bCZ에 대한 의리를 중시하리라 여겨졌다.",
    5435: "하지만 \x1bCB아자이 가문\x1bCZ의 젊은 당주 \x1bCA나가마사\x1bCZ는,\n신흥 세력 \x1bCA노부나가\x1bCZ와 손잡는 길을 택했다.\n이렇게 혼인 동맹이 맺어졌다……",
    5436: "저는 \x1bCA오다 노부나가\x1bCZ의 누이 \x1bCA오이치\x1bCZ입니다.\n부족한 몸이나, 오래도록 잘 부탁드립니다.",
    5437: "나는 \x1bCA나가마사\x1bCZ다.\n앞으로 함께 걸어가자!",
    5438: "이렇게 \x1bCC오미\x1bCZ에서 한 쌍의 부부가 태어났다.\n두 사람 앞에 슬픈 운명이 기다리고 있으리라고는,\n아직 아무도 상상하지 못했다……",
    5439: "\x1bCB아마고 가문\x1bCZ이 멸망한 뒤,\n어느 초승달 뜬 밤――",
    5440: "내가 온 힘을 바친 \x1bCB아마고 가문\x1bCZ이\n끝내 멸망하고 말다니……\n우리 가신들의 힘이 모자랐던 것인가?",
    5441: "달이여, 내게 알려 다오!\n나는 무엇을 해야 하는가?\n무엇이 부족했던 것인가?",
    5442: "\x1bCA시카노스케\x1bCZ는 어느 날 초승달에\n‘명예로운 공을 세우게 해 달라’고 빌어\n그 소원을 이룬 뒤부터……",
    5443: "고난이 닥칠 때마다 홀로,\n달에게 기도하게 되었다.",
    5444: "그때는 공을 세우려 필사적이었다.\n이제 다시 죽을힘을 다하리라.\n\x1bCB아마고 가문\x1bCZ을 부흥시키기 위해……",
    5445: "달이여! 내게 칠난팔고를 내려 주소서!\n모든 고난을 이겨 내 보이겠습니다!\n그날에는 주가를 되살릴 힘을 주소서!",
    5446: "자신의 비원이 이루어지길 비는 대신,\n달에게 칠난팔고를 빈 \x1bCA야마나카 시카노스케\x1bCZ.",
    5447: "그 뒤 그는 각지를 떠돌며,\n온갖 수단을 다해 \x1bCB아마고 가문\x1bCZ의 부흥에 매진했다……",
    5448: "아버지 \x1bCA요시타쓰\x1bCZ가 급사한 뒤, 젊은 \x1bCA사이토 다쓰오키\x1bCZ는\n\x1bCC이나바야마성\x1bCZ의 주인으로 \x1bCC미노\x1bCZ를 이끌게 되었고,\n그 중압감 때문인지 주색에 빠졌다.",
    5449: "뜻있는 가신들은 그 상황을 걱정해,\n몇 번이나 \x1bCA다쓰오키\x1bCZ에게 행실을 고치라 간했으나,\n\x1bCA다쓰오키\x1bCZ는 들으려 하지 않았다……",
    5450: "\x1bCA다쓰오키\x1bCZ 님은 오늘도 술잔치인가!\n우리의 간언을 조금도 듣지 않으시니!\n참으로 분통한 일이로다!",
    5451: "\x1bCA이나바 요시미치\x1bCZ.\n훗날 입도명인 ‘\x1bCA잇테쓰\x1bCZ’로 더 잘 알려진다.\n완고하기로 이름난 용맹한 무사다.",
    5452: "이대로라면 \x1bCC미노\x1bCZ의 앞날도 걱정스럽다.\n\x1bCA다쓰오키\x1bCZ 님의 지휘로 \x1bCB오다 가문\x1bCZ의 맹공을\n견뎌 낼 수 있을지……",
    5453: "\x1bCA우지이에 나오모토\x1bCZ. 출가해 ‘\x1bCA보쿠젠\x1bCZ’이라 칭했다.\n본래 \x1bCA구와바라\x1bCZ 성을 썼으며 \x1bCA요시타쓰\x1bCZ의 중용을 받아,\n가신단에서도 중진으로 꼽혔다.",
    5454: "우리도 앞으로 어찌 처신할지\n진지하게 생각할 때가 된 듯하군……",
    5455: "\x1bCA안도 모리나리\x1bCZ. 한때 \x1bCA이가\x1bCZ 성을 썼다.\n\x1bCA도산\x1bCZ, \x1bCA요시타쓰\x1bCZ, \x1bCA다쓰오키\x1bCZ 삼대를 섬긴 중신이며,\n\x1bCA우지이에\x1bCZ, \x1bCA이나바\x1bCZ와 가까웠다.",
    5456: "그들이 주군을 포기하려던 때에 호응하듯,\n적 \x1bCB오다 가문\x1bCZ도\n연이어 회유 공작을 걸어왔다.",
    5457: "우리에게 \x1bCB오다 가문\x1bCZ으로 돌아서라는 건가?\n그리 쉬운 일은 아닐세……",
    5458: "그리해 주시면 물론 감사하나,\n억지로 청하지는 않겠습니다.\n그저 못 본 척만 해 주신다면……",
    5459: "\x1bCB오다 가문\x1bCZ이 \x1bCC이나바야마성\x1bCZ을 공격해도,\n우리는 구원군을 보내지 말라는 뜻인가?",
    5460: "그러면 직접 \x1bCA다쓰오키\x1bCZ 공을 배신하는 것은 아니니,\n여러분도 마음이 괴롭지 않을 겁니다.\n어떻습니까, \x1bCA이나바\x1bCZ 공?",
    5461: "으음……\n좀 생각하게 해 주게!",
    5462: "이처럼 열심히 설득한 끝에,\n\x1bCA안도\x1bCZ, \x1bCA이나바\x1bCZ, \x1bCA우지이에\x1bCZ 세 중신의 마음은\n이미 \x1bCB오다 가문\x1bCZ으로 기울어 있었다……",
    5463: "기둥부터 크게 흔들린 \x1bCB사이토 가문\x1bCZ은,\n\x1bCA오다 노부나가\x1bCZ가 쳐들어오기 전부터\n이미 속이 빈 것이나 다름없었다.",
    5464: "훗날 \x1bCB오다 가문\x1bCZ에서도 중용된 세 사람은,\n‘미노 삼인중’이라 불리게 된다……",
    5465: "\x1bCA아시카가\x1bCZ 막부 재건을 명분으로 내건 \x1bCA오다 노부나가는,\n\x1bCZ\x1bCC교토\x1bCZ의 적대 세력을 모두 몰아내고,\n\x1bCA아시카가 요시아키\x1bCZ를 쇼군 자리에 복귀시켰다.",
    5466: "\x1bCA노부나가\x1bCZ 공,\n그대에게 아무리 감사해도 모자라오……",
    5467: "그러니 그대를 간레이에 임명하고자 하오.",
    5468: "감사한 분부입니다만,\n제게는 너무 벅찬 직책입니다.",
    5469: "흐음……\n그렇다면 부쇼군 자리는 어떻소?",
    5470: "그 또한 감사한 분부이나,\n역시 제게는 벅찬 직책입니다……",
    5471: "(이 사내……\n　대체 무엇을 원하는가?)",
    5472: "제 소망은 간단합니다. \x1bCC오와리\x1bCZ와\n\x1bCC미노\x1bCZ 영지를 보장받고,\n\x1bCC이즈미\x1bCZ 한 곳을 다스리면 충분합니다.",
    5473: "뭐야, 그 정도면 되는가?\n참으로 욕심이 없구려……",
    5474: "\x1bCC이즈미\x1bCZ에는 아직 \x1bCB미요시\x1bCZ 무리가 있지만……\n좋소. 마음껏 빼앗아 보시오.",
    5475: "참으로 감사한 일입니다.\n본디 그럴 생각이었습니다.\n그럼 이만……",
    5476: "……잠깐, \x1bCA노부나가\x1bCZ 공!",
    5477: "예!",
    5478: "그렇다면 이제부터 그대를,\n나의 아버지, 막부의 아버지라 부르겠소.\n후후, 이래도 거절하지는 않겠지?",
    5479: "예.\n삼가 받들겠습니다.",
    5480: "그날 밤·\x1bCA노부나가\x1bCZ의 숙소――",
    5481: "정말이지,\n\x1bCC교토\x1bCZ 사람들은 왜 그리 빙빙 돌려 말하지?",
    5482: "그것이 아마 \x1bCC교토\x1bCZ의 방식이겠지요……",
    5483: "시시하군.\n나를 떠보는 것인지 모르겠지만,\n거절하면 속 깊은 자로 보이기야 하겠지.",
    5484: "말씀하신 대로입니다.",
    5485: "게다가 내게 간레이나 부쇼군 자리는\n아무 가치도 없다. \x1bCC교토\x1bCZ 거리와 \x1bCA미쓰히데\x1bCZ,\n그 둘을 얻은 것이 가장 큰 수확이다.",
    5486: "황송합니다……",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    5366: ["kawanamishu_and_nagaragawa_terms_require_glossary_review"],
    5385: ["joshu_tiger_epithet_requires_glossary_review"],
    5410: ["ueno_first_spear_commendation_requires_historical_review"],
    5434: ["azai_asakura_alliance_lineage_crosschecked_against_sc_jp"],
    5445: ["seven_hardships_phrase_requires_glossary_review"],
    5451: ["ittetsu_buddhist_name_requires_glossary_review"],
    5453: ["bokuzen_and_kuwabara_names_require_glossary_review"],
    5455: ["ando_morinari_name_history_requires_glossary_review"],
    5464: ["mino_triumvirate_term_requires_glossary_review"],
    5465: ["sc_cross_line_esc_span_preserved_exactly"],
    5467: ["kanrei_title_requires_glossary_review"],
    5469: ["deputy_shogun_title_requires_glossary_review"],
    5478: ["father_of_shogunate_anecdote_requires_historical_review"],
}

PREVIOUS_ARTIFACT_PINS = {
    **shared.PREVIOUS_ARTIFACT_PINS,
    "evidence/alignment_evidence.v0.18.json": (
        "E1D40FC55AF570DC9298F87EC720435366AA55DEDAE5F54956C9C49E770145A4"
    ),
    "public/msgev_ko_historical_events_5238_5358.v0.18.json": (
        "B6E9F58EBC968B89D6B8765F22E3353F234B3418CE441A6DDE7442B70F164EE1"
    ),
    "review/review_index.v0.18.json": (
        "1EB13DC83C2A2F49CC1532D299FD8FFC1B5F5242FE4F259CA67E9AE7F51801C7"
    ),
    "validation.v0.18.json": (
        "279A28FEC4B400CAF027D84441CCBBCD948B1A7759C403833E5FE289B8BD546B"
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
    if len(ids) != 128 or ids != sorted(TRANSLATIONS):
        raise ValueError("batch19 ids are not the exact 128 displayed entries")
    return ids


def event_for(entry_id: int) -> str:
    matches = [
        event["event_id"]
        for event in EVENTS
        if event["start_id"] <= entry_id <= event["end_id"]
    ]
    if len(matches) != 1:
        raise ValueError(f"id {entry_id} does not map to one batch19 event group")
    return str(matches[0])


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
        5358,
        5359,
        5382,
        5383,
        5411,
        5412,
        5438,
        5439,
        5447,
        5448,
        5464,
        5465,
        5486,
        5487,
    )
    evidence["schema"] = "nobu16.kr.event-dialogue-alignment-evidence.v19"
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
    review["schema"] = "nobu16.kr.event-dialogue-review-index.v19"
    validation["schema"] = "nobu16.kr.event-dialogue-generation-validation.v19"
    validation["font_integration"].pop(
        "current_font_or_installer_must_not_include_batch18", None
    )
    validation["font_integration"][
        "current_font_or_installer_must_not_include_batch19"
    ] = True
    integrity = validation["preexisting_integrity"]
    integrity["dialogue_v01_v18_artifacts_before"] = integrity.pop(
        "dialogue_v01_v17_artifacts_before"
    )
    integrity["dialogue_v01_v18_artifacts_after"] = integrity.pop(
        "dialogue_v01_v17_artifacts_after"
    )
    safety = validation["safety"]
    safety.pop(
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_v14_v15_v16_v17_artifacts_modified",
        None,
    )
    safety[
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_v14_v15_v16_v17_v18_artifacts_modified"
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
