#!/usr/bin/env python3
"""Build source-free ev_strdata event and ending batch v0.17 artifacts."""

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


BATCH_ID = "ev-strdata-events-endings-3277-3484-v0.17"
OVERLAY_NAME = "ev_strdata_ko_events_and_endings_3277_3484.v0.17.json"
EVIDENCE_NAME = "alignment_evidence.v0.17.json"
REVIEW_NAME = "review_index.v0.17.json"
VALIDATION_NAME = "validation.v0.17.json"

SCOPE_START = 3277
SCOPE_END = 3484
NEXT_DISPLAY_ID = 3485
TRANSLATED_COUNT = 190
INSPECTED_COUNT = 208
DEFERRED_COUNT = 18

TRANSLATED_IDS_SHA256 = "DF5BBB1969BCE6272FDD34364D4967AD437F8EE384586B67E40AD3B72180E7C4"
TRANSLATION_MAP_SHA256 = "BF3CD704E04E981DAC899FCA880B6FFDCBA597C749B7A6E4244B5D72503934A3"
SOURCE_SC_HASHES_SHA256 = "0CC69D44416806E69780A9D2BA79F5FB65CCEDC1B25018D72CA7A9B91EEC0536"
ALL_REFERENCE_HASHES_SHA256 = "B4C19061A335F9C49F1E0A5D3220CE3AFB3E769A1C5C8A5C45E88971DE7A72E4"
INSPECTED_IDS_SHA256 = "BE01932BBA2B73D8684B9E66088F876D558ADB189DC5089D4B9F5ADAB484AFE7"
DEFERRED_IDS_SHA256 = "CBD6A8F8CB20A423BE5D38411A6AB667ACECB736DCE08404B714ABDC1882D9FA"
DEFERRED_REFERENCE_HASHES_SHA256 = "939A78F21D7E2B16BBA0B78310F296F43CB5777B1AAC6C28188AAFC87CC9F049"
PREVIOUS_DEFERRED_UNION_COUNT = 531
PREVIOUS_DEFERRED_UNION_SHA256 = "C4C66D1ED26A140E6BAE5C68185FEDD869CA2AB7E636F348DEDDF256C99BF31F"
EMPTY_IDS_SHA256 = "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
NEXT_DISPLAY_REFERENCE_HASHES = {
    "SC": "8924AC440D0E1C827C03E06B7EBEC611AA4D55E1493B7847EC7729F0BF0340FF",
    "JP": "5A4BCA7F5B4BA29E2C58FDCC36ED410A75B911554552C9B035463ED957CB6DA9",
    "TC": "D73F381B4FC9BADEBF42AD81D47B2F8D42968E54268D75A095F1EE10D8F80405",
}

