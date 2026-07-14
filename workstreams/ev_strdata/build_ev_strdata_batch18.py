#!/usr/bin/env python3
"""Build source-free ev_strdata historical event batch v0.18 artifacts."""

from __future__ import annotations

import argparse
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_common_message_overlay as common  # noqa: E402
import build_ev_strdata_batch1 as shared  # noqa: E402


BATCH_ID = "ev-strdata-historical-events-3485-3661-v0.18"
OVERLAY_NAME = "ev_strdata_ko_historical_events_3485_3661.v0.18.json"
EVIDENCE_NAME = "alignment_evidence.v0.18.json"
REVIEW_NAME = "review_index.v0.18.json"
VALIDATION_NAME = "validation.v0.18.json"

SCOPE_START = 3485
SCOPE_END = 3661
NEXT_DISPLAY_ID = 3662
TRANSLATED_COUNT = 177
INSPECTED_COUNT = 177
DEFERRED_COUNT = 0

TRANSLATED_IDS_SHA256 = "517A94D7521C68010481803EA2A2BF482E6BA57260ADA9C94E8C5C69A62468D4"
TRANSLATION_MAP_SHA256 = "02C3F3AC68E43843AA517E7DCB894757FCBD6EEDA9737CBD849C44A5917BB3C8"
SOURCE_SC_HASHES_SHA256 = "44306F714350DBCF327E734DA1A61CD2FDEA7A5B962457094823F729497A9AEA"
ALL_REFERENCE_HASHES_SHA256 = "9C7B3A325A3FEFA4A9F003CABDC54F1FD768EA7345DF02E141858FFB6386E451"
INSPECTED_IDS_SHA256 = TRANSLATED_IDS_SHA256
DEFERRED_IDS_SHA256 = "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
PREVIOUS_DEFERRED_UNION_COUNT = 549
PREVIOUS_DEFERRED_UNION_SHA256 = "13D87F620AE49897C10127F8FED317F99859FA89CCAF13CDAACBE0D81787F449"
NEXT_DISPLAY_REFERENCE_HASHES = {
    "SC": "58E41EA1E7EC79501377388E1BAACCAF1846E7E8925CD01435E20D11AF6113F2",
    "JP": "7186D538C9098572E6A5148BDA2A88532074AE5F663394B4E5A85ED802A58B18",
    "TC": "39A70E8C1A2BDDB50357DE72622E9E02DA551DE241321776A063B271DE4895AB",
}

