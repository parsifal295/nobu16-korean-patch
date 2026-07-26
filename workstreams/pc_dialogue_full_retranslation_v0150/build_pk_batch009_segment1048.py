#!/usr/bin/env python3
"""Build source-redacted PK block-2 dialogue segment 1048 decisions."""

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

import build_base_batch001_segment03 as BASE_A
import build_base_batch001_segment04 as BASE_B
import build_base_batch001_segment05 as BASE_C
import build_pk_batch004_segment1033 as ROOT_LOW
import build_pk_batch004_segment1034 as ROOT_MIDDLE
import build_pk_batch004_segment1035 as ROOT_HIGH
import build_pk_batch006_segment1040 as ROOT904
import build_pk_batch007_segment1043 as ROOT_LATE
import build_pk_batch007_segment1044 as COMMON
import build_pk_batch008_segment1047 as LEFT_PK


ENGINE = COMMON.ENGINE
GENERAL = COMMON.GENERAL
UTIL = COMMON.UTIL
HELPERS = COMMON.HELPERS
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B009_S1048.private.v1.jsonl"
)
BASE_DECISIONS = (
    (
        BASE_A.OUTPUT,
        "355F419DE02A85E08DF5CAC1822D92704A0282AC8281C75948FC96103731A512",
    ),
    (
        BASE_B.OUTPUT,
        "27E503F726EB736E350C8ABE8C41EF3C3539FBD32B2D128EA1CBFE1BCF04779C",
    ),
    (
        BASE_C.OUTPUT,
        "1BD8A4EE882A22D2CFD19DD1FF59B00023B7EA5EE840A830EDF3304A1C195D3A",
    ),
)
LEFT_DECISION_SHA256 = (
    "9B91982E88F0548BA6C21A5590539FE1FEB9B1F837A387E60CC09D00F6C2C3DF"
)
SEGMENT = 1048
QUEUE_BATCH_ID = "pk_msggame-B009"
BLOCK_ID = 2
QUEUE_START = 0
QUEUE_STOP = 67
PK_RECORD_IDS = tuple(range(131, 169))
BASE_RECORD_IDS = tuple(range(125, 163))
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
    if 125 <= int(coordinate.split(":")[1]) <= 162
}


