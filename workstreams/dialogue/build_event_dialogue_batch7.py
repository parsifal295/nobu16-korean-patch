#!/usr/bin/env python3
"""Build source-free Korean historical event dialogue batch7 (3819-3929)."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
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
import build_event_dialogue_batch6 as shared  # noqa: E402


BATCH_ID = "msgev_historical_events_3819_3929.v0.7"
OVERLAY_NAME = "msgev_ko_historical_events_3819_3929.v0.7.json"
EVIDENCE_NAME = "alignment_evidence.v0.7.json"
REVIEW_NAME = "review_index.v0.7.json"
VALIDATION_NAME = "validation.v0.7.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 3819
SCOPE_END = 3929
EXCLUDED_INTERNAL_IDS: tuple[int, ...] = ()
BRACKET_TOKEN_RE = re.compile(r"\[[a-z0-9_]+\]")

EVENTS = (
    {
        "event_id": "miyoshi_changes_allegiance",
        "title_ko": "미요시 나가요시의 진영 교체",
        "start_id": 3819,
        "end_id": 3839,
        "selected_count": 21,
    },
    {
        "event_id": "matsudaira_under_imagawa_rule",
        "title_ko": "마쓰다이라 가문의 이마가와 종속",
        "start_id": 3840,
        "end_id": 3854,
        "selected_count": 15,
    },
    {
        "event_id": "nagao_masakage_submission",
        "title_ko": "나가오 마사카게의 신종",
        "start_id": 3855,
        "end_id": 3879,
        "selected_count": 25,
    },
    {
        "event_id": "kikkawa_motoharu_adoption",
        "title_ko": "깃카와 모토하루의 입양",
        "start_id": 3880,
        "end_id": 3898,
        "selected_count": 19,
    },
    {
        "event_id": "otomo_nikai_kuzure",
        "title_ko": "오토모 가문의 니카이쿠즈레의 변",
        "start_id": 3899,
        "end_id": 3916,
        "selected_count": 18,
    },
    {
        "event_id": "kobayakawa_takakage_succession",
        "title_ko": "고바야카와 다카카게의 가독 계승",
        "start_id": 3917,
        "end_id": 3929,
        "selected_count": 13,
    },
)

TRANSLATIONS: dict[int, str] = {
    3819: (
        "\x1bCB오가사와라씨\x1bCZ의 방계라 칭한 \x1bCB미요시 가문\x1bCZ은\n"
        "\x1bCC아와 미요시군\x1bCZ에 기반을 닦고,\n"
        "그곳의 슈고 \x1bCB아와 호소카와씨\x1bCZ를 섬겼다."
    ),
    3820: (
        "오닌의 난 뒤, \x1bCA미요시 유키나가\x1bCZ는 \x1bCB아와 호소카와 가문\x1bCZ에서\n"
        "\x1bCB호소카와 게이초 가문\x1bCZ에 입양된 \x1bCA호소카와 스미모토\x1bCZ를 도와,\n"
        "가독 다툼에서 싸우며 권세를 얻었다."
    ),
    3821: (
        "하지만 \x1bCA미요시 유키나가\x1bCZ의 후계자 \x1bCA모토나가\x1bCZ는\n"
        "분가의 \x1bCA미요시 마사나가\x1bCZ가 퍼뜨린 모함 탓에,\n"
        "\x1bCA호소카와 스미모토\x1bCZ의 아들 \x1bCA하루모토\x1bCZ와 맞섰다."
    ),
    3822: (
        "마침내 주군 \x1bCA하루모토\x1bCZ 일파의 암약으로,\n"
        "궁지에 몰린 \x1bCA모토나가\x1bCZ는 스스로 목숨을 끊었다."
    ),
    3823: (
        "\x1bCA모토나가\x1bCZ의 아들 \x1bCA나가요시\x1bCZ는 뒤를 이어,\n"
        "부친의 원수인 \x1bCA하루모토\x1bCZ 휘하에 몸을 두었다."
    ),
    3824: (
        "형님, 언제까지나 \x1bCB호소카와 가문\x1bCZ을\n"
        "따라야만 하는 것입니까……"
    ),
    3825: (
        "\x1bCB호소카와 가문\x1bCZ이 지금 세력을 지키는 것도\n"
        "모두 우리 가문이 힘쓴 덕입니다!\n"
        "\x1bCA하루모토\x1bCZ의 그릇과는 아무 상관 없습니다."
    ),
    3826: (
        "우리…… \x1bCB미요시\x1bCZ의 힘이 없었다면,\n"
        "\x1bCB호소카와\x1bCZ 가독을 둘러싼 \x1bCA우지쓰나\x1bCZ와의 싸움에서\n"
        "벌써 맥없이 패하지 않았겠습니까?"
    ),
    3827: (
        "하지만 서두를 수는 없다.\n"
        "주군을 죽였다는 오명을 쓰면,\n"
        "주변 세력이 쳐들어올 구실이 되니까……"
    ),
    3828: (
        "그러면 이대로 \x1bCB호소카와 가문\x1bCZ의 개가 되어\n"
        "부친의 원수를 계속 섬기자는 것이오?"
    ),
    3829: (
        "부친의 원수라면 \x1bCA미요시 마사나가\x1bCZ도 마찬가지다.\n"
        "아버님께서 돌아가신 것도 결국\n"
        "그자의 모함 때문이었으니……"
    ),
    3830: (
        "\x1bCC셋쓰\x1bCZ의 \x1bCA이케다 노부마사\x1bCZ도 \x1bCA마사나가\x1bCZ의 모함 탓에\n"
        "할복하게 되었다는 소문이 있소……\n"
        "그런 자와 함께 있을 수는 없소!"
    ),
    3831: (
        "진정해라. \x1bCA마사나가\x1bCZ 따위는 상관없다.\n"
        "나는 단지 방금 전에\n"
        "주군을 죽인 자가 되기 싫다고 했을 뿐이다."
    ),
    3832: (
        "……그렇군요.\n"
        "그럼 \x1bCA호소카와 하루모토\x1bCZ가 주군이 아니면 됩니까?"
    ),
    3833: (
        "그렇다.\n"
        "더는 주군이 아닌 자를 쓰러뜨린들,\n"
        "주군을 죽였다고 불릴 리 없지……"
    ),
    3834: (
        "주군이 아니라면 당당히 적으로서 \x1bCA하루모토\x1bCZ를……\n"
        "그 앞잡이 \x1bCA마사나가\x1bCZ와 함께,\n"
        "멸망시키면 된다."
    ),
    3835: (
        "그렇다면……\n"
        "\x1bCA호소카와 하루모토\x1bCZ와 대립하는 \x1bCA호소카와 우지쓰나\x1bCZ 진영으로\n"
        "갈아탄다는 말씀이군요."
    ),
    3836: (
        "음.\n"
        "\x1bCA히사히데\x1bCZ, \x1bCA우지쓰나\x1bCZ 공에게 가거라."
    ),
    3837: "예!",
    3838: (
        "그렇게 \x1bCA나가요시\x1bCZ는 \x1bCA호소카와 하루모토\x1bCZ를 버리고,\n"
        "그와 대립하던 \x1bCA호소카와 우지쓰나\x1bCZ의 진영에\n"
        "속하기로 했다."
    ),
    3839: (
        "\x1bCA나가요시\x1bCZ의 배신으로 \x1bCA하루모토\x1bCZ와 \x1bCA우지쓰나\x1bCZ가\n"
        "\x1bCB호소카와 게이초 가문\x1bCZ의 가독을 두고 벌인 싸움은 격화했고,\n"
        "\x1bCC기나이\x1bCZ의 혼란은 한층 깊어졌다."
    ),
    3840: (
        "그 일은 너무도 갑작스러웠다.\n"
        "\x1bCC미카와 오카자키성\x1bCZ의 다이묘 \x1bCA마쓰다이라 히로타다\x1bCZ가\n"
        "아무런 전조도 없이 세상을 떠난 것이다……"
    ),
    3841: (
        "병사했다거나 누군가에게 암살당했다는 이야기도 있지만,\n"
        "진상은 전혀 밝혀지지 않았다."
    ),
    3842: (
        "중요한 것은 \x1bCA히로타다\x1bCZ의 뒤를 이을 적자 \x1bCA다케치요\x1bCZ가,\n"
        "\x1bCB이마가와 가문\x1bCZ의 인질로 \x1bCC슨푸\x1bCZ에 머물렀다는 사실이다."
    ),
    3843: "\x1bCC슨푸\x1bCZ·\x1bCC이마가와관\x1bCZ―",
    3844: (
        "\x1bCB마쓰다이라\x1bCZ 가신들은 우리에게\n"
        "\x1bCA다케치요\x1bCZ의 반환을 요구하겠지……"
    ),
    3845: (
        "\x1bCA다케치요\x1bCZ는 지금 내 절에서 학문을 닦고 있으나,\n"
        "\x1bCA요시모토\x1bCZ 님께서 명하시면\n"
        "\x1bCC오카자키\x1bCZ로 돌려보낼 수도 있습니다……"
    ),
    3846: (
        "스승께서도 짓궂으시군……\n"
        "내 뜻이 거기에 없다는 것을 알고 계시면서."
    ),
    3847: "그러면 \x1bCC오카자키\x1bCZ의 \x1bCB마쓰다이라 가문\x1bCZ은……?",
    3848: (
        "그들을 \x1bCB이마가와 가문\x1bCZ 산하에 넣는다.\n"
        "\x1bCC오카자키성\x1bCZ에는 대관과 병사를 두고,\n"
        "직접 다스리겠다."
    ),
    3849: (
        "그래서는 \x1bCB마쓰다이라\x1bCZ의 옛 가신들이 납득하지 않을 터……\n"
        "\x1bCB이마가와 가문\x1bCZ은 \x1bCA다케치요\x1bCZ가 성년이 되면 \x1bCC오카자키\x1bCZ를\n"
        "\x1bCB마쓰다이라 가문\x1bCZ에 돌려주겠다고 전하면 어떻겠습니까?"
    ),
    3850: (
        "하하하. 돌려줄 생각도 없는데 말이냐?\n"
        "좋다…… \x1bCA다케치요\x1bCZ가 성년이 되려면 멀었으니,\n"
        "당분간 꿈을 꾸게 해 주자."
    ),
    3851: (
        "\x1bCA히로타다\x1bCZ의 죽음으로 \x1bCB마쓰다이라 가문\x1bCZ은 다이묘로서\n"
        "한때 멸망했고, \x1bCC오카자키성\x1bCZ과 함께\n"
        "\x1bCB이마가와 가문\x1bCZ 산하에 편입되었다."
    ),
    3852: (
        "\x1bCB마쓰다이라\x1bCZ 가신들은 \x1bCB이마가와\x1bCZ의 지배를 받아들이고,\n"
        "\x1bCA요시모토\x1bCZ의 헛된 약속에 한 줄기 희망을 걸었다."
    ),
    3853: (
        "몇 년만 더…… \x1bCA다케치요\x1bCZ 님께서 성년이 되시면\n"
        "\x1bCC오카자키\x1bCZ의 성도, \x1bCB마쓰다이라\x1bCZ 가문도\n"
        "예전 모습으로 되살아날 것이다……"
    ),
    3854: (
        "\x1bCB마쓰다이라\x1bCZ의 옛 가신들은 그 믿음 하나로,\n"
        "\x1bCB이마가와\x1bCZ 산하의 가혹한 나날을 묵묵히 견뎠다."
    ),
    3855: (
        "\x1bCB나가오 가문\x1bCZ은 간토 간레이를 맡은\n"
        "\x1bCB야마노우치 우에스기 가문\x1bCZ의 가재를 배출한 집안이며,\n"
        "\x1bCC에치고\x1bCZ의 \x1bCB나가오 가문\x1bCZ은 그 분가에 해당한다."
    ),
    3856: (
        "하지만 \x1bCB후추 나가오 가문\x1bCZ과 \x1bCB우에다 나가오 가문\x1bCZ은\n"
        "같은 \x1bCB에치고 나가오 가문\x1bCZ의 일족이면서도,\n"
        "예전부터 사이가 험악했다."
    ),
    3857: (
        "\x1bCB후추 나가오 가문\x1bCZ의 \x1bCA다메카게\x1bCZ가 \x1bCC에치고\x1bCZ에서 세력을 넓히자,\n"
        "\x1bCB우에다 나가오 가문\x1bCZ은 반기를 들었으나,\n"
        "끝내 패하고 말았다."
    ),
    3858: (
        "\x1bCA다메카게\x1bCZ의 아들 \x1bCA하루카게\x1bCZ는 \x1bCB우에다 나가오 가문\x1bCZ을\n"
        "다시 일문 세력으로 끌어들이려\n"
        "몇 차례 교섭했지만 진척은 더뎠다."
    ),
    3859: (
        "하지만 \x1bCA하루카게\x1bCZ를 대신해 당주가 된 \x1bCA[bm1448]\x1bCZ 공은,\n"
        "\x1bCB우에다 나가오 가문\x1bCZ을 끌어들이지 않고서는\n"
        "\x1bCC에치고\x1bCZ를 장악할 수 없었다."
    ),
    3860: (
        "한편 \x1bCB우에다 나가오 가문\x1bCZ의 \x1bCA마사카게\x1bCZ도,\n"
        "\x1bCA[bm1448]\x1bCZ 공이 빠르게 \x1bCC에치고\x1bCZ의 기반을 굳히자,\n"
        "자신이 고립될 것을 염려했다."
    ),
    3861: (
        "서로의 필요는 인정했지만 교섭이 늦어지자,\n"
        "초조해진 \x1bCA[bm1448]\x1bCZ 공은 마침내 \x1bCA마사카게\x1bCZ가 있는\n"
        "\x1bCC사카토성\x1bCZ으로 군사를 보냈다……"
    ),
    3862: (
        "\x1bCA[b1448]\x1bCZ 공은 젊은데도 제법이군.\n"
        "말단 병사까지 군령이 닿고 진형에 흐트러짐이 없다.\n"
        "행군이 무엇인지 제대로 아는 자다."
    ),
    3863: (
        "만만찮은 적입니다.\n"
        "농성 준비는 마쳤습니다만……\n"
        "나가서 맞서시겠습니까?"
    ),
    3864: (
        "아니, 싸움으로 번지지 않을 것이다.\n"
        "\x1bCA[bm1448]\x1bCZ 공은 이 성을 빼앗으러 온 게 아니다.\n"
        "나와 교섭하러 온 것이다."
    ),
    3865: (
        "과연 \x1bCA[bm1448]\x1bCZ 공은 성을 포위하기만 했을 뿐,\n"
        "공격할 기색은 보이지 않았다.\n"
        "그렇다고 병량을 끊으려 하지도 않았다."
    ),
    3866: (
        "젊은이치고는 너무 노련하지만……\n"
        "좋다, 이번에는 내가 한발 물러서 주지.\n"
        "나쁜 이야기는 아닐 테니."
    ),
    3867: "\x1bCC사카토성\x1bCZ 밖, \x1bCA[b1448]\x1bCZ 공의 진영―",
    3868: "성주 \x1bCA나가오 마사카게\x1bCZ 님께서 직접 오셨습니다.",
    3869: (
        "실례하겠소.\n"
        "\x1bCA나가오 마사카게\x1bCZ가 \x1bCA[bm1448]\x1bCZ 공을 뵙고자 왔소."
    ),
    3870: (
        "이런, 이런……\n"
        "\x1bCB우에다 나가오 가문\x1bCZ 당주께서 직접 진중에 오시다니.\n"
        "참으로 감사하오."
    ),
    3871: (
        "이것은…… 앞으로 \x1bCB우에다 나가오 가문\x1bCZ이\n"
        "\x1bCB후추 나가오 가문\x1bCZ에 신종하겠다는 서약서요.\n"
        "부디 받아 주시오."
    ),
    3872: "그렇다면 앞으로는……",
    3873: "\x1bCA마사카게\x1bCZ는 \x1bCA[bm1448]\x1bCZ 공의 가신으로 힘쓰고자 하오.",
    3874: (
        "고마운 제안이니 참으로 감격스럽소.\n"
        "나 또한 그대의 성의에 보답해야겠군.\n"
        "내 누님과 혼인하는 것은 어떻소?"
    ),
    3875: (
        "이는 바라 마지않던 일이오.\n"
        "\x1bCA우에다 나가오 마사카게\x1bCZ는 이제부터 \x1bCA[bm1448]\x1bCZ 공의\n"
        "일문으로서 충성을 맹세하겠소."
    ),
    3876: (
        "공적인 이야기를 나누는 동안,\n"
        "\x1bCA[bm1448]\x1bCZ 공과 \x1bCA마사카게\x1bCZ는 서로의 사람됨을 살폈고,\n"
        "마침내 서로를 인정했다."
    ),
    3877: (
        "다른 고쿠진이 보는 앞에서 일족이라도 가차 없이\n"
        "군사를 보내 굴복시키는 모습을 보임으로써,\n"
        "가문을 다시 다잡은 \x1bCA[bm1448]\x1bCZ 공―"
    ),
    3878: (
        "당주가 친히 군사를 내어 굴복시킨 일이기에,\n"
        "\x1bCA마사카게\x1bCZ는 앞으로 \x1bCB후추 나가오 가문\x1bCZ의\n"
        "중진으로서 지위를 자연스레 인정받았다―"
    ),
    3879: (
        "두 사람은 서로 만만찮은 자라 경계하면서도 손을 잡았고,\n"
        "\x1bCB나가오 가문\x1bCZ의 결속은 굳어졌다. 그 관계의\n"
        "핵심은 한 여인에게 맡겨졌다……"
    ),
    3880: (
        "\x1bCC아키\x1bCZ와 \x1bCC이와미\x1bCZ에 세력을 넓힌 \x1bCB깃카와씨\x1bCZ.\n"
        "본래 \x1bCB후지와라씨\x1bCZ 출신으로, 가마쿠라 시대 중기에\n"
        "\x1bCC사이고쿠\x1bCZ로 근거지를 옮긴 무사 집단이었다."
    ),
    3881: (
        "현 당주 \x1bCA깃카와 오키츠네\x1bCZ도\n"
        "무용이 뛰어난 무장이었지만……"
    ),
    3882: (
        "\x1bCC갓산토다성\x1bCZ 전투에서 배신한 탓에,\n"
        "주변의 신뢰를 완전히 잃었다."
    ),
    3883: (
        "그 점에 주목한 \x1bCA모리 모토나리\x1bCZ는\n"
        "한 가지 계책을 세웠다."
    ),
    3884: (
        "\x1bCA모토하루\x1bCZ, 너는 이제부터 \x1bCB깃카와 가문\x1bCZ으로 들어가라.\n"
        "\x1bCA오키츠네\x1bCZ의 양자가 되는 것이다."
    ),
    3885: (
        "\x1bCA깃카와\x1bCZ……?\n"
        "그 경솔하다고 소문난 \x1bCA오키츠네\x1bCZ의 양자 말입니까?"
    ),
    3886: "그렇게 노골적으로 싫은 얼굴을 하지 마라!",
    3887: "……내 친정이기도 하단다?",
    3888: "이런……\n어머님, 죄송합니다.",
    3889: (
        "자유분방한 너에게 딱 맞지 않느냐.\n"
        "……혼인 상대까지 스스로 고른 녀석이니."
    ),
    3890: (
        "무가의 혼인 상대는 부모가 정하는 것이 상식이던\n"
        "당시에도 \x1bCA모토하루\x1bCZ는 스스로 원하여\n"
        "\x1bCA구마가이 노부나오\x1bCZ의 딸을 아내로 맞았다."
    ),
    3891: (
        "제가 자유분방하다 해도……\n"
        "\x1bCA오키츠네\x1bCZ와 한데 묶이는 것은 억울합니다!\n"
        "혼인도 아버님께서 반대하시기 전에……"
    ),
    3892: (
        "좋은 아이였어요.\n"
        "\x1bCA모토하루\x1bCZ는 여자를 보는 눈이 확실하군요."
    ),
    3893: (
        "너도 생각이 있다면,\n"
        "이번 양자가 무엇을 뜻하는지\n"
        "알 수 있지 않겠느냐?"
    ),
    3894: (
        "\x1bCA깃카와 오키츠네\x1bCZ는 경솔해도 싸움에는 능하다.\n"
        "그 가신들도 마찬가지……라는 뜻입니까?"
    ),
    3895: (
        "그렇다.\n"
        "네가 \x1bCB깃카와 가문\x1bCZ을 이끌어,\n"
        "이 \x1bCA모리\x1bCZ의 화살이 되어라, \x1bCA모토하루\x1bCZ."
    ),
    3896: (
        "\x1bCA모토하루\x1bCZ는 아버지의 명을 따라,\n"
        "\x1bCB깃카와\x1bCZ의 양자가 되어 \x1bCA깃카와 모토하루\x1bCZ로 이름을 바꿨다."
    ),
    3897: (
        "이윽고 \x1bCB깃카와 가문\x1bCZ 당주 \x1bCA오키츠네\x1bCZ는\n"
        "가신들에게 강제로 은거당했고,\n"
        "\x1bCA모토하루\x1bCZ가 \x1bCB깃카와 가문\x1bCZ의 당주가 되자……"
    ),
    3898: (
        "양부 \x1bCA오키츠네\x1bCZ 못지않은 주고쿠 제일의 무용으로,\n"
        "\x1bCB모리 가문\x1bCZ을 떠받치게 되었다."
    ),
    3899: "\x1bCC분고\x1bCZ의 다이묘 \x1bCA[b473]\x1bCZ 공―",
    3900: (
        "\x1bCB오토모 가문\x1bCZ 제20대 당주 \x1bCA오토모 요시아키\x1bCZ의 적자.\n"
        "다재다능했지만,\n"
        "태어날 때부터 병약한 인물이었다."
    ),
    3901: (
        "그런 \x1bCA[bm473]\x1bCZ 공이 온천 요양을 떠난다고 해도,\n"
        "수상하게 여길 사람은 없었다.\n"
        "하지만 \x1bCA[bm473]\x1bCZ 공의 노림수는 따로 있었다."
    ),
    3902: "\x1bCA[bm1730]\x1bCZ 공, 상황은 어떠한가?",
    3903: "모두 계획대로 진행되고 있습니다……",
    3904: (
        "후후후…… 그래, 그래!\n"
        "그렇다면 \x1bCA[bm1730]\x1bCZ 공, 그대는 \x1bCA뉴타\x1bCZ를 치도록 하라."
    ),
    3905: "예!\n계획대로 하겠습니다.",
    3906: "후후후, 하하하!\n이제 \x1bCB오토모\x1bCZ는 내 것이다!",
    3907: "아버님도 무르시군!\n내가 이런 때에\n온천 따위에 갈 리 없지!",
    3908: "…………",
    3909: (
        "나를 폐적하려 하다니…… 너무 무르다!\n"
        "나는 죽지 않는다, 결코 죽지 않아.\n"
        "원하는 모든 것을 손에 넣을 때까지!"
    ),
    3910: (
        "(\x1bCA[bm473]\x1bCZ 공이 때로 드러내는 어두운 패기……\n"
        "　이 나조차 눌릴 만큼 엄청나다.)"
    ),
    3911: (
        "(하지만 기복이 심한 분이다.\n"
        "　천하무쌍의 영걸 같은 모습도 있고,\n"
        "　유흥에 빠진 용렬한 장수의 모습도 있다……)"
    ),
    3912: "(고삐를 단단히 죄어야겠군.)",
    3913: (
        "\x1bCA[bm473]\x1bCZ 공의 아버지 \x1bCA오토모 요시아키\x1bCZ는 평소부터\n"
        "\x1bCA[bm473]\x1bCZ 공을 싫어해, 측실의 아들에게\n"
        "\x1bCB오토모 가문\x1bCZ을 잇게 하려 했다."
    ),
    3914: (
        "\x1bCA[bm473]\x1bCZ 공은 이를 알아채고 온천 요양을 구실로\n"
        "틈을 만들어 정변을 유도한 뒤, 행동을 일으킨 \x1bCA요시아키\x1bCZ를\n"
        "수하를 시켜 도리어 죽였다."
    ),
    3915: (
        "\x1bCB오토모씨\x1bCZ의 저택 2층에서 일어난 일이기에,\n"
        "이 사건은 보통\n"
        "'니카이쿠즈레의 변'이라 불린다."
    ),
    3916: (
        "힘으로 아버지를 넘어선 \x1bCA[bm473]\x1bCZ 공은 \x1bCB오토모 가문\x1bCZ의\n"
        "당주가 되어 \x1bCA[b1730]\x1bCZ 등 뛰어난 무장을 거느리고,\n"
        "마침내 \x1bCC규슈\x1bCZ를 석권해 갔다……"
    ),
    3917: (
        "가마쿠라 막부 고케닌인 \x1bCB도이씨\x1bCZ에서 비롯되어,\n"
        "뛰어난 수군을 거느린 \x1bCC산요\x1bCZ의 명문 \x1bCB고바야카와 가문\x1bCZ―"
    ),
    3918: (
        "\x1bCB누타\x1bCZ와 \x1bCB다케하라\x1bCZ 두 가문으로 갈라진 뒤,\n"
        "젊은 당주들이 잇달아 죽으며 세력이 쇠했다.\n"
        "\x1bCA모리 모토나리\x1bCZ는 이를 기회로 보았다."
    ),
    3919: (
        "\x1bCB고바야카와 가문\x1bCZ의 무력을 다시 살리려고,\n"
        "\x1bCA모토나리\x1bCZ는 \x1bCA오우치 요시타카\x1bCZ까지 끌어들여 움직였다."
    ),
    3920: (
        "\x1bCA요시타카\x1bCZ의 강력한 후원을 받아,\n"
        "\x1bCA모토나리\x1bCZ의 셋째 아들 \x1bCA다카카게\x1bCZ가 성을 바꾸고\n"
        "\x1bCB다케하라 고바야카와 가문\x1bCZ의 당주가 되었다."
    ),
    3921: (
        "나를 \x1bCC야마구치\x1bCZ에 맡긴 보람이 있었다……\n"
        "아버님께서는 그렇게 생각하시겠지요?"
    ),
    3922: (
        "후후후.\n"
        "분명 \x1bCA요시타카\x1bCZ가 뜻대로 움직인 것은\n"
        "\x1bCA다카카게\x1bCZ, 네가 있었기 때문이다."
    ),
    3923: (
        "이제부터 저는 \x1bCC산요\x1bCZ로 나아가,\n"
        "\x1bCB모리 가문\x1bCZ의 전진을 이끌겠습니다."
    ),
    3924: "음……\n말하지 않아도 알고 있구나?",
    3925: (
        "\x1bCB고바야카와\x1bCZ를 네게 맡긴 것은,\n"
        "네 지혜를 믿기 때문이다."
    ),
    3926: (
        "제 재주는 모두 아버님께 받은 것입니다.\n"
        "아버님처럼 계책을 잘 부려,\n"
        "\x1bCB모리 가문\x1bCZ을 위해 힘쓰겠습니다."
    ),
    3927: "그래, \x1bCB모리 가문\x1bCZ 도약의 화살이 되어라!",
    3928: (
        "얼마 뒤 \x1bCA다카카게\x1bCZ는 \x1bCB누타 고바야카와 가문\x1bCZ의 딸을 맞아,\n"
        "\x1bCB두 고바야카와 가문\x1bCZ을 통일하고,\n"
        "\x1bCB모리 가문\x1bCZ을 떠받칠 수군력을 손에 넣었다."
    ),
    3929: (
        "그리고 수군뿐 아니라\n"
        "\x1bCA다카카게\x1bCZ는 지략으로 \x1bCB모리 가문\x1bCZ의 세력을\n"
        "\x1bCC산요\x1bCZ 방면으로 넓히는 임무도 맡았다……"
    ),
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    3820: ["miyoshi_yukinaga_and_hosokawa_keicho_readings_require_review"],
    3846: ["speaker_sessai_identity_requires_officer_overlay_review"],
    3855: ["kazai_and_kanto_kanrei_terms_require_glossary_review"],
    3857: ["fuchu_nagao_rebellion_narrative_requires_semantic_review"],
    3861: ["sakato_castle_reading_requires_glossary_review"],
    3877: ["kokujin_term_requires_glossary_review"],
    3881: ["kikkawa_okitsune_reading_requires_review"],
    3882: ["gassan_toda_castle_reading_requires_glossary_review"],
    3899: ["dynamic_otomo_yoshishige_name_requires_officer_overlay_review"],
    3902: ["dynamic_bekki_akitsura_identity_requires_officer_overlay_review"],
    3904: ["nyuta_name_reading_requires_review"],
    3915: ["nikai_kuzure_incident_term_requires_glossary_review"],
    3918: ["nuta_kobayakawa_reading_requires_review"],
}


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
    if len(ids) != 111 or ids != sorted(TRANSLATIONS):
        raise ValueError("batch7 ids are not the exact 111 displayed entries")
    return ids


def event_for(entry_id: int) -> str:
    matches = [
        event["event_id"]
        for event in EVENTS
        if event["start_id"] <= entry_id <= event["end_id"]
    ]
    if len(matches) != 1:
        raise ValueError(f"id {entry_id} does not map to one batch7 event group")
    return str(matches[0])


def source_structure(text: str) -> dict[str, Any]:
    value = shared.source_structure(text)
    value["bracket_tokens"] = BRACKET_TOKEN_RE.findall(text)
    return value


def public_script_counts(text: str) -> dict[str, int]:
    return shared.public_script_counts(text)


def build(args: argparse.Namespace) -> dict[str, Any]:
    ids = selected_ids()
    loaded = {
        language: source_shared.load_source(path, language)
        for language, path in {
            "SC": args.stock_sc,
            "JP": args.stock_jp,
            "EN": args.stock_en,
        }.items()
    }
    tables = {language: value[2] for language, value in loaded.items()}

    display_failures = [
        entry_id
        for entry_id in ids
        if len(
            {
                tables[language].texts[entry_id]
                for language in ("SC", "JP", "EN")
            }
        )
        == 1
    ]
    if display_failures:
        raise ValueError(
            f"batch7 range contains all-language shared internal keys: {display_failures}"
        )

    overlay_entries: list[dict[str, Any]] = []
    evidence_entries: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for entry_id in ids:
        source_sc = tables["SC"].texts[entry_id]
        replacement = TRANSLATIONS[entry_id]
        problems = common.invariant_mismatches(source_sc, replacement)
        source_tokens = BRACKET_TOKEN_RE.findall(source_sc)
        replacement_tokens = BRACKET_TOKEN_RE.findall(replacement)
        if source_tokens != replacement_tokens:
            problems.append(
                f"bracket_tokens: source={source_tokens!r}, ko={replacement_tokens!r}"
            )
        if problems:
            failures.append({"id": entry_id, "problems": problems})
        overlay_entries.append(
            {
                "id": entry_id,
                "source_sc_utf16le_sha256": common.text_hash(source_sc),
                "ko": replacement,
            }
        )
        evidence_entries.append(
            {
                "id": entry_id,
                "event_id": event_for(entry_id),
                "references": {
                    language: {
                        "utf16le_sha256": common.text_hash(
                            tables[language].texts[entry_id]
                        ),
                        "structure": source_structure(tables[language].texts[entry_id]),
                    }
                    for language in ("SC", "JP", "EN")
                },
                "manual_semantic_crosscheck": True,
            }
        )
    if failures:
        raise ValueError(f"replacement invariants failed: {failures}")

    sc_packed, sc_raw, _ = loaded["SC"]
    overlay = {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": "MSG_PK/SC/msgev.bin",
        "base_language": "SC",
        "entry_count": len(ids),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "size": len(sc_packed),
            "packed_sha256": sha256(sc_packed),
            "raw_size": len(sc_raw),
            "raw_sha256": sha256(sc_raw),
            "string_count": STRING_COUNT,
        },
        "defaults": {"status": "translated"},
        "entries": overlay_entries,
    }
    common.validate_overlay_shape(overlay)

    boundary_ids = (
        3818,
        3819,
        3839,
        3840,
        3854,
        3855,
        3879,
        3880,
        3898,
        3899,
        3916,
        3917,
        3929,
        3930,
    )
    evidence = {
        "schema": "nobu16.kr.event-dialogue-alignment-evidence.v7",
        "batch_id": BATCH_ID,
        "resource": "msgev",
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "selected_entry_count": len(ids),
            "excluded_internal_entry_count": 0,
        },
        "alignment_basis": [
            "same_resource_role",
            "same_17910_entry_count",
            "same_numeric_string_ids",
            "manual_semantic_crosscheck_of_selected_entries",
            "no_all_language_shared_internal_keys_in_selected_range",
        ],
        "source_files": {
            language: {**SOURCE_PINS[language], "string_count": STRING_COUNT}
            for language in ("SC", "JP", "EN")
        },
        "event_groups": list(EVENTS),
        "boundary_anchors": [
            {
                "id": entry_id,
                "reference_hashes": {
                    language: common.text_hash(tables[language].texts[entry_id])
                    for language in ("SC", "JP", "EN")
                },
            }
            for entry_id in boundary_ids
        ],
        "excluded_internal_entries": [],
        "entry_count": len(ids),
        "entries": evidence_entries,
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.event-dialogue-review-index.v7",
        "batch_id": BATCH_ID,
        "quality_state": "draft_not_human_or_runtime_reviewed",
        "entry_count": len(ids),
        "entries": [
            {
                "id": entry_id,
                "event_id": event_for(entry_id),
                "status": "translated",
                "translation_origin": "assistant_generated_draft_from_pinned_sc_jp_en",
                "automated_draft": True,
                "human_review_required": True,
                "runtime_reviewed": False,
                "uncertainty_flags": UNCERTAINTY_FLAGS.get(entry_id, []),
            }
            for entry_id in ids
        ],
        "contains_commercial_source_text": False,
    }

    out_root = args.out_root.resolve()
    artifacts: dict[str, dict[str, Any]] = {}
    artifacts["overlay"] = write_json(
        out_root / "public" / OVERLAY_NAME, overlay, f"public/{OVERLAY_NAME}"
    )
    artifacts["alignment_evidence"] = write_json(
        out_root / "evidence" / EVIDENCE_NAME,
        evidence,
        f"evidence/{EVIDENCE_NAME}",
    )
    artifacts["review_index"] = write_json(
        out_root / "review" / REVIEW_NAME, review, f"review/{REVIEW_NAME}"
    )

    public_paths = {
        "overlay": out_root / "public" / OVERLAY_NAME,
        "alignment_evidence": out_root / "evidence" / EVIDENCE_NAME,
        "review_index": out_root / "review" / REVIEW_NAME,
    }
    source_free_scan = {
        name: public_script_counts(path.read_text(encoding="utf-8"))
        for name, path in public_paths.items()
    }
    if any(
        value != {"cjk_unified_count": 0, "kana_count": 0}
        for value in source_free_scan.values()
    ):
        raise ValueError("batch7 public artifact contains source-script text")

    visible_lengths = {
        entry_id: [
            len(common.ESC_RE.sub("", line))
            for line in TRANSLATIONS[entry_id].splitlines()
        ]
        for entry_id in ids
    }
    validation = {
        "schema": "nobu16.kr.event-dialogue-generation-validation.v7",
        "batch_id": BATCH_ID,
        "passed": True,
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "selected_entry_count": len(ids),
            "selected_ids_sha256": sha256(
                json.dumps(ids, separators=(",", ":")).encode("utf-8")
            ),
            "excluded_internal_entry_count": 0,
            "excluded_internal_ids_sha256": sha256(b"[]"),
        },
        "source_alignment": {
            "languages": ["SC", "JP", "EN"],
            "string_count_each": STRING_COUNT,
            "selected_reference_hash_count": len(ids) * 3,
            "manual_semantic_crosschecks": len(ids),
        },
        "replacement_invariants": {
            "checked": len(ids),
            "failures": 0,
            "custom_bracket_placeholder_checks": len(ids),
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "edge_whitespace",
                "esc_sequences_in_order",
                "control_characters",
                "line_break_sequence",
                "private_use_codepoints",
                "custom_bracket_placeholders_in_order",
            ],
        },
        "translation_status": {
            "translated_draft": len(ids),
            "human_review_required": len(ids),
            "runtime_reviewed": 0,
            "specific_uncertainty_entries": len(UNCERTAINTY_FLAGS),
        },
        "layout_heuristic": {
            "max_authored_line_codepoints_excluding_esc": max(
                length for lengths in visible_lengths.values() for length in lengths
            ),
            "entries_over_32": [
                entry_id
                for entry_id, lengths in visible_lengths.items()
                if max(lengths) > 32
            ],
            "runtime_layout_review_required": True,
        },
        "font_integration": {
            "state": "deferred_not_computed",
            "current_font_or_installer_must_not_include_batch7": True,
        },
        "source_free_scan": source_free_scan,
        "artifacts": artifacts,
        "generator": {
            "path": SCRIPT_PATH.name,
            "sha256": sha256(SCRIPT_PATH.read_bytes()),
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
            "existing_v01_v02_v03_v04_v05_v06_artifacts_modified": False,
        },
    }
    artifacts["generation_validation"] = write_json(
        out_root / VALIDATION_NAME, validation, VALIDATION_NAME
    )
    return {"out_root": out_root, "entry_count": len(ids), "artifacts": artifacts}


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
