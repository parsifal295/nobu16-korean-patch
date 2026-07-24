#!/usr/bin/env python3
"""Build Base block-0 runtime-terminal segment 1022 decisions."""

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
import build_base_batch007_segment1021 as PREVIOUS


ENGINE = PRIOR.ENGINE
GENERAL = PRIOR.GENERAL
UTIL = PRIOR.UTIL
GRAPH = PRIOR.GRAPH
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B007_S1022.private.v1.jsonl"
)
SEGMENT = 1022
QUEUE_BATCH_ID = "base_msggame-B007"
BLOCK_ID = 0
RECORD_IDS = tuple(range(2486, 2552))
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
EXPECTED_CHANGED_LITERAL_COUNT = 50
PK_RECORD_OFFSET = 68
PK_ROOT_SHIFT = 12

FULL_TERMINAL_GROUPS = {
    1060: tuple(range(2485, 2492)),
    1066: tuple(range(2492, 2499)),
    1072: tuple(range(2499, 2506)),
    1078: tuple(range(2506, 2513)),
    1084: tuple(range(2513, 2520)),
    1090: tuple(range(2520, 2527)),
    1096: tuple(range(2527, 2534)),
    1102: tuple(range(2534, 2541)),
    1108: tuple(range(2541, 2548)),
    1114: tuple(range(2548, 2555)),
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
ACTUAL_CALL_ROOTS_BY_BASE = {
    root: ((root, root + 1) if root == 1060 else (root,))
    for root in FULL_TERMINAL_GROUPS
}
ACTUAL_CALL_ROOTS_BY_PK = {
    root: tuple(
        actual_root + PK_ROOT_SHIFT
        for actual_root in ACTUAL_CALL_ROOTS_BY_BASE[root]
    )
    for root in FULL_TERMINAL_GROUPS
}
PK_RECORD_MAP = {
    (BLOCK_ID, record_id): (BLOCK_ID, record_id + PK_RECORD_OFFSET)
    for record_id in range(2485, 2555)
}

SOURCE_JP_BY_ROOT = {
    1060: (
        "良いでしょう",
        "良かろう",
        "良いでしょう",
        "良いでしょう",
        "良いでしょう",
        "良いでしょう",
        "良かろう",
    ),
    1066: (
        "りません",
        "らぬ",
        "りません",
        "りませぬ",
        "りません",
        "りませぬ",
        "らん",
    ),
    1072: (
        "られません",
        "られぬ",
        "られませぬ",
        "られませぬ",
        "られません",
        "られません",
        "られん",
    ),
    1078: (
        "ります",
        "る",
        "ります",
        "ります",
        "ります",
        "ります",
        "る",
    ),
    1084: (
        "ます",
        "る",
        "まする",
        "まする",
        "ます",
        "ます",
        "る",
    ),
    1090: (
        "ないでください",
        "るな",
        "ないでください",
        "ないでくだされ",
        "ないでください",
        "ないでくだされ",
        "るでない",
    ),
    1096: (
        "りなさい",
        "れ",
        "りください",
        "りくだされ",
        "ってください",
        "りなされ",
        "れ",
    ),
    1102: (
        "れません",
        "れぬ",
        "れませぬ",
        "れませぬ",
        "れません",
        "れませぬ",
        "れん",
    ),
    1108: (
        "なさい",
        "ろ",
        "なさい",
        "なされ",
        "なさい",
        "なされ",
        "ろ",
    ),
    1114: (
        "りましょう",
        "ろう",
        "りましょう",
        "りましょう",
        "りましょう",
        "りましょう",
        "ろう",
    ),
}

CURRENT_KO_BY_ROOT = {
    1060: (
        "좋겠지요",
        "좋겠다",
        "좋겠지요",
        "좋겠지요",
        "좋겠지요",
        "좋겠지요",
        "좋겠다",
    ),
    1066: (
        "하지 않습니다",
        "않는",
        "하지 않습니다",
        "하지 않습니다",
        "하지 않습니다",
        "하지 않습니다",
        "않",
    ),
    1072: (
        "할 수 없습니다",
        "할 수 없",
        "할 수 없습니다",
        "할 수 없습니다",
        "할 수 없습니다",
        "할 수 없습니다",
        "할 수 없",
    ),
    1078: (
        "합니다",
        "다",
        "합니다",
        "합니다",
        "합니다",
        "합니다",
        "다",
    ),
    1084: (
        "합니다",
        "다",
        "하옵니다",
        "하옵니다",
        "합니다",
        "합니다",
        "다",
    ),
    1090: (
        "하지 마십시오",
        "하지 마라",
        "하지 마십시오",
        "하지 마시오",
        "하지 마십시오",
        "하지 마시오",
        "하지 마라",
    ),
    1096: (
        "하시오",
        "라",
        "십시오",
        "시오",
        "해 주세요",
        "하시오",
        "라",
    ),
    1102: (
        "할 수 없습니다",
        "할 수 없",
        "할 수 없습니다",
        "할 수 없습니다",
        "할 수 없습니다",
        "할 수 없습니다",
        "할 수 없",
    ),
    1108: (
        "하시오",
        "라",
        "하시오",
        "하시오",
        "하시오",
        "하시오",
        "라",
    ),
    1114: (
        "합시다",
        "하리라",
        "합시다",
        "합시다",
        "합시다",
        "합시다",
        "하리라",
    ),
}

TRANSLATION_POLICY_BY_ROOT = {
    1060: (
        "좋겠지요",
        "좋겠다",
        "좋겠사옵니다",
        "좋겠사옵니다",
        "좋겠지요",
        "좋겠소",
        "좋겠다",
    ),
    1066: (
        "지 않습니다",
        "지 않는다",
        "지 않습니다",
        "지 않사옵니다",
        "지 않습니다",
        "지 않사옵니다",
        "지 않는다",
    ),
    1072: (
        "수 없습니다",
        "수 없다",
        "수 없사옵니다",
        "수 없사옵니다",
        "수 없습니다",
        "수 없습니다",
        "수 없다",
    ),
    1078: (
        "합니다",
        "한다",
        "합니다",
        "합니다",
        "합니다",
        "합니다",
        "한다",
    ),
    1084: (
        "합니다",
        "한다",
        "하옵니다",
        "하옵니다",
        "합니다",
        "합니다",
        "한다",
    ),
    1090: (
        "지 마십시오",
        "지 마라",
        "지 마십시오",
        "지 마시오",
        "지 마십시오",
        "지 마시오",
        "지 마라",
    ),
    1096: (
        "하십시오",
        "하라",
        "해 주십시오",
        "해 주시오",
        "해 주십시오",
        "하시오",
        "하라",
    ),
    1102: (
        "수 없습니다",
        "수 없다",
        "수 없사옵니다",
        "수 없사옵니다",
        "수 없습니다",
        "수 없사옵니다",
        "수 없다",
    ),
    1108: (
        "하십시오",
        "하라",
        "하십시오",
        "하시오",
        "하십시오",
        "하시오",
        "하라",
    ),
    1114: (
        "겠습니다",
        "겠다",
        "겠사옵니다",
        "겠사옵니다",
        "겠습니다",
        "겠소",
        "겠다",
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
    2485: FULL_TRANSLATION_POLICY[2485],
    2552: FULL_TRANSLATION_POLICY[2552],
    2553: FULL_TRANSLATION_POLICY[2553],
    2554: FULL_TRANSLATION_POLICY[2554],
}

ARCHIVE_TARGET_DIGESTS = {
    "base_jp": "011075C394D7DD6CD362144FF5C2FA02F3A686978EED71662C3C506F34F972BF",
    "base_current": "D63579BCE10EBEC4EA7C66E83AD2DCCAE094F31CE53A0E61F3620C63D4870B21",
    "base_sc": "2539EE25CDB8A0BFF13B3FD6D2DED7A013CD9B86139499DF9712DB53A004D28E",
    "base_tc": "2539EE25CDB8A0BFF13B3FD6D2DED7A013CD9B86139499DF9712DB53A004D28E",
    "pk_jp": "1FCFECE233268E624B5D50149F08A42B3E456196090A2CEDE149D41466812D1E",
    "pk_current": "027B28F99F8EABC452F703CCFB0461C848F8BE279E45D4640A87F019F1A9F85C",
    "pk_sc": "14A90656FF02D765492D12488944E1B8F915517EBA64355C37D108E195C29D73",
    "pk_tc": "14A90656FF02D765492D12488944E1B8F915517EBA64355C37D108E195C29D73",
    "pk_en": "14A90656FF02D765492D12488944E1B8F915517EBA64355C37D108E195C29D73",
}
ARCHIVE_FULL_DIGESTS = {
    "base_jp": "5A26171E53DBC6B216E07B662A6ED68273A5DB51E212BFE63153DB213E75378C",
    "base_current": "7D61633E24922FB7235AC0EB523F1B24ECDEF8B4053A0E42FF980A3D36ED6716",
    "base_sc": "0AE5C0C06CB6696030E4C7C810F6B21A92B6E4C65AE509A705746EA540B4ECA3",
    "base_tc": "0AE5C0C06CB6696030E4C7C810F6B21A92B6E4C65AE509A705746EA540B4ECA3",
    "pk_jp": "6931174E84433058A287DF01C88F4EAC176138496FF9AFCF81005CFF0C581808",
    "pk_current": "201C527D0CAD5132F83CFB16A6CFB84100AE790685CAEA572147AB88ED419214",
    "pk_sc": "8438BBEFEAC9DD1F4952E412B4677FEF7CA1986B0421263F1F6AEE09DE400EF5",
    "pk_tc": "8438BBEFEAC9DD1F4952E412B4677FEF7CA1986B0421263F1F6AEE09DE400EF5",
    "pk_en": "8438BBEFEAC9DD1F4952E412B4677FEF7CA1986B0421263F1F6AEE09DE400EF5",
}
JUMP_EVIDENCE = {
    "base_jp": {
        "target": (
            66,
            "D449FD8A2C75E5AC82CE0C9F54EDBF27EEEC573143A710C0FAA9C5148820AB6D",
        ),
        "full": (
            70,
            "781421021FDEF77416610C1CD8FF89DCFC5CC5F4CC24BB101E923FFBF8B90C0B",
        ),
    },
    "base_current": {
        "target": (
            66,
            "D449FD8A2C75E5AC82CE0C9F54EDBF27EEEC573143A710C0FAA9C5148820AB6D",
        ),
        "full": (
            70,
            "781421021FDEF77416610C1CD8FF89DCFC5CC5F4CC24BB101E923FFBF8B90C0B",
        ),
    },
    "pk_jp": {
        "target": (
            66,
            "15AAC93129FFC7DE0F9C6E5049C3FD674311669D627C1867CA2C0CC8A8502DF4",
        ),
        "full": (
            70,
            "D6C71FC747DD672A4F4F4FAE526AC3965D977E4D483210F813DFE107B75CABF2",
        ),
    },
    "pk_current": {
        "target": (
            66,
            "15AAC93129FFC7DE0F9C6E5049C3FD674311669D627C1867CA2C0CC8A8502DF4",
        ),
        "full": (
            70,
            "D6C71FC747DD672A4F4F4FAE526AC3965D977E4D483210F813DFE107B75CABF2",
        ),
    },
}
CALL_EVIDENCE = {
    "base_jp": (
        382,
        76,
        "16852FC1C2F751789D95390AC3147EDE477DE2E527A21DE6B0DC4DCFAB73F28A",
    ),
    "base_current": (
        330,
        70,
        "30076E4E3BBE162868E4ABAE27A4EA5ECE5517FE567A6DFF49F4F7D7B8FFDA1C",
    ),
    "pk_jp": (
        506,
        107,
        "D56026A8E3025688D3DD19E86EA278F98A99C211F9CCF9400A9E1E827DB1C116",
    ),
    "pk_current": (
        462,
        102,
        "0564F8318C07D8E21179615FF7D53C34062CA8E2925577A62920C223208C802C",
    ),
}
FLATTEN_EVIDENCE = {
    "base": (
        52,
        "8CDFE7F019F3A01338599300ADF5DD2DB6CB3604286AAC08E58F376D7A27F717",
    ),
    "pk": (
        44,
        "A7D776C1E929582F592446C30EE4B9C34CD201CD4049A53A92C1A49D2ECE1F99",
    ),
}
EMPTY_CURRENT_ONLY_FLATTEN_DIGEST = (
    "28EB118DA6659780CEF153CEBE3877B9D3019122CC7C8A25840852946B764A63"
)

INTEGRATION_NOTES = {
    1060: (
        "good-judgment predicate used after no-ga and in threat or "
        "completion contexts; the S1021 boundary policy preserves neutral, "
        "plain, courtly, and archaic voices; root1061 (PK1073) is a genuine "
        "two-leaf alias caller of the same group"
    ),
    1066: (
        "productive r-stem negative used by betrayal, cost, insufficiency, "
        "negative questions, and fixed following particles"
    ),
    1072: (
        "productive negative potential used by entrust and cannot-remain "
        "callers; caller stems must be normalized before integration"
    ),
    1078: (
        "high-volume productive r-verb affirmative terminal; lexical "
        "predicates and fixed following particles require caller rewriting"
    ),
    1084: (
        "high-volume productive affirmative terminal with masu, plain ru, "
        "and masuru registers; callers require shared predicate normalization"
    ),
    1090: (
        "negative command used by forget, give-up, and hurry callers; "
        "the Korean productive ji-mara ending replaces duplicated haji"
    ),
    1096: (
        "single start-work command caller; action-noun normalization lets "
        "all seven request and command registers share one caller"
    ),
    1102: (
        "negative potential also participates in kamo-shirenai epistemic "
        "phrases, so fixed and lexical caller rewriting remains mandatory"
    ),
    1108: (
        "Base has no live 0143 caller while PK has three spear-ready and "
        "leave-now commands; generic command registers preserve the matrix"
    ),
    1114: (
        "r-verb volitional spans inanimate future or conjecture and personal "
        "intention; Korean get- forms are safer than hortative-only hapsida"
    ),
}

BASIS = (
    "review_queue_base_msggame_B007_S1022_pristine_base_pc_jp_sole_"
    "authority_block0_records2486_2551_66_visible_full_boundary_groups_"
    "2485_2554_exact_unique_seven_literal_tuple_reverse_search_without_"
    "offset_premise_discovered_pk_plus68_roots1060_1114_pk_plus12_jp_"
    "current_sc_tc_exact_pk_en_empty_target_and_full_archive_digests_"
    "actual_014a_edges_0143_source_current_call_fixed_following_and_"
    "flattening_digests_productive_negative_potential_affirmative_"
    "command_and_volitional_semantics_runtime_caller_rewrite_pending_"
    "one_line_gap_skeleton_reverse_overlay_outside_exact_no_korean_"
    "authority_no_steam"
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
    return PRIOR.root_call_sites(records, root)


def fixed_following_blockers(
    records: dict[tuple[int, int], Any],
    root: int,
) -> tuple[str, ...]:
    return PRIOR.fixed_following_blockers(records, root)


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
        actual_roots = (
            ACTUAL_CALL_ROOTS_BY_PK[root]
            if pk
            else ACTUAL_CALL_ROOTS_BY_BASE[root]
        )
        calls = tuple(
            site
            for actual_root in actual_roots
            for site in root_call_sites(records, actual_root)
        )
        fixed = tuple(
            blocker
            for actual_root in actual_roots
            for blocker in fixed_following_blockers(records, actual_root)
        )
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
        actual_roots = (
            ACTUAL_CALL_ROOTS_BY_PK[root]
            if pk
            else ACTUAL_CALL_ROOTS_BY_BASE[root]
        )
        source_sites = {
            site
            for actual_root in actual_roots
            for site in root_call_sites(source, actual_root)
        }
        current_sites = {
            site
            for actual_root in actual_roots
            for site in root_call_sites(current, actual_root)
        }
        flattened[str(root)] = tuple(sorted(source_sites - current_sites))
        current_only[str(root)] = tuple(
            sorted(current_sites - source_sites)
        )
    return flattened, current_only


def assert_corpora(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    full_ids = tuple(range(2485, 2555))
    previous_boundary = tuple(
        PREVIOUS.FULL_TRANSLATION_POLICY[record_id]
        for record_id in FULL_TERMINAL_GROUPS[1060]
    )
    if (
        previous_boundary != TRANSLATION_POLICY_BY_ROOT[1060]
        or PREVIOUS.FULL_TRANSLATION_POLICY[2485] != "좋겠지요"
        or PREVIOUS.FULL_TRANSLATION_POLICY[2487] != "좋겠사옵니다"
        or PREVIOUS.FULL_TRANSLATION_POLICY[2490] != "좋겠소"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} S1021 root1060 boundary drifted"
        )
    for label, records in records_by_label.items():
        offset = PK_RECORD_OFFSET if label.startswith("pk_") else 0
        target_keys = tuple(
            (BLOCK_ID, record_id + offset) for record_id in RECORD_IDS
        )
        full_keys = tuple(
            (BLOCK_ID, record_id + offset) for record_id in full_ids
        )
        if (
            GENERAL.subset_digest(records, target_keys)
            != ARCHIVE_TARGET_DIGESTS[label]
            or GENERAL.subset_digest(records, full_keys)
            != ARCHIVE_FULL_DIGESTS[label]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} corpus drifted"
            )

    for record_id in full_ids:
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
                or gap_bytes(base_records[key])
                != gap_bytes(pk_records[mapped])
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
                    f"segment {SEGMENT} full skeleton drifted: "
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
                f"segment {SEGMENT} unique PK tuple drifted: {root}"
            )


def assert_runtime_graph(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    full_ids = set(range(2485, 2555))
    if {
        record_id
        for record_ids in FULL_TERMINAL_GROUPS.values()
        for record_id in record_ids
    } != full_ids:
        raise RuntimeError(f"segment {SEGMENT} full universe drifted")

    for label, evidence_by_scope in JUMP_EVIDENCE.items():
        records = records_by_label[label]
        offset = PK_RECORD_OFFSET if label.startswith("pk_") else 0
        for scope, ids in (
            ("target", set(RECORD_IDS)),
            ("full", full_ids),
        ):
            mapped_ids = {record_id + offset for record_id in ids}
            edges = PRIOR.PRIOR.PRIOR.incoming_edges(records, mapped_ids)
            evidence = evidence_by_scope[scope]
            if (
                len(edges) != evidence[0]
                or {edge[2] for edge in edges} != mapped_ids
                or PRIOR.PRIOR.PRIOR.edge_digest(edges) != evidence[1]
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {label} {scope} edge drifted"
                )

    base_edges = GRAPH.graph_edges(records_by_label["base_jp"])
    pk_edges = GRAPH.graph_edges(records_by_label["pk_jp"])
    pk_full_ids = {
        record_id + PK_RECORD_OFFSET for record_id in full_ids
    }
    for root, record_ids in FULL_TERMINAL_GROUPS.items():
        if sorted(
            GRAPH.graph_closure(base_edges, root).intersection(full_ids)
        ) != list(record_ids):
            raise RuntimeError(
                f"segment {SEGMENT} Base closure drifted: {root}"
            )
        if sorted(
            GRAPH.graph_closure(
                pk_edges,
                PK_ROOT_BY_BASE[root],
            ).intersection(pk_full_ids)
        ) != [
            record_id + PK_RECORD_OFFSET for record_id in record_ids
        ]:
            raise RuntimeError(
                f"segment {SEGMENT} PK closure drifted: {root}"
            )
    if sorted(
        GRAPH.graph_closure(base_edges, 1061).intersection(full_ids)
    ) != [2485, 2486]:
        raise RuntimeError(
            f"segment {SEGMENT} Base alias root1061 closure drifted"
        )
    if sorted(
        GRAPH.graph_closure(pk_edges, 1073).intersection(pk_full_ids)
    ) != [2553, 2554]:
        raise RuntimeError(
            f"segment {SEGMENT} PK alias root1073 closure drifted"
        )


def assert_call_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    for label, expected in CALL_EVIDENCE.items():
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
        expected = FLATTEN_EVIDENCE[edition]
        if (
            sum(len(sites) for sites in flattened.values())
            != expected[0]
            or canonical_sha256(flattened) != expected[1]
            or any(current_only.values())
            or canonical_sha256(current_only)
            != EMPTY_CURRENT_ONLY_FLATTEN_DIGEST
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {edition} flattening drifted"
            )


def assert_semantics(translations: dict[str, str]) -> None:
    if (
        translations != RAW_TRANSLATIONS
        or len(translations) != 66
        or set(EXPECTED_FULL_BASE_JP) != set(range(2485, 2555))
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
        translations["0:2487:0"] != "좋겠사옵니다"
        or translations["0:2488:0"] != "좋겠사옵니다"
        or translations["0:2490:0"] != "좋겠소"
        or translations["0:2492:0"] != "지 않습니다"
        or translations["0:2499:0"] != "수 없습니다"
        or translations["0:2520:0"] != "지 마십시오"
        or translations["0:2529:0"] != "해 주십시오"
        or translations["0:2534:0"] != "수 없습니다"
        or translations["0:2548:0"] != "겠습니다"
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
        (edition, corpus, root): tuple(
            site
            for actual_root in (
                ACTUAL_CALL_ROOTS_BY_PK[root]
                if edition == "pk"
                else ACTUAL_CALL_ROOTS_BY_BASE[root]
            )
            for site in root_call_sites(
                records_by_label[f"{edition}_{corpus}"],
                actual_root,
            )
        )
        for edition in ("base", "pk")
        for corpus in ("jp", "current")
        for root in FULL_TERMINAL_GROUPS
    }
    fixed_cache = {
        (edition, corpus, root): tuple(
            blocker
            for actual_root in (
                ACTUAL_CALL_ROOTS_BY_PK[root]
                if edition == "pk"
                else ACTUAL_CALL_ROOTS_BY_BASE[root]
            )
            for blocker in fixed_following_blockers(
                records_by_label[f"{edition}_{corpus}"],
                actual_root,
            )
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
                    "base_actual_call_roots": list(
                        ACTUAL_CALL_ROOTS_BY_BASE[root]
                    ),
                    "pk_actual_call_roots": list(
                        ACTUAL_CALL_ROOTS_BY_PK[root]
                    ),
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
                    "source_fixed_following_count": len(
                        fixed_cache[("base", "jp", root)]
                    ),
                    "current_fixed_following_count": len(
                        fixed_cache[("base", "current", root)]
                    ),
                    "pk_source_call_count": len(
                        call_cache[("pk", "jp", root)]
                    ),
                    "pk_current_call_count": len(
                        call_cache[("pk", "current", root)]
                    ),
                    "pk_source_fixed_following_count": len(
                        fixed_cache[("pk", "jp", root)]
                    ),
                    "pk_current_fixed_following_count": len(
                        fixed_cache[("pk", "current", root)]
                    ),
                    "pk_mapping_method": (
                        "unique_exact_seven_literal_tuple_reverse_search"
                    ),
                    "integration_note": INTEGRATION_NOTES[root],
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
    if changed != EXPECTED_CHANGED_LITERAL_COUNT:
        raise RuntimeError(f"segment {SEGMENT} changed count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B007_S1022",
                "queue": QUEUE_BATCH_ID,
                "source_literal_count": 66,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "changed_literal_count": changed,
                "base_pk_mapping_method": (
                    "unique_exact_seven_literal_tuple_reverse_search"
                ),
                "discovered_base_pk_record_offsets": [PK_RECORD_OFFSET],
                "discovered_base_pk_root_shifts": [PK_ROOT_SHIFT],
                "base_pk_jp_current_sc_tc_literal_and_gap_divergence": [],
                "pk_en_visible_records": [],
                "full_terminal_groups": {
                    str(root): list(record_ids)
                    for root, record_ids in FULL_TERMINAL_GROUPS.items()
                },
                "pk_root_by_base": PK_ROOT_BY_BASE,
                "cross_segment_translation_policy": (
                    CROSS_SEGMENT_TRANSLATION_POLICY
                ),
                "call_evidence": CALL_EVIDENCE,
                "flatten_evidence": FLATTEN_EVIDENCE,
                "jump_evidence": JUMP_EVIDENCE,
                "candidate_sha256": candidate_sha256,
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
                "target_runtime_skeleton_exact": True,
                "full_boundary_runtime_skeleton_exact": True,
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
