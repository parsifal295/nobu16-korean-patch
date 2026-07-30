#!/usr/bin/env python3
"""Build PK block-0 runtime-terminal segment 1030 decisions."""

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

import build_base_batch003_segment1009 as BASE
import build_pk_batch001_segment1025 as SUPPORT
import build_pk_batch002_segment1029 as LEFT


ENGINE = BASE.ENGINE
GENERAL = BASE.GENERAL
UTIL = BASE.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B003_S1030.private.v1.jsonl"
)
QUEUE_PATH = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "review_queue.private.v1.jsonl"
)
SEGMENT = 1030
BLOCK_ID = 0
QUEUE_BATCH_ID = "pk_msggame-B003"
QUEUE_ZERO_BASED_START = 0
QUEUE_ZERO_BASED_STOP = 67
RECORD_IDS = tuple(range(1663, 1730))
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
PREFIX_PK_IDS = tuple(range(1663, 1720))
INSERTED_PK_IDS = tuple(range(1720, 1727))
TAIL_PK_IDS = tuple(range(1727, 1730))
MAPPED_PK_IDS = PREFIX_PK_IDS + TAIL_PK_IDS
BASE_RECORD_MAP = {
    (BLOCK_ID, pk_record_id): (
        BLOCK_ID,
        pk_record_id - 54 if pk_record_id <= 1719 else pk_record_id - 61,
    )
    for pk_record_id in MAPPED_PK_IDS
}
PK_RECORD_COUNT = 21751

PK_SOURCE_DIVERGENCES = {
    1690: {
        "base_record_id": 1636,
        "base_jp": "きかねる",
        "pk_jp": "けませぬ",
        "base_current": "할 수 없다",
        "pk_current": "할 수 없사옵니다",
        "translation": "지 못하옵니다",
    }
}
INSERTED_JP = (
    "とうございます",
    "とうござる",
    "とうございます",
    "とうございます",
    "とうございます",
    "とうござる",
    "たい",
)
INSERTED_CURRENT = (
    "합니다",
    "하오",
    "합니다",
    "합니다",
    "합니다",
    "하오",
    "하고 싶다",
)
INSERTED_POLICY = (
    "고 싶습니다",
    "고 싶소",
    "고 싶습니다",
    "고 싶습니다",
    "고 싶습니다",
    "고 싶소",
    "고 싶다",
)
EXPECTED_PK_JP_BY_RECORD = {
    base_record_id + 54: BASE.EXPECTED_BASE_JP[base_record_id]
    for base_record_id in range(1609, 1666)
}
EXPECTED_PK_JP_BY_RECORD[1690] = PK_SOURCE_DIVERGENCES[1690][
    "pk_jp"
]
EXPECTED_PK_JP_BY_RECORD.update(
    {
        record_id: source
        for record_id, source in zip(
            INSERTED_PK_IDS,
            INSERTED_JP,
            strict=True,
        )
    }
)
EXPECTED_PK_JP_BY_RECORD.update(
    {
        base_record_id + 61: BASE.EXPECTED_BASE_JP[base_record_id]
        for base_record_id in range(1666, 1669)
    }
)

TRANSLATIONS_BY_RECORD = {
    base_record_id + 54: BASE.TRANSLATIONS_BY_RECORD[base_record_id]
    for base_record_id in range(1609, 1666)
}
TRANSLATIONS_BY_RECORD[1690] = PK_SOURCE_DIVERGENCES[1690][
    "translation"
]
TRANSLATIONS_BY_RECORD.update(
    {
        record_id: translation
        for record_id, translation in zip(
            INSERTED_PK_IDS,
            INSERTED_POLICY,
            strict=True,
        )
    }
)
TRANSLATIONS_BY_RECORD.update(
    {
        base_record_id + 61: BASE.TRANSLATIONS_BY_RECORD[base_record_id]
        for base_record_id in range(1666, 1669)
    }
)
TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}

