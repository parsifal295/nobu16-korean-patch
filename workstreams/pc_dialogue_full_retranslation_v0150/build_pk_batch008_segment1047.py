#!/usr/bin/env python3
"""Build source-redacted PK block-2 dialogue segment 1047 decisions."""

from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment01 as BASE_A
import build_base_batch001_segment02 as BASE_B
import build_base_batch001_segment03 as BASE_C
import build_pk_batch001_segment1026 as ROOT142
import build_pk_batch002_segment1027 as ROOT178
import build_pk_batch004_segment1033 as ROOT550_LEFT
import build_pk_batch004_segment1034 as ROOT550_RIGHT
import build_pk_batch006_segment1040 as ROOT904
import build_pk_batch007_segment1043 as ROOT1066
import build_pk_batch007_segment1044 as COMMON
import build_pk_batch008_segment1046 as LEFT_PK


ENGINE = COMMON.ENGINE
GENERAL = COMMON.GENERAL
UTIL = COMMON.UTIL
HELPERS = COMMON.HELPERS
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B008_S1047.private.v1.jsonl"
)
BASE_DECISIONS = (
    (
        BASE_A.OUTPUT,
        "0BAB462CFF06D1429C128B4E2EF0EF8E6C6F8EFEFEF5A8560DCB4D641EE2FF22",
    ),
    (
        BASE_B.OUTPUT,
        "13F824CA7B4A11CCBD0E811FB2BEF94B37D86F827F4475A91D244EF0DE0A9F10",
    ),
    (
        BASE_C.OUTPUT,
        "355F419DE02A85E08DF5CAC1822D92704A0282AC8281C75948FC96103731A512",
    ),
)
SEGMENT = 1047
QUEUE_BATCH_ID = "pk_msggame-B008"
BLOCK_ID = 2
QUEUE_START = 134
QUEUE_STOP = 200
PK_RECORD_IDS = tuple(range(87, 131))
BASE_RECORD_IDS = tuple(range(81, 125))
PK_RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in PK_RECORD_IDS)
PK_RECORD_COUNT = 21751

BASE_TRANSLATIONS = {
    **BASE_A.TRANSLATIONS,
    **BASE_B.TRANSLATIONS,
    **BASE_C.TRANSLATIONS,
}
BASE_RUNTIME_PENDING = (
    set(BASE_A.DYNAMIC_RUNTIME_COORDINATES)
    | set(BASE_B.DYNAMIC_RUNTIME_COORDINATES)
    | set(BASE_C.DYNAMIC_RUNTIME_COORDINATES)
)
BASE_RUNTIME_PENDING = {
    coordinate
    for coordinate in BASE_RUNTIME_PENDING
    if 81 <= int(coordinate.split(":")[1]) <= 124
}


def base_coordinate(pk_coordinate: str) -> str:
    block_id, record_id, literal_id = (
        int(value) for value in pk_coordinate.split(":")
    )
    if block_id != BLOCK_ID:
        raise RuntimeError(
            f"segment {SEGMENT} unexpected block: {pk_coordinate}"
        )
    return f"{block_id}:{record_id - 6}:{literal_id}"


def pk_coordinate(base_value: str) -> str:
    block_id, record_id, literal_id = (
        int(value) for value in base_value.split(":")
    )
    if block_id != BLOCK_ID:
        raise RuntimeError(
            f"segment {SEGMENT} unexpected Base block: {base_value}"
        )
    return f"{block_id}:{record_id + 6}:{literal_id}"


LITERAL_COUNTS = {
    **{record_id: 1 for record_id in range(87, 94)},
    **{record_id: 2 for record_id in range(94, 99)},
    **{record_id: 1 for record_id in range(99, 105)},
    **{record_id: 2 for record_id in range(105, 108)},
    108: 1,
    109: 2,
    110: 2,
    111: 2,
    112: 2,
    **{record_id: 1 for record_id in range(113, 122)},
    122: 2,
    123: 2,
    124: 2,
    125: 3,
    126: 2,
    127: 2,
    128: 1,
    129: 4,
    130: 1,
}
TARGET_COORDINATES = tuple(
    f"{BLOCK_ID}:{record_id}:{literal_id}"
    for record_id in PK_RECORD_IDS
    for literal_id in range(LITERAL_COUNTS[record_id])
)
PK_LAYOUT_ADAPTATIONS = {
    "2:94:0": "부인 ",
    "2:95:0": "따님 ",
    "2:96:0": "부인 ",
    "2:97:0": "따님 ",
    "2:98:0": "가신의 딸 ",
    "2:126:0": "뒷일은 맡겨 주시오\n이 ",
}
TRANSLATIONS = {
    coordinate: PK_LAYOUT_ADAPTATIONS.get(
        coordinate,
        BASE_TRANSLATIONS[base_coordinate(coordinate)],
    )
    for coordinate in TARGET_COORDINATES
}
RUNTIME_PENDING_COORDINATES = {
    pk_coordinate(coordinate)
    for coordinate in BASE_RUNTIME_PENDING
}
STATIC_COORDINATES = set(TARGET_COORDINATES) - RUNTIME_PENDING_COORDINATES
TARGET_KEYS = tuple(
    tuple(int(value) for value in coordinate.split(":"))
    for coordinate in TARGET_COORDINATES
)

