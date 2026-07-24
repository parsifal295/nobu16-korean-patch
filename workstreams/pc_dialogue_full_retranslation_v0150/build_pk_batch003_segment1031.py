#!/usr/bin/env python3
"""Build PK block-0 runtime-terminal segment 1031 decisions."""

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

import build_base_batch003_segment1009 as BASE_TAIL
import build_base_batch003_segment1010 as BASE_NEXT
import build_pk_batch001_segment1025 as HELPERS
import build_pk_batch003_segment1030 as LEFT_PK


ENGINE = BASE_TAIL.ENGINE
GENERAL = BASE_TAIL.GENERAL
UTIL = BASE_TAIL.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B003_S1031.private.v1.jsonl"
)
SEGMENT = 1031
QUEUE_BATCH_ID = "pk_msggame-B003"
BLOCK_ID = 0
QUEUE_ZERO_BASED_START = 67
QUEUE_ZERO_BASED_STOP = 134
RECORD_IDS = tuple(range(1730, 1797))
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
TARGET_COORDINATES = tuple(
    f"{BLOCK_ID}:{record_id}:0" for record_id in RECORD_IDS
)
PK_RECORD_COUNT = 21751

EXPECTED_PK_JP = (
    "ご覧にいれ",
    "ご覧にいれ",
    "ご覧にいれ",
    "みせ",
    "ございません",
    "ござらぬ",
    "ございません",
    "ございません",
    "ございません",
    "ござらぬ",
    "ござらぬ",
    "しません",
    "さぬ",
    "しませぬ",
    "しません",
    "しません",
    "しませぬ",
    "さぬ",
    "しています",
    "しておる",
    "しております",
    "しておりまする",
    "しています",
    "しております",
    "しておる",
    "ください",
    "してくれ",
    "ください",
    "くだされ",
    "ください",
    "あれ",
    "してくれ",
    "じています",
    "じておる",
    "じております",
    "じておりまする",
    "じています",
    "じております",
    "じておる",
    "しなければ",
    "せねば",
    "しなければ",
    "せねば",
    "しなければ",
    "せねば",
    "せねば",
    "しまいました",
    "しまった",
    "しまいました",
    "しまいました",
    "しまいました",
    "しまいました",
    "しまった",
    "しましょう",
    "しよう",
    "いたしましょう",
    "いたしましょう",
    "しましょう",
    "いたそう",
    "しよう",
    "じましょう",
    "じよう",
    "じましょう",
    "じましょう",
    "じましょう",
    "ずるといたそう",
    "じよう",
)
TRANSLATION_POLICY = (
    "보여 드리",
    "보여 드리",
    "보여 드리",
    "보여",
    "없습니다",
    "없소",
    "없습니다",
    "없습니다",
    "없습니다",
    "없소",
    "없소",
    "하지 않습니다",
    "하지 않는다",
    "하지 않사옵니다",
    "하지 않습니다",
    "하지 않습니다",
    "하지 않사옵니다",
    "하지 않는다",
    "하고 있습니다",
    "하고 있다",
    "하고 있습니다",
    "하고 있사옵니다",
    "하고 있습니다",
    "하고 있습니다",
    "하고 있다",
    "해 주십시오",
    "해 다오",
    "해 주십시오",
    "해 주시오",
    "해 주십시오",
    "하시라",
    "해 다오",
    "하고 있습니다",
    "하고 있다",
    "하고 있습니다",
    "하고 있사옵니다",
    "하고 있습니다",
    "하고 있습니다",
    "하고 있다",
    "하지 않으면",
    "해야만",
    "하지 않으면",
    "해야만",
    "하지 않으면",
    "해야만",
    "해야만",
    "버렸습니다",
    "버렸다",
    "버렸습니다",
    "버렸습니다",
    "버렸습니다",
    "버렸습니다",
    "버렸다",
    "합시다",
    "하자",
    "하겠습니다",
    "하겠습니다",
    "합시다",
    "하겠소",
    "하자",
    "읍시다",
    "자",
    "읍시다",
    "읍시다",
    "읍시다",
    "기로 하겠소",
    "자",
)
TRANSLATIONS_BY_RECORD = dict(
    zip(RECORD_IDS, TRANSLATION_POLICY, strict=True)
)
TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}

