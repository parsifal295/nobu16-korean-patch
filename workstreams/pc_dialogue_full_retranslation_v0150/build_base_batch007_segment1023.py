#!/usr/bin/env python3
"""Build Base block-0 terminal and block-1 test segment 1023 decisions."""

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

import build_base_batch006_segment1020 as PRIOR


ENGINE = PRIOR.ENGINE
GENERAL = PRIOR.GENERAL
UTIL = PRIOR.UTIL
GRAPH = PRIOR.GRAPH
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B007_S1023.private.v1.jsonl"
)
SEGMENT = 1023
QUEUE_BATCH_ID = "base_msggame-B007"
BLOCK_ID = 0
PK_RECORD_OFFSET = 68

HIDDEN_GROUP_RECORD_IDS = {2570, 2575, 2577, 2582}
RUNTIME_RECORD_IDS = tuple(
    record_id
    for record_id in range(2552, 2611)
    if record_id not in HIDDEN_GROUP_RECORD_IDS
)
RUNTIME_RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RUNTIME_RECORD_IDS)
FULL_GROUP_RECORD_IDS = set(range(2548, 2611))

FULL_TERMINAL_GROUPS = {
    1114: tuple(range(2548, 2555)),
    1120: tuple(range(2555, 2562)),
    1126: tuple(range(2562, 2569)),
    1156: tuple(range(2569, 2576)),
    1162: tuple(range(2576, 2583)),
    1168: tuple(range(2583, 2590)),
    1174: tuple(range(2590, 2597)),
    1180: tuple(range(2597, 2604)),
    1187: tuple(range(2604, 2611)),
}
TARGET_TERMINAL_GROUPS = {
    root: tuple(record_id for record_id in record_ids if record_id in RUNTIME_RECORD_IDS)
    for root, record_ids in FULL_TERMINAL_GROUPS.items()
}
PK_ROOT_BY_BASE = {
    1114: 1126,
    1120: 1132,
    1126: 1138,
    1156: 1168,
    1162: 1174,
    1168: 1180,
    1174: 1186,
    1180: 1192,
    1187: 1198,
}
PK_RECORD_MAP = {
    record_id: record_id + PK_RECORD_OFFSET
    for record_id in FULL_GROUP_RECORD_IDS
}

SOURCE_JP_BY_ROOT = {
    1114: (
        "りましょう",
        "ろう",
        "りましょう",
        "りましょう",
        "りましょう",
        "りましょう",
        "ろう",
    ),
    1120: ("わ", "ぞ", "わ", "ぞ", "わ", "ぞ", "ぞ"),
    1126: (
        "いません",
        "わぬ",
        "いませぬ",
        "いませぬ",
        "いません",
        "いませぬ",
        "わん",
    ),
    1156: ("お", "", "お", "お", "お", "お", ""),
    1162: ("ご", "", "ご", "ご", "ご", "ご", ""),
    1168: (
        "お待ちあれ",
        "待ってくれれ",
        "お待ちあれ",
        "お待ちくだされ",
        "待ってくだされ",
        "待っていただけれ",
        "待ってくれれ",
    ),
    1174: (
        "くだされ",
        "くれ",
        "くだされ",
        "くだされ",
        "いただけれ",
        "いただけれ",
        "くれれ",
    ),
    1180: (
        "御免あそばせ",
        "御免なれ",
        "御免あそばせ",
        "御免なれ",
        "御免あそばせ",
        "御免なれ",
        "失礼する",
    ),
    1187: (
        "いただける",
        "もらえる",
        "いただける",
        "いただける",
        "いただける",
        "いただける",
        "もらえる",
    ),
}
EXPECTED_FULL_BASE_JP = {
    record_id: source
    for root, record_ids in FULL_TERMINAL_GROUPS.items()
    for record_id, source in zip(record_ids, SOURCE_JP_BY_ROOT[root], strict=True)
}
EXPECTED_PK_JP_BY_ROOT = {
    **SOURCE_JP_BY_ROOT,
    1174: (
        "くだされ",
        "くれれ",
        "くだされ",
        "くだされ",
        "いただけれ",
        "いただけれ",
        "くれれ",
    ),
    1187: (
        "いただけ",
        "もらえ",
        "いただけ",
        "いただけ",
        "いただけ",
        "いただけ",
        "もらえ",
    ),
}

