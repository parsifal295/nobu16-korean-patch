#!/usr/bin/env python3
"""Build source-redacted PK block-0 runtime-terminal segment 1043."""

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

import build_base_batch007_segment1021 as BASE_LEFT
import build_base_batch007_segment1022 as BASE_RIGHT
import build_pk_batch001_segment1025 as HELPERS
import build_pk_batch005_segment1038 as COMMON

try:
    import build_pk_batch007_segment1042 as LEFT_PK
except ModuleNotFoundError:
    LEFT_PK = None


ENGINE = BASE_LEFT.ENGINE
GENERAL = BASE_LEFT.GENERAL
UTIL = BASE_LEFT.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B007_S1043.private.v1.jsonl"
)
BASE_DECISIONS = (
    (
        REPO
        / "tmp"
        / WORKSTREAM.name
        / "decisions"
        / "base_msggame_B007_S1021.private.v1.jsonl",
        "06D3624FCEB68AE1C76B1001985A7E04623340935E407BC2B82AA0865D70DB15",
    ),
    (
        REPO
        / "tmp"
        / WORKSTREAM.name
        / "decisions"
        / "base_msggame_B007_S1022.private.v1.jsonl",
        "29EEFE94FF42CEA83CB8C23D74A14CDCA45C1C70FF9AAC84444909B2D6E26DB8",
    ),
)
SEGMENT = 1043
QUEUE_BATCH_ID = "pk_msggame-B007"
BLOCK_ID = 0
QUEUE_START = 67
QUEUE_STOP = 134
RECORD_IDS = tuple(range(2540, 2607))
BASE_RECORD_IDS = tuple(range(2472, 2539))
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
TARGET_COORDINATES = tuple(
    f"{BLOCK_ID}:{record_id}:0" for record_id in RECORD_IDS
)
QUEUE_HIDDEN_COORDINATES = (
    "0:2638:0",
    "0:2643:0",
    "0:2645:0",
    "0:2650:0",
)
PK_RECORD_COUNT = 21751

FULL_PK_GROUPS = {
    1060: tuple(range(2539, 2546)),
    1066: tuple(range(2546, 2553)),
    1072: tuple(range(2553, 2560)),
    1078: tuple(range(2560, 2567)),
    1084: tuple(range(2567, 2574)),
    1090: tuple(range(2574, 2581)),
    1096: tuple(range(2581, 2588)),
    1102: tuple(range(2588, 2595)),
    1108: tuple(range(2595, 2602)),
    1114: tuple(range(2602, 2609)),
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

# These policies are fixed from pristine-PK call semantics.  The independently
# completed Base rows are checked later as corroborating context only.
ROOT_TRANSLATION_POLICY = {
    1060: (
        "괜찮습니까",
        "괜찮은가",
        "괜찮겠사옵니까",
        "괜찮겠사옵니까",
        "괜찮겠습니까",
        "괜찮겠소",
        "괜찮은가",
    ),
    1066: (
        "하겠습니다",
        "하겠다",
        "하겠사옵니다",
        "하겠사옵니다",
        "하겠습니다",
        "하겠소",
        "하겠다",
    ),
    1072: (
        "좋겠지요",
        "좋겠다",
        "좋겠사옵니다",
        "좋겠사옵니다",
        "좋겠지요",
        "좋겠소",
        "좋겠다",
    ),
    1078: (
        "지 않습니다",
        "지 않는다",
        "지 않습니다",
        "지 않사옵니다",
        "지 않습니다",
        "지 않사옵니다",
        "지 않는다",
    ),
    1084: (
        "수 없습니다",
        "수 없다",
        "수 없사옵니다",
        "수 없사옵니다",
        "수 없습니다",
        "수 없습니다",
        "수 없다",
    ),
    1090: (
        "합니다",
        "한다",
        "합니다",
        "합니다",
        "합니다",
        "합니다",
        "한다",
    ),
    1096: (
        "합니다",
        "한다",
        "하옵니다",
        "하옵니다",
        "합니다",
        "합니다",
        "한다",
    ),
    1102: (
        "지 마십시오",
        "지 마라",
        "지 마십시오",
        "지 마시오",
        "지 마십시오",
        "지 마시오",
        "지 마라",
    ),
    1108: (
        "하십시오",
        "하라",
        "해 주십시오",
        "해 주시오",
        "해 주십시오",
        "하시오",
        "하라",
    ),
    1114: (
        "수 없습니다",
        "수 없다",
        "수 없사옵니다",
        "수 없사옵니다",
        "수 없습니다",
        "수 없사옵니다",
        "수 없다",
    ),
}
TRANSLATIONS_BY_RECORD = {
    record_id: translation
    for root, record_ids in FULL_PK_GROUPS.items()
    for record_id, translation in zip(
        record_ids,
        ROOT_TRANSLATION_POLICY[root],
        strict=True,
    )
    if record_id in RECORD_IDS
}
TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}

EXPECTED_SOURCE_SEQUENCE_SHA256 = (
    "F8A0D754E449A15CA3EA83CB27017E19226DA3231F5B9257DCE6C8502331F87A"
)
EXPECTED_MAPPING_SHA256 = (
    "62AA6051F28E77514196A8F9C4EE3F6CB28EAC3EC0B65D3008590C8DD76670D1"
)
EXPECTED_POLICY_SHA256 = (
    "5668D5D05D775FE57D58353F972EF83239173E2B5769A5BFBD38AB0B0F0C89DC"
)
EXPECTED_CHANGED_LITERAL_COUNT = 52

