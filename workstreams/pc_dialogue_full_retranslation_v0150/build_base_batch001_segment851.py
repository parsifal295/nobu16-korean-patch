#!/usr/bin/env python3
"""Build Base authoring segment 851 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment842 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S851.private.v1.jsonl"
SEGMENT = 851
CAPTURE_TRANSLATIONS_907_973 = {
    "15:907:0": "에서 간자를 붙잡아",
    "15:907:2": "이(가) 벌인",
    "15:907:3": "이(가) 밀명이었다니…\n하마터면 큰일 날 뻔했소",
}
RAW_TRANSLATIONS: dict[str, str] = {
    "15:896:0": "공성전을 생각하신다면 출병하기\n전에 써야 할 계책이",
    "15:896:1": "\n적 성의 방비에 약간 손을 써 두시지요…",
    "15:897:0": (
        "공성이야말로 군략의 요체… 다만\n"
        "적이 꺼리는 일은 미리\n"
        "적극적으로 해 두어야 할 줄 아옵니다"
    ),
    "15:898:0": "적 성을 공략하려면 지혜가 필요하다\n이럴 때는 경험 많은",
    "15:898:1": "의\n계책에 귀를 기울여",
    "15:898:2": "!",
    "15:899:0": (
        "공성은 무척 손이 많이 든다던데\n"
        "미리 성의 방비를 어느 정도\n"
        "약화해 둘 수는 없겠습니까?"
    ),
    "15:900:0": (
        "공성전에는 희생이 크다… 허나\n"
        "미리 적 성의 방비를 약화해\n"
        "둘 수 있다면…"
    ),
    "15:901:0": (
        "적 성의 방비를 조금 약화해 두면\n"
        "전투의 희생도 조금은\n"
        "줄지 않겠습니까?"
    ),
    "15:902:0": (
        "미리 적 영지의 성벽에\n"
        "모종의 공작을 벌여 두면\n"
        "쉽게 공략할 수 있을 것입니다"
    ),
    "15:903:0": "싸움에 잔꾀는 따르기 마련이지\n",
    "15:903:1": "의",
    "15:903:2": "에\n공작을 벌여 보자고",
    "15:904:0": "의",
    "15:904:1": (
        "공략에\n"
        "앞서 해야 할 일이 있습니다\n"
        "공작을 벌여 전력을 약화해야 할 듯하옵니다!"
    ),
    "15:905:0": "의",
    "15:905:1": (
        "\n정면으로 공격하는 것은 어리석은 계책\n"
        "먼저 공작으로 흔들어야 할 줄 아뢰옵니다"
    ),
    "15:906:0": "전투 전에 공작을 벌이시지요\n",
    "15:906:1": "의",
    "15:906:2": "의 힘을\n미리 약화해 두면 전투에 유리할 듯합니다",
    **CAPTURE_TRANSLATIONS_907_973,
}
RECORD_ARITIES = {
    896: 2,
    897: 1,
    898: 3,
    899: 1,
    900: 1,
    901: 1,
    902: 1,
    903: 3,
    904: 2,
    905: 2,
    906: 3,
    907: 4,
}
EXPECTED_JP = {
    896: (
        "攻城戦をお考えなら軍を出す前\nに為すべき策が",
        "\n敵城の防備にちと細工を…",
    ),
    897: (
        "城攻めこそ軍略の要…ただし\n"
        "敵の嫌がることはあらかじめ\n"
        "積極的に行うべきと存じます",
    ),
    898: (
        "敵城を攻めるには知恵がいる\nここは経験豊富な",
        "の\n策に耳を傾けて",
        "！",
    ),
    899: (
        "城攻めは大変手間がかかるとか\n"
        "あらかじめ城の防備をいくらか\n"
        "削いでおけませんか？",
    ),
    900: (
        "攻城戦には犠牲が多い…されど\n"
        "事前に敵城の防備を弱らせて\n"
        "おくことができるなら…",
    ),
    901: (
        "敵の城の防備を少し削いでおけ\n"
        "れば、戦の犠牲も少しは減るの\n"
        "ではありませんか？",
    ),
    902: (
        "あらかじめ敵領の城壁に\n"
        "何か細工を施しておけば\n"
        "容易に攻め込めましょう",
    ),
    903: (
        "戦に小細工は付き物よ\n",
        "の",
        "に\n工作を仕掛けようじゃねえか",
    ),
    904: (
        "の",
        "攻略に\n"
        "先立ち、やるべきことがあります\n"
        "工作を仕掛け戦力を削ぐべきかと！",
    ),
    905: (
        "の",
        "\n正面から攻めるは愚策\nまずは工作にて揺るがすべきかと",
    ),
    906: (
        "戦いの前に工作を致しましょう\n",
        "の",
        "の力を\n事前に削いでおけば戦に利するかと",
    ),
    907: (
        "にて間者を捕らえ",
        "\n",
        "による",
        "が密命とか…\n危ないところ",
    ),
}
EXPECTED_BASE_GAPS = {
    896: ("", "014352000000", "050505"),
    897: ("", "050505"),
    898: ("", "014301000000", "014342010000", "050505"),
    **{record_id: ("", "050505") for record_id in range(899, 903)},
    903: ("", "025032", "026432", "050505"),
    904: ("025032", "026432", "050505"),
    905: ("025032", "026432", "050505"),
    906: ("", "025032", "026432", "050505"),
    907: (
        "029632",
        "014314020000",
        "025032",
        "023c",
        "014344020000050505",
    ),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    907: (
        "029632",
        "01431a020000",
        "025032",
        "023c",
        "014350020000050505",
    ),
}
EXCLUDED_BLANK_COORDINATES = {"15:907:1"}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:896:1",
    "15:897:0",
    "15:900:0",
    "15:907:3",
}
SC_AUXILIARY = {
    905: (
        ("的", "，\n正面攻击实为下策，\n窃以为应当先行破坏，动摇其军心。"),
        ("025032", "026432", "050505"),
    ),
    906: (
        ("在战事前先行破坏吧。\n事先削减了", "的", "之力，\n理应对战事有利。"),
        ("", "025032", "026432", "050505"),
    ),
    907: (
        ("于", "捉到了间谍，\n据说是", "的", "之密令……\n真庆幸能事先阻止。"),
        ("", "029632", "025032", "023c", "050505"),
    ),
}
TC_AUXILIARY = {
    905: (
        ("的", "\n從正面進攻乃不智之舉，\n應先進行破壞工作加以撼動。"),
        ("025032", "026432", "050505"),
    ),
    906: (
        ("開戰前不妨先施以破壞工作。\n事先削弱", "的", "\n應有利於戰局。"),
        ("", "025032", "026432", "050505"),
    ),
    907: (
        ("於", "捉到了間諜，\n據說是", "的", "之密令……\n真慶幸能事先阻止。"),
        ("", "029632", "025032", "023c", "050505"),
    ),
}
EN_AUXILIARY = {
    905: (
        (
            "It is foolish to simply attack the ",
            "Ös ",
            ". We should try to shake things up through destabilization first.",
        ),
        ("", "025032", "026432", "050505"),
    ),
    906: (
        (
            "LetÖs try destabilization before battle. It would help if we could "
            "chip away at the ",
            "Ös power at ",
            " before the fighting starts.",
        ),
        ("", "025032", "026432", "050505"),
    ),
    907: (
        (
            "WeÖve captured spies in ",
            ". They had the ",
            "Ös ",
            " secret orders... That could have been bad.",
        ),
        ("", "029632", "025032", "023c", "050505"),
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
    "pristine_base_pc_jp_authoritative_siege_preparation_defense_weakening_"
    "proposals_and_spy_capture_result_with_uniform_plus_7_pk_jp_mapping_pc_"
    "sc_tc_and_pk_en_auxiliary_context_dynamic_faction_castle_officer_action_"
    "tokens_historical_speaker_register_current_layout_opcode_skeleton_lf_"
    "only_literal_excluded_and_isolated_reverse_overlay_runtime_pending"
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
    excluded_blank_literals: dict[str, str],
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
    COMMON.CORE.assert_context_mapping(
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
        expected_gaps = COMMON.CORE.COMMON.gaps_from_hex(base_gaps[record_id])
        if (
            COMMON.CORE.COMMON.record_gaps(source_record) != expected_gaps
            or COMMON.CORE.COMMON.record_gaps(current_record) != expected_gaps
        ):
            raise RuntimeError(
                f"segment {segment} Base dynamic skeleton drifted: 15:{record_id}"
            )
        for literal_id, (source_literal, current_literal) in enumerate(
            zip(source_literals, current_literals)
        ):
            coordinate = f"15:{record_id}:{literal_id}"
            if coordinate in excluded_blank_literals:
                expected_blank = excluded_blank_literals[coordinate]
                if (
                    source_literal.text != expected_blank
                    or current_literal.text != expected_blank
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
    expected_count = sum(record_arities.values()) - len(excluded_blank_literals)
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
        if COMMON.CORE.COMMON.layout_signature(
            translation
        ) != COMMON.CORE.COMMON.layout_signature(current_text):
            raise RuntimeError(
                f"segment {segment} layout/outer signature drifted: {coordinate}"
            )
        if "\r" in translation or ENGINE.KANA_OR_HAN_RE.search(translation):
            raise RuntimeError(
                f"segment {segment} forbidden script/control drifted: {coordinate}"
            )
        if COMMON.CORE.COMMON.BANNED_FULLWIDTH_PUNCTUATION.intersection(
            translation
        ):
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
    excluded_blank_literals: dict[str, str],
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
    translations = COMMON.CORE.COMMON.resolved_translations(
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
        excluded_blank_literals=excluded_blank_literals,
        semantic_assertions=semantic_assertions,
    )
    COMMON.CORE.COMMON.assert_isolated_overlay_roundtrip(
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
    if "15:907:1" in raw_translations or "15:907:1" in translations:
        raise RuntimeError("segment 851 LF-only blank received a decision")
    if COMMON.CORE.source_literals(
        source_records, 907
    ) != COMMON.CORE.source_literals(source_records, 973):
        raise RuntimeError("segment 851 907/973 exact source group drifted")
    for coordinate, expected in CAPTURE_TRANSLATIONS_907_973.items():
        if raw_translations[coordinate] != expected:
            raise RuntimeError(
                f"segment 851 907/973 capture canonical drifted: {coordinate}"
            )
    exact_expectations = {
        "15:896:0": "공성전을 생각하신다면 출병하기\n전에 써야 할 계책이",
        "15:897:0": (
            "공성이야말로 군략의 요체… 다만\n"
            "적이 꺼리는 일은 미리\n"
            "적극적으로 해 두어야 할 줄 아옵니다"
        ),
        "15:904:1": (
            "공략에\n"
            "앞서 해야 할 일이 있습니다\n"
            "공작을 벌여 전력을 약화해야 할 듯하옵니다!"
        ),
    }
    for coordinate, expected in exact_expectations.items():
        if raw_translations[coordinate] != expected:
            raise RuntimeError(
                f"segment 851 audited canonical drifted: {coordinate}"
            )
    for coordinate in ("15:903:2", "15:904:1", "15:905:1", "15:906:0"):
        if "공작" not in translations[coordinate]:
            raise RuntimeError(
                f"segment 851 defense-weakening 工作 terminology drifted: {coordinate}"
            )
    joined = "\n".join(translations.values())
    for required in ("공성", "공성전", "성벽", "방비", "간자", "공작"):
        if required not in joined:
            raise RuntimeError(
                f"segment 851 siege/sabotage terminology drifted: {required}"
            )
    if any(term in joined for term in ("성 공격전", "수성", "닌자", "방어력")):
        raise RuntimeError("segment 851 retained forbidden legacy terminology")


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
        excluded_blank_literals={"15:907:1": "\n"},
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 851 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S851",
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