# The first matrix is shared with S1022 across the batch boundary. Japanese
# volitional/future callers are mixed, so Korean uses a neutral intention/
# future register matrix and defers caller-specific assembly to integration.
# Roots 1120, 1156, and 1162 are genuine Korean zero morphemes: Japanese
# sentence particles and honorific prefixes have no standalone Korean text.
TRANSLATION_POLICY_BY_ROOT = {
    1114: (
        "겠습니다",
        "겠다",
        "겠사옵니다",
        "겠사옵니다",
        "겠습니다",
        "겠소",
        "겠다",
    ),
    1120: ("", "", "", "", "", "", ""),
    1126: (
        "지 않습니다",
        "지 않는다",
        "지 않사옵니다",
        "지 않사옵니다",
        "지 않습니다",
        "지 않소",
        "지 않는다",
    ),
    1156: ("", "", "", "", "", "", ""),
    1162: ("", "", "", "", "", "", ""),
    1168: (
        "기다려 주시",
        "기다려 주",
        "기다려 주시",
        "기다려 주시",
        "기다려 주시",
        "기다려 주시",
        "기다려 주",
    ),
    1174: ("주시", "주", "주시", "주시", "주시", "주시", "주"),
    1180: (
        "실례하겠습니다",
        "실례하겠네",
        "실례하겠사옵니다",
        "실례하겠사옵니다",
        "실례하겠습니다",
        "실례하겠소",
        "실례하겠다",
    ),
    1187: (
        "주실 수 있습니다",
        "줄 수 있다",
        "주실 수 있사옵니다",
        "주실 수 있사옵니다",
        "주실 수 있습니다",
        "주실 수 있소",
        "줄 수 있다",
    ),
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
RAW_TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": FULL_TRANSLATION_POLICY[record_id]
    for record_id in RUNTIME_RECORD_IDS
}
CROSS_SEGMENT_TRANSLATION_POLICY = {
    record_id: FULL_TRANSLATION_POLICY[record_id]
    for record_id in range(2548, 2552)
}
ZERO_MORPHEME_COORDINATES = {
    coordinate
    for coordinate, translation in RAW_TRANSLATIONS.items()
    if translation == ""
}
ZERO_MORPHEME_KIND_BY_ROOT = {
    1120: "japanese_sentence_final_particle",
    1156: "japanese_honorific_prefix",
    1162: "japanese_honorific_prefix",
}

NONDISPLAY_LITERAL_COUNTS = {4: 5, 5: 4, 6: 2}
NONDISPLAY_COORDINATES = tuple(
    f"1:{record_id}:{literal_id}"
    for record_id, count in NONDISPLAY_LITERAL_COUNTS.items()
    for literal_id in range(count)
)
BLOCK1_RECORD_KEYS = ((1, 2), (1, 4), (1, 5), (1, 6))

BASE_ARCHIVE_KEYS = (
    tuple((BLOCK_ID, record_id) for record_id in range(2552, 2611))
    + BLOCK1_RECORD_KEYS
)
PK_ARCHIVE_KEYS = (
    tuple(
        (BLOCK_ID, record_id + PK_RECORD_OFFSET)
        for record_id in range(2552, 2611)
    )
    + BLOCK1_RECORD_KEYS
)
ARCHIVE_DIGESTS = {
    "base_jp": "97334832443DF142D70C3EBE2FDC4F889547F13679D8057B34AA8DBA1C86FA6C",
    "base_current": "9649626E2B00108A8D445247FEA952886E785C7C605A5DA0947230DE1382466E",
    "base_sc": "FA87CC19DA01CFFD7256191661E841F4FBD0339366FF37FE324E3527D90A7AFD",
    "base_tc": "C38DC3DE8AAC8F4494C485160777B16FEF9AB5349EF40DF7D7BE741F75751B2C",
    "pk_jp": "5037EEDF55889FB9EAD3A7E54111C3A7EA7F5F98F75C1818E7DB902BB74886BD",
    "pk_current": "34A0B5789BF082AFCD0B1F2C6908843190CF4AFF334EF6AFBC44142D173FB88C",
    "pk_sc": "5EA17FB5D089310B050F97924DBC5A72DC9AE0F05CB18386BFF1FC1C48EF3686",
    "pk_tc": "5E14EAEFF35A08B2F109ABF3F5357A3493B8E94D81775E5FDE9E4051A601A4CD",
    "pk_en": "0BE76C4C9E15399F85188F006799500DE68DCFA9E78F5478B4E317884CAE0D1E",
}
HIDDEN_EMPTY_RAW_SHA256 = (
    "0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850"
)
BLOCK1_CONTEXT_RAW_SHA256 = {
    ("base_sc", 4): "41EEF0A4538D9B258CF777FAECC09EA56CE30A1F09B003F6F9F7713A8D9CF6E6",
    ("base_tc", 4): "2A7DDE8876D999BF1FCBD8EDE76AE03D478C21BD10508E8B401BA1FB07D3F81B",
    ("base_sc", 5): HIDDEN_EMPTY_RAW_SHA256,
    ("base_tc", 5): "3D488E5B79B58F57B89CD9E26A51EE18E5601CC29977F8725F72AFEAD6D437D8",
    ("pk_en", 4): HIDDEN_EMPTY_RAW_SHA256,
    ("pk_en", 5): "E37F4B7A398E75F40976D8AC69595851B13D54EBF4305D4DD9EA2AC1399FEB77",
    ("pk_en", 6): HIDDEN_EMPTY_RAW_SHA256,
}

