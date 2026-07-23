#!/usr/bin/env python3
"""Build Base authoring segment 958 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment935 as SUPPORT


ENGINE = SUPPORT.ENGINE
COMMON = SUPPORT.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S958.private.v1.jsonl"
)
SEGMENT = 958
ACTION_TOKEN = "1B434D023C1B435A"
CASTLE_TOKEN = "026432"
FORCE_TOKEN = "025032"
TRANSLATIONS_BY_RECORD = {
    2021: (
        "공략에 대비하여\n",
        "을(를) 시행하여\n군비를 갖추어 보심이 어떠하신지요",
    ),
    2022: (
        "공략을 유리하게 이끌기 위해\n",
        "을(를) 시행하고 싶소만",
    ),
    2023: (
        "와(과)의 싸움에 대비하여\n",
        "을(를) 건의",
    ),
    2024: (
        "",
        "의 실행을 허락해 주시옵소서\n",
        "와(과)의 싸움에서\n크게 도움이 되리라 사료되옵니다",
    ),
    2025: (
        "을(를) 공격하기 전에\n",
        "을(를) 시행하여\n싸움을 유리하게 이끕시다",
    ),
    2026: (
        "을(를) 공격하기에 앞서\n",
        "을(를) 포석으로 삼아 보심이 어떠하신지요",
    ),
    2027: (
        "와(과)의 싸움을 유리하게 이끌고자\n",
        "의 실행을 허락해 주시옵소서\n결코 손해가 되지는 않을 것이옵니다",
    ),
    2028: (
        "와(과) 맞서기 전에\n",
        "을(를) 미리 시행하여\n우위를 점하고자 하옵니다",
    ),
    2029: (
        "을(를) 공략하기 전에…\n",
        "을(를) 시행하여\n채비를 빈틈없이 갖추는 게 어떻겠소?",
    ),
    2030: (
        "다가올 싸움을 유리하게 이끌기 위해\n",
        "을(를) 허락해 주시옵소서",
    ),
    2031: (
        "와(과)의 싸움에 대비한 포석으로\n",
        "을(를) 진언하옵니다",
    ),
    2032: (
        "피할 수 없는 싸움이라면\n적어도 우위를 점할 방책을 마련하고자 하오\n",
        "의 실행을 허락해 주시오",
    ),
}
EXCLUDED_NONVISIBLE_COORDINATES = {"15:2024:0": ""}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
    if f"15:{record_id}:{literal_id}"
    not in EXCLUDED_NONVISIBLE_COORDINATES
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_BASE_JP = {
    2021: ("攻略に向け\n", "を行うことで\n軍備を整えては"),
    2022: ("攻めを有利にするため\n", "をしたいのだが"),
    2023: ("との戦いに備え\n", "を具申"),
    2024: ("", "のご許可を\n", "との戦においては\n大いに役立つかと"),
    2025: ("を攻める前に\n", "を行い\n戦を有利に運びましょう"),
    2026: ("攻めに先駆けて\n", "を布石としてはいかが"),
    2027: (
        "との戦を有利に運ぶべく\n",
        "の実行をお許しあれ\n決して損にはなりますまい",
    ),
    2028: ("と事を構える前に\n", "を行っておき\n優位に進めたく存じます"),
    2029: ("を攻める前に…\n", "を行い\n支度を万全にしてはいかがか？"),
    2030: ("やがてくる戦を優位に運ぶため\n", "をお許しください"),
    2031: ("との戦いの布石として\n", "を進言する"),
    2032: (
        "避け得ぬ戦ならば\nせめて優位に運ぶ工夫を行いたく\n",
        "のご許可を",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    2021: (CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    2022: (CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    2023: (FORCE_TOKEN, ACTION_TOKEN, "0143CC010000050505"),
    2024: ("", ACTION_TOKEN, FORCE_TOKEN, "050505"),
    2025: (FORCE_TOKEN, ACTION_TOKEN, "050505"),
    2026: (FORCE_TOKEN, ACTION_TOKEN, "050505"),
    2027: (FORCE_TOKEN, ACTION_TOKEN, "050505"),
    2028: (FORCE_TOKEN, ACTION_TOKEN, "050505"),
    2029: (CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    2030: ("", ACTION_TOKEN, "050505"),
    2031: (FORCE_TOKEN, ACTION_TOKEN, "050505"),
    2032: ("", ACTION_TOKEN, "050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    2023: (FORCE_TOKEN, ACTION_TOKEN, "0143D2010000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {"15:2029:0"}
SHARED_AUXILIARY = {
    ("SC", 2024): (
        ("请您同意", "。\n在与", "对战时\n应当会派上大用场。"),
        ("", ACTION_TOKEN, FORCE_TOKEN, "050505"),
    ),
    ("TC", 2024): (
        ("請大人允准", "。\n與", "交戰應大有幫助。"),
        ("", ACTION_TOKEN, FORCE_TOKEN, "050505"),
    ),
    ("SC", 2025): (
        ("在攻打", "前，\n先进行", "，\n在战事中占据优势吧。"),
        ("", FORCE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("TC", 2025): (
        ("攻打", "前，\n不妨進行", "以主導戰局。"),
        ("", FORCE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("SC", 2026): (
        ("作为攻击", "的前奏，\n不如先做好", "的准备吧。"),
        ("", FORCE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("TC", 2026): (
        ("攻打", "前，\n不妨先以", "佈局。"),
        ("", FORCE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("SC", 2030): (
        ("为了在不久后的战事中占据优势，\n请您同意", "。"),
        ("", ACTION_TOKEN, "050505"),
    ),
    ("TC", 2030): (
        ("為了在即將到來的戰局佔優勢，\n請大人准許", "。"),
        ("", ACTION_TOKEN, "050505"),
    ),
}
PK_EN_AUXILIARY = {
    2024: (
        (
            "With your permission, I believe performing ",
            " will be a great aid to us in our fight against the ",
            ".",
        ),
        ("", ACTION_TOKEN, FORCE_TOKEN, "050505"),
    ),
    2025: (
        (
            "Let us give ourselves an advantage in the fight against the ",
            " by performing ",
            ".",
        ),
        ("", FORCE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    2026: (
        (
            "To take the initiative in our fight against the ",
            ", what do you say to performing ",
            "?",
        ),
        ("", FORCE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    2030: (
        (
            "Performing ",
            " will give us an edge in the coming battle. Please, will you approve it?",
        ),
        ("", ACTION_TOKEN, "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B115_A_pristine_base_pc_jp_authoritative_"
    "enemy_force_battle_preparation_permission_foothold_and_dynamic_"
    "action_proposals_with_explicit_base2021_2032_to_pk2051_2062_mapping_"
    "exact_base_pk_jp_sc_tc_literals_and_pk_en_auxiliary_context_dynamic_"
    "castle_026432_enemy_force_025032_and_colour_wrapped_action_1b434d_"
    "023c_1b435a_tokens_具申_as_geonui_進言_as_jineon_攻略_attack_戦_"
    "distinction_speaker_specific_historical_register_project_pair_"
    "ellipsis_2029_0_hidden_empty_2024_0_excluded_base_pk_2023_opcode_"
    "divergence_current_line_counts_and_skeleton_preserved_runtime_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    460: ("합니다", "하다", "하겠습니다", "하겠사옵니다"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    466: EXPECTED_BASE_MORPHOLOGY_TERMINALS[460],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 958 Base-to-PK mapping drifted")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != {2023}:
        raise RuntimeError("segment 958 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 958 pristine/current gap drifted")
    if EXCLUDED_NONVISIBLE_COORDINATES != {"15:2024:0": ""}:
        raise RuntimeError("segment 958 hidden exclusion drifted")
    if (
        raw_translations["15:2029:0"].count("…") != 1
        or translations["15:2029:0"].count("…") != 2
    ):
        raise RuntimeError("segment 958 ellipsis seed/pair drifted")
    joined = "\n".join(translations.values())
    for required in (
        "포석",
        "건의",
        "진언하옵니다",
        "맞서기 전에",
        "다가올 싸움",
        "방책",
        "허락해 주시옵소서",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 958 required meaning/register drifted: {required}"
            )
    for forbidden in ("일을 벌이기", "전쟁", "진행하고자", "건의하다"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 958 forbidden wording retained: {forbidden}"
            )
    if len(raw_translations) != 24 or len(translations) != 24:
        raise RuntimeError("segment 958 visible decision count drifted")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    prepared, translations, rows = COMMON.build_segment_rows_with_current_gaps(
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
    SUPPORT.annotate_morphology_evidence(
        prepared,
        rows,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        base_gaps=EXPECTED_CURRENT_GAPS,
        pk_gaps=EXPECTED_PK_JP_GAPS,
        expected_base=EXPECTED_BASE_MORPHOLOGY_TERMINALS,
        expected_pk=EXPECTED_PK_MORPHOLOGY_TERMINALS,
    )
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(rows) != 24 or len(validated) != len(translations):
        raise RuntimeError("segment 958 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"]
        or row["switch_korean_used"]
        for row in rows
    ):
        raise RuntimeError("segment 958 classification/authority drifted")
    line_distribution = {
        line_count: sum(
            text.count("\n") + 1 == line_count
            for text in translations.values()
        )
        for line_count in (1, 2, 3)
    }
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S958",
                "source_literal_count": 25,
                "decision_count": len(rows),
                "hidden_non_display_count": 1,
                "runtime_fragment_pending": len(rows),
                "dynamic_action_policy_token": ACTION_TOKEN,
                "dynamic_castle_token": CASTLE_TOKEN,
                "dynamic_enemy_force_token": FORCE_TOKEN,
                "ellipsis_pair_coordinates": sorted(
                    CURRENT_ELLIPSIS_COORDINATES
                ),
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [2023],
                "pristine_current_gap_divergence_records": [],
                "lf_count": sum(
                    text.count("\n") for text in translations.values()
                ),
                "line_distribution": line_distribution,
                "record_count": 19152,
                "outside_scope_records_exact": True,
                "target_runtime_skeleton_exact": True,
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
