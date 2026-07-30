#!/usr/bin/env python3
"""Build Base block-0 runtime-terminal segment 1010 decisions."""

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

import build_base_batch002_segment1008 as PREVIOUS
import build_base_batch003_segment1009 as PRIOR_SEGMENT


ENGINE = PREVIOUS.ENGINE
GENERAL = PREVIOUS.GENERAL
UTIL = PREVIOUS.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B003_S1010.private.v1.jsonl"
)
SEGMENT = 1010
QUEUE_BATCH_ID = "base_msggame-B003"
BLOCK_ID = 0
RECORD_IDS = tuple(range(1676, 1743))
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
PK_RECORD_OFFSET = 61
PK_RECORD_MAP = {
    (BLOCK_ID, record_id): (
        BLOCK_ID,
        record_id + PK_RECORD_OFFSET,
    )
    for record_id in RECORD_IDS
}

# The terminal tables are not monotonically rooted.  In particular, the two
# tables at 1708..1721 are selected through the distant roots 1132 and 1138.
# These are the actual 014A closures, not inferred ordinal labels.
FULL_TERMINAL_GROUPS = {
    388: tuple(range(1673, 1680)),
    394: tuple(range(1680, 1687)),
    400: tuple(range(1687, 1694)),
    406: tuple(range(1694, 1701)),
    412: tuple(range(1701, 1708)),
    1132: tuple(range(1708, 1715)),
    1138: tuple(range(1715, 1722)),
    418: tuple(range(1722, 1729)),
    424: tuple(range(1729, 1736)),
    430: tuple(range(1736, 1743)),
}
TERMINAL_GROUPS = {
    root: tuple(
        record_id
        for record_id in record_ids
        if record_id in RECORD_IDS
    )
    for root, record_ids in FULL_TERMINAL_GROUPS.items()
}
PK_ROOT_MAP = {
    388: 394,
    394: 400,
    400: 406,
    406: 412,
    412: 418,
    1132: 1144,
    1138: 1150,
    418: 424,
    424: 430,
    430: 436,
}

