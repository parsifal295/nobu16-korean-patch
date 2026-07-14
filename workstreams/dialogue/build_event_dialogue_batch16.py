#!/usr/bin/env python3
"""Build source-free Korean historical event dialogue batch16 (4977-5108)."""

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
import build_event_dialogue_batch15 as shared  # noqa: E402


BATCH_ID = "msgev_historical_events_4977_5108.v0.16"
OVERLAY_NAME = "msgev_ko_historical_events_4977_5108.v0.16.json"
EVIDENCE_NAME = "alignment_evidence.v0.16.json"
REVIEW_NAME = "review_index.v0.16.json"
VALIDATION_NAME = "validation.v0.16.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 4977
SCOPE_END = 5108
EXCLUDED_INTERNAL_IDS: tuple[int, ...] = ()
BRACKET_TOKEN_RE = shared.BRACKET_TOKEN_RE

EVENTS = (
    {
        "event_id": "yamanaka_shikanosuke_antler_helmet",
        "title_ko": "야마나카 시카노스케와 녹각 투구",
        "start_id": 4977,
        "end_id": 4991,
        "selected_count": 15,
    },
    {
        "event_id": "death_of_miyoshi_yoshioki",
        "title_ko": "미요시 요시오키의 죽음",
        "start_id": 4992,
        "end_id": 5021,
        "selected_count": 30,
    },
    {
        "event_id": "mikawa_ikko_ikki",
        "title_ko": "미카와 잇코잇키",
        "start_id": 5022,
        "end_id": 5045,
        "selected_count": 24,
    },
    {
        "event_id": "takeda_yoshinobu_incident",
        "title_ko": "다케다 요시노부 사건",
        "start_id": 5046,
        "end_id": 5077,
        "selected_count": 32,
    },
    {
        "event_id": "shingen_five_tenths_victory",
        "title_ko": "신겐의 오분승 철학",
        "start_id": 5078,
        "end_id": 5108,
        "selected_count": 31,
    },
)

