#!/usr/bin/env python3
"""Build Base block-0 runtime-terminal segment 1006 decisions."""

from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import re
import struct
import sys
import unicodedata
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment1005 as PREVIOUS


GENERAL = PREVIOUS.GENERAL
ENGINE = GENERAL.ENGINE
UTIL = GENERAL.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B002_S1006.private.v1.jsonl"
)
SEGMENT = 1006
BLOCK_ID = 0
RECORD_IDS = tuple(range(1409, 1476))
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
PK_RECORD_MAP = {
    (BLOCK_ID, record_id): (BLOCK_ID, record_id + 54)
    for record_id in RECORD_IDS
}
TRANSLATIONS_BY_RECORD = {
    1409: "지 않사옵니다",
    1410: "지 않사옵니다",
    1411: "지 않습니다",
    1412: "지 않습니다",
    1413: "지 않는다",
    1414: "아니오",
    1415: "아니",
    1416: "아니오",
    1417: "아니오",
    1418: "아니오",
    1419: "아니",
    1420: "아니야",
    1421: "아니요, 아니요",
    1422: "아니, 아니",
    1423: "아니요, 아니요",
    1424: "아니요, 아니요",
    1425: "아니요, 아니요",
    1426: "아니, 아니",
    1427: "아니, 아니",
    1428: "습니다",
    1429: "다",
    1430: "사옵니다",
    1431: "사옵니다",
    1432: "습니다",
    1433: "습니다",
    1434: "다",
    1435: "는",
    1436: "는",
    1437: "는",
    1438: "는",
    1439: "는",
    1440: "는",
    1441: "는",
    1442: "습니다",
    1443: "는다",
    1444: "사옵니다",
    1445: "사옵니다",
    1446: "습니다",
    1447: "습니다",
    1448: "는다",
    1449: "으세요",
    1450: "어라",
    1451: "으시옵소서",
    1452: "으시옵소서",
    1453: "으시오",
    1454: "으시오",
    1455: "어라",
    1456: "도록 합시다",
    1457: "자",
    1458: "도록 합시다",
    1459: "도록 합시다",
    1460: "도록 합시다",
    1461: "도록 합시다",
    1462: "자",
    1463: "예",
    1464: "음",
    1465: "예",
    1466: "옛",
    1467: "예",
    1468: "옛",
    1469: "그래",
    1470: "어머",
    1471: "오오",
    1472: "어머나",
    1473: "흠",
    1474: "어머",
    1475: "오오",
}
RAW_TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_BASE_JP = {
    1409: "おりませぬ",
    1410: "おりませぬ",
    1411: "いません",
    1412: "おりません",
    1413: "おらぬ",
    1414: "いえ",
    1415: "いや",
    1416: "いいえ",
    1417: "いいえ",
    1418: "いえ",
    1419: "いや",
    1420: "いいや",
    1421: "いえいえ",
    1422: "いやいや",
    1423: "いえいえ",
    1424: "いえいえ",
    1425: "いえいえ",
    1426: "いやいや",
    1427: "いやいや",
    1428: "おります",
    1429: "おる",
    1430: "おりまする",
    1431: "おりまする",
    1432: "おります",
    1433: "おります",
    1434: "おる",
    1435: "いる",
    1436: "おる",
    1437: "いる",
    1438: "おる",
    1439: "いる",
    1440: "おる",
    1441: "おる",
    1442: "います",
    1443: "う",
    1444: "いまする",
    1445: "いまする",
    1446: "います",
    1447: "います",
    1448: "う",
    1449: "いなさい",
    1450: "え",
    1451: "いなされませ",
    1452: "われませ",
    1453: "いなされ",
    1454: "われよ",
    1455: "え",
    1456: "いましょう",
    1457: "おう",
    1458: "いましょう",
    1459: "いましょう",
    1460: "いましょう",
    1461: "いましょう",
    1462: "おう",
    1463: "ええ",
    1464: "うむ",
    1465: "ええ",
    1466: "ははっ",
    1467: "はい",
    1468: "はっ",
    1469: "おう",
    1470: "あら",
    1471: "おお",
    1472: "まあ",
    1473: "ふむ",
    1474: "あら",
    1475: "おお",
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_PK_JP.update(
    {
        1416: "いえ",
        1417: "いえ",
        1420: "いや",
        1451: "いなされ",
    }
)
ARCHIVE_DIGESTS = {
    "base_jp": "7CE6581B0C35E0B09F68013BB17F93D3BCEC34FE46BE69EB7380D9FB65FC4E8F",
    "base_current": "982D74E2D47451A835A1AE55F427AA5C7FA44B92E22E2E7AE9602DCFC35DED37",
    "base_sc": "235DD256E236EC9555D64984ECEFF7D9DA2E4160EFDD3764BB4855438A83BB8D",
    "base_tc": "235DD256E236EC9555D64984ECEFF7D9DA2E4160EFDD3764BB4855438A83BB8D",
    "pk_jp": "EF0D3F1C9D062A5B38F47E4CFB64EDC2FD828F099CB0658C8584D016BC9DAC80",
    "pk_current": "6DC704B170AA79333764E235FB7538F675990A94661BAA0909BB5F7004BCD43C",
    "pk_sc": "9AF5FF0FF27FA674A63A974632A5CCFD87582F95DDFD316C262FF2FD009D7DB9",
    "pk_tc": "9AF5FF0FF27FA674A63A974632A5CCFD87582F95DDFD316C262FF2FD009D7DB9",
    "pk_en": "9AF5FF0FF27FA674A63A974632A5CCFD87582F95DDFD316C262FF2FD009D7DB9",
}
BASE_PK_LITERAL_DIVERGENCES = {
    "jp": (1416, 1417, 1420, 1451),
    "current": (1420, 1451),
    "sc": (),
    "tc": (),
}
BOUNDARY_EXPECTED = {
    "base_jp": {
        1407: "おりませぬ",
        1408: "おらぬ",
        1476: "なんと",
    },
    "base_current": {
        1407: "없사옵니다",
        1408: "없다",
        1476: "이럴 수가",
    },
    "pk_jp": {
        1407: "おりませぬ",
        1408: "おらぬ",
        1476: "なんと",
    },
    "pk_current": {
        1407: "없사옵니다",
        1408: "없다",
        1476: "이럴 수가",
    },
}
TERMINAL_GROUPS = {
    160: tuple(range(1407, 1414)),
    166: tuple(range(1414, 1421)),
    172: tuple(range(1421, 1428)),
    178: tuple(range(1428, 1435)),
    184: tuple(range(1435, 1442)),
    190: tuple(range(1442, 1449)),
    196: tuple(range(1449, 1456)),
    202: tuple(range(1456, 1463)),
    208: tuple(range(1463, 1470)),
    214: tuple(range(1470, 1477)),
}
BOUNDARY_TERMINAL_RECORD_IDS = (1407, 1408, 1476)
ROOT_CALL_EVIDENCE = {
    "base_jp": {
        160: (20, "2CEF18FBFCFF537E8AEC0332DA6B299D2B02550F42A04106C8DB9E281BD7890E"),
        166: (3, "B6C962B5F54B13CF1B91BB130352B299CBBB89C0BF313EC5DA07B55D3E87AFBC"),
        172: (2, "2AE53C833B51CE6E86C09371E99F0297065C4410A34028BEB780061964677DB4"),
        178: (149, "5FC6FBD913C69A4D490A9A5FCCECD710BACCB16D6323D2754F5F5FEABFB8A8E1"),
        184: (2, "DB279132214E422E4F4CB87E573C799C4C42F50E5484624EE6C8CA2D3ACAD667"),
        190: (16, "7296A7DE9D2DCE7CAA7D4C7AE2890BFB8EA8377F56829A684AD077A3041FA74D"),
        196: (1, "4D206BC5822BFA5D44BCD42E807F96DE832045DCF4A2899A0DBF599E420FB743"),
        202: (29, "CE38514C71D8C07AE27DFFED05107D38308BFBCA55EF2669D9C358CCE0E22DC1"),
        208: (2, "4C159867B036C7A2496B6474E0ECDD2BB830E297761B12F326FF77278FD18DB3"),
        214: (16, "0AD35A7BE9C77A983B88211967AD8D6883476C5DAEEA9956318475266F8C4E8E"),
    },
    "base_current": {
        160: (20, "2CEF18FBFCFF537E8AEC0332DA6B299D2B02550F42A04106C8DB9E281BD7890E"),
        166: (3, "B6C962B5F54B13CF1B91BB130352B299CBBB89C0BF313EC5DA07B55D3E87AFBC"),
        172: (2, "2AE53C833B51CE6E86C09371E99F0297065C4410A34028BEB780061964677DB4"),
        178: (141, "A34EBB05A7E0EE2904970A54DFE058AC2837C9F19A8C2D71158E4C39990BB7B5"),
        184: (2, "DB279132214E422E4F4CB87E573C799C4C42F50E5484624EE6C8CA2D3ACAD667"),
        190: (13, "2E00F678D792A369BDEF95BEDFA3F12562DD7BA247A88AF0D9F11DA1359162A4"),
        196: (1, "4D206BC5822BFA5D44BCD42E807F96DE832045DCF4A2899A0DBF599E420FB743"),
        202: (28, "99E344289EA80A91FE089103371D8086B263A0C8BC3F4A6EF14E79B81BEF508F"),
        208: (2, "4C159867B036C7A2496B6474E0ECDD2BB830E297761B12F326FF77278FD18DB3"),
        214: (16, "0AD35A7BE9C77A983B88211967AD8D6883476C5DAEEA9956318475266F8C4E8E"),
    },
    "pk_jp": {
        160: (27, "65202D821279D00DDD0F9BA37002A81B9F2F004658E37B11B3D012B30EB00A70"),
        166: (4, "B911BCA36A703A96593630D18208A60B406B2932656C8162F0D0D5CA71BD1AE8"),
        172: (2, "79034F611037DAAC66EC367FFFA3AD3BB61746BD03A46034912B2707F1F901D0"),
        178: (163, "8DAEBF5579E2EE19859845BB87D55A9D6AE929198F3F142CC655E7D0CA415F2B"),
        184: (8, "73479E32E989C2C8DA0DE81D2017B36D98E3683CAD4A086C64C08B17CBFEABD6"),
        190: (25, "F3471A7C576E899841DC57DBDBACE2AB9B03CF159A5E2285EAED6C829881ACCD"),
        196: (2, "82129034E737FEE04BA15C53440FFB9E2D3BB5F7F9E9D1F2D290EB96C6757ABF"),
        202: (33, "6DFE8C343442B9D650E8566645AFACF561F67B6399A68BC880F2A8612788D860"),
        208: (4, "C82AC16A447B132D1A928272E85142DAE73E48B81ECAAD812AF57EF4675F6CA1"),
        214: (21, "DEA4A2CB77EFE3DBEF054063C213A125333DB930E307739F3185623FD9FBB37C"),
    },
    "pk_current": {
        160: (27, "65202D821279D00DDD0F9BA37002A81B9F2F004658E37B11B3D012B30EB00A70"),
        166: (4, "B911BCA36A703A96593630D18208A60B406B2932656C8162F0D0D5CA71BD1AE8"),
        172: (2, "79034F611037DAAC66EC367FFFA3AD3BB61746BD03A46034912B2707F1F901D0"),
        178: (153, "7BDE183ECDEAB591EC90957298AE3047B4F7379E1B42BEDC84B258BA3D8D681F"),
        184: (7, "9AA9D0200BDA5E72E4C32A2DB76367539A1EF69712637D4C8324B73F8AFE3E02"),
        190: (22, "C956527FEAEB255A5198F7749A62B64BC19390A02944D44A0606210900577AED"),
        196: (2, "82129034E737FEE04BA15C53440FFB9E2D3BB5F7F9E9D1F2D290EB96C6757ABF"),
        202: (31, "66B66B460B9B660A851FEB85E1FBA0775BF57CA96401A516F3D6E86B31A0D89F"),
        208: (4, "C82AC16A447B132D1A928272E85142DAE73E48B81ECAAD812AF57EF4675F6CA1"),
        214: (21, "DEA4A2CB77EFE3DBEF054063C213A125333DB930E307739F3185623FD9FBB37C"),
    },
}
TERMINAL_EDGE_EVIDENCE = {
    "base_jp": (70, "DEAF6CB950C27FE3FBFEE5A2D8B3C7B34BEF480BC429EA4A3A2CF01993DE9138"),
    "base_current": (70, "DEAF6CB950C27FE3FBFEE5A2D8B3C7B34BEF480BC429EA4A3A2CF01993DE9138"),
    "pk_jp": (70, "47A0F06BE421D325B3814415D3A6517C1B956CDDCCE143545533434E9E890F00"),
    "pk_current": (70, "47A0F06BE421D325B3814415D3A6517C1B956CDDCCE143545533434E9E890F00"),
}
EXPECTED_014C_CANDIDATES = {
    "base_jp": ("15:25:0:193:inside_014A",),
    "base_current": ("15:25:0:193:inside_014A",),
    "pk_jp": ("15:25:0:65:inside_014A",),
    "pk_current": ("15:25:0:65:inside_014A",),
}
SOURCE_ONLY_FLATTENED_BASE_CALLS = {
    178: (
        "6:4146:1:0",
        "6:4150:1:0",
        "8:1033:2:0",
        "13:24:1:0",
        "13:108:1:0",
        "13:127:1:0",
        "15:1626:1:0",
        "15:2214:1:0",
    ),
    190: ("2:235:2:0", "6:4181:3:0", "6:4404:3:0"),
    202: ("8:1034:2:0",),
}
BOUND_SUFFIX_ROOTS = (160, 178, 184, 190, 196, 202)
CURRENT_UPSTREAM_ONLY_ASSEMBLY_BLOCKERS = {
    160: (
        "6:3528:1",
        "15:1843:1",
        "15:1845:1",
        "15:1855:1",
        "15:1857:1",
        "15:2376:1",
        "15:2394:1",
    ),
    178: (
        "6:3934:3",
        "6:3962:1",
        "6:3963:1",
        "6:3964:1",
        "6:3965:1",
        "6:3966:1",
        "6:3967:1",
        "6:3968:1",
        "6:3969:1",
        "6:3970:1",
        "6:3971:1",
        "6:3972:1",
        "6:3973:1",
        "6:4012:2",
        "6:4383:4",
        "8:288:1",
        "8:289:2",
        "8:296:3",
        "8:320:2",
        "8:331:1",
        "9:3270:2",
        "9:3673:1",
        "9:3674:1",
        "15:1833:1",
        "15:1847:1",
        "15:1937:1",
        "15:1940:1",
        "15:2375:1",
        "15:2375:2",
        "15:2377:1",
    ),
    184: ("6:4377:1", "15:1468:4"),
    190: ("6:4431:2", "7:2394:3"),
    196: (),
    202: ("7:880:1", "15:2181:2"),
}
BLOCKER_RECORD_DIGEST = (
    "703F8CFBCF47D45551C97CD6FB811F7C65D563A06EA2417F9D26809D9A4E8C79"
)
ROOT_ASSEMBLY_PLAN = {
    160: "verb/existential stem + 지 않사옵니다/지 않는다/지 않습니다",
    178: "consumer rewritten to end in 있 + 습니다/다/사옵니다",
    184: "consumer rewritten to end in 있 + 는; fixed following text also needs spacing",
    190: "consonant-final action stem + 습니다/는다/사옵니다",
    196: "웃 + 으세요/어라/으시옵소서/으시오",
    202: "verb stem + 도록 합시다/자",
}
MORPHOLOGY_COMMAND_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)
MORPHOLOGY_JUMP_RE = re.compile(b"\x01\x4A(.{4})", re.DOTALL)
BASIS = (
    "review_queue_base_msggame_B002_pristine_base_pc_jp_sole_authority_"
    "block0_runtime_voice_terminal_records1409_1475_all_literal0_with_"
    "S1005_root160_cross_segment_records1407_1413_and_root214_record1476_"
    "closure_audited_explicit_uniform_plus54_pk_mapping_four_jp_and_two_"
    "current_divergences_sc_tc_empty_pk_en_empty_context_only_014A_jump_"
    "0143_root_call_and_raw_014C_inside_014A_nonopcode_evidence_source_"
    "current_flattening_and_live_caller_boundary_blockers_bound_korean_"
    "suffix_register_matrix_negative_progressive_existential_attributive_"
    "action_imperative_volitional_acknowledgement_interjection_semantics_"
    "one_line_skeleton_runtime_fragment_pending_no_korean_authority"
)


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return tuple(
        literal.text for literal in ENGINE.parse_record_literals(records[key])
    )