ROOT_TERMINALS = {
    388: tuple(range(1730, 1734)),
    394: tuple(range(1734, 1741)),
    400: tuple(range(1741, 1748)),
    406: tuple(range(1748, 1755)),
    412: tuple(range(1755, 1762)),
    418: tuple(range(1762, 1769)),
    1144: tuple(range(1769, 1776)),
    1150: tuple(range(1776, 1783)),
    424: tuple(range(1783, 1790)),
    430: tuple(range(1790, 1797)),
}
RECORD_TO_ROOT = {
    record_id: root
    for root, record_ids in ROOT_TERMINALS.items()
    for record_id in record_ids
}
ASSEMBLY_CLASS = {
    388: "show_action_fragment_with_fixed_following",
    394: "negative_copular_or_existence",
    400: "negative_action_predicate",
    406: "progressive_action_predicate",
    412: "benefactive_request_action",
    418: "voiced_progressive_action",
    1144: "conditional_or_elliptical_obligation",
    1150: "completive_past_action",
    424: "volitional_or_intention_action",
    430: "voiced_volitional_action",
}

LEFT_ROOT388_FULL_IDS = tuple(range(1727, 1734))
LEFT_ROOT388_FULL_JP = (
    "みせ",
    "みせ",
    "ご覧にいれ",
    "ご覧にいれ",
    "ご覧にいれ",
    "ご覧にいれ",
    "みせ",
)
LEFT_ROOT388_FULL_CURRENT = (
    "보여",
    "보여",
    "보여 드리",
    "보여 드리",
    "보여 드리",
    "보여 드리",
    "보여",
)
LEFT_ROOT388_FULL_POLICY = LEFT_ROOT388_FULL_CURRENT

# The queue boundary is exactly between complete terminal groups.  Root 436
# is the next full group and belongs wholly to S1032; it is not shared.
RIGHT_NEXT_ROOT436_FULL_IDS = tuple(range(1797, 1804))
RIGHT_NEXT_ROOT436_FULL_JP = (
    "じてください",
    "ぜよ",
    "じてください",
    "じてくだされ",
    "じてください",
    "じてくだされ",
    "じろ",
)
RIGHT_NEXT_ROOT436_FULL_CURRENT = (
    "해 주십시오",
    "하라",
    "해 주십시오",
    "해 주시오",
    "해 주십시오",
    "해 주시오",
    "하라",
)
RIGHT_NEXT_ROOT436_FULL_POLICY = RIGHT_NEXT_ROOT436_FULL_CURRENT

EXPECTED_ROOT_CLOSURES = {
    388: tuple(range(388, 394)) + LEFT_ROOT388_FULL_IDS,
    394: tuple(range(394, 400)) + tuple(range(1734, 1741)),
    400: tuple(range(400, 406)) + tuple(range(1741, 1748)),
    406: tuple(range(406, 412)) + tuple(range(1748, 1755)),
    412: tuple(range(412, 418)) + tuple(range(1755, 1762)),
    418: tuple(range(418, 424)) + tuple(range(1762, 1769)),
    1144: tuple(range(1144, 1150)) + tuple(range(1769, 1776)),
    1150: tuple(range(1150, 1156)) + tuple(range(1776, 1783)),
    424: tuple(range(424, 430)) + tuple(range(1783, 1790)),
    430: tuple(range(430, 436)) + tuple(range(1790, 1797)),
    436: tuple(range(436, 442)) + RIGHT_NEXT_ROOT436_FULL_IDS,
}