SEGMENT_JUMP_EDGE_EVIDENCE = {
    "base": (
        55,
        "22751CEF2E418B334893ED0A2623E8F9F1245C6EEA0B1C76C888156131F0DA67",
    ),
    "pk": (
        55,
        "7C1643F56442FA0B3B5D393264D73017C018BCBE9B03731818751801C5D3C91E",
    ),
}
FULL_GROUP_JUMP_EDGE_EVIDENCE = {
    "base": (
        63,
        "8E01785F342E84A4438D0499CC68BC5F8DD0B54352CD473DA1900D64B41C62FD",
    ),
    "pk": (
        63,
        "B9092459FA2885AC2D7A5E03096978EFA86A4DA9BFBBEE85257DA42568BF79FC",
    ),
}
AGGREGATE_CALL_EVIDENCE = {
    "base_jp": (
        223,
        125,
        "387A05EABE05063D884D6C908075F698D6E712995B10D0DA5DAB63C4ECF0A0F2",
    ),
    "base_current": (
        182,
        112,
        "BF60665CC5D13EC3D3870662270807541F574BD57E7CC757B3351C87F9B934BF",
    ),
    "pk_jp": (
        392,
        249,
        "CCBDD70F20703E24152A1598E121EC5E52DB6FA9EA6BC67C03709A24A158C4D3",
    ),
    "pk_current": (
        359,
        235,
        "8B2818B08AB6B82D3AC259B29C23BBBF803635A57034A225F919FEC43DD51661",
    ),
}
AGGREGATE_FLATTEN_EVIDENCE = {
    "base": (
        41,
        "C6D03E6E5A1CB940EC2872AE5D630D8AC210E0A7A4310D089027C95DF693350D",
    ),
    "pk": (
        33,
        "2F64542A06F02B37611BACF0DFFECB8511128218E8CDDDE806E433CE84E9BFF7",
    ),
}
CALLER_REWRITE_EXAMPLES = {
    1114: {
        "2:216:1:0": "volitional caller",
        "6:1438:2:0": "future or inference caller",
    },
    1120: {"15:1095:1:6": "Japanese final particle has no Korean surface form"},
    1126: {
        "6:3545:1:0": "kamau negative",
        "6:4379:1:0": "iu negative before a fixed continuation",
    },
    1156: {"2:557:0:0": "honorific o prefix before a verbal noun"},
    1162: {"2:556:1:0": "honorific go prefix before a verbal noun"},
    1168: {"15:255:1:0": "wait request before fixed ba conditional"},
    1174: {"15:252:1:0": "benefactive request before fixed ba conditional"},
    1180: {"15:262:1:0": "apology for interrupting"},
}
PK_CALLER_REWRITE_EXAMPLES = {
    1187: {
        "6:3657:2:0": "benefactive potential before fixed towa",
        "6:4485:2:0": "benefactive potential before fixed reba",
    }
}

