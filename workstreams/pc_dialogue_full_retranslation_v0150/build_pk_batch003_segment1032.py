#!/usr/bin/env python3
"""Build PK block-0 runtime-terminal segment 1032 decisions."""

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

import build_base_batch003_segment1010 as LEFT_BASE
import build_base_batch003_segment1011 as RIGHT_BASE
import build_pk_batch001_segment1025 as HELPERS
import build_pk_batch003_segment1031 as LEFT_PK


ENGINE = LEFT_BASE.ENGINE
GENERAL = LEFT_BASE.GENERAL
UTIL = LEFT_BASE.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B003_S1032.private.v1.jsonl"
)
BASE_DECISIONS = (
    (
        REPO
        / "tmp"
        / WORKSTREAM.name
        / "decisions"
        / "base_msggame_B003_S1010.private.v1.jsonl",
        "6EF7A8C7C07F93B4671A55A77E0536C411BAD411B472873B38E55B1D672DCBE0",
    ),
    (
        REPO
        / "tmp"
        / WORKSTREAM.name
        / "decisions"
        / "base_msggame_B003_S1011.private.v1.jsonl",
        "075BE49C32854623B46955CC92AA939181B0AF802EF9322D54B528E62759FD34",
    ),
)
SEGMENT = 1032
QUEUE_BATCH_ID = "pk_msggame-B003"
BLOCK_ID = 0
QUEUE_START = 134
QUEUE_STOP = 200
BASE_RECORD_IDS = tuple(range(1736, 1802))
RECORD_IDS = tuple(record_id + 61 for record_id in BASE_RECORD_IDS)
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
TARGET_COORDINATES = tuple(
    f"{BLOCK_ID}:{record_id}:0" for record_id in RECORD_IDS
)
EXPECTED_PK_JP = (
    "じてください",
    "ぜよ",
    "じてください",
    "じてくだされ",
    "じてください",
    "じてくだされ",
    "じろ",
    "します",
    "す",
    "します",
    "しまする",
    "します",
    "します",
    "す",
    "さないで",
    "すな",
    "さないでください",
    "しなさいますな",
    "さないでください",
    "されますな",
    "すな",
    "ないで",
    "ずに",
    "ないまま",
    "ずに",
    "ないままで",
    "ずに",
    "ないで",
    "しますまい",
    "すまじ",
    "しますまい",
    "しますまい",
    "しますまい",
    "しますまい",
    "すまい",
    "すみません",
    "すまぬ",
    "申し訳ございませぬ",
    "申し訳ございませぬ",
    "すみません",
    "相済みません",
    "すまぬ",
    "します",
    "する",
    "いたします",
    "いたしまする",
    "します",
    "いたします",
    "する",
    "じます",
    "ずる",
    "じます",
    "じまする",
    "じます",
    "じます",
    "ずる",
    "なさいますな",
    "するな",
    "なさいますな",
    "なされますな",
    "されまするな",
    "しないでくだされ",
    "するな",
    "してください",
    "せ",
    "してくださいませ",
)
TRANSLATION_POLICY = (
    "해 주십시오",
    "하라",
    "해 주십시오",
    "해 주시오",
    "해 주십시오",
    "해 주시오",
    "하라",
    "합니다",
    "한다",
    "합니다",
    "하옵니다",
    "합니다",
    "합니다",
    "한다",
    "하지 마세요",
    "하지 마라",
    "하지 말아 주십시오",
    "하지 마시옵소서",
    "하지 말아 주십시오",
    "하지 마시오",
    "하지 마라",
    "지 않고",
    "지 않고",
    "지 않은 채",
    "지 않고",
    "지 않은 채로",
    "지 않고",
    "지 않고",
    "하지 않겠습니다",
    "하지 않으리",
    "하지 않겠사옵니다",
    "하지 않겠사옵니다",
    "하지 않겠습니다",
    "하지 않겠소",
    "하지 않으리",
    "죄송합니다",
    "미안하오",
    "송구하옵니다",
    "송구하옵니다",
    "죄송합니다",
    "면목이 없습니다",
    "미안하오",
    "합니다",
    "한다",
    "하옵니다",
    "하옵니다",
    "합니다",
    "하옵니다",
    "한다",
    "합니다",
    "한다",
    "합니다",
    "하옵니다",
    "합니다",
    "합니다",
    "한다",
    "하지 마시오",
    "하지 마라",
    "하지 마시오",
    "하지 마시옵소서",
    "하지 마시옵소서",
    "하지 말아 주시오",
    "하지 마라",
    "해 주십시오",
    "하라",
    "해 주시옵소서",
)
TRANSLATIONS_BY_RECORD = dict(
    zip(RECORD_IDS, TRANSLATION_POLICY, strict=True)
)
TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_SEQUENCE_SHA256 = (
    "0D725ABF6844A7335DB40385C5F3B7635AFC660DBA2654FF6DA37B297967ECC0"
)
EXPECTED_POLICY_SHA256 = (
    "6A8A0EE498D9C8417E4E5B702422029A6BBD01BC07F48A44275E43DD85258F52"
)
EXPECTED_CHANGED_LITERAL_COUNT = 27
PK_RECORD_COUNT = 21751
PK_ARCHIVE_DIGESTS = {
    "pk_jp": "E1F57A31CFC8BE9071C7BC876234EBDD73815AE024640B023E587054E7A77E95",
    "pk_current": "B3711A8709E3A3D21373E1A4CDA008023816AE975C5DB4873BF4FC8E1BC24C50",
    "pk_sc": "6AA23F763D16F186D77B2A9DAF4FFEC3B939DB122DFA673A073E8ACFB56D6816",
    "pk_tc": "6AA23F763D16F186D77B2A9DAF4FFEC3B939DB122DFA673A073E8ACFB56D6816",
    "pk_en": "6AA23F763D16F186D77B2A9DAF4FFEC3B939DB122DFA673A073E8ACFB56D6816",
}
PK_TARGET_JUMP_EDGE_SHA256 = (
    "5E9EFD1243740117E14AF6C711CFF367EECE4C9EDD92C346921A6D3F635C3500"
)
PK_FULL_GROUP_JUMP_EDGE_SHA256 = (
    "09538F3DE5775254369BBD4454B5B48C7BFE700F478D891B8A523A861CE9DA48"
)
FULL_PK_GROUPS = {
    436: tuple(range(1797, 1804)),
    442: tuple(range(1804, 1811)),
    448: tuple(range(1811, 1818)),
    1156: tuple(range(1818, 1825)),
    454: tuple(range(1825, 1832)),
    460: tuple(range(1832, 1839)),
    466: tuple(range(1839, 1846)),
    472: tuple(range(1846, 1853)),
    478: tuple(range(1853, 1860)),
    484: tuple(range(1860, 1867)),
}
RECORD_TO_ROOT = {
    record_id: root
    for root, record_ids in FULL_PK_GROUPS.items()
    for record_id in record_ids
    if record_id in RECORD_IDS
}
EXPECTED_ROOT_CLOSURES = {
    root: tuple(range(root, root + 6)) + record_ids
    for root, record_ids in FULL_PK_GROUPS.items()
}
EMPTY_CANONICAL_SHA256 = (
    "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
)
NO_CALL_EVIDENCE = (
    (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
    (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
    (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
)
EXPECTED_CALL_EVIDENCE = {
    436: NO_CALL_EVIDENCE,
    442: (
        (
            17,
            "CEE6DD4F8A014A6B44BA7FE7A02390486CE47F9CF428EE2E857A4F36F1475CDF",
            3,
            "712DBEDADD46FBEACFB8250FFCF8790D501B18943DB680B581981AEF185C06F6",
        ),
        (
            14,
            "AEF0FA5AC7933619A49B47B9AA31A69FCFC01AF6D5E1364F2B1D6DE5ABDB91AA",
            2,
            "B03CE7206E51581BA63358BD064508DA2E9CECEFC055BCFC59EAC998D8007961",
        ),
        (
            3,
            "6A615B09D4E1DDF2D3B4C844722015C68E6751E439CD603578AEB166F3846DF5",
            0,
            EMPTY_CANONICAL_SHA256,
        ),
    ),
    448: NO_CALL_EVIDENCE,
    1156: NO_CALL_EVIDENCE,
    454: NO_CALL_EVIDENCE,
    460: (
        (
            3,
            "39F9A00D10A1A077AAE04C32A8AFA9B7040A9BF83D4515EC7B279F457BAA363C",
            1,
            "EF55C2BC0F704291E4D92F3B2F0D4B33C52525B3176C32FAEFD1BC9C58A3C107",
        ),
        (
            3,
            "39F9A00D10A1A077AAE04C32A8AFA9B7040A9BF83D4515EC7B279F457BAA363C",
            1,
            "EF55C2BC0F704291E4D92F3B2F0D4B33C52525B3176C32FAEFD1BC9C58A3C107",
        ),
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
    ),
    466: (
        (
            94,
            "64ACB234AB45DEAF687686A99147220D220CC2E52BAF4671084094EEBCEB2212",
            11,
            "9007FA9F6BB2E34127533A0E4E7A2831105C636A5A8808FD8784910C1FA3F5DE",
        ),
        (
            79,
            "11FA6C0EED1D4794BC36DE72E9C542BCEA548EA8850E6B5A64B4979531BD95BE",
            11,
            "9007FA9F6BB2E34127533A0E4E7A2831105C636A5A8808FD8784910C1FA3F5DE",
        ),
        (
            15,
            "67DB2BC9B70C4FFF1F431E1F8A589963EAAD5A9CBC8D1A11FB878DB25413247A",
            0,
            EMPTY_CANONICAL_SHA256,
        ),
    ),
    472: (
        (
            6,
            "84410B226830C21DB0F7CC68434EC1F3AF561B864BA0568664683DBA6A72FEAF",
            0,
            EMPTY_CANONICAL_SHA256,
        ),
        (
            4,
            "30E6931EBB1015A7BC57D7FE0950DB2772DAF6AEE95B72C06FB2ACB9D98F83A2",
            0,
            EMPTY_CANONICAL_SHA256,
        ),
        (
            2,
            "9ECAAC5CFA667967799C6E1D455B31E6F3CDD551623037EAAC52A9D9A7BF45FE",
            0,
            EMPTY_CANONICAL_SHA256,
        ),
    ),
    478: (
        (
            2,
            "62D31FE5D6C85F2A21500B48EBE6CB55B8F0DB65953E9796F25085EA2E8BFEE3",
            0,
            EMPTY_CANONICAL_SHA256,
        ),
        (
            2,
            "62D31FE5D6C85F2A21500B48EBE6CB55B8F0DB65953E9796F25085EA2E8BFEE3",
            0,
            EMPTY_CANONICAL_SHA256,
        ),
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
    ),
    484: NO_CALL_EVIDENCE,
}
MORPHOLOGY_014C_RE = re.compile(b"\x01\x4C(.{4})", re.DOTALL)
EXPECTED_014C_OVERLAP = ((15, 25, 0, 65, 84213762),)
LEFT_BOUNDARY_IDS = FULL_PK_GROUPS[436]
LEFT_BOUNDARY_JP = EXPECTED_PK_JP[:7]
LEFT_BOUNDARY_CURRENT = (
    "해 주십시오",
    "하라",
    "해 주십시오",
    "해 주시오",
    "해 주십시오",
    "해 주시오",
    "하라",
)
LEFT_BOUNDARY_POLICY = TRANSLATION_POLICY[:7]
RIGHT_BOUNDARY_IDS = FULL_PK_GROUPS[484]
RIGHT_BOUNDARY_JP = (
    "してください",
    "せ",
    "してくださいませ",
    "してくだされ",
    "してください",
    "してくだされ",
    "せ",
)
RIGHT_BOUNDARY_CURRENT = (
    "해 주십시오",
    "세",
    "해 주시옵소서",
    "해 주시오",
    "해 주십시오",
    "해 주시오",
    "세",
)
RIGHT_BOUNDARY_POLICY = (
    "해 주십시오",
    "하라",
    "해 주시옵소서",
    "해 주시오",
    "해 주십시오",
    "해 주시오",
    "하라",
)
ROOT_ASSEMBLY_PLAN = {
    436: "caller action stem + respectful/plain request ending",
    442: "caller action stem + speaker-register finite ending",
    448: "caller action stem + prohibition ending",
    1156: "caller predicate stem + negative continuative ending",
    454: "caller action stem + negative volitional ending",
    460: "speaker-register apology",
    466: "caller action stem + speaker-register finite ending",
    472: "caller voiced action stem + speaker-register finite ending",
    478: "caller action stem + prohibition ending",
    484: "caller action stem + respectful/plain request ending",
}
BASIS = (
    "review_queue_pk_msggame_B003_zero_based_visible_ordinals134_199_"
    "pristine_pk_pc_jp_sole_translation_authority_block0_records1797_"
    "1862_66_visible_no_hidden_after_pk_only_seven_terminal_insertion_"
    "independently_pinned_pk_source_and_translation_policy_global_unique_"
    "contiguous_literal_gap_reverse_search_discovered_minus61_Base_"
    "records1736_1801_auxiliary_only_exact_pk_base_jp_current_sc_tc_"
    "empty_pk_en_subset_digests_target66_full_boundary70_014a_incoming_"
    "source_current_full_closures_0143_call_fixed_flatten_digests_raw_"
    "014c_false_positive_guard_left_full_root436_no_shared_S1031_right_"
    "root484_cross_next_batch_full_policy_request_finite_prohibition_"
    "negative_continuative_volitional_apology_register_matrices_all_"
    "runtime_pending_no_historic_or_switch_korean_authority_one_line_"
    "protected_skeleton_outside_reverse_exact_no_steam"
)


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return LEFT_BASE.literal_texts(records, key)


def gap_bytes(record: Any) -> tuple[bytes, ...]:
    return LEFT_BASE.gap_bytes(record)


def archive_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    return LEFT_BASE.archive_records(prepared)


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


def sequence_starts(
    records: dict[tuple[int, int], Any],
    sequence: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...],
) -> tuple[int, ...]:
    maximum = max(
        record_id
        for block_id, record_id in records
        if block_id == BLOCK_ID
    )
    count = len(sequence)
    return tuple(
        start
        for start in range(maximum - count + 2)
        if all(
            (BLOCK_ID, start + ordinal) in records
            for ordinal in range(count)
        )
        and record_signature(records, start, count) == sequence
    )


def assert_queue_contract(prepared: Any) -> None:
    rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line
        and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        target["coordinate"]
        for row in rows
        for target in row["target_literals"]
        if target["visible"]
    )
    hidden = tuple(
        target["coordinate"]
        for row in rows
        for target in row["target_literals"]
        if not target["visible"]
    )
    if (
        len(rows) != 200
        or len(visible) != 200
        or hidden
        or visible[QUEUE_START:QUEUE_STOP] != TARGET_COORDINATES
        or rows[0]["record_coordinate"] != "0:1663"
        or rows[-1]["record_coordinate"] != "0:1862"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} private queue ordinal contract drifted"
        )