EXPECTED_SOURCE_SHA256 = (
    "58BA176918086E728F27E27E825B5C26E958BE9455D58394A5FEDBEFDA67BDE1"
)
EXPECTED_CURRENT_SHA256 = (
    "CF8A6295518713E766D8C503FFC1F9351D1BB3DD1F756CF19D288730A0D09B88"
)
EXPECTED_POLICY_SHA256 = (
    "77AB98F587211C0B7C60F3C7CA9E11608E8685C3DDCF0D2E5AF3DE323589BF1C"
)
EXPECTED_MAPPING_SHA256 = (
    "3BF16C2CDE6FCB917879889CAA26D3FB66359FC4D10B5E10D3BA8388C0FF8CF9"
)
EXPECTED_GAP_SHA256 = (
    "579346B48A4BE77B1900E8F7CD4CBDC26DD3DB8D547CBF7D3AFE56E1788982F0"
)
EXPECTED_DIRECT_CALL_SHA256 = (
    "A66EC72E476CB12DC7511869F6E0121B1171E39220D3427F6E36454BA6F7D568"
)
EXPECTED_DYNAMIC_CONTROL_COUNT = 22
EXPECTED_DYNAMIC_CONTROL_SHA256 = (
    "39E57DAF2CA4D5A552E6C9031EC25AFE43E832EA3396B602A62A2037F5A1A1CD"
)
EXPECTED_DIVERGENCE_SHA256 = (
    "5D96E4429D98743132FFE29EC4CA168F08BCE2937021C600CB96E4BED57B610B"
)
EXPECTED_CHANGED_LITERAL_COUNT = 58
EXPECTED_CANDIDATE_SHA256 = (
    "A9AD21BE56C8CDE9B538C1983A93B1B0F888BAF07A9FC9F5DFD1151E5C0D96D9"
)
PK_ARCHIVE_DIGESTS = {
    "pk_jp": "023F61F8F5CF1A6C8539F739A5144BF8A6948B224F632EDB0891CDF5510FC4B1",
    "pk_current": "BD2696417596474C07ACC473531C931B5B4D3CCF1641EAD474678F59927B702A",
    "pk_sc": "A52D4A278E61B5C678FD758C3EE6A5194497D5230B29B09C900AB28469037177",
    "pk_tc": "B57B6541A7D1D2D0A463F48A06D1E85A23340C78C56F2A81D770C079EEF0EDE4",
    "pk_en": "CB570E11DD8FE3AA346E5A4E870624E594D4142EBA026FC5DF8689EA952C234B",
}
EXPECTED_CURRENT_LITERAL_DIVERGENCE_IDS = {
    87,
    88,
    89,
    90,
    91,
    92,
    93,
    94,
    95,
    96,
    97,
    98,
    103,
    104,
    110,
    113,
    114,
    115,
    116,
    117,
    118,
    126,
    128,
}
EXPECTED_GAP_DIVERGENCES = {
    125: (
        ("", "",),
        ("014308000000", "014308000000"),
        ("024734", "024734"),
        ("01432A040000050505", "01431E040000050505"),
    ),
    127: (
        ("024734", "024734"),
        ("014326020000", "01431A020000"),
        ("014388030000050505", "01437C030000050505"),
    ),
    129: (
        ("", ""),
        ("014308000000", "014308000000"),
        ("02473E", "02473E"),
        ("014390040000", "014384040000"),
        ("01438E000000050505", "01438E000000050505"),
    ),
}
DIRECT_CALL_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)
EXPECTED_DIRECT_CALLS = (
    (2, 105, 1, 0, 8),
    (2, 106, 1, 0, 8),
    (2, 107, 1, 0, 8),
    (2, 108, 0, 0, 8),
    (2, 109, 1, 0, 8),
    (2, 110, 1, 0, 8),
    (2, 111, 2, 0, 178),
    (2, 112, 2, 0, 178),
    (2, 123, 1, 0, 8),
    (2, 125, 1, 0, 8),
    (2, 125, 3, 0, 1066),
    (2, 127, 1, 0, 550),
    (2, 127, 2, 0, 904),
    (2, 129, 1, 0, 8),
    (2, 129, 3, 0, 1168),
    (2, 129, 4, 0, 142),
    (2, 130, 0, 0, 8),
)

