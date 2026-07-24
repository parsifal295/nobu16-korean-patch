#!/usr/bin/env python3
"""Build PK block-0 runtime-terminal segment 1036 decisions."""

from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch004_segment1014 as BASE_PREV
import build_base_batch005_segment1015 as BASE_CURRENT
import build_pk_batch001_segment1025 as HELPERS
import build_pk_batch004_segment1035 as LEFT_PK


ENGINE = BASE_PREV.ENGINE
GENERAL = BASE_PREV.GENERAL
UTIL = BASE_PREV.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B005_S1036.private.v1.jsonl"
)
BASE_DECISIONS = (
    (
        REPO
        / "tmp"
        / WORKSTREAM.name
        / "decisions"
        / "base_msggame_B004_S1014.private.v1.jsonl",
        "DCB63A91FEBA238727F7CCDC6911D974E40E19E64CC93A86DEA65BC39D6D5F2F",
    ),
    (
        REPO
        / "tmp"
        / WORKSTREAM.name
        / "decisions"
        / "base_msggame_B005_S1015.private.v1.jsonl",
        "34F8B17E10F324BFFC50596DEBED3A6CA2190714FC5C7BBC165D5A0103C2F1A3",
    ),
)
SEGMENT = 1036
QUEUE_BATCH_ID = "pk_msggame-B005"
BLOCK_ID = 0
QUEUE_START = 0
QUEUE_STOP = 67
BASE_RECORD_IDS = tuple(range(2000, 2067))
RECORD_IDS = tuple(range(2068, 2135))
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
TARGET_COORDINATES = tuple(
    f"{BLOCK_ID}:{record_id}:0" for record_id in RECORD_IDS
)
QUEUE_HIDDEN_COORDINATES = (
    "0:2147:0",
    "0:2149:0",
    "0:2151:0",
)

# Pristine PK PC JP is the sole translation authority.  The tuple is embedded
# here so that reverse mapping and semantic review remain source-bearing.
EXPECTED_PK_JP = (
    "で",
    "で",
    "てません",
    "てぬ",
    "てませぬ",
    "てませぬ",
    "てません",
    "てませぬ",
    "てぬ",
    "では",
    "では",
    "それでは",
    "ならば",
    "じゃあ",
    "では",
    "じゃあ",
    "では",
    "では",
    "では",
    "では",
    "では",
    "では",
    "じゃ",
    "ではない",
    "ならざる",
    "ではない",
    "ならざる",
    "ではない",
    "でない",
    "じゃない",
    "ではありません",
    "ではない",
    "ではございませぬ",
    "ではございませぬ",
    "ではありません",
    "ではござらぬ",
    "じゃねえ",
    "どう",
    "どう",
    "いかが",
    "いかが",
    "どう",
    "いかが",
    "どう",
    "どきなさい",
    "どけ",
    "おどきなされ",
    "どいてくだされ",
    "どいてください",
    "どきなされ",
    "どけ",
    "とのこと",
    "とのこと",
    "との話",
    "との話",
    "ということ",
    "との由",
    "って話",
    "ね",
    "な",
    "ですね",
    "な",
    "わね",
    "な",
    "な",
    "わ",
    "な",
)

