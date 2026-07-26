#!/usr/bin/env python3
"""Build source-redacted PK block-2 system-text segment 1049."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment05 as BASE_LEFT
import build_base_batch001_segment06 as BASE_A
import build_base_batch001_segment07 as BASE_B
import build_pk_batch008_segment1047 as COMMON
import build_pk_batch009_segment1048 as LEFT_PK


ENGINE = COMMON.ENGINE
GENERAL = COMMON.GENERAL
UTIL = COMMON.UTIL
HELPERS = COMMON.HELPERS
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B009_S1049.private.v1.jsonl"
)
BASE_DECISIONS = (
    (
        BASE_A.OUTPUT,
        "38F5F5B24EBA1486C55E3C9BBBA89F3031EE6B220F94DD0DA80EF6241831A099",
    ),
    (
        BASE_B.OUTPUT,
        "B85B0219068242FFDA529BF88D59E57A721101DD0957303E0ECF2917B7E42875",
    ),
)

SEGMENT = 1049
QUEUE_BATCH_ID = "pk_msggame-B009"
BLOCK_ID = 2
QUEUE_START = 67
QUEUE_STOP = 133
PK_RECORD_IDS = tuple(range(169, 204))
BASE_RECORD_IDS = tuple(range(163, 198))
PK_RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in PK_RECORD_IDS)
PK_RECORD_COUNT = 21751


literal_texts = COMMON.literal_texts
gap_bytes = COMMON.gap_bytes
archive_records = COMMON.archive_records


def target_coordinates_from_records(
    records: dict[tuple[int, int], Any],
) -> tuple[str, ...]:
    return tuple(
        f"{BLOCK_ID}:{record_id}:{literal_id}"
        for record_id in PK_RECORD_IDS
        for literal_id in range(
            len(literal_texts(records, (BLOCK_ID, record_id)))
        )
    )


BASE_TRANSLATIONS = {
    **BASE_A.TRANSLATIONS,
    **BASE_B.TRANSLATIONS,
}
BASE_RUNTIME_PENDING = (
    set(BASE_A.DYNAMIC_RUNTIME_COORDINATES)
    | set(BASE_B.DYNAMIC_RUNTIME_COORDINATES)
)
PK_LAYOUT_ADAPTATIONS = {
    "2:192:0": "옛 본거지인 ",
    "2:192:1": "의 함락으로\n본거지를 ",
    "2:192:2": "에 옮겼습니다",
}


def normalize_base_translation(value: str) -> str:
    return value.translate({0x300C: 0x22, 0x300D: 0x22})


def base_coordinate(pk_coordinate: str) -> str:
    block_id, record_id, literal_id = (
        int(value) for value in pk_coordinate.split(":")
    )
    return f"{block_id}:{record_id - 6}:{literal_id}"


def make_translation_policy(
    target_coordinates: tuple[str, ...],
) -> dict[str, str]:
    return {
        coordinate: PK_LAYOUT_ADAPTATIONS.get(
            coordinate,
            normalize_base_translation(
                BASE_TRANSLATIONS[base_coordinate(coordinate)]
            ),
        )
        for coordinate in target_coordinates
    }


def make_runtime_pending(
    target_coordinates: tuple[str, ...],
) -> set[str]:
    return {
        coordinate
        for coordinate in target_coordinates
        if base_coordinate(coordinate) in BASE_RUNTIME_PENDING
    }


DYNAMIC_RECORD_ROLES = {
    172: "court office title",
    173: "court-connected house name",
    176: "sect-leading house name",
    177: "authoritative house name",
    186: "controlled-castle count",
    187: "force and region names",
    188: "former and destination base names",
    189: "planned and new destination base names",
    190: "destination and source base names",
    191: "source and destination base names",
    192: "fallen former base and replacement base names",
    193: "policy name and additional-policy count",
    194: "policy name",
    195: "policy name after prestige reduction",
    196: "policy name conflicting with the ruler tenet",
    197: "policy name",
    198: "issued policy name and additional-policy count",
    199: "issued policy name and level",
    200: "issued policy name and additional-policy count",
    201: "issued policy name and level",
    202: "scheduled policy name",
    203: "scheduled policy name and additional-policy count",
}

EXPECTED_COORDINATE_SHA256 = (
    "740F7C7152FF5106F3007CC7BA45B26BCD8EB029AAA1DDF3C32FA7DD12C310BC"
)
EXPECTED_SOURCE_LITERAL_SHA256 = (
    "470B5646122936927E5C2EFA209937A8620BB4508F34749538B8DA3879E931B2"
)
EXPECTED_CURRENT_LITERAL_SHA256 = (
    "E872972FFF459D8C77D2B7402555743567BFBB96541E7DF49464A3680091B387"
)
EXPECTED_POLICY_SHA256 = (
    "4E55F87B3F385CAA6FB3F21432344F532DCE183BDD5471A3E41AFC2A8DB2806F"
)
EXPECTED_SOURCE_SEQUENCE_SHA256 = (
    "C06300B16D346E1B247035E89452C3385798FDE9B28DB252AAD38B2AF4CE35E0"
)
EXPECTED_MAPPING_SHA256 = (
    "34F84E3D4D83FF2CBD91E2F2AE072B50E1B97A20D17744137BEA0C8975CD9E8C"
)
EXPECTED_GAP_SHA256 = (
    "63452FE975291EDAD5567682B58AEB0776CE85070A29F63D76B4D6BCDE82FEAE"
)
EXPECTED_DYNAMIC_CONTROL_COUNT = 34
EXPECTED_DYNAMIC_CONTROL_SHA256 = (
    "094EC274A475E7EBF3132BD94519882147CE662CB5A055E430E07A51965AA60E"
)
EXPECTED_CURRENT_DIVERGENCE_IDS = {
    169,
    170,
    171,
    174,
    175,
    178,
    179,
    180,
    181,
    182,
    183,
    184,
    185,
    188,
    189,
    192,
    194,
    195,
    196,
    197,
    198,
    199,
    200,
    201,
    202,
    203,
}
EXPECTED_CURRENT_DIVERGENCE_SHA256 = (
    "9C06133A8390344A981EDF5B420315056D6C841FCC043C59CFB4B4088F9BA2A4"
)
PK_ARCHIVE_DIGESTS = {
    "pk_jp": "5BFDBECB44C2EDD112934B159C8C2EF0269C39219A9B4E51FB9C588D3ACBC6D8",
    "pk_current": "8E1BDA6A9077E54F5FCD9BB48415BDA7ADD659EA4712D326D0D3023F234573FB",
    "pk_sc": "BB8CD75538DC920D37E80E0F6C0CB7FCFB93DC0180EFB92668EDC41675CA1D71",
    "pk_tc": "358097187A18C4EB1D356E98AEA3BF5CD28E0A8399CC53F2AF3C0EACEBA75AB9",
    "pk_en": "77DD73A2F4AF75136A823DC9F24ADED4FD02CD3E1820EEA0400D9EE1C7A6DA44",
}
EXPECTED_CANDIDATE_SHA256 = (
    "2AA4150A71E2B0B66FAB02538B98141B1BAAD40DA811CE62D9502CFA2711C145"
)
EXPECTED_CHANGED_LITERAL_COUNT = 64

LEFT_RECORD_2_168_KEY = (2, 168)
LEFT_RECORD_2_168_SOURCE_RAW_SHA256 = (
    "24878F36FD4005A6E5A09E2B3272235ECB91A806FD0EB155BD2E1E8723FCA472"
)
LEFT_RECORD_2_168_CURRENT_RAW_SHA256 = (
    "B0EE1622FCB92954DE8E1F5E849D41DF50920B4349F86B364DEBA07DB8052F53"
)
LEFT_RECORD_2_168_SOURCE_LITERALS_SHA256 = (
    "49D23232E14611BAEE1AF7EFA0BBE76047F0DAC64256A668910CBE3ABB5874AF"
)
LEFT_RECORD_2_168_CURRENT_LITERALS_SHA256 = (
    "85FB6195B5E37693359A4330FCAC9ED747D1981CBE4087538743B2A9F059DAAD"
)
LEFT_RECORD_2_168_GAP_SHA256 = (
    "1CC2A260D7BB8541A016461FB0C96DC256159F81BA3AF79BBCDAFCE7619CAB2D"
)
LEFT_RECORD_2_168_SOURCE_SIGNATURE_SHA256 = (
    "9CDE259836ABA23B728E0FB99CA8BB96EE703919228B3F54D2A4587FDF376583"
)
LEFT_RECORD_2_168_CURRENT_SIGNATURE_SHA256 = (
    "F3105600A99E087F1EE55F34A6D6A852E0A9A854CB4CA6222A3C9E37BD10C73E"
)
LEFT_RECORD_2_168_POLICY = (
    BASE_LEFT.TRANSLATIONS["2:162:0"],
    BASE_LEFT.TRANSLATIONS["2:162:1"],
)
LEFT_RECORD_2_168_POLICY_SHA256 = (
    "C78ED0AD002F0E4CC5E8FF4CED7774498608DFF56F962D2A17135353381C0CC5"
)

RIGHT_RECORD_2_203_KEY = (2, 203)
RIGHT_RECORD_2_203_SOURCE_RAW_SHA256 = (
    "34FA3A01D4EA70DAA679248299EC2146F4050F277460D9BA35409DBEC7AA3CA7"
)
RIGHT_RECORD_2_203_CURRENT_RAW_SHA256 = (
    "D9DF622EADCF1448E527D6D1DC9FF13C758A37F898C016830411D7E8B5EA437D"
)
RIGHT_RECORD_2_203_SOURCE_LITERALS_SHA256 = (
    "B88C187B4D562FA880145744E8CDB1E918C253F72293427CAD82DB6A4A440E38"
)
RIGHT_RECORD_2_203_CURRENT_LITERALS_SHA256 = (
    "ECA509A13450C7168DA5C43625086C2734DB2842C04CEE8D1133F60D49592079"
)
RIGHT_RECORD_2_203_GAP_SHA256 = (
    "EE73C886762A2467E924CD38DE3B26437CCBE65DEC256CB4F81AD9FDC29D7D01"
)
RIGHT_RECORD_2_203_SOURCE_SIGNATURE_SHA256 = (
    "CD80392C5FAD83F1A07F633F33EEF1CE2C38CCD6361C503A53BFCC9218E6D2D3"
)
RIGHT_RECORD_2_203_CURRENT_SIGNATURE_SHA256 = (
    "C3A9577D63EEB1EA31FA3A3BB96704F1383D27E7D161EC45ED7A82B05273AA8B"
)
RIGHT_RECORD_2_203_POLICY = (
    normalize_base_translation(BASE_B.TRANSLATIONS["2:197:0"]),
    normalize_base_translation(BASE_B.TRANSLATIONS["2:197:1"]),
    normalize_base_translation(BASE_B.TRANSLATIONS["2:197:2"]),
)
RIGHT_RECORD_2_203_POLICY_SHA256 = (
    "1084A5327F6B1984DE18498DDF224CCBDA3EE6232A4E56BE9016759A33774DA3"
)

BASIS = (
    "pristine PK source is the sole translation authority; a globally "
    "unique 35-record literal-gap sequence independently discovers the "
    "exact Base minus-six continuation; mapped source, simplified and "
    "traditional records are byte-identical while current divergences "
    "are explicit; completed Base policy is corroboration only; PK token "
    "order adaptation prevents duplicate base-move wording; established "
    "court, sect, castle-town, prestige, tenet and policy terminology is "
    "kept consistent; every control gap, token role, line signature, "
    "outside record, reverse overlay, two-run result, source redaction "
    "and Steam read-only state is guarded; no event width rule is used"
)


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


def record_signature(
    records: dict[tuple[int, int], Any],
    record_id: int,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    key = (BLOCK_ID, record_id)
    return (
        literal_texts(records, key),
        tuple(value.hex().upper() for value in gap_bytes(records[key])),
    )


def sequence_starts(
    records: dict[tuple[int, int], Any],
    sequence: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...],
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
        if all(
            record_signature(records, start + ordinal) == signature
            for ordinal, signature in enumerate(sequence)
        )
    )


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


def direct_runtime_calls(
    records: dict[tuple[int, int], Any],
) -> tuple[tuple[int, int, int, int, int], ...]:
    rows: list[tuple[int, int, int, int, int]] = []
    for record_id in PK_RECORD_IDS:
        for gap_id, gap in enumerate(
            gap_bytes(records[(BLOCK_ID, record_id)])
        ):
            for match in HELPERS.MORPHOLOGY_JUMP_RE.finditer(gap):
                rows.append(
                    (
                        BLOCK_ID,
                        record_id,
                        gap_id,
                        match.start(),
                        int.from_bytes(match.group(1), "little"),
                    )
                )
    return tuple(rows)


def assert_tracked_builder_source_redacted() -> None:
    if ENGINE.KANA_OR_HAN_RE.search(SCRIPT.read_text(encoding="utf-8")):
        raise RuntimeError(
            f"segment {SEGMENT} tracked builder contains source text"
        )


def assert_queue_contract(
    prepared: Any,
    target_coordinates: tuple[str, ...],
) -> None:
    rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line
    ]
    rows = [
        row for row in rows if row.get("batch_id") == QUEUE_BATCH_ID
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
    expected_records = tuple(
        f"{BLOCK_ID}:{record_id}" for record_id in PK_RECORD_IDS
    )
    owned_rows = tuple(
        row["record_coordinate"] for row in rows[38:73]
    )
    if (
        len(rows) != 111
        or len(visible) != 199
        or hidden
        or visible[QUEUE_START:QUEUE_STOP] != target_coordinates
        or len(target_coordinates) != 66
        or HELPERS.canonical_sha256(target_coordinates)
        != EXPECTED_COORDINATE_SHA256
        or target_coordinates[0] != "2:169:0"
        or target_coordinates[-1] != "2:203:2"
        or rows[0]["record_coordinate"] != "2:131"
        or rows[-1]["record_coordinate"] != "2:241"
        or owned_rows != expected_records
    ):
        raise RuntimeError(
            f"segment {SEGMENT} private queue contract drifted"
        )


def assert_completed_base_policy(
    prepared: Any,
    target_coordinates: tuple[str, ...],
) -> None:
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
    for coordinate in target_coordinates:
        base_value = base_coordinate(coordinate)
        row = rows_by_coordinate.get(base_value)
        expected_pending = base_value in BASE_RUNTIME_PENDING
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
) -> bool:
    key = LEFT_RECORD_2_168_KEY
    source_contract = record_contract(records_by_label["pk_jp"], key)
    current_contract = record_contract(
        records_by_label["pk_current"],
        key,
    )
    if source_contract != (
        LEFT_RECORD_2_168_SOURCE_RAW_SHA256,
        LEFT_RECORD_2_168_SOURCE_LITERALS_SHA256,
        LEFT_RECORD_2_168_GAP_SHA256,
        LEFT_RECORD_2_168_SOURCE_SIGNATURE_SHA256,
    ) or current_contract != (
        LEFT_RECORD_2_168_CURRENT_RAW_SHA256,
        LEFT_RECORD_2_168_CURRENT_LITERALS_SHA256,
        LEFT_RECORD_2_168_GAP_SHA256,
        LEFT_RECORD_2_168_CURRENT_SIGNATURE_SHA256,
    ) or (
        gap_bytes(records_by_label["pk_jp"][key])
        != gap_bytes(records_by_label["pk_current"][key])
    ) or (
        HELPERS.canonical_sha256(LEFT_RECORD_2_168_POLICY)
        != LEFT_RECORD_2_168_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} independent left boundary drifted"
        )

    required = (
        "RIGHT_RECORD_2_168_KEY",
        "RIGHT_RECORD_2_168_SOURCE_RAW_SHA256",
        "RIGHT_RECORD_2_168_CURRENT_RAW_SHA256",
        "RIGHT_RECORD_2_168_SOURCE_LITERALS_SHA256",
        "RIGHT_RECORD_2_168_CURRENT_LITERALS_SHA256",
        "RIGHT_RECORD_2_168_GAP_SHA256",
        "RIGHT_RECORD_2_168_SOURCE_SIGNATURE_SHA256",
        "RIGHT_RECORD_2_168_CURRENT_SIGNATURE_SHA256",
        "RIGHT_RECORD_2_168_POLICY",
    )
    if not all(hasattr(LEFT_PK, name) for name in required):
        raise RuntimeError(
            f"segment {SEGMENT} S1048 boundary export is incomplete"
        )
    expected = (
        LEFT_RECORD_2_168_KEY,
        LEFT_RECORD_2_168_SOURCE_RAW_SHA256,
        LEFT_RECORD_2_168_CURRENT_RAW_SHA256,
        LEFT_RECORD_2_168_SOURCE_LITERALS_SHA256,
        LEFT_RECORD_2_168_CURRENT_LITERALS_SHA256,
        LEFT_RECORD_2_168_GAP_SHA256,
        LEFT_RECORD_2_168_SOURCE_SIGNATURE_SHA256,
        LEFT_RECORD_2_168_CURRENT_SIGNATURE_SHA256,
        LEFT_RECORD_2_168_POLICY,
    )
    actual = tuple(getattr(LEFT_PK, name) for name in required)
    if actual != expected:
        raise RuntimeError(
            f"segment {SEGMENT} mandatory S1048 boundary drifted"
        )
    return True


def assert_mapping_and_corpora(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    target_coordinates: tuple[str, ...],
    translations: dict[str, str],
) -> None:
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    source_sequence = tuple(
        record_signature(source, record_id)
        for record_id in PK_RECORD_IDS
    )
    mapping = tuple(
        (coordinate, base_coordinate(coordinate))
        for coordinate in target_coordinates
    )
    if (
        HELPERS.canonical_sha256(source_sequence)
        != EXPECTED_SOURCE_SEQUENCE_SHA256
        or sequence_starts(source, source_sequence) != (169,)
        or sequence_starts(
            records_by_label["base_jp"],
            source_sequence,
        )
        != (163,)
        or HELPERS.canonical_sha256(mapping)
        != EXPECTED_MAPPING_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} unique source mapping drifted"
        )

    source_literals = tuple(
        literal_texts(
            source,
            (BLOCK_ID, int(coordinate.split(":")[1])),
        )[int(coordinate.split(":")[2])]
        for coordinate in target_coordinates
    )
    current_literals = tuple(
        literal_texts(
            current,
            (BLOCK_ID, int(coordinate.split(":")[1])),
        )[int(coordinate.split(":")[2])]
        for coordinate in target_coordinates
    )
    if (
        HELPERS.canonical_sha256(source_literals)
        != EXPECTED_SOURCE_LITERAL_SHA256
        or HELPERS.canonical_sha256(current_literals)
        != EXPECTED_CURRENT_LITERAL_SHA256
        or HELPERS.canonical_sha256(
            tuple(translations[value] for value in target_coordinates)
        )
        != EXPECTED_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} literal or policy digest drifted"
        )
    for label, expected in PK_ARCHIVE_DIGESTS.items():
        if (
            GENERAL.subset_digest(
                records_by_label[label],
                PK_RECORD_KEYS,
            )
            != expected
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} archive drifted"
            )

    current_divergences: set[int] = set()
    for pk_record_id, base_record_id in zip(
        PK_RECORD_IDS,
        BASE_RECORD_IDS,
        strict=True,
    ):
        pk_key = (BLOCK_ID, pk_record_id)
        base_key = (BLOCK_ID, base_record_id)
        for language in ("jp", "sc", "tc"):
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
                records_by_label["base_current"],
                base_key,
            )
        ):
            current_divergences.add(pk_record_id)
        if (
            gap_bytes(records_by_label["pk_current"][pk_key])
            != gap_bytes(records_by_label["pk_jp"][pk_key])
        ):
            raise RuntimeError(
                f"segment {SEGMENT} PK current gap drifted: "
                f"{pk_record_id}"
            )
    if (
        current_divergences != EXPECTED_CURRENT_DIVERGENCE_IDS
        or HELPERS.canonical_sha256(
            tuple(sorted(current_divergences))
        )
        != EXPECTED_CURRENT_DIVERGENCE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} current divergence evidence drifted"
        )

    gap_payload = tuple(
        (
            record_id,
            tuple(
                gap.hex().upper()
                for gap in gap_bytes(source[(BLOCK_ID, record_id)])
            ),
        )
        for record_id in PK_RECORD_IDS
    )
    if HELPERS.canonical_sha256(gap_payload) != EXPECTED_GAP_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} target gap digest drifted"
        )


def assert_runtime_controls(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    runtime_pending: set[str],
) -> dict[int, int]:
    source_controls = dynamic_controls(records_by_label["pk_jp"])
    current_controls = dynamic_controls(records_by_label["pk_current"])
    controls_by_record = Counter(row[0] for row in source_controls)
    dynamic_record_ids = {
        int(coordinate.split(":")[1])
        for coordinate in runtime_pending
    }
    if (
        len(source_controls) != EXPECTED_DYNAMIC_CONTROL_COUNT
        or HELPERS.canonical_sha256(source_controls)
        != EXPECTED_DYNAMIC_CONTROL_SHA256
        or current_controls != source_controls
        or direct_runtime_calls(records_by_label["pk_jp"])
        or direct_runtime_calls(records_by_label["pk_current"])
        or dynamic_record_ids != set(DYNAMIC_RECORD_ROLES)
        or set(controls_by_record) != set(DYNAMIC_RECORD_ROLES)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime-control evidence drifted"
        )
    return dict(controls_by_record)


def assert_right_boundary(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    translations: dict[str, str],
) -> None:
    key = RIGHT_RECORD_2_203_KEY
    source_contract = record_contract(records_by_label["pk_jp"], key)
    current_contract = record_contract(
        records_by_label["pk_current"],
        key,
    )
    policy = tuple(
        translations[f"2:203:{literal_id}"]
        for literal_id in range(3)
    )
    if source_contract != (
        RIGHT_RECORD_2_203_SOURCE_RAW_SHA256,
        RIGHT_RECORD_2_203_SOURCE_LITERALS_SHA256,
        RIGHT_RECORD_2_203_GAP_SHA256,
        RIGHT_RECORD_2_203_SOURCE_SIGNATURE_SHA256,
    ) or current_contract != (
        RIGHT_RECORD_2_203_CURRENT_RAW_SHA256,
        RIGHT_RECORD_2_203_CURRENT_LITERALS_SHA256,
        RIGHT_RECORD_2_203_GAP_SHA256,
        RIGHT_RECORD_2_203_CURRENT_SIGNATURE_SHA256,
    ) or policy != RIGHT_RECORD_2_203_POLICY or (
        HELPERS.canonical_sha256(policy)
        != RIGHT_RECORD_2_203_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} right boundary drifted"
        )


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    target_coordinates: tuple[str, ...],
    translations: dict[str, str],
    runtime_pending: set[str],
) -> None:
    static_coordinates = set(target_coordinates) - runtime_pending
    if (
        len(target_coordinates) != 66
        or len(translations) != 66
        or len(runtime_pending) != 53
        or len(static_coordinates) != 13
        or set(PK_LAYOUT_ADAPTATIONS)
        != {"2:192:0", "2:192:1", "2:192:2"}
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic universe drifted"
        )
    current = records_by_label["pk_current"]
    for coordinate in target_coordinates:
        translation = translations[coordinate]
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        current_text = literal_texts(
            current,
            (block_id, record_id),
        )[literal_id]
        expected = PK_LAYOUT_ADAPTATIONS.get(
            coordinate,
            normalize_base_translation(
                BASE_TRANSLATIONS[base_coordinate(coordinate)]
            ),
        )
        if (
            translation != expected
            or not ENGINE.is_visible_translation_candidate(current_text)
            or UTIL.layout_signature(translation)
            != UTIL.layout_signature(current_text)
            or ENGINE.protected_signature(translation)
            != ENGINE.protected_signature(current_text)
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} translation policy drifted: "
                f"{coordinate}"
            )

    assembled_adaptation = (
        translations["2:192:0"],
        translations["2:192:1"],
        translations["2:192:2"],
    )
    if (
        assembled_adaptation != (
            "옛 본거지인 ",
            "의 함락으로\n본거지를 ",
            "에 옮겼습니다",
        )
        or sum(
            value.count("본거지") for value in assembled_adaptation
        )
        != 2
    ):
        raise RuntimeError(
            f"segment {SEGMENT} PK token-order adaptation drifted"
        )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    translations: dict[str, str],
) -> tuple[bytes, str]:
    resource = prepared.resources["pk_msggame"]
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
    for coordinate, translation in translations.items():
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
            f"segment {SEGMENT} reverse overlay is not byte-exact"
        )
    candidate_sha256 = hashlib.sha256(candidate).hexdigest().upper()
    if candidate_sha256 != EXPECTED_CANDIDATE_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} candidate digest drifted"
        )
    if resource.current_path.read_bytes() != resource.current_blob:
        raise RuntimeError(
            f"segment {SEGMENT} Steam input changed during build"
        )
    return candidate, candidate_sha256


def build_rows() -> tuple[
    Any,
    tuple[str, ...],
    dict[str, str],
    set[str],
    list[dict[str, Any]],
    bytes,
    str,
    bool,
    dict[int, int],
]:
    assert_tracked_builder_source_redacted()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    records_by_label = archive_records(prepared)
    target_coordinates = target_coordinates_from_records(
        records_by_label["pk_current"]
    )
    translations = make_translation_policy(target_coordinates)
    runtime_pending = make_runtime_pending(target_coordinates)
    assert_queue_contract(prepared, target_coordinates)
    assert_completed_base_policy(prepared, target_coordinates)
    left_imported = assert_left_boundary(records_by_label)
    assert_mapping_and_corpora(
        records_by_label,
        target_coordinates,
        translations,
    )
    controls_by_record = assert_runtime_controls(
        records_by_label,
        runtime_pending,
    )
    assert_right_boundary(records_by_label, translations)
    assert_semantics(
        records_by_label,
        target_coordinates,
        translations,
        runtime_pending,
    )
    candidate, candidate_sha256 = build_candidate(
        prepared,
        records_by_label,
        translations,
    )

    rows: list[dict[str, Any]] = []
    for coordinate in target_coordinates:
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        pending = coordinate in runtime_pending
        row: dict[str, Any] = {
            "schema": ENGINE.DECISION_SCHEMA,
            "resource": "pk_msggame",
            "coordinate": coordinate,
            "source_record_raw_sha256":
            target["source_record_raw_sha256"],
            "current_ko_utf16le_sha256":
            target["current_ko_utf16le_sha256"],
            "translation": translations[coordinate],
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
            "pk_protected_layout_adaptation":
            coordinate in PK_LAYOUT_ADAPTATIONS,
            "pk_event_912px_rule_applied": False,
        }
        if pending:
            row["runtime_assembly_evidence"] = {
                "record_role": DYNAMIC_RECORD_ROLES[record_id],
                "record_token_count": controls_by_record[record_id],
                "record_translation_components": [
                    translations[
                        f"{BLOCK_ID}:{record_id}:{value}"
                    ]
                    for value in range(
                        len(
                            literal_texts(
                                records_by_label["pk_current"],
                                (BLOCK_ID, record_id),
                            )
                        )
                    )
                ],
                "automatic_space_inserted": False,
                "runtime_integration_required": True,
                "caller_rewrite_required_before_runtime_approval": False,
                "pk_token_order_adapted": record_id == 192,
                "control_gap_guarded": True,
            }
        rows.append(row)

    changed = sum(
        translations[coordinate]
        != literal_texts(
            records_by_label["pk_current"],
            (
                BLOCK_ID,
                int(coordinate.split(":")[1]),
            ),
        )[int(coordinate.split(":")[2])]
        for coordinate in target_coordinates
    )
    if changed != EXPECTED_CHANGED_LITERAL_COUNT:
        raise RuntimeError(
            f"segment {SEGMENT} changed count drifted: {changed}"
        )
    return (
        prepared,
        target_coordinates,
        translations,
        runtime_pending,
        rows,
        candidate,
        candidate_sha256,
        left_imported,
        controls_by_record,
    )


def main() -> int:
    first = build_rows()
    second = build_rows()
    (
        prepared,
        target_coordinates,
        translations,
        runtime_pending,
        rows,
        candidate,
        candidate_sha256,
        left_imported,
        controls_by_record,
    ) = first
    if (
        target_coordinates != second[1]
        or translations != second[2]
        or runtime_pending != second[3]
        or ENGINE.jsonl(rows) != ENGINE.jsonl(second[4])
        or candidate != second[5]
        or candidate_sha256 != second[6]
        or left_imported != second[7]
        or controls_by_record != second[8]
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
            {"runtime_fragment_pending": 53, "retranslated": 13}
        )
        or any(
            row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            for row in rows
        )
        or prepared.resources["pk_msggame"].current_path.read_bytes()
        != prepared.resources["pk_msggame"].current_blob
    ):
        raise RuntimeError(
            f"segment {SEGMENT} final validation drifted"
        )

    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B009_S1049",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [67, 132],
                "first_coordinate": target_coordinates[0],
                "last_coordinate": target_coordinates[-1],
                "record_count": len(PK_RECORD_IDS),
                "source_literal_count": len(target_coordinates),
                "decision_count": len(rows),
                "runtime_fragment_pending": len(runtime_pending),
                "retranslated": len(rows) - len(runtime_pending),
                "changed_literal_count": EXPECTED_CHANGED_LITERAL_COUNT,
                "mapping_method":
                "global_unique_literal_gap_sequence",
                "discovered_base_record_range": [163, 197],
                "discovered_pk_minus_base_offset": 6,
                "source_sequence_sha256":
                EXPECTED_SOURCE_SEQUENCE_SHA256,
                "translation_policy_sha256": EXPECTED_POLICY_SHA256,
                "dynamic_control_count":
                EXPECTED_DYNAMIC_CONTROL_COUNT,
                "dynamic_control_sha256":
                EXPECTED_DYNAMIC_CONTROL_SHA256,
                "pk_layout_adaptation_coordinates":
                sorted(PK_LAYOUT_ADAPTATIONS),
                "s1048_boundary_import_exact": left_imported,
                "right_record_2_203_contract_exported": True,
                "candidate_sha256": candidate_sha256,
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
                "tracked_builder_source_text_count": 0,
                "mapped_jp_sc_tc_records_exact": True,
                "all_token_roles_guarded": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "pk_event_912px_rule_applied": False,
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