FULL_TERMINAL_GROUPS = {
    328: tuple(range(1657, 1664)),
    334: tuple(range(1664, 1671)),
    340: tuple(range(1671, 1678)),
    346: tuple(range(1678, 1685)),
    352: tuple(range(1685, 1692)),
    358: tuple(range(1692, 1699)),
    364: tuple(range(1699, 1706)),
    370: tuple(range(1706, 1713)),
    376: tuple(range(1713, 1720)),
    382: INSERTED_PK_IDS,
    388: tuple(range(1727, 1734)),
}
FULL_TERMINAL_IDS = tuple(
    record_id
    for record_ids in FULL_TERMINAL_GROUPS.values()
    for record_id in record_ids
)
EXPECTED_GRAPH_CLOSURES = {
    root: tuple(range(root, root + 6)) + record_ids
    for root, record_ids in FULL_TERMINAL_GROUPS.items()
}
RECORD_TO_ROOT = {
    record_id: root
    for root, record_ids in FULL_TERMINAL_GROUPS.items()
    for record_id in record_ids
    if record_id in RECORD_IDS
}

PK_ARCHIVE_DIGESTS = {
    "pk_jp": "4268E33566B0616E1E08407C88DD7BB4B531FC29656525EFDA037603BF9B00D5",
    "pk_current": "C3537FED9B2AA8BC4263365C9B6A90AAA42C887A08CBA99D237695725C15CFA4",
    "pk_sc": "72AABE4A25E7A1A9165C6C408903A3D7F09ECCE70772F6F646C1FCDE3F9DCD3D",
    "pk_tc": "72AABE4A25E7A1A9165C6C408903A3D7F09ECCE70772F6F646C1FCDE3F9DCD3D",
    "pk_en": "72AABE4A25E7A1A9165C6C408903A3D7F09ECCE70772F6F646C1FCDE3F9DCD3D",
}
EXPECTED_TARGET_INCOMING = (
    67,
    "29D65B93D553C8883AB3618CA90E023B8DBF8C14FF7A3B42794097C5F8F63BFF",
)
EXPECTED_FULL_INCOMING = (
    77,
    "C2E19BF8ED77C414A31C59863D7D31BCE69FAA650C544934688CF837022FAD30",
)
EXPECTED_REVERSE_MAP_SHA256 = (
    "E185B6F8528C4B44056DE14C60709BFCBEDF5F15726AC56B52BAF79C856EE614"
)
EXPECTED_CHANGED_LITERAL_COUNT = 39

LEFT_ROOT328_FULL_IDS = LEFT.RIGHT_BOUNDARY_IDS
LEFT_ROOT328_FULL_JP = LEFT.RIGHT_BOUNDARY_JP
LEFT_ROOT328_FULL_CURRENT = LEFT.RIGHT_BOUNDARY_CURRENT
LEFT_ROOT328_FULL_POLICY = LEFT.RIGHT_BOUNDARY_POLICY
RIGHT_ROOT388_FULL_IDS = tuple(range(1727, 1734))
RIGHT_ROOT388_FULL_JP = (
    "みせ",
    "みせ",
    "ご覧にいれ",
    "ご覧にいれ",
    "ご覧にいれ",
    "ご覧にいれ",
    "みせ",
)
RIGHT_ROOT388_FULL_CURRENT = (
    "보여",
    "보여",
    "보여 드리",
    "보여 드리",
    "보여 드리",
    "보여 드리",
    "보여",
)
RIGHT_ROOT388_FULL_POLICY = RIGHT_ROOT388_FULL_CURRENT
RIGHT_ROOT388_INCOMING = (
    (0, 389, 0, 6, 1727),
    (0, 389, 0, 18, 1728),
    (0, 391, 0, 83, 1733),
    (0, 392, 0, 6, 1729),
    (0, 392, 0, 18, 1730),
    (0, 393, 0, 6, 1731),
    (0, 393, 0, 18, 1732),
)
INSERTED_CALLER_SITE = "7:2499:2:0"
INSERTED_CALLER_JP = (
    "攻め、\n我らも加わり",
    "！\n軍団からは",
)
INSERTED_CALLER_CURRENT = (
    "공략에\n우리도 참가하겠습니다",
    "!\n군단에서는",
)

