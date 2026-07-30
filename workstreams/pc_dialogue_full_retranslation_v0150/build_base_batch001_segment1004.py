#!/usr/bin/env python3
"""Build Base block-0 runtime-fragment segment 1004 decisions."""

from __future__ import annotations

import hashlib
import importlib.util
import re
import struct
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S1004.private.v1.jsonl"
)
SEGMENT = 1004
BLOCK_ID = 0
NONQUEUE_CONTROL_ONLY_RECORD_IDS = (
    1276,
    1278,
    1279,
    1287,
    1289,
    1290,
)
NONQUEUE_CONTROL_ONLY_RECORD_HEX = {
    1276: "024935050505",
    1278: "024934050505",
    1279: "024933050505",
    1287: "024A35050505",
    1289: "024A34050505",
    1290: "024A33050505",
}
RECORD_IDS = tuple(
    record_id
    for record_id in range(1270, 1343)
    if record_id not in NONQUEUE_CONTROL_ONLY_RECORD_IDS
)
PK_RECORD_MAP = {record_id: record_id + 54 for record_id in RECORD_IDS}


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s1004",
        ENGINE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENGINE = load_engine()
MORPHOLOGY_COMMAND_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)
MORPHOLOGY_JUMP_RE = re.compile(b"\x01\x4A(.{4})", re.DOTALL)

SAMA_RECORD_IDS = (
    1270,
    1272,
    1274,
    1281,
    1283,
    1285,
    1292,
    1294,
    1296,
)
TONO_RECORD_IDS = (
    1271,
    1273,
    1275,
    1282,
    1284,
    1286,
    1293,
    1295,
    1297,
)
ME_RECORD_IDS = (1277, 1280, 1288, 1291)

TRANSLATIONS_BY_RECORD: dict[int, str] = {
    **{record_id: "님" for record_id in SAMA_RECORD_IDS},
    **{record_id: "공" for record_id in TONO_RECORD_IDS},
    **{record_id: "놈" for record_id in ME_RECORD_IDS},
    1298: "으음……",
    1299: "음……",
    1300: "하하하",
    1301: "후후후",
    1302: "습니다",
    1303: "다",
    1304: "사옵니다",
    1305: "사옵니다",
    1306: "습니다",
    1307: "소",
    1308: "다",
    1309: "하다",
    1310: "하다",
    1311: "하옵니다",
    1312: "하옵니다",
    1313: "합니다",
    1314: "하오",
    1315: "하다",
    1316: "습니다",
    1317: "다",
    1318: "사옵니다",
    1319: "사옵니다",
    1320: "사옵니다",
    1321: "습니다",
    1322: "다",
    1323: "겠지요",
    1324: "겠지",
    1325: "겠사옵니다",
    1326: "겠사옵니다",
    1327: "사옵니다",
    1328: "습니다",
    1329: "겠지",
    1330: "으므로",
    1331: "기에",
    1332: "사오니",
    1333: "사오니",
    1334: "으니",
    1335: "으니",
    1336: "다면",
    1337: "합니다",
    1338: "한다",
    1339: "하옵니다",
    1340: "합니다",
    1341: "합니다",
    1342: "합니다",
}
TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}

EXPECTED_BASE_JP: dict[int, str] = {
    **{record_id: "様" for record_id in SAMA_RECORD_IDS},
    **{record_id: "殿" for record_id in TONO_RECORD_IDS},
    **{record_id: "め" for record_id in ME_RECORD_IDS},
    1298: "ううむ……",
    1299: "うーん……",
    1300: "はっはっは",
    1301: "うふふ",
    1302: "ありました",
    1303: "あった",
    1304: "ございました",
    1305: "ございました",
    1306: "ありました",
    1307: "ござった",
    1308: "あった",
    1309: "危うい",
    1310: "危うい",
    1311: "危のうございまする",
    1312: "危のうございまする",
    1313: "危のうございます",
    1314: "危のうござる",
    1315: "危うい",
    1316: "あります",
    1317: "ある",
    1318: "ございます",
    1319: "ございまする",
    1320: "ありまする",
    1321: "あります",
    1322: "ある",
    1323: "ありましょう",
    1324: "あろう",
    1325: "ございましょう",
    1326: "ござりましょう",
    1327: "ございます",
    1328: "あります",
    1329: "あろう",
    1330: "ありますので",
    1331: "あるため",
    1332: "ございますれば",
    1333: "ございますれば",
    1334: "ありますれば",
    1335: "ありますれば",
    1336: "あらば",
    1337: "申します",
    1338: "いう",
    1339: "申しまする",
    1340: "申します",
    1341: "申します",
    1342: "申します",
}
EXPECTED_PK_JP = {
    **EXPECTED_BASE_JP,
    1298: "ううむ…",
    1299: "うーん…",
    1327: "ございましょう",
    1328: "ありましょう",
    1336: "あるので",
}
BASE_PK_LITERAL_DIVERGENCE_RECORD_IDS = (1298, 1299, 1327, 1328, 1336)
BASE_PK_RAW_DIVERGENCE_RECORD_IDS = BASE_PK_LITERAL_DIVERGENCE_RECORD_IDS
BASE_PK_DIVERGENCE_EVIDENCE = {
    1298: {
        "base_jp": "ううむ……",
        "pk_jp": "ううむ…",
        "base_authoritative_ko": "으음……",
        "reason": "preserve Base two-mark project ellipsis",
    },
    1299: {
        "base_jp": "うーん……",
        "pk_jp": "うーん…",
        "base_authoritative_ko": "음……",
        "reason": "preserve Base two-mark project ellipsis",
    },
    1327: {
        "base_jp": "ございます",
        "pk_jp": "ございましょう",
        "base_authoritative_ko": "사옵니다",
        "reason": "Base present statement, not PK volitional",
    },
    1328: {
        "base_jp": "あります",
        "pk_jp": "ありましょう",
        "base_authoritative_ko": "습니다",
        "reason": "Base present statement, not PK volitional",
    },
    1336: {
        "base_jp": "あらば",
        "pk_jp": "あるので",
        "base_authoritative_ko": "다면",
        "reason": "Base conditional, not PK causal",
    },
}
PROJECT_ELLIPSIS_RECORD_IDS = (1298, 1299)
PK_EN_VISIBLE_RECORD_IDS = (
    1271,
    1273,
    1275,
    1282,
    1284,
    1286,
    1293,
    1295,
    1297,
    1298,
    1299,
    1300,
    1301,
)
HONORIFIC_SUFFIX_POLICY = {
    "様": {
        "translation": "님",
        "record_ids": SAMA_RECORD_IDS,
        "reason": "general respectful name suffix",
    },
    "殿": {
        "translation": "공",
        "record_ids": TONO_RECORD_IDS,
        "reason": (
            "historical personal honorific preserved distinctly from 様; "
            "국립국어원 분석 지침상 이름 뒤 공(公)은 별개 단위이므로 "
            "all no-space dynamic-name callers remain spacing-pending"
        ),
    },
    "め": {
        "translation": "놈",
        "record_ids": ME_RECORD_IDS,
        "reason": "hostile personal suffix",
    },
}
KOREAN_SPACING_EVIDENCE_URL = (
    "https://www.korean.go.kr/common/download.do"
    "?c_file_name=bdda5df5-1772-4ee2-8d3a-e31143cfe99a.pdf"
    "&file_path=reportData"
    "&o_file_name=2020년_어휘의미_말뭉치_연구_분석_사업_최종보고서.pdf"
)
TONO_SPACING_POLICY = {
    "automatic_space_inserted": False,
    "semantic_candidate": "공",
    "review": (
        "공(公)은 이름 뒤 별개 단위이므로 dynamic name-title 경계에 "
        "공백을 보강하고 뒤 조사까지 호출별로 재검토해야 함"
    ),
    "evidence_url": KOREAN_SPACING_EVIDENCE_URL,
}

