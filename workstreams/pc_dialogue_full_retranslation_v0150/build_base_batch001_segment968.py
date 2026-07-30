#!/usr/bin/env python3
"""Build Base authoring segment 968 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment959 as CANONICAL_959
import build_base_batch001_segment960 as CANONICAL_960


ENGINE = CANONICAL_960.ENGINE
COMMON = CANONICAL_960.COMMON
SUPPORT = CANONICAL_960.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S968.private.v1.jsonl"
)
SEGMENT = 968
ACTION_TOKEN = CANONICAL_960.ACTION_TOKEN
FORCE_TOKEN = CANONICAL_959.FORCE_TOKEN
CASTLE_TOKEN = CANONICAL_959.CASTLE_TOKEN
CANONICAL_RECORD_MAP = {
    2127: (CANONICAL_959, 2043),
    2128: (CANONICAL_960, 2044),
    2129: (CANONICAL_960, 2045),
}
TRANSLATIONS_BY_RECORD = {
    2127: CANONICAL_959.TRANSLATIONS_BY_RECORD[2043],
    2128: CANONICAL_960.TRANSLATIONS_BY_RECORD[2044],
    2129: CANONICAL_960.TRANSLATIONS_BY_RECORD[2045],
    2130: (
        "을(를) 공격하는 중에 미안하네만\n",
        "을(를) 추진하고 싶네",
    ),
    2131: (
        "을(를) 공략하는 동안 후방을 지킬 방책으로\n",
        "을(를) 시행하도록 허락해 주시오",
    ),
    2132: (
        "와의 싸움 이후를 내다보고\n",
        "을(를) 건의",
    ),
    2133: (
        "을(를) 공략하는 한편\n",
        "의 시행에 대해서도\n",
        "고려해 주시길 바라고 ",
    ),
    2134: (
        "을(를) 공략하는 일뿐 아니라\n",
        "의 시행에도\n눈을 돌려 보시는 것이 어떻겠습니까?",
    ),
    2135: (
        "을(를) 공격하는 동시에\n",
        "도 함께 추진하는 것이\n상책이라 사료되옵니다",
    ),
    2136: (
        "",
        "을(를) 공략하는 중이라 송구하오나\n",
        "을(를) 추진하도록 허락해\n주시기를 바라옵니다",
    ),
    2137: (
        "",
        "을(를) 공략하는 데 참전하지 않았으므로\n",
        "을(를) 추진하고자 하오니\n허락해 주시옵소서",
    ),
}
EXCLUDED_NONVISIBLE_COORDINATES = {
    "15:2136:0": "",
    "15:2137:0": "",
}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(translations)
    if f"15:{record_id}:{literal_id}" not in EXCLUDED_NONVISIBLE_COORDINATES
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_BASE_JP = {
    2127: CANONICAL_959.EXPECTED_BASE_JP[2043],
    2128: CANONICAL_960.EXPECTED_BASE_JP[2044],
    2129: CANONICAL_960.EXPECTED_BASE_JP[2045],
    2130: ("攻めの最中すまないが\n", "を進めたい"),
    2131: ("攻めの留守居として\n", "をお許しあれ"),
    2132: ("との戦の先を見据え\n", "を具申"),
    2133: ("攻略と並行し\n", "についても\n", "考慮願"),
    2134: ("攻略のみならず\n", "にも\n目を向けられてはいかが"),
    2135: ("攻めと同時に\n", "をも進めるが\n上策かと存ずる"),
    2136: ("", "攻略中恐縮ですが\n", "を進める許可を\nいただきたく存じます"),
    2137: ("", "攻略に参陣しておらぬゆえ\n", "を進めたく\n許可を願いまする"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    2127: CANONICAL_959.EXPECTED_BASE_GAPS[2043],
    2128: CANONICAL_960.EXPECTED_BASE_GAPS[2044],
    2129: CANONICAL_960.EXPECTED_BASE_GAPS[2045],
    2130: (FORCE_TOKEN, ACTION_TOKEN, "050505"),
    2131: (CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    2132: (FORCE_TOKEN, ACTION_TOKEN, "0143CC010000050505"),
    2133: (
        CASTLE_TOKEN,
        ACTION_TOKEN,
        "01438A040000",
        "0143BE000000050505",
    ),
    2134: (CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    2135: (CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    2136: ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    2137: ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    2132: (FORCE_TOKEN, ACTION_TOKEN, "0143D2010000050505"),
    2133: (
        CASTLE_TOKEN,
        ACTION_TOKEN,
        "014396040000",
        "0143BE000000050505",
    ),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {"15:2127:1"}
SHARED_AUXILIARY = {
    ("SC", 2132): (
        ("请容我展望与", "的战事发展，\n呈报", "。"),
        ("", FORCE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("TC", 2132): (
        ("考量到與", "之間的戰火，\n微臣奏請", "。"),
        ("", FORCE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("SC", 2133): (
        ("在攻略", "的同时，\n也请您考虑一下\n", "。"),
        ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("TC", 2133): (
        ("於", "攻略當下，\n關於", "也請大人\n考慮並行。"),
        ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("SC", 2134): (
        ("除了攻略", "，\n请您也关注一下\n", "吧。"),
        ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    ("TC", 2134): (
        ("心思別只放在", "的攻略，\n", "不妨也關注一下。"),
        ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    ),
}
PK_EN_AUXILIARY = {
    2132: (
        (
            "Looking towards the outcome of our battle against the ",
            ", I would like to give my submission for ",
            ".",
        ),
        ("", FORCE_TOKEN, ACTION_TOKEN, "050505"),
    ),
    2133: (
        (
            "Would you consider performing ",
            " to go alongside our preparations to capture ",
            "?",
        ),
        ("", ACTION_TOKEN, CASTLE_TOKEN, "050505"),
    ),
    2134: (
        (
            "We must not preoccupy ourselves with only the capture of ",
            ". Would you consider turning your attention to ",
            "?",
        ),
        ("", CASTLE_TOKEN, ACTION_TOKEN, "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B116_B_pristine_base_pc_jp_authoritative_"
    "wartime_parallel_dynamic_action_policy_advice_with_explicit_base2127_"
    "2137_to_pk2157_2167_mapping_exact_base_pk_jp_sc_tc_and_actual_pk_en_"
    "auxiliary_context_dynamic_action_force_and_castle_tokens_direction_"
    "B115_2043_2045_plus_84_exact_canonical_tuple_reuse_war_attack_and_"
    "capture_distinctions_geonui_register_dynamic_supplement_siheang_and_"
    "susin_promotion_current_korean_morphology_terminal_corpora_base_pk_"
    "opcode_divergences_recorded_hidden_empty_literals_excluded_project_"
    "ellipsis_pair_current_line_counts_and_protected_skeleton_preserved_"
    "runtime_fragment_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    190: ("있습니다", "으", "있사옵니다"),
    460: ("합니다", "하다", "하겠습니다", "하겠사옵니다"),
    1162: ("고", ""),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    190: EXPECTED_BASE_MORPHOLOGY_TERMINALS[190],
    466: EXPECTED_BASE_MORPHOLOGY_TERMINALS[460],
    1174: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1162],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    for record_id, (module, canonical_id) in CANONICAL_RECORD_MAP.items():
        if (
            TRANSLATIONS_BY_RECORD[record_id]
            is not module.TRANSLATIONS_BY_RECORD[canonical_id]
            or EXPECTED_BASE_JP[record_id]
            != module.EXPECTED_BASE_JP[canonical_id]
            or EXPECTED_BASE_GAPS[record_id]
            != module.EXPECTED_BASE_GAPS[canonical_id]
        ):
            raise RuntimeError(
                f"segment 968 B115 canonical import drifted: {record_id}"
            )
        source = source_records[(15, record_id)]
        canonical = source_records[(15, canonical_id)]
        if (
            tuple(x.text for x in ENGINE.parse_record_literals(source))
            != tuple(x.text for x in ENGINE.parse_record_literals(canonical))
            or COMMON.UTIL.record_gaps(source)
            != COMMON.UTIL.record_gaps(canonical)
        ):
            raise RuntimeError(
                f"segment 968 live +84 exact reuse drifted: "
                f"{canonical_id}/{record_id}"
            )
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 968 Base-to-PK mapping drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 968 Base-to-PK JP literal drifted")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != {2132, 2133}:
        raise RuntimeError("segment 968 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 968 pristine/current gap drifted")
    if any(
        sum(gap.count(ACTION_TOKEN) for gap in gaps) != 1
        for gaps in EXPECTED_BASE_GAPS.values()
    ):
        raise RuntimeError("segment 968 action-token cardinality drifted")
    if (
        raw_translations["15:2127:1"].count("…") != 1
        or translations["15:2127:1"].count("…") != 2
    ):
        raise RuntimeError("segment 968 project ellipsis pair drifted")
    joined = "\n".join(translations.values())
    for required in (
        "싸움",
        "공격",
        "공략",
        "건의",
        "시행",
        "추진",
        "참전",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 968 required meaning drifted: {required}")
    for forbidden in ("당가", "진행", "실행", "。"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 968 forbidden wording retained: {forbidden}"
            )
    if len(raw_translations) != 23 or len(translations) != 23:
        raise RuntimeError("segment 968 visible decision count drifted")


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
    if len(rows) != 23 or len(validated) != len(translations):
        raise RuntimeError("segment 968 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 968 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S968",
                "source_literal_count": 25,
                "decision_count": len(rows),
                "hidden_non_display_count": 2,
                "hidden_coordinates": EXCLUDED_NONVISIBLE_COORDINATES,
                "runtime_fragment_pending": len(rows),
                "canonical_record_map": {
                    record_id: canonical_id
                    for record_id, (_, canonical_id) in CANONICAL_RECORD_MAP.items()
                },
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [2132, 2133],
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
