#!/usr/bin/env python3
"""Build Base block-0 runtime-terminal segment 1009 decisions."""

from __future__ import annotations

import hashlib
import json
import struct
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch002_segment1007 as GRAPH
import build_base_batch002_segment1008 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
GENERAL = PREVIOUS.GENERAL
UTIL = PREVIOUS.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B003_S1009.private.v1.jsonl"
)
SEGMENT = 1009
QUEUE_BATCH_ID = "base_msggame-B003"
BLOCK_ID = 0
RECORD_IDS = tuple(range(1609, 1676))
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)


def mapped_pk_record_id(record_id: int) -> int:
    if record_id <= 1665:
        return record_id + 54
    return record_id + 61


PK_RECORD_MAP = {
    (BLOCK_ID, record_id): (BLOCK_ID, mapped_pk_record_id(record_id))
    for record_id in RECORD_IDS
}

EXPECTED_BASE_JP = {
    1609: "くれた",
    1610: "くださる",
    1611: "くださる",
    1612: "くださいます",
    1613: "くださいます",
    1614: "くれます",
    1615: "くださいまする",
    1616: "くれる",
    1617: "いてください",
    1618: "け",
    1619: "いてくださいまし",
    1620: "いてくだされ",
    1621: "いてください",
    1622: "きなされ",
    1623: "け",
    1624: "いでください",
    1625: "げ",
    1626: "いでくださいまし",
    1627: "いでくだされ",
    1628: "いでください",
    1629: "ぎなされ",
    1630: "げ",
    1631: "けませぬ",
    1632: "けぬ",
    1633: "けません",
    1634: "けませぬ",
    1635: "けません",
    1636: "きかねる",
    1637: "けぬ",
    1638: "おいでください",
    1639: "来い",
    1640: "おいでください",
    1641: "おいでくだされ",
    1642: "来てください",
    1643: "来てくだされ",
    1644: "来い",
    1645: "きましょう",
    1646: "こう",
    1647: "きましょう",
    1648: "くとしましょう",
    1649: "きましょう",
    1650: "きましょう",
    1651: "こう",
    1652: "ぎましょう",
    1653: "ごう",
    1654: "ぎましょう",
    1655: "ぐとしましょう",
    1656: "ぎましょう",
    1657: "ぐといたそう",
    1658: "ごう",
    1659: "ございます",
    1660: "ござる",
    1661: "ございます",
    1662: "ございます",
    1663: "ございます",
    1664: "ござる",
    1665: "ある",
    1666: "みせ",
    1667: "みせ",
    1668: "ご覧にいれ",
    1669: "ご覧にいれ",
    1670: "ご覧にいれ",
    1671: "ご覧にいれ",
    1672: "みせ",
    1673: "ございません",
    1674: "ござらぬ",
    1675: "ございません",
}

TRANSLATIONS_BY_RECORD = {
    1609: "주었다",
    1610: "주신다",
    1611: "주신다",
    1612: "주십니다",
    1613: "주십니다",
    1614: "줍니다",
    1615: "주시옵니다",
    1616: "준다",
    1617: "들어 주십시오",
    1618: "들어라",
    1619: "들어 주십시오",
    1620: "들어 주시오",
    1621: "들어 주십시오",
    1622: "들으시오",
    1623: "들어라",
    1624: "어 주십시오",
    1625: "어라",
    1626: "어 주십시오",
    1627: "어 주시오",
    1628: "어 주십시오",
    1629: "으시오",
    1630: "어라",
    1631: "지 못하옵니다",
    1632: "지 못한다",
    1633: "지 못합니다",
    1634: "지 못하옵니다",
    1635: "지 못합니다",
    1636: "기 어렵다",
    1637: "지 못한다",
    1638: "오십시오",
    1639: "오너라",
    1640: "오십시오",
    1641: "와 주시오",
    1642: "와 주십시오",
    1643: "와 주시오",
    1644: "오너라",
    1645: "겠습니다",
    1646: "겠다",
    1647: "겠습니다",
    1648: "기로 하겠습니다",
    1649: "겠습니다",
    1650: "겠습니다",
    1651: "겠다",
    1652: "겠습니다",
    1653: "겠다",
    1654: "겠습니다",
    1655: "기로 하겠습니다",
    1656: "겠습니다",
    1657: "기로 하겠소",
    1658: "겠다",
    1659: "입니다",
    1660: "있소",
    1661: "입니다",
    1662: "입니다",
    1663: "입니다",
    1664: "있소",
    1665: "있다",
    1666: "보여",
    1667: "보여",
    1668: "보여 드리",
    1669: "보여 드리",
    1670: "보여 드리",
    1671: "보여 드리",
    1672: "보여",
    1673: "없습니다",
    1674: "없소",
    1675: "없습니다",
}
TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}

