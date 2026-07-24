#!/usr/bin/env python3
"""Build Base block-0 runtime-terminal segment 1011 decisions."""

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

import build_base_batch002_segment1007 as GRAPH
import build_base_batch002_segment1008 as PRIOR


ENGINE = PRIOR.ENGINE
GENERAL = PRIOR.GENERAL
UTIL = PRIOR.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B003_S1011.private.v1.jsonl"
)
SEGMENT = 1011
QUEUE_BATCH_ID = "base_msggame-B003"
BLOCK_ID = 0
RECORD_IDS = tuple(range(1743, 1809))
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)

# PK inserts one seven-record terminal family before this semantic range.
# Exact seven-literal JP tuple matching establishes +61; +54 would point at
# unrelated grammar families.
PK_RECORD_MAP = {
    (BLOCK_ID, record_id): (BLOCK_ID, record_id + 61)
    for record_id in RECORD_IDS
}

EXPECTED_BASE_JP = {
    1743: "します",
    1744: "す",
    1745: "します",
    1746: "しまする",
    1747: "します",
    1748: "します",
    1749: "す",
    1750: "さないで",
    1751: "すな",
    1752: "さないでください",
    1753: "しなさいますな",
    1754: "さないでください",
    1755: "されますな",
    1756: "すな",
    1757: "ないで",
    1758: "ずに",
    1759: "ないまま",
    1760: "ずに",
    1761: "ないままで",
    1762: "ずに",
    1763: "ないで",
    1764: "しますまい",
    1765: "すまじ",
    1766: "しますまい",
    1767: "しますまい",
    1768: "しますまい",
    1769: "しますまい",
    1770: "すまい",
    1771: "すみません",
    1772: "すまぬ",
    1773: "申し訳ございませぬ",
    1774: "申し訳ございませぬ",
    1775: "すみません",
    1776: "相済みません",
    1777: "すまぬ",
    1778: "します",
    1779: "する",
    1780: "いたします",
    1781: "いたしまする",
    1782: "します",
    1783: "いたします",
    1784: "する",
    1785: "じます",
    1786: "ずる",
    1787: "じます",
    1788: "じまする",
    1789: "じます",
    1790: "じます",
    1791: "ずる",
    1792: "なさいますな",
    1793: "するな",
    1794: "なさいますな",
    1795: "なされますな",
    1796: "されまするな",
    1797: "しないでくだされ",
    1798: "するな",
    1799: "してください",
    1800: "せ",
    1801: "してくださいませ",
    1802: "してくだされ",
    1803: "してください",
    1804: "してくだされ",
    1805: "せ",
    1806: "しません",
    1807: "せぬ",
    1808: "いたしません",
}