TRANSLATIONS = {
    3485: "본래 \x1bCB이마가와 가문\x1bCZ의 군사였던 \x1bCA호조 소운\x1bCZ(\x1bCA이세 소즈이\x1bCZ)는\n\x1bCC이즈·사가미\x1bCZ에서 독립을 선언했고,\n적자 \x1bCA우지쓰나\x1bCZ는 \x1bCC무사시\x1bCZ·\x1bCC시모사\x1bCZ·\x1bCC스루가\x1bCZ로 진출했다.",
    3486: "그 \x1bCC스루가\x1bCZ에서 \x1bCA우지쓰나\x1bCZ를 손바닥 위에 올려놓고 다룬 이는\n훗날 ‘가이도 제일의 무사’라 불린\n\x1bCB이마가와 가문\x1bCZ 당주 \x1bCA이마가와 고로 요시모토\x1bCZ였다.",
    3487: "\x1bCA우지쓰나\x1bCZ가 죽었는가.\n그런가, 그 사내가……",
    3488: "그렇습니다.\n이미 눈치채셨겠지만\n이는 더없이 좋은 기회입니다.",
    3489: "허허, 승려답지 않게 험한 말을 하는군……\n하지만 스승이여, 나는 마음속 깊이\n\x1bCA우지쓰나\x1bCZ와 다시 한번 싸우고 싶었소.",
    3490: "5년 전의 나는 아직 어렸고\n\x1bCA우지쓰나\x1bCZ 앞에서 손도 쓰지 못했지.",
    3491: "형을 밀어내고 가독을 이어 오만했던 나를\n정신 차리게 한 사람이 바로 우지쓰나였소……",
    3492: "내 아버지의 사촌이라지만\n참으로 무서운 사내였지.\n그래서 다시 한번 겨루고 싶었건만……",
    3493: "흠, 그렇다면 \x1bCA우지쓰나\x1bCZ는 요시모토 님께\n또 한 명의 스승이었던 셈이군요.",
    3494: "하하!\n그럴지도 모르겠군.\n말하자면 또 한 명의 스승이지.",
    3495: "그렇다면 이번에는 \x1bCA요시모토\x1bCZ 님께서 스승이 되십시오.\n\x1bCA우지쓰나\x1bCZ의 아들 \x1bCA우지야스\x1bCZ에게\n난세를 살아가는 법을 가르쳐 주시지요.",
    3496: "죽은 이는 남기고 산 이는 이어받는다……\n그 산 이가 죽을 때면 다시 이을 자가 나타나지요.\n사람은 그렇게 만들어지는 법입니다.",
    3497: "이런, 자신에게 유리할 때만\n설교를 참 잘하는군.\n이번 싸움으로 네게 한 수 가르쳐 주마……",
    3498: "\x1bCA이마가와 요시모토\x1bCZ는 \x1bCA우지쓰나\x1bCZ의 죽음을 틈타 \x1bCC스루가\x1bCZ로\n출병해 \x1bCC간바라성\x1bCZ 등 \x1bCC스루가 동부\x1bCZ를 점령했다.\n이른바 ‘가토의 난’이다……",
    3499: "\x1bCA요시모토\x1bCZ는 \x1bCA[b1251]\x1bCZ에게도 공동 작전을 제안했고\n\x1bCA[bm1251]\x1bCZ도 흔쾌히 받아들여 공격에 가담했다.\n이 움직임은 곧바로 \x1bCA우지야스\x1bCZ에게 전해졌다.",
    3500: "서둘러 \x1bCC스루가\x1bCZ로 향한다!\n그곳은 \x1bCB이마가와\x1bCZ와 \x1bCB다케다\x1bCZ의 움직임을 막는 요충지다.\n결코 빼앗길 수 없다!",
    3501: "보, 보고드립니다!",
    3502: "간토 간레이 \x1bCA우에스기 노리마사\x1bCZ와 \x1bCC오기가야쓰\x1bCZ의 \x1bCA우에스기 도모사다\x1bCZ……\n게다가 고가 구보 \x1bCA아시카가 하루우지\x1bCZ 님까지 전선에 가담해 \n함께 \x1bCC가와고에성\x1bCZ을 공격하고 있습니다!",
    3503: "\x1bCA하루우지\x1bCZ라고? 내 매부가 아니냐!\n그 자식…… 대체 무슨 생각이지!\n틀림없이 \x1bCA노리마사\x1bCZ에게 꾀인 게야!",
    3504: "그뿐만이 아닌 듯하구나, \x1bCA마고쿠로\x1bCZ.\n\x1bCA노리마사\x1bCZ를 뒤에서 움직인 자가 있다……\n동서 양쪽에서 우리를 협공하려는 것이지.",
    3505: "그렇다면 설마…… \x1bCA이마가와 요시모토\x1bCZ가!?\n\x1bCB다케다 가문\x1bCZ뿐 아니라 \x1bCB두 우에스기 가문\x1bCZ과 \x1bCB고가 구보\x1bCZ까지\n모두 손아귀에 넣었다는 건가!",
    3506: "그래, 틀림없다.\n그런데 \x1bCC가와고에\x1bCZ에 모인 적군은 얼마나 되느냐?",
    3507: "그, 그것이…… 군세가 워낙 많아\n정찰병도 다 세지 못했다고 합니다……\n대략 8만이라 합니다……",
    3508: "8만…… 쉽게 모을 수 있는 수가 아니군.\n하지만 \x1bCB두 우에스기 가문\x1bCZ과 \x1bCB고가 구보\x1bCZ가 힘을 합쳤다면\n수만을 넘길 수도 있겠지……",
    3509: "형님, 이건 위험해……\n\x1bCC가와고에\x1bCZ를 잃으면 \x1bCB호조\x1bCZ의 \x1bCC간토\x1bCZ 지배는\n모두 물거품이 된다고!",
    3510: "……\x1bCA마고쿠로\x1bCZ, \x1bCC가와고에성\x1bCZ을 맡아 주겠느냐?\n이기라고는 하지 않겠다.\n지지 말고 버텨 주기만 하면 된다.",
    3511: "나더러 죽으라는 말이오, 형님?",
    3512: "……",
    3513: "그런 얼굴 하지 마시오!\n나는 하치만의 화신이라 불린 몸이오.\n죽으라 해도 그리 쉽게 죽지는 않소!",
    3514: "미안하다, \x1bCA마고쿠로\x1bCZ. 아니, \x1bCA[bm790]\x1bCZ!\n내가 저지른 실수를\n네게 수습하게 하다니……",
    3515: "아버님이 돌아가신 뒤\n곧바로 \x1bCB이마가와\x1bCZ와 화친했어야 했다.\n그랬다면 이런 사태까지는……",
    3516: "형님, 지금 그런 약한 소리는 듣고 싶지 않소!\n내가 살아 돌아오거든\n그때 내 원망을 실컷 들어 주시오!",
    3517: "그래, 알겠다! \x1bCC가와고에\x1bCZ는 맡기마! \n남은 것은 가토다. 이제 와서 \x1bCA요시모토\x1bCZ가 물러나지는 않겠지.\n그렇다고 쉽게 이길 상대도 아니고……",
    3518: "그럼……\n달리 손쓸 방법이 없다는 거요?",
    3519: "아니다. 이번 \x1bCA요시모토\x1bCZ의 포위망에도……\n빈틈이 있다면 서쪽이다.\n\x1bCA요시모토\x1bCZ의 진영에 가담한…… \x1bCA[b1251]\x1bCZ.",
    3520: "\x1bCA[bm1251]\x1bCZ가 가장 속내를 알 수 없는 자다. 겉으로는\n\x1bCA요시모토\x1bCZ에게 협력하면서 남몰래 어부지리를 노리고 있지.\n그 생각을 도리어 우리가 이용하는 것이다……!",
    3521: "그 모습을 보니 서쪽은 걱정 없겠군.\n나는 동쪽, \x1bCC가와고에\x1bCZ로 가겠소!",
    3522: "부탁한다, \x1bCA[bm790]\x1bCZ.\n서쪽을 정리하면 곧바로 구원하러 가겠다.\n그때까지 절대로 죽어서는 안 된다!",
    3523: "참으로 무리한 말을 하는군……\n그럼 형님, 다녀오겠소!",
    3524: "이렇게 \x1bCA요시모토\x1bCZ가 펼친 포위망을 막기 위해\n\x1bCA[b790]\x1bCZ는 \x1bCC가와고에성\x1bCZ으로 향했고\n\x1bCA우지야스\x1bCZ는 \x1bCC가토\x1bCZ로 출진했다……",
    3525: "\x1bCA[b1251]\x1bCZ의 아우 \x1bCA다케다 노부시게\x1bCZ―",
    3526: "젊어서부터 아버지 \x1bCA노부토라\x1bCZ에게 그릇을 인정받았으며\n\x1bCA[bm1251]\x1bCZ를 미워한 \x1bCA노부토라\x1bCZ가 그를\n\x1bCB다케다 가문\x1bCZ의 당주로 세우려 했던 일로 유명하다.",
    3527: "\x1bCB다케다 가문\x1bCZ·\x1bCC쓰쓰지가사키관\x1bCZ―",
    3528: "\x1bCA노부시게\x1bCZ, 무엇을 하고 있느냐?",
    3529: "영주님.\n태어날 아이를 위해\n가훈을 만들고 있었습니다.",
    3530: "……영주님이라 부르지 마라. 우리는 형제가 아니냐.\n그런데 어떤 가훈을 만들고 있느냐?\n내게도 보여 주겠느냐?",
    3531: "……형님의 부탁이라면 보여 드리겠습니다.\n여기 있습니다.\n보십시오!",
    3532: "음……\n‘첫째\u3000영원토록\n영주님을 배신해서는 안 된다’",
    3533: "‘둘째\u3000영주님께서 내리신 녹봉에\n\u3000결코 불만을 품어서는 안 된다’",
    3534: "……이런 내용이 모두 몇 조나 되느냐?",
    3535: "99조입니다.",
    3536: "그, 그러냐…… 조금만 더\n\x1bCB다케다 가문\x1bCZ 밖에서도 쓸모 있는 내용으로 만들 수 없느냐?",
    3537: "그럴 수 없습니다.\n제가\n\x1bCB다케다 가문\x1bCZ 밖에서 살아갈 일은 없으니까요……",
    3538: "너는 여전하구나……\n어째서 그토록 나에게 충성을 다하느냐?",
    3539: "생각해 보면 아버님은\n네게 \x1bCB다케다\x1bCZ의 당주 자리를 물려주려 했고\n그래서 남몰래 가보를 건네셨지?",
    3540: "예, 하지만 모두 형님께 바쳤습니다.",
    3541: "(아버님도 참 보람이 없으시군……)",
    3542: "형님께는 \x1bCB다케다 가문\x1bCZ을 이끌고 천하를 얻을 힘이 있습니다.\n잔재주밖에 없는 저는 그저 형님을 믿고\n따를 뿐입니다.",
    3543: "저는 형님께 은혜를 입었습니다.\n형님께 큰일이 생긴다면\n가장 먼저 달려가 싸우다 죽겠습니다.",
    3544: "이제 됐다, 잘 알겠다.\n물어본 내가 어리석었구나.\n……싸우다 죽을 필요는 없다. 죽지 마라!",
    3545: "예, 앞으로도 변함없이\n형님께 충성을 다하겠습니다.",
    3546: "(\x1bCA덴큐 노부시게\x1bCZ, 가신으로서는\n\u3000이만한 장수가 또 없겠지……)",
    3547: "(하지만 우리는 피를 나눈 형제다.\n\u3000혈육의 정이 조금은 있어도 되지 않을까.\n\u3000그리 생각하는 것은 내 어리광일까……)",
    3548: "99조에 이르는 다케다 노부시게의 가훈에는\n\x1bCA[bm1251]\x1bCZ에게 충성을 맹세하는 조항 외에도\n무사가 지켜야 할 생활 규범이 많이 담겨 있었다……",
    3549: "이는 훗날 유명해진 고슈 법도지차제의\n원형이 되었다고 전해진다.",
    3550: "참모 \x1bCA나베시마 나오시게\x1bCZ는 \x1bCB류조지 가문\x1bCZ의 전략을 맡았다.\n바쁜 나날을 내조로 받쳐 준 이는\n사랑하는 아내 \x1bCA히코쓰루히메\x1bCZ였다.",
    3551: "두 사람의 만남은 전설처럼 전해진다.\n어느 날 전투에서 승리해 돌아오던 길에\n\x1bCA나오시게\x1bCZ가 \x1bCC이이모리성\x1bCZ에서 \x1bCA히코쓰루\x1bCZ에게 첫눈에 반했다고 한다……",
    3552: "이봐, 점심은 아직인가!\n이럴 줄 알았다면 여기 들르지 말고\n곧바로 거성으로 돌아갈 걸 그랬군.",
    3553: "전하께서 갑자기 들르셔서\n주방도 점심을 준비하느라 정신이 없는 듯합니다.\n……제가 잠시 살펴보고 오겠습니다.",
    3554: "예상치 못한 많은 장병이 찾아오자\n점심 준비에 쫓긴 시녀들은\n큰 혼란에 빠졌다.",
    3555: "모두 진정하세요!\n손님 수만큼 정어리는 준비되어 있습니다.\n일을 나눠 차례대로 구우면 됩니다!",
    3556: "(음, 저 여인은……?)",
    3557: "아, 그대는 생선을\n잘 굽지 못하는 모양이군요. 이리 주세요!\n제가 대신 구워 드리죠!",
    3558: "전혀 서두를 필요 없어요.\n차근차근 순서대로 나르면 됩니다.\n침착하게 준비합시다!",
    3559: "(훌륭한 지시로 시녀들을 이끌며\n\u3000그 많은 정어리를 굽다니……\n\u3000저토록 영리한 여인도 있었구나.)",
    3560: "이보게…… 생선을 구우면서\n시녀들에게 지시하는 저 여인은\n어느 집안의 여인인가?",
    3561: "\x1bCA이시이 쓰네노부\x1bCZ의 따님 \x1bCA히코쓰루\x1bCZ 님입니다.\n전에는 \x1bCA노토미 노부즈미\x1bCZ 님께 시집갔지만\n\x1bCA노토미\x1bCZ 님이 전사해 지금은 과부이십니다……",
    3562: "오.\n그렇다면 지금은 혼자란 말인가……",
    3563: "\x1bCA히코쓰루\x1bCZ는 재치 있게 시녀들을 이끌 뿐 아니라\n앞장서서 정어리를 구웠다. 그 솜씨에 \x1bCA나오시게\x1bCZ가\n마음을 빼앗겨 훗날 정식으로 청혼했다.",
    3564: "\x1bCA히코쓰루\x1bCZ는 전국시대에는 드문 연애결혼으로\n아내가 된 뒤 총명함과 포용력으로\n냉철한 군사 \x1bCA나베시마 나오시게\x1bCZ를 보좌했다고 한다……",
    3565: "\x1bCC교토\x1bCZ에서 \x1bCC미노\x1bCZ로 간 기름 장수는 슈고\n\x1bCB도키씨\x1bCZ의 신임을 얻어 유력 무장이 되었다.\n그 아들 \x1bCA[bm924]\x1bCZ가 \x1bCB도키씨\x1bCZ를 몰아내고 전국 다이묘가 되었다.",
    3566: "하극상의 전형이었던 \x1bCC미노\x1bCZ의 \x1bCB사이토 가문\x1bCZ은\n이제 \x1bCA오다 노부나가\x1bCZ의 공세에 밀려\n4대에 걸친 역사를 끝내려 하고 있었다.",
    3567: "기뻐하라, \x1bCA기초\x1bCZ!\n장인어른이 내게 넘겨주겠다고 했던\n\x1bCC미노\x1bCZ 땅을 마침내 손에 넣었다!",
    3568: "……축하드립니다.",
    3569: "왜 그러느냐.\n아버지를 죽인 형이라지만\n친정이 멸망하니 슬픈 것이냐?",
    3570: "아닙니다. 이제 \x1bCB사이토 가문\x1bCZ에는 미련이 없습니다.\n이렇게 될 운명이었겠지요.\n지금은 \x1bCC미노\x1bCZ가 하루빨리 되살아나기만을 바랄 뿐입니다……",
    3571: "걱정하지 마라!\n\x1bCB사이토 가문\x1bCZ의 잔당을 평정한 뒤\n나는 이 \x1bCC미노\x1bCZ 땅으로 근거지를 옮길 생각이다!",
    3572: "\x1bCC오와리\x1bCZ보다 \x1bCC미노\x1bCZ가 \x1bCC기나이\x1bCZ에……\n아니, 천하에 더 가까우니 말이다!",
    3573: "기쁨에 들뜬 \x1bCB오다 가문\x1bCZ의 군세와 달리\n패배한 \x1bCA사이토 다쓰오키\x1bCZ는 미련을 남긴 채\n\x1bCC미노\x1bCZ를 떠났다……",
    3574: "이놈, \x1bCA노부나가\x1bCZ!\n두고 보아라!\n언젠가…… 반드시 복수하겠다!",
    3575: "\x1bCA사이토 다쓰오키\x1bCZ는 그 뒤 \x1bCC나가라강\x1bCZ을 따라 내려가\n\x1bCC이세 나가시마\x1bCZ로 달아났다고도, 옛 인연을 찾아\n\x1bCC에치젠\x1bCZ으로 갔다고도 전해진다.",
    3576: "이해에 \x1bCC미노\x1bCZ의 전국 다이묘 \x1bCA사이토 다카마사\x1bCZ는\n적은 수하만 이끌고 교토에 올라\n쇼군 \x1bCA[b75]\x1bCZ를 배알했다.",
    3577: "구보 님의 존안을 뵈어 황공하옵니다……\n저는 \x1bCA사이토 다카마사\x1bCZ라 합니다.\n교토 귀환을 진심으로 축하드립니다.",
    3578: "그대가 \x1bCC미노\x1bCZ의 \x1bCA사이토 다카마사\x1bCZ인가.\n소문은 들었다.\n아버지 \x1bCA[bm924]\x1bCZ를 죽인 자라던데……?",
    3579: "황공합니다. \x1bCA[bm924]\x1bCZ…… 제 아버지이긴 하나\n악행을 많이 저질러 고쿠진들의 원망이 깊었습니다.\n부득이하게 토벌할 수밖에 없었습니다.",
    3580: "가신이 주군을 죽이고 아들이 아버지를 죽이는 것이\n전국 난세의 이치인가……\n참으로 허망한 일이구나.",
    3581: "그 일은 차치하고, 구보 님.\n이번에 교토에 온 까닭은\n청이 하나 있기 때문입니다.",
    3582: "호오……?\n말해 보아라.",
    3583: "\x1bCB사이토 가문\x1bCZ은 미노 슈고다이 직을 맡고 있으며\n\x1bCB쇼군가\x1bCZ의 호코슈로서\n구보 님께 직접 충성을 바쳐 온 집안입니다.",
    3584: "……그 \x1bCB사이토 가문\x1bCZ의 이름은\n그대가 죽인 아버지 \x1bCA[bm924]\x1bCZ가 빼앗은 것이 아니냐.\n본래 기름 장수의 후손이라 들었다만?",
    3585: "그렇습니다.\n구보 님께 충성을 다할 수 있다면\n\x1bCB사이토\x1bCZ의 이름 따위는 버릴 생각입니다.",
    3586: "바라건대 쇼군가 오쇼반슈 가운데\n어느 한 집안의 이름을\n이 \x1bCA다카마사\x1bCZ에게 내려 주시지 않겠습니까.",
    3587: "(하극상으로 출세한 아버지를 죽인 자가\n오래된 가문 이름을 그토록 탐하다니……\n\u3000참으로 우스운 일이로군……)",
    3588: "마음대로 하여라……\n어차피 내게는 아무런 실권도 없다.\n이름뿐인 구보에 지나지 않으니.",
    3589: "예!",
    3590: "\x1bCA사이토 다카마사\x1bCZ는 이때\n쇼군 \x1bCA요시테루\x1bCZ에게 무로마치 막부 사시키의 하나이자\n외가와 인연이 있는 \x1bCB잇시키 가문\x1bCZ의 이름을 인정받았다.",
    3591: "아버지를 죽였다는 오명과\n출신을 둘러싼 의혹을\n\x1bCB사이토\x1bCZ라는 성과 함께 묻으려 했는지도 모른다……",
    3592: "동시에 이름도 \x1bCA다카마사\x1bCZ에서\n‘\x1bCA요시타쓰\x1bCZ’로 바꾸었다.\n\x1bCB잇시키 가문\x1bCZ의 돌림자인 ‘요시’를 넣은 것이다.",
    3593: "하지만 이 개성은\n당사자 외에는 좀처럼 인정받지 못했다……",
    3594: "‘\x1bCA잇시키 요시타쓰\x1bCZ’로 이름을 바꾸었지만\n실제로는 ‘\x1bCA사이토 요시타쓰\x1bCZ’라고 부르는 이가\n더 많았다고 한다.",
    3595: "\x1bCB호조 가문\x1bCZ의 시조 \x1bCA소운\x1bCZ(\x1bCA이세 소즈이\x1bCZ)는\n본래 \x1bCA이마가와 우지치카\x1bCZ의 숙부이자 군사였으나\n훗날 독립해 \x1bCC간토\x1bCZ로 영지를 넓혀 갔다.",
    3596: "\x1bCA우지쓰나\x1bCZ 대에는 \x1bCA이마가와\x1bCZ와 \x1bCA호조\x1bCZ가 서로 다른\n다이묘 가문이 되어 \x1bCC스루가\x1bCZ 동부, 곧 \x1bCC후지강\x1bCZ 동쪽을\n둘러싸고 서로 적대하기에 이르렀다.",
    3597: "\x1bCB이마가와 가문\x1bCZ으로서는 본래 지배하던 \x1bCC가토\x1bCZ를\n가신 집안이던 \x1bCB호조 가문\x1bCZ에 빼앗긴 채\n언제까지고 내버려 둘 수는 없었다.",
    3598: "자, \x1bCA우지야스\x1bCZ 녀석……\n어떻게 나올지 볼 만하겠군.\n앞뒤로 적을 두고 어찌할 테냐?",
    3599: "\x1bCA요시모토\x1bCZ의 계책으로 이미 \x1bCB야마노우치\x1bCZ·\x1bCB오기가야쓰\x1bCZ의\n\x1bCB두 우에스기 가문\x1bCZ과 고가 구보 \x1bCA아시카가 하루우지\x1bCZ까지 힘을 합쳐\n\x1bCB호조 가문\x1bCZ의 \x1bCC가와고에성\x1bCZ을 공격하고 있었다……",
    3600: "\x1bCA우지야스\x1bCZ는 매부 \x1bCA쓰나시게\x1bCZ를 \x1bCC가와고에성\x1bCZ 방어에 보내고\n자신은 이 \x1bCC가토\x1bCZ에\n진을 친 모양입니다.",
    3601: "군사를 나누었는가.\n정석이라지만 참으로 시시한 계책이군.\n그 정도로 이 \x1bCA요시모토\x1bCZ를 이길 수 있다고 생각하나……",
    3602: "우리에게는 \x1bCB다케다군\x1bCZ도 원군으로 와 있습니다.\n질 리가 없습니다.",
    3603: "\x1bCB이마가와\x1bCZ·\x1bCB다케다\x1bCZ 연합군은 \x1bCC나가쿠보성\x1bCZ과 \x1bCC기쓰네바시\x1bCZ에서\n\x1bCA호조 우지야스\x1bCZ의 군세를 격퇴했다.",
    3604: "이번 싸움은 다소 져도 상관없다.\n진정한 적은 시간이다……!\n시간이 아깝다! 서둘러 끝내야 한다!",
    3605: "작은 싸움의 승패에 매달릴 틈은 없다.\n\x1bCA우지야스\x1bCZ는 \x1bCA요시모토\x1bCZ의 의도를 비껴 가며\n기사회생의 수를 둘 기회를 노렸다……",
    3606: "\x1bCA우지야스\x1bCZ, 역시 내 적수가 아니었나……\n하지만 어딘가 지는 모습이 부자연스럽군.\n다른 계책이라도 있는 것인가?",
    3607: "\x1bCA요시모토\x1bCZ 님, 최악의 사태가 벌어졌습니다.\n미처 알아채지 못한 것은 빈승의 불찰입니다……",
    3608: "무슨 일이냐, 무엇이 벌어졌지?",
    3609: "우군인 \x1bCA다케다 하루노부\x1bCZ가 사자를 보내\n\x1bCB호조\x1bCZ와 화친하라고 권해 왔습니다……",
    3610: "뭐라!?\n\x1bCA하루노부\x1bCZ 녀석, \x1bCB호조\x1bCZ로 돌아선 것인가!",
    3611: "\x1bCA우지야스\x1bCZ는 \x1bCA요시모토\x1bCZ의 원군인 \x1bCA다케다 하루노부\x1bCZ에 주목해\n싸움이 시작되자마자\n화친의 중재를 부탁하고 있었다.",
    3612: "\x1bCA다케다 하루노부\x1bCZ에게도\n\x1bCB이마가와\x1bCZ와 \x1bCB호조\x1bCZ 두 가문의 다툼을 중재하여\n양쪽 모두에게 은혜를 베푸는 것은 나쁘지 않은 일이었다.",
    3613: "그렇다면 \x1bCB호조 가문\x1bCZ이 \x1bCC가토\x1bCZ의 성들을 \x1bCB이마가와 가문\x1bCZ에\n넘기는 조건으로 두 가문은 화친한다.\n이 조건으로 괜찮겠는가?",
    3614: "이의 없다. \x1bCC가토\x1bCZ는 \x1bCC하코네산\x1bCZ 너머에 있어\n지키기도 번거로운 땅이니\n이참에 \x1bCB이마가와 가문\x1bCZ에 넘기겠다.",
    3615: "\x1bCC가토\x1bCZ는 본래 \x1bCB이마가와 가문\x1bCZ이 다스리던 땅이다.\n그저 제자리로 돌아온 셈이지만……\n돌려받는다면 싸움을 계속할 이유는 없다.",
    3616: "다소 마음에 들지는 않으나\n이 자리에서 서로 군사를 물리고\n싸움을 그치기로 약속하겠다.",
    3617: "좋다, 이로써 화의가 성립되었다!\n이 \x1bCA하루노부\x1bCZ도 힘써 중재한 보람이 있군.\n하하하!",
    3618: "…………",
    3619: "\x1bCB이마가와\x1bCZ·\x1bCB호조\x1bCZ·\x1bCB다케다\x1bCZ의 미묘한 관계는\n훗날 고소슨 삼국동맹으로 이어지지만\n그것은 아직 훗날의 이야기다.",
    3620: "지금은 불리한 조건으로나마\n정전을 얻어 낸 \x1bCA우지야스\x1bCZ가\n벌써 다음 행동에 나섰다는 점을 보아야 할 것이다……",
    3621: "좋아, 이쪽 싸움은 끝났다!\n겉보기에는 손해를 보았지만\n\x1bCC가토\x1bCZ 땅쯤은 잃어도 아깝지 않다!",
    3622: "기다려라…… \x1bCA쓰나시게\x1bCZ!\n당장 \x1bCC가와고에성\x1bCZ으로 달려가겠다!",
    3623: "어느 여름밤―\n\x1bCA우지야스\x1bCZ는 가까운 이들과 함께\n높은 누각에서 더위를 식히고 있었다.",
    3624: "음, 무슨 소리가 들리지 않느냐?",
    3625: "저건 여우 울음소리군.\n여름에 울다니 별일이야.",
    3626: "그렇군요……\n여우는 여름에 우는 짐승이 아닙니다.\n흉사의 징조가 아니면 좋겠습니다……",
    3627: "이봐요, 형님.\n그런 불길한 말은 하지 마시오!",
    3628: "그렇구나……\n그렇다면 이건 어떠냐?",
    3629: "전해지는 말로는\n\x1bCA우지야스\x1bCZ가 이때 이런 와카를 지었다고 한다.",
    3630: "\u3000\u3000\u3000여름은 왔네, 소리 높여 우는 매미의 허물옷\n저마다 제 몸에 걸쳐 입어라",
    3631: "……?",
    3632: "역시 아버님, 참으로 훌륭한 와카입니다.",
    3633: "무슨 뜻이냐?",
    3634: "‘왔다(기쓰)’와 ‘소리(네)’를 구 사이에 나누어 두었다.\n여름에 우는 여우의 불길한 소리를 여우에게 돌려\n조복하려는 와카다.",
    3635: "그렇구나…… 무슨 말인지 모르겠군.\n하지만 울음소리는 정말 멎었어!",
    3636: "하지만……\n이 일로 여우가 아버님께 해코지하지 않으면 좋겠습니다……",
    3637: "걱정거리는 끝이 없구나……",
    3638: "\x1bCA호조 우지야스\x1bCZ는 이처럼 무략뿐 아니라\n와카에도 밝은 문인이자 독서가였으며\n역사서 ‘아즈마카가미’도 지녔다고 한다.",
    3639: "바로 \x1bCA우지야스\x1bCZ야말로\n‘겉은 문, 속은 무’라 평가받은\n문무를 겸비한 명장이었다.",
    3640: "참고로 이 이야기에는 뒷이야기가 있다.\n\x1bCA우지야스\x1bCZ가 죽은 뒤 \x1bCA우지마사\x1bCZ는 여우의 저주를 걱정해\n‘\x1bCA호조\x1bCZ 이나리’를 세웠다.",
    3641: "전해지는 말로는\n\x1bCA호조\x1bCZ 이나리의 개구리를 닮은 ‘개구리 바위’가\n\x1bCC오다와라\x1bCZ에 위기가 닥칠 때마다 반드시 운다고 한다……",
    3642: "\x1bCA다메카게\x1bCZ가 당주이던 시절의 \x1bCB에치고 나가오 가문\x1bCZ은\n주가인 \x1bCB에치고 우에스기 가문\x1bCZ의 위세를 뛰어넘어\n\x1bCC에치고\x1bCZ 제일의 세력으로 군림했다.",
    3643: "하지만 \x1bCA다메카게\x1bCZ는 그 과정에서 \x1bCA우에스기\x1bCZ 가신과\n\x1bCC에치고\x1bCZ의 고쿠진들과 여러 차례 충돌해\n모든 이의 지지를 받은 것은 아니었다.",
    3644: "그 모순은 \x1bCA다메카게\x1bCZ가 죽고\n장남 \x1bCA하루카게\x1bCZ가 뒤를 이은 뒤 터져 나왔으며\n\x1bCB나가오 가문\x1bCZ을 배반하는 자도 나타나기 시작했다……",
    3645: "으음, 어째서 모두 나에게 이빨을 드러내는가……\n나는 아무것도 하지 않았는데.\n죽은 아버지를 원망해야 한단 말인가……?",
    3646: "병약하고 우유부단한 \x1bCA하루카게\x1bCZ로서는\n이 사태를 수습하기 어려울 것이다……\n뜻있는 가신들은 그렇게 걱정했다.",
    3647: "그들이 기대를 건 사람은\n\x1bCA하루카게\x1bCZ와 나이 차가 큰 아우로서\n\x1bCC린센지\x1bCZ에서 불도를 닦던 \x1bCA도라치요\x1bCZ였다.",
    3648: "\x1bCA도라치요\x1bCZ 님은 수행 중이면서도\n문무를 겸비한 장수의 그릇이라 들었습니다.\n부디 \x1bCB나가오 가문\x1bCZ의 위기를 구해 주십시오!",
    3649: "저는 \x1bCA덴시쓰 선사\x1bCZ의 제자로서\n이 \x1bCC린센지\x1bCZ에서 일생을 마칠 생각입니다……\n무사가 될 뜻은 없습니다.",
    3650: "아니다! \x1bCA도라치요\x1bCZ여!\n슈고다이 가문에 태어났다면\n나라 안 백성의 기대에 응하는 것이 네 숙명이다.",
    3651: "선사님……",
    3652: "난세를 끝내고 사람들에게 평안을 가져오는 일도\n부처의 길과 통하는 중생 구제다.",
    3653: "게다가 형님인 \x1bCA하루카게\x1bCZ 님도\n고쿠진들의 반란에 가슴 아파하고 계신다.\n피를 나눈 아우인 네가 돕지 않고 어쩌겠느냐!",
    3654: "알겠습니다, 선사님……\n부족한 \x1bCA도라치요\x1bCZ, 불도를 포기하고 무사가 되어\n형님을 돕는 길을 택하겠습니다.",
    3655: "오오!\n그럼 당장 원복을 준비하자꾸나!",
    3656: "\x1bCA도라치요\x1bCZ는 가신들의 청을 받아 원복하고\n\x1bCA가게토라\x1bCZ라 이름 지어 형 \x1bCA하루카게\x1bCZ를 섬기게 되었다.\n훗날의 \x1bCA우에스기\x1bCZ 겐신―",
    3657: "원복한 지 얼마 지나지 않아\n\x1bCA가게토라\x1bCZ는 \x1bCC도치오성\x1bCZ을 공격한 고쿠진 반란군을 빠르게 진압하며\n군사적 재능의 편린을 드러냈다.",
    3658: "참으로 훌륭한 지휘다…… 첫 출진이라니 믿을 수 없군!\n마치 비사문천이 이승에 나타난 듯하다……",
    3659: "유약한 \x1bCA하루카게\x1bCZ와 정반대로 \x1bCA가게토라\x1bCZ는 용맹하게 싸웠다.\n그 과감한 모습은 널리 알려졌고\n아버지 \x1bCA다메카게\x1bCZ를 떠올리는 이도 적지 않았다.",
    3660: "차라리 \x1bCA하루카게\x1bCZ 님이 아니라\n\x1bCA가게토라\x1bCZ 님이 \x1bCB나가오 가문\x1bCZ의 당주가 된다면―\n……아니, 아직은 입에 담지 말자.",
    3661: "훗날 군신이라 불릴 사내의\n전쟁으로 점철된 삶은 이렇게 막을 올렸다.",
}

