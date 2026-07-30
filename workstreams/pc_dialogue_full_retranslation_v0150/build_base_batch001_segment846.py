#!/usr/bin/env python3
"""Build Base authoring segment 846 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment824 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S846.private.v1.jsonl"
SEGMENT = 846
SUCCESS_TRANSLATION = (
    "에서 잇키 선동에 성공했습니다!\n"
    "당분간 진압하는 데 시간이 걸릴 것입니다"
)
RAW_TRANSLATIONS: dict[str, str] = {
    **{f"15:{record_id}:0": SUCCESS_TRANSLATION for record_id in range(815, 824)},
    "15:824:0": "로부터",
    "15:824:1": "을(를) 받아\n",
    "15:824:2": "에서 잇키가 발생하여",
    "15:825:0": "로부터",
    "15:825:1": "을(를) 받아\n",
    "15:825:2": "을(를) 비롯한 총",
    "15:825:3": "개 성에서 잇키가 발생하여",
    "15:826:0": "에서 간자를 붙잡아",
    "15:827:0": "의",
    "15:827:1": "으로(로)",
    "15:827:2": "을(를) 비롯한 총",
    "15:827:3": "개 성에서 잇키 발생",
}
RECORD_ARITIES = {
    **{record_id: 1 for record_id in range(815, 824)},
    824: 3,
    825: 4,
    826: 1,
    827: 4,
}
EXPECTED_BASE_GAPS = {
    **{record_id: ("029632", "050505") for record_id in range(815, 824)},
    824: ("025032", "023c", "026432", "014314020000050505"),
    825: ("025032", "023c", "026432", "0232", "014314020000050505"),
    826: ("026432", "014314020000050505"),
    827: ("025032", "023c", "026432", "0232", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **{record_id: ("029632", "050505") for record_id in range(815, 824)},
    824: ("025032", "023c", "026432", "01431a020000050505"),
    825: ("025032", "023c", "026432", "0232", "01431a020000050505"),
    826: ("026432", "01431a020000050505"),
    827: ("025032", "023c", "026432", "0232", "050505"),
}
EXPECTED_PK_EN_ARITIES = {
    **{record_id: 1 for record_id in range(815, 824)},
    824: 4,
    825: 5,
    826: 2,
    827: 5,
}
EXPECTED_PK_EN_GAPS = {
    **{record_id: ("", "050505") for record_id in range(815, 824)},
    824: ("", "023c", "025032", "026432", "050505"),
    825: ("", "023c", "025032", "0232", "026432", "050505"),
    826: ("", "026432", "050505"),
    827: ("", "025032", "023c", "0232", "026432", "050505"),
}
PK_JP_VARIANTS = {
    825: (
        "より",
        "を受け\n",
        "など",
        "城にて\n一揆が発生し",
    ),
    827: ("の", "で", "など", "城で一揆発生"),
}
EMPTY_RECORD_IDS = set(range(828, 840))
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
BASIS = (
    "pristine_base_pc_jp_authoritative_ikki_success_notification_sender_plot_"
    "multi_castle_outbreak_spy_capture_and_ui_fragments_with_exact_repeated_"
    "success_group_explicit_base_pk_jp_825_827_nado_line_variant_sc_tc_exact_"
    "pk_en_sc_tc_auxiliary_context_828_839_pristine_current_empty_slots_"
    "preserved_current_pc_layout_token_gap_switch_stem_runtime_assembly_pending"
)


def _literal_array(record: Any) -> tuple[str, ...]:
    return tuple(literal.text for literal in ENGINE.parse_record_literals(record))


def assert_empty_slots(prepared: Any) -> None:
    base = prepared.resources["base_msggame"]
    pk = prepared.resources["pk_msggame"]
    base_source = ENGINE.archive_records(base.pristine_archive)
    base_current = ENGINE.archive_records(base.current_archive)
    pk_source = ENGINE.archive_records(pk.pristine_archive)
    base_context = {
        language: ENGINE.archive_records(archive)
        for language, archive in base.context_archives.items()
    }
    pk_context = {
        language: ENGINE.archive_records(archive)
        for language, archive in pk.context_archives.items()
    }
    empty_gaps = COMMON.SHARED.gaps_from_hex(("", "050505"))
    for record_id in EMPTY_RECORD_IDS:
        for label, records, mapped_id in (
            ("Base pristine", base_source, record_id),
            ("Base current", base_current, record_id),
            ("PK pristine", pk_source, record_id + 7),
        ):
            record = records[(15, mapped_id)]
            if (
                _literal_array(record) != ("",)
                or COMMON.SHARED.record_gaps(record) != empty_gaps
                or ENGINE.is_visible_translation_candidate("")
            ):
                raise RuntimeError(
                    f"segment 846 {label} empty slot drifted: {mapped_id}"
                )
        for language in ("SC", "TC"):
            base_aux = base_context[language][(15, record_id)]
            pk_aux = pk_context[language][(15, record_id + 7)]
            if (
                _literal_array(base_aux) != ("",)
                or _literal_array(pk_aux) != ("",)
                or COMMON.SHARED.record_gaps(base_aux) != empty_gaps
                or COMMON.SHARED.record_gaps(pk_aux) != empty_gaps
            ):
                raise RuntimeError(
                    f"segment 846 {language} empty slot drifted: {record_id}"
                )
        pk_en = pk_context["EN"][(15, record_id + 7)]
        if (
            _literal_array(pk_en) != ("",)
            or COMMON.SHARED.record_gaps(pk_en) != empty_gaps
        ):
            raise RuntimeError(f"segment 846 PK EN empty slot drifted: {record_id + 7}")


def assert_context_mapping(
    *,
    source_records: dict[tuple[int, int], Any],
    pk_source_records: dict[tuple[int, int], Any],
    base_context: dict[str, dict[tuple[int, int], Any]],
    pk_context: dict[str, dict[tuple[int, int], Any]],
) -> None:
    mapped_ids = {record_id + 7 for record_id in RECORD_ARITIES}
    if mapped_ids != set(range(822, 835)):
        raise RuntimeError("segment 846 uniform +7 record mapping drifted")

    for record_id, arity in RECORD_ARITIES.items():
        base_record = source_records[(15, record_id)]
        pk_record = pk_source_records[(15, record_id + 7)]
        base_literals = _literal_array(base_record)
        pk_literals = _literal_array(pk_record)
        if len(base_literals) != arity or len(pk_literals) != arity:
            raise RuntimeError(f"segment 846 mapped JP arity drifted: {record_id}")
        if record_id in PK_JP_VARIANTS:
            if pk_literals != PK_JP_VARIANTS[record_id]:
                raise RuntimeError(
                    f"segment 846 expected PK JP variant drifted: {record_id + 7}"
                )
        elif base_literals != pk_literals:
            raise RuntimeError(f"segment 846 mapped PK JP array drifted: {record_id}")
        if COMMON.SHARED.record_gaps(base_record) != COMMON.SHARED.gaps_from_hex(
            EXPECTED_BASE_GAPS[record_id]
        ):
            raise RuntimeError(f"segment 846 Base JP token skeleton drifted: {record_id}")
        if COMMON.SHARED.record_gaps(pk_record) != COMMON.SHARED.gaps_from_hex(
            EXPECTED_PK_JP_GAPS[record_id]
        ):
            raise RuntimeError(
                f"segment 846 PK JP token skeleton drifted: {record_id + 7}"
            )

        for language in ("SC", "TC"):
            base_aux = base_context[language][(15, record_id)]
            pk_aux = pk_context[language][(15, record_id + 7)]
            if (
                _literal_array(base_aux) != _literal_array(pk_aux)
                or COMMON.SHARED.record_gaps(base_aux)
                != COMMON.SHARED.record_gaps(pk_aux)
            ):
                raise RuntimeError(
                    f"segment 846 mapped {language} array/token drifted: {record_id}"
                )

        pk_en = pk_context["EN"][(15, record_id + 7)]
        if len(_literal_array(pk_en)) != EXPECTED_PK_EN_ARITIES[record_id]:
            raise RuntimeError(f"segment 846 PK EN arity drifted: {record_id + 7}")
        if COMMON.SHARED.record_gaps(pk_en) != COMMON.SHARED.gaps_from_hex(
            EXPECTED_PK_EN_GAPS[record_id]
        ):
            raise RuntimeError(
                f"segment 846 PK EN token skeleton drifted: {record_id + 7}"
            )


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    success_source = (
        "で一揆の煽動に成功しました！\n"
        "しばらくは鎮圧に時間がかかるでしょう",
    )
    if any(
        _literal_array(source_records[(15, record_id)]) != success_source
        for record_id in range(815, 824)
    ):
        raise RuntimeError("segment 846 815-823 exact success source group drifted")
    if len(
        {raw_translations[f"15:{record_id}:0"] for record_id in range(815, 824)}
    ) != 1:
        raise RuntimeError("segment 846 815-823 exact success translation group drifted")

    expected_base_variants = {
        825: ("より", "を受け\n", "ら", "城にて一揆が発生し"),
        827: ("の", "で", "ら", "城で一揆発生"),
    }
    for record_id, expected in expected_base_variants.items():
        if _literal_array(source_records[(15, record_id)]) != expected:
            raise RuntimeError(
                f"segment 846 authoritative Base JP variant drifted: {record_id}"
            )

    exact_expectations = {
        "15:824:0": "로부터",
        "15:825:0": "로부터",
        "15:825:2": "을(를) 비롯한 총",
        "15:826:0": "에서 간자를 붙잡아",
        "15:827:0": "의",
        "15:827:1": "으로(로)",
        "15:827:2": "을(를) 비롯한 총",
        "15:827:3": "개 성에서 잇키 발생",
    }
    for coordinate, expected in exact_expectations.items():
        if raw_translations[coordinate] != expected:
            raise RuntimeError(f"segment 846 token role/terminology drifted: {coordinate}")
    joined = "\n".join(translations.values())
    if "보다" in joined or "첩자" in joined or "폭동" in joined:
        raise RuntimeError("segment 846 retained forbidden terminology")


def assert_scope(
    prepared: Any,
    *,
    translations: dict[str, str],
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
        source_records=source_records,
        pk_source_records=pk_source_records,
        base_context=base_context,
        pk_context=pk_context,
    )

    expected_coordinates = set()
    for record_id, arity in RECORD_ARITIES.items():
        source_record = source_records[(15, record_id)]
        current_record = current_records[(15, record_id)]
        source_literals = ENGINE.parse_record_literals(source_record)
        current_literals = ENGINE.parse_record_literals(current_record)
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(f"segment 846 source/current arity drifted: 15:{record_id}")
        expected_gaps = COMMON.SHARED.gaps_from_hex(EXPECTED_BASE_GAPS[record_id])
        if (
            COMMON.SHARED.record_gaps(source_record) != expected_gaps
            or COMMON.SHARED.record_gaps(current_record) != expected_gaps
        ):
            raise RuntimeError(
                f"segment 846 Base dynamic skeleton drifted: 15:{record_id}"
            )
        for literal_id, (source_literal, current_literal) in enumerate(
            zip(source_literals, current_literals)
        ):
            coordinate = f"15:{record_id}:{literal_id}"
            if not ENGINE.is_visible_translation_candidate(source_literal.text):
                raise RuntimeError(f"segment 846 blank source literal: {coordinate}")
            if not ENGINE.is_visible_translation_candidate(current_literal.text):
                raise RuntimeError(f"segment 846 blank current literal: {coordinate}")
            expected_coordinates.add(coordinate)

    if set(RAW_TRANSLATIONS) != expected_coordinates:
        raise RuntimeError("segment 846 raw decision coordinate universe drifted")
    if set(translations) != expected_coordinates or len(translations) != 21:
        raise RuntimeError("segment 846 resolved decision universe/count drifted")
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        current_text = ENGINE.parse_record_literals(
            current_records[(block_id, record_id)]
        )[literal_id].text
        if COMMON.SHARED.layout_signature(
            translation
        ) != COMMON.SHARED.layout_signature(current_text):
            raise RuntimeError(f"segment 846 layout/outer signature drifted: {coordinate}")
        if "\r" in translation or ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(f"segment 846 forbidden script/control: {coordinate}")
        if COMMON.SHARED.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
            raise RuntimeError(f"segment 846 fullwidth punctuation: {coordinate}")
        if "…" in translation.replace("……", ""):
            raise RuntimeError(f"segment 846 unpaired ellipsis: {coordinate}")

    assert_semantics(source_records, RAW_TRANSLATIONS, translations)
    assert_empty_slots(prepared)


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    current_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    translations = COMMON.SHARED.resolved_translations(
        current_records, RAW_TRANSLATIONS
    )
    assert_scope(prepared, translations=translations)
    COMMON.SHARED.assert_isolated_overlay_roundtrip(
        prepared,
        segment=SEGMENT,
        translations=translations,
        record_arities=RECORD_ARITIES,
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
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
            }
        )
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 846 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S846",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "empty_records_preserved_without_decisions": len(EMPTY_RECORD_IDS),
                "dynamic_runtime_review_pending": len(rows),
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
