#!/usr/bin/env python3
"""Build source-free Korean historical event dialogue batch14 (4691-4838)."""

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
import build_event_dialogue_batch13 as shared  # noqa: E402


BATCH_ID = "msgev_historical_events_4691_4838.v0.14"
OVERLAY_NAME = "msgev_ko_historical_events_4691_4838.v0.14.json"
EVIDENCE_NAME = "alignment_evidence.v0.14.json"
REVIEW_NAME = "review_index.v0.14.json"
VALIDATION_NAME = "validation.v0.14.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 4691
SCOPE_END = 4838
EXCLUDED_INTERNAL_IDS: tuple[int, ...] = ()
BRACKET_TOKEN_RE = shared.BRACKET_TOKEN_RE

EVENTS = (
    {
        "event_id": "death_of_takeda_nobushige",
        "title_ko": "다케다 노부시게의 전사",
        "start_id": 4691,
        "end_id": 4719,
        "selected_count": 29,
    },
    {
        "event_id": "amakasu_rearguard_against_baba",
        "title_ko": "아마카스 가게모치의 후위전",
        "start_id": 4720,
        "end_id": 4750,
        "selected_count": 31,
    },
    {
        "event_id": "kagetora_becomes_kanto_kanrei",
        "title_ko": "가게토라의 간토 간레이 취임",
        "start_id": 4751,
        "end_id": 4768,
        "selected_count": 18,
    },
    {
        "event_id": "yoshiyori_claims_chunagon_title",
        "title_ko": "아네가코지 요시요리의 주나곤 자칭",
        "start_id": 4769,
        "end_id": 4799,
        "selected_count": 31,
    },
    {
        "event_id": "nobunaga_letter_to_nene",
        "title_ko": "노부나가가 네네에게 보낸 편지",
        "start_id": 4800,
        "end_id": 4810,
        "selected_count": 11,
    },
    {
        "event_id": "kuroda_kanbei_enters_turbulent_age",
        "title_ko": "구로다 간베에의 난세 출진",
        "start_id": 4811,
        "end_id": 4813,
        "selected_count": 3,
    },
    {
        "event_id": "kiyosu_alliance",
        "title_ko": "오다·마쓰다이라 기요스 동맹",
        "start_id": 4814,
        "end_id": 4838,
        "selected_count": 25,
    },
)