FULL_GROUP_RECORD_IDS = {
    328: tuple(range(1603, 1610)),
    334: tuple(range(1610, 1617)),
    340: tuple(range(1617, 1624)),
    346: tuple(range(1624, 1631)),
    352: tuple(range(1631, 1638)),
    358: tuple(range(1638, 1645)),
    364: tuple(range(1645, 1652)),
    370: tuple(range(1652, 1659)),
    376: tuple(range(1659, 1666)),
    382: tuple(range(1666, 1673)),
    388: tuple(range(1673, 1680)),
}
TARGET_GROUP_RECORD_IDS = {
    root: tuple(
        record_id for record_id in record_ids if record_id in RECORD_IDS
    )
    for root, record_ids in FULL_GROUP_RECORD_IDS.items()
}
RECORD_TO_ROOT = {
    record_id: root
    for root, record_ids in TARGET_GROUP_RECORD_IDS.items()
    for record_id in record_ids
}
PK_ROOT_MAP = {
    328: 328,
    334: 334,
    340: 340,
    346: 346,
    352: 352,
    358: 358,
    364: 364,
    370: 370,
    376: 376,
    382: 388,
    388: 394,
}
PK_FULL_GROUP_RECORD_IDS = {
    root: tuple(mapped_pk_record_id(record_id) for record_id in record_ids)
    for root, record_ids in FULL_GROUP_RECORD_IDS.items()
}
FULL_BASE_RECORD_IDS = tuple(
    record_id
    for record_ids in FULL_GROUP_RECORD_IDS.values()
    for record_id in record_ids
)
FULL_PK_RECORD_IDS = tuple(
    record_id
    for record_ids in PK_FULL_GROUP_RECORD_IDS.values()
    for record_id in record_ids
)

PREVIOUS_BOUNDARY_CURRENT = {
    1603: "주셨다",
    1604: "주었다",
    1605: "주셨습니다",
    1606: "주셨습니다",
    1607: "주었습니다",
    1608: "주셨다",
}
NEXT_BOUNDARY_SOURCE_JP = {
    1676: "ございません",
    1677: "ございません",
    1678: "ござらぬ",
    1679: "ござらぬ",
}
NEXT_BOUNDARY_CURRENT = {
    1676: "아닙니다",
    1677: "아닙니다",
    1678: "없소",
    1679: "없소",
}
NEXT_BOUNDARY_TRANSLATION_POLICY = {
    1676: "없습니다",
    1677: "없습니다",
    1678: "없소",
    1679: "없소",
}
FULL_NEGATIVE_EXISTENCE_POLICY = (
    "없습니다",
    "없소",
    "없습니다",
    "없습니다",
    "없습니다",
    "없소",
    "없소",
)