TRANSLATIONS: dict[int, str] = {
    4977: "\x1bCA다카카게\x1bCZ, 저길 봐.",
    4978: "보라니……?\n무엇을 말입니까?",
    4979: "저 녹각 쓴 녀석 말이야.\n유난히 눈에 띄는 녹각 투구 말이다.",
    4980: "음, 훌륭하군요.\n그런데 실력은 어떻습니까?",
    4981: "강한 녀석이야.\n혼자서 열여섯 명인가,\n서른 명인가를 베어 넘겼다더군.",
    4982: "열여섯과 서른은 차이가 너무 큰데요……\n그럼 형님보다도 강합니까?",
    4983: "바보 같은 소리……\n힘만 보면 나보다 강할지도 모르지.\n하지만 전쟁은 힘으로만 하는 게 아니야.",
    4984: "후후……\n그렇다면 가장 강한 사람은\n아무래도 저겠군요.",
    4985: "마음대로 말해라…… 온다!",
    4986: "\x1bCA야마나카 시카노스케 유키모리\x1bCZ, 등장!\n\x1bCA모리 모토나리\x1bCZ, 네 목을 받으러 왔다!",
    4987: "너희 같은 잡병에게는 볼일 없다!",
    4988: "하지만 내 앞을 가로막는다면,\n용서하지 않겠다!",
    4989: "\x1bCA야마나카 시카노스케\x1bCZ.\n그 이름은 형에게 받은\n훌륭한 녹각 투구에서 유래했다고 한다.",
    4990: "‘체격이 장대하여,\n　갑옷을 입고 전장에 서기만 하면,\n　모두가 그 당당한 모습에 넋을 잃었다.’",
    4991: "훗날 그는,\n\x1bCC주고쿠\x1bCZ에서 모르는 이가 없을 만큼\n이름난 용장으로 성장하게 된다.",
    4992: "\x1bCA미요시 나가요시\x1bCZ의 적자 \x1bCA미요시 요시오키\x1bCZ는\n젊은 나이에 뛰어난 명성을 얻었다.",
    4993: "\x1bCA나가요시\x1bCZ가 병약해진 뒤에는,\n\x1bCA마쓰나가 히사히데\x1bCZ와 함께 각지를 누비며 공을 세워,\n\x1bCB미요시 가문\x1bCZ의 앞날도 탄탄해 보였다.",
    4994: "그러나――",
    4995: "뭐라고? 도련님이 쓰러지셨다고?",
    4996: "예, 갑작스러운 병이라고 합니다.\n지금 의원이 진찰하고 있습니다.",
    4997: "…………",
    4998: "병으로 쓰러진 \x1bCA미요시 요시오키\x1bCZ는 명의\n\x1bCA마나세 도산\x1bCZ의 치료에도 차도가 없었고,\n끝내 영면했다.",
    4999: "\x1bCB미요시 가문\x1bCZ·\x1bCA미요시 나가요시\x1bCZ의 거성――",
    5000: "이번 일은,\n두고두고 안타까울 따름입니다.",
    5001: "\x1bCA히사히데\x1bCZ여……\n돌이켜 보면 우리도 참 멀리까지 왔구나.",
    5002: "…………",
    5003: "아버지가 돌아가시고, 어린 나는\n\x1bCB미요시\x1bCZ 가문을 지키려고 필사적으로 싸웠다.",
    5004: "아와를 떠나 너를 만난 뒤에도\n계속 싸우며 수많은 적을 쓰러뜨렸다.\n하지만 비도한 짓을 했다고는 생각하지 않는다.",
    5005: "(그래, 본래 \x1bCA나가요시\x1bCZ 님은 피를 즐기지 않고,\n　자애롭고 고아한 마음을 지니신 분이다.\n　내가 평생 섬기기에 마땅한 주군이지……)",
    5006: "내게 칼을 겨눈 자,\n나를 배신하고 멸하려 한 자.\n나는 그런 자들만 쓰러뜨렸을 뿐이다.",
    5007: "그런데도……\n\x1bCA가즈마사\x1bCZ, \x1bCA짓큐\x1bCZ, \x1bCA요시오키\x1bCZ……\n모두 나를 두고 먼저 떠나 버렸구나.",
    5008: "내게 대체 무슨 죄가 있기에,\n하늘은 이토록 가혹한 벌을 내리는가!",
    5009: "전쟁 자체가 죄라면,\n난세에 태어난 것부터가\n이미 잘못이었다는 말인가!?",
    5010: "주군……",
    5011: "하아…… 이제 됐다……\n\x1bCC시코쿠\x1bCZ의 좋은 돌을 가져와 \x1bCA요시오키\x1bCZ의 묘를 만들어라.\n적어도 마음 편히 잠들게 해 주고 싶다.",
    5012: "\x1bCA요시오키\x1bCZ의 묘는 \x1bCC시코쿠\x1bCZ에서 가져온\n단단한 자연석으로 만들었는데,\n두드리면 맑고 높은 소리가 울려서",
    5013: "‘미요시 간간석’이라 불렸고,\n지금도 많은 이가 찾는 명소가 되었다.",
    5014: "\x1bCA히사히데\x1bCZ, 나는 조금 지쳤다.\n당분간 가문의 일은 네게 맡기마.",
    5015: "주군, 잠시 기다려 주십시오.\n쉬러 가시기 전에,\n한 가지 아뢰고 싶은 일이 있습니다.",
    5016: "무엇이냐?\n말해 보아라.",
    5017: "이런 때에,\n참으로 말씀드리기 어렵습니다만……",
    5018: "(도련님이 돌아가신 이제,\n　\x1bCA나가요시\x1bCZ 님마저 세상을 떠나시면,\n　\x1bCB미요시\x1bCZ에 내가 지킬 사람은 아무도 없다)　",
    5019: "(그렇다면 이 가문을 내 것으로 삼아,\n　내 뜻대로 바꾸고 이끌어 가리라.\n　그것이 나만의 \x1bCB미요시\x1bCZ를 향한 충의다.)",
    5020: "후계자의 죽음으로,\n정무에 뜻을 잃는 다이묘는 결코 적지 않다.",
    5021: "\x1bCA나가요시\x1bCZ도 뛰어난 적자 \x1bCA요시오키\x1bCZ의 죽음에\n마음이 크게 꺾였고, 통제를 잃은\n\x1bCB미요시\x1bCZ 가문은 갈수록 혼란에 빠져들었다.",
    5022: "오케하자마 전투 뒤 \x1bCB오다 가문\x1bCZ과 기요스 동맹을 맺은\n\x1bCB미카와 마쓰다이라 가문\x1bCZ은 마침내 \x1bCB이마가와 가문\x1bCZ과 결별했다.",
    5023: "당주 \x1bCA마쓰다이라 모토야스\x1bCZ는 이름을 \x1bCA이에야스\x1bCZ로 바꾸고,\n\x1bCC미카와국\x1bCZ 통일을 향해 힘차게 나아갔다.",
    5024: "하지만 이를 달갑게 여기지 않는 이들이 있었다.\n바로 \x1bCC미카와\x1bCZ의 \x1bCB잇코슈\x1bCZ 신도들이었다.",
    5025: "그들은 \x1bCA이에야스\x1bCZ의 아버지 \x1bCA마쓰다이라 히로타다\x1bCZ 대부터\n슈고시 불입의 특권을 누리고 있었다.",
    5026: "그 특권을 인정하지 않는 \x1bCA이에야스\x1bCZ에게 반기를 들고,\n문도들과 함께 \x1bCA이에야스\x1bCZ를 공격하기 시작했다.",
    5027: "그중에는 ‘충절이 개와 같다’고 불린\n미카와 무사들의 모습도 있었다.",
    5028: "신앙과 충절 사이에서 고뇌한 끝에,\n가신단의 절반이 문도 편을 택했다……",
    5029: "\x1bCC미카와국\x1bCZ과 \x1bCB마쓰다이라 가문\x1bCZ은\n순식간에 삼베처럼 뒤엉켰다.",
    5030: "이때 \x1bCB잇코슈\x1bCZ 편에 선 주요 인물은,\n먼저 \x1bCA혼다 마사노부\x1bCZ와 동생 \x1bCA마사시게\x1bCZ……",
    5031: "훗날 도쿠가와 십육신장에 꼽히는\n\x1bCA와타나베 모리츠나\x1bCZ,",
    5032: "또 \x1bCA하치야 한노조\x1bCZ라는 이름으로 알려진\n\x1bCA하치야 사다쓰구\x1bCZ,",
    5033: "그 밖에도 \x1bCA나쓰메 히로쓰구\x1bCZ, \x1bCA나이토 기요나가\x1bCZ 등\n\x1bCA이에야스\x1bCZ가 의지하던 무장들이었다.",
    5034: "이럴 수가…… \x1bCC미카와\x1bCZ가 둘로 갈라졌단 말인가?",
    5035: "무슨 수를 써서라도 서둘러 수습해야 한다.\n아니면 다이묘들이 \x1bCC미카와\x1bCZ를 물어뜯을 것이다!",
    5036: "동맹을 맺은 \x1bCB오다 가문\x1bCZ조차,\n\x1bCB마쓰다이라 가문\x1bCZ을 못 미더워해\n우리를 버리는 것은 필연이다.",
    5037: "끝내겠다. 무슨 수를 써서라도.\n그러지 않으면 우리에게 미래는 없다……",
    5038: "\x1bCA이에야스\x1bCZ는 남은 가신단을 이끌고 전장에서\n\x1bCB잇코슈\x1bCZ를 무찌른 뒤 화의를 맺었다.",
    5039: "그리고 가신들에게 귀참을 권하는 한편,\n\x1bCB잇코슈\x1bCZ의 문도 조직을 해체하고……",
    5040: "사원에는 다른 종파로 개종하라고 강요하여,\n거부하는 사원은 철거하는\n엄중한 처분을 내렸다.",
    5041: "저항하는 가신도 용서하지 않고,\n칩거 또는 추방 처분을 내렸다.",
    5042: "그 뒤 오랫동안 \x1bCB잇코슈\x1bCZ에게\n\x1bCC미카와\x1bCZ는 출입 금지 지역이 되었고,\n\x1bCB마쓰다이라 가문\x1bCZ도 멸망의 위기에서 벗어났다.",
    5043: "\x1bCA이에야스\x1bCZ에게 이 사건은 다이묘가 된 뒤\n처음 맞은 위기라 할 만했으며,\n\x1bCC미카와\x1bCZ 통일을 위해……",
    5044: "종교든 가신이든 자신의 적이 된 자는\n모두 잘라 버리는,",
    5045: "냉혹한 지배자로서의 면모를\n여실히 드러낸 사건이었다……",
    5046: "\x1bCB다케다 가문\x1bCZ에 거센 충격이 일었다.",
    5047: "전대 \x1bCA노부토라\x1bCZ 때부터 섬긴 중신 \x1bCA오부 도라마사\x1bCZ가\n모반을 꾀했다는 이유로 자결을 명받고,",
    5048: "마찬가지로 모반의 주모자라 지목된\n\x1bCA신겐\x1bCZ의 적자 \x1bCA요시노부\x1bCZ도 구금된 것이다.",
    5049: "무슨 변명이라도 있느냐?",
    5050: "변명은 없습니다.\n하지만 드릴 말씀은 있습니다!",
    5051: "아버님,\n\x1bCB이마가와\x1bCZ는 제 아내의 집안이자 선대부터 이어진 맹우입니다.",
    5052: "그 \x1bCB이마가와\x1bCZ가 곤경에 빠졌는데도 외면하고,\n도움의 손길은커녕\n그 틈을 타 공격하려 하시다니……",
    5053: "이는 무사의 길이 아닙니다!\n\x1bCB다케다\x1bCZ의 가문명이 땅에 떨어질 것입니다!",
    5054: "\x1bCA요시노부\x1bCZ.\n너는 그런 말밖에 하지 못하느냐?\n그것이 얼마나 하찮고 좁은지도 모르느냐.",
    5055: "알고 싶지도 않습니다.\n\x1bCA[b1448]\x1bCZ 공이라면,\n결코 이를 하찮다고 하지 않으셨을 겁니다.",
    5056: "의에 빠져 의를 위해 죽는 것도 좋겠지.\n하지만 네가 품은 것은 의가 아니다.",
    5057: "남이 불어넣은 거짓된 의에 취하고,\n주변의 부추김에 들떠서는,\n각오도 없이 고통에서 달아나려 할 뿐이다.",
    5058: "모든 사욕을 끊고 대가를 바라지 않으며,\n살을 에는 듯한 고통 속에서도 대의를 내걸고 싸우는\n\x1bCA[bm1448]\x1bCZ의 발끝에도 미치지 못한다.",
    5059: "고통을 모르는 어리석은 놈……\n어리석은…… 어리석은 내 아들아……\n누가 이자를 끌고 가라!",
    5060: "아버님!\n그 악행에는 반드시 대가가 따를 것입니다!\n인과가 돌아 \x1bCB다케다 가문\x1bCZ에 닥칠 것입니다!",
    5061: "인과는 돌고 돈다, 인가……",
    5062: "……주군.",
    5063: "\x1bCA요시노부\x1bCZ가 그토록 어리석어진 것은 내 허물이다.\n네 형까지 휘말리게 해 미안하구나.",
    5064: "결코 그렇지 않습니다.\n형님의 고통을 알아채지 못한 것은\n제 불찰이었습니다.",
    5065: "\x1bCA겐시로\x1bCZ, 적비 부대는 네가 이어라.\n역적 \x1bCA오부\x1bCZ의 이름은 버리고,\n끊긴 \x1bCA야마가타\x1bCZ의 이름을 이어 새로 태어나라.",
    5066: "예!",
    5067: "\x1bCA가쓰요리\x1bCZ는 있느냐?",
    5068: "여기 있습니다.",
    5069: "이제부터 네가 \x1bCB다케다 가문\x1bCZ의 후계자다.\n결코 어리석은 형처럼 되지 마라.",
    5070: "예!",
    5071: "(형님은…… 형님은 죽는다.\n　형님의 무엇이 어리석다는 건지……\n　지금의 나는 아직 알 수 없다.)",
    5072: "(하지만 아버님의 고통은 안다.\n　그리고 괴로워하는 아버님은 형님이 말한\n　악인으로는 도저히 보이지 않는다……)",
    5073: "(고통을 모르는 어리석은 자라……)",
    5074: "그리하여,\n\x1bCA다케다 요시노부\x1bCZ는 \x1bCC도코지\x1bCZ에 유폐된 채 죽었다.",
    5075: "\x1bCA오부 도라마사\x1bCZ를 비롯해,\n\x1bCB다케다\x1bCZ 가문의 친\x1bCB이마가와\x1bCZ파는 거의 숙청되었다.",
    5076: "외교 방침을 바꾼 \x1bCB다케다 가문\x1bCZ은\n\x1bCC스루가\x1bCZ 병합을 목표로 군대를 남쪽으로 돌렸고,",
    5077: "\x1bCA다케다 요시노부\x1bCZ를 대신할 \x1bCB다케다 가문\x1bCZ의 후계자로\n넷째 아들 \x1bCA가쓰요리\x1bCZ가 지명되었다.",
    5078: "\x1bCB다케다 가문\x1bCZ·\x1bCC쓰쓰지가사키관\x1bCZ――",
    5079: "\x1bCA마사유키\x1bCZ, 네게 하나 묻겠다.",
    5080: "예, 무엇을 물으시겠습니까?",
    5081: "\x1bCC에치고\x1bCZ의 \x1bCA[bm1448]\x1bCZ가,\n나보다 못한 점이 무엇인지 아느냐?",
    5082: "(못한 점이라……\n　전쟁 실력이라 답해야 하나?\n　하지만 너무 아첨처럼 들리겠지.)",
    5083: "(그럼 무엇이지……\n　거짓말 솜씨? 아니, 이건 곤란하다.\n　욕심? 이것도 입에 담을 말이 아니야.)",
    5084: "후후……\n고민하는 모양이구나.",
    5085: "\x1bCA[bm1448]\x1bCZ가 나보다 못한 점이라……\n그런 것은 아예 없을지도 모르겠구나.\n모든 면에서 \x1bCA[bm1448]\x1bCZ가 나보다 나은가……",
    5086: "아닙니다……\n그것은 ‘인’이라고 생각합니다.",
    5087: "그 답의 뜻을 물어도 되겠느냐?",
    5088: "주군과 \x1bCA[bm1448]\x1bCZ 모두 백성에게 어진 명군이십니다.\n하지만 \x1bCA[bm1448]\x1bCZ는 전장에서 적에게 자비가 없고,\n가차 없이 몰아붙여 이기기를 좋아합니다.",
    5089: "주군께서는 이겨도 적을 지나치게 쫓지 않으십니다.\n싸움 뒤 적이 늘어나는 쪽은 \x1bCA[b1448]\x1bCZ이고,\n아군이 늘어나는 쪽은 주군이십니다.",
    5090: "훌륭하다. 과연 \x1bCA마사유키\x1bCZ로구나.",
    5091: "(오, 맞혔나……)",
    5092: "맞지는 않았지만, 크게 빗나가지도 않았다.",
    5093: "(정답은 아니었나?)",
    5094: "잘 들어라.\n전쟁은 오분승을 상으로 삼고,\n칠분승은 중, 십분승은 하로 삼는다.",
    5095: "적을 늘리지 않기 위해서이기도 하지만,\n무엇보다 제 마음을 다스리기 위해서다.",
    5096: "마음을 다스리기 위해서입니까?",
    5097: "그렇다.\n오분승은 다음 싸움을 향한 분발심을 낳는다.",
    5098: "하지만 칠분승은 나태함을 낳고,\n십분승에 이르면 반드시\n교만함을 낳게 되지.",
    5099: "그러므로 나는 언제나 오분승에서 멈춘다.\n십분승을 바라는 \x1bCA[bm1448]\x1bCZ는 한두 번 전쟁에서\n나를 이겨도 결코 나를 넘지는 못한다.",
    5100: "감복했습니다.",
    5101: "무슨 일이든 십분, 완벽을 바라서는 안 된다.\n사람에게도 마찬가지다.",
    5102: "백 명 중 아흔아홉에게 칭찬받는 자는\n경박하거나, 말재주꾼이거나, 도둑이거나,\n아첨꾼이지…… 좋은 사람일 리 없다.",
    5103: "사람과 세상에 십분을 바라서는 안 된다.\n십분이 없기에,\n우리는 지혜를 짜내는 것이다.",
    5104: "명심하겠습니다!",
    5105: "(과연 주군이시다.\n　주군조차 스스로 십분이 아님을 인정하신다.\n　이 또한 하나의 각오이리라……)",
    5106: "(그런 각오가 없다면,\n　난세를 헤쳐 나갈 수 없겠구나.)",
    5107: "‘무릇 싸움은 오분승을 상으로 삼고,\n　칠분승을 중, 십분승을 하로 삼는다.’",
    5108: "오늘날까지 널리 쓰이는 이 말에는,\n세상에 완벽을 바라지 않는다는\n\x1bCA[bm1251]\x1bCZ의 깊은 철학이 잘 드러나 있다.",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    4989: ["shikanosuke_name_and_antler_helmet_origin_require_review"],
    4990: ["historical_quotation_wording_requires_review"],
    4998: ["manase_dosan_name_requires_glossary_review"],
    5013: ["miyoshi_kankan_stone_name_requires_glossary_review"],
    5025: ["shugo_shi_funyu_term_requires_glossary_review"],
    5031: ["tokugawa_sixteen_protectors_term_requires_glossary_review"],
    5032: ["hachiya_hannojo_name_requires_glossary_review"],
    5041: ["chikkyo_punishment_term_requires_glossary_review"],
    5065: ["red_cavalry_and_genjiro_titles_require_glossary_review"],
    5074: ["tokoji_place_name_requires_glossary_review"],
    5094: ["five_seven_ten_victory_terms_require_style_review"],
    5107: ["historical_quotation_wording_requires_review"],
}

