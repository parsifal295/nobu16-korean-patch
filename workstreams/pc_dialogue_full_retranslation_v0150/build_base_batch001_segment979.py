#!/usr/bin/env python3
"""Build Base authoring segment 979 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment978 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S979.private.v1.jsonl"
)
SEGMENT = 979
CASTLE_TOKEN = PREVIOUS.CASTLE_TOKEN
FORCE_TOKEN = PREVIOUS.FORCE_TOKEN
VALUE_TOKEN = PREVIOUS.VALUE_TOKEN
TRANSLATIONS_BY_RECORD = {
    2251: (
        "본거지 개발이 아직 진행 중이라면\n군 개발을 추진하면서\n호기를 놓치지 않도록 유의",
    ),
    2252: (
        "아직 개발할 수 있는 성이 남아",
        "\n석고 증강도 추진하면서\n호기를 놓치지 않도록 유의",
    ),
    2253: PREVIOUS.OPPORTUNITY_WAIT_TRANSLATION,
    2254: (
        "헌언을 허락해 주시",
        "니,",
        "\n그러면 지금 해야 할 일에 관해\n",
        "의 견해를 말씀",
    ),
    2255: (
        "조금이나마 참고가 된다면 다행",
        "\n잊지 않도록 이 안을 건의해 두겠사오니\n필요하시다면",
        "참조해 ",
    ),
    2256: (
        "의 병사들이 우리 영지를 여러 차례 침범했소…\n그 성을 함락해 우환을 끊어야 한다고",
        "\n군의를 열",
        "판단해 주시기를 청하",
    ),
    2257: (
        "그 말씀을 기다리고 있",
        "!\n즉시 출병을 준비",
    ),
    2258: (
        "…알겠",
        "\n고통받는 이는 영주와 그 백성이오\n그 점을 잊지 마시기를",
    ),
    2259: (
        "거듭되는 행패…더는 용납",
        "!\n우리의 적은",
        "에 있도다\n자, 출진하리라!",
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
    2251: ("本拠の開発も未だ途上にあれば\n郡開発を進めながら\n好機を逃さぬように",),
    2252: ("まだ開発できる城も", "\n石高増強なども進めながら\n好機を逃さぬように"),
    2253: PREVIOUS.EXPECTED_BASE_JP[2248],
    2254: ("献言の", "許し、", "\nでは、今なすべきことについて\n", "の見解を申"),
    2255: ("少しでも参考になれば幸い", "\n忘れぬよう、この案を具申しておきますゆえ\n必要とあらば", "参照"),
    2256: ("の兵が我が領を侵すこと幾度…\nかの城を落とし憂いを断つべきかと", "\n軍議を開き、", "判断を願"),
    2257: ("その言を待ってお", "！\n直ちに出兵の支度を整え"),
    2258: ("…承", "\n苦しむのは領主とその民\nその事をお忘れなきよう"),
    2259: ("度重なる狼藉…堪忍な", "！\n我らが敵は", "にあり\nいざ、出陣せん！"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    2251: ("", "014394000000050505"),
    2252: ("", "014352000000", "014394000000050505"),
    2253: ("", "050505"),
    2254: ("", "014384040000", "014318010000", "014301000000", "01437E0400000143FC010000050505"),
    2255: ("", "01432C020000", "01438A040000", "014396010000050505"),
    2256: (CASTLE_TOKEN, "0143E2000000", "01438A040000", "0143BE000000050505"),
    2257: ("", "014368020000", "01431E040000050505"),
    2258: ("", "014368020000", "050505"),
    2259: ("", "01432A040000", CASTLE_TOKEN, "050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    2254: ("", "014390040000", "014318010000", "014301000000", "01438A040000014302020000050505"),
    2255: ("", "014338020000", "014396040000", "01439C010000050505"),
    2256: (CASTLE_TOKEN, "0143E2000000", "014396040000", "0143BE000000050505"),
    2257: ("", "014374020000", "01432A040000050505"),
    2258: ("", "014374020000", "050505"),
    2259: ("", "014336040000", CASTLE_TOKEN, "050505"),
}
PK_RECORD_MAP = {
    record_id: record_id + (30 if record_id <= 2253 else 31)
    for record_id in RECORD_ARITIES
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:2256:0",
    "15:2258:0",
    "15:2259:0",
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 2251): (("既然目前还在开发根据地，\n可以下令在开发郡的同时，\n也要注意不要错过好时机。",), ("", "050505")),
    ("TC", 2251): (("根據地的開發若尚未完成，\n可在開發郡的同時，\n等待好時機。",), ("", "050505")),
    ("SC", 2252): (("还有城需要开发。\n在下令增加石高的同时，\n也要注意不要错过好时机。",), ("", "050505")),
    ("TC", 2252): (("還有可以進行開發的城。\n進行增強石高等的同時，\n也別錯過好時機。",), ("", "050505")),
    ("SC", 2253): PREVIOUS.SHARED_AUXILIARY[("SC", 2248)],
    ("TC", 2253): PREVIOUS.SHARED_AUXILIARY[("TC", 2248)],
    ("SC", 2254): (("大人在烦恼什么？\n若对当下该做之事感到迷茫，\n便请听听我的建议吧。",), ("", "050505")),
    ("TC", 2254): (("大人在煩惱什麼？\n若對當下該做之事感到迷茫，\n便請聽聽我的建議吧。",), ("", "050505")),
    ("SC", 2255): (("能有参考价值便好了。\n为了备忘会作为呈报而提案。\n需要时便请参照。",), ("", "050505")),
    ("TC", 2255): (("能有參考價值便好了。\n為了備忘會作為呈報而提案。\n需要時便請參照。",), ("", "050505")),
    ("SC", 2256): (
        ("的敌兵再三侵犯吾之领地……\n看来若不攻陷该城，难绝后患。\n请召开军事会议，做出决断。",),
        (CASTLE_TOKEN, "050505"),
    ),
    ("TC", 2256): (
        ("敵兵自", "屢屢侵略我方領地……\n看來只能攻下該城，斷絕後患。\n召開軍議，請願裁斷。"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("SC", 2257): (("就是等你这句话！\n立即做好出兵的准备吧！",), ("", "050505")),
    ("TC", 2257): (("就等大人這句話！\n立刻準備出兵！",), ("", "050505")),
    ("SC", 2258): (("……明白了。\n切记，\n受苦的是领主和其百姓。",), ("", "050505")),
    ("TC", 2258): (("……遵命！\n不能忘記\n受苦的是領主和領地的人民。",), ("", "050505")),
    ("SC", 2259): (("一片狼藉……让人无法忍受！\n", "乃我等大敌！\n现在便出阵吧！"), ("", CASTLE_TOKEN, "050505")),
    ("TC", 2259): (("接連的攻擊暴行……不可饒恕！\n我們的敵人就在", "！\n立刻出陣！"), ("", CASTLE_TOKEN, "050505")),
}
PK_EN_AUXILIARY = {
    2251: (("If development at the main base is still underway, it might be the perfect time to develop the county.",), ("", "050505")),
    2252: (("There are still castles that can be developed. We shouldnÖt pass up this opportunity to increase our crop production.",), ("", "050505")),
    2253: PREVIOUS.PK_EN_AUXILIARY[2248],
    2254: (("Thank you for considering my proposal. I will now convey what I believe should be our next steps.",), ("", "050505")),
    2255: (("Please refer to this submitted proposal if it proves necessary. I would be pleased if it served some use to you.",), ("", "050505")),
    2256: (
        ("Soldiers of ", " have often trespassed upon my land. Taking the castle should put an end to this nuisance. I am ready to march on your word."),
        ("", CASTLE_TOKEN, "050505"),
    ),
    2257: (("Those are the very words I was waiting for! I will ready the soldiers at once!",), ("", "050505")),
    2258: (("Acknowledged. Remember, it is the land holders and the people who will suffer.",), ("", "050505")),
    2259: (("These repeated acts of barbarism will not be tolerated! Our enemy is ", "! Let us march!"), ("", CASTLE_TOKEN, "050505")),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B117_B_pristine_base_pc_jp_authoritative_"
    "development_opportunity_counsel_permission_proposal_submission_border_"
    "incursion_and_campaign_response_with_explicit_base2251_2253_plus30_and_"
    "base2254_2259_plus31_pk_mapping_after_pk_only_insertion_exact_base_pk_jp_"
    "sc_tc_and_actual_pk_en_context_dynamic_castle_morphology_direction_"
    "counsel_permission_not_forgiveness_proposal_as_geonui_main_base_as_"
    "bongeoji_county_development_as_gun_gaebal_crop_yield_as_seokgo_"
    "barbarism_as_haengpae_campaign_as_chulbyeong_chuljin_static2253_exact_"
    "reuse_from2248_project_ellipsis_pairs_current_line_counts_and_skeleton_"
    "preserved"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    1: ("소승", "나", "저", "소인", "이 몸"),
    82: ("있습니다", "있다", "있사옵니다", "입니다", "이옵니다"),
    148: ("하겠습니다", "하겠다", "하자"),
    190: ("있습니다", "으", "있사옵니다"),
    226: ("생각합니다", "생각한다", "생각하오", "생각하옵니다", "생각하옵나이다"),
    280: ("고마운 일", "더없이 황송하기", "고맙다", "감사합니다", "황송하오", "송구하옵니다"),
    406: ("주십시오", "해 다오", "저것", "주시오"),
    508: ("", "다"),
    556: ("입니다", "다", "이오"),
    616: ("했습니다", "었다"),
    1054: ("합시다", "듯"),
    1066: ("하지 않습니다", "않는", "않"),
    1150: ("합시다", "그렇군"),
    1156: ("오", ""),
    1162: ("고", ""),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    1: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1],
    82: EXPECTED_BASE_MORPHOLOGY_TERMINALS[82],
    148: EXPECTED_BASE_MORPHOLOGY_TERMINALS[148],
    190: EXPECTED_BASE_MORPHOLOGY_TERMINALS[190],
    226: EXPECTED_BASE_MORPHOLOGY_TERMINALS[226],
    280: EXPECTED_BASE_MORPHOLOGY_TERMINALS[280],
    412: EXPECTED_BASE_MORPHOLOGY_TERMINALS[406],
    514: EXPECTED_BASE_MORPHOLOGY_TERMINALS[508],
    568: EXPECTED_BASE_MORPHOLOGY_TERMINALS[556],
    628: EXPECTED_BASE_MORPHOLOGY_TERMINALS[616],
    1066: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1054],
    1078: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1066],
    1162: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1150],
    1168: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1156],
    1174: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1162],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if {
        record_id: PK_RECORD_MAP[record_id] - record_id
        for record_id in RECORD_ARITIES
    } != {
        **{record_id: 30 for record_id in range(2251, 2254)},
        **{record_id: 31 for record_id in range(2254, 2260)},
    }:
        raise RuntimeError("segment 979 Base-to-PK insertion-aware mapping drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 979 Base-to-PK JP literal drifted")
    pk_gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if pk_gap_divergences != {2254, 2255, 2256, 2257, 2258, 2259}:
        raise RuntimeError("segment 979 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 979 pristine/current gap drifted")
    if TRANSLATIONS_BY_RECORD[2253] is not PREVIOUS.OPPORTUNITY_WAIT_TRANSLATION:
        raise RuntimeError("segment 979 Base2248/2253 exact tuple reuse drifted")
    permission_prefixes = {
        f"{TRANSLATIONS_BY_RECORD[2254][0]}{ending}"
        f"{TRANSLATIONS_BY_RECORD[2254][1]}"
        for ending in EXPECTED_BASE_MORPHOLOGY_TERMINALS[1156]
    }
    if permission_prefixes != {
        "헌언을 허락해 주시오니,",
        "헌언을 허락해 주시니,",
    }:
        raise RuntimeError("segment 979 counsel-permission morphology drifted")
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(f"segment 979 project ellipsis pair drifted: {coordinate}")
    joined = "\n".join(translations.values())
    for required in ("본거지", "군 개발", "석고", "헌언", "허락", "건의", "행패"):
        if required not in joined:
            raise RuntimeError(f"segment 979 required terminology drifted: {required}")
    for forbidden in ("용서", "사면", "진언", "구신", "낭자", "狼藉", "。"):
        if forbidden in joined:
            raise RuntimeError(f"segment 979 forbidden wording retained: {forbidden}")
    if len(raw_translations) != 21 or len(translations) != 21:
        raise RuntimeError("segment 979 visible decision count drifted")


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
    static_row = next(row for row in rows if row["coordinate"] == "15:2253:0")
    static_row["scope_classification"] = "retranslated"
    static_row["runtime_review"] = "not_required"
    static_row["basis"] = (
        "pristine_base_pc_jp_authoritative_static_complete_literal_"
        "exact_reuse_of_base2248_opportunity_wait_translation"
    )
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(rows) != 21 or len(validated) != len(translations):
        raise RuntimeError("segment 979 validated count drifted")
    static_rows = [row for row in rows if row["coordinate"] == "15:2253:0"]
    pending_rows = [row for row in rows if row["coordinate"] != "15:2253:0"]
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
        raise RuntimeError("segment 979 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S979",
                "source_literal_count": 21,
                "decision_count": len(rows),
                "hidden_non_display_count": 0,
                "retranslated": 1,
                "runtime_fragment_pending": len(rows) - 1,
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [2254, 2255, 2256, 2257, 2258, 2259],
                "pristine_current_gap_divergence_records": [],
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
