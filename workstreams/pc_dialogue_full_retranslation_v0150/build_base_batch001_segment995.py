#!/usr/bin/env python3
"""Build Base authoring segment 995 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path
from typing import Any, Callable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment986 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
SUPPORT = PREVIOUS.SUPPORT
UTIL = PREVIOUS.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S995.private.v1.jsonl"
)
SEGMENT = 995

AGRICULTURE_ADVICE = ("에서는\n농업 발전에 힘써야겠군",)
COMMERCE_ADVICE = ("의 상업을\n더욱 발전시켜야겠군",)
TRANSLATIONS_BY_RECORD: dict[tuple[int, int], tuple[str, ...]] = {
    (15, 2419): (
        "싸움은 병력의 많고 적음으로 판가름 나는 법…\n",
        "에 원군을 청하여\n",
        "도움",
    ),
    (15, 2420): (
        "요격할 병사를 모아야 합니다\n이럴 때는 맹우",
        "에게\n",
        "도움을 청하는 것이",
    ),
    (15, 2421): (
        "에 원군을 청해 보는 건 어떻겠습니까?\n",
        "의 부탁이라면\n매몰차게 거절하지는 못할 것",
    ),
    (16, 1): ("후후, 하찮은 꾀라며\n얕보아서는 안 되느니라",),
    (16, 2): ("취락을 장악하는 일도\n그리 녹록지는 않다",),
    (16, 3): ("노동력이 남는다면\n성하 시설을 손보아 볼까…",),
    (16, 4): ("싸움 없는 세상은\n정녕 찾아오는 것일까…",),
    (16, 5): AGRICULTURE_ADVICE,
    (16, 6): COMMERCE_ADVICE,
    (16, 7): (
        "야말로\n현재",
        "에 필요하군",
    ),
    (16, 8): AGRICULTURE_ADVICE,
    (16, 9): COMMERCE_ADVICE,
    (16, 10): ("의 증축으로\n성하를 더욱 강화하리라",),
    (16, 11): ("의 모든 힘을 모아\n대전에 대비하라!",),
    (16, 12): ("의 석고를\n조금이라도 높여",),
}
RAW_TRANSLATIONS = {
    f"{block_id}:{record_id}:{literal_id}": translation
    for (block_id, record_id), translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
}
RECORD_KEYS = (
    *((15, record_id) for record_id in range(2419, 2423)),
    *((16, record_id) for record_id in range(0, 13)),
)
PK_RECORD_MAP: dict[tuple[int, int], tuple[int, int] | None] = {
    **{
        (15, record_id): (15, record_id + 31)
        for record_id in range(2419, 2422)
    },
    (15, 2422): None,
    **{(16, record_id): (16, record_id) for record_id in range(0, 13)},
}
EXPECTED_SOURCE_ARITIES = {
    (15, 2419): 3,
    (15, 2420): 3,
    (15, 2421): 2,
    (15, 2422): 1,
    (16, 0): 1,
    (16, 1): 1,
    (16, 2): 1,
    (16, 3): 1,
    (16, 4): 2,
    (16, 5): 1,
    (16, 6): 1,
    (16, 7): 2,
    (16, 8): 1,
    (16, 9): 1,
    (16, 10): 1,
    (16, 11): 1,
    (16, 12): 1,
}
EXPECTED_CURRENT_ARITIES = {
    **EXPECTED_SOURCE_ARITIES,
    (16, 4): 1,
}
HIDDEN_NON_DISPLAY_COORDINATES = {"15:2422:0", "16:0:0"}
STATIC_COORDINATES = {f"16:{record_id}:0" for record_id in range(1, 5)}
ELLIPSIS_COORDINATES = {
    "15:2419:0",
    "16:3:0",
    "16:4:0",
}
EXPECTED_LITERAL_DIVERGENCES = {
    "JP": {(16, 3)},
    "SC": set(),
    "TC": set(),
}
EXPECTED_GAP_DIVERGENCES = {
    "JP": {
        (15, 2419),
        (15, 2420),
        (15, 2421),
        (16, 2),
        (16, 4),
        (16, 12),
    },
    "SC": set(),
    "TC": set(),
}
EXPECTED_PRISTINE_CURRENT_GAP_DIVERGENCES = {(16, 2), (16, 4)}
REINFORCEMENT_TARGET_TOKEN = "025132"
CASTLE_TOKEN = "02463F"
FACILITY_TOKEN = "023C"
TOKEN_CONTRACTS = (
    ((15, 2419), 1, 1, REINFORCEMENT_TARGET_TOKEN),
    ((15, 2420), 1, 1, REINFORCEMENT_TARGET_TOKEN),
    ((15, 2421), 0, 0, REINFORCEMENT_TARGET_TOKEN),
    ((16, 5), 0, 0, CASTLE_TOKEN),
    ((16, 6), 0, 0, CASTLE_TOKEN),
    ((16, 7), 0, 0, FACILITY_TOKEN),
    ((16, 7), 1, 1, CASTLE_TOKEN),
    ((16, 8), 0, 0, CASTLE_TOKEN),
    ((16, 9), 0, 0, CASTLE_TOKEN),
    ((16, 10), 0, 0, FACILITY_TOKEN),
    ((16, 11), 0, 0, CASTLE_TOKEN),
    ((16, 12), 0, 0, CASTLE_TOKEN),
)
EXPECTED_BASE_MORPHOLOGY = {
    7: ("저희", "우리"),
    598: ("이겠지요", "이리라", "이겠지"),
    688: ("어떻게", "어떠하오"),
    976: ("받겠습니다", "받자", "받읍시다", "받겠다"),
    1054: ("합시다", "듯"),
    1162: ("고", ""),
}
EXPECTED_PK_MORPHOLOGY = {
    7: ("우리",),
    610: EXPECTED_BASE_MORPHOLOGY[598],
    700: EXPECTED_BASE_MORPHOLOGY[688],
    988: EXPECTED_BASE_MORPHOLOGY[976],
    1066: EXPECTED_BASE_MORPHOLOGY[1054],
    1174: EXPECTED_BASE_MORPHOLOGY[1162],
}
UNRESOLVED_RUNTIME_BRANCHES = (
    "15:2419:1-2/root1162+976",
    "15:2420:1-2/root1162+688+598",
    "16:12:0/root1054",
)
ARCHIVE_DIGESTS = {
    "base_jp": "EF450477DBB076C7D0A1B8FD072B2EF00FF78D8A0D6FD013A4CE448504514C2B",
    "base_current": "8763DCB8A767ECB79B70009181667D778A4BFF24968E174484D4F151D0AD2FBA",
    "base_sc": "334E11B43B6261A52218404FCD6D027674CDBFA2E6BEF6B904A6B795975828BE",
    "base_tc": "703DFE9989D5CFD3022D8A5D60680AD907C889943EB2A1EB992CB2E67B073DF5",
    "pk_jp": "1574AF7674438BA7E27AA29BC7B29E467429932F8D780E1F649E65A75B5C756F",
    "pk_current": "D841B616FFD022124C39B4A02A51A82F459746BA9D7C0013B693F9CBAB11814E",
    "pk_sc": "10BEB6ED1C6162729F042549A359AA685D1324CCAEF22DFDFB3F1615873313E5",
    "pk_tc": "864DEABDB80276AE6836638B27A4BBE83C8095276925FE26B6463529308FDF23",
    "pk_en": "EC424D7F1DBCD59D42C577875A93BF05BC8E47ECEF32BD9364519D469354A38E",
}
BASIS = (
    "review_queue_base_msggame_B119_B_pristine_base_pc_jp_authoritative_"
    "reinforcement_requests_settlement_and_castle_development_agriculture_"
    "commerce_facility_expansion_and_kokudaka_advice_with_explicit_"
    "base15_2419_2421_to_pk_plus31_and_base16_same_coordinate_mapping_"
    "base15_2422_and_base16_0_empty_opcode_records_excluded_exact_pc_sc_tc_"
    "and_contextual_pk_en_労力_as_nodongnyeok_集落_as_chwirak_版図_as_pando_"
    "石高_as_seokgo_dynamic_tokens_morphology_terminals_current_line_counts_"
    "and_project_ellipsis_preserved_no_korean_build_authority"
)


def literal_texts(
    records: dict[tuple[int, int], Any],
    record_key: tuple[int, int],
) -> tuple[str, ...]:
    return tuple(
        literal.text
        for literal in ENGINE.parse_record_literals(records[record_key])
    )


def gap_bytes(
    records: dict[tuple[int, int], Any],
    record_key: tuple[int, int],
) -> tuple[bytes, ...]:
    return UTIL.record_gaps(records[record_key])


def subset_digest(
    records: dict[tuple[int, int], Any],
    record_keys: tuple[tuple[int, int], ...],
) -> str:
    digest = hashlib.sha256()
    for block_id, record_id in record_keys:
        record = records[(block_id, record_id)]
        digest.update(struct.pack("<III", block_id, record_id, len(record.data)))
        digest.update(record.data)
    return digest.hexdigest().upper()


def assert_overlay_roundtrip(
    prepared: Any,
    *,
    segment: int,
    translations: dict[str, str],
    target_records: set[tuple[int, int]],
) -> str:
    base = prepared.resources["base_msggame"]
    current_records = ENGINE.archive_records(base.current_archive)
    replacements: dict[tuple[int, int, int], str] = {}
    reverse: dict[tuple[int, int, int], str] = {}
    for coordinate, translation in translations.items():
        key = tuple(int(value) for value in coordinate.split(":"))
        replacements[key] = translation
        reverse[key] = ENGINE.parse_record_literals(
            current_records[key[:2]]
        )[key[2]].text
    rebuilt = ENGINE.rebuild_packed_with_literals(
        base.current_blob,
        replacements,
    )
    rebuilt_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(rebuilt).archive
    )
    if len(current_records) != 19152 or len(rebuilt_records) != 19152:
        raise RuntimeError(f"segment {segment} Base record count drifted")
    for key, current_record in current_records.items():
        if (
            key not in target_records
            and rebuilt_records[key].data != current_record.data
        ):
            raise RuntimeError(
                f"segment {segment} changed an out-of-scope record: {key}"
            )
    for key in target_records:
        if gap_bytes(rebuilt_records, key) != gap_bytes(current_records, key):
            raise RuntimeError(f"segment {segment} changed skeleton: {key}")
    for key, translation in replacements.items():
        actual = ENGINE.parse_record_literals(rebuilt_records[key[:2]])[
            key[2]
        ].text
        if actual != translation:
            raise RuntimeError(
                f"segment {segment} UTF-16 round-trip failed: {key}"
            )
    reversed_blob = ENGINE.rebuild_packed_with_literals(rebuilt, reverse)
    if reversed_blob != base.current_blob:
        raise RuntimeError(
            f"segment {segment} reverse overlay is not byte-exact"
        )
    return hashlib.sha256(rebuilt).hexdigest().upper()


def build_segment_rows(
    *,
    output: Path,
    segment: int,
    record_keys: tuple[tuple[int, int], ...],
    pk_record_map: dict[tuple[int, int], tuple[int, int] | None],
    raw_translations: dict[str, str],
    source_arities: dict[tuple[int, int], int],
    current_arities: dict[tuple[int, int], int],
    hidden_coordinates: set[str],
    static_coordinates: set[str],
    ellipsis_coordinates: set[str],
    literal_divergences: dict[str, set[tuple[int, int]]],
    gap_divergences: dict[str, set[tuple[int, int]]],
    pristine_current_gap_divergences: set[tuple[int, int]],
    archive_digests: dict[str, str],
    basis: str,
    semantic_assertions: Callable[[dict[str, str]], None],
) -> tuple[Any, dict[str, str], list[dict[str, object]], str]:
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
    if (
        tuple(source_arities) != record_keys
        or tuple(current_arities) != record_keys
        or set(pk_record_map) != set(record_keys)
        or set(archive_digests) != set(archives)
    ):
        raise RuntimeError(f"segment {segment} record universe drifted")
    pk_record_keys = tuple(
        mapped
        for key in record_keys
        if (mapped := pk_record_map[key]) is not None
    )
    for label, records in records_by_label.items():
        keys = pk_record_keys if label.startswith("pk_") else record_keys
        if subset_digest(records, keys) != archive_digests[label]:
            raise RuntimeError(f"segment {segment} {label} corpus drifted")

    base_jp = records_by_label["base_jp"]
    current = records_by_label["base_current"]
    for key in record_keys:
        if (
            len(literal_texts(base_jp, key)) != source_arities[key]
            or len(literal_texts(current, key)) != current_arities[key]
        ):
            raise RuntimeError(f"segment {segment} arity drifted: {key}")
    actual_current_gap_divergences = {
        key
        for key in record_keys
        if gap_bytes(base_jp, key) != gap_bytes(current, key)
    }
    if (
        actual_current_gap_divergences
        != pristine_current_gap_divergences
    ):
        raise RuntimeError(
            f"segment {segment} pristine/current gaps drifted"
        )

    for language in ("JP", "SC", "TC"):
        base_records = records_by_label[f"base_{language.lower()}"]
        pk_records = records_by_label[f"pk_{language.lower()}"]
        actual_literal_divergences = set()
        actual_gap_divergences = set()
        for key in record_keys:
            mapped = pk_record_map[key]
            if mapped is None:
                continue
            if literal_texts(base_records, key) != literal_texts(
                pk_records,
                mapped,
            ):
                actual_literal_divergences.add(key)
            if gap_bytes(base_records, key) != gap_bytes(pk_records, mapped):
                actual_gap_divergences.add(key)
        if actual_literal_divergences != literal_divergences[language]:
            raise RuntimeError(
                f"segment {segment} {language} literal mapping drifted"
            )
        if actual_gap_divergences != gap_divergences[language]:
            raise RuntimeError(
                f"segment {segment} {language} gap mapping drifted"
            )

    for key in record_keys:
        mapped = pk_record_map[key]
        if mapped is None or f"{key[0]}:{key[1]}:0" in hidden_coordinates:
            continue
        if not any(
            text.strip()
            for text in literal_texts(records_by_label["pk_en"], mapped)
        ):
            raise RuntimeError(
                f"segment {segment} PK EN context became empty: {key}"
            )

    translations = UTIL.resolved_translations(current, raw_translations)
    expected_coordinates = {
        f"{block_id}:{record_id}:{literal_id}"
        for block_id, record_id in record_keys
        for literal_id in range(current_arities[(block_id, record_id)])
    } - hidden_coordinates
    if set(translations) != expected_coordinates:
        raise RuntimeError(f"segment {segment} coordinate universe drifted")
    if not static_coordinates <= expected_coordinates:
        raise RuntimeError(f"segment {segment} static universe drifted")
    actual_ellipsis = {
        coordinate
        for coordinate in expected_coordinates
        if "…" in literal_texts(
            current,
            tuple(int(value) for value in coordinate.split(":")[:2]),
        )[int(coordinate.split(":")[2])]
    }
    if actual_ellipsis != ellipsis_coordinates:
        raise RuntimeError(f"segment {segment} ellipsis universe drifted")
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        current_text = literal_texts(current, (block_id, record_id))[
            literal_id
        ]
        if UTIL.layout_signature(translation) != UTIL.layout_signature(
            current_text
        ):
            raise RuntimeError(
                f"segment {segment} layout signature drifted: {coordinate}"
            )
        if (
            "\r" in translation
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation)
            or "…" in translation.replace("……", "")
        ):
            raise RuntimeError(
                f"segment {segment} text residue drifted: {coordinate}"
            )
    semantic_assertions(translations)
    candidate_sha256 = assert_overlay_roundtrip(
        prepared,
        segment=segment,
        translations=translations,
        target_records=set(record_keys),
    )

    rows: list[dict[str, object]] = []
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        key = (block_id, record_id)
        target = prepared.visible_targets[
            ("base_msggame", block_id, record_id, literal_id)
        ]
        is_static = coordinate in static_coordinates
        row: dict[str, object] = {
            "schema": ENGINE.DECISION_SCHEMA,
            "resource": "base_msggame",
            "coordinate": coordinate,
            "source_record_raw_sha256": target["source_record_raw_sha256"],
            "current_ko_utf16le_sha256": target[
                "current_ko_utf16le_sha256"
            ],
            "translation": translation,
            "semantic_review": "approved",
            "scope_classification": (
                "retranslated" if is_static else "runtime_fragment_pending"
            ),
            "layout_review": "unchanged_from_current",
            "runtime_review": "not_required" if is_static else "pending",
            "basis": basis,
            "historic_korean_used": False,
            "switch_korean_used": False,
        }
        base_operands = SUPPORT.morphology_operands(
            gap_bytes(current, key)[literal_id + 1].hex()
        )
        mapped = pk_record_map[key]
        pk_operands: tuple[int, ...] = ()
        if mapped is not None:
            mapped_gaps = gap_bytes(records_by_label["pk_current"], mapped)
            if literal_id + 1 < len(mapped_gaps):
                pk_operands = SUPPORT.morphology_operands(
                    mapped_gaps[literal_id + 1].hex()
                )
        if base_operands or pk_operands:
            row["runtime_morphology_samples"] = {
                "base": [
                    {
                        "opcode": (
                            b"\x01\x43" + struct.pack("<I", operand)
                        ).hex().upper(),
                        "terminal_literals": list(
                            SUPPORT.morphology_terminal_literals(
                                current,
                                operand,
                            )
                        ),
                    }
                    for operand in base_operands
                ],
                "pk": [
                    {
                        "mapped_coordinate": (
                            f"{mapped[0]}:{mapped[1]}"
                            if mapped is not None
                            else None
                        ),
                        "opcode": (
                            b"\x01\x43" + struct.pack("<I", operand)
                        ).hex().upper(),
                        "terminal_literals": list(
                            SUPPORT.morphology_terminal_literals(
                                records_by_label["pk_current"],
                                operand,
                            )
                        ),
                    }
                    for operand in pk_operands
                ],
            }
        rows.append(row)
    ENGINE.atomic_write(output, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        output,
        require_complete=False,
    )
    if len(validated) != len(rows):
        raise RuntimeError(f"segment {segment} validation count drifted")
    return prepared, translations, rows, candidate_sha256


def assert_semantics(translations: dict[str, str]) -> None:
    joined = "\n".join(translations.values())
    for required in (
        "원군",
        "취락",
        "노동력",
        "농업",
        "상업",
        "성하",
        "석고",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 995 required meaning drifted: {required}")
    for forbidden in (
        "얕은꾀",
        "여력",
        "당가",
        "을(를)",
        "아카조나에",
        "、",
        "。",
    ):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 995 forbidden wording retained: {forbidden}"
            )
    if TRANSLATIONS_BY_RECORD[(16, 5)] is not TRANSLATIONS_BY_RECORD[(16, 8)]:
        raise RuntimeError("segment 995 agriculture exact group drifted")
    if TRANSLATIONS_BY_RECORD[(16, 6)] is not TRANSLATIONS_BY_RECORD[(16, 9)]:
        raise RuntimeError("segment 995 commerce exact group drifted")
    if not translations["15:2421:1"].endswith("못할 것"):
        raise RuntimeError("segment 995 request morphology stem drifted")
    assembled = {
        f"{translations['15:2421:1']}{ending}".splitlines()[-1]
        for ending in ("이겠지요", "이리라", "이겠지")
    }
    if assembled != {
        "매몰차게 거절하지는 못할 것이겠지요",
        "매몰차게 거절하지는 못할 것이리라",
        "매몰차게 거절하지는 못할 것이겠지",
    }:
        raise RuntimeError("segment 995 request assembly drifted")


def assert_dynamic_runtime_contracts(
    prepared: Any,
    *,
    segment: int,
    record_keys: tuple[tuple[int, int], ...],
    pk_record_map: dict[tuple[int, int], tuple[int, int] | None],
    token_contracts: tuple[
        tuple[tuple[int, int], int, int, str],
        ...,
    ],
    expected_base_morphology: dict[int, tuple[str, ...]],
    expected_pk_morphology: dict[int, tuple[str, ...]],
    translations: dict[str, str],
    static_coordinates: set[str],
    rows: list[dict[str, object]],
) -> None:
    base_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    pk_records = ENGINE.archive_records(
        prepared.resources["pk_msggame"].current_archive
    )

    observed_base = {
        operand
        for key in record_keys
        for gap in gap_bytes(base_records, key)
        for operand in SUPPORT.morphology_operands(gap.hex())
    }
    observed_pk = {
        operand
        for key in record_keys
        if (mapped := pk_record_map[key]) is not None
        for gap in gap_bytes(pk_records, mapped)
        for operand in SUPPORT.morphology_operands(gap.hex())
    }
    if observed_base != set(expected_base_morphology):
        raise RuntimeError(
            f"segment {segment} Base morphology universe drifted"
        )
    if observed_pk != set(expected_pk_morphology):
        raise RuntimeError(
            f"segment {segment} PK morphology universe drifted"
        )
    for records, expected, side in (
        (base_records, expected_base_morphology, "Base"),
        (pk_records, expected_pk_morphology, "PK"),
    ):
        for operand, terminals in expected.items():
            actual = SUPPORT.morphology_terminal_literals(records, operand)
            if actual != terminals:
                raise RuntimeError(
                    f"segment {segment} {side} morphology terminal "
                    f"drifted: {operand}"
                )

    for key, base_gap_id, pk_gap_id, expected_hex in token_contracts:
        actual_base = (
            gap_bytes(base_records, key)[base_gap_id].hex().upper()
        )
        mapped = pk_record_map[key]
        if actual_base != expected_hex or mapped is None:
            raise RuntimeError(
                f"segment {segment} Base token direction drifted: "
                f"{key}/{base_gap_id}"
            )
        actual_pk = (
            gap_bytes(pk_records, mapped)[pk_gap_id].hex().upper()
        )
        if actual_pk != expected_hex:
            raise RuntimeError(
                f"segment {segment} PK token direction drifted: "
                f"{key}/{mapped}/{pk_gap_id}"
            )

    expected_pending = set(translations) - static_coordinates
    actual_pending = {
        str(row["coordinate"])
        for row in rows
        if row["scope_classification"] == "runtime_fragment_pending"
        and row["runtime_review"] == "pending"
    }
    if actual_pending != expected_pending:
        raise RuntimeError(
            f"segment {segment} runtime-pending universe drifted"
        )


def main() -> int:
    prepared, translations, rows, candidate_sha256 = build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        record_keys=RECORD_KEYS,
        pk_record_map=PK_RECORD_MAP,
        raw_translations=RAW_TRANSLATIONS,
        source_arities=EXPECTED_SOURCE_ARITIES,
        current_arities=EXPECTED_CURRENT_ARITIES,
        hidden_coordinates=HIDDEN_NON_DISPLAY_COORDINATES,
        static_coordinates=STATIC_COORDINATES,
        ellipsis_coordinates=ELLIPSIS_COORDINATES,
        literal_divergences=EXPECTED_LITERAL_DIVERGENCES,
        gap_divergences=EXPECTED_GAP_DIVERGENCES,
        pristine_current_gap_divergences=(
            EXPECTED_PRISTINE_CURRENT_GAP_DIVERGENCES
        ),
        archive_digests=ARCHIVE_DIGESTS,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )
    assert_dynamic_runtime_contracts(
        prepared,
        segment=SEGMENT,
        record_keys=RECORD_KEYS,
        pk_record_map=PK_RECORD_MAP,
        token_contracts=TOKEN_CONTRACTS,
        expected_base_morphology=EXPECTED_BASE_MORPHOLOGY,
        expected_pk_morphology=EXPECTED_PK_MORPHOLOGY,
        translations=translations,
        static_coordinates=STATIC_COORDINATES,
        rows=rows,
    )
    if len(rows) != 21 or len(translations) != 21:
        raise RuntimeError("segment 995 decision count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S995",
                "source_literal_count": 24,
                "current_literal_count": 23,
                "decision_count": len(rows),
                "hidden_non_display_count": 2,
                "retranslated": len(STATIC_COORDINATES),
                "runtime_fragment_pending": (
                    len(rows) - len(STATIC_COORDINATES)
                ),
                "explicit_pk_mapping": {
                    f"{key[0]}:{key[1]}": (
                        f"{mapped[0]}:{mapped[1]}"
                        if mapped is not None
                        else None
                    )
                    for key, mapped in PK_RECORD_MAP.items()
                },
                "base_pk_literal_divergences": {
                    language: [
                        f"{key[0]}:{key[1]}"
                        for key in sorted(divergences)
                    ]
                    for language, divergences in (
                        EXPECTED_LITERAL_DIVERGENCES.items()
                    )
                },
                "base_pk_gap_divergences": {
                    language: [
                        f"{key[0]}:{key[1]}"
                        for key in sorted(divergences)
                    ]
                    for language, divergences in (
                        EXPECTED_GAP_DIVERGENCES.items()
                    )
                },
                "pristine_current_gap_divergences": [
                    f"{key[0]}:{key[1]}"
                    for key in sorted(
                        EXPECTED_PRISTINE_CURRENT_GAP_DIVERGENCES
                    )
                ],
                "exact_translation_groups": [
                    ["16:5", "16:8"],
                    ["16:6", "16:9"],
                ],
                "runtime_unresolved_branches": list(
                    UNRESOLVED_RUNTIME_BRANCHES
                ),
                "ellipsis_coordinates": sorted(ELLIPSIS_COORDINATES),
                "lf_count": sum(
                    text.count("\n") for text in translations.values()
                ),
                "candidate_sha256": candidate_sha256,
                "record_count": 19152,
                "outside_scope_records_exact": True,
                "target_runtime_skeleton_exact": True,
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
