#!/usr/bin/env python3
"""Build Base authoring segment 978 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment977 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S978.private.v1.jsonl"
)
SEGMENT = 978
CASTLE_TOKEN = PREVIOUS.CASTLE_TOKEN
FORCE_TOKEN = PREVIOUS.FORCE_TOKEN
ALLY_FORCE_TOKEN = "025132"
OUR_VALUE_TOKEN = "023D"
VALUE_TOKEN = PREVIOUS.VALUE_TOKEN
OPPORTUNITY_WAIT_TRANSLATION = (
    "이제는 유능한 무장을 찾는 등\n호기를 기다릴 뿐입니다",
)
TRANSLATIONS_BY_RECORD = {
    2240: (
        "전황은 우리 쪽이 우세합니다. ",
        "\n우선 눈앞의 싸움에서 승리를 거두고\n착실히 판도를 넓혀 나갑시다.",
    ),
    2241: (
        "전황은 결코 우세하다고 할 수 없습니다. ",
        "\n피해가 커질 듯하다면\n물러날 때를 가늠하는 것도 긴요합니다.",
    ),
    2242: (
        "다음 목표로 삼아야 할 곳은",
        "\n현재 적 병력은",
        "이며\n아군 병력은",
    ),
    2243: (
        "적에게는 우호 세력이 없으니\n원군을 부를 걱정도",
    ),
    2244: (
        "이(가) 적의 편에 붙어",
        "\n쳐들어갈 때는 원군을 경계하",
        "주의해 ",
    ),
    2245: (
        "을(를) 비롯한",
        "개 세력이\n적의 편에 붙어",
        "\n쳐들어갈 때는 원군을 경계하",
        "주의해 ",
    ),
    2246: (
        "본거지 개발이 아직 끝나지 않았다면\n군 개발을 명해 보시는 게 어떻겠습니까?",
    ),
    2247: (
        "아직 개발할 성이 남아 있습니다. ",
        "\n석고 증강을 명해 보시는 게 어떻겠습니까?",
    ),
    2248: OPPORTUNITY_WAIT_TRANSLATION,
    2249: (
        "외교 관계상, 지금은 어느 인접 세력도\n침공할 수 없",
    ),
    2250: (
        "그러나 병력",
        "의",
        "에 대해서는\n외교 관계가 바뀔 때\n다음 목표로 삼는 것도 고려해 주십시오",
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
    2240: ("戦況はこちらが優勢", "\nまずは目下の戦いで勝利を収め\n着実に版図を広げ"),
    2241: ("戦況は決して優勢とは言え", "\n損害が大きくなるようであれば\n引き際を見極めることも肝心"),
    2242: ("次の目標とするべきは", "\n現在、敵方の兵力", "に対し\n我が方の兵力は"),
    2243: ("味方はおらず\n援軍を呼ばれる心配も",),
    2244: ("が味方について", "\n攻め入る際は援軍に", "注意"),
    2245: ("など", "勢力を\n味方につけて", "\n攻め入る際は援軍に", "注意"),
    2246: ("本拠の開発も未だ途上にあれば\n郡開発を命じてみては",),
    2247: ("まだ開発できる城も", "\n石高増強を命じてみては"),
    2248: ("あとは有能な武将を探すなどして\n好機を待つばかり",),
    2249: ("外交の関係上、今はいずれの隣接勢力にも\n侵攻することができ",),
    2250: ("しかし兵力", "の", "については\n外交関係が変化したときに\n次の目標とすることもご一考を"),
}
EXPECTED_PK_JP = {
    **EXPECTED_BASE_JP,
    2243: ("また、", "に味方する家はなく\n援軍を呼ばれる心配は"),
    2244: ("また、", "は\n", "を味方につけて", "\n攻め入る際は援軍に", "注意"),
    2245: ("また、", "は\n", "など", "勢力を味方につけて", "\n攻め入る際は援軍に", "注意"),
}
EXPECTED_BASE_GAPS = {
    2240: ("", "014326020000", "01431E040000050505"),
    2241: ("", "0143E0020000", "01432C020000050505"),
    2242: ("", f"{FORCE_TOKEN}014356020000", "023C", f"{OUR_VALUE_TOKEN}014326020000050505"),
    2243: ("", "0143DA020000050505"),
    2244: (ALLY_FORCE_TOKEN, "0143B2000000", "01438A040000", "014396010000050505"),
    2245: (ALLY_FORCE_TOKEN, VALUE_TOKEN, "0143B2000000", "01438A040000", "014396010000050505"),
    2246: ("", "0143B0020000014356020000050505"),
    2247: ("", "014352000000", "0143B0020000014356020000050505"),
    2248: ("", "050505"),
    2249: ("", "0143E0020000050505"),
    2250: ("", "023C", FORCE_TOKEN, "050505"),
}
EXPECTED_CURRENT_GAPS = {
    **EXPECTED_BASE_GAPS,
    2240: ("", "", "050505"),
    2241: ("", "", "050505"),
    2246: ("", "050505"),
    2247: ("", "", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    2240: ("", "014332020000", "01432A040000050505"),
    2241: ("", "0143EC020000", "014338020000050505"),
    2242: ("", f"{FORCE_TOKEN}014362020000", "023C", f"{OUR_VALUE_TOKEN}014332020000050505"),
    2243: ("", FORCE_TOKEN, "0143F2020000050505"),
    2244: ("", FORCE_TOKEN, ALLY_FORCE_TOKEN, "0143B2000000", "014396040000", "01439C010000050505"),
    2245: ("", FORCE_TOKEN, ALLY_FORCE_TOKEN, VALUE_TOKEN, "0143B2000000", "014396040000", "01439C010000050505"),
    2246: ("", "0143BC020000014362020000050505"),
    2247: ("", "014352000000", "0143BC020000014362020000050505"),
    2249: ("", "0143EC020000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 2240): (("战况为我方优势，\n先以眼下的胜利为目标，\n一点点扩大版图吧。",), ("", "050505")),
    ("TC", 2240): (("目前的戰況是我方佔優勢。\n先設法贏得眼前的戰爭，\n再逐步地擴大版圖吧。",), ("", "050505")),
    ("SC", 2241): (("战况绝不能说是处于优势，\n在损失扩大前\n务必掌握好撤退的时机。",), ("", "050505")),
    ("TC", 2241): (("目前的戰況並不樂觀。\n在損害擴大之前，\n務必掌握好撤退的時機。",), ("", "050505")),
    ("SC", 2242): (
        ("应该把", "作为下一个目标，\n目前，相对于", "敌方兵力，\n我方的兵力为", "。"),
        ("", FORCE_TOKEN, "023C", OUR_VALUE_TOKEN, "050505"),
    ),
    ("TC", 2242): (
        ("下個目標是", "，\n目前敵方的兵力為", "，\n而我方則是", "。"),
        ("", FORCE_TOKEN, "023C", OUR_VALUE_TOKEN, "050505"),
    ),
    ("SC", 2246): (("既然目前还在开发根据地，\n下令开发郡如何？",), ("", "050505")),
    ("TC", 2246): (("若根據地的開發尚未完成，\n不妨下令開發郡如何？",), ("", "050505")),
    ("SC", 2247): (("尚有可进行开始的城。\n不妨下令增加石高如何。",), ("", "050505")),
    ("TC", 2247): (("尚有可進行開發的城。\n不妨下令增強石高如何？",), ("", "050505")),
    ("SC", 2248): (("接下来便是寻找有能力的武将，\n等待好时机了。",), ("", "050505")),
    ("TC", 2248): (("接著，只須尋找有能力的武將，\n等待佳機了。",), ("", "050505")),
    ("SC", 2249): (("从外交关系上来说，己方现在\n无法进攻周围任何一个势力。",), ("", "050505")),
    ("TC", 2249): (("從外交關係上來說，目前我們無法對\n周邊的任何勢力發動進攻。",), ("", "050505")),
    ("SC", 2250): (
        ("不过，就以兵力", "的", "，\n考虑到外交姿态可能发生变化，\n可以考虑将其作为下一个目标。"),
        ("", "023C", FORCE_TOKEN, "050505"),
    ),
    ("TC", 2250): (
        ("不過，就兵力", "的", "來看，\n只要外交關係發生變化，\n也有可能將其做為下一個目標。"),
        ("", "023C", FORCE_TOKEN, "050505"),
    ),
}
PK_EN_AUXILIARY = {
    2240: (("We have the advantage. Let us take our certain victory and expand our territory.",), ("", "050505")),
    2241: (("We clearly lack the advantage. It is important that we pull out before our losses grow too great.",), ("", "050505")),
    2242: (
        ("I believe the ", " should be our next target. At present, our ", " soldiers are up against their ", "."),
        ("", FORCE_TOKEN, OUR_VALUE_TOKEN, "023C", "050505"),
    ),
    2243: (("There is no need to worry about reinforcements; the ", " clan have no allies."), ("", FORCE_TOKEN, "050505")),
    2244: (("TheyÖre allied with the ", ". We should be cautious of them calling for reinforcements."), ("", ALLY_FORCE_TOKEN, "050505")),
    2245: (
        ("The ", " clan have ", " allies, including the ", ". We must be careful should they call for reinforcements."),
        ("", FORCE_TOKEN, VALUE_TOKEN, ALLY_FORCE_TOKEN, "050505"),
    ),
    2246: (("If development at the main base is still underway, why donÖt we order the countyÖs development?",), ("", "050505")),
    2247: (("There are still castles in need of development. I believe we should order the crops to be increased.",), ("", "050505")),
    2248: (("IÖm just waiting for the opportunity to find a talented officer.",), ("", "050505")),
    2249: (("Due to our diplomatic connections, we are unable to invade any of the adjacent clans.",), ("", "050505")),
    2250: (
        ("But should our diplomatic relationship change, the ", " with their ", " soldiers could be considered a good target."),
        ("", FORCE_TOKEN, "023C", "050505"),
    ),
}
AUXILIARY_OVERRIDES = {
    **SUPPORT.make_auxiliary_overrides(SHARED_AUXILIARY, PK_EN_AUXILIARY),
    ("base", "SC", 2243): (("因为没有友军，\n就无需担心呼叫援军。",), ("", "050505")),
    ("base", "TC", 2243): (("對方並無友軍，\n應無需擔心援軍的問題。",), ("", "050505")),
    ("pk", "SC", 2243): (("而且，", "没有友军，\n就无需担心呼叫援军。"), ("", FORCE_TOKEN, "050505")),
    ("pk", "TC", 2243): (("而且，", "並無友軍，\n應無需擔心援軍的問題。"), ("", FORCE_TOKEN, "050505")),
    ("base", "SC", 2244): (("是敌方的友军，\n攻进敌阵时要小心援军。",), (ALLY_FORCE_TOKEN, "050505")),
    ("base", "TC", 2244): (("敵方有", "作為友軍，\n進攻時要小心援軍。"), ("", ALLY_FORCE_TOKEN, "050505")),
    ("pk", "SC", 2244): (("而且，", "是", "的友军，\n攻进敌阵时要小心援军。"), ("", ALLY_FORCE_TOKEN, FORCE_TOKEN, "050505")),
    ("pk", "TC", 2244): (("而且，", "有", "作為友軍，\n進攻時要小心援軍。"), ("", FORCE_TOKEN, ALLY_FORCE_TOKEN, "050505")),
    ("base", "SC", 2245): (("等", "势力是敌方的友军，\n攻进敌阵时要小心援军。"), (ALLY_FORCE_TOKEN, VALUE_TOKEN, "050505")),
    ("base", "TC", 2245): (("敵方有", "等", "勢力作為友軍，\n進攻時要小心援軍。"), ("", ALLY_FORCE_TOKEN, VALUE_TOKEN, "050505")),
    ("pk", "SC", 2245): (("而且，", "等", "势力\n是", "的友军，\n攻进敌阵时要小心援军。"), ("", ALLY_FORCE_TOKEN, VALUE_TOKEN, FORCE_TOKEN, "050505")),
    ("pk", "TC", 2245): (("而且，", "有\n", "等", "勢力作為友軍，\n進攻時要小心援軍。"), ("", FORCE_TOKEN, ALLY_FORCE_TOKEN, VALUE_TOKEN, "050505")),
}
BASIS = (
    "review_queue_base_msggame_B117_B_pristine_base_pc_jp_authoritative_"
    "strategic_advantage_target_selection_reinforcements_main_base_county_"
    "development_crop_yield_and_diplomatic_targeting_with_explicit_base2240_"
    "2250_to_pk2270_2280_mapping_actual_base_pk_sc_tc_and_pk_en_context_"
    "base_authoritative_2243_2245_pk_literal_expansion_recorded_dynamic_force_"
    "ally_force_value_and_troop_value_direction_version_map_and_current2240_"
    "2241_2246_2247_flattened_skeleton_recorded_territory_as_pando_main_base_"
    "as_bongeoji_county_development_as_gun_gaebal_crop_yield_as_seokgo_"
    "reinforcements_as_wongun_examples_as_deung_static2248_exact_complete_"
    "current_line_counts_and_outer_whitespace_preserved"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    178: ("있습니다", "있다", "있사옵니다"),
    406: ("주십시오", "해 다오", "저것", "주시오"),
    550: ("입니다", "다", "이오", "이옵니다"),
    598: ("이겠지요", "이리라", "이겠지"),
    730: ("없습니다", "없다", "없소", "아닙니다", "아니옵니다"),
    736: ("않습니다", "않는다"),
    1162: ("고", ""),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    82: ("있습니다", "있다", "있사옵니다", "입니다", "이옵니다"),
    178: EXPECTED_BASE_MORPHOLOGY_TERMINALS[178],
    412: EXPECTED_BASE_MORPHOLOGY_TERMINALS[406],
    562: EXPECTED_BASE_MORPHOLOGY_TERMINALS[550],
    568: ("입니다", "다", "이오"),
    610: EXPECTED_BASE_MORPHOLOGY_TERMINALS[598],
    700: ("어떻게", "어떠하오"),
    748: EXPECTED_BASE_MORPHOLOGY_TERMINALS[736],
    754: ("없습니다", "없다", "없사옵니다"),
    1066: ("합시다", "듯"),
    1174: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1162],
}
MORPHOLOGY_PK_GAPS = {
    **EXPECTED_PK_JP_GAPS,
    # PK expands these Base records with leading literals. Re-align only the
    # morphology evidence gaps to the corresponding Base-authored literals.
    2243: ("", "0143F2020000050505"),
    2244: ("", "0143B2000000", "014396040000", "01439C010000050505"),
    2245: ("", VALUE_TOKEN, "0143B2000000", "014396040000", "01439C010000050505"),
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 978 Base-to-PK mapping drifted")
    literal_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_JP[record_id] != EXPECTED_PK_JP[record_id]
    }
    if literal_divergences != {2243, 2244, 2245}:
        raise RuntimeError("segment 978 Base-to-PK literal divergence drifted")
    pk_gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if pk_gap_divergences != {2240, 2241, 2242, 2243, 2244, 2245, 2246, 2247, 2249}:
        raise RuntimeError("segment 978 Base-to-PK gap divergence drifted")
    current_gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_CURRENT_GAPS[record_id]
    }
    if current_gap_divergences != {2240, 2241, 2246, 2247}:
        raise RuntimeError("segment 978 pristine/current gap divergence drifted")
    if TRANSLATIONS_BY_RECORD[2248] is not OPPORTUNITY_WAIT_TRANSLATION:
        raise RuntimeError("segment 978 static opportunity tuple reuse drifted")
    joined = "\n".join(translations.values())
    for required in ("판도", "원군", "본거지", "군 개발", "석고", "등"):
        if required not in joined:
            raise RuntimeError(f"segment 978 required terminology drifted: {required}")
    for forbidden in ("세력권", "지원군", "근거지", "군락 개발", "따위", "。"):
        if forbidden in joined:
            raise RuntimeError(f"segment 978 forbidden wording retained: {forbidden}")
    if not TRANSLATIONS_BY_RECORD[2250][2].endswith("고려해 주십시오"):
        raise RuntimeError("segment 978 diplomatic-target counsel became incomplete")
    if len(raw_translations) != 23 or len(translations) != 23:
        raise RuntimeError("segment 978 visible decision count drifted")


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
        pk_gaps=MORPHOLOGY_PK_GAPS,
        expected_base=EXPECTED_BASE_MORPHOLOGY_TERMINALS,
        expected_pk=EXPECTED_PK_MORPHOLOGY_TERMINALS,
    )
    static_row = next(row for row in rows if row["coordinate"] == "15:2248:0")
    static_row["scope_classification"] = "retranslated"
    static_row["runtime_review"] = "not_required"
    static_row["basis"] = (
        "pristine_base_pc_jp_authoritative_static_complete_literal_"
        "exact_canonical_opportunity_wait_translation"
    )
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(rows) != 23 or len(validated) != len(translations):
        raise RuntimeError("segment 978 validated count drifted")
    static_rows = [row for row in rows if row["coordinate"] == "15:2248:0"]
    pending_rows = [row for row in rows if row["coordinate"] != "15:2248:0"]
    if (
        len(static_rows) != 1
        or static_rows[0]["scope_classification"] != "retranslated"
        or static_rows[0]["runtime_review"] != "not_required"
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
        raise RuntimeError("segment 978 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S978",
                "source_literal_count": 23,
                "decision_count": len(rows),
                "hidden_non_display_count": 0,
                "retranslated": 1,
                "runtime_fragment_pending": len(rows) - 1,
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [2243, 2244, 2245],
                "base_pk_jp_gap_divergence_records": [
                    2240,
                    2241,
                    2242,
                    2243,
                    2244,
                    2245,
                    2246,
                    2247,
                    2249,
                ],
                "pristine_current_gap_divergence_records": [2240, 2241, 2246, 2247],
                "lf_count": sum(text.count("\n") for text in translations.values()),
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
