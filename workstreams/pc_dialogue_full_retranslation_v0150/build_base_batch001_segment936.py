#!/usr/bin/env python3
"""Build Base authoring segment 936 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment935 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S936.private.v1.jsonl"
)
SEGMENT = 936
LARGE_ALLY_TRANSLATION = (
    "규모가 우리 가문보다 크니\n거리낌 없이 의지하",
)
TRANSLATIONS_BY_RECORD = {
    1803: (
        "우리 가문은",
        "의",
        "에\n종속되어",
        "\n그 때문에 자유롭게 외교하지",
    ),
    1804: (
        "의",
        "를 종속시키고",
        "\n그 가문에는 쉽게 원군을 요청할 수 있으니\n세력을 넓히는 데 잘 활용",
    ),
    1805: (
        "우리 가문은 여러 세력을 종속시키고",
        "\n그중 가장 규모가 큰",
        "의",
        "등은\n든든한 원군으로 기대",
    ),
    1807: (
        "우리는",
        "의",
        "와(과)\n",
        "의 동맹을 맺고",
    ),
    1808: (
        "우리 가문은 여러 세력과 동맹 관계에",
        "만\n가장 믿을 만한 상대는",
        "의",
        "와(과)의\n",
        "에 이르는 동맹",
    ),
    1809: (
        "세력 규모로는\n그리 크다고 할 수",
        "만\n효과적으로 활용하고 싶은 동맹",
    ),
    1810: (
        "우리 가문과 규모가 비슷한 세력이니\n서로에게 이로운 동맹일",
    ),
    1811: LARGE_ALLY_TRANSLATION,
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
    1803: ("当家は", "の", "に\n従属して", "\nそのため、自由な外交はでき"),
    1804: ("の", "を従属させて", "\nかの家からならば援軍を呼ぶも容易\n勢力を伸ばすためうまく利用"),
    1805: ("当家は複数の勢力を従属させて", "\n最も大きい", "の", "などは\n頼もしい援軍として期待でき"),
    1807: ("我らは", "の", "と\n", "の同盟を結んで"),
    1808: ("当家は複数勢力と同盟関係に", "が\n最も頼れるのは", "の", "との\n", "に及ぶ同盟"),
    1809: ("勢力の規模としては\nそれほど大きくは", "が\n有効に活用したい同盟"),
    1810: ("当家とさほど変わらぬ規模の勢力だけに\n互いに利益となる同盟と言え",),
    1811: ("規模は当家を上回っているため\n遠慮なく頼ってい",),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1803: ("", "023C", "025132", "0143B2000000", "0143E0020000050505"),
    1804: ("023C", "025132", "0143B2000000", "0143A2010000050505"),
    1805: ("", "0143B2000000", "023C", "025132", "01431E040000050505"),
    1807: ("", "023C", "025132", "023D", "0143B2000000050505"),
    1808: ("", "014352000000", "023C", "025132", "023D", "014356020000050505"),
    1809: ("", "0143DA020000", "01431A020000050505"),
    1810: ("", "01431E040000050505"),
    1811: ("", "01436C010000050505"),
}
EXPECTED_CURRENT_GAPS = dict(EXPECTED_BASE_GAPS)
EXPECTED_PK_JP_GAPS = {
    1803: ("", "023C", "025132", "0143B2000000", "0143EC020000050505"),
    1804: ("023C", "025132", "0143B2000000", "0143A8010000050505"),
    1805: ("", "0143B2000000", "023C", "025132", "01432A040000050505"),
    1807: ("", "023C", "025132", "023D", "0143B2000000050505"),
    1808: ("", "014352000000", "023C", "025132", "023D", "014362020000050505"),
    1809: ("", "0143E6020000", "014326020000050505"),
    1810: ("", "01432A040000050505"),
    1811: ("", "01436C010000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES: set[str] = set()
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
SHARED_AUXILIARY = {
    ("SC", 1803): (
        ("\r本家正从属于\n", "的", "。\n因此，无法进行自由的外交。"),
        ("", "023C", "025132", "050505"),
    ),
    ("SC", 1804): (
        ("的", "目前在本家统御下，\n既为从属势力就容易要求援军，\n不妨在拓展势力上加以利用。"),
        ("023C", "025132", "050505"),
    ),
    ("SC", 1805): (
        ("目前有复数势力在本家统御下，\n", "的", "等规模最大，\n作为援军值得信赖。"),
        ("", "023C", "025132", "050505"),
    ),
    ("SC", 1807): (
        ("我们与", "的", "\n", "缔结了同盟。"),
        ("", "023C", "025132", "023D", "050505"),
    ),
    ("SC", 1808): (
        ("本家虽与复数势力缔结同盟，\n其中与", "的", "为", "同盟，\n应该最可靠。"),
        ("", "023C", "025132", "023D", "050505"),
    ),
    ("SC", 1809): (("势力规模\n并不算大，但我希望能有效的用好\n这个同盟。",), ("", "050505")),
    ("SC", 1810): (("此势力规模与本家相差不大，\n同盟关系可以说对彼此都有利。",), ("", "050505")),
    ("SC", 1811): (("它的规模比本家要大，\n尽可倚重。",), ("", "050505")),
    ("TC", 1803): (
        ("本家正從屬於\n", "的", "。\n因此，無法進行自由的外交。"),
        ("", "023C", "025132", "050505"),
    ),
    ("TC", 1804): (
        ("的", "目前在本家統御下，\n既為從屬勢力就容易要求援軍，\n不妨在拓展勢力上加以利用。"),
        ("023C", "025132", "050505"),
    ),
    ("TC", 1805): (
        ("目前有複數勢力在本家統御下，\n", "的", "等規模最大，\n作為援軍值得信賴。"),
        ("", "023C", "025132", "050505"),
    ),
    ("TC", 1807): (
        ("我方與", "的", "為\n", "同盟關係。"),
        ("", "023C", "025132", "023D", "050505"),
    ),
    ("TC", 1808): (
        ("本家雖與複數勢力締結同盟，\n其中與", "的", "為", "同盟，\n應該最可靠。"),
        ("", "023C", "025132", "023D", "050505"),
    ),
    ("TC", 1809): (("其勢力規模雖沒多大，\n且看如何有效活用此同盟。",), ("", "050505")),
    ("TC", 1810): (("其勢力規模與本家不相上下，\n可謂互利互惠的同盟。",), ("", "050505")),
    ("TC", 1811): (("其勢力規模在本家之上，\n作為後盾再可靠不過。",), ("", "050505")),
}
PK_EN_AUXILIARY = {
    1803: (
        ("Our clan are vassals to the ", " of ", ", so weÖre not free to enact our own diplomacy."),
        ("", "025132", "023C", "050505"),
    ),
    1804: (
        (
            "With the ",
            " of ",
            " as vassals, we can easily call for reinforcements. We should take advantage of this to improve our clan.",
        ),
        ("", "025132", "023C", "050505"),
    ),
    1805: (
        (
            "Our clan has dominance over several clans, the biggest being the ",
            " of ",
            ". We can count on them for reinforcements.",
        ),
        ("", "025132", "023C", "050505"),
    ),
}
AUXILIARY_OVERRIDES = PREVIOUS.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B112_C_pristine_base_pc_jp_authoritative_"
    "vassalage_reinforcements_alliance_scale_and_mutual_benefit_with_"
    "explicit_base1803_1811_excluding_empty1806_to_pk1833_1841_mapping_"
    "exact_base_pk_jp_sc_tc_and_actual_pk_en_auxiliary_context_project_"
    "uri_gamun_jongsok_wongun_dongmaeng_terms_dynamic_house_force_and_"
    "duration_tokens_023c_025132_023d_direction_current_korean_morphology_"
    "terminal_corpora_and_cross_resource_opcode_divergences_recorded_"
    "1811_canonical_for_1821_exact_reuse_current_line_counts_and_protected_"
    "skeleton_preserved_runtime_fragment_pending"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    82: ("있습니다", "있다", "있사옵니다", "입니다", "이옵니다"),
    178: ("있습니다", "있다", "있사옵니다"),
    364: ("겠습니다", "이렇게", "기로 하지"),
    418: ("합시다", "하자", "않다", "하겠다", "하겠습니다"),
    538: ("입니다", "다", "이니라", "이오", "이옵니다"),
    598: ("이겠지요", "이리라", "이겠지"),
    730: ("없습니다", "없다", "없소", "아닙니다", "아니옵니다"),
    736: ("않습니다", "않는다"),
    1054: ("합시다", "듯"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    82: EXPECTED_BASE_MORPHOLOGY_TERMINALS[82],
    178: EXPECTED_BASE_MORPHOLOGY_TERMINALS[178],
    364: EXPECTED_BASE_MORPHOLOGY_TERMINALS[364],
    424: ("합시다", "하자", "하겠다", "하겠습니다"),
    550: EXPECTED_BASE_MORPHOLOGY_TERMINALS[538],
    610: EXPECTED_BASE_MORPHOLOGY_TERMINALS[598],
    742: EXPECTED_BASE_MORPHOLOGY_TERMINALS[730],
    748: EXPECTED_BASE_MORPHOLOGY_TERMINALS[736],
    1066: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1054],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records, raw_translations
    if TRANSLATIONS_BY_RECORD[1811] is not LARGE_ALLY_TRANSLATION:
        raise RuntimeError("segment 936 large-ally canonical tuple split")
    if set(RECORD_ARITIES) != {
        1803,
        1804,
        1805,
        1807,
        1808,
        1809,
        1810,
        1811,
    }:
        raise RuntimeError("segment 936 nonempty record universe drifted")
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 936 Base-to-PK mapping drifted")
    divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if divergences != {1803, 1804, 1805, 1808, 1809, 1810}:
        raise RuntimeError("segment 936 Base-to-PK gap divergence drifted")
    joined = "\n".join(translations.values())
    for required in ("우리 가문", "종속", "원군", "동맹", "세력"):
        if required not in joined:
            raise RuntimeError(f"segment 936 required terminology drifted: {required}")
    for forbidden in ("당가", "지배하", "속국"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 936 forbidden terminology retained: {forbidden}"
            )
    for particle in ("와(과)",):
        if particle not in joined:
            raise RuntimeError(f"segment 936 dynamic particle guard drifted: {particle}")
    if translations["15:1804:1"] != "를 종속시키고":
        raise RuntimeError("segment 936 1804 vassal-state stem drifted")
    if len(translations) != 24:
        raise RuntimeError("segment 936 visible decision count drifted")


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
    PREVIOUS.annotate_morphology_evidence(
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
    if len(rows) != 24 or len(validated) != len(translations):
        raise RuntimeError("segment 936 validated count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        for row in rows
    ):
        raise RuntimeError("segment 936 runtime classification drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S936",
                "decision_count": len(rows),
                "retranslated": 0,
                "runtime_fragment_pending": len(rows),
                "excluded_empty_record_ids": [1806],
                "dynamic_token_directions": {
                    "023C": "house_or_force_component",
                    "025132": "force_or_house_component",
                    "023D": "alliance_duration_or_second_house_component",
                },
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [
                    1803,
                    1804,
                    1805,
                    1808,
                    1809,
                    1810,
                ],
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
