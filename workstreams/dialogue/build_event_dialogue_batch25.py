#!/usr/bin/env python3
"""Build source-free Korean historical event dialogue batch25 (6142-6268)."""

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
import build_event_dialogue_batch24 as shared  # noqa: E402


source_shared = shared.source_shared
BATCH_ID = "msgev_historical_events_6142_6268.v0.25"
OVERLAY_NAME = "msgev_ko_historical_events_6142_6268.v0.25.json"
EVIDENCE_NAME = "alignment_evidence.v0.25.json"
REVIEW_NAME = "review_index.v0.25.json"
VALIDATION_NAME = "validation.v0.25.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 6142
SCOPE_END = 6268
EXCLUDED_INTERNAL_IDS: tuple[int, ...] = ()
BRACKET_TOKEN_RE = shared.BRACKET_TOKEN_RE

EVENTS = (
    {
        "event_id": "retreat_from_mikatagahara",
        "title_ko": "미카타가하라 패전과 하마마쓰 후퇴",
        "start_id": 6142,
        "end_id": 6163,
        "selected_count": 22,
    },
    {
        "event_id": "death_of_takeda_shingen",
        "title_ko": "다케다 신겐의 죽음",
        "start_id": 6164,
        "end_id": 6193,
        "selected_count": 30,
    },
    {
        "event_id": "todo_takatora_white_mochi",
        "title_ko": "도도 다카토라와 출세의 흰 떡",
        "start_id": 6194,
        "end_id": 6234,
        "selected_count": 41,
    },
    {
        "event_id": "death_of_azai_nagamasa",
        "title_ko": "아자이 나가마사의 최후",
        "start_id": 6235,
        "end_id": 6259,
        "selected_count": 25,
    },
    {
        "event_id": "end_of_echigo_uesugi",
        "title_ko": "에치고 우에스기 가문의 단절",
        "start_id": 6260,
        "end_id": 6268,
        "selected_count": 9,
    },
)