RUNTIME_INTEGRATION_EVIDENCE = {
    94: {
        "integration_mode": "dynamic_person_name_subject_boundary",
        "source_free_korean_example": (
            "부인 유키가 무장으로 원복했습니다"
        ),
    },
    105: {
        "integration_mode": "dynamic_name_honorific_boundary",
        "source_free_korean_example": (
            "성인식을 마친 뒤 주군의 패업에 힘을 보태고자\n"
            "갈고닦은 문무를 마음껏 펼치겠사옵니다"
        ),
    },
    111: {
        "integration_mode": "flatten_dynamic_count_terminal",
        "source_free_korean_example": (
            "원복을 마치고 한 사람 몫을 하게 된 무장: 3명"
        ),
    },
    112: {
        "integration_mode": "flatten_dynamic_count_terminal",
        "source_free_korean_example": (
            "원복을 마치고 휘하에 들어오는 무장: 3명"
        ),
    },
    113: {
        "integration_mode": "dynamic_force_name_genitive_boundary",
        "source_free_korean_example": (
            "오다 가문의 적대 목표가 갱신되었습니다"
        ),
    },
    119: {
        "integration_mode": "dynamic_marriage_partner_boundary",
        "source_free_korean_example": (
            "오다 측과 맺은 혼인 동맹을 파기하게 됩니다"
        ),
    },
    122: {
        "integration_mode": "dynamic_successor_name_subject_boundary",
        "source_free_korean_example": (
            "뒷일은 내게 맡겨\n이 후계자가 크게 키워 줄 테니까!"
        ),
    },
    125: {
        "integration_mode": "normalize_action_noun_before_intent",
        "source_free_korean_example": (
            "선대에 뒤지지 않도록 제 무용으로\n"
            "가문의 이름을 천하에 선양하겠사옵니다"
        ),
    },
    127: {
        "integration_mode": "joint_copula_and_delegation_request",
        "source_free_korean_example": (
            "가문의 이름이 주는 책임은 무겁지만 자랑스럽기도 하니\n"
            "절로 마음가짐이 바로 서는군요\n"
            "부디 뒷일은 맡겨 주십시오"
        ),
    },
    126: {
        "integration_mode": "dynamic_successor_name_spacing_boundary",
        "source_free_korean_example": (
            "뒷일은 맡겨 주시오\n"
            "이 후계자가 우리 가문을 패자로 만들겠소"
        ),
    },
    129: {
        "integration_mode": "zero_prefix_and_action_boundary_rewrite",
        "source_free_korean_example": (
            "부디 안심하십시오. 선대가 지켜 온 가문을\n"
            "제 지혜와 용맹으로 더욱 번영시키겠다고 약속합니다"
        ),
    },
}
EXPECTED_INTEGRATION_CLASS_COUNTS = dict(
    Counter(
        evidence["integration_mode"]
        for evidence in RUNTIME_INTEGRATION_EVIDENCE.values()
    )
)

BASIS = (
    "pristine PK JP authoritative; PC EN SC TC context-only; unique "
    "44-record source-literal reverse match to completed Base records81_124 "
    "with exact plus6 mapping; three PK-specific runtime-root gap shifts; "
    "completed Base Korean policy and classification reused coordinate by "
    "coordinate with six PK protected-outer-whitespace surface adaptations; "
    "dynamic name, count, copula, delegation, intention, "
    "honorific zero-prefix and action-terminal boundaries guarded; line "
    "signatures, tokens, gaps, outside-scope records, reverse overlay, "
    "two-run reproduction and Steam read-only state checked"
)


literal_texts = COMMON.literal_texts
gap_bytes = COMMON.gap_bytes
archive_records = COMMON.archive_records


