#!/usr/bin/env python3
"""Build PK block-0 runtime morphology-table segment 1024 decisions."""

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

import build_base_batch001_segment1003 as BASE
import build_base_batch001_segment1004 as NEXT
import build_base_batch001_segment1005 as NEXT_NEXT
import build_base_batch006_segment1020 as RUNTIME


ENGINE = BASE.ENGINE
SUPPORT = BASE.SUPPORT
UTIL = BASE.UTIL
COMMON = BASE.COMMON
GRAPH = RUNTIME.GRAPH
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B001_S1024.private.v1.jsonl"
)
BASE_DECISION = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S1003.private.v1.jsonl"
)
BASE_DECISION_SHA256 = (
    "CBBAF1F92502BF1BF5210A8153F918CAF3CF6CD40143C9C455ACAA02FC4C8B3C"
)
SEGMENT = 1024
QUEUE_BATCH_ID = "pk_msggame-B001"
BLOCK_ID = 0
NONQUEUE_CONTROL_ONLY_PK_RECORD_IDS = {
    1257,
    1259,
    1261,
    1299,
    1301,
    1302,
    1319,
    1321,
    1322,
}
TARGET_PK_RECORD_IDS = tuple(
    record_id
    for record_id in range(1248, 1324)
    if record_id not in NONQUEUE_CONTROL_ONLY_PK_RECORD_IDS
)
TARGET_COORDINATES = tuple(
    f"{BLOCK_ID}:{record_id}:0" for record_id in TARGET_PK_RECORD_IDS
)
TARGET_PK_KEYS = tuple(
    (BLOCK_ID, record_id) for record_id in TARGET_PK_RECORD_IDS
)
FULL_PK_RECORD_IDS = tuple(range(1247, 1324))
FULL_PK_KEYS = tuple(
    (BLOCK_ID, record_id) for record_id in FULL_PK_RECORD_IDS
)
EXPECTED_CHANGED_LITERAL_COUNT = 14

TARGET_ARCHIVE_DIGESTS = {
    "base_jp": "3F8F513497D1D9D30461668212DEE68A6F265E7CADE509FC02520703F24BDDC4",
    "base_current": "7F647325C882D3B0A65B1E7A84FC8680F07EC036F7BD3B2F512750E6E5EFFC61",
    "base_sc": "0F52AD2F70083502DE03EE17B5B34BAAE87029D4499C6555B0334E96EB214417",
    "base_tc": "203A945BBC1A39BC2A246580DD7537DB7B4F64682C4FD5A49003C39BFED59854",
    "pk_jp": "9F459A772B937060439CAFEA7C0F9C66DE775D6EE3ECA4B41736840B55627AC7",
    "pk_current": "3D6D81D28E875542419D694186EC16EE006E466B5971C0B304DC7A4D3945DD8B",
    "pk_sc": "678BA9280DF50AFFAF31AD02011041346249DB26186B07609CF07EFBC919008B",
    "pk_tc": "A3D80365332B6867214AD42606392B84CE92545FC7CA58F608B56C882F147962",
    "pk_en": "15EA8FE862AC92E5957EEA4B51FA225DADC219794271F6F5DF49AEC07D8CA3E9",
}
FULL_ARCHIVE_DIGESTS = {
    "base_jp": "9BCAB8099B75B8B8B01C301B600CF603BDFB20C16692EC108AA2E3F697A42CF0",
    "base_current": "C695BEFAEFE425FAB8B1387384344F79D4CBA8541BC812D09E8C68CD54D7DA0D",
    "base_sc": "A44AAF25C91164B8E436E0D9BFD53191CF7F0152CF5019CF7F0DE723753F8BCA",
    "base_tc": "153C37812C584DE9B9CE4D9BD318A8D3D57B8E49256A47CDC6A379DECC0012D4",
    "pk_jp": "DDDDE120A74D3A8C6C02FD0F1B4EDB29469C4FAAA8F1FBB4EBADD0A06641DE12",
    "pk_current": "E3F4D89A2E48651FC9B3921756402B1DC60323A3760B14CA3F22F0FA6DEDCECA",
    "pk_sc": "95FD2517E6AAA520D0EDFD12C893B539B6D4F995003A4850DBEFF6C9427421DA",
    "pk_tc": "BD3A60D7133BDE27C6D80BA4B20572106904DF65CD63FEB41639A9B95EB99B97",
    "pk_en": "0AB10B0CD6C5A4B80D194DCB49CCFADC0321EB899C759B255C73AF0DDA3C2875",
}