def base_coordinate(pk_value: str) -> str:
    block_id, record_id, literal_id = (
        int(value) for value in pk_value.split(":")
    )
    if block_id != BLOCK_ID:
        raise RuntimeError(
            f"segment {SEGMENT} unexpected block: {pk_value}"
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
    131: 3,
    132: 1,
    133: 4,
    134: 2,
    135: 2,
    136: 1,
    137: 3,
    138: 1,
    139: 1,
    140: 2,
    141: 1,
    142: 3,
    143: 2,
    144: 2,
    145: 3,
    146: 2,
    147: 2,
    148: 1,
    149: 2,
    150: 1,
    151: 2,
    152: 2,
    153: 2,
    154: 2,
    155: 2,
    156: 2,
    157: 2,
    158: 1,
    159: 1,
    160: 1,
    161: 1,
    162: 1,
    163: 1,
    164: 1,
    165: 1,
    166: 2,
    167: 2,
    168: 2,
}
TARGET_COORDINATES = tuple(
    f"{BLOCK_ID}:{record_id}:{literal_id}"
    for record_id in PK_RECORD_IDS
    for literal_id in range(LITERAL_COUNTS[record_id])
)
PK_LAYOUT_ADAPTATIONS = {
    "2:152:0": BASE_TRANSLATIONS["2:146:0"] + " ",
    "2:152:1": "\n" + BASE_TRANSLATIONS["2:146:1"],
    "2:153:0": BASE_TRANSLATIONS["2:147:0"] + " ",
    "2:153:1": "\n" + BASE_TRANSLATIONS["2:147:1"],
    "2:154:0": BASE_TRANSLATIONS["2:148:0"] + " ",
    "2:154:1": "\n" + BASE_TRANSLATIONS["2:148:1"],
    "2:155:0": BASE_TRANSLATIONS["2:149:0"] + " ",
    "2:155:1": "\n" + BASE_TRANSLATIONS["2:149:1"],
    "2:156:0": BASE_TRANSLATIONS["2:150:0"] + " ",
    "2:156:1": "\n" + BASE_TRANSLATIONS["2:150:1"],
    "2:157:0": BASE_TRANSLATIONS["2:151:0"] + " ",
    "2:157:1": "\n" + BASE_TRANSLATIONS["2:151:1"],
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
    "385DF388EBFA5044982623B1CC483360CE7FEA82BA78FF06A0C04176542FFFBD"
)
EXPECTED_CURRENT_SHA256 = (
    "C0600868C6BE7FAB5E9E1F0769803F05C11CCC5A1FA538AACC7040C40D86486B"
)
EXPECTED_POLICY_SHA256 = (
    "8B46A872465C79F5AD85AB50BE8388CDBF1354ED3EB9A3EF2AF4D38434FBDB8E"
)
EXPECTED_MAPPING_SHA256 = (
    "C58FD6C6050DBDA55A658AB06A646544D2C89D83C6166C088E59B21A5890EA71"
)
EXPECTED_GAP_SHA256 = (
    "FCF97016758363AF6D7C6208FD38CE0B113D5F862166D5EC42064B710776E5B3"
)
EXPECTED_DIRECT_CALL_SHA256 = (
    "1FCC8522BD7C2F164D2008D8C58D60301BFA161ED91F6E9A078408AEEB3889AF"
)
EXPECTED_DYNAMIC_CONTROL_COUNT = 31
EXPECTED_DYNAMIC_CONTROL_SHA256 = (
    "9F6793076F0A0E3FB8EF16F2872F97B30E6B8293CF7F70B56286B651FFAE2484"
)
EXPECTED_DIVERGENCE_SHA256 = (
    "0794B66BFABAD21C60C1C9074C53F632AB6E06A70803FD7BAE1E2D76C15F4718"
)
EXPECTED_CURRENT_DIVERGENCE_SHA256 = (
    "3407F43699DDC70703ADD1409010B51480D6DA33F01043EF086C71A0503B0213"
)
EXPECTED_CHANGED_LITERAL_COUNT = 58
EXPECTED_CANDIDATE_SHA256 = (
    "9CBE6A05B35D2A9A9CFC647F672A6C1ABA4644B465F1860431D65A35B64A2908"
)
PK_ARCHIVE_DIGESTS = {
    "pk_jp": "02A25B035C8F202FE3BF8756913D43F4D730236CE711757C6101A6DAE98F2D58",
    "pk_current": "8A596750AF0D8A54185EB5BA33078EFCBF8EE7D4554722D6601935DB2633F17F",
    "pk_sc": "BFE445E230CC052D3E0297452E3F2B111EAEB9C6E145AA38A0BEFBBF04B67081",
    "pk_tc": "E113E39CFE895F8359E5400699888CF60AD7D14CA11C11C3ADCDDA5E73EDAA9E",
    "pk_en": "007182AC6AE17A14360E34C86F7229AA57558C910CCF14A6653C7156DDE465CD",
}
EXPECTED_CURRENT_LITERAL_DIVERGENCE_IDS = (
    138,
    144,
    148,
    150,
    152,
    153,
    154,
    155,
    156,
    157,
    158,
    159,
    162,
    163,
    164,
    165,
    166,
)
EXPECTED_GAP_DIVERGENCES = {
    131: (
        ("014308000000", "014308000000"),
        ("01434A020000", "01433E020000"),
        ("014301000000", "014301000000"),
        ("014388030000050505", "01437C030000050505"),
    ),
    133: (
        ("", ""),
        (
            "014342010000014308000000",
            "014342010000014308000000",
        ),
        ("024635", "024635"),
        ("014374020000", "014368020000"),
        ("01432A040000050505", "01431E040000050505"),
    ),
    135: (
        ("", ""),
        ("014390040000", "014384040000"),
        ("014326020000050505", "01431A020000050505"),
    ),
    137: (
        ("", ""),
        ("014308000000", "014308000000"),
        ("014396040000", "01438A040000"),
        (
            "01432A0400000143FC010000050505",
            "01431E0400000143F6010000050505",
        ),
    ),
    142: (
        ("0143D0000000", "0143D0000000"),
        ("024635", "024635"),
        ("02473E", "02473E"),
        ("014348040000050505", "01433C040000050505"),
    ),
}
DIRECT_CALL_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)
EXPECTED_DIRECT_CALLS = (
    (2, 131, 0, 0, 8),
    (2, 131, 1, 0, 586),
    (2, 131, 2, 0, 1),
    (2, 131, 3, 0, 904),
    (2, 133, 1, 0, 322),
    (2, 133, 1, 6, 8),
    (2, 133, 3, 0, 628),
    (2, 133, 4, 0, 1066),
    (2, 134, 0, 0, 8),
    (2, 134, 1, 0, 1),
    (2, 135, 1, 0, 1168),
    (2, 135, 2, 0, 550),
    (2, 137, 1, 0, 8),
    (2, 137, 2, 0, 1174),
    (2, 137, 3, 0, 1066),
    (2, 137, 3, 6, 508),
    (2, 140, 1, 0, 1),
    (2, 141, 0, 0, 1),
    (2, 142, 0, 0, 208),
    (2, 142, 3, 0, 1096),
)

