#!/usr/bin/env python3
"""Build PK block-0 runtime-terminal segment 1037 decisions."""

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

import build_base_batch005_segment1015 as LEFT_BASE
import build_base_batch005_segment1016 as RIGHT_BASE
import build_pk_batch001_segment1025 as HELPERS
import build_pk_batch005_segment1036 as LEFT_PK


ENGINE = RIGHT_BASE.ENGINE
GENERAL = RIGHT_BASE.GENERAL
UTIL = RIGHT_BASE.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B005_S1037.private.v1.jsonl"
)
BASE_DECISIONS = (
    (
        REPO
        / "tmp"
        / WORKSTREAM.name
        / "decisions"
        / "base_msggame_B005_S1015.private.v1.jsonl",
        "34F8B17E10F324BFFC50596DEBED3A6CA2190714FC5C7BBC165D5A0103C2F1A3",
    ),
    (
        REPO
        / "tmp"
        / WORKSTREAM.name
        / "decisions"
        / "base_msggame_B005_S1016.private.v1.jsonl",
        "CA3D0894416D1C92C23F46D24B1D1774130031160A0E8B9F198FA773C4DBDD49",
    ),
)
SEGMENT = 1037
QUEUE_BATCH_ID = "pk_msggame-B005"
BLOCK_ID = 0
QUEUE_START = 67
QUEUE_STOP = 134
HIDDEN_RECORD_IDS = (2147, 2149, 2151)
OWNED_RECORD_IDS = tuple(range(2135, 2205))
RECORD_IDS = tuple(
    record_id
    for record_id in OWNED_RECORD_IDS
    if record_id not in HIDDEN_RECORD_IDS
)
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
OWNED_RECORD_KEYS = tuple(
    (BLOCK_ID, record_id) for record_id in OWNED_RECORD_IDS
)
FULL_RECORD_IDS = tuple(range(2133, 2210))
FULL_RECORD_KEYS = tuple(
    (BLOCK_ID, record_id) for record_id in FULL_RECORD_IDS
)
TARGET_COORDINATES = tuple(
    f"{BLOCK_ID}:{record_id}:0" for record_id in RECORD_IDS
)
QUEUE_HIDDEN_COORDINATES = (
    "0:2147:0",
    "0:2149:0",
    "0:2151:0",
)
PK_RECORD_COUNT = 21751