PK_TARGET_ARCHIVE_DIGESTS = {
    "pk_jp": "79F6635AB9CCDBA294DF712CC748EABD033BCFC7920BC7BE0E114F7D37D424AE",
    "pk_current": "7D5DE87C03F83C8030A8818D70B5FFC233E4F17F6934CE37507E5C6108E6254F",
    "pk_sc": "66286EEDA944631F46A9B94BF38DC4EA277438972631C4039ED53AC6D24A8DA7",
    "pk_tc": "66286EEDA944631F46A9B94BF38DC4EA277438972631C4039ED53AC6D24A8DA7",
    "pk_en": "66286EEDA944631F46A9B94BF38DC4EA277438972631C4039ED53AC6D24A8DA7",
}
PK_FULL_ARCHIVE_DIGESTS = {
    "pk_jp": "F58BA8D788247821A98BD17852818BE59CC189B4424E6B91B9D931F32EA3AEDA",
    "pk_current": "7AB62FD72772CDF1961D7E478E431803463F6C52FCC16C4BFE99073FC3407127",
    "pk_sc": "A04F1E6AEA1ADB6A8B0C5152F5731F165517A0B9FC7E9C81F78B6E0DEB650B5C",
    "pk_tc": "A04F1E6AEA1ADB6A8B0C5152F5731F165517A0B9FC7E9C81F78B6E0DEB650B5C",
    "pk_en": "A04F1E6AEA1ADB6A8B0C5152F5731F165517A0B9FC7E9C81F78B6E0DEB650B5C",
}
PK_TARGET_JUMP_EDGE_SHA256 = (
    "A68374927726D4638C14C963A4072087C0765939671AA08A77AEFD992C27E3DF"
)
PK_FULL_GROUP_JUMP_EDGE_SHA256 = (
    "11D1F5CAA819C76AD9D70124DBDA618A7522DDB57407C216B7029DCB189EC5E0"
)
EXPECTED_CALL_EVIDENCE_SHA256 = (
    "6E7EFF59552ED010386536B65E824F174886C66CB0AB58F5C80E96F4CB7FF2F9"
)
EXPECTED_CALLER_CONTEXT_SHA256 = (
    "C35D98F9B8C67C5D039B13E0C3BCE8D34F2C8BF47F585383CD9E8AFEA391688F"
)
MORPHOLOGY_014C_RE = re.compile(b"\x01\x4C(.{4})", re.DOTALL)
EXPECTED_014C_OVERLAP = ((15, 25, 0, 65, 84213762),)

LEFT_BOUNDARY_IDS = FULL_PK_GROUPS[1060]
LEFT_BOUNDARY_SOURCE_SHA256 = (
    "64F508B5CA5680159C99E58C456556A5CD4692E636D39770AE9EAA965E234D9F"
)
LEFT_BOUNDARY_CURRENT_SHA256 = (
    "3D177D5993938B707FF158D2F208CBB4E39EF62C44A6E0DDC02A94EAB676393C"
)
LEFT_BOUNDARY_CURRENT = (
    "괜찮은가",
    "좋은가",
    "괜찮으시겠습니까",
    "괜찮으시겠습니까",
    "괜찮을까요",
    "괜찮으시겠소",
    "좋은가",
)
LEFT_BOUNDARY_POLICY = ROOT_TRANSLATION_POLICY[1060]

RIGHT_ROOT1114_FULL_IDS = FULL_PK_GROUPS[1114]
RIGHT_ROOT1114_FULL_SOURCE_SHA256 = (
    "7C276D2D7DAE101732F09212433DB482D2DFB7FAD07037E27F4077351B123D3F"
)
RIGHT_ROOT1114_FULL_CURRENT = (
    "할 수 없습니다",
    "할 수 없",
    "할 수 없습니다",
    "할 수 없습니다",
    "할 수 없습니다",
    "할 수 없습니다",
    "할 수 없",
)
RIGHT_ROOT1114_FULL_POLICY = ROOT_TRANSLATION_POLICY[1114]
RIGHT_BOUNDARY_IDS = RIGHT_ROOT1114_FULL_IDS
RIGHT_BOUNDARY_SOURCE_SHA256 = RIGHT_ROOT1114_FULL_SOURCE_SHA256
RIGHT_BOUNDARY_CURRENT_SHA256 = (
    "7C3E1F4F752F60A6D9F25A8970B721F31205A7087E3DBC8EF615B1113893FFB8"
)
RIGHT_BOUNDARY_CURRENT = RIGHT_ROOT1114_FULL_CURRENT
RIGHT_BOUNDARY_POLICY = RIGHT_ROOT1114_FULL_POLICY