RUNTIME_INTEGRATION_EVIDENCE = {
    131: {
        "integration_mode": "speaker_copula_recipient_and_request",
        "source_free_korean_example": (
            "도쿠가와 님, 지금까지 가주로서 소임을 다하시느라\n"
            "참으로 고생 많으셨습니다\n"
            "뒷일은 이에야스에게 맡겨 주시오"
        ),
    },
    133: {
        "integration_mode": "name_subject_copula_and_intent",
        "source_free_korean_example": (
            "안심하십시오, 이 이에야스가\n"
            "당주가 된 이상 어떤 수를 써서라도 가문을 번영시키겠습니다"
        ),
    },
    134: {
        "integration_mode": "predecessor_and_successor_names",
        "source_free_korean_example": (
            "노부나가의 뒤를 이어\n"
            "노부타다가 가문을 끝까지 지키겠소"
        ),
    },
    135: {
        "integration_mode": "zero_prefix_and_copula_flattening",
        "source_free_korean_example": (
            "우리 가문의 앞날을 맡게 되다니\n"
            "더없는 기쁨인 동시에 막중한 소임에 마음이 다잡히는군"
        ),
    },
    137: {
        "integration_mode": "name_zero_prefix_intent_and_particle",
        "source_free_korean_example": (
            "이런, 살날이 얼마 남지 않았지만\n"
            "노부나가의 기대에는 반드시 부응하겠소"
        ),
    },
    142: {
        "integration_mode": "speaker_person_house_and_terminal",
        "source_free_korean_example": (
            "이에야스 님, 이 노부타다는 목숨을 걸고\n"
            "도쿠가와 가문의 존속과 번영을 이루어 내겠습니다"
        ),
    },
    143: {
        "integration_mode": "person_and_house_name_particles",
        "source_free_korean_example": (
            "이에야스가 도쿠가와 가문의 당주로"
        ),
    },
    144: {
        "integration_mode": "house_and_person_name_particles",
        "source_free_korean_example": (
            "도쿠가와 가문의 이에야스가 출가"
        ),
    },
    145: {
        "integration_mode": "old_and_new_force_name_boundary",
        "source_free_korean_example": (
            "오다 가문에서 도쿠가와 가문으로 세력명 변경"
        ),
    },
    146: {
        "integration_mode": "force_name_subject_and_agent",
        "source_free_korean_example": (
            "오다 가문은 도쿠가와 가문에 의해 멸망"
        ),
    },
    148: {
        "integration_mode": "person_name_subject_boundary",
        "source_free_korean_example": "이에야스가 병에 걸렸습니다",
    },
    149: {
        "integration_mode": "person_name_and_count_boundary",
        "source_free_korean_example": (
            "이에야스를 포함한 3명이 병에 걸렸습니다"
        ),
    },
    151: {
        "integration_mode": "person_name_and_count_boundary",
        "source_free_korean_example": (
            "이에야스를 포함한 3명이 병에서 회복했습니다"
        ),
    },
    152: {
        "integration_mode": "force_name_object_boundary",
        "source_free_korean_example": (
            "공략 대상인 오다 세력을 제압해 공략 방침을 달성했습니다"
        ),
    },
    157: {
        "integration_mode": "castle_name_object_boundary",
        "source_free_korean_example": (
            "공략 대상인 아즈치성을 함락했습니다"
        ),
    },
    160: {
        "integration_mode": "castle_name_direction_boundary",
        "source_free_korean_example": (
            "아즈치성 방면의 진군로가 사라져 "
            "공략 대상에서 해제되었습니다"
        ),
    },
    166: {
        "integration_mode": "office_name_predicate_boundary",
        "source_free_korean_example": (
            "당주가 막부에서 맡은 관직: 관령임"
        ),
    },
    167: {
        "integration_mode": "founder_lineage_house_name_boundary",
        "source_free_korean_example": (
            "막부를 연 시조의 계통을 잇는 가문: "
            "아시카가 가문의 당주임"
        ),
    },
    168: {
        "integration_mode": "bakufu_connection_house_name_boundary",
        "source_free_korean_example": (
            "막부와 연고가 있는 가문: 호소카와 가문의 당주임"
        ),
    },
}
EXPECTED_INTEGRATION_EVIDENCE_SHA256 = (
    "0D4329A7575C5C28F12927BAEA6C4E40010206FA7FADFCDB5953CEC1BF066969"
)