TRANSLATIONS = {
    3277: "\x1bCC사쓰마국\x1bCZ·\x1bCC보노쓰\x1bCZ―",
    3278: "아……!",
    3279: "주님, 감사합니다.\n지금껏 제 여정을 이끌어 주셨습니다.",
    3280: "‘나는 길이다’라고 하신 주님,\n저희가 나아갈 길을 인도해 주소서.",
    3281: "예수회 선교사\n\x1bCA프란치스코 하비에르\x1bCZ―",
    3282: "말라카에서 포교하던 중,\n일본인 \x1bCA야지로\x1bCZ에게 일본의 사정을 듣고\n바다를 건너기를 간절히 바랐다.",
    3283: "이해에 그는 \x1bCA야지로\x1bCZ와\n여러 선교사를 이끌고 처음 일본 땅을 밟았다.",
    3284: "이 나라 사람들에게 ‘구원’을 전해야 한다……",
    3285: "\x1bCA하비에르\x1bCZ는 \x1bCC가고시마\x1bCZ에 상륙한 뒤\n2년 남짓 일본 각지를 돌며\n수많은 다이묘와 백성에게 교리를 전했다.",
    3286: "그 뒤로 기독교는\n일본에 조금씩 퍼져 나갔다……",
    3287: "스승님,\n와 주셔서 기쁩니다.",
    3288: "별말씀을요. 전하께서 \x1bCC미노\x1bCZ를 얻어\n천하를 향한 발판을 마련하셨는데\n어찌 축하하러 오지 않겠습니까.",
    3289: "그 일 말인데, 스승님.\n나는 이곳에 자리 잡으려 하오.\n어떻게 생각하시오?",
    3290: "하하하.\n전하께서 가실 길은 전하만이 정할 수 있지요……\n빈승이 막아도 소용없는 일입니다.",
    3291: "게다가 이곳은 \x1bCC교토\x1bCZ와 가까운 요충지이니\n빈승이 말릴 까닭도 없습니다……",
    3292: "그렇군.\n그렇다면 스승님,\n이 땅에 좋은 이름을 붙이고 싶소.",
    3293: "\x1bCA노부나가\x1bCZ가 함락한 \x1bCC이나바야마성\x1bCZ의 성하 마을은\n당시 \x1bCC이노쿠치\x1bCZ라 불렸다.",
    3294: "오, 그런 생각을 하셨군요.\n\x1bCC이나바야마\x1bCZ에는 예부터\n\x1bCC기잔\x1bCZ이라는 운치 있는 별칭이 있었다 합니다.",
    3295: "당나라의 산 이름에서 따온 것인가.\n그렇다면 \x1bCC이노쿠치\x1bCZ는 \x1bCC기잔\x1bCZ 기슭이니……\n‘\x1bCC기후\x1bCZ’라 부르면 어떻겠소?",
    3296: "허허허.\n참으로 훌륭한 이름이라 생각합니다.",
    3297: "\x1bCA주 문왕\x1bCZ은 \x1bCC기산\x1bCZ에서 천하를 평정했고,\n\x1bCA공자\x1bCZ는 \x1bCC곡부\x1bCZ에서 태어나 학문을 닦았지요.\n틀림없이 복된 땅이 될 것입니다……",
    3298: "그럼 정했소!\n이제부터 이 마을을 \x1bCC기후\x1bCZ라 부르겠소.\n마을을 굽어보는 \x1bCC이나바야마성\x1bCZ은 \x1bCC기후성\x1bCZ이다!",
    3299: "성과 마을 모두 내가 새로 세우겠다.\n나의 천하는 이곳에서 시작된다.",
    3300: "그렇다면 전하.\n도장에 이 말을\n새겨 보시는 건 어떻겠습니까?",
    3301: "이것은……?\n‘천하포무’로군.",
    3302: "그렇습니다.\n전해지는 말로는 \x1bCA주 무왕\x1bCZ이 일곱 덕으로\n천하를 평정했다 하지요.",
    3303: "무라는 글자는\n창을 멈춘다는 뜻으로도\n풀이할 수 있습니다.",
    3304: "자, 잠깐만, 스승님!\n나도 이제 오와리의 멍청이가 아니오.\n긴 강론은 내가 은거한 뒤에 해 주시오.",
    3305: "하지만 천하포무…… 그 말은 마음에 드는군.\n이 도장이 딱 좋겠소!\n고맙소, 스승님.",
    3306: "하하하, 좋습니다, 좋아요.\n그런 면은 여전하신 듯하여\n빈승도 안심했습니다.",
    3307: "이름을 붙인 경위에는 여러 설이 있으나,\n어쨌든 \x1bCC이노쿠치\x1bCZ 마을은 ‘\x1bCC기후\x1bCZ’로,\n\x1bCC이나바야마성\x1bCZ은 ‘\x1bCC기후성\x1bCZ’으로 다시 세워졌다.",
    3308: "이와 함께 \x1bCA노부나가\x1bCZ는\n‘천하포무’ 도장을 쓰기 시작하며\n자신의 뜻을 천하에 알렸다……",
    3311: "\x1bCC오우\x1bCZ는 교토에서 멀리 떨어져 있어\n무로마치 막부가 세워진 이래\n다이묘들의 다툼과 전쟁이 끊이지 않았다……",
    3312: "그러나 \x1bCB[bus] 가문\x1bCZ이 적극적으로 세력을 넓힌 끝에\n마침내 \x1bCC도호쿠\x1bCZ 지방이 하나로 통일되었다.",
    3313: "아직 온 나라가 전란에 휩싸여 있었으나,\n\x1bCC오우\x1bCZ만은 \x1bCB[bus] 가문\x1bCZ의 통치 아래\n잠시나마 평화를 누릴 수 있었다……",
    3316: "무로마치 막부가 세워진 이래\n여러 세력의 이해관계가 복잡하게 얽힌 \x1bCC간토\x1bCZ에서는\n전란이 일어나는 일이 드물지 않았다…… ",
    3317: "그러나 \x1bCB[bus] 가문\x1bCZ이 적극적으로 세력을 넓힌 끝에\n마침내 \x1bCC간토\x1bCZ 지방이 하나로 통일되었다.",
    3318: "아직 온 나라가 전란에 휩싸여 있었으나,\n\x1bCC간토\x1bCZ만은 \x1bCB[bus] 가문\x1bCZ의 통치 아래\n잠시나마 평화를 누릴 수 있었다……",
    3321: "\x1bCC호쿠리쿠\x1bCZ는 중앙과 지방을 잇는 요충지로,\n\x1bCC기나이\x1bCZ와 \x1bCC간토\x1bCZ 양쪽의 정세와 다툼에 휘말려\n전쟁이 끊이지 않았다…… ",
    3322: "그러나 \x1bCB[bus] 가문\x1bCZ이 적극적으로 세력을 넓힌 끝에\n마침내 \x1bCC호쿠리쿠\x1bCZ 지방이 하나로 통일되었다.",
    3323: "아직 온 나라가 전란에 휩싸여 있었으나,\n\x1bCC호쿠리쿠\x1bCZ만은 \x1bCB[bus] 가문\x1bCZ의 통치 아래\n잠시나마 평화를 누릴 수 있었다……",
    3326: "험준한 산들로 둘러싸인 \x1bCC고신\x1bCZ 지방은\n수많은 군웅이 할거하여\n싸움이 끊이지 않던 땅이었다…… ",
    3327: "그러나 \x1bCB[bus] 가문\x1bCZ이 적극적으로 세력을 넓힌 끝에\n마침내 \x1bCC고신\x1bCZ 지방이 하나로 통일되었다.",
    3328: "아직 온 나라가 전란에 휩싸여 있었으나,\n\x1bCC고신\x1bCZ만은 \x1bCB[bus] 가문\x1bCZ의 통치 아래\n잠시나마 평화를 누릴 수 있었다……",
    3331: "\x1bCC가미가타\x1bCZ와 \x1bCC간토\x1bCZ를 잇는 \x1bCC도카이도\x1bCZ 연안에는\n강대한 다이묘가 잇따라 등장해\n세력 다툼이 갈수록 치열해졌다…… ",
    3332: "그러나 \x1bCB[bus] 가문\x1bCZ이 적극적으로 통일에 나선 끝에\n마침내 \x1bCC도카이\x1bCZ 지방이 하나로 통일되었다.",
    3333: "아직 온 나라가 전란에 휩싸여 있었으나,\n\x1bCC도카이\x1bCZ 지방만은 \x1bCB[bus] 가문\x1bCZ의 통치 아래\n잠시나마 평화를 누릴 수 있었다……",
    3336: "오닌의 난으로 황폐해진 \x1bCC교토\x1bCZ를 비롯한\n\x1bCC기나이\x1bCZ 일대는 여러 다이묘가\n막부의 주도권을 놓고 다투는 격전지였다.",
    3337: "그러나 질서를 바로잡으려는\n\x1bCB[bus] 가문\x1bCZ의 끊임없는 노력으로\n마침내 \x1bCC긴키\x1bCZ 지방이 하나로 통일되었다.",
    3338: "아직 온 나라가 전란에 휩싸여 있었으나,\n\x1bCC긴키\x1bCZ만은 \x1bCB[bus] 가문\x1bCZ의 통치 아래\n잠시나마 평화를 누릴 수 있었다……",
    3341: "남북조의 다툼 이래\n권세를 잡은 슈고 다이묘가 끊임없이 바뀌며 \n\x1bCC주고쿠\x1bCZ 지방에서는 수많은 전투가 벌어졌다…… ",
    3342: "\x1bCB[bus] 가문\x1bCZ은 여러 세력의 다툼 속에서 두각을 나타냈고,\n적극적인 공세 끝에\n마침내 \x1bCC주고쿠\x1bCZ 지방을 하나로 통일했다.",
    3343: "아직 온 나라가 전란에 휩싸여 있었으나,\n\x1bCC주고쿠\x1bCZ 지방만은 \x1bCB[bus] 가문\x1bCZ의 통치 아래\n잠시나마 평화를 누릴 수 있었다……",
    3346: "전국시대 내내 걸출한 다이묘가 나타나지 못한 데다, \n\x1bCC긴키\x1bCZ와 \x1bCC주고쿠\x1bCZ 다이묘들의 다툼에 휘말려\n\x1bCC시코쿠\x1bCZ 지방에서는 강대한 세력이 자라지 못했다……",
    3347: "그러나 \x1bCB[bus] 가문\x1bCZ의 적극적인 공세 끝에\n마침내 \x1bCC시코쿠\x1bCZ 지방이 하나로 통일되었다.",
    3348: "아직 온 나라가 전란에 휩싸여 있었으나,\n\x1bCC시코쿠\x1bCZ만은 \x1bCB[bus] 가문\x1bCZ의 통치 아래\n잠시나마 평화를 누릴 수 있었다……",
    3351: "남북조의 다툼 이래 전통 있는 슈고 다이묘들이\n서로 등을 돌리고 죽고 죽이는 싸움을 거듭해\n\x1bCC규슈\x1bCZ 지방에서는 전쟁이 끊이지 않았다.",
    3352: "그러나 이를 기회로 삼은 \x1bCB[bus] 가문\x1bCZ이\n적극적인 공세로 세력을 넓힌 끝에\n마침내 \x1bCC규슈\x1bCZ 전역이 하나로 통일되었다.",
    3353: "아직 온 나라가 전란에 휩싸여 있었으나,\n\x1bCC규슈\x1bCZ만은 \x1bCB[bus] 가문\x1bCZ의 통치 아래\n잠시나마 평화를 누릴 수 있었다……",
    3354: "전하, 조정에서\n칙사가 왔습니다!",
    3355: "뭐라? 칙사라고?\n대체 무슨 일이지?",
    3356: "\x1bCA[bus]\x1bCZ 공, 반갑소.\n천황께서 그대의 통일 대업을 크게 기뻐하셨소.",
    3357: "성은이 망극하옵니다.\n천하의 평정을 위한 저희의 노력이\n천황 폐하께 전해졌다니 황공할 따름입니다……",
    3358: "그리고 천황께서 특별히 분부하셨소.\n관백, 정이대장군, 태정대신 가운데 하나를 맡으라 하셨소.",
    3359: "뭐라……!",
    3360: "모두 천하인에게 걸맞은 조정의 요직이니\n원하는 자리를 고르면 되오.\n자, 어느 자리로 정했소……?",
    3361: "폐하의 뜻은 참으로 감사하오나\n저는 모든 관직을 사양하고자 합니다.",
    3362: "뭐라!?\n칙명을 거절하겠다는 것이오!\n대체 무슨 생각이오?",
    3363: "천하태평의 대업은 아직 이루는 중입니다.\n지금의 저로서는 그런 중직을 맡을 수 없습니다.\n참으로 황공하옵니다……",
    3364: "제가 \x1bCA[bum]\x1bCZ로서 진정한 천하통일을 이룬 뒤\n그때 다시 삼가 생각해 보겠습니다.",
    3365: "그렇소…… 흠……\n폐하께서 몹시 실망하시겠군.\n알겠소. 그대의 뜻을 폐하께 아뢰리다.",
    3366: "정이대장군은 무가의 동량에게 걸맞은 자리입니다.\n부족한 몸이오나\n장군직을 삼가 받들겠습니다.",
    3367: "알겠소. 폐하께 아뢰겠소.\n조만간 사자를 보내\n장군 임명의 칙명을 전하게 하리다……",
    3368: "정이대장군은 무가의 동량에게 걸맞은 자리입니다.\n부족한 몸이오나\n장군직을 삼가 받들겠습니다.",
    3369: "알겠소. 폐하께 아뢰겠소.\n조만간 사자를 보내\n장군 임명의 칙명을 전하게 하리다……",
    3370: "하지만 지금도 장군이 재임 중인데\n제가 억지로 그 자리를 차지해도\n정말 괜찮겠습니까?",
    3371: "그 일이라면 \x1bCA[bt]\x1bCZ 공에게 약속을 받아 두었소.\n조만간 조용히 현 장군을 물러나게 할 것이니\n걱정하지 않아도 되오.",
    3372: "그렇다면 여러 신하의 으뜸으로서\n조정의 정무를 관장하는 관백직을 받들겠습니다.",
    3373: "알겠소. 폐하께 아뢰겠소.\n조만간 사자를 보내\n관백 임명의 칙명을 전하게 하리다……",
    3374: "하지만 관백은 예부터 \x1bCB후지와라 북가\x1bCZ의\n적통인 \x1bCB섭관가\x1bCZ만 오를 수 있던 요직입니다.\n제가 맡아도 정말 괜찮겠습니까?",
    3375: "폐하께서는 예부터 \x1bCB섭관가\x1bCZ가 맡아 온 전통보다\n그대가 천하를 평정한 공적을 더 높이 평가하셨소.",
    3376: "그러니 옛 선례를 깨서라도\n그대에게 관백직을 내리려 하시는 것이오.\n기꺼이 받아들이시오.",
    3377: "그렇다면 태정관의 최고위이자\n조정의 정점에 서는 태정대신직을 받들겠습니다.",
    3378: "알겠소. 폐하께 아뢰겠소.\n조만간 사자를 보내\n태정대신 임명의 칙명을 전하게 하리다……",
    3379: "이 \x1bCA[bum]\x1bCZ가\n언젠가 조정의 최고 관직에 오를 줄이야……",
    3380: "그대가 천하를 평정한 공적을\n폐하께서 그만큼 높이 평가하신다는 뜻이오.",
    3381: "그렇다면 여러 신하의 으뜸으로서\n조정의 정무를 관장하는 관백직을 받들겠습니다.",
    3382: "알겠소. 위에 보고하겠소.\n며칠 뒤 관백 임명의 뜻을 전할 칙사가 올 것이오……",
    3383: "하지만 지금도 무가 출신 관백이 재임 중인데\n제가 그 관직을 빼앗듯 맡아도\n정말 괜찮겠습니까?",
    3384: "문제없소. \x1bCA[bk]\x1bCZ 공이 남몰래\n관백직을 사임하겠다고 약속했소.\n그러니 걱정할 것 없소.",
    3385: "전국의 모든 다이묘가\n\x1bCB[bus]\x1bCZ의 지배에 따르겠다고 맹세했다.",
    3386: "\x1bCA[bu]\x1bCZ는 천하의 평정을 드높이 선포하고\n전국에 사사로운 싸움을 금했다. 어떤 이유로도\n다이묘가 제멋대로 영토를 다툴 수 없게 되었다.",
    3387: "백 년 동안 이 나라 곳곳에서 무사들이 벌인\n격렬하고도 무익한 싸움이 마침내 끝났다.\n이로써 전국시대는 막을 내렸다.",
    3388: "참으로 긴 여정이었지만……\n마침내 전쟁 없는 세상을 맞이했다.\n이 또한 여러 다이묘가 협력해 준 덕분이다.",
    3389: "이 태평성대를 하루라도 오래 이어 가려면\n서둘러 새로운 나라를 세워야 한다……!",
    3390: "\x1bCB[bus] 가문\x1bCZ이 전국의 모든 성을 장악하고\n맞설 수 있는 세력을 모조리 없앴다.\n마침내 천하통일을 이룬 것이다.",
    3391: "\x1bCB[bu]\x1bCZ는 천하의 평정을 드높이 선포하고\n전국에 사사로운 싸움을 금했다. 이제 누구도\n제멋대로 영토를 다툴 수 없게 되었다.",
    3392: "백 년 동안 이어진 전국시대가 막을 내리고\n‘\x1bCB[bus]\x1bCZ의 평화’라 불리는 시대가 찾아왔다……",
    3393: "참으로 긴 여정이었지만……\n이렇게 전쟁 없는 세상을 맞이했다.\n모두 가신들이 힘써 준 덕분이다.",
    3394: "‘창업은 쉬우나 수성은 어렵다’고 했다.\n한시라도 빨리 \x1bCB[bus] 가문\x1bCZ의 지배를 굳혀\n이 태평성대를 하루라도 오래 지켜야 한다……!",
    3395: "\x1bCA[bu]\x1bCZ는 관백으로서 전국을 통일하고\n무가 관백이 각지의 다이묘를 다스리는 새 정권을 세웠다.",
    3396: "이렇게 \x1bCA[bu]\x1bCZ는 관백에 취임하고\n\x1bCC[cuh]\x1bCZ에 정무 기관을 두었다. 무가 관백이\n각지의 다이묘를 다스리는 새 정권을 세운 것이다.",
    3397: "\x1bCA[bu]\x1bCZ는 태정대신에 임명되어\n정무 기관을 설치했다. 각지의 다이묘를 다스리는 천하인,\n‘\x1bCC[cuh]\x1bCZ 전하’라 불리게 되었다.",
    3398: "\x1bCA[bu]\x1bCZ가 천하를 통일하자 조정은\n\x1bCB아시카가 가문\x1bCZ을 대신할 무가의 동량으로 인정했다.\n정이대장군에 임명하고 막부 개설을 허락한 것이다.",
    3399: "조정도 \x1bCA[bu]\x1bCZ의 공적을 인정하여\n정이대장군에 임명했다.\n\x1bCA[bus]\x1bCZ 막부가 성립한 것이다.",
    3400: "\x1bCA[bu]\x1bCZ는 정이대장군이 되어\n무가의 동량으로서\n새로운 막부를 열었다.",
    3401: "\x1bCA[bu]\x1bCZ는 정이대장군으로서\n전국을 통일했다. 진정한 무가의 동량이 되어\n무로마치 막부를 다시 일으켰다……",
    3402: "\x1bCA[bu]\x1bCZ의 위세는 \x1bCB아시카가 종가\x1bCZ를 능가해\n진정한 무가의 동량으로 인정받았다. 정이대장군에\n임명되어 무로마치 막부를 다시 일으켰다.",
    3403: "그리고 세월이 흘러……\n\x1bCA[bus]\x1bCZ 정권은 안정된 통치를 이어 가며\n대다수 백성의 마음을 얻었다.",
    3404: "많은 이가 기다리던 전쟁 없는 시대가\n마침내 찾아왔으니 당연한 일이었다.\n전국시대는 그렇게 막을 내렸다.",
    3405: "\x1bCA[bus]\x1bCZ 정권은 그 뒤로도 수많은 시련을\n이겨 냈다. 천재지변, 정변, 재정난……\n문제를 하나씩 착실히 해결해 나갔다.",
    3406: "그때마다 사회의 제도를 고치고\n안정된 통치 아래 문화와 경제가 꽃피는\n황금시대를 이루어 냈다.",
    3407: "그 300년 역사는 일본사에 찬란히 빛나는\n\x1bCA[bus]\x1bCZ 시대로서\n사람들의 기억에 새겨졌다……",
    3408: "그리고 세월이 흘러……\n천하에 평화를 가져온 \x1bCA[bus]\x1bCZ 정권은\n국내의 통치 기반을 다지는 데 힘썼다.",
    3409: "\x1bCC[cuh]\x1bCZ를 국정의 중심지로 정비하고\n새로운 제도의 틀을 마련했으며\n다시는 전란이 일어나지 않도록 경계를 강화했다.",
    3410: "그러나 때로는 그 경계가 지나친 규제를 낳아\n종교와 경제, 신분을 비롯한 모든 분야가\n경직되기도 했다……",
    3411: "이질적인 존재를 용납하지 않는 굳건한 봉건 지배는\n200년 동안 이어지며\n\x1bCA[bus]\x1bCZ 시대라 불리는 세상을 이루었다.",
    3412: "그리고 세월이 흘러……\n\x1bCB[bus] 가문\x1bCZ의 지배는 유력 다이묘들의 도움을 받아\n안정기에 접어들었다.",
    3413: "전란에서 벗어난 사람들은 해방감에 힘입어\n여러 나라와의 교역에 몰두했고\n일본은 큰 경제 발전의 시대를 맞이했다.",
    3414: "하지만 그 경제 발전의 혜택은\n\x1bCB[bus] 가문\x1bCZ뿐 아니라 백성과\n유력 다이묘들의 힘까지 키웠다.",
    3415: "마침내 \x1bCA[bis]\x1bCZ 등의 다이묘는\n\x1bCB[bus] 가문\x1bCZ의 통치를 꺼리며\n점차 독립하려는 움직임을 보였다.",
    3416: "그럼에도 \x1bCA[bum]\x1bCZ가 기틀을 다진\n\x1bCA[bus]\x1bCZ 정권은 약 150년 동안\n그 명맥을 이어 갔다.",
    3417: "그리고 세월이 흘러……\n유력 다이묘들의 보좌를 받은 \x1bCB[bus] 가문\x1bCZ은\n안정된 지배를 이루었다.",
    3418: "사람들은 한동안 전쟁을 잊고\n평화로운 삶을 누렸다. 그러나 잇따른 천재지변으로\n\x1bCA[bus]\x1bCZ 정권은 심각한 재정난에 빠졌다.",
    3419: "중앙의 통치가 흔들리는 틈을 타\n각지의 유력 다이묘들이 할거하면서\n다시 분권 체제로 돌아갔다.",
    3420: "초대 \x1bCA[bum]\x1bCZ가 한때 온존시킨 \x1bCA[bis]\x1bCZ 등의 세력이\n도리어 화근이 되었는지도 모른다.",
    3421: "각지의 다이묘가 다시 천하를 다투게 되었으나\n100년 동안 일본의 평화를 지킨 \x1bCA[bus]\x1bCZ 시대는\n사람들의 기억에 오래도록 남았다.",
    3422: "그리고 세월이 흘러……\n새로 시작된 \x1bCB[bus] 가문\x1bCZ의 통치는\n전국의 전란을 끝냈지만,",
    3423: "다시는 전쟁을 일으키지 않으려 한\n\x1bCB[bus] 가문\x1bCZ의 통치는 지나치게 강압적이었고\n다이묘와 백성의 불만이 쌓여 갔다.",
    3424: "한동안 겉으로 터져 나오지는 않았으나\n정권이 여러 대를 거치는 동안\n불온한 움직임은 점점 거세졌다……",
    3425: "마침내 80년이 지나 각지에서 반란이 잇따랐다.\n더는 힘으로 억누를 수 없게 되어\n일본에는 다시 전란의 시대가 찾아왔다.",
    3426: "\x1bCB[bus] 가문\x1bCZ은 오닌의 난 뒤의 \x1bCB아시카가 쇼군가\x1bCZ처럼\n실권을 잃고\n명목상의 동량으로만 존속했다……",
    3427: "그리고 세월이 흘러……\n\x1bCB[bus] 가문\x1bCZ의 천하통일은\n평화로운 시대가 오리라는 기대를 낳았다.",
    3428: "하지만 다소 강압적으로 추진한 통일 사업에\n백성은 큰 불만을 품었고, \x1bCA[bu]\x1bCZ의 죽음을\n계기로 분노가 폭발했다.",
    3429: "곳곳에서 잇키가 잇따르자\n\x1bCB[bis] 가문\x1bCZ 등 유력 다이묘는 \x1bCA[bus]\x1bCZ의 지배를 떠나\n도리어 혼란을 세력 다지기에 이용했다.",
    3430: "한 시대의 영걸 \x1bCA[bu]\x1bCZ가 세상을 떠난 뒤\n불과 몇 년 만에\n일본은 다시 혼돈의 전국시대로 돌아갔다……",
    3431: "그리고 세월이 흘러……\n일본은 \x1bCB[bus] 가문\x1bCZ의 천하통일로\n잠시 평화로운 시대를 맞이했다.",
    3432: "그러나 \x1bCA[bus]\x1bCZ 정권의 시선은 이미\n일본 국내에만 머물지 않고\n바다 너머를 향하고 있었다.",
    3433: "안정된 국내에서 특산품 생산을 장려하고\n전매로 얻은 막대한 이익을\n수출품 가공에 투자했다.",
    3434: "강대한 군사력과 경제력을 바탕으로\n해적과 유럽 상인이 활개 치는 동아시아 해역의\n교역권에 국가로서 뛰어들었다.",
    3435: "이렇게 \x1bCA[bus]\x1bCZ 일본은 근대 유럽 열강보다 앞서\n중상주의 무역 국가의 길을 걸으며\n세계 시장을 지배하게 되었다……",
    3436: "그리고 세월이 흘러……\n\x1bCA[bu]\x1bCZ는 통일한 지 몇 년 뒤 조정에\n자신과 가신들의 모든 관직을 반납했다.",
    3437: "이로써 일본 역사상 처음으로\n조정이 내린 관위를 권력의 바탕으로 삼지 않는\n독자적인 무가 정권이 탄생했다.",
    3438: "조정은 이 움직임에 당황했지만\n\x1bCA[bus]\x1bCZ 정권은 섭정과 관백, 대신 중심의 공가 사회와\n거리를 유지하면서도 조정 자체는 보전했다.",
    3439: "마침내 정치 권력은 \x1bCB[bus] 가문\x1bCZ이 맡고\n의례적 권위는 조정이 맡는 특수한 이중 국가로\n안정되어 그것이 일상이 되었다.",
    3440: "무가와 공가는 서로 부족한 부분을 보완하며\n오랫동안 태평한 세상을 지켜 나갔다.",
    3441: "전국시대에는\n\x1bCB쇼군 아시카가 가문\x1bCZ과 \x1bCB간레이 호소카와 가문\x1bCZ이 각각 분열하여\n오랜 세월 서로 다투고 있었다.",
    3442: "정쟁이 벌어질 때마다 \x1bCB아시카가 가문\x1bCZ의 당주는 \x1bCC교토\x1bCZ를 떠났다.\n현 쇼군 \x1bCA아시카가 [bm75]\x1bCZ 역시 \x1bCC교토\x1bCZ가 아닌\n\x1bCC오미\x1bCZ에서 원복을 치르고 쇼군직에 올랐다.",
    3443: "하지만 무로마치 막부의 본거지는 역시 \x1bCC교토\x1bCZ였다.\n\x1bCA[bm75]\x1bCZ도 여러 차례 \x1bCC교토\x1bCZ로 돌아갈 계획을 세우고\n\x1bCC교토\x1bCZ를 지배하는 \x1bCB미요시 가문\x1bCZ과 교섭했지만……",
    3444: "\x1bCB미요시 가문\x1bCZ은 본래 \x1bCB호소카와 가문\x1bCZ의 가신이었다.\n즉 \x1bCA[bm75]\x1bCZ가 보기에는 가신의 가신에 불과했다.\n자존심 탓인지 교섭은 좀처럼 나아가지 않았다.",
    3445: "또한 \x1bCB아시카가 가문\x1bCZ 안에서도 \x1bCB미요시 세력\x1bCZ을 원망하던\n\x1bCA호소카와 하루모토\x1bCZ 등이 계속 화친에 반대해\n\x1bCC교토\x1bCZ 귀환은 좀처럼 이루어지지 않았다.",
    3446: "이대로는 끝이 없겠군.\n\x1bCC교토\x1bCZ로 돌아가려면…… 여기서 \x1bCA하루모토\x1bCZ를 버리자.\n\x1bCA나가요시\x1bCZ와 교섭하는 것이다!",
    3447: "\x1bCA구보\x1bCZ 님께서 저희의 존재를 인정해 주신다면\n저희도 귀환을 막을 까닭이 없습니다.\n삼가 모시도록 하겠습니다.",
    3448: "\x1bCA미요시 나가요시\x1bCZ를 오토모슈, 곧 \x1bCB쇼군가\x1bCZ 직신으로\n인정하면서 양측은 화친했다.\n마침내 \x1bCA[bm75]\x1bCZ의 \x1bCC교토\x1bCZ 귀환이 눈앞에 다가왔다.",
    3449: "한편 끝까지 화친에 반대한\n\x1bCA호소카와 하루모토\x1bCZ 등은 \x1bCC교토\x1bCZ를 떠나 자취를 감췄다……",
    3450: "이제 와서 가신 집안인 \x1bCB미요시\x1bCZ와 손잡을 수 있겠느냐!\n나는 화의에 반대한다!\n끝까지 저항하겠다!",
    3451: "쇼군이 \x1bCC교토\x1bCZ로 돌아오기로 하자 오랜만에 무로마치 막부의\n질서가 회복되는 듯했으나\n그것도 오래가지는 못했다.",
    3452: "이제 반\x1bCB미요시\x1bCZ의 선봉이 된 \x1bCA호소카와 하루모토\x1bCZ 등은\n각지의 \x1bCB미요시\x1bCZ 가문 거점을 끈질기게 공격했다.\n새로운 \x1bCB아시카가\x1bCZ·\x1bCB미요시\x1bCZ 협조 체제가 흔들렸다.",
    3453: "이놈, \x1bCA하루모토\x1bCZ……!\n끝까지 우리에게 맞서겠다는 것이냐.\n\x1bCA구보\x1bCZ 님도 어찌 지켜보기만 하시는가!",
    3454: "…………",
    3455: "이윽고 \x1bCB미요시 가문\x1bCZ과의 화친에 소극적이던\n\x1bCA[bm75]\x1bCZ의 측근들 사이에서도 \x1bCA하루모토\x1bCZ에 동조하는 움직임이 나타나\n\x1bCA[bm75]\x1bCZ도 더는 발뺌할 수 없는 처지에 몰렸다.",
    3456: "그래도 \x1bCA[bm75]\x1bCZ는 입경을 시도했으나 경계하던\n\x1bCB미요시 세력\x1bCZ에 막혀 \x1bCC히가시야마\x1bCZ의 \x1bCC료젠성\x1bCZ에 틀어박혔다.\n이로써 화의는 완전히 무너졌다.",
    3457: "떠돌이 구보…… 역시 믿을 수 없군.\n\x1bCA하루모토\x1bCZ를 이용해 우리를 속이다니!",
    3458: "이런, \x1bCC교토\x1bCZ가 코앞인데 또 들어가지 못하다니!\n\x1bCB미요시\x1bCZ 놈들……\n정이대장군을 무엇으로 보는 것이냐!",
    3459: "\x1bCC료젠성\x1bCZ은 \x1bCB미요시군\x1bCZ의 공격으로 함락되었다.\n쇼군 \x1bCA[bm75]\x1bCZ는 다시 \x1bCC오미\x1bCZ로 달아났고\n\x1bCA하루모토\x1bCZ 등도 그 뒤를 따랐다.",
    3460: "결국 아무것도 달라지지 않았다.\n상황은 화친 전으로 완전히 돌아갔고\n\x1bCB아시카가\x1bCZ와 \x1bCB미요시\x1bCZ의 불신만 더 깊어졌다.",
    3461: "한때 형 \x1bCA노부나가\x1bCZ에게 등을 돌리고\n이노 전투에서 패했으나\n어머니의 중재로 목숨을 건진 \x1bCA오다 노부카쓰\x1bCZ―",
    3462: "하지만 그 치욕은\n그가 도저히 삼킬 수 없는 것이었다.\n재기를 노리며 남몰래 계책을 꾸몄다.",
    3463: "\x1bCA가쓰이에\x1bCZ, 이번에는 승산이 있다.\n이 \x1bCC오와리\x1bCZ에도 형과 맞서는 세력이 많다.\n그들과 손잡을 길을 마련했다!",
    3464: "\x1bCA노부카쓰\x1bCZ 님……",
    3465: "이번에야말로 내가 \x1bCB오다\x1bCZ의 당주다!\n멍청한 형은 이루지 못할\n평온한 \x1bCC오와리\x1bCZ를 세워 보이겠다!",
    3466: "\x1bCA노부카쓰\x1bCZ가 \x1bCA가쓰이에\x1bCZ에게 재기 계획을 밝힌\n며칠 뒤, 사태는 뜻밖의 방향으로 흘렀다.",
    3467: "뭐라!\n형님이 위독하다고?",
    3468: "예…… 갑작스러운 병으로 숨도 가쁘시다 합니다.\n내일을 기약할 수 없는 상태라\n마지막으로 \x1bCA노부카쓰\x1bCZ 님을 뵙고 싶다 하셨습니다……",
    3469: "그 형이 그토록 심한 병에 걸릴 줄이야……\n하지만 마지막에 그토록 미워하던 나를\n보고 싶다니, 사람의 정은 남아 있었나 보군.",
    3470: "아마 전하께서는 마지막 자리에서\n\x1bCB오다\x1bCZ의 가독을\n\x1bCA노부카쓰\x1bCZ 님께 잇게 하실 생각인 듯합니다……",
    3471: "오, 틀림없이 그렇겠지.\n형님에게는 아직 자식이 없으니\n나 말고는 후계자가 없다.",
    3472: "군사를 일으킬 필요도 없이\n\x1bCB오다\x1bCZ의 가독이 굴러 들어오다니……\n좋아, \x1bCC기요스성\x1bCZ으로 가자!",
    3473: "\x1bCA노부카쓰\x1bCZ는 가독을 잇게 한다는 유언을 기대하며\n병상에 누운 \x1bCA노부나가\x1bCZ를 문병하러\n\x1bCC기요스성\x1bCZ으로 들어갔다……",
    3474: "그리고\n다시는 돌아오지 못했다.",
    3475: "뻔히 보이는 꾀병에 속아 넘어가다니.\n솔직하다고는 할 수 있지만 전국의 세상에서는\n말 그대로 목숨을 앗아 갈 약점이로군……",
    3476: "피를 나눈 아우를 직접 베고도\n조금도 후회하지 않으십니까?",
    3477: "없다.\n전에 말했을 텐데.\n내가 보는 것은 \x1bCB오다 가문\x1bCZ이 아니다. 천하다!",
    3478: "\x1bCA가쓰이에\x1bCZ.\n너도 그것을 믿었기에\n\x1bCA간주로\x1bCZ의 계책을 내게 밀고한 것이겠지?",
    3479: "(\x1bCA노부카쓰\x1bCZ 님을 죽음으로 몰아넣은 것은\n\u3000다른 누구도 아닌 이 \x1bCA가쓰이에\x1bCZ다……\n\u3000언젠가는 그 대가를 치러야 한다.)",
    3480: "(하지만 이 결단이 잘못되지 않았음을 증명하려면\n\u3000앞으로 나는 온 마음을 다해\n\u3000전하의 천하 쟁취를 돕겠다!)",
    3481: "예……! 이제부터\n이 \x1bCA시바타 가쓰이에\x1bCZ, 전하의 천하 쟁취를 위해\n선봉에 서서 힘을 다하겠습니다!",
    3482: "친어머니 \x1bCA도타 고젠\x1bCZ이 슬픔에 잠긴 것은\n말할 것도 없었다. 하지만 \x1bCA노부카쓰\x1bCZ의 죽음은 뜻밖에도\n가문 안에 거의 동요를 일으키지 않았다.",
    3483: "\x1bCA노부카쓰\x1bCZ의 모반이 두 번째였던 데다\n전보다 \x1bCA노부나가\x1bCZ의 지배가 가문에\n깊이 뿌리내렸기 때문일지도 모른다.",
    3484: "어쨌든 \x1bCA노부카쓰\x1bCZ의 죽음은 \x1bCB오다\x1bCZ 가문을 결속시켰고\n\x1bCA노부나가\x1bCZ를 중심으로 \x1bCC오와리\x1bCZ를 통일하는 체제를\n더욱 굳건하게 만들었다.",
}