def discover_mapping(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[dict[int, int], int]:
    expected_sequence = tuple(
        ((source,), ("", "050505"))
        for source in EXPECTED_PK_JP
    )
    pk_sequence = record_signature(
        records_by_label["pk_jp"],
        RECORD_IDS[0],
        len(RECORD_IDS),
    )
    digest = hashlib.sha256(
        json.dumps(
            pk_sequence,
            ensure_ascii=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest().upper()
    if (
        pk_sequence != expected_sequence
        or digest != EXPECTED_SEQUENCE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} expected source sequence drifted"
        )
    base_hits = sequence_starts(
        records_by_label["base_jp"],
        pk_sequence,
    )
    pk_hits = sequence_starts(
        records_by_label["pk_jp"],
        pk_sequence,
    )
    if base_hits != (1736,) or pk_hits != (1797,):
        raise RuntimeError(
            f"segment {SEGMENT} global source reverse search drifted"
        )
    offset = pk_hits[0] - base_hits[0]
    mapping = {
        pk_record_id: pk_record_id - offset
        for pk_record_id in RECORD_IDS
    }
    if offset != 61 or tuple(mapping.values()) != BASE_RECORD_IDS:
        raise RuntimeError(
            f"segment {SEGMENT} discovered record mapping drifted"
        )
    return mapping, offset


def assert_source_and_runtime(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    mapping: dict[int, int],
) -> None:
    if HELPERS.canonical_sha256(TRANSLATION_POLICY) != EXPECTED_POLICY_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} translation policy digest drifted"
        )
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
                    f"segment {SEGMENT} PK skeleton drifted: "
                    f"{label}/{pk_key}"
                )
        if literal_texts(records_by_label["pk_jp"], pk_key) != (
            EXPECTED_PK_JP[ordinal],
        ):
            raise RuntimeError(
                f"segment {SEGMENT} pristine PK source drifted: {pk_key}"
            )
        for language in ("jp", "current", "sc", "tc"):
            if (
                records_by_label[f"pk_{language}"][pk_key].data
                != records_by_label[f"base_{language}"][base_key].data
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} exact PK/Base {language} "
                    f"record mapping drifted: {pk_key}/{base_key}"
                )
        if literal_texts(records_by_label["pk_en"], pk_key) != ("",):
            raise RuntimeError(
                f"segment {SEGMENT} PK EN context drifted: {pk_key}"
            )