# These Korean terminals were reviewed directly against EXPECTED_PK_JP and
# actual PK callers.  Completed Base decisions are checked only afterward as
# auxiliary consistency evidence.
TRANSLATION_POLICY = (
    "이고",
    "이고",
    "지 못합니다",
    "지 못한다",
    "지 못하옵니다",
    "지 못하옵니다",
    "지 못합니다",
    "지 못하옵니다",
    "지 못한다",
    "그러면",
    "그러면",
    "그렇다면",
    "그렇다면",
    "그럼",
    "그러면",
    "그럼",
    "인데",
    "인데",
    "인데",
    "인데",
    "인데",
    "인데",
    "인데",
    "이 아니다",
    "아닌",
    "이 아니다",
    "아닌",
    "이 아니다",
    "아니다",
    "이 아니다",
    "이 아닙니다",
    "이 아니다",
    "이 아니옵니다",
    "이 아니옵니다",
    "이 아닙니다",
    "이 아니오",
    "아니다",
    "어떻습니까",
    "어떠한가",
    "어떠하옵니까",
    "어떠하옵니까",
    "어떻습니까",
    "어떠하오",
    "어떠한가",
    "비키시오",
    "비켜라",
    "비키시오",
    "비켜 주시오",
    "비켜 주십시오",
    "비키시오",
    "비켜라",
    "라는 소식",
    "라는 소식",
    "라는 이야기",
    "라는 이야기",
    "라는 것",
    "라는 소식",
    "라는 이야기",
    "지요",
    "군",
    "이지요",
    "군",
    "네요",
    "군",
    "군",
    "네요",
    "군",
)
TRANSLATIONS_BY_RECORD = dict(
    zip(RECORD_IDS, TRANSLATION_POLICY, strict=True)
)
TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_SEQUENCE_SHA256 = (
    "225F1A8E5CB750F62B5D9E8E80F1F76AA6CA95DB080389B44C956CB7F080461F"
)
EXPECTED_POLICY_SHA256 = (
    "191BAAE2A6028481030451AAC2E609E2C71410754128E87D8EBA8C4D0957F89D"
)
EXPECTED_CHANGED_LITERAL_COUNT = 34
PK_RECORD_COUNT = 21751
PK_TARGET_ARCHIVE_DIGESTS = {
    "pk_jp": "A07AF06A985D1F5098CF007B0FD352F1493737B15EEC75A0A8661EFDD8B8082F",
    "pk_current": "BA3271F107DB356DCAB1A187FE72CE3FE62D6DE199607B1C2201D687900A06E3",
    "pk_sc": "AA4D43A2813D3D4F78B98A40A606B1D9990F6F967023E4F9615EEB1DA945E6B3",
    "pk_tc": "AA4D43A2813D3D4F78B98A40A606B1D9990F6F967023E4F9615EEB1DA945E6B3",
    "pk_en": "AA4D43A2813D3D4F78B98A40A606B1D9990F6F967023E4F9615EEB1DA945E6B3",
}
PK_FULL_ARCHIVE_DIGESTS = {
    "pk_jp": "C5373932BE3EBC4DBBB786623D2494547056F225D56251BFB9D56CCBEAA9E19F",
    "pk_current": "D19B1CF74A5F84CB95B222C05EE180913C8E877C350A193906ED863F71EE7106",
    "pk_sc": "D7E206848AAF516992C101D1029D7CB75C3C459CC60ECD856FC901A2C26069C4",
    "pk_tc": "D7E206848AAF516992C101D1029D7CB75C3C459CC60ECD856FC901A2C26069C4",
    "pk_en": "D7E206848AAF516992C101D1029D7CB75C3C459CC60ECD856FC901A2C26069C4",
}
PK_TARGET_JUMP_EDGE_SHA256 = (
    "19EC5CAAFF0E992F323D0423F45D7BDB30D952BFAA75287A327EDB616E7C84D9"
)
PK_FULL_GROUP_JUMP_EDGE_SHA256 = (
    "3BBD0FDB281E93C9BA5983FAE7F9A210D4C5A3E73B319DF4794125DF09CFC7FF"
)
EXPECTED_CALL_EVIDENCE_SHA256 = (
    "275E64C36D6F3653FE367AF63023ED3660CFB98020D7F40225DB8275222ACA8F"
)
EXPECTED_CALLER_CONTEXT_SHA256 = (
    "D1D01269F7A53576A3C16DD354FBAF743016E7FC0A7BA6B6EE6039BE48CB3AB2"
)