TRANSLATIONS_BY_RECORD = {
    1743: "합니다",
    1744: "한다",
    1745: "합니다",
    1746: "하옵니다",
    1747: "합니다",
    1748: "합니다",
    1749: "한다",
    1750: "하지 마세요",
    1751: "하지 마라",
    1752: "하지 말아 주십시오",
    1753: "하지 마시옵소서",
    1754: "하지 말아 주십시오",
    1755: "하지 마시오",
    1756: "하지 마라",
    1757: "지 않고",
    1758: "지 않고",
    1759: "지 않은 채",
    1760: "지 않고",
    1761: "지 않은 채로",
    1762: "지 않고",
    1763: "지 않고",
    1764: "하지 않겠습니다",
    1765: "하지 않으리",
    1766: "하지 않겠사옵니다",
    1767: "하지 않겠사옵니다",
    1768: "하지 않겠습니다",
    1769: "하지 않겠소",
    1770: "하지 않으리",
    1771: "죄송합니다",
    1772: "미안하오",
    1773: "송구하옵니다",
    1774: "송구하옵니다",
    1775: "죄송합니다",
    1776: "면목이 없습니다",
    1777: "미안하오",
    1778: "합니다",
    1779: "한다",
    1780: "하옵니다",
    1781: "하옵니다",
    1782: "합니다",
    1783: "하옵니다",
    1784: "한다",
    1785: "합니다",
    1786: "한다",
    1787: "합니다",
    1788: "하옵니다",
    1789: "합니다",
    1790: "합니다",
    1791: "한다",
    1792: "하지 마시오",
    1793: "하지 마라",
    1794: "하지 마시오",
    1795: "하지 마시옵소서",
    1796: "하지 마시옵소서",
    1797: "하지 말아 주시오",
    1798: "하지 마라",
    1799: "해 주십시오",
    1800: "하라",
    1801: "해 주시옵소서",
    1802: "해 주시오",
    1803: "해 주십시오",
    1804: "해 주시오",
    1805: "하라",
    1806: "하지 않습니다",
    1807: "하지 않는다",
    1808: "하지 않사옵니다",
}
RAW_TRANSLATIONS = {
    f"0:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}

ARCHIVE_DIGESTS = {
    "base_jp": "252CAA562AE85249746EAEF88902B4E965F72EA33BC52DC44CE36DB0F3FEE2F3",
    "base_current": "4A63F3400A19AD0C1272719F12C7FDFDA898D80CE053769DD78D4A750255561C",
    "base_sc": "47DD4613289EE07B5501B010D70E5226200BEA76FA0459BA8BD8F90376793C71",
    "base_tc": "47DD4613289EE07B5501B010D70E5226200BEA76FA0459BA8BD8F90376793C71",
    "pk_jp": "C54AF026314084D318002063010054348594E7AB099F2020B1D6B8EBB4A6E581",
    "pk_current": "6A7498B078AFB1AF796A0549C0A08E2FD50536D1EA73DF4C795AA8F671511CDB",
    "pk_sc": "3D21B2E733DF5C77F204E823F32938D05DADBAE8C325DA8002BF1D6309F2EC83",
    "pk_tc": "3D21B2E733DF5C77F204E823F32938D05DADBAE8C325DA8002BF1D6309F2EC83",
    "pk_en": "3D21B2E733DF5C77F204E823F32938D05DADBAE8C325DA8002BF1D6309F2EC83",
}

TERMINAL_GROUPS = {
    436: tuple(range(1743, 1750)),
    442: tuple(range(1750, 1757)),
    1144: tuple(range(1757, 1764)),
    448: tuple(range(1764, 1771)),
    454: tuple(range(1771, 1778)),
    460: tuple(range(1778, 1785)),
    466: tuple(range(1785, 1792)),
    472: tuple(range(1792, 1799)),
    478: tuple(range(1799, 1806)),
    484: tuple(range(1806, 1813)),
}
PK_ROOT_BY_BASE = {
    436: 442,
    442: 448,
    1144: 1156,
    448: 454,
    454: 460,
    460: 466,
    466: 472,
    472: 478,
    478: 484,
    484: 490,
}

CROSS_SEGMENT_SOURCE_JP = {
    1809: "いたしませぬ",
    1810: "しません",
    1811: "いたさぬ",
    1812: "せぬ",
}
CROSS_SEGMENT_CURRENT_KO = {
    1809: "하지 않사옵니다",
    1810: "하지 않습니다",
    1811: "하지 않겠다",
    1812: "하지 않다",
}
CROSS_SEGMENT_TRANSLATION_POLICY = {
    1809: "하지 않사옵니다",
    1810: "하지 않습니다",
    1811: "하지 않소",
    1812: "하지 않는다",
}

SEGMENT_JUMP_EDGE_SHA256 = {
    "base": "590FDCF2DD870852662F9937392D02850ACC09C7DB4DC6D2AD53A0ABCDB6A404",
    "pk": "68C845A1367F86B554300E8D651DEFDCFFC2B393D7C4E2C2FD340160E82150CE",
}
FULL_GROUP_JUMP_EDGE_SHA256 = {
    "base": "3FFEE6307C5D602DEE7DAD1AEB00C1F20ADC51D5D7881C94236FF81F2AE5E8CB",
    "pk": "0254165E8129920300817B05DCC75D68B87F1871242A6E6A99EAED36123DD67F",
}

ROOT_EVIDENCE = {
    436: {
        "pk_root": 442,
        "base_source": (
            10,
            "884866564CBD5892DFDDBDB45F7DCFC59853EE188C4CCDB0C0365718C5F60B2C",
        ),
        "base_current": (
            7,
            "2DF807FB1CDE357E3E2BE5BACFDD28E76031D1107110F361B19D1E40A78D45EA",
        ),
        "pk_source": (
            17,
            "766D0F67036C187219C8221AEF63EAC7F45829EAA0952CDB28618F3B9D8B79C0",
        ),
        "pk_current": (
            14,
            "05A4A34673B2163954257FCA8BDA47E53D7DC4DBCC479821E58ABEA9EBB72EEB",
        ),
    },
    442: {
        "pk_root": 448,
        "base_source": (
            0,
            "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        ),
        "base_current": (
            0,
            "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        ),
        "pk_source": (
            0,
            "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        ),
        "pk_current": (
            0,
            "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        ),
    },
    1144: {
        "pk_root": 1156,
        "base_source": (
            0,
            "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        ),
        "base_current": (
            0,
            "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        ),
        "pk_source": (
            0,
            "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        ),
        "pk_current": (
            0,
            "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        ),
    },
    448: {
        "pk_root": 454,
        "base_source": (
            0,
            "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        ),
        "base_current": (
            0,
            "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        ),
        "pk_source": (
            0,
            "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        ),
        "pk_current": (
            0,
            "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        ),
    },
    454: {
        "pk_root": 460,
        "base_source": (
            3,
            "10512DEBD717F91A304EB27913B46D03C6C5F24C56EAB8BCCD2220BC693A0C57",
        ),
        "base_current": (
            3,
            "10512DEBD717F91A304EB27913B46D03C6C5F24C56EAB8BCCD2220BC693A0C57",
        ),
        "pk_source": (
            3,
            "653D61FB291059125481FF5228AE1F7888C2D27701CA947E9934A468B6343A8D",
        ),
        "pk_current": (
            3,
            "653D61FB291059125481FF5228AE1F7888C2D27701CA947E9934A468B6343A8D",
        ),
    },
    460: {
        "pk_root": 466,
        "base_source": (
            89,
            "C2EC3D4B6F717DDA2B72FFD2304D982BFB82BBF5FC7642EFA29E6B06D29C064D",
        ),
        "base_current": (
            62,
            "C05333F7080B9F3A0CB2CCA398E8BE16ED7B8765E4C7A25EBEA1782675E3971C",
        ),
        "pk_source": (
            94,
            "C3737ECDC424A501928BB27769F38CF086E344D44DD2348AE80CE64A9707B476",
        ),
        "pk_current": (
            79,
            "EB19406F66B1CF25918A0C91E30B983E0BFEE125E7CBA9D6757EF0D5B6FAE398",
        ),
    },
    466: {
        "pk_root": 472,
        "base_source": (
            4,
            "CD229BE18BE18827B580D6F68BCCD89F1E223918084772F1E14905CC993CB8FC",
        ),
        "base_current": (
            2,
            "3C2C8BDA2021A3E239B97AE9EF3C0CA409C7BEBD0B1BBBEB98ABC030DB110E73",
        ),
        "pk_source": (
            6,
            "3BAE86BFF4AF1277E985ABF0A79AAB1F6B9148284D682D20BD919D151AFE2894",
        ),
        "pk_current": (
            4,
            "31D98018FD974890757C9AD830B7F3825F65585A9F9F80D86937F2ABCCD5120F",
        ),
    },
    472: {
        "pk_root": 478,
        "base_source": (
            2,
            "C8F869722E080B9E718DA6B789690339FA15B8F1D91CACA1D29A926BDEE375EB",
        ),
        "base_current": (
            2,
            "C8F869722E080B9E718DA6B789690339FA15B8F1D91CACA1D29A926BDEE375EB",
        ),
        "pk_source": (
            2,
            "6DA45537EAF4C0BCAECA21AA2B7B4A6CC5F055C6666C04A06856D56074DF02AC",
        ),
        "pk_current": (
            2,
            "6DA45537EAF4C0BCAECA21AA2B7B4A6CC5F055C6666C04A06856D56074DF02AC",
        ),
    },
    478: {
        "pk_root": 484,
        "base_source": (
            0,
            "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        ),
        "base_current": (
            0,
            "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        ),
        "pk_source": (
            0,
            "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        ),
        "pk_current": (
            0,
            "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
        ),
    },
    484: {
        "pk_root": 490,
        "base_source": (
            5,
            "9C8C3AC62F4D8197E2B3D1A540F1A14CB05DF34E10C37EA7A8A4AE5D37907C14",
        ),
        "base_current": (
            4,
            "DCF6F6EACA19EB56F9BECB45883E9966615AD3C2D08B16FDA84335F6AB278D85",
        ),
        "pk_source": (
            5,
            "69CAFB279692B5B6A855DD0D98A0DE0C52BE78C49B976EDD67EDF4E9513E7AAF",
        ),
        "pk_current": (
            4,
            "43AC4AF20923BF7D1B9260D5B164F790E3AE192806490E66423723E5130F9FF1",
        ),
    },
}

SOURCE_ONLY_FLATTENED_CALLS = {
    436: (
        "15:2195:1:0",
        "15:253:2:0",
        "6:4179:2:0",
    ),
    460: (
        "2:512:1:0",
        "2:519:2:0",
        "6:1438:1:0",
        "6:1439:1:0",
        "6:1440:1:0",
        "6:1441:1:0",
        "6:1442:1:0",
        "6:1443:1:0",
        "6:1444:1:0",
        "6:1445:1:0",
        "6:1446:1:0",
        "6:1447:1:0",
        "6:1448:1:0",
        "6:1449:1:0",
        "6:4186:1:0",
        "6:4188:1:0",
        "6:4189:1:0",
        "6:4192:1:0",
        "6:4195:1:0",
        "6:4196:1:0",
        "6:4197:1:0",
        "6:4198:1:0",
        "6:4392:2:0",
        "6:4393:2:0",
        "6:4394:2:0",
        "7:262:1:0",
        "8:396:1:0",
    ),
    466: (
        "6:3531:1:0",
        "6:4190:1:0",
    ),
    484: ("15:226:2:0",),
}
PK_SOURCE_ONLY_FLATTENED_CALLS = {
    442: (
        "15:2225:1:0",
        "15:256:2:0",
        "6:4209:2:0",
    ),
    466: (
        "2:526:1:0",
        "2:533:2:0",
        "6:4216:1:0",
        "6:4218:1:0",
        "6:4219:1:0",
        "6:4222:1:0",
        "6:4225:1:0",
        "6:4226:1:0",
        "6:4227:1:0",
        "6:4228:1:0",
        "6:4451:2:0",
        "6:4452:2:0",
        "6:4453:2:0",
        "7:266:1:0",
        "8:408:1:0",
    ),
    472: (
        "6:3538:1:0",
        "6:4220:1:0",
    ),
    490: ("15:229:2:0",),
}

CURRENT_CALLER_REWRITE_EXAMPLES = {
    436: {
        "6:4032:1": "caller already ends with complete 받자옵니다",
        "7:2416:2": "mixed clause requires predicate-specific assembly",
    },
    454: {
        "6:2169:2": "runtime root is shared inside a multi-fragment sentence",
    },
    460: {
        "6:2155:1": "물러가도록 하 stem needs a compatible terminal",
        "6:4337:3": "착수하면 is not compatible with a generic action terminal",
    },
    466: {
        "6:3511:1": "황공하기 그지없 stem needs a voiced-conjugation rewrite",
    },
    472: {
        "1:9:1": "겸손 stem assembles naturally only with a full prohibition",
        "6:4459:2": "current 할 수 있다 fragment needs caller restructuring",
    },
    484: {
        "6:3550:3": "잊지 않 stem cannot take a second full negative",
        "15:226:2": "source call was flattened in current Korean",
    },
}

BASIS = (
    "review_queue_base_msggame_B003_C_pristine_base_pc_jp_authoritative_"
    "block0_runtime_terminal_records1743_1808_exact_seven_literal_tuple_"
    "plus61_pk_semantic_mapping_after_pk_only_seven_record_insertion_"
    "base_pk_root_pair_closures_jp_current_sc_tc_exact_pk_en_empty_"
    "archive_digests_all_014a_incoming_edges_source_current_0143_root_"
    "call_coordinate_digests_source_only_flattening_registries_cross_"
    "segment_root484_records1809_1812_contract_action_prohibition_"
    "negative_continuative_negative_volitional_apology_request_and_"
    "register_matrices_runtime_caller_rewrite_pending_one_line_reverse_"
    "overlay_no_korean_build_authority"
)


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return PRIOR.literal_texts(records, key)


def gap_bytes(record: Any) -> tuple[bytes, ...]:
    return PRIOR.gap_bytes(record)


def root_call_sites(
    records: dict[tuple[int, int], Any],
    root: int,
) -> tuple[str, ...]:
    return tuple(
        f"{key[0]}:{key[1]}:{gap_id}:{match.start()}"
        for key in sorted(records)
        for gap_id, gap in enumerate(gap_bytes(records[key]))
        for match in PRIOR.PREVIOUS.MORPHOLOGY_COMMAND_RE.finditer(gap)
        if struct.unpack("<I", match.group(1))[0] == root
    )


def archive_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    return PRIOR.archive_records(prepared)


def incoming_edges(
    records: dict[tuple[int, int], Any],
    target_ids: set[int],
) -> list[list[int]]:
    return [
        [block_id, record_id, operand]
        for (block_id, record_id), record in sorted(records.items())
        for operand in PRIOR.PREVIOUS.operands(
            record.data,
            PRIOR.PREVIOUS.MORPHOLOGY_JUMP_RE,
        )
        if operand in target_ids
    ]


def digest_edges(edges: list[list[int]]) -> str:
    return hashlib.sha256(
        json.dumps(edges, separators=(",", ":")).encode("ascii")
    ).hexdigest().upper()


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
        key = (BLOCK_ID, record_id)
        mapped = (BLOCK_ID, record_id + 61)
        if (
            literal_texts(records_by_label["base_jp"], key)
            != (source_jp,)
            or literal_texts(records_by_label["base_current"], key)
            != (CROSS_SEGMENT_CURRENT_KO[record_id],)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} cross literal drifted: {key}"
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
    full_base_ids = {
        record_id
        for record_ids in TERMINAL_GROUPS.values()
        for record_id in record_ids
    }
    if full_base_ids != set(range(1743, 1813)):
        raise RuntimeError(f"segment {SEGMENT} full group universe drifted")

    for edition, offset in (("base", 0), ("pk", 61)):
        target_ids = {record_id + offset for record_id in RECORD_IDS}
        full_ids = {record_id + offset for record_id in full_base_ids}
        for corpus in ("jp", "current"):
            records = records_by_label[f"{edition}_{corpus}"]
            edges = incoming_edges(records, target_ids)
            if (
                len(edges) != len(RECORD_IDS)
                or {edge[2] for edge in edges} != target_ids
                or digest_edges(edges) != SEGMENT_JUMP_EDGE_SHA256[edition]
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {edition}_{corpus} "
                    "terminal edge drifted"
                )
            full_edges = incoming_edges(records, full_ids)
            if (
                len(full_edges) != len(full_ids)
                or {edge[2] for edge in full_edges} != full_ids
                or digest_edges(full_edges)
                != FULL_GROUP_JUMP_EDGE_SHA256[edition]
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {edition}_{corpus} "
                    "full-group edge drifted"
                )

    base_edges = GRAPH.graph_edges(records_by_label["base_jp"])
    pk_edges = GRAPH.graph_edges(records_by_label["pk_jp"])
    for base_root, base_record_ids in TERMINAL_GROUPS.items():
        pk_root = PK_ROOT_BY_BASE[base_root]
        if sorted(
            GRAPH.graph_closure(base_edges, base_root).intersection(
                full_base_ids
            )
        ) != list(base_record_ids):
            raise RuntimeError(
                f"segment {SEGMENT} Base closure drifted: {base_root}"
            )
        expected_pk_ids = {record_id + 61 for record_id in base_record_ids}
        if sorted(
            GRAPH.graph_closure(pk_edges, pk_root).intersection(
                {record_id + 61 for record_id in full_base_ids}
            )
        ) != sorted(expected_pk_ids):
            raise RuntimeError(
                f"segment {SEGMENT} PK closure drifted: {pk_root}"
            )

        evidence = ROOT_EVIDENCE[base_root]
        for edition, root, flattened in (
            (
                "base",
                base_root,
                SOURCE_ONLY_FLATTENED_CALLS.get(base_root, ()),
            ),
            (
                "pk",
                pk_root,
                PK_SOURCE_ONLY_FLATTENED_CALLS.get(pk_root, ()),
            ),
        ):
            source_sites = root_call_sites(
                records_by_label[f"{edition}_jp"],
                root,
            )
            current_sites = root_call_sites(
                records_by_label[f"{edition}_current"],
                root,
            )
            for corpus, sites in (
                ("source", source_sites),
                ("current", current_sites),
            ):
                expected_count, expected_sha256 = evidence[
                    f"{edition}_{corpus}"
                ]
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
            if set(source_sites) - set(current_sites) != set(flattened):
                raise RuntimeError(
                    f"segment {SEGMENT} {edition} source-only "
                    f"calls drifted: {root}"
                )
            if set(current_sites) - set(source_sites):
                raise RuntimeError(
                    f"segment {SEGMENT} {edition} current-only "
                    f"calls appeared: {root}"
                )

        current_coordinates = {
            site.rsplit(":", 1)[0]
            for site in root_call_sites(
                records_by_label["base_current"],
                base_root,
            )
        }
        examples = set(CURRENT_CALLER_REWRITE_EXAMPLES.get(base_root, {}))
        if not examples.issubset(
            current_coordinates
            | {
                site.rsplit(":", 1)[0]
                for site in SOURCE_ONLY_FLATTENED_CALLS.get(
                    base_root,
                    (),
                )
            }
        ):
            raise RuntimeError(
                f"segment {SEGMENT} caller example drifted: {base_root}"
            )


def assert_semantics(translations: dict[str, str]) -> None:
    if (
        translations != RAW_TRANSLATIONS
        or len(translations) != 66
        or set(EXPECTED_BASE_JP) != set(RECORD_IDS)
    ):
        raise RuntimeError(f"segment {SEGMENT} translation universe drifted")

    expected_groups = {
        436: (
            "합니다",
            "한다",
            "합니다",
            "하옵니다",
            "합니다",
            "합니다",
            "한다",
        ),
        442: (
            "하지 마세요",
            "하지 마라",
            "하지 말아 주십시오",
            "하지 마시옵소서",
            "하지 말아 주십시오",
            "하지 마시오",
            "하지 마라",
        ),
        1144: (
            "지 않고",
            "지 않고",
            "지 않은 채",
            "지 않고",
            "지 않은 채로",
            "지 않고",
            "지 않고",
        ),
        448: (
            "하지 않겠습니다",
            "하지 않으리",
            "하지 않겠사옵니다",
            "하지 않겠사옵니다",
            "하지 않겠습니다",
            "하지 않겠소",
            "하지 않으리",
        ),
        454: (
            "죄송합니다",
            "미안하오",
            "송구하옵니다",
            "송구하옵니다",
            "죄송합니다",
            "면목이 없습니다",
            "미안하오",
        ),
        460: (
            "합니다",
            "한다",
            "하옵니다",
            "하옵니다",
            "합니다",
            "하옵니다",
            "한다",
        ),
        466: (
            "합니다",
            "한다",
            "합니다",
            "하옵니다",
            "합니다",
            "합니다",
            "한다",
        ),
        472: (
            "하지 마시오",
            "하지 마라",
            "하지 마시오",
            "하지 마시옵소서",
            "하지 마시옵소서",
            "하지 말아 주시오",
            "하지 마라",
        ),
        478: (
            "해 주십시오",
            "하라",
            "해 주시옵소서",
            "해 주시오",
            "해 주십시오",
            "해 주시오",
            "하라",
        ),
    }
    for root, expected in expected_groups.items():
        record_ids = TERMINAL_GROUPS[root]
        if tuple(
            translations[f"0:{record_id}:0"]
            for record_id in record_ids
        ) != expected:
            raise RuntimeError(
                f"segment {SEGMENT} register matrix drifted: {root}"
            )
    if tuple(
        translations[f"0:{record_id}:0"]
        for record_id in range(1806, 1809)
    ) + tuple(
        CROSS_SEGMENT_TRANSLATION_POLICY[record_id]
        for record_id in range(1809, 1813)
    ) != (
        "하지 않습니다",
        "하지 않는다",
        "하지 않사옵니다",
        "하지 않사옵니다",
        "하지 않습니다",
        "하지 않소",
        "하지 않는다",
    ):
        raise RuntimeError(
            f"segment {SEGMENT} negative boundary matrix drifted"
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
        current_text = literal_texts(current, (BLOCK_ID, record_id))[0]
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
        if record_id in RECORD_IDS
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
        pk_root = PK_ROOT_BY_BASE[root]
        evidence = ROOT_EVIDENCE[root]
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
                    "pk_semantic_root": pk_root,
                    "base_record_id": record_id,
                    "pk_semantic_record_id": record_id + 61,
                    "automatic_space_inserted": False,
                    "full_terminal_record_ids": list(
                        TERMINAL_GROUPS[root]
                    ),
                    "pk_full_terminal_record_ids": [
                        value + 61 for value in TERMINAL_GROUPS[root]
                    ],
                    "source_call_count": evidence["base_source"][0],
                    "current_call_count": evidence["base_current"][0],
                    "pk_source_call_count": evidence["pk_source"][0],
                    "pk_current_call_count": evidence["pk_current"][0],
                    "source_only_flattened_calls": list(
                        SOURCE_ONLY_FLATTENED_CALLS.get(root, ())
                    ),
                    "pk_source_only_flattened_calls": list(
                        PK_SOURCE_ONLY_FLATTENED_CALLS.get(pk_root, ())
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
            (BLOCK_ID, int(coordinate.split(":")[1])),
        )[0]
        for coordinate, translation in translations.items()
    )
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B003_S1011",
                "queue": QUEUE_BATCH_ID,
                "source_literal_count": 66,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "changed_literal_count": changed,
                "base_pk_semantic_record_offset": 61,
                "base_pk_jp_current_sc_tc_literal_divergence_records": [],
                "base_pk_jp_current_sc_tc_gap_divergence_records": [],
                "pk_en_visible_records": [],
                "terminal_groups": {
                    str(root): list(record_ids)
                    for root, record_ids in TERMINAL_GROUPS.items()
                },
                "pk_root_by_base": PK_ROOT_BY_BASE,
                "cross_segment_translation_policy": (
                    CROSS_SEGMENT_TRANSLATION_POLICY
                ),
                "root_evidence": ROOT_EVIDENCE,
                "source_only_flattened_calls": (
                    SOURCE_ONLY_FLATTENED_CALLS
                ),
                "pk_source_only_flattened_calls": (
                    PK_SOURCE_ONLY_FLATTENED_CALLS
                ),
                "caller_rewrite_examples": (
                    CURRENT_CALLER_REWRITE_EXAMPLES
                ),
                "segment_jump_edge_sha256": (
                    SEGMENT_JUMP_EDGE_SHA256
                ),
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
