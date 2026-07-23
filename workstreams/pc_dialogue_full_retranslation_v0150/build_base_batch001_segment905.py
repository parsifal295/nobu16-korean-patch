#!/usr/bin/env python3
"""Build Base authoring segment 905 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment884 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S905.private.v1.jsonl"
)
SEGMENT = 905
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1486:0": "에서 민심이 불안해져",
    "15:1486:1": "\n잇키로 번질 위험도",
    "15:1486:2": "\n이럴 때는 백성을 위무하는 것이",
    "15:1487:0": "재해로 인해",
    "15:1487:1": "에서는\n불온한 움직임이",
    "15:1487:2": "\n잇키를 경계해야 할",
    "15:1488:0": "에서 재해로 인한 잇키 발생을 막음",
    "15:1489:0": "전방의",
    "15:1489:1": "에 쌀이 부족하다 하오니\n",
    "15:1489:2": (
        "에 비축분이 있사옵니다\n"
        "병량을 운반하는 것이"
    ),
    "15:1490:0": "에서",
    "15:1490:1": "(으)로 병량",
    "15:1490:2": "을 이송",
    "15:1491:0": "전방의",
    "15:1491:1": "에서 병력이 부족하다 하오니\n",
    "15:1491:2": (
        "의 병사들은 사기가 높으니\n"
        "부디 보충에 투입해 주시기를 바라옵니다"
    ),
    "15:1492:0": "에서",
    "15:1492:1": "(으)로 병력",
    "15:1492:2": "을 이송",
}
RECORD_ARITIES = {
    1486: 3,
    1487: 3,
    1488: 1,
    1489: 3,
    1490: 3,
    1491: 3,
    1492: 3,
}
EXPECTED_BASE_JP = {
    1486: (
        "で民に不安が広がって",
        "\n一揆に発展する危険も",
        "\nここは慰撫しては",
    ),
    1487: (
        "災害によって",
        "では\n不穏な動きが",
        "\n一揆への警戒を行うべき",
    ),
    1488: ("で災害による一揆の発生を回避",),
    1489: (
        "前方の",
        "で米が足らぬとか\n",
        "に備蓄がありますゆえ\n兵糧を運んでは",
    ),
    1490: ("から", "へ兵糧", "を移送"),
    1491: (
        "前方の",
        "で兵が足らぬとか\n",
        "の兵は意気軒昂\nぜひ補填に使っていただきたく",
    ),
    1492: ("から", "へ兵", "を移送"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1486: (
        "026434",
        "0143B2000000",
        "014352000000",
        "0143B0020000014324010000050505",
    ),
    1487: (
        "",
        "026434",
        "014378010000",
        "014320020000050505",
    ),
    1488: ("026432", "050505"),
    1489: (
        "",
        "026432",
        "026532",
        "0143B0020000014324010000050505",
    ),
    1490: ("026532", "026432", "0232", "050505"),
    1491: ("", "026432", "026532", "050505"),
    1492: ("026532", "026432", "0232", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1486: (
        "026434",
        "0143B2000000",
        "014352000000",
        "0143BC020000014324010000050505",
    ),
    1487: (
        "",
        "026434",
        "014378010000",
        "01432C020000050505",
    ),
    1489: (
        "",
        "026432",
        "026532",
        "0143BC020000014324010000050505",
    ),
}
PK_RECORD_MAP = {
    record_id: record_id + 15 for record_id in RECORD_ARITIES
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}


def make_auxiliary_overrides(
    shared: dict[
        tuple[str, int], tuple[tuple[str, ...], tuple[str, ...]]
    ],
    pk_en: dict[int, tuple[tuple[str, ...], tuple[str, ...]]],
) -> dict[
    tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
]:
    return {
        **{
            (side, language, record_id): expected
            for (language, record_id), expected in shared.items()
            for side in ("base", "pk")
        },
        **{
            ("pk", "EN", record_id): expected
            for record_id, expected in pk_en.items()
        },
    }


SHARED_AUXILIARY = {
    ("SC", 1486): (
        (
            "中民心动摇正在扩大。\n"
            "恐有发生暴动的危险。\n"
            "建议此时以安抚人心为重。",
        ),
        ("026434", "050505"),
    ),
    ("TC", 1486): (
        (
            "中民心動搖。\n"
            "恐有發生一揆的危險。\n"
            "建議此時以安撫人心為重。",
        ),
        ("026434", "050505"),
    ),
    ("SC", 1487): (
        ("因灾害导致形势动荡。\n务必对暴动提高警戒。",),
        ("026434", "050505"),
    ),
    ("TC", 1487): (
        ("因災害\n導致情勢動盪。\n務必對一揆提高警戒。",),
        ("026434", "050505"),
    ),
    ("SC", 1488): (
        ("成功避免", "因灾害导致的一揆"),
        ("", "026432", "050505"),
    ),
    ("TC", 1488): (
        ("成功避免", "因災害導致的一揆"),
        ("", "026432", "050505"),
    ),
    ("SC", 1489): (
        ("的军粮不足，\n从后方的", "\n开始运送军粮如何？"),
        ("026432", "026532", "050505"),
    ),
    ("TC", 1489): (
        ("的軍糧不足，\n從後方的", "\n運送軍糧如何？"),
        ("026432", "026532", "050505"),
    ),
    ("SC", 1490): (
        ("从", "向", "运送军粮", "。"),
        ("", "026532", "026432", "0232", "050505"),
    ),
    ("TC", 1490): (
        ("從", "運輸軍糧", "至", "。"),
        ("", "026532", "0232", "026432", "050505"),
    ),
    ("SC", 1491): (
        ("的兵力消耗很大。\n从后方的", "\n补充兵力如何？"),
        ("026432", "026532", "050505"),
    ),
    ("TC", 1491): (
        ("的兵力嚴重消耗。\n從後方的", "\n補充兵力如何？"),
        ("026432", "026532", "050505"),
    ),
    ("SC", 1492): (
        ("从", "向", "运送兵卒", "。"),
        ("", "026532", "026432", "0232", "050505"),
    ),
    ("TC", 1492): (
        ("從", "派兵", "至", "。"),
        ("", "026532", "0232", "026432", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1486: (
        (
            "The people of ",
            " are growing restless. If things continue this way, we may "
            "have a revolt on our hands. I suggest we pacify them.",
        ),
        ("", "026434", "050505"),
    ),
    1487: (
        (
            "The disasters have left the people of ",
            " restless. We should be watchful for signs of a revolt.",
        ),
        ("", "026434", "050505"),
    ),
    1488: (
        ("A disaster-related revolt at ", " was avoided."),
        ("", "026432", "050505"),
    ),
    1489: (
        (
            "ThereÖs a shortage of rice at ",
            ", but we still have plenty at ",
            ". I suggest we transport some over.",
        ),
        ("", "026432", "026532", "050505"),
    ),
    1490: (
        (" supplies were transported from ", " to ", "."),
        ("0232", "026532", "026432", "050505"),
    ),
    1491: (
        (
            "ThereÖs a shortage of soldiers at ",
            ". The soldiers at ",
            " are motivated and in high spirits, so perhaps we should "
            "send some over.",
        ),
        ("", "026432", "026532", "050505"),
    ),
    1492: (
        (" soldiers were transported from ", " to ", "."),
        ("0232", "026532", "026432", "050505"),
    ),
}
AUXILIARY_OVERRIDES = make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B109_pristine_base_pc_jp_authoritative_"
    "disaster_revolt_pacification_rations_and_troop_transfer_proposals_"
    "and_results_with_uniform_plus_15_pk_mapping_exact_base_pk_jp_sc_tc_"
    "and_actual_pk_en_auxiliary_context_慰撫_as_위무_一揆_as_잇키_兵糧_as_"
    "병량_兵_as_contextual_병력_or_병사_補填_as_보충_dynamic_source_and_"
    "destination_castle_quantity_tokens_live_inflection_stems_current_line_"
    "counts_and_opcode_skeleton_preserved_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    transfer_expectations = {
        1490: ("에서", "(으)로 병량", "을 이송"),
        1492: ("에서", "(으)로 병력", "을 이송"),
    }
    for record_id, expected in transfer_expectations.items():
        actual = tuple(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(3)
        )
        if actual != expected:
            raise RuntimeError(
                f"segment 905 transfer token order drifted: {record_id}"
            )
    joined = "\n".join(translations.values())
    for required in (
        "위무",
        "잇키",
        "민심",
        "병량",
        "병력",
        "병사",
        "보충",
        "비축분",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 905 meaning or terminology drifted: {required}"
            )
    for forbidden in ("폭동", "군량", "보전", "당가"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 905 forbidden terminology retained: {forbidden}"
            )
    stem_expectations = {
        "15:1486:0": "불안해져",
        "15:1486:1": "위험도",
        "15:1486:2": "것이",
        "15:1487:1": "움직임이",
        "15:1487:2": "해야 할",
        "15:1489:2": "것이",
    }
    for coordinate, ending in stem_expectations.items():
        if not raw_translations[coordinate].endswith(ending):
            raise RuntimeError(
                f"segment 905 live inflection stem drifted: {coordinate}"
            )
    if len(raw_translations) != 19:
        raise RuntimeError("segment 905 visible decision count drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
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
        raise RuntimeError("segment 905 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S905",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "base_to_pk_offset": 15,
                "disaster_revolt_pacification_records": 3,
                "rations_troop_transfer_records": 4,
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
