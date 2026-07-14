#!/usr/bin/env python3
"""Build source-free Korean historical event dialogue batch17 (5109-5237)."""

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
import build_event_dialogue_batch16 as shared  # noqa: E402


BATCH_ID = "msgev_historical_events_5109_5237.v0.17"
OVERLAY_NAME = "msgev_ko_historical_events_5109_5237.v0.17.json"
EVIDENCE_NAME = "alignment_evidence.v0.17.json"
REVIEW_NAME = "review_index.v0.17.json"
VALIDATION_NAME = "validation.v0.17.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 5109
SCOPE_END = 5237
EXCLUDED_INTERNAL_IDS: tuple[int, ...] = ()
BRACKET_TOKEN_RE = shared.BRACKET_TOKEN_RE

EVENTS = (
    {
        "event_id": "hirayu_hot_spring_white_monkey",
        "title_ko": "흰 원숭이와 히라유 온천",
        "start_id": 5109,
        "end_id": 5136,
        "selected_count": 28,
    },
    {
        "event_id": "takenaka_hanbei_seizes_inabayama",
        "title_ko": "다케나카 한베에의 이나바야마성 탈취",
        "start_id": 5137,
        "end_id": 5160,
        "selected_count": 24,
    },
    {
        "event_id": "yoshihime_marries_date_terumune",
        "title_ko": "요시히메와 다테 데루무네의 혼인",
        "start_id": 5161,
        "end_id": 5183,
        "selected_count": 23,
    },
    {
        "event_id": "death_of_nagao_masakage_and_usami_sadamitsu",
        "title_ko": "나가오 마사카게와 우사미 사다미츠의 죽음",
        "start_id": 5184,
        "end_id": 5217,
        "selected_count": 34,
    },
    {
        "event_id": "death_of_miyoshi_nagayoshi",
        "title_ko": "미요시 나가요시의 죽음",
        "start_id": 5218,
        "end_id": 5237,
        "selected_count": 20,
    },
)

