#!/usr/bin/env python3
"""Build source-redacted PK block-0 runtime-terminal segment 1039."""

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

import build_base_batch005_segment1017 as BASE_LEFT
import build_base_batch006_segment1018 as BASE_RIGHT
import build_pk_batch001_segment1025 as HELPERS
import build_pk_batch005_segment1038 as LEFT_PK


ENGINE = BASE_LEFT.ENGINE
GENERAL = BASE_LEFT.GENERAL
UTIL = BASE_LEFT.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B006_S1039.private.v1.jsonl"
)
BASE_DECISIONS = (
    (
        REPO
        / "tmp"
        / WORKSTREAM.name
        / "decisions"
        / "base_msggame_B005_S1017.private.v1.jsonl",
        "FB13D563291597287C9EBCDBB61887C47B427FAA45FC2365123D9FF049EF990A",
    ),
    (
        REPO
        / "tmp"
        / WORKSTREAM.name
        / "decisions"
        / "base_msggame_B006_S1018.private.v1.jsonl",
        "0651CC4E77A5B21E6FBD713AA33019B10BE3164DF6081165122D09A9F365A224",
    ),
)
SEGMENT = 1039
QUEUE_BATCH_ID = "pk_msggame-B006"
BLOCK_ID = 0
QUEUE_START = 0
QUEUE_STOP = 67
BASE_RECORD_IDS = tuple(range(2203, 2270))
RECORD_IDS = tuple(range(2271, 2338))
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
TARGET_COORDINATES = tuple(
    f"{BLOCK_ID}:{record_id}:0" for record_id in RECORD_IDS
)
QUEUE_HIDDEN_COORDINATES = ("0:2406:0", "0:2410:0")
PK_RECORD_COUNT = 21751

# Source text is intentionally absent from this tracked builder.  Exact
# pristine-PK source, control gaps, sequence, and caller contexts are guarded
# by their independent hashes below and are read only at execution time.
EXPECTED_SOURCE_SEQUENCE_SHA256 = (
    "5B34A9D763AA7C2297DEB783B5E4054B9BCAC9A117DB5697DB99159852EA2FF5"
)
EXPECTED_MAPPING_SHA256 = (
    "79485CBE19C40E73DF0BC4ECFC0AD957C547F9AA6D579C3350AB89622CF7C474"
)
EXPECTED_POLICY_SHA256 = (
    "49D50C6AD51BE276C0B4FAFB44EA7F465463A98BF4669651E132699F97783A0E"
)
EXPECTED_CHANGED_LITERAL_COUNT = 52

