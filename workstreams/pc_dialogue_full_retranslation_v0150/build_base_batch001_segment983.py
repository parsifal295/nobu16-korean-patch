#!/usr/bin/env python3
"""Build Base authoring segment 983 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment982 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S983.private.v1.jsonl"
)
SEGMENT = 983
DESTINATION_TOKEN = PREVIOUS.DESTINATION_TOKEN
OFFICER_TOKEN = "024633"
CASTLE_TOKEN = "026432"
UNIT_TOKEN = "029632"
FACILITY_TOKEN = "1B4349023C1B435A"
TRANSLATIONS_BY_RECORD = {
    2285: (
        "전선으로 전봉되기를 바라는 자가",
        "\n",
        "(으)로 배치해 주",
        "겠습니까?\n지략에서 역량을 발휘하게",
    ),
    2286: (
        "후방으로 전봉되기를 바라는 자가",
        "\n",
        "(으)로 배치해 주",
        "겠습니까?\n내정에서 힘을 발휘할 것으로 보입니다",
    ),
    2287: (
        "바라던 대로 영지를 옮겨 주시니\n감사의 말씀도 이루 말할 수",
        "\n우리 가문을 위해 전선에서 진력",
    ),
    2288: (
        "설마 소망이 이루어질 줄이야…\n"
        "전선에서 이 무용을 떨치며\n"
        "더욱 충근에 매진해",
    ),
    2289: (
        "오래전부터 바라던 전선의 영지\n"
        "내 목숨과 바꾸어서라도 다스리고 지키며\n"
        "찬란한 전공을 자랑",
    ),
    2290: (
        "바라던 대로 영지를 옮겨 주시니\n감사의 말씀도 이루 말할 수",
        "\n우리 가문을 위해 후방에서 진력",
    ),
    2291: (
        "설마 소망이 이루어질 줄이야…\n"
        "후방에서 정무 수완을 발휘하며\n"
        "더욱 충근에 매진해",
    ),
    2292: (
        "오래전부터 바라던 후방의 영지\n"
        "내 목숨과 바꾸어서라도 다스리고 지키며\n"
        "착실한 성과를 거두도록",
    ),
    2293: ("을(를)", "의", "(으)로 영지를 옮겼습니다"),
    2294: ("의", "을(를) 증축하여\n성하를 더욱 번성하게"),
    2295: (
        "세력 운영에 익숙해지셨을 무렵이니\n이제 조언을 줄이도록",
        "?",
    ),
    2296: (
        "게임 설정에서 가이드 건의를 끄시겠습니까?\n"
        "※나중에 언제든 변경할 수 있습니다\n"
        " (설정>시나리오>가이드 건의)\n"
        "※가이드 외의 건의는 평소대로 발생합니다",
    ),
}
EXCLUDED_NONVISIBLE_COORDINATES = {
    "15:2285:1": "\n",
    "15:2286:1": "\n",
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
    2285: (
        "前線への転封を望む者が",
        "\n",
        "へ配してや",
        "か\n知略に力を発揮してくれ",
    ),
    2286: (
        "後方への転封を望む者が",
        "\n",
        "に配してや",
        "か\n内政に力を発揮してくれるかと",
    ),
    2287: (
        "希望通りの領地変更につき\n感謝の言葉も",
        "\n当家のため、前線にて尽く",
    ),
    2288: (
        "よもや望みが叶うとは…\n"
        "前線にて我が武を振るい\n"
        "一層忠勤に励",
    ),
    2289: (
        "かねてより所望した前線の領地\n"
        "我が身に代えても治め守り\n"
        "華々しい戦働きを",
    ),
    2290: (
        "希望通りの領地変更につき\n感謝の言葉も",
        "\n当家のため、後方にて尽く",
    ),
    2291: (
        "よもや望みが叶うとは…\n"
        "後方にて我が政務の腕をもって\n"
        "一層忠勤に励",
    ),
    2292: (
        "かねてより所望した後方の領地\n"
        "我が身に代えても治め守り\n"
        "堅実なる成果を見せ",
    ),
    2293: ("を", "の", "に領地替え"),
    2294: ("の", "を増築し\n城下を充実させ"),
    2295: ("勢力の舵取りに慣れた頃合かと\nそろそろ助言を控え", "か？"),
    2296: (
        "ゲーム設定のガイド具申発生をOFFにしますか？\n"
        "※あとからいつでも変更できます\n"
        "　（設定＞シナリオ＞ガイド具申）\n"
        "※ガイド以外の具申は通常通り発生します",
    ),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    2285: (
        "",
        "0143B2000000",
        DESTINATION_TOKEN,
        "01432A040000",
        "01431E040000050505",
    ),
    2286: (
        "",
        "0143B2000000",
        DESTINATION_TOKEN,
        "01432A040000",
        "050505",
    ),
    2287: ("", "0143DA020000", "01437E040000050505"),
    2288: ("", "0143C4030000050505"),
    2289: ("", "014394000000050505"),
    2290: ("", "0143DA020000", "01437E040000050505"),
    2291: ("", "0143C4030000050505"),
    2292: ("", "01431E040000050505"),
    2293: (OFFICER_TOKEN, CASTLE_TOKEN, UNIT_TOKEN, "050505"),
    2294: (CASTLE_TOKEN, FACILITY_TOKEN, "01431E040000050505"),
    2295: ("", "01431E040000", "050505"),
    2296: ("", "050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    2285: (
        "",
        "0143B2000000",
        DESTINATION_TOKEN,
        "014336040000",
        "01432A040000050505",
    ),
    2286: (
        "",
        "0143B2000000",
        DESTINATION_TOKEN,
        "014336040000",
        "050505",
    ),
    2287: ("", "0143E6020000", "01438A040000050505"),
    2288: ("", "0143D0030000050505"),
    2289: EXPECTED_BASE_GAPS[2289],
    2290: ("", "0143E6020000", "01438A040000050505"),
    2291: ("", "0143D0030000050505"),
    2292: ("", "01432A040000050505"),
    2293: EXPECTED_BASE_GAPS[2293],
    2294: (CASTLE_TOKEN, FACILITY_TOKEN, "01432A040000050505"),
    2295: ("", "01432A040000", "050505"),
    2296: EXPECTED_BASE_GAPS[2296],
}
PK_RECORD_MAP = {record_id: record_id + 31 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {"15:2288:0", "15:2291:0"}

SHARED_AUXILIARY = {
    ("SC", 2285): (
        ("有人希望被调往前线。\n不如就配属至", "，\n发挥其谋略的才能吧。"),
        ("", DESTINATION_TOKEN, "050505"),
    ),
    ("TC", 2285): (
        ("有人自願改封至前線。\n就派至", "，\n好讓他在智略方面發揮實力吧。"),
        ("", DESTINATION_TOKEN, "050505"),
    ),
    ("SC", 2286): (
        ("有人希望被调往后方。\n不如就配属至", "，\n发挥其内政的才能吧。"),
        ("", DESTINATION_TOKEN, "050505"),
    ),
    ("TC", 2286): (
        ("有人自願改封至後方。\n就派至", "，\n好讓他在內政方面發揮實力吧。"),
        ("", DESTINATION_TOKEN, "050505"),
    ),
    ("SC", 2287): (("如愿变更领地，\n感激不尽。\n于前线效忠主家吧。",), ("", "050505")),
    ("TC", 2287): (("如願變更領地，\n感激不盡。\n於前線效忠主家吧。",), ("", "050505")),
    ("SC", 2288): (("竟能如我所愿……\n我将于前线大展身手，\n尽忠职守。",), ("", "050505")),
    ("TC", 2288): (("竟能如我所願……\n我將於前線大展身手，\n盡忠職守。",), ("", "050505")),
    ("SC", 2289): (("一直想获得的前线领地，\n将换我来治理，\n让我展现战斗的才华吧。",), ("", "050505")),
    ("TC", 2289): (("一直想獲得的前線領地，\n將換我來治理，\n讓我展現戰鬥的才華吧。",), ("", "050505")),
    ("SC", 2290): (("如愿变更领地，\n感激不尽。\n于后方效忠主家吧。",), ("", "050505")),
    ("TC", 2290): (("如願變更領地，\n感激不盡。\n於後方效忠主家吧。",), ("", "050505")),
    ("SC", 2291): (("竟能如我所愿……\n我将于后方展现政务才能，\n尽忠职守。",), ("", "050505")),
    ("TC", 2291): (("竟能如我所願……\n我將於後方展現政務才能，\n盡忠職守。",), ("", "050505")),
    ("SC", 2292): (("一直想获得的后方领地，\n将换我来治理，\n我会展现出坚实的成果的。",), ("", "050505")),
    ("TC", 2292): (("一直想獲得的後方領地，\n將換我來治理，\n我會展現出堅實的成果的。",), ("", "050505")),
    ("SC", 2293): (
        ("将", "的领地更换为", "的", "。"),
        ("", OFFICER_TOKEN, CASTLE_TOKEN, UNIT_TOKEN, "050505"),
    ),
    ("TC", 2293): (
        ("將", "的領地更換為", "的", "。"),
        ("", OFFICER_TOKEN, CASTLE_TOKEN, UNIT_TOKEN, "050505"),
    ),
    ("SC", 2294): (
        ("扩建", "的", "，\n让城下更加繁荣吧。"),
        ("", CASTLE_TOKEN, FACILITY_TOKEN, "050505"),
    ),
    ("TC", 2294): (
        ("增築", "的", "，\n充實城下。"),
        ("", CASTLE_TOKEN, FACILITY_TOKEN, "050505"),
    ),
    ("SC", 2295): (
        ("应该已经适应了当势力的领袖吧，\n准备好面对\n关于进展的建议了吗？",),
        ("", "050505"),
    ),
    ("TC", 2295): (
        ("已經熟悉該如何掌控勢力了，\n今後就減少進行相關的建議吧？",),
        ("", "050505"),
    ),
    ("SC", 2296): (
        (
            "要将游戏设定的指引呈报发生设定为OFF吗？\n"
            "　※之后也能随时变更\n"
            "　　（设定＞剧本＞指引呈报）\n"
            "　※指引以外的呈报正常发生",
        ),
        ("", "050505"),
    ),
    ("TC", 2296): (
        (
            "要將遊戲設定的指引呈報發生設定為OFF嗎？\n"
            "　※之後也能隨時變更\n"
            "　　（設定＞劇本＞指引呈報）\n"
            "　※指引以外的呈報正常發生",
        ),
        ("", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    2285: (
        (
            "There is an officer wishing to be relocated to the front lines. ",
            " could use a boost in intelligence, so why not assign them there?",
        ),
        ("", DESTINATION_TOKEN, "050505"),
    ),
    2286: (
        (
            "There is an officer wishing to be relocated to the rear. ",
            " could use a boost in political ability, so why not assign them there?",
        ),
        ("", DESTINATION_TOKEN, "050505"),
    ),
    2287: (
        (
            "I want to thank you for considering my preferences in placement. "
            "I will give my all on the front lines.",
        ),
        ("", "050505"),
    ),
    2288: (
        (
            "My wishes have been answered! My unwavering loyalty shall be known "
            "by my valor on the front lines!",
        ),
        ("", "050505"),
    ),
    2289: (
        ("Finally, a domain on the front lines! I shall defend it in glorious combat.",),
        ("", "050505"),
    ),
    2290: (
        (
            "I want to thank you for considering my preferences in placement. "
            "I will give my all supporting the clan from the back lines.",
        ),
        ("", "050505"),
    ),
    2291: (
        (
            "My wishes have been answered! My unwavering loyalty shall be known "
            "by my political support from the rear!",
        ),
        ("", "050505"),
    ),
    2292: (
        (
            "Finally, a domain on the back lines! I shall devote myself wholly "
            "to its defense and governance.",
        ),
        ("", "050505"),
    ),
    2293: (
        (" has been transferred to ", "Ös ", "."),
        (OFFICER_TOKEN, CASTLE_TOKEN, UNIT_TOKEN, "050505"),
    ),
    2294: (
        ("LetÖs further improve ", " by constructing its ", "."),
        ("", CASTLE_TOKEN, FACILITY_TOKEN, "050505"),
    ),
    2295: (
        (
            "It seems like youÖve gotten a good hold on commanding the clan. "
            "I expect youÖll no longer require my counsel.",
        ),
        ("", "050505"),
    ),
    2296: (
        (
            "Turn off guide submissions?\n"
            "*This setting can be changed at any time.\n"
            "(Settings>Scenario>Guide Submissions)\n"
            "*Submissions unrelated to the guide will still be provided.",
        ),
        ("", "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B118_A_pristine_base_pc_jp_authoritative_"
    "front_rear_tenpo_responses_domain_transfer_castle_town_expansion_"
    "guide_submission_ui_with_explicit_base2285_2296_to_pk2316_2327_"
    "plus31_mapping_exact_base_pk_jp_sc_tc_literals_actual_pk_en_"
    "auxiliary_context_kotobank_dictionary_tenpo_chukin_tokeya_hanto_"
    "period_meanings_officer_castle_destination_facility_token_direction_"
    "two_hidden_lf_literals_morphology_terminal_corpora_current_line_"
    "counts_ellipsis_pairs_and_protected_skeleton_preserved_runtime_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    148: ("하겠습니다", "하겠다", "하자"),
    178: ("있습니다", "있다", "있사옵니다"),
    730: ("없습니다", "없다", "없소", "아닙니다", "아니옵니다"),
    964: ("봅시다", "이제"),
    1054: ("합시다", "듯"),
    1066: ("하지 않습니다", "않는", "않"),
    1150: ("합시다", "그렇군"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    148: EXPECTED_BASE_MORPHOLOGY_TERMINALS[148],
    178: EXPECTED_BASE_MORPHOLOGY_TERMINALS[178],
    742: EXPECTED_BASE_MORPHOLOGY_TERMINALS[730],
    976: EXPECTED_BASE_MORPHOLOGY_TERMINALS[964],
    1066: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1054],
    1078: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1066],
    1162: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1150],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {31}:
        raise RuntimeError("segment 983 Base-to-PK mapping drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 983 Base-to-PK JP literal drifted")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != {
        2285,
        2286,
        2287,
        2288,
        2290,
        2291,
        2292,
        2294,
        2295,
    }:
        raise RuntimeError("segment 983 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 983 pristine/current gap drifted")
    if (
        EXPECTED_BASE_GAPS[2285][2] != DESTINATION_TOKEN
        or EXPECTED_BASE_GAPS[2286][2] != DESTINATION_TOKEN
        or EXPECTED_BASE_GAPS[2293][:3]
        != (OFFICER_TOKEN, CASTLE_TOKEN, UNIT_TOKEN)
        or EXPECTED_BASE_GAPS[2294][:2] != (CASTLE_TOKEN, FACILITY_TOKEN)
    ):
        raise RuntimeError("segment 983 dynamic token direction drifted")
    if SUPPORT.morphology_operands(EXPECTED_BASE_GAPS[2285][3]) != (1066,):
        raise RuntimeError("segment 983 negative proposal morphology drifted")
    if SUPPORT.morphology_operands(EXPECTED_BASE_GAPS[2285][4]) != (1054,):
        raise RuntimeError("segment 983 ability proposal morphology drifted")
    joined = "\n".join(translations.values())
    for required in (
        "전봉",
        "충근",
        "전공",
        "정무",
        "우리 가문",
        "성하",
        "가이드 건의",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 983 terminology drifted: {required}")
    for forbidden in ("당가", "영지 교체", "。", "！", "？"):
        if forbidden in joined:
            raise RuntimeError(f"segment 983 forbidden wording retained: {forbidden}")
    if (
        raw_translations["15:2289:0"].replace("전선", "후방")
        != raw_translations["15:2292:0"].replace("착실한 성과를 거두도록", "찬란한 전공을 자랑")
    ):
        raise RuntimeError("segment 983 front/rear domain response frame drifted")
    if set(EXCLUDED_NONVISIBLE_COORDINATES) != {"15:2285:1", "15:2286:1"}:
        raise RuntimeError("segment 983 hidden LF coordinate drifted")
    if len(raw_translations) != 22 or len(translations) != 22:
        raise RuntimeError("segment 983 visible decision count drifted")


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
    if len(rows) != 22 or len(validated) != len(translations):
        raise RuntimeError("segment 983 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 983 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S983",
                "source_literal_count": sum(RECORD_ARITIES.values()),
                "decision_count": len(rows),
                "hidden_non_display_count": len(EXCLUDED_NONVISIBLE_COORDINATES),
                "runtime_fragment_pending": len(rows),
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [
                    record_id
                    for record_id in RECORD_ARITIES
                    if EXPECTED_BASE_GAPS[record_id]
                    != EXPECTED_PK_JP_GAPS[record_id]
                ],
                "pristine_current_gap_divergence_records": [],
                "lf_count": sum(text.count("\n") for text in translations.values()),
                "line_distribution": {
                    line_count: sum(
                        text.count("\n") + 1 == line_count
                        for text in translations.values()
                    )
                    for line_count in (1, 2, 3, 4)
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