# These are actual 014A roots and their complete seven-register terminal
# groups. S1037 owns the tail of root 724 and the head of root 784.
FULL_PK_GROUPS = {
    724: tuple(range(2133, 2140)),
    730: tuple(range(2140, 2147)),
    736: tuple(range(2147, 2154)),
    742: tuple(range(2154, 2161)),
    748: tuple(range(2161, 2168)),
    754: tuple(range(2168, 2175)),
    760: tuple(range(2175, 2182)),
    766: tuple(range(2182, 2189)),
    772: tuple(range(2189, 2196)),
    778: tuple(range(2196, 2203)),
    784: tuple(range(2203, 2210)),
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

# Pristine PK PC JP is the sole translation authority. These matrices are
# independently pinned from that corpus, including all three non-display
# empty leaves in root 736.
EXPECTED_SOURCE_MATRICES = {
    724: ("わ", "な", "ね", "な", "わね", "な", "な"),
    730: ("ね", "な", "ね", "な", "ね", "な", "な"),
    736: ("", "な", "", "な", "", "な", "な"),
    742: (
        "ありません",
        "ない",
        "ございません",
        "ございませぬ",
        "ありません",
        "ござらぬ",
        "ない",
    ),
    748: (
        "ません",
        "ぬ",
        "ませぬ",
        "ませぬ",
        "ません",
        "ませぬ",
        "ぬ",
    ),
    754: (
        "ありません",
        "ない",
        "ありません",
        "ありませぬ",
        "ありません",
        "ありませぬ",
        "ない",
    ),
    760: ("ない", "ぬ", "ない", "ぬ", "ない", "ぬ", "ぬ"),
    766: (
        "ありませんでした",
        "なかった",
        "ございませんでした",
        "ございませなんだ",
        "ありませんでした",
        "ございませんでした",
        "なかった",
    ),
    772: (
        "ませんでした",
        "なかった",
        "ませんでした",
        "ませなんだ",
        "ませんでした",
        "ませんでした",
        "なかった",
    ),
    778: (
        "ないでしょう",
        "なかろう",
        "ござりますまい",
        "ござりますまい",
        "ないでしょう",
        "ありますまい",
        "なかろう",
    ),
    784: (
        "なければ",
        "なければ",
        "なければ",
        "なければ",
        "なきゃ",
        "なければ",
        "なければ",
    ),
}
EXPECTED_FULL_PK_JP = {
    record_id: source
    for root, record_ids in FULL_PK_GROUPS.items()
    for record_id, source in zip(
        record_ids,
        EXPECTED_SOURCE_MATRICES[root],
        strict=True,
    )
}

# The register order is the runtime's seven-way speaker matrix. Formal,
# plain, and period-register distinctions are retained without invented
# archaic Korean.
TRANSLATION_MATRICES = {
    724: ("네요", "군", "지요", "군", "네요", "군", "군"),
    730: ("지요", "군", "지요", "군", "지요", "군", "군"),
    736: ("", "군", "", "군", "", "군", "군"),
    742: (
        "없습니다",
        "없다",
        "없사옵니다",
        "없사옵니다",
        "없습니다",
        "없소",
        "없다",
    ),
    748: (
        "하지 않습니다",
        "하지 않는다",
        "하지 않사옵니다",
        "하지 않사옵니다",
        "하지 않습니다",
        "하지 않사옵니다",
        "하지 않는다",
    ),
    754: (
        "없습니다",
        "없다",
        "없습니다",
        "없사옵니다",
        "없습니다",
        "없사옵니다",
        "없다",
    ),
    760: (
        "하지 않는다",
        "하지 않는다",
        "하지 않는다",
        "하지 않는다",
        "하지 않는다",
        "하지 않는다",
        "하지 않는다",
    ),
    766: (
        "없었습니다",
        "없었다",
        "없었사옵니다",
        "없었사옵니다",
        "없었습니다",
        "없었사옵니다",
        "없었다",
    ),
    772: (
        "하지 않았습니다",
        "하지 않았다",
        "하지 않았습니다",
        "하지 않았사옵니다",
        "하지 않았습니다",
        "하지 않았습니다",
        "하지 않았다",
    ),
    778: (
        "없겠지요",
        "없으리",
        "없겠사옵니다",
        "없겠사옵니다",
        "없겠지요",
        "없겠소",
        "없으리",
    ),
    784: (
        "지 않으면",
        "지 않으면",
        "지 않으면",
        "지 않으면",
        "지 않으면",
        "지 않으면",
        "지 않으면",
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

LEFT_BOUNDARY_IDS = FULL_PK_GROUPS[724]
LEFT_BOUNDARY_JP = EXPECTED_SOURCE_MATRICES[724]
LEFT_BOUNDARY_CURRENT = ("와", "군", "군", "군", "네", "군", "군")
LEFT_BOUNDARY_POLICY = TRANSLATION_MATRICES[724]
RIGHT_BOUNDARY_IDS = FULL_PK_GROUPS[784]
RIGHT_BOUNDARY_JP = EXPECTED_SOURCE_MATRICES[784]
RIGHT_BOUNDARY_CURRENT = (
    "않으면",
    "않으면",
    "않으면",
    "않으면",
    "않으면",
    "않으면",
    "않으면",
)
RIGHT_BOUNDARY_POLICY = TRANSLATION_MATRICES[784]

EXPECTED_SOURCE_SEQUENCE_SHA256 = (
    "9E284AE3A0529E01E9CE9DE021BA9D2B4B349A3EAA6D6CA559B932273C0C6186"
)
EXPECTED_MAPPING_SHA256 = (
    "960CF87F1F51DE8EAFD1F8674DF7C8F05EEEB0F9F9FED10AD9013F86EF4FB3D0"
)
EXPECTED_VISIBLE_POLICY_SHA256 = (
    "8479DFCB38F4229B4BDA0B3344FDE15B87509BE1221C4DF95E27874F57626CE9"
)
EXPECTED_OWNED_POLICY_SHA256 = (
    "0FCBC0270685192C006E240FEB99DF2C7C14D0704CB2F78F05760F7ABBDADAE6"
)
EXPECTED_CHANGED_LITERAL_COUNT = 40
HIDDEN_EMPTY_RAW_SHA256 = (
    "2DED36CFD4BD604EEB3E2E5446D33F30F1E362A92AF887A87EE07739A4C961C4"
)
PK_OWNED_ARCHIVE_DIGESTS = {
    "pk_jp": "2D255AA2D120FA979E7189312E6CAE53AA29BE55460B0BF22A4DCF6D2FE7790C",
    "pk_current": "328AB930BCB048EEE1E4E77EBA64ED2CBA5A732C7D0998797AC95505BED3F630",
    "pk_sc": "3C7DE8AD06806E54C25AE69CB1FE9232B8D6486B0A515051FD2314F45013EEB9",
    "pk_tc": "3C7DE8AD06806E54C25AE69CB1FE9232B8D6486B0A515051FD2314F45013EEB9",
    "pk_en": "3C7DE8AD06806E54C25AE69CB1FE9232B8D6486B0A515051FD2314F45013EEB9",
}
PK_VISIBLE_ARCHIVE_DIGESTS = {
    "pk_jp": "81DF0EE04E31DA5E4F321C74B11675D412C8232274E741A636822B06815AF4AD",
    "pk_current": "E1A4DCF76B387630D8A0B44D59F71266BD1DF43395350E931964287C8B93C6B8",
    "pk_sc": "FBC9EEF236C3BE0A07344A6FAF9ABDF0939524A32C95CD3941C1EF21C6EBB465",
    "pk_tc": "FBC9EEF236C3BE0A07344A6FAF9ABDF0939524A32C95CD3941C1EF21C6EBB465",
    "pk_en": "FBC9EEF236C3BE0A07344A6FAF9ABDF0939524A32C95CD3941C1EF21C6EBB465",
}
PK_FULL_ARCHIVE_DIGESTS = {
    "pk_jp": "6D88E06270997CFD77B00EA73B28C63DF5AAA41B1F121F1A50B8CD95A62261AD",
    "pk_current": "E23C262E45DA0D1FEE8B1B5388D18C7EB11BE7406905E15B50E210E517FB84CE",
    "pk_sc": "19DA23BE68D3E19BFC4F8AA567CC6A005DF83D24C98934A2D8ADB030D926A82D",
    "pk_tc": "19DA23BE68D3E19BFC4F8AA567CC6A005DF83D24C98934A2D8ADB030D926A82D",
    "pk_en": "19DA23BE68D3E19BFC4F8AA567CC6A005DF83D24C98934A2D8ADB030D926A82D",
}
PK_TARGET_INCOMING_SHA256 = (
    "F92DC8DF647C90D919144126DA043583399541CD707E82A39B3C4713F623CC1A"
)
PK_VISIBLE_INCOMING_SHA256 = (
    "E899D22B40FF5154AAB537142AEE6637DAF4303E53E45EBD55C019D042A98807"
)
PK_FULL_INCOMING_SHA256 = (
    "B6E6ABE51100B8C70385C7268319F4677B11DC906C4E877C304D5EA9DB5EAEC5"
)
EXPECTED_CALL_EVIDENCE_SHA256 = (
    "0D23AB6624EE4616E7E1857F52A457C864792F43346DF992F2FEB6D3AE3F4213"
)
ROOT784_ROOT730_CHAIN_GAP_SHA256 = (
    "7D70ED713CC4DEE54E5B7AAE18C673782AA00CAEF974DB4BAD015D0F74BE103F"
)
ROOT784_ROOT730_CHAIN_COMMANDS = ((0, 784), (6, 730))
MORPHOLOGY_014C_RE = re.compile(b"\x01\x4C(.{4})", re.DOTALL)
EXPECTED_014C_OVERLAP = ((15, 25, 0, 65, 84213762),)

ROOT_TRANSLATION_RATIONALE = {
    724: (
        "Japanese feminine/neutral confirmation particles are rendered "
        "by Korean register-sensitive confirmation endings; caller stems "
        "must be normalized where current Korean already embeds an ending."
    ),
    730: (
        "The confirmation-particle matrix distinguishes polite 지요 from "
        "plain 군 while preserving the seven runtime registers."
    ),
    736: (
        "Empty source leaves remain byte-exact non-display records; the "
        "four visible な leaves retain the plain realization 군."
    ),
    742: (
        "Existential absence uses 없다 across modern, plain, and period "
        "registers, including 없사옵니다/없소 where the source register "
        "requires it."
    ),
    748: (
        "The inflectional negative ません/ぬ requires a Korean action stem "
        "plus 하지 않다; callers must be normalized or flattened when "
        "their current text already contains a finite negative."
    ),
    754: (
        "Existential absence is distinguished from generic verbal "
        "negation and retains the source register matrix."
    ),
    760: (
        "Plain generic negative leaves use 하지 않는다; incompatible "
        "already-finite current callers are normalized or flattened."
    ),
    766: (
        "Past existential absence uses 없었다 with formal and period "
        "register variants, rather than the current 아니었다 substitutions."
    ),
    772: (
        "Past generic verbal negation uses 하지 않았다 with the source "
        "speaker-register distinctions intact."
    ),
    778: (
        "Negative conjecture is rendered as 없겠-/없으리, preserving "
        "politeness and period-register variation without pseudo-archaic "
        "wording."
    ),
    784: (
        "Conditional negative なければ/なきゃ is an inflectional fragment "
        "지 않으면; current callers must supply a compatible action stem."
    ),
}
ROOT_ASSEMBLY_PLAN = {
    724: (
        "normalize any already-finite Korean caller to a predicate stem "
        "before retaining the selected confirmation terminal; flatten "
        "callers already completed in current"
    ),
    730: (
        "normalize any embedded 군/지요 in the current caller, then retain "
        "the selected register terminal"
    ),
    736: (
        "preserve the three hidden empty leaves; normalize visible caller "
        "stems where 군 cannot directly follow the current Korean"
    ),
    742: (
        "normalize a current caller that already ends in 없 before the "
        "없다 register terminal and normalize following punctuation; "
        "subroot 743 also requires a Korean lexical boundary"
    ),
    748: (
        "rewrite the caller to a Korean action stem before 하지 않다, or "
        "flatten an already complete current sentence"
    ),
    754: (
        "rewrite the Korean lexical boundary before the 없다 terminal; "
        "normalize or flatten callers already containing finite absence"
    ),
    760: (
        "rewrite the caller to an action stem before 하지 않는다, or "
        "flatten already complete current sentences"
    ),
    766: (
        "rewrite the Korean lexical boundary before the past 없다 "
        "terminal; flatten callers already containing finite absence"
    ),
    772: (
        "rewrite the caller to an action stem before past 하지 않다, or "
        "flatten already complete current sentences"
    ),
    778: (
        "rewrite the Korean lexical boundary before the negative "
        "conjectural terminal; flatten callers already complete in current"
    ),
    784: (
        "the 7:2442 caller chains root784 immediately into root730; "
        "flatten both terminals into one source-free Korean obligation"
    ),
}

# Every example is pinned to an actual pristine/current caller. Direct and
# normalize examples are live current 0143 calls; flatten examples are
# source-only 0143 calls whose current Korean record has already absorbed
# the command.
CALLER_INTEGRATION_EVIDENCE = {
    724: (
        {
            "call_site": "2:223:1:6",
            "observed_current_left": "의 차례인 듯",
            "observed_current_right": "\n특기인 이 언변으로",
            "integration_mode": "normalize_and_retain_terminal",
            "source_free_korean_example": (
                "의 차례인 듯하네요\n특기인 이 언변으로"
            ),
        },
        {
            "call_site": "13:106:1:6",
            "observed_source_left": (
                "また、統率力に優れているゆえ\n"
                "郡の発展や戦の際にも頼りにな"
            ),
            "observed_source_right": "",
            "observed_current_left": (
                "또한 통솔력이 뛰어나므로\n"
                "군의 발전과 전쟁에서도 든든한 도움이 될 것입니다."
            ),
            "observed_current_right": "",
            "integration_mode": "flatten_command_in_caller",
            "source_free_korean_example": (
                "또한 통솔력이 뛰어나므로\n"
                "군의 발전과 전쟁에서도 든든한 도움이 될 것입니다."
            ),
        },
    ),
    730: (
        {
            "call_site": "6:4615:4:6",
            "observed_current_left": "\n생각보다 더 진심이군",
            "observed_current_right": "",
            "integration_mode": "normalize_and_retain_terminal",
            "source_free_korean_example": "\n생각보다 더 진심이군",
        },
    ),
    736: (
        {
            "call_site": "6:4619:1:0",
            "observed_current_left": "이번 전쟁을 끝내고 싶다는 건",
            "observed_current_right": (
                "가?\n조건에 따라 받아들일 수도 있지만\n"
                "대가가 없으면 가신들에게 면이 서지 않"
            ),
            "integration_mode": "normalize_and_retain_terminal",
            "source_free_korean_example": (
                "이번 전쟁을 끝내고 싶다는 것이군가?\n"
                "조건에 따라 받아들일 수도 있지만\n"
                "대가가 없으면 가신들에게 면이 서지 않"
            ),
        },
    ),
    742: (
        {
            "call_site": "2:541:2:0",
            "observed_current_left": (
                "부대의 조총으로\n꿰뚫지 못할 것은 없"
            ),
            "observed_current_right": "！",
            "integration_mode":
            "normalize_and_retain_terminal_and_normalize_following_punctuation",
            "source_free_korean_example": (
                "부대의 조총으로\n꿰뚫지 못할 것은 없습니다!"
            ),
        },
    ),
    743: (
        {
            "call_site": "7:330:2:0",
            "observed_current_left": "이 무릎 꿇는 일은",
            "observed_current_right": "",
            "integration_mode": "rewrite_boundary_and_retain_terminal",
            "source_free_korean_example": "이 무릎 꿇는 일은 없습니다",
        },
    ),
    748: (
        {
            "call_site": "6:3676:2:0",
            "observed_current_left": (
                "을(를) 몰수하다니\n그런 일은 결단코 인정할 수 없"
            ),
            "observed_current_right": "",
            "integration_mode": "normalize_and_retain_terminal",
            "source_free_korean_example": (
                "을(를) 몰수하다니\n그런 일은 결단코 인정하지 않습니다"
            ),
        },
    ),
    754: (
        {
            "call_site": "6:4177:1:0",
            "observed_current_left": (
                "전선의 병력이 부족해\n공략할 수 있는 세력이"
            ),
            "observed_current_right": "\n다른 군단의 지원이 있다면 혹시…",
            "integration_mode": "rewrite_boundary_and_retain_terminal",
            "source_free_korean_example": (
                "전선의 병력이 부족해\n공략할 수 있는 세력이 없습니다\n"
                "다른 군단의 지원이 있다면 혹시…"
            ),
        },
    ),
    760: (
        {
            "call_site": "2:363:2:0",
            "observed_source_left": "！\n騎馬隊の好きにはさせ",
            "observed_source_right": "！",
            "observed_current_left": "\n기마대가 마음대로 하게 두지 ",
            "observed_current_right": "않겠다!",
            "integration_mode": "flatten_command_in_caller",
            "source_free_korean_example": (
                "\n기마대가 마음대로 하게 두지 않겠다!"
            ),
        },
    ),
    766: (
        {
            "call_site": "6:4206:1:0",
            "observed_current_left": (
                "다룰 수 있는 금전이 적어서인지\n유효한 제안은"
            ),
            "observed_current_right": "",
            "integration_mode": "rewrite_boundary_and_retain_terminal",
            "source_free_korean_example": (
                "다룰 수 있는 금전이 적어서인지\n유효한 제안은 없었습니다"
            ),
        },
    ),
    772: (
        {
            "call_site": "15:1538:1:0",
            "observed_source_left": (
                "城下の牢人に登用をもちかけたものの\n我が力及ばず…\n"
                "成果は得られ"
            ),
            "observed_source_right": "",
            "observed_current_left": (
                "성하의 낭인에게 등용을 권했으나\n"
                "제 힘이 미치지 못하여…\n성과는 얻지 못했습니다."
            ),
            "observed_current_right": "",
            "integration_mode": "flatten_command_in_caller",
            "source_free_korean_example": (
                "성하의 낭인에게 등용을 권했으나\n"
                "제 힘이 미치지 못하여…\n성과는 얻지 못했습니다."
            ),
        },
    ),
    778: (
        {
            "call_site": "6:3683:3:0",
            "observed_current_left": "에게 잘못 따위",
            "observed_current_right": "",
            "integration_mode": "rewrite_boundary_and_retain_terminal",
            "source_free_korean_example": "에게 잘못 따위 없겠지요",
        },
    ),
    784: (
        {
            "call_site": "7:2442:2:0",
            "observed_current_left": "\n앞으로의 행동을 정하",
            "observed_current_right": "",
            "integration_mode": "flatten_fixed_command_chain_in_caller",
            "source_free_korean_example": (
                "\n앞으로의 행동을 정해야겠군"
            ),
        },
    ),
}
EXPECTED_INTEGRATION_CLASS_COUNTS = {
    "normalize_and_retain_terminal": 4,
    "flatten_command_in_caller": 3,
    "normalize_and_retain_terminal_and_normalize_following_punctuation":
    1,
    "rewrite_boundary_and_retain_terminal": 4,
    "flatten_fixed_command_chain_in_caller": 1,
}
BASIS = (
    "review_queue_pk_msggame_B005_zero_based_visible_ordinals67_133_"
    "pristine_pk_pc_jp_sole_translation_authority_block0_records2135_"
    "2204_67_visible_three_hidden_empty_leaves_excluded_from_decisions_"
    "global_unique_exact70_literal_gap_reverse_search_discovered_Base_"
    "records2067_2136_plus68_uniform_only_after_search_Base_auxiliary_"
    "completed_Base_S1015_S1016_policy_crosscheck_pk_jp_current_sc_tc_en_"
    "owned_visible_full_boundary_archive_digests_014a_incoming_target70_"
    "visible67_full77_source_current_edges_full_seven_register_closures_"
    "subroot743_closure_0143_call_fixed_source_only_current_only_digests_"
    "valid_014c_zero_one_overlap_false_positive_source_current_current_"
    "caller_direct_normalize_flatten_source_free_examples_both_full_"
    "boundary_matrices_runtime_pending_no_historic_or_switch_korean_"
    "protected_skeleton_hidden_raw_outside_reverse_two_run_no_steam"
)


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return RIGHT_BASE.literal_texts(records, key)


def gap_bytes(record: Any) -> tuple[bytes, ...]:
    return RIGHT_BASE.gap_bytes(record)


def archive_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    return RIGHT_BASE.archive_records(prepared)


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
        ((EXPECTED_FULL_PK_JP[record_id],), ("", "050505"))
        for record_id in OWNED_RECORD_IDS
    )
    digest = hashlib.sha256(
        json.dumps(
            expected_sequence,
            ensure_ascii=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest().upper()
    if digest != EXPECTED_SOURCE_SEQUENCE_SHA256:
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
    if base_hits != (2067,) or pk_hits != (2135,):
        raise RuntimeError(
            f"segment {SEGMENT} global source reverse search drifted"
        )
    offset = pk_hits[0] - base_hits[0]
    mapping = {
        pk_record_id: base_hits[0] + ordinal
        for ordinal, pk_record_id in enumerate(OWNED_RECORD_IDS)
    }
    if (
        offset != 68
        or tuple(mapping.values()) != tuple(range(2067, 2137))
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
        != EXPECTED_VISIBLE_POLICY_SHA256
        or HELPERS.canonical_sha256(
            tuple(
                FULL_TRANSLATION_POLICY[record_id]
                for record_id in OWNED_RECORD_IDS
            )
        )
        != EXPECTED_OWNED_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} translation policy digest drifted"
        )
    for label in PK_OWNED_ARCHIVE_DIGESTS:
        if (
            GENERAL.subset_digest(
                records_by_label[label],
                OWNED_RECORD_KEYS,
            )
            != PK_OWNED_ARCHIVE_DIGESTS[label]
            or GENERAL.subset_digest(
                records_by_label[label],
                RECORD_KEYS,
            )
            != PK_VISIBLE_ARCHIVE_DIGESTS[label]
            or GENERAL.subset_digest(
                records_by_label[label],
                FULL_RECORD_KEYS,
            )
            != PK_FULL_ARCHIVE_DIGESTS[label]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} independent {label} digest drifted"
            )
    hidden_keys = tuple(
        (BLOCK_ID, record_id) for record_id in HIDDEN_RECORD_IDS
    )
    for label in PK_OWNED_ARCHIVE_DIGESTS:
        if (
            GENERAL.subset_digest(records_by_label[label], hidden_keys)
            != HIDDEN_EMPTY_RAW_SHA256
            or any(
                records_by_label[label][key].data
                != bytes.fromhex("070701070702050505")
                for key in hidden_keys
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} hidden raw record drifted: {label}"
            )
    for pk_record_id, base_record_id in mapping.items():
        pk_key = (BLOCK_ID, pk_record_id)
        base_key = (BLOCK_ID, base_record_id)
        for label in PK_OWNED_ARCHIVE_DIGESTS:
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
            EXPECTED_FULL_PK_JP[pk_record_id],
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


def caller_context(
    records: dict[tuple[int, int], Any],
    call_site: str,
) -> tuple[str, str]:
    block_id, record_id, gap_id, _ = (
        int(value) for value in call_site.split(":")
    )
    literals = ENGINE.parse_record_literals(records[(block_id, record_id)])
    return (
        literals[gap_id - 1].text if gap_id else "",
        literals[gap_id].text if gap_id < len(literals) else "",
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
            if mode == "flatten_command_in_caller":
                if (
                    call_site not in source_calls
                    or call_site in current_calls
                    or caller_context(source, call_site)
                    != (
                        example["observed_source_left"],
                        example["observed_source_right"],
                    )
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} flattened caller evidence "
                        f"drifted: {root}/{call_site}"
                    )
            elif call_site not in current_calls:
                raise RuntimeError(
                    f"segment {SEGMENT} live caller evidence drifted: "
                    f"{root}/{call_site}"
                )
            if caller_context(current, call_site) != (
                example["observed_current_left"],
                example["observed_current_right"],
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} current caller context drifted: "
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
            f"segment {SEGMENT} caller integration class count drifted"
        )


def assert_runtime_graph(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[str, tuple[tuple[int | str, ...], ...]]:
    target_ids = set(OWNED_RECORD_IDS)
    visible_ids = set(RECORD_IDS)
    full_ids = set(FULL_RECORD_IDS)
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    for label, records in (("pk_jp", source), ("pk_current", current)):
        target_edges = incoming_jump_rows(records, target_ids)
        visible_edges = incoming_jump_rows(records, visible_ids)
        full_edges = incoming_jump_rows(records, full_ids)
        if (
            len(target_edges) != 70
            or {row[4] for row in target_edges} != target_ids
            or HELPERS.canonical_sha256(target_edges)
            != PK_TARGET_INCOMING_SHA256
            or len(visible_edges) != 67
            or {row[4] for row in visible_edges} != visible_ids
            or HELPERS.canonical_sha256(visible_edges)
            != PK_VISIBLE_INCOMING_SHA256
            or len(full_edges) != 77
            or {row[4] for row in full_edges} != full_ids
            or HELPERS.canonical_sha256(full_edges)
            != PK_FULL_INCOMING_SHA256
        ):
            raise RuntimeError(
                f"segment {SEGMENT} independent {label} "
                "incoming 014A graph drifted"
            )
        graph = HELPERS.graph_edges(records)
        for root, expected_closure in EXPECTED_ROOT_CLOSURES.items():
            if tuple(sorted(HELPERS.graph_closure(graph, root))) != (
                expected_closure
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} independent {label} "
                    f"closure drifted: {root}"
                )
        if tuple(sorted(HELPERS.graph_closure(graph, 743))) != (
            743,
            2154,
            2155,
        ):
            raise RuntimeError(
                f"segment {SEGMENT} independent {label} "
                "subroot 743 closure drifted"
            )
        subroot_calls = HELPERS.root_call_sites(records, 743)
        if (
            len(subroot_calls) != 2
            or HELPERS.canonical_sha256(subroot_calls)
            != "474EF6CAEBDAC840DEE970735A55E7AA55A7A048A8D807149C3BDD7F1F7C0BC7"
            or HELPERS.fixed_following_blockers(records, 743)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} independent {label} "
                "subroot 743 call evidence drifted"
            )
        chain_gap = gap_bytes(records[(7, 2442)])[2]
        chain_commands = tuple(
            (
                match.start(),
                struct.unpack("<I", match.group(1))[0],
            )
            for match in HELPERS.MORPHOLOGY_COMMAND_RE.finditer(
                chain_gap
            )
        )
        if (
            hashlib.sha256(chain_gap).hexdigest().upper()
            != ROOT784_ROOT730_CHAIN_GAP_SHA256
            or chain_commands != ROOT784_ROOT730_CHAIN_COMMANDS
        ):
            raise RuntimeError(
                f"segment {SEGMENT} independent {label} "
                "root784/root730 fixed command chain drifted"
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

    evidence = collect_call_evidence(source, current)
    if (
        HELPERS.canonical_sha256(evidence)
        != EXPECTED_CALL_EVIDENCE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} independent PK "
            "0143 call/fixed/flatten evidence drifted"
        )
    assert_caller_integration_evidence(source, current)
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
        or tuple(
            literal_texts(source, (BLOCK_ID, record_id))[0]
            for record_id in RIGHT_BOUNDARY_IDS
        )
        != RIGHT_BOUNDARY_JP
        or tuple(
            literal_texts(current, (BLOCK_ID, record_id))[0]
            for record_id in RIGHT_BOUNDARY_IDS
        )
        != RIGHT_BOUNDARY_CURRENT
    ):
        raise RuntimeError(
            f"segment {SEGMENT} full seven-register boundary drifted"
        )
    if (
        LEFT_BOUNDARY_POLICY
        != tuple(
            LEFT_BASE.FULL_TRANSLATION_POLICY[record_id - 68]
            for record_id in LEFT_BOUNDARY_IDS
        )
        or RIGHT_BOUNDARY_POLICY
        != tuple(
            RIGHT_BASE.FULL_TRANSLATION_POLICY[record_id - 68]
            for record_id in RIGHT_BOUNDARY_IDS
        )
        or tuple(
            TRANSLATIONS_BY_RECORD[record_id]
            for record_id in range(2135, 2140)
        )
        != LEFT_BOUNDARY_POLICY[2:]
        or tuple(
            TRANSLATIONS_BY_RECORD[record_id]
            for record_id in range(2203, 2205)
        )
        != RIGHT_BOUNDARY_POLICY[:2]
        or LEFT_BOUNDARY_IDS != LEFT_PK.RIGHT_ROOT724_FULL_IDS
        or LEFT_BOUNDARY_JP != LEFT_PK.RIGHT_ROOT724_FULL_JP
        or LEFT_BOUNDARY_CURRENT
        != LEFT_PK.RIGHT_ROOT724_FULL_CURRENT
        or LEFT_BOUNDARY_POLICY
        != LEFT_PK.RIGHT_ROOT724_FULL_POLICY
    ):
        raise RuntimeError(
            f"segment {SEGMENT} full boundary policy drifted"
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
    for pk_record_id in RECORD_IDS:
        base_record_id = mapping[pk_record_id]
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
                f"segment {SEGMENT} completed Base semantic policy "
                f"drifted: {coordinate}"
            )
    for pk_record_id in HIDDEN_RECORD_IDS:
        base_record_id = mapping[pk_record_id]
        if (
            f"{BLOCK_ID}:{base_record_id}:0" in rows_by_coordinate
            or FULL_TRANSLATION_POLICY[pk_record_id] != ""
        ):
            raise RuntimeError(
                f"segment {SEGMENT} hidden Base policy drifted: "
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
            LEFT_BASE.FULL_TRANSLATION_POLICY[base_record_id]
            if base_record_id in LEFT_BASE.FULL_TRANSLATION_POLICY
            else RIGHT_BASE.FULL_TRANSLATION_POLICY[base_record_id]
        )
        if FULL_TRANSLATION_POLICY[pk_record_id] != expected:
            raise RuntimeError(
                f"segment {SEGMENT} mapped semantic policy drifted: "
                f"{pk_record_id}/{base_record_id}"
            )
    if any(
        (
            not translation
            or "\r" in translation
            or "\n" in translation
            or translation != translation.strip()
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation)
        )
        for translation in translations.values()
    ):
        raise RuntimeError(
            f"segment {SEGMENT} protected translation text drifted"
        )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    translations: dict[str, str],
) -> tuple[bytes, str]:
    pk = prepared.resources["pk_msggame"]
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
        pk.current_blob,
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
            != (translations[f"{BLOCK_ID}:{record_id}:0"],)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} candidate terminal drifted: {key}"
            )
    for record_id in HIDDEN_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        if candidate_records[key].data != current[key].data:
            raise RuntimeError(
                f"segment {SEGMENT} hidden record changed: {key}"
            )
    if ENGINE.rebuild_packed_with_literals(candidate, reverse) != (
        pk.current_blob
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
        row_examples = list(
            CALLER_INTEGRATION_EVIDENCE.get(root, ())
        )
        if root == 742:
            row_examples.extend(CALLER_INTEGRATION_EVIDENCE[743])
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
                "source_free_current_caller_evidence": row_examples,
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
                    "visible_owned_terminal_record_ids": [
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
                        root
                        in {
                            724,
                            730,
                            736,
                            742,
                            748,
                            754,
                            760,
                            766,
                            772,
                            778,
                            784,
                        }
                    ),
                    "assembly_plan": ROOT_ASSEMBLY_PLAN[root],
                    "source_free_caller_integration_examples":
                    row_examples,
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
                "segment": "pk_msggame_B005_S1037",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [67, 133],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "owned_record_count": len(OWNED_RECORD_IDS),
                "source_literal_count": len(RECORD_IDS),
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "confirmed_non_display": len(HIDDEN_RECORD_IDS),
                "changed_literal_count": EXPECTED_CHANGED_LITERAL_COUNT,
                "caller_integration_example_class_counts":
                EXPECTED_INTEGRATION_CLASS_COUNTS,
                "base_mapping_method": (
                    "global_unique_exact70_literal_gap_reverse_search"
                ),
                "discovered_base_record_range": [2067, 2136],
                "discovered_pk_minus_base_offset": offset,
                "source_sequence_sha256":
                EXPECTED_SOURCE_SEQUENCE_SHA256,
                "base_reverse_map_sha256": EXPECTED_MAPPING_SHA256,
                "visible_translation_policy_sha256":
                EXPECTED_VISIBLE_POLICY_SHA256,
                "owned_translation_policy_sha256":
                EXPECTED_OWNED_POLICY_SHA256,
                "hidden_raw_sha256": HIDDEN_EMPTY_RAW_SHA256,
                "pk_target70_incoming_sha256":
                PK_TARGET_INCOMING_SHA256,
                "pk_visible67_incoming_sha256":
                PK_VISIBLE_INCOMING_SHA256,
                "pk_full77_incoming_sha256":
                PK_FULL_INCOMING_SHA256,
                "pk_call_fixed_flatten_evidence_sha256":
                EXPECTED_CALL_EVIDENCE_SHA256,
                "root784_root730_fixed_chain_gap_sha256":
                ROOT784_ROOT730_CHAIN_GAP_SHA256,
                "valid_incoming_014c_count": 0,
                "left_root724_full_policy":
                list(LEFT_BOUNDARY_POLICY),
                "right_root784_full_policy":
                list(RIGHT_BOUNDARY_POLICY),
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
                "subroot743_closure_exact": True,
                "root784_root730_fixed_command_chain_exact": True,
                "call_fixed_flatten_evidence_exact": True,
                "source_free_current_caller_evidence_exact": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "both_boundary_full_register_contracts_exact": True,
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
