#!/usr/bin/env python3
"""Build Base authoring segment 976 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment975 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
SUPPORT = PREVIOUS.SUPPORT
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S976.private.v1.jsonl"
)
SEGMENT = 976
CASTLE_TOKEN = "026432"
CAPTURE_COUNCIL = (
    "지금이라면",
    "을(를) 함락시킬 수 있",
    "\n군의에서 출진을 명해 주십시오!",
)
TRANSLATIONS_BY_RECORD = {
    2218: ("적 부대를 협격하면\n큰 피해를 입힐 수 있습니다",),
    2219: (
        "의 반격이 거세어\n아군이 피해를 입고 있",
        "\n다른 방향에서도 공격하는 것이",
    ),
    2220: (
        "의 저항이 거세어\n공격 측의 피해가 커져 가고",
        "\n다른 방향에도 부대를 파견하는 것이",
    ),
    2221: (
        "은(는) 방비가 견고하여\n"
        "함락하려면 시간이 걸린다 하옵니다\n"
        "여러 방향에서 공격하시는 것이",
    ),
    2222: (
        "이번 싸움에는 승산이 없습니다",
        "\n부대를 철수시켜도 되겠습니까?",
    ),
    2223: (
        "…말씀드리기 괴롭사오나",
        "\n이번 싸움에서는 승기를 잡기 어려우니\n"
        "철수할 때라 사료되옵니다",
    ),
    2224: (
        "우리 가문의 전세가 좋지 않으니\n"
        "피해가 커지기 전에 철병을 명해 주십시오…",
    ),
    2225: (
        "이번 싸움에는 승산이 없습니다",
        "\n헛되이 피해를 늘리기 전에\n철수할 것을 진언드리옵니다",
    ),
    2226: (
        "군단에 새로운 부하를 편입하면\n"
        "모든 성을 두루 살필 수 있을 듯하옵니다",
    ),
    2227: CAPTURE_COUNCIL,
    2228: CAPTURE_COUNCIL,
    2229: (
        "우리 전력이라면",
        "은(는)\n함락할 만한 성",
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
    2218: ("敵部隊を挟撃することで\n大きな被害を与えられ",),
    2219: (
        "からの反撃が強く\nお味方に被害がでてい",
        "\n別方向からも攻めては",
    ),
    2220: (
        "の抵抗が激しく\n攻め手の被害が拡大して",
        "\n別方向にも部隊を派遣しては",
    ),
    2221: (
        "は頑強で\n攻め落とすには時間がかかるとのこと\n"
        "複数方向から攻撃しては",
    ),
    2222: ("この戦、勝ち目は", "\n撤退させてもよろしい"),
    2223: ("…心苦しくはあ", "が\n此度の戦にて勝機は遠く\n撤退の機かと"),
    2224: ("当家の旗色芳しからず\n傷浅きうちに撤兵の指示を…",),
    2225: ("この戦、勝ち目は", "\nいたずらに被害を増す前に\n撤退を進言いたします"),
    2226: ("軍団に新たな配下を編入すれば\nすべての城に目が行き届くかと",),
    2227: ("今なら", "を落とせ", "\n軍議で出陣のご命令を！"),
    2228: ("今なら", "を落とせ", "\n軍議で出陣のご命令を！"),
    2229: ("我らの戦力ならば", "は\n落とすことができる"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    2218: ("", "01433c040000050505"),
    2219: (
        CASTLE_TOKEN,
        "01433c040000",
        "0143b0020000014324010000050505",
    ),
    2220: (
        CASTLE_TOKEN,
        "0143b2000000",
        "0143b0020000014324010000050505",
    ),
    2221: (CASTLE_TOKEN, "0143b0020000014324010000050505"),
    2222: ("", "0143fe020000", "014324010000050505"),
    2223: ("", "014336040000", "0143e2000000050505"),
    2224: ("", "050505"),
    2225: ("", "0143fe020000", "050505"),
    2226: ("", "050505"),
    2227: ("", CASTLE_TOKEN, "01433c040000", "050505"),
    2228: ("", CASTLE_TOKEN, "01433c040000", "050505"),
    2229: ("", CASTLE_TOKEN, "014356020000050505"),
}
EXPECTED_CURRENT_GAPS = {
    **EXPECTED_BASE_GAPS,
    2218: ("", "050505"),
    2222: ("", "", "050505"),
    2223: ("", "", "050505"),
    2225: ("", "", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    **EXPECTED_BASE_GAPS,
    2218: ("", "014348040000050505"),
    2219: (
        CASTLE_TOKEN,
        "014348040000",
        "0143bc020000014324010000050505",
    ),
    2220: (
        CASTLE_TOKEN,
        "0143b2000000",
        "0143bc020000014324010000050505",
    ),
    2221: (CASTLE_TOKEN, "0143bc020000014324010000050505"),
    2222: ("", "01430a030000", "014324010000050505"),
    2223: ("", "014342040000", "0143e2000000050505"),
    2225: ("", "01430a030000", "050505"),
    2227: ("", CASTLE_TOKEN, "014348040000", "050505"),
    2228: ("", CASTLE_TOKEN, "014348040000", "050505"),
    2229: ("", CASTLE_TOKEN, "014362020000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {"15:2223:0", "15:2224:0"}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 2218): (("通过夹击敌方部队，\n对敌方造成巨大打击。",), ("", "050505")),
    ("TC", 2218): (("採取夾擊必能痛擊\n敵方部隊。",), ("", "050505")),
    ("SC", 2219): (
        ("的反击十分强烈，\n己方已经出现损失，\n不如从其他方向进攻如何？",),
        (CASTLE_TOKEN, "050505"),
    ),
    ("TC", 2219): (
        ("的反擊猛烈，\n導致友方受害嚴重。\n不妨也從別的方向發動進攻。",),
        (CASTLE_TOKEN, "050505"),
    ),
    ("SC", 2220): (
        ("的抵抗非常顽强，\n攻方的损失正在扩大。\n不如也向其他方向派遣部队如何？",),
        (CASTLE_TOKEN, "050505"),
    ),
    ("TC", 2220): (
        ("頑強抵抗，\n導致進攻部隊受害嚴重。\n不妨也對其他方向派遣部隊。",),
        (CASTLE_TOKEN, "050505"),
    ),
    ("SC", 2221): (
        ("十分顽强，\n看来攻略要花很长时间。\n不如从多个方向对其进攻如何？",),
        (CASTLE_TOKEN, "050505"),
    ),
    ("TC", 2221): (
        ("據說", "非常頑強，\n一時無法擊破。\n不妨多方向發動攻擊。"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("SC", 2222): (("此战没有取胜的可能了。\n可否让部队撤退呢？",), ("", "050505")),
    ("TC", 2222): (
        ("這場戰爭，看來是毫無勝算了。\n是否令部隊撤退？",),
        ("", "050505"),
    ),
    ("SC", 2223): (
        ("……虽然难以接受，\n但此战已无胜算，\n是时候撤退了。",),
        ("", "050505"),
    ),
    ("TC", 2223): (
        ("……實在很抱歉，\n但這場戰鬥毫無勝算，\n還請盡早撤退。",),
        ("", "050505"),
    ),
    ("SC", 2224): (
        ("本家的战况不太妙，\n请趁伤亡尚不严重之时下令撤兵……",),
        ("", "050505"),
    ),
    ("TC", 2224): (
        ("本家的戰況不利。\n請在傷亡慘重之前下令撤兵……",),
        ("", "050505"),
    ),
    ("SC", 2225): (
        ("此战没有取胜的可能了。\n在白白增加损失之前，\n还请考虑撤退。",),
        ("", "050505"),
    ),
    ("TC", 2225): (
        ("這場戰爭，看來是毫無勝算了。\n在白白增加損傷之前，\n還請考慮撤退。",),
        ("", "050505"),
    ),
    ("SC", 2226): (
        ("若是向军团编入新的麾下，\n应该就可以顾及到全部的城了。",),
        ("", "050505"),
    ),
    ("TC", 2226): (
        ("臣認為，在軍團裡編入的新屬下，\n以便掌控全部的城。",),
        ("", "050505"),
    ),
    ("SC", 2227): (
        ("正是攻打 ", "的绝好时机。\n马上召开军事会议吧。"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("TC", 2227): (
        ("現在是進攻", "的好時機。\n立刻召開軍議。"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("SC", 2228): (
        ("如今可攻下", "，\n请于军议之上下达出阵命令！"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("TC", 2228): (
        ("要攻潰", "得趁現在。\n軍議時請下令出陣！"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("SC", 2229): (
        ("以我等的战斗力，\n攻陷", "不在话下。"),
        ("", CASTLE_TOKEN, "050505"),
    ),
    ("TC", 2229): (
        ("憑我等的戰力\n應可攻潰", "。"),
        ("", CASTLE_TOKEN, "050505"),
    ),
}
PK_EN_AUXILIARY = {
    2218: (
        ("We can deal a huge blow to the enemy unit if we trap them in a pincer attack.",),
        ("", "050505"),
    ),
    2219: (
        (
            "Our allies have suffered casualties by ",
            "Ös vicious counterattack. "
            "We should try attacking from a different angle.",
        ),
        ("", CASTLE_TOKEN, "050505"),
    ),
    2220: (
        (
            " is putting up heavy resistance, and the attackers are taking a lot "
            "of damage. We ought to dispatch some soldiers from a different angle.",
        ),
        (CASTLE_TOKEN, "050505"),
    ),
    2221: (
        (
            "It will take some time to break through ",
            "Ös defenses. We should attack the castle from multiple directions.",
        ),
        ("", CASTLE_TOKEN, "050505"),
    ),
    2222: (
        ("There is no victory in sight. Will you allow us to retreat?",),
        ("", "050505"),
    ),
    2223: (
        (
            "It pains me to say, but victory is beyond our reach at this time. "
            "We should retreat.",
        ),
        ("", "050505"),
    ),
    2224: (
        (
            "This will not bode well for our reputation, but we should retreat "
            "while the wounded are still few.",
        ),
        ("", "050505"),
    ),
    2225: (
        (
            "I do not see the opportunity for victory here. "
            "I suggest we retreat before we suffer excessive damage.",
        ),
        ("", "050505"),
    ),
    2226: (
        (
            "We should send our new retainers to the provinces to ensure "
            "all our castles are attended to.",
        ),
        ("", "050505"),
    ),
    2227: (
        (
            "If we attack now, we will surely capture ",
            ". We are ready to march on your command!",
        ),
        ("", CASTLE_TOKEN, "050505"),
    ),
    2228: (
        (
            "If we attack now, we will surely capture ",
            ". We are ready to march on your command!",
        ),
        ("", CASTLE_TOKEN, "050505"),
    ),
    2229: (
        ("At our current power, we will be able to take down ", "."),
        ("", CASTLE_TOKEN, "050505"),
    ),
}
AUXILIARY_OVERRIDES = SUPPORT.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B117_A_pristine_base_pc_jp_authoritative_"
    "pincer_siege_retreat_and_army_management_dialogue_with_explicit_"
    "base2218_2229_to_pk2248_2259_mapping_exact_base_pk_jp_sc_tc_and_pk_"
    "en_auxiliary_context_挟撃_as_hyeopgyeok_撤退_as_cheolsu_撤兵_as_"
    "cheolbyeong_軍議_as_gunui_当家_as_uri_gamun_進言_as_jineon_傷浅き_"
    "as_before_losses_deepen_dynamic_castle_token_subject_direction_"
    "exact_2227_2228_source_gap_and_korean_tuple_reuse_current_korean_"
    "morphology_terminal_corpora_all_pristine_current_and_base_pk_opcode_"
    "divergences_recorded_project_ellipsis_current_line_counts_and_"
    "protected_skeleton_preserved_mixed_static_and_runtime_pending_"
    "classification"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    178: ("있습니다", "있다", "있사옵니다"),
    292: ("일까요", "일까", "입니까"),
    598: ("이겠지요", "이리라", "이겠지"),
    688: ("어떻게", "어떠하오"),
    1084: ("합니다", "다", "하옵니다"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    178: EXPECTED_BASE_MORPHOLOGY_TERMINALS[178],
    226: (
        "생각합니다",
        "생각한다",
        "생각하오",
        "생각하옵니다",
        "생각하옵나이다",
    ),
    292: EXPECTED_BASE_MORPHOLOGY_TERMINALS[292],
    610: EXPECTED_BASE_MORPHOLOGY_TERMINALS[598],
    700: EXPECTED_BASE_MORPHOLOGY_TERMINALS[688],
    778: (
        "않을 것입니다",
        "없으리라",
        "없을 것입니다",
        "있지 않을 것이오",
    ),
    1090: ("합니다", "다"),
    1096: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1084],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 976 Base-to-PK mapping drifted")
    if EXPECTED_BASE_JP != EXPECTED_PK_JP:
        raise RuntimeError("segment 976 Base-to-PK JP literal drifted")
    if {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    } != {2218, 2219, 2220, 2221, 2222, 2223, 2225, 2227, 2228, 2229}:
        raise RuntimeError("segment 976 Base-to-PK gap divergence drifted")
    if {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_CURRENT_GAPS[record_id]
    } != {2218, 2222, 2223, 2225}:
        raise RuntimeError("segment 976 pristine/current gap divergence drifted")
    if any(
        EXPECTED_BASE_GAPS[record_id][0] != CASTLE_TOKEN
        for record_id in (2219, 2220, 2221)
    ) or any(
        EXPECTED_BASE_GAPS[record_id][1] != CASTLE_TOKEN
        for record_id in (2227, 2228, 2229)
    ):
        raise RuntimeError("segment 976 castle-token direction drifted")
    if (
        EXPECTED_BASE_JP[2227] != EXPECTED_BASE_JP[2228]
        or EXPECTED_BASE_GAPS[2227] != EXPECTED_BASE_GAPS[2228]
        or TRANSLATIONS_BY_RECORD[2227] != TRANSLATIONS_BY_RECORD[2228]
        or TRANSLATIONS_BY_RECORD[2227] is not CAPTURE_COUNCIL
        or TRANSLATIONS_BY_RECORD[2228] is not CAPTURE_COUNCIL
    ):
        raise RuntimeError("segment 976 Base2227/2228 exact tuple reuse drifted")
    joined = "\n".join(translations.values())
    for required in (
        "협격",
        "철수",
        "철병",
        "군의",
        "우리 가문",
        "진언",
    ):
        if required not in joined:
            raise RuntimeError(
                f"segment 976 historical or semantic terminology drifted: {required}"
            )
    for forbidden in ("당가", "후퇴할 것을 진언", "상처가 얕", "군사 회의"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 976 forbidden wording retained: {forbidden}"
            )
    if (
        raw_translations["15:2224:0"]
        != "우리 가문의 전세가 좋지 않으니\n"
        "피해가 커지기 전에 철병을 명해 주십시오…"
    ):
        raise RuntimeError("segment 976 当家 or 傷浅き meaning drifted")
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 976 project ellipsis normalization drifted: {coordinate}"
            )
    if len(raw_translations) != 22 or len(translations) != 22:
        raise RuntimeError("segment 976 visible decision count drifted")


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
    for row in rows:
        if row["coordinate"] in {"15:2224:0", "15:2226:0"}:
            row["scope_classification"] = "retranslated"
            row["runtime_review"] = "not_required"
    return prepared, translations, rows


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(rows) != 22 or len(validated) != len(translations):
        raise RuntimeError("segment 976 validated count drifted")
    static_coordinates = {"15:2224:0", "15:2226:0"}
    if any(
        (
            row["scope_classification"],
            row["runtime_review"],
        )
        != (
            ("retranslated", "not_required")
            if row["coordinate"] in static_coordinates
            else ("runtime_fragment_pending", "pending")
        )
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError("segment 976 runtime/authority classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S976",
                "source_literal_count": 22,
                "decision_count": len(rows),
                "hidden_non_display_count": 0,
                "runtime_fragment_pending": 20,
                "retranslated_static": 2,
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [
                    2218,
                    2219,
                    2220,
                    2221,
                    2222,
                    2223,
                    2225,
                    2227,
                    2228,
                    2229,
                ],
                "pristine_current_gap_divergence_records": [
                    2218,
                    2222,
                    2223,
                    2225,
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
