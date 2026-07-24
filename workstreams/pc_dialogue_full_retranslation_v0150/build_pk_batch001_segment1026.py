#!/usr/bin/env python3
"""Build PK block-0 runtime-terminal segment 1026 decisions."""

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

import build_base_batch001_segment1004 as LEFT_BASE
import build_base_batch001_segment1005 as BASE
import build_base_batch002_segment1006 as RIGHT_BASE
import build_pk_batch001_segment1025 as LEFT_PK


ENGINE = BASE.ENGINE
UTIL = BASE.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B001_S1026.private.v1.jsonl"
)
QUEUE_PATH = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "review_queue.private.v1.jsonl"
)
SEGMENT = 1026
BLOCK_ID = 0
QUEUE_BATCH_ID = "pk_msggame-B001"
QUEUE_ZERO_BASED_START = 134
QUEUE_ZERO_BASED_STOP = 200
BASE_RECORD_IDS = tuple(range(1343, 1409))
RECORD_IDS = tuple(record_id + 54 for record_id in BASE_RECORD_IDS)
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
BASE_RECORD_MAP = {
    (BLOCK_ID, record_id): (BLOCK_ID, record_id - 54)
    for record_id in RECORD_IDS
}
TRANSLATIONS_BY_RECORD = {
    record_id + 54: BASE.TRANSLATIONS_BY_RECORD[record_id]
    for record_id in BASE_RECORD_IDS
}
RAW_TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}
PK_RECORD_COUNT = 21751
JUMP_EDGE_SHA256 = (
    "3D6984E72801485A9CB48D57111EDC45122289B5CEE4C7C92F829D41C014039F"
)
ROOT_CALL_COUNTS = {
    100: 3,
    106: 0,
    112: 1,
    118: 0,
    124: 2,
    130: 0,
    136: 6,
    142: 109,
    148: 61,
    154: 0,
    160: 27,
}
EXPECTED_CALL_EVIDENCE = {
    100: ((3, "54F90C508C2C169EB0E621151B9FBDDE3CDB90BAE36734DA391853E5C60D2DF5", 1, "5555D711360118E541B7518FB2CE584ECC1C0EDB94E36BF235AB466187B5368B"), (3, "54F90C508C2C169EB0E621151B9FBDDE3CDB90BAE36734DA391853E5C60D2DF5", 1, "5555D711360118E541B7518FB2CE584ECC1C0EDB94E36BF235AB466187B5368B"), (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945")),
    106: ((0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"), (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"), (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945")),
    112: ((1, "81EC4A110F27F9319B8EC035D5B65A8E3C54069C19BF6678E2483DE965B70E4F", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"), (1, "81EC4A110F27F9319B8EC035D5B65A8E3C54069C19BF6678E2483DE965B70E4F", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"), (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945")),
    118: ((0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"), (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"), (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945")),
    124: ((3, "6727C06B54C873116E30667436260FB2154D395D872B3F6AB9A514D20D148A52", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"), (2, "3D1B696DDD72478B7432A5733D9B91618BCAFFCA73D783F5B1F5BD2EE90742A2", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"), (1, "AD01BE40596EAC671A1AD969E6C583EE00B0EE4586545BC1851AEA43FF14EB10", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945")),
    130: ((0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"), (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"), (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945")),
    136: ((8, "A388F425F2BE960A28FAFFD5581B322AB8DB379D23B99E141140D1C2F61549D6", 7, "988BE4B72A2C4059566801F92C5560EF2BF9FBE3FD87A2CF6F650D2E2973D572"), (6, "096FFFF8E368A28E3AE0ADB229ADD59E90972F5512215920826D765010ACC432", 5, "1B16E76F1B0DBA4B1530DFD1DB7DF0D0DEF22681D5184E6BB05E9E7BA939BC62"), (2, "F533E7367EFFC2CF79B1F76B3A1F7121A02EED7BFB8F143D68BE8F220CA74466", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945")),
    142: ((115, "2AA982609FE5BA4DEF44DA2CEF4BE8965221338B9A3F78E5D831FCE71C42B0B1", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"), (109, "C30D3E91F8F9B2A387865AC6FEEF3CE2EA94722E8680EE54075D2E5CFF83434B", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"), (6, "AA961CAAB46A0F6440F60F2F6C9EC7CD236459A190E1719A2D6C8F04B45BA46F", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945")),
    148: ((70, "D4F78C486A783B82E8D3AFC59CB0538145D934E547C321BE54126CD1EC2B6F8E", 7, "E1D8B671E6DA1905DDB71FF33322376FCD9769C271990D826209B0B9A5451B60"), (61, "ABB5D26AD72C3178904AB09D3BAE0E26A7799D1D9A4A7F5C323D3F7C91DB7FD6", 6, "40CBABCA23DB1FAE7F36E8A5E2DFA12BBB82390CF2049E3CBC49E17B318783BF"), (9, "377ADF56C11A2D1DA5056C2ED5BC78AE20B6F33813A3BCA8817A608F033C519D", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945")),
    154: ((0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"), (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"), (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945")),
    160: ((27, "4E5EEC1BD3788EA36B5B66B55C79C0A47F046321A6D8BEDC35B88707A5C2D7F5", 9, "54E280983B7A1D48949B9359EAFA639EB09A8F1B624FF698DC18EDA26C50FB3C"), (27, "4E5EEC1BD3788EA36B5B66B55C79C0A47F046321A6D8BEDC35B88707A5C2D7F5", 9, "54E280983B7A1D48949B9359EAFA639EB09A8F1B624FF698DC18EDA26C50FB3C"), (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945")),
}
EXPECTED_DETAILED_JUMP_EVIDENCE = (
    66,
    "EA106B4766F98203DF6C8CE8515FBEFC3A772411E1AADB33E476FE965F279B39",
)
EXPECTED_REVERSE_MAP_SHA256 = (
    "FD9B1D1EAF2A7C456594EBBDE068C9F695618A37F969A9208144E7ABE9A3EE9C"
)
DISPATCHER_TARGETS = {
    103: (1397,),
    107: (1398, 1399),
    109: (1404,),
    110: (1400, 1401),
    111: (1402, 1403),
    113: (1405, 1406),
    115: (1411,),
    116: (1407, 1408),
    117: (1409, 1410),
    119: (1412, 1413),
    121: (1418,),
    122: (1414, 1415),
    123: (1416, 1417),
    125: (1419, 1420),
    127: (1425,),
    128: (1421, 1422),
    129: (1423, 1424),
    131: (1426, 1427),
    133: (1432,),
    134: (1428, 1429),
    135: (1430, 1431),
    137: (1433, 1434),
    139: (1439,),
    140: (1435, 1436),
    141: (1437, 1438),
    143: (1440, 1441),
    145: (1446,),
    146: (1442, 1443),
    147: (1444, 1445),
    149: (1447, 1448),
    151: (1453,),
    152: (1449, 1450),
    153: (1451, 1452),
    155: (1454, 1455),
    157: (1460,),
    158: (1456, 1457),
    159: (1458, 1459),
    161: (1461, 1462),
}
OWNED_TERMINAL_GROUPS = {
    root: tuple(record_id + 54 for record_id in record_ids)
    for root, record_ids in BASE.TERMINAL_GROUPS.items()
}
ROOT_ASSEMBLY_PLAN = {
    100: {"upstream": "말", "example": "말+한다"},
    106: {"upstream": "none", "example": "말씀하시다/말하다"},
    112: {"upstream": "none", "example": "안 됩니다"},
    118: {"upstream": "none", "example": "가겠습니다/간다"},
    124: {
        "upstream": "caller-specific action stem",
        "example": "정진하+겠습니다",
    },
    130: {"upstream": "none", "example": "가시오/가라"},
    136: {
        "upstream": "caller-specific past stem ending in 었",
        "example": "대비하였+습니다",
    },
    142: {
        "upstream": "caller-specific action or verbal-noun stem",
        "example": "말+합니다",
    },
    148: {
        "upstream": "caller-specific action or verbal-noun stem",
        "example": "보호+하겠습니다",
    },
    154: {"upstream": "none", "example": "있어서/였고"},
    160: {
        "upstream": "caller-specific predicate stem",
        "example": "연연하+지 않습니다",
    },
}
LEFT_BOUNDARY_IDS = tuple(range(1391, 1398))
LEFT_BOUNDARY_JP = (
    "申します",
    "いう",
    "申しまする",
    "申します",
    "申します",
    "申します",
    "申す",
)
LEFT_BOUNDARY_CURRENT = (
    "아룁니다",
    "말하다",
    "아뢰옵니다",
    "아룁니다",
    "아룁니다",
    "아룁니다",
    "아뢴다",
)
LEFT_BOUNDARY_POLICY = tuple(
    LEFT_BASE.TRANSLATIONS_BY_RECORD[record_id]
    for record_id in range(1337, 1343)
) + (BASE.TRANSLATIONS_BY_RECORD[1343],)
RIGHT_BOUNDARY_IDS = tuple(range(1461, 1468))
RIGHT_BOUNDARY_JP = (
    "おりませぬ",
    "おらぬ",
    "おりませぬ",
    "おりませぬ",
    "いません",
    "おりません",
    "おらぬ",
)
RIGHT_BOUNDARY_CURRENT = (
    "없사옵니다",
    "없다",
    "없사옵니다",
    "없사옵니다",
    "없습니다",
    "없습니다",
    "없다",
)
RIGHT_BOUNDARY_POLICY = (
    BASE.TRANSLATIONS_BY_RECORD[1407],
    BASE.TRANSLATIONS_BY_RECORD[1408],
) + tuple(
    RIGHT_BASE.TRANSLATIONS_BY_RECORD[record_id]
    for record_id in range(1409, 1414)
)
BASIS = (
    "review_queue_pk_msggame_B001_C_pristine_pk_pc_jp_authoritative_"
    "block0_person_voice_runtime_terminal_table_records1397_1462_with_"
    "independently_verified_exact_minus54_base_jp_sc_tc_and_current_"
    "counterparts_empty_pk_en_context_checked_in_base_s1005_semantic_"
    "policy_reused_only_after_exact_source_and_runtime_topology_proof_"
    "actual_pk_terminal_jump_graph_dispatcher_closures_and_live_root_"
    "call_coordinate_fixed_following_and_source_current_flatten_digests_"
    "unique_contiguous_Base_reverse_search_without_offset_assumption_"
    "say_prohibition_go_progressive_do_volitional_connective_"
    "and_negative_existence_korean_bound_suffix_design_left_root100_and_"
    "right_root160_cross_segment_boundary_matrices_agreed_runtime_"
    "assembly_pending_no_korean_build_authority"
)


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return tuple(
        literal.text for literal in ENGINE.parse_record_literals(records[key])
    )


def gap_bytes(record: Any) -> tuple[bytes, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps: list[bytes] = []
    cursor = 0
    for literal in literals:
        gaps.append(record.data[cursor : literal.marker_offset])
        cursor = literal.marker_end
    gaps.append(record.data[cursor:])
    return tuple(gaps)


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
        if all(
            literal_texts(
                pk_jp,
                (BLOCK_ID, pk_record_id),
            )
            == literal_texts(
                base_jp,
                (BLOCK_ID, base_record_id),
            )
            and gap_bytes(pk_jp[(BLOCK_ID, pk_record_id)])
            == gap_bytes(base_jp[(BLOCK_ID, base_record_id)])
            for pk_record_id, base_record_id in zip(
                RECORD_IDS,
                base_ids,
                strict=True,
            )
        ):
            candidates.append(start)
    if candidates != [1343]:
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
    if LEFT_PK.canonical_sha256(
        [
            [pk_key[1], base_key[1]]
            for pk_key, base_key in mapping.items()
        ]
    ) != EXPECTED_REVERSE_MAP_SHA256:
        raise RuntimeError(f"segment {SEGMENT} reverse map drifted")
    return mapping


def assert_source_equivalence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[tuple[int, int], tuple[int, int]]:
    # The checked-in Base audit already pins all nine exact subset digests,
    # arities, skeletons, and the +54 JP/SC/TC/current mapping.
    BASE.assert_corpora(records_by_label)
    BASE.assert_semantics(
        {
            f"0:{record_id}:0": TRANSLATIONS_BY_RECORD[record_id + 54]
            for record_id in BASE_RECORD_IDS
        }
    )
    discovered_mapping = discover_base_mapping(
        records_by_label["base_jp"],
        records_by_label["pk_jp"],
    )
    if discovered_mapping != BASE_RECORD_MAP:
        raise RuntimeError(f"segment {SEGMENT} discovered Base map drifted")
    for pk_key, base_key in discovered_mapping.items():
        for language in ("jp", "current", "sc", "tc"):
            if literal_texts(
                records_by_label[f"pk_{language}"],
                pk_key,
            ) != literal_texts(
                records_by_label[f"base_{language}"],
                base_key,
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base/PK {language} mapping drifted: "
                    f"{base_key}/{pk_key}"
                )
        if literal_texts(records_by_label["pk_en"], pk_key) != ("",):
            raise RuntimeError(
                f"segment {SEGMENT} PK EN terminal context drifted: {pk_key}"
            )
    return discovered_mapping


def assert_runtime_graph(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source_records = records_by_label["pk_jp"]
    current_records = records_by_label["pk_current"]
    target_ids = set(RECORD_IDS)
    edges = [
        [block_id, record_id, operand]
        for (block_id, record_id), record in sorted(current_records.items())
        for operand in BASE.operands(record.data, BASE.MORPHOLOGY_JUMP_RE)
        if operand in target_ids
    ]
    digest = hashlib.sha256(
        json.dumps(edges, separators=(",", ":")).encode("ascii")
    ).hexdigest().upper()
    if digest != JUMP_EDGE_SHA256 or len(edges) != len(RECORD_IDS):
        raise RuntimeError(f"segment {SEGMENT} PK terminal jump graph drifted")
    if {edge[2] for edge in edges} != target_ids:
        raise RuntimeError(
            f"segment {SEGMENT} PK terminal incoming edge universe drifted"
        )
    actual_dispatchers: dict[int, tuple[int, ...]] = {}
    for _, record_id, operand in edges:
        actual_dispatchers.setdefault(record_id, ())
        actual_dispatchers[record_id] += (operand,)
    if actual_dispatchers != DISPATCHER_TARGETS:
        raise RuntimeError(
            f"segment {SEGMENT} PK dispatcher closure topology drifted"
        )

    for label, records in (
        ("pk_jp", source_records),
        ("pk_current", current_records),
    ):
        detailed_edges = tuple(
            (
                key[0],
                key[1],
                gap_id,
                match.start(),
                struct.unpack("<I", match.group(1))[0],
            )
            for key in sorted(records)
            for gap_id, gap in enumerate(gap_bytes(records[key]))
            for match in BASE.MORPHOLOGY_JUMP_RE.finditer(gap)
            if struct.unpack("<I", match.group(1))[0] in target_ids
        )
        if (
            len(detailed_edges),
            LEFT_PK.canonical_sha256(detailed_edges),
        ) != EXPECTED_DETAILED_JUMP_EVIDENCE:
            raise RuntimeError(
                f"segment {SEGMENT} detailed jump evidence drifted: "
                f"{label}"
            )

    for root, expected_count in ROOT_CALL_COUNTS.items():
        source_calls = LEFT_PK.root_call_sites(source_records, root)
        current_calls = LEFT_PK.root_call_sites(current_records, root)
        source_fixed = LEFT_PK.fixed_following_blockers(
            source_records,
            root,
        )
        current_fixed = LEFT_PK.fixed_following_blockers(
            current_records,
            root,
        )
        source_only = tuple(
            sorted(set(source_calls) - set(current_calls))
        )
        current_only = tuple(
            sorted(set(current_calls) - set(source_calls))
        )
        actual_evidence = (
            (
                len(source_calls),
                LEFT_PK.canonical_sha256(source_calls),
                len(source_fixed),
                LEFT_PK.canonical_sha256(source_fixed),
            ),
            (
                len(current_calls),
                LEFT_PK.canonical_sha256(current_calls),
                len(current_fixed),
                LEFT_PK.canonical_sha256(current_fixed),
            ),
            (
                len(source_only),
                LEFT_PK.canonical_sha256(source_only),
                len(current_only),
                LEFT_PK.canonical_sha256(current_only),
            ),
        )
        if (
            len(current_calls) != expected_count
            or actual_evidence != EXPECTED_CALL_EVIDENCE[root]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} PK root {root} "
                "caller/fixed/flatten evidence drifted"
            )


def assert_boundaries(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    if tuple(
        literal_texts(source, (BLOCK_ID, record_id))[0]
        for record_id in LEFT_BOUNDARY_IDS
    ) != LEFT_BOUNDARY_JP:
        raise RuntimeError(f"segment {SEGMENT} left JP boundary drifted")
    if tuple(
        literal_texts(current, (BLOCK_ID, record_id))[0]
        for record_id in LEFT_BOUNDARY_IDS
    ) != LEFT_BOUNDARY_CURRENT:
        raise RuntimeError(f"segment {SEGMENT} left current boundary drifted")
    if tuple(
        literal_texts(source, (BLOCK_ID, record_id))[0]
        for record_id in RIGHT_BOUNDARY_IDS
    ) != RIGHT_BOUNDARY_JP:
        raise RuntimeError(f"segment {SEGMENT} right JP boundary drifted")
    if tuple(
        literal_texts(current, (BLOCK_ID, record_id))[0]
        for record_id in RIGHT_BOUNDARY_IDS
    ) != RIGHT_BOUNDARY_CURRENT:
        raise RuntimeError(f"segment {SEGMENT} right current boundary drifted")
    if LEFT_BOUNDARY_POLICY != (
        "합니다",
        "한다",
        "하옵니다",
        "합니다",
        "합니다",
        "합니다",
        "한다",
    ):
        raise RuntimeError(f"segment {SEGMENT} left policy boundary drifted")
    if RIGHT_BOUNDARY_POLICY != (
        "지 않사옵니다",
        "지 않는다",
        "지 않사옵니다",
        "지 않사옵니다",
        "지 않습니다",
        "지 않습니다",
        "지 않는다",
    ):
        raise RuntimeError(f"segment {SEGMENT} right policy boundary drifted")
    if (
        TRANSLATIONS_BY_RECORD[1397] != LEFT_BOUNDARY_POLICY[-1]
        or tuple(
            TRANSLATIONS_BY_RECORD[record_id]
            for record_id in (1461, 1462)
        )
        != RIGHT_BOUNDARY_POLICY[:2]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} owned boundary decisions drifted"
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
                f"segment {SEGMENT} changed an out-of-scope PK record: {key}"
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
    if translations != RAW_TRANSLATIONS or len(translations) != 66:
        raise RuntimeError(f"segment {SEGMENT} translation universe drifted")
    if translations["0:1397:0"] != "한다":
        raise RuntimeError("humble/plain speech terminal drifted")
    if translations["0:1403:0"] != "말씀하시다":
        raise RuntimeError("passive/respectful speech terminal drifted")
    if translations["0:1404:0"] != "말하다":
        raise RuntimeError("plain speech terminal retained nominal form")
    if tuple(
        translations[f"0:{record_id}:0"]
        for record_id in range(1419, 1426)
    ) != (
        "겠습니다",
        "겠다",
        "겠사옵니다",
        "겠사옵니다",
        "겠사옵니다",
        "겠다",
        "겠다",
    ):
        raise RuntimeError("continuative go terminal matrix drifted")
    if translations["0:1429:0"] != "가시오":
        raise RuntimeError("imperative direction drifted")
    if tuple(
        translations[f"0:{record_id}:0"]
        for record_id in range(1433, 1440)
    ) != (
        "었습니다",
        "었다",
        "었습니다",
        "었습니다",
        "었습니다",
        "었다",
        "었다",
    ):
        raise RuntimeError("bound past-progressive suffix matrix drifted")
    if tuple(
        translations[f"0:{record_id}:0"]
        for record_id in range(1461, 1463)
    ) != ("지 않사옵니다", "지 않는다"):
        raise RuntimeError("negative progressive suffix matrix drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]], str]:
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
    if set(translations) != {
        f"0:{record_id}:0" for record_id in RECORD_IDS
    }:
        raise RuntimeError(f"segment {SEGMENT} coordinate universe drifted")
    current = records_by_label["pk_current"]
    for coordinate, translation in translations.items():
        _, record_id, _ = (int(value) for value in coordinate.split(":"))
        current_text = literal_texts(current, (BLOCK_ID, record_id))[0]
        if not ENGINE.is_visible_translation_candidate(current_text):
            raise RuntimeError(
                f"segment {SEGMENT} target became non-visible: {coordinate}"
            )
        if UTIL.layout_signature(translation) != UTIL.layout_signature(
            current_text
        ):
            raise RuntimeError(
                f"segment {SEGMENT} layout signature drifted: {coordinate}"
            )
        if (
            "\r" in translation
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} text residue drifted: {coordinate}"
            )
    assert_semantics(translations)
    candidate_sha256 = assert_pk_overlay_roundtrip(prepared, translations)

    rows: list[dict[str, object]] = []
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        root = next(
            root
            for root, record_ids in OWNED_TERMINAL_GROUPS.items()
            if record_id in record_ids
        )
        full_terminal_ids = (
            LEFT_BOUNDARY_IDS
            if root == 100
            else RIGHT_BOUNDARY_IDS
            if root == 160
            else OWNED_TERMINAL_GROUPS[root]
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
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "runtime_assembly_evidence": {
                    "root": root,
                    "full_terminal_record_ids": list(full_terminal_ids),
                    "base_semantic_record_discovered_by_reverse_search": (
                        discovered_mapping[(block_id, record_id)][1]
                    ),
                    "source_call_count": (
                        EXPECTED_CALL_EVIDENCE[root][0][0]
                    ),
                    "current_call_count": (
                        EXPECTED_CALL_EVIDENCE[root][1][0]
                    ),
                    "source_fixed_following_count": (
                        EXPECTED_CALL_EVIDENCE[root][0][2]
                    ),
                    "current_fixed_following_count": (
                        EXPECTED_CALL_EVIDENCE[root][1][2]
                    ),
                    "source_calls_flattened_in_current": (
                        EXPECTED_CALL_EVIDENCE[root][2][0]
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
    if len(validated) != 66 or len(rows) != 66:
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
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B001_S1026",
                "queue": "pk_msggame-B001",
                "queue_zero_based_ordinals": [134, 199],
                "source_literal_count": 66,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "confirmed_non_display": 0,
                "changed_literal_count": changed,
                "base_mapping_method": (
                    "unique_contiguous_reverse_search_exact_literal_gap"
                ),
                "discovered_base_record_range": [1343, 1408],
                "discovered_pk_minus_base_offset": 54,
                "base_reverse_map_sha256": EXPECTED_REVERSE_MAP_SHA256,
                "pk_base_jp_sc_tc_current_literal_divergence_records": [],
                "pk_en_visible_records": [],
                "dispatcher_targets": {
                    str(dispatcher): list(targets)
                    for dispatcher, targets in DISPATCHER_TARGETS.items()
                },
                "root_call_counts": ROOT_CALL_COUNTS,
                "root_source_call_counts": {
                    str(root): evidence[0][0]
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
                "terminal_jump_edge_sha256": JUMP_EDGE_SHA256,
                "detailed_jump_evidence": list(
                    EXPECTED_DETAILED_JUMP_EVIDENCE
                ),
                "left_boundary_policy": list(LEFT_BOUNDARY_POLICY),
                "right_boundary_policy": list(RIGHT_BOUNDARY_POLICY),
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
