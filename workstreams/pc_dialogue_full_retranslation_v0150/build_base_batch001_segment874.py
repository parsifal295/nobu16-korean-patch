#!/usr/bin/env python3
"""Build Base authoring segment 874 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment863 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S874.private.v1.jsonl"
SEGMENT = 874
POLITE_SUGAR_REPORT = (
    "은(는) 우리 가문에 감사하고 있습니다\n"
    "설탕은 여러모로 요긴하게 쓰입니다만\n"
)
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1194:0": (
        "의 녀석들에게서 감사 서신이 왔다\n"
        "참 쉬운 놈들이군, 잘만 이용하면\n"
        "단것만으로도 성을 함락시킬 수 있겠어"
    ),
    "15:1195:0": (
        "은(는) 우리 가문에 은의를 느끼고 있사옵니다\n"
        "다른 가문의 평가가 이토록 오르다니…\n"
        "단것이란 참으로 무서운 물건이옵니다"
    ),
    "15:1196:0": (
        "은(는) 우리 가문에 감사하는 모양이옵니다\n"
        "이국 과자는 맛도 모양도 강렬하오니\n"
        "한동안 잊지 못할 것이옵니다"
    ),
    "15:1197:0": (
        POLITE_SUGAR_REPORT
        + "이런 쓰임새도 있는 것이군요"
    ),
    "15:1198:0": (
        "은(는) 단것을 고마워하는 모양\n"
        "코… 콘페… 콘페이토?는\n"
        "피로에 효험이 있으니 말이오"
    ),
    "15:1199:0": (
        "와(과)의 관계는 좋아지고 있사옵니다\n"
        "단것은 한번 입에 대면 또 먹고 싶어지는 법…\n"
        "그 매력을 뿌리치지 못한 모양이옵니다…"
    ),
    "15:1200:0": (
        "은(는), 우리 가문에 감사하고 있사옵니다\n"
        "허나… 언젠가는 이 설탕으로\n"
        "이 나라 고유의 섬세한 과자를 완성하고 싶사옵니다"
    ),
    "15:1201:0": (
        "은(는) 단것을 고마워하는 모양이오\n"
        "단것 앞에서는 하나같이 무른 자들이구려"
    ),
    "15:1202:0": (
        "은(는) 단것을 받고 기뻐하는 모양입니다\n"
        "단맛에 적대심까지 녹아 버렸군요"
    ),
    "15:1203:0": (
        "은(는) 단것에 만족한 듯하군\n"
        "…남은 것이 있다면"
    ),
    "15:1203:1": "에게도\n나눠 주었으면 한다만…",
    "15:1204:0": (
        "은(는) 단것을 받고 기뻐하는 모양입니다\n"
        "선물에는 역시 단것\n"
        "예나 지금이나 변함없군요"
    ),
    "15:1205:0": (
        POLITE_SUGAR_REPORT
        + "이런 쓰임새도 있는 것이구려"
    ),
    "15:1206:0": "이번",
    "15:1206:1": "이(가) 주효하여\n",
    "15:1206:2": (
        "의 우리 가문에 대한 인상이\n"
        "이전보다 좋아졌다고 하옵니다"
    ),
    "15:1207:0": "공물로 인해,",
    "15:1207:1": "와(과)의 우호도가 상승",
    "15:1208:0": "의 신용 ",
    "15:1208:1": "→",
}
RECORD_ARITIES = {
    **{record_id: 1 for record_id in range(1194, 1206)},
    1203: 2,
    1206: 3,
    1207: 2,
    1208: 2,
}
EXPECTED_JP = {
    1194: (
        "の連中から感謝の文が届いたぞ\n"
        "ちょろいもんだぜ、うまく使えば\n"
        "甘味だけで城を落とせるかもな",
    ),
    1195: (
        "は当家に恩義を感じております\n"
        "こうも他家からの評価が上がるとは…\n"
        "甘味とは恐ろしき代物にござるな",
    ),
    1196: (
        "は当家に感謝しておる様子\n"
        "異国の甘味は味も見た目も強烈ゆえ\n"
        "しばらくは忘れられぬはずですぞ",
    ),
    1197: (
        "は当家に感謝しています\n"
        "砂糖は様々なものに重宝しますが\n"
        "こういう使い道もあるのですね",
    ),
    1198: (
        "は甘味をありがたがっておる様子\n"
        "こっ…こんふぇ…こんぺいと？は\n"
        "疲れに効きますからなあ",
    ),
    1199: (
        "との関係は良くなっております\n"
        "甘味は一度口にすると、また食いたくなる…\n"
        "その魅力には抗えなかったようですなあ…",
    ),
    1200: (
        "は、当家に感謝してございます\n"
        "しかし…いずれはこの砂糖にて\n"
        "日の本独自の繊細な菓子を完成させたきもの",
    ),
    1201: (
        "は甘味をありがたがっておる様子\n"
        "甘き者ばかりでござるのう",
    ),
    1202: (
        "は甘味に喜んでいるようです\n"
        "甘さに敵対心も溶けてしまいましたね",
    ),
    1203: (
        "は甘味に満足したようだ\n…余っていたら",
        "にも\n分けてほしいものだが…",
    ),
    1204: (
        "は甘味に喜んでいるようです\n"
        "贈り物には甘味\n"
        "いつの時代も変わりませんね",
    ),
    1205: (
        "は当家に感謝しています\n"
        "砂糖は様々なものに重宝しますが\n"
        "こういう使い道もあるのですなあ",
    ),
    1206: (
        "此度の",
        "が奏功し\n",
        "の当家への心証が\n以前より良くなったとのこと",
    ),
    1207: ("貢物により、", "との友好度が上昇"),
    1208: ("の信用 ", "→"),
}
EXPECTED_BASE_GAPS = {
    **{
        record_id: ("025032", "050505")
        for record_id in range(1194, 1206)
    },
    1203: ("025032", "014301000000", "050505"),
    1206: ("", "023c", "025032", "050505"),
    1207: ("", "025032", "050505"),
    1208: ("025032", "0232", "0233050505"),
}
EXPECTED_PK_JP_GAPS = EXPECTED_BASE_GAPS
CURRENT_ELLIPSIS_COORDINATES = {
    "15:1195:0",
    "15:1198:0",
    "15:1199:0",
    "15:1200:0",
    "15:1203:0",
    "15:1203:1",
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
AUXILIARY_OVERRIDES = {
    **{
        (side, "SC", 1206): (
            (
                "据说这次的",
                "奏功，\n",
                "对主家的印象\n变得比以前更好了。",
            ),
            ("", "023c", "025032", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1206): (
            (
                "據說這次的",
                "奏功，\n",
                "對主家的印象\n變得比以前更好了。",
            ),
            ("", "023c", "025032", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1206): (
        (
            "Due to the success of ",
            ", the ",
            "Ös opinion of our clan is better than ever before.",
        ),
        ("", "023c", "025032", "050505"),
    ),
    **{
        (side, "SC", 1208): (
            ("的信用由", "→", "。"),
            ("025032", "0232", "0233", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1208): (
            ("的信用 ", "→", "。"),
            ("025032", "0232", "0233", "050505"),
        )
        for side in ("base", "pk")
    },
}
BASIS = (
    "review_queue_base_msggame_B105_pristine_base_pc_jp_authoritative_"
    "nanban_sweets_and_sugar_gift_reports_with_uniform_plus_8_pk_jp_sc_tc_"
    "exact_mapping_pk_en_auxiliary_context_dynamic_house_action_officer_"
    "tokens_historical_speaker_register_confeito_etymology_and_1569_frois_"
    "nobunaga_gift_context_distinct_1197_1205_endings_project_impression_"
    "tribute_friendship_and_credit_terminology_current_layout_runtime_"
    "fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if "코…… 콘페…… 콘페이토?" not in translations["15:1198:0"]:
        raise RuntimeError("segment 874 historical confeito hesitation drifted")
    if raw_translations["15:1197:0"].endswith("것이구려"):
        raise RuntimeError("segment 874 1197 polite ending collapsed into 1205")
    if not raw_translations["15:1197:0"].endswith("것이군요"):
        raise RuntimeError("segment 874 1197 polite ending drifted")
    if not raw_translations["15:1205:0"].endswith("것이구려"):
        raise RuntimeError("segment 874 1205 historical ending drifted")
    if not raw_translations["15:1200:0"].startswith(
        "은(는), 우리 가문에 감사하고 있사옵니다\n"
    ):
        raise RuntimeError("segment 874 1200 comma or house terminology drifted")
    if "이 나라 고유의" not in raw_translations["15:1200:0"]:
        raise RuntimeError("segment 874 1200 日の本 historical phrasing drifted")
    if not raw_translations["15:1201:0"].endswith(
        "단것 앞에서는 하나같이 무른 자들이구려"
    ):
        raise RuntimeError("segment 874 1201 甘き者 wordplay drifted")
    if raw_translations["15:1206:2"] != (
        "의 우리 가문에 대한 인상이\n이전보다 좋아졌다고 하옵니다"
    ):
        raise RuntimeError("segment 874 1206 心証 impression semantics drifted")

    joined = "\n".join(translations.values())
    for required in (
        "단것",
        "설탕",
        "이국 과자",
        "우리 가문",
        "인상",
        "공물",
        "신용",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 874 gift terminology drifted: {required}"
            )
    for forbidden in (
        "곤페이토",
        "심증",
        "조공품",
        "신뢰도",
        "당가",
        "일본 고유",
        "이 나라만의",
        "단것을 밝히",
        "와의",
    ):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 874 retained forbidden gift terminology: {forbidden}"
            )


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        expected_jp=EXPECTED_JP,
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
        raise RuntimeError("segment 874 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S874",
                "decision_count": len(rows),
                "retranslated": len(rows),
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