def record_gaps(record: Any) -> tuple[bytes, ...]:
    literals = ENGINE.parse_record_literals(record)
    gaps: list[bytes] = []
    cursor = 0
    for literal in literals:
        gaps.append(record.data[cursor : literal.marker_offset])
        cursor = literal.marker_end
    gaps.append(record.data[cursor:])
    return tuple(gaps)


def archive_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
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
    return {
        label: ENGINE.archive_records(archive)
        for label, archive in archives.items()
    }


def assert_archive_and_mapping(
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

    for record_id in RECORD_IDS:
        key = (BLOCK_ID, record_id)
        mapped = PK_RECORD_MAP[key]
        for label in ("base_jp", "base_current", "base_sc", "base_tc"):
            if (
                len(literal_texts(records_by_label[label], key)) != 1
                or record_gaps(records_by_label[label][key])
                != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base skeleton drifted: "
                    f"{label}/{key}"
                )
        for label in ("pk_jp", "pk_current", "pk_sc", "pk_tc", "pk_en"):
            if (
                len(literal_texts(records_by_label[label], mapped)) != 1
                or record_gaps(records_by_label[label][mapped])
                != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} PK skeleton drifted: "
                    f"{label}/{mapped}"
                )
        if literal_texts(records_by_label["base_jp"], key) != (
            EXPECTED_BASE_JP[record_id],
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base JP source drifted: {record_id}"
            )
        if literal_texts(records_by_label["pk_jp"], mapped) != (
            EXPECTED_PK_JP[record_id],
        ):
            raise RuntimeError(
                f"segment {SEGMENT} PK JP context drifted: {record_id}"
            )
        if literal_texts(records_by_label["pk_en"], mapped) != ("",):
            raise RuntimeError(
                f"segment {SEGMENT} PK EN context drifted: {record_id}"
            )

    for language in ("jp", "current", "sc", "tc"):
        actual = tuple(
            record_id
            for record_id in RECORD_IDS
            if literal_texts(
                records_by_label[f"base_{language}"],
                (BLOCK_ID, record_id),
            )
            != literal_texts(
                records_by_label[f"pk_{language}"],
                (BLOCK_ID, record_id + 54),
            )
        )
        if actual != BASE_PK_LITERAL_DIVERGENCES[language]:
            raise RuntimeError(
                f"segment {SEGMENT} Base/PK {language} mapping drifted"
            )

    for label, expected_by_id in BOUNDARY_EXPECTED.items():
        records = records_by_label[label]
        pk = label.startswith("pk_")
        for base_record_id, expected in expected_by_id.items():
            actual_id = base_record_id + 54 if pk else base_record_id
            key = (BLOCK_ID, actual_id)
            if (
                literal_texts(records, key) != (expected,)
                or record_gaps(records[key]) != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} boundary drifted: "
                    f"{label}/{base_record_id}"
                )


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


