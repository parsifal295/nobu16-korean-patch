#!/usr/bin/env python3
"""Build Base block-0 runtime-terminal segment 1014 decisions."""

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

import build_base_batch002_segment1007 as GRAPH
import build_base_batch003_segment1011 as PRIOR


ENGINE = PRIOR.ENGINE
GENERAL = PRIOR.GENERAL
UTIL = PRIOR.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B004_S1014.private.v1.jsonl"
)
SEGMENT = 1014
QUEUE_BATCH_ID = "base_msggame-B004"
BLOCK_ID = 0
RECORD_IDS = tuple(range(1948, 2014))
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)

# A second PK-only seven-record terminal family has appeared by this range.
# Exact seven-literal JP tuple matches establish +68; +61 points at the
# immediately preceding, semantically unrelated terminal families.
PK_RECORD_OFFSET = 68
PK_RECORD_MAP = {
    (BLOCK_ID, record_id): (
        BLOCK_ID,
        record_id + PK_RECORD_OFFSET,
    )
    for record_id in RECORD_IDS
}

FULL_TERMINAL_GROUPS = {
    610: tuple(range(1946, 1953)),
    616: tuple(range(1953, 1960)),
    622: tuple(range(1960, 1967)),
    628: tuple(range(1967, 1974)),
    634: tuple(range(1974, 1981)),
    640: tuple(range(1981, 1988)),
    646: tuple(range(1988, 1995)),
    652: tuple(range(1995, 2002)),
    658: tuple(range(2002, 2009)),
    664: tuple(range(2009, 2016)),
}
PK_ROOT_BY_BASE = {
    base_root: base_root + 12 for base_root in FULL_TERMINAL_GROUPS
}
TARGET_TERMINAL_GROUPS = {
    root: tuple(
        record_id for record_id in record_ids if record_id in RECORD_IDS
    )
    for root, record_ids in FULL_TERMINAL_GROUPS.items()
}

SOURCE_JP_BY_ROOT = {
    610: (
        "ちます",
        "つ",
        "ちます",
        "ちます",
        "ちます",
        "ちます",
        "つ",
    ),
    616: (
        "りました",
        "った",
        "りました",
        "りました",
        "りました",
        "りました",
        "った",
    ),
    622: (
        "いました",
        "った",
        "いました",
        "いました",
        "いました",
        "いました",
        "った",
    ),
    628: (
        "ちました",
        "った",
        "ちました",
        "ちました",
        "ちました",
        "ちました",
        "った",
    ),
    634: (
        "って",
        "って",
        "まして",
        "まして",
        "って",
        "って",
        "って",
    ),
    640: (
        "て",
        "て",
        "まして",
        "まして",
        "まして",
        "て",
        "て",
    ),
    646: (
        "ちなされ",
        "て",
        "ちなされ",
        "ちなされ",
        "ってください",
        "ってくだされ",
        "て",
    ),
    652: (
        "で",
        "で",
        "でございまして",
        "でして",
        "でして",
        "で",
        "で",
    ),
    658: (
        "てません",
        "てぬ",
        "てませぬ",
        "てませぬ",
        "てません",
        "てませぬ",
        "てぬ",
    ),
    664: (
        "では",
        "では",
        "それでは",
        "ならば",
        "じゃあ",
        "では",
        "じゃあ",
    ),
}
TRANSLATION_POLICY_BY_ROOT = {
    610: (
        "합니다",
        "한다",
        "합니다",
        "합니다",
        "합니다",
        "합니다",
        "한다",
    ),
    616: (
        "했습니다",
        "했다",
        "했습니다",
        "했습니다",
        "했습니다",
        "했습니다",
        "했다",
    ),
    622: (
        "했습니다",
        "했다",
        "했습니다",
        "했습니다",
        "했습니다",
        "했습니다",
        "했다",
    ),
    628: (
        "했습니다",
        "했다",
        "했습니다",
        "했습니다",
        "했습니다",
        "했습니다",
        "했다",
    ),
    634: (
        "하여",
        "하여",
        "하여",
        "하여",
        "하여",
        "하여",
        "하여",
    ),
    640: (
        "하여",
        "하여",
        "하여",
        "하여",
        "하여",
        "하여",
        "하여",
    ),
    646: (
        "하시오",
        "하라",
        "하시오",
        "하시오",
        "해 주십시오",
        "해 주시오",
        "하라",
    ),
    652: (
        "이고",
        "이고",
        "이옵고",
        "이며",
        "이며",
        "이고",
        "이고",
    ),
    658: (
        "지 못합니다",
        "지 못한다",
        "지 못하옵니다",
        "지 못하옵니다",
        "지 못합니다",
        "지 못하옵니다",
        "지 못한다",
    ),
    664: (
        "그러면",
        "그러면",
        "그렇다면",
        "그렇다면",
        "그럼",
        "그러면",
        "그럼",
    ),
}
EXPECTED_FULL_BASE_JP = {
    record_id: source
    for root, record_ids in FULL_TERMINAL_GROUPS.items()
    for record_id, source in zip(
        record_ids,
        SOURCE_JP_BY_ROOT[root],
        strict=True,
    )
}
FULL_TRANSLATION_POLICY = {
    record_id: translation
    for root, record_ids in FULL_TERMINAL_GROUPS.items()
    for record_id, translation in zip(
        record_ids,
        TRANSLATION_POLICY_BY_ROOT[root],
        strict=True,
    )
}
EXPECTED_BASE_JP = {
    record_id: EXPECTED_FULL_BASE_JP[record_id]
    for record_id in RECORD_IDS
}
TRANSLATIONS_BY_RECORD = {
    record_id: FULL_TRANSLATION_POLICY[record_id]
    for record_id in RECORD_IDS
}
RAW_TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}