TRANSLATIONS: dict[int, str] = {
    4691: (
        "딱따구리 전법을 \x1bCA[b1448]\x1bCZ에게 간파당해,\n"
        "\x1bCB다케다군\x1bCZ 전체가 무너지는 가운데,\n"
        "홀로 분전하는 부대가 있었다."
    ),
    4692: "바로 \x1bCA[b1251]\x1bCZ의 동생 \x1bCA덴큐 노부시게\x1bCZ의 부대였다.",
    4693: "누구 없느냐!",
    4694: "예, 여기 있습니다!",
    4695: "주군께 전하라.",
    4696: (
        "우리는 이제 \x1bCB에치고군\x1bCZ으로 돌격해 전사할 것이다!\n"
        "우리가 시간을 버는 동안 승리할 방책을 세우시고,\n"
        "절대로 구하려 하지 마시라 전해라."
    ),
    4697: "예!",
    4698: (
        "그리고 이 호로와 머리카락을 아들 \x1bCA노부토요\x1bCZ에게 전하라.\n"
        "호로에는 주군께서 친히 경문을 쓰셨으니,\n"
        "가보로 삼으라고 해라."
    ),
    4699: (
        "머리카락은 내 것이다.\n"
        "아버지로서 해 준 일은 없지만……\n"
        "주군께 충성을 바치는 것이 내 삶이었다."
    ),
    4700: "주군……!",
    4701: "가라. 반드시 내 말을 전해야 한다.",
    4702: "예!",
    4703: "모두 들어라!",
    4704: (
        "우리는 이제 \x1bCB[bs1448] 군\x1bCZ을 무너뜨린다.\n"
        "적장을 보면 반드시 베되,\n"
        "잡병은 놓아주고 쓸데없는 살생은 하지 마라."
    ),
    4705: (
        "나무하치만 대보살이시여!\n"
        "저를 \x1bCA[bm1448]\x1bCZ에게 이끌어 주소서.\n"
        "그 목으로 주군의 은혜에 보답하고 싶습니다."
    ),
    4706: (
        "자, 따르라. 고슈의 용사들이여!\n"
        "\x1bCA[b1251]\x1bCZ의 동생 \x1bCA다케다 사마노스케 노부시게\x1bCZ와 함께,\n"
        "저승길에 오르자!"
    ),
    4707: "\x1bCA다케다 노부시게\x1bCZ는 \x1bCC가와나카지마\x1bCZ에서 전사했다.\n향년 서른일곱이었다.",
    4708: (
        "그는 총명하고 침착하며 겸손하고 세심했고,\n"
        "무략과 용기, 위엄을 두루 갖춰,\n"
        "무사라면 누구나 동경했다고 한다."
    ),
    4709: "\x1bCC가와나카지마\x1bCZ·\x1bCB다케다군\x1bCZ 본진――",
    4710: "아룁니다!\n\x1bCA덴큐\x1bCZ 님께서 전사하셨습니다!",
    4711: "뭐, 뭐라고!?\n그럴 리가……!\n미안하다…… \x1bCA노부시게\x1bCZ…… 미안해……",
    4712: "내가 어리석어 너를 희생시켰구나.\n미안하다……",
    4713: "주군, 정신을 차리십시오!",
    4714: "알고 있다!\n\x1bCA노부시게\x1bCZ의 목숨을 헛되게 할 수 없다.\n반드시 전세를 되돌리겠다!",
    4715: "하지만……\n이 눈물만큼은 나도\n멈출 수가 없구나……",
    4716: "(\x1bCA노부시게\x1bCZ……\n　이제 내 마음을 아는 이가\n　또 한 사람 사라졌구나……)",
    4717: "(천하를 뜻하는 길이 이토록 험하고,\n　슬픈 것이었던가……)",
    4718: "어떤 사서에는 이렇게 적혀 있다.\n‘\x1bCA노부시게\x1bCZ는 문·무·예·의를 갖추었다.’",
    4719: (
        "온갖 미덕을 갖춘 이 부장의 죽음은,\n"
        "\x1bCB다케다 가문\x1bCZ과 \x1bCA[bm1251]\x1bCZ에게\n"
        "커다란 타격이 되었다."
    ),
    4720: (
        "\x1bCB우에스기군\x1bCZ이 \x1bCC가와나카지마\x1bCZ에서 철수할 때,\n"
        "후위를 맡은 이는 \x1bCA아마카스 가게모치\x1bCZ였다."
    ),
    4721: (
        "\x1bCA가게모치\x1bCZ는 \x1bCC사이가와\x1bCZ 강가에 진을 치고,\n"
        "강을 건너 후퇴하는 \x1bCB우에스기군\x1bCZ을 지켰다."
    ),
    4722: "적의 습격입니다!",
    4723: "왔나……\n모두 버텨라!\n\x1bCC에치고\x1bCZ로 돌아가는 아군을 반드시 지켜라!",
    4724: "저자가 \x1bCA아마카스 오미노카미\x1bCZ인가……\n좋은 목이군. 내가 받아 가겠다.",
    4725: "쳇…… \x1bCA바바 미노\x1bCZ인가……\n성가신 적이 왔군.",
    4726: (
        "오니미노라 불린 \x1bCA바바 노부하루\x1bCZ가 맹공을 퍼부었지만,\n"
        "\x1bCA가게모치\x1bCZ는 가까스로 이를 물리쳤다."
    ),
    4727: "과연, 제법 하는군.\n일단 물러난다!",
    4728: "몇 시간 뒤――",
    4729: "적의 습격입니다!",
    4730: "모두 버텨라!\n이제 곧 아군이 모두 강을 건넌다!",
    4731: "흠, 아직 그 목이 붙어 있었나.\n그럼 고맙게 받아 가마!",
    4732: "또 왔나……\n정말 끈질긴 녀석이군.",
    4733: "진형을 가다듬은 \x1bCA가게모치\x1bCZ는,\n다시 한번 \x1bCA노부하루\x1bCZ를 물리치는 데 성공했다.",
    4734: "\x1bCA바바\x1bCZ가 물러난다.\n지금 바로 진형을 가다듬어라!",
    4735: "두 번 있는 일은\n세 번도 있다고 하니까……",
    4736: "몇 시간 뒤――",
    4737: "\x1bCA가게모치\x1bCZ의 예상대로,\n\x1bCA바바 노부하루\x1bCZ가 세 번째 공격을 시작했다.",
    4738: "호오……\n진형이 잘 갖춰졌군.\n우리 공격을 읽고 있었나?",
    4739: "글쎄……\n나는 그저 속담을 믿었을 뿐이야.",
    4740: (
        "\x1bCA노부하루\x1bCZ의 습격을 예상한 \x1bCA가게모치\x1bCZ는,\n"
        "이번에도 훌륭하게 \x1bCA바바 부대\x1bCZ를 격퇴했다."
    ),
    4741: "몇 시간 뒤――",
    4742: "아무래도,\n주변에는 적이 없는 듯합니다.",
    4743: "이번에는 포기했겠지.\n아군도 충분히 멀어졌을 테니,\n우리도 철수한다!",
    4744: (
        "임무를 마쳤다고 여긴 \x1bCA가게모치\x1bCZ가\n"
        "무방비로 강을 건너던 도중,\n"
        "갑자기 화살 소리가 귓가를 스쳤다."
    ),
    4745: "서, 설마……",
    4746: (
        "후후…… 두 번 있는 일은 세 번도 있다.\n"
        "그렇다면 세 번 있는 일은 네 번도 있지.\n"
        "그렇게 생각하지 않나, \x1bCA아마카스\x1bCZ?"
    ),
    4747: "큭……\n그렇게 생각했다면,\n이토록 꼴사납게 당하지 않았을 텐데!",
    4748: "하하하! 맞는 말이다!\n그럼…… 그 목을 두고 가라!",
    4749: (
        "\x1bCA가게모치\x1bCZ는 간발의 차로 달아났지만,\n"
        "\x1bCA바바 부대\x1bCZ의 공격에 \x1bCA아마카스 부대\x1bCZ는 완전히 무너져,\n"
        "많은 사상자를 냈다."
    ),
    4750: "\x1bCA바바 노부하루\x1bCZ의 집념이 가져온,\n인간 심리의 허를 찌른 승리였다.",
    4751: (
        "늘 \x1bCB호조씨\x1bCZ의 압력에 시달리던 간토 제장들은\n"
        "\x1bCB호조\x1bCZ 영지 깊숙이 진격한 \x1bCA가게토라\x1bCZ를\n"
        "잇달아 지지하고 나섰다."
    ),
    4752: "이제 \x1bCA가게토라\x1bCZ는 \x1bCC간토\x1bCZ의 구세주가 되었다.",
    4753: (
        "이 상황에서 간토 간레이 \x1bCA우에스기 노리마사\x1bCZ는\n"
        "무력한 자신에게 자격이 없다고 판단하고,\n"
        "간레이직을 \x1bCA가게토라\x1bCZ에게 넘기기로 했다."
    ),
    4754: (
        "이를 예상이라도 했는지,\n"
        "\x1bCA가게토라\x1bCZ는 순순히 받아들여,\n"
        "간토 간레이직을 계승했다."
    ),
    4755: (
        "\x1bCA가게토라\x1bCZ의 간토 간레이 취임식은\n"
        "\x1bCC가마쿠라\x1bCZ의 \x1bCC쓰루가오카 하치만구\x1bCZ에서 열렸다.\n"
        "이는 \x1bCB호조 가문\x1bCZ을 도발하는 동시에,"
    ),
    4756: (
        "가마쿠라 막부 이래 무문의 신을 숭배해 온 곳에서\n"
        "취임식을 열어, \x1bCA가게토라\x1bCZ의 간레이 계승에\n"
        "정당성을 더하려는 뜻도 있었다."
    ),
    4757: "\x1bCA가게토라\x1bCZ 님,\n간토 간레이 취임을 축하드립니다.",
    4758: "\x1bCA가게이에\x1bCZ, 나는 이를 계기로 이름을 바꾸겠다.",
    4759: "과연, ‘\x1bCB우에스기\x1bCZ’ 성을 이으시는군요.",
    4760: "그뿐만이 아니다.",
    4761: (
        "\x1bCA노리마사\x1bCZ 공의 이름 한 글자를 받아,\n"
        "‘\x1bCA마사토라\x1bCZ’라 하겠다.\n"
        "이제부터 나는 \x1bCA우에스기 마사토라\x1bCZ다."
    ),
    4762: "……알겠습니다.",
    4763: "\x1bCA노리마사\x1bCZ 공에게 한 글자를 받는 것이\n쓸데없다고 생각하는구나.",
    4764: "아, 아닙니다……\n당치도 않습니다.",
    4765: "이름을 바꿔도 내 무용은 달라지지 않는다.\n일단 따라 주면 그만이지.",
    4766: "그렇습니다.\n이제 \x1bCC간토\x1bCZ에서 벌이는 모든 싸움은\n대의를 위한 싸움이 됩니다.",
    4767: "바로 코앞에서 이런 의식을 치렀으니,\n\x1bCB호조\x1bCZ도 체면을 구겼겠지요.",
    4768: "이렇게 되리라 예상했다.\n사욕으로 \x1bCC간토\x1bCZ를 짓누르는 \x1bCB호조\x1bCZ를……\n간토 간레이의 이름으로 멸하겠다.",
    4769: (
        "\x1bCC히다\x1bCZ는 남북조 시대 공가인 \x1bCB아네가코지 가문\x1bCZ이\n"
        "고쿠시를 맡고, 막부가 슈고로 임명한 \x1bCB교고쿠 가문\x1bCZ과\n"
        "공존하며 분할 통치하고 있었다."
    ),
    4770: (
        "전국시대에 들어서자 \x1bCB교고쿠씨\x1bCZ의 지류로,\n"
        "\x1bCC히다\x1bCZ를 맡던 \x1bCB미키 가문\x1bCZ은\n"
        "\x1bCB아네가코지 가문\x1bCZ의 이름을 빼앗으려 획책했다."
    ),
    4771: (
        "그리고 \x1bCB미키 가문\x1bCZ의 적자 \x1bCA미키 요리쓰나\x1bCZ가\n"
        "‘\x1bCA아네가코지 요리쓰나\x1bCZ’로 개명한 뒤,\n"
        "삼 년의 세월이 흘렀다."
    ),
    4772: "\x1bCB미키 가문\x1bCZ 당주 \x1bCA미키 요시요리\x1bCZ가 바라던\n주나곤 임명은 아직 이루어지지 않았다.",
    4773: "어째서냐……\n\x1bCA요리쓰나\x1bCZ, 너는 어째서라고 생각하느냐?",
    4774: "무엇이 어째서란 말씀이십니까?",
    4775: "어째서 주나곤이 되지 못하는 것 같으냐?\n이제 한 걸음만 남았다고 생각하는데.",
    4776: "주나곤은 구교, 곧 종3위에 해당하는\n의정관입니다…… 지방 무사가\n그리 쉽게 임명될 자리가 아닙니다.",
    4777: "그렇다면,\n나도 \x1bCB아네가코지\x1bCZ를 칭할 수밖에 없겠군.",
    4778: "아버님…… 제 말을 듣고 계십니까?",
    4779: "좋다, 이제부터 나는 \x1bCA아네가코지 요시요리\x1bCZ다!\n이러면 주나곤이 될 수 있겠지!",
    4780: "아버님……",
    4781: (
        "본래 \x1bCC교토\x1bCZ의 \x1bCB아네가코지 가문\x1bCZ은 공가의 격으로 따지면\n"
        "‘\x1bCB우린케\x1bCZ’에 해당한다. 극관, 곧 최고 관직을\n"
        "다이나곤으로 삼는 가문이다."
    ),
    4782: (
        "물론 참칭에 불과해 실효는 없지만,\n"
        "다이나곤 아래인 주나곤직을 원한 \x1bCA요시요리\x1bCZ가\n"
        "\x1bCB아네가코지\x1bCZ 성을 칭한 것도 근거 없지는 않았다……"
    ),
    4783: "……하아.\n성을 바꿔도 임명되지는 않는가……",
    4784: "아버님, 몸이 불편하십니까?",
    4785: "흥, 그런 게 아니다……!\n이름을 바꾼 지도 오래되었거늘……\n하아…… 주나곤……",
    4786: "아버님!",
    4787: "왜, 왜 그리 큰소리를 내느냐.",
    4788: "저는 이렇게 생각합니다.\n지금은 힘이 곧 말을 하는 난세입니다.",
    4789: "원하는 것은 자기 손으로 움켜쥔다.\n그렇지 않습니까?",
    4790: "으, 으음……\n그렇지.",
    4791: "그렇다면 아버님도 원하시는 것은\n스스로 손에 넣으시면 됩니다.",
    4792: "……그랬지.\n좋아!\n이제부터 나는 \x1bCA아네가코지 주나곤 요시요리\x1bCZ다!",
    4793: "음, 음……\n……예?",
    4794: "지금은 힘이 곧 말을 하는 난세……\n다이묘들은 제멋대로 관위를 자칭하지.",
    4795: "예, 예.\n그렇기는 합니다만.",
    4796: "그러니 나도 우선 자칭하겠다!\n그리고 언젠가 그 관위에 걸맞은\n다이묘가 되어 보이마!",
    4797: "……\n어떠냐, \x1bCA요리쓰나\x1bCZ.\n내 생각이 틀렸느냐?",
    4798: "……아닙니다. 훌륭한 결심입니다.",
    4799: "그리하여,\n‘\x1bCA아네가코지 요시요리\x1bCZ’로 이름을 바꾼 \x1bCA미키 요시요리\x1bCZ는,\n세력 확장에 매진했다.",
    4800: "\x1bCB오다 가문\x1bCZ 본거――",
    4801: "\x1bCA[b754]\x1bCZ는 당시로서는 보기 드문 연애결혼으로\n\x1bCA네네\x1bCZ를 아내로 맞았다.",
    4802: "하지만 \x1bCA[bm754]\x1bCZ는 바람기가 있어,\n사랑하는 아내 말고도 여러 여인과 염문을 뿌렸다.",
    4803: "\x1bCA[bm754]\x1bCZ와 \x1bCA네네\x1bCZ 사이에 아이가 없어,\n어떻게든 후계자를 얻으려 다른 여인들에게\n손을 댔다는 이야기도 있지만……",
    4804: "\x1bCA네네\x1bCZ…… 네가 주군께 고자질했느냐?\n내가 바람을 피웠다고 말이야.\n주군께 호되게 꾸중을 들었다.",
    4805: "당신! 혼례 때 하신 말씀을\n잊으신 건 아니겠지요?\n내게 여인은 너 하나뿐이라고……",
    4806: "으음……\n내가 그런 말을 했던가?",
    4807: "하·셨·습·니·다!\n그때 바람을 피우면 주군께 이르겠다고\n저도 분명 말씀드렸지요?",
    4808: "이런, \x1bCA네네\x1bCZ에게는 당해 낼 수가 없군……",
    4809: "주군 \x1bCA오다 노부나가\x1bCZ가 보낸 편지에는,\n\x1bCA네네\x1bCZ가 \x1bCA[bm754]\x1bCZ의 바람기로 고민하는 것을 위로한\n내용이 남아 있다……",
    4810: "‘너는 대머리 쥐에게 과분한 여인이다’――\n편지는 \x1bCA[bm754]\x1bCZ를 그렇게 표현하고,\n\x1bCA네네\x1bCZ를 격려하는 말로 채워져 있었다.",
    4811: "‘무에 기대지 않고 지혜로 일어선다.’\n그 뜻을 가슴에 품고, 이제 이 사내는\n전란의 시대로 나아가려 했다――",
    4812: (
        "\x1bCA구로다 모토타카\x1bCZ의 적자 \x1bCA고데라 간베에 요시타카\x1bCZ는 원복을\n"
        "치르며 \x1bCA고데라 마사모토\x1bCZ의 성을 받았지만, 주군을\n"
        "꺼려 본래의 \x1bCB구로다\x1bCZ 성도 함께 사용했다……"
    ),
    4813: "훗날 재능을 알아본 \x1bCA하시바 히데요시\x1bCZ를 만나,\n희대의 군사로 날개를 펼치게 되는――\n\x1bCA구로다 조스이\x1bCZ, 바로 그 사람이다……",
    4814: "\x1bCA이마가와 요시모토\x1bCZ가 오케하자마에서 전사한 일은,\n오랜 굴종을 강요당한 \x1bCB[bs1871] 가문\x1bCZ에\n천재일우의 기회였다.",
    4815: "그 기회를 놓치지 않고,\n\x1bCA[b1871]\x1bCZ는 선조 대대로 이어 온 땅\n\x1bCC미카와 오카자키성\x1bCZ에서 독립했다.",
    4816: (
        "그러나 \x1bCB이마가와 가문\x1bCZ은 \x1bCC도토미\x1bCZ와 \x1bCC스루가\x1bCZ에 건재했고,\n"
        "한편 \x1bCA요시모토\x1bCZ를 꺾은 \x1bCC오와리\x1bCZ의 \x1bCB오다 가문\x1bCZ은 기세를 올렸다.\n"
        "\x1bCB[bs1871] 가문\x1bCZ에는 양쪽을 함께 상대할 힘이 없었다."
    ),
    4817: "\x1bCC오와리\x1bCZ·\x1bCC기요스성\x1bCZ――",
    4818: "기다리고 있었다, \x1bCA다케치요\x1bCZ.\n……아니, 이제는 \x1bCA[bm1871]\x1bCZ인가.",
    4819: "\x1bCA노부나가\x1bCZ 님, 참으로 오랜만입니다.\n늦게 찾아뵌 점을 사과드립니다.",
    4820: "그러게 말이다. \x1bCB이마가와\x1bCZ에게서 독립한 건 좋다만,\n왜 곧바로 내게 오지 않았지?",
    4821: "듣자 하니 \x1bCA요시모토\x1bCZ의 전사 소식을 들었을 때,\n할복하려 했다면서?",
    4822: "그, 그것은……",
    4823: "뭐, 됐다.\n오늘 이곳에 왔다는 것은,\n\x1bCB이마가와\x1bCZ와 완전히 결별하겠다는 뜻이겠지?",
    4824: "역시 \x1bCA노부나가\x1bCZ 님은 모두 꿰뚫어 보시는군요.\n이제 \x1bCB[bs1871]\x1bCZ이 살아갈 길은\n\x1bCB오다 가문\x1bCZ과 협력하는 것뿐입니다.",
    4825: "나와 손을 잡으면 아비의 원수라 여기는 \x1bCA이마가와 우지자네\x1bCZ가\n당장 쳐들어올지도 모른다.",
    4826: "가신 중에도 아직 \x1bCB이마가와\x1bCZ의 은혜를 잊지 못한 자가\n많겠지…… 나와 손잡는 방침으로 가문을\n하나로 모을 수 있겠느냐?",
    4827: "걱정하지 않으셔도 됩니다.\n저희는 이미 \x1bCB이마가와\x1bCZ와 싸울 각오를 마쳤습니다.\n\x1bCB오다 가문\x1bCZ의 도움만 있다면……",
    4828: "현명한 판단이다. 때도 제대로 읽었군.\n네 그런 점을 높이 사는 것이다,\n\x1bCA다케치요\x1bCZ.",
    4829: "나는 반드시 천하를 얻는다!\n하지만 내 다음 천하인은……\n어쩌면 네가 될지도 모르겠군.",
    4830: "예…… 처, 천하 말씀이십니까?",
    4831: "그래, 천하다. 천하포무다!\n삼베처럼 어지러운 세상의 전쟁을 끝내려면,\n내가 천하를 얻는 수밖에 없다!",
    4832: "그토록 멀리 내다보고 계셨습니까……\n황송합니다. 하지만 제가 다음 천하인이라니,\n저를 너무 높이 평가하셨습니다.",
    4833: "아니, 나는 네 그릇을 그만큼 높이 산다.\n내가 천하인이 되는 그날까지,\n네가 내 등을 지켜 줘야겠다.",
    4834: "예, 맡겨 주십시오!\n반드시 기대에 보답하겠습니다.",
    4835: "(어디까지나 정직한 사내로군……\n　하지만 바로 그 ‘성실함’이\n　네 무서운 재능이다……)",
    4836: "이때 맺은 \x1bCA오다 노부나가\x1bCZ와 \x1bCA[b1871]\x1bCZ의 맹약은,\n훗날 기요스 동맹이라 불리는 혼인 동맹으로 발전했다.",
    4837: "동시에 \x1bCA모토야스\x1bCZ는 \x1bCA이에야스\x1bCZ로 이름을 바꾸었다.\n옛 주군 \x1bCA이마가와 요시모토\x1bCZ에게 받은 이름과 결별하고,\n\x1bCA노부나가\x1bCZ와 함께할 미래를 택했음을 드러냈다.",
    4838: "\x1bCA[bm1871]\x1bCZ는 그 성실함으로\n한결같이 \x1bCA노부나가\x1bCZ에게 협력을 아끼지 않았고,\n\x1bCA노부나가\x1bCZ도 계속 그에 보답했다.",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    4692: ["tenkyu_nobushige_title_requires_glossary_review"],
    4698: ["horo_cloak_and_inscription_require_historical_review"],
    4705: ["hachiman_daibosatsu_prayer_requires_style_review"],
    4706: ["samano_suke_title_requires_glossary_review"],
    4724: ["omi_no_kami_title_requires_glossary_review"],
    4725: ["baba_mino_and_onimino_epithets_require_glossary_review"],
    4755: ["tsurugaoka_hachimangu_name_requires_glossary_review"],
    4761: ["kagetora_to_masatora_name_change_requires_historical_review"],
    4781: ["urinke_and_court_rank_terms_require_glossary_review"],
    4810: ["bald_rat_letter_paraphrase_requires_historical_review"],
    4812: ["kodera_kanbei_yoshitaka_name_and_dual_surname_require_review"],
    4813: ["meihakuraku_metaphor_and_kuroda_josui_name_require_review"],
    4836: ["kiyosu_alliance_term_requires_glossary_review"],
}

