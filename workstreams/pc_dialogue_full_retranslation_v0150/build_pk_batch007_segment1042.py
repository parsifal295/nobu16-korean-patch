#!/usr/bin/env python3
"""Build PK block-0 runtime-terminal segment 1042 decisions."""

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

import build_base_batch006_segment1020 as BASE_LEFT
import build_base_batch007_segment1021 as BASE_RIGHT
import build_pk_batch001_segment1025 as HELPERS
import build_pk_batch005_segment1038 as COMMON
import build_pk_batch006_segment1041 as LEFT_PK


ENGINE = BASE_LEFT.ENGINE
GENERAL = BASE_LEFT.GENERAL
UTIL = BASE_LEFT.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B007_S1042.private.v1.jsonl"
)
BASE_DECISIONS = (
    (
        REPO
        / "tmp"
        / WORKSTREAM.name
        / "decisions"
        / "base_msggame_B006_S1020.private.v1.jsonl",
        "581BCCDCFB15C2412B40BF1645F7573D2E2A51479FF1A74A72416A71B23FC5CB",
    ),
    (
        REPO
        / "tmp"
        / WORKSTREAM.name
        / "decisions"
        / "base_msggame_B007_S1021.private.v1.jsonl",
        "06D3624FCEB68AE1C76B1001985A7E04623340935E407BC2B82AA0865D70DB15",
    ),
)
SEGMENT = 1042
QUEUE_BATCH_ID = "pk_msggame-B007"
BLOCK_ID = 0
QUEUE_START = 0
QUEUE_STOP = 67
RECORD_IDS = tuple(range(2473, 2540))
BASE_RECORD_IDS = tuple(range(2405, 2472))
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
    1000: tuple(range(2469, 2476)),
    1006: tuple(range(2476, 2483)),
    1012: tuple(range(2483, 2490)),
    1018: tuple(range(2490, 2497)),
    1024: tuple(range(2497, 2504)),
    1030: tuple(range(2504, 2511)),
    1036: tuple(range(2511, 2518)),
    1042: tuple(range(2518, 2525)),
    1048: tuple(range(2525, 2532)),
    1054: tuple(range(2532, 2539)),
    1060: tuple(range(2539, 2546)),
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

BASE_POLICY = {
    **BASE_LEFT.FULL_TRANSLATION_POLICY,
    **BASE_RIGHT.FULL_TRANSLATION_POLICY,
}
TRANSLATIONS_BY_RECORD = {
    record_id: BASE_POLICY[record_id - 68]
    for record_id in RECORD_IDS
}
TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}

EXPECTED_SOURCE_SEQUENCE_SHA256 = (
    "78782651A5576DCF3F7B263AA1076BA3DBA041E69D2A690B1455C77457658115"
)
EXPECTED_SOURCE_LITERAL_SHA256 = (
    "6A65557762149688068704A9B10E4F4F192345E13C599C9CA31E29689B9236E8"
)
EXPECTED_POLICY_SHA256 = (
    "CCC91BCB398BC408BAE64D1CB031CCF69D60642073B960BC14DAACE86932EEB3"
)
EXPECTED_MAPPING_SHA256 = (
    "0F053DDE34FA25CB6F94CFF0F4FC97DB8ABA0BF8612BF1B6FDDDB65BB291E981"
)
EXPECTED_CHANGED_LITERAL_COUNT = 45

PK_TARGET_ARCHIVE_DIGESTS = {
    "pk_jp": "215EA6A8266647261A490926EE6797FA742548728902C1B606EB7C62EA73773F",
    "pk_current": "1D902DA945CB37249EDF3B28601ABDF165D2415A7FF688EB6E9D86423CDCF64F",
    "pk_sc": "503CAD587D94CDE2230C3C0F7AB841FEC6EBE13E8ABEB6C4D68415845E0ED02B",
    "pk_tc": "503CAD587D94CDE2230C3C0F7AB841FEC6EBE13E8ABEB6C4D68415845E0ED02B",
    "pk_en": "503CAD587D94CDE2230C3C0F7AB841FEC6EBE13E8ABEB6C4D68415845E0ED02B",
}
PK_FULL_ARCHIVE_DIGESTS = {
    "pk_jp": "8C32CA7DF812A79CCB63282C58BF12B45EEC4B04B945098156CFF39DD49CA7B1",
    "pk_current": "F8148939CE324EBA6DF52AAD7A03FAE56C13E9AE6BBF75C96B06AB8DBF8695ED",
    "pk_sc": "7FBDE4E509E06950255F38915718BB97DF17232431ECD0C464F36CBA45AA1A25",
    "pk_tc": "7FBDE4E509E06950255F38915718BB97DF17232431ECD0C464F36CBA45AA1A25",
    "pk_en": "7FBDE4E509E06950255F38915718BB97DF17232431ECD0C464F36CBA45AA1A25",
}
PK_TARGET_EDGE = (
    67,
    "4C8B20EAE637ECD0F65E4E79E64D5EAE0993A88D532959A0D711EE1A77EF7AF8",
)
PK_FULL_EDGE = (
    77,
    "03DBE370D623E54E8F24AF7F1C904ABDA4E767B1DC6539C47681DC64E1CFA827",
)
EXPECTED_CALL_EVIDENCE_SHA256 = (
    "3A95B1F172F3F8C5FE25F53726946C8F39E17A11299440FE40C35DDB3BD6DA5F"
)
EXPECTED_ALL_CALLER_CONTEXT_SHA256 = (
    "AC880944ECD38B7A8C19B8C08CEB91473EF031D84AB607D37BDB5172DDBD640D"
)
EXPECTED_ALL_CALLER_CONTEXT_COUNT = 93
MORPHOLOGY_014C_RE = re.compile(b"\x01\x4C(.{4})", re.DOTALL)
EXPECTED_014C_OVERLAP = ((15, 25, 0, 65, 84213762),)

