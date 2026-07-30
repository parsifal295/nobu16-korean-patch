#!/usr/bin/env python3
"""Build PK block-0 runtime-terminal segment 1041 decisions."""

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

import build_base_batch006_segment1019 as BASE_LEFT
import build_base_batch006_segment1020 as BASE_RIGHT
import build_pk_batch001_segment1025 as HELPERS
import build_pk_batch005_segment1038 as COMMON

try:
    import build_pk_batch006_segment1040 as LEFT_PK
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
    / "pk_msggame_B006_S1041.private.v1.jsonl"
)
BASE_DECISIONS = (
    (
        REPO
        / "tmp"
        / WORKSTREAM.name
        / "decisions"
        / "base_msggame_B006_S1019.private.v1.jsonl",
        "71DC064001193A00A4CB03D7FB6C45D637CF5F412D07674D02FC7EADD678AEAC",
    ),
    (
        REPO
        / "tmp"
        / WORKSTREAM.name
        / "decisions"
        / "base_msggame_B006_S1020.private.v1.jsonl",
        "581BCCDCFB15C2412B40BF1645F7573D2E2A51479FF1A74A72416A71B23FC5CB",
    ),
)
SEGMENT = 1041
QUEUE_BATCH_ID = "pk_msggame-B006"
BLOCK_ID = 0
QUEUE_START = 134
QUEUE_STOP = 200
OWNED_RECORD_IDS = tuple(range(2405, 2473))
HIDDEN_RECORD_IDS = (2406, 2410)
RECORD_IDS = tuple(
    record_id
    for record_id in OWNED_RECORD_IDS
    if record_id not in HIDDEN_RECORD_IDS
)
BASE_RECORD_IDS = tuple(range(2337, 2405))
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
OWNED_RECORD_KEYS = tuple(
    (BLOCK_ID, record_id) for record_id in OWNED_RECORD_IDS
)
TARGET_COORDINATES = tuple(
    f"{BLOCK_ID}:{record_id}:0" for record_id in RECORD_IDS
)
QUEUE_HIDDEN_COORDINATES = ("0:2406:0", "0:2410:0")
PK_RECORD_COUNT = 21751

