#!/usr/bin/env python3
"""Build PK block-0 runtime-terminal segment 1034 decisions."""

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

import build_base_batch004_segment1012 as BASE_TAIL
import build_base_batch004_segment1013 as BASE_NEXT
import build_pk_batch001_segment1025 as HELPERS
import build_pk_batch004_segment1033 as LEFT_PK


ENGINE = BASE_TAIL.ENGINE
GENERAL = BASE_TAIL.GENERAL
UTIL = BASE_TAIL.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B004_S1034.private.v1.jsonl"
)
SEGMENT = 1034
QUEUE_BATCH_ID = "pk_msggame-B004"
BLOCK_ID = 0
QUEUE_ZERO_BASED_START = 67
QUEUE_ZERO_BASED_STOP = 134
RECORD_IDS = tuple(range(1935, 2002))
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
TARGET_COORDINATES = tuple(
    f"{BLOCK_ID}:{record_id}:0" for record_id in RECORD_IDS
)
PK_RECORD_COUNT = 21751
QUEUE_HIDDEN_EMPTY_RECORD_IDS = (1888, 1889, 1895, 1897, 1899)

EXPECTED_PK_JP = (
    # Shared left root 550 tail.
    "でござる",
    "じゃ",
    # Root 556.
    "でしょう",
    "だ",
    "でございましょう",
    "にございましょう",
    "でしょう",
    "でござろう",
    "じゃ",
    # Root 562.
    "です",
    "だ",
    "でございます",
    "にございます",
    "です",
    "でござる",
    "だ",
    # Root 568.
    "です",
    "だ",
    "です",
    "です",
    "です",
    "でござる",
    "だ",
    # Root 574.
    "ですが",
    "だが",
    "なれど",
    "されど",
    "ですが",
    "しかし",
    "だが",
    # Root 580.
    "たち",
    "あった",
    "がた",
    "ら",
    "たち",
    "ら",
    "ども",
    # Root 586.
    "でした",
    "だった",
    "でございました",
    "でございました",
    "でした",
    "でござった",
    "であった",
    # Root 592.
    "でした",
    "だった",
    "でした",
    "でした",
    "でした",
    "でござった",
    "であった",
    # Root 598.
    "ですね",
    "だな",
    "でございますね",
    "でございますな",
    "ですね",
    "ですな",
    "だな",
    # Root 604.
    "ですね",
    "だな",
    "ですね",
    "ですな",
    "ですね",
    "ですな",
    "だな",
    # Shared right root 610 head.
    "でしょう",
    "であろう",
)

TRANSLATION_POLICY = (
    "이오",
    "이니라",
    "이겠지요",
    "다",
    "이겠사옵니다",
    "이겠사옵니다",
    "이겠지요",
    "이리다",
    "이니라",
    "입니다",
    "다",
    "이옵니다",
    "이옵니다",
    "입니다",
    "이오",
    "다",
    "입니다",
    "다",
    "입니다",
    "입니다",
    "입니다",
    "이오",
    "다",
    "입니다만",
    "하지만",
    "허나",
    "그러나",
    "입니다만",
    "그러나",
    "하지만",
    "들",
    "있었다",
    "분들",
    "들",
    "들",
    "들",
    "들",
    "였습니다",
    "였다",
    "였사옵니다",
    "였사옵니다",
    "였습니다",
    "였소",
    "였다",
    "였습니다",
    "였다",
    "였습니다",
    "였습니다",
    "였습니다",
    "였소",
    "였다",
    "이지요",
    "이군",
    "이옵지요",
    "이옵니다그려",
    "이지요",
    "이군요",
    "이군",
    "이지요",
    "이군",
    "이지요",
    "이군요",
    "이지요",
    "이군요",
    "이군",
    "이겠지요",
    "이리라",
)
TRANSLATIONS_BY_RECORD = dict(
    zip(RECORD_IDS, TRANSLATION_POLICY, strict=True)
)
TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}

