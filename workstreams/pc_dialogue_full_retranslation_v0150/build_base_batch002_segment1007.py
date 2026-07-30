#!/usr/bin/env python3
"""Build Base block-0 runtime-terminal segment 1007 decisions."""

from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment1005 as SUPPORT


ENGINE = SUPPORT.ENGINE
GENERAL = SUPPORT.GENERAL
UTIL = SUPPORT.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B002_S1007.private.v1.jsonl"
)
SEGMENT = 1007
BLOCK_ID = 0
RECORD_IDS = tuple(range(1476, 1543))
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
PK_RECORD_MAP = {
    (BLOCK_ID, record_id): (BLOCK_ID, record_id + 54)
    for record_id in RECORD_IDS
}
PK_RECORD_KEYS = tuple(PK_RECORD_MAP[key] for key in RECORD_KEYS)

EXPECTED_JP = {
    1476: "なんと",
    1477: "恐れ入ります",
    1478: "恐れ入る",
    1479: "恐れ入ります",
    1480: "恐れ入りまする",
    1481: "恐れ入ります",
    1482: "恐れ入ります",
    1483: "恐れ入る",
    1484: "思います",
    1485: "思う",
    1486: "存じまする",
    1487: "存じます",
    1488: "存じます",
    1489: "存ずる",
    1490: "存ずる",
    1491: "あら",
    1492: "おや",
    1493: "まあ",
    1494: "やや",
    1495: "あら",
    1496: "ふむ",
    1497: "むう",
    1498: "ですか",
    1499: "か",
    1500: "でございますか",
    1501: "でございますか",
    1502: "ですか",
    1503: "でござるか",
    1504: "か",
    1505: "わ",
    1506: "か",
    1507: "わ",
    1508: "か",
    1509: "わ",
    1510: "か",
    1511: "か",
    1512: "ね",
    1513: "か",
    1514: "ですね",
    1515: "ですか",
    1516: "ね",
    1517: "か",
    1518: "か",
    1519: "かしら",
    1520: "か",
    1521: "かしら",
    1522: "か",
    1523: "かしら",
    1524: "か",
    1525: "かな",
    1526: "なんて",
    1527: "か",
    1528: "なんて",
    1529: "か",
    1530: "だわ",
    1531: "か",
    1532: "か",
    1533: "ですか",
    1534: "か",
    1535: "ですか",
    1536: "ですか",
    1537: "ですか",
    1538: "でござるか",
    1539: "か",
    1540: "けれど",
    1541: "が",
    1542: "けれども",
}

TRANSLATIONS_BY_RECORD = {
    1476: "이런",
    1477: "황송합니다",
    1478: "황송하다",
    1479: "황송합니다",
    1480: "황송하옵니다",
    1481: "황송합니다",
    1482: "황송합니다",
    1483: "황송하다",
    1484: "생각합니다",
    1485: "생각한다",
    1486: "생각하옵니다",
    1487: "생각하옵니다",
    1488: "생각하옵니다",
    1489: "생각하오",
    1490: "생각하오",
    1491: "어머",
    1492: "어라",
    1493: "어머나",
    1494: "아니",
    1495: "어머",
    1496: "흠",
    1497: "으음",
    1498: "입니까",
    1499: "인가",
    1500: "이옵니까",
    1501: "이옵니까",
    1502: "입니까",
    1503: "이오",
    1504: "인가",
    1505: "네",
    1506: "가",
    1507: "네",
    1508: "가",
    1509: "네",
    1510: "가",
    1511: "가",
    1512: "네",
    1513: "가",
    1514: "군요",
    1515: "입니까",
    1516: "네",
    1517: "가",
    1518: "가",
    1519: "일까",
    1520: "인가",
    1521: "일까",
    1522: "인가",
    1523: "일까",
    1524: "인가",
    1525: "일까",
    1526: "다니",
    1527: "나",
    1528: "다니",
    1529: "나",
    1530: "네",
    1531: "나",
    1532: "나",
    1533: "입니까",
    1534: "인가",
    1535: "입니까",
    1536: "입니까",
    1537: "입니까",
    1538: "이오",
    1539: "인가",
    1540: "지만",
    1541: "지만",
    1542: "지만",
}
TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}

