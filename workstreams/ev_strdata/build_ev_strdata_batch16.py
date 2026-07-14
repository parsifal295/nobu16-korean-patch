#!/usr/bin/env python3
"""Build source-free ev_strdata label/narration batch v0.16 artifacts."""

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


BATCH_ID = "ev-strdata-labels-narration-3007-3276-v0.16"
OVERLAY_NAME = "ev_strdata_ko_labels_and_narration_3007_3276.v0.16.json"
EVIDENCE_NAME = "alignment_evidence.v0.16.json"
REVIEW_NAME = "review_index.v0.16.json"
VALIDATION_NAME = "validation.v0.16.json"

SCOPE_START = 3007
SCOPE_END = 3276
INSPECTED_START = 3007
INSPECTED_END = 3276
NEXT_DISPLAY_ID = 3277
TRANSLATED_COUNT = 174
LABEL_COUNT = 99
NARRATION_COUNT = 75
INSPECTED_COUNT = 270
DEFERRED_COUNT = 96

TRANSLATED_IDS_SHA256 = "C8227A840BE0A276B9951422CEECD1B604428EF3A2ECDCE9E2C2880684FD41D9"
TRANSLATION_MAP_SHA256 = "E831726760DE4C90F1D326EC78E557959397AD6841005C5F22790155303D5D5B"
SOURCE_SC_HASHES_SHA256 = "B10D37DF5F2429662BA8212532AB12F77757D5DCC3F320CEED5DCCC524375C87"
ALL_REFERENCE_HASHES_SHA256 = "61D924E0F885AF6CBD8301D98F857D527CA3F0B503C30DF2DAC58F5846F47DAF"
INSPECTED_IDS_SHA256 = "E38293552A963D3D3124111ED530C7C40F13E20EA9CDC35583BCB2ED5CCC0DFE"
DEFERRED_IDS_SHA256 = "06BD88F03E814D81DC107F52B4F1B1452FF8461677854C550FAB5BC1DDD94D00"
PREVIOUS_DEFERRED_IDS_SHA256 = "2B95F92D5D9B8AB6E96DEB1A412CB34957B24978FFF2C089254A42C3CE265245"
EMPTY_IDS_SHA256 = "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
NEXT_DISPLAY_REFERENCE_HASHES = {
    "SC": "827C30CED92044331CC48B1B214A13C18943FC5EAF283FE301321EEDC6306687",
    "JP": "C3F0362A6ED7646A2B60FFFF97ADFC592FCAAC7F159674C76DF345B242E70789",
    "TC": "E967FE5CCC3C2AAD85B77420018C2469CDEC7B9C4B380FDA230A7C0ECBA2F269",
}

LABEL_TRANSLATIONS = {
    3007: "호조 쓰나시게",
    3008: "깃카와 모토하루",
    3009: "오이와 유무",
    3010: "요도도노",
    3011: "무라카미 미치야스",
    3012: "다카하시 무네토라",
    3013: "호조 사부로",
    3014: "다치바나 긴치요",
    3015: "미츠키 요시요리",
    3016: "미츠키 요리츠나",
    3017: "다카하시 조운",
    3018: "다치바나 도세쓰",
    3019: "요시히메",
    3020: "가타쿠라 고주로",
    3021: "스에 하루카타",
    3022: "바바 노부하루",
    3023: "난부 노부나오",
    3024: "난부 도시나오",
    3025: "아네가코지 요시요리",
    3026: "아네가코지 요리쓰나",
    3027: "다케다 신겐",
    3028: "마쓰다이라 이에야스",
    3029: "우에스기 마사토라",
    3030: "우에스기 가게노부",
    3031: "오토모 소린",
    3032: "미요시 요시쓰구",
    3033: "우에스기 가게카쓰",
    3034: "야마가타 마사카게",
    3035: "도쿠가와 이에야스",
    3036: "도쿠가와 히데타다",
    3037: "도쿠가와 이에미쓰",
    3038: "우에스기 겐신",
    3039: "쓰가루 다메노부",
    3040: "쓰가루 노부히라",
    3041: "하시바 히데요시",
    3042: "하시바 히데요리",
    3043: "하시바 히데나가",
    3044: "하시바 히데쓰구",
    3045: "나오에 가네쓰구",
    3046: "다치바나 무네시게",
    3047: "호소카와 유사이",
    3048: "오사카성",
    3049: "도요토미 히데요시",
    3050: "도요토미 히데요리",
    3051: "도요토미 히데나가",
    3052: "도요토미 히데쓰구",
    3053: "고바야카와 히데아키",
    3054: "아시나 요시히로",
    3055: "아시나 고지로",
    3056: "소고 마사야스",
    3057: "우에스기 겐신",
    3058: "우에스기 마사토라",
    3059: "센토인",
    3060: "야마가타 마사카게",
    3061: "다케다 신겐",
    3062: "핫토리 한조",
    3063: "구로다 간베에",
    3064: "오이치",
    3065: "기노시타 도키치로",
    3066: "하시바 히데요시",
    3067: "도요토미 히데요시",
    3068: "마쓰다이라 모토노부",
    3069: "마쓰다이라 모토야스",
    3070: "도쿠가와 이에야스",
    3071: "이코마 이에무네",
    3072: "루이",
    3073: "다치바나 긴치요",
    3074: "가신",
    3075: "사이토 도시마사",
    3076: "우에스기 데루토라",
    3077: "사이토 다카마사",
    3078: "아시카가 요시아키",
    3079: "시마즈 류하쿠",
    3080: "모니와 쓰나모토",
    3081: "가모 야스히데",
    3082: "요시히로 시게타다",
    3083: "이주인 고칸",
    3084: "오토모 치카이에",
    3085: "깃카와 모토우지",
    3086: "유라 나리시게",
    3087: "가스가 도라쓰나",
    3088: "롯카쿠 조테이",
    3089: "나가사카 조칸사이",
    3090: "오야마 하루토모",
    3091: "롯카쿠 요시스케",
    3092: "시라카와 요시치카",
    3093: "모리 모토키요",
    3094: "아라키 도훈",
    3095: "아라키 도쿤",
    3096: "센 소에키",
    3097: "오타 산라쿠사이",
    3098: "덴토쿠지 호엔",
    3099: "야규 무네요시",
    3100: "구로다 조스이",
    3101: "마쓰마에 요시히로",
    3102: "사카자키 나오모리",
    3103: "오노 다다아키",
    3104: "아나야마 바이세쓰",
    3117: "야마다 교토쿠",
}

