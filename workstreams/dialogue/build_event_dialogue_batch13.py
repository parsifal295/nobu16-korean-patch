#!/usr/bin/env python3
"""Build source-free Korean historical event dialogue batch13 (4557-4690)."""

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
import build_event_dialogue_batch12 as shared  # noqa: E402


BATCH_ID = "msgev_historical_events_4557_4690.v0.13"
OVERLAY_NAME = "msgev_ko_historical_events_4557_4690.v0.13.json"
EVIDENCE_NAME = "alignment_evidence.v0.13.json"
REVIEW_NAME = "review_index.v0.13.json"
VALIDATION_NAME = "validation.v0.13.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 4557
SCOPE_END = 4690
EXCLUDED_INTERNAL_IDS: tuple[int, ...] = ()
BRACKET_TOKEN_RE = shared.BRACKET_TOKEN_RE

EVENTS = (
    {
        "event_id": "hisahide_rebuilds_shigisan_castle",
        "title_ko": "마쓰나가 히사히데의 시기산성 축성",
        "start_id": 4557,
        "end_id": 4569,
        "selected_count": 13,
    },
    {
        "event_id": "hojo_faces_kagetora_kanto_campaign",
        "title_ko": "호조 가문과 가게토라의 간토 원정",
        "start_id": 4570,
        "end_id": 4591,
        "selected_count": 22,
    },
    {
        "event_id": "hojo_uesugi_peace_against_takeda",
        "title_ko": "다케다 침공과 호조·우에스기 화의",
        "start_id": 4592,
        "end_id": 4609,
        "selected_count": 18,
    },
    {
        "event_id": "kagetora_declares_kanto_expedition",
        "title_ko": "가게토라의 간토 원정 선언",
        "start_id": 4610,
        "end_id": 4631,
        "selected_count": 22,
    },
    {
        "event_id": "death_of_sogo_kazumasa",
        "title_ko": "소고 가즈마사의 죽음과 저주 소문",
        "start_id": 4632,
        "end_id": 4656,
        "selected_count": 25,
    },
    {
        "event_id": "death_of_nagano_narimasa",
        "title_ko": "나가노 나리마사의 유언",
        "start_id": 4657,
        "end_id": 4690,
        "selected_count": 34,
    },
)