LEFT_BOUNDARY_IDS = FULL_PK_GROUPS[1000]
LEFT_BOUNDARY_SOURCE_SHA256 = (
    "D0AC151BC2CC8B5FDD5B1BF2B085C8BD6E96CD638DB08B47879AED61610066EE"
)
LEFT_BOUNDARY_CURRENT = (
    "받고서",
    "받아서",
    "받고서",
    "받고서",
    "받아서",
    "받고",
    "받아서",
)
LEFT_BOUNDARY_POLICY = LEFT_BOUNDARY_CURRENT
LEFT_BOUNDARY_CURRENT_SHA256 = (
    "39081206758303986AF040205B3F9A08E2D510813C257E08AC1E273D41D16527"
)

RIGHT_BOUNDARY_IDS = FULL_PK_GROUPS[1060]
RIGHT_BOUNDARY_SOURCE_SHA256 = (
    "64F508B5CA5680159C99E58C456556A5CD4692E636D39770AE9EAA965E234D9F"
)
RIGHT_BOUNDARY_CURRENT = (
    "괜찮은가",
    "좋은가",
    "괜찮으시겠습니까",
    "괜찮으시겠습니까",
    "괜찮을까요",
    "괜찮으시겠소",
    "좋은가",
)
RIGHT_BOUNDARY_POLICY = (
    "괜찮습니까",
    "괜찮은가",
    "괜찮겠사옵니까",
    "괜찮겠사옵니까",
    "괜찮겠습니까",
    "괜찮겠소",
    "괜찮은가",
)
RIGHT_BOUNDARY_CURRENT_SHA256 = (
    "3D177D5993938B707FF158D2F208CBB4E39EF62C44A6E0DDC02A94EAB676393C"
)
RIGHT_BOUNDARY_POLICY_SHA256 = (
    "38C914119CD9DDD76C0D5E24F879E1DC34106E7A2687AD0CDEDFE1F39692D869"
)
RIGHT_ROOT1060_FULL_IDS = RIGHT_BOUNDARY_IDS
RIGHT_ROOT1060_FULL_SOURCE_SHA256 = RIGHT_BOUNDARY_SOURCE_SHA256
RIGHT_ROOT1060_FULL_CURRENT = RIGHT_BOUNDARY_CURRENT
RIGHT_ROOT1060_FULL_POLICY = RIGHT_BOUNDARY_POLICY

ROOT_ASSEMBLY_PLAN = {
    1000: (
        "receipt connective with no live caller; preserve the full imported "
        "left boundary and its seven-register matrix"
    ),
    1006: (
        "respectful or hostile person noun; rewrite the completed current "
        "predicate into an attributive form without automatic spacing"
    ),
    1012: (
        "past giving or benefactive action; restore direction and insert "
        "the Korean auxiliary boundary before fixed emphatic following"
    ),
    1018: (
        "cessation command; insert the object-command boundary and retain "
        "the seven-speaker imperative register"
    ),
    1024: (
        "present giving, offering, or receipt matrix with no live caller; "
        "direction and deference remain distinct by speaker"
    ),
    1030: (
        "imperative giving or benefactive matrix with no live caller; "
        "command strength remains distinct by speaker"
    ),
    1036: (
        "future or volitional benefactive action; normalize lexical stems, "
        "giving direction, and explicit auxiliary spacing across complete "
        "and source-only callers"
    ),
    1042: (
        "sentence-final recognition or assertion particle; current Korean "
        "often already completes the clause, and chained fixed terminals "
        "require joint copular rewriting"
    ),
    1048: (
        "acceptability adjective used in recommendation, command, question, "
        "and fixed-following constructions; each caller requires semantic "
        "assembly rather than literal concatenation"
    ),
    1054: (
        "complete positive evaluation matrix with no live caller; preserve "
        "the seven-speaker register distinctions"
    ),
    1060: (
        "permission or acceptability question; normalize incomplete current "
        "callers and expose the full right boundary for the next segment"
    ),
}

