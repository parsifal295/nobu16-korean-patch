#!/usr/bin/env python3
"""Build source-redacted PK mixed internal-test/dialogue segment 1046."""

from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment08 as BASE_TEST
import build_base_batch001_segment01 as BASE_DIALOGUE
import build_pk_batch001_segment1025 as HELPERS
import build_pk_batch005_segment1038 as COMMON
import build_pk_batch007_segment1042 as PRIOR
import build_pk_batch008_segment1045 as LEFT_PK


ENGINE = PRIOR.ENGINE
GENERAL = PRIOR.GENERAL
UTIL = PRIOR.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B008_S1046.private.v1.jsonl"
)
BASE_TEST_DECISIONS = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S08.private.v1.jsonl"
)

SEGMENT = 1046
QUEUE_BATCH_ID = "pk_msggame-B008"
QUEUE_START = 67
QUEUE_STOP = 134
PK_RECORD_COUNT = 21751

BLOCK1_LITERAL_COUNTS = {
    9: 3,
    10: 6,
    11: 5,
    12: 6,
    13: 2,
    14: 4,
    15: 4,
    16: 2,
    17: 1,
    18: 4,
    19: 3,
    20: 4,
    21: 3,
    22: 3,
    23: 3,
    24: 2,
    25: 3,
    26: 2,
    27: 2,
    28: 2,
    29: 1,
    30: 3,
}
NON_DISPLAY_COORDINATES = (
    ("1:9:2",)
    + tuple(
        f"1:{record_id}:{literal_id}"
        for record_id in range(10, 31)
        for literal_id in range(BLOCK1_LITERAL_COUNTS[record_id])
    )
)
DIALOGUE_COORDINATE = "2:86:0"
TARGET_COORDINATES = NON_DISPLAY_COORDINATES + (DIALOGUE_COORDINATE,)
OWNED_RECORD_KEYS = (
    tuple((1, record_id) for record_id in range(9, 32))
    + ((2, 85), (2, 86))
)
VISIBLE_RECORD_KEYS = (
    tuple((1, record_id) for record_id in range(9, 31))
    + ((2, 86),)
)
BLOCK1_KEYS = tuple((1, record_id) for record_id in range(32))
BLOCK2_CONTEXT_KEYS = tuple((2, record_id) for record_id in range(84, 91))
HIDDEN_KEYS = ((1, 31), (2, 85))
QUEUE_HIDDEN_COORDINATES = (
    "0:2728:0",
    "1:2:0",
    "1:31:0",
    "2:85:0",
)

TRANSLATION = BASE_DIALOGUE.TRANSLATIONS["2:80:0"]
TRANSLATIONS = {DIALOGUE_COORDINATE: TRANSLATION}
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "92EB898328C5B268EBB7BC49CADCB798A30909373A590A1BC3EBE0DED7896D70"
)
BASE_DIALOGUE_DECISION_SHA256 = (
    "0BAB462CFF06D1429C128B4E2EF0EF8E6C6F8EFEFEF5A8560DCB4D641EE2FF22"
)

EXPECTED_COORDINATE_SHA256 = (
    "828E036D1CD082A29FDDE78CF0EFBBB036C20FAC2BD5CC07B2B41F4560F3BFFE"
)
EXPECTED_SOURCE_LITERAL_SHA256 = (
    "E38F3B89863AEDE8E2AD41FC620F3971472BAC199A958C3BC4F8C4A6785A4F4A"
)
EXPECTED_CURRENT_LITERAL_SHA256 = (
    "53BCA0EF30720632A014E13A6FECA7BFECC6F42C51DDA031307BAB7B0EC51A95"
)