ARCHIVE_DIGESTS = {
    "base_jp": "1B96AD8916E58E090B5C9D2F881A87D479DDBEC2677DB397A7CE75895C519DC6",
    "base_current": "FC6D4C4F2436182CCE32F85B6BE4DA96A78CA73E2324F2BEF44524FDA1D60F53",
    "base_sc": "8CFB9A9EA88F3D2FE0D1DCFF3BF44754228B2779758068A445E74C34C3C3D8AA",
    "base_tc": "8C3F3EB16B0181C5CD4C4180ED3D12BAAA3A3619B80535ECD695863CC4FF192B",
    "pk_jp": "2AD637A10B04BE05E4707AE2AEDA7134657E4F2195522111756974B6D7387E18",
    "pk_current": "865673BB768F0C82AF80E62B41D07D66D9538553D80B7FB7875CB9FC71C49868",
    "pk_sc": "A3EF20DC02879537C1FBA76A22E9D61BC803B782CEB76647C3ED8DA0BE361A73",
    "pk_tc": "51C213F96A336084E5D2B878A84515704361839F3E6483375F8ABF078D9AB5B1",
    "pk_en": "EADA159698D4DA1F62EA09D86CA7A4D3F722AD91E1933F519A8A25AB0687EF6C",
}

EXPECTED_GRAPH_EVIDENCE = {
    21: (
        (1270, 1271),
        20,
        "340DA0D26367F41D01AC968379D775FF4AECDCBC5F27B77B9D47202BB8DA9F31",
    ),
    29: (
        (1270, 1271),
        154,
        "9303B83E78B97B8EFFA0CFE85CE39BACBFD91A0B031DDA8CF5D2C91416B25135",
    ),
    34: (
        (1274, 1275),
        46,
        "AF21F7BF93848298DDBD7D9957001F4954C4D269FABBCB5DA6646056A57C3EE4",
    ),
    37: (
        (1270, 1271),
        2,
        "E6369B2523454C3F010F1CCE89309075D1A70A1EFDA7A207BCFC57AA28802C31",
    ),
    46: (
        (1277, 1281),
        6,
        "7B4BAF07B4C3DF4106E87037756BAAF614BF42173AF4FAC26FB7FC26CDC23A66",
    ),
    50: (
        (1285, 1286),
        12,
        "A71B1258A8723551119A9B7BCEBCB8969D43F8CD31EF6D83A19BAE9332BCEF21",
    ),
    68: (
        (1298, 1299),
        2,
        "8F312410E0F092C49845BCEE1804F694192673FE6C443F669152DF49C79D2941",
    ),
    69: (
        (1300, 1301),
        2,
        "90FF72ABBEA9CA673E6C7E904F9BB47AE3F0758DA87FAAA5C7ED29065E0BB650",
    ),
    70: (
        tuple(range(1302, 1309)),
        13,
        "97948EDF2EB2A6DB7C5886EBBBE5D3C788BD4B2673458B3E0CFEE618D1DA6A4C",
    ),
    76: (
        tuple(range(1309, 1316)),
        1,
        "3F17D868D19896ED622792E244AEC2DC4ED2077823871BC431BA8ABBE2296D19",
    ),
    82: (
        tuple(range(1316, 1323)),
        52,
        "E566F94597AC3A8B60C8AA13CA97F3E9FFBE83A4E9595A3FCE3FEDFEB3699155",
    ),
    88: (
        tuple(range(1323, 1330)),
        3,
        "DAC12FE57C1AA60ED43D4AFCF6333F5B326D3B0AAA318036D0728B339F9CB07E",
    ),
    94: (
        tuple(range(1330, 1337)),
        7,
        "DD03C679B43BDADE75C881C6BDC827727EF7E517A6EEDE496D32619CF1AD1CA2",
    ),
    100: (
        tuple(range(1337, 1343)),
        3,
        "661E6E73C25DDC687E2880B866A47C55403AC7295DBA07F6CFC8AE696DC36A70",
    ),
}
NO_OBSERVED_MORPHOLOGY_C_PATH_RECORD_IDS = (
    1272,
    1273,
    1280,
    1282,
    1283,
    1284,
    1288,
    1291,
    1292,
    1293,
    1294,
    1295,
    1296,
    1297,
)
LIVE_BOUND_SUFFIX_ROOTS = (70, 76, 82, 88, 94, 100)
EXPECTED_CURRENT_LIVE_ROOT_CALLS = {
    70: (
        13,
        "97948EDF2EB2A6DB7C5886EBBBE5D3C788BD4B2673458B3E0CFEE618D1DA6A4C",
    ),
    76: (
        1,
        "3F17D868D19896ED622792E244AEC2DC4ED2077823871BC431BA8ABBE2296D19",
    ),
    82: (
        45,
        "98F5A3C38D07742CC69A4B7CA4D59968A02FD1ED1B60ABD7AE4828B740ADCB94",
    ),
    88: (
        3,
        "DAC12FE57C1AA60ED43D4AFCF6333F5B326D3B0AAA318036D0728B339F9CB07E",
    ),
    94: (
        7,
        "DD03C679B43BDADE75C881C6BDC827727EF7E517A6EEDE496D32619CF1AD1CA2",
    ),
    100: (
        3,
        "661E6E73C25DDC687E2880B866A47C55403AC7295DBA07F6CFC8AE696DC36A70",
    ),
}
CURRENT_UPSTREAM_ONLY_ASSEMBLY_BLOCKERS = {
    70: {
        "6:3671:3": "fixed right `인가`",
        "8:265:1": "adjacent root 502 may emit sentence-final 여/다",
        "8:266:1": "fixed right `가`",
        "8:266:2": "adjacent root 502 may emit sentence-final 여/다",
        "8:288:4": "adjacent root 502 may emit sentence-final 여/다",
        "8:305:1": "adjacent root 274 emits 하지만/이",
        "8:327:1": "fixed right `이(가)`",
        "8:330:2": "fixed following noun requires an attributive form",
    },
    82: {
        "6:3533:3": "fixed right `가`",
        "15:1627:1": "adjacent root 718 emits 군",
        "15:1808:1": "fixed right `이(가)`",
    },
    88: {
        "9:3681:3": "fixed right `군`",
    },
    94: {
        "13:114:2": "fixed following clause has no separator",
        "13:125:2": "fixed following clause has no separator",
    },
    100: {
        "8:276:2": "fixed following `그러니` has no separator",
    },
}
CURRENT_BLOCKER_RECORD_SHA256 = {
    (6, 3533): "907CC316E708E0D92CEC6BF1A60FCF45DEBFE1A5775F3557EE34B8730FEE1EF6",
    (6, 3671): "541A0787B5D8058B59ED210AAD7350E6DCC8DF2837CDE4E76B83A621A5D05497",
    (8, 265): "5183C11C88374570AA15FB9B02F1C6BB4876EDE30E8F3BFC42EDEC62D45DFE64",
    (8, 266): "F9AE4C3A0890A76DD4D9C6F31C9B03A74055691D66B48080B96FB457560283A1",
    (8, 276): "A1E764368E0D2EFC287CE3116424639FBE435C647D2B932B79EBAC256AD8255D",
    (8, 288): "2B0511FCF139D7A7DC8F9F0702F55465253A34B0BB5C0BAB934E51F10F039B9F",
    (8, 305): "D56AFF2B95ABAAB045389160416A29D685566CAE6373AE7C7F2C4496FF4DD470",
    (8, 327): "21FCD16373F29D30DA88496B3D018ACDB019BD7EA0EA9C3B8D4FF8D549A74126",
    (8, 330): "3C8989403ACA667697077B202ED0512736B12728E4D1107FD6515EAFFEBE2A29",
    (9, 3681): "12F0FB27D72AD7294946DD6716ED1AA32B83FA9F4BADB2124EC483363E116726",
    (13, 114): "091E3EC11EBC7695E842051F6FB8D5868C8CD8ED55A6943F6C8B0486EC6E74E9",
    (13, 125): "97E47128069CECACC774A8C23BCFA22A0CE06C37D645B67FAEC5A043ACF8F997",
    (15, 1627): "736C4477D46D0CE4680186CC33F6FE56E91A1930FBF6C3100E314A37EC52B49B",
    (15, 1808): "363EFF14056E804A169D2751671888A23541EC40144AA6A5FE4B2CFA6A62F0E3",
}
SOURCE_ONLY_FLATTENED_ROOT_82_CALLS = (
    "2:246:1:0",
    "13:23:1:0",
    "13:55:1:0",
    "15:219:2:0",
    "15:245:2:0",
    "15:263:2:0",
    "15:2247:1:0",
)
SOURCE_ONLY_DOWNSTREAM_ROOT_DEPENDENCIES = {
    "15:219:2:0": 712,
    "15:245:2:0": 712,
    "15:263:2:0": 502,
}
ROOT_TERMINAL_RECORD_IDS = {
    70: tuple(range(1302, 1309)),
    76: tuple(range(1309, 1316)),
    82: tuple(range(1316, 1323)),
    88: tuple(range(1323, 1330)),
    94: tuple(range(1330, 1337)),
    100: tuple(range(1337, 1343)),
}
ROOT_ASSEMBLY_PLAN = {
    70: {
        "upstream": "consumer-specific past stem ending in 었",
        "example": "있었+습니다",
    },
    76: {
        "upstream": "위험",
        "example": "위험+하옵니다",
    },
    82: {
        "upstream": "있",
        "example": "있+사옵니다",
    },
    88: {
        "upstream": "있",
        "example": "있+겠사옵니다",
    },
    94: {
        "upstream": "있",
        "example": "있+사오니",
    },
    100: {
        "upstream": "말",
        "example": "말+하옵니다",
        "cross_segment_terminal": "0:1343:0 -> 한다 (S1005)",
    },
}
VOICE_SUFFIX_EVIDENCE = {
    70: {
        "ありました": "습니다",
        "あった": "다",
        "ございました": "사옵니다",
        "ござった": "소",
    },
    76: {
        "危うい": "하다",
        "危のうございまする": "하옵니다",
        "危のうございます": "합니다",
        "危のうござる": "하오",
    },
    82: {
        "あります": "습니다",
        "ある": "다",
        "ございます/ございまする/ありまする": "사옵니다",
    },
    88: {
        "ありましょう": "겠지요",
        "あろう": "겠지",
        "ございましょう/ござりましょう": "겠사옵니다",
        "ございます": "사옵니다",
        "あります": "습니다",
    },
    94: {
        "ありますので": "으므로",
        "あるため": "기에",
        "ございますれば": "사오니",
        "ありますれば": "으니",
        "あらば": "다면",
    },
    100: {
        "申します": "합니다",
        "いう": "한다",
        "申しまする": "하옵니다",
        "申す": "한다 (0:1343:0, S1005)",
    },
}
EXACT_REUSE_GROUPS = (
    SAMA_RECORD_IDS,
    TONO_RECORD_IDS,
    ME_RECORD_IDS,
    (1302, 1306),
    (1303, 1308),
    (1304, 1305),
    (1309, 1310, 1315),
    (1311, 1312),
    (1316, 1321, 1328),
    (1317, 1322),
    (1318, 1327),
    (1324, 1329),
    (1332, 1333),
    (1334, 1335),
    (1337, 1340, 1341, 1342),
)
AMBIGUOUS_FRAGMENT_GROUPS = {
    "tono_dynamic_name_spacing_pending": [
        f"0:{record_id}:0" for record_id in TONO_RECORD_IDS
    ],
    "honorific_alternate_table_entries_without_observed_C_path": [
        f"0:{record_id}:0"
        for record_id in NO_OBSERVED_MORPHOLOGY_C_PATH_RECORD_IDS
    ],
    "base_pair_vs_pk_single_ellipsis_hesitation": [
        "0:1298:0",
        "0:1299:0",
    ],
    "gozaimashita_copular_or_existential": ["0:1304:0", "0:1305:0"],
    "formal_archaic_existential_register": [
        "0:1318:0",
        "0:1319:0",
        "0:1320:0",
        "0:1325:0",
        "0:1326:0",
        "0:1327:0",
    ],
    "conditional_or_causal_reba_araba": [
        f"0:{record_id}:0" for record_id in range(1332, 1337)
    ],
    "mousu_as_speech_or_humble_action_auxiliary": [
        f"0:{record_id}:0" for record_id in range(1337, 1343)
    ],
    "upstream_stem_only_insufficient_live_callers": [
        coordinate
        for blockers in CURRENT_UPSTREAM_ONLY_ASSEMBLY_BLOCKERS.values()
        for coordinate in blockers
    ],
    "source_root_82_calls_flattened_in_current": list(
        SOURCE_ONLY_FLATTENED_ROOT_82_CALLS
    ),
}
BASIS = (
    "review_queue_base_msggame_B001_block0_1270_1342_pristine_base_pc_"
    "jp_sole_authority_runtime_honorific_laughter_and_morphology_fragment_"
    "table_with_explicit_base_to_pk_plus54_mapping_62_source_record_exact_"
    "five_jp_divergences_pk_context_only_base_sc_tc_and_pk_en_context_"
    "morphology_C_root_terminal_closure_use_count_and_coordinate_digest_"
    "guards_current_live_root_call_digests_upstream_bound_suffix_design_"
    "and_exact_downstream_or_fixed_right_boundary_blocker_registry_name_"
    "suffix_register_existential_conditional_humble_action_review_project_"
    "ellipsis_korean_go_kr_name_title_spacing_evidence_one_line_protected_"
    "skeleton_runtime_fragment_pending_no_korean_authority"
)