def assert_root_call_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    sites_by_label: dict[str, dict[int, tuple[str, ...]]] = {}
    for label, expected_by_root in ROOT_CALL_EVIDENCE.items():
        records = records_by_label[label]
        sites_by_label[label] = {}
        for root, (expected_count, expected_sha256) in (
            expected_by_root.items()
        ):
            sites = root_call_sites(records, root)
            actual_sha256 = hashlib.sha256(
                "\n".join(sites).encode("ascii")
            ).hexdigest().upper()
            if (
                len(sites) != expected_count
                or actual_sha256 != expected_sha256
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} root call drifted: {label}/{root}"
                )
            sites_by_label[label][root] = sites

    for edition in ("base", "pk"):
        source = sites_by_label[f"{edition}_jp"]
        current = sites_by_label[f"{edition}_current"]
        for root in TERMINAL_GROUPS:
            if set(current[root]) - set(source[root]):
                raise RuntimeError(
                    f"segment {SEGMENT} current added root call: "
                    f"{edition}/{root}"
                )

    base_source = sites_by_label["base_jp"]
    base_current = sites_by_label["base_current"]
    for root in TERMINAL_GROUPS:
        expected = set(SOURCE_ONLY_FLATTENED_BASE_CALLS.get(root, ()))
        if (
            set(base_source[root]) - set(base_current[root]) != expected
            or set(base_current[root]) - set(base_source[root])
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base flattening drifted: {root}"
            )