OWNED_ARCHIVE_DIGESTS = {
    "pk_jp": "08097D6A82F407DB3D141A7433588235ABDA713A47B45741020426E266E1B407",
    "pk_current": "AFD977B90B95EDB350CC570EFA4EFE4C0D6D7EC88C5E09AD3D08CFF4FDFDD310",
    "pk_sc": "B2F07A1A668A7EC0B584A6A2EF2314A709DEF47D659A09A5B77C4A3F8F0F1986",
    "pk_tc": "E6479F7CFE729B228D52CA2C28151B5D901175A84181BA2BD3DC940291308AE9",
    "pk_en": "618763F184FD8A0DCB097AD50EFD4183E760997B64EE8FC6710D2E315BAC8829",
}
BLOCK1_ARCHIVE_DIGESTS = {
    "pk_jp": "583D870F49524DAC0751B15C6C1AACF26C0012E4F1752D292E43EAA3F223B935",
    "pk_current": "1648327A6092F489E040C4F635FDFCB3DABB6AEAA5E58AFBF79B7D7A9DA2AFF1",
    "pk_sc": "508E1AC6D965C5AC2331DFE82C38B2313CD3BFA2C77726963E5F7992D18823C5",
    "pk_tc": "B7AF3F49BD9A6CFB5EC5E55F0EC878C51A9ADE597BCF618D96829F791C958F92",
    "pk_en": "CDF929BDAF9DEC18E1A9E5CEA57528AE499E921CD9B7193CB50A849CC5413D2C",
}
BLOCK2_CONTEXT_ARCHIVE_DIGESTS = {
    "pk_jp": "7E4C948D32D773AFDD630EC109AD9DA850050CB7FB1E0187DD63878354D841F0",
    "pk_current": "F5F44C6B6DFC37598D0A4E9439CCEC8C87E31D06A0E965C1101CF0D991FD6C11",
    "pk_sc": "709EB839916C5A158F3D6B778E6E0323D9E5AAF68517F63F58B1622DD6616BF6",
    "pk_tc": "BF62A82C30015E3D3633C11FB4B858F2990B0C477AE24DFF8A14B80DB7BE0F3A",
    "pk_en": "22E9D9ED4F10C65ADA7E7D1F06685F6A776F762276F3496E406AF88B6801B914",
}
VISIBLE_RECORD_ARCHIVE_DIGESTS = {
    "pk_jp": "D5D6F46F61F73808FB993970C76959B79C9D7805A166FA255B208EC36C48AC24",
    "pk_current": "F47A4975F8DAFFB1F753EBF39209BD5DB42CB12ACED600431D11E50488C4110A",
    "pk_sc": "CEA94C97C6A507ECF700169ABEBCBA8F0216EBF43A4B9257E1972B15AFAF7963",
    "pk_tc": "D869140BBDDF3FE8EAAC0329724E8DDB92AAD60330AC0D683B2D9F9A130F1155",
    "pk_en": "2F95D6285743F2932C8A53B04101CD5647702CC69C303D52EBF74395E4F3B7A5",
}

EXPECTED_BLOCK1_LITERAL_SEQUENCE_SHA256 = (
    "85EC82FA0B1C7F644CC36BAB23B443E025F2885D9A756276E3076EA630CBA610"
)
EXPECTED_BLOCK1_0143_MAPPING_SHA256 = (
    "CA04952E6924F0413CB75DDED1FB5D98B7305775CADD4B117FB3ABF508648D17"
)
EXPECTED_BLOCK1_JUMP_SHA256 = (
    "4F06952DC7FED0945C059E1C5F1E4BF774F9096E4745BF503D2BCFDDEC87BCC5"
)
EXPECTED_MULTILINGUAL_SKELETON_SHA256 = (
    "E4D7EE0EAB878E0F3869B21234A9A8CC742666C2B6B3D990B384A0E92AB1B802"
)
EXPECTED_HIDDEN_ARCHIVE_SHA256 = (
    "33340A6F7468868F6277B9702236A963FDACD9971CB9C0CCD093CEA186A1079C"
)
BASE_TEST_DECISION_SHA256 = (
    "3D741EF9B1AE8F1BA500EAB25D649EB670B8A7B790C97CCF55A078EC9E61E116"
)

SHARED_RECORD_1_9_KEY = (1, 9)
SHARED_RECORD_1_9_SOURCE_RAW_SHA256 = (
    "B17ABAF3DD05C3425272F58EF2795282143E326984A84A4A4A506584DA6F9FB7"
)
SHARED_RECORD_1_9_CURRENT_RAW_SHA256 = (
    "CF1B839E1FB98866959C0B9B806C8EC01A542378B5CE1E4B93150231221EC6D0"
)
SHARED_RECORD_1_9_SOURCE_LITERALS_SHA256 = (
    "D1CCC56BD4A76F82314B8C88446AA243F1558100443D21471295FD46EF5B8B45"
)
SHARED_RECORD_1_9_CURRENT_LITERALS_SHA256 = (
    "E72614E1EE4DFC182831C9470F31BF4D412A39C663DDC1BD02D9DFE71DCA7674"
)
SHARED_RECORD_1_9_SOURCE_GAPS_SHA256 = (
    "6A800E7FA6A32B19093E5AD9D8F42E1DA229A85DFF39EB5F8239AE0764B5ADD8"
)
SHARED_RECORD_1_9_CURRENT_GAPS_SHA256 = (
    "6A800E7FA6A32B19093E5AD9D8F42E1DA229A85DFF39EB5F8239AE0764B5ADD8"
)
SHARED_RECORD_1_9_SOURCE_SIGNATURE_SHA256 = (
    "16DBCEE38F2692BC0470DC85E0B39CD5FE96A8C9843E9C297674BB71A4818980"
)
SHARED_RECORD_1_9_CURRENT_SIGNATURE_SHA256 = (
    "BC6C574E7D52A6946EC97E9C7D58F346388A354114150B11B2417F12352B316B"
)