ARCHIVE_DIGESTS = {
    "base_jp": "4E3AD270D48234F9BF806FF89CD061B8BBD7280C7259A84F9C6D985713221CEF",
    "base_current": "7991886DD1F547581A1951DA302E90EAF1F6AFC7E8B419014F79BF492EE1F989",
    "base_sc": "265DD1FDFD95CC0B686A937D2CD6C5375981919DB1EE17130A0DECAEE69D6255",
    "base_tc": "265DD1FDFD95CC0B686A937D2CD6C5375981919DB1EE17130A0DECAEE69D6255",
    "pk_jp": "84C2FED132AE000C0FED6355234718796D6C8F1142709E65A991B1F84E2AB1F0",
    "pk_current": "C3B7D811DEF0E166C58AA947E5F2922759C7BF5EDB527490F6BD10CE825EE1C2",
    "pk_sc": "D6EB4128C38762BD7E6D3784A18B300CD1D1FFDD41F0A0263ED227DBDD40EA66",
    "pk_tc": "D6EB4128C38762BD7E6D3784A18B300CD1D1FFDD41F0A0263ED227DBDD40EA66",
    "pk_en": "D6EB4128C38762BD7E6D3784A18B300CD1D1FFDD41F0A0263ED227DBDD40EA66",
}

CROSS_SEGMENT_SOURCE_JP = {
    1946: "ちます",
    1947: "つ",
    2014: "では",
    2015: "じゃあ",
}
CROSS_SEGMENT_CURRENT_KO = {
    1946: "합니다",
    1947: "츠",
    2014: "그럼",
    2015: "그럼",
}
CROSS_SEGMENT_TRANSLATION_POLICY = {
    record_id: FULL_TRANSLATION_POLICY[record_id]
    for record_id in CROSS_SEGMENT_SOURCE_JP
}

SEGMENT_JUMP_EDGE_SHA256 = {
    "base": "B7DCB15CF6EFD37FC0C5D1A521E086FD9B4C3D098D66A8F68014ADA922674FFE",
    "pk": "F0714609E028D76E9F371906FCA3BD9B5A1E979C917B2F049165C6BF7048B12C",
}
FULL_GROUP_JUMP_EDGE_SHA256 = {
    "base": "F8AE3DBE90ED86572414A6DDEA0AB5AEDC68DBE0ACE1981728888677FAF73B46",
    "pk": "B07ADE4FE20D114EA8F57565775F9E5509A5C20EA307E4C8F773D7B331969D71",
}

