#!/usr/bin/env python3
"""Build PK block-0 runtime-terminal segment 1040 decisions.

The tracked builder deliberately contains no source-language dialogue.
Source authority is established from pristine PK at runtime and pinned by
digests; source-bearing decisions are written only below ignored tmp/.
"""

from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch006_segment1018 as BASE_LEFT
import build_base_batch006_segment1019 as BASE_RIGHT
import build_pk_batch001_segment1025 as HELPERS
import build_pk_batch006_segment1039 as LEFT_PK


ENGINE = BASE_RIGHT.ENGINE
GENERAL = BASE_RIGHT.GENERAL
UTIL = BASE_RIGHT.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B006_S1040.private.v1.jsonl"
)
BASE_DECISIONS = (
    (
        REPO
        / "tmp"
        / WORKSTREAM.name
        / "decisions"
        / "base_msggame_B006_S1018.private.v1.jsonl",
        "0651CC4E77A5B21E6FBD713AA33019B10BE3164DF6081165122D09A9F365A224",
    ),
    (
        REPO
        / "tmp"
        / WORKSTREAM.name
        / "decisions"
        / "base_msggame_B006_S1019.private.v1.jsonl",
        "71DC064001193A00A4CB03D7FB6C45D637CF5F412D07674D02FC7EADD678AEAC",
    ),
)
SEGMENT = 1040
QUEUE_BATCH_ID = "pk_msggame-B006"
BLOCK_ID = 0
QUEUE_START = 67
QUEUE_STOP = 134
BASE_RECORD_IDS = tuple(range(2270, 2337))
RECORD_IDS = tuple(range(2338, 2405))
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
FULL_RECORD_IDS = tuple(range(2336, 2406))
FULL_RECORD_KEYS = tuple(
    (BLOCK_ID, record_id) for record_id in FULL_RECORD_IDS
)
TARGET_COORDINATES = tuple(
    f"{BLOCK_ID}:{record_id}:0" for record_id in RECORD_IDS
)
QUEUE_HIDDEN_COORDINATES = ("0:2406:0", "0:2410:0")
PK_RECORD_COUNT = 21751

# These are actual 014A roots. The topology intentionally includes the
# reused 526/532 roots rather than inventing ordinal successors.
FULL_PK_GROUPS = {
    898: tuple(range(2336, 2343)),
    526: tuple(range(2343, 2350)),
    532: tuple(range(2350, 2357)),
    904: tuple(range(2357, 2364)),
    910: tuple(range(2364, 2371)),
    916: tuple(range(2371, 2378)),
    922: tuple(range(2378, 2385)),
    928: tuple(range(2385, 2392)),
    934: tuple(range(2392, 2399)),
    940: tuple(range(2399, 2406)),
}
RECORD_TO_ROOT = {
    record_id: root
    for root, record_ids in FULL_PK_GROUPS.items()
    for record_id in record_ids
    if record_id in RECORD_IDS
}
EXPECTED_ROOT_CLOSURES = {
    root: tuple(range(root, root + 6)) + record_ids
    for root, record_ids in FULL_PK_GROUPS.items()
}

# Seven entries follow the runtime speaker-register order. These Korean-only
# policies retain formal, plain, and period-register distinctions.
TRANSLATION_POLICY_BY_ROOT = {
    898: (
        "해 주었으면 합니다",
        "해 주었으면 한다",
        "해 주시기를 바라옵니다",
        "해 주시기를 바라옵니다",
        "해 주었으면 합니다",
        "해 주었으면 하오",
        "해 주었으면 한다",
    ),
    526: (
        "왔습니다",
        "왔다",
        "왔사옵니다",
        "왔사옵니다",
        "왔습니다",
        "왔소",
        "왔다",
    ),
    532: (
        "주십시오",
        "오너라",
        "주시옵소서",
        "주시옵소서",
        "주십시오",
        "주시오",
        "오너라",
    ),
    904: (
        "맡겨 주십시오",
        "맡겨 다오",
        "맡겨 주십시오",
        "맡겨 주십시오",
        "맡겨 주십시오",
        "맡겨 주시오",
        "맡겨라",
    ),
    910: (
        "기다려 주십시오",
        "기다려 다오",
        "기다려 주십시오",
        "기다려 주시오",
        "기다려 주십시오",
        "기다려 주셨으면 하오",
        "기다려 다오",
    ),
    916: (
        "기다리십시오",
        "기다려라",
        "기다리십시오",
        "기다리시오",
        "기다려 주십시오",
        "기다려라",
        "기다려라",
    ),
    922: (
        "기다려 주십시오",
        "기다리시오",
        "기다려 주시옵소서",
        "기다려 주시오",
        "기다려 주십시오",
        "기다리시오",
        "기다리고 있거라",
    ),
    928: (
        "지 않습니다",
        "지 않는다",
        "지 않사옵니다",
        "지 않사옵니다",
        "지 않습니다",
        "지 않습니다",
        "지 않는다",
    ),
    934: (
        "훌륭합니다",
        "훌륭하다",
        "훌륭하옵니다",
        "훌륭하옵니다",
        "훌륭합니다",
        "훌륭하오",
        "훌륭하다",
    ),
    940: (
        "합니다",
        "한다",
        "합니다",
        "하옵니다",
        "합니다",
        "합니다",
        "한다",
    ),
}
FULL_TRANSLATION_POLICY = {
    record_id: translation
    for root, record_ids in FULL_PK_GROUPS.items()
    for record_id, translation in zip(
        record_ids,
        TRANSLATION_POLICY_BY_ROOT[root],
        strict=True,
    )
}
TRANSLATIONS_BY_RECORD = {
    record_id: FULL_TRANSLATION_POLICY[record_id]
    for record_id in RECORD_IDS
}
TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}

LEFT_ROOT898_FULL_IDS = FULL_PK_GROUPS[898]
LEFT_ROOT898_SOURCE_SHA256 = (
    "018B23C46A980848516C9C14A9464C545A7472BA9ABD98F080B84AB3FA9DA398"
)
LEFT_ROOT898_FULL_CURRENT = (
    "원한다",
    "원한다",
    "받고 싶다",
    "받고 싶다",
    "원한다",
    "원한다",
    "원한다",
)
LEFT_ROOT898_FULL_POLICY = TRANSLATION_POLICY_BY_ROOT[898]