CURRENT_EXCLUDED_IDS = frozenset()
PREVIOUS_DEFERRED_BATCHES = (
    {
        "version": "v0.13",
        "batch_id": "ev-strdata-event-labels-2207-2406-v0.13",
        "ids": frozenset(range(2207, 2400)),
        "count": 193,
        "ids_sha256": "B346249D6B010CCC0243DE9AE75377A7FF0E0401F8A5FDC1E74621634B9FD9BB",
    },
    {
        "version": "v0.14",
        "batch_id": "ev-strdata-event-labels-2407-2580-v0.14",
        "ids": frozenset(range(2581, 2780)),
        "count": 199,
        "ids_sha256": "A3083AED6A0EB0D670B9E3A19D50BF78D60D6325533C2D04D381993F28345373",
    },
    {
        "version": "v0.15",
        "batch_id": "ev-strdata-character-speaker-labels-2780-2971-v0.15",
        "ids": frozenset(
            {2953, 2954, 2955, 2959, 2960, 2964, 2965, 2967}
            | set(range(2972, 2998))
            | {2998, 2999}
            | set(range(3000, 3007))
        ),
        "count": 43,
        "ids_sha256": "2B95F92D5D9B8AB6E96DEB1A412CB34957B24978FFF2C089254A42C3CE265245",
    },
    {
        "version": "v0.16",
        "batch_id": "ev-strdata-labels-narration-3007-3276-v0.16",
        "ids": frozenset(
            set(range(3105, 3116))
            | {3116}
            | set(range(3118, 3201))
            | {3201}
        ),
        "count": 96,
        "ids_sha256": "06BD88F03E814D81DC107F52B4F1B1452FF8461677854C550FAB5BC1DDD94D00",
    },
    {
        "version": "v0.17",
        "batch_id": "ev-strdata-events-endings-3277-3484-v0.17",
        "ids": frozenset(
            {
                3309, 3310, 3314, 3315, 3319, 3320, 3324, 3325, 3329,
                3330, 3334, 3335, 3339, 3340, 3344, 3345, 3349, 3350,
            }
        ),
        "count": 18,
        "ids_sha256": "CBD6A8F8CB20A423BE5D38411A6AB667ACECB736DCE08404B714ABDC1882D9FA",
    },
)
PREVIOUS_DEFERRED_IDS = frozenset(
    entry_id
    for batch in PREVIOUS_DEFERRED_BATCHES
    for entry_id in batch["ids"]
)
CLASS_COUNTS = {
    "hojo_fox_poem_event": 19,
    "kagetora_first_campaign_event": 20,
    "kato_conflict_event": 68,
    "nabeshima_family_event": 15,
    "saito_clan_event": 30,
    "takeda_nobushige_event": 25,
}
TERMINOLOGY_REVIEW_IDS = frozenset(
    {3486, 3502, 3527, 3546, 3549, 3561, 3583, 3586, 3590, 3619,
     3630, 3634, 3638, 3641, 3649, 3658}
)
RELATED_MSGEV_COLOR_DIFFERENCE_IDS = (3596, 3643)
TRANSLATED_UNIQUE_SOURCE_HASH_COUNT = 177
REPEATED_SOURCE_ID_GROUPS: tuple[tuple[int, ...], ...] = ()
EXCLUDED_CANDIDATE_COUNTS = {
    "actor_reference": 0,
    "dummy_placeholder": 0,
    "empty_slot": 0,
    "internal_event_key": 0,
}