SOURCE_JP_BY_ROOT = {
    388: (
        "ございません",
        "ござらぬ",
        "ございません",
        "ございません",
        "ございません",
        "ござらぬ",
        "ござらぬ",
    ),
    394: (
        "しません",
        "さぬ",
        "しませぬ",
        "しません",
        "しません",
        "しませぬ",
        "さぬ",
    ),
    400: (
        "しています",
        "しておる",
        "しております",
        "しておりまする",
        "しています",
        "しております",
        "しておる",
    ),
    406: (
        "ください",
        "してくれ",
        "ください",
        "くだされ",
        "ください",
        "あれ",
        "してくれ",
    ),
    412: (
        "じています",
        "じておる",
        "じております",
        "じておりまする",
        "じています",
        "じております",
        "じておる",
    ),
    1132: (
        "しなければ",
        "せねば",
        "しなければ",
        "せねば",
        "しなければ",
        "せねば",
        "せねば",
    ),
    1138: (
        "しまいました",
        "しまった",
        "しまいました",
        "しまいました",
        "しまいました",
        "しまいました",
        "しまった",
    ),
    418: (
        "しましょう",
        "しよう",
        "いたしましょう",
        "いたしましょう",
        "しましょう",
        "いたそう",
        "せん",
    ),
    424: (
        "じましょう",
        "じよう",
        "じましょう",
        "じましょう",
        "じましょう",
        "ずるといたそう",
        "じよう",
    ),
    430: (
        "じてください",
        "ぜよ",
        "じてください",
        "じてくだされ",
        "じてください",
        "じてくだされ",
        "じろ",
    ),
}
TRANSLATION_POLICY_BY_ROOT = {
    388: (
        "없습니다",
        "없소",
        "없습니다",
        "없습니다",
        "없습니다",
        "없소",
        "없소",
    ),
    394: (
        "하지 않습니다",
        "하지 않는다",
        "하지 않사옵니다",
        "하지 않습니다",
        "하지 않습니다",
        "하지 않사옵니다",
        "하지 않는다",
    ),
    400: (
        "하고 있습니다",
        "하고 있다",
        "하고 있습니다",
        "하고 있사옵니다",
        "하고 있습니다",
        "하고 있습니다",
        "하고 있다",
    ),
    406: (
        "해 주십시오",
        "해 다오",
        "해 주십시오",
        "해 주시오",
        "해 주십시오",
        "하시라",
        "해 다오",
    ),
    412: (
        "하고 있습니다",
        "하고 있다",
        "하고 있습니다",
        "하고 있사옵니다",
        "하고 있습니다",
        "하고 있습니다",
        "하고 있다",
    ),
    1132: (
        "하지 않으면",
        "해야만",
        "하지 않으면",
        "해야만",
        "하지 않으면",
        "해야만",
        "해야만",
    ),
    1138: (
        "버렸습니다",
        "버렸다",
        "버렸습니다",
        "버렸습니다",
        "버렸습니다",
        "버렸습니다",
        "버렸다",
    ),
    418: (
        "합시다",
        "하자",
        "하겠습니다",
        "하겠습니다",
        "합시다",
        "하겠소",
        "하자",
    ),
    424: (
        "합시다",
        "하자",
        "합시다",
        "합시다",
        "합시다",
        "하기로 하겠소",
        "하자",
    ),
    430: (
        "해 주십시오",
        "하라",
        "해 주십시오",
        "해 주시오",
        "해 주십시오",
        "해 주시오",
        "하라",
    ),
}
EXPECTED_FULL_BASE_JP = {
    record_id: source
    for root, record_ids in FULL_TERMINAL_GROUPS.items()
    for record_id, source in zip(
        record_ids,
        SOURCE_JP_BY_ROOT[root],
        strict=True,
    )
}
FULL_TRANSLATION_POLICY = {
    record_id: translation
    for root, record_ids in FULL_TERMINAL_GROUPS.items()
    for record_id, translation in zip(
        record_ids,
        TRANSLATION_POLICY_BY_ROOT[root],
        strict=True,
    )
}
EXPECTED_BASE_JP = {
    record_id: EXPECTED_FULL_BASE_JP[record_id]
    for record_id in RECORD_IDS
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_PK_JP[1728] = "しよう"
TRANSLATIONS_BY_RECORD = {
    record_id: FULL_TRANSLATION_POLICY[record_id]
    for record_id in RECORD_IDS
}
RAW_TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}
CROSS_SEGMENT_CURRENT_KO = {
    1673: "아닙니다",
    1674: "없소",
    1675: "아닙니다",
}
CROSS_SEGMENT_TRANSLATION_POLICY = {
    record_id: FULL_TRANSLATION_POLICY[record_id]
    for record_id in range(1673, 1676)
}

ARCHIVE_DIGESTS = {
    "base_jp": "BB53FAEDEBCDF25A3D7DAFB0EFC6115CA6ECAA8FE1B0CE6CD1F38CB74884D854",
    "base_current": "59D2C6E57E90B165783F9BFF4EBA12229EA70E9E50AE8B5122F9FC4927B3C434",
    "base_sc": "18619A2EF839462B977E6B13AAF360E57264A1096CBF5F7DB7EBCD42BAEBEEEE",
    "base_tc": "18619A2EF839462B977E6B13AAF360E57264A1096CBF5F7DB7EBCD42BAEBEEEE",
    "pk_jp": "77AD86E000B51F329427F3B025FB635FCF528F2061D0C32573FCAED53A3E0EC3",
    "pk_current": "A78308F6A91177E37A78548736057CA8C3087E076E3E03039373F2C3711FDDDB",
    "pk_sc": "A85C131A1F987E95C3440588B5D96AB578FA0311B471BD3E6C0DCAD665A33EA3",
    "pk_tc": "A85C131A1F987E95C3440588B5D96AB578FA0311B471BD3E6C0DCAD665A33EA3",
    "pk_en": "A85C131A1F987E95C3440588B5D96AB578FA0311B471BD3E6C0DCAD665A33EA3",
}
BASE_PK_LITERAL_DIVERGENCES = {
    "jp": (1728,),
    "current": (1728,),
    "sc": (),
    "tc": (),
}
TARGET_JUMP_EDGE_SHA256 = {
    "base": "CE467F83AE1BC85D87F810EC85F1D2559EEC7BDED3CEF704A867A7EC6F72E09A",
    "pk": "199BCFBFDCB9B50882BD35C4CD728D5F05BAFE8DF40BC3F15BD15C0B6C7D4CBC",
}
FULL_GROUP_JUMP_EDGE_SHA256 = {
    "base": "EC5CCC056E114FEA9315BA0B5D364D61D86C4705E1AEA745A809B6472A3E272D",
    "pk": "CFA5D5B4833B1DAC6ED8F1D4D77A4FF8056BDB339EF9CFC98AC2DDDB9DF50E5F",
}
EXPECTED_RAW_014C = {
    "base_jp": ("15:25:0:193:inside_014A",),
    "base_current": ("15:25:0:193:inside_014A",),
    "pk_jp": ("15:25:0:65:inside_014A",),
    "pk_current": ("15:25:0:65:inside_014A",),
}

