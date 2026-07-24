#!/usr/bin/env python3
"""Build Base authoring segment 969 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment968 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S969.private.v1.jsonl"
)
SEGMENT = 969
ACTION_TOKEN = PREVIOUS.ACTION_TOKEN
FORCE_TOKEN = PREVIOUS.FORCE_TOKEN
CASTLE_TOKEN = PREVIOUS.CASTLE_TOKEN
TRANSLATIONS_BY_RECORD = {
    2138: (
        "와의 싸움뿐 아니라\n",
        "의 시행 여부도\n판단해 주시기를 바라옵니다",
    ),
    2139: (
        "을(를) 공략하는 데 차출되지 않았으므로\n",
        "을(를) 추진하고자 하오",
    ),
    2140: (
        "와의 싸움뿐 아니라\n",
        "의 시행 또한\n필요한 조치라 사료되옵니다",
    ),
    2141: (
        "와의 싸움 이후를 내다보고\n",
        "을(를) 추진하여\n다음에 대비하시는 것이 어떻겠습니까?",
    ),
    2142: ("○○을 위해,",),
    2143: ("에 관한 도움말을 확인하시겠습니까?",),
    2144: (
        "에서 일어난 사건을\n시노비가 조사해 왔다고 하옵니다!\n"
        "그 서신에 따르면…",
    ),
    2145: (
        "요즘 ",
        "에서 일어난 사건의\n자세한 내막이 알려",
        "\n전말을 보고",
        "?",
    ),
    2146: (
        "에서 일어난 사건의 경위가\n우리 가문에까지 전해졌사옵니다\n",
        "도 그 경위를 확인",
        "?",
    ),
    2147: (
        "에서 일어난 사건에 관한\n상세한 보고가 도착했습니다\n"
        "시노비의 서신에 따르면…",
    ),
    2148: (
        "에서 일어난 일의 상세한 사정을\n듣고 왔소\n"
        "떠돌이 승려의 말로는, 아무래도…",
    ),
    2149: (
        "에서 사건이 있었다 하옵니다\n자세한 이야기를 입수해 왔사오며\n"
        "아무래도 이런 경위인 듯하온데…",
    ),
}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_BASE_JP = {
    2138: ("との戦のみならず\n", "についても\nご判断をたまわりたく"),
    2139: ("攻略に呼ばれなかったため\n", "を進めたく存ずる"),
    2140: ("との戦のみでなく\n", "もまた\n必要な措置かと存じます"),
    2141: ("との戦の先を見据え\n", "を進め\n次に備えてはいかがでしょうか"),
    2142: ("○○のため、",),
    2143: ("についてのヘルプを確認しますか？",),
    2144: ("で起きた一件を\n忍びが調べてまいったとのこと！\nその書状によると…",),
    2145: ("近ごろの", "の事件について\n詳しい話を仕入れて", "\n顛末を報告", "か？"),
    2146: (
        "で起きた事件のいきさつ\n当家にまでも伝わっております\n",
        "もお聞きにな",
        "か？",
    ),
    2147: ("で起きた事件、\n詳しい報告がもたらされました\n忍びの書状によれば…",),
    2148: ("で起きた件の子細を\n聞いてまいった\n旅の僧の話では、なんでも…",),
    2149: ("で事件があったとの由\n詳しい話を入手してまいりました\nどうやらこんな経緯のようで…",),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    2138: (FORCE_TOKEN, ACTION_TOKEN, "050505"),
    2139: (CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    2140: (FORCE_TOKEN, ACTION_TOKEN, "050505"),
    2141: (FORCE_TOKEN, ACTION_TOKEN, "050505"),
    2142: ("", "050505"),
    2143: ("023C", "050505"),
    2144: (FORCE_TOKEN, "050505"),
    2145: ("", FORCE_TOKEN, "014308020000", "014394000000", "050505"),
    2146: (FORCE_TOKEN, "014308000000", "014336040000", "050505"),
    2147: (FORCE_TOKEN, "050505"),
    2148: (FORCE_TOKEN, "050505"),
    2149: (FORCE_TOKEN, "050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    2145: ("", FORCE_TOKEN, "01430E020000", "014394000000", "050505"),
    2146: (FORCE_TOKEN, "014308000000", "014342040000", "050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:2144:0",
    "15:2147:0",
    "15:2148:0",
    "15:2149:0",
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 2138): (
        ("除了与", "的战事，\n也请为", "\n做出决断吧。"),
        ("", FORCE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("TC", 2138): (
        ("不光是對抗", "，\n", "也有請大人判斷。"),
        ("", FORCE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("SC", 2142): (("为了○○，",), ("", "050505")),
    ("TC", 2142): (("為了○○，",), ("", "050505")),
    ("SC", 2143): (("要查看", "的帮助吗？"), ("", "023C", "050505")),
    ("TC", 2143): (("是否要觀看", "的相關說明？"), ("", "023C", "050505")),
    ("SC", 2145): (
        ("最近在", "发生的那件事，\n已经获得了详细的情报。\n是否要报告来龙去脉？"),
        ("", FORCE_TOKEN, "050505"),
    ),
    ("TC", 2145): (
        ("最近在", "發生的那件事，\n已經獲得了詳細的情報。\n是否要報告來龍去脈？"),
        ("", FORCE_TOKEN, "050505"),
    ),
    ("SC", 2146): (
        ("关于在", "发生的事件，\n本家好像已得知了详情。\n是否要听一下呢？"),
        ("", FORCE_TOKEN, "050505"),
    ),
    ("TC", 2146): (
        ("關於在", "發生的事件，\n本家好像已得知了詳情。\n是否要聽一下呢？"),
        ("", FORCE_TOKEN, "050505"),
    ),
    ("SC", 2147): (
        ("在", "发生的事，\n已有具体的报告。\n据间谍的书信所讲……"),
        ("", FORCE_TOKEN, "050505"),
    ),
    ("TC", 2147): (
        ("發生在", "的事件\n已送來詳細的報告。\n根據忍者的書信看來……"),
        ("", FORCE_TOKEN, "050505"),
    ),
    ("SC", 2148): (
        ("据旅行僧口中所讲，\n在", "发生的事，\n什么都……"),
        ("", FORCE_TOKEN, "050505"),
    ),
    ("TC", 2148): (
        ("已聽聞發生於", "的\n事件詳情。\n聽旅僧說似乎……"),
        ("", FORCE_TOKEN, "050505"),
    ),
}
PK_EN_AUXILIARY = {
    2138: (
        (
            "Fighting the ",
            " is not our only preoccupation. I humbly ask that you make "
            "a decision concerning ",
            ".",
        ),
        ("", FORCE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    2142: (("For ÌÌ,",), ("", "050505")),
    2143: (
        ("Would you like to consult the help screen concerning ", "?"),
        ("", "023C", "050505"),
    ),
    2145: (
        (
            "I recently learned of an incident concerning the ",
            ". Shall I report the details?",
        ),
        ("", FORCE_TOKEN, "050505"),
    ),
    2146: (
        (
            "Details concerning the ",
            " incident have been made known to me. "
            "Would you like to hear the particulars?",
        ),
        ("", FORCE_TOKEN, "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B116_B_pristine_base_pc_jp_authoritative_"
    "war_and_dynamic_action_policy_judgment_help_template_and_incident_"
    "reporting_with_explicit_base2138_2149_to_pk2168_2179_mapping_exact_"
    "base_pk_jp_sc_tc_and_actual_pk_en_auxiliary_context_dynamic_action_"
    "force_castle_and_help_subject_tokens_direction_template_placeholder_"
    "boundary_shinobi_glossary_term_our_house_war_and_capture_distinctions_"
    "tenmatsu_ikisatsu_and_shisai_meanings_kept_distinct_dynamic_supplement_"
    "sihaeng_and_susin_promotion_current_korean_morphology_terminal_corpora_"
    "base_pk_opcode_divergences_recorded_project_ellipsis_pairs_current_"
    "line_counts_and_protected_skeleton_preserved_runtime_fragment_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    8: (
        "아버님",
        "어머님",
        "할아버님",
        "할머님",
        "숙부님",
        "숙모님",
        "그대",
        "너",
        "주군님",
        "주군",
        "도련님",
        "공주님",
        "쇼군님",
        "스님",
        "네놈",
        "귀하",
        "귀공",
        "원숭이",
        "놈",
        "이놈",
        "누님",
        "형님",
    ),
    148: ("하겠습니다", "하겠다", "하자"),
    520: ("당도했습니다", "졌다"),
    1078: ("합니다", "다"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    8: (
        "아버님",
        "어머님",
        "할아버님",
        "할머님",
        "숙부님",
        "숙모님",
        "그대",
        "너",
        "주군님",
        "주군",
        "도련님",
        "공주님",
        "쇼군님",
        "스님",
        "네놈",
        "님",
        "귀하",
        "귀공",
        "원숭이",
        "놈",
        "이놈",
        "누님",
        "형님",
    ),
    148: EXPECTED_BASE_MORPHOLOGY_TERMINALS[148],
    526: EXPECTED_BASE_MORPHOLOGY_TERMINALS[520],
    1090: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1078],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 969 Base-to-PK mapping drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 969 Base-to-PK JP literal drifted")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != {2145, 2146}:
        raise RuntimeError("segment 969 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 969 pristine/current gap drifted")
    action_records = {
        record_id
        for record_id, gaps in EXPECTED_BASE_GAPS.items()
        if sum(gap.count(ACTION_TOKEN) for gap in gaps) == 1
    }
    if action_records != set(range(2138, 2142)):
        raise RuntimeError("segment 969 action-token boundary drifted")
    verified_morphology_compositions = {
        "15:2145:1": (
            EXPECTED_BASE_MORPHOLOGY_TERMINALS[520][1],
            "자세한 내막이 알려졌다",
        ),
        "15:2145:2": (
            EXPECTED_BASE_MORPHOLOGY_TERMINALS[148][0],
            "전말을 보고하겠습니다",
        ),
        "15:2146:1": (
            EXPECTED_BASE_MORPHOLOGY_TERMINALS[1078][0],
            "경위를 확인합니다",
        ),
    }
    if any(
        not (
            raw_translations[coordinate] + terminal
        ).endswith(expected)
        for coordinate, (terminal, expected)
        in verified_morphology_compositions.items()
    ):
        raise RuntimeError("segment 969 verified morphology stem drifted")
    if (
        EXPECTED_BASE_GAPS[2142] != ("", "050505")
        or TRANSLATIONS_BY_RECORD[2142] != ("○○을 위해,",)
        or EXPECTED_BASE_GAPS[2143] != ("023C", "050505")
        or not TRANSLATIONS_BY_RECORD[2143][0].startswith("에 관한")
    ):
        raise RuntimeError("segment 969 template/help token direction drifted")
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 969 project ellipsis pair drifted: {coordinate}"
            )
    joined = "\n".join(translations.values())
    for required in (
        "우리 가문",
        "시행",
        "추진",
        "시노비",
        "전말",
        "경위",
        "상세한 사정",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 969 required meaning drifted: {required}")
    for forbidden in ("당가", "진행", "자초지종", "닌자", "。"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 969 forbidden wording retained: {forbidden}"
            )
    if len(raw_translations) != 21 or len(translations) != 21:
        raise RuntimeError("segment 969 visible decision count drifted")


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
    template_row = next(
        row for row in rows if row["coordinate"] == "15:2142:0"
    )
    template_row["scope_classification"] = "retranslated"
    template_row["runtime_review"] = "not_required"
    template_row["basis"] = (
        "pristine_base_pc_jp_authoritative_static_purpose_template_"
        "complete_literal_with_no_runtime_opcode_or_dynamic_fragment"
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
    if len(rows) != 21 or len(validated) != len(translations):
        raise RuntimeError("segment 969 validated count drifted")
    template_rows = [
        row for row in rows if row["coordinate"] == "15:2142:0"
    ]
    pending_rows = [
        row for row in rows if row["coordinate"] != "15:2142:0"
    ]
    if (
        len(template_rows) != 1
        or template_rows[0]["scope_classification"] != "retranslated"
        or template_rows[0]["runtime_review"] != "not_required"
        or any(
            row["scope_classification"] != "runtime_fragment_pending"
            or row["runtime_review"] != "pending"
            for row in pending_rows
        )
        or any(
            row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            for row in rows
        )
    ):
        raise RuntimeError("segment 969 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S969",
                "source_literal_count": 21,
                "decision_count": len(rows),
                "hidden_non_display_count": 0,
                "retranslated": 1,
                "runtime_fragment_pending": len(rows) - 1,
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [2145, 2146],
                "pristine_current_gap_divergence_records": [],
                "ellipsis_coordinates": sorted(CURRENT_ELLIPSIS_COORDINATES),
                "lf_count": sum(
                    text.count("\n") for text in translations.values()
                ),
                "line_distribution": {
                    line_count: sum(
                        text.count("\n") + 1 == line_count
                        for text in translations.values()
                    )
                    for line_count in (1, 2, 3)
                },
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
