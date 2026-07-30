#!/usr/bin/env python3
"""Build Base block-0 runtime-terminal segment 1017 decisions."""

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

import build_base_batch004_segment1012 as FIXED
import build_base_batch004_segment1014 as PRIOR


ENGINE = PRIOR.ENGINE
GENERAL = PRIOR.GENERAL
UTIL = PRIOR.UTIL
GRAPH = PRIOR.GRAPH
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B005_S1017.private.v1.jsonl"
)
SEGMENT = 1017
QUEUE_BATCH_ID = "base_msggame-B005"
BLOCK_ID = 0
RECORD_IDS = tuple(range(2151, 2217))
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
PK_RECORD_OFFSET = 68
PK_ROOT_SHIFT = 12

FULL_TERMINAL_GROUPS = {
    784: tuple(range(2149, 2156)),
    790: tuple(range(2156, 2163)),
    796: tuple(range(2163, 2170)),
    802: tuple(range(2170, 2177)),
    808: tuple(range(2177, 2184)),
    814: tuple(range(2184, 2191)),
    820: tuple(range(2191, 2198)),
    826: tuple(range(2198, 2205)),
    832: tuple(range(2205, 2212)),
    838: tuple(range(2212, 2219)),
}
TARGET_TERMINAL_GROUPS = {
    root: tuple(
        record_id
        for record_id in record_ids
        if record_id in RECORD_IDS
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
    for record_id in range(2149, 2219)
}

SOURCE_JP_BY_ROOT = {
    784: (
        "なされて",
        "なされて",
        "なされて",
        "なされて",
        "なされて",
        "なされて",
        "して",
    ),
    790: ("なぞ", "など", "なぞ", "なぞ", "など", "など", "ごとき"),
    796: (
        "なりません",
        "ならぬ",
        "なりませぬ",
        "なりませぬ",
        "なりません",
        "なりませぬ",
        "ならん",
    ),
    802: (
        "なりません",
        "ならぬ",
        "なりませぬ",
        "なりませぬ",
        "なりません",
        "ならぬ",
        "ならん",
    ),
    808: (
        "なんですって",
        "なんだと",
        "なんですって",
        "なんですと",
        "なんですって",
        "何たること",
        "なんだと",
    ),
    814: ("憎い", "憎き", "憎き", "憎き", "憎い", "憎き", "憎たらしい"),
    820: ("にくい", "がたい", "にくき", "づらき", "にくい", "がたき", "にくい"),
    826: ("くっ", "ぬう", "くっ", "ううむ", "くっ", "むう", "ぬうう"),
    832: ("ね", "だな", "ですね", "ですな", "ね", "じゃな", "だな"),
    838: ("のです", "のだ", "のです", "のです", "のです", "のだ", "のじゃ"),
}
CURRENT_KO_BY_ROOT = {
    784: (
        "하시어",
        "하시어",
        "하시어",
        "하시어",
        "하시어",
        "하시어",
        "하고",
    ),
    790: ("따위", "따위", "따위", "따위", "따위", "따위", "따위"),
    796: (
        "안 됩니다",
        "안 된다",
        "아니 되옵니다",
        "아니 되옵니다",
        "안 됩니다",
        "아니 되옵니다",
        "안 된다",
    ),
    802: (
        "안 됩니다",
        "안 된다",
        "아니 되옵니다",
        "아니 되옵니다",
        "안 됩니다",
        "안 된다",
        "안 된다",
    ),
    808: (
        "무엇이라고요",
        "무엇이라",
        "무엇이라고요",
        "무엇이라고",
        "무엇이라고요",
        "이럴 수가",
        "무엇이라",
    ),
    814: ("밉다", "미운", "미운", "미운", "밉다", "미운", "얄미운"),
    820: (
        "하기 어려운",
        "기 어렵다",
        "얄미운",
        "하기 어려운",
        "하기 어려운",
        "어려운",
        "하기 어려운",
    ),
    826: ("크윽", "으윽", "크윽", "으음", "크윽", "으음", "으으윽"),
    832: ("군", "이군", "이지요", "이군요", "군", "이로군", "이군"),
    838: (
        "인 것입니다",
        "인 것이다",
        "인 것입니다",
        "인 것입니다",
        "인 것입니다",
        "인 것이다",
        "이니라",
    ),
}
TRANSLATION_POLICY_BY_ROOT = {
    784: (
        "하시는 것",
        "하시는 것",
        "하시는 것",
        "하시는 것",
        "하시는 것",
        "하시는 것",
        "하는 것",
    ),
    790: CURRENT_KO_BY_ROOT[790],
    796: CURRENT_KO_BY_ROOT[796],
    802: CURRENT_KO_BY_ROOT[802],
    808: (
        "뭐라고요",
        "뭐라고",
        "뭐라고요",
        "뭐라고요",
        "뭐라고요",
        "이럴 수가",
        "뭐라고",
    ),
    814: ("미운", "미운", "미운", "미운", "미운", "미운", "얄미운"),
    820: (
        "하기 어려운",
        "하기 어려운",
        "하기 어려운",
        "하기 어려운",
        "하기 어려운",
        "하기 어려운",
        "하기 어려운",
    ),
    826: CURRENT_KO_BY_ROOT[826],
    832: CURRENT_KO_BY_ROOT[832],
    838: (
        "것입니다",
        "것이다",
        "것입니다",
        "것입니다",
        "것입니다",
        "것이다",
        "것이니라",
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
    2149: FULL_TRANSLATION_POLICY[2149],
    2150: FULL_TRANSLATION_POLICY[2150],
    2217: FULL_TRANSLATION_POLICY[2217],
    2218: FULL_TRANSLATION_POLICY[2218],
}

ARCHIVE_DIGESTS = {
    "base_jp": "FF81D7640640F960F59FD29F52366847AAB8BA5BFFAE6E7CF34B80A37C001683",
    "base_current": "C2BE1BAA21753E435199ED8A152F4EDD27B8E3F1744F0C71133052971DCBF087",
    "base_sc": "B3ECA552335E6A5C2B459D2F1C0FD7E47086A9030FD43DDBA1E28C42E06D01B7",
    "base_tc": "B3ECA552335E6A5C2B459D2F1C0FD7E47086A9030FD43DDBA1E28C42E06D01B7",
    "pk_jp": "83972A9F80703A1C2841738225A44E8F7B7C87CF774EBE6B60FE1957C9BEEA59",
    "pk_current": "5266C09E0788D2F403FF6439A5F471FC1C4310675A1A5C8D88EEB53B98FBD5D7",
    "pk_sc": "2FC9AE9C6B6E334F02C6A21B6578ED1349222A059B31D26DB48600F29AB656F6",
    "pk_tc": "2FC9AE9C6B6E334F02C6A21B6578ED1349222A059B31D26DB48600F29AB656F6",
    "pk_en": "2FC9AE9C6B6E334F02C6A21B6578ED1349222A059B31D26DB48600F29AB656F6",
}
SEGMENT_JUMP_EDGE_EVIDENCE = {
    "base": (
        66,
        "D0925BF947DDF91C03C4AE7F5F355ABCBEFC94878A738D70CD3C6E6BDAF945AA",
    ),
    "pk": (
        66,
        "3517083960CB8BE6E772F8C4510BC51D74C3FE40ADE345420F0C438D74C6323C",
    ),
}
FULL_GROUP_JUMP_EDGE_EVIDENCE = {
    "base": (
        70,
        "D80711F74ED70029824BC9EB1CC75DCE3059DC137090FCF0BBE464C82AECBC2A",
    ),
    "pk": (
        70,
        "46305082D0EB35B0B5EEC2196DFF9290955C0843D4ECCF7E05974F2F2128751B",
    ),
}
AGGREGATE_CALL_EVIDENCE = {
    "base_jp": (
        31,
        8,
        "973FBF4D3F31BF6580FFB19B5B0A9F7E99092A4582D090C97053320582C620C0",
    ),
    "base_current": (
        25,
        7,
        "159ABFEBFC64C0D2E20DC3A04940CCAC2BB6B32141AB7CC9DC54427EEDFB7566",
    ),
    "pk_jp": (
        46,
        10,
        "8FBC77F206151CE7D8C3E26ED16D56FEAC7EF7D2FC2C1B555E6AAAEA07704726",
    ),
    "pk_current": (
        38,
        8,
        "8FD0652D26CA43E66065BFB461F266B491A5B302B8E315ED97EBEE06F589C2C2",
    ),
}
AGGREGATE_FLATTEN_EVIDENCE = {
    "base": (
        6,
        "FBF9E009BEDB78EE40379D7AA7BFB15BAC98A816314CFC8BF0B701ACDFCF09E7",
    ),
    "pk": (
        8,
        "05C89A2DE57349D634CBAC22668089B9F560658CA45973CA9A91DE9F277B0FDE",
    ),
}
CALLER_REWRITE_EXAMPLES = {
    784: {
        "15:315:4": "접견 stem and following topic phrase require joint rewriting",
    },
    796: {
        "7:2801:2": "참을 수 stem requires the negative-obligation terminal",
    },
    808: {
        "1:20:0": "standalone surprise exclamation requires natural spoken Korean",
    },
    814: {
        "2:552:1": (
            "fixed dynamic 024833 person token follows the terminal, so "
            "the Korean adjective must remain attributive"
        ),
    },
    820: {
        "1:27:1": "공략하기 어려운 must remain attributive before 성",
    },
    838: {
        "6:3507:1": "verb predicate requires explanatory 것 construction",
    },
}

BASIS = (
    "review_queue_base_msggame_B005_S1017_pristine_base_pc_jp_sole_"
    "authority_block0_records2151_2216_66_visible_full_boundary_groups_"
    "2149_2218_exact_unique_seven_literal_tuple_reverse_search_pk_plus68_"
    "roots784_838_pk_plus12_jp_current_sc_tc_exact_pk_en_empty_archive_"
    "digests_014a_terminal_edges_0143_source_current_calls_flattening_"
    "and_fixed_following_aggregate_digests_honorific_connective_"
    "negative_obligation_surprise_hateful_difficult_attributive_"
    "interjection_sentence_final_and_explanatory_semantics_runtime_"
    "caller_rewrite_pending_hateful_attributive_before_dynamic_person_"
    "token_one_line_reverse_overlay_no_korean_authority"
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
        calls = PRIOR.root_call_sites(records, actual_root)
        fixed = FIXED.fixed_following_blockers(records, actual_root)
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
        source_sites = set(PRIOR.root_call_sites(source, actual_root))
        current_sites = set(PRIOR.root_call_sites(current, actual_root))
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

    for record_id in range(2149, 2219):
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
                f"segment {SEGMENT} contextual corpus drifted: "
                f"{record_id}"
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
            (EXPECTED_FULL_BASE_JP[record_id],)
            for record_id in record_ids
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
    if full_ids != set(range(2149, 2219)):
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
                edges = PRIOR.incoming_edges(records, mapped_ids)
                if (
                    len(edges) != evidence[0]
                    or {edge[2] for edge in edges} != mapped_ids
                    or PRIOR.edge_digest(edges) != evidence[1]
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
        pk_ids = {
            record_id + PK_RECORD_OFFSET for record_id in full_ids
        }
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

    current_calls = {
        root: {
            site.rsplit(":", 1)[0]
            for site in PRIOR.root_call_sites(
                records_by_label["base_current"],
                root,
            )
        }
        for root in FULL_TERMINAL_GROUPS
    }
    for root, examples in CALLER_REWRITE_EXAMPLES.items():
        if not set(examples).issubset(current_calls[root]):
            raise RuntimeError(
                f"segment {SEGMENT} caller example drifted: {root}"
            )

    if (
        gap_bytes(records_by_label["base_jp"][(2, 552)])[1]
        != bytes.fromhex("01432E030000024833")
        or gap_bytes(records_by_label["base_current"][(2, 552)])[1]
        != bytes.fromhex("01432E030000024833")
        or gap_bytes(records_by_label["pk_jp"][(2, 569)])[1]
        != bytes.fromhex("01433A030000024833")
        or gap_bytes(records_by_label["pk_current"][(2, 569)])[1]
        != bytes.fromhex("01433A030000024833")
    ):
        raise RuntimeError(
            f"segment {SEGMENT} root 814 dynamic person token drifted"
        )


def assert_semantics(translations: dict[str, str]) -> None:
    if (
        translations != RAW_TRANSLATIONS
        or len(translations) != 66
        or set(EXPECTED_FULL_BASE_JP) != set(range(2149, 2219))
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
        translations["0:2193:0"] != "하기 어려운"
        or translations["0:2212:0"] != "것입니다"
        or translations["0:2177:0"] != "뭐라고요"
        or translations["0:2184:0"] != "미운"
        or translations["0:2188:0"] != "미운"
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
    call_cache = {
        (edition, corpus, root): PRIOR.root_call_sites(
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
    if changed != 21:
        raise RuntimeError(f"segment {SEGMENT} changed count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B005_S1017",
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
                "aggregate_flatten_evidence": (
                    AGGREGATE_FLATTEN_EVIDENCE
                ),
                "segment_jump_edge_evidence": (
                    SEGMENT_JUMP_EDGE_EVIDENCE
                ),
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