EMPTY_SITE_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB924"
    "27AE41E4649B934CA495991B7852B855"
)
ROOT_CALL_COUNTS = {
    label: {
        root: (
            1
            if root == 382
            else BASE.ROOT_CALL_EVIDENCE[label].get(
                root,
                (0, EMPTY_SITE_SHA256),
            )[0]
        )
        for root in FULL_TERMINAL_GROUPS
    }
    for label in ("pk_jp", "pk_current")
}
EXPECTED_FIXED_FOLLOWING = {
    label: {
        root: sites
        for root, sites in BASE.FIXED_FOLLOWING_BLOCKERS[label].items()
        if root in FULL_TERMINAL_GROUPS
    }
    for label in ("pk_jp", "pk_current")
}
EXPECTED_SOURCE_ONLY_FLATTENED = {
    root: sites
    for root, sites in BASE.SOURCE_ONLY_FLATTENED_CALLS["pk"].items()
    if root in FULL_TERMINAL_GROUPS
}

ASSEMBLY_PLAN = {
    328: "benefactive-past predicate selected by speaker register",
    334: "benefactive give predicate selected by speaker register",
    340: "聞 + listen/accept imperative; caller prefix requires rewrite",
    346: "godan/te-form + polite request ending",
    352: "predicate stem + inability ending",
    358: "come imperative selected by speaker register",
    364: "unvoiced-godan caller stem + volitional ending",
    370: "voiced-godan caller stem + volitional ending",
    376: "caller-specific copular or existential predicate",
    382: (
        "加わりとうございます is 加わりたくございます with "
        "u-onbin; rewrite current caller to 우리도 참가하 + desire ending"
    ),
    388: "show/demonstrate stem plus caller-specific fixed action ending",
}
BASIS = (
    "review_queue_pk_msggame_B003_visible_ordinals0_66_pristine_pk_pc_"
    "jp_sole_translation_authority_records1663_1729_piecewise_unique_"
    "Base_reverse_search_plus54_records1663_1719_pk_only_inserted_"
    "root382_records1720_1726_plus61_records1727_1729_explicit_pk1690_"
    "kemasenu_register_override_inserted_kuwawaritogozaimasu_desire_"
    "u_onbin_independent_semantics_pk_en_sc_tc_blank_context_actual_"
    "014A_target_and_full_closures_0143_callers_fixed_following_source_"
    "current_flatten_and_014C_overlap_guard_left_S1029_root328_and_"
    "right_S1031_root388_full_matrices_benefactive_listen_request_"
    "inability_come_volitional_copular_existential_desire_show_"
    "runtime_caller_rewrite_pending_no_historic_or_switch_korean_"
    "authority_one_line_skeleton_outside_reverse_exact_no_steam"
)