ROOT_TERMINALS = {
    214: (1476,),
    220: tuple(range(1477, 1484)),
    226: tuple(range(1484, 1491)),
    232: tuple(range(1491, 1498)),
    238: tuple(range(1498, 1505)),
    244: tuple(range(1505, 1512)),
    250: tuple(range(1512, 1519)),
    256: tuple(range(1519, 1526)),
    262: tuple(range(1526, 1533)),
    268: tuple(range(1533, 1540)),
    274: tuple(range(1540, 1543)),
}
RECORD_TO_ROOT = {
    record_id: root
    for root, record_ids in ROOT_TERMINALS.items()
    for record_id in record_ids
}
ASSEMBLY_CLASS = {
    214: "standalone_exclamatory_prefix",
    220: "speaker_register_humble_predicate",
    226: "speaker_register_thought_predicate",
    232: "speaker_register_interjection",
    238: "polymorphic_copular_question",
    244: "polymorphic_bound_final_particle",
    250: "polymorphic_bound_agreement_or_question",
    256: "polymorphic_bound_dubitative_question",
    262: "pk_observed_bound_exclamation_or_question",
    268: "polymorphic_copular_or_predicative_question",
    274: "bound_contrastive_connective",
}

ARCHIVE_DIGESTS = {
    "base_jp": "1CEAF22ED214C530BDE86DC29DC2CBA0F4DB3F5969949B5171AA5324C0F556B9",
    "base_current": "81073DC5B26A0B0A5F4D16D457AE05ED51C6F0B215F7AFA2EB8BFF9BBD0D9420",
    "base_sc": "EE8304F78A7EB72D5684E015996AB522BCF49B6690CC6872E4E4D11F5E02A11A",
    "base_tc": "EE8304F78A7EB72D5684E015996AB522BCF49B6690CC6872E4E4D11F5E02A11A",
    "pk_jp": "E5F626F73918E93325BD6319075A3C0E39CB4B312495D12F7BFF0D4954AA5886",
    "pk_current": "A6C0C6B78A0EE936C747D547E4CDA05D595D8FD42A6BCAD449D663E4B6EC2B8B",
    "pk_sc": "68B0DA2704050C12D6612B362944B60B75915F84134E95A725382AF2453C0456",
    "pk_tc": "68B0DA2704050C12D6612B362944B60B75915F84134E95A725382AF2453C0456",
    "pk_en": "68B0DA2704050C12D6612B362944B60B75915F84134E95A725382AF2453C0456",
}

JUMP_EVIDENCE = {
    "base_jp": (
        67,
        "95F7CA0FBDDFDFFEBC056D19668DAD1E1A09510EC207CB09A39E32CB03A0BCF8",
    ),
    "base_current": (
        67,
        "95F7CA0FBDDFDFFEBC056D19668DAD1E1A09510EC207CB09A39E32CB03A0BCF8",
    ),
    "pk_jp": (
        67,
        "8BD5C24A91C80D32B11CF28DE7727BBACAAE2464A4078C7402C6C6D69710FE00",
    ),
    "pk_current": (
        67,
        "8BD5C24A91C80D32B11CF28DE7727BBACAAE2464A4078C7402C6C6D69710FE00",
    ),
}

