#!/usr/bin/env python3
"""Build Base authoring segment 888 decisions for the v0.15.0 retranslation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch001_segment881 as CAPTURE_S881
import build_base_batch001_segment887 as PREVIOUS


ENGINE = PREVIOUS.ENGINE
COMMON = PREVIOUS.COMMON
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B001_S888.private.v1.jsonl"
)
SEGMENT = 888
COUNTY_DEVELOPMENT_SOURCE_JP = (
    "で",
    "を開拓し",
    "ぞ！\n民も皆協力してくれて助か",
    "\nこれもこの地を治める",
    "の人望",
)
COUNTY_DEVELOPMENT_CANONICAL = (
    "에서",
    "을(를) 개척하",
    "다!\n백성도 모두 힘을 보태 주어 큰 도움이",
    "\n이 또한 이 땅을 다스리는",
    "의 인망",
)
COUNTY_DEVELOPMENT_BASE_GAPS = (
    "029632",
    "02BE32",
    "014314020000",
    "014368020000",
    "014301000000",
    "014356020000050505",
)
COUNTY_DEVELOPMENT_PK_GAPS = (
    "029632",
    "02BE32",
    "01431A020000",
    "014374020000",
    "014301000000",
    "014362020000050505",
)
RAW_TRANSLATIONS: dict[str, str] = {
    "15:1365:0": CAPTURE_S881.RAW_TRANSLATIONS["15:1276:0"],
    "15:1365:2": CAPTURE_S881.RAW_TRANSLATIONS["15:1276:2"],
    "15:1365:3": CAPTURE_S881.RAW_TRANSLATIONS["15:1276:3"],
    "15:1366:0": "큭… 설마 허를 찔릴 줄이야\n그자는 아마도",
    "15:1366:1": "의 수하\n",
    "15:1366:2": "도 비열한 수를 쓰는 법",
    "15:1366:3": "…!",
    "15:1367:0": "병량 생산 효과를 지닌 군을 성장시키",
    "15:1367:1": "\n군이 성장하여 군 특성의 LV가 오르면\n병량 생산이 증가하",
    "15:1368:0": "농민들의 신뢰를 잃을지도 모르",
    "15:1368:1": (
        "지만\n"
        "당장이라도 병사를 내보내고자\n"
        "백성에게서 병량을 징수하고자"
    ),
    "15:1369:0": "병량을 인근 농촌에서\n서둘러 모으고자",
    "15:1369:1": "\n민심을 잃",
    "15:1369:2": "지만, 어쩔 수 없지…",
    **{
        f"15:1370:{literal_id}": translation
        for literal_id, translation in enumerate(COUNTY_DEVELOPMENT_CANONICAL)
    },
}
RECORD_ARITIES = {
    1365: 4,
    1366: 4,
    1367: 2,
    1368: 2,
    1369: 3,
    1370: 5,
}
EXPECTED_BASE_JP = {
    1365: (
        "にて間者を捕らえ",
        "\n",
        "による",
        "が密命とか…\n危ないところ",
    ),
    1366: (
        "くっ…まさか不覚を取ろうとは\nあれはおそらく",
        "が手の者\n",
        "も卑劣な手を使うもの",
        "…！",
    ),
    1367: (
        "兵糧生産効果を持つ郡を成長させ",
        "\n郡が成長し郡特性のLVが上がると\n兵糧生産が増え",
    ),
    1368: (
        "農村の信は失うやもしれ",
        "が\nすぐにでも兵を出すべく\n民より兵糧を徴収したく",
    ),
    1369: (
        "兵糧を近隣の農村より\n急ぎ集めたいと",
        "\n民心は離れ",
        "が、已む無し…",
    ),
    1370: COUNTY_DEVELOPMENT_SOURCE_JP,
}
EXPECTED_PK_JP = dict(EXPECTED_BASE_JP)
EXPECTED_BASE_GAPS = {
    1365: (
        "026432",
        "014314020000",
        "025032",
        "023C",
        "014344020000050505",
    ),
    1366: ("", "024833", "02483E", "014306040000", "050505"),
    1367: ("", "01433C040000", "01433C040000050505"),
    1368: ("", "0143E0020000", "0143E2000000050505"),
    1369: ("", "0143E2000000", "01433C040000", "050505"),
    1370: COUNTY_DEVELOPMENT_BASE_GAPS,
}
EXPECTED_PK_JP_GAPS = {
    1365: (
        "026432",
        "01431A020000",
        "025032",
        "023C",
        "014350020000050505",
    ),
    1366: ("", "024833", "02483E", "014312040000", "050505"),
    1367: ("", "014348040000", "014348040000050505"),
    1368: ("", "0143EC020000", "0143E2000000050505"),
    1369: ("", "0143E2000000", "014348040000", "050505"),
    1370: COUNTY_DEVELOPMENT_PK_GAPS,
}
PK_RECORD_MAP = {
    1365: 1379,
    1366: 1381,
    1367: 1382,
    1368: 1383,
    1369: 1384,
    1370: 1385,
}
CURRENT_ELLIPSIS_COORDINATES = {
    "15:1365:3",
    "15:1366:0",
    "15:1366:3",
    "15:1369:2",
}
EXCLUDED_NONVISIBLE_COORDINATES = {"15:1365:1": "\n"}
SHARED_AUXILIARY = {
    ("SC", 1365): (
        (
            "已于",
            "逮捕间谍。\n据说是",
            "的",
            "发出密令……\n差点就没命了。",
        ),
        ("", "026432", "025032", "023C", "050505"),
    ),
    ("TC", 1365): (
        (
            "已於",
            "逮捕間諜。\n據說是",
            "的",
            "發出密令……\n差點就沒命了。",
        ),
        ("", "026432", "025032", "023C", "050505"),
    ),
    ("SC", 1366): (
        ("呃……太大意了。\n那是", "的手下吗？\n居然会被", "的人攻击受伤……"),
        ("", "024833", "02483E", "050505"),
    ),
    ("TC", 1366): (
        ("呃……太大意了。\n那是", "的手下嗎？\n居然會被", "的人攻擊受傷……"),
        ("", "024833", "02483E", "050505"),
    ),
    ("SC", 1368): (
        ("或许会失去村庄的信用\n但应该立即出兵，\n从村们手中征收军粮才是。",),
        ("", "050505"),
    ),
    ("TC", 1368): (
        ("或許將失去農村的民心，\n但應當立刻出兵，\n向人民徵收軍糧。",),
        ("", "050505"),
    ),
    ("SC", 1369): (
        ("应该火速从附近的村庄\n征集军粮，虽然有失民心，\n但也是不得已而为之……",),
        ("", "050505"),
    ),
    ("TC", 1369): (
        ("臣認為，應立刻從鄰近的\n農村開始徵收軍糧。\n失去民心實屬無奈之事……",),
        ("", "050505"),
    ),
}
PK_EN_AUXILIARY = {
    1365: (
        (
            "WeÖve captured spies in ",
            ". They had the ",
            "Ös ",
            " secret orders... That could have been bad.",
        ),
        ("", "026432", "025032", "023C", "050505"),
    ),
    1366: (
        (
            "Blast! I didnÖt think weÖd be caught off guard. This must be ",
            "Ös doing. To think the ",
            " would use such underhanded tactics...",
        ),
        ("", "024833", "02483E", "050505"),
    ),
    1367: (
        (
            "We should develop a county with supply production. As a county "
            "develops, so too will the level of its county traits, thereby "
            "increasing supply production.",
        ),
        ("", "050505"),
    ),
    1368: (
        (
            "The farms may not like it, but IÖd like to order a collection "
            "of supplies to send to the soldiers at once.",
        ),
        ("", "050505"),
    ),
    1369: (
        (
            "WeÖd like to collect supplies from neighboring farms at once. "
            "The people wonÖt like it, but weÖve got no choice.",
        ),
        ("", "050505"),
    ),
}
AUXILIARY_OVERRIDES = CAPTURE_S881.make_auxiliary_overrides(
    SHARED_AUXILIARY,
    PK_EN_AUXILIARY,
)
BASIS = (
    "review_queue_base_msggame_B107_pristine_base_pc_jp_authoritative_"
    "captured_spy_counterintelligence_tutorial_supply_collection_and_county_"
    "development_reports_with_explicit_plus_14_plus_15_base_to_pk_mapping_"
    "hidden_newline_excluded_exact_base_pk_jp_sc_tc_and_actual_pk_en_context_"
    "B106_spy_capture_canonical_reused_0143_conjugation_stems_guarded_"
    "nomin_no_shin_farmers_trust_minshin_popular_sentiment_jinbo_distinguished_"
    "runtime_fragment_pending"
)


def source_literals(
    source_records: dict[tuple[int, int], Any],
    record_id: int,
) -> tuple[str, ...]:
    return tuple(
        literal.text
        for literal in ENGINE.parse_record_literals(source_records[(15, record_id)])
    )


def assert_semantics(
    source_records: dict[tuple[int, int], Any],
    raw_translations: dict[str, str],
    translations: dict[str, str],
) -> None:
    if "15:1365:1" in raw_translations or "15:1365:1" in translations:
        raise RuntimeError("segment 888 excluded hidden newline received a decision")
    for literal_id in (0, 2, 3):
        coordinate = f"15:1365:{literal_id}"
        canonical = CAPTURE_S881.RAW_TRANSLATIONS[f"15:1276:{literal_id}"]
        if raw_translations[coordinate] != canonical:
            raise RuntimeError(
                f"segment 888 B106 captured-spy canonical drifted: {coordinate}"
            )
    if source_literals(source_records, 1365) != CAPTURE_S881.EXPECTED_BASE_JP[1276]:
        raise RuntimeError("segment 888 B106 captured-spy source equivalence drifted")
    if (
        not raw_translations["15:1367:0"].endswith("군을 성장시키")
        or not raw_translations["15:1367:1"].endswith("병량 생산이 증가하")
        or EXPECTED_BASE_GAPS[1367][1:3]
        != ("01433C040000", "01433C040000050505")
    ):
        raise RuntimeError("segment 888 1367 tutorial verb-stem assembly drifted")
    if (
        not raw_translations["15:1368:0"].endswith("모르")
        or not raw_translations["15:1368:1"].startswith("지만\n")
        or not raw_translations["15:1368:1"].endswith("병량을 징수하고자")
        or EXPECTED_BASE_GAPS[1368][1:3]
        != ("0143E0020000", "0143E2000000050505")
    ):
        raise RuntimeError("segment 888 1368 runtime conjugation assembly drifted")
    if (
        not raw_translations["15:1369:0"].endswith("서둘러 모으고자")
        or not raw_translations["15:1369:1"].endswith("민심을 잃")
        or not raw_translations["15:1369:2"].startswith("지만,")
        or EXPECTED_BASE_GAPS[1369][1:3]
        != ("0143E2000000", "01433C040000")
    ):
        raise RuntimeError("segment 888 1369 runtime conjugation assembly drifted")
    if (
        not translations["15:1366:0"].startswith("큭…… ")
        or translations["15:1366:0"].count("…") != 2
        or translations["15:1366:3"] != "……!"
        or not translations["15:1369:2"].endswith("……")
        or translations["15:1369:2"].count("…") != 2
    ):
        raise RuntimeError("segment 888 resolved project ellipsis pairing drifted")
    for record_id in range(1370, 1389):
        if source_literals(source_records, record_id) != COUNTY_DEVELOPMENT_SOURCE_JP:
            raise RuntimeError(
                f"segment 888 exact 19-record development source drifted: {record_id}"
            )
    actual_development = tuple(
        raw_translations[f"15:1370:{literal_id}"]
        for literal_id in range(len(COUNTY_DEVELOPMENT_CANONICAL))
    )
    if actual_development != COUNTY_DEVELOPMENT_CANONICAL:
        raise RuntimeError("segment 888 county development canonical drifted")
    joined = "\n".join(translations.values())
    for required in (
        "간자를 붙잡아",
        "허를 찔릴 줄이야",
        "병량 생산",
        "농민들의 신뢰",
        "민심을 잃",
        "힘을 보태",
        "의 인망",
    ):
        if required not in joined:
            raise RuntimeError(f"segment 888 meaning or terminology drifted: {required}")
    if "농촌의 신망" in joined or "농민들의 민심" in joined:
        raise RuntimeError("segment 888 農村の信/民心 terminology distinction collapsed")


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]]]:
    return COMMON.build_segment_rows(
        output=OUTPUT,
        segment=SEGMENT,
        raw_translations=RAW_TRANSLATIONS,
        record_arities=RECORD_ARITIES,
        expected_base_jp=EXPECTED_BASE_JP,
        expected_pk_jp=EXPECTED_PK_JP,
        base_gaps=EXPECTED_BASE_GAPS,
        pk_jp_gaps=EXPECTED_PK_JP_GAPS,
        pk_record_map=PK_RECORD_MAP,
        ellipsis_coordinates=CURRENT_ELLIPSIS_COORDINATES,
        auxiliary_overrides=AUXILIARY_OVERRIDES,
        excluded_nonvisible_coordinates=EXCLUDED_NONVISIBLE_COORDINATES,
        basis=BASIS,
        semantic_assertions=assert_semantics,
    )


def main() -> int:
    prepared, translations, rows = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(prepared, OUTPUT, require_complete=False)
    if len(validated) != len(translations):
        raise RuntimeError("segment 888 validated count drifted")
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B001_S888",
                "decision_count": len(rows),
                "retranslated": len(rows),
                "dynamic_runtime_review_pending": len(rows),
                "base_to_pk_offsets": [14, 15],
                "excluded_hidden_newline": "15:1365:1",
                "b106_spy_capture_canonical_reused": True,
                "runtime_conjugation_stem_guards": [1368, 1369],
                "county_development_group_size": 19,
                "county_development_canonical_defined": True,
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