EMPTY_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
ROOT_CALL_EVIDENCE = {
    "base": {
        388: {
            "source": (5, "DAA98E8D640CADE66915274436611EAF2A372D80B41CABD42425F771DEE52A58"),
            "current": (3, "9B4AA5A50549DF5A31A309B0DAF26DB8EC0356C8C800806FFD612344B356A48F"),
        },
        394: {"source": (0, EMPTY_SHA256), "current": (0, EMPTY_SHA256)},
        400: {
            "source": (7, "EB6E9144FD70271245E7974095E85B26A518B1A84000638665F4D834C48D4BDD"),
            "current": (5, "F92FCC74C8C21F4FD14BF14CF9239131AC93C887764F95D7F722686F4F031A1C"),
        },
        406: {
            "source": (15, "E81FB63C55E3744AF066573579549BBAF165B290DD71584386E308EE33D0C379"),
            "current": (11, "00DB2F39612EB13AE3842400513A63E01E3D123D6148C7FBCD46FB919FA4089B"),
        },
        412: {
            "source": (1, "1539B8ACFE0B38773C923BAB58ABDFEA65B0B28076448C7B1FDD0DA6D5C70879"),
            "current": (1, "1539B8ACFE0B38773C923BAB58ABDFEA65B0B28076448C7B1FDD0DA6D5C70879"),
        },
        1132: {
            "source": (2, "5A567E80955A069D9D572529499EFE845A999BF53BF5B54C1FBB8FA4A17711CA"),
            "current": (2, "5A567E80955A069D9D572529499EFE845A999BF53BF5B54C1FBB8FA4A17711CA"),
        },
        1138: {
            "source": (1, "99AEEEC2B4591ED3E4F0C4D3EBDC655C01A2DB3E94A19D4C3AD2D172AE051DA5"),
            "current": (1, "99AEEEC2B4591ED3E4F0C4D3EBDC655C01A2DB3E94A19D4C3AD2D172AE051DA5"),
        },
        418: {
            "source": (10, "8C07AAB9C1EFA050BD2E7CEE0FA0649D61099649BCC0CB4A2785741132C47281"),
            "current": (10, "8C07AAB9C1EFA050BD2E7CEE0FA0649D61099649BCC0CB4A2785741132C47281"),
        },
        424: {
            "source": (1, "433CB54141D731B4CFEF2F961256404AD70D947218FC6CEE20AB66E8738BC187"),
            "current": (1, "433CB54141D731B4CFEF2F961256404AD70D947218FC6CEE20AB66E8738BC187"),
        },
        430: {"source": (0, EMPTY_SHA256), "current": (0, EMPTY_SHA256)},
    },
    "pk": {
        388: {
            "source": (5, "8344E369C1319FF7A5F868D179FAEC1D23B28ED50A5C24E2C5EE789BFFCAC9E0"),
            "current": (3, "EF7A5583C4C06C71D4747FCBD5DBF9E57D71C35266CBBE3F8026E8DE5908AE12"),
        },
        394: {"source": (0, EMPTY_SHA256), "current": (0, EMPTY_SHA256)},
        400: {
            "source": (8, "F36F7276BAE7A9C171934DFDE659317F8A414B4ABE13290A961A7659BEB5A8C2"),
            "current": (6, "4197E45A67FD6AC4E1D02FCB0030E3FA9A8BAA233D0723B63CF2C696FD424CFE"),
        },
        406: {
            "source": (21, "D6678CA32D5DB7C14B6573EAC864EC580AC540F34C7AC1EF8BB5F62AE63B7FA7"),
            "current": (17, "657657B52F75D40B12933394252FB8C19E498D720B6B1FAD6384193B12A65742"),
        },
        412: {
            "source": (1, "F056644404A9D6E61270A9A60E52B2D86317CD325630425F8BF06B9B37129D02"),
            "current": (1, "F056644404A9D6E61270A9A60E52B2D86317CD325630425F8BF06B9B37129D02"),
        },
        1132: {
            "source": (4, "284573BCF5A85C2CDF5F962BD41AD01E6FC216F615F9DBD24A886ED860B84015"),
            "current": (4, "284573BCF5A85C2CDF5F962BD41AD01E6FC216F615F9DBD24A886ED860B84015"),
        },
        1138: {
            "source": (1, "CEB9DC11458D677F1B0B05059CD50E5C4BE20ADA3FE3CCBCE6763C61A60C9023"),
            "current": (1, "CEB9DC11458D677F1B0B05059CD50E5C4BE20ADA3FE3CCBCE6763C61A60C9023"),
        },
        418: {
            "source": (16, "D1996AABEFF05653B5040F488D05D3A3E0CEBFC3AE768162C43B4694E9300276"),
            "current": (15, "55ECD6A71529D0BE138E35887BEB328DB32C6DA316093C339102FF302D956EC4"),
        },
        424: {
            "source": (3, "6CAE3A9368B6F2F1671EA965F1DFE40597BFF98495BBAB22671A16D94D1D4A77"),
            "current": (1, "433CB54141D731B4CFEF2F961256404AD70D947218FC6CEE20AB66E8738BC187"),
        },
        430: {"source": (0, EMPTY_SHA256), "current": (0, EMPTY_SHA256)},
    },
}
SOURCE_ONLY_FLATTENED_CALLS = {
    "base": {
        388: ("13:110:1:0", "13:116:1:0"),
        400: ("6:4151:1:0", "6:4171:1:0"),
        406: (
            "2:246:3:0",
            "15:220:4:0",
            "15:246:3:0",
            "15:2194:3:0",
        ),
    },
    "pk": {
        388: ("13:110:1:0", "13:116:1:0"),
        400: ("6:4181:1:0", "6:4201:1:0"),
        406: (
            "2:252:3:0",
            "15:223:4:0",
            "15:249:3:0",
            "15:2224:3:0",
        ),
        418: ("6:4346:1:0",),
        424: ("6:4687:1:0", "6:4688:1:0"),
    },
}
FIXED_FOLLOWING_BLOCKERS = {
    "base": {
        388: ("6:3639:2",),
        394: (),
        400: ("6:3616:1", "8:319:2"),
        406: (),
        412: (),
        1132: ("7:2442:2",),
        1138: (),
        418: (),
        424: (),
        430: (),
    },
    "pk": {
        388: (),
        394: (),
        400: ("6:3623:1", "6:4635:1", "8:329:2"),
        406: (),
        412: (),
        1132: ("6:4627:1", "6:4683:1", "7:2488:2"),
        1138: (),
        418: ("15:1537:3",),
        424: (),
        430: (),
    },
}
BLOCKER_RECORD_DIGESTS = {
    "base_jp": "34FECDB90ED7637D3A7CBE8CAC5513E75B8F22A41598EFDC6B658F1F456AE24C",
    "base_current": "09E8AB345B6C6736CBAB4CCDD6E934840A1F0D1DD9B2BC1C1C8703CF8E7A7E99",
    "pk_jp": "09B0099B773FC037D65C0FFB081932FAAA76FA8DABEEFB819521BE4DE148925B",
    "pk_current": "7637AF58CA2B0735BA5B8E745873A737A33C333C76EB7D227FEB9BA20941A54B",
}
ROOT_ASSEMBLY_PLAN = {
    388: "existential/apology caller rewritten before 없습니다/없소",
    394: "action predicate normalized before full negative terminal",
    400: "action predicate normalized before progressive terminal",
    406: "action noun normalized before 해 주십시오/해 다오/하시라",
    412: "voiced action predicate normalized before progressive terminal",
    1132: "conditional or elliptical obligation caller rewritten by context",
    1138: "action connective normalized before completive past terminal",
    418: "action predicate normalized before volitional/intention terminal",
    424: "voiced action predicate normalized before volitional terminal",
    430: "voiced action predicate normalized before imperative terminal",
}
MORPHOLOGY_COMMAND_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)
MORPHOLOGY_JUMP_RE = re.compile(b"\x01\x4A(.{4})", re.DOTALL)
BASIS = (
    "review_queue_base_msggame_B003_pristine_base_pc_jp_sole_authority_"
    "block0_runtime_voice_terminal_records1676_1742_literal0_with_"
    "root388_cross_segment_records1673_1679_exact_plus61_pk_record_"
    "mapping_nonordinal_base_roots1132_1138_and_explicit_pk_root_map_"
    "base_pk_record1728_sen_shiyou_positive_volitional_divergence_"
    "all_014a_terminal_edges_graph_closures_0143_call_sites_raw_014c_"
    "classification_source_current_flattening_fixed_following_blockers_"
    "negative_progressive_request_conditional_completive_volitional_"
    "imperative_polarity_tense_and_register_matrices_runtime_pending_"
    "one_line_skeleton_outside_scope_reverse_overlay_no_korean_authority"
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


def root_call_sites(
    records: dict[tuple[int, int], Any],
    root: int,
) -> tuple[str, ...]:
    return tuple(
        f"{key[0]}:{key[1]}:{gap_id}:{match.start()}"
        for key in sorted(records)
        for gap_id, gap in enumerate(gap_bytes(records[key]))
        for match in MORPHOLOGY_COMMAND_RE.finditer(gap)
        if struct.unpack("<I", match.group(1))[0] == root
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

    divergences = {
        language: []
        for language in ("jp", "current", "sc", "tc")
    }
    for record_id in RECORD_IDS:
        key = (BLOCK_ID, record_id)
        mapped = PK_RECORD_MAP[key]
        if literal_texts(records_by_label["base_jp"], key) != (
            EXPECTED_BASE_JP[record_id],
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base JP drifted: {record_id}"
            )
        if literal_texts(records_by_label["pk_jp"], mapped) != (
            EXPECTED_PK_JP[record_id],
        ):
            raise RuntimeError(
                f"segment {SEGMENT} PK JP drifted: {record_id}"
            )
        for label in ("base_jp", "base_current", "base_sc", "base_tc"):
            if (
                len(literal_texts(records_by_label[label], key)) != 1
                or gap_bytes(records_by_label[label][key])
                != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base skeleton drifted: "
                    f"{label}/{record_id}"
                )
        for label in ("pk_jp", "pk_current", "pk_sc", "pk_tc", "pk_en"):
            if (
                len(literal_texts(records_by_label[label], mapped)) != 1
                or gap_bytes(records_by_label[label][mapped])
                != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} PK skeleton drifted: "
                    f"{label}/{record_id}"
                )
        for language in divergences:
            if literal_texts(
                records_by_label[f"base_{language}"],
                key,
            ) != literal_texts(
                records_by_label[f"pk_{language}"],
                mapped,
            ):
                divergences[language].append(record_id)
        if literal_texts(records_by_label["pk_en"], mapped) != ("",):
            raise RuntimeError(
                f"segment {SEGMENT} PK EN became visible: {record_id}"
            )

    if {
        language: tuple(record_ids)
        for language, record_ids in divergences.items()
    } != BASE_PK_LITERAL_DIVERGENCES:
        raise RuntimeError(
            f"segment {SEGMENT} Base/PK divergences drifted"
        )
    if (
        literal_texts(records_by_label["base_current"], (0, 1728))
        != ("않다",)
        or literal_texts(records_by_label["pk_current"], (0, 1789))
        != ("하자",)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} record1728 current divergence drifted"
        )

    for record_id in range(1673, 1676):
        key = (BLOCK_ID, record_id)
        mapped = (BLOCK_ID, record_id + PK_RECORD_OFFSET)
        if (
            literal_texts(records_by_label["base_jp"], key)
            != (EXPECTED_FULL_BASE_JP[record_id],)
            or literal_texts(records_by_label["base_current"], key)
            != (CROSS_SEGMENT_CURRENT_KO[record_id],)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} root388 boundary drifted: "
                f"{record_id}"
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
                    f"segment {SEGMENT} root388 mapping drifted: "
                    f"{language}/{record_id}"
                )
        for label in ("base_jp", "base_current", "base_sc", "base_tc"):
            if gap_bytes(records_by_label[label][key]) != (
                b"",
                b"\x05\x05\x05",
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} boundary Base gap drifted"
                )
        for label in ("pk_jp", "pk_current", "pk_sc", "pk_tc", "pk_en"):
            if gap_bytes(records_by_label[label][mapped]) != (
                b"",
                b"\x05\x05\x05",
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} boundary PK gap drifted"
                )
        if literal_texts(records_by_label["pk_en"], mapped) != ("",):
            raise RuntimeError(
                f"segment {SEGMENT} boundary PK EN became visible"
            )