def classify(entry_id: int) -> str:
    if entry_id <= 3524 or 3595 <= entry_id <= 3622:
        return "kato_conflict_event"
    if entry_id <= 3549:
        return "takeda_nobushige_event"
    if entry_id <= 3564:
        return "nabeshima_family_event"
    if entry_id <= 3594:
        return "saito_clan_event"
    if entry_id <= 3641:
        return "hojo_fox_poem_event"
    return "kagetora_first_campaign_event"


def non_display_kind(text: str) -> str | None:
    if text == "":
        return "empty_slot"
    if text.isascii() and all(char.isalnum() or char == "_" for char in text):
        return "internal_event_key"
    if text.startswith("[b") and text.endswith("]") and text.count("[") == 1:
        return "actor_reference"
    if not text.strip() or text.count("?") >= 2 and text.isascii():
        return "dummy_placeholder"
    return None


def generated_file_map(root: Path) -> dict[str, bytes]:
    paths = (
        Path("public") / OVERLAY_NAME,
        Path("evidence") / EVIDENCE_NAME,
        Path("review") / REVIEW_NAME,
        Path(VALIDATION_NAME),
    )
    return {path.as_posix(): (root / path).read_bytes() for path in paths}


def previous_deferred_overlap_metadata() -> dict[str, Any]:
    overlap_ids = sorted(CURRENT_EXCLUDED_IDS & PREVIOUS_DEFERRED_IDS)
    return {
        "previous_batches": [
            {
                "version": batch["version"],
                "batch_id": batch["batch_id"],
                "deferred_entry_count": batch["count"],
                "deferred_ids_sha256": batch["ids_sha256"],
            }
            for batch in PREVIOUS_DEFERRED_BATCHES
        ],
        "previous_deferred_union_entry_count": PREVIOUS_DEFERRED_UNION_COUNT,
        "previous_deferred_union_ids_sha256": PREVIOUS_DEFERRED_UNION_SHA256,
        "current_deferred_entry_count": DEFERRED_COUNT,
        "current_deferred_ids_sha256": DEFERRED_IDS_SHA256,
        "overlap_entry_count": len(overlap_ids),
        "overlap_ids_sha256": shared.hash_json(overlap_ids),
        "overlap_detected": bool(overlap_ids),
    }