BASIS = (
    "review_queue_base_msggame_B007_S1023_pristine_base_pc_jp_sole_"
    "authority_block0_records2552_2611_55_visible_four_hidden_full_"
    "boundary_group2548_2554_plus68_semantic_pk_mapping_roots1114_1187_"
    "exact_unique_tuple_reverse_search_except_record2591_base_kure_pk_"
    "kurere_and_base1187_complete_potential_vs_pk1198_bound_stems_base_"
    "singleton1186_2611_empty_no_calls_014a_terminal_edges_0143_source_"
    "current_calls_flattening_and_fixed_following_digests_mixed_future_"
    "volition_simple_negative_korean_zero_morpheme_sentence_particles_"
    "and_honorific_prefixes_conditional_wait_benefactive_request_apology_"
    "and_benefactive_potential_runtime_caller_rewrite_pending_block1_"
    "records4_6_confirmed_internal_font_grammar_test_by_base_pk_exact_"
    "punctuation_control_skeleton_sc_tc_glyph_fixture_and_pk_en_test_"
    "string_continuity_with_prior_records7_30_classification_no_korean_"
    "authority"
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


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest().upper()


def root_call_sites(
    records: dict[tuple[int, int], Any],
    root: int,
) -> tuple[str, ...]:
    return PRIOR.root_call_sites(records, root)


def fixed_following_blockers(
    records: dict[tuple[int, int], Any],
    root: int,
) -> tuple[str, ...]:
    return PRIOR.fixed_following_blockers(records, root)


def call_payload(
    records: dict[tuple[int, int], Any],
    *,
    pk: bool,
) -> tuple[dict[str, dict[str, tuple[str, ...]]], int, int]:
    payload: dict[str, dict[str, tuple[str, ...]]] = {}
    call_count = 0
    fixed_count = 0
    for root in FULL_TERMINAL_GROUPS:
        actual_root = PK_ROOT_BY_BASE[root] if pk else root
        calls = root_call_sites(records, actual_root)
        fixed = fixed_following_blockers(records, actual_root)
        payload[str(root)] = {"calls": calls, "fixed": fixed}
        call_count += len(calls)
        fixed_count += len(fixed)
    return payload, call_count, fixed_count


def flatten_payload(
    source: dict[tuple[int, int], Any],
    current: dict[tuple[int, int], Any],
    *,
    pk: bool,
) -> tuple[dict[str, tuple[str, ...]], dict[str, tuple[str, ...]]]:
    flattened: dict[str, tuple[str, ...]] = {}
    current_only: dict[str, tuple[str, ...]] = {}
    for root in FULL_TERMINAL_GROUPS:
        actual_root = PK_ROOT_BY_BASE[root] if pk else root
        source_sites = set(root_call_sites(source, actual_root))
        current_sites = set(root_call_sites(current, actual_root))
        flattened[str(root)] = tuple(sorted(source_sites - current_sites))
        current_only[str(root)] = tuple(sorted(current_sites - source_sites))
    return flattened, current_only


def assert_block1_test_fixture(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    for label, records in records_by_label.items():
        if hashlib.sha256(records[(1, 2)].data).hexdigest().upper() != HIDDEN_EMPTY_RAW_SHA256:
            raise RuntimeError(f"segment {SEGMENT} block1 hidden record drifted: {label}")

    expected_literals = {
        4: ("、", "、", "、", "、", "、"),
        5: ("、", "、", "、", "、"),
        6: ("、", "、"),
    }
    expected_gaps = {
        4: ("026E32", "026E33", "026E34", "026E35", "026E36", "026E37050505"),
        5: (
            "014301000000",
            "014308000000",
            "014344000000",
            "014345000000",
            "050505",
        ),
        6: ("024633", "024634", "024635050505"),
    }
    for record_id in NONDISPLAY_LITERAL_COUNTS:
        for label in ("base_jp", "base_current", "pk_jp", "pk_current"):
            record = records_by_label[label][(1, record_id)]
            if (
                literal_texts(records_by_label[label], (1, record_id))
                != expected_literals[record_id]
                or tuple(gap.hex().upper() for gap in gap_bytes(record))
                != expected_gaps[record_id]
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} block1 punctuation fixture drifted: "
                    f"{label}/{record_id}"
                )
        for language in ("jp", "current", "sc", "tc"):
            if (
                records_by_label[f"base_{language}"][(1, record_id)].data
                != records_by_label[f"pk_{language}"][(1, record_id)].data
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} block1 Base/PK drifted: "
                    f"{language}/{record_id}"
                )

    for (label, record_id), expected in BLOCK1_CONTEXT_RAW_SHA256.items():
        actual = hashlib.sha256(
            records_by_label[label][(1, record_id)].data
        ).hexdigest().upper()
        if actual != expected:
            raise RuntimeError(
                f"segment {SEGMENT} block1 context drifted: {label}/{record_id}"
            )
    if literal_texts(records_by_label["pk_en"], (1, 5)) != ("test string",):
        raise RuntimeError(f"segment {SEGMENT} block1 test-string evidence drifted")


