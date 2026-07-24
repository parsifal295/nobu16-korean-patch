#!/usr/bin/env python3
"""Build Base block-0 runtime-terminal segment 1008 decisions."""

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

import build_base_batch001_segment1005 as PREVIOUS
import build_base_batch002_segment1007 as PRIOR_SEGMENT


ENGINE = PREVIOUS.ENGINE
GENERAL = PREVIOUS.GENERAL
UTIL = PREVIOUS.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B002_S1008.private.v1.jsonl"
)
SEGMENT = 1008
QUEUE_BATCH_ID = "base_msggame-B002"
RECORD_IDS = tuple(range(1543, 1609))
RECORD_KEYS = tuple((0, record_id) for record_id in RECORD_IDS)
PK_RECORD_MAP = {
    (0, record_id): (0, record_id + 54) for record_id in RECORD_IDS
}

EXPECTED_BASE_JP = {
    1543: "が",
    1544: "けれども",
    1545: "が",
    1546: "が",
    1547: "ありがたいこと",
    1548: "ありがたき限り",
    1549: "ありがとうございます",
    1550: "恐縮にございます",
    1551: "ありがとうございます",
    1552: "かたじけない",
    1553: "ありがたい",
    1554: "だろう",
    1555: "だろう",
    1556: "でしょう",
    1557: "でしょう",
    1558: "かと",
    1559: "かと",
    1560: "だろう",
    1561: "でしょうか",
    1562: "かな",
    1563: "でしょうか",
    1564: "でしょうか",
    1565: "ですか",
    1566: "ですかな",
    1567: "かな",
    1568: "きません",
    1569: "かぬ",
    1570: "きませぬ",
    1571: "きませぬ",
    1572: "きません",
    1573: "きませぬ",
    1574: "かぬ",
    1575: "お聞きなさい",
    1576: "聞くがいい",
    1577: "どうかお聞きを",
    1578: "お聞き入れくだされ",
    1579: "お聞きください",
    1580: "聞いてくだされ",
    1581: "聞いてくれ",
    1582: "きます",
    1583: "く",
    1584: "きまする",
    1585: "きます",
    1586: "きます",
    1587: "きまする",
    1588: "く",
    1589: "ぎます",
    1590: "ぐ",
    1591: "ぎまする",
    1592: "ぎます",
    1593: "ぎます",
    1594: "ぎまする",
    1595: "ぐ",
    1596: "くだされ",
    1597: "くれ",
    1598: "くださいまし",
    1599: "くださりませ",
    1600: "くださいませ",
    1601: "くだされ",
    1602: "くれ",
    1603: "くださった",
    1604: "くれた",
    1605: "くださいました",
    1606: "くだされました",
    1607: "くれました",
    1608: "くださった",
}
TRANSLATIONS_BY_RECORD = {
    1543: "지만",
    1544: "지만",
    1545: "지만",
    1546: "지만",
    1547: "고마운 일이군요",
    1548: "고마울 따름이다",
    1549: "감사합니다",
    1550: "황송하옵니다",
    1551: "감사합니다",
    1552: "황송하오",
    1553: "고맙다",
    1554: "이겠지",
    1555: "이겠지",
    1556: "이겠지요",
    1557: "이겠지요",
    1558: "인가 하고",
    1559: "인가 하고",
    1560: "이겠지",
    1561: "일까요",
    1562: "일까",
    1563: "일까요",
    1564: "일까요",
    1565: "입니까",
    1566: "일까 하오",
    1567: "일까",
    1568: "지 않습니다",
    1569: "지 않는다",
    1570: "지 않사옵니다",
    1571: "지 않사옵니다",
    1572: "지 않습니다",
    1573: "지 않사옵니다",
    1574: "지 않는다",
    1575: "들으세요",
    1576: "들어라",
    1577: "부디 들어 주소서",
    1578: "받아들여 주시오",
    1579: "들어 주십시오",
    1580: "들어 주시오",
    1581: "들어다오",
    1582: "합니다",
    1583: "한다",
    1584: "하옵니다",
    1585: "합니다",
    1586: "합니다",
    1587: "하옵니다",
    1588: "한다",
    1589: "합니다",
    1590: "한다",
    1591: "하옵니다",
    1592: "합니다",
    1593: "합니다",
    1594: "하옵니다",
    1595: "한다",
    1596: "주시오",
    1597: "다오",
    1598: "주십시오",
    1599: "주소서",
    1600: "주십시오",
    1601: "주시오",
    1602: "다오",
    1603: "주셨다",
    1604: "주었다",
    1605: "주셨습니다",
    1606: "주셨사옵니다",
    1607: "주었습니다",
    1608: "주셨다",
}
RAW_TRANSLATIONS = {
    f"0:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}

ARCHIVE_DIGESTS = {
    "base_jp": "5C72E4C4D0C85AC5252C60B2E7798BF2C41A255254639113C933234EC8CE8AD7",
    "base_current": "4AC5E017CD76ECF4602879DFD28A59D5BFD4617A1B08F9394BD7BD0A6D294E3F",
    "base_sc": "640EEC5E09EE29E42A002E87647613750AE02821FA6E0E835E38AF0587873DA3",
    "base_tc": "640EEC5E09EE29E42A002E87647613750AE02821FA6E0E835E38AF0587873DA3",
    "pk_jp": "A889D2469F77930534E1913961A4AEBD212FAA2FD9AF4ABA7B20A1242108077B",
    "pk_current": "08122D87945A3CF679D8A840B62CD3BA1E331A51F3B11496C453AEA771C6BC22",
    "pk_sc": "FA0142450CF1FE03EF696F2CEEA337F4A44F2EC33282CC94B687F1B69A843A5F",
    "pk_tc": "FA0142450CF1FE03EF696F2CEEA337F4A44F2EC33282CC94B687F1B69A843A5F",
    "pk_en": "FA0142450CF1FE03EF696F2CEEA337F4A44F2EC33282CC94B687F1B69A843A5F",
}
TERMINAL_GROUPS = {
    274: tuple(range(1543, 1547)),
    280: tuple(range(1547, 1554)),
    286: tuple(range(1554, 1561)),
    292: tuple(range(1561, 1568)),
    298: tuple(range(1568, 1575)),
    304: tuple(range(1575, 1582)),
    310: tuple(range(1582, 1589)),
    316: tuple(range(1589, 1596)),
    322: tuple(range(1596, 1603)),
    328: tuple(range(1603, 1609)),
}
FULL_GROUP_RECORD_IDS = {
    274: tuple(range(1540, 1547)),
    **{
        root: record_ids
        for root, record_ids in TERMINAL_GROUPS.items()
        if root not in (274, 328)
    },
    328: tuple(range(1603, 1610)),
}
CROSS_SEGMENT_SOURCE_JP = {
    1540: "けれど",
    1541: "が",
    1542: "けれども",
    1609: "くれた",
}
CROSS_SEGMENT_CURRENT_KO = {
    1540: "하지만",
    1541: "이",
    1542: "하지만",
    1609: "주었다",
}
CROSS_SEGMENT_TRANSLATION_POLICY = {
    1540: "지만",
    1541: "지만",
    1542: "지만",
    1609: "주었다",
}
BASE_JUMP_EDGE_SHA256 = (
    "1E040B747766944DE90723055ACCA443B5039C466162CBD70C8C5F0FF7449E6C"
)
PK_JUMP_EDGE_SHA256 = (
    "D5E70072012E5BF6DFA22DAE88F25B56A2A93B08D2A9CFEFC263667220CB7B98"
)
FULL_GROUP_JUMP_EDGE_SHA256 = {
    "base": (
        "1ADCDAB538FC99CCAD45F6BC068D454C6C107015737AC9558B880FFA8DF5CDB6"
    ),
    "pk": (
        "DD657A716D387851EBE589432C949FF87EFB86B6A4D44F5F0BA3FF21F1806488"
    ),
}
ROOT_CALL_EVIDENCE = {
    274: {
        "source": (
            19,
            "9F4134C6DAF5BBB7E3A07A8D87E810C6D1690D201E874E4201D64A266F8EFE29",
        ),
        "current": (
            19,
            "9F4134C6DAF5BBB7E3A07A8D87E810C6D1690D201E874E4201D64A266F8EFE29",
        ),
    },
    280: {
        "source": (
            15,
            "D4894088FA53810DCB65355CE2BAA5C84D6DEF8D6D2863F9FDE87EBA4DBB1F49",
        ),
        "current": (
            15,
            "D4894088FA53810DCB65355CE2BAA5C84D6DEF8D6D2863F9FDE87EBA4DBB1F49",
        ),
    },
    286: {
        "source": (
            28,
            "3CB2CAA00778A44F613DB3102057DB4F3EA40FD3A1373B25C0F7B67C26B53E7F",
        ),
        "current": (
            19,
            "C3EC5CAA80C3D70FBFEE484F33DEBA41E2A4FBB29B9137D2969E3E4579D087D5",
        ),
    },
    292: {
        "source": (
            27,
            "2154BC1A5DAEEA90E043BB1A91BCE8D3616B61FDE35D31A7E1CE1FAB576EF134",
        ),
        "current": (
            23,
            "890C90D863D8EB9199D07C9E9083B6DDB9C9229B5DD67E1E5EE133260C96508B",
        ),
    },
    298: {
        "source": (
            6,
            "37C13363717CFD67C6A1BD7CFDB26C0EC940DC6811F1031E7E9EBA77BE315DE1",
        ),
        "current": (
            6,
            "37C13363717CFD67C6A1BD7CFDB26C0EC940DC6811F1031E7E9EBA77BE315DE1",
        ),
    },
    304: {
        "source": (
            4,
            "65AA3FA569C477ADCB57757F53D97F43E954F3931EEB71B74C9A849E1519A777",
        ),
        "current": (
            4,
            "65AA3FA569C477ADCB57757F53D97F43E954F3931EEB71B74C9A849E1519A777",
        ),
    },
    310: {
        "source": (
            8,
            "00EA37ABC69CBFCAED4832F3272762DD6F28C9E5CF8D1E310CE48D0FC32D05B4",
        ),
        "current": (
            8,
            "00EA37ABC69CBFCAED4832F3272762DD6F28C9E5CF8D1E310CE48D0FC32D05B4",
        ),
    },
    316: {
        "source": (
            0,
            "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        ),
        "current": (
            0,
            "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        ),
    },
    322: {
        "source": (
            80,
            "980AD148B46049A2CD8C78E7F50CA5E2134337F6103813D43F5B46626715B275",
        ),
        "current": (
            76,
            "DB0B45C3105C651978B11039F96BAFC4C1E55CAFF58FBA5706106739AEC15D30",
        ),
    },
    328: {
        "source": (
            1,
            "573EF8540C30D6331FAB36C50CFAC82E6550CBB46E45DC82A4277BAE172A7AC0",
        ),
        "current": (
            1,
            "573EF8540C30D6331FAB36C50CFAC82E6550CBB46E45DC82A4277BAE172A7AC0",
        ),
    },
}
PK_ROOT_CALL_EVIDENCE = {
    274: {
        "source": (
            17,
            "6F6B10AD0533EF82956D41195A067DA7E4A612C6195D1E86E48D6BDB48FCE833",
        ),
        "current": (
            17,
            "6F6B10AD0533EF82956D41195A067DA7E4A612C6195D1E86E48D6BDB48FCE833",
        ),
    },
    280: {
        "source": (
            18,
            "3A0BEC7F17E7DB70A734653837096CC49A0E0F7DE401A14FBDE88D56A0976CCB",
        ),
        "current": (
            18,
            "3A0BEC7F17E7DB70A734653837096CC49A0E0F7DE401A14FBDE88D56A0976CCB",
        ),
    },
    286: {
        "source": (
            69,
            "66B511A727ED3449BB7D1D157FF2BBD23B1C5FE778D2BB866D13BC8259528E09",
        ),
        "current": (
            57,
            "4008392ADAEC87A215C3799DB63864097B57C357CBD77131130D471D8B2918F0",
        ),
    },
    292: {
        "source": (
            31,
            "CC1FA65CAFED7068328AC13CC9C9EDC2DED7220A19383096124AAB936EDF616B",
        ),
        "current": (
            26,
            "4BBC54E0E8F76B96A5B398AF71DA923A8AA5AA719DC3077AEA8F0312AAF415A5",
        ),
    },
    298: {
        "source": (
            11,
            "FEE9A7546A4213A178E1B627032C9D3FFD4B60C77C1E80EA5B72FF221589D35A",
        ),
        "current": (
            11,
            "FEE9A7546A4213A178E1B627032C9D3FFD4B60C77C1E80EA5B72FF221589D35A",
        ),
    },
    304: {
        "source": (
            4,
            "40F5C07725DB7711F4C70B84D8C8C0168F59E1F48035E01FE39C11A70B405FB5",
        ),
        "current": (
            4,
            "40F5C07725DB7711F4C70B84D8C8C0168F59E1F48035E01FE39C11A70B405FB5",
        ),
    },
    310: {
        "source": (
            14,
            "2BE5FF64A473F42668E39A7EF1C8BC1FB297A4E843F66708E3096137207630A9",
        ),
        "current": (
            14,
            "2BE5FF64A473F42668E39A7EF1C8BC1FB297A4E843F66708E3096137207630A9",
        ),
    },
    316: {
        "source": (
            0,
            "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        ),
        "current": (
            0,
            "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        ),
    },
    322: {
        "source": (
            94,
            "392237D1FD9837729E4BF97F96B4576AC0AE90C52653772D72CE4D74FC142144",
        ),
        "current": (
            85,
            "C9FDF5BCEC55541BCAB2AB226319D9037739E80DE9610E6A3FEB48FD7A3AFEFA",
        ),
    },
    328: {
        "source": (
            1,
            "70D255115AF35B31D2D2FD62D53B1F44E1E4D93F3A5E01A614F5295E18414EE1",
        ),
        "current": (
            1,
            "70D255115AF35B31D2D2FD62D53B1F44E1E4D93F3A5E01A614F5295E18414EE1",
        ),
    },
}
SOURCE_ONLY_FLATTENED_CALLS = {
    286: (
        "15:1823:1:0",
        "15:221:1:0",
        "15:222:1:0",
        "15:226:1:0",
        "15:243:1:0",
        "15:246:1:0",
        "15:247:1:0",
        "15:255:3:0",
        "15:260:1:0",
    ),
    292: (
        "13:30:1:0",
        "15:2216:2:6",
        "15:2222:2:0",
        "6:4460:1:0",
    ),
    322: (
        "13:127:2:0",
        "2:408:1:0",
        "2:557:2:0",
        "6:4439:1:0",
    ),
}
PK_SOURCE_ONLY_FLATTENED_CALLS = {
    286: (
        "6:4840:1:0",
        "8:1114:2:0",
        "15:224:1:0",
        "15:225:1:0",
        "15:229:1:0",
        "15:246:1:0",
        "15:249:1:0",
        "15:250:1:0",
        "15:258:3:0",
        "15:259:3:0",
        "15:263:1:0",
        "15:1853:1:0",
    ),
    292: (
        "6:4519:1:0",
        "13:30:1:0",
        "15:261:2:6",
        "15:2246:2:6",
        "15:2252:2:0",
    ),
    322: (
        "2:415:1:0",
        "2:574:2:0",
        "6:3560:1:0",
        "6:3561:1:0",
        "6:3566:1:0",
        "6:3569:1:0",
        "6:4498:1:0",
        "6:4858:1:0",
        "13:127:2:0",
    ),
}
CURRENT_CALLER_REWRITE_EXAMPLES = {
    274: {
        "8:288:2": "completed 입니다 cannot directly take bound 지만",
        "15:2359:1": "current 하나 plus 지만 would be 하나지만",
    },
    286: {
        "7:2428:2": "current upstream already ends 것이다",
        "15:268:1": "current upstream already contains conjectural 것이다",
    },
    292: {
        "1:15:3": "nominal 말인 needs a copular question form",
        "15:1877:3": "어떠 stem needs a verbal question ending",
    },
    298: {
        "2:525:2": "효 is not a usable Korean predicate stem",
        "6:3514:1": "놀 stem and following clause require a caller rewrite",
    },
    304: {
        "15:1769:2": "caller already contains a full listening instruction",
    },
    310: {
        "1:12:4": "물러 plus generic 하다 terminal is not grammatical",
        "15:1900:1": "들 plus generic 하다 terminal is not grammatical",
    },
    322: {
        "6:4435:2": "caller already ends 임명해 주 before benefactive terminal",
        "15:1554:2": "caller already contains complete 내려 주시오",
    },
}
BASIS = (
    "review_queue_base_msggame_B002_C_pristine_base_pc_jp_authoritative_"
    "block0_runtime_terminal_records1543_1608_uniform_plus54_pk_mapping_"
    "jp_current_sc_tc_exact_and_pk_en_empty_archive_digests_full_014a_"
    "incoming_edges_all_base_pk_source_current_0143_root_call_coordinate_"
    "digests_base_pk_source_only_flattened_call_registries_cross_segment_"
    "root274_records_"
    "1540_1542_and_root328_record1609_contract_contrastive_gratitude_"
    "conjectural_question_negative_listening_action_benefactive_register_"
    "matrices_feminine_nasai_polite_request_and_desukana_haoche_register_"
    "runtime_caller_rewrite_pending_one_line_reverse_overlay_"
    "no_korean_build_authority"
)


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return PREVIOUS.literal_texts(records, key)


def gap_bytes(record: Any) -> tuple[bytes, ...]:
    return PREVIOUS.gap_bytes(record)


def root_call_sites(
    records: dict[tuple[int, int], Any],
    root: int,
) -> tuple[str, ...]:
    return tuple(
        f"{key[0]}:{key[1]}:{gap_id}:{match.start()}"
        for key in sorted(records)
        for gap_id, gap in enumerate(gap_bytes(records[key]))
        for match in PREVIOUS.MORPHOLOGY_COMMAND_RE.finditer(gap)
        if struct.unpack("<I", match.group(1))[0] == root
    )


def archive_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    return PREVIOUS.archive_records(prepared)


def assert_corpora(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    for label, records in records_by_label.items():
        keys = (
            tuple(PK_RECORD_MAP.values())
            if label.startswith("pk_")
            else RECORD_KEYS
        )
        if GENERAL.subset_digest(records, keys) != ARCHIVE_DIGESTS[label]:
            raise RuntimeError(f"segment {SEGMENT} {label} corpus drifted")

    for key in RECORD_KEYS:
        mapped = PK_RECORD_MAP[key]
        record_id = key[1]
        if literal_texts(records_by_label["base_jp"], key) != (
            EXPECTED_BASE_JP[record_id],
        ):
            raise RuntimeError(
                f"segment {SEGMENT} pristine JP drifted: {key}"
            )
        for label in ("base_jp", "base_current", "base_sc", "base_tc"):
            if (
                len(literal_texts(records_by_label[label], key)) != 1
                or gap_bytes(records_by_label[label][key])
                != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base skeleton drifted: "
                    f"{label}/{key}"
                )
        for label in ("pk_jp", "pk_current", "pk_sc", "pk_tc", "pk_en"):
            if (
                len(literal_texts(records_by_label[label], mapped)) != 1
                or gap_bytes(records_by_label[label][mapped])
                != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} PK skeleton drifted: "
                    f"{label}/{mapped}"
                )
        for language in ("jp", "current", "sc", "tc"):
            if literal_texts(
                records_by_label[f"base_{language}"],
                key,
            ) != literal_texts(
                records_by_label[f"pk_{language}"],
                mapped,
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {language} mapping drifted: "
                    f"{key}/{mapped}"
                )
        if literal_texts(records_by_label["pk_en"], mapped) != ("",):
            raise RuntimeError(
                f"segment {SEGMENT} PK EN context drifted: {mapped}"
            )

    for record_id, source_jp in CROSS_SEGMENT_SOURCE_JP.items():
        key = (0, record_id)
        mapped = (0, record_id + 54)
        if (
            literal_texts(records_by_label["base_jp"], key)
            != (source_jp,)
            or literal_texts(records_by_label["base_current"], key)
            != (CROSS_SEGMENT_CURRENT_KO[record_id],)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} cross-segment literal drifted: {key}"
            )
        for label in ("base_jp", "base_current", "base_sc", "base_tc"):
            if gap_bytes(records_by_label[label][key]) != (
                b"",
                b"\x05\x05\x05",
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} cross Base skeleton drifted: "
                    f"{label}/{key}"
                )
        for language in ("jp", "current", "sc", "tc"):
            if literal_texts(
                records_by_label[f"base_{language}"],
                key,
            ) != literal_texts(
                records_by_label[f"pk_{language}"],
                mapped,
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} cross mapping drifted: "
                    f"{language}/{key}/{mapped}"
                )
        if literal_texts(records_by_label["pk_en"], mapped) != ("",):
            raise RuntimeError(
                f"segment {SEGMENT} cross PK EN drifted: {mapped}"
            )


def assert_runtime_graph(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    for edition, offset, expected_jump_sha256 in (
        ("base", 0, BASE_JUMP_EDGE_SHA256),
        ("pk", 54, PK_JUMP_EDGE_SHA256),
    ):
        target_ids = {record_id + offset for record_id in RECORD_IDS}
        for corpus in ("jp", "current"):
            records = records_by_label[f"{edition}_{corpus}"]
            edges = [
                [block_id, record_id, operand]
                for (block_id, record_id), record in sorted(records.items())
                for operand in PREVIOUS.operands(
                    record.data,
                    PREVIOUS.MORPHOLOGY_JUMP_RE,
                )
                if operand in target_ids
            ]
            digest = hashlib.sha256(
                json.dumps(edges, separators=(",", ":")).encode("ascii")
            ).hexdigest().upper()
            if (
                digest != expected_jump_sha256
                or len(edges) != len(RECORD_IDS)
                or {edge[2] for edge in edges} != target_ids
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {edition}_{corpus} "
                    "terminal edge drifted"
                )

            full_group_ids = {
                record_id + offset
                for record_ids in FULL_GROUP_RECORD_IDS.values()
                for record_id in record_ids
            }
            full_group_edges = [
                [block_id, record_id, operand]
                for (block_id, record_id), record in sorted(records.items())
                for operand in PREVIOUS.operands(
                    record.data,
                    PREVIOUS.MORPHOLOGY_JUMP_RE,
                )
                if operand in full_group_ids
            ]
            full_group_digest = hashlib.sha256(
                json.dumps(
                    full_group_edges,
                    separators=(",", ":"),
                ).encode("ascii")
            ).hexdigest().upper()
            if (
                full_group_digest != FULL_GROUP_JUMP_EDGE_SHA256[edition]
                or len(full_group_edges) != len(full_group_ids)
                or {
                    edge[2] for edge in full_group_edges
                } != full_group_ids
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {edition}_{corpus} "
                    "full-group terminal edge drifted"
                )

    for edition, evidence_by_root, flattened_by_root in (
        ("base", ROOT_CALL_EVIDENCE, SOURCE_ONLY_FLATTENED_CALLS),
        ("pk", PK_ROOT_CALL_EVIDENCE, PK_SOURCE_ONLY_FLATTENED_CALLS),
    ):
        source_records = records_by_label[f"{edition}_jp"]
        current_records = records_by_label[f"{edition}_current"]
        for root, evidence in evidence_by_root.items():
            source_sites = root_call_sites(source_records, root)
            current_sites = root_call_sites(current_records, root)
            for corpus, sites in (
                ("source", source_sites),
                ("current", current_sites),
            ):
                expected_count, expected_sha256 = evidence[corpus]
                actual_sha256 = hashlib.sha256(
                    "\n".join(sites).encode("ascii")
                ).hexdigest().upper()
                if (
                    len(sites) != expected_count
                    or actual_sha256 != expected_sha256
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} {edition} {corpus} "
                        f"root call drifted: {root}"
                    )
            expected_source_only = set(flattened_by_root.get(root, ()))
            if (
                set(source_sites) - set(current_sites)
                != expected_source_only
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {edition} source-only "
                    f"calls drifted: {root}"
                )
            if set(current_sites) - set(source_sites):
                raise RuntimeError(
                    f"segment {SEGMENT} {edition} current-only "
                    f"calls appeared: {root}"
                )
            if edition == "base":
                current_coordinates = {
                    site.rsplit(":", 1)[0] for site in current_sites
                }
                examples = set(
                    CURRENT_CALLER_REWRITE_EXAMPLES.get(root, {})
                )
                if not examples.issubset(current_coordinates):
                    raise RuntimeError(
                        f"segment {SEGMENT} caller example drifted: "
                        f"{root}"
                    )

    if set().union(*map(set, TERMINAL_GROUPS.values())) != set(RECORD_IDS):
        raise RuntimeError(f"segment {SEGMENT} terminal universe drifted")
    if (
        FULL_GROUP_RECORD_IDS[274] != tuple(range(1540, 1547))
        or FULL_GROUP_RECORD_IDS[328] != tuple(range(1603, 1610))
    ):
        raise RuntimeError(
            f"segment {SEGMENT} cross-segment group drifted"
        )


def assert_semantics(translations: dict[str, str]) -> None:
    if (
        translations != RAW_TRANSLATIONS
        or len(translations) != 66
        or set(EXPECTED_BASE_JP) != set(RECORD_IDS)
    ):
        raise RuntimeError(f"segment {SEGMENT} translation universe drifted")
    if {
        translations[f"0:{record_id}:0"]
        for record_id in range(1543, 1547)
    } != {"지만"} or set(
        CROSS_SEGMENT_TRANSLATION_POLICY[record_id]
        for record_id in range(1540, 1543)
    ) != {"지만"}:
        raise RuntimeError(
            f"segment {SEGMENT} contrastive root policy drifted"
        )
    if tuple(
        PRIOR_SEGMENT.TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(1540, 1543)
    ) != ("지만", "지만", "지만"):
        raise RuntimeError(
            f"segment {SEGMENT} S1007 root274 boundary drifted"
        )
    if tuple(
        translations[f"0:{record_id}:0"]
        for record_id in range(1547, 1554)
    ) != (
        "고마운 일이군요",
        "고마울 따름이다",
        "감사합니다",
        "황송하옵니다",
        "감사합니다",
        "황송하오",
        "고맙다",
    ):
        raise RuntimeError(
            f"segment {SEGMENT} gratitude register matrix drifted"
        )
    if tuple(
        translations[f"0:{record_id}:0"]
        for record_id in range(1554, 1561)
    ) != (
        "이겠지",
        "이겠지",
        "이겠지요",
        "이겠지요",
        "인가 하고",
        "인가 하고",
        "이겠지",
    ) or tuple(
        translations[f"0:{record_id}:0"]
        for record_id in range(1561, 1568)
    ) != (
        "일까요",
        "일까",
        "일까요",
        "일까요",
        "입니까",
        "일까 하오",
        "일까",
    ):
        raise RuntimeError(
            f"segment {SEGMENT} copular conjecture matrix drifted"
        )
    if tuple(
        translations[f"0:{record_id}:0"]
        for record_id in range(1568, 1575)
    ) != (
        "지 않습니다",
        "지 않는다",
        "지 않사옵니다",
        "지 않사옵니다",
        "지 않습니다",
        "지 않사옵니다",
        "지 않는다",
    ):
        raise RuntimeError(f"segment {SEGMENT} negative matrix drifted")
    if tuple(
        translations[f"0:{record_id}:0"]
        for record_id in range(1575, 1582)
    ) != (
        "들으세요",
        "들어라",
        "부디 들어 주소서",
        "받아들여 주시오",
        "들어 주십시오",
        "들어 주시오",
        "들어다오",
    ):
        raise RuntimeError(
            f"segment {SEGMENT} listening request matrix drifted"
        )
    neutral_action = (
        "합니다",
        "한다",
        "하옵니다",
        "합니다",
        "합니다",
        "하옵니다",
        "한다",
    )
    if tuple(
        translations[f"0:{record_id}:0"]
        for record_id in range(1582, 1589)
    ) != neutral_action or tuple(
        translations[f"0:{record_id}:0"]
        for record_id in range(1589, 1596)
    ) != neutral_action:
        raise RuntimeError(
            f"segment {SEGMENT} action register matrix drifted"
        )
    if tuple(
        translations[f"0:{record_id}:0"]
        for record_id in range(1596, 1603)
    ) != (
        "주시오",
        "다오",
        "주십시오",
        "주소서",
        "주십시오",
        "주시오",
        "다오",
    ):
        raise RuntimeError(
            f"segment {SEGMENT} benefactive imperative matrix drifted"
        )
    if tuple(
        translations[f"0:{record_id}:0"]
        for record_id in range(1603, 1609)
    ) + (CROSS_SEGMENT_TRANSLATION_POLICY[1609],) != (
        "주셨다",
        "주었다",
        "주셨습니다",
        "주셨사옵니다",
        "주었습니다",
        "주셨다",
        "주었다",
    ):
        raise RuntimeError(
            f"segment {SEGMENT} benefactive past matrix drifted"
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


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]], str]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    records_by_label = archive_records(prepared)
    assert_corpora(records_by_label)
    assert_runtime_graph(records_by_label)

    current = records_by_label["base_current"]
    translations = dict(RAW_TRANSLATIONS)
    assert_semantics(translations)
    for coordinate, translation in translations.items():
        _, record_id, _ = (int(value) for value in coordinate.split(":"))
        current_text = literal_texts(current, (0, record_id))[0]
        if not ENGINE.is_visible_translation_candidate(current_text):
            raise RuntimeError(
                f"segment {SEGMENT} target became non-visible: "
                f"{coordinate}"
            )
        if UTIL.layout_signature(translation) != UTIL.layout_signature(
            current_text
        ):
            raise RuntimeError(
                f"segment {SEGMENT} layout signature drifted: "
                f"{coordinate}"
            )

    candidate_sha256 = GENERAL.assert_overlay_roundtrip(
        prepared,
        segment=SEGMENT,
        translations=translations,
        target_records=set(RECORD_KEYS),
    )
    root_by_record = {
        record_id: root
        for root, record_ids in TERMINAL_GROUPS.items()
        for record_id in record_ids
    }
    rows: list[dict[str, object]] = []
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        target = prepared.visible_targets[
            ("base_msggame", block_id, record_id, literal_id)
        ]
        root = root_by_record[record_id]
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
                    "root": root,
                    "automatic_space_inserted": False,
                    "full_terminal_record_ids": list(
                        FULL_GROUP_RECORD_IDS[root]
                    ),
                    "source_call_count": ROOT_CALL_EVIDENCE[root][
                        "source"
                    ][0],
                    "current_call_count": ROOT_CALL_EVIDENCE[root][
                        "current"
                    ][0],
                    "pk_source_call_count": PK_ROOT_CALL_EVIDENCE[root][
                        "source"
                    ][0],
                    "pk_current_call_count": PK_ROOT_CALL_EVIDENCE[root][
                        "current"
                    ][0],
                    "source_only_flattened_calls": list(
                        SOURCE_ONLY_FLATTENED_CALLS.get(root, ())
                    ),
                    "pk_source_only_flattened_calls": list(
                        PK_SOURCE_ONLY_FLATTENED_CALLS.get(root, ())
                    ),
                    "caller_rewrite_examples": (
                        CURRENT_CALLER_REWRITE_EXAMPLES.get(root, {})
                    ),
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
            (0, int(coordinate.split(":")[1])),
        )[0]
        for coordinate, translation in translations.items()
    )
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B002_S1008",
                "queue": QUEUE_BATCH_ID,
                "source_literal_count": 66,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "changed_literal_count": changed,
                "base_pk_record_offset": 54,
                "base_pk_jp_current_sc_tc_literal_divergence_records": [],
                "base_pk_jp_current_sc_tc_gap_divergence_records": [],
                "pk_en_visible_records": [],
                "terminal_groups": {
                    str(root): list(record_ids)
                    for root, record_ids in TERMINAL_GROUPS.items()
                },
                "full_group_record_ids": {
                    str(root): list(record_ids)
                    for root, record_ids in FULL_GROUP_RECORD_IDS.items()
                },
                "cross_segment_translation_policy": (
                    CROSS_SEGMENT_TRANSLATION_POLICY
                ),
                "root_call_evidence": ROOT_CALL_EVIDENCE,
                "pk_root_call_evidence": PK_ROOT_CALL_EVIDENCE,
                "source_only_flattened_calls": SOURCE_ONLY_FLATTENED_CALLS,
                "pk_source_only_flattened_calls": (
                    PK_SOURCE_ONLY_FLATTENED_CALLS
                ),
                "caller_rewrite_examples": (
                    CURRENT_CALLER_REWRITE_EXAMPLES
                ),
                "terminal_jump_edge_sha256": {
                    "base": BASE_JUMP_EDGE_SHA256,
                    "pk": PK_JUMP_EDGE_SHA256,
                },
                "full_group_jump_edge_sha256": (
                    FULL_GROUP_JUMP_EDGE_SHA256
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