CALLER_INTEGRATION_EVIDENCE = {
    1006: (
        {
            "call_site": "15:1476:1:0",
            "observed_current_left": "은(는) 모략을 모른다",
            "observed_current_right": (
                "\n이런 무리는 금세 유언비어를 믿고\n주가를 저버리"
            ),
            "expected_current_gap_hex": "0143EE030000",
            "integration_mode": "rewrite_predicate_to_person_attributive",
            "source_free_korean_example": (
                "은(는) 모략을 모르는 분\n"
                "이런 무리는 금세 유언비어를 믿고\n"
                "주가를 저버릴 것입니다"
            ),
        },
    ),
    1012: (
        {
            "call_site": "8:966:1:0",
            "observed_current_left": "의 힘을\n약화시켜",
            "observed_current_right": "！",
            "expected_current_gap_hex": (
                "0143F403000001436C040000"
            ),
            "integration_mode": "insert_benefactive_space_fixed_following",
            "source_free_korean_example": (
                "의 힘을\n약화시켜 주었습니다!"
            ),
        },
    ),
    1018: (
        {
            "call_site": "1:23:2:0",
            "observed_current_left": "。싸움을",
            "observed_current_right": "。",
            "expected_current_gap_hex": "0143FA030000",
            "integration_mode": "insert_object_command_space",
            "source_free_korean_example": "싸움을 그만두십시오.",
        },
    ),
    1036: (
        {
            "call_site": "1:24:1:0",
            "observed_current_left": (
                "이(가) 지면 물구나무서서 알몸으로 마을을 한 바퀴 돌고"
            ),
            "observed_current_right": "。",
            "expected_current_gap_hex": "01430C040000",
            "integration_mode": "normalize_benefactive_motion_and_space",
            "source_free_korean_example": (
                "이(가) 지면 물구나무서서 알몸으로 마을을 "
                "한 바퀴 돌아 주겠습니다."
            ),
        },
        {
            "call_site": "6:4415:2:0",
            "observed_current_left": (
                "에게!\n취락 장악 따위 눈 깜짝할 새에\n끝내"
            ),
            "observed_current_right": "",
            "expected_current_gap_hex": "01430C040000050505",
            "integration_mode": "insert_benefactive_auxiliary_space",
            "source_free_korean_example": (
                "에게!\n취락 장악 따위는 눈 깜짝할 새에\n"
                "끝내 주겠습니다"
            ),
        },
        {
            "call_site": "6:4633:4:0",
            "observed_current_left": (
                "을 추천했으니\n바라는 것을 조금은 말해 보"
            ),
            "observed_current_right": "",
            "expected_current_gap_hex": "01430C040000050505",
            "integration_mode": "rewrite_benefactive_request_acceptance",
            "source_free_korean_example": (
                "을 추천했으니\n바라는 바를 조금은 들어 주겠습니다"
            ),
        },
        {
            "call_site": "15:1509:4:0",
            "observed_current_left": "이 실력을 조금 단련시켜",
            "observed_current_right": "\n맡겨 주시겠습니까?",
            "expected_current_gap_hex": "01430C040000",
            "integration_mode": "rewrite_benefactive_instruction",
            "source_free_korean_example": (
                "이 기량을 조금 가르쳐 주겠습니다\n"
                "맡겨 주시겠습니까?"
            ),
        },
        {
            "call_site": "15:2216:3:0",
            "observed_current_left": "\n출병하여, 방해하",
            "observed_current_right": "",
            "expected_current_gap_hex": "01430C040000050505",
            "integration_mode": "normalize_benefactive_intervention",
            "source_free_korean_example": (
                "\n출병하여 방해해 주겠습니다"
            ),
        },
        {
            "call_site": "15:2217:2:0",
            "observed_current_left": (
                "에 걸어 둔 조략을\n출진하여 파헤쳐"
            ),
            "observed_current_right": "",
            "expected_current_gap_hex": "01430C040000050505",
            "integration_mode": "normalize_historical_benefactive_action",
            "source_free_korean_example": (
                "에 걸어 둔 조략을\n출진하여 밝혀 주겠습니다"
            ),
        },
    ),
    1042: (
        {
            "call_site": "6:4694:2:0",
            "observed_current_left": (
                "까?\n이걸 받고도 거절하면 부끄러운 일입니"
            ),
            "observed_current_right": "",
            "expected_current_gap_hex": (
                "0143120400000143E0020000050505"
            ),
            "integration_mode": "rewrite_fixed_copular_confirmation",
            "source_free_korean_example": (
                "이걸 받아들이지 않으면 부끄러운 일이군요"
            ),
        },
        {
            "call_site": "6:4723:1:0",
            "observed_current_left": "결국 이 정도였군",
            "observed_current_right": (
                "\n삶든 굽든 마음대로 하시오"
            ),
            "expected_current_gap_hex": (
                "0143120400000143E0020000"
            ),
            "integration_mode": "flatten_completed_assertion_chain",
            "source_free_korean_example": (
                "결국 이 정도로군\n삶든 굽든 마음대로 하시오"
            ),
        },
        {
            "call_site": "15:1381:3:0",
            "observed_current_left": "도 비열한 수를 쓰는 법",
            "observed_current_right": "…！",
            "expected_current_gap_hex": "014312040000",
            "integration_mode": "rewrite_nominalized_recognition",
            "source_free_korean_example": (
                "도 비열한 수를 쓰는군요…!"
            ),
        },
        {
            "call_site": "16:81:1:0",
            "observed_current_left": (
                "후방 성에서의 정무…\n내 진면목을 보일 때로군"
            ),
            "observed_current_right": "",
            "expected_current_gap_hex": "014312040000050505",
            "integration_mode": "flatten_completed_recognition",
            "source_free_korean_example": (
                "후방 성에서의 정무…\n내 진면목을 보일 때로군요"
            ),
        },
    ),
    1048: (
        {
            "call_site": "6:4573:1:0",
            "observed_current_left": (
                "의 포섭은 순조롭게 진행되어\n"
                "성째로 돌아설 계책까지 있다 합니다\n"
                "자세한 내용은 당사자에게 직접 들어 보시는 게"
            ),
            "observed_current_right": "인가 하고",
            "expected_current_gap_hex": "014318040000",
            "integration_mode": "rewrite_fixed_recommendation",
            "source_free_korean_example": (
                "의 포섭은 순조롭게 진행되어\n"
                "성째로 돌아설 계책까지 있다고 합니다\n"
                "자세한 내용은 당사자에게 직접 들어 보시는 게 "
                "좋을까 하여"
            ),
        },
        {
            "call_site": "6:4723:2:0",
            "observed_current_left": (
                "\n삶든 굽든 마음대로 하시오"
            ),
            "observed_current_right": "",
            "expected_current_gap_hex": "014318040000050505",
            "integration_mode": "flatten_completed_recommendation_command",
            "source_free_korean_example": (
                "\n삶든 굽든 마음대로 하시오"
            ),
        },
        {
            "call_site": "6:4763:1:0",
            "observed_current_left": (
                "전쟁은 끝났다는 것이지요"
            ),
            "observed_current_right": (
                "?\n양쪽 가신과 영민들도 기뻐할 것입니다"
            ),
            "expected_current_gap_hex": (
                "014318040000014300010000"
            ),
            "integration_mode": "rewrite_fixed_acceptability_question",
            "source_free_korean_example": (
                "전쟁은 끝났다는 것으로 괜찮습니까?\n"
                "양쪽 가신과 영민도 기뻐할 것입니다"
            ),
        },
        {
            "call_site": "9:4142:5:0",
            "observed_current_left": "은 여기서 포박하겠다",
            "observed_current_right": "",
            "expected_current_gap_hex": "014318040000050505",
            "integration_mode": "rewrite_historical_capture_command",
            "source_free_korean_example": "은 여기서 포박을 받아라",
        },
        {
            "call_site": "15:1234:2:0",
            "observed_current_left": (
                "을(를) 함락하려면\n두더지 공격을 쓰는 것이\n"
            ),
            "observed_current_right": "",
            "expected_current_gap_hex": (
                "01431804000001431E010000050505"
            ),
            "integration_mode": "rewrite_fixed_siege_recommendation",
            "source_free_korean_example": (
                "을(를) 함락하려면\n갱도 공격을 쓰는 것이 좋겠습니다"
            ),
        },
        {
            "call_site": "15:1412:2:0",
            "observed_current_left": "\n말을 건네 보셔도",
            "observed_current_right": "인가",
            "expected_current_gap_hex": (
                "014318040000014362020000"
            ),
            "integration_mode": "rewrite_fixed_permission_question",
            "source_free_korean_example": (
                "\n말을 걸어 보셔도 괜찮습니까?"
            ),
        },
        {
            "call_site": "15:2296:2:0",
            "observed_current_left": (
                "\n맞지 않는 성하 방침의 성이 없는지\n재검토하셔도"
            ),
            "observed_current_right": "인가 하고",
            "expected_current_gap_hex": "014318040000",
            "integration_mode": "rewrite_fixed_policy_review",
            "source_free_korean_example": (
                "\n맞지 않는 성하 방침의 성이 없는지\n"
                "재검토하셔도 괜찮을까 하여"
            ),
        },
    ),
    1060: (
        {
            "call_site": "6:4585:3:0",
            "observed_current_left": "\n만나 보시겠습니",
            "observed_current_right": "？\n",
            "expected_current_gap_hex": "014324040000",
            "integration_mode": "rewrite_acceptance_permission_question",
            "source_free_korean_example": (
                "\n받아들여도 괜찮습니까?\n"
            ),
        },
        {
            "call_site": "6:4897:3:0",
            "observed_current_left": (
                "\n다음 사람들로 괜찮습니"
            ),
            "observed_current_right": "？",
            "expected_current_gap_hex": "014324040000",
            "integration_mode": "normalize_incomplete_selection_question",
            "source_free_korean_example": (
                "\n다음 사람들로 괜찮습니까?"
            ),
        },
        {
            "call_site": "7:2437:2:0",
            "observed_current_left": "\n귀환하더라도",
            "observed_current_right": "",
            "expected_current_gap_hex": "014324040000050505",
            "integration_mode": "rewrite_return_permission_question",
            "source_free_korean_example": (
                "\n귀환해도 괜찮습니까"
            ),
        },
    ),
}
SOURCE_ONLY_FLATTEN_EVIDENCE = {
    1036: (
        {
            "call_site": "6:4700:1:0",
            "observed_current_literals": (
                "어쩔 수 없군.\n이 정도면 받아들이겠다.",
            ),
            "observed_current_gaps_hex": ("", "050505"),
            "integration_mode": "flatten_source_only_benefactive_acceptance",
            "source_free_korean_example": (
                "어쩔 수 없군\n그렇다면 받아 주겠습니다"
            ),
        },
        {
            "call_site": "15:264:3:0",
            "observed_current_literals": (
                "선동에는 약간의 자금이 필요하오",
                ".\n",
                "교서로 호소한다면",
                "\n선동은 틀림없이 성공할 것이오.",
            ),
            "observed_current_gaps_hex": ("", "", "", "", "050505"),
            "integration_mode": "flatten_source_only_historical_benefactive",
            "source_free_korean_example": (
                "이(가) 교서로 호소해 주겠습니다\n"
                "그러면 선동은 확실한 것이 됩니다"
            ),
        },
    ),
    1048: (
        {
            "call_site": "15:2268:2:0",
            "observed_current_literals": (
                "지금은 움직일 때가 아니옵니다. ",
                "\n기회를 엿보는 편이 ",
                "좋겠사옵니다.",
            ),
            "observed_current_gaps_hex": ("", "", "", "050505"),
            "integration_mode": "flatten_source_only_recommendation",
            "source_free_korean_example": (
                "\n잠시 기회를 기다리는 것이 좋을까 하여"
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
EXPECTED_SOURCE_ONLY_CLASS_COUNTS = dict(
    Counter(
        str(example["integration_mode"])
        for examples in SOURCE_ONLY_FLATTEN_EVIDENCE.values()
        for example in examples
    )
)

BASIS = (
    "pristine PK JP authoritative; unique literal-gap global reverse "
    "mapping to Base plus68 used only as semantic context; actual 0143 "
    "calls, 014A closures, fixed following, source-only and current-only "
    "flattening guarded; seven-speaker register and giving, receipt, "
    "benefactive, command, recognition, recommendation and permission "
    "functions reviewed independently; Korean caller rewrites require "
    "explicit spacing because runtime inserts none; S1041 left root1000 "
    "contract and full right root1060 contract guarded; source-bearing "
    "decisions remain ignored, with skeleton, outside-scope, reverse, "
    "two-run and Steam-read-only guarantees"
)


literal_texts = COMMON.literal_texts
gap_bytes = COMMON.gap_bytes
archive_records = COMMON.archive_records
record_signature = COMMON.record_signature
sequence_starts = COMMON.sequence_starts
incoming_jump_rows = COMMON.incoming_jump_rows
caller_context_and_gap = COMMON.caller_context_and_gap


def assert_tracked_builder_source_redacted() -> None:
    if ENGINE.KANA_OR_HAN_RE.search(SCRIPT.read_text(encoding="utf-8")):
        raise RuntimeError(
            f"segment {SEGMENT} tracked builder contains source text"
        )


def assert_queue_contract(prepared: Any) -> None:
    rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
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
    sequence = tuple(
        record_signature(records_by_label["pk_jp"], record_id)
        for record_id in RECORD_IDS
    )
    if (
        HELPERS.canonical_sha256(sequence)
        != EXPECTED_SOURCE_SEQUENCE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} literal-gap source sequence drifted"
        )
    base_hits = sequence_starts(records_by_label["base_jp"], sequence)
    pk_hits = sequence_starts(records_by_label["pk_jp"], sequence)
    if base_hits != (2405,) or pk_hits != (2473,):
        raise RuntimeError(
            f"segment {SEGMENT} source reverse search drifted: "
            f"{base_hits}/{pk_hits}"
        )
    mapping = {
        pk_record_id: base_hits[0] + ordinal
        for ordinal, pk_record_id in enumerate(RECORD_IDS)
    }
    if (
        {pk - base for pk, base in mapping.items()} != {68}
        or tuple(mapping.values()) != BASE_RECORD_IDS
        or HELPERS.canonical_sha256(tuple(mapping.items()))
        != EXPECTED_MAPPING_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} discovered mapping drifted"
        )
    return mapping, 68


def assert_sources(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    mapping: dict[int, int],
) -> None:
    source = records_by_label["pk_jp"]
    if (
        HELPERS.canonical_sha256(
            tuple(
                literal_texts(source, (BLOCK_ID, record_id))[0]
                for record_id in RECORD_IDS
            )
        )
        != EXPECTED_SOURCE_LITERAL_SHA256
        or HELPERS.canonical_sha256(
            tuple(TRANSLATIONS_BY_RECORD.values())
        )
        != EXPECTED_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} source or policy digest drifted"
        )
    full_keys = tuple(
        (BLOCK_ID, record_id) for record_id in range(2469, 2546)
    )
    for label, expected in PK_TARGET_ARCHIVE_DIGESTS.items():
        if GENERAL.subset_digest(
            records_by_label[label], RECORD_KEYS
        ) != expected:
            raise RuntimeError(
                f"segment {SEGMENT} target {label} digest drifted"
            )
    for label, expected in PK_FULL_ARCHIVE_DIGESTS.items():
        if GENERAL.subset_digest(
            records_by_label[label], full_keys
        ) != expected:
            raise RuntimeError(
                f"segment {SEGMENT} full {label} digest drifted"
            )
    for pk_record_id, base_record_id in mapping.items():
        pk_key = (BLOCK_ID, pk_record_id)
        base_key = (BLOCK_ID, base_record_id)
        for language in ("jp", "current", "sc", "tc"):
            if (
                records_by_label[f"pk_{language}"][pk_key].data
                != records_by_label[f"base_{language}"][base_key].data
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} PK/Base {language} record "
                    f"drifted: {pk_key}/{base_key}"
                )
        if literal_texts(records_by_label["pk_en"], pk_key) != ("",):
            raise RuntimeError(
                f"segment {SEGMENT} PK EN context drifted: {pk_key}"
            )
        for label in PK_TARGET_ARCHIVE_DIGESTS:
            if (
                len(literal_texts(records_by_label[label], pk_key)) != 1
                or gap_bytes(records_by_label[label][pk_key])
                != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} target skeleton drifted: "
                    f"{label}/{pk_key}"
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


