#!/usr/bin/env python3
"""Build PK block-0 runtime-fragment segment 1025 decisions."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import struct
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
ENGINE_PATH = WORKSTREAM / "build_pc_dialogue_full_retranslation_v0150.py"
QUEUE_PATH = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "review_queue.private.v1.jsonl"
)
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B001_S1025.private.v1.jsonl"
)
BASE_DECISION_PATHS = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S1004.private.v1.jsonl",
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S1005.private.v1.jsonl",
)

SEGMENT = 1025
QUEUE_BATCH_ID = "pk_msggame-B001"
BLOCK_ID = 0
QUEUE_ZERO_BASED_START = 67
QUEUE_ZERO_BASED_STOP = 134
NONQUEUE_CONTROL_ONLY_RECORD_IDS = (
    1330,
    1332,
    1333,
    1341,
    1343,
    1344,
)
NONQUEUE_CONTROL_ONLY_RECORD_HEX = {
    1330: "024935050505",
    1332: "024934050505",
    1333: "024933050505",
    1341: "024A35050505",
    1343: "024A34050505",
    1344: "024A33050505",
}
RECORD_IDS = tuple(
    record_id
    for record_id in range(1324, 1397)
    if record_id not in NONQUEUE_CONTROL_ONLY_RECORD_IDS
)
RIGHT_BOUNDARY_RECORD_ID = 1397
FULL_REVERSE_SEARCH_RECORD_IDS = tuple(range(1324, 1398))


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_engine_s1025",
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
    1324,
    1326,
    1328,
    1335,
    1337,
    1339,
    1346,
    1348,
    1350,
)
TONO_RECORD_IDS = (
    1325,
    1327,
    1329,
    1336,
    1338,
    1340,
    1347,
    1349,
    1351,
)
ME_RECORD_IDS = (1331, 1334, 1342, 1345)

TRANSLATIONS_BY_RECORD: dict[int, str] = {
    **{record_id: "님" for record_id in SAMA_RECORD_IDS},
    **{record_id: "공" for record_id in TONO_RECORD_IDS},
    **{record_id: "놈" for record_id in ME_RECORD_IDS},
    1352: "으음……",
    1353: "음……",
    1354: "하하하",
    1355: "후후후",
    1356: "습니다",
    1357: "다",
    1358: "사옵니다",
    1359: "사옵니다",
    1360: "습니다",
    1361: "소",
    1362: "다",
    1363: "하다",
    1364: "하다",
    1365: "하옵니다",
    1366: "하옵니다",
    1367: "합니다",
    1368: "하오",
    1369: "하다",
    1370: "습니다",
    1371: "다",
    1372: "사옵니다",
    1373: "사옵니다",
    1374: "사옵니다",
    1375: "습니다",
    1376: "다",
    1377: "겠지요",
    1378: "겠지",
    1379: "겠사옵니다",
    1380: "겠사옵니다",
    1381: "겠사옵니다",
    1382: "겠지요",
    1383: "겠지",
    1384: "으므로",
    1385: "기에",
    1386: "사오니",
    1387: "사오니",
    1388: "으니",
    1389: "으니",
    1390: "으므로",
    1391: "합니다",
    1392: "한다",
    1393: "하옵니다",
    1394: "합니다",
    1395: "합니다",
    1396: "합니다",
}
TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": TRANSLATIONS_BY_RECORD[record_id]
    for record_id in RECORD_IDS
}
RIGHT_BOUNDARY_POLICY = {
    100: (
        "합니다",
        "한다",
        "하옵니다",
        "합니다",
        "합니다",
        "합니다",
        "한다",
    )
}

EXPECTED_PK_JP: dict[int, str] = {
    **{record_id: "様" for record_id in SAMA_RECORD_IDS},
    **{record_id: "殿" for record_id in TONO_RECORD_IDS},
    **{record_id: "め" for record_id in ME_RECORD_IDS},
    1352: "ううむ…",
    1353: "うーん…",
    1354: "はっはっは",
    1355: "うふふ",
    1356: "ありました",
    1357: "あった",
    1358: "ございました",
    1359: "ございました",
    1360: "ありました",
    1361: "ござった",
    1362: "あった",
    1363: "危うい",
    1364: "危うい",
    1365: "危のうございまする",
    1366: "危のうございまする",
    1367: "危のうございます",
    1368: "危のうござる",
    1369: "危うい",
    1370: "あります",
    1371: "ある",
    1372: "ございます",
    1373: "ございまする",
    1374: "ありまする",
    1375: "あります",
    1376: "ある",
    1377: "ありましょう",
    1378: "あろう",
    1379: "ございましょう",
    1380: "ござりましょう",
    1381: "ございましょう",
    1382: "ありましょう",
    1383: "あろう",
    1384: "ありますので",
    1385: "あるため",
    1386: "ございますれば",
    1387: "ございますれば",
    1388: "ありますれば",
    1389: "ありますれば",
    1390: "あるので",
    1391: "申します",
    1392: "いう",
    1393: "申しまする",
    1394: "申します",
    1395: "申します",
    1396: "申します",
    1397: "申す",
}

# These are semantic equivalences used only to discover the completed Base
# counterpart. Translation authority remains the pristine PK Japanese above.
APPROVED_BASE_SOURCE_EQUIVALENCE = {
    1352: "ううむ……",
    1353: "うーん……",
    1381: "ございます",
    1382: "あります",
    1390: "あらば",
}
PK_TRANSLATION_DIVERGENCE_FROM_BASE = {
    1381: {
        "base_translation": "사옵니다",
        "pk_translation": "겠사옵니다",
        "reason": "PK ございましょう is conjectural, unlike Base ございます",
    },
    1382: {
        "base_translation": "습니다",
        "pk_translation": "겠지요",
        "reason": "PK ありましょう is conjectural, unlike Base あります",
    },
    1390: {
        "base_translation": "다면",
        "pk_translation": "으므로",
        "reason": "PK あるので is causal, unlike Base あらば",
    },
}

HONORIFIC_SUFFIX_POLICY = {
    "様": {
        "translation": "님",
        "record_ids": SAMA_RECORD_IDS,
        "reason": "general respectful dynamic-name suffix",
    },
    "殿": {
        "translation": "공",
        "record_ids": TONO_RECORD_IDS,
        "reason": "historical personal honorific distinct from 様",
    },
    "め": {
        "translation": "놈",
        "record_ids": ME_RECORD_IDS,
        "reason": "hostile personal suffix",
    },
}
TONO_SPACING_POLICY = {
    "automatic_space_inserted": False,
    "semantic_candidate": "공",
    "caller_rewrite_required": True,
    "review": "dynamic name-title 경계의 공백과 뒤 조사를 호출별로 보강",
}

ROOT_TERMINAL_RECORD_IDS = {
    70: tuple(range(1356, 1363)),
    76: tuple(range(1363, 1370)),
    82: tuple(range(1370, 1377)),
    88: tuple(range(1377, 1384)),
    94: tuple(range(1384, 1391)),
    100: tuple(range(1391, 1398)),
}
ROOT_ASSEMBLY_PLAN = {
    70: {"upstream": "consumer-specific past stem ending in 었", "example": "있었+습니다"},
    76: {"upstream": "위험", "example": "위험+하옵니다"},
    82: {"upstream": "있", "example": "있+사옵니다"},
    88: {"upstream": "있", "example": "있+겠사옵니다"},
    94: {"upstream": "있", "example": "있+사오니/으므로"},
    100: {
        "upstream": "말",
        "example": "말+하옵니다",
        "cross_segment_terminal": "0:1397:0 -> 한다 (S1026)",
    },
}
EXPECTED_COMPOSITIONS = {
    70: {"있었습니다", "있었다", "있었사옵니다", "있었소"},
    76: {"위험하다", "위험하옵니다", "위험합니다", "위험하오"},
    82: {"있습니다", "있다", "있사옵니다"},
    88: {"있겠지요", "있겠지", "있겠사옵니다"},
    94: {"있으므로", "있기에", "있사오니", "있으니"},
    100: {"말합니다", "말한다", "말하옵니다"},
}

EXPECTED_ROOT_TARGETS = {
    21: (1324, 1325),
    29: (1324, 1325),
    34: (1328, 1329),
    37: (1324, 1325),
    46: (1330, 1331, 1335),
    50: (1333, 1339, 1340),
    68: (1352, 1353),
    69: (1354, 1355),
    **ROOT_TERMINAL_RECORD_IDS,
}
NO_OBSERVED_0143_PATH_RECORD_IDS = (
    1326,
    1327,
    1334,
    1336,
    1337,
    1338,
    1342,
    1345,
    1346,
    1347,
    1348,
    1349,
    1350,
    1351,
)

# (source calls, source call SHA, source fixed, source fixed SHA),
# (current calls, current call SHA, current fixed, current fixed SHA),
# (source-only calls, source-only SHA, current-only calls, current-only SHA).
EXPECTED_CALL_EVIDENCE = {
    21: ((20, "4D0C5EC90EA819A07A46CF944020C83BD7402C02D454BD476C5D87A76C68B7B2", 20, "A1A468F1F09C76435AFE9499B1B5CAE5F689F5DCD58D8DF519FB20C5888BED48"), (20, "4D0C5EC90EA819A07A46CF944020C83BD7402C02D454BD476C5D87A76C68B7B2", 20, "A1A468F1F09C76435AFE9499B1B5CAE5F689F5DCD58D8DF519FB20C5888BED48"), (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945")),
    29: ((171, "B512AB79B7E9D797CC7CCC955733D6520EE1FBFA9D9379EEE0FE2F4B24219B71", 153, "E0AEBCAC94137AB645702EC52FE4EDD15FFEC412AC7A44C376272DD82E23C91C"), (171, "B512AB79B7E9D797CC7CCC955733D6520EE1FBFA9D9379EEE0FE2F4B24219B71", 152, "2E5CA18598D1AF7912508F436E12EE7A42325D59D9D31D4F09FB6CD05903AA32"), (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945")),
    34: ((47, "EF57C30BDADAE7349AA60388395690E5869422A567BD4C717FAF76EFCC6AB634", 47, "80E9FA160FA6B189413CC2C88FA37174EE3B1928281E69DEF9035028CE8B67CD"), (47, "EF57C30BDADAE7349AA60388395690E5869422A567BD4C717FAF76EFCC6AB634", 45, "602DEC5F3E84267152DFAD4D39C98A2D271FD49829C2A1CB6C25B3E7B0672820"), (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945")),
    37: ((2, "1A990A740FA9E021555CC34DCAAF817A33781F35CDCF312C4B6177DD3957720C", 2, "0BCD8252796F399424EEAE2E6626F04DF4A41B18419D50526B292BED6F9228BA"), (2, "1A990A740FA9E021555CC34DCAAF817A33781F35CDCF312C4B6177DD3957720C", 2, "0BCD8252796F399424EEAE2E6626F04DF4A41B18419D50526B292BED6F9228BA"), (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945")),
    46: ((6, "EF7A7FEF2D30E5C58E70102EC9217772113EB43DB3BB8881B854723A4CF1BB56", 6, "C6FB81857FAAD13215BEFCABA8D331A0C369EAF166E6FB013C4D914C9D33B018"), (6, "EF7A7FEF2D30E5C58E70102EC9217772113EB43DB3BB8881B854723A4CF1BB56", 6, "C6FB81857FAAD13215BEFCABA8D331A0C369EAF166E6FB013C4D914C9D33B018"), (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945")),
    50: ((12, "01F5CE68B87AFA4B821FF09AAABB08DDC26CF41CFC25C0D000A63E548CFDC521", 11, "0FA818F520AA28D19F0BE70FF3098C60F4A371E804AA3E97CD8D5E3D314C5BF8"), (12, "01F5CE68B87AFA4B821FF09AAABB08DDC26CF41CFC25C0D000A63E548CFDC521", 11, "0FA818F520AA28D19F0BE70FF3098C60F4A371E804AA3E97CD8D5E3D314C5BF8"), (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945")),
    68: ((3, "8874EBE6ED5ADA6FB6D1F9EA1FBE27D3355D0CA88C62FB86C19F4D8695A3B248", 1, "029197796336B501A238E15FBAD01865DAD22E0DD7F1843727117EC60D1308C5"), (3, "8874EBE6ED5ADA6FB6D1F9EA1FBE27D3355D0CA88C62FB86C19F4D8695A3B248", 1, "029197796336B501A238E15FBAD01865DAD22E0DD7F1843727117EC60D1308C5"), (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945")),
    69: ((4, "1C2B421F14AC1A0EEBA117293D92CD99C83A8789323489503FFA0DD40F2D0CDF", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"), (3, "D6A76D397C17D32CC7989994E1F0E44D22AF78F825AD78DA425FC32998AE919D", 1, "5ECD9CE7F41E3B3806D05BF0F26EB056C4295B0663F3B50FA4707F47F01CD1A7"), (1, "EF9A8F246155839946AE279036EF79F84871D3C42060B3AEDEFFB5CC75F47B12", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945")),
    70: ((13, "2CC2D48F938EDA627AFEBB027D7F17293211E69204D9296FD59C2AD33A1A913F", 8, "FA7282DD564B9ADC16F4D5101465871C4F33884EF66D1220ED0E6596F38E452F"), (13, "2CC2D48F938EDA627AFEBB027D7F17293211E69204D9296FD59C2AD33A1A913F", 8, "FA7282DD564B9ADC16F4D5101465871C4F33884EF66D1220ED0E6596F38E452F"), (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945")),
    76: ((1, "F86364F864794206865DFE5273763F9D482D0A771AD8576761C3E2A691D145FF", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"), (1, "F86364F864794206865DFE5273763F9D482D0A771AD8576761C3E2A691D145FF", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"), (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945")),
    82: ((66, "07F81FAF6D701199CCE48466BFB3ED3D9674BFBAC4FA9EF20C908894EF280CFC", 7, "D5910E14E3E3EEE0B632A16DD19A614161A4E08E593E5F57B20A540B143C9CB7"), (58, "8E33E03623C60E1C352E60F39DC3F1969CA6BDA8CD3A5AF30CC02ACE8AE7AA80", 4, "F7F6B91E1B80277268861BAB3B5FAF3A2067353E839C5EEF32AA4929F3838240"), (8, "D6F7E84FC456D30B41E3BCCE979468927A5F0C8F3558E3EC24C9E2AD6DB2DD53", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945")),
    88: ((4, "3AEC08480869C352D9F5F9F99CFA33A9A718561F1ED7CDE2CF29E1B56763BB92", 1, "C4DF8EE60A1BA0A8BE09AB903C467921FC18622D5303F638A3B4D5E5AE4F596C"), (4, "3AEC08480869C352D9F5F9F99CFA33A9A718561F1ED7CDE2CF29E1B56763BB92", 1, "C4DF8EE60A1BA0A8BE09AB903C467921FC18622D5303F638A3B4D5E5AE4F596C"), (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945")),
    94: ((7, "FFD3D981E83916B5FD053595FC429EDAB3E84C0060CF2D6F0168A6B58D2955E8", 2, "1817CB11CC55281FF2B8177B8C4230D276ACF11E09021C3F118DCD8538FBE401"), (7, "FFD3D981E83916B5FD053595FC429EDAB3E84C0060CF2D6F0168A6B58D2955E8", 2, "1817CB11CC55281FF2B8177B8C4230D276ACF11E09021C3F118DCD8538FBE401"), (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945")),
    100: ((3, "54F90C508C2C169EB0E621151B9FBDDE3CDB90BAE36734DA391853E5C60D2DF5", 1, "5555D711360118E541B7518FB2CE584ECC1C0EDB94E36BF235AB466187B5368B"), (3, "54F90C508C2C169EB0E621151B9FBDDE3CDB90BAE36734DA391853E5C60D2DF5", 1, "5555D711360118E541B7518FB2CE584ECC1C0EDB94E36BF235AB466187B5368B"), (0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945", 0, "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945")),
}

ARCHIVE_DIGESTS = {
    "pk_jp": "C1C751B25AC4D59C06035FCA6C0FA2D441BB0AD1195B5D6733781E6AAA80E506",
    "pk_current": "8235BDAF400E8116571588A247BC18DEE9B0CC1FC7AB2A8815E5F082C7C5322E",
    "pk_sc": "2E55B51188CA46EB89B7CEFD1E7C8D7181AA9592CDC1183C5E9C54CA3F145FA0",
    "pk_tc": "9F4B28854011431E613BE0506BFABACC1012EE7D0E8936B766637557DB6B3E91",
    "pk_en": "B02D5F8A5E3D5FF5310BFB508470385A2518A80544684C801D9D3C9D3C580414",
}
EXPECTED_JUMP_EVIDENCE = (
    125,
    "B688699A82AEDE423232643D44223050C74814F166F861B9E007046B4B39C9EA",
)
EXPECTED_REVERSE_MAP_SHA256 = (
    "F29DD231292C67B8A56B3AAFC2B6E24DEF3AAE75B6595C3299D74C4688470849"
)
EXPECTED_CHANGED_LITERAL_COUNT = 52

BASIS = (
    "review_queue_pk_msggame_B001_S1025_zero_based_ordinals67_133_"
    "pristine_pk_pc_jp_sole_authority_records1324_1396_exact_67_visible_"
    "six_control_only_exclusions_full_1324_1397_boundary_unique_contiguous_"
    "Base_reverse_search_by_literal_semantic_equivalence_and_exact_gap_"
    "skeleton_without_offset_assumption_discovered_plus54_graph_topology_"
    "equivalence_014a_jump_0143_source_current_call_fixed_and_flatten_"
    "digests_completed_Base_decisions_auxiliary_only_PK_specific_"
    "conjectural_and_causal_divergence_dynamic_name_sama_tono_me_"
    "historical_honorific_register_bound_suffix_assembly_left_S1024_"
    "right_S1026_boundary_agreement_all_runtime_pending_no_korean_authority"
)


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest().upper()


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
    record_ids: tuple[int, ...],
) -> str:
    digest = hashlib.sha256()
    for record_id in record_ids:
        data = records[(BLOCK_ID, record_id)].data
        digest.update(struct.pack("<III", BLOCK_ID, record_id, len(data)))
        digest.update(data)
    return digest.hexdigest().upper()


def graph_edges(
    records: dict[tuple[int, int], Any],
) -> dict[int, set[int]]:
    edges: dict[int, set[int]] = defaultdict(set)
    for (block_id, record_id), record in sorted(records.items()):
        if block_id != BLOCK_ID:
            continue
        for gap in record_gaps(record):
            for match in MORPHOLOGY_JUMP_RE.finditer(gap):
                edges[record_id].add(struct.unpack("<I", match.group(1))[0])
    return edges


def graph_closure(edges: dict[int, set[int]], root: int) -> set[int]:
    pending = [root]
    seen: set[int] = set()
    while pending:
        record_id = pending.pop()
        if record_id in seen:
            continue
        seen.add(record_id)
        pending.extend(edges.get(record_id, set()) - seen)
    return seen


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


def is_text_boundary(character: str) -> bool:
    return (
        character.isspace()
        or unicodedata.category(character).startswith("P")
        or character == "…"
    )


def fixed_following_blockers(
    records: dict[tuple[int, int], Any],
    root: int,
) -> tuple[str, ...]:
    blockers: list[str] = []
    for key in sorted(records):
        literals = ENGINE.parse_record_literals(records[key])
        for gap_id, gap in enumerate(record_gaps(records[key])):
            for match in MORPHOLOGY_COMMAND_RE.finditer(gap):
                if struct.unpack("<I", match.group(1))[0] != root:
                    continue
                right = (
                    literals[gap_id].text
                    if gap_id < len(literals)
                    else ""
                )
                post = gap[match.end() :]
                if (
                    (bool(post) and post != b"\x05\x05\x05")
                    or (bool(right) and not is_text_boundary(right[0]))
                ):
                    blockers.append(f"{key[0]}:{key[1]}:{gap_id}")
    return tuple(blockers)


def incoming_jump_rows(
    records: dict[tuple[int, int], Any],
) -> tuple[tuple[int, int, int, int, int], ...]:
    target_ids = set(FULL_REVERSE_SEARCH_RECORD_IDS)
    rows: list[tuple[int, int, int, int, int]] = []
    for key in sorted(records):
        for gap_id, gap in enumerate(record_gaps(records[key])):
            for match in MORPHOLOGY_JUMP_RE.finditer(gap):
                operand = struct.unpack("<I", match.group(1))[0]
                if operand in target_ids:
                    rows.append(
                        (
                            key[0],
                            key[1],
                            gap_id,
                            match.start(),
                            operand,
                        )
                    )
    return tuple(rows)


def load_queue_targets() -> dict[str, dict[str, Any]]:
    rows = [
        json.loads(line)
        for line in QUEUE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    visible_coordinates: list[str] = []
    selected: dict[str, dict[str, Any]] = {}
    for row in rows:
        if row.get("batch_id") != QUEUE_BATCH_ID:
            continue
        for target in row["target_literals"]:
            if not target.get("visible"):
                continue
            coordinate = target["coordinate"]
            visible_coordinates.append(coordinate)
            if coordinate in TRANSLATIONS:
                selected[coordinate] = {
                    "row": row,
                    "target": target,
                }
    expected_coordinates = list(TRANSLATIONS)
    if (
        len(visible_coordinates) != 200
        or visible_coordinates[
            QUEUE_ZERO_BASED_START:QUEUE_ZERO_BASED_STOP
        ]
        != expected_coordinates
        or set(selected) != set(expected_coordinates)
    ):
        raise RuntimeError(f"segment {SEGMENT} private queue slice drifted")
    return selected


def discover_base_mapping(
    base_jp: dict[tuple[int, int], Any],
    pk_jp: dict[tuple[int, int], Any],
) -> dict[int, int]:
    pk_ids = FULL_REVERSE_SEARCH_RECORD_IDS
    block_zero_ids = sorted(
        record_id
        for block_id, record_id in base_jp
        if block_id == BLOCK_ID
    )
    candidates: list[int] = []
    for start in block_zero_ids:
        base_ids = tuple(range(start, start + len(pk_ids)))
        if any((BLOCK_ID, record_id) not in base_jp for record_id in base_ids):
            continue
        compatible = True
        for pk_id, base_id in zip(pk_ids, base_ids, strict=True):
            pk_literals = literal_texts(pk_jp, pk_id)
            base_literals = literal_texts(base_jp, base_id)
            expected_base = APPROVED_BASE_SOURCE_EQUIVALENCE.get(pk_id)
            literal_match = (
                pk_literals == base_literals
                if expected_base is None
                else (
                    pk_literals == (EXPECTED_PK_JP[pk_id],)
                    and base_literals == (expected_base,)
                )
            )
            if (
                not literal_match
                or record_gaps(pk_jp[(BLOCK_ID, pk_id)])
                != record_gaps(base_jp[(BLOCK_ID, base_id)])
            ):
                compatible = False
                break
        if compatible:
            candidates.append(start)
    if candidates != [1270]:
        raise RuntimeError(
            f"segment {SEGMENT} Base reverse search is not unique: "
            f"{candidates}"
        )
    mapping = {
        pk_id: candidates[0] + ordinal
        for ordinal, pk_id in enumerate(pk_ids)
    }
    if canonical_sha256(
        [[pk_id, mapping[pk_id]] for pk_id in pk_ids]
    ) != EXPECTED_REVERSE_MAP_SHA256:
        raise RuntimeError(f"segment {SEGMENT} discovered mapping drifted")
    return mapping


def load_base_auxiliary_decisions() -> dict[str, str]:
    translations: dict[str, str] = {}
    for path in BASE_DECISION_PATHS:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if (
                row.get("resource") == "base_msggame"
                and isinstance(row.get("translation"), str)
            ):
                translations[row["coordinate"]] = row["translation"]
    return translations


def assert_corpora_and_mapping(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    mapping: dict[int, int],
) -> None:
    for label, expected in ARCHIVE_DIGESTS.items():
        actual = subset_digest(
            records_by_label[label],
            FULL_REVERSE_SEARCH_RECORD_IDS,
        )
        if actual != expected:
            raise RuntimeError(f"segment {SEGMENT} {label} corpus drifted")

    pk_jp = records_by_label["pk_jp"]
    pk_current = records_by_label["pk_current"]
    base_jp = records_by_label["base_jp"]
    for record_id, expected in EXPECTED_PK_JP.items():
        if literal_texts(pk_jp, record_id) != (expected,):
            raise RuntimeError(
                f"segment {SEGMENT} pristine PK JP drifted: {record_id}"
            )
        if (
            record_gaps(pk_jp[(BLOCK_ID, record_id)])
            != record_gaps(pk_current[(BLOCK_ID, record_id)])
            or record_gaps(pk_jp[(BLOCK_ID, record_id)])
            != record_gaps(base_jp[(BLOCK_ID, mapping[record_id])])
        ):
            raise RuntimeError(
                f"segment {SEGMENT} mapped gap skeleton drifted: "
                f"{record_id}/{mapping[record_id]}"
            )
    for record_id, expected_hex in (
        NONQUEUE_CONTROL_ONLY_RECORD_HEX.items()
    ):
        for label in ("pk_jp", "pk_current"):
            record = records_by_label[label][(BLOCK_ID, record_id)]
            if (
                record.data.hex().upper() != expected_hex
                or ENGINE.parse_record_literals(record)
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} control-only record drifted: "
                    f"{label}/{record_id}"
                )


def assert_graph_and_calls(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    mapping: dict[int, int],
) -> dict[int, list[int]]:
    pk_jp = records_by_label["pk_jp"]
    pk_current = records_by_label["pk_current"]
    base_jp = records_by_label["base_jp"]
    pk_edges = graph_edges(pk_jp)
    base_edges = graph_edges(base_jp)
    full_ids = set(FULL_REVERSE_SEARCH_RECORD_IDS)
    mapped_base_ids = set(mapping.values())
    reverse_mapping = {base_id: pk_id for pk_id, base_id in mapping.items()}

    actual_roots = {
        root
        for root in pk_edges
        if graph_closure(pk_edges, root).intersection(full_ids)
        and root_call_sites(pk_jp, root)
    }
    if actual_roots != set(EXPECTED_ROOT_TARGETS):
        raise RuntimeError(f"segment {SEGMENT} 0143 root universe drifted")

    reachable_roots_by_record: dict[int, list[int]] = {
        record_id: [] for record_id in RECORD_IDS
    }
    covered_visible: set[int] = set()
    for root, expected_targets in EXPECTED_ROOT_TARGETS.items():
        pk_targets = tuple(
            sorted(graph_closure(pk_edges, root).intersection(full_ids))
        )
        base_targets = tuple(
            sorted(
                reverse_mapping[base_id]
                for base_id in graph_closure(
                    base_edges,
                    root,
                ).intersection(mapped_base_ids)
            )
        )
        if pk_targets != expected_targets or base_targets != expected_targets:
            raise RuntimeError(
                f"segment {SEGMENT} graph counterpart drifted: {root}"
            )
        for record_id in set(expected_targets).intersection(RECORD_IDS):
            reachable_roots_by_record[record_id].append(root)
            covered_visible.add(record_id)

        source_calls = root_call_sites(pk_jp, root)
        current_calls = root_call_sites(pk_current, root)
        source_fixed = fixed_following_blockers(pk_jp, root)
        current_fixed = fixed_following_blockers(pk_current, root)
        source_only = tuple(sorted(set(source_calls) - set(current_calls)))
        current_only = tuple(sorted(set(current_calls) - set(source_calls)))
        actual_evidence = (
            (
                len(source_calls),
                canonical_sha256(source_calls),
                len(source_fixed),
                canonical_sha256(source_fixed),
            ),
            (
                len(current_calls),
                canonical_sha256(current_calls),
                len(current_fixed),
                canonical_sha256(current_fixed),
            ),
            (
                len(source_only),
                canonical_sha256(source_only),
                len(current_only),
                canonical_sha256(current_only),
            ),
        )
        if actual_evidence != EXPECTED_CALL_EVIDENCE[root]:
            raise RuntimeError(
                f"segment {SEGMENT} caller/fixed/flatten drifted: {root}"
            )

    if set(RECORD_IDS) - covered_visible != set(
        NO_OBSERVED_0143_PATH_RECORD_IDS
    ):
        raise RuntimeError(
            f"segment {SEGMENT} no-observed-0143 universe drifted"
        )
    for label in ("pk_jp", "pk_current"):
        rows = incoming_jump_rows(records_by_label[label])
        if (len(rows), canonical_sha256(rows)) != EXPECTED_JUMP_EVIDENCE:
            raise RuntimeError(
                f"segment {SEGMENT} 014A jump evidence drifted: {label}"
            )
    return reachable_roots_by_record


def assert_translation_semantics(
    mapping: dict[int, int],
    base_decisions: dict[str, str],
) -> None:
    if (
        len(RECORD_IDS) != 67
        or set(TRANSLATIONS_BY_RECORD) != set(RECORD_IDS)
        or set(EXPECTED_PK_JP)
        != set(RECORD_IDS).union({RIGHT_BOUNDARY_RECORD_ID})
    ):
        raise RuntimeError(f"segment {SEGMENT} coordinate universe drifted")
    for source_text, policy in HONORIFIC_SUFFIX_POLICY.items():
        for record_id in policy["record_ids"]:
            if (
                EXPECTED_PK_JP[record_id] != source_text
                or TRANSLATIONS_BY_RECORD[record_id]
                != policy["translation"]
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} honorific policy drifted: "
                    f"{record_id}"
                )

    for record_id in RECORD_IDS:
        base_coordinate = f"0:{mapping[record_id]}:0"
        base_translation = base_decisions.get(base_coordinate)
        translation = TRANSLATIONS_BY_RECORD[record_id]
        divergence = PK_TRANSLATION_DIVERGENCE_FROM_BASE.get(record_id)
        if divergence is None:
            if base_translation != translation:
                raise RuntimeError(
                    f"segment {SEGMENT} auxiliary Base policy drifted: "
                    f"{record_id}/{base_coordinate}"
                )
        elif (
            base_translation != divergence["base_translation"]
            or translation != divergence["pk_translation"]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} PK-specific policy drifted: "
                f"{record_id}"
            )
    boundary_base_coordinate = f"0:{mapping[RIGHT_BOUNDARY_RECORD_ID]}:0"
    if (
        base_decisions.get(boundary_base_coordinate)
        != RIGHT_BOUNDARY_POLICY[100][-1]
        or tuple(
            TRANSLATIONS_BY_RECORD[record_id]
            for record_id in range(1391, 1397)
        )
        + (RIGHT_BOUNDARY_POLICY[100][-1],)
        != RIGHT_BOUNDARY_POLICY[100]
    ):
        raise RuntimeError(f"segment {SEGMENT} right boundary drifted")

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
            upstream_by_root[root]
            + (
                TRANSLATIONS_BY_RECORD[record_id]
                if record_id in TRANSLATIONS_BY_RECORD
                else RIGHT_BOUNDARY_POLICY[root][-1]
            )
            for record_id in record_ids
        }
        if actual != EXPECTED_COMPOSITIONS[root]:
            raise RuntimeError(
                f"segment {SEGMENT} Korean bound composition drifted: "
                f"{root}"
            )
    for record_id, translation in TRANSLATIONS_BY_RECORD.items():
        if (
            "\r" in translation
            or "\n" in translation
            or translation != translation.strip()
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or "…" in translation.replace("……", "")
        ):
            raise RuntimeError(
                f"segment {SEGMENT} text residue drifted: {record_id}"
            )


def build_rows() -> tuple[
    Any,
    dict[str, str],
    list[dict[str, object]],
    bytes,
    dict[int, int],
]:
    queue_targets = load_queue_targets()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    base = prepared.resources["base_msggame"]
    pk = prepared.resources["pk_msggame"]
    records_by_label = {
        "base_jp": ENGINE.archive_records(base.pristine_archive),
        "pk_jp": ENGINE.archive_records(pk.pristine_archive),
        "pk_current": ENGINE.archive_records(pk.current_archive),
        "pk_sc": ENGINE.archive_records(pk.context_archives["SC"]),
        "pk_tc": ENGINE.archive_records(pk.context_archives["TC"]),
        "pk_en": ENGINE.archive_records(pk.context_archives["EN"]),
    }
    mapping = discover_base_mapping(
        records_by_label["base_jp"],
        records_by_label["pk_jp"],
    )
    assert_corpora_and_mapping(records_by_label, mapping)
    reachable_roots = assert_graph_and_calls(records_by_label, mapping)
    base_decisions = load_base_auxiliary_decisions()
    assert_translation_semantics(mapping, base_decisions)

    current_records = records_by_label["pk_current"]
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
        target = prepared.visible_targets.get(
            ("pk_msggame", block_id, record_id, literal_id)
        )
        if target is None:
            raise RuntimeError(
                f"segment {SEGMENT} target absent: {coordinate}"
            )
        queue_target = queue_targets[coordinate]["target"]
        queue_row = queue_targets[coordinate]["row"]
        if (
            queue_target["current_ko_utf16le_sha256"]
            != target["current_ko_utf16le_sha256"]
            or queue_row["source_record_raw_sha256"]
            != target["source_record_raw_sha256"]
            or queue_row["source_jp_literals"]
            != [EXPECTED_PK_JP[record_id]]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} queue/source guard drifted: "
                f"{coordinate}"
            )
        current_signature = ENGINE.protected_signature(
            literals[literal_id].text
        )
        translation_signature = ENGINE.protected_signature(translation)
        if translation_signature != current_signature:
            raise RuntimeError(
                f"segment {SEGMENT} protected signature drifted: "
                f"{coordinate}"
            )

        roots = reachable_roots[record_id]
        row: dict[str, object] = {
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
            "runtime_assembly_evidence": {
                "observed_0143_roots": roots,
                "alternate_dispatch_table_entry_no_observed_0143_path": (
                    not roots
                ),
                "base_semantic_record_discovered_by_reverse_search": (
                    mapping[record_id]
                ),
                "automatic_space_inserted": False,
                "runtime_integration_required": True,
                "root_evidence": {
                    str(root): {
                        "full_terminal_record_ids": list(
                            EXPECTED_ROOT_TARGETS[root]
                        ),
                        "source_call_count": EXPECTED_CALL_EVIDENCE[root][0][0],
                        "current_call_count": EXPECTED_CALL_EVIDENCE[root][1][0],
                        "source_fixed_following_count": (
                            EXPECTED_CALL_EVIDENCE[root][0][2]
                        ),
                        "current_fixed_following_count": (
                            EXPECTED_CALL_EVIDENCE[root][1][2]
                        ),
                        "source_calls_flattened_in_current": (
                            EXPECTED_CALL_EVIDENCE[root][2][0]
                        ),
                    }
                    for root in roots
                },
            },
        }
        morphology_root = next(
            (
                root
                for root, record_ids in ROOT_TERMINAL_RECORD_IDS.items()
                if record_id in record_ids
            ),
            None,
        )
        if morphology_root is not None:
            row["runtime_assembly_evidence"]["assembly_plan"] = (
                ROOT_ASSEMBLY_PLAN[morphology_root]
            )
        if record_id in TONO_RECORD_IDS:
            row["honorific_spacing_evidence"] = TONO_SPACING_POLICY
        if record_id in PK_TRANSLATION_DIVERGENCE_FROM_BASE:
            row["pk_specific_semantic_divergence"] = (
                PK_TRANSLATION_DIVERGENCE_FROM_BASE[record_id]
            )
        rows.append(row)

    replacements = {
        tuple(int(value) for value in coordinate.split(":")): translation
        for coordinate, translation in TRANSLATIONS.items()
    }
    candidate = ENGINE.rebuild_packed_with_literals(
        pk.current_blob,
        replacements,
    )
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    target_keys = {(BLOCK_ID, record_id) for record_id in RECORD_IDS}
    if len(candidate_records) != len(current_records):
        raise RuntimeError(f"segment {SEGMENT} record count drifted")
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
    if reversed_blob != pk.current_blob:
        raise RuntimeError(f"segment {SEGMENT} reverse overlay drifted")
    return prepared, TRANSLATIONS, rows, candidate, mapping


def main() -> int:
    first = build_rows()
    second = build_rows()
    prepared, translations, rows, candidate, mapping = first
    if (
        candidate != second[3]
        or ENGINE.jsonl(rows) != ENGINE.jsonl(second[2])
        or mapping != second[4]
    ):
        raise RuntimeError(f"segment {SEGMENT} second-run reproduction drifted")

    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(rows) != 67 or len(validated) != len(translations):
        raise RuntimeError(f"segment {SEGMENT} validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime/authority flags drifted"
        )

    pk = prepared.resources["pk_msggame"]
    current_records = ENGINE.archive_records(pk.current_archive)
    changed = sum(
        TRANSLATIONS_BY_RECORD[record_id]
        != literal_texts(current_records, record_id)[0]
        for record_id in RECORD_IDS
    )
    if changed != EXPECTED_CHANGED_LITERAL_COUNT:
        raise RuntimeError(f"segment {SEGMENT} changed count drifted")
    discovered_offsets = sorted(
        {pk_id - base_id for pk_id, base_id in mapping.items()}
    )
    if discovered_offsets != [54]:
        raise RuntimeError(
            f"segment {SEGMENT} discovered offset set drifted"
        )

    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B001_S1025",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [67, 133],
                "source_literal_count": 67,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "confirmed_non_display": 0,
                "changed_literal_count": changed,
                "nonqueue_control_only_record_ids": list(
                    NONQUEUE_CONTROL_ONLY_RECORD_IDS
                ),
                "base_mapping_method": (
                    "unique_contiguous_reverse_search_exact_gap_skeleton"
                ),
                "discovered_base_record_range": [
                    min(mapping.values()),
                    max(mapping.values()),
                ],
                "discovered_offset_set": discovered_offsets,
                "base_reverse_map_sha256": EXPECTED_REVERSE_MAP_SHA256,
                "pk_specific_semantic_divergence": (
                    PK_TRANSLATION_DIVERGENCE_FROM_BASE
                ),
                "left_boundary_policy": {
                    "root21_29_37": {"1324": "님", "1325": "공"},
                    "root34": {"1328": "님", "1329": "공"},
                    "root46": {"1331": "놈", "1335": "님"},
                },
                "right_boundary_root100": {
                    "record_ids": list(ROOT_TERMINAL_RECORD_IDS[100]),
                    "policy": list(RIGHT_BOUNDARY_POLICY[100]),
                },
                "root_terminal_record_ids": ROOT_TERMINAL_RECORD_IDS,
                "target_runtime_skeleton_exact": True,
                "protected_signature_exact": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
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