def assert_queue_contract(prepared: Any) -> None:
    rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
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
        len(rows) != 127
        or len(visible) != 200
        or hidden
        != ("0:2728:0", "1:2:0", "1:31:0", "2:85:0")
        or visible[QUEUE_START:QUEUE_STOP] != TARGET_COORDINATES
        or rows[0]["record_coordinate"] != "0:2677"
        or rows[-1]["record_coordinate"] != "2:130"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} private queue ordinal contract drifted"
        )


def record_literal_sequence(
    records: dict[tuple[int, int], Any],
    start: int,
    count: int,
) -> tuple[tuple[str, ...], ...]:
    return tuple(
        literal_texts(records, (BLOCK_ID, record_id))
        for record_id in range(start, start + count)
    )


def sequence_starts(
    records: dict[tuple[int, int], Any],
    sequence: tuple[tuple[str, ...], ...],
) -> tuple[int, ...]:
    record_ids = sorted(
        record_id
        for block_id, record_id in records
        if block_id == BLOCK_ID
    )
    return tuple(
        start
        for start in range(
            min(record_ids),
            max(record_ids) - len(sequence) + 2,
        )
        if record_literal_sequence(records, start, len(sequence))
        == sequence
    )


def mapping_pairs() -> tuple[tuple[str, str], ...]:
    return tuple(
        (coordinate, base_coordinate(coordinate))
        for coordinate in TARGET_COORDINATES
    )


def direct_calls(
    records: dict[tuple[int, int], Any],
) -> tuple[tuple[int, int, int, int, int], ...]:
    rows: list[tuple[int, int, int, int, int]] = []
    for record_id in PK_RECORD_IDS:
        for gap_id, gap in enumerate(
            gap_bytes(records[(BLOCK_ID, record_id)])
        ):
            for match in DIRECT_CALL_RE.finditer(gap):
                rows.append(
                    (
                        BLOCK_ID,
                        record_id,
                        gap_id,
                        match.start(),
                        struct.unpack("<I", match.group(1))[0],
                    )
                )
    return tuple(rows)


def dynamic_controls(
    records: dict[tuple[int, int], Any],
) -> tuple[tuple[int, int, str], ...]:
    return tuple(
        (record_id, gap_id, gap.hex().upper())
        for record_id in PK_RECORD_IDS
        for gap_id, gap in enumerate(
            gap_bytes(records[(BLOCK_ID, record_id)])
        )
        if gap.startswith(b"\x02")
    )


def assert_completed_base_policy(prepared: Any) -> None:
    rows_by_coordinate: dict[str, dict[str, Any]] = {}
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
        ENGINE.validate_decisions(prepared, path, require_complete=False)
        for line in path.read_text(encoding="utf-8").splitlines():
            if line:
                row = json.loads(line)
                rows_by_coordinate[str(row["coordinate"])] = row
    for coordinate, translation in TRANSLATIONS.items():
        base_value = base_coordinate(coordinate)
        row = rows_by_coordinate.get(base_value)
        expected_pending = coordinate in RUNTIME_PENDING_COORDINATES
        if (
            row is None
            or row["resource"] != "base_msggame"
            or row["translation"] != BASE_TRANSLATIONS[base_value]
            or row["semantic_review"] != "approved"
            or (
                row["scope_classification"]
                != (
                    "runtime_fragment_pending"
                    if expected_pending
                    else "retranslated"
                )
            )
            or (
                row["runtime_review"]
                != ("pending" if expected_pending else "not_required")
            )
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
        ):
            raise RuntimeError(
                f"segment {SEGMENT} completed Base policy drifted: "
                f"{base_value}"
            )


