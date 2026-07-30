#!/usr/bin/env python3
"""Build Base block-0 runtime-terminal segment 1020 decisions."""

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

import build_base_batch005_segment1017 as PRIOR


ENGINE = PRIOR.ENGINE
GENERAL = PRIOR.GENERAL
UTIL = PRIOR.UTIL
GRAPH = PRIOR.GRAPH
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B006_S1020.private.v1.jsonl"
)
SEGMENT = 1020
QUEUE_BATCH_ID = "base_msggame-B006"
BLOCK_ID = 0
RECORD_IDS = tuple(range(2353, 2419))
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
PK_RECORD_OFFSET = 68
PK_ROOT_SHIFT = 12

FULL_TERMINAL_GROUPS = {
    946: tuple(range(2352, 2359)),
    952: tuple(range(2359, 2366)),
    958: tuple(range(2366, 2373)),
    964: tuple(range(2373, 2380)),
    970: tuple(range(2380, 2387)),
    976: tuple(range(2387, 2394)),
    982: tuple(range(2394, 2401)),
    988: tuple(range(2401, 2408)),
    994: tuple(range(2408, 2415)),
    1000: tuple(range(2415, 2422)),
}
TARGET_TERMINAL_GROUPS = {
    root: tuple(
        record_id for record_id in record_ids if record_id in RECORD_IDS
    )
    for root, record_ids in FULL_TERMINAL_GROUPS.items()
}
PK_ROOT_BY_BASE = {
    root: root + PK_ROOT_SHIFT for root in FULL_TERMINAL_GROUPS
}
PK_RECORD_MAP = {
    (BLOCK_ID, record_id): (
        BLOCK_ID,
        record_id + PK_RECORD_OFFSET,
    )
    for record_id in range(2352, 2422)
}