ARCHIVE_DIGESTS = {
    "base_jp": "28EDE80B96C46F7C32C0ABBA1A3F750B4256522B8CDCB72538E70134CD48F820",
    "base_current": "11697F1371097D79638734D4D2D83E2516B980DE6C5674E25C316E0CD07BCCD7",
    "base_sc": "D9254A3AC20730C218CB226B0E0D26C99CC6716E74003D050F45CE10DE87D00F",
    "base_tc": "D9254A3AC20730C218CB226B0E0D26C99CC6716E74003D050F45CE10DE87D00F",
    "pk_jp": "26667FF0D70FE366E74A6DA732BDE8D040A69701579EACF7BD54B3C1A865ABDE",
    "pk_current": "34F9388025FF3D14FA59152C22FB5691B1EBB953A87FDAFE5384422DAAE9DFCC",
    "pk_sc": "955E0071BD0A27E6B1661B431444F54D8286D622EC614AA8A66037934D6E0691",
    "pk_tc": "955E0071BD0A27E6B1661B431444F54D8286D622EC614AA8A66037934D6E0691",
    "pk_en": "955E0071BD0A27E6B1661B431444F54D8286D622EC614AA8A66037934D6E0691",
}
PK_SOURCE_DIVERGENCES = {
    1636: {
        "base_jp": "きかねる",
        "pk_jp": "けませぬ",
        "base_current": "할 수 없다",
        "pk_current": "할 수 없사옵니다",
    }
}
PK_INSERTED_GROUP = {
    "record_ids": tuple(range(1720, 1727)),
    "root": 382,
    "jp": (
        "とうございます",
        "とうござる",
        "とうございます",
        "とうございます",
        "とうございます",
        "とうござる",
        "たい",
    ),
    "current": (
        "합니다",
        "하오",
        "합니다",
        "합니다",
        "합니다",
        "하오",
        "하고 싶다",
    ),
    "incoming_014a_sha256": (
        "8F615999E16D9C6F48FC6CFEB891CE4845C06C3673B5E8D347E02B6BC8E651A4"
    ),
    "caller_row_sha256": {
        "pk_jp": (
            "EB967539DB93297A347D948BF67EC0E0B8FDFCE3A06CDCCDE93D87DE055BBFDA"
        ),
        "pk_current": (
            "B28D4ABDD9EC5EEF2BDAA49C323A42AFA6CC4C62ECE9C964F3C8C530B8787183"
        ),
    },
    "caller_site": "7:2499:2:0",
}
JUMP_EDGE_EVIDENCE = {
    "base": {
        "target_count": 67,
        "target_sha256": (
            "16529D17F751251C2967374258EC1544E4A957B501AAF4C910705A3A49742B95"
        ),
        "full_count": 77,
        "full_sha256": (
            "81488BD5E87950A27F7599C43AC85BE694A386A78302DC29C1163BF4F811B2CD"
        ),
    },
    "pk": {
        "target_count": 67,
        "target_sha256": (
            "39EA0100F06BE07721A47324616FC4394B137F485D261F2547604D39ACE81B88"
        ),
        "full_count": 77,
        "full_sha256": (
            "DB14A738718D2BA539C1060449111A171372C4AD977A0AA2B52682BF5D1FDFEC"
        ),
    },
}
CALLER_ROW_EVIDENCE = {
    "base_jp": (
        69,
        "61AD73C4DD0DDFF0DA900D56C8C9A97067FBC014AF73F67FCA9F02D8AB2392E9",
    ),
    "base_current": (
        52,
        "368ADB5A95F41BD04BFF6B3DD5AE707A1B3805ABE8355FFAEFF64C08FCB3228B",
    ),
    "pk_jp": (
        105,
        "AAC3EF84380AFC04F5B3F5E7F6204C85B5B93E097EE11293E5531CA5AD489403",
    ),
    "pk_current": (
        90,
        "8186E693891B40B1FA7CEF2851F66F97300285FFD96652EB96BDACE0CCBD1FE9",
    ),
}
ROOT_CALL_EVIDENCE = {
    "base_jp": {
        328: (1, "573EF8540C30D6331FAB36C50CFAC82E6550CBB46E45DC82A4277BAE172A7AC0"),
        340: (1, "F6D1ACF0E1363349A86D5E4D3B61EC54CD612610892404003DF7C64A546E482E"),
        352: (1, "65A707883F23B0369BDC22990BAE5CE2B94BF315C3133B4D5A9F172E6150E9DF"),
        364: (28, "A6613115764178938306ABFD871F1AEA5923C8634A4A29A45C0184B553D30503"),
        370: (2, "665EF70E4FCA0A98A3A3864E93CCB7FBCDBCA83BAD48762A7759B94491AFFB60"),
        376: (28, "1C6821C2AA4184774CF076438D77324212670D3F3D0297863CA372731AD5A012"),
        382: (3, "7F0EF7A7EA3CE40EC9280D9AE23AABCB822ED150764D6ECD8CB1730DCDFF9809"),
        388: (5, "DAA98E8D640CADE66915274436611EAF2A372D80B41CABD42425F771DEE52A58"),
    },
    "base_current": {
        328: (1, "573EF8540C30D6331FAB36C50CFAC82E6550CBB46E45DC82A4277BAE172A7AC0"),
        340: (1, "F6D1ACF0E1363349A86D5E4D3B61EC54CD612610892404003DF7C64A546E482E"),
        352: (1, "65A707883F23B0369BDC22990BAE5CE2B94BF315C3133B4D5A9F172E6150E9DF"),
        364: (24, "37B4260A1511CD59BC0518C05D9E08099FBEF067E938C3B620DC35E943B3BC88"),
        376: (21, "FC92C3D862A191DFB11D854CAC314C54C145A5BF5F18C67D2B0357B5A6E24FA3"),
        382: (1, "039BC42E3E0177822420D944F6ABAAEF69CEB5599E1BF8A322F7A4D26703BFF6"),
        388: (3, "9B4AA5A50549DF5A31A309B0DAF26DB8EC0356C8C800806FFD612344B356A48F"),
    },
    "pk_jp": {
        328: (1, "70D255115AF35B31D2D2FD62D53B1F44E1E4D93F3A5E01A614F5295E18414EE1"),
        340: (2, "ABBFE8EEA99863E1B9D3B4B59EAA3D6EBC7C7FA33D0FFFAAC26FFC59DF8459C3"),
        352: (2, "DDC5F20A26ACEB6F51A1AB43A944F91CD79E2E322A230F9167DACEE44437EC77"),
        364: (42, "23E91ECB56118F99A25596B4515E6C015AF869368313022EE0FDE2991078199E"),
        370: (2, "90F9A9E7C8E0E8BFE1860AF99A42B9E4237EADED4A67B305C6EAD157269A8806"),
        376: (48, "ABA71997BFEEFE3D25F397A8848D451F11447A3E085A2EDE7DC2D04C50398111"),
        388: (3, "BAEE927B482799D3C6F4DD0E0B59F19306753751D655FB9389B0AABEB6E356A4"),
        394: (5, "8344E369C1319FF7A5F868D179FAEC1D23B28ED50A5C24E2C5EE789BFFCAC9E0"),
    },
    "pk_current": {
        328: (1, "70D255115AF35B31D2D2FD62D53B1F44E1E4D93F3A5E01A614F5295E18414EE1"),
        340: (2, "ABBFE8EEA99863E1B9D3B4B59EAA3D6EBC7C7FA33D0FFFAAC26FFC59DF8459C3"),
        352: (2, "DDC5F20A26ACEB6F51A1AB43A944F91CD79E2E322A230F9167DACEE44437EC77"),
        364: (38, "1533B93A0A6D56B31FEBE08BD32E3FA96CF9962A7AF1F53D849A0B78E9306C44"),
        376: (41, "A5AB70B57FF9E7C01CF5DB62B9A6A27F9CB6FDEA83C4458605BFD60D39E19EC1"),
        388: (3, "BAEE927B482799D3C6F4DD0E0B59F19306753751D655FB9389B0AABEB6E356A4"),
        394: (3, "EF7A5583C4C06C71D4747FCBD5DBF9E57D71C35266CBBE3F8026E8DE5908AE12"),
    },
}
SOURCE_ONLY_FLATTENED_CALLS = {
    "base": {
        364: ("15:1588:2:0", "15:1822:2:0", "2:484:1:0", "8:1060:2:0"),
        370: ("15:2211:1:0", "8:398:2:0"),
        376: (
            "12:45:1:0",
            "12:47:1:0",
            "12:49:1:0",
            "12:55:1:0",
            "12:57:1:0",
            "12:59:1:0",
            "12:61:1:0",
        ),
        382: ("2:331:1:0", "2:536:1:0"),
        388: ("13:110:1:0", "13:116:1:0"),
    },
    "pk": {
        364: ("15:1618:2:0", "15:1852:2:0", "2:498:1:0", "8:1072:2:0"),
        370: ("15:2241:1:0", "8:410:2:0"),
        376: (
            "12:45:1:0",
            "12:47:1:0",
            "12:49:1:0",
            "12:55:1:0",
            "12:57:1:0",
            "12:59:1:0",
            "12:61:1:0",
        ),
        394: ("13:110:1:0", "13:116:1:0"),
    },
}
FIXED_FOLLOWING_BLOCKERS = {
    "base_jp": {
        364: ("6:4335:2:0",),
        376: ("8:330:1:0", "15:1584:2:0", "15:2154:1:0"),
        382: ("2:331:1:0", "2:536:1:0", "15:259:3:0"),
        388: ("6:3639:2:0",),
    },
    "base_current": {
        364: ("6:4335:2:0",),
        376: ("8:330:1:0", "15:1584:2:0", "15:2154:1:0"),
        382: ("15:259:3:0",),
        388: ("6:3639:2:0",),
    },
    "pk_jp": {
        352: ("15:2472:2:0",),
        364: ("6:4394:2:0",),
        376: (
            "6:4588:5:0",
            "7:2512:1:0",
            "7:2512:2:0",
            "8:340:1:0",
            "9:3951:1:0",
            "15:1614:2:0",
            "15:2184:1:0",
        ),
        388: ("2:338:1:0", "2:550:1:0", "15:262:3:0"),
    },
    "pk_current": {
        352: ("15:2472:2:0",),
        364: ("6:4394:2:0",),
        376: (
            "6:4588:5:0",
            "7:2512:1:0",
            "7:2512:2:0",
            "8:340:1:0",
            "9:3951:1:0",
            "15:1614:2:0",
            "15:2184:1:0",
        ),
        388: ("2:338:1:0", "2:550:1:0", "15:262:3:0"),
    },
}
VALID_014C_EVIDENCE = {
    "base_jp": (),
    "base_current": (),
    "pk_jp": (),
    "pk_current": (),
}
OVERLAPPED_014C_EVIDENCE = {
    "base_jp": ((15, 25, 0, 193, 84213762),),
    "base_current": ((15, 25, 0, 193, 84213762),),
    "pk_jp": ((15, 25, 0, 65, 84213762),),
    "pk_current": ((15, 25, 0, 65, 84213762),),
}
ZERO_LIVE_CALL_ROOTS = (334, 346, 358)
SEMANTIC_AMBIGUITIES = {
    352: (
        "Base voice 5 is きかねる (기 어렵다), but the mapped PK voice "
        "5 is けませぬ (지 못하옵니다); Base pristine JP controls."
    ),
    364: (
        "Japanese volitional forms cover both speaker intention and "
        "hortative force; each caller must choose a Korean predicate "
        "stem and confirm 겠다 versus an inclusive 청유 rewrite."
    ),
    370: (
        "Voiced-godan volitional callers are already flattened in "
        "current Base/PK; source callers require later reintegration."
    ),
    376: (
        "ございます/ござる/ある serves both copular and existential "
        "contexts; one Korean terminal cannot cover both without "
        "caller-specific upstream rewrites."
    ),
    382: (
        "보여/보여 드리 is followed by a fixed action terminal at live "
        "callers, so upstream and downstream pieces must be rewritten "
        "as one assembly."
    ),
    388: (
        "Negative ござる is predominantly existential here, while one "
        "gift-question caller is copular; the latter needs a caller "
        "rewrite around the 없습니다 matrix."
    ),
}

