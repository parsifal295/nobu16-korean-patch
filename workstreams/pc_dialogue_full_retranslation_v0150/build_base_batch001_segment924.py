#!/usr/bin/env python3
"""Build Base authoring segment 924 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment923 as COMMON_SEGMENT


COMMON = COMMON_SEGMENT.COMMON
ENGINE = COMMON_SEGMENT.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S924.private.v1.jsonl"
)
SEGMENT = 924
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1669:0": "우리 가문의 확장을 가로막는\n",
    "15:1669:1": "을(를) 공략 목표로 삼는 방안을\n",
    "15:1669:2": "검토하여",
    "15:1670:0": (
        "공략 목표를 가신단에 알리고\n"
        "힘을 집결시키면,"
    ),
    "15:1670:1": "도\n반드시 쳐부술 수 있소",
    "15:1671:0": (
        "을(를) 우리 가문의 공략 목표로 삼고\n"
        "각 성에서 군비를 갖추는 것이\n"
    ),
    "15:1671:1": "인가",
    "15:1672:0": "시간이 있다면\n꼭",
    "15:1672:1": "논공행상",
    "15:1672:2": "에",
    "15:1672:3": "모습을 보여 주시면\n승진한 이들도 기뻐",
    "15:1673:0": "논공행상",
    "15:1673:1": "은(는) 확인하",
    "15:1673:2": (
        "인가?\n"
        "승진한 인물들을 알아 두면\n"
        "전략에 도움이 되"
    ),
    "15:1674:0": "논공행상",
    "15:1674:1": "의 결과가\n새로 정리되",
    "15:1674:2": (
        "\n가신단의 동향을 살필 좋은 기회라 생각하옵니다"
    ),
    "15:1675:0": "논공행상",
    "15:1675:1": "의 결과가\n새로 정리되",
    "15:1675:2": "\n성을 맡길 만한 이도 성장해 오",
    "15:1676:0": "논공행상",
    "15:1676:1": "의 결과가\n새로 정리되",
    "15:1676:2": "\n영지를 늘려 줄 만한 이도",
}
RECORD_ARITIES = {
    1669: 3,
    1670: 2,
    1671: 2,
    1672: 4,
    1673: 3,
    1674: 3,
    1675: 3,
    1676: 3,
}
EXPECTED_BASE_JP = {
    1669: (
        "当家拡大の障壁となる\n",
        "を攻略目標とする旨\n",
        "検討して",
    ),
    1670: (
        "攻略目標を家中に示し\n力を集結させれば、",
        "とて\n必ずや打ち破れる",
    ),
    1671: (
        "を当家の攻略目標とし\n各城にて軍備を進めては\n",
        "か",
    ),
    1672: (
        "時間があれば\n是非",
        "論功行賞",
        "に",
        "顔出しを\n昇進した者らも喜",
    ),
    1673: (
        "論功行賞",
        "は確認し",
        "か？\n昇進した顔触れを知ることで\n戦略の助けともな",
    ),
    1674: (
        "論功行賞",
        "の結果が\n新たにまとめられ",
        "\n家中の様子を見る良い機会かと",
    ),
    1675: (
        "論功行賞",
        "の結果が\n新たにまとめられ",
        "\n城を任せられる者も育ってき",
    ),
    1676: (
        "論功行賞",
        "の結果が\n新たにまとめられ",
        "\n知行を増やせる者も",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1669: ("", "026432", "01438a040000", "014342010000050505"),
    1670: ("", "026432", "014356020000050505"),
    1671: ("026432", "0143b002000001435c020000", "050505"),
    1672: (
        "014384040000",
        "1b434d",
        "1b435a",
        "014384040000",
        "014370030000050505",
    ),
    1673: (
        "1b434d",
        "1b435a",
        "014314020000",
        "01435a040000050505",
    ),
    1674: ("1b434d", "1b435a", "014314020000", "050505"),
    1675: (
        "1b434d",
        "1b435a",
        "014314020000",
        "014314020000050505",
    ),
    1676: (
        "1b434d",
        "1b435a",
        "014314020000",
        "0143b2000000050505",
    ),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1669: ("", "026432", "014396040000", "014342010000050505"),
    1670: ("", "026432", "014362020000050505"),
    1671: ("026432", "0143bc020000014368020000", "050505"),
    1672: (
        "014390040000",
        "1b434d",
        "1b435a",
        "014390040000",
        "01437c030000050505",
    ),
    1673: (
        "1b434d",
        "1b435a",
        "01431a020000",
        "014366040000050505",
    ),
    1674: ("1b434d", "1b435a", "01431a020000", "050505"),
    1675: (
        "1b434d",
        "1b435a",
        "01431a020000",
        "01431a020000050505",
    ),
    1676: (
        "1b434d",
        "1b435a",
        "01431a020000",
        "0143b2000000050505",
    ),
}
PK_RECORD_MAP = {
    1669: 1699,
    1670: 1700,
    1671: 1701,
    1672: 1702,
    1673: 1703,
    1674: 1704,
    1675: 1705,
    1676: 1706,
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}

SHARED_AUXILIARY = {
    ("SC", 1669): (
        ("把妨碍本家扩张的", "\n作为攻略目标一事，\n请您多加考虑。"),
        ("", "026432", "050505"),
    ),
    ("TC", 1669): (
        ("將妨礙本家擴大的", "\n作為攻略目標一事，\n請您多加考慮。"),
        ("", "026432", "050505"),
    ),
    ("SC", 1670): (
        ("向家中明示攻略目标，\n若能集中力量的话，\n一定能击破", "吧。"),
        ("", "026432", "050505"),
    ),
    ("TC", 1670): (
        ("將攻略目標出示於臣下，\n使其集結力量的話，\n即使是", "也必定能擊破吧。"),
        ("", "026432", "050505"),
    ),
    ("SC", 1671): (
        ("将", "作为本家的攻略目标，\n于各城进行军备，如何？"),
        ("", "026432", "050505"),
    ),
    ("TC", 1671): (
        ("將", "作為本家的攻略目標，\n並於各城進行軍備如何？"),
        ("", "026432", "050505"),
    ),
    ("SC", 1672): (
        ("如果有时间，\n请务必要在", "论功行赏", "中露面，\n晋升的人也会很高兴。"),
        ("", "1b434d", "1b435a", "050505"),
    ),
    ("TC", 1672): (
        ("若有時間，\n務必當面", "論功行賞", "，\n想必晉升者也會備感欣慰。"),
        ("", "1b434d", "1b435a", "050505"),
    ),
    ("SC", 1673): (
        ("已经确定", "论功行赏", "了吗？\n与晋升者见面，\n有助于提升战略。"),
        ("", "1b434d", "1b435a", "050505"),
    ),
    ("TC", 1673): (
        ("論功行賞", "是否確認過了？\n熟悉一下晉升成員，\n對戰略應該也有幫助。"),
        ("1b434d", "1b435a", "050505"),
    ),
    ("SC", 1674): (
        ("论功行赏", "的结果\n已经重新统计完毕。\n这也是观察家中情况的好时机。"),
        ("1b434d", "1b435a", "050505"),
    ),
    ("TC", 1674): (
        ("論功行賞", "的結果\n已重新統整完畢，\n不妨趁此良機掌握家中情況。"),
        ("1b434d", "1b435a", "050505"),
    ),
    ("SC", 1675): (
        ("论功行赏", "的结果\n已完成总结，\n城的管理者也成长了。"),
        ("1b434d", "1b435a", "050505"),
    ),
    ("TC", 1675): (
        ("論功行賞", "的結果\n已重新統整完畢，\n也培育了能委任城池的人才。"),
        ("1b434d", "1b435a", "050505"),
    ),
    ("SC", 1676): (
        ("论功行赏", "的结果\n已完成总结，\n也有能增加知行的人。"),
        ("1b434d", "1b435a", "050505"),
    ),
    ("TC", 1676): (
        ("論功行賞", "的結果\n已重新統整完畢，\n也有能增加知行的人。"),
        ("1b434d", "1b435a", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1669: (
        (" stands in the way of our clanÖs expansion. We should attack it.",),
        ("026432", "050505"),
    ),
    1670: (
        (
            "If we inform the clan of our target and gather our forces, IÖm sure we can take down ",
            ".",
        ),
        ("", "026432", "050505"),
    ),
    1671: (
        (
            "Why donÖt we set ",
            " as our target and begin building up forces at our castles?",
        ),
        ("", "026432", "050505"),
    ),
    1672: (
        (
            "If you have the time, please make an appearance at the ",
            "honor commendation",
            ". Those who were promoted would be glad to see you.",
        ),
        ("", "1b434d", "1b435a", "050505"),
    ),
    1673: (
        (
            "Have you checked the ",
            "honor commendation",
            "? Knowing the people who were promoted could help our strategy.",
        ),
        ("", "1b434d", "1b435a", "050505"),
    ),
    1674: (
        (
            "The results of the ",
            "honor commendation",
            " have been compiled. ItÖd be a good way to check whatÖs happening in the clan.",
        ),
        ("", "1b434d", "1b435a", "050505"),
    ),
    1675: (
        (
            "The results of the ",
            "honor commendation",
            " have been compiled. Some of them should be ready to command a castle.",
        ),
        ("", "1b434d", "1b435a", "050505"),
    ),
    1676: (
        (
            "The results of the ",
            "honor commendation",
            " have been compiled. Some of them should be ready for increased dominion.",
        ),
        ("", "1b434d", "1b435a", "050505"),
    ),
}
AUXILIARY_OVERRIDES = {
    **{
        (side, language, record_id): expected
        for (language, record_id), expected in SHARED_AUXILIARY.items()
        for side in ("base", "pk")
    },
    **{
        ("pk", "EN", record_id): expected
        for record_id, expected in PK_EN_AUXILIARY.items()
    },
}
BASIS = (
    "review_queue_base_msggame_B111_B_pristine_base_pc_jp_authoritative_"
    "attack_target_and_honor_commemoration_advice_with_explicit_base1669_"
    "to1676_pk1699_to1706_plus30_mapping_exact_base_pk_sc_tc_and_pk_en_"
    "auxiliary_context_attack_target_retainer_body_honor_commemoration_"
    "promotion_fief_battle_preparation_glossary_runtime_tokens_colour_tags_"
    "speaker_voice_and_live_inflection_preserved"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    joined = "\n".join(translations.values())
    for required in (
        "우리 가문",
        "공략 목표",
        "가신단",
        "논공행상",
        "승진",
        "영지",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 924 required terminology drifted: {required}")
    for forbidden in (
        "당가",
        "가중",
        "지행",
        "영지를 늘릴 수 있는 이",
        "論功行賞",
        "。",
        "、",
        "！",
    ):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 924 retained forbidden terminology: {forbidden}"
            )
    for coordinate, ending in {
        "15:1669:2": "검토하여",
        "15:1670:1": "있소",
        "15:1672:3": "기뻐",
        "15:1673:1": "확인하",
        "15:1673:2": "되",
        "15:1674:1": "정리되",
        "15:1675:1": "정리되",
        "15:1675:2": "성장해 오",
        "15:1676:1": "정리되",
        "15:1676:2": "이도",
    }.items():
        if not raw_translations[coordinate].endswith(ending):
            raise RuntimeError(
                f"segment 924 live inflection stem drifted: {coordinate}"
            )
    if raw_translations["15:1674:2"] != (
        "\n가신단의 동향을 살필 좋은 기회라 생각하옵니다"
    ):
        raise RuntimeError("segment 924 家中 meaning drifted")
    if raw_translations["15:1676:2"] != "\n영지를 늘려 줄 만한 이도":
        raise RuntimeError("segment 924 知行 meaning drifted")
    if set(PK_RECORD_MAP.items()) != {
        (1669, 1699),
        (1670, 1700),
        (1671, 1701),
        (1672, 1702),
        (1673, 1703),
        (1674, 1704),
        (1675, 1705),
        (1676, 1706),
    }:
        raise RuntimeError("segment 924 explicit Base-to-PK mapping drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows_with_current_gaps(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        expected_base_jp=EXPECTED_BASE_JP,
        expected_pk_jp=EXPECTED_PK_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        current_gaps=EXPECTED_CURRENT_GAPS,
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
    if len(rows) != 23 or len(translations) != 23:
        raise RuntimeError("segment 924 fixed decision count drifted")
    if len(validated) != len(translations):
        raise RuntimeError("segment 924 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S924",
                "decision_count": len(rows),
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "explicit_plus30_pk_mapping": True,
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