ROOT_TRANSLATION_RATIONALE = {
    1060: (
        "Permission and acceptability questions retain neutral, plain, "
        "courtly, and period interrogative voices."
    ),
    1066: (
        "The shared volitional family is most safely represented as speaker "
        "intent; completed hortatives, predictions, and questions are "
        "flattened at their callers."
    ),
    1072: (
        "Recommendation and conjecture require a seven-voice judgment "
        "matrix, with courtly and period forms preserved."
    ),
    1078: (
        "The productive consonant-stem negative must attach to a normalized "
        "lexical predicate without an inserted space."
    ),
    1084: (
        "The negative-potential family retains ability semantics and "
        "requires caller stems to be rewritten before attachment."
    ),
    1090: (
        "The productive affirmative family must not collapse receiving, "
        "granting, governing, and utilization into one lexical action."
    ),
    1096: (
        "The second affirmative family preserves courtly forms while "
        "benefactive, honorific, and already-complete callers are flattened."
    ),
    1102: (
        "The prohibitive family removes duplicated light verbs and retains "
        "polite, plain, and period command distinctions."
    ),
    1108: (
        "The positive command family distinguishes direct commands from "
        "benefactive requests across all seven voices."
    ),
    1114: (
        "The negative-potential family is retained for true inability; "
        "epistemic and already-complete callers are flattened separately."
    ),
}
ROOT_ASSEMBLY_PLAN = {
    1060: (
        "rewrite the caller to an acceptability phrase and add an explicit "
        "boundary before the selected interrogative terminal"
    ),
    1066: (
        "normalize action callers to a compatible action noun before the "
        "intent terminal; flatten completed hortative or predictive callers"
    ),
    1072: (
        "insert an explicit boundary before the judgment terminal or "
        "flatten callers that already contain a complete conclusion"
    ),
    1078: (
        "attach the bound negative directly to a normalized lexical stem; "
        "rewrite fixed following text and completed callers jointly"
    ),
    1084: (
        "rewrite the lexical caller to a compatible attributive stem before "
        "the negative-potential terminal"
    ),
    1090: (
        "select a precise Korean action noun for receiving, granting, "
        "governing, or using before the generic affirmative terminal"
    ),
    1096: (
        "normalize simple actions before the affirmative terminal and "
        "flatten benefactive, honorific, or completed constructions"
    ),
    1102: (
        "attach the prohibitive terminal to a bare verb stem or flatten a "
        "caller that already contains the complete prohibition"
    ),
    1108: (
        "retain the selected command after a Korean action stem and jointly "
        "normalize the remaining chained commands"
    ),
    1114: (
        "rewrite true inability callers before the potential terminal and "
        "flatten epistemic or already-complete constructions"
    ),
}