def record_gaps(record: Any) -> tuple[bytes, ...]:
    gaps: list[bytes] = []
    cursor = 0
    for literal in ENGINE.parse_record_literals(record):
        gaps.append(record.data[cursor : literal.marker_offset])
        cursor = literal.marker_end
    gaps.append(record.data[cursor:])
    return tuple(gaps)


def literal_texts(
    records: dict[tuple[int, int], Any],
    record_id: int,
) -> tuple[str, ...]:
    return tuple(
        literal.text
        for literal in ENGINE.parse_record_literals(
            records[(BLOCK_ID, record_id)]
        )
    )


def subset_digest(
    records: dict[tuple[int, int], Any],
    keys: tuple[tuple[int, int], ...],
) -> str:
    digest = hashlib.sha256()
    for block_id, record_id in keys:
        data = records[(block_id, record_id)].data
        digest.update(struct.pack("<III", block_id, record_id, len(data)))
        digest.update(data)
    return digest.hexdigest().upper()


def assert_archive_and_mapping(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    base_keys = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
    pk_keys = tuple(
        (BLOCK_ID, PK_RECORD_MAP[record_id]) for record_id in RECORD_IDS
    )
    for label, records in records_by_label.items():
        keys = pk_keys if label.startswith("pk_") else base_keys
        if subset_digest(records, keys) != ARCHIVE_DIGESTS[label]:
            raise RuntimeError(f"segment {SEGMENT} {label} corpus drifted")

    base_jp = records_by_label["base_jp"]
    base_current = records_by_label["base_current"]
    pk_jp = records_by_label["pk_jp"]
    literal_divergences: set[int] = set()
    raw_divergences: set[int] = set()
    pk_en_visible: set[int] = set()
    for record_id in RECORD_IDS:
        mapped = PK_RECORD_MAP[record_id]
        if literal_texts(base_jp, record_id) != (
            EXPECTED_BASE_JP[record_id],
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base JP drifted: {record_id}"
            )
        if literal_texts(pk_jp, mapped) != (
            EXPECTED_PK_JP[record_id],
        ):
            raise RuntimeError(
                f"segment {SEGMENT} PK JP drifted: {record_id}/{mapped}"
            )
        if (
            literal_texts(base_jp, record_id)
            != literal_texts(pk_jp, mapped)
        ):
            literal_divergences.add(record_id)
        if (
            base_jp[(BLOCK_ID, record_id)].data
            != pk_jp[(BLOCK_ID, mapped)].data
        ):
            raw_divergences.add(record_id)
        if (
            record_gaps(base_jp[(BLOCK_ID, record_id)])
            != record_gaps(base_current[(BLOCK_ID, record_id)])
            or record_gaps(base_jp[(BLOCK_ID, record_id)])
            != record_gaps(pk_jp[(BLOCK_ID, mapped)])
        ):
            raise RuntimeError(
                f"segment {SEGMENT} source/current/PK gap drifted: "
                f"{record_id}/{mapped}"
            )
        for language in ("sc", "tc"):
            base_context = records_by_label[f"base_{language}"]
            pk_context = records_by_label[f"pk_{language}"]
            if (
                literal_texts(base_context, record_id)
                != literal_texts(pk_context, mapped)
                or record_gaps(base_context[(BLOCK_ID, record_id)])
                != record_gaps(pk_context[(BLOCK_ID, mapped)])
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {language.upper()} mapping "
                    f"drifted: {record_id}/{mapped}"
                )
        pk_en_literals = literal_texts(
            records_by_label["pk_en"],
            mapped,
        )
        if any(
            ENGINE.is_visible_translation_candidate(text)
            for text in pk_en_literals
        ):
            pk_en_visible.add(record_id)

    if literal_divergences != set(BASE_PK_LITERAL_DIVERGENCE_RECORD_IDS):
        raise RuntimeError("segment 1004 Base/PK literal divergence drifted")
    if raw_divergences != set(BASE_PK_RAW_DIVERGENCE_RECORD_IDS):
        raise RuntimeError("segment 1004 Base/PK raw divergence drifted")
    if pk_en_visible != set(PK_EN_VISIBLE_RECORD_IDS):
        raise RuntimeError("segment 1004 PK EN visibility drifted")

    for record_id, expected_hex in (
        NONQUEUE_CONTROL_ONLY_RECORD_HEX.items()
    ):
        for label, records in records_by_label.items():
            actual_record_id = (
                record_id + 54
                if label.startswith("pk_")
                else record_id
            )
            record = records[(BLOCK_ID, actual_record_id)]
            if (
                record.data.hex().upper() != expected_hex
                or ENGINE.parse_record_literals(record)
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} nonqueue control-only "
                    f"record drifted: {label}/{actual_record_id}"
                )


