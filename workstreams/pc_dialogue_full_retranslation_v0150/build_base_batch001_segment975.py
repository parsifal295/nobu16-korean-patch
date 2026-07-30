#!/usr/bin/env python3
"""Build Base authoring segment 975 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment974 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S975.private.v1.jsonl"
)
SEGMENT = 975
PERSON_TOKEN = PREVIOUS.PERSON_TOKEN
OFFICER_TOKEN = "024634"
TRANSLATIONS_BY_RECORD = {
    2206: (
        "주군 가문의 번영을 위해 사력을 다하리다\n"
        "공명을 세우게 해 달라고 달에 기원하리다",
    ),
    2207: (
        "분부를 받드는 영광을 입었으니\n"
        "제 문무의 진수를 보여 드리겠습니다",
    ),
    2208: (
        "모든 일은 이",
        "에게 맡겨 주시오\n군사의 지휘 솜씨를 발휘",
    ),
    2209: (
        "그토록 현명한 결단에 그저 감사드리오\n"
        "주군의 오른팔로서 이 목숨을 다 바치겠소",
    ),
    2210: (
        "앞서 무례하게 상신하여 결례를 범",
        "\n이 또한",
        "이(가) 주군 가문을 염려한 까닭이었으니…",
    ),
    2211: (
        "검은 승복을 걸친 이 승려도 팔을 걷어붙이겠습니다",
        "\n배워 익힌 방편의 묘를 보여 드리겠습니다",
    ),
    2212: (
        "웅무영략에 뛰어난 이 오니,",
        "\n전장 밖에서도 공을 세워 보이리라",
    ),
    2213: (
        "우리 부대가 협격을 받고 있사옵니다",
        "\n일단 물러나 태세를 정비해야 할 듯하옵니다",
    ),
    2214: (
        "적의 협격을 받고 있습니다",
        "…\n잠시 후퇴하도록 허락해 주십시오!",
    ),
    2215: (
        "불찰로 협격을 당했습니다",
        "!\n여기서는 후퇴할 수밖에 없습니다",
    ),
    2216: (
        "지금이라면 적 부대를 협격할 수 있습니다",
        "\n아군 부대에\n협격 지시를 내려 보시지요",
    ),
    2217: (
        "적을 협격할 절호의 기회입니다",
        "\n부대에 지시를 내리십시오!",
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
    2206: ("主家繁栄のため死力を尽くす所存\n功名を得んことを月に祈",),
    2207: ("ご下命の栄を賜りました\n我が文武の奥義ご覧に入れ",),
    2208: ("万事この", "にお任せあれ\n軍師の采配お見せ"),
    2209: ("斯くご英断有難き限り\n殿が右腕としてこの命に尽く",),
    2210: (
        "先の不躾なる上申ご無礼つかまつ",
        "\nこれも",
        "が主家を思う故なれば…",
    ),
    2211: ("この黒衣の片肌脱", "\n学び得た方便が妙をお見せ"),
    2212: ("雄武英略に優れたるがこの鬼", "\n戦場の外こそ功を成してみせん"),
    2213: ("我が方の部隊が挟撃されてい", "\n一度退いて態勢を立て直すべきかと"),
    2214: ("敵の挟撃を受けて", "…\n一時後退の許可を！"),
    2215: ("不覚、挟撃を受け", "！\nここは後退するほか"),
    2216: ("今なら敵部隊を挟撃でき", "\nお味方の部隊へ\n指示を出しては"),
    2217: ("敵を挟撃する好機", "\n部隊へ指示を出"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    2206: ("", "01435a040000050505"),
    2207: ("", "01431e040000050505"),
    2208: ("", PERSON_TOKEN, "014394000000050505"),
    2209: ("", "01437e040000050505"),
    2210: ("", "014368020000", PERSON_TOKEN, "050505"),
    2211: ("", "014372010000", "014394000000050505"),
    2212: ("", OFFICER_TOKEN, "050505"),
    2213: ("", "01433c040000", "050505"),
    2214: ("", "0143b2000000", "050505"),
    2215: ("", "014314020000", "0143da020000050505"),
    2216: ("", "01433c040000", "0143b0020000014324010000050505"),
    2217: ("", "01431a020000", "01437e040000050505"),
}
EXPECTED_CURRENT_GAPS = {
    **EXPECTED_BASE_GAPS,
    2206: ("", "050505"),
    2207: ("", "050505"),
    2209: ("", "050505"),
    2211: ("", "", "050505"),
    2213: ("", "", "050505"),
    2214: ("", "", "050505"),
    2215: ("", "", "050505"),
    2216: ("", "", "050505"),
    2217: ("", "", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    2206: ("", "014366040000050505"),
    2207: ("", "01432a040000050505"),
    2209: ("", "01438a040000050505"),
    2210: ("", "014374020000", PERSON_TOKEN, "050505"),
    2213: ("", "014348040000", "050505"),
    2215: ("", "01431a020000", "0143e6020000050505"),
    2216: ("", "014348040000", "0143bc020000014324010000050505"),
    2217: ("", "014326020000", "01438a040000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {"15:2210:2", "15:2214:1"}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 2206): (
        ("为了主家的繁荣，赴汤蹈火在所不辞。\n明月啊，保佑我立下功名吧。",),
        ("", "050505"),
    ),
    ("TC", 2206): (
        ("為主家的繁榮，赴湯蹈火在所不辭。\n明月啊，保佑我立下功名吧。",),
        ("", "050505"),
    ),
    ("SC", 2207): (
        ("承蒙任命，不胜光荣。\n且看我在文武两方的造诣吧。",),
        ("", "050505"),
    ),
    ("TC", 2207): (
        ("承蒙任命，不勝光榮。\n就讓您看看我在文武兩方的絕活吧。",),
        ("", "050505"),
    ),
    ("SC", 2208): (
        ("所有都交给我", "吧。\n是时候展示作为军师的神机妙算了。"),
        ("", PERSON_TOKEN, "050505"),
    ),
    ("TC", 2208): (
        ("萬事就交給我", "。\n是時候展現作為軍師的手腕了。"),
        ("", PERSON_TOKEN, "050505"),
    ),
    ("SC", 2209): (
        ("英明的决断，\n我愿做大人的左右手，鞠躬尽瘁，死而后已。",),
        ("", "050505"),
    ),
    ("TC", 2209): (
        ("大人的英明決斷，讓我不勝感激。\n我願作大人的左右手，鞠躬盡瘁，死而後已。",),
        ("", "050505"),
    ),
    ("SC", 2210): (
        ("对于先前的无礼倍感抱歉。\n这也是", "为主家所思而致…"),
        ("", PERSON_TOKEN, "050505"),
    ),
    ("TC", 2210): (
        ("請原諒我先前的無禮。\n但我", "也是為了主家著想……"),
        ("", PERSON_TOKEN, "050505"),
    ),
    ("SC", 2211): (
        ("就让贫僧助您一臂之力吧。\n过去习得的种种妙计定能派上用场。",),
        ("", "050505"),
    ),
    ("TC", 2211): (
        ("就讓貧僧助您一臂之力吧。\n過去習得的種種妙計定能派上用場。",),
        ("", "050505"),
    ),
    ("SC", 2212): (
        ("我这鬼", "雄武英略过人，\n在战场之外，更要立下功绩。"),
        ("", OFFICER_TOKEN, "050505"),
    ),
    ("TC", 2212): (
        ("我鬼", "雄武英略過人，\n沙場之外必定也能立功。"),
        ("", OFFICER_TOKEN, "050505"),
    ),
    ("SC", 2213): (
        ("我方部队正遭到敌人夹击，\n应该暂时撤退，重整态势。",),
        ("", "050505"),
    ),
    ("TC", 2213): (
        ("我方部隊遭敵人夾擊。\n應暫且撤退，重整態勢。",),
        ("", "050505"),
    ),
    ("SC", 2214): (("正遭受敌人的夹击……\n请准许暂时撤退！",), ("", "050505")),
    ("TC", 2214): (("遭敵人夾擊……\n請下令暫時後退！",), ("", "050505")),
    ("SC", 2215): (("失策，竟受到夹击！\n现在只好后撤了。",), ("", "050505")),
    ("TC", 2215): (("不好了，遭到夾擊！\n此時只能後退。",), ("", "050505")),
    ("SC", 2216): (
        ("现在可以夹击敌军了。\n向我军\n发出指令。",),
        ("", "050505"),
    ),
    ("TC", 2216): (
        ("現在方可夾擊敵方部隊，\n不妨向我方部隊下達指示。",),
        ("", "050505"),
    ),
    ("SC", 2217): (("这是夹击敌军的好机会，\n向部队下令吧。",), ("", "050505")),
    ("TC", 2217): (("現為夾擊敵軍的良機，\n向部隊下達指示吧！",), ("", "050505")),
}
PK_EN_AUXILIARY = {
    2206: (
        (
            "Everything I have is freely given for the prosperity of my clan. "
            "I pray to the moon for glory.",
        ),
        ("", "050505"),
    ),
    2207: (
        (
            "It is an honor to receive your order. "
            "You shall see my devotion to the military arts.",
        ),
        ("", "050505"),
    ),
    2208: (
        ("Leave everything to ", ". See how a tactician commands."),
        ("", PERSON_TOKEN, "050505"),
    ),
    2209: (
        (
            "My gratitude for your excellent decision shall be equaled by my "
            "diligent perseverance to see your works done.",
        ),
        ("", "050505"),
    ),
    2210: (
        ("I must apologize for my insolence. ", " merely thinks of the clanÖs welfare..."),
        ("", PERSON_TOKEN, "050505"),
    ),
    2211: (
        (
            "You have my cooperation. "
            "I will demonstrate the wonders of what IÖve learned.",
        ),
        ("", "050505"),
    ),
    2212: (
        (
            "Bravery is a virtue, true. But I, the demon ",
            ", will be much more effective off of the battlefield.",
        ),
        ("", OFFICER_TOKEN, "050505"),
    ),
    2213: (
        (
            "My unit has been surrounded by a pincer attack. "
            "We must fall back and recover our strength.",
        ),
        ("", "050505"),
    ),
    2214: (
        ("The enemy is performing a pincer attack! Requesting permission to retreat!",),
        ("", "050505"),
    ),
    2215: (
        ("I was unprepared for a pincer attack. WeÖve no choice but to retreat.",),
        ("", "050505"),
    ),
    2216: (
        (
            "Now is the perfect time to strike the enemy with a pincer attack. "
            "Will you give the orders to our allies?",
        ),
        ("", "050505"),
    ),
    2217: (
        ("We have an opportunity to make a pincer attack. LetÖs give the order!",),
        ("", "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B117_A_pristine_base_pc_jp_authoritative_"
    "loyalty_command_and_pincer_attack_dialogue_with_explicit_base2206_"
    "2217_to_pk2236_2247_mapping_exact_base_pk_jp_sc_tc_and_pk_en_"
    "auxiliary_context_主家_as_jugun_gamun_上申_as_sangsin_distinct_from_"
    "gusim_jineon_heoneon_黒衣_as_black_monk_robe_片肌脱ぎ_as_rolling_up_"
    "sleeves_方便_as_buddhist_bangpyeon_雄武英略_as_ungmuyeongnyak_挟撃_"
    "as_hyeopgyeok_person_and_officer_token_direction_current_korean_"
    "morphology_terminal_corpora_all_pristine_current_and_base_pk_opcode_"
    "divergences_recorded_project_ellipsis_current_line_counts_and_"
    "protected_skeleton_preserved_runtime_fragment_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    148: ("하겠습니다", "하겠다", "하자"),
    616: ("했습니다", "었다"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    148: EXPECTED_BASE_MORPHOLOGY_TERMINALS[148],
    178: ("있습니다", "있다", "있사옵니다"),
    292: ("일까요", "일까", "입니까"),
    370: ("겠습니다", "고우", "기로 하자", "기로 하지"),
    538: ("했습니다", "다"),
    550: ("입니다", "다", "이니라", "이오", "이옵니다"),
    628: EXPECTED_BASE_MORPHOLOGY_TERMINALS[616],
    700: ("어떻게", "어떠하오"),
    742: ("없습니다", "없다", "없소", "아닙니다", "아니옵니다"),
    1066: ("합시다", "듯"),
    1096: ("합니다", "다", "하옵니다"),
    1126: ("합시다", "하리라"),
    1162: ("합시다", "그렇군"),
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 975 Base-to-PK mapping drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 975 Base-to-PK JP literal drifted")
    if {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    } != {2206, 2207, 2209, 2210, 2213, 2215, 2216, 2217}:
        raise RuntimeError("segment 975 Base-to-PK gap divergence drifted")
    if {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_CURRENT_GAPS[record_id]
    } != {2206, 2207, 2209, 2211, 2213, 2214, 2215, 2216, 2217}:
        raise RuntimeError("segment 975 pristine/current gap divergence drifted")
    if EXPECTED_BASE_GAPS[2208][1] != PERSON_TOKEN:
        raise RuntimeError("segment 975 person-token direction drifted")
    if EXPECTED_BASE_GAPS[2212][1] != OFFICER_TOKEN:
        raise RuntimeError("segment 975 officer-token direction drifted")
    if (
        EXPECTED_BASE_GAPS[2210][2] != PERSON_TOKEN
        or not raw_translations["15:2210:2"].startswith(
            "이(가) 주군 가문을 "
        )
    ):
        raise RuntimeError("segment 975 dynamic person subject particle drifted")
    joined = "\n".join(translations.values())
    for required in (
        "주군 가문",
        "상신",
        "검은 승복",
        "팔을 걷어붙",
        "방편",
        "웅무영략",
        "협격",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 975 historical or semantic terminology drifted: {required}"
            )
    for forbidden in ("주가", "구신", "진언", "헌언", "묘책"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 975 forbidden wording retained: {forbidden}"
            )
    if (
        "上申" not in EXPECTED_BASE_JP[2210][0]
        or "黒衣" not in EXPECTED_BASE_JP[2211][0]
        or "方便" not in EXPECTED_BASE_JP[2211][1]
        or "雄武英略" not in EXPECTED_BASE_JP[2212][0]
    ):
        raise RuntimeError("segment 975 high-risk source terminology drifted")
    assembled_officer = (
        raw_translations["15:2212:0"]
        + "○○"
        + raw_translations["15:2212:1"]
    )
    if assembled_officer != (
        "웅무영략에 뛰어난 이 오니,○○\n"
        "전장 밖에서도 공을 세워 보이리라"
    ) or ":" in assembled_officer:
        raise RuntimeError("segment 975 Base2212 officer-token assembly drifted")
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 975 project ellipsis normalization drifted: {coordinate}"
            )
    if len(raw_translations) != 22 or len(translations) != 22:
        raise RuntimeError("segment 975 visible decision count drifted")


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
        raise RuntimeError("segment 975 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 975 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S975",
                "source_literal_count": 22,
                "decision_count": len(rows),
                "hidden_non_display_count": 0,
                "runtime_fragment_pending": len(rows),
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [
                    2206,
                    2207,
                    2209,
                    2210,
                    2213,
                    2215,
                    2216,
                    2217,
                ],
                "pristine_current_gap_divergence_records": [
                    2206,
                    2207,
                    2209,
                    2211,
                    2213,
                    2214,
                    2215,
                    2216,
                    2217,
                ],
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