EMPTY_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
ROOT_EVIDENCE = {
    610: {
        "pk_root": 622,
        "base_source": (0, EMPTY_SHA256),
        "base_current": (0, EMPTY_SHA256),
        "pk_source": (0, EMPTY_SHA256),
        "pk_current": (0, EMPTY_SHA256),
    },
    616: {
        "pk_root": 628,
        "base_source": (
            136,
            "0A434131826C43BFAC128B41E627C226CDADD4D9F64589B0050D2CCDF2237A1A",
        ),
        "base_current": (
            115,
            "F4ECADAC7D81D0F8DC183DA84D9DE923D9EAE2D0B116496155458ED93A8FF797",
        ),
        "pk_source": (
            166,
            "C7B2ACE5C491EEB6DD68A9D9ED54001D6591D5B0E6DB33A1972C9FD79B2C4877",
        ),
        "pk_current": (
            145,
            "D145A861D5E2940C536B827A1D5B349B6C67352CEAA0F053B8A54FB2F9154BB4",
        ),
    },
    622: {
        "pk_root": 634,
        "base_source": (
            6,
            "E03B8FF2760F6BADDE797B27FCDE4E6652865E7E082719C33905C9A5440955B0",
        ),
        "base_current": (
            5,
            "4F401B98637F3D80B5C00F3F1D809F578169196142C9A9432E5F8313EABF1E71",
        ),
        "pk_source": (
            15,
            "BC9C5EFA08B2B1C8289307CB444A93AC627442ABA7746FA232D4C8490916280D",
        ),
        "pk_current": (
            13,
            "10D1992FEB0EE4EBA0B8E525013FDD7054DB7217954FF1BE9264BA85CC9891DC",
        ),
    },
    628: {
        "pk_root": 640,
        "base_source": (
            2,
            "5D25151EF13FCF160516A6706A9C5C9F0A8F454210741E3CAF48DBB9A751E8EF",
        ),
        "base_current": (
            2,
            "5D25151EF13FCF160516A6706A9C5C9F0A8F454210741E3CAF48DBB9A751E8EF",
        ),
        "pk_source": (
            2,
            "50E131428E50A3CF04A7A907A6966B61E75C67B3ACAC20016203924661FB0D8B",
        ),
        "pk_current": (
            2,
            "50E131428E50A3CF04A7A907A6966B61E75C67B3ACAC20016203924661FB0D8B",
        ),
    },
    634: {
        "pk_root": 646,
        "base_source": (0, EMPTY_SHA256),
        "base_current": (0, EMPTY_SHA256),
        "pk_source": (0, EMPTY_SHA256),
        "pk_current": (0, EMPTY_SHA256),
    },
    640: {
        "pk_root": 652,
        "base_source": (
            1,
            "AB002135DBBB19C3F46C4D5214D3A179EA9A738CB18E395CFA204F4A75726A9D",
        ),
        "base_current": (
            1,
            "AB002135DBBB19C3F46C4D5214D3A179EA9A738CB18E395CFA204F4A75726A9D",
        ),
        "pk_source": (
            1,
            "8E04859A19B22F70AD885BA1D603D3D61E992610EF662A2EC5F2C5136FCC458F",
        ),
        "pk_current": (
            1,
            "8E04859A19B22F70AD885BA1D603D3D61E992610EF662A2EC5F2C5136FCC458F",
        ),
    },
    646: {
        "pk_root": 658,
        "base_source": (0, EMPTY_SHA256),
        "base_current": (0, EMPTY_SHA256),
        "pk_source": (0, EMPTY_SHA256),
        "pk_current": (0, EMPTY_SHA256),
    },
    652: {
        "pk_root": 664,
        "base_source": (0, EMPTY_SHA256),
        "base_current": (0, EMPTY_SHA256),
        "pk_source": (0, EMPTY_SHA256),
        "pk_current": (0, EMPTY_SHA256),
    },
    658: {
        "pk_root": 670,
        "base_source": (
            1,
            "1DC4B971FEB7E17DCC318487ED89D9EC3974D61B9409B27A810CF3863B2BACC2",
        ),
        "base_current": (
            1,
            "1DC4B971FEB7E17DCC318487ED89D9EC3974D61B9409B27A810CF3863B2BACC2",
        ),
        "pk_source": (
            2,
            "DE388B8C63002BEE17BBCCA769616D05FAE3AEC4B98285C6A33C8E968B359DC8",
        ),
        "pk_current": (
            2,
            "DE388B8C63002BEE17BBCCA769616D05FAE3AEC4B98285C6A33C8E968B359DC8",
        ),
    },
    664: {
        "pk_root": 676,
        "base_source": (0, EMPTY_SHA256),
        "base_current": (0, EMPTY_SHA256),
        "pk_source": (
            1,
            "41B87A47A8C2C49A35E07822EF9D9F3B77089FF2BEF6EAC3E6E7F767EB6FA315",
        ),
        "pk_current": (
            1,
            "41B87A47A8C2C49A35E07822EF9D9F3B77089FF2BEF6EAC3E6E7F767EB6FA315",
        ),
    },
}