RIGHT_RECORD_2_86_KEY = (2, 86)
RIGHT_RECORD_2_86_SOURCE_RAW_SHA256 = (
    "18A1AE5187A5384BBB5CB268060C623488ABD86FFE0FF89315D08E51AA13B6B9"
)
RIGHT_RECORD_2_86_CURRENT_RAW_SHA256 = (
    "DE87AC9D587CE62438031D21F4FBB2ABB72CABF754A265C2414C2D4FE1FAEEB8"
)
RIGHT_RECORD_2_86_SOURCE_LITERAL_SHA256 = (
    "97AC38AD52D281170CE13AF52DBE88B231CC334BB452B2D8497461CE9B00B640"
)
RIGHT_RECORD_2_86_CURRENT_LITERAL_SHA256 = (
    "0D3AA97349AC6710D4DE169F9FCAADB22D7B2465C1045CEF84A918E2BD09FF08"
)
RIGHT_RECORD_2_86_GAP_SHA256 = (
    "7ED182E06D902CDCF3965BA128BBD9951AFCFF21E8FA25D427CD62B887EC0E29"
)
RIGHT_RECORD_2_86_SOURCE_SIGNATURE_SHA256 = (
    "4BF5CC0AD810C68121AE20BFD1E7CE9AA8B48EA1EE1ABBE050C688E245E679D2"
)
RIGHT_RECORD_2_86_CURRENT_SIGNATURE_SHA256 = (
    "428D1FBB56B441732193EFA8955863C5081A3463EE860DEF95EBD02F35EFCD45"
)
RIGHT_RECORD_2_86_POLICY = TRANSLATION
RIGHT_RECORD_2_86_LAYOUT_SIGNATURE = (
    1,
    (("", ""), ("", "")),
    (0, 0),
    (),
    (),
    (),
    (),
    "",
    "",
)

CONTROL_0143_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)
CLASSIFICATION_BASIS = (
    "independent PK block-one graph and multilingual skeleton evidence; "
    "the owned coordinates are unreachable from the block's internal "
    "jump graph and belong to the same grammar/font test scaffold that "
    "is independently classified in Base; pristine bytes are preserved"
)
DIALOGUE_BASIS = (
    "pristine PK is the sole translation authority; exact pristine JP "
    "and control correspondence imports the completed Base S01 Korean "
    "policy, follows the project glossary's standalone coming-of-age "
    "term, retains the princess title and reflective plain-period voice, "
    "and preserves the two-line token-free skeleton"
)


literal_texts = COMMON.literal_texts
gap_bytes = COMMON.gap_bytes
archive_records = COMMON.archive_records
canonical_sha256 = HELPERS.canonical_sha256


def record_contract(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, str, str, str]:
    record = records[key]
    literals = literal_texts(records, key)
    gaps = tuple(value.hex().upper() for value in gap_bytes(record))
    return (
        hashlib.sha256(record.data).hexdigest().upper(),
        canonical_sha256(literals),
        canonical_sha256(gaps),
        canonical_sha256((literals, gaps)),
    )


def literal_sequence_hits(
    records: dict[tuple[int, int], Any],
    sequence: tuple[tuple[str, ...], ...],
) -> tuple[tuple[int, int], ...]:
    hits: list[tuple[int, int]] = []
    for block_id in sorted({key[0] for key in records}):
        record_ids = sorted(
            key[1] for key in records if key[0] == block_id
        )
        if not record_ids:
            continue
        for start in range(record_ids[0], record_ids[-1] + 1):
            if all(
                (block_id, start + ordinal) in records
                and literal_texts(
                    records,
                    (block_id, start + ordinal),
                )
                == expected
                for ordinal, expected in enumerate(sequence)
            ):
                hits.append((block_id, start))
    return tuple(hits)


def exact_signature_hits(
    records: dict[tuple[int, int], Any],
    signature: tuple[tuple[str, ...], tuple[str, ...]],
) -> tuple[tuple[int, int], ...]:
    return tuple(
        key
        for key in sorted(records)
        if (
            literal_texts(records, key),
            tuple(value.hex().upper() for value in gap_bytes(records[key])),
        )
        == signature
    )


