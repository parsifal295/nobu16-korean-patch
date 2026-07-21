#!/usr/bin/env python3
"""Create a source-backed, read-only review for 3900-series compact events.

This workstream records semantic restoration text and Static Patch 007 layout
evidence only.  It deliberately does not build a message binary, touch the
Steam installation, invoke Git, publish a release, or contact the network.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import math
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
PUBLIC = WORKSTREAM / "public"
OUTPUT = PUBLIC / "manual_compact_3900_review.v1.json"
VALIDATION = WORKSTREAM / "validation.v1.json"

TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.manual-compact-3900-review.v1"
RESOURCE = "MSG_PK/JP/msgev.bin"
MIN_ID = 3900
MAX_ID = 3999
EXPECTED_TARGET_IDS = (
    3901,
    3913,
    3914,
    3916,
    3918,
    3920,
    3928,
    3930,
    3933,
    3940,
    3943,
    3946,
    3948,
    3953,
    3954,
    3956,
    3957,
    3962,
    3963,
    3967,
    3968,
    3969,
    3970,
    3973,
    3981,
    3982,
    3986,
    3988,
    3989,
    3990,
    3994,
    3996,
)
EXPECTED_CURRENT_DIFF_IDS = (3953, 3954, 3956, 3957, 3986)

# Static Patch 007 authority.  The raw G1N values are converted to the 30px
# runtime layout; the obsolete raw-912px gate is never used here.
RUNTIME_FONT_PX = 30
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
MAX_EFFECTIVE_WIDTH_PX = 912
MAX_RAW_WIDTH_PX = 1440
MAX_LINES = 4

CURRENT_PATH = (
    REPO
    / "tmp"
    / "pc_event_manual_compact_static007_6000_7999_restore_v1"
    / "candidate-final"
    / "MSG_PK"
    / "JP"
    / "msgev.bin"
)
CURRENT_EXPECTED = {
    "packed_sha256": "D99390D4F2D7D469C105439A11476B01830F5E96287B278C164045CBC7BA3547",
    "raw_sha256": "567C8C3C2F371E27CBE6FFEAB9F8F3EE7F6D6F13A2C179682A5A7F7D3F35780F",
    "string_count": 17916,
}
DIRECT_JP_PATH = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
    r"\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals"
    r"\MSG_PK\JP\msgev.bin"
)
DIRECT_EN_PATH = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\EN\msgev.bin")
DIRECT_SC_PATH = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\SC\msgev.bin")
DIRECT_TC_PATH = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\TC\msgev.bin")
LEGACY_KO_PATH = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
    r"\file_only_transaction\steam-jp-v0.10.0-original-font-rollback-v1"
    r"\originals\MSG_PK\JP\msgev.bin"
)
HISTORICAL_MANIFEST = (
    REPO
    / "workstreams"
    / "steam_jp_msgev_full_layout_v2"
    / "public"
    / "msgev_ko_steam_jp_full_layout.v2.json"
)
RESERVATION_MANIFEST = (
    REPO
    / "workstreams"
    / "steam_jp_msgev_full_layout_v2"
    / "public"
    / "runtime_token_reservations.v1.json"
)
INVENTORY_MANIFEST = (
    REPO
    / "workstreams"
    / "pc_event_manual_compact_korean_layout_inventory_v1"
    / "public"
    / "msgev_manual_compact_korean_layout_inventory.v1.json"
)

DIRECT_EXPECTED = {
    "jp": {
        "packed_sha256": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
        "raw_sha256": "07D7512BE0235753FC7BB0C7C548B61F471D9CDED01379E63B8AF8EAE013813E",
        "string_count": 17916,
    },
    "en": {
        "packed_sha256": "BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E",
        "raw_sha256": "6A1F3891412EBFF5AC3188F498C9951431154192D69E82B7ABB6F25AA934D911",
        "string_count": 17916,
    },
    "sc": {
        "packed_sha256": "7C443515D8B42DD5D1A516FE606DB8880F21296F7BEF0C5D067FEA7D9FC991BA",
        "raw_sha256": "3ACE267E6B9774D8C940C9D7940F168B61744ADDF7C082F2CB1EA7E9BBD82B5E",
        "string_count": 17916,
    },
    "tc": {
        "packed_sha256": "89D183BA95C3BB83B52A5EE408664D5247C695A1DB192105A5D906737E6F78B6",
        "raw_sha256": "42DC893AA9FF9D3E7B75FBCFFBEFD7C3DFC338CAB71E942C081BDC52C9024BF6",
        "string_count": 17916,
    },
    "legacy": {
        "packed_sha256": "2CA183DA690D45A75702EA0F35C70966786B59E9440B8B8F49BE9652342F81AC",
        "raw_sha256": "EDCF7A9CEBD605BB2275D5A3B92A76E7E2F652B2391554F24C6A8BDD2EF91A08",
        "string_count": 17916,
    },
}

ESC = "\x1b"
ESC_RE = re.compile(r"\x1bC[ABCZ]")
RUNTIME_RE = re.compile(r"\[[A-Za-z]{1,16}\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+ #0]*\d*(?:\.\d+)?[A-Za-z]")
LINEBREAK_RE = re.compile(r"\r\n|\r|\n")


def ca(value: str) -> str:
    return f"{ESC}CA{value}{ESC}CZ"


def cb(value: str) -> str:
    return f"{ESC}CB{value}{ESC}CZ"


def cc(value: str) -> str:
    return f"{ESC}CC{value}{ESC}CZ"


# Every selected row is explicit.  None of these values is generated by an
# LF-strip or a legacy-file bulk replacement.  The reasons reference direct
# PC JP/EN/SC/TC as semantic witnesses; JP source line breaks are not copied.
PROPOSALS: Mapping[int, Mapping[str, str]] = {
    3901: {
        "strategy": "restore_unabridged_legacy_korean",
        "reason": "Restore the hot-spring treatment pretext, the absence of suspicion, and the separate hidden aim.",
        "text": (
            f"그런 {ca('[bm473]')} 공이 온천 요양을 떠난다고 해도,\n"
            "수상하게 여길 사람은 없었다.\n"
            f"하지만 {ca('[bm473]')} 공의 노림수는 따로 있었다."
        ),
    },
    3913: {
        "strategy": "source_complete_retranslation_and_semantic_reflow",
        "reason": "Restore the father relation and specify that the intended successor was the child born to the concubine, not merely a generic concubine's child.",
        "text": (
            f"{ca('[bm473]')} 공의 아버지 {ca('오토모 요시아키')}는 평소부터\n"
            f"{ca('[bm473]')} 공을 싫어해,\n"
            "측실과의 사이에서 태어난 아들에게\n"
            f"{cb('오토모 가문')}을 잇게 하려 했다."
        ),
    },
    3914: {
        "strategy": "source_complete_retranslation_and_semantic_reflow",
        "reason": "Restore discovery of the plot, the hot-spring pretext, the manufactured opening, the coup, and the counter-killing without keeping the compressed syntax.",
        "text": (
            f"{ca('[bm473]')} 공은 이를 알아차리고 온천 요양을 구실로\n"
            f"틈을 만들어 정변을 유도한 뒤, 거사를 일으킨 {ca('요시아키')}를\n"
            "수하를 시켜 도리어 죽였다."
        ),
    },
    3916: {
        "strategy": "source_complete_retranslation_and_semantic_reflow",
        "reason": "Restore overcoming the father by force, the clan headship, the able retainers, and the gradual domination of Kyushu.",
        "text": (
            f"힘으로 아버지를 제압한 {ca('[bm473]')} 공은 {cb('오토모 가문')}의\n"
            f"당주가 되어 {ca('[b1730]')} 등 뛰어난 무장을 거느리고,\n"
            f"마침내 {cc('규슈')}를 석권해 갔다……"
        ),
    },
    3918: {
        "strategy": "restore_unabridged_legacy_korean",
        "reason": "Restore the two-clan split, the weakened power after successive young-head deaths, and Motonari's recognition of the opportunity.",
        "text": (
            f"{cb('누타')}와 {cb('다케하라')} 두 가문으로 갈라진 뒤,\n"
            "젊은 당주들이 잇달아 죽으며 세력이 쇠했다.\n"
            f"{ca('모리 모토나리')}는 이를 기회로 보았다."
        ),
    },
    3920: {
        "strategy": "restore_unabridged_legacy_korean",
        "reason": "Restore Yoshitaka's backing, Takakage as Motonari's third son, the surname change, and the Takehara Kobayakawa headship.",
        "text": (
            f"{ca('요시타카')}의 강력한 후원을 받아,\n"
            f"{ca('모토나리')}의 셋째 아들 {ca('다카카게')}가 성을 바꾸고\n"
            f"{cb('다케하라 고바야카와 가문')}의 당주가 되었다."
        ),
    },
    3928: {
        "strategy": "source_complete_retranslation_and_semantic_reflow",
        "reason": "Restore the timing, the marriage to the Numata Kobayakawa daughter, unification of both houses, and the naval power obtained for Mori.",
        "text": (
            f"얼마 뒤 {ca('다카카게')}는 {cb('누타 고바야카와 가문')}의 딸을 아내로 맞아,\n"
            f"{cb('두 고바야카와 가문')}을 통일하고,\n"
            f"{cb('모리 가문')}을 지탱할 수군력을 손에 넣었다."
        ),
    },
    3930: {
        "strategy": "restore_unabridged_legacy_korean",
        "reason": "Restore the years since the full-scale invasion began and the ongoing gradual encroachment on Shinano.",
        "text": (
            f"{cc('가이')}의 전국 다이묘 {ca('[b1251]')} 공이\n"
            "본격적으로 침공을 시작한 지 몇 해,\n"
            f"{cc('시나노')}는 차츰 {cb('다케다 가문')}에 잠식되고 있었다……"
        ),
    },
    3933: {
        "strategy": "restore_unabridged_legacy_korean",
        "reason": "Restore the earlier Uedahara victory and the especially strong anti-Takeda resolve among the Shinano group.",
        "text": (
            f"{ca('요시키요')}는 일찍이 {cc('우에다하라')} 땅에서\n"
            f"{ca('[bm1251]')}의 군을 무찌른 바 있어, {cb('시나노 무리')} 중에서도\n"
            f"{ca('[bm1251]')}에 대한 대항 의식이 한층 강했다."
        ),
    },
    3940: {
        "strategy": "restore_unabridged_legacy_korean",
        "reason": "Restore the tenfold-force contrast, the failure to take Toishi Castle, and the ruler's mounting impatience.",
        "text": (
            f"하지만 성병보다 열 배 많은 {cb('다케다군')}도\n"
            f"{cc('도이시성')}을 좀처럼 함락하지 못했다.\n"
            f"{ca('[bm1251]')} 공의 초조함은 커져만 갔다……"
        ),
    },
    3943: {
        "strategy": "restore_unabridged_legacy_korean",
        "reason": "Restore the early arrival, the two-sided attack with Toishi soldiers, the chaos, and the forced retreat.",
        "text": (
            f"예상보다 빨리 도착한 {ca('무라카미 요시키요')}와\n"
            f"{cc('도이시성')}의 병사에게 협격당한 {cb('다케다군')}은\n"
            "대혼란에 빠져 철수를 피할 수 없었다."
        ),
    },
    3946: {
        "strategy": "restore_unabridged_legacy_korean",
        "reason": "Restore the Oe lineage, the clan description, and its subordinate position until the middle Sengoku period.",
        "text": (
            f"{cb('아키 모리씨')}는 가마쿠라 막부 고케닌·{cb('오에씨')}의\n"
            "흐름을 잇는 일족이다. 전국 중기까지는\n"
            "주변 세력에 휘둘리는 존재에 지나지 않았다."
        ),
    },
    3948: {
        "strategy": "source_complete_retranslation_and_semantic_reflow",
        "reason": "Clarify that even as lord Mori had not gained enough supremacy to rule former equals by force.",
        "text": (
            f"가문 안에는 한때 {ca('모리')}와 동격이던 고쿠진도 있어,\n"
            f"주군인 {ca('모리')}조차 그들을 강권으로 다스릴 만큼\n"
            "우위를 굳히지 못했다."
        ),
    },
    3953: {
        "strategy": "reconcile_later_current_terminology_with_source_complete_restoration",
        "reason": "Use the established Inoue spelling while restoring the council summons and the public personal admonition.",
        "text": (
            "그 지경이면 더는 내버려 둘 수 없군……\n"
            f"우선 {ca('이노우에 모토카네')}를 평정 자리에 부르자.\n"
            "사람들 앞에서 내가 직접 타이르겠다."
        ),
    },
    3954: {
        "strategy": "reconcile_later_current_terminology_with_source_complete_restoration",
        "reason": "Restore Motonari's response to the Inoue faction and the refusal to attend the castle under evasive excuses.",
        "text": (
            f"눈에 거슬리는 {cb('이노우에당')}의 횡포를 막고자\n"
            f"{ca('모토나리')}는 {ca('이노우에 모토카네')}를 성으로 불러들였으나,\n"
            f"{ca('모토카네')}는 이런저런 핑계를 대며 등성을 거부했다…"
        ),
    },
    3956: {
        "strategy": "reconcile_later_current_terminology_with_source_complete_restoration",
        "reason": "Retain the established Inoue spelling and restore the secret assassin, the raid, and the purge of more than thirty members.",
        "text": (
            f"{ca('모토나리')}는 몰래 자객을 보내 {ca('이노우에 모토카네')}를 암살했다.\n"
            f"이어 동요한 {cb('이노우에 일파')}의 저택을 급습해,\n"
            "일족 30여 명을 단숨에 숙청했다."
        ),
    },
    3957: {
        "strategy": "reconcile_later_current_terminology_with_source_complete_restoration",
        "reason": "Restore the family-wide document, all eleven listed charges, and the broad denunciation while retaining the established Inoue spelling.",
        "text": (
            f"그 뒤 {ca('모토나리')}는 가문에 문서를 반포해,\n"
            f"{cb('이노우에 일파')}의 죄목을 무려 11개나 열거하고,\n"
            "그들의 잘못을 대대적으로 알렸다."
        ),
    },
    3962: {
        "strategy": "restore_unabridged_legacy_korean",
        "reason": "Restore the Gassan-Toda defeat, loss of interest in administration, indulgence, and burdens imposed on the people.",
        "text": (
            f"갓산토다성 전투에서 대패한 {ca('오우치 요시타카')}는\n"
            "정무에 흥미를 잃고 유흥에 빠졌으며,\n"
            "백성에게도 무거운 부담을 지웠다……"
        ),
    },
    3963: {
        "strategy": "restore_unabridged_legacy_korean",
        "reason": "Restore the Saigoku greatest-daimyo status, the allowance for poetry and tea, and the admonition about martial duty.",
        "text": (
            f"주군, {cb('오우치 가문')}은 {cc('사이고쿠')} 제일의 대다이묘입니다.\n"
            "와카와 다회도 좋지만,\n"
            "무사의 본분은 무예임을 잊지 마십시오……"
        ),
    },
    3967: {
        "strategy": "source_complete_retranslation_and_semantic_reflow",
        "reason": "Restore the chief-retainer rank, the secret invitation, and Haruhide's precise relationship as Yoshitaka's nephew rather than the vague 'nephew-like' wording.",
        "text": (
            f"중신 필두인 {ca('스에 다카후사')}는 {cb('오우치 가문')}의 앞날에\n"
            f"위기감을 품고, 은밀히 {ca('요시타카')}의 조카인\n"
            f"{ca('하루히데')}를 {cb('오토모 가문')}에서 {cc('야마구치')}로 불러들이고 있었다…"
        ),
    },
    3968: {
        "strategy": "source_complete_retranslation_and_semantic_reflow",
        "reason": "Restore Haruhide's parentage, former adoption, the birth of Yoshitaka's biological child, and the return to the Otomo clan without using a five-line layout.",
        "text": (
            f"{ca('하루히데')}는 {ca('오토모 요시아키')}와\n"
            f"{ca('요시타카')}의 누이의 아들로, 한때 {ca('요시타카')}의\n"
            f"양자가 되었으나, {ca('요시타카')}에게 친아들이\n"
            f"태어나자 {cb('오토모 가문')}으로 돌아왔다."
        ),
    },
    3969: {
        "strategy": "source_complete_retranslation_and_semantic_reflow",
        "reason": "Restore the secret preparation of a successor, support from Motonari and others, and the step-by-step plan to overthrow the lord's house.",
        "text": (
            f"몰래 {ca('요시타카')}의 후계자를 마련한 {ca('다카후사')}는,\n"
            f"{cb('오우치 가문')}을 따르던 {ca('모리 모토나리')} 등의 지지도 얻어,\n"
            "주군 가문 전복 계획을 차근차근 다듬어 갔다……"
        ),
    },
    3970: {
        "strategy": "restore_unabridged_legacy_korean",
        "reason": "Restore the 'one day' lead-in, the uprising in Haruhide's name, the rapid pacification of castles, and the approach to Yamaguchi.",
        "text": (
            "그리고 어느 날……\n"
            f"마침내 {ca('다카후사')}는 {ca('하루히데')}를 받들어 거병했다.\n"
            f"순식간에 여러 성을 평정하고 {cc('야마구치')}로 다가갔다."
        ),
    },
    3973: {
        "strategy": "restore_unabridged_legacy_korean",
        "reason": "Restore the comparison with a pleasure-seeking lord, the speaker's own advice, and the claimed benefit to Ouchi.",
        "text": (
            f"적어도 유흥에만 빠진 {ca('요시타카')} 님보다는,\n"
            "제가 하는 말을 모두 받아들이는\n"
            f"{ca('하루히데')} 님이 {cb('오우치')}를 위해 더 낫겠지요……"
        ),
    },
    3981: {
        "strategy": "restore_unabridged_legacy_korean",
        "reason": "Restore Reizei Takatoyo's full name, the breakout from Sue's siege, the flight to Taineiji, and the renewed encirclement there.",
        "text": (
            f"측근인 {ca('레이제이 다카토요')}의 분전으로 {cb('스에군')}의 포위를\n"
            f"빠져나온 {ca('요시타카')}는 {cc('나가토')}의 {cc('다이네이지')}로 달아났으나\n"
            "다시 그 땅에서 포위당했다."
        ),
    },
    3982: {
        "strategy": "restore_unabridged_legacy_korean",
        "reason": "Restore the first-person resolve for seppuku, the request for kaishaku, and the end of the Ouchi clan history.",
        "text": (
            f"{ca('다카토요')}…… 이제 됐다. 여기까지다.\n"
            "나는 이곳에서 할복하겠다…… 가이샤쿠해 다오.\n"
            f"{cb('오우치 가문')}의 역사도 여기서 끝이다!"
        ),
    },
    3986: {
        "strategy": "reconcile_later_current_revision_with_source_complete_restoration",
        "reason": "The later current row has valid naming but remains abbreviated. Restore that Takafusa sought only a succession transfer, did not intend to take his lord's life, and was shaken by the suicide report.",
        "text": (
            f"{ca('다카후사')}는 {ca('요시타카')}에게 {ca('하루히데')}로\n"
            "가독을 넘기게 할 생각만 했고,\n"
            "주군의 목숨까지 빼앗을 생각은 없었기에\n"
            "자결 소식에 동요했다."
        ),
    },
    3988: {
        "strategy": "source_complete_retranslation_and_semantic_reflow",
        "reason": "Restore the new-lord relationship and both name changes: Takafusa receives a character from Haruhide, while Haruhide receives 'Yoshi' from the shogun.",
        "text": (
            f"{ca('다카후사')}는 새 주군 {ca('하루히데')}에게서 한 글자를 받아\n"
            f"{ca('하루카타')}로 이름을 고쳤고,\n"
            f"{ca('하루히데')}는 쇼군에게서 ‘요시’ 자를 받아\n"
            f"{ca('요시나가')}로 개명했다."
        ),
    },
    3989: {
        "strategy": "restore_unabridged_legacy_korean",
        "reason": "Restore the coercive methods, criticism over driving the former lord to death, and the gradual loss of support.",
        "text": (
            f"하지만 {ca('하루카타')}의 강압적인 방식은 마찰을 불렀고,\n"
            "옛 주군을 죽음으로 몰았다는 비판까지 겹쳐,\n"
            f"{ca('모리 모토나리')} 등의 지지를 잃어 갔다."
        ),
    },
    3990: {
        "strategy": "source_complete_retranslation_and_semantic_reflow",
        "reason": "Restore that events ran contrary to the renamed man's expectations and that Ouchi was drawn into an ever deeper vortex of unrest.",
        "text": (
            f"{ca('다카후사')}에서 {ca('하루카타')}로 이름을 고친 그의 뜻과는 달리,\n"
            f"{cb('오우치 가문')}은 이후 더 깊은 동란의 소용돌이에\n"
            "휘말려 갔다……"
        ),
    },
    3994: {
        "strategy": "source_complete_retranslation_and_semantic_reflow",
        "reason": "Replace the awkward literal 'on the palm' construction while restoring the manipulation, forced recognition of status, marriage, and rhetorical question.",
        "text": (
            f"형님과 {ca('[bm1448]')}를 손아귀에 넣고, 자신의 지위를\n"
            f"충분히 인정시킨 {ca('마사카게')} 님이 내 남편이 된다…\n"
            "유쾌하지 않습니까."
        ),
    },
    3996: {
        "strategy": "restore_unabridged_legacy_korean",
        "reason": "Restore the assurance that both the elder sister and future brother-in-law will never be treated carelessly, plus the request to marry in peace.",
        "text": (
            f"누님은 물론, 이제 매형이 될 {ca('마사카게')} 공도\n"
            f"{ca('[bm1448]')} 공이 결코 소홀히 대하지 않겠습니다.\n"
            "마음 편히 시집가 주십시오……"
        ),
    },
}


class ReviewError(RuntimeError):
    """Raised when an immutable review input or a reviewed output drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewError(message)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_digest(value: str) -> str:
    return digest(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def path_label(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO.resolve()).as_posix()
    except ValueError:
        return str(path)


def load_table(path: Path, expected: Mapping[str, Any], label: str) -> tuple[dict[str, Any], tuple[str, ...]]:
    require(path.is_file(), f"missing {label}: {path}")
    packed = path.read_bytes()
    _header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    require(rebuild_message_table(table, table.texts) == raw, f"{label}: table round-trip differs")
    profile = {
        "path": path_label(path),
        "packed_size": len(packed),
        "packed_sha256": digest(packed),
        "raw_size": len(raw),
        "raw_sha256": digest(raw),
        "string_count": len(table.texts),
    }
    for key, expected_value in expected.items():
        require(profile[key] == expected_value, f"{label}: {key} drift")
    return profile, tuple(table.texts)


def read_json(path: Path) -> Any:
    require(path.is_file(), f"missing JSON source: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_linebreaks(value: str) -> str:
    return LINEBREAK_RE.sub("\n", value)


def normalize_legacy_layout(value: str) -> str:
    return "\n".join(line.lstrip(" \u3000") for line in normalize_linebreaks(value).split("\n"))


def is_full_width_visible(character: str) -> bool:
    codepoint = ord(character)
    return (
        0x1100 <= codepoint <= 0x11FF
        or 0x3130 <= codepoint <= 0x318F
        or 0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xAC00 <= codepoint <= 0xD7AF
        or 0xF900 <= codepoint <= 0xFAFF
    )


def control_signature(value: str) -> dict[str, Any]:
    printf_matches = list(PRINTF_RE.finditer(value))
    printf_offsets = {match.start() for match in printf_matches}
    other_controls: list[str] = []
    pua: list[str] = []
    for offset, character in enumerate(value):
        if character in "\r\n" or character == ESC:
            continue
        if unicodedata.category(character) == "Cc":
            other_controls.append(f"U+{ord(character):04X}")
        if 0xE000 <= ord(character) <= 0xF8FF:
            pua.append(f"U+{ord(character):04X}")
    return {
        "esc_tags": ESC_RE.findall(value),
        "runtime_tokens": RUNTIME_RE.findall(value),
        "printf_tokens": [match.group(0) for match in printf_matches],
        "unknown_percent_count": sum(
            1 for offset, character in enumerate(value) if character == "%" and offset not in printf_offsets
        ),
        "other_c0_controls": other_controls,
        "pua_codepoints": pua,
        "terminator_nul_count": value.count("\x00"),
    }


def assert_colour_layout(value: str, entry_id: int) -> None:
    inside = False
    cursor = 0
    while cursor < len(value):
        if value[cursor] == ESC:
            tag = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(tag) is not None, f"{entry_id}: malformed ESC tag {tag!r}")
            if tag == f"{ESC}CZ":
                require(inside, f"{entry_id}: unpaired colour close")
                inside = False
            else:
                require(not inside, f"{entry_id}: nested colour span")
                inside = True
            cursor += 3
            continue
        require(not (inside and value[cursor] in "\r\n"), f"{entry_id}: LF inside colour tag")
        cursor += 1
    require(not inside, f"{entry_id}: unterminated colour span")


def visible_units(value: str) -> list[str]:
    visible = ESC_RE.sub("", value)
    return re.findall(r"\[[^\[\]\r\n]+\]|[\w]+|[^\s]", visible, flags=re.UNICODE)


def reintroduced_surface_units(before: str, after: str) -> list[str]:
    before_units = visible_units(before)
    after_units = visible_units(after)
    result: list[str] = []
    for opcode, _left_start, _left_end, right_start, right_end in difflib.SequenceMatcher(
        a=before_units, b=after_units, autojunk=False
    ).get_opcodes():
        if opcode in {"insert", "replace"}:
            for unit in after_units[right_start:right_end]:
                if unit not in result:
                    result.append(unit)
    return result


def display_name(names: Sequence[str], source_name_id: int) -> str:
    require(0 <= source_name_id < len(names), f"runtime name ID outside table: {source_name_id}")
    return ESC_RE.sub("", normalize_linebreaks(names[source_name_id])).replace("\n", " ")


def line_metrics(
    entry_id: int,
    target: str,
    names: Sequence[str],
    reservations: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    metrics: list[dict[str, Any]] = []
    for line_number, encoded_line in enumerate(normalize_linebreaks(target).split("\n"), 1):
        assert_colour_layout(encoded_line, entry_id)
        template = ESC_RE.sub("", encoded_line)
        runtime_items: list[dict[str, Any]] = []

        def replace_runtime(match: re.Match[str]) -> str:
            token = match.group(0)
            reservation = reservations.get(token)
            require(isinstance(reservation, Mapping), f"{entry_id}: reservation missing for {token}")
            source_name_id = reservation.get("source_name_id")
            raw_reserved = reservation.get("reserved_full_name_width_px")
            require(isinstance(source_name_id, int), f"{entry_id}: invalid source name ID for {token}")
            require(isinstance(raw_reserved, int), f"{entry_id}: invalid reservation width for {token}")
            shown = display_name(names, source_name_id)
            shown_full = sum(is_full_width_visible(character) for character in shown)
            runtime_items.append(
                {
                    "token": token,
                    "source_name_id": source_name_id,
                    "display_string": shown,
                    "display_full_width_character_count": shown_full,
                    "display_half_width_character_count": len(shown) - shown_full,
                    "reserved_raw_g1n_width_px": raw_reserved,
                    "reserved_effective_width_px": math.ceil(raw_reserved * RUNTIME_FONT_PX / RAW_FULL_WIDTH_PX),
                    "runtime_proven": False,
                    "reservation_reason": "Catalog full-name upper bound; raw reservation is scaled by 30/48 and is not a runtime-proven scene measurement.",
                }
            )
            return shown

        display = RUNTIME_RE.sub(replace_runtime, template)
        literal = RUNTIME_RE.sub("", template)
        literal_full = sum(is_full_width_visible(character) for character in literal)
        literal_half = len(literal) - literal_full
        raw_literal = literal_full * RAW_FULL_WIDTH_PX + literal_half * RAW_HALF_WIDTH_PX
        raw_reserved = sum(item["reserved_raw_g1n_width_px"] for item in runtime_items)
        raw_width = raw_literal + raw_reserved
        effective_width = math.ceil(raw_width * RUNTIME_FONT_PX / RAW_FULL_WIDTH_PX)
        display_full = sum(is_full_width_visible(character) for character in display)
        metrics.append(
            {
                "line_number": line_number,
                "encoded_string": encoded_line,
                "display_string": display,
                "raw_g1n_width_px": raw_width,
                "literal_raw_g1n_width_px": raw_literal,
                "reserved_raw_g1n_width_px": raw_reserved,
                "effective_width_px": effective_width,
                "full_width_character_count": display_full,
                "half_width_character_count": len(display) - display_full,
                "runtime_reservations": runtime_items,
                "exceeds_912px": effective_width > MAX_EFFECTIVE_WIDTH_PX,
            }
        )
    return metrics


def source_summary(profile: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: profile[key]
        for key in ("path", "packed_size", "packed_sha256", "raw_size", "raw_sha256", "string_count")
    }


def build_bundle() -> tuple[dict[str, Any], dict[str, Any]]:
    current_profile, current = load_table(CURRENT_PATH, CURRENT_EXPECTED, "strict current input")
    jp_profile, jp = load_table(DIRECT_JP_PATH, DIRECT_EXPECTED["jp"], "direct JP")
    en_profile, en = load_table(DIRECT_EN_PATH, DIRECT_EXPECTED["en"], "direct EN")
    sc_profile, sc = load_table(DIRECT_SC_PATH, DIRECT_EXPECTED["sc"], "direct SC")
    tc_profile, tc = load_table(DIRECT_TC_PATH, DIRECT_EXPECTED["tc"], "direct TC")
    legacy_profile, legacy = load_table(LEGACY_KO_PATH, DIRECT_EXPECTED["legacy"], "pre-compaction Korean")
    require(
        all(len(values) == len(current) for values in (jp, en, sc, tc, legacy)),
        "source table string count mismatch",
    )

    historical_doc = read_json(HISTORICAL_MANIFEST)
    reservations_doc = read_json(RESERVATION_MANIFEST)
    inventory_doc = read_json(INVENTORY_MANIFEST)
    historical_entries = historical_doc.get("entries")
    reservations = reservations_doc.get("reservations")
    inventory_rows = inventory_doc.get("rows")
    require(isinstance(historical_entries, list), "historical entries missing")
    require(isinstance(reservations, Mapping), "runtime reservation map missing")
    require(isinstance(inventory_rows, list), "manual inventory rows missing")

    selected = [
        row
        for row in historical_entries
        if isinstance(row, Mapping)
        and MIN_ID <= row.get("id", -1) <= MAX_ID
        and (
            row.get("operation") == "manual_compact_korean_layout"
            or "manual_compact_korean_layout" in row.get("newline_operations", [])
        )
    ]
    selected.sort(key=lambda row: row["id"])
    selected_ids = tuple(row["id"] for row in selected)
    require(selected_ids == EXPECTED_TARGET_IDS, f"manual compact selection drift: {selected_ids}")
    require(set(PROPOSALS) == set(EXPECTED_TARGET_IDS), "proposal coverage drift")

    current_diff_ids = tuple(
        row["id"] for row in selected if current[row["id"]] != row.get("ko")
    )
    require(current_diff_ids == EXPECTED_CURRENT_DIFF_IDS, f"current-difference scope drift: {current_diff_ids}")
    inventory_by_id = {
        row.get("entry_id"): row for row in inventory_rows if isinstance(row, Mapping) and isinstance(row.get("entry_id"), int)
    }

    entries: list[dict[str, Any]] = []
    strategy_counts: Counter[str] = Counter()
    legacy_exact_ids: list[int] = []
    source_retranslation_ids: list[int] = []
    current_reconciled_ids: list[int] = []
    runtime_token_ids: list[int] = []
    four_line_ids: list[int] = []

    for historical_row in selected:
        entry_id = historical_row["id"]
        compact = historical_row.get("ko")
        require(isinstance(compact, str), f"{entry_id}: historical Korean missing")
        proposal = PROPOSALS[entry_id]
        proposed = proposal["text"]
        current_ko = current[entry_id]
        legacy_ko = normalize_legacy_layout(legacy[entry_id])
        inventory_row = inventory_by_id.get(entry_id)
        require(isinstance(inventory_row, Mapping), f"{entry_id}: inventory row missing")

        for value in (compact, current_ko, legacy_ko, proposed, jp[entry_id]):
            assert_colour_layout(value, entry_id)
        compact_signature = control_signature(compact)
        current_signature = control_signature(current_ko)
        legacy_signature = control_signature(legacy_ko)
        proposed_signature = control_signature(proposed)
        jp_signature = control_signature(jp[entry_id])
        require(
            proposed_signature == current_signature == compact_signature == jp_signature,
            f"{entry_id}: proposed/current/compact/JP protected signature drift",
        )
        require(
            legacy_signature == current_signature,
            f"{entry_id}: legacy protected signature differs; manual migration evidence required",
        )

        lines = line_metrics(entry_id, proposed, current, reservations)
        require(1 <= len(lines) <= MAX_LINES, f"{entry_id}: line count {len(lines)} exceeds max {MAX_LINES}")
        require(not any(line["exceeds_912px"] for line in lines), f"{entry_id}: effective width exceeds 912px")
        strategy = proposal["strategy"]
        strategy_counts[strategy] += 1
        if proposed == legacy_ko:
            legacy_exact_ids.append(entry_id)
        else:
            source_retranslation_ids.append(entry_id)
        if strategy.startswith("reconcile_later_current"):
            current_reconciled_ids.append(entry_id)
        if proposed_signature["runtime_tokens"]:
            runtime_token_ids.append(entry_id)
        if len(lines) == 4:
            four_line_ids.append(entry_id)

        entries.append(
            {
                "entry_id": entry_id,
                "scene_batch_id": inventory_row.get("scene_batch_id"),
                "review_status": "ready_for_semantic_restoration_candidate",
                "restoration_strategy": strategy,
                "review_judgement": proposal["reason"],
                "historical_manual_compact_ko": compact,
                "current_ko_at_strict_6000_7999_baseline": current_ko,
                "legacy_precompaction_ko": legacy_ko,
                "proposed_ko": proposed,
                "legacy_matches_proposed_after_indent_normalization": proposed == legacy_ko,
                "historical_compact_to_proposed_surface_units": reintroduced_surface_units(compact, proposed),
                "current_to_proposed_surface_units": reintroduced_surface_units(current_ko, proposed),
                "direct_pc_sources": {
                    "jp": jp[entry_id],
                    "en": en[entry_id],
                    "sc": sc[entry_id],
                    "tc": tc[entry_id],
                },
                "text_sha256_utf16le": {
                    "historical_manual_compact_ko": text_digest(compact),
                    "current_ko": text_digest(current_ko),
                    "legacy_precompaction_ko": text_digest(legacy_ko),
                    "proposed_ko": text_digest(proposed),
                },
                "control_signature": {
                    "historical_manual_compact": compact_signature,
                    "current": current_signature,
                    "legacy_precompaction": legacy_signature,
                    "proposed": proposed_signature,
                    "direct_pc_jp": jp_signature,
                    "proposed_current_compact_jp_match": True,
                },
                "layout": {
                    "line_count": len(lines),
                    "max_lines": MAX_LINES,
                    "all_lines_pass_static_patch_007": True,
                    "any_line_exceeds_912px": False,
                    "lines": lines,
                },
                "review_policy": {
                    "japanese_source_linebreaks_used_as_layout_authority": False,
                    "korean_linebreaks_are_manual_semantic_boundaries": True,
                    "sentence_shortening_or_deletion_allowed": False,
                    "automatic_linebreak_stripping_forbidden": True,
                    "automatic_decompaction_forbidden": True,
                },
            }
        )

    require(len(entries) == len(EXPECTED_TARGET_IDS), "entry accounting drift")
    require(current_reconciled_ids == list(EXPECTED_CURRENT_DIFF_IDS), "current reconciliation accounting drift")

    max_raw = max(line["raw_g1n_width_px"] for entry in entries for line in entry["layout"]["lines"])
    max_effective = max(line["effective_width_px"] for entry in entries for line in entry["layout"]["lines"])
    max_line_count = max(entry["layout"]["line_count"] for entry in entries)
    payload = {
        "schema": SCHEMA,
        "scope": {
            "resource": RESOURCE,
            "event_id_range": [MIN_ID, MAX_ID],
            "manual_compact_target_count": len(entries),
            "current_differs_from_historical_compact_ids": list(current_diff_ids),
            "legacy_exact_restoration_count": len(legacy_exact_ids),
            "source_complete_retranslation_or_terminology_correction_count": len(source_retranslation_ids),
            "later_current_revision_reconciled_count": len(current_reconciled_ids),
            "candidate_binary_created": False,
            "steam_files_written": False,
            "git_or_release_actions_performed": False,
            "network_operation_performed": False,
        },
        "layout_baseline": {
            "authority": "Static Patch 007 verified PK event-dialogue layout",
            "runtime_font_px": RUNTIME_FONT_PX,
            "runtime_usable_line_width_px": MAX_EFFECTIVE_WIDTH_PX,
            "max_lines": MAX_LINES,
            "raw_g1n_full_width_advance_px": RAW_FULL_WIDTH_PX,
            "raw_g1n_half_width_advance_px": RAW_HALF_WIDTH_PX,
            "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "raw_g1n_pass_limit_px": MAX_RAW_WIDTH_PX,
            "effective_width_pass_limit_px": MAX_EFFECTIVE_WIDTH_PX,
            "dynamic_name_reservations": "Catalog full-name reservation scaled by 30/48; runtime_proven stays false.",
        },
        "sources": {
            "strict_current_ko_6000_7999_successor": source_summary(current_profile),
            "direct_pc_jp_pristine": source_summary(jp_profile),
            "direct_pc_en": source_summary(en_profile),
            "direct_pc_sc": source_summary(sc_profile),
            "direct_pc_tc": source_summary(tc_profile),
            "legacy_precompaction_ko_backup": source_summary(legacy_profile),
            "historical_manual_compact_manifest": {
                "path": path_label(HISTORICAL_MANIFEST),
                "sha256": digest(HISTORICAL_MANIFEST.read_bytes()),
            },
            "runtime_reservation_manifest": {
                "path": path_label(RESERVATION_MANIFEST),
                "sha256": digest(RESERVATION_MANIFEST.read_bytes()),
            },
            "manual_compact_inventory": {
                "path": path_label(INVENTORY_MANIFEST),
                "sha256": digest(INVENTORY_MANIFEST.read_bytes()),
            },
        },
        "judgement_groups": [
            {
                "group": "exact_unabridged_legacy_restoration",
                "ids": legacy_exact_ids,
                "reason": "The pre-compaction Korean is source-complete, retains semantic Korean boundaries, and passes the current four-line Static Patch 007 gate.",
            },
            {
                "group": "source_complete_retranslation_or_terminology_correction",
                "ids": source_retranslation_ids,
                "reason": "The source witnesses require a more precise Korean relation, term, agent, or clause construction than a blind legacy restore. No semantic material is deleted.",
            },
            {
                "group": "later_current_revision_reconciled",
                "ids": current_reconciled_ids,
                "reason": "3953/3954/3956/3957 retain the later Inoue spelling while restoring source-complete clauses; 3986 retains valid current naming but remains abbreviated. None is overwritten blindly.",
            },
            {
                "group": "four_line_semantic_layout",
                "ids": four_line_ids,
                "reason": "Four Korean semantic lines are permitted by Static Patch 007. They are not compressed to three lines merely to match the old rule.",
            },
            {
                "group": "runtime_name_token_reservation_reviewed",
                "ids": runtime_token_ids,
                "reason": "All runtime-token rows have a catalog full-name reservation. Width is conservatively reserved then scaled by 30/48; runtime_proven remains false.",
            },
        ],
        "hold_disposition": {
            "entry_3820_existing_quality_hold": {
                "in_scope": False,
                "action_taken": "none",
                "reason": "3820 is outside the assigned 3900-3999 range. It remains untouched; resolving it requires its own source-context and speaker-quality review.",
            },
            "unresolved_runtime_token_holds_in_scope": {
                "ids": [],
                "reason": "Every runtime token occurring in this scope has a reservation-catalog entry. The evidence is conservative only, so runtime_proven is explicitly false in each line report.",
            },
        },
        "counts": {
            "strategy_counts": dict(sorted(strategy_counts.items())),
            "runtime_token_row_count": len(runtime_token_ids),
            "four_line_row_count": len(four_line_ids),
            "max_raw_g1n_width_px": max_raw,
            "max_effective_width_px": max_effective,
            "max_line_count": max_line_count,
            "all_rows_within_912px": True,
            "all_rows_within_four_lines": True,
        },
        "entries": entries,
        "safety": {
            "candidate_binary_written": False,
            "steam_game_resource_written": False,
            "git_operation_performed": False,
            "release_published": False,
            "network_operation_performed": False,
        },
    }
    validation = {
        "schema": "nobu16.kr.manual-compact-3900-review-validation.v1",
        "status": "PASS",
        "review_output": path_label(OUTPUT),
        "target_count": len(entries),
        "target_ids": list(EXPECTED_TARGET_IDS),
        "current_diff_ids": list(current_diff_ids),
        "runtime_token_row_count": len(runtime_token_ids),
        "four_line_row_count": len(four_line_ids),
        "max_raw_g1n_width_px": max_raw,
        "max_effective_width_px": max_effective,
        "max_line_count": max_line_count,
        "over_912px_line_count": 0,
        "candidate_binary_created": False,
        "steam_files_written": False,
        "git_or_release_actions_performed": False,
        "network_operation_performed": False,
    }
    return payload, validation


def write_atomic(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(content)
    temporary.replace(path)


def source_whitespace_check() -> None:
    for number, line in enumerate(SCRIPT.read_text(encoding="utf-8").splitlines(), 1):
        require(line == line.rstrip(), f"trailing whitespace at {SCRIPT.name}:{number}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify", "summary"))
    args = parser.parse_args(argv)
    source_whitespace_check()
    payload, validation = build_bundle()
    if args.command == "build":
        write_atomic(OUTPUT, canonical_json(payload))
        validation = {**validation, "review_output_sha256": digest(OUTPUT.read_bytes())}
        write_atomic(VALIDATION, canonical_json(validation))
        print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
        return 0
    if args.command == "verify":
        require(OUTPUT.is_file(), f"missing review output: {OUTPUT}")
        require(VALIDATION.is_file(), f"missing validation output: {VALIDATION}")
        require(OUTPUT.read_bytes() == canonical_json(payload), "review JSON differs from deterministic rebuild")
        expected_validation = {**validation, "review_output_sha256": digest(OUTPUT.read_bytes())}
        require(VALIDATION.read_bytes() == canonical_json(expected_validation), "validation JSON differs from deterministic rebuild")
        print(json.dumps(expected_validation, ensure_ascii=False, sort_keys=True))
        return 0
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ReviewError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