def assert_runtime_graph(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    target_ids = set(RECORD_IDS)
    full_ids = {
        record_id
        for record_ids in FULL_PK_GROUPS.values()
        for record_id in record_ids
    }
    if full_ids != set(range(1797, 1867)):
        raise RuntimeError(
            f"segment {SEGMENT} full PK group universe drifted"
        )
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    for label, records in (("pk_jp", source), ("pk_current", current)):
        target_edges = RIGHT_BASE.incoming_edges(records, target_ids)
        full_edges = RIGHT_BASE.incoming_edges(records, full_ids)
        if (
            len(target_edges) != 66
            or {row[2] for row in target_edges} != target_ids
            or RIGHT_BASE.digest_edges(target_edges)
            != PK_TARGET_JUMP_EDGE_SHA256
            or len(full_edges) != 70
            or {row[2] for row in full_edges} != full_ids
            or RIGHT_BASE.digest_edges(full_edges)
            != PK_FULL_GROUP_JUMP_EDGE_SHA256
        ):
            raise RuntimeError(
                f"segment {SEGMENT} independent {label} "
                "incoming jump graph drifted"
            )
        graph = HELPERS.graph_edges(records)
        for root, expected_closure in EXPECTED_ROOT_CLOSURES.items():
            actual_closure = tuple(
                sorted(HELPERS.graph_closure(graph, root))
            )
            if actual_closure != expected_closure:
                raise RuntimeError(
                    f"segment {SEGMENT} independent {label} "
                    f"closure drifted: {root}"
                )

    for root, expected_evidence in EXPECTED_CALL_EVIDENCE.items():
        source_calls = HELPERS.root_call_sites(source, root)
        current_calls = HELPERS.root_call_sites(current, root)
        source_fixed = HELPERS.fixed_following_blockers(source, root)
        current_fixed = HELPERS.fixed_following_blockers(current, root)
        source_only = tuple(
            sorted(set(source_calls) - set(current_calls))
        )
        current_only = tuple(
            sorted(set(current_calls) - set(source_calls))
        )
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
                f"segment {SEGMENT} independent PK "
                f"call/fixed/flatten evidence drifted: {root}"
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
                        RIGHT_BASE.GRAPH.MORPHOLOGY_JUMP_RE.finditer(gap)
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
                    if any(
                        match.start() in span for span in jump_spans
                    ):
                        overlapped.append(row)
                    else:
                        valid.append(row)
        if valid or tuple(overlapped) != EXPECTED_014C_OVERLAP:
            raise RuntimeError(
                f"segment {SEGMENT} independent {label} "
                "014C evidence drifted"
            )

    # These completed Base guards are auxiliary cross-checks only after all
    # independently pinned pristine-PK evidence above has passed.
    LEFT_BASE.assert_corpora(records_by_label)
    LEFT_BASE.assert_runtime_graph(records_by_label)
    LEFT_BASE.assert_fixed_following(records_by_label)
    RIGHT_BASE.assert_corpora(records_by_label)
    RIGHT_BASE.assert_runtime_graph(records_by_label)


def assert_boundaries(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    if tuple(
        literal_texts(source, (BLOCK_ID, record_id))[0]
        for record_id in LEFT_BOUNDARY_IDS
    ) != LEFT_BOUNDARY_JP:
        raise RuntimeError(
            f"segment {SEGMENT} left source boundary drifted"
        )
    if tuple(
        literal_texts(current, (BLOCK_ID, record_id))[0]
        for record_id in LEFT_BOUNDARY_IDS
    ) != LEFT_BOUNDARY_CURRENT:
        raise RuntimeError(
            f"segment {SEGMENT} left current boundary drifted"
        )
    if LEFT_BOUNDARY_POLICY != TRANSLATION_POLICY[:7]:
        raise RuntimeError(
            f"segment {SEGMENT} left policy boundary drifted"
        )
    if (
        LEFT_PK.RIGHT_NEXT_ROOT436_FULL_IDS != LEFT_BOUNDARY_IDS
        or LEFT_PK.RIGHT_NEXT_ROOT436_FULL_JP != LEFT_BOUNDARY_JP
        or LEFT_PK.RIGHT_NEXT_ROOT436_FULL_CURRENT
        != LEFT_BOUNDARY_CURRENT
        or LEFT_PK.RIGHT_NEXT_ROOT436_FULL_POLICY
        != LEFT_BOUNDARY_POLICY
    ):
        raise RuntimeError(
            f"segment {SEGMENT} S1031/root436 cross-assert drifted"
        )
    if tuple(
        literal_texts(source, (BLOCK_ID, record_id))[0]
        for record_id in RIGHT_BOUNDARY_IDS
    ) != RIGHT_BOUNDARY_JP:
        raise RuntimeError(
            f"segment {SEGMENT} right source boundary drifted"
        )
    if tuple(
        literal_texts(current, (BLOCK_ID, record_id))[0]
        for record_id in RIGHT_BOUNDARY_IDS
    ) != RIGHT_BOUNDARY_CURRENT:
        raise RuntimeError(
            f"segment {SEGMENT} right current boundary drifted"
        )
    expected_right_policy = tuple(
        RIGHT_BASE.TRANSLATIONS_BY_RECORD[record_id - 61]
        for record_id in RIGHT_BOUNDARY_IDS
    )
    if RIGHT_BOUNDARY_POLICY != expected_right_policy:
        raise RuntimeError(
            f"segment {SEGMENT} right policy boundary drifted"
        )


def assert_completed_base_policy(
    prepared: Any,
    mapping: dict[int, int],
) -> None:
    rows_by_coordinate: dict[str, dict[str, object]] = {}
    for path, expected_sha256 in BASE_DECISIONS:
        if (
            not path.is_file()
            or hashlib.sha256(path.read_bytes()).hexdigest().upper()
            != expected_sha256
        ):
            raise RuntimeError(
                f"segment {SEGMENT} completed Base decision drifted: "
                f"{path.name}"
            )
        ENGINE.validate_decisions(
            prepared,
            path,
            require_complete=False,
        )
        for line in path.read_text(encoding="utf-8").splitlines():
            if line:
                row = json.loads(line)
                rows_by_coordinate[str(row["coordinate"])] = row

    for pk_record_id, base_record_id in mapping.items():
        coordinate = f"{BLOCK_ID}:{base_record_id}:0"
        row = rows_by_coordinate.get(coordinate)
        expected = TRANSLATIONS_BY_RECORD[pk_record_id]
        if (
            row is None
            or row["resource"] != "base_msggame"
            or row["semantic_review"] != "approved"
            or row["translation"] != expected
        ):
            raise RuntimeError(
                f"segment {SEGMENT} completed Base semantic policy "
                f"drifted: {coordinate}"
            )


def assert_semantics(translations: dict[str, str]) -> None:
    if (
        translations != TRANSLATIONS
        or len(translations) != 66
        or set(TRANSLATIONS_BY_RECORD) != set(RECORD_IDS)
        or set(RECORD_TO_ROOT) != set(RECORD_IDS)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} translation universe drifted"
        )
    LEFT_BASE.assert_semantics(dict(LEFT_BASE.RAW_TRANSLATIONS))
    RIGHT_BASE.assert_semantics(dict(RIGHT_BASE.RAW_TRANSLATIONS))
    for pk_record_id, base_record_id in zip(
        RECORD_IDS,
        BASE_RECORD_IDS,
        strict=True,
    ):
        expected = (
            LEFT_BASE.TRANSLATIONS_BY_RECORD[base_record_id]
            if base_record_id <= 1742
            else RIGHT_BASE.TRANSLATIONS_BY_RECORD[base_record_id]
        )
        if TRANSLATIONS_BY_RECORD[pk_record_id] != expected:
            raise RuntimeError(
                f"segment {SEGMENT} mapped semantic policy drifted: "
                f"{pk_record_id}/{base_record_id}"
            )
    if tuple(
        TRANSLATIONS_BY_RECORD[record_id]
        for record_id in LEFT_BOUNDARY_IDS
    ) != LEFT_BOUNDARY_POLICY:
        raise RuntimeError(
            f"segment {SEGMENT} left semantic matrix drifted"
        )
    if tuple(
        TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(1860, 1863)
    ) != RIGHT_BOUNDARY_POLICY[:3]:
        raise RuntimeError(
            f"segment {SEGMENT} right semantic matrix drifted"
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
        or set(replacements) != {
            (BLOCK_ID, record_id, 0) for record_id in RECORD_IDS
        }
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate universe drifted"
        )
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
    reversed_blob = ENGINE.rebuild_packed_with_literals(
        candidate,
        reverse,
    )
    if reversed_blob != pk.current_blob:
        raise RuntimeError(
            f"segment {SEGMENT} reverse overlay is not byte-exact"
        )
    return (
        candidate,
        hashlib.sha256(candidate).hexdigest().upper(),
    )


def build_rows() -> tuple[
    Any,
    dict[str, str],
    list[dict[str, object]],
    bytes,
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
    mapping, offset = discover_mapping(records_by_label)
    assert_source_and_runtime(records_by_label, mapping)
    assert_runtime_graph(records_by_label)
    assert_boundaries(records_by_label)
    assert_completed_base_policy(prepared, mapping)
    translations = dict(TRANSLATIONS)
    assert_semantics(translations)

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
            or "\r" in translation
            or "\n" in translation
            or translation != translation.strip()
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} protected line drifted: "
                f"{coordinate}"
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
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        root = RECORD_TO_ROOT[record_id]
        evidence = EXPECTED_CALL_EVIDENCE[root]
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
                        FULL_PK_GROUPS[root]
                    ),
                    "full_graph_closure_record_ids": list(
                        EXPECTED_ROOT_CLOSURES[root]
                    ),
                    "owned_terminal_record_ids": [
                        value
                        for value in FULL_PK_GROUPS[root]
                        if value in RECORD_IDS
                    ],
                    "base_semantic_record_discovered_by_reverse_search":
                    mapping[record_id],
                    "source_call_count": evidence[0][0],
                    "current_call_count": evidence[1][0],
                    "source_fixed_following_count": evidence[0][2],
                    "current_fixed_following_count": evidence[1][2],
                    "source_calls_flattened_in_current":
                    evidence[2][0],
                    "current_only_calls": evidence[2][2],
                    "incoming_jump_graph_guarded": True,
                    "valid_incoming_014c_count": 0,
                    "automatic_space_inserted": False,
                    "runtime_integration_required": True,
                    "assembly_plan": ROOT_ASSEMBLY_PLAN[root],
                },
            }
        )
    changed = sum(
        translations[f"{BLOCK_ID}:{record_id}:0"]
        != literal_texts(current, (BLOCK_ID, record_id))[0]
        for record_id in RECORD_IDS
    )
    if changed != EXPECTED_CHANGED_LITERAL_COUNT:
        raise RuntimeError(
            f"segment {SEGMENT} changed count drifted"
        )
    return (
        prepared,
        translations,
        rows,
        candidate,
        candidate_sha256,
        offset,
    )