def assert_runtime_graph(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    all_base_terminals = {
        record_id
        for record_ids in FULL_TERMINAL_GROUPS.values()
        for record_id in record_ids
    }
    if (
        len(all_base_terminals) != 70
        or set().union(*map(set, TERMINAL_GROUPS.values()))
        != set(RECORD_IDS)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} terminal universe drifted"
        )

    for edition, offset in (("base", 0), ("pk", PK_RECORD_OFFSET)):
        target_ids = {
            record_id + offset for record_id in RECORD_IDS
        }
        full_ids = {
            record_id + offset for record_id in all_base_terminals
        }
        for corpus in ("jp", "current"):
            records = records_by_label[f"{edition}_{corpus}"]
            for label, target, expected_count, expected_sha256 in (
                (
                    "target",
                    target_ids,
                    67,
                    TARGET_JUMP_EDGE_SHA256[edition],
                ),
                (
                    "full",
                    full_ids,
                    70,
                    FULL_GROUP_JUMP_EDGE_SHA256[edition],
                ),
            ):
                edges = [
                    [block_id, record_id, operand]
                    for (block_id, record_id), record in sorted(
                        records.items()
                    )
                    for operand in PREVIOUS.PREVIOUS.operands(
                        record.data,
                        MORPHOLOGY_JUMP_RE,
                    )
                    if operand in target
                ]
                actual_sha256 = hashlib.sha256(
                    json.dumps(
                        edges,
                        separators=(",", ":"),
                    ).encode("ascii")
                ).hexdigest().upper()
                if (
                    len(edges) != expected_count
                    or actual_sha256 != expected_sha256
                    or {edge[2] for edge in edges} != target
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} {edition}_{corpus} "
                        f"{label} 014A edges drifted"
                    )

            graph: dict[int, set[int]] = defaultdict(set)
            for (block_id, record_id), record in records.items():
                if block_id != BLOCK_ID:
                    continue
                graph[record_id].update(
                    PREVIOUS.PREVIOUS.operands(
                        record.data,
                        MORPHOLOGY_JUMP_RE,
                    )
                )
            for base_root, base_terminals in (
                FULL_TERMINAL_GROUPS.items()
            ):
                actual_root = (
                    base_root
                    if edition == "base"
                    else PK_ROOT_MAP[base_root]
                )
                expected_terminals = {
                    record_id + offset
                    for record_id in base_terminals
                }
                actual_terminals = (
                    graph_closure(graph, actual_root) & full_ids
                )
                if actual_terminals != expected_terminals:
                    raise RuntimeError(
                        f"segment {SEGMENT} {edition}_{corpus} "
                        f"root closure drifted: {base_root}/"
                        f"{actual_root}"
                    )

    for edition in ("base", "pk"):
        source_records = records_by_label[f"{edition}_jp"]
        current_records = records_by_label[f"{edition}_current"]
        for base_root in FULL_TERMINAL_GROUPS:
            actual_root = (
                base_root
                if edition == "base"
                else PK_ROOT_MAP[base_root]
            )
            source_sites = root_call_sites(source_records, actual_root)
            current_sites = root_call_sites(current_records, actual_root)
            for corpus, sites in (
                ("source", source_sites),
                ("current", current_sites),
            ):
                expected_count, expected_sha256 = (
                    ROOT_CALL_EVIDENCE[edition][base_root][corpus]
                )
                actual_sha256 = hashlib.sha256(
                    "\n".join(sites).encode("ascii")
                ).hexdigest().upper()
                if (
                    len(sites) != expected_count
                    or actual_sha256 != expected_sha256
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} {edition} {corpus} "
                        f"0143 calls drifted: {base_root}/"
                        f"{actual_root}"
                    )
            expected_flattened = set(
                SOURCE_ONLY_FLATTENED_CALLS[edition].get(
                    base_root,
                    (),
                )
            )
            if (
                set(source_sites) - set(current_sites)
                != expected_flattened
                or set(current_sites) - set(source_sites)
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {edition} source/current "
                    f"flattening drifted: {base_root}"
                )

    for label, expected in EXPECTED_RAW_014C.items():
        records = records_by_label[label]
        raw_014c: list[str] = []
        for key in sorted(records):
            for gap_id, gap in enumerate(gap_bytes(records[key])):
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
                        start <= position
                        and position + 2 <= end
                        for start, end in jump_spans
                    )
                    raw_014c.append(
                        f"{key[0]}:{key[1]}:{gap_id}:"
                        f"{position}:"
                        f"{'inside_014A' if inside_jump else 'standalone'}"
                    )
                    position += 1
        if tuple(raw_014c) != expected:
            raise RuntimeError(
                f"segment {SEGMENT} {label} raw 014C drifted"
            )
        if any(item.endswith(":standalone") for item in raw_014c):
            raise RuntimeError(
                f"segment {SEGMENT} valid standalone 014C appeared"
            )