DEFERRED_INTERNAL_IDS = frozenset(
    {
        3309, 3310, 3314, 3315, 3319, 3320, 3324, 3325, 3329,
        3330, 3334, 3335, 3339, 3340, 3344, 3345, 3349, 3350,
    }
)
PRIOR_DEFERRED_BATCHES = (
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
)
PREVIOUS_DEFERRED_IDS = frozenset(
    entry_id
    for batch in PRIOR_DEFERRED_BATCHES
    for entry_id in batch["ids"]
)
CLASS_COUNTS = {
    "court_office_dialogue": 31,
    "historical_event_dialogue": 76,
    "national_ending_narration": 56,
    "regional_ending_narration": 27,
}
REPEATED_SOURCE_ID_GROUPS = (
    (3366, 3368),
    (3372, 3381),
)
TRANSLATED_UNIQUE_SOURCE_HASH_COUNT = 188


def classify(entry_id: int) -> str:
    if 3311 <= entry_id <= 3353:
        return "regional_ending_narration"
    if 3354 <= entry_id <= 3384:
        return "court_office_dialogue"
    if 3385 <= entry_id <= 3440:
        return "national_ending_narration"
    return "historical_event_dialogue"


def generated_file_map(root: Path) -> dict[str, bytes]:
    paths = (
        Path("public") / OVERLAY_NAME,
        Path("evidence") / EVIDENCE_NAME,
        Path("review") / REVIEW_NAME,
        Path(VALIDATION_NAME),
    )
    return {path.as_posix(): (root / path).read_bytes() for path in paths}