CALL_EVIDENCE = {
    "base_jp": {
        214: (16, "0AD35A7BE9C77A983B88211967AD8D6883476C5DAEEA9956318475266F8C4E8E"),
        220: (2, "34FE29B7946AE7FEA9E0ADA7EDE3DF9529E19AEE9BBD87D1C8599AB1C1ED3B67"),
        226: (71, "FD0F52632F79AA31E8783FF80300781133EDC09146CD49F246B5BBF472B11F27"),
        232: (2, "2AF878A5C4A0678B2DE364C6A280C6652B45F51E14CC0FA55A4D08163B62E214"),
        238: (23, "404FF3EDEBABFDDA9E3A975F63CC7ED05BA4420F32F83E7605AD49EAB701F4A9"),
        244: (1, "79B74093F0E7E7F8A10977AC398016FBC86407A40B719E9A29B9C1D906A8FDDC"),
        250: (4, "2FC6E06881297E88E7A2D51E08CD6D64C714695B6AC537F2FFD62C3E2AE15989"),
        256: (7, "8A15C6BE9D616105B7A3B4DD0DD6BF0B93D9A9C409AC718583D783C8F72C8D82"),
        268: (8, "0ECB04D207B1041F60BCCFDFC543199E151A6C75F316F7ED9EFCD68056EB715E"),
        274: (19, "9F4134C6DAF5BBB7E3A07A8D87E810C6D1690D201E874E4201D64A266F8EFE29"),
    },
    "base_current": {
        214: (16, "0AD35A7BE9C77A983B88211967AD8D6883476C5DAEEA9956318475266F8C4E8E"),
        220: (2, "34FE29B7946AE7FEA9E0ADA7EDE3DF9529E19AEE9BBD87D1C8599AB1C1ED3B67"),
        226: (66, "86AD24310CBFAAA67946F675462EF4A62A6902DCC7BCE80337A601EA3C001490"),
        232: (2, "2AF878A5C4A0678B2DE364C6A280C6652B45F51E14CC0FA55A4D08163B62E214"),
        238: (21, "17BFFB92A5D7969CA2CCB02CE5D88F8F4C698788BCFA82877CFFE4FF92E30F25"),
        244: (1, "79B74093F0E7E7F8A10977AC398016FBC86407A40B719E9A29B9C1D906A8FDDC"),
        250: (4, "2FC6E06881297E88E7A2D51E08CD6D64C714695B6AC537F2FFD62C3E2AE15989"),
        256: (5, "E60DF14AD60C7D259EF746BE22A7EAE32E885FA4F4650F91B4F2010286707733"),
        268: (7, "90A3BF697507C9366BAB6F4CE195842ED0663CF5D3B7A55596CC450A1B651E8B"),
        274: (19, "9F4134C6DAF5BBB7E3A07A8D87E810C6D1690D201E874E4201D64A266F8EFE29"),
    },
    "pk_jp": {
        214: (21, "DEA4A2CB77EFE3DBEF054063C213A125333DB930E307739F3185623FD9FBB37C"),
        220: (2, "9A4716106CE12A875FDAC2B39D8DFE46C522398598A23006628F9711909F2F61"),
        226: (75, "18DD511B2CC61B3C3C41460814F7B835E05AE2E8D02588B3AF5901B303147FBC"),
        232: (5, "137401201BD428CDAC5C6E7E1473F6036AD1AC6A5FE122752E264FBC8A6A3953"),
        237: (1, "B47271827170FBCEA78413E7667CDBF43C0666E9A6C0931BC659BA130D2B6137"),
        238: (28, "C2A1F6EE3C78058DD78E01392FCE5029873FDFB7D9846B6562686C3C5C18A98E"),
        244: (2, "8CABFEA0656EF8EBB8AB1AFD39EBDF3F97AE57F0B388DEA83A8D8CAFA3458591"),
        250: (5, "1B45E4D64F619A4214B838950E27DBBB92CDB2370D3D3C0B81C37413E54EAF29"),
        256: (14, "C818ECB11CB05B2C138B0B80B7215CF2159C03F51E6BAAAD3B12490ED86056AA"),
        262: (1, "6D368A0989B774C74B47ECACE74DC09D2AEAADA5012C442F124983EA6D832182"),
        268: (27, "07B0C26F906F90E8ABB2D497AA97F1E0E1C44D3CC08C3C4C6AD7281263261ABF"),
        274: (17, "6F6B10AD0533EF82956D41195A067DA7E4A612C6195D1E86E48D6BDB48FCE833"),
    },
    "pk_current": {
        214: (21, "DEA4A2CB77EFE3DBEF054063C213A125333DB930E307739F3185623FD9FBB37C"),
        220: (2, "9A4716106CE12A875FDAC2B39D8DFE46C522398598A23006628F9711909F2F61"),
        226: (70, "8A7529A7DD7EC403A2DB789871D3DD069839EE61CD9F049C17DC3802990415A7"),
        232: (5, "137401201BD428CDAC5C6E7E1473F6036AD1AC6A5FE122752E264FBC8A6A3953"),
        237: (1, "B47271827170FBCEA78413E7667CDBF43C0666E9A6C0931BC659BA130D2B6137"),
        238: (27, "2B96B075001DEAA5952CBB8949B819CE22204F39D23B6A75EFA636655E930F8C"),
        244: (2, "8CABFEA0656EF8EBB8AB1AFD39EBDF3F97AE57F0B388DEA83A8D8CAFA3458591"),
        250: (5, "1B45E4D64F619A4214B838950E27DBBB92CDB2370D3D3C0B81C37413E54EAF29"),
        256: (12, "58F35432842EB220B960CE96616FD71A281E62CB00612FEA5A2F59C8AFEFC14F"),
        262: (1, "6D368A0989B774C74B47ECACE74DC09D2AEAADA5012C442F124983EA6D832182"),
        268: (26, "5FE373290290F6F88D4CE26AF4A29D97A9174F2AEE53C964DB0C5641651DCB9F"),
        274: (17, "6F6B10AD0533EF82956D41195A067DA7E4A612C6195D1E86E48D6BDB48FCE833"),
    },
}
CALLER_EVIDENCE_SHA256 = {
    "base_jp": "26125A0CF0B8E15D3A71667F834B38C9190FFBB12C23B00EE9167E5A38B10751",
    "base_current": "3A2CFD4332872B5773676429666A0A8B2C38AC13868A01C434877A1E1D281461",
    "pk_jp": "8968C11918C70F8D1FF31E6F57651B57876C37E0F22770588A163EBA4F53312F",
    "pk_current": "FEDE80A821522ED96685A98954BB4A74F9AD4EAA1A43EF4B4EAFAF696774F3ED",
}