# Exported for S1041's direct left-boundary contract.
RIGHT_ROOT940_FULL_IDS = FULL_PK_GROUPS[940]
RIGHT_ROOT940_SOURCE_SHA256 = (
    "8BC825C6678FDE7635181CD245096CFAA1FDCBCCA318036F1A5DA0A9B51F6B55"
)
RIGHT_ROOT940_FULL_CURRENT = (
    "봅니다",
    "음",
    "봅니다",
    "보옵니다",
    "봅니다",
    "봅니다",
    "음",
)
RIGHT_ROOT940_FULL_POLICY = TRANSLATION_POLICY_BY_ROOT[940]

EXPECTED_SOURCE_LITERAL_SHA256 = (
    "80F4A9BF795DBB6535A98EC9CE84E1E7C71E9FD7C3DDA747BE4E5CEA815A82A7"
)
EXPECTED_SOURCE_SIGNATURE_SHA256 = (
    "2780D6E2C8B9C60BD7D2C224D25E4800BF7CF1E0B4030BFDB545EE61D46C5B40"
)
EXPECTED_POLICY_SHA256 = (
    "884F7628EBEF88DB6FDE6DB09E5A5EDEC6D87B0A15F06DE479465D68C9DD5B92"
)
EXPECTED_MAPPING_SHA256 = (
    "E170C60D32B476A54AA209D8826AB4DBB564C896BD5A865F28ED803F4592319E"
)
EXPECTED_CHANGED_LITERAL_COUNT = 45
PK_TARGET_ARCHIVE_DIGESTS = {
    "pk_jp": "5B94CEBFFD67BE5E529C04A8552B3E8FE73A64119E6F7DBCB8E390EE9411B705",
    "pk_current": "219C931F70EA809807F13C94B57E600467BD619BE4C88C5D72517CEC569067B7",
    "pk_sc": "3677B0A4821CCBF755E0B51C6584E5561C1AC01901643521F89237E0F52F4A0E",
    "pk_tc": "3677B0A4821CCBF755E0B51C6584E5561C1AC01901643521F89237E0F52F4A0E",
    "pk_en": "3677B0A4821CCBF755E0B51C6584E5561C1AC01901643521F89237E0F52F4A0E",
}
PK_FULL_ARCHIVE_DIGESTS = {
    "pk_jp": "F992831BA4AABEB680F0E7EE9C149E22EE4196BDF2E4A9C0D24B1A54E220929E",
    "pk_current": "DA252B76B8A46CB4DE0117AAD2B34CA6B5C5EFDF4598730C193CD6E4C0C9D119",
    "pk_sc": "EE7A4823DB03C0E5E94C6D2F26BB31E7D94D2D9D08C3891A5AB9251E5382268F",
    "pk_tc": "EE7A4823DB03C0E5E94C6D2F26BB31E7D94D2D9D08C3891A5AB9251E5382268F",
    "pk_en": "EE7A4823DB03C0E5E94C6D2F26BB31E7D94D2D9D08C3891A5AB9251E5382268F",
}
PK_TARGET_INCOMING_SHA256 = (
    "15F60C044A788C3DB2AE849D5303D95F901904AB039D0C5F8517988865DC2CE5"
)
PK_FULL_INCOMING_SHA256 = (
    "353A3282D4C67949F25BF5D00B16789216EB9128146E9659D16479BBE506C7A2"
)
EXPECTED_CALL_EVIDENCE_SHA256 = (
    "40402C9C4C2F0C08AF657AA398CF7A7F1FF14B64E3F2F35A40DE622766094C69"
)
ROOT940_CHAIN_GAP_SHA256 = (
    "DB42BD2491E8A0A5967457D3A01C2329251574AD4087D7FC07C0FA01A3262F8B"
)
MORPHOLOGY_014C_RE = re.compile(b"\x01\x4C(.{4})", re.DOTALL)
EXPECTED_014C_OVERLAP = ((15, 25, 0, 65, 84213762),)

ROOT_TRANSLATION_RATIONALE = {
    898: (
        "A desired action is expressed as a complete Korean request matrix, "
        "with courtly and plain registers kept distinct; caller predicates "
        "must be rewritten before the request ending."
    ),
    526: (
        "This family is the auxiliary return-after-action sense, so the "
        "policy uses 왔다 rather than the unrelated defeat idiom; finite "
        "current callers must be flattened or normalized."
    ),
    532: (
        "The sole caller is a direction to follow the speaker, so the plain "
        "imperative is 오너라 rather than a direction away from the speaker."
    ),
    904: (
        "Delegation requests retain formal, plain, and courtly speaker "
        "registers; caller boundaries require explicit spacing or flattening."
    ),
    910: (
        "Polite and plain requests to wait are kept distinct, including the "
        "courtly wish form."
    ),
    916: (
        "The latent command family preserves direct, polite, and courtly "
        "imperatives even though no live caller currently reaches it."
    ),
    922: (
        "The wait-request family preserves courtly and plain variation; its "
        "only pristine call is already flattened in current Korean."
    ),
    928: (
        "This is a bound verbal negative, not a standalone verb; callers "
        "must supply a compatible Korean lexical stem before 지 않다."
    ),
    934: (
        "Standalone praise is rendered as 훌륭하다 with the full register "
        "matrix and composes directly before the current exclamation."
    ),
    940: (
        "This is a bound finite verb family. Korean lexical stems vary by "
        "caller, so callers must be semantically rewritten before the 하다 "
        "register ending or flattened when already complete."
    ),
}
ROOT_ASSEMBLY_PLAN = {
    898: (
        "rewrite each caller to the requested action stem, then retain the "
        "selected desire/request terminal; jointly flatten fixed desire text"
    ),
    526: (
        "normalize the completed action and explicit word boundary before "
        "the auxiliary return terminal, or flatten already-finite callers"
    ),
    532: (
        "retain the follow/come command terminal while normalizing the caller "
        "boundary and full-width sentence punctuation"
    ),
    904: (
        "insert or rewrite an explicit Korean boundary before the delegation "
        "request; flatten callers already complete in current Korean"
    ),
    910: (
        "insert a Korean boundary before the wait request where needed; "
        "terminal-at-line-start callers can compose directly"
    ),
    916: "no live caller; preserve the seven-register command policy",
    922: (
        "the pristine command was flattened into a complete current Korean "
        "sentence and must remain registered for reintegration"
    ),
    928: (
        "normalize the caller to its Korean lexical stem before the bound "
        "negative; jointly rewrite fixed conditional or contrast text"
    ),
    934: "standalone praise terminal followed by normalized punctuation",
    940: (
        "rewrite to a Korean lexical or action-noun stem before the finite "
        "terminal; flatten fixed clauses, command chains, and complete callers"
    ),
}