def literal_texts(
    records: dict[tuple[int, int], Any],
    record_id: int,
) -> tuple[str, ...]:
    return tuple(
        literal.text
        for literal in ENGINE.parse_record_literals(
            records[(BLOCK_ID, record_id)]
        )
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


def sequence_candidates(
    base_jp: dict[tuple[int, int], Any],
    pk_jp: dict[tuple[int, int], Any],
    pk_ids: tuple[int, ...],
    equivalences: dict[int, tuple[str, str]],
) -> tuple[int, ...]:
    block_zero_ids = sorted(
        record_id
        for block_id, record_id in base_jp
        if block_id == BLOCK_ID
    )
    candidates: list[int] = []
    for start in block_zero_ids:
        base_ids = tuple(range(start, start + len(pk_ids)))
        if any((BLOCK_ID, record_id) not in base_jp for record_id in base_ids):
            continue
        matched = True
        for pk_record_id, base_record_id in zip(
            pk_ids,
            base_ids,
            strict=True,
        ):
            base_text = literal_texts(base_jp, base_record_id)
            pk_text = literal_texts(pk_jp, pk_record_id)
            if pk_record_id in equivalences:
                expected_base, expected_pk = equivalences[pk_record_id]
                text_matches = (
                    base_text == (expected_base,)
                    and pk_text == (expected_pk,)
                )
            else:
                text_matches = base_text == pk_text
            if (
                not text_matches
                or gap_bytes(base_jp[(BLOCK_ID, base_record_id)])
                != gap_bytes(pk_jp[(BLOCK_ID, pk_record_id)])
            ):
                matched = False
                break
        if matched:
            candidates.append(start)
    return tuple(candidates)


def discover_base_mapping(
    base_jp: dict[tuple[int, int], Any],
    pk_jp: dict[tuple[int, int], Any],
) -> dict[tuple[int, int], tuple[int, int]]:
    divergence = PK_SOURCE_DIVERGENCES[1690]
    prefix_candidates = sequence_candidates(
        base_jp,
        pk_jp,
        PREFIX_PK_IDS,
        {1690: (divergence["base_jp"], divergence["pk_jp"])},
    )
    tail_candidates = sequence_candidates(
        base_jp,
        pk_jp,
        TAIL_PK_IDS,
        {},
    )
    inserted_candidates = sequence_candidates(
        base_jp,
        pk_jp,
        INSERTED_PK_IDS,
        {},
    )
    if (
        prefix_candidates != (1609,)
        or tail_candidates != (1666,)
        or inserted_candidates
    ):
        raise RuntimeError(
            f"segment {SEGMENT} piecewise reverse search drifted: "
            f"{prefix_candidates}/{tail_candidates}/"
            f"{inserted_candidates}"
        )
    mapping = {
        (BLOCK_ID, pk_record_id): (
            BLOCK_ID,
            1609 + ordinal,
        )
        for ordinal, pk_record_id in enumerate(PREFIX_PK_IDS)
    }
    mapping.update(
        {
            (BLOCK_ID, pk_record_id): (
                BLOCK_ID,
                1666 + ordinal,
            )
            for ordinal, pk_record_id in enumerate(TAIL_PK_IDS)
        }
    )
    if mapping != BASE_RECORD_MAP:
        raise RuntimeError(f"segment {SEGMENT} discovered Base map drifted")
    evidence = [
        [
            pk_record_id,
            mapping.get((BLOCK_ID, pk_record_id), (None, None))[1],
        ]
        for pk_record_id in RECORD_IDS
    ]
    if SUPPORT.canonical_sha256(evidence) != EXPECTED_REVERSE_MAP_SHA256:
        raise RuntimeError(f"segment {SEGMENT} reverse map digest drifted")
    return mapping


def assert_source_and_mapping(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[tuple[int, int], tuple[int, int]]:
    BASE.assert_corpora(records_by_label)
    BASE.assert_full_group_boundaries(records_by_label)
    for label, expected_digest in PK_ARCHIVE_DIGESTS.items():
        actual = GENERAL.subset_digest(
            records_by_label[label],
            RECORD_KEYS,
        )
        if actual != expected_digest:
            raise RuntimeError(
                f"segment {SEGMENT} target corpus drifted: {label}"
            )
    for record_id in RECORD_IDS:
        key = (BLOCK_ID, record_id)
        for label in PK_ARCHIVE_DIGESTS:
            if (
                len(literal_texts(records_by_label[label], record_id)) != 1
                or gap_bytes(records_by_label[label][key])
                != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} PK skeleton drifted: "
                    f"{label}/{key}"
                )
        if literal_texts(records_by_label["pk_jp"], record_id) != (
            EXPECTED_PK_JP_BY_RECORD[record_id],
        ):
            raise RuntimeError(
                f"segment {SEGMENT} pristine PK JP drifted: {key}"
            )
        for label in ("pk_sc", "pk_tc", "pk_en"):
            if literal_texts(records_by_label[label], record_id) != ("",):
                raise RuntimeError(
                    f"segment {SEGMENT} auxiliary context drifted: "
                    f"{label}/{key}"
                )

    mapping = discover_base_mapping(
        records_by_label["base_jp"],
        records_by_label["pk_jp"],
    )
    for pk_key, base_key in mapping.items():
        pk_record_id = pk_key[1]
        if pk_record_id == 1690:
            expected = PK_SOURCE_DIVERGENCES[1690]
            if (
                literal_texts(records_by_label["base_jp"], base_key[1])
                != (expected["base_jp"],)
                or literal_texts(records_by_label["pk_jp"], pk_record_id)
                != (expected["pk_jp"],)
                or literal_texts(
                    records_by_label["base_current"],
                    base_key[1],
                )
                != (expected["base_current"],)
                or literal_texts(
                    records_by_label["pk_current"],
                    pk_record_id,
                )
                != (expected["pk_current"],)
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} PK1690 divergence drifted"
                )
        else:
            for language in ("jp", "current"):
                if (
                    records_by_label[f"base_{language}"][base_key].data
                    != records_by_label[f"pk_{language}"][pk_key].data
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} mapped bytes drifted: "
                        f"{language}/{base_key}/{pk_key}"
                    )
        for language in ("sc", "tc"):
            if (
                records_by_label[f"base_{language}"][base_key].data
                != records_by_label[f"pk_{language}"][pk_key].data
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} mapped context drifted: "
                    f"{language}/{base_key}/{pk_key}"
                )
    if tuple(
        literal_texts(records_by_label["pk_jp"], record_id)[0]
        for record_id in INSERTED_PK_IDS
    ) != INSERTED_JP or tuple(
        literal_texts(records_by_label["pk_current"], record_id)[0]
        for record_id in INSERTED_PK_IDS
    ) != INSERTED_CURRENT:
        raise RuntimeError(
            f"segment {SEGMENT} PK-only inserted literals drifted"
        )
    return mapping