# These roots and terminal groups are asserted after an exhaustive closure
# search; they are not used to discover the Base mapping.
FULL_PK_GROUPS = {
    550: tuple(range(1930, 1937)),
    556: tuple(range(1937, 1944)),
    562: tuple(range(1944, 1951)),
    568: tuple(range(1951, 1958)),
    574: tuple(range(1958, 1965)),
    580: tuple(range(1965, 1972)),
    586: tuple(range(1972, 1979)),
    592: tuple(range(1979, 1986)),
    598: tuple(range(1986, 1993)),
    604: tuple(range(1993, 2000)),
    610: tuple(range(2000, 2007)),
}
EXPECTED_ROOT_CLOSURES = {
    root: tuple(range(root, root + 6)) + record_ids
    for root, record_ids in FULL_PK_GROUPS.items()
}
EXPECTED_SUBROOT_CLOSURES = {
    569: (569, 1951, 1952),
}
RECORD_TO_ROOT = {
    record_id: root
    for root, record_ids in FULL_PK_GROUPS.items()
    for record_id in record_ids
    if record_id in RECORD_IDS
}
ROOT_ASSEMBLY_PLAN = {
    550: "caller nominal predicate normalized before copular ending",
    556: "caller nominal predicate normalized before conjectural ending",
    562: "caller nominal predicate normalized before copular ending",
    568: "caller nominal predicate normalized before copular ending",
    574: "caller nominal predicate normalized before connective ending",
    580: "caller person noun normalized before plural ending",
    586: "caller nominal predicate normalized before honorific past copula",
    592: "caller nominal predicate normalized before past copula",
    598: "caller nominal predicate normalized before confirmation ending",
    604: "caller nominal predicate normalized before confirmation ending",
    610: "caller nominal predicate normalized before conjectural ending",
}

LEFT_ROOT550_FULL_IDS = tuple(range(1930, 1937))
LEFT_ROOT550_FULL_JP = (
    "です",
    "だ",
    "でございます",
    "にございます",
    "です",
    "でござる",
    "じゃ",
)
LEFT_ROOT550_FULL_CURRENT = (
    "입니다",
    "다",
    "이옵니다",
    "이옵니다",
    "입니다",
    "이오",
    "이니라",
)
LEFT_ROOT550_FULL_POLICY = LEFT_ROOT550_FULL_CURRENT

RIGHT_ROOT610_FULL_IDS = tuple(range(2000, 2007))
RIGHT_ROOT610_FULL_JP = (
    "でしょう",
    "であろう",
    "でしょう",
    "でしょう",
    "でしょう",
    "でしょう",
    "だろう",
)
RIGHT_ROOT610_FULL_CURRENT = (
    "이겠지요",
    "이리라",
    "이겠지요",
    "이겠지요",
    "이겠지요",
    "이겠지요",
    "이겠지",
)
RIGHT_ROOT610_FULL_POLICY = RIGHT_ROOT610_FULL_CURRENT

EXPECTED_SEQUENCE_EVIDENCE = {
    "full67": (
        1935,
        67,
        (1867,),
        (1935,),
        "81316C370682876EDD2F5BA3B1B9F66A054E8AFDA584CB1D55B83592B61BAB26",
    ),
    "tail14": (
        1935,
        14,
        (1867,),
        (1935,),
        "5BB996482FDDF0C4146A0E57D5554FD6E5DC28686FC1D6E392C95750596C2DBE",
    ),
    "next53": (
        1949,
        53,
        (1881,),
        (1949,),
        "5345B78251E8545357B64F475B0448CC14FD6C16FF2E52295FA19401C511A54A",
    ),
}
EXPECTED_MAPPING_SHA256 = (
    "1576BFA8F4F9D744C0F869EDEEDBEF2F02D92CB0B46A7EEC434964C59D630800"
)
EXPECTED_POLICY_SHA256 = (
    "28C435E2BFA07A44F612511A82714FE186924F25C5FA841809AACA449C9D27BC"
)
EXPECTED_CHANGED_LITERAL_COUNT = 5

