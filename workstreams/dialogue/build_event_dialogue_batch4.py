#!/usr/bin/env python3
"""Build source-free Korean historical event dialogue batch4 (3441-3564)."""

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
import build_event_dialogue_batch3 as shared  # noqa: E402


BATCH_ID = "msgev_historical_events_3441_3564.v0.4"
OVERLAY_NAME = "msgev_ko_historical_events_3441_3564.v0.4.json"
EVIDENCE_NAME = "alignment_evidence.v0.4.json"
REVIEW_NAME = "review_index.v0.4.json"
VALIDATION_NAME = "validation.v0.4.json"
STRING_COUNT = shared.STRING_COUNT
SOURCE_PINS = shared.SOURCE_PINS
SCOPE_START = 3441
SCOPE_END = 3564
EXCLUDED_INTERNAL_IDS: tuple[int, ...] = ()
BRACKET_TOKEN_RE = re.compile(r"\[[a-z0-9_]+\]")

EVENTS = (
    {
        "event_id": "ashikaga_miyoshi_reconciliation",
        "title_ko": "아시카가·미요시 화의와 결렬",
        "start_id": 3441,
        "end_id": 3460,
        "selected_count": 20,
    },
    {
        "event_id": "oda_nobukatsu_second_rebellion",
        "title_ko": "오다 노부카쓰의 두 번째 모반",
        "start_id": 3461,
        "end_id": 3484,
        "selected_count": 24,
    },
    {
        "event_id": "kato_kawagoe_crisis",
        "title_ko": "가토의 난과 가와고에 위기",
        "start_id": 3485,
        "end_id": 3524,
        "selected_count": 40,
    },
    {
        "event_id": "takeda_nobushige_house_code",
        "title_ko": "다케다 노부시게의 가훈",
        "start_id": 3525,
        "end_id": 3549,
        "selected_count": 25,
    },
    {
        "event_id": "nabeshima_hikotsuru_marriage",
        "title_ko": "나베시마 나오시게와 히코쓰루",
        "start_id": 3550,
        "end_id": 3564,
        "selected_count": 15,
    },
)