def is_text_boundary(character: str) -> bool:
    return (
        character.isspace()
        or unicodedata.category(character).startswith("P")
        or character == "\u2026"
    )


def fixed_following_blockers(
    records: dict[tuple[int, int], Any],
    root: int,
) -> tuple[str, ...]:
    blockers: list[str] = []
    for key in sorted(records):
        literals = ENGINE.parse_record_literals(records[key])
        for gap_id, gap in enumerate(gap_bytes(records[key])):
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
                    blockers.append(
                        f"{key[0]}:{key[1]}:{gap_id}"
                    )
    return tuple(blockers)


def assert_fixed_following(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    for label in ("base_jp", "base_current", "pk_jp", "pk_current"):
        edition = label.split("_", 1)[0]
        records = records_by_label[label]
        blocker_keys: set[tuple[int, int]] = set()
        for base_root in FULL_TERMINAL_GROUPS:
            actual_root = (
                base_root
                if edition == "base"
                else PK_ROOT_MAP[base_root]
            )
            actual = fixed_following_blockers(records, actual_root)
            expected = FIXED_FOLLOWING_BLOCKERS[edition][base_root]
            if actual != expected:
                raise RuntimeError(
                    f"segment {SEGMENT} {label} fixed-following "
                    f"blockers drifted: {base_root}/{actual_root}"
                )
            blocker_keys.update(
                tuple(int(value) for value in site.split(":")[:2])
                for site in actual
            )

        digest = hashlib.sha256()
        for block_id, record_id in sorted(blocker_keys):
            data = records[(block_id, record_id)].data
            digest.update(
                struct.pack(
                    "<III",
                    block_id,
                    record_id,
                    len(data),
                )
            )
            digest.update(data)
        if (
            digest.hexdigest().upper()
            != BLOCKER_RECORD_DIGESTS[label]
            or len(blocker_keys) != (4 if edition == "base" else 7)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} blocker bytes drifted"
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
        CROSS_SEGMENT_TRANSLATION_POLICY[record_id]
        for record_id in range(1673, 1676)
    ) != ("없습니다", "없소", "없습니다"):
        raise RuntimeError(
            f"segment {SEGMENT} root388 boundary policy drifted"
        )
    if tuple(
        PRIOR_SEGMENT.TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(1673, 1676)
    ) != tuple(
        CROSS_SEGMENT_TRANSLATION_POLICY[record_id]
        for record_id in range(1673, 1676)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} S1009 root388 boundary drifted"
        )
    if tuple(
        FULL_TRANSLATION_POLICY[record_id]
        for record_id in range(1673, 1680)
    ) != (
        "없습니다",
        "없소",
        "없습니다",
        "없습니다",
        "없습니다",
        "없소",
        "없소",
    ):
        raise RuntimeError(
            f"segment {SEGMENT} full root388 matrix drifted"
        )
    for root, record_ids in TERMINAL_GROUPS.items():
        actual = tuple(
            translations[f"0:{record_id}:0"]
            for record_id in record_ids
        )
        full_ids = FULL_TERMINAL_GROUPS[root]
        start = full_ids.index(record_ids[0])
        expected = TRANSLATION_POLICY_BY_ROOT[root][
            start : start + len(record_ids)
        ]
        if actual != expected:
            raise RuntimeError(
                f"segment {SEGMENT} register matrix drifted: {root}"
            )
    if (
        translations["0:1699:0"] != "하시라"
        or translations["0:1716:0"] != "버렸다"
        or translations["0:1721:0"] != "버렸다"
        or translations["0:1727:0"] != "하겠소"
        or translations["0:1728:0"] != "하자"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} imperative/completive/"
            "volitional semantics drifted"
        )
    for coordinate, translation in translations.items():
        if (
            "\r" in translation
            or "\n" in translation
            or translation != translation.strip()
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(
                translation
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} text residue drifted: "
                f"{coordinate}"
            )