CALLER_INTEGRATION_EVIDENCE = {
    1060: (
        {
            "call_site": "7:2437:2:0",
            "observed_current_left": "\n귀환하더라도",
            "observed_current_right": "",
            "expected_current_gap_hex": "014324040000050505",
            "integration_mode": "insert_boundary_retain_question_terminal",
            "source_free_korean_example": "\n귀환해도 괜찮은가",
        },
    ),
    1066: (
        {
            "call_site": "2:137:3:0",
            "observed_current_left": "기대에는 부응해 보이",
            "observed_current_right": "",
            "expected_current_gap_hex":
            "01432A0400000143FC010000050505",
            "integration_mode": "normalize_action_retain_intent_terminal",
            "source_free_korean_example": "기대에 부응하겠습니다",
        },
        {
            "call_site": "13:122:2:0",
            "source_only": True,
            "observed_current_literals": (
                "특별한 특성은 없으나,\n"
                "그 능력을 살릴 수 있는 곳에서 일하게 하면\n"
                "반드시 활약할 수 있습니다.",
            ),
            "observed_current_gaps_hex": ("", "050505"),
            "integration_mode":
            "source_only_utilization_call_flattened_in_current",
            "source_free_korean_example": (
                "그 능력을 살릴 수 있는 곳에서 일하게 하면\n"
                "반드시 활약할 수 있습니다."
            ),
        },
        {
            "call_site": "15:2237:1:0",
            "source_only": True,
            "observed_current_literals": (
                "귀한 분부를 받들게 되었으니\n"
                "제 문무의 진수를 보여 드리겠습니다.",
            ),
            "observed_current_gaps_hex": ("", "050505"),
            "integration_mode":
            "source_only_received_order_call_flattened_in_current",
            "source_free_korean_example": (
                "귀한 분부를 받들게 되었으니\n"
                "제 문무의 진수를 보여 드리겠습니다."
            ),
        },
        {
            "call_site": "15:266:1:0",
            "source_only": True,
            "observed_current_literals": (
                "외람되오나 잠시 귀를 빌리겠소!\n"
                "여기서는 상인의 지혜를 빌려드리겠으니",
                "\n돈이 힘을 쓰는 것이 전국의 세상이지요.",
            ),
            "observed_current_gaps_hex": ("", "", "050505"),
            "integration_mode":
            "source_only_benefactive_call_flattened_in_current",
            "source_free_korean_example": (
                "상인의 지혜를 빌려 드리겠으니\n"
                "전국시대에는 돈이 힘을 발휘하지요."
            ),
        },
    ),
    1072: (
        {
            "call_site": "15:2386:3:0",
            "observed_current_left": (
                "\n자원이 풍부한 타가와의 외교나\n"
                "농촌을 가진 군을 우수한 무장에게 맡기는 등\n"
                "잘 꾸려 나가는 것이"
            ),
            "observed_current_right": "",
            "expected_current_gap_hex": "014330040000050505",
            "integration_mode": "insert_boundary_retain_judgment_terminal",
            "source_free_korean_example": (
                "자원이 풍부한 타가와 교섭하거나\n"
                "농촌을 우수한 무장에게 맡겨 잘 꾸리는 것이 좋겠지요"
            ),
        },
        {
            "call_site": "13:87:1:0",
            "source_only": True,
            "observed_current_literals": (
                "우선 본거지에 속한 군의 대관으로서\n"
                "공훈을 세워 신분을 올린 뒤\n"
                "지행지를 맡기는 것이 좋겠습니다.",
            ),
            "observed_current_gaps_hex": ("", "050505"),
            "integration_mode":
            "source_only_complete_judgment_flattened_in_current",
            "source_free_korean_example": (
                "공훈을 세워 신분을 올린 뒤\n"
                "지행지를 맡기는 것이 좋겠습니다."
            ),
        },
        {
            "call_site": "2:258:1:0",
            "observed_current_left": (
                "대가 자랑하는 철포의 위력\n뼈저리게 알게 되리라"
            ),
            "observed_current_right": "！",
            "expected_current_gap_hex": "014330040000",
            "integration_mode":
            "flatten_complete_conclusion_and_normalize_punctuation",
            "source_free_korean_example": (
                "대가 자랑하는 철포의 위력을\n뼈저리게 알게 되리라!"
            ),
        },
    ),
    1078: (
        {
            "call_site": "6:3408:4:0",
            "observed_current_left": "의 기대는 저버리",
            "observed_current_right": "",
            "expected_current_gap_hex":
            "0143360400000143FC010000050505",
            "integration_mode": "direct_bound_negative_composition",
            "source_free_korean_example": "의 기대는 저버리지 않습니다",
        },
        {
            "call_site": "15:2395:3:0",
            "observed_current_left": (
                "\n싸움이나 흉작에 대비해 아무리 있어도 곤란하지 않"
            ),
            "observed_current_right": (
                "이(가)\n필요에 따라 거래에 쓰는 것도 한 방법일 듯합니다"
            ),
            "expected_current_gap_hex": "014336040000",
            "integration_mode":
            "rewrite_utilization_caller_and_fixed_following",
            "source_free_korean_example": (
                "싸움이나 흉작에 대비해 아무리 많아도 문제되지 않으며,\n"
                "필요하면 거래에 활용하는 것도 한 방법일 듯합니다"
            ),
        },
        {
            "call_site": "6:1558:2:0",
            "source_only": True,
            "observed_current_literals": (
                "당가가",
                " 측과 단교하게 되었으니\n"
                "여러 나라가 우리를 가만두지 않을 터.\n"
                "철저히 대비해야 합니다",
            ),
            "observed_current_gaps_hex": ("", "025032", "050505"),
            "integration_mode":
            "source_only_complete_negative_flattened_in_current",
            "source_free_korean_example": (
                "여러 나라가 우리를 가만두지 않을 터.\n"
                "철저히 대비해야 합니다"
            ),
        },
    ),
    1084: (
        {
            "call_site": "15:270:2:0",
            "observed_current_left": "\n이런 대사를 속된 무리에게 맡기",
            "observed_current_right": "\n이곳은 귀한 혈통이신",
            "expected_current_gap_hex": "01433C040000",
            "integration_mode":
            "normalize_attributive_retain_negative_potential",
            "source_free_korean_example": (
                "이런 대사를 속된 무리에게 맡길 수 없습니다\n"
                "이곳은 귀한 혈통이신"
            ),
        },
        {
            "call_site": "15:1618:1:0",
            "source_only": True,
            "observed_current_literals": (
                "한 나라의 지배에 만족해선 안 됩니다.",
                "\n다음 나라를 공격하기 위한 거점으로\n"
                "발전시켜 나가야 합니다.",
            ),
            "observed_current_gaps_hex": ("", "", "050505"),
            "integration_mode":
            "source_only_complete_inability_flattened_in_current",
            "source_free_korean_example": (
                "한 나라의 지배에 만족해선 안 됩니다.\n"
                "다음 나라를 공격할 거점으로 발전시켜야 합니다."
            ),
        },
    ),
    1090: (
        {
            "call_site": "6:3515:1:0",
            "observed_current_left": "훈공 1위, 황송히 받",
            "observed_current_right": "！\n",
            "expected_current_gap_hex": "014342040000",
            "integration_mode":
            "rewrite_receipt_action_and_normalize_punctuation",
            "source_free_korean_example": "훈공 1위, 황송히 수령합니다!\n",
        },
        {
            "call_site": "6:4423:3:0",
            "observed_current_left": (
                "군입니다\n새로운 영지를 하사하"
            ),
            "observed_current_right": "인가?",
            "expected_current_gap_hex": "014342040000",
            "integration_mode":
            "flatten_grant_question_and_fixed_following",
            "source_free_korean_example": (
                "군입니다\n새로운 영지를 하사하시겠습니까?"
            ),
        },
        {
            "call_site": "15:2570:4:0",
            "observed_current_left": "성은 우리 가문이 통치하고",
            "observed_current_right": "",
            "expected_current_gap_hex": "014342040000050505",
            "integration_mode":
            "normalize_governing_action_retain_affirmative",
            "source_free_korean_example": "성은 우리 가문이 통치합니다",
        },
        {
            "call_site": "13:106:1:0",
            "source_only": True,
            "observed_current_literals": (
                "또한 통솔력이 뛰어나므로\n"
                "군의 발전과 전쟁에서도 든든한 도움이 될 것입니다.",
            ),
            "observed_current_gaps_hex": ("", "050505"),
            "integration_mode":
            "source_only_benefit_result_flattened_in_current",
            "source_free_korean_example": (
                "통솔력이 뛰어나므로\n"
                "군의 발전과 전쟁에서도 든든한 도움이 될 것입니다."
            ),
        },
    ),
    1096: (
        {
            "call_site": "2:573:2:0",
            "observed_current_left": "무운을\n빌어 드리",
            "observed_current_right": "",
            "expected_current_gap_hex": "014348040000050505",
            "integration_mode": "flatten_benefactive_prayer_caller",
            "source_free_korean_example": "무운을\n빌어 드립니다",
        },
        {
            "call_site": "6:4217:1:0",
            "source_only": True,
            "observed_current_literals": (
                "강한 불만을 품은 무장에게\n"
                "당가로 돌아서도록 권유합니다.",
            ),
            "observed_current_gaps_hex": ("", "050505"),
            "integration_mode":
            "source_only_complete_action_flattened_in_current",
            "source_free_korean_example": (
                "강한 불만을 품은 무장에게\n"
                "당가로 돌아서도록 권유합니다."
            ),
        },
        {
            "call_site": "15:2248:1:0",
            "source_only": True,
            "observed_current_literals": (
                "적 부대를 협격하면\n큰 피해를 입힐 수 있습니다.",
            ),
            "observed_current_gaps_hex": ("", "050505"),
            "integration_mode":
            "source_only_effect_result_flattened_in_current",
            "source_free_korean_example": (
                "적 부대를 협격하면\n큰 피해를 입힐 수 있습니다."
            ),
        },
    ),
    1102: (
        {
            "call_site": "1:28:1:0",
            "observed_current_left": "11년 10월 3일을 잊",
            "observed_current_right": "。",
            "expected_current_gap_hex": "01434E040000",
            "integration_mode":
            "direct_prohibitive_and_normalize_punctuation",
            "source_free_korean_example":
            "11년 10월 3일을 잊지 마십시오.",
        },
        {
            "call_site": "2:409:1:0",
            "observed_current_left": (
                "지금이 승부처다!\n모두, 포기하지 마라"
            ),
            "observed_current_right": "！",
            "expected_current_gap_hex": "01434E040000",
            "integration_mode":
            "flatten_complete_prohibition_and_normalize_punctuation",
            "source_free_korean_example": (
                "지금이 승부처다!\n모두, 포기하지 마라!"
            ),
        },
    ),
    1108: (
        {
            "call_site": "6:4210:1:0",
            "observed_current_left": "에 착수하",
            "observed_current_right": "\n공을 세운 자에게는 포상을 내려",
            "expected_current_gap_hex": "014354040000",
            "integration_mode":
            "retain_command_and_rewrite_remaining_chain",
            "source_free_korean_example": (
                "에 착수하십시오\n"
                "공을 세운 자에게는 포상을 내릴 것이니\n"
                "모두 힘쓰십시오"
            ),
        },
    ),
    1114: (
        {
            "call_site": "9:3991:1:0",
            "observed_current_left": (
                "좋은 적과 싸우기를\n지금부터 기다리기 어렵"
            ),
            "observed_current_right": "",
            "expected_current_gap_hex": "01435A040000050505",
            "integration_mode":
            "normalize_true_inability_retain_potential_terminal",
            "source_free_korean_example": (
                "좋은 적과 싸울 때를\n더는 기다릴 수 없습니다"
            ),
        },
        {
            "call_site": "15:1539:2:0",
            "observed_current_left": (
                "\n더 넓은 인맥을 지닌 자라면\n찾아낼 수 있을지도"
            ),
            "observed_current_right": "",
            "expected_current_gap_hex": "01435A040000050505",
            "integration_mode": "flatten_epistemic_possibility_caller",
            "source_free_korean_example": (
                "더 넓은 인맥을 지닌 자라면\n"
                "찾아낼 수 있을지도 모릅니다"
            ),
        },
        {
            "call_site": "15:261:3:0",
            "source_only": True,
            "observed_current_literals": (
                "인재를 빼내는 방안은 다소 위험하지만",
                "\n연고자를 내세워 권유한다면",
                "\n잘되면 모두 함께 돌아설지도 모릅니다.",
            ),
            "observed_current_gaps_hex": ("", "", "", "050505"),
            "integration_mode":
            "source_only_epistemic_call_flattened_in_current",
            "source_free_korean_example": (
                "연고자를 내세워 권유한다면\n"
                "잘되면 모두 함께 돌아설지도 모릅니다."
            ),
        },
    ),
}
EXPECTED_INTEGRATION_CLASS_COUNTS = dict(
    Counter(
        str(example["integration_mode"])
        for examples in CALLER_INTEGRATION_EVIDENCE.values()
        for example in examples
    )
)

