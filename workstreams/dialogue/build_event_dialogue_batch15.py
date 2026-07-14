#!/usr/bin/env python3
"""Build source-free Korean historical event dialogue batch15 (4839-4976)."""

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
import build_event_dialogue_batch14 as shared  # noqa: E402


BATCH_ID = "msgev_historical_events_4839_4976.v0.15"
OVERLAY_NAME = "msgev_ko_historical_events_4839_4976.v0.15.json"
EVIDENCE_NAME = "alignment_evidence.v0.15.json"
REVIEW_NAME = "review_index.v0.15.json"
VALIDATION_NAME = "validation.v0.15.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 4839
SCOPE_END = 4976
EXCLUDED_INTERNAL_IDS: tuple[int, ...] = ()
BRACKET_TOKEN_RE = shared.BRACKET_TOKEN_RE

EVENTS = (
    {
        "event_id": "akitsura_reforms_yoshishige_with_dance",
        "title_ko": "아키쓰라의 연회와 요시시게의 개심",
        "start_id": 4839,
        "end_id": 4873,
        "selected_count": 35,
    },
    {
        "event_id": "death_of_miyoshi_jikkyu",
        "title_ko": "미요시 짓큐의 죽음",
        "start_id": 4874,
        "end_id": 4887,
        "selected_count": 14,
    },
    {
        "event_id": "takeda_katsuyori_comes_of_age",
        "title_ko": "스와 시로 가쓰요리의 원복",
        "start_id": 4888,
        "end_id": 4910,
        "selected_count": 23,
    },
    {
        "event_id": "sanada_masayuki_comes_of_age",
        "title_ko": "사나다 마사유키의 원복",
        "start_id": 4911,
        "end_id": 4914,
        "selected_count": 4,
    },
    {
        "event_id": "death_of_mori_takamoto",
        "title_ko": "모리 다카모토의 죽음",
        "start_id": 4915,
        "end_id": 4939,
        "selected_count": 25,
    },
    {
        "event_id": "motoyasu_independence_at_okazaki",
        "title_ko": "모토야스의 오카자키 독립",
        "start_id": 4940,
        "end_id": 4976,
        "selected_count": 37,
    },
)