# All observed text below is current Korean. No source-language dialogue is
# embedded in this tracked file.
CALLER_INTEGRATION_EVIDENCE = {
    898: (
        {
            "call_site": "6:3590:2:0",
            "observed_current_left": "으로서\n보필할 대상:",
            "observed_current_right": "",
            "expected_current_gap_hex": "014382030000050505",
            "integration_mode": "normalize_and_retain_desire",
            "source_free_korean_example": (
                "으로서\n보필할 대상을 정해 주시기를 바라옵니다"
            ),
        },
        {
            "call_site": "6:4679:1:0",
            "observed_current_left": (
                "그쪽에도 나쁘지 않은 이야기일 것이오\n"
                "그 점을 감안해 주시"
            ),
            "observed_current_right": "기 바라오",
            "expected_current_gap_hex": "014382030000",
            "integration_mode": "normalize_and_flatten_fixed_desire",
            "source_free_korean_example": (
                "그쪽에도 나쁘지 않은 이야기일 것이오\n"
                "그 점을 감안해 주었으면 하오"
            ),
        },
    ),
    526: (
        {
            "call_site": "15:2175:2:0",
            "observed_current_left": "사건에 대해\n상세한 이야기를 알아내",
            "observed_current_right": "\n전말을 보고",
            "expected_current_gap_hex": "01430E020000",
            "integration_mode": "boundary_and_retain_auxiliary",
            "source_free_korean_example": (
                "사건에 대해\n상세한 이야기를 알아내 왔습니다\n전말을 보고"
            ),
        },
        {
            "call_site": "8:1119:1:0",
            "observed_current_left": "을 발전시켰습니다",
            "observed_current_right": (
                "!\n그 땅은 전에 없이 번창하고 있으니\n"
                "그 혜택도 더욱 커질 것입니다"
            ),
            "expected_current_gap_hex": "01430E020000",
            "integration_mode": "flatten_complete_caller",
            "source_free_korean_example": (
                "을 발전시켰습니다!\n"
                "그 땅은 전에 없이 번창하고 있으니\n"
                "그 혜택도 더욱 커질 것입니다"
            ),
        },
    ),
    532: (
        {
            "call_site": "1:10:4:0",
            "observed_current_left": (
                "。하지만 짚이는 곳이 있으니, 따라"
            ),
            "observed_current_right": "。단서가 있다고 믿",
            "expected_current_gap_hex": "014314020000",
            "integration_mode": "normalize_caller_and_punctuation",
            "source_free_korean_example": (
                ". 하지만 짚이는 곳이 있으니, 따라오너라. "
                "단서가 있다고 믿는다."
            ),
        },
    ),
    904: (
        {
            "call_site": "13:113:3:0",
            "observed_current_left": "에게 선봉의 소임을,",
            "observed_current_right": "\n적을 무찔러 보이",
            "expected_current_gap_hex": "014388030000",
            "integration_mode": "boundary_rewrite_and_retain_request",
            "source_free_korean_example": (
                "에게 선봉의 소임을 맡겨 주십시오\n적을 무찔러 보이"
            ),
        },
        {
            "call_site": "2:221:1:0",
            "observed_current_left": (
                "사람을 쓰는 일에는 제법 자신이 있지……\n"
                "부하 지휘는 내게 맡겨라."
            ),
            "observed_current_right": "",
            "expected_current_gap_hex": "014388030000050505",
            "integration_mode": "flatten_complete_caller",
            "source_free_korean_example": (
                "사람을 쓰는 일에는 제법 자신이 있지……\n"
                "부하 지휘는 내게 맡겨라."
            ),
        },
        {
            "call_site": "2:218:1:0",
            "observed_current_left": (
                "백성을 다스리는 비결은 오직 진심뿐.\n"
                "이 군의 장악은 제게 "
            ),
            "observed_current_right": "맡기십시오!",
            "expected_source_gap_hex": "014388030000",
            "expected_current_gap_hex": "",
            "integration_mode": "flatten_source_command_in_current",
            "source_free_korean_example": (
                "백성을 다스리는 비결은 오직 진심뿐.\n"
                "이 군의 장악은 제게 맡기십시오!"
            ),
        },
        {
            "call_site": "6:1430:1:0",
            "observed_current_left": "、",
            "observed_current_right": "\n반드시",
            "expected_current_gap_hex": "014388030000",
            "integration_mode": "normalize_leading_punctuation",
            "source_free_korean_example": ", 맡겨 주십시오\n반드시",
        },
    ),
    910: (
        {
            "call_site": "15:1928:1:0",
            "observed_current_left": "조금만 더",
            "observed_current_right": "\n결과가 나올 때까지\n남은",
            "expected_current_gap_hex": "01438E030000",
            "integration_mode": "boundary_rewrite_and_retain_request",
            "source_free_korean_example": (
                "조금만 더 기다려 주십시오\n결과가 나올 때까지\n남은"
            ),
        },
        {
            "call_site": "6:3678:0:0",
            "observed_current_left": "",
            "observed_current_right": "\n어째서",
            "expected_current_gap_hex": "01438E030000",
            "integration_mode": "direct_composition",
            "source_free_korean_example": "기다려 주십시오\n어째서",
        },
    ),
    922: (
        {
            "call_site": "15:2225:2:0",
            "observed_current_left": "\n낭보를 기다려 주십시오.",
            "observed_current_right": "",
            "expected_source_gap_hex": "01439A030000050505",
            "expected_current_gap_hex": "050505",
            "integration_mode": "flatten_source_command_in_current",
            "source_free_korean_example": "\n낭보를 기다려 주십시오.",
        },
    ),
    928: (
        {
            "call_site": "6:3627:3:0",
            "observed_current_left": (
                "을(를) 내놓는 것은\n그다지 내키지 않"
            ),
            "observed_current_right": "…",
            "expected_current_gap_hex": "0143A0030000",
            "integration_mode": "normalize_negative_stem",
            "source_free_korean_example": (
                "을(를) 내놓는 것은\n그다지 내키지 않습니다…"
            ),
        },
        {
            "call_site": "6:3528:3:0",
            "observed_current_left": (
                "、지향할 곳은 아직 저 위\n한층 더 힘쓰"
            ),
            "observed_current_right": "와",
            "expected_current_gap_hex": "0143A0030000",
            "integration_mode": "flatten_fixed_conditional",
            "source_free_korean_example": (
                ", 지향할 곳은 아직 저 위\n한층 더 힘쓰지 않으면"
            ),
        },
        {
            "call_site": "6:4674:1:0",
            "observed_current_left": "많은 것을 바라지는 않습니",
            "observed_current_right": "만 굳이 말하자면…",
            "expected_current_gap_hex": "0143A0030000",
            "integration_mode": "normalize_stem_and_retain_fixed_particle",
            "source_free_korean_example": (
                "많은 것을 바라지는 않습니다만 굳이 말하자면…"
            ),
        },
    ),
    934: (
        {
            "call_site": "1:25:0:0",
            "observed_current_left": "",
            "observed_current_right": "! 이제는",
            "expected_current_gap_hex": "0143A6030000",
            "integration_mode": "direct_composition",
            "source_free_korean_example": "훌륭합니다! 이제는",
        },
    ),
    940: (
        {
            "call_site": "7:2490:6:0",
            "observed_current_left": "가세를 부탁하",
            "observed_current_right": "！",
            "expected_current_gap_hex": "0143AC030000",
            "integration_mode": "normalize_stem_and_punctuation",
            "source_free_korean_example": "가세를 부탁합니다!",
        },
        {
            "call_site": "6:4793:1:0",
            "observed_current_left": "\n더 좋은 영지를 원합니",
            "observed_current_right": "\n통치에 힘쓰겠습니",
            "expected_current_gap_hex": "0143AC030000",
            "integration_mode": "normalize_stem_and_retain_terminal",
            "source_free_korean_example": (
                "\n더 좋은 영지를 원합니다\n통치에 힘쓰겠습니"
            ),
        },
        {
            "call_site": "15:1911:1:0",
            "observed_current_left": "매달 유지비가 늘어",
            "observed_current_right": (
                "가\n그에 걸맞은 대가는 얻을 수 있"
            ),
            "expected_current_gap_hex": "0143AC030000",
            "integration_mode": "flatten_fixed_clause",
            "source_free_korean_example": (
                "매달 유지비가 늘어나지만\n"
                "그에 걸맞은 대가는 얻을 수 있"
            ),
        },
        {
            "call_site": "6:4224:1:0",
            "observed_current_left": (
                "적성 장수의 충성을 흔들기 위해\n"
                "당주의 나쁜 소문을 퍼뜨립니다."
            ),
            "observed_current_right": "",
            "expected_source_gap_hex": "0143AC030000050505",
            "expected_current_gap_hex": "050505",
            "integration_mode": "flatten_source_command_in_current",
            "source_free_korean_example": (
                "적성 장수의 충성을 흔들기 위해\n"
                "당주의 나쁜 소문을 퍼뜨립니다."
            ),
        },
        {
            "call_site": "2:231:1:0",
            "observed_current_left": (
                "적의 공격을 신속히 물리치도록,\n"
                "엄중히 경계하며 전진하자."
            ),
            "observed_current_right": "",
            "expected_current_gap_hex":
            "0143AC0300000143FC010000050505",
            "integration_mode": "flatten_fixed_command_chain",
            "source_free_korean_example": (
                "적의 공격을 신속히 물리치도록,\n"
                "엄중히 경계하며 전진하자."
            ),
        },
        {
            "call_site": "7:2502:3:0",
            "observed_current_left": "을 공격하겠습니다",
            "observed_current_right": "！",
            "expected_current_gap_hex": "0143AC030000",
            "integration_mode": "flatten_complete_caller",
            "source_free_korean_example": "을 공격하겠습니다!",
        },
    ),
}
EXPECTED_INTEGRATION_CLASS_COUNTS = {
    "normalize_and_retain_desire": 1,
    "normalize_and_flatten_fixed_desire": 1,
    "boundary_and_retain_auxiliary": 1,
    "flatten_complete_caller": 3,
    "normalize_caller_and_punctuation": 1,
    "boundary_rewrite_and_retain_request": 2,
    "flatten_source_command_in_current": 3,
    "normalize_leading_punctuation": 1,
    "direct_composition": 2,
    "normalize_negative_stem": 1,
    "flatten_fixed_conditional": 1,
    "normalize_stem_and_retain_fixed_particle": 1,
    "normalize_stem_and_punctuation": 1,
    "normalize_stem_and_retain_terminal": 1,
    "flatten_fixed_clause": 1,
    "flatten_fixed_command_chain": 1,
}
BASIS = (
    "review_queue_pk_msggame_B006_zero_based_visible_ordinals67_133_"
    "pristine_pk_pc_jp_runtime_source_authority_no_source_dialogue_in_"
    "tracked_builder_block0_records2338_2404_67_visible_global_unique_"
    "exact67_literal_gap_reverse_search_discovered_Base2270_2336_plus68_"
    "Base_auxiliary_only_pk_jp_current_sc_tc_en_target67_full70_digests_"
    "014a_incoming_all_labels_source_current_full_closures_0143_call_fixed_"
    "source_only_current_only_aggregate_014c_overlap_false_positive_one_"
    "left_root898_independent_full_policy_right_root940_exported_policy_"
    "desire_auxiliary_return_follow_delegation_wait_negative_praise_"
    "finite_register_matrices_actual_current_caller_boundary_normalize_"
    "flatten_fixed_chain_examples_no_automatic_space_all_runtime_pending_"
    "no_historic_or_switch_authority_skeleton_outside_reverse_two_run_"
    "source_bearing_decisions_ignored_tmp_only_steam_read_only"
)


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return BASE_RIGHT.literal_texts(records, key)