PK_TARGET_ARCHIVE_DIGESTS = {
    "pk_jp": "5A37069F29D7A604EAD93BA187975794D3F96ADDEFBD9655FF09BD3AD9C5B3F4",
    "pk_current": "1318DB6FCF617EED70DB917F207E5F250E7EE68A1B50D8BA34A401FA9D8867A4",
    "pk_sc": "9D13A1C1BBA0EE1F116EDDE4F2AD140F04182EE0CF3B89B0EF71DE64D2F3D3AE",
    "pk_tc": "9D13A1C1BBA0EE1F116EDDE4F2AD140F04182EE0CF3B89B0EF71DE64D2F3D3AE",
    "pk_en": "9D13A1C1BBA0EE1F116EDDE4F2AD140F04182EE0CF3B89B0EF71DE64D2F3D3AE",
}
PK_FULL_ARCHIVE_DIGESTS = {
    "pk_jp": "48D3B84E710CEA1DE6780E6E999E7A33558013DC17EC079D0348EDE5A8FF2B86",
    "pk_current": "EDB7AA0CA61A96CA72D3E142035651073FB158A7FC4C41A5B4395B78B9B33158",
    "pk_sc": "FD73CA56051B58C8C9CB2613475AF72C486A50CF1CF327FD30D9D214A6E28A7D",
    "pk_tc": "FD73CA56051B58C8C9CB2613475AF72C486A50CF1CF327FD30D9D214A6E28A7D",
    "pk_en": "FD73CA56051B58C8C9CB2613475AF72C486A50CF1CF327FD30D9D214A6E28A7D",
}
EXPECTED_EDGE_EVIDENCE = {
    "target": (
        67,
        "BE78625564C3790B7506423F3BF20387530B9AACB9035F47F7253BD0C5121A1C",
    ),
    "full": (
        77,
        "FF2F5DFAAD575F826EF0C082999B0F0CF131E8B53D06CADAED96A90F088CB703",
    ),
}
EMPTY_CANONICAL_SHA256 = (
    "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
)
EXPECTED_CALL_EVIDENCE = {
    550: (
        (177, "C09E1E720591004E18605570B5F72C14E16C2319545ED73A431C9F0279AFFF81", 25, "8FC0F951532CDB6FE34EBB50C3E2BA9B32CEBCDDE0682066CFC3E73E843024E8"),
        (169, "7E968264996B6C9117AB8D8D206B9F8AB267AD648063C87F57DD7EF0E53146C1", 24, "25459FA80B093303165E6A8C6BE75D1033679FBA4DC2840CD5ADFE0D296115F8"),
        (8, "25DCAAB071AE688936645475BCE57DF172918488A0E2D853B8E1A853EFE44068", 0, EMPTY_CANONICAL_SHA256),
    ),
    556: (
        (7, "4D935BAA45A9E12716FB318492CE4E78618BB273E2642AA78F593B08D51EA9F0", 1, "D027098328CAF662120C32BEB094D067BBB20620484B6414DD2B3CDBD58497C4"),
        (7, "4D935BAA45A9E12716FB318492CE4E78618BB273E2642AA78F593B08D51EA9F0", 1, "D027098328CAF662120C32BEB094D067BBB20620484B6414DD2B3CDBD58497C4"),
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
    ),
    562: (
        (60, "10E154CF159868390C12D390FAACFF31CD344131DD587E20C7DBE27EC08CFA93", 17, "96C23E3412539BF0842836D0C78039D8E2EBE3E318B573F82F3FF53F93691685"),
        (54, "4239C3225322B800E2E6ABD1F3D7A774E67B147F5D5B24EA8F21F073D23869AA", 14, "587451590D87135AFCC5BE5ABA461A036E06275939437DC974D909D9171E3619"),
        (6, "D514C2EF89DA90E89261050CEFEEE09EB8FC4B3755333C3FE21D919148FA36A8", 0, EMPTY_CANONICAL_SHA256),
    ),
    568: (
        (231, "09099F3A5054AF258142A668D114BC4FF615226780CFB99FCFF39D2FF2F1305D", 55, "5FADADB66C6F03A00579D9EE8035D404F25A5E213EADE41C66058B82ACD43950"),
        (222, "484B65A42455B0589128208D96AC8DE470B492CE7A80D84BD0F4F6DBF5F56229", 54, "67ADC3607825BDFA534A72EAE94BC1A1939B20145746CAE4BFA37D69F8408D67"),
        (9, "D0D16D30D16503BF259BD4609F64BBB3531192375BE38C503DBE11681B813B63", 0, EMPTY_CANONICAL_SHA256),
    ),
    569: (
        (1, "3E0F998160BF7DD02FF87F3B3E450994C12AC88DEB726596AFC16580CAD89AD2", 0, EMPTY_CANONICAL_SHA256),
        (1, "3E0F998160BF7DD02FF87F3B3E450994C12AC88DEB726596AFC16580CAD89AD2", 0, EMPTY_CANONICAL_SHA256),
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
    ),
    574: (
        (7, "C2553B5B0648618C47E25CBA3225A14B1A2F23687F61F17A2AB754BF86F5ABCA", 2, "02C00E54E0B35B00852F8AB9287EE91A813D6E03AC8EF3476C466F13D346DDCF"),
        (7, "C2553B5B0648618C47E25CBA3225A14B1A2F23687F61F17A2AB754BF86F5ABCA", 2, "02C00E54E0B35B00852F8AB9287EE91A813D6E03AC8EF3476C466F13D346DDCF"),
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
    ),
    580: (
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
    ),
    586: (
        (15, "B9E4E3A6C2F7734A257CDDE67DCC405D745E9BCAB5DD0C37019F3FAC63F67A78", 0, EMPTY_CANONICAL_SHA256),
        (6, "9CB82F7335415DD2C4C1E165AED1D856D0DE5FC5C73586B3DCE95F69BF7E6009", 0, EMPTY_CANONICAL_SHA256),
        (9, "C54177370D333423714F4E7061CBBF8252117CD3DC02CDD5640605F9E08BA61E", 0, EMPTY_CANONICAL_SHA256),
    ),
    592: (
        (7, "8785E9558550D67ECB8C36C4CE74C2CCA9558086D3FD90DF6BE40A93862C4A92", 1, "8C697AB3DC09106507A4965F9614117B988ACACD705F863E5B126351361674FA"),
        (7, "8785E9558550D67ECB8C36C4CE74C2CCA9558086D3FD90DF6BE40A93862C4A92", 1, "8C697AB3DC09106507A4965F9614117B988ACACD705F863E5B126351361674FA"),
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
    ),
    598: (
        (43, "D10E530F1832E481A8E3443897F09D067CCD817B80D29BBD66ABA231EFF8D4B2", 0, EMPTY_CANONICAL_SHA256),
        (40, "8835BE6C4210684798F699D79820CABF31C3B935CECB677C75F964BD79300BA5", 0, EMPTY_CANONICAL_SHA256),
        (3, "DC235AD5FE34791A017651B7DDE5FA3FBF9AC8885E2747AA96FAB9BEDEE46131", 0, EMPTY_CANONICAL_SHA256),
    ),
    604: (
        (21, "39CA085E3D99EEFFCDB48BF6A0F4355EFC24BF326BE5E97879EE7438207C2F88", 0, EMPTY_CANONICAL_SHA256),
        (21, "39CA085E3D99EEFFCDB48BF6A0F4355EFC24BF326BE5E97879EE7438207C2F88", 1, "6804365B95703799363C4E92C16281DD17671D6F5D7FEB53E268B79A78A7E9BE"),
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
    ),
    610: (
        (243, "D9F3A25D6A1C549FDD7C6EA4867B4A7BF6D5DF481E15FEF4C1B86370ECFFD979", 38, "67370DF600EECEDFAD8A56AE3B7FB5EE3A0CE97DE8C7733417D98CDCC024C7CA"),
        (230, "EC90CC9063A24D263E0ABA8C68E220D2C08AB5722353D379A3F0B34111F2FBBE", 34, "C926BEA334757D397F2A00DEBD6DF00D4125B42AED182B9FF8770A347744B785"),
        (13, "4893F860A35A7A810B9D2DCDF2F5584DFDC3A3B955DF0CAC9A25DA2EABE3DB06", 0, EMPTY_CANONICAL_SHA256),
    ),
}
MORPHOLOGY_014C_RE = re.compile(b"\x01\x4C(.{4})", re.DOTALL)
EXPECTED_014C_OVERLAP = ((15, 25, 0, 65, 84213762),)

