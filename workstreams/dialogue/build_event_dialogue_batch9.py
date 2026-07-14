#!/usr/bin/env python3
"""Build source-free Korean historical event dialogue batch9 (4032-4160)."""

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
import build_event_dialogue_batch8 as shared  # noqa: E402


BATCH_ID = "msgev_historical_events_4032_4160.v0.9"
OVERLAY_NAME = "msgev_ko_historical_events_4032_4160.v0.9.json"
EVIDENCE_NAME = "alignment_evidence.v0.9.json"
REVIEW_NAME = "review_index.v0.9.json"
VALIDATION_NAME = "validation.v0.9.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 4032
SCOPE_END = 4160
EXCLUDED_INTERNAL_IDS: tuple[int, ...] = ()
BRACKET_TOKEN_RE = re.compile(r"\[[a-z0-9_]+\]")

EVENTS = (
    {
        "event_id": "uesugi_norimasa_echigo_exile",
        "title_ko": "우에스기 노리마사의 에치고 망명",
        "start_id": 4032,
        "end_id": 4055,
        "selected_count": 24,
    },
    {
        "event_id": "murakami_yoshikiyo_exile",
        "title_ko": "무라카미 요시키요의 몰락과 망명",
        "start_id": 4056,
        "end_id": 4087,
        "selected_count": 32,
    },
    {
        "event_id": "kaizu_castle_kitsutsuki_strategy",
        "title_ko": "가이즈성 축성과 딱따구리 전법",
        "start_id": 4088,
        "end_id": 4104,
        "selected_count": 17,
    },
    {
        "event_id": "hirate_masahide_remonstrative_suicide",
        "title_ko": "히라테 마사히데의 간언과 자결",
        "start_id": 4105,
        "end_id": 4127,
        "selected_count": 23,
    },
    {
        "event_id": "uesugi_masatora_becomes_terutora",
        "title_ko": "우에스기 마사토라, 데루토라로 개명",
        "start_id": 4128,
        "end_id": 4133,
        "selected_count": 6,
    },
    {
        "event_id": "asakura_soteki_creed",
        "title_ko": "아사쿠라 소테키의 승리관",
        "start_id": 4134,
        "end_id": 4138,
        "selected_count": 5,
    },
    {
        "event_id": "asakura_soteki_death",
        "title_ko": "아사쿠라 소테키의 죽음",
        "start_id": 4139,
        "end_id": 4160,
        "selected_count": 22,
    },
)