BASIS = (
    "review_queue_base_msggame_B003_S1009_pristine_base_pc_jp_sole_"
    "authority_block0_runtime_terminal_records1609_1675_piecewise_pk_"
    "mapping_plus54_through1665_plus61_from1666_pk_inserted_root382_"
    "excluded_base1636_kikaneru_vs_pk_kemasenu_divergence_all_base_pk_"
    "014a_target_and_full_boundary_edges_0143_caller_row_and_per_root_"
    "digests_source_current_flattening_valid_014c_none_overlap_guard_"
    "fixed_following_blockers_root328_s1008_boundary_contract_full_"
    "seven_voice_benefactive_listen_godan_inability_come_volitional_"
    "copular_existence_show_negative_existence_tables_runtime_caller_"
    "rewrite_pending_one_line_reverse_overlay_no_korean_build_authority"
)


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return PREVIOUS.literal_texts(records, key)


def gap_bytes(record: Any) -> tuple[bytes, ...]:
    return PREVIOUS.gap_bytes(record)


def archive_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    return PREVIOUS.archive_records(prepared)


def digest_rows(rows: list[list[object]]) -> str:
    return hashlib.sha256(
        json.dumps(rows, separators=(",", ":")).encode("ascii")
    ).hexdigest().upper()


def is_text_boundary(character: str) -> bool:
    return (
        character.isspace()
        or unicodedata.category(character).startswith("P")
        or character == "\u2026"
    )