PREVIOUS_ARTIFACT_PINS = {
    **shared.PREVIOUS_ARTIFACT_PINS,
    "evidence/alignment_evidence.v0.13.json": (
        "2BFBAF33FF4F7631AA357DA9DCB75CACEC3AE623886B2377EE3EAEFDC78364C9"
    ),
    "public/msgev_ko_historical_events_4557_4690.v0.13.json": (
        "DF52C23A3F94971F7B8D308DAE787C69951F08F3B879B9851A60327180E6B87E"
    ),
    "review/review_index.v0.13.json": (
        "5493740F875F8AFED7D9FE3CAB3CF8FD389D0C805CFDB9B111783DE0D7E3493D"
    ),
    "validation.v0.13.json": (
        "43E633DA4542A046123CC2F50C5206379C06DF8F8F1029FDFD765FADE79948FD"
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
    if len(ids) != 148 or ids != sorted(TRANSLATIONS):
        raise ValueError("batch14 ids are not the exact 148 displayed entries")
    return ids


def event_for(entry_id: int) -> str:
    matches = [
        event["event_id"]
        for event in EVENTS
        if event["start_id"] <= entry_id <= event["end_id"]
    ]
    if len(matches) != 1:
        raise ValueError(f"id {entry_id} does not map to one batch14 event group")
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
        4690,
        4691,
        4719,
        4720,
        4750,
        4751,
        4768,
        4769,
        4799,
        4800,
        4810,
        4811,
        4813,
        4814,
        4838,
        4839,
    )
    evidence["schema"] = "nobu16.kr.event-dialogue-alignment-evidence.v14"
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
    review["schema"] = "nobu16.kr.event-dialogue-review-index.v14"
    validation["schema"] = "nobu16.kr.event-dialogue-generation-validation.v14"
    validation["font_integration"].pop(
        "current_font_or_installer_must_not_include_batch13", None
    )
    validation["font_integration"][
        "current_font_or_installer_must_not_include_batch14"
    ] = True
    integrity = validation["preexisting_integrity"]
    integrity["dialogue_v01_v13_artifacts_before"] = integrity.pop(
        "dialogue_v01_v12_artifacts_before"
    )
    integrity["dialogue_v01_v13_artifacts_after"] = integrity.pop(
        "dialogue_v01_v12_artifacts_after"
    )
    safety = validation["safety"]
    safety.pop(
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_artifacts_modified",
        None,
    )
    safety[
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_artifacts_modified"
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