SOURCE_JP_BY_ROOT = {
    946: (
        "お命じください",
        "命じてくれ",
        "お命じください",
        "お命じくだされ",
        "命じてください",
        "命じてくだされ",
        "命じてくれ",
    ),
    952: (
        "めません",
        "めぬ",
        "めませぬ",
        "めませぬ",
        "めません",
        "めませぬ",
        "めん",
    ),
    958: ("もう", "もはや", "もはや", "もはや", "もう", "もう", "もう"),
    964: (
        "みましょう",
        "もう",
        "みましょう",
        "みましょう",
        "みましょう",
        "みましょう",
        "もう",
    ),
    970: (
        "いただきます",
        "もらう",
        "いただきます",
        "いただきます",
        "もらいます",
        "いただく",
        "もらう",
    ),
    976: (
        "いただきましょう",
        "もらおう",
        "いただきましょう",
        "いただきましょう",
        "もらいましょう",
        "いただこう",
        "もらおう",
    ),
    982: (
        "いただきました",
        "もらった",
        "いただきました",
        "いただきました",
        "もらいました",
        "いただいた",
        "もらった",
    ),
    988: (
        "いただきまして",
        "もらって",
        "いただきまして",
        "いただきまして",
        "もらいまして",
        "いただいて",
        "もらって",
    ),
    994: ("お人", "お人", "御仁", "御仁", "お人", "お人", "奴"),
    1000: (
        "あげました",
        "やった",
        "さしあげました",
        "やりました",
        "あげました",
        "やりました",
        "やった",
    ),
}
CURRENT_KO_BY_ROOT = {
    946: (
        "명하여 주십시오",
        "명령해 다오",
        "명하여 주십시오",
        "명하여 주시게",
        "명령해 주십시오",
        "명령을 내려 주소서",
        "명령해 다오",
    ),
    952: (
        "못합니다",
        "못하다",
        "못합니다",
        "못합니다",
        "못합니다",
        "못합니다",
        "못",
    ),
    958: ("이제", "이제", "이제", "이제", "이제", "이제", "이제"),
    964: (
        "봅시다",
        "이제",
        "봅시다",
        "봅시다",
        "봅시다",
        "봅시다",
        "이제",
    ),
    970: (
        "받습니다",
        "받는다",
        "받습니다",
        "받습니다",
        "받습니다",
        "받다",
        "받는다",
    ),
    976: (
        "받겠습니다",
        "받자",
        "받겠습니다",
        "받겠습니다",
        "받읍시다",
        "받겠다",
        "받자",
    ),
    982: (
        "받았습니다",
        "받았다",
        "받았습니다",
        "받았습니다",
        "받았습니다",
        "받았다",
        "받았다",
    ),
    988: (
        "받고서",
        "받아서",
        "받고서",
        "받고서",
        "받아서",
        "받고",
        "받아서",
    ),
    994: ("사람", "사람", "어른", "어른", "사람", "사람", "놈"),
    1000: (
        "주었습니다",
        "해냈다",
        "드렸습니다",
        "해냈습니다",
        "주었습니다",
        "해냈습니다",
        "해냈다",
    ),
}
TRANSLATION_POLICY_BY_ROOT = {
    946: (
        "명해 주십시오",
        "명해 다오",
        "명해 주십시오",
        "명해 주시오",
        "명해 주십시오",
        "명해 주시오",
        "명해 다오",
    ),
    952: (
        "지 못합니다",
        "지 못한다",
        "지 못하옵니다",
        "지 못하옵니다",
        "지 못합니다",
        "지 못하옵니다",
        "지 못한다",
    ),
    958: ("더는", "더는", "더는", "더는", "더는", "더는", "더는"),
    964: (
        "합시다",
        "하자",
        "합시다",
        "합시다",
        "합시다",
        "합시다",
        "하자",
    ),
    970: (
        "하겠습니다",
        "하겠다",
        "하겠사옵니다",
        "하겠사옵니다",
        "하겠습니다",
        "하겠소",
        "하겠다",
    ),
    976: (
        "받겠습니다",
        "받자",
        "받겠사옵니다",
        "받겠사옵니다",
        "받읍시다",
        "받겠소",
        "받자",
    ),
    982: (
        "받았습니다",
        "받았다",
        "받았사옵니다",
        "받았사옵니다",
        "받았습니다",
        "받았소",
        "받았다",
    ),
    988: CURRENT_KO_BY_ROOT[988],
    994: ("분", "분", "분", "분", "분", "분", "놈"),
    1000: (
        "주었습니다",
        "주었다",
        "드렸습니다",
        "주었습니다",
        "주었습니다",
        "주었습니다",
        "주었다",
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
EXPECTED_FULL_CURRENT_KO = {
    record_id: current
    for root, record_ids in FULL_TERMINAL_GROUPS.items()
    for record_id, current in zip(
        record_ids,
        CURRENT_KO_BY_ROOT[root],
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
TRANSLATIONS_BY_RECORD = {
    record_id: FULL_TRANSLATION_POLICY[record_id]
    for record_id in RECORD_IDS
}
RAW_TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}
CROSS_SEGMENT_TRANSLATION_POLICY = {
    2352: FULL_TRANSLATION_POLICY[2352],
    2419: FULL_TRANSLATION_POLICY[2419],
    2420: FULL_TRANSLATION_POLICY[2420],
    2421: FULL_TRANSLATION_POLICY[2421],
}

ARCHIVE_DIGESTS = {
    "base_jp": "025EFDD1BD4DB5FB2D9792226F711B79E39BDEA76D072897260E0368FE515CFB",
    "base_current": "68F24EDD06B7B76A6950A5ABEF0B18045EA5754EA58E340618055BEE28649E2E",
    "base_sc": "1B099E880CCDEC8F66FAB0238D1B5E2E1D88C5510CC3F98B969ED35D37E00FAC",
    "base_tc": "1B099E880CCDEC8F66FAB0238D1B5E2E1D88C5510CC3F98B969ED35D37E00FAC",
    "pk_jp": "8B780412E8177012C96FBFED0C35ED73BA10EAB68B7275145A538CDA01EBD8DB",
    "pk_current": "8F55E5358433EEC16BE8E9038778CDA5D355A48C2FCCC960C29A7377EDC9AAD1",
    "pk_sc": "8E208F231A4FD4F98550E2911A4E861C8E6CA694784527BB988D464531729D54",
    "pk_tc": "8E208F231A4FD4F98550E2911A4E861C8E6CA694784527BB988D464531729D54",
    "pk_en": "8E208F231A4FD4F98550E2911A4E861C8E6CA694784527BB988D464531729D54",
}
SEGMENT_JUMP_EDGE_EVIDENCE = {
    "base": (
        66,
        "6AE1137641712FD648EE2968202A7AFF058CDE9C21A3214336C69207F8BB2576",
    ),
    "pk": (
        66,
        "95853A7CD0710D41508D58CC4B15ED66CC7F55BBBDCB52D7E06EEB8156E202A4",
    ),
}
FULL_GROUP_JUMP_EDGE_EVIDENCE = {
    "base": (
        70,
        "C25D3B5B422C4EECCB5122752943687A17D9FBD169C9FB678FDF1D89A33D8574",
    ),
    "pk": (
        70,
        "3EE77BFE5E30EB7AA2347360CB99088184F86F8A3BFCBB72066601E89948283E",
    ),
}
AGGREGATE_CALL_EVIDENCE = {
    "base_jp": (
        51,
        6,
        "796920535D7C5756C41B70A9FA1E9D3219F47CFC78DC50CF77A72433F8506B4D",
    ),
    "base_current": (
        49,
        6,
        "8610547A2661DD085252D4F53781DCE46DB06A967457E933EA720CFAE314C3AC",
    ),
    "pk_jp": (
        59,
        6,
        "34034EFCE4A08503E15C692354504073837A96E93E57D748CCAB9BC6F6A9E533",
    ),
    "pk_current": (
        56,
        6,
        "6062C4C2D3189476205FF67D93C7C19199984643DAA2B8AF0DC5416183E7DB01",
    ),
}
AGGREGATE_FLATTEN_EVIDENCE = {
    "base": (
        2,
        "020735B326679B4DD31E0C88EDA540749FFCEEA97E034165F773F4C3617FB370",
    ),
    "pk": (
        3,
        "8674AB0FEFF40E6C377964C743AFD53DB2854104537A1425C8D0E21897073F19",
    ),
}
CALLER_REWRITE_EXAMPLES = {
    946: {
        "7:2397:1:0": "action object requires a complete command terminal",
    },
    952: {
        "1:22:1:0": "바라 stem requires a productive inability terminal",
    },
    958: {
        "1:22:2:0": "negative context means 더는, not temporal 이제",
    },
    964: {
        "2:543:2:0": "잡 stem requires contextual volitional assembly",
        "8:1016:2:0": "fixed following interrogative requires joint rewriting",
    },
    970: {
        "6:2155:2:0": "させてもらう expresses permitted intention, not receipt",
        "7:330:2:0": "refusal intention requires a complete Korean ending",
    },
    976: {
        "1:19:2:0": "achievement recipient requires lexical receive semantics",
        "13:110:2:0": "benefactive request was flattened in current Korean",
    },
    982: {
        "6:4149:1:0": "fixed following 城 requires an attributive receive form",
    },
    994: {
        "15:1461:1:0": "honorific person noun is predicative before the line break",
    },
    1000: {
        "8:954:1:0": "weakening boast uses benefactive やる, not accomplishment",
    },
}

BASIS = (
    "review_queue_base_msggame_B006_S1020_pristine_base_pc_jp_sole_"
    "authority_block0_records2353_2418_66_visible_full_boundary_groups_"
    "2352_2421_exact_unique_seven_literal_tuple_reverse_search_pk_plus68_"
    "roots946_1000_pk_plus12_jp_current_sc_tc_exact_pk_en_empty_archive_"
    "digests_014a_terminal_edges_0143_source_current_calls_flattening_"
    "and_fixed_following_aggregate_digests_command_inability_negative_"
    "adverb_volitional_permission_intention_receive_benefactive_person_"
    "honorific_and_yaru_semantics_runtime_caller_rewrite_pending_one_"
    "line_reverse_overlay_no_korean_authority"
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
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest().upper()


def root_call_sites(
    records: dict[tuple[int, int], Any],
    root: int,
) -> tuple[str, ...]:
    return PRIOR.PRIOR.root_call_sites(records, root)


def fixed_following_blockers(
    records: dict[tuple[int, int], Any],
    root: int,
) -> tuple[str, ...]:
    return PRIOR.FIXED.fixed_following_blockers(records, root)


def call_payload(
    records: dict[tuple[int, int], Any],
    *,
    pk: bool,
) -> tuple[dict[str, dict[str, tuple[str, ...]]], int, int]:
    payload: dict[str, dict[str, tuple[str, ...]]] = {}
    call_count = 0
    fixed_count = 0
    for root in FULL_TERMINAL_GROUPS:
        actual_root = root + (PK_ROOT_SHIFT if pk else 0)
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
        actual_root = root + (PK_ROOT_SHIFT if pk else 0)
        source_sites = set(root_call_sites(source, actual_root))
        current_sites = set(root_call_sites(current, actual_root))
        flattened[str(root)] = tuple(sorted(source_sites - current_sites))
        current_only[str(root)] = tuple(sorted(current_sites - source_sites))
    return flattened, current_only


def assert_corpora(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    for label, records in records_by_label.items():
        keys = tuple(
            (
                BLOCK_ID,
                record_id
                + (PK_RECORD_OFFSET if label.startswith("pk_") else 0),
            )
            for record_id in RECORD_IDS
        )
        if GENERAL.subset_digest(records, keys) != ARCHIVE_DIGESTS[label]:
            raise RuntimeError(f"segment {SEGMENT} {label} corpus drifted")

    for record_id in range(2352, 2422):
        key = (BLOCK_ID, record_id)
        mapped = PK_RECORD_MAP[key]
        if literal_texts(records_by_label["base_jp"], key) != (
            EXPECTED_FULL_BASE_JP[record_id],
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base JP drifted: {record_id}"
            )
        if literal_texts(records_by_label["base_current"], key) != (
            EXPECTED_FULL_CURRENT_KO[record_id],
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base current drifted: {record_id}"
            )
        for language in ("jp", "current", "sc", "tc"):
            base_records = records_by_label[f"base_{language}"]
            pk_records = records_by_label[f"pk_{language}"]
            if (
                literal_texts(base_records, key)
                != literal_texts(pk_records, mapped)
                or gap_bytes(base_records[key]) != gap_bytes(pk_records[mapped])
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base/PK drifted: "
                    f"{language}/{record_id}"
                )
        if (
            literal_texts(records_by_label["base_sc"], key) != ("",)
            or literal_texts(records_by_label["base_tc"], key) != ("",)
            or literal_texts(records_by_label["pk_en"], mapped) != ("",)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} contextual corpus drifted: {record_id}"
            )
        for label, actual_key in (
            ("base_jp", key),
            ("base_current", key),
            ("base_sc", key),
            ("base_tc", key),
            ("pk_jp", mapped),
            ("pk_current", mapped),
            ("pk_sc", mapped),
            ("pk_tc", mapped),
            ("pk_en", mapped),
        ):
            if (
                len(literal_texts(records_by_label[label], actual_key)) != 1
                or gap_bytes(records_by_label[label][actual_key])
                != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} full boundary skeleton drifted: "
                    f"{label}/{record_id}"
                )

    pk_jp = records_by_label["pk_jp"]
    max_pk_record_id = max(
        record_id for block_id, record_id in pk_jp if block_id == BLOCK_ID
    )
    for root, record_ids in FULL_TERMINAL_GROUPS.items():
        expected = tuple(
            (EXPECTED_FULL_BASE_JP[record_id],) for record_id in record_ids
        )
        hits = [
            start
            for start in range(max_pk_record_id - 5)
            if all(
                (BLOCK_ID, start + ordinal) in pk_jp
                for ordinal in range(7)
            )
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


def assert_runtime_graph(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    full_ids = {
        record_id
        for record_ids in FULL_TERMINAL_GROUPS.values()
        for record_id in record_ids
    }
    if full_ids != set(range(2352, 2422)):
        raise RuntimeError(f"segment {SEGMENT} full universe drifted")

    for edition, offset in (("base", 0), ("pk", PK_RECORD_OFFSET)):
        for corpus in ("jp", "current"):
            records = records_by_label[f"{edition}_{corpus}"]
            for ids, evidence, label in (
                (
                    set(RECORD_IDS),
                    SEGMENT_JUMP_EDGE_EVIDENCE[edition],
                    "target",
                ),
                (
                    full_ids,
                    FULL_GROUP_JUMP_EDGE_EVIDENCE[edition],
                    "full",
                ),
            ):
                mapped_ids = {record_id + offset for record_id in ids}
                edges = PRIOR.PRIOR.incoming_edges(records, mapped_ids)
                if (
                    len(edges) != evidence[0]
                    or {edge[2] for edge in edges} != mapped_ids
                    or PRIOR.PRIOR.edge_digest(edges) != evidence[1]
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} {edition}_{corpus} "
                        f"{label} edge drifted"
                    )

    base_edges = GRAPH.graph_edges(records_by_label["base_jp"])
    pk_edges = GRAPH.graph_edges(records_by_label["pk_jp"])
    for root, record_ids in FULL_TERMINAL_GROUPS.items():
        if sorted(
            GRAPH.graph_closure(base_edges, root).intersection(full_ids)
        ) != list(record_ids):
            raise RuntimeError(
                f"segment {SEGMENT} Base closure drifted: {root}"
            )
        pk_ids = {record_id + PK_RECORD_OFFSET for record_id in full_ids}
        if sorted(
            GRAPH.graph_closure(
                pk_edges,
                PK_ROOT_BY_BASE[root],
            ).intersection(pk_ids)
        ) != [
            record_id + PK_RECORD_OFFSET for record_id in record_ids
        ]:
            raise RuntimeError(
                f"segment {SEGMENT} PK closure drifted: {root}"
            )


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
                f"segment {SEGMENT} caller example drifted: {root}"
            )


def assert_semantics(translations: dict[str, str]) -> None:
    if (
        translations != RAW_TRANSLATIONS
        or len(translations) != 66
        or set(EXPECTED_FULL_BASE_JP) != set(range(2352, 2422))
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
    if (
        translations["0:2366:0"] != "더는"
        or translations["0:2373:0"] != "합시다"
        or translations["0:2380:0"] != "하겠습니다"
        or translations["0:2408:0"] != "분"
        or translations["0:2416:0"] != "주었다"
    ):
        raise RuntimeError(f"segment {SEGMENT} semantic fix drifted")
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
        if UTIL.layout_signature(translation) != UTIL.layout_signature(
            current_text
        ):
            raise RuntimeError(
                f"segment {SEGMENT} layout signature drifted: {coordinate}"
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
    call_cache = {
        (edition, corpus, root): root_call_sites(
            records_by_label[f"{edition}_{corpus}"],
            root + (PK_ROOT_SHIFT if edition == "pk" else 0),
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
                    "pk_semantic_root": PK_ROOT_BY_BASE[root],
                    "base_record_id": record_id,
                    "pk_semantic_record_id": record_id + PK_RECORD_OFFSET,
                    "automatic_space_inserted": False,
                    "full_terminal_record_ids": list(
                        FULL_TERMINAL_GROUPS[root]
                    ),
                    "pk_full_terminal_record_ids": [
                        value + PK_RECORD_OFFSET
                        for value in FULL_TERMINAL_GROUPS[root]
                    ],
                    "source_call_count": len(
                        call_cache[("base", "jp", root)]
                    ),
                    "current_call_count": len(
                        call_cache[("base", "current", root)]
                    ),
                    "pk_source_call_count": len(
                        call_cache[("pk", "jp", root)]
                    ),
                    "pk_current_call_count": len(
                        call_cache[("pk", "current", root)]
                    ),
                    "caller_rewrite_examples": (
                        CALLER_REWRITE_EXAMPLES.get(root, {})
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
    if changed != 48:
        raise RuntimeError(f"segment {SEGMENT} changed count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B006_S1020",
                "queue": QUEUE_BATCH_ID,
                "source_literal_count": 66,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "changed_literal_count": changed,
                "base_pk_semantic_record_offset": PK_RECORD_OFFSET,
                "base_pk_root_shift": PK_ROOT_SHIFT,
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