TRANSLATIONS: dict[int, str] = {
    4557: (
        "동생 \x1bCA나가요리\x1bCZ의 무공을 발판 삼아, \x1bCA마쓰나가 히사히데\x1bCZ는\n"
        "주군 \x1bCA미요시 나가요시\x1bCZ의 측근이 된 뒤 이재를 발휘해\n"
        "\x1bCB미요시 가문\x1bCZ의 온갖 정무를 관장했다."
    ),
    4558: (
        "이제 \x1bCC기나이\x1bCZ 전역을 지배하고\n"
        "쇼군의 권위까지 거머쥔 \x1bCB미요시\x1bCZ 정권에서도,\n"
        "\x1bCA히사히데\x1bCZ의 실력과 존재감은 단연 돋보였다."
    ),
    4559: (
        "단조쇼히쓰에 임명된 \x1bCA히사히데\x1bCZ는,\n"
        "\x1bCC야마토\x1bCZ와 \x1bCC가와치\x1bCZ의 경계에 있는\n"
        "\x1bCC시기산성\x1bCZ을 맡게 되었다."
    ),
    4560: (
        "\x1bCC야마토\x1bCZ에는 \x1bCC고후쿠지\x1bCZ의 승관을 비롯해,\n"
        "\x1bCB미요시 가문\x1bCZ에 복종하지 않는 무사가 많다.\n"
        "\x1bCC가와치\x1bCZ 접경 성을 \x1bCC야마토\x1bCZ 지배 거점으로 삼아야 한다……"
    ),
    4561: (
        "그렇다면 이런 초라한 성으로는 안 된다.\n"
        "지금까지 본 어떤 성에도 뒤지지 않는,\n"
        "견고하고 강대한 성으로 만들겠다."
    ),
    4562: (
        "한때 \x1bCB가와치 하타케야마 가문\x1bCZ을 쥐락펴락한 \x1bCA기자와 나가마사\x1bCZ가\n"
        "쌓은 이 성을, 이제 \x1bCB미요시 가문\x1bCZ을 관장하는 내가\n"
        "더욱 견고하게 고치는 것도 나쁘지 않겠군……"
    ),
    4563: (
        "\x1bCB쇼토쿠 태자\x1bCZ 이래의 전승을 자랑하는\n"
        "\x1bCC조고손시지\x1bCZ가 자리한 이 산에 전례 없는 성을 쌓아,\n"
        "\x1bCC야마토\x1bCZ의 \x1bCB국인중\x1bCZ에게 보여 주마."
    ),
    4564: (
        "어쩌면…… \x1bCB야마토 무리\x1bCZ뿐만 아니라\n"
        "\x1bCB미요시\x1bCZ 일문마저 적으로 돌려,\n"
        "싸우게 될지도 모르지만……"
    ),
    4565: (
        "\x1bCA나가요시\x1bCZ는 \x1bCA히사히데\x1bCZ를 전적으로 신뢰했지만,\n"
        "\x1bCB미요시 가문\x1bCZ 안의 권력 다툼은 물밑에서 치열하게 벌어졌다."
    ),
    4566: (
        "\x1bCA히사히데\x1bCZ도 자신이 특히\n"
        "\x1bCB미요시 가문\x1bCZ 일문에게 좋게 보이지 않음을 알았기에,\n"
        "제 지위가 반석 같지 않다는 것을 깨달았다."
    ),
    4567: (
        "그런 속셈 때문인지는 확실하지 않으나,\n"
        "\x1bCA히사히데\x1bCZ는 \x1bCC시기산성\x1bCZ의 성주가 되자\n"
        "대대적인 성곽 개수를 시작했다."
    ),
    4568: (
        "험준한 \x1bCC시기산\x1bCZ 정상 가까이에 4층짜리\n"
        "웅대한 천수를 세웠다. 그 위용은 훗날\n"
        "\x1bCC아즈치성\x1bCZ에도 영향을 주었다……"
    ),
    4569: (
        "근세 거의 모든 성곽에 세워진 천수의\n"
        "원형이 되었다고도 한다. \x1bCA히사히데\x1bCZ는\n"
        "축성의 재능을 세상에 유감없이 떨쳤다."
    ),
    4570: (
        "\x1bCA[b1448]\x1bCZ가 산을 넘어 \x1bCC간토\x1bCZ로 온다……\n"
        "그 소식은 곧 \x1bCB호조 가문\x1bCZ에도 전해졌고,\n"
        "\x1bCA우지야스\x1bCZ는 강적의 출현에 대비했다."
    ),
    4571: (
        "\x1bCA요시모토\x1bCZ의 죽음으로 삼국동맹이 흔들린 틈을\n"
        "\x1bCA[bm1448]\x1bCZ가 놓치지 않고,\n"
        "싸움을 걸어온 것이 틀림없다……"
    ),
    4572: "그런가, 마침내 움직였나……",
    4573: (
        "예, \x1bCC에치고\x1bCZ의 \x1bCA[b1448]\x1bCZ가\n"
        "전 간토 간레이 \x1bCA우에스기 노리마사\x1bCZ를 받들고,\n"
        "우리를 치려 병력을 모으고 있습니다!"
    ),
    4574: "왔나……\n얼마나 모일 것 같으냐?",
    4575: "글쎄요, 십만쯤 되지 않겠습니까.",
    4576: (
        "이봐, \x1bCC가와고에\x1bCZ 때보다 많잖아.\n"
        "원한을 단단히 샀나 보군."
    ),
    4577: "그래서 어쩔 셈이야?\n또 성에 틀어박히는 건 질색이라고.",
    4578: "아무것도 하지 않는다.\n우리는 그런 사내를 상대하지 않는다.",
    4579: "상대하지 않는다니……\n그게 통할 상대인가?",
    4580: (
        "통할 때까지 상대하지 않는다.\n"
        "그 사내와 정면으로 싸우다가는,\n"
        "목숨이 몇 개라도 모자랄 테니."
    ),
    4581: "얼굴의 흉터 하나 늘어나는 정도로는\n끝나지 않는다…… 이거군.",
    4582: "그 대군을 이끌고 \x1bCC간토\x1bCZ를 누빈다면,\n오래 버티지는 못할 것이다.",
    4583: (
        "굶주림에 시달리다 \x1bCC에치고\x1bCZ로 달아날 때……\n"
        "그때야말로 우리의 무서움을 알려 주마."
    ),
    4584: "그자는 집념이 강해.\n그렇게 순순히 돌아가 줄까?",
    4585: (
        "그래서 하는 말이지.\n"
        "이 \x1bCC간토\x1bCZ에서 온갖 난폭한 짓을 벌여\n"
        "백성의 군량을 빼앗을지도 몰라."
    ),
    4586: "손은 써 두겠다.\n\x1bCC가이\x1bCZ의 탐욕스러운 중을 움직이지.",
    4587: "과연……\n호랑이 굴에 다른 호랑이를 풀겠다는 건가.",
    4588: (
        "간토 간레이였으나 \x1bCB호조 가문\x1bCZ에 쫓겨\n"
        "\x1bCC에치고\x1bCZ로 달아난\n"
        "\x1bCA우에스기 노리마사\x1bCZ뿐 아니라,"
    ),
    4589: (
        "\x1bCC간토\x1bCZ에서 계속 \x1bCB호조씨\x1bCZ에 맞선\n"
        "\x1bCB우에스기 가문\x1bCZ의 옛 가신 \x1bCA나가노 나리마사\x1bCZ와 \x1bCA오타 스케마사\x1bCZ,"
    ),
    4590: (
        "오랫동안 \x1bCB호조\x1bCZ와 적대한 아와의 맹주\n"
        "\x1bCA사토미 요시타카\x1bCZ 등 수많은 다이묘가\n"
        "\x1bCB[bs1448] 가문\x1bCZ에 가세했다."
    ),
    4591: (
        "이제,\n"
        "\x1bCB호조 가문\x1bCZ은 가와고에 야전 이래\n"
        "가장 큰 위기를 맞게 되었다."
    ),
    4592: (
        "\x1bCA이마가와 요시모토\x1bCZ의 죽음으로 고소슨 삼국동맹이 흔들렸다.\n"
        "\x1bCA신겐\x1bCZ은 후계자 \x1bCA우지자네\x1bCZ를 믿을 수 없다고 보고,\n"
        "\x1bCB이마가와 영지\x1bCZ 침공을 꾀했다."
    ),
    4593: (
        "가문의 친\x1bCB이마가와\x1bCZ파 구심점이던 적자\n"
        "\x1bCA요시노부\x1bCZ의 죽음이라는 비극이 있었지만,\n"
        "마침내 \x1bCB다케다군\x1bCZ은 \x1bCC스루가\x1bCZ로 진군했다……"
    ),
    4594: (
        "\x1bCA[bm1251]\x1bCZ가 우리와 \x1bCB다케다\x1bCZ가 \x1bCC스루가\x1bCZ를\n"
        "반씩 나누자는 서신을 보내왔습니다."
    ),
    4595: "감히 그런 말을 하다니!\n즉시 군사를 물리라고 \x1bCA신겐\x1bCZ에게 전하라!",
    4596: "\x1bCA신겐\x1bCZ은 물러나지 않을 겁니다.\n그렇게 되면……",
    4597: "\x1bCB다케다\x1bCZ와는 관계를 끊어야겠지.",
    4598: (
        "하지만,\n"
        "\x1bCB다케다\x1bCZ와 \x1bCB우에스기\x1bCZ를 모두 적으로 돌리면 악수다.\n"
        "그걸 막으려고 삼국동맹을 맺은 것 아닌가?"
    ),
    4599: "그래.\n그러니 두 가문을 모두 적으로 만들지만 않으면 된다……",
    4600: "그 말씀은……\n설마 \x1bCB우에스기\x1bCZ와 화친을?",
    4601: "음, 전부터 생각하던 일이다.\n\x1bCA우지쿠니\x1bCZ, 진척은 어떠냐?",
    4602: (
        "예! 전에 간토 간레이 문제에서\n"
        "우리가 양보한 뒤에야,\n"
        "\x1bCA[bm1448]\x1bCZ가 이야기를 들을 뜻을 보였습니다."
    ),
    4603: (
        "\x1bCA호조 우지쓰나\x1bCZ가 고가 구보 \x1bCB아시카가 가문\x1bCZ을 보호하고,\n"
        "\x1bCA우지야스\x1bCZ가 \x1bCA우에스기 노리마사\x1bCZ를 \x1bCC간토\x1bCZ에서 몰아낸 뒤,\n"
        "\x1bCB호조 가문\x1bCZ은 간토 간레이를 자칭했다."
    ),
    4604: (
        "\x1bCA[b1448]\x1bCZ는 \x1bCB우에스기\x1bCZ 당주·간레이를 \x1bCA노리마사\x1bCZ에게 받아,\n"
        "자신이 정통이라며 화의를 거부했다……"
    ),
    4605: (
        "\x1bCB호조 가문\x1bCZ이 간토 간레이를 칭하는 한,\n"
        "화의에는 응하지 않겠다는 태도였다."
    ),
    4606: (
        "그런 허울뿐인 간레이직은 필요 없다.\n"
        "\x1bCA[b1448]\x1bCZ에게 줘 버리지.\n"
        "\x1bCB우에스기\x1bCZ와의 교섭을 진행하라."
    ),
    4607: (
        "곧 \x1bCB다케다\x1bCZ와 전쟁이 벌어질 것이다.\n"
        "\x1bCA[bm1448]\x1bCZ도 그렇지만 \x1bCA신겐\x1bCZ 역시 강적이다.\n"
        "\x1bCA쓰나시게\x1bCZ, \x1bCA우지테루\x1bCZ, 단단히 각오해라."
    ),
    4608: "알겠습니다.",
    4609: "맡겨 둬!\n벌써부터 몸이 근질거리는군.",
    4610: "\x1bCC에치고\x1bCZ·\x1bCC가스가야마성\x1bCZ――",
    4611: (
        "오케하자마 전투에서 \x1bCA이마가와 요시모토\x1bCZ가 죽은 여파는\n"
        "멀리 \x1bCC에치고\x1bCZ에도 미치고 있었다."
    ),
    4612: "\x1bCA요시모토\x1bCZ가 죽었는가……",
    4613: "예.\n고소슨 삼국동맹에 금이 갔습니다.\n지금이야말로 좋은 기회입니다.",
    4614: (
        "\x1bCA이마가와 요시모토\x1bCZ는 \x1bCC스루가\x1bCZ·\x1bCC미카와\x1bCZ·\x1bCC도토미\x1bCZ를 장악해,\n"
        "그 영향력을 무시할 수 없는 명장이었다."
    ),
    4615: (
        "가령 \x1bCB[bs1448] 가문\x1bCZ도\n"
        "\x1bCB다케다 가문\x1bCZ과의 싸움을 중단당할 만큼,\n"
        "무시할 수 없는 존재였다."
    ),
    4616: (
        "후계자 \x1bCA우지자네\x1bCZ는 무력하다……\n"
        "우선 \x1bCB다케다\x1bCZ를 쳐 천하에 우리의 의를 보일까."
    ),
    4617: "외람되오나 한 말씀 올리겠습니다.",
    4618: (
        "\x1bCB다케다\x1bCZ를 치기보다 먼저,\n"
        "간토 간레이 \x1bCA우에스기 노리마사\x1bCZ 님의 요청에 응해\n"
        "\x1bCC간토\x1bCZ로 군사를 보내야 한다고 생각합니다."
    ),
    4619: (
        "호오……\n"
        "\x1bCB무라카미\x1bCZ 공의 옛 영지인 \x1bCC시나노\x1bCZ를 되찾기보다\n"
        "그쪽이 먼저라는 말인가."
    ),
    4620: "그렇습니다.\n그것이 우리 \x1bCB[bs1448] 가문\x1bCZ의 의일 것입니다.",
    4621: (
        "훌륭하다!\n"
        "그 \x1bCA무라카미\x1bCZ 공의 의로운 마음에,\n"
        "언젠가 이 \x1bCA가게토라\x1bCZ가 신의로 보답하리라."
    ),
    4622: "모두 들었을 것이다.\n이제 우리는 간토로 군사를 보낸다.",
    4623: (
        "의의 칼날로 간적 \x1bCA호조 우지야스\x1bCZ의 목을 베고,\n"
        "간토 간레이의 깃발 아래 그 땅의 혼란을 바로잡겠다."
    ),
    4624: (
        "\x1bCA[bm1448]\x1bCZ 님.\n"
        "우리의 의로운 칼날에 \x1bCA노리마사\x1bCZ 님은\n"
        "무엇으로 보답하시겠습니까?"
    ),
    4625: (
        "후후……\n"
        "역시 \x1bCA도모노부\x1bCZ, 궁금한가?\n"
        "아마 네가 생각하는 바로 그것일 것이다."
    ),
    4626: "이거 참……\n기대해도 되겠습니까?",
    4627: (
        "우리 \x1bCB[bs1448]\x1bCZ 가문은 이익을 구하지 않는다.\n"
        "하지만 신의로 움직였다면,\n"
        "그에 걸맞은 보답이 있어야 옳다."
    ),
    4628: "그렇습니다.\n공명정대함이 우리의 길.\n바른 길에는 바른 보답이 따릅니다.",
    4629: (
        "그리하여 \x1bCA[b1448]\x1bCZ는\n"
        "간토 간레이 \x1bCA우에스기 노리마사\x1bCZ를 받들고,\n"
        "천하에 간토 원정의 뜻을 밝혔다."
    ),
    4630: (
        "\x1bCC간토\x1bCZ의 제후들은 \x1bCB호조 가문\x1bCZ의 군사적 압력을 두려워해,\n"
        "이 원정을 환영했다."
    ),
    4631: (
        "\x1bCA[bm1448]\x1bCZ의 의로운 깃발 아래 모인 다이묘의 이름은,\n"
        "훗날 ‘간토 마쿠추몬’이라 불리는 문서에 남았다."
    ),
    4632: (
        "\x1bCA미요시 나가요시\x1bCZ의 동생들은 모두 개성이 강했는데,\n"
        "그중 ‘오니소고’라는 별명으로 이름난 맹장이\n"
        "\x1bCA소고 가즈마사\x1bCZ였다――"
    ),
    4633: (
        "형을 도와 각지를 전전하며 \x1bCB미요시 가문\x1bCZ의 위세를\n"
        "넓히는 데 큰 공을 세웠다.\n"
        "하지만 서른이라는 젊은 나이에 세상을 떠났다……"
    ),
    4634: "그…… 오니소고…… \x1bCA가즈마사\x1bCZ 님이\n돌아가셨다는 말이냐!?",
    4635: (
        "예! 그런데 그뿐만이 아닙니다!\n"
        "\x1bCB미요시\x1bCZ 가문 안에서는…… \x1bCA마쓰나가\x1bCZ 님이\n"
        "\x1bCA소고\x1bCZ 님을 저주했다는 소문이 돌고 있습니다……"
    ),
    4636: (
        "말도 안 된다! 내가 무슨 이유로\n"
        "오니소고를 해친단 말이냐!\n"
        "터무니없는 소문에 불과하다!"
    ),
    4637: (
        "가문 안의 소문일 뿐이오나……\n"
        "\x1bCC아리마\x1bCZ 온천에서 \x1bCA소고\x1bCZ 님과\n"
        "무슨 이야기를 나누지 않으셨습니까?"
    ),
    4638: (
        "그래, \x1bCC아리마 온천\x1bCZ에 요양하러 갔을 때\n"
        "\x1bCA소고\x1bCZ 님을 만났지만…… 그때는\n"
        "\x1bCA소고\x1bCZ 님의 말 이야기밖에 하지 않았는데?"
    ),
    4639: "(그래, 그저 시시한 이야기였을 뿐……)",
    4640: "――몇 달 전·\x1bCC아리마 온천\x1bCZ",
    4641: "음…… \x1bCA마쓰나가\x1bCZ?",
    4642: (
        "이런, 이런……\n"
        "\x1bCA가즈마사\x1bCZ 님도 온천 요양을 오셨습니까?\n"
        "어디 몸이라도 불편하신지요?"
    ),
    4643: "흥……",
    4644: (
        "그러고 보니…… \x1bCA소고\x1bCZ 님은 회색 말을 좋아하신다지요.\n"
        "하지만 그 말을 타고 이 온천까지 오는 것은\n"
        "몹시 위험한 일입니다."
    ),
    4645: "흥…… 별소리를 다 하는군.\n내 애마에 무슨 불만이라도 있나?",
    4646: (
        "항간의 소문입니다만, 이곳을 지키는\n"
        "아리마 곤겐은 회색 말을 싫어한다고 합니다……\n"
        "미신일지도 모르나 조심하십시오."
    ),
    4647: (
        "신불 따위 아랑곳하지 않는 \x1bCA마쓰나가\x1bCZ가 그런 말을 하나.\n"
        "내 애마를 트집 잡다니 무례하기 짝이 없군……\n"
        "불쾌하다. 돌아가겠다!"
    ),
    4648: "이런, 그저 이곳 전승을 알려 드렸을 뿐인데.\n단단히 미움을 샀군……",
    4649: (
        "\x1bCC아리마\x1bCZ 온천에서는 시시한 이야기밖에 하지 않았다.\n"
        "그게 어째서 내가 \x1bCA소고\x1bCZ 님을 저주한 일이 된 거지……"
    ),
    4650: (
        "이번에 \x1bCA소고\x1bCZ 님이 돌아가신 것은……\n"
        "\x1bCA마쓰나가\x1bCZ 님이 불길하다고 한 말에서\n"
        "떨어진 탓이라고 합니다."
    ),
    4651: (
        "뭐라고…… 아리마 곤겐의 소문 그대로인가.\n"
        "용맹한 오니소고가 낙마하다니……\n"
        "내가 의심받을 만도 하군."
    ),
    4652: (
        "(골치 아프게 되었군……\n"
        "　\x1bCA가즈마사\x1bCZ 님의 죽음으로 나는 \x1bCB미요시\x1bCZ 가문에서\n"
        "　더욱 미움을 사게 되겠어.)"
    ),
    4653: (
        "(주군께 남은 두 아우……\n"
        "　\x1bCA짓큐\x1bCZ 님과 \x1bCA후유야스\x1bCZ 님에게도 비슷한 일이\n"
        "　생긴다면 내 처지는 더욱……)"
    ),
    4654: (
        "\x1bCA소고 가즈마사\x1bCZ는 병사했다거나 낙마했다는 등\n"
        "전승이 엇갈리지만, 당시부터 지금까지\n"
        "\x1bCA히사히데\x1bCZ가 암살했다는 소문은 끊이지 않는다."
    ),
    4655: (
        "\x1bCA가즈마사\x1bCZ의 죽음으로 \x1bCA히사히데\x1bCZ가 큰 이익을 본 것은\n"
        "틀림없다. 그를 의심할 여지는\n"
        "차고 넘쳤던 것이다."
    ),
    4656: (
        "\x1bCB미요시 가문\x1bCZ에 특히 큰 공을 세운 \x1bCA가즈마사\x1bCZ의 죽음은\n"
        "군사적으로 큰 타격이었을 뿐 아니라,\n"
        "가문 전체에 짙은 그림자를 드리웠다……"
    ),
    4657: (
        "조슈의 호랑이라 두려움을 사며, 적과의 최전선에서\n"
        "\x1bCA[b1251]\x1bCZ의 침공을 막아 온 \x1bCC미노와\x1bCZ 성주\n"
        "\x1bCA나가노 나리마사\x1bCZ――"
    ),
    4658: (
        "하지만 이 용장도 일흔을 넘기자 병석에 눕는 날이\n"
        "잦아졌고, 손님이 찾아와도\n"
        "만나기를 거절하게 되었다."
    ),
    4659: "누구 없느냐!",
    4660: "예!\n부르셨습니까?",
    4661: "오늘 손님이 올 듯하니,\n맞을 준비를 하라.",
    4662: "알겠습니다!\n(요즘 이 성에 손님이 찾아오는 일은\n　거의 없었는데……)",
    4663: (
        "잠시 뒤 손님 한 사람이 찾아왔다.\n"
        "그것도 \x1bCA나리마사\x1bCZ의 적인 \x1bCB[bs1251] 가문\x1bCZ의 무장이……"
    ),
    4664: "주군!\n\x1bCA사나다 단조노조\x1bCZ 님께서 오셨습니다!",
    4665: "왔는가…… 곧 들여라.",
    4666: "\x1bCA나가노\x1bCZ 공.\n오랫동안 찾아뵙지 못해 송구합니다.",
    4667: "괜찮네.\n내 수명이 다하기 전에\n자네를 만나 기쁘구려.",
    4668: "그렇다면 역시 병환이……",
    4669: "이 \x1bCA나리마사\x1bCZ도 이제 일흔.\n주가 \x1bCB우에스기 가문\x1bCZ의 운세도 다 기울었군……",
    4670: (
        "\x1bCB나가노 가문\x1bCZ의 주군인 간토 간레이 \x1bCB야마노우치 우에스기 가문\x1bCZ\n"
        "당주 \x1bCA노리마사\x1bCZ는 남쪽에서 닥친 \x1bCB호조 가문\x1bCZ의 압력을\n"
        "견디지 못하고 \x1bCC에치고\x1bCZ로 달아난 상태였다."
    ),
    4671: (
        "지금은 \x1bCA사나다 유키타카\x1bCZ가 \x1bCB다케다 가문\x1bCZ을 따르지만,\n"
        "한때 적대하던 \x1bCB다케다\x1bCZ의 공격을 받고,\n"
        "\x1bCA나리마사\x1bCZ를 의지해 이 \x1bCC미노와성\x1bCZ으로 달아나……"
    ),
    4672: "\x1bCA나리마사\x1bCZ와 함께 \x1bCA우에스기 노리마사\x1bCZ를\n보필한 적도 있었다……",
    4673: (
        "자네가 이 \x1bCC미노와\x1bCZ에 있을 때…… 주군 \x1bCA노리마사\x1bCZ는\n"
        "자네의 진언을 받아들이지 않았지.\n"
        "참으로 요령을 알 수 없는 분이었네."
    ),
    4674: (
        "그 뒤 자네는 \x1bCC가이\x1bCZ로 떠나 버렸지.\n"
        "\x1bCB가이 다케다\x1bCZ는 자네를 모사로 등용해,\n"
        "\x1bCC기타시나노\x1bCZ와 \x1bCC니시코즈케\x1bCZ를 차지해 갔고."
    ),
    4675: "…………",
    4676: (
        "언젠가 \x1bCC코즈케 전역\x1bCZ도 누군가에게 빼앗기겠지.\n"
        "아들 \x1bCA나리모리\x1bCZ도 기개 있는 무사로 자랐지만,\n"
        "도저히 \x1bCA[bm1251]\x1bCZ와 겨룰 그릇은 아니네."
    ),
    4677: "어디의 누군지도 모를 자에게 넘어갈 바에는,\n자네 같은 사내에게 넘기고 싶군.",
    4678: "조슈의 호랑이에게서\n그런 나약한 말을 듣게 될 줄이야……",
    4679: (
        "일단 듣게.\n"
        "\x1bCC미노와\x1bCZ 북쪽에 \x1bCC누마타령\x1bCZ이라는 땅이 있네.\n"
        "사방이 산으로 둘러싸이고 좋은 논밭이 있지."
    ),
    4680: "건강할 때의 나라면 쉽게 빼앗았겠지만,\n지금은 병 때문에 몸을 움직일 수 없네.",
    4681: (
        "\x1bCC시나노\x1bCZ에 뿌리내린 자네야말로 \x1bCC누마타\x1bCZ의 주인에 걸맞네.\n"
        "\x1bCA유키타카\x1bCZ, 언젠가 자네가 \x1bCC누마타\x1bCZ를 차지해,\n"
        "\x1bCC조슈\x1bCZ 공략의 거점으로 삼게."
    ),
    4682: "근래 멀어진 저를 이렇게까지\n염려해 주시니 그저 감사할 따름입니다.",
    4683: "염려해서가 아니야……\n나는 기대하고 있는 걸세.",
    4684: (
        "내가 지켜 온 이 \x1bCC조슈\x1bCZ에서,\n"
        "내 지휘를 이어받은 자네와,\n"
        "자네의 아들, 손자들이……"
    ),
    4685: (
        "교만한 대다이묘의 대군을 철저히 깨뜨려……\n"
        "그 코를 납작하게 만드는 걸세……\n"
        "이보다…… 통쾌한 일이…… 쿨럭……"
    ),
    4686: "\x1bCA나리마사\x1bCZ 님!",
    4687: (
        "\x1bCA유키타카\x1bCZ, 내 아이들에게 전하게…… 법요는 필요 없다.\n"
        "그저 \x1bCA[b1251]\x1bCZ의 목을 내 무덤 앞에 바치고,\n"
        "적에게 항복하지 말고 전사하라 전해 주게……"
    ),
    4688: "\x1bCC조슈\x1bCZ를 부탁하네……\n\x1bCC누마타\x1bCZ는…… 자네 손에 달렸어……",
    4689: (
        "\x1bCA[b1251]\x1bCZ조차 \x1bCA나리마사\x1bCZ가 \x1bCC미노와\x1bCZ에 있으면,\n"
        "\x1bCC코즈케\x1bCZ를 못 얻는다고 한 명장 \x1bCA나가노 나리마사\x1bCZ가 숨졌다."
    ),
    4690: (
        "훗날 \x1bCA사나다 유키타카\x1bCZ의 아들 \x1bCA마사유키\x1bCZ가,\n"
        "\x1bCC누마타성\x1bCZ의 성주가 되어 \x1bCA나리마사\x1bCZ의 바람을 이루었다."
    ),
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    4559: ["danjo_shohitsu_court_title_requires_glossary_review"],
    4563: ["chogosonshiji_and_kokushu_terms_require_glossary_review"],
    4587: ["tiger_idiom_adaptation_requires_style_review"],
    4590: ["satomi_yoshitaka_and_kanto_names_require_glossary_review"],
    4593: ["yoshinobu_death_chronology_requires_historical_review"],
    4631: ["kanto_makuchumon_document_title_requires_glossary_review"],
    4632: ["sogo_kazumasa_and_onisogo_readings_require_glossary_review"],
    4646: ["arima_gongen_and_grey_horse_legend_require_historical_review"],
    4653: ["miyoshi_jikkyu_reading_requires_glossary_review"],
    4657: ["tiger_of_joshu_epithet_requires_style_review"],
    4664: ["sanada_danjo_no_jo_title_requires_glossary_review"],
    4687: ["hoyo_memorial_term_requires_glossary_review"],
}