NARRATION_TRANSLATIONS = {
    3202: "\x1bCB가이 겐지\x1bCZ의 명문 \x1bCB다케다 가문\x1bCZ.\n\x1bCB아시카가 일문\x1bCZ의 명가 \x1bCB이마가와 가문\x1bCZ.\n\x1bCA이마가와\x1bCZ의 휘하를 벗어나 새 땅 \x1bCC간토\x1bCZ로 진출한 \x1bCB호조 가문\x1bCZ.",
    3203: "동국에 웅거한 세 대다이묘는,\n때로 손을 잡고 때로 서로 속이며,\n영토를 다투는 맞수로서 서로를 경계해 왔다.",
    3204: "그러나 덴분 23년(1554년),\n각자 배후에 적을 둔 세 가문의 이해가\n뜻밖에도 맞아떨어졌다.",
    3205: "이 기회를 놓칠 수 없다!\n즉시 움직인 이는 \x1bCB이마가와 가문\x1bCZ을 떠받친\n먹빛 승복의 군사 \x1bCA다이겐 소후\x1bCZ였다.",
    3206: "또 다른 이름은 \x1bCA셋사이 선사\x1bCZ. 범상치 않은 승려였다.",
    3207: "\x1bCA셋사이\x1bCZ는 두 가문에 재빨리 손을 써,\n\x1bCA이마가와 요시모토\x1bCZ·\x1bCA다케다 하루노부\x1bCZ·\n\x1bCA호조 우지야스\x1bCZ 각자의 적남에게",
    3208: "서로의 딸을 아내로 맞게 하는 혼담을 성사시켜,\n\x1bCC고소슨\x1bCZ 삼각 동맹 결성에 힘썼다.",
    3209: "마무리 단계로\n\x1bCA셋사이\x1bCZ는 \x1bCA하루노부\x1bCZ와 \x1bCA우지야스\x1bCZ를\n자신과 인연이 있는 \x1bCC스루가 젠토쿠지\x1bCZ에 초대했다.",
    3210: "오늘날 이 회담이 실재하지 않았다는 설도 있지만,\n세 거물이 정말 한자리에 모였다면\n무슨 이야기를 나눴을지 상상할수록 흥미롭다.",
    3211: "호걸끼리 서로 속내를 읽지 못하고, 읽히지도 않는다.\n하지만 그래도 상관없었다.",
    3212: "세 사람이 \x1bCC젠토쿠지\x1bCZ에서 손을 잡았다는 사실 자체가……\n주변의 여러 다이묘에게\n크나큰 위협이 되었으니 말이다.",
    3213: "타산과 이해, 그리고\n혼인으로 맺어진 삼각형은",
    3214: "향배가 끊임없이 바뀌던 전국시대에도\n매우 드물게 십수 년이라는 긴 세월 동안\n유지되었다.",
    3215: "서국 제일의 대국으로 칭송받던 \x1bCB오우치 가문\x1bCZ도 이제는\n주군을 죽이고 실권을 장악한\n\x1bCA스에 하루카타\x1bCZ의 꼭두각시로 전락했다.",
    3216: "한편 \x1bCA오우치\x1bCZ·\x1bCA아마고\x1bCZ라는 대국 사이를 오가며\n국인 세력에서 다이묘로 급성장한 \x1bCA모리 모토나리\x1bCZ는\n그 \x1bCA하루카타\x1bCZ에게 도전장을 내밀었다.",
    3217: "덴분 24년(1555년),\n두 지략가의 대결은 두뇌전으로 막을 올렸다.",
    3218: "\x1bCA모토나리\x1bCZ는 신성한 땅 \x1bCC이쓰쿠시마\x1bCZ에 미끼가 될 성을 쌓았다.\n전략적으로 아무런 의미도 없이,\n오직 \x1bCB오우치\x1bCZ군을 끌어들이기 위한 성이었다.",
    3219: "의심은 마음속에 귀신을 낳는 법……",
    3220: "\x1bCA모토나리\x1bCZ만 한 지략가가 쓸모없는 성을 지을 리 없다.\n그 선입견 때문에 \x1bCA하루카타\x1bCZ는 대군을 이끌고\n\x1bCC미야오성\x1bCZ으로 향했다.",
    3221: "바로 내가 바라던 바다!\n\x1bCA하루카타\x1bCZ가 진을 쳤다는 소식을 듣자 \x1bCA모토나리\x1bCZ는 폭풍우 치는 밤,\n적은 병력으로 몰래 \x1bCC이쓰쿠시마\x1bCZ를 향해 출항했다.",
    3222: "어둠을 틈탄다 해도\n폭풍 속의 출항은 자살행위였다.\n하지만 \x1bCA모토나리\x1bCZ는 바로 오늘이 길일이라고 호언했다.",
    3223: "다음 날 아침, 미야오성을 포위하던 군대는\n배후에서 들이닥친 적의 기습에 잠을 깼다.",
    3224: "어째서 \x1bCB모리군\x1bCZ이 여기에!\n설마 어젯밤 폭풍을 뚫고 온 것인가?",
    3225: "기습당한 \x1bCB오우치 가문\x1bCZ의 대군은 좁은 섬에서\n옴짝달싹하지 못한 채 완전히 통제를 잃었다.",
    3226: "간신히 전장을 벗어난 \x1bCA하루카타\x1bCZ는\n바닷길로 퇴각하려 항구로 달려갔다.",
    3227: "그러나 그가 목격한 것은 아군의 군선이\n\x1bCA모토나리\x1bCZ가 배치한 수군에게\n모조리 먹잇감이 되는 광경이었다.",
    3228: "일대의 효웅 \x1bCA스에 하루카타\x1bCZ는\n절망 속에서 스스로 생을 마감했다.",
    3229: "\x1bCA오우치\x1bCZ에서 \x1bCA모리\x1bCZ로……\n\x1bCC주고쿠\x1bCZ의 패자가 교체되는 순간이었다.",
    3230: "겐키 원년.\n\x1bCA오다 노부나가\x1bCZ는 쇼군 \x1bCA아시카가 요시아키\x1bCZ의 대리로서\n\x1bCC와카사\x1bCZ의 내분을 평정하고자 출진했다.",
    3231: "하지만 그것은 구실에 지나지 않았다. 진짜 목적은\n이웃 나라 \x1bCC에치젠\x1bCZ에 웅거하며 \x1bCA요시아키\x1bCZ·\x1bCA노부나가\x1bCZ에 반항하는\n\x1bCA아사쿠라 요시카게\x1bCZ를 견제하는 데 있었다.",
    3232: "\x1bCC쓰루가\x1bCZ에 들어선 \x1bCB오다\x1bCZ군이 \x1bCC가네가사키성\x1bCZ을 함락하고\n이제 막 \x1bCC기노메 고개\x1bCZ를 넘으려던 찰나,\n수수께끼의 위문품이 도착했다.",
    3233: "양 끝을 끈으로 묶은 자루…… 그 안에는 팥이\n가득 들어 있었다. 보낸 이는 \x1bCC고호쿠\x1bCZ의 다이묘\n\x1bCA아자이 나가마사\x1bCZ에게 시집간 여동생 \x1bCA오이치\x1bCZ였다.",
    3234: "이 자루가 무엇을 뜻하는지\n막료들은 골머리를 앓았다.\n수수께끼를 푼 이는 \x1bCA기노시타 도키치로 히데요시\x1bCZ였다.",
    3235: "팥은 우리, 양 끝을 묶은 끈은\n\x1bCB아사쿠라\x1bCZ와 \x1bCB아자이\x1bCZ……",
    3236: "즉 배후의 \x1bCA아자이 나가마사\x1bCZ가 적으로 돌아서\n\x1bCC오다\x1bCZ군을 앞뒤에서\n협공한다는 암시가 틀림없었다.",
    3237: "아니, 적으로 돌아섰다는 표현은 정확하지 않다.\n원래 \x1bCC아자이 가문\x1bCZ은 \x1bCC아사쿠라 가문\x1bCZ과 오랜 동맹이었다.",
    3238: "그 사이에 \x1bCA노부나가\x1bCZ가 끼어들어 아끼는 여동생을 아내로 보냈다.",
    3239: "부부의 금슬은 좋았고, \x1bCA노부나가\x1bCZ 또한\n순박한 매제를 아꼈다. 그런 \x1bCA나가마사\x1bCZ가\n하필 지금 등을 돌린 것이다.",
    3240: "\x1bCA나가마사\x1bCZ는 처남보다 오랜 동맹을 택했을 뿐이다.\n하지만 \x1bCA오이치\x1bCZ는\n그 사이에 끼이고 말았다.",
    3241: "남편을 따르면 오라버니를 버려야 하고,\n오라버니에게 위기를 알리면 남편을 배신하게 된다.",
    3242: "고뇌 끝에 보낸 팥자루의 양 끝을 묶은 끈은\n오라버니와 남편이라는,\n\x1bCA오이치\x1bCZ를 옭아맨 질곡이기도 했다.",
    3243: "\x1bCA나가마사\x1bCZ의 역심이 사실이라면 한시도 지체할 수 없다.\n\x1bCA노부나가\x1bCZ는 \x1bCA히데요시\x1bCZ에게 후위를 맡기고\n전군에 즉시 철수하라고 명했다.",
    3244: "매제를 향한 원망은 뒤로 미룰 때였다.\n우선 이 절체절명의 사지를 벗어나\n\x1bCC교토\x1bCZ로 돌아가야 했다……",
    3245: "겐키 2년(1571년).\n\x1bCC교토\x1bCZ의 귀문 \x1bCC히에이산\x1bCZ을 전군으로 포위한\n\x1bCA노부나가\x1bCZ의 분노는 한계에 달했다.",
    3246: "누구나 칭송했다. \x1bCA전교대사\x1bCZ 이래의\n호국을 위한 대도량이자, 여러 종파의\n숭앙을 받는 불문의 중심이라고.",
    3247: "겉으로는 그랬을 것이다.\n하지만 실제로 엔랴쿠지는 예부터 신위를 등에 업고\n강소를 거듭하며 권익을 넓혀 왔다.",
    3248: "승병의 무력과 전국의 장원을 함께 거느린\n중세 최대급의 권문이었다.",
    3249: "그 권문이\n\x1bCA노부나가\x1bCZ에게 등을 돌린 \x1bCA아자이\x1bCZ·\x1bCA아사쿠라\x1bCZ 무리와\n손을 잡았으니 용서할 수 없었다.",
    3250: "쇼군의 보호자인 \x1bCA노부나가\x1bCZ에게 대드는 것은\n막부에 대한 반역과 다름없다.",
    3251: "무사의 질서를 따르려 하지 않는 그들은\n\x1bCA노부나가\x1bCZ가 그리는 천하의 설계도에\n필요 없는 존재였다.",
    3252: "하지만…… 여러 나라가 숭앙하는 절을 불태우면\n비난의 화살이 \x1bCA노부나가\x1bCZ에게 쏟아질 터였다.",
    3253: "가신들은 주군의 난폭한 처사를 간언했다.",
    3254: "과거 똑같이 근본중당에 불을 지른 쇼군\n\x1bCA아시카가 요시노리\x1bCZ와 간레이 \x1bCA호소카와 마사모토\x1bCZ도\n모두 비명횡사했다…… 부처의 벌을 피할 수 없다고.",
    3255: "그러나 신불을 두려워하지 않는 \x1bCA노부나가\x1bCZ는 들으려 하지 않았다.\n저것을 절이 아니라 성이라 생각하라!",
    3256: "뜻밖에도 홀로 과감히 주명을 받든 이는\n옛 권위를 누구보다 중시하는 \x1bCA아케치 미쓰히데\x1bCZ였다.",
    3257: "주군을 귀신이라 불리게 하느니 내가 귀신이 되리라.\n각오를 품은 \x1bCA미쓰히데\x1bCZ는 산문에 불을 질렀다.",
    3258: "산 위의 가람은 홍련에 휩싸였고,\n달아나던 승려와 속인도 포위군에게 베였다.",
    3259: "아비규환의 지옥도도 \x1bCA노부나가\x1bCZ에게는\n중세라는 유물과의 결별에 지나지 않았다.",
    3260: "얄궂게도 이 공으로 \x1bCA미쓰히데\x1bCZ는\n\x1bCA노부나가\x1bCZ의 가신 중 처음으로 성주가 되어,\n불탄 터인 \x1bCC사카모토\x1bCZ에 성을 쌓도록 허락받았다……",
    3261: "\x1bCA신겐\x1bCZ, 상경……\n이보다 \x1bCA노부나가\x1bCZ의 간담을 서늘하게 한 소식은 없었다.",
    3262: "겐키 3년(1572년). 쇼군 \x1bCA요시아키\x1bCZ까지 가담한\n반\x1bCB오다\x1bCZ 연합에서 가장 강하고도 성가신 남자……\n\x1bCC가이\x1bCZ의 노련한 영웅이 마침내 움직였다.",
    3263: "상경로인 \x1bCC도토미\x1bCZ·\x1bCC미카와\x1bCZ를 다스리는 이는\n\x1bCA노부나가\x1bCZ의 둘도 없는 맹우를 자처하는 \x1bCA도쿠가와 이에야스\x1bCZ였다.",
    3264: "\x1bCA이에야스\x1bCZ는 그 사명과 책무에 분기해,\n서쪽으로 가는 \x1bCB다케다\x1bCZ군을 순순히 통과시키지 않겠다고 다짐했다.",
    3265: "하지만 그런 \x1bCA이에야스\x1bCZ의 기세를 비웃듯\n\x1bCA신겐\x1bCZ은 \x1bCC엔슈\x1bCZ 북부의 \x1bCC후타마타성\x1bCZ을 함락하고는",
    3266: "\x1bCA이에야스\x1bCZ가 틀어박힌 \x1bCC하마마쓰성\x1bCZ은 거들떠보지도 않고\n군을 서쪽으로 돌려 \x1bCC미카와\x1bCZ 방면으로 나아갔다.",
    3267: "마치 \x1bCA신겐\x1bCZ의 눈에는 \x1bCA노부나가\x1bCZ만 있을 뿐,\n\x1bCA이에야스\x1bCZ 따위는 존재하지도 않는 듯했다……",
    3268: "서른을 갓 넘겨\n아직 젊은 혈기가 남은 \x1bCA이에야스\x1bCZ는\n자신을 무시하는 진군에 격분했다.",
    3269: "\x1bCB다케다\x1bCZ에게 \x1bCC미카와\x1bCZ 무사의 오기를 보여 주리라!",
    3270: "말없는 도발에 이끌려 가신들의 간언도 듣지 않고\n용맹하게 추격전을 벌인 \x1bCA이에야스\x1bCZ는\n\x1bCC미카타가하라\x1bCZ에서 적군을 따라잡았다.",
    3271: "하지만 싸움을 걸자마자\n백전노장 \x1bCA신겐\x1bCZ의 병법에 농락당했다.",
    3272: "불과 한 시각 만에\n수천 병력이 괴멸한 압도적인 패배.\n망연할 틈도 없이 \x1bCA이에야스\x1bCZ는 사지에 빠졌다.",
    3273: "주군을 구하려 여러 충신이 '내가 \x1bCA이에야스\x1bCZ다'라고 외치며\n\x1bCA이에야스\x1bCZ 대신 목숨을 잃었다.",
    3274: "그 틈을 타 낙담한 주군을\n필사적으로 \x1bCC하마마쓰성\x1bCZ까지 피신시킨 심복들 덕분에\n\x1bCA이에야스\x1bCZ는 목숨을 건졌다.",
    3275: "\x1bCA이에야스\x1bCZ는 이 싸움에서 겪은\n\x1bCA신겐\x1bCZ을 향한 공포와 경의…… 자신의 경솔함……\n그리고 가신들의 충절을……",
    3276: "평생 잊지 않고\n적에게 배우며 자신을 경계했다고 한다.",
}