def gap_bytes(record: Any) -> tuple[bytes, ...]:
    return BASE_RIGHT.gap_bytes(record)


def archive_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    return BASE_RIGHT.archive_records(prepared)


def record_signature(
    records: dict[tuple[int, int], Any],
    start: int,
    count: int,
) -> tuple[tuple[tuple[str, ...], tuple[str, ...]], ...]:
    return tuple(
        (
            literal_texts(records, (BLOCK_ID, record_id)),
            tuple(
                value.hex().upper()
                for value in gap_bytes(records[(BLOCK_ID, record_id)])
            ),
        )
        for record_id in range(start, start + count)
    )


def sequence_starts(
    records: dict[tuple[int, int], Any],
    sequence: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...],
) -> tuple[int, ...]:
    maximum = max(
        record_id
        for block_id, record_id in records
        if block_id == BLOCK_ID
    )
    count = len(sequence)
    return tuple(
        start
        for start in range(maximum - count + 2)
        if all(
            (BLOCK_ID, start + ordinal) in records
            for ordinal in range(count)
        )
        and record_signature(records, start, count) == sequence
    )


def incoming_jump_rows(
    records: dict[tuple[int, int], Any],
    target_ids: set[int],
) -> tuple[tuple[int, int, int, int, int], ...]:
    rows: list[tuple[int, int, int, int, int]] = []
    for key in sorted(records):
        for gap_id, gap in enumerate(gap_bytes(records[key])):
            for match in HELPERS.MORPHOLOGY_JUMP_RE.finditer(gap):
                operand = struct.unpack("<I", match.group(1))[0]
                if operand in target_ids:
                    rows.append(
                        (
                            key[0],
                            key[1],
                            gap_id,
                            match.start(),
                            operand,
                        )
                    )
    return tuple(rows)