def block1_jump_rows(
    records: dict[tuple[int, int], Any],
) -> tuple[tuple[int, int, int, int, int], ...]:
    rows: list[tuple[int, int, int, int, int]] = []
    for record_id in range(32):
        record = records[(1, record_id)]
        for gap_id, gap in enumerate(gap_bytes(record)):
            for match in HELPERS.MORPHOLOGY_JUMP_RE.finditer(gap):
                rows.append(
                    (
                        1,
                        record_id,
                        gap_id,
                        match.start(),
                        struct.unpack("<I", match.group(1))[0],
                    )
                )
    return tuple(rows)


def normalized_0143_gap(value: bytes) -> bytes:
    result = bytearray(value)
    for match in CONTROL_0143_RE.finditer(value):
        result[match.start() + 2 : match.start() + 6] = b"\0\0\0\0"
    return bytes(result)


def multilingual_skeleton(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[object, ...], ...]:
    rows: list[tuple[object, ...]] = []
    for label in ("pk_jp", "pk_current", "pk_sc", "pk_tc", "pk_en"):
        for record_id in (3, 4, 5, 29, 30):
            literals = literal_texts(
                records_by_label[label],
                (1, record_id),
            )
            text = "".join(literals)
            categories = Counter(
                unicodedata.category(character)[0]
                for character in text
            )
            rows.append(
                (
                    label,
                    record_id,
                    len(literals),
                    sum(bool(value) for value in literals),
                    len(text),
                    text.count("\n"),
                    sum(
                        0xE000 <= ord(character) <= 0xF8FF
                        for character in text
                    ),
                    tuple(
                        (category, categories[category])
                        for category in sorted(categories)
                    ),
                )
            )
    return tuple(rows)


def assert_tracked_builder_source_redacted() -> None:
    tracked_text = SCRIPT.read_text(encoding="utf-8")
    matches = ENGINE.KANA_OR_HAN_RE.findall(tracked_text)
    if matches:
        raise RuntimeError(
            f"segment {SEGMENT} tracked builder contains source text"
        )


def assert_queue_contract(prepared: Any) -> None:
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
    if (
        len(rows) != 127
        or len(visible) != 200
        or hidden != QUEUE_HIDDEN_COORDINATES
        or visible[QUEUE_START:QUEUE_STOP] != TARGET_COORDINATES
        or canonical_sha256(TARGET_COORDINATES)
        != EXPECTED_COORDINATE_SHA256
        or rows[0]["record_coordinate"] != "0:2677"
        or rows[-1]["record_coordinate"] != "2:130"
        or rows[58]["record_coordinate"] != "1:9"
        or rows[79]["record_coordinate"] != "1:30"
        or rows[80]["record_coordinate"] != "1:31"
        or rows[81]["record_coordinate"] != "2:85"
        or rows[82]["record_coordinate"] != "2:86"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} private queue contract drifted"
        )


def assert_archive_contracts(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    for label in OWNED_ARCHIVE_DIGESTS:
        records = records_by_label[label]
        if (
            GENERAL.subset_digest(records, OWNED_RECORD_KEYS)
            != OWNED_ARCHIVE_DIGESTS[label]
            or GENERAL.subset_digest(records, BLOCK1_KEYS)
            != BLOCK1_ARCHIVE_DIGESTS[label]
            or GENERAL.subset_digest(records, BLOCK2_CONTEXT_KEYS)
            != BLOCK2_CONTEXT_ARCHIVE_DIGESTS[label]
            or GENERAL.subset_digest(records, VISIBLE_RECORD_KEYS)
            != VISIBLE_RECORD_ARCHIVE_DIGESTS[label]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} archive drifted"
            )
    source_literals = tuple(
        literal_texts(
            records_by_label["pk_jp"],
            tuple(int(value) for value in coordinate.split(":"))[:2],
        )[int(coordinate.rsplit(":", 1)[1])]
        for coordinate in TARGET_COORDINATES
    )
    current_literals = tuple(
        literal_texts(
            records_by_label["pk_current"],
            tuple(int(value) for value in coordinate.split(":"))[:2],
        )[int(coordinate.rsplit(":", 1)[1])]
        for coordinate in TARGET_COORDINATES
    )
    if (
        canonical_sha256(source_literals)
        != EXPECTED_SOURCE_LITERAL_SHA256
        or canonical_sha256(current_literals)
        != EXPECTED_CURRENT_LITERAL_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} visible literal universe drifted"
        )