def assert_left_boundary(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    key = LEFT_PK.RIGHT_RECORD_2_86_KEY
    source_contract = LEFT_PK.record_contract(
        records_by_label["pk_jp"], key
    )
    current_contract = LEFT_PK.record_contract(
        records_by_label["pk_current"], key
    )
    if (
        key != (BLOCK_ID, PK_RECORD_IDS[0] - 1)
        or source_contract
        != (
            LEFT_PK.RIGHT_RECORD_2_86_SOURCE_RAW_SHA256,
            LEFT_PK.RIGHT_RECORD_2_86_SOURCE_LITERAL_SHA256,
            LEFT_PK.RIGHT_RECORD_2_86_GAP_SHA256,
            LEFT_PK.RIGHT_RECORD_2_86_SOURCE_SIGNATURE_SHA256,
        )
        or current_contract
        != (
            LEFT_PK.RIGHT_RECORD_2_86_CURRENT_RAW_SHA256,
            LEFT_PK.RIGHT_RECORD_2_86_CURRENT_LITERAL_SHA256,
            LEFT_PK.RIGHT_RECORD_2_86_GAP_SHA256,
            LEFT_PK.RIGHT_RECORD_2_86_CURRENT_SIGNATURE_SHA256,
        )
        or gap_bytes(records_by_label["pk_jp"][key])
        != gap_bytes(records_by_label["pk_current"][key])
        or LEFT_PK.RIGHT_RECORD_2_86_POLICY
        != BASE_A.TRANSLATIONS["2:80:0"]
        or HELPERS.canonical_sha256(
            (LEFT_PK.RIGHT_RECORD_2_86_POLICY,)
        )
        != LEFT_PK.EXPECTED_TRANSLATION_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} left boundary contract drifted"
        )


def assert_mapping_and_corpora(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source_sequence = record_literal_sequence(
        records_by_label["pk_jp"], 87, 44
    )
    if (
        sequence_starts(records_by_label["base_jp"], source_sequence)
        != (81,)
        or sequence_starts(records_by_label["pk_jp"], source_sequence)
        != (87,)
        or HELPERS.canonical_sha256(mapping_pairs())
        != EXPECTED_MAPPING_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} source mapping drifted"
        )
    if (
        HELPERS.canonical_sha256(
            tuple(
                literal_texts(
                    records_by_label["pk_jp"],
                    (BLOCK_ID, int(coordinate.split(":")[1])),
                )[int(coordinate.split(":")[2])]
                for coordinate in TARGET_COORDINATES
            )
        )
        != EXPECTED_SOURCE_SHA256
        or HELPERS.canonical_sha256(
            tuple(
                literal_texts(
                    records_by_label["pk_current"],
                    (BLOCK_ID, int(coordinate.split(":")[1])),
                )[int(coordinate.split(":")[2])]
                for coordinate in TARGET_COORDINATES
            )
        )
        != EXPECTED_CURRENT_SHA256
        or HELPERS.canonical_sha256(
            tuple(TRANSLATIONS[coordinate] for coordinate in TARGET_COORDINATES)
        )
        != EXPECTED_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} source/current/policy digest drifted"
        )
    for label, expected in PK_ARCHIVE_DIGESTS.items():
        if GENERAL.subset_digest(
            records_by_label[label], PK_RECORD_KEYS
        ) != expected:
            raise RuntimeError(
                f"segment {SEGMENT} {label} archive drifted"
            )

    current_literal_divergences: set[int] = set()
    divergence_rows: list[
        tuple[int, int, tuple[str, ...], tuple[str, ...]]
    ] = []
    for pk_record_id, base_record_id in zip(
        PK_RECORD_IDS, BASE_RECORD_IDS, strict=True
    ):
        pk_key = (BLOCK_ID, pk_record_id)
        base_key = (BLOCK_ID, base_record_id)
        if (
            literal_texts(records_by_label["pk_jp"], pk_key)
            != literal_texts(records_by_label["base_jp"], base_key)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} mapped JP literal drifted: "
                f"{pk_record_id}"
            )
        for language in ("sc", "tc"):
            if (
                records_by_label[f"pk_{language}"][pk_key].data
                != records_by_label[f"base_{language}"][base_key].data
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} mapped {language} drifted: "
                    f"{pk_record_id}"
                )
        if (
            literal_texts(records_by_label["pk_current"], pk_key)
            != literal_texts(records_by_label["base_current"], base_key)
        ):
            current_literal_divergences.add(pk_record_id)

        pk_gaps = tuple(
            gap.hex().upper()
            for gap in gap_bytes(records_by_label["pk_jp"][pk_key])
        )
        base_gaps = tuple(
            gap.hex().upper()
            for gap in gap_bytes(records_by_label["base_jp"][base_key])
        )
        if pk_record_id in EXPECTED_GAP_DIVERGENCES:
            expected_pairs = EXPECTED_GAP_DIVERGENCES[pk_record_id]
            if (
                tuple(zip(pk_gaps, base_gaps, strict=True))
                != expected_pairs
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} mapped gap shift drifted: "
                    f"{pk_record_id}"
                )
            divergence_rows.append(
                (pk_record_id, base_record_id, pk_gaps, base_gaps)
            )
        elif pk_gaps != base_gaps:
            raise RuntimeError(
                f"segment {SEGMENT} unexpected gap shift: "
                f"{pk_record_id}"
            )
        if gap_bytes(records_by_label["pk_current"][pk_key]) != (
            gap_bytes(records_by_label["pk_jp"][pk_key])
        ):
            raise RuntimeError(
                f"segment {SEGMENT} PK source/current gap drifted: "
                f"{pk_record_id}"
            )
    if (
        current_literal_divergences
        != EXPECTED_CURRENT_LITERAL_DIVERGENCE_IDS
        or HELPERS.canonical_sha256(tuple(divergence_rows))
        != EXPECTED_DIVERGENCE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} mapped divergence evidence drifted"
        )
    gap_payload = tuple(
        (
            record_id,
            tuple(
                gap.hex().upper()
                for gap in gap_bytes(
                    records_by_label["pk_jp"][(BLOCK_ID, record_id)]
                )
            ),
        )
        for record_id in PK_RECORD_IDS
    )
    if HELPERS.canonical_sha256(gap_payload) != EXPECTED_GAP_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} target gap digest drifted"
        )