def assert_all_caller_context(
    source: dict[tuple[int, int], Any],
    current: dict[tuple[int, int], Any],
) -> None:
    rows: list[tuple[int | str, ...]] = []
    for root in FULL_PK_GROUPS:
        for label, records in (
            ("pk_jp", source),
            ("pk_current", current),
        ):
            for call_site in HELPERS.root_call_sites(records, root):
                rows.append(
                    (
                        label,
                        root,
                        call_site,
                        *caller_context_and_gap(records, call_site),
                    )
                )
    if (
        len(rows) != EXPECTED_ALL_CALLER_CONTEXT_COUNT
        or HELPERS.canonical_sha256(tuple(rows))
        != EXPECTED_ALL_CALLER_CONTEXT_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} all caller contexts drifted"
        )


def assert_caller_evidence(
    current: dict[tuple[int, int], Any],
) -> None:
    current_calls = {
        root: set(HELPERS.root_call_sites(current, root))
        for root in FULL_PK_GROUPS
    }
    counts: Counter[str] = Counter()
    for root, examples in CALLER_INTEGRATION_EVIDENCE.items():
        for example in examples:
            call_site = str(example["call_site"])
            counts[str(example["integration_mode"])] += 1
            if call_site not in current_calls[root]:
                raise RuntimeError(
                    f"segment {SEGMENT} caller site drifted: "
                    f"{root}/{call_site}"
                )
            left, right, gap = caller_context_and_gap(current, call_site)
            if (
                left != example["observed_current_left"]
                or right != example["observed_current_right"]
                or gap != example["expected_current_gap_hex"]
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} caller context drifted: "
                    f"{root}/{call_site}"
                )
            sample = str(example["source_free_korean_example"])
            if (
                ENGINE.KANA_OR_HAN_RE.search(sample)
                or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(sample)
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} caller example is not "
                    f"source-free Korean: {root}/{call_site}"
                )
    if dict(counts) != EXPECTED_INTEGRATION_CLASS_COUNTS:
        raise RuntimeError(
            f"segment {SEGMENT} caller integration classes drifted"
        )


