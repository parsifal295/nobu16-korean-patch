#!/usr/bin/env python3
"""Build PK block-0 runtime-terminal segment 1027 decisions."""

from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch002_segment1006 as BASE
import build_base_batch002_segment1007 as RIGHT_BASE
import build_pk_batch001_segment1025 as AUDIT
import build_pk_batch001_segment1026 as LEFT


ENGINE = BASE.ENGINE
GENERAL = BASE.GENERAL
UTIL = BASE.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B002_S1027.private.v1.jsonl"
)
QUEUE_PATH = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "review_queue.private.v1.jsonl"
)
SEGMENT = 1027
BLOCK_ID = 0
QUEUE_BATCH_ID = "pk_msggame-B002"
QUEUE_ZERO_BASED_START = 0
QUEUE_ZERO_BASED_STOP = 67
BASE_RECORD_IDS = tuple(range(1409, 1476))
RECORD_IDS = tuple(range(1463, 1530))
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
BASE_RECORD_MAP = {
    (BLOCK_ID, record_id): (BLOCK_ID, record_id - 54)
    for record_id in RECORD_IDS
}
PK_SOURCE_DIVERGENCE_BASE_IDS = BASE.BASE_PK_LITERAL_DIVERGENCES["jp"]
PK_CURRENT_DIVERGENCE_BASE_IDS = BASE.BASE_PK_LITERAL_DIVERGENCES[
    "current"
]
APPROVED_SOURCE_EQUIVALENCES = {
    base_record_id + 54: (
        BASE.EXPECTED_BASE_JP[base_record_id],
        BASE.EXPECTED_PK_JP[base_record_id],
    )
    for base_record_id in PK_SOURCE_DIVERGENCE_BASE_IDS
}
PK_TRANSLATION_OVERRIDES = {
    1474: "아니",
    1505: "으시오",
}
TRANSLATIONS_BY_RECORD = {
    base_record_id + 54: BASE.TRANSLATIONS_BY_RECORD[base_record_id]
    for base_record_id in BASE_RECORD_IDS
}
TRANSLATIONS_BY_RECORD.update(PK_TRANSLATION_OVERRIDES)
RAW_TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}
PK_RECORD_COUNT = 21751
EXPECTED_CHANGED_LITERAL_COUNT = 51
EXPECTED_REVERSE_MAP_SHA256 = (
    "BC6ECAD3CF169710A8B9D9C153E5197DE4655B41CF9EB1FA01AF5838FB8EF4BD"
)
EXPECTED_TARGET_INCOMING_EVIDENCE = (
    67,
    "F2310F21C6419BABEF88352367FF98E7BAC27976A5015FBB3E3F68BE2C4752AD",
)
FULL_TERMINAL_GROUPS = {
    root: tuple(record_id + 54 for record_id in record_ids)
    for root, record_ids in BASE.TERMINAL_GROUPS.items()
}
RECORD_TO_ROOT = {
    record_id: root
    for root, record_ids in FULL_TERMINAL_GROUPS.items()
    for record_id in record_ids
    if record_id in RECORD_IDS
}
EXPECTED_FIXED_EVIDENCE = {
    "pk_jp": {
        160: (9, "54E280983B7A1D48949B9359EAFA639EB09A8F1B624FF698DC18EDA26C50FB3C"),
        166: (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"),
        172: (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"),
        178: (30, "A572418DA2A97E7C98EDDF09943EF45ED86C27A75E83A8B83EBEFD624C5472FF"),
        184: (8, "0373E5646B920D0935659AAA99E8E45D96E4FF43DA70CDBF838732C6798A1385"),
        190: (6, "C91AE7702B845392A3CAD808699597ACA8976B5AEE800DEFBF5ECDAC97466CCC"),
        196: (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"),
        202: (3, "240FC078E967EA48CAB4555993C347CC8291816B8374387926772B076BB6A7DE"),
        208: (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"),
        214: (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"),
    },
    "pk_current": {
        160: (9, "54E280983B7A1D48949B9359EAFA639EB09A8F1B624FF698DC18EDA26C50FB3C"),
        166: (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"),
        172: (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"),
        178: (28, "9A71917B273B314E750C9BF83C239980757E525B0735D72C3B3E35E546A6A546"),
        184: (7, "6AFEEC1B78670E928E7C42374203590DF8DF1B4247165E0C8DE2A7162D4C0A15"),
        190: (5, "366EAB60F1FFB0433409CE2A1FE349CFBB31F4E8B9DB238050C0A5603ED72FF3"),
        196: (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"),
        202: (2, "04C51A713C8A7DC517E34D7B932C28DEF017CC74B088EB32B24FA55C73123270"),
        208: (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"),
        214: (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"),
    },
}
EXPECTED_SOURCE_ONLY_FLATTENED = {
    160: (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"),
    166: (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"),
    172: (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"),
    178: (10, "3C492FB468C8F4690051BA15B761B0494E9F909D7D5A03076B4F45792BA24643"),
    184: (1, "87F55F65AE82427EF07398764BFE2444310F3D471A46D47BDA6F1159D31FC854"),
    190: (3, "2293147A580F06C1BFC4500DEFA8E73EAA93530756FEAE7AF4E65013103871A3"),
    196: (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"),
    202: (2, "6FC375F7775546979D3D045815882716057EC9883256388284C1B41808FE01D2"),
    208: (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"),
    214: (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"),
}
RIGHT_BOUNDARY_INCOMING = (
    (0, 211, 0, 83, 1523),
    (0, 215, 0, 6, 1524),
    (0, 215, 0, 18, 1525),
    (0, 217, 0, 83, 1530),
    (0, 218, 0, 6, 1526),
    (0, 218, 0, 18, 1527),
    (0, 219, 0, 6, 1528),
    (0, 219, 0, 18, 1529),
)
LEFT_ROOT160_FULL_IDS = LEFT.RIGHT_BOUNDARY_IDS
LEFT_ROOT160_FULL_JP = LEFT.RIGHT_BOUNDARY_JP
LEFT_ROOT160_FULL_CURRENT = LEFT.RIGHT_BOUNDARY_CURRENT
LEFT_ROOT160_FULL_POLICY = LEFT.RIGHT_BOUNDARY_POLICY
RIGHT_ROOT214_FULL_IDS = tuple(range(1524, 1531))
RIGHT_ROOT214_FULL_JP = tuple(
    BASE.EXPECTED_PK_JP[record_id]
    for record_id in range(1470, 1476)
) + (RIGHT_BASE.EXPECTED_JP[1476],)
RIGHT_ROOT214_FULL_CURRENT = (
    "어머",
    "오오",
    "뭐",
    "흠",
    "어머",
    "오오",
    "이럴 수가",
)
RIGHT_ROOT214_FULL_POLICY = tuple(
    BASE.TRANSLATIONS_BY_RECORD[record_id]
    for record_id in range(1470, 1476)
) + (RIGHT_BASE.TRANSLATIONS_BY_RECORD[1476],)
ROOT_ASSEMBLY_PLAN = {
    160: "caller-specific predicate stem + negative progressive ending",
    166: "speaker-register denial response",
    172: "reduplicated speaker-register denial response",
    178: "caller predicate stem + existential/progressive ending",
    184: "caller predicate stem + attributive existential ending",
    190: "caller action stem + speech-register ending",
    196: "caller action stem + imperative ending",
    202: "caller verb stem + volitional ending",
    208: "speaker-register acknowledgement/interjection",
    214: (
        "speaker-register interjection with cross-segment standalone "
        "exclamatory branch"
    ),
}
BASIS = (
    "review_queue_pk_msggame_B002_pristine_pk_pc_jp_sole_authority_"
    "block0_runtime_voice_terminal_records1463_1529_all_visible_literal0_"
    "independent_exact_minus54_Base_reverse_search_with_four_explicit_"
    "pk_source_equivalences_and_two_pk_specific_translation_overrides_"
    "base_sc_tc_pk_sc_tc_en_context_only_actual_pk_014A_closure_0143_"
    "caller_fixed_following_source_current_flatten_and_014C_false_"
    "positive_evidence_left_S1026_root160_and_right_S1028_root214_full_"
    "cross_segment_policies_negative_denial_existential_attributive_"
    "action_imperative_volitional_acknowledgement_interjection_"
    "semantics_one_line_skeleton_runtime_fragment_pending_no_korean_"
    "build_authority"
)


def literal_texts(
    records: dict[tuple[int, int], Any],
    record_id: int,
) -> tuple[str, ...]:
    return AUDIT.literal_texts(records, record_id)


def record_gaps(record: Any) -> tuple[bytes, ...]:
    return AUDIT.record_gaps(record)


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
    visible_coordinates = [
        target["coordinate"]
        for row in rows
        if row.get("batch_id") == QUEUE_BATCH_ID
        for target in row["target_literals"]
        if target.get("visible")
    ]
    expected = [f"0:{record_id}:0" for record_id in RECORD_IDS]
    if (
        len(visible_coordinates) != 200
        or visible_coordinates[
            QUEUE_ZERO_BASED_START:QUEUE_ZERO_BASED_STOP
        ]
        != expected
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
        matched = True
        for pk_record_id, base_record_id in zip(
            RECORD_IDS,
            base_ids,
            strict=True,
        ):
            pk_text = literal_texts(pk_jp, pk_record_id)
            base_text = literal_texts(base_jp, base_record_id)
            if pk_record_id in APPROVED_SOURCE_EQUIVALENCES:
                expected_base, expected_pk = APPROVED_SOURCE_EQUIVALENCES[
                    pk_record_id
                ]
                text_matches = (
                    base_text == (expected_base,)
                    and pk_text == (expected_pk,)
                )
            else:
                text_matches = base_text == pk_text
            if (
                not text_matches
                or record_gaps(pk_jp[(BLOCK_ID, pk_record_id)])
                != record_gaps(base_jp[(BLOCK_ID, base_record_id)])
            ):
                matched = False
                break
        if matched:
            candidates.append(start)
    if candidates != [1409]:
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
    evidence = [
        [list(pk_key), list(base_key)]
        for pk_key, base_key in mapping.items()
    ]
    if AUDIT.canonical_sha256(evidence) != EXPECTED_REVERSE_MAP_SHA256:
        raise RuntimeError(f"segment {SEGMENT} reverse map drifted")
    return mapping


def assert_source_equivalence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[tuple[int, int], tuple[int, int]]:
    BASE.assert_archive_and_mapping(records_by_label)
    RIGHT_BASE.assert_corpora(records_by_label)
    mapping = discover_base_mapping(
        records_by_label["base_jp"],
        records_by_label["pk_jp"],
    )
    if mapping != BASE_RECORD_MAP:
        raise RuntimeError(f"segment {SEGMENT} discovered Base map drifted")
    for pk_key, base_key in mapping.items():
        base_record_id = base_key[1]
        pk_record_id = pk_key[1]
        for language in ("sc", "tc"):
            if (
                records_by_label[f"pk_{language}"][pk_key].data
                != records_by_label[f"base_{language}"][base_key].data
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} context mapping drifted: "
                    f"{language}/{base_key}/{pk_key}"
                )
        if literal_texts(records_by_label["pk_en"], pk_record_id) != ("",):
            raise RuntimeError(
                f"segment {SEGMENT} PK EN context drifted: {pk_key}"
            )
        source_differs = (
            literal_texts(records_by_label["pk_jp"], pk_record_id)
            != literal_texts(records_by_label["base_jp"], base_record_id)
        )
        current_differs = (
            literal_texts(records_by_label["pk_current"], pk_record_id)
            != literal_texts(
                records_by_label["base_current"],
                base_record_id,
            )
        )
        if source_differs != (
            base_record_id in PK_SOURCE_DIVERGENCE_BASE_IDS
        ):
            raise RuntimeError(
                f"segment {SEGMENT} source divergence drifted: {pk_key}"
            )
        if current_differs != (
            base_record_id in PK_CURRENT_DIVERGENCE_BASE_IDS
        ):
            raise RuntimeError(
                f"segment {SEGMENT} current divergence drifted: {pk_key}"
            )
    return mapping


def incoming_jump_rows(
    records: dict[tuple[int, int], Any],
    target_ids: set[int],
) -> tuple[tuple[int, int, int, int, int], ...]:
    rows: list[tuple[int, int, int, int, int]] = []
    for key in sorted(records):
        for gap_id, gap in enumerate(record_gaps(records[key])):
            for match in BASE.MORPHOLOGY_JUMP_RE.finditer(gap):
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


def assert_runtime_graph(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    BASE.assert_root_call_evidence(records_by_label)
    BASE.assert_jump_and_014c_evidence(records_by_label)
    BASE.assert_live_assembly(records_by_label["base_current"])
    target_ids = set(RECORD_IDS)
    full_boundary_ids = set(range(1461, 1531))
    edges_by_label: dict[str, dict[int, set[int]]] = {}
    for label in ("pk_jp", "pk_current"):
        records = records_by_label[label]
        rows = incoming_jump_rows(records, target_ids)
        evidence = (len(rows), AUDIT.canonical_sha256(rows))
        if (
            evidence != EXPECTED_TARGET_INCOMING_EVIDENCE
            or {row[4] for row in rows} != target_ids
            or any(sum(row[4] == target for row in rows) != 1 for target in target_ids)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} incoming jump evidence drifted: {label}"
            )
        edges = AUDIT.graph_edges(records)
        edges_by_label[label] = edges
        for root, expected in FULL_TERMINAL_GROUPS.items():
            actual = tuple(
                sorted(
                    AUDIT.graph_closure(edges, root)
                    & full_boundary_ids
                )
            )
            if actual != expected:
                raise RuntimeError(
                    f"segment {SEGMENT} graph closure drifted: "
                    f"{label}/{root}"
                )
        boundary_rows = incoming_jump_rows(
            records,
            set(range(1523, 1531)),
        )
        if boundary_rows != RIGHT_BOUNDARY_INCOMING:
            raise RuntimeError(
                f"segment {SEGMENT} right boundary jumps drifted: {label}"
            )
        for root, expected in EXPECTED_FIXED_EVIDENCE[label].items():
            fixed = AUDIT.fixed_following_blockers(records, root)
            if (len(fixed), AUDIT.canonical_sha256(fixed)) != expected:
                raise RuntimeError(
                    f"segment {SEGMENT} fixed-following drifted: "
                    f"{label}/{root}"
                )

    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    for root, expected in EXPECTED_SOURCE_ONLY_FLATTENED.items():
        source_calls = AUDIT.root_call_sites(source, root)
        current_calls = AUDIT.root_call_sites(current, root)
        source_only = tuple(sorted(set(source_calls) - set(current_calls)))
        current_only = tuple(sorted(set(current_calls) - set(source_calls)))
        if (
            (len(source_only), AUDIT.canonical_sha256(source_only))
            != expected
            or current_only
        ):
            raise RuntimeError(
                f"segment {SEGMENT} caller flattening drifted: {root}"
            )

    for label, edges in edges_by_label.items():
        root208 = AUDIT.graph_closure(edges, 208) & full_boundary_ids
        root214 = AUDIT.graph_closure(edges, 214) & full_boundary_ids
        if (
            root208 != set(range(1517, 1524))
            or root214 != set(RIGHT_ROOT214_FULL_IDS)
            or root208 & root214
        ):
            raise RuntimeError(
                f"segment {SEGMENT} 1523/1524 root separation drifted: "
                f"{label}"
            )


def assert_boundaries(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    if tuple(
        literal_texts(source, record_id)[0]
        for record_id in LEFT_ROOT160_FULL_IDS
    ) != LEFT_ROOT160_FULL_JP:
        raise RuntimeError(f"segment {SEGMENT} left JP boundary drifted")
    if tuple(
        literal_texts(current, record_id)[0]
        for record_id in LEFT_ROOT160_FULL_IDS
    ) != LEFT_ROOT160_FULL_CURRENT:
        raise RuntimeError(
            f"segment {SEGMENT} left current boundary drifted"
        )
    if LEFT_ROOT160_FULL_POLICY != (
        "지 않사옵니다",
        "지 않는다",
        "지 않사옵니다",
        "지 않사옵니다",
        "지 않습니다",
        "지 않습니다",
        "지 않는다",
    ):
        raise RuntimeError(f"segment {SEGMENT} left policy drifted")
    if tuple(
        literal_texts(source, record_id)[0]
        for record_id in RIGHT_ROOT214_FULL_IDS
    ) != RIGHT_ROOT214_FULL_JP:
        raise RuntimeError(f"segment {SEGMENT} right JP boundary drifted")
    if tuple(
        literal_texts(current, record_id)[0]
        for record_id in RIGHT_ROOT214_FULL_IDS
    ) != RIGHT_ROOT214_FULL_CURRENT:
        raise RuntimeError(
            f"segment {SEGMENT} right current boundary drifted"
        )
    if RIGHT_ROOT214_FULL_POLICY != (
        "어머",
        "오오",
        "어머나",
        "흠",
        "어머",
        "오오",
        "이런",
    ):
        raise RuntimeError(f"segment {SEGMENT} right policy drifted")
    if (
        tuple(
            TRANSLATIONS_BY_RECORD[record_id]
            for record_id in range(1463, 1468)
        )
        != LEFT_ROOT160_FULL_POLICY[2:]
        or tuple(
            TRANSLATIONS_BY_RECORD[record_id]
            for record_id in range(1524, 1530)
        )
        != RIGHT_ROOT214_FULL_POLICY[:-1]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} owned boundary policy drifted"
        )


def assert_semantics(translations: dict[str, str]) -> None:
    BASE.assert_semantics(dict(BASE.RAW_TRANSLATIONS))
    RIGHT_BASE.assert_semantics(dict(RIGHT_BASE.TRANSLATIONS))
    if (
        translations != RAW_TRANSLATIONS
        or len(translations) != 67
        or set(TRANSLATIONS_BY_RECORD) != set(RECORD_IDS)
        or set(RECORD_TO_ROOT) != set(RECORD_IDS)
    ):
        raise RuntimeError(f"segment {SEGMENT} translation universe drifted")
    for pk_record_id, base_record_id in (
        (record_id, record_id - 54) for record_id in RECORD_IDS
    ):
        expected = PK_TRANSLATION_OVERRIDES.get(
            pk_record_id,
            BASE.TRANSLATIONS_BY_RECORD[base_record_id],
        )
        if TRANSLATIONS_BY_RECORD[pk_record_id] != expected:
            raise RuntimeError(
                f"segment {SEGMENT} semantic mapping drifted: "
                f"{pk_record_id}"
            )
    if (
        tuple(
            TRANSLATIONS_BY_RECORD[record_id]
            for record_id in range(1468, 1475)
        )
        != ("아니오", "아니", "아니오", "아니오", "아니오", "아니", "아니")
        or tuple(
            TRANSLATIONS_BY_RECORD[record_id]
            for record_id in range(1475, 1482)
        )
        != (
            "아니요, 아니요",
            "아니, 아니",
            "아니요, 아니요",
            "아니요, 아니요",
            "아니요, 아니요",
            "아니, 아니",
            "아니, 아니",
        )
    ):
        raise RuntimeError("denial register matrices drifted")
    if (
        TRANSLATIONS_BY_RECORD[1474] != "아니"
        or TRANSLATIONS_BY_RECORD[1505] != "으시오"
        or APPROVED_SOURCE_EQUIVALENCES[1474]
        != ("いいや", "いや")
        or APPROVED_SOURCE_EQUIVALENCES[1505]
        != ("いなされませ", "いなされ")
    ):
        raise RuntimeError("PK-specific compact source semantics drifted")
    if tuple(
        TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(1517, 1524)
    ) != ("예", "음", "예", "옛", "예", "옛", "그래"):
        raise RuntimeError("acknowledgement register matrix drifted")


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
                f"segment {SEGMENT} changed out-of-scope PK record: {key}"
            )
    for key in target_records:
        if record_gaps(rebuilt_records[key]) != record_gaps(
            current_records[key]
        ):
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
    discovered_mapping = assert_source_equivalence(records_by_label)
    assert_runtime_graph(records_by_label)
    assert_boundaries(records_by_label)
    translations = dict(RAW_TRANSLATIONS)
    assert_semantics(translations)
    current = records_by_label["pk_current"]
    for coordinate, translation in translations.items():
        _, record_id, _ = (
            int(value) for value in coordinate.split(":")
        )
        current_text = literal_texts(current, record_id)[0]
        if (
            not ENGINE.is_visible_translation_candidate(current_text)
            or "\r" in translation
            or "\n" in translation
            or translation != translation.strip()
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation)
            or UTIL.layout_signature(translation)
            != UTIL.layout_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} protected line drifted: {coordinate}"
            )
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
        source_calls = BASE.ROOT_CALL_EVIDENCE["pk_jp"][root][0]
        current_calls = BASE.ROOT_CALL_EVIDENCE["pk_current"][root][0]
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
                        FULL_TERMINAL_GROUPS[root]
                    ),
                    "owned_terminal_record_ids": [
                        terminal_id
                        for terminal_id in FULL_TERMINAL_GROUPS[root]
                        if terminal_id in RECORD_IDS
                    ],
                    "base_semantic_record_discovered_by_reverse_search": (
                        discovered_mapping[(block_id, record_id)][1]
                    ),
                    "source_call_count": source_calls,
                    "current_call_count": current_calls,
                    "source_fixed_following_count": (
                        EXPECTED_FIXED_EVIDENCE["pk_jp"][root][0]
                    ),
                    "current_fixed_following_count": (
                        EXPECTED_FIXED_EVIDENCE["pk_current"][root][0]
                    ),
                    "source_calls_flattened_in_current": (
                        EXPECTED_SOURCE_ONLY_FLATTENED[root][0]
                    ),
                    "automatic_space_inserted": False,
                    "runtime_integration_required": True,
                    "assembly_plan": ROOT_ASSEMBLY_PLAN[root],
                },
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
            int(coordinate.split(":")[1]),
        )[0]
        for coordinate, translation in translations.items()
    )
    if changed != EXPECTED_CHANGED_LITERAL_COUNT:
        raise RuntimeError(f"segment {SEGMENT} changed count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B002_S1027",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [0, 66],
                "source_literal_count": 67,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "confirmed_non_display": 0,
                "changed_literal_count": changed,
                "base_mapping_method": (
                    "unique_contiguous_reverse_search_exact_literal_gap_"
                    "with_four_approved_pk_source_equivalences"
                ),
                "discovered_base_record_range": [1409, 1475],
                "discovered_pk_minus_base_offset": 54,
                "base_reverse_map_sha256": EXPECTED_REVERSE_MAP_SHA256,
                "pk_base_jp_divergence_records": list(
                    PK_SOURCE_DIVERGENCE_BASE_IDS
                ),
                "pk_base_current_divergence_records": list(
                    PK_CURRENT_DIVERGENCE_BASE_IDS
                ),
                "pk_specific_translation_overrides": {
                    str(record_id): translation
                    for record_id, translation in (
                        PK_TRANSLATION_OVERRIDES.items()
                    )
                },
                "pk_en_visible_records": [],
                "root_call_counts": {
                    str(root): BASE.ROOT_CALL_EVIDENCE[
                        "pk_current"
                    ][root][0]
                    for root in FULL_TERMINAL_GROUPS
                },
                "root_source_fixed_following_counts": {
                    str(root): EXPECTED_FIXED_EVIDENCE["pk_jp"][root][0]
                    for root in FULL_TERMINAL_GROUPS
                },
                "root_current_fixed_following_counts": {
                    str(root): EXPECTED_FIXED_EVIDENCE[
                        "pk_current"
                    ][root][0]
                    for root in FULL_TERMINAL_GROUPS
                },
                "root_source_calls_flattened_in_current": {
                    str(root): EXPECTED_SOURCE_ONLY_FLATTENED[root][0]
                    for root in FULL_TERMINAL_GROUPS
                },
                "target_incoming_jump_evidence": list(
                    EXPECTED_TARGET_INCOMING_EVIDENCE
                ),
                "raw_014c_standalone_command_count": 0,
                "left_root160_full_policy": list(
                    LEFT_ROOT160_FULL_POLICY
                ),
                "right_root214_full_policy": list(
                    RIGHT_ROOT214_FULL_POLICY
                ),
                "root208_ends_at_pk_record": 1523,
                "root214_cross_segment_records": list(
                    RIGHT_ROOT214_FULL_IDS
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