SOURCE_ONLY_FLATTENED_CALLS = {
    616: (
        "15:2204:1:0",
        "15:2261:1:0",
        "6:1450:1:0",
        "6:1451:1:0",
        "6:1452:1:0",
        "6:1453:1:0",
        "6:1454:1:0",
        "6:1455:1:0",
        "6:1456:1:0",
        "6:1457:1:0",
        "6:1458:1:0",
        "6:1459:1:0",
        "6:1460:1:0",
        "6:1461:1:0",
        "6:1520:2:0",
        "6:4178:1:0",
        "8:1067:1:0",
        "8:1068:1:0",
        "8:1068:2:0",
        "8:1183:1:0",
        "8:398:1:0",
    ),
    622: ("8:1057:1:0",),
}
PK_SOURCE_ONLY_FLATTENED_CALLS = {
    628: (
        "15:2234:1:0",
        "15:2292:1:0",
        "6:1454:1:0",
        "6:1455:1:0",
        "6:1456:1:0",
        "6:1457:1:0",
        "6:1458:1:0",
        "6:1459:1:0",
        "6:1460:1:0",
        "6:1461:1:0",
        "6:1462:1:0",
        "6:1463:1:0",
        "6:1464:1:0",
        "6:1465:1:0",
        "6:1526:2:0",
        "6:4208:1:0",
        "8:1079:1:0",
        "8:1080:1:0",
        "8:1080:2:0",
        "8:1199:1:0",
        "8:410:1:0",
    ),
    634: (
        "6:4639:2:0",
        "8:1069:1:0",
    ),
}

CURRENT_CALLER_REWRITE_EXAMPLES = {
    616: {
        "2:127:3": "당주라니 is already a completed current Korean phrase",
        "6:2068:2": "되 stem and following clause need joint rewriting",
    },
    622: {
        "7:873:1": "일으키고 말 stem requires a completive past",
        "15:1630:2": "듣 stem requires lexical past conjugation",
    },
    628: {
        "8:288:3": "미리 손을 써 stem requires a past connective",
    },
    640: {
        "6:3541:1": "아뢰 stem needs a connective rather than current 서",
    },
    658: {
        "6:3513:1": "보탬이 될 stem requires an inability ending",
    },
}

BASIS = (
    "review_queue_base_msggame_B004_C_pristine_base_pc_jp_authoritative_"
    "block0_runtime_terminal_records1948_2013_exact_seven_literal_tuple_"
    "plus68_pk_semantic_mapping_after_two_pk_only_seven_record_"
    "insertions_base_pk_root_shift_plus12_jp_current_sc_tc_exact_pk_en_"
    "empty_archive_digests_all_014a_segment_and_full_boundary_edges_"
    "source_current_0143_root_call_coordinate_digests_source_only_"
    "flattening_registries_cross_segment_records1946_1947_2014_2015_"
    "contract_neutral_action_past_connective_imperative_copular_"
    "connective_inability_and_transition_matrices_runtime_caller_"
    "rewrite_pending_one_line_reverse_overlay_no_korean_build_authority"
)


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return PRIOR.literal_texts(records, key)


def gap_bytes(record: Any) -> tuple[bytes, ...]:
    return PRIOR.gap_bytes(record)


def archive_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    return PRIOR.archive_records(prepared)


def root_call_sites(
    records: dict[tuple[int, int], Any],
    root: int,
) -> tuple[str, ...]:
    return tuple(
        f"{key[0]}:{key[1]}:{gap_id}:{match.start()}"
        for key in sorted(records)
        for gap_id, gap in enumerate(gap_bytes(records[key]))
        for match in PRIOR.PRIOR.PREVIOUS.MORPHOLOGY_COMMAND_RE.finditer(
            gap
        )
        if struct.unpack("<I", match.group(1))[0] == root
    )