CALL_EVIDENCE = {
    "base_jp": (
        1205,
        1070,
        "FB2E9A9028C938B543B834E819B2E58C7C5BD1CCB2A4A77A6E7A6005EACF1709",
    ),
    "base_current": (
        1203,
        1068,
        "F8ACCDD537A38E2FF4CFC2CF0A196BFAF828684356DF393EC772869257E92328",
    ),
    "pk_jp": (
        1358,
        1206,
        "97ED2B52F41E4FD0C5AF65743198E162E7E17C68570D385E53CF85A1E4294591",
    ),
    "pk_current": (
        1354,
        1199,
        "3310CF8426583EE5B6F3152CBFD4D592C57BCE6D50E7569909BBB964F6561B9E",
    ),
}
FLATTEN_EVIDENCE = {
    "base": (
        2,
        "C199F50DBCAA62E34A47FCBB91FEB63F11157925A5EAE66E7E3C57F684CF53BA",
        0,
        "386DA300A1C40AE2594177920B70A12F8443734A98DD8CBFF587F7743E4CBE28",
    ),
    "pk": (
        4,
        "665DCC175C8C7C8B05F46713E39815BB42D9F84E4DF1DCB6D3758562737F4959",
        0,
        "D7CD5A257074AC2D611DA719B155D702069F06E4195840E84DE4A3DE3A68B3A5",
    ),
}
PK_ONLY_TRANSLATION_OVERRIDES_BY_BASE_RECORD = {
    1209: "우리",
}
EXPECTED_CHANGED_BASE_RECORD_IDS = (
    BASE.CURRENT_TRANSLATION_DIVERGENCE_IDS - {1209}
)

# These roots cross from the S1024 addressee table into S1025's dynamic
# title-suffix entries.  They are source-graph facts, not ordinal guesses.
S1025_LEFT_BOUNDARY_POLICY = {
    1324: "님",
    1325: "공",
    1328: "님",
    1329: "공",
    1331: "놈",
    1335: "님",
}
S1025_LEFT_BOUNDARY_CLOSURE = {
    21: (1324, 1325),
    29: (1324, 1325),
    37: (1324, 1325),
    34: (1328, 1329),
    46: (1331, 1335),
}
S1026_ROOT100_POLICY = {
    1391: "합니다",
    1392: "한다",
    1393: "하옵니다",
    1394: "합니다",
    1395: "합니다",
    1396: "합니다",
    1397: "한다",
}

TOKEN_PREFIX_BY_PK_RECORD = {
    1258: "024635",
    1260: "024634",
    1262: "024633",
    1300: "024735",
    1303: "024733",
    1304: "024735",
    1305: "024735",
    1306: "024734",
    1307: "024734",
    1308: "024733",
    1309: "024733",
    1320: "024835",
    1323: "024833",
}

BASIS = (
    "review_queue_pk_msggame_B001_visible_ordinals0_66_exact_pristine_"
    "pk_pc_jp_sole_translation_authority_block0_records1248_1323_67_"
    "visible_nine_control_only_records_excluded_full1247_1323_context_"
    "only_pk_en_sc_tc_pristine_base_jp_and_completed_base_S1003_decision_"
    "auxiliary_unique_prefix_and_suffix_tuple_discovery_without_offset_"
    "premise_graph_closure_semantic_mapping_with_only_root8_pk_extension_"
    "exact_source_current_archive_literal_gap_and_control_guards_014a_"
    "incoming_graph_reachable_0143_call_fixed_following_and_flattening_"
    "digests_runtime_pronoun_kinship_title_honorific_hostile_and_dynamic_"
    "name_fragments_pk_watakushitachi_changed_to_watashitachi_uses_uri_"
    "S1025_roots21_29_37_34_46_boundary_policy_and_S1026_root100_policy_"
    "one_line_protected_skeleton_runtime_fragment_pending_no_historic_"
    "or_switch_korean_authority_reverse_overlay_outside_exact_no_steam"
)


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return BASE.literal_texts(records, key)


