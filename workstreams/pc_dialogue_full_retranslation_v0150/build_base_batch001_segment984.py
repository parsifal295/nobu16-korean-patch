#!/usr/bin/env python3
"""Build Base authoring segment 984 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment983 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S984.private.v1.jsonl"
)
SEGMENT = 984
SUPPORT_FORCE_TOKEN = "025A32"
ACKNOWLEDGEMENT = "명심"
CASTLE_GOAL_TRANSLATION = (
    "우리 가문의 목표로\n지배하에 둔 성을 늘리자고\n내거는 것은",
)
TRANSLATIONS_BY_RECORD = {
    2297: (ACKNOWLEDGEMENT, "\n필요하시다면 언제든 명을 내려"),
    2298: (
        ACKNOWLEDGEMENT,
        "\n조언이 필요 없게 되면\n언제든 지시를 바꾸어",
    ),
    2299: (
        "의 군단은\n"
        "인재 운용이 다소 빠듯하여…\n"
        "전투에 능한 장수가 필요한 상태",
    ),
    2300: (
        "우리 군단에는 전투에 능한 장수 자리가\n비어",
        "\n배속을 검토해",
    ),
    2301: (
        "가능하면 전투에 능한 장수를\n우리 군단에 배속하기를 희망",
        "\n여러모로 일손이 부족하여…",
    ),
    2302: (
        "의 군단은\n"
        "인재 운용이 다소 빠듯하여…\n"
        "정무에 능한 장수가 필요한 상태",
    ),
    2303: (
        "우리 군단에는 정무에 능한 장수 자리가\n비어",
        "\n배속을 검토해",
    ),
    2304: (
        "가능하면 정무에 능한 장수를\n우리 군단에 배속하기를 희망",
        "\n여러모로 일손이 부족하여…",
    ),
    2305: (
        "우리 군단의 공세를 강화하고자\n",
        "의 지원을\n부디 청하고자 합니다",
    ),
    2306: (
        "승기가 찾아왔으니,",
        "을(를)\n우리 군단의 지원으로 돌려\n승부수를 띄우게 해",
    ),
    2307: (
        "머지않아 우리 군단도 공세로 나서고자 하니\n",
        "에게\n우리를 원호하도록 명할 수",
        "?",
    ),
    2308: CASTLE_GOAL_TRANSLATION,
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
    2297: ("承知し", "\n必要とあらば、いつでも指示を"),
    2298: ("承知し", "\n助言が不要になった時は\nいつでも指示を変更して"),
    2299: ("の軍団にて\nいささか人繰りが苦しく…\n戦に長けた将が必要",),
    2300: ("我が軍団にて戦に長けた将が\n不足して", "\n配属を検討して"),
    2301: ("なるべく戦に長けた将の\n我が軍団への配属を希望", "\n人手がなにかと足らず…"),
    2302: ("の軍団にて\nいささか人繰りが苦しく…\n政に長けた将が必要",),
    2303: ("我が軍団にて政に長けた将が\n不足して", "\n配属を検討して"),
    2304: ("なるべく政に長けた将の\n我が軍団への配属を希望", "\n人手がなにかと足らず…"),
    2305: ("我が軍団による攻勢を強めるため\n", "による支援を\nどうかお願いしたく"),
    2306: ("勝機到来、", "を\n我が軍団の支援に回し\n勝負に出させて"),
    2307: ("近々、我が軍団も攻めに転じたく\n", "に\n我らの援護を命じて頂け", "か"),
    2308: ("当家の目標として\n支配下にある城の増加を\n掲げては",),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    2297: ("", "014314020000", "014342010000050505"),
    2298: ("", "014314020000", "014342010000050505"),
    2299: ("014301000000", "01432C020000050505"),
    2300: ("", "0143B2000000", "014342010000050505"),
    2301: ("", "0143CC010000", "050505"),
    2302: ("014301000000", "01432C020000050505"),
    2303: ("", "0143B2000000", "014342010000050505"),
    2304: ("", "0143CC010000", "050505"),
    2305: ("", SUPPORT_FORCE_TOKEN, "050505"),
    2306: ("", SUPPORT_FORCE_TOKEN, "014342010000050505"),
    2307: ("", SUPPORT_FORCE_TOKEN, "0143DA020000", "050505"),
    2308: ("", "0143B0020000014356020000050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    2297: ("", "01431A020000", "014342010000050505"),
    2298: ("", "01431A020000", "014342010000050505"),
    2299: ("014301000000", "014338020000050505"),
    2300: EXPECTED_BASE_GAPS[2300],
    2301: ("", "0143D2010000", "050505"),
    2302: ("014301000000", "014338020000050505"),
    2303: EXPECTED_BASE_GAPS[2303],
    2304: ("", "0143D2010000", "050505"),
    2305: EXPECTED_BASE_GAPS[2305],
    2306: EXPECTED_BASE_GAPS[2306],
    2307: ("", SUPPORT_FORCE_TOKEN, "0143E6020000", "050505"),
    2308: ("", "0143BC020000014362020000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 31 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:2299:0",
    "15:2301:1",
    "15:2302:0",
    "15:2304:1",
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}

SHARED_AUXILIARY = {
    ("SC", 2297): (("明白了。\n有需要的话，请随时指示。",), ("", "050505")),
    ("TC", 2297): (("明白了。\n有需要的話，請隨時指示。",), ("", "050505")),
    ("SC", 2298): (
        ("明白了。\n即使不等待呈报，如果不需要建议，\n可以随时调整指示。",),
        ("", "050505"),
    ),
    ("TC", 2298): (
        ("是！\n若認為無需建議時無須等到呈報，\n請隨時變更指示。",),
        ("", "050505"),
    ),
    ("SC", 2299): (
        ("的军团\n多少有些人才匮乏……\n需要些擅战的将领。",),
        ("014301000000", "050505"),
    ),
    ("TC", 2299): (
        ("的軍團有點缺乏人才……\n需要擅於戰鬥的將領。",),
        ("014301000000", "050505"),
    ),
    ("SC", 2300): (
        ("我的军团中缺乏\n擅于战斗的将领。\n请考虑配置。",),
        ("", "050505"),
    ),
    ("TC", 2300): (
        ("我的軍團中缺乏\n擅於戰鬥的將領。\n請考慮配置。",),
        ("", "050505"),
    ),
    ("SC", 2301): (
        ("热切希望擅于战斗的将领\n能配置到我的军团里，\n人手有些不足……",),
        ("", "050505"),
    ),
    ("TC", 2301): (
        ("熱切希望擅於戰鬥的將領\n能配置到我的軍團裡，\n人手有些不足……",),
        ("", "050505"),
    ),
    ("SC", 2302): (
        ("的军团\n有点缺乏人才……\n需要擅于政务的将领。",),
        ("014301000000", "050505"),
    ),
    ("TC", 2302): (
        ("的軍團\n有點缺乏人才……\n需要擅於政務的將領。",),
        ("014301000000", "050505"),
    ),
    ("SC", 2303): (
        ("我的军团中缺乏\n擅于政务的将领。\n请考虑配置。",),
        ("", "050505"),
    ),
    ("TC", 2303): (
        ("我的軍團中缺乏\n擅於政務的將領。\n請考慮配置。",),
        ("", "050505"),
    ),
    ("SC", 2304): (
        ("热切希望擅于政务的将领\n能配置到我的军团里，\n人手有些不足……",),
        ("", "050505"),
    ),
    ("TC", 2304): (
        ("熱切希望擅於政務的將領\n能配置到我的軍團裡，\n人手有些不足……",),
        ("", "050505"),
    ),
    ("SC", 2305): (
        ("臣认为，为了让我军团的战况好转，\n应请求", "的支援。"),
        ("", SUPPORT_FORCE_TOKEN, "050505"),
    ),
    ("TC", 2305): (
        ("臣認為，為了讓我軍團的戰況好轉，\n應請求", "的支援。"),
        ("", SUPPORT_FORCE_TOKEN, "050505"),
    ),
    ("SC", 2306): (
        ("胜机已至，务必请求", "\n支援我军团，一定胜负。"),
        ("", SUPPORT_FORCE_TOKEN, "050505"),
    ),
    ("TC", 2306): (
        ("勝機已至，務必請求", "\n支援我軍團，一定勝負。"),
        ("", SUPPORT_FORCE_TOKEN, "050505"),
    ),
    ("SC", 2307): (
        ("为了巩固胜利，\n将", "的方针\n变更为支援我军团，如何？"),
        ("", SUPPORT_FORCE_TOKEN, "050505"),
    ),
    ("TC", 2307): (
        ("為了鞏固勝利，\n將", "的方針\n變更為支援我軍團，如何？"),
        ("", SUPPORT_FORCE_TOKEN, "050505"),
    ),
    ("SC", 2308): (
        ("将增加的受掌控之城数量，\n作为本家的目标，\n公布于众如何？",),
        ("", "050505"),
    ),
    ("TC", 2308): (
        ("以增加支配城數\n作為本家的目標如何？ ",),
        ("", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    2297: (
        ("Understood. Should you require my assistance, I am always at your command.",),
        ("", "050505"),
    ),
    2298: (
        (
            "Understood. Of course, you can change your mind whenever you feel "
            "my advice has become unnecessary.",
        ),
        ("", "050505"),
    ),
    2299: (
        (
            "IÖve had some difficulty making do with so few people. I need an "
            "officer with plenty of battlefield experience.",
        ),
        ("", "050505"),
    ),
    2300: (
        (
            "My province lacks officers experienced in battle. Would you "
            "consider posting one here?",
        ),
        ("", "050505"),
    ),
    2301: (
        (
            "IÖd like to have officers with battlefield experience in my "
            "province. As of now, we lack sufficient manpower.",
        ),
        ("", "050505"),
    ),
    2302: (
        (
            "IÖve had some difficulty making do with so few people. I need an "
            "officer with plenty of political acumen.",
        ),
        ("", "050505"),
    ),
    2303: (
        (
            "My province lacks officers experienced in politics. Would you "
            "consider posting one here?",
        ),
        ("", "050505"),
    ),
    2304: (
        (
            "IÖd like to have officers with political experience in my "
            "province. As of now, we lack sufficient manpower.",
        ),
        ("", "050505"),
    ),
    2305: (
        (
            "Could I ask that you send ",
            " to assist in strengthening my provinceÖs offensive capabilities?",
        ),
        ("", SUPPORT_FORCE_TOKEN, "050505"),
    ),
    2306: (
        ("The time for victory is upon us. Please send ", " to assist my province."),
        ("", SUPPORT_FORCE_TOKEN, "050505"),
    ),
    2307: (
        ("My province wants a taste of the action too. Please allow us to back up ", "."),
        ("", SUPPORT_FORCE_TOKEN, "050505"),
    ),
    2308: (
        (
            "What do you think of setting a goal of increasing the number of "
            "castles under our clanÖs control?",
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
    "guide_advice_replies_corps_staffing_battle_and_political_officer_"
    "assignment_support_requests_and_clan_castle_goal_with_explicit_"
    "base2297_2308_to_pk2328_2339_plus31_mapping_exact_base_pk_jp_sc_"
    "tc_literals_actual_pk_en_auxiliary_context_kotobank_toke_"
    "period_house_meaning_personnel_assignment_offensive_support_and_"
    "025a32_force_token_direction_actual_morphology_terminal_corpora_"
    "current_line_counts_ellipsis_pairs_and_protected_skeleton_preserved_"
    "runtime_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    1: ("소승", "나", "저", "소인", "이 몸"),
    178: ("있습니다", "있다", "있사옵니다"),
    322: ("주시오", "다오", "주소서"),
    460: ("합니다", "하다", "하겠습니다", "하겠사옵니다"),
    532: ("했습니다", "다"),
    556: ("입니다", "다", "이오"),
    598: ("이겠지요", "이리라", "이겠지"),
    688: ("어떻게", "어떠하오"),
    730: ("없습니다", "없다", "없소", "아닙니다", "아니옵니다"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    1: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1],
    178: EXPECTED_BASE_MORPHOLOGY_TERMINALS[178],
    322: EXPECTED_BASE_MORPHOLOGY_TERMINALS[322],
    466: EXPECTED_BASE_MORPHOLOGY_TERMINALS[460],
    538: EXPECTED_BASE_MORPHOLOGY_TERMINALS[532],
    568: EXPECTED_BASE_MORPHOLOGY_TERMINALS[556],
    610: EXPECTED_BASE_MORPHOLOGY_TERMINALS[598],
    700: EXPECTED_BASE_MORPHOLOGY_TERMINALS[688],
    742: EXPECTED_BASE_MORPHOLOGY_TERMINALS[730],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {31}:
        raise RuntimeError("segment 984 Base-to-PK mapping drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 984 Base-to-PK JP literal drifted")
    gap_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if gap_divergences != {2297, 2298, 2299, 2301, 2302, 2304, 2307, 2308}:
        raise RuntimeError("segment 984 Base-to-PK gap divergence drifted")
    if EXPECTED_CURRENT_GAPS != EXPECTED_BASE_GAPS:
        raise RuntimeError("segment 984 pristine/current gap drifted")
    if any(
        EXPECTED_BASE_GAPS[record_id][1] != SUPPORT_FORCE_TOKEN
        for record_id in (2305, 2306, 2307)
    ):
        raise RuntimeError("segment 984 support force token direction drifted")
    if (
        raw_translations["15:2297:0"] != ACKNOWLEDGEMENT
        or raw_translations["15:2298:0"] != ACKNOWLEDGEMENT
    ):
        raise RuntimeError("segment 984 acknowledgement canonical drifted")
    if TRANSLATIONS_BY_RECORD[2308] is not CASTLE_GOAL_TRANSLATION:
        raise RuntimeError("segment 984 castle goal object identity drifted")
    if (
        EXPECTED_BASE_JP[2299][0].replace("戦に長けた", "政に長けた")
        != EXPECTED_BASE_JP[2302][0]
        or raw_translations["15:2299:0"].replace("전투에 능한", "정무에 능한")
        != raw_translations["15:2302:0"]
    ):
        raise RuntimeError("segment 984 battle/politics staffing parallel drifted")
    joined = "\n".join(translations.values())
    for required in ("군단", "배속", "공세", "지원", "승기", "원호", "우리 가문"):
        if required not in joined:
            raise RuntimeError(f"segment 984 terminology drifted: {required}")
    for forbidden in ("당가", "의기", "。", "！", "？"):
        if forbidden in joined:
            raise RuntimeError(f"segment 984 forbidden wording retained: {forbidden}")
    if (
        SUPPORT.morphology_operands(EXPECTED_BASE_GAPS[2308][1]) != (688, 598)
        or SUPPORT.morphology_operands(EXPECTED_PK_JP_GAPS[2308][1])
        != (700, 610)
    ):
        raise RuntimeError("segment 984 goal proposal morphology drifted")
    if len(raw_translations) != 22 or len(translations) != 22:
        raise RuntimeError("segment 984 visible decision count drifted")


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
        raise RuntimeError("segment 984 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 984 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S984",
                "source_literal_count": sum(RECORD_ARITIES.values()),
                "decision_count": len(rows),
                "hidden_non_display_count": 0,
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