def assert_queue_contract(prepared: Any) -> None:
    rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line
        and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        target["coordinate"]
        for row in rows
        for target in row["target_literals"]
        if target["visible"]
    )
    hidden = tuple(
        target["coordinate"]
        for row in rows
        for target in row["target_literals"]
        if not target["visible"]
    )
    if (
        len(rows) != 202
        or len(visible) != 200
        or hidden != QUEUE_HIDDEN_COORDINATES
        or visible[QUEUE_START:QUEUE_STOP] != TARGET_COORDINATES
        or rows[0]["record_coordinate"] != "0:2271"
        or rows[-1]["record_coordinate"] != "0:2472"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} private queue ordinal contract drifted"
        )


def discover_mapping(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[dict[int, int], int]:
    source_literals = tuple(
        literal_texts(
            records_by_label["pk_jp"],
            (BLOCK_ID, record_id),
        )[0]
        for record_id in RECORD_IDS
    )
    if (
        HELPERS.canonical_sha256(source_literals)
        != EXPECTED_SOURCE_LITERAL_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} pristine source literal digest drifted"
        )
    sequence = record_signature(
        records_by_label["pk_jp"],
        RECORD_IDS[0],
        len(RECORD_IDS),
    )
    signature_digest = hashlib.sha256(
        json.dumps(
            sequence,
            ensure_ascii=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest().upper()
    if signature_digest != EXPECTED_SOURCE_SIGNATURE_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} pristine source signature drifted"
        )
    base_hits = sequence_starts(records_by_label["base_jp"], sequence)
    pk_hits = sequence_starts(records_by_label["pk_jp"], sequence)
    if base_hits != (2270,) or pk_hits != (2338,):
        raise RuntimeError(
            f"segment {SEGMENT} global source reverse search drifted"
        )
    offset = pk_hits[0] - base_hits[0]
    mapping = {
        pk_record_id: base_hits[0] + ordinal
        for ordinal, pk_record_id in enumerate(RECORD_IDS)
    }
    if (
        offset != 68
        or tuple(mapping.values()) != BASE_RECORD_IDS
        or HELPERS.canonical_sha256(tuple(mapping.items()))
        != EXPECTED_MAPPING_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} discovered record mapping drifted"
        )
    return mapping, offset


def assert_source_and_runtime(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    mapping: dict[int, int],
) -> None:
    if (
        HELPERS.canonical_sha256(
            tuple(TRANSLATIONS_BY_RECORD.values())
        )
        != EXPECTED_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} translation policy digest drifted"
        )
    for label, expected in PK_TARGET_ARCHIVE_DIGESTS.items():
        if (
            GENERAL.subset_digest(records_by_label[label], RECORD_KEYS)
            != expected
        ):
            raise RuntimeError(
                f"segment {SEGMENT} target {label} digest drifted"
            )
    for label, expected in PK_FULL_ARCHIVE_DIGESTS.items():
        if (
            GENERAL.subset_digest(
                records_by_label[label],
                FULL_RECORD_KEYS,
            )
            != expected
        ):
            raise RuntimeError(
                f"segment {SEGMENT} full {label} digest drifted"
            )
    for pk_record_id, base_record_id in mapping.items():
        pk_key = (BLOCK_ID, pk_record_id)
        base_key = (BLOCK_ID, base_record_id)
        for label in PK_TARGET_ARCHIVE_DIGESTS:
            if (
                len(literal_texts(records_by_label[label], pk_key)) != 1
                or gap_bytes(records_by_label[label][pk_key])
                != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} PK skeleton drifted: "
                    f"{label}/{pk_key}"
                )
        for language in ("jp", "current", "sc", "tc"):
            if (
                records_by_label[f"pk_{language}"][pk_key].data
                != records_by_label[f"base_{language}"][base_key].data
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} PK/Base {language} mapping "
                    f"drifted: {pk_key}/{base_key}"
                )
        if literal_texts(records_by_label["pk_en"], pk_key) != ("",):
            raise RuntimeError(
                f"segment {SEGMENT} PK EN context drifted: {pk_key}"
            )