def gap_hexes(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return BASE.gap_hexes(records, key)


def archive_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    base = prepared.resources["base_msggame"]
    pk = prepared.resources["pk_msggame"]
    archives = {
        "base_jp": base.pristine_archive,
        "base_current": base.current_archive,
        "base_sc": base.context_archives["SC"],
        "base_tc": base.context_archives["TC"],
        "pk_jp": pk.pristine_archive,
        "pk_current": pk.current_archive,
        "pk_sc": pk.context_archives["SC"],
        "pk_tc": pk.context_archives["TC"],
        "pk_en": pk.context_archives["EN"],
    }
    return {
        label: ENGINE.archive_records(archive)
        for label, archive in archives.items()
    }


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest().upper()


def sequence_starts(
    records: dict[tuple[int, int], Any],
    sequence: tuple[str, ...],
) -> tuple[int, ...]:
    maximum = max(
        record_id
        for block_id, record_id in records
        if block_id == BLOCK_ID
    )
    return tuple(
        start
        for start in range(maximum - len(sequence) + 2)
        if all(
            (BLOCK_ID, start + ordinal) in records
            and literal_texts(
                records,
                (BLOCK_ID, start + ordinal),
            )
            == (text,)
            for ordinal, text in enumerate(sequence)
        )
    )


def assert_queue_contract(prepared: Any) -> None:
    batch_rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line
        and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible_coordinates = tuple(
        target["coordinate"]
        for row in batch_rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(batch_rows) != 201
        or len(visible_coordinates) != 200
        or visible_coordinates[:67] != TARGET_COORDINATES
        or visible_coordinates[67] != "0:1324:0"
        or set(TARGET_PK_RECORD_IDS)
        != set(range(1248, 1324))
        - NONQUEUE_CONTROL_ONLY_PK_RECORD_IDS
    ):
        raise RuntimeError(
            f"segment {SEGMENT} private queue ordinal contract drifted"
        )


def discover_base_mapping(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[dict[int, int], int]:
    base_source = records_by_label["base_jp"]
    pk_source = records_by_label["pk_jp"]
    prefix_base = tuple(
        BASE.EXPECTED_BASE_JP[(BLOCK_ID, record_id)][0]
        for record_id in range(1194, 1201)
    )
    prefix_pk = tuple(
        BASE.EXPECTED_PK_JP[(BLOCK_ID, record_id)][0]
        for record_id in range(1194, 1201)
    )
    suffix_base = tuple(
        BASE.EXPECTED_BASE_JP[(BLOCK_ID, record_id)][0]
        for record_id in range(1256, 1265)
    )
    suffix_pk = tuple(
        BASE.EXPECTED_PK_JP[(BLOCK_ID, record_id)][0]
        for record_id in range(1256, 1265)
    )
    prefix_base_hits = sequence_starts(base_source, prefix_base)
    prefix_pk_hits = sequence_starts(pk_source, prefix_pk)
    suffix_base_hits = sequence_starts(base_source, suffix_base)
    suffix_pk_hits = sequence_starts(pk_source, suffix_pk)
    if (
        prefix_base_hits != (1194,)
        or prefix_pk_hits != (1248,)
        or suffix_base_hits != (1256,)
        or suffix_pk_hits != (1310,)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} unique Base/PK tuple discovery drifted"
        )
    prefix_delta = prefix_pk_hits[0] - prefix_base_hits[0]
    suffix_delta = suffix_pk_hits[0] - suffix_base_hits[0]
    if prefix_delta != suffix_delta:
        raise RuntimeError(
            f"segment {SEGMENT} independently discovered mapping drifted"
        )
    delta = prefix_delta
    mapping = {
        pk_record_id: pk_record_id - delta
        for pk_record_id in FULL_PK_RECORD_IDS
    }
    if (
        set(mapping.values()) != set(range(1193, 1270))
        or {
            mapping[pk_record_id]
            for pk_record_id in NONQUEUE_CONTROL_ONLY_PK_RECORD_IDS
        }
        != set(BASE.ZERO_LITERAL_RECORD_HEX)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} discovered mapping universe drifted"
        )
    return mapping, delta


