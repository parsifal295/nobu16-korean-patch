#!/usr/bin/env python3
"""Build source-free Korean historical ending dialogue batch3 (3309-3440)."""

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
import build_event_dialogue_batch2 as shared  # noqa: E402


BATCH_ID = "msgev_event_endings_3311_3440.v0.3"
OVERLAY_NAME = "msgev_ko_event_endings_3311_3440.v0.3.json"
EVIDENCE_NAME = "alignment_evidence.v0.3.json"
REVIEW_NAME = "review_index.v0.3.json"
VALIDATION_NAME = "validation.v0.3.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 3309
SCOPE_END = 3440
EXCLUDED_INTERNAL_IDS = (
    3309,
    3310,
    3314,
    3315,
    3319,
    3320,
    3324,
    3325,
    3329,
    3330,
    3334,
    3335,
    3339,
    3340,
    3344,
    3345,
    3349,
    3350,
)
INTERNAL_KEY_RE = re.compile(r"event_ending_region_[a-z0-9_]+\Z")
BRACKET_TOKEN_RE = re.compile(r"\[[a-z0-9_]+\]")

EVENTS = (
    {
        "event_id": "regional_unification_endings",
        "title_ko": "지역 통일 엔딩",
        "start_id": 3311,
        "end_id": 3353,
        "selected_count": 27,
    },
    {
        "event_id": "imperial_office_choice",
        "title_ko": "조정 관직 선택",
        "start_id": 3354,
        "end_id": 3384,
        "selected_count": 31,
    },
    {
        "event_id": "national_unification_prologue",
        "title_ko": "천하통일 선언",
        "start_id": 3385,
        "end_id": 3394,
        "selected_count": 10,
    },
    {
        "event_id": "office_based_unification_results",
        "title_ko": "관직별 통일 결과",
        "start_id": 3395,
        "end_id": 3402,
        "selected_count": 8,
    },
    {
        "event_id": "long_term_regime_endings",
        "title_ko": "장기 정권 결말",
        "start_id": 3403,
        "end_id": 3440,
        "selected_count": 38,
    },
)