TRANSLATIONS: dict[int, str] = {
    4839: "\x1bCA오토모 요시시게\x1bCZ는 한동안\n평정 자리에 모습을 보이지 않았다.",
    4840: "태생부터 병약했기에 가신들도\n처음에는 걱정했지만, 곧 그것이\n쓸데없는 염려였음을 알게 되었다.",
    4841: "\x1bCA요시시게\x1bCZ는 날마다 자신의 저택에서 연회를 열고,\n주색에 빠져 있었던 것이다.",
    4842: "\x1bCB오토모 가문\x1bCZ·\x1bCC후나이성\x1bCZ――",
    4843: "오늘도 \x1bCA요시시게\x1bCZ 님은 오시지 않는가?",
    4844: "예, 예.\n아직 저택에서…… 그, 연회를……",
    4845: "…………!",
    4846: "히익!",
    4847: "아무래도 손을 써야겠군.",
    4848: "다음 날부터 \x1bCA요시시게\x1bCZ에 이어 \x1bCA아키쓰라\x1bCZ도\n평정 자리에 모습을 보이지 않았다.",
    4849: "사람들은 모두 놀라고 걱정했지만,\n그 이유를 알고는 더욱 놀랐다.",
    4850: "놀랍게도 \x1bCA아키쓰라\x1bCZ도 \x1bCC교토\x1bCZ에서 무희를 불러,\n자신의 집에서 연회를 열고 있었다.",
    4851: "그 소문에 흥미를 느낀 \x1bCA요시시게\x1bCZ는,\n\x1bCA아키쓰라\x1bCZ의 연회에 초대해 달라고 했다.",
    4852: "달맞이, 꽃놀이, 술자리……\n그 모든 것을 싫어하던 그 고지식한 자가,\n설마 이런 춤을 좋아할 줄이야.",
    4853: "음, 음. 좋은 일이군.\n사람이 전쟁만을 위해 사는 건 아니지!\n나까지 기분이 좋아지는구나.",
    4854: "그러면 먼저,\n‘삼박자’라 불리는 춤입니다.",
    4855: "음?\n\x1bCA아키쓰라\x1bCZ는 없는가?\n뭐, 됐다. 시작하라.",
    4856: "그러면……",
    4857: "무희의 경쾌한 춤에,\n\x1bCA요시시게\x1bCZ는 크게 기뻐하며 금세 흥이 올랐다.",
    4858: "보잘것없는 춤을 보여 드려 송구합니다.",
    4859: "아니, 아니다!\n그렇지 않다!\n과연 \x1bCC교토\x1bCZ의 춤이군. 훌륭하고 아름답다!",
    4860: "이게 끝인가?\n다음 춤은 없는 것이냐……?\n뭐, 됐다. 누구 없느냐, 술을 따라라.",
    4861: "그렇다면 그 일은 제가 맡겠습니다.",
    4862: "헉! \x1bCA아키쓰라\x1bCZ!!",
    4863: "이제야 얼굴을 보여 주셨군요.\n주군께 드릴 말씀이 있습니다.",
    4864: "…………",
    4865: "그리하여 \x1bCA아키쓰라\x1bCZ가 주색에 빠지지 말라며\n간곡히 타이르자, \x1bCA요시시게\x1bCZ도 그 뜻을 이해하고,\n앞으로 태도를 고치겠다고 맹세했다.",
    4866: "이때,\n\x1bCA아키쓰라\x1bCZ가 부른 무희들의 춤은\n‘쓰루사키오도리’로 오늘날까지 전해진다.",
    4867: "다음 날,\n\x1bCB오토모 가문\x1bCZ·\x1bCC후나이관\x1bCZ――",
    4868: "\x1bCA아키쓰라\x1bCZ.\n내가 뉘우쳤다는 증거로,\n출가하려고 한다.",
    4869: "이제부터 법호를 ‘\x1bCA소린\x1bCZ’이라 하겠다.\n어떠냐, 좋은 이름이지?",
    4870: "(주군은 타이르면 받아들이는 분이지만,\n　그때뿐인 경우가 많다……)",
    4871: "(이 일이 훗날 큰 재앙을 부르지 않아야 할 텐데……\n　아니, 그렇게 되지 않도록\n　내가 더욱 힘써야 한다.)",
    4872: "\x1bCA요시시게\x1bCZ가 출가하자,\n\x1bCA아키쓰라\x1bCZ도 뒤따라 출가해 ‘\x1bCA도세쓰\x1bCZ’이라 칭했다.",
    4873: "그 법호에는\n‘길 위의 눈은 녹을 때까지 자리를 옮기지 않는다’는\n\x1bCA도세쓰\x1bCZ의 의로운 마음이 담겼다고 한다.",
    4874: "\x1bCB미요시 가문\x1bCZ은 \x1bCB오가사와라 가문\x1bCZ의 지류로,\n\x1bCC아와 미요시군\x1bCZ이 성씨의 땅이다. \x1bCA미요시 나가요시\x1bCZ가\n상경한 뒤에도 \x1bCC아와\x1bCZ 중심의 \x1bCC시코쿠\x1bCZ가 기반이었다.",
    4875: "형 \x1bCA나가요시\x1bCZ와 동생 \x1bCA소고 가즈마사\x1bCZ가 \x1bCC기나이\x1bCZ를 다스릴 때,\n\x1bCC시코쿠\x1bCZ를 통치하며 기반을 지킨 이는\n\x1bCA미요시 짓큐\x1bCZ였다. 하지만……",
    4876: "\x1bCA마쓰나가\x1bCZ 님, 큰일입니다!\n\x1bCA미요시 짓큐\x1bCZ 님이 \x1bCC이즈미\x1bCZ에서…… \x1bCB네고로슈\x1bCZ가 쏜\n총탄에 맞아 전사하셨습니다……",
    4877: "뭐라고!?\n그게 사실이냐? \x1bCA짓큐\x1bCZ 님이……",
    4878: "\x1bCB미요시 가문\x1bCZ의 얼굴은 \x1bCA나가요시\x1bCZ 님…… 틀림없지만,\n뒤에서 떠받친 이는 \x1bCA짓큐\x1bCZ 님이었다……",
    4879: "얼마 전 \x1bCA소고 가즈마사\x1bCZ 님이 돌아가셨는데, 이제\n\x1bCA짓큐\x1bCZ 님마저…… 앞으로 \x1bCB미요시 가문\x1bCZ은\n어찌 되는 것인가?",
    4880: "남은 아우 \x1bCA아타기 후유야스\x1bCZ 님에게마저……\n만일의 일이 생기면 어찌한단 말인가.",
    4881: "어쩌면 세상은 이 \x1bCA히사히데\x1bCZ가 \x1bCB미요시 가문\x1bCZ을\n쥐락펴락하려고 아우들을 차례로\n죽였다고 떠들지도 모르겠군……",
    4882: "나만큼 \x1bCB미요시 가문\x1bCZ에 충절을 다하는 이도\n없건만…… 세상이란 제멋대로군.",
    4883: "차라리 진짜 간신이라도……\n되어 볼까?",
    4884: "두 동생 \x1bCA소고 가즈마사\x1bCZ와 \x1bCA미요시 짓큐\x1bCZ를 잇달아\n잃은 \x1bCA미요시 나가요시\x1bCZ는 낙담한 탓인지,\n이후 자주 병석에 눕게 되었다.",
    4885: "\x1bCA나가요시\x1bCZ의 적자 \x1bCA요시오키\x1bCZ는 총명했지만 아직 어려,\n가문을 이끌려면 실력자의\n보좌가 필요했다.",
    4886: "사람들은 그 실력자가 남은 동생\n\x1bCA아타기 후유야스\x1bCZ와 필두 중신 \x1bCA마쓰나가 히사히데\x1bCZ,\n두 사람뿐이라고 입을 모았다.",
    4887: "두 사람이 대치하는 기묘한 균형 속에서\n최악의 사태가 일어나리라고는,\n아직 아무도 상상하지 못했다……",
    4888: "\x1bCB다케다 가문\x1bCZ의 저택――",
    4889: "이날 \x1bCA[b1251]\x1bCZ의 넷째 아들이자,\n\x1bCA스와히메\x1bCZ가 남긴 아이인 \x1bCA시로\x1bCZ가 원복을 맞았다.",
    4890: "\x1bCB다케다 가문\x1bCZ의 가신들은 \x1bCA시로\x1bCZ의 새 이름에\n이목을 집중했다.",
    4891: "이름에 어떤 글자를 쓰느냐에 따라,\n\x1bCA시로\x1bCZ가 앞으로 \x1bCB다케다 가문\x1bCZ에서\n차지할 위치가 정해지기 때문이다.",
    4892: "\x1bCA시로\x1bCZ야.\n세월이 빨라 너도 원복을 맞았구나……",
    4893: "예.",
    4894: "…………",
    4895: "오늘부터 \x1bCA가쓰요리\x1bCZ라 칭하라.\n\x1bCA스와 시로 가쓰요리\x1bCZ, 그것이 네 이름이다.",
    4896: "……!\n(호오, \x1bCB다케다 가문\x1bCZ 대대로 내려온 통자\n　‘노부’는 넣지 않았군.)",
    4897: "(게다가 \x1bCB스와 가문\x1bCZ 대대로 내려온 통자\n　‘요리’를 받다니……\n　주군의 뜻은 분명하군.)",
    4898: "예! 알겠습니다!\n일문의 한 사람으로 이 몸을 바치겠습니다.",
    4899: "음, 좋은 눈빛이구나……\n(어미와 똑같은 눈을 하고 있군.\n　하지만 어미와 같은 길을 걷게 하고 싶지는 않다.)",
    4900: "(\x1bCB다케다 가문\x1bCZ에 얽매이면서도,\n　\x1bCB다케다 가문\x1bCZ 안에서 멸시받는 슬픈 길은 말이다……\n　원하는 대로 살아라, \x1bCA가쓰요리\x1bCZ!)",
    4901: "\x1bCA가쓰요리\x1bCZ, 네가 \x1bCB스와\x1bCZ를 이어 \x1bCC시나노\x1bCZ를 다스려라.\n\x1bCA노부토모\x1bCZ, \x1bCA노부하루\x1bCZ, 너희는\n\x1bCA가쓰요리\x1bCZ를 도와 \x1bCC시나노\x1bCZ를 안정시켜라.",
    4902: "예!\n맡겨 주십시오.",
    4903: "맡겨 주십시오.",
    4904: "그럼 평정은 여기까지다.\n모두 수고했다.",
    4905: "후우……\n\x1bCA가쓰요리\x1bCZ의 어머니가 아버님의 총애를 받았기에,\n어찌 될지 걱정했는데……",
    4906: "하지만 아버님 정도 되는 대장이라면,\n그런 일로 길을 그르치지는 않으시는군.",
    4907: "후후……\n이제 내가 \x1bCB다케다\x1bCZ의 후계자인가……!",
    4908: "\x1bCA다케다 신겐\x1bCZ이 \x1bCA시로\x1bCZ에게 ‘노부’를 주지 않은 것은,\n\x1bCA시로\x1bCZ를 후계자 후보에서 제외한다는\n분명한 의사 표시였다.",
    4909: "이에 따라,\n\x1bCA요시노부\x1bCZ가 \x1bCB다케다\x1bCZ의 차기 당주로 내정되었고,",
    4910: "\x1bCA스와 시로 가쓰요리\x1bCZ는 명문 \x1bCB스와씨\x1bCZ를 이어,\n\x1bCB다케다 가문\x1bCZ의 \x1bCC스와\x1bCZ·\x1bCC시나노\x1bCZ 지배를 굳히는\n초석의 역할을 맡게 되었다.",
    4911: "\x1bCA사나다 유키타카\x1bCZ의 셋째 아들 \x1bCA겐고로\x1bCZ가 원복을 맞았다.",
    4912: "형 \x1bCA노부쓰나\x1bCZ와 \x1bCA마사테루\x1bCZ가 있어 가독을 잇지 못하고,\n\x1bCB무토 가문\x1bCZ에 양자로 들어가,\n\x1bCA기헤에 마사유키\x1bCZ라 칭했다고 한다.",
    4913: "훗날 \x1bCB사나다 가문\x1bCZ으로 돌아와, 탁월한 지혜로\n희대의 모장으로서 지휘를 펼쳐,\n‘표리비흥의 자’라 평가받게 되는 사내……",
    4914: "바로 이때, 난세에\n\x1bCA사나다 마사유키\x1bCZ라는 사내가 풀려난 것이다.",
    4915: "\x1bCB아마고\x1bCZ 공격 준비를 마친 \x1bCA모리 다카모토\x1bCZ는,\n어느 날 밤 국인중의 환대를 받았다.",
    4916: "그 뒤 \x1bCC아키\x1bCZ로 돌아온 \x1bCA다카모토\x1bCZ는,\n잠자리에 들자 몸이 좋지 않다고 호소했다.",
    4917: "후후…… 내가 어리석다는 것은 알고 있다고 여겼는데,\n이런 함정조차 알아채지 못하다니!",
    4918: "계책이 많으면 이기고 적으면 진다…… 인가.\n아버님, 못난 아들을 용서해 주십시오……",
    4919: "\x1bCB모리\x1bCZ의 앞날을…… 모두에게 맡기마……\n\x1bCA고쓰루마루\x1bCZ야…… 못난 아비라 미안하구나……\n쿨럭!",
    4920: "위대한 아버지와 뛰어난 동생의 그늘에 가려서도,\n\x1bCB모리 가문\x1bCZ을 계속 떠받친 \x1bCA다카모토\x1bCZ는,\n이렇게 짧은 생을 마쳤다.",
    4921: "사인은 독살과 병사라는 설이 있으나,\n오늘날까지 명확히 밝혀지지 않았다.",
    4922: "\x1bCA다카모토\x1bCZ의 사망 소식은 곧,\n\x1bCB아마고\x1bCZ 공격을 시작한 \x1bCA모토나리\x1bCZ에게 전해졌다.",
    4923: "뭐, 뭐라고!\n다, \x1bCA다카모토\x1bCZ가…… 그럴 리가……\n정말이냐? 잘못 들은 게 아니냐?",
    4924: "안타깝게도……",
    4925: "말도 안 돼…… 어째서 \x1bCA다카모토\x1bCZ가……\n아비보다 먼저 죽다니…… 이 불효자식!",
    4926: "주, 주군……",
    4927: "…………",
    4928: "주군, 괜찮으십니까?",
    4929: "……잘 들어라. 가신들에게 이렇게 전하라.",
    4930: "\x1bCB아마고\x1bCZ를 멸하는 것이야말로,\n\x1bCA다카모토\x1bCZ를 위한 공양이다.\n평소와 다른 각오로 싸움에 임하라고.",
    4931: "\x1bCA다카모토\x1bCZ가 남긴 아이…… \x1bCA고쓰루마루\x1bCZ, 아니 \x1bCA데루모토\x1bCZ에게,\n\x1bCB아마고\x1bCZ는 아비의 원수나 마찬가지다.\n\x1bCB모리 가문\x1bCZ 모두가 복수전에 나선다.",
    4932: "예!",
    4933: "이것이 업보인가……\n전장에서 적의 목숨을 빼앗고,\n계략으로 적의 핏줄을 끊은 내게 내린…… 업보.",
    4934: "그렇다면 그 업보조차 무략으로 삼아 주마.\n복수전을 명분으로 \x1bCB아마고\x1bCZ를 멸하겠다.",
    4935: "미안하다, \x1bCA다카모토\x1bCZ. 미안해……\n귀축 같은 마음을 지닌 아비를 용서해 다오……",
    4936: "아들들에게 보낸 편지가 많이 남은 \x1bCA모토나리\x1bCZ는,\n가족을 무척 세심하게 사랑한 사람이었다.",
    4937: "틈날 때마다 \x1bCA다카모토\x1bCZ를 훈계한 것도,\n큰 기대와 사랑을 품었다는 증거다.",
    4938: "그 \x1bCA다카모토\x1bCZ를 불운하게 잃은 \x1bCA모토나리\x1bCZ의 슬픔은,\n헤아릴 수 없을 만큼 깊은 동시에,",
    4939: "그 슬픔을 복수전에 이용한\n센고쿠 다이묘로서의 비장한 각오 또한\n전율할 만큼 엄청났다.",
    4940: "\x1bCA이마가와 요시모토\x1bCZ가 설마 \x1bCC오케하자마\x1bCZ에서 전사하다니――\n그 충격적인 소식은 \x1bCB이마가와\x1bCZ 휘하의 한 부대로\n진군하던 \x1bCA마쓰다이라 모토야스\x1bCZ에게도 전해졌다.",
    4941: "\x1bCA요시모토\x1bCZ 님이 \x1bCB오다군\x1bCZ에게 죽었다고?\n설마…… 거짓 정보겠지?",
    4942: "아닙니다…… 진중에서 농담을 하지는 않습니다.\n아무래도 사실인 듯합니다.",
    4943: "하지만 쉽게 믿을 수 없다.\n적의 몇 배나 되는 병력을 거느리고도…… 전사하다니!\n적이 흘린 거짓 정보가 아니냐?",
    4944: "틀림없습니다. 주군의 외숙인\n\x1bCA미즈노 노부모토\x1bCZ 님과 어머님 \x1bCA오다이\x1bCZ 님에게서도\n소식이 들어왔습니다.",
    4945: "뭐라고? 어머님에게서도!?",
    4946: "예.",
    4947: "그렇다면 거짓일 리가 없겠군.",
    4948: "……끝장이군.\n우리는 이제 어찌해야 하는가……",
    4949: "어서 물러납시다.\n\x1bCB오다군\x1bCZ이 추격해 오기 전에,\n먼저 \x1bCC오카자키\x1bCZ의 \x1bCC다이주지\x1bCZ로 가시지요!",
    4950: "……으, 음.",
    4951: "\x1bCA모토야스\x1bCZ는 몇 안 되는 가신과 함께,\n\x1bCB마쓰다이라 가문\x1bCZ의 보리사인 \x1bCC다이주지\x1bCZ로 달아났다.",
    4952: "여기까지 왔으면 안심입니다.\n목숨을 건졌군요.\n저는 주변을 살펴보고 오겠습니다.",
    4953: "목숨을 건졌나…… 지금까지는 그렇지.\n하지만 앞으로 어찌해야 하나……",
    4954: "내게 남은 것은\n얼마 안 되는 병사뿐. 이것으로 무엇을 할 수 있지!?\n머지않아 \x1bCB오다\x1bCZ에게 짓밟힐 것이다.",
    4955: "차라리,\n여기서 할복해 버리겠다!",
    4956: "진정하십시오, \x1bCA[bm1871]\x1bCZ 님.",
    4957: "다, 당신은…… \x1bCA쇼닌\x1bCZ 님.",
    4958: "\x1bCA[bm1871]\x1bCZ 님, 헛되이 목숨을 버리지 마십시오.\n바로 지금, 이곳에서 당신만이 할 수 있는 일이\n생겨났기 때문입니다.",
    4959: "나만이 할 수 있는 일……?",
    4960: "당신은 본래 \x1bCB[bs1871]\x1bCZ의 당주…… \x1bCB이마가와 가문\x1bCZ의\n인질이 아닙니다. \x1bCA요시모토\x1bCZ 님의 죽음으로 \x1bCB[bm1871]\x1bCZ은\n\x1bCB이마가와 가문\x1bCZ의 굴레에서 풀려났습니다.",
    4961: "\x1bCA요시모토\x1bCZ 님의 후계자 \x1bCA우지자네\x1bCZ 님은 삼국 태수의\n그릇이 아닙니다. \x1bCA모토야스\x1bCZ 님이 \x1bCB미카와 무리\x1bCZ를 이끌고,\n\x1bCB이마가와\x1bCZ 지배에서 벗어나 독립할 때입니다……",
    4962: "그런 엄청난 일을,\n내, 내가 할 수는 없어……",
    4963: "엄청나도 괜찮습니다.\n\x1bCC미카와\x1bCZ 백성도, \x1bCB[bs1871]\x1bCZ의 가신들도,\n\x1bCA[bn1871]\x1bCZ 님께 그것을 바라고 있습니다.",
    4964: "망설여도 괜찮습니다.\n하지만 망설일 때는 먼 곳을 바라보십시오.\n그러면 미혹을 끊고 나아갈 수 있을 것입니다.",
    4965: "염리예토, 흔구정토.\n더러운 땅을 떠나 정토를 구한다는 뜻입니다.",
    4966: "\x1bCA[bm1871]\x1bCZ 님, 난세의 더러움을 씻어 내고,\n이 세상을 정토처럼 평안하게 만드는 날을 꿈꾸며,\n그 이상을 내걸고 먼 길을 걸으십시오.",
    4967: "…………",
    4968: "주, 주군!\n좋은 소식입니다!",
    4969: "무슨 일이냐?",
    4970: "\x1bCC오카자키성\x1bCZ이 비었습니다.\n\x1bCA요시모토\x1bCZ가 죽었다는 소식에 \x1bCB이마가와\x1bCZ 성대들이\n모두 \x1bCC스루가\x1bCZ로 달아났습니다!",
    4971: "\x1bCC오카자키\x1bCZ가……\n우리 성이 지금 텅 비었다는 말이냐!",
    4972: "운이 트였습니다!\n이제 우리 성 \x1bCC오카자키\x1bCZ로 돌아가시지요!",
    4973: "으, 음.\n그래…… \x1bCC오카자키\x1bCZ로 돌아가자!",
    4974: "\x1bCC오카자키성\x1bCZ으로 돌아온 \x1bCA모토야스\x1bCZ는 \x1bCB이마가와 가문\x1bCZ에서\n독립해, 센고쿠 다이묘 \x1bCB마쓰다이라 가문\x1bCZ의\n당주로서 난세의 무대에 나섰다.",
    4975: "염리예토　흔구정토",
    4976: "\x1bCA도요 쇼닌\x1bCZ의 이 가르침은 \x1bCA모토야스\x1bCZ의 깃발 문구가 되어,\n\x1bCB마쓰다이라군\x1bCZ이 있는 곳에는 반드시\n그 깃발이 나부끼게 되었다.",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    4854: ["mitsubyoshi_dance_title_requires_glossary_review"],
    4866: ["tsurusaki_odori_name_requires_glossary_review"],
    4872: ["akitsura_to_dosetsu_name_change_requires_historical_review"],
    4873: ["dosetsu_dharma_name_etymology_requires_historical_review"],
    4876: ["negorozu_and_miyoshi_jikkyu_terms_require_glossary_review"],
    4896: ["takeda_nobu_generational_character_requires_glossary_review"],
    4897: ["suwa_yori_generational_character_requires_glossary_review"],
    4912: ["kihee_masayuki_and_muto_adoption_require_historical_review"],
    4913: ["hyori_hikyo_epithet_requires_glossary_review"],
    4917: ["takamoto_poisoning_context_requires_historical_review"],
    4919: ["kotsurumaru_childhood_name_requires_glossary_review"],
    4930: ["memorial_battle_wording_requires_style_review"],
    4957: ["shonin_title_requires_glossary_review"],
    4965: ["onriedo_gongujodo_korean_rendering_requires_glossary_review"],
    4976: ["toyo_shonin_name_requires_glossary_review"],
}