def deferred_metadata() -> list[dict[str, Any]]:
    return [
        {
            "classification": "internal_event_key",
            "status": "excluded",
            "reason": "ascii_event_lookup_key_not_display_text",
            "ids": sorted(DEFERRED_INTERNAL_IDS),
            "count": DEFERRED_COUNT,
            "ids_sha256": DEFERRED_IDS_SHA256,
            "ordered_reference_hashes_sha256": DEFERRED_REFERENCE_HASHES_SHA256,
            "excluded_from_overlay_and_translation_progress": True,
        }
    ]


def previous_deferred_overlap_metadata() -> dict[str, Any]:
    overlap_ids = sorted(DEFERRED_INTERNAL_IDS & PREVIOUS_DEFERRED_IDS)
    return {
        "previous_batches": [
            {
                "version": batch["version"],
                "batch_id": batch["batch_id"],
                "deferred_entry_count": batch["count"],
                "deferred_ids_sha256": batch["ids_sha256"],
            }
            for batch in PRIOR_DEFERRED_BATCHES
        ],
        "previous_deferred_union_entry_count": PREVIOUS_DEFERRED_UNION_COUNT,
        "previous_deferred_union_ids_sha256": PREVIOUS_DEFERRED_UNION_SHA256,
        "current_deferred_entry_count": DEFERRED_COUNT,
        "overlap_entry_count": len(overlap_ids),
        "overlap_ids_sha256": shared.hash_json(overlap_ids),
        "overlap_detected": bool(overlap_ids),
    }