def assert_archive_guards(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    mapping: dict[int, int],
) -> None:
    base_target_keys = tuple(
        (BLOCK_ID, mapping[pk_record_id])
        for pk_record_id in TARGET_PK_RECORD_IDS
    )
    base_full_keys = tuple(
        (BLOCK_ID, mapping[pk_record_id])
        for pk_record_id in FULL_PK_RECORD_IDS
    )
    for label, records in records_by_label.items():
        target_keys = (
            TARGET_PK_KEYS if label.startswith("pk_") else base_target_keys
        )
        full_keys = (
            FULL_PK_KEYS if label.startswith("pk_") else base_full_keys
        )
        if (
            COMMON.subset_digest(records, target_keys)
            != TARGET_ARCHIVE_DIGESTS[label]
            or COMMON.subset_digest(records, full_keys)
            != FULL_ARCHIVE_DIGESTS[label]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} archive guard drifted"
            )

    for pk_record_id in FULL_PK_RECORD_IDS:
        base_record_id = mapping[pk_record_id]
        base_key = (BLOCK_ID, base_record_id)
        pk_key = (BLOCK_ID, pk_record_id)
        if base_record_id in BASE.ZERO_LITERAL_RECORD_HEX:
            expected_hex = BASE.ZERO_LITERAL_RECORD_HEX[base_record_id]
            for label in records_by_label:
                actual_key = (
                    pk_key if label.startswith("pk_") else base_key
                )
                if (
                    records_by_label[label][actual_key].data.hex().upper()
                    != expected_hex
                    or ENGINE.parse_record_literals(
                        records_by_label[label][actual_key]
                    )
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} {label} control-only "
                        f"record drifted: {actual_key}"
                    )
            continue

        if (
            literal_texts(records_by_label["base_jp"], base_key)
            != BASE.EXPECTED_BASE_JP[base_key]
            or literal_texts(records_by_label["pk_jp"], pk_key)
            != BASE.EXPECTED_PK_JP[base_key]
            or gap_hexes(records_by_label["base_jp"], base_key)
            != BASE.EXPECTED_BASE_GAPS[base_key]
            or gap_hexes(records_by_label["pk_jp"], pk_key)
            != BASE.EXPECTED_PK_JP_GAPS[base_key]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} mapped source or skeleton drifted: "
                f"{base_key}/{pk_key}"
            )
        for label in (
            "base_jp",
            "base_current",
            "pk_jp",
            "pk_current",
        ):
            actual_key = pk_key if label.startswith("pk_") else base_key
            if len(literal_texts(records_by_label[label], actual_key)) != 1:
                raise RuntimeError(
                    f"segment {SEGMENT} {label} literal arity drifted: "
                    f"{actual_key}"
                )
            if gap_hexes(
                records_by_label[label],
                actual_key,
            ) != BASE.EXPECTED_BASE_GAPS[base_key]:
                raise RuntimeError(
                    f"segment {SEGMENT} {label} gap skeleton drifted: "
                    f"{actual_key}"
                )

        if base_key in BASE.SOURCE_EXACT_RECORD_KEYS:
            if (
                records_by_label["base_jp"][base_key].data
                != records_by_label["pk_jp"][pk_key].data
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} source-exact mapping drifted: "
                    f"{base_key}/{pk_key}"
                )
        elif (
            records_by_label["base_jp"][base_key].data
            == records_by_label["pk_jp"][pk_key].data
        ):
            raise RuntimeError(
                f"segment {SEGMENT} expected PK wording difference "
                f"vanished: {base_key}/{pk_key}"
            )

    for language in ("JP", "SC", "TC"):
        base_records = records_by_label[f"base_{language.lower()}"]
        pk_records = records_by_label[f"pk_{language.lower()}"]
        literal_divergences = {
            (BLOCK_ID, mapping[pk_record_id])
            for pk_record_id in FULL_PK_RECORD_IDS
            if mapping[pk_record_id] not in BASE.ZERO_LITERAL_RECORD_HEX
            and literal_texts(
                base_records,
                (BLOCK_ID, mapping[pk_record_id]),
            )
            != literal_texts(pk_records, (BLOCK_ID, pk_record_id))
        }
        gap_divergences = {
            (BLOCK_ID, mapping[pk_record_id])
            for pk_record_id in FULL_PK_RECORD_IDS
            if mapping[pk_record_id] not in BASE.ZERO_LITERAL_RECORD_HEX
            and gap_hexes(
                base_records,
                (BLOCK_ID, mapping[pk_record_id]),
            )
            != gap_hexes(pk_records, (BLOCK_ID, pk_record_id))
        }
        if (
            literal_divergences
            != BASE.EXPECTED_LITERAL_DIVERGENCES[language]
            or gap_divergences
            != BASE.EXPECTED_GAP_DIVERGENCES[language]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {language} contextual mapping drifted"
            )