def incoming_edges(
    records: dict[tuple[int, int], Any],
    target_ids: set[int],
) -> list[list[int]]:
    return [
        [block_id, record_id, operand]
        for (block_id, record_id), record in sorted(records.items())
        for operand in PRIOR.PRIOR.PREVIOUS.operands(
            record.data,
            PRIOR.PRIOR.PREVIOUS.MORPHOLOGY_JUMP_RE,
        )
        if operand in target_ids
    ]


def edge_digest(edges: list[list[int]]) -> str:
    return hashlib.sha256(
        json.dumps(edges, separators=(",", ":")).encode("ascii")
    ).hexdigest().upper()


def assert_corpora(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    for label, records in records_by_label.items():
        keys = (
            tuple(PK_RECORD_MAP.values())
            if label.startswith("pk_")
            else RECORD_KEYS
        )
        if GENERAL.subset_digest(records, keys) != ARCHIVE_DIGESTS[label]:
            raise RuntimeError(f"segment {SEGMENT} {label} corpus drifted")

    for key in RECORD_KEYS:
        record_id = key[1]
        mapped = PK_RECORD_MAP[key]
        if literal_texts(records_by_label["base_jp"], key) != (
            EXPECTED_BASE_JP[record_id],
        ):
            raise RuntimeError(
                f"segment {SEGMENT} pristine JP drifted: {key}"
            )
        for label in ("base_jp", "base_current", "base_sc", "base_tc"):
            if (
                len(literal_texts(records_by_label[label], key)) != 1
                or gap_bytes(records_by_label[label][key])
                != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base skeleton drifted: "
                    f"{label}/{key}"
                )
        for label in ("pk_jp", "pk_current", "pk_sc", "pk_tc", "pk_en"):
            if (
                len(literal_texts(records_by_label[label], mapped)) != 1
                or gap_bytes(records_by_label[label][mapped])
                != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} PK skeleton drifted: "
                    f"{label}/{mapped}"
                )
        for language in ("jp", "current", "sc", "tc"):
            if literal_texts(
                records_by_label[f"base_{language}"],
                key,
            ) != literal_texts(
                records_by_label[f"pk_{language}"],
                mapped,
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {language} mapping drifted: "
                    f"{key}/{mapped}"
                )
        if literal_texts(records_by_label["pk_en"], mapped) != ("",):
            raise RuntimeError(
                f"segment {SEGMENT} PK EN context drifted: {mapped}"
            )

    for record_id, source_jp in CROSS_SEGMENT_SOURCE_JP.items():
        key = (BLOCK_ID, record_id)
        mapped = (BLOCK_ID, record_id + PK_RECORD_OFFSET)
        if (
            literal_texts(records_by_label["base_jp"], key)
            != (source_jp,)
            or literal_texts(records_by_label["base_current"], key)
            != (CROSS_SEGMENT_CURRENT_KO[record_id],)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} cross literal drifted: {key}"
            )
        for language in ("jp", "current", "sc", "tc"):
            if literal_texts(
                records_by_label[f"base_{language}"],
                key,
            ) != literal_texts(
                records_by_label[f"pk_{language}"],
                mapped,
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} cross mapping drifted: "
                    f"{language}/{key}/{mapped}"
                )
        if literal_texts(records_by_label["pk_en"], mapped) != ("",):
            raise RuntimeError(
                f"segment {SEGMENT} cross PK EN drifted: {mapped}"
            )