TRANSLATIONS: dict[int, str] = {
    6142: "미카타가하라 전투는\n\x1bCB다케다군\x1bCZ의 완승으로 끝났다.",
    6143: "참패한 \x1bCB도쿠가와 가문\x1bCZ은 수많은 장병을 잃었고,\n\x1bCA[bm1871]\x1bCZ도 여러 측근을 대신 희생시킨 끝에,\n맨몸으로 \x1bCC하마마쓰성\x1bCZ을 향해 달리고 있었다.",
    6144: "헉…… 헉……\n빌어먹을…… 이럴 수가……",
    6145: "주군, 정신을 차리십시오!\n성이 바로 눈앞입니다, 주군!",
    6146: "성…… \x1bCC하마마쓰\x1bCZ……\n나는…… 살아난 건가……!",
    6147: "예!\n다치지 않으셔서 정말 다행입니다.",
    6148: "내 몸 따위는 아무래도 좋다!\n……횃불을 밝혀라! 성문은 열어 두어라!\n도망쳐 오는 자들을 모두 맞아들여라!",
    6149: "뭐라고요!?\n적까지 성 안으로 들이실 셈입니까!?",
    6150: "모른다! 그런 건 알 바 아니다!\n아무튼 이제 아무 생각도 하고 싶지 않다!",
    6151: "……그저\n그 지옥에서 돌아오는 자들을 맞아 주고 싶다.\n그뿐이다!",
    6152: "알겠느냐.\n성문은 열어 두어라!",
    6153: "알겠습니다.\n그럼 아군을 북돋우도록 진중의 북을 치겠습니다.",
    6154: "\x1bCA사카이\x1bCZ 공?",
    6155: "\x1bCC하마마쓰성\x1bCZ·성 밖――",
    6156: "모두 멈춰라!\n아무래도 낌새가 이상하다……",
    6157: "\x1bCA[b1871]\x1bCZ를 추격하던 \x1bCA야마가타 마사카게\x1bCZ는\n\x1bCC하마마쓰성\x1bCZ의 모습을 보고 걸음을 멈췄다.",
    6158: "호오, 공성계인가……?\n우리를 꾀는 듯한 북소리까지 들리는군.\n무슨 계책이지……?",
    6159: "…………",
    6160: "후후후…… 제법 애먹을 듯하군.\n오늘 밤 싸움은 여기까지다!\n철수한다!",
    6161: "\x1bCA야마가타 마사카게\x1bCZ는\n\x1bCB도쿠가와 가문\x1bCZ이 공성계를 썼다고 보고,\n추격을 멈춘 채 군사를 물렸다.",
    6162: "간신히 목숨은 건졌지만,\n미카타가하라 전투의 참패와\n\x1bCA[b1251]\x1bCZ의 무서울 만큼 강한 힘은……",
    6163: "충격적인 기억이 되어,\n[bm1871]의 뇌리에 깊이 새겨졌다.",
    6164: "아버지 \x1bCA노부토라\x1bCZ를 추방하고 가독을 이은 뒤,\n30년이 넘는 세월이 흘렀다……",
    6165: "수많은 승리를 쌓은\n\x1bCA[b1251]\x1bCZ은 천하에 이름을 떨친\n무적의 군략가였다.",
    6166: "하지만,\n그런 \x1bCA[bm1251]\x1bCZ조차\n병마를 이길 수는 없었다.",
    6167: "\x1bCA가쓰요리\x1bCZ……\n내 명이 다한 듯하구나.",
    6168: "내가 죽으면 네가 \x1bCB다케다 가문\x1bCZ의 당주다.\n지금부터 이르는 말을 어기지 말고,\n\x1bCB다케다 가문\x1bCZ을 지켜라.",
    6169: "예!",
    6170: "먼저 내 죽음을 숨겨라.\n천하에 알려지면,\n사방의 적이 밀려들 것이다……",
    6171: "함부로 군사를 움직이지 마라.\n군사를 움직이면 내 죽음을\n반드시 적에게 들키고 말 것이다……",
    6172: "…………",
    6173: "오직 선정을 베푸는 데 마음을 쓰고,\n적이 오면 막으며,\n적이 물러가면 쫓지 말고 수비를 굳혀라.",
    6174: "그렇게 3년만 버티면,\n적은 저절로 \x1bCB다케다 가문\x1bCZ에 굴복할 것이다.",
    6175: "(3년이라……\n　과연 \x1bCA노부나가\x1bCZ가 기다려 줄까?)",
    6176: "위급할 때를 대비해 \x1bCC에치고\x1bCZ와 우호를 맺어라.",
    6177: "에치고……\n\x1bCB[bs1448]\x1bCZ과 말씀이십니까!?",
    6178: "그래, \x1bCA[bm1448]\x1bCZ는 천하의 의로운 장수다.\n후후…… 적으로 돌리면 성가시기 짝이 없지만,\n아군이 되면 그만큼 믿음직한 자도 없다.",
    6179: "(이제 우리의 적은\n　\x1bCB[bs1448]\x1bCZ이 아니라는 뜻인가.)",
    6180: "내 유해는 \x1bCC스와\x1bCZ의 호수에 가라앉혀라.\n네 어머니도…… 그곳에 잠들어 있다……",
    6181: "예, 예!",
    6182: "(아버님께서\n　어머님을 기억하고 계셨구나……!)",
    6183: "\x1bCA겐시로\x1bCZ……\n\x1bCA겐시로\x1bCZ는 없느냐?",
    6184: "주군, 겐시로 여기 있습니다!",
    6185: "\x1bCC교토\x1bCZ에 오르지 못하고 죽는 것이 한스럽다……\n하지만 \x1bCB다케다\x1bCZ에는 아직 네가 있다.\n\x1bCB다케다\x1bCZ의 선봉…… 아카조나에가 있다……",
    6186: "\x1bCA겐시로\x1bCZ……\n\x1bCC세타\x1bCZ에 우리 \x1bCB다케다\x1bCZ의 깃발을 세워라……!",
    6187: "주군!",
    6188: "(아버님께서는 마지막에도 \x1bCA겐시로\x1bCZ인가……)",
    6189: "(이제 그런 건 됐다……\n　앞으로는 내가 다스릴 시대다.\n　내가 바로 다케다의 총령이다.)",
    6190: "　　　대저 타고난 골격이 좋으니,\n　　　연지 없이도 절로 풍류롭다.",
    6191: "이 사세구를 남기고,\n가이의 호랑이 \x1bCA[b1251]\x1bCZ은 세상을 떠났다.",
    6192: "\x1bCA신겐\x1bCZ이 유언으로 말한 ‘\x1bCC세타\x1bCZ’는\n\x1bCC시가현\x1bCZ을 흐르는 \x1bCC세타강\x1bCZ의 다리……\n\x1bCC교토\x1bCZ로 들어가는 길목을 뜻한다고 한다.",
    6193: "눈부신 전공을 수없이 세우고도,\n상경만은 이루지 못한 한이\n그 마지막 말에 배어 있다……",
    6194: "\x1bCC미카와국\x1bCZ·\x1bCC요시다주쿠\x1bCZ――",
    6195: "이런, 무사님.\n어서 오십시오.",
    6196: "주인장, 나를 기억하나?",
    6197: "……글쎄요?\n어디서 뵈었습니까?",
    6198: "후후……\n기억하지 못해도 무리는 아니지.\n몰라볼 만큼 훌륭해졌으니 말이야……",
    6199: "과거 \x1bCA도도 다카토라\x1bCZ는 낭인으로 여러 나라를\n떠돌던 시절 이 가게에 들른 적이 있었다.",
    6200: "배, 배가…… 너무 고프다……",
    6201: "오, 거기 무사님!",
    6202: "응……?\n아, 아아, 나 말인가?",
    6203: "예, 바로 무사님입니다.\n긴 여행에 지치셨지요?\n어떻습니까, 저희 가게에서 떡이라도 드시지요.",
    6204: "맛있어서 볼이 떨어질 정도라고,\n이 근처에서는 소문이 자자합니다!",
    6205: "아니, 그게, 나는……\n볼이…… 떨어지는…… 떡……",
    6206: "부드러운 떡이 입안에서 녹아서,\n여행의 피로 따위 단숨에 날아갑니다!\n자자, 이쪽으로 오시지요!",
    6207: "\x1bCA다카토라\x1bCZ는 상인이 이끄는 대로 자리에 앉아,\n나오는 떡을 차례차례 먹어 치웠다.",
    6208: "맛있다! 이렇게 맛있는 떡은 처음이다!\n입안에서 사르르 녹아서……\n정말 볼이 떨어질 듯하군……",
    6209: "역시 무사님이십니다.\n참으로 호쾌하게 드시는군요!",
    6210: "(헉……!\n　떡이 너무 맛있어서,\n　기세를 타고 마구 먹어 버렸다……)",
    6211: "주인장, 사실 나는 무일푼이다!\n한 푼도 가진 것이 없다! 하지만 이 떡이\n너무 맛있어서…… 그만……",
    6212: "정말 미안하다!\n이번만 눈감아 줄 수 없겠나!",
    6213: "그랬군요…… 사정은 알겠습니다.\n그렇다면 지금은 값을 받지 않겠습니다.\n출세하신 뒤에 다시 받도록 하지요.",
    6214: "저, 정말인가!\n고맙기 그지없군……",
    6215: "무일푼이면 불편한 일이 많으시겠지요.\n얼마 되지는 않지만,\n노자와 저희 가게 떡을 챙겨 드리겠습니다.",
    6216: "그, 그럴 수는 없다!\n돈도 내지 않고 그런 것까지 받을 순 없어!",
    6217: "괜찮습니다, 신경 쓰지 마십시오.\n저희 흰 떡을 드신 무사님이\n훗날 성을 가진 다이묘가 되어 은혜를 갚으러……",
    6218: "흰 떡 ‘시로모치’가 성을 가진 ‘시로모치’로……\n말장난처럼 들리지만,\n그런 날을 꿈꾸며 기다리겠습니다……",
    6219: "미안하군……!\n나는 반드시 돌아오겠다!\n이 은혜는 잊지 않겠다!",
    6220: "나다!\n무일푼으로 떡을 먹고도,\n용서받았던 \x1bCA도도 다카토라\x1bCZ다!",
    6221: "……아, 그때 그분이군요!\n성함을 듣지 못했던 터라,\n큰 실례를 저질렀습니다.",
    6222: "그러고 보니 이름을 밝히지 않았군!\n뭐, 그런 것은 됐다.\n나도 주인장 덕분에 이제 성을 가진 다이묘다!",
    6223: "세상에……\n흰 떡이 정말 성주를 만들었군요!",
    6224: "그래서 오늘 은혜를 갚으러 왔다.\n우선 그래…… 이 돈으로,\n여기 있는 떡을 전부 사도록 하지!",
    6225: "이, 이렇게 큰돈은……\n도저히 받을 수 없습니다!",
    6226: "사양하지 마라.\n그때의 떡값과 노자를 돌려줄 뿐이다.",
    6227: "하지만 이토록 큰돈은……\n그렇다면 이렇게 하지요.",
    6228: "이 돈은 돌려드리겠습니다.\n그 대신,\n제 소원 하나를 들어주시겠습니까?",
    6229: "무엇이냐? 주인장의 부탁이라면,\n무엇이든 들어주마!",
    6230: "\x1bCA다카토라\x1bCZ 님께서 이곳을 지나실 때마다,\n저희 가게에 들러\n떡을 드셔 주셨으면 합니다.",
    6231: "그런 것으로 되겠느냐?\n그거라면 쉬운 일이지.\n가신도 잔뜩 데려올 테니 기다리고 있어라!",
    6232: "예, 언제든 기다리고 있겠습니다!",
    6233: "주인장의 따뜻한 행동에 감동한 \x1bCA다카토라\x1bCZ는 훗날,\n흰 원 셋의 ‘흰 떡 셋’을 깃발로 삼았다고 한다……",
    6234: "강담으로 유명한 ‘출세의 흰 떡’ 일화는\n어디까지가 꾸며 낸 이야기이고,\n어디까지가 사실인지 분명하지 않다……",
    6235: "천하를 제 것으로 삼으려 전횡하는 손위처남\n\x1bCA오다 노부나가\x1bCZ에 맞서 자신의 의를 관철하고자,\n결연히 일어선 \x1bCA아자이 나가마사\x1bCZ……",
    6236: "하지만 이제,\n그의 무운이 다하려 하고 있었다.",
    6237: "…………",
    6238: "\x1bCA나가마사\x1bCZ 님……",
    6239: "\x1bCA오이치\x1bCZ인가…… 여기서 무엇을 하느냐?\n아이들을 데리고 달아나라고 했을 텐데!",
    6240: "\x1bCA나가마사\x1bCZ 님.\n한 가지 여쭈어도 되겠습니까?",
    6241: "후, 무엇이냐?\n……내가 이승에서 답할 수 있는 것이라면,\n무엇이든 알려 주마.",
    6242: "\x1bCA나가마사\x1bCZ 님은,\n왜 오라버니와 전쟁을 하셨습니까?",
    6243: "물론 맹우인 \x1bCB아사쿠라 가문\x1bCZ에\n칼을 겨눈 오라버니를 내버려 두는 것은\n의에 어긋나는 일이었기 때문이다……",
    6244: "…………",
    6245: "……라고 말하고 싶지만, 진실은 아니다.\n내 마음과 무사의 혼은 바라고 있었다.\n\x1bCB아자이\x1bCZ와 이 \x1bCA나가마사\x1bCZ가 천하를 제패할 날을……",
    6246: "하지만 손위처남을 계속 따랐다면,\n수많은 휘하 장수 중 하나로 끝났겠지.\n그리 생각했기에 칼을 들었을 뿐이다……",
    6247: "……그 말씀을 들으니 안심이 됩니다.",
    6248: "안심……?",
    6249: "예.\n제가 \x1bCA나가마사\x1bCZ 님을 연모하는 마음……\n\x1bCA나가마사\x1bCZ 님께서 저를 아끼는 마음……",
    6250: "저는 그런 마음이\n\x1bCB아사쿠라\x1bCZ를 향한 의리보다도 못한 것인지,\n줄곧 걱정했습니다.",
    6251: "후, 후후…… 쓸데없는 걱정이다.\n오히려 내 야심은 그대를 아내로 맞은 날\n태어났으니 말이다!",
    6252: "기쁜 말씀입니다……\n그러니 제 사랑이\n\x1bCA나가마사\x1bCZ 님의 목숨을 빼앗는군요.",
    6253: "……그래.\n그대의 사랑에 바치는 것이라면,\n이 목숨도 아깝지 않다.",
    6254: "자, 이제 됐다……\n성을 나가라. 아이들을 부탁한다!",
    6255: "예, \x1bCA나가마사\x1bCZ 님……",
    6256: "어떤 위로도, 구원도 필요 없다……\n무사의 최후란\n그런 것이라 생각했다.",
    6257: "\x1bCA오이치\x1bCZ……\n그대를 만난 것은,\n더없는 행운이었다.",
    6258: "당주 \x1bCA아자이 나가마사\x1bCZ가 자결하면서,\n센고쿠 다이묘 \x1bCB아자이 가문\x1bCZ은 멸망했다.",
    6259: "하지만 그 핏줄은 성이 함락되기 직전 빠져나와,\n\x1bCA노부나가\x1bCZ의 보호를 받은 \x1bCA오이치\x1bCZ와 딸들을 통해,\n후세로 이어지게 된다……",
    6260: "에치고 슈고 \x1bCB우에스기 가문\x1bCZ은\n간토 간레이 \x1bCB야마노우치 우에스기 가문\x1bCZ의 분가로,\n종가에 여러 양자를 보낸 유력 가문이었다.",
    6261: "슈고로서 46년 동안 \x1bCC에치고\x1bCZ를 다스린\n\x1bCA우에스기 후사사다\x1bCZ가 죽은 뒤,\n슈고다이 \x1bCA나가오 요시카게\x1bCZ·\x1bCA다메카게\x1bCZ에게 밀려,\n점차 쇠망의 길로 접어들었다.",
    6262: "마지막 당주 \x1bCA사다자네\x1bCZ는\n\x1bCA나가오 하루카게\x1bCZ와 아우 \x1bCA가게토라\x1bCZ를 중재하는 등,\n여전히 그 권위를 존중받았지만……",
    6263: "에치고 슈고직을 물려줄 아들이 없어,\n홀로 조용히\n마지막 때를 맞이하고 있었다.",
    6264: "이 나라는 \x1bCA[b1448]\x1bCZ이 타고난 전쟁 재능을 발휘해,\n국인들을 거느리고 있다.\n이제 슈고 따위는 필요 없을지도 모르겠군……",
    6265: "나에게는 자식도 없다.\n에치고 슈고 \x1bCB우에스기 가문\x1bCZ은 연기처럼\n사라지겠지만…… 그것도 좋겠지.",
    6266: "그러고 보니 \x1bCA다테 다네무네\x1bCZ 공에게서 양자를\n받기로 한 이야기도 있었지. \x1bCB다테 가문\x1bCZ 안의 다툼으로,\n흐지부지되고 말았지만……",
    6267: "이제 와서는 모든 것이 그립구나……",
    6268: "\x1bCA사다자네\x1bCZ의 죽음으로 \x1bCB에치고 우에스기 가문\x1bCZ은 단절됐다.\n\x1bCC에치고\x1bCZ는 슈고가 없는 채로 슈고다이 \x1bCA나가오 가게토라\x1bCZ가\n계속 다스리게 된다……",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    6142: ["mikatagahara_battle_name_requires_glossary_review"],
    6153: ["jin_daiko_term_rendered_as_camp_drum_requires_style_review"],
    6157: ["yamagata_masakage_name_requires_glossary_review"],
    6158: ["empty_fort_strategy_term_requires_glossary_review"],
    6178: ["gisho_honorific_rendered_as_righteous_general_requires_style_review"],
    6185: ["akazonae_term_requires_glossary_review"],
    6186: ["seta_place_name_requires_glossary_review"],
    6190: ["shingen_death_poem_requires_poetry_review"],
    6192: ["seta_bridge_and_shiga_names_require_glossary_review"],
    6194: ["yoshida_juku_place_term_requires_glossary_review"],
    6199: ["todo_takatora_name_requires_glossary_review"],
    6218: ["shiromochi_castle_holder_pun_requires_style_review"],
    6233: ["takatora_white_mochi_banner_requires_history_review"],
    6234: ["shusse_no_shiromochi_tale_title_requires_glossary_review"],
    6246: ["yoriki_status_term_requires_glossary_review"],
    6256: ["samurai_death_religious_nuance_requires_style_review"],
    6260: ["echigo_shugo_and_kanto_kanrei_titles_require_glossary_review"],
    6261: ["fusasada_yoshikage_tamekage_names_require_glossary_review"],
    6264: ["kunishu_term_requires_glossary_review"],
    6268: ["echigo_shugodai_governance_term_requires_history_review"],
}