BASIS = (
    "review_queue_pk_msggame_B004_zero_based_visible_ordinals67_133_"
    "pristine_pk_pc_jp_sole_translation_authority_block0_records1935_"
    "2001_67_visible_no_hidden_independent_global_exact67_and_partition_"
    "tail14_Base1867_next53_Base1881_reverse_search_same_pk_hits_offset_"
    "plus68_discovered_not_assumed_exact_jp_current_sc_tc_skeleton_blank_"
    "en_context_actual_014a_exhaustive_full_root_and_live_subroot569_"
    "closures_0143_fixed_flatten_014c_guards_left_root550_cross_S1033_"
    "right_root610_cross_S1035_actual_full_shared_group_copular_"
    "connective_plural_past_confirmation_conjectural_register_matrices_"
    "runtime_caller_rewrite_pending_no_historic_or_switch_korean_"
    "authority_one_line_skeleton_outside_reverse_two_run_no_steam"
)


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return tuple(
        literal.text for literal in ENGINE.parse_record_literals(records[key])
    )


def gap_bytes(record: Any) -> tuple[bytes, ...]:
    return HELPERS.record_gaps(record)


def archive_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    return BASE_TAIL.archive_records(prepared)


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
    signature: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...],
) -> tuple[int, ...]:
    count = len(signature)
    maximum = max(
        record_id
        for block_id, record_id in records
        if block_id == BLOCK_ID
    )
    return tuple(
        start
        for start in range(maximum - count + 2)
        if all(
            (BLOCK_ID, start + ordinal) in records
            for ordinal in range(count)
        )
        and record_signature(records, start, count) == signature
    )


