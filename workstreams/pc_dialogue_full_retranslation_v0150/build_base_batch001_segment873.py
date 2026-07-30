#!/usr/bin/env python3
"""Build Base authoring segment 873 decisions for the v0.15.0 retranslation."""

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
CORE = COMMON.CORE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S873.private.v1.jsonl"
SEGMENT = 873
ROAD_OPEN_PAIR = ("·", "와(과)", "사이에 가도가 개통")
ROAD_LINK_PAIR = ("부터", "(으)로 이어지는 가도가 개통")
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1185:0": ROAD_OPEN_PAIR[0],
    "15:1185:1": ROAD_OPEN_PAIR[1],
    "15:1185:2": ROAD_OPEN_PAIR[2],
    "15:1186:0": ROAD_OPEN_PAIR[0],
    "15:1186:1": ROAD_OPEN_PAIR[1],
    "15:1186:2": ROAD_OPEN_PAIR[2],
    "15:1187:0": "·",
    "15:1187:1": "사이로 군세가 통행 가능",
    "15:1188:0": ROAD_LINK_PAIR[0],
    "15:1188:1": ROAD_LINK_PAIR[1],
    "15:1189:0": ROAD_LINK_PAIR[0],
    "15:1189:1": ROAD_LINK_PAIR[1],
    "15:1190:0": "와(과)의 관계를\n개선할 좋은 방도가",
    "15:1190:1": "\n금전을 조금 맡겨",
    "15:1191:0": "금전을 써서\n",
    "15:1191:1": "와(과) 우리 가문의 관계를\n개선해 나가",
    "15:1192:0": "와(과)의 관계 개선은\n",
    "15:1192:1": "에",
    "15:1192:2": "\n금전에 걸맞은 성과를 보이",
    "15:1193:0": "와(과)의 우호도 ",
    "15:1193:1": "→",
}
RECORD_ARITIES = {
    1185: 3,
    1186: 3,
    1187: 2,
    1188: 2,
    1189: 2,
    1190: 2,
    1191: 2,
    1192: 3,
    1193: 2,
}
EXPECTED_JP = {
    1185: ("・", "と", "の間に街道が開通"),
    1186: ("・", "と", "の間に街道が開通"),
    1187: ("・", "間を軍勢が通行可能に"),
    1188: ("から", "へと繋がる街道が開通"),
    1189: ("から", "へと繋がる街道が開通"),
    1190: (
        "との関係を\n改善する良き一手が",
        "\n金銭を少々、預けて",
    ),
    1191: (
        "金銭を用いて\n",
        "と当家の関係を\n改善して参",
    ),
    1192: (
        "との関係改善は\n",
        "に",
        "\n金銭に見合う成果を示",
    ),
    1193: ("との友好度 ", "→"),
}
EXPECTED_BASE_GAPS = {
    1185: ("", "029632", "029732", "050505"),
    1186: ("", "029632", "029732", "050505"),
    1187: ("029632", "029732", "050505"),
    1188: ("029632", "029732", "050505"),
    1189: ("029632", "029732", "050505"),
    1190: ("025032", "014352000000", "014342010000050505"),
    1191: ("", "025032", "01435a040000050505"),
    1192: (
        "025032",
        "014301000000",
        "01437c030000",
        "01437e040000050505",
    ),
    1193: ("025032", "023c", "023d050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1191: ("", "025032", "014366040000050505"),
    1192: (
        "025032",
        "014301000000",
        "014388030000",
        "01438a040000050505",
    ),
}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
AUXILIARY_OVERRIDES = {
    **{
        (side, "SC", 1187): (
            ("军队可通行于", "与", "之间。"),
            ("", "029632", "029732", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1187): (
            ("軍隊可通行於", "與", "之間。"),
            ("", "029632", "029732", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1187): (
        ("Armies can now pass between ", " and ", "."),
        ("", "029632", "029732", "050505"),
    ),
    **{
        (side, "SC", 1190): (
            ("有个改善和", "的关系的好方法。\n先给点儿钱吧。"),
            ("", "025032", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1190): (
            ("有個改善和", "的關係的好方法。\n請先寄放點兒錢吧。"),
            ("", "025032", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1190): (
        (
            "I know a way we can improve relations with the ",
            ". ItÖll just take a little bit of gold.",
        ),
        ("", "025032", "050505"),
    ),
    **{
        (side, "SC", 1191): (
            ("拿钱来改善\n", "与本家的关系吧。"),
            ("", "025032", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1191): (
            ("拿錢來改善\n", "與本家的關係吧。"),
            ("", "025032", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1191): (
        (
            "We could improve our clanÖs relationship with the ",
            " with some gold.",
        ),
        ("", "025032", "050505"),
    ),
    **{
        (side, "SC", 1192): (
            (
                "要改善和",
                "的关系，\n就让",
                "来吧。\n会拿出和钱相对的成果的。",
            ),
            ("", "025032", "014301000000", "050505"),
        )
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 1192): (
            (
                "要改善和",
                "的關係，\n就讓",
                "來吧。\n會拿出和錢相對的成果的。",
            ),
            ("", "025032", "014301000000", "050505"),
        )
        for side in ("base", "pk")
    },
    ("pk", "EN", 1192): (
        (
            "Leave improving our relationship with ",
            " to me. The results will be worth the gold.",
        ),
        ("", "025032", "050505"),
    ),
}
BASIS = (
    "review_queue_base_msggame_B105_pristine_base_pc_jp_authoritative_"
    "road_connection_ui_and_gold_relationship_improvement_proposals_with_"
    "uniform_plus_8_pk_jp_sc_tc_exact_mapping_pk_en_auxiliary_context_exact_"
    "duplicate_source_pairs_dynamic_house_officer_and_speaker_inflection_"
    "tokens_project_kaido_gold_and_friendship_terminology_current_layout_"
    "runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for left_record_id, right_record_id in ((1185, 1186), (1188, 1189)):
        if CORE.source_literals(
            source_records, left_record_id
        ) != CORE.source_literals(source_records, right_record_id):
            raise RuntimeError(
                "segment 873 exact source pair drifted: "
                f"{left_record_id}/{right_record_id}"
            )
        left = tuple(
            raw_translations[f"15:{left_record_id}:{literal_id}"]
            for literal_id in range(RECORD_ARITIES[left_record_id])
        )
        right = tuple(
            raw_translations[f"15:{right_record_id}:{literal_id}"]
            for literal_id in range(RECORD_ARITIES[right_record_id])
        )
        left_resolved = tuple(
            translations[f"15:{left_record_id}:{literal_id}"]
            for literal_id in range(RECORD_ARITIES[left_record_id])
        )
        right_resolved = tuple(
            translations[f"15:{right_record_id}:{literal_id}"]
            for literal_id in range(RECORD_ARITIES[right_record_id])
        )
        if left != right or left_resolved != right_resolved:
            raise RuntimeError(
                "segment 873 exact translation pair drifted: "
                f"{left_record_id}/{right_record_id}"
            )

    for record_id in (1185, 1186):
        if tuple(
            raw_translations[f"15:{record_id}:{literal_id}"]
            for literal_id in range(3)
        ) != ROAD_OPEN_PAIR:
            raise RuntimeError(
                f"segment 873 road-opening particle canonical drifted: {record_id}"
            )
    if not raw_translations["15:1190:0"].endswith("방도가"):
        raise RuntimeError("segment 873 1190 first dynamic inflection drifted")
    if not raw_translations["15:1190:1"].endswith("맡겨"):
        raise RuntimeError("segment 873 1190 second dynamic stem drifted")
    if not raw_translations["15:1191:1"].endswith("나가"):
        raise RuntimeError("segment 873 1191 dynamic stem drifted")
    if not raw_translations["15:1192:2"].endswith("보이"):
        raise RuntimeError("segment 873 1192 dynamic stem drifted")
    if raw_translations["15:1192:1"] != "에":
        raise RuntimeError(
            "segment 873 1192 postposition before live 0143 fragment drifted"
        )
    for coordinate in ("15:1190:0", "15:1190:1", "15:1191:1", "15:1192:2"):
        if raw_translations[coordinate].endswith(
            ("다", "요", "오", "옵니다", "습니다")
        ):
            raise RuntimeError(
                f"segment 873 completed verb precedes live 0143: {coordinate}"
            )

    joined = "\n".join(translations.values())
    for required in ("가도", "금전", "관계 개선", "우호도", "우리 가문"):
        if required not in joined:
            raise RuntimeError(
                f"segment 873 relationship terminology drifted: {required}"
            )
    if any(term in joined for term in ("호감도", "돈", "당가", "와의")):
        raise RuntimeError(
            "segment 873 retained forbidden relationship terminology"
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
        raise RuntimeError("segment 873 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S873",
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
