#!/usr/bin/env python3
"""Build source-free Korean historical event dialogue batch20 (5487-5628)."""

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
import build_event_dialogue_batch19 as shared  # noqa: E402


BATCH_ID = "msgev_historical_events_5487_5628.v0.20"
OVERLAY_NAME = "msgev_ko_historical_events_5487_5628.v0.20.json"
EVIDENCE_NAME = "alignment_evidence.v0.20.json"
REVIEW_NAME = "review_index.v0.20.json"
VALIDATION_NAME = "validation.v0.20.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 5487
SCOPE_END = 5628
EXCLUDED_INTERNAL_IDS: tuple[int, ...] = ()
BRACKET_TOKEN_RE = shared.BRACKET_TOKEN_RE

EVENTS = (
    {
        "event_id": "salt_for_the_enemy",
        "title_ko": "적에게 소금을 보내다",
        "start_id": 5487,
        "end_id": 5509,
        "selected_count": 23,
    },
    {
        "event_id": "hanbei_joins_under_hideyoshi",
        "title_ko": "다케나카 한베에의 등용",
        "start_id": 5510,
        "end_id": 5533,
        "selected_count": 24,
    },
    {
        "event_id": "nobunaga_recognizes_gamo_ujisato",
        "title_ko": "노부나가가 알아본 가모 우지사토",
        "start_id": 5534,
        "end_id": 5552,
        "selected_count": 19,
    },
    {
        "event_id": "gamo_yasuhide_silver_namazuo_helmet",
        "title_ko": "가모 야스히데의 은빛 메기꼬리 투구",
        "start_id": 5553,
        "end_id": 5574,
        "selected_count": 22,
    },
    {
        "event_id": "baba_nobuharu_burns_imagawa_treasure",
        "title_ko": "바바 노부하루가 태운 이마가와 보물",
        "start_id": 5575,
        "end_id": 5593,
        "selected_count": 19,
    },
    {
        "event_id": "baba_nobuharus_five_articles",
        "title_ko": "바바 노부하루의 오개조",
        "start_id": 5594,
        "end_id": 5628,
        "selected_count": 35,
    },
)