PREVIOUS_ARTIFACT_PINS = {
    **shared.PREVIOUS_ARTIFACT_PINS,
    "evidence/alignment_evidence.v0.24.json": (
        "6AD7755A3DFE83545EE9F3F94ADBCE56B4ECD06E4A4ACDAFBACDB18FBC0E1FFE"
    ),
    "public/msgev_ko_historical_events_6020_6141.v0.24.json": (
        "C9FC4A48DE817074F33751BACE29C5A86C46B1008147AEFEE8A9B29CC9EB06C3"
    ),
    "review/review_index.v0.24.json": (
        "3F82FEC995A2AE0D6BD70D487875DEA076EB9010A699A081E3C83CB352DB4F12"
    ),
    "validation.v0.24.json": (
        "9E22D24DE965117384ED890D5ACD9520E8A3C25C9A08F7A2E7AACC8A6382993E"
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
        6141,
        6142,
        6163,
        6164,
        6193,
        6194,
        6234,
        6235,
        6259,
        6260,
        6268,
        6269,
    )
    evidence["schema"] = "nobu16.kr.event-dialogue-alignment-evidence.v25"
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
    review["schema"] = "nobu16.kr.event-dialogue-review-index.v25"
    validation["schema"] = "nobu16.kr.event-dialogue-generation-validation.v25"
    validation["font_integration"].pop(
        "current_font_or_installer_must_not_include_batch24", None
    )
    validation["font_integration"][
        "current_font_or_installer_must_not_include_batch25"
    ] = True
    integrity = validation["preexisting_integrity"]
    integrity["dialogue_v01_v24_artifacts_before"] = integrity.pop(
        "dialogue_v01_v23_artifacts_before"
    )
    integrity["dialogue_v01_v24_artifacts_after"] = integrity.pop(
        "dialogue_v01_v23_artifacts_after"
    )
    safety = validation["safety"]
    safety.pop(
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_v14_v15_v16_v17_v18_v19_v20_v21_v22_v23_artifacts_modified",
        None,
    )
    safety[
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_v14_v15_v16_v17_v18_v19_v20_v21_v22_v23_v24_artifacts_modified"
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
