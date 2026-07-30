#!/usr/bin/env python3
"""Build PK block-0 runtime-terminal segment 1038 decisions."""

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

import build_base_batch005_segment1016 as BASE_LEFT
import build_base_batch005_segment1017 as BASE_RIGHT
import build_pk_batch001_segment1025 as HELPERS
import build_pk_batch005_segment1037 as LEFT_PK


ENGINE = BASE_LEFT.ENGINE
GENERAL = BASE_LEFT.GENERAL
UTIL = BASE_LEFT.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B005_S1038.private.v1.jsonl"
)
BASE_DECISIONS = (
    (
        REPO
        / "tmp"
        / WORKSTREAM.name
        / "decisions"
        / "base_msggame_B005_S1016.private.v1.jsonl",
        "CA3D0894416D1C92C23F46D24B1D1774130031160A0E8B9F198FA773C4DBDD49",
    ),
    (
        REPO
        / "tmp"
        / WORKSTREAM.name
        / "decisions"
        / "base_msggame_B005_S1017.private.v1.jsonl",
        "FB13D563291597287C9EBCDBB61887C47B427FAA45FC2365123D9FF049EF990A",
    ),
)
SEGMENT = 1038
QUEUE_BATCH_ID = "pk_msggame-B005"
BLOCK_ID = 0
QUEUE_START = 134
QUEUE_STOP = 200
BASE_RECORD_IDS = tuple(range(2137, 2203))
RECORD_IDS = tuple(range(2205, 2271))
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
TARGET_COORDINATES = tuple(
    f"{BLOCK_ID}:{record_id}:0" for record_id in RECORD_IDS
)
QUEUE_HIDDEN_COORDINATES = (
    "0:2147:0",
    "0:2149:0",
    "0:2151:0",
)
PK_RECORD_COUNT = 21751