def fixed_following_blockers(
    records: dict[tuple[int, int], Any],
    roots: set[int],
) -> dict[int, tuple[str, ...]]:
    blockers: dict[int, list[str]] = defaultdict(list)
    for key in sorted(records):
        record = records[key]
        literals = ENGINE.parse_record_literals(record)
        for gap_id, gap in enumerate(gap_bytes(record)):
            for match in GRAPH.MORPHOLOGY_COMMAND_RE.finditer(gap):
                root = struct.unpack("<I", match.group(1))[0]
                if root not in roots:
                    continue
                right = (
                    literals[gap_id].text
                    if gap_id < len(literals)
                    else ""
                )
                post = gap[match.end() :]
                has_adjacent_command = (
                    bool(post) and post != b"\x05\x05\x05"
                )
                has_fixed_right = (
                    bool(right) and not is_text_boundary(right[0])
                )
                if has_adjacent_command or has_fixed_right:
                    blockers[root].append(
                        f"{key[0]}:{key[1]}:{gap_id}:{match.start()}"
                    )
    return {
        root: tuple(sites) for root, sites in sorted(blockers.items())
    }


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
        record_id = key[1]
        mapped = PK_RECORD_MAP[key]
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
        if record_id in PK_SOURCE_DIVERGENCES:
            expected = PK_SOURCE_DIVERGENCES[record_id]
            for label in (
                "base_jp",
                "pk_jp",
                "base_current",
                "pk_current",
            ):
                lookup_key = mapped if label.startswith("pk_") else key
                if literal_texts(
                    records_by_label[label],
                    lookup_key,
                ) != (expected[label],):
                    raise RuntimeError(
                        f"segment {SEGMENT} mapped divergence drifted: "
                        f"{label}/{lookup_key}"
                    )
        else:
            for language in ("jp", "current"):
                if literal_texts(
                    records_by_label[f"base_{language}"],
                    key,
                ) != literal_texts(
                    records_by_label[f"pk_{language}"],
                    mapped,
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} mapping drifted: "
                        f"{language}/{key}/{mapped}"
                    )
        for language in ("sc", "tc"):
            if (
                literal_texts(
                    records_by_label[f"base_{language}"],
                    key,
                )
                != ("",)
                or literal_texts(
                    records_by_label[f"pk_{language}"],
                    mapped,
                )
                != ("",)
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} auxiliary context drifted: "
                    f"{language}/{key}/{mapped}"
                )
        if literal_texts(records_by_label["pk_en"], mapped) != ("",):
            raise RuntimeError(
                f"segment {SEGMENT} PK EN context drifted: {mapped}"
            )


