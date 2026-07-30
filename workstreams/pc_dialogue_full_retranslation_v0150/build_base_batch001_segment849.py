#!/usr/bin/env python3
"""Build Base authoring segment 849 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment848 as PRIOR


COMMON = PRIOR.COMMON
ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S849.private.v1.jsonl"
SEGMENT = 849
RAW_TRANSLATIONS: dict[str, str] = {
    **{
        f"15:{record_id}:0": PRIOR.CONTROL_ADVANCE_TRANSLATION
        for record_id in range(873, 877)
    },
    "15:877:0": "의 지배율이",
    "15:877:1": "만큼 확대(",
    "15:877:2": "→",
    "15:877:3": ")",
    "15:878:0": "의 지배율이",
    "15:878:1": "만큼 상승(",
    "15:878:2": "→",
    "15:878:3": ")",
    "15:879:0": "다음에 공략할 곳은",
    "15:879:1": "인가?\n그렇다면",
    "15:879:2": "이(가) 선봉에 나서겠소!\n…아니, 그 전에 한 가지 계책이 있소",
    "15:880:0": "의",
    "15:880:1": "공략을\n생각하고 계시다면 부디",
    "15:880:2": "\n에게 선봉을 맡겨 주시옵소서! 다만 그 전에…",
    "15:881:0": "의",
    "15:881:1": (
        "은(는)\n"
        "공략할 만한 성인 듯하오나\n"
        "정면으로 공략하는 것은 어리석은 계책인 듯하옵니다…"
    ),
    "15:882:0": "이(가) 보기에는",
    "15:882:1": "의\n",
    "15:882:2": (
        "은(는) 제법 공략하기 까다로운 성…\n"
        "미리 힘을 깎아 두어야 할 듯하옵니다"
    ),
}
RECORD_ARITIES = {
    **{record_id: 1 for record_id in range(873, 877)},
    877: 4,
    878: 4,
    879: 3,
    880: 3,
    881: 2,
    882: 3,
}
EXPECTED_BASE_GAPS = {
    **{record_id: ("029632", "050505") for record_id in range(873, 877)},
    877: ("029632", "0232", "0233", "0234", "050505"),
    878: ("029632", "0232", "0233", "0234", "050505"),
    879: ("", "026432", "014301000000", "050505"),
    880: ("025032", "026432", "014301000000", "050505"),
    881: ("025032", "026432", "050505"),
    882: ("014301000000", "025032", "026432", "050505"),
}
EXPECTED_PK_JP_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_EN_ARITIES = {
    **{record_id: 1 for record_id in range(873, 883)},
    878: 4,
}
EXPECTED_PK_EN_GAPS = {
    **{record_id: ("", "050505") for record_id in range(873, 883)},
    878: ("029632", "0232", "0233", "0234", "050505"),
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:879:2",
    "15:880:2",
    "15:881:1",
    "15:882:2",
}
BASIS = (
    "base_msggame_B103_pristine_base_pc_jp_authoritative_exact_control_"
    "advance_result_group_control_rate_ui_and_personality_castle_assault_"
    "subterfuge_proposals_uniform_plus_7_pk_jp_sc_arrays_base_pk_sc_tc_"
    "exact_pk_en_auxiliary_context_dynamic_faction_castle_person_and_numeric_"
    "tokens_historical_register_current_pc_layout_gap_signature_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    advance_source = (
        "の支配を進めました\nこれで収入や兵も増えましたぞ",
    )
    if any(
        COMMON.source_literals(source_records, record_id) != advance_source
        for record_id in range(865, 877)
    ):
        raise RuntimeError("segment 849 865-876 exact control source drifted")
    if any(
        raw_translations[f"15:{record_id}:0"] != PRIOR.CONTROL_ADVANCE_TRANSLATION
        for record_id in range(873, 877)
    ):
        raise RuntimeError("segment 849 865-876 cross-segment translation drifted")

    expected_jp = {
        877: ("の支配率が", "拡大(", "→", ")"),
        878: ("の支配率が", "上昇(", "→", ")"),
        879: (
            "次に攻めるのは",
            "か？\nそれなら",
            "が先鋒に！\n…いや、その前に１つ案がある",
        ),
        880: (
            "の",
            "攻めを\nお考えなら是非",
            "\nに先鋒を！　ただその前に…",
        ),
        881: (
            "の",
            "は\n攻め甲斐のある城のようですが\n正面から攻めるのは愚策かと…",
        ),
        882: (
            "が思うに",
            "の\n",
            "は少々厄介な城…\n事前に力を削いでおくべきかと",
        ),
    }
    for record_id, expected in expected_jp.items():
        if COMMON.source_literals(source_records, record_id) != expected:
            raise RuntimeError(f"segment 849 authoritative Base JP drifted: {record_id}")

    exact_expectations = {
        "15:877:0": "의 지배율이",
        "15:877:1": "만큼 확대(",
        "15:878:1": "만큼 상승(",
        "15:879:1": "인가?\n그렇다면",
        "15:879:2": "이(가) 선봉에 나서겠소!\n…아니, 그 전에 한 가지 계책이 있소",
        "15:880:0": "의",
        "15:880:2": "\n에게 선봉을 맡겨 주시옵소서! 다만 그 전에…",
        "15:881:0": "의",
        "15:882:0": "이(가) 보기에는",
        "15:882:1": "의\n",
    }
    for coordinate, expected in exact_expectations.items():
        if raw_translations[coordinate] != expected:
            raise RuntimeError(f"segment 849 token role/particle drifted: {coordinate}")

    joined = "\n".join(translations.values())
    for required in ("지배율", "선봉", "공략", "계책", "힘을 깎아"):
        if required not in joined:
            raise RuntimeError(f"segment 849 terminology drifted: {required}")
    if any(term in joined for term in ("선봉으로", "공격할 보람", "지배를 진행")):
        raise RuntimeError("segment 849 retained forbidden legacy phrasing")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        pk_en_arities=EXPECTED_PK_EN_ARITIES,
        pk_en_gaps=EXPECTED_PK_EN_GAPS,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 849 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S849",
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