PK_ARCHIVE_DIGESTS = {
    "pk_jp": "C22B607CD134B7849D8A585F59F867221C994D8AB0820E0BF134FD1ABFA1D254",
    "pk_current": "FD4E370BDA35D614FE79E1EBE763540FDCE759B0A8719BFDAC2ADF6E08FF9102",
    "pk_sc": "3CAD2544D6C090EBA413492E527AEEE8A87312E60C24F9D89581AF8D6FBBFCD6",
    "pk_tc": "3CAD2544D6C090EBA413492E527AEEE8A87312E60C24F9D89581AF8D6FBBFCD6",
    "pk_en": "3CAD2544D6C090EBA413492E527AEEE8A87312E60C24F9D89581AF8D6FBBFCD6",
}
TARGET_JUMP_EDGE_SHA256 = (
    "DECF445679FC75FA2C608DC95F46EAAA5AE6BB2BBE9766BFDA57921841F1EF4F"
)
FULL_JUMP_EDGE_SHA256 = (
    "E49736C52E0D1DD0F83A3EEEB84332F2762A6B45B2B028BC61DA393CB0FE302B"
)
EXPECTED_REVERSE_MAP_SHA256 = (
    "3FD6443304B00A92BCF334CA3582BC4B39ED26EEDAF69AC4A0C70249D9C022A9"
)
EXPECTED_POLICY_SHA256 = (
    "E83F0416B1CA96F29B2BACC759B1709DF20DF5AE0AE506AC4EB5EE159B76D5B8"
)
EMPTY_CANONICAL_SHA256 = (
    "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
)
EXPECTED_CALL_EVIDENCE = {
    388: (
        (3, "2DB01A0396F71E4807ABAB5D3F9A1D1562907164AA57E0B7AFBA3967F5E17BA5", 3, "BF1A8023416A955DD1B56D13EF56702BA4B04E2ED1E2277113B809B494853EC8"),
        (3, "2DB01A0396F71E4807ABAB5D3F9A1D1562907164AA57E0B7AFBA3967F5E17BA5", 3, "BF1A8023416A955DD1B56D13EF56702BA4B04E2ED1E2277113B809B494853EC8"),
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
    ),
    394: (
        (5, "AEC6691AA535E0E81B0D79BECBB890B4215E0980E52E3376AD41A3918E2B0B57", 0, EMPTY_CANONICAL_SHA256),
        (3, "ADFEEB33E43F59B3BF076FA68B146EF160340574CE0BB882F4F137BDC47E5D55", 0, EMPTY_CANONICAL_SHA256),
        (2, "55E9EA7BABFE1E93606A53EEC458A65C90D278061356D857D91CE3EBEFBF8F5A", 0, EMPTY_CANONICAL_SHA256),
    ),
    400: (
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
    ),
    406: (
        (8, "A995829F4F4777987DC83B0C964ED77BF1FDBB438F157B8528811234323A38E6", 3, "740E74E71A82FA75655153532EAD3C0208AF438A59C795467CADDD6934117936"),
        (6, "6E2BFFEFE94716D77F3096884B3076F5FDAAC3C33735A1A9E42077DA27D5B537", 3, "740E74E71A82FA75655153532EAD3C0208AF438A59C795467CADDD6934117936"),
        (2, "B482E3E944248D1A229FD72DF1FD22356F3E0670094DA20AE6D389106C7D7A2F", 0, EMPTY_CANONICAL_SHA256),
    ),
    412: (
        (21, "0042761105F4FEDC4CB537DDC73B4D44E3DF199EAE77A44A59634E4B2ABA4FFD", 0, EMPTY_CANONICAL_SHA256),
        (17, "EF15DD704131F9C2C998B3A1FCCCA6E56E6B45ADE1B04046A8173AA8C16CDEE4", 0, EMPTY_CANONICAL_SHA256),
        (4, "A054F6BF373BB964F5FDDA863B4DEEB3E56A3BA811DFCF2D7FA5500D9AB85750", 0, EMPTY_CANONICAL_SHA256),
    ),
    418: (
        (1, "ACEFACB484E7B20FCA8FCDA34191D72E96CE112B9812A13EDD9411E850A2BDE3", 0, EMPTY_CANONICAL_SHA256),
        (1, "ACEFACB484E7B20FCA8FCDA34191D72E96CE112B9812A13EDD9411E850A2BDE3", 0, EMPTY_CANONICAL_SHA256),
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
    ),
    1144: (
        (4, "F30F2FCC808F861A854E948213F85F0FEC36FC0E1B099C20A002A662CF894A37", 3, "644C145E24038FEAE0A537B8D86E0BA247D54FC4CA0C541404D28294061EDDCA"),
        (4, "F30F2FCC808F861A854E948213F85F0FEC36FC0E1B099C20A002A662CF894A37", 3, "644C145E24038FEAE0A537B8D86E0BA247D54FC4CA0C541404D28294061EDDCA"),
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
    ),
    1150: (
        (1, "B288716EAE5EB02EAF5A4DA79A7E8C21E7751EA7962120A2A81C2A892C44E052", 0, EMPTY_CANONICAL_SHA256),
        (1, "B288716EAE5EB02EAF5A4DA79A7E8C21E7751EA7962120A2A81C2A892C44E052", 0, EMPTY_CANONICAL_SHA256),
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
    ),
    424: (
        (16, "C4CE3609502A65FBD37BA910345B59A88B3EB640F0FFCF01E2C8BCD2360B3BDD", 1, "E6CF2281AAB5E987E5E11D2063A5FB029C595F4294230FFEFCD6A8176E57B956"),
        (15, "9990454E446C84B007E313E7668E97C8691A54193A93CBFE2F2991B3AE8C9954", 1, "E6CF2281AAB5E987E5E11D2063A5FB029C595F4294230FFEFCD6A8176E57B956"),
        (1, "0388FE507E3F237F9AF1DCF7BFAC7B764903007A5D8F69BB97B935A7E576F613", 0, EMPTY_CANONICAL_SHA256),
    ),
    430: (
        (3, "025DF3A27764756BFDFA82E690916EF04F4DD6BF80BAE67D11C7F7C487942F8C", 0, EMPTY_CANONICAL_SHA256),
        (1, "6C0EC577256CA410248851B647B757CCB0D3E5CC2185416163689AC1A06689F2", 0, EMPTY_CANONICAL_SHA256),
        (2, "078F8B02564FEA8F104F3C09FDC4B4014BF22087548034631137AADCD2A13419", 0, EMPTY_CANONICAL_SHA256),
    ),
    436: (
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
    ),
}
EXPECTED_CHANGED_LITERAL_COUNT = 21
MORPHOLOGY_014C_RE = re.compile(b"\x01\x4C(.{4})", re.DOTALL)