def build_rows() -> tuple[Any, list[dict[str, object]], str]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    records_by_label = archive_records(prepared)
    assert_corpora(records_by_label)
    assert_runtime_graph(records_by_label)
    assert_fixed_following(records_by_label)

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
                    "base_root": root,
                    "pk_root": PK_ROOT_MAP[root],
                    "base_record_id": record_id,
                    "pk_record_id": record_id + PK_RECORD_OFFSET,
                    "base_jp": EXPECTED_BASE_JP[record_id],
                    "pk_jp": EXPECTED_PK_JP[record_id],
                    "base_pk_literal_divergent": (
                        record_id
                        in BASE_PK_LITERAL_DIVERGENCES["jp"]
                    ),
                    "full_terminal_record_ids": list(
                        FULL_TERMINAL_GROUPS[root]
                    ),
                    "source_call_count": (
                        ROOT_CALL_EVIDENCE["base"][root][
                            "source"
                        ][0]
                    ),
                    "current_call_count": (
                        ROOT_CALL_EVIDENCE["base"][root][
                            "current"
                        ][0]
                    ),
                    "pk_source_call_count": (
                        ROOT_CALL_EVIDENCE["pk"][root][
                            "source"
                        ][0]
                    ),
                    "pk_current_call_count": (
                        ROOT_CALL_EVIDENCE["pk"][root][
                            "current"
                        ][0]
                    ),
                    "source_only_flattened_calls": list(
                        SOURCE_ONLY_FLATTENED_CALLS[
                            "base"
                        ].get(root, ())
                    ),
                    "pk_source_only_flattened_calls": list(
                        SOURCE_ONLY_FLATTENED_CALLS[
                            "pk"
                        ].get(root, ())
                    ),
                    "fixed_following_blockers": list(
                        FIXED_FOLLOWING_BLOCKERS["base"][root]
                    ),
                    "pk_fixed_following_blockers": list(
                        FIXED_FOLLOWING_BLOCKERS["pk"][root]
                    ),
                    "assembly_plan": ROOT_ASSEMBLY_PLAN[root],
                    "automatic_space_inserted": False,
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
        raise RuntimeError(
            f"segment {SEGMENT} validation count drifted"
        )
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
        row["translation"]
        != literal_texts(
            current,
            (
                BLOCK_ID,
                int(str(row["coordinate"]).split(":")[1]),
            ),
        )[0]
        for row in rows
    )
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B003_S1010",
                "queue": QUEUE_BATCH_ID,
                "source_literal_count": 67,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "changed_literal_count": changed,
                "base_pk_record_offset": PK_RECORD_OFFSET,
                "base_pk_jp_literal_divergence_records": [1728],
                "base_pk_current_literal_divergence_records": [1728],
                "base_pk_sc_tc_gap_divergence_records": [],
                "pk_en_visible_records": [],
                "terminal_groups": {
                    str(root): list(record_ids)
                    for root, record_ids in TERMINAL_GROUPS.items()
                },
                "full_terminal_groups": {
                    str(root): list(record_ids)
                    for root, record_ids in (
                        FULL_TERMINAL_GROUPS.items()
                    )
                },
                "pk_root_map": PK_ROOT_MAP,
                "cross_segment_translation_policy": (
                    CROSS_SEGMENT_TRANSLATION_POLICY
                ),
                "source_only_flattened_calls": (
                    SOURCE_ONLY_FLATTENED_CALLS
                ),
                "fixed_following_blockers": (
                    FIXED_FOLLOWING_BLOCKERS
                ),
                "fixed_following_blocker_record_counts": {
                    "base": 4,
                    "pk": 7,
                },
                "raw_014c_standalone_command_count": 0,
                "target_jump_edge_sha256": (
                    TARGET_JUMP_EDGE_SHA256
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
                "protected_signature_exact": True,
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