TRANSLATIONS: dict[int, str] = {
    4032: (
        "간토 간레이는 가마쿠라 구보를 보좌하는 요직이다.\n"
        "무로마치 막부 초기를 빼면, 역대 \x1bCB우에스기 가문\x1bCZ 당주는\n"
        "교토의 쇼군이 직접 임명했다."
    ),
    4033: (
        "분가가 많던 \x1bCB우에스기 가문\x1bCZ에서,\n"
        "종가인 \x1bCB야마노우치 우에스기 가문\x1bCZ은 \x1bCB에치고 우에스기 가문\x1bCZ에서\n"
        "\x1bCA노리자네\x1bCZ·\x1bCA아키사다\x1bCZ 등 많은 양자를 들였다……"
    ),
    4034: (
        "교토쿠의 난 이후,\n"
        "세력을 키운 분가·\x1bCB오기야쓰 우에스기 가문\x1bCZ과 대립했고,\n"
        "마침내 조쿄의 난이 일어났다."
    ),
    4035: (
        "이 내란에는 \x1bCB고가쿠보 가문\x1bCZ까지 휘말렸다.\n"
        "\x1bCC간토\x1bCZ가 피폐해지는 동안, \x1bCB오기야쓰 가문\x1bCZ이 불러들인\n"
        "맹호·\x1bCA호조 소운\x1bCZ이 어부지리를 얻었다."
    ),
    4036: (
        "\x1bCA소운\x1bCZ은 본래 \x1bCB스루가 이마가와 가문\x1bCZ의 일개 책사였으나,\n"
        "원군을 청한 \x1bCB오기야쓰 가문\x1bCZ뿐 아니라\n"
        "\x1bCB야마노우치 가문\x1bCZ의 세력도 차례로 흡수했다."
    ),
    4037: (
        "\x1bCA소운\x1bCZ의 손자 \x1bCA우지야스\x1bCZ 대에 이르러,\n"
        "가와고에 전투에서 \x1bCB오기야쓰 가문\x1bCZ을 멸망시켰고,\n"
        "이제 적류인 \x1bCB야마노우치 우에스기 가문\x1bCZ마저 없애려 했다."
    ),
    4038: (
        "\x1bCA우지야스\x1bCZ 이놈……\n"
        "간토 간레이이자 \x1bCB야마노우치 우에스기 가문\x1bCZ 당주인 내게\n"
        "이런 무례를 범하다니, 용서 못 한다!!"
    ),
    4039: (
        "\x1bCB야마노우치\x1bCZ의 나리께선 참 태평하시군.\n"
        "낡은 권위밖에 붙들 것이 없는 명문가는\n"
        "이토록 썩어 버리는가."
    ),
    4040: (
        "간토 간레이가 대체 얼마나 대단한 자리인가?\n"
        "그런 칭호라면 내 아버지 \x1bCA우지쓰나\x1bCZ도\n"
        "진작에 자칭하셨다."
    ),
    4041: (
        "혈통이 중요한가, 실력이 중요한가……\n"
        "이제 저 태평한 나리에게\n"
        "똑똑히 가르쳐 줘야겠군."
    ),
    4042: (
        "제길…… 간토 간레이이자 \x1bCB우에스기\x1bCZ의 당주인 내가\n"
        "이런 곳에서 죽을 수는 없다!"
    ),
    4043: (
        "나는 절대 죽지 않는다!\n"
        "반드시 \x1bCC간토\x1bCZ를 내 손으로 되찾겠다!\n"
        "명심해 둬라!"
    ),
    4044: (
        "\x1bCA우에스기 노리마사\x1bCZ는 \x1bCB호조군\x1bCZ의 포위를 벗어나,\n"
        "\x1bCC에치고\x1bCZ로 멀리 달아났다.\n"
        "\x1bCC간토\x1bCZ에 전란을 부른 간토 간레이직과 함께……"
    ),
    4045: "\x1bCC에치고\x1bCZ·\x1bCC가스가야마성\x1bCZ―",
    4046: (
        "그렇군. \x1bCA호조 우지야스\x1bCZ에게 패해,\n"
        "우리 \x1bCC에치고\x1bCZ까지 피신하셨다는 말씀이군요."
    ),
    4047: (
        "우리 \x1bCB야마노우치 우에스기 가문\x1bCZ과 \x1bCB에치고 우에스기 가문\x1bCZ은\n"
        "대대로 가까웠네. \x1bCB에치고 우에스기 가문\x1bCZ은 이미 사라졌지만,\n"
        "그 가재인 \x1bCB나가오 가문\x1bCZ은 내 일가나 다름없지."
    ),
    4048: (
        "망할 \x1bCB호조\x1bCZ 놈들은 멋대로 간토 간레이를 칭하고 있네.\n"
        "\x1bCB우에스기\x1bCZ를 대표하는 자로서 용납할 수 없지.\n"
        "무슨 수를 써서라도 \x1bCB호조\x1bCZ를 멸해야 하네."
    ),
    4049: (
        "이를 위해서라면 \x1bCB야마노우치 우에스기 가문\x1bCZ의 가독과,\n"
        "간토 간레이직까지 그대에게 넘겨도\n"
        "좋다고 생각하네……"
    ),
    4050: (
        "아니, 그게 무슨 말씀이십니까!\n"
        "가신의 가신에 불과한 제게 야마노우치 가독을요?\n"
        "분에 넘치는 영광입니다……"
    ),
    4051: (
        "하지만 간토 간레이직은 본래,\n"
        "교토에 계신 \x1bCA구보\x1bCZ 님께서 임명하셔야 할 자리.\n"
        "여기서 받는 것은 사양하겠습니다……"
    ),
    4052: (
        "그런 절차는 나중에 밟으면 되네!\n"
        "우, 우선 \x1bCB호조\x1bCZ를 멸하고 \x1bCC간토\x1bCZ를\n"
        "\x1bCB우에스기 가문\x1bCZ의 손에 돌려주게…… 부탁하네!"
    ),
    4053: (
        "저 \x1bCA가게토라\x1bCZ, 그 말씀을 잊지 않겠습니다.\n"
        "모든 준비를 마치고 때가 오면 반드시 \x1bCA노리마사\x1bCZ 님을\n"
        "\x1bCC간토\x1bCZ로 모시고 가겠습니다……"
    ),
    4054: (
        "갈 곳 잃은 간토 간레이·\x1bCA우에스기 노리마사\x1bCZ는 이렇게\n"
        "\x1bCC에치고\x1bCZ로 물러났다. 가독과 간레이직의 양도를 약속하고,\n"
        "\x1bCB나가오 가문\x1bCZ의 보호를 받게 되었다."
    ),
    4055: (
        "\x1bCA노리마사\x1bCZ는 \x1bCC후추\x1bCZ(오늘날 \x1bCC조에쓰시\x1bCZ)에서,\n"
        "옛 \x1bCB에치고 우에스기 가문\x1bCZ의 슈고소 터에\n"
        "\x1bCC오타테\x1bCZ라는 저택을 짓고 살았다고 한다."
    ),
    4056: (
        "과거 여러 차례\n"
        "\x1bCA[bm1251]\x1bCZ 공에게 쓴맛을 안긴 \x1bCA무라카미 요시키요\x1bCZ도,\n"
        "마침내 궁지에 몰릴 때가 왔다."
    ),
    4057: (
        "\x1bCB다케다군\x1bCZ에 가담한 \x1bCA사나다 유키타카\x1bCZ의 조략으로,\n"
        "가신들이 잇달아 배신한 것이다……"
    ),
    4058: (
        "이, 이놈 \x1bCA[bm1251]\x1bCZ……!\n"
        "전투로는 나를 이기지 못하니,\n"
        "이런 간사한 수를 쓰는구나!"
    ),
    4059: (
        "비겁한 놈, 기억해 둬라!\n"
        "이 빚은 반드시 갚아 주마!!"
    ),
    4060: "\x1bCB다케다군\x1bCZ·\x1bCA[bm1251]\x1bCZ 공의 본진―",
    4061: "여기까지 오는 길이 참 길었군……",
    4062: "예.\n하지만 마침내 이 땅을 되찾았습니다.",
    4063: "이 모든 것은,\n주군의 도움이 있었기에 가능했습니다.",
    4064: (
        "빈말은 됐다.\n"
        "내가 몇 번을 공격해도 못 뺏은 이 성을\n"
        "그대는 단숨에 떨어뜨렸지."
    ),
    4065: "내 힘 덕분만은 아닐 터……\n그대에게 있고, 내게 없는 것은 무엇인가?",
    4066: (
        "싸우지 않고 이기는 것이 병법의 극의.\n"
        "성을 치는 건 하책, 마음을 치는 것이 상책입니다.\n"
        "조략에 이기면 전투는 팔 할을 이긴 셈이지요."
    ),
    4067: (
        "……그렇다 해도,\n"
        "제 조략이 효과를 거둘 수 있었던 것은\n"
        "오직 주군의 위세와 군세 덕분입니다."
    ),
    4068: (
        "그런가……\n"
        "즉, 내 군세가 있었다면\n"
        "굳이 싸울 필요도 없었다는 말이군."
    ),
    4069: (
        "싸우지 않고 이긴다……\n"
        "안다고 생각했지만,\n"
        "마음 한구석이 늘 조급했던 모양이군."
    ),
    4070: "역시 나도 아버지의 아들인가……",
    4071: "……",
    4072: "고맙다, \x1bCA유키타카\x1bCZ!\n내 미숙함을 또 하나 깨달았구나.",
    4073: "며칠 뒤.\n\x1bCB[bs1448] 가문\x1bCZ·\x1bCC가스가야마성\x1bCZ―",
    4074: "염치를 무릅쓰고 청하오!\n부디 이 \x1bCA요시키요\x1bCZ에게 힘을 빌려주시오!",
    4075: (
        "원수 \x1bCA[bm1251]\x1bCZ를 치고,\n"
        "\x1bCC시나노\x1bCZ로 돌아갈 수만 있다면,\n"
        "어떤 고난도 마다하지 않겠소!!"
    ),
    4076: "……고개를 드시오, \x1bCA요시키요\x1bCZ 공.",
    4077: "예!",
    4078: (
        "한 가지 묻겠소.\n"
        "왜 나에게 도움을 청하는 거요?\n"
        "다른 사람에게 부탁할 생각은 없었소?"
    ),
    4079: (
        "없었소……\n"
        "이 일대에서 가장 싸움에 능한 분은\n"
        "\x1bCA가게토라\x1bCZ 님이라고 알고 있었기 때문이오."
    ),
    4080: (
        "나를 꺾은 \x1bCA[bm1251]\x1bCZ에게 이길 수 있는 분은,\n"
        "\x1bCA가게토라\x1bCZ 님밖에 없소!"
    ),
    4081: "후, 후후……\n싸움에 능하다라. 좋은 대답이오.",
    4082: "좋소.\n내 힘을 빌려주겠소……",
    4083: "가, 감개무량하오!",
    4084: (
        "감사할 것 없소.\n"
        "\x1bCA[bm1251]\x1bCZ 공이 \x1bCC젠코지다이라\x1bCZ에서 멋대로 굴게 두면,\n"
        "우리에게도 훗날 걸림돌이 될 테니."
    ),
    4085: (
        "무엇보다……\n"
        "\x1bCA[bm1251]\x1bCZ의 힘이 어느 정도인지,\n"
        "나도 알아 두어야 하니까!"
    ),
    4086: (
        "\x1bCB무라카미 가문\x1bCZ의 멸망으로,\n"
        "\x1bCB다케다 가문\x1bCZ은 \x1bCC시나노 북부\x1bCZ에서 영향력을 넓혀\n"
        "\x1bCB[bs1448] 가문\x1bCZ과 이해관계가 충돌하게 되었다."
    ),
    4087: (
        "\x1bCA[b1251]\x1bCZ와 \x1bCA[b1448]\x1bCZ―\n"
        "숙명적인 싸움의 씨앗이,\n"
        "이곳에서 싹텄다……"
    ),
    4088: (
        "\x1bCA무라카미 요시키요\x1bCZ를 \x1bCC에치고\x1bCZ로 몰아내고,\n"
        "\x1bCC시나노 북부\x1bCZ 지배권을 굳힌 \x1bCA[b1251]\x1bCZ―"
    ),
    4089: (
        "축성의 명수·\x1bCA야마모토 간스케\x1bCZ의 설계로\n"
        "\x1bCC가이즈성\x1bCZ을 쌓아,\n"
        "다가올 \x1bCA[b1448]\x1bCZ의 침공에 대비했다."
    ),
    4090: (
        "하지만 침공에 대비해 세운 \x1bCC가이즈성\x1bCZ은\n"
        "뜻밖의 역할을 맡게 되었다."
    ),
    4091: "주군,\n사가미에서 사자가 왔습니다……",
    4092: "알고 있다.\n그렇게 전하고 돌려보내라.",
    4093: (
        "이거 참.\n"
        "동맹만 아니었다면 \x1bCC가이즈성\x1bCZ을 \x1bCA마사노부\x1bCZ에게 맡기고,\n"
        "군을 \x1bCC교토\x1bCZ로 향하게 했을 텐데."
    ),
    4094: (
        "\x1bCA[b1448]\x1bCZ의 맹공을 받아,\n"
        "사가미의 영웅 \x1bCA호조 우지야스\x1bCZ는\n"
        "본거지 \x1bCC오다와라성\x1bCZ까지 몰렸다."
    ),
    4095: (
        "고소슨 삼국동맹을 방패 삼아,\n"
        "\x1bCA[bm1251]\x1bCZ에게 \x1bCA[b1448]\x1bCZ 견제를 요청했다."
    ),
    4096: (
        "그 요청에 응해,\n"
        "\x1bCA[bm1251]\x1bCZ 공은 \x1bCC가이즈성\x1bCZ에 들어가 \x1bCC가스가야마성\x1bCZ을\n"
        "노리는 태세를 보이려 했다."
    ),
    4097: (
        "그렇지 않습니다, 주군.\n"
        "\x1bCB호조\x1bCZ가 우리 뒤를 지켜 주기에,\n"
        "주군께서 교토로 올라가실 수 있는 겁니다."
    ),
    4098: (
        "\x1bCA우지야스\x1bCZ……\n"
        "그 고집불통이 \x1bCA[bm1448]\x1bCZ를 막으면 될 것을.\n"
        "걸핏하면 우리에게 매달리는군."
    ),
    4099: (
        "그건 그렇다 치고, 지금 \x1bCA[bm1448]\x1bCZ는\n"
        "\x1bCC오다와라\x1bCZ를 포위하고 있다고 한다."
    ),
    4100: (
        "아무리 주군께서 \x1bCC가이즈\x1bCZ에 들어오셨어도,\n"
        "그자가 \x1bCC에치고\x1bCZ로 돌아갔다가\n"
        "군을 이끌고 오겠습니까?"
    ),
    4101: (
        "온다! 반드시 올 것이다!\n"
        "그게 바로 그 사내, \x1bCA[b1448]\x1bCZ!\n"
        "비사문천의 화신을 자처할 만한 장수다."
    ),
    4102: "그 비사문천을 칠 방책은?",
    4103: "있습니다.\n만반의 준비를 마쳤습니다.",
    4104: (
        "딱따구리 전법……\n"
        "제 최고의 군략으로,\n"
        "비사문천을 무찔러 보이겠습니다."
    ),
    4105: (
        "\x1bCA오다 노부나가\x1bCZ는 소년 시절 바보라 불렸다.\n"
        "골치를 앓던 아버지 \x1bCA노부히데\x1bCZ는 믿을 만한 노신들을\n"
        "\x1bCA노부나가\x1bCZ 곁에 두어 교육하게 했다."
    ),
    4106: (
        "그중 \x1bCA히라테 나카쓰카사노조 마사히데\x1bCZ는,\n"
        "\x1bCA노부나가\x1bCZ를 모시는 가신들의 중진으로서,\n"
        "거친 행동을 일삼는 \x1bCA노부나가\x1bCZ를 거듭 간했다."
    ),
    4107: (
        "\x1bCA노부히데\x1bCZ의 장례에서 기이한 난행을 보인 \x1bCA노부나가\x1bCZ 때문에\n"
        "새 당주를 불안해하는 가신이 많았고,\n"
        "\x1bCA마사히데\x1bCZ도 가슴 아파했다……"
    ),
    4108: (
        "\x1bCA노부히데\x1bCZ 님께서 돌아가신 뒤, \x1bCC오와리\x1bCZ를 다스리는\n"
        "자리에 올랐는데도 난행을 고칠 기미가 없다.\n"
        "내 교육이 부족했던 것인가……"
    ),
    4109: "영감, 자네 아들이 문제다.\n제대로 꾸짖어 둬라.",
    4110: "아니, 주군.\n못난 제 아들이 무슨 일을 저질렀습니까?",
    4111: (
        "\x1bCA고로에몬\x1bCZ이 가진 말이 대단한 명마라더군.\n"
        "내게 바치라 했더니, 그 녀석이\n"
        "절대 못 준다는 말만 되풀이하잖나!"
    ),
    4112: (
        "주군, 제 아들이라 감싸는 건 아닙니다만,\n"
        "\x1bCA고로에몬\x1bCZ의 말이 옳다고 생각합니다."
    ),
    4113: "뭐라고?",
    4114: (
        "무사는 언제나 가문과 주군을 지키고자,\n"
        "전투 준비를 갖추는 법…… 그중 말은\n"
        "무사에게 가장 중요한 군비입니다."
    ),
    4115: (
        "아무리 주군의 명령이라도, 유사시에\n"
        "그 주군을 지키며 싸우려면 평소부터\n"
        "말을 잘 돌보는 것이 당연한 도리입니다."
    ),
    4116: (
        "……여전히 영감은 고지식하군.\n"
        "\x1bCA고로에몬\x1bCZ도 아비를 쏙 빼닮았어.\n"
        "융통성 없는 것까지 똑같다니까!"
    ),
    4117: (
        "그 논리라면 명마를 주군에게 바쳐야\n"
        "전투에서 주군이 더 안전하지 않겠나.\n"
        "그쪽이 훨씬 충의다운 일이지!"
    ),
    4118: "……",
    4119: (
        "뭐, 됐다!\n"
        "나는 매사냥이나 다녀오마.\n"
        "\x1bCA고로에몬\x1bCZ에게 잘 일러 둬라!"
    ),
    4120: (
        "아아…… 이제 내가 무슨 말을 해도\n"
        "저 성정은 바뀌지 않으시겠지.\n"
        "내가 감당할 수 있는 분이 아니구나……"
    ),
    4121: (
        "\x1bCA노부히데\x1bCZ 님, 송구합니다.\n"
        "이 \x1bCA마사히데\x1bCZ, 평생 단 한 번만\n"
        "주군의 명을 거스르겠습니다."
    ),
    4122: (
        "제 목숨으로 \x1bCA노부나가\x1bCZ 님께 간하겠습니다!\n"
        "저 난행을 막을 방법은 이것뿐입니다.\n"
        "꾸지람은 저승에서 듣겠습니다……"
    ),
    4123: (
        "그날 밤, \x1bCA히라테 마사히데\x1bCZ가 할복했다는 소식에\n"
        "\x1bCA노부나가\x1bCZ는 경악했다."
    ),
    4124: (
        "영감! 왜 죽은 거냐!\n"
        "내 진심을…… 알아채지 못한 건가!\n"
        "그 잔소리도 이제 두 번 다시 못 듣는 건가!"
    ),
    4125: "영감…… 용서해라.\n용서해 줘……!",
    4126: (
        "아버지 \x1bCA노부히데\x1bCZ가 죽었을 때조차\n"
        "보이지 않았던 눈물이,\n"
        "그 눈에서 흘렀다고 한다……"
    ),
    4127: (
        "교육을 맡은 \x1bCA히라테 마사히데\x1bCZ의 죽음은 젊은 \x1bCA노부나가\x1bCZ에게\n"
        "큰 충격을 주었다. \x1bCA노부나가\x1bCZ는 그를 위해\n"
        "\x1bCC세이슈지\x1bCZ를 세우고 명복을 빌었다고 한다……"
    ),
    4128: (
        "그해, \x1bCA우에스기 마사토라\x1bCZ는 쇼군 \x1bCA아시카가 요시테루\x1bCZ에게\n"
        "이름 한 글자를 받아 ‘\x1bCA데루토라\x1bCZ’로 개명했다."
    ),
    4129: (
        "예전에 상경했을 때도 \x1bCA요시테루\x1bCZ가 권했지만,\n"
        "당시는 아직 간레이의 가신, 즉 쇼군의\n"
        "직속 가신이 아니었기에 한사코 사양했다."
    ),
    4130: (
        "이제 간토 간레이직과 \x1bCB우에스기\x1bCZ 가독을 이었으므로,\n"
        "쇼군의 직신으로서 \x1bCA요시테루\x1bCZ의 호의를 받아\n"
        "정식으로 이름을 바꾼 것이다."
    ),
    4131: (
        "얼마 전 \x1bCA마사토라\x1bCZ라는 이름을 받은 참이라,\n"
        "곧바로 또 개명하기는 송구스럽습니다만,\n"
        "구보 님께서 꼭 받으라 하셔서……"
    ),
    4132: (
        "괜찮네, 괜찮아. 쇼군께서 직접 제안하신 이름이니.\n"
        "내 이름보다 훨씬 귀한 법이지.\n"
        "사양 말고 마음 놓고 사용하게."
    ),
    4133: (
        "이렇게 ‘\x1bCA우에스기 데루토라\x1bCZ’가 탄생했다.\n"
        "29대에 이르는 간토 간레이직 역사에서 쇼군에게 직접\n"
        "이름 한 글자를 받은 것은 처음이었다."
    ),
    4134: "이겼나……\n싱거운 싸움이었군.",
    4135: (
        "아니…… 무사는 개라 불리든,\n"
        "짐승이라 불리든 이기는 것이 중요하지.\n"
        "이것으로 됐다……"
    ),
    4136: (
        "하지만……\n"
        "가슴 뛰고, 혼이 떨리는\n"
        "그런 싸움을 만나고 싶구나."
    ),
    4137: "“무사는 개라 불리든 짐승이라 불리든,\n　이기는 것이 근본이다.”",
    4138: (
        "60년 넘게 최전선에서 지휘하며,\n"
        "계속 승리한 \x1bCA소테키\x1bCZ의 이 말은\n"
        "수많은 무장의 가슴에 새겨졌다."
    ),
    4139: "\x1bCB아사쿠라 가문\x1bCZ의 중신·\x1bCA아사쿠라 소테키\x1bCZ―",
    4140: (
        "\x1bCB아사쿠라 가문\x1bCZ 당주·\x1bCA아사쿠라 요시카게\x1bCZ의 증조부와 형제로,\n"
        "가문의 군사를 도맡은 중진이었다."
    ),
    4141: (
        "그 역량은 확실하여,\n"
        "\x1bCA소테키\x1bCZ가 있는 한 그 누구도\n"
        "\x1bCC에치젠\x1bCZ 땅에 발을 들일 수 없었다."
    ),
    4142: "하지만 그 \x1bCA소테키\x1bCZ도 마침내 병으로 쓰러졌다……",
    4143: "\x1bCA소테키\x1bCZ 님.\n몸은 좀 어떠십니까?",
    4144: (
        "주군, 저를 ‘\x1bCA소테키\x1bCZ 님’이라 부르지 마십시오.\n"
        "\x1bCA아사쿠라\x1bCZ의 당주께서 그런 말씨를\n"
        "쓰셔서는 안 됩니다!"
    ),
    4145: "음……\n정말 미안하네.",
    4146: (
        "하지만 \x1bCA소테키\x1bCZ 님은 \x1bCA아사쿠라\x1bCZ의 주춧돌.\n"
        "예를 갖추지 않을 수는 없으니……"
    ),
    4147: "……이삼 일 뒤면 다시 출사하겠습니다.\n부디 안심하고 기다리십시오.",
    4148: "그, 그런가!\n그렇다면……",
    4149: "후, 후후후후……\n저리도 유약한 자가 \x1bCA아사쿠라\x1bCZ의 당주인가!",
    4150: "내가 조금 너무 오래 산 모양이군.\n이제 일문 친족의 얼굴조차 잘 모르겠어!",
    4151: (
        "형님의 피를 이은 당주들을 줄곧 떠받쳤지만……\n"
        "역시 모반해 내가 당주가 됐어야 했나.\n"
        "일생일대의 실수였구나!"
    ),
    4152: (
        "\x1bCA소테키\x1bCZ는 한때 \x1bCB아사쿠라 가문\x1bCZ 당주 자리를 노려\n"
        "모반을 꾀했으나, 거사 직전 마음을 돌려\n"
        "공모자를 밀고한 과거가 있었다……"
    ),
    4153: (
        "셀 수 없이 많은 전장을 누볐다.\n"
        "하지만 단 한 번도 죽음을 두려워하지 않았지.\n"
        "이제 와 발버둥 칠 생각도 없다…… 다만……"
    ),
    4154: (
        "\x1bCA오다 노부히데\x1bCZ의 아들…… \x1bCA노부나가\x1bCZ라고 했나……\n"
        "지금은 어떤 사내로 자랐을까.\n"
        "3년만 더 살아 그 앞날을 보고 싶었는데……"
    ),
    4155: (
        "그 얼간이……\n"
        "언젠가 \x1bCC에치젠\x1bCZ에 쳐들어올지도 모르지.\n"
        "그리되면 \x1bCA요시카게\x1bCZ 따윈 버티지 못할 텐데……"
    ),
    4156: "후후, 난세인가……\n무사란 이래서 재미있어.",
    4157: (
        "\x1bCA아사쿠라 소테키\x1bCZ는 한때 \x1bCA오다 노부히데\x1bCZ와 함께,\n"
        "\x1bCA사이토 도산\x1bCZ과 맞서 싸운 적이 있었다."
    ),
    4158: (
        "그때의 인연 때문인지,\n"
        "이 명장은 최후의 순간까지 \x1bCA오다 노부나가\x1bCZ의\n"
        "앞날에 관심을 두었다고 전한다."
    ),
    4159: (
        "승리야말로 무사의 본분.\n"
        "그 말대로 계속 승리한 참된 무사,\n"
        "\x1bCA아사쿠라 소테키\x1bCZ는 조용히 생을 마쳤다."
    ),
    4160: (
        "그가 죽은 뒤 \x1bCA아사쿠라\x1bCZ에는,\n"
        "유약한 당주만 남았다……"
    ),
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    4032: ["kanto_kanrei_and_kamakura_kubo_terms_require_glossary_review"],
    4033: ["uesugi_branch_and_norizane_akisada_names_require_review"],
    4034: ["kyotoku_and_chokyo_war_readings_require_review"],
    4035: ["koga_kubo_and_ogigayatsu_terms_require_glossary_review"],
    4040: ["ujitsuna_spelling_follows_existing_dialogue_convention"],
    4053: ["sc_first_person_kagetora_resolves_en_speaker_error"],
    4055: ["fuchu_joetsu_otate_and_shugosho_terms_require_review"],
    4066: ["strategy_maxim_requires_style_review"],
    4084: ["zenkojidaira_reading_requires_review"],
    4089: ["kaizu_castle_reading_requires_glossary_review"],
    4093: ["alliance_meaning_resolved_against_jp_en_due_awkward_sc"],
    4095: ["kososun_triple_alliance_term_requires_glossary_review"],
    4104: ["woodpecker_strategy_term_requires_glossary_review"],
    4106: ["hirate_court_title_reading_requires_review"],
    4111: ["goroemon_reading_requires_officer_review"],
    4127: ["seishuji_temple_reading_requires_review"],
    4128: ["terutora_name_and_henki_paraphrase_require_review"],
    4133: ["twenty_ninth_generation_resolved_against_sc_jp_due_en_error"],
    4137: ["soteki_maxim_requires_specialist_style_review"],
    4141: ["defensive_meaning_resolved_against_sc_jp_due_reversed_en"],
    4151: ["soteki_rebellion_anecdote_requires_historical_review"],
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
    if len(ids) != 129 or ids != sorted(TRANSLATIONS):
        raise ValueError("batch9 ids are not the exact 129 displayed entries")
    return ids


def event_for(entry_id: int) -> str:
    matches = [
        event["event_id"]
        for event in EVENTS
        if event["start_id"] <= entry_id <= event["end_id"]
    ]
    if len(matches) != 1:
        raise ValueError(f"id {entry_id} does not map to one batch9 event group")
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
            f"batch9 range contains all-language shared internal keys: {display_failures}"
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
        4031,
        4032,
        4055,
        4056,
        4087,
        4088,
        4104,
        4105,
        4127,
        4128,
        4133,
        4134,
        4138,
        4139,
        4160,
        4161,
    )
    evidence = {
        "schema": "nobu16.kr.event-dialogue-alignment-evidence.v9",
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
        "schema": "nobu16.kr.event-dialogue-review-index.v9",
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
        raise ValueError("batch9 public artifact contains source-script text")

    visible_lengths = {
        entry_id: [
            len(common.ESC_RE.sub("", line))
            for line in TRANSLATIONS[entry_id].splitlines()
        ]
        for entry_id in ids
    }
    entries_over_32 = [
        entry_id
        for entry_id, lengths in visible_lengths.items()
        if max(lengths) > 32
    ]
    validation = {
        "schema": "nobu16.kr.event-dialogue-generation-validation.v9",
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
            "entries_over_32": entries_over_32,
            "source_fixed_linebreak_exceptions": [
                entry_id
                for entry_id in entries_over_32
                if "\n" not in tables["SC"].texts[entry_id]
            ],
            "runtime_layout_review_required": True,
        },
        "font_integration": {
            "state": "deferred_not_computed",
            "current_font_or_installer_must_not_include_batch9": True,
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
            "common_builder_or_other_workstream_modified": False,
            "existing_v01_v02_v03_v04_v05_v06_v07_v08_artifacts_modified": False,
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
