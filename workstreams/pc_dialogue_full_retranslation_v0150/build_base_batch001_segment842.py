#!/usr/bin/env python3
"""Build Base authoring segment 842 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment821 as CORE


ENGINE = CORE.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S842.private.v1.jsonl"
SEGMENT = 842
RAW_TRANSLATIONS: dict[str, str] = {
    "15:761:0": (
        "의 인근 군에서 급히 병사를 모았습니다\n"
        "여러 대가를 치르고 얻은 병사입니다\n"
        "부디 이 병력으로 성을 지켜 주십시오"
    ),
    "15:762:0": (
        "의 인근 군에서 병사를 긁어모았사옵니다\n"
        "이를 한탄하는 백성도 이 병력으로 지켜질 것이옵니다\n"
        "지휘를… 부탁드리옵니다"
    ),
    "15:763:0": (
        "의 인근 군에서 병사를 모았사옵니다\n"
        "치른 희생은 예상한 범위 안이옵니다\n"
        "모처럼 얻은 병사이니 잘 활용해 주시옵소서"
    ),
    "15:764:0": (
        "의 주변에서 병사를 긁어모았습니다\n"
        "다소 무리한 점은 너그러이 용서해 주십시오\n"
        "그럼 전투에 전념해야 하겠습니다"
    ),
    "15:765:0": (
        "주변에서 병사를 긁어모았사옵니다\n"
        "오늘 백성의 탄식을 내일의 평안으로 잇기 위해\n"
        "기필코 적이 영내를 유린하게 두지 않겠사옵니다"
    ),
    "15:766:0": (
        "의 인근에서 병사를 긁어모았습니다\n"
        "백성의 반발은 있었습니다만\n"
        "우선 지켜 내고 봐야겠지요"
    ),
    "15:767:0": (
        "인근에서 급히 병사를 모았다\n"
        "백성에게 무리를 강요하고 말았으나\n"
        "적을 몰아내지 못하면 거기서 끝이다"
    ),
    "15:768:0": (
        "의 인근에서 급히 병사를 모았습니다\n"
        "백성의 고통에 보답하기 위해서라도\n"
        "우선 끝까지 지켜 내야겠습니다"
    ),
    "15:769:0": (
        "의 인근에서 급히 병사를 모았습니다\n"
        "백성은 불만이겠지만, 패한다면\n"
        "불만으로 끝날 일이 아닐 테니 말입니다"
    ),
    "15:770:0": "·",
    "15:770:1": "의 병력이 일시적으로",
    "15:770:2": "상승\n·",
    "15:770:3": "소속 군의 민충",
    "15:771:0": "·",
    "15:771:1": "의 병력이 일시적으로",
    "15:771:2": "상승\n·",
    "15:771:3": "소속 군의 민충",
    "15:772:0": "의",
    "15:772:1": "에서\n대규모 징병이 실시되어\n많은 병사가 모인 듯",
    "15:773:0": "의 병력이",
    "15:773:1": "상승",
}
RECORD_ARITIES = {
    **{record_id: 1 for record_id in range(761, 770)},
    770: 4,
    771: 4,
    772: 3,
    773: 2,
}
EXPECTED_JP = {
    761: (
        "の近隣郡から急ぎ兵を集めました\n"
        "様々なものを代償に得た兵です\n"
        "どうか、これで城を守ってください",
    ),
    762: (
        "の近隣郡より兵をかき集めました\n"
        "これに嘆く民も、この兵で守られよう\n"
        "采配…頼みましたぞ",
    ),
    763: (
        "の近隣郡より兵を集めました\n"
        "失ったものは想定内です\n"
        "せっかく得た兵、活かしてくだされ",
    ),
    764: (
        "の周辺で兵をかき集めました\n"
        "多少の無理のほどは、ご容赦を\n"
        "それでは、戦に集中いたしましょう",
    ),
    765: (
        "周りにて兵をかき集めましたわ\n"
        "今日の民の嘆きを、明日の安堵に繋げるため\n"
        "きっと敵めに領内を荒らさせますまいぞ",
    ),
    766: (
        "の近隣から兵をかき集めました\n"
        "民の反発はありましたが\n"
        "まずは守り切ってからですね",
    ),
    767: (
        "近隣より急ぎ兵を集めた\n"
        "民に無理を強いてしまったが\n"
        "敵を排除できねばそこでお仕舞いだ",
    ),
    768: (
        "の近隣で急ぎ兵を集めました\n"
        "民の苦しみに報いるためにも\n"
        "まずは守り切りましょう",
    ),
    769: (
        "の近隣から急ぎ兵を集めました\n"
        "民は不満でしょうが、負ければ\n"
        "不満どころじゃすみませんからな",
    ),
    770: ("・", "の兵力が一時的に", "上昇\n・", "所属郡の民忠"),
    771: ("・", "の兵力が一時的に", "上昇\n・", "所属郡の民忠"),
    772: (
        "の",
        "にて\n大規模な徴兵が実施され\n多くの兵が集ったよう",
        "",
    ),
    773: ("の兵力が", "上昇"),
}
EXPECTED_BASE_GAPS = {
    **{record_id: ("026432", "050505") for record_id in range(761, 770)},
    770: ("", "026432", "0232", "026432", "0233050505"),
    771: ("", "026432", "0232", "026432", "0233050505"),
    772: ("026433", "026432", "01432c020000", "050505"),
    773: ("026432", "0232", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    772: ("026433", "026432", "014338020000", "050505"),
}
EXCLUDED_BLANK_COORDINATES = {"15:772:2"}
CURRENT_ELLIPSIS_COORDINATES = {"15:762:0"}
SC_AUXILIARY = {
    772: (
        ("于", "的", "\n实施了大规模的徵兵，\n似乎有不少士兵聚集。"),
        ("", "026433", "026432", "050505"),
    ),
    773: (("的士兵提升", "。"), ("026432", "0232", "050505")),
}
TC_AUXILIARY = {
    772: (
        ("於", "的", "\n實施了大規模的徵兵，\n似乎有不少士兵聚集。"),
        ("", "026433", "026432", "050505"),
    ),
    773: (("的兵力", "上升"), ("026432", "0232", "050505")),
}
EN_AUXILIARY = {
    772: (
        (
            "A large-scale conscription was carried out at ",
            "Ös ",
            ", and many soldiers were gathered.",
        ),
        ("", "026433", "026432", "050505"),
    ),
    773: (
        ("Ös soldiers increased by ", "."),
        ("026432", "0232", "050505"),
    ),
}
AUXILIARY_OVERRIDES = {
    **{
        (side, "SC", record_id): value
        for side in ("base", "pk")
        for record_id, value in SC_AUXILIARY.items()
    },
    **{
        (side, "TC", record_id): value
        for side in ("base", "pk")
        for record_id, value in TC_AUXILIARY.items()
    },
    **{
        ("pk", "EN", record_id): value
        for record_id, value in EN_AUXILIARY.items()
    },
}
BASIS = (
    "pristine_base_pc_jp_authoritative_emergency_conscription_results_and_"
    "troop_popular_loyalty_ui_with_uniform_plus_7_pk_jp_sc_tc_mapping_pk_"
    "en_auxiliary_context_dynamic_county_castle_force_and_value_tokens_"
    "historical_speaker_register_current_pc_layout_opcode_skeleton_excluded_"
    "empty_literal_and_isolated_reverse_overlay_verified_runtime_assembly_pending"
)


def assert_scope_with_exclusions(
    prepared: Any,
    *,
    segment: int,
    raw_translations: dict[str, str],
    translations: dict[str, str],
    record_arities: dict[int, int],
    expected_jp: dict[int, tuple[str, ...]],
    base_gaps: dict[int, tuple[str, ...]],
    pk_jp_gaps: dict[int, tuple[str, ...]],
    ellipsis_coordinates: set[str],
    auxiliary_overrides: dict[
        tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
    ],
    excluded_blank_coordinates: set[str],
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
    CORE.assert_context_mapping(
        segment=segment,
        record_arities=record_arities,
        expected_jp=expected_jp,
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
        expected_gaps = CORE.COMMON.gaps_from_hex(base_gaps[record_id])
        if (
            CORE.COMMON.record_gaps(source_record) != expected_gaps
            or CORE.COMMON.record_gaps(current_record) != expected_gaps
        ):
            raise RuntimeError(
                f"segment {segment} Base dynamic skeleton drifted: 15:{record_id}"
            )
        for literal_id, (source_literal, current_literal) in enumerate(
            zip(source_literals, current_literals)
        ):
            coordinate = f"15:{record_id}:{literal_id}"
            if coordinate in excluded_blank_coordinates:
                if (
                    source_literal.text != ""
                    or current_literal.text != ""
                    or ENGINE.is_visible_translation_candidate(source_literal.text)
                    or ENGINE.is_visible_translation_candidate(current_literal.text)
                    or coordinate in raw_translations
                    or coordinate in translations
                ):
                    raise RuntimeError(
                        f"segment {segment} excluded blank literal drifted: {coordinate}"
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
    expected_count = sum(record_arities.values()) - len(excluded_blank_coordinates)
    if len(translations) != expected_count:
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
        if CORE.COMMON.layout_signature(translation) != CORE.COMMON.layout_signature(
            current_text
        ):
            raise RuntimeError(
                f"segment {segment} layout/outer signature drifted: {coordinate}"
            )
        if "\r" in translation or ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(
                f"segment {segment} forbidden script/control drifted: {coordinate}"
            )
        if CORE.COMMON.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation):
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
    ellipsis_coordinates: set[str],
    auxiliary_overrides: dict[
        tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
    ],
    excluded_blank_coordinates: set[str],
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
    translations = CORE.COMMON.resolved_translations(
        current_records, raw_translations
    )
    assert_scope_with_exclusions(
        prepared,
        segment=segment,
        raw_translations=raw_translations,
        translations=translations,
        record_arities=record_arities,
        expected_jp=expected_jp,
        base_gaps=base_gaps,
        pk_jp_gaps=pk_jp_gaps,
        ellipsis_coordinates=ellipsis_coordinates,
        auxiliary_overrides=auxiliary_overrides,
        excluded_blank_coordinates=excluded_blank_coordinates,
        semantic_assertions=semantic_assertions,
    )
    CORE.COMMON.assert_isolated_overlay_roundtrip(
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
    if CORE.source_literals(source_records, 770) != CORE.source_literals(
        source_records, 771
    ):
        raise RuntimeError("segment 842 770/771 exact UI source group drifted")
    for literal_id in range(4):
        if raw_translations[f"15:770:{literal_id}"] != raw_translations[
            f"15:771:{literal_id}"
        ]:
            raise RuntimeError(
                f"segment 842 770/771 exact UI translation drifted: {literal_id}"
            )
    if raw_translations["15:772:0"] != "의" or not raw_translations[
        "15:772:1"
    ].startswith("에서\n"):
        raise RuntimeError("segment 842 15:772 dynamic force/castle particles drifted")
    if "15:772:2" in raw_translations:
        raise RuntimeError("segment 842 excluded blank received a raw decision")

    dynamic_possessives = {
        761,
        762,
        763,
        764,
        766,
        768,
        769,
    }
    for record_id in dynamic_possessives:
        if not translations[f"15:{record_id}:0"].startswith("의 "):
            raise RuntimeError(
                f"segment 842 dynamic nearby-county particle drifted: {record_id}"
            )
    if not translations["15:773:0"].startswith("의 병력이"):
        raise RuntimeError("segment 842 15:773 dynamic troop subject drifted")

    joined = "\n".join(translations.values())
    for required in ("병사", "병력", "백성", "민충", "군", "대규모 징병"):
        if required not in joined:
            raise RuntimeError(
                f"segment 842 conscription/UI terminology drifted: {required}"
            )
    if any(
        forbidden in joined
        for forbidden in ("당가", "민심", "현", "징집병", "호족")
    ):
        raise RuntimeError("segment 842 retained forbidden legacy terminology")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        expected_jp=EXPECTED_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        auxiliary_overrides=AUXILIARY_OVERRIDES,
        excluded_blank_coordinates=EXCLUDED_BLANK_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 842 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S842",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "excluded_blank_decisions": len(EXCLUDED_BLANK_COORDINATES),
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