BASIS = (
    "review_queue_pk_msggame_B003_zero_based_visible_ordinals67_133_"
    "pristine_pk_pc_jp_sole_translation_authority_block0_records1730_"
    "1796_67_visible_no_hidden_or_control_exclusions_independent_pk_"
    "source_policy_archive_and_runtime_evidence_unique_exact_Base_S1009_"
    "tail7_reverse_hit1669_plus_unique_Base_S1010_first60_near_reverse_"
    "hit1676_with_only_base1728_sen_vs_pk1789_shiyou_divergence_same_"
    "haja_semantics_exact_jp_current_sc_tc_en_skeleton_full_014a_0143_"
    "closure_fixed_flatten_and_014c_guards_left_root388_cross_S1030_"
    "right_queue_boundary_exact_between_groups_next_root436_wholly_S1032_"
    "negative_existence_action_progressive_request_conditional_"
    "completive_and_volitional_register_matrices_root430_active_mit_"
    "stem_suffix_endings_source_only_eung_calls_flattened_all_runtime_"
    "pending_"
    "no_historic_or_switch_korean_authority_no_steam"
)


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return tuple(
        literal.text for literal in ENGINE.parse_record_literals(records[key])
    )


def gap_bytes(record: Any) -> tuple[bytes, ...]:
    return HELPERS.record_gaps(record)


def archive_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    return BASE_TAIL.archive_records(prepared)


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


def assert_queue_contract(prepared: Any) -> None:
    rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line
    ]
    batch_targets = [
        target
        for row in rows
        if row.get("batch_id") == QUEUE_BATCH_ID
        for target in row["target_literals"]
    ]
    visible = tuple(
        target["coordinate"]
        for target in batch_targets
        if target.get("visible")
    )
    hidden = tuple(
        target["coordinate"]
        for target in batch_targets
        if not target.get("visible")
    )
    if (
        len(visible) != 200
        or hidden
        or visible[
            QUEUE_ZERO_BASED_START:QUEUE_ZERO_BASED_STOP
        ]
        != TARGET_COORDINATES
    ):
        raise RuntimeError(
            f"segment {SEGMENT} private queue ordinal contract drifted"
        )