SOURCE_ONLY_FLATTENED_CALLS = {
    "base": {
        226: (
            "13:121:1:0",
            "15:2223:2:0",
            "8:1181:1:0",
            "8:1183:2:0",
            "8:1187:1:0",
        ),
        238: ("6:1132:1:0", "6:550:1:0"),
        256: ("15:282:2:0", "6:547:2:0"),
        268: ("6:4404:2:0",),
    },
    "pk": {
        226: (
            "13:121:1:0",
            "15:2253:2:0",
            "8:1197:1:0",
            "8:1199:2:0",
            "8:1203:1:0",
        ),
        238: ("6:1134:1:0",),
        256: ("15:285:2:0", "2:361:1:6"),
        268: ("6:4463:2:0",),
    },
}

VALID_014C_EVIDENCE: dict[str, tuple[tuple[int, int, int, int, int], ...]] = {
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

MORPHOLOGY_COMMAND_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)
MORPHOLOGY_JUMP_RE = re.compile(b"\x01\x4A(.{4})", re.DOTALL)
MORPHOLOGY_014C_RE = re.compile(b"\x01\x4C(.{4})", re.DOTALL)

BASIS = (
    "review_queue_base_msggame_B002_S1007_pristine_base_pc_jp_sole_"
    "authority_block0_runtime_speaker_terminal_table_records1476_1542_"
    "with_exact_uniform_plus54_pk_jp_current_sc_tc_mapping_blank_base_sc_"
    "tc_and_pk_en_sc_tc_context_67_incoming_014a_edges_full_base_and_pk_"
    "0143_caller_closure_record_gap_digests_source_to_current_flattening_"
    "registry_014c_false_positive_inside_014a_operand_guard_humble_thought_"
    "interjection_question_dubitative_and_bound_contrastive_register_"
    "review_all_runtime_fragment_pending_no_korean_build_authority"
)


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return tuple(
        literal.text for literal in ENGINE.parse_record_literals(records[key])
    )