def validate_batch_sources(loaded: dict[str, dict[str, Any]]) -> list[int]:
    ids = sorted(TRANSLATIONS)
    inspected_ids = list(range(SCOPE_START, SCOPE_END + 1))
    deferred_ids = sorted(DEFERRED_INTERNAL_IDS)

    if len(ids) != TRANSLATED_COUNT or ids[0] != SCOPE_START or ids[-1] != SCOPE_END:
        raise shared.EvStrDataError("v0.17 translated count or boundary changed")
    if len(inspected_ids) != INSPECTED_COUNT or len(deferred_ids) != DEFERRED_COUNT:
        raise shared.EvStrDataError("v0.17 inspected or deferred count changed")
    if set(ids) & DEFERRED_INTERNAL_IDS:
        raise shared.EvStrDataError("v0.17 translated and internal-key ids overlap")
    if sorted(ids + deferred_ids) != inspected_ids:
        raise shared.EvStrDataError("v0.17 inspected partition changed")
    if shared.hash_json(ids) != TRANSLATED_IDS_SHA256:
        raise shared.EvStrDataError("v0.17 translated id digest changed")
    if shared.hash_json(inspected_ids) != INSPECTED_IDS_SHA256:
        raise shared.EvStrDataError("v0.17 inspected id digest changed")
    if shared.hash_json(deferred_ids) != DEFERRED_IDS_SHA256:
        raise shared.EvStrDataError("v0.17 deferred id digest changed")
    if shared.hash_json([[entry_id, TRANSLATIONS[entry_id]] for entry_id in ids]) != TRANSLATION_MAP_SHA256:
        raise shared.EvStrDataError("v0.17 Korean translation map changed")

    for batch in PRIOR_DEFERRED_BATCHES:
        ordered = sorted(batch["ids"])
        if len(ordered) != batch["count"] or shared.hash_json(ordered) != batch["ids_sha256"]:
            raise shared.EvStrDataError(f"{batch['version']} deferred exclusion pin changed")
    if len(PREVIOUS_DEFERRED_IDS) != PREVIOUS_DEFERRED_UNION_COUNT:
        raise shared.EvStrDataError("v0.13-v0.16 deferred union count changed")
    if shared.hash_json(sorted(PREVIOUS_DEFERRED_IDS)) != PREVIOUS_DEFERRED_UNION_SHA256:
        raise shared.EvStrDataError("v0.13-v0.16 deferred union digest changed")
    overlap = sorted(DEFERRED_INTERNAL_IDS & PREVIOUS_DEFERRED_IDS)
    if overlap or shared.hash_json(overlap) != EMPTY_IDS_SHA256:
        raise shared.EvStrDataError("v0.17 exclusions overlap v0.13-v0.16 exclusions")

    class_counts = Counter(classify(entry_id) for entry_id in ids)
    if dict(sorted(class_counts.items())) != CLASS_COUNTS:
        raise shared.EvStrDataError("v0.17 functional classification counts changed")

    source_sc_hashes: list[str] = []
    all_reference_hashes: list[str] = []
    ids_by_source_hash: dict[str, list[int]] = defaultdict(list)
    replacement_by_source_hash: dict[str, str] = {}
    for entry_id in ids:
        references = [
            loaded[language]["table"].texts[entry_id]
            for language in shared.LANGUAGES
        ]
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
        prior = replacement_by_source_hash.setdefault(source_hash, TRANSLATIONS[entry_id])
        if prior != TRANSLATIONS[entry_id]:
            raise shared.EvStrDataError(
                f"id {entry_id}: repeated SC source has inconsistent Korean translations"
            )
    repeated_groups = tuple(
        tuple(group)
        for group in ids_by_source_hash.values()
        if len(group) > 1
    )
    if repeated_groups != REPEATED_SOURCE_ID_GROUPS:
        raise shared.EvStrDataError("v0.17 repeated-source groups changed")
    if len(ids_by_source_hash) != TRANSLATED_UNIQUE_SOURCE_HASH_COUNT:
        raise shared.EvStrDataError("v0.17 unique SC source count changed")
    if shared.hash_json(source_sc_hashes) != SOURCE_SC_HASHES_SHA256:
        raise shared.EvStrDataError("v0.17 ordered SC source hashes changed")
    if shared.hash_json(all_reference_hashes) != ALL_REFERENCE_HASHES_SHA256:
        raise shared.EvStrDataError("v0.17 ordered SC/JP/TC source hashes changed")

    deferred_reference_hashes: list[str] = []
    for entry_id in deferred_ids:
        references = [
            loaded[language]["table"].texts[entry_id]
            for language in shared.LANGUAGES
        ]
        if len(set(references)) != 1:
            raise shared.EvStrDataError(f"id {entry_id}: internal key differs by language")
        key = references[0]
        if not key or not key.isascii() or not all(char.isalnum() or char == "_" for char in key):
            raise shared.EvStrDataError(f"id {entry_id}: internal key classification changed")
        deferred_reference_hashes.extend(common.text_hash(text) for text in references)
    if shared.hash_json(deferred_reference_hashes) != DEFERRED_REFERENCE_HASHES_SHA256:
        raise shared.EvStrDataError("v0.17 deferred internal-key hashes changed")

    for language in shared.LANGUAGES:
        next_text = loaded[language]["table"].texts[NEXT_DISPLAY_ID]
        if not next_text.strip():
            raise shared.EvStrDataError(f"v0.17 next display is empty for {language}")
        if common.text_hash(next_text) != NEXT_DISPLAY_REFERENCE_HASHES[language]:
            raise shared.EvStrDataError(f"v0.17 next display anchor changed for {language}")
    return ids