def assert_queue_contract(prepared: Any) -> None:
    rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line
    ]
    batch_targets = [
        target
        for row in rows
        if row.get("batch_id") == QUEUE_BATCH_ID
        for target in row["target_literals"]
    ]
    visible = tuple(
        target["coordinate"]
        for target in batch_targets
        if target.get("visible")
    )
    hidden = tuple(
        target["coordinate"]
        for target in batch_targets
        if not target.get("visible")
    )
    if (
        len([row for row in rows if row.get("batch_id") == QUEUE_BATCH_ID])
        != 205
        or len(visible) != 200
        or visible[
            QUEUE_ZERO_BASED_START:QUEUE_ZERO_BASED_STOP
        ]
        != TARGET_COORDINATES
        or hidden
        != tuple(
            f"{BLOCK_ID}:{record_id}:0"
            for record_id in QUEUE_HIDDEN_EMPTY_RECORD_IDS
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} private queue ordinal contract drifted"
        )


def discover_mapping(
    base_jp: dict[tuple[int, int], Any],
    pk_jp: dict[tuple[int, int], Any],
) -> dict[int, int]:
    observed: dict[str, tuple[Any, ...]] = {}
    for label, expected in EXPECTED_SEQUENCE_EVIDENCE.items():
        pk_start, count, _, _, _ = expected
        signature = record_signature(pk_jp, pk_start, count)
        observed[label] = (
            pk_start,
            count,
            sequence_starts(base_jp, signature),
            sequence_starts(pk_jp, signature),
            HELPERS.canonical_sha256(signature),
        )
    if observed != EXPECTED_SEQUENCE_EVIDENCE:
        raise RuntimeError(
            f"segment {SEGMENT} independent global/partition "
            f"reverse search drifted: {observed}"
        )

    full_base_start = observed["full67"][2][0]
    mapping = {
        pk_record_id: full_base_start + ordinal
        for ordinal, pk_record_id in enumerate(RECORD_IDS)
    }
    if (
        tuple(mapping.values()) != tuple(range(1867, 1934))
        or HELPERS.canonical_sha256(
            [[pk_record_id, base_record_id]
             for pk_record_id, base_record_id in mapping.items()]
        )
        != EXPECTED_MAPPING_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} reverse map drifted")
    return mapping


def assert_sources_and_mapping(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    mapping: dict[int, int],
) -> None:
    full_keys = tuple((BLOCK_ID, record_id) for record_id in range(1930, 2007))
    for scope, keys, digests in (
        ("target", RECORD_KEYS, PK_TARGET_ARCHIVE_DIGESTS),
        ("full", full_keys, PK_FULL_ARCHIVE_DIGESTS),
    ):
        for label, expected_digest in digests.items():
            actual_digest = GENERAL.subset_digest(
                records_by_label[label],
                keys,
            )
            if actual_digest != expected_digest:
                raise RuntimeError(
                    f"segment {SEGMENT} {scope} {label} digest drifted"
                )

    for ordinal, (pk_record_id, base_record_id) in enumerate(
        mapping.items()
    ):
        pk_key = (BLOCK_ID, pk_record_id)
        base_key = (BLOCK_ID, base_record_id)
        if literal_texts(records_by_label["pk_jp"], pk_key) != (
            EXPECTED_PK_JP[ordinal],
        ):
            raise RuntimeError(
                f"segment {SEGMENT} pristine PK source drifted: {pk_key}"
            )
        for label in ("pk_jp", "pk_current", "pk_sc", "pk_tc", "pk_en"):
            if (
                len(literal_texts(records_by_label[label], pk_key)) != 1
                or gap_bytes(records_by_label[label][pk_key])
                != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} PK skeleton drifted: "
                    f"{label}/{pk_key}"
                )
        for label in ("pk_sc", "pk_tc", "pk_en"):
            if literal_texts(records_by_label[label], pk_key) != ("",):
                raise RuntimeError(
                    f"segment {SEGMENT} context drifted: {label}/{pk_key}"
                )
        for language in ("jp", "current", "sc", "tc"):
            if (
                records_by_label[f"pk_{language}"][pk_key].data
                != records_by_label[f"base_{language}"][base_key].data
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} exact Base/PK {language} "
                    f"mapping drifted: {base_key}/{pk_key}"
                )