def related_msgev_review_metadata() -> dict[str, Any]:
    return {
        "related_batches": [
            "msgev_historical_events_3441_3564.v0.4",
            "msgev_historical_events_3565_3688.v0.5",
        ],
        "same_numeric_id_semantic_reviewed_entry_count": TRANSLATED_COUNT,
        "terminology_cross_checked": True,
        "direct_translation_reuse": False,
        "ev_strdata_sc_color_structure_differs_at_ids": list(
            RELATED_MSGEV_COLOR_DIFFERENCE_IDS
        ),
        "ev_strdata_sc_structure_is_authoritative": True,
        "commercial_source_text_included": False,
    }


def validate_batch_sources(loaded: dict[str, dict[str, Any]]) -> list[int]:
    ids = sorted(TRANSLATIONS)
    inspected_ids = list(range(SCOPE_START, SCOPE_END + 1))
    if len(ids) != TRANSLATED_COUNT or ids != inspected_ids:
        raise shared.EvStrDataError("v0.18 translated scope changed")
    if len(inspected_ids) != INSPECTED_COUNT:
        raise shared.EvStrDataError("v0.18 inspected count changed")
    if CURRENT_EXCLUDED_IDS or DEFERRED_COUNT != 0:
        raise shared.EvStrDataError("v0.18 current exclusion set changed")
    if shared.hash_json(ids) != TRANSLATED_IDS_SHA256:
        raise shared.EvStrDataError("v0.18 translated id digest changed")
    if shared.hash_json(inspected_ids) != INSPECTED_IDS_SHA256:
        raise shared.EvStrDataError("v0.18 inspected id digest changed")
    if shared.hash_json(sorted(CURRENT_EXCLUDED_IDS)) != DEFERRED_IDS_SHA256:
        raise shared.EvStrDataError("v0.18 excluded id digest changed")
    if shared.hash_json([[entry_id, TRANSLATIONS[entry_id]] for entry_id in ids]) != TRANSLATION_MAP_SHA256:
        raise shared.EvStrDataError("v0.18 Korean translation map changed")

    for batch in PREVIOUS_DEFERRED_BATCHES:
        ordered = sorted(batch["ids"])
        if len(ordered) != batch["count"] or shared.hash_json(ordered) != batch["ids_sha256"]:
            raise shared.EvStrDataError(f"{batch['version']} deferred exclusion pin changed")
    if len(PREVIOUS_DEFERRED_IDS) != PREVIOUS_DEFERRED_UNION_COUNT:
        raise shared.EvStrDataError("v0.13-v0.17 deferred union count changed")
    if shared.hash_json(sorted(PREVIOUS_DEFERRED_IDS)) != PREVIOUS_DEFERRED_UNION_SHA256:
        raise shared.EvStrDataError("v0.13-v0.17 deferred union digest changed")
    overlap = sorted(CURRENT_EXCLUDED_IDS & PREVIOUS_DEFERRED_IDS)
    if overlap or shared.hash_json(overlap) != DEFERRED_IDS_SHA256:
        raise shared.EvStrDataError("v0.18 exclusions overlap v0.13-v0.17 exclusions")

    class_counts = Counter(classify(entry_id) for entry_id in ids)
    if dict(sorted(class_counts.items())) != CLASS_COUNTS:
        raise shared.EvStrDataError("v0.18 event classification counts changed")

    source_sc_hashes: list[str] = []
    all_reference_hashes: list[str] = []
    ids_by_source_hash: dict[str, list[int]] = defaultdict(list)
    detected_counts = Counter()
    for entry_id in ids:
        references = [
            loaded[language]["table"].texts[entry_id]
            for language in shared.LANGUAGES
        ]
        for text in references:
            kind = non_display_kind(text)
            if kind is not None:
                detected_counts[kind] += 1
        if any(not text.strip() for text in references):
            raise shared.EvStrDataError(f"id {entry_id}: empty aligned display text")
        source_sc = references[0]
        source_hash = common.text_hash(source_sc)
        source_sc_hashes.append(source_hash)
        all_reference_hashes.extend(common.text_hash(text) for text in references)
        ids_by_source_hash[source_hash].append(entry_id)
        failures = shared.replacement_failures(source_sc, TRANSLATIONS[entry_id])
        if failures:
            raise shared.EvStrDataError(f"id {entry_id}: invariant mismatch: {failures}")
    if detected_counts:
        raise shared.EvStrDataError(f"v0.18 non-display candidate found: {dict(detected_counts)}")
    repeated_groups = tuple(
        tuple(group)
        for group in ids_by_source_hash.values()
        if len(group) > 1
    )
    if repeated_groups != REPEATED_SOURCE_ID_GROUPS:
        raise shared.EvStrDataError("v0.18 repeated-source groups changed")
    if len(ids_by_source_hash) != TRANSLATED_UNIQUE_SOURCE_HASH_COUNT:
        raise shared.EvStrDataError("v0.18 unique SC source count changed")
    if shared.hash_json(source_sc_hashes) != SOURCE_SC_HASHES_SHA256:
        raise shared.EvStrDataError("v0.18 ordered SC source hashes changed")
    if shared.hash_json(all_reference_hashes) != ALL_REFERENCE_HASHES_SHA256:
        raise shared.EvStrDataError("v0.18 ordered SC/JP/TC source hashes changed")

    for language in shared.LANGUAGES:
        next_text = loaded[language]["table"].texts[NEXT_DISPLAY_ID]
        if non_display_kind(next_text) is not None:
            raise shared.EvStrDataError(f"v0.18 next candidate is not display text for {language}")
        if common.text_hash(next_text) != NEXT_DISPLAY_REFERENCE_HASHES[language]:
            raise shared.EvStrDataError(f"v0.18 next display anchor changed for {language}")
    return ids