TRANSLATIONS: dict[int, str] = {
    5109: "\x1bCA[b588]\x1bCZ가 이끄는 \x1bCB다케다군\x1bCZ이 \x1bCC히다\x1bCZ로 쳐들어갔다――",
    5110: "정예를 자랑하는 고슈 병사들조차,\n\x1bCC히다\x1bCZ의 험준한 산길에 고전하고 있었다.",
    5111: "주, 주군……\n더는…… 더는 걸을…… 수 없습니다……",
    5112: "큭……\n약한 소리 하지 마라!\n그러고도 \x1bCB다케다\x1bCZ의 이름을 짊어질 셈이냐!",
    5113: "하지만 주군……\n어째서인지 힘이 들어가지 않습니다……",
    5114: "음, 듣고 보니,\n이 기이한 독기……",
    5115: "이건…… 독안개다!",
    5116: "그, 그런가!\n그래서……",
    5117: "무, 무념…… 이런 일로……",
    5118: "강행군의 피로 탓인지,\n유황 가스가 뿜어져 나오는 곳에 들어선 \x1bCB다케다군\x1bCZ 병사들은\n한 명씩 차례로 쓰러졌다.",
    5119: "(큭…… 눈앞이 흐려진다……\n　전장에서는 적수가 없다던 내가……\n　이토록 꼴사납게……)",
    5120: "(여기서 죽는 것인가……\n　주군께서 천하를 얻는 모습도 못 보고……\n　전장도 아닌 이런 곳에서……)",
    5121: "…………",
    5122: "(뭐지…… 원숭이……?\n　이런 곳에……)",
    5123: "\x1bCA겐시로\x1bCZ여,\n이런 곳에서 죽을 셈이냐?\n나는 이제 \x1bCC교토\x1bCZ로 올라갈 참인데 말이다.",
    5124: "주, 주군!?",
    5125: "헉……!\n여, 여기는……",
    5126: "끼끼!\n우끼!!",
    5127: "역시…… 원숭이잖아.",
    5128: "끼끼끼!\n우끼끼!!!",
    5129: "……뭐지?\n따라오라는 것이냐?",
    5130: "\x1bCA[bm588]\x1bCZ 일행은 흰 원숭이를 따라,\n깊은 산속에 숨은 온천에 다다랐다.",
    5131: "오오, 이건……\n온천이 아닌가!\n살았다……",
    5132: "우끼끼!",
    5133: "저것은……\n부처님의 사자였던가.",
    5134: "참으로 감사한 일이로다……\n주군, \x1bCA겐시로\x1bCZ는 살아서 가이로 돌아가겠습니다!",
    5135: "피로와 독안개에 쓰러진 \x1bCB다케다군\x1bCZ 병사들도,\n온천에 몸을 담그자 빠르게 소생해,\n행군을 계속할 기운을 되찾았다고 한다.",
    5136: "일설에는,\n\x1bCA[b588]\x1bCZ가 발견한 이 온천이\n오늘날 \x1bCC기후현 다카야마시\x1bCZ의 \x1bCC히라유 온천\x1bCZ이라고 한다.",
    5137: "\x1bCC미노국\x1bCZ·\x1bCC이나바야마성\x1bCZ―― 이 이름난 성은,\n\x1bCA사이토 도산\x1bCZ이 본거지로 삼은 뒤 아들 \x1bCA요시타쓰\x1bCZ와\n손자 \x1bCA다쓰오키\x1bCZ가 대대로 거성으로 삼았다.",
    5138: "하지만 \x1bCA다쓰오키\x1bCZ는 아직 젊어, 가신과 고쿠진을\n하나로 묶을 힘이 없었고,",
    5139: "자신감이 없는 탓에 주색에 빠지는\n악순환에 빠져 있었다.",
    5140: "\x1bCA다쓰오키\x1bCZ 님의 향락은 참으로 곤란하군.\n이래서는 \x1bCB미노 고쿠진\x1bCZ에게\n본보기가 서지 않아……",
    5141: "말씀대로입니다, 장인어른.\n이대로라면 \x1bCC미노\x1bCZ 한 구니가 쇠퇴하여,\n주변 다이묘의 침공을 받을 것입니다……",
    5142: "위태로운 것은 분명하네. 다행히 \x1bCC이나바야마성\x1bCZ은\n견고하니, 그리 쉽게 공격해 올 자는\n없으리라 생각하네만……",
    5143: "\x1bCC이나바야마성\x1bCZ이 견고하다고요?\n저는 꼭 그렇다고 생각하지 않습니다……",
    5144: "험준한 \x1bCC긴카산\x1bCZ 정상에 있어 주변 평지를 한눈에\n내려다볼 수 있지. 어떤 적이 쳐들어와도,\n쉽게 함락되지는 않을 텐데……?",
    5145: "그것도 우리 가신들이 받쳐 주기 때문입니다……\n그 전제가 없다면, 저 성을 빼앗는 일은\n그리 어렵지 않을 것입니다.",
    5146: "사위, 아무리 네 군략이 뛰어나다 해도,\n그건 불가능하다.\n함부로 큰소리해서는 안 되네……?",
    5147: "아닙니다, 허언이 아닙니다.\n의심스러우시면 지금 당장 공략해\n보여 드릴까요?",
    5148: "바, 바보 같은 소리 마라!\n주군의 성을 공략하다니……!",
    5149: "아닙니다. \x1bCA다쓰오키\x1bCZ 님께 따끔히 가르칠 기회입니다.\n음…… 부하는 십여 명이면 충분합니다.\n장인어른도 구경 삼아 함께 가시지요. 갑시다!",
    5150: "어, 어이! \x1bCA한베에\x1bCZ!\n내 말 좀 들어라……!",
    5151: "\x1bCA모리나리\x1bCZ는 제 눈을 의심했다. 사위 \x1bCA한베에\x1bCZ는\n선언대로 부하들에게 정확히 지시를 내린 뒤,\n몰래 \x1bCC이나바야마\x1bCZ성 안으로 잠입해……",
    5152: "성 안 곳곳을 눈부시게 제압했다. 주군\n\x1bCA사이토 다쓰오키\x1bCZ까지 유폐하고, 불과 열여섯 명으로\n순식간에 \x1bCC이나바야마성\x1bCZ을 함락한 것이다.",
    5153: "이럴 수가……\n정말 십여 명으로 성을 함락했어!\n믿음직하면서도 두려운 군략이로군.",
    5154: "젊은 \x1bCA다케나카 한베에\x1bCZ가 불과 적은 병력으로\n난공불락의 \x1bCC이나바야마성\x1bCZ을 제압했다는 소식에,\n이웃 구니의 다이묘들도 놀라 관심을 보였다.",
    5155: "아버지 대부터 \x1bCB사이토 가문\x1bCZ에 골머리를 앓던\n\x1bCA오다 노부나가\x1bCZ는 \x1bCC미노 반국\x1bCZ과 맞바꾸어 성과 함께\n\x1bCA한베에\x1bCZ를 고용하고 싶다고 제안했지만……",
    5156: "주군의 난행을 간했을 뿐이라며 거절한 뒤,\n\x1bCA한베에\x1bCZ는 선뜻 성을 \x1bCA다쓰오키\x1bCZ에게 돌려주고,\n스스로 근신하며 영지에 틀어박혔다.",
    5157: "행동은 대담했지만, \x1bCA한베에\x1bCZ도 주군에게\n굴욕을 안긴 일을 깊이 반성하고\n있는 모양이군……",
    5158: "하지만 정작 \x1bCA다쓰오키\x1bCZ 님은 성을 빼앗긴 분노 탓에,\n주색에 더욱 빠져들고 말았으니,\n\x1bCA한베에\x1bCZ도 예상하지 못했겠지……",
    5159: "이런……\n가신도 가신이라면,\n주군도 주군인가……",
    5160: "이나바야마성 소동은 \x1bCA사이토 다쓰오키\x1bCZ의 불만만 남긴 채\n막을 내렸다. 보기 드문 군재를 드러낸\n\x1bCA한베에\x1bCZ의 이름만 높이면서……",
    5161: "\x1bCC오슈\x1bCZ 전역을 휩쓴 대란, 덴분의 난.",
    5162: "\x1bCC오우\x1bCZ 최대 세력이던\n\x1bCB다테 가문\x1bCZ 당주 \x1bCA다네무네\x1bCZ와\n그 적자 \x1bCA하루무네\x1bCZ 사이의 내분이었다.",
    5163: "\x1bCB다테 가문\x1bCZ의 지배를 받던 \x1bCC오우\x1bCZ의 여러 다이묘는\n이를 계기로 대거 독립하여,\n자신들의 세력을 넓혔다.",
    5164: "\x1bCB모가미 가문\x1bCZ도 그런 다이묘 가문 중 하나였다.\n덴분의 난에서는 승리한 \x1bCA하루무네\x1bCZ 편에 섰지만,\n\x1bCB다테 가문\x1bCZ과의 관계는 단순하지 않았다.",
    5165: "내분이 끊이지 않는 \x1bCC오우\x1bCZ에서,\n조금이라도 외적을 줄이려던 두 가문은\n혼인 관계를 맺기로 했다.",
    5166: "\x1bCA모가미 요시모리\x1bCZ의 딸 \x1bCA요시히메\x1bCZ가,\n\x1bCA다테 하루무네\x1bCZ의 후계자 \x1bCA데루무네\x1bCZ에게 시집가게 되었다.",
    5167: "내 동생아!\n마침내 이런 날이 오고 말았구나……",
    5168: "예, 이것도 난세의 이치겠지요.\n이제 저는 \x1bCB다테 가문\x1bCZ으로 갑니다.",
    5169: "그런가……",
    5170: "그리 슬퍼하지 않으셔도 됩니다.\n제가 \x1bCB모가미 가문\x1bCZ의 여자라는 사실을\n잊을 리 없으니까요.",
    5171: "결코 \x1bCB모가미 가문\x1bCZ에 손대게 하지 않겠습니다.\n오라버니는 걱정하지 마시고,\n\x1bCB모가미 가문\x1bCZ을 번성시켜 주십시오.",
    5172: "그런가…… 그런가……",
    5173: "하아……\n오라버니는 \x1bCB모가미 가문\x1bCZ의 적자이십니다.\n이런 사소한 일로 고민하지 마십시오.",
    5174: "사소한 일이라니……!\n그렇지만 이제 좀처럼 만나지 못할 텐데.\n뭐, 고민해도 어쩔 수 없지만……",
    5175: "고민해도 어쩔 수 없는 일……\n고민해도 어쩔 수 없는 일…… 좋아!",
    5176: "부탁한다, 동생아.\n\x1bCB모가미 가문\x1bCZ과 \x1bCB다테 가문\x1bCZ의 화목을 지켜 다오.",
    5177: "예, 맡겨 주십시오.",
    5178: "편지를 보내마!\n몸조심해야 한다!\n무슨 일이 생기면 당장 돌아와야 한다!",
    5179: "예……",
    5180: "(겉보기와 달리,\n　오라버니도 여린 구석이 있군요……)",
    5181: "\x1bCA요시아키\x1bCZ는 동생 \x1bCA요시히메\x1bCZ를 몹시 아꼈고,\n본래 편지 쓰기를 좋아했는지, 수많은 편지를\n시집간 동생에게 보냈다.",
    5182: "어쨌든,\n그리하여 \x1bCB다테 가문\x1bCZ과 \x1bCB모가미 가문\x1bCZ은 혼인으로 맺어졌고,\n이 혼인은 \x1bCC오슈\x1bCZ의 운명을 크게 바꾸게 된다.",
    5183: "독안룡 \x1bCA다테 마사무네\x1bCZ.\n\x1bCA데루무네\x1bCZ와 \x1bCA요시히메\x1bCZ 사이에 태어날 이 영웅이,\n훗날 \x1bCC오슈\x1bCZ를 거세게 뒤흔들게 된다.",
    5184: "\x1bCA나가오 마사카게\x1bCZ는 \x1bCA[bm1448]\x1bCZ의 먼 친척으로,\n\x1bCA[bm1448]\x1bCZ의 누이 \x1bCA센토인\x1bCZ을 아내로 둔\n일문중의 실력자였다.",
    5185: "그의 부친 \x1bCA후사나가\x1bCZ는 \x1bCA[bm1448]\x1bCZ의 아버지\n\x1bCA다메카게\x1bCZ와 적대했고, 그도 \x1bCA[bm1448]\x1bCZ와 맞섰지만,\n둘 다 용서받아 가신이 되었다.",
    5186: "일문을 이끄는 통솔력은 확실했지만,\n그 반골 기질을 불안하게 여기는 자도\n적지 않았다.",
    5187: "\x1bCC노지리호\x1bCZ 인근·\x1bCA우사미 사다미츠\x1bCZ의 저택――",
    5188: "\x1bCA마사카게\x1bCZ는,\n\x1bCA우사미 사다미츠\x1bCZ가 연 연회에 초대받았다.",
    5189: "\x1bCA마사카게\x1bCZ 공,\n연회는 즐거우십니까?",
    5190: "\x1bCA우사미\x1bCZ 공,\n이런 연회에 초대해 주시니,\n참으로 감사할 따름입니다.",
    5191: "별말씀을.\n\x1bCB[bs1448]\x1bCZ의 주춧돌인 \x1bCA마사카게\x1bCZ 공이 안 계시면,\n시작할 연회도 시작하지 못하지요.",
    5192: "게다가,\n들려 드리고 싶은 이야기도 있습니다……",
    5193: "……오?\n무슨 이야기입니까?",
    5194: "호수에서 뱃놀이를 즐기면서,\n느긋하게 이야기하지 않으시겠습니까?",
    5195: "\x1bCA마사카게\x1bCZ는 \x1bCA사다미츠\x1bCZ의 권유를 따라,\n\x1bCC노지리호\x1bCZ 물가를 걷기 시작했다.",
    5196: "\x1bCA마사카게\x1bCZ 공.\n\x1bCB[bs1448]\x1bCZ 가문은 이대로는 버티지 못합니다.",
    5197: "…………",
    5198: "\x1bCA[bm1448]\x1bCZ 님은 분명 전쟁에 강하십니다.\n하지만 지나치게 많은 적을 만드십니다.",
    5199: "\x1bCA다메카게\x1bCZ 님 때와 아무것도 달라지지 않았습니다.\n너무 많은 적에게 둘러싸여,\n움직이지도 못하게 될 것입니다.",
    5200: "\x1bCC에치고\x1bCZ가 다시 전쟁이 끊이지 않는 수라장이 된다……\n그대의 주장도 일리는 있소만……",
    5201: "만약 지금 \x1bCA[bm1448]\x1bCZ 님께 무슨 일이 생긴다면,\n\x1bCB[bs1448]\x1bCZ을 하나로 묶을 사람은\n\x1bCA마사카게\x1bCZ 공밖에 없습니다.",
    5202: "함부로 그런 말씀 마시오……\n오, 이곳은?",
    5203: "……호수에 도착한 모양이군요.\n자, 먼저 타시지요.",
    5204: "하지만 뱃놀이를 떠난 두 사람은,\n두 번 다시 돌아오지 못했다.",
    5205: "호수 한가운데에서 배가 가라앉았고, 이튿날 아침\n\x1bCA나가오 마사카게\x1bCZ와 \x1bCA우사미 사다미츠\x1bCZ 두 사람의 시신이\n물 위에 떠오른 채 발견되었기 때문이다.",
    5206: "\x1bCA마사카게\x1bCZ의 시신에는 칼자국이 있었다고도 한다.\n\x1bCA사다미츠\x1bCZ가 목숨을 걸고 주가의 불안을 없앴다는\n소문도 돌았지만, 진상은 알 수 없다.",
    5207: "\x1bCB[bs1448] 가문\x1bCZ·\x1bCA[b1448]\x1bCZ의 거성",
    5208: "아아, 어째서 이런 일이……",
    5209: "언니, 무슨 말씀을 드려야 할지 모르겠습니다.",
    5210: "저는 소문을 믿지 않습니다. \x1bCA우사미\x1bCZ 공이 남편에게\n해칠 마음을 품었다고도 생각하지 않아요……\n하지만 두 분이 돌아가신 것은 사실이지요……",
    5211: "정말 다정하고…… 멋진 남편이었습니다.\n이제 그이의 명복을 빌며,\n조용히 살아가려고 합니다.",
    5212: "언니……",
    5213: "다만 한 가지 마음에 걸리는 것은 \x1bCA우노마쓰\x1bCZ입니다.\n그 어린 나이에 아버지를 잃다니……",
    5214: "그 일은 제게 맡겨 주십시오.\n\x1bCA우노마쓰\x1bCZ를 제 후계자로 삼아,\n반드시 명장으로 키우겠습니다.",
    5215: "\x1bCA나가오 마사카게\x1bCZ와 \x1bCA센토인\x1bCZ 부부의 아들 \x1bCA우노마쓰\x1bCZ는,\n\x1bCA[bm1448]\x1bCZ의 양자로 거두어졌다.",
    5216: "훗날 \x1bCB나가오 가문\x1bCZ을 이은 \x1bCA우노마쓰\x1bCZ는 \x1bCA아키카게\x1bCZ로 개명하고,\n다시 \x1bCA우에스기 가게카쓰\x1bCZ라 칭하게 된다.",
    5217: "훗날 \x1bCA가게카쓰\x1bCZ와 그를 둘러싼 \x1bCB우에스기 가문\x1bCZ의 동란.\n그 운명의 수레바퀴가 지금 움직이기 시작했다.",
    5218: "\x1bCB호소카와\x1bCZ 가신의 자리에서 주군을 뛰어넘고,\n\x1bCC기나이\x1bCZ에 쇼군마저 능가하는 세력을 세운 \x1bCA미요시 나가요시\x1bCZ.\n어떤 서양인은 그를 ‘일본의 부왕’이라 불렀다.",
    5219: "그 \x1bCA나가요시\x1bCZ를 받친 동생들――\n‘오니’라 불린 맹장 \x1bCA소고 가즈마사\x1bCZ와,\n다인으로도 이름난 \x1bCA미요시 짓큐\x1bCZ는 이미 죽고 없었다.",
    5220: "남은 동생으로 \x1bCC세토우치\x1bCZ 수군을 지휘한\n\x1bCA아타기 후유야스\x1bCZ는 \x1bCA나가요시\x1bCZ의 으뜸가는 중신\n\x1bCA마쓰나가 히사히데\x1bCZ와 대립했다……",
    5221: "그 \x1bCA후유야스\x1bCZ가 설마 \x1bCA나가요시\x1bCZ에게 불려가,\n형에게 그 자리에서 자결을 강요받으리라고는\n아무도 예상하지 못했을 것이다.",
    5222: "\x1bCA히사히데\x1bCZ, 내 판단이 옳았던가……?\n이제 동생들은…… 아무도 남지 않았구나.\n나를 받칠 이는…… 너밖에 없다.",
    5223: "주군의 결단, 참으로 훌륭했습니다.\n이제 후계자를 위협할 존재는\n사라졌습니다…… 가문은 평안할 것입니다.",
    5224: "후계자…… \x1bCA요시쓰구\x1bCZ를 말하는가?\n과연 그 그릇으로\n\x1bCB미요시 가문\x1bCZ을 지킬 수 있을까……?",
    5225: "걱정하지 마십시오.\n이 \x1bCA히사히데\x1bCZ가 힘껏 보좌하겠습니다……",
    5226: "\x1bCA나가요시\x1bCZ는 친아들 \x1bCA요시오키\x1bCZ를 먼저 떠나보낸 뒤,\n\x1bCA소고 가즈마사\x1bCZ의 아들 \x1bCA요시쓰구\x1bCZ를 양자로 맞아,\n후계자로 삼겠다고 선언했다.",
    5227: "어린 \x1bCA요시쓰구\x1bCZ의 권위를 지키려고,\n\x1bCA나가요시\x1bCZ와 \x1bCA히사히데\x1bCZ는 \x1bCA후유야스\x1bCZ가 \x1bCA요시쓰구\x1bCZ를\n위협하기 전에 \x1bCA후유야스\x1bCZ를 죽인 것이다……",
    5228: "나도 이제 오래 살지는 못하겠지……\n\x1bCA요시쓰구\x1bCZ에게 \x1bCC기나이\x1bCZ와 \x1bCC아와\x1bCZ를 지킬 그릇이 없다면,\n네가 \x1bCB미요시 가문\x1bCZ을…… 맡아라.",
    5229: "어찌 그리 약한 말씀을 하십니까!\n주군이 계셔야 \x1bCA히사히데\x1bCZ도 있습니다. \x1bCA요시쓰구\x1bCZ 님이\n훌륭한 후계자가 될 때까지 건강하십시오!",
    5230: "아니다, 내 몸은 내가 가장 잘 안다……\n……자, 말해 다오, \x1bCA히사히데\x1bCZ.\n내 손은…… 천하에…… 닿았던가……?",
    5231: "물론입니다.\n\x1bCA나가요시\x1bCZ 님이야말로 일본의 왕이셨습니다.",
    5232: "그런가…… 고맙구나……\n……그동안 고생시켰구나…… \x1bCA히사히데\x1bCZ.",
    5233: "\x1bCA나가요시\x1bCZ는 \x1bCA노부나가\x1bCZ보다 먼저 쇼군을 옹립하고,\n\x1bCC기나이\x1bCZ 전역에서 권세를 떨쳤으니, 어쩌면\n최초의 천하인이라 부를 수 있을지도 모른다.",
    5234: "하지만 동생들을 잃고,\n아들마저 먼저 보낸 그의 최후는,\n너무나 쓸쓸했다.",
    5235: "\x1bCA나가요시\x1bCZ 님은 내가 유일하게 충절을 바칠 만한\n분이셨다…… 그 \x1bCA나가요시\x1bCZ 님이 돌아가신 지금,\n나는 앞으로 어디로 가야 하는가……",
    5236: "(만약 \x1bCA요시쓰구\x1bCZ의 그릇이 모자라다면……\n　네가 \x1bCB미요시 가문\x1bCZ을…… 맡아라……)",
    5237: "이런……\n이제는 내가 앞장서서\n세상을 이끌어야 하는가?",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    5110: ["koshu_soldier_term_requires_glossary_review"],
    5115: ["poison_mist_and_sulfur_gas_wording_requires_review"],
    5136: ["hirayu_hot_spring_origin_requires_historical_review"],
    5138: ["kokujin_term_requires_glossary_review"],
    5140: ["mino_kokujin_term_requires_glossary_review"],
    5155: ["mino_half_province_offer_requires_historical_review"],
    5161: ["tenmon_revolt_name_requires_glossary_review"],
    5183: ["one_eyed_dragon_epithet_requires_glossary_review"],
    5187: ["nojiri_lake_and_usami_sadamitsu_names_require_review"],
    5206: ["masakage_usami_death_theory_requires_historical_review"],
    5213: ["unomatsu_childhood_name_requires_glossary_review"],
    5218: ["viceroy_of_japan_title_requires_glossary_review"],
    5233: ["first_tenka_bito_claim_requires_historical_review"],
}