def call_payload(
    records: dict[tuple[int, int], Any],
    roots: tuple[int, ...],
) -> tuple[dict[str, dict[str, tuple[str, ...]]], int, int]:
    payload: dict[str, dict[str, tuple[str, ...]]] = {}
    call_count = 0
    fixed_count = 0
    for root in roots:
        calls = RUNTIME.root_call_sites(records, root)
        fixed = RUNTIME.fixed_following_blockers(records, root)
        payload[str(root)] = {"calls": calls, "fixed": fixed}
        call_count += len(calls)
        fixed_count += len(fixed)
    return payload, call_count, fixed_count


def assert_graph_and_calls(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    mapping: dict[int, int],
) -> None:
    base_ids = set(mapping.values())
    pk_ids = set(mapping)
    roots_by_label = {
        "base_jp": tuple(
            sorted(BASE.EXPECTED_SOURCE_REACHABLE_ROOT_CALLS["base"])
        ),
        "base_current": tuple(
            sorted(BASE.EXPECTED_REACHABLE_ROOT_CALLS["base"])
        ),
        "pk_jp": tuple(
            sorted(BASE.EXPECTED_SOURCE_REACHABLE_ROOT_CALLS["pk"])
        ),
        "pk_current": tuple(
            sorted(BASE.EXPECTED_REACHABLE_ROOT_CALLS["pk"])
        ),
    }
    for label, roots in roots_by_label.items():
        records = records_by_label[label]
        corpus = "pk" if label.startswith("pk_") else "base"
        source_version = label.endswith("_jp")
        ids = pk_ids if corpus == "pk" else base_ids
        incoming, root_calls, root_summary = BASE.graph_evidence(
            records,
            ids,
        )
        expected_calls = (
            BASE.EXPECTED_SOURCE_REACHABLE_ROOT_CALLS[corpus]
            if source_version
            else BASE.EXPECTED_REACHABLE_ROOT_CALLS[corpus]
        )
        expected_summary = (
            BASE.EXPECTED_SOURCE_REACHABLE_ROOT_SUMMARY_SHA256[corpus]
            if source_version
            else BASE.EXPECTED_REACHABLE_ROOT_SUMMARY_SHA256[corpus]
        )
        if (
            incoming != BASE.EXPECTED_GRAPH_INCOMING[corpus]
            or root_calls != expected_calls
            or root_summary != expected_summary
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} 014A/0143 graph drifted"
            )
        payload, call_count, fixed_count = call_payload(records, roots)
        expected = CALL_EVIDENCE[label]
        if (
            call_count != expected[0]
            or fixed_count != expected[1]
            or canonical_sha256(payload) != expected[2]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} call/fixed evidence drifted"
            )

    for edition in ("base", "pk"):
        source_label = f"{edition}_jp"
        current_label = f"{edition}_current"
        roots = tuple(
            sorted(
                set(roots_by_label[source_label])
                | set(roots_by_label[current_label])
            )
        )
        flattened: dict[str, tuple[str, ...]] = {}
        current_only: dict[str, tuple[str, ...]] = {}
        for root in roots:
            source_sites = set(
                RUNTIME.root_call_sites(
                    records_by_label[source_label],
                    root,
                )
            )
            current_sites = set(
                RUNTIME.root_call_sites(
                    records_by_label[current_label],
                    root,
                )
            )
            flattened[str(root)] = tuple(
                sorted(source_sites - current_sites)
            )
            current_only[str(root)] = tuple(
                sorted(current_sites - source_sites)
            )
        expected = FLATTEN_EVIDENCE[edition]
        if (
            sum(len(sites) for sites in flattened.values())
            != expected[0]
            or canonical_sha256(flattened) != expected[1]
            or sum(len(sites) for sites in current_only.values())
            != expected[2]
            or canonical_sha256(current_only) != expected[3]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {edition} caller flattening drifted"
            )

    base_edges = GRAPH.graph_edges(records_by_label["base_jp"])
    pk_edges = GRAPH.graph_edges(records_by_label["pk_jp"])
    common_roots = (1, 4, 6, 7, 8, 13, 17, 20, 21, 29, 34, 37, 46)
    for root in common_roots:
        base_closure = GRAPH.graph_closure(
            base_edges,
            root,
        ).intersection(base_ids)
        mapped_closure = {
            pk_record_id
            for pk_record_id, base_record_id in mapping.items()
            if base_record_id in base_closure
        }
        pk_closure = GRAPH.graph_closure(
            pk_edges,
            root,
        ).intersection(pk_ids)
        expected_pk_only = {1304} if root == 8 else set()
        if (
            pk_closure - mapped_closure != expected_pk_only
            or mapped_closure - pk_closure
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base/PK graph mapping drifted: {root}"
            )
    if (
        GRAPH.graph_closure(base_edges, 1232).intersection(base_ids)
        != {1232}
        or GRAPH.graph_closure(pk_edges, 1286).intersection(pk_ids)
        != {1286}
        or GRAPH.graph_closure(pk_edges, 1307).intersection(pk_ids)
        != {1307}
    ):
        raise RuntimeError(
            f"segment {SEGMENT} direct semantic root mapping drifted"
        )