def incoming_jump_rows(
    records: dict[tuple[int, int], Any],
    target_ids: set[int],
) -> tuple[tuple[int, int, int, int, int], ...]:
    rows: list[tuple[int, int, int, int, int]] = []
    for (block_id, record_id), record in sorted(records.items()):
        for gap_id, gap in enumerate(gap_bytes(record)):
            for match in BASE_TAIL.GRAPH.MORPHOLOGY_JUMP_RE.finditer(gap):
                operand = struct.unpack("<I", match.group(1))[0]
                if operand in target_ids:
                    rows.append(
                        (
                            block_id,
                            record_id,
                            gap_id,
                            match.start(),
                            operand,
                        )
                    )
    return tuple(rows)


def discover_root_closures(
    records: dict[tuple[int, int], Any],
) -> tuple[dict[int, tuple[int, ...]], dict[int, tuple[int, ...]]]:
    graph = HELPERS.graph_edges(records)
    closure_cache = {
        node: HELPERS.graph_closure(graph, node)
        for node in graph
    }
    full: dict[int, tuple[int, ...]] = {}
    for expected_root, terminal_ids in FULL_PK_GROUPS.items():
        terminal_set = set(terminal_ids)
        hits = tuple(
            sorted(
                (
                    node,
                    tuple(sorted(closure)),
                )
                for node, closure in closure_cache.items()
                if len(closure) == 13 and terminal_set.issubset(closure)
            )
        )
        expected = (
            (expected_root, EXPECTED_ROOT_CLOSURES[expected_root]),
        )
        if hits != expected:
            raise RuntimeError(
                f"segment {SEGMENT} exhaustive root discovery "
                f"drifted: {terminal_ids}/{hits}"
            )
        full[expected_root] = hits[0][1]

    subroots: dict[int, tuple[int, ...]] = {}
    full_root568 = set(full[568])
    for node in sorted(full_root568):
        if node == 568:
            continue
        closure = closure_cache.get(
            node,
            HELPERS.graph_closure(graph, node),
        )
        if (
            len(closure) > 1
            and closure < full_root568
            and HELPERS.root_call_sites(records, node)
        ):
            subroots[node] = tuple(sorted(closure))
    if subroots != EXPECTED_SUBROOT_CLOSURES:
        raise RuntimeError(
            f"segment {SEGMENT} live subroot discovery drifted: "
            f"{subroots}"
        )
    return full, subroots