TRANSLATIONS: dict[int, str] = {
    5487: "\x1bCA이마가와 요시모토\x1bCZ가 죽은 지 몇 해 뒤,\n\x1bCA[b1251]\x1bCZ은 고소슨 삼국 동맹을 파기하고,\n\x1bCB이마가와 가문\x1bCZ과 적대할 뜻을 분명히 했다.",
    5488: "이에 \x1bCB이마가와 가문\x1bCZ 당주 \x1bCA우지자네\x1bCZ는\n동맹을 유지한 \x1bCA호조 우지야스\x1bCZ와 손잡고,\n\x1bCB다케다령\x1bCZ에 소금을 팔지 못하게 했다.",
    5489: "바다와 닿지 않은 \x1bCC가이\x1bCZ는 소금을 만들 수 없어,\n\x1bCB이마가와\x1bCZ와 \x1bCB호조령\x1bCZ 상인에게 크게 의존했기에,\n\x1bCB다케다\x1bCZ는 곤경에 빠졌다.",
    5490: "내가……\n방심했구나!",
    5491: "\x1bCA우지자네\x1bCZ는 그렇다 쳐도,\n\x1bCA우지야스\x1bCZ까지 이런 수를 쓰다니.\n과연 우리의 약점을 꿰뚫었구나……",
    5492: "한편 \x1bCC에치고\x1bCZ의 \x1bCA[b1448]\x1bCZ에게도\n적 \x1bCB다케다 가문\x1bCZ이 소금 부족에 시달린다는 소식이 닿았다……",
    5493: "\x1bCC가이\x1bCZ는 산악국이라 소금을 전혀 얻지 못해,\n그 \x1bCA[bm1251]\x1bCZ 입도도 고생한다 합니다.\n우리 가문에는 절호의 기회입니다!",
    5494: "절호의 기회……? 아니다!\n지금은 적이라도 \x1bCB다케다\x1bCZ를 구할 때다!",
    5495: "뭐라고……!?",
    5496: "소금길을 끊는 짓은,\n싸움으로 결판내지 못하는 비겁자나\n하는 일이다!",
    5497: "참된 무사라면 비사문천이 지켜보는 가운데,\n정정당당한 한판 승부로\n\x1bCB다케다\x1bCZ를 꺾어야 한다!",
    5498: "하아……",
    5499: "그러니 우리 영지의 소금을 정가에\n\x1bCB다케다\x1bCZ에게 팔겠다고 전하라!\n곤경을 틈타 비싸게 파는 상인은 단속하라!",
    5500: "궁하던 소금 공급에 길이 열리자,\n\x1bCA[bm1251]\x1bCZ은 일단 \x1bCA[bm1448]\x1bCZ의 온정에\n감사를 전했다……",
    5501: "결국 \x1bCA[bm1448]\x1bCZ은\n\x1bCC에치고\x1bCZ의 소금을 우리에게 파는 것이다.\n거저 주는 건 아니지……",
    5502: "지금까지 \x1bCB이마가와\x1bCZ와 \x1bCB호조령\x1bCZ의 소금에 의존한 우리가\n이제는 \x1bCC에치고\x1bCZ의 소금에\n의존하게 되도록 꾸민 듯하군……",
    5503: "그렇게 되면 다음에는,\n언제 \x1bCA[bm1448]\x1bCZ이 소금을 끊을지 모른다……\n그래도 급한 불을 끈 것은 틀림없지만.",
    5504: "그렇군……\n\x1bCA[bm1448]\x1bCZ 측은 이를\n절호의 기회로 본 것이야.",
    5505: "게다가 우리에게 소금을 보내며,\n\x1bCA[bm1448]\x1bCZ이 의로운 장수라는 명성도 커진다……\n모두 계산한 일이군.",
    5506: "소금과 함께 은혜까지 팔다니……\n겉보기와 달리 빈틈없는 사내로군.\n나도 본받아야겠어.",
    5507: "‘적에게 소금을 보내다’라는 유명한 일화는\n속담으로 널리 퍼졌고, 의로운 장수\n\x1bCA[b1448]\x1bCZ의 평가는 더욱 높아졌다.",
    5508: "한편 이 이야기는 \x1bCA[bm1448]\x1bCZ의 정의뿐 아니라,\n소금을 비싸게 팔지 않았다는 점에서\n거래의 공정함을 보인 일화로도 읽힌다.",
    5509: "\x1bCA[bm1448]\x1bCZ의 도움에 감사해,\n\x1bCA[bm1251]\x1bCZ이 답례로 보낸 칼은\n‘시오도메노타치’라 불리며 지금도 남아 있다.",
    5510: "한때 적은 병력으로 \x1bCC이나바야마성\x1bCZ을 빼앗은\n\x1bCA다케나카 한베에 시게하루\x1bCZ는 그 뒤 은거해,\n\x1bCC오미\x1bCZ에서 살았다고 전한다.",
    5511: "\x1bCA오다 노부나가\x1bCZ가 \x1bCB미노 사이토 가문\x1bCZ을 멸한 뒤에도,\n\x1bCA한베에\x1bCZ는 어디에도 출사하지 않고,\n밭을 갈고 책을 읽으며 지냈다.",
    5512: "\x1bCA한베에\x1bCZ 공,\n오늘은 좋은 답을 들을 수 없겠습니까?",
    5513: "또 오셨습니까. 참으로 끈질긴 분이군요.\n\x1bCB사이토 가문\x1bCZ이 멸망한 지금,\n저는 누구도 섬길 생각이 없습니다.",
    5514: "게다가 저는 타고난 병약한 몸이라……\n전쟁에도 도움이 되지 않을 겁니다.",
    5515: "그러지 마시고, 어떻게 좀 안 되겠습니까……",
    5516: "\x1bCB오다\x1bCZ 가신 \x1bCA[b754]\x1bCZ은 어디서 알아냈는지,\n\x1bCA한베에\x1bCZ의 은거지를 찾아내어\n끈질기게 출사를 권하고 있었다.",
    5517: "열의는 잘 알겠습니다.\n하지만 귀하의 주군 \x1bCA오다 노부나가\x1bCZ 공은\n너무 난폭한 분으로 보이는군요.",
    5518: "그렇지 않습니다.\n주군은 비천한 출신인 저를 발탁하여,\n활약할 기회를 주신 분입니다.",
    5519: "하지만 그 성정은 언젠가 적과 가신에게\n쓸데없는 원한을 사, 천하포무의 이상도\n도중에 무너지고 말 겁니다.",
    5520: "호오……\n우리 주군의 ‘천하포무’ 뜻을 알고 계십니까.\n역시 \x1bCA한베에\x1bCZ 공입니다.",
    5521: "그 목표에는 저도 크게 공감합니다.\n다만 \x1bCA노부나가\x1bCZ라는 분이 직접 이룰지는……\n위태롭다고 봅니다.",
    5522: "걱정하지 마십시오.\n주군 혼자 천하포무를 이루지 못한다면,\n우리 가신들이 받쳐 드리면 됩니다.",
    5523: "호오?",
    5524: "저만 있는 것도 아닙니다.\n\x1bCB오다\x1bCZ에는 온갖 재능을 지닌 자들이 있습니다. 모두\n주군의 사람됨에 반해 가신이 된 이들입니다.",
    5525: "그런 온갖 인재가 저마다 재능을\n살릴 수 있는 곳이 \x1bCB오다 가문\x1bCZ입니다.\n실력만 있으면 주군께서 발탁해 주십니다!",
    5526: "……흥미롭군요.\n\x1bCA노부나가\x1bCZ 공 혼자서는 불가능해도,\n여러분이 돕는다면 가능할지도 모르겠군요.",
    5527: "\x1bCA[bs754]\x1bCZ 공.\n무례한 말이나, 저는 \x1bCA오다 노부나가\x1bCZ 공보다\n귀하에게서 더 큰 미래를 봅니다.",
    5528: "예?\n아닙니다, 아닙니다. 칭찬에 익숙지 않아,\n그저 부끄러울 따름입니다만……",
    5529: "좋습니다. 저는\n오다 \x1bCA노부나가\x1bCZ 공을 섬기는 것이 아니라,\n\x1bCA[bs754]\x1bCZ 공, 귀하를 섬기겠습니다.",
    5530: "오오, 뭐라고요!\n제 아래로 와 주시겠습니까!\n정말 감사합니다!",
    5531: "(\x1bCA오다 노부나가\x1bCZ가 한 대에 천하포무를 이루지 못한다면,\n　그 뒤를 잇는 이는 반드시\n　이 \x1bCA[b754]\x1bCZ이라는 사내겠지……)",
    5532: "(그리고 그 판단을 현실로 만드는 것도,\n　이 \x1bCA한베에\x1bCZ의 수완이겠지……\n　그때까지 목숨이 붙어 있으면 좋으련만.)",
    5533: "이렇게 \x1bCA[b754]\x1bCZ의 요리키라는 형식으로\n\x1bCB오다 가문\x1bCZ을 섬긴 전설의 군사 \x1bCA다케나카 한베에\x1bCZ는,\n다시 전국의 무대에 나서게 되었다……",
    5534: "\x1bCC오미\x1bCZ 명문·\x1bCB가모 가문\x1bCZ――",
    5535: "당주 \x1bCA가모 가타히데\x1bCZ가 오다 \x1bCA노부나가\x1bCZ에게 복속하자,\n적자 \x1bCA우지사토\x1bCZ를 인질로 \x1bCA노부나가\x1bCZ에게 보냈다.",
    5536: "호오……\n네가 \x1bCB가모\x1bCZ의 아들이냐!",
    5537: "예!\n저는 \x1bCA우지사토\x1bCZ라고 합니다.",
    5538: "…………",
    5539: "…………",
    5540: "눈빛이 좋구나……\n보통 무장은 아닌 듯하다.",
    5541: "마음에 들었다!\n\x1bCA우지사토\x1bCZ, 언젠가 내 딸을 네게 주마.\n물러가도 좋다!",
    5542: "예!\n더없는 영광입니다!",
    5543: "주, 주군.\n그런 약속을 이리 가볍게 하셔도……\n……괜찮겠습니까?",
    5544: "둘째 딸이 아직 시집가지 않았지……\n그 아이를 \x1bCB가모 가문\x1bCZ의 아들에게 주겠다.",
    5545: "주군!",
    5546: "\x1bCA가쓰이에\x1bCZ로구나.\n그러고 보니 네 눈도 좋군.\n저 아이처럼 용장의 눈이다.",
    5547: "\x1bCA가쓰이에\x1bCZ, 네게도 내 딸을……\n아니, 나이 차이가 너무 큰가.\n그래, 내 누이를 주면 어떠냐?",
    5548: "노, 농담도 그만하십시오……!",
    5549: "하하하!\n\x1bCB가모\x1bCZ의 아들은 네게 맡기마.\n오니시바타 아래에서 단련시켜라!",
    5550: "예……",
    5551: "기록에 따르면 \x1bCA노부나가\x1bCZ는 \x1bCA우지사토\x1bCZ를 처음 보고,\n‘\x1bCB가모\x1bCZ의 아이는 눈빛부터 남다르다’며,\n매우 마음에 들어 했다고 한다.",
    5552: "명장은 명장을 알아보는 법.\n\x1bCA노부나가\x1bCZ의 눈은 틀리지 않았고, \x1bCA우지사토\x1bCZ는\n천하에 이름을 떨친 명장으로 성장한다……",
    5553: "\x1bCA가모 야스히데\x1bCZ의 거성――",
    5554: "이날 \x1bCA가모 야스히데\x1bCZ는\n새로 \x1bCB가모 가문\x1bCZ을 섬길 가신과 만났다.",
    5555: "오늘부터 출사하게 되었습니다.\n앞으로 잘 이끌어 주시기를 부탁드립니다.",
    5556: "그래.\n그대가 공을 세우기를 기대하겠다.",
    5557: "……그렇지.\n우리 가문에서 공을 세우는 법을 알려 주마.",
    5558: "전장에는 내 부하 중 은빛 메기꼬리 투구를 쓰고,\n늘 선진을 달리는 자가 있다.",
    5559: "그자에게 지지 않도록 활약하면,\n반드시 공을 세울 수 있을 것이다!",
    5560: "은빛 메기꼬리 투구……?",
    5561: "며칠 뒤――",
    5562: "여어, 신참!\n드디어 전투로군.",
    5563: "예, 주군께서\n은빛 메기꼬리 투구의 무사가 선진에 있으니,\n그에게 지지 말고 활약하라 하셨습니다.",
    5564: "하하하!\n주군은 모두에게 그렇게 말씀하시지.\n하지만 그건 불가능하다고 보네.",
    5565: "불가능하다니……\n어째서입니까?",
    5566: "자,\n저길 보게.",
    5567: "고참 가신이 가리킨 곳에는,\n은빛 메기꼬리 투구를 쓴\n위풍당당한 \x1bCA야스히데\x1bCZ가 있었다……",
    5568: "예……\n은빛 투구의 무사가 주군이셨습니까!?",
    5569: "그래.\n주군의 무예와 용기를 이길 자는 없지.\n우리도 따라가기 벅찰 정도야……",
    5570: "세상에……\n정말 대단한 가문을 섬기게 되었군.",
    5571: "\x1bCA가모 야스히데\x1bCZ는 늘 이렇게 말했다고 한다.",
    5572: "총대장으로 전장에 섰을 때,\n그저 ‘공격하라’고 명령만 해서는\n병사들이 움직여 주지 않는다……",
    5573: "병사들을 움직이게 하려면,\n총대장이 먼저 나아가,\n‘이리 오라’고 명해야 한다……",
    5574: "그러면 총대장을 버릴 수 없는\n병사들은,\n반드시 뒤따라온다고.",
    5575: "\x1bCA이마가와 우지자네\x1bCZ를 몰아내고 \x1bCC스루가\x1bCZ를 장악한\n\x1bCA[b1251]\x1bCZ은 \x1bCC슨푸관\x1bCZ에 남은\n\x1bCB이마가와 가문\x1bCZ의 보물에 눈독을 들였다.",
    5576: "귀족 취향인 \x1bCA요시모토\x1bCZ였으니……\n분명 값진 물건을 쌓아 두었겠지.",
    5577: "후후……\n왕도를 걸으려면 돈은 아무리 많아도 모자라지.\n누가 창고에 가서 옮겨 오너라.",
    5578: "예!",
    5579: "잠시만 기다리십시오, 주군!\n그런 걱정은 하지 않으셔도 됩니다!",
    5580: "오오, \x1bCA노부하루\x1bCZ로구나!\n벌써 옮겨 놓았느냐?\n과연 너답구나.",
    5581: "예.\n제가 먼저 \x1bCC슨푸\x1bCZ에 가서,\n보물을 모두 불태워 재로 만들었습니다!",
    5582: "뭐라고……?\n다시 말해 보겠느냐?",
    5583: "예!\n보물은 제가 전부 태웠습니다.\n걱정하지 않으셔도 됩니다!",
    5584: "…………",
    5585: "…………",
    5586: "……호오, 걱정하지 않아도 된다?",
    5587: "그렇습니다!",
    5588: "이제 주군께서 적의 보물을 빼앗는\n탐욕스러운 장수라 욕먹을 일은 없습니다.\n부디 걱정하지 마십시오!",
    5589: "그런가……",
    5590: "후, 후후후……\n보물보다 이름을 아껴야 한다는 말이로군!",
    5591: "과연 \x1bCA노부하루\x1bCZ다.\n너라면 다이묘로 삼아도 아깝지 않겠구나!",
    5592: "\x1bCA바바 노부하루\x1bCZ는 다케다 사천왕이라 불린 장수 중\n가장 연장자였고, \x1bCA[bm1251]\x1bCZ보다도 나이가 많았다.",
    5593: "그 노련한 전략과,\n언제나 냉정함을 잃지 않는 큰 그릇은\n몇 번이나 \x1bCB다케다 가문\x1bCZ을 구하게 된다……",
    5594: "\x1bCB다케다 가문\x1bCZ·\x1bCA바바 노부하루\x1bCZ 저택――",
    5595: "\x1bCA바바\x1bCZ 님!",
    5596: "음, \x1bCA유키타카\x1bCZ의 아들이로군.\n이름이 분명……?",
    5597: "저는 \x1bCA마사유키\x1bCZ라 합니다.\n오늘 \x1bCA바바\x1bCZ 님께 무사의 마음가짐을 여쭙고자,\n찾아왔습니다.",
    5598: "그런가……\n그렇다면 들려주마.",
    5599: "호오, 어떤 가르침을 들려주시려나?",
    5600: "꽤 즐거운 시간이 되겠군.",
    5601: "부디 저희도 함께 듣게 해 주십시오!",
    5602: "좋다, 애송이들아.\n모두 함께 듣거라.",
    5603: "하하…… 애송이는 아닙니다만.",
    5604: "강하고 용맹하면 공을 세우고,\n겁이 많으면 실수한다…… 당연한 일이지만,\n중요한 것은 마음가짐이다!",
    5605: "나는 젊을 때부터,\n늘 다섯 가지를 명심했다.\n그 뒤로는 실수한 적이 없지!",
    5606: "다섯 가지입니까?",
    5607: "오니미노의 오개조 말씀이군요.",
    5608: "그 다섯 가지란 무엇입니까?",
    5609: "첫째, 아군 사기가 적보다 높다면,\n가장 먼저 돌격해 공을 세워라.",
    5610: "단, 아군 사기가 낮으면 멈추어라.\n개죽음하거나 멋대로 앞섰다고 꾸지람받는 것이\n고작일 테니.",
    5611: "(주위와 보조를 맞추라는 뜻인가?)",
    5612: "둘째, 평소 아군의 용장과 가까이 지내며,\n그를 본보기 삼아 뒤지지 않도록 힘써라.",
    5613: "지금 바로 우리가 하고 있는 일이군요.",
    5614: "셋째, 투구의 후키가에시가 아래로 향하고,\n등깃발이 전혀 흔들리지 않는 적은 강적이다……",
    5615: "후키가에시가 위로 향하고,\n등깃발이 흔들리는 적은 약하다.\n먼저 약한 적부터 쓰러뜨려라.",
    5616: "반대가 아닌가……?",
    5617: "전장에서도 침착한 적은\n강하다는 뜻일 겁니다.",
    5618: "넷째, 창끝을 위로 든 적은 약하고,\n아래로 내린 적은 강하다.",
    5619: "창끝이 가지런한 부대는 창 아시가루다.\n창끝 길이가 제각각이면 무사 부대다.\n무사 부대를 노려 쓰러뜨려라……",
    5620: "(아시가루는 모두 지급받은 무기를 쓰니 가지런하고,\n　무사 부대는 저마다 제 창을 가져오니,\n　창끝이 맞지 않는다는 뜻인가……)",
    5621: "다섯째, 적의 기세가 왕성하면 수비하며 견디고,\n적의 기세가 꺾이면,\n곧바로 공격하라!",
    5622: "……여러 말을 했지만,\n전쟁은 천변만화하는 법.\n미리 정한 것과 달라질 때도 많을 것이다……",
    5623: "달라지면 달라진 대로 맞춰,\n전장에서 능숙하게 움직여라.\n그것이 가장 중요하다!",
    5624: "상황이 달라졌다고 당황하면 꼴사납고,\n오히려 실패하기 쉽다.\n흐름에 몸을 맡겨 최선을 다할 뿐이다……",
    5625: "(\x1bCA바바\x1bCZ 님 말씀은 대부분,\n　주위를 잘 살피는 것에서 시작하는군.)",
    5626: "(정해진 규칙만 따르기보다,\n　주위를 살피며 움직인다……\n　그것이 내가 지향할 바일지도 모르겠군.)",
    5627: "다케다 사천왕 중 최연장자인 \x1bCA바바 노부하루\x1bCZ에게는,\n후진을 가르친 일화가 많이 남아 있다.",
    5628: "그의 좌우명은 ‘상재전장’――\n그 글귀가 적힌 족자가,\n늘 \x1bCA노부하루\x1bCZ의 방에 걸려 있었다고 한다.",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    5487: ["ko_so_sun_alliance_term_requires_glossary_review"],
    5497: ["bishamonten_reference_requires_glossary_review"],
    5507: ["send_salt_to_the_enemy_proverb_requires_style_review"],
    5509: ["shiodome_no_tachi_name_requires_glossary_review"],
    5510: ["takenaka_hanbei_full_name_requires_glossary_review"],
    5533: ["yoriki_service_status_requires_glossary_review"],
    5549: ["oni_shibata_epithet_requires_glossary_review"],
    5558: ["silver_namazuo_helmet_term_requires_glossary_review"],
    5575: ["sunpu_residence_term_requires_glossary_review"],
    5592: ["takeda_big_four_term_requires_glossary_review"],
    5607: ["oni_mino_five_articles_term_requires_glossary_review"],
    5614: ["fukigaeshi_helmet_term_requires_glossary_review"],
    5628: ["jozaisenjo_motto_reading_requires_glossary_review"],
}