def build_once(game_root: Path, out_root: Path) -> dict[str, Any]:
    loaded, before = shared.load_sources(game_root)
    ids = validate_batch_sources(loaded)
    overlap = previous_deferred_overlap_metadata()
    related_review = related_msgev_review_metadata()

    overlay_entries: list[dict[str, Any]] = []
    evidence_entries: list[dict[str, Any]] = []
    for entry_id in ids:
        source_sc = loaded["SC"]["table"].texts[entry_id]
        overlay_entries.append(
            {
                "id": entry_id,
                "source_sc_utf16le_sha256": common.text_hash(source_sc),
                "ko": TRANSLATIONS[entry_id],
            }
        )
        evidence_entries.append(
            {
                "id": entry_id,
                "classification": classify(entry_id),
                "references": {
                    language: {
                        "utf16le_sha256": common.text_hash(
                            loaded[language]["table"].texts[entry_id]
                        ),
                        "structure": shared.text_structure(
                            loaded[language]["table"].texts[entry_id]
                        ),
                    }
                    for language in shared.LANGUAGES
                },
                "translation_origin": "manual_sc_jp_tc_aligned_with_msgev_term_crosscheck",
            }
        )

    sc_packed = loaded["SC"]["packed"]
    sc_raw = loaded["SC"]["raw"]
    overlay = {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": shared.RESOURCE,
        "base_language": "SC",
        "entry_count": TRANSLATED_COUNT,
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "size": len(sc_packed),
            "packed_sha256": shared.sha256(sc_packed),
            "raw_size": len(sc_raw),
            "raw_sha256": shared.sha256(sc_raw),
            "string_count": shared.STRING_COUNT,
        },
        "defaults": {"status": "translated"},
        "entries": overlay_entries,
    }
    original_allowlist = common.ALLOWED_RESOURCES
    common.ALLOWED_RESOURCES = original_allowlist | shared.SUPPORTED_RESOURCES
    try:
        common.validate_overlay_shape(overlay)
    finally:
        common.ALLOWED_RESOURCES = original_allowlist

    source_files = {
        language: {
            **shared.SOURCE_PINS[language],
            "relative_path": loaded[language]["relative"],
            "string_count": shared.STRING_COUNT,
        }
        for language in shared.LANGUAGES
    }
    boundary_ids = (
        SCOPE_START - 1,
        SCOPE_START,
        3524,
        3525,
        3549,
        3550,
        3564,
        3565,
        3575,
        3576,
        3594,
        3595,
        3622,
        3623,
        3641,
        3642,
        SCOPE_END,
        NEXT_DISPLAY_ID,
    )
    evidence = {
        "schema": "nobu16.kr.ev-strdata-alignment-evidence.v18",
        "batch_id": BATCH_ID,
        "resource": "ev_strdata",
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "translated_display_entry_count": TRANSLATED_COUNT,
            "inspected_entry_count": INSPECTED_COUNT,
            "deferred_internal_entry_count": DEFERRED_COUNT,
            "next_display_id": NEXT_DISPLAY_ID,
            "functional_section": "historical_event_dialogue_and_narration",
            "functional_class_counts": CLASS_COUNTS,
            "excluded_candidate_counts": EXCLUDED_CANDIDATE_COUNTS,
        },
        "translation_mapping": {
            "sha256": TRANSLATION_MAP_SHA256,
            "entry_count": TRANSLATED_COUNT,
            "embedded_in_generator": True,
            "commercial_source_text_included": False,
        },
        "alignment_basis": [
            "same_resource_role",
            "same_17868_string_count",
            "same_numeric_string_ids",
            "sc_jp_tc_semantic_review",
            "exact_sc_hash_for_every_overlay_entry",
            "ordered_sc_jp_tc_hash_set_pin",
            "standalone_internal_placeholder_actor_and_empty_detection",
            "v013_through_v017_deferred_union_overlap_check",
            "related_msgev_terminology_crosscheck",
        ],
        "reference_language_note": (
            "The installed MSG tree has no EN ev_strdata resource; TC is the third "
            "reference alongside SC and JP. Official strings are represented only by hashes."
        ),
        "source_files": source_files,
        "boundary_anchors": [
            {
                "id": entry_id,
                "reference_hashes": {
                    language: common.text_hash(
                        loaded[language]["table"].texts[entry_id]
                    )
                    for language in shared.LANGUAGES
                },
            }
            for entry_id in boundary_ids
        ],
        "entry_count": TRANSLATED_COUNT,
        "entries": evidence_entries,
        "deferred_internal_groups": [],
        "previous_deferred_overlap": overlap,
        "related_msgev_review": related_review,
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.ev-strdata-review-index.v18",
        "batch_id": BATCH_ID,
        "quality_state": "historical_event_translation_draft_pending_runtime_review",
        "entry_count": TRANSLATED_COUNT,
        "terminology_review_count": len(TERMINOLOGY_REVIEW_IDS),
        "entries": [
            {
                "id": entry_id,
                "status": "translated",
                "classification": classify(entry_id),
                "translation_origin": "manual_sc_jp_tc_aligned_with_msgev_term_crosscheck",
                "human_review_required": True,
                "runtime_reviewed": False,
                "uncertainty_flags": ["event_text_runtime_layout"]
                + (
                    ["historical_term_or_reading_review"]
                    if entry_id in TERMINOLOGY_REVIEW_IDS
                    else []
                ),
            }
            for entry_id in ids
        ],
        "deferred_internal_groups": [],
        "previous_deferred_overlap": overlap,
        "related_msgev_review": related_review,
        "contains_commercial_source_text": False,
    }

    overlay_path = out_root / "public" / OVERLAY_NAME
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    for path, value in (
        (overlay_path, overlay),
        (evidence_path, evidence),
        (review_path, review),
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(shared.encode_json(value))

    source_free_scan = {
        path.relative_to(out_root).as_posix(): shared.source_free_counts(path.read_bytes())
        for path in (overlay_path, evidence_path, review_path)
    }
    if any(
        counts != {"han_or_kana_count": 0, "embedded_nul_count": 0}
        for counts in source_free_scan.values()
    ):
        raise shared.EvStrDataError(
            "v0.18 public artifact contains source script text or an embedded NUL"
        )

    binary = shared.common_binary_build(game_root, overlay_path)
    after = {
        relative: shared.sha256((game_root / Path(relative)).read_bytes())
        for relative in before
    }
    if before != after:
        raise shared.EvStrDataError("installed game resource changed during v0.18 build")

    artifacts = {
        path.relative_to(out_root).as_posix(): {
            "size": path.stat().st_size,
            "sha256": shared.sha256(path.read_bytes()),
        }
        for path in (overlay_path, evidence_path, review_path)
    }
    validation = {
        "schema": "nobu16.kr.ev-strdata-generation-validation.v18",
        "batch_id": BATCH_ID,
        "passed": True,
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "translated_display_entry_count": TRANSLATED_COUNT,
            "translated_ids_sha256": TRANSLATED_IDS_SHA256,
            "inspected_entry_count": INSPECTED_COUNT,
            "inspected_ids_sha256": INSPECTED_IDS_SHA256,
            "deferred_internal_entry_count": DEFERRED_COUNT,
            "deferred_ids_sha256": DEFERRED_IDS_SHA256,
            "next_display_id": NEXT_DISPLAY_ID,
            "total_string_slots": shared.STRING_COUNT,
            "sc_display_translation_target_count": shared.DISPLAY_TARGET_COUNT_SC,
            "functional_class_counts": CLASS_COUNTS,
            "excluded_candidate_counts": EXCLUDED_CANDIDATE_COUNTS,
        },
        "source_alignment": {
            "languages": list(shared.LANGUAGES),
            "english_reference_available": False,
            "traditional_chinese_used_as_third_reference": True,
            "string_count_each": shared.STRING_COUNT,
            "translated_reference_hash_count": TRANSLATED_COUNT * len(shared.LANGUAGES),
            "translated_ids_nonempty_in_all_references": TRANSLATED_COUNT,
            "ordered_sc_source_hashes_sha256": SOURCE_SC_HASHES_SHA256,
            "ordered_all_reference_hashes_sha256": ALL_REFERENCE_HASHES_SHA256,
            "source_files": source_files,
        },
        "translation": {
            "translation_map_sha256": TRANSLATION_MAP_SHA256,
            "translation_map_entry_count": TRANSLATED_COUNT,
            "exact_sc_hashes_emitted": TRANSLATED_COUNT,
            "runtime_layout_review_flag_count": TRANSLATED_COUNT,
            "historical_term_or_reading_review_flag_count": len(TERMINOLOGY_REVIEW_IDS),
            "source_text_embedded": False,
        },
        "repeated_source_policy": {
            "same_source_same_translation_required": True,
            "translated_unique_source_hash_count": TRANSLATED_UNIQUE_SOURCE_HASH_COUNT,
            "translated_repeated_source_group_count": 0,
            "repeated_source_id_groups": [],
            "failures": 0,
        },
        "deferred_internal_groups": [],
        "previous_deferred_overlap": overlap,
        "related_msgev_review": related_review,
        "replacement_invariants": {
            "checked": TRANSLATED_COUNT,
            "failures": 0,
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "edge_whitespace",
                "esc_sequences_in_order",
                "control_characters",
                "line_break_sequence",
                "private_use_codepoints",
                "bracket_placeholders_in_order",
            ],
        },
        "raw_format": {
            "lz4_wrapper_decompression": "OK",
            "message_table_parser": "tools/nobu16_msg_table.py",
            "raw_parse_rebuild_byte_exact_languages": list(shared.LANGUAGES),
            "binary_builder_state": "enabled_offline_output_only",
        },
        "offline_binary_build": {
            **binary,
            "installed_target_written": False,
        },
        "source_free_scan": source_free_scan,
        "artifacts": artifacts,
        "generator": {
            "path": SCRIPT_PATH.name,
            "sha256": shared.sha256(SCRIPT_PATH.read_bytes()),
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
            "official_source_text_exposed_in_public_artifacts": False,
            "process_memory_access": False,
            "executable_modified": False,
            "registry_modified": False,
            "existing_v01_through_v017_artifacts_modified": False,
        },
    }
    validation_path = out_root / VALIDATION_NAME
    validation_path.parent.mkdir(parents=True, exist_ok=True)
    validation_path.write_bytes(shared.encode_json(validation))
    if shared.source_free_counts(validation_path.read_bytes()) != {
        "han_or_kana_count": 0,
        "embedded_nul_count": 0,
    }:
        raise shared.EvStrDataError("v0.18 validation is not source-free")
    return {
        "entry_count": TRANSLATED_COUNT,
        "inspected_count": INSPECTED_COUNT,
        "deferred_count": DEFERRED_COUNT,
        "next_display_id": NEXT_DISPLAY_ID,
        "files": generated_file_map(out_root),
    }