def incoming_jump_rows(
    records: dict[tuple[int, int], Any],
    target_ids: set[int],
) -> tuple[tuple[int, int, int, int, int], ...]:
    rows: list[tuple[int, int, int, int, int]] = []
    for key in sorted(records):
        for gap_id, gap in enumerate(gap_bytes(records[key])):
            for match in BASE.GRAPH.MORPHOLOGY_JUMP_RE.finditer(gap):
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


def call_site_evidence(
    records: dict[tuple[int, int], Any],
    root: int,
) -> tuple[int, str]:
    sites = SUPPORT.root_call_sites(records, root)
    return (
        len(sites),
        hashlib.sha256(
            "\n".join(sites).encode("ascii")
        ).hexdigest().upper(),
    )


def assert_runtime_graph(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    BASE.assert_jump_and_call_graphs(records_by_label)
    BASE.assert_014c_and_blockers(records_by_label)
    target_ids = set(RECORD_IDS)
    full_ids = set(FULL_TERMINAL_IDS)
    for label in ("pk_jp", "pk_current"):
        records = records_by_label[label]
        target_rows = incoming_jump_rows(records, target_ids)
        full_rows = incoming_jump_rows(records, full_ids)
        if (
            (len(target_rows), SUPPORT.canonical_sha256(target_rows))
            != EXPECTED_TARGET_INCOMING
            or {row[4] for row in target_rows} != target_ids
            or any(
                sum(row[4] == target for row in target_rows) != 1
                for target in target_ids
            )
            or (len(full_rows), SUPPORT.canonical_sha256(full_rows))
            != EXPECTED_FULL_INCOMING
            or {row[4] for row in full_rows} != full_ids
        ):
            raise RuntimeError(
                f"segment {SEGMENT} incoming 014A drifted: {label}"
            )
        edges = SUPPORT.graph_edges(records)
        for root, expected in EXPECTED_GRAPH_CLOSURES.items():
            actual = tuple(sorted(SUPPORT.graph_closure(edges, root)))
            if actual != expected:
                raise RuntimeError(
                    f"segment {SEGMENT} full closure drifted: "
                    f"{label}/{root}"
                )
        if incoming_jump_rows(
            records,
            set(RIGHT_ROOT388_FULL_IDS),
        ) != RIGHT_ROOT388_INCOMING:
            raise RuntimeError(
                f"segment {SEGMENT} right boundary incoming drifted: "
                f"{label}"
            )

        for root in FULL_TERMINAL_GROUPS:
            actual = call_site_evidence(records, root)
            if root == 382:
                expected_sites = (INSERTED_CALLER_SITE,)
                expected = (
                    1,
                    hashlib.sha256(
                        "\n".join(expected_sites).encode("ascii")
                    ).hexdigest().upper(),
                )
            else:
                expected = BASE.ROOT_CALL_EVIDENCE[label].get(
                    root,
                    (0, EMPTY_SITE_SHA256),
                )
            if actual != expected:
                raise RuntimeError(
                    f"segment {SEGMENT} 0143 calls drifted: "
                    f"{label}/{root}"
                )

        actual_fixed = BASE.fixed_following_blockers(
            records,
            set(FULL_TERMINAL_GROUPS),
        )
        if actual_fixed != EXPECTED_FIXED_FOLLOWING[label]:
            raise RuntimeError(
                f"segment {SEGMENT} fixed-following drifted: {label}"
            )

    source_records = records_by_label["pk_jp"]
    current_records = records_by_label["pk_current"]
    flattened: dict[int, tuple[str, ...]] = {}
    current_only: dict[int, tuple[str, ...]] = {}
    for root in FULL_TERMINAL_GROUPS:
        source_sites = SUPPORT.root_call_sites(source_records, root)
        current_sites = SUPPORT.root_call_sites(current_records, root)
        source_only = tuple(
            sorted(set(source_sites) - set(current_sites))
        )
        added = tuple(sorted(set(current_sites) - set(source_sites)))
        if source_only:
            flattened[root] = source_only
        if added:
            current_only[root] = added
    if (
        flattened != EXPECTED_SOURCE_ONLY_FLATTENED
        or current_only
    ):
        raise RuntimeError(
            f"segment {SEGMENT} source/current flattening drifted"
        )

    for label in ("pk_jp", "pk_current"):
        records = records_by_label[label]
        caller_key = (7, 2499)
        literals = ENGINE.parse_record_literals(records[caller_key])
        if label == "pk_jp":
            expected_left, expected_right = INSERTED_CALLER_JP
        else:
            expected_left, expected_right = INSERTED_CALLER_CURRENT
        if (
            literals[1].text != expected_left
            or literals[2].text != expected_right
            or SUPPORT.root_call_sites(records, 382)
            != (INSERTED_CALLER_SITE,)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} inserted caller drifted: {label}"
            )