def main() -> int:
    first = build_rows()
    second = build_rows()
    prepared, translations, rows, candidate, candidate_sha256, offset = first
    if (
        translations != second[1]
        or ENGINE.jsonl(rows) != ENGINE.jsonl(second[2])
        or candidate != second[3]
        or candidate_sha256 != second[4]
        or offset != second[5]
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
        raise RuntimeError(
            f"segment {SEGMENT} validation count drifted"
        )
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B003_S1032",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [134, 199],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "source_literal_count": 66,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "confirmed_non_display": 0,
                "changed_literal_count": EXPECTED_CHANGED_LITERAL_COUNT,
                "base_mapping_method":
                "global_unique_contiguous_literal_gap_reverse_search",
                "discovered_base_record_range": [
                    BASE_RECORD_IDS[0],
                    BASE_RECORD_IDS[-1],
                ],
                "discovered_pk_minus_base_offset": offset,
                "source_sequence_sha256": EXPECTED_SEQUENCE_SHA256,
                "translation_policy_sha256": EXPECTED_POLICY_SHA256,
                "pk_target_incoming_sha256":
                PK_TARGET_JUMP_EDGE_SHA256,
                "pk_full_group_incoming_sha256":
                PK_FULL_GROUP_JUMP_EDGE_SHA256,
                "left_root436_full_policy":
                list(LEFT_BOUNDARY_POLICY),
                "right_root484_full_policy":
                list(RIGHT_BOUNDARY_POLICY),
                "candidate_sha256": candidate_sha256,
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
                "target_runtime_skeleton_exact": True,
                "full_graph_closures_exact": True,
                "call_fixed_flatten_evidence_exact": True,
                "valid_incoming_014c_count": 0,
                "s1031_root436_boundary_cross_assert_exact": True,
                "right_root484_cross_next_full_assert_exact": True,
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
