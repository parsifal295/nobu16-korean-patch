#!/usr/bin/env python3
"""Build Base authoring segment 899 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment856 as CANONICAL_B106
import build_base_batch001_segment884 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S899.private.v1.jsonl"
)
SEGMENT = 899
NEXT_MOVE_REPORT = (
    "\n전력을 약화한 지금이야말로 "
    "다음 수를 둘 호기라 사료되옵니다"
)
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1439:0": "의",
    "15:1439:1": "을(를) 완수하",
    "15:1439:2": NEXT_MOVE_REPORT,
    "15:1440:0": "을(를) 비롯한",
    "15:1440:1": "개 성에서",
    "15:1440:2": "을(를) 완수하",
    "15:1440:3": NEXT_MOVE_REPORT,
    "15:1441:0": "을(를) 시도한",
    "15:1441:1": "개 성 가운데,\n",
    "15:1441:2": "을(를) 비롯한",
    "15:1441:3": "개 성에서 완수하",
    "15:1441:4": (
        "!\n전력을 약화한 지금이야말로 "
        "다음 수를 둘 호기라 사료되옵니다"
    ),
    "15:1442:0": "의 간자가 벌인",
    "15:1442:1": "을(를) 받아\n",
    "15:1442:2": "의 병량과 병력에\n피해가 발생하",
    "15:1442:3": "…",
    "15:1443:0": "의 간자가 벌인",
    "15:1443:1": "을(를) 받아\n",
    "15:1443:2": "을(를) 비롯한",
    "15:1443:3": "개 성의 병량과 병력에\n피해가 발생하",
    "15:1443:4": "…",
}
RECORD_ARITIES = {
    1439: 3,
    1440: 4,
    1441: 5,
    1442: 4,
    1443: 5,
}
EXPECTED_BASE_JP = {
    1439: (
        "の",
        "を成し遂げ",
        "\n戦力を削いだ今こそ、次の手を打つ好機かと",
    ),
    1440: (
        "ら",
        "城の",
        "を成し遂げ",
        "\n戦力を削いだ今こそ、次の手を打つ好機かと",
    ),
    1441: (
        "をしかけた",
        "城のうち、\n",
        "ら",
        "城にて成し遂げ",
        "！\n戦力を削いだ今こそ、次の手を打つ好機かと",
    ),
    1442: (
        "の間者による",
        "を受け\n",
        "の兵糧と兵力に\n被害が出",
        "…",
    ),
    1443: (
        "の間者による",
        "を受け\n",
        "ら",
        "城の兵糧と兵力に\n被害が出",
        "…",
    ),
}
EXPECTED_PK_JP = EXPECTED_BASE_JP
EXPECTED_BASE_GAPS = {
    1439: ("026432", "023c", "014314020000", "050505"),
    1440: ("026432", "0232", "023c", "014314020000", "050505"),
    1441: (
        "023c",
        "0233",
        "026432",
        "0232",
        "014314020000",
        "050505",
    ),
    1442: ("025032", "023c", "026432", "014314020000", "050505"),
    1443: (
        "025032",
        "023c",
        "026432",
        "0232",
        "014314020000",
        "050505",
    ),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    1439: ("026432", "023c", "01431a020000", "050505"),
    1440: ("026432", "0232", "023c", "01431a020000", "050505"),
    1441: (
        "023c",
        "0233",
        "026432",
        "0232",
        "01431a020000",
        "050505",
    ),
    1442: ("025032", "023c", "026432", "01431a020000", "050505"),
    1443: (
        "025032",
        "023c",
        "026432",
        "0232",
        "01431a020000",
        "050505",
    ),
}
PK_RECORD_MAP = {
    record_id: record_id + 15 for record_id in RECORD_ARITIES
}
CURRENT_ELLIPSIS_COORDINATES = {"15:1442:3", "15:1443:4"}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}

SHARED_AUXILIARY = {
    ("SC", 1439): (
        ("已达成", "的", "。\n现已削弱战力，正是进行下一计策的好时机。"),
        ("", "026432", "023c", "050505"),
    ),
    ("TC", 1439): (
        ("已達成", "的", "。\n現已削弱戰力，正是進行下一計策的好時機。"),
        ("", "026432", "023c", "050505"),
    ),
    ("SC", 1440): (
        ("等", "城的", "完成了。\n应趁现在实力下降，乘胜追击。"),
        ("026432", "0232", "023c", "050505"),
    ),
    ("TC", 1440): (
        ("等", "城的", "已經達成。\n趁著目前戰力不足，乘勝追擊。"),
        ("026432", "0232", "023c", "050505"),
    ),
    ("SC", 1441): (
        (
            "施加了",
            "的",
            "城之中，\n",
            "等",
            "城达成了！\n如今战力削弱，是展开下一步的好机会。",
        ),
        ("", "023c", "0233", "026432", "0232", "050505"),
    ),
    ("TC", 1441): (
        (
            "進行",
            "的",
            "城當中，\n在",
            "等",
            "城已經成功！\n戰力已遭削弱，現在務必乘勝追擊！",
        ),
        ("", "023c", "0233", "026432", "0232", "050505"),
    ),
    ("SC", 1442): (
        ("遭受到", "的间谍的", "，\n", "的军粮与兵力出现了损失……"),
        ("", "025032", "023c", "026432", "050505"),
    ),
    ("TC", 1442): (
        ("遭到", "間諜的", "，\n導致", "軍糧和兵力受損……"),
        ("", "025032", "023c", "026432", "050505"),
    ),
    ("SC", 1443): (
        ("受到", "间谍的", "，\n", "等", "城的耐久与兵力受创……"),
        ("", "025032", "023c", "026432", "0232", "050505"),
    ),
    ("TC", 1443): (
        ("受到", "間諜的", "，\n", "等", "城的耐久與兵力受創……"),
        ("", "025032", "023c", "026432", "0232", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1439: (
        (
            "Our ",
            " on ",
            " was a success. Now that their power has dwindled, "
            "we should make our next move.",
        ),
        ("", "023c", "026432", "050505"),
    ),
    1440: (
        (
            "Our ",
            " on ",
            " castle(s), including ",
            ", was a success. Now that their power has dwindled, "
            "we should make our next move.",
        ),
        ("", "023c", "0232", "026432", "050505"),
    ),
    1441: (
        (
            "Of the ",
            " castle(s) where we tried ",
            ", ",
            " of them were successful, including at ",
            ". Now that their power has dwindled, "
            "we should make our next move.",
        ),
        ("", "0233", "023c", "0232", "026432", "050505"),
    ),
    1442: (
        (
            "After sustaining ",
            " from the ",
            " spy net, ",
            "Ös supplies and soldiers have been affected.",
        ),
        ("", "023c", "025032", "026432", "050505"),
    ),
    1443: (
        (
            "After sustaining ",
            " from the ",
            " spy net, supplies and soldiers have been affected in ",
            " castle(s), including ",
            ".",
        ),
        ("", "023c", "025032", "0232", "026432", "050505"),
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
    "review_queue_base_msggame_B108_pristine_base_pc_jp_authoritative_"
    "single_and_plural_castle_operation_success_and_spy_damage_reports_"
    "with_uniform_plus_15_pk_mapping_base_pk_sc_tc_exact_pk_en_auxiliary_"
    "context_b106_spy_damage_canonical_wording_operation_actor_target_"
    "perspective_rations_and_troop_damage_distinguished_ra_plural_count_"
    "relations_live_past_inflection_stems_current_layout_and_opcode_"
    "skeleton_preserved_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if raw_translations["15:1442:0"] != (
        CANONICAL_B106.RAW_TRANSLATIONS["15:972:0"]
    ):
        raise RuntimeError("segment 899 B106 spy-damage actor canonical drifted")
    plural_expectations = {
        "15:1440:0": "을(를) 비롯한",
        "15:1441:2": "을(를) 비롯한",
        "15:1443:2": "을(를) 비롯한",
    }
    for coordinate, expected in plural_expectations.items():
        if raw_translations[coordinate] != expected:
            raise RuntimeError(
                f"segment 899 plural castle relation drifted: {coordinate}"
            )
    stem_expectations = {
        "15:1439:1": "완수하",
        "15:1440:2": "완수하",
        "15:1441:3": "완수하",
        "15:1442:2": "발생하",
        "15:1443:3": "발생하",
    }
    for coordinate, ending in stem_expectations.items():
        if not raw_translations[coordinate].endswith(ending):
            raise RuntimeError(
                f"segment 899 live past-opcode stem drifted: {coordinate}"
            )
    for record_id, literal_id in ((1442, 2), (1443, 3)):
        text = raw_translations[f"15:{record_id}:{literal_id}"]
        if "병량과 병력" not in text or "내구" in text:
            raise RuntimeError(
                f"segment 899 rations/troop damage distinction drifted: "
                f"{record_id}"
            )
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if raw_translations[coordinate] != "…" or translations[coordinate] != "……":
            raise RuntimeError(
                f"segment 899 ellipsis seed/pair drifted: {coordinate}"
            )


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
        raise RuntimeError("segment 899 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S899",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "single_plural_operation_result_records": 5,
                "explicit_pk_mapping": True,
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