TRANSLATIONS = {**LABEL_TRANSLATIONS, **NARRATION_TRANSLATIONS}
DUMMY_IDS = frozenset(set(range(3105, 3116)) | set(range(3118, 3201)))
ACTOR_REFERENCE_IDS = frozenset({3116})
EMPTY_SLOT_IDS = frozenset({3201})
DEFERRED_GROUP_IDS = {
    "dummy_placeholder": DUMMY_IDS,
    "actor_reference": ACTOR_REFERENCE_IDS,
    "empty_slot": EMPTY_SLOT_IDS,
}
DEFERRED_GROUP_PINS = {
    "dummy_placeholder": {
        "count": 94,
        "ids_sha256": "E0DC069741079E4E6B7E20C2DBCAF993FF2E399C78D5B609CA527FFD20C38E06",
        "ordered_reference_hashes_sha256": "92294D393ADE01EF40D12EEFE3BCB0F0F686C8803150F706C3027D55C0AC1BC8",
    },
    "actor_reference": {
        "count": 1,
        "ids_sha256": "3A64813075A425CE11D35A881A3194FFB9078639058FEDF2E1DB93ECE6E8C902",
        "ordered_reference_hashes_sha256": "F614574998A9328E6B9A6BF7DC760C296C1DA25CBA9221766BC8201401CA13DC",
    },
    "empty_slot": {
        "count": 1,
        "ids_sha256": "B7EBFC2CA74F5D50D45C0E79DD925AEE93A3AB660E8696848AA8733553072402",
        "ordered_reference_hashes_sha256": "FA33EA0904E6D842F16C84C86DB90F69C2158C45990717E771FB4F1A52F54A07",
    },
}
PREVIOUS_DEFERRED_IDS = frozenset(
    {2953, 2954, 2955, 2959, 2960, 2964, 2965, 2967}
    | set(range(2972, 2998))
    | {2998, 2999}
    | set(range(3000, 3007))
)
UNCERTAIN_READING_IDS = frozenset({3082, 3083, 3089, 3090, 3094, 3117})
CLASS_COUNTS = {
    "generic_speaker_label": 1,
    "historical_event_narration": 75,
    "named_character_label": 97,
    "place_label": 1,
}
REPEATED_SOURCE_ID_GROUPS = (
    (3014, 3073),
    (3027, 3061),
    (3029, 3058),
    (3034, 3060),
    (3035, 3070),
    (3038, 3057),
    (3041, 3066),
    (3049, 3067),
)