def graph_closure(
    edges: dict[int, set[int]],
    root: int,
) -> set[int]:
    pending = [root]
    seen: set[int] = set()
    while pending:
        record_id = pending.pop()
        if record_id in seen:
            continue
        seen.add(record_id)
        pending.extend(edges.get(record_id, set()) - seen)
    return seen


def assert_graph_evidence(
    source_records: dict[tuple[int, int], Any],
) -> None:
    edges: dict[int, set[int]] = defaultdict(set)
    uses: dict[int, list[str]] = defaultdict(list)
    for key in sorted(source_records):
        record = source_records[key]
        if key[0] == BLOCK_ID:
            for match in MORPHOLOGY_JUMP_RE.finditer(record.data):
                edges[key[1]].add(struct.unpack("<I", match.group(1))[0])
        for gap_id, gap in enumerate(record_gaps(record)):
            for match in MORPHOLOGY_COMMAND_RE.finditer(gap):
                operand = struct.unpack("<I", match.group(1))[0]
                uses[operand].append(
                    f"{key[0]}:{key[1]}:{gap_id}:{match.start()}"
                )

    target_ids = set(RECORD_IDS)
    actual_roots = {
        root
        for root in uses
        if graph_closure(edges, root).intersection(target_ids)
    }
    if actual_roots != set(EXPECTED_GRAPH_EVIDENCE):
        raise RuntimeError("segment 1004 morphology root universe drifted")

    covered: set[int] = set()
    for root, (expected_targets, expected_count, expected_sha) in (
        EXPECTED_GRAPH_EVIDENCE.items()
    ):
        actual_targets = tuple(
            sorted(graph_closure(edges, root).intersection(target_ids))
        )
        actual_uses = uses[root]
        actual_sha = hashlib.sha256(
            "\n".join(actual_uses).encode("ascii")
        ).hexdigest().upper()
        if (
            actual_targets != expected_targets
            or len(actual_uses) != expected_count
            or actual_sha != expected_sha
        ):
            raise RuntimeError(
                f"segment {SEGMENT} morphology evidence drifted: {root}"
            )
        covered.update(actual_targets)
    if target_ids - covered != set(
        NO_OBSERVED_MORPHOLOGY_C_PATH_RECORD_IDS
    ):
        raise RuntimeError(
            "segment 1004 no-observed-C-path terminal universe drifted"
        )