EXPECTED_PK_JP = (
    "なければ",
    "なければ",
    "なきゃ",
    "なければ",
    "なければ",
    "なされ",
    "なされ",
    "なされ",
    "なされ",
    "なされ",
    "なされ",
    "す",
    "なされて",
    "なされて",
    "なされて",
    "なされて",
    "なされて",
    "なされて",
    "して",
    "なぞ",
    "など",
    "なぞ",
    "なぞ",
    "など",
    "など",
    "ごとき",
    "なりません",
    "ならぬ",
    "なりませぬ",
    "なりませぬ",
    "なりません",
    "なりませぬ",
    "ならん",
    "なりません",
    "ならぬ",
    "なりませぬ",
    "なりませぬ",
    "なりません",
    "ならぬ",
    "ならん",
    "なんですって",
    "なんだと",
    "なんですって",
    "なんですと",
    "なんですって",
    "何たること",
    "なんだと",
    "憎い",
    "憎き",
    "憎き",
    "憎き",
    "憎い",
    "憎き",
    "憎たらしい",
    "にくい",
    "がたい",
    "にくき",
    "づらき",
    "にくい",
    "がたき",
    "にくい",
    "くっ",
    "ぬう",
    "くっ",
    "ううむ",
    "くっ",
)
TRANSLATION_POLICY = (
    "지 않으면",
    "지 않으면",
    "지 않으면",
    "지 않으면",
    "지 않으면",
    "하시",
    "하시",
    "하시",
    "하시",
    "하시",
    "하시",
    "하",
    "하시는 것",
    "하시는 것",
    "하시는 것",
    "하시는 것",
    "하시는 것",
    "하시는 것",
    "하는 것",
    "따위",
    "따위",
    "따위",
    "따위",
    "따위",
    "따위",
    "따위",
    "안 됩니다",
    "안 된다",
    "아니 되옵니다",
    "아니 되옵니다",
    "안 됩니다",
    "아니 되옵니다",
    "안 된다",
    "안 됩니다",
    "안 된다",
    "아니 되옵니다",
    "아니 되옵니다",
    "안 됩니다",
    "안 된다",
    "안 된다",
    "뭐라고요",
    "뭐라고",
    "뭐라고요",
    "뭐라고요",
    "뭐라고요",
    "이럴 수가",
    "뭐라고",
    "미운",
    "미운",
    "미운",
    "미운",
    "미운",
    "미운",
    "얄미운",
    "하기 어려운",
    "하기 어려운",
    "하기 어려운",
    "하기 어려운",
    "하기 어려운",
    "하기 어려운",
    "하기 어려운",
    "크윽",
    "으윽",
    "크윽",
    "으음",
    "크윽",
)
TRANSLATIONS_BY_RECORD = dict(
    zip(RECORD_IDS, TRANSLATION_POLICY, strict=True)
)
TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_SOURCE_SHA256 = (
    "756161062BA5F819C9D3C89F884F09B32CE787ADF59DC9D9DD96AE5BE6C646DE"
)
EXPECTED_POLICY_SHA256 = (
    "212680F567421498A956617B26752BFA52086B415DDEB25E6BC296EF060326A2"
)
EXPECTED_MAPPING_SHA256 = (
    "530BE82A8DA820BD0DD35DCD5C8C5A01C7A633D98C0B7CFCAB172DCD08398A23"
)
EXPECTED_CHANGED_LITERAL_COUNT = 29
PK_TARGET_ARCHIVE_DIGESTS = {
    "pk_jp": "42E4F88EF48A23D9E12CD5A07D632B8F4821993E77E3272EECD84EB7CD02E072",
    "pk_current": "6E03837D33983A10EB5A971C00711F4D56CB5564D31A967F8BEC07471E66D255",
    "pk_sc": "8358267433FD9467EFA87FFA0FEA55838FEC3776CE9D18100F228301AFD81521",
    "pk_tc": "8358267433FD9467EFA87FFA0FEA55838FEC3776CE9D18100F228301AFD81521",
    "pk_en": "8358267433FD9467EFA87FFA0FEA55838FEC3776CE9D18100F228301AFD81521",
}
PK_FULL_ARCHIVE_DIGESTS = {
    "pk_jp": "F5AB3C94827F6DA8E67E26961C941327214A9E61A475BACCEA4A55CAE94912AE",
    "pk_current": "3E915540857EFCCDAC26A36125D88F363B670D33C99A39DED2FAB5B40B5B203B",
    "pk_sc": "B7306C0286544BF674C4CD22441AC31C66242B72AF28D9F287C802C4C6DB3CCC",
    "pk_tc": "B7306C0286544BF674C4CD22441AC31C66242B72AF28D9F287C802C4C6DB3CCC",
    "pk_en": "B7306C0286544BF674C4CD22441AC31C66242B72AF28D9F287C802C4C6DB3CCC",
}
PK_TARGET_EDGE_SHA256 = (
    "FFEDCABA187FC6CE928B21C1011A13725BB70887E9C0A4307352A4C3F27C236B"
)
PK_FULL_EDGE_SHA256 = (
    "9C4A70B55212C6187222DCEF59AB7F3E280F674726E262D75C0553D2FCA935A5"
)
EXPECTED_CALL_EVIDENCE_SHA256 = (
    "7EAE7DEE9D541518B5DE3FBDD5D394063AFB5024588AE83AF0ECE3D9162D2E5F"
)
ROOT784_CHAIN_GAP_SHA256 = (
    "7D70ED713CC4DEE54E5B7AAE18C673782AA00CAEF974DB4BAD015D0F74BE103F"
)