PREVIOUS_ARTIFACT_PINS = {
    **shared.PREVIOUS_ARTIFACT_PINS,
    "evidence/alignment_evidence.v0.19.json": (
        "C9CAC451FFC28C1BFACEA9543BD632E171311F36745F53C48D8257363B72F3AE"
    ),
    "public/msgev_ko_historical_events_5359_5486.v0.19.json": (
        "9BD0043254DEDE78D9B11D1F8D7FDC66316277BB54B2964DB178F68EFDBFA88E"
    ),
    "review/review_index.v0.19.json": (
        "F529FA5AEB92F4EE4037AC480DE5287278CE083ED59CB2932781E76E2827BCD5"
    ),
    "validation.v0.19.json": (
        "056605D93E105ACFBAFE4391FFA69FC6B0C0A5D4788C7D279FBB4FC8C5D6A633"
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
    if len(ids) != 142 or ids != sorted(TRANSLATIONS):
        raise ValueError("batch20 ids are not the exact 142 displayed entries")
    return ids


def event_for(entry_id: int) -> str:
    matches = [
        event["event_id"]
        for event in EVENTS
        if event["start_id"] <= entry_id <= event["end_id"]
    ]
    if len(matches) != 1:
        raise ValueError(f"id {entry_id} does not map to one batch20 event group")
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
        5486,
        5487,
        5509,
        5510,
        5533,
        5534,
        5552,
        5553,
        5574,
        5575,
        5593,
        5594,
        5628,
        5629,
    )
    evidence["schema"] = "nobu16.kr.event-dialogue-alignment-evidence.v20"
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
    review["schema"] = "nobu16.kr.event-dialogue-review-index.v20"
    validation["schema"] = "nobu16.kr.event-dialogue-generation-validation.v20"
    validation["font_integration"].pop(
        "current_font_or_installer_must_not_include_batch19", None
    )
    validation["font_integration"][
        "current_font_or_installer_must_not_include_batch20"
    ] = True
    integrity = validation["preexisting_integrity"]
    integrity["dialogue_v01_v19_artifacts_before"] = integrity.pop(
        "dialogue_v01_v18_artifacts_before"
    )
    integrity["dialogue_v01_v19_artifacts_after"] = integrity.pop(
        "dialogue_v01_v18_artifacts_after"
    )
    safety = validation["safety"]
    safety.pop(
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_v14_v15_v16_v17_v18_artifacts_modified",
        None,
    )
    safety[
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_v14_v15_v16_v17_v18_v19_artifacts_modified"
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