BASIS = (
    "pristine PK JP authoritative; PC EN SC TC and Base context-only; "
    "unique 38-record source-literal reverse match to completed Base "
    "records125_162 with exact plus6 mapping; five PK runtime-root gap "
    "shifts; completed Base Korean policy and classification reused "
    "coordinate by coordinate with twelve protected whitespace-only PK "
    "layout adaptations; speaker, person, force, house, castle, count, "
    "office, copula, request, intent and zero-prefix assembly guarded; "
    "historical terms and speaker register reviewed; line signatures, "
    "tokens, gaps, outside-scope records, reverse overlay, two-run "
    "reproduction and Steam read-only state checked"
)

literal_texts = COMMON.literal_texts
gap_bytes = COMMON.gap_bytes
archive_records = COMMON.archive_records

LEFT_RECORD_2_130_KEY = (2, 130)
LEFT_RECORD_2_130_SOURCE_RAW_SHA256 = (
    "8876838C95094AAB58C4DEB9EE3C7A16995122BF4336DDFD0ABBACBD1FBA00B1"
)
LEFT_RECORD_2_130_CURRENT_RAW_SHA256 = (
    "00F104DCA6FAE2FF3EDEB27167C9540ED5CAC718FC1B34C1F3DEE0DC1AE2D21F"
)
LEFT_RECORD_2_130_SOURCE_LITERAL_SHA256 = (
    "3DCFF49B340C217F257B57CA1F01D00B091351C0A03A7087E632A9CFE5550B94"
)
LEFT_RECORD_2_130_CURRENT_LITERAL_SHA256 = (
    "D0FEC981D5D0608BC40B644E1C033E01A22A3D0366A20DCEB6EC8F9489CA805E"
)
LEFT_RECORD_2_130_GAP_SHA256 = (
    "0FD5E6B1AEBD2D430875F80D538C91AD6A9814AEBAFFD45B120B91A33D4DAEBD"
)
LEFT_RECORD_2_130_SOURCE_SIGNATURE_SHA256 = (
    "2387A8E4C4F8DD4E9E0AAF269C96A5870B82177544B5CA87543AAD7A959FEE0F"
)
LEFT_RECORD_2_130_CURRENT_SIGNATURE_SHA256 = (
    "891CB9437CB5D75C2B4B31925394CB1AA669E52537A2A01229A106FB8FE3C2BF"
)