FULL_PK_GROUPS = {
    784: tuple(range(2203, 2210)),
    790: tuple(range(2210, 2217)),
    796: tuple(range(2217, 2224)),
    802: tuple(range(2224, 2231)),
    808: tuple(range(2231, 2238)),
    814: tuple(range(2238, 2245)),
    820: tuple(range(2245, 2252)),
    826: tuple(range(2252, 2259)),
    832: tuple(range(2259, 2266)),
    838: tuple(range(2266, 2273)),
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
LEFT_BOUNDARY_IDS = FULL_PK_GROUPS[784]
LEFT_BOUNDARY_JP = (
    "なければ",
    "なければ",
    "なければ",
    "なければ",
    "なきゃ",
    "なければ",
    "なければ",
)
LEFT_BOUNDARY_CURRENT = (
    "않으면",
    "않으면",
    "않으면",
    "않으면",
    "않으면",
    "않으면",
    "않으면",
)
LEFT_BOUNDARY_POLICY = (
    "지 않으면",
    "지 않으면",
    "지 않으면",
    "지 않으면",
    "지 않으면",
    "지 않으면",
    "지 않으면",
)
RIGHT_BOUNDARY_IDS = FULL_PK_GROUPS[838]
RIGHT_BOUNDARY_JP = (
    "くっ",
    "ぬう",
    "くっ",
    "ううむ",
    "くっ",
    "むう",
    "ぬうう",
)
RIGHT_BOUNDARY_CURRENT = (
    "크윽",
    "으윽",
    "크윽",
    "으음",
    "크윽",
    "으음",
    "으으윽",
)
RIGHT_BOUNDARY_POLICY = RIGHT_BOUNDARY_CURRENT
MORPHOLOGY_014C_RE = re.compile(b"\x01\x4C(.{4})", re.DOTALL)
EXPECTED_014C_OVERLAP = ((15, 25, 0, 65, 84213762),)

ROOT_ASSEMBLY_PLAN = {
    784: (
        "conditional negative suffix; normalize the Korean caller to its "
        "lexical stem before attaching 지 않으면; flatten the three "
        "root784+root730 chained sites because a bare 조건형+군 is not "
        "valid Korean"
    ),
    790: (
        "attributive honorific/plain stem rather than an imperative; "
        "normalize 출진하 to 출진 before 하시 plus fixed 는"
    ),
    796: (
        "proposal nominalization rather than a sequential connective; "
        "the fixed topic phrase must be jointly rewritten"
    ),
    802: "disparaging comparison particle 따위; no live PK caller",
    808: (
        "negative obligation or prohibition ending; direct, normalized, "
        "already-complete, and source-only-flattened callers require "
        "distinct integration"
    ),
    814: (
        "negative obligation matrix; pristine calls were flattened in "
        "current Korean and must remain registered for reintegration"
    ),
    820: "standalone spoken surprise exclamation",
    826: (
        "hateful predicate or attributive adjective before a fixed "
        "dynamic person token; caller spacing and predicate need integration"
    ),
    832: (
        "difficulty adjective; caller and following castle noun must be "
        "jointly normalized to 공략하기 어려운 성"
    ),
    838: "standalone groan/interjection",
}
CALLER_INTEGRATION_EVIDENCE = {
    784: (
        {
            "call_site": "6:3514:2:0",
            "observed_current_left": "\n더욱 힘써",
            "observed_current_right": "！",
            "expected_current_gap_hex": "014310030000",
            "integration_mode":
            "normalize_caller_and_following_punctuation",
            "source_free_korean_example": "\n더욱 힘쓰지 않으면!",
        },
        {
            "call_site": "7:2442:2:0",
            "observed_current_left": "\n앞으로의 행동을 정하",
            "observed_current_right": "",
            "expected_current_gap_hex":
            "0143100300000143DA020000050505",
            "integration_mode":
            "flatten_chained_condition_and_final_particle",
            "source_free_korean_example":
            "\n앞으로의 행동을 정해야겠군",
        },
        {
            "call_site": "15:315:2:0",
            "observed_current_left": "\n회답을 서둘러",
            "observed_current_right": "",
            "expected_current_gap_hex": "014310030000050505",
            "integration_mode": "normalize_and_retain_terminal",
            "source_free_korean_example": "\n회답을 서두르지 않으면",
        },
    ),
    790: (
        {
            "call_site": "7:2513:2:0",
            "observed_current_left": "까?\n출진하",
            "observed_current_right": "는 부대를 보강하기 위해,\n군단에서",
            "expected_current_gap_hex": "014316030000",
            "integration_mode": "normalize_and_retain_terminal",
            "source_free_korean_example": (
                "까?\n출진하시는 부대를 보강하기 위해,\n군단에서"
            ),
        },
    ),
    796: (
        {
            "call_site": "15:320:4:0",
            "observed_current_left": "접견",
            "observed_current_right": "은(는) 어떠",
            "expected_current_gap_hex": "01431C030000",
            "integration_mode": "flatten_fixed_topic_in_caller",
            "source_free_korean_example": "접견해 보시는 것이 어떠",
        },
    ),
    808: (
        {
            "call_site": "6:554:1:0",
            "observed_current_left": "사전 정지 작업을 게을리하고서는\n",
            "observed_current_right": "",
            "expected_current_gap_hex": "014328030000050505",
            "integration_mode": "direct_composition",
            "source_free_korean_example": (
                "사전 정지 작업을 게을리하고서는\n안 됩니다"
            ),
        },
        {
            "call_site": "7:884:2:0",
            "observed_current_left": "인가…\n그렇다면 그 이빨, 막아야 한다",
            "observed_current_right": "",
            "expected_current_gap_hex": "014328030000050505",
            "integration_mode": "flatten_complete_caller",
            "source_free_korean_example": (
                "인가…\n그렇다면 그 이빨을 막아야 한다"
            ),
        },
        {
            "call_site": "7:2488:2:6",
            "observed_current_left": "\n속히 진압",
            "observed_current_right": "",
            "expected_current_gap_hex":
            "014378040000014328030000050505",
            "integration_mode": "normalize_and_retain_terminal",
            "source_free_korean_example": "\n속히 진압하지 않으면 안 됩니다",
        },
        {
            "call_site": "7:2879:2:0",
            "observed_current_left": (
                "이(가) 이웃 나라에 있는 것\n더는 참을 수"
            ),
            "observed_current_right": "\n우리 군단으로 쳐부수고 오",
            "expected_current_gap_hex": "014328030000",
            "integration_mode": "flatten_complete_caller",
            "source_free_korean_example": (
                "이(가) 이웃 나라에 있는 것\n더는 참을 수 없습니다\n"
                "우리 군단으로 쳐부수고 오"
            ),
        },
        {
            "call_site": "9:3985:1:0",
            "observed_current_left": (
                "성하의 방어가 갖춰지기 전에\n여기까지 침공당하다니……\n"
                "설비가 없는 곳을 두텁게 지켜야 합니다."
            ),
            "observed_current_right": "",
            "expected_current_gap_hex": "014328030000050505",
            "integration_mode": "flatten_complete_caller",
            "source_free_korean_example": (
                "성하의 방어가 갖춰지기 전에\n여기까지 침공당하다니……\n"
                "설비가 없는 곳을 두텁게 지켜야 합니다."
            ),
        },
        {
            "call_site": "15:1572:5:0",
            "observed_current_left": (
                "을(를) 제압하려면\n그 땅을 알아야 한다"
            ),
            "observed_current_right": "",
            "expected_current_gap_hex": "014328030000050505",
            "integration_mode": "flatten_complete_caller",
            "source_free_korean_example": (
                "을(를) 제압하려면\n그 땅을 알아야 한다"
            ),
        },
        {
            "call_site": "8:286:2:0",
            "observed_current_left": (
                "\n여차하면 쌀을 거래로 손에 넣는 것도\n생각해야"
            ),
            "observed_current_right": "",
            "expected_current_gap_hex": "014328030000050505",
            "integration_mode": "flatten_complete_caller",
            "source_free_korean_example": (
                "\n여차하면 쌀을 거래로 손에 넣는 것도\n생각해야 합니다"
            ),
        },
        {
            "call_site": "6:1138:1:0",
            "observed_source_left": (
                "外に目を向けることも\n忘れては"
            ),
            "observed_source_right": "",
            "observed_current_left": (
                "바깥을 살피는 것도\n잊어서는 안 된다."
            ),
            "observed_current_right": "",
            "expected_source_gap_hex": "014328030000050505",
            "expected_current_gap_hex": "050505",
            "integration_mode": "flatten_source_command_in_current",
            "source_free_korean_example": (
                "바깥을 살피는 것도\n잊어서는 안 된다."
            ),
        },
        {
            "call_site": "8:1079:2:0",
            "observed_source_left": (
                "\n民の生活を脅かさぬよう\n余計な争いは避けねば"
            ),
            "observed_source_right": "",
            "observed_current_left": (
                "\n백성의 생활을 위협하지 않도록\n"
                "쓸데없는 싸움은 피해야 합니다."
            ),
            "observed_current_right": "",
            "expected_source_gap_hex":
            "0143280300000143DA020000050505",
            "expected_current_gap_hex": "050505",
            "integration_mode": "flatten_source_command_in_current",
            "source_free_korean_example": (
                "\n백성의 생활을 위협하지 않도록\n"
                "쓸데없는 싸움은 피해야 합니다."
            ),
        },
    ),
    814: (
        {
            "call_site": "12:18:2:0",
            "observed_source_left": (
                "\r\n　我が志、果たすその時まで\r\n"
                "　決して歩みを止めては"
            ),
            "observed_source_right": "）",
            "observed_current_left": (
                "\r\n　내 뜻을 이루는 그날까지\r\n"
                "　결코 걸음을 멈춰서는 안 된다"
            ),
            "observed_current_right": "）",
            "expected_source_gap_hex": "01432E030000",
            "expected_current_gap_hex": "",
            "integration_mode": "flatten_source_command_in_current",
            "source_free_korean_example": (
                "\r\n　내 뜻을 이루는 그날까지\r\n"
                "　결코 걸음을 멈춰서는 안 된다）"
            ),
        },
        {
            "call_site": "6:4366:1:0",
            "observed_source_left": (
                "商いを制す者が天下を制す！\n"
                "一文銭とて疎かにしては"
            ),
            "observed_source_right": "！",
            "observed_current_left": (
                "상업을 지배하는 자가 천하를 지배한다!\n"
                "한 푼의 돈도 소홀히 하지 않겠다"
            ),
            "observed_current_right": "!",
            "expected_source_gap_hex":
            "01432E030000014302020000",
            "expected_current_gap_hex": "",
            "integration_mode": "flatten_source_command_in_current",
            "source_free_korean_example": (
                "상업을 지배하는 자가 천하를 지배한다!\n"
                "한 푼의 돈도 소홀히 하지 않겠다!"
            ),
        },
    ),
    820: (
        {
            "call_site": "1:20:0:0",
            "observed_current_left": "",
            "observed_current_right": "！　",
            "expected_current_gap_hex": "014334030000",
            "integration_mode": "normalize_following_punctuation",
            "source_free_korean_example": "뭐라고요! ",
        },
    ),
    826: (
        {
            "call_site": "2:569:1:0",
            "observed_current_left": "적은 그",
            "observed_current_right": "!\n지금 여기서 쳐부수어 주",
            "expected_current_gap_hex": "01433A030000024833",
            "integration_mode": "normalize_around_fixed_dynamic_person",
            "source_free_korean_example": (
                "적은 그 미운 [동적인물]!\n지금 여기서 쳐부수어 주"
            ),
        },
    ),
    832: (
        {
            "call_site": "1:27:1:0",
            "observed_current_left": "이를 공략하여",
            "observed_current_right": "성을 참으로 잘 함락했도다!",
            "expected_current_gap_hex": "014340030000",
            "integration_mode": "flatten_attributive_castle_phrase",
            "source_free_korean_example": (
                "이 공략하기 어려운 성을 참으로 잘 함락했도다!"
            ),
        },
    ),
    838: (
        {
            "call_site": "6:3679:0:0",
            "observed_current_left": "",
            "observed_current_right": "、\n늙은이의",
            "expected_current_gap_hex": "014346030000",
            "integration_mode": "normalize_following_punctuation",
            "source_free_korean_example": "크윽,\n늙은이의",
        },
        {
            "call_site": "7:993:0:0",
            "observed_current_left": "",
            "observed_current_right": "、",
            "expected_current_gap_hex": "014346030000",
            "integration_mode": "normalize_following_punctuation",
            "source_free_korean_example": "크윽,",
        },
    ),
}
EXPECTED_INTEGRATION_CLASS_COUNTS = {
    "normalize_caller_and_following_punctuation": 1,
    "flatten_chained_condition_and_final_particle": 1,
    "normalize_and_retain_terminal": 3,
    "flatten_fixed_topic_in_caller": 1,
    "direct_composition": 1,
    "flatten_complete_caller": 5,
    "flatten_source_command_in_current": 4,
    "normalize_following_punctuation": 3,
    "normalize_around_fixed_dynamic_person": 1,
    "flatten_attributive_castle_phrase": 1,
}
BASIS = (
    "review_queue_pk_msggame_B005_zero_based_visible_ordinals134_199_"
    "pristine_pk_pc_jp_sole_translation_authority_block0_records2205_"
    "2270_66_visible_queue_hidden_three_outside_owned_segment_unique_"
    "global_exact66_literal_gap_reverse_search_discovered_Base2137_2202_"
    "uniform_plus68_not_assumed_exact_pk_base_jp_current_sc_tc_and_blank_"
    "pk_en_target66_full_boundary70_archive_digests_014a_all_labels_full_"
    "closures_0143_fixed_flatten_current_only_014c_overlap_false_positive_"
    "one_left_root784_full_right_root838_full_negative_conditional_"
    "honorific_attributive_nominalization_comparison_obligation_surprise_"
    "hateful_difficulty_interjection_policies_actual_current_caller_direct_"
    "normalize_flatten_source_free_examples_all_runtime_pending_no_"
    "historic_or_switch_korean_authority_one_line_skeleton_outside_"
    "reverse_two_run_no_steam"
)


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return BASE_LEFT.literal_texts(records, key)


def gap_bytes(record: Any) -> tuple[bytes, ...]:
    return BASE_LEFT.gap_bytes(record)


def archive_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    return BASE_LEFT.archive_records(prepared)


def record_signature(
    records: dict[tuple[int, int], Any],
    record_id: int,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    key = (BLOCK_ID, record_id)
    return (
        literal_texts(records, key),
        tuple(value.hex().upper() for value in gap_bytes(records[key])),
    )


def sequence_starts(
    records: dict[tuple[int, int], Any],
    sequence: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...],
) -> tuple[int, ...]:
    signatures = {
        record_id: record_signature(records, record_id)
        for block_id, record_id in records
        if block_id == BLOCK_ID
    }
    maximum = max(signatures)
    count = len(sequence)
    return tuple(
        start
        for start in range(maximum - count + 2)
        if all(
            signatures.get(start + ordinal) == signature
            for ordinal, signature in enumerate(sequence)
        )
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
        len(rows) != 203
        or len(visible) != 200
        or hidden != QUEUE_HIDDEN_COORDINATES
        or visible[QUEUE_START:QUEUE_STOP] != TARGET_COORDINATES
        or rows[0]["record_coordinate"] != "0:2068"
        or rows[-1]["record_coordinate"] != "0:2270"
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
    base_hits = sequence_starts(records_by_label["base_jp"], sequence)
    pk_hits = sequence_starts(records_by_label["pk_jp"], sequence)
    if base_hits != (2137,) or pk_hits != (2205,):
        raise RuntimeError(
            f"segment {SEGMENT} source reverse search drifted: "
            f"{base_hits}/{pk_hits}"
        )
    mapping = {
        pk_record_id: base_hits[0] + ordinal
        for ordinal, pk_record_id in enumerate(RECORD_IDS)
    }
    offsets = {pk_record_id - base_id for pk_record_id, base_id in mapping.items()}
    if (
        offsets != {68}
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
    if (
        HELPERS.canonical_sha256(EXPECTED_PK_JP)
        != EXPECTED_SOURCE_SHA256
        or HELPERS.canonical_sha256(TRANSLATION_POLICY)
        != EXPECTED_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} source or policy digest drifted"
        )
    full_keys = tuple((BLOCK_ID, record_id) for record_id in range(2203, 2273))
    for label, expected in PK_TARGET_ARCHIVE_DIGESTS.items():
        if GENERAL.subset_digest(records_by_label[label], RECORD_KEYS) != expected:
            raise RuntimeError(
                f"segment {SEGMENT} target {label} digest drifted"
            )
    for label, expected in PK_FULL_ARCHIVE_DIGESTS.items():
        if GENERAL.subset_digest(records_by_label[label], full_keys) != expected:
            raise RuntimeError(
                f"segment {SEGMENT} full {label} digest drifted"
            )
    for ordinal, (pk_record_id, base_record_id) in enumerate(mapping.items()):
        pk_key = (BLOCK_ID, pk_record_id)
        base_key = (BLOCK_ID, base_record_id)
        if literal_texts(records_by_label["pk_jp"], pk_key) != (
            EXPECTED_PK_JP[ordinal],
        ):
            raise RuntimeError(
                f"segment {SEGMENT} pristine PK source drifted: {pk_key}"
            )
        for label in PK_TARGET_ARCHIVE_DIGESTS:
            if (
                len(literal_texts(records_by_label[label], pk_key)) != 1
                or gap_bytes(records_by_label[label][pk_key])
                != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} PK skeleton drifted: {label}/{pk_key}"
                )
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


def assert_caller_evidence(
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
            flattened_source = mode == "flatten_source_command_in_current"
            if flattened_source:
                if call_site not in source_calls or call_site in current_calls:
                    raise RuntimeError(
                        f"segment {SEGMENT} source-only caller site "
                        f"drifted: {root}/{call_site}"
                    )
                source_left, source_right, source_gap = (
                    caller_context_and_gap(source, call_site)
                )
                if (
                    source_left != example["observed_source_left"]
                    or source_right != example["observed_source_right"]
                    or source_gap != example["expected_source_gap_hex"]
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} source-only caller context "
                        f"drifted: {root}/{call_site}"
                    )
            elif call_site not in current_calls:
                raise RuntimeError(
                    f"segment {SEGMENT} caller site drifted: "
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
                    f"segment {SEGMENT} caller context drifted: "
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
    full_ids = set(range(2203, 2273))
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
            len(target_edges) != 66
            or HELPERS.canonical_sha256(target_edges)
            != PK_TARGET_EDGE_SHA256
            or len(full_edges) != 70
            or HELPERS.canonical_sha256(full_edges)
            != PK_FULL_EDGE_SHA256
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} incoming graph drifted"
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
    root784_chain_gap = gap_bytes(
        records_by_label["pk_current"][(7, 2442)]
    )[2]
    root784_chain_targets = tuple(
        struct.unpack("<I", match.group(1))[0]
        for match in HELPERS.MORPHOLOGY_COMMAND_RE.finditer(
            root784_chain_gap
        )
    )
    if (
        hashlib.sha256(root784_chain_gap).hexdigest().upper()
        != ROOT784_CHAIN_GAP_SHA256
        or root784_chain_targets != (784, 730)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} root784 chained condition/final "
            "particle evidence drifted"
        )
    assert_caller_evidence(
        records_by_label["pk_jp"],
        records_by_label["pk_current"],
    )
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
        tuple(
            literal_texts(source, (BLOCK_ID, record_id))[0]
            for record_id in LEFT_BOUNDARY_IDS
        )
        != LEFT_BOUNDARY_JP
        or tuple(
            literal_texts(current, (BLOCK_ID, record_id))[0]
            for record_id in LEFT_BOUNDARY_IDS
        )
        != LEFT_BOUNDARY_CURRENT
        or LEFT_BOUNDARY_POLICY
        != tuple(
            BASE_LEFT.FULL_TRANSLATION_POLICY[record_id - 68]
            for record_id in LEFT_BOUNDARY_IDS
        )
        or LEFT_BOUNDARY_IDS != LEFT_PK.RIGHT_BOUNDARY_IDS
        or LEFT_BOUNDARY_JP != LEFT_PK.RIGHT_BOUNDARY_JP
        or LEFT_BOUNDARY_CURRENT != LEFT_PK.RIGHT_BOUNDARY_CURRENT
        or LEFT_BOUNDARY_POLICY != LEFT_PK.RIGHT_BOUNDARY_POLICY
    ):
        raise RuntimeError(
            f"segment {SEGMENT} left root784 boundary drifted"
        )
    if (
        tuple(
            literal_texts(source, (BLOCK_ID, record_id))[0]
            for record_id in RIGHT_BOUNDARY_IDS
        )
        != RIGHT_BOUNDARY_JP
        or tuple(
            literal_texts(current, (BLOCK_ID, record_id))[0]
            for record_id in RIGHT_BOUNDARY_IDS
        )
        != RIGHT_BOUNDARY_CURRENT
        or RIGHT_BOUNDARY_POLICY
        != tuple(
            BASE_RIGHT.FULL_TRANSLATION_POLICY[record_id - 68]
            for record_id in RIGHT_BOUNDARY_IDS
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} right root838 boundary drifted"
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
    for pk_record_id, base_record_id in zip(
        RECORD_IDS,
        BASE_RECORD_IDS,
        strict=True,
    ):
        expected = (
            BASE_LEFT.FULL_TRANSLATION_POLICY[base_record_id]
            if base_record_id <= 2162
            else BASE_RIGHT.FULL_TRANSLATION_POLICY[base_record_id]
        )
        if TRANSLATIONS_BY_RECORD[pk_record_id] != expected:
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
    if (
        ENGINE.rebuild_packed_with_literals(candidate, reverse)
        != resource.current_blob
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
                        root != 802
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
                "segment": "pk_msggame_B005_S1038",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [134, 199],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "source_literal_count": 66,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "confirmed_non_display": 0,
                "changed_literal_count": changed,
                "caller_integration_example_class_counts":
                EXPECTED_INTEGRATION_CLASS_COUNTS,
                "base_mapping_method":
                "global_unique_contiguous_literal_gap_reverse_search",
                "discovered_base_record_range": [2137, 2202],
                "discovered_pk_minus_base_offset": offset,
                "source_sequence_sha256": EXPECTED_SOURCE_SHA256,
                "translation_policy_sha256": EXPECTED_POLICY_SHA256,
                "pk_target_incoming_sha256": PK_TARGET_EDGE_SHA256,
                "pk_full_group_incoming_sha256": PK_FULL_EDGE_SHA256,
                "pk_call_fixed_flatten_evidence_sha256":
                EXPECTED_CALL_EVIDENCE_SHA256,
                "root784_chained_gap_sha256":
                ROOT784_CHAIN_GAP_SHA256,
                "valid_incoming_014c_count": 0,
                "left_root784_full_policy": list(LEFT_BOUNDARY_POLICY),
                "right_root838_full_policy": list(RIGHT_BOUNDARY_POLICY),
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
                "source_free_current_caller_evidence_exact": True,
                "s1037_root784_boundary_contract_exact": True,
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
