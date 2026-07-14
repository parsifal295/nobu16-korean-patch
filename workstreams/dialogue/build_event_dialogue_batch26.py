#!/usr/bin/env python3
"""Build source-free Korean historical event dialogue batch26 (6269-6372)."""

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
import build_event_dialogue_batch25 as shared  # noqa: E402


source_shared = shared.source_shared
BATCH_ID = "msgev_historical_events_6269_6372.v0.26"
OVERLAY_NAME = "msgev_ko_historical_events_6269_6372.v0.26.json"
EVIDENCE_NAME = "alignment_evidence.v0.26.json"
REVIEW_NAME = "review_index.v0.26.json"
VALIDATION_NAME = "validation.v0.26.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 6269
SCOPE_END = 6372
EXCLUDED_INTERNAL_IDS: tuple[int, ...] = ()
BRACKET_TOKEN_RE = shared.BRACKET_TOKEN_RE

EVENTS = (
    {
        "event_id": "yoshiaki_breaks_with_nobunaga",
        "title_ko": "요시아키와 노부나가의 결별",
        "start_id": 6269,
        "end_id": 6287,
        "selected_count": 19,
    },
    {
        "event_id": "fall_of_asakura_clan",
        "title_ko": "아사쿠라 가문의 멸망",
        "start_id": 6288,
        "end_id": 6300,
        "selected_count": 13,
    },
    {
        "event_id": "mitsuhide_joins_hokoshu",
        "title_ko": "미쓰히데의 호코슈 편입",
        "start_id": 6301,
        "end_id": 6322,
        "selected_count": 22,
    },
    {
        "event_id": "hisahide_submits_to_nobunaga",
        "title_ko": "마쓰나가 히사히데의 노부나가 귀순",
        "start_id": 6323,
        "end_id": 6348,
        "selected_count": 26,
    },
    {
        "event_id": "sakichi_and_three_cups_of_tea",
        "title_ko": "사키치와 세 잔의 차",
        "start_id": 6349,
        "end_id": 6372,
        "selected_count": 24,
    },
)