def assert_runtime_dependencies(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    calls = direct_calls(records_by_label["pk_jp"])
    controls = dynamic_controls(records_by_label["pk_jp"])
    if (
        calls != EXPECTED_DIRECT_CALLS
        or direct_calls(records_by_label["pk_current"]) != calls
        or HELPERS.canonical_sha256(calls)
        != EXPECTED_DIRECT_CALL_SHA256
        or len(controls) != EXPECTED_DYNAMIC_CONTROL_COUNT
        or dynamic_controls(records_by_label["pk_current"]) != controls
        or HELPERS.canonical_sha256(controls)
        != EXPECTED_DYNAMIC_CONTROL_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime-control evidence drifted"
        )
    if (
        ROOT142.ROOT_ASSEMBLY_PLAN[142]["upstream"]
        != "caller-specific action or verbal-noun stem"
        or ROOT178.ROOT_ASSEMBLY_PLAN[178]
        != "caller predicate stem + existential/progressive ending"
        or ROOT550_LEFT.ROOT_ASSEMBLY_PLAN[550]
        != "caller nominal predicate + copular ending"
        or ROOT550_RIGHT.ROOT_ASSEMBLY_PLAN[550]
        != "caller nominal predicate normalized before copular ending"
        or ROOT904.ROOT_ASSEMBLY_PLAN[904]
        != (
            "insert or rewrite an explicit Korean boundary before the "
            "delegation request; flatten callers already complete in "
            "current Korean"
        )
        or ROOT1066.ROOT_TRANSLATION_POLICY[1066]
        != (
            "하겠습니다",
            "하겠다",
            "하겠사옵니다",
            "하겠사옵니다",
            "하겠습니다",
            "하겠소",
            "하겠다",
        )
        or ROOT1066.ROOT_TRANSLATION_POLICY[1066]
        != ROOT1066.BASE_LEFT.TRANSLATION_MATRICES[1054]
        or ROOT550_RIGHT.LEFT_ROOT550_FULL_POLICY
        != ROOT550_LEFT.BASE_MIDDLE.TRANSLATION_POLICY_BY_ROOT[538]
        or ROOT904.TRANSLATION_POLICY_BY_ROOT[904]
        != tuple(
            ROOT904.BASE_RIGHT.FULL_TRANSLATION_POLICY[record_id]
            for record_id in ROOT904.BASE_RIGHT.FULL_TERMINAL_GROUPS[892]
        )
        or COMMON.BASE_RIGHT.TRANSLATION_POLICY_BY_ROOT[1156]
        != ("", "", "", "", "", "", "")
        or set(
            ROOT1066.HELPERS.root_call_sites(
                records_by_label["pk_jp"], 1066
            )
        ).isdisjoint({"2:125:3:0"})
        or set(
            ROOT904.HELPERS.root_call_sites(
                records_by_label["pk_jp"], 904
            )
        ).isdisjoint({"2:127:2:0"})
        or set(
            ROOT1066.HELPERS.root_call_sites(
                records_by_label["pk_jp"], 1168
            )
        ).isdisjoint({"2:129:3:0"})
    ):
        raise RuntimeError(
            f"segment {SEGMENT} completed runtime dependency drifted"
        )
    counts = Counter(
        str(evidence["integration_mode"])
        for evidence in RUNTIME_INTEGRATION_EVIDENCE.values()
    )
    if dict(counts) != EXPECTED_INTEGRATION_CLASS_COUNTS:
        raise RuntimeError(
            f"segment {SEGMENT} integration class drifted"
        )
    for evidence in RUNTIME_INTEGRATION_EVIDENCE.values():
        sample = str(evidence["source_free_korean_example"])
        if (
            ENGINE.KANA_OR_HAN_RE.search(sample)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(sample)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} source-free integration sample drifted"
            )