def root_call_sites(
    records: dict[tuple[int, int], Any],
    root: int,
) -> tuple[str, ...]:
    return tuple(
        f"{key[0]}:{key[1]}:{gap_id}:{match.start()}"
        for key in sorted(records)
        for gap_id, gap in enumerate(record_gaps(records[key]))
        for match in MORPHOLOGY_COMMAND_RE.finditer(gap)
        if struct.unpack("<I", match.group(1))[0] == root
    )


def assert_live_assembly_evidence(
    source_records: dict[tuple[int, int], Any],
    current_records: dict[tuple[int, int], Any],
) -> None:
    if (
        set(ROOT_TERMINAL_RECORD_IDS)
        != set(LIVE_BOUND_SUFFIX_ROOTS)
        or set(ROOT_ASSEMBLY_PLAN) != set(LIVE_BOUND_SUFFIX_ROOTS)
        or set(EXPECTED_CURRENT_LIVE_ROOT_CALLS)
        != set(LIVE_BOUND_SUFFIX_ROOTS)
    ):
        raise RuntimeError(
            "segment 1004 live bound-suffix root universe drifted"
        )
    current_sites_by_root: dict[int, tuple[str, ...]] = {}
    for root, (expected_count, expected_sha256) in (
        EXPECTED_CURRENT_LIVE_ROOT_CALLS.items()
    ):
        sites = root_call_sites(current_records, root)
        actual_sha256 = hashlib.sha256(
            "\n".join(sites).encode("ascii")
        ).hexdigest().upper()
        if (
            len(sites) != expected_count
            or actual_sha256 != expected_sha256
        ):
            raise RuntimeError(
                f"segment {SEGMENT} current root calls drifted: {root}"
            )
        current_sites_by_root[root] = sites

    source_root_82 = set(root_call_sites(source_records, 82))
    current_root_82 = set(current_sites_by_root[82])
    if (
        source_root_82 - current_root_82
        != set(SOURCE_ONLY_FLATTENED_ROOT_82_CALLS)
        or current_root_82 - source_root_82
    ):
        raise RuntimeError(
            "segment 1004 source/current root 82 flattening drifted"
        )
    if not set(SOURCE_ONLY_DOWNSTREAM_ROOT_DEPENDENCIES).issubset(
        SOURCE_ONLY_FLATTENED_ROOT_82_CALLS
    ):
        raise RuntimeError(
            "segment 1004 source-only dependency universe drifted"
        )

    blocker_count = 0
    for root, blockers in (
        CURRENT_UPSTREAM_ONLY_ASSEMBLY_BLOCKERS.items()
    ):
        current_call_coordinates = {
            site.rsplit(":", 1)[0]
            for site in current_sites_by_root[root]
        }
        if not set(blockers).issubset(current_call_coordinates):
            raise RuntimeError(
                f"segment {SEGMENT} blocker call drifted: {root}"
            )
        blocker_count += len(blockers)
    if blocker_count != 15 or 76 in (
        CURRENT_UPSTREAM_ONLY_ASSEMBLY_BLOCKERS
    ):
        raise RuntimeError(
            "segment 1004 upstream-only blocker universe drifted"
        )
    for key, expected_sha256 in CURRENT_BLOCKER_RECORD_SHA256.items():
        actual_sha256 = hashlib.sha256(
            current_records[key].data
        ).hexdigest().upper()
        if actual_sha256 != expected_sha256:
            raise RuntimeError(
                f"segment {SEGMENT} blocker record drifted: {key}"
            )