def assert_full_group_boundaries(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    previous_source = {
        record_id: PREVIOUS.EXPECTED_BASE_JP[record_id]
        for record_id in range(1603, 1609)
    }
    for record_id in FULL_BASE_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        mapped = (BLOCK_ID, mapped_pk_record_id(record_id))
        if record_id < 1609:
            expected_jp = previous_source[record_id]
            expected_current = PREVIOUS_BOUNDARY_CURRENT[record_id]
        elif record_id in EXPECTED_BASE_JP:
            expected_jp = EXPECTED_BASE_JP[record_id]
            expected_current = literal_texts(
                records_by_label["base_current"],
                key,
            )[0]
        else:
            expected_jp = NEXT_BOUNDARY_SOURCE_JP[record_id]
            expected_current = NEXT_BOUNDARY_CURRENT[record_id]
        if (
            literal_texts(records_by_label["base_jp"], key)
            != (expected_jp,)
            or literal_texts(records_by_label["base_current"], key)
            != (expected_current,)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} full boundary literal drifted: {key}"
            )
        if (
            len(literal_texts(records_by_label["base_jp"], key)) != 1
            or gap_bytes(records_by_label["base_jp"][key])
            != (b"", b"\x05\x05\x05")
        ):
            raise RuntimeError(
                f"segment {SEGMENT} full boundary skeleton drifted: {key}"
            )
        for label in (
            "base_jp",
            "base_current",
            "base_sc",
            "base_tc",
            "pk_jp",
            "pk_current",
            "pk_sc",
            "pk_tc",
            "pk_en",
        ):
            lookup_key = mapped if label.startswith("pk_") else key
            if (
                len(literal_texts(
                    records_by_label[label],
                    lookup_key,
                ))
                != 1
                or gap_bytes(records_by_label[label][lookup_key])
                != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} full skeleton drifted: "
                    f"{label}/{lookup_key}"
                )
        if record_id == 1636:
            continue
        for language in ("jp", "current", "sc", "tc"):
            if literal_texts(
                records_by_label[f"base_{language}"],
                key,
            ) != literal_texts(
                records_by_label[f"pk_{language}"],
                mapped,
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} full mapping drifted: "
                    f"{language}/{key}/{mapped}"
                )
        if literal_texts(records_by_label["pk_en"], mapped) != ("",):
            raise RuntimeError(
                f"segment {SEGMENT} full PK EN drifted: {mapped}"
            )
        for language in ("sc", "tc"):
            if literal_texts(
                records_by_label[f"base_{language}"],
                key,
            ) != ("",):
                raise RuntimeError(
                    f"segment {SEGMENT} full Base {language} "
                    f"context drifted: {key}"
                )

    previous_policy = tuple(
        PREVIOUS.TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(1603, 1609)
    ) + (TRANSLATIONS_BY_RECORD[1609],)
    if previous_policy != (
        "주셨다",
        "주었다",
        "주셨습니다",
        "주셨사옵니다",
        "주었습니다",
        "주셨다",
        "주었다",
    ):
        raise RuntimeError(
            f"segment {SEGMENT} S1008 root328 contract drifted"
        )

    inserted_ids = set(PK_INSERTED_GROUP["record_ids"])
    for corpus in ("jp", "current"):
        label = f"pk_{corpus}"
        actual_literals = tuple(
            literal_texts(
                records_by_label[label],
                (BLOCK_ID, record_id),
            )[0]
            for record_id in PK_INSERTED_GROUP["record_ids"]
        )
        if actual_literals != PK_INSERTED_GROUP[corpus]:
            raise RuntimeError(
                f"segment {SEGMENT} inserted PK root382 "
                f"{corpus} literals drifted"
            )
        for record_id in PK_INSERTED_GROUP["record_ids"]:
            key = (BLOCK_ID, record_id)
            if gap_bytes(records_by_label[label][key]) != (
                b"",
                b"\x05\x05\x05",
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} inserted PK root382 "
                    f"skeleton drifted: {label}/{key}"
                )
        edges = GRAPH.incoming_jump_rows(
            records_by_label[label],
            inserted_ids,
        )
        if (
            len(edges) != 7
            or {row[4] for row in edges} != inserted_ids
            or digest_rows(edges)
            != PK_INSERTED_GROUP["incoming_014a_sha256"]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} inserted PK root382 "
                f"014A edges drifted: {label}"
            )
        caller_rows, caller_sites = GRAPH.caller_rows(
            records_by_label[label],
            inserted_ids,
        )
        if (
            len(caller_rows) != 1
            or digest_rows(caller_rows)
            != PK_INSERTED_GROUP["caller_row_sha256"][label]
            or caller_sites
            != {
                PK_INSERTED_GROUP["root"]: (
                    PK_INSERTED_GROUP["caller_site"],
                )
            }
        ):
            raise RuntimeError(
                f"segment {SEGMENT} inserted PK root382 "
                f"caller drifted: {label}"
            )


def assert_jump_and_call_graphs(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    for side, target_ids, full_ids in (
        ("base", set(RECORD_IDS), set(FULL_BASE_RECORD_IDS)),
        (
            "pk",
            {key[1] for key in PK_RECORD_MAP.values()},
            set(FULL_PK_RECORD_IDS),
        ),
    ):
        for corpus in ("jp", "current"):
            label = f"{side}_{corpus}"
            records = records_by_label[label]
            for scope, ids in (
                ("target", target_ids),
                ("full", full_ids),
            ):
                rows = GRAPH.incoming_jump_rows(records, ids)
                evidence = JUMP_EDGE_EVIDENCE[side]
                if (
                    len(rows) != evidence[f"{scope}_count"]
                    or digest_rows(rows) != evidence[f"{scope}_sha256"]
                    or {row[4] for row in rows} != ids
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} {label} "
                        f"{scope} 014A edge drifted"
                    )

            rows, sites = GRAPH.caller_rows(records, full_ids)
            expected_count, expected_sha256 = CALLER_ROW_EVIDENCE[label]
            if (
                len(rows) != expected_count
                or digest_rows(rows) != expected_sha256
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {label} caller rows drifted"
                )
            actual_root_evidence = {
                root: (
                    len(root_sites),
                    hashlib.sha256(
                        "\n".join(root_sites).encode("ascii")
                    ).hexdigest().upper(),
                )
                for root, root_sites in sorted(sites.items())
            }
            if actual_root_evidence != ROOT_CALL_EVIDENCE[label]:
                raise RuntimeError(
                    f"segment {SEGMENT} {label} root calls drifted"
                )

        _, source_sites = GRAPH.caller_rows(
            records_by_label[f"{side}_jp"],
            full_ids,
        )
        _, current_sites = GRAPH.caller_rows(
            records_by_label[f"{side}_current"],
            full_ids,
        )
        roots = set(source_sites) | set(current_sites)
        flattened = {
            root: tuple(
                sorted(
                    set(source_sites.get(root, ()))
                    - set(current_sites.get(root, ()))
                )
            )
            for root in roots
            if set(source_sites.get(root, ()))
            != set(current_sites.get(root, ()))
        }
        current_only = {
            root: tuple(
                sorted(
                    set(current_sites.get(root, ()))
                    - set(source_sites.get(root, ()))
                )
            )
            for root in roots
            if set(current_sites.get(root, ()))
            - set(source_sites.get(root, ()))
        }
        if (
            flattened != SOURCE_ONLY_FLATTENED_CALLS[side]
            or current_only
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {side} caller flattening drifted"
            )