def classify(entry_id: int) -> str:
    if entry_id in NARRATION_TRANSLATIONS:
        return "historical_event_narration"
    if entry_id == 3048:
        return "place_label"
    if entry_id == 3074:
        return "generic_speaker_label"
    return "named_character_label"


def generated_file_map(root: Path) -> dict[str, bytes]:
    paths = (
        Path("public") / OVERLAY_NAME,
        Path("evidence") / EVIDENCE_NAME,
        Path("review") / REVIEW_NAME,
        Path(VALIDATION_NAME),
    )
    return {path.as_posix(): (root / path).read_bytes() for path in paths}


def deferred_metadata() -> list[dict[str, Any]]:
    reasons = {
        "dummy_placeholder": "dummy_placeholder_not_display_text",
        "actor_reference": "runtime_actor_reference_not_display_text",
        "empty_slot": "empty_string_slot_not_display_text",
    }
    return [
        {
            "classification": classification,
            "status": "deferred",
            "reason": reasons[classification],
            "ids": sorted(DEFERRED_GROUP_IDS[classification]),
            **DEFERRED_GROUP_PINS[classification],
            "excluded_from_overlay_and_translation_progress": True,
        }
        for classification in (
            "dummy_placeholder",
            "actor_reference",
            "empty_slot",
        )
    ]


