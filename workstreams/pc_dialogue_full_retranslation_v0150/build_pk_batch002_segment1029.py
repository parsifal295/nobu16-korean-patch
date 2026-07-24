#!/usr/bin/env python3
"""Build PK block-0 runtime-terminal segment 1029 decisions."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch002_segment1008 as BASE
import build_base_batch003_segment1009 as RIGHT_BASE
import build_pk_batch001_segment1025 as HELPERS


ENGINE = BASE.ENGINE
GENERAL = BASE.GENERAL
UTIL = BASE.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B002_S1029.private.v1.jsonl"
)
BASE_DECISION = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B002_S1008.private.v1.jsonl"
)
BASE_DECISION_SHA256 = (
    "BB0EE3186ECBBB1697FB5BD6625265F198BA61741586F65A5E4CEAC96B661E14"
)
SEGMENT = 1029
QUEUE_BATCH_ID = "pk_msggame-B002"
BLOCK_ID = 0
BASE_RECORD_IDS = tuple(range(1543, 1609))
RECORD_IDS = tuple(record_id + 54 for record_id in BASE_RECORD_IDS)
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
TARGET_COORDINATES = tuple(
    f"{BLOCK_ID}:{record_id}:0" for record_id in RECORD_IDS
)
EXPECTED_PK_JP = (
    "が",
    "けれども",
    "が",
    "が",
    "ありがたいこと",
    "ありがたき限り",
    "ありがとうございます",
    "恐縮にございます",
    "ありがとうございます",
    "かたじけない",
    "ありがたい",
    "だろう",
    "だろう",
    "でしょう",
    "でしょう",
    "かと",
    "かと",
    "だろう",
    "でしょうか",
    "かな",
    "でしょうか",
    "でしょうか",
    "ですか",
    "ですかな",
    "かな",
    "きません",
    "かぬ",
    "きませぬ",
    "きませぬ",
    "きません",
    "きませぬ",
    "かぬ",
    "お聞きなさい",
    "聞くがいい",
    "どうかお聞きを",
    "お聞き入れくだされ",
    "お聞きください",
    "聞いてくだされ",
    "聞いてくれ",
    "きます",
    "く",
    "きまする",
    "きます",
    "きます",
    "きまする",
    "く",
    "ぎます",
    "ぐ",
    "ぎまする",
    "ぎます",
    "ぎます",
    "ぎまする",
    "ぐ",
    "くだされ",
    "くれ",
    "くださいまし",
    "くださりませ",
    "くださいませ",
    "くだされ",
    "くれ",
    "くださった",
    "くれた",
    "くださいました",
    "くだされました",
    "くれました",
    "くださった",
)
TRANSLATION_POLICY = (
    "지만",
    "지만",
    "지만",
    "지만",
    "고마운 일이군요",
    "고마울 따름이다",
    "감사합니다",
    "황송하옵니다",
    "감사합니다",
    "황송하오",
    "고맙다",
    "이겠지",
    "이겠지",
    "이겠지요",
    "이겠지요",
    "인가 하고",
    "인가 하고",
    "이겠지",
    "일까요",
    "일까",
    "일까요",
    "일까요",
    "입니까",
    "일까 하오",
    "일까",
    "지 않습니다",
    "지 않는다",
    "지 않사옵니다",
    "지 않사옵니다",
    "지 않습니다",
    "지 않사옵니다",
    "지 않는다",
    "들으세요",
    "들어라",
    "부디 들어 주소서",
    "받아들여 주시오",
    "들어 주십시오",
    "들어 주시오",
    "들어다오",
    "합니다",
    "한다",
    "하옵니다",
    "합니다",
    "합니다",
    "하옵니다",
    "한다",
    "합니다",
    "한다",
    "하옵니다",
    "합니다",
    "합니다",
    "하옵니다",
    "한다",
    "주시오",
    "다오",
    "주십시오",
    "주소서",
    "주십시오",
    "주시오",
    "다오",
    "주셨다",
    "주었다",
    "주셨습니다",
    "주셨사옵니다",
    "주었습니다",
    "주셨다",
)
TRANSLATIONS_BY_RECORD = dict(
    zip(RECORD_IDS, TRANSLATION_POLICY, strict=True)
)
TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_CHANGED_LITERAL_COUNT = 28
EXPECTED_POLICY_SHA256 = (
    "AFCE9174685CA27A95C7E0C69526467AFE2E9E2E12AE48E5F3882BE0D565D75C"
)
EXPECTED_SEQUENCE_SHA256 = (
    "CB46944803FF63A3A4EFB394A63DDD549A92C44066874A7B8D06397BC76D52AB"
)
PK_RECORD_COUNT = 21751
PK_ARCHIVE_DIGESTS = {
    "pk_jp": "A889D2469F77930534E1913961A4AEBD212FAA2FD9AF4ABA7B20A1242108077B",
    "pk_current": "08122D87945A3CF679D8A840B62CD3BA1E331A51F3B11496C453AEA771C6BC22",
    "pk_sc": "FA0142450CF1FE03EF696F2CEEA337F4A44F2EC33282CC94B687F1B69A843A5F",
    "pk_tc": "FA0142450CF1FE03EF696F2CEEA337F4A44F2EC33282CC94B687F1B69A843A5F",
    "pk_en": "FA0142450CF1FE03EF696F2CEEA337F4A44F2EC33282CC94B687F1B69A843A5F",
}
PK_TARGET_JUMP_EDGE_SHA256 = (
    "D5E70072012E5BF6DFA22DAE88F25B56A2A93B08D2A9CFEFC263667220CB7B98"
)
PK_FULL_GROUP_JUMP_EDGE_SHA256 = (
    "DD657A716D387851EBE589432C949FF87EFB86B6A4D44F5F0BA3FF21F1806488"
)
ROOT_BY_PK_RECORD = {
    record_id + 54: root
    for root, record_ids in BASE.TERMINAL_GROUPS.items()
    for record_id in record_ids
}
EXPECTED_ROOT_CLOSURES = {
    274: tuple(range(274, 280)) + tuple(range(1594, 1601)),
    280: tuple(range(280, 286)) + tuple(range(1601, 1608)),
    286: tuple(range(286, 292)) + tuple(range(1608, 1615)),
    292: tuple(range(292, 298)) + tuple(range(1615, 1622)),
    298: tuple(range(298, 304)) + tuple(range(1622, 1629)),
    304: tuple(range(304, 310)) + tuple(range(1629, 1636)),
    310: tuple(range(310, 316)) + tuple(range(1636, 1643)),
    316: tuple(range(316, 322)) + tuple(range(1643, 1650)),
    322: tuple(range(322, 328)) + tuple(range(1650, 1657)),
    328: tuple(range(328, 334)) + tuple(range(1657, 1664)),
}
EMPTY_CANONICAL_SHA256 = (
    "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
)
EXPECTED_CALL_EVIDENCE = {
    274: (
        (17, "EAA2FE1327B8A1CCE10583581FCFB89DE2C19A3ED626E13F27CCDCF1944C2CD8", 3, "E28EC78ED94BF701004206E29A204D027550E9B56CAD507DCFA9C40934C8E5D0"),
        (17, "EAA2FE1327B8A1CCE10583581FCFB89DE2C19A3ED626E13F27CCDCF1944C2CD8", 3, "E28EC78ED94BF701004206E29A204D027550E9B56CAD507DCFA9C40934C8E5D0"),
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
    ),
    280: (
        (18, "6AA9CDA3EF84E1BC9312D6A182670070FD1CCCE5F3A6E193DA5B4F9B5FEDDD1B", 0, EMPTY_CANONICAL_SHA256),
        (18, "6AA9CDA3EF84E1BC9312D6A182670070FD1CCCE5F3A6E193DA5B4F9B5FEDDD1B", 0, EMPTY_CANONICAL_SHA256),
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
    ),
    286: (
        (69, "19EFADE24A2B8259D515CF796385363321381459ED1EB0315E7FF953F8CC6920", 0, EMPTY_CANONICAL_SHA256),
        (57, "6C0D3B09170292A99E0841A36486E71B0021D972BD81896621C654687C51F55F", 0, EMPTY_CANONICAL_SHA256),
        (12, "92C52BCBBF30CAFA1F75D15CF746DE06CE82F9939704111E89A620621BDF6113", 0, EMPTY_CANONICAL_SHA256),
    ),
    292: (
        (31, "483CBAF94A74C68D0A7F72236CB1A0ACC6534BD949BCEDECBDC84B37B4C2C661", 0, EMPTY_CANONICAL_SHA256),
        (26, "3A66844D35CDAB9300FAB6AA75EE1F2A78696E0E6BD0AD26512C5AC52B195AA7", 0, EMPTY_CANONICAL_SHA256),
        (5, "DF9752ABC5438B8E8DE16A13C6F83CAED7394A58FAC222B849AD8269B5B7279F", 0, EMPTY_CANONICAL_SHA256),
    ),
    298: (
        (11, "B7F0BBD1529D9D0887EAE3ED94551E21D2D15CCB2E786FFE0CC8BFD8D9264250", 4, "7B50D297C01FFC3EB20269EA629298999D0D5F699D200A10758332644D8A9783"),
        (11, "B7F0BBD1529D9D0887EAE3ED94551E21D2D15CCB2E786FFE0CC8BFD8D9264250", 4, "7B50D297C01FFC3EB20269EA629298999D0D5F699D200A10758332644D8A9783"),
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
    ),
    304: (
        (4, "2140E24BCC013F232CFC48AF34560F6A929A61B4A45F68DC54CC6BDF8EC2F2E3", 0, EMPTY_CANONICAL_SHA256),
        (4, "2140E24BCC013F232CFC48AF34560F6A929A61B4A45F68DC54CC6BDF8EC2F2E3", 0, EMPTY_CANONICAL_SHA256),
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
    ),
    310: (
        (14, "940538BCF06CB41831910805907589F53201A9AAB26DEDFC769459917CD5E3B7", 4, "A78A83CDA704007BFEADDABFF6559C59F241BBA4F83F41B4EE700D95F9928794"),
        (14, "940538BCF06CB41831910805907589F53201A9AAB26DEDFC769459917CD5E3B7", 4, "A78A83CDA704007BFEADDABFF6559C59F241BBA4F83F41B4EE700D95F9928794"),
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
    ),
    316: (
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
    ),
    322: (
        (94, "82745D3BED769A2A1602C13744138E4BD3EC481058EA0A727E980856FB506EAA", 3, "DA1F8A82FF7F09680055CFE452470D2FDBABFB15580549E2471E421542E5B954"),
        (85, "20DCC6CE93DC4969A07F76464BC27677F01F6747E8EA9701A6081DF1917A7AAC", 3, "DA1F8A82FF7F09680055CFE452470D2FDBABFB15580549E2471E421542E5B954"),
        (9, "249F2C7B463A8B60A2A21AC5027C310EC13126B51873B8E55AF428BBA139CBA2", 0, EMPTY_CANONICAL_SHA256),
    ),
    328: (
        (1, "4C9E88E30505822B4F8E5E370324A688BFC22F88E21F21F3DDFA0203B1D17A68", 0, EMPTY_CANONICAL_SHA256),
        (1, "4C9E88E30505822B4F8E5E370324A688BFC22F88E21F21F3DDFA0203B1D17A68", 0, EMPTY_CANONICAL_SHA256),
        (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
    ),
}
LEFT_BOUNDARY_IDS = tuple(range(1594, 1601))
LEFT_BOUNDARY_JP = (
    "けれど",
    "が",
    "けれども",
    "が",
    "けれども",
    "が",
    "が",
)
LEFT_BOUNDARY_CURRENT = (
    "하지만",
    "이",
    "하지만",
    "이",
    "하지만",
    "이",
    "이",
)
LEFT_BOUNDARY_POLICY = ("지만",) * 7
RIGHT_BOUNDARY_IDS = tuple(range(1657, 1664))
RIGHT_BOUNDARY_JP = (
    "くださった",
    "くれた",
    "くださいました",
    "くだされました",
    "くれました",
    "くださった",
    "くれた",
)
RIGHT_BOUNDARY_CURRENT = (
    "주셨다",
    "주었다",
    "주셨습니다",
    "주셨습니다",
    "주었습니다",
    "주셨다",
    "주었다",
)
RIGHT_BOUNDARY_POLICY = (
    "주셨다",
    "주었다",
    "주셨습니다",
    "주셨사옵니다",
    "주었습니다",
    "주셨다",
    "주었다",
)
BASIS = (
    "review_queue_pk_msggame_B002_zero_based_visible_ordinals134_199_"
    "pristine_pk_pc_jp_sole_translation_authority_block0_records1597_"
    "1662_66_visible_no_hidden_or_control_exclusions_independently_"
    "pinned_pk_source_and_policy_completed_Base_S1008_auxiliary_only_"
    "after_global_unique_contiguous_"
    "literal_gap_reverse_search_discovered_minus54_mapping_exact_pk_"
    "base_jp_current_sc_tc_and_empty_pk_en_archive_digests_full_014a_"
    "source_current_full_closure_0143_call_fixed_and_flatten_digests_"
    "root274_cross_S1028_all_jiman_policy_root328_cross_next_segment_"
    "benefactive_past_register_policy_contrastive_gratitude_conjectural_"
    "question_negative_listening_action_and_benefactive_matrices_all_"
    "runtime_pending_no_historic_or_switch_korean_authority_one_line_"
    "protected_skeleton_outside_reverse_exact_no_steam"
)


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return BASE.literal_texts(records, key)


def gap_bytes(record: Any) -> tuple[bytes, ...]:
    return BASE.gap_bytes(record)


def archive_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    return BASE.archive_records(prepared)


def record_signature(
    records: dict[tuple[int, int], Any],
    start: int,
    count: int,
) -> tuple[tuple[tuple[str, ...], tuple[str, ...]], ...]:
    return tuple(
        (
            literal_texts(records, (BLOCK_ID, record_id)),
            tuple(value.hex().upper() for value in gap_bytes(
                records[(BLOCK_ID, record_id)]
            )),
        )
        for record_id in range(start, start + count)
    )


def sequence_starts(
    records: dict[tuple[int, int], Any],
    sequence: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...],
) -> tuple[int, ...]:
    maximum = max(
        record_id
        for block_id, record_id in records
        if block_id == BLOCK_ID
    )
    count = len(sequence)
    return tuple(
        start
        for start in range(maximum - count + 2)
        if all(
            (BLOCK_ID, start + ordinal) in records
            for ordinal in range(count)
        )
        and record_signature(records, start, count) == sequence
    )


def assert_queue_contract(prepared: Any) -> None:
    batch_rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line
        and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        target["coordinate"]
        for row in batch_rows
        for target in row["target_literals"]
        if target["visible"]
    )
    hidden = tuple(
        target["coordinate"]
        for row in batch_rows
        for target in row["target_literals"]
        if not target["visible"]
    )
    if (
        len(batch_rows) != 200
        or len(visible) != 200
        or hidden
        or visible[134:200] != TARGET_COORDINATES
        or batch_rows[0]["record_coordinate"] != "0:1463"
        or batch_rows[-1]["record_coordinate"] != "0:1662"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} private queue ordinal contract drifted"
        )


def discover_mapping(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[dict[int, int], int]:
    expected_sequence = tuple(
        (
            (EXPECTED_PK_JP[ordinal],),
            ("", "050505"),
        )
        for ordinal in range(len(RECORD_IDS))
    )
    expected_digest = hashlib.sha256(
        json.dumps(
            expected_sequence,
            ensure_ascii=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest().upper()
    if expected_digest != EXPECTED_SEQUENCE_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} expected source sequence drifted"
        )
    base_hits = sequence_starts(
        records_by_label["base_jp"],
        expected_sequence,
    )
    pk_hits = sequence_starts(
        records_by_label["pk_jp"],
        expected_sequence,
    )
    if base_hits != (1543,) or pk_hits != (1597,):
        raise RuntimeError(
            f"segment {SEGMENT} global source reverse search drifted"
        )
    offset = pk_hits[0] - base_hits[0]
    mapping = {
        pk_record_id: pk_record_id - offset
        for pk_record_id in RECORD_IDS
    }
    if offset != 54 or tuple(mapping.values()) != BASE_RECORD_IDS:
        raise RuntimeError(
            f"segment {SEGMENT} discovered record mapping drifted"
        )
    return mapping, offset


def assert_source_and_runtime(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    mapping: dict[int, int],
) -> None:
    for label, expected_digest in PK_ARCHIVE_DIGESTS.items():
        actual_digest = GENERAL.subset_digest(
            records_by_label[label],
            RECORD_KEYS,
        )
        if actual_digest != expected_digest:
            raise RuntimeError(
                f"segment {SEGMENT} independent {label} digest drifted"
            )

    for ordinal, (pk_record_id, base_record_id) in enumerate(
        mapping.items()
    ):
        pk_key = (BLOCK_ID, pk_record_id)
        base_key = (BLOCK_ID, base_record_id)
        for label in PK_ARCHIVE_DIGESTS:
            if (
                len(literal_texts(records_by_label[label], pk_key)) != 1
                or gap_bytes(records_by_label[label][pk_key])
                != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} independent PK skeleton "
                    f"drifted: {label}/{pk_key}"
                )
        if literal_texts(records_by_label["pk_jp"], pk_key) != (
            EXPECTED_PK_JP[ordinal],
        ):
            raise RuntimeError(
                f"segment {SEGMENT} independent pristine PK source "
                f"drifted: {pk_key}"
            )
        for label in ("pk_sc", "pk_tc", "pk_en"):
            if literal_texts(records_by_label[label], pk_key) != ("",):
                raise RuntimeError(
                    f"segment {SEGMENT} independent blank context "
                    f"drifted: {label}/{pk_key}"
                )
        for language in ("jp", "current", "sc", "tc"):
            if (
                records_by_label[f"pk_{language}"][pk_key].data
                != records_by_label[f"base_{language}"][base_key].data
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} exact {language} mapping drifted: "
                    f"{base_key}/{pk_key}"
                )

    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    target_ids = set(RECORD_IDS)
    full_group_ids = target_ids | {1594, 1595, 1596, 1663}
    for label, records in (("source", source), ("current", current)):
        target_edges = [
            [block_id, record_id, operand]
            for (block_id, record_id), record in sorted(records.items())
            for operand in BASE.PREVIOUS.operands(
                record.data,
                BASE.PREVIOUS.MORPHOLOGY_JUMP_RE,
            )
            if operand in target_ids
        ]
        full_group_edges = [
            [block_id, record_id, operand]
            for (block_id, record_id), record in sorted(records.items())
            for operand in BASE.PREVIOUS.operands(
                record.data,
                BASE.PREVIOUS.MORPHOLOGY_JUMP_RE,
            )
            if operand in full_group_ids
        ]
        target_digest = hashlib.sha256(
            json.dumps(target_edges, separators=(",", ":")).encode("ascii")
        ).hexdigest().upper()
        full_group_digest = hashlib.sha256(
            json.dumps(
                full_group_edges,
                separators=(",", ":"),
            ).encode("ascii")
        ).hexdigest().upper()
        if (
            len(target_edges) != 66
            or {row[2] for row in target_edges} != target_ids
            or target_digest != PK_TARGET_JUMP_EDGE_SHA256
            or len(full_group_edges) != 70
            or {row[2] for row in full_group_edges} != full_group_ids
            or full_group_digest != PK_FULL_GROUP_JUMP_EDGE_SHA256
        ):
            raise RuntimeError(
                f"segment {SEGMENT} independent PK {label} "
                "incoming jump graph drifted"
            )

        graph = HELPERS.graph_edges(records)
        for root, expected_closure in EXPECTED_ROOT_CLOSURES.items():
            actual_closure = tuple(
                sorted(HELPERS.graph_closure(graph, root))
            )
            if actual_closure != expected_closure:
                raise RuntimeError(
                    f"segment {SEGMENT} independent PK {label} "
                    f"closure drifted: {root}"
                )

    for root, expected_evidence in EXPECTED_CALL_EVIDENCE.items():
        source_calls = HELPERS.root_call_sites(source, root)
        current_calls = HELPERS.root_call_sites(current, root)
        source_fixed = HELPERS.fixed_following_blockers(source, root)
        current_fixed = HELPERS.fixed_following_blockers(current, root)
        source_only = tuple(sorted(set(source_calls) - set(current_calls)))
        current_only = tuple(sorted(set(current_calls) - set(source_calls)))
        actual_evidence = (
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
        if actual_evidence != expected_evidence:
            raise RuntimeError(
                f"segment {SEGMENT} independent PK call/fixed/flatten "
                f"evidence drifted: {root}"
            )

    # Completed Base evidence remains an auxiliary cross-check only after
    # all independently pinned pristine PK guards have passed.
    BASE.assert_corpora(records_by_label)
    BASE.assert_runtime_graph(records_by_label)


def assert_boundaries(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    if tuple(
        literal_texts(source, (BLOCK_ID, record_id))[0]
        for record_id in LEFT_BOUNDARY_IDS
    ) != LEFT_BOUNDARY_JP:
        raise RuntimeError(f"segment {SEGMENT} left source boundary drifted")
    if tuple(
        literal_texts(current, (BLOCK_ID, record_id))[0]
        for record_id in LEFT_BOUNDARY_IDS
    ) != LEFT_BOUNDARY_CURRENT:
        raise RuntimeError(f"segment {SEGMENT} left current boundary drifted")
    if LEFT_BOUNDARY_POLICY != ("지만",) * 7:
        raise RuntimeError(f"segment {SEGMENT} left policy boundary drifted")
    if tuple(
        literal_texts(source, (BLOCK_ID, record_id))[0]
        for record_id in RIGHT_BOUNDARY_IDS
    ) != RIGHT_BOUNDARY_JP:
        raise RuntimeError(f"segment {SEGMENT} right source boundary drifted")
    if tuple(
        literal_texts(current, (BLOCK_ID, record_id))[0]
        for record_id in RIGHT_BOUNDARY_IDS
    ) != RIGHT_BOUNDARY_CURRENT:
        raise RuntimeError(
            f"segment {SEGMENT} right current boundary drifted"
        )
    if RIGHT_BOUNDARY_POLICY != (
        "주셨다",
        "주었다",
        "주셨습니다",
        "주셨사옵니다",
        "주었습니다",
        "주셨다",
        "주었다",
    ):
        raise RuntimeError(f"segment {SEGMENT} right policy boundary drifted")
    if (
        tuple(
            TRANSLATIONS_BY_RECORD[record_id]
            for record_id in range(1597, 1601)
        )
        != LEFT_BOUNDARY_POLICY[3:]
        or tuple(
            TRANSLATIONS_BY_RECORD[record_id]
            for record_id in range(1657, 1663)
        )
        != RIGHT_BOUNDARY_POLICY[:6]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} owned boundary policy drifted"
        )
    auxiliary_left_policy = tuple(
        BASE.PRIOR_SEGMENT.TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(1540, 1543)
    ) + tuple(
        BASE.TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(1543, 1547)
    )
    auxiliary_right_policy = tuple(
        BASE.TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(1603, 1609)
    ) + (RIGHT_BASE.TRANSLATIONS_BY_RECORD[1609],)
    if (
        auxiliary_left_policy != LEFT_BOUNDARY_POLICY
        or auxiliary_right_policy != RIGHT_BOUNDARY_POLICY
    ):
        raise RuntimeError(
            f"segment {SEGMENT} auxiliary Base boundary policy drifted"
        )


def load_base_semantic_policy(prepared: Any) -> dict[str, str]:
    if (
        not BASE_DECISION.is_file()
        or hashlib.sha256(BASE_DECISION.read_bytes()).hexdigest().upper()
        != BASE_DECISION_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} completed Base decision guard drifted"
        )
    validated = ENGINE.validate_decisions(
        prepared,
        BASE_DECISION,
        require_complete=False,
    )
    policy = {
        f"{block_id}:{record_id}:{literal_id}": translation
        for (
            resource,
            block_id,
            record_id,
            literal_id,
        ), translation in validated.items()
        if resource == "base_msggame"
    }
    if policy != BASE.RAW_TRANSLATIONS:
        raise RuntimeError(
            f"segment {SEGMENT} completed Base semantic policy drifted"
        )
    return policy


def build_translations(
    mapping: dict[int, int],
    base_policy: dict[str, str],
) -> dict[str, str]:
    auxiliary_base_translations = {
        f"{BLOCK_ID}:{pk_record_id}:0":
        base_policy[f"{BLOCK_ID}:{base_record_id}:0"]
        for pk_record_id, base_record_id in mapping.items()
    }
    translations = dict(TRANSLATIONS)
    if auxiliary_base_translations != translations:
        raise RuntimeError(
            f"segment {SEGMENT} auxiliary Base semantic policy drifted"
        )
    BASE.assert_semantics(
        {
            f"{BLOCK_ID}:{record_id}:0":
            translations[f"{BLOCK_ID}:{record_id + 54}:0"]
            for record_id in BASE_RECORD_IDS
        }
    )
    return translations


def assert_translation_semantics(translations: dict[str, str]) -> None:
    policy_rows = [
        [
            record_id,
            EXPECTED_PK_JP[ordinal],
            TRANSLATION_POLICY[ordinal],
            ROOT_BY_PK_RECORD[record_id],
        ]
        for ordinal, record_id in enumerate(RECORD_IDS)
    ]
    if (
        len(EXPECTED_PK_JP) != 66
        or len(TRANSLATION_POLICY) != 66
        or translations != TRANSLATIONS
        or HELPERS.canonical_sha256(policy_rows)
        != EXPECTED_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} independent semantic policy drifted"
        )
    if tuple(
        TRANSLATIONS_BY_RECORD[record_id]
        for record_id in range(1601, 1608)
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
    if (
        TRANSLATIONS_BY_RECORD[1620] != "일까 하오"
        or TRANSLATIONS_BY_RECORD[1629] != "들으세요"
        or TRANSLATIONS_BY_RECORD[1638] != "하옵니다"
        or TRANSLATIONS_BY_RECORD[1645] != "하옵니다"
        or TRANSLATIONS_BY_RECORD[1660] != "주셨사옵니다"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} speech-level or historic register drifted"
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
        or set(replacements) != {
            (BLOCK_ID, record_id, 0) for record_id in RECORD_IDS
        }
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
    int,
]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_queue_contract(prepared)
    records_by_label = archive_records(prepared)
    mapping, offset = discover_mapping(records_by_label)
    assert_source_and_runtime(records_by_label, mapping)
    assert_boundaries(records_by_label)
    base_policy = load_base_semantic_policy(prepared)
    translations = build_translations(mapping, base_policy)
    assert_translation_semantics(translations)
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
            or "\r" in translation
            or "\n" in translation
            or translation != translation.strip()
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation)
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
        root = ROOT_BY_PK_RECORD[record_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
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
                "automatic_space_inserted": False,
                "leading_trailing_space_protected": True,
                "pk_record_id": record_id,
                "base_semantic_record_id": base_record_id,
                "base_mapping_method": (
                    "global_unique_contiguous_literal_gap_reverse_search"
                ),
                "discovered_record_offset": offset,
                "root": root,
                "pk_source_call_count": (
                    EXPECTED_CALL_EVIDENCE[root][0][0]
                ),
                "pk_current_call_count": (
                    EXPECTED_CALL_EVIDENCE[root][1][0]
                ),
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
                "full_graph_closure_record_ids": list(
                    EXPECTED_ROOT_CLOSURES[root]
                ),
                "incoming_jump_graph_guarded": True,
                "runtime_integration_required": True,
            },
        }
        examples = BASE.CURRENT_CALLER_REWRITE_EXAMPLES.get(root)
        if examples:
            row["runtime_fragment_note"] = (
                "caller-specific rewrite examples: "
                + "; ".join(
                    f"{coordinate_value}={note}"
                    for coordinate_value, note in sorted(examples.items())
                )
            )
        rows.append(row)
    return (
        prepared,
        translations,
        rows,
        candidate,
        candidate_sha256,
        offset,
    )


def main() -> int:
    (
        prepared,
        translations,
        rows,
        candidate,
        candidate_sha256,
        offset,
    ) = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if (
        len(rows) != 66
        or len(translations) != 66
        or len(validated) != 66
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
            f"segment {SEGMENT} changed literal count drifted"
        )

    second = build_rows()
    if (
        second[1] != translations
        or second[2] != rows
        or second[3] != candidate
        or second[4] != candidate_sha256
        or second[5] != offset
    ):
        raise RuntimeError(
            f"segment {SEGMENT} second-run reproduction drifted"
        )
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B002_S1029",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [134, 199],
                "first_coordinate": TARGET_COORDINATES[0],
                "last_coordinate": TARGET_COORDINATES[-1],
                "source_literal_count": 66,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "confirmed_non_display": 0,
                "changed_literal_count": changed,
                "base_mapping_method": (
                    "global_unique_contiguous_literal_gap_reverse_search"
                ),
                "discovered_base_record_range": [
                    BASE_RECORD_IDS[0],
                    BASE_RECORD_IDS[-1],
                ],
                "discovered_pk_minus_base_offset": offset,
                "source_sequence_sha256": EXPECTED_SEQUENCE_SHA256,
                "translation_policy_sha256": EXPECTED_POLICY_SHA256,
                "pk_call_fixed_flatten_evidence": EXPECTED_CALL_EVIDENCE,
                "pk_source_only_flattened_calls": {
                    str(root): evidence[2][0]
                    for root, evidence in EXPECTED_CALL_EVIDENCE.items()
                    if evidence[2][0]
                },
                "left_boundary_policy": list(LEFT_BOUNDARY_POLICY),
                "right_boundary_policy": list(RIGHT_BOUNDARY_POLICY),
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