def record_gaps(record: Any) -> tuple[bytes, ...]:
    return SUPPORT.gap_bytes(record)


def archive_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    return SUPPORT.archive_records(prepared)


def operands(data: bytes, pattern: re.Pattern[bytes]) -> tuple[int, ...]:
    return tuple(
        struct.unpack("<I", match.group(1))[0]
        for match in pattern.finditer(data)
    )


def graph_edges(
    records: dict[tuple[int, int], Any],
) -> dict[int, set[int]]:
    edges: dict[int, set[int]] = defaultdict(set)
    for (block_id, record_id), record in sorted(records.items()):
        if block_id != BLOCK_ID:
            continue
        for gap in record_gaps(record):
            edges[record_id].update(operands(gap, MORPHOLOGY_JUMP_RE))
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


def incoming_jump_rows(
    records: dict[tuple[int, int], Any],
    target_ids: set[int],
) -> list[list[int]]:
    rows: list[list[int]] = []
    for (block_id, record_id), record in sorted(records.items()):
        for gap_id, gap in enumerate(record_gaps(record)):
            for match in MORPHOLOGY_JUMP_RE.finditer(gap):
                operand = struct.unpack("<I", match.group(1))[0]
                if operand in target_ids:
                    rows.append(
                        [
                            block_id,
                            record_id,
                            gap_id,
                            match.start(),
                            operand,
                        ]
                    )
    return rows


def caller_rows(
    records: dict[tuple[int, int], Any],
    target_ids: set[int],
) -> tuple[list[list[object]], dict[int, tuple[str, ...]]]:
    edges = graph_edges(records)
    rows: list[list[object]] = []
    sites: dict[int, list[str]] = defaultdict(list)
    for (block_id, record_id), record in sorted(records.items()):
        for gap_id, gap in enumerate(record_gaps(record)):
            for match in MORPHOLOGY_COMMAND_RE.finditer(gap):
                operand = struct.unpack("<I", match.group(1))[0]
                terminals = tuple(
                    sorted(graph_closure(edges, operand).intersection(target_ids))
                )
                if not terminals:
                    continue
                coordinate = (
                    f"{block_id}:{record_id}:{gap_id}:{match.start()}"
                )
                sites[operand].append(coordinate)
                rows.append(
                    [
                        operand,
                        block_id,
                        record_id,
                        gap_id,
                        match.start(),
                        list(terminals),
                        hashlib.sha256(record.data).hexdigest().upper(),
                        gap.hex().upper(),
                    ]
                )
    return rows, {
        root: tuple(root_sites) for root, root_sites in sites.items()
    }