def previous_deferred_overlap_metadata(deferred_ids: list[int]) -> dict[str, Any]:
    overlap_ids = sorted(set(deferred_ids) & PREVIOUS_DEFERRED_IDS)
    return {
        "previous_batch_id": "ev-strdata-character-speaker-labels-2780-2971-v0.15",
        "previous_deferred_entry_count": 43,
        "previous_deferred_ids_sha256": PREVIOUS_DEFERRED_IDS_SHA256,
        "current_deferred_entry_count": DEFERRED_COUNT,
        "overlap_entry_count": len(overlap_ids),
        "overlap_ids_sha256": shared.hash_json(overlap_ids),
        "overlap_detected": bool(overlap_ids),
    }


def validate_batch_sources(loaded: dict[str, dict[str, Any]]) -> list[int]:
    ids = sorted(TRANSLATIONS)
    inspected_ids = list(range(INSPECTED_START, INSPECTED_END + 1))
    deferred_ids = sorted(
        entry_id
        for group in DEFERRED_GROUP_IDS.values()
        for entry_id in group
    )
    if len(ids) != TRANSLATED_COUNT or len(LABEL_TRANSLATIONS) != LABEL_COUNT:
        raise shared.EvStrDataError("v0.16 translated/label counts changed")
    if len(NARRATION_TRANSLATIONS) != NARRATION_COUNT:
        raise shared.EvStrDataError("v0.16 narration count changed")
    if ids[0] != SCOPE_START or ids[-1] != SCOPE_END:
        raise shared.EvStrDataError("v0.16 translated id boundary changed")
    if set(ids) & set(deferred_ids):
        raise shared.EvStrDataError("v0.16 translated and deferred ids overlap")
    if sorted(ids + deferred_ids) != inspected_ids:
        raise shared.EvStrDataError("v0.16 inspected partition changed")
    if len(inspected_ids) != INSPECTED_COUNT or len(deferred_ids) != DEFERRED_COUNT:
        raise shared.EvStrDataError("v0.16 inspected/deferred counts changed")
    if shared.hash_json(ids) != TRANSLATED_IDS_SHA256:
        raise shared.EvStrDataError("v0.16 translated id digest changed")
    if shared.hash_json(inspected_ids) != INSPECTED_IDS_SHA256:
        raise shared.EvStrDataError("v0.16 inspected id digest changed")
    if shared.hash_json(deferred_ids) != DEFERRED_IDS_SHA256:
        raise shared.EvStrDataError("v0.16 deferred id digest changed")
    if shared.hash_json([[entry_id, TRANSLATIONS[entry_id]] for entry_id in ids]) != TRANSLATION_MAP_SHA256:
        raise shared.EvStrDataError("v0.16 Korean translation map changed")
    if shared.hash_json(sorted(PREVIOUS_DEFERRED_IDS)) != PREVIOUS_DEFERRED_IDS_SHA256:
        raise shared.EvStrDataError("v0.15 deferred id digest changed")
    overlap = sorted(set(deferred_ids) & PREVIOUS_DEFERRED_IDS)
    if overlap or shared.hash_json(overlap) != EMPTY_IDS_SHA256:
        raise shared.EvStrDataError("v0.16 deferred ids overlap v0.15 exclusions")

    class_counts = Counter(classify(entry_id) for entry_id in ids)
    if dict(sorted(class_counts.items())) != CLASS_COUNTS:
        raise shared.EvStrDataError("v0.16 functional classification counts changed")

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
    if repeated_groups != REPEATED_SOURCE_ID_GROUPS or len(ids_by_source_hash) != 166:
        raise shared.EvStrDataError("v0.16 repeated-source groups changed")
    if shared.hash_json(source_sc_hashes) != SOURCE_SC_HASHES_SHA256:
        raise shared.EvStrDataError("v0.16 ordered SC source hashes changed")
    if shared.hash_json(all_reference_hashes) != ALL_REFERENCE_HASHES_SHA256:
        raise shared.EvStrDataError("v0.16 ordered SC/JP/TC source hashes changed")

    for classification, group in DEFERRED_GROUP_IDS.items():
        ordered_ids = sorted(group)
        pin = DEFERRED_GROUP_PINS[classification]
        reference_hashes = [
            common.text_hash(loaded[language]["table"].texts[entry_id])
            for entry_id in ordered_ids
            for language in shared.LANGUAGES
        ]
        if len(ordered_ids) != pin["count"]:
            raise shared.EvStrDataError(f"v0.16 {classification} count changed")
        if shared.hash_json(ordered_ids) != pin["ids_sha256"]:
            raise shared.EvStrDataError(f"v0.16 {classification} id digest changed")
        if shared.hash_json(reference_hashes) != pin["ordered_reference_hashes_sha256"]:
            raise shared.EvStrDataError(f"v0.16 {classification} source hashes changed")
    for language in shared.LANGUAGES:
        if loaded[language]["table"].texts[3201] != "":
            raise shared.EvStrDataError(f"v0.16 empty-slot structure changed for {language}")
        if common.text_hash(loaded[language]["table"].texts[NEXT_DISPLAY_ID]) != NEXT_DISPLAY_REFERENCE_HASHES[language]:
            raise shared.EvStrDataError(f"v0.16 next display anchor changed for {language}")
    return ids