def assert_source_only_evidence(
    source: dict[tuple[int, int], Any],
    current: dict[tuple[int, int], Any],
) -> None:
    counts: Counter[str] = Counter()
    for root, examples in SOURCE_ONLY_FLATTEN_EVIDENCE.items():
        source_only = (
            set(HELPERS.root_call_sites(source, root))
            - set(HELPERS.root_call_sites(current, root))
        )
        for example in examples:
            call_site = str(example["call_site"])
            counts[str(example["integration_mode"])] += 1
            if call_site not in source_only:
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
            sample = str(example["source_free_korean_example"])
            if (
                ENGINE.KANA_OR_HAN_RE.search(sample)
                or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(sample)
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} source-only example is not "
                    f"source-free Korean: {root}/{call_site}"
                )
    if dict(counts) != EXPECTED_SOURCE_ONLY_CLASS_COUNTS:
        raise RuntimeError(
            f"segment {SEGMENT} source-only classes drifted"
        )


def assert_runtime_graph(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[str, tuple[tuple[int | str, ...], ...]]:
    target_ids = set(RECORD_IDS)
    full_ids = set(range(2469, 2546))
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
        for target_set, expected, description in (
            (target_ids, PK_TARGET_EDGE, "target"),
            (full_ids, PK_FULL_EDGE, "full"),
        ):
            edges = incoming_jump_rows(records, target_set)
            if (
                len(edges) != expected[0]
                or HELPERS.canonical_sha256(edges) != expected[1]
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {label} {description} "
                    "incoming graph drifted"
                )
    for label in ("pk_jp", "pk_current"):
        records = records_by_label[label]
        graph = HELPERS.graph_edges(records)
        for root, expected in EXPECTED_ROOT_CLOSURES.items():
            if tuple(sorted(HELPERS.graph_closure(graph, root))) != expected:
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
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    evidence = collect_call_evidence(source, current)
    if HELPERS.canonical_sha256(evidence) != EXPECTED_CALL_EVIDENCE_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} call/fixed/flatten evidence drifted"
        )
    assert_all_caller_context(source, current)
    assert_caller_evidence(current)
    assert_source_only_evidence(source, current)
    BASE_LEFT.assert_corpora(records_by_label)
    BASE_LEFT.assert_runtime_graph(records_by_label)
    BASE_RIGHT.assert_corpora(records_by_label)
    BASE_RIGHT.assert_runtime_graph(records_by_label)
    return evidence