def assert_014c_and_blockers(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    for label in ("base_jp", "base_current", "pk_jp", "pk_current"):
        valid: list[tuple[int, int, int, int, int]] = []
        overlapped: list[tuple[int, int, int, int, int]] = []
        for (block_id, record_id), record in sorted(
            records_by_label[label].items()
        ):
            for gap_id, gap in enumerate(gap_bytes(record)):
                jump_spans = [
                    range(match.start(), match.end())
                    for match in GRAPH.MORPHOLOGY_JUMP_RE.finditer(gap)
                ]
                for match in GRAPH.MORPHOLOGY_014C_RE.finditer(gap):
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
        if (
            tuple(valid) != VALID_014C_EVIDENCE[label]
            or tuple(overlapped) != OVERLAPPED_014C_EVIDENCE[label]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} 014C evidence drifted"
            )

        roots = (
            set(FULL_GROUP_RECORD_IDS)
            if label.startswith("base_")
            else set(PK_ROOT_MAP.values())
        )
        actual_blockers = fixed_following_blockers(
            records_by_label[label],
            roots,
        )
        if actual_blockers != FIXED_FOLLOWING_BLOCKERS[label]:
            raise RuntimeError(
                f"segment {SEGMENT} {label} blocker drifted"
            )


def assert_semantics(translations: dict[str, str]) -> None:
    if (
        len(RECORD_IDS) != 67
        or set(EXPECTED_BASE_JP) != set(RECORD_IDS)
        or set(TRANSLATIONS_BY_RECORD) != set(RECORD_IDS)
        or set(RECORD_TO_ROOT) != set(RECORD_IDS)
        or translations != TRANSLATIONS
    ):
        raise RuntimeError(f"segment {SEGMENT} decision universe drifted")
    if any(
        root in ROOT_CALL_EVIDENCE[label]
        for root in ZERO_LIVE_CALL_ROOTS
        for label in ROOT_CALL_EVIDENCE
    ):
        raise RuntimeError(
            f"segment {SEGMENT} zero-call root evidence drifted"
        )
    if TRANSLATIONS_BY_RECORD[1609] != "주었다":
        raise RuntimeError(f"segment {SEGMENT} root328 boundary drifted")
    matrices = {
        (1610, 1617): (
            "주신다",
            "주신다",
            "주십니다",
            "주십니다",
            "줍니다",
            "주시옵니다",
            "준다",
        ),
        (1617, 1624): (
            "들어 주십시오",
            "들어라",
            "들어 주십시오",
            "들어 주시오",
            "들어 주십시오",
            "들으시오",
            "들어라",
        ),
        (1624, 1631): (
            "어 주십시오",
            "어라",
            "어 주십시오",
            "어 주시오",
            "어 주십시오",
            "으시오",
            "어라",
        ),
        (1631, 1638): (
            "지 못하옵니다",
            "지 못한다",
            "지 못합니다",
            "지 못하옵니다",
            "지 못합니다",
            "기 어렵다",
            "지 못한다",
        ),
        (1638, 1645): (
            "오십시오",
            "오너라",
            "오십시오",
            "와 주시오",
            "와 주십시오",
            "와 주시오",
            "오너라",
        ),
        (1645, 1652): (
            "겠습니다",
            "겠다",
            "겠습니다",
            "기로 하겠습니다",
            "겠습니다",
            "겠습니다",
            "겠다",
        ),
        (1652, 1659): (
            "겠습니다",
            "겠다",
            "겠습니다",
            "기로 하겠습니다",
            "겠습니다",
            "기로 하겠소",
            "겠다",
        ),
        (1659, 1666): (
            "입니다",
            "있소",
            "입니다",
            "입니다",
            "입니다",
            "있소",
            "있다",
        ),
        (1666, 1673): (
            "보여",
            "보여",
            "보여 드리",
            "보여 드리",
            "보여 드리",
            "보여 드리",
            "보여",
        ),
    }
    for (start, stop), expected in matrices.items():
        actual = tuple(
            TRANSLATIONS_BY_RECORD[record_id]
            for record_id in range(start, stop)
        )
        if actual != expected:
            raise RuntimeError(
                f"segment {SEGMENT} matrix drifted: {start}..{stop - 1}"
            )
    actual_negative = tuple(
        TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(1673, 1676)
    ) + tuple(
        NEXT_BOUNDARY_TRANSLATION_POLICY[record_id]
        for record_id in range(1676, 1680)
    )
    if actual_negative != FULL_NEGATIVE_EXISTENCE_POLICY:
        raise RuntimeError(
            f"segment {SEGMENT} negative-existence matrix drifted"
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


def evidence_for_root(
    label: str,
    root: int,
) -> dict[str, object]:
    count, sha256 = ROOT_CALL_EVIDENCE[label].get(
        root,
        (
            0,
            "E3B0C44298FC1C149AFBF4C8996FB924"
            "27AE41E4649B934CA495991B7852B855",
        ),
    )
    return {"count": count, "sha256": sha256}


def build_rows() -> tuple[Any, list[dict[str, object]], str]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    records_by_label = archive_records(prepared)
    assert_corpora(records_by_label)
    assert_full_group_boundaries(records_by_label)
    assert_jump_and_call_graphs(records_by_label)
    assert_014c_and_blockers(records_by_label)
    assert_semantics(TRANSLATIONS)

    current = records_by_label["base_current"]
    for coordinate, translation in TRANSLATIONS.items():
        _, record_id, _ = (int(value) for value in coordinate.split(":"))
        current_text = literal_texts(
            current,
            (BLOCK_ID, record_id),
        )[0]
        if (
            not ENGINE.is_visible_translation_candidate(current_text)
            or "\n" in current_text
            or current_text != current_text.strip()
            or "\n" in translation
            or translation != translation.strip()
            or UTIL.layout_signature(translation)
            != UTIL.layout_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} protected signature drifted: "
                f"{coordinate}"
            )

    candidate_sha256 = GENERAL.assert_overlay_roundtrip(
        prepared,
        segment=SEGMENT,
        translations=TRANSLATIONS,
        target_records=set(RECORD_KEYS),
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        target = prepared.visible_targets[
            ("base_msggame", block_id, record_id, literal_id)
        ]
        root = RECORD_TO_ROOT[record_id]
        pk_root = PK_ROOT_MAP[root]
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
                    "pk_root": pk_root,
                    "base_full_terminal_record_ids": list(
                        FULL_GROUP_RECORD_IDS[root]
                    ),
                    "pk_full_terminal_record_ids": list(
                        PK_FULL_GROUP_RECORD_IDS[root]
                    ),
                    "pk_mapped_record_id": mapped_pk_record_id(record_id),
                    "pk_source_divergence": (
                        PK_SOURCE_DIVERGENCES.get(record_id)
                    ),
                    "base_source_calls": evidence_for_root(
                        "base_jp",
                        root,
                    ),
                    "base_current_calls": evidence_for_root(
                        "base_current",
                        root,
                    ),
                    "pk_source_calls": evidence_for_root(
                        "pk_jp",
                        pk_root,
                    ),
                    "pk_current_calls": evidence_for_root(
                        "pk_current",
                        pk_root,
                    ),
                    "base_source_only_flattened_calls": list(
                        SOURCE_ONLY_FLATTENED_CALLS["base"].get(
                            root,
                            (),
                        )
                    ),
                    "pk_source_only_flattened_calls": list(
                        SOURCE_ONLY_FLATTENED_CALLS["pk"].get(
                            pk_root,
                            (),
                        )
                    ),
                    "base_fixed_following_blockers": list(
                        FIXED_FOLLOWING_BLOCKERS["base_current"].get(
                            root,
                            (),
                        )
                    ),
                    "pk_fixed_following_blockers": list(
                        FIXED_FOLLOWING_BLOCKERS["pk_current"].get(
                            pk_root,
                            (),
                        )
                    ),
                    "semantic_ambiguity": (
                        SEMANTIC_AMBIGUITIES.get(root)
                    ),
                    "zero_live_0143_calls": (
                        root in ZERO_LIVE_CALL_ROOTS
                    ),
                    "runtime_integration_required": True,
                },
            }
        )
    return prepared, rows, candidate_sha256