def assert_boundaries(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    for side, ids, expected_jp, expected_current in (
        (
            "left",
            LEFT_ROOT328_FULL_IDS,
            LEFT_ROOT328_FULL_JP,
            LEFT_ROOT328_FULL_CURRENT,
        ),
        (
            "right",
            RIGHT_ROOT388_FULL_IDS,
            RIGHT_ROOT388_FULL_JP,
            RIGHT_ROOT388_FULL_CURRENT,
        ),
    ):
        actual_jp = tuple(
            literal_texts(source, record_id)[0]
            for record_id in ids
        )
        actual_current = tuple(
            literal_texts(current, record_id)[0]
            for record_id in ids
        )
        if actual_jp != expected_jp or actual_current != expected_current:
            raise RuntimeError(
                f"segment {SEGMENT} {side} boundary drifted"
            )
    if LEFT_ROOT328_FULL_POLICY != (
        "주셨다",
        "주었다",
        "주셨습니다",
        "주셨사옵니다",
        "주었습니다",
        "주셨다",
        "주었다",
    ):
        raise RuntimeError(f"segment {SEGMENT} left policy drifted")
    if RIGHT_ROOT388_FULL_POLICY != (
        "보여",
        "보여",
        "보여 드리",
        "보여 드리",
        "보여 드리",
        "보여 드리",
        "보여",
    ):
        raise RuntimeError(f"segment {SEGMENT} right policy drifted")
    if (
        TRANSLATIONS_BY_RECORD[1663] != LEFT_ROOT328_FULL_POLICY[-1]
        or tuple(
            TRANSLATIONS_BY_RECORD[record_id]
            for record_id in TAIL_PK_IDS
        )
        != RIGHT_ROOT388_FULL_POLICY[:3]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} owned boundary policy drifted"
        )