TRANSLATIONS: dict[int, str] = {
    6269: "상경한 뒤, \x1bCA아시카가 요시아키\x1bCZ와 \x1bCA오다 노부나가\x1bCZ는\n서로 이용하면서도 협력 관계를 유지해,\n\x1bCC교토\x1bCZ를 다스리며 주변 적과 맞서 왔다.",
    6270: "하지만 \x1bCA노부나가\x1bCZ에 대한 반항이 거세지면서,\n\x1bCA요시아키\x1bCZ와 측근들은 \x1bCA노부나가\x1bCZ의 우위에\n서서히 의문을 품기 시작했다……",
    6271: "\x1bCB오다 가문\x1bCZ도 그런 불신을 감지하고,\n\x1bCB아시카가 쇼군가\x1bCZ를 더 의심하고 경계했다.",
    6272: "‘이견 17개조’라니?\n그게 무엇이냐?",
    6273: "이는 \x1bCA오다 노부나가\x1bCZ 님께서\n공방님께 올린 의견서인 듯합니다.",
    6274: "‘이견 17개조’는 이전의 ‘전중어정’과 달리,\n처음부터 끝까지 \x1bCA요시아키\x1bCZ와 그 측근을 비판한\n일방적인 의견서였다.",
    6275: "\x1bCA노부나가\x1bCZ 놈…… 나를 쇼군으로 무엇이라 여기는가!\n내가 \x1bCA노부나가\x1bCZ의 도움으로 쇼군이 된 것은 사실이나,\n나 없이는 \x1bCA노부나가\x1bCZ도 있을 수 없었을 텐데!",
    6276: "하지만 지금은 참으셔야 합니다……\n\x1bCB아시카가\x1bCZ와 \x1bCB오다\x1bCZ의 유대가 천하 평정의 열쇠이니……",
    6277: "\x1bCA호소카와\x1bCZ 님, 더는 공방님께 인내를 강요할\n필요가 없습니다! 공방님, 희소식입니다!",
    6278: "무슨 일이냐!",
    6279: "전선에서 급보입니다. \x1bCA[b1251]\x1bCZ께서 \x1bCB오다 가문\x1bCZ을\n쓰러뜨리고자 군사를 일으켜 \x1bCC미카타가하라\x1bCZ에서\n\x1bCA노부나가\x1bCZ의 동맹 \x1bCB도쿠가와 가문\x1bCZ을 격파했다 합니다!",
    6280: "뭐라! \x1bCA[bm1251]\x1bCZ가 마침내 일어섰단 말인가……!",
    6281: "이 기회를 놓쳐서는 안 됩니다!\n공방님도 곧바로 \x1bCA노부나가\x1bCZ 토벌을 위해 거병하십시오!",
    6282: "기다리십시오!\n안 됩니다!\n\x1bCA오다\x1bCZ 님과 싸워서는 승산이 없습니다!",
    6283: "\x1bCA호소카와\x1bCZ 님은 \x1bCB오다\x1bCZ 편을 지나치게 드시는군.\n공방님께서 친히 거병하시면 여러 다이묘도 따르리라!\n쓸데없는 참견은 필요 없다!",
    6284: "에잇, 입 다물어라!\n공방님, 절대 아니 됩니다!",
    6285: "…………",
    6286: "아직 겉으로 드러내지는 않았으나, 이 무렵부터\n\x1bCA요시아키\x1bCZ는 속으로 \x1bCA노부나가\x1bCZ를 완전히 저버리고,\n거병 계획을 세우기 시작했다.",
    6287: "천하포무를 깃발로 내걸고,\n함께 여기까지 나아온 두 야심가.\n하지만 두 사람이 갈라설 때가 다가오고 있었다……",
    6288: "\x1bCA아사쿠라 도시카게\x1bCZ(훗날 \x1bCA에이린\x1bCZ) 이래,\n\x1bCC이치조다니성\x1bCZ을 본거지로 약 백 년 동안\n\x1bCC에치젠\x1bCZ 한 나라를 다스린 \x1bCB아사쿠라 가문\x1bCZ……",
    6289: "마침내 그 종말의 때가 왔다.\n그 끝을 고한 것은 \x1bCB오다 가문\x1bCZ의 군세였다.\n\x1bCA노부나가\x1bCZ는 주저 없이 \x1bCC이치조다니\x1bCZ 성하에 방화를 명했다.",
    6290: "\x1bCC호쿠리쿠\x1bCZ의 \x1bCC작은 교토\x1bCZ라 불리며,\n백 년 영화가 깃든 \x1bCB아사쿠라 가문\x1bCZ의 \x1bCC이치조다니\x1bCZ 성하도,\n모두 무자비한 불길에 휩싸였다.",
    6291: "내가 무슨 잘못을 했단 말인가.\n\x1bCA노부나가\x1bCZ에게 거역한 것이 죄인가?\n선조에게서 물려받은 땅을 불태울 만큼……",
    6292: "아아, \x1bCA소테키\x1bCZ 님만 살아 계셨더라면,\n이런 일은 일어나지 않았을 텐데……",
    6293: "주군……\n우선 이곳에서 피하셔야 합니다!",
    6294: "망연자실한 \x1bCA아사쿠라 요시카게\x1bCZ는\n자기 목숨만이라도 부지하려 \x1bCA아사쿠라 가게아키라\x1bCZ의 인도로\n간신히 달아났다.",
    6295: "그러나 \x1bCA요시카게\x1bCZ의 절망은 끝나지 않았다.\n마지막까지 따르던 \x1bCA아사쿠라 가게아키라\x1bCZ가\n설마 \x1bCB오다 측\x1bCZ으로 돌아설 줄이야……",
    6296: "이놈, \x1bCA가게아키라\x1bCZ!\n너마저 나를 버리는가!",
    6297: "이제 더 저항해도 소용없습니다.\n이쯤에서 \x1bCB아사쿠라 가문\x1bCZ의 마지막 당주로서\n합당한 최후를 맞으십시오……",
    6298: "이런 곳에서 죽다니……\n원통하다…… 원통하구나!!",
    6299: "가신들에게 모조리 배신당해,\n너무도 비통한 최후를 강요받은 \x1bCA아사쿠라 요시카게\x1bCZ의\n자결로써……",
    6300: "\x1bCC에치젠\x1bCZ의 센고쿠 다이묘 \x1bCB아사쿠라 가문\x1bCZ의 역사는,\n이렇게 막을 내렸다.",
    6301: "\x1bCA아시카가 요시아키\x1bCZ가 \x1bCA오다 노부나가\x1bCZ의 도움으로\n상경해 세이이타이쇼군에 오른 뒤에는,\n두 사람을 이어 준 \x1bCA아케치 미쓰히데\x1bCZ의 노력이 있었다.",
    6302: "그런 인연으로 \x1bCA미쓰히데\x1bCZ는 \x1bCB아시카가\x1bCZ·\n\x1bCB오다\x1bCZ 양 가문에 몸담아 일했고,\n누구의 가신인지 모호해지고 있었다.",
    6303: "\x1bCA[bm1773]\x1bCZ, 요즘 \x1bCA미쓰히데\x1bCZ와 만나고 있느냐?",
    6304: "아닙니다. \x1bCA오다\x1bCZ 님의 명을 받아 눈부시게 활약하느라,\n몹시 바쁜 모양이라\n저도 좀처럼 만나지 못하고 있습니다……",
    6305: "그렇다. \x1bCA미쓰히데\x1bCZ는 본래 우리 가신일 터.\n언제부터인가 \x1bCB오다\x1bCZ 가신처럼\n대우받는 것은 몹시 불쾌하구나!",
    6306: "\x1bCA[bm1773]\x1bCZ. \x1bCA미쓰히데\x1bCZ를 만나 속마음을 확인해 오너라.\n네가 \x1bCB오다\x1bCZ를 택할지,\n\x1bCB아시카가\x1bCZ를 택할지 말이다……!",
    6307: "\x1bCA요시아키\x1bCZ의 질책을 받은 \x1bCA미쓰히데\x1bCZ는 당혹스러웠다.\n그는 \x1bCB아시카가\x1bCZ·\x1bCB오다\x1bCZ 양 가문을 위해\n동분서주한 것뿐이었기 때문이다.",
    6308: "공방님께서 그런 말씀을 하시다니……\n저야말로 섭섭합니다.",
    6309: "그토록 말씀하시니 진퇴양난입니다.\n출가하여 은둔하는 길밖에 없겠군요.",
    6310: "자, 그리 성급히 굴지 마십시오.\n공방님께서 \x1bCA아케치\x1bCZ 님을 중히 여기시기에\n놓아주고 싶지 않으신 것입니다.",
    6311: "그대만 좋다면,\n\x1bCB아시카가 가문\x1bCZ의 직신이라는 증거로\n호코슈에 이름을 올려도 좋다 하셨소.",
    6312: "호코슈는 막부의 직제다.\n실권은 없었으나 쇼군 직속의 명예로운\n지위로 여겨졌다.",
    6313: "고마운 말씀이지만, 호코슈에 들면\n\x1bCB오다 가문\x1bCZ과 양속할 수는 없으니.\n어찌해야 할까……",
    6314: "\x1bCA미쓰히데\x1bCZ는 여전히 망설였으나, \x1bCA호소카와 후지타카\x1bCZ의\n열성적인 설득으로 호코슈가 되기를 승낙하고,\n\x1bCA요시아키\x1bCZ에게 감사 인사를 올렸다.",
    6315: "이번에 공방님께서 친히 명하여 호코슈에\n들게 해 주셨으니, 참으로 감사합니다.\n감사의 말씀을 올립니다……",
    6316: "그래.\n앞으로는 \x1bCB아시카가 가문\x1bCZ을 섬기는 일을 첫째로 삼아,\n더욱 충성을 다하거라!",
    6317: "예!\n이 \x1bCA미쓰히데\x1bCZ, 힘이 다하는 날까지……",
    6318: "（이것으로 좋다……\n　이런 유능한 사내를 \x1bCA노부나가\x1bCZ에게 독점시키는 것은\n　너무 아까운 일이니）",
    6319: "（\x1bCA요시아키\x1bCZ 님을 섬기는 일 자체엔 이의가 없다……\n　하지만 결과적으로 \x1bCA노부나가\x1bCZ 님을 배신하게 된다.\n　이 결정이 정말 옳았을까……）",
    6320: "이렇게 \x1bCA미쓰히데\x1bCZ는 \x1bCB오다\x1bCZ·\n\x1bCB아시카가\x1bCZ 양 가문에 속한 어정쩡한 처지를 벗어나,\n\x1bCA요시아키\x1bCZ의 직신으로 일하게 되었다……",
    6321: "뭐라, \x1bCA미쓰히데\x1bCZ가!?\n이놈…… 나보다 공방을 택했단 말인가!",
    6322: "재능은 있어도 어리석은 사내로군……\n훗날 후회하지나 마라!",
    6323: "\x1bCA미요시 나가요시\x1bCZ가 죽은 뒤 뒤를 이은 \x1bCA미요시 요시쓰구\x1bCZ는,\n가문의 실력자인 미요시 삼인중에게 주도권을 빼앗겨\n구심력이 떨어지고 있었다.",
    6324: "본래 \x1bCB미요시\x1bCZ 가문 안에서도 \x1bCA나가요시\x1bCZ의 아우들과\n분가의 중진인 삼인중, 그리고 \x1bCA나가요시\x1bCZ 측근\n\x1bCA마쓰나가 히사히데\x1bCZ 등은 서로 반목하고 있었다.",
    6325: "\x1bCB미요시 가문\x1bCZ의 핵심이던 \x1bCA나가요시\x1bCZ가 죽은 뒤,\n\x1bCA요시쓰구\x1bCZ로는 그 분열을 막지 못해,\n가문 내 다툼은 갈수록 격화됐다……",
    6326: "삼인중 놈들…… \x1bCA나가요시\x1bCZ 님이 돌아가신 뒤,\n안하무인으로 구는 꼴은 눈 뜨고 못 보겠다!\n\x1bCA요시쓰구\x1bCZ 님도 너무 마음이 약하시고……",
    6327: "\x1bCA나가요시\x1bCZ 님께서 돌아가실 때,\n\x1bCA요시쓰구\x1bCZ 님을 받들겠다고 맹세했지만,\n이제는 그것도 어려울지 모르겠군……",
    6328: "（\x1bCA요시쓰구\x1bCZ가 그릇이 못 된다면……\n　네가…… \x1bCB미요시 가문\x1bCZ을 짊어지거라……）",
    6329: "한때 \x1bCA나가요시\x1bCZ 님은 쇼군의 권력을 넘어,\n\x1bCC기나이\x1bCZ를 다스렸다. 그런 자리에 서려는\n사내가 나타난 듯하군.",
    6330: "\x1bCA오다 노부나가\x1bCZ…… 그 사내가\n\x1bCA나가요시\x1bCZ 님에 버금가는 그릇을 지녔다면,\n그쪽에 붙는 길도 있겠군.",
    6331: "후후…… 이런 때에는\n평소 괴짜니 악당이니 욕먹던 명성이\n도움이 될지도 모르겠군.",
    6332: "어디, 하나\n삼인중과 \x1bCA오다 노부나가\x1bCZ를 상대로\n큰 연극을 벌여 볼까……",
    6333: "\x1bCA히사히데\x1bCZ는 교묘하게 삼인중에게서\n\x1bCA미요시 요시쓰구\x1bCZ를 떼어 내 품에 안고,\n홀로 \x1bCA오다 노부나가\x1bCZ에게 항복을 청했다.",
    6334: "\x1bCA마쓰나가 히사히데\x1bCZ라고 합니다.\n알현을 허락해 주시길……",
    6335: "그렇군, 네가 \x1bCA히사히데\x1bCZ인가……\n주가를 빼앗고 대불을 불태우며 쇼군을 죽인,\n참으로 흥미로운 사내라 들었다.",
    6336: "과찬이십니다.\n하지만 소문이란 것은\n대개 과장이 심한 법이지요.",
    6337: "뭐냐, 하지 않았단 말인가?\n재미없군……",
    6338: "후후후…… 불 없는 곳에 연기 나랴고도 하지요.\n아, 그건 그렇고\n이는 친분의 표시입니다.",
    6339: "그것은……!\n구주쿠가미 가지인가.\n내가 원하는 것을 알고 있었나?",
    6340: "후후, 신중함도 갖췄군.\n역시 너는 흥미로운 사내인 듯하다!",
    6341: "네가 원하는 것 말이냐……\n\x1bCC야마토\x1bCZ는 차지하는 대로 네 것이니,\n좋을 대로 하거라.",
    6342: "예!\n고마운 말씀입니다.",
    6343: "\x1bCA히사히데\x1bCZ는 \x1bCA미요시 요시쓰구\x1bCZ의 신병을 \x1bCA노부나가\x1bCZ에게 맡기고,\n자신은 \x1bCC시기산성\x1bCZ에서 독립 세력이 되어\n\x1bCA노부나가\x1bCZ에게 종속한 다이묘가 되었다.",
    6344: "\x1bCA나가요시\x1bCZ 님께서 맡기신 \x1bCA요시쓰구\x1bCZ 님을\n삼인중에게서 떼어 내 신변을 지켰다.\n이로써 의리도 다한 셈이지.",
    6345: "이제부터는 악명 높은 이 \x1bCA마쓰나가 히사히데\x1bCZ가\n\x1bCA나가요시\x1bCZ 님의 뜻을 이어 \x1bCA노부나가\x1bCZ를 이용해,\n하고 싶은 대로 하겠다. 하하하!",
    6346: "이놈, \x1bCA히사히데\x1bCZ! 역시 악당이었군!\n우리의 신여를 감쪽같이 빼앗아 갔어!",
    6347: "\x1bCA노부나가\x1bCZ와 \x1bCA히사히데\x1bCZ 따위가 무엇이냐!\n\x1bCC기나이\x1bCZ를 다스릴 수 있는 건 우리뿐이다!\n본때를 보여 주겠다!",
    6348: "\x1bCA요시쓰구\x1bCZ를 빼앗긴 삼인중은 격분해,\n\x1bCA히사히데\x1bCZ와 그를 받아들인 \x1bCA노부나가\x1bCZ에게\n적의를 불태우게 되었다.",
    6349: "\x1bCA기노시타 도키치로\x1bCZ, 새 이름 \x1bCA[b754]\x1bCZ는\n\x1bCA오다 노부나가\x1bCZ에게 공을 인정받아,\n차츰 중신의 길을 걷기 시작했지만……",
    6350: "\x1bCA히데요시\x1bCZ의 약점은\n자신의 가신이 너무 적다는 것이었다.",
    6351: "명문 출신이 아닌 그에게는\n교양과 무예에 뛰어나고 믿음직한 친척도\n그리 많지 않았기 때문이다.",
    6352: "그래서 \x1bCA히데요시\x1bCZ는 장래 있는 젊은이를 등용해\n자기 수하로 길러내고자,\n영지 안을 자주 돌아보았다.",
    6353: "후우, 재능 있는 젊은이라고 해도\n그리 쉽게 찾을 수는 없군!\n조금 피곤하니 저 절에서 쉬어 갈까……",
    6354: "이런, 영주님.\n어서 오십시오.\n무슨 일로 저희 절에 오셨습니까?",
    6355: "아니, 잠시 쉬러 들렀을 뿐이네.\n잠깐 방 하나를 빌릴 수 있겠나?",
    6356: "그렇다면 얼마든지 괜찮습니다.\n여봐라, 영주님께 차를 내어 드려라!",
    6357: "변변찮은 차입니다만……\n드십시오.",
    6358: "……음, 맛있군!\n마침 목이 말랐는데.\n단숨에 마셔 버렸구나. 한 잔 더 주게.",
    6359: "알겠습니다.\n여기……\n아까보다 조금 뜨겁습니다만.",
    6360: "흠, 제법이군.\n아니…… 염치없지만 한 잔 더\n마시고 싶어졌네. 받을 수 있겠나?",
    6361: "사양하지 마십시오.\n세 번째 잔은 더 뜨겁게 우렸으니,\n서두르지 말고 드십시오……",
    6362: "어디 보자…… 후우!\n오오, 이것도 맛있군.",
    6363: "그런데…… 저 아이는 절의 동자승인가?\n차를 타는 솜씨가 제법이군.",
    6364: "이 아이는 \x1bCA사키치\x1bCZ라고 하며,\n예법을 배우러 이 절에 다니는 아이입니다……",
    6365: "（흠. 내 바람을 헤아려 처음에는 미지근한 차를 내고,\n차츰 뜨겁게 한 마음씀씀이……\n얄미울 만큼 영리한 아이로군.）",
    6366: "\x1bCA사키치\x1bCZ라 했느냐, 나를 섬겨 보지 않겠나?\n훗날 훌륭한 장수로 만들어 주겠다.",
    6367: "정말입니까?\n바라던 일이니…… 반드시!\n오늘부터라도 성에 들어가겠습니다!",
    6368: "하하하…… 기쁜 일에는 솔직히 기뻐하는군.\n그런 면은 아직 아이답구나.",
    6369: "아…… 죄송합니다!\n너무 앞서 나갔습니다……\n참으로 분수 없는 자라……",
    6370: "좋다, 좋다…… \x1bCA사키치\x1bCZ야,\n내 아래에서 학문과 무예를 닦거라.\n성장하면 내 가신으로 거두어 주마.",
    6371: "예!\n더없는 영광입니다!",
    6372: "이 \x1bCA사키치\x1bCZ 소년이 훗날,\n\x1bCA히데요시\x1bCZ가 가장 믿는 능리 \x1bCA이시다 미쓰나리\x1bCZ가 되리라고는,\n물론 이때 아무도 알지 못했다……",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    6272: ["iken_junana_kajo_title_requires_glossary_review"],
    6274: ["denchu_okite_term_and_iken_junana_kajo_require_glossary_review"],
    6276: ["tenka_seihitsu_rendered_as_worldly_peace_requires_style_review"],
    6279: ["mikatagahara_and_dynamic_shingen_placeholder_require_review"],
    6288: ["asakura_toshikage_eirin_and_ichijodani_names_require_glossary_review"],
    6290: ["hokuriku_little_kyoto_wording_requires_style_review"],
    6301: ["seii_taishogun_title_requires_glossary_review"],
    6311: ["hokoshu_and_jikishin_status_terms_require_glossary_review"],
    6312: ["hokoshu_institution_explanation_requires_history_review"],
    6314: ["hosokawa_fujitaka_name_and_hokoshu_term_require_review"],
    6323: ["miyoshi_trio_role_requires_glossary_review"],
    6338: ["no_smoke_without_fire_idiom_requires_style_review"],
    6339: ["tsukumo_gami_nasu_tea_caddy_name_requires_glossary_review"],
    6343: ["shigisan_castle_and_vassal_daimyo_status_require_history_review"],
    6346: ["mikoshi_metaphor_rendered_as_shinyeo_requires_style_review"],
    6349: ["dynamic_hideyoshi_placeholder_and_name_change_require_review"],
    6352: ["kogai_retainer_training_nuance_requires_style_review"],
    6365: ["three_cups_of_tea_anecdote_requires_history_review"],
    6372: ["nori_administrator_term_requires_style_review"],
}

