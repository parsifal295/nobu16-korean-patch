#!/usr/bin/env python3
"""Build Base authoring segment 872 decisions for the v0.15.0 retranslation."""

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
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S872.private.v1.jsonl"
SEGMENT = 872

ROAD_REPORTS = {
    1161: (
        "로 통하는 가도가 완성됐다!\n"
        "이제 여러모로 편리해지겠군"
    ),
    1162: (
        "로 통하는 가도가 완성되었소이다\n"
        "수송도 이동도 빨라질 것이오"
    ),
    1163: (
        "새 가도가 완성되었소이다\n",
        "이 한층 가까워진 듯하구려",
    ),
    1164: (
        "로 통하는 가도가 개통되었습니다\n"
        "이로써 병력 운용의 폭도 넓어질 것입니다"
    ),
    1165: (
        "로 통하는 가도가 열렸소이다\n"
        "이제 병사를 한결 움직이기 쉬워질 것이외다"
    ),
    1166: (
        "로 통하는 가도가 개통되었사옵니다\n"
        "이로써 영내는 더욱 다니기 쉬워지고\n"
        "전술의 폭이 넓어질 것이옵니다"
    ),
    1167: (
        "로 통하는 가도가 열렸사옵니다\n"
        "영내의 이동이 수월해져\n"
        "앞으로 병력을 운용하는 방식도 달라질 것이옵니다"
    ),
    1168: (
        "로 통하는 가도가 놓였사옵니다\n"
        "이로써 영내에서 병사를 움직이기 수월해지오니\n"
        "적을 상대로 유리하게 싸울 수 있사옵니다"
    ),
    1169: (
        "로 통하는 길이 생겼습니다\n"
        "이제 행군이 한결 수월해지겠군요"
    ),
    1170: (
        "까지 가는 경로가 늘었다\n"
        "전략의 폭이 크게 넓어졌군"
    ),
    1171: (
        "로 통하는 길이 생겼습니다\n"
        "이로써 행군도 수월해지겠군요"
    ),
    1172: (
        "에 새 가도가 완성되었소이다\n"
        "이로써 다양한 침공 방법을 강구할 수 있겠구려"
    ),
}
RAW_TRANSLATIONS: dict[str, str] = {}
for left_record_id, report in ROAD_REPORTS.items():
    values = report if isinstance(report, tuple) else (report,)
    right_record_id = left_record_id + 12
    for literal_id, text in enumerate(values):
        RAW_TRANSLATIONS[f"15:{left_record_id}:{literal_id}"] = text
        RAW_TRANSLATIONS[f"15:{right_record_id}:{literal_id}"] = text

RECORD_ARITIES = {
    **{record_id: 1 for record_id in range(1161, 1185)},
    1163: 2,
    1175: 2,
}
EXPECTED_JP = {
    1161: (
        "に通じる街道が完成したぜ\n"
        "これで何かと便利になるなあ",
    ),
    1162: (
        "に通じる街道が完成いたした\n"
        "輸送も移動も速くなりますぞ",
    ),
    1163: (
        "新たな街道が完成しましたぞ\n",
        "が近づいたようですな",
    ),
    1164: (
        "に通じる街道が開通しました\n"
        "これで用兵の幅も広がるというものです",
    ),
    1165: (
        "に通ずる街道が開き申した\n"
        "これで兵を動かしやすくなりましょうぞ",
    ),
    1166: (
        "に通じる街道が開通しました\n"
        "これで領内はいよいよ通りやすくなり\n"
        "戦術の幅が広がりまするぞ",
    ),
    1167: (
        "に通じる街道が開けてございます\n"
        "領内の移動がしやすくなり\n"
        "今後の兵の動かし方も変わってまいりますな",
    ),
    1168: (
        "に通ずる街道が通りましたわ\n"
        "これにて領内で兵が動かしやすうなりまする\n"
        "敵に対し有利に戦えまするぞ",
    ),
    1169: (
        "に通じる道ができました\n"
        "これで行軍が楽になりましょう",
    ),
    1170: (
        "への経路が増えた\n"
        "戦略の幅が大いに広がったな",
    ),
    1171: (
        "に通じる道ができました\n"
        "これにて行軍も楽になりましょう",
    ),
    1172: (
        "に新たな街道が完成しましたぞ\n"
        "これで様々な侵攻方法を考えられますな",
    ),
}
EXPECTED_JP.update(
    {
        record_id + 12: literals
        for record_id, literals in tuple(EXPECTED_JP.items())
    }
)
EXPECTED_BASE_GAPS = {
    **{
        record_id: ("029632", "050505")
        for record_id in range(1161, 1185)
    },
    1163: ("", "029632", "050505"),
    1175: ("", "029632", "050505"),
}
EXPECTED_PK_JP_GAPS = EXPECTED_BASE_GAPS
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
AUXILIARY_OVERRIDES: dict[
    tuple[str, str, int], tuple[tuple[str, ...], tuple[str, ...]]
] = {}
BASIS = (
    "review_queue_base_msggame_B105_pristine_base_pc_jp_authoritative_"
    "road_completion_reports_with_uniform_plus_8_pk_jp_sc_tc_exact_mapping_"
    "twelve_exact_speaker_pairs_dynamic_destination_tokens_historical_register_"
    "project_kaido_march_force_employment_and_strategy_terminology_current_"
    "layout_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for left_record_id in range(1161, 1173):
        right_record_id = left_record_id + 12
        if CORE.source_literals(
            source_records, left_record_id
        ) != CORE.source_literals(source_records, right_record_id):
            raise RuntimeError(
                "segment 872 exact road source pair drifted: "
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
                "segment 872 exact road translation pair drifted: "
                f"{left_record_id}/{right_record_id}"
            )

    joined = "\n".join(translations.values())
    for required in ("가도", "병력 운용", "행군", "전략", "침공"):
        if required not in joined:
            raise RuntimeError(
                f"segment 872 road terminology drifted: {required}"
            )
    for forbidden in ("용병", "군대길", "행진"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 872 retained forbidden road terminology: {forbidden}"
            )
    if raw_translations["15:1169:0"] == raw_translations["15:1171:0"]:
        raise RuntimeError("segment 872 distinct march reports collapsed")


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
        raise RuntimeError("segment 872 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S872",
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