def assert_neighbor_boundaries(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    delta: int,
) -> None:
    pk_source = records_by_label["pk_jp"]
    for pk_record_id, policy in S1025_LEFT_BOUNDARY_POLICY.items():
        base_record_id = pk_record_id - delta
        if (
            literal_texts(
                pk_source,
                (BLOCK_ID, pk_record_id),
            )
            != (NEXT.EXPECTED_PK_JP[base_record_id],)
            or NEXT.TRANSLATIONS_BY_RECORD[base_record_id] != policy
        ):
            raise RuntimeError(
                f"segment {SEGMENT} S1025 boundary policy drifted: "
                f"{pk_record_id}"
            )
    boundary_ids = set(S1025_LEFT_BOUNDARY_POLICY)
    for label in ("pk_jp", "pk_current"):
        edges = GRAPH.graph_edges(records_by_label[label])
        for root, expected_ids in S1025_LEFT_BOUNDARY_CLOSURE.items():
            actual = GRAPH.graph_closure(
                edges,
                root,
            ).intersection(boundary_ids)
            if actual != set(expected_ids):
                raise RuntimeError(
                    f"segment {SEGMENT} {label} S1025 cross-boundary "
                    f"closure drifted: {root}"
                )

    imported_root100 = {
        **{
            base_record_id + delta:
            NEXT.TRANSLATIONS_BY_RECORD[base_record_id]
            for base_record_id in range(1337, 1343)
        },
        1343 + delta: NEXT_NEXT.TRANSLATIONS_BY_RECORD[1343],
    }
    if imported_root100 != S1026_ROOT100_POLICY:
        raise RuntimeError(
            f"segment {SEGMENT} S1026 root100 boundary policy drifted"
        )


def load_base_semantic_policy(
    prepared: Any,
) -> dict[str, str]:
    if (
        not BASE_DECISION.is_file()
        or hashlib.sha256(BASE_DECISION.read_bytes()).hexdigest().upper()
        != BASE_DECISION_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} completed Base decision guard drifted"
        )
    validated = ENGINE.validate_decisions(
        prepared,
        BASE_DECISION,
        require_complete=False,
    )
    policy = {
        f"{block_id}:{record_id}:{literal_id}": translation
        for (
            resource,
            block_id,
            record_id,
            literal_id,
        ), translation in validated.items()
        if resource == "base_msggame"
    }
    if policy != BASE.RAW_TRANSLATIONS:
        raise RuntimeError(
            f"segment {SEGMENT} completed Base semantic policy drifted"
        )
    return policy