def build_once(game_root: Path, out_root: Path) -> dict[str, Any]:
    loaded, before = shared.load_sources(game_root)
    ids = validate_batch_sources(loaded)
    deferred_ids = sorted(
        entry_id
        for group in DEFERRED_GROUP_IDS.values()
        for entry_id in group
    )

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
        "entry_count": len(ids),
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
        3047,
        3048,
        3073,
        3074,
        3104,
        3105,
        3116,
        3117,
        3118,
        3200,
        3201,
        3202,
        3214,
        3215,
        3229,
        3230,
        3244,
        3245,
        3260,
        3261,
        SCOPE_END,
        NEXT_DISPLAY_ID,
    )
    deferred = deferred_metadata()
    overlap = previous_deferred_overlap_metadata(deferred_ids)
    evidence = {
        "schema": "nobu16.kr.ev-strdata-alignment-evidence.v16",
        "batch_id": BATCH_ID,
        "resource": "ev_strdata",
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "translated_display_entry_count": TRANSLATED_COUNT,
            "translated_label_count": LABEL_COUNT,
            "translated_narration_count": NARRATION_COUNT,
            "inspected_entry_count": INSPECTED_COUNT,
            "deferred_internal_entry_count": DEFERRED_COUNT,
            "next_display_id": NEXT_DISPLAY_ID,
            "functional_section": "character_alias_labels_and_historical_event_narration",
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
            "dummy_actor_reference_and_empty_slot_classification",
            "v015_deferred_overlap_check",
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
        "schema": "nobu16.kr.ev-strdata-review-index.v16",
        "batch_id": BATCH_ID,
        "quality_state": "labels_and_historical_narration_draft_pending_runtime_review",
        "entry_count": TRANSLATED_COUNT,
        "uncertain_reading_count": len(UNCERTAIN_READING_IDS),
        "entries": [
            {
                "id": entry_id,
                "status": "translated",
                "classification": classify(entry_id),
                "translation_origin": "manual_sc_jp_tc_aligned_review",
                "human_review_required": True,
                "runtime_reviewed": False,
                "uncertainty_flags": (
                    ["rare_person_or_alias_reading"]
                    if entry_id in UNCERTAIN_READING_IDS
                    else []
                )
                + (
                    ["historical_narration_runtime_layout"]
                    if entry_id in NARRATION_TRANSLATIONS
                    else []
                ),
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
            "v0.16 public artifact contains source script text or an embedded NUL"
        )

    binary = shared.common_binary_build(game_root, overlay_path)
    after = {
        relative: shared.sha256((game_root / Path(relative)).read_bytes())
        for relative in before
    }
    if before != after:
        raise shared.EvStrDataError("installed game resource changed during v0.16 build")

    artifacts = {
        path.relative_to(out_root).as_posix(): {
            "size": path.stat().st_size,
            "sha256": shared.sha256(path.read_bytes()),
        }
        for path in (overlay_path, evidence_path, review_path)
    }
    validation = {
        "schema": "nobu16.kr.ev-strdata-generation-validation.v16",
        "batch_id": BATCH_ID,
        "passed": True,
        "scope": {
            "start_id": SCOPE_START,
            "end_id": SCOPE_END,
            "translated_display_entry_count": TRANSLATED_COUNT,
            "translated_label_count": LABEL_COUNT,
            "translated_narration_count": NARRATION_COUNT,
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
            "uncertain_reading_review_flag_count": len(UNCERTAIN_READING_IDS),
            "narration_runtime_layout_review_flag_count": NARRATION_COUNT,
            "source_text_embedded": False,
        },
        "repeated_source_policy": {
            "same_source_same_translation_required": True,
            "translated_unique_source_hash_count": 166,
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
            "existing_v01_through_v015_artifacts_modified": False,
        },
    }
    validation_path = out_root / VALIDATION_NAME
    validation_path.parent.mkdir(parents=True, exist_ok=True)
    validation_path.write_bytes(shared.encode_json(validation))
    if shared.source_free_counts(validation_path.read_bytes()) != {
        "han_or_kana_count": 0,
        "embedded_nul_count": 0,
    }:
        raise shared.EvStrDataError("v0.16 validation is not source-free")
    return {
        "entry_count": TRANSLATED_COUNT,
        "label_count": LABEL_COUNT,
        "narration_count": NARRATION_COUNT,
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
    with tempfile.TemporaryDirectory(prefix="nobu16-evstr16-a-") as first_tmp:
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr16-b-") as second_tmp:
            first = build_once(game_root, Path(first_tmp))
            second = build_once(game_root, Path(second_tmp))
            if first["files"] != second["files"]:
                raise shared.EvStrDataError(
                    "isolated A/B v0.16 public artifacts are not byte-identical"
                )
    final = build_once(game_root, out_root)
    if final["files"] != first["files"]:
        raise shared.EvStrDataError(
            "final v0.16 public artifacts differ from isolated A/B output"
        )
    after = {path.as_posix(): shared.sha256(path.read_bytes()) for path in source_paths}
    if before != after:
        raise shared.EvStrDataError("installed game resource changed across v0.16 build")
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
    print(f"labels={result['label_count']}")
    print(f"narration={result['narration_count']}")
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
