#!/usr/bin/env python3
"""Build PK block-0 runtime-terminal segment 1035 decisions."""

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

import build_base_batch004_segment1013 as LEFT_BASE
import build_base_batch004_segment1014 as RIGHT_BASE
import build_pk_batch001_segment1025 as HELPERS
import build_pk_batch004_segment1034 as LEFT_PK


ENGINE = LEFT_BASE.ENGINE
GENERAL = LEFT_BASE.GENERAL
UTIL = LEFT_BASE.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B004_S1035.private.v1.jsonl"
)
BASE_DECISIONS = (
    (
        REPO
        / "tmp"
        / WORKSTREAM.name
        / "decisions"
        / "base_msggame_B004_S1013.private.v1.jsonl",
        "AC2133A77B6E899AD6179ADA394D17ABCCB20C851F1CBC270CBAC541A5EABFEA",
    ),
    (
        REPO
        / "tmp"
        / WORKSTREAM.name
        / "decisions"
        / "base_msggame_B004_S1014.private.v1.jsonl",
        "DCB63A91FEBA238727F7CCDC6911D974E40E19E64CC93A86DEA65BC39D6D5F2F",
    ),
)
SEGMENT = 1035
QUEUE_BATCH_ID = "pk_msggame-B004"
BLOCK_ID = 0
QUEUE_START = 134
QUEUE_STOP = 200
BASE_RECORD_IDS = tuple(range(1934, 2000))
RECORD_IDS = tuple(record_id + 68 for record_id in BASE_RECORD_IDS)
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
TARGET_COORDINATES = tuple(
    f"{BLOCK_ID}:{record_id}:0" for record_id in RECORD_IDS
)
QUEUE_HIDDEN_COORDINATES = (
    "0:1888:0",
    "0:1889:0",
    "0:1895:0",
    "0:1897:0",
    "0:1899:0",
)
EXPECTED_PK_JP = (
    "でしょう",
    "でしょう",
    "でしょう",
    "でしょう",
    "だろう",
    "でしょう",
    "であろう",
    "でございましょう",
    "でございましょう",
    "でありましょう",
    "でござろう",
    "であろう",
    "ちます",
    "つ",
    "ちます",
    "ちます",
    "ちます",
    "ちます",
    "つ",
    "りました",
    "った",
    "りました",
    "りました",
    "りました",
    "りました",
    "った",
    "いました",
    "った",
    "いました",
    "いました",
    "いました",
    "いました",
    "った",
    "ちました",
    "った",
    "ちました",
    "ちました",
    "ちました",
    "ちました",
    "った",
    "って",
    "って",
    "まして",
    "まして",
    "って",
    "って",
    "って",
    "て",
    "て",
    "まして",
    "まして",
    "まして",
    "て",
    "て",
    "ちなされ",
    "て",
    "ちなされ",
    "ちなされ",
    "ってください",
    "ってくだされ",
    "て",
    "で",
    "で",
    "でございまして",
    "でして",
    "でして",
)
TRANSLATION_POLICY = (
    "이겠지요",
    "이겠지요",
    "이겠지요",
    "이겠지요",
    "이겠지",
    "이겠지요",
    "이리라",
    "이겠사옵니다",
    "이겠사옵니다",
    "이겠지요",
    "이리다",
    "이리라",
    "합니다",
    "한다",
    "합니다",
    "합니다",
    "합니다",
    "합니다",
    "한다",
    "했습니다",
    "했다",
    "했습니다",
    "했습니다",
    "했습니다",
    "했습니다",
    "했다",
    "했습니다",
    "했다",
    "했습니다",
    "했습니다",
    "했습니다",
    "했습니다",
    "했다",
    "했습니다",
    "했다",
    "했습니다",
    "했습니다",
    "했습니다",
    "했습니다",
    "했다",
    "하여",
    "하여",
    "하여",
    "하여",
    "하여",
    "하여",
    "하여",
    "하여",
    "하여",
    "하여",
    "하여",
    "하여",
    "하여",
    "하여",
    "하시오",
    "하라",
    "하시오",
    "하시오",
    "해 주십시오",
    "해 주시오",
    "하라",
    "이고",
    "이고",
    "이옵고",
    "이며",
    "이며",
)
TRANSLATIONS_BY_RECORD = dict(
    zip(RECORD_IDS, TRANSLATION_POLICY, strict=True)
)
TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_SEQUENCE_SHA256 = (
    "1930BF6F188C02CB4CA4B959B54A179BB4F89E7FEB7DEBD7C9B36511EBF71892"
)
EXPECTED_POLICY_SHA256 = (
    "C7C8257D87F17E3F6F281A68C01B45A5537396DE01753373885C5E2129BDD298"
)
EXPECTED_CHANGED_LITERAL_COUNT = 32
PK_RECORD_COUNT = 21751
PK_ARCHIVE_DIGESTS = {
    "pk_jp": "61C71161C4D363CFC23771DCED4CCB0300D8485C3601C50888FE1D1A122B9E2C",
    "pk_current": "173F72CD611DCF15ABDCE4F0D41D9D16E5C50E7FB1136ABC1C3CC0A3D25D95EB",
    "pk_sc": "0DCE9085876118419103ED2E4A1C7738205AEAFEE9DD42489EA1FEBC30D8D573",
    "pk_tc": "0DCE9085876118419103ED2E4A1C7738205AEAFEE9DD42489EA1FEBC30D8D573",
    "pk_en": "0DCE9085876118419103ED2E4A1C7738205AEAFEE9DD42489EA1FEBC30D8D573",
}
PK_TARGET_JUMP_EDGE_SHA256 = (
    "016CF56BD83A499EF0019C4CBCD2E9CA80D2755EC4A5E1E4D3D5895E4CAB9CDD"
)
PK_FULL_GROUP_JUMP_EDGE_SHA256 = (
    "E9F7C566678475C037C1B8595E1FD7F5C3A2D95FF83B1C61F140530C70144DEC"
)
EXPECTED_CALL_EVIDENCE_SHA256 = (
    "B93886E8F7D42A06FC2A9EC62F660FF4B11F78854328050E7333CF2C2253B7B9"
)
FULL_PK_GROUPS = {
    610: tuple(range(2000, 2007)),
    616: tuple(range(2007, 2014)),
    622: tuple(range(2014, 2021)),
    628: tuple(range(2021, 2028)),
    634: tuple(range(2028, 2035)),
    640: tuple(range(2035, 2042)),
    646: tuple(range(2042, 2049)),
    652: tuple(range(2049, 2056)),
    658: tuple(range(2056, 2063)),
    664: tuple(range(2063, 2070)),
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
LEFT_BOUNDARY_IDS = FULL_PK_GROUPS[610]
LEFT_BOUNDARY_JP = (
    "でしょう",
    "であろう",
    "でしょう",
    "でしょう",
    "でしょう",
    "でしょう",
    "だろう",
)
LEFT_BOUNDARY_CURRENT = (
    "이겠지요",
    "이리라",
    "이겠지요",
    "이겠지요",
    "이겠지요",
    "이겠지요",
    "이겠지",
)
LEFT_BOUNDARY_POLICY = LEFT_BOUNDARY_CURRENT
RIGHT_BOUNDARY_IDS = FULL_PK_GROUPS[664]
RIGHT_BOUNDARY_JP = (
    "で",
    "で",
    "でございまして",
    "でして",
    "でして",
    "で",
    "で",
)
RIGHT_BOUNDARY_CURRENT = (
    "에서",
    "에서",
    "이옵고",
    "이어서",
    "이어서",
    "에서",
    "에서",
)
RIGHT_BOUNDARY_POLICY = (
    "이고",
    "이고",
    "이옵고",
    "이며",
    "이며",
    "이고",
    "이고",
)
MORPHOLOGY_014C_RE = re.compile(b"\x01\x4C(.{4})", re.DOTALL)
EXPECTED_014C_OVERLAP = ((15, 25, 0, 65, 84213762),)
ROOT_ASSEMBLY_PLAN = {
    610: (
        "normalize a Korean nominal/predicate caller before the "
        "conjectural ending; flatten callers with incompatible fixed text"
    ),
    616: "caller nominal/predicate stem + high-register conjectural ending",
    622: "caller action stem + speaker-register finite ending",
    628: (
        "rewrite to a source-free Korean action noun before "
        "했습니다/했다, or flatten an already complete caller"
    ),
    634: (
        "rewrite to a source-free Korean action noun before "
        "했습니다/했다; flatten incompatible fixed continuations"
    ),
    640: (
        "both live callers have incompatible fixed continuations and "
        "must be flattened in the caller rather than directly composed"
    ),
    646: "no live caller; retain source semantics as connective 하여",
    652: "live 아뢰 caller composes directly as 아뢰하여도",
    658: "caller action stem + command/request ending",
    664: "caller nominal stem + connective copula ending",
}
CALLER_INTEGRATION_EVIDENCE = {
    610: (
        {
            "call_site": "6:3539:3:0",
            "observed_current_left": "의 패업을 뒷받침하기엔 힘이 부족",
            "observed_current_right": "",
            "integration_mode": "normalize_and_retain_terminal",
            "source_free_korean_example": (
                "의 패업을 뒷받침하기엔 역부족이겠지요"
            ),
        },
        {
            "call_site": "6:3503:1:0",
            "observed_current_left": (
                "에 승진할 기회가 돌아오다니\n"
                "참으로 고마운 일이로다"
            ),
            "observed_current_right": "인가",
            "integration_mode": "flatten_command_in_caller",
            "source_free_korean_example": (
                "에 승진할 기회가 돌아오다니\n참으로 고마운 일인가"
            ),
        },
    ),
    628: (
        {
            "call_site": "8:1198:1:0",
            "observed_current_left": (
                "금 광맥을 파냈다고\n백성이 보고를"
            ),
            "observed_current_right": "\n채굴에 나서는 것이 어떠할지",
            "integration_mode": "normalize_and_retain_terminal",
            "source_free_korean_example": (
                "금 광맥을 파냈다고\n백성이 보고했습니다\n"
                "채굴에 나서는 것이 어떠할지"
            ),
        },
        {
            "call_site": "15:473:5:0",
            "observed_current_left": "에게 배반",
            "observed_current_right": "！",
            "integration_mode": "direct_composition",
            "source_free_korean_example": "에게 배반했습니다！",
        },
    ),
    634: (
        {
            "call_site": "6:4616:1:0",
            "observed_current_left": "또 왔나 싶었습니",
            "observed_current_right": "만…\n설마",
            "integration_mode": "normalize_and_retain_terminal",
            "source_free_korean_example": "또 왔나 생각했습니다만…\n설마",
        },
        {
            "call_site": "7:884:1:0",
            "observed_current_left": "를 일으키고 말",
            "observed_current_right": (
                "인가…\n그렇다면 그 이빨, 막아야 한다"
            ),
            "integration_mode": "flatten_command_in_caller",
            "source_free_korean_example": (
                "를 일으키고 말았는가…\n"
                "그렇다면 그 이빨, 막아야 한다"
            ),
        },
    ),
    640: (
        {
            "call_site": "8:296:2:0",
            "observed_current_left": "이지만\n미리 대책을 세운",
            "observed_current_right": (
                "이(가) 있었기에\n무사히 넘길 수 있었던 땅이"
            ),
            "integration_mode": "flatten_command_in_caller",
            "source_free_korean_example": (
                "이지만\n미리 대책을 세웠기에\n"
                "무사히 넘길 수 있었던 땅이"
            ),
        },
        {
            "call_site": "8:316:2:0",
            "observed_current_left": "\n선수를 치",
            "observed_current_right": (
                "지역은, 그로 인해\n화를 면할 수 있어"
            ),
            "integration_mode": "flatten_command_in_caller",
            "source_free_korean_example": (
                "\n선수를 친 지역은, 그로 인해\n화를 면할 수 있어"
            ),
        },
    ),
    652: (
        {
            "call_site": "6:3548:1:0",
            "observed_current_left": "라 아뢰",
            "observed_current_right": "도\n",
            "integration_mode": "direct_composition",
            "source_free_korean_example": "라 아뢰하여도\n",
        },
    ),
}
BASIS = (
    "review_queue_pk_msggame_B004_zero_based_visible_ordinals134_199_"
    "pristine_pk_pc_jp_sole_translation_authority_block0_records2002_"
    "2067_66_visible_after_two_pk_only_terminal_insertions_queue_hidden_"
    "five_all_outside_owned_slice_independently_pinned_pk_source_policy_"
    "global_unique_contiguous_literal_gap_reverse_search_discovered_"
    "minus68_Base_records1934_1999_auxiliary_only_exact_pk_base_jp_"
    "current_sc_tc_empty_pk_en_subset_digests_target66_full_boundary70_"
    "014a_incoming_source_current_full_closures_0143_call_fixed_flatten_"
    "aggregate_digest_014c_valid_zero_overlap_false_positive_one_left_"
    "root610_cross_S1034_right_root664_cross_next_full_policies_"
    "conjectural_finite_past_connective_command_copula_register_matrices_"
    "source_free_current_caller_normalize_or_flatten_examples_pinned_"
    "all_runtime_pending_no_historic_or_switch_korean_authority_one_line_"
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


def incoming_jump_rows(
    records: dict[tuple[int, int], Any],
    target_ids: set[int],
) -> tuple[tuple[int, int, int, int, int], ...]:
    rows: list[tuple[int, int, int, int, int]] = []
    for key in sorted(records):
        for gap_id, gap in enumerate(gap_bytes(records[key])):
            for match in HELPERS.MORPHOLOGY_JUMP_RE.finditer(gap):
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
        len(rows) != 205
        or len(visible) != 200
        or hidden != QUEUE_HIDDEN_COORDINATES
        or visible[QUEUE_START:QUEUE_STOP] != TARGET_COORDINATES
        or rows[0]["record_coordinate"] != "0:1863"
        or rows[-1]["record_coordinate"] != "0:2067"
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
    digest = hashlib.sha256(
        json.dumps(
            expected_sequence,
            ensure_ascii=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest().upper()
    if digest != EXPECTED_SEQUENCE_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} expected source sequence drifted"
        )
    base_hits = sequence_starts(
        records_by_label["base_jp"],
        expected_sequence,
    )
    pk_hits = sequence_starts(
        records_by_label["pk_jp"],
        expected_sequence,
    )
    if base_hits != (1934,) or pk_hits != (2002,):
        raise RuntimeError(
            f"segment {SEGMENT} global source reverse search drifted"
        )
    offset = pk_hits[0] - base_hits[0]
    mapping = {
        pk_record_id: pk_record_id - offset
        for pk_record_id in RECORD_IDS
    }
    if offset != 68 or tuple(mapping.values()) != BASE_RECORD_IDS:
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
        if GENERAL.subset_digest(
            records_by_label[label],
            RECORD_KEYS,
        ) != expected_digest:
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
            if literal_texts(
                records_by_label[f"pk_{language}"],
                pk_key,
            ) != literal_texts(
                records_by_label[f"base_{language}"],
                base_key,
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} PK/Base {language} mapping "
                    f"drifted: {pk_key}/{base_key}"
                )
        if literal_texts(records_by_label["pk_en"], pk_key) != ("",):
            raise RuntimeError(
                f"segment {SEGMENT} PK EN context drifted: {pk_key}"
            )


def collect_call_evidence(
    source: dict[tuple[int, int], Any],
    current: dict[tuple[int, int], Any],
) -> dict[str, tuple[tuple[int | str, ...], ...]]:
    evidence: dict[str, tuple[tuple[int | str, ...], ...]] = {}
    for root in FULL_PK_GROUPS:
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
        evidence[str(root)] = (
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
    return evidence


def assert_caller_integration_evidence(
    current: dict[tuple[int, int], Any],
) -> None:
    for root, examples in CALLER_INTEGRATION_EVIDENCE.items():
        actual_calls = set(HELPERS.root_call_sites(current, root))
        for example in examples:
            call_site = str(example["call_site"])
            if call_site not in actual_calls:
                raise RuntimeError(
                    f"segment {SEGMENT} caller example site drifted: "
                    f"{root}/{call_site}"
                )
            block_id, record_id, gap_id, _ = (
                int(value) for value in call_site.split(":")
            )
            literals = ENGINE.parse_record_literals(
                current[(block_id, record_id)]
            )
            left = literals[gap_id - 1].text if gap_id else ""
            right = (
                literals[gap_id].text
                if gap_id < len(literals)
                else ""
            )
            if (
                left != example["observed_current_left"]
                or right != example["observed_current_right"]
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} caller example context drifted: "
                    f"{root}/{call_site}"
                )


def assert_runtime_graph(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[str, tuple[tuple[int | str, ...], ...]]:
    target_ids = set(RECORD_IDS)
    full_ids = {
        record_id
        for record_ids in FULL_PK_GROUPS.values()
        for record_id in record_ids
    }
    if full_ids != set(range(2000, 2070)):
        raise RuntimeError(
            f"segment {SEGMENT} full PK group universe drifted"
        )
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    for label, records in (("pk_jp", source), ("pk_current", current)):
        target_edges = incoming_jump_rows(records, target_ids)
        full_edges = incoming_jump_rows(records, full_ids)
        if (
            len(target_edges) != 66
            or {row[4] for row in target_edges} != target_ids
            or HELPERS.canonical_sha256(target_edges)
            != PK_TARGET_JUMP_EDGE_SHA256
            or len(full_edges) != 70
            or {row[4] for row in full_edges} != full_ids
            or HELPERS.canonical_sha256(full_edges)
            != PK_FULL_GROUP_JUMP_EDGE_SHA256
        ):
            raise RuntimeError(
                f"segment {SEGMENT} independent {label} "
                "incoming jump graph drifted"
            )
        graph = HELPERS.graph_edges(records)
        for root, expected_closure in EXPECTED_ROOT_CLOSURES.items():
            if tuple(
                sorted(HELPERS.graph_closure(graph, root))
            ) != expected_closure:
                raise RuntimeError(
                    f"segment {SEGMENT} independent {label} "
                    f"closure drifted: {root}"
                )

        valid: list[tuple[int, int, int, int, int]] = []
        overlapped: list[tuple[int, int, int, int, int]] = []
        for (block_id, record_id), record in sorted(records.items()):
            for gap_id, gap in enumerate(gap_bytes(record)):
                jump_spans = [
                    range(match.start(), match.end())
                    for match in HELPERS.MORPHOLOGY_JUMP_RE.finditer(gap)
                ]
                for match in MORPHOLOGY_014C_RE.finditer(gap):
                    row = (
                        block_id,
                        record_id,
                        gap_id,
                        match.start(),
                        struct.unpack("<I", match.group(1))[0],
                    )
                    if any(match.start() in span for span in jump_spans):
                        overlapped.append(row)
                    else:
                        valid.append(row)
        if valid or tuple(overlapped) != EXPECTED_014C_OVERLAP:
            raise RuntimeError(
                f"segment {SEGMENT} independent {label} "
                "014C evidence drifted"
            )

    evidence = collect_call_evidence(source, current)
    if (
        HELPERS.canonical_sha256(evidence)
        != EXPECTED_CALL_EVIDENCE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} independent PK "
            "call/fixed/flatten evidence drifted"
        )
    assert_caller_integration_evidence(current)

    # Completed Base guards are auxiliary cross-checks after all independently
    # pinned pristine-PK evidence has passed.
    LEFT_BASE.assert_corpora(records_by_label)
    LEFT_BASE.assert_runtime_graph(records_by_label)
    RIGHT_BASE.assert_corpora(records_by_label)
    RIGHT_BASE.assert_runtime_graph(records_by_label)
    return evidence


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
    if LEFT_BOUNDARY_POLICY != tuple(
        LEFT_BASE.FULL_TRANSLATION_POLICY[record_id - 68]
        for record_id in LEFT_BOUNDARY_IDS
    ):
        raise RuntimeError(
            f"segment {SEGMENT} left policy boundary drifted"
        )
    if (
        LEFT_BOUNDARY_IDS != LEFT_PK.RIGHT_ROOT610_FULL_IDS
        or LEFT_BOUNDARY_JP != LEFT_PK.RIGHT_ROOT610_FULL_JP
        or LEFT_BOUNDARY_CURRENT
        != LEFT_PK.RIGHT_ROOT610_FULL_CURRENT
        or LEFT_BOUNDARY_POLICY != LEFT_PK.RIGHT_ROOT610_FULL_POLICY
    ):
        raise RuntimeError(
            f"segment {SEGMENT} S1034/S1035 root610 contract drifted"
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
    if RIGHT_BOUNDARY_POLICY != tuple(
        RIGHT_BASE.FULL_TRANSLATION_POLICY[record_id - 68]
        for record_id in RIGHT_BOUNDARY_IDS
    ):
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
    LEFT_BASE.assert_semantics(dict(LEFT_BASE.TRANSLATIONS))
    RIGHT_BASE.assert_semantics(dict(RIGHT_BASE.RAW_TRANSLATIONS))
    for pk_record_id, base_record_id in zip(
        RECORD_IDS,
        BASE_RECORD_IDS,
        strict=True,
    ):
        expected = (
            LEFT_BASE.TRANSLATIONS_BY_RECORD[base_record_id]
            if base_record_id <= 1947
            else RIGHT_BASE.TRANSLATIONS_BY_RECORD[base_record_id]
        )
        if TRANSLATIONS_BY_RECORD[pk_record_id] != expected:
            raise RuntimeError(
                f"segment {SEGMENT} mapped semantic policy drifted: "
                f"{pk_record_id}/{base_record_id}"
            )
    if tuple(
        TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(2002, 2007)
    ) != LEFT_BOUNDARY_POLICY[2:]:
        raise RuntimeError(
            f"segment {SEGMENT} left semantic matrix drifted"
        )
    if tuple(
        TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(2063, 2068)
    ) != RIGHT_BOUNDARY_POLICY[:5]:
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
    if ENGINE.rebuild_packed_with_literals(
        candidate,
        reverse,
    ) != pk.current_blob:
        raise RuntimeError(
            f"segment {SEGMENT} reverse overlay is not byte-exact"
        )
    return candidate, hashlib.sha256(candidate).hexdigest().upper()


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
    call_evidence = assert_runtime_graph(records_by_label)
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
        evidence = call_evidence[str(root)]
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
                    "source_calls_flattened_in_current": evidence[2][0],
                    "current_only_call_count": evidence[2][2],
                    "incoming_jump_graph_guarded": True,
                    "valid_incoming_014c_count": 0,
                    "automatic_space_inserted": False,
                    "runtime_integration_required": True,
                    "assembly_plan": ROOT_ASSEMBLY_PLAN[root],
                    "source_free_caller_integration_examples": list(
                        CALLER_INTEGRATION_EVIDENCE.get(root, ())
                    ),
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
                "segment": "pk_msggame_B004_S1035",
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
                "pk_call_fixed_flatten_evidence_sha256":
                EXPECTED_CALL_EVIDENCE_SHA256,
                "valid_incoming_014c_count": 0,
                "left_root610_full_policy":
                list(LEFT_BOUNDARY_POLICY),
                "right_root664_full_policy":
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
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "s1034_root610_boundary_contract_exact": True,
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