def assert_corpora(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    for label, records in records_by_label.items():
        keys = PK_ARCHIVE_KEYS if label.startswith("pk_") else BASE_ARCHIVE_KEYS
        if GENERAL.subset_digest(records, keys) != ARCHIVE_DIGESTS[label]:
            raise RuntimeError(f"segment {SEGMENT} {label} corpus drifted")

    for label in ("base_jp", "base_current", "base_sc", "base_tc"):
        singleton = records_by_label[label][(BLOCK_ID, 2611)]
        if (
            hashlib.sha256(singleton.data).hexdigest().upper()
            != HIDDEN_EMPTY_RAW_SHA256
            or literal_texts(records_by_label[label], (BLOCK_ID, 2611)) != ("",)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base singleton 2611 drifted: {label}"
            )

    literal_divergences = {
        "jp": {2591, *range(2604, 2611)},
        "current": {2591, *range(2604, 2611)},
        "sc": set(),
        "tc": set(),
    }
    for root, record_ids in FULL_TERMINAL_GROUPS.items():
        for ordinal, record_id in enumerate(record_ids):
            base_key = (BLOCK_ID, record_id)
            pk_key = (BLOCK_ID, PK_RECORD_MAP[record_id])
            if literal_texts(records_by_label["base_jp"], base_key) != (
                EXPECTED_FULL_BASE_JP[record_id],
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base JP drifted: {record_id}"
                )
            if literal_texts(records_by_label["pk_jp"], pk_key) != (
                EXPECTED_PK_JP_BY_ROOT[root][ordinal],
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} PK JP drifted: {record_id}"
                )
            for language in ("jp", "current", "sc", "tc"):
                base_records = records_by_label[f"base_{language}"]
                pk_records = records_by_label[f"pk_{language}"]
                is_divergent = record_id in literal_divergences[language]
                if (
                    (
                        literal_texts(base_records, base_key)
                        != literal_texts(pk_records, pk_key)
                    )
                    != is_divergent
                    or gap_bytes(base_records[base_key]) != gap_bytes(pk_records[pk_key])
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} Base/PK divergence drifted: "
                        f"{language}/{record_id}"
                    )
            if literal_texts(records_by_label["pk_en"], pk_key) != ("",):
                raise RuntimeError(
                    f"segment {SEGMENT} grammar PK EN drifted: {record_id}"
                )
            for label, key in (
                ("base_jp", base_key),
                ("base_current", base_key),
                ("base_sc", base_key),
                ("base_tc", base_key),
                ("pk_jp", pk_key),
                ("pk_current", pk_key),
                ("pk_sc", pk_key),
                ("pk_tc", pk_key),
                ("pk_en", pk_key),
            ):
                if (
                    len(literal_texts(records_by_label[label], key)) != 1
                    or gap_bytes(records_by_label[label][key])
                    != (b"", b"\x05\x05\x05")
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} grammar skeleton drifted: "
                        f"{label}/{record_id}"
                    )

    pk_jp = records_by_label["pk_jp"]
    max_pk_record_id = max(
        record_id for block_id, record_id in pk_jp if block_id == BLOCK_ID
    )
    for root, record_ids in FULL_TERMINAL_GROUPS.items():
        if root in {1174, 1187}:
            continue
        expected = tuple(
            (EXPECTED_FULL_BASE_JP[record_id],) for record_id in record_ids
        )
        hits = [
            start
            for start in range(max_pk_record_id - 5)
            if all((BLOCK_ID, start + ordinal) in pk_jp for ordinal in range(7))
            and tuple(
                literal_texts(pk_jp, (BLOCK_ID, start + ordinal))
                for ordinal in range(7)
            )
            == expected
        ]
        expected_start = record_ids[0] + PK_RECORD_OFFSET
        if hits != [expected_start]:
            raise RuntimeError(
                f"segment {SEGMENT} PK tuple mapping drifted: {root}"
            )

    assert_block1_test_fixture(records_by_label)


