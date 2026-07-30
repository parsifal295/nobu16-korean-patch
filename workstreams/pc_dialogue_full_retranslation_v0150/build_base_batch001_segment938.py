#!/usr/bin/env python3
"""Build Base authoring segment 938 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment937 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
MORPHOLOGY = PREVIOUS.PREVIOUS.PREVIOUS
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S938.private.v1.jsonl"
)
SEGMENT = 938
TRANSLATIONS_BY_RECORD = {
    1824: (
        "당면 목표로는",
        "을(를) 추천",
        "\n군비를 갖추면 전시에 다소 전력 차이가 있더라도\n"
        "뒤집기 어렵지 않을 것으로",
    ),
    1825: (
        "이미 싸울 때가 무르익어",
        "\n지금,",
        "(으)로 침공을 시작하면\n우리 쪽의 승산이 높을 것",
    ),
    1828: (
        "우리 가문은 현재,",
        "의",
        "와(과)\n실제로 교전하고",
    ),
    1829: (
        "우리 가문은 현재,",
        "의",
        "등\n여러 세력과 교전하고",
    ),
    1830: (
        "공격과 수비를 병행하기는 매우 어려운 일…\n"
        "어느 쪽이든 빨리 결판나기를 희망",
    ),
    1831: (
        "침공은 대체로 순조롭다고 할",
        "\n다만, 방심해서는 안 되",
        " 늘 경계해야 합니다",
    ),
    1832: (
        "침공은 다소 난항을 겪고",
        "\n싸움의 승패는 아직 드러나지",
        "만\n물러날 때도 생각해 두어야 하겠습니다",
    ),
    1833: (
        "침략을 받고",
        "만\n전황은 우리 가문이 우세하다고 판단",
        "…\n경계를 늦추지 않고 이대로 넘기고 싶은 참",
    ),
    1834: (
        "지금 침략을 받고 있어\n우리 쪽이 열세인 것으로 판단",
        "\n어떤 식으로든 대책을 마련해야 하겠습니다",
    ),
    1835: ("다만, 멸망하는 것도 시간문제",),
    1836: ("공략까지는 시간이 좀 걸릴 모양",),
}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, record_translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(record_translations)
}
RECORD_ARITIES = {
    1824: 3,
    1825: 3,
    1826: 1,
    1828: 3,
    1829: 3,
    1830: 1,
    1831: 3,
    1832: 3,
    1833: 3,
    1834: 2,
    1835: 1,
    1836: 1,
}
EXPECTED_BASE_JP = {
    1824: (
        "目下の目標には",
        "を勧め",
        "\n軍備を整えれば、戦時に多少戦力差があれど\n覆すも容易かと",
    ),
    1825: (
        "既に戦機は熟して",
        "\n今、",
        "へ侵攻を開始すれば\n当方の勝算は高い",
    ),
    1826: ("",),
    1828: ("当家は現在、", "の", "と\nまさに刃を交えて"),
    1829: ("当家は現在、", "の", "など\n複数の勢力と刃を交えて"),
    1830: ("攻めと守りの両立は至難…\nいずれかの早期決着が望まれ",),
    1831: ("侵攻はおよそ順調といえ", "\nただ、油断は", "無用に"),
    1832: (
        "侵攻はやや難航して",
        "\n戦の勝敗はまだ見え",
        "が\n引き際についても考えおくべきかと",
    ),
    1833: (
        "侵略を受けては",
        "が\n戦況は当家が優勢と見",
        "…\n気を緩めず、やり過ごしたいところ",
    ),
    1834: (
        "まさにいま侵略を受けており\n当方の劣勢が見て取れ",
        "\n何らかの手立てが不可欠かと",
    ),
    1835: ("ただ、滅亡も時間の問題",),
    1836: ("攻略までしばらくかかりそう",),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1824: ("", "026432", "01433C040000", "0143E2000000050505"),
    1825: ("", "0143B2000000", "026432", "01431E010000050505"),
    1826: ("", "050505"),
    1828: ("", "023C", "025132", "0143B2000000050505"),
    1829: ("", "023C", "025132", "0143B2000000050505"),
    1830: ("", "01433C040000050505"),
    1831: ("", "01431E040000", "01438A040000", "050505"),
    1832: ("", "0143B2000000", "0143E0020000", "050505"),
    1833: ("", "0143B2000000", "01433C040000", "01432C020000050505"),
    1834: ("", "01433C040000", "050505"),
    1835: ("", "014356020000050505"),
    1836: ("", "01431A020000050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    1824: ("", "026432", "014348040000", "0143E2000000050505"),
    1825: ("", "0143B2000000", "026432", "01431E010000050505"),
    1826: ("", "050505"),
    1828: ("", "023C", "025132", "0143B2000000050505"),
    1829: ("", "023C", "025132", "0143B2000000050505"),
    1830: ("", "014348040000050505"),
    1831: ("", "01432A040000", "014396040000", "050505"),
    1832: ("", "0143B2000000", "0143EC020000", "050505"),
    1833: ("", "0143B2000000", "014348040000", "014338020000050505"),
    1834: ("", "014348040000", "050505"),
    1835: ("", "014362020000050505"),
    1836: ("", "014326020000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:1830:0",
    "15:1833:2",
}
EXCLUDED_NONVISIBLE_COORDINATES = {"15:1826:0": ""}
SHARED_AUXILIARY = {
    ("SC", 1824): (
        (
            "建议将当下目标指向",
            "。\n若能整备军队，战时纵使稍有战力之差距，\n亦易于逆转情势吧。",
        ),
        ("", "026432", "050505"),
    ),
    ("SC", 1825): (
        ("臣认为时机已成熟！\n应对", "出兵，\n我方胜算极高。"),
        ("", "026432", "050505"),
    ),
    ("SC", 1826): (("",), ("", "050505")),
    ("SC", 1828): (
        ("我方目前与", "的", "\n正处于交战状态。"),
        ("", "023C", "025132", "050505"),
    ),
    ("SC", 1829): (
        ("本家目前正与", "的", "等\n多数势力交锋中。"),
        ("", "023C", "025132", "050505"),
    ),
    ("SC", 1830): (
        ("同时进行攻打与防御绝非良策，\n速战速决吧。",),
        ("", "050505"),
    ),
    ("SC", 1831): (("虽然攻打还算顺利，\n但切忌大意。",), ("", "050505")),
    ("SC", 1832): (
        ("攻打可说不上顺利，\n若依旧毫无起色，还是趁早收手吧。",),
        ("", "050505"),
    ),
    ("SC", 1833): (
        ("虽然遭到侵略，\n但战况仍处于优势。\n速战速决吧。",),
        ("", "050505"),
    ),
    ("SC", 1834): (
        ("遭到侵略，战况很不妙。\n使出任何手段也要守住。",),
        ("", "050505"),
    ),
    ("SC", 1835): (("不过，它的覆灭也是迟早的事了。",), ("", "050505")),
    ("SC", 1836): (("看来要过段时间才能攻略了。",), ("", "050505")),
    ("TC", 1824): (
        (
            "建議將當下目標指向",
            "。\n若能整備軍隊，戰時縱使稍有戰力之差距，\n亦易於逆轉情勢吧。",
        ),
        ("", "026432", "050505"),
    ),
    ("TC", 1825): (
        ("臣認為時機已成熟！\n應對", "出兵，\n我方勝算極高。"),
        ("", "026432", "050505"),
    ),
    ("TC", 1826): (("",), ("", "050505")),
    ("TC", 1828): (
        ("我方目前與", "的", "\n正處於交戰狀態。"),
        ("", "023C", "025132", "050505"),
    ),
    ("TC", 1829): (
        ("本家目前正與", "的", "等\n多數勢力交鋒中。"),
        ("", "023C", "025132", "050505"),
    ),
    ("TC", 1830): (
        ("攻防同時並進絕非良策，\n還是速戰速決吧。",),
        ("", "050505"),
    ),
    ("TC", 1831): (("雖然攻打還算順利，\n但切忌大意。",), ("", "050505")),
    ("TC", 1832): (
        ("攻打可說不上順利，\n若依舊毫無起色，還是趁早收手吧。",),
        ("", "050505"),
    ),
    ("TC", 1833): (
        ("雖然遭到侵略，\n但戰況仍處於優勢。\n速戰速決吧。",),
        ("", "050505"),
    ),
    ("TC", 1834): (
        ("遭到侵略，戰況很不妙。\n使出任何手段也要守住。",),
        ("", "050505"),
    ),
    ("TC", 1835): (("不過，滅亡亦為時間早晚的問題。",), ("", "050505")),
    ("TC", 1836): (("距離攻略尚須一段時間。",), ("", "050505")),
}
PK_EN_AUXILIARY = {
    1824: (
        (
            "I recommend targeting ",
            ". It should be easy to turn the tides of war as long as we bring enough soldiers.",
        ),
        ("", "026432", "050505"),
    ),
    1825: (
        (
            "The time has come. If we attack ",
            " now, the odds should be in our favor.",
        ),
        ("", "026432", "050505"),
    ),
    1828: (
        ("Our clan is currently on the verge of war with the ", " of ", "."),
        ("", "025132", "023C", "050505"),
    ),
    1829: (
        (
            "Our clan is currently on the verge of war with several clans, including the ",
            " of ",
            ".",
        ),
        ("", "025132", "023C", "050505"),
    ),
    1830: (
        (
            "It is difficult to find the right balance between offense and defense. LetÖs just hope we can settle this quickly.",
        ),
        ("", "050505"),
    ),
    1831: (
        ("The invasion is proceeding smoothly, but we cannot let down our guard.",),
        ("", "050505"),
    ),
    1832: (
        (
            "WeÖre having some trouble with the invasion. It is hard to predict the warÖs outcome as of now, but we should consider our avenues of retreat.",
        ),
        ("", "050505"),
    ),
    1833: (
        (
            "Although weÖve been invaded, we still have the upper hand. We must keep up the pressure.",
        ),
        ("", "050505"),
    ),
    1834: (("WeÖre invaded and outnumbered. We must take action.",), ("", "050505")),
}
AUXILIARY_OVERRIDES = MORPHOLOGY.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B113_A_pristine_base_pc_jp_authoritative_"
    "war_target_timing_active_wars_and_war_situation_assessment_with_"
    "explicit_base1824_1836_excluding_missing1827_and_empty1826_to_pk1854_"
    "1866_mapping_exact_base_pk_jp_sc_tc_and_actual_pk_en_auxiliary_"
    "context_project_uri_gamun_chulbyeong_timing_gongnyak_jeonhwang_terms_"
    "dynamic_force_castle_tokens_direction_current_korean_morphology_"
    "terminal_corpora_and_cross_resource_opcode_divergences_recorded_"
    "project_ellipsis_pair_current_line_counts_and_protected_skeleton_"
    "preserved_runtime_fragment_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    178: ("있습니다", "있다", "있사옵니다"),
    226: ("생각합니다", "생각한다", "생각하오", "생각하옵니다", "생각하옵나이다"),
    286: ("이겠지", "인가 하고", "이겠지요"),
    538: ("입니다", "다", "이니라", "이오", "이옵니다"),
    556: ("입니다", "다", "이오"),
    598: ("이겠지요", "이리라", "이겠지"),
    736: ("않습니다", "않는다"),
    1054: ("합시다", "듯"),
    1084: ("합니다", "다", "하옵니다"),
    1162: ("고", ""),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    178: EXPECTED_BASE_MORPHOLOGY_TERMINALS[178],
    226: EXPECTED_BASE_MORPHOLOGY_TERMINALS[226],
    286: EXPECTED_BASE_MORPHOLOGY_TERMINALS[286],
    550: EXPECTED_BASE_MORPHOLOGY_TERMINALS[538],
    568: EXPECTED_BASE_MORPHOLOGY_TERMINALS[556],
    610: EXPECTED_BASE_MORPHOLOGY_TERMINALS[598],
    748: EXPECTED_BASE_MORPHOLOGY_TERMINALS[736],
    1066: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1054],
    1096: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1084],
    1174: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1162],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if set(RECORD_ARITIES) != {
        1824,
        1825,
        1826,
        1828,
        1829,
        1830,
        1831,
        1832,
        1833,
        1834,
        1835,
        1836,
    }:
        raise RuntimeError("segment 938 record universe drifted")
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 938 Base-to-PK mapping drifted")
    divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if divergences != {1824, 1830, 1831, 1832, 1833, 1834, 1835, 1836}:
        raise RuntimeError("segment 938 Base-to-PK gap divergence drifted")
    if any(
        EXPECTED_BASE_JP[record_id] != EXPECTED_PK_JP[record_id]
        for record_id in RECORD_ARITIES
    ):
        raise RuntimeError("segment 938 Base-to-PK literal divergence drifted")
    joined = "\n".join(translations.values())
    for required in (
        "우리 가문",
        "싸울 때",
        "공략",
        "전황",
        "교전",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 938 required terminology drifted: {required}")
    for forbidden in ("당가", "전기가", "칼날을 맞대", "결착", "지난한"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 938 forbidden phrasing retained: {forbidden}"
            )
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 938 ellipsis seed/pair drifted: {coordinate}"
            )
    if not raw_translations["15:1833:2"].endswith("싶은 참"):
        raise RuntimeError("segment 938 Base1833 copula stem drifted")
    if set(EXCLUDED_NONVISIBLE_COORDINATES) != {"15:1826:0"}:
        raise RuntimeError("segment 938 hidden literal exclusion drifted")
    if len(translations) != 26:
        raise RuntimeError("segment 938 visible decision count drifted")


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
    MORPHOLOGY.annotate_morphology_evidence(
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
    if len(rows) != 26 or len(validated) != len(translations):
        raise RuntimeError("segment 938 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 938 runtime classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S938",
                "decision_count": len(rows),
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "excluded_nonvisible_coordinates": EXCLUDED_NONVISIBLE_COORDINATES,
                "missing_record_ids": [1827],
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [
                    1824,
                    1830,
                    1831,
                    1832,
                    1833,
                    1834,
                    1835,
                    1836,
                ],
                "contextual_ellipsis_normalized_to_project_pair": len(
                    CURRENT_ELLIPSIS_COORDINATES
                ),
                "record_count": 19152,
                "outside_scope_records_exact": True,
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