PREVIOUS_ARTIFACT_PINS = {
    **shared.PREVIOUS_ARTIFACT_PINS,
    "evidence/alignment_evidence.v0.12.json": (
        "B0C1BA9A4A48ACFDA9233ED2ABF450F64C0D172B57BEA6FBE96076AB279ADF70"
    ),
    "public/msgev_ko_historical_events_4418_4556.v0.12.json": (
        "AF0061757E9E6B4220A0AC55C9E0C617260746F9098C2EBCEC39301AD5265248"
    ),
    "review/review_index.v0.12.json": (
        "C9D7D8901C2888301402DF624FBA8C84FB9CA760DFDDB5A0D21D68D3822BDE93"
    ),
    "validation.v0.12.json": (
        "E5F2D94BD7E1B654143ED8C12DBC68B554734EDEFE0D853FE3D0F1AD52155CA1"
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
    if len(ids) != 134 or ids != sorted(TRANSLATIONS):
        raise ValueError("batch13 ids are not the exact 134 displayed entries")
    return ids


def event_for(entry_id: int) -> str:
    matches = [
        event["event_id"]
        for event in EVENTS
        if event["start_id"] <= entry_id <= event["end_id"]
    ]
    if len(matches) != 1:
        raise ValueError(f"id {entry_id} does not map to one batch13 event group")
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
        4556,
        4557,
        4569,
        4570,
        4591,
        4592,
        4609,
        4610,
        4631,
        4632,
        4656,
        4657,
        4690,
        4691,
    )
    evidence["schema"] = "nobu16.kr.event-dialogue-alignment-evidence.v13"
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
    review["schema"] = "nobu16.kr.event-dialogue-review-index.v13"
    validation["schema"] = "nobu16.kr.event-dialogue-generation-validation.v13"
    validation["font_integration"].pop(
        "current_font_or_installer_must_not_include_batch12", None
    )
    validation["font_integration"][
        "current_font_or_installer_must_not_include_batch13"
    ] = True
    integrity = validation["preexisting_integrity"]
    integrity["dialogue_v01_v12_artifacts_before"] = integrity.pop(
        "dialogue_v01_v11_artifacts_before"
    )
    integrity["dialogue_v01_v12_artifacts_after"] = integrity.pop(
        "dialogue_v01_v11_artifacts_after"
    )
    safety = validation["safety"]
    safety.pop(
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_artifacts_modified",
        None,
    )
    safety[
        "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_artifacts_modified"
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