def assert_translation_semantics() -> None:
    if (
        len(RECORD_IDS) != 67
        or set(TRANSLATIONS_BY_RECORD) != set(RECORD_IDS)
        or set(EXPECTED_BASE_JP) != set(RECORD_IDS)
        or set(EXPECTED_PK_JP) != set(RECORD_IDS)
    ):
        raise RuntimeError("segment 1004 coordinate universe drifted")
    if set(PK_RECORD_MAP.values()) != {
        record_id + 54 for record_id in RECORD_IDS
    }:
        raise RuntimeError("segment 1004 +54 PK mapping drifted")
    if set(BASE_PK_DIVERGENCE_EVIDENCE) != set(
        BASE_PK_LITERAL_DIVERGENCE_RECORD_IDS
    ):
        raise RuntimeError(
            "segment 1004 Base/PK divergence evidence drifted"
        )
    for record_id, evidence in BASE_PK_DIVERGENCE_EVIDENCE.items():
        if (
            evidence["base_jp"] != EXPECTED_BASE_JP[record_id]
            or evidence["pk_jp"] != EXPECTED_PK_JP[record_id]
            or evidence["base_authoritative_ko"]
            != TRANSLATIONS_BY_RECORD[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} divergence rationale drifted: "
                f"{record_id}"
            )
    for source_text, policy in HONORIFIC_SUFFIX_POLICY.items():
        for record_id in policy["record_ids"]:
            if (
                EXPECTED_BASE_JP[record_id] != source_text
                or TRANSLATIONS_BY_RECORD[record_id]
                != policy["translation"]
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} honorific policy drifted: "
                    f"{record_id}"
                )
    if set(VOICE_SUFFIX_EVIDENCE) != set(LIVE_BOUND_SUFFIX_ROOTS):
        raise RuntimeError("segment 1004 voice suffix evidence drifted")
    for reuse_group in EXACT_REUSE_GROUPS:
        if len(
            {TRANSLATIONS_BY_RECORD[record_id] for record_id in reuse_group}
        ) != 1:
            raise RuntimeError(
                f"segment {SEGMENT} exact Korean reuse drifted: "
                f"{reuse_group}"
            )
    for record_id, translation in TRANSLATIONS_BY_RECORD.items():
        coordinate = f"{BLOCK_ID}:{record_id}:0"
        if (
            "\r" in translation
            or "\n" in translation
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or "…" in translation.replace("……", "")
            or translation != translation.strip()
        ):
            raise RuntimeError(
                f"segment {SEGMENT} text residue/layout drifted: "
                f"{coordinate}"
            )
    for record_id in PROJECT_ELLIPSIS_RECORD_IDS:
        if (
            EXPECTED_BASE_JP[record_id].count("…") != 2
            or EXPECTED_PK_JP[record_id].count("…") != 1
            or TRANSLATIONS_BY_RECORD[record_id].count("…") != 2
        ):
            raise RuntimeError(
                f"segment {SEGMENT} ellipsis policy drifted: {record_id}"
            )
    if (
        TRANSLATIONS_BY_RECORD[1271] != "공"
        or TRANSLATIONS_BY_RECORD[1299] != "음……"
        or TRANSLATIONS_BY_RECORD[1311] != "하옵니다"
        or TRANSLATIONS_BY_RECORD[1313] != "합니다"
        or TRANSLATIONS_BY_RECORD[1332] != "사오니"
        or TRANSLATIONS_BY_RECORD[1337] != "합니다"
        or TRANSLATIONS_BY_RECORD[1339] != "하옵니다"
    ):
        raise RuntimeError("segment 1004 register/assembly choices drifted")
    expected_compositions = {
        70: {
            "있었습니다",
            "있었다",
            "있었사옵니다",
            "있었소",
        },
        76: {
            "위험하다",
            "위험하옵니다",
            "위험합니다",
            "위험하오",
        },
        82: {"있습니다", "있다", "있사옵니다"},
        88: {
            "있겠지요",
            "있겠지",
            "있겠사옵니다",
            "있사옵니다",
            "있습니다",
        },
        94: {
            "있으므로",
            "있기에",
            "있사오니",
            "있으니",
            "있다면",
        },
        100: {"말합니다", "말한다", "말하옵니다"},
    }
    upstream_by_root = {
        70: "있었",
        76: "위험",
        82: "있",
        88: "있",
        94: "있",
        100: "말",
    }
    for root, record_ids in ROOT_TERMINAL_RECORD_IDS.items():
        actual = {
            upstream_by_root[root] + TRANSLATIONS_BY_RECORD[record_id]
            for record_id in record_ids
        }
        if actual != expected_compositions[root]:
            raise RuntimeError(
                f"segment {SEGMENT} bound suffix composition drifted: "
                f"{root}"
            )


