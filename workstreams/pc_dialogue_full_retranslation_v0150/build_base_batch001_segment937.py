#!/usr/bin/env python3
"""Build Base authoring segment 937 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment936 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S937.private.v1.jsonl"
)
SEGMENT = 937
SMALL_SCALE_PREFIX = PREVIOUS.TRANSLATIONS_BY_RECORD[1809][0]
TRANSLATIONS_BY_RECORD = {
    1812: (
        "우리 가문은",
        "의",
        "와(과) 험악한 관계라\n언제 전쟁이 벌어져도 이상하지 않은 정세",
    ),
    1813: (
        "우리 가문은 여러 적을 두고 있으며,\n그중 가장 큰 적은",
        "의",
        "…\n그야말로 위기에 놓였다고 할 수 있을",
    ),
    1814: (
        "그",
        "은(는)\n전력이 그리 크다고 할 수",
        "만\n무슨 일이든 방심은 금물",
    ),
    1815: (
        "그",
        "이(가)\n과연 무엇을 해 올지…\n늘 주의를 기울여야 한다고",
    ),
    1816: (
        "그",
        "은(는)\n유감스럽게도 우리 가문보다 강대하여…\n유연하게 대응해야 할",
    ),
    1817: (
        "세력을 발전시키려면 적을 줄이는 것이 긴요\n",
        "의",
        "와(과)는\n더 나은 관계를 맺어야 한다고",
    ),
    1818: (
        "영토를 넓히려면 적을 줄여야 한다고 봅니다\n",
        "의",
        "와(과),",
        "의",
        "와(과)는\n좋은 관계를 유지해야 할 것",
    ),
    1819: (
        SMALL_SCALE_PREFIX,
        "만\n효과적으로 활용하고 싶은 다이묘",
    ),
    1820: (
        "우리 가문과 규모가 비슷한 세력이니\n서로에게 이로운 관계일",
    ),
    1821: PREVIOUS.LARGE_ALLY_TRANSLATION,
    1822: (
        "현재 특별히 경계할 세력은 없습니다",
        "\n주변 세력의 전력을 주시하며\n외교와 공략 전략을 세워 나가야 합니다",
    ),
    1823: (
        "싸울 때가 머지않았으니 군비를 갖추기 위해서라도\n"
        "전군에 공략 목표를 제시해야 합니다",
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
    1812: ("当家は", "の", "と険悪な関係にあり\nいつ戦が始まってもおかしくない情勢"),
    1813: ("当家は複数の敵を抱えており、\n中でも最大は", "の", "…\nまさに危地にあると言え"),
    1814: ("その", "は\n戦力としてはさほど大きく", "が\n何事も油断は禁物"),
    1815: ("その", "が\n果たして何をしてくるか…\n常に注意を払うべきかと"),
    1816: ("その", "は\n残念ながら当家よりも強大にて…\n立ち回りの妙が求められ"),
    1817: ("勢力の発展には、敵を絞り込むことこそ肝要\n", "の", "とは\nより良い関係を築くべきと"),
    1818: ("領土を広げる上では、敵は絞るべきかと\n", "の", "や", "の", "とは\n良い関係を保つべき"),
    1819: ("勢力の規模としては\nそれほど大きくは", "が\n有効に活用したい大名"),
    1820: ("当家とさほど変わらぬ規模の勢力だけに\n互いに利益となる関係と言え",),
    1821: ("規模は当家を上回っているため\n遠慮なく頼ってい",),
    1822: ("現在、関係に注意すべき勢力は", "\n周辺勢力の戦力に気を付けつつ\n外交・攻略の戦略をたててい"),
    1823: ("戦機は近く、軍備を整えるためにも\n全軍に攻略目標を示すべき",),
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1812: ("", "023C", "025132", "01432C020000050505"),
    1813: ("", "023C", "025132", "01431E040000050505"),
    1814: ("", "025132", "0143DA020000", "01431A020000050505"),
    1815: ("", "025132", "0143E2000000050505"),
    1816: ("", "025132", "01431E040000050505"),
    1817: ("", "023C", "025132", "0143E2000000050505"),
    1818: ("", "023C", "025132", "023D", "025232", "014356020000050505"),
    1819: ("", "0143DA020000", "01431A020000050505"),
    1820: ("", "01431E040000050505"),
    1821: ("", "01436C010000050505"),
    1822: ("", "0143DA020000", "01436C010000050505"),
    1823: ("", "01431E010000050505"),
}
EXPECTED_CURRENT_GAPS = {
    **EXPECTED_BASE_GAPS,
    1822: ("", "", "050505"),
    1823: ("", "050505"),
}
EXPECTED_PK_JP_GAPS = {
    1812: ("", "023C", "025132", "014338020000050505"),
    1813: ("", "023C", "025132", "01432A040000050505"),
    1814: ("", "025132", "0143E6020000", "014326020000050505"),
    1815: ("", "025132", "0143E2000000050505"),
    1816: ("", "025132", "01432A040000050505"),
    1817: ("", "023C", "025132", "0143E2000000050505"),
    1818: ("", "023C", "025132", "023D", "025232", "014362020000050505"),
    1819: ("", "0143E6020000", "014326020000050505"),
    1820: ("", "01432A040000050505"),
    1821: ("", "01436C010000050505"),
    1822: ("", "0143E6020000", "01436C010000050505"),
    1823: ("", "01431E010000050505"),
}
PK_RECORD_MAP = {record_id: record_id + 30 for record_id in RECORD_ARITIES}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:1813:2",
    "15:1815:1",
    "15:1816:1",
}
EXCLUDED_NONVISIBLE_COORDINATES: dict[str, str] = {}
STATIC_RECORD_IDS = {1822, 1823}
SHARED_AUXILIARY = {
    ("SC", 1812): (
        ("本家与", "的", "彼此交恶，\n战火一触即发。"),
        ("", "023C", "025132", "050505"),
    ),
    ("SC", 1813): (
        ("本家目前与复数势力为敌，\n其中", "的", "相当难缠……\n可谓正处于危险之中。"),
        ("", "023C", "025132", "050505"),
    ),
    ("SC", 1814): (("当下之敌", "，\n其规模虽不敌本家，\n但依旧不得大意。"), ("", "025132", "050505")),
    ("SC", 1815): (("当下之敌", "，\n该势力不知会如何出招……\n应时时提高警觉。"), ("", "025132", "050505")),
    ("SC", 1816): (
        ("当下之敌", "，\n毕竟其势力庞大，在我方之上……\n若未能灵活周旋，恐将致命。"),
        ("", "025132", "050505"),
    ),
    ("SC", 1817): (
        ("发展势力的关键在于少树敌。\n我认为应当与", "的", "\n构建起更为良好的关系。"),
        ("", "023C", "025132", "050505"),
    ),
    ("SC", 1818): (
        ("既然要扩张领土，就该少树敌。\n我们应当与", "的", "、", "的", "\n保持良好的关系。"),
        ("", "023C", "025132", "023D", "025232", "050505"),
    ),
    ("SC", 1819): (("势力规模\n并不算太大，\n但我希望能充分利用这个大名。",), ("", "050505")),
    ("SC", 1820): (("这个势力比本家规模相差不大，\n我们的关系可以说对双方都有利。",), ("", "050505")),
    ("SC", 1821): (("它的规模比本家要大，\n尽可倚重。",), ("", "050505")),
    ("SC", 1822): (
        ("目前无需留意势力之间的关系。\n小心周边势力的战力，\n同时制定外交丶攻略的战略吧。",),
        ("", "050505"),
    ),
    ("SC", 1823): (("臣认为现应整军备战，\n向全军指示攻略目标。",), ("", "050505")),
    ("TC", 1812): (
        ("本家與", "的", "彼此交惡，\n戰火一觸即發。"),
        ("", "023C", "025132", "050505"),
    ),
    ("TC", 1813): (
        ("本家目前與複數勢力為敵，\n其中", "的", "相當難纏……\n可謂正處於危險地帶。"),
        ("", "023C", "025132", "050505"),
    ),
    ("TC", 1814): (("當下之敵", "，\n其規模雖不敵本家，\n但依舊不得大意。"), ("", "025132", "050505")),
    ("TC", 1815): (("當下之敵", "，\n該勢力不知會如何出招……\n應時時提高警覺。"), ("", "025132", "050505")),
    ("TC", 1816): (
        ("當下之敵", "，\n畢竟其勢力龐大，在我方之上……\n若未能靈活周旋，恐將致命。"),
        ("", "025132", "050505"),
    ),
    ("TC", 1817): (
        ("減少敵人乃拓展勢力的關鍵所在，\n與", "的", "之間應改善關係。"),
        ("", "023C", "025132", "050505"),
    ),
    ("TC", 1818): (
        ("欲擴張領土則應減少敵人，\n與", "的", "及", "的", "\n須維持良好關係。"),
        ("", "023C", "025132", "023D", "025232", "050505"),
    ),
    ("TC", 1819): (("其勢力規模雖沒多大，\n且看如何有效活用此大名。",), ("", "050505")),
    ("TC", 1820): (("其勢力規模與本家不相上下，\n可謂互利互惠的關係。",), ("", "050505")),
    ("TC", 1821): (("其勢力規模在本家之上，\n作為後盾再可靠不過。",), ("", "050505")),
    ("TC", 1822): (
        ("當下無需留關係之勢力。\n於留意周邊勢力之戰力的同時，\n制定外交、攻略的戰略吧。",),
        ("", "050505"),
    ),
    ("TC", 1823): (("臣認為現應整軍備戰，\n向全軍指示攻略目標。",), ("", "050505")),
}
PK_EN_AUXILIARY = {
    1812: (
        ("Our clan is perceived poorly by the ", " of ", ". A war could erupt at any moment."),
        ("", "025132", "023C", "050505"),
    ),
    1813: (
        ("Our clan has several enemies, but the largest one is the ", " of ", ". This could be dangerous."),
        ("", "025132", "023C", "050505"),
    ),
    1817: (
        (
            "To improve our clan, we must reduce our number of enemies. We might want to build a better connection with the ",
            " of ",
            ".",
        ),
        ("", "025132", "023C", "050505"),
    ),
    1818: (
        (
            "To expand our territory, we need to reduce our opposition. ItÖs important we maintain good relationships with the ",
            " of ",
            " and ",
            "Ös ",
            ".",
        ),
        ("", "025132", "023C", "023D", "025232", "050505"),
    ),
    1819: (("Their clan may not be large in scale, but theyÖd be a valuable daimyª all the same.",), ("", "050505")),
    1820: (("Their scale is not that different from ours, so a connection would be mutually beneficial.",), ("", "050505")),
    1821: (("They are larger than our clan, so theyÖd make for a reliable ally.",), ("", "050505")),
    1822: (
        ("There are no clans we need to pay attention to at the moment. LetÖs keep an eye on our neighboring clansÖ forces and exercise a mix of diplomacy and aggression.",),
        ("", "050505"),
    ),
    1823: (("War will soon be upon us. We must mobilize our forces and relay the target.",), ("", "050505")),
}
AUXILIARY_OVERRIDES = PREVIOUS.PREVIOUS.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B112_C_pristine_base_pc_jp_authoritative_"
    "hostile_relations_enemy_assessment_relationship_improvement_territory_"
    "expansion_daimyo_scale_and_war_preparation_with_explicit_base1812_"
    "1823_to_pk1842_1853_mapping_exact_base_pk_jp_sc_tc_and_actual_pk_en_"
    "auxiliary_context_project_uri_gamun_yeongto_daimyo_gongnyak_mokpyo_"
    "terms_dynamic_house_force_and_second_target_tokens_023c_025132_023d_"
    "025232_direction_current_korean_morphology_terminal_corpora_and_cross_"
    "resource_opcode_divergences_recorded_kotobank_sourced_senki_natural_"
    "korean_1822_1823_current_static_opcode_removal_preserved_1811_1821_"
    "canonical_exact_reuse_project_ellipsis_pair_current_line_counts_and_"
    "protected_skeleton_preserved_static_and_runtime_split"
)
EXPECTED_BASE_MORPHOLOGY_TERMINALS = {
    226: ("생각합니다", "생각한다", "생각하오", "생각하옵니다", "생각하옵나이다"),
    364: ("겠습니다", "이렇게", "기로 하지"),
    538: ("입니다", "다", "이니라", "이오", "이옵니다"),
    556: ("입니다", "다", "이오"),
    598: ("이겠지요", "이리라", "이겠지"),
    730: ("없습니다", "없다", "없소", "아닙니다", "아니옵니다"),
    1054: ("합시다", "듯"),
}
EXPECTED_PK_MORPHOLOGY_TERMINALS = {
    226: EXPECTED_BASE_MORPHOLOGY_TERMINALS[226],
    364: EXPECTED_BASE_MORPHOLOGY_TERMINALS[364],
    550: EXPECTED_BASE_MORPHOLOGY_TERMINALS[538],
    568: EXPECTED_BASE_MORPHOLOGY_TERMINALS[556],
    610: EXPECTED_BASE_MORPHOLOGY_TERMINALS[598],
    742: EXPECTED_BASE_MORPHOLOGY_TERMINALS[730],
    1066: EXPECTED_BASE_MORPHOLOGY_TERMINALS[1054],
}


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    del source_records
    if TRANSLATIONS_BY_RECORD[1821] is not PREVIOUS.LARGE_ALLY_TRANSLATION:
        raise RuntimeError("segment 937 Base1811/1821 canonical tuple split")
    if TRANSLATIONS_BY_RECORD[1819][0] is not SMALL_SCALE_PREFIX:
        raise RuntimeError("segment 937 Base1809/1819 prefix reuse split")
    if {mapped - base for base, mapped in PK_RECORD_MAP.items()} != {30}:
        raise RuntimeError("segment 937 Base-to-PK mapping drifted")
    divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_PK_JP_GAPS[record_id]
    }
    if divergences != {1812, 1813, 1814, 1816, 1818, 1819, 1820, 1822}:
        raise RuntimeError("segment 937 Base-to-PK gap divergence drifted")
    current_divergences = {
        record_id
        for record_id in RECORD_ARITIES
        if EXPECTED_BASE_GAPS[record_id] != EXPECTED_CURRENT_GAPS[record_id]
    }
    if current_divergences != STATIC_RECORD_IDS:
        raise RuntimeError("segment 937 pristine/current gap divergence drifted")
    joined = "\n".join(translations.values())
    for required in (
        "우리 가문",
        "영토",
        "다이묘",
        "공략 목표",
        "싸울 때",
        "관계",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 937 required terminology drifted: {required}")
    for forbidden in ("당가", "전기가 임박", "적을 좁히", "무슨 짓"):
        if forbidden in joined:
            raise RuntimeError(
                f"segment 937 forbidden phrasing retained: {forbidden}"
            )
    for coordinate in CURRENT_ELLIPSIS_COORDINATES:
        if (
            raw_translations[coordinate].count("…") != 1
            or translations[coordinate].count("…") != 2
        ):
            raise RuntimeError(
                f"segment 937 ellipsis seed/pair drifted: {coordinate}"
            )
    if len(translations) != 28:
        raise RuntimeError("segment 937 visible decision count drifted")


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
    for row in rows:
        record_id = int(str(row["coordinate"]).split(":")[1])
        if record_id in STATIC_RECORD_IDS:
            row["scope_classification"] = "retranslated"
            row["runtime_review"] = "not_required"
    PREVIOUS.PREVIOUS.annotate_morphology_evidence(
        prepared,
        rows,
        record_arities=RECORD_ARITIES,
        pk_record_map=PK_RECORD_MAP,
        base_gaps=EXPECTED_CURRENT_GAPS,
        pk_gaps=EXPECTED_PK_JP_GAPS,
        expected_base=EXPECTED_BASE_MORPHOLOGY_TERMINALS,
        expected_pk=EXPECTED_PK_MORPHOLOGY_TERMINALS,
        skip_records=STATIC_RECORD_IDS,
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
    if len(rows) != 28 or len(validated) != len(translations):
        raise RuntimeError("segment 937 validated count drifted")
    static_rows = [
        row
        for row in rows
        if row["scope_classification"] == "retranslated"
        and row["runtime_review"] == "not_required"
    ]
    if len(static_rows) != 3:
        raise RuntimeError("segment 937 static classification count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S937",
                "decision_count": len(rows),
                "retranslated": len(static_rows),
                "runtime_fragment_pending": len(rows) - len(static_rows),
                "static_record_ids": sorted(STATIC_RECORD_IDS),
                "pristine_current_gap_divergence_records": sorted(
                    STATIC_RECORD_IDS
                ),
                "canonical_base1811_1821_reuse": True,
                "explicit_pk_mapping": PK_RECORD_MAP,
                "base_pk_jp_literal_divergence_records": [],
                "base_pk_jp_gap_divergence_records": [
                    1812,
                    1813,
                    1814,
                    1816,
                    1818,
                    1819,
                    1820,
                    1822,
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