def assert_runtime_graph(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if {
        record_id
        for record_ids in FULL_TERMINAL_GROUPS.values()
        for record_id in record_ids
    } != FULL_GROUP_RECORD_IDS:
        raise RuntimeError(f"segment {SEGMENT} full group universe drifted")

    target_ids = set(RUNTIME_RECORD_IDS)
    for edition, offset in (("base", 0), ("pk", PK_RECORD_OFFSET)):
        for corpus in ("jp", "current"):
            records = records_by_label[f"{edition}_{corpus}"]
            for ids, evidence, label in (
                (target_ids, SEGMENT_JUMP_EDGE_EVIDENCE[edition], "target"),
                (
                    FULL_GROUP_RECORD_IDS,
                    FULL_GROUP_JUMP_EDGE_EVIDENCE[edition],
                    "full",
                ),
            ):
                mapped_ids = {record_id + offset for record_id in ids}
                edges = PRIOR.PRIOR.PRIOR.incoming_edges(records, mapped_ids)
                if (
                    len(edges) != evidence[0]
                    or {edge[2] for edge in edges} != mapped_ids
                    or PRIOR.PRIOR.PRIOR.edge_digest(edges) != evidence[1]
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} {edition}_{corpus} "
                        f"{label} edge drifted"
                    )

    base_edges = GRAPH.graph_edges(records_by_label["base_jp"])
    pk_edges = GRAPH.graph_edges(records_by_label["pk_jp"])
    for root, record_ids in FULL_TERMINAL_GROUPS.items():
        if sorted(
            GRAPH.graph_closure(base_edges, root).intersection(FULL_GROUP_RECORD_IDS)
        ) != list(record_ids):
            raise RuntimeError(
                f"segment {SEGMENT} Base closure drifted: {root}"
            )
        pk_ids = {
            record_id + PK_RECORD_OFFSET for record_id in FULL_GROUP_RECORD_IDS
        }
        if sorted(
            GRAPH.graph_closure(pk_edges, PK_ROOT_BY_BASE[root]).intersection(pk_ids)
        ) != [record_id + PK_RECORD_OFFSET for record_id in record_ids]:
            raise RuntimeError(
                f"segment {SEGMENT} PK closure drifted: {root}"
            )
    if (
        sorted(GRAPH.graph_closure(base_edges, 1186)) != [1186, 2611]
        or root_call_sites(records_by_label["base_jp"], 1186)
        or root_call_sites(records_by_label["base_current"], 1186)
    ):
        raise RuntimeError(f"segment {SEGMENT} Base singleton root drifted")


def assert_call_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    for label, expected in AGGREGATE_CALL_EVIDENCE.items():
        payload, call_count, fixed_count = call_payload(
            records_by_label[label],
            pk=label.startswith("pk_"),
        )
        if (
            call_count != expected[0]
            or fixed_count != expected[1]
            or canonical_sha256(payload) != expected[2]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} call evidence drifted"
            )

    for edition in ("base", "pk"):
        flattened, current_only = flatten_payload(
            records_by_label[f"{edition}_jp"],
            records_by_label[f"{edition}_current"],
            pk=edition == "pk",
        )
        expected = AGGREGATE_FLATTEN_EVIDENCE[edition]
        if (
            sum(len(sites) for sites in flattened.values()) != expected[0]
            or canonical_sha256(flattened) != expected[1]
            or any(current_only.values())
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {edition} flattening drifted"
            )

    source_calls = {
        root: set(root_call_sites(records_by_label["base_jp"], root))
        for root in FULL_TERMINAL_GROUPS
    }
    for root, examples in CALLER_REWRITE_EXAMPLES.items():
        if not set(examples).issubset(source_calls[root]):
            raise RuntimeError(
                f"segment {SEGMENT} Base caller example drifted: {root}"
            )
    for root, examples in PK_CALLER_REWRITE_EXAMPLES.items():
        if not set(examples).issubset(
            root_call_sites(records_by_label["pk_jp"], PK_ROOT_BY_BASE[root])
        ):
            raise RuntimeError(
                f"segment {SEGMENT} PK caller example drifted: {root}"
            )


