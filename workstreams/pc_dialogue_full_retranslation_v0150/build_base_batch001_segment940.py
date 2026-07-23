#!/usr/bin/env python3
"""Build Base authoring segment 940 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment939 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
MORPHOLOGY = PREVIOUS.MORPHOLOGY
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S940.private.v1.jsonl"
)
SEGMENT = 940
TRANSLATIONS_BY_RECORD = {
    1846: (
        "영토를 넓히려면\n",
        "의",
        "을(를)\n공격하는 것이 좋을 것으로",
    ),
    1847: (
        "준비는 이미 모두 갖추어져",
        "그러니\n당장이라도 공격하고 싶은 참",
    ),
    1848: (
        "다만, 지금은 아직 시기상조…병력을\n"
        "증강한 뒤 공격하는 것이 타당할 것",
    ),
    1849: (
        "다만, 지금은 아직 시기상조…병량을\n"
        "더 비축한 뒤 공격하는 것이 타당할 것",
    ),
    1850: (
        "다만, 지금은 아직 시기상조…우군을\n"
        "늘린 뒤 공격하는 것이 타당할 것",
        "\n국인중이나 다른 세력을 우군으로 확보",
    ),
    1851: (
        "다만, 지금은 아직 시기상조…병력을 증강하고\n"
        "병량을 더 비축한 뒤 공격하는 것이\n타당할 것",
    ),
    1852: (
        "다만, 지금은 아직 시기상조…병량을 비축하고\n"
        "우군을 더 확보한 뒤 공격하는 것이\n타당할 것",
    ),
    1853: (
        "다만, 지금은 아직 시기상조…병력을\n"
        "증강하고 우군을 확보한 뒤 공격하는 것이\n타당할 것",
    ),
    1854: (
        "다만, 지금은 아직 시기상조…병력을 증강하고\n"
        "병량을 비축하며 우군까지 확보한 뒤\n공격하는 것이 타당할 것",
    ),
    1855: (
        "이렇다 할 무장도",
        "그러니\n두려워",
    ),
    1856: (
        "다만, 명장이라 불리는",
        "은(는)\n주의해야 할 상대",
        "…",
    ),
    1857: (
        "눈에 띄는 무장은",
        "만,\n",
        "등의 움직임은 예의주시",
    ),
}
RAW_TRANSLATIONS = {
    f"15:{record_id}:{literal_id}": translation
    for record_id, record_translations in TRANSLATIONS_BY_RECORD.items()
    for literal_id, translation in enumerate(record_translations)
}
RECORD_ARITIES = {
    record_id: len(translations)
    for record_id, translations in TRANSLATIONS_BY_RECORD.items()
}
EXPECTED_BASE_JP = {
    1846: ("領土を広げるには\n", "の", "を\n攻めるのがよいかと"),
    1847: ("支度はすでに整って", "ゆえ\nすぐにでも攻めたいところ"),
    1848: ("ただ、今はまだ時期尚早…兵力を\n増強してから攻めるのが妥当",),
    1849: ("ただ、今はまだ時期尚早…兵糧の\n備蓄を増やしてから攻めるのが妥当",),
    1850: (
        "ただ、今はまだ時期尚早…味方を\n増やしてから攻めるのが妥当",
        "\n国衆や他勢力を味方につけ",
    ),
    1851: (
        "ただ、今はまだ時期尚早…兵力を増強し\n"
        "兵糧の備蓄を増やしてから攻めるのが\n妥当",
    ),
    1852: (
        "ただ、今はまだ時期尚早…兵糧の備蓄と\n"
        "味方を増やしてから攻めるのが\n妥当",
    ),
    1853: (
        "ただ、今はまだ時期尚早…兵力を\n"
        "増強し味方を増やしてから攻めるのが\n妥当",
    ),
    1854: (
        "ただ、今はまだ時期尚早…兵力増強や\n"
        "兵糧備蓄の強化、味方の確保などを行ってから\n攻めるのが妥当",
    ),
    1855: ("さほどの武将も", "ゆえ\n恐るるに足"),
    1856: ("ただ、名将と呼ばれる", "には\n注意が必要", "が…"),
    1857: ("際立った武将は", "が、\n", "などの動きは気にな"),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1846: ("", "023C", "025132", "0143E2000000050505"),
    1847: ("", "0143B2000000", "01431A020000050505"),
    1848: ("", "014356020000050505"),
    1849: ("", "014356020000050505"),
    1850: ("", "014356020000", "01431E040000050505"),
    1851: ("", "014356020000050505"),
    1852: ("", "014356020000050505"),
    1853: ("", "014356020000050505"),
    1854: ("", "014356020000050505"),
    1855: ("", "0143A0000000", "01432A040000050505"),
    1856: ("", "024933", "014326020000", "050505"),
    1857: ("", "0143A0000000", "024933", "014336040000050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    1846: ("", "023C", "025132", "0143E2000000050505"),
    1847: ("", "0143B2000000", "014326020000050505"),
    1848: ("", "014362020000050505"),
    1849: ("", "014362020000050505"),
    1850: ("", "014362020000", "01432A040000050505"),
    1851: ("", "014362020000050505"),
    1852: ("", "014362020000050505"),
    1853: ("", "014362020000050505"),
    1854: ("", "014362020000050505"),
    1855: ("", "0143A0000000", "014336040000050505"),
    1856: ("", "024933", "014332020000", "050505"),
    1857: ("", "0143A0000000", "024933", "014342040000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:1848:0",
    "15:1849:0",
    "15:1850:0",
    "15:1851:0",
    "15:1852:0",
    "15:1853:0",
    "15:1854:0",
    "15:1856:2",
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 1846): (
        ("要扩展领土，\n可以攻打\n", "的", "。"),
        ("", "023C", "025132", "050505"),
    ),
    ("SC", 1847): (("眼下已准备万全，\n随时都可以攻打。",), ("", "050505")),
    ("SC", 1848): (
        ("但如今还不是时候……还是\n增强兵力后再行攻击较为妥当。",),
        ("", "050505"),
    ),
    ("SC", 1849): (
        ("但如今还不是时候……还是\n增加军粮储备后再行攻击较为妥当。",),
        ("", "050505"),
    ),
    ("SC", 1850): (
        ("但如今还不是时候……还是\n多增加战友后再行攻击较为妥当。\n拉拢国众和其他势力吧。",),
        ("", "050505"),
    ),
    ("SC", 1851): (
        ("但如今还不是时候……还是增强兵力，\n增加军粮储备后再行攻击\n较为妥当。",),
        ("", "050505"),
    ),
    ("SC", 1852): (
        ("但如今还不是时候……还是增加军粮储备，\n多增加战友后再行攻击\n较为妥当。",),
        ("", "050505"),
    ),
    ("SC", 1853): (
        ("但如今还不是时候……还是\n增强兵力，多增加战友后再行攻击\n较为妥当。",),
        ("", "050505"),
    ),
    ("SC", 1854): (
        ("但如今还不是时候……还是增强兵力，\n强化军粮储备，确保战友后\n再行攻击较为妥当。",),
        ("", "050505"),
    ),
    ("SC", 1855): (("此处并无良将，\n不值得畏惧。",), ("", "050505")),
    ("SC", 1856): (
        ("但此处有人称作名将的", "在，\n需要小心……"),
        ("", "024933", "050505"),
    ),
    ("SC", 1857): (
        ("此处并无值得一提的武将，\n但", "等的动向叫人不放心。"),
        ("", "024933", "050505"),
    ),
    ("TC", 1846): (
        ("若欲擴張領土，\n不妨攻打", "的", "。"),
        ("", "023C", "025132", "050505"),
    ),
    ("TC", 1847): (("作戰準備一切就緒，\n盼能立刻進攻。",), ("", "050505")),
    ("TC", 1848): (
        ("然而，目前時機尚早……\n不妨先增強兵力再進攻較為妥當。",),
        ("", "050505"),
    ),
    ("TC", 1849): (
        ("然而，目前時機尚早……\n不妨先儲備軍糧再進攻較為妥當。",),
        ("", "050505"),
    ),
    ("TC", 1850): (
        ("然而，目前時機尚早……\n不妨先增添戰友再進攻較為妥當。\n拉攏國眾及其他勢力加入我方吧！",),
        ("", "050505"),
    ),
    ("TC", 1851): (
        ("然而，目前時機尚早……\n不妨先增強兵力、儲備軍糧再進攻較為妥當。",),
        ("", "050505"),
    ),
    ("TC", 1852): (
        ("然而，目前時機尚早……\n不妨先儲備軍糧、增添戰友再進攻較為妥當。",),
        ("", "050505"),
    ),
    ("TC", 1853): (
        ("然而，目前時機尚早……\n不妨先增強兵力、增添戰友再進攻較為妥當。",),
        ("", "050505"),
    ),
    ("TC", 1854): (
        ("然而，目前時機尚早……\n不妨先增強兵力、儲備軍糧、增添戰友再進攻較為妥當。",),
        ("", "050505"),
    ),
    ("TC", 1855): (("當中並無多強的武將，\n不足為懼。",), ("", "050505")),
    ("TC", 1856): (
        ("不過，", "乃名將也，\n尚須留意……"),
        ("", "024933", "050505"),
    ),
    ("TC", 1857): (
        ("當中雖無傑出武將，\n但", "等之動向令人擔憂。"),
        ("", "024933", "050505"),
    ),
}
PK_EN_AUXILIARY: dict[
    int, tuple[tuple[str, ...], tuple[str, ...]]
] = {}
AUXILIARY_OVERRIDES = MORPHOLOGY.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B113_A_pristine_base_pc_jp_authoritative_"
    "territorial_expansion_attack_readiness_exact_troops_provisions_allies_"
    "condition_matrix_and_enemy_general_assessment_with_explicit_base1846_"
    "1857_to_pk1876_1887_mapping_exact_base_pk_jp_sc_tc_and_blank_pk_en_"
    "auxiliary_context_project_uri_gamun_gukinjung_byeongnyeok_byeongnyang_"
    "ugun_terms_dynamic_house_force_and_officer_tokens_direction_current_"
    "korean_morphology_terminal_corpora_and_cross_resource_opcode_"
    "divergences_recorded_project_ellipsis_pair_current_line_counts_and_"
    "protected_skeleton_preserved_runtime_fragment_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    160: ("없사옵니다", "없다", "없습니다"),
    178: ("있습니다", "있다", "있사옵니다"),
    226: ("생각합니다", "생각한다", "생각하오", "생각하옵니다", "생각하옵나이다"),
    538: ("입니다", "다", "이니라", "이오", "이옵니다"),
    550: ("입니다", "다", "이오", "이옵니다"),
    598: ("이겠지요", "이리라", "이겠지"),
    1054: ("합시다", "듯"),
    1066: ("하지 않습니다", "않는", "않"),
    1078: ("합니다", "다"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    160: EXPECTED_BASE_MORPHOLOGY_TERMINALS[160],
    178: EXPECTED_BASE_MORPHOLOGY_TERMINALS[178],
    226: EXPECTED_BASE_MORPHOLOGY_TERMINALS[226],
    550: EXPECTED_BASE_MORPHOLOGY_TERMINALS[538],
    562: EXPECTED_BASE_MORPHOLOGY_TERMINALS[550],
    610: EXPECTED_BASE_MORPHOLOGY_TERMINALS[598],
    1066: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1054],
    1078: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1066],
    1090: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1078],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 940 Base-to-PK mapping drifted")
    divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if divergences != set(range(1847, 1858)):
        raise RuntimeError("segment 940 Base-to-PK gap divergence drifted")
    if any(
        EXPECTED_BASE_JP[record_id] != EXPECTED_PK_JP[record_id]
        for record_id in RECORD_ARITIES
    ):
        raise RuntimeError("segment 940 Base-to-PK literal divergence drifted")
    joined = "\n".join(translations.values())
    for required in ("영토", "국인중", "우군", "병력", "병량", "명장"):
        if required not in joined:
            raise RuntimeError(f"segment 940 required terminology drifted: {required}")
    for forbidden in ("당가", "호족", "아군을\n늘", "시기가 이르", "무장도\n없"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 940 forbidden phrasing retained: {forbidden}"
            )
    expected_conditions = {
        1848: {"병력"},
        1849: {"병량"},
        1850: {"우군"},
        1851: {"병력", "병량"},
        1852: {"병량", "우군"},
        1853: {"병력", "우군"},
        1854: {"병력", "병량", "우군"},
    }
    for record_id, expected in expected_conditions.items():
        text = "\n".join(TRANSLATIONS_BY_RECORD[record_id])
        actual = {
            term
            for term in ("병력", "병량", "우군")
            if term in text
        }
        if actual != expected:
            raise RuntimeError(
                f"segment 940 readiness condition matrix drifted: {record_id}"
            )
    if "국인중" not in TRANSLATIONS_BY_RECORD[1850][1]:
        raise RuntimeError("segment 940 kokujin rendering drifted")
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 940 ellipsis seed/pair drifted: {coordinate}"
            )
    if len(translations) != 21:
        raise RuntimeError("segment 940 visible decision count drifted")


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
    if len(rows) != 21 or len(validated) != len(translations):
        raise RuntimeError("segment 940 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 940 runtime classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S940",
                "decision_count": len(rows),
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": list(range(1847, 1858)),
                "readiness_condition_matrix_exact": True,
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