def assert_jump_and_014c_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    for label, (expected_count, expected_sha256) in (
        TERMINAL_EDGE_EVIDENCE.items()
    ):
        records = records_by_label[label]
        offset = 54 if label.startswith("pk_") else 0
        target_ids = {
            record_id + offset
            for record_ids in TERMINAL_GROUPS.values()
            for record_id in record_ids
        }
        edges_by_node: dict[int, set[int]] = defaultdict(set)
        evidence: list[str] = []
        incoming: set[int] = set()
        for key in sorted(records):
            for gap_id, gap in enumerate(record_gaps(records[key])):
                for match in MORPHOLOGY_JUMP_RE.finditer(gap):
                    operand = struct.unpack("<I", match.group(1))[0]
                    if key[0] == BLOCK_ID:
                        edges_by_node[key[1]].add(operand)
                    if operand in target_ids:
                        evidence.append(
                            f"{key[0]}:{key[1]}:{gap_id}:"
                            f"{match.start()}:{operand}"
                        )
                        incoming.add(operand)
        actual_sha256 = hashlib.sha256(
            "\n".join(evidence).encode("ascii")
        ).hexdigest().upper()
        if (
            len(evidence) != expected_count
            or actual_sha256 != expected_sha256
            or incoming != target_ids
        ):
            raise RuntimeError(
                f"segment {SEGMENT} 014A terminal edges drifted: {label}"
            )
        for root, base_terminals in TERMINAL_GROUPS.items():
            expected_terminals = {
                record_id + offset for record_id in base_terminals
            }
            actual_terminals = (
                graph_closure(edges_by_node, root) & target_ids
            )
            if actual_terminals != expected_terminals:
                raise RuntimeError(
                    f"segment {SEGMENT} graph closure drifted: "
                    f"{label}/{root}"
                )

        raw_014c: list[str] = []
        for key in sorted(records):
            for gap_id, gap in enumerate(record_gaps(records[key])):
                jump_spans = [
                    (match.start(), match.end())
                    for match in MORPHOLOGY_JUMP_RE.finditer(gap)
                ]
                position = 0
                while True:
                    position = gap.find(b"\x01\x4C", position)
                    if position < 0:
                        break
                    inside_jump = any(
                        start <= position and position + 2 <= end
                        for start, end in jump_spans
                    )
                    classification = (
                        "inside_014A" if inside_jump else "standalone"
                    )
                    raw_014c.append(
                        f"{key[0]}:{key[1]}:{gap_id}:"
                        f"{position}:{classification}"
                    )
                    position += 1
        if tuple(raw_014c) != EXPECTED_014C_CANDIDATES[label]:
            raise RuntimeError(
                f"segment {SEGMENT} raw 014C evidence drifted: {label}"
            )
        if any(item.endswith(":standalone") for item in raw_014c):
            raise RuntimeError(
                f"segment {SEGMENT} standalone 014C command appeared"
            )


