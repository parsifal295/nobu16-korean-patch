#!/usr/bin/env python3
"""Build Base authoring segment 860 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment853 as PRIOR


ENGINE = PRIOR.ENGINE
CORE = PRIOR.COMMON.COMMON.CORE
UTIL = CORE.COMMON
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S860.private.v1.jsonl"
SEGMENT = 860
REPEATED_REFUSAL_TRANSLATION = (
    "송구하옵니다\n",
    "님께서는 완강히 우리 가문의 군문에\n항복하기를 거부하셨습니다",
)
RAW_TRANSLATIONS: dict[str, str] = {
    f"15:{record_id}:{literal_id}": translation
    for record_id in range(1020, 1032)
    for literal_id, translation in enumerate(REPEATED_REFUSAL_TRANSLATION)
}
RECORD_ARITIES = {record_id: 2 for record_id in range(1020, 1032)}
REPEATED_REFUSAL_JP = (
    "申し訳ありませぬ\n",
    "殿は頑なに当家の軍門に\n降るを拒みました",
)
EXPECTED_JP = {
    record_id: REPEATED_REFUSAL_JP for record_id in RECORD_ARITIES
}
EXPECTED_BASE_GAPS = {
    record_id: ("", "024833", "050505") for record_id in RECORD_ARITIES
}
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
PK_RECORD_MAP = {record_id: record_id + 7 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
AUXILIARY_OVERRIDES: dict[
    tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
] = {}
BASIS = (
    "pristine_base_pc_jp_authoritative_repeated_incorporation_refusal_report_"
    "with_explicit_base_to_pk_record_map_pc_sc_tc_and_pk_en_auxiliary_context_"
    "dynamic_officer_token_historical_subordinate_register_current_layout_"
    "opcode_skeleton_exact_repeated_source_translation_arrays_and_isolated_"
    "reverse_overlay_verified_runtime_assembly_pending"
)


def expected_auxiliary(
    *,
    side: str,
    language: str,
    record_id: int,
    overrides: dict[
        tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
    ],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    return overrides.get((side, language, record_id), CORE.DEFAULT_AUXILIARY)


def assert_context_mapping(
    *,
    segment: int,
    record_arities: dict[int, int],
    expected_jp: dict[int, tuple[str, ...]],
    base_gaps: dict[int, tuple[str, ...]],
    pk_jp_gaps: dict[int, tuple[str, ...]],
    pk_record_map: dict[int, int],
    auxiliary_overrides: dict[
        tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
    ],
    source_records: dict[tuple[int, int], Any],
    pk_source_records: dict[tuple[int, int], Any],
    base_context: dict[str, dict[tuple[int, int], Any]],
    pk_context: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if set(pk_record_map) != set(record_arities):
        raise RuntimeError(f"segment {segment} PK mapping coordinate universe drifted")
    if len(set(pk_record_map.values())) != len(pk_record_map):
        raise RuntimeError(f"segment {segment} PK mapping is not one-to-one")

    for record_id in record_arities:
        mapped_id = pk_record_map[record_id]
        expected_offset = 7 if record_id <= 1045 else 8
        if mapped_id != record_id + expected_offset:
            raise RuntimeError(
                f"segment {segment} PK insertion correction drifted: {record_id}"
            )
        base_record = source_records[(15, record_id)]
        pk_record = pk_source_records[(15, mapped_id)]
        base_literals = tuple(
            literal.text for literal in ENGINE.parse_record_literals(base_record)
        )
        pk_literals = tuple(
            literal.text for literal in ENGINE.parse_record_literals(pk_record)
        )
        if base_literals != expected_jp[record_id]:
            raise RuntimeError(
                f"segment {segment} Base JP literal array drifted: {record_id}"
            )
        if pk_literals != expected_jp[record_id]:
            raise RuntimeError(
                f"segment {segment} mapped PK JP literal array drifted: {mapped_id}"
            )
        if UTIL.record_gaps(base_record) != UTIL.gaps_from_hex(base_gaps[record_id]):
            raise RuntimeError(
                f"segment {segment} Base JP token skeleton drifted: {record_id}"
            )
        if UTIL.record_gaps(pk_record) != UTIL.gaps_from_hex(
            pk_jp_gaps[record_id]
        ):
            raise RuntimeError(
                f"segment {segment} PK JP token skeleton drifted: {mapped_id}"
            )

        for side, languages, context_id in (
            ("base", ("SC", "TC"), record_id),
            ("pk", ("SC", "TC", "EN"), mapped_id),
        ):
            records_by_language = base_context if side == "base" else pk_context
            for language in languages:
                expected_literals, expected_gaps = expected_auxiliary(
                    side=side,
                    language=language,
                    record_id=record_id,
                    overrides=auxiliary_overrides,
                )
                record = records_by_language[language][(15, context_id)]
                actual_literals = tuple(
                    literal.text for literal in ENGINE.parse_record_literals(record)
                )
                if actual_literals != expected_literals:
                    raise RuntimeError(
                        f"segment {segment} {side} {language} literal array drifted: "
                        f"{context_id}"
                    )
                if UTIL.record_gaps(record) != UTIL.gaps_from_hex(expected_gaps):
                    raise RuntimeError(
                        f"segment {segment} {side} {language} token skeleton drifted: "
                        f"{context_id}"
                    )


def assert_scope(
    prepared: Any,
    *,
    segment: int,
    raw_translations: dict[str, str],
    translations: dict[str, str],
    record_arities: dict[int, int],
    expected_jp: dict[int, tuple[str, ...]],
    base_gaps: dict[int, tuple[str, ...]],
    pk_jp_gaps: dict[int, tuple[str, ...]],
    pk_record_map: dict[int, int],
    ellipsis_coordinates: set[str],
    auxiliary_overrides: dict[
        tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
    ],
    semantic_assertions: Callable[
        [dict[tuple[int, int], Any], dict[str, str], dict[str, str]], None
    ],
) -> None:
    base = prepared.resources["base_msggame"]
    pk = prepared.resources["pk_msggame"]
    source_records = ENGINE.archive_records(base.pristine_archive)
    current_records = ENGINE.archive_records(base.current_archive)
    pk_source_records = ENGINE.archive_records(pk.pristine_archive)
    base_context = {
        language: ENGINE.archive_records(archive)
        for language, archive in base.context_archives.items()
    }
    pk_context = {
        language: ENGINE.archive_records(archive)
        for language, archive in pk.context_archives.items()
    }
    assert_context_mapping(
        segment=segment,
        record_arities=record_arities,
        expected_jp=expected_jp,
        base_gaps=base_gaps,
        pk_jp_gaps=pk_jp_gaps,
        pk_record_map=pk_record_map,
        auxiliary_overrides=auxiliary_overrides,
        source_records=source_records,
        pk_source_records=pk_source_records,
        base_context=base_context,
        pk_context=pk_context,
    )

    expected_coordinates = set()
    actual_current_ellipsis = set()
    for record_id, arity in record_arities.items():
        source_record = source_records[(15, record_id)]
        current_record = current_records[(15, record_id)]
        source_literals = ENGINE.parse_record_literals(source_record)
        current_literals = ENGINE.parse_record_literals(current_record)
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(
                f"segment {segment} source/current arity drifted: 15:{record_id}"
            )
        expected_gaps = UTIL.gaps_from_hex(base_gaps[record_id])
        if (
            UTIL.record_gaps(source_record) != expected_gaps
            or UTIL.record_gaps(current_record) != expected_gaps
        ):
            raise RuntimeError(
                f"segment {segment} Base dynamic skeleton drifted: 15:{record_id}"
            )
        for literal_id, (source_literal, current_literal) in enumerate(
            zip(source_literals, current_literals)
        ):
            coordinate = f"15:{record_id}:{literal_id}"
            if not ENGINE.is_visible_translation_candidate(source_literal.text):
                raise RuntimeError(
                    f"segment {segment} unexpected blank source literal: {coordinate}"
                )
            if not ENGINE.is_visible_translation_candidate(current_literal.text):
                raise RuntimeError(
                    f"segment {segment} unexpected blank current literal: {coordinate}"
                )
            expected_coordinates.add(coordinate)
            if "…" in current_literal.text:
                actual_current_ellipsis.add(coordinate)

    if set(raw_translations) != expected_coordinates:
        raise RuntimeError(f"segment {segment} raw decision coordinate universe drifted")
    if set(translations) != expected_coordinates:
        raise RuntimeError(
            f"segment {segment} resolved decision coordinate universe drifted"
        )
    if len(translations) != sum(record_arities.values()):
        raise RuntimeError(f"segment {segment} visible decision count drifted")
    if actual_current_ellipsis != ellipsis_coordinates:
        raise RuntimeError(f"segment {segment} current ellipsis coordinates drifted")

    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        current_text = ENGINE.parse_record_literals(
            current_records[(block_id, record_id)]
        )[literal_id].text
        if UTIL.layout_signature(translation) != UTIL.layout_signature(current_text):
            raise RuntimeError(
                f"segment {segment} layout/outer signature drifted: {coordinate}"
            )
        if "\r" in translation or ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(
                f"segment {segment} forbidden script/control drifted: {coordinate}"
            )
        if UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(
                f"segment {segment} retains banned fullwidth punctuation: {coordinate}"
            )
        if "…" in translation.replace("……", ""):
            raise RuntimeError(
                f"segment {segment} retains an unpaired ellipsis: {coordinate}"
            )

    semantic_assertions(source_records, raw_translations, translations)


def build_segment_rows(
    *,
    output: Path,
    segment: int,
    raw_translations: dict[str, str],
    record_arities: dict[int, int],
    expected_jp: dict[int, tuple[str, ...]],
    base_gaps: dict[int, tuple[str, ...]],
    pk_jp_gaps: dict[int, tuple[str, ...]],
    pk_record_map: dict[int, int],
    ellipsis_coordinates: set[str],
    auxiliary_overrides: dict[
        tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
    ],
    basis: str,
    semantic_assertions: Callable[
        [dict[tuple[int, int], Any], dict[str, str], dict[str, str]], None
    ],
) -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    current_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    translations = UTIL.resolved_translations(current_records, raw_translations)
    assert_scope(
        prepared,
        segment=segment,
        raw_translations=raw_translations,
        translations=translations,
        record_arities=record_arities,
        expected_jp=expected_jp,
        base_gaps=base_gaps,
        pk_jp_gaps=pk_jp_gaps,
        pk_record_map=pk_record_map,
        ellipsis_coordinates=ellipsis_coordinates,
        auxiliary_overrides=auxiliary_overrides,
        semantic_assertions=semantic_assertions,
    )
    UTIL.assert_isolated_overlay_roundtrip(
        prepared,
        segment=segment,
        translations=translations,
        record_arities=record_arities,
    )
    rows = []
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
                "source_record_raw_sha256": target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256": target["current_ko_utf16le_sha256"],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending",
                "basis": basis,
                "historic_korean_used": False,
                "switch_korean_used": False,
            }
        )
    return prepared, translations, rows


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    canonical_source = CORE.source_literals(source_records, 1020)
    for record_id in range(1020, 1032):
        if CORE.source_literals(source_records, record_id) != canonical_source:
            raise RuntimeError(
                f"segment 860 repeated refusal source drifted: {record_id}"
            )
        for literal_id, expected in enumerate(REPEATED_REFUSAL_TRANSLATION):
            coordinate = f"15:{record_id}:{literal_id}"
            if raw_translations[coordinate] != expected:
                raise RuntimeError(
                    f"segment 860 repeated refusal raw translation drifted: {coordinate}"
                )
            if translations[coordinate] != expected:
                raise RuntimeError(
                    f"segment 860 repeated refusal resolved translation drifted: "
                    f"{coordinate}"
                )
    joined = "\n".join(translations.values())
    if "군문에\n항복하기를 거부하셨습니다" not in joined:
        raise RuntimeError("segment 860 軍門に降る terminology drifted")
    if any(term in joined for term in ("군문에 드는", "투항", "산하", "당가")):
        raise RuntimeError("segment 860 retained forbidden legacy terminology")
    if any(coordinate.startswith("15:1095:") for coordinate in translations):
        raise RuntimeError("segment 860 hidden 1095 entered visible decision scope")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        expected_jp=EXPECTED_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        pk_record_map=PK_RECORD_MAP,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        auxiliary_overrides=AUXILIARY_OVERRIDES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 860 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S860",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "record_count": 19152,
                "explicit_pk_record_mapping_verified": True,
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