def build_rows() -> tuple[
    Any,
    dict[str, str],
    list[dict[str, object]],
    bytes,
]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    base = prepared.resources["base_msggame"]
    pk = prepared.resources["pk_msggame"]
    archives = {
        "base_jp": base.pristine_archive,
        "base_current": base.current_archive,
        "base_sc": base.context_archives["SC"],
        "base_tc": base.context_archives["TC"],
        "pk_jp": pk.pristine_archive,
        "pk_current": pk.current_archive,
        "pk_sc": pk.context_archives["SC"],
        "pk_tc": pk.context_archives["TC"],
        "pk_en": pk.context_archives["EN"],
    }
    records_by_label = {
        label: ENGINE.archive_records(archive)
        for label, archive in archives.items()
    }
    assert_archive_and_mapping(records_by_label)
    assert_graph_evidence(records_by_label["base_jp"])
    assert_live_assembly_evidence(
        records_by_label["base_jp"],
        records_by_label["base_current"],
    )
    assert_translation_semantics()

    current_records = records_by_label["base_current"]
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        literals = ENGINE.parse_record_literals(
            current_records[(block_id, record_id)]
        )
        if (
            len(literals) != 1
            or literal_id != 0
            or not ENGINE.is_visible_translation_candidate(
                literals[literal_id].text
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} current target drifted: {coordinate}"
            )
        current_signature = ENGINE.protected_signature(
            literals[literal_id].text
        )
        translation_signature = ENGINE.protected_signature(translation)
        for field in (
            "non_layout_controls",
            "leading_whitespace",
            "trailing_whitespace",
        ):
            if translation_signature[field] != current_signature[field]:
                raise RuntimeError(
                    f"segment {SEGMENT} protected signature drifted: "
                    f"{coordinate}/{field}"
                )
        target = prepared.visible_targets.get(
            ("base_msggame", block_id, record_id, literal_id)
        )
        if target is None:
            raise RuntimeError(
                f"segment {SEGMENT} target absent: {coordinate}"
            )
        row: dict[str, object] = {
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
        }
        root = next(
            (
                candidate_root
                for candidate_root, record_ids in (
                    ROOT_TERMINAL_RECORD_IDS.items()
                )
                if record_id in record_ids
            ),
            None,
        )
        if root is not None:
            row["runtime_assembly_evidence"] = {
                "root": root,
                "automatic_space_inserted": False,
                "source_call_count": EXPECTED_GRAPH_EVIDENCE[root][1],
                "current_live_call_count": (
                    EXPECTED_CURRENT_LIVE_ROOT_CALLS[root][0]
                ),
                "assembly_plan": ROOT_ASSEMBLY_PLAN[root],
                "upstream_stem_only_sufficient_for_all_live_calls": (
                    root
                    not in CURRENT_UPSTREAM_ONLY_ASSEMBLY_BLOCKERS
                ),
                "downstream_or_fixed_right_blockers": list(
                    CURRENT_UPSTREAM_ONLY_ASSEMBLY_BLOCKERS.get(
                        root,
                        {},
                    )
                ),
            }
            if root == 82:
                row["runtime_assembly_evidence"][
                    "source_calls_flattened_in_current"
                ] = list(SOURCE_ONLY_FLATTENED_ROOT_82_CALLS)
        if record_id in TONO_RECORD_IDS:
            row["honorific_spacing_evidence"] = TONO_SPACING_POLICY
        rows.append(row)

    replacements = {
        tuple(int(value) for value in coordinate.split(":")): translation
        for coordinate, translation in TRANSLATIONS.items()
    }
    candidate = ENGINE.rebuild_packed_with_literals(
        base.current_blob,
        replacements,
    )
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    target_keys = {(BLOCK_ID, record_id) for record_id in RECORD_IDS}
    if len(candidate_records) != len(current_records):
        raise RuntimeError("segment 1004 candidate record count drifted")
    for key, current_record in current_records.items():
        candidate_record = candidate_records[key]
        if key not in target_keys:
            if candidate_record.data != current_record.data:
                raise RuntimeError(
                    f"segment {SEGMENT} outside-scope drifted: {key}"
                )
            continue
        if (
            record_gaps(candidate_record) != record_gaps(current_record)
            or literal_texts(candidate_records, key[1])
            != (TRANSLATIONS_BY_RECORD[key[1]],)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} target skeleton drifted: {key}"
            )

    reverse_replacements = {
        (BLOCK_ID, record_id, 0): literal_texts(
            current_records,
            record_id,
        )[0]
        for record_id in RECORD_IDS
    }
    reversed_blob = ENGINE.rebuild_packed_with_literals(
        candidate,
        reverse_replacements,
    )
    if reversed_blob != base.current_blob:
        raise RuntimeError("segment 1004 reverse overlay drifted")
    return prepared, TRANSLATIONS, rows, candidate