def is_text_boundary(character: str) -> bool:
    return (
        character.isspace()
        or unicodedata.category(character).startswith("P")
        or character == "\u2026"
    )


def current_assembly_blockers(
    records: dict[tuple[int, int], Any],
    root: int,
) -> tuple[str, ...]:
    blockers: list[str] = []
    for key in sorted(records):
        record = records[key]
        literals = ENGINE.parse_record_literals(record)
        for gap_id, gap in enumerate(record_gaps(record)):
            for match in MORPHOLOGY_COMMAND_RE.finditer(gap):
                if struct.unpack("<I", match.group(1))[0] != root:
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
                    blockers.append(f"{key[0]}:{key[1]}:{gap_id}")
    return tuple(blockers)


def assert_live_assembly(
    current_records: dict[tuple[int, int], Any],
) -> None:
    if set(CURRENT_UPSTREAM_ONLY_ASSEMBLY_BLOCKERS) != set(
        BOUND_SUFFIX_ROOTS
    ):
        raise RuntimeError(
            f"segment {SEGMENT} blocker root universe drifted"
        )
    blocker_record_keys: set[tuple[int, int]] = set()
    for root in BOUND_SUFFIX_ROOTS:
        actual = current_assembly_blockers(current_records, root)
        expected = CURRENT_UPSTREAM_ONLY_ASSEMBLY_BLOCKERS[root]
        if actual != expected:
            raise RuntimeError(
                f"segment {SEGMENT} assembly blockers drifted: {root}"
            )
        blocker_record_keys.update(
            tuple(int(value) for value in site.split(":")[:2])
            for site in actual
        )
    digest = hashlib.sha256()
    for block_id, record_id in sorted(blocker_record_keys):
        data = current_records[(block_id, record_id)].data
        digest.update(struct.pack("<III", block_id, record_id, len(data)))
        digest.update(data)
    if (
        digest.hexdigest().upper() != BLOCKER_RECORD_DIGEST
        or len(blocker_record_keys) != 42
        or sum(
            len(sites)
            for sites in CURRENT_UPSTREAM_ONLY_ASSEMBLY_BLOCKERS.values()
        )
        != 43
    ):
        raise RuntimeError(
            f"segment {SEGMENT} blocker record bytes drifted"
        )