FULL_PK_GROUPS = {
    664: tuple(range(2063, 2070)),
    670: tuple(range(2070, 2077)),
    676: tuple(range(2077, 2084)),
    682: tuple(range(2084, 2091)),
    688: tuple(range(2091, 2098)),
    694: tuple(range(2098, 2105)),
    700: tuple(range(2105, 2112)),
    706: tuple(range(2112, 2119)),
    712: tuple(range(2119, 2126)),
    718: tuple(range(2126, 2133)),
    724: tuple(range(2133, 2140)),
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

LEFT_ROOT664_FULL_IDS = FULL_PK_GROUPS[664]
LEFT_ROOT664_FULL_JP = (
    "で",
    "で",
    "でございまして",
    "でして",
    "でして",
    "で",
    "で",
)
LEFT_ROOT664_FULL_CURRENT = (
    "에서",
    "에서",
    "이옵고",
    "이어서",
    "이어서",
    "에서",
    "에서",
)
LEFT_ROOT664_FULL_POLICY = (
    "이고",
    "이고",
    "이옵고",
    "이며",
    "이며",
    "이고",
    "이고",
)
RIGHT_ROOT724_FULL_IDS = FULL_PK_GROUPS[724]
RIGHT_ROOT724_FULL_JP = (
    "わ",
    "な",
    "ね",
    "な",
    "わね",
    "な",
    "な",
)
RIGHT_ROOT724_FULL_CURRENT = (
    "와",
    "군",
    "군",
    "군",
    "네",
    "군",
    "군",
)
RIGHT_ROOT724_FULL_POLICY = (
    "네요",
    "군",
    "지요",
    "군",
    "네요",
    "군",
    "군",
)

MORPHOLOGY_014C_RE = re.compile(b"\x01\x4C(.{4})", re.DOTALL)
EXPECTED_014C_OVERLAP = ((15, 25, 0, 65, 84213762),)

ROOT_ASSEMBLY_PLAN = {
    664: (
        "no live 0143 caller; preserve the connective-copula register "
        "matrix as a guarded runtime terminal family"
    ),
    670: (
        "normalize potential-verb callers to a Korean action stem before "
        "the negative-ability terminal; flatten an already finite caller"
    ),
    676: (
        "rewrite the fixed following caller to provide a Korean lexical "
        "separator after the discourse-conditional terminal"
    ),
    682: (
        "the sole current caller already expresses the unfinished "
        "contrast and must be flattened instead of double-composed"
    ),
    688: (
        "no live 0143 caller; preserve the negative-copula register "
        "matrix as a guarded runtime terminal family"
    ),
    694: (
        "normalize the Korean copular case at a nominal caller and "
        "flatten the fixed interrogative continuation"
    ),
    700: (
        "current callers already contain proposal-question wording; "
        "normalize a retained predicate or flatten/rewrite complete callers"
    ),
    706: (
        "rewrite the caller boundary with a Korean lexical separator "
        "before the movement command"
    ),
    712: (
        "compose after a Korean proposition where compatible; flatten "
        "callers that already contain a complete report"
    ),
    718: (
        "compose after a compatible Korean stem; normalize finite stems "
        "or flatten an already complete current sentence"
    ),
    724: (
        "compose after a compatible Korean stem; normalize continuative "
        "stems or flatten already complete current sentences"
    ),
}

# Each example is tied to an actual current PK call site.  The example output
# is Korean-only and states the caller repair that the later integration pass
# must make; no historical Korean string is treated as semantic authority.
CALLER_INTEGRATION_EVIDENCE = {
    670: (
        {
            "call_site": "6:3520:1:0",
            "observed_current_left": (
                "이(가) 훈공 일위라니…\n"
                "아랫사람은 무작정 땀 흘리는 것으로밖에\n"
                "보탬이 될"
            ),
            "observed_current_right": "…그 일념으로",
            "integration_mode": "normalize_and_retain_terminal",
            "source_free_korean_example": (
                "이(가) 훈공 일위라니…\n"
                "아랫사람은 무작정 땀 흘리는 것으로밖에\n"
                "보탬이 되지 못합니다…그 일념으로"
            ),
        },
        {
            "call_site": "7:2514:2:0",
            "observed_current_left": "도움이 되지 못하겠군",
            "observed_current_right": "…\n",
            "integration_mode": "flatten_call_in_caller",
            "source_free_korean_example": "도움이 되지 못하겠군…\n",
        },
    ),
    676: (
        {
            "call_site": "6:4733:2:0",
            "observed_current_left": "？\n",
            "observed_current_right": "께서는 직접 짐만 꾸리도록 하시",
            "integration_mode":
            "rewrite_fixed_following_and_normalize_punctuation",
            "source_free_korean_example": (
                "?\n그렇다면 [동적 인물명]께서는 직접 짐만 꾸리도록 하시"
            ),
        },
    ),
    682: (
        {
            "call_site": "6:4893:2:0",
            "observed_current_left": "다는\n그런 약속이었을 텐데요",
            "observed_current_right": "…",
            "integration_mode": "flatten_call_in_caller",
            "source_free_korean_example": (
                "다는\n그런 약속이었을 텐데요…"
            ),
        },
    ),
    694: (
        {
            "call_site": "6:4608:1:6",
            "observed_current_left": "、",
            "observed_current_right": "인가\n",
            "integration_mode":
            "flatten_fixed_interrogative_and_normalize_punctuation",
            "source_free_korean_example": ", 아니옵니까\n",
        },
        {
            "call_site": "7:2485:1:0",
            "observed_current_left": "충분한 병력을 낼 수 있는 출진지",
            "observed_current_right": "",
            "integration_mode": "normalize_nominal_case",
            "source_free_korean_example": (
                "충분한 병력을 낼 수 있는 출진지가 아닙니다"
            ),
        },
    ),
    700: (
        {
            "call_site": "6:2074:3:0",
            "observed_current_left": (
                "\n다시금 지침을 보이시는 것이 어떠할지"
            ),
            "observed_current_right": "인가",
            "integration_mode": "flatten_and_rewrite_question",
            "source_free_korean_example": (
                "\n다시금 지침을 보이시는 것이 어떻습니까"
            ),
        },
        {
            "call_site": "6:4245:1:0",
            "observed_current_left": "그렇다면,\n이쪽의 책략은",
            "observed_current_right": "",
            "integration_mode": "normalize_and_retain_terminal",
            "source_free_korean_example": (
                "그렇다면,\n이쪽의 책략은 어떻습니까"
            ),
        },
        {
            "call_site": "15:2467:1:0",
            "observed_current_left": "평정중을 임명하시겠습니까",
            "observed_current_right": (
                "\n가문의 방침을 정하고 결속을 다지려면\n"
                "평정중의 역할이 중요합니다"
            ),
            "integration_mode": "flatten_call_in_caller",
            "source_free_korean_example": (
                "평정중을 임명하시겠습니까\n"
                "가문의 방침을 정하고 결속을 다지려면\n"
                "평정중의 역할이 중요합니다"
            ),
        },
    ),
    706: (
        {
            "call_site": "1:20:3:0",
            "observed_current_left": "! 에잇, 그곳을",
            "observed_current_right": "！",
            "integration_mode":
            "rewrite_lexical_boundary_and_normalize_following_punctuation",
            "source_free_korean_example": "! 에잇, 그곳을 비키시오!",
        },
    ),
    712: (
        {
            "call_site": "1:21:1:0",
            "observed_current_left": "아무래도 호게호게",
            "observed_current_right": "…어떠한가",
            "integration_mode": "direct_composition",
            "source_free_korean_example": (
                "아무래도 호게호게라는 소식…어떠한가"
            ),
        },
        {
            "call_site": "8:314:2:0",
            "observed_current_left": (
                "\n허나 미리 손을 써 둔 덕에\n해를 면한 땅이 있소"
            ),
            "observed_current_right": "",
            "integration_mode": "flatten_call_in_caller",
            "source_free_korean_example": (
                "\n허나 미리 손을 써 둔 덕에\n해를 면한 땅이 있소"
            ),
        },
    ),
    718: (
        {
            "call_site": "6:3764:2:0",
            "observed_current_left": (
                "가\n앞날을 내다보고 신용을 쌓는 것도 나쁘지 않"
            ),
            "observed_current_right": "",
            "integration_mode": "direct_composition",
            "source_free_korean_example": (
                "가\n앞날을 내다보고 신용을 쌓는 것도 나쁘지 않지요"
            ),
        },
        {
            "call_site": "7:829:1:0",
            "observed_current_left": (
                "이(가) 이토록 쇠퇴할 줄이야…\n"
                "이대로 섬겨도 미래는 없다"
            ),
            "observed_current_right": (
                "\n충성을 다하는 것도 여기까지라"
            ),
            "integration_mode": "normalize_and_retain_terminal",
            "source_free_korean_example": (
                "이(가) 이토록 쇠퇴할 줄이야…\n"
                "이대로 섬겨도 미래는 없군\n"
                "충성을 다하는 것도 여기까지라"
            ),
        },
        {
            "call_site": "15:2557:5:6",
            "observed_current_left": (
                "고 하니,\n감장을 몇 장 써도 모자랍니다"
            ),
            "observed_current_right": "！",
            "integration_mode":
            "flatten_call_and_normalize_following_punctuation",
            "source_free_korean_example": (
                "고 하니,\n감장을 몇 장 써도 모자랍니다!"
            ),
        },
    ),
    724: (
        {
            "call_site": "2:223:1:6",
            "observed_current_left": "의 차례인 듯",
            "observed_current_right": "\n특기인 이 언변으로",
            "integration_mode": "direct_composition",
            "source_free_korean_example": (
                "의 차례인 듯군\n특기인 이 언변으로"
            ),
        },
        {
            "call_site": "6:3861:1:6",
            "observed_current_left": (
                "조정의 신용을 충분히 얻었지만,\n"
                "관직에 빈자리가 없다고 합니다……\n"
                "헌금을 중단하고 기다릴 수밖에 없습니다."
            ),
            "observed_current_right": "",
            "integration_mode": "flatten_call_in_caller",
            "source_free_korean_example": (
                "조정의 신용을 충분히 얻었지만,\n"
                "관직에 빈자리가 없다고 합니다……\n"
                "헌금을 중단하고 기다릴 수밖에 없습니다."
            ),
        },
        {
            "call_site": "6:3972:1:6",
            "observed_current_left": (
                "적의 위신이 당가를 웃돌아 병사들이\n"
                "다소 불안해하고"
            ),
            "observed_current_right": "…\n부디 방심하지 않도록",
            "integration_mode": "normalize_and_retain_terminal",
            "source_free_korean_example": (
                "적의 위신이 당가를 웃돌아 병사들이\n"
                "다소 불안해하는군…\n부디 방심하지 않도록"
            ),
        },
    ),
}

BASIS = (
    "review_queue_pk_msggame_B005_zero_based_visible_ordinals0_66_"
    "pristine_pk_pc_jp_sole_translation_authority_block0_records2068_"
    "2134_67_visible_queue_hidden_three_all_outside_owned_slice_"
    "global_unique_contiguous_literal_gap_reverse_search_discovered_"
    "minus68_Base_records2000_2066_auxiliary_only_exact_pk_base_jp_"
    "current_sc_tc_empty_pk_en_target_and_full_subset_digests_"
    "actual_014a_incoming_source_current_full_eleven_closures_"
    "actual_0143_source_current_calls_fixed_source_only_flatten_current_"
    "only_and_all_caller_left_right_context_digest_014c_valid_zero_"
    "overlap_false_positive_one_full_left_root664_cross_S1035_and_full_"
    "right_root724_boundaries_source_borne_negative_ability_discourse_"
    "unfinished_contrast_negative_copula_proposal_command_quotative_"
    "terminal_particle_register_matrices_source_free_direct_normalize_"
    "flatten_rewrite_examples_all_runtime_fragments_evidence_classified_"
    "no_historic_or_switch_korean_authority_one_line_protected_skeleton_"
    "outside_reverse_exact_no_steam"
)


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return BASE_PREV.literal_texts(records, key)


def gap_bytes(record: Any) -> tuple[bytes, ...]:
    return BASE_PREV.gap_bytes(record)


def archive_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    return BASE_PREV.archive_records(prepared)


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


def call_context_rows(
    records: dict[tuple[int, int], Any],
    root: int,
) -> tuple[tuple[str, str, str], ...]:
    rows: list[tuple[str, str, str]] = []
    for site in HELPERS.root_call_sites(records, root):
        block_id, record_id, gap_id, _ = (
            int(value) for value in site.split(":")
        )
        literals = ENGINE.parse_record_literals(
            records[(block_id, record_id)]
        )
        rows.append(
            (
                site,
                literals[gap_id - 1].text if gap_id else "",
                literals[gap_id].text if gap_id < len(literals) else "",
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
    expected_sequence = tuple(
        ((source,), ("", "050505"))
        for source in EXPECTED_PK_JP
    )
    if (
        HELPERS.canonical_sha256(expected_sequence)
        != EXPECTED_SEQUENCE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} expected source sequence drifted"
        )
    base_hits = sequence_starts(
        records_by_label["base_jp"],
        expected_sequence,
    )
    pk_hits = sequence_starts(
        records_by_label["pk_jp"],
        expected_sequence,
    )
    if base_hits != (2000,) or pk_hits != (2068,):
        raise RuntimeError(
            f"segment {SEGMENT} global source reverse search drifted"
        )
    offset = pk_hits[0] - base_hits[0]
    mapping = {
        pk_record_id: pk_record_id - offset
        for pk_record_id in RECORD_IDS
    }
    if offset != 68 or tuple(mapping.values()) != BASE_RECORD_IDS:
        raise RuntimeError(
            f"segment {SEGMENT} discovered record mapping drifted"
        )
    return mapping, offset


def assert_source_and_runtime(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    mapping: dict[int, int],
) -> None:
    if (
        HELPERS.canonical_sha256(TRANSLATION_POLICY)
        != EXPECTED_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} translation policy digest drifted"
        )
    full_keys = tuple((BLOCK_ID, value) for value in range(2063, 2140))
    for label, expected_digest in PK_TARGET_ARCHIVE_DIGESTS.items():
        if (
            GENERAL.subset_digest(records_by_label[label], RECORD_KEYS)
            != expected_digest
            or GENERAL.subset_digest(records_by_label[label], full_keys)
            != PK_FULL_ARCHIVE_DIGESTS[label]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} independent {label} digest drifted"
            )
    for ordinal, (pk_record_id, base_record_id) in enumerate(
        mapping.items()
    ):
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
        if literal_texts(records_by_label["pk_jp"], pk_key) != (
            EXPECTED_PK_JP[ordinal],
        ):
            raise RuntimeError(
                f"segment {SEGMENT} pristine PK source drifted: {pk_key}"
            )
        for language in ("jp", "current", "sc", "tc"):
            if literal_texts(
                records_by_label[f"pk_{language}"],
                pk_key,
            ) != literal_texts(
                records_by_label[f"base_{language}"],
                base_key,
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
    current: dict[tuple[int, int], Any],
) -> None:
    for root, examples in CALLER_INTEGRATION_EVIDENCE.items():
        actual_calls = set(HELPERS.root_call_sites(current, root))
        for example in examples:
            call_site = str(example["call_site"])
            if call_site not in actual_calls:
                raise RuntimeError(
                    f"segment {SEGMENT} caller example site drifted: "
                    f"{root}/{call_site}"
                )
            block_id, record_id, gap_id, _ = (
                int(value) for value in call_site.split(":")
            )
            literals = ENGINE.parse_record_literals(
                current[(block_id, record_id)]
            )
            left = literals[gap_id - 1].text if gap_id else ""
            right = (
                literals[gap_id].text
                if gap_id < len(literals)
                else ""
            )
            if (
                left != example["observed_current_left"]
                or right != example["observed_current_right"]
                or ENGINE.KANA_OR_HAN_RE.search(
                    str(example["source_free_korean_example"])
                )
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} caller example context drifted: "
                    f"{root}/{call_site}"
                )