BASIS = (
    "pristine PK source is the sole translation authority; source text is "
    "redacted from this tracked builder; unique global literal-gap reverse "
    "search discovers the Base context range and offset; exact target and "
    "full archive digests, incoming jump closures, all actual source and "
    "current caller contexts, fixed following text, source-only and "
    "current-only deltas are guarded; seven-voice history-aware policies "
    "distinguish receiving, granting, benefiting, governing, and utilizing; "
    "caller assembly never assumes an automatic space; left and right full "
    "boundary policies, skeleton, outside scope, reverse overlay, two-run "
    "reproduction, source redaction, and Steam read-only state are checked"
)


literal_texts = COMMON.literal_texts
gap_bytes = COMMON.gap_bytes
archive_records = COMMON.archive_records
record_signature = COMMON.record_signature
sequence_starts = COMMON.sequence_starts
incoming_jump_rows = COMMON.incoming_jump_rows


def caller_context(
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


def call_context_rows(
    records: dict[tuple[int, int], Any],
    root: int,
) -> tuple[tuple[str, str, str, str], ...]:
    return tuple(
        (site, *caller_context(records, site))
        for site in HELPERS.root_call_sites(records, root)
    )


def assert_tracked_builder_source_redacted() -> None:
    tracked_text = SCRIPT.read_text(encoding="utf-8")
    if ENGINE.KANA_OR_HAN_RE.search(tracked_text):
        raise RuntimeError(
            f"segment {SEGMENT} tracked builder contains source text"
        )


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
        len(rows) != 204
        or len(visible) != 200
        or hidden != QUEUE_HIDDEN_COORDINATES
        or visible[QUEUE_START:QUEUE_STOP] != TARGET_COORDINATES
        or rows[0]["record_coordinate"] != "0:2473"
        or rows[-1]["record_coordinate"] != "0:2676"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} private queue ordinal contract drifted"
        )