FULL_PK_GROUPS = {
    838: tuple(range(2266, 2273)),
    844: tuple(range(2273, 2280)),
    850: tuple(range(2280, 2287)),
    856: tuple(range(2287, 2294)),
    862: tuple(range(2294, 2301)),
    868: tuple(range(2301, 2308)),
    874: tuple(range(2308, 2315)),
    880: tuple(range(2315, 2322)),
    886: tuple(range(2322, 2329)),
    892: tuple(range(2329, 2336)),
    898: tuple(range(2336, 2343)),
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

CUSTOM_ROOT892_POLICY = (
    "겠지요",
    "리라",
    "겠사옵니다",
    "겠사옵니다",
    "겠지요",
    "겠소",
    "리라",
)
EXPECTED_CUSTOM_ROOT892_POLICY_SHA256 = (
    "88629494BD5E7FA2EAE2BD477F0CF436D90582986E2042E3CDA427513D163B69"
)
EXPECTED_AUX_BASE_ROOT880_POLICY_SHA256 = (
    "9EB1EB15A2F03AEE29AD7AE82849AB0A53AAE213DB6F8EECB9A397809AE8EDEE"
)
CUSTOM_ROOT844_POLICY = (
    "지요",
    "이군",
    "이지요",
    "이군요",
    "지요",
    "이로군",
    "이군",
)
EXPECTED_CUSTOM_ROOT844_POLICY_SHA256 = (
    "B920B028F73FA7DB5ACE348F9AA1DF0D4A3B001BE56D3D16E6555EA8E76618FD"
)
EXPECTED_AUX_BASE_ROOT832_POLICY_SHA256 = (
    "F810C4ABAAF23FEC795A2E9784511D42666F6160FE917C62C3227DF2ED2868F9"
)
AUXILIARY_BASE_DIVERGENCE_RECORD_IDS = frozenset(
    (2273, 2277, *range(2329, 2336))
)

TRANSLATION_MATRICES = {
    838: (
        "크윽",
        "으윽",
        "크윽",
        "으음",
        "크윽",
        "으음",
        "으으윽",
    ),
    844: CUSTOM_ROOT844_POLICY,
    850: (
        "것입니다",
        "것이다",
        "것입니다",
        "것입니다",
        "것입니다",
        "것이다",
        "것이니라",
    ),
    856: (
        "것입니다",
        "것이다",
        "것이옵니다",
        "것입니다",
        "것입니다",
        "것입니다",
        "것이다",
    ),
    862: ("예", "예", "예", "옛", "예", "옛", "옛"),
    868: (
        "하지 않습니다",
        "하지 않는다",
        "하지 않사옵니다",
        "하지 않사옵니다",
        "하지 않습니다",
        "하지 않사옵니다",
        "하지 않는다",
    ),
    874: (
        "하시오",
        "하라",
        "하시오",
        "하시오",
        "하시오",
        "하시오",
        "하라",
    ),
    880: (
        "지 못합니다",
        "지 못한다",
        "지 못하옵니다",
        "지 못하옵니다",
        "지 못합니다",
        "지 못하옵니다",
        "지 못한다",
    ),
    886: ("어머", "호오", "이럴 수가", "호오", "어머", "흠", "호오"),
    892: CUSTOM_ROOT892_POLICY,
    898: (
        "해 주었으면 합니다",
        "해 주었으면 한다",
        "해 주시기를 바라옵니다",
        "해 주시기를 바라옵니다",
        "해 주었으면 합니다",
        "해 주었으면 하오",
        "해 주었으면 한다",
    ),
}
FULL_TRANSLATION_POLICY = {
    record_id: translation
    for root, record_ids in FULL_PK_GROUPS.items()
    for record_id, translation in zip(
        record_ids,
        TRANSLATION_MATRICES[root],
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

LEFT_BOUNDARY_IDS = FULL_PK_GROUPS[838]
LEFT_BOUNDARY_CURRENT = TRANSLATION_MATRICES[838]
LEFT_BOUNDARY_POLICY = TRANSLATION_MATRICES[838]
LEFT_BOUNDARY_SOURCE_SHA256 = (
    "ACA05D8E49C0A2002F65AB21930E2FF83EEBC1DDDB5E2ECB2897E2E82F3C3B90"
)
LEFT_BOUNDARY_CURRENT_SHA256 = (
    "50584F782F291B15382B4B0A61C7B013546490A59168913C3642242D0CC64E5A"
)

# The next segment may import this complete right-boundary policy.  The
# pristine source itself remains redacted; its digest is the contract.
RIGHT_BOUNDARY_IDS = FULL_PK_GROUPS[898]
RIGHT_BOUNDARY_CURRENT = (
    "원한다",
    "원한다",
    "받고 싶다",
    "받고 싶다",
    "원한다",
    "원한다",
    "원한다",
)
RIGHT_BOUNDARY_POLICY = TRANSLATION_MATRICES[898]
RIGHT_BOUNDARY_SOURCE_SHA256 = (
    "018B23C46A980848516C9C14A9464C545A7472BA9ABD98F080B84AB3FA9DA398"
)
RIGHT_BOUNDARY_CURRENT_SHA256 = (
    "4CA0A4CB7404363D01E6852D69735385344EB676B5727EE7017E1A0F3BAA0020"
)
RIGHT_BOUNDARY_POLICY_SHA256 = (
    "27ECFB247F0DA2CE9050573255035D25EBF12EAAEF8DA02A7A75969E100CC057"
)
RIGHT_ROOT898_FULL_IDS = RIGHT_BOUNDARY_IDS
RIGHT_ROOT898_FULL_CURRENT = RIGHT_BOUNDARY_CURRENT
RIGHT_ROOT898_FULL_POLICY = RIGHT_BOUNDARY_POLICY
RIGHT_ROOT898_FULL_SOURCE_SHA256 = RIGHT_BOUNDARY_SOURCE_SHA256

PK_TARGET_ARCHIVE_DIGESTS = {
    "pk_jp": "413F1487AA01A6378252DBBE43CB91C04D7EE0E09992DD01982078F44C121BCD",
    "pk_current": "AA3FB2F479EF4DE1F4D5FDB54789509A3CA5360C8859E6551525692910AC0816",
    "pk_sc": "BDED7B639FDEC7F705823F738AA69ED28A7812B4627D376280760106CC7A808F",
    "pk_tc": "BDED7B639FDEC7F705823F738AA69ED28A7812B4627D376280760106CC7A808F",
    "pk_en": "BDED7B639FDEC7F705823F738AA69ED28A7812B4627D376280760106CC7A808F",
}
PK_FULL_ARCHIVE_DIGESTS = {
    "pk_jp": "59B012CD1B7115C9E826277B52ACF6FCF150497925DDAA7D1A90E65908212DEA",
    "pk_current": "3CDBC32967EA808E006F6DFF6F504DE201126ED6F9895AFBA7671FD94935E51A",
    "pk_sc": "2807CFBA5C4FD487C4D605E1CF8CFA137C278CD2E7872C3AB984A9C7A5B65A36",
    "pk_tc": "2807CFBA5C4FD487C4D605E1CF8CFA137C278CD2E7872C3AB984A9C7A5B65A36",
    "pk_en": "2807CFBA5C4FD487C4D605E1CF8CFA137C278CD2E7872C3AB984A9C7A5B65A36",
}
PK_TARGET_JUMP_EDGE_SHA256 = (
    "A3385309653DFF726B867E39BC10DD1938B7D12FA96089BA71228D92BFDFCE3C"
)
PK_FULL_GROUP_JUMP_EDGE_SHA256 = (
    "3D865E747DE261DD231E1FAE8AA0EAF96D37736B338EB668BFADB3D331BD2F33"
)
EXPECTED_CALL_EVIDENCE_SHA256 = (
    "AC06AC9059B35CE10ABB1ED3A529E426B3F54DB251AD77CD930B13E108DD0A80"
)
EXPECTED_CALLER_CONTEXT_SHA256 = (
    "2595C364488789E43B3FD9C67B55EBB010CC356E5A4968B6C9A9E232C9AE2CB7"
)
MORPHOLOGY_014C_RE = re.compile(b"\x01\x4C(.{4})", re.DOTALL)
EXPECTED_014C_OVERLAP = ((15, 25, 0, 65, 84213762),)

ROOT_TRANSLATION_RATIONALE = {
    838: (
        "Standalone groans retain the established voice matrix; caller "
        "punctuation must be normalized separately."
    ),
    844: (
        "Bare confirmation particles use 지요, consistently with the "
        "already-audited adjacent matrices; copular forms retain polite, "
        "plain, and period distinctions."
    ),
    850: (
        "The explanatory nominalizer is rendered as a register-sensitive "
        "것 construction, with caller predicates changed to attributive form."
    ),
    856: (
        "The second explanatory family preserves its heightened register "
        "without retaining the current redundant copula."
    ),
    862: (
        "Neutral acknowledgement is 예; clipped military acknowledgement "
        "is 옛, matching the established period register."
    ),
    868: (
        "The inflectional negative is expressed by an action-noun caller "
        "plus 하지 않다, preserving formal and period registers."
    ),
    874: (
        "The command family uses 하시오/하라; the sole live caller requires "
        "a Korean 하 predicate and normalized punctuation."
    ),
    880: (
        "The bound inability ending is 지 못하다; its fixed following "
        "confirmation must be jointly rewritten."
    ),
    886: (
        "Standalone reactions distinguish surprise, admiration, and "
        "reflection by voice rather than retaining the vague current form."
    ),
    892: (
        "Both live callers are predictions, and one has an explicit "
        "third-person subject; therefore the auxiliary Base exhortative "
        "policy is rejected in favor of a conjectural voice matrix."
    ),
    898: (
        "The desire/request family preserves formal, plain, and period "
        "registers; callers are normalized to Korean action nouns."
    ),
}
ROOT_ASSEMBLY_PLAN = {
    838: "standalone groan plus normalized following punctuation",
    844: (
        "normalize the Korean predicate before retaining the selected "
        "confirmation particle, or flatten an already complete caller"
    ),
    850: (
        "rewrite the caller into an attributive predicate before the 것 "
        "terminal, or flatten an already complete current sentence"
    ),
    856: (
        "rewrite the predicate and any incompatible fixed following text "
        "around the explanatory 것 terminal"
    ),
    862: (
        "direct acknowledgement where the caller begins after the terminal; "
        "flatten fixed text that already contains the acknowledgement"
    ),
    868: (
        "rewrite the lexical caller to a Korean action noun before 하지 "
        "않다"
    ),
    874: "Korean 하 predicate plus command terminal and normalized punctuation",
    880: (
        "flatten the sole caller's inability terminal together with the "
        "fixed following confirmation"
    ),
    886: (
        "standalone reaction plus normalized punctuation; rewrite fixed "
        "text that already contains an interjection"
    ),
    892: (
        "normalize both callers to compatible Korean prediction stems "
        "before the conjectural terminal"
    ),
    898: (
        "normalize request callers to Korean action nouns before the "
        "register-sensitive desire terminal, or flatten duplicate wording"
    ),
}

# Only current Korean caller text is tracked.  Pristine source caller strings
# are represented by the aggregate context hash and are never embedded here.
CALLER_INTEGRATION_EVIDENCE = {
    838: (
        {
            "call_site": "6:3679:0:0",
            "observed_current_left": "",
            "observed_current_right": "、\n늙은이의",
            "integration_mode":
            "direct_and_normalize_following_punctuation",
            "source_free_korean_example": "으음,\n늙은이의",
        },
    ),
    844: (
        {
            "call_site": "15:1514:2:0",
            "observed_current_left": "이 있는 듯",
            "observed_current_right": "\n여기서 한번,",
            "integration_mode": "normalize_and_retain_terminal",
            "source_free_korean_example": (
                "이 있는 듯하지요\n여기서 한번,"
            ),
        },
        {
            "call_site": "2:356:1:0",
            "observed_current_left": "빈틈투성이로군",
            "observed_current_right": "!\n내 맹공에 떨어라!",
            "integration_mode": "flatten_live_call_in_caller",
            "source_free_korean_example": (
                "빈틈투성이로군!\n내 맹공에 떨어라!"
            ),
        },
        {
            "call_site": "15:2584:2:0",
            "observed_current_left": "\n전군, 준비는 완벽합니까",
            "observed_current_right": "\n",
            "integration_mode": "normalize_and_retain_terminal",
            "source_free_korean_example": (
                "\n전군, 준비는 완벽하지요\n"
            ),
        },
    ),
    850: (
        {
            "call_site": "2:225:2:0",
            "observed_current_left": "않겠다!\n굳게 지키는 데 ",
            "observed_current_right": "전념하겠다!",
            "integration_mode": "source_only_call_flattened_in_current",
            "source_free_korean_example": (
                "않겠다!\n굳게 지키는 데 전념하겠다!"
            ),
        },
        {
            "call_site": "6:4363:2:0",
            "observed_current_left": "의 이름을 세상에 널리 알리겠",
            "observed_current_right": "！",
            "integration_mode":
            "normalize_and_retain_terminal_with_punctuation",
            "source_free_korean_example": (
                "의 이름을 세상에 널리 알릴 것입니다!"
            ),
        },
        {
            "call_site": "6:4941:2:0",
            "observed_current_left": "다면…\n가능하면 싸움은 피하고 싶습니다",
            "observed_current_right": "",
            "integration_mode": "flatten_live_call_in_caller",
            "source_free_korean_example": (
                "다면…\n가능하면 싸움은 피하고 싶습니다"
            ),
        },
    ),
    856: (
        {
            "call_site": "6:3534:1:0",
            "observed_current_left": "이(가) 되었다",
            "observed_current_right": "\n이 정도는 해",
            "integration_mode": "rewrite_caller_around_terminal",
            "source_free_korean_example": (
                "이(가) 되었다\n이 정도는 해야 할 것이다"
            ),
        },
        {
            "call_site": "6:4443:4:0",
            "observed_current_left": "이 세워진다",
            "observed_current_right": "이…",
            "integration_mode": "rewrite_caller_and_fixed_following",
            "source_free_korean_example": "이 세워지는 것이…",
        },
    ),
    862: (
        {
            "call_site": "15:2368:0:0",
            "observed_current_left": "",
            "observed_current_right": (
                "、이번 목표…\n가신들에게 똑똑히 전하여, 실현을 위해\n"
                "전원, 진력"
            ),
            "integration_mode":
            "direct_and_normalize_following_punctuation",
            "source_free_korean_example": (
                "예, 이번 목표…\n가신들에게 똑똑히 전하여, 실현을 위해\n"
                "전원, 진력"
            ),
        },
        {
            "call_site": "6:3614:0:0",
            "observed_current_left": "",
            "observed_current_right": (
                "예, 이 목숨이 다할 때까지\n온 힘을 다하겠습니다."
            ),
            "integration_mode": "flatten_fixed_following_in_caller",
            "source_free_korean_example": (
                "예, 이 목숨이 다할 때까지\n온 힘을 다하겠습니다."
            ),
        },
        {
            "call_site": "6:4209:0:0",
            "observed_current_left": "",
            "observed_current_right": "알겠습니다.",
            "integration_mode": "source_only_call_flattened_in_current",
            "source_free_korean_example": "알겠습니다.",
        },
    ),
    868: (
        {
            "call_site": "1:20:2:0",
            "observed_current_left": "의 주군은 결코 흔들",
            "observed_current_right": "! 에잇, 그곳을",
            "integration_mode": "normalize_action_noun_and_retain_terminal",
            "source_free_korean_example": (
                "의 주군은 결코 굴복하지 않습니다! 에잇, 그곳을"
            ),
        },
    ),
    874: (
        {
            "call_site": "1:26:1:0",
            "observed_current_left": "크게 기뻐",
            "observed_current_right": "！",
            "integration_mode":
            "direct_composition_and_normalize_punctuation",
            "source_free_korean_example": "크게 기뻐하시오!",
        },
    ),
    880: (
        {
            "call_site": "1:25:2:0",
            "observed_current_left": "를 애송이라 부르",
            "observed_current_right": "군.",
            "integration_mode": "flatten_terminal_and_fixed_confirmation",
            "source_free_korean_example": (
                "를 애송이라 부르지는 못하겠군."
            ),
        },
    ),
    886: (
        {
            "call_site": "6:4609:0:0",
            "observed_current_left": "",
            "observed_current_right": "、",
            "integration_mode":
            "direct_and_normalize_following_punctuation",
            "source_free_korean_example": "호오,",
        },
        {
            "call_site": "6:4705:0:0",
            "observed_current_left": "",
            "observed_current_right": "오, 나쁘지 않군.",
            "integration_mode": "rewrite_fixed_following_and_retain_terminal",
            "source_free_korean_example": "호오, 나쁘지 않군.",
        },
    ),
    892: (
        {
            "call_site": "15:1702:4:0",
            "observed_current_left": (
                "얼굴을 내비쳐\n승진한 자들도 기뻐"
            ),
            "observed_current_right": "",
            "integration_mode":
            "normalize_third_person_conjectural_caller",
            "source_free_korean_example": (
                "얼굴을 내비치면\n승진한 자들도 기뻐하겠지요"
            ),
        },
        {
            "call_site": "6:3529:2:0",
            "observed_current_left": "인가\n꽃이 피면, 다음은 열매를 맺",
            "observed_current_right": "",
            "integration_mode": "normalize_conjectural_caller",
            "source_free_korean_example": (
                "인가\n꽃이 피면, 다음은 결실을 맺겠지요"
            ),
        },
    ),
    898: (
        {
            "call_site": "15:2091:1:0",
            "observed_current_left": (
                "을(를) 공격하려면 목표를\n정하고"
            ),
            "observed_current_right": "가\n지금은 일단",
            "integration_mode": "rewrite_caller_and_fixed_following",
            "source_free_korean_example": (
                "을(를) 공격하려면 목표를\n정해 주었으면 합니다만\n"
                "지금은 일단"
            ),
        },
        {
            "call_site": "6:3590:2:0",
            "observed_current_left": "으로서\n보필할 대상:",
            "observed_current_right": "",
            "integration_mode": "rewrite_dynamic_token_caller",
            "source_free_korean_example": (
                "[동적 신분](으)로서\n[동적 인물명]을(를) "
                "보필해 주었으면 합니다"
            ),
        },
        {
            "call_site": "6:4679:1:0",
            "observed_current_left": (
                "그쪽에도 나쁘지 않은 이야기일 것이오\n"
                "그 점을 감안해 주시"
            ),
            "observed_current_right": "기 바라오",
            "integration_mode": "flatten_duplicate_desire_terminal",
            "source_free_korean_example": (
                "그쪽에도 나쁘지 않은 이야기일 것이오\n"
                "그 점을 감안해 주시기 바라오"
            ),
        },
    ),
}

BASIS = (
    "review_queue_pk_msggame_B006_zero_based_visible_ordinals0_66_"
    "pristine_pk_pc_jp_sole_translation_authority_source_text_redacted_"
    "from_tracked_builder_block0_records2271_2337_67_visible_queue_hidden_"
    "two_outside_slice_global_unique_literal_gap_reverse_search_Base_"
    "records2203_2269_plus68_only_after_search_Base_auxiliary_jp_current_"
    "sc_tc_exact_pk_en_empty_target_full_archive_digests_actual_014a_"
    "incoming_source_current_eleven_full_closures_actual_0143_calls_fixed_"
    "source_only_current_only_and_all_caller_context_digest_valid_014c_"
    "zero_overlap_false_positive_one_left_root838_imported_S1038_contract_"
    "right_root898_full_policy_exported_confirmation_source_justified_"
    "bare_particle_divergence_explanatory_military_"
    "acknowledgement_negative_command_inability_reaction_conjectural_"
    "desire_register_matrices_root892_source_justified_conjectural_"
    "divergence_from_auxiliary_Base_exhortative_policy_current_caller_"
    "direct_normalize_flatten_rewrite_examples_no_automatic_space_"
    "all_runtime_fragments_no_historic_or_switch_korean_authority_"
    "one_line_skeleton_outside_reverse_two_run_steam_read_only"
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
    source_sequence = record_signature(
        records_by_label["pk_jp"],
        RECORD_IDS[0],
        len(RECORD_IDS),
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
    if base_hits != (2203,) or pk_hits != (2271,):
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
    full_keys = tuple((BLOCK_ID, value) for value in range(2266, 2343))
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
    source: dict[tuple[int, int], Any],
    current: dict[tuple[int, int], Any],
) -> None:
    if set(CALLER_INTEGRATION_EVIDENCE) != set(FULL_PK_GROUPS):
        raise RuntimeError(
            f"segment {SEGMENT} caller example root coverage drifted"
        )
    for root, examples in CALLER_INTEGRATION_EVIDENCE.items():
        source_calls = set(HELPERS.root_call_sites(source, root))
        current_calls = set(HELPERS.root_call_sites(current, root))
        for example in examples:
            call_site = str(example["call_site"])
            mode = str(example["integration_mode"])
            if mode == "source_only_call_flattened_in_current":
                if call_site not in source_calls or call_site in current_calls:
                    raise RuntimeError(
                        f"segment {SEGMENT} source-only caller drifted: "
                        f"{root}/{call_site}"
                    )
            elif call_site not in current_calls:
                raise RuntimeError(
                    f"segment {SEGMENT} live caller drifted: "
                    f"{root}/{call_site}"
                )
            left, right, _ = caller_context(current, call_site)
            source_free = str(example["source_free_korean_example"])
            if (
                left != example["observed_current_left"]
                or right != example["observed_current_right"]
                or ENGINE.KANA_OR_HAN_RE.search(source_free)
                or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(
                    source_free
                )
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} caller example drifted: "
                    f"{root}/{call_site}"
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
    if full_ids != set(range(2266, 2343)):
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
                "incoming 014A graph drifted"
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
    return call_evidence, context_evidence


def assert_boundaries(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
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
        or LEFT_BOUNDARY_IDS != LEFT_PK.RIGHT_BOUNDARY_IDS
        or actual_left_source != LEFT_PK.RIGHT_BOUNDARY_JP
        or actual_left_current != LEFT_PK.RIGHT_BOUNDARY_CURRENT
        or LEFT_BOUNDARY_POLICY != LEFT_PK.RIGHT_BOUNDARY_POLICY
    ):
        raise RuntimeError(
            f"segment {SEGMENT} S1038/S1039 root838 boundary drifted"
        )
    if (
        HELPERS.canonical_sha256(actual_right_source)
        != RIGHT_BOUNDARY_SOURCE_SHA256
        or HELPERS.canonical_sha256(actual_right_current)
        != RIGHT_BOUNDARY_CURRENT_SHA256
        or actual_right_current != RIGHT_BOUNDARY_CURRENT
        or HELPERS.canonical_sha256(RIGHT_BOUNDARY_POLICY)
        != RIGHT_BOUNDARY_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} right root898 boundary drifted"
        )


def auxiliary_policy_for_base_record(base_record_id: int) -> str:
    source = (
        BASE_LEFT.FULL_TRANSLATION_POLICY
        if base_record_id in BASE_LEFT.FULL_TRANSLATION_POLICY
        else BASE_RIGHT.FULL_TRANSLATION_POLICY
    )
    return source[base_record_id]


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
        auxiliary = auxiliary_policy_for_base_record(base_record_id)
        if (
            row is None
            or row["resource"] != "base_msggame"
            or row["semantic_review"] != "approved"
            or row["translation"] != auxiliary
        ):
            raise RuntimeError(
                f"segment {SEGMENT} completed Base auxiliary policy "
                f"drifted: {coordinate}"
            )
        actual = TRANSLATIONS_BY_RECORD[pk_record_id]
        if (
            pk_record_id in AUXILIARY_BASE_DIVERGENCE_RECORD_IDS
        ) == (actual == auxiliary):
            raise RuntimeError(
                f"segment {SEGMENT} Base divergence contract drifted: "
                f"{coordinate}"
            )


def assert_semantics(translations: dict[str, str]) -> None:
    if (
        translations != TRANSLATIONS
        or len(translations) != 67
        or set(TRANSLATIONS_BY_RECORD) != set(RECORD_IDS)
        or set(RECORD_TO_ROOT) != set(RECORD_IDS)
        or set(TRANSLATION_MATRICES) != set(FULL_PK_GROUPS)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} translation universe drifted"
        )
    if (
        HELPERS.canonical_sha256(CUSTOM_ROOT892_POLICY)
        != EXPECTED_CUSTOM_ROOT892_POLICY_SHA256
        or HELPERS.canonical_sha256(
            BASE_RIGHT.TRANSLATION_POLICY_BY_ROOT[880]
        )
        != EXPECTED_AUX_BASE_ROOT880_POLICY_SHA256
        or CUSTOM_ROOT892_POLICY
        == BASE_RIGHT.TRANSLATION_POLICY_BY_ROOT[880]
        or HELPERS.canonical_sha256(CUSTOM_ROOT844_POLICY)
        != EXPECTED_CUSTOM_ROOT844_POLICY_SHA256
        or HELPERS.canonical_sha256(
            BASE_LEFT.TRANSLATION_POLICY_BY_ROOT[832]
        )
        != EXPECTED_AUX_BASE_ROOT832_POLICY_SHA256
        or CUSTOM_ROOT844_POLICY
        == BASE_LEFT.TRANSLATION_POLICY_BY_ROOT[832]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic divergence drifted"
        )
    for record_id in RECORD_IDS:
        if record_id in AUXILIARY_BASE_DIVERGENCE_RECORD_IDS:
            continue
        auxiliary = auxiliary_policy_for_base_record(record_id - 68)
        if TRANSLATIONS_BY_RECORD[record_id] != auxiliary:
            raise RuntimeError(
                f"segment {SEGMENT} auxiliary policy drifted: {record_id}"
            )
    if (
        tuple(
            TRANSLATIONS_BY_RECORD[record_id]
            for record_id in range(2271, 2273)
        )
        != LEFT_BOUNDARY_POLICY[-2:]
        or tuple(
            TRANSLATIONS_BY_RECORD[record_id]
            for record_id in range(2336, 2338)
        )
        != RIGHT_BOUNDARY_POLICY[:2]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic boundary drifted"
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
    if pk.current_path.read_bytes() != pk.current_blob:
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
                "translation_rationale": ROOT_TRANSLATION_RATIONALE[root],
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
                    "auxiliary_base_policy_diverged":
                    record_id in AUXILIARY_BASE_DIVERGENCE_RECORD_IDS,
                    "auxiliary_base_divergence_reason": (
                        ROOT_TRANSLATION_RATIONALE[root]
                        if record_id
                        in AUXILIARY_BASE_DIVERGENCE_RECORD_IDS
                        else ""
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
                "segment": "pk_msggame_B006_S1039",
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
                "discovered_base_record_range": [2203, 2269],
                "discovered_pk_minus_base_offset": offset,
                "source_sequence_sha256":
                EXPECTED_SOURCE_SEQUENCE_SHA256,
                "translation_policy_sha256":
                EXPECTED_POLICY_SHA256,
                "source_justified_base_divergence_record_ids":
                sorted(AUXILIARY_BASE_DIVERGENCE_RECORD_IDS),
                "pk_target_incoming_sha256":
                PK_TARGET_JUMP_EDGE_SHA256,
                "pk_full_group_incoming_sha256":
                PK_FULL_GROUP_JUMP_EDGE_SHA256,
                "pk_call_fixed_flatten_evidence_sha256":
                EXPECTED_CALL_EVIDENCE_SHA256,
                "pk_all_caller_context_sha256":
                EXPECTED_CALLER_CONTEXT_SHA256,
                "valid_incoming_014c_count": 0,
                "left_root838_full_policy":
                list(LEFT_BOUNDARY_POLICY),
                "right_root898_full_policy":
                list(RIGHT_BOUNDARY_POLICY),
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
                "s1038_root838_boundary_contract_exact": True,
                "right_root898_full_policy_exported": True,
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