def discover_mapping(
    base_jp: dict[tuple[int, int], Any],
    pk_jp: dict[tuple[int, int], Any],
) -> dict[int, int]:
    maximum = max(
        record_id
        for block_id, record_id in base_jp
        if block_id == BLOCK_ID
    )
    tail_signature = record_signature(pk_jp, 1730, 7)
    tail_hits = tuple(
        start
        for start in range(maximum - 7 + 2)
        if all(
            (BLOCK_ID, start + ordinal) in base_jp
            for ordinal in range(7)
        )
        and record_signature(base_jp, start, 7) == tail_signature
    )

    next_signature = record_signature(pk_jp, 1737, 60)
    next_hits: list[tuple[int, tuple[int, ...]]] = []
    for start in range(maximum - 60 + 2):
        if not all(
            (BLOCK_ID, start + ordinal) in base_jp
            for ordinal in range(60)
        ):
            continue
        candidate = record_signature(base_jp, start, 60)
        if any(
            candidate[ordinal][1] != next_signature[ordinal][1]
            for ordinal in range(60)
        ):
            continue
        mismatches = tuple(
            ordinal
            for ordinal in range(60)
            if candidate[ordinal][0] != next_signature[ordinal][0]
        )
        if len(mismatches) <= 1:
            next_hits.append((start, mismatches))
    if tail_hits != (1669,) or next_hits != [(1676, (52,))]:
        raise RuntimeError(
            f"segment {SEGMENT} independent Base reverse search "
            f"drifted: {tail_hits}/{next_hits}"
        )

    mapping = {
        pk_record_id: (
            tail_hits[0] + ordinal
            if pk_record_id < 1737
            else next_hits[0][0] + pk_record_id - 1737
        )
        for ordinal, pk_record_id in enumerate(RECORD_IDS)
    }
    mapping_sha256 = HELPERS.canonical_sha256(
        [[pk_record_id, base_record_id]
         for pk_record_id, base_record_id in mapping.items()]
    )
    if (
        mapping_sha256 != EXPECTED_REVERSE_MAP_SHA256
        or tuple(mapping.values()) != tuple(range(1669, 1736))
    ):
        raise RuntimeError(f"segment {SEGMENT} reverse map drifted")
    return mapping


def assert_source_and_mapping(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    mapping: dict[int, int],
) -> None:
    for label, expected_digest in PK_ARCHIVE_DIGESTS.items():
        actual_digest = GENERAL.subset_digest(
            records_by_label[label],
            RECORD_KEYS,
        )
        if actual_digest != expected_digest:
            raise RuntimeError(
                f"segment {SEGMENT} independent {label} digest drifted"
            )

    for ordinal, (pk_record_id, base_record_id) in enumerate(
        mapping.items()
    ):
        pk_key = (BLOCK_ID, pk_record_id)
        base_key = (BLOCK_ID, base_record_id)
        for label in PK_ARCHIVE_DIGESTS:
            if (
                len(literal_texts(records_by_label[label], pk_key)) != 1
                or gap_bytes(records_by_label[label][pk_key])
                != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} independent PK skeleton "
                    f"drifted: {label}/{pk_key}"
                )
        if literal_texts(records_by_label["pk_jp"], pk_key) != (
            EXPECTED_PK_JP[ordinal],
        ):
            raise RuntimeError(
                f"segment {SEGMENT} pristine PK source drifted: {pk_key}"
            )
        for label in ("pk_sc", "pk_tc", "pk_en"):
            if literal_texts(records_by_label[label], pk_key) != ("",):
                raise RuntimeError(
                    f"segment {SEGMENT} blank context drifted: "
                    f"{label}/{pk_key}"
                )

        for language in ("jp", "current", "sc", "tc"):
            if (
                pk_record_id == 1789
                and language in ("jp", "current")
            ):
                continue
            if (
                records_by_label[f"pk_{language}"][pk_key].data
                != records_by_label[f"base_{language}"][base_key].data
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} exact Base/PK {language} "
                    f"mapping drifted: {base_key}/{pk_key}"
                )

    if (
        literal_texts(records_by_label["base_jp"], (BLOCK_ID, 1728))
        != ("せん",)
        or literal_texts(records_by_label["pk_jp"], (BLOCK_ID, 1789))
        != ("しよう",)
        or literal_texts(
            records_by_label["base_current"],
            (BLOCK_ID, 1728),
        )
        != ("않다",)
        or literal_texts(
            records_by_label["pk_current"],
            (BLOCK_ID, 1789),
        )
        != ("하자",)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} unique Base/PK divergence drifted"
        )


