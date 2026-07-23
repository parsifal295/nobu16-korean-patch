#!/usr/bin/env python3
"""Build Base authoring segment 856 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment855 as PRIOR


COMMON = PRIOR.COMMON
ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S856.private.v1.jsonl"
SEGMENT = 856
CAPTURE_TRANSLATIONS = {
    "15:973:0": "에서 간자를 붙잡아",
    "15:973:2": "이(가) 벌인",
    "15:973:3": "이(가) 밀명이었다니…\n하마터면 큰일 날 뻔했소",
}
RAW_TRANSLATIONS: dict[str, str] = {
    "15:967:0": PRIOR.FAILURE_TRANSLATION,
    "15:968:0": PRIOR.FAILURE_TRANSLATION,
    "15:969:0": "·",
    "15:969:1": "의 내구가",
    "15:969:2": "감소\n·",
    "15:969:3": "의 병력이",
    "15:969:4": "감소",
    "15:970:0": "·",
    "15:970:1": "에 대한 공작 실패",
    "15:971:0": "·",
    "15:971:1": "에 대한 공작 실패",
    "15:972:0": "의 간자가 벌인",
    "15:972:1": "을(를) 받아\n",
    "15:972:2": "의 내구에",
    "15:972:3": "\n병력에",
    "15:972:4": "의 피해가 발생하",
    "15:972:5": "…",
    **CAPTURE_TRANSLATIONS,
    "15:974:0": "이(가)",
    "15:974:1": "에 대한 공작에 성공",
    "15:975:0": "에 대한 공작에 실패하여,",
    "15:975:1": "이(가) 부상",
}
RECORD_ARITIES = {
    967: 1,
    968: 1,
    969: 5,
    970: 2,
    971: 2,
    972: 6,
    973: 4,
    974: 2,
    975: 2,
}
EXPECTED_JP = {
    967: PRIOR.FAILURE_SOURCE,
    968: PRIOR.FAILURE_SOURCE,
    969: ("・", "の耐久が", "減少\n・", "の兵力が", "減少"),
    970: ("・", "の工作に失敗"),
    971: ("・", "の工作に失敗"),
    972: ("の間者による", "を受け\n", "の耐久に", "\n兵力に", "の被害が出", "…"),
    973: ("にて間者を捕らえ", "\n", "による", "が密命とか…\n危ないところ"),
    974: ("が", "の工作に成功"),
    975: ("の工作に失敗し、", "が負傷"),
}
EXPECTED_BASE_GAPS = {
    967: ("026432", "050505"),
    968: ("026432", "050505"),
    969: ("", "026432", "0232", "026432", "0233", "050505"),
    970: ("", "026432", "050505"),
    971: ("", "026432", "050505"),
    972: (
        "025032",
        "023c",
        "026432",
        "0232",
        "0233",
        "014314020000",
        "050505",
    ),
    973: (
        "026432",
        "014314020000",
        "025032",
        "023c",
        "01433e020000050505",
    ),
    974: ("024633", "026432", "050505"),
    975: ("026432", "024633", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    972: (
        "025032",
        "023c",
        "026432",
        "0232",
        "0233",
        "01431a020000",
        "050505",
    ),
    973: (
        "026432",
        "01431a020000",
        "025032",
        "023c",
        "01434a020000050505",
    ),
}
EXCLUDED_BLANK_COORDINATES = {"15:973:1"}
CURRENT_ELLIPSIS_COORDINATES = {"15:972:5", "15:973:3"}
SC_972 = (
    "因",
    "的间谍发动的",
    "，\n",
    "的耐久已受害",
    "，\n兵力已受害",
    "……",
)
TC_972 = (
    "因",
    "的間諜發動的",
    "，\n",
    "的耐久已受害",
    "，\n兵力已受害",
    "……",
)
EN_972 = (
    "After sustaining ",
    " from the ",
    " spy net, ",
    " suffered ",
    " HP damage and lost ",
    " soldier(s).",
)
SC_973 = ("已于", "逮捕间谍。\n据说是", "的", "发出密令……\n差点就没命了。")
TC_973 = ("已於", "逮捕間諜。\n據說是", "的", "發出密令……\n差點就沒命了。")
EN_973 = (
    "WeÖve captured spies in ",
    ". They had the ",
    "Ös ",
    " secret orders... That could have been bad.",
)
SC_974 = ("对", "的破坏工作成功了。")
TC_974 = ("對", "破壞工作成功。")
EN_974 = (" successfully destabilized ", ".")
SC_975 = ("的破坏工作失败了，", "负伤。")
TC_975 = ("破壞工作失敗，", "負傷。")
EN_975 = ("The destabilization of ", " was a failure. ", " was injured.")
AUXILIARY_OVERRIDES = {
    **{
        (side, "SC", 972): (
            SC_972,
            ("", "025032", "023c", "026432", "0232", "0233", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 972): (
            TC_972,
            ("", "025032", "023c", "026432", "0232", "0233", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 972): (
        EN_972,
        ("", "023c", "025032", "026432", "0232", "0233", "050505"),
    ),
    **{
        (side, "SC", 973): (
            SC_973,
            ("", "026432", "025032", "023c", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 973): (
            TC_973,
            ("", "026432", "025032", "023c", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 973): (
        EN_973,
        ("", "026432", "025032", "023c", "050505"),
    ),
    **{
        (side, "SC", 974): (SC_974, ("024633", "026432", "050505"))
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 974): (TC_974, ("024633", "026432", "050505"))
        for side in ("base", "pk")
    },
    ("pk", "EN", 974): (EN_974, ("024633", "026432", "050505")),
    **{
        (side, "SC", 975): (SC_975, ("026432", "024633", "050505"))
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 975): (TC_975, ("026432", "024633", "050505"))
        for side in ("base", "pk")
    },
    ("pk", "EN", 975): (
        EN_975,
        ("", "026432", "024633", "050505"),
    ),
}
BASIS = (
    "review_queue_base_msggame_B103_pristine_base_pc_jp_authoritative_"
    "destabilization_failure_ui_damage_spy_capture_success_injury_fragments_"
    "with_exact_24_record_failure_and_970_971_groups_cross_batch_907_973_full_"
    "source_group_uniform_plus_7_pk_jp_sc_tc_arrays_pk_en_sc_tc_context_"
    "dynamic_token_order_numeric_particles_excluded_973_1_newline_preserved_"
    "runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for record_id in range(945, 969):
        if COMMON.CORE.source_literals(source_records, record_id) != PRIOR.FAILURE_SOURCE:
            raise RuntimeError(
                f"segment 856 exact failure source group drifted: {record_id}"
            )
    for record_id in (967, 968):
        if raw_translations[f"15:{record_id}:0"] != PRIOR.FAILURE_TRANSLATION:
            raise RuntimeError(
                f"segment 856 exact failure translation drifted: {record_id}"
            )
    if COMMON.CORE.source_literals(
        source_records, 970
    ) != COMMON.CORE.source_literals(source_records, 971):
        raise RuntimeError("segment 856 970/971 exact UI source group drifted")
    for literal_id in range(2):
        if raw_translations[f"15:970:{literal_id}"] != raw_translations[
            f"15:971:{literal_id}"
        ]:
            raise RuntimeError(
                f"segment 856 970/971 exact UI translation drifted: {literal_id}"
            )
    if COMMON.CORE.source_literals(
        source_records, 907
    ) != COMMON.CORE.source_literals(source_records, 973):
        raise RuntimeError("segment 856 907/973 full-source exact group drifted")
    for coordinate, expected in CAPTURE_TRANSLATIONS.items():
        if raw_translations[coordinate] != expected:
            raise RuntimeError(f"segment 856 973 canonical drifted: {coordinate}")
    if "15:973:1" in raw_translations or "15:973:1" in translations:
        raise RuntimeError("segment 856 excluded newline received a decision")

    exact_expectations = {
        "15:969:1": "의 내구가",
        "15:970:1": "에 대한 공작 실패",
        "15:972:0": "의 간자가 벌인",
        "15:972:2": "의 내구에",
        "15:972:4": "의 피해가 발생하",
        "15:973:0": "에서 간자를 붙잡아",
        "15:973:2": "이(가) 벌인",
        "15:973:3": "이(가) 밀명이었다니…\n하마터면 큰일 날 뻔했소",
        "15:974:0": "이(가)",
        "15:974:1": "에 대한 공작에 성공",
        "15:975:0": "에 대한 공작에 실패하여,",
        "15:975:1": "이(가) 부상",
    }
    for coordinate, expected in exact_expectations.items():
        if raw_translations[coordinate] != expected:
            raise RuntimeError(
                f"segment 856 token order/particle/terminology drifted: {coordinate}"
            )
    joined = "\n".join(translations.values())
    for required in ("내구", "공작", "간자", "병력", "피해", "부상"):
        if required not in joined:
            raise RuntimeError(f"segment 856 terminology drifted: {required}")
    if any(term in joined for term in ("내구도", "책략", "첩자", "공작원")):
        raise RuntimeError("segment 856 retained forbidden terminology")


def assert_scope_with_newline_exclusion(
    prepared: Any,
    *,
    raw_translations: dict[str, str],
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
    COMMON.CORE.assert_context_mapping(
        segment=SEGMENT,
        record_arities=RECORD_ARITIES,
        expected_jp=EXPECTED_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        auxiliary_overrides=AUXILIARY_OVERRIDES,
        source_records=source_records,
        pk_source_records=pk_source_records,
        base_context=base_context,
        pk_context=pk_context,
    )

    expected_coordinates = set()
    actual_current_ellipsis = set()
    for record_id, arity in RECORD_ARITIES.items():
        source_record = source_records[(15, record_id)]
        current_record = current_records[(15, record_id)]
        source_literals = ENGINE.parse_record_literals(source_record)
        current_literals = ENGINE.parse_record_literals(current_record)
        if len(source_literals) != arity or len(current_literals) != arity:
            raise RuntimeError(
                f"segment 856 source/current arity drifted: 15:{record_id}"
            )
        expected_gaps = COMMON.CORE.COMMON.gaps_from_hex(
            EXPECTED_BASE_GAPS[record_id]
        )
        if (
            COMMON.CORE.COMMON.record_gaps(source_record) != expected_gaps
            or COMMON.CORE.COMMON.record_gaps(current_record) != expected_gaps
        ):
            raise RuntimeError(
                f"segment 856 Base dynamic skeleton drifted: 15:{record_id}"
            )
        for literal_id, (source_literal, current_literal) in enumerate(
            zip(source_literals, current_literals)
        ):
            coordinate = f"15:{record_id}:{literal_id}"
            if coordinate in EXCLUDED_BLANK_COORDINATES:
                if (
                    source_literal.text != "\n"
                    or current_literal.text != "\n"
                    or ENGINE.is_visible_translation_candidate(source_literal.text)
                    or ENGINE.is_visible_translation_candidate(current_literal.text)
                    or coordinate in raw_translations
                    or coordinate in translations
                ):
                    raise RuntimeError(
                        f"segment 856 excluded newline drifted: {coordinate}"
                    )
                continue
            if not ENGINE.is_visible_translation_candidate(source_literal.text):
                raise RuntimeError(f"segment 856 blank source literal: {coordinate}")
            if not ENGINE.is_visible_translation_candidate(current_literal.text):
                raise RuntimeError(f"segment 856 blank current literal: {coordinate}")
            expected_coordinates.add(coordinate)
            if "…" in current_literal.text:
                actual_current_ellipsis.add(coordinate)

    if set(raw_translations) != expected_coordinates:
        raise RuntimeError("segment 856 raw decision coordinate universe drifted")
    if set(translations) != expected_coordinates:
        raise RuntimeError("segment 856 resolved decision coordinate universe drifted")
    if len(translations) != 24:
        raise RuntimeError("segment 856 visible decision count drifted")
    if actual_current_ellipsis != CURRENT_ELLIPSIS_COORDINATES:
        raise RuntimeError("segment 856 current ellipsis coordinates drifted")

    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        current_text = ENGINE.parse_record_literals(
            current_records[(block_id, record_id)]
        )[literal_id].text
        if COMMON.CORE.COMMON.layout_signature(
            translation
        ) != COMMON.CORE.COMMON.layout_signature(current_text):
            raise RuntimeError(
                f"segment 856 layout/outer signature drifted: {coordinate}"
            )
        if "\r" in translation or ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(
                f"segment 856 forbidden script/control drifted: {coordinate}"
            )
        if COMMON.CORE.COMMON.BANNED_FULLWIDTH_PUNCTUATION.intersection(
            translation
        ):
            raise RuntimeError(
                f"segment 856 retains fullwidth punctuation: {coordinate}"
            )
        if "…" in translation.replace("……", ""):
            raise RuntimeError(f"segment 856 retains unpaired ellipsis: {coordinate}")

    assert_semantics(source_records, raw_translations, translations)


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    current_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    translations = COMMON.CORE.COMMON.resolved_translations(
        current_records, RAW_TRANSLATIONS
    )
    assert_scope_with_newline_exclusion(
        prepared,
        raw_translations=RAW_TRANSLATIONS,
        translations=translations,
    )
    COMMON.CORE.COMMON.assert_isolated_overlay_roundtrip(
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
        raise RuntimeError("segment 856 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S856",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "excluded_blank_decisions": len(EXCLUDED_BLANK_COORDINATES),
                "dynamic_runtime_review_pending": len(rows),
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