def discover_mapping(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[dict[int, int], int]:
    source_sequence = tuple(
        record_signature(records_by_label["pk_jp"], record_id)
        for record_id in RECORD_IDS
    )
    if (
        HELPERS.canonical_sha256(source_sequence)
        != EXPECTED_SOURCE_SEQUENCE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} pristine source sequence drifted"
        )
    base_hits = sequence_starts(
        records_by_label["base_jp"],
        source_sequence,
    )
    pk_hits = sequence_starts(
        records_by_label["pk_jp"],
        source_sequence,
    )
    if base_hits != (2472,) or pk_hits != (2540,):
        raise RuntimeError(
            f"segment {SEGMENT} global source reverse search drifted: "
            f"{base_hits}/{pk_hits}"
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
    full_keys = tuple(
        (BLOCK_ID, record_id) for record_id in range(2539, 2609)
    )
    for label, target_digest in PK_TARGET_ARCHIVE_DIGESTS.items():
        if (
            GENERAL.subset_digest(records_by_label[label], RECORD_KEYS)
            != target_digest
            or GENERAL.subset_digest(records_by_label[label], full_keys)
            != PK_FULL_ARCHIVE_DIGESTS[label]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} independent {label} digest drifted"
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
                    f"segment {SEGMENT} PK/Base auxiliary {language} "
                    f"mapping drifted: {pk_key}/{base_key}"
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


def assert_caller_integration_evidence(
    source: dict[tuple[int, int], Any],
    current: dict[tuple[int, int], Any],
) -> None:
    if set(CALLER_INTEGRATION_EVIDENCE) != set(FULL_PK_GROUPS):
        raise RuntimeError(
            f"segment {SEGMENT} caller example root coverage drifted"
        )
    class_counts: Counter[str] = Counter()
    for root, examples in CALLER_INTEGRATION_EVIDENCE.items():
        source_calls = set(HELPERS.root_call_sites(source, root))
        current_calls = set(HELPERS.root_call_sites(current, root))
        for example in examples:
            call_site = str(example["call_site"])
            class_counts[str(example["integration_mode"])] += 1
            if bool(example.get("source_only")):
                if (
                    call_site not in source_calls
                    or call_site in current_calls
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} source-only caller drifted: "
                        f"{root}/{call_site}"
                    )
                block_id, record_id, _, _ = (
                    int(value) for value in call_site.split(":")
                )
                record = current[(block_id, record_id)]
                actual_literals = tuple(
                    literal.text
                    for literal in ENGINE.parse_record_literals(record)
                )
                actual_gaps = tuple(
                    value.hex().upper() for value in gap_bytes(record)
                )
                if (
                    actual_literals
                    != tuple(example["observed_current_literals"])
                    or actual_gaps
                    != tuple(example["observed_current_gaps_hex"])
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} source-only current record "
                        f"drifted: {root}/{call_site}"
                    )
            else:
                if call_site not in current_calls:
                    raise RuntimeError(
                        f"segment {SEGMENT} live caller drifted: "
                        f"{root}/{call_site}"
                    )
                left, right, gap = caller_context(current, call_site)
                if (
                    left != example["observed_current_left"]
                    or right != example["observed_current_right"]
                    or gap != example["expected_current_gap_hex"]
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} live caller context drifted: "
                        f"{root}/{call_site}"
                    )
            source_free = str(example["source_free_korean_example"])
            if (
                ENGINE.KANA_OR_HAN_RE.search(source_free)
                or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(
                    source_free
                )
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} caller example is not "
                    f"source-free Korean: {root}/{call_site}"
                )
    if dict(class_counts) != EXPECTED_INTEGRATION_CLASS_COUNTS:
        raise RuntimeError(
            f"segment {SEGMENT} caller integration classes drifted"
        )