def build_translations(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    mapping: dict[int, int],
    base_policy: dict[str, str],
) -> dict[str, str]:
    translations: dict[str, str] = {}
    for pk_record_id in TARGET_PK_RECORD_IDS:
        base_record_id = mapping[pk_record_id]
        translation = PK_ONLY_TRANSLATION_OVERRIDES_BY_BASE_RECORD.get(
            base_record_id,
            base_policy[f"{BLOCK_ID}:{base_record_id}:0"],
        )
        translations[
            f"{BLOCK_ID}:{pk_record_id}:0"
        ] = translation
    if tuple(translations) != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} translation ordinal universe drifted"
        )

    source_divergence_ids = {
        mapping[pk_record_id]
        for pk_record_id in TARGET_PK_RECORD_IDS
        if literal_texts(
            records_by_label["base_jp"],
            (BLOCK_ID, mapping[pk_record_id]),
        )
        != literal_texts(
            records_by_label["pk_jp"],
            (BLOCK_ID, pk_record_id),
        )
    }
    if source_divergence_ids != {
        key[1] for key in BASE.PK_JP_WORDING_OVERRIDES
    }:
        raise RuntimeError(
            f"segment {SEGMENT} PK wording authority drifted"
        )
    if (
        translations["0:1263:0"] != "우리"
        or translations["0:1267:0"] != "자네"
        or translations["0:1269:0"] != "그대"
        or translations["0:1271:0"] != "네놈"
        or translations["0:1273:0"] != "당신"
        or translations["0:1288:0"] != "주군님"
        or translations["0:1294:0"] != "은거하신 어르신"
        or translations["0:1296:0"] != "아가씨"
        or {
            translations[f"0:{record_id}:0"]
            for record_id in (1305, 1307, 1309)
        }
        != {"공"}
        or translations["0:1312:0"] != "저놈"
        or translations["0:1313:0"] != "그놈"
        or translations["0:1314:0"] != "그놈"
        or translations["0:1316:0"] != "이놈"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic correction policy drifted"
        )

    current = records_by_label["pk_current"]
    changed_base_ids = {
        mapping[pk_record_id]
        for pk_record_id in TARGET_PK_RECORD_IDS
        if translations[f"0:{pk_record_id}:0"]
        != literal_texts(current, (BLOCK_ID, pk_record_id))[0]
    }
    if changed_base_ids != EXPECTED_CHANGED_BASE_RECORD_IDS:
        raise RuntimeError(
            f"segment {SEGMENT} changed semantic set drifted"
        )
    return translations


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
        len(current) != 21751
        or len(candidate_records) != 21751
        or set(replacements) != {
            (BLOCK_ID, record_id, 0)
            for record_id in TARGET_PK_RECORD_IDS
        }
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate universe drifted"
        )
    target_keys = set(TARGET_PK_KEYS)
    for key, current_record in current.items():
        if (
            key not in target_keys
            and candidate_records[key].data != current_record.data
        ):
            raise RuntimeError(
                f"segment {SEGMENT} changed out-of-scope record: {key}"
            )
    for record_id in TARGET_PK_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        if (
            gap_hexes(candidate_records, key)
            != gap_hexes(current, key)
            or literal_texts(candidate_records, key)
            != (translations[f"0:{record_id}:0"],)
            or SUPPORT.morphology_terminal_literals(
                candidate_records,
                record_id,
            )
            != (translations[f"0:{record_id}:0"],)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} candidate terminal drifted: {key}"
            )
    reversed_blob = ENGINE.rebuild_packed_with_literals(
        candidate,
        reverse,
    )
    if reversed_blob != pk.current_blob:
        raise RuntimeError(
            f"segment {SEGMENT} reverse overlay is not byte-exact"
        )
    return candidate, hashlib.sha256(candidate).hexdigest().upper()