def assert_corpora(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    for label, records in records_by_label.items():
        keys = PK_RECORD_KEYS if label.startswith("pk_") else RECORD_KEYS
        if GENERAL.subset_digest(records, keys) != ARCHIVE_DIGESTS[label]:
            raise RuntimeError(f"segment {SEGMENT} {label} corpus drifted")

    for record_id in RECORD_IDS:
        base_key = (BLOCK_ID, record_id)
        pk_key = PK_RECORD_MAP[base_key]
        for label in ("base_jp", "base_current", "base_sc", "base_tc"):
            if (
                len(literal_texts(records_by_label[label], base_key)) != 1
                or record_gaps(records_by_label[label][base_key])
                != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base record/gap drifted: "
                    f"{label}/{base_key}"
                )
        for label in (
            "pk_jp",
            "pk_current",
            "pk_sc",
            "pk_tc",
            "pk_en",
        ):
            if (
                len(literal_texts(records_by_label[label], pk_key)) != 1
                or record_gaps(records_by_label[label][pk_key])
                != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} PK record/gap drifted: "
                    f"{label}/{pk_key}"
                )
        if literal_texts(records_by_label["base_jp"], base_key) != (
            EXPECTED_JP[record_id],
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base source text drifted: {base_key}"
            )
        if literal_texts(records_by_label["pk_jp"], pk_key) != (
            EXPECTED_JP[record_id],
        ):
            raise RuntimeError(
                f"segment {SEGMENT} PK source mapping drifted: {pk_key}"
            )
        for language in ("jp", "current", "sc", "tc"):
            if (
                records_by_label[f"base_{language}"][base_key].data
                != records_by_label[f"pk_{language}"][pk_key].data
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base/PK {language} mapping drifted: "
                    f"{base_key}/{pk_key}"
                )
        for label, key in (
            ("base_sc", base_key),
            ("base_tc", base_key),
            ("pk_sc", pk_key),
            ("pk_tc", pk_key),
            ("pk_en", pk_key),
        ):
            if literal_texts(records_by_label[label], key) != ("",):
                raise RuntimeError(
                    f"segment {SEGMENT} blank context drifted: {label}/{key}"
                )


