#!/usr/bin/env python3
"""Build Base authoring segment 962 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment961 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
CANONICAL_B = PREVIOUS.PREVIOUS
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S962.private.v1.jsonl"
)
SEGMENT = 962
ACTION_TOKEN = PREVIOUS.ACTION_TOKEN
FORCE_TOKEN = PREVIOUS.FORCE_TOKEN
CASTLE_TOKEN = "026432"
TRANSLATIONS_BY_RECORD = {
    2063: (
        "(이)가 상대… 목표로 삼을 성을\n고르는 것이 고민",
        "\n뭐, 우선은",
        "(이)라도…",
    ),
    2064: (
        "목표로 삼을 성은 아직",
        "\n우선은",
        "을(를)\n시험해 볼 생각",
        ".",
    ),
    2065: (
        "자,",
        "(이)가 상대인가\n우선은",
        "에서\n상황을 살펴보",
        ".",
    ),
    2066: (
        "지금은 공략 목표가 없군요\n",
        "을(를) 시행해 보는 건\n어떨까요?",
    ),
    2067: (
        "공략 목표가 정해지지 않았다면\n",
        "을(를) 시험해 보시겠습니까?",
    ),
    2068: (
        "적은",
        "… 어디부터\n공격해야 할지. 우선 지금은\n",
        "을(를) 진언드리겠습니다",
    ),
    2069: (
        "을(를) 공격하는 일은\n뒤로 미루도록",
        ". 우선은\n",
        "을(를) 실행해 보는 게 어떻겠습니까?",
    ),
    2070: CANONICAL_B.ROUGH_WARTIME_REQUEST_TRANSLATION,
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
    2063: ("が相手…目標の城は\n悩みどころ", "\nま、ひとまず", "でも…"),
    2064: ("目標の城が決まって", "\nひとまずは", "でも\n試してみ", "か"),
    2065: ("さて、", "が相手か\nひとまずは", "で\n様子を見", "かのう"),
    2066: ("今は目標がありませんね\n", "を実行してみては\nどうかしら？"),
    2067: ("目標が定まっていないなら\n", "を試してみては？"),
    2068: ("敵は", "…どこから\n攻めたものか。ひとまず今は\n", "を進言いたします"),
    2069: ("攻めはまだ先に\nな", "。ひとまず\n", "を実行してみては？"),
    2070: CANONICAL_B.EXPECTED_BASE_JP[2046],
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    2063: (FORCE_TOKEN, "01434A020000", ACTION_TOKEN, "050505"),
    2064: ("", "0143A0000000", ACTION_TOKEN, "01433C040000", "050505"),
    2065: ("", FORCE_TOKEN, ACTION_TOKEN, "01431E040000", "050505"),
    2066: ("", ACTION_TOKEN, "050505"),
    2067: ("", ACTION_TOKEN, "050505"),
    2068: ("", FORCE_TOKEN, ACTION_TOKEN, "050505"),
    2069: (FORCE_TOKEN, "01435A040000", ACTION_TOKEN, "050505"),
    2070: CANONICAL_B.EXPECTED_BASE_GAPS[2046],
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    2063: (FORCE_TOKEN, "014356020000", ACTION_TOKEN, "050505"),
    2064: ("", "0143A0000000", ACTION_TOKEN, "014348040000", "050505"),
    2065: ("", FORCE_TOKEN, ACTION_TOKEN, "01432A040000", "050505"),
    2069: (FORCE_TOKEN, "014366040000", ACTION_TOKEN, "050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:2063:0",
    "15:2063:2",
    "15:2068:1",
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 2066): (
        ("现在没有目标啊。\n不如实行", "\n看看吧？"),
        ("", ACTION_TOKEN, "050505"),
    ),
    ("TC", 2066): (
        ("現在沒有目標呢。\n執行", "看看如何？"),
        ("", ACTION_TOKEN, "050505"),
    ),
}
PK_EN_AUXILIARY = {
    2066: (
        (
            "We havenÖt any targets set, have we? "
            "What would you say to executing ",
            "?",
        ),
        ("", ACTION_TOKEN, "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B115_C_pristine_base_pc_jp_authoritative_"
    "unsettled_attack_target_and_interim_dynamic_action_policy_advice_"
    "with_explicit_base2063_2070_to_pk2093_2100_mapping_exact_base_pk_jp_"
    "sc_tc_and_actual_pk_en_auxiliary_context_dynamic_force_castle_and_"
    "colour_wrapped_action_tokens_attack_capture_and_war_kept_distinct_"
    "jing-eon_register_current_korean_morphology_terminal_corpora_base_pk_"
    "opcode_divergences_recorded_B_canonical_rough_wartime_tuple_imported_"
    "project_ellipsis_pairs_japanese_full_stop_removed_current_line_counts_"
    "and_protected_skeleton_preserved_runtime_fragment_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    160: ("없사옵니다", "없다", "없습니다"),
    586: ("이지요", "이군", "이군요", "이옵니다요", "이옵니다그려"),
    1054: ("합시다", "듯"),
    1084: ("합니다", "다", "하옵니다"),
    1114: ("합시다", "하리라"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    160: EXPECTED_BASE_MORPHOLOGY_TERMINALS[160],
    598: EXPECTED_BASE_MORPHOLOGY_TERMINALS[586],
    1066: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1054],
    1096: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1084],
    1126: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1114],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if TRANSLATIONS_BY_RECORD[2070] is not CANONICAL_B.ROUGH_WARTIME_REQUEST_TRANSLATION:
        raise RuntimeError("segment 962 B canonical wartime tuple reuse drifted")
    if (
        EXPECTED_BASE_JP[2070] != CANONICAL_B.EXPECTED_BASE_JP[2046]
        or EXPECTED_BASE_GAPS[2070] != CANONICAL_B.EXPECTED_BASE_GAPS[2046]
    ):
        raise RuntimeError("segment 962 Base2046/2070 exact source reuse drifted")
    reference = source_records[(15, 2046)]
    target = source_records[(15, 2070)]
    if (
        tuple(x.text for x in ENGINE.parse_record_literals(reference))
        != tuple(x.text for x in ENGINE.parse_record_literals(target))
        or COMMON.UTIL.record_gaps(reference) != COMMON.UTIL.record_gaps(target)
    ):
        raise RuntimeError("segment 962 live Base2046/2070 exact reuse drifted")
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 962 Base-to-PK mapping drifted")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != {2063, 2064, 2065, 2069}:
        raise RuntimeError("segment 962 Base-to-PK gap divergence drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 962 Base-to-PK JP literal drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 962 pristine/current gap drifted")
    if any(
        sum(gap.count(ACTION_TOKEN) for gap in gaps) != 1
        for gaps in EXPECTED_BASE_GAPS.values()
    ):
        raise RuntimeError("segment 962 action-token cardinality drifted")
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 962 project ellipsis pair drifted: {coordinate}"
            )
    joined = "\n".join(translations.values())
    for required in (
        "공략 목표",
        "공격하는 일",
        "진언",
        "시행",
        "실행",
        "시험",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 962 required meaning drifted: {required}")
    for forbidden in ("진행", "。", "건의드리겠습니다"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 962 forbidden wording retained: {forbidden}"
            )
    if TRANSLATIONS_BY_RECORD[2066][1] != (
        "을(를) 시행해 보는 건\n어떨까요?"
    ):
        raise RuntimeError("segment 962 試してみては canonical 시행 drifted")
    if "공격해야 할지" not in TRANSLATIONS_BY_RECORD[2068][1]:
        raise RuntimeError("segment 962 攻めたものか attack wording drifted")
    if (
        "실행해 보는 게" not in TRANSLATIONS_BY_RECORD[2069][2]
        or TRANSLATIONS_BY_RECORD[2069][1] != ". 우선은\n"
    ):
        raise RuntimeError("segment 962 実行 and punctuation linkage drifted")
    if len(raw_translations) != 23 or len(translations) != 23:
        raise RuntimeError("segment 962 visible decision count drifted")


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
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(rows) != 23 or len(validated) != len(translations):
        raise RuntimeError("segment 962 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 962 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S962",
                "source_literal_count": 23,
                "decision_count": len(rows),
                "hidden_non_display_count": 0,
                "runtime_fragment_pending": len(rows),
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [2063, 2064, 2065, 2069],
                "pristine_current_gap_divergence_records": [],
                "ellipsis_coordinates": sorted(CURRENT_ELLIPSIS_COORDINATES),
                "lf_count": sum(text.count("\n") for text in translations.values()),
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