TRANSLATIONS: dict[int, str] = {
    3441: (
        "전국시대,\n"
        "\x1bCB쇼군 아시카가 가문\x1bCZ과 \x1bCB간레이 호소카와 가문\x1bCZ도 각각 분열해,\n"
        "오랫동안 서로 싸우고 있었다."
    ),
    3442: (
        "정쟁 때마다 \x1bCB아시카가 가문\x1bCZ의 당주는 \x1bCC교토\x1bCZ를 떠났고,\n"
        "현 쇼군 \x1bCA아시카가 [bm75]\x1bCZ 또한 \x1bCC교토\x1bCZ가 아닌\n"
        "\x1bCC오미\x1bCZ에서 원복을 치르고 쇼군직에 올랐다."
    ),
    3443: (
        "하지만 무로마치 막부의 본거지는 역시 \x1bCC교토\x1bCZ였다.\n"
        "쇼군 \x1bCA[bm75]\x1bCZ 또한 몇 번이나 \x1bCC교토\x1bCZ로 돌아가려 꾀하며,\n"
        "\x1bCC교토\x1bCZ를 지배하는 \x1bCB미요시 가문\x1bCZ과 교섭했지만……"
    ),
    3444: (
        "\x1bCB미요시 가문\x1bCZ은 본래 \x1bCB호소카와 가문\x1bCZ의 가신이었다.\n"
        "곧 쇼군 \x1bCA[bm75]\x1bCZ의 눈에는 가신의 가신에 불과했다.\n"
        "자존심이 방해했는지 교섭은 진척되지 않았다."
    ),
    3445: (
        "게다가 \x1bCB아시카가 가문\x1bCZ 내부에서도 \x1bCB미요시 세력\x1bCZ을 원망한\n"
        "\x1bCA호소카와 하루모토\x1bCZ 등이 계속 화친에 반대해,\n"
        "\x1bCC교토\x1bCZ 귀환은 좀처럼 이루어지지 않았다."
    ),
    3446: (
        "이대로는 끝이 없겠군.\n"
        "\x1bCC교토\x1bCZ로 돌아가기 위해…… 여기서 \x1bCA하루모토\x1bCZ를 끊는다.\n"
        "\x1bCA나가요시\x1bCZ와 교섭을 진행하라!"
    ),
    3447: (
        "\x1bCA쇼군\x1bCZ께서 저희의 존재를 인정해 주신다면,\n"
        "저희도 귀환을 막을 이유가 없습니다.\n"
        "삼가 맞이하겠습니다."
    ),
    3448: (
        "\x1bCA미요시 나가요시\x1bCZ를 오토모슈, 즉 \x1bCB쇼군가\x1bCZ 직신으로\n"
        "인정하면서 양측의 화의가 성립했다.\n"
        "마침내 \x1bCA[bm75]\x1bCZ의 \x1bCC교토\x1bCZ 귀환이 눈앞에 들어왔다."
    ),
    3449: (
        "한편 끝까지 화의에 반대한\n"
        "\x1bCA호소카와 하루모토\x1bCZ 일파는 \x1bCC교토\x1bCZ를 떠나 자취를 감췄다……"
    ),
    3450: (
        "이제 와 가신 집안인 \x1bCB미요시\x1bCZ와 손을 잡을 수 있겠느냐!\n"
        "나는 화의에 반대한다!\n"
        "끝까지 맞서겠다!"
    ),
    3451: (
        "쇼군의 \x1bCC교토\x1bCZ 귀환이 정해져, 오랜만에 무로마치 막부의\n"
        "질서가 회복될 듯했지만,\n"
        "그것도 오래가지는 못했다."
    ),
    3452: (
        "이제 반\x1bCB미요시\x1bCZ의 선봉이 된 \x1bCA호소카와 하루모토\x1bCZ 일파가\n"
        "각지의 \x1bCB미요시 가문\x1bCZ 거점을 집요하게 공격해,\n"
        "새로운 \x1bCB아시카가\x1bCZ·\x1bCB미요시\x1bCZ 협력 체제를 뒤흔들었다."
    ),
    3453: (
        "이놈 \x1bCA하루모토\x1bCZ……!\n"
        "끝까지 우리에게 맞서겠다는 것이냐.\n"
        "\x1bCA쇼군\x1bCZ께서는 어째서 보고만 계시는가!"
    ),
    3454: "…………",
    3455: (
        "이윽고 본래 \x1bCB미요시 가문\x1bCZ과의 화친에 소극적이던\n"
        "\x1bCA[bm75]\x1bCZ의 측근 중에도 \x1bCA하루모토\x1bCZ에 동조하는 자가 생겨,\n"
        "\x1bCA[bm75]\x1bCZ 본인도 더는 발뺌할 수 없는 처지에 몰렸다."
    ),
    3456: (
        "그래도 \x1bCA[bm75]\x1bCZ 본인은 교토 입성을 꾀했으나, 경계하던\n"
        "\x1bCB미요시 세력\x1bCZ에 막혀 \x1bCC히가시야마\x1bCZ의 \x1bCC료젠성\x1bCZ에 농성했다.\n"
        "이로써 화의는 완전히 무너졌다."
    ),
    3457: (
        "떠돌이 쇼군…… 역시 믿을 수 없군.\n"
        "\x1bCA하루모토\x1bCZ를 앞세워 우리를 속이다니!"
    ),
    3458: (
        "이럴 수가, \x1bCC교토\x1bCZ를 눈앞에 두고 또 들어가지 못하다니!\n"
        "\x1bCB미요시\x1bCZ 놈들……\n"
        "정이대장군을 무엇으로 아는 것이냐!"
    ),
    3459: (
        "\x1bCC료젠성\x1bCZ은 \x1bCB미요시군\x1bCZ의 공격으로 함락되었다.\n"
        "쇼군 \x1bCA[bm75]\x1bCZ 일행은 다시 \x1bCC오미\x1bCZ로 달아났고,\n"
        "\x1bCA하루모토\x1bCZ 일파도 그 뒤를 따랐다."
    ),
    3460: (
        "결국 아무 소용도 없었다.\n"
        "\x1bCB아시카가\x1bCZ와 \x1bCB미요시\x1bCZ 양측의 불신만 커졌을 뿐,\n"
        "상황은 화의 전으로 완전히 돌아갔다."
    ),
    3461: (
        "과거 형 \x1bCA노부나가\x1bCZ를 배신하고,\n"
        "이노 전투에서 패했으나,\n"
        "어머니의 중재로 목숨을 건진 \x1bCA오다 노부카쓰\x1bCZ―"
    ),
    3462: (
        "하지만 그 치욕은\n"
        "그가 참고 넘길 수 있는 것이 아니었다.\n"
        "재기를 노리며 남몰래 계책을 짜고 있었다."
    ),
    3463: (
        "\x1bCA가쓰이에\x1bCZ, 이번에는 승산이 있다.\n"
        "형과 대립하는 세력이 이 \x1bCC오와리\x1bCZ에도 많다.\n"
        "그들과 손잡을 방도가 생겼다!"
    ),
    3464: "\x1bCA노부카쓰\x1bCZ 님……",
    3465: (
        "이번에야말로 내가 \x1bCB오다\x1bCZ의 당주다!\n"
        "멍청한 형으로는 이룰 수 없는,\n"
        "평온한 \x1bCC오와리\x1bCZ를 세워 보이겠다!"
    ),
    3466: (
        "\x1bCA노부카쓰\x1bCZ가 재기 계획을 \x1bCA가쓰이에\x1bCZ에게 밝힌 뒤\n"
        "며칠 후, 사태는 뜻밖의 방향으로 흘렀다."
    ),
    3467: "뭐라고!\n형님이 위독하시다고?",
    3468: (
        "예…… 갑작스러운 병으로 숨도 가쁘신 상태입니다.\n"
        "내일을 기약하기 어렵다 하시며,\n"
        "마지막으로 \x1bCA노부카쓰\x1bCZ 님을 뵙고 싶다고……"
    ),
    3469: (
        "그 형이 그토록 앓다니, 사람 일은 모르는 법이군……\n"
        "하지만 마지막에 그토록 미워하던 나를\n"
        "보고 싶다니, 인간적인 정은 남아 있었나 보군."
    ),
    3470: (
        "아마 주군께서는 임종을 앞두고,\n"
        "\x1bCB오다\x1bCZ의 가독을 \x1bCA노부카쓰\x1bCZ 님께\n"
        "잇게 하겠다는 유언을 남기시려는 듯합니다……"
    ),
    3471: (
        "오, 과연 그렇겠군.\n"
        "형님에게는 아직 자식이 없으니.\n"
        "나 말고는 후계자가 없지."
    ),
    3472: (
        "군사를 일으킬 필요도 없이,\n"
        "\x1bCB오다\x1bCZ의 가독이 굴러들어 오다니……\n"
        "좋아, 어서 \x1bCC기요스성\x1bCZ으로 가자!"
    ),
    3473: (
        "\x1bCA노부카쓰\x1bCZ는 가독을 잇게 한다는 유언을 기대하며,\n"
        "병상에 누운 \x1bCA노부나가\x1bCZ를 문병하고자\n"
        "\x1bCC기요스성\x1bCZ으로 들어갔고……"
    ),
    3474: "그 뒤,\n다시는 돌아오지 못했다.",
    3475: (
        "뻔히 보이는 꾀병에 걸려들다니.\n"
        "순진하다고도 할 수 있겠지만, 전국시대에는\n"
        "말 그대로 목숨을 잃을 허점이지……"
    ),
    3476: "피를 나눈 아우를 손수 베고도,\n후회가 없으십니까?",
    3477: (
        "없다.\n"
        "전에도 말했을 텐데.\n"
        "내가 보는 것은 \x1bCB오다 가문\x1bCZ이 아니다. 천하다!"
    ),
    3478: (
        "\x1bCA가쓰이에\x1bCZ.\n"
        "너도 그 뜻을 믿었기에,\n"
        "\x1bCA간주로\x1bCZ의 계책을 내게 밀고한 것이겠지?"
    ),
    3479: (
        "(\x1bCA노부카쓰\x1bCZ 님을 죽음으로 몰아넣은 것은\n"
        " 다른 누구도 아닌 이 \x1bCA가쓰이에\x1bCZ다……\n"
        " 언젠가 반드시 그 대가를 치러야겠지.)"
    ),
    3480: (
        "(하지만 이 결단이 잘못되지 않았음을\n"
        " 보여 주기 위해서라도, 앞으로 온 힘을 다해\n"
        " 주군의 천하 쟁취를 돕겠다!)"
    ),
    3481: (
        "예……!\n"
        "지금부터 이 \x1bCA시바타 가쓰이에\x1bCZ,\n"
        "주군의 천하 쟁취를 위해 선봉에 서겠습니다!"
    ),
    3482: (
        "친어머니 \x1bCA도타고젠\x1bCZ이 비탄에 잠긴 것은\n"
        "말할 필요도 없다. 그러나 \x1bCA노부카쓰\x1bCZ의 죽음은 뜻밖에도\n"
        "가문에 거의 동요를 일으키지 않았다."
    ),
    3483: (
        "\x1bCA노부카쓰\x1bCZ의 모반이 두 번째였던 데다,\n"
        "예전보다 \x1bCA노부나가\x1bCZ의 지배가 깊이 뿌리내린 것이\n"
        "그 배경이었을지도 모른다."
    ),
    3484: (
        "어쨌든 \x1bCA노부카쓰\x1bCZ의 죽음은 \x1bCB오다\x1bCZ 가문을 결속시켰고,\n"
        "\x1bCA노부나가\x1bCZ를 중심으로 \x1bCC오와리\x1bCZ를 통일할 체제를\n"
        "더욱 굳건하게 만들었다."
    ),
    3485: (
        "\x1bCB이마가와 가문\x1bCZ의 군사였던 \x1bCA호조 소운\x1bCZ(\x1bCA이세 소즈이\x1bCZ)은\n"
        "\x1bCC이즈·사가미\x1bCZ를 차지하고 독립했으며,\n"
        "적자 \x1bCA우지쓰나\x1bCZ는 \x1bCC무사시\x1bCZ·\x1bCC시모사\x1bCZ·\x1bCC스루가\x1bCZ로 진출했다."
    ),
    3486: (
        "그 \x1bCC스루가\x1bCZ에서 \x1bCA우지쓰나\x1bCZ에게 농락당한 이는,\n"
        "훗날 ‘가이도 제일의 무사’라 불리는\n"
        "\x1bCB이마가와 가문\x1bCZ 당주 \x1bCA이마가와 고로 요시모토\x1bCZ였다."
    ),
    3487: "\x1bCA우지쓰나\x1bCZ가 죽었나.\n그런가, 그 사내가……",
    3488: "그렇습니다.\n이미 눈치채셨겠지만,\n이것은 절호의 기회입니다.",
    3489: (
        "허허, 승려답지 않게 섬뜩한 말을 하는군……\n"
        "하지만 스승이여, 마음 한구석으로는\n"
        "\x1bCA우지쓰나\x1bCZ와 다시 한번 싸우고 싶었소."
    ),
    3490: "5년 전의 나는 아직 젊어,\n\x1bCA우지쓰나\x1bCZ 앞에서 아무것도 하지 못했지……",
    3491: (
        "형을 물리치고 가독을 이어 우쭐해진 나를\n"
        "정신 차리게 한 사람이 바로 우지쓰나였소……"
    ),
    3492: (
        "내 아버지의 사촌이라지만,\n"
        "참으로 무서운 사내였소.\n"
        "그래서 다시 한번 맞서고 싶었는데……"
    ),
    3493: (
        "흠, 그렇다면 \x1bCA우지쓰나\x1bCZ는 요시모토 님께\n"
        "또 한 명의 스승인 셈이군요."
    ),
    3494: "하하!\n그럴지도 모르겠군.\n말하자면 또 한 명의 스승이지.",
    3495: (
        "그렇다면 이제 \x1bCA요시모토\x1bCZ 님이 스승이 되십시오.\n"
        "\x1bCA우지쓰나\x1bCZ의 아들 \x1bCA우지야스\x1bCZ에게 난세의 법도를\n"
        "가르쳐 주시는 건 어떻겠습니까?"
    ),
    3496: (
        "죽은 자가 남기고, 산 자가 이어받습니다……\n"
        "그가 죽을 때면 다시 이어받을 자가 나타나지요.\n"
        "그렇게 인간은 만들어지는 것입니다."
    ),
    3497: (
        "이런, 자기에게 유리할 때만\n"
        "설교를 참 잘하는군.\n"
        "어디, 전쟁이 무엇인지 가르쳐 줘 볼까……"
    ),
    3498: (
        "\x1bCA이마가와 요시모토\x1bCZ는 \x1bCA우지쓰나\x1bCZ의 죽음을 틈타 \x1bCC스루가\x1bCZ에\n"
        "군사를 보내 \x1bCC간바라성\x1bCZ 등 \x1bCC스루가 동부\x1bCZ를 점령했다.\n"
        "이른바 ‘가토의 난’이다……"
    ),
    3499: (
        "\x1bCA요시모토\x1bCZ는 \x1bCA[b1251]\x1bCZ에게도 공동 작전을 제안했고,\n"
        "\x1bCA[bm1251]\x1bCZ 측도 흔쾌히 받아들여 공격에 가담했다.\n"
        "이 움직임은 곧 \x1bCA우지야스\x1bCZ에게 전해졌다."
    ),
    3500: (
        "즉시 \x1bCC스루가\x1bCZ로 간다!\n"
        "그곳은 \x1bCB이마가와\x1bCZ와 \x1bCB다케다\x1bCZ의 움직임을 막을 요충지다.\n"
        "절대 잃을 수 없다!"
    ),
    3501: "보, 보고드립니다!",
    3502: (
        "간토 간레이 \x1bCA노리마사\x1bCZ와 \x1bCC오기야쓰\x1bCZ의 \x1bCA도모사다\x1bCZ……\n"
        "거기에 고가쿠보 \x1bCA아시카가 하루우지\x1bCZ 님까지 가세해,\n"
        "\x1bCC가와고에성\x1bCZ을 공격하고자 진군 중입니다!"
    ),
    3503: (
        "\x1bCA하루우지\x1bCZ라고? 내 매제잖아!\n"
        "그 자식…… 무슨 생각이지!\n"
        "분명 \x1bCA노리마사\x1bCZ 놈에게 부추김을 받았군!"
    ),
    3504: (
        "그뿐만이 아닌 듯하구나, \x1bCA마고쿠로\x1bCZ.\n"
        "그 \x1bCA노리마사\x1bCZ의 등을 떠민 자가 있다……\n"
        "동서에서 우리를 협공하려고 말이지."
    ),
    3505: (
        "그럼 설마…… \x1bCA이마가와 요시모토\x1bCZ가!?\n"
        "\x1bCB다케다 가문\x1bCZ뿐 아니라 \x1bCB양 우에스기 가문\x1bCZ과 \x1bCB고가쿠보\x1bCZ까지\n"
        "모두 조종한다는 건가!"
    ),
    3506: "그래, 틀림없다.\n그럼 \x1bCC가와고에\x1bCZ에 모인 적병은 얼마나 되지?",
    3507: (
        "그, 그것이…… 병력이 너무 많아\n"
        "척후도 다 세지 못할 정도라……\n"
        "대략 8만이라고 합니다……"
    ),
    3508: (
        "8만…… 쉽게 모을 수 있는 수가 아니군.\n"
        "하지만 \x1bCB양 우에스기 가문\x1bCZ과 \x1bCB고가쿠보\x1bCZ가 힘을 합쳤다면,\n"
        "수만을 넘는 것도 가능하겠지……"
    ),
    3509: (
        "형님, 이건 위험해……\n"
        "\x1bCC가와고에\x1bCZ를 잃으면 \x1bCB호조\x1bCZ의 \x1bCC간토\x1bCZ 지배는\n"
        "모두 물거품이 된다고!"
    ),
    3510: (
        "……\x1bCA마고쿠로\x1bCZ, \x1bCC가와고에성\x1bCZ을 맡아 주겠느냐?\n"
        "이기라는 말은 하지 않겠다.\n"
        "지지 않고 버텨 주기만 하면 된다."
    ),
    3511: "죽으러 가라는 겁니까, 형님?",
    3512: "……",
    3513: (
        "그런 표정 짓지 마!\n"
        "하치만의 화신이라 불린 나다.\n"
        "죽으라 해도 쉽게 죽을 것 같으냐!"
    ),
    3514: (
        "미안하다, \x1bCA마고쿠로\x1bCZ. 아니, \x1bCA[bm790]\x1bCZ!\n"
        "내가 저지른 실수를\n"
        "네게 수습하게 하다니……"
    ),
    3515: (
        "아버지가 돌아가신 뒤,\n"
        "곧바로 \x1bCB이마가와\x1bCZ와 화친했어야 했다.\n"
        "그랬다면 이런 사태까지는……"
    ),
    3516: (
        "형님, 지금은 그런 약한 소리 듣고 싶지 않아!\n"
        "내가 살아 돌아오면,\n"
        "그때 내 원망이나 실컷 들어 달라고!"
    ),
    3517: (
        "그래, 알았다! \x1bCC가와고에\x1bCZ는 맡기마!\n"
        "남은 곳은 가토다. 이제 와 \x1bCA요시모토\x1bCZ가 물러나지는 않겠지.\n"
        "그렇다고 쉽게 이길 상대도 아니고……"
    ),
    3518: "그러면……\n이제 방법이 없는 건가?",
    3519: (
        "아니, 이번 \x1bCA요시모토\x1bCZ의 우리를 향한 포위망……\n"
        "틈이 있다면 서쪽이다.\n"
        "\x1bCA요시모토\x1bCZ의 진영에 가담한…… \x1bCA[b1251]\x1bCZ."
    ),
    3520: (
        "\x1bCA[bm1251]\x1bCZ 공은 속내를 알 수 없는 자다. 겉으로는\n"
        "\x1bCA요시모토\x1bCZ를 돕는 척하며 남몰래 어부지리를 노리고 있지.\n"
        "그 생각을 거꾸로 우리가 이용한다……!"
    ),
    3521: "그렇다면 서쪽은 걱정 없겠군.\n나는 동쪽, \x1bCC가와고에\x1bCZ로 간다!",
    3522: (
        "부탁한다, \x1bCA[bm790]\x1bCZ.\n"
        "서쪽을 정리하면 곧바로 구원하러 가겠다.\n"
        "그때까지 절대 죽어서는 안 된다!"
    ),
    3523: "무리한 말을 하는군, 정말……\n그럼 형님, 다녀오지!",
    3524: (
        "이리하여 \x1bCA요시모토\x1bCZ가 펼친 포위망을 막고자,\n"
        "\x1bCA[b790]\x1bCZ 일행은 \x1bCC가와고에성\x1bCZ으로 향했다.\n"
        "그리고 \x1bCA우지야스\x1bCZ는 \x1bCC가토\x1bCZ로 출진했다……"
    ),
    3525: "\x1bCA[b1251]\x1bCZ의 아우 \x1bCA다케다 노부시게\x1bCZ―",
    3526: (
        "어려서부터 그 재능을 아버지 \x1bCA노부토라\x1bCZ에게 인정받아,\n"
        "\x1bCA[bm1251]\x1bCZ 공을 싫어한 \x1bCA노부토라\x1bCZ가 \x1bCB다케다 가문\x1bCZ 당주로\n"
        "세우려 했던 것으로 알려져 있다."
    ),
    3527: "\x1bCB다케다 가문\x1bCZ·\x1bCC쓰쓰지가사키관\x1bCZ―",
    3528: "\x1bCA노부시게\x1bCZ, 무엇을 하고 있느냐?",
    3529: "주군.\n태어날 아이를 위해,\n가훈을 만들고 있었습니다.",
    3530: (
        "……주군은 그만두거라. 우리는 형제가 아니냐.\n"
        "그래, 어떤 가훈을 만들고 있느냐?\n"
        "내게도 보여 주겠느냐?"
    ),
    3531: "……형님의 부탁이라면.\n여기 있습니다.\n보십시오!",
    3532: "음……\n“제1조　영원히\n주군을 배반해서는 안 된다”",
    3533: "“제2조　주군에게 받은 녹봉에\n 절대로 불만을 품어서는 안 된다”",
    3534: "……이런 조항을 몇 개나 쓴 것이냐?",
    3535: "99개 조항입니다.",
    3536: "그, 그러냐…… 조금만 더,\n\x1bCB다케다 가문\x1bCZ 밖에서도 쓸 만한 내용으로 만들 수 없겠느냐?",
    3537: "불가능합니다.\n제가 \x1bCB다케다 가문\x1bCZ 밖에서 산다는 것은\n있을 수 없으니까요……",
    3538: "너도 변함이 없구나……\n어째서 그토록 나에게 충성을 다하느냐?",
    3539: (
        "생각해 보면 아버지는 네게 \x1bCB다케다 가문\x1bCZ 당주 자리를\n"
        "물려주려 했다. 그래서 남몰래\n"
        "가보를 네게 주셨던 게 아니냐?"
    ),
    3540: "예, 하지만 모두 형님께 바쳤습니다.",
    3541: "(아버지도 보람이 없으시겠군……)",
    3542: (
        "형님께는 \x1bCB다케다 가문\x1bCZ을 천하로 이끌 힘이 있습니다.\n"
        "작은 재주밖에 없는 저는 그저 형님을 믿고,\n"
        "형님을 따를 뿐입니다."
    ),
    3543: "저는 형님께 은혜를 입었습니다.\n형님께 변고가 생긴다면,\n가장 먼저 달려가 싸우다 죽겠습니다.",
    3544: (
        "이제 됐다, 알겠다.\n"
        "그런 것을 물은 내가 어리석었구나.\n"
        "……죽지는 말거라. 죽어서는 안 된다!"
    ),
    3545: "예, 앞으로도 변함없이\n형님께 충성을 다하겠습니다.",
    3546: "(\x1bCA덴큐 노부시게\x1bCZ, 가신으로서는\n 이보다 나은 장수가 없겠지……)",
    3547: (
        "(하지만 우리는 피를 나눈 형제다.\n"
        " 육친의 정 같은 것이 있어도 좋을 텐데.\n"
        " 그렇게 생각하는 건 내 어리광일까……)"
    ),
    3548: (
        "99개 조항에 이르는 다케다 노부시게의 가훈에는,\n"
        "\x1bCA[bm1251]\x1bCZ 공을 향한 충성을 맹세하는 항목뿐 아니라\n"
        "무사의 생활 규범을 적은 항목도 많았고……"
    ),
    3549: "훗날 유명해진 고슈 법도지차제의\n원형이 되었다고 전해진다.",
    3550: (
        "\x1bCA나베시마 나오시게\x1bCZ는 \x1bCB류조지 가문\x1bCZ의 전략을 맡은 참모였다.\n"
        "그 바쁜 나날을 내조로 뒷받침한 이가\n"
        "사랑하는 아내 \x1bCA히코쓰루히메\x1bCZ였다."
    ),
    3551: (
        "두 사람의 첫 만남에는 전설이 깃들어 있다.\n"
        "어느 날 전투에서 승리하고 귀환하던 길에,\n"
        "\x1bCA나오시게\x1bCZ는 \x1bCC이이모리성\x1bCZ에서 \x1bCA히코쓰루\x1bCZ에게 반했다고 한다……"
    ),
    3552: "이봐, 점심은 아직인가!\n이럴 줄 알았으면 여기 들르지 말고,\n곧장 거성으로 돌아갈 걸 그랬군.",
    3553: "주군께서 갑자기 들르셔서, 점심 준비로\n주방도 혼란스러운 모양입니다.\n……제가 살펴보고 오겠습니다.",
    3554: "예상치 못한 많은 장병이 찾아오자,\n점심을 준비하느라 바빠진 시녀들은\n큰 혼란에 빠졌다.",
    3555: "여러분, 조금 진정하세요!\n손님 수만큼 정어리를 준비해 두었습니다.\n일을 나눠 차례대로 구우면 됩니다!",
    3556: "(음, 저 여인은……?)",
    3557: "아, 정어리 굽는 솜씨가\n그다지 좋지 않군요. 이리 주세요!\n제가 대신 구워 드릴게요!",
    3558: "전혀 당황할 필요 없어요.\n순서에 맞춰 나르면 괜찮습니다.\n차분하게 준비해요!",
    3559: "(훌륭한 지시로 시녀들을 이끌며\n 수많은 정어리를 굽고 있다……\n 저토록 현명한 여인이 있다니.)",
    3560: "이보게…… 정어리를 구우면서\n시녀들에게 지시하는 저 여인은\n누구의 아내나 딸인가?",
    3561: (
        "저분은 \x1bCA이시이 쓰네노부\x1bCZ의 따님 \x1bCA히코쓰루\x1bCZ 님입니다.\n"
        "예전에는 \x1bCA노토미 노부즈미\x1bCZ 님께 시집갔지만,\n"
        "\x1bCA노토미\x1bCZ 님이 전사해 지금은 과부이십니다……"
    ),
    3562: "호오.\n그렇다면 지금은 혼자인가……",
    3563: (
        "기지를 발휘해 시녀들을 지휘할 뿐 아니라,\n"
        "앞장서 정어리를 굽는 \x1bCA히코쓰루\x1bCZ의 솜씨에\n"
        "매료된 \x1bCA나오시게\x1bCZ는 훗날 정식으로 청혼했다."
    ),
    3564: (
        "전국시대에는 드문 연애결혼으로\n"
        "아내가 된 \x1bCA히코쓰루\x1bCZ는 총명함과 포용력으로,\n"
        "냉철한 군사 \x1bCA나베시마 나오시게\x1bCZ를 뒷받침했다고 한다……"
    ),
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    3442: ["dynamic_given_name_spacing_requires_runtime_review"],
    3448: ["otomoshu_term_requires_glossary_review"],
    3456: ["ryozen_castle_reading_requires_glossary_review"],
    3461: ["nobukatsu_name_reading_requires_glossary_review"],
    3481: ["katsuie_name_reading_requires_glossary_review"],
    3486: ["kaido_ichi_no_yumitori_rendering_requires_glossary_review"],
    3498: ["kato_war_term_requires_glossary_review"],
    3502: ["kanto_titles_and_place_readings_require_glossary_review"],
    3504: ["magokuro_identity_requires_context_review"],
    3527: ["tsutsujigasaki_yakata_term_requires_glossary_review"],
    3546: ["tenkyu_title_requires_glossary_review"],
    3549: ["koshu_hatto_no_shidai_term_requires_glossary_review"],
    3550: ["hikotsuruhime_name_reading_requires_glossary_review"],
    3561: ["notomi_name_reading_requires_glossary_review"],
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
    if len(ids) != 124 or ids != sorted(TRANSLATIONS):
        raise ValueError("batch4 ids are not the exact 124 displayed entries")
    return ids


def event_for(entry_id: int) -> str:
    matches = [
        event["event_id"]
        for event in EVENTS
        if event["start_id"] <= entry_id <= event["end_id"]
    ]
    if len(matches) != 1:
        raise ValueError(f"id {entry_id} does not map to one batch4 event group")
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
        language: shared.load_source(path, language)
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
            f"batch4 range contains all-language shared internal keys: {display_failures}"
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
        3440,
        3441,
        3460,
        3461,
        3484,
        3485,
        3524,
        3525,
        3549,
        3550,
        3564,
        3565,
    )
    evidence = {
        "schema": "nobu16.kr.event-dialogue-alignment-evidence.v4",
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
        "schema": "nobu16.kr.event-dialogue-review-index.v4",
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
        raise ValueError("batch4 public artifact contains source-script text")

    visible_lengths = {
        entry_id: [
            len(common.ESC_RE.sub("", line))
            for line in TRANSLATIONS[entry_id].splitlines()
        ]
        for entry_id in ids
    }
    validation = {
        "schema": "nobu16.kr.event-dialogue-generation-validation.v4",
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
            "current_font_or_installer_must_not_include_batch4": True,
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
            "existing_v01_v02_v03_artifacts_modified": False,
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