def assert_shared_record_contract(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> bool:
    source = record_contract(
        records_by_label["pk_jp"],
        SHARED_RECORD_1_9_KEY,
    )
    current = record_contract(
        records_by_label["pk_current"],
        SHARED_RECORD_1_9_KEY,
    )
    if source != (
        SHARED_RECORD_1_9_SOURCE_RAW_SHA256,
        SHARED_RECORD_1_9_SOURCE_LITERALS_SHA256,
        SHARED_RECORD_1_9_SOURCE_GAPS_SHA256,
        SHARED_RECORD_1_9_SOURCE_SIGNATURE_SHA256,
    ) or current != (
        SHARED_RECORD_1_9_CURRENT_RAW_SHA256,
        SHARED_RECORD_1_9_CURRENT_LITERALS_SHA256,
        SHARED_RECORD_1_9_CURRENT_GAPS_SHA256,
        SHARED_RECORD_1_9_CURRENT_SIGNATURE_SHA256,
    ):
        raise RuntimeError(
            f"segment {SEGMENT} shared record contract drifted"
        )

    required = (
        "SHARED_RECORD_1_9_KEY",
        "SHARED_RECORD_1_9_SOURCE_RAW_SHA256",
        "SHARED_RECORD_1_9_CURRENT_RAW_SHA256",
        "SHARED_RECORD_1_9_SOURCE_LITERALS_SHA256",
        "SHARED_RECORD_1_9_CURRENT_LITERALS_SHA256",
        "SHARED_RECORD_1_9_SOURCE_GAPS_SHA256",
        "SHARED_RECORD_1_9_CURRENT_GAPS_SHA256",
        "SHARED_RECORD_1_9_SOURCE_SIGNATURE_SHA256",
        "SHARED_RECORD_1_9_CURRENT_SIGNATURE_SHA256",
    )
    for name in required:
        if globals()[name] != getattr(LEFT_PK, name):
            raise RuntimeError(
                f"segment {SEGMENT} S1045 shared contract drifted: {name}"
            )
    if LEFT_PK.RIGHT_RECORD_1_9_OWNED_LITERAL_IDS != (0, 1):
        raise RuntimeError(
            f"segment {SEGMENT} S1045 ownership contract drifted"
        )
    return True


def assert_block1_non_display(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[str, object]:
    for label in OWNED_ARCHIVE_DIGESTS:
        if sum(
            key[0] == 1 for key in records_by_label[label]
        ) != 32:
            raise RuntimeError(
                f"segment {SEGMENT} {label} block-one size drifted"
            )

    source_sequence = tuple(
        literal_texts(records_by_label["pk_jp"], (1, record_id))
        for record_id in range(9, 31)
    )
    if (
        canonical_sha256(source_sequence)
        != EXPECTED_BLOCK1_LITERAL_SEQUENCE_SHA256
        or literal_sequence_hits(
            records_by_label["pk_jp"],
            source_sequence,
        )
        != ((1, 9),)
        or literal_sequence_hits(
            records_by_label["base_jp"],
            source_sequence,
        )
        != ((1, 9),)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} block-one reverse search drifted"
        )

    mapping_rows: list[tuple[int, int, int, int, int]] = []
    raw_mismatch_expected = set((9, 10, *range(18, 29)))
    for language in ("jp", "current", "sc", "tc"):
        pk_records = records_by_label[f"pk_{language}"]
        base_records = records_by_label[f"base_{language}"]
        raw_mismatch: set[int] = set()
        for record_id in range(9, 31):
            key = (1, record_id)
            if literal_texts(pk_records, key) != literal_texts(
                base_records,
                key,
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {language} Base literal drifted"
                )
            pk_gaps = gap_bytes(pk_records[key])
            base_gaps = gap_bytes(base_records[key])
            if (
                len(pk_gaps) != len(base_gaps)
                or any(
                    normalized_0143_gap(pk_gap)
                    != normalized_0143_gap(base_gap)
                    for pk_gap, base_gap in zip(
                        pk_gaps,
                        base_gaps,
                        strict=True,
                    )
                )
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {language} Base skeleton drifted"
                )
            if pk_records[key].data != base_records[key].data:
                raw_mismatch.add(record_id)
            if language == "jp":
                for gap_id, (pk_gap, base_gap) in enumerate(
                    zip(pk_gaps, base_gaps, strict=True)
                ):
                    pk_matches = list(CONTROL_0143_RE.finditer(pk_gap))
                    base_matches = list(
                        CONTROL_0143_RE.finditer(base_gap)
                    )
                    if [match.start() for match in pk_matches] != [
                        match.start() for match in base_matches
                    ]:
                        raise RuntimeError(
                            f"segment {SEGMENT} 0143 topology drifted"
                        )
                    for pk_match, base_match in zip(
                        pk_matches,
                        base_matches,
                        strict=True,
                    ):
                        mapping_rows.append(
                            (
                                record_id,
                                gap_id,
                                pk_match.start(),
                                struct.unpack(
                                    "<I",
                                    pk_match.group(1),
                                )[0],
                                struct.unpack(
                                    "<I",
                                    base_match.group(1),
                                )[0],
                            )
                        )
        expected = raw_mismatch_expected if language in {
            "jp",
            "current",
        } else set()
        if raw_mismatch != expected:
            raise RuntimeError(
                f"segment {SEGMENT} {language} Base raw delta drifted"
            )
    if (
        len(mapping_rows) != 55
        or canonical_sha256(tuple(mapping_rows))
        != EXPECTED_BLOCK1_0143_MAPPING_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Base 0143 mapping drifted"
        )

    for record_id in range(9, 31):
        if any(
            literal
            for literal in literal_texts(
                records_by_label["pk_en"],
                (1, record_id),
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} English test skeleton drifted"
            )

    jump_rows_by_label: dict[str, tuple[tuple[int, ...], ...]] = {}
    for label in OWNED_ARCHIVE_DIGESTS:
        rows = block1_jump_rows(records_by_label[label])
        jump_rows_by_label[label] = rows
        if (
            len(rows) != 2
            or canonical_sha256(rows)
            != EXPECTED_BLOCK1_JUMP_SHA256
            or {row[4] for row in rows} != {10002, 10031}
            or any(9 <= row[4] <= 31 for row in rows)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} block-one graph drifted"
            )
    if len(set(jump_rows_by_label.values())) != 1:
        raise RuntimeError(
            f"segment {SEGMENT} multilingual jump graph diverged"
        )

    skeleton = multilingual_skeleton(records_by_label)
    if (
        canonical_sha256(skeleton)
        != EXPECTED_MULTILINGUAL_SKELETON_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} multilingual test skeleton drifted"
        )

    if (
        not BASE_TEST_DECISIONS.is_file()
        or hashlib.sha256(
            BASE_TEST_DECISIONS.read_bytes()
        ).hexdigest().upper()
        != BASE_TEST_DECISION_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Base test decision evidence drifted"
        )
    ENGINE.validate_decisions(
        prepared,
        BASE_TEST_DECISIONS,
        require_complete=False,
    )
    base_rows = {
        row["coordinate"]: row
        for row in (
            json.loads(line)
            for line in BASE_TEST_DECISIONS.read_text(
                encoding="utf-8"
            ).splitlines()
            if line
        )
    }
    base_relevant = tuple(
        f"1:{record_id}:{literal_id}"
        for record_id in range(9, 31)
        for literal_id in range(BLOCK1_LITERAL_COUNTS[record_id])
    )
    if (
        len(base_rows) != 71
        or len(base_relevant) != 68
        or any(
            coordinate not in base_rows
            or base_rows[coordinate]["scope_classification"]
            != "confirmed_non_display"
            or base_rows[coordinate]["runtime_review"]
            != "not_required"
            for coordinate in base_relevant
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Base corroboration drifted"
        )
    return {
        "block_record_count": 32,
        "owned_non_display_literal_count": len(
            NON_DISPLAY_COORDINATES
        ),
        "internal_jump_count": 2,
        "owned_internal_incoming_jump_count": 0,
        "multilingual_skeleton_sha256":
        EXPECTED_MULTILINGUAL_SKELETON_SHA256,
        "base_test_decision_sha256": BASE_TEST_DECISION_SHA256,
        "base_corroborating_literal_count": len(base_relevant),
    }


def assert_hidden_records(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    rows = tuple(
        (
            label,
            key,
            hashlib.sha256(
                records_by_label[label][key].data
            ).hexdigest().upper(),
        )
        for label in OWNED_ARCHIVE_DIGESTS
        for key in HIDDEN_KEYS
    )
    if (
        canonical_sha256(rows) != EXPECTED_HIDDEN_ARCHIVE_SHA256
        or any(
            literal_texts(records_by_label[label], key) != ("",)
            or gap_bytes(records_by_label[label][key])
            != (b"", b"\x05\x05\x05")
            for label in OWNED_ARCHIVE_DIGESTS
            for key in HIDDEN_KEYS
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} hidden separator drifted"
        )


def assert_dialogue(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> int:
    key = RIGHT_RECORD_2_86_KEY
    source_records = records_by_label["pk_jp"]
    current_records = records_by_label["pk_current"]
    source = record_contract(source_records, key)
    current = record_contract(current_records, key)
    if source != (
        RIGHT_RECORD_2_86_SOURCE_RAW_SHA256,
        RIGHT_RECORD_2_86_SOURCE_LITERAL_SHA256,
        RIGHT_RECORD_2_86_GAP_SHA256,
        RIGHT_RECORD_2_86_SOURCE_SIGNATURE_SHA256,
    ) or current != (
        RIGHT_RECORD_2_86_CURRENT_RAW_SHA256,
        RIGHT_RECORD_2_86_CURRENT_LITERAL_SHA256,
        RIGHT_RECORD_2_86_GAP_SHA256,
        RIGHT_RECORD_2_86_CURRENT_SIGNATURE_SHA256,
    ):
        raise RuntimeError(
            f"segment {SEGMENT} dialogue contract drifted"
        )

    source_signature = (
        literal_texts(source_records, key),
        tuple(
            value.hex().upper()
            for value in gap_bytes(source_records[key])
        ),
    )
    if (
        exact_signature_hits(source_records, source_signature)
        != ((2, 86),)
        or exact_signature_hits(
            records_by_label["base_jp"],
            source_signature,
        )
        != ((2, 80),)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} dialogue reverse search drifted"
        )
    for language in ("jp", "sc", "tc"):
        if (
            records_by_label[f"pk_{language}"][key].data
            != records_by_label[f"base_{language}"][(2, 80)].data
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {language} Base context drifted"
            )
    if (
        records_by_label["pk_current"][key].data
        == records_by_label["base_current"][(2, 80)].data
    ):
        raise RuntimeError(
            f"segment {SEGMENT} current Base divergence disappeared"
        )
    if (
        not BASE_DIALOGUE.OUTPUT.is_file()
        or hashlib.sha256(
            BASE_DIALOGUE.OUTPUT.read_bytes()
        ).hexdigest().upper()
        != BASE_DIALOGUE_DECISION_SHA256
        or TRANSLATION
        != BASE_DIALOGUE.TRANSLATIONS["2:80:0"]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} completed Base policy drifted"
        )

    source_text = literal_texts(source_records, key)[0]
    current_text = literal_texts(current_records, key)[0]
    if (
        len(literal_texts(source_records, key)) != 1
        or len(literal_texts(current_records, key)) != 1
        or gap_bytes(source_records[key]) != (b"", b"\x05\x05\x05")
        or gap_bytes(current_records[key]) != (b"", b"\x05\x05\x05")
        or any(
            b"\x01" in gap
            for gap in (
                *gap_bytes(source_records[key]),
                *gap_bytes(current_records[key]),
            )
        )
        or UTIL.layout_signature(source_text)
        != RIGHT_RECORD_2_86_LAYOUT_SIGNATURE
        or UTIL.layout_signature(current_text)
        != RIGHT_RECORD_2_86_LAYOUT_SIGNATURE
        or UTIL.layout_signature(TRANSLATION)
        != RIGHT_RECORD_2_86_LAYOUT_SIGNATURE
        or source_text.count("\n") != 1
        or current_text.count("\n") != 1
        or TRANSLATION.count("\n") != 1
        or ENGINE.protected_signature(TRANSLATION)
        != ENGINE.protected_signature(current_text)
        or ENGINE.KANA_OR_HAN_RE.search(TRANSLATION)
        or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(TRANSLATION)
        or canonical_sha256((TRANSLATION,))
        != EXPECTED_TRANSLATION_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} dialogue policy drifted"
        )
    return 6


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str]:
    resource = prepared.resources["pk_msggame"]
    current = records_by_label["pk_current"]
    replacement_key = (*RIGHT_RECORD_2_86_KEY, 0)
    current_text = literal_texts(
        current,
        RIGHT_RECORD_2_86_KEY,
    )[0]
    candidate = ENGINE.rebuild_packed_with_literals(
        resource.current_blob,
        {replacement_key: TRANSLATION},
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
    for key, record in current.items():
        if (
            key != RIGHT_RECORD_2_86_KEY
            and candidate_records[key].data != record.data
        ):
            raise RuntimeError(
                f"segment {SEGMENT} changed out-of-scope record: {key}"
            )
    if (
        literal_texts(
            candidate_records,
            RIGHT_RECORD_2_86_KEY,
        )
        != (TRANSLATION,)
        or gap_bytes(
            candidate_records[RIGHT_RECORD_2_86_KEY]
        )
        != gap_bytes(current[RIGHT_RECORD_2_86_KEY])
        or ENGINE.rebuild_packed_with_literals(
            candidate,
            {replacement_key: current_text},
        )
        != resource.current_blob
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate overlay drifted"
        )
    return candidate, hashlib.sha256(candidate).hexdigest().upper()


def build_rows() -> tuple[
    Any,
    list[dict[str, object]],
    bytes,
    str,
    bool,
    dict[str, object],
    int,
]:
    assert_tracked_builder_source_redacted()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_queue_contract(prepared)
    records_by_label = archive_records(prepared)
    assert_archive_contracts(records_by_label)
    left_imported = assert_shared_record_contract(records_by_label)
    classification = assert_block1_non_display(
        prepared,
        records_by_label,
    )
    assert_hidden_records(records_by_label)
    base_delta = assert_dialogue(records_by_label)
    candidate, candidate_sha256 = build_candidate(
        prepared,
        records_by_label,
    )

    rows: list[dict[str, object]] = []
    for coordinate in NON_DISPLAY_COORDINATES:
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "pk_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256":
                target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256":
                target["current_ko_utf16le_sha256"],
                "semantic_review": "approved",
                "scope_classification": "confirmed_non_display",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required",
                "basis": CLASSIFICATION_BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "classification_evidence": classification,
            }
        )

    target = prepared.visible_targets[("pk_msggame", 2, 86, 0)]
    rows.append(
        {
            "schema": ENGINE.DECISION_SCHEMA,
            "resource": "pk_msggame",
            "coordinate": DIALOGUE_COORDINATE,
            "source_record_raw_sha256":
            target["source_record_raw_sha256"],
            "current_ko_utf16le_sha256":
            target["current_ko_utf16le_sha256"],
            "translation": TRANSLATION,
            "semantic_review": "approved",
            "scope_classification": "retranslated",
            "layout_review": "unchanged_from_current",
            "runtime_review": "not_required",
            "basis": DIALOGUE_BASIS,
            "historic_korean_used": False,
            "switch_korean_used": False,
            "translation_rationale": (
                "The exact Base/PK pristine-JP match reuses the audited "
                "project glossary term for the standalone ceremony; the "
                "reflective plain register and title remain explicit."
            ),
            "layout_evidence": {
                "line_count": 2,
                "current_line_lengths": [15, 18],
                "replacement_line_lengths": [15, 15],
                "protected_token_count": 0,
                "line_signature_preserved": True,
                "event_dialogue_912px_rule_applied": False,
            },
            "correspondence_evidence": {
                "global_source_signature_unique_in_pk": True,
                "global_source_signature_unique_in_base": True,
                "base_record_id": 80,
                "pk_minus_base_record_delta": base_delta,
                "base_used_as_context_only": True,
                "completed_base_policy_imported": True,
                "base_decision_sha256":
                BASE_DIALOGUE_DECISION_SHA256,
            },
        }
    )
    if (
        len(rows) != 67
        or sum(
            row["scope_classification"] == "confirmed_non_display"
            for row in rows
        )
        != 66
        or sum(
            row["scope_classification"] == "retranslated"
            for row in rows
        )
        != 1
    ):
        raise RuntimeError(
            f"segment {SEGMENT} decision universe drifted"
        )
    return (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        left_imported,
        classification,
        base_delta,
    )