PREVIOUS_ARTIFACT_PINS = {
    **shared.PREVIOUS_ARTIFACT_PINS,
    "evidence/alignment_evidence.v0.14.json": (
        "BA0DD48874CF1C1ABB76080412FE8C3B696F9B24EAAC6EA1525E3DD253D4E387"
    ),
    "public/msgev_ko_historical_events_4691_4838.v0.14.json": (
        "55C711208DE0A3039FC609EE38D4EF7DC0C63785DA950A4960051745CEF05EFA"
    ),
    "review/review_index.v0.14.json": (
        "5D3A42032FA982DC7B2418E3972F6283B26E97732E4498842C0F78DE22CC0F5E"
    ),
    "validation.v0.14.json": (
        "A1AFBFAF519B28DF2CFA0398544E0E2CC01C02CFBE802F887A011E8A3167752B"
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
        raise ValueError("batch15 ids are not the exact 138 displayed entries")
    return ids


def event_for(entry_id: int) -> str:
    matches = [
        event["event_id"]
        for event in EVENTS
        if event["start_id"] <= entry_id <= event["end_id"]
    ]
    if len(matches) != 1:
        raise ValueError(f"id {entry_id} does not map to one batch15 event group")
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
        4838,
        4839,
        4873,
        4874,
        4887,
        4888,
        4910,
        4911,
        4914,
        4915,
        4939,
        4940,
        4976,
        4977,
    )
    evidence["schema"] = "nobu16.kr.event-dialogue-alignment-evidence.v15"
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
    review["schema"] = "nobu16.kr.event-dialogue-review-index.v15"
    validation["schema"] = "nobu16.kr.event-dialogue-generation-validation.v15"
    validation["font_integration"].pop(
        "current_font_or_installer_must_not_include_batch14", None
    )
    validation["font_integration"][
        "current_font_or_installer_must_not_include_batch15"
    ] = True
    integrity = validation["preexisting_integrity"]
    integrity["dialogue_v01_v14_artifacts_before"] = integrity.pop(
        "dialogue_v01_v13_artifacts_before"
    )
    integrity["dialogue_v01_v14_artifacts_after"] = integrity.pop(
        "dialogue_v01_v13_artifacts_after"
    )
    safety = validation["safety"]
    safety.pop(
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_artifacts_modified",
        None,
    )
    safety[
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_v14_artifacts_modified"
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