def assert_semantics(translations: dict[str, str]) -> None:
    if translations != RAW_TRANSLATIONS or len(translations) != 55:
        raise RuntimeError(f"segment {SEGMENT} translation universe drifted")
    for root, record_ids in FULL_TERMINAL_GROUPS.items():
        actual = tuple(
            (
                translations[f"0:{record_id}:0"]
                if record_id in RUNTIME_RECORD_IDS
                else CROSS_SEGMENT_TRANSLATION_POLICY.get(record_id, "")
            )
            for record_id in record_ids
        )
        if actual != TRANSLATION_POLICY_BY_ROOT[root]:
            raise RuntimeError(
                f"segment {SEGMENT} register matrix drifted: {root}"
            )
    if (
        len(ZERO_MORPHEME_COORDINATES) != 17
        or translations["0:2552:0"] != "겠습니다"
        or translations["0:2562:0"] != "지 않습니다"
        or translations["0:2583:0"] != "기다려 주시"
        or translations["0:2590:0"] != "주시"
        or translations["0:2597:0"] != "실례하겠습니다"
        or translations["0:2604:0"] != "주실 수 있습니다"
    ):
        raise RuntimeError(f"segment {SEGMENT} semantic policy drifted")
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


def assert_empty_runtime_morpheme_gate() -> None:
    try:
        ENGINE.validate_translation_shape(
            "와",
            "",
            "unchanged_from_current",
            "ordinary_blank_probe",
        )
    except ENGINE.RetranslationError:
        pass
    else:
        raise RuntimeError(
            f"segment {SEGMENT} ordinary blank replacement gate drifted"
        )
    ENGINE.validate_translation_shape(
        "와",
        "",
        "unchanged_from_current",
        "zero_morpheme_probe",
        allow_empty_runtime_morpheme=True,
    )
    try:
        ENGINE.validate_translation_shape(
            "와",
            "와",
            "unchanged_from_current",
            "nonempty_zero_morpheme_probe",
            allow_empty_runtime_morpheme=True,
        )
    except ENGINE.RetranslationError:
        pass
    else:
        raise RuntimeError(
            f"segment {SEGMENT} zero morpheme exact-empty gate drifted"
        )


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]], str]:
    assert_empty_runtime_morpheme_gate()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    records_by_label = archive_records(prepared)
    assert_corpora(records_by_label)
    assert_runtime_graph(records_by_label)
    assert_call_evidence(records_by_label)

    current = records_by_label["base_current"]
    translations = dict(RAW_TRANSLATIONS)
    assert_semantics(translations)
    for coordinate, translation in translations.items():
        _, record_id, _ = (int(value) for value in coordinate.split(":"))
        current_text = literal_texts(current, (BLOCK_ID, record_id))[0]
        if not ENGINE.is_visible_translation_candidate(current_text):
            raise RuntimeError(
                f"segment {SEGMENT} target became non-visible: {coordinate}"
            )
        if UTIL.layout_signature(translation) != UTIL.layout_signature(current_text):
            raise RuntimeError(
                f"segment {SEGMENT} layout signature drifted: {coordinate}"
            )

    candidate_sha256 = GENERAL.assert_overlay_roundtrip(
        prepared,
        segment=SEGMENT,
        translations=translations,
        target_records=set(RUNTIME_RECORD_KEYS),
    )
    record_to_root = {
        record_id: root
        for root, record_ids in TARGET_TERMINAL_GROUPS.items()
        for record_id in record_ids
    }
    call_cache = {
        (edition, corpus, root): root_call_sites(
            records_by_label[f"{edition}_{corpus}"],
            PK_ROOT_BY_BASE[root] if edition == "pk" else root,
        )
        for edition in ("base", "pk")
        for corpus in ("jp", "current")
        for root in FULL_TERMINAL_GROUPS
    }
    rows: list[dict[str, object]] = []
    for coordinate, translation in translations.items():
        _, record_id, _ = (int(value) for value in coordinate.split(":"))
        target = prepared.visible_targets[
            ("base_msggame", BLOCK_ID, record_id, 0)
        ]
        root = record_to_root[record_id]
        row: dict[str, object] = {
            "schema": ENGINE.DECISION_SCHEMA,
            "resource": "base_msggame",
            "coordinate": coordinate,
            "source_record_raw_sha256": target["source_record_raw_sha256"],
            "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
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
                "pk_semantic_root": PK_ROOT_BY_BASE[root],
                "base_record_id": record_id,
                "pk_semantic_record_id": record_id + PK_RECORD_OFFSET,
                "automatic_space_inserted": False,
                "full_terminal_record_ids": list(FULL_TERMINAL_GROUPS[root]),
                "pk_full_terminal_record_ids": [
                    value + PK_RECORD_OFFSET
                    for value in FULL_TERMINAL_GROUPS[root]
                ],
                "source_call_count": len(call_cache[("base", "jp", root)]),
                "current_call_count": len(
                    call_cache[("base", "current", root)]
                ),
                "pk_source_call_count": len(call_cache[("pk", "jp", root)]),
                "pk_current_call_count": len(
                    call_cache[("pk", "current", root)]
                ),
                "caller_rewrite_examples": CALLER_REWRITE_EXAMPLES.get(root, {}),
                "pk_caller_rewrite_examples": PK_CALLER_REWRITE_EXAMPLES.get(
                    root, {}
                ),
                "runtime_integration_required": True,
            },
        }
        if coordinate in ZERO_MORPHEME_COORDINATES:
            row["empty_runtime_morpheme"] = True
            row["empty_runtime_morpheme_kind"] = ZERO_MORPHEME_KIND_BY_ROOT[
                root
            ]
            assembly_evidence = row["runtime_assembly_evidence"]
            if not isinstance(assembly_evidence, dict):
                raise RuntimeError(
                    f"segment {SEGMENT} runtime assembly evidence drifted"
                )
            assembly_evidence["empty_runtime_morpheme_source_jp"] = (
                EXPECTED_FULL_BASE_JP[record_id]
            )
            assembly_evidence["korean_zero_morpheme_caller_review"] = (
                "approved"
            )
        rows.append(row)

    for coordinate in NONDISPLAY_COORDINATES:
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        target = prepared.visible_targets[
            ("base_msggame", block_id, record_id, literal_id)
        ]
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target[
                    "current_ko_utf16le_sha256"
                ],
                "semantic_review": "approved",
                "scope_classification": "confirmed_non_display",
                "layout_review": "not_needed",
                "runtime_review": "not_required",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
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
    if (
        sum(
            row["scope_classification"] == "runtime_fragment_pending"
            for row in rows
        )
        != 55
        or sum(
            row["scope_classification"] == "confirmed_non_display"
            for row in rows
        )
        != 11
        or sum(row.get("empty_runtime_morpheme") is True for row in rows)
        != 17
        or any(
            row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            for row in rows
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} classification or authority flag drifted"
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
    if changed != 55:
        raise RuntimeError(f"segment {SEGMENT} changed count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B007_S1023",
                "queue": QUEUE_BATCH_ID,
                "source_literal_count": 66,
                "decision_count": len(rows),
                "runtime_fragment_pending": 55,
                "confirmed_non_display": 11,
                "empty_runtime_morpheme": 17,
                "changed_literal_count": changed,
                "base_pk_semantic_record_offset": PK_RECORD_OFFSET,
                "base_pk_jp_current_literal_divergence_records": [
                    2591,
                    *range(2604, 2611),
                ],
                "base_pk_sc_tc_gap_divergence_records": [],
                "pk_en_visible_records": ["1:5"],
                "full_terminal_groups": {
                    str(root): list(record_ids)
                    for root, record_ids in FULL_TERMINAL_GROUPS.items()
                },
                "pk_root_by_base": PK_ROOT_BY_BASE,
                "cross_segment_translation_policy": (
                    CROSS_SEGMENT_TRANSLATION_POLICY
                ),
                "aggregate_call_evidence": AGGREGATE_CALL_EVIDENCE,
                "aggregate_flatten_evidence": AGGREGATE_FLATTEN_EVIDENCE,
                "segment_jump_edge_evidence": SEGMENT_JUMP_EDGE_EVIDENCE,
                "full_group_jump_edge_evidence": (
                    FULL_GROUP_JUMP_EDGE_EVIDENCE
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
