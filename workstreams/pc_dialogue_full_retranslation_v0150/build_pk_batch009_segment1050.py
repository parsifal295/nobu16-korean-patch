#!/usr/bin/env python3
"""Build source-redacted PK block-2 dialogue segment 1050 decisions."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment07 as BASE_A
import build_base_batch001_segment09 as BASE_B
import build_base_batch001_segment10 as BASE_C
import build_pk_batch008_segment1047 as COMMON
import build_pk_batch009_segment1049 as LEFT_PK


ENGINE = COMMON.ENGINE
GENERAL = COMMON.GENERAL
UTIL = COMMON.UTIL
HELPERS = COMMON.HELPERS
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B009_S1050.private.v1.jsonl"
)
BASE_DECISIONS = (
    (
        BASE_A.OUTPUT,
        "B85B0219068242FFDA529BF88D59E57A721101DD0957303E0ECF2917B7E42875",
    ),
    (
        BASE_B.OUTPUT,
        "667C0E34183BBC54B32F419070069071CB1DE31F9602E5512526354F3A032EDD",
    ),
    (
        BASE_C.OUTPUT,
        "622F7062434BC62FEC5733BF1DA91CCAFB403D1FE78F6B4D397F5CEB3BC88F6B",
    ),
)

SEGMENT = 1050
QUEUE_BATCH_ID = "pk_msggame-B009"
QUEUE_START = 133
QUEUE_STOP = 199
BLOCK_ID = 2
PK_RECORD_IDS = tuple(range(204, 242))
BASE_RECORD_IDS = tuple(range(198, 236))
PK_RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in PK_RECORD_IDS)
PK_RECORD_COUNT = 21751

LITERAL_COUNTS = {
    204: 3,
    205: 3,
    206: 3,
    207: 3,
    208: 2,
    209: 2,
    210: 2,
    211: 1,
    212: 1,
    213: 3,
    214: 3,
    215: 1,
    216: 1,
    217: 1,
    218: 2,
    219: 1,
    220: 3,
    221: 1,
    222: 2,
    223: 3,
    224: 1,
    225: 3,
    226: 1,
    227: 1,
    228: 1,
    229: 1,
    230: 2,
    231: 1,
    232: 1,
    233: 3,
    234: 1,
    235: 1,
    236: 1,
    237: 1,
    238: 1,
    239: 1,
    240: 1,
    241: 3,
}
TARGET_COORDINATES = tuple(
    f"{BLOCK_ID}:{record_id}:{literal_id}"
    for record_id in PK_RECORD_IDS
    for literal_id in range(LITERAL_COUNTS[record_id])
)

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


def base_coordinate(pk_coordinate: str) -> str:
    block_id, record_id, literal_id = (
        int(value) for value in pk_coordinate.split(":")
    )
    if block_id != BLOCK_ID:
        raise RuntimeError(
            f"segment {SEGMENT} unexpected block: {pk_coordinate}"
        )
    return f"{block_id}:{record_id - 6}:{literal_id}"


def normalize_base_translation(value: str) -> str:
    return value.translate({0x300C: 0x22, 0x300D: 0x22})


TRANSLATIONS = {
    coordinate: normalize_base_translation(
        BASE_TRANSLATIONS[base_coordinate(coordinate)]
    )
    for coordinate in TARGET_COORDINATES
}
SOURCE_STYLE_QUOTE_NORMALIZED_COORDINATES = {
    coordinate
    for coordinate in TARGET_COORDINATES
    if TRANSLATIONS[coordinate]
    != BASE_TRANSLATIONS[base_coordinate(coordinate)]
}
PK_MORPHOLOGY_ADAPTATIONS = {
    "2:220:2": (
        BASE_TRANSLATIONS["2:214:2"]
        + " "
        + BASE_TRANSLATIONS["2:214:3"]
    ),
}
PK_LAYOUT_ADAPTATIONS = {
    "2:221:0": (
        "사람을 쓰는 데는 제법 자신이 있지……\n"
        "부하 지휘는 내게 맡겨라."
    ),
}
TERMINOLOGY_ADAPTATIONS = {
    "2:228:0": (
        "공성이야말로 나의 본분이다.\n"
        "적병들아, 똑똑히 깨달아라!"
    ),
}
TRANSLATIONS.update(PK_MORPHOLOGY_ADAPTATIONS)
TRANSLATIONS.update(PK_LAYOUT_ADAPTATIONS)
TRANSLATIONS.update(TERMINOLOGY_ADAPTATIONS)

RUNTIME_PENDING_COORDINATES = {
    coordinate
    for coordinate in TARGET_COORDINATES
    if base_coordinate(coordinate) in BASE_RUNTIME_PENDING
}
STATIC_COORDINATES = (
    set(TARGET_COORDINATES) - RUNTIME_PENDING_COORDINATES
)

EXPECTED_SOURCE_LITERAL_SHA256 = (
    "08B0C67334E2B68DC4C024CA894C37FD66C628E5C2D4F867827958438D4B750E"
)
EXPECTED_CURRENT_LITERAL_SHA256 = (
    "D2E506CD9E03087D02D165255AFBA61A191E89B01C6D5FB47D9DFB1BE42ED029"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "D02632B6C9AE2DBD6AF924F2E120625204B99019D902F09328F63FB166AE9291"
)
EXPECTED_MAPPING_SHA256 = (
    "ED76ADAAF1A29A1D16763A6F4100B7BE7C26F0710AC4915464B95670B1F11D84"
)
EXPECTED_GAP_SHA256 = (
    "55FC3DFA51B343D86CA0B12BB4F88D273FD09F23D662A49E1DD805D77934DC28"
)
EXPECTED_GAP_DIVERGENCE_SHA256 = (
    "A0FEC5161B08CAC90A6F94973617ECF5B8B09F21A3CEDDF8D5CD4489A5D83D33"
)
EXPECTED_GAP_DIVERGENCE_RECORD_IDS = {
    218,
    219,
    220,
    221,
    222,
    223,
    225,
    226,
    230,
    231,
    233,
    236,
    241,
}
EXPECTED_SOURCE_CONTROL_SHA256 = (
    "2CA4BECDA13D371A9E0DA6B0E4821B76ED1067A9408578BB25FC0BC6748B1554"
)
EXPECTED_CURRENT_CONTROL_SHA256 = (
    "2B572170A4E8ED811E490A594BAF74A51BB54596DD4283E92FCBCA316E86A002"
)
EXPECTED_CALL_MODE_SHA256 = (
    "6716FF21018F72DFAE35547D1271298D215B2257526F48B64B8EC2B486130446"
)
EXPECTED_PENDING_SHA256 = (
    "4A36602DB6FC29680C34F9A251323BA7C0E208312536052C875155F7767C3F46"
)
EXPECTED_CANDIDATE_SHA256 = (
    "C04387B0D28C880867D432B4A0DECBE3B6A5EB4420B630EC2AFDA05CDEEFFAC8"
)
EXPECTED_CHANGED_LITERAL_COUNT = 54

EXPECTED_ARCHIVE_DIGESTS = {
    "pk_jp": "42332C291D788DBA1B440333E60D7C4EBF090BF76698CD4D14A3EC5B3A9DCF13",
    "pk_current": "EC18E495BD0A3D5B850FFCBE9B88091AFF584CBF0C9AEDE438C677275AC60B05",
    "pk_sc": "DEE9A7EEEC18A2AF0C63C372C3B226315C065DB4CCFCAB6158FB2522AD1AA237",
    "pk_tc": "1C1A515327C3FE4B919E32E942C93D70234E3B937D6D2D506B201EB9B5CFB69A",
    "pk_en": "DE8FA025EF04BB7C44118B31930CBF0E681BD8E23A5DFE270D16E5B71CD522AB",
    "base_jp": "BF4F00DD161250A7A963C879757AEBB0BBB6428FFA69BB809CBD1C33A8DED68B",
    "base_current": "8F604026150012469F0B40D97A93DE04314E0739B46B7F48C3B7381AE3D5011C",
    "base_sc": "FB979E2359B921794012A4596BDDB73E0F89A45948611AF816F3C21EC85C2D4A",
    "base_tc": "6387FD7236B25717AB449F984D5647A07047A82E99FA6122B7654D33D6AA81AF",
}

LEFT_RECORD_2_203_KEY = (2, 203)
LEFT_RECORD_2_203_SOURCE_RAW_SHA256 = (
    "34FA3A01D4EA70DAA679248299EC2146F4050F277460D9BA35409DBEC7AA3CA7"
)
LEFT_RECORD_2_203_CURRENT_RAW_SHA256 = (
    "D9DF622EADCF1448E527D6D1DC9FF13C758A37F898C016830411D7E8B5EA437D"
)
LEFT_RECORD_2_203_SOURCE_LITERAL_SHA256 = (
    "B88C187B4D562FA880145744E8CDB1E918C253F72293427CAD82DB6A4A440E38"
)
LEFT_RECORD_2_203_CURRENT_LITERAL_SHA256 = (
    "ECA509A13450C7168DA5C43625086C2734DB2842C04CEE8D1133F60D49592079"
)
LEFT_RECORD_2_203_GAP_SHA256 = (
    "EE73C886762A2467E924CD38DE3B26437CCBE65DEC256CB4F81AD9FDC29D7D01"
)
LEFT_RECORD_2_203_SOURCE_SIGNATURE_SHA256 = (
    "CD80392C5FAD83F1A07F633F33EEF1CE2C38CCD6361C503A53BFCC9218E6D2D3"
)
LEFT_RECORD_2_203_CURRENT_SIGNATURE_SHA256 = (
    "C3A9577D63EEB1EA31FA3A3BB96704F1383D27E7D161EC45ED7A82B05273AA8B"
)
LEFT_RECORD_2_203_POLICY = tuple(
    normalize_base_translation(
        BASE_A.TRANSLATIONS[f"2:197:{literal_id}"]
    )
    for literal_id in range(3)
)
LEFT_RECORD_2_203_POLICY_SHA256 = (
    "1084A5327F6B1984DE18498DDF224CCBDA3EE6232A4E56BE9016759A33774DA3"
)

RIGHT_RECORD_2_241_KEY = (2, 241)
RIGHT_RECORD_2_241_SOURCE_RAW_SHA256 = (
    "7C294E1788CD68E3EB1300BE4461C7A32DF62BC9C4A8DDAE3544965AD3383886"
)
RIGHT_RECORD_2_241_CURRENT_RAW_SHA256 = (
    "BB901EAD473307AD2C26B2FDE6232719E078B073C41FDA2479031FC9C3D8B5DA"
)
RIGHT_RECORD_2_241_SOURCE_LITERAL_SHA256 = (
    "E51E77ED98DF94DED58212256CDCAFA8BFA37C5F5B5EDA2B9DFDA2BFF07253E6"
)
RIGHT_RECORD_2_241_CURRENT_LITERAL_SHA256 = (
    "55E1582B64D442FC8B559ECFF705F47B7632687C080A704E1E4458FD947BDC20"
)
RIGHT_RECORD_2_241_SOURCE_GAP_SHA256 = (
    "87D463633DDA39CF572FB22B0B78EA70B4EDCA690AEE59CE262432F169BF93AD"
)
RIGHT_RECORD_2_241_CURRENT_GAP_SHA256 = (
    "07C516A20BEB70BC0DFD73554749DC93EE646F325F922C88E9949D70F3BE4768"
)
RIGHT_RECORD_2_241_SOURCE_SIGNATURE_SHA256 = (
    "56E68637E384C1EB1358403EFD614036763C8012FCA83F42139D12300506C661"
)
RIGHT_RECORD_2_241_CURRENT_SIGNATURE_SHA256 = (
    "47B90506A20496734CD156862BD02E60AED174AD96C25BAA1B3F69C331C6204E"
)
RIGHT_RECORD_2_241_POLICY = tuple(
    TRANSLATIONS[f"2:241:{literal_id}"] for literal_id in range(3)
)

CONTROL_0143_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)
CONTROL_014C_RE = re.compile(b"\x01\x4c(.{4})", re.DOTALL)
CONTROL_02_RE = re.compile(b"\x02(.{2})", re.DOTALL)

RUNTIME_INTEGRATION_EVIDENCE = {
    204: ("policy_level_start", "정책「[정책명]」 레벨 [수치]단계의 발령 준비를 시작"),
    205: ("policy_list_start", "「[정책명]」 등 [수치]개 정책의 발령 준비를 시작"),
    206: ("policy_level_start", "정책「[정책명]」 레벨 [수치]단계의 발령 준비를 시작"),
    207: ("policy_list_start", "「[정책명]」 등 [수치]개 정책의 발령 준비를 시작"),
    208: ("prestige_value_rise", "우리 가문 위신이 [수치]로 상승"),
    209: ("prestige_value_fall", "우리 가문 위신이 [수치]로 하락"),
    210: ("target_prestige_gain", "[대상]을 제압하여 위신 [수치] 획득"),
    211: ("castle_fall_notice", "[성명]이 함락"),
    213: ("post_appointment", "역직「[역직명]」 취임, 위신 [수치] 획득"),
    214: ("office_appointment", "관직「[관직명]」 취임, 위신 [수치] 획득"),
    215: ("castle_slot_rise", "[성명]에 건설 가능 구획이 증가"),
    216: ("castle_slot_fall", "[성명]의 건설 가능 구획이 감소"),
    218: ("delegation_flattened", "이 군의 장악은 제게 맡겨 주십시오!"),
    219: ("officer_network", "[인물명]이 쌓아 온 인맥을 우리 가문에 보탠다"),
    220: ("officer_support", "[인물명]에게 맡겨 주시오. [인물명]의 활약을 든든히 뒷받침합니다"),
    222: ("oratory_flattened", "능숙한 언변으로 반드시 신용을 얻어 오겠습니다!"),
    223: ("officer_assistance", "[인물명]이 [대상]을 보좌하여 반드시 신용을 얻어 온다"),
    225: ("territory_defense", "내 영지는 한 치도 침범하게 두지 않고 굳게 지키겠다"),
    230: ("expected_performance", "무가의 본분을 다할 테니 활약을 기대해도 좋다"),
    231: ("guarded_advance", "적의 공격을 물리치도록 엄중히 경계하며 전진한다"),
    233: ("counterattack", "강공을 두려워하지 않고 지금 반격한다"),
    236: ("pincer_attack", "여러 공격로에서 협격하는 용병의 묘리"),
    241: ("covert_work", "그늘에서 할 일은 내게 맡기라는 계책가의 말"),
}

BASIS = (
    "pristine PK JP authoritative; PC EN SC TC and Base context-only; "
    "38-record PK sequence uniquely located with an explicit one-record "
    "literal-composition normalization against completed Base records "
    "198_235; completed Base Korean policy and classification reused, "
    "with one PK literal-composition adaptation and one protected-line "
    "adaptation, one protected-line adaptation, source-style quote "
    "normalization and one glossary-driven terminology correction; "
    "source/current runtime-control modes, shifted gaps, dynamic assembly "
    "examples, line signatures, outside-scope records, reverse overlay, "
    "two-run reproduction and Steam read-only state guarded"
)


literal_texts = COMMON.literal_texts
gap_bytes = COMMON.gap_bytes
archive_records = COMMON.archive_records


def canonical_sha256(value: object) -> str:
    return HELPERS.canonical_sha256(value)


def record_contract(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, str, str, str]:
    literals = literal_texts(records, key)
    gaps = tuple(
        value.hex().upper() for value in gap_bytes(records[key])
    )
    return (
        hashlib.sha256(records[key].data).hexdigest().upper(),
        canonical_sha256(literals),
        canonical_sha256(gaps),
        canonical_sha256((literals, gaps)),
    )


def source_sequence(
    records: dict[tuple[int, int], Any],
    start: int,
) -> tuple[tuple[str, ...], ...]:
    return tuple(
        literal_texts(records, (BLOCK_ID, record_id))
        for record_id in range(start, start + len(PK_RECORD_IDS))
    )


def exact_sequence_starts(
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
        if source_sequence(records, start) == sequence
    )


def normalized_base_sequence_starts(
    records: dict[tuple[int, int], Any],
    sequence: tuple[tuple[str, ...], ...],
) -> tuple[int, ...]:
    record_ids = sorted(
        record_id
        for block_id, record_id in records
        if block_id == BLOCK_ID
    )
    hits: list[int] = []
    for start in range(
        min(record_ids),
        max(record_ids) - len(sequence) + 2,
    ):
        matched = True
        for ordinal, expected in enumerate(sequence):
            actual = literal_texts(
                records,
                (BLOCK_ID, start + ordinal),
            )
            if ordinal == 16:
                matched = (
                    len(expected) == 3
                    and len(actual) == 4
                    and expected[:2] == actual[:2]
                    and expected[2] == actual[2] + actual[3]
                )
            else:
                matched = expected == actual
            if not matched:
                break
        if matched:
            hits.append(start)
    return tuple(hits)


def control_rows(
    records: dict[tuple[int, int], Any],
) -> tuple[tuple[int, int, str, object], ...]:
    rows: list[tuple[int, int, str, object]] = []
    for record_id in PK_RECORD_IDS:
        for gap_id, gap in enumerate(
            gap_bytes(records[(BLOCK_ID, record_id)])
        ):
            rows.extend(
                (
                    record_id,
                    gap_id,
                    "0143",
                    int.from_bytes(match.group(1), "little"),
                )
                for match in CONTROL_0143_RE.finditer(gap)
            )
            rows.extend(
                (
                    record_id,
                    gap_id,
                    "014C",
                    int.from_bytes(match.group(1), "little"),
                )
                for match in CONTROL_014C_RE.finditer(gap)
            )
            rows.extend(
                (
                    record_id,
                    gap_id,
                    "02",
                    match.group(1).hex().upper(),
                )
                for match in CONTROL_02_RE.finditer(gap)
            )
    return tuple(rows)


def call_modes(
    source: dict[tuple[int, int], Any],
    current: dict[tuple[int, int], Any],
) -> tuple[tuple[object, ...], ...]:
    rows: list[tuple[object, ...]] = []
    for record_id in PK_RECORD_IDS:
        source_calls = tuple(
            (
                gap_id,
                int.from_bytes(match.group(1), "little"),
            )
            for gap_id, gap in enumerate(
                gap_bytes(source[(BLOCK_ID, record_id)])
            )
            for match in CONTROL_0143_RE.finditer(gap)
        )
        current_calls = tuple(
            (
                gap_id,
                int.from_bytes(match.group(1), "little"),
            )
            for gap_id, gap in enumerate(
                gap_bytes(current[(BLOCK_ID, record_id)])
            )
            for match in CONTROL_0143_RE.finditer(gap)
        )
        current_values = tuple(
            (gap_id, match.group(1).hex().upper())
            for gap_id, gap in enumerate(
                gap_bytes(current[(BLOCK_ID, record_id)])
            )
            for match in CONTROL_02_RE.finditer(gap)
        )
        if source_calls or current_calls or current_values:
            rows.append(
                (
                    record_id,
                    source_calls,
                    current_calls,
                    current_values,
                )
            )
    return tuple(rows)


def assert_queue_contract(prepared: Any) -> None:
    rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        str(target["coordinate"])
        for row in rows
        for target in row["target_literals"]
        if target["visible"]
    )
    hidden = tuple(
        str(target["coordinate"])
        for row in rows
        for target in row["target_literals"]
        if not target["visible"]
    )
    owned_rows = tuple(
        row
        for row in rows
        if int(str(row["record_coordinate"]).split(":")[1])
        in PK_RECORD_IDS
    )
    if (
        len(rows) != 111
        or len(visible) != 199
        or hidden
        or visible[QUEUE_START:QUEUE_STOP] != TARGET_COORDINATES
        or len(owned_rows) != 38
        or owned_rows[0]["record_coordinate"] != "2:204"
        or owned_rows[-1]["record_coordinate"] != "2:241"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} private queue contract drifted"
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
        ENGINE.validate_decisions(
            prepared,
            path,
            require_complete=False,
        )
        for line in path.read_text(encoding="utf-8").splitlines():
            if line:
                row = json.loads(line)
                rows_by_coordinate[str(row["coordinate"])] = row

    required = {
        coordinate
        for coordinate in BASE_TRANSLATIONS
        if (
            coordinate.startswith("2:")
            and 198 <= int(coordinate.split(":")[1]) <= 235
        )
    }
    if len(required) != 67:
        raise RuntimeError(
            f"segment {SEGMENT} Base policy universe drifted"
        )
    for coordinate in required:
        row = rows_by_coordinate.get(coordinate)
        pending = coordinate in BASE_RUNTIME_PENDING
        if (
            row is None
            or row["resource"] != "base_msggame"
            or row["translation"] != BASE_TRANSLATIONS[coordinate]
            or row["semantic_review"] != "approved"
            or row["scope_classification"]
            != (
                "runtime_fragment_pending"
                if pending
                else "retranslated"
            )
            or row["runtime_review"]
            != ("pending" if pending else "not_required")
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
        ):
            raise RuntimeError(
                f"segment {SEGMENT} completed Base policy drifted: "
                f"{coordinate}"
            )


def assert_archive_contracts(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    for label, expected_sha256 in EXPECTED_ARCHIVE_DIGESTS.items():
        record_ids = (
            PK_RECORD_IDS
            if label.startswith("pk_")
            else BASE_RECORD_IDS
        )
        rows = tuple(
            (
                BLOCK_ID,
                record_id,
                hashlib.sha256(
                    records_by_label[label][
                        (BLOCK_ID, record_id)
                    ].data
                ).hexdigest().upper(),
            )
            for record_id in record_ids
        )
        if canonical_sha256(rows) != expected_sha256:
            raise RuntimeError(
                f"segment {SEGMENT} archive contract drifted: {label}"
            )


def assert_mapping_and_controls(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    sequence = source_sequence(source, PK_RECORD_IDS[0])
    if (
        canonical_sha256(sequence)
        != EXPECTED_SOURCE_LITERAL_SHA256
        or canonical_sha256(
            source_sequence(current, PK_RECORD_IDS[0])
        )
        != EXPECTED_CURRENT_LITERAL_SHA256
        or exact_sequence_starts(source, sequence) != (204,)
        or normalized_base_sequence_starts(
            records_by_label["base_jp"],
            sequence,
        )
        != (198,)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} source mapping drifted"
        )

    for pk_record_id, base_record_id in zip(
        PK_RECORD_IDS,
        BASE_RECORD_IDS,
    ):
        pk_literals = literal_texts(
            source,
            (BLOCK_ID, pk_record_id),
        )
        base_literals = literal_texts(
            records_by_label["base_jp"],
            (BLOCK_ID, base_record_id),
        )
        if pk_record_id == 220:
            exact = (
                len(pk_literals) == 3
                and len(base_literals) == 4
                and pk_literals[:2] == base_literals[:2]
                and pk_literals[2]
                == base_literals[2] + base_literals[3]
            )
        else:
            exact = pk_literals == base_literals
        if (
            not exact
            or records_by_label["pk_sc"][
                (BLOCK_ID, pk_record_id)
            ].data
            != records_by_label["base_sc"][
                (BLOCK_ID, base_record_id)
            ].data
            or records_by_label["pk_tc"][
                (BLOCK_ID, pk_record_id)
            ].data
            != records_by_label["base_tc"][
                (BLOCK_ID, base_record_id)
            ].data
        ):
            raise RuntimeError(
                f"segment {SEGMENT} mapped corpus drifted: "
                f"{pk_record_id}"
            )

    mapping = tuple(
        (
            coordinate,
            base_coordinate(coordinate),
            coordinate
            in (
                set(PK_MORPHOLOGY_ADAPTATIONS)
                | set(PK_LAYOUT_ADAPTATIONS)
                | set(TERMINOLOGY_ADAPTATIONS)
                | set(SOURCE_STYLE_QUOTE_NORMALIZED_COORDINATES)
            ),
        )
        for coordinate in TARGET_COORDINATES
    )
    gaps = tuple(
        (
            record_id,
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    source[(BLOCK_ID, record_id)]
                )
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    current[(BLOCK_ID, record_id)]
                )
            ),
        )
        for record_id in PK_RECORD_IDS
    )
    divergences = tuple(
        (
            pk_record_id,
            base_record_id,
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    source[(BLOCK_ID, pk_record_id)]
                )
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["base_jp"][
                        (BLOCK_ID, base_record_id)
                    ]
                )
            ),
        )
        for pk_record_id, base_record_id in zip(
            PK_RECORD_IDS,
            BASE_RECORD_IDS,
        )
        if gap_bytes(source[(BLOCK_ID, pk_record_id)])
        != gap_bytes(
            records_by_label["base_jp"][
                (BLOCK_ID, base_record_id)
            ]
        )
    )
    source_controls = control_rows(source)
    current_controls = control_rows(current)
    modes = call_modes(source, current)
    if (
        canonical_sha256(mapping) != EXPECTED_MAPPING_SHA256
        or canonical_sha256(gaps) != EXPECTED_GAP_SHA256
        or canonical_sha256(divergences)
        != EXPECTED_GAP_DIVERGENCE_SHA256
        or {row[0] for row in divergences}
        != EXPECTED_GAP_DIVERGENCE_RECORD_IDS
        or len(source_controls) != 38
        or canonical_sha256(source_controls)
        != EXPECTED_SOURCE_CONTROL_SHA256
        or len(current_controls) != 26
        or canonical_sha256(current_controls)
        != EXPECTED_CURRENT_CONTROL_SHA256
        or any(row[2] == "014C" for row in source_controls)
        or any(row[2] == "014C" for row in current_controls)
        or len(modes) != 19
        or canonical_sha256(modes) != EXPECTED_CALL_MODE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} control mapping drifted"
        )


def assert_boundary_contracts(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    if (
        record_contract(source, LEFT_RECORD_2_203_KEY)
        != (
            LEFT_RECORD_2_203_SOURCE_RAW_SHA256,
            LEFT_RECORD_2_203_SOURCE_LITERAL_SHA256,
            LEFT_RECORD_2_203_GAP_SHA256,
            LEFT_RECORD_2_203_SOURCE_SIGNATURE_SHA256,
        )
        or record_contract(current, LEFT_RECORD_2_203_KEY)
        != (
            LEFT_RECORD_2_203_CURRENT_RAW_SHA256,
            LEFT_RECORD_2_203_CURRENT_LITERAL_SHA256,
            LEFT_RECORD_2_203_GAP_SHA256,
            LEFT_RECORD_2_203_CURRENT_SIGNATURE_SHA256,
        )
        or record_contract(source, RIGHT_RECORD_2_241_KEY)
        != (
            RIGHT_RECORD_2_241_SOURCE_RAW_SHA256,
            RIGHT_RECORD_2_241_SOURCE_LITERAL_SHA256,
            RIGHT_RECORD_2_241_SOURCE_GAP_SHA256,
            RIGHT_RECORD_2_241_SOURCE_SIGNATURE_SHA256,
        )
        or record_contract(current, RIGHT_RECORD_2_241_KEY)
        != (
            RIGHT_RECORD_2_241_CURRENT_RAW_SHA256,
            RIGHT_RECORD_2_241_CURRENT_LITERAL_SHA256,
            RIGHT_RECORD_2_241_CURRENT_GAP_SHA256,
            RIGHT_RECORD_2_241_CURRENT_SIGNATURE_SHA256,
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} boundary contract drifted"
        )
    imported_left = (
        LEFT_PK.RIGHT_RECORD_2_203_KEY,
        LEFT_PK.RIGHT_RECORD_2_203_SOURCE_RAW_SHA256,
        LEFT_PK.RIGHT_RECORD_2_203_CURRENT_RAW_SHA256,
        LEFT_PK.RIGHT_RECORD_2_203_SOURCE_LITERALS_SHA256,
        LEFT_PK.RIGHT_RECORD_2_203_CURRENT_LITERALS_SHA256,
        LEFT_PK.RIGHT_RECORD_2_203_GAP_SHA256,
        LEFT_PK.RIGHT_RECORD_2_203_SOURCE_SIGNATURE_SHA256,
        LEFT_PK.RIGHT_RECORD_2_203_CURRENT_SIGNATURE_SHA256,
        LEFT_PK.RIGHT_RECORD_2_203_POLICY,
        LEFT_PK.RIGHT_RECORD_2_203_POLICY_SHA256,
    )
    local_left = (
        LEFT_RECORD_2_203_KEY,
        LEFT_RECORD_2_203_SOURCE_RAW_SHA256,
        LEFT_RECORD_2_203_CURRENT_RAW_SHA256,
        LEFT_RECORD_2_203_SOURCE_LITERAL_SHA256,
        LEFT_RECORD_2_203_CURRENT_LITERAL_SHA256,
        LEFT_RECORD_2_203_GAP_SHA256,
        LEFT_RECORD_2_203_SOURCE_SIGNATURE_SHA256,
        LEFT_RECORD_2_203_CURRENT_SIGNATURE_SHA256,
        LEFT_RECORD_2_203_POLICY,
        LEFT_RECORD_2_203_POLICY_SHA256,
    )
    if imported_left != local_left:
        raise RuntimeError(
            f"segment {SEGMENT} S1049 left boundary drifted"
        )


def assert_semantics() -> None:
    if (
        len(TARGET_COORDINATES) != 66
        or len(TRANSLATIONS) != 66
        or len(RUNTIME_PENDING_COORDINATES) != 51
        or len(STATIC_COORDINATES) != 15
        or canonical_sha256(
            tuple(sorted(RUNTIME_PENDING_COORDINATES))
        )
        != EXPECTED_PENDING_SHA256
        or set(RUNTIME_INTEGRATION_EVIDENCE)
        != {
            int(coordinate.split(":")[1])
            for coordinate in RUNTIME_PENDING_COORDINATES
        }
        or PK_MORPHOLOGY_ADAPTATIONS["2:220:2"]
        != (
            BASE_TRANSLATIONS["2:214:2"]
            + " "
            + BASE_TRANSLATIONS["2:214:3"]
        )
        or set(PK_LAYOUT_ADAPTATIONS) != {"2:221:0"}
        or set(TERMINOLOGY_ADAPTATIONS) != {"2:228:0"}
        or SOURCE_STYLE_QUOTE_NORMALIZED_COORDINATES
        != {
            "2:204:0",
            "2:204:1",
            "2:205:0",
            "2:205:1",
            "2:206:0",
            "2:206:1",
            "2:207:0",
            "2:207:1",
            "2:213:0",
            "2:213:1",
            "2:214:0",
            "2:214:1",
        }
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic universe drifted"
        )
    for coordinate, translation in TRANSLATIONS.items():
        if coordinate in PK_MORPHOLOGY_ADAPTATIONS:
            expected = PK_MORPHOLOGY_ADAPTATIONS[coordinate]
        elif coordinate in PK_LAYOUT_ADAPTATIONS:
            expected = PK_LAYOUT_ADAPTATIONS[coordinate]
        elif coordinate in TERMINOLOGY_ADAPTATIONS:
            expected = TERMINOLOGY_ADAPTATIONS[coordinate]
        else:
            expected = normalize_base_translation(
                BASE_TRANSLATIONS[base_coordinate(coordinate)]
            )
        if (
            translation != expected
            or "\r" in translation
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or (
                UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(
                    translation
                )
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} translation policy drifted: "
                f"{coordinate}"
            )
    if (
        canonical_sha256(
            tuple(
                TRANSLATIONS[coordinate]
                for coordinate in TARGET_COORDINATES
            )
        )
        != EXPECTED_TRANSLATION_POLICY_SHA256
        or canonical_sha256(
            tuple(sorted(RUNTIME_PENDING_COORDINATES))
        )
        != EXPECTED_PENDING_SHA256
        or any(
            ENGINE.KANA_OR_HAN_RE.search(example)
            for _, example in RUNTIME_INTEGRATION_EVIDENCE.values()
        )
        or ENGINE.KANA_OR_HAN_RE.search(
            SCRIPT.read_text(encoding="utf-8")
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} source-redaction policy drifted"
        )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
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
        resource.current_blob,
        replacements,
    )
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    if (
        len(current) != PK_RECORD_COUNT
        or len(candidate_records) != PK_RECORD_COUNT
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate universe drifted"
        )
    target_record_keys = set(PK_RECORD_KEYS)
    for key, record in current.items():
        if (
            key not in target_record_keys
            and candidate_records[key].data != record.data
        ):
            raise RuntimeError(
                f"segment {SEGMENT} changed outside scope: {key}"
            )
    for key in PK_RECORD_KEYS:
        if gap_bytes(candidate_records[key]) != gap_bytes(current[key]):
            raise RuntimeError(
                f"segment {SEGMENT} changed target gaps: {key}"
            )
    for coordinate, translation in TRANSLATIONS.items():
        key = tuple(int(value) for value in coordinate.split(":"))
        if (
            literal_texts(candidate_records, key[:2])[key[2]]
            != translation
        ):
            raise RuntimeError(
                f"segment {SEGMENT} candidate literal drifted: "
                f"{coordinate}"
            )
    if (
        ENGINE.rebuild_packed_with_literals(candidate, reverse)
        != resource.current_blob
    ):
        raise RuntimeError(
            f"segment {SEGMENT} reverse overlay drifted"
        )
    changed = sum(
        translation != reverse[key]
        for key, translation in replacements.items()
    )
    candidate_sha256 = hashlib.sha256(candidate).hexdigest().upper()
    if (
        changed != EXPECTED_CHANGED_LITERAL_COUNT
        or candidate_sha256 != EXPECTED_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate digest drifted"
        )
    return candidate, candidate_sha256, changed


def build_rows() -> tuple[
    Any,
    list[dict[str, Any]],
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
    assert_completed_base_policy(prepared)
    assert_archive_contracts(records_by_label)
    assert_mapping_and_controls(records_by_label)
    assert_boundary_contracts(records_by_label)
    assert_semantics()

    current = records_by_label["pk_current"]
    for coordinate, translation in TRANSLATIONS.items():
        key = tuple(int(value) for value in coordinate.split(":"))
        current_text = literal_texts(current, key[:2])[key[2]]
        if (
            not ENGINE.is_visible_translation_candidate(current_text)
            or UTIL.layout_signature(translation)
            != UTIL.layout_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} protected layout drifted: "
                f"{coordinate}"
            )

    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records_by_label,
    )
    modes_by_record = {
        int(row[0]): row for row in call_modes(
            records_by_label["pk_jp"],
            current,
        )
    }
    rows: list[dict[str, Any]] = []
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        translation = TRANSLATIONS[coordinate]
        pending = coordinate in RUNTIME_PENDING_COORDINATES
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        row: dict[str, Any] = {
            "schema": ENGINE.DECISION_SCHEMA,
            "resource": "pk_msggame",
            "coordinate": coordinate,
            "source_record_raw_sha256":
            target["source_record_raw_sha256"],
            "current_ko_utf16le_sha256":
            target["current_ko_utf16le_sha256"],
            "translation": translation,
            "semantic_review": "approved",
            "scope_classification": (
                "runtime_fragment_pending"
                if pending
                else "retranslated"
            ),
            "layout_review": "unchanged_from_current",
            "runtime_review": "pending" if pending else "not_required",
            "basis": BASIS,
            "historic_korean_used": False,
            "switch_korean_used": False,
            "mapped_base_record_id": record_id - 6,
            "base_policy_coordinate": base_coordinate(coordinate),
            "pk_literal_composition_adaptation":
            coordinate in PK_MORPHOLOGY_ADAPTATIONS,
            "pk_protected_line_adaptation":
            coordinate in PK_LAYOUT_ADAPTATIONS,
            "glossary_terminology_adaptation":
            coordinate in TERMINOLOGY_ADAPTATIONS,
            "source_style_quote_normalized":
            coordinate in SOURCE_STYLE_QUOTE_NORMALIZED_COORDINATES,
            "pk_shifted_gap_record":
            record_id in EXPECTED_GAP_DIVERGENCE_RECORD_IDS,
        }
        if coordinate == "2:220:2":
            row["base_policy_companion_coordinate"] = "2:214:3"
        if pending:
            mode = modes_by_record.get(record_id)
            evidence_mode, example = (
                RUNTIME_INTEGRATION_EVIDENCE[record_id]
            )
            row["runtime_assembly_evidence"] = {
                "integration_mode": evidence_mode,
                "source_free_korean_example": example,
                "source_current_control_mode": mode,
                "caller_rewrite_required_before_runtime_approval": True,
                "completed_base_classification_reused": True,
                "pk_control_gap_guarded": True,
            }
        rows.append(row)
    return prepared, rows, candidate, candidate_sha256, changed


def main() -> int:
    first = build_rows()
    second = build_rows()
    prepared, rows, candidate, candidate_sha256, changed = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
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
            f"segment {SEGMENT} decision validation drifted"
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
                "segment": "pk_msggame_B009_S1050",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "owned_record_count": len(PK_RECORD_IDS),
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "changed_literal_count": changed,
                "base_mapping_method":
                "unique_38_record_sequence_with_one_literal_composition",
                "mapped_base_record_range": [198, 235],
                "pk_minus_base_record_delta": 6,
                "pk_literal_composition_adaptation_count":
                len(PK_MORPHOLOGY_ADAPTATIONS),
                "pk_protected_line_adaptation_count":
                len(PK_LAYOUT_ADAPTATIONS),
                "glossary_terminology_adaptation_count":
                len(TERMINOLOGY_ADAPTATIONS),
                "source_style_quote_normalization_count":
                len(SOURCE_STYLE_QUOTE_NORMALIZED_COORDINATES),
                "pk_shifted_gap_record_count":
                len(EXPECTED_GAP_DIVERGENCE_RECORD_IDS),
                "source_control_count": 38,
                "current_control_count": 26,
                "runtime_integration_record_count":
                len(RUNTIME_INTEGRATION_EVIDENCE),
                "source_literal_sha256":
                EXPECTED_SOURCE_LITERAL_SHA256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "mapping_sha256": EXPECTED_MAPPING_SHA256,
                "gap_sha256": EXPECTED_GAP_SHA256,
                "call_mode_sha256": EXPECTED_CALL_MODE_SHA256,
                "candidate_sha256": candidate_sha256,
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
                "target_runtime_skeleton_exact": True,
                "completed_base_policy_exact": True,
                "source_only_flattening_guarded": True,
                "dynamic_runtime_controls_exact": True,
                "source_free_runtime_integration_evidence_exact": True,
                "left_boundary_s1049_contract_exact": True,
                "right_boundary_record_2_241_contract_exported": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tracked_builder_source_redacted": True,
                "pk_event_912_rule_applied": False,
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