def assert_semantics() -> None:
    if (
        len(TARGET_COORDINATES) != 66
        or len(TRANSLATIONS) != 66
        or len(RUNTIME_PENDING_COORDINATES) != 51
        or len(STATIC_COORDINATES) != 15
        or set(PK_LAYOUT_ADAPTATIONS)
        != {
            "2:94:0",
            "2:95:0",
            "2:96:0",
            "2:97:0",
            "2:98:0",
            "2:126:0",
        }
        or set(TARGET_COORDINATES)
        != RUNTIME_PENDING_COORDINATES | STATIC_COORDINATES
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic universe drifted"
        )
    for coordinate, translation in TRANSLATIONS.items():
        if (
            translation
            != PK_LAYOUT_ADAPTATIONS.get(
                coordinate,
                BASE_TRANSLATIONS[base_coordinate(coordinate)],
            )
            or "\r" in translation
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} translation policy drifted: "
                f"{coordinate}"
            )
    if ENGINE.KANA_OR_HAN_RE.search(SCRIPT.read_text(encoding="utf-8")):
        raise RuntimeError(
            f"segment {SEGMENT} tracked builder contains source text"
        )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str]:
    resource = prepared.resources["pk_msggame"]
    current = records_by_label["pk_current"]
    replacements = {
        tuple(int(value) for value in coordinate.split(":")):
        translation
        for coordinate, translation in TRANSLATIONS.items()
    }
    reverse = {
        key: literal_texts(current, key[:2])[key[2]]
        for key in replacements
    }
    candidate = ENGINE.rebuild_packed_with_literals(
        resource.current_blob, replacements
    )
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    if (
        len(current) != PK_RECORD_COUNT
        or len(candidate_records) != PK_RECORD_COUNT
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate record universe drifted"
        )
    target_record_keys = set(PK_RECORD_KEYS)
    for key, record in current.items():
        if (
            key not in target_record_keys
            and candidate_records[key].data != record.data
        ):
            raise RuntimeError(
                f"segment {SEGMENT} changed out-of-scope record: {key}"
            )
    for key in PK_RECORD_KEYS:
        if gap_bytes(candidate_records[key]) != gap_bytes(current[key]):
            raise RuntimeError(
                f"segment {SEGMENT} target gap changed: {key}"
            )
    for coordinate, translation in TRANSLATIONS.items():
        key = tuple(int(value) for value in coordinate.split(":"))
        if literal_texts(candidate_records, key[:2])[key[2]] != translation:
            raise RuntimeError(
                f"segment {SEGMENT} candidate literal drifted: {coordinate}"
            )
    if ENGINE.rebuild_packed_with_literals(candidate, reverse) != (
        resource.current_blob
    ):
        raise RuntimeError(
            f"segment {SEGMENT} reverse overlay is not byte-exact"
        )
    candidate_sha256 = hashlib.sha256(candidate).hexdigest().upper()
    if candidate_sha256 != EXPECTED_CANDIDATE_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} candidate digest drifted"
        )
    return candidate, candidate_sha256