def assert_runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    for label in ("pk_jp", "pk_current"):
        records = records_by_label[label]
        full, subroots = discover_root_closures(records)
        if full != EXPECTED_ROOT_CLOSURES or subroots != EXPECTED_SUBROOT_CLOSURES:
            raise RuntimeError(
                f"segment {SEGMENT} {label} closure drifted"
            )
        for scope, target_ids in (
            ("target", set(RECORD_IDS)),
            ("full", set(range(1930, 2007))),
        ):
            rows = incoming_jump_rows(records, target_ids)
            actual = (len(rows), HELPERS.canonical_sha256(rows))
            if actual != EXPECTED_EDGE_EVIDENCE[scope]:
                raise RuntimeError(
                    f"segment {SEGMENT} {label} {scope} 014A drifted"
                )

    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    for root, expected in EXPECTED_CALL_EVIDENCE.items():
        source_calls = HELPERS.root_call_sites(source, root)
        current_calls = HELPERS.root_call_sites(current, root)
        source_fixed = HELPERS.fixed_following_blockers(source, root)
        current_fixed = HELPERS.fixed_following_blockers(current, root)
        source_only = tuple(sorted(set(source_calls) - set(current_calls)))
        current_only = tuple(sorted(set(current_calls) - set(source_calls)))
        actual = (
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
        if actual != expected:
            raise RuntimeError(
                f"segment {SEGMENT} root {root} "
                "0143/fixed/flatten evidence drifted"
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
                        BASE_TAIL.GRAPH.MORPHOLOGY_JUMP_RE.finditer(gap)
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
                    if any(match.start() in span for span in jump_spans):
                        overlapped.append(row)
                    else:
                        valid.append(row)
        if valid or tuple(overlapped) != EXPECTED_014C_OVERLAP:
            raise RuntimeError(
                f"segment {SEGMENT} {label} 014C evidence drifted"
            )

    # Completed Base audits are auxiliary cross-checks only, reached after
    # the pristine PK source and runtime evidence have independently passed.
    BASE_TAIL.assert_corpora(records_by_label)
    BASE_TAIL.assert_runtime_graph(records_by_label)
    BASE_TAIL.assert_fixed_following(records_by_label)
    BASE_NEXT.assert_corpora(records_by_label)
    BASE_NEXT.assert_runtime_graph(records_by_label)


def assert_boundaries(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    actual_left_jp = tuple(
        literal_texts(source, (BLOCK_ID, record_id))[0]
        for record_id in LEFT_ROOT550_FULL_IDS
    )
    actual_left_current = tuple(
        literal_texts(current, (BLOCK_ID, record_id))[0]
        for record_id in LEFT_ROOT550_FULL_IDS
    )
    if (
        actual_left_jp != LEFT_ROOT550_FULL_JP
        or actual_left_current != LEFT_ROOT550_FULL_CURRENT
        or LEFT_ROOT550_FULL_IDS != LEFT_PK.RIGHT_ROOT550_FULL_IDS
        or LEFT_ROOT550_FULL_JP != LEFT_PK.RIGHT_ROOT550_FULL_JP
        or LEFT_ROOT550_FULL_CURRENT
        != LEFT_PK.RIGHT_ROOT550_FULL_CURRENT
        or LEFT_ROOT550_FULL_POLICY
        != LEFT_PK.RIGHT_ROOT550_FULL_POLICY
        or tuple(
            TRANSLATIONS_BY_RECORD[record_id]
            for record_id in (1935, 1936)
        )
        != LEFT_ROOT550_FULL_POLICY[5:]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} S1033/S1034 root550 boundary drifted"
        )

    actual_right_jp = tuple(
        literal_texts(source, (BLOCK_ID, record_id))[0]
        for record_id in RIGHT_ROOT610_FULL_IDS
    )
    actual_right_current = tuple(
        literal_texts(current, (BLOCK_ID, record_id))[0]
        for record_id in RIGHT_ROOT610_FULL_IDS
    )
    auxiliary_right_policy = tuple(
        BASE_NEXT.FULL_TRANSLATION_POLICY[record_id]
        for record_id in range(1932, 1939)
    )
    if (
        actual_right_jp != RIGHT_ROOT610_FULL_JP
        or actual_right_current != RIGHT_ROOT610_FULL_CURRENT
        or auxiliary_right_policy != RIGHT_ROOT610_FULL_POLICY
        or tuple(
            TRANSLATIONS_BY_RECORD[record_id]
            for record_id in (2000, 2001)
        )
        != RIGHT_ROOT610_FULL_POLICY[:2]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} S1034/S1035 root610 boundary drifted"
        )


def assert_semantics(
    mapping: dict[int, int],
    translations: dict[str, str],
) -> None:
    policy_rows = [
        [
            record_id,
            EXPECTED_PK_JP[ordinal],
            TRANSLATION_POLICY[ordinal],
        ]
        for ordinal, record_id in enumerate(RECORD_IDS)
    ]
    if (
        len(EXPECTED_PK_JP) != 67
        or len(TRANSLATION_POLICY) != 67
        or set(RECORD_TO_ROOT) != set(RECORD_IDS)
        or translations != TRANSLATIONS
        or HELPERS.canonical_sha256(policy_rows)
        != EXPECTED_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} independent semantic policy drifted"
        )

    auxiliary_policy = {
        pk_record_id: (
            BASE_TAIL.FULL_TRANSLATION_POLICY[base_record_id]
            if base_record_id <= 1880
            else BASE_NEXT.FULL_TRANSLATION_POLICY[base_record_id]
        )
        for pk_record_id, base_record_id in mapping.items()
    }
    if auxiliary_policy != TRANSLATIONS_BY_RECORD:
        raise RuntimeError(
            f"segment {SEGMENT} auxiliary Base policy drifted"
        )
    BASE_TAIL.assert_semantics(BASE_TAIL.RAW_TRANSLATIONS)
    BASE_NEXT.assert_semantics(BASE_NEXT.TRANSLATIONS)

    if (
        TRANSLATIONS_BY_RECORD[1940] != "이겠사옵니다"
        or TRANSLATIONS_BY_RECORD[1967] != "분들"
        or TRANSLATIONS_BY_RECORD[1974] != "였사옵니다"
        or TRANSLATIONS_BY_RECORD[1988] != "이옵지요"
        or TRANSLATIONS_BY_RECORD[2001] != "이리라"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} register or morphology policy drifted"
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
        or set(replacements)
        != {(BLOCK_ID, record_id, 0) for record_id in RECORD_IDS}
    ):
        raise RuntimeError(f"segment {SEGMENT} candidate universe drifted")
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
    reversed_blob = ENGINE.rebuild_packed_with_literals(candidate, reverse)
    if reversed_blob != pk.current_blob:
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
]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_queue_contract(prepared)
    records_by_label = archive_records(prepared)
    mapping = discover_mapping(
        records_by_label["base_jp"],
        records_by_label["pk_jp"],
    )
    assert_sources_and_mapping(records_by_label, mapping)
    assert_runtime_evidence(records_by_label)
    assert_boundaries(records_by_label)
    translations = dict(TRANSLATIONS)
    assert_semantics(mapping, translations)

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
        ):
            raise RuntimeError(
                f"segment {SEGMENT} protected text drifted: {coordinate}"
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
        base_record_id = mapping[record_id]
        root = RECORD_TO_ROOT[record_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        evidence: dict[str, object] = {
            "automatic_space_inserted": False,
            "leading_trailing_space_protected": True,
            "pk_record_id": record_id,
            "base_semantic_record_id": base_record_id,
            "base_mapping_method": (
                "unique_global_exact67_confirmed_by_unique_tail14_"
                "and_next53_partition_searches"
            ),
            "root": root,
            "full_terminal_record_ids": list(FULL_PK_GROUPS[root]),
            "full_graph_closure_record_ids": list(
                EXPECTED_ROOT_CLOSURES[root]
            ),
            "pk_source_call_count": EXPECTED_CALL_EVIDENCE[root][0][0],
            "pk_current_call_count": EXPECTED_CALL_EVIDENCE[root][1][0],
            "pk_source_fixed_following_count": (
                EXPECTED_CALL_EVIDENCE[root][0][2]
            ),
            "pk_current_fixed_following_count": (
                EXPECTED_CALL_EVIDENCE[root][1][2]
            ),
            "pk_source_calls_flattened_in_current": (
                EXPECTED_CALL_EVIDENCE[root][2][0]
            ),
            "pk_current_only_calls": (
                EXPECTED_CALL_EVIDENCE[root][2][2]
            ),
            "incoming_jump_graph_guarded": True,
            "valid_incoming_014c_count": 0,
            "assembly_plan": ROOT_ASSEMBLY_PLAN[root],
            "runtime_integration_required": True,
        }
        if record_id in (1951, 1952):
            evidence["live_subroot"] = {
                "root": 569,
                "closure_record_ids": list(
                    EXPECTED_SUBROOT_CLOSURES[569]
                ),
                "pk_source_call_count": (
                    EXPECTED_CALL_EVIDENCE[569][0][0]
                ),
                "pk_current_call_count": (
                    EXPECTED_CALL_EVIDENCE[569][1][0]
                ),
            }
        if record_id in (1935, 1936):
            evidence["shared_left_root_with_segment"] = 1033
        if record_id in (2000, 2001):
            evidence["shared_right_root_with_segment"] = 1035
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
                "runtime_assembly_evidence": evidence,
            }
        )
    return prepared, translations, rows, candidate, candidate_sha256


