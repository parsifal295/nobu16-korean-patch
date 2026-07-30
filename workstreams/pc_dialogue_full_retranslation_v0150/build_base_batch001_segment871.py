#!/usr/bin/env python3
"""Build Base authoring segment 871 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment870 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S871.private.v1.jsonl"
SEGMENT = 871
ROAD_1143 = (
    "을(를) 가도로 이어야 하오\n"
    "길은 병력을 움직이는 요체\n"
    "길을 장악하는 자가 전쟁을 지배하는 법이오"
)
ROAD_1144 = (
    "(으)로 통하는 새 길을 모색하겠습니다\n"
    "침공로가 많을수록\n"
    "다양한 전략에 대응할 수 있습니다"
)
ROAD_1145 = (
    "(으)로 통하는 길을 개척한다\n"
    "진군로는 많을수록 좋은 법이지"
)
ROAD_1146 = (
    "(으)로 통하는 새 길을 열도록 하지요\n"
    "선택할 수 있는 길이 많을수록\n"
    "세울 수 있는 계책도 많아집니다"
)
ROAD_1147 = (
    "은(는) 교통의 요지입니다\n"
    "새 가도를 정비하면\n"
    "전략의 폭도 넓어질 것이옵니다"
)
PAIR_CANONICALS = {
    1136: COMMON.ROAD_1136,
    1137: COMMON.ROAD_1137,
    1138: COMMON.ROAD_1138,
    1139: COMMON.ROAD_1139,
    1140: COMMON.ROAD_1140,
    1141: COMMON.ROAD_1141,
    1142: COMMON.ROAD_1142,
    1143: ROAD_1143,
    1144: ROAD_1144,
    1145: ROAD_1145,
    1146: ROAD_1146,
    1147: ROAD_1147,
}
RAW_TRANSLATIONS: dict[str, str] = {
    **{
        f"15:{record_id}:0": translation
        for record_id, translation in (
            (1143, ROAD_1143),
            (1144, ROAD_1144),
            (1145, ROAD_1145),
            (1146, ROAD_1146),
            (1147, ROAD_1147),
        )
    },
    **{
        f"15:{left + 12}:0": translation
        for left, translation in PAIR_CANONICALS.items()
    },
    "15:1160:0": "(으)로 통하는 군도를 부설하",
    "15:1160:1": "\n이 새 길을 이용하면\n여러 방면에서 공격해 들어갈 수도 있",
}
RECORD_ARITIES = {
    **{record_id: 1 for record_id in range(1143, 1160)},
    1160: 2,
}
EXPECTED_BASE_JP = {
    1143: (
        "を街道にて結ばれるべし\n"
        "道は兵を動かす要じゃ\n"
        "道を制する者が戦を制しまするぞ",
    ),
    1144: (
        "への新たな経路を模索します\n"
        "侵攻路が多ければ\n"
        "様々な戦略に対応できます",
    ),
    1145: ("への経路を開拓する\n進軍路は多いに越したことあるまい",),
    1146: (
        "への新たな経路を開きましょう\n"
        "選択できる道が多いほど\n"
        "立てられる策も多くなりますよ",
    ),
    1147: (
        "は交通の要所です\n"
        "新たな街道を整備すれば\n"
        "戦略の幅も広がりますぞ",
    ),
    1148: COMMON.EXPECTED_BASE_JP[1136],
    1149: COMMON.EXPECTED_BASE_JP[1137],
    1150: COMMON.EXPECTED_BASE_JP[1138],
    1151: COMMON.EXPECTED_BASE_JP[1139],
    1152: COMMON.EXPECTED_BASE_JP[1140],
    1153: COMMON.EXPECTED_BASE_JP[1141],
    1154: COMMON.EXPECTED_BASE_JP[1142],
    1155: (
        "を街道にて結ばれるべし\n"
        "道は兵を動かす要じゃ\n"
        "道を制する者が戦を制しまするぞ",
    ),
    1156: (
        "への新たな経路を模索します\n"
        "侵攻路が多ければ\n"
        "様々な戦略に対応できます",
    ),
    1157: ("への経路を開拓する\n進軍路は多いに越したことあるまい",),
    1158: (
        "への新たな経路を開きましょう\n"
        "選択できる道が多いほど\n"
        "立てられる策も多くなりますよ",
    ),
    1159: (
        "は交通の要所です\n"
        "新たな街道を整備すれば\n"
        "戦略の幅も広がりますぞ",
    ),
    1160: (
        "へ通ずる軍道を敷設いたし",
        "\nこの新しい道を用いることで\n多方から攻め入ることも叶",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    **{record_id: ("029632", "050505") for record_id in range(1143, 1160)},
    1160: ("026532", "014314020000", "0143ca000000050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1160: ("026532", "01431a020000", "0143ca000000050505"),
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
AUXILIARY_OVERRIDES = {
    **{
        (side, "SC", 1144): (
            ("将摸索通往", "的新路线。\n进攻路线越多，\n可采用的战略就越丰富。"),
            ("", "029632", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1144): (
            ("通往", "的新路徑有待開闢。\n進攻路線越多，\n越能以多樣化戰略來因應。"),
            ("", "029632", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "SC", 1160): (
            ("已经铺设好通往", "的军道了。\n利用这条新道，\n便能实现从多个方向进攻。"),
            ("", "026532", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1160): (
            ("已經鋪設通往", "的軍道了。\n利用這條新道，\n應能從多個方向進攻吧。"),
            ("", "026532", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1160): (
        (
            "We have constructed military roads leading up to ",
            ". New avenues of attack will open up to us if we use it.",
        ),
        ("", "026532", "050505"),
    ),
}
BASIS = (
    "review_queue_base_msggame_B105_pristine_base_pc_jp_authoritative_road_"
    "proposal_speaker_pairs_and_military_road_completion_with_uniform_plus_8_"
    "pk_mapping_explicit_base_pk_jp_arrays_base_pk_sc_tc_exact_pk_en_context_"
    "twelve_exact_1136_1148_through_1147_1159_translation_pairs_project_"
    "kaido_military_road_transport_hub_and_invasion_route_terminology_1160_"
    "two_live_conjugation_stems_current_layout_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for left, canonical in PAIR_CANONICALS.items():
        right = left + 12
        if COMMON.COMMON.CORE.source_literals(
            source_records, left
        ) != COMMON.COMMON.CORE.source_literals(source_records, right):
            raise RuntimeError(
                f"segment 871 exact road-proposal source pair drifted: {left}/{right}"
            )
        left_translation = (
            COMMON.RAW_TRANSLATIONS[f"15:{left}:0"]
            if left <= 1142
            else raw_translations[f"15:{left}:0"]
        )
        if left_translation != canonical or raw_translations[
            f"15:{right}:0"
        ] != canonical:
            raise RuntimeError(
                f"segment 871 exact road-proposal translation pair drifted: "
                f"{left}/{right}"
            )
    opcode_stems = {
        "15:1160:0": "(으)로 통하는 군도를 부설하",
        "15:1160:1": "\n이 새 길을 이용하면\n여러 방면에서 공격해 들어갈 수도 있",
    }
    for coordinate, expected in opcode_stems.items():
        if raw_translations[coordinate] != expected:
            raise RuntimeError(f"segment 871 1160 opcode stem drifted: {coordinate}")
        if raw_translations[coordinate].endswith(
            ("다", "요", "오", "니다", "습니다", "사옵니다")
        ):
            raise RuntimeError(
                f"segment 871 completed verb precedes 1160 live opcode: {coordinate}"
            )
    joined = "\n".join(translations.values())
    for required in ("가도", "군도", "교통의 요지", "침공로", "진군로", "병력"):
        if required not in joined:
            raise RuntimeError(f"segment 871 road terminology drifted: {required}")
    if any(
        term in joined
        for term in ("당가", "본가", "진공로", "침공 루트", "군용 도로")
    ):
        raise RuntimeError("segment 871 retained forbidden road terminology")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.COMMON.build_segment_rows(
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
        raise RuntimeError("segment 871 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S871",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "exact_road_proposal_pairs": len(PAIR_CANONICALS),
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
