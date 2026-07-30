#!/usr/bin/env python3
"""Build Base authoring segment 869 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment863 as LEGACY


ENGINE = LEGACY.ENGINE
CORE = LEGACY.CORE
UTIL = LEGACY.COMMON
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S869.private.v1.jsonl"
SEGMENT = 869
STANCE_CHANGE = ("와(과)의 외교 자세가 「", "」→「", "」(으)로 변경")
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1121:0": "·이간 공작으로 인해,",
    "15:1121:1": "와(과)",
    "15:1121:2": "이(가) 단교",
    "15:1122:0": "·",
    "15:1122:1": "와(과)의 우호도 하락\n·",
    "15:1122:2": "와(과)의 우호도 하락\n·우리 가문의 악명",
    "15:1122:3": "→",
    "15:1123:0": "와(과)",
    "15:1123:1": "사이에",
    "15:1123:2": "일간 교섭 불가",
    "15:1124:0": "와(과)",
    "15:1124:1": "을(를) 대상으로 한 이간 공작에 실패",
    **{
        f"15:{record_id}:{literal_id}": translation
        for record_id in (1125, 1126)
        for literal_id, translation in enumerate(STANCE_CHANGE)
    },
    "15:1127:0": "…\n역시, 믿을 수",
    "15:1127:1": "인가",
    "15:1128:0": (
        "에서 온 사자가 교섭에 응하지 않겠다고 하옵니다…!\n"
        "우리 가문에 대한 악평이 온 나라에 퍼졌다고 합니다\n"
    ),
    "15:1128:1": "의",
    "15:1128:2": "…",
}
RECORD_ARITIES = {
    1121: 3,
    1122: 4,
    1123: 3,
    1124: 2,
    1125: 3,
    1126: 3,
    1127: 2,
    1128: 3,
}
EXPECTED_BASE_JP = {
    1121: ("・離間工作により、", "と", "が手切"),
    1122: (
        "・",
        "との友好度が低下\n・",
        "との友好度が低下\n・当家の悪名",
        "→",
    ),
    1123: ("と", "の間で", "日間交渉不可"),
    1124: ("と", "への離間計に失敗"),
    1125: ("との外交姿勢が「", "」→「", "」に"),
    1126: ("との外交姿勢が「", "」→「", "」に"),
    1127: ("…\nやはり、信用な", "か"),
    1128: (
        "より、交渉に応じぬと使者が…！\n"
        "当家に対する悪評を国中で聞くとのこと\n",
        "の",
        "…",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1121: ("", "025032", "025132", "050505"),
    1122: ("", "025032", "025132", "0232", "1b434b02331b435a050505"),
    1123: ("025132", "025032", "023c", "050505"),
    1124: ("025032", "025132", "050505"),
    1125: ("025032", "023c", "023d", "050505"),
    1126: ("025032", "023c", "023d", "050505"),
    1127: ("025033", "01432a040000", "050505"),
    1128: ("025132", "025032", "023c01435c0200000143ce020000", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1127: ("025033", "014336040000", "050505"),
    1128: ("025132", "025032", "023c0143680200000143da020000", "050505"),
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:1127:0",
    "15:1128:0",
    "15:1128:2",
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
AUXILIARY_OVERRIDES = {
    **{
        (side, "SC", 1123): (
            ("在", "日内，", "和", "無法交涉。"),
            ("", "023c", "025132", "025032", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1123): (
            ("天內，", "和", "無法交涉。"),
            ("023c", "025132", "025032", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1123): (
        (
            "Negotiations between the ",
            " and the ",
            " will be unavailable for ",
            " day(s).",
        ),
        ("", "025132", "025032", "023c", "050505"),
    ),
    **{
        (side, "SC", 1124): (
            ("对", "和", "的离间之计失败。"),
            ("", "025032", "025132", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1124): (
            ("對", "和", "的離間計，失敗。"),
            ("", "025032", "025132", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1124): (
        ("The bondbreaker ploy aimed at the ", " and the ", " has failed."),
        ("", "025032", "025132", "050505"),
    ),
    **{
        (side, language, record_id): (
            (
                ("与", "的外交态度由「", "」变为「", "」")
                if language == "SC"
                else ("與", "的外交態度由「", "」變為「", "」")
            ),
            ("", "025032", "023c", "023d", "050505"),
        )
        for side in ("base", "pk")
        for language in ("SC", "TC")
        for record_id in (1125, 1126)
    },
    **{
        ("pk", "EN", record_id): (
            ("Diplomatic stance with the ", " has gone from ", " to ", "."),
            ("", "025032", "023c", "023d", "050505"),
        )
        for record_id in (1125, 1126)
    },
    **{
        (side, "SC", 1127): (
            ("……\n果然无法信赖啊。",),
            ("025033", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1127): (
            ("……\n果然無法信賴啊。",),
            ("025033", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1127): (
        ("I guess ", " canÖt be trusted after all..."),
        ("", "025033", "050505"),
    ),
    **{
        (side, "SC", 1128): (
            (
                "使者称",
                "不会接受交涉……！\n说是在国内听到了对本家的恶评。\n是",
                "的",
                "吧……",
            ),
            ("", "025132", "025032", "023c", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1128): (
            (
                "使者傳來消息，",
                "不會接受交涉……！\n據說是國內流傳著對本家的惡評。\n或許是",
                "的",
                "吧……",
            ),
            ("", "025132", "025032", "023c", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1128): (
        (
            " sent a messenger to tell us he wonÖt negotiate! IÖm sure youÖve heard the bad rumors being spread about our clan by now. It must be the ",
            "Ös ",
            "...",
        ),
        ("025132", "025032", "023c", "050505"),
    ),
}
BASIS = (
    "review_queue_base_msggame_B105_pristine_base_pc_jp_authoritative_"
    "sowing_discord_results_ui_diplomatic_stance_failure_and_bad_reputation_"
    "reports_with_uniform_plus_8_pk_mapping_explicit_base_and_pk_jp_arrays_"
    "base_pk_sc_tc_exact_pk_en_auxiliary_dynamic_house_value_action_and_"
    "conjugation_tokens_project_diplomacy_terminology_current_layout_and_"
    "opcode_skeleton_runtime_fragment_pending"
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
    mapped_ids = {record_id + 8 for record_id in record_arities}
    expected_mapped_ids = set(range(min(record_arities) + 8, max(record_arities) + 9))
    if mapped_ids != expected_mapped_ids or mapped_ids & UTIL.PK_ONLY_RECORD_IDS:
        raise RuntimeError(f"segment {segment} uniform +8 mapping drifted")
    for record_id in record_arities:
        base_record = source_records[(15, record_id)]
        pk_record = pk_source_records[(15, record_id + 8)]
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
                f"segment {segment} mapped PK JP literal array drifted: {record_id + 8}"
            )
        if UTIL.record_gaps(base_record) != UTIL.gaps_from_hex(base_gaps[record_id]):
            raise RuntimeError(
                f"segment {segment} Base JP token skeleton drifted: {record_id}"
            )
        if UTIL.record_gaps(pk_record) != UTIL.gaps_from_hex(pk_jp_gaps[record_id]):
            raise RuntimeError(
                f"segment {segment} PK JP token skeleton drifted: {record_id + 8}"
            )
        for side, languages, mapped_id in (
            ("base", ("SC", "TC"), record_id),
            ("pk", ("SC", "TC", "EN"), record_id + 8),
        ):
            records_by_language = base_context if side == "base" else pk_context
            for language in languages:
                expected_literals, expected_gaps = expected_auxiliary(
                    side, language, record_id, auxiliary_overrides
                )
                record = records_by_language[language][(15, mapped_id)]
                actual_literals = tuple(
                    literal.text for literal in ENGINE.parse_record_literals(record)
                )
                if actual_literals != expected_literals:
                    raise RuntimeError(
                        f"segment {segment} {side} {language} literal array drifted: "
                        f"{mapped_id}"
                    )
                if UTIL.record_gaps(record) != UTIL.gaps_from_hex(expected_gaps):
                    raise RuntimeError(
                        f"segment {segment} {side} {language} token skeleton drifted: "
                        f"{mapped_id}"
                    )


def assert_scope(
    prepared: Any,
    *,
    segment: int,
    raw_translations: dict[str, str],
    translations: dict[str, str],
    record_arities: dict[int, int],
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
    if len(translations) != sum(record_arities.values()) - len(
        excluded_nonvisible_coordinates
    ):
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
    translations = UTIL.resolved_translations(current_records, raw_translations)
    assert_scope(
        prepared,
        segment=segment,
        raw_translations=raw_translations,
        translations=translations,
        record_arities=record_arities,
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
    if CORE.source_literals(source_records, 1125) != CORE.source_literals(
        source_records, 1126
    ):
        raise RuntimeError("segment 869 exact diplomatic-stance source pair drifted")
    for literal_id in range(3):
        if raw_translations[f"15:1125:{literal_id}"] != raw_translations[
            f"15:1126:{literal_id}"
        ]:
            raise RuntimeError(
                f"segment 869 exact diplomatic-stance translation pair drifted: "
                f"{literal_id}"
            )
    if raw_translations["15:1127:0"] != "…\n역시, 믿을 수":
        raise RuntimeError("segment 869 1127 trust opcode stem drifted")
    if raw_translations["15:1127:1"] != "인가":
        raise RuntimeError("segment 869 1127 question completion drifted")
    joined = "\n".join(translations.values())
    for required in ("이간 공작", "단교", "우호도", "악명", "교섭"):
        if required not in joined:
            raise RuntimeError(f"segment 869 diplomacy terminology drifted: {required}")
    if any(term in joined for term in ("이간계", "절연", "당가", "본가")):
        raise RuntimeError("segment 869 retained forbidden diplomacy terminology")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
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
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 869 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S869",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "excluded_nonvisible_decisions": len(
                    EXCLUDED_NONVISIBLE_COORDINATES
                ),
                "contextual_ellipsis_normalized_to_project_pair": len(
                    CURRENT_ELLIPSIS_COORDINATES
                ),
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