def assert_runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    target_ids = set(RECORD_IDS)
    full_ids = target_ids | {1727, 1728, 1729}
    for label in ("pk_jp", "pk_current"):
        records = records_by_label[label]
        target_edges = [
            [block_id, record_id, operand]
            for (block_id, record_id), record in sorted(records.items())
            for operand in BASE_TAIL.GRAPH.operands(
                record.data,
                BASE_TAIL.GRAPH.MORPHOLOGY_JUMP_RE,
            )
            if operand in target_ids
        ]
        full_edges = [
            [block_id, record_id, operand]
            for (block_id, record_id), record in sorted(records.items())
            for operand in BASE_TAIL.GRAPH.operands(
                record.data,
                BASE_TAIL.GRAPH.MORPHOLOGY_JUMP_RE,
            )
            if operand in full_ids
        ]
        target_digest = hashlib.sha256(
            json.dumps(target_edges, separators=(",", ":")).encode("ascii")
        ).hexdigest().upper()
        full_digest = hashlib.sha256(
            json.dumps(full_edges, separators=(",", ":")).encode("ascii")
        ).hexdigest().upper()
        if (
            len(target_edges) != 67
            or {row[2] for row in target_edges} != target_ids
            or target_digest != TARGET_JUMP_EDGE_SHA256
            or len(full_edges) != 70
            or {row[2] for row in full_edges} != full_ids
            or full_digest != FULL_JUMP_EDGE_SHA256
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} 014A graph drifted"
            )

        graph = HELPERS.graph_edges(records)
        for root, expected_closure in EXPECTED_ROOT_CLOSURES.items():
            actual_closure = tuple(
                sorted(HELPERS.graph_closure(graph, root))
            )
            if actual_closure != expected_closure:
                raise RuntimeError(
                    f"segment {SEGMENT} {label} full closure drifted: "
                    f"{root}"
                )

    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    for root, expected_evidence in EXPECTED_CALL_EVIDENCE.items():
        source_calls = HELPERS.root_call_sites(source, root)
        current_calls = HELPERS.root_call_sites(current, root)
        source_fixed = HELPERS.fixed_following_blockers(source, root)
        current_fixed = HELPERS.fixed_following_blockers(current, root)
        source_only = tuple(sorted(set(source_calls) - set(current_calls)))
        current_only = tuple(sorted(set(current_calls) - set(source_calls)))
        actual_evidence = (
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
        if actual_evidence != expected_evidence:
            raise RuntimeError(
                f"segment {SEGMENT} root {root} "
                "0143/fixed/flatten evidence drifted"
            )

    for label in ("pk_jp", "pk_current"):
        valid: list[tuple[int, int, int, int, int]] = []
        overlapped: list[tuple[int, int, int, int, int]] = []
        for (block_id, record_id), record in sorted(
            records_by_label[label].items()
        ):
            for gap_id, gap in enumerate(gap_bytes(record)):
                jump_spans = [
                    range(match.start(), match.end())
                    for match in (
                        BASE_TAIL.GRAPH.MORPHOLOGY_JUMP_RE.finditer(gap)
                    )
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
        if (
            valid
            or tuple(overlapped)
            != ((15, 25, 0, 65, 84213762),)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} 014C evidence drifted"
            )

    # Completed Base audits are auxiliary cross-checks, reached only after
    # all pristine PK evidence above has independently passed.
    BASE_TAIL.assert_corpora(records_by_label)
    BASE_TAIL.assert_full_group_boundaries(records_by_label)
    BASE_TAIL.assert_jump_and_call_graphs(records_by_label)
    BASE_TAIL.assert_014c_and_blockers(records_by_label)
    BASE_NEXT.assert_corpora(records_by_label)
    BASE_NEXT.assert_runtime_graph(records_by_label)
    BASE_NEXT.assert_fixed_following(records_by_label)


def assert_boundaries(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    actual_left_jp = tuple(
        literal_texts(source, (BLOCK_ID, record_id))[0]
        for record_id in LEFT_ROOT388_FULL_IDS
    )
    actual_left_current = tuple(
        literal_texts(current, (BLOCK_ID, record_id))[0]
        for record_id in LEFT_ROOT388_FULL_IDS
    )
    if (
        actual_left_jp != LEFT_ROOT388_FULL_JP
        or actual_left_current != LEFT_ROOT388_FULL_CURRENT
        or LEFT_ROOT388_FULL_IDS != LEFT_PK.RIGHT_ROOT388_FULL_IDS
        or LEFT_ROOT388_FULL_JP != LEFT_PK.RIGHT_ROOT388_FULL_JP
        or LEFT_ROOT388_FULL_CURRENT
        != LEFT_PK.RIGHT_ROOT388_FULL_CURRENT
        or LEFT_ROOT388_FULL_POLICY
        != LEFT_PK.RIGHT_ROOT388_FULL_POLICY
    ):
        raise RuntimeError(
            f"segment {SEGMENT} S1030/S1031 root388 boundary drifted"
        )

    actual_right_jp = tuple(
        literal_texts(source, (BLOCK_ID, record_id))[0]
        for record_id in RIGHT_NEXT_ROOT436_FULL_IDS
    )
    actual_right_current = tuple(
        literal_texts(current, (BLOCK_ID, record_id))[0]
        for record_id in RIGHT_NEXT_ROOT436_FULL_IDS
    )
    auxiliary_right_policy = tuple(
        BASE_NEXT.FULL_TRANSLATION_POLICY[record_id]
        for record_id in range(1736, 1743)
    )
    if (
        actual_right_jp != RIGHT_NEXT_ROOT436_FULL_JP
        or actual_right_current != RIGHT_NEXT_ROOT436_FULL_CURRENT
        or auxiliary_right_policy != RIGHT_NEXT_ROOT436_FULL_POLICY
        or set(RIGHT_NEXT_ROOT436_FULL_IDS).intersection(RECORD_IDS)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} right non-shared root436 drifted"
        )

    if (
        tuple(
            TRANSLATIONS_BY_RECORD[record_id]
            for record_id in range(1730, 1734)
        )
        != LEFT_ROOT388_FULL_POLICY[3:]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} owned left boundary policy drifted"
        )


