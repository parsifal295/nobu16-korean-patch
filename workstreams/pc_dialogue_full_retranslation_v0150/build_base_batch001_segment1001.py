#!/usr/bin/env python3
"""Build Base authoring segment 1001 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment1000 as PREVIOUS
import build_base_batch001_segment734 as CANONICAL_734
import build_base_batch001_segment735 as CANONICAL_735


ENGINE = PREVIOUS.ENGINE
GENERAL = PREVIOUS.PREVIOUS.PREVIOUS
SUPPORT = GENERAL.SUPPORT
UTIL = GENERAL.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S1001.private.v1.jsonl"
)
SEGMENT = 1001
RecordKey = tuple[int, int]

HONGO = PREVIOUS.TRANSLATIONS_BY_RECORD[(17, 12)][0]
TAKITA = PREVIOUS.PREVIOUS.TRANSLATIONS_BY_RECORD[(17, 5)][0]
OTOMO = PREVIOUS.TRANSLATIONS_BY_RECORD[(17, 8)][1]

TRANSLATIONS_BY_RECORD: dict[RecordKey, tuple[str, ...]] = {
    (17, 18): (
        CANONICAL_734.TRANSLATIONS["9:3787:0"],
    ),
    (17, 19): (
        CANONICAL_734.TRANSLATIONS["9:3788:0"],
        CANONICAL_734.TRANSLATIONS["9:3788:1"],
    ),
    (17, 20): (
        CANONICAL_735.TRANSLATIONS["9:3789:0"],
        CANONICAL_735.TRANSLATIONS["9:3789:1"],
        CANONICAL_735.TRANSLATIONS["9:3789:2"],
    ),
    (17, 21): (
        CANONICAL_735.TRANSLATIONS["9:3790:0"],
    ),
    (17, 22): (
        CANONICAL_735.TRANSLATIONS["9:3791:0"],
    ),
    (17, 23): (
        CANONICAL_735.TRANSLATIONS["9:3792:0"],
        CANONICAL_735.TRANSLATIONS["9:3792:1"],
        CANONICAL_735.TRANSLATIONS["9:3792:2"],
    ),
    (17, 24): (
        CANONICAL_735.TRANSLATIONS["9:3793:0"],
        CANONICAL_735.TRANSLATIONS["9:3793:1"],
        CANONICAL_735.TRANSLATIONS["9:3793:2"],
    ),
    (17, 25): (
        CANONICAL_735.TRANSLATIONS["9:3794:0"],
    ),
    (17, 26): (
        CANONICAL_735.TRANSLATIONS["9:3795:0"],
    ),
}
RAW_TRANSLATIONS = {
    f"{block_id}:{record_id}:{literal_id}": translation
    for (block_id, record_id), translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
}
RECORD_ARITIES = {
    key: len(translations)
    for key, translations in TRANSLATIONS_BY_RECORD.items()
}
PK_RECORD_MAP: dict[RecordKey, RecordKey | None] = {
    (17, 18): (17, 18),
    (17, 19): None,
    (17, 20): (17, 51),
    (17, 21): (17, 22),
    (17, 22): (17, 23),
    (17, 23): (17, 24),
    (17, 24): (17, 25),
    (17, 25): (17, 26),
    (17, 26): (17, 27),
}
PK_CONTEXTUAL_REWRITES: dict[RecordKey, tuple[RecordKey, ...]] = {
    (17, 19): ((17, 49), (17, 50)),
}
EXPECTED_BASE_JP = {
    (17, 18): ("逃がすな！追え！",),
    (17, 19): (
        "北郷",
        "殿はうまくやっているな…\n全隊、反転準備！",
    ),
    (17, 20): (
        "……！　これは伏兵策の陣形じゃ！\n前進！　",
        "田北",
        "らを救え！",
    ),
    (17, 21): ("進軍をやめい\n殿の合図があるまで待機せよ",),
    (17, 22): (
        "ここらで兵を伏せようぞ\nどれだけ釣れるか、楽しみだのう",
    ),
    (17, 23): (
        "掛かったな、全軍前進！\n",
        "大友",
        "軍を一網打尽にせよ！",
    ),
    (17, 24): (
        "突撃じゃ！\n奴らを",
        "高城川",
        "に叩き込めい！",
    ),
    (17, 25): ("やはり伏兵…\n救援は間に合わぬか…！",),
    (17, 26): ("伏兵がおったぞ！混乱している内に蹴散らすぞ！",),
}
EXPECTED_BASE_GAPS = {
    (17, 18): ("", "050505"),
    (17, 19): ("1B4331", "1B435A", "050505"),
    (17, 20): ("", "1B4333", "1B435A", "050505"),
    (17, 21): ("", "050505"),
    (17, 22): ("", "050505"),
    (17, 23): ("", "1B4333", "1B435A", "050505"),
    (17, 24): ("", "1B4333", "1B435A", "050505"),
    (17, 25): ("", "050505"),
    (17, 26): ("", "050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP = {
    key: EXPECTED_BASE_JP[key]
    for key, mapped in PK_RECORD_MAP.items()
    if mapped is not None
}
EXPECTED_PK_GAPS = {
    key: (
        ("", "1B4331", "1B435A", "050505")
        if key == (17, 20)
        else EXPECTED_BASE_GAPS[key]
    )
    for key, mapped in PK_RECORD_MAP.items()
    if mapped is not None
}
EXPECTED_PK_CONTEXT_JP = {
    (17, 49): (
        "伏兵がなったか！\n後は北郷殿が敵をおびき寄せられれば・・・",
    ),
    (17, 50): ("この身が果ててもこの策成功させて見せるぞ！",),
}
EXPECTED_PK_CONTEXT_CURRENT = {
    (17, 49): (
        "복병은 준비됐나!\n이제 호고 님이 적을 유인해 오기만 하면……",
    ),
    (17, 50): (
        "이 몸이 쓰러지더라도 반드시 이 계책을 성공시키겠다!",
    ),
}
ARCHIVE_DIGESTS = {
    "base_jp": "89BCF637BCFF49AD2B6D31EAA93A222E79059D2422662F4E6A08E40746C095E4",
    "base_current": "9492163166AE2F8187D3629A9C59B46BD451A16F1A13517AB673D5C0C47FDD3E",
    "base_sc": "BED58F327D721EA6ACFAA5DD6215C1EB59E1917BFE2A48324BB597D277417803",
    "base_tc": "BED58F327D721EA6ACFAA5DD6215C1EB59E1917BFE2A48324BB597D277417803",
    "pk_jp": "23BEFE89127D9590DAD5F8470695EB495E40C808BE3430BAD56203A2DC4D086B",
    "pk_current": "806C095CEB71C7564F841697B37E1BF916865C01F3154FBA1BEC34266ADC71EA",
    "pk_sc": "CFF7DAB6604E9296DDDEA942AF4903456D333706A89A9EBAFA50F8D3EC44CF33",
    "pk_tc": "CFF7DAB6604E9296DDDEA942AF4903456D333706A89A9EBAFA50F8D3EC44CF33",
    "pk_en": "CFF7DAB6604E9296DDDEA942AF4903456D333706A89A9EBAFA50F8D3EC44CF33",
}
PK_CONTEXT_DIGESTS = {
    "pk_jp": "2DD60F919B4CDA390BBA028604CC5B0B87B65FC43B5F86EAE877CFE2C960649D",
    "pk_current": "BD52087B7586A3D8FBA0743D56AD030CB4914DAEB1E1A6369B3526922CC79A01",
    "pk_sc": "9222838C1CFD62A9B2A84A69293C63555A0C162189C2B0EC35D4E0E2478C9F90",
    "pk_tc": "9222838C1CFD62A9B2A84A69293C63555A0C162189C2B0EC35D4E0E2478C9F90",
    "pk_en": "9222838C1CFD62A9B2A84A69293C63555A0C162189C2B0EC35D4E0E2478C9F90",
}
CURRENT_ELLIPSIS_COORDINATES = {
    "17:19:1",
    "17:20:0",
    "17:25:0",
}
STATIC_COORDINATES = set(RAW_TRANSLATIONS)
HISTORICAL_EVIDENCE_URLS = {
    "北郷_reading_and_history": (
        "https://www.city.miyakonojo.miyazaki.jp/site/"
        "jidaibunkazai/3791.html"
    ),
    "田北_clan_reading": (
        "https://museum.city.fukuoka.jp/archives/exhibition/"
        "2001/20011218_shinshuzo/"
    ),
    "高城川_history": (
        "https://www.qsr.mlit.go.jp/miyazaki/kasen/omaru/"
        "gaiyou/omaru_rekishi.html"
    ),
}
BASIS = (
    "review_queue_base_msggame_B120_A_pristine_local_pc_jp_authoritative_"
    "mimikawa_takajo_river_tsurinobuse_sequence_with_explicit_nonidentity_"
    "base_pk_block17_mapping_unmapped_base_17_19_contextually_rewritten_as_"
    "pk_17_49_17_50_and_base_17_20_mapped_to_pk_17_51_exact_base_pk_jp_"
    "sc_tc_and_empty_pk_en_subset_digests_explicit_colour_tag_gap_"
    "divergence_17_20_fixed_colour_tags_no_morphology_current_line_counts_"
    "protected_signatures_project_ellipsis_source_tuple_exact_canonical_"
    "reuse_from_base_9_3787_through_9_3795_and_hongo_takita_otomo_reuse_"
    "official_miyakonojo_fukuoka_museum_and_kyushu_mlit_evidence_static_"
    "retranslated_only_no_korean_build_authority"
)


def literal_texts(
    records: dict[RecordKey, Any],
    key: RecordKey,
) -> tuple[str, ...]:
    return GENERAL.literal_texts(records, key)


def gap_hexes(
    records: dict[RecordKey, Any],
    key: RecordKey,
) -> tuple[str, ...]:
    return GENERAL.gap_hexes(records, key)


def assert_empty_context(
    records: dict[RecordKey, Any],
    key: RecordKey,
    *,
    label: str,
) -> None:
    if literal_texts(records, key) != ("",):
        raise RuntimeError(f"segment {SEGMENT} {label} text drifted: {key}")
    if gap_hexes(records, key) != ("", "050505"):
        raise RuntimeError(
            f"segment {SEGMENT} {label} skeleton drifted: {key}"
        )


def assert_semantics(
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    canonical_by_record = {
        (17, 18): tuple(
            CANONICAL_734.TRANSLATIONS[f"9:3787:{literal_id}"]
            for literal_id in range(RECORD_ARITIES[(17, 18)])
        ),
        (17, 19): tuple(
            CANONICAL_734.TRANSLATIONS[f"9:3788:{literal_id}"]
            for literal_id in range(RECORD_ARITIES[(17, 19)])
        ),
        **{
            (17, record_id): tuple(
                CANONICAL_735.TRANSLATIONS[
                    f"9:{record_id + 3769}:{literal_id}"
                ]
                for literal_id in range(
                    RECORD_ARITIES[(17, record_id)]
                )
            )
            for record_id in range(20, 27)
        },
    }
    if TRANSLATIONS_BY_RECORD != canonical_by_record:
        raise RuntimeError("segment 1001 source-exact canonical reuse drifted")
    if TRANSLATIONS_BY_RECORD[(17, 19)][0] != HONGO:
        raise RuntimeError("segment 1001 Hongo exact spelling reuse drifted")
    if not TRANSLATIONS_BY_RECORD[(17, 20)][1].startswith(
        TAKITA + " "
    ):
        raise RuntimeError("segment 1001 Takita exact spelling reuse drifted")
    if TRANSLATIONS_BY_RECORD[(17, 23)][1] != OTOMO:
        raise RuntimeError("segment 1001 Otomo exact spelling reuse drifted")
    if HONGO != "혼고" or TAKITA != "다키타" or OTOMO != "오토모":
        raise RuntimeError("segment 1001 inherited name spelling drifted")
    if TRANSLATIONS_BY_RECORD[(17, 24)][1] != "다카조가와":
        raise RuntimeError("segment 1001 Takajo River spelling drifted")
    joined = "\n".join(translations.values())
    for required in (
        "추격하라",
        "전 부대, 반전 준비",
        "복병을 둔 진형",
        "다키타 일행",
        "매복시키자",
        "걸려들었군",
        "일망타진",
        "다카조가와",
        "원군",
        "쓸어버리자",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 1001 required terminology drifted: {required}"
            )
    for forbidden in (
        "호고",
        "다바루",
        "다카조강",
        "북향",
        "기타키타",
        "복병책",
        "낚일지",
        "쫓아라",
    ):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 1001 forbidden wording retained: {forbidden}"
            )
    if len(HISTORICAL_EVIDENCE_URLS) != 3:
        raise RuntimeError("segment 1001 evidence registry drifted")
    if len(raw_translations) != 16 or len(translations) != 16:
        raise RuntimeError("segment 1001 visible decision count drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
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
    base_keys = tuple(RECORD_ARITIES)
    mapped_base_keys = tuple(
        key for key, mapped in PK_RECORD_MAP.items() if mapped is not None
    )
    pk_keys = tuple(
        mapped
        for mapped in PK_RECORD_MAP.values()
        if mapped is not None
    )
    context_keys = tuple(
        key
        for keys in PK_CONTEXTUAL_REWRITES.values()
        for key in keys
    )
    expected_universe = set(RECORD_ARITIES)
    for label, values in (
        ("PK map", PK_RECORD_MAP),
        ("Base JP", EXPECTED_BASE_JP),
        ("Base gaps", EXPECTED_BASE_GAPS),
        ("current gaps", EXPECTED_CURRENT_GAPS),
    ):
        if set(values) != expected_universe:
            raise RuntimeError(f"segment {SEGMENT} {label} universe drifted")
    if set(EXPECTED_PK_JP) != set(mapped_base_keys):
        raise RuntimeError("segment 1001 PK JP universe drifted")
    if set(EXPECTED_PK_GAPS) != set(mapped_base_keys):
        raise RuntimeError("segment 1001 PK gap universe drifted")
    if set(PK_CONTEXTUAL_REWRITES) != {
        key for key, mapped in PK_RECORD_MAP.items() if mapped is None
    }:
        raise RuntimeError("segment 1001 contextual rewrite universe drifted")
    if set(ARCHIVE_DIGESTS) != set(archives):
        raise RuntimeError("segment 1001 archive digest universe drifted")
    if set(PK_CONTEXT_DIGESTS) != {
        label for label in archives if label.startswith("pk_")
    }:
        raise RuntimeError("segment 1001 context digest universe drifted")
    for label, records in records_by_label.items():
        keys = pk_keys if label.startswith("pk_") else base_keys
        actual = GENERAL.subset_digest(records, keys)
        if actual != ARCHIVE_DIGESTS[label]:
            raise RuntimeError(f"segment {SEGMENT} {label} corpus drifted")
        if label.startswith("pk_"):
            context_actual = GENERAL.subset_digest(records, context_keys)
            if context_actual != PK_CONTEXT_DIGESTS[label]:
                raise RuntimeError(
                    f"segment {SEGMENT} {label} context corpus drifted"
                )

    source_records = records_by_label["base_jp"]
    current_records = records_by_label["base_current"]
    pk_source_records = records_by_label["pk_jp"]
    expected_coordinates: set[str] = set()
    actual_ellipsis: set[str] = set()
    for key, arity in RECORD_ARITIES.items():
        if literal_texts(source_records, key) != EXPECTED_BASE_JP[key]:
            raise RuntimeError(
                f"segment {SEGMENT} Base JP literal drifted: {key}"
            )
        source_literals = ENGINE.parse_record_literals(source_records[key])
        current_literals = ENGINE.parse_record_literals(current_records[key])
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(
                f"segment {SEGMENT} source/current arity drifted: {key}"
            )
        if gap_hexes(source_records, key) != EXPECTED_BASE_GAPS[key]:
            raise RuntimeError(
                f"segment {SEGMENT} Base pristine skeleton drifted: {key}"
            )
        if gap_hexes(current_records, key) != EXPECTED_CURRENT_GAPS[key]:
            raise RuntimeError(
                f"segment {SEGMENT} Base current skeleton drifted: {key}"
            )
        for language in ("sc", "tc"):
            assert_empty_context(
                records_by_label[f"base_{language}"],
                key,
                label=f"Base {language.upper()}",
            )
        mapped = PK_RECORD_MAP[key]
        if mapped is not None:
            if literal_texts(pk_source_records, mapped) != EXPECTED_PK_JP[key]:
                raise RuntimeError(
                    f"segment {SEGMENT} PK JP literal drifted: {key}/{mapped}"
                )
            if gap_hexes(pk_source_records, mapped) != EXPECTED_PK_GAPS[key]:
                raise RuntimeError(
                    f"segment {SEGMENT} PK JP skeleton drifted: "
                    f"{key}/{mapped}"
                )
            if gap_hexes(
                records_by_label["pk_current"],
                mapped,
            ) != EXPECTED_PK_GAPS[key]:
                raise RuntimeError(
                    f"segment {SEGMENT} PK current skeleton drifted: "
                    f"{key}/{mapped}"
                )
            for language in ("sc", "tc", "en"):
                assert_empty_context(
                    records_by_label[f"pk_{language}"],
                    mapped,
                    label=f"PK {language.upper()}",
                )
        for literal_id, (source_literal, current_literal) in enumerate(
            zip(source_literals, current_literals)
        ):
            coordinate = f"{key[0]}:{key[1]}:{literal_id}"
            if not ENGINE.is_visible_translation_candidate(
                source_literal.text
            ) or not ENGINE.is_visible_translation_candidate(
                current_literal.text
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} unexpected blank target: {coordinate}"
                )
            expected_coordinates.add(coordinate)
            if "…" in current_literal.text:
                actual_ellipsis.add(coordinate)

    for key in context_keys:
        if literal_texts(
            records_by_label["pk_jp"],
            key,
        ) != EXPECTED_PK_CONTEXT_JP[key]:
            raise RuntimeError(
                f"segment {SEGMENT} PK contextual JP drifted: {key}"
            )
        if literal_texts(
            records_by_label["pk_current"],
            key,
        ) != EXPECTED_PK_CONTEXT_CURRENT[key]:
            raise RuntimeError(
                f"segment {SEGMENT} PK contextual current drifted: {key}"
            )
        for label in ("pk_jp", "pk_current"):
            if gap_hexes(records_by_label[label], key) != ("", "050505"):
                raise RuntimeError(
                    f"segment {SEGMENT} {label} context skeleton drifted: "
                    f"{key}"
                )
        for language in ("sc", "tc", "en"):
            assert_empty_context(
                records_by_label[f"pk_{language}"],
                key,
                label=f"PK contextual {language.upper()}",
            )

    literal_divergences = {
        key
        for key in mapped_base_keys
        if EXPECTED_BASE_JP[key] != EXPECTED_PK_JP[key]
    }
    gap_divergences = {
        key
        for key in mapped_base_keys
        if EXPECTED_BASE_GAPS[key] != EXPECTED_PK_GAPS[key]
    }
    if literal_divergences:
        raise RuntimeError("segment 1001 PK literal divergence drifted")
    if gap_divergences != {(17, 20)}:
        raise RuntimeError("segment 1001 PK gap divergence drifted")

    morphology_sources = (
        tuple(EXPECTED_BASE_GAPS.values())
        + tuple(EXPECTED_CURRENT_GAPS.values())
        + tuple(EXPECTED_PK_GAPS.values())
        + tuple(("",
                 "050505") for _key in context_keys)
    )
    observed_morphology = {
        operand
        for gaps in morphology_sources
        for gap in gaps
        for operand in SUPPORT.morphology_operands(gap)
    }
    if observed_morphology:
        raise RuntimeError("segment 1001 morphology operand drifted")

    if set(RAW_TRANSLATIONS) != expected_coordinates:
        raise RuntimeError("segment 1001 raw coordinate universe drifted")
    translations = dict(RAW_TRANSLATIONS)
    if set(translations) != expected_coordinates:
        raise RuntimeError("segment 1001 resolved coordinate universe drifted")
    if actual_ellipsis != CURRENT_ELLIPSIS_COORDINATES:
        raise RuntimeError("segment 1001 ellipsis universe drifted")
    if STATIC_COORDINATES != expected_coordinates:
        raise RuntimeError("segment 1001 static coordinate universe drifted")
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        current_text = ENGINE.parse_record_literals(
            current_records[(block_id, record_id)]
        )[literal_id].text
        if translation.count("\n") != current_text.count("\n"):
            raise RuntimeError(
                f"segment {SEGMENT} LF layout drifted: {coordinate}"
            )
        current_signature = ENGINE.protected_signature(current_text)
        translation_signature = ENGINE.protected_signature(translation)
        for field in (
            "non_layout_controls",
            "leading_whitespace",
            "trailing_whitespace",
        ):
            if translation_signature[field] != current_signature[field]:
                raise RuntimeError(
                    f"segment {SEGMENT} protected layout drifted: "
                    f"{coordinate}/{field}"
                )
        if (
            "\r" in translation
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation)
            or "…" in translation.replace("……", "")
        ):
            raise RuntimeError(
                f"segment {SEGMENT} text residue drifted: {coordinate}"
            )
        if coordinate in CURRENT_ELLIPSIS_COORDINATES and not (
            translation.count("…") >= 2
            and translation.count("…") % 2 == 0
        ):
            raise RuntimeError(
                f"segment {SEGMENT} ellipsis pair drifted: {coordinate}"
            )
    assert_semantics(RAW_TRANSLATIONS, translations)
    GENERAL.assert_general_overlay_roundtrip(
        prepared,
        segment=SEGMENT,
        translations=translations,
        record_arities=RECORD_ARITIES,
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
                "scope_classification": "retranslated",
                "layout_review": "unchanged_from_current",
                "runtime_review": "not_required",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
            }
        )
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(rows) != 16 or len(validated) != len(translations):
        raise RuntimeError("segment 1001 validated count drifted")
    if any(
        row["scope_classification"] != "retranslated"
        or row["runtime_review"] != "not_required"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 1001 classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S1001",
                "queue": "base_msggame-B120",
                "source_literal_count": 16,
                "decision_count": len(rows),
                "hidden_non_display_count": 0,
                "retranslated": len(rows),
                "runtime_fragment_pending": 0,
                "explicit_pk_mapping": {
                    f"{key[0]}:{key[1]}": (
                        None
                        if mapped is None
                        else f"{mapped[0]}:{mapped[1]}"
                    )
                    for key, mapped in PK_RECORD_MAP.items()
                },
                "pk_contextual_rewrites": {
                    f"{key[0]}:{key[1]}": [
                        f"{mapped[0]}:{mapped[1]}"
                        for mapped in mapped_keys
                    ]
                    for key, mapped_keys in PK_CONTEXTUAL_REWRITES.items()
                },
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": ["17:20"],
                "pristine_current_gap_divergence_records": [],
                "base_pk_sc_tc_literal_divergence_records": [],
                "base_pk_sc_tc_gap_divergence_records": [],
                "pk_en_visible_records": [],
                "morphology_operands": [],
                "ellipsis_coordinates": sorted(
                    CURRENT_ELLIPSIS_COORDINATES
                ),
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