def assert_semantics(translations: dict[str, str]) -> None:
    BASE.assert_semantics(dict(BASE.TRANSLATIONS))
    if (
        len(RECORD_IDS) != 67
        or set(EXPECTED_PK_JP_BY_RECORD) != set(RECORD_IDS)
        or set(TRANSLATIONS_BY_RECORD) != set(RECORD_IDS)
        or set(RECORD_TO_ROOT) != set(RECORD_IDS)
        or translations != TRANSLATIONS
    ):
        raise RuntimeError(f"segment {SEGMENT} translation universe drifted")
    for pk_key, base_key in BASE_RECORD_MAP.items():
        pk_record_id = pk_key[1]
        expected = (
            PK_SOURCE_DIVERGENCES[1690]["translation"]
            if pk_record_id == 1690
            else BASE.TRANSLATIONS_BY_RECORD[base_key[1]]
        )
        if TRANSLATIONS_BY_RECORD[pk_record_id] != expected:
            raise RuntimeError(
                f"segment {SEGMENT} mapped policy drifted: "
                f"{pk_record_id}"
            )
    if tuple(
        TRANSLATIONS_BY_RECORD[record_id]
        for record_id in INSERTED_PK_IDS
    ) != INSERTED_POLICY:
        raise RuntimeError(
            f"segment {SEGMENT} inserted desire policy drifted"
        )
    if (
        INSERTED_POLICY
        == INSERTED_CURRENT
        or INSERTED_POLICY[-1] != "고 싶다"
        or any(
            value != "고 싶습니다"
            for value in (
                INSERTED_POLICY[0],
                INSERTED_POLICY[2],
                INSERTED_POLICY[3],
                INSERTED_POLICY[4],
            )
        )
        or INSERTED_POLICY[1] != "고 싶소"
        or INSERTED_POLICY[5] != "고 싶소"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} inserted voice matrix drifted"
        )
    if tuple(
        TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(1685, 1692)
    ) != (
        "지 못하옵니다",
        "지 못한다",
        "지 못합니다",
        "지 못하옵니다",
        "지 못합니다",
        "지 못하옵니다",
        "지 못한다",
    ):
        raise RuntimeError(
            f"segment {SEGMENT} PK inability register drifted"
        )
    if tuple(
        TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(1713, 1720)
    ) != (
        "입니다",
        "있소",
        "입니다",
        "입니다",
        "입니다",
        "있소",
        "있다",
    ):
        raise RuntimeError(
            f"segment {SEGMENT} copular/existential matrix drifted"
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
        if gap_bytes(rebuilt_records[key]) != gap_bytes(
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
    discovered_mapping = assert_source_and_mapping(records_by_label)
    assert_runtime_graph(records_by_label)
    assert_boundaries(records_by_label)
    translations = dict(TRANSLATIONS)
    assert_semantics(translations)
    current = records_by_label["pk_current"]
    for coordinate, translation in translations.items():
        _, record_id, _ = (
            int(value) for value in coordinate.split(":")
        )
        current_text = literal_texts(current, record_id)[0]
        if (
            not ENGINE.is_visible_translation_candidate(current_text)
            or "\n" in current_text
            or current_text != current_text.strip()
            or "\n" in translation
            or translation != translation.strip()
            or UTIL.layout_signature(translation)
            != UTIL.layout_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} protected signature drifted: "
                f"{coordinate}"
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
        base_key = discovered_mapping.get((block_id, record_id))
        evidence: dict[str, object] = {
            "pk_root": root,
            "full_terminal_record_ids": list(
                FULL_TERMINAL_GROUPS[root]
            ),
            "full_graph_closure_record_ids": list(
                EXPECTED_GRAPH_CLOSURES[root]
            ),
            "mapping_class": (
                "pk_only_inserted_root382"
                if base_key is None
                else "base_plus54"
                if record_id <= 1719
                else "base_plus61"
            ),
            "base_semantic_record_discovered_by_reverse_search": (
                None if base_key is None else base_key[1]
            ),
            "source_call_count": ROOT_CALL_COUNTS["pk_jp"][root],
            "current_call_count": ROOT_CALL_COUNTS[
                "pk_current"
            ][root],
            "source_fixed_following_count": len(
                EXPECTED_FIXED_FOLLOWING["pk_jp"].get(root, ())
            ),
            "current_fixed_following_count": len(
                EXPECTED_FIXED_FOLLOWING["pk_current"].get(root, ())
            ),
            "source_calls_flattened_in_current": len(
                EXPECTED_SOURCE_ONLY_FLATTENED.get(root, ())
            ),
            "automatic_space_inserted": False,
            "caller_rewrite_required_before_runtime_approval": True,
            "runtime_integration_required": True,
            "assembly_plan": ASSEMBLY_PLAN[root],
        }
        if root == 382:
            evidence.update(
                {
                    "pk_only_source_group": True,
                    "caller_site": INSERTED_CALLER_SITE,
                    "source_left_literal": INSERTED_CALLER_JP[0],
                    "current_left_literal_requires_rewrite": (
                        INSERTED_CALLER_CURRENT[0]
                    ),
                    "required_korean_left_literal": "공략에\n우리도 참가하",
                }
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
            int(coordinate.split(":")[1]),
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
                "segment": "pk_msggame_B003_S1030",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [0, 66],
                "source_literal_count": 67,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "confirmed_non_display": 0,
                "changed_literal_count": changed,
                "mapping_method": (
                    "piecewise_unique_reverse_search_plus54_pk_inserted_"
                    "root382_plus61"
                ),
                "discovered_prefix_base_range": [1609, 1665],
                "pk_only_inserted_records": list(INSERTED_PK_IDS),
                "discovered_tail_base_range": [1666, 1668],
                "reverse_map_sha256": EXPECTED_REVERSE_MAP_SHA256,
                "pk_source_divergence_records": [1690],
                "pk_en_sc_tc_visible_records": [],
                "target_incoming_014a_evidence": list(
                    EXPECTED_TARGET_INCOMING
                ),
                "full_incoming_014a_evidence": list(
                    EXPECTED_FULL_INCOMING
                ),
                "root_source_call_counts": {
                    str(root): count
                    for root, count in ROOT_CALL_COUNTS["pk_jp"].items()
                },
                "root_current_call_counts": {
                    str(root): count
                    for root, count in (
                        ROOT_CALL_COUNTS["pk_current"].items()
                    )
                },
                "root_source_fixed_following_counts": {
                    str(root): len(
                        EXPECTED_FIXED_FOLLOWING["pk_jp"].get(root, ())
                    )
                    for root in FULL_TERMINAL_GROUPS
                },
                "root_current_fixed_following_counts": {
                    str(root): len(
                        EXPECTED_FIXED_FOLLOWING[
                            "pk_current"
                        ].get(root, ())
                    )
                    for root in FULL_TERMINAL_GROUPS
                },
                "root_source_calls_flattened_in_current": {
                    str(root): len(
                        EXPECTED_SOURCE_ONLY_FLATTENED.get(root, ())
                    )
                    for root in FULL_TERMINAL_GROUPS
                },
                "valid_014c_command_count": 0,
                "left_root328_full_policy": list(
                    LEFT_ROOT328_FULL_POLICY
                ),
                "inserted_root382_policy": list(INSERTED_POLICY),
                "right_root388_full_policy": list(
                    RIGHT_ROOT388_FULL_POLICY
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