PREVIOUS_ARTIFACT_PINS = {
    **shared.PREVIOUS_ARTIFACT_PINS,
    "evidence/alignment_evidence.v0.16.json": (
        "B2ACF15590D6F56CD649281FE56801BDC70693F7BAF2CADB71C2D9E24ECD15B5"
    ),
    "public/msgev_ko_historical_events_4977_5108.v0.16.json": (
        "2C84A767E44C53AA2C903242634B134D4FEC89A0B8897BF2E3357581E292A0EF"
    ),
    "review/review_index.v0.16.json": (
        "0B916057D9D3C538A9EFB9CC2036D63097D8A6B93BDA648E505740B64A1AACB3"
    ),
    "validation.v0.16.json": (
        "0A2F79C2CEAF7A3D494D2AC23B014BD75D3D08E0A67DA742BA0E14DC46AF2B18"
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
    if len(ids) != 129 or ids != sorted(TRANSLATIONS):
        raise ValueError("batch17 ids are not the exact 129 displayed entries")
    return ids


def event_for(entry_id: int) -> str:
    matches = [
        event["event_id"]
        for event in EVENTS
        if event["start_id"] <= entry_id <= event["end_id"]
    ]
    if len(matches) != 1:
        raise ValueError(f"id {entry_id} does not map to one batch17 event group")
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
        5108,
        5109,
        5136,
        5137,
        5160,
        5161,
        5183,
        5184,
        5217,
        5218,
        5237,
        5238,
    )
    evidence["schema"] = "nobu16.kr.event-dialogue-alignment-evidence.v17"
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
    review["schema"] = "nobu16.kr.event-dialogue-review-index.v17"
    validation["schema"] = "nobu16.kr.event-dialogue-generation-validation.v17"
    validation["font_integration"].pop(
        "current_font_or_installer_must_not_include_batch16", None
    )
    validation["font_integration"][
        "current_font_or_installer_must_not_include_batch17"
    ] = True
    integrity = validation["preexisting_integrity"]
    integrity["dialogue_v01_v16_artifacts_before"] = integrity.pop(
        "dialogue_v01_v15_artifacts_before"
    )
    integrity["dialogue_v01_v16_artifacts_after"] = integrity.pop(
        "dialogue_v01_v15_artifacts_after"
    )
    safety = validation["safety"]
    safety.pop(
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_v14_v15_artifacts_modified",
        None,
    )
    safety[
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_v14_v15_v16_artifacts_modified"
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