def main() -> int:
    first = build_rows()
    second = build_rows()
    (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        left_imported,
        classification,
        base_delta,
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or left_imported != second[4]
        or classification != second[5]
        or base_delta != second[6]
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
    if (
        len(validated) != 67
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
                "segment": "pk_msggame_B008_S1046",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [67, 133],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "source_literal_count": 67,
                "decision_count": len(rows),
                "confirmed_non_display": 66,
                "retranslated": 1,
                "changed_literal_count": 1,
                "hidden_non_display_record_count": len(HIDDEN_KEYS),
                "block1_classification":
                "internal_grammar_font_test_non_display",
                "block1_record_count":
                classification["block_record_count"],
                "block1_internal_jump_count":
                classification["internal_jump_count"],
                "block1_owned_internal_incoming_jump_count":
                classification[
                    "owned_internal_incoming_jump_count"
                ],
                "block1_multilingual_skeleton_sha256":
                classification["multilingual_skeleton_sha256"],
                "block1_base_corroboration_only": True,
                "block2_record86_classification":
                "real_dialogue_retranslated",
                "block2_record86_base_record": 80,
                "block2_pk_minus_base_delta": base_delta,
                "block2_event_912px_rule_applied": False,
                "s1045_shared_record_import_available":
                left_imported,
                "shared_record_1_9_contract_exported": True,
                "right_record_2_86_contract_exported": True,
                "candidate_sha256": candidate_sha256,
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
                "tracked_builder_source_text_count": 0,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
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
