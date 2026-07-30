#!/usr/bin/env python3
"""Build Base authoring segment 854 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment842 as COMMON


ENGINE = COMMON.ENGINE
OUTPUT = REPO / "tmp" / WORKSTREAM.name / "decisions" / "base_msggame_B001_S854.private.v1.jsonl"
SEGMENT = 854
RAW_TRANSLATIONS: dict[str, str] = {
    "15:926:0": (
        "포위하기 전에 공작을 펼쳐\n"
        "방비를 약화해 두는 것…\n"
        "좋은 계책이라 사료되옵니다"
    ),
    "15:927:0": (
        "공작으로 방비를 약화한다… 과연\n"
        "공성은 정정당당히 치르고 싶으나\n"
        "전국의 난세라면 그것만으로는 부족한 법"
    ),
    "15:928:0": "다가올 공성전에 대비한 공작이라…\n이 일은",
    "15:928:1": "에게 맡겨 주십시오\n적의 방비에 구멍을 뚫어 보이겠습니다",
    "15:929:0": (
        "공성 전에 공작이라니, 좋은 생각이십니다\n"
        "적이 꺼리는 일은 미리\n"
        "적극적으로 해 두어야 하겠지요"
    ),
    "15:930:0": "과연 공성에 필요한 것은 지혜\n이 일은 경험이 풍부한",
    "15:930:1": "에게\n맡겨 주시옵소서",
    "15:931:0": (
        "공작에 착수하겠습니다\n"
        "아무리 견고한 성이라도 이 개미구멍 하나로\n"
        "무너지게 될 것입니다"
    ),
    "15:932:0": (
        "공작이라면 맡겨 주시오\n"
        "어떤 성에든 잠입하여\n"
        "적의 방비를 무너뜨려 보이겠소"
    ),
    "15:933:0": (
        "힘으로 공격할 필요는 없겠지요\n"
        "미리 공략하기 쉽도록\n"
        "손을 써 두면 되니까요"
    ),
    "15:934:0": "미리 성벽에 손을 써 두면\n쉽게 쳐들어갈 수 있을 것입니다",
    "15:935:0": "에 대한 공작을 완수하여",
    "15:935:1": "!\n방비가 크게 무너진 지금이야말로\n그곳을 공략할 호기",
    "15:936:0": "에 공작을 펼쳤습니다\n당분간은 수비가 허술할 것입니다",
    "15:937:0": "에 공작을 펼쳤다\n수비가 무너졌으니 공략하기 쉬워졌다",
    "15:938:0": "에 공작을 펼쳤습니다\n쳐들어가기에 좋은 기회라\n할 수 있겠지요",
    "15:939:0": "에 공작을 펼쳤사옵니다\n당분간은 수비가 허술할 것이옵니다",
    "15:940:0": (
        "에 조금 손을 써 두었사옵니다\n"
        "당분간 수비가 허술해져\n"
        "있을 것이옵니다"
    ),
    "15:941:0": "에 대한 공작을 펼쳤습니다\n이로써 성의 방비도 허술해졌을 것입니다",
    "15:942:0": "에 대한 공작을 감행했다\n조금은 공략하기 쉬워졌을 것이다",
    "15:943:0": (
        "에 대한 공작을 펼쳤습니다\n"
        "이로써 성의 수비는\n"
        "다소 약해졌을 것입니다"
    ),
    "15:944:0": "에서 공작을 펼치고 왔습니다\n방비가 조금은 약해졌을 터…",
}
RECORD_ARITIES = {
    926: 1,
    927: 1,
    928: 2,
    929: 1,
    930: 2,
    931: 1,
    932: 1,
    933: 1,
    934: 1,
    935: 2,
    936: 1,
    937: 1,
    938: 1,
    939: 1,
    940: 1,
    941: 1,
    942: 1,
    943: 1,
    944: 1,
}
EXPECTED_JP = {
    926: ("包囲する前に工作を施し\n防備を脆くしておく…\n良き策かと存じます",),
    927: (
        "工作にて防備を削ぐ…なるほど\n"
        "城攻めは正々堂々とありたいが\n"
        "戦国の世なれば、それだけでは足らぬもの",
    ),
    928: (
        "来たる攻城戦に備えて工作とは…\nここは",
        "にお任せを\n敵の防備に穴を開けてみせましょう",
    ),
    929: (
        "城攻め前に工作とは、良きお考えです\n"
        "敵の嫌がることはあらかじめ\n"
        "積極的に行っておくべきでしょう",
    ),
    930: (
        "なるほど、城攻めにいるものと申さば知恵\nここは経験豊富な",
        "に\nお任せくだされ",
    ),
    931: (
        "工作にかかります\n"
        "堅固な城も、このアリの穴から\n"
        "崩れることでしょう",
    ),
    932: (
        "工作ならお任せあれ\n"
        "いかなる城にも侵入し\n"
        "敵の防備を崩してみせようぞ",
    ),
    933: (
        "力攻めする必要などありませんね\n"
        "あらかじめ攻めやすいよう\n"
        "細工をしておけばよいのですから",
    ),
    934: ("あらかじめ城壁に細工を施しておけば\n容易に攻め込めましょう",),
    935: (
        "の工作、成し遂げて",
        "！\n防備が大きく崩れた今こそ\nかの地を攻め取る好機",
    ),
    936: ("に工作を行いました\nしばらくの間は守りが薄いはずです",),
    937: ("に工作を致した\n守りが崩れたゆえ、攻め易うなったぞ",),
    938: ("に工作を施しました\n攻め込むには好機と\nいえましょうな",),
    939: ("に工作をいたしました\nしばらくの間は守りが薄いはずです",),
    940: ("にちと悪さをいたした\nしばしの間、守りは薄うなって\nおりましょう",),
    941: ("への工作を行いました\nこれで城の防備ももろくなったはずです",),
    942: ("の工作を敢行した\n少しは攻めやすくなったことだろう",),
    943: ("への工作を行いました\nこれで城の守りは\n多少弱くなったことでしょう",),
    944: ("にて工作をしてきました\n少しは防備がもろくなったはず…",),
}
EXPECTED_BASE_GAPS = {
    926: ("", "050505"),
    927: ("", "050505"),
    928: ("", "014301000000", "050505"),
    929: ("", "050505"),
    930: ("", "014301000000", "050505"),
    931: ("", "050505"),
    932: ("", "050505"),
    933: ("", "050505"),
    934: ("", "050505"),
    935: ("026432", "014308020000", "01435c020000050505"),
    **{record_id: ("026432", "050505") for record_id in range(936, 945)},
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    935: ("026432", "01430e020000", "014368020000050505"),
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:926:0",
    "15:927:0",
    "15:928:0",
    "15:944:0",
}
SC_935 = (
    "已完成对",
    "的工作！\n城的防御已经被大幅破坏，\n现在正是攻略此地的大好时机。",
)
TC_935 = (
    "已完成對",
    "的工作！\n城的防禦已經被大幅破壞，\n現在正是攻略此地的大好時機。",
)
EN_935 = (
    "WeÖve done what we can in terms of destabilization at ",
    "! Now that their defenses have crumbled, we should attack!",
)
AUXILIARY_OVERRIDES = {
    **{
        (side, "SC", 935): (SC_935, ("", "026432", "050505"))
        for side in ("base", "pk")
    },
    **{
        (side, "TC", 935): (TC_935, ("", "026432", "050505"))
        for side in ("base", "pk")
    },
    ("pk", "EN", 935): (EN_935, ("", "026432", "050505")),
}
BASIS = (
    "review_queue_base_msggame_B103_pristine_base_pc_jp_authoritative_"
    "castle_destabilization_plan_acceptance_and_success_reports_with_exact_"
    "uniform_plus_7_pk_jp_sc_tc_arrays_pk_en_sc_tc_auxiliary_context_"
    "historical_person_register_dynamic_person_castle_particles_current_pc_"
    "line_token_gap_signature_preserved_runtime_fragment_pending"
)


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for record_id, expected in EXPECTED_JP.items():
        if COMMON.CORE.source_literals(source_records, record_id) != expected:
            raise RuntimeError(f"segment 854 authoritative Base JP drifted: {record_id}")
    if not (
        raw_translations["15:928:1"].startswith("에게 ")
        and raw_translations["15:930:1"].startswith("에게\n")
        and raw_translations["15:935:0"].startswith("에 대한 공작")
    ):
        raise RuntimeError("segment 854 dynamic person/castle particle drifted")
    joined = "\n".join(translations.values())
    for required in ("공작", "방비", "공성", "공략", "수비", "성벽"):
        if required not in joined:
            raise RuntimeError(f"segment 854 terminology drifted: {required}")
    exact_expectations = {
        "15:927:0": (
            "공작으로 방비를 약화한다… 과연\n"
            "공성은 정정당당히 치르고 싶으나\n"
            "전국의 난세라면 그것만으로는 부족한 법"
        ),
        "15:928:0": "다가올 공성전에 대비한 공작이라…\n이 일은",
        "15:930:1": "에게\n맡겨 주시옵소서",
        "15:931:0": (
            "공작에 착수하겠습니다\n"
            "아무리 견고한 성이라도 이 개미구멍 하나로\n"
            "무너지게 될 것입니다"
        ),
        "15:935:0": "에 대한 공작을 완수하여",
        "15:937:0": "에 공작을 펼쳤다\n수비가 무너졌으니 공략하기 쉬워졌다",
        "15:940:0": (
            "에 조금 손을 써 두었사옵니다\n"
            "당분간 수비가 허술해져\n"
            "있을 것이옵니다"
        ),
    }
    for coordinate, expected in exact_expectations.items():
        if raw_translations[coordinate] != expected:
            raise RuntimeError(
                f"segment 854 audited canonical drifted: {coordinate}"
            )
    if any(term in joined for term in ("세공", "내구", "첩자", "폭동")):
        raise RuntimeError("segment 854 retained forbidden terminology")


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
        excluded_blank_coordinates=set(),
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 854 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S854",
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