RIGHT_RECORD_2_168_KEY = (2, 168)
RIGHT_RECORD_2_168_SOURCE_RAW_SHA256 = (
    "24878F36FD4005A6E5A09E2B3272235ECB91A806FD0EB155BD2E1E8723FCA472"
)
RIGHT_RECORD_2_168_CURRENT_RAW_SHA256 = (
    "B0EE1622FCB92954DE8E1F5E849D41DF50920B4349F86B364DEBA07DB8052F53"
)
RIGHT_RECORD_2_168_SOURCE_LITERALS_SHA256 = (
    "49D23232E14611BAEE1AF7EFA0BBE76047F0DAC64256A668910CBE3ABB5874AF"
)
RIGHT_RECORD_2_168_CURRENT_LITERALS_SHA256 = (
    "85FB6195B5E37693359A4330FCAC9ED747D1981CBE4087538743B2A9F059DAAD"
)
RIGHT_RECORD_2_168_GAP_SHA256 = (
    "1CC2A260D7BB8541A016461FB0C96DC256159F81BA3AF79BBCDAFCE7619CAB2D"
)
RIGHT_RECORD_2_168_SOURCE_SIGNATURE_SHA256 = (
    "9CDE259836ABA23B728E0FB99CA8BB96EE703919228B3F54D2A4587FDF376583"
)
RIGHT_RECORD_2_168_CURRENT_SIGNATURE_SHA256 = (
    "F3105600A99E087F1EE55F34A6D6A852E0A9A854CB4CA6222A3C9E37BD10C73E"
)
RIGHT_RECORD_2_168_POLICY = (
    TRANSLATIONS["2:168:0"],
    TRANSLATIONS["2:168:1"],
)
RIGHT_RECORD_2_168_POLICY_SHA256 = (
    "C78ED0AD002F0E4CC5E8FF4CED7774498608DFF56F962D2A17135353381C0CC5"
)
RIGHT_RECORD_2_168_GAP_HEX = ("", "02463E", "050505")
RIGHT_RECORD_2_168_OWNED_LITERAL_IDS = (0, 1)
RIGHT_RECORD_2_168_LAYOUT_SIGNATURE = (
    (0, (("", ""),), (0,), (), (), (), (), "", ""),
    (0, (("", ""),), (0,), (), (), (), (), "", ""),
)
RIGHT_RECORD_2_168_RAW_SHA256 = {
    "pk_jp": RIGHT_RECORD_2_168_SOURCE_RAW_SHA256,
    "pk_current": RIGHT_RECORD_2_168_CURRENT_RAW_SHA256,
}
RIGHT_RECORD_2_168_LITERAL_SHA256 = {
    "pk_jp": RIGHT_RECORD_2_168_SOURCE_LITERALS_SHA256,
    "pk_current": RIGHT_RECORD_2_168_CURRENT_LITERALS_SHA256,
}
RIGHT_RECORD_2_168_SIGNATURE_SHA256 = {
    "pk_jp": RIGHT_RECORD_2_168_SOURCE_SIGNATURE_SHA256,
    "pk_current": RIGHT_RECORD_2_168_CURRENT_SIGNATURE_SHA256,
}