def assert_jump_and_call_graphs(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    targets_by_label = {
        "base_jp": set(RECORD_IDS),
        "base_current": set(RECORD_IDS),
        "pk_jp": {record_id + 54 for record_id in RECORD_IDS},
        "pk_current": {record_id + 54 for record_id in RECORD_IDS},
    }
    for label, target_ids in targets_by_label.items():
        records = records_by_label[label]
        jump_rows = incoming_jump_rows(records, target_ids)
        expected_count, expected_sha256 = JUMP_EVIDENCE[label]
        actual_sha256 = hashlib.sha256(
            json.dumps(jump_rows, separators=(",", ":")).encode("ascii")
        ).hexdigest().upper()
        if (
            len(jump_rows) != expected_count
            or actual_sha256 != expected_sha256
            or {row[4] for row in jump_rows} != target_ids
            or any(
                sum(row[4] == target for row in jump_rows) != 1
                for target in target_ids
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} incoming 014A graph drifted"
            )

        edges = graph_edges(records)
        offset = 54 if label.startswith("pk_") else 0
        for root, record_ids in ROOT_TERMINALS.items():
            actual = tuple(
                sorted(
                    graph_closure(edges, root).intersection(target_ids)
                )
            )
            expected = tuple(record_id + offset for record_id in record_ids)
            if actual != expected:
                raise RuntimeError(
                    f"segment {SEGMENT} {label} terminal closure drifted: "
                    f"{root}"
                )

        rows, sites = caller_rows(records, target_ids)
        expected_calls = CALL_EVIDENCE[label]
        if set(sites) != set(expected_calls):
            raise RuntimeError(
                f"segment {SEGMENT} {label} 0143 root universe drifted"
            )
        for root, (expected_site_count, expected_site_sha256) in (
            expected_calls.items()
        ):
            actual_sites = sites[root]
            actual_site_sha256 = hashlib.sha256(
                "\n".join(actual_sites).encode("ascii")
            ).hexdigest().upper()
            if (
                len(actual_sites) != expected_site_count
                or actual_site_sha256 != expected_site_sha256
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {label} 0143 calls drifted: {root}"
                )
        caller_sha256 = hashlib.sha256(
            json.dumps(rows, separators=(",", ":")).encode("ascii")
        ).hexdigest().upper()
        if caller_sha256 != CALLER_EVIDENCE_SHA256[label]:
            raise RuntimeError(
                f"segment {SEGMENT} {label} caller record/gap drifted"
            )

    for side in ("base", "pk"):
        source_targets = targets_by_label[f"{side}_jp"]
        current_targets = targets_by_label[f"{side}_current"]
        _, source_sites = caller_rows(
            records_by_label[f"{side}_jp"],
            source_targets,
        )
        _, current_sites = caller_rows(
            records_by_label[f"{side}_current"],
            current_targets,
        )
        roots = set(source_sites) | set(current_sites)
        actual_flattened = {
            root: tuple(
                sorted(set(source_sites.get(root, ())) - set(
                    current_sites.get(root, ())
                ))
            )
            for root in roots
            if set(source_sites.get(root, ()))
            != set(current_sites.get(root, ()))
        }
        current_only = {
            root: tuple(
                sorted(set(current_sites.get(root, ())) - set(
                    source_sites.get(root, ())
                ))
            )
            for root in roots
            if set(current_sites.get(root, ()))
            - set(source_sites.get(root, ()))
        }
        if (
            actual_flattened != SOURCE_ONLY_FLATTENED_CALLS[side]
            or current_only
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {side} flattened caller drifted"
            )


def assert_014c_false_positive_guard(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    for label in (
        "base_jp",
        "base_current",
        "pk_jp",
        "pk_current",
    ):
        valid: list[tuple[int, int, int, int, int]] = []
        overlapped: list[tuple[int, int, int, int, int]] = []
        for (block_id, record_id), record in sorted(
            records_by_label[label].items()
        ):
            for gap_id, gap in enumerate(record_gaps(record)):
                jump_spans = [
                    range(match.start(), match.end())
                    for match in MORPHOLOGY_JUMP_RE.finditer(gap)
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
        if (
            tuple(valid) != VALID_014C_EVIDENCE[label]
            or tuple(overlapped) != OVERLAPPED_014C_EVIDENCE[label]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} 014C evidence drifted"
            )


def assert_semantics(translations: dict[str, str]) -> None:
    if (
        len(RECORD_IDS) != 67
        or set(EXPECTED_JP) != set(RECORD_IDS)
        or set(TRANSLATIONS_BY_RECORD) != set(RECORD_IDS)
        or set(RECORD_TO_ROOT) != set(RECORD_IDS)
        or translations != TRANSLATIONS
    ):
        raise RuntimeError(f"segment {SEGMENT} decision universe drifted")
    if TRANSLATIONS_BY_RECORD[1476] != "이런":
        raise RuntimeError("exclamatory なんと meaning drifted")
    if tuple(
        TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(1477, 1484)
    ) != (
        "황송합니다",
        "황송하다",
        "황송합니다",
        "황송하옵니다",
        "황송합니다",
        "황송합니다",
        "황송하다",
    ):
        raise RuntimeError("恐れ入る register matrix drifted")
    if tuple(
        TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(1484, 1491)
    ) != (
        "생각합니다",
        "생각한다",
        "생각하옵니다",
        "생각하옵니다",
        "생각하옵니다",
        "생각하오",
        "생각하오",
    ):
        raise RuntimeError("思う/存ずる register matrix drifted")
    if tuple(
        TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(1491, 1498)
    ) != ("어머", "어라", "어머나", "아니", "어머", "흠", "으음"):
        raise RuntimeError("interjection register matrix drifted")
    if tuple(
        TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(1526, 1533)
    ) != ("다니", "나", "다니", "나", "네", "나", "나"):
        raise RuntimeError("PK-observed bound exclamation matrix drifted")
    if any(
        TRANSLATIONS_BY_RECORD[record_id] != "지만"
        for record_id in range(1540, 1543)
    ):
        raise RuntimeError("bound contrastive matrix drifted")
    for left, right in (
        (1498, 1533),
        (1499, 1534),
        (1502, 1535),
        (1502, 1536),
        (1502, 1537),
        (1503, 1538),
        (1504, 1539),
    ):
        if TRANSLATIONS_BY_RECORD[left] != TRANSLATIONS_BY_RECORD[right]:
            raise RuntimeError(
                f"question-ending exact reuse drifted: {left}/{right}"
            )


def build_rows() -> tuple[Any, list[dict[str, object]], str]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    records_by_label = archive_records(prepared)
    assert_corpora(records_by_label)
    assert_jump_and_call_graphs(records_by_label)
    assert_014c_false_positive_guard(records_by_label)
    assert_semantics(TRANSLATIONS)

    current = records_by_label["base_current"]
    for coordinate, translation in TRANSLATIONS.items():
        _, record_id, _ = (int(value) for value in coordinate.split(":"))
        current_text = literal_texts(current, (BLOCK_ID, record_id))[0]
        if (
            not ENGINE.is_visible_translation_candidate(current_text)
            or "\n" in current_text
            or current_text != current_text.strip()
            or "\n" in translation
            or translation != translation.strip()
            or UTIL.layout_signature(translation)
            != UTIL.layout_signature(current_text)
            or "\r" in translation
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} line/signature drifted: {coordinate}"
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
        evidence: dict[str, object] = {
            "base_root": root,
            "incoming_014a_guarded": True,
            "valid_incoming_014c_count": 0,
            "base_source_call_count": CALL_EVIDENCE["base_jp"].get(
                root,
                (0, ""),
            )[0],
            "base_current_call_count": CALL_EVIDENCE[
                "base_current"
            ].get(root, (0, ""))[0],
            "pk_source_call_count": CALL_EVIDENCE["pk_jp"].get(
                root,
                (0, ""),
            )[0],
            "pk_current_call_count": CALL_EVIDENCE["pk_current"].get(
                root,
                (0, ""),
            )[0],
            "assembly_class": ASSEMBLY_CLASS[root],
            "caller_rewrite_required_before_runtime_approval": True,
        }
        if record_id in (1495, 1496):
            evidence["pk_additional_direct_root"] = 237
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
                "runtime_assembly_evidence": evidence,
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
        raise RuntimeError(f"segment {SEGMENT} validation count drifted")

    current = archive_records(prepared)["base_current"]
    changed = sum(
        translation
        != literal_texts(current, (BLOCK_ID, int(coordinate.split(":")[1])))[
            0
        ]
        for coordinate, translation in TRANSLATIONS.items()
    )
    decision_sha256 = hashlib.sha256(OUTPUT.read_bytes()).hexdigest().upper()
    builder_sha256 = hashlib.sha256(SCRIPT.read_bytes()).hexdigest().upper()
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B002_S1007",
                "queue": "base_msggame-B002",
                "source_literal_count": 67,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "changed_literal_count": changed,
                "base_pk_record_offset": 54,
                "base_pk_jp_current_sc_tc_divergence_records": [],
                "pk_en_visible_records": [],
                "incoming_014a_count_base": 67,
                "incoming_014a_count_pk": 67,
                "valid_incoming_014c_count": 0,
                "overlapped_014c_false_positive_count": 1,
                "base_source_caller_count": sum(
                    count for count, _ in CALL_EVIDENCE["base_jp"].values()
                ),
                "base_current_caller_count": sum(
                    count
                    for count, _ in CALL_EVIDENCE["base_current"].values()
                ),
                "pk_source_caller_count": sum(
                    count for count, _ in CALL_EVIDENCE["pk_jp"].values()
                ),
                "pk_current_caller_count": sum(
                    count
                    for count, _ in CALL_EVIDENCE["pk_current"].values()
                ),
                "candidate_sha256": candidate_sha256,
                "decision_sha256": decision_sha256,
                "builder_sha256": builder_sha256,
                "target_source_current_records_and_gaps_exact": True,
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