def collect_call_evidence(
    source: dict[tuple[int, int], Any],
    current: dict[tuple[int, int], Any],
) -> dict[str, tuple[tuple[int | str, ...], ...]]:
    evidence: dict[str, tuple[tuple[int | str, ...], ...]] = {}
    for root in FULL_PK_GROUPS:
        source_calls = HELPERS.root_call_sites(source, root)
        current_calls = HELPERS.root_call_sites(current, root)
        source_fixed = HELPERS.fixed_following_blockers(source, root)
        current_fixed = HELPERS.fixed_following_blockers(current, root)
        source_only = tuple(sorted(set(source_calls) - set(current_calls)))
        current_only = tuple(sorted(set(current_calls) - set(source_calls)))
        evidence[str(root)] = (
            (
                len(source_calls),
                HELPERS.canonical_sha256(source_calls),
                len(source_fixed),
                HELPERS.canonical_sha256(source_fixed),
            ),
            (
                len(current_calls),
                HELPERS.canonical_sha256(current_calls),
                len(current_fixed),
                HELPERS.canonical_sha256(current_fixed),
            ),
            (
                len(source_only),
                HELPERS.canonical_sha256(source_only),
                len(current_only),
                HELPERS.canonical_sha256(current_only),
            ),
        )
    return evidence


def caller_context_and_gap(
    records: dict[tuple[int, int], Any],
    call_site: str,
) -> tuple[str, str, str]:
    block_id, record_id, gap_id, _ = (
        int(value) for value in call_site.split(":")
    )
    literals = ENGINE.parse_record_literals(records[(block_id, record_id)])
    return (
        literals[gap_id - 1].text if gap_id else "",
        literals[gap_id].text if gap_id < len(literals) else "",
        gap_bytes(records[(block_id, record_id)])[gap_id].hex().upper(),
    )


def assert_caller_integration_evidence(
    source: dict[tuple[int, int], Any],
    current: dict[tuple[int, int], Any],
) -> None:
    class_counts: Counter[str] = Counter()
    for root, examples in CALLER_INTEGRATION_EVIDENCE.items():
        source_calls = set(HELPERS.root_call_sites(source, root))
        current_calls = set(HELPERS.root_call_sites(current, root))
        for example in examples:
            call_site = str(example["call_site"])
            mode = str(example["integration_mode"])
            class_counts[mode] += 1
            source_only = mode == "flatten_source_command_in_current"
            if source_only:
                if call_site not in source_calls or call_site in current_calls:
                    raise RuntimeError(
                        f"segment {SEGMENT} source-only caller site "
                        f"drifted: {root}/{call_site}"
                    )
                source_gap = caller_context_and_gap(source, call_site)[2]
                if source_gap != example["expected_source_gap_hex"]:
                    raise RuntimeError(
                        f"segment {SEGMENT} source-only caller gap "
                        f"drifted: {root}/{call_site}"
                    )
            elif call_site not in current_calls:
                raise RuntimeError(
                    f"segment {SEGMENT} live caller site drifted: "
                    f"{root}/{call_site}"
                )
            left, right, current_gap = caller_context_and_gap(
                current,
                call_site,
            )
            if (
                left != example["observed_current_left"]
                or right != example["observed_current_right"]
                or current_gap != example["expected_current_gap_hex"]
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} current caller context drifted: "
                    f"{root}/{call_site}"
                )
            if ENGINE.KANA_OR_HAN_RE.search(
                str(example["source_free_korean_example"])
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} caller example is not "
                    f"source-free Korean: {root}/{call_site}"
                )
    if dict(class_counts) != EXPECTED_INTEGRATION_CLASS_COUNTS:
        raise RuntimeError(
            f"segment {SEGMENT} caller integration class count drifted"
        )


def assert_runtime_graph(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[str, tuple[tuple[int | str, ...], ...]]:
    target_ids = set(RECORD_IDS)
    full_ids = set(FULL_RECORD_IDS)
    if full_ids != {
        record_id
        for record_ids in FULL_PK_GROUPS.values()
        for record_id in record_ids
    }:
        raise RuntimeError(
            f"segment {SEGMENT} full group universe drifted"
        )
    for label in PK_TARGET_ARCHIVE_DIGESTS:
        records = records_by_label[label]
        target_edges = incoming_jump_rows(records, target_ids)
        full_edges = incoming_jump_rows(records, full_ids)
        if (
            len(target_edges) != 67
            or {row[4] for row in target_edges} != target_ids
            or HELPERS.canonical_sha256(target_edges)
            != PK_TARGET_INCOMING_SHA256
            or len(full_edges) != 70
            or {row[4] for row in full_edges} != full_ids
            or HELPERS.canonical_sha256(full_edges)
            != PK_FULL_INCOMING_SHA256
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} incoming 014A graph drifted"
            )
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    for label, records in (("pk_jp", source), ("pk_current", current)):
        graph = HELPERS.graph_edges(records)
        for root, expected in EXPECTED_ROOT_CLOSURES.items():
            if tuple(sorted(HELPERS.graph_closure(graph, root))) != (
                expected
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {label} closure drifted: {root}"
                )
        valid: list[tuple[int, int, int, int, int]] = []
        overlapped: list[tuple[int, int, int, int, int]] = []
        for (block_id, record_id), record in sorted(records.items()):
            for gap_id, gap in enumerate(gap_bytes(record)):
                jump_spans = [
                    range(match.start(), match.end())
                    for match in HELPERS.MORPHOLOGY_JUMP_RE.finditer(gap)
                ]
                for match in MORPHOLOGY_014C_RE.finditer(gap):
                    row = (
                        block_id,
                        record_id,
                        gap_id,
                        match.start(),
                        struct.unpack("<I", match.group(1))[0],
                    )
                    if any(match.start() in span for span in jump_spans):
                        overlapped.append(row)
                    else:
                        valid.append(row)
        if valid or tuple(overlapped) != EXPECTED_014C_OVERLAP:
            raise RuntimeError(
                f"segment {SEGMENT} {label} 014C evidence drifted"
            )
    evidence = collect_call_evidence(source, current)
    if (
        HELPERS.canonical_sha256(evidence)
        != EXPECTED_CALL_EVIDENCE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} 0143 call/fixed/flatten evidence drifted"
        )
    assert_caller_integration_evidence(source, current)

    chain_gap = gap_bytes(current[(2, 231)])[1]
    chain_targets = tuple(
        struct.unpack("<I", match.group(1))[0]
        for match in HELPERS.MORPHOLOGY_COMMAND_RE.finditer(chain_gap)
    )
    if (
        hashlib.sha256(chain_gap).hexdigest().upper()
        != ROOT940_CHAIN_GAP_SHA256
        or chain_targets != (940, 508)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} root940 fixed command chain drifted"
        )
    return evidence