def assert_runtime_graph(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[
    dict[str, tuple[tuple[int | str, ...], ...]],
    dict[str, dict[str, tuple[tuple[str, str, str, str], ...]]],
]:
    target_ids = set(RECORD_IDS)
    full_ids = {
        record_id
        for record_ids in FULL_PK_GROUPS.values()
        for record_id in record_ids
    }
    if full_ids != set(range(2539, 2609)):
        raise RuntimeError(
            f"segment {SEGMENT} full PK group universe drifted"
        )
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    for label, records in (
        ("pk_jp", source),
        ("pk_current", current),
    ):
        target_edges = incoming_jump_rows(records, target_ids)
        full_edges = incoming_jump_rows(records, full_ids)
        if (
            len(target_edges) != 67
            or {row[4] for row in target_edges} != target_ids
            or HELPERS.canonical_sha256(target_edges)
            != PK_TARGET_JUMP_EDGE_SHA256
            or len(full_edges) != 70
            or {row[4] for row in full_edges} != full_ids
            or HELPERS.canonical_sha256(full_edges)
            != PK_FULL_GROUP_JUMP_EDGE_SHA256
        ):
            raise RuntimeError(
                f"segment {SEGMENT} independent {label} "
                "incoming graph drifted"
            )
        graph = HELPERS.graph_edges(records)
        for root, expected_closure in EXPECTED_ROOT_CLOSURES.items():
            if tuple(
                sorted(HELPERS.graph_closure(graph, root))
            ) != expected_closure:
                raise RuntimeError(
                    f"segment {SEGMENT} independent {label} "
                    f"closure drifted: {root}"
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
                f"segment {SEGMENT} independent {label} "
                "014C evidence drifted"
            )

    call_evidence = collect_call_evidence(source, current)
    if (
        HELPERS.canonical_sha256(call_evidence)
        != EXPECTED_CALL_EVIDENCE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} independent PK call evidence drifted"
        )
    context_evidence = {
        "source": {
            str(root): call_context_rows(source, root)
            for root in FULL_PK_GROUPS
        },
        "current": {
            str(root): call_context_rows(current, root)
            for root in FULL_PK_GROUPS
        },
    }
    if (
        HELPERS.canonical_sha256(context_evidence)
        != EXPECTED_CALLER_CONTEXT_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} caller context digest drifted"
        )
    assert_caller_integration_evidence(source, current)
    BASE_LEFT.assert_corpora(records_by_label)
    BASE_LEFT.assert_runtime_graph(records_by_label)
    BASE_RIGHT.assert_corpora(records_by_label)
    BASE_RIGHT.assert_runtime_graph(records_by_label)
    return call_evidence, context_evidence


def assert_boundaries(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> bool:
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    actual_left_source = tuple(
        literal_texts(source, (BLOCK_ID, record_id))[0]
        for record_id in LEFT_BOUNDARY_IDS
    )
    actual_left_current = tuple(
        literal_texts(current, (BLOCK_ID, record_id))[0]
        for record_id in LEFT_BOUNDARY_IDS
    )
    actual_right_source = tuple(
        literal_texts(source, (BLOCK_ID, record_id))[0]
        for record_id in RIGHT_BOUNDARY_IDS
    )
    actual_right_current = tuple(
        literal_texts(current, (BLOCK_ID, record_id))[0]
        for record_id in RIGHT_BOUNDARY_IDS
    )
    if (
        HELPERS.canonical_sha256(actual_left_source)
        != LEFT_BOUNDARY_SOURCE_SHA256
        or HELPERS.canonical_sha256(actual_left_current)
        != LEFT_BOUNDARY_CURRENT_SHA256
        or actual_left_current != LEFT_BOUNDARY_CURRENT
        or HELPERS.canonical_sha256(actual_right_source)
        != RIGHT_BOUNDARY_SOURCE_SHA256
        or HELPERS.canonical_sha256(actual_right_current)
        != RIGHT_BOUNDARY_CURRENT_SHA256
        or actual_right_current != RIGHT_BOUNDARY_CURRENT
    ):
        raise RuntimeError(
            f"segment {SEGMENT} independent boundary digest drifted"
        )
    base_policy = {
        **BASE_LEFT.FULL_TRANSLATION_POLICY,
        **BASE_RIGHT.FULL_TRANSLATION_POLICY,
    }
    if (
        LEFT_BOUNDARY_POLICY
        != tuple(
            base_policy[record_id - 68]
            for record_id in LEFT_BOUNDARY_IDS
        )
        or RIGHT_BOUNDARY_POLICY
        != tuple(
            base_policy[record_id - 68]
            for record_id in RIGHT_BOUNDARY_IDS
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} auxiliary Base boundary drifted"
        )

    imported = False
    required = (
        "RIGHT_ROOT1060_FULL_IDS",
        "RIGHT_ROOT1060_FULL_SOURCE_SHA256",
        "RIGHT_ROOT1060_FULL_CURRENT",
        "RIGHT_ROOT1060_FULL_POLICY",
    )
    if LEFT_PK is not None and all(
        hasattr(LEFT_PK, name) for name in required
    ):
        imported = True
        if (
            LEFT_BOUNDARY_IDS != LEFT_PK.RIGHT_ROOT1060_FULL_IDS
            or LEFT_BOUNDARY_SOURCE_SHA256
            != LEFT_PK.RIGHT_ROOT1060_FULL_SOURCE_SHA256
            or LEFT_BOUNDARY_CURRENT
            != LEFT_PK.RIGHT_ROOT1060_FULL_CURRENT
            or LEFT_BOUNDARY_POLICY
            != LEFT_PK.RIGHT_ROOT1060_FULL_POLICY
        ):
            raise RuntimeError(
                f"segment {SEGMENT} S1042 root1060 boundary drifted"
            )
    return imported


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
        row = rows_by_coordinate.get(
            f"{BLOCK_ID}:{base_record_id}:0"
        )
        if (
            row is None
            or row["resource"] != "base_msggame"
            or row["semantic_review"] != "approved"
            or row["translation"]
            != TRANSLATIONS_BY_RECORD[pk_record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} completed Base context drifted: "
                f"{base_record_id}"
            )


def assert_semantics(translations: dict[str, str]) -> None:
    if (
        translations != TRANSLATIONS
        or len(translations) != 67
        or set(TRANSLATIONS_BY_RECORD) != set(RECORD_IDS)
        or set(RECORD_TO_ROOT) != set(RECORD_IDS)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} translation universe drifted"
        )
    base_policy = {
        **BASE_LEFT.FULL_TRANSLATION_POLICY,
        **BASE_RIGHT.FULL_TRANSLATION_POLICY,
    }
    for pk_record_id, translation in TRANSLATIONS_BY_RECORD.items():
        if translation != base_policy[pk_record_id - 68]:
            raise RuntimeError(
                f"segment {SEGMENT} auxiliary Base policy diverged: "
                f"{pk_record_id}"
            )
    for coordinate, translation in translations.items():
        if (
            "\r" in translation
            or "\n" in translation
            or translation != translation.strip()
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} text residue drifted: {coordinate}"
            )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    translations: dict[str, str],
) -> tuple[bytes, str]:
    resource = prepared.resources["pk_msggame"]
    current = records_by_label["pk_current"]
    replacements = {
        (BLOCK_ID, record_id, 0): translations[
            f"{BLOCK_ID}:{record_id}:0"
        ]
        for record_id in RECORD_IDS
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
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate record universe drifted"
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
    bool,
]:
    assert_tracked_builder_source_redacted()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_queue_contract(prepared)
    records_by_label = archive_records(prepared)
    mapping, offset = discover_mapping(records_by_label)
    assert_source_and_runtime(records_by_label, mapping)
    call_evidence, _ = assert_runtime_graph(records_by_label)
    left_imported = assert_boundaries(records_by_label)
    assert_completed_base_policy(prepared, mapping)
    translations = dict(TRANSLATIONS)
    assert_semantics(translations)

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
                f"segment {SEGMENT} protected line drifted: "
                f"{coordinate}"
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
                "translation_rationale":
                ROOT_TRANSLATION_RATIONALE[root],
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
                    "base_context_record_discovered_by_reverse_search":
                    mapping[record_id],
                    "source_call_count": evidence[0][0],
                    "current_call_count": evidence[1][0],
                    "source_fixed_following_count": evidence[0][2],
                    "current_fixed_following_count": evidence[1][2],
                    "source_calls_flattened_in_current": evidence[2][0],
                    "current_only_call_count": evidence[2][2],
                    "owned_operand_has_exactly_one_incoming_014a": True,
                    "full_root_graph_closure_guarded": True,
                    "all_actual_caller_contexts_guarded": True,
                    "valid_incoming_014c_count": 0,
                    "automatic_space_inserted": False,
                    "runtime_integration_required": True,
                    "caller_rewrite_required_before_runtime_approval": True,
                    "assembly_plan": ROOT_ASSEMBLY_PLAN[root],
                    "source_free_caller_integration_examples": list(
                        CALLER_INTEGRATION_EVIDENCE[root]
                    ),
                    "auxiliary_base_policy_diverged": False,
                    "auxiliary_base_divergence_reason": "",
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
        left_imported,
    )