def record_contract(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, str, str, str]:
    record = records[key]
    literals = literal_texts(records, key)
    gaps = tuple(value.hex().upper() for value in gap_bytes(record))
    return (
        hashlib.sha256(record.data).hexdigest().upper(),
        HELPERS.canonical_sha256(literals),
        HELPERS.canonical_sha256(gaps),
        HELPERS.canonical_sha256((literals, gaps)),
    )


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
    owned_rows = tuple(
        row["record_coordinate"] for row in rows[: len(PK_RECORD_IDS)]
    )
    if (
        len(rows) != 111
        or len(visible) != 199
        or hidden
        or visible[QUEUE_START:QUEUE_STOP] != TARGET_COORDINATES
        or rows[0]["record_coordinate"] != "2:131"
        or rows[-1]["record_coordinate"] != "2:241"
        or owned_rows
        != tuple(f"2:{record_id}" for record_id in PK_RECORD_IDS)
        or visible[QUEUE_STOP] != "2:169:0"
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
    for coordinate in TARGET_COORDINATES:
        base_value = base_coordinate(coordinate)
        row = rows_by_coordinate.get(base_value)
        expected_pending = coordinate in RUNTIME_PENDING_COORDINATES
        if (
            row is None
            or row["resource"] != "base_msggame"
            or row["translation"] != BASE_TRANSLATIONS[base_value]
            or row["semantic_review"] != "approved"
            or row["scope_classification"]
            != (
                "runtime_fragment_pending"
                if expected_pending
                else "retranslated"
            )
            or row["runtime_review"]
            != ("pending" if expected_pending else "not_required")
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
    key = LEFT_RECORD_2_130_KEY
    source = record_contract(records_by_label["pk_jp"], key)
    current = record_contract(records_by_label["pk_current"], key)
    if (
        not LEFT_PK.OUTPUT.is_file()
        or hashlib.sha256(LEFT_PK.OUTPUT.read_bytes()).hexdigest().upper()
        != LEFT_DECISION_SHA256
        or LEFT_PK.TARGET_COORDINATES[-1] != "2:130:0"
        or LEFT_PK.TRANSLATIONS["2:130:0"]
        != BASE_A.TRANSLATIONS["2:124:0"]
        or source
        != (
            LEFT_RECORD_2_130_SOURCE_RAW_SHA256,
            LEFT_RECORD_2_130_SOURCE_LITERAL_SHA256,
            LEFT_RECORD_2_130_GAP_SHA256,
            LEFT_RECORD_2_130_SOURCE_SIGNATURE_SHA256,
        )
        or current
        != (
            LEFT_RECORD_2_130_CURRENT_RAW_SHA256,
            LEFT_RECORD_2_130_CURRENT_LITERAL_SHA256,
            LEFT_RECORD_2_130_GAP_SHA256,
            LEFT_RECORD_2_130_CURRENT_SIGNATURE_SHA256,
        )
        or gap_bytes(records_by_label["pk_jp"][key])
        != gap_bytes(records_by_label["pk_current"][key])
    ):
        raise RuntimeError(
            f"segment {SEGMENT} S1047 left boundary drifted"
        )


def assert_mapping_and_corpora(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source_sequence = record_literal_sequence(
        records_by_label["pk_jp"], PK_RECORD_IDS[0], len(PK_RECORD_IDS)
    )
    if (
        sequence_starts(records_by_label["base_jp"], source_sequence)
        != (BASE_RECORD_IDS[0],)
        or sequence_starts(records_by_label["pk_jp"], source_sequence)
        != (PK_RECORD_IDS[0],)
        or HELPERS.canonical_sha256(mapping_pairs())
        != EXPECTED_MAPPING_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} source mapping drifted"
        )
    source_literals = tuple(
        literal_texts(
            records_by_label["pk_jp"],
            (BLOCK_ID, int(coordinate.split(":")[1])),
        )[int(coordinate.split(":")[2])]
        for coordinate in TARGET_COORDINATES
    )
    current_literals = tuple(
        literal_texts(
            records_by_label["pk_current"],
            (BLOCK_ID, int(coordinate.split(":")[1])),
        )[int(coordinate.split(":")[2])]
        for coordinate in TARGET_COORDINATES
    )
    if (
        HELPERS.canonical_sha256(source_literals)
        != EXPECTED_SOURCE_SHA256
        or HELPERS.canonical_sha256(current_literals)
        != EXPECTED_CURRENT_SHA256
        or HELPERS.canonical_sha256(
            tuple(
                TRANSLATIONS[coordinate]
                for coordinate in TARGET_COORDINATES
            )
        )
        != EXPECTED_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} source/current/policy digest drifted"
        )
    for label, expected in PK_ARCHIVE_DIGESTS.items():
        if (
            GENERAL.subset_digest(
                records_by_label[label], PK_RECORD_KEYS
            )
            != expected
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} archive drifted"
            )

    current_divergences: list[int] = []
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
            != literal_texts(
                records_by_label["base_current"], base_key
            )
        ):
            current_divergences.append(pk_record_id)

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

    current_divergence_tuple = tuple(current_divergences)
    if (
        current_divergence_tuple
        != EXPECTED_CURRENT_LITERAL_DIVERGENCE_IDS
        or HELPERS.canonical_sha256(current_divergence_tuple)
        != EXPECTED_CURRENT_DIVERGENCE_SHA256
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
        or dynamic_controls(records_by_label["pk_current"])
        != controls
        or HELPERS.canonical_sha256(controls)
        != EXPECTED_DYNAMIC_CONTROL_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime-control evidence drifted"
        )

    pk_root508_policy = tuple(
        ROOT_LOW.TRANSLATION_POLICY_ALL[
            record_id - ROOT_LOW.OWNED_RECORD_IDS[0]
        ]
        for record_id in ROOT_LOW.FULL_PK_GROUPS[508]
    )
    pk_root586_policy = tuple(
        ROOT_MIDDLE.TRANSLATIONS_BY_RECORD[record_id]
        for record_id in ROOT_MIDDLE.FULL_PK_GROUPS[586]
    )
    base_root574_policy = tuple(
        ROOT_MIDDLE.BASE_NEXT.FULL_TRANSLATION_POLICY[record_id]
        for record_id
        in ROOT_MIDDLE.BASE_NEXT.FULL_TERMINAL_GROUPS[574]
    )
    pk_root628_policy = tuple(
        ROOT_HIGH.TRANSLATIONS_BY_RECORD[record_id]
        for record_id in ROOT_HIGH.FULL_PK_GROUPS[628]
    )
    base_root616_policy = tuple(
        ROOT_HIGH.RIGHT_BASE.FULL_TRANSLATION_POLICY[record_id]
        for record_id
        in ROOT_HIGH.RIGHT_BASE.FULL_TERMINAL_GROUPS[616]
    )
    base_root892_policy = tuple(
        ROOT904.BASE_RIGHT.FULL_TRANSLATION_POLICY[record_id]
        for record_id in ROOT904.BASE_RIGHT.FULL_TERMINAL_GROUPS[892]
    )
    if (
        pk_root586_policy != base_root574_policy
        or pk_root628_policy != base_root616_policy
        or pk_root508_policy
        != ROOT_LOW.BASE_MIDDLE.TRANSLATION_POLICY_BY_ROOT[502]
        or ROOT904.TRANSLATION_POLICY_BY_ROOT[904]
        != base_root892_policy
        or ROOT_LATE.ROOT_TRANSLATION_POLICY[1066]
        != ROOT_LATE.BASE_LEFT.TRANSLATION_MATRICES[1054]
        or ROOT_LATE.ROOT_TRANSLATION_POLICY[1096]
        != ROOT_LATE.BASE_RIGHT.TRANSLATION_POLICY_BY_ROOT[1084]
        or ROOT_MIDDLE.LEFT_ROOT550_FULL_POLICY
        != ROOT_LOW.BASE_MIDDLE.TRANSLATION_POLICY_BY_ROOT[538]
        or COMMON.BASE_RIGHT.TRANSLATION_POLICY_BY_ROOT[1156]
        != ("", "", "", "", "", "", "")
        or COMMON.BASE_RIGHT.TRANSLATION_POLICY_BY_ROOT[1162]
        != ("", "", "", "", "", "", "")
    ):
        raise RuntimeError(
            f"segment {SEGMENT} shifted runtime policy drifted"
        )

    expected_sites = {
        586: {"2:131:1:0"},
        904: {"2:131:3:0"},
        628: {"2:133:3:0"},
        1066: {"2:133:4:0", "2:137:3:0"},
        1168: {"2:135:1:0"},
        550: {"2:135:2:0"},
        1174: {"2:137:2:0"},
        508: {"2:137:3:6"},
        1096: {"2:142:3:0"},
    }
    for root, sites in expected_sites.items():
        actual = set(
            HELPERS.root_call_sites(records_by_label["pk_jp"], root)
        )
        if not sites.issubset(actual):
            raise RuntimeError(
                f"segment {SEGMENT} root call-site drifted: {root}"
            )

    if (
        HELPERS.canonical_sha256(RUNTIME_INTEGRATION_EVIDENCE)
        != EXPECTED_INTEGRATION_EVIDENCE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} integration evidence drifted"
        )
    for evidence in RUNTIME_INTEGRATION_EVIDENCE.values():
        sample = str(evidence["source_free_korean_example"])
        if (
            ENGINE.KANA_OR_HAN_RE.search(sample)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(sample)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} source-free sample drifted"
            )


