#!/usr/bin/env python3
"""Build Base authoring segment 884 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment883 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.FRAMEWORK
UTIL = COMMON.UTIL
CORE = COMMON.CORE
FRAMEWORK = sys.modules[__name__]
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S884.private.v1.jsonl"
)
SEGMENT = 884

REINFORCEMENT_FIELD_COMPLETIONS = {
    1318: (
        "에 병사를 보충하였소\n"
        "성으로 돌아갔다면 시간을 허비했을 터\n"
        "순조롭게 마쳐 다행이었소"
    ),
    1319: (
        "에 병력을 보충했습니다\n"
        "이제 적과 맞붙어도 안심이군요"
    ),
    1320: (
        "에 병력을 보충했다\n"
        "이 정도면 충분히 싸울 수 있겠군"
    ),
    1321: (
        "에 병력을 보충했습니다\n"
        "이제 교전해도 안심이군요"
    ),
    1322: (
        "에 병력을 보충했습니다\n"
        "병사들을 무사히 데려다주었습니다!"
    ),
}
S883_COMPLETION_SOURCE_IDS = {
    1323: 1311,
    1324: 1312,
    1325: 1313,
    1326: 1314,
    1327: 1315,
    1328: 1316,
    1329: 1317,
}
EXACT_FIELD_COMPLETION_PAIRS = {
    1318: 1330,
    1319: 1331,
    1320: 1332,
    1321: 1333,
    1322: 1334,
}
TROOP_CHANGE_SUMMARY = ("·", "의 병력이", "증가\n·", "의 병력이", "감소")
RAW_TRANSLATIONS: dict[str, str] = {
    **{
        f"15:{record_id}:0": translation
        for record_id, translation in REINFORCEMENT_FIELD_COMPLETIONS.items()
    },
    **{
        f"15:{record_id}:0": PREVIOUS.RAW_TRANSLATIONS[
            f"15:{source_id}:0"
        ]
        for record_id, source_id in S883_COMPLETION_SOURCE_IDS.items()
    },
    **{
        f"15:{duplicate_id}:0": REINFORCEMENT_FIELD_COMPLETIONS[source_id]
        for source_id, duplicate_id in EXACT_FIELD_COMPLETION_PAIRS.items()
    },
    **{
        f"15:1335:{literal_id}": translation
        for literal_id, translation in enumerate(TROOP_CHANGE_SUMMARY)
    },
}
RECORD_ARITIES = {
    **{record_id: 1 for record_id in range(1318, 1335)},
    1335: 5,
}
EXPECTED_BASE_JP = {
    1318: (
        "に兵を補充いたした\n"
        "城に戻っては時間を損じまするゆえ\n"
        "うまくゆきて良うござったわ",
    ),
    1319: (
        "へ兵の補充を行いました\n"
        "これで敵と当たっても安心ですね",
    ),
    1320: (
        "へ兵の補充を行った\n"
        "これだけおれば十分戦えよう",
    ),
    1321: (
        "へ兵の補充を行いました\n"
        "これで交戦しても安心ですね",
    ),
    1322: (
        "へ兵を補充しました\n"
        "無事、送り届けましたぞ！",
    ),
    1323: (
        "への補充を終えてきたぞ\n"
        "兵の数はこれで十分だな！",
    ),
    1324: (
        "へ兵の補充をいたしました\n"
        "彼らも些か少数であったゆえ、\n"
        "兵の数が増え、安心したでしょう",
    ),
    1325: (
        "に兵の補充をしてまいりましたぞ\n"
        "これにて兵力については心配いらぬでしょう",
    ),
    1326: (
        "への兵の補充は完了です\n"
        "無事追いつき、兵を合流させることで\n"
        "城に寄らせることなく補充を終えました",
    ),
    1327: (
        "の兵力は万全にござる\n"
        "無事追いつきて合流し\n"
        "進軍を止めることなく、兵を補充いたした",
    ),
    1328: (
        "に合流いたし\n"
        "兵の補充を終えて戻りました\n"
        "どうぞお心安く",
    ),
    1329: (
        "に部隊を合流させ\n"
        "進行を止めることなく兵を補充いたしました\n"
        "これで兵力の心配はご無用かと",
    ),
    1330: (
        "に兵を補充いたした\n"
        "城に戻っては時間を損じまするゆえ\n"
        "うまくゆきて良うござったわ",
    ),
    1331: (
        "へ兵の補充を行いました\n"
        "これで敵と当たっても安心ですね",
    ),
    1332: (
        "へ兵の補充を行った\n"
        "これだけおれば十分戦えよう",
    ),
    1333: (
        "へ兵の補充を行いました\n"
        "これで交戦しても安心ですね",
    ),
    1334: (
        "へ兵を補充しました\n"
        "無事、送り届けましたぞ！",
    ),
    1335: ("・", "の兵力が", "増加\n・", "の兵力が", "減少"),
}
EXPECTED_PK_JP = EXPECTED_BASE_JP
EXPECTED_BASE_GAPS = {
    **{
        record_id: ("026e32", "050505")
        for record_id in range(1318, 1335)
    },
    1335: ("", "026e32", "0232", "026432", "0232", "050505"),
}
EXPECTED_PK_JP_GAPS = EXPECTED_BASE_GAPS
PK_RECORD_MAP = {
    record_id: record_id + 8 for record_id in RECORD_ARITIES
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
AUXILIARY_OVERRIDES: dict[
    tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
] = {}
BASIS = (
    "review_queue_base_msggame_B107_pristine_base_pc_jp_authoritative_"
    "marching_unit_reinforcement_completion_reports_and_troop_change_ui_"
    "with_explicit_plus_8_pk_jp_sc_tc_mapping_blank_pk_en_auxiliary_"
    "context_b106_s883_completion_canonical_reuse_exact_source_pairs_"
    "field_reinforcement_without_castle_return_dynamic_unit_and_castle_"
    "tokens_speaker_register_current_layout_and_opcode_skeleton_preserved_"
    "runtime_fragment_pending"
)


def expected_auxiliary(
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
    pk_record_map: dict[int, int],
    expected_base_jp: dict[int, tuple[str, ...]],
    expected_pk_jp: dict[int, tuple[str, ...]],
    base_gaps: dict[int, tuple[str, ...]],
    pk_jp_gaps: dict[int, tuple[str, ...]],
    auxiliary_overrides: dict[
        tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
    ],
    source_records: dict[tuple[int, int], Any],
    pk_source_records: dict[tuple[int, int], Any],
    base_context: dict[str, dict[tuple[int, int], Any]],
    pk_context: dict[str, dict[tuple[int, int], Any]],
) -> None:
    record_ids = set(record_arities)
    if set(pk_record_map) != record_ids:
        raise RuntimeError(f"segment {segment} PK mapping key universe drifted")
    if len(set(pk_record_map.values())) != len(pk_record_map):
        raise RuntimeError(f"segment {segment} PK mapping is not one-to-one")
    for expected in (
        expected_base_jp,
        expected_pk_jp,
        base_gaps,
        pk_jp_gaps,
    ):
        if set(expected) != record_ids:
            raise RuntimeError(
                f"segment {segment} expected context key universe drifted"
            )
    if any(
        record_id not in record_ids
        for _, _, record_id in auxiliary_overrides
    ):
        raise RuntimeError(
            f"segment {segment} auxiliary override escaped Base record scope"
        )

    for record_id in record_arities:
        mapped_id = pk_record_map[record_id]
        base_record = source_records[(15, record_id)]
        pk_record = pk_source_records[(15, mapped_id)]
        base_literals = tuple(
            literal.text for literal in ENGINE.parse_record_literals(base_record)
        )
        pk_literals = tuple(
            literal.text for literal in ENGINE.parse_record_literals(pk_record)
        )
        if base_literals != expected_base_jp[record_id]:
            raise RuntimeError(
                f"segment {segment} Base JP literal array drifted: {record_id}"
            )
        if pk_literals != expected_pk_jp[record_id]:
            raise RuntimeError(
                f"segment {segment} mapped PK JP literal array drifted: "
                f"{record_id}->{mapped_id}"
            )
        if UTIL.record_gaps(base_record) != UTIL.gaps_from_hex(
            base_gaps[record_id]
        ):
            raise RuntimeError(
                f"segment {segment} Base JP token skeleton drifted: {record_id}"
            )
        if UTIL.record_gaps(pk_record) != UTIL.gaps_from_hex(
            pk_jp_gaps[record_id]
        ):
            raise RuntimeError(
                f"segment {segment} PK JP token skeleton drifted: "
                f"{record_id}->{mapped_id}"
            )

        for side, languages, context_id in (
            ("base", ("SC", "TC"), record_id),
            ("pk", ("SC", "TC", "EN"), mapped_id),
        ):
            records_by_language = base_context if side == "base" else pk_context
            for language in languages:
                expected_literals, expected_gaps = expected_auxiliary(
                    side,
                    language,
                    record_id,
                    auxiliary_overrides,
                )
                record = records_by_language[language][(15, context_id)]
                actual_literals = tuple(
                    literal.text
                    for literal in ENGINE.parse_record_literals(record)
                )
                if actual_literals != expected_literals:
                    raise RuntimeError(
                        f"segment {segment} {side} {language} literal array "
                        f"drifted: {context_id}"
                    )
                if UTIL.record_gaps(record) != UTIL.gaps_from_hex(expected_gaps):
                    raise RuntimeError(
                        f"segment {segment} {side} {language} token skeleton "
                        f"drifted: {context_id}"
                    )


def assert_scope(
    prepared: Any,
    *,
    segment: int,
    raw_translations: dict[str, str],
    translations: dict[str, str],
    record_arities: dict[int, int],
    pk_record_map: dict[int, int],
    expected_base_jp: dict[int, tuple[str, ...]],
    expected_pk_jp: dict[int, tuple[str, ...]],
    base_gaps: dict[int, tuple[str, ...]],
    pk_jp_gaps: dict[int, tuple[str, ...]],
    ellipsis_coordinates: set[str],
    auxiliary_overrides: dict[
        tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
    ],
    excluded_nonvisible_coordinates: dict[str, str],
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
        pk_record_map=pk_record_map,
        expected_base_jp=expected_base_jp,
        expected_pk_jp=expected_pk_jp,
        base_gaps=base_gaps,
        pk_jp_gaps=pk_jp_gaps,
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
                f"segment {segment} source/current arity drifted: "
                f"15:{record_id}"
            )
        expected_gaps = UTIL.gaps_from_hex(base_gaps[record_id])
        if (
            UTIL.record_gaps(source_record) != expected_gaps
            or UTIL.record_gaps(current_record) != expected_gaps
        ):
            raise RuntimeError(
                f"segment {segment} Base dynamic skeleton drifted: "
                f"15:{record_id}"
            )
        for literal_id, (source_literal, current_literal) in enumerate(
            zip(source_literals, current_literals)
        ):
            coordinate = f"15:{record_id}:{literal_id}"
            if coordinate in excluded_nonvisible_coordinates:
                expected_text = excluded_nonvisible_coordinates[coordinate]
                if (
                    source_literal.text != expected_text
                    or current_literal.text != expected_text
                    or ENGINE.is_visible_translation_candidate(source_literal.text)
                    or ENGINE.is_visible_translation_candidate(current_literal.text)
                    or coordinate in raw_translations
                    or coordinate in translations
                ):
                    raise RuntimeError(
                        f"segment {segment} excluded nonvisible literal drifted: "
                        f"{coordinate}"
                    )
                continue
            if not ENGINE.is_visible_translation_candidate(source_literal.text):
                raise RuntimeError(
                    f"segment {segment} unexpected blank source literal: "
                    f"{coordinate}"
                )
            if not ENGINE.is_visible_translation_candidate(current_literal.text):
                raise RuntimeError(
                    f"segment {segment} unexpected blank current literal: "
                    f"{coordinate}"
                )
            expected_coordinates.add(coordinate)
            if "…" in current_literal.text:
                actual_current_ellipsis.add(coordinate)

    if set(raw_translations) != expected_coordinates:
        raise RuntimeError(
            f"segment {segment} raw decision coordinate universe drifted"
        )
    if set(translations) != expected_coordinates:
        raise RuntimeError(
            f"segment {segment} resolved decision coordinate universe drifted"
        )
    expected_count = sum(record_arities.values()) - len(
        excluded_nonvisible_coordinates
    )
    if len(translations) != expected_count:
        raise RuntimeError(f"segment {segment} visible decision count drifted")
    if actual_current_ellipsis != ellipsis_coordinates:
        raise RuntimeError(
            f"segment {segment} current ellipsis coordinates drifted"
        )

    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        current_text = ENGINE.parse_record_literals(
            current_records[(block_id, record_id)]
        )[literal_id].text
        if UTIL.layout_signature(translation) != UTIL.layout_signature(
            current_text
        ):
            raise RuntimeError(
                f"segment {segment} layout/outer signature drifted: "
                f"{coordinate}"
            )
        if "\r" in translation or ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(
                f"segment {segment} forbidden script/control drifted: "
                f"{coordinate}"
            )
        if UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(
                f"segment {segment} retains banned fullwidth punctuation: "
                f"{coordinate}"
            )
        if "…" in translation.replace("……", ""):
            raise RuntimeError(
                f"segment {segment} retains an unpaired ellipsis: "
                f"{coordinate}"
            )

    semantic_assertions(source_records, raw_translations, translations)


def build_segment_rows(
    *,
    output: Path,
    segment: int,
    raw_translations: dict[str, str],
    record_arities: dict[int, int],
    pk_record_map: dict[int, int],
    expected_base_jp: dict[int, tuple[str, ...]],
    expected_pk_jp: dict[int, tuple[str, ...]],
    base_gaps: dict[int, tuple[str, ...]],
    pk_jp_gaps: dict[int, tuple[str, ...]],
    ellipsis_coordinates: set[str],
    auxiliary_overrides: dict[
        tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
    ],
    excluded_nonvisible_coordinates: dict[str, str],
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
    translations = UTIL.resolved_translations(
        current_records,
        raw_translations,
    )
    assert_scope(
        prepared,
        segment=segment,
        raw_translations=raw_translations,
        translations=translations,
        record_arities=record_arities,
        pk_record_map=pk_record_map,
        expected_base_jp=expected_base_jp,
        expected_pk_jp=expected_pk_jp,
        base_gaps=base_gaps,
        pk_jp_gaps=pk_jp_gaps,
        ellipsis_coordinates=ellipsis_coordinates,
        auxiliary_overrides=auxiliary_overrides,
        excluded_nonvisible_coordinates=excluded_nonvisible_coordinates,
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
    for source_id, duplicate_id in EXACT_FIELD_COMPLETION_PAIRS.items():
        if CORE.source_literals(
            source_records,
            source_id,
        ) != CORE.source_literals(source_records, duplicate_id):
            raise RuntimeError(
                f"segment 884 exact field-completion source pair drifted: "
                f"{source_id}/{duplicate_id}"
            )
        if raw_translations[f"15:{source_id}:0"] != raw_translations[
            f"15:{duplicate_id}:0"
        ]:
            raise RuntimeError(
                f"segment 884 exact field-completion translation pair "
                f"drifted: {source_id}/{duplicate_id}"
            )
    for record_id, source_id in S883_COMPLETION_SOURCE_IDS.items():
        if CORE.source_literals(
            source_records,
            record_id,
        ) != CORE.source_literals(source_records, source_id):
            raise RuntimeError(
                f"segment 884 B106 S883 completion source reuse drifted: "
                f"{record_id}/{source_id}"
            )
        if raw_translations[f"15:{record_id}:0"] != (
            PREVIOUS.RAW_TRANSLATIONS[f"15:{source_id}:0"]
        ):
            raise RuntimeError(
                f"segment 884 B106 S883 completion translation reuse drifted: "
                f"{record_id}/{source_id}"
            )
    if tuple(
        raw_translations[f"15:1335:{literal_id}"]
        for literal_id in range(5)
    ) != TROOP_CHANGE_SUMMARY:
        raise RuntimeError("segment 884 troop-change UI canonical drifted")
    joined = "\n".join(translations.values())
    for required in (
        "병력을 보충",
        "병사를 보충",
        "성으로 돌아갔다면",
        "시간을 허비",
        "교전",
        "무사히 데려다",
        "병력이",
        "증가",
        "감소",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 884 reinforcement semantics drifted: {required}"
            )
    if any(term in joined for term in ("병사의 보충", "성에 돌아가")):
        raise RuntimeError(
            "segment 884 retained forbidden reinforcement phrasing"
        )


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        expected_base_jp=EXPECTED_BASE_JP,
        expected_pk_jp=EXPECTED_PK_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        auxiliary_overrides=AUXILIARY_OVERRIDES,
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(validated) != len(translations):
        raise RuntimeError("segment 884 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S884",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "exact_field_completion_pairs": len(
                    EXACT_FIELD_COMPLETION_PAIRS
                ),
                "b106_s883_completion_canonical_reuses": len(
                    S883_COMPLETION_SOURCE_IDS
                ),
                "explicit_pk_mapping": True,
                "contextual_ellipsis_normalized_to_project_pair": 0,
                "record_count": 19152,
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