def build_once(game_root: Path, out_root: Path) -> dict[str, Any]:
    loaded, before = shared.load_sources(game_root)
    ids = validate_batch_sources(loaded)
    deferred = deferred_metadata()
    overlap = previous_deferred_overlap_metadata()

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
                "translation_origin": "manual_sc_jp_tc_aligned_review",
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
        3308,
        3309,
        3310,
        3311,
        3350,
        3351,
        3384,
        3385,
        3440,
        3441,
        3460,
        3461,
        SCOPE_END,
        NEXT_DISPLAY_ID,
    )
    evidence = {
        "schema": "nobu16.kr.ev-strdata-alignment-evidence.v17",
        "batch_id": BATCH_ID,
        "resource": "ev_strdata",
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "translated_display_entry_count": TRANSLATED_COUNT,
            "inspected_entry_count": INSPECTED_COUNT,
            "deferred_internal_entry_count": DEFERRED_COUNT,
            "next_display_id": NEXT_DISPLAY_ID,
            "functional_section": "historical_events_regional_and_national_endings",
            "functional_class_counts": CLASS_COUNTS,
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
            "repeated_source_requires_identical_korean_translation",
            "ascii_internal_event_key_exclusion",
            "v013_through_v016_deferred_union_overlap_check",
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
        "deferred_internal_groups": deferred,
        "previous_deferred_overlap": overlap,
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.ev-strdata-review-index.v17",
        "batch_id": BATCH_ID,
        "quality_state": "event_and_ending_translation_draft_pending_runtime_review",
        "entry_count": TRANSLATED_COUNT,
        "entries": [
            {
                "id": entry_id,
                "status": "translated",
                "classification": classify(entry_id),
                "translation_origin": "manual_sc_jp_tc_aligned_review",
                "human_review_required": True,
                "runtime_reviewed": False,
                "uncertainty_flags": ["event_text_runtime_layout"],
            }
            for entry_id in ids
        ],
        "deferred_internal_groups": deferred,
        "previous_deferred_overlap": overlap,
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
            "v0.17 public artifact contains source script text or an embedded NUL"
        )

    binary = shared.common_binary_build(game_root, overlay_path)
    after = {
        relative: shared.sha256((game_root / Path(relative)).read_bytes())
        for relative in before
    }
    if before != after:
        raise shared.EvStrDataError("installed game resource changed during v0.17 build")

    artifacts = {
        path.relative_to(out_root).as_posix(): {
            "size": path.stat().st_size,
            "sha256": shared.sha256(path.read_bytes()),
        }
        for path in (overlay_path, evidence_path, review_path)
    }
    validation = {
        "schema": "nobu16.kr.ev-strdata-generation-validation.v17",
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
            "source_text_embedded": False,
        },
        "repeated_source_policy": {
            "same_source_same_translation_required": True,
            "translated_unique_source_hash_count": TRANSLATED_UNIQUE_SOURCE_HASH_COUNT,
            "translated_repeated_source_group_count": len(REPEATED_SOURCE_ID_GROUPS),
            "repeated_source_id_groups": [list(group) for group in REPEATED_SOURCE_ID_GROUPS],
            "failures": 0,
        },
        "deferred_internal_groups": deferred,
        "previous_deferred_overlap": overlap,
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
            "existing_v01_through_v016_artifacts_modified": False,
        },
    }
    validation_path = out_root / VALIDATION_NAME
    validation_path.parent.mkdir(parents=True, exist_ok=True)
    validation_path.write_bytes(shared.encode_json(validation))
    if shared.source_free_counts(validation_path.read_bytes()) != {
        "han_or_kana_count": 0,
        "embedded_nul_count": 0,
    }:
        raise shared.EvStrDataError("v0.17 validation is not source-free")
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
    with tempfile.TemporaryDirectory(prefix="nobu16-evstr17-a-") as first_tmp:
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr17-b-") as second_tmp:
            first = build_once(game_root, Path(first_tmp))
            second = build_once(game_root, Path(second_tmp))
            if first["files"] != second["files"]:
                raise shared.EvStrDataError(
                    "isolated A/B v0.17 public artifacts are not byte-identical"
                )
    final = build_once(game_root, out_root)
    if final["files"] != first["files"]:
        raise shared.EvStrDataError(
            "final v0.17 public artifacts differ from isolated A/B output"
        )
    after = {path.as_posix(): shared.sha256(path.read_bytes()) for path in source_paths}
    if before != after:
        raise shared.EvStrDataError("installed game resource changed across v0.17 build")
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