def assert_semantics(translations: dict[str, str]) -> None:
    if (
        translations != RAW_TRANSLATIONS
        or len(translations) != 67
        or set(EXPECTED_BASE_JP) != set(RECORD_IDS)
        or set(EXPECTED_PK_JP) != set(RECORD_IDS)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} translation universe drifted"
        )
    if tuple(
        PREVIOUS.TRANSLATIONS_BY_RECORD[record_id]
        for record_id in (1407, 1408)
    ) != ("지 않사옵니다", "지 않는다"):
        raise RuntimeError(
            f"segment {SEGMENT} S1005 root160 boundary drifted"
        )
    if tuple(
        translations[f"0:{record_id}:0"]
        for record_id in range(1409, 1414)
    ) != (
        "지 않사옵니다",
        "지 않사옵니다",
        "지 않습니다",
        "지 않습니다",
        "지 않는다",
    ):
        raise RuntimeError("negative progressive register matrix drifted")
    if tuple(
        translations[f"0:{record_id}:0"]
        for record_id in range(1421, 1428)
    ) != (
        "아니요, 아니요",
        "아니, 아니",
        "아니요, 아니요",
        "아니요, 아니요",
        "아니요, 아니요",
        "아니, 아니",
        "아니, 아니",
    ):
        raise RuntimeError("reduplicated denial register matrix drifted")
    if tuple(
        translations[f"0:{record_id}:0"]
        for record_id in range(1428, 1435)
    ) != (
        "습니다",
        "다",
        "사옵니다",
        "사옵니다",
        "습니다",
        "습니다",
        "다",
    ):
        raise RuntimeError("existential/progressive suffix matrix drifted")
    if {
        translations[f"0:{record_id}:0"]
        for record_id in range(1435, 1442)
    } != {"는"}:
        raise RuntimeError("attributive existential suffix drifted")
    if tuple(
        translations[f"0:{record_id}:0"]
        for record_id in range(1442, 1449)
    ) != (
        "습니다",
        "는다",
        "사옵니다",
        "사옵니다",
        "습니다",
        "습니다",
        "는다",
    ):
        raise RuntimeError("action verb suffix matrix drifted")
    if tuple(
        translations[f"0:{record_id}:0"]
        for record_id in range(1449, 1456)
    ) != (
        "으세요",
        "어라",
        "으시옵소서",
        "으시옵소서",
        "으시오",
        "으시오",
        "어라",
    ):
        raise RuntimeError("imperative suffix register matrix drifted")
    if tuple(
        translations[f"0:{record_id}:0"]
        for record_id in range(1456, 1463)
    ) != (
        "도록 합시다",
        "자",
        "도록 합시다",
        "도록 합시다",
        "도록 합시다",
        "도록 합시다",
        "자",
    ):
        raise RuntimeError("volitional suffix register matrix drifted")
    if (
        translations["0:1466:0"] != "옛"
        or translations["0:1468:0"] != "옛"
        or translations["0:1469:0"] != "그래"
        or translations["0:1472:0"] != "어머나"
    ):
        raise RuntimeError(
            "acknowledgement/interjection semantics drifted"
        )