def main() -> int:
    first = build_rows()
    second = build_rows()
    prepared, translations, rows, candidate, candidate_sha256 = first
    if (
        translations != second[1]
        or rows != second[2]
        or candidate != second[3]
        or candidate_sha256 != second[4]
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
            (BLOCK_ID, int(coordinate.split(":")[1])),
        )[0]
        for coordinate, translation in translations.items()
    )
    if changed != EXPECTED_CHANGED_LITERAL_COUNT:
        raise RuntimeError(
            f"segment {SEGMENT} changed literal count drifted: {changed}"
        )

    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B004_S1034",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [67, 133],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "source_literal_count": 67,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "confirmed_non_display": 0,
                "changed_literal_count": changed,
                "base_mapping_method": (
                    "unique_global_exact67_plus_unique_tail14_next53"
                ),
                "discovered_base_record_ranges": [
                    [1867, 1880],
                    [1881, 1933],
                ],
                "discovered_pk_minus_base_offset": 68,
                "base_reverse_map_sha256": EXPECTED_MAPPING_SHA256,
                "translation_policy_sha256": EXPECTED_POLICY_SHA256,
                "pk_call_fixed_flatten_evidence": EXPECTED_CALL_EVIDENCE,
                "left_shared_root550_full_record_ids": list(
                    LEFT_ROOT550_FULL_IDS
                ),
                "right_shared_root610_full_record_ids": list(
                    RIGHT_ROOT610_FULL_IDS
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
                "s1033_boundary_cross_assert_exact": True,
                "right_shared_root610_actual_closure_exact": True,
                "second_run_reproduction_exact": True,
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