FULL_PK_GROUPS = {
    940: tuple(range(2399, 2406)),
    946: tuple(range(2406, 2413)),
    952: tuple(range(2413, 2420)),
    958: tuple(range(2420, 2427)),
    964: tuple(range(2427, 2434)),
    970: tuple(range(2434, 2441)),
    976: tuple(range(2441, 2448)),
    982: tuple(range(2448, 2455)),
    988: tuple(range(2455, 2462)),
    994: tuple(range(2462, 2469)),
    1000: tuple(range(2469, 2476)),
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

EXPECTED_SOURCE_SHA256 = (
    "8255DE75D274FE3C88E1549650F41D75AE8A8E315ACC52989CD56EEB55926F81"
)
EXPECTED_POLICY_SHA256 = (
    "6933306B026818D7914EB5D97DA33B78F763F00A6DCF85784275DEB60BEBAFF5"
)
EXPECTED_MAPPING_SHA256 = (
    "3B71A1516E7943AE166BC30B1E1A7E457210765C2109FCD21E7559DA269961F7"
)
EXPECTED_HIDDEN_RAW_SHA256 = (
    "A3B020175A7848DB7440FEF6A3C7B7BF8B91DA64824E8305718CCD324E8E270A"
)
EXPECTED_CHANGED_LITERAL_COUNT = 50

PK_TARGET_ARCHIVE_DIGESTS = {
    "pk_jp": "A09DA91E65AB548B36C9A3CB50D80A5C048F1FF13B3DA7A3A89F609C83B32DA1",
    "pk_current": "E513A5E78B0D94A6C69BA3EC7D6F9EACDF5E6085F771E8866B5EC972FEC23426",
    "pk_sc": "93BE105834BD56C29B3A93CA55894C7A4599CCCF35FB4038BE362A78475EBC07",
    "pk_tc": "93BE105834BD56C29B3A93CA55894C7A4599CCCF35FB4038BE362A78475EBC07",
    "pk_en": "93BE105834BD56C29B3A93CA55894C7A4599CCCF35FB4038BE362A78475EBC07",
}
PK_OWNED_ARCHIVE_DIGESTS = {
    "pk_jp": "A53AD90141294106DCDC8FF83D023D559990E2ECE0F7148F1FF4A49248565C7F",
    "pk_current": "C876AFF09054C1D54287232C7082B178F7AB08643C5A1C1F20AB1A558832BBCE",
    "pk_sc": "50FBD7A0CA86F9D577A6EA20C3851E70432A10F9EFDF3F4E6788B2075C9729BA",
    "pk_tc": "50FBD7A0CA86F9D577A6EA20C3851E70432A10F9EFDF3F4E6788B2075C9729BA",
    "pk_en": "50FBD7A0CA86F9D577A6EA20C3851E70432A10F9EFDF3F4E6788B2075C9729BA",
}
PK_FULL_ARCHIVE_DIGESTS = {
    "pk_jp": "A3058AE511A1B0C4E74673B9FFBB8E28B2572AF70E2F689A8917AE6E59DCDC5F",
    "pk_current": "331BDC89D5B66A8C97A3216B80DDD9575744087BA99C4F7879C5F96A39DB7BB7",
    "pk_sc": "ED48426EF9CD30DC07752C746145D1B70A1C34741D734ED7CA19FCA708E920DA",
    "pk_tc": "ED48426EF9CD30DC07752C746145D1B70A1C34741D734ED7CA19FCA708E920DA",
    "pk_en": "ED48426EF9CD30DC07752C746145D1B70A1C34741D734ED7CA19FCA708E920DA",
}
PK_TARGET_EDGE = (
    66,
    "61051151CD12B05C3BFCC88E74493416A1043FAD1BDB0DCC1E90DD873AF583F0",
)
PK_OWNED_EDGE = (
    68,
    "BC4DA8959338E027C9C8C9331724FA82B42637B44F455D6911066507925D2A95",
)
PK_FULL_EDGE = (
    77,
    "35D8DBE9F85F2ECAC1FA8DF38084561028AD9ED2D5308BC714BE5A5794A2610D",
)
EXPECTED_CALL_EVIDENCE_SHA256 = (
    "D1053E0DCFB92070C3320FD4F6B1E3D1F982D25A86099805F8811DA3EAEE6D3F"
)
MORPHOLOGY_014C_RE = re.compile(b"\x01\x4C(.{4})", re.DOTALL)
EXPECTED_014C_OVERLAP = ((15, 25, 0, 65, 84213762),)

LEFT_BOUNDARY_IDS = FULL_PK_GROUPS[940]
LEFT_BOUNDARY_SOURCE_SHA256 = (
    "8BC825C6678FDE7635181CD245096CFAA1FDCBCCA318036F1A5DA0A9B51F6B55"
)
LEFT_BOUNDARY_CURRENT = (
    "봅니다",
    "음",
    "봅니다",
    "보옵니다",
    "봅니다",
    "봅니다",
    "음",
)
LEFT_BOUNDARY_POLICY = (
    "합니다",
    "한다",
    "합니다",
    "하옵니다",
    "합니다",
    "합니다",
    "한다",
)
RIGHT_BOUNDARY_IDS = FULL_PK_GROUPS[1000]
RIGHT_BOUNDARY_SOURCE_SHA256 = (
    "D0AC151BC2CC8B5FDD5B1BF2B085C8BD6E96CD638DB08B47879AED61610066EE"
)
RIGHT_BOUNDARY_CURRENT = (
    "받고서",
    "받아서",
    "받고서",
    "받고서",
    "받아서",
    "받고",
    "받아서",
)
RIGHT_BOUNDARY_POLICY = RIGHT_BOUNDARY_CURRENT
RIGHT_ROOT1000_FULL_IDS = RIGHT_BOUNDARY_IDS
RIGHT_ROOT1000_FULL_SOURCE_SHA256 = RIGHT_BOUNDARY_SOURCE_SHA256
RIGHT_ROOT1000_FULL_CURRENT = RIGHT_BOUNDARY_CURRENT
RIGHT_ROOT1000_FULL_POLICY = RIGHT_BOUNDARY_POLICY

ROOT_ASSEMBLY_PLAN = {
    940: (
        "finite action ending; current Korean has complete callers, repeated "
        "terminal sites, a source-only flatten, and fixed punctuation, so "
        "the caller stem and following text require joint normalization"
    ),
    946: (
        "disparaging noun or topic particle; two non-display empty register "
        "slots remain byte-exact and there is no live PK caller"
    ),
    952: (
        "effort command; remove the duplicated 힘써 주 caller tail before "
        "retaining the selected seven-register command"
    ),
    958: (
        "request for an order; insert an explicit caller boundary because "
        "the runtime does not add a Korean space"
    ),
    964: (
        "negative-ability ending; normalize to the lexical stem and attach "
        "지 못- without a space"
    ),
    970: (
        "already/no-longer adverb; jointly rewrite both fixed boundaries so "
        "더는 is separated from the surrounding sentence"
    ),
    976: (
        "hortative or first-person volitional ending; complete and "
        "source-only callers, irregular Korean stems, an interrogative "
        "fixed boundary, and register-sensitive variants require caller "
        "normalization or flattening"
    ),
    982: (
        "deferential/plain intentional action or assertive benefactive "
        "request; Japanese benefactive syntax cannot be composed with the "
        "current completed Korean light verbs"
    ),
    988: (
        "future receipt or benefactive request; normalize each caller by "
        "meaning rather than literally appending 받-"
    ),
    994: (
        "past receipt or benefactive result; attributive attachment, "
        "benefactive voice, and already-completed perception require caller "
        "rewrites"
    ),
    1000: (
        "receipt connective; no direct root call in either pristine or "
        "current PK, but the full seven-register boundary remains guarded"
    ),
}

CALLER_INTEGRATION_EVIDENCE = {
    940: (
        {
            "call_site": "2:231:1:0",
            "observed_current_left": (
                "적의 공격을 신속히 물리치도록,\n"
                "엄중히 경계하며 전진하자."
            ),
            "observed_current_right": "",
            "expected_current_gap_hex": (
                "0143AC0300000143FC010000050505"
            ),
            "integration_mode": "flatten_complete_chained_caller",
            "source_free_korean_example": (
                "적의 공격을 신속히 물리치고자\n"
                "엄중히 경계하며 전진하겠습니다."
            ),
        },
        {
            "call_site": "2:499:1:0",
            "observed_current_left": (
                "전투의 승패는 병사에게 달렸다……\n"
                "모두, 너희를 믿겠다."
            ),
            "observed_current_right": "",
            "expected_current_gap_hex": (
                "0143AC0300000143FC010000050505"
            ),
            "integration_mode": "flatten_complete_chained_caller",
            "source_free_korean_example": (
                "전투에서 가장 중요한 건 병사들의 활약…\n"
                "모두, 잘 부탁합니다."
            ),
        },
        {
            "call_site": "6:4793:1:0",
            "observed_current_left": "\n더 좋은 영지를 원합니",
            "observed_current_right": "\n통치에 힘쓰겠습니",
            "expected_current_gap_hex": "0143AC030000",
            "integration_mode": "normalize_repeated_terminal_chain",
            "source_free_korean_example": (
                "\n더 좋은 영지를 원합니다\n통치에 힘쓸 테니"
            ),
        },
        {
            "call_site": "6:4793:2:0",
            "observed_current_left": "\n통치에 힘쓰겠습니",
            "observed_current_right": "니 부디…",
            "expected_current_gap_hex": "0143AC030000",
            "integration_mode": "normalize_repeated_terminal_chain",
            "source_free_korean_example": "\n통치에 힘쓸 테니 부디…",
        },
        {
            "call_site": "7:2490:6:0",
            "observed_current_left": "가세를 부탁하",
            "observed_current_right": "！",
            "expected_current_gap_hex": "0143AC030000",
            "integration_mode": "normalize_stem_and_punctuation",
            "source_free_korean_example": "가세를 부탁합니다!",
        },
    ),
    952: (
        {
            "call_site": "6:3886:3:0",
            "observed_current_left": "\n모두들, 힘써 주",
            "observed_current_right": "",
            "expected_current_gap_hex": "0143B8030000050505",
            "integration_mode": "rewrite_boundary_retain_terminal",
            "source_free_korean_example": "\n모두들, 힘써라",
        },
    ),
    958: (
        {
            "call_site": "6:3571:1:0",
            "observed_current_left": "감사한 말씀\n무엇이든",
            "observed_current_right": "",
            "expected_current_gap_hex": "0143BE030000050505",
            "integration_mode": "insert_boundary_space_retain_terminal",
            "source_free_korean_example": (
                "감사한 말씀\n무엇이든 명해 주십시오"
            ),
        },
        {
            "call_site": "6:4427:2:0",
            "observed_current_left": (
                "。필요하다면\n「지행」에서 다시"
            ),
            "observed_current_right": "",
            "expected_current_gap_hex": "0143BE030000050505",
            "integration_mode": "insert_boundary_space_retain_terminal",
            "source_free_korean_example": (
                "필요하다면\n지행에서 다시 명해 주십시오"
            ),
        },
    ),
    964: (
        {
            "call_site": "1:22:1:0",
            "observed_current_left": "원군은 바라",
            "observed_current_right": "…",
            "expected_current_gap_hex": "0143C4030000",
            "integration_mode": "direct_composition",
            "source_free_korean_example": "원군은 바라지 못합니다…",
        },
    ),
    970: (
        {
            "call_site": "1:22:2:0",
            "observed_current_left": "…",
            "observed_current_right": "손쓸 방도가 없다.",
            "expected_current_gap_hex": "0143CA030000",
            "integration_mode": "rewrite_fixed_both_boundaries",
            "source_free_korean_example": "…더는 손쓸 방도가 없다.",
        },
    ),
    976: (
        {
            "call_site": "2:548:2:0",
            "observed_current_left": (
                "는,\n다른 가문과 함께 나아가겠"
            ),
            "observed_current_right": "",
            "expected_current_gap_hex": "0143D0030000050505",
            "integration_mode": "joint_rewrite_register_terminal",
            "source_free_korean_example": (
                "는,\n다른 가문과 함께 나아갑시다"
            ),
        },
        {
            "call_site": "2:560:2:0",
            "observed_current_left": "\n지략을 다해 승기를 잡자.",
            "observed_current_right": "",
            "expected_current_gap_hex": "0143D0030000050505",
            "integration_mode": "flatten_complete_current_caller",
            "source_free_korean_example": (
                "\n지략을 다해 승기를 잡읍시다."
            ),
        },
        {
            "call_site": "6:3774:1:0",
            "observed_current_left": "에게 정전 중재를 청",
            "observed_current_right": "",
            "expected_current_gap_hex": "0143D0030000050505",
            "integration_mode": "direct_composition",
            "source_free_korean_example": "에게 정전 중재를 청합시다",
        },
        {
            "call_site": "6:4424:3:0",
            "observed_current_left": (
                "성주로서\n성하 발전을 위해 힘쓰"
            ),
            "observed_current_right": "",
            "expected_current_gap_hex": "0143D0030000050505",
            "integration_mode": "rewrite_first_person_volition",
            "source_free_korean_example": (
                "성주로서\n성하 발전을 위해 힘쓰겠습니다"
            ),
        },
        {
            "call_site": "8:1028:2:0",
            "observed_current_left": (
                "할까\n자, 어떤 방침으로 임"
            ),
            "observed_current_right": "인가…",
            "expected_current_gap_hex": "0143D0030000",
            "integration_mode": "rewrite_fixed_interrogative",
            "source_free_korean_example": (
                "적에게 노려지기 쉬운 지역임을 생각하면\n"
                "느긋하게 내정을 다듬고 있을 여유는 없으리라\n"
                "자, 어떤 방침으로 임할까…"
            ),
        },
    ),
    982: (
        {
            "call_site": "6:2161:2:0",
            "observed_current_left": "\n이만 물러가도록 하",
            "observed_current_right": "",
            "expected_current_gap_hex": "0143D6030000050505",
            "integration_mode": "normalize_duplicated_light_verb",
            "source_free_korean_example": "\n이만 물러가겠습니다",
        },
        {
            "call_site": "6:3871:1:0",
            "observed_current_left": (
                "취임은,\n대단히 죄송하지만 사양하겠습니다."
            ),
            "observed_current_right": "",
            "expected_current_gap_hex": "0143D6030000050505",
            "integration_mode": "flatten_complete_current_caller",
            "source_free_korean_example": (
                "취임은,\n대단히 죄송하지만 사양하겠습니다."
            ),
        },
        {
            "call_site": "6:3961:4:0",
            "observed_current_left": (
                "협력을 염두에 두고\n친선을 시작하고자"
            ),
            "observed_current_right": "",
            "expected_current_gap_hex": "0143D6030000050505",
            "integration_mode": "flatten_intention_caller",
            "source_free_korean_example": (
                "협력을 염두에 두고\n친선을 시작하겠습니다"
            ),
        },
        {
            "call_site": "6:4653:2:0",
            "observed_current_left": (
                "…\n당연히 몇 가지 요구는 들어주셔야 합니"
            ),
            "observed_current_right": (
                "\n그 정도 각오는 하고 오신 겁니"
            ),
            "expected_current_gap_hex": "0143D6030000",
            "integration_mode": "joint_rewrite_both_fragments",
            "source_free_korean_example": (
                "…\n당연히 몇 가지 요구는 들어주셔야 합니다"
                "\n그 정도 각오는 하고 오신 것이겠지요?"
            ),
        },
        {
            "call_site": "6:4767:1:0",
            "observed_current_left": "그럼 이로써 휴전을 맺읍시다",
            "observed_current_right": (
                "\n이후에는 좋은 관계를 맺고 싶군"
            ),
            "expected_current_gap_hex": "0143D6030000",
            "integration_mode": "flatten_complete_bilateral_caller",
            "source_free_korean_example": (
                "그럼 이로써 휴전을 맺겠습니다"
                "\n이후에는 좋은 관계를 맺고 싶습니다"
            ),
        },
        {
            "call_site": "7:334:2:0",
            "observed_current_left": "이(가)\n이번에는 거절하도록",
            "observed_current_right": (
                "\n아직 도저히 그럴 마음은…"
            ),
            "expected_current_gap_hex": "0143D6030000",
            "integration_mode": "normalize_declination",
            "source_free_korean_example": (
                "이(가)\n이번에는 거절하겠습니다"
            ),
        },
        {
            "call_site": "7:2835:3:0",
            "observed_current_left": "을 항복시켜",
            "observed_current_right": "",
            "expected_current_gap_hex": "0143D6030000050505",
            "integration_mode": "normalize_causative",
            "source_free_korean_example": "을 항복시키겠습니다",
        },
    ),
    988: (
        {
            "call_site": "1:19:2:0",
            "observed_current_left": "이",
            "observed_current_right": "。",
            "expected_current_gap_hex": "0143DC030000",
            "integration_mode": "boundary_space_punctuation",
            "source_free_korean_example": "이 받겠습니다.",
        },
        {
            "call_site": "6:3771:2:0",
            "observed_current_left": (
                "\n그것이 귀가의 뜻이라면\n그대로 받아들이"
            ),
            "observed_current_right": "",
            "expected_current_gap_hex": "0143DC030000050505",
            "integration_mode": "normalize_receipt_future",
            "source_free_korean_example": (
                "\n그것이 귀가의 뜻이라면\n그대로 받아들이겠습니다"
            ),
        },
        {
            "call_site": "6:4808:3:0",
            "observed_current_left": (
                "과는\n모든 관계를 끊어 주시"
            ),
            "observed_current_right": "",
            "expected_current_gap_hex": "0143DC030000050505",
            "integration_mode": "rewrite_benefactive_request",
            "source_free_korean_example": (
                "과는\n모든 관계를 끊어 주십시오"
            ),
        },
        {
            "call_site": "15:2450:3:0",
            "observed_current_left": "조력하여",
            "observed_current_right": "",
            "expected_current_gap_hex": "0143DC030000050505",
            "integration_mode": "rewrite_benefactive_request",
            "source_free_korean_example": "조력해 주십시오",
        },
    ),
    994: (
        {
            "call_site": "6:3557:1:0",
            "observed_current_left": "이토록 후하게 등용해",
            "observed_current_right": "\n",
            "expected_current_gap_hex": "0143E2030000",
            "integration_mode": "rewrite_benefactive_past",
            "source_free_korean_example": (
                "이토록 후하게 등용해 주셨습니다\n"
            ),
        },
        {
            "call_site": "6:4179:1:0",
            "observed_current_left": (
                "상황이 변화하였기에\n공략 지시를"
            ),
            "observed_current_right": "성을\n공격할 수 있",
            "expected_current_gap_hex": "0143E2030000",
            "integration_mode": "rewrite_attributive_receipt",
            "source_free_korean_example": (
                "상황이 변화하였기에\n공략 지시를 받은 성을\n"
                "공격할 수 있습니다"
            ),
        },
        {
            "call_site": "6:4747:1:0",
            "observed_current_left": "의 진심을 보았습니",
            "observed_current_right": "\n이만큼 해 주신",
            "expected_current_gap_hex": "0143E2030000",
            "integration_mode": "flatten_completed_benefactive",
            "source_free_korean_example": (
                "의 진심을 보여 주셨습니다\n이만큼 해 주신다면"
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
    "pristine PK JP authoritative; PC EN SC TC and unique full-record Base "
    "reverse match context-only; exact two-hidden-row raw preservation; "
    "seven-register terminal matrices reused from independently completed "
    "Base semantics; actual 0143 calls, 014A closures, fixed-following and "
    "source/current flatten deltas guarded; Korean caller boundaries audited "
    "without automatic spacing; complete, repeated, irregular, benefactive, "
    "hortative, ability-negative and connective callers classified; left "
    "root940 and right root1000 full policies guarded; one-line skeleton, "
    "outside-scope, reverse-overlay, two-run and Steam-read-only guarantees"
)


literal_texts = COMMON.literal_texts
gap_bytes = COMMON.gap_bytes
archive_records = COMMON.archive_records
record_signature = COMMON.record_signature
sequence_starts = COMMON.sequence_starts
incoming_jump_rows = COMMON.incoming_jump_rows
caller_context_and_gap = COMMON.caller_context_and_gap


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
    sequence = tuple(
        record_signature(records_by_label["pk_jp"], record_id)
        for record_id in OWNED_RECORD_IDS
    )
    base_hits = sequence_starts(records_by_label["base_jp"], sequence)
    pk_hits = sequence_starts(records_by_label["pk_jp"], sequence)
    if base_hits != (2337,) or pk_hits != (2405,):
        raise RuntimeError(
            f"segment {SEGMENT} source reverse search drifted: "
            f"{base_hits}/{pk_hits}"
        )
    mapping = {
        pk_record_id: base_hits[0] + ordinal
        for ordinal, pk_record_id in enumerate(OWNED_RECORD_IDS)
    }
    if (
        {pk - base for pk, base in mapping.items()} != {68}
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
        != EXPECTED_SOURCE_SHA256
        or HELPERS.canonical_sha256(
            tuple(TRANSLATIONS_BY_RECORD.values())
        )
        != EXPECTED_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} source or policy digest drifted"
        )
    full_keys = tuple(
        (BLOCK_ID, record_id) for record_id in range(2399, 2476)
    )
    for label, expected in PK_TARGET_ARCHIVE_DIGESTS.items():
        if GENERAL.subset_digest(
            records_by_label[label], RECORD_KEYS
        ) != expected:
            raise RuntimeError(
                f"segment {SEGMENT} target {label} digest drifted"
            )
    for label, expected in PK_OWNED_ARCHIVE_DIGESTS.items():
        if GENERAL.subset_digest(
            records_by_label[label], OWNED_RECORD_KEYS
        ) != expected:
            raise RuntimeError(
                f"segment {SEGMENT} owned {label} digest drifted"
            )
    for label, expected in PK_FULL_ARCHIVE_DIGESTS.items():
        if GENERAL.subset_digest(
            records_by_label[label], full_keys
        ) != expected:
            raise RuntimeError(
                f"segment {SEGMENT} full {label} digest drifted"
            )
    hidden_raw = tuple(
        (
            label,
            record_id,
            records_by_label[label][(BLOCK_ID, record_id)].data.hex().upper(),
        )
        for label in ("pk_jp", "pk_current", "pk_sc", "pk_tc", "pk_en")
        for record_id in HIDDEN_RECORD_IDS
    )
    if HELPERS.canonical_sha256(hidden_raw) != EXPECTED_HIDDEN_RAW_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} hidden raw records drifted"
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
        if pk_record_id in HIDDEN_RECORD_IDS:
            for label in PK_OWNED_ARCHIVE_DIGESTS:
                if (
                    literal_texts(records_by_label[label], pk_key) != ("",)
                    or gap_bytes(records_by_label[label][pk_key])
                    != (b"", b"\x05\x05\x05")
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} hidden skeleton drifted: "
                        f"{label}/{pk_key}"
                    )
        else:
            for label in PK_OWNED_ARCHIVE_DIGESTS:
                if (
                    len(literal_texts(records_by_label[label], pk_key)) != 1
                    or gap_bytes(records_by_label[label][pk_key])
                    != (b"", b"\x05\x05\x05")
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} visible skeleton drifted: "
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
            if ENGINE.KANA_OR_HAN_RE.search(sample):
                raise RuntimeError(
                    f"segment {SEGMENT} caller example is not "
                    f"source-free Korean: {root}/{call_site}"
                )
    if dict(counts) != EXPECTED_INTEGRATION_CLASS_COUNTS:
        raise RuntimeError(
            f"segment {SEGMENT} caller integration classes drifted"
        )


def assert_runtime_graph(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[str, tuple[tuple[int | str, ...], ...]]:
    target_ids = set(RECORD_IDS)
    owned_ids = set(OWNED_RECORD_IDS)
    full_ids = set(range(2399, 2476))
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
            (owned_ids, PK_OWNED_EDGE, "owned"),
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
    evidence = collect_call_evidence(
        records_by_label["pk_jp"],
        records_by_label["pk_current"],
    )
    if HELPERS.canonical_sha256(evidence) != EXPECTED_CALL_EVIDENCE_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} call/fixed/flatten evidence drifted"
        )
    assert_caller_evidence(records_by_label["pk_current"])
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
    if (
        HELPERS.canonical_sha256(
            tuple(
                literal_texts(source, (BLOCK_ID, record_id))[0]
                for record_id in LEFT_BOUNDARY_IDS
            )
        )
        != LEFT_BOUNDARY_SOURCE_SHA256
        or tuple(
            literal_texts(current, (BLOCK_ID, record_id))[0]
            for record_id in LEFT_BOUNDARY_IDS
        )
        != LEFT_BOUNDARY_CURRENT
        or LEFT_BOUNDARY_POLICY
        != tuple(
            BASE_POLICY[record_id - 68]
            for record_id in LEFT_BOUNDARY_IDS
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} left root940 boundary drifted"
        )
    if LEFT_PK is None:
        raise RuntimeError(
            f"segment {SEGMENT} left S1040 boundary module is unavailable"
        )
    if (
        LEFT_BOUNDARY_IDS != LEFT_PK.RIGHT_ROOT940_FULL_IDS
        or LEFT_BOUNDARY_SOURCE_SHA256
        != LEFT_PK.RIGHT_ROOT940_SOURCE_SHA256
        or LEFT_BOUNDARY_CURRENT
        != LEFT_PK.RIGHT_ROOT940_FULL_CURRENT
        or LEFT_BOUNDARY_POLICY
        != LEFT_PK.RIGHT_ROOT940_FULL_POLICY
    ):
        raise RuntimeError(
            f"segment {SEGMENT} S1040 root940 boundary contract drifted"
        )
    if (
        HELPERS.canonical_sha256(
            tuple(
                literal_texts(source, (BLOCK_ID, record_id))[0]
                for record_id in RIGHT_BOUNDARY_IDS
            )
        )
        != RIGHT_BOUNDARY_SOURCE_SHA256
        or tuple(
            literal_texts(current, (BLOCK_ID, record_id))[0]
            for record_id in RIGHT_BOUNDARY_IDS
        )
        != RIGHT_BOUNDARY_CURRENT
        or RIGHT_BOUNDARY_POLICY
        != tuple(
            BASE_POLICY[record_id - 68]
            for record_id in RIGHT_BOUNDARY_IDS
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} right root1000 boundary drifted"
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
        or len(translations) != 66
        or set(TRANSLATIONS_BY_RECORD) != set(RECORD_IDS)
        or set(RECORD_TO_ROOT) != set(RECORD_IDS)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} translation universe drifted"
        )
    BASE_LEFT.assert_semantics(dict(BASE_LEFT.TRANSLATIONS))
    BASE_RIGHT.assert_semantics(dict(BASE_RIGHT.RAW_TRANSLATIONS))
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
    for record_id in HIDDEN_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        if candidate_records[key].data != current[key].data:
            raise RuntimeError(
                f"segment {SEGMENT} hidden record changed: {key}"
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
                "runtime_assembly_evidence": {
                    "root": root,
                    "full_terminal_record_ids": list(
                        FULL_PK_GROUPS[root]
                    ),
                    "owned_terminal_record_ids": [
                        value
                        for value in FULL_PK_GROUPS[root]
                        if value in OWNED_RECORD_IDS
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
                        root not in (946, 1000)
                    ),
                    "assembly_plan": ROOT_ASSEMBLY_PLAN[root],
                    "source_free_caller_integration_examples": list(
                        CALLER_INTEGRATION_EVIDENCE.get(root, ())
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
        len(rows) != 66
        or len(validated) != 66
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
                "segment": "pk_msggame_B006_S1041",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [134, 199],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "owned_record_count": len(OWNED_RECORD_IDS),
                "source_literal_count": len(RECORD_IDS),
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "confirmed_non_display": len(HIDDEN_RECORD_IDS),
                "changed_literal_count": changed,
                "caller_integration_example_class_counts":
                EXPECTED_INTEGRATION_CLASS_COUNTS,
                "base_mapping_method":
                "global_unique_exact68_literal_gap_reverse_search",
                "discovered_base_record_range": [2337, 2404],
                "discovered_pk_minus_base_offset": offset,
                "source_sequence_sha256": EXPECTED_SOURCE_SHA256,
                "translation_policy_sha256": EXPECTED_POLICY_SHA256,
                "hidden_raw_sha256": EXPECTED_HIDDEN_RAW_SHA256,
                "pk_target_incoming_sha256": PK_TARGET_EDGE[1],
                "pk_owned_incoming_sha256": PK_OWNED_EDGE[1],
                "pk_full_group_incoming_sha256": PK_FULL_EDGE[1],
                "pk_call_fixed_flatten_evidence_sha256":
                EXPECTED_CALL_EVIDENCE_SHA256,
                "valid_incoming_014c_count": 0,
                "left_root940_full_policy": list(LEFT_BOUNDARY_POLICY),
                "right_root1000_full_policy": list(RIGHT_BOUNDARY_POLICY),
                "candidate_sha256": candidate_sha256,
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
                "target_runtime_skeleton_exact": True,
                "hidden_non_display_raw_exact": True,
                "full_graph_closures_exact": True,
                "call_fixed_flatten_evidence_exact": True,
                "source_free_current_caller_evidence_exact": True,
                "s1040_root940_boundary_contract_exact": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
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