TRANSLATIONS: dict[int, str] = {
    3311: (
        "수도에서 멀리 떨어진 \x1bCC오우\x1bCZ에서는,\n"
        "무로마치 막부가 열린 이래 다이묘의 다툼이 끊이지 않아\n"
        "전쟁이 그칠 날이 없었지만……"
    ),
    3312: "적극적으로 세력을 넓힌 \x1bCB[bus]\x1bCZ 가문에 의해,\n마침내 \x1bCC도호쿠\x1bCZ 지방은 통일을 맞았다.",
    3313: "전국에는 아직 전쟁의 불길이 남았지만,\n이 \x1bCC오우\x1bCZ는 \x1bCB[bus]\x1bCZ 가문의 지배 아래\n한동안 평화를 누렸다……",
    3316: "무로마치 막부가 열린 이래 세력들의 이해가 얽혀,\n\x1bCC간토\x1bCZ에서는 늘 전쟁이 일어나는 것이\n당연하게 여겨졌지만…… ",
    3317: "적극적으로 세력을 넓힌 \x1bCB[bus]\x1bCZ 가문에 의해,\n마침내 \x1bCC간토\x1bCZ 지방은 통일을 맞았다.",
    3318: "전국에는 아직 전쟁의 불길이 남았지만,\n이 \x1bCC간토\x1bCZ는 \x1bCB[bus]\x1bCZ 가문의 지배 아래\n한동안 평화를 누렸다……",
    3321: "중앙과 지방을 잇는 요충지 \x1bCC호쿠리쿠\x1bCZ는\n\x1bCC기나이\x1bCZ·\x1bCC간토\x1bCZ 양쪽의 정세와 분쟁에 휘말려\n전쟁이 끊이지 않았지만…… ",
    3322: "적극적으로 세력을 넓힌 \x1bCB[bus]\x1bCZ 가문에 의해,\n마침내 \x1bCC호쿠리쿠\x1bCZ 지방은 통일을 맞았다.",
    3323: "전국에는 아직 전쟁의 불길이 남았지만,\n이 \x1bCC호쿠리쿠\x1bCZ는 \x1bCB[bus]\x1bCZ 가문의 지배 아래\n한동안 평화를 누렸다……",
    3326: "험준한 산들로 둘러싸인 \x1bCC고신\x1bCZ 지방은\n수많은 군웅이 패권을 다투며,\n전쟁이 끊이지 않는 땅이었지만…… ",
    3327: "적극적으로 세력을 넓힌 \x1bCB[bus]\x1bCZ 가문의 노력으로,\n마침내 \x1bCC고신\x1bCZ 지방은 통일을 맞았다.",
    3328: "전국에는 아직 전쟁의 불길이 남았지만,\n이 \x1bCC고신\x1bCZ은 \x1bCB[bus]\x1bCZ 가문의 지배 아래\n한동안 평화를 누렸다……",
    3331: "\x1bCC가미가타\x1bCZ와 \x1bCC간토\x1bCZ를 잇는 \x1bCC도카이도\x1bCZ 연안에는\n진취적인 다이묘가 여럿 등장해,\n세력 다툼 또한 치열했지만…… ",
    3332: "통일에 힘쓴 \x1bCB[bus]\x1bCZ 가문의 끊임없는 노력으로,\n마침내 \x1bCC도카이\x1bCZ 지방은 통일을 맞았다.",
    3333: "전국에는 아직 전쟁의 불길이 남았지만,\n\x1bCC도카이\x1bCZ 지방은 \x1bCB[bus]\x1bCZ 가문의 지배 아래\n한동안 평화를 누렸다……",
    3336: "오닌의 난으로 황폐해진 \x1bCC교토\x1bCZ를 포함한 \x1bCC긴키\x1bCZ 일대는\n여러 다이묘가 막부의 주도권을 놓고\n끊임없이 싸워 온 땅이었지만……",
    3337: "그러나 평온을 이루려는\n\x1bCB[bus]\x1bCZ 가문의 노력이 결실을 맺어,\n마침내 \x1bCC긴키\x1bCZ는 통일을 맞았다.",
    3338: "전국에는 아직 전쟁의 불길이 남았지만,\n이 \x1bCC긴키\x1bCZ는 \x1bCB[bus]\x1bCZ 가문의 지배 아래\n한동안 평화를 누렸다……",
    3341: "남북조의 다툼 이래 강력한 슈고 다이묘가\n쉴 새 없이 교체되며,\n수많은 전쟁이 벌어진 \x1bCC주고쿠\x1bCZ 지방…… ",
    3342: "그 세력 다툼에서 두각을 드러낸\n\x1bCB[bus]\x1bCZ 가문의 적극적인 공세로,\n마침내 \x1bCC주고쿠\x1bCZ 지방은 통일을 맞았다.",
    3343: "전국에는 아직 전쟁의 불길이 남았지만,\n이 \x1bCC주고쿠\x1bCZ 지방은 \x1bCB[bus]\x1bCZ 가문의 지배 아래\n한동안 평화를 누렸다……",
    3346: "전국시대 내내 중심이 될 강력한 다이묘가 없어,\n\x1bCC긴키\x1bCZ와 \x1bCC주고쿠\x1bCZ 다이묘들의 다툼에 휘말리고\n강대한 권력이 자라지 못한 \x1bCC시코쿠\x1bCZ 지방……",
    3347: "하지만 거침없이 공세를 펼친 \x1bCB[bus]\x1bCZ 가문에 의해,\n마침내 \x1bCC시코쿠\x1bCZ는 통일을 맞았다.",
    3348: "전국에는 아직 전쟁의 불길이 남았지만,\n이 \x1bCC시코쿠\x1bCZ는 \x1bCB[bus]\x1bCZ 가문의 지배 아래\n한동안 평화를 누렸다……",
    3351: "남북조의 다툼 이래 오랜 슈고 다이묘들이\n서로 반목하며 항쟁을 벌여,\n전쟁이 끊이지 않았던 \x1bCC규슈\x1bCZ 지방……",
    3352: "하지만 이를 기회로 본 \x1bCB[bus]\x1bCZ 가문이\n적극적인 공세로 세력을 넓혀,\n마침내 \x1bCC규슈\x1bCZ 전역을 통일했다.",
    3353: "전국에는 아직 전쟁의 불길이 남았지만,\n이 \x1bCC규슈\x1bCZ는 \x1bCB[bus]\x1bCZ 가문의 지배 아래\n한동안 평화를 누렸다……",
    3354: "주군, 조정에서 우리 가문으로\n칙사를 보냈다고 합니다!",
    3355: "뭐라, 칙사?\n대체 무슨 일이지?",
    3356: "\x1bCA[bus]\x1bCZ 공, 평안하십니까.\n폐하께서도 귀공의 통일 대업을 크게 기뻐하십니다.",
    3357: "황공한 말씀입니다.\n천하의 평안을 위한 저희의 노력이\n폐하의 귀에까지 닿았다니 몸 둘 바를 모르겠습니다……",
    3358: "폐하께서 특별히 명하셨습니다.\n관백·정이대장군·태정대신 중 하나를 내리신다는 분부입니다.",
    3359: "뭐라……!",
    3360: "모두 천하인에게 걸맞은 조정의 요직이니,\n마음 가는 대로 고르라는 분부입니다.\n자, 어느 자리로 정하시겠습니까……?",
    3361: "폐하의 뜻은 참으로 감사하오나,\n어느 자리든 모두 사양하겠습니다.",
    3362: "뭐라!?\n칙명을 사양하겠다고!\n대체 무슨 생각이오?",
    3363: "천하의 평정은 아직 갈 길이 멉니다.\n저는 아직 그런 요직을 받을 그릇이 못 됩니다.\n참으로 황공한 일이옵니다……",
    3364: "부족한 \x1bCA[bum]\x1bCZ, 천하를 진정 통일한 뒤에\n그때 다시 말씀해 주십시오.",
    3365: "그런가…… 이런.\n폐하께서도 크게 낙담하시겠군.\n알겠소. 귀공의 뜻은 그대로 아뢰겠소.",
    3366: "정이대장군이야말로 무가의 동량에게 어울리는 자리.\n허락된다면,\n장군직을 받들고 싶습니다.",
    3367: "알겠소. 폐하께 아뢰겠소.\n조만간 장군 선하의 칙사가\n다시 파견될 것이오……",
    3368: "정이대장군이야말로 무가의 동량에게 어울리는 자리.\n허락된다면,\n장군직을 받들고 싶습니다.",
    3369: "알겠소. 폐하께 아뢰겠소.\n조만간 장군 선하의 칙사가\n다시 파견될 것이오……",
    3370: "하지만 현직 쇼군이 계신데,\n제가 그분을 밀어내고 취임해도\n괜찮겠습니까?",
    3371: "염려 마시오. \x1bCA[bt]\x1bCZ 공에게 비밀리에\n장군직에서 물러나겠다는 승낙을 받았소.\n그러니 아무 걱정도 마시오.",
    3372: "그렇다면 신하 중 으뜸이며\n조정의 중추를 맡는 관백직을 받들고 싶습니다.",
    3373: "알겠소. 폐하께 아뢰겠소.\n조만간 관백 선하의 칙사가\n다시 파견될 것이오……",
    3374: "하지만 관백은 예부터 \x1bCB후지와라 북가\x1bCZ의\n직계인 \x1bCB섭관가\x1bCZ만 오를 수 있는 요직.\n제가 취임해도 괜찮겠습니까?",
    3375: "폐하께서는 귀공이 천하 평정을 위해 세운 공을\n기존 \x1bCB섭관가\x1bCZ보다도 높이 평가하십니다.",
    3376: "그래서 선례를 깨뜨려서라도\n귀공에게 관백직을 내리겠다고 하셨소.\n삼가 받으시오.",
    3377: "그렇다면 태정관의 최고위이자\n조정의 정점인 태정대신직을 원합니다.",
    3378: "알겠소. 폐하께 아뢰겠소.\n조만간 태정대신 선하의 칙사가\n다시 파견될 것이오……",
    3379: "설마 \x1bCA[bum]\x1bCZ, 이 몸이\n조정의 최고위직에 오를 날이 오다니……",
    3380: "그만큼 폐하께서 귀공의 천하 평정 공로를\n높이 평가하신다는 뜻이오. 감사히 받으시오.",
    3381: "그렇다면 신하 중 으뜸이며 조정의 중추를 맡는\n관백직을 받들고 싶습니다.",
    3382: "알겠소. 폐하께 아뢰겠소.\n조만간 관백 선하의 칙사가 다시 파견될 것이오……",
    3383: "하지만 이미 무가 출신 관백이 계신데,\n제가 그분을 밀어내고 취임해도\n괜찮겠습니까?",
    3384: "염려 마시오. \x1bCA[bk]\x1bCZ 공에게 비밀리에\n관백직에서 물러나겠다는 승낙을 받았소.\n그러니 아무 걱정도 마시오.",
    3385: "전국의 모든 다이묘가\n\x1bCB[bus]\x1bCZ 가문의 지배에 복종할 것을 맹세했다.",
    3386: "\x1bCA[bu]\x1bCZ 공은 천하의 평안을 드높이 외치고,\n전국에 소부지령을 선포했다. 이유를 불문하고,\n다이묘 사이의 사적인 영토 분쟁은 금지되었다.",
    3387: "백 년 동안 이 나라 곳곳에서 무사들이\n칼을 맞댄 격렬하고 헛된 싸움이 끝나,\n마침내 전국시대가 막을 내렸다.",
    3388: "긴 여정이었지만……\n마침내 전쟁 없는 세상을 맞았다.\n모두 다른 다이묘들이 힘을 보태 준 덕분이다.",
    3389: "이 태평성대를 하루라도 오래 지키려면,\n새 나라를 서둘러 세워야 한다……!",
    3390: "\x1bCB[bus]\x1bCZ 가문이 전국의 모든 성을 장악하고,\n맞설 수 있는 세력은 사라졌다.\n마침내 천하통일을 이뤘다.",
    3391: "\x1bCB[bu]\x1bCZ 공은 천하의 평안을 드높이 외치고,\n전국에 소부지령을 선포했다. 이제 누구든,\n사적인 영토 분쟁을 벌이는 일은 금지되었다.",
    3392: "백 년간 이어진 전국시대가 막을 내리고,\n‘\x1bCB[bus]\x1bCZ 가문의 평화’라 불릴 시대가 열렸다……",
    3393: "참으로 긴 여정이었지만……\n이렇게 전쟁 없는 세상을 맞았다.\n모두 가신들이 애쓴 덕분이다.",
    3394: "“창업은 쉬우나 수성은 어렵다”고 했다.\n하루빨리 \x1bCB[bus]\x1bCZ 가문의 지배를 굳혀,\n이 태평성대를 오래 지켜야 한다……!",
    3395: "\x1bCA[bu]\x1bCZ 공은 관백으로서 전국을 통일하고,\n무가 관백이 각국 다이묘를 다스리는 새 정권을 세웠다.",
    3396: "이렇게 \x1bCA[bu]\x1bCZ 공은 관백에 취임해,\n\x1bCC[cuh]\x1bCZ에 정무청을 두었다. 무가 출신 관백이\n각국 다이묘를 다스리는 새 정권을 세운 것이다.",
    3397: "\x1bCA[bu]\x1bCZ 공은 태정대신에 임명되어\n정무청을 두었다. 각국 다이묘를 다스리는 천하인,\n‘\x1bCC[cuh]\x1bCZ 공’이라 불렸다.",
    3398: "\x1bCA[bu]\x1bCZ의 천하통일로 조정은 그를\n\x1bCB아시카가 가문\x1bCZ을 대신할 무가의 동량으로 인정하고,\n정이대장군에 임명해 막부 개설을 허락했다.",
    3399: "\x1bCA[bu]\x1bCZ의 공적은 조정에서도 인정받아,\n정이대장군에 임명되었다.\n\x1bCA[bus]\x1bCZ 막부가 성립한 것이다.",
    3400: "\x1bCA[bu]\x1bCZ 공은 정이대장군이 되어,\n무가의 동량으로서\n새로운 막부를 열었다.",
    3401: "\x1bCA[bu]\x1bCZ 공은 정이대장군으로서\n전국 통일을 이뤘다. 진정한 무가의 동량이 되어,\n무로마치 막부의 재흥을 완수했다……",
    3402: "\x1bCA[bu]\x1bCZ의 위세는 \x1bCB아시카가 본가\x1bCZ를 뛰어넘어,\n진정한 무가의 동량으로 인정받았다. 정이대장군에\n임명되어 무로마치 막부의 재흥을 완수했다.",
    3403: "그리고 세월이 흘러……\n\x1bCA[bus]\x1bCZ 정권은 안정된 통치를 이어 가며,\n대다수 민심을 얻었다.",
    3404: "많은 이가 기다리던 전쟁 없는 시대가\n마침내 찾아왔으니 당연한 일이었다.\n전국시대는 끝을 고했다.",
    3405: "그 뒤에도 \x1bCA[bus]\x1bCZ 정권은 수많은 시련을\n이겨 냈다. 천재지변·정변·재정난……\n문제를 하나씩 착실히 해결해 나갔다.",
    3406: "그때마다 사회 제도를 개선하고,\n안정된 통치 아래 문화와 경제가 꽃피는\n황금시대를 일구었다.",
    3407: "그 300년의 역사는 일본사에 찬란히 빛나는\n\x1bCA[bus]\x1bCZ 시대라 불리며,\n사람들의 기억에 새겨졌다……",
    3408: "그리고 세월이 흘러……\n천하에 평화를 가져온 \x1bCA[bus]\x1bCZ 정권은\n국내 체제를 다지는 데 힘썼다.",
    3409: "\x1bCC[cuh]\x1bCZ를 국정의 중심지로 정비하고,\n새로운 제도의 틀을 세워,\n다시는 전란이 일어나지 않도록 경계를 강화했다.",
    3410: "하지만 그 경계는 때로 지나친 규제를 낳아,\n종교·경제·신분 등 모든 분야를\n경직시키기도 했다……",
    3411: "이질적인 존재를 용납하지 않는 강고한 봉건 통치는\n200년 동안 이어져,\n\x1bCA[bus]\x1bCZ 시대라 불리는 세상을 이루었다.",
    3412: "그리고 세월이 흘러……\n\x1bCB[bus]\x1bCZ 가문의 지배는 유력 다이묘들의 지지를 받아,\n안정기에 접어들었다.",
    3413: "전란에서 벗어난 사람들은 해방감에 힘입어,\n여러 나라와의 교역에 힘썼고,\n일본은 큰 경제 발전의 시대를 맞았다.",
    3414: "하지만 경제 발전의 혜택은\n\x1bCB[bus]\x1bCZ 가문뿐 아니라 백성과\n유력 다이묘들의 힘도 키웠다.",
    3415: "이윽고 \x1bCA[bis]\x1bCZ 가문을 비롯한 다이묘들은\n\x1bCB[bus]\x1bCZ 가문의 통치를 꺼리며,\n점차 독립하려는 움직임을 보였다.",
    3416: "그래도 \x1bCA[bum]\x1bCZ의 손으로 기틀을 세운\n\x1bCA[bus]\x1bCZ 정권은 약 150년 동안,\n그 명맥을 이어 갔다.",
    3417: "그리고 세월이 흘러……\n유력 다이묘들의 보좌에 힘입어,\n\x1bCB[bus]\x1bCZ 가문은 안정된 통치를 이뤘다.",
    3418: "사람들은 한동안 전쟁을 잊고 평화를 누렸지만,\n연이은 천재지변으로\n\x1bCA[bus]\x1bCZ 정권은 심각한 재정난에 빠졌다.",
    3419: "중앙의 통치가 흔들린 틈을 타,\n각지의 유력 다이묘들이 할거하면서,\n다시 분권 체제로 옮겨 갔다.",
    3420: "초대 \x1bCA[bum]\x1bCZ 때 \x1bCA[bis]\x1bCZ 등 세력을\n남겨 둔 일이 화근이었을지도 모른다.",
    3421: "다시 각지의 다이묘들이 다투는 시대가 왔지만,\n그전까지 100년간 일본의 평화를 지킨\n\x1bCA[bus]\x1bCZ 시대는 사람들의 기억에 오래 남았다.",
    3422: "그리고 세월이 흘러……\n새로 시작된 \x1bCB[bus]\x1bCZ 가문의 통치는\n전국시대의 싸움을 끝냈지만,",
    3423: "전쟁이 다시 일어나지 않게 하려던\n\x1bCB[bus]\x1bCZ 가문의 통치는 다소 강압적으로 변했고,\n다이묘와 백성의 불만이 쌓여 갔다.",
    3424: "한동안 겉으로 터져 나오지는 않았지만,\n정권이 대를 거듭할수록\n불온한 움직임은 빨라졌다……",
    3425: "마침내 80년 뒤 각지에서 반란이 잇따랐다.\n더는 힘으로 억누를 수 없게 되어,\n전란의 시대가 다시 찾아왔다.",
    3426: "\x1bCB[bus]\x1bCZ 가문은 과거 오닌의 난 이후\n\x1bCB아시카가 쇼군가\x1bCZ처럼 실권을 잃고,\n명목상의 동량으로만 존속했다……",
    3427: "그리고 세월이 흘러……\n\x1bCB[bus]\x1bCZ 가문의 천하통일은\n평화로운 시대가 오리라는 기대를 낳았다.",
    3428: "하지만 다소 강압적이었던 통일 사업에\n백성은 불만을 품었고, \x1bCA[bu]\x1bCZ의 죽음을\n계기로 그 분노가 폭발했다.",
    3429: "잇따르는 잇키를 맞아 \x1bCB[bis]\x1bCZ 가문 등\n유력 다이묘들은 \x1bCA[bus]\x1bCZ의 지배를 포기하고,\n동란을 이용해 오히려 세력 기반을 다졌다.",
    3430: "한 시대의 영걸 \x1bCA[bu]\x1bCZ 공이 세상을 떠난 뒤,\n불과 몇 년 만에 세상은\n다시 전국의 혼돈으로 돌아갔다……",
    3431: "그리고 세월이 흘러……\n일본은 \x1bCB[bus]\x1bCZ 가문의 천하통일로,\n잠시 평화로운 시대를 맞았다.",
    3432: "하지만 \x1bCA[bus]\x1bCZ 정권의 눈은 이제\n일본 국내에만 머물지 않고,\n해외로 향했다.",
    3433: "안정된 국내에서는 특산품 생산을 장려하고,\n전매로 얻은 막대한 이익을\n수출품 가공에 돌렸다.",
    3434: "군사력과 경제력을 바탕으로, 해적과\n유럽 상인이 활개 치는 동아시아 해역의\n교역권에 국가로서 뛰어들었다.",
    3435: "이렇게 \x1bCA[bus]\x1bCZ의 일본은 근대 유럽보다 먼저,\n중상주의적 무역 국가로서\n세계 시장을 주도하게 되었다……",
    3436: "그리고 세월이 흘러……\n\x1bCA[bu]\x1bCZ 공은 천하통일 몇 년 뒤\n조정에 자신과 가신들의 모든 관직을 반납했다.",
    3437: "이로써 일본 역사상 처음으로,\n조정이 내리는 관위를 기반으로 삼지 않는\n독자적인 무가 권력이 탄생했다.",
    3438: "이 움직임에 조정은 당황했지만, \x1bCA[bus]\x1bCZ 정권은\n섭관과 대신 중심의 공가 사회와 거리를 두면서도,\n조정 자체는 그대로 보존했다.",
    3439: "이윽고 정치 권력은 \x1bCB[bus]\x1bCZ 가문이 맡고,\n의례적 권위는 조정이 맡는 특수한 이중국가로\n안정되어 국가의 상시 체제가 되었다.",
    3440: "무가와 공가는 서로 부족한 부분을 보완하며,\n오랫동안 태평성대를 지켜 나갔다.",
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    3311: ["regional_name_ou_requires_glossary_review"],
    3326: ["regional_name_koshin_requires_glossary_review"],
    3358: ["court_office_titles_require_glossary_review"],
    3367: ["court_proclamation_term_requires_glossary_review"],
    3374: ["fujiwara_hokke_and_sekkan_house_terms_require_review"],
    3386: ["sobuji_edict_term_requires_glossary_review"],
    3396: ["government_office_term_rendered_generically"],
    3411: ["authoritarian_ending_tone_requires_style_review"],
    3429: ["ikki_term_requires_glossary_review"],
    3438: ["court_society_terms_require_glossary_review"],
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
    excluded = set(EXCLUDED_INTERNAL_IDS)
    ids = [entry_id for entry_id in range(SCOPE_START, SCOPE_END + 1) if entry_id not in excluded]
    if len(ids) != 114 or set(ids) != set(TRANSLATIONS):
        raise ValueError("batch3 ids are not the exact 114 meaningful entries")
    return ids


def event_for(entry_id: int) -> str:
    matches = [
        event["event_id"]
        for event in EVENTS
        if event["start_id"] <= entry_id <= event["end_id"]
    ]
    if len(matches) != 1:
        raise ValueError(f"id {entry_id} does not map to one batch3 event group")
    return str(matches[0])


def load_source(path: Path, language: str) -> tuple[bytes, bytes, Any]:
    return shared.load_source(path, language)


def source_structure(text: str) -> dict[str, Any]:
    value = shared.source_structure(text)
    value["bracket_tokens"] = BRACKET_TOKEN_RE.findall(text)
    return value


def public_script_counts(text: str) -> dict[str, int]:
    return {
        "cjk_unified_count": shared.cjk_unified_count(text),
        "kana_count": shared.kana_count(text),
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    ids = selected_ids()
    loaded = {
        language: load_source(path, language)
        for language, path in {
            "SC": args.stock_sc,
            "JP": args.stock_jp,
            "EN": args.stock_en,
        }.items()
    }
    tables = {language: value[2] for language, value in loaded.items()}

    excluded_evidence: list[dict[str, Any]] = []
    for entry_id in EXCLUDED_INTERNAL_IDS:
        texts = [tables[language].texts[entry_id] for language in ("SC", "JP", "EN")]
        if len(set(texts)) != 1 or INTERNAL_KEY_RE.fullmatch(texts[0]) is None:
            raise ValueError(f"id {entry_id} is not a shared internal region key")
        excluded_evidence.append(
            {
                "id": entry_id,
                "reason": "nonlocalized_internal_region_key",
                "reference_hashes": {
                    language: common.text_hash(tables[language].texts[entry_id])
                    for language in ("SC", "JP", "EN")
                },
            }
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

    boundary_ids = (3308, 3309, 3310, 3311, 3353, 3354, 3384, 3385, 3440, 3441)
    evidence = {
        "schema": "nobu16.kr.event-dialogue-alignment-evidence.v3",
        "batch_id": BATCH_ID,
        "resource": "msgev",
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "selected_entry_count": len(ids),
            "excluded_internal_entry_count": len(EXCLUDED_INTERNAL_IDS),
        },
        "alignment_basis": [
            "same_resource_role",
            "same_17910_entry_count",
            "same_numeric_string_ids",
            "manual_semantic_crosscheck_of_selected_entries",
            "internal_region_keys_identical_in_sc_jp_en_and_left_unchanged",
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
        "excluded_internal_entries": excluded_evidence,
        "entry_count": len(ids),
        "entries": evidence_entries,
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.event-dialogue-review-index.v3",
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
    if any(value != {"cjk_unified_count": 0, "kana_count": 0} for value in source_free_scan.values()):
        raise ValueError("batch3 public artifact contains source-script text")

    visible_lengths = {
        entry_id: [
            len(common.ESC_RE.sub("", line))
            for line in TRANSLATIONS[entry_id].splitlines()
        ]
        for entry_id in ids
    }
    validation = {
        "schema": "nobu16.kr.event-dialogue-generation-validation.v3",
        "batch_id": BATCH_ID,
        "passed": True,
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "selected_entry_count": len(ids),
            "selected_ids_sha256": sha256(
                json.dumps(ids, separators=(",", ":")).encode("utf-8")
            ),
            "excluded_internal_entry_count": len(EXCLUDED_INTERNAL_IDS),
            "excluded_internal_ids_sha256": sha256(
                json.dumps(EXCLUDED_INTERNAL_IDS, separators=(",", ":")).encode(
                    "utf-8"
                )
            ),
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
            "entries_over_30": [
                entry_id
                for entry_id, lengths in visible_lengths.items()
                if max(lengths) > 30
            ],
            "runtime_layout_review_required": True,
        },
        "font_integration": {
            "state": "deferred_not_computed",
            "current_font_v6_or_installer_must_not_include_batch3": True,
        },
        "source_free_scan": source_free_scan,
        "artifacts": artifacts,
        "generator": {
            "path": SCRIPT_PATH.name,
            "sha256": sha256(SCRIPT_PATH.read_bytes()),
        },
        "safety": {
            "installed_game_files_modified": False,
            "font_files_modified": False,
            "installer_modified": False,
            "existing_v01_or_v02_artifacts_modified": False,
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