def main() -> int:
    prepared, rows, candidate_sha256 = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(validated) != 67 or len(rows) != 67:
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
        for coordinate, translation in TRANSLATIONS.items()
    )
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B003_S1009",
                "queue": QUEUE_BATCH_ID,
                "source_literal_count": 67,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "changed_literal_count": changed,
                "base_pk_mapping": {
                    "1609_1665": 54,
                    "1666_1675": 61,
                },
                "base_pk_source_divergences": (
                    PK_SOURCE_DIVERGENCES
                ),
                "pk_inserted_group": PK_INSERTED_GROUP,
                "full_group_record_ids": FULL_GROUP_RECORD_IDS,
                "pk_full_group_record_ids": (
                    PK_FULL_GROUP_RECORD_IDS
                ),
                "pk_root_map": PK_ROOT_MAP,
                "jump_edge_evidence": JUMP_EDGE_EVIDENCE,
                "caller_row_evidence": CALLER_ROW_EVIDENCE,
                "root_call_evidence": ROOT_CALL_EVIDENCE,
                "source_only_flattened_calls": (
                    SOURCE_ONLY_FLATTENED_CALLS
                ),
                "fixed_following_blockers": (
                    FIXED_FOLLOWING_BLOCKERS
                ),
                "valid_014c_evidence": VALID_014C_EVIDENCE,
                "overlapped_014c_evidence": (
                    OVERLAPPED_014C_EVIDENCE
                ),
                "zero_live_call_roots": ZERO_LIVE_CALL_ROOTS,
                "semantic_ambiguities": SEMANTIC_AMBIGUITIES,
                "next_boundary_translation_policy": (
                    NEXT_BOUNDARY_TRANSLATION_POLICY
                ),
                "candidate_sha256": candidate_sha256,
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
                "target_runtime_skeleton_exact": True,
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