def assert_runtime_graph(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[
    dict[str, tuple[tuple[int | str, ...], ...]],
    dict[str, dict[str, tuple[tuple[str, str, str], ...]]],
]:
    target_ids = set(RECORD_IDS)
    full_ids = {
        record_id
        for record_ids in FULL_PK_GROUPS.values()
        for record_id in record_ids
    }
    if full_ids != set(range(2063, 2140)):
        raise RuntimeError(
            f"segment {SEGMENT} full PK group universe drifted"
        )
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    for label, records in (("pk_jp", source), ("pk_current", current)):
        target_edges = incoming_jump_rows(records, target_ids)
        full_edges = incoming_jump_rows(records, full_ids)
        if (
            len(target_edges) != 67
            or {row[4] for row in target_edges} != target_ids
            or HELPERS.canonical_sha256(target_edges)
            != PK_TARGET_JUMP_EDGE_SHA256
            or len(full_edges) != 77
            or {row[4] for row in full_edges} != full_ids
            or HELPERS.canonical_sha256(full_edges)
            != PK_FULL_GROUP_JUMP_EDGE_SHA256
        ):
            raise RuntimeError(
                f"segment {SEGMENT} independent {label} "
                "incoming jump graph drifted"
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
            f"segment {SEGMENT} independent PK "
            "call/fixed/flatten evidence drifted"
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
            f"segment {SEGMENT} caller left/right context drifted"
        )
    assert_caller_integration_evidence(current)
    return call_evidence, context_evidence


def assert_boundaries(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    actual_left_jp = tuple(
        literal_texts(source, (BLOCK_ID, record_id))[0]
        for record_id in LEFT_ROOT664_FULL_IDS
    )
    actual_left_current = tuple(
        literal_texts(current, (BLOCK_ID, record_id))[0]
        for record_id in LEFT_ROOT664_FULL_IDS
    )
    actual_right_jp = tuple(
        literal_texts(source, (BLOCK_ID, record_id))[0]
        for record_id in RIGHT_ROOT724_FULL_IDS
    )
    actual_right_current = tuple(
        literal_texts(current, (BLOCK_ID, record_id))[0]
        for record_id in RIGHT_ROOT724_FULL_IDS
    )
    if (
        actual_left_jp != LEFT_ROOT664_FULL_JP
        or actual_left_current != LEFT_ROOT664_FULL_CURRENT
        or LEFT_ROOT664_FULL_POLICY
        != tuple(
            BASE_PREV.FULL_TRANSLATION_POLICY[record_id - 68]
            for record_id in LEFT_ROOT664_FULL_IDS
        )
        or LEFT_ROOT664_FULL_IDS != LEFT_PK.RIGHT_BOUNDARY_IDS
        or LEFT_ROOT664_FULL_JP != LEFT_PK.RIGHT_BOUNDARY_JP
        or LEFT_ROOT664_FULL_CURRENT != LEFT_PK.RIGHT_BOUNDARY_CURRENT
        or LEFT_ROOT664_FULL_POLICY != LEFT_PK.RIGHT_BOUNDARY_POLICY
    ):
        raise RuntimeError(
            f"segment {SEGMENT} S1035/S1036 root664 boundary drifted"
        )
    if (
        actual_right_jp != RIGHT_ROOT724_FULL_JP
        or actual_right_current != RIGHT_ROOT724_FULL_CURRENT
        or RIGHT_ROOT724_FULL_POLICY
        != tuple(
            BASE_CURRENT.FULL_TRANSLATION_POLICY[record_id - 68]
            for record_id in RIGHT_ROOT724_FULL_IDS
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} right root724 boundary drifted"
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
        ENGINE.validate_decisions(
            prepared,
            path,
            require_complete=False,
        )
        for line in path.read_text(encoding="utf-8").splitlines():
            if line:
                row = json.loads(line)
                rows_by_coordinate[str(row["coordinate"])] = row
    for pk_record_id, base_record_id in mapping.items():
        coordinate = f"{BLOCK_ID}:{base_record_id}:0"
        row = rows_by_coordinate.get(coordinate)
        expected = TRANSLATIONS_BY_RECORD[pk_record_id]
        if (
            row is None
            or row["resource"] != "base_msggame"
            or row["semantic_review"] != "approved"
            or row["translation"] != expected
        ):
            raise RuntimeError(
                f"segment {SEGMENT} completed Base auxiliary policy "
                f"drifted: {coordinate}"
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
    for pk_record_id, base_record_id in zip(
        RECORD_IDS,
        BASE_RECORD_IDS,
        strict=True,
    ):
        base_policy = (
            BASE_PREV.FULL_TRANSLATION_POLICY
            if base_record_id in BASE_PREV.FULL_TRANSLATION_POLICY
            else BASE_CURRENT.FULL_TRANSLATION_POLICY
        )
        if TRANSLATIONS_BY_RECORD[pk_record_id] != base_policy[
            base_record_id
        ]:
            raise RuntimeError(
                f"segment {SEGMENT} auxiliary Base policy drifted: "
                f"{pk_record_id}/{base_record_id}"
            )
    if tuple(
        TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(2068, 2070)
    ) != LEFT_ROOT664_FULL_POLICY[-2:]:
        raise RuntimeError(
            f"segment {SEGMENT} left semantic boundary drifted"
        )
    if tuple(
        TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(2133, 2135)
    ) != RIGHT_ROOT724_FULL_POLICY[:2]:
        raise RuntimeError(
            f"segment {SEGMENT} right semantic boundary drifted"
        )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    translations: dict[str, str],
) -> tuple[bytes, str]:
    pk = prepared.resources["pk_msggame"]
    current = records_by_label["pk_current"]
    replacements = {
        tuple(int(value) for value in coordinate.split(":")):
        translation
        for coordinate, translation in translations.items()
    }
    reverse = {
        key: literal_texts(current, key[:2])[key[2]]
        for key in replacements
    }
    candidate = ENGINE.rebuild_packed_with_literals(
        pk.current_blob,
        replacements,
    )
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    if (
        len(current) != PK_RECORD_COUNT
        or len(candidate_records) != PK_RECORD_COUNT
        or set(replacements) != {
            (BLOCK_ID, record_id, 0) for record_id in RECORD_IDS
        }
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
            != (translations[f"{BLOCK_ID}:{record_id}:0"],)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} candidate terminal drifted: {key}"
            )
    if ENGINE.rebuild_packed_with_literals(
        candidate,
        reverse,
    ) != pk.current_blob:
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
    call_evidence, _ = assert_runtime_graph(records_by_label)
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
            or "\r" in translation
            or "\n" in translation
            or translation != translation.strip()
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation)
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
                    "owned_operand_has_exactly_one_incoming_014a": True,
                    "full_root_graph_closure_guarded": True,
                    "all_actual_caller_left_right_contexts_guarded": True,
                    "valid_incoming_014c_count": 0,
                    "automatic_space_inserted": False,
                    "live_0143_call_observed": bool(
                        evidence[0][0] or evidence[1][0]
                    ),
                    "runtime_integration_required": bool(
                        evidence[0][0] or evidence[1][0]
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
            f"segment {SEGMENT} changed count drifted"
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
    if len(validated) != 67 or len(rows) != 67:
        raise RuntimeError(
            f"segment {SEGMENT} validation count drifted"
        )
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B005_S1036",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [0, 66],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "source_literal_count": 67,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "confirmed_non_display": 0,
                "changed_literal_count": EXPECTED_CHANGED_LITERAL_COUNT,
                "base_mapping_method":
                "global_unique_contiguous_literal_gap_reverse_search",
                "discovered_base_record_range": [
                    BASE_RECORD_IDS[0],
                    BASE_RECORD_IDS[-1],
                ],
                "discovered_pk_minus_base_offset": offset,
                "source_sequence_sha256": EXPECTED_SEQUENCE_SHA256,
                "translation_policy_sha256": EXPECTED_POLICY_SHA256,
                "pk_target_incoming_sha256":
                PK_TARGET_JUMP_EDGE_SHA256,
                "pk_full_group_incoming_sha256":
                PK_FULL_GROUP_JUMP_EDGE_SHA256,
                "pk_call_fixed_flatten_evidence_sha256":
                EXPECTED_CALL_EVIDENCE_SHA256,
                "pk_all_caller_context_sha256":
                EXPECTED_CALLER_CONTEXT_SHA256,
                "valid_incoming_014c_count": 0,
                "left_root664_full_policy":
                list(LEFT_ROOT664_FULL_POLICY),
                "right_root724_full_policy":
                list(RIGHT_ROOT724_FULL_POLICY),
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
                "all_actual_caller_contexts_exact": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "s1035_root664_boundary_contract_exact": True,
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