def assert_runtime_graph(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    full_base_ids = {
        record_id
        for record_ids in FULL_TERMINAL_GROUPS.values()
        for record_id in record_ids
    }
    if full_base_ids != set(range(1946, 2016)):
        raise RuntimeError(f"segment {SEGMENT} full group universe drifted")

    for edition, offset in (("base", 0), ("pk", PK_RECORD_OFFSET)):
        target_ids = {record_id + offset for record_id in RECORD_IDS}
        full_ids = {record_id + offset for record_id in full_base_ids}
        for corpus in ("jp", "current"):
            records = records_by_label[f"{edition}_{corpus}"]
            edges = incoming_edges(records, target_ids)
            if (
                len(edges) != len(RECORD_IDS)
                or {edge[2] for edge in edges} != target_ids
                or edge_digest(edges) != SEGMENT_JUMP_EDGE_SHA256[edition]
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {edition}_{corpus} "
                    "terminal edge drifted"
                )
            full_edges = incoming_edges(records, full_ids)
            if (
                len(full_edges) != len(full_ids)
                or {edge[2] for edge in full_edges} != full_ids
                or edge_digest(full_edges)
                != FULL_GROUP_JUMP_EDGE_SHA256[edition]
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {edition}_{corpus} "
                    "full-group edge drifted"
                )

    base_edges = GRAPH.graph_edges(records_by_label["base_jp"])
    pk_edges = GRAPH.graph_edges(records_by_label["pk_jp"])
    full_pk_ids = {
        record_id + PK_RECORD_OFFSET for record_id in full_base_ids
    }
    for base_root, base_record_ids in FULL_TERMINAL_GROUPS.items():
        pk_root = PK_ROOT_BY_BASE[base_root]
        if sorted(
            GRAPH.graph_closure(base_edges, base_root).intersection(
                full_base_ids
            )
        ) != list(base_record_ids):
            raise RuntimeError(
                f"segment {SEGMENT} Base closure drifted: {base_root}"
            )
        if sorted(
            GRAPH.graph_closure(pk_edges, pk_root).intersection(
                full_pk_ids
            )
        ) != [
            record_id + PK_RECORD_OFFSET
            for record_id in base_record_ids
        ]:
            raise RuntimeError(
                f"segment {SEGMENT} PK closure drifted: {pk_root}"
            )

        evidence = ROOT_EVIDENCE[base_root]
        for edition, root, flattened in (
            (
                "base",
                base_root,
                SOURCE_ONLY_FLATTENED_CALLS.get(base_root, ()),
            ),
            (
                "pk",
                pk_root,
                PK_SOURCE_ONLY_FLATTENED_CALLS.get(pk_root, ()),
            ),
        ):
            source_sites = root_call_sites(
                records_by_label[f"{edition}_jp"],
                root,
            )
            current_sites = root_call_sites(
                records_by_label[f"{edition}_current"],
                root,
            )
            for corpus, sites in (
                ("source", source_sites),
                ("current", current_sites),
            ):
                expected_count, expected_sha256 = evidence[
                    f"{edition}_{corpus}"
                ]
                actual_sha256 = hashlib.sha256(
                    "\n".join(sites).encode("ascii")
                ).hexdigest().upper()
                if (
                    len(sites) != expected_count
                    or actual_sha256 != expected_sha256
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} {edition} {corpus} "
                        f"root call drifted: {root}"
                    )
            if set(source_sites) - set(current_sites) != set(flattened):
                raise RuntimeError(
                    f"segment {SEGMENT} {edition} source-only "
                    f"calls drifted: {root}"
                )
            if set(current_sites) - set(source_sites):
                raise RuntimeError(
                    f"segment {SEGMENT} {edition} current-only "
                    f"calls appeared: {root}"
                )

        current_coordinates = {
            site.rsplit(":", 1)[0]
            for site in root_call_sites(
                records_by_label["base_current"],
                base_root,
            )
        }
        examples = set(CURRENT_CALLER_REWRITE_EXAMPLES.get(base_root, {}))
        if not examples.issubset(current_coordinates):
            raise RuntimeError(
                f"segment {SEGMENT} caller example drifted: {base_root}"
            )