PREVIOUS_ARTIFACT_PINS = {
    **shared.PREVIOUS_ARTIFACT_PINS,
    "evidence/alignment_evidence.v0.15.json": (
        "4BA6A777EE108B84E8FE9723A97AF75CD6A8FDDEE9BC9B9908A24D0BAFB5DA6B"
    ),
    "public/msgev_ko_historical_events_4839_4976.v0.15.json": (
        "81568BBD13BF61F4CAE83E9F893ECA7DA723ADB76200F25D1D38011FFE3A831A"
    ),
    "review/review_index.v0.15.json": (
        "957C55863EEEBB23E0D36FCBACB2BB630E195F2A2A3039D852D97BFF4B0B1C71"
    ),
    "validation.v0.15.json": (
        "C2298D40384B680FF482DCD63B7E13BFC9FD1236FD83B434A1DBA3DAE09A0BF4"
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
    if len(ids) != 132 or ids != sorted(TRANSLATIONS):
        raise ValueError("batch16 ids are not the exact 132 displayed entries")
    return ids


def event_for(entry_id: int) -> str:
    matches = [
        event["event_id"]
        for event in EVENTS
        if event["start_id"] <= entry_id <= event["end_id"]
    ]
    if len(matches) != 1:
        raise ValueError(f"id {entry_id} does not map to one batch16 event group")
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
        4976,
        4977,
        4991,
        4992,
        5021,
        5022,
        5045,
        5046,
        5077,
        5078,
        5108,
        5109,
    )
    evidence["schema"] = "nobu16.kr.event-dialogue-alignment-evidence.v16"
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
    review["schema"] = "nobu16.kr.event-dialogue-review-index.v16"
    validation["schema"] = "nobu16.kr.event-dialogue-generation-validation.v16"
    validation["font_integration"].pop(
        "current_font_or_installer_must_not_include_batch15", None
    )
    validation["font_integration"][
        "current_font_or_installer_must_not_include_batch16"
    ] = True
    integrity = validation["preexisting_integrity"]
    integrity["dialogue_v01_v15_artifacts_before"] = integrity.pop(
        "dialogue_v01_v14_artifacts_before"
    )
    integrity["dialogue_v01_v15_artifacts_after"] = integrity.pop(
        "dialogue_v01_v14_artifacts_after"
    )
    safety = validation["safety"]
    safety.pop(
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_v14_artifacts_modified",
        None,
    )
    safety[
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_v14_v15_artifacts_modified"
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