def assert_semantics() -> None:
    expected_adaptations = {
        f"2:{record_id}:{literal_id}"
        for record_id in range(152, 158)
        for literal_id in (0, 1)
    }
    if (
        len(TARGET_COORDINATES) != 67
        or len(TRANSLATIONS) != 67
        or len(RUNTIME_PENDING_COORDINATES) != 59
        or len(STATIC_COORDINATES) != 8
        or set(PK_LAYOUT_ADAPTATIONS) != expected_adaptations
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
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(
                translation
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} translation policy drifted: "
                f"{coordinate}"
            )
    if ENGINE.KANA_OR_HAN_RE.search(
        SCRIPT.read_text(encoding="utf-8")
    ):
        raise RuntimeError(
            f"segment {SEGMENT} tracked builder contains source text"
        )


def assert_right_boundary(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    key = RIGHT_RECORD_2_168_KEY
    source = record_contract(records_by_label["pk_jp"], key)
    current = record_contract(records_by_label["pk_current"], key)
    if (
        key != (BLOCK_ID, PK_RECORD_IDS[-1])
        or source
        != (
            RIGHT_RECORD_2_168_SOURCE_RAW_SHA256,
            RIGHT_RECORD_2_168_SOURCE_LITERALS_SHA256,
            RIGHT_RECORD_2_168_GAP_SHA256,
            RIGHT_RECORD_2_168_SOURCE_SIGNATURE_SHA256,
        )
        or current
        != (
            RIGHT_RECORD_2_168_CURRENT_RAW_SHA256,
            RIGHT_RECORD_2_168_CURRENT_LITERALS_SHA256,
            RIGHT_RECORD_2_168_GAP_SHA256,
            RIGHT_RECORD_2_168_CURRENT_SIGNATURE_SHA256,
        )
        or tuple(
            value.hex().upper()
            for value in gap_bytes(records_by_label["pk_jp"][key])
        )
        != RIGHT_RECORD_2_168_GAP_HEX
        or gap_bytes(records_by_label["pk_current"][key])
        != gap_bytes(records_by_label["pk_jp"][key])
        or HELPERS.canonical_sha256(RIGHT_RECORD_2_168_POLICY)
        != RIGHT_RECORD_2_168_POLICY_SHA256
        or tuple(
            UTIL.layout_signature(value)
            for value in RIGHT_RECORD_2_168_POLICY
        )
        != RIGHT_RECORD_2_168_LAYOUT_SIGNATURE
        or tuple(
            UTIL.layout_signature(value)
            for value in literal_texts(
                records_by_label["pk_current"], key
            )
        )
        != RIGHT_RECORD_2_168_LAYOUT_SIGNATURE
        or RIGHT_RECORD_2_168_OWNED_LITERAL_IDS != (0, 1)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} S1049 right boundary drifted"
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
        if literal_texts(candidate_records, key[:2])[key[2]] != (
            translation
        ):
            raise RuntimeError(
                f"segment {SEGMENT} candidate literal drifted: "
                f"{coordinate}"
            )
    if (
        tuple(
            literal_texts(
                candidate_records, RIGHT_RECORD_2_168_KEY
            )[literal_id]
            for literal_id in RIGHT_RECORD_2_168_OWNED_LITERAL_IDS
        )
        != RIGHT_RECORD_2_168_POLICY
        or ENGINE.rebuild_packed_with_literals(candidate, reverse)
        != resource.current_blob
    ):
        raise RuntimeError(
            f"segment {SEGMENT} reverse or right boundary drifted"
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
    assert_right_boundary(records_by_label)

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
                f"segment {SEGMENT} protected line drifted: "
                f"{coordinate}"
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
            "source_record_raw_sha256":
            target["source_record_raw_sha256"],
            "current_ko_utf16le_sha256":
            target["current_ko_utf16le_sha256"],
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
            "pk_protected_whitespace_adaptation":
            coordinate in PK_LAYOUT_ADAPTATIONS,
            "pk_specific_runtime_root_shift":
            record_id in EXPECTED_GAP_DIVERGENCES,
        }
        if pending:
            row["runtime_assembly_evidence"] = {
                "direct_call_targets": sorted(
                    set(calls_by_record.get(record_id, []))
                ),
                "dynamic_control_guarded": any(
                    item[0] == record_id
                    for item in dynamic_controls(
                        records_by_label["pk_jp"]
                    )
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
            (BLOCK_ID, int(coordinate.split(":")[1])),
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
        len(rows) != 67
        or len(validated) != 67
        or counts
        != Counter(
            {"runtime_fragment_pending": 59, "retranslated": 8}
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
                "segment": "pk_msggame_B009_S1048",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [0, 66],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "owned_record_count": len(PK_RECORD_IDS),
                "source_literal_count": len(TARGET_COORDINATES),
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "changed_literal_count": EXPECTED_CHANGED_LITERAL_COUNT,
                "base_mapping_method":
                "unique_38_record_source_literal_reverse_match",
                "discovered_base_record_range": [125, 162],
                "discovered_pk_minus_base_offset": 6,
                "pk_specific_runtime_root_shift_count":
                len(EXPECTED_GAP_DIVERGENCES),
                "pk_protected_whitespace_adaptation_count":
                len(PK_LAYOUT_ADAPTATIONS),
                "source_sequence_sha256": EXPECTED_SOURCE_SHA256,
                "translation_policy_sha256": EXPECTED_POLICY_SHA256,
                "mapping_sha256": EXPECTED_MAPPING_SHA256,
                "gap_sha256": EXPECTED_GAP_SHA256,
                "direct_call_sha256": EXPECTED_DIRECT_CALL_SHA256,
                "dynamic_control_count":
                EXPECTED_DYNAMIC_CONTROL_COUNT,
                "dynamic_control_sha256":
                EXPECTED_DYNAMIC_CONTROL_SHA256,
                "candidate_sha256": candidate_sha256,
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
                "left_boundary_s1047_contract_exact": True,
                "right_boundary_s1049_contract_exported": True,
                "target_runtime_skeleton_exact": True,
                "completed_base_policy_exact": True,
                "pk_runtime_root_shifts_exact": True,
                "pk_runtime_root_shift_policies_equivalent": True,
                "dynamic_runtime_controls_exact": True,
                "historical_terms_and_register_reviewed": True,
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