def main() -> int:
    first = build_rows()
    second = build_rows()
    (
        prepared,
        translations,
        rows,
        candidate,
        candidate_sha256,
        offset,
        left_imported,
    ) = first
    if (
        translations != second[1]
        or ENGINE.jsonl(rows) != ENGINE.jsonl(second[2])
        or candidate != second[3]
        or candidate_sha256 != second[4]
        or offset != second[5]
        or left_imported != second[6]
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
        or prepared.resources["pk_msggame"].current_path.read_bytes()
        != prepared.resources["pk_msggame"].current_blob
    ):
        raise RuntimeError(
            f"segment {SEGMENT} final validation drifted"
        )
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B007_S1043",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [67, 133],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "source_literal_count": 67,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "confirmed_non_display": 0,
                "changed_literal_count": EXPECTED_CHANGED_LITERAL_COUNT,
                "base_mapping_method":
                "global_unique_contiguous_literal_gap_reverse_search",
                "discovered_base_record_range": [2472, 2538],
                "discovered_pk_minus_base_offset": offset,
                "source_sequence_sha256":
                EXPECTED_SOURCE_SEQUENCE_SHA256,
                "translation_policy_sha256":
                EXPECTED_POLICY_SHA256,
                "source_justified_base_divergence_record_ids": [],
                "pk_target_incoming_sha256":
                PK_TARGET_JUMP_EDGE_SHA256,
                "pk_full_group_incoming_sha256":
                PK_FULL_GROUP_JUMP_EDGE_SHA256,
                "pk_call_fixed_flatten_evidence_sha256":
                EXPECTED_CALL_EVIDENCE_SHA256,
                "pk_all_caller_context_sha256":
                EXPECTED_CALLER_CONTEXT_SHA256,
                "valid_incoming_014c_count": 0,
                "left_root1060_full_policy":
                list(LEFT_BOUNDARY_POLICY),
                "left_root1060_independent_contract_exact": True,
                "s1042_root1060_boundary_import_available":
                left_imported,
                "right_root1114_full_policy":
                list(RIGHT_ROOT1114_FULL_POLICY),
                "candidate_sha256": candidate_sha256,
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
                "tracked_builder_source_text_redacted": True,
                "target_runtime_skeleton_exact": True,
                "full_graph_closures_exact": True,
                "call_fixed_flatten_evidence_exact": True,
                "all_actual_caller_contexts_exact": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "right_root1114_full_policy_exported": True,
                "second_run_reproduction_exact": True,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "steam_read_only": True,
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