PREVIOUS_ARTIFACT_PINS = {
    **shared.PREVIOUS_ARTIFACT_PINS,
    "evidence/alignment_evidence.v0.25.json": (
        "3A1977F08593A2FFC580472E4CCC256B9D035633CC8B4693238D275F550906BF"
    ),
    "public/msgev_ko_historical_events_6142_6268.v0.25.json": (
        "D84EB96DA649971811D80DDFDB154D30E4B305FD2D5889ADB462585A9315D891"
    ),
    "review/review_index.v0.25.json": (
        "02FA3B53EE2AE08E1E6EB7A425816DBC6C8AD529CBB01BD8E0769B150D30B14A"
    ),
    "validation.v0.25.json": (
        "0A7C766B415A97171ADC56E1E92999CB2DEE3D30DD96A23DC4AD8F452676C3F4"
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
        entry_id
        for entry_id in range(SCOPE_START, SCOPE_END + 1)
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
        6268,
        6269,
        6287,
        6288,
        6300,
        6301,
        6322,
        6323,
        6348,
        6349,
        6372,
        6373,
    )
    evidence["schema"] = "nobu16.kr.event-dialogue-alignment-evidence.v26"
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
    review["schema"] = "nobu16.kr.event-dialogue-review-index.v26"
    validation["schema"] = "nobu16.kr.event-dialogue-generation-validation.v26"
    validation["font_integration"].pop(
        "current_font_or_installer_must_not_include_batch25", None
    )
    validation["font_integration"][
        "current_font_or_installer_must_not_include_batch26"
    ] = True
    integrity = validation["preexisting_integrity"]
    integrity["dialogue_v01_v25_artifacts_before"] = integrity.pop(
        "dialogue_v01_v24_artifacts_before"
    )
    integrity["dialogue_v01_v25_artifacts_after"] = integrity.pop(
        "dialogue_v01_v24_artifacts_after"
    )
    safety = validation["safety"]
    safety.pop(
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_v14_v15_v16_v17_v18_v19_v20_v21_v22_v23_v24_artifacts_modified",
        None,
    )
    safety[
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_v14_v15_v16_v17_v18_v19_v20_v21_v22_v23_v24_v25_artifacts_modified"
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