def build_rows() -> tuple[
    Any,
    dict[str, str],
    list[dict[str, object]],
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
    mapping, delta = discover_base_mapping(records_by_label)
    assert_archive_guards(records_by_label, mapping)
    BASE.assert_control_only_records(records_by_label)
    BASE.assert_table_and_usage_contracts(records_by_label)
    assert_graph_and_calls(records_by_label, mapping)
    assert_neighbor_boundaries(records_by_label, delta)
    base_policy = load_base_semantic_policy(prepared)
    translations = build_translations(
        records_by_label,
        mapping,
        base_policy,
    )
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
            UTIL.layout_signature(translation)
            != UTIL.layout_signature(current_text)
            or "\r" in translation
            or "\n" in translation
            or translation != translation.strip()
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(
                translation
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} protected text drifted: {coordinate}"
            )

    _, candidate_sha256 = build_candidate(
        prepared,
        records_by_label,
        translations,
    )
    source_edges = GRAPH.graph_edges(records_by_label["pk_jp"])
    roots = tuple(
        sorted(BASE.EXPECTED_SOURCE_REACHABLE_ROOT_CALLS["pk"])
    )
    root_closures = {
        root: GRAPH.graph_closure(source_edges, root).intersection(
            set(FULL_PK_RECORD_IDS)
        )
        for root in roots
    }
    rows: list[dict[str, object]] = []
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        base_record_id = mapping[record_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        row: dict[str, object] = {
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
                "automatic_space_inserted": False,
                "leading_trailing_space_protected": True,
                "pk_record_id": record_id,
                "base_semantic_record_id": base_record_id,
                "base_mapping_method": (
                    "two_independent_unique_literal_tuples_plus_graph"
                ),
                "discovered_record_delta": delta,
                "reachable_source_roots": [
                    root
                    for root in roots
                    if record_id in root_closures[root]
                ],
                "incoming_jump_graph_guarded": True,
                "reachable_0143_call_sets_guarded": True,
                "fixed_following_guarded": True,
                "source_current_flattening_guarded": True,
                "runtime_integration_required": True,
            },
        }
        base_coordinate = f"0:{base_record_id}:0"
        if base_coordinate in BASE.AMBIGUOUS_FRAGMENT_NOTES:
            row["runtime_fragment_note"] = (
                BASE.AMBIGUOUS_FRAGMENT_NOTES[base_coordinate]
            )
        if record_id in TOKEN_PREFIX_BY_PK_RECORD:
            row["runtime_token_contract"] = {
                "pk_prefix": TOKEN_PREFIX_BY_PK_RECORD[record_id],
                "order": "token_then_literal",
                "automatic_space_inserted": False,
            }
        if record_id in (1286, 1307):
            row["direct_root_evidence"] = {
                "pk_root": record_id,
                "source_call_count": len(
                    RUNTIME.root_call_sites(
                        records_by_label["pk_jp"],
                        record_id,
                    )
                ),
                "current_call_count": len(
                    RUNTIME.root_call_sites(
                        records_by_label["pk_current"],
                        record_id,
                    )
                ),
                "fixed_following_count": len(
                    RUNTIME.fixed_following_blockers(
                        records_by_label["pk_jp"],
                        record_id,
                    )
                ),
            }
        rows.append(row)
    return prepared, translations, rows, candidate_sha256, delta


def main() -> int:
    prepared, translations, rows, candidate_sha256, delta = build_rows()
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
            (
                BLOCK_ID,
                int(coordinate.split(":")[1]),
            ),
        )[0]
        for coordinate, translation in translations.items()
    )
    if changed != EXPECTED_CHANGED_LITERAL_COUNT:
        raise RuntimeError(
            f"segment {SEGMENT} changed literal count drifted"
        )
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B001_S1024",
                "queue": QUEUE_BATCH_ID,
                "queue_visible_ordinals": [0, 66],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "source_literal_count": 67,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "confirmed_non_display": 0,
                "changed_literal_count": changed,
                "nonqueue_control_only_record_ids": sorted(
                    NONQUEUE_CONTROL_ONLY_PK_RECORD_IDS
                ),
                "base_mapping_method": (
                    "two_independent_unique_literal_tuples_plus_graph"
                ),
                "discovered_base_to_pk_record_delta": delta,
                "pk_only_semantic_override": {
                    "0:1263:0": "우리",
                },
                "call_evidence": CALL_EVIDENCE,
                "flatten_evidence": FLATTEN_EVIDENCE,
                "s1025_left_boundary_policy": (
                    S1025_LEFT_BOUNDARY_POLICY
                ),
                "s1025_left_boundary_closure": (
                    S1025_LEFT_BOUNDARY_CLOSURE
                ),
                "s1026_root100_policy": S1026_ROOT100_POLICY,
                "target_runtime_skeleton_exact": True,
                "full_boundary_runtime_skeleton_exact": True,
                "protected_signature_exact": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "candidate_sha256": candidate_sha256,
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
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