def assert_semantics(
    mapping: dict[int, int],
    translations: dict[str, str],
) -> None:
    policy_rows = [
        [
            record_id,
            EXPECTED_PK_JP[ordinal],
            TRANSLATION_POLICY[ordinal],
        ]
        for ordinal, record_id in enumerate(RECORD_IDS)
    ]
    if (
        len(EXPECTED_PK_JP) != 67
        or len(TRANSLATION_POLICY) != 67
        or set(RECORD_TO_ROOT) != set(RECORD_IDS)
        or translations != TRANSLATIONS
        or HELPERS.canonical_sha256(policy_rows)
        != EXPECTED_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} independent semantic policy drifted"
        )

    auxiliary_policy = {
        pk_record_id: (
            BASE_TAIL.TRANSLATIONS_BY_RECORD[base_record_id]
            if base_record_id <= 1675
            else BASE_NEXT.TRANSLATIONS_BY_RECORD[base_record_id]
        )
        for pk_record_id, base_record_id in mapping.items()
    }
    auxiliary_divergences = {
        record_id: (
            auxiliary_policy[record_id],
            TRANSLATIONS_BY_RECORD[record_id],
        )
        for record_id in RECORD_IDS
        if auxiliary_policy[record_id]
        != TRANSLATIONS_BY_RECORD[record_id]
    }
    if auxiliary_divergences != {
        1790: ("합시다", "읍시다"),
        1791: ("하자", "자"),
        1792: ("합시다", "읍시다"),
        1793: ("합시다", "읍시다"),
        1794: ("합시다", "읍시다"),
        1795: ("하기로 하겠소", "기로 하겠소"),
        1796: ("하자", "자"),
    }:
        raise RuntimeError(
            f"segment {SEGMENT} auxiliary Base policy drifted"
        )
    BASE_TAIL.assert_semantics(BASE_TAIL.TRANSLATIONS)
    BASE_NEXT.assert_semantics(BASE_NEXT.RAW_TRANSLATIONS)

    if (
        TRANSLATIONS_BY_RECORD[1760] != "하시라"
        or TRANSLATIONS_BY_RECORD[1788] != "하겠소"
        or TRANSLATIONS_BY_RECORD[1789] != "하자"
        or TRANSLATIONS_BY_RECORD[1795] != "기로 하겠소"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} speech-level or volitional policy drifted"
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
        or set(replacements)
        != {(BLOCK_ID, record_id, 0) for record_id in RECORD_IDS}
    ):
        raise RuntimeError(f"segment {SEGMENT} candidate universe drifted")
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
    reversed_blob = ENGINE.rebuild_packed_with_literals(candidate, reverse)
    if reversed_blob != pk.current_blob:
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
]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_queue_contract(prepared)
    records_by_label = archive_records(prepared)
    mapping = discover_mapping(
        records_by_label["base_jp"],
        records_by_label["pk_jp"],
    )
    assert_source_and_mapping(records_by_label, mapping)
    assert_runtime_evidence(records_by_label)
    assert_boundaries(records_by_label)
    translations = dict(TRANSLATIONS)
    assert_semantics(mapping, translations)

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
                f"segment {SEGMENT} protected text drifted: {coordinate}"
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
        base_record_id = mapping[record_id]
        root = RECORD_TO_ROOT[record_id]
        full_terminal_ids = (
            LEFT_ROOT388_FULL_IDS
            if root == 388
            else ROOT_TERMINALS[root]
        )
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        evidence: dict[str, object] = {
            "automatic_space_inserted": False,
            "leading_trailing_space_protected": True,
            "pk_record_id": record_id,
            "base_semantic_record_id": base_record_id,
            "base_mapping_method": (
                "two_unique_contiguous_reverse_searches_exact_tail7_"
                "and_next60_single_pinned_source_divergence"
            ),
            "root": root,
            "full_terminal_record_ids": list(full_terminal_ids),
            "full_graph_closure_record_ids": list(
                EXPECTED_ROOT_CLOSURES[root]
            ),
            "pk_source_call_count": EXPECTED_CALL_EVIDENCE[root][0][0],
            "pk_current_call_count": EXPECTED_CALL_EVIDENCE[root][1][0],
            "pk_source_fixed_following_count": (
                EXPECTED_CALL_EVIDENCE[root][0][2]
            ),
            "pk_current_fixed_following_count": (
                EXPECTED_CALL_EVIDENCE[root][1][2]
            ),
            "pk_source_calls_flattened_in_current": (
                EXPECTED_CALL_EVIDENCE[root][2][0]
            ),
            "pk_current_only_calls": (
                EXPECTED_CALL_EVIDENCE[root][2][2]
            ),
            "incoming_jump_graph_guarded": True,
            "valid_incoming_014c_count": 0,
            "assembly_class": ASSEMBLY_CLASS[root],
            "runtime_integration_required": True,
        }
        if record_id == 1789:
            evidence["pk_source_diverges_from_base"] = {
                "base_source": "せん",
                "pk_source": "しよう",
                "same_korean_policy": "하자",
            }
        if root == 430:
            evidence["pk_specific_active_caller_composition"] = {
                "source_callers": ["信◆", "応◆", "応◆"],
                "active_current_caller": "1:10:5",
                "active_current_stem": "믿◆",
                "source_only_flattened_callers": [
                    "6:4687:1",
                    "6:4688:1",
                ],
                "terminal_boundary": "읍시다/자/기로 하겠소",
                "reason": (
                    "all seven voice branches compose naturally from "
                    "the active 믿◆ stem; 합시다/하자 would produce "
                    "믿합시다/믿하자"
                ),
            }
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
                "runtime_assembly_evidence": evidence,
            }
        )
    return prepared, translations, rows, candidate, candidate_sha256