def assert_boundaries(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    if (
        HELPERS.canonical_sha256(
            tuple(
                literal_texts(source, (BLOCK_ID, record_id))[0]
                for record_id in LEFT_ROOT898_FULL_IDS
            )
        )
        != LEFT_ROOT898_SOURCE_SHA256
        or tuple(
            literal_texts(current, (BLOCK_ID, record_id))[0]
            for record_id in LEFT_ROOT898_FULL_IDS
        )
        != LEFT_ROOT898_FULL_CURRENT
        or LEFT_ROOT898_FULL_POLICY
        != tuple(
            BASE_LEFT.FULL_TRANSLATION_POLICY[record_id - 68]
            for record_id in LEFT_ROOT898_FULL_IDS
        )
        or LEFT_ROOT898_FULL_IDS != LEFT_PK.RIGHT_ROOT898_FULL_IDS
        or LEFT_ROOT898_SOURCE_SHA256
        != LEFT_PK.RIGHT_ROOT898_FULL_SOURCE_SHA256
        or LEFT_ROOT898_FULL_CURRENT
        != LEFT_PK.RIGHT_ROOT898_FULL_CURRENT
        or LEFT_ROOT898_FULL_POLICY
        != LEFT_PK.RIGHT_ROOT898_FULL_POLICY
    ):
        raise RuntimeError(
            f"segment {SEGMENT} left root898 boundary drifted"
        )
    if (
        HELPERS.canonical_sha256(
            tuple(
                literal_texts(source, (BLOCK_ID, record_id))[0]
                for record_id in RIGHT_ROOT940_FULL_IDS
            )
        )
        != RIGHT_ROOT940_SOURCE_SHA256
        or tuple(
            literal_texts(current, (BLOCK_ID, record_id))[0]
            for record_id in RIGHT_ROOT940_FULL_IDS
        )
        != RIGHT_ROOT940_FULL_CURRENT
        or RIGHT_ROOT940_FULL_POLICY
        != tuple(
            BASE_RIGHT.FULL_TRANSLATION_POLICY[record_id - 68]
            for record_id in RIGHT_ROOT940_FULL_IDS
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} right root940 boundary drifted"
        )


def assert_completed_base_policy(
    prepared: Any,
    mapping: dict[int, int],
) -> None:
    rows_by_coordinate: dict[str, dict[str, object]] = {}
    for path, expected_sha256 in BASE_DECISIONS:
        if (
            not path.is_file()
            or hashlib.sha256(path.read_bytes()).hexdigest().upper()
            != expected_sha256
        ):
            raise RuntimeError(
                f"segment {SEGMENT} completed Base decision drifted: "
                f"{path.name}"
            )
        ENGINE.validate_decisions(prepared, path, require_complete=False)
        for line in path.read_text(encoding="utf-8").splitlines():
            if line:
                row = json.loads(line)
                rows_by_coordinate[str(row["coordinate"])] = row
    for pk_record_id, base_record_id in mapping.items():
        row = rows_by_coordinate.get(f"{BLOCK_ID}:{base_record_id}:0")
        if (
            row is None
            or row["resource"] != "base_msggame"
            or row["semantic_review"] != "approved"
            or row["translation"]
            != TRANSLATIONS_BY_RECORD[pk_record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} completed Base policy drifted: "
                f"{base_record_id}"
            )


def assert_semantics(
    translations: dict[str, str],
    mapping: dict[int, int],
) -> None:
    if (
        translations != TRANSLATIONS
        or len(translations) != 67
        or set(TRANSLATIONS_BY_RECORD) != set(RECORD_IDS)
        or set(RECORD_TO_ROOT) != set(RECORD_IDS)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} translation universe drifted"
        )
    for pk_record_id, base_record_id in mapping.items():
        expected = (
            BASE_LEFT.FULL_TRANSLATION_POLICY[base_record_id]
            if base_record_id in BASE_LEFT.FULL_TRANSLATION_POLICY
            else BASE_RIGHT.FULL_TRANSLATION_POLICY[base_record_id]
        )
        if TRANSLATIONS_BY_RECORD[pk_record_id] != expected:
            raise RuntimeError(
                f"segment {SEGMENT} mapped semantic policy drifted: "
                f"{pk_record_id}/{base_record_id}"
            )
    for coordinate, translation in translations.items():
        if (
            not translation
            or "\r" in translation
            or "\n" in translation
            or translation != translation.strip()
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} protected translation drifted: "
                f"{coordinate}"
            )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    translations: dict[str, str],
) -> tuple[bytes, str]:
    resource = prepared.resources["pk_msggame"]
    current = records_by_label["pk_current"]
    replacements = {
        tuple(int(value) for value in coordinate.split(":")): translation
        for coordinate, translation in translations.items()
    }
    reverse = {
        key: literal_texts(current, key[:2])[key[2]]
        for key in replacements
    }
    candidate = ENGINE.rebuild_packed_with_literals(
        resource.current_blob,
        replacements,
    )
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    if (
        len(current) != PK_RECORD_COUNT
        or len(candidate_records) != PK_RECORD_COUNT
        or set(replacements)
        != {(BLOCK_ID, record_id, 0) for record_id in RECORD_IDS}
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate universe drifted"
        )
    target_keys = set(RECORD_KEYS)
    for key, record in current.items():
        if (
            key not in target_keys
            and candidate_records[key].data != record.data
        ):
            raise RuntimeError(
                f"segment {SEGMENT} changed out-of-scope record: {key}"
            )
    for record_id in RECORD_IDS:
        key = (BLOCK_ID, record_id)
        if (
            gap_bytes(candidate_records[key]) != gap_bytes(current[key])
            or literal_texts(candidate_records, key)
            != (TRANSLATIONS_BY_RECORD[record_id],)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} candidate target drifted: {key}"
            )
    if ENGINE.rebuild_packed_with_literals(candidate, reverse) != (
        resource.current_blob
    ):
        raise RuntimeError(
            f"segment {SEGMENT} reverse overlay is not byte-exact"
        )
    return candidate, hashlib.sha256(candidate).hexdigest().upper()