def main() -> int:
    prepared, translations, rows, candidate = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(rows) != 67 or len(validated) != len(translations):
        raise RuntimeError("segment 1004 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 1004 runtime/authority flags drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S1004",
                "source_literal_count": 67,
                "decision_count": len(rows),
                "nonqueue_control_only_record_count": len(
                    NONQUEUE_CONTROL_ONLY_RECORD_IDS
                ),
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "explicit_pk_mapping_offset": 54,
                "base_pk_raw_exact_records": (
                    len(RECORD_IDS)
                    - len(BASE_PK_RAW_DIVERGENCE_RECORD_IDS)
                ),
                "base_pk_jp_literal_divergence_records": list(
                    BASE_PK_LITERAL_DIVERGENCE_RECORD_IDS
                ),
                "base_pk_divergence_evidence": (
                    BASE_PK_DIVERGENCE_EVIDENCE
                ),
                "base_pk_gap_divergence_records": [],
                "honorific_suffix_policy": HONORIFIC_SUFFIX_POLICY,
                "tono_spacing_policy": TONO_SPACING_POLICY,
                "morphology_graph_root_count": len(
                    EXPECTED_GRAPH_EVIDENCE
                ),
                "morphology_graph_external_use_count": sum(
                    evidence[1]
                    for evidence in EXPECTED_GRAPH_EVIDENCE.values()
                ),
                "current_live_bound_suffix_root_calls": {
                    str(root): evidence[0]
                    for root, evidence in (
                        EXPECTED_CURRENT_LIVE_ROOT_CALLS.items()
                    )
                },
                "current_live_bound_suffix_call_count": sum(
                    evidence[0]
                    for evidence in (
                        EXPECTED_CURRENT_LIVE_ROOT_CALLS.values()
                    )
                ),
                "upstream_stem_only_sufficient_for_all_live_calls": False,
                "upstream_stem_only_blocked_live_call_count": sum(
                    len(blockers)
                    for blockers in (
                        CURRENT_UPSTREAM_ONLY_ASSEMBLY_BLOCKERS.values()
                    )
                ),
                "upstream_stem_only_blockers": (
                    CURRENT_UPSTREAM_ONLY_ASSEMBLY_BLOCKERS
                ),
                "source_root_82_calls_flattened_in_current": list(
                    SOURCE_ONLY_FLATTENED_ROOT_82_CALLS
                ),
                "source_only_downstream_root_dependencies": (
                    SOURCE_ONLY_DOWNSTREAM_ROOT_DEPENDENCIES
                ),
                "root_assembly_plan": ROOT_ASSEMBLY_PLAN,
                "voice_suffix_evidence": VOICE_SUFFIX_EVIDENCE,
                "no_observed_C_path_records": list(
                    NO_OBSERVED_MORPHOLOGY_C_PATH_RECORD_IDS
                ),
                "ellipsis_coordinates": [
                    f"0:{record_id}:0"
                    for record_id in PROJECT_ELLIPSIS_RECORD_IDS
                ],
                "ambiguous_fragment_groups": AMBIGUOUS_FRAGMENT_GROUPS,
                "line_distribution": {"1": len(rows)},
                "record_count": 19152,
                "outside_scope_records_exact": True,
                "nonqueue_control_only_records_exact": True,
                "target_runtime_skeleton_exact": True,
                "reverse_overlay_exact": True,
                "candidate_sha256": hashlib.sha256(
                    candidate
                ).hexdigest().upper(),
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
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