def build_rows() -> tuple[
    Any,
    list[dict[str, Any]],
    bytes,
    str,
]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_queue_contract(prepared)
    records_by_label = archive_records(prepared)
    assert_completed_base_policy(prepared)
    assert_left_boundary(records_by_label)
    assert_mapping_and_corpora(records_by_label)
    assert_runtime_dependencies(records_by_label)
    assert_semantics()

    current = records_by_label["pk_current"]
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        current_text = literal_texts(
            current, (block_id, record_id)
        )[literal_id]
        if (
            not ENGINE.is_visible_translation_candidate(current_text)
            or UTIL.layout_signature(translation)
            != UTIL.layout_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} protected line drifted: {coordinate}"
            )
    candidate, candidate_sha256 = build_candidate(
        prepared, records_by_label
    )
    calls_by_record: dict[int, list[int]] = {}
    for _, record_id, _, _, target in EXPECTED_DIRECT_CALLS:
        calls_by_record.setdefault(record_id, []).append(target)

    rows: list[dict[str, Any]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        pending = coordinate in RUNTIME_PENDING_COORDINATES
        row: dict[str, Any] = {
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
            "scope_classification": (
                "runtime_fragment_pending" if pending else "retranslated"
            ),
            "layout_review": "unchanged_from_current",
            "runtime_review": "pending" if pending else "not_required",
            "basis": BASIS,
            "historic_korean_used": False,
            "switch_korean_used": False,
            "base_policy_coordinate": base_coordinate(coordinate),
            "mapped_base_record_id": record_id - 6,
            "pk_protected_outer_whitespace_adaptation":
            coordinate in PK_LAYOUT_ADAPTATIONS,
            "pk_specific_runtime_root_shift":
            record_id in EXPECTED_GAP_DIVERGENCES,
        }
        if pending:
            row["runtime_assembly_evidence"] = {
                "direct_call_targets": sorted(
                    set(calls_by_record.get(record_id, []))
                ),
                "automatic_space_inserted": False,
                "runtime_integration_required": True,
                "caller_rewrite_required_before_runtime_approval": True,
                "source_free_integration_example":
                RUNTIME_INTEGRATION_EVIDENCE.get(record_id),
                "completed_base_classification_reused": True,
                "pk_control_gap_guarded": True,
            }
        rows.append(row)
    changed = sum(
        translation
        != literal_texts(
            current,
            (
                BLOCK_ID,
                int(coordinate.split(":")[1]),
            ),
        )[int(coordinate.split(":")[2])]
        for coordinate, translation in TRANSLATIONS.items()
    )
    if changed != EXPECTED_CHANGED_LITERAL_COUNT:
        raise RuntimeError(
            f"segment {SEGMENT} changed count drifted: {changed}"
        )
    return prepared, rows, candidate, candidate_sha256


def main() -> int:
    first = build_rows()
    second = build_rows()
    prepared, rows, candidate, candidate_sha256 = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} second-run reproduction drifted"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared, OUTPUT, require_complete=False
    )
    counts = Counter(
        str(row["scope_classification"]) for row in rows
    )
    if (
        len(rows) != 66
        or len(validated) != 66
        or counts
        != Counter(
            {"runtime_fragment_pending": 51, "retranslated": 15}
        )
        or any(
            row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            for row in rows
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} decision classification drifted"
        )
    steam_before = hashlib.sha256(
        prepared.resources["pk_msggame"].current_path.read_bytes()
    ).hexdigest().upper()
    steam_after = hashlib.sha256(
        prepared.resources["pk_msggame"].current_path.read_bytes()
    ).hexdigest().upper()
    if (
        steam_before != steam_after
        or steam_before
        != "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Steam file drifted"
        )
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B008_S1047",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [134, 199],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "owned_record_count": len(PK_RECORD_IDS),
                "source_literal_count": len(TARGET_COORDINATES),
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "changed_literal_count":
                EXPECTED_CHANGED_LITERAL_COUNT,
                "base_mapping_method":
                "unique_44_record_source_literal_reverse_match",
                "discovered_base_record_range": [81, 124],
                "discovered_pk_minus_base_offset": 6,
                "pk_specific_runtime_root_shift_count":
                len(EXPECTED_GAP_DIVERGENCES),
                "pk_protected_outer_whitespace_adaptation_count":
                len(PK_LAYOUT_ADAPTATIONS),
                "source_sequence_sha256": EXPECTED_SOURCE_SHA256,
                "translation_policy_sha256":
                EXPECTED_POLICY_SHA256,
                "mapping_sha256": EXPECTED_MAPPING_SHA256,
                "gap_sha256": EXPECTED_GAP_SHA256,
                "direct_call_sha256": EXPECTED_DIRECT_CALL_SHA256,
                "dynamic_control_count": EXPECTED_DYNAMIC_CONTROL_COUNT,
                "dynamic_control_sha256":
                EXPECTED_DYNAMIC_CONTROL_SHA256,
                "candidate_sha256": candidate_sha256,
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
                "target_runtime_skeleton_exact": True,
                "completed_base_policy_exact": True,
                "left_boundary_s1046_contract_exact": True,
                "pk_runtime_root_shifts_exact": True,
                "pk_runtime_root_shift_policies_equivalent": True,
                "dynamic_runtime_controls_exact": True,
                "source_free_runtime_integration_evidence_exact": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tracked_builder_source_redacted": True,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "steam_read_only": True,
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