def build_rows() -> tuple[
    Any,
    dict[str, str],
    list[dict[str, object]],
    bytes,
    str,
    int,
]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_queue_contract(prepared)
    records_by_label = archive_records(prepared)
    mapping, offset = discover_mapping(records_by_label)
    assert_source_and_runtime(records_by_label, mapping)
    call_evidence = assert_runtime_graph(records_by_label)
    assert_boundaries(records_by_label)
    assert_completed_base_policy(prepared, mapping)
    translations = dict(TRANSLATIONS)
    assert_semantics(translations, mapping)
    current = records_by_label["pk_current"]
    for coordinate, translation in translations.items():
        _, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        current_text = literal_texts(
            current,
            (BLOCK_ID, record_id),
        )[literal_id]
        if (
            not ENGINE.is_visible_translation_candidate(current_text)
            or UTIL.layout_signature(translation)
            != UTIL.layout_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} protected line drifted: {coordinate}"
            )
    candidate, candidate_sha256 = build_candidate(
        prepared,
        records_by_label,
        translations,
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        root = RECORD_TO_ROOT[record_id]
        evidence = call_evidence[str(root)]
        examples = list(CALLER_INTEGRATION_EVIDENCE.get(root, ()))
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "pk_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target[
                    "source_record_raw_sha256"
                ],
                "current_ko_utf16le_sha256": target[
                    "current_ko_utf16le_sha256"
                ],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "translation_rationale": ROOT_TRANSLATION_RATIONALE[root],
                "source_free_current_caller_evidence": examples,
                "runtime_assembly_evidence": {
                    "root": root,
                    "full_terminal_record_ids": list(
                        FULL_PK_GROUPS[root]
                    ),
                    "owned_terminal_record_ids": [
                        value
                        for value in FULL_PK_GROUPS[root]
                        if value in RECORD_IDS
                    ],
                    "base_semantic_record_discovered_by_reverse_search":
                    mapping[record_id],
                    "source_call_count": evidence[0][0],
                    "current_call_count": evidence[1][0],
                    "source_fixed_following_count": evidence[0][2],
                    "current_fixed_following_count": evidence[1][2],
                    "source_calls_flattened_in_current": evidence[2][0],
                    "current_only_call_count": evidence[2][2],
                    "incoming_jump_graph_guarded": True,
                    "valid_incoming_014c_count": 0,
                    "automatic_space_inserted": False,
                    "runtime_integration_required": True,
                    "caller_rewrite_required_before_runtime_approval": (
                        root != 916
                    ),
                    "assembly_plan": ROOT_ASSEMBLY_PLAN[root],
                    "source_free_caller_integration_examples": examples,
                },
            }
        )
    changed = sum(
        translations[f"{BLOCK_ID}:{record_id}:0"]
        != literal_texts(current, (BLOCK_ID, record_id))[0]
        for record_id in RECORD_IDS
    )
    if changed != EXPECTED_CHANGED_LITERAL_COUNT:
        raise RuntimeError(
            f"segment {SEGMENT} changed count drifted: {changed}"
        )
    return (
        prepared,
        translations,
        rows,
        candidate,
        candidate_sha256,
        offset,
    )


def main() -> int:
    first = build_rows()
    second = build_rows()
    prepared, translations, rows, candidate, candidate_sha256, offset = first
    if (
        translations != second[1]
        or ENGINE.jsonl(rows) != ENGINE.jsonl(second[2])
        or candidate != second[3]
        or candidate_sha256 != second[4]
        or offset != second[5]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} second-run reproduction drifted"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if (
        len(validated) != 67
        or len(rows) != 67
        or any(
            row["scope_classification"] != "runtime_fragment_pending"
            or row["runtime_review"] != "pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            for row in rows
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} decision classification drifted"
        )
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B006_S1040",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [67, 133],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "source_literal_count": len(RECORD_IDS),
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "confirmed_non_display": 0,
                "changed_literal_count": EXPECTED_CHANGED_LITERAL_COUNT,
                "caller_integration_example_class_counts":
                EXPECTED_INTEGRATION_CLASS_COUNTS,
                "base_mapping_method":
                "global_unique_exact67_literal_gap_reverse_search",
                "discovered_base_record_range": [
                    BASE_RECORD_IDS[0],
                    BASE_RECORD_IDS[-1],
                ],
                "discovered_pk_minus_base_offset": offset,
                "source_literal_sha256":
                EXPECTED_SOURCE_LITERAL_SHA256,
                "source_signature_sha256":
                EXPECTED_SOURCE_SIGNATURE_SHA256,
                "base_reverse_map_sha256": EXPECTED_MAPPING_SHA256,
                "translation_policy_sha256": EXPECTED_POLICY_SHA256,
                "pk_target67_incoming_sha256":
                PK_TARGET_INCOMING_SHA256,
                "pk_full70_incoming_sha256":
                PK_FULL_INCOMING_SHA256,
                "pk_call_fixed_flatten_evidence_sha256":
                EXPECTED_CALL_EVIDENCE_SHA256,
                "root940_fixed_chain_gap_sha256":
                ROOT940_CHAIN_GAP_SHA256,
                "valid_incoming_014c_count": 0,
                "left_root898_full_policy":
                list(LEFT_ROOT898_FULL_POLICY),
                "right_root940_full_policy":
                list(RIGHT_ROOT940_FULL_POLICY),
                "candidate_sha256": candidate_sha256,
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
                "tracked_builder_contains_source_dialogue": False,
                "target_runtime_skeleton_exact": True,
                "full_graph_closures_exact": True,
                "root940_fixed_command_chain_exact": True,
                "call_fixed_flatten_evidence_exact": True,
                "source_free_current_caller_evidence_exact": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "both_boundary_full_register_contracts_exact": True,
                "s1039_root898_boundary_contract_exact": True,
                "second_run_reproduction_exact": True,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "steam_write_performed": False,
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
