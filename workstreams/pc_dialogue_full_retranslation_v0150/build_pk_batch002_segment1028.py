#!/usr/bin/env python3
"""Build PK block-0 runtime-terminal segment 1028 decisions."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch002_segment1007 as BASE
import build_base_batch002_segment1008 as RIGHT_BASE
import build_pk_batch001_segment1025 as SUPPORT
import build_pk_batch002_segment1027 as LEFT_PK
import build_pk_batch002_segment1029 as RIGHT_PK


ENGINE = BASE.ENGINE
GENERAL = BASE.GENERAL
UTIL = BASE.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B002_S1028.private.v1.jsonl"
)
QUEUE_PATH = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "review_queue.private.v1.jsonl"
)
SEGMENT = 1028
BLOCK_ID = 0
QUEUE_BATCH_ID = "pk_msggame-B002"
QUEUE_ZERO_BASED_START = 67
QUEUE_ZERO_BASED_STOP = 134
RECORD_IDS = tuple(range(1530, 1597))
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
BASE_RECORD_MAP = {
    (BLOCK_ID, record_id): (BLOCK_ID, record_id - 54)
    for record_id in RECORD_IDS
}
PK_RECORD_COUNT = 21751

EXPECTED_PK_JP = (
    "なんと",
    "恐れ入ります",
    "恐れ入る",
    "恐れ入ります",
    "恐れ入りまする",
    "恐れ入ります",
    "恐れ入ります",
    "恐れ入る",
    "思います",
    "思う",
    "存じまする",
    "存じます",
    "存じます",
    "存ずる",
    "存ずる",
    "あら",
    "おや",
    "まあ",
    "やや",
    "あら",
    "ふむ",
    "むう",
    "ですか",
    "か",
    "でございますか",
    "でございますか",
    "ですか",
    "でござるか",
    "か",
    "わ",
    "か",
    "わ",
    "か",
    "わ",
    "か",
    "か",
    "ね",
    "か",
    "ですね",
    "ですか",
    "ね",
    "か",
    "か",
    "かしら",
    "か",
    "かしら",
    "か",
    "かしら",
    "か",
    "かな",
    "なんて",
    "か",
    "なんて",
    "か",
    "だわ",
    "か",
    "か",
    "ですか",
    "か",
    "ですか",
    "ですか",
    "ですか",
    "でござるか",
    "か",
    "けれど",
    "が",
    "けれども",
)

TRANSLATION_POLICY = (
    "이런",
    "황송합니다",
    "황송하다",
    "황송합니다",
    "황송하옵니다",
    "황송합니다",
    "황송합니다",
    "황송하다",
    "생각합니다",
    "생각한다",
    "생각하옵니다",
    "생각하옵니다",
    "생각하옵니다",
    "생각하오",
    "생각하오",
    "어머",
    "어라",
    "어머나",
    "아니",
    "어머",
    "흠",
    "으음",
    "입니까",
    "인가",
    "이옵니까",
    "이옵니까",
    "입니까",
    "이오",
    "인가",
    "네",
    "가",
    "네",
    "가",
    "네",
    "가",
    "가",
    "네",
    "가",
    "군요",
    "입니까",
    "네",
    "가",
    "가",
    "일까",
    "인가",
    "일까",
    "인가",
    "일까",
    "인가",
    "일까",
    "다니",
    "나",
    "다니",
    "나",
    "네",
    "나",
    "나",
    "입니까",
    "인가",
    "입니까",
    "입니까",
    "입니까",
    "이오",
    "인가",
    "지만",
    "지만",
    "지만",
)
TRANSLATIONS_BY_RECORD = dict(
    zip(RECORD_IDS, TRANSLATION_POLICY, strict=True)
)
TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}

ROOT_TERMINALS = {
    214: (1530,),
    220: tuple(range(1531, 1538)),
    226: tuple(range(1538, 1545)),
    232: tuple(range(1545, 1552)),
    238: tuple(range(1552, 1559)),
    244: tuple(range(1559, 1566)),
    250: tuple(range(1566, 1573)),
    256: tuple(range(1573, 1580)),
    262: tuple(range(1580, 1587)),
    268: tuple(range(1587, 1594)),
    274: tuple(range(1594, 1597)),
}
RECORD_TO_ROOT = {
    record_id: root
    for root, record_ids in ROOT_TERMINALS.items()
    for record_id in record_ids
}
ASSEMBLY_CLASS = {
    214: "standalone_exclamatory_prefix",
    220: "speaker_register_humble_predicate",
    226: "speaker_register_thought_predicate",
    232: "speaker_register_interjection",
    238: "polymorphic_copular_question",
    244: "polymorphic_bound_final_particle",
    250: "polymorphic_bound_agreement_or_question",
    256: "polymorphic_bound_dubitative_question",
    262: "pk_observed_bound_exclamation_or_question",
    268: "polymorphic_copular_or_predicative_question",
    274: "bound_contrastive_connective",
}

LEFT_ROOT214_FULL_IDS = tuple(range(1524, 1531))
LEFT_ROOT214_FULL_JP = (
    "あら",
    "おお",
    "まあ",
    "ふむ",
    "あら",
    "おお",
    "なんと",
)
LEFT_ROOT214_FULL_CURRENT = (
    "어머",
    "오오",
    "뭐",
    "흠",
    "어머",
    "오오",
    "이럴 수가",
)
LEFT_ROOT214_FULL_POLICY = (
    "어머",
    "오오",
    "어머나",
    "흠",
    "어머",
    "오오",
    "이런",
)

RIGHT_ROOT274_FULL_IDS = tuple(range(1594, 1601))
RIGHT_ROOT274_FULL_JP = (
    "けれど",
    "が",
    "けれども",
    "が",
    "けれども",
    "が",
    "が",
)
RIGHT_ROOT274_FULL_CURRENT = (
    "하지만",
    "이",
    "하지만",
    "이",
    "하지만",
    "이",
    "이",
)
RIGHT_ROOT274_FULL_POLICY = ("지만",) * 7

EXPECTED_GRAPH_CLOSURES = {
    214: tuple(range(214, 220)) + LEFT_ROOT214_FULL_IDS,
    220: tuple(range(220, 226)) + tuple(range(1531, 1538)),
    226: tuple(range(226, 232)) + tuple(range(1538, 1545)),
    232: tuple(range(232, 238)) + tuple(range(1545, 1552)),
    237: (237, 1549, 1550),
    238: tuple(range(238, 244)) + tuple(range(1552, 1559)),
    244: tuple(range(244, 250)) + tuple(range(1559, 1566)),
    250: tuple(range(250, 256)) + tuple(range(1566, 1573)),
    256: tuple(range(256, 262)) + tuple(range(1573, 1580)),
    262: tuple(range(262, 268)) + tuple(range(1580, 1587)),
    268: tuple(range(268, 274)) + tuple(range(1587, 1594)),
    274: tuple(range(274, 280)) + RIGHT_ROOT274_FULL_IDS,
}

PK_ARCHIVE_DIGESTS = {
    "pk_jp": "E5F626F73918E93325BD6319075A3C0E39CB4B312495D12F7BFF0D4954AA5886",
    "pk_current": "A6C0C6B78A0EE936C747D547E4CDA05D595D8FD42A6BCAD449D663E4B6EC2B8B",
    "pk_sc": "68B0DA2704050C12D6612B362944B60B75915F84134E95A725382AF2453C0456",
    "pk_tc": "68B0DA2704050C12D6612B362944B60B75915F84134E95A725382AF2453C0456",
    "pk_en": "68B0DA2704050C12D6612B362944B60B75915F84134E95A725382AF2453C0456",
}
EXPECTED_INCOMING_JUMP_EVIDENCE = (
    67,
    "8BD5C24A91C80D32B11CF28DE7727BBACAAE2464A4078C7402C6C6D69710FE00",
)
EXPECTED_REVERSE_MAP_SHA256 = (
    "377C80769FD10D4E08F8B7823A569CC68818C1740F0AFC7A27BB81D08E334CCE"
)
EMPTY_EVIDENCE_SHA256 = (
    "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
)
EXPECTED_CALL_EVIDENCE = {
    214: (
        (21, "8684DA9196E3138BDBBA26EBC13B53090F858E10AA56838C757A8617AC7AE4E8", 0, EMPTY_EVIDENCE_SHA256),
        (21, "8684DA9196E3138BDBBA26EBC13B53090F858E10AA56838C757A8617AC7AE4E8", 0, EMPTY_EVIDENCE_SHA256),
        (0, EMPTY_EVIDENCE_SHA256, 0, EMPTY_EVIDENCE_SHA256),
    ),
    220: (
        (2, "C8D0B97FEF8230351F34015EEDCB2AC23FA0C2E48EDAF7E2035DF1CD6275621F", 1, "BD8E6A1C7B85DFC440803FC18AE321926BDD3CD07472F56695475771C6246076"),
        (2, "C8D0B97FEF8230351F34015EEDCB2AC23FA0C2E48EDAF7E2035DF1CD6275621F", 1, "BD8E6A1C7B85DFC440803FC18AE321926BDD3CD07472F56695475771C6246076"),
        (0, EMPTY_EVIDENCE_SHA256, 0, EMPTY_EVIDENCE_SHA256),
    ),
    226: (
        (75, "D4340DEB0C096F9BBACA9AE7975ABC43BF559A088BA6B43C5348752752EB493A", 5, "3BB66271422D40955FF757A5D6028A2216CF07CFF5C141F8AEB470110EEFE8AA"),
        (70, "FAE1C3421487157897DD30CD7B08C37C02C1CE94D8746365FFDF45AC1B5D1E06", 5, "3BB66271422D40955FF757A5D6028A2216CF07CFF5C141F8AEB470110EEFE8AA"),
        (5, "675F070849944F61EE8FB8075FBDD2A0BE5272C42E3F97C06D0C8940E1983332", 0, EMPTY_EVIDENCE_SHA256),
    ),
    232: (
        (5, "9B7B3CAB7CC98B18EC624EBCDBF97E35488F92D15E23BF59CFD92819C3060E2B", 0, EMPTY_EVIDENCE_SHA256),
        (5, "9B7B3CAB7CC98B18EC624EBCDBF97E35488F92D15E23BF59CFD92819C3060E2B", 0, EMPTY_EVIDENCE_SHA256),
        (0, EMPTY_EVIDENCE_SHA256, 0, EMPTY_EVIDENCE_SHA256),
    ),
    237: (
        (1, "E5DFDFF32C23E913B300E2D8462F679A2641B0D54EFCBB5B0C79F6FC3868C46E", 0, EMPTY_EVIDENCE_SHA256),
        (1, "E5DFDFF32C23E913B300E2D8462F679A2641B0D54EFCBB5B0C79F6FC3868C46E", 0, EMPTY_EVIDENCE_SHA256),
        (0, EMPTY_EVIDENCE_SHA256, 0, EMPTY_EVIDENCE_SHA256),
    ),
    238: (
        (28, "AF0DF29F88C7DAF5C834D5E3E8B2AA7C130DB584B1965C9C2E8E4F66B504DC41", 0, EMPTY_EVIDENCE_SHA256),
        (27, "A504F0CE94D9FBCA491F3A1B4220AE249E3101A8F8BCEBDD44297F54B5887CCA", 0, EMPTY_EVIDENCE_SHA256),
        (1, "C1E773D4BFAA166AD8F75B3118A1E44F35B60CF52E3074D1EE8E791724069D00", 0, EMPTY_EVIDENCE_SHA256),
    ),
    244: (
        (2, "3E20D9B1CA9ABE80E3C1C215654C881D051C8AD4850E53E2632BA0AEBAFAD08D", 0, EMPTY_EVIDENCE_SHA256),
        (2, "3E20D9B1CA9ABE80E3C1C215654C881D051C8AD4850E53E2632BA0AEBAFAD08D", 0, EMPTY_EVIDENCE_SHA256),
        (0, EMPTY_EVIDENCE_SHA256, 0, EMPTY_EVIDENCE_SHA256),
    ),
    250: (
        (5, "0564DA5F7FC0C5218F8428F5DD61F89C9972DCEDB4263FA6CBA5AB1EF4B07EDC", 0, EMPTY_EVIDENCE_SHA256),
        (5, "0564DA5F7FC0C5218F8428F5DD61F89C9972DCEDB4263FA6CBA5AB1EF4B07EDC", 0, EMPTY_EVIDENCE_SHA256),
        (0, EMPTY_EVIDENCE_SHA256, 0, EMPTY_EVIDENCE_SHA256),
    ),
    256: (
        (14, "4934CA7A7674EC271FA97FBD127253F148AFB88E8F741587347AD40BF2670B2C", 0, EMPTY_EVIDENCE_SHA256),
        (12, "769F5E05517150A39627ADB459B43C0487716F574E0ED07A23FC869DA78A7B11", 0, EMPTY_EVIDENCE_SHA256),
        (2, "F9EF8094D887CF125006555522AF46602FCA60A29515E41E8FD0B7B096E1AB9A", 0, EMPTY_EVIDENCE_SHA256),
    ),
    262: (
        (1, "A15F2711FEE9B6BA7E933ECEE1E4CA1A8C4B33713AC85A6E1D5CE88E692BFEFA", 0, EMPTY_EVIDENCE_SHA256),
        (1, "A15F2711FEE9B6BA7E933ECEE1E4CA1A8C4B33713AC85A6E1D5CE88E692BFEFA", 0, EMPTY_EVIDENCE_SHA256),
        (0, EMPTY_EVIDENCE_SHA256, 0, EMPTY_EVIDENCE_SHA256),
    ),
    268: (
        (27, "4364407B239B9FCF777220B710198D21623D7FA9D9CA7884E45DD91EE812CABC", 1, "70073E33D1CEECD7D5E230603CA4346A7C3CA6DB975B9F16F6AF2E8ED7D76A82"),
        (26, "7023DBFDCB6A4780A8E40A582D6C6DCB72B186AB2DFF38E3A2FD15BC088FC79E", 7, "CC366ADBBE174255E9FECC77EA857E2B8264407CCFD1EBA763B6D907A5863394"),
        (1, "0EE28BA03F22241E0836568C80E92B5D40BFF889D45CF689340E3ECAC4AB7DB7", 0, EMPTY_EVIDENCE_SHA256),
    ),
    274: (
        (17, "EAA2FE1327B8A1CCE10583581FCFB89DE2C19A3ED626E13F27CCDCF1944C2CD8", 3, "E28EC78ED94BF701004206E29A204D027550E9B56CAD507DCFA9C40934C8E5D0"),
        (17, "EAA2FE1327B8A1CCE10583581FCFB89DE2C19A3ED626E13F27CCDCF1944C2CD8", 3, "E28EC78ED94BF701004206E29A204D027550E9B56CAD507DCFA9C40934C8E5D0"),
        (0, EMPTY_EVIDENCE_SHA256, 0, EMPTY_EVIDENCE_SHA256),
    ),
}
EXPECTED_CHANGED_LITERAL_COUNT = 36

BASIS = (
    "review_queue_pk_msggame_B002_S1028_pristine_pk_pc_jp_sole_"
    "translation_authority_block0_runtime_terminal_records1530_1596_"
    "exact_pk_source_current_sc_tc_en_subset_digests_unique_contiguous_"
    "Base_reverse_search_without_offset_assumption_and_exact_jp_current_"
    "sc_tc_record_byte_equivalence_only_then_base_semantic_policy_aid_"
    "actual_pk_source_current_014a_graph_full_closures_0143_caller_"
    "fixed_following_and_flatten_digests_pk_extra_direct_root237_"
    "left_root214_and_right_root274_cross_segment_full_seven_source_"
    "current_policy_matrices_runtime_fragments_pending_no_korean_build_"
    "authority"
)


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return tuple(
        literal.text for literal in ENGINE.parse_record_literals(records[key])
    )


def gap_bytes(record: Any) -> tuple[bytes, ...]:
    return SUPPORT.record_gaps(record)


def archive_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    return BASE.archive_records(prepared)


def assert_queue_slice() -> None:
    rows = [
        json.loads(line)
        for line in QUEUE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    batch_targets = [
        target
        for row in rows
        if row.get("batch_id") == QUEUE_BATCH_ID
        for target in row["target_literals"]
    ]
    visible_coordinates = [
        target["coordinate"]
        for target in batch_targets
        if target.get("visible")
    ]
    expected = [f"0:{record_id}:0" for record_id in RECORD_IDS]
    expected_set = set(expected)
    if (
        len(visible_coordinates) != 200
        or visible_coordinates[
            QUEUE_ZERO_BASED_START:QUEUE_ZERO_BASED_STOP
        ]
        != expected
        or any(
            target["coordinate"] in expected_set
            and not target.get("visible")
            for target in batch_targets
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} private queue slice drifted")


def discover_base_mapping(
    base_jp: dict[tuple[int, int], Any],
    pk_jp: dict[tuple[int, int], Any],
) -> dict[tuple[int, int], tuple[int, int]]:
    block_zero_ids = sorted(
        record_id
        for block_id, record_id in base_jp
        if block_id == BLOCK_ID
    )
    candidates: list[int] = []
    for start in block_zero_ids:
        base_ids = tuple(range(start, start + len(RECORD_IDS)))
        if any((BLOCK_ID, record_id) not in base_jp for record_id in base_ids):
            continue
        if all(
            literal_texts(pk_jp, (BLOCK_ID, pk_record_id))
            == literal_texts(base_jp, (BLOCK_ID, base_record_id))
            and gap_bytes(pk_jp[(BLOCK_ID, pk_record_id)])
            == gap_bytes(base_jp[(BLOCK_ID, base_record_id)])
            for pk_record_id, base_record_id in zip(
                RECORD_IDS,
                base_ids,
                strict=True,
            )
        ):
            candidates.append(start)
    if candidates != [1476]:
        raise RuntimeError(
            f"segment {SEGMENT} Base reverse search is not unique: "
            f"{candidates}"
        )
    mapping = {
        (BLOCK_ID, pk_record_id): (
            BLOCK_ID,
            candidates[0] + ordinal,
        )
        for ordinal, pk_record_id in enumerate(RECORD_IDS)
    }
    mapping_sha256 = SUPPORT.canonical_sha256(
        [
            [pk_key[1], base_key[1]]
            for pk_key, base_key in mapping.items()
        ]
    )
    if mapping_sha256 != EXPECTED_REVERSE_MAP_SHA256:
        raise RuntimeError(f"segment {SEGMENT} reverse map drifted")
    return mapping


def assert_source_and_mapping(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[tuple[int, int], tuple[int, int]]:
    for label, expected_digest in PK_ARCHIVE_DIGESTS.items():
        actual = GENERAL.subset_digest(
            records_by_label[label],
            RECORD_KEYS,
        )
        if actual != expected_digest:
            raise RuntimeError(
                f"segment {SEGMENT} {label} corpus drifted"
            )

    for ordinal, record_id in enumerate(RECORD_IDS):
        key = (BLOCK_ID, record_id)
        for label in PK_ARCHIVE_DIGESTS:
            if (
                len(literal_texts(records_by_label[label], key)) != 1
                or gap_bytes(records_by_label[label][key])
                != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} PK record/gap drifted: "
                    f"{label}/{key}"
                )
        if literal_texts(records_by_label["pk_jp"], key) != (
            EXPECTED_PK_JP[ordinal],
        ):
            raise RuntimeError(
                f"segment {SEGMENT} pristine PK source drifted: {key}"
            )
        for label in ("pk_sc", "pk_tc", "pk_en"):
            if literal_texts(records_by_label[label], key) != ("",):
                raise RuntimeError(
                    f"segment {SEGMENT} blank context drifted: "
                    f"{label}/{key}"
                )

    discovered_mapping = discover_base_mapping(
        records_by_label["base_jp"],
        records_by_label["pk_jp"],
    )
    if discovered_mapping != BASE_RECORD_MAP:
        raise RuntimeError(f"segment {SEGMENT} discovered Base map drifted")

    for pk_key, base_key in discovered_mapping.items():
        for language in ("jp", "current", "sc", "tc"):
            if (
                records_by_label[f"pk_{language}"][pk_key].data
                != records_by_label[f"base_{language}"][base_key].data
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base/PK {language} mapping "
                    f"drifted: {base_key}/{pk_key}"
                )

    # Base is an auxiliary translation-policy cross-check only after the
    # pristine PK corpus and independently discovered mapping have passed.
    BASE.assert_corpora(records_by_label)
    base_translations = {
        f"0:{record_id - 54}:0": translation
        for record_id, translation in TRANSLATIONS_BY_RECORD.items()
    }
    BASE.assert_semantics(base_translations)
    if any(
        BASE.TRANSLATIONS_BY_RECORD[record_id - 54] != translation
        for record_id, translation in TRANSLATIONS_BY_RECORD.items()
    ):
        raise RuntimeError(
            f"segment {SEGMENT} auxiliary Base policy diverged"
        )
    return discovered_mapping


def assert_runtime_graph(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    BASE.assert_jump_and_call_graphs(records_by_label)
    BASE.assert_014c_false_positive_guard(records_by_label)

    target_ids = set(RECORD_IDS)
    for label in ("pk_jp", "pk_current"):
        records = records_by_label[label]
        jump_rows = BASE.incoming_jump_rows(records, target_ids)
        actual_jump_evidence = (
            len(jump_rows),
            SUPPORT.canonical_sha256(jump_rows),
        )
        if (
            actual_jump_evidence != EXPECTED_INCOMING_JUMP_EVIDENCE
            or {row[4] for row in jump_rows} != target_ids
            or any(
                sum(row[4] == target for row in jump_rows) != 1
                for target in target_ids
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} incoming 014A drifted"
            )

        edges = SUPPORT.graph_edges(records)
        for root, expected_closure in EXPECTED_GRAPH_CLOSURES.items():
            actual_closure = tuple(
                sorted(SUPPORT.graph_closure(edges, root))
            )
            if actual_closure != expected_closure:
                raise RuntimeError(
                    f"segment {SEGMENT} {label} full closure drifted: "
                    f"{root}"
                )

    source_records = records_by_label["pk_jp"]
    current_records = records_by_label["pk_current"]
    for root, expected_evidence in EXPECTED_CALL_EVIDENCE.items():
        source_calls = SUPPORT.root_call_sites(source_records, root)
        current_calls = SUPPORT.root_call_sites(current_records, root)
        source_fixed = SUPPORT.fixed_following_blockers(
            source_records,
            root,
        )
        current_fixed = SUPPORT.fixed_following_blockers(
            current_records,
            root,
        )
        source_only = tuple(sorted(set(source_calls) - set(current_calls)))
        current_only = tuple(sorted(set(current_calls) - set(source_calls)))
        actual_evidence = (
            (
                len(source_calls),
                SUPPORT.canonical_sha256(source_calls),
                len(source_fixed),
                SUPPORT.canonical_sha256(source_fixed),
            ),
            (
                len(current_calls),
                SUPPORT.canonical_sha256(current_calls),
                len(current_fixed),
                SUPPORT.canonical_sha256(current_fixed),
            ),
            (
                len(source_only),
                SUPPORT.canonical_sha256(source_only),
                len(current_only),
                SUPPORT.canonical_sha256(current_only),
            ),
        )
        if actual_evidence != expected_evidence:
            raise RuntimeError(
                f"segment {SEGMENT} PK root {root} "
                "caller/fixed/flatten evidence drifted"
            )


def assert_boundaries(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    for side, record_ids, expected_jp, expected_current in (
        (
            "left",
            LEFT_ROOT214_FULL_IDS,
            LEFT_ROOT214_FULL_JP,
            LEFT_ROOT214_FULL_CURRENT,
        ),
        (
            "right",
            RIGHT_ROOT274_FULL_IDS,
            RIGHT_ROOT274_FULL_JP,
            RIGHT_ROOT274_FULL_CURRENT,
        ),
    ):
        actual_jp = tuple(
            literal_texts(source, (BLOCK_ID, record_id))[0]
            for record_id in record_ids
        )
        actual_current = tuple(
            literal_texts(current, (BLOCK_ID, record_id))[0]
            for record_id in record_ids
        )
        if actual_jp != expected_jp or actual_current != expected_current:
            raise RuntimeError(
                f"segment {SEGMENT} {side} full boundary drifted"
            )

    if (
        LEFT_ROOT214_FULL_IDS != LEFT_PK.RIGHT_ROOT214_FULL_IDS
        or LEFT_ROOT214_FULL_JP != LEFT_PK.RIGHT_ROOT214_FULL_JP
        or LEFT_ROOT214_FULL_CURRENT
        != LEFT_PK.RIGHT_ROOT214_FULL_CURRENT
        or LEFT_ROOT214_FULL_POLICY
        != LEFT_PK.RIGHT_ROOT214_FULL_POLICY
    ):
        raise RuntimeError(
            f"segment {SEGMENT} S1027/S1028 root214 policy diverged"
        )

    if (
        RIGHT_ROOT274_FULL_IDS != RIGHT_PK.LEFT_BOUNDARY_IDS
        or RIGHT_ROOT274_FULL_JP != RIGHT_PK.LEFT_BOUNDARY_JP
        or RIGHT_ROOT274_FULL_CURRENT != RIGHT_PK.LEFT_BOUNDARY_CURRENT
        or RIGHT_ROOT274_FULL_POLICY != RIGHT_PK.LEFT_BOUNDARY_POLICY
    ):
        raise RuntimeError(
            f"segment {SEGMENT} S1028/S1029 root274 policy diverged"
        )

    base_right_policy = tuple(
        BASE.TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(1540, 1543)
    ) + tuple(
        RIGHT_BASE.TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(1543, 1547)
    )
    if (
        base_right_policy != RIGHT_ROOT274_FULL_POLICY
        or TRANSLATIONS_BY_RECORD[1530]
        != LEFT_ROOT214_FULL_POLICY[-1]
        or tuple(
            TRANSLATIONS_BY_RECORD[record_id]
            for record_id in range(1594, 1597)
        )
        != RIGHT_ROOT274_FULL_POLICY[:3]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} owned boundary policy drifted"
        )


def assert_pk_overlay_roundtrip(
    prepared: Any,
    translations: dict[str, str],
) -> str:
    pk = prepared.resources["pk_msggame"]
    current_records = ENGINE.archive_records(pk.current_archive)
    replacements: dict[tuple[int, int, int], str] = {}
    reverse: dict[tuple[int, int, int], str] = {}
    for coordinate, translation in translations.items():
        key = tuple(int(value) for value in coordinate.split(":"))
        replacements[key] = translation
        reverse[key] = ENGINE.parse_record_literals(
            current_records[key[:2]]
        )[key[2]].text
    rebuilt = ENGINE.rebuild_packed_with_literals(
        pk.current_blob,
        replacements,
    )
    rebuilt_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(rebuilt).archive
    )
    if (
        len(current_records) != PK_RECORD_COUNT
        or len(rebuilt_records) != PK_RECORD_COUNT
    ):
        raise RuntimeError(f"segment {SEGMENT} PK record count drifted")
    target_records = set(RECORD_KEYS)
    for key, current_record in current_records.items():
        if (
            key not in target_records
            and rebuilt_records[key].data != current_record.data
        ):
            raise RuntimeError(
                f"segment {SEGMENT} changed an out-of-scope PK record: "
                f"{key}"
            )
    for key in target_records:
        if gap_bytes(rebuilt_records[key]) != gap_bytes(current_records[key]):
            raise RuntimeError(
                f"segment {SEGMENT} changed PK runtime skeleton: {key}"
            )
    for key, translation in replacements.items():
        actual = ENGINE.parse_record_literals(rebuilt_records[key[:2]])[
            key[2]
        ].text
        if actual != translation:
            raise RuntimeError(
                f"segment {SEGMENT} PK UTF-16 round-trip failed: {key}"
            )
    reversed_blob = ENGINE.rebuild_packed_with_literals(rebuilt, reverse)
    if reversed_blob != pk.current_blob:
        raise RuntimeError(
            f"segment {SEGMENT} PK reverse overlay is not byte-exact"
        )
    return hashlib.sha256(rebuilt).hexdigest().upper()


def assert_semantics(translations: dict[str, str]) -> None:
    if (
        len(RECORD_IDS) != 67
        or len(EXPECTED_PK_JP) != 67
        or len(TRANSLATION_POLICY) != 67
        or set(ROOT_TERMINALS)
        != {214, 220, 226, 232, 238, 244, 250, 256, 262, 268, 274}
        or set(RECORD_TO_ROOT) != set(RECORD_IDS)
        or translations != TRANSLATIONS
    ):
        raise RuntimeError(f"segment {SEGMENT} decision universe drifted")
    if TRANSLATIONS_BY_RECORD[1530] != "이런":
        raise RuntimeError("exclamatory なんと meaning drifted")
    if tuple(
        TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(1531, 1538)
    ) != (
        "황송합니다",
        "황송하다",
        "황송합니다",
        "황송하옵니다",
        "황송합니다",
        "황송합니다",
        "황송하다",
    ):
        raise RuntimeError("恐れ入る register matrix drifted")
    if tuple(
        TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(1538, 1545)
    ) != (
        "생각합니다",
        "생각한다",
        "생각하옵니다",
        "생각하옵니다",
        "생각하옵니다",
        "생각하오",
        "생각하오",
    ):
        raise RuntimeError("思う/存ずる register matrix drifted")
    if tuple(
        TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(1545, 1552)
    ) != ("어머", "어라", "어머나", "아니", "어머", "흠", "으음"):
        raise RuntimeError("interjection register matrix drifted")
    if tuple(
        TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(1580, 1587)
    ) != ("다니", "나", "다니", "나", "네", "나", "나"):
        raise RuntimeError("PK-observed bound exclamation matrix drifted")
    if any(
        TRANSLATIONS_BY_RECORD[record_id] != "지만"
        for record_id in range(1594, 1597)
    ):
        raise RuntimeError("bound contrastive matrix drifted")
    for left, right in (
        (1552, 1587),
        (1553, 1588),
        (1556, 1589),
        (1556, 1590),
        (1556, 1591),
        (1557, 1592),
        (1558, 1593),
    ):
        if TRANSLATIONS_BY_RECORD[left] != TRANSLATIONS_BY_RECORD[right]:
            raise RuntimeError(
                f"question-ending exact reuse drifted: {left}/{right}"
            )


def build_rows() -> tuple[
    Any,
    dict[str, str],
    list[dict[str, object]],
    str,
]:
    assert_queue_slice()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    records_by_label = archive_records(prepared)
    discovered_mapping = assert_source_and_mapping(records_by_label)
    assert_runtime_graph(records_by_label)
    assert_boundaries(records_by_label)
    translations = dict(TRANSLATIONS)
    current = records_by_label["pk_current"]
    for coordinate, translation in translations.items():
        _, record_id, _ = (int(value) for value in coordinate.split(":"))
        current_text = literal_texts(
            current,
            (BLOCK_ID, record_id),
        )[0]
        if (
            not ENGINE.is_visible_translation_candidate(current_text)
            or "\n" in current_text
            or current_text != current_text.strip()
            or "\n" in translation
            or translation != translation.strip()
            or UTIL.layout_signature(translation)
            != UTIL.layout_signature(current_text)
            or "\r" in translation
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} line/signature drifted: {coordinate}"
            )
    assert_semantics(translations)
    candidate_sha256 = assert_pk_overlay_roundtrip(
        prepared,
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
        full_terminal_ids = (
            LEFT_ROOT214_FULL_IDS
            if root == 214
            else RIGHT_ROOT274_FULL_IDS
            if root == 274
            else ROOT_TERMINALS[root]
        )
        evidence: dict[str, object] = {
            "pk_root": root,
            "full_terminal_record_ids": list(full_terminal_ids),
            "full_graph_closure_record_ids": list(
                EXPECTED_GRAPH_CLOSURES[root]
            ),
            "base_semantic_record_discovered_by_reverse_search": (
                discovered_mapping[(block_id, record_id)][1]
            ),
            "incoming_014a_guarded": True,
            "valid_incoming_014c_count": 0,
            "source_call_count": EXPECTED_CALL_EVIDENCE[root][0][0],
            "current_call_count": EXPECTED_CALL_EVIDENCE[root][1][0],
            "source_fixed_following_count": (
                EXPECTED_CALL_EVIDENCE[root][0][2]
            ),
            "current_fixed_following_count": (
                EXPECTED_CALL_EVIDENCE[root][1][2]
            ),
            "source_calls_flattened_in_current": (
                EXPECTED_CALL_EVIDENCE[root][2][0]
            ),
            "current_only_calls": EXPECTED_CALL_EVIDENCE[root][2][2],
            "assembly_class": ASSEMBLY_CLASS[root],
            "automatic_space_inserted": False,
            "caller_rewrite_required_before_runtime_approval": True,
            "runtime_integration_required": True,
        }
        if record_id in (1549, 1550):
            evidence["pk_additional_direct_root"] = 237
            evidence["pk_additional_direct_root_call_count"] = (
                EXPECTED_CALL_EVIDENCE[237][0][0]
            )
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
                "runtime_assembly_evidence": evidence,
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
            }
        )
    return prepared, translations, rows, candidate_sha256


def main() -> int:
    first = build_rows()
    second = build_rows()
    prepared, translations, rows, candidate_sha256 = first
    if (
        translations != second[1]
        or ENGINE.jsonl(rows) != ENGINE.jsonl(second[2])
        or candidate_sha256 != second[3]
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
        raise RuntimeError(f"segment {SEGMENT} validation count drifted")

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
            f"segment {SEGMENT} changed count drifted: {changed}"
        )

    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B002_S1028",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [67, 133],
                "source_literal_count": 67,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "confirmed_non_display": 0,
                "changed_literal_count": changed,
                "base_mapping_method": (
                    "unique_contiguous_reverse_search_exact_literal_gap"
                ),
                "discovered_base_record_range": [1476, 1542],
                "discovered_pk_minus_base_offset": 54,
                "base_reverse_map_sha256": EXPECTED_REVERSE_MAP_SHA256,
                "pk_base_jp_sc_tc_current_record_divergence_records": [],
                "pk_en_visible_records": [],
                "incoming_014a_evidence": list(
                    EXPECTED_INCOMING_JUMP_EVIDENCE
                ),
                "root_source_call_counts": {
                    str(root): evidence[0][0]
                    for root, evidence in EXPECTED_CALL_EVIDENCE.items()
                },
                "root_current_call_counts": {
                    str(root): evidence[1][0]
                    for root, evidence in EXPECTED_CALL_EVIDENCE.items()
                },
                "root_source_fixed_following_counts": {
                    str(root): evidence[0][2]
                    for root, evidence in EXPECTED_CALL_EVIDENCE.items()
                },
                "root_current_fixed_following_counts": {
                    str(root): evidence[1][2]
                    for root, evidence in EXPECTED_CALL_EVIDENCE.items()
                },
                "root_source_calls_flattened_in_current": {
                    str(root): evidence[2][0]
                    for root, evidence in EXPECTED_CALL_EVIDENCE.items()
                },
                "pk_additional_direct_root237_records": [1549, 1550],
                "left_root214_full_policy": list(
                    LEFT_ROOT214_FULL_POLICY
                ),
                "right_root274_full_policy": list(
                    RIGHT_ROOT274_FULL_POLICY
                ),
                "candidate_sha256": candidate_sha256,
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
                "target_source_current_records_and_gaps_exact": True,
                "target_runtime_skeleton_exact": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "s1027_boundary_cross_assert_exact": True,
                "s1029_boundary_cross_assert_exact": True,
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