def assert_boundaries(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    actual_left_current = tuple(
        literal_texts(current, (BLOCK_ID, record_id))[0]
        for record_id in LEFT_BOUNDARY_IDS
    )
    if (
        HELPERS.canonical_sha256(
            tuple(
                literal_texts(source, (BLOCK_ID, record_id))[0]
                for record_id in LEFT_BOUNDARY_IDS
            )
        )
        != LEFT_BOUNDARY_SOURCE_SHA256
        or actual_left_current != LEFT_BOUNDARY_CURRENT
        or HELPERS.canonical_sha256(actual_left_current)
        != LEFT_BOUNDARY_CURRENT_SHA256
        or LEFT_BOUNDARY_POLICY
        != tuple(
            BASE_POLICY[record_id - 68]
            for record_id in LEFT_BOUNDARY_IDS
        )
        or LEFT_BOUNDARY_IDS != LEFT_PK.RIGHT_ROOT1000_FULL_IDS
        or LEFT_BOUNDARY_SOURCE_SHA256
        != LEFT_PK.RIGHT_ROOT1000_FULL_SOURCE_SHA256
        or LEFT_BOUNDARY_CURRENT
        != LEFT_PK.RIGHT_ROOT1000_FULL_CURRENT
        or LEFT_BOUNDARY_POLICY
        != LEFT_PK.RIGHT_ROOT1000_FULL_POLICY
    ):
        raise RuntimeError(
            f"segment {SEGMENT} S1041 root1000 boundary drifted"
        )
    actual_right_current = tuple(
        literal_texts(current, (BLOCK_ID, record_id))[0]
        for record_id in RIGHT_BOUNDARY_IDS
    )
    if (
        HELPERS.canonical_sha256(
            tuple(
                literal_texts(source, (BLOCK_ID, record_id))[0]
                for record_id in RIGHT_BOUNDARY_IDS
            )
        )
        != RIGHT_BOUNDARY_SOURCE_SHA256
        or actual_right_current != RIGHT_BOUNDARY_CURRENT
        or HELPERS.canonical_sha256(actual_right_current)
        != RIGHT_BOUNDARY_CURRENT_SHA256
        or RIGHT_BOUNDARY_POLICY
        != tuple(
            BASE_POLICY[record_id - 68]
            for record_id in RIGHT_BOUNDARY_IDS
        )
        or HELPERS.canonical_sha256(RIGHT_BOUNDARY_POLICY)
        != RIGHT_BOUNDARY_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} right root1060 boundary drifted"
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
    for pk_record_id in RECORD_IDS:
        base_record_id = mapping[pk_record_id]
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
    BASE_LEFT.assert_semantics(dict(BASE_LEFT.RAW_TRANSLATIONS))
    BASE_RIGHT.assert_semantics(dict(BASE_RIGHT.TRANSLATIONS))
    for pk_record_id, translation in TRANSLATIONS_BY_RECORD.items():
        if translation != BASE_POLICY[pk_record_id - 68]:
            raise RuntimeError(
                f"segment {SEGMENT} mapped policy drifted: {pk_record_id}"
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
    if resource.current_path.read_bytes() != resource.current_blob:
        raise RuntimeError(
            f"segment {SEGMENT} Steam PK input changed during build"
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
    assert_tracked_builder_source_redacted()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_queue_contract(prepared)
    records_by_label = archive_records(prepared)
    mapping, offset = discover_mapping(records_by_label)
    assert_sources(records_by_label, mapping)
    call_evidence = assert_runtime_graph(records_by_label)
    assert_boundaries(records_by_label)
    assert_completed_base_policy(prepared, mapping)
    translations = dict(TRANSLATIONS)
    assert_semantics(translations)

    current = records_by_label["pk_current"]
    for coordinate, translation in translations.items():
        _, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        current_text = literal_texts(
            current, (BLOCK_ID, record_id)
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
                "source_free_current_caller_evidence": list(
                    CALLER_INTEGRATION_EVIDENCE.get(root, ())
                ),
                "source_free_source_only_caller_evidence": list(
                    SOURCE_ONLY_FLATTEN_EVIDENCE.get(root, ())
                ),
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
                    "all_caller_contexts_guarded": True,
                    "valid_incoming_014c_count": 0,
                    "automatic_space_inserted": False,
                    "seven_speaker_register_guarded": True,
                    "benefactive_or_receipt_semantics": (
                        root in (1000, 1012, 1024, 1030, 1036)
                    ),
                    "runtime_integration_required": True,
                    "caller_rewrite_required_before_runtime_approval": (
                        root in CALLER_INTEGRATION_EVIDENCE
                    ),
                    "assembly_plan": ROOT_ASSEMBLY_PLAN[root],
                    "source_free_caller_integration_examples": list(
                        CALLER_INTEGRATION_EVIDENCE.get(root, ())
                    ),
                    "source_free_source_only_integration_examples": list(
                        SOURCE_ONLY_FLATTEN_EVIDENCE.get(root, ())
                    ),
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
        len(rows) != 67
        or len(validated) != 67
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
    current = archive_records(prepared)["pk_current"]
    changed = sum(
        translations[f"{BLOCK_ID}:{record_id}:0"]
        != literal_texts(current, (BLOCK_ID, record_id))[0]
        for record_id in RECORD_IDS
    )
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B007_S1042",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [0, 66],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "source_literal_count": len(RECORD_IDS),
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "changed_literal_count": changed,
                "caller_integration_example_class_counts":
                EXPECTED_INTEGRATION_CLASS_COUNTS,
                "source_only_example_class_counts":
                EXPECTED_SOURCE_ONLY_CLASS_COUNTS,
                "base_mapping_method":
                "global_unique_exact68_literal_gap_reverse_search",
                "discovered_base_record_range": [2405, 2471],
                "discovered_pk_minus_base_offset": offset,
                "source_sequence_sha256":
                EXPECTED_SOURCE_SEQUENCE_SHA256,
                "source_literal_sha256":
                EXPECTED_SOURCE_LITERAL_SHA256,
                "translation_policy_sha256": EXPECTED_POLICY_SHA256,
                "mapping_sha256": EXPECTED_MAPPING_SHA256,
                "pk_target_incoming_sha256": PK_TARGET_EDGE[1],
                "pk_full_group_incoming_sha256": PK_FULL_EDGE[1],
                "pk_call_fixed_flatten_evidence_sha256":
                EXPECTED_CALL_EVIDENCE_SHA256,
                "all_caller_context_sha256":
                EXPECTED_ALL_CALLER_CONTEXT_SHA256,
                "valid_incoming_014c_count": 0,
                "left_root1000_full_policy":
                list(LEFT_BOUNDARY_POLICY),
                "right_root1060_full_policy":
                list(RIGHT_BOUNDARY_POLICY),
                "candidate_sha256": candidate_sha256,
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
                "target_runtime_skeleton_exact": True,
                "full_graph_closures_exact": True,
                "call_fixed_flatten_evidence_exact": True,
                "all_caller_contexts_exact": True,
                "source_free_current_caller_evidence_exact": True,
                "source_free_source_only_caller_evidence_exact": True,
                "s1041_root1000_boundary_contract_exact": True,
                "right_root1060_boundary_exported": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tracked_builder_source_redacted": True,
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