def main() -> int:
    first = build_rows()
    second = build_rows()
    prepared, translations, rows, candidate, candidate_sha256 = first
    if (
        translations != second[1]
        or rows != second[2]
        or candidate != second[3]
        or candidate_sha256 != second[4]
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
        or len(translations) != 67
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
        translation
        != literal_texts(
            current,
            (BLOCK_ID, int(coordinate.split(":")[1])),
        )[0]
        for coordinate, translation in translations.items()
    )
    if changed != EXPECTED_CHANGED_LITERAL_COUNT:
        raise RuntimeError(
            f"segment {SEGMENT} changed literal count drifted: {changed}"
        )

    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B003_S1031",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [67, 133],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "source_literal_count": 67,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "confirmed_non_display": 0,
                "changed_literal_count": changed,
                "base_mapping_method": (
                    "unique_exact_tail7_and_unique_next60_with_one_"
                    "pinned_source_divergence"
                ),
                "discovered_base_record_ranges": [
                    [1669, 1675],
                    [1676, 1735],
                ],
                "discovered_pk_minus_base_offset": 61,
                "base_reverse_map_sha256": EXPECTED_REVERSE_MAP_SHA256,
                "translation_policy_sha256": EXPECTED_POLICY_SHA256,
                "pk_base_source_divergence": {
                    "pk_record_id": 1789,
                    "base_record_id": 1728,
                    "base_jp": "せん",
                    "pk_jp": "しよう",
                    "translation": "하자",
                },
                "pk_call_fixed_flatten_evidence": EXPECTED_CALL_EVIDENCE,
                "left_root388_full_policy": list(
                    LEFT_ROOT388_FULL_POLICY
                ),
                "right_shared_root": None,
                "right_next_root436_full_record_ids": list(
                    RIGHT_NEXT_ROOT436_FULL_IDS
                ),
                "candidate_sha256": candidate_sha256,
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
                "target_runtime_skeleton_exact": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "s1030_boundary_cross_assert_exact": True,
                "right_boundary_between_complete_groups": True,
                "second_run_reproduction_exact": True,
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