def assert_semantics(translations: dict[str, str]) -> None:
    if (
        translations != RAW_TRANSLATIONS
        or len(translations) != 66
        or set(EXPECTED_BASE_JP) != set(RECORD_IDS)
    ):
        raise RuntimeError(f"segment {SEGMENT} translation universe drifted")
    for root, record_ids in FULL_TERMINAL_GROUPS.items():
        actual = tuple(
            (
                translations[f"0:{record_id}:0"]
                if record_id in RECORD_IDS
                else CROSS_SEGMENT_TRANSLATION_POLICY[record_id]
            )
            for record_id in record_ids
        )
        if actual != TRANSLATION_POLICY_BY_ROOT[root]:
            raise RuntimeError(
                f"segment {SEGMENT} register matrix drifted: {root}"
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


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]], str]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    records_by_label = archive_records(prepared)
    assert_corpora(records_by_label)
    assert_runtime_graph(records_by_label)

    current = records_by_label["base_current"]
    translations = dict(RAW_TRANSLATIONS)
    assert_semantics(translations)
    for coordinate, translation in translations.items():
        _, record_id, _ = (int(value) for value in coordinate.split(":"))
        current_text = literal_texts(current, (BLOCK_ID, record_id))[0]
        if not ENGINE.is_visible_translation_candidate(current_text):
            raise RuntimeError(
                f"segment {SEGMENT} target became non-visible: "
                f"{coordinate}"
            )
        if UTIL.layout_signature(translation) != UTIL.layout_signature(
            current_text
        ):
            raise RuntimeError(
                f"segment {SEGMENT} layout signature drifted: "
                f"{coordinate}"
            )

    candidate_sha256 = GENERAL.assert_overlay_roundtrip(
        prepared,
        segment=SEGMENT,
        translations=translations,
        target_records=set(RECORD_KEYS),
    )
    record_to_root = {
        record_id: root
        for root, record_ids in TARGET_TERMINAL_GROUPS.items()
        for record_id in record_ids
    }
    rows: list[dict[str, object]] = []
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        target = prepared.visible_targets[
            ("base_msggame", block_id, record_id, literal_id)
        ]
        root = record_to_root[record_id]
        pk_root = PK_ROOT_BY_BASE[root]
        evidence = ROOT_EVIDENCE[root]
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
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
                    "base_root": root,
                    "pk_semantic_root": pk_root,
                    "base_record_id": record_id,
                    "pk_semantic_record_id": (
                        record_id + PK_RECORD_OFFSET
                    ),
                    "automatic_space_inserted": False,
                    "full_terminal_record_ids": list(
                        FULL_TERMINAL_GROUPS[root]
                    ),
                    "pk_full_terminal_record_ids": [
                        value + PK_RECORD_OFFSET
                        for value in FULL_TERMINAL_GROUPS[root]
                    ],
                    "source_call_count": evidence["base_source"][0],
                    "current_call_count": evidence["base_current"][0],
                    "pk_source_call_count": evidence["pk_source"][0],
                    "pk_current_call_count": evidence["pk_current"][0],
                    "source_only_flattened_calls": list(
                        SOURCE_ONLY_FLATTENED_CALLS.get(root, ())
                    ),
                    "pk_source_only_flattened_calls": list(
                        PK_SOURCE_ONLY_FLATTENED_CALLS.get(pk_root, ())
                    ),
                    "caller_rewrite_examples": (
                        CURRENT_CALLER_REWRITE_EXAMPLES.get(root, {})
                    ),
                    "runtime_integration_required": True,
                },
            }
        )
    return prepared, translations, rows, candidate_sha256


def main() -> int:
    prepared, translations, rows, candidate_sha256 = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(validated) != 66 or len(rows) != 66:
        raise RuntimeError(f"segment {SEGMENT} validation count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime or authority flag drifted"
        )

    current = archive_records(prepared)["base_current"]
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
                "segment": "base_msggame_B004_S1014",
                "queue": QUEUE_BATCH_ID,
                "source_literal_count": 66,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "changed_literal_count": changed,
                "base_pk_semantic_record_offset": PK_RECORD_OFFSET,
                "base_pk_root_shift": 12,
                "base_pk_jp_current_sc_tc_literal_divergence_records": [],
                "base_pk_jp_current_sc_tc_gap_divergence_records": [],
                "pk_en_visible_records": [],
                "full_terminal_groups": {
                    str(root): list(record_ids)
                    for root, record_ids in FULL_TERMINAL_GROUPS.items()
                },
                "pk_root_by_base": PK_ROOT_BY_BASE,
                "cross_segment_translation_policy": (
                    CROSS_SEGMENT_TRANSLATION_POLICY
                ),
                "root_evidence": ROOT_EVIDENCE,
                "source_only_flattened_calls": (
                    SOURCE_ONLY_FLATTENED_CALLS
                ),
                "pk_source_only_flattened_calls": (
                    PK_SOURCE_ONLY_FLATTENED_CALLS
                ),
                "caller_rewrite_examples": (
                    CURRENT_CALLER_REWRITE_EXAMPLES
                ),
                "segment_jump_edge_sha256": (
                    SEGMENT_JUMP_EDGE_SHA256
                ),
                "full_group_jump_edge_sha256": (
                    FULL_GROUP_JUMP_EDGE_SHA256
                ),
                "candidate_sha256": candidate_sha256,
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
                "target_runtime_skeleton_exact": True,
                "protected_signature_exact": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
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