def build_rows() -> tuple[Any, list[dict[str, object]], str]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    records_by_label = archive_records(prepared)
    assert_archive_and_mapping(records_by_label)
    assert_root_call_evidence(records_by_label)
    assert_jump_and_014c_evidence(records_by_label)
    assert_live_assembly(records_by_label["base_current"])

    translations = dict(RAW_TRANSLATIONS)
    assert_semantics(translations)
    current = records_by_label["base_current"]
    for coordinate, translation in translations.items():
        _, record_id, _ = (
            int(value) for value in coordinate.split(":")
        )
        current_text = literal_texts(
            current,
            (BLOCK_ID, record_id),
        )[0]
        if (
            not ENGINE.is_visible_translation_candidate(current_text)
            or "\r" in translation
            or "\n" in translation
            or translation != translation.strip()
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation)
            or UTIL.layout_signature(translation)
            != UTIL.layout_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} protected line drifted: "
                f"{coordinate}"
            )

    candidate_sha256 = GENERAL.assert_overlay_roundtrip(
        prepared,
        segment=SEGMENT,
        translations=translations,
        target_records=set(RECORD_KEYS),
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        target = prepared.visible_targets[
            ("base_msggame", block_id, record_id, literal_id)
        ]
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
        raise RuntimeError(
            f"segment {SEGMENT} validation count drifted"
        )
    current = archive_records(prepared)["base_current"]
    changed = sum(
        TRANSLATIONS_BY_RECORD[record_id]
        != literal_texts(current, (BLOCK_ID, record_id))[0]
        for record_id in RECORD_IDS
    )
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B002_S1006",
                "queue": "base_msggame-B002",
                "source_literal_count": 67,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "changed_literal_count": changed,
                "base_pk_record_offset": 54,
                "base_pk_jp_literal_divergence_records": list(
                    BASE_PK_LITERAL_DIVERGENCES["jp"]
                ),
                "base_pk_current_literal_divergence_records": list(
                    BASE_PK_LITERAL_DIVERGENCES["current"]
                ),
                "base_pk_sc_tc_gap_divergence_records": [],
                "pk_en_visible_records": [],
                "cross_segment_root160_records": list(
                    TERMINAL_GROUPS[160]
                ),
                "cross_segment_root214_records": list(
                    TERMINAL_GROUPS[214]
                ),
                "source_only_flattened_base_calls": {
                    str(root): list(sites)
                    for root, sites in (
                        SOURCE_ONLY_FLATTENED_BASE_CALLS.items()
                    )
                },
                "upstream_only_blocker_counts": {
                    str(root): len(sites)
                    for root, sites in (
                        CURRENT_UPSTREAM_ONLY_ASSEMBLY_BLOCKERS.items()
                    )
                },
                "upstream_only_blocker_count": 43,
                "root_assembly_plan": ROOT_ASSEMBLY_PLAN,
                "raw_014c_standalone_command_count": 0,
                "terminal_edge_evidence": TERMINAL_EDGE_EVIDENCE,
                "candidate_sha256": candidate_sha256,
                "protected_line_count": 1,
                "target_runtime_skeleton_exact": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "historic_korean_used": False,
                "switch_korean_used": False,
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