def build_reproducibly(game_root: Path, out_root: Path) -> dict[str, Any]:
    game_root = game_root.resolve()
    out_root = out_root.resolve()
    source_paths = [
        game_root / "MSG" / language / "ev_strdata.bin"
        for language in shared.LANGUAGES
    ]
    before = {path.as_posix(): shared.sha256(path.read_bytes()) for path in source_paths}
    with tempfile.TemporaryDirectory(prefix="nobu16-evstr18-a-") as first_tmp:
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr18-b-") as second_tmp:
            first = build_once(game_root, Path(first_tmp))
            second = build_once(game_root, Path(second_tmp))
            if first["files"] != second["files"]:
                raise shared.EvStrDataError(
                    "isolated A/B v0.18 public artifacts are not byte-identical"
                )
    final = build_once(game_root, out_root)
    if final["files"] != first["files"]:
        raise shared.EvStrDataError(
            "final v0.18 public artifacts differ from isolated A/B output"
        )
    after = {path.as_posix(): shared.sha256(path.read_bytes()) for path in source_paths}
    if before != after:
        raise shared.EvStrDataError("installed game resource changed across v0.18 build")
    return final


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=REPO_ROOT.parent)
    parser.add_argument("--out-root", type=Path, default=WORKSTREAM_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = build_reproducibly(args.game_root, args.out_root)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={args.out_root.resolve()}")
    print(f"translated={result['entry_count']}")
    print(f"inspected={result['inspected_count']}")
    print(f"deferred_internal={result['deferred_count']}")
    print(f"next_display_id={result['next_display_id']}")
    for relative, blob in sorted(result["files"].items()):
        print(f"{relative}_sha256={shared.sha256(blob)}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
